from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.docx_templates import (
    SIGNATURE_LABEL,
    DocxLayout,
    field_value_error,
    is_email_label,
    is_signature_target,
    normalized,
)
from app.generation import GenerationError

MAX_RESPONSE_CHARACTERS = 200_000


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class Citation(StrictModel):
    source_id: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=1, max_length=3000)


class FieldProposal(StrictModel):
    cell_id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=250)
    entity: Literal["company", "person", "project", "authority", "other"]
    kind: Literal["data", "choice", "declaration", "signature"]
    status: Literal["proposed", "missing", "needs_review", "not_applicable"]
    value: str | None = Field(max_length=1500)
    evidence: list[Citation] = Field(max_length=8)
    reason: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def normalize_unwritten_metadata(cls, value: object) -> object:
        # Normalize display-only metadata without authorizing writes or inventing citations.
        if (
            isinstance(value, dict)
            and value.get("status") in ("missing", "needs_review", "not_applicable")
            and value.get("value") is None
        ):
            value = value.copy()
            value.setdefault("evidence", [])
            if (
                isinstance(value.get("label"), str)
                and not value["label"].strip()
                and isinstance(value.get("cell_id"), str)
            ):
                value["label"] = value["cell_id"]
        return value


class ModelProposals(StrictModel):
    fields: list[FieldProposal] = Field(max_length=400)
    warnings: list[str] = Field(max_length=40)


@dataclass(frozen=True)
class CompilationSources:
    selected: list[dict]
    total_chunks: int
    total_characters: int

    def coverage(self) -> dict:
        return {
            "total_chunks": self.total_chunks,
            "selected_chunks": len(self.selected),
            "total_characters": self.total_characters,
            "selected_characters": sum(len(item["content"]) for item in self.selected),
            "partial": len(self.selected) < self.total_chunks,
            "strategy": "bounded_spread_by_scope",
        }


def source_catalog(sources: CompilationSources, instructions: str = "") -> list[dict]:
    catalog = []
    for source in sources.selected:
        kind = source.get("source_kind", "source")
        origin = (
            "user" if kind == "project_facts"
            else "extracted" if kind == "call_facts" else "document"
        )
        catalog.append({**source, "source_kind": kind, "origin": origin})
    if instructions.strip():
        catalog.append({
            "id": "user:instructions",
            "document_id": None,
            "source_name": "Indicazioni dell'utente per questa compilazione",
            "chunk_index": None,
            "content": instructions.strip(),
            "scope": "user",
            "source_kind": "user_instructions",
            "origin": "user",
        })
    return catalog


def _complete_numeric_evidence(value: str, quote: str, source: str) -> bool:
    """Check numeric-bearing tokens against the source, even across quote edges.

    This is a lexical integrity check, not validation of tax IDs, dates or
    formatted amounts. Punctuation-delimited date components remain usable.
    """
    value, quote, source = normalized(value), normalized(quote), normalized(source)
    numeric_tokens = [
        token.span() for token in re.finditer(r"\w+", value)
        if any(char.isdigit() for char in token.group())
    ]
    if not numeric_tokens:
        return True
    # Lookaheads include overlapping occurrences. Test only occurrences inside
    # the actual cited span, not an unrelated occurrence elsewhere in the chunk.
    value_offsets = [match.start() for match in re.finditer(rf"(?={re.escape(value)})", quote)]
    for citation in re.finditer(rf"(?={re.escape(quote)})", source):
        for offset in value_offsets:
            start = citation.start() + offset
            if all(
                (start + left == 0 or not re.match(r"\w", source[start + left - 1]))
                and (start + right == len(source) or not re.match(r"\w", source[start + right]))
                for left, right in numeric_tokens
            ):
                return True
    return False


def _complete_email_evidence(value: str, quote: str, source: str) -> bool:
    """An abbreviated quote cannot hide the rest of an address in the source."""
    value, quote, source = normalized(value), normalized(quote), normalized(source)
    email_token = r"\w!#$%&'*+/=?^`{|}~@\-"
    complete_value = re.compile(
        rf"(?<![{email_token}.]){re.escape(value)}"
        rf"(?![{email_token}]|\.[\w-])",
    )
    occurrences = list(complete_value.finditer(source))
    return any(
        citation.start() <= occurrence.start()
        and occurrence.end() <= citation.start() + len(quote)
        for citation in re.finditer(rf"(?={re.escape(quote)})", source)
        for occurrence in occurrences
    )


def validate_proposals(
    content: str,
    layout: DocxLayout,
    sources: CompilationSources,
    *,
    instructions: str = "",
    explicit_user_values: dict[str, str] | None = None,
) -> dict:
    if len(content) > MAX_RESPONSE_CHARACTERS:
        raise GenerationError("La risposta di compilazione supera il limite supportato")
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
    try:
        proposals = ModelProposals.model_validate_json(cleaned)
    except (ValidationError, ValueError, RecursionError) as exc:
        raise GenerationError("Campi restituiti dal modello in un formato non valido") from exc
    source_map = {source["id"]: source for source in source_catalog(sources, instructions)}
    seen = set()
    fields = []
    for item in proposals.fields:
        if item.cell_id not in layout.candidate_ids or item.cell_id in seen:
            raise GenerationError(
                "Il modello indica un campo non scrivibile, sconosciuto o duplicato"
            )
        seen.add(item.cell_id)
        if item.status != "proposed" and item.value is not None:
            raise GenerationError("Un campo non compilabile contiene un valore inatteso")
        if item.status == "proposed" and not item.value:
            raise GenerationError("Un campo proposto non contiene un valore")
        evidence, rejected_evidence, checks, codes = [], [], [], []
        for citation in item.evidence:
            source = source_map.get(citation.source_id)
            if source is None:
                code, message = "unknown_source", "La fonte citata non e stata fornita"
            elif normalized(citation.quote) not in normalized(source["content"]):
                code, message = "invalid_quote", "La citazione non compare nella fonte indicata"
            else:
                code = None
            if code is not None:
                codes.append(code)
                checks.append(message)
                rejected_evidence.append({**citation.model_dump(), "reason": message})
                continue
            evidence.append(
                {
                    "source_id": source["id"],
                    "document_id": source["document_id"],
                    "source_name": source["source_name"],
                    "scope": source["scope"],
                    "source_kind": source["source_kind"],
                    "origin": source["origin"],
                    "fragment": (
                        source["chunk_index"] + 1 if source["chunk_index"] is not None else None
                    ),
                    "page": None,
                    "quote": citation.quote,
                    "content_sha256": hashlib.sha256(source["content"].encode()).hexdigest(),
                }
            )
        if item.status == "proposed":
            from app.compilation_semantics import empty_value_reason

            if error := empty_value_reason(item.value, item.label):
                checks.append(error)
                codes.append("empty_information")
            user_confirmed = (
                explicit_user_values is not None
                and explicit_user_values.get(item.cell_id) == item.value
                and any(c["source_id"] == "user:instructions" for c in evidence)
            )
            if (
                is_signature_target(layout, item.cell_id)
                or SIGNATURE_LABEL.search(item.label)
                or (not user_confirmed and (
                    item.kind != "data"
                    or normalized(item.value) in {"si", "sì", "no", "x", "true", "false", "n/a"}
                ))
            ):
                checks.append("Scelta, dichiarazione o firma: nessuna scrittura automatica")
                codes.append("protected_field")
            if not evidence or not any(
                normalized(item.value) in normalized(citation["quote"]) for citation in evidence
            ):
                checks.append("Il valore non compare letteralmente nelle evidenze citate")
                codes.append("value_not_in_quote")
            elif not any(
                _complete_numeric_evidence(
                    item.value, citation["quote"], source_map[citation["source_id"]]["content"],
                )
                for citation in evidence
            ):
                checks.append("Il valore ritaglia un numero o codice alfanumerico nella fonte")
                codes.append("partial_numeric_evidence")
            if evidence and item.entity in {"company", "person"} and not any(
                citation["scope"] != "general" for citation in evidence
            ):
                checks.append("La General KB non e una prova anagrafica aziendale")
                codes.append("general_only")
            if any(ord(c) < 32 and c not in "\n\r\t" for c in item.value):
                checks.append("Il valore contiene caratteri non supportati")
                codes.append("unsupported_characters")
            if error := field_value_error(layout, item.cell_id, item.value, label=item.label):
                codes.append(error[0])
                checks.append(error[1])
            elif (
                layout.field_types.get(item.cell_id) == "email" or is_email_label(item.label)
            ) and evidence:
                if not any(
                    _complete_email_evidence(
                        item.value, citation["quote"], source_map[citation["source_id"]]["content"],
                    )
                    for citation in evidence
                ):
                    codes.append("partial_email_evidence")
                    checks.append("Il recapito e solo una parte dell'indirizzo nella fonte citata")
        written = item.value if item.status == "proposed" and not checks else None
        fields.append(
            {
                **item.model_dump(exclude={"evidence"}),
                "status": "needs_review" if checks else item.status,
                "written_value": written,
                "location": layout.location(item.cell_id),
                "evidence": evidence,
                "rejected_evidence": rejected_evidence,
                "validation_notes": list(dict.fromkeys(checks)),
                "validation_codes": list(dict.fromkeys(codes)),
            }
        )
    classified = {field["cell_id"] for field in fields}
    return {
        "fields": fields,
        "unclassified_cells": sorted(set(layout.cells) - classified),
        "unclassified_fields": sorted(layout.candidate_ids - classified),
        "unsupported_locations": layout.unsupported_locations,
        "warnings": proposals.warnings,
    }
