"""Long USER messages: actual API/persistence and gates, simulated provider only."""

import json

import pytest
from pydantic import ValidationError
from test_compilation_global_dialogue import conditional
from test_compilation_global_sessions import api as api
from test_compilation_global_sessions import provider as provider
from test_compilation_global_sessions import resolve, start

from app import compilation_sessions, intents
from app.compilation_chat import ChatControl, ClarificationReply
from app.compilation_global_contract import UserFieldRequest
from app.db import connection
from app.generation import GenerationError
from app.schemas import MAX_QUESTION_LENGTH, QuestionRequest


@pytest.fixture
def anyio_backend():
    return "asyncio"


def long_message(size=3000):
    text = "  Confermo il ramo societario.\n" + "Contesto documentato da verificare. " * 130
    return text[:size - 2] + "\n "


def test_full_message_is_not_a_2000_character_extract_limit():
    message = long_message(MAX_QUESTION_LENGTH)
    assert len(message) == MAX_QUESTION_LENGTH
    assert QuestionRequest(question=message).question == message
    # StrictModel trims evidence excerpts; original request/history must not.
    parsed = ClarificationReply(slot=1, action="CONDITION_TRUE", user_quote=message)
    assert parsed.user_quote == message.strip()
    assert ChatControl(kind="pause", user_quote=message).user_quote == message.strip()


@pytest.mark.parametrize("action", ["VALUE", "CONDITION_TRUE", "UNKNOWN", "SKIP"])
def test_quote_above_request_limit_is_rejected_without_truncation(action):
    with pytest.raises(ValidationError):
        ClarificationReply(slot=1, action=action, value="Bari" if action == "VALUE" else None,
                           user_quote="Bari " + "a" * MAX_QUESTION_LENGTH)


def test_actual_unsupported_value_stays_unsupported_and_distinct_from_long_context():
    with pytest.raises(ValidationError):
        ClarificationReply(slot=1, action="VALUE", value="a" * 1501, user_quote="a" * 1501)


def test_historical_CRAA_failure_is_MODEL_metadata_not_USER_answer():
    from pathlib import Path

    original = Path(__file__).parent / "fixtures/long-user-v1/craa-diagnosis.json"
    rejected = json.loads(original.read_text())["clarifications"]["p5.s0"]
    assert len(rejected["proposal"]["reason"]) == 225
    with pytest.raises(ValidationError, match="200 characters"):
        UserFieldRequest.model_validate(rejected["proposal"])


def router(monkeypatch, message, *, check="SUPPORTED", failed=False, reply=None):
    requests = []

    async def request(client, settings, body, timeout, **kwargs):
        requests.append(body)
        if failed:
            raise GenerationError("Provider simulato non disponibile")
        if kwargs["response_schema"]["title"] == "ReplyScopeChecks":
            guard = json.loads(body["messages"][1]["content"])
            assert guard["message"] == message
            raw = {"checks": [{"slot": 1, "result": check}]}
        else:
            assert body["messages"][1]["content"].endswith(message)
            raw = {"intent": "answer_fields", "answer": "", "queries": [], "target": "form",
                   "replies": [reply or {"slot": 1, "action": "CONDITION_TRUE",
                                         "user_quote": message}]}
        return json.dumps(raw), "simulated", {"total_tokens": 10}

    monkeypatch.setattr(intents, "request_model_content", request)
    return requests


async def say(api, s, message):
    return await api.post("/api/projects/alpha/answer", json={
        "question": message, "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"],
    })


@pytest.mark.anyio
@pytest.mark.parametrize("size", [2000, 2001, 3999, 4000])
async def test_long_valid_decision_is_checked_persisted_and_kept_separate_from_SOURCE(
    api, provider, monkeypatch, size,
):
    s = await conditional(api, monkeypatch)
    message = long_message(size)
    calls = router(monkeypatch, message)
    response = await say(api, s, message)
    assert response.status_code == 200, response.text
    assert response.json()["question"] == message
    current = compilation_sessions.get_session("alpha", s["id"])
    receipt = current["global_compilation"]["dialogue"]["answers"]["condition:c"]
    assert receipt["user_quote"] == message.strip() and receipt["applies"] is True
    assert receipt["provenance"] == "USER"
    assert current["global_compilation"]["dialogue"]["user_values"] == {}
    history = (await api.get(f"/api/projects/alpha/conversations/{s['conversation_id']}")).json()
    assert history["turns"][-1]["question"] == message
    with connection() as db:
        row = db.execute("SELECT question FROM conversation_turns WHERE id=?",
                         (response.json()["turn_id"],)).fetchone()
        assert row["question"] == message
    assert len(calls) == 2  # One router plus independent relevance verifier; no global rerun.
    for old, new in zip(s["global_compilation"]["fields"],
                        current["global_compilation"]["fields"], strict=True):
        assert new.get("proposed_value", new.get("value")) == old.get(
            "proposed_value", old.get("value"))
        assert new.get("source_evidence") == old.get("source_evidence")


@pytest.mark.anyio
@pytest.mark.parametrize("check", ["UNRELATED", "AMBIGUOUS"])
async def test_long_unrelated_or_ambiguous_indication_is_retained_but_never_accepted(
    api, provider, monkeypatch, check,
):
    s = await conditional(api, monkeypatch)
    message = long_message()
    router(monkeypatch, message, check=check)
    response = await say(api, s, message)
    assert response.status_code == 200 and response.json()["question"] == message
    current = compilation_sessions.get_session("alpha", s["id"])
    assert current["global_compilation"]["dialogue"].get("answers", {}) == {}
    assert current == s


@pytest.mark.anyio
async def test_provider_error_preserves_original_in_server_history_and_no_false_receipts(
    api, provider, monkeypatch,
):
    s = await conditional(api, monkeypatch)
    message = long_message()
    router(monkeypatch, message, failed=True)
    response = await say(api, s, message)
    assert response.status_code == 200 and response.json()["generation_status"] == "failed"
    assert response.json()["question"] == message
    current = compilation_sessions.get_session("alpha", s["id"])
    assert current == s
    history = (await api.get(f"/api/projects/alpha/conversations/{s['conversation_id']}")).json()
    assert history["turns"][-1]["question"] == message


@pytest.mark.anyio
async def test_oversized_request_is_explicitly_rejected_and_never_partially_written(
    api, provider, monkeypatch,
):
    s = await conditional(api, monkeypatch)
    calls = router(monkeypatch, "not sent")
    response = await say(api, s, long_message(4000) + "x")
    assert response.status_code == 422
    assert not calls
    assert compilation_sessions.get_session("alpha", s["id"]) == s


@pytest.mark.anyio
async def test_fabricated_quote_in_long_message_cannot_authorize_a_condition(
    api, provider, monkeypatch,
):
    s = await conditional(api, monkeypatch)
    message = long_message()
    router(monkeypatch, message, reply={"slot": 1, "action": "CONDITION_TRUE",
                                      "user_quote": "Sono una persona non citata."})
    response = await say(api, s, message)
    assert response.status_code == 200
    current = compilation_sessions.get_session("alpha", s["id"])
    assert current["global_compilation"]["dialogue"].get("answers", {}) == {}
    assert response.json()["question"] == message


async def value_checkpoint(api):
    s = await resolve(api, await start(api))
    with connection() as db:
        row = compilation_sessions._row(db, "alpha", s["id"])
        state = json.loads(row["state_json"])
        slot = {"slot": 1, "kind": "value", "key": "field:t0.r1.c1", "label": "Sede legale",
                "field_ids": ["t0.r1.c1"], "condition": "", "context": "Sede legale"}
        state["global_compilation"]["dialogue"]["question"] = {
            "kind": "clarifications", "slots": [slot], "message": "Quale sede legale devo usare?",
            "field_ids": [],
        }
        return compilation_sessions.save_state(db, row, state, "fixture_value_checkpoint")


@pytest.mark.anyio
@pytest.mark.parametrize("case", ["valid", "different_subject", "fabricated", "too_long"])
async def test_long_message_does_not_weaken_value_scope_and_literal_validation(
    api, provider, monkeypatch, case,
):
    s = await value_checkpoint(api)
    value = "a" * 1501 if case == "too_long" else "Via della Luna 8"
    message = f"  La sede legale è {value}.\n" + long_message(2100)
    if case == "different_subject":
        message = message.replace("La sede legale", "La residenza personale di Anna Bianchi")
    if case == "fabricated":
        message = message.replace(value, "Via del Sole 12")
    router(monkeypatch, message, check="UNRELATED" if case == "different_subject" else "SUPPORTED",
           reply={"slot": 1, "action": "VALUE", "value": value, "user_quote": message})
    response = await say(api, s, message)
    assert response.status_code == 200 and response.json()["question"] == message
    current = compilation_sessions.get_session("alpha", s["id"])
    user_values = current["global_compilation"]["dialogue"].get("user_values", {})
    if case == "valid":
        assert user_values["t0.r1.c1"]["value"] == value
        assert user_values["t0.r1.c1"]["user_quote"] == message.strip()
        assert user_values["t0.r1.c1"]["provenance"] == "USER"
        current = await resolve(api, current)
        from app.compilation_global_dialogue import export_selection

        ids, conditions, user_ids = export_selection(current)
        export = await api.post(f"/api/projects/alpha/compilation-sessions/{s['id']}/global-draft",
                               json={"version": current["version"], "candidate_ids": ids,
                                     "user_candidate_ids": user_ids,
                                     "confirmed_condition_ids": conditions,
                                     "allow_unresolved": True})
        assert export.status_code == 200, export.text
        report = (await api.get(export.json()["last_generation"]["downloads"]["report"])).json()
        assert [f["provenance"] for f in report["fields"]] == ["SOURCE", "USER"]
        assert report["fields"][1]["written_value"] == value
        assert not report["fields"][1]["source_evidence"]
    else:
        assert not user_values
    history = (await api.get(f"/api/projects/alpha/conversations/{s['conversation_id']}")).json()
    assert history["turns"][-1]["question"] == message
