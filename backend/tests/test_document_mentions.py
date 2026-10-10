"""Document mentions: real PDF/FTS5/Qdrant and persistence, simulated AI only."""

import hashlib
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document
from test_compilation_conversation import start, step
from test_compilation_sessions import docx, simulate
from test_form_retrieval import chat as chat
from test_form_retrieval import global_source, plan, upload

from app import main, retrieval
from app.db import connection, get_storage_path, init_database
from app.repository import reload_evidence

PDF = (Path(__file__).resolve().parents[2] / "demo-documents/bandi/"
       "minervino-elenco-sia/originali/avviso.pdf")
QUERY = "avviso selezione pubblica elenco professionisti qualificati"


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def source(client, *, project="alpha", name="requisiti.txt", content=None):
    response = await client.post(f"/api/projects/{project}/files", files={
        "file": (name, content or QUERY.encode()),
    })
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.anyio
@pytest.mark.parametrize("planned_target", ["source", "form", "mixed"])
async def test_pdf_mention_scopes_search_and_history_even_if_planner_selects_a_form(
    chat, planned_target,
):
    client, replies, requests, _ = chat
    selected = await source(client, name="istruzioni.pdf", content=PDF.read_bytes())
    # Same names/terms deliberately make filename and unrestricted search unreliable.
    await source(client, name="istruzioni.pdf", content=PDF.read_bytes())
    await source(client, project="beta", name="istruzioni.pdf", content=PDF.read_bytes())
    form = await upload(client, name="istruzioni.txt", text=QUERY)
    await global_source(client, QUERY)
    replies.extend([plan(planned_target, form["id"] if planned_target != "source" else None,
                         QUERY), {
        "answer": "L'avviso riguarda un elenco di professionisti qualificati [1].",
        "citation_ids": [1],
    }])
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "Spiegami cosa richiede il documento e se posso compilarlo",
        "document_id": selected["id"],
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["generation_status"] == "completed", result
    assert result["evidence"] and {e["file_id"] for e in result["evidence"]} == {selected["id"]}
    assert all(e["role"] == "source" and e["project_id"] == "alpha"
               for e in result["evidence"])
    reference = {"document_id": selected["id"], "name": selected["name"], "role": "source"}
    assert result["document_reference"] == reference and result["form_reference"] is None
    assert result["compilation"] is None and len(requests) == 2
    assert '"can_compile": false' in requests[0]["messages"][1]["content"]
    assert "MODULO DA ANALIZZARE" not in requests[1]["messages"][1]["content"]
    init_database()  # Reopening/migrating is idempotent and preserves the selected source.
    cid = result["conversation_id"]
    conversation = (await client.get(f"/api/projects/alpha/conversations/{cid}")).json()
    assert conversation["document_reference"] == reference
    assert conversation["turns"][0]["document_reference"] == reference
    assert (await client.get("/api/projects/alpha/compilation-sessions")).json() == []
    with connection() as db:
        path = db.execute("SELECT storage_path FROM project_files WHERE id=?",
                          (selected["id"],)).fetchone()[0]
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    assert hashlib.sha256((get_storage_path() / path).read_bytes()).digest() == hashlib.sha256(
        PDF.read_bytes(),
    ).digest()
    # Removing a selection clears only current context; deleting preserves turn snapshots.
    replies.append({"intent": "reply", "answer": "Prego!", "queries": [], "target": "source"})
    await client.post("/api/projects/alpha/answer", json={
        "question": "grazie", "conversation_id": cid,
    })
    await client.delete(f"/api/projects/alpha/files/{selected['id']}")
    conversation = (await client.get(f"/api/projects/alpha/conversations/{cid}")).json()
    assert conversation["document_reference"] is None
    assert conversation["turns"][0]["document_reference"] == reference
    assert conversation["turns"][1]["document_reference"] is None


@pytest.mark.anyio
async def test_new_document_reference_consults_docx_then_starts_only_on_compile_intent(chat):
    client, replies, _, _ = chat
    form = (await client.post("/api/projects/alpha/forms", files={
        "file": ("qualsiasi-nome.docx", docx()),
    })).json()
    replies.extend([plan("form", form["id"], "Denominazione sociale Sede legale"), {
        "answer": "Il modulo richiede denominazione e sede legale [1].", "citation_ids": [1],
    }])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "spiegami questo modulo", "document_id": form["id"],
    })).json()
    assert result["generation_status"] == "completed", result
    assert all(e["role"] == "form" and e["file_id"] == form["id"] for e in result["evidence"])
    assert result["document_reference"] == {
        "document_id": form["id"], "name": form["name"], "role": "form",
    }
    assert (await client.get("/api/projects/alpha/compilation-sessions")).json() == []
    replies.append({"intent": "compile", "target": "form", "answer": "", "queries": []})
    compiled = (await client.post("/api/projects/alpha/answer", json={
        "question": "compilalo", "document_id": form["id"],
        "conversation_id": result["conversation_id"],
    })).json()
    assert compiled["compilation"]["action"] == "start", compiled
    sessions = (await client.get("/api/projects/alpha/compilation-sessions")).json()
    assert len(sessions) == 1 and sessions[0]["original_file_id"] == form["id"]


@pytest.mark.anyio
@pytest.mark.parametrize("role", ["source", "form"])
async def test_compile_non_compilable_document_explains_without_substituting_module(chat, role):
    client, replies, _, _ = chat
    module = (await client.post("/api/projects/alpha/forms", files={
        "file": ("modulo.docx", docx()),
    })).json()
    selected = (await source(client) if role == "source" else
                await upload(client, name="testo.txt", text=QUERY))
    replies.append({"intent": "compile", "target": "form", "answer": "", "queries": [],
                    "form_id": module["id"]})
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "compila questo documento", "document_id": selected["id"],
    })).json()
    assert result["generation_status"] == "direct", result
    assert selected["name"] in result["answer"] and "DOCX" in result["answer"]
    assert "modulo.docx" in result["answer"] and result["compilation"] is None
    assert (await client.get("/api/projects/alpha/compilation-sessions")).json() == []


@pytest.mark.anyio
@pytest.mark.parametrize("role", ["source", "form"])
async def test_consultation_and_rejected_compile_preserve_pending_session(chat, monkeypatch, role):
    client, replies, _, _ = chat
    session, _ = await start(chat, content=docx(("Data abilitazione",)))
    simulate(monkeypatch)
    session = await step(client, session)
    assert session["status"] == "WAITING_FOR_USER" and session["chat"]["question"]
    selected = (await source(client) if role == "source" else
                await upload(client, name="altro-modulo.txt", text=QUERY))
    replies.extend([plan(role, selected["id"] if role == "form" else None, QUERY), {
        "answer": "Il documento descrive l'elenco di professionisti [1].", "citation_ids": [1],
    }, {"intent": "compile", "target": "form", "answer": "", "queries": []}])
    with connection() as db:
        before = db.execute("SELECT state_json,version FROM compilation_sessions WHERE id=?",
                            (session["id"],)).fetchone()
        before = tuple(before)
        revisions = db.execute("SELECT COUNT(*) FROM compilation_session_revisions").fetchone()[0]
    for question in ("Spiegami il documento", "compila questo documento"):
        response = await client.post("/api/projects/alpha/answer", json={
            "question": question, "document_id": selected["id"],
            "conversation_id": session["conversation_id"],
            "compilation_session_id": session["id"], "compilation_version": session["version"],
        })
        assert response.status_code == 200, response.text
        assert response.json()["compilation"] is None
        with connection() as db:
            current_row = db.execute(
                "SELECT state_json,version FROM compilation_sessions WHERE id=?", (session["id"],),
            ).fetchone()
            assert tuple(current_row) == before
            count = db.execute("SELECT COUNT(*) FROM compilation_session_revisions").fetchone()[0]
            assert count == revisions
    current = (await client.get(f"/api/projects/alpha/compilation-sessions/{session['id']}")).json()
    assert current["chat"]["question"] == session["chat"]["question"]
    assert current["fields"] == session["fields"]
    assert len((await client.get("/api/projects/alpha/compilation-sessions")).json()) == 1


@pytest.mark.anyio
async def test_docx_without_supported_fields_is_explained_without_starting_session(chat):
    client, replies, _, _ = chat
    document = Document()
    document.add_paragraph("Avviso di selezione pubblica. Requisiti e istruzioni.")
    buffer = BytesIO()
    document.save(buffer)
    selected = (await client.post("/api/projects/alpha/forms", files={
        "file": ("documento.docx", buffer.getvalue()),
    })).json()
    replies.append({"intent": "compile", "target": "form", "answer": "", "queries": []})
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "compilalo", "document_id": selected["id"],
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert "campi compilabili supportati" in result["answer"]
    assert result["generation_status"] == "direct" and result["compilation"] is None
    assert (await client.get("/api/projects/alpha/compilation-sessions")).json() == []


@pytest.mark.anyio
@pytest.mark.parametrize("case", ["other_project", "missing", "conflicting_legacy", "wrong_role"])
async def test_invalid_document_rejected_before_conversation_or_provider(chat, case):
    client, _, requests, _ = chat
    chosen = await source(client, project="beta" if case == "other_project" else "alpha")
    fields = {"document_id": chosen["id"]}
    if case == "missing":
        fields["document_id"] = 999999
    elif case == "conflicting_legacy":
        fields["form_id"] = chosen["id"] + 1
    elif case == "wrong_role":
        with connection() as db:
            db.execute("UPDATE project_files SET kind='template' WHERE id=?", (chosen["id"],))
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "spiegamelo", **fields,
    })
    assert response.status_code == (422 if case == "conflicting_legacy" else 404)
    assert requests == []
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0] == 0


@pytest.mark.anyio
async def test_document_filter_survives_neighbors_and_evidence_reload(chat, monkeypatch):
    client, replies, requests, _ = chat
    selected = await source(client, content=((QUERY + " testo ") * 220).encode())
    other = await source(client, name="altra-fonte.txt")
    await global_source(client, QUERY)
    await upload(client, name="modulo.txt", text=QUERY)
    scoped = retrieval.search_project_evidence("alpha", QUERY, include_neighbors=True,
                                               document_id=selected["id"])
    assert len(scoped) > 1 and {e["file_id"] for e in scoped} == {selected["id"]}
    wrong = retrieval.search_project_evidence("alpha", QUERY, document_id=other["id"])
    assert wrong
    filtered = reload_evidence("alpha", scoped + wrong, document_id=selected["id"])
    assert filtered and all(e["file_id"] == selected["id"] for e in filtered)
    # A stale/misbehaving retriever cannot smuggle a different source into generation.
    monkeypatch.setattr(main, "search_project_evidence", lambda *a, **kw: wrong)
    replies.append(plan("source", query=QUERY))
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "spiegami il documento", "document_id": selected["id"],
    })).json()
    assert result["generation_status"] == "no_evidence"
    assert result["evidence"] == [] and len(requests) == 1


@pytest.mark.anyio
async def test_legacy_reference_is_read_without_backfilling_historical_rows(chat):
    client, replies, _, _ = chat
    form = await upload(client, name="vecchio.txt", text=QUERY)
    replies.append({"intent": "reply", "answer": "Va bene.", "queries": [], "target": "source"})
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "grazie", "form_id": form["id"],
    })).json()
    cid = result["conversation_id"]
    with connection() as db:
        db.execute("ALTER TABLE conversations DROP COLUMN selected_document_id")
        db.execute("ALTER TABLE conversation_turns DROP COLUMN document_reference_json")
    init_database()
    init_database()
    conversation = (await client.get(f"/api/projects/alpha/conversations/{cid}")).json()
    expected = {"document_id": form["id"], "name": form["name"], "role": "form"}
    assert conversation["document_reference"] == expected
    assert conversation["turns"][0]["document_reference"] == expected
    with connection() as db:
        stored = db.execute("SELECT document_reference_json FROM conversation_turns").fetchone()[0]
        assert stored is None
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
