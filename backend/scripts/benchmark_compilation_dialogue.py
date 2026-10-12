"""Frozen dialogue gold, real routing, isolated persistence; no production changes.

Run from backend with PYTHONPATH=.; credentials are read-only and never archived.
This measures prepared dialogue checkpoints, not SOURCE retrieval or new analysis.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

from app import ai_profiles, compilation_chat, compilation_sessions, intents
from app import compilation_global_sessions as adapter
from app.compilation_global import build_global_input
from app.config import AISettings, use_ai_settings
from app.db import connection, get_db_path, get_storage_path, init_database
from app.project_forms import _save_form
from app.repository import create_project
from app.schemas import ProjectCreate

FIXTURE = Path(__file__).resolve().parents[2] / "demo-documents/benchmark-dialogo/v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_fixture(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or digest(path.read_bytes()) != expected:
            raise ValueError("Fixture modificata o percorso esterno: " + name)
    contexts = json.loads((root / "contexts.json").read_text())
    cases = json.loads((root / "cases.json").read_text())["cases"]
    if len(cases) > min(manifest["max_cases"], 48):
        raise ValueError("Budget casi superato")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("ID caso duplicato")
    for case in cases:
        context = contexts[case["context"]]
        slots = {str(s["slot"]) for s in context["slots"]}
        if not set(case["expected"]["actions"]) <= slots:
            raise ValueError("Gold riferito a slot inesistente")
    return manifest, contexts, cases


def real_settings(project):
    """Explicitly read-only: don't copy profiles, keys or unrelated user data."""
    with sqlite3.connect(get_db_path().resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT a.* FROM ai_profiles a WHERE a.id=COALESCE("
            "(SELECT profile_id FROM project_ai_settings WHERE project_id=?),"
            "(SELECT default_profile_id FROM ai_preferences WHERE id=1))", (project,),
        ).fetchone()
    if not row or row["provider"] != "deepseek" or row["model"] != "deepseek-flash":
        raise ValueError("Il progetto deve selezionare il profilo reale deepseek-flash")
    return AISettings(api_key=ai_profiles._decrypt(row["encrypted_api_key"]),
                      model=row["model"], provider=row["provider"], base_url=row["base_url"],
                      context_window=row["context_window"], thinking=False)


def seed_checkpoint(project, form, context, case_id, original_path):
    """Author a test checkpoint ONLY in the temporary DB, never a live session."""
    s = compilation_sessions.create_session(project, form["id"], start_in_chat=True,
                                             engine="global")
    question = None if not context["kind"] else {
        **copy.deepcopy(context), "field_ids": list(dict.fromkeys(
            cid for slot in context["slots"] for cid in slot["field_ids"])),
    }
    with connection() as db:
        row = compilation_sessions._row(db, project, s["id"])
        state = json.loads(row["state_json"])
        data = state["global_compilation"]
        data["catalog"] = build_global_input(compilation_sessions.read_original(row),
                                             project, [])["form"]
        paragraphs = {p["id"]: p["text"] for b in data["catalog"]["blocks"]
                      for p in b["paragraphs"]}
        fields = []
        for cid, candidate in data["catalog"]["candidates"].items():
            if cid not in data["writable_ids"]:
                continue
            label = next(paragraphs[p] for p in candidate["anchor_paragraph_ids"]
                         if paragraphs[p].strip())
            fields.append({"candidate_id": cid, "label": label, "kind": "data",
                           "disposition": "missing", "validation": "REVIEW_REQUIRED",
                           "validation_errors": [], "conditions": [], "source_evidence": [],
                           "form_evidence": {"quote": label}})
        folder = get_storage_path() / project / "_global_compilations" / s["id"] / case_id
        folder.mkdir(parents=True)
        # A source-free empty proposal, not a simulated provider response. Export
        # revalidates this fixture through the existing validator. No SOURCE facts.
        (folder / "response.txt").write_text(json.dumps({
            "version": 10, "facts": {}, "fields": {}, "conditions": {}, "bindings": {},
            "uncertain_paragraph_ids": [],
        }))
        user_values = {}
        if case_id.startswith("generate-"):
            user_values["t0.r1.c1"] = {
                "value": "contatti@aurora.example", "user_quote": "contatti@aurora.example",
                "provenance": "USER", "label": "Recapito comunicazioni", "previous": None,
            }
        data.update(phase="REVIEW", attempts=1, paused=context.get("paused", False),
                    artifact_path=str(folder.relative_to(get_storage_path())),
                    audit={"fields": fields, "conditions": {}, "unassigned_count": 0},
                    dialogue={"phase": "READY", "question": question,
                              "message": context.get("message"), "answers": {},
                              "user_values": user_values, "held_candidate_ids": []})
        state["status"] = "GENERATED" if context.get("generated") else "WAITING_FOR_USER"
        state["last_error"] = None
        s = compilation_sessions.save_state(db, row, state, "benchmark_checkpoint_fixture")
    assert digest(original_path.read_bytes()) == state["template_sha256"]
    return s


def changed_state(before, after, slots):
    first, last = [s["global_compilation"]["dialogue"] for s in (before, after)]
    updates, values = {}, {}
    for slot in slots:
        key, number = slot["key"], str(slot["slot"])
        record = last["answers"].get(key)
        if record != first["answers"].get(key) and record:
            updates[number] = record["action"]
            if record.get("value") is not None:
                values[number] = record["value"]
    allowed_keys = {s["key"] for s in slots}
    unexpected = [key for key in set(last["answers"]) | set(first["answers"])
                  if first["answers"].get(key) != last["answers"].get(key)
                  and key not in allowed_keys]
    allowed_fields = {s["field_ids"][0] for s in slots if s["kind"] == "value"}
    unexpected += [cid for cid in set(last["user_values"]) | set(first["user_values"])
                   if first["user_values"].get(cid) != last["user_values"].get(cid)
                   and cid not in allowed_fields]
    provenance_ok = all(r["provenance"] == "USER" for r in last["answers"].values()) and all(
        r["provenance"] == "USER" for r in last["user_values"].values())
    return {"actions": updates, "values": values, "unexpected_recipients": unexpected,
            "provenance_ok": provenance_ok, "paused": after["chat"]["paused_by_user"]}


def score_case(case, result):
    expected = case["expected"]
    effects = result["effects"]
    checks = {
        "intent": result["intent"] in expected["intents"],
        "actions": effects["actions"] == expected["actions"],
        "values": effects["values"] == expected["values"],
        "export_intent": result["export_requested"] == expected["export_requested"],
        "recipients": not effects["unexpected_recipients"],
        "provenance": effects["provenance_ok"],
        "no_execution_error": result.get("error") is None,
    }
    if "paused" in expected:
        checks["paused"] = effects["paused"] == expected["paused"]
    if "target" in expected:
        checks["target"] = result.get("target") == expected["target"]
    return {"passed": all(checks.values()), "checks": checks}


async def benchmark(args):
    manifest, contexts, cases = load_fixture(args.fixture)
    settings = real_settings(args.project)
    if not settings.configured:
        raise ValueError("Profilo non configurato")
    output = Path(args.output).resolve()
    if output.is_relative_to(Path(args.fixture).resolve()):
        raise ValueError("L'output non può modificare la fixture")
    output.mkdir(parents=True, exist_ok=False)

    def save(path, value):
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        target.write_text(text.replace(settings.api_key, "[REDACTED]") + "\n")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    save("protocol.json", {"head": head, "fixture": manifest, "cases": len(cases),
         "provider": settings.provider, "model": settings.model, "thinking": False,
         "max_calls": 2 * len(cases), "serial": True, "new_analysis_calls": 0,
         "gold_in_prompt": False, "prepared_checkpoints": True,
         "simulated_providers": False, "application_changes_during_run": False,
         "scope": "routing + actual USER/control mutations and authorized exports; "
                  "no RAG/new analysis/narration or SOURCE quality measurement"})
    original_transport = intents.request_model_content
    measurements, case_calls = [], []
    active_case = ""

    async def observe(client, config, body, timeout, **kwargs):
        assert config.provider == settings.provider and config.model == settings.model
        index = len(case_calls) + 1
        path = f"{active_case}/call-{index}"
        save(path + "-request.json", {"body": body, "schema": kwargs.get("response_schema")})
        started = time.perf_counter()
        record = {"attempt": index}
        case_calls.append(record)
        try:
            raw, model, usage = await original_transport(client, config, body, timeout, **kwargs)
            record.update(raw=raw, model=model, usage=usage)
            try:
                cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
                allowed = {s["slot"] for s in (intents.routing_context(compilation) or {}).get(
                    "slots", [])}
                plan = intents.parse_turn_plan(json.loads(cleaned), allowed)
                intents.bind_turn_plan(plan, compilation, current_message)
                record["schema_valid"] = True
            except ValueError as exc:
                record["schema_valid"] = False
                record["validation_error"] = (exc.errors(include_input=False, include_url=False)
                                               if hasattr(exc, "errors") else str(exc))
            return raw, model, usage
        except Exception as exc:
            record["error"] = type(exc).__name__
            raise
        finally:
            record["seconds"] = time.perf_counter() - started
            save(path + "-response.json", record)

    variables = ("MAPI_DB_PATH", "MAPI_STORAGE_PATH", "MAPI_KNOWLEDGE_PATH")
    previous = {key: os.environ.get(key) for key in variables}
    try:
        with tempfile.TemporaryDirectory(prefix="mapi-dialogue-") as runtime:
            private = Path(runtime)
            os.environ.update(MAPI_DB_PATH=str(private / "fixture.db"),
                              MAPI_STORAGE_PATH=str(private / "uploads"),
                              MAPI_KNOWLEDGE_PATH=str(private / "knowledge"))
            init_database()
            project = create_project(ProjectCreate(title="Benchmark dialogo", description="V1"))
            project_id = project["id"]
            form_path = Path(args.fixture) / "modulo-dialogo.docx"
            original_hash = digest(form_path.read_bytes())
            form = _save_form(project_id, form_path.name, form_path.read_bytes())
            intents.request_model_content = observe
            with use_ai_settings(settings):
                for case in cases:
                    active_case, case_calls = case["id"], []
                    current_message = case["message"]
                    context = contexts[case["context"]]
                    seed_id = case["context"] + "-" + case["id"]
                    before = seed_checkpoint(project_id, form, context, seed_id, form_path)
                    after = before
                    save(f"{active_case}/before.json", before)
                    compilation = (None if context.get("mode") == "idle" else
                                   compilation_chat.planner_context(before))
                    history = ([{"question": "Compila questo modulo", "answer": context["message"]}]
                               if context["message"] else [])
                    result = {"id": active_case, "category": case["category"], "intent": None,
                              "export_requested": False, "error": None}
                    started = time.perf_counter()
                    try:
                        planned = await intents.plan_chat_turn(case["message"], history, [form],
                            selected_form={"id": form["id"], "name": form["name"]},
                            compilation=compilation)
                        decision = planned.decision
                        result.update(intent=planned.intent, decision=decision.model_dump())
                        # main.answer applies this guard before planning. Measure
                        # the semantic planner too, retaining the diagnostic call.
                        direct = intents.route_compilation_control(intents.ChatDecision(
                            action="reply", answer="Controllo", target="source", queries=[]),
                            case["message"], None if compilation is None else before)
                        if (direct.action == "compilation_control"
                                and direct.control.kind == "finish"):
                            decision = direct
                            result["direct_finish_guard"] = True
                        if isinstance(decision, compilation_chat.ClarificationDecision):
                            text, command = await compilation_chat.handle_group_decision(
                                project_id, before["conversation_id"], decision, before,
                                case["message"], before["version"])
                            result.update(message=text, command=command)
                        else:
                            # Record planner separately; the production dispatch also protects
                            # explicit controls. Compile/RAG/reply deliberately stop at routing.
                            decision = intents.route_compilation_control(decision, case["message"],
                                None if compilation is None else before)
                            result.update(effective_decision=decision.model_dump(),
                                          target=decision.target)
                            is_control = decision.action == "compilation_control"
                            export = decision.action == "compilation_generate" or (
                                is_control and decision.control.kind == "finish")
                            result["export_requested"] = export
                            if is_control or export:
                                text, command = await adapter.handle_chat_action(
                                    before, decision, before["version"], case["message"])
                                result.update(message=text, command=command)
                        after = compilation_sessions.get_session(project_id, before["id"])
                    except Exception as exc:
                        result["error"] = {"type": type(exc).__name__, "detail": str(exc)}
                        after = compilation_sessions.get_session(project_id, before["id"])
                    result.update(effects=changed_state(before, after, context["slots"]),
                                  calls=copy.deepcopy(case_calls),
                                  seconds=time.perf_counter()-started,
                                  generated=after["version"] != before["version"]
                                            and after["status"] == "GENERATED")
                    result["score"] = score_case(case, result)
                    save(f"{active_case}/after.json", after)
                    if result["generated"]:
                        from app.document_compilation_routes import _get_run

                        run = after["last_generation"]
                        # The public report is already embedded nowhere in the payload;
                        # copy only output files, never the private SQLite or credentials.
                        saved = _get_run(project_id, run["id"])
                        folder = get_storage_path() / saved["storage_path"]
                        save(f"{active_case}/generated-report.json",
                             json.loads(saved["report_json"]))
                        for name in ("bozza.docx", "template.docx"):
                            shutil.copy2(folder / name, output / active_case / name)
                        result["downloads"] = run["downloads"]
                    save(f"{active_case}/result.json", result)
                    measurements.append(result)
                    save("results.json", measurements)
                    failed = [k for k, v in result["score"]["checks"].items() if not v]
                    print(json.dumps({"id": active_case, "intent": result["intent"],
                                      "passed": result["score"]["passed"],
                                      "failed_checks": failed}, ensure_ascii=False), flush=True)
            assert digest(form_path.read_bytes()) == original_hash
            summary = {"head": head, "cases": len(measurements),
                       "passed": sum(r["score"]["passed"] for r in measurements),
                       "failed_checks": dict(Counter(k for r in measurements
                           for k, v in r["score"]["checks"].items() if not v)),
                       "calls": sum(len(r["calls"]) for r in measurements),
                       "retries": sum(max(0, len(r["calls"])-1) for r in measurements),
                       "total_tokens": sum(c.get("usage", {}).get("total_tokens", 0)
                           for r in measurements for c in r["calls"]),
                       "seconds": sum(r["seconds"] for r in measurements),
                       "generated": sum(r["generated"] for r in measurements),
                       "fixture_original_unchanged": True, "live_db_writes": 0}
            save("summary.json", summary)
            print(json.dumps(summary, ensure_ascii=False), flush=True)
    finally:
        intents.request_model_content = original_transport
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Read-only real model selection")
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(benchmark(parser.parse_args()))


if __name__ == "__main__":
    main()
