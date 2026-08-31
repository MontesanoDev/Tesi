from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import replace
from shutil import rmtree
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.artifacts import (
    ArtifactReadOnlyError,
    ensure_project_artifacts,
    get_project_artifact,
    list_project_artifacts,
    replace_project_artifact,
    seed_markdown_artifacts,
    update_project_artifact,
)
from app.call_facts import (
    CallFactsDocument,
    CallFactsFormatError,
    parse_call_facts_markdown,
    render_call_facts_document,
    revise_call_fact,
)
from app.db import get_knowledge_path, get_storage_path, init_database
from app.draft_generation import (
    DraftInputError,
    generate_grounded_draft,
    render_draft_markdown,
)
from app.fact_extraction import extract_call_facts, load_project_source_chunks
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
    chunk_text,
    ingest_global_upload,
    ingest_upload,
)
from app.intents import direct_system_answer
from app.repository import (
    add_global_document,
    add_project_file,
    contextualize_search_query,
    create_project,
    delete_global_document,
    delete_project,
    get_company_context,
    get_conversation,
    get_conversation_history,
    get_document_review,
    get_global_document_record,
    get_global_knowledge,
    get_or_create_conversation,
    get_project,
    get_project_file_record,
    is_follow_up_question,
    list_project_global_documents,
    list_projects,
    recent_conversation_evidence,
    save_conversation_turn,
    search_project_evidence,
    set_project_global_document_link,
    sync_call_fact_review_metrics,
    update_call_fact_metrics,
    update_call_fact_review_metrics,
    update_global_document_content,
    update_project,
    update_project_file_content,
)
from app.schemas import (
    CallFactRevision,
    CallFactsExtractionResponse,
    CallFactsReview,
    ConversationDetail,
    DocumentReview,
    DraftGenerationResponse,
    EvidenceSearch,
    GlobalKnowledgeDocument,
    GlobalKnowledgeDocumentContent,
    GlobalKnowledgeDocumentUpdate,
    GlobalKnowledgeLinkUpdate,
    GlobalKnowledgeOverview,
    GroundedAnswerResponse,
    KnowledgeArtifactDetail,
    KnowledgeArtifactSummary,
    KnowledgeArtifactUpdate,
    ProjectCreate,
    ProjectDetail,
    ProjectFile,
    ProjectFileContent,
    ProjectFileUpdate,
    ProjectGlobalKnowledgeDocument,
    ProjectSummary,
    ProjectUpdate,
    QuestionRequest,
)
from app.seed import seed_database


def _call_facts_review_payload(artifact: dict, document: CallFactsDocument) -> dict:
    return {
        "artifact": artifact,
        "facts": [
            {
                "id": fact.id,
                "title": fact.title,
                "value": fact.value,
                "status": fact.status,
                "sources": [
                    {"name": source.name, "fragment": source.fragment} for source in fact.sources
                ],
            }
            for fact in document.facts
        ],
        "missing_information": document.missing_information,
        "pending_count": document.pending_count,
        "verified_count": document.verified_count,
        "discarded_count": document.discarded_count,
    }


def _get_call_facts_document(project_id: str) -> tuple[dict, CallFactsDocument]:
    artifact_id = f"{project_id}--call-facts"
    artifact = get_project_artifact(project_id, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artefatto Call Facts non trovato")
    try:
        document = parse_call_facts_markdown(artifact["content"])
    except CallFactsFormatError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return artifact, replace(document, project_id=project_id)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    seed_database()
    seed_markdown_artifacts()
    sync_call_fact_review_metrics()
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


@app.patch("/api/projects/{project_id}", response_model=ProjectDetail)
async def project_update(project_id: str, payload: ProjectUpdate) -> dict:
    updated = update_project(project_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return updated


@app.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def project_delete(project_id: str) -> Response:
    if not delete_project(project_id):
        raise HTTPException(status_code=404, detail="Progetto non trovato")

    for root, relative_path in (
        (get_storage_path(), project_id),
        (get_knowledge_path(), f"projects/{project_id}"),
    ):
        resolved_root = root.resolve()
        project_path = (resolved_root / relative_path).resolve()
        if resolved_root in project_path.parents:
            rmtree(project_path, ignore_errors=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/global-knowledge", response_model=GlobalKnowledgeOverview)
async def global_knowledge() -> dict:
    return get_global_knowledge()


@app.post(
    "/api/global-knowledge/files",
    response_model=GlobalKnowledgeDocument,
    status_code=status.HTTP_201_CREATED,
)
async def global_knowledge_file_create(
    file: Annotated[UploadFile, File(description="Documento PDF, TXT o Markdown")],
    category: Annotated[Literal["general", "company"], Form()] = "company",
) -> dict:
    try:
        document = await ingest_global_upload(category, file)
    except UnsupportedDocumentError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except (EmptyDocumentError, InvalidDocumentError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return add_global_document(document, category)


@app.get(
    "/api/global-knowledge/files/{document_id}/content",
    response_model=GlobalKnowledgeDocumentContent,
)
async def global_knowledge_file_content(document_id: int) -> dict:
    document = get_global_document_record(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento globale non trovato")
    if document["mime_type"] not in {"text/plain", "text/markdown"}:
        raise HTTPException(
            status_code=415,
            detail="Soltanto le fonti TXT e Markdown possono essere modificate",
        )

    storage_root = get_storage_path().resolve()
    path = (storage_root / document["storage_path"]).resolve()
    if storage_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File della fonte non trovato")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise HTTPException(status_code=422, detail="La fonte testuale non e leggibile") from exc
    return {**document, "content": content}


@app.put(
    "/api/global-knowledge/files/{document_id}/content",
    response_model=GlobalKnowledgeDocumentContent,
)
async def global_knowledge_file_content_update(
    document_id: int,
    payload: GlobalKnowledgeDocumentUpdate,
) -> dict:
    document = get_global_document_record(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento globale non trovato")
    if document["mime_type"] not in {"text/plain", "text/markdown"}:
        raise HTTPException(
            status_code=415,
            detail="Soltanto le fonti TXT e Markdown possono essere modificate",
        )

    chunks = chunk_text(payload.content)
    if not chunks:
        raise HTTPException(status_code=422, detail="La fonte non puo essere vuota")

    storage_root = get_storage_path().resolve()
    path = (storage_root / document["storage_path"]).resolve()
    if storage_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File della fonte non trovato")

    encoded = payload.content.encode("utf-8")
    previous_content = path.read_bytes()
    temporary_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary_path.write_bytes(encoded)
        temporary_path.replace(path)
        updated = update_global_document_content(
            document_id,
            len(encoded),
            chunks,
        )
    except Exception:
        path.write_bytes(previous_content)
        raise
    finally:
        temporary_path.unlink(missing_ok=True)
    if updated is None:
        path.write_bytes(previous_content)
        raise HTTPException(status_code=404, detail="Documento globale non trovato")
    return {**updated, "content": payload.content}


@app.delete(
    "/api/global-knowledge/files/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def global_knowledge_file_delete(document_id: int) -> Response:
    deleted = delete_global_document(document_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Documento aziendale non trovato")
    storage_root = get_storage_path().resolve()
    path = (storage_root / deleted["storage_path"]).resolve()
    if storage_root in path.parents:
        path.unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/projects/{project_id}", response_model=ProjectDetail)
async def project(project_id: str) -> dict:
    result = get_project(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result


@app.get(
    "/api/projects/{project_id}/global-knowledge",
    response_model=list[ProjectGlobalKnowledgeDocument],
)
async def project_global_knowledge(project_id: str) -> list[dict]:
    documents = list_project_global_documents(project_id)
    if documents is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return documents


@app.put(
    "/api/projects/{project_id}/global-knowledge/{document_id}",
    response_model=ProjectGlobalKnowledgeDocument,
)
async def project_global_knowledge_update(
    project_id: str,
    document_id: int,
    payload: GlobalKnowledgeLinkUpdate,
) -> dict:
    document = set_project_global_document_link(project_id, document_id, payload.linked)
    if document is None:
        raise HTTPException(status_code=404, detail="Progetto o documento aziendale non trovato")
    return document


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


@app.post(
    "/api/projects/{project_id}/call-facts/extract",
    response_model=CallFactsExtractionResponse,
)
async def project_call_facts_extract(project_id: str) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    source_chunks = load_project_source_chunks(project_id)
    if not source_chunks:
        raise HTTPException(
            status_code=422,
            detail="Carica e indicizza almeno una fonte prima di estrarre i Call Facts",
        )
    try:
        extraction = await extract_call_facts(
            project_id,
            project["title"],
            source_chunks,
        )
    except GenerationNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    artifact_id = f"{project_id}--call-facts"
    artifact = replace_project_artifact(
        project_id,
        artifact_id,
        extraction.markdown,
        status="Da verificare",
    )
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artefatto Call Facts non trovato")
    update_call_fact_metrics(project_id, extraction.fact_count, extraction.missing_count)
    return {
        "artifact": artifact,
        "fact_count": extraction.fact_count,
        "missing_count": extraction.missing_count,
        "evidence_count": extraction.evidence_count,
        "model": extraction.model,
        "total_tokens": extraction.total_tokens,
    }


@app.get(
    "/api/projects/{project_id}/call-facts",
    response_model=CallFactsReview,
)
async def project_call_facts(project_id: str) -> dict:
    if get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    artifact, document = _get_call_facts_document(project_id)
    return _call_facts_review_payload(artifact, document)


@app.patch(
    "/api/projects/{project_id}/call-facts/{fact_id}",
    response_model=CallFactsReview,
)
async def project_call_fact_revision(
    project_id: str,
    fact_id: str,
    payload: CallFactRevision,
) -> dict:
    if get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    artifact, document = _get_call_facts_document(project_id)
    if artifact["version"] != payload.version:
        raise HTTPException(
            status_code=409,
            detail="call-facts.md e stato aggiornato: ricarica la revisione",
        )
    try:
        revised = revise_call_fact(
            document,
            fact_id,
            payload.action,
            title=payload.title,
            value=payload.value,
        )
    except CallFactsFormatError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if revised.pending_count:
        artifact_status = "Da verificare"
    elif revised.verified_count:
        artifact_status = "Verificato"
    else:
        artifact_status = "Revisionato"
    updated = replace_project_artifact(
        project_id,
        artifact["id"],
        render_call_facts_document(revised),
        status=artifact_status,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Artefatto Call Facts non trovato")
    update_call_fact_review_metrics(
        project_id=project_id,
        active_count=revised.active_count,
        verified_count=revised.verified_count,
        pending_count=revised.pending_count,
        discarded_count=revised.discarded_count,
        missing_count=len(revised.missing_information),
    )
    return _call_facts_review_payload(updated, revised)


@app.post(
    "/api/projects/{project_id}/draft/generate",
    response_model=DraftGenerationResponse,
)
async def project_draft_generate(project_id: str) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")

    _, call_facts = _get_call_facts_document(project_id)
    verified_facts = [fact for fact in call_facts.facts if fact.status == "verified"]
    if not verified_facts:
        raise HTTPException(
            status_code=422,
            detail="Verifica almeno un Call Fact prima di generare il draft",
        )

    artifact_ids = {
        "template": f"{project_id}--template",
        "project_facts": f"{project_id}--project-facts",
        "draft": f"{project_id}--draft",
    }
    artifacts = {
        name: get_project_artifact(project_id, artifact_id)
        for name, artifact_id in artifact_ids.items()
    }
    if any(artifact is None for artifact in artifacts.values()):
        raise HTTPException(
            status_code=422,
            detail="Gli artefatti richiesti per il draft non sono completi",
        )

    template = artifacts["template"]
    project_facts = artifacts["project_facts"]
    if template is None or project_facts is None:
        raise RuntimeError("Gli artefatti validati non sono piu disponibili")
    if template["status"] == "Da configurare":
        raise HTTPException(
            status_code=422,
            detail="Configura il Template prima di generare il draft",
        )

    company_sources = get_company_context()
    try:
        generated = await generate_grounded_draft(
            project_title=project["title"],
            template_markdown=template["content"],
            company_sources=company_sources,
            project_facts_markdown=project_facts["content"],
            verified_facts=verified_facts,
        )
    except DraftInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GenerationNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    markdown = render_draft_markdown(
        project_id,
        generated,
        verified_facts,
        company_sources,
    )
    draft = replace_project_artifact(
        project_id,
        artifact_ids["draft"],
        markdown,
        status="Da verificare",
    )
    if draft is None:
        raise HTTPException(status_code=404, detail="Artefatto Draft non trovato")
    return {
        "artifact": draft,
        "verified_fact_count": len(verified_facts),
        "used_fact_count": len(generated.used_fact_ids),
        "missing_information": generated.missing_information,
        "model": generated.model,
        "total_tokens": generated.total_tokens,
    }


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
    file: Annotated[UploadFile, File(description="Documento PDF, TXT o Markdown")],
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


@app.get(
    "/api/projects/{project_id}/files/{file_id}/content",
    response_model=ProjectFileContent,
)
async def project_file_content(project_id: str, file_id: int) -> dict:
    document = get_project_file_record(project_id, file_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Fonte del progetto non trovata")
    if document["mime_type"] not in {"text/plain", "text/markdown"}:
        raise HTTPException(
            status_code=415,
            detail="Soltanto le fonti TXT e Markdown possono essere modificate",
        )

    storage_root = get_storage_path().resolve()
    path = (storage_root / document["storage_path"]).resolve()
    if storage_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File della fonte non trovato")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise HTTPException(status_code=422, detail="La fonte testuale non e leggibile") from exc
    return {**document, "content": content}


@app.put(
    "/api/projects/{project_id}/files/{file_id}/content",
    response_model=ProjectFileContent,
)
async def project_file_content_update(
    project_id: str,
    file_id: int,
    payload: ProjectFileUpdate,
) -> dict:
    document = get_project_file_record(project_id, file_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Fonte del progetto non trovata")
    if document["mime_type"] not in {"text/plain", "text/markdown"}:
        raise HTTPException(
            status_code=415,
            detail="Soltanto le fonti TXT e Markdown possono essere modificate",
        )

    chunks = chunk_text(payload.content)
    if not chunks:
        raise HTTPException(status_code=422, detail="La fonte non puo essere vuota")

    storage_root = get_storage_path().resolve()
    path = (storage_root / document["storage_path"]).resolve()
    if storage_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="File della fonte non trovato")

    encoded = payload.content.encode("utf-8")
    previous_content = path.read_bytes()
    temporary_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary_path.write_bytes(encoded)
        temporary_path.replace(path)
        updated = update_project_file_content(
            project_id,
            file_id,
            len(encoded),
            chunks,
        )
    except Exception:
        path.write_bytes(previous_content)
        raise
    finally:
        temporary_path.unlink(missing_ok=True)
    if updated is None:
        path.write_bytes(previous_content)
        raise HTTPException(status_code=404, detail="Fonte del progetto non trovata")
    return {**updated, "content": payload.content}


@app.get("/api/projects/{project_id}/document-review", response_model=DocumentReview)
async def document_review(project_id: str) -> dict:
    result = get_document_review(project_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return result
