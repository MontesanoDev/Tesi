"""Exercise planning -> search -> answer with real API and simulated model responses."""

import asyncio
import json

import httpx
import pytest

from app import main
from app.db import init_database
from app.intents import ChatDecision, PlannedTurn
from app.repository import get_or_create_conversation, save_conversation_turn
from app.seed import seed_database

PROJECT = "fondo-riqualificazione-2027"
URL = f"/api/projects/{PROJECT}"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def chat(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "chat.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "http://provider.test")
    monkeypatch.setenv("DEEPSEEK_MODEL", "selected-model")
    init_database()
    seed_database()
    original = httpx.AsyncClient
    transport = httpx.ASGITransport(app=main.app)
    async with original(transport=transport, base_url="http://test") as client:
        replies, requests = [], []

        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            assert body["model"] == "selected-model"
            assert replies, "Unexpected additional model call"
            reply = replies.pop(0)
            if isinstance(reply, httpx.Response):
                return reply
            content = reply if isinstance(reply, str) else json.dumps(reply)
            return httpx.Response(200, json={
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"total_tokens": 20},
                "model": "selected-model",
            })

        monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(
            transport=httpx.MockTransport(handler), **kwargs,
        ))
        yield client, replies, requests


def previous_turn():
    conversation = get_or_create_conversation(PROJECT, None, "Chi e il responsabile?")
    save_conversation_turn(conversation["id"], {
        "question": "Chi e il responsabile?", "answer": "Il responsabile e Rossi [8].",
        "generation_status": "completed", "model": "old-model",
        "evidence": [], "citations": [8],
    })
    return conversation["id"]


def no_search(*_args, **_kwargs):
    pytest.fail("This message must not search documents")


@pytest.mark.anyio
@pytest.mark.parametrize("question", ["ok grazie", "Gentilissimo, per ora ho finito", "Chi sei?"])
async def test_conversational_reply_is_one_call_without_search(chat, monkeypatch, question):
    client, replies, requests = chat
    conversation = previous_turn()
    replies.append({
        "intent": "reply", "target": "source", "answer": "Prego, a disposizione!", "queries": [],
    })
    monkeypatch.setattr(main, "search_project_evidence", no_search)
    response = await client.post(f"{URL}/answer", json={
        "question": question, "conversation_id": conversation,
    })
    payload = response.json()
    assert payload["generation_status"] == "direct"
    assert payload["answer"] == "Prego, a disposizione!"
    assert payload["evidence"] == payload["citations"] == payload["missing_information"] == []
    assert payload["model"] == "selected-model"
    assert payload["total_tokens"] == 20
    assert len(requests) == 1
    prompt = requests[0]["messages"][1]["content"]
    assert "Rossi" in prompt and "[8]" not in prompt
    assert prompt.endswith(question)
    history = (await client.get(f"{URL}/conversations/{conversation}")).json()["turns"]
    assert len(history) == 2
    assert history[-1]["generation_status"] == "direct"
    assert history[-1]["evidence"] == []


@pytest.mark.anyio
async def test_compound_request_searches_both_objectives_and_deduplicates(chat, monkeypatch):
    client, replies, requests = chat
    for name, text in [
        ("oggetto.txt", "Oggetto appalto: direzione lavori residenze universitarie."),
        ("contatti.txt", "Responsabile telefono 0123456789 e PEC ufficio@example.test."),
    ]:
        assert (await client.post(f"{URL}/files", files={
            "file": (name, text.encode(), "text/plain"),
        })).status_code == 201
    searches = []
    search = main.search_project_evidence

    def recorded_search(project, query, **kwargs):
        searches.append(query)
        return search(project, query, **kwargs)

    monkeypatch.setattr(main, "search_project_evidence", recorded_search)
    replies.extend([
        {"intent": "retrieve", "target": "source", "answer": "", "queries": [
            "Oggetto appalto", "Responsabile telefono PEC", "oggetto appalto",
        ]},
        {"answer": "Direzione lavori [1]. Telefono 0123456789 [2].", "citation_ids": [1, 2]},
    ])
    response = await client.post(f"{URL}/answer", json={
        "question": "Ciao, riassumi il bando e dammi un contatto del responsabile",
    })
    payload = response.json()
    assert payload["generation_status"] == "completed"
    assert searches == ["Oggetto appalto", "Responsabile telefono PEC"]
    assert {item["source_name"] for item in payload["evidence"]} == {"oggetto.txt", "contatti.txt"}
    assert len(payload["evidence"]) == 2
    assert payload["total_tokens"] == 40
    assert len(requests) == 2
    assert "0123456789" in requests[1]["messages"][1]["content"]
    history = (await client.get(
        f"{URL}/conversations/{payload['conversation_id']}",
    )).json()["turns"]
    assert len(history) == 1
    assert history[0]["evidence"] == payload["evidence"]


@pytest.mark.anyio
async def test_follow_up_uses_resolved_query_and_fresh_sources(chat):
    client, replies, requests = chat
    conversation = previous_turn()
    await client.post(f"{URL}/files", files={
        "file": ("recapito.txt", b"Recapito responsabile Rossi: 0123456789.", "text/plain"),
    })
    replies.extend([
        {"intent": "retrieve", "target": "source", "answer": "",
         "queries": ["Recapito responsabile Rossi"]},
        {"answer": "Il recapito e 0123456789 [1].", "citation_ids": [1]},
    ])
    response = await client.post(f"{URL}/answer", json={
        "question": "Come posso contattarlo?", "conversation_id": conversation,
    })
    assert response.json()["generation_status"] == "completed"
    prompt = requests[-1]["messages"][1]["content"]
    assert "[8]" not in prompt
    assert "0123456789" in prompt
    assert prompt.index("EVIDENZE DISPONIBILI") < prompt.index("Come posso contattarlo?")


@pytest.mark.anyio
@pytest.mark.parametrize("plan", [
    "not json", "[]",
    {"intent": "retrieve", "target": "source", "answer": "", "queries": []},
    {"intent": "reply", "target": "source", "answer": "Dato [1]", "queries": []},
    {"intent": "retrieve", "target": "source", "answer": "Dato inventato", "queries": ["Contatti"]},
    {"intent": "reply", "target": "source", "answer": "Prego!", "queries": ["Contatti"]},
    {"intent": "retrieve", "target": "source", "answer": "", "queries": ["   "]},
    {"intent": "retrieve", "target": "source", "answer": "", "queries": ["a", "b", "c", "d"]},
    {"intent": "retrieve", "answer": "", "queries": ["partita IVA"]},
    {"intent": "retrieve", "target": "invalid", "answer": "", "queries": ["partita IVA"]},
    {"intent": "retrieve", "target": "source", "form_id": 1, "answer": "", "queries": ["IVA"]},
    {"intent": "retrieve", "target": "form", "form_id": -1, "answer": "", "queries": ["IVA"]},
    {"intent": "retrieve", "target": "mixed", "answer": "", "queries": []},
    {"intent": "retrieve", "target": "source", "answer": "", "queries": ["partita IVA"],
     "source_queries": ["partita IVA"]},
    {"intent": "retrieve", "target": "mixed", "answer": "", "queries": ["requisiti", "allegati"],
     "source_queries": ["partita IVA", "sede"]},
])
async def test_invalid_plan_does_not_trigger_arbitrary_search_or_answer(chat, monkeypatch, plan):
    client, replies, requests = chat
    replies.extend([plan, plan])
    monkeypatch.setattr(main, "search_project_evidence", no_search)
    response = await client.post(f"{URL}/answer", json={"question": "Mi aiuti?"})
    payload = response.json()
    assert payload["generation_status"] == "failed"
    assert "decisione valida" in payload["notice"]
    assert payload["answer"] is None
    assert payload["evidence"] == []
    assert len(requests) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("first,corrected", [
    (
        {"intent": "reply", "target": "source", "answer": "Sono Mapi RAG."},
        {"intent": "reply", "target": "source", "answer": "Sono Mapi RAG.", "queries": []},
    ),
    (
        {"intent": "retrieve", "target": "source", "answer": "Fornisci il documento",
         "queries": ["Scadenza"]},
        {"intent": "retrieve", "target": "source", "answer": "", "queries": ["Scadenza"]},
    ),
])
async def test_invalid_decision_is_repaired_before_search_or_reply(chat, first, corrected):
    client, replies, requests = chat
    await client.post(f"{URL}/files", files={
        "file": ("scadenza.txt", b"Scadenza: 15 settembre", "text/plain"),
    })
    replies.extend([first, corrected])
    retrieving = corrected["intent"] == "retrieve"
    if retrieving:
        replies.append({"answer": "Scadenza 15 settembre [1].", "citation_ids": [1]})
    payload = (await client.post(f"{URL}/answer", json={"question": "Mi aiuti?"})).json()
    assert payload["generation_status"] == ("completed" if retrieving else "direct")
    assert len(requests) == (3 if retrieving else 2)
    assert payload["total_tokens"] == 20 * len(requests)
    assert requests[1]["messages"][:2] == requests[0]["messages"]
    assert requests[1]["messages"][-2]["content"] == json.dumps(first)
    assert "contratto" in requests[1]["messages"][-1]["content"]


@pytest.mark.anyio
@pytest.mark.parametrize("recovered", [False, True])
@pytest.mark.parametrize("known_usage", [False, True])
async def test_truncated_plan_has_one_retry_and_includes_its_usage(chat, recovered, known_usage):
    client, replies, requests = chat
    truncated = httpx.Response(200, json={
        "choices": [{"message": {"content": '{"intent":'}, "finish_reason": "length"}],
        "usage": {"total_tokens": 30} if known_usage else {},
    })
    replies.extend([
        truncated,
        {"intent": "reply", "target": "source", "answer": "Ciao!", "queries": []}
        if recovered else truncated,
    ])
    payload = (await client.post(f"{URL}/answer", json={"question": "Ciao"})).json()
    assert [r["max_tokens"] for r in requests] == [1024, 2048]
    assert requests[0]["messages"] == requests[1]["messages"]
    assert payload["evidence"] == []
    if recovered:
        assert payload["generation_status"] == "direct"
        assert payload["total_tokens"] == (50 if known_usage else None)
    else:
        assert payload["generation_status"] == "failed"
        assert "limite di 2048 token" in payload["notice"]


@pytest.mark.anyio
async def test_citation_repair_cost_includes_planning(chat):
    client, replies, requests = chat
    await client.post(f"{URL}/files", files={
        "file": ("recapito.txt", b"Recapito responsabile: 0123456789.", "text/plain"),
    })
    replies.extend([
        {"intent": "retrieve", "target": "source", "answer": "",
         "queries": ["Recapito responsabile"]},
        {"answer": "Recapito 0123456789 [24].", "citation_ids": [24]},
        {"answer": "Recapito 0123456789 [1].", "citation_ids": [1]},
    ])
    payload = (await client.post(f"{URL}/answer", json={"question": "Un contatto?"})).json()
    assert payload["generation_status"] == "completed"
    assert payload["total_tokens"] == 60
    assert len(requests) == 3
    assert requests[2]["messages"][:2] == requests[1]["messages"]


@pytest.mark.anyio
@pytest.mark.parametrize("stage", ["planning", "answer"])
async def test_entire_chat_has_one_deadline(chat, monkeypatch, stage):
    client, _, requests = chat
    await client.post(f"{URL}/files", files={
        "file": ("recapito.txt", b"Recapito responsabile: 0123456789.", "text/plain"),
    })
    cancelled = asyncio.Event()

    async def stalled(*_args, **_kwargs):
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()

    async def plan(question, history, forms=None):
        return PlannedTurn(ChatDecision(
            action="retrieve", target="source", answer="", queries=["Recapito responsabile"],
        ), "selected-model", 20)

    monkeypatch.setattr(main, "chat_timeout_seconds", lambda: 0.05)
    monkeypatch.setattr(main, "plan_chat_turn", stalled if stage == "planning" else plan)
    monkeypatch.setattr(main, "generate_grounded_answer", stalled)
    payload = (await client.post(f"{URL}/answer", json={"question": "Un contatto?"})).json()
    assert cancelled.is_set()
    assert not requests
    assert payload["generation_status"] == "failed"
    assert payload["answer"] is None
    assert "limite complessivo di 0.05 secondi" in payload["notice"]
    assert bool(payload["evidence"]) is (stage == "answer")
