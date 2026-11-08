"""Deterministic review of narrator holds on documented proposals (30 Oct).

Real campaigns of 30 October: 129 of 139 narrator holds blocked values equal to the gold or
differing only in form; with structured holds they became verification questions the frozen
USER policy deferred (Minervino run 2 of the final campaign: 18 values). A doubt alone neither
blocks a valid value nor authorizes it: SOURCE, conditions, receipts and validators decide.
"""

import pytest
from test_compilation_global_sessions import api, provider, resolve, start
from test_compilation_hold_rereview import window_data
from test_compilation_p3_hold_validation import FIRST, SECOND, SUMMARY, hold, narrator, state

from app import compilation_global_dialogue as dialogue
from app.compilation_hold_review import review

__all__ = ["api", "provider"]
SUBJECT = "Persona Demo"
SOURCES = [{"chunk_id": 7, "source_name": "scheda.md", "content":
            f"### {SUBJECT}\\n- Sezione dell'albo: non disponibile.\\n- Ruolo: socio."}]


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def case(conditions=(), answers=None, result="unknown", **field):
    data = window_data()
    data["hold_review_revision"] = 1
    data["audit"]["facts"] = {"f": {"subject": SUBJECT, "property": "sezione",
                                    "validation": "GROUNDED_PROPOSAL"}}
    data["audit"]["conditions"] = {c: {"result": result, "form_evidence": {"quote": c}}
                                   for c in conditions}
    data["audit"]["fields"] = [{"candidate_id": "x", "label": "Sezione", "kind": "data",
                                "validation": "GROUNDED_PROPOSAL", "fact_id": "f",
                                "conditions": list(conditions), "validation_errors": [],
                                "source_evidence": [{"quote": "| Persona Demo | A |"}],
                                **field}]
    data["dialogue"]["answers"] = answers or {}
    return data


def decide(data, quote="Dubbio del narratore", cause="fonte_insufficiente"):
    return review(data, "x", {"evidence_quote": quote, "cause": cause}, SOURCES)


def test_an_unverifiable_doubt_on_a_valid_unconditional_value_goes_back_to_the_gates():
    assert decide(case()) == {"verdict": "dubbio_generico", "action": "release"}


def test_a_contradicting_SOURCE_statement_on_the_same_subject_is_asked_with_both_texts():
    decision = decide(case(), quote="- Sezione dell'albo: non disponibile.")
    assert decision["verdict"] == "evidenza_contraddittoria" and decision["action"] == "verify"
    assert decision["contrary"]["source_name"] == "scheda.md"


def test_a_negation_of_another_property_or_subject_contradicts_nothing():
    other = [{"chunk_id": 8, "source_name": "x.md", "content": "Altro: la sezione non è nota."}]
    assert review(case(), "x", {"evidence_quote": "la sezione non è nota."}, other)[
        "action"] == "release"  # The chunk does not name the subject.
    assert decide(case(), quote="- Ruolo: socio.")["action"] == "release"  # No negation.


def test_an_open_governing_condition_keeps_the_hold_bound_to_its_question():
    decision = decide(case(conditions=["c"]))
    assert decision == {"verdict": "applicabilita_incerta", "action": "bind",
                        "key": "conditions:c"}


def test_confirmed_applicability_releases_and_an_exclusion_keeps_the_gates_blocking():
    yes = {"condition:c": {"applies": True, "action": "CONDITION_TRUE"}}
    assert decide(case(conditions=["c"], answers=yes)) == {
        "verdict": "applicabilita_confermata", "action": "release"}
    assert decide(case(conditions=["c"], result="true"))["action"] == "release"
    no = {"condition:c": {"applies": False, "action": "CONDITION_FALSE"}}
    assert decide(case(conditions=["c"], answers=no))["action"] == "keep"


def test_no_grounded_proposal_or_a_checkbox_option_is_never_released_by_the_review():
    assert decide(case(validation="REJECTED", fact_id=None,
                       validation_errors=["Fatto SOURCE assente o rifiutato"]))[
        "action"] == "keep"
    assert decide(case(choice_group_id="g"))["action"] == "select"
    assert decide(case(), cause="applicabilita_incerta")["action"] == "verify"


@pytest.mark.anyio
async def test_the_doubt_on_a_valid_value_is_set_aside_and_the_draft_says_so(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Via del Sole 9")]},
             {"questions": []})
    s = await resolve(api, await start(api))
    record = state(s)["hold_records"][SECOND]
    assert state(s)["held_candidate_ids"] == []
    assert record["release_reason"] == "DETERMINISTIC_REVIEW"
    assert record["review"]["verdict"] == "dubbio_generico"
    assert not [q for q in s["chat"]["question"]["slots"] if q["key"].startswith("hold:")]
    assert dialogue.export_selection(s)[0] == [FIRST, SECOND]  # Back to the ordinary gates.
    data = {"dialogue": state(s), "audit": {"fields": [{"candidate_id": SECOND,
                                                        "label": "Sede legale"}]}}
    assert dialogue.reviewed_doubts_notice(data, {SECOND}).startswith(
        "Da rivedere: 1 dati trovati nelle fonti (Sede legale)")
    assert dialogue.reviewed_doubts_notice(data, set()) == ""  # Only values actually written.
