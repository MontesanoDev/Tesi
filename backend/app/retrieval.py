"""Both search engines expose LangChain's Retriever -> list[Document] contract."""

from itertools import zip_longest

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from app.ai_profiles import ProfileError
from app.repository import _expand_neighbor_evidence, get_project
from app.repository import search_project_evidence as search_lexical_evidence
from app.retrieval_documents import document_evidence, evidence_document
from app.retrieval_settings import (
    RetrievalError,
    RetrievalSettings,
    public_settings,
    resolve_settings,
)
from app.vector_retrieval import run_vector_search


def merge_evidence_results(groups: list[list[dict]], limit: int = 8) -> list[dict]:
    """Alternate ranked results so each query gets space in the bounded context."""
    merged, seen = [], set()
    for row in zip_longest(*groups):
        for item in row:
            if item is None or item["chunk_id"] in seen:
                continue
            seen.add(item["chunk_id"])
            merged.append(item)
            if len(merged) == limit:
                return merged
    return merged


def expand_evidence_context(project_id: str, anchors: list[dict]) -> list[dict]:
    # Reserve context for neighboring text after merging queries. Merging eight
    # hits from each query first would crowd all neighbors out of the final list.
    return _expand_neighbor_evidence(project_id, anchors, max_results=8)


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
