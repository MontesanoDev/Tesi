from __future__ import annotations

import json
from pathlib import Path
from shutil import rmtree
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app.db import connection, get_storage_path, touch_project
from app.document_compilation import compile_document
from app.docx_templates import MAX_DOCX_BYTES, DocumentInputError, DocxTooLargeError
from app.generation import GenerationError, GenerationNotConfiguredError
from app.repository import get_project

router = APIRouter(
    prefix="/api/projects/{project_id}/document-compilations", tags=["Compilazione DOCX"]
)
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _payload(row: dict, *, include_report: bool = True) -> dict:
    base = f"/api/projects/{row['project_id']}/document-compilations/{row['id']}"
    result = {
        "id": row["id"],
        "project_id": row["project_id"],
        "template_name": row["template_name"],
        "created_at": row["created_at"],
        "status": "needs_review",
        "downloads": {kind: f"{base}/download/{kind}" for kind in ("docx", "report", "template")},
    }
    if include_report:
        result["report"] = json.loads(row["report_json"])
    return result


def _persist(project_id: str, filename: str, template: bytes, draft: bytes, report: dict) -> dict:
    run_id = uuid4().hex
    root = get_storage_path().resolve()
    folder = (root / project_id / "_compilations" / run_id).resolve()
    if root not in folder.parents:
        raise DocumentInputError("Percorso del progetto non valido")
    report_json = json.dumps(report, ensure_ascii=False, indent=2)
    created = False
    try:
        with connection() as db:
            # Serialize the final save with project deletion; recheck after the LLM call.
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail="Il progetto e stato eliminato")
            folder.mkdir(parents=True, exist_ok=False)
            created = True
            (folder / "template.docx").write_bytes(template)
            (folder / "bozza.docx").write_bytes(draft)
            (folder / "report.json").write_text(report_json, encoding="utf-8")
            row = {
                "id": run_id,
                "project_id": project_id,
                "template_name": filename,
                "storage_path": str(folder.relative_to(root)),
                "report_json": report_json,
                "created_at": report["created_at"],
            }
            db.execute(
                """
                INSERT INTO document_compilations
                    (id, project_id, template_name, storage_path, report_json, created_at)
                VALUES (:id, :project_id, :template_name, :storage_path, :report_json, :created_at)
                """,
                row,
            )
            touch_project(db, project_id)
    except Exception:
        if created:
            rmtree(folder, ignore_errors=True)
        raise
    return _payload(row)


@router.post("", status_code=201)
async def create_compilation(
    project_id: str,
    file: Annotated[
        UploadFile, File(description="Modello DOCX con celle vuote o segnaposti nei paragrafi")
    ],
    instructions: Annotated[str, Form(max_length=4000)] = "",
) -> dict:
    try:
        project = get_project(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Progetto non trovato")
        filename = Path((file.filename or "").replace("\\", "/")).name
        if Path(filename).suffix.lower() != ".docx":
            raise HTTPException(
                status_code=415, detail="Carica un modello DOCX, non DOC, PDF o Markdown"
            )
        if len(filename) > 180 or any(ord(c) < 32 for c in filename):
            raise HTTPException(status_code=422, detail="Nome del modello non valido")
        data = await file.read(MAX_DOCX_BYTES + 1)
    finally:
        await file.close()
    try:
        draft, report = await compile_document(
            project_id, project["title"], data, instructions.strip()
        )
        return await run_in_threadpool(_persist, project_id, filename, data, draft, report)
    except DocxTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except DocumentInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GenerationNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Impossibile salvare la compilazione") from exc


@router.get("")
def list_compilations(project_id: str) -> list[dict]:
    if get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    with connection() as db:
        rows = db.execute(
            """
            SELECT * FROM document_compilations WHERE project_id = ?
            ORDER BY created_at DESC, id DESC LIMIT 100
            """,
            (project_id,),
        ).fetchall()
    return [_payload(dict(row), include_report=False) for row in rows]


def _get_run(project_id: str, run_id: str) -> dict:
    with connection() as db:
        row = db.execute(
            "SELECT * FROM document_compilations WHERE project_id = ? AND id = ?",
            (project_id, run_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Compilazione non trovata nel progetto")
    return dict(row)


@router.get("/{run_id}")
def get_compilation(project_id: str, run_id: str) -> dict:
    return _payload(_get_run(project_id, run_id))


@router.get("/{run_id}/download/{kind}")
def download_compilation(
    project_id: str, run_id: str, kind: Literal["docx", "report", "template"]
) -> FileResponse:
    row = _get_run(project_id, run_id)
    names = {"docx": "bozza.docx", "report": "report.json", "template": "template.docx"}
    root = get_storage_path().resolve()
    path = (root / row["storage_path"] / names[kind]).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File della compilazione non trovato")
    stem = Path(row["template_name"]).stem
    filename = f"{stem}-bozza.docx" if kind == "docx" else names[kind]
    return FileResponse(
        path,
        media_type="application/json" if kind == "report" else DOCX_MIME,
        filename=filename,
        headers={"Cache-Control": "no-store"},
    )
