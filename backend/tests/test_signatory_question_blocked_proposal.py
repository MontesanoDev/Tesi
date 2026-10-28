"""A blocked MODEL proposal for the signatory must not remove the FORM-owned question.

Attempt 03: the model proposed the signatory block with a role binding rejected by the
validator (the FORM leaves the role blank, so a required role cannot be quoted there). The
proposals stayed blocked, which was right, but the FORM-owned «Il sottoscritto» question
vanished with them, and so did the signatory condition: no destination of it was valid.
Expected order: the FORM-owned name, then the SOURCE derivation for the chosen person, then
the condition over the derived destinations (the USER scope digest covers their final form).
"""

import copy

from test_compilation_selected_person import NAME, case

from app.compilation_global_dialogue import open_condition_questions, question_pool
from app.compilation_scope_review import blocked_source_fields, blocked_user_fields, proof, target
from app.compilation_source_reuse import reuse_selected_person, signatory_fields

BLOCKED = ["Binding di ruolo rifiutato"]
# As in attempt 03: grounded personal facts of the right person, only the role binding fails.
FACTS = {"p0.s0": NAME, "p0.s1": "Torino", "p0.s2": "TO", "p0.s3": "12 gennaio 1985",
         "p1.s0": "Milano", "p1.s1": "MI", "p1.s2": "Via Roma 24", "p1.s3": "NREADA85A52L219R"}
BLOCK = [*FACTS, "p2.s0"]


def blocked_case():
    """The selected-person case without USER answers: every signatory destination carries a
    MODEL proposal blocked by the role binding and an unknown signatory condition."""
    data, layout, sources = case()
    data["dialogue"] = {"answers": {}, "user_values": {}}
    data["generation_revision"] = 3  # Sections profile: USER scope verification enabled.
    audit = data["audit"]
    audit["conditions"]["c_firm"] = {
        "result": "unknown", "reason": "Sottoscrittore e relativa carica non confermati",
        "form_evidence": {"paragraph_id": "paragraph:0",
                          "quote": "Il sottoscritto ________, nato a"}}
    for cid, value in FACTS.items():
        audit["facts"]["f_" + cid] = {"subject": NAME, "entity": "person", "value": value,
                                      "validation": "GROUNDED_PROPOSAL"}
    for field in audit["fields"]:
        cid = field["candidate_id"]
        if cid in BLOCK:
            fact = "f_" + cid if cid in FACTS else None
            field.update(conditions=["c_firm"], validation="REVIEW_REQUIRED",
                         validation_errors=list(BLOCKED), disposition="conditional",
                         subject_binding={"binding_id": "b", "validation_errors": list(BLOCKED)},
                         **({"proposal": {"disposition": "conditional", "fact_id": fact},
                             "fact_id": fact} if fact else {}))
    next(f for f in audit["fields"] if f["candidate_id"] == "p0.s0")["label"] = "Il sottoscritto"
    return data, layout, sources


def keys(pool):
    return [q["key"] for q in pool]


def receipt(data, key, ids, action, value=None, quote=None):
    record = {"action": action, "user_quote": quote or value or "Confermo", "provenance": "USER",
              "affected_fields": list(ids),
              **({"value": value} if value else {"applies": action == "CONDITION_TRUE"})}
    record["scope_validation"] = proof(target(data, key, ids), record)
    data["dialogue"]["answers"][key] = record
    return record


def chosen(name):
    """USER answers the FORM-owned name; the backend then derives from SOURCE."""
    data, layout, sources = blocked_case()
    receipt(data, "field:p0.s0", ["p0.s0"], "VALUE", value=name)
    data["dialogue"]["user_values"]["p0.s0"] = {"value": name, "user_quote": name,
                                                "provenance": "USER"}
    data["audit"] = reuse_selected_person(data, layout, "alpha", sources)
    return data


def test_blocked_proposal_offers_the_form_owned_name_before_any_condition():
    data, _, _ = blocked_case()
    pool = question_pool(data)
    name = next(q for q in pool if q["key"] == "field:p0.s0")
    assert name["form_owned"] and name["field_ids"] == ["p0.s0"]
    assert "condition:c_firm" not in keys(pool)  # No valid destination to confirm yet.
    fallback = open_condition_questions(pool)  # What the backend asks if the narrator is silent.
    assert name["slot"] in [q.slot for q in fallback]


def test_the_blocked_proposal_is_never_offered_as_a_value():
    data, _, _ = blocked_case()
    field = signatory_fields(data)["p0.s0"]
    assert not {"proposal", "fact_id", "value", "proposed_value", "conditions"} & set(field)
    assert field["blocked_model_proposal"] == {"validation_errors": BLOCKED,
                                               "fact_id": "f_p0.s0", "conditions": ["c_firm"]}
    original = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p0.s0")
    assert original["validation_errors"] == BLOCKED and original["proposal"]  # Unchanged.


def test_valid_proposal_and_invalid_destination_keep_their_previous_treatment():
    data, _, _ = blocked_case()
    valid = copy.deepcopy(data)
    next(f for f in valid["audit"]["fields"] if f["candidate_id"] == "p0.s0").update(
        validation_errors=[], subject_binding={"binding_id": "b", "validation_errors": []})
    assert "p0.s0" not in signatory_fields(valid)  # The narrator reviews a usable proposal.
    name = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p0.s0")
    name.pop("proposal")
    name["validation_errors"] = ["Destinazione FORM non valida"]
    assert "p0.s0" not in signatory_fields(data)  # No proposal: an invalid target stays out.


def test_chosen_person_then_condition_over_the_derived_destinations():
    data = chosen(NAME)
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    derived = sorted(c for c, f in fields.items() if f.get("source_reuse"))
    assert derived and set(derived) <= set(BLOCK) - {"p0.s0"}
    assert all(fields[c]["source_reuse"]["subject"] == NAME and fields[c]["value"] is None
               and fields[c]["conditions"] == ["c_firm"] for c in derived)
    assert fields["p0.s1"]["proposed_value"] == "Torino"
    question = next(q for q in question_pool(data) if q["key"] == "condition:c_firm")
    assert set(derived) <= set(question["field_ids"])
    assert set(derived) <= blocked_source_fields(data)  # Not before the USER confirmation.
    receipt(data, "condition:c_firm", question["field_ids"], "CONDITION_TRUE")
    assert not set(derived) & blocked_source_fields(data)
    assert "p0.s0" not in blocked_user_fields(data)


def test_a_condition_receipt_does_not_cover_destinations_it_did_not_show():
    data = chosen(NAME)
    receipt(data, "condition:c_firm", ["p0.s1"], "CONDITION_TRUE")
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    others = {c for c, f in fields.items() if f.get("source_reuse")} - {"p0.s1"}
    assert others and others <= blocked_source_fields(data)


def test_negative_receipt_blocks_and_absent_person_reuses_nothing():
    data = chosen(NAME)
    question = next(q for q in question_pool(data) if q["key"] == "condition:c_firm")
    receipt(data, "condition:c_firm", question["field_ids"], "CONDITION_FALSE")
    derived = {f["candidate_id"] for f in data["audit"]["fields"] if f.get("source_reuse")}
    assert derived <= blocked_source_fields(data)
    absent = chosen("Bruno Verdi")
    assert not any(f.get("source_reuse") for f in absent["audit"]["fields"])
    assert "condition:c_firm" not in keys(question_pool(absent))
