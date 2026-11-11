"""The same calendar date written twice in SOURCE is one documented value, not a choice.

Manual Minervino test 2 (29 Oct): the partner table gave «18/05/2015» and the narrative
«18 maggio 2015» for the same registration; the backend treated them as unselected
alternatives, the field lost its value and the user was asked for a documented date.
"""

import json
from io import BytesIO

import pytest
from docx import Document

from app.compilation_global import validate_global_proposal
from app.docx_templates import inspect_docx


def case(other):
    doc = Document()
    doc.add_heading("Dati dell'organizzazione", 1)
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Iscrizione dal"
    table.cell(1, 0).text = "Iscrizione del direttore tecnico dal"
    stream = BytesIO()
    doc.save(stream)
    content = f"Alba: iscritta dal 18/05/2015; nella relazione: iscritta dal {other}."
    source = {"chunk_id": -7, "file_id": -3, "chunk_index": 0, "source_name": "profilo.txt",
              "role": "source", "scope": "global", "category": "company",
              "project_id": None, "content": content}
    facts = {key: {"subject": "Alba", "entity": "company", "aspect": "identity",
                   "property": "data iscrizione", "value": value,
                   "evidence": [{"chunk_id": -7, "quote": content}]}
             for key, value in (("a", "18/05/2015"), ("b", other))}
    fields = {"t0.r0.c1": {"label": "Iscrizione dal", "kind": "data", "disposition": "value",
                           "property": "data iscrizione", "fact_id": "a", "conditions": [],
                           "form": {"paragraph_id": "paragraph:1", "quote": "Iscrizione dal"}},
              # As in test 2, the other wording proves a second field of the same person.
              "t0.r1.c1": {"label": "Iscrizione del direttore tecnico dal", "kind": "data",
                           "disposition": "value", "property": "data iscrizione",
                           "fact_id": "b", "conditions": [],
                           "form": {"paragraph_id": "paragraph:3",
                                    "quote": "Iscrizione del direttore tecnico dal"}}}
    payload = {"version": 6, "conditions": {}, "fields": fields, "facts": facts}
    return validate_global_proposal(json.dumps(payload), inspect_docx(stream.getvalue()),
                                    "alpha", [source])["fields"][0]


@pytest.mark.parametrize("other", ["18 maggio 2015", "18.5.2015", "18-05-2015"])
def test_the_same_date_in_another_format_keeps_the_documented_value(other):
    field = case(other)
    assert field["validation"] == "GROUNDED_PROPOSAL"
    assert field["value"] == "18/05/2015" and field["fact_id"] == "a"
    assert "alternatives" not in field


@pytest.mark.parametrize("other", ["19 maggio 2015", "18/05/2016", "maggio 2015"])
def test_a_different_or_partial_date_is_still_a_choice_for_the_user(other):
    field = case(other)
    assert field["validation"] == "REVIEW_REQUIRED"
    assert field["review_kind"] == "unselected_alternatives"
    assert field["value"] is field["written_value"] is field["fact_id"] is None
