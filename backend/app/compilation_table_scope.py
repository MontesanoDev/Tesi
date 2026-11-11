"""Opt-in rev3: an explicit conditional table caption needs its own applicability check.

Only a non-editable, one-cell caption table with a bold instruction «da compilare
in/nel caso di», immediately followed by a data table (blank paragraphs allowed).
No entity-type inference, invented condition or automatic USER authorization.
Missing/invalid/uncoupled conditions keep both SOURCE and USER writes blocked.
"""
from __future__ import annotations

import re

from app.requirement_checks import normalized_form_text as norm


def enabled(data):
    return data.get("generation_revision") == 3 and data.get("table_scope_revision") == 1


def scopes(catalog):
    result = []
    for index, block in enumerate(catalog["blocks"]):
        tables = block.get("tables", [])
        if len(tables) != 1 or len(tables[0]["rows"]) != 1 or len(tables[0]["rows"][0]) != 1:
            continue
        table = tables[0]
        caption = table["rows"][0][0]
        if caption.get("table_ids"):
            continue
        if any(c.get("location", {}).get("table_id") == table["id"]
               for c in catalog["candidates"].values()):
            continue
        paragraphs = [p for p in block["paragraphs"] if p["id"] in caption["paragraph_ids"]]
        anchors = {p["id"] for p in paragraphs if p["text"].strip()}
        conditional = False
        for p in paragraphs:
            text = norm(p["text"])
            for marker in ("da compilare in caso di ", "da compilare nel caso di "):
                prefix, found, tail = text.partition(marker)
                if found and tail and p.get("all_text_direct_bold") and re.fullmatch(
                    r"[\d.()\s]*[a-z]?[.)\s]*", prefix):
                    conditional = True
        if not conditional:
            continue
        for next_block in catalog["blocks"][index + 1:]:
            following = next_block.get("tables", [])
            if following:
                if len(following) == 1:
                    ids = [cid for cid, c in catalog["candidates"].items()
                           if c.get("location", {}).get("table_id") == following[0]["id"]]
                    if ids:
                        result.append({"anchor_ids": sorted(anchors), "candidate_ids": ids,
                                       "table_id": following[0]["id"]})
                break
            if any(p["text"].strip() for p in next_block["paragraphs"]):
                break
    return result



def condition_ids(audit, region):
    return [key for key, c in audit.get("conditions", {}).items()
            if not c.get("validation_errors") and (c.get("form_evidence") or {}).get(
                "paragraph_id") in region["anchor_ids"]]


def apply(audit, catalog):
    regions = scopes(catalog)
    for region in regions:
        keys = condition_ids(audit, region)
        for field in audit.get("fields", []):
            if field["candidate_id"] in region["candidate_ids"]:
                field["conditions"] = sorted(set(field.get("conditions", [])) | set(keys))
        for key in keys:
            condition = audit["conditions"][key]
            condition["applies_to"] = sorted(set(condition.get("applies_to", []))
                                               | set(region["candidate_ids"]))
    audit["table_scope"] = {"revision": 1, "origin": "BACKEND", "regions": regions}
    return audit


def blocked_fields(data):
    if not enabled(data):
        return set()
    audit = data.get("audit") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    blocked = set()
    # Recompute from the original catalog: missing/stale projection is never permission.
    for region in scopes(data.get("catalog") or {"blocks": [], "candidates": {}}):
        required = set(condition_ids(audit, region))
        for cid in region["candidate_ids"]:
            if not required or not required <= set(fields.get(cid, {}).get("conditions", [])):
                blocked.add(cid)
    return blocked
