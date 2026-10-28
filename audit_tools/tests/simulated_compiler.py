"""The unchanged candidate compiler behind FastAPI; only the remote provider is simulated.

The application's own post_chat, HTTPX clients, semaphore, retries, cache and timeouts run.
The remote transport is a scripted DeepSeek stand-in at AsyncHTTPTransport and any
non-loopback connection fails. Zero LLM calls; the narrator is stubbed as in the backend tests.
"""
import asyncio
import contextlib
import json
import os
import socket
import sys
from pathlib import Path

import httpx
import pytest

BACKEND = Path(__file__).parents[2] / 'backend'
os.environ['PYTHON_DOTENV_DISABLED'] = '1'
for folder in (BACKEND / 'tests', BACKEND):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import test_compilation_resilient_segments as rev2
from app import ai_profiles, ai_transport, compilation_chat, generation
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.config import AISettings
from app.db import connection, get_storage_path, init_database
from app.main import app
from app.repository import create_project
from app.retrieval_settings import RetrievalInput, save_settings
from app.schemas import ProjectCreate
from ollama import Client, ListResponse
from test_compilation_sessions import source

from audit_tools.narrator_harness import budget, metrics

assert Path(adapter.__file__).resolve().is_relative_to(BACKEND)
ORIGINAL = adapter._resilient_proposal, adapter.global_request  # Re-instrumenting never nests.
SETTINGS = AISettings(api_key='synthetic-test-key', model='deepseek-flash',
                      base_url='https://api.deepseek.com', provider='deepseek')
BASE = '/api/projects/alpha/compilation-sessions'
USAGE = {'prompt_tokens':100,'completion_tokens':10,'total_tokens':110,
         'prompt_cache_hit_tokens':40,'prompt_cache_miss_tokens':60,
         'completion_tokens_details':{'reasoning_tokens':4}}
RATES = {'cache_hit':.006,'cache_miss':.3,'output':1.2}


class Provider:
    """Per segment index: a delay and an outcome ('ok', an exception, or an awaitable hook)."""

    def __init__(self):
        self.delay, self.plan, self.usage, self.wires = {}, {}, {}, []
        self.flight = self.peak = 0
        self.default_delay = .3

    async def handle_async_request(self, request):
        assert (request.url.host, request.url.path) == ('api.deepseek.com', '/chat/completions')
        body = json.loads(request.content)
        index, ids = rev2.segment_of(body)
        self.wires.append((index, request.content))
        self.flight += 1
        self.peak = max(self.peak, self.flight)
        try:
            await asyncio.sleep(self.delay.get(index, self.default_delay))
            outcome = self.plan.get(index, 'ok')
            if isinstance(outcome, BaseException):
                raise outcome
            if callable(outcome):
                await outcome()
        finally:
            self.flight -= 1
        raw = rev2.ordinary(json.loads(body['messages'][1]['content']), ids)
        usage = self.usage.get(index, USAGE)  # None: a valid answer without usage.
        return httpx.Response(200, json={'model':'deepseek-flash','choices':[
            {'message':{'role':'assistant','content':raw},'finish_reason':'stop'}],
            **({'usage':usage} if usage is not None else {})})


async def summarize(client, settings, body, timeout, **kwargs):
    """Narrator stand-in of the backend tests: the narrator is out of scope here."""
    data = json.loads(body['messages'][1]['content'])
    return json.dumps({**({'message': 'Ho trovato dati nelle fonti.'}
                          if data['conversation_stage'] == 'initial' else {}),
                       'questions': [{'slot': q['slot'], **(
                           {'confirmation': 'questa situazione si applica'}
                           if q['kind'] == 'applicability' else
                           {'question': 'Quale dato vuoi indicare?'})}
                           for q in data['question_pool'][:3]]}), 'simulated', {}


@pytest.fixture
def world(tmp_path, monkeypatch):
    for key in [k for k in os.environ if k.startswith('MAPI_')]:
        monkeypatch.delenv(key)
    monkeypatch.setenv('MAPI_COMPILATION_PROFILE', 'sezioni-2026-10-25')
    monkeypatch.setenv('MAPI_DB_PATH', str(tmp_path / 'sessions.db'))
    monkeypatch.setenv('MAPI_STORAGE_PATH', str(tmp_path / 'uploads'))
    monkeypatch.setenv('MAPI_KNOWLEDGE_PATH', str(tmp_path / 'knowledge'))
    init_database()
    create_project(ProjectCreate(title='Alpha', description='Audit harness'))
    monkeypatch.setattr(Client, 'list', lambda *a: ListResponse(
        models=[{'model': 'bge-m3', 'digest': 'audit-harness'}]))
    monkeypatch.setattr(Client, 'embed', lambda *a, **kw: {
        'embeddings': [[1.0, .5, .1] for _ in kw['input']]})
    save_settings(RetrievalInput(backend='fts5'))
    monkeypatch.setattr(compilation_chat, 'CHAT_ENGINE', 'global')
    monkeypatch.setattr(adapter, 'get_ai_settings', lambda: SETTINGS)
    monkeypatch.setattr(ai_profiles, 'resolve_project_settings', lambda project: SETTINGS)
    monkeypatch.setattr(dialogue, 'get_ai_settings', lambda: SETTINGS)
    monkeypatch.setattr(dialogue, 'request_model_content', summarize)
    monkeypatch.setattr(adapter, 'TIMEOUT_SECONDS', 1.0)  # Scaled model timeout (300 s real).
    provider = Provider()
    monkeypatch.setattr(httpx.AsyncHTTPTransport, 'handle_async_request',
                        provider.handle_async_request)
    real_connect = socket.socket.connect

    def loopback_only(sock, address):
        assert not isinstance(address, tuple) or address[0] in {'127.0.0.1', '::1', 'localhost'}
        return real_connect(sock, address)

    monkeypatch.setattr(socket.socket, 'connect', loopback_only)
    return provider


def instrument(monkeypatch, root, *, limit=budget.LIMIT, reserve_tokens=0, admission=True,
               wait_check=None, on_refusal=None):
    """The campaign wiring of server.py, without its FREEZE/gate files: post_chat observed,
    (admission) segment tickets taken when each client opens, and (on_refusal) refusals
    turned into the controlled error. Without them: the behaviour of the 02 harness."""
    metrics.install_transport_observer()
    wait_check = wait_check or (lambda: None)
    extra = {'on_refusal': on_refusal} if on_refusal else {}

    async def observed(client, settings, body, **kwargs):
        return await metrics.observe(ai_transport.post_chat, client, settings, body, root,
                                     limit=limit, reserve_tokens=reserve_tokens, rates=RATES,
                                     wait_check=wait_check, **extra, **kwargs)

    monkeypatch.setattr(generation, 'post_chat', observed)
    if admission:
        metrics.install_admission_hook()
        planned, built = metrics.plan_segments(
            *ORIGINAL, ledger=root / 'budget-ledger.json', limit=limit,
            reserve_tokens=reserve_tokens, wait_check=wait_check, **extra)
        monkeypatch.setattr(adapter, '_resilient_proposal', planned)
        monkeypatch.setattr(adapter, 'global_request', built)
    return root / 'budget-ledger.json'


@contextlib.asynccontextmanager
async def application():
    # Unhandled application errors become HTTP 500, as under uvicorn.
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                                 base_url='http://test') as client:
        upload = await client.post('/api/projects/alpha/forms',
                                   files={'file': ('modulo.docx', rev2.form_docx(300))})
        assert upload.status_code == 201, upload.text
        await source(client, 'Codice: ABC123', name='dati.md')
        yield client, upload.json()['id']


async def session(client, form_id):
    response = await client.post(BASE, json={'form_id': form_id, 'engine': 'global',
                                             'start_in_chat': True})
    assert response.status_code == 201, response.text
    return response.json()


async def resolve(client, current):
    return await client.post(f'{BASE}/{current["id"]}/resolve',
                             json={'version': current['version'], 'automatic': True})


def state(current):
    with connection() as db:
        return json.loads(db.execute('SELECT state_json FROM compilation_sessions WHERE id=?',
                                     (current['id'],)).fetchone()[0])


def folder(current):
    return get_storage_path().resolve() / 'alpha' / '_global_compilations' / current['id']


def cache(current):
    return {json.loads(p.read_text())['segment']: json.loads(p.read_text())['raw']
            for p in (folder(current) / 'segment-cache').glob('*.json')}


def report(current):
    """Segment report of the latest analysis of the session."""
    root = get_storage_path().resolve() / state(current)['global_compilation']['artifact_path']
    return json.loads((root / 'segments' / 'report.json').read_text())


def segment_bound(provider):
    """Largest reservation among the segment requests seen by the provider."""
    return max(budget.bound(json.loads(content)) for _, content in provider.wires)


def records(root):
    return [json.loads(p.read_text()) for p in (root / 'provider-calls').glob('*/metrics.json')]


async def settled(ledger, seconds=5):
    """Orphaned segments keep running after a failed analysis: wait for their settlement."""
    for _ in range(int(seconds / .05)):
        if not budget.totals(ledger)['reserved_live']:
            return
        await asyncio.sleep(.05)
    raise AssertionError('Live reservations did not settle')
