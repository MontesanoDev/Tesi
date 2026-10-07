from contextlib import contextmanager

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app import compilation_sessions as sessions
from app.ai_profiles import ProfileError, project_ai_context
from app.compilation_session_models import (
    CreateSession,
    FinalizeRequest,
    ResolveRequest,
    UpdateFields,
)
from app.compilation_session_resolution import resolve_session
from app.docx_templates import DocumentInputError, DocxTooLargeError
from app.generation import GenerationError, GenerationNotConfiguredError
from app.retrieval_settings import RetrievalError

router = APIRouter(
    prefix="/api/projects/{project_id}/compilation-sessions", tags=["Sessioni compilazione DOCX"]
)


@contextmanager
def api_errors():
    try:
        yield
    except DocxTooLargeError as exc:
        raise HTTPException(413, str(exc)) from exc
    except DocumentInputError as exc:
        raise HTTPException(422, str(exc)) from exc
    except GenerationNotConfiguredError as exc:
        raise HTTPException(503, str(exc)) from exc
    except (GenerationError, RetrievalError) as exc:
        raise HTTPException(502, str(exc)) from exc
    except ProfileError as exc:
        raise HTTPException(422, str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(504, "Risoluzione scaduta; sessione riprendibile") from exc
    except OSError as exc:
        raise HTTPException(500, "Errore di archiviazione della sessione") from exc


@router.post("", status_code=201)
def create_session(project_id: str, body: CreateSession) -> dict:
    with api_errors():
        return sessions.create_session(project_id, body.form_id, body.conversation_id,
                                       start_in_chat=body.start_in_chat)


@router.get("")
def list_sessions(project_id: str, conversation_id: str | None = None) -> list[dict]:
    return sessions.list_sessions(project_id, conversation_id)


@router.get("/{session_id}")
def get_session(project_id: str, session_id: str) -> dict:
    return sessions.get_session(project_id, session_id)


@router.get("/{session_id}/revisions")
def get_revisions(project_id: str, session_id: str) -> list[dict]:
    return sessions.revisions(project_id, session_id)


@router.post("/{session_id}/resolve")
async def resolve(project_id: str, session_id: str, body: ResolveRequest) -> dict:
    with api_errors(), project_ai_context(project_id):
        try:
            return await resolve_session(project_id, session_id, body.version, body.field_ids,
                                         automatic=body.automatic)
        except GenerationError as exc:
            # Workflow recovery only. The SOURCE engine and its validators reject
            # the entire invalid batch; transport/parser/storage errors still fail.
            if body.automatic and str(exc) == "Output strutturato della risoluzione non valido":
                recovered = await run_in_threadpool(
                    sessions.recover_invalid_automatic_step, project_id, session_id, body.version,
                )
                if recovered is not None:
                    return recovered
            raise


@router.patch("/{session_id}/fields")
def update_fields(project_id: str, session_id: str, body: UpdateFields) -> dict:
    with api_errors():
        return sessions.update_fields(project_id, session_id, body.version, body.fields)


@router.post("/{session_id}/finalize")
async def finalize(project_id: str, session_id: str, body: FinalizeRequest) -> dict:
    with api_errors():
        return await run_in_threadpool(
            sessions.finalize_session, project_id, session_id, body.version, body.allow_unresolved
        )
