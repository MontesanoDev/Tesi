"""Bounded SOURCE reuse after a registered USER signatory selection.

No inference of a signatory from a company role. An exact, unique personal
record supplies properties; USER supplies only the selection. Every export
recomputes these proposals from current SOURCE and receipts. Unsupported FORM
layouts and ambiguous records remain unresolved. The model response is immutable.
"""

import re
from collections import Counter
from copy import deepcopy

from app.compilation_global import _allowed_sources, _citation_audit, _shared_facts
from app.compilation_global_contract import SourceSpan
from app.compilation_role_records import _identity as record_identity
from app.compilation_role_records import _same_person, _subject_records, _text, _uncertain
from app.compilation_sessions import validate_value

_MARKER = r"\[\[([^\[\]]+)\]\]"
# One explicit grammatical subject, stopping before the distinct operator.
# This deliberately supports only the complete, unambiguous inline grammar.
_SIGNATORY = re.compile(
    r"Il\s+sottoscritt[oa]\s+" + _MARKER + r",?\s*nat[oa]\s+a\s+" + _MARKER
    + r"\s*\(\s*" + _MARKER + r"\s*\)\s+il\s+" + _MARKER
    + r",?\s*residente\s+in\s+" + _MARKER + r"\s*\(\s*" + _MARKER
    + r"\s*\),?\s*(?:via|via/piazza)\s+" + _MARKER + r",?\s*C\.?F\.?\s*"
    + _MARKER + r",?\s*in\s+qualità\s+di\s+" + _MARKER
    + r"\s+dell[’']operatore\s+economico\s+" + _MARKER, re.I)
_PROPERTIES = {
    "luogo di nascita": "birth", "data di nascita": "date",
    "comune di residenza": "residence", "indirizzo di residenza": "address",
    "codice fiscale personale": "cf", "codice fiscale personale dimostrativo": "cf",
    "codice fiscale": "cf", "nome": "first", "cognome": "last",
}

_SELECTION = re.compile(
    r"(?:^|[.;\n])\s*(?:per (?:questa|la) (?:pratica|domanda)\s+)?"
    r"(?:il\s+)?firmatario\s+(?:scelto|designato)\s+(?:è|sarà|:)\s+([^,;.!?\n]+)", re.I)
_SELECTION_V13 = re.compile(
    r"(?:^|[.;\n])\s*(?:per (?:questa|la) (?:pratica|domanda|procedura)\s+)?"
    r"(?:il\s+)?firmatario\s+(?:scelto|designato)\s+"
    r"(?:per\s+(?:questa|la)\s+(?:pratica|domanda|procedura)\s*)?"
    r"(?:è|sarà|:)\s+([^,;.!?\n]+)", re.I)


def _signatory_groups(data):
    from app.compilation_signatory_form import inline_signatory_names, signatory_groups

    groups = signatory_groups(data["catalog"])
    if data.get("backend_revision") == 13:
        names = {g["name_id"] for g in groups}
        groups.extend(g for g in inline_signatory_names(data["catalog"])
                      if g["name_id"] not in names)
    return groups


def _selection(data, candidate_id):
    """An accepted literal selection, never a company role or unparsed start text."""
    from app.compilation_chat import has_user_alternatives

    dialogue = data.get("dialogue") or {}
    pattern = _SELECTION_V13 if data.get("backend_revision") == 13 else _SELECTION
    users, answers = dialogue.get("user_values", {}), dialogue.get("answers", {})
    user, receipt = users.get(candidate_id, {}), answers.get("field:" + candidate_id, {})
    if receipt.get("action") in {"UNKNOWN", "SKIP", "REFUSE"}:
        return None
    name = user.get("value")
    if (isinstance(name, str) and user.get("provenance") == "USER"
            and receipt.get("provenance") == "USER" and receipt.get("action") == "VALUE"
            and receipt.get("value") == name and receipt.get("user_quote") == user.get("user_quote")
            and _text(name) in _text(user.get("user_quote", ""))):
        return name, receipt
    selections = []
    for key, answer in answers.items():
        condition = data["audit"].get("conditions", {}).get(key.removeprefix("condition:"), {})
        quote = answer.get("user_quote", "")
        if (not key.startswith("condition:") or answer.get("provenance") != "USER"
                or answer.get("action") != "CONDITION_TRUE" or answer.get("applies") is not True
                or condition.get("validation") != "GROUNDED_PROPOSAL"
                or condition.get("validation_errors") or not condition.get("form_evidence")
                or not isinstance(quote, str) or _uncertain(quote)
                or (answer.get("ambiguity_check") != "SEMANTIC_GUARD"
                    and has_user_alternatives(quote))):
            continue
        for match in pattern.finditer(quote):
            selections.append((match[1].strip(), {
                **deepcopy(answer), "selection_receipt_key": key}))
    if len({_text(name) for name, _ in selections}) == 1:
        return selections[0]
    if selections:
        return None
    name_ids = {ids[0] for ids, _, _ in _form_groups(data["catalog"])} | {
        g["name_id"] for g in _signatory_groups(data)}
    if name_ids != {candidate_id}:
        return None
    # The context was acquired from this session's start turn by the backend,
    # not from SOURCE, MODEL output or unrelated conversation history. Interpret
    # only an explicit closed selection sentence, never a role or a bare name.
    requests = [r for r in data.get("user_context", []) if r.get("kind") == "recorded_request"
                and r.get("provenance") == "USER" and type(r.get("turn_id")) is int]
    retraction = (r"\b(?:non\s+confermo\s+(?:questa\s+scelta|(?:il\s+)?firmatario)|"
                  r"non\s+ho\s+ancora\s+scelto\s+chi\s+firma|"
                  r"firmatario\s+(?:è|e)\s+(?:ancora\s+)?da\s+decidere|"
                  r"annullo\s+(?:la\s+)?scelta\s+del\s+firmatario)\b")
    if any(re.search(retraction, r.get("user_quote", ""), re.I) for r in requests):
        return None
    for request in requests:
        quote = request.get("user_quote", "")
        for match in pattern.finditer(quote):
            literal = match[0].lstrip(".;\n ")
            if (quote[match.end():].lstrip().startswith("?") or _uncertain(literal)
                    or has_user_alternatives(literal)):
                continue
            selections.append((match[1].strip(), {"action": "VALUE", "provenance": "USER",
                "value": match[1].strip(), "user_quote": literal,
                "selection_receipt_key": "request:" + str(request["turn_id"]),
                "selection_origin": "explicit_session_start_selection"}))
    if len({_text(name) for name, _ in selections}) == 1:
        return selections[0]
    return None


def _replaceable(field, audit, name, value, prop):
    """A new independent proposal may supersede a failed binding, not a conflict."""
    if field.get("validation") == "GROUNDED_PROPOSAL" or field.get("proposal_grounding"):
        return False
    proposal = field.get("proposal")
    if proposal is None:
        return True
    if (not isinstance(proposal, dict)
            or proposal.get("disposition") not in {"value", "conditional"}
            or field.get("alternatives") or proposal.get("alternative_fact_ids")):
        return False
    fact = audit.get("facts", {}).get(proposal.get("fact_id"), {})
    return (fact.get("validation") == "GROUNDED_PROPOSAL" and fact.get("entity") == "person"
            and _text(fact.get("subject", "")) == _text(name)
            and (_text(fact.get("value", "")) == _text(value) or prop == "address"
                 and _text(fact.get("value", "")) == _text("via " + value)))


def _profiles(sources, name):
    """Read explicit labelled profiles; overlapping chunks remain independent."""
    records = []
    for source in sources:
        if source.get("category") == "general":
            continue
        lines = source["content"].splitlines()
        for index, line in enumerate(lines):
            heading = re.fullmatch(r"\s*#{1,6}\s+(.+?)\s+[-–—]\s+anagrafica(?: sintetica)?\s*",
                                   line, re.I)
            if not heading or _text(heading[1]) != _text(name):
                continue
            values, quotes, conflict = {}, {}, False
            for item in lines[index + 1:]:
                if re.match(r"\s*#{1,6}\s+", item):
                    break
                prop = re.fullmatch(r"\s*-\s+([^:\n]+):\s*(.+?)\.?\s*", item)
                if not prop or (key := _PROPERTIES.get(_text(prop[1]))) is None:
                    if item.strip():
                        break  # New prose/person is outside the labelled profile.
                    continue
                value = prop[2].strip()
                if _uncertain(value) or key in values and _text(values[key]) != _text(value):
                    conflict = True
                values[key], quotes[key] = value, item
            records.append({"source": source, "header": line, "values": values,
                            "quotes": quotes, "conflict": conflict})
    return records


def _identity(sources, name):
    sources = list(sources)
    records = _profiles(sources, name)
    if not records or any(r["conflict"] for r in records):
        return None
    for key in _PROPERTIES.values():
        if len({_text(r["values"][key]) for r in records if key in r["values"]}) > 1:
            return None
    complete = [r for r in records if re.fullmatch(r"[A-Z0-9]{16}", r["values"].get("cf", ""))
                and _text(r["values"].get("first", "") + " " + r["values"].get("last", ""))
                == _text(name)]
    if not complete:
        return None
    cf = _text(complete[0]["values"]["cf"])
    for source in sources:
        if source.get("category") == "general":
            continue
        for record in _subject_records(source["content"], None):
            other_cf = record_identity(record).get("cf")
            same_name = _same_person(record["subject"], name)
            if (same_name and other_cf and other_cf != cf) or (not same_name and other_cf == cf):
                return None  # Includes homonyms in differently formatted records.
    # No property transfer between partial records or people joined by name.
    return max(complete, key=lambda r: len(r["values"]))


def _role(sources, profile, name, operator):
    """Only an explicit same-document named assertion, never inferred powers."""
    assertions, owners = [], []
    sources = list(sources)
    if not operator:
        return None
    for source in sources:
        if source["file_id"] != profile["source"]["file_id"]:
            continue
        for line in source["content"].splitlines():
            match = re.fullmatch(r"\s*-\s+(?:\*\*)?(?:Società|Denominazione sociale)"
                                 r"(?::\*\*|\*\*:|:)\s*(.+?)\s*", line, re.I)
            if match:
                owners.append((_text(match[1]).rstrip("."), source, line))
    if {o[0] for o in owners} != {_text(operator).rstrip(".")}:
        return None
    for source in sources:
        if source["file_id"] != profile["source"]["file_id"]:
            continue
        for line in source["content"].splitlines():
            match = re.fullmatch(r"\s*-\s+\*\*(.+?)\*\*:\s*\*\*(.+?)\*\*(.*)", line)
            if not match or _text(match[1]) != _text(name):
                continue
            assertion = line[:match.end(2) + 2]
            if _uncertain(match[2]) or _uncertain(match[3].split(".", 1)[0]):
                return None
            if not re.search(r"\bdella società\b", match[2], re.I):
                continue  # Other company relationships need their own explicit proof.
            # A documented role phrase, excluding an explicit company/time qualifier.
            value = re.split(r"\s+(?:della società|dal\s+\d)", match[2], maxsplit=1, flags=re.I)[0]
            assertions.append((value, source, assertion))
    if len({_text(a[0]) for a in assertions}) == 1:
        return assertions[0], owners
    return None


def _form_groups(catalog):
    paragraphs = []
    for block in catalog.get("blocks", []):
        if block.get("tables"):
            paragraphs.append({"id": "table-boundary", "text": "TABLE BOUNDARY"})
        else:
            paragraphs.extend(block["paragraphs"])
    for start, paragraph in enumerate(paragraphs):
        if "sottoscritt" not in _text(paragraph["text"]):
            continue
        selected = paragraphs[start:start + 4]
        if any(p["id"] == "table-boundary" for p in selected):
            continue
        text = "\n".join(p.get("text_with_fields", p["text"]) for p in selected)
        match = _SIGNATORY.search(text)
        if match and len(set(match.groups())) == 10:
            yield match.groups(), selected, match[0]


def source_reuse_requested(data):
    if (data.get("audit") or {}).get("version") != 12:
        return False
    return (any(_selection(data, ids[0]) for ids, _, _ in _form_groups(data["catalog"]))
            or any(_selection(data, g["name_id"]) for g in _signatory_groups(data)))


def signatory_fields(data):
    """One FORM-owned name question even if the model omitted a clarification."""
    if (data.get("audit") or {}).get("version") != 12:
        return {}
    fields = {f["candidate_id"]: f for f in (data.get("audit") or {}).get("fields", [])}
    result = {}
    for ids, paragraphs, _ in _form_groups(data.get("catalog", {})):
        field = fields.get(ids[0])
        if field is None or field.get("proposal") or field.get("validation_errors"):
            continue
        result[ids[0]] = {**field, "label": "Il sottoscritto", "kind": "data",
            "disposition": "review", "form_evidence": {
                "paragraph_id": paragraphs[0]["id"], "quote": paragraphs[0]["text"]}}
    for group in _signatory_groups(data):
        cid = group["name_id"]
        field = fields.get(cid)
        if (cid in result or not field or field.get("proposal") or field.get("source_reuse")
                or field.get("validation_errors")):
            continue
        result[cid] = {**field, "label": "Nome del firmatario della domanda", "kind": "data",
            "disposition": "review", "form_evidence": {
                "paragraph_id": group["proofs"][0]["id"],
                "quote": group["proofs"][0]["text"]}}
    return result


def _labelled_properties(group, profile):
    """Extract only literal components; do not manufacture combined SOURCE text."""
    values, quotes = profile["values"], profile["quotes"]
    props = group["targets"]
    result = {}
    for cid, prop in props.items():
        if prop in {"birth", "residence", "birth_province", "residence_province"}:
            base = prop.removesuffix("_province")
            if base not in values:
                continue
            place = re.fullmatch(r"([^()\n]+?)\s*\(([A-Z]{2})\)", values[base])
            if prop.endswith("_province"):
                if place:
                    result[cid] = (place[2], quotes[base], prop)
            else:
                result[cid] = (place[1] if place and base + "_province" in props.values()
                               else values[base], quotes[base], prop)
        elif prop in {"date", "cf"} and prop in values:
            result[cid] = (values[prop], quotes[prop], prop)
        elif prop in {"address", "house"} and "address" in values:
            address = values["address"]
            # A preprinted 'via' may consume that exact prefix only. A corso,
            # viale or unlabelled/ambiguous house number is never silently changed.
            street = re.fullmatch(r"via\s+(.+)", address, re.I)
            split = re.fullmatch(r"(.+?)\s+(\d+[A-Za-z]?(?:/[A-Za-z0-9]+)?)", street[1]) \
                if street else None
            if prop == "house" and split:
                result[cid] = (split[2], quotes["address"], prop)
            elif prop == "address":
                proof = next((p for p in group["proofs"] if ("[[" + cid + "]]") in
                              p.get("text_with_fields", "")), None)
                prefix = proof["text_with_fields"].split("[[" + cid + "]]")[0] if proof else ""
                if re.search(r"\bvia(?:/piazza)?\s*$", prefix, re.I):
                    if street and ("house" not in props.values() or split):
                        result[cid] = (split[1] if "house" in props.values() else street[1],
                                       quotes["address"], prop)
                elif "house" not in props.values():
                    result[cid] = (address, quotes["address"], prop)
    return result


def _reuse_labelled(data, audit, fields, layout, project_id, sources, legacy_names):
    from app.compilation_attribution import check_source_target

    newly_assigned = 0
    groups = _signatory_groups(data)
    for group in groups:
        name_id = group["name_id"]
        if name_id in legacy_names or not (selection := _selection(data, name_id)):
            continue
        name, receipt = selection
        if (len(groups) > 1 and (receipt.get("selection_origin")
                or receipt.get("selection_receipt_key", "").startswith("condition:"))):
            continue  # A global name choice does not choose between distinct FORM blocks.
        profile = _identity(sources.values(), name)
        if profile is None:
            continue
        # SOURCE grounding proves a fact, not its attribution to the person
        # selected for these FORM targets. Keep the fact/proof, veto the link.
        for cid in group["targets"]:
            existing = fields.get(cid, {})
            if not (existing.get("validation") == "GROUNDED_PROPOSAL"
                    or existing.get("proposal_grounding") == "GROUNDED_PROPOSAL"):
                continue
            fact = audit.get("facts", {}).get(existing.get("fact_id") or existing.get(
                "proposed_fact_id") or (existing.get("proposal") or {}).get("fact_id"), {})
            if fact and (fact.get("entity") != "person" or not _same_person(
                fact.get("subject", ""), name)):
                rejected = {**existing, "validation": "REJECTED", "value": None,
                    "written_value": None, "proposed_value": None,
                    "validation_errors": [*existing.get("validation_errors", []),
                        "Il fatto SOURCE non riguarda il firmatario scelto dall'utente"],
                    "selected_subject_check": {"result": "rejected", "subject": name,
                        "selection_receipt": deepcopy(receipt),
                        "actual_subject": fact.get("subject"), "entity": fact.get("entity")},
                    "coverage": {"state": "REJECTED_PROPOSAL", "origin": "BACKEND",
                                 "reason": "Soggetto diverso dal firmatario selezionato"}}
                rejected.pop("proposal_grounding", None)
                fields[cid] = rejected
        source = profile["source"]
        properties = _labelled_properties(group, profile)
        properties[name_id] = (name, profile["header"], "name")
        op = fields.get(group.get("operator_id"), {})
        op_fact = audit.get("facts", {}).get(op.get("fact_id") or op.get("proposed_fact_id"), {})
        operator = op.get("proposed_value", op.get("value")) if (
            op_fact.get("entity") == "company" and (op.get("validation") == "GROUNDED_PROPOSAL"
            or op.get("proposal_grounding") == "GROUNDED_PROPOSAL")) else None
        role = _role(sources.values(), profile, name, operator)
        if role:
            for cid, prop in group["targets"].items():
                if prop == "role":
                    properties[cid] = (role[0][0], role[0][2], prop)
        identity_quotes = [profile["header"], *[profile["quotes"][k]
                                                for k in ("first", "last", "cf")]]
        for cid, (value, quote, prop) in properties.items():
            field = fields.get(cid)
            if (not field or cid in (data.get("dialogue") or {}).get("user_values", {})
                    or cid not in data["writable_ids"] or field.get("source_reuse")
                    or not _replaceable(field, audit, name, value, prop)):
                continue
            proof_source = role[0][1] if prop == "role" else source
            fact = {"subject": name, "entity": "person", "aspect": "representation"
                    if prop == "role" else "identity", "property": prop, "value": value,
                    "evidence": [{"chunk_id": proof_source["chunk_id"], "quote": quote}]}
            validated = _shared_facts({"f": fact}, sources, reject_empty=True)["f"]
            checked = validate_value(layout, {"id": cid, "label": prop, "entity": "person"},
                                     value, proof_source, quote)
            target = check_source_target(cid, data["catalog"], validated)
            if (validated["validation"] != "GROUNDED_PROPOSAL" or checked["validation_codes"]
                    or checked["written_value"] != value or target["validation_codes"]):
                continue
            conditions = sorted(set(field.get("conditions", [])) | set(fields[name_id].get(
                "conditions", [])) | (set(op.get("conditions", [])) if prop == "role" else set()))
            if data.get("backend_revision") == 13:
                from app.compilation_factual_recovery import blocked_conditions

                if blocked_conditions(data, audit, conditions):
                    continue
            if any(audit["conditions"].get(c, {}).get("validation_errors") for c in conditions):
                continue
            checks = {c: {"result": audit["conditions"].get(c, {}).get("result", "unknown")}
                      for c in conditions}
            proof = group["target_proofs"][cid][0]
            labels = {"name": "Nome del firmatario scelto", "birth": "Luogo di nascita",
                "birth_province": "Provincia di nascita", "date": "Data di nascita",
                "cf": "Codice fiscale personale", "residence": "Comune di residenza",
                "residence_province": "Provincia di residenza", "address": "Via di residenza",
                "house": "Numero civico di residenza", "role": "Carica documentata"}
            fields[cid] = {**field, "label": labels[prop], "kind": "data", "entity": "person",
                "disposition": "conditional" if conditions else "value", "conditions": conditions,
                "condition_checks": checks, "validation": "REVIEW_REQUIRED",
                "validation_errors": [], "proposal_grounding": "GROUNDED_PROPOSAL",
                "proposed_value": value, "value": None, "written_value": None,
                "source_evidence": validated["source_evidence"],
                "form_evidence": {"paragraph_id": proof["id"], "quote": proof["text"]},
                "coverage": {"state": "PROPOSED", "origin": "BACKEND",
                             "reason": "Riuso SOURCE dopo scelta USER"},
                "source_reuse": {"method": "selected_person_labelled_properties",
                    "subject": name, "selection_candidate_id": name_id,
                    "selection_receipt": deepcopy(receipt), "property": prop, "fact": fact,
                    "original_validation_errors": list(field.get("validation_errors", [])),
                    "form_quote": "\n".join(p["text"] for p in group["proofs"]),
                    "target_proofs": deepcopy(group["proofs"]), "identity_quotes": identity_quotes,
                    "identity_evidence": [_citation_audit(SourceSpan(
                        chunk_id=source["chunk_id"], quote=q), source, q)
                        for q in identity_quotes]},
                "semantic_review_required": True}
            if prop == "role":
                fields[cid]["source_reuse"]["operator_evidence"] = [
                    _citation_audit(SourceSpan(chunk_id=s["chunk_id"], quote=q), s, q)
                    for _, s, q in role[1]] + deepcopy(op.get("source_evidence", []))
            newly_assigned += field.get("proposal") is None
    return newly_assigned


def reuse_selected_person(data, layout, project_id, sources):
    """Return a fresh effective audit; no writes, LLM calls or resolved values."""
    source_map = _allowed_sources(project_id, sources)
    audit = deepcopy(data["audit"])
    if audit.get("version") != 12:
        return audit
    dialogue = data.get("dialogue") or {}
    users = dialogue.get("user_values", {})
    fields = {f["candidate_id"]: f for f in audit["fields"]}
    newly_assigned = 0
    for cid, field in signatory_fields(data).items():
        if cid in users:
            fields[cid] = field
    for ids, paragraphs, form_quote in _form_groups(data["catalog"]):
        selection = _selection(data, ids[0])
        if selection is None:
            continue
        name, receipt = selection
        profile = _identity(source_map.values(), name)
        if profile is None:
            continue
        values, quotes, source = profile["values"], profile["quotes"], profile["source"]
        properties = {}
        for key, destinations in [("birth", ids[1:3]), ("residence", ids[4:6])]:
            place = re.fullmatch(r"([^()\n]+?)\s*\(([A-Z]{2})\)", values.get(key, ""))
            if place:
                for cid, value in zip(destinations, place.groups()):
                    properties[cid] = (value, source, quotes[key], key)
        for key, cid in [("date", ids[3]), ("cf", ids[7])]:
            if key in values:
                properties[cid] = (values[key], source, quotes[key], key)
        # FORM already prints 'via'. Extract its literal SOURCE component only;
        # never rewrite a corso/viale as a via or silently discard a street type.
        street = re.fullmatch(r"via\s+(.+)", values.get("address", ""), re.I)
        if street:
            properties[ids[6]] = (street[1], source, quotes["address"], "address")
        op = fields.get(ids[9], {})
        operator_fact = audit.get("facts", {}).get(
            op.get("fact_id") or op.get("proposed_fact_id"), {})
        operator = op.get("proposed_value", op.get("value")) if (
            (op.get("validation") == "GROUNDED_PROPOSAL" or
             op.get("proposal_grounding") == "GROUNDED_PROPOSAL")
            and operator_fact.get("entity") == "company") else None
        role = _role(source_map.values(), profile, name, operator)
        if role:
            properties[ids[8]] = (*role[0], "role")
        identity_quotes = [profile["header"], *[quotes[k] for k in ("first", "last", "cf")]]
        identity_fact = {"subject": name, "entity": "person", "aspect": "identity",
                         "property": "nome", "value": name,
                         "evidence": [{"chunk_id": source["chunk_id"], "quote": profile["header"]}]}
        identity = _shared_facts(
            {"identity": identity_fact}, source_map, reject_empty=True)["identity"]
        if identity["validation"] != "GROUNDED_PROPOSAL":
            continue
        if ids[0] not in users:
            properties[ids[0]] = (name, source, profile["header"], "name")
        for cid, (value, proof_source, quote, prop) in properties.items():
            field = fields.get(cid)
            if (not field or cid in users or cid not in data["writable_ids"]
                    or field.get("source_reuse")
                    or not _replaceable(field, audit, name, value, prop)):
                continue
            conditions = sorted(set(field.get("conditions", []))
                                | set(fields[ids[0]].get("conditions", []))
                                | (set(op.get("conditions", [])) if prop == "role" else set()))
            if data.get("backend_revision") == 13:
                from app.compilation_factual_recovery import blocked_conditions

                if blocked_conditions(data, audit, conditions):
                    continue
            checks = {c: {"result": audit["conditions"].get(c, {}).get("result", "unknown")}
                      for c in conditions}
            if any(audit["conditions"].get(c, {}).get("validation_errors") for c in conditions):
                continue
            fact = {"subject": name, "entity": "person",
                    "aspect": "representation" if prop == "role" else "identity",
                    "property": prop, "value": value,
                    "evidence": [{"chunk_id": proof_source["chunk_id"], "quote": quote}]}
            validated = _shared_facts({"fact": fact}, source_map, reject_empty=True)["fact"]
            checked = validate_value(layout, {"id": cid, "label": prop, "entity": "person"},
                                     value, proof_source, quote)
            if (validated["validation"] != "GROUNDED_PROPOSAL" or checked["validation_codes"]
                    or checked["written_value"] != value):
                continue
            paragraph = next(p for p in paragraphs if f"[[{cid}]]" in p.get("text_with_fields", ""))
            label = {ids[0]: "Nome del firmatario scelto", ids[1]: "Comune di nascita",
                     ids[2]: "Provincia di nascita",
                     ids[3]: "Data di nascita", ids[4]: "Comune di residenza",
                     ids[5]: "Provincia di residenza", ids[6]: "Indirizzo di residenza",
                     ids[7]: "Codice fiscale personale", ids[8]: "Carica documentata"}[cid]
            fields[cid] = {**field, "label": label, "kind": "data", "entity": "person",
                "disposition": "conditional" if conditions else "value", "conditions": conditions,
                "condition_checks": checks, "validation": "REVIEW_REQUIRED",
                "validation_errors": [],
                "proposal_grounding": "GROUNDED_PROPOSAL", "proposed_value": value,
                "value": None, "written_value": None,
                "form_evidence": {"paragraph_id": paragraph["id"], "quote": paragraph["text"]},
                "source_evidence": validated["source_evidence"],
                "coverage": {"state": "PROPOSED", "origin": "BACKEND",
                             "reason": "Riuso SOURCE dopo scelta USER"},
                "source_reuse": {"method": "selected_person_literal_properties", "subject": name,
                    "selection_candidate_id": ids[0], "selection_receipt": deepcopy(receipt),
                    "original_validation_errors": list(field.get("validation_errors", [])),
                    "form_quote": form_quote, "identity_evidence": [
                        _citation_audit(SourceSpan(chunk_id=source["chunk_id"], quote=q), source, q)
                        for q in identity_quotes],
                    "identity_quotes": identity_quotes, "property": prop, "fact": fact},
                "semantic_review_required": True}
            newly_assigned += field.get("proposal") is None
            if prop == "role":
                fields[cid]["source_reuse"]["operator_evidence"] = [
                    _citation_audit(SourceSpan(chunk_id=s["chunk_id"], quote=q), s, q)
                    for _, s, q in role[1]] + deepcopy(op.get("source_evidence", []))
    newly_assigned += _reuse_labelled(data, audit, fields, layout, project_id, source_map,
                                    {ids[0] for ids, _, _ in _form_groups(data["catalog"])})
    audit["fields"] = list(fields.values())
    if data.get("backend_revision") == 13:
        from app.compilation_factual_recovery import recover

        audit = recover(data, audit, layout, project_id, source_map)
    safety = {}
    if data.get("attribution_safety_revision") == 1:
        from app.compilation_attribution_safety import apply_attribution_safety

        audit, safety = apply_attribution_safety(audit, source_map)
    reused = [f for f in audit["fields"] if f.get("source_reuse")]
    if reused:
        audit["source_reuse_count"] = len(reused)
    if reused or safety or any(f.get("selected_subject_check") for f in audit["fields"]):
        audit["counts"] = dict(Counter(f["validation"] for f in audit["fields"]))
        audit["unassigned_count"] = max(0, audit.get("unassigned_count", 0) - newly_assigned)
        if "coverage_summary" in audit:
            counts = Counter(f["coverage"]["state"] for f in audit["fields"])
            for key, state in {"proposed": "PROPOSED", "rejected": "REJECTED_PROPOSAL",
                               "explained_unfilled": "EXPLAINED_UNFILLED",
                               "explicitly_unassessed": "UNASSESSED", "unexplained": "UNEXPLAINED",
                               "rejected_explanations": "REJECTED_EXPLANATION"}.items():
                audit["coverage_summary"][key] = counts[state]
    from app.compilation_value_completeness import refresh_reused

    return refresh_reused(audit, layout, data["catalog"], source_map)
