"""A confirmation repeated as a free instruction keeps everything it had already authorized.

Real dialogue on Minervino: 16 values in the first draft, then «Scelgo l'opzione 4…» sent to the
already confirmed branch. That receipt had no question text, so the FORM choice of the region left
the audit; the new receipt covered the box's derived target and voided itself. Second draft: no
values at all, and the choice could not be given. Synthetic FORM.
"""

import test_capacity_choice_ownership as owner
import test_equivalent_conditions_question as base

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_chat import ClarificationReply
from app.compilation_choices import materialize_choices
from app.compilation_conversation import targets
from app.compilation_global_dialogue import condition_receipts

CID, GROUP, CHOICE = base.CID, "form_capacity_0", "choice:form_capacity_0"
AGAIN = "Sì, partecipo come legale rappresentante della società di ingegneria."


def case(revision=1):
    data, layout = base.case()
    data.update(conversation_revision=1, phase="REVIEW")
    data["validated"] = {**data["audit"]}
    if revision:
        data["conversation_turn_revision"] = revision
    return base.confirm(data, layout, base.applicability(data)[0]), layout


def by_key(data, key):
    return next((q for q in targets(data) if q["key"] == key), None)


def repeat(data, layout):
    """What apply_replies records for a direct instruction: no question text, same guard proof."""
    slot = by_key(data, "condition:seg1")
    reply = ClarificationReply(slot=1, action="CONDITION_TRUE", user_quote=AGAIN)
    record = {"action": "CONDITION_TRUE", "user_quote": AGAIN, "provenance": "USER",
              "label": slot["label"], "ambiguity_check": "SEMANTIC_GUARD", "applies": True,
              "affected_fields": list(slot["field_ids"]), "scope_validation": scope.proof(
                  scope.target(data, slot["key"], slot["field_ids"]), reply)}
    data["dialogue"]["answers"].update(condition_receipts(data, slot, record, reply))
    return base.derive(data, layout)


def test_a_repeated_confirmation_stays_valid_and_authorizes_the_same_destinations():
    first, layout = case()
    covered = first["dialogue"]["answers"]["condition:seg1"]["affected_fields"]
    after = repeat(first, layout)
    answers = after["dialogue"]["answers"]
    assert set(answers["condition:seg1"]["affected_fields"]) == set(covered)
    assert CID not in answers["condition:seg1"]["affected_fields"]
    for cid in covered:
        for key in ("condition:seg1", "condition:seg2"):
            assert scope.valid_receipt(after, key, answers[key], cid)
    assert not {"p4.s0", "p6.s0"} & scope.blocked_source_fields(after)


def test_the_form_choice_survives_it_and_can_be_addressed_directly():
    first, layout = case()
    after = repeat(first, layout)
    group = after["audit"]["choice_groups"][GROUP]
    assert group["applicable"] == {CID: ["seg1", "seg2"]}
    target = by_key(after, CHOICE)
    assert target["kind"] == "choice"
    assert target["field_ids"] == list(group["options"])
    assert len(target["alternatives"]) == 3
    # Asked once, whether or not it was the next question: nothing else marks the box.
    assert len(owner.kind(after, "choice")) == 1


def test_confirming_again_marks_no_box_and_only_the_explicit_choice_does():
    first, layout = case()
    after = repeat(first, layout)
    assert branches.effective_user_values(after) == {}
    assert materialize_choices(after, [], []) == ({}, [])
    chosen = owner.choose(after, layout)
    assert branches.capacity_choice_valid(chosen, CID, "seg1")
    assert materialize_choices(chosen, [], [CID]) == ({CID: True}, [])


def test_a_stale_receipt_that_covered_the_box_is_asked_again_without_it():
    first, layout = case()
    old = first["dialogue"]["answers"]["condition:seg1"]
    old["affected_fields"] = [*old["affected_fields"], CID]  # As saved before this fix.
    first["hold_resolution_revision"] = 1
    [slot] = [q for q in base.applicability(first) if q["key"] == "condition:seg1"]
    assert slot.get("stale_receipt") and CID not in slot["field_ids"]


def test_a_confirmation_never_shown_is_still_not_a_shown_answer_without_a_guard_proof():
    first, layout = case()
    first["dialogue"]["answers"]["condition:seg1"].pop("scope_validation")
    first["dialogue"]["answers"]["condition:seg1"].pop("question")
    first["dialogue"]["answers"]["condition:seg2"].pop("scope_validation")
    first["dialogue"]["answers"]["condition:seg2"].pop("question")
    assert GROUP not in base.derive(first, layout)["audit"]["choice_groups"]


def test_the_previous_profile_keeps_its_targets():
    first, _ = case(revision=None)
    assert by_key(first, CHOICE) is None
