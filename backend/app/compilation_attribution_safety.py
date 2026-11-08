"""Organization check on grounded personal-role proposals (new sessions only).

A named SOURCE attestation ("- **P:** R di X", or the bold V13 form) binds the
role to organization X. An explicit X must be a company that the draft itself
grounds, or a bare generic self reference; otherwise the personal proposal
loses its grounding. Unrecognized phrasing is left to the existing gates.
This can only remove grounding, and a USER receipt never lifts the block.
The identifier-class and closed attestation-consistency checks were measured
and excluded (preregistered evaluation, 21 October 2026).
"""

import re
from copy import deepcopy

from app.compilation_global import _role_text
from app.compilation_role_records import _same_person, _text, _uncertain

REVISION = 1
NAMED = re.compile(r"\s*[-*]\s+\*\*(?P<name>[^*]+?)(?::\*\*|\*\*:)\s*(?P<rest>.+)")
# An abbreviation dot (S.r.l.) continues the name; a dot before a space ends it.
OWNER = (r"(?:\s+(?:di|del|della|dello|presso)\s+|\s+dell['’]\s*)"
         r"(?P<owner>(?:[^;,.*]|\.(?=[^\s*]))+)")
# Same generic company nouns as compilation_attribution.COMPANY: a self reference.
GENERIC_OWNER = re.compile(r"(?:la\s+|l['’]\s*)?(?:società|impresa|azienda|operatore\s+economico)"
                           r"(?!\w)", re.IGNORECASE)
# Closed grammatical class: prepositions, articulated forms and relative 'che'.
PREPOSITION = (r"(?:di|a|da|in|con|su|per|tra|fra|che|nel\w*|nell['’]|dal\w*|dall['’]|al\w*|"
               r"all['’]|del\w*|dell['’]|sul\w*|sull['’])(?!\w)")
REASON = "Attestazione del ruolo per un'organizzazione diversa da quella della bozza"


def _grounded(field):
    return (field.get("validation") == "GROUNDED_PROPOSAL"
            or field.get("proposal_grounding") == "GROUNDED_PROPOSAL")


def _norm(value):
    return re.sub(r"\W", "", _text(value))


def own_organization(raw, operators):
    """A grounded company of this draft, or a bare generic self reference
    optionally followed by a prepositional phrase without proper names."""
    raw = raw.strip()
    generic = GENERIC_OWNER.match(raw)
    if generic:
        tail = raw[generic.end():]
        capitalized = any(word[:1].isupper() for word in tail.split())
        if not tail.strip() or (re.match(r"\s+" + PREPOSITION, tail, re.IGNORECASE)
                                and not capitalized):
            return True
        raw = tail if capitalized else raw
    named = _norm(raw)
    return len(named) >= 4 and any(named.startswith(o) or o.startswith(named) for o in operators)


def foreign_attestations(source_map, subject, role, operators):
    """Certain named attestations of this person and role at another organization."""
    role_raw = r"\s+".join(map(re.escape, _role_text(role).split()))
    found = []
    for chunk in sorted(source_map):
        source = source_map[chunk]
        if source.get("category") == "general":
            continue
        for line in source["content"].splitlines():
            named = NAMED.fullmatch(line)
            if not named or not _same_person(named["name"].strip(), subject):
                continue
            rest = named["rest"].strip()
            if rest.startswith("**") and "**" in rest[2:]:
                bold, after = rest[2:].split("**", 1)
                shape = re.match(role_raw + r"(?!\w)(?:" + OWNER + r")?", bold.strip(),
                                 re.IGNORECASE)
                certain = not _uncertain(bold) and not _uncertain(after.split(".", 1)[0])
            elif "**" not in rest:
                shape = re.match(role_raw + r"(?:\s*(?:$|[;,.])|" + OWNER + r"\s*(?:$|[;,.]))",
                                 rest, re.IGNORECASE)
                certain = not _uncertain(line)
            else:
                continue
            if (shape and certain and shape["owner"]
                    and not own_organization(shape["owner"], operators)):
                found.append({"chunk_id": chunk, "line": line.strip()[:300],
                              "organization": shape["owner"].strip()})
    return found


def apply_attribution_safety(audit, source_map):
    """Return (audit, blocked); blocked maps candidate ids to the foreign attestations."""
    result = deepcopy(audit)
    facts = result.get("facts") or {}
    bindings = result.get("bindings") or {}

    def fact_of(field):
        proposal = field.get("proposal") or {}
        return facts.get(field.get("fact_id") or field.get("proposed_fact_id")
                         or proposal.get("fact_id"), {})

    operators = {_norm(fact_of(f).get("subject", "")) for f in result.get("fields", [])
                 if _grounded(f) and fact_of(f).get("entity") == "company"} - {""}
    blocked = {}
    for field in result.get("fields", []):
        reuse = field.get("source_reuse") or {}
        fact = reuse.get("fact") or fact_of(field)
        if not _grounded(field) or fact.get("entity") != "person":
            continue
        if reuse.get("property") == "role":
            role, subject = field.get("proposed_value", field.get("value")), reuse.get("subject")
        elif (field.get("subject_binding") or {}).get("result") == "literal_match":
            binding = bindings.get(field["subject_binding"].get("binding_id"), {})
            role, subject = binding.get("source_role"), fact.get("subject")
        else:
            continue
        if not isinstance(role, str) or not role or not subject:
            continue
        foreign = foreign_attestations(source_map, subject, role, operators)
        if not foreign:
            continue
        field.update(validation="REJECTED", value=None, fact_id=None, written_value=None)
        for key in ("proposal_grounding", "proposed_value", "proposed_fact_id"):
            field.pop(key, None)
        field["validation_errors"] = [*field.get("validation_errors", []), REASON]
        field["attribution_safety"] = {"revision": REVISION, "role": role, "subject": subject,
                                       "foreign_attestations": foreign}
        field["coverage"] = {"state": "REJECTED_PROPOSAL", "origin": "BACKEND", "reason": REASON}
        blocked[field["candidate_id"]] = foreign
    if blocked:
        result["attribution_safety"] = {"revision": REVISION, "blocked": sorted(blocked)}
    return result, blocked
