"""A MODEL choice group rejected by the validator never takes the FORM capacity choice (30 Oct).

Real Minervino run (E2E campaign, code cd47147): the model declared an exclusive group with 3 of
the 7 «IN QUALITÀ DI» options, rejected as incomplete. Its options still counted as owned, so the
backend never derived its capacity choice: the question was never asked, the chosen box stayed
empty and the holds waiting for that choice could not be released. A valid group keeps the
region. Synthetic FORM.
"""

from copy import deepcopy

import test_capacity_choice_ownership as ownership
import test_equivalent_conditions_question as base

from app.compilation_choices import materialize_choices

PARTIAL = {"validation_errors": ["Gruppo esclusivo incompleto rispetto alla lista fisica Word"],
           "label": "Ruolo del sottoscrittore", "selection": "single", "min_selected": 1,
           "conditions": [], "form_evidence": {"paragraph_id": "paragraph:0",
                                               "quote": "IN QUALITÀ DI"},
           "options": {"p1.cb0": {"label": "Professionista singolo"},
                       "p5.cb0": {"label": "Mandatario di raggruppamento"}}}


def with_model_group(validation):
    data, layout = base.case()
    data["validated"]["choice_groups"] = {"m_role": {**deepcopy(PARTIAL),
                                                     "validation": validation}}
    data["audit"] = deepcopy(data["validated"])
    return base.confirm(data, layout, base.applicability(data)[0]), layout


def test_a_rejected_model_group_leaves_the_capacity_choice_to_the_backend():
    after, layout = with_model_group("REJECTED")
    group = after["audit"]["choice_groups"]["form_capacity_0"]
    assert group["origin"] == "FORM_capacity_choice"
    assert [q["key"] for q in ownership.kind(after, "choice")] == [ownership.KEY]
    chosen = ownership.choose(after, layout)
    assert materialize_choices(chosen, [], [base.CID]) == ({base.CID: True}, [])


def test_a_valid_model_group_still_owns_the_region():
    after, _ = with_model_group("GROUNDED_GROUP")
    assert "form_capacity_0" not in after["audit"]["choice_groups"]
