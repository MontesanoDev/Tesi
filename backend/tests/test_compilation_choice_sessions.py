"""Real API/persistence/export with simulated transports, not model benchmarks."""

import copy
import json

import pytest
from test_compilation_choices import choice_case as generic_case
from test_compilation_global_sessions import BASE, resolve
from test_compilation_global_sessions import api as global_api
from test_compilation_global_sessions import provider as global_provider
from test_compilation_sessions import source
from test_docx_checkboxes import states

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.db import connection

api, provider, choice_case = global_api, global_provider, generic_case


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def start_choice(api, choice_case, monkeypatch, *, automatic=True):
    uploaded = await api.post("/api/projects/alpha/forms", files={
        "file": ("scelte.docx", choice_case[0].original)})
    assert uploaded.status_code == 201
    await source(api, choice_case[1][0]["content"])
    calls = []

    async def request(client, settings, body, timeout, **kwargs):
        data = json.loads(body["messages"][1]["content"])
        calls.append(data)
        payload = copy.deepcopy(choice_case[2])
        assert data["schema_output"]["properties"]["version"]["const"] == 11
        if automatic:
            chunk = next(s["chunk_id"] for s in data["sources"] if "Vega" in s["content"])
            for fact in payload["facts"].values():
                for proof in fact["evidence"]:
                    proof["chunk_id"] = chunk
        else:
            payload["fields"], payload["facts"] = {}, {}
        return json.dumps(payload), "simulated", {}

    async def summarize(client, settings, body, timeout, **kwargs):
        data = json.loads(body["messages"][1]["content"])
        return json.dumps({**({"message": "Ho verificato i dati disponibili e le scelte."}
                             if data["conversation_stage"] == "initial" else {}),
                           "questions": [{"slot": q["slot"],
                                          **({"confirmation": "questa situazione si applica"}
                                             if q["kind"] == "applicability" else {"question":
                                             "Quale tipologia vuoi indicare tra le alternative?"})}
                                         for q in data["question_pool"][:3]]}), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", request)
    monkeypatch.setattr(dialogue, "request_model_content", summarize)
    result = await api.post(BASE, json={"form_id": uploaded.json()["id"], "engine": "global",
                                       "start_in_chat": True})
    assert result.status_code == 201
    return await resolve(api, result.json()), calls


@pytest.mark.anyio
async def test_source_choices_persist_and_export_with_scope_and_original(api, provider, choice_case,
                                                                       monkeypatch):
    s, calls = await start_choice(api, choice_case, monkeypatch)
    assert s["global_compilation"]["proposal_count"] == 2
    assert len(calls) == 1 and s["summary"]["resolved"] == 0
    assert s == (await api.get(f"{BASE}/{s['id']}")).json()
    ids, conditions, users = dialogue.export_selection(s)
    assert set(ids) == {"p2.cb0", "p3.cb0"} and not conditions and not users
    result = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ids, "allow_unresolved": True})
    assert result.status_code == 200, result.text
    generated = result.json()["last_generation"]["downloads"]
    docx = (await api.get(generated["docx"])).content
    assert states(docx) == {"p3.cb0": True, "p4.cb0": False}
    assert (await api.get(generated["template"])).content == choice_case[0].original
    report = (await api.get(generated["report"])).json()
    assert report["written_field_count"] == 2 and report["resolved"] == 0
    assert all(f["provenance"] == "SOURCE" for f in report["fields"])
    assert all(f["source_evidence"][0]["scope"] == "global" for f in report["fields"])
    assert all(f["source_evidence"][0]["category"] == "company" for f in report["fields"])
    assert report["checkbox_values"] == {"p2.cb0": True, "p3.cb0": False}


@pytest.mark.anyio
async def test_choice_without_source_user_reply_targets_group_and_export_is_user(
    api, provider, choice_case, monkeypatch,
):
    from app import intents

    s, calls = await start_choice(api, choice_case, monkeypatch, automatic=False)
    slot = s["chat"]["question"]["slots"][0]
    assert slot["kind"] == "choice" and slot["field_ids"] == ["p2.cb0", "p3.cb0"]
    message = "Per questa domanda partecipo come professionista autonomo."
    checks = []

    async def route(client, settings, body, timeout, **kwargs):
        if kwargs["response_schema"]["title"] == "ReplyScopeChecks":
            data = json.loads(body["messages"][1]["content"])
            checks.append(data)
            assert data["proposals"][0]["selected_options"] == [2]
            return json.dumps({"checks": [{"slot": 1, "result": "SUPPORTED"}]}), "simulated", {}
        return json.dumps({"intent": "answer_fields", "answer": "", "queries": [],
                           "target": "form", "replies": [{"slot": 1, "action": "VALUE",
                           "value": message, "user_quote": message,
                           "selected_options": [2]}]}), "simulated", {}

    monkeypatch.setattr(intents, "request_model_content", route)
    response = await api.post("/api/projects/alpha/answer", json={"question": message,
        "document_id": s["form_id"], "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"]})
    assert response.status_code == 200, response.text
    s = sessions.get_session("alpha", s["id"])
    assert s["chat"]["auto_continue"] and len(checks) == 1
    s = await resolve(api, s)
    assert len(calls) == 1
    with connection() as db:
        data = json.loads(sessions._row(db, "alpha", s["id"])["state_json"])["global_compilation"]
    users = data["dialogue"]["user_values"]
    assert users["p3.cb0"]["value"] is True and users["p2.cb0"]["value"] is False
    assert "p4.s0" not in users
    ids, conditions, user_ids = dialogue.export_selection(s)
    result = await api.post(f"{BASE}/{s['id']}/global-draft", json={"version": s["version"],
        "candidate_ids": ids, "confirmed_condition_ids": conditions, "user_candidate_ids": user_ids,
        "allow_unresolved": True})
    assert result.status_code == 200, result.text
    generated = result.json()["last_generation"]["downloads"]
    assert states((await api.get(generated["docx"])).content) == {"p3.cb0": False, "p4.cb0": True}
    report = (await api.get(generated["report"])).json()
    assert all(f["provenance"] == "USER" and not f["source_evidence"] for f in report["fields"])


@pytest.mark.anyio
@pytest.mark.parametrize("action", ["UNKNOWN", "SKIP", "CLARIFY"])
async def test_defer_or_ambiguous_choice_never_changes_boolean_values(
    api, provider, choice_case, monkeypatch, action,
):
    s, _ = await start_choice(api, choice_case, monkeypatch, automatic=False)
    s, errors = dialogue.apply_replies("alpha", s["id"], s["version"], [ClarificationReply(
        slot=1, action=action, user_quote="Una risposta incerta")], "Una risposta incerta")
    assert bool(errors) == (action == "CLARIFY")
    with connection() as db:
        data = json.loads(sessions._row(db, "alpha", s["id"])["state_json"])["global_compilation"]
    assert not data["dialogue"].get("user_values")
    if action != "CLARIFY":
        s = await resolve(api, s)
        assert s["chat"]["question"]["kind"] == "generate"


@pytest.mark.anyio
async def test_pause_resume_preserve_group_and_wrong_project_cannot_read_or_export(
    api, provider, choice_case, monkeypatch,
):
    s, _ = await start_choice(api, choice_case, monkeypatch, automatic=False)
    before = s["chat"]["question"]
    paused = adapter.control_session("alpha", s["id"], s["version"], "pause")
    assert paused["chat"]["question"] is None
    resumed = adapter.control_session("alpha", s["id"], paused["version"], "resume")
    assert resumed["id"] == s["id"] and resumed["chat"]["question"] == before
    assert (await api.get(f"/api/projects/beta/compilation-sessions/{s['id']}")).status_code == 404
    assert (await api.post(f"/api/projects/beta/compilation-sessions/{s['id']}/global-draft",
        json={"version": resumed["version"], "allow_unresolved": True,
              "candidate_ids": ["p2.cb0"]})).status_code == 404


@pytest.mark.anyio
async def test_changed_source_blocks_checkbox_export(api, provider, choice_case, monkeypatch):
    s, _ = await start_choice(api, choice_case, monkeypatch)
    with connection() as db:
        db.execute("UPDATE global_document_chunks SET content=content || ' changed'")
    result = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ["p2.cb0"], "allow_unresolved": True})
    assert result.status_code == 409 and sessions.get_session("alpha", s["id"])[
        "last_generation"] is None
