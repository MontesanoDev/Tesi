"""Read-only Ollama embedding inventory, isolated DB and simulated transport."""

import httpx
import pytest
from test_ai_settings import anyio_backend as anyio_backend
from test_ai_settings import client as client

from app import retrieval_routes
from app.ai_discovery import discover_models
from app.config import AISettings
from app.db import connection
from app.retrieval_settings import RetrievalInput, public_settings, save_settings

URL = "/api/settings/retrieval/models"
OLLAMA = "https://embedding.example"
KEY = "fake-embedding-key"


def mock_server(monkeypatch, handler):
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )


def no_index_or_generation(*args, **kwargs):
    raise AssertionError("Inventory must not index, check embeddings or generate")


@pytest.mark.anyio
async def test_lists_embedding_capability_only_without_writes_or_qdrant(client, monkeypatch):
    saved = save_settings(RetrievalInput(
        backend="qdrant", embedding_url=OLLAMA, embedding_api_key=KEY,
        qdrant_mode="remote", qdrant_api_key="separate-qdrant-secret",
    ))
    with connection() as db:
        before = db.execute(
            "SELECT value FROM app_metadata WHERE key='retrieval_settings_v1'",
        ).fetchone()[0]
    paths = []

    def handler(request):
        assert request.url.host == "embedding.example"
        assert request.headers.get("authorization") == f"Bearer {KEY}"
        paths.append(request.url.path)
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [
                {"name": "bge-m3:latest"}, {"name": "nomic-embed-text:latest"},
                {"name": "generic-chat"}, {"name": "ambiguous"},
            ]})
        assert request.url.path == "/api/show"
        import json
        model = json.loads(request.content)["model"]
        capabilities = {"generic-chat": ["completion"], "ambiguous": []}.get(model, ["embedding"])
        return httpx.Response(200, json={"capabilities": capabilities})

    mock_server(monkeypatch, handler)
    monkeypatch.setattr(retrieval_routes, "run_vector_search", no_index_or_generation)
    monkeypatch.setattr(retrieval_routes, "check_connection", no_index_or_generation)
    response = await client.post(URL, json={"embedding_url": OLLAMA})
    assert response.status_code == 200
    assert response.json() == {"models": ["bge-m3:latest", "nomic-embed-text:latest"]}
    assert response.headers["cache-control"] == "no-store"
    assert KEY not in response.text
    assert paths.count("/api/tags") == 1 and paths.count("/api/show") == 4
    with connection() as db:
        after = db.execute(
            "SELECT value FROM app_metadata WHERE key='retrieval_settings_v1'",
        ).fetchone()[0]
    assert after == before and public_settings() == saved


@pytest.mark.anyio
async def test_new_endpoint_requires_reentry_or_clear_of_embedding_key(client, monkeypatch):
    save_settings(RetrievalInput(embedding_url=OLLAMA, embedding_api_key=KEY))
    monkeypatch.setattr(retrieval_routes, "discover_models", no_index_or_generation)
    response = await client.post(URL, json={"embedding_url": "https://different.example"})
    assert response.status_code == 422
    assert "reinserisci o rimuovi" in response.text
    assert KEY not in response.text


@pytest.mark.anyio
@pytest.mark.parametrize("patch,authorization", [
    ({"embedding_api_key": "replacement"}, "Bearer replacement"),
    ({"clear_embedding_api_key": True}, None),
])
async def test_temporary_credentials_are_not_saved(client, monkeypatch, patch, authorization):
    saved = save_settings(RetrievalInput(embedding_url=OLLAMA, embedding_api_key=KEY))

    def handler(request):
        assert request.url.host == "different.example"
        assert request.headers.get("authorization") == authorization
        return httpx.Response(200, json={"models": []})

    mock_server(monkeypatch, handler)
    response = await client.post(URL, json={"embedding_url": "https://different.example", **patch})
    assert response.status_code == 200 and response.json() == {"models": []}
    assert public_settings() == saved


@pytest.mark.anyio
@pytest.mark.parametrize("status", [401, 403, 404, 500])
async def test_http_errors_are_safe_and_explicit(client, monkeypatch, status):
    mock_server(monkeypatch, lambda request: httpx.Response(status, text=f"secret={KEY}"))
    response = await client.post(URL, json={"embedding_url": OLLAMA, "embedding_api_key": KEY})
    assert response.status_code == 502
    assert KEY not in response.text
    assert ("non autorizzato" if status in (401, 403) else "non disponibile") in response.text


@pytest.mark.anyio
@pytest.mark.parametrize("body", [{"models": "bad"}, [], {"models": [{"name": "bad\nname"}]}])
async def test_malformed_inventory_never_offers_an_unverified_model(client, monkeypatch, body):
    mock_server(monkeypatch, lambda request: httpx.Response(200, json=body))
    response = await client.post(URL, json={"embedding_url": OLLAMA})
    assert response.status_code == 502 or response.json() == {"models": []}


@pytest.mark.anyio
async def test_offline_ollama_returns_sanitized_failure(client, monkeypatch):
    def handler(request):
        raise httpx.ConnectError(f"Authorization {KEY}", request=request)
    mock_server(monkeypatch, handler)
    response = await client.post(URL, json={"embedding_url": OLLAMA})
    assert response.status_code == 502 and KEY not in response.text


@pytest.mark.anyio
async def test_completion_inventory_still_excludes_embedding_only_models(client, monkeypatch):
    mock_server(monkeypatch, lambda request: httpx.Response(200, json={"models": [
        {"name": "chat", "capabilities": ["completion"]},
        {"name": "bge-m3", "capabilities": ["embedding"]},
        {"name": "both", "capabilities": ["embedding", "completion"]},
    ]}))
    config = AISettings(provider="ollama", api_key=None, model="chat", base_url=OLLAMA)
    assert await discover_models(config) == ["both", "chat"]
    assert await discover_models(config, ollama_capability="embedding") == ["bge-m3", "both"]


@pytest.mark.anyio
async def test_invalid_secret_validation_never_echoes_payload(client):
    response = await client.post(URL, json={"embedding_url": "not-a-url", "embedding_api_key": KEY})
    assert response.status_code == 422 and KEY not in response.text
