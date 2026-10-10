"""Chat integration: real isolated persistence/retrieval, simulated AI providers."""

import asyncio

import pytest
from test_compilation_sessions import api as session_api
from test_compilation_sessions import docx
from test_form_retrieval import chat as retrieval_chat
from test_form_retrieval import global_source, plan, upload

from app.db import connection

api = session_api
chat = retrieval_chat


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_chat_start_creates_persistent_conversation_and_reuses_same_pair(api):
    uploaded = await api.post("/api/projects/alpha/forms", files={
        "file": ("domanda.docx", docx()),
    })
    form_id = uploaded.json()["id"]
    base = "/api/projects/alpha/compilation-sessions"
    response = await api.post(base, json={"form_id": form_id, "start_in_chat": True})
    assert response.status_code == 201, response.text
    session = response.json()
    conversation_id = session["conversation_id"]
    assert conversation_id and session["status"] == "CREATED"
    assert session["summary"]["pending"] == 2 and session["last_generation"] is None
    conversation = (await api.get(f"/api/projects/alpha/conversations/{conversation_id}")).json()
    assert conversation["turns"] == []
    assert conversation["form_reference"] == {"form_id": form_id, "name": "domanda.docx"}
    # Concurrent double start cannot create another session for this pair.
    repeats = await asyncio.gather(*[
        api.post(base, json={"form_id": form_id, "conversation_id": conversation_id,
                             "start_in_chat": True}) for _ in range(2)
    ])
    assert all(r.json()["id"] == session["id"] for r in repeats)
    assert all(r.json()["version"] == session["version"] for r in repeats)
    listed = (await api.get(base, params={"conversation_id": conversation_id})).json()
    assert [s["id"] for s in listed] == [session["id"]]
    assert (await api.get(f"{base}/{session['id']}")).json() == session
    assert (await api.get("/api/projects/beta/compilation-sessions",
                          params={"conversation_id": conversation_id})).status_code == 404
    assert (await api.post("/api/projects/beta/compilation-sessions", json={
        "form_id": form_id, "conversation_id": conversation_id, "start_in_chat": True,
    })).status_code == 404
    assert (await api.get(base, params={"conversation_id": "unknown"})).status_code == 404
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM compilation_sessions").fetchone()[0] == 1


@pytest.mark.anyio
async def test_start_failure_rolls_back_new_chat(api, monkeypatch):
    from app import compilation_sessions
    from app.docx_templates import DocumentInputError

    form = (await api.post("/api/projects/alpha/forms", files={
        "file": ("domanda.docx", docx()),
    })).json()
    with connection() as db:
        before = db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

    def fail(_):
        raise DocumentInputError("Modulo non leggibile")

    monkeypatch.setattr(compilation_sessions, "inspect_docx", fail)
    response = await api.post("/api/projects/alpha/compilation-sessions", json={
        "form_id": form["id"], "start_in_chat": True,
    })
    assert response.status_code == 422
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0] == before
        assert db.execute("SELECT COUNT(*) FROM compilation_sessions").fetchone()[0] == 0


@pytest.mark.anyio
async def test_mention_pins_form_retrieval_persists_reference_but_never_starts_session(chat):
    client, replies, requests, _ = chat
    form = await upload(client, name="scelto.txt", text="Allegati richiesti: documento identità.")
    other = await upload(client, name="altro.txt", text="Allegati richiesti: referenze bancarie.")
    await upload(client, project="beta", name="privato.txt", text="Allegati privati.")
    await global_source(client, "Allegati richiesti: informazioni aziendali.")
    replies.extend([plan("form", other["id"], "allegati richiesti"), {
        "answer": "Il modulo richiede il documento di identità [1].", "citation_ids": [1],
    }])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "quali allegati richiede?", "form_id": form["id"],
    })).json()
    assert result["generation_status"] == "completed", result
    assert {e["file_id"] for e in result["evidence"]} == {form["id"]}
    assert all(e["role"] == "form" for e in result["evidence"])
    assert result["form_reference"] == {"form_id": form["id"], "name": form["name"]}
    prompt = requests[0]["messages"][1]["content"]
    assert "La sola selezione non avvia" in prompt and form["name"] in prompt
    assert other["name"] not in prompt
    cid = result["conversation_id"]
    conversation = (await client.get(f"/api/projects/alpha/conversations/{cid}")).json()
    assert conversation["form_reference"] == result["form_reference"]
    assert conversation["turns"][0]["form_reference"] == result["form_reference"]
    assert (await client.get("/api/projects/alpha/compilation-sessions")).json() == []
    # Removing the mention clears the next turn's context, not historical references.
    replies.append({"intent": "reply", "target": "source", "form_id": None,
                    "answer": "Prego!", "queries": []})
    await client.post("/api/projects/alpha/answer", json={
        "question": "grazie", "conversation_id": cid,
    })
    conversation = (await client.get(f"/api/projects/alpha/conversations/{cid}")).json()
    assert conversation["form_reference"] is None
    assert conversation["turns"][0]["form_reference"] == result["form_reference"]
    assert conversation["turns"][1]["form_reference"] is None


@pytest.mark.anyio
async def test_factual_mention_stays_source_and_deleted_form_does_not_break_history(chat):
    client, replies, _, _ = chat
    form = await upload(client, name="scelto.txt", text="Partita IVA: 999999 da dichiarare")
    source = await global_source(client, "Partita IVA Mapi: 01234567890.")
    replies.extend([plan("source", query="partita IVA Mapi"), {
        "answer": "La partita IVA è 01234567890 [1].", "citation_ids": [1],
    }])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "qual è la partita IVA di Mapi?", "form_id": form["id"],
    })).json()
    assert result["generation_status"] == "completed"
    assert {e["file_id"] for e in result["evidence"]} == {-source["id"]}
    assert all(e["role"] == "source" for e in result["evidence"])
    assert (await client.delete(f"/api/projects/alpha/forms/{form['id']}")).status_code == 204
    conversation = (await client.get(
        f"/api/projects/alpha/conversations/{result['conversation_id']}",
    )).json()
    assert conversation["form_reference"] is None
    assert conversation["turns"][0]["form_reference"]["form_id"] == form["id"]


@pytest.mark.anyio
@pytest.mark.parametrize("invalid", ["other_project", "source", "missing"])
async def test_mention_rejects_unavailable_form_before_chat_or_provider(chat, invalid):
    client, _, requests, _ = chat
    if invalid == "other_project":
        form_id = (await upload(client, "beta", name="altro.txt", text="Modulo"))["id"]
    elif invalid == "source":
        form_id = (await client.post("/api/projects/alpha/files", files={
            "file": ("fonte.txt", b"Fonte fattuale"),
        })).json()["id"]
    else:
        form_id = 999999
    with connection() as db:
        before = db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "riassumilo", "form_id": form_id,
    })
    assert response.status_code == 404
    assert requests == []
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0] == before
