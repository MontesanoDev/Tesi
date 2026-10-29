"""A confirmation that releases documented SOURCE data is always asked, and the draft says why
documented data stayed empty.

Manual Minervino tests 3 and 4 (29 Oct): an open condition governing the operator's grounded
proposals sat in the pool for two turns while the narrator chose deferrable decisions; the
draft left the data empty with «Le informazioni non verificate restano vuote». Synthetic FORM.
"""

from test_signatory_hold_shared_clause import OPERATOR, OUTSIDE, shared_clause_case

from app.compilation_global_dialogue import (
    DialoguePlan,
    question_pool,
    render_dialogue,
    unexported_notice,
)

CLAUSE = "Legale rappresentante di società di ingegneria"


def case(operator="semantic"):
    data, _, _ = shared_clause_case(operator)
    for key in ("c_firm", "c_section"):
        data["audit"]["conditions"][key]["form_evidence"]["quote"] = CLAUSE
    data["audit"]["fields"].append({  # An open value the narrator prefers to ask.
        "candidate_id": "x8.s0", "label": "Codice pratica", "conditions": [],
        "validation": "REVIEW_REQUIRED", "disposition": "review", "validation_errors": [],
        "form_evidence": {"paragraph_id": "paragraph:2", "quote": "Codice pratica"}})
    data["writable_ids"] = [*data["writable_ids"], "x8.s0"]
    return data


def rendered(data, chosen_kind):
    pool = question_pool(data)
    chosen = [q for q in pool if q["kind"] == chosen_kind]
    plan = DialoguePlan(message="Riepilogo dei punti aperti.", questions=[
        {"slot": q["slot"], "question": "Puoi indicarlo?"} for q in chosen])
    return render_dialogue(plan, pool)["question"]["slots"]


def test_an_omitted_condition_over_documented_data_is_asked_by_the_backend():
    slots = rendered(case(), "value")  # The narrator asks only the open value.
    [condition] = [s for s in slots if s["kind"] == "applicability"]
    assert condition["question"].startswith("Confermi che si applica al vostro caso quanto "
                                            f"indicato nel modulo: «{CLAUSE}» (riguarda: ")
    assert "Operatore economico" in condition["question"]  # The data it releases are named.
    assert OPERATOR in condition["field_ids"]
    assert any(s["key"] == "field:x8.s0" for s in slots)  # The narrator's question stays.


def test_a_condition_without_documented_data_is_left_to_the_narrator():
    data = case(operator="exists")  # c_firm waits for the name; c_section governs no proposal.
    assert [q["documented"] for q in question_pool(data) if q["kind"] == "applicability"] == [0]
    assert all(s["kind"] != "applicability" for s in rendered(data, "value"))


def test_the_draft_names_documented_data_left_empty_and_why():
    data = case()
    notice = unexported_notice(data, written=set())
    assert notice.startswith("Restano vuoti: 1 dati trovati nelle fonti (")
    assert f"aspettano la tua conferma su «{CLAUSE}»" in notice
    data["dialogue"]["answers"]["condition:c_firm"] = {"applies": False, "action":
                                                       "CONDITION_FALSE", "provenance": "USER"}
    assert unexported_notice(data, written=set()) == ""  # An exclusion is justified.
    data["dialogue"]["answers"].clear()
    data["dialogue"]["held_candidate_ids"] = [OPERATOR]
    assert "sono sospesi in attesa di una verifica" in unexported_notice(data, written=set())
    assert unexported_notice(data, written={OPERATOR}) == ""
    assert OUTSIDE not in unexported_notice(data, written=set())  # No proposal, not listed.
