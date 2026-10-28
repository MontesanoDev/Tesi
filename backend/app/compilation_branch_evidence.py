"""Bounded FORM/USER/SOURCE conjunctions and positive receipt-to-control links.

No general semantic inference: unsupported syntax/cardinality remains unknown.
Original model proposals and USER receipts are never rewritten.
"""

import re
from copy import deepcopy

from app.compilation_role_records import _uncertain


def _text(value):
    return " ".join(value.replace("**", "").casefold().split()).strip(" .☐☑")


def _accepted(condition, receipt):
    from app.compilation_chat import has_user_alternatives

    return (
        condition.get("validation") == "GROUNDED_PROPOSAL"
        and not condition.get("validation_errors")
        and condition.get("form_evidence")
        and receipt.get("provenance") == "USER"
        and receipt.get("action") == "CONDITION_TRUE"
        and receipt.get("applies") is True
        and receipt.get("question")
        and receipt.get("user_quote")
        and (receipt.get("ambiguity_check") == "SEMANTIC_GUARD"
             or not has_user_alternatives(receipt['user_quote']))
    )


def _capacity_region(catalog, cid):
    """The literal capacity heading bounds all options, including intervening data."""
    paragraphs = [p for b in catalog["blocks"] for p in b["paragraphs"]]
    position = {p["id"]: i for i, p in enumerate(paragraphs)}
    candidate = catalog["candidates"][cid]
    if "table_id" in candidate["location"]:
        return None
    index = position[candidate["context_id"]]

    def boundary(p):
        text = p["text"].strip()
        if p.get("text_with_fields") or p.get("controls"):
            return False
        return p.get("outline_level") is not None or (text and text.isupper())

    start = next((i for i in range(index - 1, -1, -1) if boundary(paragraphs[i])), None)
    if start is None or _text(paragraphs[start]["text"]) != "in qualità di":
        return None
    end = next((i for i in range(index + 1, len(paragraphs)) if boundary(paragraphs[i])), None)
    if end is None or end - start > 64:
        return None
    options = {}
    for option_id, c in catalog["candidates"].items():
        if c["type"] != "checkbox" or not start < position[c["context_id"]] < end:
            continue
        p = paragraphs[position[c["context_id"]]]
        siblings = [
            x
            for x in catalog["candidates"].values()
            if x["type"] == "checkbox" and x["context_id"] == c["context_id"]
        ]
        if (
            len(siblings) != 1
            or "table_id" in c["location"]
            or c["section_ids"] != candidate["section_ids"]
        ):
            return None
        label = p["text"].strip(" ☐☑")
        if not 1 <= len(label) <= 250:
            return None
        options[option_id] = {
            "label": label,
            "form": {"paragraph_id": p["id"], "quote": p["text_with_choices"]},
        }
    if cid not in options or not 2 <= len(options) <= 32:
        return None
    return paragraphs[start], options


def _receipt_control(data, key, condition, receipt):
    if not _accepted(condition, receipt) or condition.get("aspect") not in {
        "legal_type",
        "participation",
    }:
        return None
    catalog = data["catalog"]
    form = condition["form_evidence"]
    matches = [
        (cid, c)
        for cid, c in catalog["candidates"].items()
        if c["type"] == "checkbox" and c["context_id"] == form["paragraph_id"]
    ]
    if len(matches) != 1:
        return None
    cid, _ = matches[0]
    paragraph = next(
        p for b in catalog["blocks"] for p in b["paragraphs"] if p["id"] == form["paragraph_id"]
    )
    if (
        _text(paragraph["text"]) != _text(form["quote"])
        or cid not in condition.get("applies_to", [])
        or not (region := _capacity_region(catalog, cid))
    ):
        return None
    _, options = region
    if any(catalog["candidates"][peer].get("initial_checked") for peer in options if peer != cid):
        return None  # Unknown cardinality cannot safely clear an existing peer.
    # Another positive decision in this same capacity list is not silently combined.
    for other_key, other in data["audit"].get("conditions", {}).items():
        if other_key == key or not _accepted(
            other, data.get("dialogue", {}).get("answers", {}).get("condition:" + other_key, {})
        ):
            continue
        if any(
            peer != cid
            and peer in other.get("applies_to", [])
            and other["form_evidence"]["paragraph_id"] == catalog["candidates"][peer]["context_id"]
            for peer in options
        ):
            return None
    return cid, region


def effective_user_values(data):
    """Derived links reuse the exact receipt; they are not new USER answers."""
    values = dict((data.get("dialogue") or {}).get("user_values", {}))
    answers = (data.get("dialogue") or {}).get("answers", {})
    for cid, value in (data.get("audit") or {}).get("receipt_choice_values", {}).items():
        key = value.get("receipt_key", "").removeprefix("condition:")
        receipt = answers.get("condition:" + key, {})
        condition = data["audit"].get("conditions", {}).get(key, {})
        group = data["audit"].get("choice_groups", {}).get(value.get("choice_group_id"), {})
        match = _receipt_control(data, key, condition, receipt)
        if (
            cid not in values
            and value.get("value") is True
            and value.get("provenance") == "USER"
            and receipt == value.get("receipt")
            and receipt.get("user_quote") == value.get("user_quote")
            and group.get("validation") == "GROUNDED_GROUP"
            and group.get("selection") == "unknown"
            and match
            and match[0] == cid
            and set(group.get("options", {})) == set(match[1][1])
            and all(
                group["options"][peer]["label"] == option["label"]
                for peer, option in match[1][1].items()
            )
        ):
            values[cid] = value
    return values


def receipt_choice_value(data, cid):
    if cid in (data.get('dialogue') or {}).get('user_values', {}):
        return None
    value = (data.get('audit') or {}).get('receipt_choice_values', {}).get(cid)
    return value if value and effective_user_values(data).get(cid) == value else None


def _participation(receipt, operator):
    # Full literal subject and explicit affirmative participation clause only.
    # A quoted statement, hypothetical, generic yes or company role is insufficient.
    quote = receipt.get("user_quote", "")
    pattern = (
        r"(?:^|[.;]\s*)"
        r"(?:Confermo(?: quanto già indicato(?: nella richiesta iniziale)?)?:\s*)?"
        + re.escape(operator)
        + r"\s+partecipa\s+(?:soltanto\s+|solo\s+)?come\s+([^;.!?]+)(?:[;.]|$)"
    )
    matches = list(re.finditer(pattern, quote, re.I))
    if len(matches) != 1 or _uncertain(matches[0][1]):
        return None
    return matches[0][1].strip()


def _role_proof(binding, subject, role, operator, sources):
    prefix = _text(subject + ": " + role + " di " + operator)
    proofs = []
    for proof in binding.get("source_evidence", []):
        source = sources.get(proof["chunk_id"])
        if not source or source.get("category") == "general":
            continue
        for line in source["content"].splitlines():
            text = _text(line.lstrip(" -"))
            if not re.match(re.escape(prefix) + r"\.?(?:;|$)", text):
                continue
            if _text(proof["quote"]) not in _text(line) or _uncertain(line.split(";")[0]):
                continue
            proofs.append({**proof, "quote": line})
    # Conflicting/uncertain named statements about this exact role/operator veto reuse.
    for source in sources.values():
        for line in source["content"].splitlines():
            text = _text(line)
            if all(_text(x) in text for x in [subject, role, operator]) and _uncertain(text):
                return []
    return proofs


def _branch(data, key, condition, sources):
    audit = data["audit"]
    answer = (data.get("dialogue") or {}).get("answers", {}).get("condition:" + key, {})
    if (
        condition.get("result") != "unknown"
        or condition.get("validation_errors")
        or condition.get("validation") != "GROUNDED_PROPOSAL"
        or condition.get("operator") != "semantic"
        or answer.get("applies") is False
        or answer.get("action") == "REFUSE"
        or re.search(
            r"\b(?:non compil\w*|non inser\w*|lasci\w*.*(?:bianco|vuot\w*))\b",
            answer.get("user_quote", ""),
            re.I,
        )
    ):
        return None
    form = condition.get("form_evidence") or {}
    paragraph = next(
        (
            p["text"]
            for b in data["catalog"]["blocks"]
            for p in b["paragraphs"]
            if p["id"] == form.get("paragraph_id")
        ),
        "",
    )
    if paragraph != form.get("quote"):
        return None
    match = re.fullmatch(r"(?:la quale|il quale|che) ha come (.+):", paragraph, re.I)
    if not match:
        return None
    alternatives = []
    for part in re.split(r"\s+o\s+", match[1]):
        alternative = re.fullmatch(r"(.+?)\s*\(per le (.+?)\)", part)
        if not alternative:
            return None
        alternatives.append((alternative[1], alternative[2]))
    if len(alternatives) < 2:
        return None
    fields = [f for f in audit["fields"] if key in f.get("conditions", [])]
    if not fields or any(
        f.get("proposal_grounding") != "GROUNDED_PROPOSAL" or f.get("validation_errors")
        for f in fields
    ):
        return None
    roles = set()
    for field in fields:
        fact = audit["facts"].get(field.get("proposed_fact_id"), {})
        check = field.get("subject_binding") or {}
        binding = audit.get("bindings", {}).get(check.get("binding_id"), {})
        if (
            fact.get("entity") != "person"
            or fact.get("validation") != "GROUNDED_PROPOSAL"
            or check.get("result") != "literal_match"
            or check.get("validation_errors")
            or binding.get("validation") != "GROUNDED_PROPOSAL"
            or binding.get("validation_errors")
            or binding.get("form_evidence") != form
            or _text(binding.get("required_role", "")) != _text(binding.get("source_role", ""))
        ):
            return None
        roles.add((fact["subject"], check["binding_id"]))
    if len(roles) != 1:
        return None
    subject, binding_id = next(iter(roles))
    binding = audit["bindings"][binding_id]
    proofs = []
    for parent_key, parent in audit["conditions"].items():
        receipt = (data.get("dialogue") or {}).get("answers", {}).get("condition:" + parent_key, {})
        if (
            parent_key == key
            or not _accepted(parent, receipt)
            or not {f["candidate_id"] for f in fields} <= set(parent.get("applies_to", []))
            or not _receipt_control(data, parent_key, parent, receipt)
        ):
            continue
        owners = {
            audit["facts"][f.get("fact_id") or f.get("proposed_fact_id")]["subject"]
            for f in audit["fields"]
            if parent_key in f.get("conditions", [])
            and (
                f.get("validation") == "GROUNDED_PROPOSAL"
                or f.get("proposal_grounding") == "GROUNDED_PROPOSAL"
            )
            and audit["facts"].get(f.get("fact_id") or f.get("proposed_fact_id"), {}).get("entity")
            == "company"
            and _text(audit["facts"][f.get("fact_id") or f.get("proposed_fact_id")]["value"])
            == _text(audit["facts"][f.get("fact_id") or f.get("proposed_fact_id")]["subject"])
        }
        if len(owners) != 1:
            continue
        operator = next(iter(owners))
        selected_type = _participation(receipt, operator)
        choices = [
            (role, kind)
            for role, kind in alternatives
            if selected_type
            and _text(kind) == _text(selected_type)
            and _text(kind) in _text(parent["form_evidence"]["quote"])
            and _text(role) == _text(binding["required_role"])
        ]
        if len(choices) != 1:
            continue
        role, kind = choices[0]
        evidence = _role_proof(binding, subject, role, operator, sources)
        if evidence:
            proofs.append(
                {
                    "receipt_key": "condition:" + parent_key,
                    "receipt": deepcopy(receipt),
                    "form_evidence": deepcopy(form),
                    "participation_type": kind,
                    "role": role,
                    "subject": subject,
                    "operator": operator,
                    "source_evidence": evidence,
                    "binding_id": binding_id,
                }
            )
    return proofs[0] if len(proofs) == 1 else None


def reconcile_branches(data, layout, project_id, sources):
    from app.compilation_choices import validate_groups
    from app.compilation_global import _allowed_sources, _form_bindings

    result = deepcopy(data["audit"])
    if result.get("version") != 12 or data["catalog"].get("template_sha256") != layout.sha256:
        return result
    catalog = data["catalog"]
    source_map = _allowed_sources(project_id, sources)
    current = {**data, "audit": result}
    for key, condition in result.get("conditions", {}).items():
        proof = _branch(current, key, condition, source_map)
        if not proof:
            continue
        condition.update(
            result="true", grounding_basis="verified_FORM_USER_SOURCE_branch", branch_evidence=proof
        )
        for field in result["fields"]:
            if key in field.get("condition_checks", {}):
                field["condition_checks"][key]["result"] = "true"
                field["condition_checks"][key]["grounding_basis"] = condition["grounding_basis"]
    paragraphs, local = _form_bindings(catalog)
    used = {
        cid
        for group in result.get("choice_groups", {}).values()
        for cid in group.get("options", {})
    }
    for key, condition in result.get("conditions", {}).items():
        receipt = (data.get("dialogue") or {}).get("answers", {}).get("condition:" + key, {})
        match = _receipt_control(current, key, condition, receipt)
        if not match:
            continue
        cid, (heading, options) = match
        if used & options.keys():
            continue
        group_id = "form_receipt_" + cid
        record = dict(
            label=heading["text"],
            subject="Richiedente",
            property="qualità di partecipazione",
            form={"paragraph_id": heading["id"], "quote": heading["text"]},
            selection="unknown",
            min_selected=0,
            options=options,
            conditions=[],
        )
        group = validate_groups(
            {group_id: record}, catalog, paragraphs, local, result["conditions"]
        )[group_id]
        if group["validation"] != "GROUNDED_GROUP":
            continue
        group["origin"] = "FORM_receipt_link"
        result.setdefault("choice_groups", {})[group_id] = group
        used.update(options)
        for field in result["fields"]:
            if field["candidate_id"] in options:
                field.update(
                    choice_group_id=group_id,
                    kind="choice",
                    form_evidence=group["options"][field["candidate_id"]]["form_evidence"],
                    label=options[field["candidate_id"]]["label"],
                )
        result.setdefault("receipt_choice_values", {})[cid] = {
            "value": True,
            "provenance": "USER",
            "label": options[cid]["label"],
            "user_quote": receipt["user_quote"],
            "receipt_key": "condition:" + key,
            "receipt": deepcopy(receipt),
            "choice_group_id": group_id,
        }
    return result
