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

