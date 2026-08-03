from __future__ import annotations

import hashlib
from pathlib import Path

from app.db import connection, get_knowledge_path
from app.ingestion import chunk_text


class ArtifactReadOnlyError(ValueError):
    pass


GLOBAL_ARTIFACTS = (
    ("general-kb", "general_kb", "General KB", "general-kb.md", "Da configurare"),
    (
        "company-facts",
        "company_facts",
        "Company Facts",
        "company-facts.md",
        "Verificato",
    ),
)
PROJECT_ARTIFACTS = (
    ("call-facts", "call_facts", "Call Facts", "call-facts.md", "Da estrarre"),
    (
        "project-facts",
        "project_facts",
        "Project Facts",
        "project-facts.md",
        "Bozza",
    ),
    ("template", "template", "Template", "template.md", "Da configurare"),
)


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _artifact_path(relative_path: str) -> Path:
    root = get_knowledge_path().resolve()
    path = (root / relative_path).resolve()
    if path != root and root not in path.parents:
        raise ValueError("Percorso dell'artefatto non valido")
    return path


def _write_artifact(relative_path: str, content: str) -> None:
    path = _artifact_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _read_artifact(relative_path: str) -> str:
    return _artifact_path(relative_path).read_text(encoding="utf-8")


def _frontmatter(kind: str, scope: str, project_id: str | None, status: str) -> str:
    project_line = f"project: {project_id}\n" if project_id else ""
    return (
        "---\n"
        f"artifact: {kind}\n"
        f"scope: {scope}\n"
        f"{project_line}"
        f"status: {status.lower().replace(' ', '_')}\n"
        "---\n"
    )


def _global_content(kind: str, company_facts: list[dict]) -> str:
    if kind == "company_facts":
        sections = "\n\n".join(f"## {fact['label']}\n\n{fact['value']}" for fact in company_facts)
        return (
            f"{_frontmatter(kind, 'global', None, 'Verificato')}\n"
            "# Company Facts\n\n"
            "Dati aziendali verificati e condivisi tra i progetti.\n\n"
            f"{sections}\n"
        )
    return (
        f"{_frontmatter(kind, 'global', None, 'Da configurare')}\n"
        "# General KB\n\n"
        "> Aggiungere qui norme, procedure e conoscenze tecniche condivise.\n"
    )


def _project_content(kind: str, project: dict) -> str:
    project_id = project["id"]
    if kind == "project_facts":
        body = (
            "# Project Facts\n\n"
            "## Titolo\n\n"
            f"{project['title']}\n\n"
            "## Descrizione\n\n"
            f"{project['description']}\n"
        )
        status = "Bozza"
    elif kind == "call_facts":
        body = (
            "# Call Facts\n\n"
            "> I fatti estratti dalle fonti del progetto compariranno qui "
            "con la loro provenienza.\n"
        )
        status = "Da estrarre"
    else:
        body = "# Template\n\n> Definire qui la struttura Markdown dell'output atteso.\n"
        status = "Da configurare"
    return f"{_frontmatter(kind, 'project', project_id, status)}\n{body}"


def _metadata(byte_size: int, version: int, scope: str) -> str:
    size = f"{max(1, round(byte_size / 1024))} KB"
    scope_label = "globale" if scope == "global" else "progetto"
    return f"Markdown · {size} · v{version} · {scope_label}"


def _replace_chunks(
    db,
    project_id: str,
    file_id: int,
    content: str,
    indexed: bool,
) -> int:
    db.execute("DELETE FROM document_chunks WHERE file_id = ?", (file_id,))
    chunks = chunk_text(content) if indexed else []
    db.executemany(
        """
        INSERT INTO document_chunks (
            project_id, file_id, chunk_index, content, char_count
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [(project_id, file_id, index, chunk, len(chunk)) for index, chunk in enumerate(chunks)],
    )
    return len(chunks)


def _link_artifact(db, project_id: str, artifact: dict, content: str) -> None:
    existing = db.execute(
        """
        SELECT file_id FROM project_artifact_links
        WHERE project_id = ? AND artifact_id = ?
        """,
        (project_id, artifact["id"]),
    ).fetchone()
    indexed = artifact["status"] not in {"Da configurare", "Da estrarre"}
    file_status = "Indicizzato" if indexed else "Da compilare"
    if existing is None:
        sort_order = db.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM project_files WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        cursor = db.execute(
            """
            INSERT INTO project_files (
                project_id, name, metadata, kind, status, storage_path,
                mime_type, byte_size, page_count, chunk_count, sort_order
            ) VALUES (?, ?, ?, 'artifact', ?, ?, 'text/markdown', ?, 1, 0, ?)
            """,
            (
                project_id,
                artifact["filename"],
                _metadata(artifact["byte_size"], artifact["version"], artifact["scope"]),
                file_status,
                artifact["storage_path"],
                artifact["byte_size"],
                sort_order,
            ),
        )
        file_id = cursor.lastrowid
        if file_id is None:
            raise RuntimeError("L'artefatto non ha ricevuto un file indicizzabile")
        db.execute(
            """
            INSERT INTO project_artifact_links (project_id, artifact_id, file_id)
            VALUES (?, ?, ?)
            """,
            (project_id, artifact["id"], file_id),
        )
    else:
        file_id = existing["file_id"]

    chunk_count = _replace_chunks(db, project_id, file_id, content, indexed)
    db.execute(
        """
        UPDATE project_files
        SET name = ?, metadata = ?, status = ?, storage_path = ?,
            byte_size = ?, chunk_count = ?
        WHERE id = ?
        """,
        (
            artifact["filename"],
            _metadata(artifact["byte_size"], artifact["version"], artifact["scope"]),
            file_status,
            artifact["storage_path"],
            artifact["byte_size"],
            chunk_count,
            file_id,
        ),
    )


def _insert_artifact(
    db,
    artifact_id: str,
    project_id: str | None,
    kind: str,
    scope: str,
    title: str,
    filename: str,
    relative_path: str,
    status: str,
    content: str,
) -> dict:
    existing = db.execute(
        "SELECT * FROM knowledge_artifacts WHERE id = ?",
        (artifact_id,),
    ).fetchone()
    if existing is None:
        _write_artifact(relative_path, content)
        db.execute(
            """
            INSERT INTO knowledge_artifacts (
                id, project_id, kind, scope, title, filename, storage_path,
                status, content_hash, byte_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact_id,
                project_id,
                kind,
                scope,
                title,
                filename,
                relative_path,
                status,
                _content_hash(content),
                len(content.encode("utf-8")),
            ),
        )
        existing = db.execute(
            "SELECT * FROM knowledge_artifacts WHERE id = ?",
            (artifact_id,),
        ).fetchone()
    else:
        try:
            content = _read_artifact(existing["storage_path"])
        except FileNotFoundError:
            _write_artifact(existing["storage_path"], content)
        actual_hash = _content_hash(content)
        if actual_hash != existing["content_hash"]:
            db.execute(
                """
                UPDATE knowledge_artifacts
                SET status = 'Modifica esterna', content_hash = ?, byte_size = ?,
                    version = version + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (actual_hash, len(content.encode("utf-8")), artifact_id),
            )
            existing = db.execute(
                "SELECT * FROM knowledge_artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()
    return dict(existing)


def _ensure_project_artifacts(db, project: dict, company_facts: list[dict]) -> None:
    project_id = project["id"]
    for slug, kind, title, filename, status in GLOBAL_ARTIFACTS:
        artifact_id = f"global--{slug}"
        artifact = _insert_artifact(
            db,
            artifact_id,
            None,
            kind,
            "global",
            title,
            filename,
            f"global/{filename}",
            status,
            _global_content(kind, company_facts),
        )
        _link_artifact(db, project_id, artifact, _read_artifact(artifact["storage_path"]))

    for slug, kind, title, filename, status in PROJECT_ARTIFACTS:
        artifact_id = f"{project_id}--{slug}"
        artifact = _insert_artifact(
            db,
            artifact_id,
            project_id,
            kind,
            "project",
            title,
            filename,
            f"projects/{project_id}/{filename}",
            status,
            _project_content(kind, project),
        )
        _link_artifact(db, project_id, artifact, _read_artifact(artifact["storage_path"]))


def seed_markdown_artifacts() -> None:
    with connection() as db:
        company_facts = [
            dict(row)
            for row in db.execute(
                """
                SELECT key, label, value FROM company_facts
                WHERE verified = 1 ORDER BY sort_order
                """
            ).fetchall()
        ]
        projects = [dict(row) for row in db.execute("SELECT * FROM projects").fetchall()]
        for project in projects:
            _ensure_project_artifacts(db, project, company_facts)


def ensure_project_artifacts(project_id: str) -> None:
    with connection() as db:
        project = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if project is None:
            return
        company_facts = [
            dict(row)
            for row in db.execute(
                """
                SELECT key, label, value FROM company_facts
                WHERE verified = 1 ORDER BY sort_order
                """
            ).fetchall()
        ]
        _ensure_project_artifacts(db, dict(project), company_facts)


def list_project_artifacts(project_id: str) -> list[dict] | None:
    with connection() as db:
        if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            return None
        return [
            dict(row)
            for row in db.execute(
                """
                SELECT
                    a.id, a.kind, a.scope, a.title, a.filename, a.status,
                    a.byte_size, a.version, a.updated_at,
                    CASE WHEN a.project_id = ? THEN 1 ELSE 0 END AS editable,
                    f.chunk_count
                FROM project_artifact_links l
                JOIN knowledge_artifacts a ON a.id = l.artifact_id
                JOIN project_files f ON f.id = l.file_id
                WHERE l.project_id = ?
                ORDER BY
                    CASE a.scope WHEN 'project' THEN 0 ELSE 1 END,
                    CASE a.kind
                        WHEN 'call_facts' THEN 0
                        WHEN 'project_facts' THEN 1
                        WHEN 'template' THEN 2
                        WHEN 'company_facts' THEN 3
                        ELSE 4
                    END
                """,
                (project_id, project_id),
            ).fetchall()
        ]


def get_project_artifact(project_id: str, artifact_id: str) -> dict | None:
    with connection() as db:
        row = db.execute(
            """
            SELECT
                a.*, CASE WHEN a.project_id = ? THEN 1 ELSE 0 END AS editable,
                f.chunk_count
            FROM project_artifact_links l
            JOIN knowledge_artifacts a ON a.id = l.artifact_id
            JOIN project_files f ON f.id = l.file_id
            WHERE l.project_id = ? AND a.id = ?
            """,
            (project_id, project_id, artifact_id),
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["content"] = _read_artifact(result["storage_path"])
    return result


def update_project_artifact(project_id: str, artifact_id: str, content: str) -> dict | None:
    with connection() as db:
        row = db.execute(
            """
            SELECT a.* FROM project_artifact_links l
            JOIN knowledge_artifacts a ON a.id = l.artifact_id
            WHERE l.project_id = ? AND a.id = ?
            """,
            (project_id, artifact_id),
        ).fetchone()
        if row is None:
            return None
        artifact = dict(row)
        if artifact["project_id"] != project_id:
            raise ArtifactReadOnlyError(
                "L'artefatto globale va modificato dalle impostazioni generali"
            )

        _write_artifact(artifact["storage_path"], content)
        byte_size = len(content.encode("utf-8"))
        db.execute(
            """
            UPDATE knowledge_artifacts
            SET status = 'Bozza aggiornata', content_hash = ?, byte_size = ?,
                version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (_content_hash(content), byte_size, artifact_id),
        )
        updated = dict(
            db.execute(
                "SELECT * FROM knowledge_artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()
        )
        links = db.execute(
            "SELECT project_id FROM project_artifact_links WHERE artifact_id = ?",
            (artifact_id,),
        ).fetchall()
        for link in links:
            _link_artifact(db, link["project_id"], updated, content)

    return get_project_artifact(project_id, artifact_id)


def get_company_markdown() -> str | None:
    with connection() as db:
        row = db.execute(
            "SELECT storage_path FROM knowledge_artifacts WHERE id = 'global--company-facts'"
        ).fetchone()
    if row is None:
        return None
    try:
        return _read_artifact(row["storage_path"])
    except FileNotFoundError:
        return None
