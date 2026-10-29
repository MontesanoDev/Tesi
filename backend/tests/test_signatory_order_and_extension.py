"""The signatory is chosen before its conditions; a confirmation never loses derived data silently.

Manual Minervino test 2 (29 Oct): the signatory condition, which governed only the name field,
was confirmed before the name; the name was then asked again, the SOURCE derivation added the
person's data and office, and the scope gate left them empty because the earlier receipt never
showed them. Synthetic FORM of test_signatory_question_blocked_proposal.
"""

from test_signatory_question_blocked_proposal import BLOCK, NAME, blocked_case, keys, receipt

from app.compilation_global_dialogue import question_pool
from app.compilation_scope_review import blocked_source_fields
from app.compilation_source_reuse import reuse_selected_person


def open_name_case():
    """As in test 2: no blocked proposal, the name only reviewable, the block conditional."""
    data, layout, sources = blocked_case()
    for field in data["audit"]["fields"]:
        if field["candidate_id"] in BLOCK:
            for key in ("proposal", "fact_id", "validation_errors", "subject_binding"):
                field.pop(key, None)
            field["disposition"] = "review" if field["candidate_id"] == "p0.s0" else (
                "conditional")
    name = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p0.s0")
    name["form_evidence"] = {"paragraph_id": "paragraph:0", "quote": "Il sottoscritto ____"}
    return data, layout, sources


def choose(data, layout, sources, name=NAME):
    receipt(data, "field:p0.s0", ["p0.s0"], "VALUE", value=name)
    data["dialogue"]["user_values"]["p0.s0"] = {"value": name, "user_quote": name,
                                                "provenance": "USER"}
    data["audit"] = reuse_selected_person(data, layout, "alpha", sources)
    return {f["candidate_id"] for f in data["audit"]["fields"] if f.get("source_reuse")}


def test_the_signatory_condition_waits_for_the_name_even_without_a_blocked_proposal():
    data, _, _ = open_name_case()
    pool = keys(question_pool(data))
    assert "field:p0.s0" in pool and "condition:c_firm" not in pool
    data["dialogue"]["answers"]["field:p0.s0"] = {"action": "SKIP", "provenance": "USER",
                                                 "user_quote": "Rinvio"}
    assert "condition:c_firm" in keys(question_pool(data))  # A deferred name releases it.


def test_after_the_name_one_confirmation_covers_the_derived_data():
    data, layout, sources = open_name_case()
    derived = choose(data, layout, sources)
    assert derived
    question = next(q for q in question_pool(data) if q["key"] == "condition:c_firm")
    assert derived <= set(question["field_ids"]) and not question.get("extension")
    receipt(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE")
    assert not derived & blocked_source_fields(data)
    assert "condition:c_firm" not in keys(question_pool(data))


def test_a_confirmation_given_too_early_is_asked_again_naming_the_new_data():
    data, layout, sources = open_name_case()
    receipt(data, "condition:c_firm", ["p0.s0"], "CONDITION_TRUE")  # Test 2: before the name.
    derived = choose(data, layout, sources)
    assert derived <= blocked_source_fields(data)  # Not covered: never written silently...
    [question] = [q for q in question_pool(data) if q["key"] == "condition:c_firm"]
    assert question["question"].startswith("Dopo la tua conferma ho ricavato dalle fonti")
    assert set(question["field_ids"]) >= derived | {"p0.s0"}  # ...asked again, naming them.
    receipt(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE")
    assert not derived & blocked_source_fields(data)
    assert "condition:c_firm" not in keys(question_pool(data))  # Then never again.


def test_a_deferred_or_excluded_condition_is_never_asked_again():
    for action in ("SKIP", "CONDITION_FALSE"):
        data, layout, sources = open_name_case()
        receipt(data, "condition:c_firm", ["p0.s0"], action)
        derived = choose(data, layout, sources)
        assert "condition:c_firm" not in keys(question_pool(data))
        assert derived <= blocked_source_fields(data)
