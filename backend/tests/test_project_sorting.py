import sqlite3

import httpx
import pytest

from app.artifacts import (
    ensure_project_artifacts,
    replace_project_artifact,
    seed_markdown_artifacts,
)
from app.db import connection, init_database
from app.main import app
from app.repository import (
    create_project,
    get_or_create_conversation,
    list_projects,
    save_conversation_turn,
    sync_call_fact_review_metrics,
)
from app.schemas import ProjectCreate


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "test.db"
    monkeypatch.setenv("MAPI_DB_PATH", str(path))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    init_database()
    return path


def add_project(title):
    project = create_project(ProjectCreate(title=title, description="Progetto di prova"))
    ensure_project_artifacts(project["id"])
    return project["id"]


def set_date(project_id, timestamp):
    with connection() as db:
        db.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (timestamp, project_id))


def project_date(project_id):
    with connection() as db:
        row = db.execute(
            "SELECT updated_at FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return row[0]


def test_projects_sort_by_modification_not_insert_order_and_keep_milliseconds(database):
    latest = add_project("Ultimo modificato")
    older = add_project("Vecchio modificato")
    newest_insert = add_project("Ultimo inserito")
    set_date(latest, "2026-01-01 12:00:00.900")
    set_date(older, "2026-01-01 12:00:00.100")
    set_date(newest_insert, "2025-12-31 12:00:00")

    assert [project["id"] for project in list_projects()] == [latest, older, newest_insert]
    assert [project["id"] for project in list_projects()] == [latest, older, newest_insert]


def test_new_projects_have_modification_dates_and_ties_are_stable(database):
    first = add_project("Progetto uno")
    second = add_project("Progetto due")
    assert project_date(first)
    assert project_date(second)
    with connection() as db:
        db.execute("UPDATE projects SET created_at = '2020-01-01', updated_at = '2020-01-01'")
    assert [project["id"] for project in list_projects()] == [second, first]


@pytest.mark.anyio
async def test_api_rename_upload_and_edit_move_project_to_top(database):
    changed = add_project("Progetto da aggiornare")
    unchanged = add_project("Progetto recente")
    set_date(unchanged, "2025-02-01 12:00:00")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        set_date(changed, "2025-01-01 12:00:00")
        assert (await client.get("/api/projects")).json()[0]["id"] == unchanged
        response = await client.patch(f"/api/projects/{changed}", json={"title": "Nuovo nome"})
        assert response.status_code == 200
        assert (await client.get("/api/projects")).json()[0]["id"] == changed

        set_date(changed, "2025-01-01 12:00:00")
        response = await client.post(
            f"/api/projects/{changed}/files",
            files={"file": ("nota.txt", b"Contenuto tecnico del progetto.", "text/plain")},
        )
        assert response.status_code == 201
        file_id = response.json()["id"]
        assert (await client.get("/api/projects")).json()[0]["id"] == changed

        set_date(changed, "2025-01-01 12:00:00")
        response = await client.put(
            f"/api/projects/{changed}/files/{file_id}/content",
            json={"content": "Nota tecnica aggiornata."},
        )
        assert response.status_code == 200
        assert (await client.get("/api/projects")).json()[0]["id"] == changed
    assert project_date(unchanged) == "2025-02-01 12:00:00"


@pytest.mark.parametrize("slug", ["template", "draft", "project-facts", "call-facts"])
def test_artifact_saves_update_only_the_owning_project(database, slug):
    changed = add_project("Progetto da modificare")
    unchanged = add_project("Progetto distinto")
    set_date(changed, "2020-01-01 12:00:00")
    set_date(unchanged, "2021-01-01 12:00:00")
    replace_project_artifact(changed, f"{changed}--{slug}", "# Contenuto aggiornato", "Bozza")
    assert project_date(changed) > "2021-01-01"
    assert project_date(unchanged) == "2021-01-01 12:00:00"
    assert list_projects()[0]["id"] == changed


def test_chat_activity_updates_project_but_reading_and_startup_do_not(database):
    project_id = add_project("Progetto conversazione")
    set_date(project_id, "2020-01-01 12:00:00")
    list_projects()
    init_database()
    seed_markdown_artifacts()
    sync_call_fact_review_metrics()
    assert project_date(project_id) == "2020-01-01 12:00:00"
    conversation = get_or_create_conversation(project_id, None, "Chi sei?")
    save_conversation_turn(conversation["id"], {
        "question": "Chi sei?", "answer": "Sono Mapi", "generation_status": "direct",
    })
    assert project_date(project_id) > "2020-01-01 12:00:00"


def test_existing_database_migrates_without_resetting_dates(tmp_path, monkeypatch):
    path = tmp_path / "legacy.db"
    monkeypatch.setenv("MAPI_DB_PATH", str(path))
    with sqlite3.connect(path) as db:
        db.execute("""
            CREATE TABLE projects (
                id TEXT PRIMARY KEY, title TEXT, description TEXT, status TEXT,
                status_tone TEXT, updated_label TEXT, instructions TEXT,
                shared_source_count INTEGER DEFAULT 0, model_count INTEGER DEFAULT 0,
                call_fact_count INTEGER DEFAULT 0, missing_fact_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            INSERT INTO projects (id, title, created_at)
            VALUES ('legacy', 'Progetto esistente', '2020-01-02 12:00:00')
        """)
    init_database()
    assert project_date("legacy") == "2020-01-02 12:00:00"
    set_date("legacy", "2024-06-01 12:00:00")
    init_database()
    assert project_date("legacy") == "2024-06-01 12:00:00"
    created = create_project(
        ProjectCreate(title="Progetto nuovo", description="Su database migrato")
    )
    assert project_date(created["id"])
