"""A bounded second look at already grounded role evidence never releases a hold itself."""
from copy import deepcopy

import pytest
from test_compilation_hold_rereview import HELD, empty_context, window_data
from test_compilation_resilient_segments import form_docx

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_hold_rereview as rereview
from app.docx_templates import inspect_docx

ROW = "| Persona Demo | Ingegnere | 40% |"
TITLE = "Soci della società"
CONTRAST = "Il ruolo aziendale non equivale a una nomina per un diverso incarico."


def source_data(revision=2):
    data = window_data()
    data.update(hold_rereview_revision=revision, writable_ids=list(data["catalog"]["candidates"]))
    data["audit"]["facts"] = {"f": {"subject": "Persona Demo", "entity": "person",
                                     "validation": "GROUNDED_PROPOSAL"}}
    data["audit"]["bindings"] = {"b": {"required_role": "socio", "source_role": "socio",
        "validation": "GROUNDED_PROPOSAL", "form_evidence": {"quote": "Soci"},
        "source_evidence": [{"quote": TITLE, "role": "source"}]}}
    field = data["audit"]["fields"][0]
    field.update(validation="GROUNDED_PROPOSAL", value="ABC123", disposition="value", kind="data",
        fact_id="f", form_evidence={"paragraph_id": "paragraph:0", "quote": "Dato 0"},
        subject_binding={"binding_id": "b", "result": "literal_match", "validation_errors": [],
            "record_attributions": [{"subject": "Persona Demo", "title": TITLE,
                                     "header": "Persona | Ruolo | Quota", "row": ROW}],
            "source_evidence": [{"quote": ROW, "role": "source"}]})
    return data


def source_plan(quote):
    return dialogue.ContinuationPlan(held_proposal_slots=[1], hold_reviews=[
        dialogue.ProposalHoldReview(proposal_slot=1, blocker="source", reason="Ruolo da verificare",
            evidence_quote=quote, missing_information="Prova del ruolo di socio")])


def update(data, quote):
    context = empty_context(["ABC123"])
    context["document_values"][0]["source_quote"] = quote
    return dialogue._hold_updates(data, [{"candidate_id": HELD, "selectable": True}], context,
                                  source_plan(quote), "review-1", pool=[])


@pytest.mark.parametrize("quote", [ROW, CONTRAST])
@pytest.mark.parametrize("revision", [1, 2])
def test_bound_source_role_can_be_rereviewed_once_only_in_the_new_revision(quote, revision):
    data = source_data(revision)
    result = update(data, quote)
    assert result["held_candidate_ids"] == [HELD]  # Never automatically released.
    assert (result["hold_records"][HELD].get("rereview") == "pending") is (revision == 2)


def pending_data():
    data = source_data()
    data["dialogue"].update(update(data, ROW))
    data["dialogue"].update(phase="READY", reviewed_candidate_ids=[HELD])
    return data


@pytest.mark.parametrize("keep", [False, True])
def test_the_narrator_can_release_or_keep_the_hold_but_only_once(keep):
    data = pending_data()
    assert rereview.due(data) == {HELD}
    assert dialogue.export_selection({"global_compilation": {
        **data, "fields": adapter.review_fields(data)}})[0] == []
    note = rereview.context_note(data, HELD)
    assert note["source_records"][0]["title"] == TITLE
    assert note["source_records"][0]["row"] == ROW
    context = empty_context(["ABC123"])
    context["document_values"][0]["source_quote"] = ROW
    result = dialogue._hold_updates(data, [{"candidate_id": HELD, "selectable": True}], context,
        source_plan(ROW) if keep else dialogue.ContinuationPlan(), "review-2", pool=[])
    assert result["hold_records"][HELD]["rereview"] == "done"
    assert result["held_candidate_ids"] == ([HELD] if keep else [])
    data["dialogue"].update(result)
    assert not rereview.due(data)
    ids = dialogue.export_selection({"global_compilation": {
        **data, "fields": adapter.review_fields(data)}})[0]
    assert ids == ([] if keep else [HELD])
    assert update(data, ROW)["hold_records"][HELD]["rereview"] == "done"


@pytest.mark.parametrize("mutation", ["binding", "fact", "form", "condition", "user"])
def test_a_changed_proof_or_revoked_condition_cannot_reuse_the_pending_check(mutation):
    data = pending_data()
    if mutation == "binding":
        data["audit"]["bindings"]["b"]["source_role"] = "altro ruolo"
    elif mutation == "fact":
        data["audit"]["facts"]["f"]["subject"] = "Altra persona"
    elif mutation == "form":
        data["catalog"]["blocks"][0]["paragraphs"][0]["text"] += " Altro requisito"
    else:
        data["audit"]["fields"][0]["conditions"] = ["k"]
        if mutation == "user":
            data["dialogue"]["answers"]["condition:k"] = {"action": "CONDITION_FALSE",
                                                           "applies": False}
    assert not rereview.due(data)
    assert data["dialogue"]["held_candidate_ids"] == [HELD]


@pytest.mark.parametrize("case", ["review_required", "fact_rejected", "binding_rejected",
                                  "not_selectable", "another_blocker", "duplicate_record",
                                  "no_record", "another_role"])
def test_unproven_or_ambiguous_roles_are_not_marked_for_the_new_review(case):
    data = source_data()
    field = data["audit"]["fields"][0]
    proposal = {"candidate_id": HELD, "selectable": case != "not_selectable"}
    review = source_plan(ROW).hold_reviews[0].model_dump()
    # No role-name fallback: this test isolates the structured-record criterion.
    review["missing_information"] = "Prova documentale"
    if case == "review_required":
        field["subject_binding"]["result"] = "review_required"
    elif case == "fact_rejected":
        data["audit"]["facts"]["f"]["validation"] = "REJECTED"
    elif case == "binding_rejected":
        data["audit"]["bindings"]["b"]["validation_errors"] = ["Contraddizione"]
    elif case == "another_blocker":
        review["blocker"] = "form"
    elif case == "duplicate_record":
        field["subject_binding"]["record_attributions"] *= 2
    elif case == "no_record":
        field["subject_binding"]["record_attributions"] = []
    elif case == "another_role":
        data["audit"]["bindings"]["b"]["source_role"] = "dipendente"
    assert rereview.source_check(data, proposal, review) is None


def test_a_bad_reference_in_the_second_review_keeps_the_hold():
    data = pending_data()
    result = dialogue._hold_updates(data, [{"candidate_id": HELD, "selectable": True}],
        empty_context(["ABC123"]), dialogue.ContinuationPlan(), "review-2", pool=[],
        irregular={"invalid_references": [{"proposal_slot": 99}], "repeated_references": {}})
    assert result["held_candidate_ids"] == [HELD]
    assert result["hold_records"][HELD]["rereview"] == "done"


def test_existing_revision_one_and_old_sessions_keep_their_profile(monkeypatch):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_HOLD_REREVIEW_REVISION", "2")
    assert adapter.initial_state(inspect_docx(form_docx(3)))["hold_rereview_revision"] == 2
    assert not rereview.source_check(source_data(1), {"candidate_id": HELD, "selectable": True},
                                    source_plan(ROW).hold_reviews[0].model_dump())
    data = deepcopy(source_data())
    data.pop("hold_rereview_revision")
    assert not rereview.enabled(data)
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "2")
    assert "hold_rereview_revision" not in adapter.initial_state(inspect_docx(form_docx(3)))
