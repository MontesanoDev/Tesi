"""Conditional FORM caption omitted from otherwise valid JSON: no implied applicability."""
import json
from io import BytesIO

import pytest
import test_compilation_resilient_segments as rev2
from docx import Document
from test_compilation_global_sessions import api, provider

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_scope_review as scope
from app.compilation_chat import ClarificationReply
from app.compilation_segments import applicability_states
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]


def form(*, instruction="2.a) da compilare in caso di ADESIONE AL PROGETTO",
         between=None, bold=True):
    doc = Document()
    doc.add_table(rows=1, cols=1).cell(0, 0).paragraphs[0].add_run(instruction).bold = bold
    if between is not None:
        doc.add_paragraph(between)
    doc.add_table(rows=1, cols=1).cell(0, 0).text = "Dato riservato: ____________"
    doc.add_paragraph("Dato indipendente: ____________")
    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


def writer(inp, ids):
    targets = rev2.dato_ids(inp, ids)
    return json.dumps(rev2.envelope(inp, {c: rev2.slot(inp, c) for c in targets}))


@pytest.mark.anyio
@pytest.mark.parametrize("flag", [None, "1"])
async def test_valid_json_cannot_silently_omit_the_conditional_caption(
    api, provider, monkeypatch, flag,
):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    if flag:
        monkeypatch.setenv("MAPI_TABLE_SCOPE_REVISION", flag)
    else:
        monkeypatch.delenv("MAPI_TABLE_SCOPE_REVISION", raising=False)
    s = await rev2.started(api, monkeypatch, form(), rev2.Model({0: [writer], 1: [writer]}))
    response = await rev2.analyze(api, s)
    assert response.status_code == 200, response.text
    s = response.json()
    data = rev2.state_of(s)["global_compilation"]
    conditional = next(cid for cid, c in data["catalog"]["candidates"].items()
                       if c.get("location", {}).get("table_id") == "table:1")
    selected, _, _ = dialogue.export_selection(s)
    if not flag:
        assert conditional in selected
        return
    assert conditional not in selected
    assert (await rev2.draft(api, s, [*selected, conditional])).status_code == 409
    assert selected
    assert (await rev2.draft(api, s, selected)).status_code == 200

