"""Real independent guard on frozen proposed assignments, with isolated writes."""

import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from app import compilation_chat, compilation_sessions, intents
from app.compilation_chat import ClarificationDecision, ClarificationReply
from app.compilation_reply_guard import ReplyScopeChecks, verify_field_replies
from app.config import use_ai_settings
from app.db import init_database
from app.project_forms import _save_form
from app.repository import create_project
from app.schemas import ProjectCreate
from scripts.benchmark_compilation_dialogue import (
    FIXTURE,
    changed_state,
    digest,
    load_fixture,
    real_settings,
    seed_checkpoint,
)

GUARD_FIXTURE = FIXTURE.parent / "guard-v1"


async def benchmark(args):
    _, contexts, _ = load_fixture(FIXTURE)
    manifest = json.loads((GUARD_FIXTURE / "manifest.json").read_text())
    for name, expected in manifest["base_files"].items():
        assert digest((FIXTURE / name).read_bytes()) == expected
    for name, expected in manifest["files"].items():
        assert digest((GUARD_FIXTURE / name).read_bytes()) == expected
    cases = json.loads((GUARD_FIXTURE / "cases.json").read_text())["cases"]
    assert len(cases) <= min(9, manifest["max_cases"])
    settings = real_settings(args.project)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    def save(path, data):
        p = output / path
        p.parent.mkdir(exist_ok=True, parents=True)
        text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2)
        p.write_text(text.replace(settings.api_key, "[REDACTED]") + "\n")

    save("protocol.json", {"head": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip(), "manifest": manifest,
        "model": settings.model, "cases": len(cases), "max_calls": len(cases),
        "simulated_providers": False, "new_router_calls": 0, "prepared_proposals": True})
    original = intents.request_model_content
    records, active_case, response = [], "", {}

    async def observe(client, config, body, timeout, **kwargs):
        save(active_case + "/request.json", {"body": body, "schema": kwargs["response_schema"]})
        started = time.perf_counter()
        try:
            raw, model, usage = await original(client, config, body, timeout, **kwargs)
            response.update(raw=raw, model=model, usage=usage)
            try:
                ReplyScopeChecks.model_validate_json(raw)
                response["schema_valid"] = True
            except ValueError:
                response["schema_valid"] = False
            return raw, model, usage
        except Exception as exc:
            response["error"] = type(exc).__name__
            raise
        finally:
            response["seconds"] = time.perf_counter()-started
            save(active_case + "/response.json", response)

    variables = ("MAPI_DB_PATH", "MAPI_STORAGE_PATH", "MAPI_KNOWLEDGE_PATH")
    old = {key: os.environ.get(key) for key in variables}
    try:
        with tempfile.TemporaryDirectory(prefix="mapi-reply-guard-") as runtime:
            folder = Path(runtime)
            os.environ.update(MAPI_DB_PATH=str(folder / "fixture.db"),
                              MAPI_STORAGE_PATH=str(folder / "uploads"),
                              MAPI_KNOWLEDGE_PATH=str(folder / "knowledge"))
            init_database()
            project = create_project(ProjectCreate(title="Benchmark guard", description="V1" * 2))
            project_id = project["id"]
            path = FIXTURE / "modulo-dialogo.docx"
            form = _save_form(project_id, path.name, path.read_bytes())
            with use_ai_settings(settings):
                for case in cases:
                    active_case, response = case["id"], {}
                    context = contexts[case["context"]]
                    before = seed_checkpoint(project_id, form, context, active_case, path)
                    save(active_case + "/before.json", before)
                    replies = [ClarificationReply.model_validate(r) for r in case["proposals"]]
                    verification = await verify_field_replies(case["message"],
                        intents.routing_context(compilation_chat.planner_context(before)),
                        replies, request=observe)
                    kept = [r for r in replies if r.slot in verification.allowed_slots]
                    if kept:
                        await compilation_chat.handle_group_decision(project_id,
                            before["conversation_id"], ClarificationDecision(
                                action="ANSWER", replies=kept), before,
                            case["message"], before["version"])
                    after = compilation_sessions.get_session(project_id, before["id"])
                    effects = changed_state(before, after, context["slots"])
                    result = {"case": active_case, "allowed": sorted(verification.allowed_slots),
                              "expected": case["expected_allowed_slots"],
                              "effects": effects, "total_tokens": verification.total_tokens}
                    result["passed"] = (response.get("schema_valid") is True
                        and result["allowed"] == result["expected"]
                        and set(effects["actions"]) == {str(s) for s in result["expected"]}
                        and effects["provenance_ok"] and not effects["unexpected_recipients"])
                    save(active_case + "/after.json", after)
                    save(active_case + "/result.json", result)
                    records.append(result)
                    save("results.json", records)
                    print(json.dumps(result, ensure_ascii=False), flush=True)
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(benchmark(parser.parse_args()))


if __name__ == "__main__":
    main()
