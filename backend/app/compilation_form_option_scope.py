"""Bounded FORM dependencies of printed data on the FORM text that introduces them.

Revision 1: ASCII alternative ending in ':' -> next data paragraph. Recognizes only two
fixed body options separated by an isolated OPPURE. Blank paragraphs are allowed; tables
and any intervening printed text break the link.
Revision 2 adds explicit conditional instructions: an entirely bold body paragraph without
fields, «(da compilare in/nel caso di …)» (the markers of compilation_table_scope), governs
the text destinations of the following body paragraphs up to a table, the next instruction
or a bold paragraph without fields that is not a parenthetical note.
This is not checkbox parsing, entity classification or procedural authorization.
No missing MODEL condition is invented, and no SOURCE fact chooses an option.
"""
import re

from app.compilation_option_regions import BOX_GLYPHS
from app.requirement_checks import normalized_form_text as norm

MARKER = re.compile(r"^\[\s*\]")
INSTRUCTIONS = ("da compilare in caso di ", "da compilare nel caso di ")


def enabled(data):
    return (data.get("generation_revision") == 3
            and data.get("form_option_scope_revision") in {1, 2})


def _option(paragraph, owned):
    text = paragraph["text"].strip()
    return (MARKER.match(text) and len(re.findall(r"\[[^\]]*\]", text)) == 1
            and not BOX_GLYPHS.search(text) and not paragraph.get("controls")
            and not owned.get(paragraph["id"]))


def _instruction(paragraph, owned):
    if (owned.get(paragraph["id"]) or paragraph.get("controls")
            or not paragraph.get("all_text_direct_bold")):
        return False
    text = norm(paragraph["text"])
    for marker in INSTRUCTIONS:
        prefix, found, tail = text.partition(marker)
        if found and tail.strip(" ().;:") and re.fullmatch(r"[\d.()\s]*[a-z]?[.)\s]*", prefix):
            return True
    return False


def _instruction_regions(catalog, owned, body):
    result = []
    for index, paragraph in enumerate(body):
        if paragraph is None or not _instruction(paragraph, owned):
            continue
        scope = []
        for following in body[index + 1:]:
            # A table, the next instruction or a heading ends the scope; parenthetical bold
            # notes inside repeated member blocks do not.
            if (following is None or _instruction(following, owned)
                    or (following.get("all_text_direct_bold") and not owned.get(following["id"])
                        and not following.get("controls")
                        and not norm(following["text"]).startswith("("))):
                break
            scope.append(following["id"])
        ids = sorted(cid for cid, candidate in catalog['candidates'].items()
                     if candidate.get('context_id') in scope
                     and (candidate.get('type') == 'text'
                          or candidate.get('control_type') == 'text_ascii'))
        if ids:
            result.append({"kind": "instruction", "paragraph_id": paragraph["id"],
                           "quote": paragraph["text"], "paragraph_ids": scope,
                           "candidate_ids": ids})
    return result


def regions(catalog, revision=1):
    # Text markers were already FORM scope boundaries before becoming writable.
    # Preserve that structural view so enabling their writer cannot erase a veto.
    textual = {cid for cid, c in catalog.get('candidates', {}).items()
               if c.get('control_type') == 'text_ascii'}
    owned = {}
    for cid, candidate in catalog.get("candidates", {}).items():
        if cid in textual:
            continue
        owned.setdefault(candidate.get("context_id"), []).append(cid)
    # None is a barrier, including nested/cell paragraphs. Never cross a table.
    body = []
    for block in catalog.get("blocks", []):
        if block.get("tables"):
            body.append(None)
        else:
            body.extend({**p, 'controls': [c for c in p.get('controls', [])
                                         if c['id'] not in textual]} if textual else p
                        for p in block["paragraphs"] if p["text"].strip()
                        or p.get("controls") or owned.get(p["id"]))
    result = _instruction_regions(catalog, owned, body) if revision == 2 else []
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


def _instruction_clause(text):
    return norm(text).strip(" ().;:")


def _covers_instruction(quote, instruction):
    """Whole instruction, or an anchored prefix reaching at least its first alternative.

    A trailing legal reference may be left out; an inner fragment, a prefix that stops
    before the first «ovvero», comma or semicolon, or one cut inside a word is not enough.
    """
    q, full = _instruction_clause(quote), _instruction_clause(instruction)
    if q == full:
        return True
    marker = next((m.strip() for m in INSTRUCTIONS if m.strip() in full), None)
    if not marker or marker not in q or not full.startswith(q):
        return False
    start = full.index(marker) + len(marker)
    cuts = [i for i in (full.find(" ovvero ", start), full.find(",", start),
                        full.find(";", start)) if i >= 0]
    return len(q) >= (min(cuts) if cuts else len(full)) and full[len(q)] in " ,;)"


def condition_ids(audit, region):
    """The whole introducing clause, not a matching word or a distant condition."""
    instruction = region.get("kind") == "instruction"
    keys = []
    for key, condition in audit.get("conditions", {}).items():
        evidence = condition.get("form_evidence") or {}
        quote = evidence.get("quote", "")
        if (not condition.get("validation_errors")
                and evidence.get("paragraph_id") == region["paragraph_id"]
                and (_covers_instruction(quote, region["quote"]) if instruction
                     else _clause(quote) == _clause(region["quote"]))):
            keys.append(key)
    return keys


def apply(audit, catalog, revision=1):
    found = regions(catalog, revision)
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
    audit["form_option_scope"] = {"revision": revision, "origin": "BACKEND", "regions": found}
    return audit


def _uncovered(data, kinds):
    if not enabled(data):
        return set()
    audit = data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    result = set()
    for region in regions(data.get("catalog") or {}, data["form_option_scope_revision"]):
        if region.get("kind", "option") not in kinds:
            continue
        keys = set(condition_ids(audit, region))
        result.update(cid for cid in region["candidate_ids"] if not keys
                      or not keys <= set(fields.get(cid, {}).get("conditions", [])))
    return result


def uncovered_fields(data):
    """Recompute from the original FORM: missing/stale projections cannot grant permission."""
    return _uncovered(data, {"option", "instruction"})


def instruction_uncovered_fields(data):
    return _uncovered(data, {"instruction"})


def blocked_fields(data):
    if not enabled(data):
        return set()
    from app.compilation_scope_review import valid_receipt

    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    result = uncovered_fields(data)
    for region in regions(data.get("catalog") or {}, data["form_option_scope_revision"]):
        for key in condition_ids(audit, region):
            receipt = answers.get("condition:" + key, {})
            for cid in region["candidate_ids"]:
                if (audit["conditions"][key].get("result") == "false"
                        or receipt.get("applies") is not True
                        or not valid_receipt(data, "condition:" + key, receipt, cid)):
                    result.add(cid)
    return result
