import httpx
import pytest

from app.db import connection, init_database
from app.generation import GeneratedAnswer
from app.main import app
from app.seed import seed_database


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    init_database()
    seed_database()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as value:
        yield value


@pytest.mark.anyio
async def test_project_vertical_slice(client):
    health = await client.get("/api/health")
    assert health.status_code == 200

    projects = await client.get("/api/projects")
    assert projects.status_code == 200
    assert len(projects.json()) == 3

    detail = await client.get("/api/projects/fondo-riqualificazione-2027")
    assert detail.status_code == 200
    assert len(detail.json()["files"]) == 2
    assert detail.json()["call_fact_count"] == 14

    review = await client.get("/api/projects/fondo-riqualificazione-2027/document-review")
    assert review.status_code == 200
    assert review.json()["total_fields"] == 6


@pytest.mark.anyio
async def test_create_project_persists(client):
    response = await client.post(
        "/api/projects",
        json={
            "title": "Nuova candidatura",
            "description": "Prima configurazione del progetto",
        },
    )
    assert response.status_code == 201
    project_id = response.json()["id"]

    persisted = await client.get(f"/api/projects/{project_id}")
    assert persisted.status_code == 200
    assert persisted.json()["title"] == "Nuova candidatura"


@pytest.mark.anyio
async def test_identity_question_bypasses_retrieval_and_generation(client, monkeypatch):
    async def unexpected_generation(*_args, **_kwargs):
        raise AssertionError("DeepSeek non deve essere chiamato per una domanda di sistema")

    monkeypatch.setattr("app.main.generate_grounded_answer", unexpected_generation)
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/answer",
        json={"question": "Chi sei?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "direct"
    assert payload["model"] == "Mapi RAG"
    assert payload["evidence"] == []
    assert payload["citations"] == []
    assert payload["total_tokens"] == 0
    assert payload["answer"].startswith("Sono Mapi RAG")
    assert payload["conversation_id"].startswith("conv-")
    assert payload["turn_id"] > 0

    persisted = await client.get(
        f"/api/projects/fondo-riqualificazione-2027/conversations/{payload['conversation_id']}"
    )
    assert persisted.status_code == 200
    assert persisted.json()["title"] == "Chi sei?"
    assert persisted.json()["turns"][0]["answer"] == payload["answer"]
    assert persisted.json()["turns"][0]["generation_status"] == "direct"

    project = await client.get("/api/projects/fondo-riqualificazione-2027")
    recent = project.json()["conversations"][0]
    assert recent["id"] == payload["conversation_id"]
    assert recent["metadata"] == "Ora · 1 messaggio"


@pytest.mark.anyio
async def test_answer_rejects_a_conversation_from_another_project(client):
    response = await client.post(
        "/api/projects/adeguamento-sismico-edificio-b/answer",
        json={
            "question": "Chi sei?",
            "conversation_id": "requisiti-ammissibilita",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversazione non trovata"


@pytest.mark.anyio
async def test_answer_explains_when_no_evidence_is_available(client, monkeypatch):
    async def unexpected_generation(*_args, **_kwargs):
        raise AssertionError("DeepSeek non deve colmare l'assenza totale di fonti")

    monkeypatch.setattr("app.main.generate_grounded_answer", unexpected_generation)
    response = await client.post(
        "/api/projects/adeguamento-sismico-edificio-b/answer",
        json={"question": "Qual è il recapito del responsabile?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "no_evidence"
    assert payload["answer"].startswith("Non trovo nelle fonti indicizzate")
    assert payload["missing_information"]


@pytest.mark.anyio
async def test_follow_up_reuses_previous_document_evidence(client, monkeypatch):
    previous_evidence = {
        "chunk_id": 7,
        "file_id": 1,
        "source_name": "bando.pdf",
        "chunk_index": 12,
        "excerpt": "Il responsabile del procedimento è indicato nella sezione.",
        "relevance": 4.2,
    }
    history = [
        {
            "question": "Chi è il responsabile?",
            "answer": "Il responsabile è indicato nella fonte [1].",
            "evidence": [previous_evidence],
        }
    ]
    monkeypatch.setattr("app.main.get_conversation_history", lambda _id: history)
    monkeypatch.setattr(
        "app.main.search_project_evidence",
        lambda *_args, **_kwargs: [],
    )

    async def fake_generation(
        question,
        evidence,
        company_facts=None,
        conversation_history=None,
    ):
        assert question == "Come contattarlo?"
        assert evidence[0]["content"] == previous_evidence["excerpt"]
        assert conversation_history == history
        return GeneratedAnswer(
            answer="Le evidenze disponibili non riportano un recapito verificabile [1].",
            citations=[1],
            missing_information=["Recapito del responsabile"],
            model="deepseek-test",
            total_tokens=31,
        )

    monkeypatch.setattr("app.main.generate_grounded_answer", fake_generation)
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/answer",
        json={
            "question": "Come contattarlo?",
            "conversation_id": "requisiti-ammissibilita",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "completed"
    assert payload["evidence"][0]["chunk_id"] == previous_evidence["chunk_id"]
    assert payload["missing_information"] == ["Recapito del responsabile"]


@pytest.mark.anyio
async def test_upload_document_extracts_and_persists_chunks(client, monkeypatch):
    content = ("Requisito tecnico verificabile con fonte documentale. " * 80).encode()
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/files",
        files={"file": ("capitolato-tecnico.txt", content, "text/plain")},
    )

    assert response.status_code == 201
    uploaded = response.json()
    assert uploaded["name"] == "capitolato-tecnico.txt"
    assert uploaded["status"] == "Indicizzato"
    assert uploaded["chunk_count"] >= 2

    detail = await client.get("/api/projects/fondo-riqualificazione-2027")
    assert detail.status_code == 200
    assert detail.json()["files"][-1]["name"] == "capitolato-tecnico.txt"
    assert detail.json()["source_count"] == 13

    with connection() as db:
        persisted_chunks = db.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE file_id = ?",
            (uploaded["id"],),
        ).fetchone()[0]
    assert persisted_chunks == uploaded["chunk_count"]

    evidence = await client.get(
        "/api/projects/fondo-riqualificazione-2027/evidence",
        params={"q": "Quali sono i requisiti tecnici verificabili?"},
    )
    assert evidence.status_code == 200
    assert evidence.json()["results"][0]["source_name"] == "capitolato-tecnico.txt"
    assert "Requisito tecnico" in evidence.json()["results"][0]["excerpt"]

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    not_configured = await client.post(
        "/api/projects/fondo-riqualificazione-2027/answer",
        json={"question": "Quali sono i requisiti tecnici verificabili?"},
    )
    assert not_configured.status_code == 200
    assert not_configured.json()["generation_status"] == "not_configured"
    assert not_configured.json()["evidence"]

    generation_calls = []

    async def fake_generation(
        question,
        retrieved_evidence,
        company_facts=None,
        conversation_history=None,
    ):
        generation_calls.append(
            {
                "question": question,
                "history": conversation_history or [],
            }
        )
        assert retrieved_evidence[0]["content"]
        assert any(fact["key"] == "organization_type" for fact in company_facts or [])
        return GeneratedAnswer(
            answer="Il requisito deve essere verificabile nella fonte [1].",
            citations=[1],
            missing_information=[],
            model="deepseek-test",
            total_tokens=42,
        )

    monkeypatch.setattr("app.main.generate_grounded_answer", fake_generation)
    generated = await client.post(
        "/api/projects/fondo-riqualificazione-2027/answer",
        json={"question": "Quali sono i requisiti tecnici verificabili?"},
    )
    assert generated.status_code == 200
    assert generated.json()["generation_status"] == "completed"
    assert generated.json()["citations"] == [1]
    assert generated.json()["model"] == "deepseek-test"
    assert generation_calls[0]["history"] == []

    conversation_id = generated.json()["conversation_id"]
    follow_up = await client.post(
        "/api/projects/fondo-riqualificazione-2027/answer",
        json={
            "question": "E quali sono?",
            "conversation_id": conversation_id,
        },
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["conversation_id"] == conversation_id
    assert generation_calls[1]["history"][0]["question"] == (
        "Quali sono i requisiti tecnici verificabili?"
    )

    persisted = await client.get(
        f"/api/projects/fondo-riqualificazione-2027/conversations/{conversation_id}"
    )
    assert persisted.status_code == 200
    assert len(persisted.json()["turns"]) == 2
    assert persisted.json()["turns"][0]["citations"] == [1]
    assert "content" not in persisted.json()["turns"][0]["evidence"][0]


@pytest.mark.anyio
async def test_upload_rejects_unsupported_documents(client):
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/files",
        files={"file": ("render.png", b"not-an-image", "image/png")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Sono supportati soltanto file PDF e TXT"
