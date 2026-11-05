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
from app.compilation_conversation import (
    fit_turn_parts,
    selective_pool,
    targets,
    without_repeated_edits,
)
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


def test_a_long_turn_keeps_answers_and_writes_and_reports_only_what_is_left_out():
    reply = {"slot": 1, "action": "CONDITION_TRUE", "user_quote": "Sì."}
    edits = [{"target": 5, "action": "SKIP", "user_quote": "Rinvio le categorie."},
             {"target": 4, "action": "VALUE", "user_quote": "Firma Ada Neri.", "value": "Ada Neri"},
             {"target": 3, "action": "CONDITION_TRUE", "user_quote": "Ada Neri firma."},
             {"target": 6, "action": "REFUSE", "user_quote": "Non autorizzo dichiarazioni."}]
    kept, left_out = fit_turn_parts([reply], edits)
    assert [e["target"] for e in kept] == [4, 3, 5]
    assert left_out == ["Non autorizzo dichiarazioni."]
    assert fit_turn_parts([], edits) == (edits, [])
    assert fit_turn_parts([reply] * 4, edits)[0] == []


@pytest.mark.anyio
async def test_a_turn_with_too_many_parts_is_not_lost_and_says_what_it_did_not_record(
    api, provider, monkeypatch,
):
    # Real run: 1 reply + 4 edits failed twice and the whole message was lost.
    s = await analyzed(api, monkeypatch)
    signer, condition = active_signatory(s), condition_target(s)
    others = [q for q in targets(session_data(s)) if q["key"] not in {
        signer["key"], condition["key"]} and q["kind"] == "value"][:2]
    refused = "Non autorizzo altro."
    message = f"{MESSAGE} Rinvio il resto. {refused} Rinvio anche questo."
    plan = {"intent": "answer_fields", "replies": [REPLY], "edits": [
        {"target": condition["target"], "action": "CONDITION_TRUE",
         "user_quote": "Sì, confermo che partecipiamo come società di ingegneria."},
        {"target": others[0]["target"], "action": "SKIP", "user_quote": "Rinvio il resto."},
        {"target": others[1]["target"], "action": "SKIP", "user_quote": "Rinvio anche questo."},
        {"target": others[1]["target"] + 1000, "action": "REFUSE", "user_quote": refused}]}
    s, _, routed = await route(s, monkeypatch, message, plan)
    assert isinstance(routed.decision, chat.ClarificationDecision)
    d = s["global_compilation"]["dialogue"]
    assert values(s)[signer["field_ids"][0]]["value"] == "Ada Neri"
    assert d["answers"][condition["key"]]["applies"] is True
    assert f"«{refused}»" in dialogue.continuation_receipt(d)


@pytest.mark.anyio
async def test_the_previous_profile_keeps_the_old_single_intent_contract(
    api, provider, monkeypatch,
):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30-r2")
    s = await analyzed(api, monkeypatch)
    assert not chat.planner_context(s)["conversation_data"].get("conversation_turn_revision")


def test_only_a_reply_repeating_an_edit_goes():
    yes = {"slot": 1, "action": "CONDITION_TRUE", "user_quote": "Sì, confermo."}
    name = {"slot": 1, "action": "VALUE", "value": "Ada Neri", "user_quote": "Ada Neri firma."}
    edit = {"target": 3, "action": "VALUE", "value": "Ada Neri", "user_quote": "Ada Neri firma."}
    assert without_repeated_edits([yes, name], [edit]) == [yes]
    other_quote = {**edit, "user_quote": "Firma Ada Neri."}
    assert without_repeated_edits([yes, name], [other_quote]) == [yes, name]
    other_value = {**edit, "value": "Ada Bianchi"}
    assert without_repeated_edits([yes, name], [other_value]) == [yes, name]
    skipped = {**edit, "action": "SKIP"}
    assert without_repeated_edits([yes, name], [skipped]) == [yes, name]


@pytest.mark.anyio
async def test_a_name_repeated_on_the_slot_does_not_cancel_the_confirmation(
    api, provider, monkeypatch,
):
    # Real runs: the name both on slot 1 and on its target; the confirmation was asked again.
    s = await analyzed(api, monkeypatch)
    signer, condition = active_signatory(s), condition_target(s)
    s, _, _ = await route(s, monkeypatch, "La firmataria è Ada Neri.",
                          {"intent": "answer_fields", "replies": [REPLY], "edits": []})
    s = await resolve(api, s)
    [slot] = chat.planner_context(s)["question"]["slots"]
    assert slot["kind"] == "applicability"
    quote = "La firmataria è Ada Bianchi."
    yes = "Sì, confermo che partecipiamo come società di ingegneria."
    plan = {"intent": "answer_fields",
            "replies": [{"slot": 1, "action": "CONDITION_TRUE", "user_quote": yes},
                        {"slot": 1, "action": "VALUE", "value": "Ada Bianchi",
                         "user_quote": quote}],
            "edits": [{"target": signer["target"], "action": "VALUE", "value": "Ada Bianchi",
                       "user_quote": quote}]}
    s, _, routed = await route(s, monkeypatch, f"{yes} {quote}", plan)
    assert isinstance(routed.decision, chat.ClarificationDecision)
    answers = s["global_compilation"]["dialogue"]["answers"]
    assert answers[condition["key"]]["applies"] is True
    assert values(s)[signer["field_ids"][0]]["value"] == "Ada Bianchi"


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
