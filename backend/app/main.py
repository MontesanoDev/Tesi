from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_database
from app.repository import create_project, get_document_review, get_project, list_projects
from app.schemas import DocumentReview, ProjectCreate, ProjectDetail, ProjectSummary
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


@app.get("/api/projects/{project_id}/document-review", response_model=DocumentReview)
async def document_review(project_id: str) -> dict:
    result = get_document_review(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result
