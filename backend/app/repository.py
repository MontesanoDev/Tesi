from __future__ import annotations

import re
import sqlite3
import unicodedata
from uuid import uuid4

from app.db import connection
from app.ingestion import IngestedDocument
from app.schemas import ProjectCreate

SEARCH_STOP_WORDS = {
    "che",
    "chi",
    "come",
    "con",
    "cosa",
    "dei",
    "del",
    "della",
    "delle",
    "gli",
    "nel",
    "nella",
    "per",
    "qual",
    "quale",
    "quali",
    "sono",
    "una",
}
TEMPORAL_QUERY_TERMS = {
    "data",
    "date",
    "entro",
    "quando",
    "scadenza",
    "scadenze",
    "termine",
    "termini",
}
DATE_PATTERN = re.compile(r"\b(?:\d{1,2}[./-]){2}\d{2,4}\b")
TIME_PATTERN = re.compile(r"\bore\s+\d{1,2}(?:[.:]\d{2})?", flags=re.IGNORECASE)


def _rows(db: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in db.execute(query, params).fetchall()]


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"progetto-{uuid4().hex[:8]}"


def _format_size(byte_size: int) -> str:
    if byte_size >= 1024 * 1024:
        return f"{byte_size / (1024 * 1024):.1f} MB".replace(".0 ", " ")
    if byte_size >= 1024:
        return f"{round(byte_size / 1024)} KB"
    return f"{byte_size} B"


def _build_fts_query(query: str) -> str:
    tokens = re.findall(r"[^\W_]+", query.lower(), flags=re.UNICODE)
    meaningful = [
        token
        for token in tokens
        if token not in SEARCH_STOP_WORDS
        and (len(token) >= 3 or any(char.isdigit() for char in token))
    ]
    terms = []
    for token in dict.fromkeys(meaningful):
        if len(token) >= 5 and token[-1] in "aeiou":
            terms.append(f'"{token[:-1]}"*')
        else:
            terms.append(f'"{token}"')
    return " OR ".join(terms)


def _rerank_evidence(query: str, candidates: list[dict], limit: int) -> list[dict]:
    query_tokens = set(re.findall(r"[^\W_]+", query.lower(), flags=re.UNICODE))
    temporal_query = bool(query_tokens & TEMPORAL_QUERY_TERMS)

    for candidate in candidates:
        relevance = -candidate.pop("rank")
        content = candidate["content"]
        if temporal_query:
            if DATE_PATTERN.search(content):
                relevance += 3.0
            if TIME_PATTERN.search(content):
                relevance += 1.5
        candidate["relevance"] = round(relevance, 6)
    candidates.sort(key=lambda item: item["relevance"], reverse=True)

    selected: list[dict] = []
    deferred: list[dict] = []
    for candidate in candidates:
        duplicates_adjacent_chunk = any(
            item["file_id"] == candidate["file_id"]
            and abs(item["chunk_index"] - candidate["chunk_index"]) <= 1
            for item in selected
        )
        if duplicates_adjacent_chunk:
            deferred.append(candidate)
        elif len(selected) < limit:
            selected.append(candidate)
    if len(selected) < limit:
        selected.extend(deferred[: limit - len(selected)])
    return selected


def list_projects() -> list[dict]:
    with connection() as db:
        return _rows(
            db,
            """
            SELECT
                p.id, p.title, p.description, p.status, p.status_tone,
                p.updated_label, p.shared_source_count AS source_count,
                p.model_count
            FROM projects p
            ORDER BY p.rowid
            """,
        )


def get_project(project_id: str) -> dict | None:
    with connection() as db:
        project = db.execute(
            """
            SELECT
                p.*,
                p.shared_source_count AS source_count
            FROM projects p
            WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()
        if project is None:
            return None

        result = dict(project)
        result["files"] = _rows(
            db,
            """
            SELECT id, name, metadata, kind, status, page_count, chunk_count
            FROM project_files WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
        result["knowledge_sources"] = _rows(
            db,
            """
            SELECT id, name, detail, scope, tone, item_count
            FROM knowledge_sources WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
        result["conversations"] = _rows(
            db,
            """
            SELECT id, title, metadata, target
            FROM conversations WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
        return result


def create_project(payload: ProjectCreate) -> dict:
    base_id = _slugify(payload.title)
    with connection() as db:
        project_id = base_id
        suffix = 2
        while db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            project_id = f"{base_id}-{suffix}"
            suffix += 1
        db.execute(
            """
            INSERT INTO projects (
                id, title, description, status, status_tone, updated_label,
                instructions, shared_source_count, model_count,
                call_fact_count, missing_fact_count
            ) VALUES (?, ?, ?, 'In configurazione', 'info', 'Aggiornato ora',
                      'Usa solo informazioni presenti nelle fonti.', 0, 0, 0, 0)
            """,
            (project_id, payload.title, payload.description),
        )
    project = get_project(project_id)
    if project is None:
        raise RuntimeError("Il progetto appena creato non e stato trovato")
    return project


def add_project_file(project_id: str, document: IngestedDocument) -> dict | None:
    chunk_count = len(document.chunks)
    chunk_label = "frammento" if chunk_count == 1 else "frammenti"
    file_type = "PDF" if document.mime_type == "application/pdf" else "TXT"
    metadata = f"{file_type} · {_format_size(document.byte_size)} · {chunk_count} {chunk_label}"

    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        sort_order = db.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM project_files WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        cursor = db.execute(
            """
            INSERT INTO project_files (
                project_id, name, metadata, kind, status, storage_path,
                mime_type, byte_size, page_count, chunk_count, sort_order
            ) VALUES (?, ?, ?, 'source', 'Indicizzato', ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                document.name,
                metadata,
                document.storage_path,
                document.mime_type,
                document.byte_size,
                document.page_count,
                chunk_count,
                sort_order,
            ),
        )
        file_id = cursor.lastrowid
        if file_id is None:
            raise RuntimeError("Il file indicizzato non ha ricevuto un identificativo")
        db.executemany(
            """
            INSERT INTO document_chunks (
                project_id, file_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (project_id, file_id, index, content, len(content))
                for index, content in enumerate(document.chunks)
            ],
        )
        db.execute(
            """
            UPDATE projects
            SET shared_source_count = shared_source_count + 1,
                updated_label = 'Aggiornato ora'
            WHERE id = ?
            """,
            (project_id,),
        )
        row = db.execute(
            """
            SELECT id, name, metadata, kind, status, page_count, chunk_count
            FROM project_files WHERE id = ?
            """,
            (file_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def search_project_evidence(project_id: str, query: str, limit: int = 4) -> list[dict] | None:
    fts_query = _build_fts_query(query)
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        if not fts_query:
            return []
        candidates = _rows(
            db,
            """
            SELECT
                c.id AS chunk_id,
                c.file_id,
                f.name AS source_name,
                c.chunk_index,
                c.content,
                snippet(document_chunks_fts, 2, '', '', ' … ', 36) AS excerpt,
                bm25(document_chunks_fts) AS rank
            FROM document_chunks_fts
            JOIN document_chunks c ON c.id = document_chunks_fts.rowid
            JOIN project_files f ON f.id = c.file_id
            WHERE document_chunks_fts MATCH ? AND c.project_id = ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, project_id, max(limit * 6, 24)),
        )
    return _rerank_evidence(query, candidates, limit)


def get_document_review(project_id: str) -> dict | None:
    project = get_project(project_id)
    if project is None:
        return None
    with connection() as db:
        fields = _rows(
            db,
            """
            SELECT id, section, label, value, provenance, source_kind, status
            FROM document_fields WHERE project_id = ? ORDER BY sort_order
            """,
            (project_id,),
        )
    completed = sum(field["status"] != "missing" for field in fields)
    return {
        "title": "Modulo di candidatura A",
        "subtitle": "Bozza generata dal modello ufficiale",
        "completed_fields": completed,
        "total_fields": len(fields),
        "fields": fields,
    }
