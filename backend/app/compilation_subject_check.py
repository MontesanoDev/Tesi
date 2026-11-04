"""Whose data is it? Evidence, destinations and USER replies (subject_check_revision 1).

A fact's subject was a claim of the model: validators read the value in the citation and the
entity type asked by the FORM, never whether the cited line belongs to that subject. A real
guard accepted «La Camera di Commercio di Studio Rossi S.r.l. ha iscrizione n. …» on the operator's
field, with nothing to compare it to. This module reads the owner from the SOURCE text alone (bold
lead, table row, inline name, heading above) and never from the model's reason or label.

- verified: the line or its section names the fact's subject.
- mismatch: it names someone else: the proposal is rejected.
- ambiguous: it names several candidates, or homonyms with different tax codes: the proposal is
  suspended and the USER gets a targeted question. Nothing is matched by guesswork.
- unverifiable: no owner is written anywhere near the line and no other candidate competes:
  existing gates decide, as before. Most company records have a single subject.

A USER value is checked the same way: a message attributing it explicitly to another subject,
or to a personal address on a company seat, is refused. A correction naming the destination's
own subject, or carrying the new subject as the value itself, is not.
"""

from __future__ import annotations

import re
from collections import Counter
from copy import deepcopy

from app.compilation_role_records import _same_person, _text

REVISION = 1
LEGAL_FORM = (r"S\.?\s?r\.?\s?l\.?(?:s\.?)?|S\.?\s?p\.?\s?a\.?|S\.?\s?n\.?\s?c\.?|"
              r"S\.?\s?a\.?\s?s\.?|Soc\.?\s+Coop\.?|S\.?\s?c\.?\s?a\.?\s?r\.?\s?l\.?")
COMPANY = re.compile(r"((?:[A-ZÀ-Ý0-9][\w'’&-]*\s+){1,6})(?i:" + LEGAL_FORM + r")(?![\w])")
LEGAL_TAIL = re.compile(r"\s+(?:" + LEGAL_FORM + r")\s*$", re.IGNORECASE)
TITLE = r"(?:(?:Ing|Arch|Dott|Dott\.ssa|Dr|Geom|Avv|Prof|Sig|Sig\.ra)\.?\s+)"
PERSON = re.compile(r"(?:" + TITLE + r")?([A-ZÀ-Ý][a-zà-ÿ'’]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ'’]+){1,3})")
NOT_A_PERSON = re.compile(
    r"\b(?:camera|commercio|registro|imprese|partita|iva|ordine|albo|collegio|provincia|comune|"
    r"regione|via|piazza|corso|viale|sede|legale|società|studio|consorzio|direttore|tecnico|"
    r"amministratore|unico|rappresentante|responsabile|codice|fiscale|numero|data|nome|cognome|"
    r"ministero|tribunale|agenzia|entrate|italia|ingegneri|architetti|geometri|ruoli|dati)\b",
    re.IGNORECASE)
LEAD = re.compile(r"^\s*(?:[-*]\s+)?\*\*(?P<name>[^*]+?)(?::\*\*|\*\*\s*:)")
HEADING = re.compile(r"^\s*(?P<level>#{1,6})\s+(?P<text>.+)$")
TAX_CODE = re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b")
PERSONAL_PLACE = re.compile(
    r"\b(?:residenz\w*|residente|domicili\w*|abitazion\w*|casa\s+(?:mia|sua)|"
    r"studio\s+(?:personale|privato)|mio\s+studio)\b", re.IGNORECASE)
COMPANY_PLACE = re.compile(r"\bsede\s+(?:legale|operativa|sociale|della\s+società)\b",
                           re.IGNORECASE)
ATTRIBUTED = r"(?:di|del|della|dello|dell['’]|per|a\s+nome\s+di|intestat\w+\s+a)\s+"
# «di Reggio Emilia» after these nouns is a place or an institution, never a person.
PLACE_NOUN = re.compile(r"\b(?:comune|provincia|città|regione|camera|commercio|ordine|collegio|"
                        r"albo|tribunale|sede|via|piazza|agenzia|ministero|studio|società)\s*$",
                        re.IGNORECASE)


def enabled(data):
    return data.get("subject_check_revision") == REVISION


def company_key(name):
    words = re.findall(r"[^\W_]+", _text(LEGAL_TAIL.sub("", name or "")))
    return frozenset(w for w in words if w not in {"la", "il", "di", "e", "società"})


def same_company(a, b):
    left, right = company_key(a), company_key(b)
    return bool(left and right and (left <= right or right <= left))


def same_person(a, b):
    if not a or not b:
        return False
    plain = [re.sub(r"^" + TITLE, "", " ".join(x.split()), flags=re.IGNORECASE) for x in (a, b)]
    return _same_person(a, b) or sorted(_text(plain[0]).split()) == sorted(_text(plain[1]).split())


def same_subject(a, b, entity):
    return same_company(a, b) if entity == "company" else same_person(a, b)


def _person_like(text):
    match = PERSON.fullmatch(" ".join((text or "").split()))
    return bool(match) and not NOT_A_PERSON.search(match.group(1))


def known_subjects(audit):
    """Named subjects of this draft, from its facts and bindings; never from model reasons."""
    people, companies = set(), set()
    for fact in (audit.get("facts") or {}).values():
        subject = str(fact.get("subject") or "").strip()
        if not subject:
            continue
        if fact.get("entity") == "person":
            people.add(subject)
        elif fact.get("entity") == "company":
            companies.add(subject)
    return {"person": sorted(people), "company": sorted(companies)}


def named_in(text, known):
    """Names written in this text: legal-form companies, known subjects, name-shaped people."""
    found = {"person": [], "company": []}
    for match in COMPANY.finditer(text or ""):
        found["company"].append(" ".join(match.group(0).split()))
    lowered = _text(text or "")
    for company in known.get("company", []):
        core = _text(LEGAL_TAIL.sub("", company))
        if core and re.search(r"(?<!\w)" + re.escape(core) + r"(?!\w)", lowered) and not any(
                same_company(company, other) for other in found["company"]):
            found["company"].append(company)
    for person in known.get("person", []):
        bare = re.sub(r"^" + TITLE, "", person, flags=re.IGNORECASE)
        words = _text(bare).split()
        patterns = [" ".join(words), " ".join(reversed(words))]
        if len(words) >= 2 and any(re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", lowered)
                                   for p in patterns):
            found["person"].append(person)
    return found


def _line_of(lines, quote):
    wanted = _text(quote or "")
    for index, line in enumerate(lines):
        current = _text(line)
        if current and (wanted in current or current in wanted):
            return index
    return None


def _owners(lines, index, known):
    """The owner written for this line: its lead, its row, its text, then its headings."""
    line = lines[index]
    lead = LEAD.match(line)
    if lead:
        name = re.sub(r"\s+", " ", lead["name"]).strip()
        if COMPANY.search(name) or any(same_company(name, c) for c in known.get("company", [])):
            return {"person": [], "company": [name]}, "lead"
        if _person_like(name) or any(same_person(name, p) for p in known.get("person", [])):
            return {"person": [name], "company": []}, "lead"
    if line.lstrip().startswith("|"):
        found = named_in(line, known)
        first = next((c.strip() for c in line.strip().strip("|").split("|") if c.strip()), "")
        if not found["person"] and _person_like(first):
            found["person"].append(first)
        if found["person"] or found["company"]:
            return found, "table_row"
    found = named_in(line, known)
    if found["person"] or found["company"]:
        return found, "line"
    level = 7
    for above in range(index - 1, -1, -1):
        heading = HEADING.match(lines[above])
        if not heading or len(heading["level"]) >= level:
            continue
        level = len(heading["level"])
        text = re.sub(r"\s+[-–—].*$", "", heading["text"]).strip(" *")
        found = named_in(heading["text"], known)
        if not found["person"] and _person_like(text):
            found["person"].append(text)
        if found["person"] or found["company"]:
            return found, "heading"
    return {"person": [], "company": []}, None


def _homonyms(source_map, subject):
    """Records of the same name with different tax codes: two people, whatever the model said."""
    codes = set()
    for source in source_map.values():
        for line in source.get("content", "").splitlines():
            if same_name_on_line(line, subject):
                codes.update(TAX_CODE.findall(line))
    return len(codes) > 1


def same_name_on_line(line, subject):
    words = _text(re.sub(r"^" + TITLE, "", subject or "", flags=re.IGNORECASE)).split()
    return len(words) >= 2 and bool(re.search(
        r"(?<!\w)" + re.escape(" ".join(words)) + r"(?!\w)", _text(line)))


def evidence_owner(fact, source_map, known):
    """{result, owners, basis} for one fact: the SOURCE lines it cites decide, not its claim."""
    subject, entity = str(fact.get("subject") or ""), fact.get("entity")
    if entity not in {"person", "company"} or not subject:
        return {"result": "unverifiable", "owners": [], "basis": None}
    if same_subject(str(fact.get("value") or ""), subject, entity):
        return {"result": "verified", "owners": [subject], "basis": "value"}
    if entity == "person" and _homonyms(source_map, subject):
        return {"result": "ambiguous", "owners": [subject], "basis": "homonyms"}
    verdicts = []
    for proof in fact.get("source_evidence", []):
        source = source_map.get(proof.get("chunk_id"))
        if not source:
            continue
        lines = source.get("content", "").splitlines()
        index = _line_of(lines, proof.get("quote"))
        if index is None:
            continue
        owners, basis = _owners(lines, index, known)
        verdicts.append(_verdict(owners, basis, subject, entity))
    if any(v["result"] == "verified" for v in verdicts):
        return next(v for v in verdicts if v["result"] == "verified")
    for result in ("ambiguous", "mismatch"):
        if any(v["result"] == result for v in verdicts):
            return next(v for v in verdicts if v["result"] == result)
    return {"result": "unverifiable", "owners": [], "basis": None}


def _verdict(owners, basis, subject, entity):
    same = [o for o in owners[entity] if same_subject(o, subject, entity)]
    others = [o for o in owners[entity] if not same_subject(o, subject, entity)]
    if same and others and basis in {"line", "table_row"} and entity == "person":
        return {"result": "ambiguous", "owners": owners[entity], "basis": basis}
    if same:
        return {"result": "verified", "owners": same, "basis": basis}
    if others:
        return {"result": "mismatch", "owners": others, "basis": basis}
    # Another kind of owner: a person's own record is not a company's, and vice versa. A company
    # named in a heading or in a person's line says nothing against that person's data.
    other = "company" if entity == "person" else "person"
    if owners[other] and (basis == "lead" or (entity == "company" and basis == "heading")):
        return {"result": "mismatch", "owners": owners[other], "basis": basis}
    return {"result": "unverifiable", "owners": [], "basis": basis}


def _fact_of(field, facts):
    reuse = field.get("source_reuse") or {}
    proposal = field.get("proposal") or {}
    return reuse.get("fact") or facts.get(field.get("fact_id") or field.get("proposed_fact_id")
                                          or proposal.get("fact_id"), {})


def _documented(field):
    return (not field.get("validation_errors")
            and (field.get("validation") == "GROUNDED_PROPOSAL"
                 or field.get("proposal_grounding") == "GROUNDED_PROPOSAL"))


def _chain(candidate):
    return candidate.get("continuation_origin_paragraph_id") or candidate.get("context_id")


def _reject(field, reason, check):
    field.update(validation="REJECTED", value=None, fact_id=None, written_value=None,
                 subject_check=check)
    for key in ("proposal_grounding", "proposed_value", "proposed_fact_id"):
        field.pop(key, None)
    field["validation_errors"] = [*field.get("validation_errors", []), reason]
    field["coverage"] = {"state": "REJECTED_PROPOSAL", "origin": "BACKEND", "reason": reason}


def _suspend(field, reason, check):
    """No value leaves this field until the USER says whose it is: a targeted value question."""
    field.update(validation="REVIEW_REQUIRED", value=None, fact_id=None, written_value=None,
                 disposition="review", review_kind="subject_uncertain", subject_check=check)
    for key in ("proposal_grounding", "proposed_value", "proposed_fact_id"):
        field.pop(key, None)
    if isinstance(field.get("proposal"), dict):
        field["proposal"] = {k: v for k, v in field["proposal"].items() if k != "fact_id"}
    field["coverage"] = {"state": "CLARIFICATION", "origin": "BACKEND", "reason": reason}


def apply(data, audit, source_map):
    """Reject evidence of another subject, suspend the ambiguous; verified data stay untouched."""
    result = deepcopy(audit)
    if not enabled(data):
        return result
    facts, known = result.get("facts") or {}, known_subjects(result)
    candidates = (data.get("catalog") or {}).get("candidates", {})
    fields = {f["candidate_id"]: f for f in result.get("fields", [])}
    report = Counter()
    for cid, field in fields.items():
        if not _documented(field):
            continue
        fact = _fact_of(field, facts)
        check = evidence_owner(fact, source_map, known)
        field["subject_evidence"] = check
        report[check["result"]] += 1
        if check["result"] == "mismatch":
            _reject(field, f"L'evidenza SOURCE riguarda «{check['owners'][0]}», non "
                           f"«{fact.get('subject')}»", check)
        elif check["result"] == "ambiguous":
            shown = " e ".join(dict.fromkeys(check["owners"]))
            _suspend(field, f"Dalla SOURCE non si stabilisce a chi si riferisce il dato ({shown})",
                     {**check, "value": fact.get("value"),
                      "quote": (fact.get("source_evidence") or [{}])[0].get("quote", "")})
    # One FORM chain has one company owner: the data of another company do not fill it.
    chains = {}
    for cid, field in fields.items():
        fact = _fact_of(field, facts)
        if _documented(field) and fact.get("entity") == "company" and cid in candidates:
            chains.setdefault(_chain(candidates[cid]), []).append((cid, fact))
    for items in chains.values():
        owners = Counter()
        for _, fact in items:
            match = next((o for o in owners if same_company(o, fact.get("subject", ""))), None)
            owners[match or fact.get("subject", "")] += 1
        if len(owners) < 2:
            continue
        named = [f.get("subject") for _, f in items
                 if same_company(str(f.get("value") or ""), str(f.get("subject") or ""))]
        ranked = owners.most_common()
        owner = named[0] if named else (ranked[0][0] if ranked[0][1] > ranked[1][1] else None)
        for cid, fact in items:
            if owner is None:
                _suspend(fields[cid], "Il blocco del modulo riporta dati di società diverse",
                         {"result": "ambiguous", "owners": list(owners), "basis": "form_chain",
                          "value": fact.get("value"),
                          "quote": (fact.get("source_evidence") or [{}])[0].get("quote", "")})
                report["ambiguous"] += 1
            elif not same_company(owner, fact.get("subject", "")):
                _reject(fields[cid], f"Il dato riguarda «{fact.get('subject')}», ma il blocco del "
                                     f"modulo riguarda «{owner}»",
                        {"result": "mismatch", "owners": [fact.get("subject")],
                         "basis": "form_chain"})
                report["mismatch"] += 1
    result["subject_check"] = {"revision": REVISION, **report}
    return result


def destination_subject(data, cid):
    """Whose destination is this, from verified facts or USER values; None when not written."""
    from app.compilation_attribution import check_source_target

    audit = data.get("audit") or {}
    facts = audit.get("facts") or {}
    fields = {f["candidate_id"]: f for f in audit.get("fields", [])}
    catalog = data.get("catalog") or {}
    candidates = catalog.get("candidates", {})
    field = fields.get(cid, {})
    names = []
    fact = _fact_of(field, facts)
    if fact.get("subject"):
        names.append((fact["subject"], fact.get("entity")))
    for option in field.get("alternatives") or []:
        other = facts.get(option.get("fact_id"), {})
        if other.get("subject"):
            names.append((other["subject"], other.get("entity")))
    if not names and cid in candidates:
        chain = _chain(candidates[cid])
        for other_id, other in fields.items():
            other_fact = _fact_of(other, facts)
            if (other_id in candidates and _chain(candidates[other_id]) == chain
                    and _documented(other) and other_fact.get("subject")):
                names.append((other_fact["subject"], other_fact.get("entity")))
    entity = None
    if cid in candidates:
        try:
            entity = check_source_target(cid, catalog, {"entity": None}).get("expected_entity")
        except (KeyError, ValueError):
            entity = None
    entity = entity or (names[0][1] if names else None)
    same_kind = [n for n, e in names if e == entity] or [n for n, _ in names]
    unique = []
    for name in same_kind:
        if not any(same_subject(name, u, entity) for u in unique):
            unique.append(name)
    return {"name": unique[0] if len(unique) == 1 else None, "entity": entity,
            "candidates": unique} if (unique or entity) else None


def form_prefix(data, cid):
    catalog = data.get("catalog") or {}
    candidate = (catalog.get("candidates") or {}).get(cid) or {}
    return str((candidate.get("slot_context") or {}).get("before") or "")


def slot_context(data, field_ids):
    """What the guard and the deterministic check compare a USER value to; no digest involved."""
    if len(field_ids) != 1:
        return None
    audit = data.get("audit") or {}
    expected = destination_subject(data, field_ids[0])
    users = (data.get("dialogue") or {}).get("user_values") or {}
    registered = [str(v.get("value")) for v in users.values() if v.get("value")]
    known = known_subjects(audit)
    prefix = form_prefix(data, field_ids[0])
    return {"expected": expected, "known": known, "user_values": registered,
            "form_scope": ("company_seat" if re.search(r"\bsede\b", prefix, re.I)
                           and not PERSONAL_PLACE.search(prefix) else
                           "personal_place" if PERSONAL_PLACE.search(prefix) else None)}


def foreign_reply(text, value, check):
    """Refuse only what the message states: {code, named, expected} or None.

    The value itself never counts as a foreign name (a corrected name or denomination is the
    destination's own subject); naming the expected subject too leaves the decision to the guard.
    """
    if not check:
        return None
    expected = check.get("expected") or {}
    entity, name = expected.get("entity"), expected.get("name")
    candidates = expected.get("candidates") or ([name] if name else [])
    rest = text or ""
    if value:
        rest = re.sub(re.escape(str(value)), " ", rest, flags=re.IGNORECASE)
    place = check.get("form_scope")
    if place == "company_seat" and PERSONAL_PLACE.search(rest) and not COMPANY_PLACE.search(rest):
        return {"code": "place", "named": PERSONAL_PLACE.search(rest).group(0),
                "expected": "la sede dell'operatore"}
    if place == "personal_place" and COMPANY_PLACE.search(rest) and not PERSONAL_PLACE.search(rest):
        return {"code": "place", "named": COMPANY_PLACE.search(rest).group(0),
                "expected": "il luogo personale chiesto dal modulo"}
    if not candidates or not entity:
        return None
    found = named_in(rest, check.get("known") or {})
    allowed = [*candidates, *(check.get("user_values") or [])]
    if any(same_subject(n, a, entity) for n in found[entity] for a in allowed):
        return None
    # An explicit attribution only: a role of the company, or a reference to the expected one,
    # is not a foreign owner. Name-shaped unknown people are left to the guard.
    foreign = [n for n in found[entity] if not any(same_subject(n, a, entity) for a in allowed)]
    attributed = [n for n in foreign if re.search(
        ATTRIBUTED + r"(?:\w+\.\s+)?" + re.escape(n), rest, re.IGNORECASE)
        or re.search(re.escape(n) + r"\s*(?:ha|:)", rest, re.IGNORECASE)]
    if attributed:
        return {"code": "subject", "named": attributed[0], "expected": candidates[0]}
    other = "person" if entity == "company" else "company"
    if entity == "company":
        crossed = [n for n in found[other] if re.search(
            ATTRIBUTED + re.escape(n), rest, re.IGNORECASE)]
        if crossed:
            return {"code": "subject", "named": crossed[0], "expected": candidates[0]}
    # A person the sources never mention, explicitly named as the owner of the value. The real
    # guard accepted «Il codice fiscale di Mario Bianchi è …» on a director's field.
    companies = (check.get("known") or {}).get("company", [])
    for match in re.finditer(ATTRIBUTED + PERSON.pattern, rest):
        name = match.group(1)
        if (not PLACE_NOUN.search(rest[:match.start()]) and _person_like(name)
                and not any(same_person(name, a) for a in allowed)
                and not any(same_company(name, c) for c in companies)):
            return {"code": "subject", "named": name, "expected": candidates[0]}
    return None


FOREIGN_TEXT = {
    "subject": "il messaggio riferisce il dato a «{named}», ma il campo riguarda «{expected}»",
    "place": "il messaggio parla di «{named}», ma il campo riguarda {expected}",
}


def foreign_text(found):
    return FOREIGN_TEXT[found["code"]].format(**found)
