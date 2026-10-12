"""Real narration on frozen, revalidated audits; no live session writes.

Run from backend with PYTHONPATH=.; no gold or expected IDs enter the request.
One call per case, no retries. Raw captures are saved by the production narrator.
"""

import argparse
import asyncio
import copy
import hashlib
import json
import subprocess
from pathlib import Path

from app import compilation_global_dialogue as dialogue
from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_sessions import initial_state, review_fields
from app.config import use_ai_settings
from app.docx_templates import inspect_docx
from scripts.benchmark_compilation_dialogue import real_settings

FIXTURE = Path(__file__).resolve().parents[2] / "demo-documents/benchmark-sintesi/v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_fixture(root=FIXTURE):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or sha(path.read_bytes()) != expected:
            raise ValueError("Fixture modificata o percorso esterno: " + name)
    cases = json.loads((root / "cases.json").read_text())["cases"]
    if len(cases) > min(manifest["max_cases"], 7):
        raise ValueError("Budget casi superato")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("ID duplicati")
    for case in cases:
        for name in ("document", "sources", "proposal", "dialogue"):
            if case[name] and case[name] not in manifest["files"]:
                raise ValueError("File non congelato: " + case[name])
    return manifest, cases


def prepare_case(case, root=FIXTURE):
    root = Path(root)
    layout = inspect_docx((root / case["document"]).read_bytes(), require_candidates=False)
    sources = json.loads((root / case["sources"]).read_text())
    audit = validate_global_proposal((root / case["proposal"]).read_text(), layout,
                                    case["project_id"], sources, expected_version=10)
    data = initial_state(layout)
    data.update(phase="REVIEW", attempts=1, audit=audit,
                catalog=build_global_input(layout, case["project_id"], sources)["form"],
                dialogue=json.loads((root / case["dialogue"]).read_text())
                if case["dialogue"] else {})
    writable = set(data["writable_ids"])
    expected_ids = case["expected"]["exportable_source_ids"] + case["expected"]["held_ids"]
    if not set(expected_ids) <= writable:
        raise ValueError("Gold fuori dalle posizioni scrivibili")
    return data


def fingerprint():
    return {str(p): sha(p.read_bytes()) for p in sorted(Path("app").rglob("*.py"))}


async def run(args):
    manifest, cases = load_fixture(args.fixture)
    # Preflight all cases before any API call or credential access.
    prepared = [prepare_case(case, args.fixture) for case in cases]
    settings = real_settings(args.project)
    args.output.mkdir(parents=True, exist_ok=False)

    def save(path, value):
        raw = json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(raw.replace(settings.api_key, "[REDACTED]") + "\n")

    code = fingerprint()
    protocol = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "application_files": code, "fixture": manifest, "real_provider": True,
                "provider": settings.provider, "model": settings.model,
                "gold_in_prompt": False, "max_calls": len(cases), "new_analysis_calls": 0,
                "max_tokens_per_call": 2048, "timeout_seconds": 45, "retries": 0,
                "live_session_writes": False, "phase": args.phase}
    save(args.output / "protocol.json", protocol)
    results = []
    for case, data in zip(cases, prepared, strict=True):
        assert fingerprint() == code, "Application changed during benchmark"
        folder = args.output / case["id"]
        folder.mkdir()
        save(folder / "before.json", data)
        with use_ai_settings(settings):
            result = await dialogue.narrate(copy.deepcopy(data), folder)
        selection = dialogue.export_selection({"global_compilation": {
            **data, "fields": review_fields(data), "dialogue": result}})
        actual = {"exportable_source_ids": sorted(selection[0]),
                  "held_ids": sorted(result.get("held_candidate_ids", [])),
                  "needs_question": bool((result.get("question") or {}).get("slots"))}
        expected = {**case["expected"], "exportable_source_ids": sorted(
            case["expected"]["exportable_source_ids"]), "held_ids": sorted(
            case["expected"]["held_ids"])}
        item = {"id": case["id"], "pass": actual == expected and not result.get("error"),
                "actual": actual, "expected": expected, "error": result.get("error"),
                "usage": result.get("usage", {}), "ai_seconds": result["ai_seconds"],
                "http_calls": result["http_calls"], "message": result["message"]}
        save(folder / "comparison.json", item)
        results.append(item)
        save(args.output / "results.json", {"phase": args.phase, "results": results,
            "passed": sum(r["pass"] for r in results), "total": len(results)})
        print(json.dumps({k: item[k] for k in ("id", "pass", "actual", "ai_seconds")}), flush=True)
    assert fingerprint() == code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=["before", "after"], required=True)
    parser.add_argument("--project", default="prova")
    asyncio.run(run(parser.parse_args()))
