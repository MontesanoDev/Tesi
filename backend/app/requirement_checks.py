"""Ephemeral, quoted requirements and factual support for one chat response.

This does not resolve DOCX candidates or keep compilation state. The backend
renders availability only from validated source values, never model prose.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

from pydantic import BaseModel, ConfigDict, Field

MAX_REQUIREMENTS = 16
# Bound provider output separately from the context budget. A seventeenth valid
# requirement must not invalidate the first sixteen grounded requirements.
MAX_EXTRACTION_REQUIREMENTS = 32
MAX_FORM_QUOTE = 2000


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def normalized_form_text(text: str) -> str:
    # Typographic variants only: preserve words, order and internal punctuation.
    return normalized(text).translate(str.maketrans({
        "’": "'", "‘": "'", "ʼ": "'", "“": '"', "”": '"', "–": "-", "—": "-",
    }))


def contains_form_span(text: str, span: str) -> bool:
    span = normalized_form_text(span).rstrip(" :")
    if not span:
        return False
    # A terminal field colon is optional; ISO 9001 must not match ISO 90010.
    pattern = (r"(?<!\w)" if span[0].isalnum() else "") + re.escape(span)
    pattern += r"(?!\w)" if span[-1].isalnum() else ""
    return re.search(pattern, normalized_form_text(text)) is not None


AVAILABILITY_PATTERNS = (
    r"\b(?:posso|possiamo|puoi|potete|potremmo|puo|possono|e possibile)\b"
    r".{0,100}\b(?:compil\w*|valorizz\w*|soddisf\w*)\b",
    r"\b(?:abbiamo|ho|avete|hai)\b.{0,70}"
    r"\b(?:dati|informazioni|sede|denominazione|direttore|partita|certificaz\w*)\b",
    r"\b(?:dato|dati|informazioni|campo|campi|valore|valori|direttore|sede|modulo)\b"
    r".{0,60}\b(?:disponibil\w*|compilabil\w*|valorizzabil\w*)\b",
    r"\b(?:documenti|fonti)\b.{0,50}\bcontengono\b.{0,40}\b(?:dato|dati|valore|valori)\b",
)


def availability_requested(question: str) -> bool:
    text = normalized(question)
    return any(re.search(pattern, text) for pattern in AVAILABILITY_PATTERNS) or bool(
        re.search(r"\b(?:manca|mancano)\b.{0,70}\b(?:compil\w*|complet\w*)\b", text)
    )


def claims_availability(text: str) -> bool:
    for sentence in re.split(r"[.!?;\n]", normalized(text)):
        for pattern in AVAILABILITY_PATTERNS:
            for match in re.finditer(pattern, sentence):
                prefix = sentence[max(0, match.start() - 35):match.start()]
                if not re.search(r"\b(?:non|nessun\w*)\b", prefix):
                    return True
    return False


class Requirement(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    form_quote: str = Field(min_length=2, max_length=MAX_FORM_QUOTE)
    form_citation_id: int = Field(ge=1)
    person_role: str = Field(
        default="", max_length=120,
        description="Ruolo di una persona fisica, copiato dal FORM. Vuoto per dati aziendali, "
                    "titoli di sezione, categorie di operatori, condizioni e allegati.",
    )


class RequirementPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    requirements: list[Requirement] = Field(max_length=MAX_EXTRACTION_REQUIREMENTS)


class SourceSupport(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    requirement_id: int = Field(ge=1)
    source_citation_id: int = Field(ge=1)
    source_quote: str = Field(min_length=2, max_length=800)
    value: str = Field(min_length=2, max_length=300)


class RequirementChecks(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    supports: list[SourceSupport] = Field(max_length=MAX_REQUIREMENTS)


def validate_requirements(plan: RequirementPlan, forms: list[dict]) -> RequirementPlan:
    seen, unique, errors = set(), [], []
    for requirement in plan.requirements:
        index = requirement.form_citation_id - 1
        key = (normalized_form_text(requirement.person_role),
               normalized_form_text(requirement.name).rstrip(" :"))
        if key in seen:
            continue  # Only the first already validated occurrence is used below.
        error = None
        if not 0 <= index < len(forms) or forms[index].get("role") != "form":
            error = "form_citation_id non identifica una evidence FORM"
        elif not contains_form_span(forms[index]["content"], requirement.form_quote):
            error = "form_quote assente nella evidence citata"
        elif not contains_form_span(requirement.form_quote, requirement.name):
            error = "name assente in form_quote: usa un'etichetta letterale più breve"
        elif requirement.person_role and not contains_form_span(
            requirement.form_quote, requirement.person_role,
        ):
            error = (
                "person_role assente in form_quote: includi il contesto del soggetto nell'estratto"
            )
        elif any(claims_availability(text) or re.search(r"\[\d+]", text)
                 for text in (requirement.name, requirement.person_role)):
            error = "Un requisito non può essere un'affermazione di disponibilità"
        if error:
            errors.append(f"{requirement.name}: {error}")
            continue
        unique.append(requirement)
        seen.add(key)
    if errors:
        raise ValueError("\n".join(errors))
    return plan.model_copy(update={"requirements": unique[:MAX_REQUIREMENTS]})


def requirement_label(requirement: Requirement) -> str:
    if requirement.person_role:
        return f"{requirement.person_role}: {requirement.name}"
    return requirement.name


def requirement_source_queries(requirements: list[Requirement]) -> list[str]:
    """Queries cannot come from the generic question or from invented field names."""
    names = [
        requirement_label(requirement) + (
            " ragione sociale S.r.l. S.p.A."
            if normalized(requirement.name) == "denominazione sociale" else ""
        )
        for requirement in requirements
    ]
    # Called on one coherent source cluster, never interleave unrelated fields.
    size = 1 if len(names) <= 2 else 2
    return [" ".join(names[start:start + size]) + " dati effettivi operatore economico"
            for start in range(0, len(names), size)]


def _requirement_tokens(name: str) -> set[str]:
    return set(re.findall(r"\w{3,}", normalized(name))) - {
        "del", "della", "dell", "dei", "degli", "delle", "alla", "alle", "con", "per",
        "all", "allo", "agli", "appartenenza", "operatore", "economico",
    }


def quote_matches_requirement(requirement: Requirement, quote: str, value: str) -> bool:
    raw_quote = quote
    name, quote, value = map(normalized, (requirement.name, quote, value))
    if requirement.person_role:
        if not contains_form_span(quote, requirement.person_role):
            return False
    elif name in {
        "nome e cognome", "qualifica professionale", "ordine professionale di appartenenza",
    }:
        # A generic personal field may refer to different people in the form.
        # It needs the same explicit role in both quoted contexts before any
        # person's value can be called available; a name elsewhere is insufficient.
        roles = ("direttore tecnico", "legale rappresentante", "socio", "soci")
        if not any(role in normalized(requirement.form_quote) and role in quote for role in roles):
            return False
    # Professional registration has conventional equivalent labels (albo,
    # iscrizione professionale, ordine). Bind the number to that actual local
    # relation, not to a number anywhere in a paragraph mentioning the role.
    if _professional_registration_number(name):
        return _registration_value(quote, value)
    tokens = _requirement_tokens(name)
    # Conservative textual association. A bare corporate name can document
    # denomination without a field heading; it cannot document a director.
    corporate_name = name == "denominazione sociale" and bool(
        re.search(r"\b(?:s\s*\.?\s*r\s*\.?\s*l|s\s*\.?\s*p\s*\.?\s*a)\b", value)
    )
    if re.search(r"\d", value) and not corporate_name:
        # A numeric value elsewhere in a long quote cannot support a field
        # merely because the field label also occurs somewhere in that quote.
        clauses = [normalized(clause) for clause in re.split(
            r"\n|;|\.\s+(?=[a-z])", raw_quote.casefold(),
        )]
        for index, clause in enumerate(clauses):
            if index and clauses[index - 1].rstrip().endswith(":"):
                clause = clauses[index - 1] + " " + clause
            if (contains_form_span(clause, value) and tokens
                    and all(token in clause for token in tokens)):
                return True
        return False
    return corporate_name or bool(tokens and all(token in quote for token in tokens))


def _professional_registration_number(name: str) -> bool:
    return bool(re.search(r"\bnumero\b", name) and re.search(r"\biscrizion\w*\b", name)
                and re.search(r"\b(?:albo|ordine|professionale)\b", name))


def _registration_value(quote: str, value: str) -> bool:
    if not re.fullmatch(r"\d{1,12}", value):
        return False
    # No arbitrary gaps: an unrelated phone, year, invoice or other registration
    # number cannot be selected just because the same chunk mentions an albo.
    relation = (
        r"(?:numero\s+di\s+)?iscrizione\s+"
        r"(?:professionale|(?:all['’]?|all[ao]?\s+)\s*(?:albo|ordine)(?:\s+professionale)?)"
        r"(?:\s+simulat[oa])?\s*(?:(?:n\.?|numero)\s*)?[:\-]?\s*"
        r"(?P<value>\d{1,12})(?!\w)"
    )
    for match in re.finditer(relation, quote):
        prefix = re.split(r"[.;\n]", quote[:match.start()])[-1]
        if match['value'] == value and not re.search(
            r"\b(?:non|nessun\w*|esempio|ipotetic\w*)\b", prefix,
        ):
            return True
    return False


def validated_supports(
    checks: RequirementChecks, requirements: list[Requirement],
    forms: list[dict], sources: list[dict],
    *, discard_invalid: bool = False,
    source_coverage: dict[int, set[int]] | None = None,
) -> dict[int, SourceSupport]:
    if discard_invalid:
        verified = {}
        counts = Counter(support.requirement_id for support in checks.supports)
        for support in checks.supports:
            if counts[support.requirement_id] > 1:
                continue  # Competing proposals do not establish one verified value.
            try:
                verified.update(validated_supports(
                    RequirementChecks(supports=[support]), requirements, forms, sources,
                    source_coverage=source_coverage,
                ))
            except ValueError:
                continue
        return verified
    all_evidence = forms + sources
    verified = {}
    for support in checks.supports:
        index, requirement_id = support.source_citation_id - 1, support.requirement_id
        quote, value = normalized(support.source_quote), normalized(support.value)
        if (
            not 1 <= requirement_id <= len(requirements) or requirement_id in verified
            or not len(forms) <= index < len(all_evidence)
            or all_evidence[index].get("role") != "source"
            or (source_coverage is not None and (
                requirement_id not in source_coverage
                or support.source_citation_id not in source_coverage[requirement_id]
            ))
            or quote not in normalized(all_evidence[index]["content"]) or value not in quote
            or not re.search(r"\w", value) or not value.strip("_ .…-[]")
            or value in {"si", "no", "disponibile", "verificato", "compilabile"}
            or re.search(r"\[\d+]", value) or claims_availability(support.value)
            or re.search(
                r"\b(?:da compilare|non indicat\w*|non documentat\w*|non disponibil\w*)\b", value,
            )
        ):
            raise ValueError("Disponibilità senza valore ed estratto sostenuti da una SOURCE")
        requirement = requirements[requirement_id - 1]
        if (
            set(re.findall(r"\w+", value)) <= set(re.findall(r"\w+", normalized(requirement.name)))
            or re.search(r"\b(?:norme|criteri generali|esempio generico)\b", quote)
            or not quote_matches_requirement(requirement, support.source_quote, support.value)
        ):
            missing_words = sorted(word for word in _requirement_tokens(requirement.name)
                                   if word not in quote)
            raise ValueError(
                f"Requisito {requirement_id} ({requirement_label(requirement)}): "
                "la SOURCE non associa il valore al singolo dato e al soggetto. "
                f"Parole del campo assenti nell'estratto: {', '.join(missing_words) or 'nessuna'}. "
                "Copia un estratto contiguo che includa il contesto del ruolo e "
                "le parole del campo; non inventare o riscrivere il testo."
            )
        verified[requirement_id] = support
    return verified


def render_requirement_checks(
    requirements: list[Requirement], verified: dict[int, SourceSupport],
    *, searched_ids: set[int] | None = None,
) -> tuple[str, list[int], list[str]]:
    required, available, unverified, citations, missing = [], [], [], [], []
    not_searched = []
    for index, requirement in enumerate(requirements, start=1):
        label = requirement_label(requirement)
        required.append(f"- {label} [{requirement.form_citation_id}].")
        citations.append(requirement.form_citation_id)
        if searched_ids is not None and index not in searched_ids:
            not_searched.append(f"- {label}: non ricercato per limite di copertura/budget.")
            missing.append(f"{label} (non ricercato per limite di copertura/budget)")
        elif support := verified.get(index):
            available.append(
                f"- {label}: {support.value} [{support.source_citation_id}]. "
                "Valore riscontrato nelle fonti, utilizzabile per una prima compilazione."
            )
            citations.append(support.source_citation_id)
        else:
            unverified.append(f"- {label}: disponibilità non verificata nelle fonti.")
            missing.append(label)
    answer = "Requisiti del modulo:\n" + "\n".join(required)
    answer += "\n\nInformazioni verificate nelle fonti:\n" + (
        "\n".join(available) if available else "Nessun valore fattuale verificato."
    )
    answer += "\n\nInformazioni non ancora verificate:\n" + (
        "\n".join(unverified) if unverified else "Nessuna fra i requisiti qui analizzati."
    )
    if not_searched:
        answer += "\n\nRequisiti non ricercati:\n" + "\n".join(not_searched)
    if not verified:
        answer += (
            "\n\nPosso identificare dal modulo quali dati sono richiesti, ma non posso ancora "
            "considerarli compilabili perché non ho trovato fonti fattuali che ne attestino "
            "i valori."
        )
    answer += (
        "\n\nIl confronto riguarda solo i requisiti e le evidenze recuperati; "
        "non certifica la completezza del modulo né avvia una compilazione."
    )
    return answer, list(dict.fromkeys(citations)), missing
