"""A body option governs the next table only if it announces it (E2E campaign, 29 Oct).

Benchmark compilazione V1: «☐ Dichiaro il possesso della ISO 9001» was followed by the
unrelated CCIAA table: the option region governed it, the declaration authorization bundled
the CCIAA data, and the USER's refusal of the declaration left three documented values empty.
"""

from docx import Document
from test_compilation_catalog import catalog
from test_compilation_option_authorization import CLAUSE, cciaa_doc

from app.compilation_option_regions import option_regions


def governed(cat):
    return {cid for region in option_regions(cat) for cid in region["field_ids"]}


def tables(cat, ids):
    return {cat["candidates"][cid]["location"].get("table_id") for cid in ids}


def test_a_complete_declaration_does_not_govern_the_next_table():
    doc = Document()
    doc.add_paragraph("☐ Dichiaro il possesso della ISO 9001")
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Iscrizione CCIAA"
    table.rows[1].cells[0].text = "Numero iscrizione REA"
    cat = catalog(doc)
    assert "table:0" not in tables(cat, governed(cat))


def test_an_option_announcing_its_data_still_governs_the_table():
    cat = catalog(cciaa_doc())
    assert CLAUSE.endswith("seguenti dati:")
    assert "table:0" in tables(cat, governed(cat))
    doc = Document()  # «… avente la seguente» (Minervino capacity option), without a colon.
    doc.add_paragraph("☐ Legale rappresentante di società di ingegneria avente la seguente")
    doc.add_table(rows=1, cols=2).rows[0].cells[0].text = "Denominazione"
    cat = catalog(doc)
    assert "table:0" in tables(cat, governed(cat))
