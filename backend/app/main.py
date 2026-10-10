from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path
from shutil import rmtree
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from app.ai_profiles import import_legacy_configuration, project_ai_context
from app.ai_routes import router as ai_router
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
from app.compilation_chat import (
    ActiveFieldDecision,
    ClarificationDecision,
    active_session,
    handle_active_decision,
    handle_decision,
    handle_group_decision,
    planner_context,
)
from app.compilation_session_routes import router as compilation_session_router
from app.db import get_knowledge_path, get_storage_path, init_database
from app.document_compilation_routes import router as document_compilation_router
from app.draft_generation import (
    DraftInputError,
    generate_grounded_draft,
    render_draft_markdown,
)
from app.fact_extraction import extract_call_facts, load_project_source_chunks
from app.generation import (
    GenerationError,
    GenerationNotConfiguredError,
    chat_timeout_seconds,
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
from app.intents import (
    ChatDecision,
    plan_chat_turn,
    plan_requirement_checks,
    route_availability_request,
    route_compilation_control,
)
from app.project_forms import list_forms
from app.project_forms import router as project_forms_router
from app.repository import (
    add_global_document,
    add_project_file,
    create_project,
    delete_global_document,
    delete_project,
    delete_project_file,
    get_company_context,
    get_conversation,
    get_conversation_history,
    get_document_review,
    get_global_document_record,
    get_global_knowledge,
    get_or_create_conversation,
    get_project,
    get_project_file_record,
    list_project_global_documents,
    list_projects,
    save_conversation_turn,
    set_project_global_document_link,
    sync_call_fact_review_metrics,
    update_call_fact_metrics,
    update_call_fact_review_metrics,
    update_global_document_content,
    update_project,
    update_project_file_content,
)
from app.retrieval import expand_evidence_context, merge_evidence_results, search_project_evidence
from app.retrieval_routes import router as retrieval_router
from app.retrieval_settings import RetrievalError
from app.schemas import (
    MAX_QUESTION_LENGTH,
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
from app.source_planning import (
    MAX_CLUSTER_EVIDENCE,
    SOURCE_ANCHORS_PER_QUERY,
    cluster_queries,
    plan_source_search,
)


def _call_facts_review_payload(artifact: dict, document: CallFactsDocument) -> dict:
    return {
        "artifact": artifact,
        "facts": [
            {
                "id": fact.id,
                "title": fact.title,
                "value": fact.value,
                "status": fact.status,
                "origin": fact.origin,
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
    import_legacy_configuration()
    seed_database()
    seed_markdown_artifacts()
    sync_call_fact_review_metrics()
    yield


logger = logging.getLogger(__name__)
app = FastAPI(title="Mapi RAG API", version="0.1.0", lifespan=lifespan)
app.include_router(document_compilation_router)
app.include_router(compilation_session_router)
app.include_router(project_forms_router)
app.include_router(ai_router)
app.include_router(retrieval_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{host}:{port}"
        for host in ("localhost", "127.0.0.1")
        for port in sorted({"5173", os.getenv("MAPI_FRONTEND_PORT") or "5173"})
    ],
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
def global_knowledge_file_delete(document_id: int) -> Response:
    try:
        deleted = delete_global_document(document_id)
    except (OSError, ValueError):
        raise HTTPException(
            status_code=500, detail="Impossibile eliminare la fonte globale; riprova"
        ) from None
    if deleted is None:
        raise HTTPException(status_code=404, detail="Documento aziendale non trovato")
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
    current = get_project_artifact(project_id, artifact_id)
    document = None
    if current and current["kind"] == "call_facts":
        try:
            document = parse_call_facts_markdown(payload.content)
        except CallFactsFormatError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        result = update_project_artifact(project_id, artifact_id, payload.content)
    except ArtifactReadOnlyError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Artefatto Markdown non trovato")
    if document is not None:
        update_call_fact_review_metrics(
            project_id=project_id,
            active_count=len(document.available_facts),
            discarded_count=document.discarded_count,
            missing_count=len(document.missing_information),
        )
    return result


@app.post(
    "/api/projects/{project_id}/call-facts/extract",
    response_model=CallFactsExtractionResponse,
)
async def project_call_facts_extract(project_id: str) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    artifact_id = f"{project_id}--call-facts"
    original = get_project_artifact(project_id, artifact_id)
    if original is None:
        raise HTTPException(status_code=404, detail="Dati del progetto non trovati")
    source_chunks = load_project_source_chunks(project_id)
    if not source_chunks:
        raise HTTPException(
            status_code=422,
            detail="Carica e indicizza almeno una fonte prima di estrarre i dati del progetto",
        )
    try:
        with project_ai_context(project_id):
            extraction = await extract_call_facts(
                project_id,
                project["title"],
                source_chunks,
            )
    except GenerationNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    current = get_project_artifact(project_id, artifact_id)
    if current is None or current["version"] != original["version"]:
        raise HTTPException(
            status_code=409,
            detail="I dati sono cambiati durante l'estrazione. Ricarica prima di riprovare.",
        )
    artifact = replace_project_artifact(
        project_id,
        artifact_id,
        extraction.markdown,
        status="Estratto",
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

    artifact_status = "Disponibile" if revised.available_facts else "Nessun dato disponibile"
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
        active_count=len(revised.available_facts),
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
    available_facts = call_facts.available_facts

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
    if template["status"] == "Da configurare" or not template["content"].strip():
        raise HTTPException(
            status_code=422,
            detail="Carica o crea e salva un modello prima di generare la compilazione",
        )

    company_sources = get_company_context()
    try:
        with project_ai_context(project_id):
            generated = await generate_grounded_draft(
                project_title=project["title"],
                template_markdown=template["content"],
                company_sources=company_sources,
                project_facts_markdown=project_facts["content"],
                available_facts=available_facts,
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
        available_facts,
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
        "verified_fact_count": sum(fact.status == "verified" for fact in available_facts),
        "available_fact_count": len(available_facts),
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
    q: Annotated[str, Query(min_length=2, max_length=MAX_QUESTION_LENGTH)],
    limit: Annotated[int, Query(ge=1, le=8)] = 4,
    target: Literal["source", "form"] = "source",
    form_id: Annotated[int | None, Query(gt=0)] = None,
) -> dict:
    if target == "source" and form_id is not None:
        raise HTTPException(422, "form_id richiede target=form")
    try:
        results = await run_in_threadpool(
            search_project_evidence, project_id, q, limit, target=target, form_id=form_id,
        )
    except RetrievalError as exc:
        raise HTTPException(503, str(exc)) from None
    if results is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return {"query": q, "results": results}


@app.post("/api/projects/{project_id}/answer", response_model=GroundedAnswerResponse)
async def project_answer(project_id: str, payload: QuestionRequest) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    form_reference = None
    document_reference = None
    selected_document = None
    mentioned_forms = None
    document_id = payload.document_id if payload.document_id is not None else payload.form_id
    if document_id is not None:
        document = next((file for file in project["files"]
                         if file["id"] == document_id and file["kind"] in {"source", "form"}), None)
        if document is None or (payload.form_id is not None and document["kind"] != "form"):
            raise HTTPException(404, "Documento menzionato non trovato nel progetto")
        document_reference = {
            "document_id": document_id, "name": document["name"], "role": document["kind"],
        }
        selected_document = {**document_reference, "can_compile": (
            document["kind"] == "form" and Path(document["name"]).suffix.lower() == ".docx"
        )}
    if document_reference and document_reference["role"] == "form":
        mentioned_forms = [f for f in await run_in_threadpool(list_forms, project_id)
                           if f["id"] == document_id]
        if not mentioned_forms:
            raise HTTPException(404, "Modulo menzionato non trovato nel progetto")
        form = mentioned_forms[0]
        form_reference = {"form_id": form["id"], "name": form["name"]}
    conversation = get_or_create_conversation(
        project_id,
        payload.conversation_id,
        payload.question,
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversazione non trovata")
    conversation_id = conversation["id"]
    history = get_conversation_history(conversation_id)
    compilation_session = await run_in_threadpool(
        active_session, project_id, conversation_id,
        payload.form_id if payload.document_id is None else None,
        payload.compilation_session_id,
    )

    def persist(response: dict) -> dict:
        turn_id = save_conversation_turn(conversation_id, response)
        if turn_id is None:
            raise HTTPException(
                status_code=404,
                detail="La conversazione o il progetto sono stati eliminati durante la risposta",
            )
        return {
            **response,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
        }

    base_response = {
        "question": payload.question,
        "form_reference": form_reference,
        "document_reference": document_reference,
        "answer": None,
        "citations": [],
        "missing_information": [],
        "evidence": [],
        "model": None,
        "total_tokens": None,
        "notice": None,
    }

    async def interrupted_compilation():
        if compilation_session is None:
            return None
        # Standalone controls already have a conservative deterministic guard.
        # A provider outage must not prevent an explicit pause/resume.
        control = route_compilation_control(ChatDecision(
            action="reply", answer="Controllo", target="source", queries=[],
        ), payload.question, compilation_session)
        if control.action == "compilation_control":
            text, command = await handle_decision(
                project_id, conversation_id, control, form_reference, compilation_session,
                payload.question, payload.compilation_version,
            )
            return persist({**base_response, "answer": text, "compilation": command,
                            "generation_status": "direct"})
        return persist({
            **base_response,
            "answer": "Ho conservato i dati già verificati. Non sono riuscito a completare "
                      "questo passaggio. Puoi riprovare o esportare una bozza parziale.",
            "compilation": {"session_id": compilation_session["id"], "action": "clarify"},
            "generation_status": "failed",
        })

    # An explicit finish is a session command, even at an applicability checkpoint.
    # Handle it before planning so the leading 'no' cannot become a field answer.
    direct_control = route_compilation_control(ChatDecision(
        action="reply", answer="Controllo", target="source", queries=[],
    ), payload.question, compilation_session)
    if direct_control.action == "compilation_control" and direct_control.control.kind == "finish":
        text, command = await handle_decision(
            project_id, conversation_id, direct_control, form_reference, compilation_session,
            payload.question, payload.compilation_version,
        )
        return persist({**base_response, "answer": text, "compilation": command,
                        "generation_status": "direct"})

    try:
        # Pin the same provider/model for planning, answering and citation repair.
        with project_ai_context(project_id):
            timeout_seconds = chat_timeout_seconds()
            async with asyncio.timeout(timeout_seconds):
                forms = (mentioned_forms if mentioned_forms is not None
                         else await run_in_threadpool(list_forms, project_id))
                planned = await plan_chat_turn(
                    payload.question, history, forms,
                    **({"selected_document": selected_document}
                       if payload.document_id is not None else
                       {"selected_form": form_reference} if form_reference else {}),
                    **({"compilation": planner_context(compilation_session)}
                       if compilation_session else {}),
                )
                if isinstance(planned.decision, ClarificationDecision):
                    text, command = await handle_group_decision(
                        project_id, conversation_id, planned.decision,
                        compilation_session, payload.question, payload.compilation_version,
                    )
                    return persist({**base_response, "answer": text, "compilation": command,
                                    "generation_status": "direct", "model": planned.model,
                                    "total_tokens": planned.total_tokens})
                if isinstance(planned.decision, ActiveFieldDecision):
                    text, command = await handle_active_decision(
                        project_id, conversation_id, planned.decision, form_reference,
                        compilation_session, payload.question, payload.compilation_version,
                    )
                    return persist({**base_response, "answer": text, "compilation": command,
                                    "generation_status": "direct", "model": planned.model,
                                    "total_tokens": planned.total_tokens})
                workflow_decision = route_compilation_control(
                    planned.decision, payload.question, compilation_session,
                )
                if (workflow_decision.action == "compile" and selected_document
                        and not selected_document["can_compile"]):
                    available_forms = await run_in_threadpool(list_forms, project_id)
                    available = [f["name"] for f in available_forms
                                 if Path(f["name"]).suffix.lower() == ".docx"]
                    text = (f"Posso consultare «{selected_document['name']}», ma questo documento "
                            "non è un modulo DOCX compilabile. ")
                    text += ("Seleziona con @ il modulo da compilare: " + ", ".join(available)
                             if available else
                             "Carica il modulo DOCX da compilare e selezionalo con @.")
                    return persist({**base_response, "answer": text, "generation_status": "direct",
                                    "model": planned.model, "total_tokens": planned.total_tokens})
                if workflow_decision.action not in {"reply", "retrieve"}:
                    text, command = await handle_decision(
                        project_id, conversation_id, workflow_decision, form_reference,
                        compilation_session, payload.question, payload.compilation_version,
                    )
                    return persist({**base_response, "answer": text, "compilation": command,
                                    "generation_status": "direct", "model": planned.model,
                                    "total_tokens": planned.total_tokens})
                source_mention = bool(document_reference and document_reference["role"] == "source")
                decision = (planned.decision if source_mention else
                            route_availability_request(planned.decision, payload.question, forms))
                if source_mention and decision.action == "retrieve":
                    decision = decision.model_copy(update={
                        "target": "source", "form_id": None, "source_queries": [],
                    })
                if form_reference and decision.target in {"form", "mixed"}:
                    decision = decision.model_copy(update={"form_id": form_reference["form_id"]})
                logger.info(
                    "Chat routing project=%s planned=%s effective=%s form_id=%s",
                    project_id, planned.decision.target, decision.target, decision.form_id,
                )
                token_counts = [planned.total_tokens]
                if decision.action == "reply":
                    return persist({
                        **base_response,
                        "answer": decision.answer,
                        "generation_status": "direct",
                        "model": planned.model,
                        "total_tokens": planned.total_tokens,
                    })

                mixed = decision.target == "mixed"
                target = "form" if mixed else decision.target
                form_id = decision.form_id
                if target == "form" and form_id not in {form["id"] for form in forms}:
                    return persist({
                        **base_response,
                        "answer": (
                            "Non riesco a recuperare il contenuto del modulo richiesto. "
                            "Indica il nome di un modulo caricato in questo progetto."
                        ),
                        "generation_status": "no_evidence",
                        "missing_information": ["Identificazione del modulo richiesto"],
                        "model": planned.model,
                        "total_tokens": planned.total_tokens,
                        "notice": "Modulo assente o ambiguo; nessuna fonte sostitutiva.",
                    })
                contexts = {}
                requirements = None
                source_coverage = None
                # Separate retrieval and budgets: sources cannot crowd out requirements,
                # and form neighbors can never be promoted into factual evidence.
                for target in (("form", "source") if mixed else (target,)):
                    groups = []
                    if mixed and target == "source":
                        requirement_plan = await plan_requirement_checks(
                            payload.question, contexts["form"],
                        )
                        requirements = requirement_plan.plan.requirements
                        token_counts.append(requirement_plan.total_tokens)
                        logger.info(
                            "Chat requirements project=%s validated=%d attempts=%d",
                            project_id, len(requirements), requirement_plan.attempts,
                        )
                        if not requirements:
                            return persist({
                                **base_response,
                                "answer": (
                                    "Non ho verificato nelle evidenze del modulo requisiti "
                                    "pertinenti alla richiesta. La disponibilità non è stata "
                                    "valutata nelle fonti."
                                ),
                                "generation_status": "no_evidence",
                                "missing_information": [
                                    "Requisiti pertinenti sostenuti dal modulo",
                                ],
                                "model": requirement_plan.model,
                                "total_tokens": (
                                    sum(token_counts)
                                    if all(n is not None for n in token_counts) else None
                                ),
                                "notice": (
                                    "Nessun requisito verificato dopo due letture "
                                    "delle stesse evidenze FORM."
                                ),
                            })
                        source_plan = await plan_source_search(requirements)
                        token_counts.append(source_plan.total_tokens)
                        sources, coverage_chunks = {}, {}
                        for cluster_index, cluster in enumerate(source_plan.clusters, 1):
                            cluster_groups = []
                            queries = cluster_queries(cluster, requirements)
                            logger.info(
                                "Chat SOURCE cluster=%d requirements=%s queries=%s",
                                cluster_index, cluster.requirement_ids, queries,
                            )
                            for query in queries:
                                results = await run_in_threadpool(
                                    search_project_evidence, project_id, query,
                                    limit=SOURCE_ANCHORS_PER_QUERY, include_neighbors=False,
                                    target="source", form_id=None,
                                )
                                if results is None:
                                    raise HTTPException(
                                        404, "Progetto eliminato durante la ricerca",
                                    )
                                cluster_groups.append(results)
                            anchors = merge_evidence_results(
                                cluster_groups, limit=MAX_CLUSTER_EVIDENCE,
                            )
                            cluster_evidence = await run_in_threadpool(
                                expand_evidence_context, project_id, anchors,
                                target="source", max_results=MAX_CLUSTER_EVIDENCE,
                            )
                            chunks = {item["chunk_id"] for item in cluster_evidence}
                            for requirement_id in cluster.requirement_ids:
                                coverage_chunks[requirement_id] = chunks
                            sources.update((item["chunk_id"], item) for item in cluster_evidence)
                            contexts["source"] = list(sources.values())
                            base_response["evidence"] = contexts["form"] + contexts["source"]
                            logger.info("Chat SOURCE cluster=%d evidence=%s",
                                        cluster_index, sorted(chunks))
                        contexts["source"] = list(sources.values())
                        citations = {item["chunk_id"]: index for index, item in enumerate(
                            contexts["source"], len(contexts["form"]) + 1,
                        )}
                        source_coverage = {
                            index: {citations[chunk] for chunk in chunks}
                            for index, chunks in coverage_chunks.items()
                        }
                        logger.info("Chat SOURCE coverage searched=%s not_searched=%s evidence=%d",
                                    sorted(source_coverage), sorted(source_plan.not_searched),
                                    len(contexts["source"]))
                        continue
                    else:
                        queries = decision.queries
                    logger.info(
                        "Chat search project=%s target=%s queries=%s", project_id, target, queries,
                    )
                    selected_form = form_id if target == "form" else None
                    document_scope = {"document_id": document_id} if source_mention else {}
                    anchor_limit = 2 if mixed and target == "form" else 4
                    for query in queries:
                        results = await run_in_threadpool(
                            search_project_evidence, project_id, query,
                            limit=anchor_limit, include_neighbors=False,
                            target=target, form_id=selected_form,
                            **document_scope,
                        )
                        if results is None:
                            raise HTTPException(
                                status_code=404,
                                detail="Il progetto e stato eliminato durante la ricerca",
                            )
                        groups.append(results)
                        contexts[target] = merge_evidence_results(groups, limit=anchor_limit)
                        base_response["evidence"] = [
                            item for rows in contexts.values() for item in rows
                        ]
                    merged_count = len(contexts[target])
                    evidence = await run_in_threadpool(
                        expand_evidence_context, project_id, contexts[target],
                        target=target, form_id=selected_form, max_results=4 if mixed else 8,
                        **document_scope,
                    )
                    contexts[target] = evidence
                    logger.info(
                        "Chat bucket project=%s target=%s merged=%d expanded=%d",
                        project_id, target, merged_count, len(evidence),
                    )
                    base_response["evidence"] = [
                        item for rows in contexts.values() for item in rows
                    ]
                    if not evidence and (target == "form" or not mixed):
                        return persist({
                            **base_response,
                            "answer": (
                                "Non riesco a recuperare il contenuto del modulo richiesto. "
                                "Il modulo potrebbe richiedere la reindicizzazione dall'originale."
                                if target == "form" else
                                "Non trovo nelle fonti indicizzate informazioni sufficienti per "
                                f"rispondere in modo verificabile a «{payload.question}». Il dato "
                                "richiesto deve essere aggiunto o confermato da una fonte prima "
                                "di utilizzarlo."
                            ),
                            "missing_information": [
                                "Contenuto indicizzato del modulo richiesto" if target == "form"
                                else "Una fonte contenente il dato richiesto dall'utente",
                            ],
                            "generation_status": "no_evidence",
                            "model": planned.model,
                            "total_tokens": planned.total_tokens,
                            "notice": (
                                "Nessuna evidenza del modulo recuperata; nessuna fonte sostitutiva."
                                if target == "form" else
                                "Le fonti non contengono dati verificabili per questa richiesta."
                            ),
                        })
                options = {
                    "factual_evidence": contexts["source"], "requirements": requirements,
                    "source_coverage": source_coverage,
                } if mixed else {}
                generated = await generate_grounded_answer(
                    payload.question, contexts["form"] if mixed else evidence,
                    conversation_history=history, **options,
                )
                token_counts.append(generated.total_tokens)
                total_tokens = (
                    sum(token_counts) if all(n is not None for n in token_counts) else None
                )
                return persist({
                    **base_response,
                    "answer": generated.answer,
                    "citations": generated.citations,
                    "missing_information": generated.missing_information,
                    "generation_status": "completed",
                    "model": generated.model,
                    "total_tokens": total_tokens,
                })
    except RetrievalError as exc:
        raise HTTPException(503, str(exc)) from None
    except GenerationNotConfiguredError as exc:
        return persist({**base_response, "generation_status": "not_configured", "notice": str(exc)})
    except GenerationError as exc:
        if compilation_session:
            logger.warning("DOCX chat model failure error=%s", type(exc).__name__)
            return await interrupted_compilation()
        return persist({**base_response, "generation_status": "failed", "notice": str(exc)})
    except TimeoutError:
        if compilation_session:
            logger.warning("DOCX chat timeout session=%s", compilation_session["id"])
            return await interrupted_compilation()
        return persist({
            **base_response,
            "generation_status": "failed",
            "notice": (
                f"La richiesta non e stata completata entro il limite complessivo di "
                f"{timeout_seconds:g} secondi. Riprova con una domanda piu specifica."
            ),
        })


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


@app.delete(
    "/api/projects/{project_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def project_file_delete(project_id: str, file_id: int) -> Response:
    try:
        deleted = delete_project_file(project_id, file_id)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=500, detail="Impossibile eliminare la fonte; riprova",
        ) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Fonte del progetto non trovata")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
