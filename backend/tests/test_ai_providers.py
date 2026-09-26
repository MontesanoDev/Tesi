"""Provider discovery, native protocols and account linking, with fake credentials only."""

import base64
import hashlib
import json
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from test_ai_settings import DEEPSEEK, PROJECT, SECRET
from test_ai_settings import anyio_backend as anyio_backend
from test_ai_settings import client as client

from app.ai_login import token_hash
from app.ai_profiles import _decrypt, resolve_project_settings
from app.ai_providers import PROVIDERS
from app.ai_transport import post_chat
from app.config import DeepSeekSettings
from app.db import connection, get_db_path, init_database


def mock_provider(monkeypatch, handler):
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(
            transport=httpx.MockTransport(handler),
            **kw,
        ),
    )


@pytest.mark.anyio
async def test_migration_preserves_keys_and_foreign_keys(client):
    old = (await client.post("/api/settings/ai/profiles", json=DEEPSEEK)).json()
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": old["id"]})
    with connection() as db:
        encrypted = db.execute("SELECT encrypted_api_key FROM ai_profiles").fetchone()[0]
        db.execute("PRAGMA foreign_keys=OFF")
        db.executescript("""
            CREATE TABLE ai_profiles_old (
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                provider TEXT NOT NULL CHECK(provider IN ('deepseek', 'ollama', 'compatible')),
                base_url TEXT NOT NULL, model TEXT NOT NULL, encrypted_api_key TEXT,
                context_window INTEGER NOT NULL DEFAULT 32768,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO ai_profiles_old SELECT * FROM ai_profiles;
            DROP TABLE ai_profiles;
            ALTER TABLE ai_profiles_old RENAME TO ai_profiles;
        """)
    init_database()
    init_database()
    result = (await client.get("/api/settings/ai")).json()
    assert result["profiles"] == [old] and result["default_profile_id"] == old["id"]
    assert {item["id"] for item in result["providers"]} == set(PROVIDERS)
    selected = (await client.get(f"/api/projects/{PROJECT}/ai-model")).json()
    assert selected == {"profile_id": old["id"], "effective_profile": old}
    assert resolve_project_settings(PROJECT).api_key == SECRET
    with connection() as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("SELECT encrypted_api_key FROM ai_profiles").fetchone()[0] == encrypted
    response = await client.post(
        "/api/settings/ai/profiles", json={**DEEPSEEK, "provider": "anthropic"}
    )
    assert response.status_code == 201


@pytest.mark.anyio
@pytest.mark.parametrize("provider", list(PROVIDERS))
async def test_discovery_auth_pagination_and_text_filters(client, monkeypatch, provider):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.method == "GET"
        if provider == "anthropic":
            assert request.headers["x-api-key"] == SECRET
            assert request.headers["anthropic-version"] == "2023-06-01"
            assert "authorization" not in request.headers
            if "after_id" not in request.url.params:
                return httpx.Response(
                    200,
                    json={
                        "data": [{"id": "model-a"}],
                        "has_more": True,
                        "last_id": "model-a",
                    },
                )
            assert request.url.params["after_id"] == "model-a"
        else:
            assert request.headers.get("authorization") == f"Bearer {SECRET}"
        if request.url.path.endswith("/key"):
            return httpx.Response(200, json={"data": {"label": "test key"}})
        if provider == "ollama":
            assert request.url.path == "/api/tags"
            return httpx.Response(
                200,
                json={
                    "models": [
                        {"name": "model-a"},
                        {
                            "name": "model-b",
                            "capabilities": [
                                "completion",
                                "vision",
                                "audio",
                                "tools",
                                "thinking",
                            ],
                        },
                    ]
                },
            )
        assert request.url.path == "/models"
        entries = [{"id": "model-b"}, {"id": "model-a"}, {"id": "model-a"}, {"id": ""}, None]
        if provider == "openai":
            entries += [{"id": "text-embedding-test"}, {"id": "gpt-audio-test"}]
        if provider == "mistral":
            entries += [
                {"id": "embedding-test", "capabilities": {"completion_chat": False}},
                {"id": "invalid-mistral-metadata", "capabilities": ["completion"]},
            ]
        if provider == "openrouter":
            entries += [
                {"id": "image-test", "architecture": {"output_modalities": ["image"]}},
                {"id": "no-json-test", "supported_parameters": ["temperature"]},
            ]
        return httpx.Response(200, json={"data": entries})

    mock_provider(monkeypatch, handler)
    response = await client.post("/api/settings/ai/check", json={**DEEPSEEK, "provider": provider})
    assert response.status_code == 200, response.text
    assert response.json()["models"] == ["model-a", "model-b"]
    assert len(calls) == (2 if provider in {"anthropic", "openrouter"} else 1)


@pytest.mark.anyio
async def test_openrouter_checks_key_before_public_inventory(client, monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(401, json={"error": SECRET})

    mock_provider(monkeypatch, handler)
    response = await client.post(
        "/api/settings/ai/check", json={**DEEPSEEK, "provider": "openrouter"}
    )
    assert response.status_code == 502 and SECRET not in response.text
    assert len(calls) == 1 and calls[0].url.path == "/key"


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["openai", "anthropic"])
@pytest.mark.parametrize("finish", ["complete", "length", "refusal", "incomplete"])
async def test_native_protocols_normalize_finish_reasons_and_usage(provider, finish):
    settings = DeepSeekSettings(SECRET, "test-model", "https://provider.test/v1", provider)
    messages = [{"role": "system", "content": "Return JSON"}, {"role": "user", "content": "Test"}]

    def handler(request):
        body = json.loads(request.content)
        assert "temperature" not in body and "thinking" not in body
        assert "response_format" not in body
        if provider == "openai":
            assert request.url.path == "/v1/responses"
            assert request.headers["authorization"] == f"Bearer {SECRET}"
            assert body == {
                "model": "test-model",
                "input": messages,
                "store": False,
                "max_output_tokens": 800,
                "text": {"format": {"type": "json_object"}},
            }
            block = (
                {"type": "refusal", "refusal": "No"}
                if finish == "refusal"
                else {
                    "type": "output_text",
                    "text": '{"ok":true}',
                }
            )
            return httpx.Response(
                200,
                json={
                    "status": "completed" if finish in {"complete", "refusal"} else "incomplete",
                    "output": [{"type": "reasoning"}, {"type": "message", "content": [block]}],
                    "incomplete_details": {"reason": "max_output_tokens"}
                    if finish == "length"
                    else None,
                    "usage": {"total_tokens": 33},
                },
            )
        assert request.url.path == "/v1/messages"
        assert request.headers["x-api-key"] == SECRET
        assert body == {
            "model": "test-model",
            "system": messages[0]["content"],
            "messages": messages[1:],
            "max_tokens": 800,
            "stream": False,
        }
        return httpx.Response(
            200,
            json={
                "stop_reason": {
                    "complete": "end_turn",
                    "length": "max_tokens",
                    "refusal": "refusal",
                    "incomplete": "pause_turn",
                }[finish],
                "content": [{"type": "text", "text": '{"ok":true}'}],
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 12,
                    "cache_creation_input_tokens": 6,
                    "cache_read_input_tokens": 5,
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as remote:
        response = await post_chat(
            remote,
            settings,
            {
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.1,
                "thinking": {"type": "disabled"},
            },
        )
    result = response.json()
    assert result["usage"]["total_tokens"] == 33 and result["model"] == "test-model"
    assert (
        result["choices"][0]["finish_reason"]
        == {
            "complete": "stop",
            "length": "length",
            "refusal": "content_filter",
            "incomplete": "incomplete",
        }[finish]
    )


@pytest.mark.anyio
async def test_pkce_keeps_key_private_and_consumes_login_on_save(client, monkeypatch):
    begin = await client.post("/api/settings/ai/openrouter/login")
    assert begin.status_code == 200 and begin.headers["cache-control"] == "no-store"
    flow = begin.json()
    token = flow["connection_token"]
    url = urlsplit(flow["authorization_url"])
    assert url.scheme == "https" and url.netloc == "openrouter.ai"
    with connection() as db:
        row = db.execute("SELECT * FROM ai_login_flows").fetchone()
        assert row["token_hash"] == token_hash(token)
        verifier = _decrypt(row["encrypted_verifier"])
        assert token not in str(dict(row)) and verifier not in str(dict(row))
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    )
    assert parse_qs(url.query)["code_challenge"] == [challenge]
    assert parse_qs(url.query)["code_challenge_method"] == ["S256"]
    calls = []

    def handler(request):
        calls.append(request)
        assert request.url.host == "openrouter.ai"
        if request.method == "POST":
            assert request.url.path == "/api/v1/auth/keys"
            assert json.loads(request.content) == {
                "code": "test-code",
                "code_verifier": verifier,
                "code_challenge_method": "S256",
            }
            return httpx.Response(200, json={"key": SECRET})
        assert request.headers["authorization"] == f"Bearer {SECRET}"
        return httpx.Response(200, json={"data": [{"id": "provider/model"}]})

    mock_provider(monkeypatch, handler)
    profile = {
        **DEEPSEEK,
        "provider": "openrouter",
        "api_key": "",
        "base_url": PROVIDERS["openrouter"].base_url,
        "connection_token": token,
    }
    assert (await client.post("/api/settings/ai/check", json=profile)).status_code == 422
    complete = await client.post(
        "/api/settings/ai/openrouter/login/complete",
        json={
            "connection_token": token,
            "code": "test-code",
        },
    )
    assert complete.status_code == 200 and SECRET not in complete.text
    replay = await client.post(
        "/api/settings/ai/openrouter/login/complete",
        json={
            "connection_token": token,
            "code": "test-code",
        },
    )
    assert replay.status_code == 422 and len(calls) == 1
    with connection() as db:
        row = db.execute("SELECT * FROM ai_login_flows").fetchone()
        assert row["encrypted_verifier"] is None and SECRET not in row["encrypted_api_key"]
    for patch in [{"base_url": "https://attacker.test"}, {"provider": "openai"}]:
        assert (
            await client.post("/api/settings/ai/check", json={**profile, **patch})
        ).status_code == 422
    assert len(calls) == 1
    assert (await client.post("/api/settings/ai/check", json=profile)).status_code == 200
    saved = await client.post("/api/settings/ai/profiles", json=profile)
    assert saved.status_code == 201 and SECRET not in saved.text and token not in saved.text
    assert resolve_project_settings(PROJECT).api_key == SECRET
    assert (await client.post("/api/settings/ai/profiles", json=profile)).status_code == 422
    with connection() as db:
        assert db.execute("SELECT count(*) FROM ai_login_flows").fetchone()[0] == 0


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["expired", "wrong_token", "http", "bad_json", "redirect"])
async def test_failed_login_hides_secrets_and_creates_no_profile(client, monkeypatch, failure):
    token = (await client.post("/api/settings/ai/openrouter/login")).json()["connection_token"]
    calls = []
    if failure == "expired":
        with connection() as db:
            db.execute("UPDATE ai_login_flows SET expires_at=0")
    if failure == "wrong_token":
        token = "x" * 64

    def handler(request):
        calls.append(request)
        return httpx.Response(
            307 if failure == "redirect" else 401 if failure == "http" else 200,
            json={"error": SECRET},
            headers={"Location": "https://attacker.test"},
        )

    mock_provider(monkeypatch, handler)
    response = await client.post(
        "/api/settings/ai/openrouter/login/complete",
        json={
            "connection_token": token,
            "code": SECRET,
        },
    )
    assert (
        response.status_code == 422 and SECRET not in response.text and token not in response.text
    )
    assert len(calls) == (0 if failure in {"expired", "wrong_token"} else 1)
    assert (await client.get("/api/settings/ai")).json()["profiles"] == []


@pytest.mark.anyio
async def test_input_errors_hide_codes_and_missing_cipher_is_not_replaced(client):
    response = await client.post(
        "/api/settings/ai/openrouter/login/complete",
        json={
            "connection_token": "short",
            "code": SECRET,
        },
    )
    assert response.status_code == 422 and SECRET not in response.text
    await client.post("/api/settings/ai/openrouter/login")
    get_db_path().with_suffix(".ai-key").unlink()
    response = await client.post("/api/settings/ai/openrouter/login")
    assert response.status_code == 422
    assert not get_db_path().with_suffix(".ai-key").exists()
