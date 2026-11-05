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


def derived_targets(data):
    """The same fallback FORM targets the guard sees as the backend-owned question and later
    SOURCE derivation, including when the model omitted the name field."""
    from app.compilation_source_reuse import signatory_fields
    from app.compilation_user_extraction import target_fields

    return {**signatory_fields(data), **target_fields(data)}


def target(data, key, field_ids, user_conditions=None, *, derived=None):
    catalog, audit = data.get("catalog") or {}, data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    fields.update(derived_targets(data) if derived is None else derived)
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
    if user_conditions is not None:
        description["user_conditions"] = user_conditions
    return {**description, "digest": request_digest({
        "target": description, "form": catalog.get("blocks", []),
        "initial_user_requests": data.get("user_context", [])})}


def context(data, slots):
    """Complete FORM once, actual affected destinations for each backend-owned slot."""
    if not enabled(data):
        return None
    targets = {str(q["slot"]): target(data, q["key"], q["field_ids"]) for q in slots}
    from app import compilation_subject_check

    if compilation_subject_check.enabled(data):
        for q in slots:  # Beside the target, outside its digest: receipts stay valid.
            if q.get("kind") == "value" and (check := compilation_subject_check.slot_context(
                    data, q["field_ids"])):
                targets[str(q["slot"])]["subject"] = check
    if data.get("conversation_revision") == 1:
        for q in slots:
            if q["key"].startswith("condition:"):
                # The model's structural inventory can be wider than this USER
                # operation (e.g. only the name is currently usable). Preserve
                # the inventory and explicitly identify the scope being checked.
                targets[str(q["slot"])]["requested_confirmation"] = {
                    "candidate_ids": list(q["field_ids"]),
                    "form_clause": q.get("condition", ""),
                    "scope_kind": "only_requested_destinations",
                    "other_MODEL_scope_destinations_requested": False}
    return {"revision": 1, "form_blocks": data["catalog"]["blocks"],
            "initial_user_requests": data.get("user_context", []),
            "slots": targets}


def proof(scope_target, reply):
    """Bind the checked reply to this target; never accept a digest returned by the model."""
    record = reply if isinstance(reply, dict) else reply.model_dump()
    return request_digest({"target": scope_target["digest"],
                           "action": record.get("action"),
                           "user_quote": record.get("user_quote"),
                           "value": record.get("normalized_value") or record.get("value"),
                           "selected_options": record.get("selected_options")})


def scope_receipt(data, key, field_ids, reply):
    """Backend scope proof of a checked reply; a value keeps the condition replies it saw."""
    scope_target = target(data, key, field_ids)
    scope = {"scope_validation": proof(scope_target, reply), "affected_fields": list(field_ids)}
    if not key.startswith("condition:"):
        scope["checked_conditions"] = scope_target["user_conditions"]
    return scope


def _checked(data, key, receipt, ids, seen, memo):
    """Scope target and proof of one receipt.

    One check reads one frozen state, and a receipt covers many fields: both are derived once per
    receipt instead of once per covered field. No memo, no sharing.
    """
    if memo is None:
        scope_target = target(data, key, ids, seen)
        return scope_target, proof(scope_target, receipt)
    slot = (key, id(receipt), seen is None)
    if slot not in memo:
        if "derived" not in memo:
            memo["derived"] = derived_targets(data)
        scope_target = target(data, key, ids, seen, derived=memo["derived"])
        memo[slot] = scope_target, proof(scope_target, receipt)
    return memo[slot]


def valid_receipt(data, key, receipt, cid, memo=None):
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
    seen = receipt.get("checked_conditions")
    if key.startswith("condition:") or seen is None:
        return receipt["scope_validation"] == _checked(data, key, receipt, ids, None, memo)[1]
    if receipt["scope_validation"] != _checked(data, key, receipt, ids, seen, memo)[1]:
        return False
    # A later USER confirmation covering this field keeps the value checked before it
    # (signatory name asked before its condition, or a confirmation extended to derived
    # data). Any other change, an exclusion or a deferral invalidates it.
    answers = (data.get("dialogue") or {}).get("answers", {})
    return all(now == seen.get(c) or (
        seen.get(c, {}).get("applies") in {None, True} and now.get("applies") is True
        and valid_receipt(data, "condition:" + c, answers.get("condition:" + c, {}), cid, memo))
        for c, now in _checked(data, key, receipt, ids, None, memo)[0]["user_conditions"].items())


def blocked_source_fields(data, *, linked_user_controls=False):
    """Direct export confirmations cannot bypass the candidate's USER scope verification."""
    if not enabled(data):
        return set()
    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    from app.compilation_form_option_scope import blocked_fields as option_blocked
    from app.compilation_table_scope import blocked_fields

    blocked = blocked_fields(data) | option_blocked(data)
    memo = {}
    for field in audit.get("fields", []):
        cid = field["candidate_id"]
        for c in field.get("conditions", []):
            key, receipt = "condition:" + c, answers.get("condition:" + c, {})
            result = audit.get("conditions", {}).get(c, {}).get("result", "unknown")
            if result == "false" or receipt.get("applies") is False:
                blocked.add(cid)
            elif receipt.get("applies") is True or result == "unknown":
                from app.compilation_branch_evidence import (
                    capacity_choice_valid,
                    linked_receipt_valid,
                )

                # The explicit choice receipt covers its option and binds this condition's
                # USER answer; it releases no other condition of the same control.
                valid = valid_receipt(data, key, receipt, cid, memo) or (
                    linked_user_controls and (linked_receipt_valid(data, cid, key)
                                              or capacity_choice_valid(data, cid, c)))
                if receipt.get("applies") is not True or not valid:
                    blocked.add(cid)
    if data.get("conversation_turn_revision") == 1:
        from app.compilation_branch_evidence import other_capacity_branches

        blocked |= other_capacity_branches(data)
    return blocked


def blocked_user_fields(data):
    """A literal USER value alone proves neither branch applicability nor attribution."""
    if not enabled(data):
        return set()
    from app.compilation_branch_evidence import effective_user_values

    dialogue = data.get("dialogue") or {}
    answers = dialogue.get("answers", {})
    blocked = blocked_source_fields(data, linked_user_controls=True)
    groups = (data.get("audit") or {}).get("choice_groups", {})
    for cid, value in effective_user_values(data).items():
        from app.compilation_branch_evidence import capacity_choice_valid, linked_receipt_valid

        if linked_receipt_valid(data, cid):
            continue  # Proven condition link; it does not relax any other blocked condition.
        key = "choice:" + str(value["choice_group_id"]) if value.get("choice_group_id") else \
            "field:" + cid
        receipt = answers.get(key, {})
        if not valid_receipt(data, key, receipt, cid):
            blocked.add(cid)
        elif groups.get(str(value.get("choice_group_id")), {}).get(
                "origin") == "FORM_capacity_choice" and not capacity_choice_valid(data, cid):
            blocked.add(cid)  # Only the selected, applicable option of the region.
        elif not value.get("choice_group_id") and (receipt.get("value") != value.get("value")
                                                   or receipt.get("user_quote") != value.get(
                                                       "user_quote")):
            blocked.add(cid)
    return blocked
