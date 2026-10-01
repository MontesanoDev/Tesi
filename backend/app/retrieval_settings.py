"""Retrieval configuration is independent of the model used to generate answers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from threading import RLock
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.ai_profiles import ProfileError, ProfileInput, _cipher, _decrypt
from app.db import connection

RETRIEVAL_LOCK = RLock()  # Local Qdrant is single-process; serialize index/config changes.
SETTINGS_KEY = "retrieval_settings_v1"


class RetrievalError(ValueError):
    pass


class RetrievalInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    backend: Literal["fts5", "qdrant"] = "fts5"
    qdrant_mode: Literal["local", "remote"] = "local"
    qdrant_url: str = Field(default="http://127.0.0.1:6333", max_length=500)
    qdrant_api_key: SecretStr | None = None
    clear_qdrant_api_key: bool = False
    embedding_url: str = Field(default="http://127.0.0.1:11434", max_length=500)
    embedding_model: str = Field(default="bge-m3", min_length=1, max_length=160)
    embedding_api_key: SecretStr | None = None
    clear_embedding_api_key: bool = False
    query_prefix: str = Field(default="", max_length=500)
    document_prefix: str = Field(default="", max_length=500)

    @field_validator("qdrant_url", "embedding_url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        return ProfileInput.clean_url(value)

    @field_validator("embedding_model", "query_prefix", "document_prefix")
    @classmethod
    def clean_text(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("Il testo contiene caratteri non validi")
        return value


@dataclass(frozen=True)
class RetrievalSettings:
    backend: str
    qdrant_mode: str
    qdrant_url: str
    embedding_url: str
    embedding_model: str
    query_prefix: str
    document_prefix: str
    qdrant_api_key: str | None = field(default=None, repr=False)
    embedding_api_key: str | None = field(default=None, repr=False)


def _stored() -> dict:
    with connection() as db:
        row = db.execute("SELECT value FROM app_metadata WHERE key=?", (SETTINGS_KEY,)).fetchone()
    return json.loads(row[0]) if row else {}


def public_settings(stored: dict | None = None) -> dict:
    stored = _stored() if stored is None else stored
    defaults = RetrievalInput().model_dump()
    return {
        name: stored.get(name, value) for name, value in defaults.items() if "api_key" not in name
    } | {
        "has_qdrant_api_key": bool(stored.get("encrypted_qdrant_api_key")),
        "has_embedding_api_key": bool(stored.get("encrypted_embedding_api_key")),
    }


def resolve_settings(payload: RetrievalInput | None = None) -> RetrievalSettings:
    stored = _stored()
    public = {k: v for k, v in public_settings(stored).items() if not k.startswith("has_")}
    values = payload.model_dump() if payload else RetrievalInput(**public).model_dump()
    for service in ("qdrant", "embedding"):
        key_name = f"{service}_api_key"
        secret = values.pop(key_name)
        clear = values.pop(f"clear_{key_name}")
        raw = secret.get_secret_value().strip() if secret else None
        if raw and (len(raw) > 4096 or any(ord(char) < 32 for char in raw)):
            raise ProfileError("La chiave contiene caratteri non validi o e troppo lunga")
        saved = stored.get(f"encrypted_{key_name}")
        if saved and not clear and not raw and values[f"{service}_url"] != stored[f"{service}_url"]:
            raise ProfileError("Indirizzo modificato: reinserisci o rimuovi la relativa chiave API")
        values[key_name] = None if clear else raw or _decrypt(saved)
    return RetrievalSettings(**values)


def save_settings(payload: RetrievalInput) -> dict:
    with RETRIEVAL_LOCK:
        settings = resolve_settings(payload)
        stored = {key: value for key, value in vars(settings).items() if "api_key" not in key}
        for service in ("qdrant", "embedding"):
            secret = getattr(settings, f"{service}_api_key")
            stored[f"encrypted_{service}_api_key"] = (
                _cipher(create=True).encrypt(secret.encode()).decode() if secret else None
            )
        with connection() as db:
            db.execute(
                "INSERT INTO app_metadata(key,value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (SETTINGS_KEY, json.dumps(stored)),
            )
        return public_settings()
