"""Frozen guard protocol checks; no real or simulated AI calls here."""

import json
import shutil

import pytest

from scripts.benchmark_compilation_reply_guard import GUARD_FIXTURE, load_guard_fixture

FIXTURE = GUARD_FIXTURE.parent / "group-confirmations-v1"


@pytest.mark.parametrize("root,count", [(GUARD_FIXTURE, 9), (FIXTURE, 16)])
def test_frozen_guard_cases_have_bounded_real_slots(root, count):
    manifest, contexts, cases = load_guard_fixture(root)
    assert len(cases) == count <= manifest["max_cases"]
    for case in cases:
        assert set(case["expected_allowed_slots"]) <= {
            s["slot"] for s in contexts[case["context"]]["slots"]}


def test_changed_group_fixture_rejected_before_provider(tmp_path):
    root = tmp_path / "guard"
    shutil.copytree(FIXTURE, root)
    (root / "contexts.json").write_text("{}")
    with pytest.raises(ValueError, match="Fixture guard modificata"):
        load_guard_fixture(root)


def test_recorded_case_keeps_proposals_and_precise_questions_separate_from_gold():
    _, contexts, cases = load_guard_fixture(FIXTURE)
    case = next(c for c in cases if c["id"] == "recorded-real")
    context = contexts[case["context"]]
    assert case["message"].startswith("Confermo entrambe:")
    assert case["proposals"][1]["user_quote"] == "il partecipante è quello indicato nelle fonti"
    assert all(s["question"] in context["message"] for s in context["slots"])
    assert "expected" not in json.dumps(context)
