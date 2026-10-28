import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from audit_tools.narrator_harness import budget, metrics

BODY = {'model':'deepseek-flash','messages':[{'role':'user','content':'synthetic'}], 'max_tokens':20}
USAGE = {'prompt_tokens':10,'completion_tokens':5,'total_tokens':15,
         'prompt_cache_hit_tokens':4,'prompt_cache_miss_tokens':6,
         'completion_tokens_details':{'reasoning_tokens':3}}
RATES = {'cache_hit':.006,'cache_miss':.3,'output':1.2}
URL = 'https://provider.invalid/chat/completions'
SETTINGS = SimpleNamespace(api_key='synthetic-test-key')


def result(root):
    return json.loads(next((root/'provider-calls').glob('*/metrics.json')).read_text())


async def post(client, settings, body):
    return await client.post(URL, json=body, headers={'Authorization':'Bearer synthetic-test-key'})


@pytest.mark.parametrize('case',['success','http_error','timeout','transport_error','before_dispatch',
                                  'bad_usage','no_usage','budget','body_read_error'])
def test_actual_transport_accounting(tmp_path, case):
    async def run():
        dispatched=[]
        class BrokenBody(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield b'{'
                raise httpx.ReadError('simulated body failure')
        async def provider(request):
            dispatched.append(request)
            if case=='timeout':raise httpx.ReadTimeout('simulated',request=request)
            if case=='transport_error':raise httpx.ConnectError('simulated',request=request)
            if case=='body_read_error':return httpx.Response(200,stream=BrokenBody())
            usage={**USAGE,'total_tokens':99} if case=='bad_usage' else USAGE
            return httpx.Response(503 if case=='http_error' else 200,
                                  json={} if case=='no_usage' else {'usage':usage})
        def before(request):
            if case=='before_dispatch':raise RuntimeError('Rejected before any transport')
        metrics.install_transport_observer()
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            try:
                await metrics.observe(post,client,SETTINGS,BODY,tmp_path,rates=RATES,
                    before_dispatch=before,limit=1 if case=='budget' else budget.LIMIT)
            except (httpx.HTTPError,RuntimeError):
                assert case in {'timeout','transport_error','before_dispatch','budget','body_read_error'}
        r=result(tmp_path)
        assert len(dispatched)==(0 if case in {'before_dispatch','budget'} else 1)
        if not dispatched:
            assert r['transport_started'] is False and r['estimated_cost_USD']==0
            assert budget.totals(tmp_path/'budget-ledger.json')['charged']==0
        elif case in {'timeout','transport_error','bad_usage','no_usage','body_read_error'}:
            assert r['billing']=='unknown' and r['measured_tokens'] is None
            assert r['estimated_cost_USD'] is None
            assert r['budget']['charged']==budget.bound(BODY) and r['budget']['stop']
        else:
            assert r['billing']=='provider_usage_reported' and r['measured_tokens']==15
            assert r['budget']['charged']==15 and r['estimated_cost_USD']>0
            assert r['transports'][0]['status']==(503 if case=='http_error' else 200)
        text=''.join(p.read_text() for p in (tmp_path/'provider-calls').rglob('*.json'))
        assert 'synthetic-test-key' not in text
    asyncio.run(run())


@pytest.mark.parametrize('synchronous',[False,True])
@pytest.mark.parametrize('redirect',[False,True])
def test_parameters_hooks_redirects_and_timeout_are_unchanged(tmp_path,synchronous,redirect):
    def snapshot(r):
        return {'url':str(r.url),'method':r.method,'body':r.content,
                'headers':list(r.headers.multi_items()),'extensions':r.extensions.copy()}
    async def asynchronous(observed):
        seen=[];hooks=[]
        async def provider(r):
            seen.append(snapshot(r))
            return (httpx.Response(307,headers={'location':'/final'},json={'usage':USAGE})
                if r.url.path=='/chat/completions' else httpx.Response(200,json={'usage':USAGE}))
        async def req_hook(r):hooks.append('request:'+r.url.path)
        async def res_hook(r):hooks.append('response:'+str(r.status_code))
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),follow_redirects=redirect,
             timeout=httpx.Timeout(7,connect=2),headers={'X-Application':'unchanged'},
             event_hooks={'request':[req_hook],'response':[res_hook]}) as client:
            response=(await metrics.observe(post,client,SETTINGS,BODY,tmp_path,rates=RATES)
                      if observed else await post(client,SETTINGS,BODY))
        return seen,hooks,response.status_code
    def sync(observed):
        seen=[];hooks=[]
        def provider(r):
            seen.append(snapshot(r))
            return (httpx.Response(307,headers={'location':'/final'},json={'usage':USAGE})
                if r.url.path=='/chat/completions' else httpx.Response(200,json={'usage':USAGE}))
        with httpx.Client(transport=httpx.MockTransport(provider),follow_redirects=redirect,
             timeout=httpx.Timeout(7,connect=2),headers={'X-Application':'unchanged'},
             event_hooks={'request':[lambda r:hooks.append('request:'+r.url.path)],
                          'response':[lambda r:hooks.append('response:'+str(r.status_code))]}) as client:
            operation=lambda:client.post(URL,json=BODY,headers={'Authorization':'Bearer synthetic-test-key'})
            response=metrics.observe_sync(operation,BODY,tmp_path,rates=RATES) if observed else operation()
        return seen,hooks,response.status_code
    metrics.install_transport_observer()
    before=sync(False) if synchronous else asyncio.run(asynchronous(False))
    after=sync(True) if synchronous else asyncio.run(asynchronous(True))
    assert before==after
    r=result(tmp_path)
    assert len(r['transports'])==(2 if redirect else 1)
    assert r['measured_tokens']==15*len(r['transports'])
    assert r['reserved_tokens']==budget.bound(BODY)*len(r['transports'])


def test_second_redirect_hop_cannot_bypass_budget(tmp_path):
    metrics.install_transport_observer()
    calls=[]
    def provider(r):
        calls.append(r)
        return httpx.Response(307,headers={'location':'/final'},json={'usage':USAGE})
    with (httpx.Client(transport=httpx.MockTransport(provider),follow_redirects=True) as client,
          pytest.raises(RuntimeError,match='Budget')):
            metrics.observe_sync(lambda:client.post(URL,json=BODY),BODY,tmp_path,
                                 limit=budget.bound(BODY),rates=RATES)
    assert len(calls)==1
    assert result(tmp_path)['measured_tokens']==15


def test_cancelled_transport_is_not_free(tmp_path):
    async def run():
        async def provider(request):
            raise asyncio.CancelledError()
        metrics.install_transport_observer()
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            with pytest.raises(asyncio.CancelledError):
                await metrics.observe(post,client,SETTINGS,BODY,tmp_path)
        assert result(tmp_path)['billing']=='unknown'
        assert result(tmp_path)['budget']['charged']==budget.bound(BODY)
    asyncio.run(run())


def test_waiting_reservation_is_not_a_failed_request(tmp_path):
    async def run():
        metrics.install_transport_observer()
        async def provider(request):
            await asyncio.sleep(.15)
            return httpx.Response(200,json={'usage':USAGE})
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            await asyncio.gather(*(metrics.observe(post,client,SETTINGS,BODY,tmp_path,
                limit=budget.bound(BODY)+15,wait_check=lambda:None) for _ in range(2)))
        records=[json.loads(p.read_text()) for p in (tmp_path/'provider-calls').glob('*/metrics.json')]
        assert len(records)==2 and all('error' not in r for r in records)
        assert all(r['billing']=='provider_usage_reported' for r in records)
        assert budget.totals(tmp_path/'budget-ledger.json')['charged']==30
    asyncio.run(run())


@pytest.mark.parametrize('details',[['not an object'], {'reasoning_tokens':6}, {'reasoning_tokens':True}])
def test_malformed_reasoning_is_unknown(details):
    response=httpx.Response(200,json={'usage':{**USAGE,'completion_tokens_details':details}})
    assert metrics.usage_of(response) is None
