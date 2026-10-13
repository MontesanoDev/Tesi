"""Real follow-up workflow on a recorded SOURCE proposal in a private database.

No new global analysis, no simulated provider, no live-session mutation or DOCX export.
"""

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import httpx
from pydantic import SecretStr

from app import ai_profiles, compilation_global_dialogue, compilation_sessions, intents
from app.compilation_global import (
    build_global_input,
    load_document_corpus,
    validate_global_proposal,
)
from app.db import connection, get_db_path, get_storage_path, init_database
from app.docx_templates import inspect_docx
from app.main import app
from app.project_forms import _save_form
from app.repository import create_project, get_conversation, save_conversation_turn
from app.schemas import ProjectCreate
from scripts.benchmark_compilation_dialogue import real_settings

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "backend/data/compilation-audit/conversation-flow-20261013"
MESSAGES = ["1 si 2 si e 3 lascia in bianco", "di ingegneria"]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def seed_sources(sources, project):
    grouped = defaultdict(list)
    for source in sources:
        grouped[(source["file_id"], source["source_name"], source["category"])].append(source)
    storage = get_storage_path()
    storage.mkdir(parents=True, exist_ok=True)
    with connection() as db:
        for (fid, name, category), rows in grouped.items():
            relative = f"source-{fid}.txt"
            (storage / relative).write_text("\n".join(r["content"] for r in rows))
            if fid < 0:
                db.execute("INSERT INTO global_documents(id,name,category,metadata,status,"
                    "storage_path,mime_type,byte_size,page_count,chunk_count) "
                    "VALUES (?,?,?,'Fixture','Indicizzato',?,'text/plain',0,1,?)",
                    (-fid, name, category, relative, len(rows)))
                for r in rows:
                    db.execute("INSERT INTO global_document_chunks "
                               "(id,document_id,chunk_index,content,char_count) VALUES (?,?,?,?,?)",
                               (-r["chunk_id"], -fid, r["chunk_index"], r["content"],
                                len(r["content"])))
            else:
                db.execute("INSERT INTO project_files(id,project_id,name,metadata,kind,status,"
                    "storage_path,mime_type,byte_size,page_count,chunk_count) "
                    "VALUES (?,?,?,'Fixture','source','Indicizzato',?,'text/plain',0,1,?)",
                    (fid, project, name, relative, len(rows)))
                for r in rows:
                    db.execute("INSERT INTO document_chunks "
                               "(id,project_id,file_id,chunk_index,content,char_count) "
                               "VALUES (?,?,?,?,?,?)", (
                        r["chunk_id"], project, fid, r["chunk_index"], r["content"],
                        len(r["content"])))


async def main(args):
    from real_text_conversation import fingerprint

    settings = real_settings("minervino-di-lecce-elenco-sia")
    live_db = get_db_path().resolve()
    live_before = fingerprint(live_db)
    code = {p.name: digest(p.read_bytes()) for p in (REPO / "backend/app").glob("*.py")}
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(text.replace(settings.api_key, "[REDACTED]") + "\n")

    calls, current = [], "initial"
    save("live-database-before.json", live_before)

    def observe(original, stage):
        async def request(client, config, body, timeout, **kwargs):
            name = current + f"/call-{len(calls) + 1:02d}"
            record = {"stage": "guard" if kwargs.get("response_schema", {}).get(
                "title") == "ReplyScopeChecks" else stage, "path": name}
            calls.append(record)
            save(name + "-request.json", {"body": body, "schema": kwargs.get("response_schema")})
            start = time.perf_counter()
            raw, model, usage = await original(client, config, body, timeout, **kwargs)
            record.update(model=model, usage=usage, seconds=time.perf_counter() - start)
            save(name + "-response.json", {"raw": raw, **record})
            return raw, model, usage
        return request

    intents.request_model_content = observe(intents.request_model_content, "routing")
    compilation_global_dialogue.request_model_content = observe(
        compilation_global_dialogue.request_model_content, "narration")
    material = ROOT / "diagnosis/analysis"
    messages = (["riprendi", "Sì, confermo di presentare la domanda come legale rappresentante "
                 "dell'operatore economico"] if args.resume_existing else MESSAGES)
    raw = (material / "response.txt").read_text()
    original = (material / "original.docx").read_bytes()
    source_snapshot = json.loads((material / "input.json").read_text())["sources"]
    save("protocol.json", {"recorded_source_proposal": digest(raw.encode()),
        "original_sha256": digest(original), "new_analysis_calls": 0, "messages": messages,
        "resume_existing_checkpoint": args.resume_existing,
        "application_files": code, "model": settings.model, "provider_simulated": False,
        "prepared_checkpoint": True, "max_resolves_per_turn": 2, "export_requested": False})
    previous = {k: os.environ.get(k) for k in (
        "MAPI_DB_PATH", "MAPI_STORAGE_PATH", "MAPI_KNOWLEDGE_PATH")}
    try:
        with tempfile.TemporaryDirectory(prefix="mapi-real-followup-") as temporary:
            private = Path(temporary)
            os.environ.update(MAPI_DB_PATH=str(private / "private.db"),
                MAPI_STORAGE_PATH=str(private / "uploads"), MAPI_KNOWLEDGE_PATH=str(private / "kb"))
            init_database()
            ai_profiles.save_profile(ai_profiles.ProfileInput(name="Private real provider",
                provider=settings.provider, model=settings.model, base_url=settings.base_url,
                api_key=SecretStr(settings.api_key), context_window=settings.context_window))
            project = create_project(ProjectCreate(
                title="Replay dialogo", description="Fixture"))["id"]
            seed_sources(source_snapshot, project)
            form = _save_form(project, "domanda-iscrizione.docx", original)
            s = compilation_sessions.create_session(project, form["id"], engine="global",
                                                      start_in_chat=True)
            layout = inspect_docx(original)
            with connection() as db:
                sources = load_document_corpus(db, project)
                def corpus(records):
                    return sorted((r["chunk_id"], r["content"], r["category"]) for r in records)
                assert corpus(sources) == corpus(source_snapshot)
                row = compilation_sessions._row(db, project, s["id"])
                state = json.loads(row["state_json"])
                data = build_global_input(layout, project, sources)
                audit = validate_global_proposal(raw, layout, project, sources, expected_version=11)
                folder = (get_storage_path() / project / "_global_compilations"
                          / s["id"] / "recorded")
                folder.mkdir(parents=True)
                (folder / "response.txt").write_text(raw)
                (folder / "original.docx").write_bytes(original)
                state["global_compilation"].update(phase="REVIEW", attempts=1, contract_version=11,
                    audit=audit, catalog=data["form"], reading_plan=data["reading_plan"],
                    artifact_path=str(folder.relative_to(get_storage_path())),
                    dialogue={"phase": "PENDING", "answers": {}, "user_values": {}})
                if args.resume_existing:
                    checkpoint = json.loads((ROOT / "diagnosis/session-state.json").read_text())
                    state["global_compilation"]["dialogue"] = checkpoint[
                        "global_compilation"]["dialogue"]
                state.update(status="WAITING_FOR_USER")
                s = compilation_sessions.save_state(db, row, state, "fixture_recorded_proposal")
            save_conversation_turn(s["conversation_id"], {"question": "Compila il modulo",
                "answer": "Ricevuta provvisoria", "generation_status": "direct",
                "compilation": {"session_id": s["id"], "action": "start"}})
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                         base_url="http://private", timeout=120) as client:
                url = f"/api/projects/{project}/compilation-sessions/{s['id']}"
                if not args.resume_existing:
                    response = await client.post(url + "/resolve", json={"version": s["version"]})
                    assert response.status_code == 200, response.text
                    s = response.json()
                before_fields = s["global_compilation"]["fields"]
                save("initial/state.json", s)
                for index, message in enumerate(messages, 1):
                    current = f"turn-{index}"
                    response = await client.post(f"/api/projects/{project}/answer", json={
                        "question": message, "document_id": form["id"],
                        "conversation_id": s["conversation_id"], "compilation_session_id": s["id"],
                        "compilation_version": s["version"]})
                    save(current + "/response.json", {"status": response.status_code,
                                                       "body": response.json()})
                    assert response.status_code == 200, response.text
                    s = (await client.get(url)).json()
                    for _ in range(2):
                        if not s["chat"]["auto_continue"]:
                            break
                        response = await client.post(url + "/resolve", json={
                            "version": s["version"]})
                        assert response.status_code == 200, response.text
                        s = response.json()
                    assert before_fields == s["global_compilation"]["fields"]
                    assert s["last_generation"] is None
                    save(current + "/state.json", s)
                    print(json.dumps({"turn": index, "message": s["global_compilation"][
                        "dialogue"]["message"]}, ensure_ascii=False), flush=True)
                save("conversation.json", get_conversation(project, s["conversation_id"]))
                save("calls.json", calls)
                shutil.copytree(folder, args.output / "artifact")
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        live_after = fingerprint(live_db)
        save("live-database-after.json", live_after)
        unchanged = live_after == live_before
        code_unchanged = all(digest((REPO / "backend/app" / p).read_bytes()) == sha
                             for p, sha in code.items())
        save("integrity.json", {"live_database_unchanged": unchanged,
            "application_unchanged": code_unchanged, "private_db_removed": not private.exists(),
            "changed_tables": sorted(k for k in set(live_before) | set(live_after)
                                     if live_before.get(k) != live_after.get(k))})
        assert unchanged and code_unchanged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume-existing", action="store_true")
    asyncio.run(main(parser.parse_args()))
