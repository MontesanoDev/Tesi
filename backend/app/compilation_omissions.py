"""Omitted proposals worth one targeted recovery (omission_recovery_revision 1).

Real campaign on 94e8726 (Minervino run 1): the model left 19 member destinations without any
proposal, declaring them «unassessed» («Tre soci documentati in tabella; il FORM non indica quale
nominativo occupi lo slot 1»), although SOURCE documents them and other runs fill them. In the
59 recent real runs the explanations split sharply. The other ones («source_not_found»,
«manual_input», «condition_unknown», a rejected explanation, a USER clarification) covered 5.336
positions outside the gold values and 49 missing values (13 of them from failed segments, now
retried for JSON syntax). «unassessed» on a destination with a FORM anchor was always a missing
value (21 of 21 over all recorded runs); «unassessed» without an anchor was a layout cell.

Only those are omissions: a text destination with no proposal and no validator rejection, that
the model itself declared not assessed, with a FORM anchor (paragraph or slot text). They go back
to the model in the segment's single recovery call, under the same validators; nothing is
filled by the backend, and justified empties are never touched.
"""

from __future__ import annotations

import re

REVISION = 1


def enabled(data):
    return data.get("omission_recovery_revision") == REVISION


def _anchored(candidate):
    slot = candidate.get("slot_context") or {}
    text = f"{slot.get('before', '')} {slot.get('after', '')}"
    return bool(candidate.get("anchor_paragraph_ids")) or bool(re.search(r"[^\W\d_]{3,}", text))


def label(candidate, cid):
    before = " ".join(((candidate.get("slot_context") or {}).get("before") or "").split())
    return before.strip(" :.;,_")[-80:] or cid


def omitted_destinations(payload, audit, candidate_ids, catalog):
    """{cid: {label, reasons}} for the destinations the model declared not assessed."""
    from app.compilation_segments import _proposes

    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    result = {}
    for cid in candidate_ids:
        candidate = (catalog.get("candidates") or {}).get(cid) or {}
        field, record = fields.get(cid) or {}, (payload.get("fields") or {}).get(cid)
        coverage = field.get("coverage") or {}
        if (candidate.get("type") != "text" or _proposes(record)
                or field.get("validation_errors") or not _anchored(candidate)
                or coverage.get("state") != "UNASSESSED" or coverage.get("origin") != "MODEL"):
            continue
        result[cid] = {"label": label(candidate, cid),
                       "reasons": [str(coverage.get("reason") or "non valutata")[:240]]}
    return result
