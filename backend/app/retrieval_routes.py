from fastapi import APIRouter, HTTPException

from app.ai_routes import PrivateSettingsRoute
from app.retrieval_settings import (
    RetrievalError,
    RetrievalInput,
    public_settings,
    resolve_settings,
    save_settings,
)
from app.vector_retrieval import check_connection, run_vector_search

router = APIRouter(
    prefix="/api/settings/retrieval",
    tags=["Ricerca nelle fonti"],
    route_class=PrivateSettingsRoute,
)


@router.get("")
def settings() -> dict:
    return public_settings()


@router.put("")
def update_settings(payload: RetrievalInput) -> dict:
    return save_settings(payload)


@router.post("/check")
def check(payload: RetrievalInput) -> dict:
    try:
        return check_connection(resolve_settings(payload))
    except RetrievalError as exc:
        raise HTTPException(502, str(exc)) from None


@router.post("/index")
def index() -> dict:
    try:
        return run_vector_search(resolve_settings())
    except RetrievalError as exc:
        raise HTTPException(502, str(exc)) from None
