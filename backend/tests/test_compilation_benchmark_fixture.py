"""Fixture and audit-tool regressions, not semantic evaluation of an AI provider."""

import copy
import hashlib
import json
from collections import Counter
from types import SimpleNamespace

import pytest

from app.compilation_global import build_global_input
from app.docx_templates import field_value_error, inspect_docx
from scripts import benchmark_compilation_global as runner
from scripts.compilation_benchmark_fixture import load_fixture, score_fixture
from scripts.create_compilation_benchmark import FIXTURE, build_fixture


@pytest.fixture
def material():
    return load_fixture(FIXTURE)


def test_authored_fixture_is_byte_reproducible_and_manifest_complete():
    first, second = build_fixture(), build_fixture()
    assert first == second
    for name, value in first.items():
        assert (FIXTURE / name).read_bytes() == value, name
    manifest = json.loads(first["manifest.json"])
    assert set(manifest["files"]) == set(first) - {"manifest.json"}


def test_every_physical_position_has_one_authored_annotation(material):
    layout = inspect_docx(material["path"].read_bytes())
    data = build_global_input(layout, material["gold"]["project_id"], material["sources"])
    fields = material["gold"]["fields"]
    assert len(fields) == len({f["key"] for f in fields}) == 55
    assert set(data["form"]["candidates"]) == {f["candidate_id"] for f in fields}
    assert Counter(c["type"] for c in data["form"]["candidates"].values()) == {
        "text": 44, "checkbox": 11}
    assert "expected_state" not in json.dumps(data)
    assert "annotation_origin" not in json.dumps(data)
    assert len(data["sources"]) == 7


def test_visual_branches_share_word_outline_but_authored_semantics_differ(material):
    data = build_global_input(inspect_docx(material["path"].read_bytes()),
                              material["gold"]["project_id"], material["sources"])
    fields = {f["key"]: f for f in material["gold"]["fields"]}
    candidates = data["form"]["candidates"]
    assert candidates[fields["singolo_nome"]["candidate_id"]]["section_ids"] == (
        candidates[fields["dt_nome"]["candidate_id"]]["section_ids"])
    assert fields["singolo_nome"]["expected_state"] == "NOT_APPLICABLE"
    assert fields["dt_nome"]["expected_state"] == "RESOLVED"
    assert fields["firmatario"]["expected_state"] == "MISSING"
    assert len({fields[k]["subject"] for k in ["singolo_nome", "dt_nome", "firmatario"]}) == 3
    for key in ["singolo", "associato", "ingegneria", "direttore"]:
        assert material["gold"]["sections"][key]["word_heading"] is False


def test_supported_values_are_literal_in_authored_sources_and_syntactically_valid(material):
    layout = inspect_docx(material["path"].read_bytes())
    sources = {s["chunk_id"]: s for s in material["sources"]}
    for field in material["gold"]["fields"]:
        if field["expected_state"] != "RESOLVED" or field["type"] == "checkbox":
            continue
        assert any(field["expected_value"] in sources[c]["content"]
                   for c in field["source_chunk_ids"]), field["key"]
        assert field_value_error(layout, field["candidate_id"], field["expected_value"]) is None


def test_unknown_conflicting_and_non_data_positions_are_explicit(material):
    assert Counter(f["expected_state"] for f in material["gold"]["fields"]) == {
        "RESOLVED": 22, "NOT_APPLICABLE": 9, "AMBIGUOUS": 1, "MISSING": 14,
        "NEEDS_APPLICABILITY": 6, "CONFLICTING": 1, "MANUAL": 1, "DO_NOT_FILL": 1}
    keys = {f["key"]: f for f in material["gold"]["fields"]}
    assert keys["dt_albo"]["expected_value"] == "5739"
    assert keys["dt_data"]["expected_value"] is None
    assert keys["procura"]["expected_state"] == "NEEDS_APPLICABILITY"
    assert keys["iso_possesso"]["expected_state"] == "MISSING"


def test_outside_project_source_is_not_part_of_the_model_input(material):
    excluded = json.loads((FIXTURE / "excluded-sources.json").read_text())
    layout = inspect_docx(material["path"].read_bytes())
    with pytest.raises(ValueError, match="fuori progetto"):
        build_global_input(layout, material["gold"]["project_id"], material["sources"] + excluded)
    data = build_global_input(layout, material["gold"]["project_id"], material["sources"])
    assert 901 not in [s["chunk_id"] for s in data["sources"]]
    assert "12/06/2014" not in json.dumps(data)


@pytest.mark.parametrize("change", ["form", "source", "gold"])
def test_changed_fixture_requires_a_new_frozen_manifest(material, tmp_path, change):
    for name, value in build_fixture().items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    name = {"form": "modulo-benchmark.docx", "source": "sources.json", "gold": "gold.json"}[change]
    with (tmp_path / name).open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="modificata"):
        load_fixture(tmp_path)


def sample_proposal(material, key="denominazione"):
    expected = next(f for f in material["gold"]["fields"] if f["key"] == key)
    return {"version": 5, "conditions": {}, "facts": {
        "f": {"value": expected["expected_value"], "evidence": [{"chunk_id": -1}]}},
        "fields": {expected["candidate_id"]: {"disposition": "value", "fact_id": "f"}}}


def test_literal_score_does_not_claim_semantic_approval_or_completion(material):
    raw = json.dumps(sample_proposal(material))
    score = score_fixture(raw, None, material["gold"])
    assert score["value_and_source_matches"] == 1
    assert score["grounded_value_and_source_matches"] == 0
    assert score["semantic_acceptance"] is False
    assert score["omitted"] == 54
    assert score["docx_writes"] == score["session_writes"] == 0


@pytest.mark.parametrize("key", ["firmatario", "procura", "dt_data", "iso_numero",
                                  "polizza", "singolo_nome", "spazio"])
def test_assignment_to_an_unsupported_or_excluded_target_is_reported(material, key):
    proposal = sample_proposal(material)
    field = next(f for f in material["gold"]["fields"] if f["key"] == key)
    assignment = next(iter(proposal["fields"].values()))
    proposal["fields"] = {field["candidate_id"]: assignment}
    score = score_fixture(json.dumps(proposal), None, material["gold"])
    assert score["unexpected_values"] == 1
    assert score["value_and_source_matches"] == 0


def test_correct_value_with_wrong_source_is_not_counted(material):
    proposal = sample_proposal(material)
    proposal["facts"]["f"]["evidence"] = [{"chunk_id": -201}]
    score = score_fixture(json.dumps(proposal), None, material["gold"])
    assert score["value_and_source_matches"] == 0
    assert score["unexpected_values"] == 1


def test_empty_response_is_55_omissions_not_55_missing_values(material):
    raw = json.dumps({"version": 5, "fields": {}, "facts": {}, "conditions": {}})
    score = score_fixture(raw, None, material["gold"])
    assert score["omitted"] == 55
    assert score["unexpected_values"] == score["unexpected_na"] == 0


@pytest.mark.parametrize("key,kind", [("polizza", "conflicting"), ("corrispondenza", "ambiguous")])
def test_review_scoring_is_explicitly_limited_to_kind_and_source_ids(material, key, kind):
    expected = next(f for f in material["gold"]["fields"] if f["key"] == key)
    proof = {"chunk_id": expected["source_chunk_ids"][0]}
    proposal = {"version": 6, "conditions": {}, "facts": {
        "a": {"value": "Alternativa A", "evidence": [proof]},
        "b": {"value": "Alternativa B", "evidence": [proof]}},
        "fields": {expected["candidate_id"]: {
            "disposition": "review", "review_kind": kind, "alternative_fact_ids": ["a", "b"]}}}
    score = score_fixture(json.dumps(proposal), None, material["gold"])
    assert score["review_kind_and_source_matches"] == 1
    assert score["grounded_review_kind_and_source_matches"] == 0
    assert score["unexpected_values"] == 0
    assert score["semantic_acceptance"] is False
    proposal["facts"]["b"]["evidence"] = [{"chunk_id": 999999}]
    assert score_fixture(json.dumps(proposal), None, material["gold"])[
        "review_kind_and_source_matches"] == 0


def test_review_cannot_be_counted_for_a_single_known_value(material):
    proposal = sample_proposal(material)
    assignment = next(iter(proposal["fields"].values()))
    assignment.update(disposition="review", review_kind="ambiguous",
                      alternative_fact_ids=["f", "f"])
    score = score_fixture(json.dumps(proposal), None, material["gold"])
    assert score["review_kind_and_source_matches"] == score["value_and_source_matches"] == 0


def test_cli_requires_exactly_one_input_mode(tmp_path):
    common = ["--profile-project", "profile", "--output", str(tmp_path)]
    assert runner.arguments(common + ["--fixture", str(FIXTURE)]).fixture == FIXTURE
    assert runner.arguments(common + ["--project", "p", "--form-id", "1"]).form_id == 1
    with pytest.raises(SystemExit):
        runner.arguments(common)
    with pytest.raises(SystemExit):
        runner.arguments(common + ["--fixture", str(FIXTURE), "--project", "p"])


def test_fixture_runner_never_reads_local_corpus_or_sends_gold(material, tmp_path, monkeypatch):
    """Simulated software test: no API call and no model-quality claim."""
    raw = json.dumps({"version": 5, "fields": {}, "facts": {}, "conditions": {}})
    captured = []

    async def model(_client, _settings, body, _timeout, **_kwargs):
        captured.append(copy.deepcopy(body))
        return raw, "simulated-software-test", {"total_tokens": 0}

    def forbidden(*args, **kwargs):
        pytest.fail("Fixture runner must not read the local document database")

    monkeypatch.setattr(runner, "get_db_path", forbidden)
    monkeypatch.setattr(runner, "load_document_corpus", forbidden)
    monkeypatch.setattr(runner, "request_model_content", model)
    monkeypatch.setattr(runner, "resolve_project_settings", lambda _: SimpleNamespace(
        provider="deepseek", configured=True, model="simulated-software-test",
        api_key="software-test-key", context_window=32768))
    output = tmp_path / "audit"
    before = hashlib.sha256(material["path"].read_bytes()).hexdigest()
    assert runner.run(runner.arguments([
        "--fixture", str(FIXTURE), "--profile-project", "unused", "--output", str(output)]))
    assert len(captured) == 1
    sent = json.loads(captured[0]["messages"][1]["content"])
    assert len(sent["form"]["candidates"]) == 55
    assert "expected_state" not in json.dumps(sent)
    assert "annotation_origin" not in json.dumps(sent)
    assert (output / "fixture/gold.json").is_file()
    assert json.loads((output / "fixture-score.json").read_text())["omitted"] == 55
    assert hashlib.sha256(material["path"].read_bytes()).hexdigest() == before
