"""The ordinary «Compilazione DOCX» profile: one canonical creation profile, by FORM segments.

These tests remove the historical switch set by conftest.py, so they see the real default.
"""

import json
import os

import pytest
import test_compilation_resilient_segments as rev2
from test_compilation_global_sessions import api, provider, resolve, start
from test_compilation_p3_hold_validation import SUMMARY, hold, narrator

from app import (
    compilation_branch_scope,
    compilation_form_option_scope,
    compilation_hold_rereview,
    compilation_scope_review,
    compilation_table_scope,
)
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_profile import PREVIOUS, PROFILE_NAME, SECTIONS, historical_flags
from app.db import get_storage_path
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]

EXPERIMENT = ["MAPI_DIALOGUE_REVISION", "MAPI_NARRATION_RECOVERY_REVISION",
              "MAPI_GENERATION_REVISION", "MAPI_DERIVATION_REVISION",
              "MAPI_BRANCH_SCOPE_REVISION", "MAPI_HOLD_REREVIEW_REVISION",
              "MAPI_TABLE_SCOPE_REVISION", "MAPI_FORM_OPTION_SCOPE_REVISION"]


@pytest.fixture(autouse=True)
def ordinary_default(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)
    for variable in EXPERIMENT:
        monkeypatch.delenv(variable, raising=False)


def revisions(state):
    return {k: v for k, v in state.items() if k.endswith("revision")}


def test_new_sessions_get_the_complete_sections_profile_without_any_variable():
    state = adapter.initial_state(inspect_docx(rev2.form_docx(3)))
    assert revisions(state) == SECTIONS
    assert state["compilation_profile"] == PROFILE_NAME
    assert SECTIONS == {
        "backend_revision": 13, "option_authorization_revision": 1,
        "attribution_safety_revision": 1, "derivation_revision": 1, "dialogue_revision": 1,
        "generation_revision": 3, "narration_recovery_revision": 1, "branch_scope_revision": 1,
        "table_scope_revision": 1, "hold_rereview_revision": 2, "form_option_scope_revision": 2,
        "text_checkbox_revision": 1}
    assert PROFILE_NAME == "sezioni-2026-10-25"


@pytest.mark.parametrize("stale", [
    {"MAPI_GENERATION_REVISION": "0"}, {"MAPI_GENERATION_REVISION": "2"},
    {"MAPI_DIALOGUE_REVISION": "0", "MAPI_DERIVATION_REVISION": "0"},
    {"MAPI_HOLD_REREVIEW_REVISION": "1", "MAPI_TABLE_SCOPE_REVISION": "0"},
    {"MAPI_COMPILATION_PROFILE": "qualsiasi altro valore"},
    {"MAPI_FORM_OPTION_SCOPE_REVISION": "1"}, {"MAPI_FORM_OPTION_SCOPE_REVISION": "0"},
])
def test_stale_experiment_variables_cannot_alter_the_ordinary_profile(monkeypatch, stale):
    for variable, value in stale.items():
        monkeypatch.setenv(variable, value)
    assert revisions(adapter.initial_state(inspect_docx(rev2.form_docx(3)))) == SECTIONS


def test_every_control_of_the_profile_is_actually_enabled_by_these_flags():
    """No partial combination: each dependency holds for the canonical flags."""
    data = dict(SECTIONS)
    assert compilation_scope_review.enabled(data)  # Rev 3 scope receipts and final gate.
    assert compilation_branch_scope.enabled(data)  # R1.
    assert compilation_table_scope.enabled(data)  # Conditional tables.
    assert compilation_hold_rereview.enabled(data)  # Misattributed holds.
    assert compilation_form_option_scope.enabled(data)  # FORM options and instructions.
    assert data["hold_rereview_revision"] == 2  # And grounded SOURCE role holds.
    assert dialogue.narration_attempt_limit(data) == 2  # Narrator recovery.
    assert data["dialogue_revision"] == 1  # Hold re-reviews need the P3 question pool.


def _previous_initial_flags(env):
    """Reference copy of the creation rules before 24 October 2026."""
    experiment = {revision: 1 for revision, variable in (
        ("dialogue_revision", "MAPI_DIALOGUE_REVISION"),
        ("narration_recovery_revision", "MAPI_NARRATION_RECOVERY_REVISION"),
        ("generation_revision", "MAPI_GENERATION_REVISION")) if env.get(variable) == "1"}
    if env.get("MAPI_DERIVATION_REVISION", "1") == "1":
        experiment["derivation_revision"] = 1
    if env.get("MAPI_GENERATION_REVISION") in {"2", "3"}:
        experiment["generation_revision"] = int(env["MAPI_GENERATION_REVISION"])
    if experiment.get("generation_revision") == 3 and env.get("MAPI_BRANCH_SCOPE_REVISION") == "1":
        experiment["branch_scope_revision"] = 1
    if (experiment.get("generation_revision") == 3
            and env.get("MAPI_HOLD_REREVIEW_REVISION") in {"1", "2"}):
        experiment["hold_rereview_revision"] = int(env["MAPI_HOLD_REREVIEW_REVISION"])
    if experiment.get("generation_revision") == 3 and env.get("MAPI_TABLE_SCOPE_REVISION") == "1":
        experiment["table_scope_revision"] = 1
    return {"backend_revision": 13, "option_authorization_revision": 1,
            "attribution_safety_revision": 1, **experiment}


@pytest.mark.parametrize("env", [
    {}, {"MAPI_DERIVATION_REVISION": "0"}, {"MAPI_DIALOGUE_REVISION": "1"},
    {"MAPI_GENERATION_REVISION": "1"}, {"MAPI_GENERATION_REVISION": "2"},
    {"MAPI_GENERATION_REVISION": "3", "MAPI_DIALOGUE_REVISION": "1",
     "MAPI_NARRATION_RECOVERY_REVISION": "1", "MAPI_BRANCH_SCOPE_REVISION": "1",
     "MAPI_HOLD_REREVIEW_REVISION": "2", "MAPI_TABLE_SCOPE_REVISION": "1"},
    {"MAPI_GENERATION_REVISION": "2", "MAPI_BRANCH_SCOPE_REVISION": "1"},
])
def test_the_historical_switch_reproduces_the_previous_creation_rules(monkeypatch, env):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "storico")
    for variable, value in env.items():
        monkeypatch.setenv(variable, value)
    expected = _previous_initial_flags(dict(os.environ))
    assert historical_flags() == expected
    state = adapter.initial_state(inspect_docx(rev2.form_docx(3)))
    assert revisions(state) == expected and "compilation_profile" not in state


@pytest.mark.anyio
async def test_a_new_ordinary_session_compiles_by_sections_and_exports_only_reviewed_values(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Dato 59", "source")]},
             {"questions": []})
    model = rev2.Model()
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    assert revisions(session["global_compilation"]) == SECTIONS
    session = (await rev2.analyze(api, session)).json()
    data = rev2.state_of(session)["global_compilation"]
    assert revisions(data) == SECTIONS and data["compilation_profile"] == PROFILE_NAME
    report = data["audit"]["generation_segments"]
    assert report["revision"] == 3 and [s["status"] for s in report["segments"]] == [
        "analyzed"] * 3
    # Every segment reads the complete FORM and owns only its destinations.
    root = get_storage_path().resolve() / data["artifact_path"] / "segments"
    requests = sorted(root.glob("*/request.json"))
    assert len(requests) == len(model.calls) == 3
    owned = []
    for path in requests:
        body = json.loads(path.read_text())
        segment_input = json.loads(body["messages"][1]["content"])
        own = body["messages"][2]["content"].rsplit("[", 1)[1].rstrip("]").split(",")
        assert [b["id"] for b in segment_input["form"]["blocks"]] == [
            b["id"] for b in data["catalog"]["blocks"]]
        assert sorted(segment_input["form"]["candidates"]) == sorted(own)
        owned += own
    assert sorted(owned) == sorted(data["catalog"]["candidates"])
    for flag in ("branch_scope", "table_scope"):
        assert flag in data["audit"]
    held = set(data["dialogue"]["held_candidate_ids"])
    ids, _, _ = dialogue.export_selection(session)
    assert held and ids and not held & set(ids)
    assert (await rev2.draft(api, session, [*ids, *held])).status_code == 409
    exported = await rev2.draft(api, session, ids)
    assert exported.status_code == 200, exported.text


@pytest.mark.anyio
async def test_an_existing_session_keeps_the_profile_it_was_created_with(
    api, provider, monkeypatch,
):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "storico")
    session = await start(api)  # Monolithic session, the standard simulated provider.
    created = revisions(session["global_compilation"])
    assert "generation_revision" not in created
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE")  # The new default is now in force.
    session = await resolve(api, session)
    data = rev2.state_of(session)["global_compilation"]
    assert revisions(data) == created and "compilation_profile" not in data
    assert "generation_segments" not in data["audit"]  # Still the monolithic analysis.


def test_the_emergency_switch_recreates_the_profile_before_the_form_scope_adoption(monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-24")
    state = adapter.initial_state(inspect_docx(rev2.form_docx(3)))
    assert revisions(state) == PREVIOUS["sezioni-2026-10-24"]
    assert state["compilation_profile"] == "sezioni-2026-10-24"
    assert "form_option_scope_revision" not in state
    assert not compilation_form_option_scope.enabled(state)
    assert {**PREVIOUS["sezioni-2026-10-24"], "form_option_scope_revision": 2,
            "text_checkbox_revision": 1} == SECTIONS
    assert "text_checkbox_revision" not in state


def test_text_checkbox_catalog_is_automatic_but_old_sessions_are_not_upgraded():
    from test_text_checkboxes import form_bytes

    from app.compilation_catalog import build_compilation_catalog
    from app.compilation_sessions import read_original

    original = form_bytes()
    layout = inspect_docx(original, require_candidates=False)
    new = adapter.initial_state(layout)
    assert new["compilation_profile"] == "sezioni-2026-10-25"
    assert new["text_checkbox_revision"] == 1
    assert "p0.txcb0" in new["catalog"]["candidates"]
    previous = {k: v for k, v in new.items() if k != "text_checkbox_revision"}
    state = {"engine": "global", "template_sha256": layout.sha256, "global_compilation": previous}
    row = {"original": original, "state_json": json.dumps(state)}
    reopened = read_original(row)
    assert reopened.text_checkbox_revision == 0
    assert "p0.txcb0" not in build_compilation_catalog(reopened)["candidates"]
    assert json.loads(row["state_json"])["global_compilation"] == previous
