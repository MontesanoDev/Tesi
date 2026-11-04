"""One message can answer the active question and give other data; nothing is lost in silence.

Real Minervino turn: «Sì, confermo… Leonardo Montemurro è il firmatario…» with one active question.
The router sent the signatory to a slot that did not exist and the backend dropped it, without any
error or notice: nine personal fields stayed empty and the next question was on something else.
"""

import json
from io import BytesIO

import pytest
from docx import Document
from test_clarification_loop import CLAUSE, LINE, SOURCE, analysis, route, values
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_sessions import source

from app import compilation_chat as chat
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_conversation import selective_pool, targets
from app.compilation_scope_review import session_data

__all__ = ["api", "provider"]

SIGNATORY = "Il sottoscritto ____________, nato a ____________"
PERSON = ("\n### Ada Neri - amministratore unico\n\n- Nome e cognome: Ada Neri.\n"
          "- Luogo di nascita: Bari.\n- Data di nascita: 01/01/1980.\n")
MESSAGE = ("Sì, confermo che partecipiamo come società di ingegneria. "
           "La firmataria è Ada Neri.")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


async def analyzed(api, monkeypatch):
    doc = Document()
    for line in (CLAUSE, "Denominazione ____________", LINE, SIGNATORY):
        doc.add_paragraph(line)
    stream = BytesIO()
    doc.save(stream)
    form = (await api.post("/api/projects/alpha/forms",
                           files={"file": ("modulo.docx", stream.getvalue())})).json()
    await source(api, SOURCE + PERSON, name="societa.md")

    async def model(client, settings, body, timeout, **kwargs):
        return json.dumps(analysis(json.loads(body["messages"][1]["content"]))), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", model)
    return await resolve(api, (await api.post(BASE, json={
        "form_id": form["id"], "engine": "global", "start_in_chat": True})).json())


def active_signatory(s):
    """The active question: the signatory name, which unlocks the most data in this FORM."""
    [slot] = chat.planner_context(s)["question"]["slots"]
    assert slot["kind"] == "value" and slot["slot"] == 1
    return next(q for q in targets(session_data(s)) if q["key"].startswith("field:p3."))


def condition_target(s):
    return next(q for q in targets(session_data(s)) if q["kind"] == "applicability")


REPLY = {"slot": 1, "action": "VALUE", "value": "Ada Neri",
         "user_quote": "La firmataria è Ada Neri."}


@pytest.mark.anyio
async def test_one_message_answers_the_question_and_gives_another_destination(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    signer, condition = active_signatory(s), condition_target(s)
    plan = {"intent": "answer_fields", "replies": [REPLY], "edits": [
        {"target": condition["target"], "action": "CONDITION_TRUE",
         "user_quote": "Sì, confermo che partecipiamo come società di ingegneria."}]}
    s, calls, routed = await route(s, monkeypatch, MESSAGE, plan)
    assert isinstance(routed.decision, chat.ClarificationDecision)
    assert len(json.loads(calls[0]["messages"][1]["content"])["proposals"]) == 2
    d = s["global_compilation"]["dialogue"]
    assert values(s)[signer["field_ids"][0]]["value"] == "Ada Neri"
    assert d["answers"][condition["key"]]["applies"] is True
    assert "field:" + signer["field_ids"][0] in d["answers"]


@pytest.mark.anyio
async def test_each_part_has_its_own_verdict_a_refused_edit_leaves_the_answer_standing(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    signer = active_signatory(s)
    number = next(q for q in targets(session_data(s)) if q.get("alternatives"))
    message = "La firmataria è Ada Neri. Il numero di Beta S.p.A. è 123."
    plan = {"intent": "answer_fields", "replies": [REPLY], "edits": [
        {"target": number["target"], "action": "VALUE", "value": "123",
         "user_quote": "Il numero di Beta S.p.A. è 123."}]}
    s, _, _ = await route(s, monkeypatch, message, plan)
    assert number["field_ids"][0] not in values(s)
    assert values(s)[signer["field_ids"][0]]["value"] == "Ada Neri"


@pytest.mark.anyio
async def test_a_reply_on_a_slot_that_does_not_exist_is_repaired_once_then_reported(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    signer = active_signatory(s)
    plan = {"intent": "answer_fields", "replies": [REPLY, {
        "slot": 3, "action": "CONDITION_TRUE", "user_quote": "Sì, partecipiamo come società."}]}
    s, _, _ = await route(s, monkeypatch, MESSAGE, plan)
    receipt = dialogue.continuation_receipt(s["global_compilation"]["dialogue"])
    assert "Non ho registrato questa parte del messaggio: «Sì, partecipiamo come società.»" in (
        receipt)
    assert values(s)[signer["field_ids"][0]]["value"] == "Ada Neri"


@pytest.mark.anyio
async def test_the_previous_profile_keeps_the_old_single_intent_contract(
    api, provider, monkeypatch,
):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30-r2")
    s = await analyzed(api, monkeypatch)
    assert not chat.planner_context(s)["conversation_data"].get("conversation_turn_revision")


def test_the_question_that_unlocks_more_data_comes_first():
    data = {"conversation_turn_revision": 1, "dialogue": {"requested_keys": []},
            "catalog": {"blocks": [], "candidates": {}}}
    choose = {"key": "field:b", "kind": "value", "field_ids": ["b"],
              "documented_alternatives": True, "impact": 1, "label": "Numero"}
    signer = {"key": "field:a", "kind": "value", "field_ids": ["a"], "form_owned": True,
              "impact": 1, "label": "Sottoscritto"}
    from app import compilation_conversation as conversation

    original = conversation.person_groups
    conversation.person_groups = lambda d: {"a": set("abcdefghi")}
    try:
        assert selective_pool(data, [choose, signer])[0]["key"] == "field:a"
        condition = {"key": "condition:c", "kind": "applicability", "field_ids": ["x"] * 40,
                     "documented": 40, "impact": 40, "label": "Ramo"}
        assert selective_pool(data, [signer, condition])[0]["key"] == "condition:c"
    finally:
        conversation.person_groups = original


def test_the_draft_says_apart_what_is_absent_not_assessed_or_suspended():
    def field(cid, label, **extra):
        return {"candidate_id": cid, "label": label, "conditions": [], **extra}

    data = {"conversation_turn_revision": 1, "dialogue": {"answers": {}}, "audit": {
        "conditions": {"c": {"result": "unknown"}}, "fields": [
            field("a", "Fax", coverage={"state": "EXPLAINED_UNFILLED",
                                        "outcome": "source_not_found"}),
            field("b", "Sito web", coverage={"state": "UNASSESSED", "origin": "MODEL"}),
            field("c", "Partita IVA", review_kind="subject_uncertain", coverage={
                "state": "CLARIFICATION"}),
            # A branch never confirmed and a field already written say nothing here.
            field("d", "Ramo", conditions=["c"], coverage={"state": "UNASSESSED"}),
            field("e", "Telefono", coverage={"state": "UNASSESSED"})]}}
    notice = dialogue.unexported_notice(data, written={"e"})
    assert "L'analisi non ha trovato nelle fonti: 1 (Fax)." in notice
    assert "Non sono stati valutati: 1 (Sito web)." in notice
    assert "non è certo a chi si riferiscono: 1 (Partita IVA)." in notice
    assert "Ramo" not in notice and "Telefono" not in notice
    assert not dialogue._empty_kinds({**data, "conversation_turn_revision": None}, set())
