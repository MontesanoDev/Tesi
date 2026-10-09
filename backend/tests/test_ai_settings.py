"""Configuration, credential isolation and provider routing, without external AI calls."""

import asyncio
import json

import httpx
import pytest

from app.ai_profiles import (
    ProfileInput,
    import_legacy_configuration,
    project_ai_context,
    resolve_project_settings,
    save_profile,
    select_project_profile,
)
from app.ai_providers import PROVIDERS
from app.ai_transport import post_chat
from app.artifacts import seed_markdown_artifacts
from app.config import AISettings, get_ai_settings
from app.db import connection, get_db_path, init_database
from app.main import app
from app.seed import seed_database

PROJECT = "fondo-riqualificazione-2027"
SECRET = "test-secret-not-a-real-credential"
DEEPSEEK = {
    "name": "DeepSeek ufficio",
    "provider": "deepseek",
    "api_key": SECRET,
    "base_url": "https://provider.test",
    "model": "remote-test",
}
OLLAMA = {
    "name": "Locale",
    "provider": "ollama",
    "base_url": "http://127.0.0.1:11434",
    "model": "local-test",
    "context_window": 16384,
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    init_database()
    seed_database()
    seed_markdown_artifacts()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as value:
        yield value


@pytest.mark.anyio
async def test_persistence_encryption_defaults_and_selection(client):
    response = await client.post("/api/settings/ai/profiles", json=DEEPSEEK)
    assert response.status_code == 201
    cloud = response.json()
    assert cloud["has_api_key"] is True
    assert SECRET not in response.text
    with connection() as db:
        encrypted = db.execute("SELECT encrypted_api_key FROM ai_profiles").fetchone()[0]
        assert encrypted and SECRET not in encrypted
    assert get_db_path().with_suffix(".ai-key").stat().st_mode & 0o777 == 0o600
    assert SECRET not in repr(resolve_project_settings(PROJECT))
    local = (await client.post("/api/settings/ai/profiles", json=OLLAMA)).json()
    assert not local["has_api_key"]
    init_database()  # Additive/idempotent schema initialization preserves saved settings.
    settings = (await client.get("/api/settings/ai")).json()
    assert len(settings["profiles"]) == 2
    assert settings["default_profile_id"] == cloud["id"]
    selected = (await client.get(f"/api/projects/{PROJECT}/ai-model")).json()
    assert selected == {"profile_id": None, "effective_profile": cloud, "thinking": False}
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": local["id"]})
    assert resolve_project_settings(PROJECT).provider == "ollama"
    assert resolve_project_settings(PROJECT).context_window == 16384
    assert (await client.delete(f"/api/settings/ai/profiles/{local['id']}")).status_code == 422
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": None})
    await client.put("/api/settings/ai/default", json={"profile_id": local["id"]})
    assert resolve_project_settings(PROJECT).model == "local-test"
    assert (await client.delete(f"/api/settings/ai/profiles/{cloud['id']}")).status_code == 204
    assert (await client.delete(f"/api/settings/ai/profiles/{local['id']}")).status_code == 204
    assert not resolve_project_settings(PROJECT).configured


@pytest.mark.anyio
async def test_project_thinking_persists_only_with_a_selected_profile(client):
    profile = (await client.post("/api/settings/ai/profiles", json=DEEPSEEK)).json()
    response = await client.put(
        f"/api/projects/{PROJECT}/ai-model",
        json={"profile_id": profile["id"], "thinking": True},
    )
    assert response.json()["thinking"] is True
    assert resolve_project_settings(PROJECT).thinking is True
    # Changing the model when thinking is not specified keeps the preference.
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": profile["id"]})
    assert (await client.get(f"/api/projects/{PROJECT}/ai-model")).json()["thinking"] is True
    # Returning to the shared default removes the project preference.
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": None})
    assert resolve_project_settings(PROJECT).thinking is False


@pytest.mark.anyio
async def test_thinking_migration_preserves_existing_project_profile(client):
    profile = (await client.post("/api/settings/ai/profiles", json=DEEPSEEK)).json()
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": profile["id"]})
    # Reproduce the previous schema with an existing project selection.
    with connection() as db:
        db.execute("ALTER TABLE project_ai_settings DROP COLUMN thinking_mode")
    init_database()
    init_database()
    selected = (await client.get(f"/api/projects/{PROJECT}/ai-model")).json()
    assert selected == {
        "profile_id": profile["id"], "effective_profile": profile, "thinking": False,
    }
    assert resolve_project_settings(PROJECT).api_key == SECRET
    with connection() as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


@pytest.mark.anyio
async def test_keep_replace_clear_and_redirect_protection(client):
    profile = (await client.post("/api/settings/ai/profiles", json=DEEPSEEK)).json()
    url = f"/api/settings/ai/profiles/{profile['id']}"
    payload = {**DEEPSEEK, "api_key": "", "model": "another-model"}
    assert (await client.put(url, json=payload)).status_code == 200
    assert resolve_project_settings(PROJECT).api_key == SECRET
    redirected = {**payload, "base_url": "https://another.test"}
    assert (await client.put(url, json=redirected)).status_code == 422
    assert (
        await client.post(
            "/api/settings/ai/check",
            json={
                **redirected,
                "profile_id": profile["id"],
            },
        )
    ).status_code == 422
    replacement = {**redirected, "api_key": "new-test-key"}
    assert (await client.put(url, json=replacement)).status_code == 200
    assert resolve_project_settings(PROJECT).api_key == "new-test-key"
    assert (await client.put(url, json={**replacement, "clear_api_key": True})).status_code == 422
    assert (await client.put(url, json={**OLLAMA, "clear_api_key": True})).status_code == 200
    assert resolve_project_settings(PROJECT).api_key is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "patch",
    [
        {"context_window": 0},
        {"base_url": "file:///etc/passwd"},
        {"base_url": f"https://user:{SECRET}@example.test"},
        {"provider": "invalid"},
        {"api_key": {"secret": SECRET}},
        {"extra": SECRET},
    ],
)
async def test_validation_does_not_echo_credentials(client, patch):
    response = await client.post("/api/settings/ai/profiles", json={**DEEPSEEK, **patch})
    assert response.status_code == 422
    assert SECRET not in response.text
    assert all("input" not in error for error in response.json()["detail"])


@pytest.mark.anyio
async def test_legacy_migrates_once_and_never_reappears_after_deletion(client, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", SECRET)
    import_legacy_configuration()
    import_legacy_configuration()
    profiles = (await client.get("/api/settings/ai")).json()["profiles"]
    assert len(profiles) == 1
    assert resolve_project_settings(PROJECT).api_key == SECRET
    await client.delete(f"/api/settings/ai/profiles/{profiles[0]['id']}")
    import_legacy_configuration()
    assert (await client.get("/api/settings/ai")).json()["profiles"] == []
    assert not resolve_project_settings(PROJECT).configured


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["deepseek", "ollama", "compatible"])
async def test_discovery_reuses_saved_key_without_generation(client, monkeypatch, provider):
    payload = (
        {**OLLAMA, "base_url": "http://192.0.2.10:11434"}
        if provider == "ollama"
        else {**DEEPSEEK, "provider": provider}
    )
    profile = (await client.post("/api/settings/ai/profiles", json=payload)).json()
    requests = []

    def handler(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.url.host == httpx.URL(payload["base_url"]).host
        assert request.url.port == httpx.URL(payload["base_url"]).port
        assert request.url.path == ("/api/tags" if provider == "ollama" else "/models")
        assert request.headers.get("Authorization") == (
            None if provider == "ollama" else f"Bearer {SECRET}"
        )
        return httpx.Response(
            200,
            json={"models": [{"name": "local-test", "capabilities": ["completion"]}]}
            if provider == "ollama"
            else {"data": [{"id": "remote-test"}]},
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original(
            transport=httpx.MockTransport(handler),
            **kwargs,
        ),
    )
    response = await client.post(
        "/api/settings/ai/check",
        json={
            **payload,
            "api_key": "",
            "profile_id": profile["id"],
        },
    )
    assert response.status_code == 200
    assert response.json()["models"] == [payload["model"]]
    assert len(requests) == 1
    assert SECRET not in response.text


@pytest.mark.anyio
@pytest.mark.parametrize("status_code", [401, 307])
async def test_discovery_does_not_follow_redirect_or_expose_provider_errors(
    client,
    monkeypatch,
    status_code,
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status_code, json={"error": SECRET}, headers={"Location": "https://another.test/models"}
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original(
            transport=httpx.MockTransport(handler),
            **kwargs,
        ),
    )
    response = await client.post("/api/settings/ai/check", json=DEEPSEEK)
    assert response.status_code == 502
    assert SECRET not in response.text
    assert len(requests) == 1


@pytest.mark.anyio
async def test_missing_encryption_key_is_reported_without_using_environment(client, monkeypatch):
    await client.post("/api/settings/ai/profiles", json=DEEPSEEK)
    get_db_path().with_suffix(".ai-key").unlink()
    monkeypatch.setenv("DEEPSEEK_API_KEY", "legacy-must-not-be-used")
    from app.generation import GenerationNotConfiguredError

    with pytest.raises(GenerationNotConfiguredError, match="backup"):
        with project_ai_context(PROJECT):
            pytest.fail("Missing credentials must fail before generation")
    response = await client.post("/api/settings/ai/profiles", json=DEEPSEEK)
    assert response.status_code == 422
    assert not get_db_path().with_suffix(".ai-key").exists()


@pytest.mark.anyio
async def test_concurrent_operations_pin_model_and_secret_across_updates(client):
    first = save_profile(ProfileInput(**DEEPSEEK))
    second = save_profile(ProfileInput(**OLLAMA))
    second_project = (
        await client.post(
            "/api/projects",
            json={
                "title": "Secondo progetto",
                "description": "Isolamento dei modelli",
            },
        )
    ).json()["id"]
    select_project_profile(second_project, second["id"])
    started, changed = asyncio.Event(), asyncio.Event()

    async def existing_compilation():
        with project_ai_context(PROJECT):
            initial = get_ai_settings()
            started.set()
            await changed.wait()
            assert get_ai_settings() is initial
            assert initial.model == "remote-test"
            assert initial.api_key == SECRET

    async def other_project():
        await started.wait()
        with project_ai_context(second_project):
            assert get_ai_settings().provider == "ollama"
            save_profile(ProfileInput(**{**DEEPSEEK, "api_key": "new-key"}), first["id"])
            select_project_profile(PROJECT, second["id"])
            changed.set()
            await asyncio.sleep(0)
            assert get_ai_settings().provider == "ollama"

    await asyncio.gather(existing_compilation(), other_project())
    assert resolve_project_settings(PROJECT).provider == "ollama"


@pytest.mark.anyio
@pytest.mark.parametrize("use_schema", [False, True])
@pytest.mark.parametrize(
    "provider",
    ["deepseek", "compatible", "ollama", "google", "mistral", "xai", "groq", "openrouter"],
)
async def test_provider_wire_format_and_usage(provider, use_schema):
    settings = AISettings(
        SECRET if provider != "ollama" else None,
        "test-model",
        "https://provider.test/v1",
        provider,
        context_window=65536,
    )
    messages = [
        {"role": "system", "content": "Restituisci JSON"},
        {"role": "user", "content": "Dati di prova"},
    ]
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}

    def handler(request):
        body = json.loads(request.content)
        assert body["messages"] == messages
        assert body["model"] == "test-model"
        if provider == "ollama":
            assert request.url == "https://provider.test/api/chat"
            assert "authorization" not in request.headers
            assert body["options"] == {"temperature": 0.1, "num_ctx": 65536, "num_predict": 1234}
            assert body["format"] == (schema if use_schema else "json")
            assert body["stream"] is False
            return httpx.Response(
                200,
                json={
                    "message": {"content": '{"ok":true}'},
                    "done": True,
                    "done_reason": "stop",
                    "prompt_eval_count": 10,
                    "eval_count": 4,
                },
            )
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["authorization"] == f"Bearer {SECRET}"
        assert ("thinking" in body) == (provider == "deepseek")
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"ok":true}'}, "finish_reason": "stop"}],
                "usage": {"total_tokens": 14},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        response = await post_chat(
            client,
            settings,
            {
                "model": settings.model,
                "messages": messages,
                "max_tokens": 1234,
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
            },
            response_schema=schema if use_schema else None,
        )
    assert response.json()["choices"][0]["message"]["content"] == '{"ok":true}'
    assert response.json()["usage"]["total_tokens"] == 14


@pytest.mark.anyio
@pytest.mark.parametrize("operation", ["chat", "facts", "draft"])
@pytest.mark.parametrize("provider", list(PROVIDERS))
async def test_selected_provider_routes_all_generation_paths(
    client, monkeypatch, operation, provider
):
    """Real routes, prompts, validators and persistence; only provider HTTP is simulated."""
    profile = {**(OLLAMA if provider == "ollama" else DEEPSEEK), "provider": provider}
    local = (await client.post("/api/settings/ai/profiles", json=profile)).json()
    await client.put(f"/api/projects/{PROJECT}/ai-model", json={"profile_id": local["id"]})
    await client.post(
        f"/api/projects/{PROJECT}/files",
        files={
            "file": (
                "avviso.txt",
                b"Requisito tecnico: iscrizione all'albo professionale.",
                "text/plain",
            ),
        },
    )
    await client.put(
        f"/api/projects/{PROJECT}/artifacts/{PROJECT}--template",
        json={
            "content": "# Modello\n\nRequisito: [TODO]",
        },
    )
    replies = {
        "chat": {"answer": "Occorre l'iscrizione all'albo professionale [1].", "citation_ids": [1]},
        "facts": {
            "facts": [
                {
                    "title": "Requisito",
                    "value": "iscrizione all'albo professionale",
                    "evidence_ids": [1],
                }
            ],
            "missing_information": [],
        },
        "draft": {
            "markdown": "# Bozza\n\n[TODO: confermare il requisito]",
            "used_fact_ids": [],
            "missing_information": ["Conferma requisito"],
        },
    }
    calls = []

    def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        assert body["model"] == profile["model"]
        content = json.dumps(
            {"action": "retrieve", "target": "source", "answer": "",
             "queries": ["Requisito tecnico"]}
            if operation == "chat" and len(calls) == 1 else replies[operation]
        )
        if provider == "ollama":
            assert request.url.path == "/api/chat"
            assert "authorization" not in request.headers
            data = {
                "done": True,
                "done_reason": "stop",
                "message": {"content": content},
                "prompt_eval_count": 100,
                "eval_count": 30,
            }
        elif provider == "openai":
            assert request.url.path == "/responses"
            assert body["store"] is False
            assert [item["role"] for item in body["input"]] == ["system", "user"]
            data = {
                "status": "completed",
                "output": [
                    {"type": "reasoning", "summary": []},
                    {"type": "message", "content": [{"type": "output_text", "text": content}]},
                ],
                "usage": {"total_tokens": 130},
            }
        elif provider == "anthropic":
            assert request.url.path == "/messages"
            assert request.headers["x-api-key"] == SECRET
            assert body["system"] and [item["role"] for item in body["messages"]] == ["user"]
            data = {
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": content}],
                "usage": {"input_tokens": 100, "output_tokens": 30},
            }
        else:
            assert request.url.path == "/chat/completions"
            assert request.headers["authorization"] == f"Bearer {SECRET}"
            assert [item["role"] for item in body["messages"]] == ["system", "user"]
            data = {
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"total_tokens": 130},
            }
        return httpx.Response(200, json={**data, "model": profile["model"]})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original(
            transport=httpx.MockTransport(handler),
            **kwargs,
        ),
    )
    if operation == "chat":
        response = await client.post(
            f"/api/projects/{PROJECT}/answer", json={"question": "Quale requisito tecnico?"}
        )
        assert response.json()["generation_status"] == "completed"
    else:
        path = "call-facts/extract" if operation == "facts" else "draft/generate"
        response = await client.post(f"/api/projects/{PROJECT}/{path}")
    assert response.status_code in {200, 201}, response.text
    assert len(calls) == (2 if operation == "chat" else 1)
    payload = response.json()
    assert payload["model"] == profile["model"]
    assert payload["total_tokens"] == (260 if operation == "chat" else 130)
