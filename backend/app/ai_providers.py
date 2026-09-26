"""Provider protocols and UI metadata; model names are discovered from each service."""

from dataclasses import asdict, dataclass
from typing import Literal

ProviderId = Literal[
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "mistral",
    "xai",
    "groq",
    "openrouter",
    "ollama",
    "compatible",
]


@dataclass(frozen=True)
class Provider:
    id: str
    name: str
    base_url: str
    credentials_url: str
    description: str
    requires_key: bool = True
    browser_login: bool = False


PROVIDERS = {
    item.id: item
    for item in (
        Provider(
            "openai",
            "OpenAI",
            "https://api.openai.com/v1",
            "https://platform.openai.com/api-keys",
            "Modelli GPT tramite API OpenAI",
        ),
        Provider(
            "anthropic",
            "Anthropic · Claude",
            "https://api.anthropic.com/v1",
            "https://platform.claude.com/settings/keys",
            "Modelli Claude tramite API Anthropic",
        ),
        Provider(
            "google",
            "Google · Gemini",
            "https://generativelanguage.googleapis.com/v1beta/openai",
            "https://aistudio.google.com/apikey",
            "Modelli Gemini tramite Google AI Studio",
        ),
        Provider(
            "deepseek",
            "DeepSeek",
            "https://api.deepseek.com",
            "https://platform.deepseek.com/api_keys",
            "Modelli DeepSeek",
        ),
        Provider(
            "mistral",
            "Mistral",
            "https://api.mistral.ai/v1",
            "https://console.mistral.ai/api-keys",
            "Modelli Mistral",
        ),
        Provider(
            "xai",
            "xAI · Grok",
            "https://api.x.ai/v1",
            "https://console.x.ai",
            "Modelli Grok tramite API xAI",
        ),
        Provider(
            "groq",
            "Groq",
            "https://api.groq.com/openai/v1",
            "https://console.groq.com/keys",
            "Modelli ospitati da Groq",
        ),
        Provider(
            "openrouter",
            "OpenRouter",
            "https://openrouter.ai/api/v1",
            "https://openrouter.ai/settings/keys",
            "Un account per modelli di diversi fornitori",
            browser_login=True,
        ),
        Provider(
            "ollama",
            "Ollama",
            "http://127.0.0.1:11434",
            "https://ollama.com",
            "Servizio Ollama locale o remoto",
            requires_key=False,
        ),
        Provider(
            "compatible",
            "Altro servizio compatibile",
            "",
            "",
            "Endpoint personalizzato compatibile con Chat Completions",
            requires_key=False,
        ),
    )
}


def provider_catalog() -> list[dict]:
    return [asdict(item) for item in PROVIDERS.values()]


def provider_headers(provider: str, api_key: str | None) -> dict[str, str]:
    if provider == "anthropic":
        return {"x-api-key": api_key or "", "anthropic-version": "2023-06-01"}
    return {"Authorization": f"Bearer {api_key}"} if api_key else {}
