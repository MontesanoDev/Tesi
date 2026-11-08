"""A valid SOURCE value cannot silently choose a printed alternative (offline API)."""
import json
from io import BytesIO

import pytest
import test_compilation_resilient_segments as rev2
from docx import Document
from test_compilation_global_sessions import api, provider

from app import compilation_global_dialogue as dialogue
from app import compilation_profile

__all__ = ["api", "provider"]
OPTION = "[] utilizzare i dati del soggetto delegato:"


def form():
    doc = Document()
    doc.add_paragraph("[ ] utilizzare i dati del richiedente;")
    doc.add_paragraph("OPPURE")
    doc.add_paragraph(OPTION)
    doc.add_paragraph("")
    doc.add_paragraph("Dato del delegato: ____________")
    doc.add_paragraph("")
    doc.add_paragraph("Dato indipendente: ____________")
    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


def activate(monkeypatch, enabled):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    original = compilation_profile.new_session_flags
    monkeypatch.setattr(compilation_profile, "new_session_flags", lambda: {
        **original(), **({"form_option_scope_revision": 1} if enabled else {})})


def writer(inp, ids):
    return json.dumps(rev2.envelope(inp, {c: rev2.slot(inp, c)
                                        for c in rev2.dato_ids(inp, ids)}))


@pytest.mark.anyio
@pytest.mark.parametrize("enabled", [False, True])
async def test_valid_source_and_json_do_not_choose_an_omitted_option(
    api, provider, monkeypatch, enabled,
):
    activate(monkeypatch, enabled)
    s = await rev2.started(api, monkeypatch, form(), rev2.Model({0: [writer], 1: [writer]}))
    response = await rev2.analyze(api, s)
    assert response.status_code == 200, response.text
    s = response.json()
    selected, _, _ = dialogue.export_selection(s)
    assert "p6.s0" in selected  # Independent, documented data.
    export = await rev2.draft(api, s, ["p4.s0", "p6.s0"])
    if enabled:
        assert export.status_code == 409, export.text
        assert "p4.s0" not in selected
        assert (await rev2.draft(api, s, selected)).status_code == 200
    else:
        assert export.status_code == 200, export.text
