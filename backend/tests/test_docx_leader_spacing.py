"""Spacing at dot leaders, including runs; no changes to values or embedded codes."""

from io import BytesIO

import pytest
from docx import Document

from app.docx_templates import fill_docx, inspect_docx


@pytest.mark.parametrize(('text', 'value', 'expected'), [
    ('albo professionale........ sezione A', 'Ordine territoriale',
     'albo professionale Ordine territoriale sezione A'),
    ('sezione ........della provincia', 'A', 'sezione A della provincia'),
    ('professione………..........; altro', 'Ingegnere', 'professione Ingegnere; altro'),
    ('Sig. ........, nato', 'Ada Neri', 'Sig. Ada Neri, nato'),
    ('Codice IT........', 'AB12', 'Codice ITAB12'),
    ('Codice IT________', 'AB12', 'Codice ITAB12'),
    ('Data ..../..../........', '27', 'Data 27/..../........'),
    ('Numero n........', '123', 'Numero n123'),
    ('(........)', 'A', '(A)'),
])
@pytest.mark.parametrize('split', [False, True])
def test_dot_leader_word_boundaries(text, value, expected, split):
    doc = Document()
    p = doc.add_paragraph()
    if split:
        for char in text:
            p.add_run(char)
    else:
        p.add_run(text)
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue())
    result = fill_docx(layout, {'p0.s0': value})
    assert Document(BytesIO(result)).paragraphs[1].text == expected
    assert layout.original == stream.getvalue()
