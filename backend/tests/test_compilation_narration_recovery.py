"""Candidate-only narrator recovery: simulated transport, real persistence and DOCX gates."""

import asyncio
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import pytest
from test_compilation_global_sessions import BASE, api, provider, resolve, start
from test_compilation_p3_hold_validation import FIRST, SECOND, SUMMARY, hold

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.db import connection, get_storage_path
from app.generation import GenerationError, GenerationTruncatedError

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def candidate(monkeypatch):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    monkeypatch.setenv("MAPI_NARRATION_RECOVERY_REVISION", "1")


def valid(context):
    return {"questions": [], "hold_groups": [],
            **({"message": SUMMARY} if context["conversation_stage"] == "initial" else {})}


class Narrator:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes) or [valid], []

    async def __call__(self, client, settings, body, timeout, **kwargs):
        self.calls.append(deepcopy(body))
        assert timeout == 45 and body["max_tokens"] == 2048
        ctx = json.loads(body["messages"][1]["content"])
        out = self.outcomes[min(len(self.calls), len(self.outcomes)) - 1]
        if isinstance(out, BaseException):
            raise out
        if callable(out):
            out = out(ctx)
        return out if isinstance(out, str) else json.dumps(out), "simulated", {
            "total_tokens": 100, "prompt_tokens": 80, "completion_tokens": 20,
            "completion_tokens_details": {"reasoning_tokens": 0}, "prompt_cache_hit_tokens": 30}


def install(monkeypatch, *outcomes):
    model = Narrator(*outcomes)
    monkeypatch.setattr(dialogue, "request_model_content", model)
    return model


def data_of(session):
    with connection() as db:
        row = sessions._row(db, "alpha", session["id"])
        return json.loads(row["state_json"])["global_compilation"]


def pending(session):
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"]["dialogue"].update(phase="PENDING", question=None,
                                                     resuming=True)
        return sessions.save_state(db, row, state, "test_narration_pending")


async def draft(api, session, ids=(), *, empty=False, users=()):
    return await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": session["version"], "candidate_ids": list(ids),
        "user_candidate_ids": list(users), "allow_unresolved": True,
        "allow_empty": empty, "user_quote": "Genera la bozza parziale"})


@pytest.mark.anyio
@pytest.mark.parametrize("error", ["json", "schema", "render", "provider", "timeout", "truncated"])
async def test_one_bounded_retry_keeps_same_analysis_and_accounts_for_usage(
    api, provider, monkeypatch, error,
):
    broken = {"json": '{"message":', "schema": {"message": SUMMARY, "hold_groups": [
        hold([], "Via del Sole 9")]}, "render": {"message": SUMMARY, "questions": [
            {"slot": 24, "question": "Qual è il dato?"}], "hold_groups": [
                hold([2], "Via del Sole 9")]},
        "provider": GenerationError("simulated unavailable"), "timeout": TimeoutError(),
        "truncated": GenerationTruncatedError(2048, 250)}[error]
    model = install(monkeypatch, broken, valid)
    session = await resolve(api, await start(api))
    result = session["global_compilation"]["dialogue"]
    recovery = result["narration_recovery"]
    assert recovery["mode"] == "completed" and recovery["retries"] == 1
    assert len(model.calls) == 2 and len(provider) == 1
    assert model.calls[0] == model.calls[1]  # No failed JSON inserted or repaired.
    assert not result.get("error") and not result.get("held_candidate_ids")
    assert len(dialogue.export_selection(session)[0]) == 2
    assert not session["last_generation"]
    if error in {"provider", "timeout"}:
        assert result["usage"] is None
    elif error == "truncated":
        assert result["usage"] == {"total_tokens": 350}
    else:
        assert result["usage"]["total_tokens"] == 200
        assert result["usage"]["prompt_cache_hit_tokens"] == 60
    assert all((get_storage_path() / data_of(session)["artifact_path"] / a["artifact_path"]
                / "request.json").is_file() for a in recovery["attempts"])


@pytest.mark.anyio
async def test_two_failures_offer_empty_draft_without_promoting_source_proposals(
    api, provider, monkeypatch,
):
    model = install(monkeypatch, '{"message":')
    session = await resolve(api, await start(api))
    result = session["global_compilation"]["dialogue"]
    assert len(model.calls) == 2 and len(provider) == 1
    assert result["narration_recovery"]["mode"] == "degraded"
    assert not result.get("error") and not session["chat"]["auto_continue"]
    assert result["empty_export_offered"] and not session["last_generation"]
    assert result["reviewed_candidate_fingerprints"] == {}
    assert set(result["narration_recovery"]["unreviewed_candidate_ids"]) == {FIRST, SECOND}
    assert dialogue.export_selection(session)[0] == []
    forced = await draft(api, session, [FIRST])
    assert forced.status_code == 409 and "non revisionata" in forced.json()["detail"]
    assert (await draft(api, session)).status_code == 422  # No implicit empty export either.
    exported = await draft(api, session, empty=True)
    assert exported.status_code == 200, exported.text


@pytest.mark.anyio
async def test_explicit_chat_export_works_after_fallback(api, provider, monkeypatch):
    from app.intents import ChatDecision

    install(monkeypatch, valid)
    session = await resolve(api, await start(api))
    install(monkeypatch, "invalid")
    session = await resolve(api, pending(session))
    text, command = await adapter.handle_chat_action(session, ChatDecision(
        action="compilation_generate", answer="", queries=[], target="form"),
        session["version"], "Genera la bozza incompleta")
    assert command["action"] == "generated" and text
    assert len(provider) == 1


@pytest.mark.anyio
async def test_fallback_preserves_v14_authorization_gate(api, provider, monkeypatch):
    from test_compilation_option_authorization import CLAUSE
    from test_compilation_sessions import docx, source

    upload = await api.post("/api/projects/alpha/forms", files={
        "file": ("modulo.docx", docx(context=CLAUSE))})
    await source(api, "Denominazione sociale: Aurora Servizi S.r.l.\nSede legale: Via del Sole 9")
    session = (await api.post(BASE, json={"form_id": upload.json()["id"], "engine": "global",
                                         "start_in_chat": True})).json()
    install(monkeypatch, valid)
    session = await resolve(api, session)
    assert len(data_of(session)["dialogue"]["reviewed_candidate_ids"]) == 2
    assert dialogue.export_selection(session)[0] == []
    install(monkeypatch, "invalid")
    session = await resolve(api, pending(session))
    assert session["global_compilation"]["dialogue"]["narration_recovery"]["mode"] == "degraded"
    assert dialogue.export_selection(session)[0] == []
    forced = await draft(api, session, [FIRST, SECOND])
    assert forced.status_code == 409 and "procedurale" in forced.json()["detail"]


@pytest.mark.anyio
async def test_fallback_keeps_old_holds_and_reviews_and_can_resume_without_new_analysis(
    api, provider, monkeypatch,
):
    install(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Via del Sole 9")]})
    session = await resolve(api, await start(api))
    before = data_of(session)
    session = pending(session)
    model = install(monkeypatch, "not JSON")
    session = await resolve(api, session)
    after = data_of(session)
    result = after["dialogue"]
    assert after["audit"] == before["audit"]
    for key in ("held_candidate_ids", "hold_records", "reviewed_candidate_fingerprints"):
        assert result[key] == before["dialogue"][key]
    assert dialogue.export_selection(session)[0] == [FIRST]
    assert result["usage"]["total_tokens"] == 200  # Never includes the previous turn's 100.
    assert len(model.calls) == 2 and len(provider) == 1
    assert (await draft(api, session, [FIRST, SECOND])).status_code == 409

    resumed = adapter.control_session("alpha", session["id"], session["version"], "resume")
    assert resumed["chat"]["auto_continue"]
    install(monkeypatch, valid)
    resumed = await resolve(api, resumed)
    assert len(provider) == 1  # No global analysis or segment regenerated.
    assert resumed["global_compilation"]["dialogue"]["narration_recovery"]["mode"] == "completed"
    assert dialogue.export_selection(resumed)[0] == [FIRST]  # Existing hold is still binding.
    exported = await draft(api, resumed, [FIRST])
    assert exported.status_code == 200, exported.text


@pytest.mark.anyio
async def test_fallback_drops_stale_review_and_preserves_user_decisions(api, provider, monkeypatch):
    install(monkeypatch, valid)
    session = await resolve(api, await start(api))
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        data = state["global_compilation"]
        d = data["dialogue"]
        d.update(phase="PENDING", question=None, resuming=True)
        d["reviewed_candidate_fingerprints"][FIRST] = "stale fingerprint"
        # A skip and an unverified USER value must survive but must not gain write authority.
        d["answers"] = {"condition:unresolved": {"action": "SKIP", "user_quote": "Rinvio",
                                                "provenance": "USER"}}
        d["user_values"] = {FIRST: {"value": "Altra società", "user_quote": "Altra società",
                                    "provenance": "USER", "label": "Denominazione sociale"}}
        saved = deepcopy(d)
        session = sessions.save_state(db, row, state, "test_stale_review")
    install(monkeypatch, "invalid")
    session = await resolve(api, session)
    result = session["global_compilation"]["dialogue"]
    assert result["answers"] == saved["answers"] and result["user_values"] == saved["user_values"]
    assert FIRST not in result["reviewed_candidate_fingerprints"]
    ids, _, users = dialogue.export_selection(session)
    assert ids == [SECOND] and not users
    assert (await draft(api, session, [FIRST])).status_code == 409
    assert (await draft(api, session, users=[FIRST])).status_code == 409


@pytest.mark.anyio
@pytest.mark.parametrize("stored", [False, True])
async def test_persisted_flag_is_authoritative_over_runtime_environment(
    api, provider, monkeypatch, stored,
):
    monkeypatch.setenv("MAPI_NARRATION_RECOVERY_REVISION", "1" if stored else "0")
    session = await start(api)
    monkeypatch.setenv("MAPI_NARRATION_RECOVERY_REVISION", "0" if stored else "1")
    model = install(monkeypatch, "invalid")
    session = await resolve(api, session)
    assert len(model.calls) == (2 if stored else 1)
    assert bool(session["global_compilation"]["dialogue"].get("error")) is not stored
    assert (session["global_compilation"].get("narration_recovery_revision") == 1) is stored


@pytest.mark.anyio
async def test_cancellation_is_not_a_fallback_or_an_export_authorization(
    api, provider, monkeypatch, tmp_path,
):
    install(monkeypatch, valid)
    session = await resolve(api, await start(api))
    data = data_of(session)
    before = deepcopy(data)
    model = install(monkeypatch, asyncio.CancelledError())
    with pytest.raises(asyncio.CancelledError):
        await dialogue.narrate(data, tmp_path)
    assert data == before and len(model.calls) == 1
    assert not list(tmp_path.glob("dialogue/recovery-*.json"))


@pytest.mark.anyio
async def test_minervino_recorded_invalid_response_in_an_empty_review_window(
    api, provider, monkeypatch,
):
    path = Path(__file__).resolve().parents[2] / (
        "backend/data/compilation-audit/sezioni-resilienti-20261022-01/e2e/minervino-2/"
        "artifacts/dialogue/2a80af27c9a142aab6aad88775182775/response.txt")
    if not path.is_file():
        pytest.skip("Risposta storica locale non disponibile")
    bad = path.read_text()
    with pytest.raises(ValueError):
        dialogue.GroupedContinuationPlan.model_validate_json(bad)
    install(monkeypatch, valid)
    session = await resolve(api, await start(api))
    model = install(monkeypatch, bad)
    session = await resolve(api, pending(session))
    for body in model.calls:
        ctx = json.loads(body["messages"][1]["content"])
        assert ctx["document_values"] == []
        schema = json.loads(body["messages"][0]["content"].split("SCHEMA OUTPUT:\n")[-1])
        assert schema["properties"]["hold_groups"]["maxItems"] == 0
    assert session["global_compilation"]["dialogue"]["narration_recovery"]["mode"] == "degraded"
    assert len(dialogue.export_selection(session)[0]) == 2
    assert (await draft(api, session, [FIRST, SECOND])).status_code == 200


@pytest.mark.anyio
async def test_recorded_minervino_state_keeps_only_current_old_reviews(
    provider, monkeypatch, tmp_path,
):
    root = Path(__file__).resolve().parents[2]
    state = root / (
        "benchmark ufficiale/sezioni-resilienti-20261022-01/trials/minervino-2/stato-finale.json")
    response = root / (
        "backend/data/compilation-audit/sezioni-resilienti-20261022-01/e2e/minervino-2/"
        "artifacts/dialogue/2a80af27c9a142aab6aad88775182775/response.txt")
    if not state.is_file() or not response.is_file():
        pytest.skip("Stato/risposta storici locali non disponibili")
    data = json.loads(state.read_text())["global_compilation"]
    assert data["dialogue"]["error"] == "ValidationError"
    assert len(data["dialogue"]["reviewed_candidate_fingerprints"]) == 63
    assert dialogue._review_window(data) == []
    data["narration_recovery_revision"] = 1  # Counterfactual in memory, not a migration.
    before = deepcopy(data)
    model = install(monkeypatch, response.read_text())
    result = await dialogue.narrate(data, tmp_path)
    assert len(model.calls) == 2 and data == before
    assert result["narration_recovery"]["mode"] == "degraded" and result["error"] is None
    assert result["answers"] == before["dialogue"]["answers"]
    assert result["held_candidate_ids"] == before["dialogue"]["held_candidate_ids"]
    assert result["reviewed_candidate_fingerprints"] == dialogue.reviewed_candidates(before)
    ids, _, _ = dialogue.export_selection({"global_compilation": {
        **data, "dialogue": result, "fields": adapter.review_fields(data)}})
    assert ids and set(ids) <= dialogue.narration_source_ids(before)


@pytest.mark.anyio
async def test_failure_of_later_review_window_does_not_approve_it(api, provider, monkeypatch):
    import test_compilation_resilient_segments as sections

    def all_values(inp, ids):
        return json.dumps(sections.envelope(inp, {cid: sections.slot(inp, cid) for cid in ids}))

    analysis = sections.Model({1: [all_values]})
    narrator = install(monkeypatch, valid, "invalid")
    session = await sections.started(api, monkeypatch, sections.form_docx(45), analysis)
    session = await resolve(api, session)
    assert session["chat"]["auto_continue"]
    assert len(data_of(session)["dialogue"]["reviewed_candidate_ids"]) == 40
    session = await resolve(api, session)
    result = session["global_compilation"]["dialogue"]
    assert len(narrator.calls) == 3 and len(analysis.calls) == 1
    assert result["narration_recovery"]["mode"] == "degraded"
    assert len(result["narration_recovery"]["unreviewed_candidate_ids"]) == 5
    ids, _, _ = dialogue.export_selection(session)
    assert len(ids) == 40
    rejected = result["narration_recovery"]["unreviewed_candidate_ids"][0]
    assert (await draft(api, session, [*ids, rejected])).status_code == 409
    assert (await draft(api, session, ids)).status_code == 200


@pytest.mark.anyio
async def test_refresh_lease_covers_both_attempts(api, provider, monkeypatch):
    install(monkeypatch, valid)
    session = await resolve(api, await start(api))
    session = pending(session)
    seen = []

    async def request(client, settings, body, timeout, **kwargs):
        with connection() as db:
            row = sessions._row(db, "alpha", session["id"])
            state = json.loads(row["state_json"])
            seen.append((datetime.fromisoformat(state["lease_until"])
                         - datetime.fromisoformat(row["updated_at"])).total_seconds())
        return json.dumps(valid(json.loads(body["messages"][1]["content"]))), "fake", {}

    monkeypatch.setattr(dialogue, "request_model_content", request)
    await resolve(api, session)
    assert 100 <= seen[0] <= 106
