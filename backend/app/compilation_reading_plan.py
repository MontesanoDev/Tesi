"""Compact reading references, never semantic evidence or writable assignments."""

import re
import unicodedata

MAX_ROLE_TARGETS = 32
MAX_RECORDS_PER_TARGET = 4


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def reading_plan(catalog, sources, contexts):
    paragraphs = {p["id"]: p["text"] for b in catalog["blocks"] for p in b["paragraphs"]}
    units = {}
    for cid, candidate in catalog["candidates"].items():
        if candidate["type"] != "text":
            continue
        origin = (candidate.get("continuation_origin_paragraph_id")
                  or candidate["location"].get("table_id") or candidate["context_id"])
        units.setdefault(origin, []).append(cid)
    targets, omitted = {}, 0
    for source in sources:
        if source.get("category") == "general":
            continue
        for line in source["content"].splitlines():
            header = re.fullmatch(r"\s*#{1,6}\s+(.+?)\s+[-–—]\s+(.+?)\s*", line)
            if not header or len(header[2]) > 150 or len(line) > 400:
                continue
            role = header[2].strip()
            pattern = r"(?<!\w)" + re.escape(normalized(role)) + r"(?!\w)"
            for pid, text in paragraphs.items():
                if not re.search(pattern, normalized(text)):
                    continue
                candidates = [cid for cid, candidate in catalog["candidates"].items()
                              if candidate["type"] == "text" and pid in contexts[cid]]
                if not candidates:
                    continue
                key = (pid, normalized(role))
                if key not in targets:
                    if len(targets) == MAX_ROLE_TARGETS:
                        omitted += 1
                        continue
                    targets[key] = {"form_paragraph_id": pid, "source_role": role,
                                    "candidate_ids": candidates, "source_records": []}
                records = targets[key]["source_records"]
                record = {"chunk_id": source["chunk_id"], "header": line.strip()}
                if record not in records:
                    if len(records) < MAX_RECORDS_PER_TARGET:
                        records.append(record)
                    else:
                        omitted += 1
    return {"units": [{"context_id": key, "candidate_ids": ids} for key, ids in units.items()],
            "source_role_targets": list(targets.values()), "omitted_role_hints": omitted,
            "meaning": "Reading references only; each value still needs its own validated SOURCE."}


def role_coverage(audit, plan):
    fields = {f["candidate_id"]: f for f in audit["fields"]}
    result = []
    for target in plan["source_role_targets"]:
        assigned = [cid for cid in target["candidate_ids"] if (
            fields[cid].get("validation") == "GROUNDED_PROPOSAL"
            or fields[cid].get("proposal_grounding") == "GROUNDED_PROPOSAL")]
        result.append({**target, "source_proposal_ids": assigned,
                       "state": "proposals_present" if assigned else "unassessed_source_role"})
    return result
