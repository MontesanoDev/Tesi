"""Run bounded synthetic cases, never a DeepSeek campaign. Artifacts stay local."""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def wait_http(url, process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError('Isolated service exited: inspect its local log')
        try:
            with urllib.request.urlopen(url,timeout=1) as response:
                if response.status==200:
                    return
        except OSError:
            time.sleep(.2)
    raise RuntimeError('Isolated service did not start')


def stop(process):
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--node',type=Path,required=True)
    parser.add_argument('--playwright',type=Path,required=True)
    parser.add_argument('--backend-port',type=int,default=18081)
    parser.add_argument('--frontend-port',type=int,default=15174)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    env={**os.environ,'MAPI_BACKEND_PORT':str(args.backend_port),'AUDIT_PLAYWRIGHT':str(args.playwright),
         'PYTHON_DOTENV_DISABLED':'1'}
    summaries=[]
    with (out/'frontend.log').open('w') as log:
        frontend=subprocess.Popen([str(args.node),'node_modules/vite/bin/vite.js','--host','127.0.0.1',
            '--port',str(args.frontend_port),'--strictPort'],cwd=root/'frontend',env=env,stdout=log,stderr=log)
        try:
            wait_http(f'http://127.0.0.1:{args.frontend_port}',frontend)
            for case in ('success','http_error','timeout','transport_error','budget'):
                folder=out/case
                with (out/f'{case}-server.log').open('w') as backend_log:
                    backend=subprocess.Popen([sys.executable,'-m','audit_tools.narrator_harness.preflight',
                        '--root',str(folder),'--case',case,'--port',str(args.backend_port)],cwd=root,
                        env=env,stdout=backend_log,stderr=backend_log)
                    try:
                        wait_http(f'http://127.0.0.1:{args.backend_port}/api/projects',backend)
                        browser=subprocess.run([str(args.node),str(root/'audit_tools/narrator_harness/preflight_browser.cjs'),
                            str(folder),f'http://127.0.0.1:{args.frontend_port}',case],cwd=root,env=env,
                            capture_output=True,text=True,timeout=90,check=False)
                        (folder/'browser-process.log').write_text(browser.stdout+browser.stderr)
                        assert browser.returncode==0, f'{case}: browser failed'
                    finally:
                        stop(backend)
                result=json.loads((folder/'browser-result.json').read_text())
                calls=[json.loads(p.read_text()) for p in (folder/'provider-calls').glob('*/metrics.json')]
                assert len(calls)==1, (case,len(calls))
                call=calls[0]
                assert call['simulated'] is True
                if case=='success':
                    assert result['status']==200 and result['response']['generation_status']=='direct'
                elif result['status']==200:
                    assert result['response']['generation_status']=='failed'
                else:
                    assert result['status']>=400
                if case=='success':
                    assert call['measured_tokens']==15
                    assert 'Risposta sintetica di preflight.' in json.dumps(result['response'])
                    for mode in ('async','sync'):
                        for policy,status,hops in [('allowed',200,2),('denied',307,1)]:
                            probe=result['probes'][f'{mode}_{policy}']
                            assert probe=={'status':200,'body':{'status':status,'hops':hops}}
                    assert result['probes']['external_allowed']['body']['blocked']=='Redirect forbidden'
                    assert result['probes']['network_denial']['body']['blocked']==['DNS','connect','connect_ex']
                elif case=='budget':
                    assert not call['transport_started']
                    assert call['billing']=='not_dispatched' and call['measured_tokens']==0
                    assert not (folder/'simulated-provider.jsonl').exists()
                else:
                    assert call['transport_started'] and call['billing']=='unknown'
                    assert call['measured_tokens'] is None and call['budget']['stop']
                summaries.append({'case':case,'api_status':result['status'],
                    'generation_status':result['response'].get('generation_status'),
                    'prepared':1,'transport_started':call['transport_started'],
                    'billing':call['billing'],'measured_tokens_simulated':call['measured_tokens'],
                    'reserved_tokens':call['reserved_tokens'],'seconds':call.get('elapsed_seconds'),
                    'probes':result.get('probes',{}),'external_network':'blocked'})
                print(json.dumps(summaries[-1]),flush=True)
                (out/'summary.json').write_text(json.dumps(summaries,indent=2))
        finally:
            stop(frontend)


if __name__=='__main__':
    main()
