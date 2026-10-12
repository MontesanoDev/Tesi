"""Frozen protocol/setup checks; no real provider used in software tests."""

import copy
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


@pytest.fixture
def role_data():
    _, cases = runner.load_fixture()
    return runner.prepare_case(next(c for c in cases if c["id"] == "generic-primo-cessato"))


def test_role_proofs_shared_per_subject_without_changing_audit(role_data):
    before = copy.deepcopy(role_data)
    context = model_context(role_data, [])
    assert role_data == before  # Full provenance and chunk references untouched.
    roles = context["role_contexts"]
    assert len(roles) == 2
    assert [v["role_context_slot"] for v in context["document_values"]] == [1, 1, 2, 2]
    assert roles[0]["subject"] == "Dr. Ada Neri"
    assert roles[1]["subject"] == "Dr. Bea Mori"
    assert "concluso nel 2019" in roles[0]["sources"][0]["quote"]
    assert "Incarico attivo" in roles[1]["sources"][0]["quote"]
    assert all(r["semantic_review_required"] for r in roles)
    assert all(s["role"] == "source" and s["category"] == "company"
               for r in roles for s in r["sources"])
    assert "chunk_id" not in json.dumps(context)
    assert "paragraph:" not in json.dumps(context)


@pytest.mark.parametrize("change", ["binding_absent", "binding_invalid", "fact_invalid",
                                   "field_binding_invalid", "form", "general"])
def test_no_role_context_from_unchecked_or_non_source_links(role_data, change):
    field = role_data["audit"]["fields"][0]
    binding_id = field["subject_binding"]["binding_id"]
    if change == "binding_absent":
        role_data["audit"]["bindings"].pop(binding_id)
    elif change == "binding_invalid":
        role_data["audit"]["bindings"][binding_id]["validation_errors"] = ["invalid"]
    elif change == "fact_invalid":
        role_data["audit"]["facts"][field["fact_id"]]["validation"] = "REVIEW_REQUIRED"
    elif change == "field_binding_invalid":
        field["subject_binding"]["result"] = "review_required"
    elif change == "form":
        field["subject_binding"]["source_evidence"][0]["role"] = "form"
    else:
        field["subject_binding"]["source_evidence"][0]["category"] = "general"
    assert model_context(role_data, [])["document_values"][0]["role_context_slot"] is None


def test_conditional_proposal_keeps_role_proof_without_confirming_condition():
    _, cases = runner.load_fixture()
    data = runner.prepare_case(next(c for c in cases if c["id"] == "catanzaro-unconfirmed"))
    context = model_context(data, [])
    director = [v for v in context["document_values"] if v["role_context_slot"]]
    assert len(director) == 4
    assert len(context["role_contexts"]) == 1
    assert all(v["conditional"] for v in director)
    assert "direttore tecnico" in context["role_contexts"][0]["sources"][0]["quote"]
    assert "answers" not in data["dialogue"]


def test_role_context_budget_and_truncation_remain_bounded(role_data):
    audit = role_data["audit"]
    original = audit["fields"][0]
    expanded = []
    for index in range(50):
        f = copy.deepcopy(original)
        cid = f"t{index}.r0.c1"
        f["candidate_id"] = cid
        fid, bid = "f" + str(index), "b" + str(index)
        audit["facts"][fid] = copy.deepcopy(audit["facts"][original["fact_id"]])
        audit["bindings"][bid] = copy.deepcopy(audit["bindings"]["b0"])
        f["fact_id"], f["subject_binding"]["binding_id"] = fid, bid
        proof = f["subject_binding"]["source_evidence"][0]
        proof["quote"] = "a" * 1000
        f["subject_binding"]["source_evidence"] = [proof] * 5
        role_data["writable_ids"].append(cid)
        expanded.append(f)
    audit["fields"] = expanded
    context = model_context(role_data, [])
    assert len(context["document_values"]) == len(context["role_contexts"]) == 40
    assert all(len(r["sources"]) == 2 for r in context["role_contexts"])
    assert all(len(s["quote"]) == 800 and s["truncated"]
               for r in context["role_contexts"] for s in r["sources"])
