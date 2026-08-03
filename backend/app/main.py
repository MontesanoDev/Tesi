from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.artifacts import (
    ArtifactReadOnlyError,
    ensure_project_artifacts,
    get_project_artifact,
    list_project_artifacts,
    seed_markdown_artifacts,
    update_project_artifact,
)
from app.db import init_database
from app.generation import (
    GenerationError,
    GenerationNotConfiguredError,
    generate_grounded_answer,
)
from app.ingestion import (
    DocumentTooLargeError,
    EmptyDocumentError,
    InvalidDocumentError,
    UnsupportedDocumentError,
    ingest_upload,
)
from app.intents import direct_system_answer
from app.repository import (
    add_project_file,
    contextualize_search_query,
    create_project,
    get_company_facts,
    get_conversation,
    get_conversation_history,
    get_document_review,
    get_or_create_conversation,
    get_project,
    is_follow_up_question,
    list_projects,
    recent_conversation_evidence,
    save_conversation_turn,
    search_project_evidence,
)
from app.schemas import (
    ConversationDetail,
    DocumentReview,
    EvidenceSearch,
    GroundedAnswerResponse,
    KnowledgeArtifactDetail,
    KnowledgeArtifactSummary,
    KnowledgeArtifactUpdate,
    ProjectCreate,
    ProjectDetail,
    ProjectFile,
    ProjectSummary,
    QuestionRequest,
)
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    seed_database()
    seed_markdown_artifacts()
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
    created = create_project(payload)
    ensure_project_artifacts(created["id"])
    result = get_project(created["id"])
    if result is None:
        raise RuntimeError("Il progetto appena creato non e piu disponibile")
    return result


@app.get("/api/projects/{project_id}", response_model=ProjectDetail)
async def project(project_id: str) -> dict:
    result = get_project(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result


@app.get(
    "/api/projects/{project_id}/artifacts",
    response_model=list[KnowledgeArtifactSummary],
)
async def project_artifacts(project_id: str) -> list[dict]:
    result = list_project_artifacts(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result


@app.get(
    "/api/projects/{project_id}/artifacts/{artifact_id}",
    response_model=KnowledgeArtifactDetail,
)
async def project_artifact(project_id: str, artifact_id: str) -> dict:
    result = get_project_artifact(project_id, artifact_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Artefatto Markdown non trovato")
    return result


@app.put(
    "/api/projects/{project_id}/artifacts/{artifact_id}",
    response_model=KnowledgeArtifactDetail,
)
async def project_artifact_update(
    project_id: str,
    artifact_id: str,
    payload: KnowledgeArtifactUpdate,
) -> dict:
    try:
        result = update_project_artifact(project_id, artifact_id, payload.content)
    except ArtifactReadOnlyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Artefatto Markdown non trovato")
    return result


@app.get(
    "/api/projects/{project_id}/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
async def project_conversation(project_id: str, conversation_id: str) -> dict:
    result = get_conversation(project_id, conversation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Conversazione non trovata")
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


@app.post("/api/projects/{project_id}/answer", response_model=GroundedAnswerResponse)
async def project_answer(project_id: str, payload: QuestionRequest) -> dict:
    if get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    conversation = get_or_create_conversation(
        project_id,
        payload.conversation_id,
        payload.question,
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversazione non trovata")
    conversation_id = conversation["id"]
    history = get_conversation_history(conversation_id)

    def persist(response: dict) -> dict:
        turn_id = save_conversation_turn(conversation_id, response)
        return {
            **response,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
        }

    direct_answer = direct_system_answer(payload.question)
    if direct_answer:
        return persist(
            {
                "question": payload.question,
                "answer": direct_answer,
                "citations": [],
                "missing_information": [],
                "evidence": [],
                "generation_status": "direct",
                "model": "Mapi RAG",
                "total_tokens": 0,
                "notice": None,
            }
        )
    search_query = contextualize_search_query(payload.question, history)
    evidence = search_project_evidence(
        project_id,
        search_query,
        limit=4,
        include_neighbors=True,
    )
    if evidence is None:
        raise RuntimeError("Il progetto validato non e piu disponibile")
    if not evidence and history and is_follow_up_question(payload.question):
        evidence = recent_conversation_evidence(history)
    base_response = {
        "question": payload.question,
        "citations": [],
        "missing_information": [],
        "evidence": evidence,
        "model": None,
        "total_tokens": None,
    }
    if not evidence:
        return persist(
            {
                **base_response,
                "answer": (
                    "Non trovo nelle fonti indicizzate informazioni sufficienti per "
                    f"rispondere in modo verificabile a «{payload.question}». Il dato "
                    "richiesto deve essere aggiunto o confermato da una fonte prima "
                    "di utilizzarlo."
                ),
                "missing_information": ["Una fonte contenente il dato richiesto dall'utente"],
                "generation_status": "no_evidence",
                "notice": "Le fonti non contengono dati verificabili per questa richiesta.",
            }
        )
    try:
        generated = await generate_grounded_answer(
            payload.question,
            evidence,
            company_facts=get_company_facts(),
            conversation_history=history,
        )
    except GenerationNotConfiguredError as exc:
        return persist(
            {
                **base_response,
                "answer": None,
                "generation_status": "not_configured",
                "notice": str(exc),
            }
        )
    except GenerationError as exc:
        return persist(
            {
                **base_response,
                "answer": None,
                "generation_status": "failed",
                "notice": str(exc),
            }
        )
    return persist(
        {
            **base_response,
            "answer": generated.answer,
            "citations": generated.citations,
            "missing_information": generated.missing_information,
            "generation_status": "completed",
            "model": generated.model,
            "total_tokens": generated.total_tokens,
            "notice": None,
        }
    )


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
