"""Conversational workflow: isolated storage, real routing/API, simulated providers."""

import json
from datetime import UTC, datetime, timedelta

import pytest
from test_compilation_sessions import docx, simulate
from test_form_retrieval import chat as retrieval_chat
from test_form_retrieval import plan

from app.compilation_chat import (
    MAX_AUTO_STEPS,
    normalize_date,
    planner_context,
    single_active_target,
)
from app.compilation_clarifications import active_group
from app.db import connection

chat = retrieval_chat
BASE = "/api/projects/alpha/compilation-sessions"


@pytest.fixture
def anyio_backend():
    return "asyncio"


def command(action, **extra):
    if action == "compilation_input":
        reply, = extra["field_replies"]
        semantic = {"set": "VALUE", "applicable": "CONDITION_TRUE",
                    "not_applicable": "CONDITION_FALSE"}[reply["action"]]
        if semantic != "VALUE":
            return {"action": semantic}
        value = reply["value"]
        if normalize_date(reply["user_quote"]) == value:
            return {"action": semantic, "value": reply["user_quote"], "normalized_value": value}
        return {"action": semantic, "value": value}
    if action == "compilation_clarify":
        return {"action": "CLARIFY", "rationale": extra.get("answer", "")}
    return {"action": action, "target": "form", "answer": "", "queries": [], **extra}


async def start(chat, text="me lo compili?", content=None):
    client, replies, _, _ = chat
    form = (await client.post("/api/projects/alpha/forms", files={
        "file": ("domanda.docx", content or docx()),
    })).json()
    replies.append(command("compile", form_id=form["id"]))
    response = await client.post("/api/projects/alpha/answer", json={
        "question": text, "form_id": form["id"],
    })
    assert response.status_code == 200, response.text
    answer = response.json()
    session = (await client.get(f"{BASE}/{answer['compilation']['session_id']}")).json()
    return session, answer


async def step(client, session):
    response = await client.post(f"{BASE}/{session['id']}/resolve", json={
        "version": session["version"], "automatic": True,
    })
    assert response.status_code == 200, response.text
    return response.json()


async def say(chat, state, message, decision):
    client, replies, _, _ = chat
    if active_group(planner_context(state)):
        slots = state["chat"]["question"]["slots"]
        if decision["action"] == "compilation_control":
            control = decision["control"]
            if control["kind"] == "pause":
                decision = {"action": "PAUSE"}
            else:
                slot = next((s for s in slots if control.get("field_id") in s["field_ids"]),
                            slots[0])
                decision = {"action": "ANSWER", "replies": [{
                    "slot": slot["slot"], "action": control["kind"].upper(),
                    "user_quote": message,
                }]}
        elif decision["action"] in {"reply", "retrieve", "compile", "compilation_generate"}:
            decision = {"action": "CHAT", "chat": decision}
        elif decision["action"] in {"VALUE", "CLARIFY", "UNKNOWN", "SKIP", "REFUSE",
                                     "CONDITION_TRUE", "CONDITION_FALSE"}:
            decision = {"action": "ANSWER", "replies": [{
                **decision, "slot": slots[0]["slot"], "user_quote": message,
            }]}
    elif single_active_target(planner_context(state)) is not None:
        if decision["action"] == "compilation_control":
            decision = {"action": decision["control"]["kind"].upper()}
        elif decision["action"] in {"reply", "retrieve", "compile", "compilation_generate"}:
            decision = {"action": "CHAT", "chat": decision}
    replies.append(decision)
    return await client.post("/api/projects/alpha/answer", json={
        "question": message, "conversation_id": state["conversation_id"],
        "form_id": state["original_file_id"], "compilation_session_id": state["id"],
        "compilation_version": state["version"],
    })


def mutate_state(session, change):
    # Test-only edits of isolated SQLite, never the user's local data.
    with connection() as db:
        state = json.loads(db.execute(
            "SELECT state_json FROM compilation_sessions WHERE id=?", (session["id"],),
        ).fetchone()[0])
        change(state)
        db.execute("UPDATE compilation_sessions SET state_json=? WHERE id=?",
                   (json.dumps(state), session["id"]))


@pytest.mark.anyio
@pytest.mark.parametrize("text", [
    "me lo compili?", "compila questo documento", "inizia la compilazione",
    "prova a compilare il modulo", "completa questo documento con i dati disponibili",
])
async def test_compilation_intent_bypasses_rag_and_reuses_session(chat, text):
    client, _, requests, _ = chat
    state, answer = await start(chat, text)
    assert answer["generation_status"] == "direct" and answer["evidence"] == []
    assert answer["answer"].startswith("Certo. Analizzo")
    assert len(requests) == 1  # No normal RAG generator can contradict the workflow.
    assert "compile" in requests[0]["messages"][0]["content"]
    assert state["chat"]["auto_continue"] and state["last_generation"] is None
    resumed = (await say(chat, state, text, command("compile"))).json()
    assert resumed["compilation"]["session_id"] == state["id"]
    history = (await client.get(
        f"/api/projects/alpha/conversations/{state['conversation_id']}",
    )).json()
    assert all(t["compilation"]["session_id"] == state["id"] for t in history["turns"])


@pytest.mark.anyio
async def test_auto_steps_stop_on_question_free_reply_localized_and_ready(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Denominazione sociale", "Data abilitazione")))
    await client.post("/api/global-knowledge/files", data={"category": "company"}, files={
        "file": ("visura.txt", b"Denominazione sociale: Mapi Ingegneria S.r.l."),
    })
    simulate(monkeypatch, {state["fields"][0]["id"]: ["Mapi Ingegneria S.r.l."]})
    state = await step(client, state)
    assert state["status"] == "WAITING_FOR_USER" and not state["chat"]["auto_continue"]
    asked = state["fields"][1]["id"]
    assert state["chat"]["question"]["field_ids"] == [asked]
    assert "Data abilitazione" in state["chat"]["question"]["message"]
    assert state["summary"]["resolved"] == 1 and state["summary"]["missing"] == 1
    blocked = await client.post(f"{BASE}/{state['id']}/resolve", json={
        "version": state["version"], "automatic": True,
    })
    assert blocked.status_code == 409
    before = state["fields"][0]
    answer = await say(chat, state, "12 giugno 2014", command("compilation_input", field_replies=[{
        "field_id": asked, "action": "set", "value": "12/06/2014", "user_quote": "12 giugno 2014",
    }]))
    assert answer.status_code == 200, answer.text
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["fields"][0] == before
    assert state["fields"][1]["value"] == "12/06/2014"
    assert state["fields"][1]["provenance"] == "USER"
    assert state["fields"][1]["source_evidence"] == []
    assert state["status"] == "READY" and state["last_generation"] is None
    assert state["chat"]["question"]["kind"] == "generate"
    generated = await say(chat, state, "Sì, genera il DOCX", command("compilation_generate"))
    assert generated.status_code == 200, generated.text
    assert generated.json()["compilation"]["action"] == "generated"
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["last_generation"] and state["status"] == "GENERATED"


@pytest.mark.anyio
@pytest.mark.parametrize("failure", [
    "ambiguous", "invented", "form_value", "partial_quote",
    "ambiguous_set",
])
async def test_ambiguous_or_ungrounded_reply_changes_no_values(chat, monkeypatch, failure):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    before = state["fields"]
    field_id = state["chat"]["question"]["field_ids"][0]
    reply = {"field_id": field_id, "action": "set", "value": "Mapi", "user_quote": "Mapi"}
    message = "Mapi oppure altra società?"
    decision = command("compilation_clarify", answer="Quale società devo usare?")
    if failure in {"invented", "form_value"}:
        message = "Non riesco a indicare un valore"
        reply["user_quote"] = message
    elif failure == "partial_quote":
        message = "Mapiano"
    if failure != "ambiguous":
        decision = command("compilation_input", field_replies=[reply])
    response = await say(chat, state, message, decision)
    assert response.status_code == 200, response.text
    assert response.json()["compilation"]["action"] == "clarify"
    after = (await client.get(f"{BASE}/{state['id']}")).json()
    assert after["fields"] == before
    assert after["version"] == state["version"] + 1
    assert after["chat"]["question"]["slots"][0]["clarify"]
    assert not after["last_generation"]


@pytest.mark.anyio
async def test_reply_restarts_auto_analysis_without_resetting_other_fields(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(tuple(f"Dato {i}" for i in range(14))))
    simulate(monkeypatch)
    state = await step(client, state)
    assert state["summary"]["pending"] == 2
    assert state["chat"]["auto_continue"] and state["chat"]["question"] is None
    state = await step(client, state)
    assert state["summary"]["pending"] == 0
    for _ in range(12):
        asked = state["chat"]["question"]["field_ids"][0]
        response = await say(chat, state, "Valore fornito", command(
            "compilation_input", field_replies=[{
                "field_id": asked, "action": "set", "value": "Valore fornito",
                "user_quote": "Valore fornito",
            }],
        ))
        assert response.status_code == 200, response.text
        state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["status"] == "WAITING_FOR_USER" and not state["chat"]["auto_continue"]
    assert state["summary"]["user_provided"] == 12
    assert state["summary"]["missing"] == 2


@pytest.mark.anyio
@pytest.mark.parametrize("budget", ["steps", "time", "interpretation"])
async def test_persistent_auto_budget_requires_explicit_resume(chat, budget):
    client, _, _, _ = chat
    state, _ = await start(chat)
    def expire(s):
        if budget == "steps":
            s["chat_workflow"]["steps"] = MAX_AUTO_STEPS
        elif budget == "time":
            s["chat_workflow"]["started_at"] = (
                datetime.now(UTC) - timedelta(minutes=11)
            ).isoformat()
        else:
            s["chat_workflow"]["paused_reason"] = "interpretation"
    mutate_state(state, expire)
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["chat"]["paused"] and not state["chat"]["auto_continue"]
    assert (await client.get(f"{BASE}/{state['id']}")).json()["chat"] == state["chat"]
    blocked = await client.post(f"{BASE}/{state['id']}/resolve", json={
        "version": state["version"], "automatic": True,
    })
    assert blocked.status_code == 409
    assert (await say(chat, state, "Prosegui compilazione", command("compile"))).status_code == 200
    after = (await client.get(f"{BASE}/{state['id']}")).json()
    assert after["chat"]["auto_continue"] and after["chat"]["steps_used"] == 0
    assert after["fields"] == state["fields"]


@pytest.mark.anyio
@pytest.mark.parametrize("message", ["No", "Non lo so", "Sì"])
async def test_applicability_does_not_supply_factual_values(chat, monkeypatch, message):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    def conditional(s):
        s["fields"][0].update(status="AMBIGUOUS", condition="consorzio stabile")
    mutate_state(state, conditional)
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    asked = state["fields"][0]["id"]
    action = "applicable" if message == "Sì" else "not_applicable"
    decision = command("compilation_input", field_replies=[{
        "field_id": asked, "action": action, "value": None,
        "user_quote": "No" if message == "Non lo so" else message,
    }]) if message != "Non lo so" else {"action": "UNKNOWN"}
    response = await say(chat, state, message, decision)
    assert response.status_code == 200, response.text
    after = (await client.get(f"{BASE}/{state['id']}")).json()
    if message == "No":
        assert after["fields"][0]["status"] == "NOT_APPLICABLE"
        assert after["fields"][0]["provenance"] == "USER"
    elif message == "Sì":
        assert after["fields"][0]["status"] == "PENDING"
        assert after["fields"][0]["applicability_confirmed"]["provenance"] == "USER"
        assert after["chat"]["auto_continue"]
        assert after["chat"]["question"] is None
    else:
        unchanged = dict(after["fields"][0])
        note = unchanged.pop("conversation_disposition")
        assert unchanged == state["fields"][0]
        assert note["kind"] == "unknown"
        assert after["fields"][1:] == state["fields"][1:]
    assert all(f["status"] != "RESOLVED" for f in after["fields"])


@pytest.mark.anyio
async def test_normal_form_question_during_compilation_does_not_mutate_state(chat, monkeypatch):
    client, replies, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    replies.extend([{"action": "CHAT", "chat": plan(
        "form", state["form_id"], "denominazione sociale",
    )}, {
        "answer": "Il modulo richiede la denominazione sociale [1].", "citation_ids": [1],
    }])
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "cosa richiede?", "conversation_id": state["conversation_id"],
        "form_id": state["form_id"],
    })
    assert response.status_code == 200, response.text
    assert not response.json()["compilation"]
    assert (await client.get(f"{BASE}/{state['id']}")).json() == state


@pytest.mark.anyio
async def test_stale_question_and_cross_project_cannot_update_or_generate(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    response = await say(chat, {**state, "version": state["version"] - 1},
                         "Genera", command("compilation_generate"))
    assert response.status_code == 409
    blocked = await client.post("/api/projects/beta/answer", json={
        "question": "Compila", "compilation_session_id": state["id"],
    })
    assert blocked.status_code == 404
    response = await say(chat, state, "Genera", command("compilation_generate"))
    assert response.json()["compilation"]["action"] == "clarify"
    assert (await client.get(f"{BASE}/{state['id']}")).json()["last_generation"] is None


@pytest.mark.anyio
async def test_two_dates_cannot_be_silently_chosen_by_planner(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Data abilitazione",)))
    simulate(monkeypatch)
    state = await step(client, state)
    response = await say(chat, state, "12 giugno 2014 oppure 12 giugno 2015", command(
        "compilation_input", field_replies=[{
            "field_id": state["fields"][0]["id"], "action": "set", "value": "12/06/2014",
            "user_quote": "12 giugno 2014",
        }],
    ))
    assert response.json()["compilation"]["action"] == "clarify"
    assert (await client.get(f"{BASE}/{state['id']}")).json()["fields"] == state["fields"]


@pytest.mark.anyio
async def test_multiple_automatic_steps_end_ready_and_count_real_work(chat, monkeypatch):
    from app.compilation_session_models import CandidateMeanings

    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(tuple("" for _ in range(7))))
    def classify(fields):
        return CandidateMeanings(fields=[{
            "candidate_id": f["id"], "classification": "decorative",
            "kind": "data", "requirement": None,
            "entity": "company", "form_quote": f["context"], "reason": "Spazio decorativo",
        } for f in fields])
    simulate(monkeypatch, classify_hook=classify)
    state = await step(client, state)
    assert state["status"] == "CREATED" and state["chat"]["auto_continue"]
    assert state["chat"]["steps_used"] == 1
    state = await step(client, state)
    assert state["status"] == "READY" and not state["chat"]["auto_continue"]
    assert state["chat"]["steps_used"] == 2 and state["summary"]["pending"] == 0
    assert state["last_generation"] is None


@pytest.mark.anyio
async def test_expired_analysis_claim_reopens_as_safe_resume(chat):
    client, _, _, _ = chat
    state, _ = await start(chat)
    def stale(s):
        s.update(status="ANALYZING", lease_until=(
            datetime.now(UTC) - timedelta(seconds=1)
        ).isoformat())
    mutate_state(state, stale)
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["chat"]["paused"] and not state["chat"]["auto_continue"]
    answer = await say(chat, state, "Riprendi compilazione", command("compile"))
    assert answer.status_code == 200, answer.text
    state = (await client.get(f"{BASE}/{state['id']}")).json()
    assert state["status"] == "CREATED" and state["chat"]["auto_continue"]
    assert state["lease_until"] is None
