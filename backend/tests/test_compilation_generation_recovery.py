"""Export consent failures are observable and retry the same immutable proposal."""

import asyncio
import json

import httpx
import pytest
from test_compilation_global_sessions import BASE, resolve, start
from test_compilation_global_sessions import api as api
from test_compilation_global_sessions import provider as provider

from app import intents, main
from app.compilation_routing_trace import RoutingTrace
from app.db import get_storage_path
from app.generation import GenerationError


@pytest.fixture
def anyio_backend():
    return "asyncio"


def consent_payload(session, message="si"):
    return {"question": message, "document_id": session["form_id"],
            "conversation_id": session["conversation_id"],
            "compilation_session_id": session["id"], "compilation_version": session["version"]}


def traces(session):
    root = get_storage_path() / session["global_compilation"]["artifact_path"] / "routing"
    return [json.loads(p.read_text()) for p in root.glob("*/trace.json")]


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["schema", "provider", "timeout", "untrusted_error"])
async def test_failed_consent_preserves_checkpoint_and_next_consent_generates(
    api, provider, monkeypatch, failure,
):
    session = await resolve(api, await start(api))
    assert session["chat"]["question"]["kind"] == "generate"
    calls = []

    async def failing(client, settings, body, timeout, **kwargs):
        calls.append(body)
        if failure == "schema":
            # A selected form ID is not allowed on a generation command. Reject it,
            # record both attempts, and never relax the schema to force an export.
            return json.dumps({"intent": "generate", "answer": "", "queries": [],
                "target": "form", "form_id": session["form_id"]}), "simulated", {}
        if failure == "timeout":
            await asyncio.sleep(1)
        if failure == "untrusted_error":
            raise GenerationError("Traceback: errore tecnico riservato test-secret")
        response = httpx.Response(503, text="Temporary outage test-secret",
                                  request=httpx.Request("POST", "https://provider.invalid"))
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GenerationError("Il servizio AI ha rifiutato la richiesta (503)") from exc

    monkeypatch.setattr(intents, "request_model_content", failing)
    if failure == "timeout":
        monkeypatch.setattr(main, "chat_timeout_seconds", lambda: 0.05)
    response = await api.post("/api/projects/alpha/answer", json=consent_payload(session))
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["generation_status"] == "failed"
    assert "interpretare" in result["answer"] and "richiesta di bozza resta aperta" in (
        result["answer"])
    assert result["notice"] and result["notice"] in result["answer"]
    assert "Traceback" not in json.dumps(result)
    assert "test-secret" not in json.dumps(result)
    assert "esportare una bozza parziale" not in result["answer"]
    assert (await api.get(f"{BASE}/{session['id']}")).json() == session
    assert (await api.get("/api/projects/alpha/document-compilations")).json() == []
    recorded, = traces(session)
    assert len(recorded["attempts"]) == len(calls) == (2 if failure == "schema" else 1)
    assert recorded["result"]["stage"] == "routing"
    assert recorded["result"]["status"] == "failed"
    if failure == "schema":
        for attempt in recorded["attempts"]:
            assert attempt["raw"] and attempt["schema"]["title"] == "TurnPlan"
            assert "Solo compile" in attempt["validation_error"]
        assert "Errori di validazione" in recorded["attempts"][1]["request"][
            "messages"][-1]["content"]
    if failure == "provider":
        assert recorded["result"]["http_status"] == 503
        assert "[REDACTED]" in recorded["result"]["http_response"]
    assert "test-secret" not in json.dumps(recorded)

    async def valid(client, settings, body, timeout, **kwargs):
        return json.dumps({"intent": "generate", "answer": "", "queries": [],
                           "target": "form"}), "simulated", {}

    monkeypatch.setattr(intents, "request_model_content", valid)
    monkeypatch.setattr(main, "chat_timeout_seconds", lambda: 30)
    retry = await api.post("/api/projects/alpha/answer", json=consent_payload(session,
                                                                          "ok sì va bene"))
    assert retry.status_code == 200, retry.text
    assert retry.json()["compilation"] == {"session_id": session["id"], "action": "generated"}
    after = (await api.get(f"{BASE}/{session['id']}")).json()
    assert after["status"] == "GENERATED" and after["version"] == session["version"] + 1
    assert after["global_compilation"]["fields"] == session["global_compilation"]["fields"]
    assert after["template_sha256"] == session["template_sha256"]
    report = (await api.get(after["last_generation"]["downloads"]["report"])).json()
    assert report["written_field_count"] == 2
    assert all(f["provenance"] == "SOURCE" for f in report["fields"])
    assert len(provider) == 1  # No second document analysis, no new source values.
    assert any(t["result"] == {"status": "routed", "intent": "generate"}
               for t in traces(session))


@pytest.mark.anyio
async def test_failed_http_response_is_captured_without_headers_or_credentials(
    api, provider, monkeypatch,
):
    session = await resolve(api, await start(api))
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(
        transport=httpx.MockTransport(lambda request: httpx.Response(
            503, text="outage test-secret", request=request)), **kwargs))
    response = await api.post("/api/projects/alpha/answer", json=consent_payload(session))
    assert response.status_code == 200 and response.json()["generation_status"] == "failed"
    assert "(503)" in response.json()["answer"]
    recorded, = traces(session)
    attempt, = recorded["attempts"]
    assert attempt["http_status"] == 503
    assert attempt["http_response"] == "outage [REDACTED]"
    assert "authorization" not in json.dumps(recorded).casefold()
    assert "test-secret" not in json.dumps(recorded)
    assert (await api.get(f"{BASE}/{session['id']}")).json() == session


@pytest.mark.anyio
async def test_trace_storage_failure_does_not_block_valid_generation(
    api, provider, monkeypatch, tmp_path,
):
    session = await resolve(api, await start(api))

    async def route(client, settings, body, timeout, **kwargs):
        return json.dumps({"intent": "generate", "answer": "", "queries": [],
                           "target": "form"}), "simulated", {}

    # Only diagnostic storage fails; renderer/output storage remains available.
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("blocked")
    monkeypatch.setattr(intents, "request_model_content", route)
    monkeypatch.setattr(RoutingTrace, "for_session",
                        lambda _: RoutingTrace(blocked / "nested", "test-secret"))
    response = await api.post("/api/projects/alpha/answer", json=consent_payload(session))
    assert response.status_code == 200, response.text
    assert response.json()["compilation"]["action"] == "generated"


@pytest.mark.parametrize("relative", ["../../outside", "/tmp/outside"])
def test_trace_rejects_artifact_path_outside_storage(tmp_path, monkeypatch, relative):
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    assert RoutingTrace.for_session({"engine": "global", "global_compilation": {
        "artifact_path": relative}}) is None
