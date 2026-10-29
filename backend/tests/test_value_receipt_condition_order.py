"""A USER value survives a later confirmation of its condition; exclusions still block it.

Replay of manual Minervino test 2 (29 Oct): the signatory name is now asked before its
condition. The name receipt was bound to the condition replies seen when it was checked
(none), so the later confirmation changed its digest and the name vanished from the DOCX.
The same happened when a confirmation was asked again to cover derived data.
"""

from test_signatory_order_and_extension import open_name_case
from test_signatory_question_blocked_proposal import NAME

from app.compilation_global_dialogue import question_pool
from app.compilation_scope_review import blocked_source_fields, blocked_user_fields, scope_receipt
from app.compilation_source_reuse import reuse_selected_person


def answer(data, key, ids, action, value=None, quote=None):
    record = {"action": action, "user_quote": quote or value or "Confermo", "provenance": "USER",
              **({"value": value} if value else {"applies": action == "CONDITION_TRUE"})}
    if action in {"VALUE", "CONDITION_TRUE", "CONDITION_FALSE"}:
        record.update(scope_receipt(data, key, ids, record))
    else:
        record["affected_fields"] = list(ids)
    data["dialogue"]["answers"][key] = record
    return record


def name_first(data, layout, sources):
    answer(data, "field:p0.s0", ["p0.s0"], "VALUE", value=NAME)
    data["dialogue"]["user_values"]["p0.s0"] = {"value": NAME, "user_quote": NAME,
                                                "provenance": "USER"}
    data["audit"] = reuse_selected_person(data, layout, "alpha", sources)
    return next(q for q in question_pool(data) if q["key"] == "condition:c_firm")


def test_the_name_given_first_survives_the_confirmation_of_its_condition():
    data, layout, sources = open_name_case()
    question = name_first(data, layout, sources)
    assert "p0.s0" in blocked_user_fields(data)  # Its condition is still unanswered.
    answer(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE")
    assert "p0.s0" not in blocked_user_fields(data)
    assert not set(question["field_ids"]) & blocked_source_fields(data)


def test_a_reconfirmation_covering_derived_data_keeps_the_name():
    data, layout, sources = open_name_case()
    answer(data, "condition:c_firm", ["p0.s0"], "CONDITION_TRUE")  # Before the name.
    question = name_first(data, layout, sources)
    assert question.get("extension")
    answer(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE", quote="Sì, vale")
    assert "p0.s0" not in blocked_user_fields(data)


def test_an_exclusion_a_deferral_or_a_confirmation_elsewhere_still_blocks_the_name():
    for action, elsewhere in (("CONDITION_FALSE", False), ("SKIP", False),
                              ("CONDITION_TRUE", True)):
        data, layout, sources = open_name_case()
        question = name_first(data, layout, sources)
        ids = [cid for cid in question["field_ids"] if not elsewhere or cid != "p0.s0"]
        answer(data, "condition:c_firm", ids, action)
        assert "p0.s0" in blocked_user_fields(data), action


def test_an_altered_record_of_the_checked_conditions_is_rejected():
    data, layout, sources = open_name_case()
    question = name_first(data, layout, sources)
    answer(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE")
    record = data["dialogue"]["answers"]["field:p0.s0"]
    record["checked_conditions"] = {"c_firm": {"action": "CONDITION_TRUE", "applies": True,
                                               "user_quote": "Confermo"}}
    assert "p0.s0" in blocked_user_fields(data)
