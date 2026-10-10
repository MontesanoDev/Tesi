"""Explicit finish is not a clarification answer, and partial export keeps all gates."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from test_compilation_clarifications import answer, checkpoint, reply
from test_compilation_condition_reuse import ROOT, WITH, WITHOUT, branch_field
from test_compilation_controls import current
from test_compilation_conversation import anyio_backend as anyio_backend
from test_compilation_conversation import chat as chat
from test_compilation_conversation import mutate_state, say, start, step
from test_compilation_sessions import docx, simulate, source

from app import compilation_sessions as sessions
from app.compilation_chat import ChatControl
from app.intents import ChatDecision, route_compilation_control


def branches(s, conditions):
    for index, (field, condition) in enumerate(zip(s["fields"], conditions, strict=True)):
        reviewed = branch_field(field["id"], condition, section=f"section-{index}",
                                entity="person" if index % 2 else "company")
        reviewed["form_evidence"] = field["form_evidence"]
        field.update(reviewed)
    s["chat_workflow"]["active_clarifications"] = []
    s["status"] = "WAITING_FOR_USER"


@pytest.mark.anyio
async def test_literal_studio_denial_applies_once_to_repeated_cells_and_children(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch, labels=("Nome", "Cognome", "Referente", "Sede"))
    mutate_state(s, lambda s: branches(s, [ROOT, "STUDIO ASSOCIATO", WITH, WITHOUT]))
    s = await current(chat[0], s)
    assert len(s["chat"]["question"]["slots"]) == 1
    r = await say(chat, s, "non siamo uno studio associato", answer(
        reply(1, "CONDITION_FALSE", quote="non siamo uno studio associato"),
    ))
    assert r.status_code == 200, r.text
    s = await current(chat[0], s)
    assert s["summary"]["not_applicable"] == 4
    assert s["chat"]["question"]["kind"] == "generate"
    resumed = sessions.chat_control("alpha", s["id"], s["version"],
                                    ChatControl(kind="resume", user_quote="riprendi"))
    assert resumed["summary"]["not_applicable"] == 4
    assert not resumed["chat"]["question"]["field_ids"]


@pytest.mark.anyio
async def test_collective_no_applies_to_exactly_two_distinct_conditions(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch, labels=("Nome", "Cognome"))
    mutate_state(s, lambda s: branches(s, ["studio associato", "società di professionisti"]))
    s = await current(chat[0], s)
    r = await say(chat, s, "no a entrambe", answer())
    assert r.status_code == 200, r.text
    s = await current(chat[0], s)
    assert s["summary"]["not_applicable"] == 2
    assert all(f["applicability"]["provenance"] == "USER" for f in s["fields"])


@pytest.mark.anyio
async def test_collective_denial_does_not_guess_between_three_conditions(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch)
    mutate_state(s, lambda s: branches(s, ["studio associato", "società di professionisti",
                                          "consorzio stabile"]))
    s = await current(chat[0], s)
    r = await say(chat, s, "no a entrambe", answer(
        reply(1, "CONDITION_FALSE", quote="no a entrambe"),
        reply(2, "CONDITION_FALSE", quote="no a entrambe"),
    ))
    assert r.status_code == 200
    s = await current(chat[0], s)
    assert s["summary"]["not_applicable"] == 0
    assert all(not f.get("applicability") for f in s["fields"])


@pytest.mark.anyio
async def test_non_so_never_becomes_a_denial_even_if_model_proposes_it(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch, labels=("Nome", "Cognome"))
    mutate_state(s, lambda s: branches(s, [ROOT, "STUDIO ASSOCIATO"]))
    s = await current(chat[0], s)
    r = await say(chat, s, "non so", answer(reply(1, "CONDITION_FALSE", quote="non so")))
    assert r.status_code == 200
    s = await current(chat[0], s)
    assert s["summary"]["not_applicable"] == 0
    assert s["chat"]["deferred"] == 2
    assert all(not f.get("applicability") for f in s["fields"])


@pytest.mark.anyio
async def test_finish_exports_partial_without_planning_questions_or_changing_source(
    chat, monkeypatch,
):
    client, _, requests, _ = chat
    s, _ = await start(chat, content=docx(("Denominazione sociale", "Referente", "Data avvio")))
    await source(client, "Denominazione sociale: Aurora S.r.l.")
    simulate(monkeypatch, {s["fields"][0]["id"]: ["Aurora S.r.l."]})
    s = await step(client, s)
    verified = deepcopy(s["fields"][0])
    previous_calls = len(requests)
    r = await client.post('/api/projects/alpha/answer', json={
        "question": "no, finisci la compilazione", "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"],
    })
    assert r.status_code == 200, r.text
    assert len(requests) == previous_calls
    assert "bozza parziale" in r.json()["answer"] and "?" not in r.json()["answer"]
    s = await current(client, s)
    assert s["status"] == "GENERATED" and s["status"] != "READY"
    assert s["fields"][0] == verified
    assert s["chat"]["question"] is None and not s["chat"]["auto_continue"]
    assert s["chat"]["finish_requested"]
    generation = (await client.get(
        f'/api/projects/alpha/document-compilations/{s["last_generation"]["id"]}',
    )).json()
    assert generation["report"]["written_field_count"] == 1
    assert not generation["report"]["ready_for_submission"]
    assert len(generation["report"]["open_issues"]) == 2
    downloaded = await client.get(s["last_generation"]["downloads"]["docx"])
    assert downloaded.status_code == 200 and downloaded.content.startswith(b"PK")
    refreshed = await current(client, s)
    assert refreshed["chat"]["question"] is None and refreshed["fields"] == s["fields"]
    resumed = sessions.chat_control("alpha", s["id"], s["version"],
                                    ChatControl(kind="resume", user_quote="riprendi"))
    assert resumed["status"] == "WAITING_FOR_USER"
    assert resumed["chat"]["question"] and not resumed["chat"]["finish_requested"]
    assert resumed["fields"][0] == verified


@pytest.mark.anyio
async def test_finish_cannot_bypass_revision_or_active_lease(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch)
    stale = await chat[0].post('/api/projects/alpha/answer', json={
        "question": "no, finisci la compilazione", "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"] - 1,
    })
    assert stale.status_code == 409
    def busy(s):
        lease = (datetime.now(UTC) + timedelta(minutes=5)).isoformat()
        s.update(status="ANALYZING", lease_until=lease)
    mutate_state(s, busy)
    r = await chat[0].post('/api/projects/alpha/answer', json={
        "question": "esporta una bozza parziale", "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"],
    })
    assert r.status_code == 409
    s = await current(chat[0], s)
    assert s["last_generation"] is None and not s["chat"]["finish_requested"]


@pytest.mark.anyio
async def test_finish_keeps_validation_gates_and_stops_even_if_export_fails(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch, labels=("Recapito", "Referente"))
    def unsupported(s):
        s["fields"][0].update(status="RESOLVED", value="Inventato", provenance="SOURCE",
                              source_evidence=[])
    mutate_state(s, unsupported)
    s = await current(chat[0], s)
    r = await chat[0].post('/api/projects/alpha/answer', json={
        "question": "no, finisci la compilazione", "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"],
    })
    assert r.status_code == 200 and r.json()["compilation"]["action"] == "paused"
    assert "blocca la generazione" in r.json()["answer"] and "?" not in r.json()["answer"]
    s = await current(chat[0], s)
    assert s["last_generation"] is None
    assert s["chat"]["question"] is None and not s["chat"]["auto_continue"]
    assert s["fields"][0]["value"] == "Inventato"  # Gate rejects; never silently writes/edits.


@pytest.mark.parametrize("text", ["continua la compilazione", "prosegui la compilazione",
                                 "non finisci la compilazione", "come finisci la compilazione?",
                                 "il campo contiene: finisci la compilazione"])
def test_finish_guard_does_not_intercept_continuation_negations_or_document_questions(text):
    initial = ChatDecision(action="reply", answer="test", queries=[], target="source")
    s = {"fields": [], "status": "WAITING_FOR_USER", "lease_until": None,
         "chat_workflow": {"steps": 0, "user_paused": False}}
    decision = route_compilation_control(initial, text, s)
    assert not decision.control or decision.control.kind == "resume"


@pytest.mark.anyio
async def test_continue_at_group_checkpoint_does_not_answer_conditions_or_export(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch, labels=("Nome", "Cognome"))
    mutate_state(s, lambda s: branches(s, [ROOT, "STUDIO ASSOCIATO"]))
    s = await current(chat[0], s)
    before = deepcopy(s["fields"])
    r = await say(chat, s, "continua la compilazione", answer(
        reply(1, "CONDITION_FALSE", quote="continua la compilazione"),
    ))
    assert r.status_code == 200, r.text
    s = await current(chat[0], s)
    assert r.json()["compilation"]["action"] == "resumed"
    assert s["fields"] == before and not s["last_generation"]


@pytest.mark.anyio
async def test_semantic_finish_paraphrase_is_distinct_from_a_group_answer(chat, monkeypatch):
    s = await checkpoint(chat, monkeypatch)
    r = await say(chat, s, "Mi basta così, crea una bozza con quello che hai", {"action": "FINISH"})
    assert r.status_code == 200, r.text
    s = await current(chat[0], s)
    assert s["status"] == "GENERATED" and not s["chat"]["question"]
    assert len(s["open_issues"]) == 3
