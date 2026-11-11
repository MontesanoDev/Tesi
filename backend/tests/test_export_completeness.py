"""The first page of the FORM depends on no option below it, and each export stays in its place.

Real manual run: company data of the header were anchored by the model on the option «Libero
professionista singolo». The question made no sense, the USER's correct «no» excluded them and the
signatory's office was never derived, while the same data were written further down.
"""

import json
from copy import deepcopy

import pytest
from docx import Document
from test_checkbox_policy import export
from test_compilation_catalog import encoded, native_checkbox
from test_compilation_global_sessions import api, provider
from test_dialogue_state import (
    asserted_change,
    chosen_option,
    condition_answer,
    form_data,
    implied_session,
)

from app import compilation_chat as chat
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.compilation_branch_evidence import (
    incompatible_option_conditions,
    release_header_from_options,
)
from app.compilation_conversation import imply_label_receipts
from app.compilation_global import build_global_input
from app.compilation_global_dialogue import continuation_receipt, question_pool
from app.compilation_profile import SECTIONS
from app.compilation_scope_review import blocked_source_fields, proof, target
from app.docx_templates import inspect_docx

__all__ = ["api", "form_data", "implied_session", "provider"]
LABEL = "dell’operatore economico"
OPTIONS = ["Libero professionista singolo", "Legale rappresentante di società di ingegneria"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def form():
    """Header above the capacity heading, two options, data under the second, a section below."""
    doc = Document()
    doc.add_paragraph(f"Carica ________ {LABEL} ________ con sede in ________")
    doc.add_paragraph("IN QUALITÀ DI")
    p = doc.add_paragraph()
    native_checkbox(p, legacy=False, checked=False)
    p.add_run(" " + OPTIONS[0])
    p = doc.add_paragraph()
    native_checkbox(p, legacy=False, checked=False)
    p.add_run(" " + OPTIONS[1])
    doc.add_paragraph("Denominazione: ________")
    doc.add_paragraph("CHIEDE")
    doc.add_paragraph("Importo: ________")
    return build_global_input(inspect_docx(encoded(doc)), "alpha", [])["form"]


def audit_on(anchor, *conditions, quote=OPTIONS[0], fields=None):
    catalog = form()
    fields = fields or {"p0.s0": conditions, "p0.s1": conditions, "p0.s2": conditions}
    return catalog, {
        "conditions": {
            "opt": {"form_evidence": {"paragraph_id": anchor, "quote": quote}, "reason": "Modello",
                    "aspect": "legal_type", "applies_to": sorted(fields), "result": "unknown",
                    "scope": [{"kind": "candidate", "id": c} for c in fields],
                    "form_clause": {"label": "x"}},
            "label": {"form_evidence": {"paragraph_id": "paragraph:0", "quote": LABEL},
                      "aspect": "participation", "result": "unknown", "reason": "Etichetta"}},
        "fields": [{"candidate_id": c, "conditions": list(keys),
                    "condition_checks": {k: {"result": "unknown"} for k in keys}}
                   for c, keys in fields.items()]}


def conditions_of(audit):
    return {f["candidate_id"]: f["conditions"] for f in audit["fields"]}


def test_a_destination_above_the_options_keeps_only_its_other_conditions():
    catalog, audit = audit_on("paragraph:2", "opt", "label")
    result = release_header_from_options(audit, catalog)
    assert conditions_of(result) == {"p0.s0": ["label"], "p0.s1": ["label"], "p0.s2": ["label"]}
    assert result["capacity_anchor"]["detached"]["opt"] == ["p0.s0", "p0.s1", "p0.s2"]
    assert result["conditions"]["opt"]["applies_to"] == []
    assert all("opt" not in f["condition_checks"] for f in result["fields"])


def test_with_no_other_condition_the_gate_moves_onto_its_own_line_and_stays():
    catalog, audit = audit_on("paragraph:2", "opt")
    result = release_header_from_options(audit, catalog)
    assert set(map(tuple, conditions_of(result).values())) == {("opt__sopra",)}
    derived = result["conditions"]["opt__sopra"]
    assert derived["form_evidence"] == {"paragraph_id": "paragraph:0", "quote": "Carica"}
    assert derived["derived_from"] == "opt" and "form_clause" not in derived
    assert derived["aspect"] == "participation"
    assert result["capacity_anchor"]["moved"]["opt"] == ["p0.s0", "p0.s1", "p0.s2"]
    assert all(f["condition_checks"] == {"opt__sopra": {"result": "unknown"}}
               for f in result["fields"])


def test_the_right_option_loses_the_header_too_the_data_below_it_stay():
    catalog, audit = audit_on("paragraph:3", "opt", "label", fields={
        "p0.s0": ("opt", "label"), "p4.s0": ("opt",), "p6.s0": ("opt",)})
    result = release_header_from_options(audit, catalog)
    assert conditions_of(result) == {"p0.s0": ["label"], "p4.s0": ["opt"], "p6.s0": ["opt"]}
    assert result["conditions"]["opt"]["applies_to"] == ["p4.s0", "p6.s0"]


@pytest.mark.parametrize("anchor", ["paragraph:0", "paragraph:6", "paragraph:99"])
def test_a_condition_not_anchored_on_an_option_is_untouched(anchor):
    catalog, audit = audit_on(anchor, "opt")
    before = deepcopy(audit)
    assert release_header_from_options(audit, catalog) == before


def test_a_form_with_no_capacity_region_is_untouched():
    doc = Document()
    doc.add_paragraph("Denominazione: ________")
    p = doc.add_paragraph()
    native_checkbox(p, legacy=False, checked=False)
    p.add_run(" Accetto")
    catalog = build_global_input(inspect_docx(encoded(doc)), "alpha", [])["form"]
    audit = {"conditions": {"opt": {"form_evidence": {"paragraph_id": "paragraph:1", "quote": "x"},
                                    "result": "unknown"}},
             "fields": [{"candidate_id": "p0.s0", "conditions": ["opt"]}]}
    before = deepcopy(audit)
    assert release_header_from_options(audit, catalog) == before


def test_a_rejected_condition_is_not_moved():
    catalog, audit = audit_on("paragraph:2", "opt")
    audit["conditions"]["opt"]["validation_errors"] = ["Errore"]
    before = deepcopy(audit)
    assert release_header_from_options(audit, catalog) == before


def session_on(*conditions):
    """Real scope proofs on the moved audit: the USER's correct «no» must not exclude the header."""
    catalog, audit = audit_on("paragraph:2", *conditions)
    data = {"export_completeness_revision": 1, "dialogue_state_revision": 1, "catalog": catalog,
            "audit": release_header_from_options(audit, catalog), "writable_ids": [],
            "generation_revision": 3, "dialogue": {"answers": {}, "user_values": {}}}
    for f in data["audit"]["fields"]:
        f.update(label=f["candidate_id"], form_evidence={"quote": "q"})
    return data


def test_a_no_on_the_incompatible_option_no_longer_reaches_the_header():
    data = session_on("opt", "label")
    reply = {"action": "CONDITION_FALSE", "applies": False, "user_quote": "No",
             "provenance": "USER"}
    data["dialogue"]["answers"]["condition:opt"] = {
        **reply, "affected_fields": ["p2.cb0"],
        "scope_validation": proof(target(data, "condition:opt", ["p2.cb0"]), reply)}
    yes = {"action": "CONDITION_TRUE", "applies": True, "user_quote": "Sì", "provenance": "USER"}
    ids = ["p0.s0", "p0.s1", "p0.s2"]
    data["dialogue"]["answers"]["condition:label"] = {
        **yes, "affected_fields": ids,
        "scope_validation": proof(target(data, "condition:label", ids), yes)}
    assert not set(ids) & blocked_source_fields(data)


def test_without_any_confirmation_the_header_stays_blocked():
    data = session_on("opt", "label")
    assert {"p0.s0", "p0.s1", "p0.s2"} <= blocked_source_fields(data)


def branch_session():
    """The moved header beside the accepted branch of the same company, real proofs."""
    catalog, audit = audit_on("paragraph:3", "opt", fields={
        "p0.s0": ("opt",), "p0.s1": ("opt",), "p4.s0": ("opt",)})
    audit["facts"] = {"f": {"entity": "company", "subject": "Società A"}}
    for f in audit["fields"]:
        f.update(proposal={"fact_id": "f"}, label=f["candidate_id"], form_evidence={"quote": "q"},
                 validation="REVIEW_REQUIRED", proposal_grounding="GROUNDED_PROPOSAL")
    audit["conditions"]["opt"]["aspect"] = "representation"
    data = {"export_completeness_revision": 1, "dialogue_state_revision": 1, "catalog": catalog,
            "audit": release_header_from_options(audit, catalog), "writable_ids": [],
            "generation_revision": 3, "conversation_revision": 1,
            "dialogue": {"answers": {}, "user_values": {}}}
    moved = data["audit"]["conditions"]["opt__sopra"]
    assert moved["applies_to"] == ["p0.s0", "p0.s1"]
    data["catalog"]["candidates"]["p0.s0"]["slot_context"] = {
        "before": moved["form_evidence"]["quote"]}
    return data


def accept_branch(data, *, applies=True):
    reply = {"action": "CONDITION_TRUE" if applies else "CONDITION_FALSE", "applies": applies,
             "user_quote": "Sì" if applies else "No", "provenance": "USER"}
    data["dialogue"]["answers"]["condition:opt"] = {
        **reply, "affected_fields": ["p4.s0"],
        "scope_validation": proof(target(data, "condition:opt", ["p4.s0"]), reply)}


def test_the_moved_gate_is_answered_by_the_accepted_branch_and_the_header_is_released():
    data = branch_session()
    assert {"p0.s0", "p0.s1"} <= blocked_source_fields(data)
    assert imply_label_receipts(data) == []  # No branch yet: nothing is implied.
    accept_branch(data)
    assert imply_label_receipts(data)
    receipt = data["dialogue"]["answers"]["condition:opt__sopra"]
    assert receipt["implied_by"] == "condition:opt"
    assert receipt["affected_fields"] == ["p0.s0", "p0.s1"]
    assert not {"p0.s0", "p0.s1"} & blocked_source_fields(data)


def test_a_denied_branch_answers_nothing_and_the_header_waits():
    data = branch_session()
    accept_branch(data, applies=False)
    assert imply_label_receipts(data) == []
    assert "condition:opt__sopra" not in data["dialogue"]["answers"]
    assert {"p0.s0", "p0.s1"} <= blocked_source_fields(data)


def closing_session():
    capacity_module, data = chosen_option()
    return capacity_module, data


def test_a_settled_region_closes_the_questions_on_its_other_options():
    module, data = closing_session()
    data["export_completeness_revision"] = 1
    data["audit"]["conditions"]["rival"]["form_evidence"]["paragraph_id"] = "paragraph:1"
    data["audit"]["conditions"]["company"]["form_evidence"]["paragraph_id"] = "paragraph:3"
    assert incompatible_option_conditions(data) == {"rival"}
    data["audit"]["fields"].append({
        "candidate_id": "p9.s0", "conditions": ["rival"], "validation": "GROUNDED_PROPOSAL",
        "label": "Sede", "form_evidence": {"quote": "sede"}, "fact_id": "x"})
    assert "condition:rival" not in [q["key"] for q in question_pool(data)]
    # An explicit USER instruction still reaches it, and only the question was closed.
    assert "condition:rival" in [q["key"] for q in question_pool(data, all_targets=True)]
    assert "p9.s0" in blocked_source_fields(data)
    data["dialogue"]["requested_keys"] = ["condition:rival"]
    assert "condition:rival" in [q["key"] for q in question_pool(data)]


def test_withdrawing_the_decision_reopens_them():
    module, data = closing_session()
    data["export_completeness_revision"] = 1
    data["audit"]["conditions"]["rival"]["form_evidence"]["paragraph_id"] = "paragraph:1"
    data["audit"]["conditions"]["company"]["form_evidence"]["paragraph_id"] = "paragraph:3"
    condition_answer(data, "company", applies=False, quote="No", ids=["p4.s0"])
    data["dialogue"]["answers"].pop(module.KEY)
    assert incompatible_option_conditions(data) == set()


def test_the_previous_profile_keeps_asking():
    _, data = closing_session()
    data["audit"]["conditions"]["rival"]["form_evidence"]["paragraph_id"] = "paragraph:1"
    assert incompatible_option_conditions(data) == set()


def test_one_clause_confirmed_twice_in_a_message_is_said_once():
    accepted = [{"action": "CONDITION_TRUE", "label": "Nota", "form_clause":
                 "La quale ha come Direttore Tecnico"},
                {"action": "CONDITION_TRUE", "label": "Nota", "form_clause":
                 "la quale ha come Direttore Tecnico."},
                {"action": "CONDITION_TRUE", "label": "Nota", "form_clause": "Altra clausola"}]
    text = continuation_receipt({"latest_turn": {"accepted": accepted}})
    assert text.count("irettore Tecnico") == 1
    assert "La quale ha come Direttore Tecnico; Altra clausola" in text


def test_both_receipts_stay_though_said_once():
    first = {"action": "CONDITION_TRUE", "label": "Nota", "form_clause": "Clausola",
             "user_quote": "Sì"}
    second = {**first, "user_quote": "Confermo"}
    latest = {"accepted": [first, second]}
    continuation_receipt({"latest_turn": latest})
    assert [r["user_quote"] for r in latest["accepted"]] == ["Sì", "Confermo"]


def test_this_profile_is_opt_in_for_new_sessions():
    assert SECTIONS["export_completeness_revision"] == 1


@pytest.mark.parametrize(("floor", "turn_id", "action", "kept"), [
    (7, 7, "updated", True),   # The stored turn is complete; this text belongs to the next one.
    (7, 8, "updated", False),  # Its own narration, finished after it was stored.
    (None, 7, "start", False),
])
def test_a_turn_is_not_rewritten_with_the_text_of_the_following_message(
    floor, turn_id, action, kept, monkeypatch,
):
    class Db:
        updates = []

        def execute(self, sql, params):
            if sql.startswith("UPDATE"):
                self.updates.append(params)
                return None

            class Cursor:
                def fetchone(self):
                    return {"id": turn_id, "answer": "Originale",
                            "compilation_json": json.dumps({"session_id": "s", "action": action})}
            return Cursor()

    state = {"engine": "global", "global_compilation": {
        "answered_after_turn": floor, "dialogue": {"phase": "READY", "message": "Testo nuovo"}}}
    monkeypatch.setattr(chat, "chat_view", lambda s: {
        "enabled": True, "auto_continue": False, "paused": False, "question": None})
    db = Db()
    chat.retain_compilation_question(db, {"conversation_id": "c", "id": "s"}, state)
    assert db.updates == ([] if kept else [("Testo nuovo", turn_id)])


async def exported_twice(api, monkeypatch, revision):
    from app.compilation_chat import ChatControl
    from app.db import connection
    from app.intents import ChatDecision

    doc = Document()
    doc.add_paragraph("Il firmatario è ________")
    _, s = await export(api, monkeypatch, doc)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        state["global_compilation"]["dialogue_state_revision"] = 1
        if not revision:  # New sessions carry the flag from the profile.
            state["global_compilation"].pop("export_completeness_revision", None)
        s = sessions.save_state(db, row, state, "test_state")
    s = await asserted_change(s)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        state["global_compilation"]["dialogue"]["latest_turn"] = {"accepted": []}
        s = sessions.save_state(db, row, state, "test_state")
    finish = ChatDecision(action="compilation_control", answer="", queries=[], target="form",
                          control=ChatControl(kind="finish", user_quote="Bozza"))
    _, command = await adapter.handle_chat_action(s, finish, s["version"], "Bozza")
    s = sessions.get_session("alpha", s["id"])
    with connection() as db:  # The stored state: the public view omits the last turn.
        _, state = adapter._row_state(db, "alpha", s["id"], s["version"])
    return s, command, state["global_compilation"]["dialogue"]


@pytest.mark.anyio
async def test_an_export_names_its_draft_and_closes_what_it_now_contains(
    api, provider, monkeypatch,
):
    s, command, stored = await exported_twice(api, monkeypatch, 1)
    assert command["action"] == "generated"
    assert command["generation_id"] == s["last_generation"]["id"]
    assert stored["latest_turn"] is None


@pytest.mark.anyio
async def test_the_previous_profile_keeps_its_last_turn(api, provider, monkeypatch):
    _, _, stored = await exported_twice(api, monkeypatch, 0)
    assert stored["latest_turn"] == {"accepted": []}


def test_the_draft_summary_invites_no_confirmation_of_an_option_not_chosen():
    from app.compilation_global_dialogue import unexported_notice

    _, data = closing_session()
    data["export_completeness_revision"] = 1
    data["audit"]["conditions"]["rival"]["form_evidence"]["paragraph_id"] = "paragraph:1"
    data["audit"]["conditions"]["company"]["form_evidence"]["paragraph_id"] = "paragraph:3"
    data["audit"]["fields"].append({
        "candidate_id": "p9.s0", "conditions": ["rival"], "validation": "GROUNDED_PROPOSAL",
        "label": "Sede dello studio", "form_evidence": {"quote": "sede"}, "fact_id": "x"})
    text = unexported_notice(data, set())
    assert "1 dati trovati nelle fonti (Sede dello studio) riguardano un'altra opzione" in text
    assert "aspettano la tua conferma su «Professionista»" not in text
    data.pop("export_completeness_revision")
    assert "aspettano la tua conferma su «Professionista»" in unexported_notice(data, set())
