"""Fresh real chat/analysis/USER/export through HTTP ASGI in a private database.

Four bounded user turns, at most two automatic resolves/turn. Frozen SOURCE import
via repository (not reingestion); same chunk content as the recorded Minervino test.
No mocks, reused analysis or manually edited sessions. Private DB/key removed on exit.
"""

import argparse
import asyncio
import hashlib
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

FIXTURE = (Path(__file__).resolve().parents[2]
           / "backend/data/compilation-audit/minervino-output-20261013/analysis")
MESSAGES = ["me lo compili?",
            "Confermo che partecipiamo come società di ingegneria. "
            "La carica del sottoscrittore lasciala vuota.",
            "Non ho altre informazioni. Salta soltanto le domande sui dati mancanti; "
            "non confermare condizioni ancora incerte.",
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

    settings = real_settings("minervino-di-lecce-elenco-sia")
    application = Path(__file__).resolve().parents[2] / "backend/app"
    frozen_code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in application.glob("*.py")}
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
         "browser": False, "transport": "HTTP ASGI", "application_files": frozen_code})
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
        with tempfile.TemporaryDirectory(prefix="mapi-text-real-") as temporary:
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
                response = await client.post("/api/projects", json={"title": "Laboratorio testuale",
                    "description": "Prova reale isolata su fixture congelata"})
                assert response.status_code == 201, response.text
                project = response.json()["id"]
                from collections import defaultdict

                from app.compilation_global import load_document_corpus
                from app.db import connection
                from app.ingestion import IngestedDocument
                from app.repository import add_global_document, add_project_file

                frozen = json.loads((FIXTURE / "input.json").read_text())["sources"]
                get_storage_path().mkdir(parents=True, exist_ok=True)
                grouped = defaultdict(list)
                for source in frozen:
                    grouped[(source["file_id"], source["category"],
                             source["source_name"])].append(source)
                for index, ((_, category, name), rows) in enumerate(grouped.items()):
                    chunks = [r["content"] for r in sorted(rows, key=lambda r: r["chunk_index"])]
                    relative = f"source-{index}.txt"
                    contents = "\n".join(chunks).encode()
                    (get_storage_path() / relative).write_bytes(contents)
                    document = IngestedDocument(name=name, storage_path=relative,
                        mime_type="text/plain", byte_size=len(contents), page_count=1,
                        chunks=chunks)
                    if category:
                        add_global_document(document, category)
                    else:
                        add_project_file(project, document)
                with connection() as db:
                    imported = load_document_corpus(db, project)
                def corpus(records):
                    return sorted((r["source_name"], r["category"] or "project",
                                   r["chunk_index"], r["content"]) for r in records)
                assert corpus(imported) == corpus(frozen)
                save("source-import.json", {"same_chunk_contents": True, "chunks": len(imported),
                                            "ids_remapped": True, "ingestion_measured": False})
                original = (FIXTURE / "original.docx").read_bytes()
                response = await client.post(f"/api/projects/{project}/forms", files={
                    "file": ("domanda-iscrizione.docx", original)})
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
                        "message": (state["chat"].get("question") or {}).get("message")},
                        ensure_ascii=False), flush=True)
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
        code_unchanged = all(hashlib.sha256((application / name).read_bytes()).hexdigest() == sha
                             for name, sha in frozen_code.items())
        save("integrity.json", {"live_database_unchanged": unchanged,
            "private_database_and_key_removed": not private.exists(),
            "application_unchanged": code_unchanged})
        assert unchanged and code_unchanged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
