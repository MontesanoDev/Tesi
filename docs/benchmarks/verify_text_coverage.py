"""Read-only verification of every generated paragraph, SOURCE proof and ZIP part."""

import hashlib
import json
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn

from app.docx_templates import DRAFT_NOTICE, _paragraph_text, inspect_docx, text_of

ROOT = Path(__file__).resolve().parents[2] / "backend/data/compilation-audit/text-coverage-20261013"


def verify(original, generated, values):
    layout = inspect_docx(original)
    paragraphs = list(layout.document.element.body.iter(qn("w:p")))
    expected = [_paragraph_text(p)[0] for p in paragraphs]
    positions = {p: i for i, p in enumerate(paragraphs)}
    edits = defaultdict(list)
    for cid, value in values.items():
        if cid in layout.slots:
            slot = layout.slots[cid]
            edits[slot.paragraph_index].append((slot.start, slot.end, value))
        else:
            children = layout.cells[cid].findall(qn("w:p"))
            for p in children:
                expected[positions[p]] = ""
            expected[positions[children[0]]] = value
    for index, replacements in edits.items():
        for start, end, value in sorted(replacements, reverse=True):
            expected[index] = expected[index][:start] + value + expected[index][end:]
    body = Document(BytesIO(generated)).element.body
    assert text_of(body[0]) == DRAFT_NOTICE
    body.remove(body[0])
    actual = [_paragraph_text(p)[0] for p in body.iter(qn("w:p"))]
    assert actual == expected
    with ZipFile(BytesIO(original)) as a, ZipFile(BytesIO(generated)) as b:
        assert a.namelist() == b.namelist()
        parts = [name for name in a.namelist() if name != "word/document.xml"]
        assert all(a.read(name) == b.read(name) for name in parts)
    return {"all_paragraphs_match": True, "unselected_positions_unchanged": True,
            "written_texts": len(values), "unchanged_other_zip_parts": len(parts),
            "original_sha256": hashlib.sha256(original).hexdigest()}


def main():
    results = []
    for p in sorted(ROOT.rglob("generated.docx")):
        result = json.loads((p.parent / "result.json").read_text())
        original = (p.parent.parent / "original.docx").read_bytes()
        results.append({"path": str(p.relative_to(ROOT)), **verify(
            original, p.read_bytes(), result["written_texts"])})
    for p in sorted(ROOT.rglob("generated-report.json")):
        if not (p.parent / "analysis/input.json").exists():
            continue  # Prepared command checkpoints use a separate fixture/report.
        report = json.loads(p.read_text())
        original = (p.parent / "template.docx").read_bytes()
        generated = (p.parent / "docx.docx").read_bytes()
        data = json.loads((p.parent / "analysis/input.json").read_text())
        sources = {s["chunk_id"]: s for s in data["sources"]}
        values = {}
        for field in report["fields"]:
            value = field["written_value"]
            if type(value) is bool:
                continue
            values[field["cell_id"]] = value
            if field["provenance"] == "SOURCE":
                assert field["source_evidence"]
                for e in field["source_evidence"]:
                    source = sources[e["chunk_id"]]
                    assert source["role"] == "source"
                    assert e["quote"] in source["content"] and value in e["quote"]
                    assert hashlib.sha256(source["content"].encode()).hexdigest() == e[
                        "content_sha256"]
        results.append({"path": str(p.parent.relative_to(ROOT)),
                        "source_proofs_checked": True, **verify(original, generated, values)})
    (ROOT / "word-verification.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
