"""Permanent regression on six frozen original DOCX files, without LLM or DB."""

import hashlib
import json
import random
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

from app.compilation_catalog import build_compilation_catalog
from app.docx_templates import DRAFT_NOTICE, fill_docx, inspect_docx

FIXTURE = Path(__file__).parent / "fixtures/formtext-v1"
MANIFEST = json.loads((FIXTURE / "manifest.json").read_text())
TEXT_IDS = [f"p12.ft{i}" for i in range(15)] + [
    "p18.ft0", "p19.ft0", "p20.ft0", "p21.ft0", "p105.ft0",
]


def read_json(path):
    return json.loads(path.read_text())


def original_case(slug):
    folder = FIXTURE / slug
    return folder, (folder / "original.docx").read_bytes()


def xml_fields(body):
    """Read field results from XML boundaries, independently of parser offsets."""
    records, stack = [], []
    for paragraph in body.iter(qn("w:p")):
        index = 0
        for node in paragraph.iter():
            if node.tag == qn("w:fldChar"):
                kind = node.get(qn("w:fldCharType"))
                if kind == "begin":
                    data = node.find(qn("w:ffData"))
                    text = data is not None and data.find(qn("w:textInput")) is not None
                    stack.append({"text": text, "ordinal": index if text else None,
                                  "nodes": [], "result": False})
                    index += int(text)
                elif kind == "separate" and stack:
                    stack[-1]["result"] = True
                elif kind == "end" and stack:
                    record = stack.pop()
                    records.append(record)
            elif node.tag == qn("w:t") and stack and stack[-1]["result"]:
                stack[-1]["nodes"].append(node)
    assert not stack
    return records


def result_text(record):
    return "".join(n.text or "" for n in record["nodes"])


def without_result_text(body):
    body = deepcopy(body)
    for field in xml_fields(body):
        if field["text"]:
            for node in field["nodes"]:
                node.text = ""
                node.attrib.pop(qn("xml:space"), None)
    return etree.tostring(body)


@pytest.mark.parametrize("slug", MANIFEST["cases"])
def test_six_frozen_catalogs_IDs_and_previous_DOCX_bytes(slug):
    folder, original = original_case(slug)
    for name, digest in MANIFEST["cases"][slug]["files"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
    parsed = inspect_docx(original, require_candidates=False)
    expected = read_json(folder / "catalog.json")
    assert build_compilation_catalog(parsed) == expected
    assert build_compilation_catalog(
        inspect_docx(original, require_candidates=False)
    ) == expected
    writes = read_json(folder / "writes.json")
    first = fill_docx(parsed, writes["text_values"], checkbox_values=writes["checkbox_values"])
    second = fill_docx(parsed, writes["text_values"], checkbox_values=writes["checkbox_values"])
    assert first == second == (folder / "previous-export.docx").read_bytes()
    with ZipFile(BytesIO(original)) as before, ZipFile(BytesIO(first)) as after:
        assert after.testzip() is None
        assert before.namelist() == after.namelist()
        for name in before.namelist():
            if name != "word/document.xml":
                assert before.read(name) == after.read(name)


def test_real_twenty_IDs_survive_reopen_and_XML_serialization_with_duplicate_names():
    _, original = original_case("cesano")
    parsed = inspect_docx(original)
    assert list(parsed.slots) == TEXT_IDS
    names = [node.get(qn("w:val")) for node in parsed.document.element.iter(qn("w:name"))
             if node.getparent().find(qn("w:textInput")) is not None]
    assert names == ["Testo1"] * 20
    encoded = BytesIO()
    parsed.document.save(encoded)
    again = inspect_docx(encoded.getvalue())
    assert list(again.slots) == TEXT_IDS
    assert [(s.start, s.end) for s in parsed.slots.values()] == [
        (s.start, s.end) for s in again.slots.values()
    ]
    catalog = build_compilation_catalog(parsed)
    assert sum(c["type"] == "text" for c in catalog["candidates"].values()) == 20
    assert sum(c["type"] == "checkbox" for c in catalog["candidates"].values()) == 68


@pytest.mark.parametrize("single", [None, *TEXT_IDS])
def test_real_fields_exact_XML_results_preserve_all_unwritten_content(single):
    _, original = original_case("cesano")
    parsed = inspect_docx(original)
    values = {cid: ("ufficio@test.demo" if cid == "p12.ft11" else f"TEST_{cid}_FINE")
              for cid in TEXT_IDS if single is None or cid == single}
    first = fill_docx(parsed, values, checkbox_values={})
    shuffled = list(values.items())
    random.Random(20261019).shuffle(shuffled)
    assert first == fill_docx(parsed, dict(shuffled), checkbox_values={})
    output = Document(BytesIO(first))
    assert output.paragraphs[0].text == DRAFT_NOTICE
    output.element.body.remove(output.element.body[0])
    before_fields = xml_fields(parsed.document.element.body)
    after_fields = xml_fields(output.element.body)
    assert len(before_fields) == len(after_fields) == 88
    assert [f["text"] for f in before_fields] == [f["text"] for f in after_fields]
    text_index = 0
    for before, after in zip(before_fields, after_fields, strict=True):
        if before["text"]:
            cid = TEXT_IDS[text_index]
            assert result_text(after) == values.get(cid, result_text(before))
            text_index += 1
        else:
            # Native checkbox cache/glyphs must also remain unchanged.
            assert result_text(after) == result_text(before)
    assert text_index == 20
    assert without_result_text(parsed.document.element.body) == without_result_text(
        output.element.body
    )
    assert parsed.original == original
