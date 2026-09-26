"""Read provider model inventories; never generate text during connection checks."""

import re

import httpx

from app.ai_providers import provider_headers
from app.config import DeepSeekSettings


async def discover_models(settings: DeepSeekSettings) -> list[str]:
    headers = provider_headers(settings.provider, settings.api_key)
    url = (
        f"{settings.base_url.removesuffix('/v1')}/api/tags"
        if settings.provider == "ollama"
        else f"{settings.base_url}/models"
    )
    entries = []
    async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
        if settings.provider == "openrouter":
            # /models is public: a successful catalog read alone does not validate the key.
            verified = await client.get(f"{settings.base_url}/key", headers=headers)
            verified.raise_for_status()
        params = {"limit": 100} if settings.provider == "anthropic" else {}
        for _ in range(20):
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Elenco modelli non valido")
            raw = data.get("models" if settings.provider == "ollama" else "data")
            if not isinstance(raw, list):
                raise ValueError("Elenco modelli non valido")
            entries.extend(raw)
            if settings.provider != "anthropic" or not data.get("has_more"):
                break
            cursor = data.get("last_id")
            if not isinstance(cursor, str) or cursor == params.get("after_id"):
                raise ValueError("Paginazione dei modelli non valida")
            params["after_id"] = cursor
        else:
            raise ValueError("Elenco modelli troppo esteso")
    key = "name" if settings.provider == "ollama" else "id"
    models = set()
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get(key), str):
            continue
        model = item[key]
        if not 0 < len(model) <= 160 or any(ord(c) < 32 for c in model):
            continue
        if settings.provider == "openai" and re.search(
            r"embedding|whisper|tts|audio|realtime|dall-e|image|moderation|transcri|sora|babbage|davinci",
            model,
            re.I,
        ):
            continue
        if settings.provider == "mistral":
            # Mistral uses an object; Ollama uses a list of capability names.
            capabilities = item.get("capabilities") or {}
            if not isinstance(capabilities, dict) or capabilities.get("completion_chat") is False:
                continue
        if settings.provider == "openrouter":
            architecture = item.get("architecture") or {}
            if not isinstance(architecture, dict):
                continue
            outputs = architecture.get("output_modalities", ["text"])
            if not isinstance(outputs, list) or "text" not in outputs:
                continue
            parameters = item.get("supported_parameters")
            if isinstance(parameters, list) and "response_format" not in parameters:
                continue
        models.add(model)
    return sorted(models)
