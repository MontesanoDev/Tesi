"""Contracts for the backend-only, single-original compilation workflow."""

from typing import Literal

from pydantic import Field, model_validator

from app.document_compilation import StrictModel
from app.requirement_checks import Requirement

BATCH_SIZE = 12
RESOLUTION_TIMEOUT = 180
LEASE_SECONDS = 240
FieldStatus = Literal[
    "PENDING",
    "RESOLVED",
    "MISSING",
    "AMBIGUOUS",
    "CONFLICTING",
    "NOT_APPLICABLE",
    "USER_PROVIDED",
]


class CreateSession(StrictModel):
    form_id: int = Field(gt=0)
    conversation_id: str | None = Field(default=None, max_length=100)
    start_in_chat: bool = False


class RevisionRequest(StrictModel):
    version: int = Field(ge=1)


class ResolveRequest(RevisionRequest):
    field_ids: list[str] | None = Field(default=None, min_length=1, max_length=BATCH_SIZE)
    automatic: bool = False


class UserFieldInput(StrictModel):
    field_id: str = Field(min_length=1, max_length=80)
    action: Literal["set", "not_applicable", "reset"] = "set"
    value: str | None = Field(default=None, min_length=1, max_length=1500)
    reason: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def check_action(self):
        if (self.action == "set") != (self.value is not None):
            raise ValueError("Solo set richiede un valore")
        if self.action == "not_applicable" and not self.reason:
            raise ValueError("Indica perché il campo non è applicabile")
        return self


class UpdateFields(RevisionRequest):
    fields: list[UserFieldInput] = Field(min_length=1, max_length=BATCH_SIZE)


class FinalizeRequest(RevisionRequest):
    allow_unresolved: bool = False


class CandidateMeaning(StrictModel):
    candidate_id: str = Field(min_length=1, max_length=80)
    classification: Literal["data", "review", "decorative"]
    requirement: Requirement | None
    form_quote: str = Field(min_length=2, max_length=2000)
    entity: Literal["company", "person", "project", "authority", "other"] = "other"
    kind: Literal["data", "choice", "declaration", "signature"] = "data"
    # Exclusion is automatic only with an explicit, grounded SOURCE exclusion.
    condition: str = Field(default="", max_length=120)
    reason: str = Field(min_length=1, max_length=2000)


class CandidateMeanings(StrictModel):
    fields: list[CandidateMeaning] = Field(max_length=BATCH_SIZE)


class ValueSupport(StrictModel):
    source_id: int = Field(ge=1)
    quote: str = Field(min_length=2, max_length=800)
    value: str = Field(min_length=2, max_length=300)


class ApplicabilitySupport(ValueSupport):
    applies: bool


class CandidateMatch(StrictModel):
    candidate_id: str = Field(min_length=1, max_length=80)
    relationship: Literal["single", "alternatives", "conflict"] = "single"
    supports: list[ValueSupport] = Field(max_length=4)
    exclusion: ValueSupport | None = None
    applicability: list[ApplicabilitySupport] = Field(default_factory=list, max_length=4)
    reason: str = Field(min_length=1, max_length=2000)


class CandidateMatches(StrictModel):
    fields: list[CandidateMatch] = Field(max_length=BATCH_SIZE)
