"""Provider-specific wire format; callers keep their existing JSON validation."""

from __future__ import annotations

import httpx

from app.ai_providers import provider_headers
from app.config import AISettings


def _normalized(
    response: httpx.Response,
    settings: AISettings,
    content: str,
    finish_reason: str,
    total_tokens: int | None,
    model: str | None,
) -> httpx.Response:
    return httpx.Response(
        200,
        request=response.request,
        json={
            "model": model or settings.model,
            "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
            "usage": {"total_tokens": total_tokens} if type(total_tokens) is int else {},
        },
    )


def _object(response: httpx.Response) -> dict:
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Risposta del servizio non valida")
    return data


async def _openai(
    client: httpx.AsyncClient, settings: AISettings, body: dict
) -> httpx.Response:
    # Responses supports current OpenAI text models without legacy max_tokens/temperature.
    response = await client.post(
        f"{settings.base_url}/responses",
        headers=provider_headers(settings.provider, settings.api_key),
        json={
            "model": settings.model,
            "input": body["messages"],
            "max_output_tokens": body["max_tokens"],
            "store": False,
            "text": {"format": {"type": "json_object"}},
        },
    )
    data = _object(response)
    if data.get("error") or not isinstance(data.get("output"), list):
        raise ValueError("Risposta OpenAI non valida")
    parts, refused = [], False
    for item in data["output"]:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        if not isinstance(item.get("content"), list):
            raise ValueError("Contenuto OpenAI non valido")
        for block in item["content"]:
            if not isinstance(block, dict):
                raise ValueError("Contenuto OpenAI non valido")
            if block.get("type") == "refusal":
                refused = True
            elif block.get("type") == "output_text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    reason = "stop" if data.get("status") == "completed" else "incomplete"
    details = data.get("incomplete_details") or {}
    if not isinstance(details, dict):
        raise ValueError("Stato OpenAI non valido")
    if refused or details.get("reason") == "content_filter":
        reason = "content_filter"
    elif details.get("reason") == "max_output_tokens":
        reason = "length"
    if reason == "stop" and not parts:
        raise ValueError("Risposta OpenAI priva di testo")
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        raise ValueError("Conteggio token OpenAI non valido")
    return _normalized(
        response, settings, "".join(parts), reason, usage.get("total_tokens"), data.get("model")
    )


async def _anthropic(
    client: httpx.AsyncClient, settings: AISettings, body: dict
) -> httpx.Response:
    # Messages uses a top-level system prompt; JSON is requested by the existing prompts.
    # Do not send OpenAI's response_format or assume every Claude supports a fixed temperature.
    response = await client.post(
        f"{settings.base_url}/messages",
        headers=provider_headers(settings.provider, settings.api_key),
        json={
            "model": settings.model,
            "max_tokens": body["max_tokens"],
            "system": "\n\n".join(
                item["content"] for item in body["messages"] if item["role"] == "system"
            ),
            "messages": [item for item in body["messages"] if item["role"] != "system"],
            "stream": False,
        },
    )
    data = _object(response)
    if not isinstance(data.get("content"), list):
        raise ValueError("Risposta Claude priva del contenuto")
    parts = [
        block["text"]
        for block in data["content"]
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    reason = {
        "end_turn": "stop",
        "stop_sequence": "stop",
        "max_tokens": "length",
        "refusal": "content_filter",
    }.get(data.get("stop_reason"), "incomplete")
    if reason == "stop" and not parts:
        raise ValueError("Risposta Claude priva di testo")
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        raise ValueError("Conteggio token Claude non valido")
    counts = [
        usage.get(key, 0)
        for key in (
            "input_tokens",
            "output_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
        )
    ]
    tokens = sum(counts) if all(type(value) is int for value in counts) and usage else None
    return _normalized(response, settings, "".join(parts), reason, tokens, data.get("model"))


async def post_chat(
    client: httpx.AsyncClient,
    settings: AISettings,
    body: dict,
) -> httpx.Response:
    if settings.provider == "openai":
        return await _openai(client, settings, body)
    if settings.provider == "anthropic":
        return await _anthropic(client, settings, body)
    headers = provider_headers(settings.provider, settings.api_key)
    payload = dict(body)
    if settings.provider != "deepseek":
        payload.pop("thinking", None)
    if settings.provider in {"google", "xai", "openrouter"}:
        payload.pop("temperature", None)
    if settings.provider != "ollama":
        return await client.post(
            f"{settings.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

    # Native Ollama supports num_ctx, unlike its OpenAI-compatible chat endpoint.
    # The context window is configurable in the UI and no .env/Modelfile is required.
    root = settings.base_url.removesuffix("/v1")
    response = await client.post(
        f"{root}/api/chat",
        headers=headers,
        json={
            "model": settings.model,
            "messages": payload["messages"],
            "stream": False,
            "format": "json",
            "think": False,
            "options": {
                "temperature": payload.get("temperature", 0.1),
                "num_predict": payload["max_tokens"],
                "num_ctx": settings.context_window,
            },
        },
    )
    data = _object(response)
    message = data.get("message") if isinstance(data, dict) else None
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise ValueError("Risposta Ollama priva del messaggio")
    prompt_tokens, output_tokens = data.get("prompt_eval_count"), data.get("eval_count")
    usage = {}
    if type(prompt_tokens) is int and type(output_tokens) is int:
        usage = {"total_tokens": prompt_tokens + output_tokens}
    return httpx.Response(
        200,
        request=response.request,
        json={
            "model": data.get("model") or settings.model,
            "choices": [
                {
                    "message": {"content": message["content"]},
                    "finish_reason": data.get("done_reason") if data.get("done") else "incomplete",
                }
            ],
            "usage": usage,
        },
    )
