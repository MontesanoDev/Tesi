"""Candidate rev 3: selected holds get one narrator re-review, never a backend release.

The backend proves only a misattribution: the hold's applicability quote, not anchored in the
proposal's own context, is the FORM clause of exactly one model condition that does not govern
the proposal. It never releases the hold itself. At the next narration the proposal returns to
the review window once, with that finding. The narrator either holds it again (kept: anchored
reasons follow the usual USER blocker, others stay held without further reviews) or not (the
proposal goes back to the unchanged backend gates). SOURCE, USER and export gates are untouched.
Revision 2 also supplies grounded person/role records when a SOURCE doubt concerns that record
or role. This is a reason to re-read the evidence, not proof that the doubt is unfounded.
"""

from __future__ import annotations

from app.requirement_checks import normalized_form_text as norm

REVISION = 1
NOTE = ("Controllo del backend: la clausola citata è la condizione di altre destinazioni e non "
        "governa questa proposta. Se resta un dubbio proprio, sospendila di nuovo citando il suo "
        "contesto; per questa sola proposta l'assenza da held_proposal_slots la restituisce ai "
        "controlli del backend.")


def enabled(data):
    return (data.get("generation_revision") == 3
            and data.get("hold_rereview_revision") in {REVISION, 2})


def foreign_condition(audit, cid, quote):
    """The single model condition whose FORM clause is quoted, if it does not govern cid."""
    from app.requirement_checks import normalized_form_text as norm

    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    text = norm(quote or "")
    cited = [key for key, condition in (audit.get("conditions") or {}).items()
             if text and text == norm((condition.get("form_evidence") or {}).get("quote", ""))]
    if len(cited) != 1:
        return None
    key = cited[0]
    if key in field.get("conditions", []) or cid in audit["conditions"][key].get(
            "applies_to", []):
        return None
    return key


def due(data):
    """Held proposals waiting for their single re-review."""
    if not enabled(data):
        return set()
    dialogue = data.get("dialogue") or {}
    records = dialogue.get("hold_records", {})
    pending = {cid for cid in dialogue.get("held_candidate_ids", [])
               if records.get(cid, {}).get("rereview") == "pending"}
    source = {cid for cid in pending if records.get(cid, {}).get("source_rereview")}
    if not source:
        return pending
    from app.compilation_global_sessions import review_fields

    candidates = {f["candidate_id"]: f for f in review_fields(data) if f["selectable"]}
    return (pending - source) | {cid for cid in source if cid in candidates and
        records[cid]["source_rereview"].get("digest") == _source_digest(data, cid)
        and source_check(data, candidates[cid], records[cid]) is not None}


def _record_for(audit, cid, quote):
    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    fact = audit.get("facts", {}).get(field.get("fact_id") or field.get("proposed_fact_id"), {})
    binding = field.get("subject_binding") or {}
    if (binding.get("result") != "literal_match" or binding.get("validation_errors")
            or fact.get("validation") != "GROUNDED_PROPOSAL" or fact.get("entity") != "person"):
        return None
    records = [r for r in binding.get("record_attributions", [])
               if r.get("row") and r.get("header") and r.get("title")
               and norm(r.get("subject", "")) == norm(fact.get("subject", ""))
               and norm(r["row"]) == norm(quote or "")]
    return records[0] if len(records) == 1 else None


def _role_for(audit, cid, missing):
    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    fact = audit.get("facts", {}).get(field.get("fact_id") or field.get("proposed_fact_id"), {})
    check = field.get("subject_binding") or {}
    binding = audit.get("bindings", {}).get(check.get("binding_id"), {})
    required = norm(binding.get("required_role", ""))
    if (check.get("result") == "literal_match" and not check.get("validation_errors")
            and binding.get("validation") == "GROUNDED_PROPOSAL"
            and not binding.get("validation_errors") and fact.get("entity") == "person"
            and fact.get("validation") == "GROUNDED_PROPOSAL" and required
            and required == norm(binding.get("source_role", ""))
            and required in norm(missing or "") and check.get("record_attributions")):
        return binding
    return None


def _source_digest(data, cid):
    from app.compilation_segments import request_digest

    audit = data.get("audit") or {}
    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    fact = audit.get("facts", {}).get(field.get("fact_id") or field.get("proposed_fact_id"))
    binding = audit.get("bindings", {}).get((field.get("subject_binding") or {}).get("binding_id"))
    return request_digest({"field": field, "fact": fact, "binding": binding,
        "conditions": {key: audit.get("conditions", {}).get(key)
                       for key in field.get("conditions", [])},
        "FORM": data.get("catalog", {}).get("blocks"),
        "destination": data.get("catalog", {}).get("candidates", {}).get(cid)})


def source_check(data, proposal, review):
    """A reason to re-read evidence, NOT a verdict that the SOURCE doubt is unfounded."""
    if (not enabled(data) or data.get("hold_rereview_revision") != 2
            or not proposal.get("selectable") or review.get("blocker") != "source"):
        return None
    cid, audit = proposal["candidate_id"], data["audit"]
    field = next((f for f in audit["fields"] if f["candidate_id"] == cid), {})
    binding_id = (field.get("subject_binding") or {}).get("binding_id")
    binding = audit.get("bindings", {}).get(binding_id, {})
    if binding.get("validation") != "GROUNDED_PROPOSAL" or binding.get("validation_errors"):
        return None
    required = norm(binding.get("required_role", ""))
    if not required or required != norm(binding.get("source_role", "")):
        return None
    record = _record_for(audit, cid, review.get("evidence_quote"))
    role = _role_for(audit, cid, review.get("missing_information"))
    if not record and not role:
        return None
    from app.compilation_scope_review import blocked_source_fields

    if cid in blocked_source_fields(data):
        return None
    return {"digest": _source_digest(data, cid),
            "basis": "bound_record" if record else "bound_role",
            "form_evidence": binding.get("form_evidence"),
            "source_records": [record] if record else (field.get("subject_binding") or {}).get(
                "record_attributions", []),
            "source_evidence": binding.get("source_evidence", []),
            "required_role": binding.get("required_role"),
            "source_role": binding.get("source_role")}


def context_note(data, cid):
    record = ((data.get("dialogue") or {}).get("hold_records") or {}).get(cid, {})
    evidence = record.get("source_rereview")
    if not evidence:
        return NOTE
    return {"instruction": "Riesamina una sola volta il dubbio SOURCE alla luce del record e del "
        "ruolo già collegati dal backend. Non è un'autorizzazione: mantieni la sospensione se "
        "restano contraddizioni, un requisito ulteriore del FORM "
        "o una designazione non dimostrata. "
        "L'assenza dall'elenco dei hold restituisce solo questa proposta ai gate ordinari.",
        **{k: v for k, v in evidence.items() if k != "digest"}}
