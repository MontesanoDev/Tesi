"""Embedding providers: isolated configuration, strict vectors and real local indexes."""

import json
from dataclasses import replace

import httpx
import pytest
from test_ai_settings import anyio_backend as anyio_backend
from test_ai_settings import client as client
from test_vector_retrieval import database as database
from test_vector_retrieval import source

from app import vector_retrieval as vector
from app.ai_profiles import ProfileError
from app.db import connection
from app.retrieval_embeddings import source_embeddings
from app.retrieval_settings import (
    RetrievalError,
    RetrievalInput,
    public_settings,
    resolve_settings,
    save_settings,
)


def config(provider="openai", **kwargs):
    return resolve_settings(RetrievalInput(
        embedding_provider=provider, embedding_url="https://embed.example/v1",
        embedding_model="embed-test", embedding_api_key="only-embedding-key", **kwargs,
    ))


def mock_sync(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(
        transport=httpx.MockTransport(handler), **kw,
    ))


def reply(vectors):
    return {"data": [{"index": i, "embedding": v} for i, v in enumerate(vectors)]}


def test_old_settings_remain_ollama_without_a_database_write(database):
    save_settings(RetrievalInput())
    with connection() as db:
        raw = json.loads(db.execute(
            "SELECT value FROM app_metadata WHERE key='retrieval_settings_v1'",
        ).fetchone()[0])
        raw.pop("embedding_provider")
        old = json.dumps(raw)
        db.execute("UPDATE app_metadata SET value=? WHERE key='retrieval_settings_v1'", (old,))
    assert public_settings()["embedding_provider"] == "ollama"
    assert resolve_settings().embedding_provider == "ollama"
    with connection() as db:
        assert db.execute(
            "SELECT value FROM app_metadata WHERE key='retrieval_settings_v1'",
        ).fetchone()[0] == old


@pytest.mark.parametrize("provider", ["openai", "mistral", "compatible"])
def test_provider_change_cannot_reuse_old_secret_even_at_same_address(database, provider):
    saved = save_settings(RetrievalInput(embedding_api_key="old-ollama-key"))
    with pytest.raises(ProfileError, match="reinserisci"):
        resolve_settings(RetrievalInput(embedding_provider=provider))
    assert public_settings() == saved


@pytest.mark.parametrize("provider", ["openai", "mistral"])
def test_cloud_provider_requires_its_own_key(database, provider):
    with pytest.raises(ProfileError, match="chiave API"):
        resolve_settings(RetrievalInput(embedding_provider=provider))


@pytest.mark.parametrize("provider", ["openai", "mistral", "compatible"])
def test_embedding_protocol_orders_vectors_and_uses_separate_auth(database, monkeypatch, provider):
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-environment-key")
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url == "https://embed.example/v1/embeddings"
        assert request.headers["authorization"] == "Bearer only-embedding-key"
        data = json.loads(request.content)
        assert data == {"model": "embed-test", "input": ["passage: uno", "passage: due"],
                        "encoding_format": "float"}
        return httpx.Response(200, json={"data": [
            {"index": 1, "embedding": [0.5, 1.0]}, {"index": 0, "embedding": [1.0, 0.5]},
        ]})

    mock_sync(monkeypatch, handler)
    with source_embeddings(config(provider, document_prefix="passage:")) as embedder:
        assert embedder.embed_documents([]) == []
        assert embedder.embed_documents(["uno", "due"]) == [[1.0, 0.5], [0.5, 1.0]]
    assert len(seen) == 1


@pytest.mark.parametrize("body", [
    {"data": []}, {"data": "bad"}, {}, {"data": [{"index": 1, "embedding": [1.0]}]},
    {"data": [{"index": True, "embedding": [1.0]}]},
    {"data": [{"index": 0, "embedding": []}]},
    {"data": [{"index": 0, "embedding": [0.0]}]},
    {"data": [{"index": 0, "embedding": [True]}]},
    {"data": [{"index": 0, "embedding": ["1.0"]}]},
])
def test_invalid_vectors_are_rejected(database, monkeypatch, body):
    mock_sync(monkeypatch, lambda request: httpx.Response(200, json=body))
    with source_embeddings(config()) as embedder, pytest.raises(RetrievalError):
        embedder.embed_query("query")


def test_duplicate_indices_and_changing_dimensions_are_rejected(database, monkeypatch):
    bodies = iter([
        {"data": [{"index": 0, "embedding": [1.0]}, {"index": 0, "embedding": [1.0]}]},
        reply([[1.0, 0.5]]), reply([[1.0]]),
    ])
    mock_sync(monkeypatch, lambda request: httpx.Response(200, json=next(bodies)))
    with source_embeddings(config()) as embedder:
        with pytest.raises(RetrievalError, match="Ordine"):
            embedder.embed_documents(["a", "b"])
    with source_embeddings(config()) as embedder:
        assert embedder.embed_query("a") == [1.0, 0.5]
        with pytest.raises(RetrievalError, match="dimensioni"):
            embedder.embed_query("b")


@pytest.mark.parametrize("status", [302, 401, 403, 429, 500])
def test_http_errors_are_sanitized_and_never_retried(database, monkeypatch, status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, headers={"Location": "https://different.example"},
                              text="only-embedding-key")

    mock_sync(monkeypatch, handler)
    with source_embeddings(config()) as embedder, pytest.raises(RetrievalError) as error:
        embedder.embed_query("a")
    assert "only-embedding-key" not in str(error.value)
    assert len(calls) == 1


def test_provider_identity_separates_indexes_and_query_prefix_is_applied_once(
    database, monkeypatch,
):
    seen = []

    def handler(request):
        values = json.loads(request.content)["input"]
        seen.extend(values)
        return httpx.Response(200, json=reply([[1.0, 0.5] for _ in values]))

    mock_sync(monkeypatch, handler)
    source(text="informazione da conservare")
    settings = config(backend="qdrant", query_prefix="query:")
    first = vector.run_vector_search(settings)
    second = vector.run_vector_search(replace(settings, embedding_provider="compatible"))
    assert first["collection"] != second["collection"]
    assert first["indexed_chunks"] == second["indexed_chunks"] == 1
    with source_embeddings(settings) as embedder:
        assert embedder.embed_query("domanda") == [1.0, 0.5]
    assert seen[-1] == "query: domanda"


@pytest.mark.anyio
@pytest.mark.parametrize("provider,entries,expected", [
    ("openai", [{"id": "text-embedding-3-small"}, {"id": "chat-model"}],
     ["text-embedding-3-small"]),
    ("mistral", [{"id": "embed", "capabilities": {"embeddings": True}},
                 {"id": "chat", "capabilities": {"embeddings": False}}], ["embed"]),
    ("mistral", [{"id": "mistral-embed"}, {"id": "codestral-embed-2505"},
                 {"id": "mistral-small-latest"}], ["codestral-embed-2505", "mistral-embed"]),
    ("mistral", [{"id": "mistral-embed", "capabilities": {"embeddings": False}}], []),
    ("compatible", [{"id": "unspecified-model"}], []),
    ("compatible", [{"id": "embed", "capabilities": ["embedding"]}], ["embed"]),
])
async def test_provider_inventory_keeps_embedding_and_chat_models_separate(
    client, monkeypatch, provider, entries, expected,
):
    original = httpx.AsyncClient
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url == "https://embed.example/v1/models"
        assert request.headers["authorization"] == "Bearer only-embedding-key"
        return httpx.Response(200, json={"data": entries})

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(
        transport=httpx.MockTransport(handler), **kw,
    ))
    response = await client.post("/api/settings/retrieval/models", json={
        "embedding_provider": provider, "embedding_url": "https://embed.example/v1",
        "embedding_api_key": "only-embedding-key",
    })
    assert response.status_code == 200 and response.json() == {"models": expected}
    assert len(seen) == 1


@pytest.mark.anyio
async def test_provider_catalog_has_only_supported_embedding_protocols(client):
    response = await client.get("/api/settings/retrieval/providers")
    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == ["ollama", "openai", "mistral", "compatible"]
