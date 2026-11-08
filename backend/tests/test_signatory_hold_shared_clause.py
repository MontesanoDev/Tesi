"""Holding the signatory conditions never splits one FORM clause declared by two segments.

Manual Minervino test 3 (29 Oct): one segment declared the society clause as the condition of
the signatory block (operator data), another as the condition of the society section. While
the name was open the first was held back, so the USER confirmed the clause for the second
only; the first became a separate question the narrator never asked, and 47 SOURCE proposals
and the chosen capacity checkbox stayed blocked in the DOCX. Synthetic FORM.
"""

from test_signatory_order_and_extension import open_name_case

from app.compilation_global_dialogue import condition_receipts, question_pool
from app.compilation_scope_review import blocked_source_fields, scope_receipt
from app.compilation_source_reuse import pending_signatory_conditions

CLAUSE = {"paragraph_id": "paragraph:0", "quote": "Il sottoscritto ________, nato a"}
OUTSIDE = "x9.s0"  # A destination of the other segment, outside the signatory block.
OPERATOR = "p2.s1"  # SOURCE proposal of the block governed by the held condition (test 3: p14.s1).


def shared_clause_case(operator="semantic"):
    data, layout, sources = open_name_case()
    audit = data["audit"]
    audit["conditions"]["c_firm"]["operator"] = operator
    operator_field = next(f for f in audit["fields"] if f["candidate_id"] == OPERATOR)
    assert operator_field["validation"] == "GROUNDED_PROPOSAL"
    operator_field["conditions"] = ["c_firm"]
    audit["conditions"]["c_section"] = {
        "result": "unknown", "operator": operator, "form_evidence": dict(CLAUSE),
        "reason": "Sezione societaria da confermare"}
    audit["fields"].append({
        "candidate_id": OUTSIDE, "label": "Socio", "conditions": ["c_section"],
        "validation": "REVIEW_REQUIRED", "disposition": "conditional", "validation_errors": [],
        "form_evidence": {"paragraph_id": "paragraph:2", "quote": "dell’operatore economico"}})
    return data, layout, sources


def governed(data, *conditions):
    """Destinations with FORM evidence (the block's placeholders are derived after the name)."""
    return {f["candidate_id"] for f in data["audit"]["fields"] if f.get("form_evidence")
            and set(f.get("conditions", [])) & set(conditions)}


def test_the_shared_clause_is_one_question_before_the_name():
    data, _, _ = shared_clause_case()
    assert "c_firm" not in pending_signatory_conditions(data)
    [slot] = [q for q in question_pool(data) if q["kind"] == "applicability"]
    assert set(slot["condition_ids"]) == {"c_firm", "c_section"}
    assert set(slot["field_ids"]) == governed(data, "c_firm", "c_section")
    assert {OPERATOR, OUTSIDE} <= set(slot["field_ids"])


def test_one_user_confirmation_covers_both_segments_and_nothing_else():
    data, _, _ = shared_clause_case()
    [slot] = [q for q in question_pool(data) if q["kind"] == "applicability"]
    reply = {"action": "CONDITION_TRUE", "applies": True, "provenance": "USER",
             "user_quote": "Sì, come legale rappresentante della società."}
    record = {**reply, **scope_receipt(data, slot["key"], slot["field_ids"], reply)}
    data["dialogue"]["answers"].update(condition_receipts(data, slot, record, reply))
    assert set(data["dialogue"]["answers"]) == {"condition:c_firm", "condition:c_section"}
    assert not governed(data, "c_firm", "c_section") & blocked_source_fields(data)
    assert all(set(r["affected_fields"]) == set(slot["field_ids"])
               for r in data["dialogue"]["answers"].values())


def test_a_clause_of_the_block_alone_still_waits_for_the_name():
    data, _, _ = shared_clause_case(operator="exists")  # Not the same semantic clause.
    assert "c_firm" in pending_signatory_conditions(data)
    keys = [q["key"] for q in question_pool(data) if q["kind"] == "applicability"]
    assert keys == ["condition:c_section"]
