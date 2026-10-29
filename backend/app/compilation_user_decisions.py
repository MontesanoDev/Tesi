"""Narrow FORM-derived dialogue agenda, never a compilation/choice authorization.

Only explicit selection instructions, execution designations, attestations and
place/date labels are recognized. MODEL coverage claims do not create requests.
Unknown layouts/branches stay unresolved. A grouped receipt needs a separate
per-destination check before any value or checkbox can be exported.
"""

import hashlib
import json
import re

SHORT_LINES, SHORT_CHARS, HEAD_CHARS = 6, 400, 240


def compact_question(question, lines, entries=()):
    """The question with only the indispensable FORM lines; the full text becomes details.

    A long FORM excerpt keeps its first line (the instruction) and a count of the options or
    lines; nothing is reworded or chosen. Decisions never authorize writes either way.
    """
    lines = [line for line in lines if line.strip()]
    if len(lines) <= SHORT_LINES and sum(map(len, lines)) <= SHORT_CHARS:
        return question + "\n" + "\n".join(lines), []
    head = lines[0] if len(lines[0]) <= HEAD_CHARS else (
        lines[0][:HEAD_CHARS - 1].rsplit(" ", 1)[0] + "…")
    columns = list(dict.fromkeys(" ".join(name.split()) for _, names in entries
                                 for name in names))
    summary = (f"{len(entries)} voci, colonne: {', '.join(columns)}." if entries else
               f"Seguono altre {len(lines) - 1} righe del modulo.")
    return f"{question}\n{head}\n{summary} Il testo completo è nei dettagli.", lines


def decision_questions(data, reserved_ids=()):
    if (data.get("audit") or {}).get("version") != 12:
        return []
    catalog = data["catalog"]
    blocks = catalog["blocks"]
    paragraphs = [p for b in blocks for p in b["paragraphs"]]
    by_id = {p["id"]: p for p in paragraphs}
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    answers = (data.get("dialogue") or {}).get("answers", {})
    users = (data.get("dialogue") or {}).get("user_values", {})
    reserved = set(reserved_ids)
    pool = []

    def available(cid):
        field = fields.get(cid, {})
        if (cid in reserved or cid in users or "field:" + cid in answers
                or cid not in data["writable_ids"] or not field
                or field.get("proposal") is not None
                or field.get("validation") == "GROUNDED_PROPOSAL"
                or field.get("proposal_grounding") == "GROUNDED_PROPOSAL"
                or field.get("kind") in {"signature", "decorative"}):
            return False
        return all(data["audit"].get("conditions", {}).get(c, {}).get("result") == "true"
                   or answers.get("condition:" + c, {}).get("applies") is True
                   for c in field.get("conditions", [])) and not any(
            data["audit"].get("conditions", {}).get(c, {}).get("result") == "false"
            or answers.get("condition:" + c, {}).get("applies") is False
            for c in field.get("conditions", []))

    def append(kind, label, ids, proofs, question, options=()):
        remaining = [cid for cid in ids if available(cid)]
        material = [catalog.get("template_sha256"), kind, ids, proofs]
        key = "decision:" + hashlib.sha256(json.dumps(
            material, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
        if not remaining or key in answers:
            return
        context, entries = "\n".join(p["quote"] for p in proofs), []
        if options:
            lines, previous = [proofs[0]["quote"]], None
            for option in options:
                columns = [name for cid, name in option["columns"] if cid in remaining]
                if not columns:
                    continue
                if option["table_id"] != previous:
                    lines.extend([option["title"], " | ".join(option["headers"])])
                    previous = option["table_id"]
                lines.append(option["label"] + ": " + ", ".join(columns))
                entries.append((option["label"], columns))
            context = "\n".join(lines)
        text, details = compact_question(question, context.split("\n"), entries)
        pool.append({"key": key, "kind": "decision", "decision_type": kind,
            "label": label, "field_ids": remaining, "condition": "", "context": context,
            "form_evidence": proofs, "alternatives": [], "impact": len(remaining),
            "write_authorized": False, "question": text,
            **({"details": details} if details else {})})
        reserved.update(remaining)

    def proof(p):
        return {"paragraph_id": p["id"], "quote": p["text"], "role": "form"}

    # Preference tables are grouped by their *explicit* preceding instruction.
    # They remain textual targets, not fabricated native choice groups.
    instruction, preference_ids, preference_proofs, options, gap = None, [], [], [], 0

    def flush():
        if instruction is not None:
            append("preferences", "Categorie e fasce d'incarico", preference_ids,
                   [proof(instruction), *preference_proofs],
                   "Quali categorie, servizi e fasce d'incarico scegli? Indica solo quelle "
                   "ancora aperte.",
                   options)

    for block in blocks:
        if block.get("tables") and instruction is not None:
            for table in block["tables"]:
                rows = table["rows"]
                header = [" ".join(by_id[pid]["text"] for pid in cell["paragraph_ids"])
                          for cell in rows[0]]
                if len(header) < 2 or not all(re.search(
                    r"\b(?:fascia|preferenza)\b", h, re.I) for h in header[1:]):
                    continue
                preceding = [by_id[pid] for pid in block.get("preceding_body_paragraph_ids", [])]
                title = preceding[-1] if preceding else instruction
                if proof(title) not in preference_proofs:
                    preference_proofs.append(proof(title))
                for row in rows[1:]:
                    label = " ".join(by_id[pid]["text"] for pid in row[0]["paragraph_ids"])
                    if len(row) != len(header) or not label.strip():
                        continue
                    columns = []
                    for index, cell in enumerate(row[1:], 1):
                        cid = cell["id"]
                        candidate = catalog["candidates"].get(cid, {})
                        if (candidate.get("type") != "text" or any(
                            by_id[pid]["text"].strip() for pid in cell["paragraph_ids"])):
                            continue
                        preference_ids.append(cid)
                        columns.append((cid, by_id[rows[0][index]["paragraph_ids"][0]]["text"]))
                        for pid in [*row[0]["paragraph_ids"], *rows[0][index]["paragraph_ids"]]:
                            item = proof(by_id[pid])
                            if item not in preference_proofs:
                                preference_proofs.append(item)
                    options.append({"table_id": table["id"], "title": title["text"],
                                    "headers": header[1:], "label": label, "columns": columns})
            gap = 0
            continue
        for paragraph in block["paragraphs"]:
            text = paragraph["text"]
            command = (re.search(r"\b(?:barrare|selezionare|scegliere)\b", text, re.I)
                       and re.search(r"\b(?:settor[ei]|tipologie|categorie|preferenze)\b",
                                     text, re.I))
            if command:
                flush()
                instruction, gap = paragraph, 0
                preference_ids, preference_proofs, options = [], [], []
            elif text.strip():
                gap += 1
                if paragraph.get("controls") or gap > 6:
                    flush()
                    instruction, preference_ids, preference_proofs, options = None, [], [], []
    flush()

    for index, paragraph in enumerate(paragraphs):
        text = paragraph["text"]
        ids = [cid for cid, c in catalog["candidates"].items()
               if c.get("context_id") == paragraph["id"]]
        if (paragraph.get("controls") and re.search(r"\bcorrispondono a verità\b", text, re.I)
                and not re.search(r"\bin caso di\b", text, re.I)):
            proofs = [proof(paragraph)]
            for following in paragraphs[index + 1:index + 33]:
                if (following.get("controls") or "text_with_fields" in following
                        or not following["text"].strip()):
                    break
                proofs.append(proof(following))
            append("attestation", "Dichiarazioni e attestazioni", ids, proofs,
                   "Puoi confermare espressamente queste dichiarazioni del modulo? Non le "
                   "ricavo dai dati aziendali.")
        elif (re.search(r"\bprofessionist[ai]\b", text, re.I) and (
            re.search(r"\bconferimento\b.*\bprestazione\b", text, re.I)
            or re.search(r"\bintegrazione delle prestazioni\b", text, re.I)
        )):
            # Consecutive blank lines are one decision, never separate people.
            for following in paragraphs[index + 1:index + 7]:
                if (following.get("controls") or "text_with_fields" not in following
                        or re.search(r"\w", following["text"].replace("_", ""))):
                    break
                ids.extend(cid for cid, c in catalog["candidates"].items()
                           if c.get("context_id") == following["id"] and c.get("type") == "text")
            integration = bool(re.search(r"\bintegrazione delle prestazioni\b", text, re.I))
            append("designation", "Professionista incaricato dell'integrazione" if integration
                   else "Professionisti esecutori", ids, [proof(paragraph)],
                   "Chi designi per questo incarico? Non lo ricavo dai ruoli aziendali.")
        elif re.match(r"\s*Luogo e data\b", text, re.I) and "text_with_fields" in paragraph:
            append("location_date", "Luogo e data della domanda", ids, [proof(paragraph)],
                   "Quali luogo e data indichi?")
    return pool
