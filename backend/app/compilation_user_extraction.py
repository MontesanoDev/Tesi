"""Literal USER data extraction, before (never instead of) the independent guard.

Only FORM-owned personal groups of the active name question are eligible. No
inference of roles, applicability, declarations or checkbox choices. Every extra
destination gets its own ordinary scope check; unsupported text remains visible.
"""

import re
from copy import deepcopy

LABELS = {"name": "Nome e cognome", "birth": "Comune di nascita",
          "birth_province": "Provincia di nascita", "date": "Data di nascita",
          "residence": "Comune di residenza", "residence_province": "Provincia di residenza",
          "address": "Indirizzo di residenza", "house": "Numero civico di residenza",
          "cf": "Codice fiscale personale"}
UNCERTAIN = re.compile(r"\b(?:non|forse|oppure|ovvero|circa|sconosciut[oa]|ignot[oa])\b|\?", re.I)
PARTS = re.compile(r"\b(?P<birth>nat[oa]\s+a|luogo\s+di\s+nascita\s*:)\s*|"
                   r"\b(?P<date>data\s+di\s+nascita\s*:)\s*|"
                   r"\b(?P<residence>residente\s+(?:a|in)|comune\s+di\s+residenza\s*:)\s*|"
                   r"\b(?P<address>via|viale|piazza|corso)\s+|"
                   r"\b(?P<cf>C\.?F\.?\s*:?|codice\s+fiscale\s*:)\s*|"
                   r"\b(?P<boundary>in\s+qualità\s+di|della\s+società|"
                   r"(?:il|la)\s+(?:direttore|direttrice|socio|socia|responsabile))\b", re.I)
PREFIX = re.compile(r"^(?:(?:il|la)\s+)?(?:sottoscrittore|sottoscrittrice|sottoscritt[oa]|"
                    r"firmatari[oa]|nome\s+e\s+cognome)\s*(?:è|:)?\s*|^sono\s+", re.I)


def enabled(data):
    return data.get("user_extraction_revision") == 1


def simple_name(value):
    """A conservative shape check, not proof that a person exists or may sign."""
    return (isinstance(value, str) and 1 <= len(value.split()) <= 8
            and bool(re.fullmatch(r"[^\W\d_]+(?:[’'\- ][^\W\d_]+)*", value.strip()))
            and not UNCERTAIN.search(value) and not PARTS.search(value)
            and not re.search(r"\b(?:sono|sottoscrittore|firmatario|confermo|nato|nata|"
                              r"residente|vive|abita|nascita|residenza|indirizzo|codice|"
                              r"fiscale|qualità|lavora|è|il|in|oppure)\b", value, re.I)
            and not re.search(r"\s+o\s+", value, re.I))


def groups(data):
    if not enabled(data):
        return []
    from app.compilation_signatory_form import signatory_groups
    from app.compilation_source_reuse import _form_groups

    result = signatory_groups(data["catalog"])
    # The complete inline grammar also handles "residente\nin" across paragraphs.
    for ids, paragraphs, _ in _form_groups(data["catalog"]):
        result = [g for g in result if g["name_id"] != ids[0]]
        props = ["name", "birth", "birth_province", "date", "residence",
                 "residence_province", "address", "cf"]
        result.append({"name_id": ids[0], "targets": dict(zip(ids, props)),
                       "target_proofs": {cid: [p for p in paragraphs if
                           f"[[{cid}]]" in p.get("text_with_fields", "")] for cid in ids[:8]}})
    known = {g["name_id"] for g in result}
    return result + [g for g in personal_groups(data["catalog"]) if g["name_id"] not in known]


def personal_groups(catalog):
    """Explicit name/property rows also work for applicants/contacts, without signing powers.

    An unknown label, another name or a non-personal property ends inheritance.
    These groups are used only for USER extraction, never for SOURCE signatory reuse.
    """
    from app.compilation_signatory_form import MARKER, _events, _property

    result, active, previous = [], None, None
    for text, proofs, _ in _events(catalog):
        markers = list(MARKER.finditer(text))
        if not markers:
            active, previous = None, None
            continue
        offset = 0
        for marker in markers:
            prefix = text[offset:marker.start()].strip().lstrip(") ,;").rstrip(" :")
            offset = marker.end()
            cid = marker[1]
            is_name = bool(re.fullmatch(r"(?:nome\s+e\s+cognome|nominativo)(?:\s+"
                r"(?:del|della|dell['’])\s*[^_,:;]+)?", prefix, re.I))
            prop = "name" if is_name else _property(prefix, previous)
            if (catalog["candidates"].get(cid, {}).get("type") != "text"
                    or prop not in LABELS):
                active, previous = None, None
                continue
            if is_name:
                active = {"name_id": cid, "targets": {}, "target_proofs": {}}
                result.append(active)
            elif not active or prop in active["targets"].values() or len(active["targets"]) >= 9:
                active, previous = None, None
                continue
            active["targets"][cid] = prop
            active["target_proofs"][cid] = proofs
            previous = prop
    return result


def target_fields(data):
    """Stable FORM metadata for atomic facts; MODEL conditions are retained, never cleared."""
    if not enabled(data):
        return {}
    from app.compilation_source_reuse import signatory_fields

    fields = {f["candidate_id"]: f for f in (data.get("audit") or {}).get("fields", [])}
    fields.update(signatory_fields(data))
    result = {}
    for group in groups(data):
        name = fields.get(group["name_id"], {})
        for cid, prop in group["targets"].items():
            field = fields.get(cid)
            proofs = group["target_proofs"].get(cid, [])
            if (prop not in LABELS or not field or not proofs or field.get("validation_errors")
                    or field.get("kind") in {"signature", "decorative", "choice", "declaration"}
                    or data["catalog"]["candidates"].get(cid, {}).get("type") != "text"):
                continue
            result[cid] = {**field, "label": field.get("label") or LABELS[prop],
                "kind": "data", "form_evidence": field.get("form_evidence") or {
                    "paragraph_id": proofs[0]["id"], "quote": proofs[0]["text"]},
                "conditions": sorted(set(field.get("conditions", [])) | (
                    set(name.get("conditions", [])) if cid != group["name_id"] else set()))}
    return result


def restore_fields(data, audit):
    """Reconstruct metadata of captured facts after immutable MODEL output is revalidated."""
    if not enabled(data):
        return audit
    users = (data.get("dialogue") or {}).get("user_values", {})
    pending = (data.get("dialogue") or {}).get("extraction_pending", {})
    ids = {cid for cid, v in users.items() if v.get("extraction")} | set(pending)
    prepared = target_fields({**data, "audit": audit})
    return {**audit, "fields": [prepared.get(f["candidate_id"], f)
                               if f["candidate_id"] in ids else f for f in audit["fields"]]}


def frames(data, slots):
    """Private backend destinations, never an LLM-selected list of IDs."""
    from app.compilation_scope_review import target

    fields, result = target_fields(data), {}
    for slot in slots:
        if slot["kind"] != "value" or len(slot["field_ids"]) != 1:
            continue
        matches = [g for g in groups(data) if g["name_id"] == slot["field_ids"][0]]
        if len(matches) != 1:
            continue
        group = matches[0]
        members = {cid: {"property": prop, "field": fields[cid],
                         "scope": target(data, "field:" + cid, [cid]),
                         "form_text": " ".join(p["text"] for p in group["target_proofs"][cid])}
                   for cid, prop in group["targets"].items() if cid in fields and prop in LABELS
                   and cid in data["writable_ids"]}
        if group["name_id"] in members:
            result[str(slot["slot"])] = {"name_id": group["name_id"], "members": members,
                                        "question": slot.get("question", "")}
    return result


def _place(text):
    if UNCERTAIN.search(text) or re.search(r"\bo\b", text, re.I):
        return None
    match = re.fullmatch(r"([^\d;,()]+?)(?:\s*\(([A-Z]{2})\))?", text.strip())
    return (match[1].strip(), match[2]) if match else None


def _date(text):
    from app.compilation_chat import normalize_date

    return bool(re.fullmatch(r"\d{1,2}[/.-]\d{1,2}[/.-]\d{4}|\d{1,2}\s+[a-zà]+\s+\d{4}",
                             text, re.I) and normalize_date(text))


def extract(frame, quote):
    """Recognize literal components; unknown/ambiguous fragments never become a name."""
    matches = list(PARTS.finditer(quote))
    if not matches:
        return None
    name = PREFIX.sub("", quote[:matches[0].start()].strip()).strip(" ,;:.")
    if not simple_name(name):
        return {"values": {}, "issues": ["Indica un solo nome e cognome per la persona richiesta."]}
    properties, issues, ambiguous = {"name": name}, [], set()
    seen = set()
    for i, match in enumerate(matches):
        kind = match.lastgroup
        if kind == "boundary":
            issues.append("Gli altri soggetti, ruoli e dichiarazioni richiedono domande distinte.")
            break
        if kind in seen:
            properties = {"name": name}
            ambiguous.update(set(LABELS) - {"name"})
            issues.append("Sono presenti dati ripetuti: precisa quelli della persona richiesta.")
            break
        seen.add(kind)
        part = quote[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(quote)]
        part = part.strip(" ,;:.")
        if kind == "birth":
            place, separator, date = part.partition(" il ")
            if _place(place):
                properties["birth"], properties["birth_province"] = _place(place)
            else:
                ambiguous.update({"birth", "birth_province"})
                issues.append("Precisa il luogo di nascita.")
            if separator:
                if _date(date):
                    properties["date"] = date
                else:
                    ambiguous.add("date")
                    issues.append("Precisa la data di nascita.")
        elif kind == "date":
            if _date(part):
                properties["date"] = part
            else:
                ambiguous.add("date")
                issues.append("Precisa la data di nascita.")
        elif kind == "residence":
            if _place(part):
                properties["residence"], properties["residence_province"] = _place(part)
            else:
                ambiguous.update({"residence", "residence_province"})
                issues.append("Precisa il comune di residenza.")
        elif kind == "address":
            if not UNCERTAIN.search(part) and re.fullmatch(r"[^,;\n]+", part):
                properties["address"] = match[0] + part
                properties["street"] = part
            else:
                ambiguous.update({"address", "house"})
                issues.append("Precisa l'indirizzo di residenza.")
        elif kind == "cf":
            if re.fullmatch(r"[A-Z0-9]{16}", part):
                properties["cf"] = part
            else:
                ambiguous.add("cf")
                issues.append("Precisa il codice fiscale personale.")
    values = {}
    props = {m["property"] for m in frame["members"].values()}
    for cid, member in frame["members"].items():
        prop = member["property"]
        value = properties.get(prop)
        if prop in {"birth", "residence"} and value and prop + "_province" not in props:
            province = properties.get(prop + "_province")
            value += f" ({province})" if province else ""
        if prop in {"address", "house"} and properties.get("street"):
            street = properties["street"]
            if "house" in props:
                split = re.fullmatch(r"(.+?)\s+(\d+[A-Za-z]?(?:[/\-][A-Za-z0-9]+)?)", street)
                if not split:
                    ambiguous.update({"address", "house"})
                    issues.append("Precisa separatamente via e numero civico.")
                    continue
                street = split[1]
                if prop == "house":
                    value = split[2]
            if prop == "address":
                if re.search(r"\bvia(?:/piazza)?\s+(?:_|\[)", member["form_text"], re.I):
                    if not re.match(r"via\s+", properties["address"], re.I):
                        issues.append("Il tipo di strada non coincide con quello del modulo.")
                        continue
                    value = street
                else:
                    value = properties["address"].removesuffix(properties["street"]) + street
        if value and value in quote:
            values[cid] = {"value": value, "user_quote": quote}
    # A mentioned but ambiguous property must not be silently replaced from SOURCE.
    unresolved = [cid for cid, member in frame["members"].items()
                  if cid not in values and (member["property"] in ambiguous
                                            or properties.get(member["property"]))]
    if unresolved and not issues:
        issues.append("Alcuni dati non sono separabili con certezza: precisa i campi mancanti.")
    return {"values": values, "issues": list(dict.fromkeys(issues)), "unresolved": unresolved}


def prepare(available_frames, replies, message):
    """Replace a compound name proposal before its check, retain every original proposal."""
    records, changed = [], []
    for reply in replies:
        frame = available_frames.get(str(reply.slot))
        parsed = (extract(frame, reply.user_quote) if frame and reply.action == "VALUE"
                  and reply.user_quote in message and reply.selected_options is None else None)
        if parsed is None:
            changed.append(reply)
            continue
        record = {"parent_slot": reply.slot, "original_reply": reply.model_dump(),
                  **parsed, "proofs": {}, "refused": {}}
        records.append(record)
        name = parsed["values"].get(frame["name_id"])
        changed.append(reply.model_copy(update={"value": name["value"], "normalized_value": None})
                       if name else reply)
    return changed, records


async def verify_extras(message, context, available_frames, records, allowed_parents, *, request):
    """Unchanged guard, max four atomic facts per batch; at most eight extras per name."""
    from app.compilation_chat import ClarificationReply
    from app.compilation_reply_guard import verify_field_replies

    tokens, diagnostics = [], []
    for record in records:
        if record["parent_slot"] not in allowed_parents:
            continue
        frame = available_frames[str(record["parent_slot"])]
        extra = [(cid, value) for cid, value in record["values"].items() if cid != frame["name_id"]]
        for start in range(0, min(len(extra), 8), 4):
            batch = extra[start:start + 4]
            slots, replies, targets = [], [], {}
            for n, (cid, value) in enumerate(batch, 1):
                member = frame["members"][cid]
                slots.append({"slot": n, "kind": "value", "label": member["field"]["label"],
                    "question": frame["question"], "context": member["form_text"],
                    "affected_field_count": 1, "affected_fields": [member["field"]["label"]]})
                replies.append(ClarificationReply(slot=n, action="VALUE", **value))
                targets[str(n)] = member["scope"]
            ctx = {**context, "slots": slots, "form_scope": {
                **context["form_scope"], "slots": targets}}
            checked = await verify_field_replies(message, ctx, replies, request=request)
            tokens.append(checked.total_tokens)
            diagnostics.append({"candidate_ids": [cid for cid, _ in batch], "raw": checked.raw,
                                "accepted_slots": sorted(checked.allowed_slots)})
            for n, (cid, _) in enumerate(batch, 1):
                if n in checked.scope_verifications:
                    record["proofs"][cid] = checked.scope_verifications[n]
                else:
                    record["refused"][cid] = checked.reasons.get(n, "UNCHECKED")
    return tokens, diagnostics


def persist(data, layout, slots, message, records):
    """Recompute the extraction under the transaction, check each proof, then save facts."""
    from app.compilation_chat import ClarificationReply
    from app.compilation_reply_guard import REASON_TEXT
    from app.compilation_scope_review import scope_receipt, valid_receipt
    from app.compilation_sessions import validate_value
    from app.compilation_value_completeness import value_check

    if not enabled(data) or not records:
        return [], [], False
    available = frames(data, list(slots.values()))
    dialogue = data["dialogue"]
    answers, users = dialogue.setdefault("answers", {}), dialogue.setdefault("user_values", {})
    history = dialogue.setdefault("user_extractions", [])
    pending = dialogue.setdefault("extraction_pending", {})
    accepted, refused = [], []
    for record in records:
        original = ClarificationReply.model_validate(record["original_reply"])
        _, recomputed = prepare(available, [original], message)
        if (not recomputed or record["parent_slot"] != original.slot
                or record["values"] != recomputed[0]["values"]
                or record["issues"] != recomputed[0]["issues"]
                or record.get("unresolved", []) != recomputed[0].get("unresolved", [])):
            raise ValueError("Estrazione USER non corrispondente alla risposta e al FORM correnti")
        frame = available[str(original.slot)]
        history.append({"message": message, **deepcopy(record)})
        dialogue.setdefault("latest_extraction_issues", []).extend(record["issues"])
        name_id = frame["name_id"]
        name = record["values"].get(name_id)
        parent = answers.get("field:" + name_id, {})
        if (not name or not valid_receipt(data, "field:" + name_id, parent, name_id)
                or parent.get("value") != name["value"]
                or parent.get("user_quote") != name["user_quote"]):
            continue  # A rejected parent never distributes its other properties.
        users[name_id]["extraction"] = {"original_quote": original.user_quote}
        for cid in record.get("unresolved", []):
            if "field:" + cid not in answers:
                pending[cid] = {"user_quote": original.user_quote,
                                "reason": "Dato espresso ma non separabile con certezza"}
        for cid, value in record["values"].items():
            if cid == name_id:
                continue
            member = frame["members"][cid]
            key, field = "field:" + cid, member["field"]
            reply = ClarificationReply(slot=1, action="VALUE", **value)
            receipt = scope_receipt(data, key, [cid], reply)
            error = None
            if cid in users or key in answers:
                error = "Il campo ha già una risposta: serve una correzione esplicita dedicata"
            elif record["proofs"].get(cid) != receipt["scope_validation"]:
                error = REASON_TEXT.get(record["refused"].get(cid, "UNCHECKED"),
                                        REASON_TEXT["UNCHECKED"])
            else:
                checked = validate_value(layout, {**field, "id": cid}, value["value"], user=True)
                complete = value_check(data, cid, value["value"], user_quote=value["user_quote"])
                if (checked["validation_codes"] or checked["written_value"] != value["value"]
                        or complete and complete["result"] != "COMPLETE"):
                    error = "Il valore richiede un chiarimento per questa posizione del modulo"
            if error:
                refused.append({"label": field["label"], "kind": "value", "key": key,
                                "reason": error})
                if key not in answers:
                    pending[cid] = {**value, "reason": error}
                continue
            users[cid] = {**value, "provenance": "USER", "label": field["label"],
                          "extraction": {"original_quote": original.user_quote}}
            answers[key] = {**value, **receipt, "action": "VALUE", "provenance": "USER",
                            "label": field["label"], "ambiguity_check": "SEMANTIC_GUARD",
                            "question": frame["question"]}
            accepted.append({**answers[key], "candidate_id": cid})
            pending.pop(cid, None)
    return accepted, refused, True


def blocked_fields(data):
    return (set((data.get("dialogue") or {}).get("extraction_pending", {}))
            if enabled(data) else set())


def mark_usable(data, accepted):
    """Report the same current USER blockers as export_selection, without authorizing any."""
    from app.compilation_form_applicability import blocked_fields as inapplicable
    from app.compilation_procedural_consent import blocked_fields as consent
    from app.compilation_scope_review import blocked_user_fields
    from app.compilation_value_completeness import blocked_fields as incomplete

    if not enabled(data) or not any(r.get("candidate_id") for r in accepted):
        return
    blocked = (blocked_user_fields(data) | inapplicable(data) | consent(data) | incomplete(data)
               | blocked_fields(data))
    for record in accepted:
        if record.get("candidate_id") and record["action"] == "VALUE":
            record["usable_for_draft"] = record["candidate_id"] not in blocked
