"""FORM-owned signatory/property links, independent of MODEL labels and SOURCE.

Only contiguous, explicitly labelled paragraphs and simple label/value rows.
An unknown label, new subject, complex table or repeated name ends inheritance.
Recognising a target supplies no identity, personal value, power or applicability.
"""

import re

MARKER = re.compile(r"\[\[([^\[\]]+)\]\]")
SIGNER = re.compile(r"\b(?:sottoscritt[oa](?:/[oa])?|sottoscrittore|firmatari[oa])\b", re.I)
COMPANY = re.compile(r"\b(?:operatore\s+economico|società|studio/società/consorzio|"
                     r"denominazione|ragione\s+sociale|sede\s+legale)\b", re.I)
OTHER_PERSON = re.compile(r"\b(?:direttore\s+tecnico|socio|associato|professionista\s+"
                          r"(?:designato|incaricato)|responsabile\s+tecnico)\b", re.I)
CONDITIONAL = re.compile(r"\b(?:se|qualora|ove|in\s+caso)\b", re.I)


def _events(catalog):
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    candidates = catalog["candidates"]
    occupied = {c["context_id"] for c in candidates.values() if "context_id" in c}
    for block in catalog["blocks"]:
        if not block.get("tables"):
            for p in block["paragraphs"]:
                yield p.get("text_with_fields", p["text"]), [p], False
            continue
        for table in block["tables"]:
            for row in table["rows"]:
                if (len(row) != 2 or any(c.get("table_ids") or "vertical_merge" in c for c in row)
                        or row[0]["id"] in occupied
                        or any(pid in occupied for pid in row[0]["paragraph_ids"])
                        or any(paragraphs[pid].get("controls")
                               for cell in row for pid in cell["paragraph_ids"])):
                    yield "BOUNDARY", [], True
                    continue
                label = " ".join(paragraphs[p]["text"] for p in row[0]["paragraph_ids"])
                cid = row[1]["id"]
                proofs = [paragraphs[p] for c in row for p in c["paragraph_ids"]]
                # Only a genuinely empty single value cell is a table destination.
                if (cid not in candidates or any(paragraphs[p]["text"].strip()
                                                 for p in row[1]["paragraph_ids"])):
                    yield "BOUNDARY", [], True
                else:
                    yield label + " [[" + cid + "]]", proofs, True


def _property(prefix, previous):
    text = " ".join(prefix.split()).strip(" ,:;")
    if SIGNER.search(text):
        return "name"
    if re.fullmatch(r"(?:nome\s+e\s+cognome|nominativo)", text, re.I):
        return "name"
    if re.search(r"(?:data\s+e\s+luogo\s+di\s+nascita|luogo\s+e\s+data\s+di\s+nascita)$",
                 text, re.I):
        return "birth_date"
    if re.search(r"(?:nat[oa](?:/[oa])?\s+a|luogo\s+di\s+nascita)$", text, re.I):
        return "birth"
    if re.search(r"data\s+di\s+nascita$", text, re.I) or (
        text.casefold() == "il" and previous in {"birth", "birth_province"}
    ):
        return "date"
    if re.search(r"(?:residente\s+(?:a|in)|comune\s+di\s+residenza)$", text, re.I):
        return "residence"
    if re.fullmatch(r"residenza", text, re.I):
        return "residence_full"
    if text == "(" and previous in {"birth", "residence"}:
        return previous + "_province"
    if re.search(r"provincia\s+di\s+(nascita|residenza)$", text, re.I):
        return "birth_province" if "nascita" in text.casefold() else "residence_province"
    if re.search(r"(?:via(?:/piazza)?|indirizzo\s+di\s+residenza)$", text, re.I):
        return "address"
    if re.fullmatch(r"n(?:\.|umero)?", text, re.I) and previous == "address":
        return "house"
    if re.search(r"(?:c\.?\s*f\.?|codice\s+fiscale(?:\s+personale)?(?:\s+n\.?)?)$", text, re.I):
        return "cf"
    if re.search(r"(?:in\s+qualità\s+di(?:\s*\(carica\s+sociale:.*\))?|carica\s+sociale)$",
                 text, re.I):
        return "role"
    return None


def signatory_groups(catalog):
    groups, active, pending, previous, steps = [], None, "", None, 0
    conditional_heading = False

    def close():
        if active and active.get("name_id"):
            groups.append(active.copy())

    for text, proofs, table_row in _events(catalog):
        if not text.strip():
            continue
        steps += 1
        if steps > 24:
            close()
            active, pending, previous = None, "", None
        matches = list(MARKER.finditer(text))
        if not matches:
            if (SIGNER.search(text) and not OTHER_PERSON.search(text)
                    and not CONDITIONAL.search(text) and not conditional_heading):
                close()
                active = {"targets": {}, "target_proofs": {}, "proofs": [], "operator_id": None}
                pending, previous, steps = "", None, 0
            elif active and re.fullmatch(r"\s*(?:residente|in qualità di)\s*", text, re.I):
                pending += " " + text
            else:
                close()
                active, pending, previous = None, "", None
                conditional_heading = bool(CONDITIONAL.search(text))
            continue
        offset = 0
        for match in matches:
            prefix = (pending if offset == 0 else "") + text[offset:match.start()]
            pending = ""
            cid = match[1]
            candidate = catalog["candidates"].get(cid, {})
            prop = _property(prefix.strip().lstrip(") ,"), previous)
            if (candidate.get("type") != "text" or
                    OTHER_PERSON.search(prefix) and prop != "role"):
                close()
                active, previous = None, None
                offset = match.end()
                continue
            if COMPANY.search(prefix) and not SIGNER.search(prefix) and prop != "role":
                if active:
                    active["operator_id"] = cid if re.search(
                        r"(?:società|operatore\s+economico|denominazione|ragione\s+sociale)",
                        prefix, re.I) else None
                close()
                active, previous = None, None
                offset = match.end()
                continue
            if SIGNER.search(prefix):
                close()
                if conditional_heading or CONDITIONAL.search(prefix):
                    active, previous = None, None
                    offset = match.end()
                    continue
                active = {"targets": {}, "target_proofs": {}, "proofs": [], "operator_id": None}
                previous, steps = None, 0
            if active is None:
                offset = match.end()
                continue
            if prop is None or prop in active["targets"].values():
                close()
                active, previous = None, None
                offset = match.end()
                continue
            if prop == "name":
                active["name_id"] = cid
            active["targets"][cid] = prop
            active["target_proofs"][cid] = proofs
            active["proofs"].extend(p for p in proofs if p not in active["proofs"])
            previous = prop
            offset = match.end()
        if active:
            pending = "" if table_row else text[offset:]
    close()
    return groups


def inline_signatory_names(catalog):
    """An explicit name in its own physical paragraph, including inside a cell.

    No inheritance across cells, empty companion destinations, subject guesses,
    or expansion to any other property. Existing groups retain precedence.
    """
    groups = []
    for block in catalog["blocks"]:
        if not block.get("tables"):
            continue  # Body grammar already owns conditional-heading boundaries.
        paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
        preceding = block.get("preceding_body_paragraph_ids", [])
        if preceding and CONDITIONAL.search(paragraphs[preceding[-1]]["text"]):
            continue
        for paragraph in block["paragraphs"]:
            text = paragraph.get("text_with_fields", "")
            markers = list(MARKER.finditer(text))
            if len(markers) != 1:
                continue
            marker = markers[0]
            prefix = text[:marker.start()].strip(" :")
            if not re.fullmatch(r"(?:il(?:/la)?|la)?\s*(?:sottoscritt[oa](?:/[oa])?|"
                                r"sottoscrittore|firmatari[oa])", prefix, re.I):
                continue
            if text[marker.end():].strip(" ,.;:"):
                continue
            cid = marker[1]
            candidate = catalog["candidates"].get(cid, {})
            if candidate.get("type") != "text" or candidate.get("context_id") != paragraph["id"]:
                continue
            cells = [cell for table in block["tables"] for row in table["rows"] for cell in row
                     if paragraph["id"] in cell["paragraph_ids"]]
            if len(cells) != 1:
                continue
            prior = cells[0]["paragraph_ids"][:cells[0]["paragraph_ids"].index(paragraph["id"])]
            if any(CONDITIONAL.search(paragraphs[p]["text"]) for p in prior):
                continue
            groups.append({"name_id": cid, "targets": {cid: "name"}, "operator_id": None,
                           "proofs": [paragraph], "target_proofs": {cid: [paragraph]}})
    return groups
