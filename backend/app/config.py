from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "backend" / ".env")


@dataclass(frozen=True)
class DeepSeekSettings:
    api_key: str | None
    model: str
    base_url: str


def get_deepseek_settings() -> DeepSeekSettings:
    return DeepSeekSettings(
        api_key=os.getenv("DEEPSEEK_API_KEY") or None,
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
    )
