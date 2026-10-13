"""Authored frozen fixture integrity, independent of any provider output."""

import hashlib
import json
from pathlib import Path

from app.compilation_global import build_global_input
from app.docx_templates import inspect_docx

ROOT = Path(__file__).resolve().parents[2] / "demo-documents/benchmark-checkbox/v1"


def test_checkbox_fixture_hashes_subjects_and_no_gold_in_input():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    layout = inspect_docx((ROOT / "modulo.docx").read_bytes(), require_candidates=False)
    sources = json.loads((ROOT / "sources.json").read_text())
    data = build_global_input(layout, manifest["project_id"], sources)
    gold = json.loads((ROOT / "gold.json").read_text())
    ids = {cid for cid, c in data["form"]["candidates"].items() if c["type"] == "checkbox"}
    assert len(ids) == 14 and ids == {g["candidate_id"] for g in gold["checkboxes"]}
    assert sum(type(g["expected"]) is bool for g in gold["checkboxes"]) == 10
    assert {g["subject"] for g in gold["checkboxes"]} == {"Vega S.r.l.", "Delta Laboratorio"}
    assert "expected" not in json.dumps(data) and "user_messages" not in json.dumps(data)
    assert manifest["runs"] == 3 and manifest["gold_in_prompt"] is False
