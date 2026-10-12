"""Literal personal record formats for the experimental V10 proposal only.

No role synonyms, domain-specific titles or name inference. These are necessary
local attribution checks, not independent semantic approval of a field value.
"""

import re
import unicodedata


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
