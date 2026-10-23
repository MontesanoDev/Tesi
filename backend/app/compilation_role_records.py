"""Bounded personal records; V12 also verifies role tables and named bullets.

No role synonyms, domain-specific titles or name inference. These are necessary
local attribution checks, not independent semantic approval of a field value.
"""

import re
import unicodedata
from datetime import date


def _text(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def _person(value, subject):
    # Optional abbreviated titles are syntax, never a qualification inferred
    # from an honorific. The complete proposed subject must still match.
    return bool(re.fullmatch(r"(?:[^\W\d_]{1,10}\.\s+){0,2}" + re.escape(_text(subject)),
                             _text(value)))


def _capital_row(line):
    first = line.strip().split(maxsplit=1)
    return bool(first and sum(c.isalpha() for c in first[0]) >= 3 and first[0].isupper())


def personal_records(source, role, subject):
    """Yield explicit heading/uppercase-row records, bounded by the next record.

    Match whole actual lines, not a cropped model quote that hides a negation.
    Values outside this personal record cannot use its role attribution.
    """
    lines = source.splitlines()
    for index, line in enumerate(lines):
        line = line.strip()
        heading = re.fullmatch(r"#{1,6}\s+(.+?)\s+[-–—]\s+(.+?)\s*", line)
        kind = None
        if heading and _text(heading[2]) == _text(role) and _person(heading[1], subject):
            kind = "person_role_heading"
        elif not heading:
            # Uppercase attribute rows are unambiguous literal formatting;
            # ordinary narrative without a colon remains unsupported.
            prefix = re.match(re.escape(_text(role)) + r"\s+", _text(line))
            if prefix:
                words = line.split()
                role_words = len(role.split())
                literal_role = " ".join(words[:role_words])
                remainder = " ".join(words[role_words:])
                name = re.split(r"\s+[-–—]\s+", remainder, maxsplit=1)[0]
                if literal_role.isupper() and _person(name, subject):
                    kind = "uppercase_role_person_row"
        if kind is None:
            continue
        end = index + 1
        while end < len(lines):
            if re.match(r"^\s*#{1,6}\s+", lines[end]) or _capital_row(lines[end]):
                break
            end += 1
        yield {"format": kind, "header": line.lstrip("# "),
               "record": "\n".join(lines[index:end]),
               "line_range": [index, end]}


def record_support(source, role_quote, role, subject, value_quotes):
    """The grounded role quote and every value quote must share one record."""
    for record in personal_records(source, role, subject):
        if (_text(record["header"]) in _text(role_quote)
                and all(_text(quote) in _text(record["record"]) for quote in value_quotes)):
            return {key: record[key] for key in ("format", "header", "line_range")}
    return None


def _uncertain(text):
    return bool(re.search(
        r"\b(?:non|senza|ex|potenzial\w*|ipotetic\w*|futur\w*|cessat\w*|revocat\w*|"
        r"esclus\w*|scadut\w*)\b|\bda\s+(?:nominare|confermare|verificare)\b", _text(text)))


def _same_person(name, subject):
    # Optional abbreviated titles on either side never establish a qualification.
    return _person(name, subject) or _person(subject, name)


def _table_records(source, role):
    """Read complete pipe tables immediately after an affirmative role heading.

    Italian singular/plural endings are syntax only, confined to this heading;
    required_role/source_role still have to agree exactly in the caller.
    """
    words = []
    for word in _text(role or "").split():
        suffix = {"o": "i", "a": "e", "e": "i"}.get(word[-1:]) if len(word) > 2 else None
        plural = word[:-1] if word.endswith("io") else word[:-1] + suffix if suffix else word
        words.append(f"(?:{re.escape(word)}|{re.escape(plural)})")
    label = r"\s+".join(words)
    lines = source.splitlines()
    for index in range(1, len(lines) - 1):
        header, delimiter = lines[index].strip(), lines[index + 1].strip()
        if not (header.startswith("|") and header.endswith("|")):
            continue
        columns = [c.strip() for c in header[1:-1].split("|")]
        separators = [c.strip() for c in delimiter.strip("|").split("|")]
        if (len(columns) < 2 or not all(columns) or len(separators) != len(columns)
                or not all(re.fullmatch(r":?-{3,}:?", c) for c in separators)):
            continue
        preceding = index - 1
        while preceding >= 0 and not lines[preceding].strip():
            preceding -= 1
        title = lines[preceding].strip() if preceding >= 0 else ""
        heading = re.fullmatch(r"#{1,6}\s+(?:\d+[.)]?\s+)?(.+)", title)
        if (not heading or _uncertain(title) or (role is not None and not re.match(
                label + r"(?:$|\s+(?:di|del|della|dello|dei|degli|delle|al|alla)\b|\s*[-—:])",
                _text(heading[1])))):
            continue
        rows, end = [], index + 2
        while end < len(lines) and lines[end].strip().startswith("|"):
            row = lines[end].strip()
            cells = [c.strip() for c in row[1:-1].split("|")] if row.endswith("|") else []
            if len(cells) != len(columns) or not cells[0]:
                rows = []
                break
            rows.append({"format": "markdown_role_table", "title": title, "header": header,
                         "delimiter": delimiter, "row": row, "subject": cells[0],
                         "line_range": [preceding, end + 1]})
            end += 1
        for row in rows:
            if sum(_same_person(other["subject"], row["subject"]) for other in rows) == 1:
                yield row


def table_support(source, role, subject, quotes, *, binding=False):
    """Require one physical table/row; never combine headings or other people."""
    matches = []
    for record in _table_records(source, role):
        if _uncertain(record["row"]) or (
                subject is not None and not _same_person(record["subject"], subject)):
            continue
        parts = [record["row"]]
        if binding:
            parts += [record[k] for k in ("title", "header", "delimiter")]
            if not all(any(_text(record[k]) == _text(q) for q in quotes)
                       for k in ("title", "row")):
                continue
        if quotes and all(any(_text(q) in _text(p) for p in parts) for q in quotes):
            matches.append(record)
    return matches[0] if len(matches) == 1 else None


def fact_record_support(source, quote, role, subject):
    """A fact's own SOURCE must independently attest its subject and exact role."""
    table = table_support(source, role, subject, [quote])
    if table:
        return table
    records = [r for r in personal_records(source, role, subject)
               if _text(quote) in _text(r["record"]) and not _uncertain(r["record"])]
    for index, line in enumerate(source.splitlines()):
        # One complete named bullet, not prose cropped after a preceding negation.
        named = re.fullmatch(r"\s*-\s+\*\*([^:*]+):\*\*\s+(.+)", line)
        if (named and _same_person(named[1], subject) and not _uncertain(line)
                and "**" not in named[2] and re.match(
                    re.escape(_text(role)) + r"(?:$|[;,\.]|\s+(?:di|del|della|dello)\b)",
                    _text(named[2])) and _text(quote) in _text(line)):
            records.append({"format": "named_role_line", "header": line.strip(),
                            "line_range": [index, index + 1]})
    if len(records) == 1:
        return {k: records[0][k] for k in ("format", "header", "line_range")}
    return None


def _subject_records(source, subject):
    """Bound each value quote to one actual person's record, independently of role."""
    for record in _table_records(source, None):
        if (subject is None or _same_person(record["subject"], subject)) and not _uncertain(
                record["row"]):
            yield {**record, "record": record["row"]}
    for line in source.splitlines():
        heading = re.fullmatch(r"\s*#{1,6}\s+(.+?)\s+[-–—]\s+(.+?)\s*", line)
        if (heading and (subject is None or _same_person(heading[1], subject))
                and not _uncertain(line)):
            for record in personal_records(source, heading[2], heading[1]):
                nested_person = re.search(r"(?m)^\s*-\s+\*\*[^:*]+:\*\*", record["record"])
                if record["header"] == line.strip().lstrip("# ") and not nested_person:
                    yield {**record, "subject": heading[1], "role": heading[2]}
        named = re.fullmatch(r"\s*-\s+\*\*([^:*]+):\*\*\s+(.+)", line)
        if (named and (subject is None or _same_person(named[1], subject)) and "**" not in named[2]
                and not _uncertain(line)):
            yield {"format": "named_person_line", "record": line, "header": line,
                   "subject": named[1]}


def _value_record(source, quote, subject):
    matches = [r for r in _subject_records(source, subject)
               if _text(quote) in _text(r["record"])]
    return matches[0] if len(matches) == 1 else None


def _property(value):
    return re.sub(r"[^\w]", "", _text(value)).replace("_", "")


# Typed SOURCE columns, not role/qualification equivalences or fixture values.
_COLUMNS = {
    "nome": {"persona", "nomeecognome", "nominativo"},
    "qualificaprofessionale": {"qualificaprofessionale"},
    "ordineprofessionale": {"albo", "ordineprofessionale"},
    "sezione": {"sezione"},
    "provincia": {"provincia"},
    "iscrizionedal": {"iscrizionedal"},
    "numeroiscrizione": {"niscrizione", "numeroiscrizione"},
    "codicefiscale": {"codicefiscale", "codicefiscaledimostrativo"},
}


def _cells(record):
    columns = [_property(c) for c in record["header"].strip("|").split("|")]
    if len(columns) != len(set(columns)):
        return {}
    return dict(zip(columns, [c.strip() for c in record["row"].strip("|").split("|")]))


def _name(value):
    # Syntax for name fields only. Never establishes a professional qualification.
    return re.sub(r"^(?:(?:ing|arch|geom|dott|dott\.ssa|dr|avv)\.\s+){1,2}", "", _text(value))


def _date(value):
    text = _text(value)
    months = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
              "agosto", "settembre", "ottobre", "novembre", "dicembre")
    numeric = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    words = re.fullmatch(r"(\d{1,2}) (" + "|".join(months) + r") (\d{4})", text)
    try:
        if numeric:
            return date(int(numeric[3]), int(numeric[2]), int(numeric[1]))
        if iso:
            return date(*map(int, iso.groups()))
        if words:
            return date(int(words[3]), months.index(words[2]) + 1, int(words[1]))
    except ValueError:
        pass
    return None


def _comparison(value, cell, prop, subject):
    if _text(value) == _text(cell):
        return "exact"
    if prop == "nome" and _name(value) == _name(cell) == _name(subject):
        return "professional_title"
    if prop == "iscrizionedal" and _date(value) and _date(value) == _date(cell):
        return "calendar_date"
    return None


def binding_value_support(binding, fact, source_map):
    """An independent exact/typed-equivalent proof in the binding's role/person row.

    Never discard a fact citation about another person. No identity merge and
    no property inferred from an arbitrary matching substring of the row.
    """
    records = []
    for proof in fact["source_evidence"]:
        record = _value_record(source_map[proof["chunk_id"]]["content"], proof["quote"],
                               fact["subject"])
        if proof["category"] == "general" or not record:
            return None
        records.append(record)
    proofs = binding["source_evidence"]
    if len({p["chunk_id"] for p in proofs}) != 1:
        return None
    chunk = proofs[0]["chunk_id"]
    row = table_support(source_map[chunk]["content"], binding["source_role"], fact["subject"],
                        [p["quote"] for p in proofs], binding=True)
    if not row:
        return None
    if any(_conflicting_keys(_identity(row), _identity(record)) for record in records):
        return None
    values = [v for k, v in _cells(row).items()
              if k in _COLUMNS.get(_property(fact["property"]), set())]
    comparison = _comparison(fact["value"], values[0], _property(fact["property"]),
                             fact["subject"]) if len(values) == 1 else None
    if not comparison:
        return None
    citations = _record_citations(chunk, row)
    if not citations:
        return None
    return {"record": {"chunk_id": chunk, **row},
            "identity_support": {"method": "direct_role_record", "subject": row["subject"]},
            "role_support": {"role": binding["source_role"], "subject": row["subject"]},
            "value_support": {"comparison": comparison, "property": fact["property"],
                              "proposed_value": fact["value"], "source_value": values[0]},
            "citations": citations}


def _identity(record):
    """Only explicitly labelled personal keys; never numbers from arbitrary prose."""
    if "row" in record:
        cells = _cells(record)
        keys = {}
        for key, columns in {"cf": _COLUMNS["codicefiscale"],
                             "order": _COLUMNS["ordineprofessionale"],
                             "number": _COLUMNS["numeroiscrizione"]}.items():
            values = {_text(v) for k, v in cells.items() if k in columns}
            keys[key] = next(iter(values)) if len(values) == 1 else "!conflict" if values else ""
        return keys
    text = record["record"]
    patterns = {
        "cf": r"codice fiscale(?: personale)?(?: dimostrativo)?",
        "order": r"(?:ordine professionale(?: simulato)?|albo)",
        "number": r"(?:numero(?: di)? iscrizione(?: professionale)?(?: simulato)?|n\. iscrizione)",
    }
    patterns = {key: r"^\s*-?\s*" + label + r"\s*:\s*(.+?)\.?\s*$"
                for key, label in patterns.items()}
    if record["format"] == "named_person_line":
        patterns = {
            "cf": r"\bcodice fiscale(?: personale)?(?: dimostrativo)?\s*:?\s*([a-z0-9]{16})\b",
            "order": r"\b(ordine (?:degli|dei|delle|di)\s+[^,;.\n]+)",
            "number": r"\b(?:numero|n\.)\s+(\d[a-z0-9/-]*)\b",
        }
    keys = {}
    for key, pattern in patterns.items():
        values = re.findall(pattern, text, re.M | re.I)
        values = {_text(v) for v in values if not _uncertain(v)}
        # Multiple distinct assertions in a single record are a conflict too.
        keys[key] = next(iter(values)) if len(values) == 1 else "!conflict" if values else ""
    return keys


def _record_certain(record):
    # Missing attributes are not negative identity assertions. Drop only a full
    # labelled missing-value line, never a negated/revoked role or cropped prose.
    text = re.sub(r"(?mi)^\s*-\s*(?!ruolo\b|carica\b|incarico\b)[^:\n]+:\s*"
                  r"non (?:disponibil[ei]|documentat[oi])\.?\s*$", "", record["record"])
    # An explicit role-versus-designation limitation is not a denial of that
    # role. Remove only this operator: any other negation/revocation still vetoes.
    text = re.sub(r"(?mi)^(Il ruolo [^\n;.]*?)\bnon equivale a\b", r"\1è distinto da", text)
    return not _uncertain(text)


def _conflicting_keys(first, second):
    return ("!conflict" in first.values() or "!conflict" in second.values()
            or any(first.get(k) and second.get(k) and first[k] != second[k]
                   for k in ("cf", "order", "number")))


def _record_citations(chunk, record):
    parts = [record[k] for k in ("title", "header", "delimiter", "row")] if "row" in record else [
        record["record"]]
    quotes = [line for part in parts for line in (
        part.splitlines() if len(part) > 800 else [part]) if line.strip()]
    return [{"chunk_id": chunk, "quote": q} for q in quotes] if all(
        len(q) <= 800 for q in quotes) else []


def linked_person_support(binding, fact, source_map, *, verified_properties=False):
    """Bounded personal-key join, independent of role and FORM applicability.

    Transfer only a personal CF or attributes of the same professional
    registration from a complete table. Never join names alone or transfer
    authority, roles, company attributes or arbitrary facts. V13 additionally
    admits typed name/qualification/registration properties, with the same
    explicit personal/registration keys and a separate physical FORM check.
    """
    prop = _property(fact["property"])
    prop = {"provinciaalbo": "provincia", "dataiscrizionealbo": "iscrizionedal",
            "numeroiscrizionealbo": "numeroiscrizione"}.get(prop, prop)
    supported = {"codicefiscale", "provincia", "iscrizionedal", "numeroiscrizione"}
    if verified_properties:
        prop = {"nomecompleto": "nome", "nomeecognome": "nome",
                "sezioneordine": "sezione", "sezionealbo": "sezione",
                "provinciaordine": "provincia", "numeroiscrizioneordine": "numeroiscrizione",
                "codicefiscalepersonale": "codicefiscale"}.get(prop, prop)
        supported |= {"nome", "qualificaprofessionale", "ordineprofessionale", "sezione"}
    if prop not in supported:
        return None
    subject = _name(fact["subject"])
    role_records = []
    for proof in binding["source_evidence"]:
        source = source_map[proof["chunk_id"]]
        if source["category"] == "general":
            return None
        for record in _subject_records(source["content"], fact["subject"]):
            role_matches = (record.get("role") and
                            _text(record["role"]) == _text(binding["source_role"]))
            if verified_properties and record["format"] == "named_person_line":
                role_matches = fact_record_support(source["content"], proof["quote"],
                                                   binding["source_role"], fact["subject"])
            if (role_matches
                    and _text(proof["quote"]) in _text(record["record"])
                    and _record_certain(record)):
                pair = (source["chunk_id"], record)
                if pair not in role_records:
                    role_records.append(pair)
    if len(role_records) != 1:
        return None
    role_chunk, role_record = role_records[0]
    role_key = _identity(role_record)
    if "!conflict" in role_key.values():
        return None
    values = []
    for proof in fact["source_evidence"]:
        if proof["category"] == "general":
            return None
        record = _value_record(source_map[proof["chunk_id"]]["content"], proof["quote"],
                               fact["subject"])
        if not record or "row" not in record or not _record_certain(record):
            return None
        cells = _cells(record)
        cell = [v for k, v in cells.items() if k in _COLUMNS[prop]]
        comparison = (_comparison(fact["value"], cell[0], prop, fact["subject"])
                      if len(cell) == 1 and verified_properties else None)
        if len(cell) != 1 or not (comparison or _text(cell[0]) == _text(fact["value"])):
            return None
        key = _identity(record)
        if "!conflict" in key.values():
            return None
        if role_key.get("cf") and re.fullmatch(r"[a-z0-9]{16}", role_key["cf"]) and (
                role_key["cf"] == key.get("cf")):
            method = "personal_identifier"
        elif (all(role_key.get(k) and role_key[k] == key.get(k) for k in ("order", "number"))
              and re.fullmatch(r"[a-z0-9/-]*\d[a-z0-9/-]*", role_key["number"])):
            method = "professional_registration"
        else:
            return None
        # Same registration is needed for a professional province even with a CF.
        if prop != "codicefiscale" and not all(
                key.get(k) and key[k] == role_key.get(k) for k in ("order", "number")):
            return None
        for source in source_map.values():
            if source["category"] == "general":
                continue
            for other in _subject_records(source["content"], None):
                other_key = _identity(other)
                same_name = _name(other["subject"]) == subject
                same_id = (key.get("cf") and key["cf"] == other_key.get("cf")) or all(
                    key.get(k) and key[k] == other_key.get(k) for k in ("order", "number"))
                if same_id and not same_name:
                    return None
                if same_name and _conflicting_keys(key, other_key):
                    return None
        values.append((proof["chunk_id"], record, key, method, cell[0], comparison or "exact"))
    if not values:
        return None
    citations = _record_citations(role_chunk, role_record)
    if not citations:
        return None
    for chunk, record, _, _, _, _ in values:
        parts = _record_citations(chunk, record)
        if not parts:
            return None
        citations.extend(parts)
    if not citations:
        return None
    key, method = values[0][2:4]
    shared = ("cf",) if method == "personal_identifier" else ("order", "number")
    return {"record": {"format": "verified_person_records", "role_chunk_id": role_chunk,
                       "value_chunk_ids": [v[0] for v in values]},
            "identity_support": {"method": method, "subject": subject,
                                 "key": {k: key[k] for k in shared},
                                 "role_record_keys": role_key,
                                 "value_record_keys": [v[2] for v in values]},
            "role_support": {"role": binding["source_role"], "subject": subject,
                             "chunk_id": role_chunk},
            "value_support": {"comparison": values[0][5] if verified_properties else "exact",
                              "property": fact["property"], "proposed_value": fact["value"],
                              "source_value": (values[0][4] if verified_properties
                                               else fact["value"])},
            "citations": citations}
