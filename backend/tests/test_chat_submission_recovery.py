"""Retries identify one USER submission, including a one-character choice."""

import asyncio

import pytest
from test_chat_flow import URL, chat, previous_turn

from app import main
from app.db import connection
from app.intents import ChatDecision, PlannedTurn

__all__ = ["chat"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_single_character_user_choice_reaches_router_and_is_saved_once(chat):
    client, replies, requests = chat
    replies.append({"intent": "reply", "target": "source", "answer": "Quale opzione?",
                    "queries": []})
    response = await client.post(f"{URL}/answer", json={"question": "4"})
    assert response.status_code == 200
    data = response.json()
    history = (await client.get(f"{URL}/conversations/{data['conversation_id']}")).json()
    assert history["turns"][0]["question"] == "4" and len(requests) == 1


@pytest.mark.anyio
async def test_transport_retry_returns_same_saved_turn_without_second_model_or_mutation(chat):
    client, replies, requests = chat
    replies.extend([{"intent": "reply", "target": "source", "answer": "Ricevuto",
                     "queries": []}] * 2)
    payload = {"question": "Scelgo la quarta opzione", "conversation_id": previous_turn(),
               "request_id": "transport-retry-1"}
    first = await client.post(f"{URL}/answer", json=payload)
    second = await client.post(f"{URL}/answer", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["turn_id"] == second.json()["turn_id"]
    assert len(requests) == 1
    history = (await client.get(f"{URL}/conversations/{payload['conversation_id']}")).json()
    assert len(history["turns"]) == 2


@pytest.mark.anyio
async def test_same_request_id_cannot_change_the_user_message(chat):
    client, replies, requests = chat
    replies.extend([{"intent": "reply", "target": "source", "answer": "Ricevuto",
                     "queries": []}] * 2)
    payload = {"question": "Prima scelta", "request_id": "same-id-changed-content"}
    assert (await client.post(f"{URL}/answer", json=payload)).status_code == 200
    response = await client.post(f"{URL}/answer", json={**payload, "question": "Altra scelta"})
    assert response.status_code == 409 and len(requests) == 1


@pytest.mark.anyio
async def test_concurrent_retry_does_not_start_a_second_dispatch(chat, monkeypatch):
    client, _, _ = chat
    started, finish = asyncio.Event(), asyncio.Event()
    calls = []

    async def plan(*args, **kwargs):
        calls.append(args)
        started.set()
        await finish.wait()
        return PlannedTurn(ChatDecision(action="reply", answer="Ricevuto", queries=[],
                                        target="source"), "simulated", 0)

    monkeypatch.setattr(main, "plan_chat_turn", plan)
    payload = {"question": "4", "request_id": "in-flight"}
    task = asyncio.create_task(client.post(f"{URL}/answer", json=payload))
    await asyncio.wait_for(started.wait(), 5)
    try:
        duplicate = await client.post(f"{URL}/answer", json=payload)
        assert duplicate.status_code == 409 and len(calls) == 1
        receipt = (await client.get(f"{URL}/answer-submissions/in-flight")).json()
        assert receipt["state"] == "pending" and receipt["request"]["question"] == "4"
    finally:
        finish.set()
    first = await task
    assert first.status_code == 200
    assert (await client.post(f"{URL}/answer", json=payload)).json() == first.json()


@pytest.mark.anyio
async def test_lost_response_after_chat_commit_is_recovered_without_new_dispatch(chat, monkeypatch):
    client, replies, requests = chat
    replies.append({"intent": "reply", "target": "source", "answer": "Ricevuto",
                    "queries": []})
    save = main.save_conversation_turn

    def lost(*args):
        save(*args)
        raise RuntimeError("response transport lost after commit")

    monkeypatch.setattr(main, "save_conversation_turn", lost)
    payload = {"question": "4", "request_id": "after-commit"}
    with pytest.raises(RuntimeError):
        await client.post(f"{URL}/answer", json=payload)
    receipt = (await client.get(f"{URL}/answer-submissions/after-commit")).json()
    assert receipt["state"] == "completed"
    second = await client.post(f"{URL}/answer", json=payload)
    assert second.status_code == 200 and len(requests) == 1
    assert second.json()["turn_id"] == receipt["response"]["turn_id"]


@pytest.mark.anyio
async def test_uncertain_interruption_preserves_payload_and_never_redispatches(chat, monkeypatch):
    client, _, _ = chat
    calls = []

    async def interrupted(*args, **kwargs):
        calls.append(args)
        raise RuntimeError("process interrupted at unknown mutation boundary")

    monkeypatch.setattr(main, "_project_answer", interrupted)
    payload = {"question": "4", "request_id": "uncertain"}
    with pytest.raises(RuntimeError):
        await client.post(f"{URL}/answer", json=payload)
    assert (await client.post(f"{URL}/answer", json=payload)).status_code == 409
    assert len(calls) == 1
    with connection() as db:
        row = db.execute("SELECT state,payload_json FROM chat_submissions").fetchone()
    assert row["state"] == "interrupted" and '"question": "4"' in row["payload_json"]
