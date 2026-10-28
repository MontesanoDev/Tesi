"""Fix 2: no fixed wait limit; legitimate wait, impossible budget and provider timeout differ.

Compiler-level cases run the unchanged candidate (5 segments, 3 concurrent, TIMEOUT_SECONDS
scaled to 1 s, simulated provider at the transport).
"""
import asyncio
import json
import time

import httpx
import pytest

from audit_tools.narrator_harness import budget, metrics
from audit_tools.tests.simulated_compiler import (
    application,
    instrument,
    records,
    report,
    resolve,
    session,
    world,
)
from audit_tools.tests.test_metrics import RATES, SETTINGS, USAGE, post

__all__ = ['world']
BODY = {'model':'deepseek-flash','messages':[{'role':'user','content':'synthetic'}],'max_tokens':20}
ONE = budget.bound(BODY)


def segment_bound(provider):
    return max(budget.bound(json.loads(content)) for _, content in provider.wires)


@pytest.mark.parametrize('admission', [False, True])
def test_queue_time_never_consumes_the_model_timeout(world, monkeypatch, tmp_path, admission):
    """Budget for one segment at a time, 0.4 s per segment, model timeout 1 s. Waiting inside
    post_chat (the 02 harness) makes the fourth segment exceed the compiler's own timeout while
    in flight; a ticket taken when the client opens leaves the timeout to the model."""
    async def run():
        async with application() as (client, form_id):
            world.default_delay = .01
            first = await resolve(client, await session(client, form_id))  # Sizes the bodies.
            assert first.status_code == 200, first.text
            limit = segment_bound(world) + 5000
            world.wires, world.peak, world.default_delay = [], 0, .4
            ledger = instrument(monkeypatch, tmp_path / 'audit', limit=limit, admission=admission)
            current = await session(client, form_id)
            response = await resolve(client, current)
            t = budget.totals(ledger)
            if not admission:
                assert response.status_code == 500
                interrupted = [r for r in records(tmp_path / 'audit') if r.get('interruption')]
                assert [r['interruption'] for r in interrupted] == ['cancelled_after_dispatch']
                assert t['stop'] and t['unknown_held'] == interrupted[0]['reserved_tokens']
                return
            assert response.status_code == 200, response.text
            segments = report(current)['segments']
            assert [s['status'] for s in segments] == ['analyzed'] * 5
            assert all(len(s['attempts']) == 1 for s in segments)
            assert world.peak == 1 and len(world.wires) == 5
            waits = [r['budget_wait'] for r in records(tmp_path / 'audit')]
            assert all(w['where'] == 'before_client_open' and w['ticket'] for w in waits)
            # Waited 0.8 s: inside post_chat, wait plus call would exceed the 1 s model timeout.
            assert max(w['seconds'] for w in waits) > .7
            assert (t['consumed'], t['reserved_live'], t['queued'], t['stop']) == (550, 0, 0, None)
            assert budget.verify(ledger) == []
    asyncio.run(run())


def test_harness_changes_neither_payloads_nor_parallelism_nor_results(world, monkeypatch, tmp_path):
    """Same FORM and SOURCE in two sessions: without the harness, then audited with a budget
    for three concurrent segments (about 381k each, so above the 900k campaign cap). Identical
    wire bytes, the same three concurrent segments, identical validated outputs and cache; the
    only differences are the audit files."""
    monkeypatch.setattr(budget, 'LIMIT', 10**7)
    async def run():
        async with application() as (client, form_id):
            plain = await session(client, form_id)
            assert (await resolve(client, plain)).status_code == 200
            plain_wires, plain_peak = sorted(world.wires), world.peak
            instrument(monkeypatch, tmp_path / 'audit', limit=3 * segment_bound(world))
            world.wires, world.peak = [], 0
            audited = await session(client, form_id)
            assert (await resolve(client, audited)).status_code == 200
        assert sorted(world.wires) == plain_wires and len(plain_wires) == 5
        assert world.peak == plain_peak == 3
        from audit_tools.tests.simulated_compiler import cache, folder, state
        assert cache(audited) == cache(plain) and len(cache(plain)) == 5
        keys = ('status', 'source', 'digest', 'candidate_ids', 'error')
        assert ([{k: s[k] for k in keys} for s in report(audited)['segments']] ==
                [{k: s[k] for k in keys} for s in report(plain)['segments']])
        response = [(folder(s) / state(s)['global_compilation']['artifact_path'].rsplit('/', 1)[1]
                     / 'response.txt').read_text() for s in (plain, audited)]
        assert response[0] == response[1]
        assert all(r['budget_wait']['seconds'] < .5 for r in records(tmp_path / 'audit'))
    asyncio.run(run())


def accelerated(monkeypatch, factor=1000):
    """Audit clock running 1000 times faster: 0.3 s of waiting count as 300 s."""
    real = time.perf_counter
    monkeypatch.setattr(metrics.time, 'perf_counter', lambda: real() * factor)


def test_legitimate_wait_has_no_fixed_limit(tmp_path, monkeypatch):
    async def run():
        metrics.install_transport_observer()
        async def provider(request):
            await asyncio.sleep(.3)
            return httpx.Response(200, json={'usage':USAGE})
        accelerated(monkeypatch)
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            await asyncio.gather(*(metrics.observe(post, client, SETTINGS, BODY, tmp_path,
                rates=RATES, limit=ONE+15, wait_check=lambda: None) for _ in range(2)))
        waits = sorted(r['budget_wait']['seconds'] for r in records(tmp_path))
        assert waits[1] > 120  # On the audit clock: the 02 harness gave up at 120 s.
        assert budget.totals(tmp_path/'budget-ledger.json')['consumed'] == 30
    asyncio.run(run())


def test_impossible_budget_stops_at_once_without_cancelling_the_call_in_flight(tmp_path,
                                                                               monkeypatch):
    async def run():
        metrics.install_transport_observer()
        release = asyncio.Event()
        async def provider(request):
            await release.wait()
            return httpx.Response(200, json={'usage':USAGE})
        accelerated(monkeypatch)
        big = {**BODY, 'messages':[{'role':'user','content':'x'*400}]}
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            def call(body):
                return metrics.observe(post, client, SETTINGS, body, tmp_path, rates=RATES,
                                       limit=budget.bound(big)-1, wait_check=lambda: None)
            first = asyncio.create_task(call(BODY))
            await asyncio.sleep(.05)
            started = time.monotonic()
            with pytest.raises(budget.Refused, match='impossible'):
                await call(big)
            assert time.monotonic() - started < .2 and not first.done()
            release.set()
            assert (await first).status_code == 200
        ledger = tmp_path/'budget-ledger.json'
        t = budget.totals(ledger)
        assert t['stop'].startswith('Budget insufficient') and t['consumed'] == 15
        outcome = sorted((r['outcome'], r.get('refusal'), r['billing']) for r in records(tmp_path))
        assert outcome == [('refused_before_dispatch', 'impossible', 'not_dispatched'),
                           ('response_received', None, 'provider_usage_reported')]
        with pytest.raises(budget.Refused, match='stopped'):
            budget.reserve(ledger, 'after', BODY, budget.bound(big)-1)
    asyncio.run(run())


def test_reservations_of_a_dead_process_are_charged_never_awaited(tmp_path, monkeypatch):
    ledger = tmp_path/'budget-ledger.json'
    ledger.write_text(json.dumps({'limit':2*ONE,'reserve':0,'calls':{'crashed':{
        'reserved':ONE,'charged':ONE,'status':'pending','owner':'4242-gone','analysis':False}},
        'queue':[{'key':'ghost','amount':ONE,'analysis':False,'owner':'4242-gone'}]}))
    async def run():
        metrics.install_transport_observer()
        accelerated(monkeypatch)
        async def provider(request):
            return httpx.Response(200, json={'usage':USAGE})
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            def call():
                return metrics.observe(post, client, SETTINGS, BODY, tmp_path, rates=RATES,
                                       limit=2*ONE, wait_check=lambda: None)
            assert (await call()).status_code == 200  # The dead waiter does not block it.
            started = time.monotonic()
            with pytest.raises(budget.Refused, match='impossible'):
                await call()  # Fits only if the crashed reservation were free credit.
            assert time.monotonic() - started < .2
    asyncio.run(run())
    t = budget.totals(ledger)
    assert (t['reserved_stale'], t['consumed'], t['queued']) == (ONE, 15, 0) and t['stop']


def test_queue_time_cancellation_and_provider_timeouts_are_distinct(tmp_path):
    async def run():
        metrics.install_transport_observer()
        async def provider(request):
            mode = json.loads(request.content)['mode']
            if mode == 'read_timeout':
                raise httpx.ReadTimeout('simulated', request=request)
            await asyncio.sleep(1 if mode == 'slow' else .3)
            return httpx.Response(200, json={'usage':USAGE})
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            def call(root, mode, limit=budget.LIMIT, check=lambda: None):
                return metrics.observe(post, client, SETTINGS, {**BODY, 'mode':mode}, root,
                                       rates=RATES, limit=limit, wait_check=check)
            with pytest.raises(httpx.ReadTimeout):
                await call(tmp_path/'a', 'read_timeout')
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(call(tmp_path/'b', 'slow'), .2)
            limit = budget.bound({**BODY, 'mode':'ok'}) + 15
            holder = asyncio.create_task(call(tmp_path/'c', 'ok', limit))
            await asyncio.sleep(.05)
            with pytest.raises(TimeoutError):  # Cancelled by its caller while waiting in line.
                await asyncio.wait_for(call(tmp_path/'c', 'ok', limit), .1)
            def gate_closed():
                raise AssertionError('Gate closed')
            with pytest.raises(AssertionError, match='Gate closed'):  # Operator ends a wait.
                await call(tmp_path/'c', 'ok', limit, gate_closed)
            await holder
        seen = {name: [(r.get('interruption'), r['outcome'], r['billing'])
                       for r in records(tmp_path/name)] for name in 'abc'}
        assert seen['a'] == [('provider_timeout', 'transport_error_or_uncertain', 'unknown')]
        assert seen['b'] == [('cancelled_after_dispatch', 'transport_error_or_uncertain',
                              'unknown')]
        assert sorted(seen['c'], key=str) == sorted([
            (None, 'response_received', 'provider_usage_reported'),
            (None, 'cancelled_while_queued', 'not_dispatched'),
            (None, 'refused_before_dispatch', 'not_dispatched')], key=str)
        t = budget.totals(tmp_path/'c'/'budget-ledger.json')
        assert (t['consumed'], t['queued'], t['calls'], t['stop']) == (15, 0, 1, None)
    asyncio.run(run())
