"""Replies written together with a request for the draft are recorded before it.

Manual Minervino test 4 (29 Oct): «1. Scelgo l'opzione 4 … 4. Rinvio … Genera ora la bozza
parziale» was routed as a draft request; the routing contract discarded the replies, so the
explicit choice never reached the DOCX and nothing told the USER. Provider outputs simulated.
"""

import json

import pytest
import test_compilation_resilient_segments as rev2
from pydantic import ValidationError
from test_compilation_clarifications import reply
from test_compilation_global_sessions import api, provider
from test_unified_routing import turn

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app import intents
from app.compilation_chat import ClarificationDecision
from app.db import connection
from app.intents import bind_turn_plan, parse_turn_plan

__all__ = ["api", "provider"]
MESSAGE = "1. Il codice è XYZ.\n\nGenera ora la bozza parziale con i dati verificati."


@pytest.fixture(autouse=True)
def candidate_runtime(monkeypatch):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    monkeypatch.setenv("MAPI_DERIVATION_REVISION", "1")


@pytest.mark.parametrize("intent", ["finish", "generate"])
def test_a_draft_request_may_carry_the_replies_of_the_same_message(intent):
    plan = parse_turn_plan(turn(intent, replies=[reply(1, value="XYZ")]), {1})
    decision = bind_turn_plan(plan, {"enabled": True, "engine": "global"}, MESSAGE)
    assert isinstance(decision, ClarificationDecision) and decision.then_finish
    assert [r.value for r in decision.replies] == ["XYZ"]
    with pytest.raises(ValueError):  # The legacy engine keeps its separate turns.
        bind_turn_plan(plan, {"enabled": True, "engine": "legacy"}, MESSAGE)


@pytest.mark.parametrize("intent", ["pause", "resume", "compile"])
def test_pause_and_resume_still_never_record_values(intent):
    with pytest.raises(ValidationError):
        parse_turn_plan(turn(intent, replies=[reply(1, value="XYZ")]), {1})


async def question_session(api, monkeypatch):
    session = await rev2.started(api, monkeypatch, rev2.form_docx(3), rev2.Model())
    response = await rev2.analyze(api, session)
    assert response.status_code == 200, response.text
    session = response.json()
    q = {"slot": 1, "key": "field:p0.s0", "kind": "value", "field_ids": ["p0.s0"],
         "label": "Codice", "condition": "", "question": "Qual è il codice?"}
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"]["dialogue"].update(
            phase="READY", error=None, question={
                "kind": "clarifications", "message": q["question"], "field_ids": [],
                "slots": [q]})
        return sessions.save_state(db, row, state, "test_question")


def simulate(monkeypatch, verdict):
    calls = []

    async def model(client, settings, body, timeout, **kwargs):
        title = kwargs["response_schema"]["title"]
        calls.append(title)
        if title in {"ReplyScopeChecks", "FormScopeChecks"}:
            return json.dumps({"checks": [{"slot": 1, "result": verdict,
                                           "scope_result": verdict}]}), "fake", {}
        return json.dumps(turn("finish", replies=[{
            "slot": 1, "action": "VALUE", "value": "XYZ", "normalized_value": None,
            "selected_options": None, "user_quote": "Il codice è XYZ"}])), "fake", {}

    async def narrator(client, settings, body, timeout, **kwargs):
        calls.append("narrator")
        return json.dumps({"questions": [], "hold_groups": []}), "fake", {}

    monkeypatch.setattr(intents, "request_model_content", model)
    monkeypatch.setattr(dialogue, "request_model_content", narrator)
    monkeypatch.setattr(dialogue, "get_ai_settings", adapter.get_ai_settings)
    return calls


async def ask(api, session):
    return await api.post("/api/projects/alpha/answer", json={
        "question": MESSAGE, "conversation_id": session["conversation_id"],
        "compilation_session_id": session["id"], "compilation_version": session["version"]})


def drafts():
    with connection() as db:
        return [json.loads(r[0]) for r in db.execute(
            "SELECT report_json FROM document_compilations ORDER BY created_at")]


@pytest.mark.anyio
async def test_the_reply_is_recorded_and_then_the_draft_contains_it(api, provider, monkeypatch):
    session = await question_session(api, monkeypatch)
    simulate(monkeypatch, "SUPPORTED")
    response = await ask(api, session)
    assert response.status_code == 200, response.text
    assert response.json()["compilation"]["action"] == "generated"
    [report] = drafts()
    written = {f["cell_id"]: f.get("written_value") for f in report["fields"]}
    assert written["p0.s0"] == "XYZ"
    assert "Ho registrato" in response.json()["answer"]


@pytest.mark.anyio
async def test_a_refused_reply_stops_the_draft_and_says_why(api, provider, monkeypatch):
    session = await question_session(api, monkeypatch)
    simulate(monkeypatch, "AMBIGUOUS")
    response = await ask(api, session)
    assert response.status_code == 200, response.text
    assert response.json()["compilation"] is None or response.json()["compilation"].get(
        "action") != "generated"
    assert not drafts()
    assert "Non ho ancora generato la bozza" in response.json()["answer"]
