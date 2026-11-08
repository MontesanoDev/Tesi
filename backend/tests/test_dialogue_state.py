"""Nothing of a message is lost, a label is not a condition, a draft is not republished.

Real manual Minervino turns: the choice given with the branch was never recorded and asked again; a
bare «4» was refused as absent from the message; 11 company fields waited on «dell'operatore
economico», the label of their own field; «metti tutti i dati di…» found no destination.
"""

import json
from io import BytesIO

import pytest
from docx import Document
from test_checkbox_policy import draft_of, export
from test_clarification_loop import values, verdicts
from test_compilation_global_sessions import api, provider, resolve
from test_mixed_turn import MESSAGE, REPLY, active_signatory, analyzed, condition_target

from app import compilation_chat as chat
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app import intents
from app.compilation_conversation import (
    literal_choice_values,
    literal_quotes,
    merge_label_conditions,
    unrouted_sentences,
)
from app.compilation_global_dialogue import condition_receipts, continuation_receipt
from app.compilation_user_extraction import extract
from app.config import use_ai_settings

__all__ = ["api", "provider"]

TURN = ("Sì, confermo che Mapi Ingegneria S.r.l. partecipa come società di ingegneria.\n\n"
        "Il sottoscrittore è Leonardo Montemurro, amministratore unico e rappresentante legale "
        "della società.\n\n"
        "Per la sezione «IN QUALITÀ DI» scelgo esplicitamente l'opzione 4: legale rappresentante "
        "di società di ingegneria.\n\n"
        "Per adesso lascia vuote categorie, attestazioni e luogo/data.")
BRANCH = "Sì, confermo che Mapi Ingegneria S.r.l. partecipa come società di ingegneria."
SIGNER = ("Il sottoscrittore è Leonardo Montemurro, amministratore unico e rappresentante legale "
          "della società.")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def session_with(kind="choice", revision=1):
    data = {"conversation_turn_revision": 1}
    if revision:
        data["dialogue_state_revision"] = revision
    return {"conversation_data": data, "question": {"slots": [{"slot": 1, "kind": kind}]}}


def chosen(option=4, quote="Per la sezione scelgo l'opzione 4.", **extra):
    return {"slot": 1, "action": "VALUE", "user_quote": quote, "value": quote,
            "selected_options": [option], **extra}


@pytest.mark.parametrize("message", ["4", "4.", " 4 ", "la 4", "opzione 4", "numero 4", "n. 4"])
def test_a_bare_option_number_is_its_own_quote(message):
    [reply] = literal_choice_values([chosen()], session_with(), message)
    assert reply["user_quote"] == message.strip() and reply["value"] == message.strip()
    assert reply["selected_options"] == [4]
    assert literal_quotes([reply], session_with(), message) == ([reply], [])


def test_a_bare_number_that_is_not_the_chosen_option_is_not_repaired():
    [reply] = literal_choice_values([chosen(option=3)], session_with(), "4")
    assert reply["user_quote"] != "4"
    _, invented = literal_quotes([reply], session_with(), "4")
    assert invented == [reply]


def test_a_bare_number_repairs_only_a_choice_of_the_new_profile():
    reply = chosen()
    assert literal_choice_values([reply], session_with(kind="value"), "4") == [reply]
    assert literal_choice_values([reply], session_with(revision=None), "4")[0][
        "user_quote"] == reply["user_quote"]
    assert literal_quotes([reply], session_with(revision=None), "4") == ([reply], [])


def test_a_value_in_the_message_is_quoted_with_its_sentence():
    message = "Scusa puoi mettere leonardo montemurro nel sottoscritto?"
    reply = {"slot": 1, "action": "VALUE", "value": "Leonardo Montemurro",
             "user_quote": "metti leonardo montemurro nel sottoscritto"}
    [fixed], invented = literal_quotes([reply], session_with(kind="value"), message)
    assert fixed["user_quote"] == message and not invented


def test_a_value_the_message_does_not_contain_is_never_repaired():
    message = "Metti tutti i dati di Leonardo nel sottoscritto"
    reply = {"slot": 1, "action": "VALUE", "value": "Lecce", "user_quote": "nato a Lecce"}
    fixed, invented = literal_quotes([reply], session_with(kind="value"), message)
    assert fixed == [reply] and invented == [reply]


def test_what_no_reply_quoted_is_what_is_left():
    assert unrouted_sentences(TURN, [BRANCH, SIGNER]) == [
        "Per la sezione «IN QUALITÀ DI» scelgo esplicitamente l'opzione 4: legale rappresentante "
        "di società di ingegneria.",
        "Per adesso lascia vuote categorie, attestazioni e luogo/data."]


def test_an_abbreviation_does_not_split_a_sentence_and_courtesies_are_nothing():
    assert unrouted_sentences(BRANCH, ["Sì, confermo che Mapi Ingegneria S.r.l. partecipa"]) == []
    assert unrouted_sentences("Ok. Grazie.", []) == []
    assert unrouted_sentences("Scelgo la 4.", []) == ["Scelgo la 4."]
    assert unrouted_sentences(BRANCH, [BRANCH]) == []


def form_data(*, quote="dell'operatore economico", aspect="participation", subject="Mapi S.r.l."):
    def field(cid, condition, fact):
        return {"candidate_id": cid, "conditions": [condition], "proposal": {"fact_id": fact}}

    return {"dialogue_state_revision": 1,
            "catalog": {"candidates": {"h1": {"slot_context": {"before": quote + " "}},
                                       "b1": {"slot_context": {"before": "denominazione "}}}},
            "audit": {"conditions": {
                "label": {"aspect": aspect, "form_evidence": {"quote": quote}},
                "branch": {"aspect": "representation",
                           "form_evidence": {"quote": "Legale rappresentante di società"}}},
                "facts": {"f1": {"entity": "company", "subject": subject},
                          "f2": {"entity": "company", "subject": "Mapi S.r.l."}},
                "fields": [field("h1", "label", "f1"), field("b1", "branch", "f2")]}}


def pool():
    return [{"key": "condition:branch", "kind": "applicability", "condition_ids": ["branch"],
             "field_ids": ["b1"], "impact": 1, "documented": 1, "affected_fields": ["Nome"]},
            {"key": "condition:label", "kind": "applicability", "condition_ids": ["label"],
             "field_ids": ["h1"], "impact": 1, "documented": 1, "affected_fields": ["Sede"]}]


def test_a_label_goes_under_the_branch_about_the_same_company():
    [merged] = merge_label_conditions(form_data(), pool())
    assert merged["key"] == "condition:branch"
    assert merged["condition_ids"] == ["branch", "label"]
    assert merged["implied_condition_ids"] == ["label"]
    assert merged["field_ids"] == ["b1", "h1"] and merged["documented"] == 2


@pytest.mark.parametrize("quote", ["Legale rappresentante di società di ingegneria",
                                   "Professionista singolo con studio in via",
                                   "Il sottoscritto", "Consorzio stabile"])
def test_a_label_naming_a_capacity_is_a_real_alternative_and_stays_apart(quote):
    assert len(merge_label_conditions(form_data(quote=quote), pool())) == 2


def test_a_clause_that_is_not_the_label_of_its_own_field_stays_apart():
    data = form_data()
    data["catalog"]["candidates"]["h1"]["slot_context"]["before"] = "con sede in "
    assert len(merge_label_conditions(data, pool())) == 2


def test_a_label_about_another_company_stays_apart():
    assert len(merge_label_conditions(form_data(subject="Altra S.r.l."), pool())) == 2


@pytest.mark.parametrize("aspect", ["representation", "legal_type", "other"])
def test_only_a_participation_or_identity_label_is_merged(aspect):
    assert len(merge_label_conditions(form_data(aspect=aspect), pool())) == 2


def test_without_an_open_branch_the_label_is_asked_on_its_own():
    assert [q["key"] for q in merge_label_conditions(form_data(), pool()[1:])] == [
        "condition:label"]


def test_the_previous_profile_keeps_them_apart():
    data = form_data()
    data.pop("dialogue_state_revision")
    assert len(merge_label_conditions(data, pool())) == 2


def receipts(applies):
    slot = {"key": "condition:branch", "condition_ids": ["branch", "label"],
            "implied_condition_ids": ["label"], "field_ids": ["b1", "h1"]}
    record = {"action": "CONDITION_TRUE" if applies else "CONDITION_FALSE", "applies": applies}
    return condition_receipts({}, slot, record, None)


def test_only_a_yes_reaches_the_label():
    assert set(receipts(True)) == {"condition:branch", "condition:label"}
    assert set(receipts(False)) == {"condition:branch"}


def frame():
    return {"name_id": "n", "trim_role": True, "question": "",
            "members": {"n": {"property": "name", "form_text": "", "scope": {}, "field": {}}}}


def test_the_role_after_the_comma_never_enters_the_name_field():
    parsed = extract(frame(), SIGNER)
    assert parsed["values"]["n"]["value"] == "Leonardo Montemurro" and not parsed["issues"]


def test_without_a_comma_or_on_the_previous_profile_nothing_changes():
    assert extract({**frame(), "trim_role": False}, SIGNER)["issues"] == [
        "Indica un solo nome e cognome per la persona richiesta."]


def test_an_accepted_change_after_an_export_says_the_file_did_not_change():
    turn = {"accepted": [{"action": "VALUE", "label": "Fax"}], "after_export": True}
    assert "Il file già esportato resta com'è" in continuation_receipt({"latest_turn": turn})
    turn["accepted"] = []
    assert "Il file già esportato" not in continuation_receipt({"latest_turn": turn})


async def rest_flow(s, monkeypatch, message, plans):
    """The real entry of a chat answer: first plan, then the second pass on what is left."""
    calls = []

    async def model(client, settings, body, timeout, **kwargs):
        if kwargs["response_schema"]["title"] == "FormScopeChecks":
            return json.dumps(verdicts(body, identified=True, fixed=None)), "s", {}
        calls.append(body["messages"][1]["content"])
        return json.dumps(
            {"answer": "", "queries": [], "target": "form", **plans.pop(0)}), "s", {}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        routed = await intents.plan_chat_turn(message, [], compilation=chat.planner_context(s))
        text, command = await adapter.answer_with_rest(
            "alpha", None, routed.decision, s, message, s["version"])
    return sessions.get_session("alpha", s["id"]), text, command, calls


@pytest.mark.anyio
async def test_a_part_the_first_pass_dropped_reaches_its_destination(api, provider, monkeypatch):
    s = await analyzed(api, monkeypatch)
    signer, condition = active_signatory(s), condition_target(s)
    quote = "Sì, confermo che partecipiamo come società di ingegneria."
    s2, text, _, calls = await rest_flow(s, monkeypatch, MESSAGE, [
        {"intent": "answer_fields", "replies": [REPLY], "edits": []},
        {"intent": "edit_fields", "edits": [{"target": condition["target"],
                                             "action": "CONDITION_TRUE", "user_quote": quote}]}])
    assert len(calls) == 2
    d = s2["global_compilation"]["dialogue"]
    assert values(s2)[signer["field_ids"][0]]["value"] == "Ada Neri"
    assert d["answers"][condition["key"]]["applies"] is True
    assert "field:" + signer["field_ids"][0] in d["answers"]
    accepted = d["latest_turn"]["accepted"]
    assert len(accepted) >= 2, "one message, one receipt with both parts"


@pytest.mark.anyio
async def test_a_message_fully_routed_costs_no_second_pass(api, provider, monkeypatch):
    s = await analyzed(api, monkeypatch)
    _, condition = active_signatory(s), condition_target(s)
    quote = "Sì, confermo che partecipiamo come società di ingegneria."
    _, _, _, calls = await rest_flow(s, monkeypatch, MESSAGE, [
        {"intent": "answer_fields", "replies": [REPLY], "edits": [
            {"target": condition["target"], "action": "CONDITION_TRUE", "user_quote": quote}]}])
    assert len(calls) == 1


@pytest.mark.anyio
async def test_what_the_second_pass_cannot_place_is_said(api, provider, monkeypatch):
    s = await analyzed(api, monkeypatch)
    s2, text, _, calls = await rest_flow(s, monkeypatch, MESSAGE, [
        {"intent": "answer_fields", "replies": [REPLY], "edits": []},
        {"intent": "explain", "answer": "Non saprei.", "target": "source"}])
    assert len(calls) == 2
    assert "Non ho registrato questa parte del messaggio" in text
    assert "Sì, confermo che partecipiamo" in s2["global_compilation"]["dialogue"]["message"]
    assert condition_target(s2)["key"] not in s2["global_compilation"]["dialogue"]["answers"]


@pytest.mark.anyio
async def test_the_previous_profile_has_no_second_pass(api, provider, monkeypatch):
    s = await analyzed(api, monkeypatch)
    assert s["global_compilation"].get("dialogue_state_revision") in {None, 1}
    from app.db import connection

    with connection() as db:
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        state["global_compilation"].pop("dialogue_state_revision", None)
        s = sessions.save_state(db, row, state, "test_state")
    _, _, _, calls = await rest_flow(s, monkeypatch, MESSAGE, [
        {"intent": "answer_fields", "replies": [REPLY], "edits": []}])
    assert len(calls) == 1


@pytest.mark.anyio
async def test_a_later_draft_keeps_the_first_identical_and_a_pause_is_not_a_change(
    api, provider, monkeypatch,
):
    from app.compilation_chat import ChatControl
    from app.intents import ChatDecision

    doc = Document()
    doc.add_paragraph("Il firmatario è ________")
    doc.save(buffer := BytesIO())
    _, s = await export(api, monkeypatch, Document(BytesIO(buffer.getvalue())))
    from app.db import connection

    with connection() as db:
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        state["global_compilation"]["dialogue_state_revision"] = 1
        s = sessions.save_state(db, row, state, "test_state")
    finish = ChatDecision(action="compilation_control", answer="", queries=[], target="form",
                          control=ChatControl(kind="finish", user_quote="Bozza"))
    _, _ = await adapter.handle_chat_action(s, finish, s["version"], "Bozza")
    s = sessions.get_session("alpha", s["id"])
    first_id = s["last_generation"]["id"]
    _, first = await draft_of(api, s)
    assert s["last_generation"]["changes_since_export"] is False
    assert "state_digest" not in s["last_generation"]
    paused = adapter.control_session("alpha", s["id"], s["version"], "pause")
    assert paused["last_generation"]["changes_since_export"] is False
    s = adapter.control_session("alpha", s["id"], paused["version"], "resume")
    assert s["last_generation"]["id"] == first_id
    s = await resolve(api, s)
    s = await asserted_change(s)
    assert s["last_generation"]["changes_since_export"] is True
    _, _ = await adapter.handle_chat_action(s, finish, s["version"], "Bozza")
    s = sessions.get_session("alpha", s["id"])
    assert s["last_generation"]["id"] != first_id
    assert s["draft_history"][-1]["id"] == first_id
    assert s["last_generation"]["changes_since_export"] is False
    response = await api.get(f"/api/projects/alpha/document-compilations/{first_id}/download/docx")
    assert response.content == first


async def asserted_change(s):
    from app.db import connection

    with connection() as db:
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        answers = state["global_compilation"]["dialogue"].setdefault("answers", {})
        answers["field:test"] = {"action": "VALUE", "value": "nuovo", "user_quote": "nuovo"}
        return sessions.save_state(db, row, state, "test_change")
