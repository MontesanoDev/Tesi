"""One provider contract, with read-only and session-write boundaries."""

import copy
import json

import pytest
from pydantic import ValidationError
from test_compilation_clarifications import checkpoint, reply
from test_compilation_controls import current
from test_compilation_conversation import anyio_backend as anyio_backend
from test_compilation_conversation import chat as chat
from test_compilation_conversation import say

from app.compilation_chat import ActiveFieldDecision, ClarificationDecision
from app.intents import ChatDecision, TurnPlan, parse_turn_plan, plan_chat_turn, routing_context


def turn(intent, **extra):
    return {"intent": intent, "answer": "", "queries": [], "target": "form", **extra}


def contexts():
    field = {"id": "private-field", "label": "Recapito", "context": "x" * 2000}
    single = {
        "enabled": True, "status": "WAITING_FOR_USER", "paused": False,
        "paused_by_user": False, "session_id": "private-session", "version": 7,
        "question": {"kind": "value", "message": "Quale recapito devo usare?",
                     "field_ids": [field["id"]]}, "fields": [field],
    }
    group = copy.deepcopy(single)
    group["question"] = {
        "kind": "clarifications", "message": "1. Quale recapito? 2. Quale referente?",
        "field_ids": [field["id"], "private-other"], "slots": [
            {**field, "kind": "value", "slot": 1, "field_ids": [field["id"]]},
            {"slot": 2, "kind": "value", "label": "Referente", "field_ids": ["private-other"]},
        ],
    }
    paused = {**copy.deepcopy(group), "paused": True, "paused_by_user": True}
    disabled = {**copy.deepcopy(group), "enabled": False}
    return [None, single, group, paused, disabled]


@pytest.mark.anyio
async def test_same_prompt_and_schema_in_every_state_one_call_per_turn(chat):
    _, replies, requests, _ = chat
    for context in contexts():
        replies.append(turn("explain", answer="Serve il recapito da indicare nel modulo.",
                            target="source"))
        before = len(requests)
        planned = await plan_chat_turn("Cosa intendi per recapito?", [], compilation=context)
        assert planned.intent == "explain" and isinstance(planned.decision, ChatDecision)
        assert len(requests) == before + 1
        prompt = requests[-1]["messages"][1]["content"]
        assert "private-field" not in prompt and "private-session" not in prompt
        schema = prompt.split("SCHEMA OUTPUT:\n", 1)[1].split("\n\nULTIMO MESSAGGIO:")[0]
        assert json.loads(schema) == TurnPlan.model_json_schema()
    assert len({r["messages"][0]["content"] for r in requests}) == 1
    for context in contexts()[3:]:
        assert routing_context(context)["slots"] == []
    assert len(routing_context(contexts()[1])["slots"][0]["context"]) == 1500


@pytest.mark.parametrize("intent", ["reply", "explain", "retrieve", "pause", "resume", "finish",
                                          "generate", "compile"])
def test_only_answer_fields_can_contain_updates(intent):
    candidate = turn(intent, replies=[reply(1, value="a@b.it")])
    if intent in {"reply", "explain"}:
        candidate.update(answer="Ti spiego la domanda.", target="source")
    elif intent == "retrieve":
        candidate.update(queries=["recapito aziendale"], target="source")
    with pytest.raises(ValidationError):
        parse_turn_plan(candidate, {1})


def test_old_contract_and_model_selected_field_are_rejected():
    with pytest.raises(ValidationError):
        TurnPlan.model_validate({"action": "reply", "answer": "Ciao", "queries": [],
                                 "target": "source"})
    with pytest.raises(ValueError):
        parse_turn_plan(turn("answer_fields", replies=[{
            **reply(1, value="Anna"), "field_id": "invented",
        }]), {1})


@pytest.mark.anyio
async def test_same_field_reply_binds_to_single_or_group_backend_snapshot(chat):
    for context, result_type in zip(contexts()[1:3], [ActiveFieldDecision, ClarificationDecision]):
        chat[1].append(turn("answer_fields", replies=[reply(1, value="a@b.it")]))
        planned = await plan_chat_turn("a@b.it", [], compilation=context)
        assert isinstance(planned.decision, result_type)
        assert planned.intent == "answer_fields"


@pytest.mark.parametrize("context", [None, *contexts()[3:]])
def test_no_active_slot_cannot_receive_an_answer(context):
    allowed = {s["slot"] for s in (routing_context(context) or {}).get("slots", [])}
    with pytest.raises(ValueError):
        parse_turn_plan(turn("answer_fields", replies=[reply(1, value="Anna")]), allowed)


@pytest.mark.anyio
async def test_uncertainty_with_explanation_does_not_defer_or_change_fields(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    result = await say(chat, state, "Non so, prima aiutami a capire cosa mi stai chiedendo", turn(
        "explain", answer="Ti chiedo il recapito da inserire nel modulo.", target="source",
    ))
    assert result.status_code == 200 and result.json()["compilation"] is None
    assert await current(chat[0], state) == state


@pytest.mark.anyio
async def test_pause_mixed_with_negative_writes_no_answer_and_explanation_stays_paused(
    chat, monkeypatch,
):
    state = await checkpoint(chat, monkeypatch)
    response = await say(chat, state, "No, preferisco interrompere qui la compilazione",
                         turn("pause"))
    assert response.status_code == 200
    paused = await current(chat[0], state)
    assert paused["chat"]["paused_by_user"] and paused["fields"] == state["fields"]
    response = await say(chat, paused, "Aiutami a capire cosa avevi chiesto", turn(
        "explain", answer="Ti avevo chiesto i dati di contatto richiesti dal modulo.",
        target="source",
    ))
    assert response.json()["compilation"] is None
    assert await current(chat[0], paused) == paused
    response = await say(chat, paused, "Possiamo riprendere la compilazione adesso", turn("resume"))
    assert response.status_code == 200
    assert not (await current(chat[0], paused))["chat"]["paused_by_user"]


@pytest.mark.anyio
@pytest.mark.parametrize("intent", ["explain", "pause"])
async def test_invalid_mixed_payload_retries_once_and_preserves_entire_session(
    chat, monkeypatch, intent,
):
    state = await checkpoint(chat, monkeypatch)
    invalid = turn(intent, replies=[reply(1, value="Anna")])
    if intent == "explain":
        invalid.update(answer="Ti spiego la domanda.", target="source")
    # Queue native invalid responses directly, bypassing any fixture scenario translation.
    chat[1].extend([invalid, invalid])
    before = len(chat[2])
    result = await chat[0].post("/api/projects/alpha/answer", json={
        "question": "Prima vorrei capire questo punto", "conversation_id": state["conversation_id"],
        "compilation_session_id": state["id"], "compilation_version": state["version"],
    })
    assert result.json()["generation_status"] == "failed"
    assert len(chat[2]) == before + 2
    assert await current(chat[0], state) == state


@pytest.mark.anyio
async def test_last_remaining_slot_keeps_its_position_after_partial_replies(chat):
    context = contexts()[1]
    context["question"]["slots"] = [{
        "slot": 4, "kind": "value", "label": "Recapito", "field_ids": ["private-field"],
    }]
    chat[1].append(turn("answer_fields", replies=[reply(4, value="a@b.it")]))
    planned = await plan_chat_turn("a@b.it", [], compilation=context)
    assert planned.decision.value == "a@b.it"
    assert routing_context(context)["slots"][0]["slot"] == 4
