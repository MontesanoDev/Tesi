"""Single-question semantic contract: real isolated APIs, simulated model output."""

import json

import pytest
from pydantic import ValidationError
from test_compilation_controls import conditional_meanings, current
from test_compilation_conversation import anyio_backend as anyio_backend
from test_compilation_conversation import chat as chat
from test_compilation_conversation import say, start, step
from test_compilation_sessions import docx, simulate, source
from test_form_retrieval import plan

from app import intents
from app.compilation_chat import (
    ActiveFieldDecision,
    handle_active_decision,
    planner_context,
    single_active_target,
)


async def conditional(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    simulate(monkeypatch, classify_hook=conditional_meanings)
    return await step(chat[0], state)


@pytest.mark.anyio
@pytest.mark.parametrize("message", [
    "no", "No, il sottoscrittore non agisce come procuratore.",
    "No, non si applica al nostro caso.",
])
async def test_semantic_false_binds_to_backend_target_without_model_ids(chat, monkeypatch, message):
    client, _, requests, _ = chat
    state = await conditional(chat, monkeypatch)
    target = state["chat"]["question"]["field_ids"][0]
    response = await say(chat, state, message, {"action": "CONDITION_FALSE"})
    assert response.status_code == 200, response.text
    assert response.json()["compilation"]["action"] == "updated"
    after = await current(client, state)
    field = next(f for f in after["fields"] if f["id"] == target)
    assert field["status"] == "NOT_APPLICABLE" and field["provenance"] == "USER"
    assert field["value"] is None and field["source_evidence"] == []
    assert field["applicability"]["applies"] is False
    assert field["applicability"]["reason"] == f"Indicazione USER: {message}"
    assert after["status"] == "READY" and after["chat"]["question"]["kind"] == "generate"
    prompt = requests[-1]["messages"][1]["content"]
    assert target not in prompt and '"field_ids"' not in prompt
    schema = json.loads(prompt.split("SCHEMA OUTPUT:\n")[1].split("\n\nULTIMO MESSAGGIO:")[0])
    assert "field_id" not in json.dumps(schema) and "user_quote" in json.dumps(schema)


@pytest.mark.anyio
async def test_condition_true_does_not_resolve_value_and_restarts_sources(chat, monkeypatch):
    client, _, _, _ = chat
    state = await conditional(chat, monkeypatch)
    response = await say(chat, state, "sì", {"action": "CONDITION_TRUE"})
    assert response.json()["compilation"]["action"] == "updated"
    after = await current(client, state)
    field = after["fields"][0]
    assert field["status"] == "PENDING" and field["value"] is None
    assert field["applicability"]["applies"] is True
    assert field["applicability"]["provenance"] == "USER"
    assert after["chat"]["auto_continue"] and after["chat"]["question"] is None
    after = await step(client, after)
    assert after["fields"][0]["status"] == "MISSING"
    assert after["chat"]["question"]["kind"] == "value"


@pytest.mark.anyio
@pytest.mark.parametrize("action,message", [
    ("UNKNOWN", "Non saprei rispondere con certezza."),
    ("SKIP", "Preferisco occuparmene più avanti."),
    ("REFUSE", "Preferisco non comunicare questo dato."),
    ("PAUSE", "Fermiamo per ora la compilazione."),
])
async def test_semantic_controls_need_no_target_from_model(chat, monkeypatch, action, message):
    client, _, _, _ = chat
    state = await conditional(chat, monkeypatch)
    response = await say(chat, state, message, {"action": action})
    assert response.status_code == 200, response.text
    after = await current(client, state)
    if action == "PAUSE":
        assert after["fields"] == state["fields"]
        assert after["chat"]["paused_by_user"] and after["chat"]["question"] is None
    else:
        field = dict(after["fields"][0])
        assert field.pop("conversation_disposition")["kind"] == action.lower()
        assert field == state["fields"][0]
        assert after["chat"]["question"]["kind"] == "deferred_summary"


@pytest.mark.anyio
async def test_value_only_changes_current_target_and_uses_user_provenance(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Denominazione sociale", "Data abilitazione")))
    await source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.")
    simulate(monkeypatch, {state["fields"][0]["id"]: ["Mapi Ingegneria S.r.l."]})
    state = await step(client, state)
    assert state["chat"]["question"]["field_ids"] == [state["fields"][1]["id"]]
    response = await say(chat, state, "12 giugno 2014", {
        "action": "VALUE", "value": "12 giugno 2014", "normalized_value": "12/06/2014",
    })
    assert response.json()["compilation"]["action"] == "updated"
    after = await current(client, state)
    assert after["fields"][0] == state["fields"][0]
    field = after["fields"][1]
    assert field["status"] == "USER_PROVIDED" and field["value"] == "12/06/2014"
    assert field["provenance"] == "USER" and field["source_evidence"] == []


@pytest.mark.anyio
@pytest.mark.parametrize("action", ["CLARIFY", "CONDITION_FALSE", "CONDITION_TRUE"])
async def test_ambiguous_answer_does_not_change_fields(chat, monkeypatch, action):
    client, _, _, _ = chat
    state = await conditional(chat, monkeypatch)
    response = await say(chat, state, "Potrebbe applicarsi oppure no", {"action": action})
    assert response.json()["compilation"]["action"] == "clarify"
    assert (await current(client, state))["fields"] == state["fields"]


@pytest.mark.anyio
@pytest.mark.parametrize("bad", [
    {"action": "CONDITION_FALSE", "field_id": "invented"},
    {"action": "CONDITION_FALSE", "id": "invented"},
    {"action": "CONDITION_FALSE", "value": "un valore fattuale"},
    {"action": "CONDITION_TRUE", "user_quote": "una scelta ritagliata"},
])
async def test_wrong_schema_retry_cannot_select_field_or_write_fact(chat, monkeypatch, bad):
    client, replies, requests, _ = chat
    state = await conditional(chat, monkeypatch)
    replies.extend([bad, bad])
    count = len(requests)
    result = await client.post("/api/projects/alpha/answer", json={
        "question": "no", "conversation_id": state["conversation_id"],
        "compilation_session_id": state["id"], "compilation_version": state["version"],
    })
    assert result.status_code == 200 and result.json()["generation_status"] == "failed"
    assert len(requests) == count + 2
    assert "Errori di validazione:" in requests[-1]["messages"][-1]["content"]
    assert (await current(client, state)) == state


@pytest.mark.anyio
async def test_schema_retry_can_recover_without_returning_target(chat, monkeypatch):
    client, replies, requests, _ = chat
    state = await conditional(chat, monkeypatch)
    replies.append({"action": "CONDITION_FALSE", "id": "invented"})
    count = len(requests)
    response = await say(chat, state, "no", {"action": "CONDITION_FALSE"})
    assert response.json()["compilation"]["action"] == "updated"
    assert len(requests) == count + 2
    assert "id: Extra inputs" in requests[-1]["messages"][-1]["content"]
    assert (await current(client, state))["fields"][0]["status"] == "NOT_APPLICABLE"


@pytest.mark.anyio
async def test_single_target_shortcut_rejects_multiple_fields(chat, monkeypatch):
    state = await conditional(chat, monkeypatch)
    context = planner_context(state)
    context["question"]["field_ids"].append("other")
    context["fields"].append({**context["fields"][0], "id": "other"})
    assert single_active_target(context) is None
    responses = chat[1]
    responses.append({"intent": "explain", "target": "source", "queries": [],
                      "answer": "A quale delle due voci ti riferisci?"})
    planned = await intents.plan_chat_turn("no", [], compilation=context)
    assert isinstance(planned.decision, intents.ChatDecision)
    assert planned.decision.action == "reply"
    assert "SCHEMA OUTPUT:" in chat[2][-1]["messages"][1]["content"]
    # An active semantic reply without a coherent backend target is never applied.
    monkeypatch.setattr("app.compilation_chat.planner_context", lambda _: context)
    from fastapi import HTTPException
    with pytest.raises(HTTPException, match="409"):
        await handle_active_decision("alpha", state["conversation_id"],
                                     ActiveFieldDecision(action="CONDITION_FALSE"),
                                     None, state, "no", state["version"])
    assert (await current(chat[0], state)) == state


@pytest.mark.anyio
async def test_stale_semantic_reply_never_updates_a_new_question(chat, monkeypatch):
    client, _, _, _ = chat
    state = await conditional(chat, monkeypatch)
    response = await say(chat, {**state, "version": state["version"] - 1}, "no", {
        "action": "CONDITION_FALSE",
    })
    assert response.status_code == 409
    assert (await current(client, state)) == state


@pytest.mark.anyio
async def test_condition_decision_on_value_question_does_not_exclude_field(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    response = await say(chat, state, "no", {"action": "CONDITION_FALSE"})
    assert response.json()["compilation"]["action"] == "clarify"
    assert (await current(client, state))["fields"] == state["fields"]


@pytest.mark.anyio
@pytest.mark.parametrize("target,question", [
    ("form", "cosa richiede?"), ("source", "qual è la sede legale?"),
])
async def test_new_question_uses_existing_document_routing(chat, monkeypatch, target, question):
    client, replies, _, _ = chat
    state = await conditional(chat, monkeypatch)
    if target == "source":
        await source(client, "Sede legale: Via X")
    replies.append({"answer": "Informazione documentata [1].", "citation_ids": [1]})
    route = plan(target, state["form_id"] if target == "form" else None,
                 "Estremi procura" if target == "form" else "sede legale")
    # Insert the planner result before the generator result, not an extra call.
    replies.insert(0, route)
    result = await client.post("/api/projects/alpha/answer", json={
        "question": question, "conversation_id": state["conversation_id"],
        "form_id": state["form_id"],
    })
    assert result.status_code == 200 and result.json()["generation_status"] == "completed"
    assert not result.json()["compilation"]
    assert all(e["role"] == target for e in result.json()["evidence"])
    assert (await current(client, state)) == state


def test_semantic_contract_cannot_contain_field_selection():
    schema = json.dumps(intents.TurnPlan.model_json_schema())
    assert "field_id" not in schema and "field_replies" not in schema
    with pytest.raises(ValidationError):
        ActiveFieldDecision(action="CONDITION_FALSE", normalized_value="inventato")


@pytest.mark.anyio
async def test_non_conversational_session_has_no_active_question_shortcut(chat, monkeypatch):
    state = await conditional(chat, monkeypatch)
    context = planner_context(state)
    context["enabled"] = False
    assert single_active_target(context) is None
