"""Bounded reusable SOURCE context, separate from approval of any proposed value."""

from app.db import connection
from app.repository import reload_evidence

MAX_PROFILE_CHARACTERS = 28_000
MAX_PROFILE_CHUNKS = 24


def profile_evidence(project_id):
    """Small company dossiers must not lose an address at a chunk boundary.

    These are search candidates, not verified facts. Property, subject, condition
    and literal evidence still traverse the ordinary matcher/reviewer/validator.
    General KB, templates, generated documents and other projects stay excluded.
    """
    with connection() as db:
        rows = db.execute(
            "SELECT -c.id chunk_id,-d.id file_id,c.chunk_index,1.0 relevance "
            "FROM global_document_chunks c JOIN global_documents d ON d.id=c.document_id "
            "WHERE d.category='company' ORDER BY d.id,c.chunk_index LIMIT ?",
            (MAX_PROFILE_CHUNKS,),
        ).fetchall()
        sources = reload_evidence(project_id, [dict(r) for r in rows], target="source", db=db)
    selected, size = [], 0
    for source in sources:
        if size + len(source["content"]) > MAX_PROFILE_CHARACTERS:
            break
        selected.append(source)
        size += len(source["content"])
    return selected


def reusable_evidence(fields):
    result = {}
    for field in fields:
        for item in [*field.get("source_evidence", []),
                     *(field.get("applicability") or {}).get("evidence", [])]:
            if item.get("role") == "source" and item.get("chunk_id") is not None:
                result[item["chunk_id"]] = item
    return list(result.values())


def semantic_context(field):
    """Only the reviewed contract can admit pooled evidence beyond lexical labels."""
    if not field.get("semantic"):
        return False
    from app.compilation_semantics import validate_persisted_semantics

    try:
        validate_persisted_semantics(field)
    except (ValueError, KeyError):
        return False
    return True
