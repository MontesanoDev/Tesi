"""Incremental conversation: real persistence/export, simulated model boundary."""

import json
from copy import deepcopy
from io import BytesIO

import pytest
from docx import Document
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_user_extraction import REAL_QUOTE, REAL_VALUE, ready

from app import compilation_chat as chat
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app import intents
from app.config import use_ai_settings
from app.db import connection

__all__ = ["api", "provider"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def conversational(api, monkeypatch, doc=None):
    if doc is None:
        session, _, _ = await ready(api, monkeypatch)
    else:
        monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
        monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
        stream = BytesIO()
        doc.save(stream)
        form = (await api.post("/api/projects/alpha/forms", files={
            "file": ("referenti.docx", stream.getvalue())})).json()

        async def empty(client, settings, body, timeout, **kwargs):
            return json.dumps({"version": 12, "fields": {}, "facts": {}, "conditions": {},
                               "bindings": {}, "choice_groups": {}, "clarifications": {},
                               "coverage": []}), "simulated", {}

        monkeypatch.setattr(adapter, "request_model_content", empty)
        session = (await api.post(BASE, json={"form_id": form["id"], "engine": "global",
                                            "start_in_chat": True})).json()
        session = await resolve(api, session)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"].update(conversation_revision=1, user_extraction_revision=1)
        state["global_compilation"]["dialogue"]["question"] = None
        return sessions.save_state(db, row, state, "test_conversation")


async def edit(session, monkeypatch, message, key, value=None, action="VALUE", reject=False,
               bad_first=False):
    from app.compilation_conversation import targets
    from app.compilation_scope_review import session_data
    entries = targets(session_data(session))
    target = next(q["target"] for q in entries if q["key"] == key)
    calls = []

    async def model(client, settings, body, timeout, **kwargs):
        calls.append(body)
        if kwargs["response_schema"]["title"] == "FormScopeChecks":
            context = json.loads(body["messages"][1]["content"])
            raw = {"checks": [{"slot": p["slot"], "result": "AMBIGUOUS" if reject else "SUPPORTED",
                               "scope_result": "SUPPORTED"} for p in context["proposals"]]}
        else:
            raw = {"intent": "edit_fields", "answer": "", "queries": [], "target": "form",
                   "edits": [{"target": target, "action": action, "value": value,
                              "user_quote": message}]}
            if bad_first and len(calls) == 1:
                raw.update(intent="answer_fields", replies=[{
                    "slot": 1, "action": "VALUE", "value": None, "user_quote": message}])
        return json.dumps(raw), "simulated", {"total_tokens": 10}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        plan = await intents.plan_chat_turn(message, [], compilation=chat.planner_context(session))
    if isinstance(plan.decision, chat.ClarificationDecision):
        await chat.handle_group_decision("alpha", None, plan.decision, session, message)
    return sessions.get_session("alpha", session["id"]), calls, plan


@pytest.mark.anyio
async def test_free_multivalue_edit_after_export_then_different_person(api, provider, monkeypatch):
    s = await conversational(api, monkeypatch)
    s, calls, _ = await edit(s, monkeypatch, REAL_QUOTE, "field:p0.s0", REAL_VALUE)
    assert len(calls) == 4  # Router + name guard + two ordinary extra guard batches.
    assert len(s["global_compilation"]["dialogue"]["user_values"]) == 7
    s = await resolve(api, s)
    ids, conditions, users = dialogue.export_selection(s)
    response = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ids, "confirmed_condition_ids": conditions,
        "user_candidate_ids": users, "allow_unresolved": True, "user_quote": "Fammi una bozza"})
    assert response.status_code == 200, response.text
    s = response.json()
    first_url = s["last_generation"]["downloads"]["docx"]
    original = (await api.get(first_url)).content
    s, _, _ = await edit(s, monkeypatch, "Il firmatario è Ada Neri, non Leonardo.",
                          "field:p0.s0", "Ada Neri")
    assert s["global_compilation"]["dialogue"]["user_values"]["p0.s0"]["value"] == "Ada Neri"
    assert not set(s["global_compilation"]["dialogue"]["user_values"]) & {
        "p0.s1", "p0.s2", "p0.s3", "p1.s0", "p1.s1", "p1.s2"}
    s = await resolve(api, s)
    ids, conditions, users = dialogue.export_selection(s)
    response = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ids, "confirmed_condition_ids": conditions,
        "user_candidate_ids": users, "allow_unresolved": True, "user_quote": "Nuova bozza"})
    assert response.status_code == 200, response.text
    second = (await api.get(response.json()["last_generation"]["downloads"]["docx"])).content
    text = "\n".join(p.text for p in Document(BytesIO(second)).paragraphs)
    assert "Ada Neri" in text and "Leonardo" not in text and "Lecce" not in text
    assert "[X]" not in text and "BOZZA NON VERIFICATA" in text
    assert (await api.get(first_url)).content == original


@pytest.mark.anyio
async def test_ambiguous_free_edit_preserves_original_without_write(api, provider, monkeypatch):
    s = await conversational(api, monkeypatch)
    before = deepcopy(s["global_compilation"]["dialogue"])
    s, _, plan = await edit(s, monkeypatch, "Il firmatario è Ada oppure Maria",
                             "field:p0.s0", "Ada", reject=True)
    assert not s["global_compilation"]["dialogue"].get("user_values")
    assert s["global_compilation"]["dialogue"] == before
    assert plan.decision.action == "reply"


def test_selective_questions_prioritize_documented_scope_over_optional_empty_fields():
    from app.compilation_conversation import selective_pool
    pool = [
        {"key": "field:x", "kind": "value", "impact": 1, "slot": 1},
        {"key": "condition:c", "kind": "applicability", "documented": 15,
         "impact": 20, "slot": 2},
        {"key": "choice:g", "kind": "choice", "impact": 4, "slot": 3},
    ]
    selected = selective_pool({"dialogue": {}}, pool)
    assert [q["key"] for q in selected] == ["condition:c"]


@pytest.mark.anyio
async def test_other_form_named_contact_withdraw_reopen_pause_and_correct(
    api, provider, monkeypatch,
):
    doc = Document()
    doc.add_paragraph("Nominativo del referente: ________")
    doc.add_paragraph("Luogo di nascita: ________")
    doc.add_paragraph("Data di nascita: ________")
    doc.add_paragraph("Nominativo del responsabile: ________")
    s = await conversational(api, monkeypatch, doc)
    message = "Metti Liam O’Connor nel campo Nominativo del referente."
    s, calls, _ = await edit(s, monkeypatch, message, "field:p0.s0", "Liam O’Connor")
    assert len(calls) == 2  # No extra extraction call for a plain name.
    assert s["global_compilation"]["dialogue"]["instructions"][-1]["message"] == message
    assert s["chat"]["auto_continue"], s["global_compilation"]["dialogue"].get("latest_turn")
    s = await resolve(api, s)
    s, _, _ = await edit(s, monkeypatch, "Non usare il nome del referente.",
                          "field:p0.s0", action="REFUSE")
    s = await resolve(api, s)
    assert "p0.s0" not in dialogue.export_selection(s)[2]
    rejected = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": [], "confirmed_condition_ids": [],
        "user_candidate_ids": ["p0.s0"], "allow_unresolved": True, "user_quote": "Bozza"})
    assert rejected.status_code == 409
    s = adapter.control_session("alpha", s["id"], s["version"], "pause")
    before = deepcopy(s["global_compilation"]["dialogue"]["answers"])
    s = adapter.control_session("alpha", s["id"], s["version"], "resume")
    assert s["global_compilation"]["dialogue"]["answers"] == before
    s, _, _ = await edit(s, monkeypatch, "Riprendiamo il nome del referente.",
                          "field:p0.s0", action="REOPEN")
    s = await resolve(api, s)
    assert s["chat"]["question"]["slots"][0]["key"] == "field:p0.s0"
    assert "p0.s0" not in dialogue.export_selection(s)[2]
    s, _, _ = await edit(s, monkeypatch, "Il nome del referente è Jean-Luc D’Amico.",
                          "field:p0.s0", "Jean-Luc D’Amico")
    s = await resolve(api, s)
    assert dialogue.export_selection(s)[2] == ["p0.s0"]
    assert "p3.s0" not in s["global_compilation"]["dialogue"]["user_values"]


@pytest.mark.anyio
async def test_unscoped_withdrawal_cannot_change_an_arbitrary_field(api, provider, monkeypatch):
    s = await conversational(api, monkeypatch)
    s, _, _ = await edit(s, monkeypatch, "Il firmatario è Ada Neri", "field:p0.s0", "Ada Neri")
    s = await resolve(api, s)
    before = deepcopy(s["global_compilation"]["dialogue"])
    s, _, _ = await edit(s, monkeypatch, "Non usare quel dato", "field:p0.s0",
                          action="REFUSE", reject=True)
    assert s["global_compilation"]["dialogue"] == before


def test_changed_identity_withdraws_original_model_values_before_source_reuse():
    from unittest.mock import patch

    from app.compilation_conversation import reconcile_identity

    data = {"conversation_revision": 1}
    original = {"facts": {"f": {"subject": "Alma Neri"}}, "fields": [{
        "candidate_id": "birth", "fact_id": "f", "validation": "GROUNDED_PROPOSAL",
        "value": "Roma", "source_evidence": [{"quote": "Alma Neri: nata a Roma"}]}]}
    with patch("app.compilation_conversation.person_groups",
               return_value={"name": {"name", "birth"}}), patch(
                   "app.compilation_source_reuse._selection", return_value=("Liam O’Connor", {})):
        result = reconcile_identity(data, original)
    assert result["fields"][0]["value"] is None
    assert result["fields"][0]["source_evidence"] == []
    assert original["fields"][0]["value"] == "Roma"


@pytest.mark.anyio
async def test_explicit_export_while_paused_does_not_resume_or_change_receipts(
    api, provider, monkeypatch,
):
    from app.compilation_chat import ChatControl
    from app.intents import ChatDecision

    s = await conversational(api, monkeypatch)
    s, _, _ = await edit(s, monkeypatch, "Il firmatario è Ada Neri", "field:p0.s0", "Ada Neri")
    s = await resolve(api, s)
    s = adapter.control_session("alpha", s["id"], s["version"], "pause")
    before = deepcopy(s["global_compilation"]["dialogue"]["answers"])
    _, command = await adapter.handle_chat_action(s, ChatDecision(action="compilation_control",
        answer="", queries=[], target="form",
        control=ChatControl(kind="finish", user_quote="Bozza")),
        s["version"], "Bozza")
    assert command["action"] == "generated"
    s = sessions.get_session("alpha", s["id"])
    assert s["chat"]["paused_by_user"]
    assert s["global_compilation"]["dialogue"]["answers"] == before


def test_no_checkbox_from_source_without_user_choice():
    from app.compilation_conversation import blocked_fields

    data = {"conversation_revision": 1, "catalog": {"candidates": {
        "option": {"type": "checkbox"}}}, "dialogue": {}}
    assert blocked_fields(data) == {"option"}
    data["dialogue"] = {"user_values": {"option": {"choice_group_id": "g", "value": True}},
                        "answers": {"choice:g": {"action": "CONDITION_TRUE", "applies": True}}}
    assert blocked_fields(data) == {"option"}  # A branch assent is not a checkbox choice.


def test_short_question_keeps_visible_scope_without_technical_counts():
    pool = [{"slot": 1, "key": "condition:c", "kind": "applicability", "label": "Società",
             "condition": "La domanda è presentata come società", "field_ids": ["a", "b"],
             "affected_fields": ["Denominazione", "Sede"], "impact": 2, "documented": 2}]
    result = dialogue.render_dialogue(dialogue.DialoguePlan(message="Ho trovato i dati aziendali."),
        pool, fill_open=True, conversational=True)
    assert len(result["question"]["slots"]) == 1
    assert result["question"]["slots"][0]["destinations_shown"]
    assert "Denominazione, Sede" in result["message"]
    assert "dati del modulo" not in result["message"]


@pytest.mark.anyio
async def test_retry_preserves_free_edit_capability_after_real_mixed_contract_error(
    api, provider, monkeypatch,
):
    s = await conversational(api, monkeypatch)
    s, calls, _ = await edit(s, monkeypatch, "Il firmatario è Ada Neri", "field:p0.s0",
                             "Ada Neri", bad_first=True)
    assert len(calls) == 3
    assert "modifiche libere restano disponibili nel retry" in calls[1]["messages"][-1]["content"]
    assert s["global_compilation"]["dialogue"]["user_values"]["p0.s0"]["value"] == "Ada Neri"


@pytest.mark.anyio
async def test_router_short_quotes_do_not_drop_the_rest_of_a_personal_sentence(
    api, provider, monkeypatch,
):
    from app.compilation_conversation import bind_edits, complete_person_reply, targets
    from app.compilation_scope_review import session_data

    s = await conversational(api, monkeypatch)
    catalog = {q["key"]: q["target"] for q in targets(session_data(s))}
    edits = [intents.TurnEdit(target=catalog["field:" + cid], action="VALUE", value=value,
                             user_quote=quote) for cid, value, quote in [
        ("p0.s0", "Leonardo Montemurro", "Il sottoscrittore è Leonardo Montemurro"),
        ("p0.s1", "Lecce", "nato a Lecce (LE)"),
        ("p0.s2", "LE", "nato a Lecce (LE)"),
        ("p0.s3", "14/11/1982", "il 14/11/1982")]]
    context, _ = bind_edits(chat.planner_context(s), edits)
    replies = [intents.TurnReply(slot=n, **e.model_dump(exclude={"target"}))
               for n, e in enumerate(edits, 1)]
    result = complete_person_reply(context, replies, REAL_QUOTE)
    assert len(result) == 1 and result[0].user_quote == REAL_QUOTE
    from app.compilation_user_extraction import prepare

    _, records = prepare(context["user_value_frames"], result, REAL_QUOTE)
    assert len(records[0]["values"]) == 7
    # A sentence with a different name cannot widen the router's asserted destination.
    assert complete_person_reply(context, replies, REAL_QUOTE.replace(
        "Leonardo Montemurro", "Ada Neri")) == replies
