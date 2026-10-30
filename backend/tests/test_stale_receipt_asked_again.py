"""A USER confirmation whose scope changed after the answer is asked again, never left silent.

Real campaign on ee80067 (Minervino run 5): the company-data condition was confirmed in the
first turn, together with the signatory name. The signatory derivation then changed one of its
destinations, so the scope proof of the receipt no longer matched: 52 documented values stayed
blocked («Ambito della decisione USER non verificato o non più coerente con il modulo») and the
confirmation was never asked again. The stale receipt still blocks (the old answer is never
reused); the question is asked again, saying why. Synthetic FORM.
"""

from copy import deepcopy

import test_equivalent_conditions_question as base

from app import compilation_scope_review as scope
from app.compilation_global_dialogue import question_pool


def stale_case(revision=1):
    data, layout = base.case()
    data["hold_resolution_revision"] = revision
    after = base.confirm(data, layout, base.applicability(data)[0])
    assert not [q for q in question_pool(after) if q["kind"] == "applicability"]
    changed = deepcopy(after)
    # One confirmed destination changes after the answer (here: its FORM label).
    field = next(f for f in changed["validated"]["fields"] if f["candidate_id"] == "p6.s0")
    field["label"] = "Sede legale della società"
    return base.derive(changed, layout)


def test_a_confirmation_with_a_changed_scope_is_asked_again_and_still_blocks():
    data = stale_case()
    assert "p6.s0" in scope.blocked_source_fields(data)  # The old answer is never reused.
    [slot] = [q for q in question_pool(data) if q["kind"] == "applicability"]
    assert slot.get("stale_receipt") and "p6.s0" in slot["field_ids"]
    assert not slot.get("extension")


def test_the_previous_profile_keeps_the_silent_block():
    data = stale_case(revision=None)
    assert "p6.s0" in scope.blocked_source_fields(data)
    assert not [q for q in question_pool(data) if q["kind"] == "applicability"]
