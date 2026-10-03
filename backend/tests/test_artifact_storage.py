import sqlite3
from pathlib import Path

import pytest

from app import artifacts
from app.db import connection, get_knowledge_path, init_database
from app.repository import create_project
from app.schemas import ProjectCreate


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    init_database()
    project_id = create_project(ProjectCreate(
        title="Progetto storage", description="Verifica salvataggio artefatti",
    ))["id"]
    artifacts.ensure_project_artifacts(project_id)
    return project_id


def snapshot(project):
    with connection() as db:
        return {
            "artifact": artifacts.get_project_artifact(project, f"{project}--project-facts"),
            "chunks": [tuple(row) for row in db.execute(
                "SELECT * FROM document_chunks WHERE project_id = ? ORDER BY id", (project,),
            )],
            "fts": [tuple(row) for row in db.execute(
                "SELECT rowid, content FROM document_chunks_fts "
                "WHERE project_id = ? ORDER BY rowid",
                (project,),
            )],
        }


@pytest.mark.parametrize("failure", ["metadata", "chunks", "commit", "file_replace"])
def test_failed_update_preserves_artifact_file_metadata_and_search_index(
    project, monkeypatch, failure,
):
    before = snapshot(project)
    if failure == "metadata":
        with connection() as db:
            db.execute("""CREATE TRIGGER fail_artifact_update
                BEFORE UPDATE ON knowledge_artifacts
                BEGIN SELECT RAISE(ABORT, 'simulated metadata failure'); END""")
    elif failure == "chunks":
        original = artifacts._link_artifact

        def fail_after_indexing(*args):
            original(*args)
            raise sqlite3.OperationalError("simulated indexing failure")

        monkeypatch.setattr(artifacts, "_link_artifact", fail_after_indexing)
    elif failure == "commit":
        original_connect = sqlite3.connect

        class FailingCommit(sqlite3.Connection):
            def commit(self):
                if self.in_transaction:
                    raise sqlite3.OperationalError("simulated commit failure")
                return super().commit()

        monkeypatch.setattr(sqlite3, "connect", lambda *args, **kwargs: original_connect(
            *args, **kwargs, factory=FailingCommit,
        ))
    else:
        def fail_replace(*args):
            raise OSError("simulated file replacement failure")

        monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises((sqlite3.Error, OSError), match="simulated"):
        artifacts.replace_project_artifact(
            project, f"{project}--project-facts",
            "Nuovo contenuto da annullare", "Bozza aggiornata",
        )
    assert snapshot(project) == before
    assert not list(get_knowledge_path().rglob("*.tmp"))
