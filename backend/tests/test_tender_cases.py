import hashlib
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document

from app.docx_templates import fill_docx, inspect_docx

ROOT = Path(__file__).resolve().parents[2]


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
