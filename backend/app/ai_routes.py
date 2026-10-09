from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

from app.ai_discovery import discover_models
from app.ai_login import LoginCode, begin_login, complete_login
from app.ai_profiles import (
    ProfileError,
    ProfileInput,
    delete_profile,
    list_settings,
    project_selection,
    save_profile,
    select_project_profile,
    set_default,
    settings_for_input,
)


class PrivateSettingsRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def private_handler(request):
            try:
                response = await handler(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except RequestValidationError as exc:
                # FastAPI's default validation errors may echo the entire secret-bearing body.
                raise HTTPException(
                    422,
                    detail=[
                        {key: error[key] for key in ("loc", "msg", "type")}
                        for error in exc.errors()
                    ],
                ) from None
            except ProfileError as exc:
                raise HTTPException(422, detail=str(exc)) from None
            except LookupError as exc:
                raise HTTPException(404, detail=str(exc)) from None

        return private_handler


router = APIRouter(prefix="/api", tags=["Modelli AI"], route_class=PrivateSettingsRoute)


class ProfileChoice(BaseModel):
    profile_id: str | None = Field(default=None, max_length=100)
    thinking: bool | None = None


class ProbeInput(ProfileInput):
    profile_id: str | None = Field(default=None, max_length=100)


@router.get("/settings/ai")
def settings() -> dict:
    return list_settings()


@router.post("/settings/ai/openrouter/login")
def openrouter_login() -> dict:
    return begin_login()


@router.post("/settings/ai/openrouter/login/complete")
async def openrouter_login_complete(payload: LoginCode) -> dict:
    return await complete_login(payload)


@router.post("/settings/ai/profiles", status_code=201)
def create_profile(payload: ProfileInput) -> dict:
    return save_profile(payload)


@router.put("/settings/ai/profiles/{profile_id}")
def update_profile(profile_id: str, payload: ProfileInput) -> dict:
    return save_profile(payload, profile_id)


@router.delete("/settings/ai/profiles/{profile_id}", status_code=204)
def remove_profile(profile_id: str) -> Response:
    delete_profile(profile_id)
    return Response(status_code=204)


@router.put("/settings/ai/default")
def default_profile(payload: ProfileChoice) -> dict:
    return set_default(payload.profile_id)


@router.get("/projects/{project_id}/ai-model")
def selected_model(project_id: str) -> dict:
    return project_selection(project_id)


@router.put("/projects/{project_id}/ai-model")
def choose_model(project_id: str, payload: ProfileChoice) -> dict:
    return select_project_profile(project_id, payload.profile_id, payload.thinking)


@router.post("/settings/ai/check")
async def check_connection(payload: ProbeInput) -> dict:
    """Discover models without sending documents or making a paid generation request."""
    settings = settings_for_input(payload, payload.profile_id)
    try:
        models = await discover_models(settings)
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        if code in {401, 403}:
            message = "Chiave API non valida o accesso non autorizzato. Controlla le credenziali."
        elif code == 404:
            message = "Elenco modelli non trovato. Controlla l'indirizzo del servizio."
        else:
            message = f"Il servizio AI ha risposto con errore {code}. Riprova piu tardi."
        raise HTTPException(502, detail=message) from None
    except httpx.HTTPError, ValueError, AttributeError:
        raise HTTPException(
            502,
            detail="Servizio non raggiungibile o risposta non valida. "
            "Controlla l'indirizzo e che il servizio sia raggiungibile dal server Mapi, "
            "anche se si trova su un altro computer.",
        ) from None
    return {
        "models": models,
        "message": (
            "Collegamento riuscito. Scegli un modello dall'elenco."
            if models
            else "Collegamento riuscito, ma nessun modello disponibile. "
            "Controlla i modelli installati o l'accesso al servizio."
        ),
    }
