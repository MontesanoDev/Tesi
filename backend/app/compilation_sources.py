"""Compilation-only semantic search names and local SOURCE/property bindings.

Search names never replace the grounded FORM requirement. They identify the
equivalent property in factual documents; values still need a literal SOURCE
span, the correct subject and the ordinary DOCX validation.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from app.generation import GenerationError
from app.requirement_checks import Requirement, contains_form_span, normalized
from app.source_planning import (
    MAX_CLUSTER_QUERIES,
    PlannedSourceSearch,
    SourceClusters,
    validate_source_plan,
)

MAX_SOURCE_NAMES = 3
MAX_ALLOWED_EVIDENCE = 8
logger = logging.getLogger(__name__)


class SourceMeaning(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    requirement_id: int = Field(ge=1, le=12)
    source_names: list[str] = Field(min_length=1, max_length=MAX_SOURCE_NAMES)


class CompilationSourcePlan(SourceClusters):
    fields: list[SourceMeaning] = Field(max_length=12)


@dataclass(frozen=True)
class CompilationSearch:
    plan: PlannedSourceSearch
    names: dict[int, list[str]]


async def plan_compilation_search(fields: list[dict], request) -> CompilationSearch:
    requirements = [Requirement.model_validate(f["requirement"]) for f in fields]
    fallback = validate_source_plan(SourceClusters(clusters=[]), requirements)
    names = {i: [r.name] for i, r in enumerate(requirements, 1)}
    contexts = list(dict.fromkeys(f["context"] for f in fields))
    try:
        proposed = await request(
            "Pianifica una ricerca SOURCE per i candidate DOCX già grounded nel FORM. "
            "Non proporre valori e non aggiungere requisiti. Raggruppa dati dello stesso "
            "soggetto/argomento: massimo 6 gruppi di 4 requirement_id, tutti una volta. "
            "Per ciascun requirement_id indica fino a 3 source_names: etichette brevi "
            "della stessa proprietà che una fonte fattuale può usare, semanticamente "
            "equivalenti nel contesto strutturale. Preferisci nomi sintetici di proprietà "
            "ai descrittori generici del modulo. Una label di ruolo/entità da compilare "
            "può chiedere l'identità/denominazione, non informazioni generiche sul ruolo. "
            "Non usare valori, nomi di aziende, persone, esempi o condizioni come etichette. "
            "Non trasformare una proprietà in un'altra: distingui sedi, soggetti, numeri "
            "e date. Le condizioni riguardano applicabilità, non cambiano il dato richiesto.",
            {"form_contexts": contexts, "requirements": [
                {"requirement_id": i, "requirement": f["requirement"],
                 "entity": f.get("entity"), "condition": f.get("condition", ""),
                 "semantic": f.get("semantic"),
                 "context_index": contexts.index(f["context"])}
                for i, f in enumerate(fields, 1)
            ]},
            CompilationSourcePlan,
        )
        plan = validate_source_plan(proposed, requirements)
        seen = set()
        for meaning in proposed.fields:
            if meaning.requirement_id > len(fields) or meaning.requirement_id in seen:
                raise ValueError("Mapping SOURCE con requirement_id sconosciuto/duplicato")
            seen.add(meaning.requirement_id)
            if any(not 2 <= len(name.strip()) <= 120 for name in meaning.source_names):
                raise ValueError("Etichetta SOURCE vuota o troppo ampia")
            names[meaning.requirement_id] = list(dict.fromkeys(
                [requirements[meaning.requirement_id - 1].name, *meaning.source_names]
            ))[:MAX_SOURCE_NAMES + 1]
    except (ValueError, GenerationError) as exc:
        logger.warning("DOCX SOURCE plan fallback error=%s", type(exc).__name__)
        # One bounded planning call. Failure preserves the literal labels and
        # explicit coverage limits; it never admits evidence or invents values.
        plan = fallback
        names = {i: [r.name] for i, r in enumerate(requirements, 1)}
    return CompilationSearch(plan, names)


def compilation_queries(cluster, requirements, names) -> list[str]:
    terms, alternatives = [], []
    for index in cluster.requirement_ids:
        requirement = requirements[index - 1]
        # Repeating the long FORM label beside every synonym gives generic
        # tender vocabulary disproportionate weight in a vector query. Search
        # the property name; the grounded original stays in matcher/validation.
        equivalent = sorted(dict.fromkeys(names[index]), key=lambda name: len(name.split()))
        terms.append(" ".join(filter(None, [requirement.person_role, equivalent[0]])))
        alternatives.append(" ".join(filter(None, [
            requirement.person_role, equivalent[min(1, len(equivalent) - 1)],
        ])))
    if len(terms) == 1:
        return list(dict.fromkeys([*terms, *alternatives]))
    size = 1 if len(terms) <= MAX_CLUSTER_QUERIES else 2
    return list(dict.fromkeys(" ".join(terms[start:start + size])
                             for start in range(0, len(terms), size)))


def company_property(field: dict, text: str, value: str | None = None) -> str | None:
    """Bind an equivalent header and value in the SAME local factual property.

    Colon-delimited properties are conservative, common documentary relations.
    A label elsewhere in the chunk cannot validate a different property's value.
    Other subjects/roles continue through the existing personal-data validator.
    """
    requirement = Requirement.model_validate(field["requirement"])
    if field.get("entity") != "company" or requirement.person_role:
        return None
    names = list(dict.fromkeys([
        requirement.name, *field.get("search", {}).get("source_names", []),
    ]))
    for line in re.split(r"\n|;", text):
        heading, separator, body = line.partition(":")
        if not separator or not body.strip():
            continue
        # Do not treat a distant paragraph as a property heading.
        if len(heading) > 180:
            continue
        for name in names:
            if contains_form_span(heading, name) and (
                value is None or contains_form_span(body, value)
            ):
                return name
    return None


def source_span(text: str, span: str) -> str:
    """Restore SOURCE spelling after deterministic Unicode/space normalization.

    No fuzzy matching or semantic paraphrase: the entire normalized span must
    occur contiguously. Offsets retain the original accents and whitespace.
    """
    chars, offsets = [], []
    for offset, char in enumerate(text):
        for part in unicodedata.normalize("NFKD", char.casefold()):
            if unicodedata.combining(part):
                continue
            if part.isspace():
                if not chars or chars[-1] == " ":
                    continue
                part = " "
            chars.append(part)
            offsets.append(offset)
    target = normalized(span)
    pattern = ((r"(?<!\w)" if target and target[0].isalnum() else "")
               + re.escape(target)
               + (r"(?!\w)" if target and target[-1].isalnum() else ""))
    match = re.search(pattern, "".join(chars)) if target else None
    if match is None:
        raise ValueError("Estratto/valore non presente nella SOURCE")
    start = match.start()
    return text[offsets[start]:offsets[start + len(target) - 1] + 1]
