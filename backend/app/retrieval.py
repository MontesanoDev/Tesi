"""Both search engines expose LangChain's Retriever -> list[Document] contract."""

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from app.ai_profiles import ProfileError
from app.repository import get_project
from app.repository import search_project_evidence as search_lexical_evidence
from app.retrieval_documents import document_evidence, evidence_document
from app.retrieval_settings import (
    RetrievalError,
    RetrievalSettings,
    public_settings,
    resolve_settings,
)
from app.vector_retrieval import run_vector_search


class ProjectRetriever(BaseRetriever):
    project_id: str
    limit: int = Field(default=4, ge=1, le=8)
    include_neighbors: bool = False


class FTS5Retriever(ProjectRetriever):
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        evidence = search_lexical_evidence(
            self.project_id,
            query,
            self.limit,
            self.include_neighbors,
        )
        return [evidence_document(item) for item in evidence or []]


class QdrantEvidenceRetriever(ProjectRetriever):
    settings: RetrievalSettings = Field(exclude=True, repr=False)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        if not query.strip() or get_project(self.project_id) is None:
            return []
        return run_vector_search(
            self.settings,
            self.project_id,
            query,
            self.limit,
            self.include_neighbors,
        )


def build_retriever(
    project_id: str,
    limit: int = 4,
    include_neighbors: bool = False,
) -> BaseRetriever:
    options = dict(project_id=project_id, limit=limit, include_neighbors=include_neighbors)
    # FTS5 remains usable even if an old embedding credential cannot be decrypted.
    if public_settings()["backend"] == "fts5":
        return FTS5Retriever(**options)
    try:
        settings = resolve_settings()
    except ProfileError as exc:
        raise RetrievalError(str(exc)) from None
    if settings.backend == "fts5":
        return FTS5Retriever(**options)
    return QdrantEvidenceRetriever(settings=settings, **options)


def search_project_evidence(
    project_id: str,
    query: str,
    limit: int = 4,
    include_neighbors: bool = False,
) -> list[dict] | None:
    if get_project(project_id) is None:
        return None
    if not query.strip():
        return []
    documents = build_retriever(project_id, limit, include_neighbors).invoke(query)
    return [document_evidence(document) for document in documents]
