import hashlib
import json
import os
from io import BytesIO
from zipfile import ZipFile

import pytest
from docx import Document
from pypdf import PdfReader

from app import document_compilation as compilation
from app.docx_templates import fill_docx, inspect_docx
from scripts.compile_docx_demo import CASES, ROOT, case_instructions, run


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.parametrize("case", CASES)
def test_demo_cases_have_sources_instructions_and_supported_templates(case):
    config = CASES[case]
    folder = ROOT / "demo-documents/bandi" / config["directory"]
    assert 0 < len(case_instructions(case)) <= 4000
    for relative in config["sources"]:
        reader = PdfReader(folder / relative)
        assert any(page.extract_text().strip() for page in reader.pages)
    layout = inspect_docx((folder / config["template"]).read_bytes())
    assert layout.candidate_ids


def test_trapani_originals_match_manifest_and_writer_preserves_package():
    folder = ROOT / "demo-documents/bandi/trapani-green"
    manifest = json.loads((folder / "fonti.json").read_text())
    for entry in manifest["files"]:
        data = (folder / entry["file"]).read_bytes()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    original = (folder / "originali/manifestazione-interesse.docx").read_bytes()
    layout = inspect_docx(original)
    assert (len(layout.cells), len(layout.slots)) == (54, 61)
    applicant = next(p for p in layout.paragraph_catalog if "Il/la sottoscritto/a" in p["text"])
    field_id = applicant["fields"][0]["id"]
    output = fill_docx(layout, {field_id: "Luca Ferri"})
    assert any(
        "Il/la sottoscritto/a Luca Ferri" in p.text for p in Document(BytesIO(output)).paragraphs
    )

    with ZipFile(BytesIO(original)) as before, ZipFile(BytesIO(output)) as after:
        assert before.namelist() == after.namelist()
        assert all(before.read(name) == after.read(name)
                   for name in before.namelist() if name != "word/document.xml")
    assert (folder / "originali/manifestazione-interesse.docx").read_bytes() == original


@pytest.mark.anyio
async def test_isolated_demo_records_calls_and_preserves_app_environment(tmp_path, monkeypatch):
    database = tmp_path / "existing.db"
    database.write_bytes(b"do not open the app database")
    monkeypatch.setenv("MAPI_DB_PATH", str(database))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "existing-storage"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "existing-knowledge"))
    original_environment = {key: os.environ[key] for key in (
        "MAPI_DB_PATH", "MAPI_STORAGE_PATH", "MAPI_KNOWLEDGE_PATH",
    )}

    async def proposals(prompt):
        payload = json.loads(prompt)
        assert "Trapani" in payload["project_title"]
        assert {s["scope"] for s in payload["sources"]} == {"company", "project", "user"}
        return json.dumps({"fields": [{
            "cell_id": field_id, "label": field_id, "entity": "other", "kind": "data",
            "status": "needs_review", "value": None, "evidence": [],
            "reason": "Risposta simulata per verificare il percorso, non la qualita AI",
        } for field_id in payload["target_ids"]], "warnings": []}), "test", 1

    monkeypatch.setattr(compilation, "request_field_proposals", proposals)
    output = tmp_path / "audit"
    await run(output, ROOT / "demo-documents/generalita-mapi.md", "trapani")
    assert all(os.environ[key] == value for key, value in original_environment.items())
    assert database.read_bytes() == b"do not open the app database"
    assert not (tmp_path / "existing-storage").exists()
    assert not (tmp_path / "existing-knowledge").exists()
    assert json.loads((output / "result.json").read_text())["success"]
    report = json.loads((output / "report.json").read_text())
    assert report["execution"]["completed_batches"] == 4
    assert len(list(output.glob("batch-*.prompt.json"))) == 4
    assert len(list(output.glob("batch-*.response.json"))) == 4
    assert (output / "bozza.docx").is_file()
