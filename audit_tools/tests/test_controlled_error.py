"""Fix 3: an irreversible stop aborts the analysis with a controlled error; nothing is cancelled.

The unchanged candidate keeps running the segments already in flight after the analysis has
failed: their answers are validated, cached and accounted, and a resumption calls only the
segments still missing. The harness adds no cancellation; it only decides the HTTP outcome.
"""
import asyncio

import httpx
import pytest

from audit_tools.narrator_harness import budget, metrics
from audit_tools.tests.simulated_compiler import (
    adapter,
    application,
    cache,
    instrument,
    records,
    report,
    resolve,
    segment_bound,
    session,
    settled,
    state,
    world,
)

__all__ = ['world']


async def sized(client, form_id, provider):
    """An unaudited analysis of the same FORM, only to size the segment reservations."""
    provider.default_delay = .01
    assert (await resolve(client, await session(client, form_id))).status_code == 200
    bound = segment_bound(provider)
    provider.wires, provider.peak, provider.default_delay = [], 0, .3
    return bound


def ledger_statuses(ledger):
    with budget.locked(ledger) as data:
        return sorted(c['status'] for c in data['calls'].values()), data.get('refusals', [])


@pytest.mark.parametrize('controlled', [False, True])
def test_stop_aborts_the_analysis_and_keeps_the_work_in_flight(world, monkeypatch, tmp_path,
                                                               controlled):
    """Segments 2 and 3 in flight together; segment 2 answers validly without usage, so the
    campaign stops (preregistered rule) while segment 3 is still running and 4 waits."""
    async def run():
        async with application() as (client, form_id):
            limit = 2 * await sized(client, form_id, world) + 5000
            world.delay, world.usage = {1: .1, 2: .2, 3: .6, 4: .1, 5: .1}, {2: None}
            ledger = instrument(monkeypatch, tmp_path / 'audit', limit=limit,
                                on_refusal=metrics.controlled if controlled else None)
            current = await session(client, form_id)
            response = await resolve(client, current)
            in_flight = world.flight
            await settled(ledger)
            return current, response, in_flight, ledger
    current, response, in_flight, ledger = asyncio.run(run())
    if controlled:
        assert response.status_code == 503
        assert 'non inviata al provider (stopped)' in response.json()['detail']
    else:
        assert response.status_code == 500  # The 02 harness: an unhandled RuntimeError.
    assert in_flight == 1  # Segment 3 was not cancelled by the failure.
    assert sorted(cache(current)) == [1, 2, 3]  # Valid answers kept, including the late one.
    stored = state(current)
    assert stored['status'] == 'FAILED' and stored['global_compilation']['audit'] is None
    assert sorted(i for i, _ in world.wires) == [1, 2, 3]  # Nothing sent after the stop.
    statuses, refusals = ledger_statuses(ledger)
    assert statuses == ['measured', 'measured', 'unknown_fully_charged']
    assert refusals and {r['kind'] for r in refusals} == {'stopped'}
    t = budget.totals(ledger)
    assert (t['consumed'], t['reserved_live'], t['queued']) == (220, 0, 0)
    assert t['unknown_held'] == t['committed'] - 220 and budget.verify(ledger) == []
    late = [r for r in records(tmp_path / 'audit') if r['transport_started']]
    assert all('interruption' not in r for r in late)  # Every dispatched call ran to its end.


def test_resumption_after_the_stop_calls_only_the_missing_segments(world, monkeypatch, tmp_path):
    """Recovery of the same session: a new ledger carries the stopped one's charges (never its
    credit); cached segments are reused and only segments 4 and 5 reach the provider."""
    async def run():
        async with application() as (client, form_id):
            limit = 2 * await sized(client, form_id, world) + 5000
            world.delay, world.usage = {1: .1, 2: .2, 3: .6, 4: .1, 5: .1}, {2: None}
            stopped = instrument(monkeypatch, tmp_path / 'stopped', limit=limit,
                                 on_refusal=metrics.controlled)
            current = await session(client, form_id)
            assert (await resolve(client, current)).status_code == 503
            await settled(stopped)
            world.wires, world.usage = [], {}
            resumed = tmp_path / 'resumed'
            carried = budget.carry(resumed / 'budget-ledger.json', stopped, limit=limit)
            ledger = instrument(monkeypatch, resumed, limit=limit, on_refusal=metrics.controlled)
            version = (await client.get(f'/api/projects/alpha/compilation-sessions/'
                                        f'{current["id"]}')).json()['version']
            again = adapter.control_session('alpha', current['id'], version, 'resume')
            response = await resolve(client, again)
            return current, response, carried, ledger
    current, response, carried, ledger = asyncio.run(run())
    assert response.status_code == 200, response.text
    segments = report(current)['segments']
    assert [(s['status'], s['source']) for s in segments] == [
        ('analyzed', 'cache')] * 3 + [('analyzed', 'called')] * 2
    assert sorted(i for i, _ in world.wires) == [4, 5]
    t = budget.totals(ledger)
    assert (t['carried'], t['consumed'], t['stop']) == (carried, 220, None)
    assert carried == budget.totals(tmp_path / 'stopped' / 'budget-ledger.json')['committed']
    assert budget.verify(ledger) == []


@pytest.mark.parametrize('audited', [False, True])
def test_irreversible_segment_failure_with_and_without_the_harness(world, monkeypatch, tmp_path,
                                                                   audited):
    """Segment 4 fails at the transport on every attempt while 2 and 3 are in flight.
    Unaudited, the candidate retries once and merges the other four (partial analysis).
    Audited, the failure has no usage: the preregistered stop refuses the retry, the analysis
    ends with the controlled error, and segments 2 and 3 still complete and are cached."""
    async def run():
        async with application() as (client, form_id):
            limit = 4 * await sized(client, form_id, world)
            monkeypatch.setattr(budget, 'LIMIT', limit)  # Room for all concurrent segments.
            world.plan, world.delay = {4: httpx.ConnectError('simulated')}, {4: .05}
            ledger = instrument(monkeypatch, tmp_path / 'audit', limit=limit,
                                on_refusal=metrics.controlled) if audited else None
            current = await session(client, form_id)
            response = await resolve(client, current)
            in_flight = world.flight
            if audited:
                await settled(ledger)
            return current, response, in_flight, ledger
    current, response, in_flight, ledger = asyncio.run(run())
    if not audited:
        assert response.status_code == 200
        segments = report(current)['segments']
        assert [s['status'] for s in segments] == ['analyzed'] * 3 + ['failed', 'analyzed']
        assert len(segments[3]['attempts']) == 2 and len(world.wires) == 6
        return
    assert response.status_code == 503 and in_flight == 2
    assert sorted(cache(current)) == [1, 2, 3]
    assert sorted(i for i, _ in world.wires) == [1, 2, 3, 4]  # The retry was never sent.
    statuses, refusals = ledger_statuses(ledger)
    assert statuses == ['measured'] * 3 + ['unknown_fully_charged']
    assert {r['kind'] for r in refusals} == {'stopped'}
    assert budget.totals(ledger)['reserved_live'] == 0
