"""Bounded FORM dependency: ASCII alternative ending in ':' -> next data paragraph.

Recognizes only two fixed body options separated by an isolated OPPURE. Blank
paragraphs are allowed; tables and any intervening printed text break the link.
This is not checkbox parsing, entity classification or procedural authorization.
No missing MODEL condition is invented, and no SOURCE fact chooses an option.
"""
import re

from app.compilation_option_regions import BOX_GLYPHS
from app.requirement_checks import normalized_form_text as norm

MARKER = re.compile(r"^\[\s*\]")


def enabled(data):
    return (data.get("generation_revision") == 3
            and data.get("form_option_scope_revision") == 1)


def _option(paragraph, owned):
    text = paragraph["text"].strip()
    return (MARKER.match(text) and len(re.findall(r"\[[^\]]*\]", text)) == 1
            and not BOX_GLYPHS.search(text) and not paragraph.get("controls")
            and not owned.get(paragraph["id"]))


def regions(catalog):
    owned = {}
    for cid, candidate in catalog.get("candidates", {}).items():
        owned.setdefault(candidate.get("context_id"), []).append(cid)
    # None is a barrier, including nested/cell paragraphs. Never cross a table.
    body = []
    for block in catalog.get("blocks", []):
        if block.get("tables"):
            body.append(None)
        else:
            body.extend(p for p in block["paragraphs"] if p["text"].strip()
                        or p.get("controls") or owned.get(p["id"]))
    result = []
    for index in range(2, len(body) - 1):
        previous, separator, option, target = body[index - 2:index + 2]
        if any(p is None for p in (previous, separator, option, target)):
            continue
        if (not _option(previous, owned) or norm(separator["text"]) != "oppure"
                or owned.get(separator["id"]) or separator.get("controls")
                or not _option(option, owned) or not option["text"].rstrip().endswith(":")):
            continue
        ids = owned.get(target["id"], [])
        if (not ids or target.get("all_text_direct_bold") or target.get("controls")
                or MARKER.match(target["text"].lstrip()) or BOX_GLYPHS.search(target["text"])
                or any(catalog["candidates"][cid].get("type") != "text" for cid in ids)):
            continue
        result.append({"paragraph_id": option["id"], "quote": option["text"],
                       "alternative_paragraph_id": previous["id"],
                       "separator_paragraph_id": separator["id"],
                       "target_paragraph_id": target["id"], "candidate_ids": sorted(ids)})
    return result


def _clause(text):
    return norm(MARKER.sub("", text.strip())).rstrip(" :")


def condition_ids(audit, region):
    """The whole introducing clause, not a matching word or a distant condition."""
    keys = []
    for key, condition in audit.get("conditions", {}).items():
        evidence = condition.get("form_evidence") or {}
        if (not condition.get("validation_errors")
                and evidence.get("paragraph_id") == region["paragraph_id"]
                and _clause(evidence.get("quote", "")) == _clause(region["quote"])):
            keys.append(key)
    return keys


def apply(audit, catalog):
    found = regions(catalog)
    for region in found:
        keys = condition_ids(audit, region)
        for field in audit.get("fields", []):
            if field["candidate_id"] in region["candidate_ids"]:
                field["conditions"] = sorted(set(field.get("conditions", [])) | set(keys))
                for key in keys:
                    field.setdefault("condition_checks", {}).setdefault(
                        key, {"result": audit["conditions"][key].get("result", "unknown")})
        for key in keys:
            condition = audit["conditions"][key]
            condition["applies_to"] = sorted(set(condition.get("applies_to", []))
                                             | set(region["candidate_ids"]))
    audit["form_option_scope"] = {"revision": 1, "origin": "BACKEND", "regions": found}
    return audit


def uncovered_fields(data):
    """Recompute from the original FORM: missing/stale projections cannot grant permission."""
    if not enabled(data):
        return set()
    audit = data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    result = set()
    for region in regions(data.get("catalog") or {}):
        keys = set(condition_ids(audit, region))
        result.update(cid for cid in region["candidate_ids"] if not keys
                      or not keys <= set(fields.get(cid, {}).get("conditions", [])))
    return result


def blocked_fields(data):
    if not enabled(data):
        return set()
    from app.compilation_scope_review import valid_receipt

    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    result = uncovered_fields(data)
    for region in regions(data.get("catalog") or {}):
        for key in condition_ids(audit, region):
            receipt = answers.get("condition:" + key, {})
            for cid in region["candidate_ids"]:
                if (audit["conditions"][key].get("result") == "false"
                        or receipt.get("applies") is not True
                        or not valid_receipt(data, "condition:" + key, receipt, cid)):
                    result.add(cid)
    return result
