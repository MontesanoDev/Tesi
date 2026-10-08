"""Prepare/replay a single global DeepSeek call on immutable isolated inputs.

Run without --live first. A live run never invokes retrieval, session resolution,
retries or repairs. Results, originals and full raw response stay under --output.
No original database, session or document is written. No secrets are serialized.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import sqlite3
import time
from contextlib import closing
from pathlib import Path

import httpx

from app.ai_profiles import resolve_project_settings
from app.ai_providers import provider_headers
from app.db import get_db_path, get_knowledge_path, get_storage_path
from app.docx_templates import fill_docx, inspect_docx
from app.global_compilation import (
    MAX_OUTPUT_TOKENS,
    PROMPT_VERSION,
    GlobalPlan,
    represent_form,
    request_body,
    validate_plan,
)
from app.ingestion import _extract_text


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def read_db(path):
    db = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def fingerprint():
    with closing(read_db(get_db_path())) as db:
        # Logical hashes include all original sessions, revisions and project data.
        tables = [r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )]
        database = {table: digest(json.dumps(sorted(
            [tuple(r) for r in db.execute(f'SELECT * FROM "{table}"')], key=repr,
        ), ensure_ascii=False, default=str).encode()) for table in tables}
    files = {}
    for root in [get_storage_path(), get_knowledge_path()]:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                files[str(path)] = digest(path.read_bytes())
    return {"tables": database, "files": files}


def source_document(row, path, scope, category, output):
    data = path.read_bytes()
    (output / f"{row['id']}{path.suffix}").write_bytes(data)
    text, pages = _extract_text(path, path.suffix.lower())
    return {"id": row["id"], "role": "source", "scope": scope, "category": category,
            "document_id": row["document_id"], "source_name": row["name"],
            "sha256": digest(data), "page_count": pages, "content": text,
            "lines": [{"line": i, "text": t} for i, t in enumerate(text.splitlines(), 1)],
            "extraction": "complete stored text; PDF reading order from pypdf"}


def prepare(session_id, output, max_tokens):
    if output.exists():
        raise ValueError("Output già esistente: usa --live sui dati preparati o un percorso nuovo")
    output.mkdir(parents=True)
    (output / "sources").mkdir()
    dump(output / "preservation-before.json", fingerprint())
    with closing(read_db(get_db_path())) as src, closing(
        sqlite3.connect(output / "snapshot.db")
    ) as dst:
        src.backup(dst)
    with closing(read_db(output / "snapshot.db")) as db:
        row = db.execute("SELECT * FROM compilation_sessions WHERE id=?", (session_id,)).fetchone()
        if row is None:
            raise ValueError("Sessione non trovata")
        project_id, form_id = row["project_id"], row["form_id"]
        state = json.loads(row["state_json"])
        original = db.execute(
            "SELECT * FROM project_files WHERE id=? AND project_id=? AND kind='form'",
            (form_id, project_id),
        ).fetchone()
        if original is None:
            raise ValueError("Originale non trovato nel progetto della sessione")
        data = (get_storage_path() / original["storage_path"]).read_bytes()
        layout = inspect_docx(data)
        if layout.sha256 != state["template_sha256"]:
            raise ValueError("L'originale non coincide con la sessione")
        (output / "original.docx").write_bytes(data)
        form = represent_form(layout) | {"project_id": project_id, "form_id": form_id,
                                        "source_name": original["name"]}
        candidates = {c["id"]: c for c in form["candidates"]}
        sources, users, excluded = [], [], []
        for source in db.execute("SELECT * FROM global_documents ORDER BY id"):
            sources.append(source_document(
                {"id": f"global:{source['id']}", "document_id": source["id"],
                 "name": source["name"]}, get_storage_path() / source["storage_path"],
                "global", source["category"], output / "sources",
            ))
        for source in db.execute("SELECT * FROM project_files WHERE project_id=? ORDER BY id",
                                 (project_id,)):
            if source["kind"] == "source":
                sources.append(source_document(
                    {"id": f"project:{source['id']}", "document_id": source["id"],
                     "name": source["name"]}, get_storage_path() / source["storage_path"],
                    f"project:{project_id}", None, output / "sources",
                ))
            elif source["kind"] == "artifact" and source["name"] == "project-facts.md":
                text = (get_knowledge_path() / source["storage_path"]).read_text()
                users.append({"id": f"project-user:{source['id']}", "origin": "USER",
                              "text": text, "project_id": project_id,
                              "source_name": source["name"]})
            else:
                excluded.append({"file_id": source["id"], "name": source["name"],
                                 "kind": source["kind"], "reason": "Not factual SOURCE"})
        for field in state["fields"]:
            if field.get("provenance") != "USER":
                continue
            applicability = field.get("applicability") or {}
            candidate = candidates[field["id"]]
            users.append({"id": f"session-user:{field['id']}", "origin": "USER",
                          "session_id": session_id, "session_version": row["version"],
                          "candidate_id": field["id"], "section_id": candidate["section_id"],
                          "condition": applicability.get("condition", field.get("condition")),
                          "applies": applicability.get("applies"), "value": field.get("value"),
                          "text": field["reason"], "status": field["status"]})
    settings = resolve_project_settings(project_id)
    body = request_body(settings, form, sources, users, max_tokens=max_tokens)
    dump(output / "inputs.json", {"FORM": form, "SOURCE": sources, "USER": users})
    dump(output / "request.json", body)
    manifest = {"prompt_version": PROMPT_VERSION, "session_id": session_id,
                "session_version": row["version"], "project_id": project_id,
                "model": settings.model, "provider": settings.provider,
                "base_url": settings.base_url, "saved_context_window": settings.context_window,
                "max_output_tokens": max_tokens, "candidate_count": len(candidates),
                "source_documents": len(sources),
                "source_characters": sum(len(s["content"]) for s in sources),
                "user_decisions": sum("candidate_id" in u for u in users),
                "excluded_project_documents": excluded,
                "request_bytes": len(json.dumps(body, ensure_ascii=False).encode()),
                "request_sha256": digest(json.dumps(body, ensure_ascii=False).encode()),
                "status": "prepared", "model_calls": 0}
    dump(output / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def validate_response(output, *, report_name="validation.json"):
    """Offline revalidation of the SAME response; never calls a model."""
    inputs = json.loads((output / "inputs.json").read_text())
    envelope = json.loads((output / "response.json").read_text())
    choice = envelope["choices"][0]
    raw = choice["message"]["content"]
    (output / "plan-raw.json").write_text(raw, encoding="utf-8")
    layout = inspect_docx((output / "original.docx").read_bytes())
    if (inputs["FORM"]["sha256"] != layout.sha256
            or {c["id"] for c in inputs["FORM"]["candidates"]} != layout.candidate_ids):
        raise ValueError("FORM congelato non coerente con hash/catalogo dell'originale")
    try:
        plan = GlobalPlan.model_validate_json(raw)
    except ValueError as exc:
        # Avoid echoing raw data or provider content in terminal exceptions.
        report = {"coverage_complete": False, "document_completed": False,
                  "ready_for_submission": False, "finish_reason": choice.get("finish_reason"),
                  "schema_error": type(exc).__name__, "writes": {}}
    else:
        dump(output / "plan.json", plan.model_dump())
        report = validate_plan(plan, inputs["FORM"], inputs["SOURCE"], inputs["USER"], layout,
                               finish_reason=choice.get("finish_reason"))
    report["usage"] = envelope.get("usage", {})
    report["validator_sha256"] = digest(
        (Path(__file__).parents[1] / "app/global_compilation.py").read_bytes(),
    )
    report["export"] = {"generated": False, "path": None, "sha256": None}
    if report["writes"]:
        data = fill_docx(layout, report["writes"])
        path = output / "bozza-globale-parziale.docx"
        path.write_bytes(data)
        report["export"] = {"generated": True, "path": path.name, "sha256": digest(data),
                            "written_candidates": len(report["writes"]), "partial": True}
    dump(output / report_name, report)
    return report


def offline_replay(source, output):
    """Re-evaluate a frozen response in a NEW directory, without profiles/network.

    Preserve every historical result and the live-call manifest. Report both the
    unchanged input hashes and zero additional model calls for this evaluation.
    """
    names = ["inputs.json", "response.json", "original.docx", "request.json", "manifest.json"]
    before = {name: digest((source / name).read_bytes()) for name in names}
    request = json.loads((source / "request.json").read_text())
    manifest = json.loads((source / "manifest.json").read_text())
    if digest(json.dumps(request, ensure_ascii=False).encode()) != manifest["request_sha256"]:
        raise ValueError("Richiesta storica modificata")
    payload = json.loads(request["messages"][1]["content"])
    inputs = json.loads((source / "inputs.json").read_text())
    if any(inputs[key] != payload[key] for key in ("FORM", "SOURCE", "USER")):
        raise ValueError("Input diversi da quelli della chiamata storica")
    output.mkdir(parents=True, exist_ok=False)
    for name in names:
        shutil.copy2(source / name, output / name)
    for name in ("validation.json", "validation-offline.json"):
        if (source / name).exists():
            shutil.copy2(source / name, output / f"baseline-{name}")
    if (source / "sources").exists():
        shutil.copytree(source / "sources", output / "sources")
    report = validate_response(output, report_name="validation-offline.json")
    after = {name: digest((source / name).read_bytes()) for name in names}
    audit = {"mode": "offline_replay", "additional_model_calls": 0,
             "historical_model_calls": manifest["model_calls"],
             "source_directory": str(source.resolve()),
             "historical_inputs_unchanged": before == after,
             "frozen_sha256": before,
             "copied_inputs_identical": all(digest((output / n).read_bytes()) == before[n]
                                            for n in names)}
    dump(output / "offline-replay.json", audit)
    if not audit["historical_inputs_unchanged"] or not audit["copied_inputs_identical"]:
        raise ValueError("Gli input storici sono cambiati durante il replay")
    return report


async def live(output):
    manifest = json.loads((output / "manifest.json").read_text())
    if manifest["status"] not in {"prepared", "not_sent"}:
        raise ValueError("Chiamata già tentata: vietati retry/fallback automatici")
    settings = resolve_project_settings(manifest["project_id"])
    if (settings.model, settings.base_url, settings.provider) != (
        manifest["model"], manifest["base_url"], "deepseek",
    ):
        raise ValueError("Profilo cambiato dopo la preparazione")
    body = json.loads((output / "request.json").read_text())
    if digest(json.dumps(body, ensure_ascii=False).encode()) != manifest["request_sha256"]:
        raise ValueError("Richiesta modificata dopo la preparazione")
    manifest.update(status="attempting", model_calls=1)
    if "error" in manifest:
        manifest["previous_connection_error"] = manifest.pop("error")
    dump(output / "manifest.json", manifest)
    print("UNA chiamata DeepSeek globale avviata; nessun retry/fallback", flush=True)
    started = time.monotonic()
    try:
        # HTTPX has no automatic status retries. Explicit total deadline as well as read timeout.
        async with httpx.AsyncClient(timeout=httpx.Timeout(1800, connect=30)) as client:
            async with asyncio.timeout(1800):
                http_started = time.monotonic()
                response = await client.post(
                    f"{settings.base_url}/chat/completions", json=body,
                    headers=provider_headers(settings.provider, settings.api_key),
                )
                manifest["http_seconds"] = round(time.monotonic() - http_started, 3)
        (output / "response.txt").write_text(response.text, encoding="utf-8")
        manifest["http_status"] = response.status_code
        response.raise_for_status()
        dump(output / "response.json", response.json())
        report = validate_response(output)
        manifest.update(status="responded", usage=report["usage"],
                        coverage_complete=report["coverage_complete"],
                        validated_values=len(report["writes"]))
    except httpx.ConnectError:
        manifest.update(status="not_sent", model_calls=0, error="Connection failed before request")
        raise
    except Exception as exc:
        # Audit boundary only: an error is recorded, never interpreted as success or retried.
        manifest.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        manifest["call_seconds"] = round(time.monotonic() - started, 3)
        dump(output / "manifest.json", manifest)
        before = json.loads((output / "preservation-before.json").read_text())
        after = fingerprint()
        dump(output / "preservation-after.json", after)
        dump(output / "preservation.json", {"originals_unchanged": before == after,
                                           "tables_checked": len(before["tables"]),
                                           "files_checked": len(before["files"])})
        print(json.dumps(manifest, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=MAX_OUTPUT_TOKENS)
    parser.add_argument("--replay-from", type=Path,
                        help="Copia una prova storica in --output e rivaluta solo offline")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--live", action="store_true")
    modes.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.replay_from and not args.validate_only:
        parser.error("--replay-from richiede --validate-only; nessuna chiamata reale consentita")
    if args.validate_only:
        if args.replay_from:
            offline_replay(args.replay_from, args.output)
        else:
            validate_response(args.output, report_name="validation-offline.json")
    elif args.live:
        asyncio.run(live(args.output))
    else:
        if not args.session_id:
            parser.error("--session-id richiesto per preparare gli input")
        prepare(args.session_id, args.output, args.max_output_tokens)


if __name__ == "__main__":
    main()
