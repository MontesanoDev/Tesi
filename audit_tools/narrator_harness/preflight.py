"""OFFLINE ONLY: real app with synthetic database and deny-all external transport.

No original data, keys, prompts or app modules are edited. Production post_chat
continues to build its own requests; the selected HTTPX transport is simulated.
"""
import argparse
import hashlib
import json
import os
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx

CASES = ('success', 'http_error', 'timeout', 'transport_error', 'budget')
USAGE = {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15,
         'prompt_cache_hit_tokens': 4, 'prompt_cache_miss_tokens': 6,
         'completion_tokens_details': {'reasoning_tokens': 3}}
BODY = {'model': 'deepseek-flash', 'messages': [{'role': 'user', 'content': 'synthetic probe'}],
        'max_tokens': 20}
LOOPBACK = {'127.0.0.1', '::1', 'localhost'}


def install_network_denial(log):
    """Block DNS/connect/connect_ex even if the HTTPX interceptor is bypassed."""
    real_dns, real_connect, real_ex = socket.getaddrinfo, socket.socket.connect, socket.socket.connect_ex
    def check(host, operation):
        if isinstance(host, bytes):
            host = host.decode('ascii')
        if host not in LOOPBACK:
            log('network-denials.jsonl', {'operation': operation, 'host': str(host)})
            raise PermissionError('Offline preflight: non-loopback network forbidden')
    def dns(host, *a, **kw):
        check(host, 'DNS')
        return real_dns(host, *a, **kw)
    def connect(s, address):
        if isinstance(address, tuple):
            check(address[0], 'connect')
        return real_connect(s, address)
    def connect_ex(s, address):
        if isinstance(address, tuple):
            check(address[0], 'connect_ex')
        return real_ex(s, address)
    socket.getaddrinfo, socket.socket.connect, socket.socket.connect_ex = dns, connect, connect_ex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, required=True)
    parser.add_argument('--port', type=int, default=18081)
    args = parser.parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    def write(name, data):
        (root/name).write_text(json.dumps(data, indent=2))
    def log(name, data):
        with (root/name).open('a') as f:
            f.write(json.dumps(data)+'\n')
    install_network_denial(log)
    runtime = root/'runtime'
    runtime.mkdir()
    code = Path(__file__).resolve().parents[2]
    os.environ.update(PYTHON_DOTENV_DISABLED='1', MAPI_AUDIT_DIR=str(root),
        MAPI_DB_PATH=str(runtime/'runtime.db'), MAPI_STORAGE_PATH=str(runtime/'uploads'),
        MAPI_KNOWLEDGE_PATH=str(runtime/'knowledge'), MAPI_COMPILATION_PROFILE='sezioni-2026-10-25')
    sys.path.insert(0, str(code/'backend'))
    from app.ai_profiles import ProfileInput, save_profile
    from app.compilation_profile import new_session_flags
    from app.db import connection, init_database
    init_database()
    with connection() as db:
        db.execute("INSERT INTO projects (id,title,description,status,status_tone,updated_label,instructions) "
                   "VALUES ('preflight','Synthetic audit preflight','','active','blue','today','')")
        db.execute("INSERT OR REPLACE INTO app_metadata VALUES ('demo_projects_initialized','1')")
    save_profile(ProfileInput(name='SIMULATED ONLY', provider='deepseek',
        model='deepseek-flash', base_url='https://api.deepseek.com', api_key='synthetic-never-valid',
        context_window=1048576))
    write('config.json', {'code_root':str(code),'runtime':str(runtime),'project_id':'preflight',
        'profile':new_session_flags(),'case':args.case,'simulated':True})
    files=[*sorted((code/'backend/app').glob('*.py')),
           *sorted((code/'audit_tools/narrator_harness').glob('*.py'))]
    write('FREEZE.json', {'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
    write('gate.json', {'open':True,'simulated_only':True})
    if args.case=='budget':
        write('budget-ledger.json', {'limit':900000,'calls':{'synthetic-prior-usage':
            {'reserved':900000,'charged':900000,'status':'measured',
             'usage':{'prompt_tokens':900000,'completion_tokens':0,'total_tokens':900000}}}})
    count=0
    def provider(request):
        nonlocal count
        count+=1
        log('simulated-provider.jsonl', {'call':count,'url':str(request.url),'method':request.method,
            'body_sha256':hashlib.sha256(request.content).hexdigest(),
            'headers':{k:v for k,v in request.headers.items() if k.lower()!='authorization'},
            'authorization_present':'authorization' in request.headers,'extensions':request.extensions})
        if request.url.host in LOOPBACK:
            return (httpx.Response(307,headers={'location':'/final'},json={'usage':USAGE})
                if request.url.path=='/redirect' else httpx.Response(200,json={'usage':USAGE}))
        assert str(request.url)=='https://api.deepseek.com/chat/completions'
        if args.case=='timeout':
            raise httpx.ReadTimeout('Synthetic timeout after transport entry',request=request)
        if args.case=='transport_error':
            raise httpx.ConnectError('Synthetic transport error',request=request)
        if args.case=='http_error':
            return httpx.Response(503,json={'error':{'message':'Synthetic provider unavailable'}})
        plan={'intent':'reply','answer':'Risposta sintetica di preflight.', 'queries':[],
              'target':'source','form_id':None,'source_queries':[],'replies':[]}
        return httpx.Response(200,json={'model':'deepseek-flash','usage':USAGE,'choices':[
            {'message':{'content':json.dumps(plan)},'finish_reason':'stop'}]})
    fake=httpx.MockTransport(provider)
    # No fallback to real transport is possible inside these clients.
    httpx.AsyncClient._transport_for_url=lambda self,url:fake
    httpx.Client._transport_for_url=lambda self,url:fake
    from . import server
    # Explicitly label every measurement as simulated, without changing post_chat/body.
    observe=server.metrics.observe
    async def simulated_observe(*a,**kw):
        kw['simulated']=True
        return await observe(*a,**kw)
    server.metrics.observe=simulated_observe

    @server.app.post('/api/__audit-probe/{case}')
    async def probe(case: str):
        """Preflight-only diagnostics, absent from all product modules."""
        folder=root/'probes'/case
        if folder.exists():
            return {'error':'duplicate probe refused'}
        folder.mkdir(parents=True)
        if case=='network_denial':
            checks=[]
            operations=[('DNS',lambda:socket.getaddrinfo('api.deepseek.com',443)),
                ('connect',lambda:socket.socket().connect(('192.0.2.1',443))),
                ('connect_ex',lambda:socket.socket().connect_ex(('192.0.2.1',443)))]
            for name,operation in operations:
                try:
                    operation()
                except (PermissionError,AssertionError):
                    checks.append(name)
            return {'blocked':checks}
        asynchronous=not case.startswith('sync_')
        follow=case.endswith('_allowed')
        explicit=case.startswith('external_')
        settings=SimpleNamespace(api_key='')
        if explicit:
            tok=server.permit.set({'body':BODY})
        try:
            if asynchronous:
                async with httpx.AsyncClient(follow_redirects=follow,timeout=7) as client:
                    async def operation(c,s,b):
                        url='https://api.deepseek.com/chat/completions' if explicit else 'http://localhost/redirect'
                        return await c.post(url,json=b)
                    try:
                        response=await server.metrics.observe(operation,client,settings,BODY,folder,simulated=True)
                        return {'status':response.status_code,'hops':len(response.history)+1}
                    except AssertionError as exc:
                        return {'blocked':str(exc)}
            else:
                with httpx.Client(follow_redirects=follow,timeout=7) as client:
                    response=server.metrics.observe_sync(lambda:client.post('http://localhost/redirect',json=BODY),BODY,folder,simulated=True)
                    return {'status':response.status_code,'hops':len(response.history)+1}
        finally:
            if explicit:
                server.permit.reset(tok)
    import uvicorn
    uvicorn.run(server.app,host='127.0.0.1',port=args.port,access_log=False)


if __name__=='__main__':
    main()
