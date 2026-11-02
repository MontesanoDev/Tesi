"""Conversation over the existing global session; no alternate writer or authorization.

Addressable FORM targets are distinct from the one question actually asked. Free
instructions are bound server-side, then checked by the ordinary independent guard.
"""

import re
from copy import deepcopy


def enabled(data):
    return data.get("conversation_revision") == 1


def fields(data):
    from app.compilation_source_reuse import signatory_fields
    from app.compilation_user_extraction import target_fields

    return {**{f["candidate_id"]: f for f in data.get("audit", {}).get("fields", [])},
            **signatory_fields(data), **target_fields(data)}


def targets(data):
    """All known FORM destinations, including answered/deferred ones; never fabricated IDs."""
    if not enabled(data) or data.get("phase") != "REVIEW":
        return []
    from app.compilation_global_dialogue import question_pool

    fresh = deepcopy(data)
    fresh["dialogue"].update(answers={}, latest_turn=None, requested_keys=[])
    pool = question_pool(fresh, all_targets=True)
    by_key = {q["key"]: q for q in pool}
    for cid, field in fields(data).items():
        if (cid not in data["writable_ids"] or not field.get("form_evidence")
                or field.get("validation_errors")
                or data["catalog"]["candidates"].get(cid, {}).get("type") != "text"
                or field.get("kind") in {"signature", "decorative", "choice", "declaration"}):
            continue
        by_key["field:" + cid] = {
            "key": "field:" + cid, "kind": "value", "field_ids": [cid],
            "label": field.get("label") or "Dato del modulo", "condition": "",
            "context": field["form_evidence"]["quote"], "impact": 1,
            "alternatives": [a["value"] for a in field.get("alternatives", [])]}
    # Choices are still guarded, condition-checked and cardinality-validated downstream.
    for key, group in data.get("audit", {}).get("choice_groups", {}).items():
        if group.get("validation") != "GROUNDED_GROUP" or group["selection"] == "unknown":
            continue
        by_key.setdefault("choice:" + key, {
            "key": "choice:" + key, "kind": "choice", "choice_group_id": key,
            "label": group["label"], "condition": "", "context": group["form_evidence"]["quote"],
            "field_ids": list(group["options"]), "impact": len(group["options"]),
            "alternatives": [o["label"] for o in group["options"].values()],
            "selection": group["selection"], "min_selected": group["min_selected"]})
    answers = data.get("dialogue", {}).get("answers", {})
    return [{**q, "target": n, "previous_action": answers.get(q["key"], {}).get("action")}
            for n, q in enumerate(by_key.values(), 1)]


def public_targets(data, entries):
    """Compact routing/explanation context. Lack of a proposal is never SOURCE absence."""
    from app.compilation_field_outcomes import field_outcomes

    outcomes = field_outcomes(data, set())["campi"]
    values = fields(data)
    users = data.get("dialogue", {}).get("user_values", {})
    return [{**{k: q.get(k) for k in ("target", "kind", "label", "previous_action")},
             "context": q.get("context", "")[:240],
             "alternatives": q.get("alternatives", []),
             "state": list(dict.fromkeys(outcomes.get(cid, {"esito": "non_valutato"})["esito"]
                       for cid in q["field_ids"])),
             "current_values": [users.get(cid, {}).get("value") or values.get(cid, {}).get(
                 "proposed_value", values.get(cid, {}).get("value")) for cid in q["field_ids"]][:3]}
            for q in entries]


def bind_edits(compilation, edits):
    """Private temporary slots, never presented as questions the user actually saw."""
    from app.compilation_scope_review import context
    from app.compilation_user_extraction import frames

    data = compilation.get("conversation_data") or {}
    if not enabled(data) or compilation.get("paused") or not edits:
        raise ValueError("Modifiche libere non disponibili: riprendi la sessione")
    available = {q["target"]: q for q in targets(data)}
    if (len({e.target for e in edits}) != len(edits)
            or any(e.target not in available for e in edits)):
        raise ValueError("Destinazione della modifica non univoca")
    slots = [{**available[e.target], "slot": n, "direct_instruction": True,
              "destinations_shown": False, "question": ""}
             for n, e in enumerate(edits, 1)]
    return {**compilation, "question": {"kind": "clarifications", "slots": slots,
            "field_ids": [], "message": (compilation.get("question") or {}).get("message", "")},
            "form_scope": context(data, slots), "user_value_frames": frames(data, slots)}, slots


def complete_person_reply(compilation, replies, message):
    """Keep the complete literal personal sentence when the router shortened its quote.

    The existing extractor owns segmentation. Only a sentence containing the routed
    quote and exactly the same parsed name is eligible; every extra still needs its
    own guard proof. No concatenation across sentences or subjects.
    """
    from app.compilation_chat import contains_span
    from app.compilation_user_extraction import extract

    if not compilation.get("conversation_data") or not enabled(compilation["conversation_data"]):
        return replies
    frames = compilation.get("user_value_frames", {})
    slots = {q["slot"]: q for q in (compilation.get("question") or {}).get("slots", [])}
    expanded, covered = {}, set()
    for reply in replies:
        frame = frames.get(str(reply.slot))
        if not frame or reply.action != "VALUE":
            continue
        candidates = []
        for sentence in re.split(r"(?<=[.!?])\s+", message):
            parsed = extract(frame, sentence) if contains_span(sentence, reply.user_quote) else None
            name = (parsed or {}).get("values", {}).get(frame["name_id"], {}).get("value")
            if name == reply.value and len((parsed or {}).get("values", {})) > 1:
                candidates.append((sentence, parsed))
        if len(candidates) == 1:
            sentence, parsed = candidates[0]
            expanded[reply.slot] = reply.model_copy(update={"user_quote": sentence})
            # Drop only redundant equal proposals; conflicting edits remain visible to guards.
            for other in replies:
                ids = slots.get(other.slot, {}).get("field_ids", [])
                found = parsed["values"].get(ids[0], {}) if len(ids) == 1 else {}
                if (other.slot != reply.slot and other.action == "VALUE" and
                        found.get("value") == other.value
                        and contains_span(sentence, other.user_quote)):
                    covered.add(other.slot)
    return [expanded.get(r.slot, r) for r in replies if r.slot not in covered]


def selective_pool(data, pool):
    """One useful next question, no questionnaire over every empty destination."""
    requested = set(data.get("dialogue", {}).get("requested_keys", []))
    pending = set(data.get("dialogue", {}).get("extraction_pending", {}))
    useful = [q for q in pool if q["key"] in requested or q.get("retry") or
              q.get("documented") or q.get("documented_alternatives") or
              q.get("form_owned") and q["kind"] == "value" or
              set(q.get("field_ids", [])) & pending]
    return sorted(useful, key=lambda q: (
        q["key"] not in requested, not q.get("retry"),
        -q.get("documented", 0), not q.get("documented_alternatives"), -q.get("impact", 0)))[:1]


def person_groups(data):
    from app.compilation_source_reuse import _form_groups, _signatory_groups
    from app.compilation_user_extraction import groups

    result = {}
    for group in [*groups(data), *_signatory_groups(data)]:
        result.setdefault(group["name_id"], set()).update(group["targets"])
    for ids, _, _ in _form_groups(data["catalog"]):
        result.setdefault(ids[0], set()).update(ids[:9])
    return result


def archive(dialogue, key, *, reason, message):
    answer = dialogue.setdefault("answers", {}).pop(key, None)
    cid = key.removeprefix("field:")
    user = (dialogue.setdefault("user_values", {}).pop(cid, None)
            if key.startswith("field:") else None)
    if answer or user:
        dialogue.setdefault("superseded", []).append({"key": key, "answer": answer,
            "user_value": user, "reason": reason, "message": message})


def before_change(data, slot, reply, message):
    """Withdraw dependent receipts BEFORE storing a changed identity. Preserve all history."""
    if not enabled(data):
        return
    dialogue = data["dialogue"]
    if slot["kind"] == "value" and reply.action == "VALUE":
        cid = slot["field_ids"][0]
        value = reply.normalized_value or reply.value
        field = fields(data).get(cid, {})
        old = dialogue.get("user_values", {}).get(cid, {}).get("value") or field.get(
            "proposed_value", field.get("value"))
        if old != value and cid in person_groups(data):
            dependent = person_groups(data)[cid] - {cid}
            for other in dependent:
                archive(dialogue, "field:" + other, reason="identity_changed", message=message)
                dialogue.get("extraction_pending", {}).pop(other, None)
                dialogue.get("reviewed_candidate_fingerprints", {}).pop(other, None)
            for key, receipt in list(dialogue.get("answers", {}).items()) if old else []:
                if key.startswith(("condition:", "choice:")) and dependent & set(
                        receipt.get("affected_fields", [])):
                    archive(dialogue, key, reason="identity_changed", message=message)
            dialogue.setdefault("identity_changes", []).append({"candidate_id": cid,
                "previous_value": old, "value": value, "message": message})
    archive(dialogue, slot["key"], reason="user_correction", message=message)


def record_action(data, slot, reply, message):
    if not enabled(data):
        return
    dialogue = data["dialogue"]
    requested = dialogue.setdefault("requested_keys", [])
    if slot["key"] in requested:
        requested.remove(slot["key"])
    excluded = dialogue.setdefault("excluded_fields", {})
    if reply.action in {"SKIP", "REFUSE", "REOPEN"}:
        for cid in slot["field_ids"]:
            excluded[cid] = {"key": slot["key"], "action": reply.action, "message": message}
        if reply.action == "REOPEN":
            requested.append(slot["key"])
    elif reply.action in {"VALUE", "CONDITION_TRUE", "CONDITION_FALSE"}:
        for cid in slot["field_ids"]:
            if excluded.get(cid, {}).get("key") == slot["key"]:
                excluded.pop(cid)


def blocked_fields(data):
    if not enabled(data):
        return set()
    dialogue = data.get("dialogue", {})
    blocked = set(dialogue.get("excluded_fields", {}))
    # Documented options alone cannot select a checkbox in this conversational flow.
    # The ordinary scope/cardinality validators still verify every USER choice.
    for cid, candidate in data["catalog"]["candidates"].items():
        if candidate.get("type") != "checkbox":
            continue
        user = dialogue.get("user_values", {}).get(cid, {})
        receipt = dialogue.get("answers", {}).get("choice:" + str(user.get("choice_group_id")), {})
        if receipt.get("action") != "VALUE" or receipt.get("selected_options") is None:
            blocked.add(cid)
    return blocked


def reconcile_identity(data, audit):
    """The immutable original proposal cannot reintroduce another person's properties.

    Only structurally proven person groups participate; SOURCE reuse then runs its usual
    evidence checks. A withdrawn MODEL proposal stays available in the audit history.
    """
    if not enabled(data):
        return audit
    from app.compilation_role_records import _same_person
    from app.compilation_source_reuse import _selection

    audit = deepcopy(audit)
    values = {f["candidate_id"]: f for f in audit["fields"]}
    for name_id, members in person_groups(data).items():
        selected = _selection({**data, "audit": audit}, name_id)
        if not selected:
            continue
        name = selected[0]
        for cid in members - {name_id}:
            field = values.get(cid)
            if not field or not (field.get("proposal_grounding") or
                                     field.get("validation") == "GROUNDED_PROPOSAL"):
                continue
            fact = audit.get("facts", {}).get(
                field.get("fact_id") or field.get("proposed_fact_id"), {})
            subject = (field.get("source_reuse") or {}).get("subject") or fact.get("subject")
            if subject and _same_person(subject, name):
                continue
            previous = deepcopy(field)
            field.update(validation="REVIEW_REQUIRED", proposal=None, proposal_grounding=None,
                         value=None, proposed_value=None, written_value=None, source_evidence=[],
                         disposition="review", superseded_identity_proposal=previous)
            field.pop("source_reuse", None)
    return audit
