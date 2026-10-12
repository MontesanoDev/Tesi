"""Frozen protocol/setup checks; no real provider used in software tests."""

import importlib.util
import json
from pathlib import Path

import pytest

from app.compilation_global_dialogue import model_context

PATH = Path(__file__).resolve().parents[2] / "docs/benchmarks/benchmark_narration_roles.py"
spec = importlib.util.spec_from_file_location("narration_roles_benchmark", PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_frozen_protocol_and_replay_keep_real_analysis_anchors():
    manifest, cases = runner.load_fixture()
    assert manifest["max_cases"] == len(cases) == 7
    assert manifest["gold_in_prompt"] is False and manifest["new_analysis_calls"] == 0
    for case in cases:
        data = runner.prepare_case(case)
        context = model_context(data, [])
        assert all(v["form_context"] for v in context["document_values"])
        assert "exportable_source_ids" not in json.dumps(context)
        assert not any(v.get("provenance") == "USER" for v in context["document_values"])


def test_literal_grounding_does_not_certify_current_role():
    _, cases = runner.load_fixture()
    for case in cases:
        if case["id"] not in {"generic-primo-cessato", "generic-entrambi-cessati"}:
            continue
        data = runner.prepare_case(case)
        proposed = [f for f in data["audit"]["fields"] if f.get("subject_binding")]
        assert len(proposed) == 4
        assert all(f["subject_binding"]["result"] == "literal_match"
                   for f in proposed)
        assert all(f["validation"] == "GROUNDED_PROPOSAL" for f in proposed)


def test_different_role_already_excluded_before_narration():
    _, cases = runner.load_fixture()
    data = runner.prepare_case(next(c for c in cases if c["id"] == "generic-ruolo-diverso"))
    assert len(model_context(data, [])["document_values"]) == 2


def test_fixture_changes_fail_before_api(tmp_path):
    (tmp_path / "cases.json").write_text("changed")
    (tmp_path / "manifest.json").write_text(json.dumps({"files": {"cases.json": "wrong"}}))
    with pytest.raises(ValueError, match="Fixture modificata"):
        runner.load_fixture(tmp_path)
