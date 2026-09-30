"""Keep lexical and vector retrieval behind the same evidence contract."""

from app.ai_profiles import ProfileError
from app.repository import get_project
from app.repository import search_project_evidence as search_lexical_evidence
from app.retrieval_settings import RetrievalError, public_settings, resolve_settings
from app.vector_retrieval import run_vector_search


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
    if public_settings()["backend"] == "fts5":
        return search_lexical_evidence(project_id, query, limit, include_neighbors)
    try:
        settings = resolve_settings()
    except ProfileError as exc:
        raise RetrievalError(str(exc)) from None
    if settings.backend == "fts5":
        return search_lexical_evidence(project_id, query, limit, include_neighbors)
    return run_vector_search(settings, project_id, query, limit, include_neighbors)
