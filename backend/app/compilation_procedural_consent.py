"""Bounded FORM-derived assent gate, independent of SOURCE factual grounding.

Recognizes explicit commitment verbs in a physical paragraph's marked clause.
Does not infer consent from facts, model labels, export or another USER decision.
Unknown layouts are not claimed to be semantically classified by this check.
"""

import hashlib
import json
import re

COMMITMENT = re.compile(
    r"\b(?:accett(?:are|a|o|ano)|acconsent(?:ire|e|o|ono)|"
    r"autorizz(?:are|a|o|ano)|elegg(?:ere|e|o|ono)|"
    r"(?:mi|si|ci)\s+impegn(?:o|a|iamo|ano))\b", re.I)
MARKER = re.compile(r"\[\[([^\[\]]+)\]\]")


def explicit_assent(quote):
    """A closed question may receive yes; an export or unrelated confirmation may not."""
    text = re.sub(r"^\s*\d+[.):]\s*", "", " ".join(quote.casefold().split())).strip(" .!;")
    if re.search(r"\b(?:non|no|forse|so|saprei|vedremo|decidere)\b", text):
        return False
    if re.fullmatch(r"(?:s[iì](?:[, :]\s*)?)?(?:confermo|autorizzo|accetto|acconsento)?", text):
        return bool(text)
    return bool(re.match(r"(?:s[iì][, :]\s*)?(?:confermo|autorizzo|accetto|acconsento)\b", text)
                and re.search(r"\b(?:dichiarazione|comunicazioni|notifiche|impegno|domicilio|"
                              r"ricezione)\b", text))


def _values(data, ids, users, fields):
    """Values that would actually be written: USER values or grounded SOURCE proposals."""
    values = {}
    for cid in ids:
        if cid not in data["writable_ids"] or cid not in fields:
            continue
        field = fields[cid]
        value = users.get(cid, {}).get("value")
        if cid not in users and (field.get("validation") == "GROUNDED_PROPOSAL"
                or field.get("proposal_grounding") == "GROUNDED_PROPOSAL"):
            value = field.get("proposed_value", field.get("value"))
        if isinstance(value, str) and value.strip() or value is True:
            values[cid] = value
    return values


def _requirement(scope, clause, values):
    key = "authorization:" + hashlib.sha256(json.dumps(
        scope, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
    rendered = MARKER.sub(lambda m: str(values.get(m[1], "________")), clause)
    question = ("Autorizzi espressamente, per questa procedura, la dichiarazione "
                "seguente con i dati indicati?\n" + rendered.strip())
    return {"key": key, "authorization": scope, "question": question}


def requirements(data):
    if (data.get("audit") or {}).get("version") != 12:
        return []
    from app.compilation_branch_evidence import effective_user_values

    users = effective_user_values(data)
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    catalog = data["catalog"]
    result = []
    for block in catalog["blocks"]:
        for paragraph in block["paragraphs"]:
            marked = paragraph.get("text_with_fields", paragraph.get("text_with_choices", ""))
            # Never carry a commitment across a paragraph, sentence or list-clause boundary.
            for clause in re.split(r"[;\n]|(?<=[.!?])\s+(?=[A-ZÀ-Ý])", marked):
                if not COMMITMENT.search(clause):
                    continue
                values = _values(data, MARKER.findall(clause), users, fields)
                if not values:
                    continue
                scope = {"template_sha256": catalog["template_sha256"],
                    "session_artifact_path": data.get("artifact_path"),
                    "field_ids": list(values), "values": values,
                    "form_evidence": {"paragraph_id": paragraph["id"],
                                      "quote": paragraph["text"], "role": "form"},
                    "marked_clause": clause}
                result.append(_requirement(scope, clause, values))
    if data.get("option_authorization_revision") == 1:
        from app.compilation_option_regions import option_regions

        # V14: a value printed under an option needs assent to the WHOLE clause.
        # Branch, condition or checkbox selections never satisfy this requirement.
        for region in option_regions(catalog):
            values = _values(data, region["field_ids"], users, fields)
            if not values:
                continue
            scope = {"template_sha256": catalog["template_sha256"],
                "session_artifact_path": data.get("artifact_path"),
                "field_ids": list(values), "values": values,
                "form_evidence": {"paragraph_id": region["paragraph_id"],
                                  "quote": region["text"], "role": "form"},
                "marked_clause": region["marked_clause"], "kind": "option_clause"}
            result.append(_requirement(scope, region["marked_clause"], values))
    return result


def accepted(data, requirement):
    from app.compilation_chat import has_user_alternatives

    receipt = (data.get("dialogue") or {}).get("answers", {}).get(requirement["key"], {})
    return bool(requirement["authorization"]["session_artifact_path"]
        and receipt.get("provenance") == "USER" and receipt.get("action") == "CONDITION_TRUE"
        and receipt.get("applies") is True and receipt.get("user_quote")
        and explicit_assent(receipt["user_quote"])
        and not has_user_alternatives(receipt["user_quote"])
        and receipt.get("question") == requirement["question"]
        and receipt.get("authorization") == requirement["authorization"])


def blocked_fields(data):
    if "audit" not in data:
        # The chat's public session deliberately omits the full SOURCE audit.
        # These flags are derived by review_fields on the server; _selected
        # independently recomputes the gate from the private state at export.
        return {f["candidate_id"] for f in data.get("fields", [])
                if f.get("procedural_authorization", {}).get("required")
                and not f["procedural_authorization"].get("confirmed")}
    return {cid for r in requirements(data) if not accepted(data, r)
            for cid in r["authorization"]["field_ids"]}


def questions(data):
    answers = (data.get("dialogue") or {}).get("answers", {})
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    pool = []
    for r in requirements(data):
        if r["key"] in answers:
            continue
        ids = r["authorization"]["field_ids"]
        conditions = {c for cid in ids for c in fields[cid].get("conditions", [])}
        if any(data["audit"].get("conditions", {}).get(c, {}).get("result") == "false"
               or answers.get("condition:" + c, {}).get("applies") is False for c in conditions):
            continue
        pool.append({**r, "kind": "applicability", "field_ids": ids,
            "label": "Autorizzazione della dichiarazione procedurale", "alternatives": [],
            "condition": r["authorization"]["form_evidence"]["quote"],
            "context": r["question"], "impact": len(ids)})
    return pool


def receipt_scope(data, slot):
    current = next((r for r in requirements(data) if r["key"] == slot["key"]), None)
    if (not current or current["authorization"] != slot.get("authorization")
            or current["question"] != slot.get("question")
            or not current["authorization"]["session_artifact_path"]):
        raise ValueError("La conferma non riguarda la dichiarazione e i valori correnti")
    return current["authorization"]
