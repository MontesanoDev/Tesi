from __future__ import annotations

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


class KnowledgeSource(BaseModel):
    id: int
    name: str
    detail: str
    scope: str
    tone: str
    item_count: int


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
