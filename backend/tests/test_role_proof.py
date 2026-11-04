"""The role stated by the value's own record, when the model cited it elsewhere.

Real Minervino runs on the same data: with the heading «### Ing. Elisa Romano - direttore tecnico»
cited, four director values were written; with the role cited only in another chunk they were
rejected («ruolo e soggetto nello stesso chunk del valore»). The omission depended on what the
model chose to cite. The same validators decide; only the citation is looked for.
"""

import json
from io import BytesIO

import pytest
from docx import Document
from test_compilation_binding_identity import source

from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_dialogue import documented_proposal
from app.compilation_source_reuse import reuse_selected_person
from app.docx_templates import inspect_docx

NAME = "Elisa Romano"
ROLE_LINE = f"- **{NAME}:** direttore tecnico di Aurora S.r.l.; iscritta con numero 8421."
SECTION = (f"### Ing. {NAME} - direttore tecnico\n\n- Nominativo completo: Ing. {NAME}.\n"
           "- Qualifica professionale nello scenario: Ingegnere.\n"
           "- Numero di iscrizione professionale: 8421.\n"
           "- Data di abilitazione e settore dell'albo: non disponibili.\n\n"
           "Il ruolo di direttore tecnico non equivale a una designazione per l'incarico.\n")
OTHER = ("### Ing. Luca Ferri - direttore tecnico\n\n"
         "- Qualifica professionale nello scenario: Geometra.\n")


def proposal(prop, label, value, quote, *, role_chunk=-9, value_chunk=-7):
    return {"version": 12, "uncertain_paragraph_ids": [], "choice_groups": {}, "coverage": [],
            "clarifications": {}, "conditions": {},
            "bindings": {"b": {
                "form": {"paragraph_id": "paragraph:0", "quote": "Direttore tecnico"},
                "required_role": "Direttore tecnico", "source_role": "Direttore tecnico",
                "evidence": [{"chunk_id": role_chunk, "quote": ROLE_LINE}]}},
            "facts": {"f": {"entity": "person", "subject": NAME, "aspect": "professional",
                            "property": prop, "value": value,
                            "evidence": [{"chunk_id": value_chunk, "quote": quote}]}},
            "fields": {"p1.s0": {
                "label": label, "kind": "data", "disposition": "value", "conditions": [],
                "property": prop, "fact_id": "f", "binding_id": "b",
                "form": {"paragraph_id": "paragraph:1", "quote": label + ": [[p1.s0]]"}}}}


def run(label, payload, content, *, revision=1):
    doc = Document()
    doc.add_paragraph("Direttore tecnico")
    doc.add_paragraph(label + ": ________")
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue())
    sources = [source(content, -7), source(ROLE_LINE, -9)]
    audit = validate_global_proposal(json.dumps(payload), layout, "alpha", sources)
    data = {"audit": audit, "catalog": build_global_input(layout, "alpha", sources)["form"],
            "writable_ids": list(layout.slots), "dialogue": {}, "backend_revision": 13,
            **({"role_proof_revision": revision} if revision else {})}
    result = reuse_selected_person(data, layout, "alpha", sources)
    return next(f for f in result["fields"] if f["candidate_id"] == "p1.s0")


CASES = [("qualifica_professionale", "Qualifica professionale", "Ingegnere",
          "- Qualifica professionale nello scenario: Ingegnere."),
         ("numero_iscrizione", "Iscritto all'albo professionale con il n.", "8421",
          "- Numero di iscrizione professionale: 8421."),
         ("nome_cognome", "Nome e cognome", NAME, f"- Nominativo completo: Ing. {NAME}.")]


@pytest.mark.parametrize("prop, label, value, quote", CASES)
def test_a_value_inside_the_persons_own_record_is_recovered_with_that_citation(
    prop, label, value, quote,
):
    field = run(label, proposal(prop, label, value, quote), SECTION)
    assert documented_proposal(field) and field.get("proposed_value") == value
    assert field["factual_recovery"]["method"] == "typed_verified_person_records"
    support = field["subject_binding"]
    assert support["result"] == "literal_match" and not field["validation_errors"]
    assert support["record_attributions"][0]["format"] == "person_role_heading"
    assert any(f"Ing. {NAME} - direttore tecnico" in p["quote"]
               for p in support["source_evidence"])


def test_the_previous_profile_keeps_the_rejection():
    prop, label, value, quote = CASES[0]
    field = run(label, proposal(prop, label, value, quote), SECTION, revision=None)
    assert field["validation_errors"] and not field.get("proposed_value")


@pytest.mark.parametrize("content, quote, value", [
    # Inside another person's section: never attributed to this one.
    (SECTION + OTHER, "- Qualifica professionale nello scenario: Geometra.", "Geometra"),
    # The same person with a different role.
    (f"### Ing. {NAME} - responsabile qualità\n\n- Qualifica professionale: Ingegnere.",
     "- Qualifica professionale: Ingegnere.", "Ingegnere"),
    # The role itself in doubt, or a doubt on the cited line.
    (f"### Ing. {NAME} - direttore tecnico\n\n- Ruolo: cessato il 1 ottobre.\n"
     "- Qualifica professionale: Ingegnere.", "- Qualifica professionale: Ingegnere.",
     "Ingegnere"),
    (f"### Ing. {NAME} - direttore tecnico\n\n- Qualifica professionale: Ingegnere, non attiva.",
     "- Qualifica professionale: Ingegnere, non attiva.", "Ingegnere"),
    # No personal record at all.
    ("- Qualifica professionale: Ingegnere.", "- Qualifica professionale: Ingegnere.",
     "Ingegnere"),
])
def test_without_the_persons_own_record_the_value_stays_rejected(content, quote, value):
    label = "Qualifica professionale"
    field = run(label, proposal("qualifica_professionale", label, value, quote), content)
    assert field["validation_errors"] and not field.get("proposed_value")
