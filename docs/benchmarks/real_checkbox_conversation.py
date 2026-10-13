"""Fresh real chat/analysis/USER/export through HTTP ASGI in a private database.

Four bounded user turns, at most two automatic resolves/turn. No mocks, reused
analysis or manually edited sessions. Credentials/private DB are removed on exit.
"""

import argparse
import asyncio
import json
import os
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

import httpx
from pydantic import SecretStr

from app import ai_profiles, intents
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.db import get_db_path, get_storage_path, init_database
from app.main import app
from scripts.benchmark_compilation_dialogue import real_settings

FIXTURE = Path(__file__).resolve().parents[2] / "demo-documents/benchmark-checkbox/v1"
MESSAGES = ["me lo compili?",
            "Per la partecipazione scegliamo la modalità individuale. Il requisito Q non lo so: "
            "salta quella dichiarazione.",
            "Salta i chiarimenti rimasti, senza confermare requisiti non documentati.",
            "Genera una bozza parziale con i dati disponibili e le scelte confermate, "
            "lasciando vuote le parti irrisolte."]


def fingerprint(path):
    import hashlib

    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        result = {}
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        for row in tables.fetchall():
            name = row[0]
            quoted = '"' + name.replace('"', '""') + '"'
            rows = db.execute(f"SELECT * FROM {quoted}").fetchall()
            result[name] = hashlib.sha256(json.dumps(sorted(rows, key=str),
                                                     default=str).encode()).hexdigest()
        return result


async def main(args):
    from benchmark_checkboxes import word_states

    settings = real_settings("prova")
    live_db = get_db_path().resolve()
    before = fingerprint(live_db)
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(raw.replace(settings.api_key, "[REDACTED]") + "\n")

    save("protocol.json", {"fresh_session": True, "new_analysis": True, "real_provider":
         settings.model, "messages": MESSAGES, "max_turns": 4, "max_auto_resolves_per_turn": 2,
         "no_manual_session_edits": True, "no_user_source_values": True,
         "browser": False, "transport": "HTTP ASGI"})
    calls, current = [], "setup"

    def observe(original, stage):
        async def request(client, config, body, timeout, **kwargs):
            name = current + f"/call-{len(calls) + 1:02d}"
            save(name + "-request.json", {"body": body, "schema": kwargs.get("response_schema")})
            start = time.perf_counter()
            raw, model, usage = await original(client, config, body, timeout, **kwargs)
            effective = "guard" if (kwargs.get("response_schema") or {}).get(
                "title") == "ReplyScopeChecks" else stage
            record = {"stage": effective, "path": name, "model": model,
                      "usage": usage, "seconds": time.perf_counter() - start}
            calls.append(record)
            save(name + "-response.json", {"raw": raw, **record})
            return raw, model, usage
        return request

    intents.request_model_content = observe(intents.request_model_content, "routing")
    adapter.request_model_content = observe(adapter.request_model_content, "analysis")
    dialogue.request_model_content = observe(dialogue.request_model_content, "narration")
    previous_env = {key: os.environ.get(key) for key in (
        "MAPI_DB_PATH", "MAPI_STORAGE_PATH", "MAPI_KNOWLEDGE_PATH")}
    try:
        with tempfile.TemporaryDirectory(prefix="mapi-checkbox-real-") as temporary:
            private = Path(temporary)
            os.environ.update(MAPI_DB_PATH=str(private / "db.sqlite"),
                              MAPI_STORAGE_PATH=str(private / "uploads"),
                              MAPI_KNOWLEDGE_PATH=str(private / "knowledge"))
            init_database()
            ai_profiles.save_profile(ai_profiles.ProfileInput(name="Isolated real DeepSeek",
                provider=settings.provider, model=settings.model, base_url=settings.base_url,
                api_key=SecretStr(settings.api_key), context_window=settings.context_window))
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                         base_url="http://isolated", timeout=400) as client:
                response = await client.post("/api/projects", json={"title": "Laboratorio checkbox",
                    "description": "Prova reale isolata su fixture congelata"})
                assert response.status_code == 201, response.text
                project = response.json()["id"]
                for source in json.loads((FIXTURE / "sources.json").read_text()):
                    response = await client.post("/api/global-knowledge/files", files={
                        "file": (source["source_name"], source["content"].encode())},
                        data={"category": source["category"]})
                    assert response.status_code == 201, response.text
                original = (FIXTURE / "modulo.docx").read_bytes()
                response = await client.post(f"/api/projects/{project}/forms", files={
                    "file": ("modulo.docx", original)})
                assert response.status_code == 201, response.text
                form = response.json()["id"]
                state = None
                for index, message in enumerate(MESSAGES):
                    if index == 2 and (state["chat"].get("question") or {}).get(
                        "kind") == "generate":
                        continue
                    current = f"turn-{index + 1:02d}"
                    payload = {"question": message, "document_id": form}
                    if state:
                        payload.update(conversation_id=state["conversation_id"],
                                       compilation_session_id=state["id"],
                                       compilation_version=state["version"])
                    save(current + "/request.json", payload)
                    response = await client.post(f"/api/projects/{project}/answer", json=payload)
                    save(current + "/response.json", {"status": response.status_code,
                                                       "body": response.json()})
                    assert response.status_code == 200, response.text
                    sid = state["id"] if state else response.json()["compilation"]["session_id"]
                    url = f"/api/projects/{project}/compilation-sessions/{sid}"
                    state = (await client.get(url)).json()
                    for step in range(2):
                        if not state["chat"]["auto_continue"]:
                            break
                        response = await client.post(url + "/resolve", json={
                            "version": state["version"], "automatic": True})
                        save(current + f"/resolve-{step}.json", {"status": response.status_code,
                                                               "body": response.json()})
                        assert response.status_code == 200, response.text
                        state = (await client.get(url)).json()
                    save(current + "/state.json", state)
                    assert state == (await client.get(url)).json()
                    print(json.dumps({"turn": index + 1, "status": state["status"],
                                      "question": state["chat"].get("question")}), flush=True)
                artifact = state["global_compilation"]["artifact_path"]
                shutil.copytree(get_storage_path() / artifact, args.output / "analysis")
                if state.get("last_generation"):
                    for kind, url in state["last_generation"]["downloads"].items():
                        response = await client.get(url)
                        assert response.status_code == 200
                        if kind == "report":
                            save("generated-report.json", response.json())
                        else:
                            (args.output / (kind + ".docx")).write_bytes(response.content)
                    assert (args.output / "template.docx").read_bytes() == original
                    save("word-checkbox-states.json", word_states(
                        (args.output / "docx.docx").read_bytes()))
                save("final-state.json", state)
                save("calls.json", calls)
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        unchanged = fingerprint(live_db) == before
        save("integrity.json", {"live_database_unchanged": unchanged,
                                 "private_database_and_key_removed": not private.exists()})
        assert unchanged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
