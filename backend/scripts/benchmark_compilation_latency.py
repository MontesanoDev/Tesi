"""Real, bounded compilation benchmark on an isolated copy; never saves credentials.

Run from backend with PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_latency.py
--help. Audit files go to --output; SQLite/index working copies are temporary.
Instrumentation delegates to the original provider and application functions.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.ai_profiles import resolve_project_settings
from app.config import use_ai_settings
from app.db import get_db_path, get_storage_path
from app.retrieval_settings import public_settings


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--form-id", type=int, required=True)
    parser.add_argument("--profile-project", required=True,
                        help="Read this project's AI profile without changing project settings")
    parser.add_argument("--output", type=Path, required=True, help="New, durable audit directory")
    parser.add_argument("--max-steps", type=int, default=6)
    parser.add_argument("--max-seconds", type=int, default=420)
    parser.add_argument("--stop-candidate-id", action="append", default=[],
                        help="Stop once all these candidates are RESOLVED/SOURCE")
    args = parser.parse_args()
    if not 1 <= args.max_steps <= 36 or not 1 <= args.max_seconds <= 600:
        parser.error("Use 1..36 steps and 1..600 seconds")
    return args


def run(args):
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    settings = resolve_project_settings(args.profile_project)
    retrieval = public_settings()
    original_db = get_db_path().resolve()
    original_storage = get_storage_path().resolve()
    # Credentials remain in memory. Do not export headers, settings objects or the DB.
    secret = settings.api_key

    def redact(value):
        if isinstance(value, dict):
            return {str(k): redact(v) for k, v in value.items()
                    if not any(word in str(k).lower()
                               for word in ("api_key", "authorization", "encrypted",
                                            "token_secret"))}
        if isinstance(value, (list, tuple, set)):
            return [redact(v) for v in value]
        if isinstance(value, str):
            return value.replace(secret, "[REDACTED]") if secret else value
        if hasattr(value, "model_dump"):
            return redact(value.model_dump(mode="json"))
        return value

    def save(name, value):
        (root / name).write_text(json.dumps(redact(value), ensure_ascii=False, indent=2))

    report = {"started_at": datetime.now(UTC).isoformat(), "root": str(root),
              "http": [], "model": [], "stages": [], "steps": [],
              "budget": {"max_steps": args.max_steps, "max_seconds": args.max_seconds}}

    def emit(kind, payload):
        print(kind, json.dumps(redact(payload), ensure_ascii=False), flush=True)
        with (root / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"at": datetime.now(UTC).isoformat(),
                                     "event": kind, "data": redact(payload)},
                                    ensure_ascii=False) + "\n")
        save("metrics.json", report)

    backend = Path(__file__).resolve().parents[1]
    repo = backend.parent
    shutil.copy2(__file__, root / "benchmark-script.py")
    save("code.json", {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "status": subprocess.check_output(["git", "status", "--short", "--branch"],
                                          cwd=repo, text=True),
        "app_sha256": {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (backend / "app").glob("*.py")},
    })
    with tempfile.TemporaryDirectory(prefix="mapi-compilation-benchmark-") as directory:
        work = Path(directory)
        with sqlite3.connect(f"file:{original_db}?mode=ro", uri=True) as source:
            source.row_factory = sqlite3.Row
            row = source.execute("SELECT * FROM project_files WHERE id=? AND project_id=?",
                                 (args.form_id, args.project)).fetchone()
            if row is None:
                raise SystemExit("Form not found in requested project")
            original = (original_storage / row["storage_path"]).read_bytes()
            with sqlite3.connect(work / "snapshot.db") as target:
                source.backup(target)
        upload = work / "uploads" / row["storage_path"]
        upload.parent.mkdir(parents=True, exist_ok=True)
        upload.write_bytes(original)
        (root / "original.docx").write_bytes(original)
        if retrieval["backend"] == "qdrant":
            if retrieval["qdrant_mode"] != "local":
                raise SystemExit("Remote Qdrant is not eligible for isolated diagnostics")
            shutil.copytree(str(original_db) + ".qdrant", str(work / "snapshot.db") + ".qdrant",
                            ignore=shutil.ignore_patterns(".lock"))
        os.environ["MAPI_DB_PATH"] = str(work / "snapshot.db")
        os.environ["MAPI_STORAGE_PATH"] = str(work / "uploads")
        os.environ["MAPI_KNOWLEDGE_PATH"] = str(work / "knowledge")
        report["configuration"] = {
            "project": args.project, "form_id": args.form_id, "document": row["name"],
            "profile_project": args.profile_project, "provider": settings.provider,
            "model": settings.model, "context_window": settings.context_window,
            "retrieval": retrieval["backend"],
            "original_sha256": hashlib.sha256(original).hexdigest(),
            "scope": ("create_session + automatic resolve service; "
                      "no USER input, no DOCX generation"),
        }
        emit("CONFIG", report["configuration"])

        from app import compilation_session_resolution as resolution
        from app import compilation_sessions as sessions
        from app import generation, intents, source_planning

        real_post = httpx.AsyncClient.post

        async def measured_post(self, url, *positional, **kwargs):
            number = len(report["http"]) + 1
            body = kwargs.get("json") or {}
            save(f"http-{number:02d}-request.json", body)
            entry = {"id": number, "endpoint": str(url).split("?")[0].split("/")[-1],
                     "model": body.get("model")}
            start = time.perf_counter()
            try:
                response = await real_post(self, url, *positional, **kwargs)
                entry["status"] = response.status_code
                try:
                    data = response.json()
                    save(f"http-{number:02d}-response.json", data)
                    entry["usage"] = data.get("usage")
                    for key in ("total_duration", "load_duration", "prompt_eval_duration",
                                "eval_duration"):
                        if isinstance(data.get(key), (int, float)):
                            entry[key + "_seconds"] = round(data[key] / 1e9, 4)
                except ValueError:
                    save(f"http-{number:02d}-response.json", {"text": response.text})
                return response
            except BaseException as exc:
                entry["error"] = type(exc).__name__
                raise
            finally:
                entry["seconds"] = round(time.perf_counter() - start, 4)
                report["http"].append(entry)
                emit("HTTP", entry)

        httpx.AsyncClient.post = measured_post
        real_request = generation.request_model_content

        async def measured_model(client, model_settings, body, timeout, **kwargs):
            number = len(report["model"]) + 1
            title = (kwargs.get("response_schema") or {}).get("title", "unstructured")
            prefix = f"model-{number:02d}-{title}"
            save(prefix + "-request.json", {"body": body, "timeout_seconds": timeout,
                                          "response_schema": kwargs.get("response_schema")})
            entry = {"id": number, "schema": title, "max_tokens": body.get("max_tokens"),
                     "input_characters": sum(len(m["content"]) for m in body["messages"])}
            emit("MODEL_START", entry)
            start = time.perf_counter()
            try:
                result = await real_request(client, model_settings, body, timeout, **kwargs)
                raw, returned_model, usage = result
                (root / (prefix + "-response.txt")).write_text(redact(raw))
                save(prefix + "-response.json", {"content": raw, "model": returned_model,
                                               "usage": usage})
                entry.update(output_characters=len(raw), usage=usage)
                return result
            except BaseException as exc:
                entry["error"] = type(exc).__name__
                raise
            finally:
                entry["seconds"] = round(time.perf_counter() - start, 4)
                report["model"].append(entry)
                emit("MODEL_END", entry)

        for module in (generation, resolution, intents, source_planning):
            if hasattr(module, "request_model_content"):
                module.request_model_content = measured_model

        def wrap(function, phase):
            async def measured(*positional, **kwargs):
                number = len(report["stages"]) + 1
                entry = {"phase": phase}
                start = time.perf_counter()
                try:
                    result = await function(*positional, **kwargs)
                    save(f"stage-{number:02d}-{phase}.json", result)
                    return result
                except BaseException as exc:
                    entry["error"] = type(exc).__name__
                    raise
                finally:
                    entry["seconds"] = round(time.perf_counter() - start, 4)
                    report["stages"].append(entry)
                    emit("STAGE", entry)
            return measured

        for name in ("plan_document", "classify_candidates", "review_meanings",
                     "retrieve_sources", "match_candidates", "review_sources"):
            setattr(resolution, name, wrap(getattr(resolution, name), name))

        async def main():
            with use_ai_settings(settings):
                start = time.perf_counter()
                session = sessions.create_session(args.project, args.form_id, start_in_chat=True)
                report["create_seconds"] = round(time.perf_counter() - start, 4)
                save("created-session.json", session)
                emit("CREATE", {"seconds": report["create_seconds"], "id": session["id"],
                                "summary": session["summary"]})
                run_start = time.perf_counter()
                report["stop_reason"] = "step_budget"
                try:
                    async with asyncio.timeout(args.max_seconds):
                        for step in range(1, args.max_steps + 1):
                            start = time.perf_counter()
                            session = await resolution.resolve_session(
                                args.project, session["id"], session["version"], automatic=True,
                            )
                            save(f"step-{step:02d}-session.json", session)
                            entry = {"step": step, "seconds": round(time.perf_counter() - start, 4),
                                     "status": session["status"], "summary": session["summary"],
                                     "diagnostics": session.get("last_resolution")}
                            report["steps"].append(entry)
                            emit("STEP", entry)
                            indexed = {f["id"]: f for f in session["fields"]}
                            if args.stop_candidate_id and all(
                                indexed.get(key, {}).get("status") == "RESOLVED"
                                and indexed[key].get("provenance") == "SOURCE"
                                for key in args.stop_candidate_id
                            ):
                                report["stop_reason"] = "requested_candidates_resolved"
                                break
                            if session["status"] in {
                                "READY", "WAITING_FOR_USER", "FAILED", "GENERATED",
                            }:
                                report["stop_reason"] = session["status"]
                                break
                except BaseException as exc:
                    report["stop_reason"] = type(exc).__name__
                    report["failure"] = {"type": type(exc).__name__, "detail": str(exc)}
                    emit("FAILURE", report["failure"])
                finally:
                    session = sessions.get_session(args.project, session["id"])
                    report["elapsed_seconds"] = round(time.perf_counter() - run_start, 4)
                    report["final_summary"] = session["summary"]
                    save("final-session.json", session)
                    save("revisions.json", sessions.revisions(args.project, session["id"]))
                    with (root / "fields.csv").open("w", newline="") as stream:
                        writer = csv.writer(stream)
                        writer.writerow(("candidate", "label", "requirement", "value", "status",
                                         "provenance", "source_chunk_ids", "validation_errors"))
                        for field in session["fields"]:
                            writer.writerow(redact([
                                field["id"], field["label"], field.get("requirement"),
                                field["value"], field["status"], field["provenance"],
                                [e.get("chunk_id") for e in field["source_evidence"]],
                                field["validation_errors"],
                            ]))
                    emit("COMPLETE", {"summary": session["summary"],
                                      "elapsed_seconds": report["elapsed_seconds"],
                                      "stop_reason": report["stop_reason"], "output": str(root)})

        asyncio.run(main())
    save("manifest.json", {
        "finished_at": datetime.now(UTC).isoformat(),
        "note": ("No persisted DB, keys, auth headers, USER input or generated draft. "
                 "Real providers."),
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in root.iterdir() if p.is_file() and p.name != "manifest.json"},
    })


if __name__ == "__main__":
    run(arguments())
