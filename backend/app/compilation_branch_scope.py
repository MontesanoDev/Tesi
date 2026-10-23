"""Candidate rev 3: an option's condition also covers the option's continuation (catalog only).

An option is a body paragraph that starts with a native checkbox or a V14 box glyph. Its
continuation is the run of body paragraphs that follows, up to the first empty paragraph,
option, bold paragraph without fields, separator line or table. A model condition anchored
on the option paragraph is linked to the destinations of that run exactly as the validator
links it to the option's own paragraph: the existing gates (dialogue, rev 3 scope receipts,
export) then treat them alike.

This only extends the reach of a condition the model already stated on that option.
It never creates a condition, never decides a branch and never infers a section:
headings, words such as «OPPURE» and options without an anchored condition are untouched.
As in V14, «[ ]» is not recognized: it neither starts nor ends a run.
"""

from __future__ import annotations

import re

from app.compilation_option_regions import BOX_GLYPHS

REVISION = 1


def enabled(data):
    return data.get("generation_revision") == 3 and data.get("branch_scope_revision") == REVISION


def _is_option(paragraph, text):
    controls = paragraph.get("controls") or []
    start = len(text) - len(text.lstrip())
    # The control precedes every printed character of the paragraph.
    return any(c["offset"] <= start for c in controls) or bool(BOX_GLYPHS.match(text.lstrip()))


def _ends_run(paragraph, text, own):
    # A separator has no letters or digits; a dotted fill-in line has its own destinations.
    return (not text.strip() or _is_option(paragraph, text)
            or (not own and (paragraph.get("all_text_direct_bold")
                             or not re.search(r"[^\W_]", text))))


def continuations(catalog):
    """Option paragraph id -> ordered candidate ids of its continuation run."""
    cells = {pid for block in catalog["blocks"] for table in block.get("tables", [])
             for row in table["rows"] for cell in row for pid in cell["paragraph_ids"]}
    owned = {}
    for cid, candidate in catalog["candidates"].items():
        owned.setdefault(candidate.get("context_id"), []).append(cid)
    body = [(block, paragraph) for block in catalog["blocks"]
            for paragraph in block["paragraphs"]]
    result = {}
    for index, (_, paragraph) in enumerate(body):
        if paragraph["id"] in cells or not _is_option(paragraph, paragraph["text"]):
            continue
        run = []
        for block, following in body[index + 1:]:
            own = owned.get(following["id"], [])
            if (following["id"] in cells or block.get("tables")
                    or _ends_run(following, following["text"], own)):
                break
            run += own
        if run:
            result[paragraph["id"]] = run
    return result


def propagate(audit, catalog):
    """Link option-anchored conditions to their continuation; record every added link."""
    runs = continuations(catalog)
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    added = {}
    for key, condition in (audit.get("conditions") or {}).items():
        anchor = (condition.get("form_evidence") or condition.get("form") or {}).get(
            "paragraph_id")
        if anchor not in runs or condition.get("validation_errors"):
            continue
        new = [cid for cid in runs[anchor] if cid in fields
               and key not in fields[cid].get("conditions", [])]
        for cid in new:
            fields[cid]["conditions"] = [*fields[cid].get("conditions", []), key]
        if new:
            condition["applies_to"] = sorted({*condition.get("applies_to", []), *new})
            added[key] = {"paragraph_id": anchor, "candidate_ids": new}
    audit["branch_scope"] = {"revision": REVISION, "origin": "BACKEND",
                             "option_continuations": added}
    return audit
