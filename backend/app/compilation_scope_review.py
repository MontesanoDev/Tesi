"""Candidate rev 3: bind semantic USER scope checks to actual FORM destinations.

Digests detect stale/mismatched receipts; they are not proofs of semantic truth.
Only the existing independent reply guard creates these internal receipts.
"""

from app.compilation_segments import request_digest


def enabled(data):
    return data.get("generation_revision") == 3


def session_data(session):
    """Public projections omit FORM/audit. Read the same persisted revision internally."""
    data = session.get("global_compilation") or {}
    if not enabled(data) or "catalog" in data:
        return data
    from app.compilation_global_sessions import _row_state
    from app.db import connection

    with connection() as db:
        _, state = _row_state(db, session["project_id"], session["id"], session["version"])
    return {**state["global_compilation"],
            **({"fields": data["fields"]} if "fields" in data else {})}


def target(data, key, field_ids):
    catalog, audit = data.get("catalog") or {}, data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    ids = sorted(set(field_ids))
    conditions = {c for cid in ids for c in fields.get(cid, {}).get("conditions", [])}
    if key.startswith("condition:"):
        conditions.add(key.removeprefix("condition:"))
    answers = (data.get("dialogue") or {}).get("answers", {})
    description = {
        "key": key,
        "destinations": [{"candidate_id": cid,
                          "candidate": catalog.get("candidates", {}).get(cid),
                          "label": fields.get(cid, {}).get("label"),
                          "form_evidence": fields.get(cid, {}).get("form_evidence"),
                          "conditions": fields.get(cid, {}).get("conditions", [])} for cid in ids],
        "conditions": {c: {k: v for k, v in audit.get("conditions", {}).get(c, {}).items()
                            if k in {"form_evidence", "reason", "aspect", "operator", "scope",
                                     "fact_ids"}} for c in sorted(conditions)},
        "user_conditions": {c: {k: v for k, v in answers.get("condition:" + c, {}).items()
                                 if k in {"action", "user_quote", "applies"}}
                            for c in sorted(conditions) if not key.startswith("condition:")},
    }
    return {**description, "digest": request_digest({
        "target": description, "form": catalog.get("blocks", []),
        "initial_user_requests": data.get("user_context", [])})}


def context(data, slots):
    """Complete FORM once, actual affected destinations for each backend-owned slot."""
    if not enabled(data):
        return None
    return {"revision": 1, "form_blocks": data["catalog"]["blocks"],
            "initial_user_requests": data.get("user_context", []),
            "slots": {str(q["slot"]): target(data, q["key"], q["field_ids"]) for q in slots}}


def proof(scope_target, reply):
    """Bind the checked reply to this target; never accept a digest returned by the model."""
    record = reply if isinstance(reply, dict) else reply.model_dump()
    return request_digest({"target": scope_target["digest"],
                           "action": record.get("action"),
                           "user_quote": record.get("user_quote"),
                           "value": record.get("normalized_value") or record.get("value"),
                           "selected_options": record.get("selected_options")})


def valid_receipt(data, key, receipt, cid):
    ids = receipt.get("affected_fields") or []
    if (cid not in ids or not receipt.get("scope_validation")
            or receipt.get("provenance") != "USER"):
        return False
    if key.startswith("condition:"):
        if receipt.get("action") not in {"CONDITION_TRUE", "CONDITION_FALSE"} or receipt.get(
                "applies") is not (receipt["action"] == "CONDITION_TRUE"):
            return False
    elif receipt.get("action") != "VALUE":
        return False
    return receipt["scope_validation"] == proof(target(data, key, ids), receipt)


def blocked_source_fields(data):
    """Direct export confirmations cannot bypass the candidate's USER scope verification."""
    if not enabled(data):
        return set()
    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    from app.compilation_table_scope import blocked_fields

    blocked = blocked_fields(data)
    for field in audit.get("fields", []):
        cid = field["candidate_id"]
        for c in field.get("conditions", []):
            key, receipt = "condition:" + c, answers.get("condition:" + c, {})
            result = audit.get("conditions", {}).get(c, {}).get("result", "unknown")
            if result == "false" or receipt.get("applies") is False:
                blocked.add(cid)
            elif receipt.get("applies") is True or result == "unknown":
                if receipt.get("applies") is not True or not valid_receipt(data, key, receipt, cid):
                    blocked.add(cid)
    return blocked


def blocked_user_fields(data):
    """A literal USER value alone proves neither branch applicability nor attribution."""
    if not enabled(data):
        return set()
    from app.compilation_branch_evidence import effective_user_values

    dialogue = data.get("dialogue") or {}
    answers = dialogue.get("answers", {})
    blocked = blocked_source_fields(data)
    for cid, value in effective_user_values(data).items():
        key = "choice:" + str(value["choice_group_id"]) if value.get("choice_group_id") else \
            "field:" + cid
        receipt = answers.get(key, {})
        if not valid_receipt(data, key, receipt, cid):
            blocked.add(cid)
        elif not value.get("choice_group_id") and (receipt.get("value") != value.get("value")
                                                   or receipt.get("user_quote") != value.get(
                                                       "user_quote")):
            blocked.add(cid)
    return blocked
