"""Real narration of a recorded failed analysis; no new analysis or session writes.

Run from backend with PYTHONPATH=.; input is the sanitized recorded-failure copy.
The model's rejected groups and recorded dialogue are replayed without repair.
"""

import argparse
import asyncio
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

from app.compilation_global import validate_global_proposal
from app.compilation_global_dialogue import (
    DialoguePlan,
    export_selection,
    narrate,
    question_pool,
    render_dialogue,
)
from app.compilation_global_sessions import initial_state, review_fields
from app.config import use_ai_settings
from app.db import get_db_path
from app.docx_templates import inspect_docx
from scripts.benchmark_compilation_dialogue import real_settings


async def main(args):
    settings = real_settings(args.project)
    if settings.provider != "deepseek" or settings.model != "deepseek-flash":
        raise ValueError("Questo replay richiede il profilo reale DeepSeek Flash")
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(text.replace(settings.api_key, "[REDACTED]") + "\n")

    application = Path(__file__).resolve().parents[2] / "backend/app"
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in application.glob("*.py")}
    original = (args.input / "original.docx").read_bytes()
    layout = inspect_docx(original)
    request = json.loads((args.input / "input.json").read_text())
    audit = validate_global_proposal((args.input / "response.txt").read_text(), layout,
                                    args.project, request["sources"], expected_version=11)
    assert audit == json.loads((args.input / "audit.json").read_text())
    data = {**initial_state(layout), "catalog": request["form"], "audit": audit}
    # Same real recorded narration, no provider call or synthetic response.
    plan = DialoguePlan.model_validate_json(next(args.input.glob("dialogue/*/response.txt"))
                                            .read_text())
    proposals = [f for f in review_fields(data) if f["selectable"]][:40]
    reviewed = {"reviewed_candidate_ids": [f["candidate_id"] for f in proposals],
                "held_candidate_ids": [proposals[i - 1]["candidate_id"]
                                       for i in plan.held_proposal_slots]}
    selection = export_selection({"global_compilation": {**data, "fields": review_fields(data),
        "dialogue": {"phase": "READY", **reviewed}}})
    replay = render_dialogue(plan, question_pool(data),
                            exportable_count=len(selection[0]) + len(selection[2]))
    save("recorded-dialogue-replay.json", replay)
    save("protocol.json", {"head": subprocess.check_output(["git", "rev-parse", "HEAD"],
        text=True).strip(), "application_sha256": code, "model": settings.model,
        "new_analysis_calls": 0, "new_narration_calls": 1, "provider_simulated": False,
        "reused_real_analysis": True, "session_writes": False,
        "original_sha256": layout.sha256, "source_audit_revalidated": True})
    for name in code:
        save("frozen-code/" + name + ".txt", (application / name).read_text())
    with use_ai_settings(settings):
        result = await narrate(data, args.output / "real-narration")
    save("result.json", result)
    assert not result.get("error"), result
    assert result["phase"] == "READY" and result.get("http_calls") == 1
    assert all(hashlib.sha256((application / name).read_bytes()).hexdigest() == digest
               for name, digest in code.items())
    assert (args.input / "original.docx").read_bytes() == original
    before = json.loads((args.input.parent / "live-before.json").read_text())
    with sqlite3.connect(get_db_path().resolve().as_uri() + "?mode=ro", uri=True) as db:
        row = db.execute("SELECT state_json,version,original FROM compilation_sessions WHERE id=?",
                         (before["session_id"],)).fetchone()
    unchanged = (hashlib.sha256(row[0].encode()).hexdigest() == before["state_sha256"]
                 and row[1] == before["version"]
                 and hashlib.sha256(row[2]).hexdigest() == before["original_sha256"])
    save("integrity.json", {"live_session_and_original_unchanged": unchanged,
         "recorded_dialogue_replayed_without_error": True,
         "grounded_conditional_proposals": audit.get("grounded_conditional_proposals", 0),
         "rejected_groups": {k: g["validation_errors"] for k, g in audit["choice_groups"].items()
                             if g["validation"] == "REJECTED"}})
    assert unchanged
    print(json.dumps({"new_analysis_calls": 0, "narration_calls": result["http_calls"],
                      "error": result.get("error"), "live_session_unchanged": unchanged}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
