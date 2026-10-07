from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_QUESTION_LENGTH = 4_000


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=240)


class ProjectUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=120)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


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
    mime_type: str | None = None
    byte_size: int = 0
    page_count: int = 0
    chunk_count: int = 0


class ProjectFileContent(ProjectFile):
    content: str


class ProjectFileUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500_000)


class GlobalKnowledgeDocument(BaseModel):
    id: int
    name: str
    category: Literal["general", "company"]
    metadata: str
    status: str
    mime_type: str
    byte_size: int
    page_count: int
    chunk_count: int


class GlobalKnowledgeDocumentContent(GlobalKnowledgeDocument):
    content: str


class GlobalKnowledgeDocumentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500_000)


class GlobalKnowledgeOverview(BaseModel):
    documents: list[GlobalKnowledgeDocument]
    document_count: int
    chunk_count: int


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
    origin: Literal["extracted", "user_corrected"] = "extracted"


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
    available_fact_count: int
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
    role: Literal["form", "source"] = "source"
    project_id: str | None = None
    document_metadata: str = ""
    scope: str | None = None
    category: Literal["company", "general"] | None = None


class FormReference(BaseModel):
    form_id: int
    name: str


class CompilationChatAction(BaseModel):
    session_id: str
    action: Literal["start", "updated", "clarify", "generated", "deferred", "paused", "resumed"]


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
    form_reference: FormReference | None = None
    compilation: CompilationChatAction | None = None


class ConversationDetail(Conversation):
    project_id: str
    turns: list[ConversationTurn]
    form_reference: FormReference | None = None


class EvidenceSearch(BaseModel):
    query: str
    results: list[Evidence]


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=MAX_QUESTION_LENGTH)
    conversation_id: str | None = Field(default=None, max_length=80)
    form_id: int | None = Field(default=None, gt=0)
    compilation_session_id: str | None = Field(default=None, max_length=100)
    compilation_version: int | None = Field(default=None, ge=1)


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
    form_reference: FormReference | None = None
    compilation: CompilationChatAction | None = None
