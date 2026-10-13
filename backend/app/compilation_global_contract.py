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
    disposition: Literal["value", "not_applicable"]
    property: str | None = Field(default=None, min_length=1, max_length=150)


class CompactGlobalProposal(StrictModel):
    version: Literal[4]
    # Receipt/uncertainty only. The inverse clause map is derived by the backend
    # from each condition's grounded FORM origin, not supplied a second time.
    reviewed_paragraph_ids: list[Reference] = Field(max_length=2048)
    uncertain_paragraph_ids: list[Reference] = Field(max_length=2048)
    conditions: dict[Reference, ScopedCondition] = Field(max_length=128)
    fields: dict[Reference, AtomicField] = Field(max_length=128)
    # Explicitly accounted for, not silently defaulted to missing/decorative.
    deferred: list[Reference] = Field(max_length=400)
    facts: dict[Reference, SharedFact] = Field(max_length=128)


class ConditionTarget(StrictModel):
    kind: Literal["candidate", "paragraph", "table", "section"]
    id: Reference


class StructuralCondition(SharedCondition):
    # These are existing structural scopes, not alternative writable positions.
    scope: list[ConditionTarget] = Field(max_length=400)


class ValueAssignment(AtomicField):
    disposition: Literal["value"]
    fact_id: Reference
    property: str = Field(min_length=1, max_length=150)


class NonApplicableAssignment(AtomicField):
    disposition: Literal["not_applicable"]
    fact_id: None = None
    property: None = None
    choice: None = None


SparseAssignment = Annotated[
    ValueAssignment | NonApplicableAssignment, Field(discriminator="disposition"),
]


class SparseGlobalProposal(StrictModel):
    version: Literal[5]
    conditions: dict[Reference, StructuralCondition] = Field(max_length=128)
    # The structural inventory already bounds destinations; no second, smaller
    # partition budget can discard valid siblings before local validation.
    fields: dict[Reference, SparseAssignment] = Field(max_length=400)
    facts: dict[Reference, SharedFact] = Field(max_length=128)
    # Only substantive uncertainty; the model need not repeat the FORM inventory.
    uncertain_paragraph_ids: list[Reference] = Field(default_factory=list, max_length=2048)


class AlternativeAssignment(SharedField):
    """Grounded alternatives are proposals to review, never a chosen value."""

    disposition: Literal["review"]
    kind: Literal["data"]
    property: str = Field(min_length=1, max_length=150)
    review_kind: Literal["ambiguous", "conflicting"]
    alternative_fact_ids: list[Reference] = Field(min_length=2, max_length=4)
    fact_id: None = None
    choice: None = None
    reason: str = Field(min_length=1, max_length=200)


AlternativeAwareAssignment = Annotated[
    ValueAssignment | NonApplicableAssignment | AlternativeAssignment,
    Field(discriminator="disposition"),
]


class AlternativeAwareProposal(SparseGlobalProposal):
    version: Literal[6]
    fields: dict[Reference, AlternativeAwareAssignment] = Field(max_length=400)


class SubjectBinding(StrictModel):
    """Proposed role association, with independently reloaded FORM/SOURCE spans."""

    form: FormSpan
    required_role: str = Field(min_length=2, max_length=150)
    source_role: str = Field(min_length=2, max_length=150)
    evidence: list[SourceSpan] = Field(min_length=1, max_length=2)


class SubjectBoundValue(ValueAssignment):
    # Required by the backend for person facts, whose entity is in another record.
    binding_id: Reference | None = None


SubjectBoundAssignment = Annotated[
    SubjectBoundValue | NonApplicableAssignment | AlternativeAssignment,
    Field(discriminator="disposition"),
]


class SubjectBoundProposal(AlternativeAwareProposal):
    version: Literal[7]
    bindings: dict[Reference, SubjectBinding] = Field(default_factory=dict, max_length=128)
    fields: dict[Reference, SubjectBoundAssignment] = Field(max_length=400)


class ConditionalValue(SubjectBoundValue):
    """Documented data whose destination still depends on an unknown condition.

    This is never a selected/writable value or evidence that the condition holds.
    """

    disposition: Literal["conditional"]
    kind: Literal["data", "choice"]
    conditions: list[Reference] = Field(min_length=1, max_length=8)
    reason: str = Field(min_length=1, max_length=200)


ConditionalAssignment = Annotated[
    SubjectBoundValue | NonApplicableAssignment | AlternativeAssignment | ConditionalValue,
    Field(discriminator="disposition"),
]


class ConditionalAwareProposal(SubjectBoundProposal):
    version: Literal[8]
    fields: dict[Reference, ConditionalAssignment] = Field(max_length=400)


class SlotAwareProposal(ConditionalAwareProposal):
    """Inline field FORM quotes include their canonical destination marker.

    This proves quote location, not semantic entailment of a proposed value.
    Historical envelopes keep their original validation behavior.
    """

    version: Literal[9]


class ContextAwareProposal(SlotAwareProposal):
    """Bounded FORM continuations and explicit SOURCE personal record formats."""

    version: Literal[10]


class ChoiceOption(StrictModel):
    label: str = Field(min_length=1, max_length=250)
    form: FormSpan


class ChoiceGroup(StrictModel):
    """Proposed semantics; the backend owns physical controls and cardinality."""

    label: str = Field(min_length=1, max_length=250)
    subject: str = Field(min_length=1, max_length=150)
    property: str = Field(min_length=1, max_length=150)
    form: FormSpan
    selection: Literal["single", "multiple", "unknown"]
    min_selected: int = Field(ge=0, le=1)
    options: dict[Reference, ChoiceOption] = Field(min_length=1, max_length=32)
    conditions: list[Reference] = Field(default_factory=list, max_length=8)


class ChoiceValue(SubjectBoundValue):
    choice_group_id: Reference | None = None


class ChoiceConditionalValue(ConditionalValue):
    choice_group_id: Reference | None = None


class UserFieldRequest(StrictModel):
    """A local FORM question, never proof of a value or of source absence."""

    label: str = Field(min_length=1, max_length=250)
    form: FormSpan
    conditions: list[Reference] = Field(default_factory=list, max_length=8)
    reason: str = Field(min_length=1, max_length=200)


ChoiceAssignment = Annotated[
    ChoiceValue | ChoiceConditionalValue | NonApplicableAssignment | AlternativeAssignment,
    Field(discriminator="disposition"),
]


class ChoiceAwareProposal(ContextAwareProposal):
    version: Literal[11]
    choice_groups: dict[Reference, ChoiceGroup] = Field(default_factory=dict, max_length=64)
    fields: dict[Reference, ChoiceAssignment] = Field(max_length=400)
    clarifications: dict[Reference, UserFieldRequest] = Field(default_factory=dict, max_length=16)


class UnfilledExplanation(StrictModel):
    """Model reasoning about unwritten positions, never a factual value or write permission."""

    candidate_ids: list[Reference] = Field(min_length=1, max_length=400)
    outcome: Literal["source_not_found", "condition_unknown", "not_applicable",
                     "not_a_field", "manual_input", "unassessed"]
    reason: str = Field(min_length=4, max_length=300)
    form: FormSpan | None = None
    conditions: list[Reference] = Field(default_factory=list, max_length=8)


class CoverageAwareProposal(ChoiceAwareProposal):
    version: Literal[12]
    coverage: list[UnfilledExplanation] = Field(max_length=400)
