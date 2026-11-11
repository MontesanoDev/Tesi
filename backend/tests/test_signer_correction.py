"""Signer changes preserve unrelated receipts; USER identity is not a SOURCE fact."""

import json
from copy import deepcopy
from io import BytesIO

import pytest
from docx import Document
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_incremental_conversation import conversational, edit
from test_compilation_value_completeness import prepared, state
from test_signatory_order_and_extension import open_name_case

from app import compilation_conversation as conversation
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_scope_review as scope
from app import compilation_sessions as sessions
from app import intents
from app.compilation_chat import ClarificationReply, planner_context
from app.compilation_value_completeness import value_check
from app.config import use_ai_settings
from app.db import connection

__all__ = ["api", "provider"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.parametrize("name", ["Paolo Conti", "Nadia D'Amico", "Jean-Luc O’Neill"])
def test_literal_full_user_name_has_own_completeness_proof(name):
    case = prepared(label="Il sottoscritto — Nome e cognome", value="Ada Neri",
                    entity="person", subject="Ada Neri")
    data, cid = state(case), case[4]
    data["conversation_revision"] = 1
    before = deepcopy(data["audit"])
    check = value_check(data, cid, name, user_quote=f"Metti {name} nel campo nome.")
    assert check["result"] == "COMPLETE"
    assert check["components"]["full_name"]["evidence"][0]["role"] == "user"
    assert data["audit"] == before  # SOURCE evaluation is neither replaced nor promoted.


@pytest.mark.parametrize("value,quote", [
    ("Paolo", "Paolo"), ("Paolo Conti", "Confermo tutto"),
    ("Paolo Conti nato a Roma", "Paolo Conti nato a Roma"),
    ("Paolo oppure Ada", "Paolo oppure Ada"), ("", "Confermo"),
])
def test_user_name_completeness_does_not_accept_partial_invented_or_compound(value, quote):
    case = prepared(label="Nome e cognome", value="Ada Neri", entity="person", subject="Ada Neri")
    data = state(case)
    data["conversation_revision"] = 1
    assert value_check(data, case[4], value, user_quote=quote)["result"] != "COMPLETE"


def test_other_compound_user_data_still_require_source():
    case = prepared(label="Numero e data d'iscrizione", value="123")
    data = state(case)
    data["conversation_revision"] = 1
    assert value_check(data, case[4], "123 del 14/03/2019",
                       user_quote="123 del 14/03/2019")["result"] != "COMPLETE"


def change_case(monkeypatch):
    data = {"conversation_revision": 1, "catalog": {"candidates": {}}, "audit": {
        "fields": [], "conditions": {
            "person": {"scope": [{"kind": "candidate", "id": "name"}],
                       "form_evidence": {"quote": "Il sottoscritto"}},
            "company": {"scope": [{"kind": "candidate", "id": "company"}],
                        "form_evidence": {"quote": "dell'operatore economico"}},
            "role": {"scope": [{"kind": "candidate", "id": "company"}],
                     "form_evidence": {"quote": "Legale rappresentante della società"}},
        }}, "dialogue": {"answers": {}, "user_values": {
            "name": {"value": "Ada Neri"}, "birth": {"value": "Roma"}}}}
    for key, affected in [("person", ["name", "birth", "role"]),
                          ("company", ["role", "company"]), ("role", ["company"])]:
        data["dialogue"]["answers"]["condition:"+key] = {
            "action": "CONDITION_TRUE", "applies": True, "affected_fields": affected,
            "provenance": "USER", "scope_validation": "previously_verified",
            "user_quote": "Conferma originale", "condition_group": "condition:company"}
    monkeypatch.setattr(conversation, "person_groups", lambda data: {
        "name": {"name", "birth", "role"}})
    monkeypatch.setattr(conversation, "fields", lambda data: {})
    monkeypatch.setattr("app.compilation_source_reuse._signatory_groups",
                        lambda data: [{"name_id": "name"}])
    return data


def test_person_change_preserves_company_receipt_but_retracts_identity_and_role(monkeypatch):
    data = change_case(monkeypatch)
    company = deepcopy(data["dialogue"]["answers"]["condition:company"])
    conversation.before_change(data, {"kind": "value", "key": "field:name", "field_ids": ["name"]},
        ClarificationReply(slot=1, action="VALUE", value="Liam Mori",
                           user_quote="Il firmatario è Liam Mori"),
        "Il firmatario è Liam Mori")
    assert data["dialogue"]["answers"].get("condition:company") == company
    assert "condition:person" not in data["dialogue"]["answers"]
    assert "condition:role" not in data["dialogue"]["answers"]
    assert "birth" not in data["dialogue"]["user_values"]
    assert {s["key"] for s in data["dialogue"]["superseded"]} >= {
        "condition:person", "condition:role", "field:birth"}


def test_missing_or_mixed_condition_scope_is_not_assumed_independent(monkeypatch):
    for declared_scope in [[], [{"kind": "candidate", "id": "name"},
                       {"kind": "candidate", "id": "company"}]]:
        data = change_case(monkeypatch)
        data["audit"]["conditions"]["company"]["scope"] = declared_scope
        slot = {"kind": "value", "key": "field:name", "field_ids": ["name"]}
        conversation.before_change(data, slot,
            ClarificationReply(slot=1, action="VALUE", value="Liam Mori", user_quote="Liam Mori"),
            "Liam Mori")
        assert "condition:company" not in data["dialogue"]["answers"]


def test_router_exposes_separate_identity_confirmation_target():
    data, _, _ = open_name_case()
    data.update(conversation_revision=1, phase="REVIEW")
    entries = conversation.targets(data)
    public = conversation.public_targets(data, entries)
    name = next(q for q in entries if q["key"] == "field:p0.s0")
    condition = next(q for q in entries if q["key"] == "condition:c_firm")
    visible = next(q for q in public if q["target"] == name["target"])
    assert visible["identity_confirmations"] == [condition["target"]]
    assert not data["dialogue"].get("answers")  # Exposing context does not authorize it.


def test_withdrawn_source_fact_keeps_form_target_and_independent_receipt_digest():
    from test_compilation_selected_person import case

    from app.compilation_source_reuse import reuse_selected_person

    data, layout, sources = case()
    data.update(conversation_revision=1, generation_revision=3)
    fresh = deepcopy(data["audit"])
    data["audit"] = reuse_selected_person(data, layout, "alpha", sources)
    before = scope.target(data, "condition:company", ["p2.s0", "p2.s1"])
    old_field = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p2.s0")
    assert old_field.get("source_reuse") and old_field.get("form_evidence")
    user = data["dialogue"]["user_values"]["p0.s0"]
    user.update(value="Paolo Conti", user_quote="Paolo Conti")
    data["dialogue"]["answers"]["field:p0.s0"].update(value="Paolo Conti", user_quote="Paolo Conti")
    reconciled = conversation.reconcile_identity(data, fresh)
    after = scope.target({**data, "audit": reconciled}, "condition:company", ["p2.s0", "p2.s1"])
    assert after["digest"] == before["digest"]
    field = next(f for f in reconciled["fields"] if f["candidate_id"] == "p2.s0")
    assert not field.get("value") and not field.get("source_evidence")
    assert field["retained_form_target"]
    again = conversation.reconcile_identity({**data, "audit": reconciled}, fresh)
    assert scope.target({**data, "audit": again}, "condition:company", ["p2.s0", "p2.s1"]) == after


def test_guard_context_distinguishes_requested_destinations_without_changing_proof():
    data, _, _ = open_name_case()
    data.update(conversation_revision=1, phase="REVIEW")
    q = {"slot": 1, "key": "condition:c_firm", "field_ids": ["p0.s0"],
         "condition": "Il sottoscritto"}
    before = scope.target(data, q["key"], q["field_ids"])
    sent = scope.context(data, [q])["slots"]["1"]
    assert sent["digest"] == before["digest"]
    assert sent["conditions"] == before["conditions"]
    assert sent["requested_confirmation"]["candidate_ids"] == ["p0.s0"]
    assert not sent["requested_confirmation"]["other_MODEL_scope_destinations_requested"]


def test_revalidation_of_unchanged_source_person_keeps_identical_fields(monkeypatch, tmp_path):
    from test_compilation_selected_person import case

    from app.compilation_source_reuse import reuse_selected_person

    data, layout, sources = case()
    data.update(conversation_revision=1, generation_revision=3, artifact_path="proposal")
    original = deepcopy(data["audit"])
    data["audit"] = reuse_selected_person(data, layout, "alpha", sources)
    folder = tmp_path / "proposal"
    folder.mkdir()
    (folder / "response.txt").write_text("immutable model response")
    monkeypatch.setattr(adapter, "get_storage_path", lambda: tmp_path)
    monkeypatch.setattr(sessions, "read_original", lambda row: layout)
    monkeypatch.setattr(adapter, "load_document_corpus", lambda db, project: sources)
    monkeypatch.setattr(adapter, "validated_audit", lambda *args, **kwargs: deepcopy(original))
    fresh = adapter.refreshed_audit(None, {"project_id": "alpha"}, {"global_compilation": data})
    assert fresh["fields"] == data["audit"]["fields"]


def test_identity_question_does_not_include_withdrawn_values_or_confirm_them(monkeypatch):
    data = change_case(monkeypatch)
    question = {"key": "condition:person", "kind": "applicability",
                "condition": "Il sottoscritto", "field_ids": ["name", "birth", "role"]}
    data["dialogue"]["user_values"].pop("birth")
    result = conversation.current_identity_scope(data, question)
    assert result["field_ids"] == ["name"]
    assert question["field_ids"] == ["name", "birth", "role"]
    assert data["audit"]["conditions"]["person"]["scope"] == [{"kind": "candidate", "id": "name"}]


@pytest.mark.anyio
async def test_other_form_free_name_export_resume_correct_preserves_first(
    api, provider, monkeypatch,
):
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Il sottoscritto — Nome e cognome"
    table.cell(1, 0).text = "Codice fiscale personale"
    s = await conversational(api, monkeypatch, doc)
    originals = []
    for name in ["Paolo Conti", "Nadia D'Amico"]:
        s, _, _ = await edit(s, monkeypatch, f"Metti {name} nel campo Il sottoscritto.",
                             "field:t0.r0.c1", name)
        assert s["global_compilation"]["dialogue"]["latest_turn"]["accepted"]
        s = await resolve(api, s)
        ids, conditions, users = dialogue.export_selection(s)
        result = await api.post(f"{BASE}/{s['id']}/global-draft", json={
            "version": s["version"], "candidate_ids": ids, "confirmed_condition_ids": conditions,
            "user_candidate_ids": users, "allow_unresolved": True, "user_quote": "Bozza"})
        assert result.status_code == 200, result.text
        s = result.json()
        url = s["last_generation"]["downloads"]["docx"]
        raw = (await api.get(url)).content
        generated = Document(BytesIO(raw))
        assert generated.tables[0].cell(0, 1).text == name
        assert not generated.tables[0].cell(1, 1).text.strip()
        assert "BOZZA NON VERIFICATA" in '\n'.join(p.text for p in generated.paragraphs)
        originals.append((url, raw))
        s = adapter.control_session("alpha", s["id"], s["version"], "pause")
        s = adapter.control_session("alpha", s["id"], s["version"], "resume")
        s = sessions.get_session("alpha", s["id"])
        s = await resolve(api, s)
    assert (await api.get(originals[0][0])).content == originals[0][1]


@pytest.mark.anyio
@pytest.mark.parametrize("reject_confirmation", [False, True])
async def test_new_identity_confirmation_survives_router_order_and_needs_own_guard(
    api, provider, monkeypatch, reject_confirmation,
):
    doc = Document()
    doc.add_paragraph("Il sottoscritto ________")
    s = await conversational(api, monkeypatch, doc)
    # Isolate receipt ordering from model generation. FORM and persistent state are real;
    # the revalidation boundary supplies the same unchanged, synthetic analysis each time.
    with connection() as db:
        row, raw = adapter._row_state(db, "alpha", s["id"], s["version"])
        data = raw["global_compilation"]
        data["audit"]["conditions"]["identity"] = {
            "result": "unknown", "aspect": "identity", "operator": "semantic",
            "form_evidence": {"paragraph_id": "paragraph:0", "quote": "Il sottoscritto"},
            "scope": [{"kind": "candidate", "id": "p0.s0"}],
            "reason": "Firmatario da confermare"}
        data["audit"]["fields"][0].update(conditions=["identity"],
            form_evidence={"paragraph_id": "paragraph:0", "quote": "Il sottoscritto"},
            label="Il sottoscritto", kind="data")
        s = sessions.save_state(db, row, raw, "test_condition_fixture")
    monkeypatch.setattr(adapter, "refreshed_audit", lambda db, row, state: deepcopy(
        state["global_compilation"]["audit"]))

    for index, name in enumerate(["Ada Neri", "Paolo Conti"]):
        data = scope.session_data(s)
        entries = conversation.targets(data)
        assert any(q["kind"] == "applicability" for q in entries), json.dumps({
            "phase": data.get("phase"), "conditions": data["audit"].get("conditions"),
            "fields": data["audit"]["fields"], "entries": entries})
        condition = next(q for q in entries if q["kind"] == "applicability")
        target = next(q for q in entries if q["key"] == "field:p0.s0")
        message = f"Confermo che il firmatario di questa domanda è {name}."

        async def model(client, settings, body, timeout, **kwargs):
            if kwargs["response_schema"]["title"] == "FormScopeChecks":
                sent = json.loads(body["messages"][1]["content"])
                checks = [{"slot": p["slot"], "result": "SUPPORTED",
                           "scope_result": "AMBIGUOUS" if index and reject_confirmation
                           and p["action"] == "CONDITION_TRUE" else "SUPPORTED"}
                          for p in sent["proposals"]]
                return json.dumps({"checks": checks}), "simulated", {}
            return json.dumps({"intent": "edit_fields", "answer": "", "queries": [],
                "target": "form", "edits": [
                    {"target": condition["target"], "action": "CONDITION_TRUE",
                     "user_quote": message},
                    {"target": target["target"], "action": "VALUE", "value": name,
                     "user_quote": message}]}), "simulated", {}

        monkeypatch.setattr(intents, "request_model_content", model)
        with use_ai_settings(adapter.get_ai_settings()):
            plan = await intents.plan_chat_turn(message, [], compilation=planner_context(s))
        from app.compilation_chat import handle_group_decision

        await handle_group_decision("alpha", None, plan.decision, s, message)
        s = sessions.get_session("alpha", s["id"])
        s = await resolve(api, s)
        assert s["global_compilation"]["dialogue"]["user_values"]["p0.s0"]["value"] == name
        if index and reject_confirmation:
            assert not dialogue.export_selection(s)[2]
            assert condition["key"] not in s["global_compilation"]["dialogue"]["answers"]
        else:
            assert "p0.s0" in dialogue.export_selection(s)[2]
            assert s["global_compilation"]["dialogue"]["answers"][condition["key"]][
                "user_quote"] == message
