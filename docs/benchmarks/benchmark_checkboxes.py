"""Real V11 analysis, bounded narration and explicit laboratory partial exports.

No live session/DB writes. Gold is scored after the real call, never sent.
Run from backend with PYTHONPATH=.; source snapshots stay frozen across repeats.
"""

import argparse
import asyncio
import hashlib
import json
import secrets
import subprocess
import time
from io import BytesIO
from pathlib import Path

import httpx
from docx import Document
from docx.oxml.ns import qn

from app.compilation_catalog import _checkboxes
from app.compilation_choices import materialize_choices
from app.compilation_global import build_global_input, global_request, validate_global_proposal
from app.compilation_global_dialogue import export_selection, narrate
from app.compilation_global_sessions import initial_state, review_fields
from app.compilation_sessions import validate_value
from app.config import use_ai_settings
from app.docx_templates import fill_docx, inspect_docx
from app.generation import request_model_content
from scripts.benchmark_compilation_dialogue import real_settings
from scripts.compilation_benchmark_fixture import load_fixture, score_fixture

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "demo-documents/benchmark-checkbox/v1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_choices():
    manifest = json.loads((FIXTURE / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        path = (FIXTURE / name).resolve()
        if not path.is_relative_to(FIXTURE) or sha(path.read_bytes()) != digest:
            raise ValueError("Fixture modificata: " + name)
    return manifest


def word_states(raw):
    body = Document(BytesIO(raw)).element.body
    # Strip only the draft banner in memory to compare original structural IDs.
    body.remove(body[0])
    positions = {p: i for i, p in enumerate(body.iter(qn("w:p")))}
    return {r["id"]: r["initial_checked"] for group in _checkboxes(body, positions).values()
            for _, r in group}


async def main(args):
    settings = real_settings(args.project)
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(raw.replace(settings.api_key, "[REDACTED]") + "\n")

    code = {str(p.relative_to(REPO)): sha(p.read_bytes()) for p in (REPO / "backend/app").glob(
        "*.py")}
    protocol = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "application_files": code, "case": args.case, "runs": args.runs,
                "gold_in_prompt": False, "real_provider": settings.model,
                "new_analysis_calls_per_run": 1, "narration_calls_per_run": 1,
                "retries": 0, "live_session_writes": False, "export_partial": args.export_partial}
    gold = None
    if args.case == "choices":
        protocol["fixture"] = load_choices()
        path, project = FIXTURE / "modulo.docx", "checkbox-lab"
        sources = json.loads((FIXTURE / "sources.json").read_text())
        gold = json.loads((FIXTURE / "gold.json").read_text())
    elif args.case == "labirinto":
        material = load_fixture(REPO / "demo-documents/benchmark-compilazione/v1")
        path, sources, project, gold = (material["path"], material["sources"],
                                       material["gold"]["project_id"], material["gold"])
        protocol["fixture"] = material["manifest"]
    elif args.case == "minervino":
        snapshot = REPO / "backend/data/compilation-audit/minervino-output-20261013/analysis"
        frozen = json.loads((snapshot / "input.json").read_text())
        path, sources, project = (snapshot / "original.docx", frozen["sources"],
                                  frozen["project_id"])
        protocol["fixture"] = {"kind": "recorded_input", "path": str(snapshot.relative_to(REPO)),
                               "input_sha256": sha((snapshot / "input.json").read_bytes())}
    else:
        pool = sorted((REPO / "demo-documents/bandi").rglob("*.docx"))
        path = secrets.choice(pool)
        protocol.update(pool=[str(p.relative_to(REPO)) for p in pool],
                        selected=str(path.relative_to(REPO)), extraction_count=1)
        sources = [s for s in json.loads((REPO / "demo-documents/benchmark-sintesi/v1/"
                                          "catanzaro-sources.json").read_text())
                   if s["scope"] == "global"]
        project = "external-checkbox-lab"
    original = path.read_bytes()
    layout = inspect_docx(original, require_candidates=False)
    data = build_global_input(layout, project, sources)
    protocol.update(original_sha256=layout.sha256, source_sha256=sha(json.dumps(sources).encode()))
    save("protocol.json", protocol)
    save("sources.json", sources)
    save("input.json", data)
    if gold:
        save("gold-audit-only.json", gold)
    (args.output / "original.docx").write_bytes(original)
    for name in code:
        save("frozen-code/" + Path(name).name + ".txt", (REPO / name).read_text())
    results = []
    for index in range(args.runs):
        prefix = f"run-{index + 1:02d}"
        folder = args.output / prefix
        folder.mkdir()
        body = global_request(settings, data, thinking=True)
        save(prefix + "/request.json", {"body": body, "schema": data["schema_output"]})
        start = time.perf_counter()
        result = {"index": index + 1, "analysis_calls": 0}

        async def capture(response):
            result["analysis_calls"] += 1
            await response.aread()
            save(prefix + "/http-response.txt", response.text)

        try:
            async with httpx.AsyncClient(timeout=300,
                                         event_hooks={"response": [capture]}) as client:
                raw, model, usage = await asyncio.wait_for(request_model_content(
                    client, settings, body, 300, response_schema=data["schema_output"]), 300)
            result.update(analysis_seconds=time.perf_counter() - start, usage=usage, model=model)
            save(prefix + "/response.txt", raw)
            audit = validate_global_proposal(raw, layout, project, sources, expected_version=11)
            save(prefix + "/audit.json", audit)
            if gold and args.case == "labirinto":
                save(prefix + "/fixture-score.json", score_fixture(raw, audit, gold))
            state = initial_state(layout)
            state.update(phase="REVIEW", audit=audit, catalog=data["form"],
                         reading_plan=data["reading_plan"])
            with use_ai_settings(settings):
                state["dialogue"] = await narrate(state, folder)
            save(prefix + "/dialogue.json", state["dialogue"])
            result.update(narration_seconds=state["dialogue"]["ai_seconds"],
                          narration_usage=state["dialogue"].get("usage"),
                          narration_error=state["dialogue"].get("error"))
            source_ids, _, _ = export_selection({"global_compilation": {
                **state, "fields": review_fields(state)}})
            result.update(groups=len(audit.get("choice_groups", {})),
                valid_groups=sum(g["validation"] == "GROUNDED_GROUP" for g in audit.get(
                    "choice_groups", {}).values()), exportable_source_ids=source_ids)
            from app.compilation_global_dialogue import source_role_coverage

            result.update(source_role_coverage=source_role_coverage(state),
                local_requests=audit.get("clarifications", {}),
                grounded_proposals=[{"candidate_id": f["candidate_id"], "label": f["label"],
                    "value": f.get("proposed_value", f.get("value")),
                    "validation": f["validation"], "conditions": f.get("conditions", []),
                    "source_evidence": f["source_evidence"]} for f in audit["fields"] if (
                        f["validation"] == "GROUNDED_PROPOSAL"
                        or f.get("proposal_grounding") == "GROUNDED_PROPOSAL")])
            save(prefix + "/state.json", state)
            if gold and args.case == "choices":
                fields = {f["candidate_id"]: f for f in audit["fields"]}
                comparisons = [{**g, "actual": fields[g["candidate_id"]].get("proposed_value",
                               fields[g["candidate_id"]].get("value")), "validation":
                               fields[g["candidate_id"]]["validation"]} for g in gold["checkboxes"]]
                result["checkbox_comparisons"] = comparisons
            if args.export_partial and not state["dialogue"].get("error"):
                # Explicit laboratory partial export. No unknown branch is confirmed.
                checkbox_values, effects = materialize_choices(state, source_ids, [])
                texts = {}
                by_id = {f["candidate_id"]: f for f in audit["fields"]}
                by_source = {s["chunk_id"]: s for s in sources}
                for cid in source_ids:
                    f = by_id[cid]
                    if data["form"]["candidates"][cid]["type"] == "checkbox":
                        continue
                    proof = f["source_evidence"][0]
                    value = f.get("proposed_value", f.get("value"))
                    checked = validate_value(layout, {"id": cid, **f}, value,
                                             by_source[proof["chunk_id"]], proof["quote"])
                    assert checked["written_value"] == value and not checked["validation_codes"]
                    texts[cid] = value
                assert audit == validate_global_proposal(raw, layout, project, sources,
                                                        expected_version=11)
                generated = fill_docx(layout, texts, checkbox_values=checkbox_values)
                (folder / "generated.docx").write_bytes(generated)
                actual = word_states(generated)
                assert all(actual[cid] is value for cid, value in checkbox_values.items())
                result.update(written_texts=texts, written_checkboxes=checkbox_values,
                              checkbox_effects=effects, word_checkbox_states=actual,
                              source_only=True, resolved=0)
            result["state"] = "audited"
        except Exception as exc:
            result.update(state="failed", error_type=type(exc).__name__, error=str(exc))
        save(prefix + "/result.json", result)
        results.append(result)
        save("results.json", results)
        assert all(sha((REPO / name).read_bytes()) == digest for name, digest in code.items())
        assert sha(path.read_bytes()) == layout.sha256
        print(json.dumps({k: result[k] for k in ("index", "state", "analysis_calls")}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["choices", "labirinto", "external", "minervino"],
                        required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project", default="prova")
    parser.add_argument("--runs", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--export-partial", action="store_true")
    asyncio.run(main(parser.parse_args()))
