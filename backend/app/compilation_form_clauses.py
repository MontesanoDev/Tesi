"""FORM clauses: identifiable DOCX units that conditions, questions and answers refer to.

Revision 1, from the immutable catalog only:
- option: a body paragraph that starts with a native checkbox or a box glyph, with its
  continuation run (compilation_branch_scope);
- alternative: a member of a list the FORM asks to prune («(eliminare le opzioni non
  pertinenti)»). Members are the blank-separated runs of body paragraphs after the instruction,
  a table joining the run before it, up to the next bold paragraph without fields.

A model condition anchored on such a list (the instruction or the bold heading just before it)
and governing data inside its alternatives is split per alternative: each part is anchored on
its alternative with exactly those destinations (E2E Trapani: «(eliminare le opzioni non
pertinenti)» as the clause of the company data, 4 runs of 11 lost to a meaningless question).
Checkboxes and data outside the alternatives stay on the model condition: a box is a USER
choice, never an applicability confirmation. A condition anchored on a clause carries it, and
the question shows the clause label instead of the model's fragment.

No condition is invented, no destination loses or gains a restriction, nothing is selected or
authorized here: the backend gates read these conditions as any other.
"""

from __future__ import annotations

import re
from copy import deepcopy

from app.compilation_option_regions import BOX_GLYPHS
from app.requirement_checks import normalized_form_text as norm

REVISION = 1
PRUNE = re.compile(
    r"^\(?\s*(?:si\s+prega\s+di\s+)?(?:eliminare|cancellare|depennare|barrare)\b[^)]{0,60}?"
    r"\b(?:non\s+pertinent\w*|che\s+non\s+(?:interessano|ricorrono)|non\s+ricorrent\w*)")


def enabled(data):
    return data.get("generation_revision") == 3 and data.get("form_clause_revision") == REVISION


def _label(paragraph):
    """The clause words before its first destination: «Legale rappresentante di Società …»."""
    text = (paragraph.get("text_with_fields") or paragraph.get("text") or "").split("[[", 1)[0]
    text = " ".join(BOX_GLYPHS.sub(" ", re.sub(r"_{2,}|\.{3,}|…", " ", text)).split())
    return text.strip(" :;,.-") or " ".join(paragraph.get("text", "").split())[:200]


def _owned(catalog):
    owned = {}
    for cid, candidate in catalog.get("candidates", {}).items():
        owned.setdefault(candidate.get("context_id"), []).append(cid)
    return owned


def prune_lists(catalog):
    """[{header_ids, members: [{paragraph_id, paragraph_ids, label, candidate_ids}]}]."""
    owned, items = _owned(catalog), []
    for block in catalog.get("blocks", []):
        if block.get("tables"):
            items.append(("table", block["paragraphs"]))
        else:
            items.extend(("paragraph", p) for p in block["paragraphs"])
    result = []
    for index, (kind, paragraph) in enumerate(items):
        if kind != "paragraph" or owned.get(paragraph["id"]) or not PRUNE.match(
                norm(paragraph["text"]).strip()):
            continue
        header = [paragraph["id"]]
        previous = next((p for k, p in reversed(items[:index]) if k == "paragraph"
                         and p["text"].strip()), None) if index else None
        if (previous is not None and previous.get("all_text_direct_bold")
                and not owned.get(previous["id"]) and not previous.get("controls")):
            header.insert(0, previous["id"])
        members, current, blank = [], None, True
        for kind, item in items[index + 1:]:
            if kind == "table":
                if current is None:
                    break
                current["paragraph_ids"] += [p["id"] for p in item]  # Joins the run before it.
                blank = False
                continue
            text = item["text"].strip()
            if not text and not owned.get(item["id"]):
                blank = True
                continue
            if (item.get("all_text_direct_bold") and not owned.get(item["id"])
                    and not item.get("controls") and not norm(text).startswith("(")):
                break  # The next heading ends the list.
            if blank or current is None:
                current = {"paragraph_id": item["id"], "paragraph_ids": [item["id"]],
                           "label": _label(item)}
                members.append(current)
            else:
                current["paragraph_ids"].append(item["id"])
            blank = False
        for member in members:
            member["candidate_ids"] = sorted(c for pid in member["paragraph_ids"]
                                             for c in owned.get(pid, []))
        members = [m for m in members if m["candidate_ids"]]
        if len(members) >= 2:
            result.append({"header_ids": header, "members": members})
    return result


def clauses(catalog):
    """paragraph id -> {id, kind, paragraph_id, label, candidate_ids}."""
    from app.compilation_branch_scope import continuations

    paragraphs = {p["id"]: p for b in catalog.get("blocks", []) for p in b["paragraphs"]}
    owned, result = _owned(catalog), {}
    for pid, run in continuations(catalog).items():
        result[pid] = {"id": "clause:" + pid, "kind": "option", "paragraph_id": pid,
                       "label": _label(paragraphs[pid]),
                       "candidate_ids": sorted({*owned.get(pid, []), *run})}
    for listing in prune_lists(catalog):
        for member in listing["members"]:
            result.setdefault(member["paragraph_id"], {
                "id": "clause:" + member["paragraph_id"], "kind": "alternative",
                "paragraph_id": member["paragraph_id"], "label": member["label"],
                "candidate_ids": member["candidate_ids"],
                "list_header_ids": listing["header_ids"]})
    return result


def _public(clause):
    return {k: clause[k] for k in ("id", "kind", "paragraph_id", "label")}


def apply(audit, catalog):
    """Anchor model conditions on FORM clauses; split list-anchored ones per alternative."""
    registry = clauses(catalog)
    paragraphs = {p["id"]: p for b in catalog.get("blocks", []) for p in b["paragraphs"]}
    headers = {pid: [registry[m["paragraph_id"]] for m in listing["members"]]
               for listing in prune_lists(catalog) for pid in listing["header_ids"]}
    boxes = {cid for cid, c in catalog.get("candidates", {}).items() if c.get("type") == "checkbox"}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    report = {"revision": REVISION, "origin": "BACKEND", "anchored": {}, "split": {}}
    for key, condition in list((audit.get("conditions") or {}).items()):
        anchor = (condition.get("form_evidence") or {}).get("paragraph_id")
        if condition.get("validation_errors") or not anchor:
            continue
        if anchor in registry:
            condition["form_clause"] = _public(registry[anchor])
            report["anchored"][key] = registry[anchor]["id"]
            continue
        parts = {}
        for cid in condition.get("applies_to", []):
            member = next((m for m in headers.get(anchor, []) if cid in m["candidate_ids"]), None)
            if member is not None and cid not in boxes:
                parts.setdefault(member["paragraph_id"], []).append(cid)
        for pid, ids in parts.items():
            new = f"{key}__{pid.removeprefix('paragraph:')}"
            derived = deepcopy(condition)
            derived.update(form_evidence={"paragraph_id": pid, "quote": paragraphs[pid]["text"]},
                           applies_to=sorted(ids), form_clause=_public(registry[pid]),
                           derived_from=key)
            audit["conditions"][new] = derived
            for cid in ids:
                field = fields.get(cid)
                if field is None:
                    continue
                field["conditions"] = list(dict.fromkeys(
                    new if c == key else c for c in field.get("conditions", [])))
                checks = field.get("condition_checks") or {}
                if key in checks:
                    checks[new] = checks.pop(key)
            report["split"].setdefault(key, {})[new] = sorted(ids)
        if parts:
            moved = {c for ids in parts.values() for c in ids}
            condition["applies_to"] = [c for c in condition.get("applies_to", [])
                                       if c not in moved]
    audit["form_clauses"] = report
    return audit
