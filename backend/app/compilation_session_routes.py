import logging
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app import compilation_sessions as sessions
from app.ai_profiles import ProfileError, project_ai_context
from app.compilation_session_models import (
    CreateSession,
    FinalizeRequest,
    GlobalDraftRequest,
    ResolveRequest,
    UpdateFields,
)
from app.compilation_session_resolution import (
    CompilationModelError,
    CompilationOutputError,
    resolve_session,
)
from app.docx_templates import DocumentInputError, DocxTooLargeError
from app.generation import GenerationError, GenerationNotConfiguredError
from app.retrieval_settings import RetrievalError

router = APIRouter(
    prefix="/api/projects/{project_id}/compilation-sessions", tags=["Sessioni compilazione DOCX"]
)
logger = logging.getLogger(__name__)


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
                                       start_in_chat=body.start_in_chat, engine=body.engine)


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
        session = await run_in_threadpool(sessions.get_session, project_id, session_id)
        if session.get("engine") == "global":
            from app.compilation_global_sessions import resolve_global

            return await resolve_global(project_id, session_id, body.version, body.field_ids)
        try:
            return await resolve_session(project_id, session_id, body.version, body.field_ids,
                                         automatic=body.automatic)
        except (CompilationModelError, TimeoutError) as exc:
            # Only failures identified at the model boundary or the explicit
            # step timeout are recoverable. Internal mapping bugs still surface.
            logger.warning("DOCX step interrupted session=%s error=%s", session_id,
                           type(exc).__name__)
            if body.automatic:
                recovered = await run_in_threadpool(
                    sessions.recover_invalid_automatic_step, project_id, session_id, body.version,
                    pause=not isinstance(exc, CompilationOutputError),
                    kind=("schema" if isinstance(exc, CompilationOutputError)
                          else "provider_timeout"),
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


@router.post("/{session_id}/global-draft")
async def global_draft(project_id: str, session_id: str, body: GlobalDraftRequest) -> dict:
    from app.compilation_global_sessions import generate_draft

    with api_errors():
        return await run_in_threadpool(generate_draft, project_id, session_id, body)


@router.get("/{session_id}/global-report")
def global_report(project_id: str, session_id: str) -> FileResponse:
    from app.compilation_global_sessions import report_path

    return FileResponse(report_path(project_id, session_id), media_type="application/json",
                        filename="proposte-compilazione.json",
                        headers={"Cache-Control": "no-store"})
