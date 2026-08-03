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

    review = await client.get(
        "/api/projects/fondo-riqualificazione-2027/document-review"
    )
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

    async def fake_generation(question, retrieved_evidence):
        assert question == "Quali sono i requisiti tecnici verificabili?"
        assert retrieved_evidence[0]["content"]
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


@pytest.mark.anyio
async def test_upload_rejects_unsupported_documents(client):
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/files",
        files={"file": ("render.png", b"not-an-image", "image/png")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Sono supportati soltanto file PDF e TXT"
