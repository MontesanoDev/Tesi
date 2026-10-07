"""Conservative checks for the condition already grounded in the structural FORM."""

import re

from app.requirement_checks import contains_form_span, normalized, normalized_form_text


def predicate(condition):
    return re.sub(r"^(?:se\s+|in caso di\s+|nel caso di\s+)", "", normalized(condition)).strip()


def condition_terms(condition):
    return set(re.findall(r"\w{3,}", predicate(condition))) - {
        "del", "della", "dell", "dei", "degli", "delle", "alla", "alle", "con", "per",
        "caso", "che", "come", "quando", "sono", "sia", "agisce", "qualita",
    }


def explicit_condition_reply(condition, quote, *, applies):
    """A model proposes the relation; the gate requires a local explicit affirmation.

    Only regular final-vowel variation is allowed for USER replies (plural, gender).
    No guessed synonym, absent source, or generic uncertainty establishes a condition.
    """
    text = normalized(quote).strip(" .!?")
    if text in ({"si", "sì", "si applica", "sì, si applica"} if applies else {
        "no", "non si applica", "non riguarda noi", "non è pertinente", "non e pertinente",
        "non è applicabile", "non e applicabile",
    }):
        return True
    terms = condition_terms(condition)
    words = set(re.findall(r"\w+", text))

    def stem(word):
        return word[:-1] if len(word) >= 5 and word[-1] in "aeio" else word

    related = bool(terms) and {stem(t) for t in terms} <= {stem(w) for w in words}
    negative = bool(re.search(r"\b(?:non|nessun\w*|senza)\b", text))
    uncertain = bool(re.search(r"\b(?:forse|sicuro|sicura|so|sappiamo|saprei)\b", text))
    return related and not uncertain and negative != applies


def known_applicability(field):
    evidence = field.get("applicability") or {}
    if evidence.get("condition") == field.get("condition"):
        return evidence.get("applies")
    # Compatibility with previous, explicit USER confirmations.
    if field.get("applicability_confirmed"):
        return True
    return None


def validate_condition_source(field, support, source):
    condition = field.get("condition", "")
    if not condition or source.get("role") != "source":
        raise ValueError("L'applicabilità richiede una condizione FORM e una SOURCE")
    if not contains_form_span(source["content"], support.quote) or not contains_form_span(
        support.quote, support.value,
    ):
        raise ValueError("La prova di applicabilità non appartiene alla SOURCE")
    # Require all predicate words in the same literal assertion as the polarity.
    # A number/value for the dependent field is not proof of this condition.
    terms = condition_terms(condition)
    value = normalized_form_text(support.value)
    if not terms or not terms <= set(re.findall(r"\w+", value)) or len(value.split()) < 3:
        raise ValueError("La SOURCE non attesta esplicitamente questa condizione")
    negative = bool(re.search(r"\b(?:non|nessun\w*|senza)\b", value))
    if negative == support.applies or re.search(
        r"\b(?:se|esempio|forse|ipotetic\w*|potrebbe)\b", value,
    ) or re.search(r"[;\n]|[.!?]\s", value):
        raise ValueError("Polarità di applicabilità non verificata nella SOURCE")
    # An extracted positive span cannot drop a preceding negation/hypothesis.
    # Inspect its local SOURCE clause, anchored through the exact quoted context.
    text, quote = normalized_form_text(source["content"]), normalized_form_text(support.quote)
    offset = quote.index(value)
    for occurrence in re.finditer(re.escape(quote), text):
        prefix = re.split(r"[;.!?]\s+", text[:occurrence.start() + offset])[-1]
        if not re.search(r"\b(?:non|nessun\w*|senza|se|esempio|forse|ipotetic\w*)\b", prefix):
            return
    raise ValueError("L'estratto omette una negazione/ipotesi precedente nella SOURCE")
