"""Small, conservative algebra of predicates already anchored and verified in FORM.

The subject of a branch is independent from the subject of a writable cell.
No legal form implies another legal form or a participation arrangement.
"""

import re

from app.compilation_applicability import known_applicability, predicate
from app.requirement_checks import contains_form_span


def expression(condition):
    """Conjunction of an explicit parent and an explicit presence/absence qualifier.

    Unknown syntax stays opaque. In particular, neither disjunction nor arbitrary
    occurrences of 'e' are split. An apposition needs the same final modifier
    and no negation/qualifier; arbitrary parenthetical explanations stay opaque.
    """
    text = predicate(condition).rstrip(" .")
    if re.search(r"\b(?:oppure|ovvero|o)\b", text):
        return frozenset({(text, True)})
    parts = re.split(r"\s+(nel caso di|in presenza di|in assenza di)\s+", text, maxsplit=1)
    root = parts[0]
    alias = re.fullmatch(r"([^()]+)\s+\(([^()]+)\)", root)
    if alias:
        def modifier(s):
            word = re.findall(r"\w+", s)[-1]
            return word[:-1] if len(word) >= 5 and word[-1] in "aeio" else word

        if modifier(alias[1]) == modifier(alias[2]) and not re.search(
            r"\b(?:non|senza|con|se|quando|oppure|ovvero|o)\b", root,
        ):
            root = alias[2]
    atoms = {(root.strip(), True)}
    if len(parts) == 3:
        atoms.add((parts[2].rstrip(" ."), parts[1] != "in assenza di"))
    return frozenset(atoms)


def owner(field):
    """Cross-section scope requires the reviewed, unchanged operator branch anchor."""
    from app.compilation_form_conditions import dependency_owner
    from app.compilation_semantics import interpretation_digest

    if dependency := dependency_owner(field):
        return dependency
    semantic = field.get("semantic") or {}
    verdict = field.get("semantic_validation") or {}
    section = next((s["text"] for s in field.get("structural", {}).get("form_sections", [])
                    if s["id"] == semantic.get("section_id")), "")
    header = re.search(r"(?:^|\))\s*dati identificativi da compilare in caso di\s+(.+)",
                       predicate(section))
    if (header and semantic.get("condition_kind") == "subject_type"
            and verdict.get("accepted") and verdict.get("condition_complete")
            and verdict.get("digest") == interpretation_digest(
                field.get("requirement"), semantic, field.get("entity"), field.get("condition"))
            and contains_form_span(header[1], field.get("condition", ""))):
        form = field["form_evidence"]
        return ("operator", form.get("project_id"), form.get("file_id"),
                form["template_sha256"])
    # Local predicates about a representative, consortium member, past service,
    # etc. retain their own entity, role and structural scope.
    if semantic.get("section_id") and verdict.get("accepted"):
        scope = (field["form_evidence"]["template_sha256"], semantic["section_id"])
    else:
        scope = field["context"]
    return ("local", field.get("entity"),
            predicate((field.get("requirement") or {}).get("person_role", "")), scope)


def key(field):
    return (owner(field), tuple(sorted(expression(field.get("condition", "")))))


def proven_relations(fields):
    """Return established predicates, never turn a field value into a decision."""
    facts = {}
    candidates = list(fields)
    candidates.extend({**f, "condition": f["form_dependency_user"]["condition"],
                       "applicability": f["form_dependency_user"]}
                      for f in fields if f.get("form_dependency_user"))
    # A verified explicit USER denial of the parent proves more than a generic
    # 'no' to a qualified branch. Retain the stored decision, derive only the
    # predicate actually denied in its quote; no SOURCE absence/type assumption.
    from app.compilation_applicability import explicit_condition_reply
    from app.compilation_form_conditions import root_condition

    for f in list(candidates):
        proof = f.get("applicability") or {}
        terms = expression(f.get("condition", ""))
        root = expression(root_condition(f.get("condition", "")))
        quote = proof.get("user_quote") or proof.get("reason", "").removeprefix(
            "Indicazione USER:").strip()
        if (proof.get("provenance") == "USER" and known_applicability(f) is False
                and len(root) == 1 and root < terms):
            parent, _ = next(iter(root))
            if (not explicit_condition_reply("", quote, applies=False)
                    and explicit_condition_reply(parent, quote, applies=False)):
                candidates.append({**f, "condition": parent, "applicability": {
                    **proof, "condition": parent, "dependency_rule": "explicit_USER_parent_denial",
                }})
    for f in candidates:
        proof = f.get("applicability") or {}
        evidence = proof.get("evidence") or []
        grounded = bool(proof.get("user_quote") or proof.get("reason")) if (
            proof.get("provenance") == "USER"
        ) else bool(evidence) and all(e.get("role") == "source" and e.get("quote")
                                     for e in evidence)
        if (f.get("condition") and f.get("applicability")
                and f["applicability"].get("provenance") in {"USER", "SOURCE"}
                and grounded
                and known_applicability(f) is not None):
            fact = (owner(f), expression(f["condition"]), known_applicability(f))
            facts.setdefault(fact, (*fact, f))
    return list(facts.values())


def conflicting_relations(field, facts):
    target, subject = expression(field["condition"]), owner(field)
    local = [(terms, applies, origin) for scope, terms, applies, origin in facts
             if scope == subject]
    for terms, applies, _ in local:
        for other, other_applies, _ in local:
            contradictory = (applies and not other_applies and other <= terms) or (
                applies and other_applies
                and any((atom, not polarity) in other for atom, polarity in terms)
            )
            if contradictory and (target & terms or target & other):
                return True
    return False


def implication(field, facts):
    if conflicting_relations(field, facts):
        return None
    target, subject = expression(field["condition"]), owner(field)
    local = [(terms, applies, origin) for scope, terms, applies, origin in facts
             if scope == subject]
    positive, negative = [], []
    for terms, applies, origin in local:
        if applies and target <= terms:
            positive.append(origin)
        elif not applies and terms <= target:
            negative.append(origin)
        elif applies and any((atom, not polarity) in terms for atom, polarity in target):
            negative.append(origin)
    # Contradictory verified decisions must not decide an unresolved dependency.
    if bool(positive) == bool(negative):
        return None
    return (bool(positive), (positive or negative)[0])


def negative_parent_reply(condition, message):
    """A literal denial of the explicit parent also denies its conjunction."""
    from app.compilation_applicability import explicit_condition_reply

    terms = expression(condition)
    return any(polarity and explicit_condition_reply(atom, message, applies=False)
               for atom, polarity in terms)
