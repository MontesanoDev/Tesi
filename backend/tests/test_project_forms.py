from io import BytesIO
from pathlib import Path

import httpx
import pytest
from docx import Document
from pypdf import PdfWriter

from app import project_forms
from app.db import connection, get_storage_path, init_database
from app.fact_extraction import load_project_source_chunks
from app.main import app
from app.repository import create_project, delete_project
from app.schemas import ProjectCreate


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    init_database()
    for title in ("Primo", "Secondo"):
        create_project(ProjectCreate(title=title, description="Progetto di prova"))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test",
    ) as result:
        yield result


def document_bytes(suffix):
    if suffix in ("txt", "md"):
        return "Domanda di partecipazione\r\nRagione sociale: ___\r\nCittà: ___".encode()
    output = BytesIO()
    if suffix == "docx":
        doc = Document()
        doc.add_paragraph("Un modulo senza posizioni compilabili e comunque archiviabile.")
        doc.save(output)
    else:
        pdf = PdfWriter()
        pdf.add_blank_page(width=200, height=200)
        pdf.write(output)
    return output.getvalue()


@pytest.mark.anyio
@pytest.mark.parametrize("suffix", ["docx", "pdf", "txt", "md"])
async def test_archive_preserves_original_without_indexing_or_compiling(client, suffix):
    original = document_bytes(suffix)
    response = await client.post(
        "/api/projects/primo/forms", files={"file": (f"domanda.{suffix}", original)},
    )
    assert response.status_code == 201, response.text
    form = response.json()
    assert form["kind"] == "form"
    assert form["status"] == "Caricato"
    assert form["chunk_count"] == 0
    assert "storage_path" not in form
    assert (await client.get("/api/projects/primo/forms")).json() == [form]
    project = (await client.get("/api/projects/primo")).json()
    assert project["files"] == [form]
    assert project["source_count"] == 0
    assert project["model_count"] == 1
    downloaded = await client.get(f"/api/projects/primo/forms/{form['id']}/download")
    assert downloaded.status_code == 200
    assert downloaded.content == original
    assert "attachment" in downloaded.headers["content-disposition"]
    assert not load_project_source_chunks("primo")
    with connection() as db:
        for table in ("document_chunks", "document_chunks_fts", "document_compilations"):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


@pytest.mark.anyio
async def test_duplicate_names_are_independent_and_removal_preserves_other_forms(client):
    rows = []
    for content in (b"Primo originale", b"Secondo originale"):
        rows.append((await client.post(
            "/api/projects/primo/forms", files={"file": ("domanda.txt", content)},
        )).json())
    assert rows[0]["id"] != rows[1]["id"]
    assert (await client.delete(f"/api/projects/primo/forms/{rows[0]['id']}")).status_code == 204
    assert (await client.get("/api/projects/primo/forms")).json() == [rows[1]]
    assert (await client.get(
        f"/api/projects/primo/forms/{rows[1]['id']}/download",
    )).content == b"Secondo originale"
    assert (await client.get("/api/projects/primo")).json()["model_count"] == 1
    assert len(list(get_storage_path().rglob("*.txt"))) == 1


@pytest.mark.anyio
async def test_project_and_source_endpoints_cannot_access_or_modify_other_roles(client):
    form = (await client.post(
        "/api/projects/primo/forms", files={"file": ("domanda.md", b"Nome: ___")},
    )).json()
    source = (await client.post(
        "/api/projects/primo/files", files={"file": ("fonte.txt", b"Dato aziendale")},
    )).json()
    for url in (
        f"/api/projects/secondo/forms/{form['id']}",
        f"/api/projects/primo/forms/{source['id']}",
    ):
        assert (await client.get(f"{url}/download")).status_code == 404
        assert (await client.delete(url)).status_code == 404
    assert (await client.delete(f"/api/projects/primo/files/{form['id']}")).status_code == 404
    url = f"/api/projects/primo/files/{form['id']}/content"
    assert (await client.get(url)).status_code == 404
    assert (await client.put(url, json={"content": "Alterato"})).status_code == 404
    assert (await client.get(f"/api/projects/primo/forms/{form['id']}/download")).content == (
        b"Nome: ___"
    )
    assert len(load_project_source_chunks("primo")) == 1


@pytest.mark.anyio
@pytest.mark.parametrize("name, content, code", [
    ("modulo.exe", b"invalid", 415),
    ("vuoto.txt", b"", 422),
    ("spazi.md", b"  \n", 422),
    ("binario.txt", b"\xff\x00", 422),
    ("falso.docx", b"invalid", 422),
    ("falso.pdf", b"invalid", 422),
    ("x" * 181 + ".txt", b"Nome: ___", 422),
])
async def test_invalid_uploads_leave_no_records_or_files(client, name, content, code):
    response = await client.post("/api/projects/primo/forms", files={"file": (name, content)})
    assert response.status_code == code, response.text
    assert (await client.get("/api/projects/primo/forms")).json() == []
    assert not list(get_storage_path().rglob("*.*"))


@pytest.mark.anyio
async def test_size_limit_and_missing_project(client, monkeypatch):
    monkeypatch.setattr(project_forms, "MAX_FILE_SIZE", 10)
    response = await client.post(
        "/api/projects/primo/forms", files={"file": ("modulo.txt", b"x" * 11)},
    )
    assert response.status_code == 413
    assert (await client.get("/api/projects/assente/forms")).status_code == 404
    assert (await client.post(
        "/api/projects/assente/forms", files={"file": ("modulo.txt", b"ok")},
    )).status_code == 404
    assert not list(get_storage_path().rglob("*.*"))


@pytest.mark.anyio
async def test_failed_save_rolls_back_file_and_database(client, monkeypatch):
    def fail(*args):
        raise OSError("disk failure")
    monkeypatch.setattr(project_forms, "touch_project", fail)
    result = await client.post(
        "/api/projects/primo/forms", files={"file": ("modulo.txt", b"Nome: ___")},
    )
    assert result.status_code == 500
    assert (await client.get("/api/projects/primo/forms")).json() == []
    assert not list(get_storage_path().rglob("*.txt"))


@pytest.mark.anyio
async def test_project_deleted_during_validation_cannot_leave_orphan_file(client, monkeypatch):
    original = project_forms._validate_file

    def delete_during_validation(data, suffix):
        original(data, suffix)
        delete_project("primo")

    monkeypatch.setattr(project_forms, "_validate_file", delete_during_validation)
    response = await client.post(
        "/api/projects/primo/forms", files={"file": ("modulo.txt", b"Nome: ___")},
    )
    assert response.status_code == 404
    assert not list(get_storage_path().rglob("*.txt"))


@pytest.mark.anyio
async def test_failed_removal_is_retriable_and_project_deletion_cleans_forms(client, monkeypatch):
    form = (await client.post(
        "/api/projects/primo/forms", files={"file": ("modulo.txt", b"Originale")},
    )).json()
    with monkeypatch.context() as patch:
        def fail(*args, **kwargs):
            raise OSError("File occupato")
        patch.setattr(Path, "unlink", fail)
        assert (await client.delete(f"/api/projects/primo/forms/{form['id']}")).status_code == 500
    assert (await client.get("/api/projects/primo/forms")).json() == [form]
    assert (await client.get(f"/api/projects/primo/forms/{form['id']}/download")).content == (
        b"Originale"
    )
    assert (await client.delete("/api/projects/primo")).status_code == 204
    assert not (get_storage_path() / "primo").exists()
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM project_files").fetchone()[0] == 0
