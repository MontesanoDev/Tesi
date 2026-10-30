"""Deterministic review of narrator holds on documented proposals (hold_review_revision 1).

E2E campaigns of 30 October: 129 of 139 narrator holds blocked values equal to the gold or
differing only in form, and the frozen USER policy deferred the verification questions they
produced, so one Minervino run lost 18 values to doubts such as «schede dimostrative non
verificate». A narrator doubt never blocks a valid value by itself and never authorizes it:
the backend decides from SOURCE, conditions, receipts and validators only.

- evidenza_assente: no grounded proposal; the validators already block it, the hold stays.
- evidenza_contraddittoria: a SOURCE statement outside the proposal's own evidence, in a chunk
  naming the same subject, says the same property is not available or has ceased; the hold
  stays and the USER gets a verification question with both texts.
- applicabilita_incerta: a governing condition is still open; the hold waits for it (its
  question is asked anyway).
- applicabilita_confermata / dubbio_generico: every governing condition is confirmed (or there
  is none) and nothing contradicts the value: the proposal goes back to the ordinary gates,
  which alone decide the export, and the draft lists it as to be reviewed.
A checkbox option stays a USER choice; an applicability doubt on a FORM clause the backend
cannot map to a condition of an unconditional field stays a question.
"""

from __future__ import annotations

import re

from app.requirement_checks import normalized_form_text as norm

REVISION = 1
CONTRARY = re.compile(
    r"\bnon\s+(?:è\s+|sono\s+)?(?:disponibil\w*|indicat\w*|present\w*|attestat\w*|"
    r"documentat\w*|riportat\w*|not[oi]\b|reperibil\w*)|\bassent[ei]\b|\bmancant[ei]\b|"
    r"\bcessat\w*|\bcessazione\b|\bnon\s+più\b|\bscadut\w*|\brevocat\w*|\bdimess\w*")
STOP = {"della", "dello", "delle", "degli", "dati", "dato", "anno", "numero", "nome", "data"}


def enabled(data):
    return data.get("hold_review_revision") == REVISION


def _words(text):
    return {w for w in re.findall(r"[^\W\d_]{4,}", norm(text or "")) if w not in STOP}


def _contrary(field, fact, quote, sources):
    """The SOURCE statement that says this subject's property is unavailable or ceased."""
    text = norm(quote or "")
    own = [norm(e.get("quote", "")) for e in field.get("source_evidence", [])]
    if len(text) < 8 or not CONTRARY.search(text) or any(text in q or q in text for q in own):
        return None
    subject = [w for w in _words(fact.get("subject")) if len(w) >= 4]
    about = _words(f"{field.get('label')} {fact.get('property')}".replace("_", " "))
    if not subject or not about & _words(text):
        return None
    for source in sources:
        content = norm(source.get("content", ""))
        if text in content and any(w in content for w in subject):
            return {"quote": quote, "source_name": source.get("source_name"),
                    "chunk_id": source.get("chunk_id")}
    return None


def review(data, cid, record, sources):
    """{verdict, action: keep|verify|select|bind|release, key?, contrary?} for one hold."""
    from app.compilation_global_dialogue import documented_proposal

    audit = data.get("audit") or {}
    answers = (data.get("dialogue") or {}).get("answers", {})
    field = next((f for f in audit.get("fields", []) if f["candidate_id"] == cid), {})
    if not field or not documented_proposal(field):
        return {"verdict": "evidenza_assente", "action": "keep"}
    fact = audit.get("facts", {}).get(field.get("fact_id") or field.get("proposed_fact_id"), {})
    contrary = _contrary(field, fact, record.get("evidence_quote"), sources)
    if contrary:
        return {"verdict": "evidenza_contraddittoria", "action": "verify", "contrary": contrary}
    if field.get("choice_group_id") or field.get("kind") == "choice":
        return {"verdict": "applicabilita_incerta", "action": "select"}  # A USER selection.
    keys = list(dict.fromkeys(field.get("conditions", [])))
    state = {c: answers.get("condition:" + c, {}).get("applies") for c in keys}
    results = {c: (audit.get("conditions", {}).get(c) or {}).get("result") for c in keys}
    if any(state[c] is False or results[c] == "false" for c in keys):
        return {"verdict": "evidenza_assente", "action": "keep"}  # Excluded: gates block it.
    open_keys = [c for c in keys if state[c] is not True and results[c] != "true"]
    if open_keys:
        return {"verdict": "applicabilita_incerta", "action": "bind",
                "key": "conditions:" + "+".join(sorted(keys))}
    if not keys and record.get("cause") in {"applicabilita_incerta", "scelta_USER"}:
        return {"verdict": "applicabilita_incerta", "action": "verify"}
    return {"verdict": "applicabilita_confermata" if keys else "dubbio_generico",
            "action": "release"}
