"""Conversation over the existing global session; no alternate writer or authorization.

Addressable FORM targets are distinct from the one question actually asked. Free
instructions are bound server-side, then checked by the ordinary independent guard.
"""

import re
from copy import deepcopy

MAX_TURN_PARTS = 4
MIN_BRANCH_UNLOCKS = 3
BARE_OPTION = re.compile(r"\W*(?:(?:l[ao]\s+)?(?:opzione|numero|n\.?)|l[ao])?\s*(\d{1,2})\W*", re.I)
SENTENCE = re.compile(r"(?<=[.!?;])\s+(?=[A-ZÀ-Ý«\"(\d])|\n+")
# A label naming a capacity is a branch of the FORM, never a mere label of the participant.
CAPACITY_WORD = re.compile(r"\b(?:rappresentant\w*|professionist\w*|prestator\w*|societ\w*|studio|"
                           r"consorzi\w*|raggruppament\w*|mandatari\w*|mandant\w*|capogruppo|"
                           r"sottoscritt\w*|firmatari\w*|procurator\w*|associat\w*)\b", re.I)


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
        # The FORM capacity region exists only under an accepted condition. Its option is still
        # marked only by this explicit choice, and it can be given before it is the next question.
        capacity = (data.get("conversation_turn_revision") == 1
                    and group.get("origin") == "FORM_capacity_choice")
        if group.get("validation") != "GROUNDED_GROUP" or (
                group["selection"] == "unknown" and not capacity):
            continue
        by_key.setdefault("choice:" + key, {
            "key": "choice:" + key, "kind": "choice", "choice_group_id": key,
            "label": group["label"], "condition": "", "context": group["form_evidence"]["quote"],
            "field_ids": list(group["options"]), "impact": len(group["options"]),
            "alternatives": [o["label"] for o in group["options"].values()],
            "selection": group["selection"], "min_selected": group["min_selected"]})
    answers = data.get("dialogue", {}).get("answers", {})
    return [{**current_identity_scope(data, q), "target": n,
             "previous_action": answers.get(q["key"], {}).get("action")}
            for n, q in enumerate(by_key.values(), 1)]


def current_identity_scope(data, question):
    """Ask about the selected person's available data, not withdrawn facts.

    Later SOURCE derivations still require the ordinary scope extension. This
    affects the operation presented to USER/guard, never the MODEL condition.
    """
    from app.compilation_signatory_form import CONDITIONAL, SIGNER

    if (question["kind"] != "applicability" or question.get("authorization")
            or not SIGNER.search(question.get("condition", ""))
            or CONDITIONAL.search(question.get("condition", ""))):
        return question
    users = data.get("dialogue", {}).get("user_values", {})
    known = fields(data)

    def available(cid):
        field = known.get(cid, {})
        return users.get(cid) or (not field.get("validation_errors") and (
            field.get("validation") == "GROUNDED_PROPOSAL"
            or field.get("proposal_grounding") == "GROUNDED_PROPOSAL")
            and field.get("proposed_value", field.get("value")) is not None)

    for name, members in person_groups(data).items():
        if (name in question["field_ids"] and set(question["field_ids"]) <= members
                and users.get(name)):
            ids = [cid for cid in question["field_ids"] if available(cid)]
            return {**question, "field_ids": ids, "impact": len(ids),
                    "affected_fields": [known.get(cid, {}).get("label", "Dato personale")
                                        for cid in ids]}
    return question


def public_targets(data, entries):
    """Compact routing/explanation context. Lack of a proposal is never SOURCE absence."""
    from app.compilation_field_outcomes import field_outcomes

    outcomes = field_outcomes(data, set())["campi"]
    values = fields(data)
    users = data.get("dialogue", {}).get("user_values", {})
    groups = person_groups(data)
    from app.compilation_signatory_form import CONDITIONAL, SIGNER

    def identity_confirmations(q):
        members = groups.get(q["field_ids"][0], set()) if q["kind"] == "value" else set()
        return [c["target"] for c in entries if members and c["kind"] == "applicability"
                and not c.get("authorization") and q["field_ids"][0] in c["field_ids"]
                and set(c["field_ids"]) <= members
                and SIGNER.search(c.get("condition", ""))
                and not CONDITIONAL.search(c.get("condition", ""))]

    return [{**{k: q.get(k) for k in ("target", "kind", "label", "previous_action")},
             "context": q.get("context", "")[:240],
             "identity_confirmations": identity_confirmations(q),
             "alternatives": q.get("alternatives", []),
             "state": list(dict.fromkeys(outcomes.get(cid, {"esito": "non_valutato"})["esito"]
                       for cid in q["field_ids"])),
             "current_values": [users.get(cid, {}).get("value") or values.get(cid, {}).get(
                 "proposed_value", values.get(cid, {}).get("value")) for cid in q["field_ids"]][:3]}
            for q in entries]


def mixed_turns(compilation):
    """An answer to the active question may also carry instructions on other destinations."""
    return bool(compilation and (compilation.get("conversation_data") or {}).get(
        "conversation_turn_revision") == 1)


def without_repeated_edits(replies, edits):
    """One datum given twice by the router is one datum, on the destination it names.

    Real Minervino turns: «Sì, confermo…» and the signatory's name both on slot 1, the name also as
    an edit on its target. Two replies on one slot are both refused, so the confirmation was lost
    and asked again. Only an identical value and quote go; the rest meets the usual guard.
    """
    given = {(e.get("value"), e.get("user_quote")) for e in edits
             if isinstance(e, dict) and e.get("action") == "VALUE"}
    return [r for r in replies if not (
        isinstance(r, dict) and r.get("action") == "VALUE"
        and (r.get("value"), r.get("user_quote")) in given)]


def state_revision(compilation):
    return bool(compilation and (compilation.get("conversation_data") or {}).get(
        "dialogue_state_revision") == 1)


def literal_choice_values(replies, compilation, message=None):
    """A choice is its option numbers, which the guard checks against the user's sentence.

    The value of a choice reply is that sentence, as the router contract says. Real runs copied the
    FORM label there and a correct, verified choice was refused as not grounded. Any span of the
    quote already passed that check, so nothing about the choice itself is taken on trust here.

    A message that is only the number of the chosen option is itself the quote. Real manual turn:
    «4» after the numbered question; the model quoted the previous message, the guard agreed on the
    option and the literal check answered «not in the USER message». Another number stays refused.
    """
    from app.compilation_chat import contains_span

    if not mixed_turns(compilation):
        return replies
    kinds = {q.get("slot"): q.get("kind")
             for q in (compilation.get("question") or {}).get("slots", [])}
    bare = BARE_OPTION.fullmatch(message or "") if state_revision(compilation) else None
    result = []
    for r in replies:
        chosen = (isinstance(r, dict) and kinds.get(r.get("slot")) == "choice"
                  and r.get("action") == "VALUE" and r.get("selected_options") is not None)
        if chosen and bare and r["selected_options"] == [int(bare[1])]:
            r = {**r, "user_quote": message.strip(), "value": message.strip()}
        elif chosen and r.get("user_quote") and not (
                r.get("value") and contains_span(r["user_quote"], r["value"])):
            r = {**r, "value": r["user_quote"]}
        result.append(r)
    return result


def literal_quotes(replies, compilation, message):
    """(replies, the ones quoting what the message does not say).

    A value literally in the message is quoted with its sentence: real manual turn, «puoi mettere
    …» quoted as «metti …» and a verified name was refused. A quote with no such value goes back to
    the router: only the current message authorizes anything, never the history or the sources.
    """
    from app.compilation_chat import contains_span

    if not state_revision(compilation):
        return replies, []
    result, invented = [], []
    for r in replies:
        quote = r.get("user_quote") if isinstance(r, dict) else None
        if not quote or contains_span(message, quote):
            result.append(r)
            continue
        value = r.get("value")
        sentence = next((s for s in sentences(message) if value and contains_span(s, value)), None)
        if r.get("action") == "VALUE" and sentence:
            result.append({**r, "user_quote": sentence})
            continue
        result.append(r)
        invented.append(r)
    return result, invented


def sentences(message):
    return [s.strip() for s in SENTENCE.split(message or "") if s and s.strip()]


def unrouted_sentences(message, quotes):
    """Sentences of the message no reply quoted: what a turn with many intents may have dropped."""
    from app.compilation_chat import contains_span

    rest = []
    for sentence in sentences(message):
        if len(sentence.split()) < 3 and not re.search(r"\d", sentence):
            continue  # «Grazie.», «Ok.»: nothing to route.
        if not any(q and (contains_span(sentence, q) or contains_span(q, sentence))
                   for q in quotes):
            rest.append(sentence)
    return rest


def _label_only(item, governed, candidates):
    """The condition's FORM quote is the text right before a slot it governs: no clause at all."""
    def clean(text):
        text = re.sub(r"\[\[[^\]]*\]\]|[._…]{2,}|[☐☑☒“”\"]", " ", str(text or ""))
        return " ".join(text.casefold().split()).strip(" ,;:.")

    quote = clean((item.get("form_evidence") or {}).get("quote"))
    if not quote or CAPACITY_WORD.search(quote):
        return False
    return any(before and (quote == before or (
        quote.startswith(before + " ") and len(quote) <= len(before) + 30))
        for before in (clean((candidates.get(c, {}).get("slot_context") or {}).get("before"))
                       for c in governed))


def _company_of(audit, field):
    fact = (audit.get("facts") or {}).get(
        (field.get("proposal") or {}).get("fact_id") or field.get("fact_id")
        or field.get("proposed_fact_id"), {})
    if fact.get("entity") == "company" and fact.get("subject"):
        return " ".join(str(fact["subject"]).casefold().split())
    return None


def _label_company(data, key, field_ids):
    """The one company of a condition that is only the FORM label of a field it governs, or None."""
    audit = data.get("audit") or {}
    item = audit.get("conditions", {}).get(key, {})
    if item.get("aspect") not in {"participation", "identity"} or not _label_only(
            item, field_ids, (data.get("catalog") or {}).get("candidates") or {}):
        return None
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    found = {c for c in (_company_of(audit, fields.get(cid, {})) for cid in field_ids) if c}
    return found.pop() if len(found) == 1 else None


def hide_labels_under_open_branch(data, pool):
    """While the branch about the same company is open, its label is not a question of its own.

    Real manual run: «dell'operatore economico», the literal label of its own field, held the
    company's 11 header fields as if it were a clause. Its answer comes from the branch
    (imply_label_receipts). Without such a branch the label is still asked, on its own.
    """
    if data.get("dialogue_state_revision") != 1:
        return pool
    audit = data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}

    def plain(q):
        return (q.get("kind") == "applicability" and not q.get("authorization")
                and not q.get("extension") and not q.get("stale_receipt"))

    labels = {q["key"]: company for q in pool if plain(q) and len(q.get("condition_ids", [])) == 1
              and (company := _label_company(data, q["condition_ids"][0], q["field_ids"]))}
    branches = [{_company_of(audit, fields.get(cid, {})) for cid in q["field_ids"]}
                for q in pool if plain(q) and q["key"] not in labels]
    return [q for q in pool if q["key"] not in labels
            or not any(labels[q["key"]] in companies for companies in branches)]


def imply_label_receipts(data):
    """A label takes the accepted USER confirmation of the branch about the same company.

    Same verified reply, own proof recomputed by the backend, `implied_by` naming its origin. It
    follows the branch at every turn: gone as soon as the branch is withdrawn, while an explicit
    USER answer on the label is never touched. It frees no person's data: a person's SOURCE
    proposal stays out unless another condition still governs it or the USER named that person.
    Returns the labels newly covered, for the receipt shown to the USER.
    """
    if data.get("dialogue_state_revision") != 1:
        return []
    from app.compilation_global_dialogue import documented_proposal
    from app.compilation_scope_review import proof, target, valid_receipt
    from app.compilation_source_reuse import pending_signatory_conditions

    audit = data.get("audit") or {}
    conditions = audit.get("conditions", {})
    answers = (data.get("dialogue") or {}).setdefault("answers", {})
    earlier = {k for k, r in answers.items() if r.get("implied_by")}
    for key in earlier:
        del answers[key]
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    branches = []
    for key, item in conditions.items():
        receipt = answers.get("condition:" + key, {})
        covered = receipt.get("affected_fields") or []
        if (item.get("aspect") in {"participation", "representation"} and covered
                and receipt.get("applies") is True
                and valid_receipt(data, "condition:" + key, receipt, covered[0])):
            branches.append(("condition:" + key, receipt,
                             {_company_of(audit, fields.get(cid, {})) for cid in covered}))
    branches.sort(key=lambda branch: -len(branch[1]["affected_fields"]))
    postponed, shown = pending_signatory_conditions(data), []
    for key, item in conditions.items():
        slot = "condition:" + key
        if (slot in answers or key in postponed or item.get("result", "unknown") != "unknown"
                or item.get("validation_errors") or not item.get("form_evidence")):
            continue
        governed = [f for f in fields.values() if key in f.get("conditions", [])
                    and not any(answers.get("condition:" + c, {}).get("applies") is False
                                for c in f.get("conditions", []))]
        company = _label_company(data, key, [f["candidate_id"] for f in governed])
        branch = company and next((b for b in branches if company in b[2]), None)
        if not branch:
            continue
        ids = [f["candidate_id"] for f in governed
               if _company_of(audit, f) == company or not documented_proposal(f)
               or f.get("source_reuse") or len(f.get("conditions", [])) > 1]
        receipt = {**deepcopy(branch[1]), "implied_by": branch[0], "affected_fields": ids}
        receipt["scope_validation"] = proof(target(data, slot, ids), receipt)
        answers[slot] = receipt
        if slot not in earlier:
            shown.append(item["form_evidence"]["quote"])
    return shown


def fit_turn_parts(replies, edits):
    """Keep a whole turn within four parts: (edits kept, quotes of the edits left out).

    A long message must not lose everything: answers to active questions stay, then writes come
    before deferrals, whose fields stay empty anyway. What is left out is told to the USER.
    """
    room = max(MAX_TURN_PARTS - len(replies), 0)
    if len(edits) <= room:
        return edits, []
    ranked = sorted(edits, key=lambda e: isinstance(e, dict) and e.get("action") in {
        "SKIP", "REFUSE"})
    return ranked[:room], [str(e.get("user_quote"))[:200] for e in ranked[room:]
                           if isinstance(e, dict) and e.get("user_quote")]


def bind_edits(compilation, edits, first_slot=1):
    """Private temporary slots, never presented as questions the user actually saw.

    From first_slot on when the same message also answers the active questions, which keep their
    numbers: every slot goes through the same guard and the same receipts.
    """
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
             for n, e in enumerate(edits, first_slot)]
    active = [] if first_slot == 1 else [
        q for q in (compilation.get("question") or {}).get("slots", [])
        if not set(q.get("field_ids", [])) & {c for s in slots for c in s["field_ids"]}]
    both = [*active, *slots]
    if len(slots) > MAX_TURN_PARTS:
        raise ValueError("Massimo quattro risposte e modifiche per turno")
    return {**compilation, "question": {"kind": "clarifications", "slots": both,
            "field_ids": [], "message": (compilation.get("question") or {}).get("message", "")},
            "form_scope": context(data, both), "user_value_frames": frames(data, both)}, slots


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


def branch_choice_unlocks(data, q):
    """Destinations an explicit choice settles: the proposals held on it, what its branch governs.

    Real campaign: 24 runs of 24 asked the FORM capacity choice before the selective questions, 0
    of 4 after, with up to 27 documented values suspended on a choice nobody asked for.
    """
    if data.get("checkbox_policy_revision") != 1 or q.get("kind") != "choice":
        return 0
    audit, dialogue = data.get("audit") or {}, data.get("dialogue") or {}
    records = dialogue.get("hold_records", {})
    settled = {cid for cid in dialogue.get("held_candidate_ids", [])
               if q["key"] in {records.get(cid, {}).get("blocker_key"),
                               (records.get(cid, {}).get("resolution") or {}).get("key")}}
    group = audit.get("choice_groups", {}).get(q.get("choice_group_id"), {})
    if group.get("origin") == "FORM_capacity_choice":
        branch = {c for keys in group.get("applicable", {}).values() for c in keys}
        settled |= {f["candidate_id"] for f in audit.get("fields", [])
                    if set(f.get("conditions", [])) & branch
                    and f.get("proposed_value", f.get("value")) is not None}
    return len(settled)


def selective_pool(data, pool):
    """One useful next question, no questionnaire over every empty destination."""
    requested = set(data.get("dialogue", {}).get("requested_keys", []))
    pending = set(data.get("dialogue", {}).get("extraction_pending", {}))
    useful = [q for q in pool if q["key"] in requested or q.get("retry") or
              q.get("documented") or q.get("documented_alternatives") or
              q.get("subject_uncertain") or
              q.get("form_owned") and q["kind"] == "value" or
              set(q.get("field_ids", [])) & pending or
              branch_choice_unlocks(data, q) >= MIN_BRANCH_UNLOCKS]
    # What the answer unlocks comes first: a signatory name opens a whole personal block.
    members = person_groups(data) if data.get("conversation_turn_revision") == 1 else {}

    def unlocks(q):
        return (len(members.get(q["field_ids"][0], ())) if q.get("form_owned")
                and q["kind"] == "value" else branch_choice_unlocks(data, q))

    chosen = sorted(useful, key=lambda q: (
        q["key"] not in requested, not q.get("retry"),
        -max(q.get("documented", 0), unlocks(q)), not q.get("documented_alternatives"),
        -q.get("impact", 0)))[:1]
    return [current_identity_scope(data, q) for q in chosen]


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


def receipt_depends_on_person(data, key, receipt, members, *, signer=False):
    """The condition's own scope, not the union of its downstream destinations.

    Grouped confirmations retain independent per-condition proofs. A company
    condition can govern a person's office without selecting that person. Unknown
    scope stays conservative; signer powers/consents never transfer to a new signer.
    """
    affected = set(receipt.get("affected_fields", []))
    if receipt.get("authorization"):
        return signer or bool(members & affected)
    if not key.startswith("condition:"):
        return bool(members & affected)
    condition = data.get("audit", {}).get("conditions", {}).get(key.removeprefix("condition:"), {})
    quote = condition.get("form_evidence", {}).get("quote", "")
    from app.compilation_signatory_form import SIGNER

    personal_clause = SIGNER.search(quote) or re.search(
        r"\b(?:legale\s+rappresentante|procurator[ei])\b", quote, re.I)
    if personal_clause and (signer or members & affected):
        return True
    if not members & affected:
        return False
    scope = condition.get("scope", [])
    if not scope or any(s.get("kind") != "candidate" for s in scope):
        return True
    return bool(members & {s.get("id") for s in scope})


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
            from app.compilation_source_reuse import _form_groups, _signatory_groups

            signer = cid in {g["name_id"] for g in _signatory_groups(data)} or any(
                ids[0] == cid for ids, _, _ in _form_groups(data["catalog"]))
            dependent = person_groups(data)[cid] - {cid}
            for other in dependent:
                archive(dialogue, "field:" + other, reason="identity_changed", message=message)
                dialogue.get("extraction_pending", {}).pop(other, None)
                dialogue.get("reviewed_candidate_fingerprints", {}).pop(other, None)
            for key, receipt in list(dialogue.get("answers", {}).items()) if old else []:
                if (key.startswith(("condition:", "choice:")) or receipt.get("authorization")) \
                        and receipt_depends_on_person(
                            data, key, receipt, dependent | {cid}, signer=signer):
                    archive(dialogue, key, reason="identity_changed", message=message)
                    condition = data["audit"].get("conditions", {}).get(
                        key.removeprefix("condition:"), {})
                    if (key.startswith("condition:") and cid in {
                            s.get("id") for s in condition.get("scope", [])}
                            and condition.get("aspect") == "identity"):
                        requested = dialogue.setdefault("requested_keys", [])
                        if key not in requested:
                            requested.append(key)
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
    # SOURCE reuse can discover an omitted FORM destination (e.g. the office).
    # Withdrawing that person's fact must not erase the physical target already
    # checked in an independent company receipt. Retain only FORM metadata, not
    # values, evidence, authority, validation verdicts or newly stamped receipts.
    previous = {f["candidate_id"]: f for f in data.get("audit", {}).get("fields", [])}
    for cid, field in values.items():
        old = previous.get(cid, {})
        if (not field.get("form_evidence") and not field.get("validation_errors")
                and old.get("form_evidence") and not old.get("validation_errors")
                and (old.get("source_reuse") or old.get("retained_form_target"))):
            field.update({k: deepcopy(old[k]) for k in (
                "label", "kind", "form_evidence", "conditions") if k in old})
            field["retained_form_target"] = True
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
