"""Identifiers of different types are not alternatives of one field (identifier_type_revision 1).

Real Minervino run: the model gave a Register number and a REA number the same property and
marked «al n.» ambiguous, although the SOURCE labels each one and even says the REA «non è» the
Register number. The USER was asked to choose, then to transcribe, what the documents already say.

The type is read from text only: the label right before the value in the cited SOURCE line, and
the FORM text right before the destination. Never from the model's property, reason or label.
- One value of the requested type, the others of a known different type: the proposal is rewritten
  before validation, so the chosen fact goes through every ordinary gate; no new write path.
- Two different values of the requested type: a real conflict, kept and explained.
- A type that cannot be read on either side: nothing changes.
- A single proposal of a known different type: another fact of the same subject with the requested
  type replaces it; otherwise the proposal is dropped and the field stays empty.
"""

from __future__ import annotations

import json
import re

REVISION = 1
LABELS = {
    "partita_iva": r"partita\s+iva|p\.?\s?iva\b|\bvat\b",
    "codice_fiscale": r"codice\s+fiscale|\bc\.\s?f\.?(?=\W|$)|\bcf\b",
    "rea": r"\br\.?\s?e\.?\s?a\.?(?=\W|$)|repertorio\s+economico",
    "registro_imprese": r"registro\s+(?:delle\s+)?imprese|\br\.\s?i\.(?=\W|$)",
    "albo": r"\balbo\b|\bordine\b|\bcollegio\b",
}
COMPILED = {kind: re.compile(pattern, re.IGNORECASE) for kind, pattern in LABELS.items()}
INSTITUTION = re.compile(r"camera\s+di\s+commercio|\bc\.?\s?c\.?\s?i\.?\s?a\.?\s?a\.?(?=\W|$)",
                         re.IGNORECASE)
BARE_NUMBER = re.compile(r"(?:\bal|\bcon\s+il|\bcon|\biscrizione\s+al|\biscrizione)?\s*"
                         r"(?:\bn\.?|\bn°|\bnumero)\s*$", re.IGNORECASE)
NAMES = {"partita_iva": "Partita IVA", "codice_fiscale": "codice fiscale", "rea": "numero REA",
         "registro_imprese": "Registro Imprese", "albo": "albo professionale"}
REACH = 90
GAP = 40


def enabled(data):
    return data.get("identifier_type_revision") == REVISION


def _matches(text):
    found = sorted((m.end(), m.start(), kind) for kind, pattern in COMPILED.items()
                   for m in pattern.finditer(text))
    return found


def _closest(text):
    """(kinds, end): the label nearest the end of this text, with a combined one before it."""
    found = _matches(text)
    if not found:
        return set(), -1
    end, start, kind = found[-1]
    kinds = {kind}
    for other_end, other_start, other in reversed(found[:-1]):
        if other_end == end or re.fullmatch(r"\s*(?:e|ed|/|-|,)\s*", text[other_end:start]):
            kinds.add(other)
            start = min(start, other_start)
    return kinds, end


def evidence_types(fact, source_map):
    """The types the SOURCE labels this value with; empty when no line shows a label for it.

    Only a label just before the value counts: no other figures in between, within a short gap.
    """
    value = " ".join(str(fact.get("value") or "").split()).casefold()
    token = re.compile(r"(?<![\w])" + re.escape(value) + r"(?![\w])") if value else None
    found = set()
    for proof in fact.get("evidence") or fact.get("source_evidence") or []:
        content = (source_map.get(proof.get("chunk_id")) or {}).get("content", "")
        quote = " ".join(str(proof.get("quote") or "").split()).casefold()
        for line in content.splitlines():
            flat = " ".join(line.split()).casefold()
            if not token or (quote and quote not in flat and flat not in quote):
                continue
            # Every occurrence: a company's tax code and VAT number can be the same figure.
            for match in token.finditer(flat):
                kinds, end = _closest(flat[:match.start()])
                gap = flat[max(end, 0):match.start()]
                if kinds and len(gap) <= GAP and not re.search(r"\d", gap):
                    found |= kinds
    return found


def _form_label(text):
    """The type a FORM label asks for: it must be the last thing before the blank."""
    stripped = text.rstrip(" :.,;_-–\t")
    kinds, end = _closest(stripped)
    return kinds if kinds and end >= len(stripped) - 1 else set()


def destination_type(candidate, paragraphs, tables):
    """The type the FORM asks for at this destination, from its own text; None when unsaid."""
    before = str((candidate.get("slot_context") or {}).get("before") or "")
    location = candidate.get("location") or {}
    if not before and location.get("table_id"):
        rows = (tables.get(location["table_id"]) or {}).get("rows") or []
        index = location.get("row_index")
        row = rows[index] if isinstance(index, int) and 0 <= index < len(rows) else []
        label = row[0] if len(row) == 2 else {}
        before = " ".join(str((paragraphs.get(p) or {}).get("text") or "")
                          for p in label.get("paragraph_ids", []))
    local = before[-REACH:]
    kinds = _form_label(local)
    if kinds:
        return next(iter(kinds)) if len(kinds) == 1 else None
    if not BARE_NUMBER.search(local):
        return None
    kinds, _ = _closest(BARE_NUMBER.sub("", local))
    if kinds:  # «REA n.», «Ordine … con il n°»: the label names this very number.
        return next(iter(kinds)) if len(kinds) == 1 else None
    paragraph = paragraphs.get(candidate.get("context_id"), {})
    marked = str(paragraph.get("text_with_fields") or "")
    marker = f"[[{candidate.get('id')}]]"
    earlier = marked.split(marker)[0] if marker in marked else local
    earlier = re.sub(r"\[\[[^]]+\]\]", " ", earlier)
    earlier = BARE_NUMBER.sub("", earlier)[-REACH:]
    kinds, end = _closest(earlier)
    institution = [m.end() for m in INSTITUTION.finditer(earlier)]
    if institution and institution[-1] > end:
        return "registro_imprese"  # A bare number after a Chamber of Commerce: its Register entry.
    return next(iter(kinds)) if len(kinds) == 1 else None


def _value(fact):
    return re.sub(r"[\s.\-/]", "", str(fact.get("value") or "")).casefold()


def resolve(raw, catalog, sources):
    """(raw, resolutions): the merged proposal with typed choices; the model output stays stored."""
    payload = json.loads(raw)
    source_map = {s["chunk_id"]: s for s in sources}
    blocks = catalog.get("blocks", [])
    paragraphs = {p["id"]: p for b in blocks for p in b.get("paragraphs", [])}
    tables = {t["id"]: t for b in blocks for t in b.get("tables", [])}
    facts, fields = payload.get("facts") or {}, payload.get("fields") or {}
    resolutions = {}
    for cid, field in fields.items():
        candidate = catalog.get("candidates", {}).get(cid)
        if not isinstance(field, dict) or not candidate or candidate.get("type") != "text":
            continue
        wanted = destination_type({**candidate, "id": cid}, paragraphs, tables)
        if wanted is None:
            continue
        options = [f for f in field.get("alternative_fact_ids") or [] if f in facts]
        if len(options) >= 2:
            resolution = _choose(field, options, facts, source_map, wanted)
        elif field.get("fact_id") in facts:
            resolution = _single(field, facts, source_map, wanted)
        else:
            resolution = None
        if resolution:
            resolutions[cid] = {"wanted": wanted, **resolution}
    return (json.dumps(payload, ensure_ascii=False), resolutions) if resolutions else (
        raw, {})


def _choose(field, options, facts, source_map, wanted):
    typed = {f: evidence_types(facts[f], source_map) for f in options}
    same = [f for f in options if wanted in typed[f]]
    if not same or any(not typed[f] for f in options):
        return None  # A value without a readable type could still be the requested one.
    values = {_value(facts[f]) for f in same}
    others = {f: sorted(typed[f]) for f in options if f not in same}
    if len(values) == 1:
        field.update(fact_id=same[0], disposition="conditional" if field.get("conditions")
                     else "value")
        field.pop("alternative_fact_ids", None)
        field.pop("review_kind", None)
        return {"action": "selected", "fact_id": same[0], "excluded": others}
    if not others:
        return {"action": "conflict", "values": [facts[f].get("value") for f in same]}
    field.update(alternative_fact_ids=same)
    return {"action": "conflict", "values": [facts[f].get("value") for f in same],
            "excluded": others}


def _single(field, facts, source_map, wanted):
    fact_id = field["fact_id"]
    kinds = evidence_types(facts[fact_id], source_map)
    if not kinds or wanted in kinds:
        return None
    subject = " ".join(str(facts[fact_id].get("subject") or "").split()).casefold()
    better = {fid: fact for fid, fact in facts.items() if isinstance(fact, dict)
              and " ".join(str(fact.get("subject") or "").split()).casefold() == subject
              and wanted in evidence_types(fact, source_map)}
    values = {_value(fact) for fact in better.values()}
    if len(values) == 1:
        replacement = next(iter(better))
        field["fact_id"] = replacement
        if better[replacement].get("property"):
            field["property"] = better[replacement]["property"]
        return {"action": "replaced", "fact_id": replacement, "excluded": {fact_id: sorted(kinds)}}
    field.pop("fact_id", None)
    field["disposition"] = "missing"
    field["reason"] = (f"Il valore citato è un identificativo di tipo diverso da "
                       f"{NAMES.get(wanted, wanted)}")
    return {"action": "dropped", "excluded": {fact_id: sorted(kinds)}}
