"""Read-only diagnosis of the archived Minervino V12 analysis; no provider calls.

Run from any directory with backend/.venv/bin/python and a NEW --output directory.
The local DB is opened mode=ro. Only the chosen output directory is written.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.compilation_global import (
    build_global_input,
    load_document_corpus,
    validate_global_proposal,
)
from app.compilation_global_dialogue import question_pool
from app.docx_templates import inspect_docx

SESSION = "a067b0abf83f4d948137728669879604"
ATTEMPT = "e8ad0f46c3b34157bbe6c9988e1341f8"
PROJECT = "minervino-di-lecce-elenco-sia"
BASE = ROOT / "backend/data/uploads" / PROJECT / "_global_compilations" / SESSION / ATTEMPT


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    watched = [ROOT / n for n in ["user prompt.json", "richiesta LLM.json",
               "risposta LLm.json", "system prompt.txt", "json narratore.json"]]
    watched += [BASE / n for n in ["input.json", "request.json", "response.txt",
                "audit.json", "metrics.json", "original.docx", "http-response.txt"]]
    before = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in watched}
    inp = read(ROOT / "user prompt.json")
    response = read(ROOT / "risposta LLm.json")
    request = read(ROOT / "richiesta LLM.json")
    narrator = read(ROOT / "json narratore.json")
    audit = read(BASE / "audit.json")
    metrics = read(BASE / "metrics.json")
    http = read(BASE / "http-response.txt")
    layout = inspect_docx((BASE / "original.docx").read_bytes(), require_candidates=False)
    replay = validate_global_proposal(compact(response), layout, PROJECT, inp["sources"],
                                      expected_version=12)
    rebuilt = build_global_input(layout, PROJECT, inp["sources"])
    by_source = defaultdict(list)
    for source in inp["sources"]:
        by_source[(source["file_id"], source["source_name"], source["category"])].append(source)
    sizes = {k: len(compact(v)) for k, v in inp.items()}
    db = sqlite3.connect(f"file:{ROOT / 'backend/data/mapi.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("BEGIN")
    row = db.execute("SELECT version,state_json,original FROM compilation_sessions WHERE id=?",
                     (SESSION,)).fetchone()
    state = json.loads(row["state_json"])
    current_sources = load_document_corpus(db, PROJECT)
    current_map = {s["chunk_id"]: s for s in current_sources}
    source_match = (len(current_sources) == len(inp["sources"]) and all(
        all(current_map.get(s["chunk_id"], {}).get(k) == v for k, v in s.items())
        for s in inp["sources"]))
    report_id = state["last_generation"]["id"]
    generation = db.execute("SELECT report_json FROM document_compilations WHERE id=?",
                            (report_id,)).fetchone()
    generation = json.loads(generation["report_json"])
    session_before = digest(row["state_json"].encode())
    db.rollback()
    db.close()
    conditions = audit.get("conditions", {})
    initial = {**state["global_compilation"], "dialogue": {}, "audit": audit}
    pool_initial = question_pool(initial)
    after_condition = {**initial, "dialogue": {"answers": {
        "condition:" + key: {"applies": True, "action": "CONDITION_TRUE"}
        for key in conditions}}}
    pool_after = question_pool(after_condition)
    rejection_errors = Counter()
    for group in audit.get("coverage_groups", []):
        rejection_errors.update(group.get("validation_errors", []))
    diagnostics = {
        "fields": audit["fields"], "coverage_groups": audit["coverage_groups"],
        "initial_question_pool": pool_initial,
        "question_pool_after_all_conditions_confirmed_in_memory": pool_after,
        "written_fields": generation["fields"],
    }
    result = {
        "kind": "offline_architecture_diagnosis_not_new_llm_benchmark",
        "date": "2026-10-15", "project": PROJECT, "session": SESSION, "attempt": ATTEMPT,
        "input_matches_archived": inp == read(BASE / "input.json"),
        "request_matches_archived": request == read(BASE / "request.json"),
        "response_matches_archived": response == read(BASE / "response.txt"),
        "request_user_matches_input": json.loads(request["messages"][1]["content"]) == inp,
        "system_prompt_matches_request": (ROOT / "system prompt.txt").read_text().rstrip()
        == request["messages"][0]["content"].rstrip(),
        "rebuilt_input_matches_archived": rebuilt == inp,
        "revalidated_audit_matches_archived": replay == audit,
        "current_db_corpus_matches_input": source_match,
        "db_original_matches_archive": digest(row["original"]) == layout.sha256,
        "input_compact_characters": len(compact(inp)),
        "input_components_characters": sizes,
        "form_components_characters": {k: len(compact(v)) for k, v in inp["form"].items()},
        "system_prompt_characters": len(request["messages"][0]["content"]),
        "response_compact_characters": len(compact(response)),
        "response_components_characters": {k: len(compact(v)) for k, v in response.items()},
        "source_content_characters": sum(len(s["content"]) for s in inp["sources"]),
        "source_documents": [{"file_id": key[0], "name": key[1], "category": key[2],
            "chunks": len(sources), "content_characters": sum(len(s["content"]) for s in sources)}
            for key, sources in by_source.items()],
        "catalog": {"candidates": len(inp["form"]["candidates"]),
            "types": dict(Counter(c["type"] for c in inp["form"]["candidates"].values())),
            "table_text_cells": len(layout.cells), "paragraph_text_slots": len(layout.slots),
            "blocks": len(inp["form"]["blocks"]),
            "paragraphs": sum(len(b["paragraphs"]) for b in inp["form"]["blocks"]),
            "tables": len(layout.catalog), "unsupported": layout.unsupported_locations,
            "read_only_parts": inp["form"]["read_only_parts"]},
        "raw_proposals": len(response["fields"]), "raw_facts": len(response["facts"]),
        "raw_choice_groups": len(response["choice_groups"]),
        "raw_clarifications": len(response["clarifications"]),
        "coverage": {k: v for k, v in narrator["coverage"].items() if k != "groups"},
        "coverage_error_occurrences_per_group": dict(rejection_errors),
        "initial_pool_size": len(pool_initial), "after_confirmation_pool_size": len(pool_after),
        "initial_pool_matches_narrator_slots": [q["slot"] for q in pool_initial]
        == [q["slot"] for q in narrator["question_pool"]],
        "analysis_usage_historical": http["usage"],
        "analysis_seconds_historical": metrics["ai_seconds"],
        "analysis_finish_reasons": [c["finish_reason"] for c in http["choices"]],
        "narrator_historical": {k: metrics["dialogue"].get(k) for k in
            ["usage", "ai_seconds", "http_calls"]},
        "current_session_version": row["version"], "generation_id": report_id,
        "written_positions": generation["written_field_count"],
        "written_provenance": dict(Counter(f["provenance"] for f in generation["fields"])),
        "watched_sha256_before": before,
    }
    after = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in watched}
    with sqlite3.connect(f"file:{ROOT / 'backend/data/mapi.db'}?mode=ro", uri=True) as check:
        current = check.execute("SELECT version,state_json FROM compilation_sessions WHERE id=?",
                                (SESSION,)).fetchone()
    result["watched_files_unchanged"] = before == after
    result["session_unchanged"] = (row["version"] == current[0]
        and session_before == digest(current[1].encode()))
    for name, obj in [("metrics.json", result), ("diagnostics.json", diagnostics)]:
        (args.output / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "watched_sha256_before"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
