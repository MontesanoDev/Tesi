"""A hold citing the FORM clause of the slot it names as its blocker is anchored (30 Oct).

Real Minervino run (E2E campaign, code cd47147): 19 operator data were held «until the quality
is chosen», citing «IN QUALITÀ DI», the FORM clause of the capacity choice slot they named. That
clause reaches the narrator only through the question pool, so the hold was marked unanchored,
got no release key and the data stayed empty after the USER chose option 4. The release still
needs the verified link of the choice to the proposal's branch and a recorded answer.
"""

from test_compilation_hold_rereview import HELD, empty_context, window_data

from app import compilation_global_dialogue as dialogue

QUOTE = "IN QUALITÀ DI"
CHOICE = {"key": "choice:capacity", "kind": "choice", "label": QUOTE, "condition": "",
          "context": QUOTE, "field_ids": ["p9.cb0", "p8.cb0"]}
OTHER = {"key": "decision:x", "kind": "decision", "label": "Luogo e data", "condition": "",
         "context": "Luogo e data", "field_ids": ["p7.s0"]}


def capacity_data():
    data = window_data()
    data["audit"]["choice_groups"] = {"capacity": {
        "origin": "FORM_capacity_choice", "applicable": {"p9.cb0": ["own"], "p8.cb0": []}}}
    return data


def held(data, conditions, pool, condition_slot=1):
    plan = dialogue.ContinuationPlan(held_proposal_slots=[1], hold_reviews=[
        dialogue.ProposalHoldReview(
            proposal_slot=1, blocker="applicability", reason="Dipende dalla qualità scelta",
            missing_information="Scelta della qualità", evidence_quote=QUOTE,
            condition_slot=condition_slot)])
    update = dialogue._hold_updates(data, [{"candidate_id": HELD, "conditions": conditions}],
                                    empty_context(["ABC123"]), plan, "r1", pool=pool)
    data["dialogue"].update(update)
    return update["hold_records"][HELD]


def choose(data, pool):
    data["dialogue"]["answers"]["choice:capacity"] = {
        "action": "VALUE", "selected_options": [1], "provenance": "USER"}
    return dialogue._hold_updates(data, [], empty_context([]), dialogue.ContinuationPlan(),
                                  "r2", pool=pool)["held_candidate_ids"]


def test_a_hold_quoting_the_capacity_choice_it_names_is_released_by_the_choice():
    data = capacity_data()
    record = held(data, ["own"], [CHOICE])
    assert record["reason_validation"] == "RECORDED"
    assert (record["blocker_key"], record["blocker_key_basis"]) == (
        "choice:capacity", "CAPACITY_CHOICE_BRANCH")
    assert data["dialogue"]["held_candidate_ids"] == [HELD]  # Held until the USER chooses.
    assert choose(data, [CHOICE]) == []


def test_the_clause_of_another_slot_or_no_slot_keeps_the_hold_unanchored():
    for pool, slot in (([OTHER], 1), ([CHOICE], None)):
        data = capacity_data()
        record = held(data, ["own"], pool, slot)
        assert record["reason_validation"] == "UNANCHORED_QUOTE"
        assert "blocker_key" not in record
        assert choose(data, pool) == [HELD]


def test_a_choice_outside_the_proposal_s_branch_never_releases_it():
    data = capacity_data()
    record = held(data, ["k"], [CHOICE])  # Its own condition is not a branch of the choice.
    assert "blocker_key" not in record
    assert choose(data, [CHOICE]) == [HELD]
