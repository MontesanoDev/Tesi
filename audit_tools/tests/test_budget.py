from concurrent.futures import ThreadPoolExecutor

import pytest

from audit_tools.narrator_harness.budget import bound, reserve, settle, totals


def body():return {'model':'deepseek-flash','messages':[{'role':'user','content':'prova à è €'}], 'max_tokens':1000}
def test_reservation_before_send(tmp_path):
    p=tmp_path/'ledger.json';reserve(p,'one',body());assert totals(p)['charged']==bound(body())
    settle(p,'one',{'prompt_tokens':30,'completion_tokens':20,'total_tokens':50})
    assert totals(p)['charged']==50
def test_unknown_charges_full_and_stops(tmp_path):
    p=tmp_path/'l.json';reserve(p,'a',body());settle(p,'a',{})
    assert totals(p)['charged']==bound(body())
    with pytest.raises(RuntimeError):reserve(p,'b',body())
def test_over_limit_never_reserved(tmp_path):
    p=tmp_path/'l.json';b=body();b['messages'][0]['content']='x'*500000
    with pytest.raises(RuntimeError,match='impossible'):reserve(p,'a',b)
    t=totals(p);assert t['charged']==0 and t['calls']==0 and t['refusals']==1
    assert t['stop'].startswith('Budget insufficient')  # It can never fit: campaign stopped.
    with pytest.raises(RuntimeError,match='stopped'):reserve(p,'b',body())
def test_atomic_concurrent_reservations(tmp_path):
    p=tmp_path/'l.json'
    def one(i):
        try:reserve(p,str(i),body());return True
        except RuntimeError:return False
    with ThreadPoolExecutor(8) as pool:accepted=sum(pool.map(one,range(40)))
    assert accepted>0 and totals(p)['charged']<=900000
def test_both_input_and_reasoning_output_count(tmp_path):
    p=tmp_path/'l.json';reserve(p,'a',body())
    settle(p,'a',{'prompt_tokens':30,'completion_tokens':20,'total_tokens':50,
        'prompt_cache_hit_tokens':30,'completion_tokens_details':{'reasoning_tokens':15}})
    assert totals(p)['charged']==50
@pytest.mark.parametrize('mutation',['no_cap','image','stream','other_model','tools'])
def test_unbounded_request_rejected(mutation):
    b=body()
    if mutation=='no_cap':b.pop('max_tokens')
    elif mutation=='image':b['messages'][0]['content']=[{'type':'image_url'}]
    elif mutation=='stream':b['stream']=True
    elif mutation=='other_model':b['model']='other'
    else:b['tools']=[{'type':'function'}]
    with pytest.raises(AssertionError):bound(b)
def test_provider_bound_violation_stops(tmp_path):
    p=tmp_path/'l.json';n=reserve(p,'a',body());settle(p,'a',{'prompt_tokens':n,'completion_tokens':1,'total_tokens':n+1})
    assert totals(p)['stop']
    with pytest.raises(RuntimeError):reserve(p,'b',body())
def test_campaign_limit_comes_from_config_up_to_the_cap(tmp_path):
    from audit_tools.narrator_harness.budget import CAP
    p=tmp_path/'l.json';reserve(p,'a',body(),CAP);assert totals(p)['limit']==CAP==3_000_000
    with pytest.raises(AssertionError):reserve(tmp_path/'m.json','a',body(),CAP+1)
