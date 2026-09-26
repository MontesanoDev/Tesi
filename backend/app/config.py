from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from app.ai_providers import PROVIDERS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "backend" / ".env")


@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str | None = field(repr=False)
    model: str
    base_url: str
    provider: str = "deepseek"
    profile_id: str | None = None
    context_window: int = 32768

    @property
    def configured(self) -> bool:
        provider = PROVIDERS.get(self.provider)
        return bool(provider and self.model and (self.api_key or not provider.requires_key))

    @property
    def label(self) -> str:
        provider = PROVIDERS.get(self.provider)
        return provider.name if provider else "Il servizio AI"


_active_settings: ContextVar[DeepSeekSettings | None] = ContextVar("ai_settings", default=None)


@contextmanager
def use_ai_settings(settings: DeepSeekSettings):
    """Pin credentials/model for an entire operation, including DOCX batches and repairs."""
    token = _active_settings.set(settings)
    try:
        yield
    finally:
        _active_settings.reset(token)


def get_deepseek_settings() -> DeepSeekSettings:
    # Kept as a compatibility entry point for the existing generation modules and scripts.
    return _active_settings.get() or get_environment_settings()


def get_environment_settings() -> DeepSeekSettings:
    return DeepSeekSettings(
        api_key=os.getenv("DEEPSEEK_API_KEY") or None,
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
    )
