"""A signature line is never the signatory name (E2E campaign, 29 Oct).

Benchmark compilazione V1: «Firma del sottoscrittore: ____» was taken for the signatory name;
the name question was asked on the signature line, then again on the real name field.
"""

from docx import Document
from test_compilation_catalog import catalog

from app.compilation_signatory_form import signatory_groups


def test_a_signature_line_is_never_the_signatory_name():
    doc = Document()
    doc.add_paragraph("Data di sottoscrizione della domanda ____________")
    doc.add_paragraph("Firma del sottoscrittore: __________")
    assert signatory_groups(catalog(doc)) == []
    doc = Document()
    doc.add_paragraph("Il sottoscritto ____________")
    assert [g["targets"] for g in signatory_groups(catalog(doc))] == [{"p0.s0": "name"}]
