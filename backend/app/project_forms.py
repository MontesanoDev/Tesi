from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from starlette.concurrency import run_in_threadpool

from app.db import connection, get_storage_path, touch_project
from app.docx_templates import DocumentInputError, DocxTooLargeError, validate_docx_package
from app.ingestion import MAX_FILE_SIZE
from app.repository import _format_size
from app.schemas import ProjectFile

router = APIRouter(prefix="/api/projects/{project_id}/forms", tags=["Moduli del progetto"])
FORM_FORMATS = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
}
PUBLIC_COLUMNS = "id, name, metadata, kind, status, mime_type, byte_size, page_count, chunk_count"


def _require_project(db, project_id: str) -> None:
    if db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")


def _form_path(project_id: str, stored_path: str) -> Path:
    root = get_storage_path().resolve()
    folder = (root / project_id / "_forms").resolve()
    path = (root / stored_path).resolve()
    if root not in folder.parents or folder not in path.parents:
        raise HTTPException(status_code=422, detail="Percorso del modulo non valido")
    return path


def _validate_file(data: bytes, suffix: str) -> None:
    # Check the container, not field candidates or compilation eligibility.
    # No extraction, chunks, retrieval indexing or model calls happen here.
    if not data:
        raise HTTPException(status_code=422, detail="Il file selezionato e vuoto")
    try:
        if suffix == ".docx":
            validate_docx_package(data)
        elif suffix == ".pdf":
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted or not reader.pages:
                raise ValueError("PDF vuoto o protetto")
        elif not data.decode("utf-8-sig").strip() or b"\x00" in data:
            raise ValueError("Testo vuoto o non valido")
    except DocxTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except (DocumentInputError, PdfReadError, ValueError, OSError) as exc:
        raise HTTPException(
            status_code=422, detail="File non leggibile o formato non supportato: " + str(exc),
        ) from exc


def _save_form(project_id: str, name: str, data: bytes) -> dict:
    suffix = Path(name).suffix.lower()
    _validate_file(data, suffix)
    relative = str(Path(project_id) / "_forms" / f"{uuid4().hex}{suffix}")
    path = _form_path(project_id, relative)
    created = False
    try:
        with connection() as db:
            db.execute("BEGIN IMMEDIATE")
            _require_project(db, project_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as target:
                created = True
                target.write(data)
            order = db.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM project_files WHERE project_id = ?",
                (project_id,),
            ).fetchone()[0]
            cursor = db.execute(
                """INSERT INTO project_files
                   (project_id, name, metadata, kind, status, storage_path,
                    mime_type, byte_size, sort_order)
                   VALUES (?, ?, ?, 'form', 'Caricato', ?, ?, ?, ?)""",
                (project_id, name, f"{suffix[1:].upper()} · {_format_size(len(data))}",
                 relative, FORM_FORMATS[suffix], len(data), order),
            )
            db.execute(
                "UPDATE projects SET model_count = model_count + 1 WHERE id = ?", (project_id,),
            )
            touch_project(db, project_id)
            row = db.execute(
                f"SELECT {PUBLIC_COLUMNS} FROM project_files WHERE id = ?", (cursor.lastrowid,),
            ).fetchone()
    except Exception:
        if created:
            path.unlink(missing_ok=True)
        raise
    return dict(row)


@router.post("", response_model=ProjectFile, status_code=201)
async def upload_form(project_id: str, file: Annotated[UploadFile, File()]) -> dict:
    try:
        with connection() as db:
            _require_project(db, project_id)
        name = Path((file.filename or "").replace("\\", "/")).name
        if not name or len(name) > 180 or any(ord(char) < 32 for char in name):
            raise HTTPException(status_code=422, detail="Nome del file non valido")
        if Path(name).suffix.lower() not in FORM_FORMATS:
            raise HTTPException(status_code=415, detail="Carica un file DOCX, PDF, TXT o Markdown")
        data = await file.read(MAX_FILE_SIZE + 1)
        if len(data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Il file supera il limite di 20 MB")
        return await run_in_threadpool(_save_form, project_id, name, data)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Impossibile salvare il modulo") from exc
    finally:
        await file.close()


@router.get("", response_model=list[ProjectFile])
def list_forms(project_id: str) -> list[dict]:
    with connection() as db:
        _require_project(db, project_id)
        rows = db.execute(
            f"SELECT {PUBLIC_COLUMNS} FROM project_files "
            "WHERE project_id = ? AND kind = 'form' ORDER BY sort_order, id",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


@router.get("/{form_id}/download")
def download_form(project_id: str, form_id: int) -> FileResponse:
    with connection() as db:
        row = db.execute(
            "SELECT * FROM project_files WHERE project_id = ? AND id = ? AND kind = 'form'",
            (project_id, form_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Modulo non trovato")
    path = _form_path(project_id, row["storage_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File del modulo non trovato")
    return FileResponse(path, filename=row["name"], media_type=row["mime_type"], headers={
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
    })


@router.delete("/{form_id}", status_code=204)
def delete_form(project_id: str, form_id: int) -> Response:
    try:
        with connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT storage_path FROM project_files "
                "WHERE project_id = ? AND id = ? AND kind = 'form'",
                (project_id, form_id),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Modulo non trovato")
            path = _form_path(project_id, row["storage_path"])
            db.execute("DELETE FROM project_files WHERE id = ?", (form_id,))
            db.execute(
                "UPDATE projects SET model_count = MAX(0, model_count - 1) WHERE id = ?",
                (project_id,),
            )
            touch_project(db, project_id)
            path.unlink(missing_ok=True)
    except OSError as exc:
        raise HTTPException(
            status_code=500, detail="Impossibile rimuovere il modulo; riprova",
        ) from exc
    return Response(status_code=204)
