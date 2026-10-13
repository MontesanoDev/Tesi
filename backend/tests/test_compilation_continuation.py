"""Dialogue receipts and stable targets, isolated persistence and simulated providers."""

import json
import random

import pytest
from test_compilation_global_sessions import api as global_api
from test_compilation_global_sessions import provider as global_provider
from test_compilation_global_sessions import resolve, start
from test_compilation_user_requests import local_request_session

from app import compilation_chat
from app import compilation_global_dialogue as dialogue
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationDecision, ClarificationReply
from app.db import connection
from app.repository import get_conversation, save_conversation_turn

api, provider = global_api, global_provider


@pytest.fixture
def anyio_backend():
    return "asyncio"


def pool(kind="applicability"):
    return [{"slot": 1, "kind": kind, "key": "condition:generic", "label": "Partecipazione",
             "field_ids": ["p1.s0", "p2.s0"], "condition": "Se partecipa come ente",
             "context": "Se partecipa come ente", "alternatives": [], "impact": 2}]


def test_boolean_question_is_rendered_from_a_declarative_confirmation():
    plan = dialogue.DialoguePlan(message="Ho registrato la tua indicazione.", questions=[
        {"slot": 1, "confirmation": "la domanda riguarda l'ente indicato nelle fonti"}])
    result = dialogue.render_dialogue(plan, pool(), follow_up=True)
    assert result["question"]["slots"][0]["question"] == (
        "Confermi che la domanda riguarda l'ente indicato nelle fonti?")
    assert result["question"]["slots"][0]["field_ids"] == ["p1.s0", "p2.s0"]
    assert "dati collegati" not in result["message"]


@pytest.mark.parametrize("kind,proposal", [
    ("value", {"confirmation": "si vuole indicare questo dato"}),
    ("applicability", {"confirmation": "quale alternativa?"}),
    ("applicability", {"confirmation": "il campo p1.s0 si applica"}),
    ("applicability", {}),
])
def test_invalid_question_never_changes_its_backend_target(kind, proposal):
    with pytest.raises(ValueError):
        dialogue.render_dialogue(dialogue.DialoguePlan(message="Ho conservato le indicazioni.",
            questions=[{"slot": 1, **proposal}]), pool(kind))


@pytest.mark.parametrize("seed", range(8))
def test_fuzzed_dialogue_questions_fail_safely_or_keep_the_same_target(seed):
    rng = random.Random(seed)
    for _ in range(40):
        raw = {"message": "Conservo le indicazioni ricevute.", "questions": [{
            "slot": rng.choice([1, 99, None, "1", []]),
            "question": rng.choice([None, 42, "Qual è il dato?", "campo p1.s0?", "🧪🧪🧪🧪"]),
            "confirmation": rng.choice([None, 42, "il caso riguarda questo ente",
                                         "quale caso?", "il campo p1.s0 si applica", "\ud800"])}]}
        try:
            result = dialogue.render_dialogue(
                dialogue.DialoguePlan.model_validate_json(json.dumps(raw)), pool())
        except ValueError:
            continue
        assert result["question"]["slots"][0]["field_ids"] == ["p1.s0", "p2.s0"]


def turn(s, action, text):
    return save_conversation_turn(s["conversation_id"], {"question": "Messaggio utente",
        "answer": text, "generation_status": "direct", "compilation": {
            "session_id": s["id"], "action": action}})


def stored_data(s):
    with connection() as db:
        return json.loads(sessions._row(db, "alpha", s["id"])["state_json"])[
            "global_compilation"]


@pytest.mark.anyio
async def test_final_initial_message_replaces_only_its_own_provisional_receipt(api, provider):
    s = await start(api)
    turn(s, "start", "Ricevuta provvisoria")
    s = await resolve(api, s)
    saved = get_conversation("alpha", s["conversation_id"])["turns"]
    assert saved[-1]["answer"] == s["global_compilation"]["dialogue"]["message"]
    assert "Ricevuta provvisoria" not in saved[-1]["answer"]


@pytest.mark.anyio
@pytest.mark.parametrize("other", ["ordinary_turn", "other_session"])
async def test_completion_does_not_replace_a_later_unrelated_turn(api, provider, other):
    s = await start(api)
    turn(s, "start", "Ricevuta provvisoria")
    if other == "ordinary_turn":
        save_conversation_turn(s["conversation_id"], {"question": "Altra domanda",
            "answer": "Risposta ordinaria", "generation_status": "completed"})
    else:
        turn({**s, "id": "another-session"}, "start", "Risposta ordinaria")
    await resolve(api, s)
    assert get_conversation("alpha", s["conversation_id"])["turns"][-1][
        "answer"] == "Risposta ordinaria"


@pytest.mark.anyio
async def test_follow_up_has_only_latest_receipt_and_keeps_source_proofs(
    api, provider, monkeypatch,
):
    s = await local_request_session(api, monkeypatch, conditional=True)
    original_fields = s["global_compilation"]["fields"][:2]
    s, errors = dialogue.apply_replies("alpha", s["id"], s["version"], [
        ClarificationReply(slot=1, action="CONDITION_TRUE", user_quote="confermo il primo punto"),
        ClarificationReply(slot=2, action="SKIP", user_quote="la carica lasciala vuota")],
        "confermo il primo punto, la carica lasciala vuota")
    assert not errors
    context = dialogue.model_context(stored_data(s), dialogue.question_pool(stored_data(s)))
    assert context["conversation_stage"] == "follow_up"
    assert [r["action"] for r in context["latest_turn"]["accepted"]] == ["CONDITION_TRUE", "SKIP"]
    assert context["latest_turn"]["unaccepted"] == []
    assert "t0.r" not in json.dumps(context["latest_turn"])
    assert len(context["document_values"]) == 2
    turn(s, "updated", "Ho registrato le indicazioni univoche.")

    async def summarize(*args, **kwargs):
        body = args[2]
        assert "message" not in kwargs["response_schema"]["properties"]
        assert '"document_values"' in body["messages"][1]["content"]
        return json.dumps({"questions": []}), "simulated", {}

    monkeypatch.setattr(dialogue, "request_model_content", summarize)
    s = await resolve(api, s)
    saved = get_conversation("alpha", s["conversation_id"])["turns"][-1]["answer"]
    assert saved == s["global_compilation"]["dialogue"]["message"]
    assert saved.startswith("Ho registrato le tue conferme.") and "Ho trovato" not in saved
    assert "Lascio in bianco" in saved
    assert dialogue.question_pool(stored_data(s)) == []
    assert dialogue.export_selection(s)[0] == ["t0.r0.c1", "t0.r1.c1"]
    assert all(a["source_evidence"] == b["source_evidence"]
               for a, b in zip(original_fields, s["global_compilation"]["fields"][:2], strict=True))
    assert sessions.get_session("alpha", s["id"]) == s


@pytest.mark.anyio
async def test_partial_updates_continue_and_report_only_unaccepted_parts(
    api, provider, monkeypatch,
):
    s = await local_request_session(api, monkeypatch, conditional=True)
    decision = ClarificationDecision(action="ANSWER", replies=[
        ClarificationReply(slot=1, action="VALUE", value="Altro", user_quote="Altro"),
        ClarificationReply(slot=2, action="SKIP", user_quote="salta la carica")])
    _, command = await compilation_chat.handle_group_decision("alpha", s["conversation_id"],
        decision, s, "Altro; salta la carica", s["version"])
    assert command["action"] == "updated"
    s = sessions.get_session("alpha", s["id"])
    receipt = s["global_compilation"]["dialogue"]["latest_turn"]
    assert [r["action"] for r in receipt["accepted"]] == ["SKIP"]
    assert len(receipt["unaccepted"]) == 1 and receipt["unaccepted"][0]["kind"] == "applicability"
    assert s["chat"]["auto_continue"]
    assert "condition:c" not in s["global_compilation"]["dialogue"]["answers"]
    assert not s["global_compilation"]["dialogue"]["user_values"]


def test_continuation_schema_has_no_inventory_message_or_new_values():
    schema = dialogue.ContinuationPlan.model_json_schema()
    assert set(schema["properties"]) == {"questions", "held_proposal_slots"}
    with pytest.raises(ValueError):
        dialogue.ContinuationPlan.model_validate({"message": "Ecco tutti i dati..."})


def test_narration_schema_and_validator_bind_closed_questions_to_boolean_slots():
    items = pool() + [{**pool("value")[0], "slot": 2}]
    schema = dialogue.narration_schema(dialogue.ContinuationPlan, items)
    branches = schema["$defs"]["DialogueQuestion"]["oneOf"]
    assert branches[0]["properties"]["slot"]["enum"] == [1]
    assert branches[0]["required"] == ["slot", "confirmation"]
    assert branches[1]["properties"]["slot"]["enum"] == [2]
    assert branches[1]["required"] == ["slot", "question"]
    plan = dialogue.DialoguePlan(message="Conservo la tua indicazione.", questions=[
        {"slot": 1, "question": "Con quale qualità partecipi?"}])
    with pytest.raises(ValueError, match="proposizione chiusa"):
        dialogue.render_dialogue(plan, items, require_confirmation=True)
    assert dialogue.narration_schema(dialogue.ContinuationPlan, [])["properties"][
        "questions"]["maxItems"] == 0


@pytest.mark.parametrize("actions,expected", [
    (["VALUE"], "Ho aggiornato i dati che hai fornito."),
    (["CONDITION_FALSE"], "Ho registrato le tue conferme."),
    (["UNKNOWN"], "Lascio in bianco i punti che hai rinviato."),
    (["SKIP", "CONDITION_TRUE"], "Ho registrato le tue conferme. Lascio in bianco"),
    ([], "Riprendiamo dal punto rimasto aperto."),
])
def test_receipt_uses_only_recorded_actions_without_source_inventory(actions, expected):
    saved = {"latest_turn": {"accepted": [{"action": a, "label": "Motivo tecnico lungo",
        "value": "Valore da non ripetere"} for a in actions], "unaccepted": []}}
    receipt = dialogue.continuation_receipt(saved)
    assert receipt.startswith(expected)
    assert "Valore da non ripetere" not in receipt and "Motivo tecnico" not in receipt


@pytest.mark.anyio
async def test_explicit_resume_refreshes_only_older_questions_not_source_analysis(
    api, provider, monkeypatch,
):
    from app.compilation_global_sessions import control_session

    s = await local_request_session(api, monkeypatch, conditional=True)
    fields = s["global_compilation"]["fields"]
    with connection() as db:
        row = sessions._row(db, "alpha", s["id"])
        state = json.loads(row["state_json"])
        state["global_compilation"]["dialogue"].pop("presentation_version", None)
        s = sessions.save_state(db, row, state, "fixture_older_question")
    s = control_session("alpha", s["id"], s["version"], "resume")
    assert s["chat"]["auto_continue"]
    s = await resolve(api, s)
    assert len(provider) == 0
    assert s["global_compilation"]["fields"] == fields
    assert s["global_compilation"]["dialogue"]["message"].startswith("Riprendiamo")
    question = s["chat"]["question"]
    s = control_session("alpha", s["id"], s["version"], "pause")
    s = control_session("alpha", s["id"], s["version"], "resume")
    assert not s["chat"]["auto_continue"] and s["chat"]["question"] == question
