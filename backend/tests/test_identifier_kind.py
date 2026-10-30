"""A VAT number is not a tax code (stabilization, 30 Oct).

E2E campaign, real Catanzaro runs: «IT01234567890», the company's partita IVA in SOURCE, was
written in the «Codice fiscale» field. An Italian tax code never carries the IT prefix, so the
validator now rejects that destination; a field asking for either identifier is unchanged.
"""

from io import BytesIO

import pytest
from docx import Document

from app.docx_templates import field_value_error, inspect_docx


def layout():
    doc = Document()
    doc.add_paragraph("Codice ____________")
    stream = BytesIO()
    doc.save(stream)
    return inspect_docx(stream.getvalue(), require_candidates=False)


@pytest.mark.parametrize("label", ["Codice fiscale", "Codice fiscale dell'impresa", "C.F."])
def test_a_vat_number_is_rejected_in_a_tax_code_field(label):
    assert field_value_error(layout(), "p0.s0", "IT01234567890", label=label)[0] == (
        "identifier_kind_mismatch")


@pytest.mark.parametrize("label,value", [("Partita IVA", "IT01234567890"),
                                         ("Codice fiscale / P.IVA", "IT01234567890"),
                                         ("Codice fiscale", "01234567890"),
                                         ("Codice fiscale", "MNTLRD82S14E506X")])
def test_compatible_identifiers_are_unchanged(label, value):
    assert field_value_error(layout(), "p0.s0", value, label=label) is None
