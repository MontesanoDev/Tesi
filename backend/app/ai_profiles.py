"""Saved AI connections and project selection. Credentials never enter public payloads."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from urllib.parse import urlsplit
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.ai_providers import PROVIDERS, ProviderId, provider_catalog
from app.config import AISettings, get_environment_settings, use_ai_settings
from app.db import connection, get_db_path


class ProfileError(ValueError):
    pass


class ProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    provider: ProviderId
    base_url: str = Field(min_length=1, max_length=500)
    model: str = Field(min_length=1, max_length=160)
    api_key: SecretStr | None = None  # None/empty preserves an existing credential.
    connection_token: SecretStr | None = Field(default=None, min_length=32, max_length=200)
    clear_api_key: bool = False
    context_window: int = Field(default=32768, ge=2048, le=1048576)

    @field_validator("base_url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        try:
            parts = urlsplit(value)
            if (
                parts.scheme not in {"http", "https"}
                or not parts.hostname
                or parts.username
                or parts.password
                or parts.query
                or parts.fragment
                or any(char.isspace() or ord(char) < 32 for char in value)
            ):
                raise ValueError
            _ = parts.port
        except ValueError:
            raise ValueError(
                "Usa un indirizzo http o https senza credenziali o parametri"
            ) from None
        return value.rstrip("/")

    @field_validator("name", "model")
    @classmethod
    def clean_text(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("Il testo contiene caratteri non validi")
        return value


def _cipher(*, create: bool = False) -> Fernet:
    # The key lives beside this database, outside uploaded/downloadable documents.
    path = get_db_path().with_suffix(".ai-key")
    if create and not path.exists():
        with connection() as db:
            if (
                db.execute(
                    "SELECT 1 FROM ai_profiles WHERE encrypted_api_key IS NOT NULL LIMIT 1"
                ).fetchone()
                or db.execute("SELECT 1 FROM ai_login_flows LIMIT 1").fetchone()
            ):
                raise ProfileError(
                    "Il file .ai-key manca ma ci sono chiavi salvate. Ripristina il backup."
                )
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        except OSError:
            raise ProfileError("Impossibile creare l'archivio delle chiavi sul server") from None
        else:
            with os.fdopen(descriptor, "wb") as target:
                target.write(Fernet.generate_key())
    try:
        return Fernet(path.read_bytes())
    except OSError, ValueError:
        raise ProfileError(
            "Archivio delle chiavi non disponibile. Ripristina il file .ai-key del backup."
        ) from None


def _decrypt(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return _cipher().decrypt(value.encode()).decode()
    except InvalidToken:
        raise ProfileError("Impossibile leggere la chiave salvata: ripristina il backup.") from None


def _public(row: sqlite3.Row | dict) -> dict:
    return {
        key: row[key]
        for key in (
            "id",
            "name",
            "provider",
            "base_url",
            "model",
            "context_window",
        )
    } | {"has_api_key": bool(row["encrypted_api_key"])}


def _get_row(db: sqlite3.Connection, profile_id: str) -> sqlite3.Row:
    row = db.execute("SELECT * FROM ai_profiles WHERE id = ?", (profile_id,)).fetchone()
    if row is None:
        raise LookupError("Configurazione AI non trovata")
    return row


def _resolved_key(payload: ProfileInput, previous: sqlite3.Row | None) -> str | None:
    new_key = payload.api_key.get_secret_value().strip() if payload.api_key else ""
    if len(new_key) > 4096 or any(ord(char) < 32 for char in new_key):
        raise ProfileError("La chiave API contiene caratteri non validi o e troppo lunga")
    if payload.clear_api_key:
        key = None
    elif new_key:
        key = new_key
    elif payload.connection_token:
        from app.ai_login import pending_key

        if payload.provider != "openrouter" or payload.base_url != PROVIDERS["openrouter"].base_url:
            raise ProfileError(
                "Il collegamento account e valido solo per l'indirizzo ufficiale OpenRouter"
            )
        key = pending_key(payload.connection_token.get_secret_value())
    elif previous is not None:
        if previous["encrypted_api_key"] and (
            payload.base_url != previous["base_url"] or payload.provider != previous["provider"]
        ):
            raise ProfileError("Se cambi servizio o indirizzo, inserisci nuovamente la chiave API")
        key = _decrypt(previous["encrypted_api_key"])
    else:
        key = None
    if PROVIDERS[payload.provider].requires_key and not key:
        raise ProfileError(f"Inserisci la chiave API di {PROVIDERS[payload.provider].name}")
    return key


def settings_for_input(payload: ProfileInput, profile_id: str | None = None) -> AISettings:
    with connection() as db:
        previous = _get_row(db, profile_id) if profile_id else None
        key = _resolved_key(payload, previous)
    return AISettings(
        api_key=key,
        model=payload.model,
        base_url=payload.base_url,
        provider=payload.provider,
        context_window=payload.context_window,
        profile_id=profile_id,
    )


def list_settings() -> dict:
    with connection() as db:
        profiles = db.execute("SELECT * FROM ai_profiles ORDER BY created_at, rowid").fetchall()
        default = db.execute(
            "SELECT default_profile_id FROM ai_preferences WHERE id = 1"
        ).fetchone()
        return {
            "profiles": [_public(row) for row in profiles],
            "default_profile_id": default[0],
            "providers": provider_catalog(),
        }


def save_profile(payload: ProfileInput, profile_id: str | None = None) -> dict:
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        previous = _get_row(db, profile_id) if profile_id else None
        key = _resolved_key(payload, previous)
        encrypted = _cipher(create=True).encrypt(key.encode()).decode() if key else None
        values = (
            payload.name,
            payload.provider,
            payload.base_url,
            payload.model,
            encrypted,
            payload.context_window,
        )
        if profile_id:
            db.execute(
                "UPDATE ai_profiles SET name=?, provider=?, base_url=?, model=?, "
                "encrypted_api_key=?, context_window=? WHERE id=?",
                (*values, profile_id),
            )
        else:
            profile_id = uuid4().hex
            first = db.execute("SELECT COUNT(*) FROM ai_profiles").fetchone()[0] == 0
            db.execute(
                "INSERT INTO ai_profiles(name, provider, base_url, model, encrypted_api_key, "
                "context_window, id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (*values, profile_id),
            )
            if first:
                db.execute(
                    "UPDATE ai_preferences SET default_profile_id=? WHERE id=1",
                    (profile_id,),
                )
        db.execute(
            "INSERT OR REPLACE INTO app_metadata(key, value) VALUES ('ai_settings_managed', '1')"
        )
        if payload.connection_token:
            from app.ai_login import token_hash

            db.execute(
                "DELETE FROM ai_login_flows WHERE token_hash=?",
                (token_hash(payload.connection_token.get_secret_value()),),
            )
        return _public(_get_row(db, profile_id))


def set_default(profile_id: str | None) -> dict:
    with connection() as db:
        if profile_id is not None:
            _get_row(db, profile_id)
        db.execute("UPDATE ai_preferences SET default_profile_id=? WHERE id=1", (profile_id,))
    return list_settings()


def delete_profile(profile_id: str) -> None:
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        _get_row(db, profile_id)
        if db.execute(
            "SELECT 1 FROM project_ai_settings WHERE profile_id=? LIMIT 1",
            (profile_id,),
        ).fetchone():
            raise ProfileError(
                "Questa configurazione e selezionata in un progetto. Cambia prima il suo modello."
            )
        db.execute("DELETE FROM ai_profiles WHERE id=?", (profile_id,))


def project_selection(project_id: str) -> dict:
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone() is None:
            raise LookupError("Progetto non trovato")
        row = db.execute(
            "SELECT profile_id FROM project_ai_settings WHERE project_id=?",
            (project_id,),
        ).fetchone()
        selected = row[0] if row else None
        default = db.execute("SELECT default_profile_id FROM ai_preferences WHERE id=1").fetchone()[
            0
        ]
        effective = selected or default
        return {
            "profile_id": selected,
            "effective_profile": _public(_get_row(db, effective)) if effective else None,
        }


def select_project_profile(project_id: str, profile_id: str | None) -> dict:
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone() is None:
            raise LookupError("Progetto non trovato")
        if profile_id is None:
            db.execute("DELETE FROM project_ai_settings WHERE project_id=?", (project_id,))
        else:
            _get_row(db, profile_id)
            db.execute(
                "INSERT INTO project_ai_settings(project_id, profile_id) VALUES (?, ?) "
                "ON CONFLICT(project_id) DO UPDATE SET profile_id=excluded.profile_id",
                (project_id, profile_id),
            )
    return project_selection(project_id)


def resolve_project_settings(project_id: str) -> AISettings:
    with connection() as db:
        row = db.execute(
            "SELECT a.* FROM ai_profiles a WHERE a.id = COALESCE("
            "(SELECT profile_id FROM project_ai_settings WHERE project_id=?),"
            "(SELECT default_profile_id FROM ai_preferences WHERE id=1))",
            (project_id,),
        ).fetchone()
        if row:
            return AISettings(
                api_key=_decrypt(row["encrypted_api_key"]),
                model=row["model"],
                base_url=row["base_url"],
                provider=row["provider"],
                profile_id=row["id"],
                context_window=row["context_window"],
            )
        managed = db.execute(
            "SELECT 1 FROM app_metadata WHERE key='ai_settings_managed'"
        ).fetchone()
    if not managed:
        return get_environment_settings()
    # Deleting a profile must never silently reactivate old cloud credentials.
    return AISettings(api_key=None, model="", base_url="")


@contextmanager
def project_ai_context(project_id: str):
    from app.generation import GenerationNotConfiguredError

    try:
        settings = resolve_project_settings(project_id)
    except ProfileError as exc:
        raise GenerationNotConfiguredError(str(exc)) from exc
    with use_ai_settings(settings):
        yield


def import_legacy_configuration() -> None:
    """One-time upgrade: existing installations can edit their configuration from the UI."""
    with connection() as db:
        managed = db.execute(
            "SELECT 1 FROM app_metadata WHERE key='ai_settings_managed'"
        ).fetchone()
    legacy = get_environment_settings()
    if not managed and legacy.api_key:
        save_profile(
            ProfileInput(
                name="DeepSeek",
                provider="deepseek",
                base_url=legacy.base_url,
                model=legacy.model,
                api_key=SecretStr(legacy.api_key),
            )
        )
