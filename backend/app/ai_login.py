"""OpenRouter's documented PKCE code flow; API keys stay on the server."""

import base64
import hashlib
import secrets
import time
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.ai_profiles import ProfileError, _cipher
from app.db import connection

FLOW_LIFETIME = 600


class LoginCode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    connection_token: SecretStr = Field(min_length=32, max_length=200)
    code: SecretStr = Field(min_length=1, max_length=4096)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def begin_login() -> dict:
    token, verifier = secrets.token_urlsafe(48), secrets.token_urlsafe(48)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    )
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM ai_login_flows WHERE expires_at <= ?", (int(time.time()),))
        encrypted = _cipher(create=True).encrypt(verifier.encode()).decode()
        db.execute(
            "INSERT INTO ai_login_flows(token_hash, encrypted_verifier, status, expires_at) "
            "VALUES (?, ?, 'pending', ?)",
            (token_hash(token), encrypted, int(time.time()) + FLOW_LIFETIME),
        )
    # Omitting callback_url is OpenRouter's supported manual-code flow, also usable on a LAN.
    return {
        "connection_token": token,
        "authorization_url": "https://openrouter.ai/auth?"
        + urlencode(
            {
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "key_label": "Mapi RAG",
            }
        ),
        "expires_in": FLOW_LIFETIME,
    }


async def complete_login(payload: LoginCode) -> dict:
    hashed = token_hash(payload.connection_token.get_secret_value())
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM ai_login_flows WHERE token_hash=?", (hashed,)).fetchone()
        if row is None or row["expires_at"] <= time.time() or row["status"] != "pending":
            raise ProfileError("Accesso scaduto o gia utilizzato. Avvia nuovamente l'accesso.")
        from app.ai_profiles import _decrypt

        verifier = _decrypt(row["encrypted_verifier"])
        db.execute("UPDATE ai_login_flows SET status='exchanging' WHERE token_hash=?", (hashed,))
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/auth/keys",
                json={
                    "code": payload.code.get_secret_value().strip(),
                    "code_verifier": verifier,
                    "code_challenge_method": "S256",
                },
            )
            response.raise_for_status()
            data = response.json()
        key = data.get("key") if isinstance(data, dict) else None
        if (
            not isinstance(key, str)
            or not key.strip()
            or len(key) > 4096
            or any(ord(char) < 32 for char in key)
        ):
            raise ValueError("Risposta di autenticazione non valida")
        encrypted = _cipher().encrypt(key.encode()).decode()
        with connection() as db:
            db.execute(
                "UPDATE ai_login_flows SET status='ready', encrypted_api_key=?, "
                "encrypted_verifier=NULL, expires_at=? WHERE token_hash=?",
                (encrypted, int(time.time()) + FLOW_LIFETIME, hashed),
            )
    except httpx.HTTPError, ValueError:
        with connection() as db:
            db.execute("DELETE FROM ai_login_flows WHERE token_hash=?", (hashed,))
        raise ProfileError(
            "Accesso OpenRouter non riuscito. Ricomincia e usa il nuovo codice."
        ) from None
    return {"message": "Account OpenRouter collegato. Scegli il modello e salva."}


def pending_key(token: str) -> str:
    from app.ai_profiles import _decrypt

    with connection() as db:
        row = db.execute(
            "SELECT * FROM ai_login_flows WHERE token_hash=?", (token_hash(token),)
        ).fetchone()
    if row is None or row["status"] != "ready" or row["expires_at"] <= time.time():
        raise ProfileError("Collegamento scaduto. Accedi di nuovo a OpenRouter.")
    key = _decrypt(row["encrypted_api_key"])
    if not key:
        raise ProfileError("Collegamento OpenRouter privo della chiave")
    return key
