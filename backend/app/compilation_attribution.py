"""Necessary FORM subject constraints, never sufficient evidence to write.

Read explicit subjects in a paragraph or bounded table label/value rows. Do
not use the model's label/conditions, carry an owner between body paragraphs
or tables, merge people, or infer that locations/contacts coincide.
Unrecognised contexts remain unclassified and retain all historical gates.
"""

import re

PERSON = re.compile(
    r"\b(?:sottoscritt[oa](?:/a)?|firmatari[oa]|direttore\s+tecnico|"
    r"responsabile\s+della\s+progettazione|professionista(?:\s+designat[oa])?|"
    r"nome\s+e\s+cognome|socio)\b", re.IGNORECASE,
)
COMPANY = re.compile(
    r"\b(?:denominazione(?:/ragione\s+sociale)?|ragione\s+sociale|sede\s+legale)\b|"
    r"\b(?:dell['’]|della\s+|dello\s+|di\s+)"
    r"(?:società|impresa|azienda|operatore\s+economico|studio/società/consorzio)\b",
    re.IGNORECASE,
)
LOCATION = re.compile(
    r"(?P<studio>\bstudio\s+(?:in|professionale)\b)|"
    r"(?P<residence>\bresiden(?:za|te)\b)|(?P<legal_office>\bsede\s+legale\b)",
    re.IGNORECASE,
)
TABLE_PERSON = re.compile(
    r"(?:(?:il(?:/la)?|la)\s+)?sottoscritt[oa](?:/a)?|firmatari[oa]|"
    r"nome\s+e\s+cognome|direttore\s+tecnico|professionista(?:\s+designat[oa])?",
    re.IGNORECASE,
)
TABLE_COMPANY = re.compile(
    r"denominazione(?:/ragione\s+sociale|\s+sociale)?|ragione\s+sociale|"
    r"società(?:\s+di\s+(?:ingegneria|professionisti))?|impresa|azienda|"
    r"sede\s+legale(?:\s*\([^)]*\))?", re.IGNORECASE,
)
TABLE_PROPERTY = re.compile(
    r"data\s+(?:e\s+luogo\s+di\s+nascita|di\s+(?:nascita|abilitazione))|"
    r"luogo\s+di\s+nascita|codice\s+fiscale(?:\s+operatore\s+economico)?|"
    r"(?:pec|e[- ]?mail|telefono|cellulare\s*\+\s*telefono)|"
    r"qualifica\s+professionale|residenza|comune(?:\s+di\s+residenza|\s+studio\s+professionale)?|"
    r"forma\s+giuridica|partita\s+iva(?:\s+operatore\s+economico)?|"
    r"ordine\s+professionale\s+di\s+appartenenza|"
    r"numero\s+di\s+iscrizione\s+all['’]albo\s+professionale",
    re.IGNORECASE,
)


def _table_target(candidate, catalog, paragraphs):
    """Only fixed-label/value rows in this table; never inferred repeat headers.

    A new owner replaces the previous one. An empty/unknown/complex row is a
    boundary. Bare 'operatore economico' is ambiguous (can be a person), so it
    also stops inheritance rather than asserting that the owner is a company.
    """
    location = candidate["location"]
    table = next((t for b in catalog["blocks"] for t in b.get("tables", [])
                  if t["id"] == location.get("table_id")), None)
    if table is None:
        return None
    target = location["row_index"]
    row = table["rows"][target]
    if (len(row) != 2 or candidate["context_id"] not in
            [row[1]["id"], *row[1]["paragraph_ids"]]):
        return None
    occupied = {c["context_id"] for c in catalog["candidates"].values()}
    owner, evidence, path = None, None, []
    for index, row in enumerate(table["rows"][:target + 1]):
        if (len(row) != 2 or any("vertical_merge" in c or c.get("table_ids") for c in row)
                or any(p in occupied for p in row[0]["paragraph_ids"])
                or row[0]["id"] in occupied
                or any(paragraphs[p].get("controls") for c in row for p in c["paragraph_ids"])):
            owner, evidence, path = None, None, []
            continue
        label = " ".join(paragraphs[p]["text"] for p in row[0]["paragraph_ids"]).strip()
        normalized = " ".join(label.split()).rstrip(":").strip()
        current = {"row_index": index, "label_cell_id": row[0]["id"],
                   "paragraph_ids": row[0]["paragraph_ids"], "quote": label}
        if TABLE_PERSON.fullmatch(normalized):
            owner, evidence, path = "person", current, []
        elif TABLE_COMPANY.fullmatch(normalized):
            owner, evidence, path = "company", current, []
        elif not TABLE_PROPERTY.fullmatch(normalized):
            owner, evidence, path = None, None, []
        path.append(current)
    if owner is None:
        return None
    return owner, {"format": "table_label_value", "table_id": table["id"],
                   "target_cell_id": table["rows"][target][1]["id"],
                   "subject_anchor": evidence, "label_path": path}, path[-1]["quote"]


def check_source_target(candidate_id, catalog, fact):
    """Veto demonstrable owner/property contradictions independently of binding.

Entity compatibility does not demonstrate identity or role. Existing SOURCE
binding, factual, condition and review checks remain necessary. Only explicit
conflicting location qualifiers are compared, without extracting new values.
"""
    result = {"result": "not_determined", "semantic_review_required": True,
              "validation_codes": [], "validation_errors": [],
              "source_subject": fact.get("subject"), "source_entity": fact.get("entity")}
    candidate = catalog["candidates"][candidate_id]
    if candidate["type"] != "text":
        return result
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    paragraph = paragraphs.get(candidate["context_id"])
    marker, prefix = f"[[{candidate_id}]]", ""
    if paragraph and "range" in candidate:
        marked = paragraph.get("text_with_fields", "")
        if marked.count(marker) == 1:
            prefix = marked.split(marker)[0]
    # Only the text before this exact physical destination can introduce its
    # owner; a later company name must not retype earlier personal fields.
    owners = [(m.end(), entity, m.group()) for entity, pattern in
              [("person", PERSON), ("company", COMPANY)] for m in pattern.finditer(prefix)]
    local_prefix = re.split(r"\[\[[^]]+\]\]", prefix)[-1]
    target = None
    if owners:
        _, expected, anchor = max(owners)
        target = expected, {
            "paragraph_id": paragraph["id"], "subject_anchor": anchor,
            "marked_prefix": prefix + marker}
    elif table_target := _table_target(candidate, catalog, paragraphs):
        expected, evidence, local_prefix = table_target
        target = expected, evidence
    if target:
        expected, evidence = target
        result.update(expected_entity=expected, form_evidence=evidence)
        if fact.get("entity") != expected:
            result["validation_codes"].append("source_subject_type_mismatch")
            result["validation_errors"].append(
                "Il soggetto SOURCE non coincide con il tipo di soggetto richiesto dal FORM")
        else:
            result["result"] = "compatible_type_only"
    # Bound location qualification to the current property, not every property
    # following a studio/address earlier in the same paragraph.
    target_scopes = list(LOCATION.finditer(local_prefix))
    if target_scopes:
        target_scope = target_scopes[-1].lastgroup
        contradictions = []
        for proof in fact.get("source_evidence", []):
            scopes = {m.lastgroup for m in LOCATION.finditer(proof["quote"])}
            if scopes and target_scope not in scopes:
                contradictions.append(proof)
        if contradictions:
            result.update(expected_property_scope=target_scope,
                          incompatible_source_evidence=contradictions)
            result["validation_codes"].append("source_property_scope_mismatch")
            result["validation_errors"].append(
                "La proprietà SOURCE citata riguarda un ambito diverso "
                "da quello richiesto dal FORM")
    if result["validation_codes"]:
        result["result"] = "rejected"
    return result
