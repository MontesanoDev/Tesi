"""Local diagnostics for chat routing; never authorizes a session operation."""

import json
import logging
import time
from pathlib import Path
from uuid import uuid4

import httpx
from pydantic import ValidationError

from app.config import get_ai_settings
from app.db import get_storage_path
from app.generation import GenerationTruncatedError

logger = logging.getLogger(__name__)


def failure_notice(exc):
    """Describe known failure classes without publishing arbitrary exception text."""
    cause = exc.__cause__
    if isinstance(exc, GenerationTruncatedError):
        return "Il modello ha interrotto la risposta per il limite di output."
    if isinstance(cause, httpx.HTTPStatusError):
        return f"Il servizio AI ha rifiutato la richiesta ({cause.response.status_code})."
    if isinstance(cause, httpx.TimeoutException):
        return "Il servizio AI non ha risposto in tempo."
    if isinstance(cause, httpx.HTTPError):
        return "Non riesco a raggiungere il servizio AI."
    if isinstance(cause, (ValidationError, ValueError, RecursionError)):
        return "La risposta del modello non rispetta il formato richiesto."
    return "Il servizio AI non ha restituito una decisione utilizzabile."


class RoutingTrace:
    def __init__(self, folder: Path, secret: str | None):
        self.folder, self.secret = folder, secret
        self.attempts = []
        self.started = time.perf_counter()
        self.result = {}

    @classmethod
    def for_session(cls, session):
        relative = ((session or {}).get("global_compilation") or {}).get("artifact_path")
        if not relative or session.get("engine") != "global":
            return None
        root = get_storage_path().resolve()
        artifact = (root / relative).resolve()
        if not artifact.is_relative_to(root) or not artifact.is_dir():
            return None
        return cls(artifact / "routing" / uuid4().hex, get_ai_settings().api_key)

    def redact(self, text):
        return text.replace(self.secret, "[REDACTED]") if self.secret else text

    def save(self):
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            raw = json.dumps({"attempts": self.attempts, "result": self.result,
                              "seconds": time.perf_counter() - self.started},
                             ensure_ascii=False, indent=2)
            (self.folder / "trace.json").write_text(self.redact(raw) + "\n",
                encoding="utf-8", errors="backslashreplace")
        except OSError:
            # Diagnostics must not fail a valid export or mask its actual error.
            logger.warning("Unable to save compilation routing trace")

    def attempt(self, body, schema):
        self.attempt_started = time.perf_counter()
        self.attempts.append({"request": body, "schema": schema, "status": "pending"})
        self.save()

    def response(self, raw, model, usage):
        self.attempts[-1].update(raw=raw, model=model, usage=usage, status="received",
                                seconds=time.perf_counter() - self.attempt_started)
        self.save()

    async def http_response(self, response):
        await response.aread()
        self.attempts[-1].update(http_status=response.status_code,
                                http_response=response.text[:65536])
        self.save()

    def validation_error(self, exc):
        errors = (exc.errors(include_input=False, include_url=False)
                  if hasattr(exc, "errors") else str(exc))
        self.attempts[-1].update(status="invalid", validation_error=str(errors)[:4000])
        self.save()

    def complete(self, intent):
        self.result = {"status": "routed", "intent": intent}
        self.save()

    def fail(self, exc, stage):
        if self.attempts and self.attempts[-1]["status"] == "pending":
            self.attempts[-1].update(status="interrupted",
                seconds=time.perf_counter() - self.attempt_started)
        self.result = {"status": "failed", "stage": stage,
                       "error": type(exc).__name__, "message": str(exc)[:2000]}
        if cause := exc.__cause__:
            self.result.update(cause=type(cause).__name__, cause_message=str(cause)[:2000])
            if response := getattr(cause, "response", None):
                self.result.update(http_status=response.status_code,
                                   http_response=response.text[:16000])
        self.save()
