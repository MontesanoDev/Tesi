import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.ai_discovery import discover_models
from app.ai_profiles import ProfileInput
from app.ai_routes import PrivateSettingsRoute
from app.config import AISettings
from app.embedding_providers import EMBEDDING_PROVIDERS, EmbeddingProvider
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


class EmbeddingServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    embedding_url: str = Field(max_length=500)
    embedding_provider: EmbeddingProvider = "ollama"
    embedding_api_key: SecretStr | None = None
    clear_embedding_api_key: bool = False

    @field_validator("embedding_url")
    @classmethod
    def clean_url(cls, value: str) -> str:
        return ProfileInput.clean_url(value)


@router.get("/providers")
def embedding_providers() -> list[dict]:
    return list(EMBEDDING_PROVIDERS)


@router.post("/models")
async def embedding_models(payload: EmbeddingServiceInput) -> dict:
    """Read embedding-capable models; never index, download or generate."""
    values = {k: v for k, v in public_settings().items() if not k.startswith("has_")}
    # Use the existing embedding credential guard. Qdrant credentials are neither
    # needed nor decrypted for this read-only probe; nothing is saved here.
    values.update(payload.model_dump(), clear_qdrant_api_key=True)
    config = resolve_settings(RetrievalInput(**values))
    try:
        models = await discover_models(AISettings(
            provider=config.embedding_provider, model=config.embedding_model,
            base_url=config.embedding_url, api_key=config.embedding_api_key,
        ), ollama_capability="embedding")
    except httpx.HTTPStatusError as exc:
        message = (
            "Accesso al provider non autorizzato. Controlla la chiave del servizio embedding."
            if exc.response.status_code in {401, 403}
            else "Elenco modelli non disponibile. Controlla l'indirizzo del servizio embedding."
        )
        raise HTTPException(502, detail=message) from None
    except httpx.HTTPError, ValueError, AttributeError:
        raise HTTPException(
            502, detail="Impossibile leggere i modelli. Controlla il collegamento al provider.",
        ) from None
    return {"models": models}


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
