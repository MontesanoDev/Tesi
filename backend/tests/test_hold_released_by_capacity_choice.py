"""A hold waiting for the FORM capacity choice is released by that choice (E2E, 29 Oct).

Real Minervino run: the narrator held 22 partner proposals «until the quality of the
application is confirmed», citing «IN QUALITÀ DI». The capacity choice governs the option
boxes, not the partners, so the hold had no release key: the USER chose option 4 and the
partners stayed empty. Refused confirmations named the model's note instead of the clause.
"""

from types import SimpleNamespace

from app.compilation_global_dialogue import _blocker_link

AUDIT = {"choice_groups": {"capacity": {"origin": "FORM_capacity_choice",
                                        "applicable": {"p39.cb0": ["c_soc"], "p21.cb0": []}}}}
POOL = [{"key": "choice:capacity", "kind": "choice", "field_ids": ["p39.cb0", "p21.cb0"]}]
REVIEW = SimpleNamespace(condition_slot=1, evidence_quote="IN QUALITÀ DI")
NO_OWN = ({"applicability_slots": []}, {"applicability_contexts": []})


def test_the_hold_is_bound_to_the_capacity_choice_of_its_branch():
    partner = {"candidate_id": "p43.s0", "conditions": ["c_soc", "c_section"]}
    assert _blocker_link(partner, NO_OWN[0], NO_OWN[1], REVIEW, POOL, AUDIT) == (
        "choice:capacity", "CAPACITY_CHOICE_BRANCH")


def test_a_choice_of_another_branch_or_another_origin_does_not_release_it():
    other = {"candidate_id": "x1.s0", "conditions": ["c_other"]}
    assert _blocker_link(other, NO_OWN[0], NO_OWN[1], REVIEW, POOL, AUDIT) == (None, None)
    plain = {"choice_groups": {"capacity": {**AUDIT["choice_groups"]["capacity"],
                                            "origin": "MODEL"}}}
    partner = {"candidate_id": "p43.s0", "conditions": ["c_soc"]}
    assert _blocker_link(partner, NO_OWN[0], NO_OWN[1], REVIEW, POOL, plain) == (None, None)
