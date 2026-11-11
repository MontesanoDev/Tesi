"""Necessary local FORM predicates, independent of MODEL conditions and assent.

Bounded Italian equality/difference grammar in a marked clause or a two-cell
label/value row. SOURCE assertions must explicitly name the same subject.
Identical literal scalar values prove equality; differing spellings never prove
inequality. Unsupported comparisons, missing operands and conflicts stay UNKNOWN.
This is an export veto, not factual grounding, a USER decision or a FORM view.
"""

import hashlib
import re
import unicodedata

MARKER = re.compile(r"\[\[([^\[\]]+)\]\]")
TRIGGER = re.compile(r"\b(?:se|qualora|quando)\b", re.I)
COMPARATIVE = re.compile(
    r"\b(?:divers\w*|differ\w*|distint\w*|ugual\w*|identic\w*|coincident\w*)\b")
RELATION = re.compile(
    r"(?P<negative>non\s+)?(?:(?:e|sia|risulta)\s+)?"
    r"(?P<operator>divers[oaie]|different[ei]|distint[oaie]|ugual[ei]|identic[oaie]|coincident[ei])"
    r"\s+(?:rispetto\s+)?(?:dall['’]|all['’]|dalla|dallo|dalle|dai|dal|da|"
    r"alla|allo|alle|al|ad|a|con)\s*(?P<reference>.+)")
UNCERTAIN = re.compile(
    r"\b(?:non|nessun\w*|senza|forse|ipotetic\w*|esempio|eventual\w*|"
    r"potrebbe|sarebbe|ignot\w*|sconosciut\w*|assente|mancante|confermare)\b")


def _text(value):
    text = unicodedata.normalize("NFKD", value).casefold()
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def _label(value):
    value = re.sub(r"\([^()]*\)", "", value)
    value = _text(value).strip(" :,.()[]\"'“”")
    return re.sub(r"^(?:(?:la|il|lo|le|i|gli)\s+|l['’])", "", value)


def _relation(value):
    match = RELATION.fullmatch(_text(value).strip(" .()"))
    if not match:
        return None
    operator = ("different" if match["operator"].startswith(("divers", "differ", "distint"))
                else "same")
    if match["negative"]:
        operator = "same" if operator == "different" else "different"
    return {"operator": operator, "reference": _label(match["reference"])}


def _contexts(cid, candidate, catalog, paragraphs):
    """No inheritance across rows, tables, cells with merges or body paragraphs."""
    result = []
    location = candidate["location"]
    for block in catalog["blocks"]:
        for table in block.get("tables", []):
            if table["id"] != location.get("table_id"):
                continue
            row = table["rows"][location["row_index"]]
            if (len(row) != 2
                    or candidate["context_id"] not in [row[1]["id"], *row[1]["paragraph_ids"]]
                    or any(c["context_id"] in [row[0]["id"], *row[0]["paragraph_ids"]]
                           for c in catalog["candidates"].values())):
                continue
            proofs = [{"paragraph_id": p, "quote": paragraphs[p]["text"], "role": "form"}
                      for p in row[0]["paragraph_ids"] if paragraphs[p]["text"].strip()]
            result.append({"text": " ".join(p["quote"] for p in proofs),
                           "ambiguous_structure": any(c.get("table_ids") or "vertical_merge" in c
                                                      for c in row),
                           "form_evidence": proofs, "anchor": {"kind": "label_value_row",
                               "table_id": table["id"], "label_cell_id": row[0]["id"],
                               "target_cell_id": row[1]["id"]}})
    edge = catalog.get("_table_form_links", {}).get(cid, {})
    if not result and edge.get("result") == "structural_match":
        proofs = edge["form_evidence"]
        result.append({"text": " ".join(p["quote"] for p in proofs),
                       "form_evidence": proofs, "anchor": edge})
    paragraph = paragraphs.get(candidate["context_id"])
    if paragraph:
        marked = paragraph.get("text_with_fields", "")
        clauses = re.split(r"[;\n]|(?<=[.!?])\s+(?=[A-ZÀ-Ý])", marked)
        for index, clause in enumerate(clauses):
            if f"[[{cid}]]" in clause:
                context = {"text": clause, "form_evidence": [{
                    "paragraph_id": paragraph["id"], "quote": paragraph["text"], "role": "form"}],
                    "anchor": {"kind": "marked_clause", "candidate_id": cid, "clause": clause}}
                if re.match(r"\s*altrimenti\b", clause, re.I):
                    # Only an immediately preceding clause in this same physical
                    # paragraph can introduce the complementary branch. No guessed scope.
                    context["alternative_of"] = clauses[index - 1] if index else ""
                result.append(context)
    return result


def requirements(catalog):
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    result = {}
    for cid, candidate in catalog["candidates"].items():
        if candidate.get("type") != "text":
            continue
        found = []
        for context in _contexts(cid, candidate, catalog, paragraphs):
            text = context.get("alternative_of", context["text"])
            triggers = list(TRIGGER.finditer(text))
            if not triggers or not COMPARATIVE.search(_text(text[triggers[0].end():])):
                if "alternative_of" in context:
                    found.append({**context, "predicate": None})
                continue
            predicate = None
            if (len(triggers) == 1 and len(MARKER.findall(text)) <= 1
                    and not context.get("ambiguous_structure")):
                trigger = triggers[0]
                left = MARKER.sub("", text[:trigger.start()]).rstrip(" ([,:")
                left = re.sub(r"\b(?:(?:compilare|indicare)\s+)?(?:solo|soltanto)$", "", left,
                              flags=re.I).strip()
                condition = MARKER.split(text[trigger.end():])[0].split(")")[0].strip(" :,")
                # An explicit subject inside the predicate must be this label.
                normalized = _text(condition)
                prefix = _text(left)
                for article in ["", "la ", "il ", "lo "]:
                    if prefix and normalized.startswith(article + prefix + " "):
                        condition = normalized[len(article + prefix):].strip()
                        break
                relation = _relation(condition)
                if left and relation:
                    predicate = {"left": _label(left), "operator": relation["operator"],
                                 "right": relation["reference"]}
                    if "alternative_of" in context:
                        predicate["operator"] = ("same" if predicate["operator"] == "different"
                                                 else "different")
            found.append({**context, "predicate": predicate})
        if found:
            result[cid] = found
    return result


def _assertions(label, other, subject, sources):
    values, relations, proofs = set(), set(), []
    keys = {_text(label + joiner + subject).rstrip(" .")
            for joiner in [" di ", " della ", " dello ", " dell'", " dell’"]}
    for source in sources.values():
        unsafe_heading = unsafe_prefix = fenced = False
        for line in source["content"].splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                fenced = not fenced
            if re.match(r"^#{1,6}\s", stripped):
                unsafe_heading = bool(UNCERTAIN.search(_text(stripped))
                                      or TRIGGER.search(stripped))
                unsafe_prefix = False
            elif not stripped:
                unsafe_prefix = False
            elif stripped.endswith(":") and (UNCERTAIN.search(_text(stripped))
                                               or TRIGGER.search(stripped)):
                unsafe_prefix = True
            if unsafe_heading or unsafe_prefix or fenced:
                continue
            key, separator, value = line.lstrip(" -*•\t").partition(":")
            if not separator or _text(key).rstrip(" .") not in keys:
                continue
            value = value.strip()
            relation = _relation(value)
            if relation:
                if relation["reference"] != other:
                    continue
                relations.add(relation["operator"])
            elif (not value or UNCERTAIN.search(_text(value)) or COMPARATIVE.search(_text(value))
                  or re.search(r"\b(?:se|qualora|quando)\b", _text(value))):
                continue
            else:
                values.add(_text(value).strip(" ."))
            proofs.append({**{k: source[k] for k in ["chunk_id", "file_id", "chunk_index",
                "source_name", "role", "scope", "project_id", "category"]}, "quote": line.strip(),
                "content_sha256": hashlib.sha256(source["content"].encode()).hexdigest()})
    return values, relations, proofs


def evaluate(audit, catalog, sources):
    """Do not change the raw proposal, facts, MODEL conditions or their results."""
    fields = {f["candidate_id"]: f for f in audit["fields"]}
    result = {}
    for cid, contexts in requirements(catalog).items():
        field = fields.get(cid, {})
        proposal = field.get("proposal") or {}
        fact_id = field.get("fact_id") or field.get("proposed_fact_id") or proposal.get("fact_id")
        fact = audit.get("facts", {}).get(fact_id, {})
        check = {"result": "unknown", "contexts": contexts, "source_evidence": [],
                 "basis": "not_demonstrated", "subject": fact.get("subject"),
                 "MODEL_conditions_used": False, "USER_authorization_used": False}
        result[cid] = check
        if len(contexts) != 1 or not contexts[0]["predicate"]:
            continue
        if fact.get("validation") != "GROUNDED_PROPOSAL" or not fact.get("subject"):
            continue
        predicate = contexts[0]["predicate"]
        left, right = predicate["left"], predicate["right"]
        lv, lr, lp = _assertions(left, right, fact["subject"], sources)
        rv, rr, rp = _assertions(right, left, fact["subject"], sources)
        check["source_evidence"] = lp + [p for p in rp if p not in lp]
        assertions = lr | rr
        if len(lv) > 1 or len(rv) > 1:
            check["basis"] = "conflicting_source_values"
            continue
        if lv and lv == rv:
            assertions.add("same")
        if len(assertions) != 1:
            if assertions:
                check["basis"] = "conflicting_source_relations"
            continue
        relation = next(iter(assertions))
        check.update(result="true" if predicate["operator"] == relation else "false",
                     basis="explicit_source_relation" if lr or rr else "identical_source_values")
    return result


def blocked_fields(data):
    """Private export and public chat both keep the veto; legacy V12 needs reanalysis.

Absent evidence is UNKNOWN, including older persisted V12 audits that have not
run this validator. No upgrade/mutation of a persisted session takes place here.
"""
    if "audit" not in data:
        return {f["candidate_id"] for f in data.get("fields", [])
                if f.get("form_applicability", {}).get("result", "true") != "true"}
    audit = data.get("audit") or {}
    if audit.get("version") != 12:
        return set()
    return {cid for cid in set(requirements(data["catalog"])) | set(
                audit.get("form_applicability", {}))
            if audit.get("form_applicability", {}).get(cid, {}).get("result") != "true"}
