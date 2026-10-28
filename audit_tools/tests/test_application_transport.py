"""Differential test of the unchanged product post_chat, with and without audit."""
import asyncio
import sys
from pathlib import Path

import httpx
import pytest

from audit_tools.narrator_harness import metrics
from audit_tools.tests.test_metrics import BODY, RATES, USAGE


@pytest.mark.parametrize('failure',[None,'http_error','timeout','connection'])
def test_product_requests_and_results_identical(tmp_path,monkeypatch,failure):
    monkeypatch.setenv('PYTHON_DOTENV_DISABLED','1')
    monkeypatch.syspath_prepend(str(Path(__file__).parents[2]/'backend'))
    from app.ai_transport import post_chat
    from app.config import AISettings
    assert Path(sys.modules['app.ai_transport'].__file__).resolve().is_relative_to(
        Path(__file__).parents[2]/'backend')
    settings=AISettings(api_key='synthetic-test-key',model='deepseek-flash',
                        base_url='https://api.deepseek.com',provider='deepseek')
    body={**BODY,'response_format':{'type':'json_object'},'thinking':{'type':'enabled'},'temperature':.1}
    async def run(instrumented):
        wires=[]
        async def provider(request):
            wires.append((str(request.url),request.method,request.content,
                list(request.headers.multi_items()),request.extensions.copy()))
            if failure=='timeout':
                raise httpx.ReadTimeout('synthetic',request=request)
            if failure=='connection':
                raise httpx.ConnectError('synthetic',request=request)
            return httpx.Response(503 if failure=='http_error' else 200,json={'usage':USAGE})
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),follow_redirects=False,
                                      timeout=httpx.Timeout(19,connect=3)) as client:
            try:
                r=(await metrics.observe(post_chat,client,settings,body,tmp_path,rates=RATES)
                   if instrumented else await post_chat(client,settings,body))
                result=(r.status_code,r.content,list(r.headers.multi_items()))
            except httpx.HTTPError as e:
                result=(type(e).__name__,str(e))
        return wires,result
    metrics.install_transport_observer()
    assert asyncio.run(run(False))==asyncio.run(run(True))
