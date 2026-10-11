"""FORM typography may differ; SOURCE values and physical anchors stay strict."""

import json
from io import BytesIO

import pytest
from docx import Document

from app.compilation_global import _form_quote, validate_global_proposal
from app.compilation_sources import source_span
from app.docx_templates import inspect_docx


@pytest.mark.parametrize("text,quote,restored", [
    ("Società tecnica ____", "Societa' tecnica", "Società tecnica"),
    ("CITTA' DI RESIDENZA ____", "città di residenza", "CITTA' DI RESIDENZA"),
    ("Telefono ______ Fax________", "Telefono ______ Fax", "Telefono ______ Fax"),
    ("____Identificativo____", "Identificativo", "Identificativo"),
    ("Località\n  operativa: ____", "LOCALITA' operativa:", "Località\n  operativa:"),
    ("Denominazione dell’ente: ____", "Denominazione dell'ente", "Denominazione dell’ente"),
    ("Unità\u00a0territoriale: ____", "unita territoriale", "Unità\u00a0territoriale"),
    ("Numero ______", "Numero __", "Numero ______"),
    ("Strada _________ Località ______", "Strada ___ Località", "Strada _________ Località"),
    ("____Fax_________________", "__Fax____", "____Fax_________________"),
])
def test_form_typography_restores_original_contiguous_text(text, quote, restored):
    assert _form_quote(text, quote) == restored


@pytest.mark.parametrize("text,quote", [
    ("Registro ISO 12345 ____", "Registro ISO 1234"),
    ("Codice X9876 ____", "9876"),
    ("Numero aziendale ____", "Numero personale"),
    ("Codice A-12 ____", "Codice A12"),
    ("sede legale ____", "sede operativa"),
    ("Numero ____", "Numero _"),
    ("Codice AB__12", "Codice AB___12"),
    ("Denominazione dell'ente", "Denominazione dellente"),
    ("ABC", ""),
])
def test_form_matching_does_not_allow_fuzzy_or_partial_words_numbers(text, quote):
    with pytest.raises(ValueError):
        _form_quote(text, quote)


@pytest.mark.parametrize("text,quote", [
    ("Società tecnica", "Societa' tecnica"),
    ("Telefono ______ Fax________", "Telefono ______ Fax"),
    ("____Identificativo____", "Identificativo"),
    ("Registro ISO 12345", "Registro ISO 1234"),
    ("Numero ______", "Numero __ Località"),
])
def test_form_normalization_does_not_weaken_source_span_matching(text, quote):
    with pytest.raises(ValueError):
        source_span(text, quote)


def test_source_components_and_complete_value_can_ground_distinct_form_destinations():
    doc = Document()
    table = doc.add_table(rows=3, cols=2)
    labels = ["Strada", "Località", "Recapito completo"]
    values = ["Via Seta 42", "Padova", "Via Seta 42, 35100 Padova (PD)"]
    for row, label in zip(table.rows, labels, strict=True):
        row.cells[0].text = label
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue())
    source = {"chunk_id": -7, "file_id": -3, "chunk_index": 0,
              "source_name": "recapiti.txt", "role": "source", "scope": "global",
              "category": "company", "project_id": None,
              "content": "Recapito di Alba: Via Seta 42, 35100 Padova (PD)."}
    fields, facts = {}, {}
    for index, (label, value) in enumerate(zip(labels, values, strict=True)):
        fact_id = f"f{index}"
        facts[fact_id] = {"subject": "Alba", "entity": "company", "aspect": "identity",
                          "property": label, "value": value,
                          "evidence": [{"chunk_id": -7, "quote": source["content"]}]}
        fields[f"t0.r{index}.c1"] = {
            "label": label, "kind": "data", "disposition": "value", "fact_id": fact_id,
            "property": label, "conditions": [],
            "form": {"paragraph_id": f"paragraph:{index * 2}", "quote": label},
        }
    result = validate_global_proposal(json.dumps({
        "version": 8, "fields": fields, "facts": facts, "conditions": {}, "bindings": {},
    }), layout, "alpha", [source])
    assert result["counts"] == {"GROUNDED_PROPOSAL": 3}
    assert [f["value"] for f in result["fields"]] == values
    assert all(f["source_evidence"][0]["chunk_id"] == -7 for f in result["fields"])
    assert result["writes"] == result["resolved"] == 0
