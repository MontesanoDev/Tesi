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
from app.compilation_branch_evidence import capacity_choice_valid
from app.compilation_conversation import (
    PERSON_REQUEST,
    hide_labels_under_open_branch,
    imply_label_receipts,
    literal_choice_values,
    literal_quotes,
    only_choices_quote_an_option,
    route_person_request,
    sentences,
    unrouted_sentences,
    unseen_question,
    without_target_numbers,
)
from app.compilation_global_dialogue import continuation_receipt, question_pool
from app.compilation_reply_guard import PERSON_REQUEST_RULE
from app.compilation_scope_review import proof, target, valid_receipt
from app.compilation_user_extraction import extract, prepare, simple_name
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


def test_a_label_is_not_asked_while_the_branch_about_the_same_company_is_open():
    assert [q["key"] for q in hide_labels_under_open_branch(form_data(), pool())] == [
        "condition:branch"]


@pytest.mark.parametrize("quote", ["Legale rappresentante di società di ingegneria",
                                   "Professionista singolo con studio in via",
                                   "Il sottoscritto", "Consorzio stabile"])
def test_a_label_naming_a_capacity_is_a_real_alternative_and_stays_apart(quote):
    assert len(hide_labels_under_open_branch(form_data(quote=quote), pool())) == 2


def test_a_clause_that_is_not_the_label_of_its_own_field_stays_apart():
    data = form_data()
    data["catalog"]["candidates"]["h1"]["slot_context"]["before"] = "con sede in "
    assert len(hide_labels_under_open_branch(data, pool())) == 2


def test_a_label_about_another_company_stays_apart():
    assert len(hide_labels_under_open_branch(form_data(subject="Altra S.r.l."), pool())) == 2


@pytest.mark.parametrize("aspect", ["representation", "legal_type", "other"])
def test_only_a_participation_or_identity_label_is_hidden(aspect):
    assert len(hide_labels_under_open_branch(form_data(aspect=aspect), pool())) == 2


def test_without_an_open_branch_the_label_is_asked_on_its_own():
    assert [q["key"] for q in hide_labels_under_open_branch(form_data(), pool()[1:])] == [
        "condition:label"]


def test_the_previous_profile_keeps_them_apart():
    data = form_data()
    data.pop("dialogue_state_revision")
    assert len(hide_labels_under_open_branch(data, pool())) == 2


def implied_session(*, applies=True, action="CONDITION_TRUE", person=None):
    """A real scope proof on the branch: only imply_label_receipts is under test."""
    data = form_data()
    data["writable_ids"] = ["h1", "b1"]
    data["catalog"].update(blocks=[], source_reuse={})
    for f in data["audit"]["fields"]:
        f.update(validation="GROUNDED_PROPOSAL", form_evidence={"quote": "q"},
                 label=f["candidate_id"])
    for item in data["audit"]["conditions"].values():
        item["result"] = "unknown"
    if person is not None:
        data["audit"]["facts"]["p1"] = {"entity": "person", "subject": "Una Persona"}
        data["audit"]["fields"].append({
            "candidate_id": "h2", "conditions": person, "proposal": {"fact_id": "p1"},
            "validation": "GROUNDED_PROPOSAL", "form_evidence": {"quote": "q"}, "label": "Carica"})
        data["catalog"]["candidates"]["h2"] = {"slot_context": {"before": ""}}
    reply = {"action": action, "applies": applies, "user_quote": "Sì", "provenance": "USER",
             "label": "Ramo"}
    receipt = {**reply, "affected_fields": ["b1"], "scope_validation": proof(
        target(data, "condition:branch", ["b1"]), reply)}
    data["dialogue"] = {"answers": {"condition:branch": receipt}}
    return data


def test_an_accepted_branch_answers_its_label_with_an_own_verifiable_receipt():
    data = implied_session()
    assert imply_label_receipts(data) == ["dell'operatore economico"]
    receipt = data["dialogue"]["answers"]["condition:label"]
    assert receipt["implied_by"] == "condition:branch" and receipt["affected_fields"] == ["h1"]
    assert valid_receipt(data, "condition:label", receipt, "h1")
    assert imply_label_receipts(data) == []  # Announced once, kept while the branch holds.
    assert "condition:label" in data["dialogue"]["answers"]


def test_a_withdrawn_branch_takes_the_implied_receipt_away():
    data = implied_session()
    imply_label_receipts(data)
    branch = data["dialogue"]["answers"]["condition:branch"]
    branch.update(action="CONDITION_FALSE", applies=False)
    branch["scope_validation"] = proof(target(data, "condition:branch", ["b1"]), branch)
    assert imply_label_receipts(data) == []
    assert "condition:label" not in data["dialogue"]["answers"]


def test_an_explicit_user_answer_on_the_label_is_never_replaced():
    data = implied_session()
    refused = {"action": "CONDITION_FALSE", "applies": False, "user_quote": "No"}
    data["dialogue"]["answers"]["condition:label"] = refused
    assert imply_label_receipts(data) == []
    assert data["dialogue"]["answers"]["condition:label"] == refused


def test_no_receipt_without_an_accepted_branch_or_on_the_previous_profile():
    data = implied_session()
    del data["dialogue"]["answers"]["condition:branch"]
    assert imply_label_receipts(data) == []
    data = implied_session()
    data.pop("dialogue_state_revision")
    assert imply_label_receipts(data) == []
    assert "condition:label" not in data["dialogue"]["answers"]


def test_a_person_proposal_is_not_freed_by_a_label_alone():
    data = implied_session(person=["label"])
    imply_label_receipts(data)
    assert data["dialogue"]["answers"]["condition:label"]["affected_fields"] == ["h1"]


def test_a_person_proposal_under_another_condition_too_stays_governed_by_it():
    data = implied_session(person=["label", "signatory"])
    imply_label_receipts(data)
    assert data["dialogue"]["answers"]["condition:label"]["affected_fields"] == ["h1", "h2"]


def chosen_option(revision=1):
    """The real capacity path with a second option under its own condition, the choice given."""
    import test_capacity_choice_question as capacity

    data, layout = capacity.capacity_case()
    if revision:
        data["dialogue_state_revision"] = revision
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    fields["p1.cb0"]["conditions"] = ["rival"]
    data["audit"]["conditions"]["rival"] = {
        **data["audit"]["conditions"]["company"], "form_evidence": {"quote": "Professionista"}}
    slot = capacity.slot_of(data)
    response = capacity.reply()
    record = {"action": "VALUE", "user_quote": response.user_quote, "provenance": "USER",
              "affected_fields": list(slot["field_ids"]), "value": response.value,
              "selected_options": response.selected_options,
              **capacity.scope.scope_receipt(data, capacity.KEY, slot["field_ids"], response)}
    for cid, chosen in capacity.user_choice(data, slot, response).items():
        data["dialogue"]["user_values"][cid] = {**chosen, "previous": None}
    data["dialogue"]["answers"][capacity.KEY] = record
    return capacity, data


def condition_answer(data, key, *, applies, quote, ids):
    reply = {"action": "CONDITION_TRUE" if applies else "CONDITION_FALSE", "applies": applies,
             "user_quote": quote, "provenance": "USER"}
    data["dialogue"]["answers"]["condition:" + key] = {
        **reply, "affected_fields": ids,
        "scope_validation": proof(target(data, "condition:" + key, ids), reply)}


def test_a_no_about_another_option_leaves_the_explicit_choice_verified():
    capacity, data = chosen_option()
    assert capacity_choice_valid(data, capacity.CID)
    condition_answer(data, "rival", applies=False, quote="No", ids=["p1.cb0"])
    assert capacity_choice_valid(data, capacity.CID)
    assert "choice:form_capacity_0" not in [q["key"] for q in question_pool(data)]


def test_a_later_confirmation_of_its_own_branch_leaves_the_explicit_choice_verified():
    capacity, data = chosen_option()
    # An extension: another quote, destinations that never include the box itself.
    condition_answer(data, "company", applies=True, quote="Sì, anche questi", ids=["p4.s0"])
    assert capacity_choice_valid(data, capacity.CID)


def test_withdrawing_its_own_branch_still_voids_the_explicit_choice():
    capacity, data = chosen_option()
    condition_answer(data, "company", applies=False, quote="No", ids=["p4.s0"])
    assert not capacity_choice_valid(data, capacity.CID)


def test_the_previous_profile_keeps_voiding_the_choice_on_any_change():
    capacity, data = chosen_option(revision=None)
    condition_answer(data, "rival", applies=False, quote="No", ids=["p1.cb0"])
    assert not capacity_choice_valid(data, capacity.CID)


def test_no_question_about_a_branch_the_explicit_choice_closed():
    capacity, data = chosen_option()
    data["audit"]["fields"].append({
        "candidate_id": "p9.s0", "conditions": ["rival"], "validation": "GROUNDED_PROPOSAL",
        "label": "Sede dello studio", "form_evidence": {"quote": "sede"}, "fact_id": "x"})
    assert "condition:rival" not in [q["key"] for q in question_pool(data)]
    # Still a target for an explicit USER instruction, and asked if the choice no longer holds.
    assert "condition:rival" in [q["key"] for q in question_pool(data, all_targets=True)
                                 ] or capacity_choice_valid(data, capacity.CID)
    condition_answer(data, "company", applies=False, quote="No", ids=["p4.s0"])
    assert "condition:rival" in [q["key"] for q in question_pool(data)]


@pytest.mark.parametrize("quote", ["Per la sezione scelgo l'opzione 4.", "opzione n. 2",
                                   "Scelgo l'opzione numero 3"])
@pytest.mark.parametrize("kind", ["value", "applicability", "decision"])
def test_a_numbered_option_is_quoted_only_by_a_choice(quote, kind):
    reply = {"slot": 1, "action": "VALUE", "user_quote": quote}
    assert only_choices_quote_an_option([reply], session_with(kind=kind)) == []
    assert only_choices_quote_an_option([reply], session_with(kind="choice")) == [reply]
    assert only_choices_quote_an_option([reply], session_with(kind=kind, revision=None)) == [reply]


def test_other_quotes_are_untouched_by_the_rule_on_options():
    kept = {"slot": 1, "action": "VALUE", "user_quote": "Il sottoscrittore è Ada Neri."}
    assert only_choices_quote_an_option([kept], session_with(kind="value")) == [kept]


@pytest.mark.parametrize(("answer", "expected"), [
    ("è una voce (target 2), ma non posso", "è una voce, ma non posso"),
    ("il campo «Nome» (target 7) oppure il blocco (target da 8 a 14).",
     "il campo «Nome» oppure il blocco."),
    ("Nessun numero qui: sede in via Roma 2.", "Nessun numero qui: sede in via Roma 2."),
])
def test_the_user_never_reads_the_routers_numbering(answer, expected):
    assert without_target_numbers(answer) == expected


def test_a_question_written_afterwards_is_hidden_from_the_second_reading():
    context = {"question": {"slots": [{"slot": 1}]}, "enabled": True, "conversation_data": {}}
    assert intents.routing_context(unseen_question(context))["slots"] == []
    assert context["question"], "the session itself is not changed"


def test_a_title_above_every_field_is_no_clause_either():
    data = form_data(quote="DOMANDA DI ISCRIZIONE ALL'ELENCO DI PROFESSIONISTI")
    data["catalog"]["candidates"] = {"p7.s0": {"slot_context": {"before": "con sede in "}},
                                     "p9.s0": {"slot_context": {"before": "denominazione "}}}
    item = data["audit"]["conditions"]["label"]
    item["form_evidence"]["paragraph_id"] = "paragraph:2"
    for field, cid in zip(data["audit"]["fields"], ["p7.s0", "p9.s0"]):
        field["candidate_id"] = cid
    entries = pool()
    entries[0]["field_ids"], entries[1]["field_ids"] = ["p9.s0"], ["p7.s0"]
    assert [q["key"] for q in hide_labels_under_open_branch(data, entries)] == ["condition:branch"]
    item["form_evidence"]["paragraph_id"] = "paragraph:8"  # Below a field: it may be a clause.
    assert len(hide_labels_under_open_branch(data, entries)) == 2


def test_a_branch_declared_as_legal_type_answers_its_label_too():
    data = implied_session()
    data["audit"]["conditions"]["branch"]["aspect"] = "legal_type"
    receipt = data["dialogue"]["answers"]["condition:branch"]
    receipt["scope_validation"] = proof(target(data, "condition:branch", ["b1"]), receipt)
    assert imply_label_receipts(data) == ["dell'operatore economico"]


def test_an_abbreviation_in_a_reference_to_the_law_is_one_sentence():
    message = ("Sì, si applica: rappresentante (art. 66, comma 1, lett. b D. Lgs. n. 36/2023) "
               "o di società (art.66, lett. c D.lgs.). Grazie mille a tutti.")
    assert sentences(message) == [
        "Sì, si applica: rappresentante (art. 66, comma 1, lett. b D. Lgs. n. 36/2023) "
        "o di società (art.66, lett. c D.lgs.).", "Grazie mille a tutti."]


@pytest.mark.parametrize(("quote", "name"), [
    ("metti leonardo rossi nato a lecce", "leonardo rossi"),
    ("scusa puoi inserire Ada Neri nata a Bari", "Ada Neri"),
    ("Il sottoscritto è Ada Neri, nata a Bari", "Ada Neri"),
])
def test_a_command_never_enters_the_name_field(quote, name):
    frame_ = {**frame(), "trim_role": True}
    assert extract(frame_, quote)["values"]["n"]["value"] == name


@pytest.mark.parametrize("value", ["metti leonardo rossi", "scusa Ada Neri", "tutti i dati"])
def test_a_phrase_is_not_a_name(value):
    assert not simple_name(value)


def replies_prepared(recorded, value, quote):
    frame_ = {**frame(), "trim_role": True, "recorded": recorded}
    reply = chat.ClarificationReply(slot=1, action="VALUE", value=value, user_quote=quote)
    [changed], _ = prepare({"1": frame_}, [reply], quote)
    return changed.value


def test_the_same_person_keeps_the_recorded_spelling():
    assert replies_prepared("Ada Neri", "ada neri", "metti ada neri") == "Ada Neri"
    assert replies_prepared("Ada Neri", "Ada Neri", "metti ada neri nata a Bari") == "Ada Neri"
    assert replies_prepared(None, "Ada Neri", "metti ada neri nata a Bari") == "Ada Neri"
    assert replies_prepared("Ada Neri", "Eva Blu", "Eva Blu") == "Eva Blu"  # Another person.


PERSON_MESSAGE = "scusa puoi mettere tutti i dati di Ada Neri nel sottoscritto ?"


def person_context(s, recorded=None):
    context = chat.planner_context(s)
    data = context["conversation_data"]
    if recorded:
        data["dialogue"].setdefault("user_values", {})[active_signatory(s)["field_ids"][0]] = {
            "value": recorded, "user_quote": recorded, "provenance": "USER"}
    return context


@pytest.mark.anyio
async def test_a_person_request_with_no_name_recorded_writes_the_name_only(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    signer = active_signatory(s)
    plan = {"intent": "explain", "answer": "Quale sezione?", "target": "source", "queries": []}
    routed = route_person_request(plan, person_context(s), PERSON_MESSAGE)
    assert routed["intent"] == "edit_fields"
    assert routed["edits"] == [{"target": signer["target"], "action": "VALUE", "value": "Ada Neri",
                                "user_quote": PERSON_MESSAGE}]


@pytest.mark.anyio
async def test_a_person_request_about_another_person_is_no_correction_made_here(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    plan = {"intent": "explain", "answer": "Il sottoscritto è un altro.", "target": "source"}
    assert route_person_request(plan, person_context(s, "Eva Blu"), PERSON_MESSAGE) == plan


@pytest.mark.anyio
async def test_a_person_request_on_the_previous_profile_is_left_to_the_router(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    context = person_context(s)
    context["conversation_data"] = {**context["conversation_data"]}
    context["conversation_data"].pop("dialogue_state_revision", None)
    plan = {"intent": "explain", "answer": "Quale sezione?", "target": "source"}
    assert route_person_request(plan, context, PERSON_MESSAGE) == plan


def recorded_person(monkeypatch, answers):
    from app import compilation_conversation as conversation

    monkeypatch.setattr(conversation, "person_groups", lambda data: {"n": {"n", "b1", "b2"}})
    monkeypatch.setattr(conversation, "fields", lambda data: {"n": {"label": "Il sottoscritto"}})
    monkeypatch.setattr(conversation, "targets", lambda data: [
        {"target": 1, "key": "field:n", "kind": "value", "field_ids": ["n"]},
        {"target": 2, "key": "condition:firm", "kind": "applicability",
         "field_ids": ["n", "b1", "b2"]},
        {"target": 3, "key": "condition:ramo", "kind": "applicability",
         "field_ids": ["b1", "x", "y"]}])
    return {"conversation_data": {
        "dialogue_state_revision": 1, "conversation_revision": 1, "catalog": {"candidates": {}},
        "dialogue": {"answers": answers, "user_values": {"n": {"value": "Ada Neri"}}}}}


def test_a_person_request_with_the_name_recorded_confirms_what_is_still_open(monkeypatch):
    plan = {"intent": "edit_fields", "edits": [
        {"target": 1, "action": "VALUE", "value": "ada neri", "user_quote": PERSON_MESSAGE}]}
    routed = route_person_request(plan, recorded_person(monkeypatch, {}), PERSON_MESSAGE)
    assert routed["edits"] == [{"target": 2, "action": "CONDITION_TRUE",
                                "user_quote": PERSON_MESSAGE}]


def test_a_person_request_with_nothing_left_to_confirm_says_so_and_changes_nothing(monkeypatch):
    answers = {"condition:firm": {"applies": True, "affected_fields": ["n", "b1", "b2"]},
               "condition:ramo": {"applies": True, "affected_fields": ["b1", "x", "y"]}}
    plan = {"intent": "edit_fields", "edits": [
        {"target": 1, "action": "VALUE", "value": "Ada Neri", "user_quote": PERSON_MESSAGE}]}
    routed = route_person_request(plan, recorded_person(monkeypatch, answers), PERSON_MESSAGE)
    assert routed["intent"] == "explain" and "è già Ada Neri" in routed["answer"]


def test_a_person_request_keeps_the_rest_of_the_message(monkeypatch):
    other = {"target": 3, "action": "SKIP", "user_quote": "Rinvia il ramo."}
    message = f"Rinvia il ramo.\n{PERSON_MESSAGE}"
    plan = {"intent": "edit_fields", "edits": [other]}
    routed = route_person_request(plan, recorded_person(monkeypatch, {}), message)
    assert routed["edits"] == [other, {"target": 2, "action": "CONDITION_TRUE",
                                       "user_quote": PERSON_MESSAGE}]


@pytest.mark.parametrize("message", ["Metti tutti i dati nel modulo.",
                                     "Compila anche quella parte con i dati della KB."])
def test_a_request_with_no_person_or_section_is_not_a_person_request(message):
    assert not PERSON_REQUEST.search(message)


@pytest.mark.parametrize("message", [
    "metti i dati di Ada Neri nel firmatario",
    "usa i dati anagrafici di Ada Neri per il sottoscritto",
    "inserisci i dati di Ada Neri nella sezione del sottoscritto", PERSON_MESSAGE])
def test_natural_wordings_of_a_person_request(message):
    assert PERSON_REQUEST.search(message)["name"] == "Ada Neri"


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
async def test_the_second_reading_cannot_answer_a_question_the_user_has_not_seen(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    condition = condition_target(s)
    deferral = {"slot": 1, "action": "SKIP",
                "user_quote": "Sì, confermo che partecipiamo come società di ingegneria."}
    s2, text, _, calls = await rest_flow(s, monkeypatch, MESSAGE, [
        {"intent": "answer_fields", "replies": [REPLY], "edits": []},
        {"intent": "answer_fields", "replies": [deferral], "edits": []},
        {"intent": "answer_fields", "replies": [deferral], "edits": []}])
    assert len(calls) == 3  # The router saw no slot: its answer is refused, then dropped.
    d = s2["global_compilation"]["dialogue"]
    assert condition["key"] not in d["answers"] and not d.get("excluded_fields")
    assert "Non ho registrato questa parte del messaggio" in text


@pytest.mark.anyio
async def test_deferring_an_extension_keeps_the_confirmation_already_given(
    api, provider, monkeypatch,
):
    from app.compilation_global_dialogue import question_pool as pool_of
    from app.compilation_scope_review import blocked_source_fields, session_data
    from app.db import connection

    s = await analyzed(api, monkeypatch)
    condition = condition_target(s)
    quote = "Sì, confermo che partecipiamo come società di ingegneria."
    s, _, _, _ = await rest_flow(s, monkeypatch, quote, [{"intent": "edit_fields", "edits": [
        {"target": condition["target"], "action": "CONDITION_TRUE", "user_quote": quote}]}])
    key = condition["key"]
    with connection() as db:  # As after a later derivation: the receipt showed fewer destinations.
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        data = state["global_compilation"]
        receipt = data["dialogue"]["answers"][key]
        ids = receipt["affected_fields"]
        assert len(ids) > 1
        receipt["affected_fields"] = ids[:1]
        receipt["scope_validation"] = proof(target(data, key, ids[:1]), receipt)
        [slot] = [q for q in pool_of(data) if q["key"] == key]
        assert slot.get("extension")
        data["dialogue"].update(phase="READY", question={
            "kind": "clarifications", "field_ids": [], "message": slot["question"],
            "slots": [{**slot, "slot": 1}]})
        s = sessions.save_state(db, row, state, "test_state")
    s2, text, _, _ = await rest_flow(s, monkeypatch, "Rinvio questi dati.", [
        {"intent": "answer_fields", "edits": [],
         "replies": [{"slot": 1, "action": "SKIP", "user_quote": "Rinvio questi dati."}]}])
    data = session_data(s2)
    kept = data["dialogue"]["answers"][key]
    assert kept["applies"] is True and kept["user_quote"] == quote
    assert kept["extension_deferred"] == ids[1:] and kept["affected_fields"] == ids[:1]
    assert set(data["dialogue"]["excluded_fields"]) == set(ids[1:])
    assert ids[0] not in blocked_source_fields(data)
    assert key not in [q["key"] for q in pool_of(data)]  # Not asked again.
    assert "i dati collegati" in text


@pytest.mark.anyio
async def test_a_numbered_option_with_no_choice_open_is_not_written_anywhere(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    signer = active_signatory(s)

    async def model(client, settings, body, timeout, **kwargs):
        return json.dumps({"answer": "", "queries": [], "target": "form", "intent": "edit_fields",
                           "edits": [{"target": signer["target"], "action": "VALUE",
                                      "value": "4", "user_quote": "Scelgo l'opzione 4."}]}), "s", {}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        planned = await intents.plan_chat_turn("Scelgo l'opzione 4.", [],
                                               compilation=chat.planner_context(s))
    assert not getattr(planned.decision, "replies", None)
    assert "Non ho ancora registrato l'opzione" in planned.decision.answer


@pytest.mark.anyio
async def test_the_rule_on_documented_data_of_a_person_reaches_the_guard_of_this_profile_only(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    condition = condition_target(s)
    quote = "Metti tutti i dati di Ada Neri nel sottoscritto."
    seen = []

    async def model(client, settings, body, timeout, **kwargs):
        if kwargs["response_schema"]["title"] == "FormScopeChecks":
            seen.append(body["messages"][0]["content"])
            return json.dumps(verdicts(body, identified=True, fixed=None)), "s", {}
        return json.dumps({"answer": "", "queries": [], "target": "form", "intent": "edit_fields",
                           "edits": [{"target": condition["target"], "action": "CONDITION_TRUE",
                                      "user_quote": quote}]}), "s", {}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        context = chat.planner_context(s)
        await intents.plan_chat_turn(quote, [], compilation=context)
        context["conversation_data"] = {**context["conversation_data"]}
        context["conversation_data"].pop("dialogue_state_revision", None)
        await intents.plan_chat_turn(quote, [], compilation=context)
    assert [PERSON_REQUEST_RULE in text for text in seen] == [True, False]


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
