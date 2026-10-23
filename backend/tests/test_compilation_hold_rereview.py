"""Rev 3 candidate, offline: a hold citing another condition's clause gets one re-review.

Counterexample recorded in the candidate campaign (minervino-2): 21 partner proposals held
with the clause of the technical-director condition, which governs other destinations.
The unanchored hold had no blocker, hence no way out for the rest of the session.
"""

import json
from copy import deepcopy

import pytest
import test_compilation_resilient_segments as rev2
from test_compilation_global_sessions import api, provider
from test_compilation_p3_hold_validation import SUMMARY, hold, narrator

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_chat import ClarificationReply
from app.compilation_hold_rereview import NOTE, due, enabled, foreign_condition
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]

HELD, GOVERNED, CLAUSE = "p0.s0", "p10.s0", "Dato 10"


@pytest.fixture(autouse=True)
def candidate_runtime(monkeypatch):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    monkeypatch.setenv("MAPI_DERIVATION_REVISION", "1")
    monkeypatch.setenv("MAPI_HOLD_REREVIEW_REVISION", "1")


def two_proposals(inp, ids):
    """A free value and a value under an open condition anchored to a distant paragraph."""
    condition = rev2.condition(inp, "paragraph:10", CLAUSE,
                               scope=[{"kind": "candidate", "id": GOVERNED}])
    return json.dumps(rev2.envelope(inp, {HELD: rev2.slot(inp, HELD),
                                          GOVERNED: rev2.slot(inp, GOVERNED, conditions=["k"])},
                                    conditions={"k": condition}))


async def held_session(api, monkeypatch, *later):
    """First summary holds the free value citing the other condition's clause."""
    seen = narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [
        hold([1], CLAUSE, "applicability")]}, *later)
    session = await rev2.started(api, monkeypatch, rev2.form_docx(12),
                                 rev2.Model({0: [two_proposals], 1: [two_proposals]}))
    response = await rev2.analyze(api, session)
    assert response.status_code == 200, response.text
    return response.json(), seen


def defer_condition(session):
    """Any USER turn triggers the next narration; the condition itself stays deferred."""
    slot = next(s for s in session["chat"]["question"]["slots"] if s["key"] == "condition:k")
    quote = "Rinvia questo punto e lascialo vuoto."
    session, errors = dialogue.apply_replies("alpha", session["id"], session["version"], [
        ClarificationReply(slot=slot["slot"], action="SKIP", user_quote=quote)], quote)
    assert not errors
    return session


def records(session):
    return session["global_compilation"]["dialogue"]["hold_records"]


def held(session):
    return session["global_compilation"]["dialogue"]["held_candidate_ids"]


@pytest.mark.anyio
async def test_the_misattribution_is_proved_and_the_hold_waits_for_one_rereview(
    api, provider, monkeypatch,
):
    session, seen = await held_session(api, monkeypatch, {"questions": []})
    record = records(session)[HELD]
    assert held(session) == [HELD]
    assert (record["reason_validation"], record["quote_location"]) == (
        "UNANCHORED_QUOTE", "question_pool")
    assert (record["misattributed_condition"], record["rereview"]) == ("k", "pending")
    assert "blocker_key" not in record
    assert HELD not in dialogue.export_selection(session)[0]  # Still held: no backend release.
    session = await rev2.analyze(api, defer_condition(session))
    session = session.json()
    value = next(v for v in seen[-1]["document_values"] if v["previous_hold"])
    assert value["previous_hold"]["backend_check"] == NOTE
    assert held(session) == []
    record = records(session)[HELD]
    assert (record["release_reason"], record["rereview"]) == ("MODEL_REREVIEW", "done")
    assert session["global_compilation"]["dialogue"]["hold_transition"][
        "released_model_rereview"] == [HELD]
    ids = dialogue.export_selection(session)[0]
    assert HELD in ids and GOVERNED not in ids  # The other condition's gate is unchanged.
    assert (await rev2.draft(api, session, ids)).status_code == 200
    refused = await rev2.draft(api, session, [*ids, GOVERNED])
    assert refused.status_code == 409


@pytest.mark.anyio
async def test_held_again_at_its_rereview_it_stays_held_for_good(api, provider, monkeypatch):
    again = {"questions": [], "hold_groups": [hold([1], CLAUSE, "applicability")]}
    session, seen = await held_session(api, monkeypatch, again, {"questions": []})
    session = (await rev2.analyze(api, defer_condition(session))).json()
    assert held(session) == [HELD] and records(session)[HELD]["rereview"] == "done"
    # A further narration no longer offers it: no loop of re-reviews.
    data = deepcopy(rev2.state_of(session)["global_compilation"])
    assert not due(data) and HELD not in {f["candidate_id"] for f in dialogue._review_window(data)}
    assert HELD not in dialogue.export_selection(session)[0]


@pytest.mark.anyio
async def test_without_the_flag_the_unanchored_hold_is_inherited_as_before(
    api, provider, monkeypatch,
):
    monkeypatch.delenv("MAPI_HOLD_REREVIEW_REVISION")
    session, seen = await held_session(api, monkeypatch, {"questions": []})
    assert "hold_rereview_revision" not in session["global_compilation"]
    assert "rereview" not in records(session)[HELD]
    session = (await rev2.analyze(api, defer_condition(session))).json()
    assert all(not v.get("previous_hold") for v in seen[-1]["document_values"])
    assert held(session) == [HELD] and HELD not in dialogue.export_selection(session)[0]


def window_data(**dialogue_state):
    catalog = rev2.model_form(rev2.form_docx(12))
    fields = [{"candidate_id": cid, "conditions": conditions} for cid, conditions in
              ((HELD, []), (GOVERNED, ["k"]), ("p5.s0", ["own"]))]
    conditions = {"k": {"result": "unknown", "applies_to": [GOVERNED],
                        "form_evidence": {"paragraph_id": "paragraph:10", "quote": CLAUSE}},
                  "own": {"result": "unknown", "applies_to": ["p5.s0"],
                          "form_evidence": {"paragraph_id": "paragraph:5", "quote": "Dato 5"}}}
    return {"generation_revision": 3, "hold_rereview_revision": 1, "catalog": catalog,
            "audit": {"version": 12, "fields": fields, "conditions": conditions},
            "dialogue": {"answers": {}, **dialogue_state}}


def test_only_a_single_foreign_clause_is_a_misattribution():
    audit = window_data()["audit"]
    assert foreign_condition(audit, HELD, CLAUSE) == "k"
    assert foreign_condition(audit, HELD, "  dato   10 ") == "k"  # Normalized comparison.
    assert foreign_condition(audit, GOVERNED, CLAUSE) is None  # Its own condition.
    assert foreign_condition(audit, "p5.s0", "Dato 5") is None
    assert foreign_condition(audit, HELD, "Una clausola qualsiasi") is None
    audit["conditions"]["k"]["applies_to"].append(HELD)
    assert foreign_condition(audit, HELD, CLAUSE) is None  # Structurally governed.
    audit = window_data()["audit"]
    audit["conditions"]["twin"] = deepcopy(audit["conditions"]["k"])
    assert foreign_condition(audit, HELD, CLAUSE) is None  # Ambiguous citation.


def plan(slots, quote, blocker):
    return dialogue.ContinuationPlan(held_proposal_slots=slots, hold_reviews=[
        dialogue.ProposalHoldReview(proposal_slot=s, blocker=blocker, reason="Dubbio",
                                    evidence_quote=quote) for s in slots])


def empty_context(values):
    return {"document_values": [{"proposal_slot": i, "label": "Codice", "value": v,
                                 "applicability_slots": []} for i, v in enumerate(values, 1)],
            "role_contexts": [], "previous_answers": [], "applicability_contexts": []}


@pytest.mark.parametrize(("quote", "blocker", "marked"), [
    (CLAUSE, "applicability", True),
    (CLAUSE, "source", False),  # Out of scope: SOURCE doubts are never re-reviewed here.
    ("ABC123", "applicability", False),  # Anchored in its own value: an ordinary hold.
    ("Dato 7", "applicability", False),  # Not the clause of any model condition.
])
def test_other_holds_keep_their_existing_handling(quote, blocker, marked):
    data = window_data()
    update = dialogue._hold_updates(data, [{"candidate_id": HELD}], empty_context(["ABC123"]),
                                    plan([1], quote, blocker), "r1", pool=[])
    assert update["held_candidate_ids"] == [HELD]
    assert ("rereview" in update["hold_records"][HELD]) is marked
    data["hold_rereview_revision"] = None
    assert not enabled(data)
    update = dialogue._hold_updates(data, [{"candidate_id": HELD}], empty_context(["ABC123"]),
                                    plan([1], quote, blocker), "r1", pool=[])
    assert "rereview" not in update["hold_records"][HELD]


def test_an_unresolvable_reference_at_the_rereview_keeps_it_held_once():
    data = window_data(held_candidate_ids=[HELD], hold_records={HELD: {
        "status": "held", "reason_status": "unverified", "rereview": "pending",
        "misattributed_condition": "k"}})
    irregular = {"invalid_references": [{"proposal_slot": 9}], "repeated_references": {}}
    update = dialogue._hold_updates(data, [{"candidate_id": HELD}], empty_context(["ABC123"]),
                                    dialogue.ContinuationPlan(), "r2", pool=[],
                                    irregular=irregular)
    assert update["held_candidate_ids"] == [HELD]
    assert update["hold_records"][HELD]["rereview"] == "done"


def test_a_pending_hold_outside_the_window_is_neither_released_nor_consumed():
    data = window_data(held_candidate_ids=[HELD], hold_records={HELD: {
        "status": "held", "reason_status": "unverified", "rereview": "pending"}})
    update = dialogue._hold_updates(data, [{"candidate_id": "p5.s0"}], empty_context(["X"]),
                                    dialogue.ContinuationPlan(), "r2", pool=[])
    assert update["held_candidate_ids"] == [HELD]
    assert update["hold_records"][HELD]["rereview"] == "pending"


def test_new_session_profile_requires_both_opt_ins(monkeypatch):
    layout = inspect_docx(rev2.form_docx(3))
    assert adapter.initial_state(layout)["hold_rereview_revision"] == 1
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "2")
    assert "hold_rereview_revision" not in adapter.initial_state(layout)
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.delenv("MAPI_HOLD_REREVIEW_REVISION")
    assert "hold_rereview_revision" not in adapter.initial_state(layout)
