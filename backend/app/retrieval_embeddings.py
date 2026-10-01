"""LangChain's Ollama adapter with Mapi's no-truncation and integrity rules.

The upstream adapter does not expose Ollama's truncate option. Only that call
is specialized; transport, model serialization and clients belong to the SDK.
"""

from __future__ import annotations

import math
from contextlib import contextmanager

import httpx
from langchain_core.runnables.config import run_in_executor
from langchain_ollama import OllamaEmbeddings
from ollama import ResponseError
from pydantic import Field

from app.retrieval_settings import RetrievalError, RetrievalSettings


class _ConfiguredAuth(httpx.Auth):
    def __init__(self, key: str | None):
        self._key = key

    def auth_flow(self, request):
        # The SDK can inherit OLLAMA_API_KEY. Only the saved service key is allowed.
        request.headers.pop("authorization", None)
        if self._key:
            request.headers["authorization"] = f"Bearer {self._key}"
        yield request


@contextmanager
def embedding_errors():
    try:
        yield
    except httpx.TimeoutException:
        raise RetrievalError("Tempo di attesa scaduto per il modello di embedding") from None
    except ResponseError as exc:
        raise RetrievalError(
            f"Ollama ha rifiutato gli embedding ({exc.status_code}). "
            "Verifica modello, accesso e lunghezza dei frammenti."
        ) from None
    except RetrievalError:
        raise
    except httpx.HTTPError, ConnectionError, ValueError, TypeError, KeyError:
        raise RetrievalError(
            "Servizio di embedding non raggiungibile o risposta non valida. "
            "Controlla l'indirizzo nelle impostazioni della ricerca."
        ) from None


class SourceEmbeddings(OllamaEmbeddings):
    query_prefix: str = ""
    document_prefix: str = ""
    expected_dimension: int | None = Field(default=None, exclude=True)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        with embedding_errors():
            vectors = self._client.embed(
                model=self.model,
                input=texts,
                truncate=False,
            )["embeddings"]
            if not isinstance(vectors, list) or len(vectors) != len(texts):
                raise RetrievalError(
                    "Il modello di embedding ha restituito un numero di vettori errato"
                )
            for vector in vectors:
                if (
                    not isinstance(vector, list)
                    or not 1 <= len(vector) <= 65536
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector)
                    or not any(vector)
                ):
                    raise RetrievalError("Il modello di embedding ha restituito vettori non validi")
                if self.expected_dimension is None:
                    self.expected_dimension = len(vector)
                elif len(vector) != self.expected_dimension:
                    raise RetrievalError(
                        "Le dimensioni degli embedding sono cambiate durante l'indicizzazione"
                    )
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed([f"{self.document_prefix} {text}".strip() for text in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._embed([f"{self.query_prefix} {text}".strip()])[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await run_in_executor(None, self.embed_documents, texts)

    async def aembed_query(self, text: str) -> list[float]:
        return await run_in_executor(None, self.embed_query, text)

    def digest(self) -> str:
        with embedding_errors():
            available = self._client.list().models
            names = {self.model, f"{self.model}:latest"}
            for item in available:
                if item.model in names and item.digest:
                    return item.digest
        raise RetrievalError(
            "Modello di embedding non installato sul servizio Ollama configurato. "
            f"Scarica {self.model} su quel servizio oppure verifica l'indirizzo "
            "nelle impostazioni avanzate della ricerca."
        )


@contextmanager
def source_embeddings(settings: RetrievalSettings):
    embeddings = SourceEmbeddings(
        model=settings.embedding_model,
        base_url=settings.embedding_url,
        query_prefix=settings.query_prefix,
        document_prefix=settings.document_prefix,
        client_kwargs={
            "auth": _ConfiguredAuth(settings.embedding_api_key),
            "timeout": httpx.Timeout(180, connect=10),
            "follow_redirects": False,
        },
    )
    try:
        yield embeddings
    finally:
        # Async methods use the same sync client through LangChain's executor.
        embeddings._client.close()
