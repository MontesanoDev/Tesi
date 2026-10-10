"""Versioned experimental output: shared SOURCE facts and FORM conditions.

These records are model proposals, including their semantic metadata. Predicate
evaluation is a necessary local check, never independent semantic acceptance.
"""

from typing import Annotated, Literal

from pydantic import Field

from app.document_compilation import StrictModel

Aspect = Literal[
    "identity", "legal_type", "location", "participation", "representation",
    "professional", "other",
]
Reference = Annotated[str, Field(min_length=1, max_length=80)]


class FormSpan(StrictModel):
    paragraph_id: str = Field(min_length=1, max_length=80)
    quote: str = Field(max_length=500)


class SourceSpan(StrictModel):
    chunk_id: int
    quote: str = Field(min_length=1, max_length=800)


class SharedFact(StrictModel):
    subject: str = Field(min_length=1, max_length=150)
    entity: Literal["company", "person", "project", "authority", "other"]
    aspect: Aspect
    property: str = Field(min_length=1, max_length=150)
    value: str = Field(min_length=1, max_length=1500)
    evidence: list[SourceSpan] = Field(min_length=1, max_length=2)


class SharedCondition(StrictModel):
    form: FormSpan
    aspect: Aspect
    operator: Literal["same", "different", "semantic"]
    fact_ids: list[Reference] = Field(max_length=2)
    reason: str = Field(min_length=1, max_length=250)


class SharedField(StrictModel):
    label: str = Field(min_length=1, max_length=250)
    kind: Literal["data", "choice", "declaration", "signature", "decorative"]
    disposition: Literal["value", "missing", "review", "not_applicable", "ignore"]
    form: FormSpan
    # Empty explicitly means no condition proposed, not proof of completeness.
    conditions: list[Reference] = Field(max_length=8)
    fact_id: Reference | None = None
    choice: bool | None = None
    reason: str = Field(default="", max_length=200)


class SharedGlobalProposal(StrictModel):
    version: Literal[2]
    facts: dict[Reference, SharedFact] = Field(max_length=128)
    conditions: dict[Reference, SharedCondition] = Field(max_length=128)
    fields: dict[Reference, SharedField] = Field(max_length=400)


class ScopedCondition(SharedCondition):
    # Semantic scope is proposed by the model, never a new structural location.
    applies_to: list[Reference] = Field(max_length=400)


class AtomicField(SharedField):
    property: str | None = Field(default=None, min_length=1, max_length=150)


class CompactGlobalProposal(StrictModel):
    version: Literal[3]
    facts: dict[Reference, SharedFact] = Field(max_length=128)
    conditions: dict[Reference, ScopedCondition] = Field(max_length=128)
    # Every nonempty FORM paragraph: [] = no clause proposed, null = uncertain.
    # Exact coverage is checked against the catalog, not a model count.
    condition_scan: dict[Reference, list[Reference] | None] = Field(max_length=2048)
    fields: dict[Reference, AtomicField] = Field(max_length=128)
    # Explicitly accounted for, not silently defaulted to missing/decorative.
    deferred: list[Reference] = Field(max_length=400)
