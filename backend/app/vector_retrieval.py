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

import httpx
from qdrant_client import QdrantClient, models

from app.db import connection, get_db_path
from app.repository import PROJECT_EVIDENCE_FILTER, _expand_neighbor_evidence, _neighbor_excerpt
from app.retrieval_settings import RETRIEVAL_LOCK, RetrievalError, RetrievalSettings

logger = logging.getLogger(__name__)
EMBED_BATCH_SIZE = 24


def corpus() -> list[dict]:
    with connection() as db:
        rows = db.execute(
            f"""
            SELECT c.id AS chunk_id, c.file_id, f.name AS source_name,
                   c.chunk_index, c.content, 'project:' || c.project_id AS scope
            FROM document_chunks c JOIN project_files f ON f.id=c.file_id
            WHERE f.project_id=c.project_id AND {PROJECT_EVIDENCE_FILTER}
            UNION ALL
            SELECT -c.id, -d.id, d.name, c.chunk_index, c.content, 'global'
            FROM global_document_chunks c JOIN global_documents d ON d.id=c.document_id
            WHERE d.category IN ('company', 'general')
            """
        ).fetchall()
    return [dict(row) for row in rows]


def content_hash(chunk: dict) -> str:
    # A move across projects must update the filter payload even if text is unchanged.
    value = [chunk[k] for k in ("content", "source_name", "scope", "file_id", "chunk_index")]
    return hashlib.sha256(json.dumps(value, ensure_ascii=False).encode()).hexdigest()


def point_id(chunk_id: int) -> str:
    return str(uuid5(NAMESPACE_URL, f"mapi:chunk:{chunk_id}"))


class OllamaEmbeddings:
    def __init__(self, settings: RetrievalSettings):
        self.settings = settings

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        headers = (
            {"Authorization": f"Bearer {self.settings.embedding_api_key}"}
            if self.settings.embedding_api_key
            else {}
        )
        try:
            with httpx.Client(timeout=httpx.Timeout(180, connect=10), headers=headers) as client:
                response = client.request(method, f"{self.settings.embedding_url}{path}", json=body)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError
                return payload
        except httpx.TimeoutException:
            raise RetrievalError("Tempo di attesa scaduto per il modello di embedding") from None
        except httpx.HTTPStatusError as exc:
            raise RetrievalError(
                f"Ollama ha rifiutato gli embedding ({exc.response.status_code}). "
                "Verifica modello, accesso e lunghezza dei frammenti."
            ) from None
        except httpx.HTTPError, ValueError:
            raise RetrievalError(
                "Servizio di embedding non raggiungibile o risposta non valida. "
                "Controlla l'indirizzo nelle impostazioni della ricerca."
            ) from None

    def digest(self) -> str:
        payload = self._request("GET", "/api/tags")
        requested = self.settings.embedding_model
        names = {requested, f"{requested}:latest"}
        available = payload.get("models")
        if not isinstance(available, list):
            raise RetrievalError("Elenco modelli del servizio di embedding non valido")
        for item in available:
            if isinstance(item, dict) and item.get("name") in names and item.get("digest"):
                return str(item["digest"])
        raise RetrievalError(
            "Modello di embedding non installato sul servizio Ollama configurato. "
            f"Scarica {requested} su quel servizio oppure scegli un modello installato."
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        payload = self._request(
            "POST",
            "/api/embed",
            {
                "model": self.settings.embedding_model,
                "input": texts,
                "truncate": False,
            },
        )
        vectors = payload.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise RetrievalError(
                "Il modello di embedding ha restituito un numero di vettori errato"
            )
        dimension = None
        for vector in vectors:
            if (
                not isinstance(vector, list)
                or not 1 <= len(vector) <= 65536
                or (dimension is not None and len(vector) != dimension)
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector)
                or not any(vector)
            ):
                raise RetrievalError("Il modello di embedding ha restituito vettori non validi")
            dimension = len(vector)
        return vectors


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
        "mapi-v1",
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
    embedder: OllamaEmbeddings,
    chunks: list[dict],
    dimension: int,
) -> dict:
    if not client.collection_exists(name):
        client.create_collection(
            name,
            vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
        )
        if settings.qdrant_mode == "remote":
            client.create_payload_index(
                name, "scope", field_schema=models.PayloadSchemaType.KEYWORD
            )
    stored = {}
    offset = None
    while True:
        points, offset = client.scroll(
            name, limit=256, offset=offset, with_payload=True, with_vectors=False
        )
        stored.update({str(p.id): p.payload or {} for p in points})
        if offset is None:
            break
    current = {point_id(c["chunk_id"]): c for c in chunks}
    deleted = sorted(set(stored) - set(current))
    if deleted:
        client.delete(name, points_selector=models.PointIdsList(points=deleted), wait=True)
    changed = [
        (key, chunk)
        for key, chunk in current.items()
        if stored.get(key, {}).get("content_hash") != content_hash(chunk)
    ]
    for start in range(0, len(changed), EMBED_BATCH_SIZE):
        batch = changed[start : start + EMBED_BATCH_SIZE]
        prefix = settings.document_prefix
        texts = [f"{prefix} {chunk['content']}".strip() for _, chunk in batch]
        vectors = embedder.embed(texts)
        if any(len(vector) != dimension for vector in vectors):
            raise RetrievalError(
                "Le dimensioni degli embedding sono cambiate durante l'indicizzazione"
            )
        client.upsert(
            name,
            points=[
                models.PointStruct(
                    id=key,
                    vector=vector,
                    payload={
                        "chunk_id": chunk["chunk_id"],
                        "scope": chunk["scope"],
                        "content_hash": content_hash(chunk),
                    },
                )
                for (key, chunk), vector in zip(batch, vectors, strict=True)
            ],
            wait=True,
        )
    # Never publish/query a mixture if an Ollama tag was replaced during indexing.
    return {
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
) -> list[dict] | dict:
    with RETRIEVAL_LOCK:
        chunks = corpus()
        embedder = OllamaEmbeddings(settings)
        digest = embedder.digest()
        text = f"{settings.query_prefix} {query or 'Verifica della ricerca'}".strip()
        vector = embedder.embed([text])[0]
        name = collection_name(settings, digest, len(vector))
        with vector_client(settings) as client:
            status = synchronize(client, name, settings, embedder, chunks, len(vector))
            if embedder.digest() != digest:
                client.delete_collection(name)
                raise RetrievalError("Modello di embedding aggiornato durante la ricerca: riprova")
            if query is None:
                return status | {"dimensions": len(vector), "embedding_digest": digest}
            hits = client.query_points(
                name,
                query=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="scope",
                            match=models.MatchAny(any=[f"project:{project_id}", "global"]),
                        )
                    ]
                ),
                limit=max(limit * 6, 24),
                with_payload=True,
                with_vectors=False,
            ).points
        # Reload after the network calls: old/deleted/differently scoped evidence is unusable.
        fresh = {c["chunk_id"]: c for c in corpus()}
        anchors, deferred = [], []
        for hit in hits:
            payload = hit.payload or {}
            chunk = fresh.get(payload.get("chunk_id"))
            if (
                chunk is None
                or chunk["scope"] not in {f"project:{project_id}", "global"}
                or payload.get("content_hash") != content_hash(chunk)
                or not math.isfinite(hit.score)
            ):
                continue
            item = {k: v for k, v in chunk.items() if k != "scope"}
            item.update(excerpt=_neighbor_excerpt(chunk["content"], 0), relevance=hit.score)
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
            return _expand_neighbor_evidence(project_id, anchors, max_results=limit * 2)
        return anchors


def check_connection(settings: RetrievalSettings) -> dict:
    embedder = OllamaEmbeddings(settings)
    digest = embedder.digest()
    vector = embedder.embed(["Verifica del modello di embedding"])[0]
    with RETRIEVAL_LOCK, vector_client(settings) as client:
        client.get_collections()
    return {
        "dimensions": len(vector),
        "embedding_digest": digest,
        "message": "Collegamento riuscito. Modello di embedding e Qdrant disponibili.",
    }
