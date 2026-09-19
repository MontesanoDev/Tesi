import json

import httpx
import pytest

from app.artifacts import seed_markdown_artifacts
from app.db import connection, get_knowledge_path, get_storage_path, init_database
from app.draft_generation import GeneratedDraft
from app.fact_extraction import (
    CallFactsExtraction,
    ExtractedFact,
    render_call_facts_markdown,
)
from app.generation import GeneratedAnswer
from app.main import app
from app.schemas import MAX_QUESTION_LENGTH, QuestionRequest
from app.seed import seed_database


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    init_database()
    seed_database()
    seed_markdown_artifacts()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as value:
        yield value


def test_question_limit_accepts_operational_prompts() -> None:
    question = "Q" * 1_500

    assert len(question) > 500
    assert QuestionRequest(question=question).question == question
    assert MAX_QUESTION_LENGTH == 4_000


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

    artifacts = await client.get(f"/api/projects/{project_id}/artifacts")
    assert artifacts.status_code == 200
    assert len(artifacts.json()) == 4
    assert all(
        artifact["kind"] not in {"company_facts", "general_kb"}
        for artifact in artifacts.json()
    )


@pytest.mark.anyio
async def test_rename_project_preserves_identity_and_data(client):
    project_id = "fondo-riqualificazione-2027"
    before = (await client.get(f"/api/projects/{project_id}")).json()

    renamed = await client.patch(
        f"/api/projects/{project_id}",
        json={"title": "  Riqualificazione scuole Puglia  "},
    )

    assert renamed.status_code == 200
    assert renamed.json()["id"] == project_id
    assert renamed.json()["title"] == "Riqualificazione scuole Puglia"
    assert renamed.json()["files"] == before["files"]
    assert (await client.get(f"/api/projects/{project_id}")).json()["title"] == (
        "Riqualificazione scuole Puglia"
    )
    assert any(
        project["title"] == "Riqualificazione scuole Puglia"
        for project in (await client.get("/api/projects")).json()
    )

    invalid = await client.patch(
        f"/api/projects/{project_id}",
        json={"title": "   "},
    )
    assert invalid.status_code == 422
    assert (
        await client.patch("/api/projects/progetto-inesistente", json={"title": "Nuovo nome"})
    ).status_code == 404


@pytest.mark.anyio
async def test_delete_project_removes_local_data_without_reseeding(client):
    created = await client.post(
        "/api/projects",
        json={
            "title": "Progetto da eliminare",
            "description": "Verifica della cancellazione definitiva",
        },
    )
    project_id = created.json()["id"]
    uploaded = await client.post(
        f"/api/projects/{project_id}/files",
        files={"file": ("nota.txt", b"Documento locale del progetto", "text/plain")},
    )
    assert uploaded.status_code == 201

    project_uploads = get_storage_path() / project_id
    project_knowledge = get_knowledge_path() / "projects" / project_id
    assert project_uploads.exists()
    assert project_knowledge.exists()

    deleted = await client.delete(f"/api/projects/{project_id}")
    assert deleted.status_code == 204
    assert (await client.get(f"/api/projects/{project_id}")).status_code == 404
    assert not project_uploads.exists()
    assert not project_knowledge.exists()

    with connection() as db:
        assert db.execute(
            "SELECT COUNT(*) FROM project_files WHERE project_id = ?", (project_id,)
        ).fetchone()[0] == 0
        assert db.execute(
            "SELECT COUNT(*) FROM knowledge_artifacts WHERE project_id = ?", (project_id,)
        ).fetchone()[0] == 0
        assert db.execute(
            "SELECT COUNT(*) FROM knowledge_artifacts WHERE scope = 'global'"
        ).fetchone()[0] == 0

    assert (await client.delete(f"/api/projects/{project_id}")).status_code == 404
    seed_database()
    project_ids = {project["id"] for project in (await client.get("/api/projects")).json()}
    assert project_id not in project_ids


@pytest.mark.anyio
async def test_markdown_artifact_update_is_versioned_and_indexed(client):
    project_id = "fondo-riqualificazione-2027"
    artifacts = await client.get(f"/api/projects/{project_id}/artifacts")
    assert artifacts.status_code == 200
    project_facts = next(
        artifact for artifact in artifacts.json() if artifact["kind"] == "project_facts"
    )
    assert project_facts["editable"] is True

    detail = await client.get(f"/api/projects/{project_id}/artifacts/{project_facts['id']}")
    assert detail.status_code == 200
    assert "# Dati inseriti per il progetto" in detail.json()["content"]

    content = (
        "---\nartifact: project_facts\nscope: project\nstatus: draft\n---\n\n"
        "# Project Facts\n\n## Requisito idraulico\n\n"
        "La verifica di resilienza idraulica è obbligatoria.\n"
    )
    updated = await client.put(
        f"/api/projects/{project_id}/artifacts/{project_facts['id']}",
        json={"content": content},
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == project_facts["version"] + 1
    assert updated.json()["chunk_count"] == 1
    assert updated.json()["content"] == content

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "resilienza idraulica"},
    )
    assert evidence.status_code == 200
    assert evidence.json()["results"][0]["source_name"] == "project-facts.md"

@pytest.mark.anyio
async def test_markdown_artifact_seed_is_idempotent(client):
    project_id = "fondo-riqualificazione-2027"
    before = await client.get(f"/api/projects/{project_id}/artifacts")

    seed_markdown_artifacts()
    seed_markdown_artifacts()

    after = await client.get(f"/api/projects/{project_id}/artifacts")
    assert after.json() == before.json()
    with connection() as db:
        artifact_files = db.execute(
            """
            SELECT COUNT(*) FROM project_files
            WHERE project_id = ? AND kind = 'artifact'
            """,
            (project_id,),
        ).fetchone()[0]
    assert artifact_files == 4


@pytest.mark.anyio
async def test_company_kb_is_indexed_once_and_available_to_every_project(client):
    project_id = "fondo-riqualificazione-2027"
    other_project_id = "adeguamento-sismico-edificio-b"
    uploaded = await client.post(
        "/api/global-knowledge/files",
        data={"category": "company"},
        files={
            "file": (
                "curriculum-mapi.txt",
                (
                    b"Mapi Ingegneria possiede esperienza verificata nella "
                    b"iperconnessione geotecnica zaffiro e nella direzione lavori."
                ),
                "text/plain",
            )
        },
    )
    assert uploaded.status_code == 201
    document = uploaded.json()
    assert document["name"] == "curriculum-mapi.txt"
    assert document["category"] == "company"
    assert document["chunk_count"] == 1

    overview = await client.get("/api/global-knowledge")
    assert overview.status_code == 200
    assert overview.json()["document_count"] == 1
    assert overview.json()["chunk_count"] == 1

    project_documents = await client.get(f"/api/projects/{project_id}/global-knowledge")
    assert project_documents.status_code == 200
    assert project_documents.json()[0]["linked"] is True

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "iperconnessione geotecnica zaffiro"},
    )
    assert evidence.status_code == 200
    assert evidence.json()["results"][0]["source_name"] == "curriculum-mapi.txt"
    assert evidence.json()["results"][0]["file_id"] < 0

    shared = await client.get(
        f"/api/projects/{other_project_id}/evidence",
        params={"q": "iperconnessione geotecnica zaffiro"},
    )
    assert shared.json()["results"][0]["source_name"] == "curriculum-mapi.txt"

    project = await client.get(f"/api/projects/{project_id}")
    company_kb = next(
        source for source in project.json()["knowledge_sources"] if source["name"] == "Company KB"
    )
    assert company_kb["item_count"] == 1
    assert company_kb["detail"] == "1 frammento disponibile"

    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM global_document_chunks").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM project_global_document_links").fetchone()[0] == 0
        assert (
            db.execute(
                "SELECT COUNT(*) FROM project_files WHERE name = 'curriculum-mapi.txt'"
            ).fetchone()[0]
            == 0
        )

    unchanged = await client.put(
        f"/api/projects/{project_id}/global-knowledge/{document['id']}",
        json={"linked": False},
    )
    assert unchanged.status_code == 200
    assert unchanged.json()["linked"] is True

    deleted = await client.delete(f"/api/global-knowledge/files/{document['id']}")
    assert deleted.status_code == 204
    assert (await client.get("/api/global-knowledge")).json()["document_count"] == 0


@pytest.mark.anyio
async def test_global_knowledge_categories_and_markdown_are_explicit(client):
    uploaded = await client.post(
        "/api/global-knowledge/files",
        data={"category": "general"},
        files={
            "file": (
                "norma-tecnica.txt",
                b"Norma tecnica generale: protocollo xilofono normativo ametista.",
                "text/plain",
            )
        },
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["category"] == "general"

    project_id = "fondo-riqualificazione-2027"
    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "xilofono normativo ametista"},
    )
    assert evidence.json()["results"][0]["source_name"] == "norma-tecnica.txt"

    project = await client.get(f"/api/projects/{project_id}")
    general_kb = next(
        source for source in project.json()["knowledge_sources"] if source["name"] == "General KB"
    )
    assert general_kb["item_count"] == 1
    assert general_kb["detail"] == "1 frammento disponibile"

    project_documents = await client.get(f"/api/projects/{project_id}/global-knowledge")
    general_document = next(
        item for item in project_documents.json() if item["id"] == uploaded.json()["id"]
    )
    assert general_document["linked"] is True

    unchanged = await client.put(
        f"/api/projects/{project_id}/global-knowledge/{uploaded.json()['id']}",
        json={"linked": False},
    )
    assert unchanged.status_code == 200
    assert unchanged.json()["linked"] is True

    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM project_global_document_links").fetchone()[0] == 0

    invalid = await client.post(
        "/api/global-knowledge/files",
        data={"category": "facts"},
        files={"file": ("facts.txt", b"Dato aziendale", "text/plain")},
    )
    assert invalid.status_code == 422

    markdown = await client.post(
        "/api/global-knowledge/files",
        data={"category": "company"},
        files={
            "file": (
                "profilo-mapi.md",
                b"# Profilo Mapi\n\nDirettore tecnico: Elisa Romano.",
                "text/markdown",
            )
        },
    )
    assert markdown.status_code == 201
    assert markdown.json()["name"] == "profilo-mapi.md"
    assert markdown.json()["mime_type"] == "text/markdown"
    assert markdown.json()["metadata"].startswith("MD ·")

    overview = await client.get("/api/global-knowledge")
    assert overview.json()["document_count"] == 2
    assert "company_fact_count" not in overview.json()
    assert (await client.get("/api/global-knowledge/company-facts")).status_code == 404

    with connection() as db:
        stored = db.execute(
            """
            SELECT c.content
            FROM global_document_chunks c
            JOIN global_documents d ON d.id = c.document_id
            WHERE d.id = ?
            """,
            (markdown.json()["id"],),
        ).fetchone()[0]
    assert "Direttore tecnico: Elisa Romano" in stored


@pytest.mark.anyio
async def test_global_text_source_can_be_edited_and_reindexed(client):
    project_id = "fondo-riqualificazione-2027"
    uploaded = await client.post(
        "/api/global-knowledge/files",
        data={"category": "company"},
        files={
            "file": (
                "profilo-operativo.md",
                b"# Profilo operativo\n\nCompetenza cromatica zaffiro obsoleta.",
                "text/markdown",
            )
        },
    )
    assert uploaded.status_code == 201
    document_id = uploaded.json()["id"]

    before = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "competenza cromatica zaffiro obsoleta"},
    )
    assert before.json()["results"][0]["source_name"] == "profilo-operativo.md"

    detail = await client.get(f"/api/global-knowledge/files/{document_id}/content")
    assert detail.status_code == 200
    assert "zaffiro obsoleta" in detail.json()["content"]

    corrected_content = (
        "# Profilo operativo\n\n"
        "Certificazione tecnica amaranto verificata per servizi di ingegneria.\n"
    )
    updated = await client.put(
        f"/api/global-knowledge/files/{document_id}/content",
        json={"content": corrected_content},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == corrected_content
    assert updated.json()["chunk_count"] == 1

    obsolete = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "competenza cromatica zaffiro obsoleta"},
    )
    assert obsolete.json()["results"] == []
    corrected = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "certificazione tecnica amaranto verificata"},
    )
    assert corrected.json()["results"][0]["source_name"] == "profilo-operativo.md"

    empty = await client.put(
        f"/api/global-knowledge/files/{document_id}/content",
        json={"content": "   \n"},
    )
    assert empty.status_code == 422

    with connection() as db:
        record = db.execute(
            "SELECT storage_path FROM global_documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        indexed_content = db.execute(
            "SELECT content FROM global_document_chunks WHERE document_id = ?",
            (document_id,),
        ).fetchone()[0]
    stored_path = get_storage_path() / record["storage_path"]
    assert stored_path.read_text(encoding="utf-8") == corrected_content
    assert "amaranto verificata" in indexed_content


@pytest.mark.anyio
async def test_external_markdown_change_is_catalogued_and_reindexed(client):
    project_id = "fondo-riqualificazione-2027"
    artifact_id = f"{project_id}--project-facts"
    before = await client.get(f"/api/projects/{project_id}/artifacts/{artifact_id}")
    external_content = "# Project Facts\n\nLa soglia geotecnica verificabile è pari al 60%.\n"
    path = get_knowledge_path() / "projects" / project_id / "project-facts.md"
    path.write_text(external_content, encoding="utf-8")

    seed_markdown_artifacts()

    after = await client.get(f"/api/projects/{project_id}/artifacts/{artifact_id}")
    assert after.status_code == 200
    assert after.json()["content"] == external_content
    assert after.json()["status"] == "Modifica esterna"
    assert after.json()["version"] == before.json()["version"] + 1
    assert after.json()["chunk_count"] == 1

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "soglia geotecnica"},
    )
    assert evidence.json()["results"][0]["source_name"] == "project-facts.md"


@pytest.mark.anyio
async def test_call_facts_extraction_updates_markdown_and_project_metrics(client, monkeypatch):
    project_id = "fondo-riqualificazione-2027"
    entered_url = f"/api/projects/{project_id}/artifacts/{project_id}--project-facts"
    await client.put(entered_url, json={"content": "# Dati inseriti\n\nFirmatario: Persona demo"})
    entered_before = (await client.get(entered_url)).json()
    uploaded = await client.post(
        f"/api/projects/{project_id}/files",
        files={
            "file": (
                "avviso.txt",
                b"Il Comune presenta la candidatura entro il 15 settembre 2025.",
                "text/plain",
            )
        },
    )
    assert uploaded.status_code == 201

    async def fake_extraction(received_project_id, title, source_chunks):
        assert received_project_id == project_id
        assert title == "Fondo Riqualificazione 2027"
        assert source_chunks[0]["source_name"] == "avviso.txt"
        markdown = render_call_facts_markdown(
            project_id,
            [ExtractedFact("Termine di candidatura", "15 settembre 2025", [1])],
            ["Ora di scadenza"],
            [{"source_name": "avviso.txt", "chunk_index": 0}],
            "deepseek-test",
        )
        return CallFactsExtraction(
            markdown=markdown,
            facts=[ExtractedFact("Termine di candidatura", "15 settembre 2025", [1])],
            missing_information=["Ora di scadenza"],
            evidence_count=1,
            model="deepseek-test",
            total_tokens=72,
        )

    monkeypatch.setattr("app.main.extract_call_facts", fake_extraction)
    response = await client.post(f"/api/projects/{project_id}/call-facts/extract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact"]["status"] == "Estratto"
    assert payload["artifact"]["chunk_count"] > 0
    assert payload["fact_count"] == 1
    assert payload["missing_count"] == 1
    assert payload["evidence_count"] == 1
    assert payload["model"] == "deepseek-test"
    assert (await client.get(entered_url)).json() == entered_before
    from app.document_compilation import load_compilation_sources

    compilation_sources = load_compilation_sources(project_id).selected
    assert any(
        item["source_kind"] == "call_facts" and "15 settembre" in item["content"]
        for item in compilation_sources
    )
    assert any(
        item["source_kind"] == "project_facts" and "Persona demo" in item["content"]
        for item in compilation_sources
    )

    review = await client.get(f"/api/projects/{project_id}/call-facts")
    assert review.status_code == 200
    assert review.json()["pending_count"] == 1
    assert review.json()["verified_count"] == 0
    fact = review.json()["facts"][0]
    assert fact["sources"] == [{"name": "avviso.txt", "fragment": 1}]

    project = await client.get(f"/api/projects/{project_id}")
    assert project.json()["call_fact_count"] == 1
    assert project.json()["missing_fact_count"] == 1
    call_facts_source = next(
        source for source in project.json()["knowledge_sources"]
        if source["name"] == "Dati del progetto"
    )
    assert call_facts_source["item_count"] == 1

    verified = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact['id']}",
        json={"action": "verify", "version": review.json()["artifact"]["version"]},
    )
    assert verified.status_code == 200
    assert verified.json()["verified_count"] == 1
    assert verified.json()["pending_count"] == 0
    assert verified.json()["facts"][0]["status"] == "verified"
    assert verified.json()["artifact"]["status"] == "Disponibile"
    assert verified.json()["artifact"]["chunk_count"] == 1

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "termine candidatura settembre"},
    )
    assert evidence.status_code == 200
    assert any(item["source_name"] == "call-facts.md" for item in evidence.json()["results"])

    stale = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact['id']}",
        json={"action": "discard", "version": review.json()["artifact"]["version"]},
    )
    assert stale.status_code == 409

    edited = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact['id']}",
        json={
            "action": "edit",
            "version": verified.json()["artifact"]["version"],
            "title": "Termine revisionato",
            "value": "Dato revisionato esclusivo",
        },
    )
    assert edited.status_code == 200
    assert edited.json()["facts"][0]["status"] == "pending"
    assert edited.json()["artifact"]["chunk_count"] > 0
    assert edited.json()["facts"][0]["origin"] == "user_corrected"

    discarded = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact['id']}",
        json={"action": "discard", "version": edited.json()["artifact"]["version"]},
    )
    assert discarded.status_code == 200
    assert discarded.json()["discarded_count"] == 1
    assert discarded.json()["artifact"]["chunk_count"] == 0
    assert not any(
        item["source_kind"] == "call_facts"
        for item in load_compilation_sources(project_id).selected
    )

    restored = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact['id']}",
        json={"action": "restore", "version": discarded.json()["artifact"]["version"]},
    )
    assert restored.status_code == 200
    assert restored.json()["facts"][0]["status"] == "pending"
    assert restored.json()["artifact"]["chunk_count"] > 0


@pytest.mark.anyio
async def test_existing_facts_reindex_without_rewriting_legacy_documents(client):
    from app.repository import sync_call_fact_review_metrics

    project_id = "fondo-riqualificazione-2027"
    url = f"/api/projects/{project_id}/artifacts/{project_id}--call-facts"
    content = render_call_facts_markdown(
        project_id, [ExtractedFact("Scadenza esclusiva", "21 ottobre 2026", [1])], [],
        [{"source_name": "bando-demo.pdf", "chunk_index": 1}], "test",
    ).replace("**Stato:** Disponibile", "**Stato:** Da verificare")
    await client.put(url, json={"content": content})
    before = (await client.get(url)).json()
    entered_url = f"/api/projects/{project_id}/artifacts/{project_id}--project-facts"
    entered = (await client.get(entered_url)).json()
    with connection() as db:
        db.execute(
            "DELETE FROM document_chunks WHERE file_id IN "
            "(SELECT file_id FROM project_artifact_links WHERE artifact_id = ?)", (before["id"],)
        )
        db.execute(
            "UPDATE project_files SET chunk_count = 0 WHERE id IN "
            "(SELECT file_id FROM project_artifact_links WHERE artifact_id = ?)", (before["id"],)
        )
    seed_markdown_artifacts()
    seed_markdown_artifacts()
    sync_call_fact_review_metrics()
    after = (await client.get(url)).json()
    assert after["content"] == content
    assert after["version"] == before["version"]
    assert after["chunk_count"] > 0
    assert (await client.get(entered_url)).json() == entered
    review = (await client.get(f"/api/projects/{project_id}/call-facts")).json()
    assert review["verified_count"] == 0
    assert review["pending_count"] == 1
    project = (await client.get(f"/api/projects/{project_id}")).json()
    source = next(s for s in project["knowledge_sources"] if s["name"] == "Dati del progetto")
    assert source["item_count"] == 1
    other = (await client.get(
        "/api/projects/adeguamento-sismico-edificio-b/evidence",
        params={"q": "Scadenza esclusiva ottobre"},
    )).json()
    assert not any("21 ottobre 2026" in item["excerpt"] for item in other["results"])


@pytest.mark.anyio
async def test_extraction_does_not_overwrite_concurrent_corrections(client, monkeypatch):
    from app.artifacts import replace_project_artifact

    project_id = "fondo-riqualificazione-2027"
    artifact_id = f"{project_id}--call-facts"
    await client.post(
        f"/api/projects/{project_id}/files",
        files={"file": ("bando.txt", b"Scadenza: 21 ottobre 2026", "text/plain")},
    )
    original = render_call_facts_markdown(
        project_id, [ExtractedFact("Scadenza", "21 ottobre 2026", [1])], [],
        [{"source_name": "bando.txt", "chunk_index": 0}], "test",
    )

    async def fake_extraction(*_args):
        replace_project_artifact(
            project_id, artifact_id, original.replace("21 ottobre", "22 ottobre"), "Disponibile"
        )
        return CallFactsExtraction(
            markdown=original, facts=[], missing_information=[], evidence_count=1,
            model="test", total_tokens=1,
        )

    monkeypatch.setattr("app.main.extract_call_facts", fake_extraction)
    response = await client.post(f"/api/projects/{project_id}/call-facts/extract")
    assert response.status_code == 409
    stored = (await client.get(f"/api/projects/{project_id}/artifacts/{artifact_id}")).json()
    assert "22 ottobre" in stored["content"]


@pytest.mark.anyio
@pytest.mark.parametrize("recovered", [False, True])
async def test_truncated_extraction_preserves_saved_data_until_complete(
    client, monkeypatch, recovered,
):
    project_id = "fondo-riqualificazione-2027"
    artifact_id = f"{project_id}--call-facts"
    artifact_url = f"/api/projects/{project_id}/artifacts/{artifact_id}"
    entered_url = f"/api/projects/{project_id}/artifacts/{project_id}--project-facts"
    uploaded = await client.post(
        f"/api/projects/{project_id}/files",
        files={"file": ("bando.txt", b"Scadenza: 21 ottobre 2026", "text/plain")},
    )
    assert uploaded.status_code == 201
    original = render_call_facts_markdown(
        project_id, [ExtractedFact("Scadenza precedente", "20 ottobre 2026", [1])], [],
        [{"source_name": "bando.txt", "chunk_index": 0}], "test",
    )
    assert (await client.put(artifact_url, json={"content": original})).status_code == 200
    before = (await client.get(artifact_url)).json()
    entered_before = (await client.get(entered_url)).json()
    project_before = (await client.get(f"/api/projects/{project_id}")).json()

    def indexed_chunks():
        with connection() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM document_chunks WHERE file_id = "
                "(SELECT file_id FROM project_artifact_links WHERE artifact_id = ?) "
                "ORDER BY chunk_index", (artifact_id,),
            ).fetchall()]

    chunks_before = indexed_chunks()
    requests = []

    def provider_response(request):
        requests.append(json.loads(request.content))
        # Even syntactically valid JSON must be rejected when the provider says length.
        content = json.dumps({
            "facts": [{"title": "Scadenza nuova", "value": "21 ottobre 2026", "evidence_ids": [1]}],
            "missing_information": [],
        })
        return httpx.Response(200, json={
            "model": "deepseek-test",
            "choices": [{
                "finish_reason": "stop" if recovered and len(requests) == 2 else "length",
                "message": {"content": content},
            }],
            "usage": {"total_tokens": 81},
        })

    transport = httpx.MockTransport(provider_response)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(
        transport=transport, **kwargs,
    ))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://provider.test")

    response = await client.post(f"/api/projects/{project_id}/call-facts/extract")
    stored = (await client.get(artifact_url)).json()
    assert [item["max_tokens"] for item in requests] == [12_000, 24_000]
    assert requests[0]["messages"] == requests[1]["messages"]
    assert (await client.get(entered_url)).json() == entered_before
    if recovered:
        assert response.status_code == 200
        assert response.json()["total_tokens"] == 162
        assert stored["version"] == before["version"] + 1
        assert "Scadenza nuova" in stored["content"]
        assert "Scadenza precedente" not in stored["content"]
        assert any("Scadenza nuova" in chunk["content"] for chunk in indexed_chunks())
    else:
        assert response.status_code == 502
        assert "ancora troppo lunga" in response.json()["detail"]
        assert stored == before
        assert indexed_chunks() == chunks_before
        assert (await client.get(f"/api/projects/{project_id}")).json() == project_before


@pytest.mark.anyio
async def test_call_facts_extraction_requires_an_indexed_source(client):
    response = await client.post(
        "/api/projects/adeguamento-sismico-edificio-b/call-facts/extract"
    )

    assert response.status_code == 422
    assert "almeno una fonte" in response.json()["detail"]


@pytest.mark.anyio
async def test_draft_generation_uses_extracted_facts_without_manual_verification(
    client, monkeypatch,
):
    project_id = "fondo-riqualificazione-2027"
    call_facts_id = f"{project_id}--call-facts"
    markdown = render_call_facts_markdown(
        project_id,
        [ExtractedFact("Termine di candidatura", "15 settembre 2025", [1])],
        ["Importo richiesto dal proponente"],
        [{"source_name": "avviso.pdf", "chunk_index": 17}],
        "deepseek-test",
    )
    updated = await client.put(
        f"/api/projects/{project_id}/artifacts/{call_facts_id}",
        json={"content": markdown},
    )
    assert updated.status_code == 200

    review = await client.get(f"/api/projects/{project_id}/call-facts")
    fact = review.json()["facts"][0]
    assert fact["status"] == "pending"

    await client.post(
        "/api/global-knowledge/files",
        data={"category": "company"},
        files={
            "file": (
                "profilo-mapi.md",
                b"# Profilo Mapi\n\nMapi Ingegneria supporta enti committenti.",
                "text/markdown",
            )
        },
    )

    async def fake_draft(
        project_title,
        template_markdown,
        company_sources,
        project_facts_markdown,
        available_facts,
    ):
        assert project_title == "Fondo Riqualificazione 2027"
        assert "# Template candidatura" in template_markdown
        assert company_sources[0]["source_name"] == "profilo-mapi.md"
        assert "Mapi Ingegneria" in company_sources[0]["content"]
        assert "Fondo Riqualificazione 2027" in project_facts_markdown
        assert [item.id for item in available_facts] == [fact["id"]]
        assert available_facts[0].status == "pending"
        return GeneratedDraft(
            markdown=(
                "# Candidatura\n\n"
                f"Termine: 15 settembre 2025 [CF:{fact['id']}]\n\n"
                "Importo: [TODO: inserire importo richiesto]"
            ),
            used_fact_ids=[fact["id"]],
            missing_information=["Importo richiesto dal proponente"],
            model="deepseek-test",
            total_tokens=144,
        )

    monkeypatch.setattr("app.main.generate_grounded_draft", fake_draft)
    response = await client.post(f"/api/projects/{project_id}/draft/generate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact"]["kind"] == "output_draft"
    assert payload["artifact"]["status"] == "Da verificare"
    assert payload["artifact"]["chunk_count"] == 0
    assert payload["verified_fact_count"] == 0
    assert payload["available_fact_count"] == 1
    assert payload["used_fact_count"] == 1
    assert "[TODO: inserire importo richiesto]" in payload["artifact"]["content"]
    assert f"[CF:{fact['id']}] Termine di candidatura" in payload["artifact"]["content"]

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "inserire importo richiesto"},
    )
    assert evidence.status_code == 200
    assert all(item["source_name"] != "draft.md" for item in evidence.json()["results"])


@pytest.mark.anyio
@pytest.mark.parametrize("model_output", ["short_reference", "discarded_fact", "mismatch"])
async def test_draft_generation_validates_provider_references_before_saving(
    client, monkeypatch, model_output,
):
    project_id = "fondo-riqualificazione-2027"
    markdown = render_call_facts_markdown(
        project_id,
        [
            ExtractedFact("Scadenza", "15 settembre 2025", [1]),
            ExtractedFact("Importo", "100 euro", [1]),
        ],
        [],
        [{"source_name": "avviso.pdf", "chunk_index": 17}],
        "deepseek-test",
    )
    updated = await client.put(
        f"/api/projects/{project_id}/artifacts/{project_id}--call-facts",
        json={"content": markdown},
    )
    assert updated.status_code == 200
    review = (await client.get(f"/api/projects/{project_id}/call-facts")).json()
    fact_id = review["facts"][0]["id"]
    pending_id = review["facts"][1]["id"]
    verified = await client.patch(
        f"/api/projects/{project_id}/call-facts/{fact_id}",
        json={"action": "verify", "version": review["artifact"]["version"]},
    )
    assert verified.status_code == 200
    discarded = await client.patch(
        f"/api/projects/{project_id}/call-facts/{pending_id}",
        json={"action": "discard", "version": verified.json()["artifact"]["version"]},
    )
    assert discarded.status_code == 200

    draft_url = f"/api/projects/{project_id}/artifacts/{project_id}--draft"
    before = (await client.get(draft_url)).json()

    def provider_response(request):
        assert request.url == httpx.URL("https://provider.test/chat/completions")
        body = json.loads(request.content)
        assert f"Riferimento da copiare: [CF:{fact_id}]" in body["messages"][1]["content"]
        assert pending_id not in body["messages"][1]["content"]
        reference = pending_id if model_output == "discarded_fact" else fact_id
        content = json.dumps({
            "markdown": f"# Candidatura\n\nDato [CF:{reference.removeprefix('cf-')}]",
            "used_fact_ids": [] if model_output == "mismatch" else [fact_id],
            "missing_information": [],
        })
        return httpx.Response(200, json={
            "model": "deepseek-test",
            "choices": [{"message": {"content": content}}],
            "usage": {"total_tokens": 81},
        })

    transport = httpx.MockTransport(provider_response)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(
        transport=transport, **kwargs,
    ))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://provider.test")

    response = await client.post(f"/api/projects/{project_id}/draft/generate")
    persisted = (await client.get(draft_url)).json()
    if model_output == "short_reference":
        assert response.status_code == 200
        assert response.json()["verified_fact_count"] == 1
        assert response.json()["used_fact_count"] == 1
        assert response.json()["total_tokens"] == 81
        assert persisted["version"] == before["version"] + 1
        assert persisted["status"] == "Da verificare"
        assert f"Dato [CF:{fact_id}]" in persisted["content"]
        assert f"[CF:{fact_id}] Scadenza - avviso.pdf, frammento 18" in persisted["content"]
        assert persisted["chunk_count"] == 0
    else:
        assert response.status_code == 502
        expected_error = "esclusi" if model_output == "discarded_fact" else "non coincidono"
        assert expected_error in response.json()["detail"]
        assert persisted == before


@pytest.mark.anyio
async def test_draft_generation_can_use_entered_data_without_extraction(client, monkeypatch):
    async def fake_draft(**kwargs):
        assert kwargs["available_facts"] == []
        assert "Adeguamento" in kwargs["project_facts_markdown"]
        return GeneratedDraft(
            markdown="# Progetto [PROJECT]", used_fact_ids=[],
            missing_information=["Scadenza del bando"], model="test", total_tokens=10,
        )

    monkeypatch.setattr("app.main.generate_grounded_draft", fake_draft)
    response = await client.post(
        "/api/projects/adeguamento-sismico-edificio-b/draft/generate"
    )

    assert response.status_code == 200
    assert response.json()["available_fact_count"] == 0
    assert response.json()["artifact"]["status"] == "Da verificare"


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
        json={"question": "Qual è il colore della moquette?"},
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
@pytest.mark.parametrize("model_content", ["[]", "null", '{"answer":'])
async def test_answer_handles_invalid_model_content_and_can_retry(
    client, monkeypatch, model_content,
):
    project_id = "fondo-riqualificazione-2027"
    uploaded = await client.post(
        f"/api/projects/{project_id}/files",
        files={"file": ("requisito.txt", b"Requisito tecnico verificabile.", "text/plain")},
    )
    assert uploaded.status_code == 201

    contents = iter([
        model_content,
        '{"answer":"Il requisito tecnico e verificabile [1].","citation_ids":[1]}',
    ])

    def provider_response(request):
        assert request.url == httpx.URL("https://provider.test/chat/completions")
        return httpx.Response(200, json={
            "model": "deepseek-test",
            "choices": [{"message": {"content": next(contents)}}],
        })

    transport = httpx.MockTransport(provider_response)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(
        transport=transport, **kwargs,
    ))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://provider.test")

    failed = await client.post(
        f"/api/projects/{project_id}/answer",
        json={"question": "Quale requisito tecnico?"},
    )
    assert failed.status_code == 200
    payload = failed.json()
    assert payload["generation_status"] == "failed"
    assert payload["answer"] is None
    assert payload["notice"].startswith("DeepSeek")
    assert payload["evidence"]
    conversation_id = payload["conversation_id"]

    retried = await client.post(
        f"/api/projects/{project_id}/answer",
        json={"question": "Quale requisito tecnico?", "conversation_id": conversation_id},
    )
    assert retried.status_code == 200
    assert retried.json()["generation_status"] == "completed"
    assert retried.json()["citations"] == [1]
    persisted = await client.get(f"/api/projects/{project_id}/conversations/{conversation_id}")
    assert [turn["generation_status"] for turn in persisted.json()["turns"]] == [
        "failed", "completed",
    ]


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
        conversation_history=None,
    ):
        generation_calls.append(
            {
                "question": question,
                "history": conversation_history or [],
            }
        )
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
async def test_project_text_source_can_be_edited_and_reindexed(client):
    project_id = "fondo-riqualificazione-2027"
    uploaded = await client.post(
        f"/api/projects/{project_id}/files",
        files={
            "file": (
                "nota-operativa.md",
                b"# Nota operativa\n\nLa soglia obsoleta e color zaffiro.",
                "text/markdown",
            )
        },
    )
    assert uploaded.status_code == 201
    file_id = uploaded.json()["id"]
    assert uploaded.json()["mime_type"] == "text/markdown"

    detail = await client.get(f"/api/projects/{project_id}/files/{file_id}/content")
    assert detail.status_code == 200
    assert "zaffiro" in detail.json()["content"]

    corrected_content = (
        "# Nota operativa\n\nLa soglia corretta e color amaranto per il collaudo finale."
    )
    updated = await client.put(
        f"/api/projects/{project_id}/files/{file_id}/content",
        json={"content": corrected_content},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == corrected_content
    assert updated.json()["metadata"].startswith("MD ·")
    assert updated.json()["chunk_count"] == 1

    with connection() as db:
        record = db.execute(
            "SELECT storage_path FROM project_files WHERE id = ?",
            (file_id,),
        ).fetchone()
        indexed_content = db.execute(
            "SELECT content FROM document_chunks WHERE file_id = ?",
            (file_id,),
        ).fetchone()[0]
    stored_content = (get_storage_path() / record["storage_path"]).read_text(
        encoding="utf-8"
    )
    assert stored_content == corrected_content
    assert "amaranto" in indexed_content

    evidence = await client.get(
        f"/api/projects/{project_id}/evidence",
        params={"q": "amaranto collaudo finale"},
    )
    assert evidence.status_code == 200
    assert evidence.json()["results"][0]["source_name"] == "nota-operativa.md"

    pdf_id = (await client.get(f"/api/projects/{project_id}")).json()["files"][0]["id"]
    pdf_editor = await client.get(f"/api/projects/{project_id}/files/{pdf_id}/content")
    assert pdf_editor.status_code == 415


@pytest.mark.anyio
async def test_upload_rejects_unsupported_documents(client):
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/files",
        files={"file": ("render.png", b"not-an-image", "image/png")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Sono supportati soltanto file PDF, TXT e Markdown"
