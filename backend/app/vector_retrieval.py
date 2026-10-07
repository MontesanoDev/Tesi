"""Qdrant indexes SQLite evidence; returned text is always reloaded from SQLite.

Before each vector query reconcile the small prototype corpus by content hash.
Only changed chunks need embedding. Deletions are applied before searching;
failed indexing aborts the request rather than querying a partial index or FTS5.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from contextlib import contextmanager
from uuid import NAMESPACE_URL, uuid4, uuid5

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from app.db import connection, get_db_path
from app.repository import PROJECT_EVIDENCE_FILTER, _expand_neighbor_evidence, _neighbor_excerpt
from app.retrieval_documents import evidence_document
from app.retrieval_embeddings import source_embeddings
from app.retrieval_settings import RETRIEVAL_LOCK, RetrievalError, RetrievalSettings

logger = logging.getLogger(__name__)
EMBED_BATCH_SIZE = 24


def corpus() -> list[dict]:
    with connection() as db:
        rows = db.execute(
            f"""
            SELECT c.id AS chunk_id, c.file_id, f.name AS source_name,
                   c.chunk_index, c.content, 'project:' || c.project_id AS scope,
                   CASE WHEN f.kind = 'form' THEN 'form' ELSE 'source' END AS role,
                   c.project_id, f.metadata AS document_metadata, NULL AS category
            FROM document_chunks c JOIN project_files f ON f.id=c.file_id
            WHERE f.project_id=c.project_id AND (f.kind = 'form' OR {PROJECT_EVIDENCE_FILTER})
            UNION ALL
            SELECT -c.id, -d.id, d.name, c.chunk_index, c.content, 'global',
                   'source', NULL, d.metadata, d.category
            FROM global_document_chunks c JOIN global_documents d ON d.id=c.document_id
            WHERE d.category IN ('company', 'general')
            """
        ).fetchall()
    return [dict(row) for row in rows]


def content_hash(chunk: dict) -> str:
    # A move across projects must update the filter payload even if text is unchanged.
    value = [chunk[k] for k in (
        "content", "source_name", "scope", "file_id", "chunk_index", "role",
        "project_id", "document_metadata", "category",
    )]
    return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode()).hexdigest()


def point_id(chunk_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"mapi:chunk:{chunk_id}"))


def collection_name(settings: RetrievalSettings, digest: str, dimension: int) -> str:
    with connection() as db:
        db.execute(
            "INSERT OR IGNORE INTO app_metadata(key,value) VALUES ('vector_namespace',?)",
            (uuid4().hex,),
        )
        namespace = db.execute(
            "SELECT value FROM app_metadata WHERE key='vector_namespace'"
        ).fetchone()[0]
    signature = [
        "mapi-langchain-v2",
        namespace,
        settings.embedding_url,
        settings.embedding_model,
        settings.query_prefix,
        settings.document_prefix,
        digest,
        dimension,
    ]
    return "mapi_" + hashlib.sha256(json.dumps(signature).encode()).hexdigest()[:32]


@contextmanager
def vector_client(settings: RetrievalSettings):
    client = None
    try:
        if settings.qdrant_mode == "local":
            # Separate directory per SQLite database, including isolated tests.
            path = str(get_db_path().resolve()) + ".qdrant"
            client = QdrantClient(path=path)
        else:
            client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=30,
            )
        yield client
    except RetrievalError:
        raise
    except Exception as exc:
        # SDK exceptions can contain URLs/headers: neither log nor expose their contents.
        logger.warning("Vector retrieval failed: %s", type(exc).__name__)
        raise RetrievalError(
            "Indice Qdrant non disponibile. Controlla collegamento e credenziali; "
            "in modalita locale usa un solo processo del backend."
        ) from None
    finally:
        if client is not None:
            client.close()


def synchronize(
    client: QdrantClient,
    name: str,
    settings: RetrievalSettings,
    embedder: Embeddings,
    chunks: list[dict],
    dimension: int,
) -> tuple[QdrantVectorStore, dict]:
    if not client.collection_exists(name):
        client.create_collection(
            name,
            vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
        )
    if settings.qdrant_mode == "remote":
        existing = client.get_collection(name).payload_schema
        for field, schema in (
            ("metadata.scope", models.PayloadSchemaType.KEYWORD),
            ("metadata.role", models.PayloadSchemaType.KEYWORD),
            ("metadata.file_id", models.PayloadSchemaType.INTEGER),
        ):
            if field not in existing:
                client.create_payload_index(name, field, field_schema=schema)
    # The query already established the dimension. Avoid an extra dummy embedding
    # in LangChain's constructor; vector searches still validate the collection.
    store = QdrantVectorStore(
        client=client,
        collection_name=name,
        embedding=embedder,
        validate_collection_config=False,
    )
    stored = {}
    offset = None
    while True:
        points, offset = client.scroll(
            name, limit=256, offset=offset, with_payload=True, with_vectors=False
        )
        stored.update({str(p.id): (p.payload or {}).get("metadata", {}) for p in points})
        if offset is None:
            break
    current = {point_id(c["chunk_id"]): c for c in chunks}
    deleted = sorted(set(stored) - set(current))
    if deleted:
        store.delete(ids=deleted, wait=True)
    changed = [
        (key, chunk)
        for key, chunk in current.items()
        if stored.get(key, {}).get("content_hash") != content_hash(chunk)
    ]
    documents = [
        Document(
            id=key,
            page_content=chunk["content"],
            metadata={
                "chunk_id": chunk["chunk_id"],
                "scope": chunk["scope"],
                "role": chunk["role"],
                "project_id": chunk["project_id"],
                "file_id": chunk["file_id"],
                "source_name": chunk["source_name"],
                "document_metadata": chunk["document_metadata"],
                "category": chunk["category"],
                "content_hash": content_hash(chunk),
            },
        )
        for key, chunk in changed
    ]
    if documents:
        store.add_documents(documents, batch_size=EMBED_BATCH_SIZE, wait=True)
    return store, {
        "collection": name,
        "indexed_chunks": len(chunks),
        "updated_chunks": len(changed),
        "deleted_chunks": len(deleted),
    }


def run_vector_search(
    settings: RetrievalSettings,
    project_id: str | None = None,
    query: str | None = None,
    limit: int = 4,
    include_neighbors: bool = False,
    *,
    target: str = "source",
    form_id: int | None = None,
) -> list[Document] | dict:
    if target not in {"source", "form"}:
        raise ValueError("Target del retrieval non valido")
    with RETRIEVAL_LOCK, source_embeddings(settings) as embedder:
        chunks = corpus()
        digest = embedder.digest()
        vector = embedder.embed_query(query or "Verifica della ricerca")
        name = collection_name(settings, digest, len(vector))
        with vector_client(settings) as client:
            store, status = synchronize(client, name, settings, embedder, chunks, len(vector))
            if embedder.digest() != digest:
                client.delete_collection(name)
                raise RetrievalError("Modello di embedding aggiornato durante la ricerca: riprova")
            if query is None:
                return status | {"dimensions": len(vector), "embedding_digest": digest}
            scopes = [f"project:{project_id}"]
            if target == "source":
                scopes.append("global")
            conditions = [
                models.FieldCondition(key="metadata.scope", match=models.MatchAny(any=scopes)),
                models.FieldCondition(key="metadata.role", match=models.MatchValue(value=target)),
            ]
            if form_id is not None:
                conditions.append(models.FieldCondition(
                    key="metadata.file_id", match=models.MatchValue(value=form_id),
                ))
            hits = store.similarity_search_with_score_by_vector(
                vector,
                filter=models.Filter(must=conditions),
                k=max(limit * 6, 24),
            )
        # Reload after the network calls: old/deleted/differently scoped evidence is unusable.
        fresh = {c["chunk_id"]: c for c in corpus()}
        anchors, deferred = [], []
        for document, score in hits:
            payload = document.metadata
            chunk = fresh.get(payload.get("chunk_id"))
            if (
                chunk is None
                or chunk["scope"] not in scopes
                or chunk["role"] != target
                or (form_id is not None and chunk["file_id"] != form_id)
                or payload.get("content_hash") != content_hash(chunk)
                or not math.isfinite(score)
            ):
                continue
            item = dict(chunk)
            item.update(excerpt=_neighbor_excerpt(chunk["content"], 0), relevance=score)
            adjacent = any(
                c["file_id"] == item["file_id"] and abs(c["chunk_index"] - item["chunk_index"]) <= 1
                for c in anchors
            )
            if adjacent:
                deferred.append(item)
            elif len(anchors) < limit:
                anchors.append(item)
        anchors.extend(deferred[: max(0, limit - len(anchors))])
        if include_neighbors:
            anchors = _expand_neighbor_evidence(
                project_id, anchors, max_results=limit * 2, target=target, form_id=form_id,
            )
        return [evidence_document(item) for item in anchors]


def check_connection(settings: RetrievalSettings) -> dict:
    with source_embeddings(settings) as embedder:
        digest = embedder.digest()
        vector = embedder.embed_query("Verifica del modello di embedding")
    with RETRIEVAL_LOCK, vector_client(settings) as client:
        client.get_collections()
    return {
        "dimensions": len(vector),
        "embedding_digest": digest,
        "message": "Collegamento riuscito. Modello di embedding e Qdrant disponibili.",
    }
