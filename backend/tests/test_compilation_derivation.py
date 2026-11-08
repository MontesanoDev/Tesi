"""Derived-state coherence after USER replies (derivation_revision 1); provider simulated.

The stored audit must always equal the audit re-derived from the immutable model output and the
current receipts, so the export selection and the final veto agree. A deferral never authorizes.
"""

import json

import pytest
from test_compilation_global_sessions import BASE, api, provider, resolve, start
from test_compilation_selected_person import NAME, case
from test_compilation_sessions import source

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.db import connection
from app.repository import save_conversation_turn

__all__ = ["api", "provider"]
START = f"Compila la domanda. Il firmatario scelto per questa domanda è {NAME}."


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def signer_session(api, monkeypatch, *, derivation):
    monkeypatch.setenv("MAPI_DERIVATION_REVISION", "1" if derivation else "0")
    _, layout, sources = case()
    uploaded = await api.post("/api/projects/alpha/forms", files={
        "file": ("modulo.docx", layout.original)})
    await source(api, sources[0]["content"], name="profili.md")

    async def proposal(client, settings, body, timeout, **kwargs):
        model_input = json.loads(body["messages"][1]["content"])
        chunk = next(s["chunk_id"] for s in model_input["sources"]
                     if "- **Società:** Aurora Servizi S.r.l." in s["content"])
        return json.dumps({"version": 12, "facts": {"company": {
            "subject": "Aurora Servizi S.r.l.", "entity": "company", "aspect": "identity",
            "property": "denominazione", "value": "Aurora Servizi S.r.l.",
            "evidence": [{"chunk_id": chunk, "quote": "- **Società:** Aurora Servizi S.r.l."}]}},
            "fields": {"p2.s1": {"label": "Operatore economico", "kind": "data",
                "disposition": "value", "conditions": [], "property": "denominazione",
                "fact_id": "company", "form": {"paragraph_id": "paragraph:2",
                    "quote": "operatore economico [[p2.s1]]"}}}, "bindings": {},
            "conditions": {}, "choice_groups": {}, "coverage": [], "clarifications": {
                "p0.s0": {"label": "Il sottoscritto", "reason": "Scelta della pratica",
                          "form": {"paragraph_id": "paragraph:0",
                                   "quote": "Il sottoscritto [[p0.s0]]"}}}}), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", proposal)
    s = (await api.post(BASE, json={"form_id": uploaded.json()["id"], "engine": "global",
                                  "start_in_chat": True})).json()
    save_conversation_turn(s["conversation_id"], {
        "question": START, "answer": "Avvio della compilazione", "generation_status": "direct",
        "compilation": {"session_id": s["id"], "action": "start"}})
    return await resolve(api, s)


def stored(s):
    with connection() as db:
        row = sessions._row(db, "alpha", s["id"])
        state = json.loads(row["state_json"])
        return row, state, adapter.refreshed_audit(db, row, state)


def reuse_ids(audit):
    return sorted(f["candidate_id"] for f in audit["fields"] if f.get("source_reuse"))


def reask(s, slot):
    """The same slot offered again (a later question): the new receipt replaces the old one."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = adapter._row_state(db, "alpha", s["id"], s["version"])
        dialogue_state = state["global_compilation"]["dialogue"]
        dialogue_state.update(phase="READY", error=None, question={
            "kind": "clarifications", "field_ids": [], "slots": [slot], "message": "?"})
        return sessions.save_state(db, row, state, "test_reask")


def reply(s, action, quote, value=None, slot=1):
    return dialogue.apply_replies("alpha", s["id"], s["version"], [
        ClarificationReply(slot=slot, action=action, value=value, user_quote=quote)], quote)


async def export(api, s):
    s = await resolve(api, s)
    ids, conditions, users = dialogue.export_selection(s)
    return await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ids, "user_candidate_ids": users,
        "confirmed_condition_ids": conditions, "allow_unresolved": True,
        "user_quote": "Genera la bozza parziale"}), ids


@pytest.mark.anyio
@pytest.mark.parametrize("derivation", [False, True])
async def test_deferral_of_a_start_selection_keeps_audit_and_export_coherent(
    api, provider, monkeypatch, derivation,
):
    """minervino-1: a SKIP on the signer slot after a start-message selection."""
    s = await signer_session(api, monkeypatch, derivation=derivation)
    _, state, fresh = stored(s)
    assert reuse_ids(state["global_compilation"]["audit"]) == reuse_ids(fresh) != []
    slot = s["chat"]["question"]["slots"][0]
    assert slot["field_ids"] == ["p0.s0"]
    s, errors = reply(s, "SKIP", f"Il firmatario scelto per questa domanda è {NAME}.")
    assert not errors
    _, state, fresh = stored(s)
    assert reuse_ids(fresh) == []  # A deferral never keeps or authorizes the reuse.
    response, ids = await export(api, s)
    if derivation:
        assert state["global_compilation"]["audit"] == fresh
        assert response.status_code == 200, response.text
        assert not set(ids) & {"p0.s0", "p0.s1", "p1.s0"}
    else:  # Reproduces the defect: stale derived state, final veto 409 (behaviour unchanged).
        assert reuse_ids(state["global_compilation"]["audit"]) != []
        assert response.status_code == 409


@pytest.mark.anyio
async def test_confirmation_revocation_and_change_follow_the_current_receipt(
    api, provider, monkeypatch,
):
    s = await signer_session(api, monkeypatch, derivation=True)
    slot = s["chat"]["question"]["slots"][0]
    s, errors = reply(s, "VALUE", NAME, value=NAME)  # Confirmation.
    assert not errors
    _, state, fresh = stored(s)
    assert state["global_compilation"]["audit"] == fresh and reuse_ids(fresh)
    s, errors = reply(reask(s, slot), "REFUSE", "Non confermo questo firmatario.")  # Revocation.
    assert not errors
    _, state, fresh = stored(s)
    assert state["global_compilation"]["audit"] == fresh and reuse_ids(fresh) == []
    s, errors = reply(reask(s, slot), "VALUE", NAME, value=NAME)  # Changed answer.
    assert not errors
    _, state, fresh = stored(s)
    assert state["global_compilation"]["audit"] == fresh and reuse_ids(fresh)
    response, _ = await export(api, s)
    assert response.status_code == 200, response.text


@pytest.mark.anyio
async def test_reply_recorded_on_a_different_slot_leaves_the_selection_unchanged(
    api, provider, monkeypatch,
):
    s = await signer_session(api, monkeypatch, derivation=True)
    _, before, _ = stored(s)
    other = {"slot": 1, "key": "field:p1.s3", "kind": "value", "field_ids": ["p1.s3"],
             "label": "C.F.", "condition": "", "context": "C.F.", "alternatives": [],
             "impact": 1, "question": "Codice fiscale?"}
    s, errors = reply(reask(s, other), "SKIP", f"Il firmatario scelto è {NAME}.")
    assert not errors
    _, state, fresh = stored(s)
    assert state["global_compilation"]["audit"] == fresh
    assert reuse_ids(fresh) == reuse_ids(before["global_compilation"]["audit"]) != []
    assert "field:p0.s0" not in state["global_compilation"]["dialogue"]["answers"]
    response, _ = await export(api, s)
    assert response.status_code == 200, response.text


def test_derivation_defaults_to_enabled_independently_of_p3(monkeypatch):
    from test_compilation_sessions import docx

    from app.docx_templates import inspect_docx

    layout = inspect_docx(docx())
    for variable in ("MAPI_DERIVATION_REVISION", "MAPI_GENERATION_REVISION",
                     "MAPI_DIALOGUE_REVISION"):
        monkeypatch.delenv(variable, raising=False)
    state = adapter.initial_state(layout)
    assert {key: value for key, value in state.items() if key.endswith("revision")} == {
        "backend_revision": 13, "option_authorization_revision": 1,
        "attribution_safety_revision": 1, "derivation_revision": 1,
    }
    monkeypatch.setenv("MAPI_DERIVATION_REVISION", "0")
    previous = adapter.initial_state(layout)
    assert previous == {key: value for key, value in state.items()
                        if key != "derivation_revision"}
    monkeypatch.setenv("MAPI_DERIVATION_REVISION", "1")
    assert adapter.initial_state(layout) == state


@pytest.mark.anyio
@pytest.mark.parametrize("created_with_fix", [False, True])
async def test_derivation_revision_is_owned_by_the_persisted_session(
    api, provider, monkeypatch, created_with_fix,
):
    """The default promotion does not upgrade old sessions or downgrade new ones."""
    if created_with_fix:
        monkeypatch.delenv("MAPI_DERIVATION_REVISION", raising=False)
    else:
        monkeypatch.setenv("MAPI_DERIVATION_REVISION", "0")
    s = await start(api)
    expected = 1 if created_with_fix else None
    assert s["global_compilation"].get("derivation_revision") == expected
    # Simulate loading the saved session after the runtime's default changes.
    if created_with_fix:
        monkeypatch.setenv("MAPI_DERIVATION_REVISION", "0")
    else:
        monkeypatch.delenv("MAPI_DERIVATION_REVISION")
    s = await resolve(api, s)
    assert s["global_compilation"].get("derivation_revision") == expected
    _, state, fresh = stored(s)
    data = state["global_compilation"]
    assert data.get("derivation_revision") == expected
    assert data["audit"] == fresh
    assert "dialogue_revision" not in data and "generation_revision" not in data
