"""Candidate rev 3: a hold that cites another condition's clause gets one narrator re-review.

The backend proves only a misattribution: the hold's applicability quote, not anchored in the
proposal's own context, is the FORM clause of exactly one model condition that does not govern
the proposal. It never releases the hold itself. At the next narration the proposal returns to
the review window once, with that finding. The narrator either holds it again (kept: anchored
reasons follow the usual USER blocker, others stay held without further reviews) or not (the
proposal goes back to the unchanged backend gates). SOURCE, USER and export gates are untouched.
"""

from __future__ import annotations

REVISION = 1
NOTE = ("Controllo del backend: la clausola citata è la condizione di altre destinazioni e non "
        "governa questa proposta. Se resta un dubbio proprio, sospendila di nuovo citando il suo "
        "contesto; per questa sola proposta l'assenza da held_proposal_slots la restituisce ai "
        "controlli del backend.")


def enabled(data):
    return (data.get("generation_revision") == 3
            and data.get("hold_rereview_revision") == REVISION)


def foreign_condition(audit, cid, quote):
    """The single model condition whose FORM clause is quoted, if it does not govern cid."""
    from app.requirement_checks import normalized_form_text as norm

    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    text = norm(quote or "")
    cited = [key for key, condition in (audit.get("conditions") or {}).items()
             if text and text == norm((condition.get("form_evidence") or {}).get("quote", ""))]
    if len(cited) != 1:
        return None
    key = cited[0]
    if key in field.get("conditions", []) or cid in audit["conditions"][key].get(
            "applies_to", []):
        return None
    return key


def due(data):
    """Held proposals waiting for their single re-review."""
    if not enabled(data):
        return set()
    dialogue = data.get("dialogue") or {}
    records = dialogue.get("hold_records", {})
    return {cid for cid in dialogue.get("held_candidate_ids", [])
            if records.get(cid, {}).get("rereview") == "pending"}
