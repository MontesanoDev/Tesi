"""Real global analysis plus narration on an immutable baseline corpus.

No live database/session changes or DOCX generation. One analysis per run;
gold, when present, is scored afterwards and never sent to the provider.
"""

import argparse
import asyncio
import hashlib
import json
import time
from pathlib import Path

import httpx

from app.ai_profiles import resolve_project_settings
from app.compilation_global import build_global_input, global_request, validate_global_proposal
from app.compilation_global_dialogue import narrate
from app.compilation_global_sessions import initial_state
from app.config import use_ai_settings
from app.docx_templates import inspect_docx
from app.generation import GenerationError, request_model_content
from scripts.compilation_benchmark_fixture import load_fixture, score_fixture

REPO = Path(__file__).resolve().parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


async def run(args):
    baseline = json.loads((args.baseline / "input.json").read_text())
    original = (args.baseline / "original.docx").read_bytes()
    project, sources = baseline["project_id"], baseline["sources"]
    settings = resolve_project_settings(args.profile_project)
    if settings.provider != "deepseek" or not settings.configured:
        raise ValueError("Serve un profilo DeepSeek reale")
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(text.replace(settings.api_key, "[REDACTED]") + "\n")

    code = {p.name: sha(p.read_bytes()) for p in (REPO / "backend/app").glob("*.py")}
    layout = inspect_docx(original, require_candidates=False)
    data = build_global_input(layout, project, sources)
    assert baseline["form"] == data["form"] and baseline["sources"] == data["sources"]
    save("input.json", data)
    (args.output / "original.docx").write_bytes(original)
    save("protocol.json", {"baseline": str(args.baseline), "provider": settings.provider,
        "model": settings.model, "source_sha256": sha(json.dumps(sources, sort_keys=True).encode()),
        "original_sha256": sha(original), "application_files": code, "runs": args.runs,
        "analysis_calls_per_run": 1, "narration_calls_per_run": 1, "retries": 0,
        "gold_in_prompt": False, "session_writes": 0, "docx_writes": 0})
    for name in ["compilation_global.py", "compilation_global_contract.py",
                 "compilation_coverage.py", "compilation_global_dialogue.py",
                 "compilation_reading_plan.py", "compilation_global_sessions.py"]:
        save("code/" + name + ".txt", (REPO / "backend/app" / name).read_text())
    fixture = (load_fixture(args.baseline / "fixture")
               if (args.baseline / "fixture").exists() else None)
    if fixture:
        save("gold-audit-only.json", fixture["gold"])
    results = []
    for index in range(args.runs):
        folder = args.output / f"run-{index + 1:02d}"
        folder.mkdir()
        body = global_request(settings, data, thinking=True)
        save(f"run-{index + 1:02d}/request.json", {"body": body, "schema": data["schema_output"]})
        start = time.perf_counter()
        result = {"run": index + 1, "http_calls": 0}

        async def capture(response):
            result["http_calls"] += 1
            await response.aread()
            save(f"run-{index + 1:02d}/http-response.txt", response.text)

        try:
            async with httpx.AsyncClient(timeout=300,
                                         event_hooks={"response": [capture]}) as client:
                raw, model, usage = await asyncio.wait_for(request_model_content(
                    client, settings, body, 300, response_schema=data["schema_output"]), 300)
            result.update(model=model, usage=usage, analysis_seconds=time.perf_counter() - start)
            save(f"run-{index + 1:02d}/response.txt", raw)
            audit = validate_global_proposal(raw, layout, project, sources, expected_version=12)
            save(f"run-{index + 1:02d}/audit.json", audit)
            if fixture:
                save(f"run-{index + 1:02d}/fixture-score.json",
                     score_fixture(raw, audit, fixture["gold"]))
            state = initial_state(layout)
            state.update(phase="REVIEW", audit=audit, catalog=data["form"],
                         reading_plan=data["reading_plan"])
            with use_ai_settings(settings):
                dialogue = await narrate(state, folder)
            save(f"run-{index + 1:02d}/dialogue.json", dialogue)
            result.update(coverage=audit["coverage_summary"], counts=audit["counts"],
                conditional_proposals=audit["grounded_conditional_proposals"],
                narration_error=dialogue.get("error"), narration_seconds=dialogue["ai_seconds"],
                narration_usage=dialogue.get("usage"), message=dialogue["message"])
        except (GenerationError, ValueError, TimeoutError, httpx.HTTPError) as exc:
            result.update(error=type(exc).__name__, detail=str(exc),
                          seconds=time.perf_counter() - start)
        results.append(result)
        save("results.json", results)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    unchanged = all(sha((REPO / "backend/app" / n).read_bytes()) == h for n, h in code.items())
    save("integrity.json", {"application_unchanged": unchanged,
                           "original_unchanged": sha((args.baseline / "original.docx").read_bytes())
                           == sha(original)})
    assert unchanged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile-project", required=True)
    parser.add_argument("--runs", type=int, choices=[1, 2, 3], default=2)
    asyncio.run(run(parser.parse_args()))
