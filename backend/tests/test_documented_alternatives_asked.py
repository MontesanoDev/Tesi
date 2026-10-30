"""A choice between documented SOURCE values is always asked, and the draft names it if empty.

E2E campaign of 30 Oct, Minervino (3 of 10 real runs): two grounded facts gave one person's name
as «Elisa Romano» and «Ing. Elisa Romano», so the backend left two names to a USER choice. The
value question sat in the pool for three turns, the narrator offered the draft instead, and the
draft notice did not name the empty data. Nothing is chosen or written by the question or the
notice. Synthetic FORM.
"""

import pytest
from test_documented_conditions_not_skipped import case, rendered

from app.compilation_global_dialogue import (
    DialoguePlan,
    question_pool,
    render_dialogue,
    unexported_notice,
)

CHOICE = "x7.s0"
VALUES = ["Anna Neri", "Ing. Anna Neri"]


def alternatives_case(kind="unselected_alternatives"):
    data = case()
    data["audit"]["fields"].append({
        "candidate_id": CHOICE, "label": "Nome del direttore tecnico", "conditions": [],
        "validation": "REVIEW_REQUIRED", "disposition": "review", "value": None,
        "fact_id": None, "review_kind": kind, "validation_errors": [],
        "proposal": {"kind": "data", "disposition": "value", "fact_id": "f_neri_a"},
        "alternatives": [{"fact_id": f"f_neri_{k}", "value": value, "source_evidence": [
            {"role": "source", "quote": f"Direttore tecnico: {value}."}]}
            for k, value in zip("ab", VALUES)],
        "form_evidence": {"paragraph_id": "paragraph:3", "quote": "Direttore tecnico ________"}})
    data["writable_ids"] = [*data["writable_ids"], CHOICE]
    return data


@pytest.mark.parametrize("kind", ["unselected_alternatives", "ambiguous", "conflicting"])
def test_an_omitted_choice_between_documented_values_is_asked_by_the_backend(kind):
    slots = rendered(alternatives_case(kind), "applicability")  # The narrator asks the condition.
    [choice] = [s for s in slots if s["key"] == "field:" + CHOICE]
    assert choice["kind"] == "value"
    assert "«Direttore tecnico»" in choice["question"]
    assert "«Anna Neri» oppure «Ing. Anna Neri»" in choice["question"]
    assert all(s["key"] != "field:x8.s0" for s in slots)  # A plain open value: narrator's call.


def test_the_choice_is_asked_even_when_the_narrator_offers_the_draft():
    pool = question_pool(alternatives_case())
    plan = DialoguePlan(message="Posso preparare la bozza.", questions=[])
    slots = render_dialogue(plan, pool)["question"]["slots"]
    assert "field:" + CHOICE in {s["key"] for s in slots}


def test_alternatives_without_SOURCE_evidence_are_not_imposed():
    data = alternatives_case()
    data["audit"]["fields"][-1]["alternatives"][1]["source_evidence"] = []
    assert all(s["key"] != "field:" + CHOICE for s in rendered(data, "applicability"))


def test_an_answered_choice_is_never_asked_again():
    data = alternatives_case()
    data["dialogue"]["answers"]["field:" + CHOICE] = {"action": "SKIP", "provenance": "USER",
                                                      "user_quote": "Rinvio"}
    assert all(q["key"] != "field:" + CHOICE for q in question_pool(data))


def test_the_draft_names_documented_values_waiting_for_a_choice():
    data = alternatives_case()
    notice = unexported_notice(data, written=set())
    assert ("1 dati trovati nelle fonti (Nome del direttore tecnico) aspettano la tua scelta "
            "tra valori diversi delle fonti") in notice
    assert "Nome del direttore tecnico" not in unexported_notice(data, written={CHOICE})
    data["dialogue"]["answers"]["field:" + CHOICE] = {"action": "SKIP", "provenance": "USER"}
    assert "Nome del direttore tecnico" not in unexported_notice(data, written=set())
