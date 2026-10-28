"""Exercise the actual guard without starting an app or reading private configuration."""
import ast
import asyncio
import contextvars
import inspect
import json
from pathlib import Path

import httpx
import pytest

SERVER = Path(__file__).parents[1] / 'narrator_harness/server.py'
URL = 'https://api.deepseek.com/chat/completions'
BODY = {'model': 'deepseek-flash', 'messages': [{'role': 'user', 'content': 'synthetic'}],
        'max_tokens': 20}


def guard():
    tree = ast.parse(SERVER.read_text())
    names = {'send_checked', 'effective_redirects'}
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and n.name in names]
    permit = contextvars.ContextVar('test_reservation', default=None)
    permit.set({'body': BODY})
    scope = {'httpx': httpx, 'json': json, 'inspect': inspect, 'permit': permit,
             'real_send': httpx.AsyncClient.send}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SERVER), 'exec'), scope)  # noqa: S102 - only locally versioned AST functions
    return scope['send_checked']


@pytest.mark.parametrize('client_default,explicit,allowed', [
    (False, 'default', True), (True, 'default', False),
    (False, False, True), (True, False, True),
    (False, True, False), (True, True, False),
])
def test_actual_async_guard_respects_httpx_redirect_semantics(monkeypatch, client_default,
                                                            explicit, allowed):
    async def run():
        calls = []
        async def provider(request):
            calls.append(request)
            return httpx.Response(200, json={'ok': True})
        checked = guard()
        monkeypatch.setattr(httpx.AsyncClient, 'send', checked)
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                                     follow_redirects=client_default) as client:
            kwargs = {} if explicit == 'default' else {'follow_redirects': explicit}
            if allowed:
                response = await client.post(URL, json=BODY, **kwargs)
                assert response.status_code == 200 and len(calls) == 1
                assert json.loads(calls[0].content) == BODY
            else:
                with pytest.raises(AssertionError, match='Redirect forbidden'):
                    await client.post(URL, json=BODY, **kwargs)
                assert not calls
    asyncio.run(run())


def test_local_redirect_follows_only_when_requested(monkeypatch):
    async def run():
        calls = []
        async def provider(request):
            calls.append(str(request.url))
            return (httpx.Response(307, headers={'location': '/end'}) if request.url.path == '/begin'
                    else httpx.Response(200, json={'ok': True}))
        monkeypatch.setattr(httpx.AsyncClient, 'send', guard())
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            assert (await client.get('http://localhost/begin')).status_code == 307
            assert len(calls) == 1
            assert (await client.get('http://localhost/begin', follow_redirects=True)).status_code == 200
            assert calls[-2:] == ['http://localhost/begin', 'http://localhost/end']
    asyncio.run(run())


@pytest.mark.parametrize('default,explicit,expected', [(False, 'default', False),
    (True, 'default', True), (True, False, False), (False, True, True)])
def test_sync_client_uses_the_same_resolution(default, explicit, expected):
    tree = ast.parse(SERVER.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'effective_redirects')
    scope = {'httpx': httpx}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SERVER), 'exec'), scope)  # noqa: S102 - only locally versioned AST functions
    with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)),
                      follow_redirects=default) as client:
        kwargs = {} if explicit == 'default' else {'follow_redirects': explicit}
        before = kwargs.copy()
        assert scope['effective_redirects'](client, kwargs) is expected
        assert kwargs == before


@pytest.mark.parametrize('client_default,explicit,allowed', [
    (False,'default',True),(True,'default',False),(False,False,True),
    (True,False,True),(False,True,False),(True,True,False)])
def test_actual_sync_guard(monkeypatch,client_default,explicit,allowed):
    tree=ast.parse(SERVER.read_text())
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)
               and n.name in {'send_checked_sync','effective_redirects'}]
    permit=contextvars.ContextVar('sync_test',default=None)
    permit.set({'body':BODY})
    scope={'httpx':httpx,'json':json,'permit':permit,'real_sync_send':httpx.Client.send}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(SERVER),'exec'),scope)  # noqa: S102
    monkeypatch.setattr(httpx.Client,'send',scope['send_checked_sync'])
    calls=[]
    def provider(r):
        calls.append(r)
        return httpx.Response(200)
    with httpx.Client(transport=httpx.MockTransport(provider),follow_redirects=client_default) as client:
        kwargs={} if explicit=='default' else {'follow_redirects':explicit}
        if allowed:
            assert client.post(URL,json=BODY,**kwargs).status_code==200
            assert len(calls)==1
        else:
            with pytest.raises(AssertionError,match='Redirect forbidden'):
                client.post(URL,json=BODY,**kwargs)
            assert not calls
