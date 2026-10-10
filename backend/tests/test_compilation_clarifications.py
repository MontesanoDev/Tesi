"""Grouped checkpoints: real isolated persistence, simulated semantic decisions."""

import json

import pytest
from test_compilation_controls import current
from test_compilation_conversation import chat as chat
from test_compilation_conversation import mutate_state, say, start, step
from test_compilation_sessions import docx, simulate, source

from app.compilation_session_models import CandidateMeanings
from app.generation import GenerationError


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def checkpoint(chat, monkeypatch, labels=("Recapito", "Referente", "Data avvio")):
    state, _ = await start(chat, content=docx(labels))
    simulate(monkeypatch)
    state = await step(chat[0], state)
    assert state["chat"]["question"]["kind"] == "clarifications"
    return state


@pytest.mark.anyio
async def test_automatic_question_remains_in_history_after_answer_and_pause(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    client = chat[0]
    url = f"/api/projects/alpha/conversations/{state['conversation_id']}"
    question = state["chat"]["question"]["message"]
    history = (await client.get(url)).json()["turns"]
    assert history[0]["answer"] == question
    await say(chat, state, "Il referente è Anna Bianchi.", answer(
        reply(2, value="Anna Bianchi", quote="Il referente è Anna Bianchi."),
    ))
    state = await current(client, state)
    await say(chat, state, "basta", {"action": "PAUSE"})
    history = (await client.get(url)).json()["turns"]
    assert len(history) == 3
    assert history[0]["answer"] == question
    assert "Anna Bianchi" not in history[0]["answer"]
    assert "Ho registrato le tue risposte" in history[1]["answer"]
    assert "pausa" in history[2]["answer"]


@pytest.mark.anyio
@pytest.mark.parametrize("message", [
    "spiegati meglio", "Non ho capito cosa mi stai chiedendo", "Puoi riformulare il secondo punto?",
])
async def test_explanation_keeps_checkpoint_fields_budget_and_history(chat, monkeypatch, message):
    state = await checkpoint(chat, monkeypatch)
    explanation = "Per referente intendo la persona da indicare nel modulo come contatto."
    before_requests = len(chat[2])
    response = await say(chat, state, message, {
        "action": "reply", "answer": explanation, "queries": [], "target": "source",
    })
    assert response.status_code == 200, response.text
    assert response.json()["answer"] == explanation
    assert response.json()["compilation"] is None
    assert await current(chat[0], state) == state
    assert len(chat[2]) == before_requests + 1
    prompt = chat[2][-1]["messages"]
    assert "explain" in prompt[0]["content"]
    assert state["chat"]["question"]["message"] in json.loads(
        prompt[1]["content"].split("CRONOLOGIA NON FATTUALE (JSON):\n", 1)[1]
        .split("\n\nMODULI DEL PROGETTO", 1)[0]
    )[0]["answer"]
    history = (await chat[0].get(
        f"/api/projects/alpha/conversations/{state['conversation_id']}",
    )).json()["turns"]
    assert history[0]["answer"] == state["chat"]["question"]["message"]
    assert history[1]["answer"] == explanation


def answer(*replies):
    return {"intent": "answer_fields", "answer": "", "queries": [], "target": "form",
            "replies": list(replies)}


def reply(slot, action="VALUE", value=None, quote=None):
    return {"slot": slot, "action": action, "value": value,
            "user_quote": quote if quote is not None else value}


@pytest.mark.anyio
async def test_missing_fields_accumulate_while_remaining_candidates_are_analyzed(chat, monkeypatch):
    client = chat[0]
    state, _ = await start(chat, content=docx(tuple(f"Dato {i}" for i in range(17))))
    simulate(monkeypatch)
    state = await step(client, state)
    assert state["summary"]["missing"] == 12 and state["summary"]["pending"] == 5
    assert state["status"] == "CREATED" and state["chat"]["question"] is None
    assert state["chat"]["auto_continue"]
    assert len(state["chat_workflow"]["pending_clarifications"]) == 12
    state = await step(client, state)
    assert state["summary"]["missing"] == 17
    assert state["status"] == "WAITING_FOR_USER" and not state["chat"]["auto_continue"]
    assert len(state["chat"]["question"]["slots"]) == 4
    assert state["chat"]["metrics"]["user_turns"] == 0


@pytest.mark.anyio
async def test_uninterpreted_pending_candidates_are_never_user_questions(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Dato sconosciuto",)))
    simulate(monkeypatch, classify_hook=lambda fields: CandidateMeanings(fields=[]))
    state = await step(chat[0], state)
    assert state["chat"]["auto_continue"] and state["chat"]["question"] is None
    state = await step(chat[0], state)
    assert not state["chat"]["auto_continue"]
    assert not state["chat"]["question"] or not state["chat"]["question"]["field_ids"]
    assert state["fields"][0]["search"]["status"] == "not_searched"


@pytest.mark.anyio
async def test_one_reply_updates_multiple_slots_and_preserves_user_provenance(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    result = await say(chat, state, "1. 055123456; 2. Anna Bianchi; 3. 12 giugno 2014", answer(
        reply(1, value="055123456"), reply(2, value="Anna Bianchi"),
        reply(3, value="12 giugno 2014"),
    ))
    assert result.status_code == 200, result.text
    state = await current(chat[0], state)
    assert state["status"] == "READY" and state["summary"]["user_provided"] == 3
    assert [f["value"] for f in state["fields"]] == ["055123456", "Anna Bianchi", "12/06/2014"]
    assert all(f["provenance"] == "USER" and not f["source_evidence"] for f in state["fields"])
    assert state["chat"]["metrics"]["user_turns"] == 1


@pytest.mark.anyio
async def test_partial_answer_keeps_only_unanswered_slots_active(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    before = state["fields"]
    result = await say(chat, state, "Il referente è Anna Bianchi.", answer(
        reply(2, value="Anna Bianchi", quote="Il referente è Anna Bianchi."),
    ))
    assert result.status_code == 200
    state = await current(chat[0], state)
    assert state["fields"][0] == before[0] and state["fields"][2] == before[2]
    assert state["fields"][1]["status"] == "USER_PROVIDED"
    assert [s["slot"] for s in state["chat"]["question"]["slots"]] == [1, 3]
    assert "Anna Bianchi" not in state["chat"]["question"]["message"]


@pytest.mark.anyio
async def test_ambiguity_in_one_slot_does_not_rollback_other_valid_reply(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    before = state["fields"]
    await say(chat, state, "1. 055123456; 2. Anna oppure Lucia", answer(
        reply(1, value="055123456"),
        reply(2, "CLARIFY", quote="Anna oppure Lucia"),
    ))
    state = await current(chat[0], state)
    assert state["fields"][0]["status"] == "USER_PROVIDED"
    assert state["fields"][1:] == before[1:]
    assert [s["slot"] for s in state["chat"]["question"]["slots"]] == [2, 3]
    assert state["chat"]["question"]["slots"][0]["clarify"]


@pytest.mark.anyio
async def test_model_cannot_cut_an_alternative_from_a_numbered_answer(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    before = state["fields"]
    await say(chat, state, "1. 055123456; 2. Anna oppure Lucia", answer(
        reply(1, value="055123456"), reply(2, value="Anna", quote="Anna"),
    ))
    state = await current(chat[0], state)
    assert state["fields"][0]["status"] == "USER_PROVIDED"
    assert state["fields"][1:] == before[1:]
    assert state["chat"]["question"]["slots"][0]["slot"] == 2
    assert state["chat"]["question"]["slots"][0]["clarify"]


@pytest.mark.anyio
async def test_unknown_skip_do_not_block_valid_values_or_repeat_deferred_slots(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    await say(chat, state, "1. non lo so; 2. Anna Bianchi; 3. salta", answer(
        reply(1, "UNKNOWN", quote="non lo so"), reply(2, value="Anna Bianchi"),
        reply(3, "SKIP", quote="salta"),
    ))
    state = await current(chat[0], state)
    assert state["fields"][0]["value"] is None and state["fields"][2]["value"] is None
    assert state["fields"][1]["status"] == "USER_PROVIDED"
    assert state["chat"]["deferred"] == 2
    assert state["chat"]["question"]["kind"] == "deferred_summary"


@pytest.mark.anyio
async def test_pause_resume_keeps_backend_group_and_slot_bindings(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    question, fields = state["chat"]["question"], state["fields"]
    await say(chat, state, "basta", {"action": "PAUSE"})
    state = await current(chat[0], state)
    assert state["chat"]["paused_by_user"] and state["chat"]["question"] is None
    await say(chat, state, "riprendi", {"action": "compilation_control", "target": "form",
        "queries": [], "answer": "", "control": {"kind": "resume", "user_quote": "riprendi"}})
    state = await current(chat[0], state)
    assert state["fields"] == fields and state["chat"]["question"] == question


@pytest.mark.anyio
async def test_shared_condition_has_high_priority_and_one_reply_excludes_group(chat, monkeypatch):
    labels = ("Recapito", "Dato A (se partecipazione collettiva)",
              "Dato B (se partecipazione collettiva)", "Dato C (se partecipazione collettiva)")
    state, _ = await start(chat, content=docx(labels))
    def meanings(fields):
        return CandidateMeanings(fields=[{
            "candidate_id": f["id"], "classification": "data", "entity": "company",
            "form_quote": f["context"], "requirement": {"name": f["label"],
            "form_quote": f["context"], "form_citation_id": 1},
            "condition": "se partecipazione collettiva" if f["id"] != fields[0]["id"] else "",
            "reason": "Condizione grounded nel contesto",
        } for f in fields])
    simulate(monkeypatch, classify_hook=meanings)
    state = await step(chat[0], state)
    slots = state["chat"]["question"]["slots"]
    assert slots[0]["impact"] == 3 and len(slots) == 1
    await say(chat, state, "No, la partecipazione non è collettiva.", answer(
        reply(1, "CONDITION_FALSE", quote="No, la partecipazione non è collettiva."),
    ))
    state = await current(chat[0], state)
    assert all(f["status"] == "NOT_APPLICABLE" and f["provenance"] == "USER"
               for f in state["fields"][1:])
    assert state["fields"][0]["status"] == "MISSING"


@pytest.mark.anyio
async def test_source_resolved_fields_are_not_asked_or_changed_by_group_reply(chat, monkeypatch):
    labels = ("Denominazione sociale", "Forma giuridica", "Sede legale", "Codice fiscale",
              "Partita IVA", "Referente", "Data avvio")
    values = ["Aurora Progetti S.r.l.", "Societa cooperativa", "Via Roma 7", "CF123456",
              "IT98765432109"]
    state, _ = await start(chat, content=docx(labels))
    await source(chat[0], "\n".join(f"{label}: {value}" for label, value in zip(labels, values)))
    simulate(monkeypatch, {f"t0.r{i}.c1": [value] for i, value in enumerate(values)})
    state = await step(chat[0], state)
    assert state["summary"]["resolved"] == 5
    before = state["fields"][:5]
    await say(chat, state, "1. Anna Bianchi; 2. salta", answer(
        reply(1, value="Anna Bianchi"), reply(2, "SKIP", quote="salta"),
    ))
    state = await current(chat[0], state)
    assert state["fields"][:5] == before
    assert all(f["provenance"] == "SOURCE" for f in state["fields"][:5])


@pytest.mark.anyio
async def test_group_schema_never_exposes_or_accepts_field_ids(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    await say(chat, state, "1. salta", answer(reply(1, "SKIP", quote="salta")))
    request = chat[2][-1]
    prompt = request["messages"][1]["content"]
    schema = json.loads(prompt.split("SCHEMA OUTPUT:\n")[1].split("\n\nULTIMO MESSAGGIO:")[0])
    assert "field_id" not in json.dumps(schema)
    assert all(f["id"] not in prompt for f in state["fields"])


@pytest.mark.anyio
async def test_pending_source_validation_rejection_gets_one_automatic_retry(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 7")
    simulate(monkeypatch, {"t0.r0.c1": ["Via Roma 7"]})
    original = __import__("app.compilation_session_resolution", fromlist=["match_candidates"])
    matcher = original.match_candidates
    calls = []
    async def match(fields, sources, coverage):
        result = await matcher(fields, sources, coverage)
        calls.append(1)
        if len(calls) == 1:
            result.fields[0].supports[0].quote = "Estratto inventato"
        return result
    monkeypatch.setattr(original, "match_candidates", match)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "MISSING"
    assert state["chat"]["auto_continue"] and state["chat"]["question"] is None
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "RESOLVED"
    assert state["fields"][0]["provenance"] == "SOURCE" and len(calls) == 2


@pytest.mark.anyio
async def test_never_searched_data_cannot_become_a_user_question(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    def unsearched(s):
        for field in s["fields"]:
            field["search"] = {"status": "not_searched"}
    mutate_state(state, unsearched)
    state = await current(chat[0], state)
    assert state["chat"]["question"] is None or not state["chat"]["question"]["field_ids"]


@pytest.mark.anyio
async def test_slot_outside_active_group_is_rejected_before_any_update(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch, labels=("Recapito", "Referente"))
    bad = answer(reply(4, value="Valore inventato"))
    chat[1].extend([bad, bad])
    response = await chat[0].post("/api/projects/alpha/answer", json={
        "question": "Il referente è Anna.", "conversation_id": state["conversation_id"],
        "compilation_session_id": state["id"], "compilation_version": state["version"],
    })
    assert response.json()["generation_status"] == "failed"
    assert (await current(chat[0], state)) == state


@pytest.mark.anyio
async def test_numbered_user_excerpts_cannot_be_transferred_to_another_slot(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch, labels=("Recapito", "Referente"))
    await say(chat, state, "1. 055123456; 2. Anna Bianchi", answer(
        reply(1, value="Anna Bianchi"), reply(2, value="055123456"),
    ))
    state_after = await current(chat[0], state)
    assert state_after["fields"] == state["fields"]


@pytest.mark.anyio
async def test_empty_association_cannot_repeat_group_forever(chat, monkeypatch):
    state = await checkpoint(chat, monkeypatch)
    await say(chat, state, "Risposta incomprensibile", answer())
    state = await current(chat[0], state)
    await say(chat, state, "Ancora incomprensibile", answer())
    state = await current(chat[0], state)
    assert state["chat"]["deferred"] == 3
    assert state["chat"]["question"]["kind"] == "deferred_summary"


@pytest.mark.anyio
async def test_invalid_batch_does_not_stop_other_candidates(chat, monkeypatch):
    from app import compilation_session_resolution as resolution

    state, _ = await start(chat, content=docx(tuple(f"Dato {i}" for i in range(13))))
    simulate(monkeypatch)
    original = resolution.classify_candidates
    calls = []
    async def classifier(fields):
        calls.append([f["id"] for f in fields])
        if any(f["id"] == "t0.r0.c1" for f in fields):
            raise resolution.CompilationOutputError(
                "Output strutturato della risoluzione non valido",
            )
        return await original(fields)
    monkeypatch.setattr(resolution, "classify_candidates", classifier)
    for _ in range(4):
        state = await step(chat[0], state)
        if not state["chat"]["auto_continue"]:
            break
    assert sum("t0.r0.c1" in batch for batch in calls) == 2
    assert state["summary"]["missing"] == 7
    assert state["summary"]["pending"] == 6
    assert state["chat"]["metrics"]["user_required_fields"] == 7
    assert "t0.r0.c1" not in state["chat"]["question"]["field_ids"]
    assert state["chat_workflow"]["output_rejections"] == 2


@pytest.mark.anyio
async def test_provider_failure_still_stops_automatic_analysis(chat, monkeypatch):
    from app import compilation_session_resolution as resolution

    state, _ = await start(chat)
    simulate(monkeypatch)
    async def failure(fields):
        raise GenerationError("Provider non disponibile")
    monkeypatch.setattr(resolution, "classify_candidates", failure)
    response = await chat[0].post(f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
        json={"version": state["version"], "automatic": True})
    assert response.status_code == 502
    state = await current(chat[0], state)
    assert state["status"] == "FAILED" and not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_exhausted_invalid_output_is_not_a_request_for_user_values(chat, monkeypatch):
    from app import compilation_session_resolution as resolution

    state, _ = await start(chat)
    simulate(monkeypatch)
    async def failure(fields):
        raise resolution.CompilationOutputError("Output strutturato della risoluzione non valido")
    monkeypatch.setattr(resolution, "classify_candidates", failure)
    state = await step(chat[0], state)
    assert state["chat"]["auto_continue"] and state["chat"]["question"] is None
    state = await step(chat[0], state)
    assert state["status"] != "FAILED" and not state["chat"]["auto_continue"]
    assert "Ho conservato" in state["chat"]["notice"]
    assert set(state["chat_workflow"]["analysis_attempts"].values()) == {2}
    assert state["chat"]["question"] is None
    assert state["chat"]["metrics"]["user_required_fields"] == 0
    assert all(f["status"] == "PENDING" and f["value"] is None for f in state["fields"])


@pytest.mark.anyio
async def test_pause_during_an_invalid_output_wins_over_automatic_recovery(chat, monkeypatch):
    from app import compilation_session_resolution as resolution
    from app import compilation_sessions as sessions
    from app.compilation_chat import ChatControl

    state, _ = await start(chat)
    simulate(monkeypatch)
    async def failure(fields):
        sessions.chat_control("alpha", state["id"], state["version"],
                              ChatControl(kind="pause", user_quote="basta"))
        raise resolution.CompilationOutputError("Output strutturato della risoluzione non valido")
    monkeypatch.setattr(resolution, "classify_candidates", failure)
    response = await chat[0].post(f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
        json={"version": state["version"], "automatic": True})
    assert response.status_code == 502
    state = await current(chat[0], state)
    assert state["chat"]["paused_by_user"] and not state["chat"]["auto_continue"]
    assert not state["chat_workflow"].get("output_rejections")
