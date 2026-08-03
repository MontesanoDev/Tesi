from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_database
from app.ingestion import (
    DocumentTooLargeError,
    EmptyDocumentError,
    InvalidDocumentError,
    UnsupportedDocumentError,
    ingest_upload,
)
from app.repository import (
    add_project_file,
    create_project,
    get_document_review,
    get_project,
    list_projects,
    search_project_evidence,
)
from app.schemas import (
    DocumentReview,
    EvidenceSearch,
    ProjectCreate,
    ProjectDetail,
    ProjectFile,
    ProjectSummary,
)
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    seed_database()
    yield


app = FastAPI(title="Mapi RAG API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/projects", response_model=list[ProjectSummary])
async def projects() -> list[dict]:
    return list_projects()


@app.post("/api/projects", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def projects_create(payload: ProjectCreate) -> dict:
    return create_project(payload)


@app.get("/api/projects/{project_id}", response_model=ProjectDetail)
async def project(project_id: str) -> dict:
    result = get_project(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result


@app.get("/api/projects/{project_id}/evidence", response_model=EvidenceSearch)
async def project_evidence(
    project_id: str,
    q: Annotated[str, Query(min_length=2, max_length=500)],
    limit: Annotated[int, Query(ge=1, le=8)] = 4,
) -> dict:
    results = search_project_evidence(project_id, q, limit)
    if results is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return {"query": q, "results": results}


@app.post(
    "/api/projects/{project_id}/files",
    response_model=ProjectFile,
    status_code=status.HTTP_201_CREATED,
)
async def project_file_create(
    project_id: str,
    file: Annotated[UploadFile, File(description="Documento PDF o TXT")],
) -> dict:
    if get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    try:
        document = await ingest_upload(project_id, file)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except (EmptyDocumentError, InvalidDocumentError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = add_project_file(project_id, document)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result


@app.get("/api/projects/{project_id}/document-review", response_model=DocumentReview)
async def document_review(project_id: str) -> dict:
    result = get_document_review(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result
