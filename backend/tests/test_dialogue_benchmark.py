"""Harness checks, not a measurement of the real model's semantic quality."""

import copy
import json
import shutil

import pytest

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.db import get_storage_path, init_database
from app.project_forms import _save_form
from app.repository import create_project
from app.schemas import ProjectCreate
from scripts.benchmark_compilation_dialogue import (
    FIXTURE,
    changed_state,
    load_fixture,
    score_case,
    seed_checkpoint,
)


def test_frozen_gold_has_unique_cases_real_slots_and_no_ids_in_model_projection():
    manifest, contexts, cases = load_fixture(FIXTURE)
    assert manifest["version"] == 1 and len(cases) == 43
    assert set(c["context"] for c in cases) == set(contexts)
    assert all(c["expected"]["values"].keys() <= c["expected"]["actions"].keys() for c in cases)


def test_changed_fixture_refused_before_any_provider_call(tmp_path):
    root = tmp_path / "fixture"
    shutil.copytree(FIXTURE, root)
    (root / "cases.json").write_text("{}")
    with pytest.raises(ValueError, match="Fixture modificata"):
        load_fixture(root)


@pytest.fixture
def checkpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "fixture.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    init_database()
    project = create_project(ProjectCreate(title="Benchmark dialogo", description="Test"))["id"]
    form = _save_form(project, "modulo.docx", (FIXTURE / "modulo-dialogo.docx").read_bytes())
    contexts = load_fixture(FIXTURE)[1]

    def make(name):
        return seed_checkpoint(project, form, contexts[name], name + "-test",
                               FIXTURE / "modulo-dialogo.docx")

    return project, contexts, make


def test_partial_real_backend_update_and_scoring_catches_wrong_recipient(checkpoint):
    from app.compilation_chat import planner_context
    from app.intents import routing_context

    project, contexts, make = checkpoint
    before = make("group")
    message = "contatti@aurora.example"
    after, errors = dialogue.apply_replies(project, before["id"], before["version"], [
        ClarificationReply(slot=2, action="VALUE", value=message, user_quote=message),
    ], message)
    assert not errors
    assert sessions.get_session(project, before["id"]) == after
    effects = changed_state(before, after, contexts["group"]["slots"])
    assert effects["actions"] == {"2": "VALUE"}
    assert effects["values"] == {"2": message} and effects["provenance_ok"]
    route = json.dumps(routing_context(planner_context(before)))
    assert "field_ids" not in route and "t0.r" not in route and "expected" not in route
    expected = next(c for c in load_fixture(FIXTURE)[2] if c["id"] == "group-partial")
    result = {"intent": "answer_fields", "effects": effects, "export_requested": False}
    assert score_case(expected, result)["passed"]
    bad = copy.deepcopy(result)
    bad["effects"]["actions"] = {"3": "VALUE"}
    assert not score_case(expected, bad)["passed"]


@pytest.mark.parametrize("context,written", [("generate", 1), ("generate_empty", 0)])
def test_fixture_exports_really_persist_user_values_or_empty_copy(checkpoint, context, written):
    from app.compilation_session_models import GlobalDraftRequest
    from app.document_compilation_routes import _get_run

    project, _, make = checkpoint
    before = make(context)
    ids, conditions, user_ids = dialogue.export_selection(before)
    after = adapter.generate_draft(project, before["id"], GlobalDraftRequest(
        version=before["version"], candidate_ids=ids, confirmed_condition_ids=conditions,
        user_candidate_ids=user_ids, allow_unresolved=True, allow_empty=not written,
        user_quote="Sì, genera.",
    ))
    report = json.loads(_get_run(project, after["last_generation"]["id"])["report_json"])
    assert after["status"] == "GENERATED" and report["written_field_count"] == written
    assert all(f["provenance"] == "USER" for f in report["fields"])
    from docx import Document

    path = get_storage_path() / _get_run(project, after["last_generation"]["id"])["storage_path"]
    actual = Document(path / "bozza.docx").tables[0].cell(1, 1).text
    assert actual == ("contatti@aurora.example" if written else "")
    assert (path / "template.docx").read_bytes() == (FIXTURE / "modulo-dialogo.docx").read_bytes()


def test_score_never_hides_provider_errors_or_unauthorized_export():
    case = next(c for c in load_fixture(FIXTURE)[2] if c["id"] == "export-no")
    result = {"intent": "reply", "export_requested": True,
              "error": {"type": "GenerationError"},
              "effects": {"actions": {}, "values": {}, "unexpected_recipients": [],
                          "provenance_ok": True}}
    score = score_case(case, result)
    assert not score["passed"]
    assert not score["checks"]["export_intent"] and not score["checks"]["no_execution_error"]
