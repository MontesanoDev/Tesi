"""Strict LangChain adapter for the OpenAI-compatible /embeddings protocol."""

import hashlib
import json
import math

import httpx
from langchain_core.embeddings import Embeddings

from app.retrieval_settings import RetrievalError, RetrievalSettings


class APIEmbeddings(Embeddings):
    def __init__(self, settings: RetrievalSettings):
        self.settings = settings
        self.expected_dimension: int | None = None
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {settings.embedding_api_key}"}
            if settings.embedding_api_key else {},
            timeout=httpx.Timeout(180, connect=10), follow_redirects=False,
        )

    def digest(self) -> str:
        # Remote APIs do not expose an Ollama-style weights digest. Tag the
        # configured service so a provider change can never reuse its vectors.
        identity = ["embedding-api-v1", self.settings.embedding_provider,
                    self.settings.embedding_url, self.settings.embedding_model]
        return hashlib.sha256(json.dumps(identity).encode()).hexdigest()

    def _embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.post(
                f"{self.settings.embedding_url}/embeddings",
                json={"model": self.settings.embedding_model, "input": texts,
                      "encoding_format": "float"},
            )
            response.raise_for_status()
            entries = response.json()["data"]
            if not isinstance(entries, list) or len(entries) != len(texts):
                raise RetrievalError("Il provider ha restituito un numero di embedding errato")
            indexed = {}
            for item in entries:
                index = item["index"]
                vector = item["embedding"]
                if type(index) is not int or not 0 <= index < len(texts) or index in indexed:
                    raise RetrievalError("Ordine degli embedding non verificabile")
                if (
                    not isinstance(vector, list) or not 1 <= len(vector) <= 65536
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector)
                    or not any(vector)
                ):
                    raise RetrievalError("Il provider ha restituito vettori non validi")
                if self.expected_dimension is None:
                    self.expected_dimension = len(vector)
                elif len(vector) != self.expected_dimension:
                    raise RetrievalError("Le dimensioni degli embedding sono cambiate")
                indexed[index] = vector
            return [indexed[i] for i in range(len(texts))]
        except httpx.TimeoutException:
            raise RetrievalError("Tempo di attesa scaduto per il provider di embedding") from None
        except httpx.HTTPStatusError as exc:
            raise RetrievalError(
                f"Il provider ha rifiutato gli embedding ({exc.response.status_code}). "
                "Controlla chiave, modello e lunghezza dei frammenti."
            ) from None
        except RetrievalError:
            raise
        except httpx.HTTPError, ValueError, TypeError, KeyError, OverflowError:
            raise RetrievalError(
                "Provider di embedding non raggiungibile o risposta non valida",
            ) from None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed([f"{self.settings.document_prefix} {text}".strip() for text in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._embed([f"{self.settings.query_prefix} {text}".strip()])[0]

    def close(self):
        self.client.close()
