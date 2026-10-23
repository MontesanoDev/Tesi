"""Persistent selection, reopened/stale sessions and bound USER replies."""

import json
from copy import deepcopy
from io import BytesIO
from types import SimpleNamespace

import pytest
from docx import Document
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_sessions import source
from test_compilation_value_completeness import prepared

from app import compilation_global_sessions as adapter
from app.compilation_global_dialogue import apply_replies
from app.db import connection

__all__ = ["api", "provider"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def start(api, monkeypatch, value="123", *, style="table",
                label="Numero e data d'iscrizione"):
    layout, sources, raw, _, cid = prepared(label=label, value=value, style=style)
    upload = await api.post("/api/projects/alpha/forms", files={
        "file": ("modulo.docx", layout.original)})
    await source(api, sources[0]["content"], name="registri.txt")

    async def proposal(client, settings, body, timeout, **kwargs):
        inp = json.loads(body["messages"][1]["content"])
        proof = next(s for s in inp["sources"] if sources[0]["content"] in s["content"])
        response = deepcopy(raw)
        response["facts"]["f"]["evidence"][0]["chunk_id"] = proof["chunk_id"]
        return json.dumps(response), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", proposal)
    session = (await api.post(BASE, json={"form_id": upload.json()["id"], "engine": "global",
                                         "start_in_chat": True})).json()
    return await resolve(api, session), cid


@pytest.mark.anyio
@pytest.mark.parametrize("style", ["table", "previous", "header", "inline", "formtext"])
@pytest.mark.parametrize("value,expected", [("123", "INCOMPLETE"),
                                          ("n.123 del 14/03/2019", "COMPLETE")])
async def test_reopened_session_and_actual_export_keep_completeness_gate(
    api, provider, monkeypatch, style, value, expected,
):
    session, cid = await start(api, monkeypatch, value, style=style)
    reopened = (await api.get(f"{BASE}/{session['id']}")).json()
    item = next(f for f in reopened["global_compilation"]["fields"] if f["candidate_id"] == cid)
    assert item["selectable"] is (expected == "COMPLETE")
    if expected != "COMPLETE":
        assert item["value_completeness"]["result"] == expected
    response = await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": session["version"], "candidate_ids": [cid], "allow_unresolved": True,
        "user_quote": "Genera la bozza parziale"})
    if expected == "COMPLETE":
        assert response.status_code == 200, response.text
        paths = response.json()["last_generation"]["downloads"]
        report = (await api.get(paths["report"])).json()
        assert report["written_field_count"] == 1
        written = Document(BytesIO((await api.get(paths["docx"])).content))
        assert value in written.element.xml
    else:
        assert response.status_code == 409, response.text
        assert "Completezza" in response.json()["detail"]
        assert (await api.get(f"{BASE}/{session['id']}")).json()["last_generation"] is None


@pytest.mark.anyio
@pytest.mark.parametrize("as_user", [False, True])
async def test_fresh_export_rejects_forged_cached_complete_verdict_and_saved_selection(
    api, provider, monkeypatch, as_user,
):
    session, cid = await start(api, monkeypatch)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        data = state["global_compilation"]
        data["audit"]["value_completeness"][cid]["result"] = "COMPLETE"
        data["dialogue"] = {"phase": "READY", "reviewed_candidate_ids": [cid]}
        if as_user:
            data["dialogue"]["user_values"] = {cid: {"value": "123", "user_quote": "123",
                                                       "provenance": "USER"}}
        db.execute("UPDATE compilation_sessions SET state_json=? WHERE id=?",
                   (json.dumps(state), row["id"]))
    response = await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": session["version"], "candidate_ids": [] if as_user else [cid],
        "user_candidate_ids": [cid] if as_user else [], "allow_unresolved": True,
        "user_quote": "Confermo ed esporta"})
    assert response.status_code == 409, response.text
    assert "Completezza" in response.json()["detail"]
    assert (await api.get(f"{BASE}/{session['id']}")).json()["last_generation"] is None


@pytest.mark.anyio
async def test_old_cached_session_without_check_is_unknown_and_not_upgraded(
    api, provider, monkeypatch,
):
    session, cid = await start(api, monkeypatch)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"]["audit"].pop("value_completeness")
        db.execute("UPDATE compilation_sessions SET state_json=? WHERE id=?",
                   (json.dumps(state), row["id"]))
    reopened = (await api.get(f"{BASE}/{session['id']}")).json()
    assert reopened["global_compilation"]["fields"][0]["value_completeness"]["result"] == "UNKNOWN"
    with connection() as db:
        _, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        assert "value_completeness" not in state["global_compilation"]["audit"]


@pytest.mark.anyio
@pytest.mark.parametrize("reply_value", ["123", "123 del 14/03/2019"])
async def test_bound_user_reply_cannot_invent_missing_source_components(
    api, provider, monkeypatch, reply_value,
):
    session, cid = await start(api, monkeypatch)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"]["dialogue"] = {"phase": "READY", "question": {
            "message": "Quali sono gli estremi?", "slots": [{"slot": 1, "key": "value:" + cid,
                "kind": "value", "label": "Numero e data", "field_ids": [cid]}]}}
        db.execute("UPDATE compilation_sessions SET state_json=? WHERE id=?",
                   (json.dumps(state), row["id"]))
    reply = SimpleNamespace(slot=1, action="VALUE", value=reply_value, normalized_value=None,
                            user_quote=reply_value, selected_options=None)
    after, errors = apply_replies("alpha", session["id"], session["version"], [reply], reply_value)
    assert errors == [1]
    assert not after["global_compilation"]["dialogue"]["user_values"]


@pytest.mark.anyio
async def test_complete_user_procedural_place_and_date_remain_writable(
    api, provider, monkeypatch,
):
    session, cid = await start(api, monkeypatch, "Bari", label="Luogo e data")
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        state["global_compilation"]["dialogue"] = {"phase": "READY", "question": {
            "message": "Indica luogo e data", "slots": [{"slot": 1, "key": "value:" + cid,
                "kind": "value", "label": "Luogo e data", "field_ids": [cid]}]}}
        db.execute("UPDATE compilation_sessions SET state_json=? WHERE id=?",
                   (json.dumps(state), row["id"]))
    text = "Bari, 21 ottobre 2026"
    reply = SimpleNamespace(slot=1, action="VALUE", value=text, normalized_value=None,
                            user_quote=text, selected_options=None)
    after, errors = apply_replies("alpha", session["id"], session["version"], [reply], text)
    assert not errors
    response = await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": after["version"], "candidate_ids": [], "user_candidate_ids": [cid],
        "allow_unresolved": True, "user_quote": "Esporta la bozza parziale"})
    assert response.status_code == 200, response.text
    paths = response.json()["last_generation"]["downloads"]
    report = (await api.get(paths["report"])).json()
    assert report["written_field_count"] == 1 and report["fields"][0]["provenance"] == "USER"


@pytest.mark.anyio
async def test_ambiguous_requirement_stays_unknown_in_persistence_and_export(
    api, provider, monkeypatch,
):
    session, cid = await start(api, monkeypatch, "123", label="Numero/data d'iscrizione")
    item = session["global_compilation"]["fields"][0]
    assert item["value_completeness"]["result"] == "UNKNOWN" and not item["selectable"]
    response = await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": session["version"], "candidate_ids": [cid], "allow_unresolved": True,
        "user_quote": "Confermo tutto, esporta"})
    assert response.status_code == 409
    assert "Completezza" in response.json()["detail"]
