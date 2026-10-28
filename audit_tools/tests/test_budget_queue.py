"""Fix 1: concurrent reservations queue in FIFO order; the analysis never takes the reserve."""
import asyncio
import json

import httpx
import pytest

from audit_tools.narrator_harness import budget, metrics
from audit_tools.tests.test_metrics import RATES, SETTINGS, USAGE, post

BODY = {'model':'deepseek-flash','messages':[{'role':'user','content':'synthetic'}],'max_tokens':20}
ONE = budget.bound(BODY)


def body(size):
    return {**BODY, 'messages':[{'role':'user','content':'x'*size}]}


def test_fifo_line_is_never_overtaken(tmp_path):
    p = tmp_path/'l.json'; big = body(400); limit = budget.bound(big)
    assert budget.enqueue(p, 'small-0', ONE, limit=limit)
    assert not budget.enqueue(p, 'big', budget.bound(big), limit=limit)
    # It would fit next to small-0, but big waits first.
    assert not budget.enqueue(p, 'small-1', ONE, limit=limit)
    budget.settle(p, 'small-0', {'prompt_tokens':0,'completion_tokens':0,'total_tokens':0})
    assert not budget.enqueue(p, 'small-1', ONE, limit=limit)
    assert budget.enqueue(p, 'big', budget.bound(big), limit=limit)
    budget.settle(p, 'big', {'prompt_tokens':1,'completion_tokens':1,'total_tokens':2})
    assert budget.enqueue(p, 'small-1', ONE, limit=limit)
    assert budget.totals(p)['queued'] == 0 and budget.verify(p) == []


def test_analysis_never_commits_the_reserve(tmp_path):
    p = tmp_path/'l.json'; limit = 3*ONE; reserve = ONE + 1
    kw = {'limit': limit, 'reserve_tokens': reserve}
    assert budget.enqueue(p, 'segment-1', ONE, analysis=True, **kw)
    assert not budget.enqueue(p, 'segment-2', ONE, analysis=True, **kw)  # Would enter the reserve.
    with pytest.raises(budget.Refused, match='busy'):
        budget.reserve(p, 'segment-3', BODY, limit, reserve_tokens=reserve, analysis=True)
    budget.withdraw(p, 'segment-2')
    assert budget.enqueue(p, 'narrator', ONE, **kw)  # Later phases may use the reserve.
    assert budget.totals(p)['committed'] == 2*ONE and budget.verify(p) == []
    with pytest.raises(AssertionError, match='reserve changed'):
        budget.enqueue(p, 'other', ONE, limit=limit, reserve_tokens=0)


def test_reservation_usage_and_uncertainty_are_separate(tmp_path):
    p = tmp_path/'l.json'
    for key in 'abc':
        budget.reserve(p, key, BODY)
    budget.settle(p, 'a', {'prompt_tokens':10,'completion_tokens':5,'total_tokens':15})
    budget.cancel_unstarted(p, 'b')
    t = budget.totals(p)
    assert (t['consumed'], t['reserved_live'], t['unknown_held']) == (15, ONE, 0)
    assert t['committed'] == t['charged'] == 15 + ONE and t['available'] == budget.LIMIT - 15 - ONE
    budget.settle(p, 'c', None)
    t = budget.totals(p)
    assert (t['consumed'], t['reserved_live'], t['unknown_held']) == (15, 0, ONE) and t['stop']
    assert t['provider_reported'] == 15  # Never the reservation held for the uncertain call.


def test_carry_over_charges_but_never_credits(tmp_path):
    old = tmp_path/'old.json'
    old.write_text(json.dumps({'limit':budget.LIMIT,'stop':None,'calls':{
        'a':{'reserved':500,'charged':40,'status':'measured','usage':{'total_tokens':40}},
        'b':{'reserved':500,'charged':0,'status':'not_dispatched','usage':None},
        'c':{'reserved':500,'charged':500,'status':'unknown_fully_charged'}}}))
    p = tmp_path/'new.json'
    assert budget.carry(p, old, reserve_tokens=10) == 540
    t = budget.totals(p)
    assert (t['carried'], t['consumed'], t['committed'], t['reserve']) == (540, 0, 540, 10)
    with pytest.raises(AssertionError, match='new ledger'):
        budget.carry(p, old, reserve_tokens=10)


def test_three_concurrent_calls_queue_without_crash(tmp_path):
    """Budget for one call at a time: the three calls run one after another, in order."""
    async def run():
        metrics.install_transport_observer()
        flight, peak, order = [0], [0], []
        async def provider(request):
            flight[0] += 1; order.append(json.loads(request.content)['n'])
            peak[0] = max(peak[0], flight[0])
            await asyncio.sleep(.15)
            flight[0] -= 1
            return httpx.Response(200, json={'usage':USAGE})
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            async def one(n):
                await asyncio.sleep(.02*n)  # Deterministic arrival order.
                return await metrics.observe(post, client, SETTINGS, {**BODY, 'n':n}, tmp_path,
                    rates=RATES, limit=budget.bound({**BODY,'n':0})+40, analysis=True,
                    wait_check=lambda: None)
            responses = await asyncio.gather(*(one(n) for n in range(3)))
        assert [r.status_code for r in responses] == [200]*3
        assert peak[0] == 1 and order == [0, 1, 2]
        ledger = tmp_path/'budget-ledger.json'
        t = budget.totals(ledger)
        assert (t['consumed'], t['reserved_live'], t['queued']) == (45, 0, 0)
        assert budget.verify(ledger) == []
        records = [json.loads(p.read_text()) for p in (tmp_path/'provider-calls').glob('*/metrics.json')]
        assert sorted(r['measured_tokens'] for r in records) == [15]*3
        assert sum('queued_UTC' in r for r in records) == 2
    asyncio.run(run())


def test_cancelled_waiter_leaves_the_line(tmp_path):
    async def run():
        metrics.install_transport_observer()
        release = asyncio.Event()
        async def provider(request):
            await release.wait()
            return httpx.Response(200, json={'usage':USAGE})
        limit = ONE + 15
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            def call():
                return metrics.observe(post, client, SETTINGS, BODY, tmp_path, rates=RATES,
                                       limit=limit, wait_check=lambda: None)
            first = asyncio.create_task(call()); await asyncio.sleep(.05)
            waiter = asyncio.create_task(call()); await asyncio.sleep(.25)
            waiter.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiter
            third = asyncio.create_task(call()); await asyncio.sleep(.05)
            release.set()
            await asyncio.gather(first, third)
        t = budget.totals(tmp_path/'budget-ledger.json')
        assert (t['consumed'], t['queued'], t['calls']) == (30, 0, 2)
    asyncio.run(run())
