from __future__ import annotations

import re
import sqlite3
import unicodedata
from uuid import uuid4

from app.db import connection
from app.schemas import ProjectCreate


def _rows(db: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in db.execute(query, params).fetchall()]


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"progetto-{uuid4().hex[:8]}"


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
            SELECT id, name, metadata, kind, status
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
