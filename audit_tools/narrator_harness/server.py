"""One isolated real application, transparent observation and pre-call budget gate."""
import asyncio
import contextvars
import functools
import hashlib
import importlib
import inspect
import itertools
import json
import os
import socket
import sqlite3
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

RAW=Path(os.environ['MAPI_AUDIT_DIR']).resolve()
CFG=json.loads((RAW/'config.json').read_text());ROOT=Path(CFG['code_root']);RUNTIME=Path(CFG['runtime'])
os.environ.update(PYTHON_DOTENV_DISABLED='1',MAPI_COMPILATION_PROFILE='sezioni-2026-10-25',
 MAPI_DB_PATH=str(RUNTIME/'runtime.db'),MAPI_STORAGE_PATH=str(RUNTIME/'uploads'),
 MAPI_KNOWLEDGE_PATH=str(RUNTIME/'knowledge'))
sys.path.insert(0,str(ROOT/'backend'))
from .budget import bound,reserve,settle,totals
from app import ai_transport,draft_generation,fact_extraction,generation

assert Path(ai_transport.__file__).resolve().is_relative_to(ROOT/'backend')
scope=contextvars.ContextVar('audit_request',default={})
permit=contextvars.ContextVar('network_reservation',default=None)
phase=contextvars.ContextVar('audit_phase',default=[])
counter=itertools.count(1);requests=itertools.count(1);events=itertools.count(1)
lock=threading.Lock();LEDGER=RAW/'budget-ledger.json'
def utc():return datetime.now(UTC).isoformat()
def save(path,value,secret=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    s=json.dumps(value,ensure_ascii=False,indent=2,default=str)
    if secret:s=s.replace(secret,'[REDACTED]')
    path.write_text(s)
def log(name,value):
    with lock:
        with (RAW/name).open('a') as f:f.write(json.dumps(value,ensure_ascii=False,default=str)+'\n')
def stop(reason):save(RAW/'STOP.json',{'reason':reason,'UTC':utc()})
def frozen():
    freeze=json.loads((RAW/'FREEZE.json').read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items()),'Frozen file changed'
    assert json.loads((RAW/'gate.json').read_text())['open'],'Gate closed'
    assert not (RAW/'STOP.json').exists(),'Campaign stopped'

# Any paid HTTP exchange must carry the reservation established by observed().
import httpx
real_send=httpx.AsyncClient.send
async def send_checked(client,request,*args,**kwargs):
    if request.url.host not in {'127.0.0.1','localhost','::1'}:
        p=permit.get()
        assert p and str(request.url)=='https://api.deepseek.com/chat/completions','Unbudgeted outbound HTTP blocked'
        assert json.loads(request.content)==p['body'],'Outgoing payload changed'
        assert not kwargs.get('follow_redirects',False),'Redirect forbidden'
    return await real_send(client,request,*args,**kwargs)
httpx.AsyncClient.send=send_checked
real_connect=socket.socket.connect
def connect_checked(s,address):
    if isinstance(address,tuple) and address[0] not in {'127.0.0.1','::1','localhost'}:
        assert permit.get(),'Unbudgeted network blocked'
    return real_connect(s,address)
socket.socket.connect=connect_checked

original=ai_transport.post_chat
async def observed(client,settings,body,**kwargs):
    frozen();ctx=scope.get()
    assert ctx.get('project_id')==CFG['project_id'],'Provider call outside test project'
    assert settings.provider=='deepseek' and settings.model=='deepseek-flash'
    assert settings.base_url.rstrip('/')=='https://api.deepseek.com'
    with sqlite3.connect(f'file:{RUNTIME}/runtime.db?mode=ro',uri=True) as db:
        states=[json.loads(r[0]) for r in db.execute('SELECT state_json FROM compilation_sessions')]
    assert len(states)<=1,'More than one experiment session'
    assert all({k:v for k,v in s.get('global_compilation',{}).items() if
                k.endswith('revision') or k=='compilation_profile'}==CFG['profile'] for s in states)
    number=next(counter);assert number<=100,'Maximum safety call count'
    key=f'{number:03d}';folder=RAW/'provider-calls'/key;folder.mkdir(parents=True,exist_ok=False)
    entry={'id':key,'request':ctx,'phase':phase.get(),'start_UTC':utc(),
           'requested_model':settings.model,'reservation':bound(body)}
    save(folder/'request.json',{'body':body,'response_schema':kwargs.get('response_schema')},settings.api_key)
    wait=time.perf_counter()
    while True:
        frozen()
        try:
            reserve(LEDGER,key,body);break
        except RuntimeError:
            with sqlite3.connect(f'file:{RUNTIME}/runtime.db?mode=ro',uri=True):pass
            ledger=json.loads(LEDGER.read_text()) if LEDGER.exists() else {'calls':{}}
            if ledger.get('stop') or not any(c['status']=='pending' for c in ledger['calls'].values()):
                stop('budget exhausted before call');entry.update(forwarded=False,error='BudgetRefused')
                save(folder/'metrics.json',entry);raise
            await asyncio.sleep(.1)  # Budget queue only; requests and model output unchanged.
    entry['budget_wait_seconds']=time.perf_counter()-wait
    token=permit.set({'key':key,'body':body});started=time.perf_counter()
    try:
        response=await original(client,settings,body,**kwargs);await response.aread()
        payload=response.json();usage=payload.get('usage',{})
        save(folder/'response.json',payload,settings.api_key)
        entry.update(forwarded=True,http_status=response.status_code,usage=usage,
                     returned_model=payload.get('model'),system_fingerprint=payload.get('system_fingerprint'),
                     finish_reasons=[c.get('finish_reason') for c in payload.get('choices',[])],
                     payload_unchanged=True)
        settle(LEDGER,key,usage)
        if totals(LEDGER)['stop']:stop(totals(LEDGER)['stop'])
        return response
    except BaseException as exc:
        entry.update(forwarded=True,error=type(exc).__name__)
        settle(LEDGER,key,None);stop('Unknown provider usage: '+type(exc).__name__)
        raise
    finally:
        permit.reset(token);entry.update(end_UTC=utc(),provider_seconds=time.perf_counter()-started)
        save(folder/'metrics.json',entry,settings.api_key)

for mod in [ai_transport,generation,draft_generation,fact_extraction]:mod.post_chat=observed
from app.main import app

# Observe named functions and their imported aliases without changing arguments/results.
TARGETS={
 'intents':['plan_chat_turn','bind_turn_plan'],
 'docx_templates':['inspect_docx','fill_docx'],
 'compilation_catalog':['build_compilation_catalog'],
 'compilation_global':['load_document_corpus','build_global_input','validate_global_proposal'],
 'compilation_segments':['resilient_partition','parse','resilient_merge','segment_input'],
 'compilation_global_sessions':['_prepare','validated_audit','refreshed_audit','_selected','generate_draft','_resilient_proposal'],
 'compilation_global_dialogue':['narrate','_narrate_once','_hold_updates','apply_replies','export_selection','model_context'],
 'compilation_reply_guard':['verify_field_replies'],
 'compilation_source_reuse':['reuse_selected_person'],
 'compilation_scope_review':['blocked_user_fields'],
 'compilation_branch_evidence':['reconcile_branches'],
 'compilation_temporal_hold':['comparison_proof','validate_releases'],
 'compilation_sessions':['save_state'],
}
replacements={}
def wrapper(fn,label):
    def begin():
        event={'id':next(events),'name':label,'request':scope.get(),'start_UTC':utc()}
        return event,time.perf_counter(),phase.set([*phase.get(),label])
    def finish(event,start,token):
        phase.reset(token);event.update(end_UTC=utc(),seconds=time.perf_counter()-start);log('timings.jsonl',event)
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def run(*a,**kw):
            event,start,token=begin()
            try:return await fn(*a,**kw)
            except BaseException as exc:event['error']=type(exc).__name__;raise
            finally:finish(event,start,token)
    else:
        @functools.wraps(fn)
        def run(*a,**kw):
            event,start,token=begin()
            try:
                result=fn(*a,**kw)
                if label=='compilation_sessions.save_state':
                    state=a[2] if len(a)>2 else kw.get('state')
                    save(RAW/'revisions'/f'{event["id"]:06d}.json',{'event':event,'state':state})
                return result
            except BaseException as exc:event['error']=type(exc).__name__;raise
            finally:finish(event,start,token)
    return run
for name,names in TARGETS.items():
    mod=importlib.import_module('app.'+name)
    for n in names:
        fn=getattr(mod,n);replacements[fn]=wrapper(fn,name+'.'+n)
for modname,mod in list(sys.modules.items()):
    if not modname.startswith('app.'):continue
    for name,value in list(vars(mod).items()):
        if inspect.isfunction(value) and value in replacements:setattr(mod,name,replacements[value])

@app.middleware('http')
async def audit_http(request,call_next):
    parts=request.url.path.split('/');pid=parts[3] if len(parts)>3 and parts[2]=='projects' else None
    ctx={'id':next(requests),'project_id':pid,'path':request.url.path,'method':request.method}
    token=scope.set(ctx);started=time.perf_counter();entry={**ctx,'start_UTC':utc()}
    try:
        response=await call_next(request);entry['status']=response.status_code;return response
    except BaseException as exc:entry['error']=type(exc).__name__;raise
    finally:
        if pid==CFG['project_id']:
            with sqlite3.connect(f'file:{RUNTIME}/runtime.db?mode=ro',uri=True) as db:
                db.row_factory=sqlite3.Row
                for row in db.execute('SELECT id,version,state_json FROM compilation_sessions'):
                    save(RAW/'persisted'/f'{ctx["id"]:05d}-v{row["version"]:03d}.json',
                         {'request':ctx,'session_id':row['id'],'version':row['version'],
                          'state':json.loads(row['state_json'])})
        entry.update(end_UTC=utc(),seconds=time.perf_counter()-started)
        log('http.jsonl',entry);scope.reset(token)

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=18080,access_log=False)
