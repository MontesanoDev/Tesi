from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=240)


class ProjectSummary(BaseModel):
    id: str
    title: str
    description: str
    status: str
    status_tone: str
    updated_label: str
    source_count: int
    model_count: int


class ProjectFile(BaseModel):
    id: int
    name: str
    metadata: str
    kind: str
    status: str
    page_count: int = 0
    chunk_count: int = 0


class GlobalKnowledgeDocument(BaseModel):
    id: int
    name: str
    metadata: str
    status: str
    mime_type: str
    byte_size: int
    page_count: int
    chunk_count: int


class GlobalKnowledgeOverview(BaseModel):
    documents: list[GlobalKnowledgeDocument]
    document_count: int
    chunk_count: int
    company_fact_count: int


class ProjectGlobalKnowledgeDocument(GlobalKnowledgeDocument):
    linked: bool


class GlobalKnowledgeLinkUpdate(BaseModel):
    linked: bool


class KnowledgeSource(BaseModel):
    id: int
    name: str
    detail: str
    scope: str
    tone: str
    item_count: int


class KnowledgeArtifactSummary(BaseModel):
    id: str
    kind: str
    scope: Literal["global", "project"]
    title: str
    filename: str
    status: str
    byte_size: int
    version: int
    updated_at: str
    editable: bool
    chunk_count: int


class KnowledgeArtifactDetail(KnowledgeArtifactSummary):
    content: str


class KnowledgeArtifactUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500_000)


class CallFactsExtractionResponse(BaseModel):
    artifact: KnowledgeArtifactDetail
    fact_count: int
    missing_count: int
    evidence_count: int
    model: str
    total_tokens: int | None


class CallFactSource(BaseModel):
    name: str
    fragment: int


class CallFactItem(BaseModel):
    id: str
    title: str
    value: str
    status: Literal["pending", "verified", "discarded"]
    sources: list[CallFactSource]


class CallFactsReview(BaseModel):
    artifact: KnowledgeArtifactDetail
    facts: list[CallFactItem]
    missing_information: list[str]
    pending_count: int
    verified_count: int
    discarded_count: int


class CallFactRevision(BaseModel):
    action: Literal["verify", "edit", "discard", "restore"]
    version: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    value: str | None = Field(default=None, min_length=1, max_length=4_000)


class DraftGenerationResponse(BaseModel):
    artifact: KnowledgeArtifactDetail
    verified_fact_count: int
    used_fact_count: int
    missing_information: list[str]
    model: str
    total_tokens: int | None


class Conversation(BaseModel):
    id: str
    title: str
    metadata: str
    target: str | None


class ProjectDetail(ProjectSummary):
    instructions: str
    call_fact_count: int
    missing_fact_count: int
    files: list[ProjectFile]
    knowledge_sources: list[KnowledgeSource]
    conversations: list[Conversation]


class DocumentField(BaseModel):
    id: int
    section: str
    label: str
    value: str | None
    provenance: str | None
    source_kind: str
    status: str


class DocumentReview(BaseModel):
    title: str
    subtitle: str
    completed_fields: int
    total_fields: int
    fields: list[DocumentField]


class Evidence(BaseModel):
    chunk_id: int
    file_id: int
    source_name: str
    chunk_index: int
    excerpt: str
    relevance: float


class ConversationTurn(BaseModel):
    id: int
    question: str
    answer: str | None
    citations: list[int]
    missing_information: list[str]
    evidence: list[Evidence]
    generation_status: Literal["completed", "direct", "not_configured", "no_evidence", "failed"]
    model: str | None
    total_tokens: int | None
    notice: str | None


class ConversationDetail(Conversation):
    project_id: str
    turns: list[ConversationTurn]


class EvidenceSearch(BaseModel):
    query: str
    results: list[Evidence]


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    conversation_id: str | None = Field(default=None, max_length=80)


class GroundedAnswerResponse(BaseModel):
    conversation_id: str
    turn_id: int
    question: str
    answer: str | None
    citations: list[int]
    missing_information: list[str]
    evidence: list[Evidence]
    generation_status: Literal["completed", "direct", "not_configured", "no_evidence", "failed"]
    model: str | None
    total_tokens: int | None
    notice: str | None
