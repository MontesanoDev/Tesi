"""Necessary completeness of a value, independent of factual/role/USER verdicts.

Bounded FORM grammars and existing physical edges. Never compose values, change
SOURCE spans, infer missing facts or promote MODEL conditions. Unsupported
requirements/records stay UNKNOWN; a literal partial fact stays a true fact.
"""

import re
import unicodedata

from app.compilation_role_records import _date, _person
from app.compilation_sources import source_span

MARKER = re.compile(r"\[\[([^\[\]]+)\]\]")
MONTHS = ("gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|"
          "ottobre|novembre|dicembre")
DATES = re.compile(r"(?<!\w)(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/.-]\d{1,2}[/.-]\d{4}|"
                   r"\d{1,2}\s+(?:" + MONTHS + r")\s+\d{4})(?!\w)", re.I)
NUMBER = re.compile(r"(?<!\w)(?:[A-Z]{1,5}[-/]?)?\d[\w/-]*(?!\w)", re.I)
STREET = re.compile(r"\b(?:via|viale|piazza|corso|largo|vicolo|localit[aà])\s+[^,;\n]+", re.I)
PLACE = re.compile(r"[^\W\d_][^\W\d_ .’'-]*(?:\s+[^\W\d_][^\W\d_ .’'-]*)*"
                   r"(?:\s*\([A-Z]{2}\))?", re.I)


def _text(value):
    text = unicodedata.normalize("NFKD", value).casefold().replace("’", "'")
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def _requirement(text):
    """Only named property combinations; punctuation alone never defines AND."""
    t = _text(text)
    join = r"\s*(?P<join>e|ed|o|oppure|/|\+)\s*"
    optional_date = bool(re.search(r"data\s+(?:facoltativa|opzionale|se disponibile)", t))
    pair = re.search(r"\bnumero" + join + r"(?P<second>data|anno)\b", t)
    reverse = re.search(r"\bdata" + join + r"numero\b", t)
    kind, required, mode = None, [], "all"
    if pair or reverse:
        match = pair or reverse
        second = pair["second"] if pair else "data"
        kind = "registration"
        required = ["number", "year" if second == "anno" else "date"]
        if re.search(r"\bordine\s*[-–—:]\s*data\s+e\s+numero", t):
            required.insert(0, "register")
        mode = {"o": "any", "oppure": "any", "/": "ambiguous", "+": "ambiguous"}.get(
            match["join"], "all")
        if optional_date:
            required = [c for c in required if c != "date"]
        for name, word in [("section", "sezione"), ("class", "classe")]:
            if re.search(r"\b" + word + r"\b", t) and not re.search(
                    word + r"\s+(?:facoltativa|opzionale|se disponibile)", t):
                required.append(name)
    elif re.search(r"\b(?:luogo\s+e\s+data|data\s+e\s+luogo)\b", t):
        kind = "birth" if "nascita" in t else "procedure_place_date"
        required = ["place", "date"]
    elif re.search(r"\bnome\s+e\s+cognome\b", t):
        kind, required = "person_identity", ["full_name"]
    elif re.search(r"\bqualifica\s+e\s+generalita\b", t):
        kind, required, mode = "open_description", ["qualification", "generalities"], "unknown"
    elif re.search(r"\b(?:cellulare\s*[+e/]\s*telefono|telefono\s*[+e/]\s*cellulare)\b", t):
        kind, required, mode = "contacts", ["mobile", "telephone"], "ambiguous"
        if re.search(r"\b(?:cellulare\s+e\s+telefono|telefono\s+e\s+cellulare)\b|"
                     r"\bentrambi\s+obbligatori\b", t):
            mode = "all"
    elif re.search(r"\boggetto\b.+\b(?:e|ed)\s+data\b", t):
        kind, required = "contract", ["description", "date"]
    elif "procura" in t and all(w in t for w in ["notaio", "repertorio", "raccolta"]):
        kind, required = "power_of_attorney", ["notary", "repertory", "collection"]
    elif re.search(r"\b(?:sede|indirizzo)\b", t):
        explicit = re.search(r"\(([^()]*)\)", t)
        components = explicit[1] if explicit else ""
        names = [("street", r"\b(?:via|piazza|strada)\b"),
                 ("place", r"\b(?:citta|comune|localita)\b"),
                 ("province", r"\bprov(?:incia)?\b"), ("postal_code", r"\bcap\b"),
                 ("civic_number", r"\b(?:civico|numero)\b")]
        required = [name for name, pattern in names if re.search(pattern, components)]
        if len(required) >= 2:
            kind = "address"
    if kind is None:
        return None
    return {"kind": kind, "required_components": required, "mode": mode,
            "SOURCE_required": kind != "procedure_place_date"}


def requirements(catalog):
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    result, fallback = {}, None
    for cid, candidate in catalog["candidates"].items():
        if candidate.get("type") != "text":
            continue
        edge = catalog.get("_table_form_links", {}).get(cid)
        proofs, context = [], ""
        if edge is not None:
            if edge["result"] != "structural_match":
                continue
            proofs = edge["form_evidence"]
            context = " ".join(p["quote"] for p in proofs)
        elif "range" in candidate:
            p = paragraphs[candidate["context_id"]]
            marked = p.get("text_with_fields", "")
            marker = f"[[{cid}]]"
            if marked.count(marker) != 1:
                continue
            before, after = marked.split(marker)
            context = MARKER.split(before)[-1]
            # A compound introduction followed by adjacent distinct slots is
            # a group of destinations, not two required values in its first slot.
            if MARKER.match(after.lstrip()) and _requirement(context):
                continue
            proofs = [{"paragraph_id": p["id"], "quote": p["text"], "role": "form"}]
        else:
            # Old V12 caches lack the backend edges/check. This fallback only
            # identifies positions needing reanalysis; it never certifies COMPLETE.
            if fallback is None:
                from app.compilation_global import _form_bindings

                fallback = _form_bindings(catalog)[1]
            ids = fallback.get(candidate["context_id"], [])
            proofs = [{"paragraph_id": p, "quote": paragraphs[p]["text"], "role": "form"}
                      for p in sorted(ids) if paragraphs[p]["text"].strip()]
            context = " ".join(p["quote"] for p in proofs)
        spec = _requirement(context)
        if spec:
            result[cid] = {**spec, "FORM_context": context, "form_evidence": proofs,
                           "candidate_id": cid, "template_sha256": catalog["template_sha256"]}
    return result


def _date_spans(value):
    result = []
    for m in DATES.finditer(value):
        literal = m.group()
        normalized = re.sub(r"[.-]", "/", literal) if re.match(r"\d{1,2}[.-]", literal) else literal
        parsed = _date(normalized)
        if parsed:
            result.append({"value": literal, "canonical": parsed.isoformat(),
                           "range": list(m.span())})
    return result


def _components(spec, value, subject):
    found = {}
    dates = _date_spans(value)
    if dates and len({d["canonical"] for d in dates}) == 1:
        found["date"] = dates[0]
    remaining = value
    for d in reversed(dates):
        a, b = d["range"]
        remaining = remaining[:a] + " " * (b - a) + remaining[b:]
    if "year" in spec["required_components"]:
        years = list(re.finditer(r"(?<!\w)(?:19|20)\d{2}(?!\w)", remaining))
        if len(years) == 1:
            m = years[0]
            found["year"] = {"value": m.group(), "range": list(m.span())}
            remaining = remaining[:m.start()] + " " * len(m.group()) + remaining[m.end():]
        elif len(dates) == 1:
            found["year"] = {"value": dates[0]["canonical"][:4],
                             "canonical": dates[0]["canonical"][:4]}
    explicit = list(re.finditer(r"\b(?:n(?:umero)?[.°º]?|num[.])\s*[:=]?\s*"
                               r"([A-Z]{0,5}[-/]?\d[\w/-]*)", remaining, re.I))
    numbers = [(m[1], m.span(1)) for m in explicit] or [
        (m.group(), m.span()) for m in NUMBER.finditer(remaining)]
    if len(numbers) == 1:
        found["number"] = {"value": numbers[0][0], "range": list(numbers[0][1])}
    kind = spec["kind"]
    if (kind == "person_identity" and subject and len(subject.split()) >= 2
            and _person(value, subject)):
        found["full_name"] = {"value": value, "range": [0, len(value)]}
    if kind in {"birth", "procedure_place_date"} and len(dates) == 1:
        a, b = dates[0]["range"]
        for start, part in [(0, value[:a]), (b, value[b:])]:
            part = re.sub(r"^(?:nato/a|nato|nata|a|il|luogo|data)\b\s*", "", part.strip(" ,:;-"),
                          flags=re.I)
            part = re.sub(r"\s+il$", "", part).strip(" ,:;-")
            if part and PLACE.fullmatch(part) and not re.search(
                    r"\b(?:residente|residenza|iscritto|numero|sede|nata|nato)\b", part, re.I):
                pos = value.find(part, start)
                found["place"] = {"value": part, "range": [pos, pos + len(part)]}
    if kind == "address":
        streets = list(STREET.finditer(value))
        if len(streets) == 1:
            m = streets[0]
            found["street"] = {"value": m.group(), "range": list(m.span())}
            civic = re.search(r"\b\d+[A-Z]?(?:/[A-Z0-9]+)?\b", m.group(), re.I)
            if civic:
                found["civic_number"] = {"value": civic.group()}
        postal = re.search(r"\b\d{5}\b", value)
        if postal:
            found["postal_code"] = {"value": postal.group(), "range": list(postal.span())}
        province = re.search(r"\(([A-Z]{2})\)|\bprov(?:incia)?\.?\s*:?\s*([A-Z]{2})\b", value)
        if province:
            found["province"] = {"value": province.group(), "range": list(province.span())}
            prefix = value[:province.start()]
            city = prefix[postal.end():] if postal else prefix.rsplit(",", 1)[-1]
            city = city.strip(" ,")
            if city and PLACE.fullmatch(city) and not STREET.search(city):
                found["place"] = {"value": city}
    if kind == "registration":
        register = re.search(r"\b(?:Ordine|Albo|Collegio)\b.+?(?=\s+(?:n\.|numero|del|dal|"
                             r"sezione|iscritt)|[,;]|$)", value, re.I)
        if register:
            found["register"] = {"value": register.group()}
        for name, word in [("section", r"sez(?:ione)?\.?"), ("class", r"classe")]:
            qualifier = re.search(r"\b" + word + r"\s*:?\s*([A-Z0-9]+)\b", value, re.I)
            if qualifier:
                found[name] = {"value": qualifier.group(), "range": list(qualifier.span())}
    if kind == "contract" and dates:
        description = DATES.sub("", value).strip(" ,:;-0123456789")
        if len(description.split()) >= 3:
            found["description"] = {"value": description}
    if kind in {"power_of_attorney", "contacts"}:
        patterns = {"notary": r"notaio", "repertory": r"repertorio|rep\.",
                    "collection": r"raccolta|racc\.", "mobile": r"cellulare",
                    "telephone": r"telefono|tel\."}
        for name in spec["required_components"]:
            m = re.search(r"\b(?:" + patterns[name] + r")\s*[:=]?\s*([^;|\n]+)", value, re.I)
            usable = m and re.search(r"\w", m[1])
            if usable:
                usable = not re.search(r"\b(?:non|ignoto|assente|mancante|fornire|nd)\b",
                                       m[1], re.I)
            if usable and name in {"repertory", "collection"}:
                usable = bool(NUMBER.fullmatch(m[1].strip()))
            if usable and kind == "contacts":
                usable = len(re.findall(r"\d", m[1])) >= 5
            if usable:
                found[name] = {"value": m[1].strip()}
    return {name: found[name] for name in spec["required_components"] if name in found}


def _coupled(spec, value, proofs, sources):
    """One existing literal value, in one actual assertion; never a span union."""
    if not spec["SOURCE_required"]:
        return True
    if spec["kind"] == "registration":
        # Component presence is insufficient: unrelated clauses inside a single
        # quoted value must not become a pair merely by sharing a SOURCE line.
        remainder = DATES.sub(" ", value)
        for part in _components(spec, value, None).values():
            remainder = remainder.replace(part["value"], " ")
        remainder = re.sub(r"\(\s*(?:sez(?:ione)?\.?|classe)\s*:?\s*[A-Z0-9]+\s*\)",
                           " ", remainder, flags=re.I)
        remainder = re.sub(r"\b(?:numero|num|n|data|anno|del|dal|di|il|e|ed|iscrizione|"
                           r"registrazione)\b", " ", remainder, flags=re.I)
        if re.search(r"\w", remainder):
            return False
    for proof in proofs:
        source = sources.get(proof["chunk_id"], {}).get("content", "")
        try:
            literal = source_span(source, value)
        except ValueError:
            continue
        for m in re.finditer(re.escape(literal), source):
            start = source.rfind("\n", 0, m.start()) + 1
            end = source.find("\n", m.end())
            record = source[start:end if end >= 0 else len(source)]
            if "\n" in literal or re.search(r"\b(?:non|esempio|ipotetic\w*)\b", record, re.I):
                continue
            keys = re.findall(r"\b(?:record|iscrizione|registrazione|contratto|procura)\s+"
                              r"(?:ID\s*[:=]?\s*)?([A-Z]+-?\d+)\b", record, re.I)
            owners = re.findall(r"\b(?:soggetto|societa|persona)\s*:\s*([^;|\n]+)", record, re.I)
            registries = {m.group().casefold() for m in re.finditer(
                r"\b(?:registro\s+(?:delle\s+)?imprese|REA|albo)\b", record, re.I)}
            if (len({_text(k) for k in keys}) > 1 or len({_text(s) for s in owners}) > 1
                    or spec["kind"] == "registration" and len(registries) > 1
                    or re.search(r"\b(?:altro|altra|secondo|seconda|distinto|distinta)\s+"
                                 r"(?:contratto|atto|iscrizione|record|procura)\b", record, re.I)):
                continue
            if spec["kind"] != "registration":
                return True
            # A value syntactically binding the pair still needs an actual
            # registration assertion. Nearby dates in other lines are irrelevant.
            registration_form = re.search(r"iscri\w*|registr\w*|albo|ordine",
                                          spec["FORM_context"], re.I)
            assertion = (r"\b(?:iscri\w*|registr\w*|albo|ordine|repertorio)\b"
                         if registration_form
                         else r"\b(?:iscri\w*|registr\w*|documento|atto|protocollo|"
                              r"certificato|fattura|contratto)\b")
            if re.search(assertion, record, re.I):
                bridge = re.search(r"\b(?:del|dal|data|anno|numero|e|ed|n[.°])\b", value, re.I)
                labels = re.search(r"\bnumero\b.+\b(?:data|anno)\b|"
                                   r"\b(?:data|anno)\b.+\bnumero\b", record, re.I)
                if bridge or labels:
                    return True
    return False


def assess(spec, value, fact, sources, *, user_quote=None):
    check = {**spec, "result": "UNKNOWN", "value": value, "components": {},
             "missing_components": [], "basis": "value_or_proof_not_demonstrated",
             "MODEL_disposition_used": False, "USER_assent_used": False}
    if not isinstance(value, str) or not value.strip() or spec["mode"] == "unknown":
        return check
    if (spec["mode"] != "any" and {"date", "year"} & set(spec["required_components"])
            and len({d["canonical"] for d in _date_spans(value)}) > 1):
        check["basis"] = "ambiguous_dates_for_one_required_component"
        return check
    found = _components(spec, value, fact.get("subject"))
    if spec["kind"] == "contacts" and fact.get("validation") == "GROUNDED_PROPOSAL":
        for name, label in [("mobile", "cellulare"), ("telephone", "telefono|tel[.]")]:
            for proof in fact.get("source_evidence", []):
                for line in proof["quote"].splitlines():
                    pattern = r"\b(?:" + label + r")\s*[:=]?\s*" + re.escape(_text(value))
                    if re.search(pattern, _text(line)):
                        found[name] = {"value": value, "range": [0, len(value)]}
    missing = [name for name in spec["required_components"] if name not in found]
    check.update(components=found, missing_components=missing)
    shape_complete = not missing or spec["mode"] == "any" and bool(found)
    if not shape_complete:
        ambiguous = spec["mode"] == "ambiguous" or spec["kind"] in {
            "person_identity", "open_description"}
        check.update(result="UNKNOWN" if ambiguous else "INCOMPLETE",
                     basis="ambiguous_requirement_or_value" if ambiguous
                     else "required_component_missing")
        if spec["kind"] == "person_identity" and fact.get("subject") and value in fact["subject"]:
            check.update(result="INCOMPLETE", basis="partial_person_identity")
        return check
    proofs = fact.get("source_evidence", [])
    if user_quote is not None and not spec["SOURCE_required"]:
        proofs = [{"role": "user", "quote": user_quote}]
    elif fact.get("validation") != "GROUNDED_PROPOSAL" or not proofs:
        check["basis"] = "SOURCE_fact_not_grounded"
        return check
    elif value != fact.get("value"):
        check["basis"] = "value_not_existing_grounded_fact"
        return check
    if len(found) > 1 and not _coupled(spec, value, proofs, sources):
        check["basis"] = "same_record_not_demonstrated"
        return check
    for component in found.values():
        supported = []
        for proof in proofs:
            try:
                literal = source_span(proof["quote"], component["value"])
            except ValueError:
                continue
            supported.append({**proof, "component_quote": literal})
        component["evidence"] = supported
        if not supported:
            check["basis"] = "component_without_provenance"
            return check
    check.update(result="COMPLETE", basis="all_required_components_documented_in_existing_value")
    return check


def evaluate(audit, catalog, sources):
    fields = {f["candidate_id"]: f for f in audit["fields"]}
    checks = {}
    for cid, spec in requirements(catalog).items():
        field = fields.get(cid, {})
        proposal = field.get("proposal") or {}
        fid = field.get("fact_id") or field.get("proposed_fact_id") or proposal.get("fact_id")
        fact = audit.get("facts", {}).get(fid, {})
        if field.get("source_reuse"):
            fact = {**field["source_reuse"].get("fact", {}),
                    "source_evidence": field.get("source_evidence", []),
                    "validation": field.get("proposal_grounding", field.get("validation"))}
        value = field.get("proposed_value", field.get("value"))
        if value is None:
            value = fact.get("value")
        checks[cid] = assess(spec, value, fact, sources)
    return checks


def refresh_reused(audit, layout, catalog, sources):
    if "value_completeness" in audit:
        from app.compilation_table_form import relations

        bound = {**catalog, "_table_form_links": relations(layout, catalog)}
        audit["value_completeness"] = evaluate(audit, bound, sources)
    return audit


def value_check(data, cid, value, *, user_quote=None):
    """USER cannot replace absent SOURCE components by confirming a partial fact."""
    audit = data.get("audit") or {}
    check = audit.get("value_completeness", {}).get(cid)
    if check is None:
        if "value_completeness" in audit or cid not in requirements(data["catalog"]):
            return None
        return {"result": "UNKNOWN", "basis": "requires_reanalysis"}
    if value == check["value"]:
        return check
    if not check["SOURCE_required"] and user_quote:
        return assess(check, value, {}, {}, user_quote=user_quote)
    return {**check, "result": "UNKNOWN", "value": value,
            "basis": "USER_value_without_same_complete_SOURCE_fact"}


def blocked_fields(data):
    if "audit" not in data:
        return {f["candidate_id"] for f in data.get("fields", [])
                if f.get("value_completeness", {}).get("result", "COMPLETE") != "COMPLETE"}
    audit = data.get("audit") or {}
    if audit.get("version") != 12:
        return set()
    if "value_completeness" not in audit:
        return set(requirements(data["catalog"]))
    from app.compilation_branch_evidence import effective_user_values

    users = effective_user_values(data)
    blocked = set()
    for cid, check in audit["value_completeness"].items():
        if cid in users:
            user = users[cid]
            check = value_check(data, cid, user["value"], user_quote=user.get("user_quote"))
        if check["result"] != "COMPLETE":
            blocked.add(cid)
    return blocked
