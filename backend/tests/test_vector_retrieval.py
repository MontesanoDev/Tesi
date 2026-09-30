"""Real persistent Qdrant, controlled embeddings; no external services required."""

import json
from contextlib import closing
from dataclasses import replace

import httpx
import pytest
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda
from ollama import Client, ListResponse, ResponseError
from qdrant_client import QdrantClient

from app import retrieval
from app import vector_retrieval as vector
from app.ai_profiles import ProfileError
from app.db import connection, get_db_path, init_database
from app.main import app
from app.retrieval_embeddings import SourceEmbeddings
from app.retrieval_settings import (
    RetrievalError,
    RetrievalInput,
    public_settings,
    resolve_settings,
    save_settings,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def database(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "retrieval.db"))
    init_database()
    with connection() as db:
        for project in ("alpha", "beta"):
            db.execute(
                "INSERT INTO projects(id,title,description,status,status_tone,updated_label,"
                "instructions) VALUES (?,?, '', '', '', '', '')",
                (project, project),
            )


def source(project="alpha", text="Scadenza 30 giugno", kind="source") -> int:
    with connection() as db:
        file_id = db.execute(
            "INSERT INTO project_files(project_id,name,metadata,kind,status) "
            "VALUES (?, 'bando.txt', '', ?, '')",
            (project, kind),
        ).lastrowid
        return db.execute(
            "INSERT INTO document_chunks(project_id,file_id,chunk_index,content,char_count) "
            "VALUES (?,?,0,?,?)",
            (project, file_id, text, len(text)),
        ).lastrowid


def shared(text="PEC aziendale: mapi@example.test") -> int:
    with connection() as db:
        file_id = db.execute(
            "INSERT INTO global_documents(name,category,metadata,status,storage_path,mime_type) "
            "VALUES ('azienda.txt','company','','','company.txt','text/plain')"
        ).lastrowid
        return -db.execute(
            "INSERT INTO global_document_chunks(document_id,chunk_index,content,char_count) "
            "VALUES (?,0,?,?)",
            (file_id, text, len(text)),
        ).lastrowid


@pytest.fixture
def embeddings(database, monkeypatch):
    state = {"digest": "model-v1", "inputs": [], "fail": False}

    def fake_list(self):
        if state["fail"]:
            raise RetrievalError("Embedding non disponibile")
        return ListResponse(models=[{"model": "embeddinggemma", "digest": state["digest"]}])

    def fake_embed(self, *, model, input, truncate):
        assert model == "embeddinggemma" and truncate is False
        state["inputs"].extend(input)
        return {
            "embeddings": [
                [
                    1.0
                    if any(t in text.lower() for t in ("scadenza", "entro", "termine"))
                    else 0.0,
                    1.0 if any(t in text.lower() for t in ("pec", "posta")) else 0.0,
                    0.1,
                ]
                for text in input
            ]
        }

    monkeypatch.setattr(Client, "list", fake_list)
    monkeypatch.setattr(Client, "embed", fake_embed)
    save_settings(RetrievalInput(backend="qdrant"))
    return state


def test_vector_search_filters_before_top_k_and_excludes_templates_and_drafts(embeddings):
    own = source(text="Termine per la candidatura: 30 giugno")
    other = source("beta", "Scadenza 30 giugno")
    template = source(text="Scadenza 30 giugno", kind="template")
    draft = source(text="Scadenza 30 giugno", kind="output_draft")
    company = shared()
    found = retrieval.search_project_evidence("alpha", "Scadenza", limit=1)
    assert [c["chunk_id"] for c in found] == [own]
    assert found[0]["content"] == "Termine per la candidatura: 30 giugno"
    assert (
        retrieval.search_project_evidence("alpha", "posta certificata", 1)[0]["chunk_id"] == company
    )
    assert {c["chunk_id"] for c in vector.corpus()} == {own, other, company}
    assert not {template, draft} & {c["chunk_id"] for c in vector.corpus()}


def test_index_reuses_vectors_and_reconciles_updates_and_deletions(embeddings):
    chunk = source()
    settings = resolve_settings()
    first = vector.run_vector_search(settings)
    assert first["updated_chunks"] == first["indexed_chunks"] == 1
    again = vector.run_vector_search(settings)
    assert again["updated_chunks"] == 0 and again["collection"] == first["collection"]
    with connection() as db:
        db.execute(
            "UPDATE document_chunks SET content='PEC nuova@example.test' WHERE id=?", (chunk,)
        )
    updated = vector.run_vector_search(settings)
    assert updated["updated_chunks"] == 1
    assert (
        retrieval.search_project_evidence("alpha", "PEC")[0]["content"] == "PEC nuova@example.test"
    )
    with connection() as db:
        db.execute("DELETE FROM project_files WHERE project_id='alpha'")
    deleted = vector.run_vector_search(settings)
    assert deleted["deleted_chunks"] == 1 and deleted["indexed_chunks"] == 0
    with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as client:
        assert client.count(first["collection"]).count == 0


def test_model_digest_and_prefix_changes_create_separate_indexes(embeddings):
    source()
    settings = resolve_settings()
    original = vector.run_vector_search(settings)
    embeddings["digest"] = "model-v2"
    updated = vector.run_vector_search(settings)
    assert updated["updated_chunks"] == 1
    assert updated["collection"] != original["collection"]
    prefixed = vector.run_vector_search(replace(settings, query_prefix="query:"))
    assert prefixed["collection"] != updated["collection"]


def test_failed_embeddings_never_fall_back_to_fts_or_query_partial_index(embeddings, monkeypatch):
    source()
    embeddings["fail"] = True
    monkeypatch.setattr(retrieval, "search_lexical_evidence", lambda *a: pytest.fail("No fallback"))
    with pytest.raises(RetrievalError, match="Embedding non disponibile"):
        retrieval.search_project_evidence("alpha", "scadenza")


def test_missing_project_and_lexical_mode_do_not_require_embeddings(database, monkeypatch):
    source()
    monkeypatch.setattr(SourceEmbeddings, "digest", lambda *a: pytest.fail("No embedding"))
    assert retrieval.search_project_evidence("missing", "scadenza") is None
    assert (
        retrieval.search_project_evidence("alpha", "scadenza")[0]["content"] == "Scadenza 30 giugno"
    )


def test_source_changed_during_vector_query_is_not_returned(embeddings, monkeypatch):
    chunk = source()
    original = QdrantClient.query_points

    def query(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        with connection() as db:
            db.execute("UPDATE document_chunks SET content='Modificato' WHERE id=?", (chunk,))
        return result

    monkeypatch.setattr(QdrantClient, "query_points", query)
    assert retrieval.search_project_evidence("alpha", "Scadenza") == []


def test_partial_indexing_failure_can_resume_without_reembedding_completed_chunks(
    embeddings, monkeypatch
):
    source(text="Scadenza giugno")
    source(text="PEC mapi@example.test")
    monkeypatch.setattr(vector, "EMBED_BATCH_SIZE", 1)
    original = SourceEmbeddings._embed
    failed = False

    def fail_second(self, texts):
        nonlocal failed
        if texts == ["PEC mapi@example.test"] and not failed:
            failed = True
            raise RetrievalError("Interrotto")
        return original(self, texts)

    monkeypatch.setattr(SourceEmbeddings, "_embed", fail_second)
    with pytest.raises(RetrievalError, match="Interrotto"):
        vector.run_vector_search(resolve_settings())
    result = vector.run_vector_search(resolve_settings())
    assert result["indexed_chunks"] == 2 and result["updated_chunks"] == 1


@pytest.mark.parametrize("vectors", [[], [[0, 0]], [[float("nan")]], [[True]], [[1], [1, 2]], None])
def test_embedding_contract_rejects_bad_vectors(database, monkeypatch, vectors):
    monkeypatch.setattr(Client, "embed", lambda *a, **kw: {"embeddings": vectors})
    with vector.source_embeddings(resolve_settings()) as embedder, pytest.raises(RetrievalError):
        embedder.embed_query("query")


def test_settings_encrypt_keys_and_require_new_credentials_for_new_endpoints(database):
    payload = RetrievalInput(qdrant_api_key="q-secret", embedding_api_key="e-secret")
    public = save_settings(payload)
    assert public["has_qdrant_api_key"] and public["has_embedding_api_key"]
    assert "secret" not in json.dumps(public)
    assert "secret" not in repr(resolve_settings())
    with connection() as db:
        raw = db.execute(
            "SELECT value FROM app_metadata WHERE key='retrieval_settings_v1'"
        ).fetchone()[0]
    assert "q-secret" not in raw and "e-secret" not in raw
    assert resolve_settings().qdrant_api_key == "q-secret"
    with pytest.raises(ProfileError, match="reinserisci"):
        resolve_settings(RetrievalInput(qdrant_url="https://other.example"))
    save_settings(RetrievalInput(clear_qdrant_api_key=True))
    assert not public_settings()["has_qdrant_api_key"]
    assert resolve_settings().embedding_api_key == "e-secret"


def test_lost_cipher_key_is_not_replaced_when_only_retrieval_has_secrets(database):
    save_settings(RetrievalInput(qdrant_api_key="q-secret"))
    path = get_db_path().with_suffix(".ai-key")
    path.rename(path.with_suffix(".saved"))
    with pytest.raises(ProfileError, match="Ripristina"):
        save_settings(RetrievalInput(qdrant_api_key="new-secret"))
    assert not path.exists()


def test_remote_embedding_protocol_uses_configured_endpoint_and_no_truncation(
    database, monkeypatch
):
    settings = resolve_settings(
        RetrievalInput(
            embedding_url="https://embedding.example/ollama",
            embedding_api_key="fake-key",
        )
    )
    original = httpx.Client

    def handler(request):
        assert request.url.host == "embedding.example"
        assert request.headers["authorization"] == "Bearer fake-key"
        if request.url.path.endswith("/tags"):
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "embeddinggemma:latest",
                            "model": "embeddinggemma:latest",
                            "digest": "fake-digest",
                        }
                    ]
                },
            )
        assert request.url.path == "/ollama/api/embed"
        assert json.loads(request.content) == {
            "model": "embeddinggemma",
            "input": ["domanda"],
            "truncate": False,
        }
        return httpx.Response(200, json={"embeddings": [[1.0, 0.5]]})

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: original(
            transport=httpx.MockTransport(handler),
            **kw,
        ),
    )
    with vector.source_embeddings(settings) as embedder:
        assert embedder.digest() == "fake-digest"
        assert embedder.embed_query("domanda") == [1.0, 0.5]


def test_qdrant_remote_connection_receives_only_its_own_key(database, monkeypatch):
    seen = []

    def client(**kwargs):
        seen.append(kwargs)
        return QdrantClient(":memory:")

    monkeypatch.setattr(vector, "QdrantClient", client)
    settings = resolve_settings(
        RetrievalInput(
            qdrant_mode="remote",
            qdrant_url="https://vectors.example",
            qdrant_api_key="q-key",
            embedding_api_key="e-key",
        )
    )
    with vector.vector_client(settings) as connected:
        assert connected.get_collections().collections == []
    assert seen == [{"url": "https://vectors.example", "api_key": "q-key", "timeout": 30}]


def test_model_replacement_during_indexing_discards_mixed_vectors(embeddings, monkeypatch):
    source()
    original = SourceEmbeddings._embed

    def change_model(self, texts):
        result = original(self, texts)
        embeddings["digest"] = "model-v2"
        return result

    monkeypatch.setattr(SourceEmbeddings, "_embed", change_model)
    with pytest.raises(RetrievalError, match="aggiornato"):
        vector.run_vector_search(resolve_settings())
    with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as client:
        assert client.get_collections().collections == []


def test_empty_corpus_query_removes_last_deleted_document(embeddings):
    source()
    status = vector.run_vector_search(resolve_settings())
    with connection() as db:
        db.execute("DELETE FROM projects WHERE id='alpha'")
    assert retrieval.search_project_evidence("beta", "Scadenza") == []
    with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as client:
        assert client.count(status["collection"]).count == 0


@pytest.mark.anyio
async def test_retrieval_api_selects_backend_and_surfaces_failure(embeddings):
    source()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        config = await client.get("/api/settings/retrieval")
        assert config.json()["backend"] == "qdrant"
        assert config.headers["cache-control"] == "no-store"
        found = await client.get("/api/projects/alpha/evidence", params={"q": "Scadenza"})
        assert found.status_code == 200 and found.json()["results"]
        embeddings["fail"] = True
        failed = await client.post("/api/projects/alpha/answer", json={"question": "Scadenza?"})
        assert failed.status_code == 503 and "Embedding" in failed.json()["detail"]
        saved = await client.put("/api/settings/retrieval", json={"backend": "fts5"})
        assert saved.status_code == 200
        found = await client.get("/api/projects/alpha/evidence", params={"q": "Scadenza"})
        assert found.status_code == 200 and found.json()["results"]


@pytest.mark.anyio
async def test_settings_validation_does_not_echo_keys(database):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        result = await client.put(
            "/api/settings/retrieval",
            json={
                "embedding_url": "invalid",
                "qdrant_api_key": "do-not-echo",
            },
        )
        assert result.status_code == 422 and "do-not-echo" not in result.text


@pytest.mark.anyio
@pytest.mark.parametrize("backend", ["fts5", "qdrant"])
async def test_retrievers_compose_in_langchain_with_the_same_document_contract(
    embeddings,
    backend,
):
    chunk = source()
    save_settings(RetrievalInput(backend=backend))
    retriever = retrieval.build_retriever("alpha", limit=1)
    assert isinstance(retriever, BaseRetriever)
    documents = await retriever.ainvoke("Scadenza")
    assert len(documents) == 1 and isinstance(documents[0], Document)
    assert documents[0].id == str(chunk)
    assert documents[0].page_content == "Scadenza 30 giugno"
    assert documents[0].metadata["source_name"] == "bando.txt"
    chain = retriever | RunnableLambda(lambda docs: [doc.metadata["chunk_id"] for doc in docs])
    assert chain.invoke("Scadenza") == [chunk]


def test_langchain_payload_keeps_sqlite_as_the_source_of_returned_text(embeddings):
    chunk = source()
    settings = resolve_settings()
    status = vector.run_vector_search(settings)
    with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as client:
        payload = client.retrieve(status["collection"], ids=[vector.point_id(chunk)])[0].payload
    assert payload["page_content"] == "Scadenza 30 giugno"
    assert payload["metadata"]["scope"] == "project:alpha"
    assert payload["metadata"]["chunk_id"] == chunk
    # A stored text copy must never bypass SQLite freshness checks.
    with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as client:
        client.set_payload(
            status["collection"],
            {"page_content": "Testo obsoleto"},
            points=[vector.point_id(chunk)],
        )
    assert (
        retrieval.search_project_evidence("alpha", "Scadenza")[0]["content"] == "Scadenza 30 giugno"
    )


def test_prefixes_are_applied_once_and_dimension_changes_are_rejected(embeddings, monkeypatch):
    settings = replace(resolve_settings(), query_prefix="query:", document_prefix="passage:")
    with vector.source_embeddings(settings) as embedder:
        embedder.embed_query("Scadenza")
        embedder.embed_documents(["PEC", "Termine"])
        assert embeddings["inputs"] == ["query: Scadenza", "passage: PEC", "passage: Termine"]
        monkeypatch.setattr(Client, "embed", lambda *a, **kw: {"embeddings": [[1.0]]})
        with pytest.raises(RetrievalError, match="dimensioni"):
            embedder.embed_query("Scadenza")


def test_ollama_sdk_does_not_forward_environment_credentials(database, monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "unrelated-cloud-secret")
    original = httpx.Client

    def handler(request):
        assert "authorization" not in request.headers
        assert json.loads(request.content)["truncate"] is False
        return httpx.Response(200, json={"embeddings": [[1.0, 0.5]]})

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: original(
            transport=httpx.MockTransport(handler),
            **kw,
        ),
    )
    with vector.source_embeddings(resolve_settings()) as embedder:
        assert embedder.embed_query("Domanda") == [1.0, 0.5]


def test_retriever_serialization_excludes_service_secrets(embeddings):
    save_settings(RetrievalInput(backend="qdrant", embedding_api_key="private-credential"))
    retriever = retrieval.build_retriever("alpha")
    assert "private-credential" not in repr(retriever)
    assert "private-credential" not in retriever.model_dump_json()


@pytest.mark.parametrize(
    "error",
    [
        httpx.ReadTimeout("private-credential"),
        ConnectionError("private-credential"),
        ResponseError("private-credential", status_code=401),
        ValueError("private-credential"),
    ],
)
def test_sdk_errors_remain_readable_without_exposing_credentials(database, monkeypatch, error):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(Client, "embed", fail)
    with vector.source_embeddings(resolve_settings()) as embedder:
        with pytest.raises(RetrievalError) as caught:
            embedder.embed_query("Domanda")
    assert "private-credential" not in str(caught.value)


@pytest.mark.anyio
async def test_async_embeddings_preserve_query_and_document_prefixes(embeddings):
    settings = replace(resolve_settings(), query_prefix="query:", document_prefix="passage:")
    with vector.source_embeddings(settings) as embedder:
        assert await embedder.aembed_query("Scadenza") == [1.0, 0.0, 0.1]
        assert await embedder.aembed_documents(["PEC"]) == [[0.0, 1.0, 0.1]]
    assert embeddings["inputs"] == ["query: Scadenza", "passage: PEC"]
