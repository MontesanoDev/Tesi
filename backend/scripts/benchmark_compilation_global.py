"""One real DeepSeek call on a complete small corpus; no session or DOCX writes.

Only audit artifacts are written. SQLite backup is temporary; live DB is read
only. No retries, simulated providers, generated drafts or semantic approvals.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.ai_profiles import resolve_project_settings
from app.compilation_global import (
    build_global_input,
    global_request,
    validate_global_proposal,
)
from app.db import get_db_path, get_storage_path
from app.docx_templates import inspect_docx
from app.generation import request_model_content
from app.repository import project_evidence_filter, reload_evidence
from scripts.compilation_benchmark_fixture import load_fixture, score_fixture


def load_document_corpus(db, project_id):
    """Reuse current role/isolation SQL and reread gate, without vector/LLM search.

    Whole uploaded documents from this project + Company/General KB. Artifacts
    (including user facts) are excluded from this first SOURCE-only experiment.
    Limits are enforced later before the request; never sample silently.
    """
    rows = db.execute(
        "SELECT c.id chunk_id,c.file_id,c.chunk_index,1.0 relevance "
        "FROM document_chunks c JOIN project_files f ON f.id=c.file_id "
        "WHERE c.project_id=? AND f.project_id=c.project_id AND f.kind='source' AND "
        + project_evidence_filter("source") + " ORDER BY c.file_id,c.chunk_index",
        (project_id,),
    ).fetchall()
    rows += db.execute(
        "SELECT -c.id chunk_id,-d.id file_id,c.chunk_index,1.0 relevance "
        "FROM global_document_chunks c JOIN global_documents d ON d.id=c.document_id "
        "WHERE d.category IN ('company','general') ORDER BY d.id,c.chunk_index",
    ).fetchall()
    return reload_evidence(project_id, [dict(r) for r in rows], target="source", db=db)


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--form-id", type=int)
    parser.add_argument("--fixture", type=Path,
                        help="Versioned synthetic DOCX/corpus, without DB ingestion")
    parser.add_argument("--profile-project", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-seconds", type=int, default=300)
    parser.add_argument("--thinking", action=argparse.BooleanOptionalAction, default=True,
                        help="Ragionamento low predefinito; --no-thinking per il controllo, "
                             "sempre una chiamata")
    args = parser.parse_args(argv)
    if args.fixture:
        if args.project is not None or args.form_id is not None:
            parser.error("--fixture cannot be combined with --project/--form-id")
    elif args.project is None or args.form_id is None:
        parser.error("Use --fixture or both --project and --form-id")
    if not 1 <= args.max_seconds <= 600:
        parser.error("Use 1..600 seconds")
    return args


def run(args):
    fixture = load_fixture(args.fixture) if args.fixture else None
    if fixture:
        args.project = fixture["manifest"]["project_id"]
    settings = resolve_project_settings(args.profile_project)
    if settings.provider != "deepseek" or not settings.configured:
        raise ValueError("Questa prova richiede un profilo DeepSeek reale configurato")
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    backend = Path(__file__).resolve().parents[1]
    repo = backend.parent
    secret = settings.api_key

    def save(name, value):
        encoded = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False, indent=2,
        )
        if secret:
            encoded = encoded.replace(secret, "[REDACTED]")
        (root / name).write_text(encoded + "\n")

    report = {"started_at": datetime.now(UTC).isoformat(), "model": settings.model,
              "provider": settings.provider, "profile_project": args.profile_project,
              "project_id": args.project, "form_id": args.form_id, "http_calls": 0,
              "semantic_calls": 0, "automatic_retries": 0, "session_writes": 0,
              "docx_writes": 0, "user_values": 0, "max_seconds": args.max_seconds,
              "thinking": args.thinking,
              "saved_profile_context_window": settings.context_window,
              "scope": "complete small document corpus, proposal + local audit only"}
    save("code.json", {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo,
                                        text=True).strip(),
        "status": subprocess.check_output(["git", "status", "--short", "--branch"],
                                          cwd=repo, text=True),
    })
    for relative in ["app/compilation_global.py", "app/compilation_global_contract.py",
                     "app/compilation_catalog.py",
                     "app/compilation_semantics.py", "app/compilation_role_records.py",
                     "app/compilation_sessions.py",
                     "app/compilation_sources.py",
                     "app/docx_templates.py", "app/document_compilation.py",
                     "scripts/benchmark_compilation_global.py",
                     "scripts/compilation_benchmark_fixture.py"]:
        target = root / "code" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backend / relative, target)
    if fixture:
        for name in [*fixture["manifest"]["files"], "manifest.json"]:
            target = root / "fixture" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fixture["root"] / name, target)
        report.update(fixture_version=fixture["gold"]["version"],
                      fixture_manifest_sha256=hashlib.sha256(
                          (fixture["root"] / "manifest.json").read_bytes()).hexdigest())

    with tempfile.TemporaryDirectory(prefix="mapi-global-proposal-") as directory:
        if fixture:
            path, sources = fixture["path"], fixture["sources"]
            original = path.read_bytes()
        else:
            copied_db = Path(directory) / "snapshot.db"
            with sqlite3.connect(f"file:{get_db_path().resolve()}?mode=ro", uri=True) as live:
                with sqlite3.connect(copied_db) as snapshot:
                    live.backup(snapshot)
            with sqlite3.connect(f"file:{copied_db}?mode=ro", uri=True) as db:
                db.row_factory = sqlite3.Row
                row = db.execute("SELECT * FROM project_files WHERE id=? AND project_id=? "
                                 "AND kind='form'", (args.form_id, args.project)).fetchone()
                if row is None:
                    raise ValueError("Modulo non presente nel progetto richiesto")
                path = get_storage_path().resolve() / row["storage_path"]
                original = path.read_bytes()
                sources = load_document_corpus(db, args.project)
        (root / "original.docx").write_bytes(original)
        layout = inspect_docx(original, require_candidates=False)
        data = build_global_input(layout, args.project, sources)
        body = global_request(settings, data, thinking=args.thinking)
        save("input.json", data)
        save("request.json", body)
        report.update(original_sha256=layout.sha256,
                      candidate_count=len(data["form"]["candidates"]),
                      source_coverage=data["source_coverage"],
                      input_characters=sum(len(m["content"]) for m in body["messages"]),
                      max_output_tokens=body["max_tokens"])
        save("metrics.json", report)
        print(json.dumps({k: report[k] for k in (
            "model", "candidate_count", "source_coverage", "input_characters",
        )}), flush=True)

        async def capture(response):
            report["http_calls"] += 1
            await response.aread()
            save("http-response.txt", response.text)
            report["http_status"] = response.status_code

        async def call():
            timeout = httpx.Timeout(args.max_seconds, connect=15)
            async with httpx.AsyncClient(timeout=timeout,
                                         event_hooks={"response": [capture]}) as client:
                report["semantic_calls"] += 1
                return await asyncio.wait_for(request_model_content(
                    client, settings, body, timeout.read,
                    response_schema=data["schema_output"],
                ), timeout=args.max_seconds)

        started = time.perf_counter()
        try:
            raw, model, usage = asyncio.run(call())
            report.update(model=model, usage=usage, ai_seconds=time.perf_counter() - started)
            save("response.txt", raw)
            audit = None
            try:
                audit = validate_global_proposal(
                    raw, layout, args.project, sources,
                    expected_version=data["schema_output"]["properties"]["version"]["const"],
                )
            finally:
                if fixture:
                    try:
                        save("fixture-score.json", score_fixture(raw, audit, fixture["gold"]))
                    except Exception as exc:
                        save("fixture-score-error.json", {"type": type(exc).__name__,
                                                          "error": str(exc)})
            save("validation.json", audit)
            report.update(validation_counts=audit["counts"], dispositions=audit["dispositions"],
                          contract_version=audit.get("version", 1),
                          proposal_assessment=audit.get("assessment", "legacy_audit_only"),
                          grounded_conditional_proposals=audit.get(
                              "grounded_conditional_proposals", 0),
                          facts=len(audit.get("facts", {})),
                          conditions=len(audit.get("conditions", {})),
                          bindings=len(audit.get("bindings", {})),
                          binding_checks=audit.get("binding_checks", {}),
                          condition_results=audit.get("condition_results", {}),
                          condition_inventory=audit.get("condition_inventory", {}),
                          deferred=audit.get("deferred_count", 0),
                          unassigned=audit.get("unassigned_count", 0),
                          rejected_unknown_assignments=len(audit.get("rejected_assignments", {})),
                          unused_facts=len(audit.get("unused_fact_ids", [])),
                          state="proposal_audited", resolved=audit["resolved"])
        except Exception as exc:
            report.update(state="failed", error_type=type(exc).__name__,
                          error=str(exc), ai_seconds=report.get(
                              "ai_seconds", time.perf_counter() - started,
                          ))
            # Capture billing/finish metadata even when normal parsing rejects a
            # truncated output. Raw HTTP was saved before the application gate.
            response_file = root / "http-response.txt"
            if response_file.exists():
                try:
                    report["usage"] = json.loads(response_file.read_text()).get("usage", {})
                except ValueError:
                    pass
        finally:
            report["original_unchanged"] = hashlib.sha256(path.read_bytes()).hexdigest() \
                == layout.sha256
            save("metrics.json", report)
            save("manifest.json", {
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*")) if p.is_file() and p.name != "manifest.json"
            })
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report["state"] == "proposal_audited"


if __name__ == "__main__":
    raise SystemExit(0 if run(arguments()) else 1)
