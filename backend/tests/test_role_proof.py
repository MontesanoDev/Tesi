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
from app.compilation_role_records import (
    binding_value_support,
    linked_person_support,
    own_record_support,
    same_typed_value,
)
from app.compilation_segments import _mark_conflicts
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


# Real Minervino runs: the same person's table row was joined or not depending on the word the model
# used for the property, or on having cited the role in two records instead of one.
HEADING = "### Ing. Elisa Romano - direttore tecnico"


def role_section(number="8421", cf=""):
    return (f"{HEADING}\n\n- Nominativo completo: Ing. {NAME}.\n"
            "- Ordine professionale simulato: Ordine degli Ingegneri di Bari.\n"
            f"- Numero di iscrizione professionale simulato: {number}.\n{cf}")


ROW = (f"| {NAME} | 40% | Ingegnere | Ordine degli Ingegneri di Bari | A | Bari (BA) | "
       "18/05/2015 | 8421 | RMNLSI85C47A662Y |")
TABLE = ("## Soci\n\n| Persona | Quota | Qualifica professionale | Albo | Sezione | Provincia | "
         "Iscrizione dal | N. iscrizione | Codice fiscale dimostrativo |\n"
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + ROW + "\n")
LINE = (f"- **{NAME}:** direttore tecnico di Aurora S.r.l.; ingegnere, Ordine degli Ingegneri di "
        "Bari, sezione A, iscritta dal 18 maggio 2015 con numero 8421.")


def linked(prop, value, *, typed=True, role_chunks=None):
    chunks = {-3: role_section(), -16: TABLE} | (role_chunks or {})
    source_map = {c: {"chunk_id": c, "content": text, "category": "company"}
                  for c, text in chunks.items()}
    quotes = {-3: HEADING, -17: LINE}
    binding = {"source_role": "direttore tecnico", "source_evidence": [
        {"chunk_id": c, "quote": quotes.get(c, HEADING)} for c in chunks if c != -16]}
    fact = {"property": prop, "subject": NAME, "value": value, "source_evidence": [
        {"chunk_id": -16, "quote": ROW, "category": "company"}]}
    return linked_person_support(binding, fact, source_map, verified_properties=True, typed=typed)


@pytest.mark.parametrize("prop, value", [
    ("nome_cognome", NAME), ("albo_professionale", "Ordine degli Ingegneri di Bari"),
    ("data_iscrizione", "18/05/2015"), ("sezione_albo", "A"), ("nome", NAME),
    ("qualifica_professionale", "Ingegnere")])
def test_the_word_chosen_for_a_property_does_not_decide_the_join(prop, value):
    support = linked(prop, value)
    assert support and support["identity_support"]["method"] == "professional_registration"


@pytest.mark.parametrize("prop, value", [
    ("nome_cognome", NAME), ("albo_professionale", "Ordine degli Ingegneri di Bari"),
    ("data_iscrizione", "18/05/2015")])
def test_the_previous_profile_keeps_those_words_unjoined(prop, value):
    assert linked(prop, value, typed=False) is None


def test_a_province_without_its_abbreviation_is_the_same_cell():
    assert linked("provincia", "Bari")["value_support"]["comparison"] == "province_abbreviation"
    assert linked("provincia_iscrizione", "Bari (BA)")
    assert linked("provincia", "Lecce") is None
    assert linked("provincia", "Bari", typed=False) is None


def test_a_property_outside_the_typed_ones_is_never_joined():
    assert linked("quota_societaria", "40%") is None
    assert linked("ruolo", "direttore tecnico") is None


def test_a_value_not_in_the_cell_of_its_property_is_not_joined():
    assert linked("data_iscrizione", "8421") is None
    assert linked("albo_professionale", "Ordine degli Architetti di Bari") is None


def test_two_records_of_the_same_registration_are_more_proof_not_a_doubt():
    assert linked("nome", NAME, role_chunks={-17: LINE})
    assert linked("sezione_albo", "A", role_chunks={-17: LINE})
    assert linked("nome", NAME, typed=False, role_chunks={-17: LINE}) is None


def test_two_registrations_under_one_name_stay_unjoined():
    other = LINE.replace("numero 8421", "numero 9999")
    assert linked("nome", NAME, role_chunks={-17: other}) is None


def test_another_registration_in_the_role_record_is_not_joined_to_the_row():
    assert linked("nome", NAME, role_chunks={-3: role_section(number="9999")}) is None


# Real Minervino runs again: a fact cited in the table row and in the person's own line, or in the
# role record and in that line, was refused because of the citation more.
def cited_twice(prop, value, line=LINE, *, typed=True):
    chunks = {-3: role_section(), -16: TABLE, -17: line}
    source_map = {c: {"chunk_id": c, "content": text, "category": "company"}
                  for c, text in chunks.items()}
    binding = {"source_role": "direttore tecnico", "source_evidence": [
        {"chunk_id": -3, "quote": HEADING}]}
    fact = {"property": prop, "subject": NAME, "value": value, "source_evidence": [
        {"chunk_id": -16, "quote": ROW, "category": "company"},
        {"chunk_id": -17, "quote": line, "category": "company"}]}
    return linked_person_support(binding, fact, source_map, verified_properties=True, typed=typed)


def test_a_value_cited_in_the_row_and_in_the_persons_line_is_joined():
    assert cited_twice("sezione", "A")
    assert cited_twice("numero_iscrizione", "8421")
    assert cited_twice("sezione", "A", typed=False) is None


def test_a_line_with_another_registration_stops_the_join():
    assert cited_twice("sezione", "A", LINE.replace("numero 8421", "numero 9999")) is None


def test_a_line_of_another_person_stops_the_join():
    other = LINE.replace(NAME, "Luca Ferri")
    assert cited_twice("sezione", "A", other) is None


def own_and_line(line=LINE):
    source_map = {-3: {"chunk_id": -3, "content": role_section(), "category": "company"},
                  -17: {"chunk_id": -17, "content": line, "category": "company"}}
    binding = {"source_role": "direttore tecnico", "source_evidence": [
        {"chunk_id": -3, "quote": HEADING}, {"chunk_id": -17, "quote": line}]}
    fact = {"property": "numero_iscrizione_albo", "subject": NAME, "value": "8421",
            "source_evidence": [
                {"chunk_id": -3, "quote": "- Numero di iscrizione professionale simulato: 8421."},
                {"chunk_id": -17, "quote": line}]}
    return own_record_support(binding, fact, source_map)


def test_the_role_record_and_the_persons_line_together_are_supported():
    assert own_and_line()


def test_a_line_of_another_person_gives_no_support_to_the_role_record():
    assert own_and_line(LINE.replace(NAME, "Luca Ferri")) is None


def test_a_line_stating_another_role_gives_no_support():
    assert own_and_line(LINE.replace("direttore tecnico", "responsabile qualità")) is None


def test_the_word_for_a_property_does_not_decide_the_role_row_either():
    title = "## 3. Soci della società al 15 ottobre 2026"
    table = TABLE.replace("## Soci", title)
    source_map = {-16: {"chunk_id": -16, "content": table, "category": "company"}}
    binding = {"source_role": "socio", "source_evidence": [
        {"chunk_id": -16, "quote": title}, {"chunk_id": -16, "quote": ROW}]}
    fact = {"property": "ordine", "subject": NAME, "value": "Ordine degli Ingegneri di Bari",
            "source_evidence": [{"chunk_id": -16, "quote": ROW, "category": "company"}]}
    assert binding_value_support(binding, fact, source_map, typed=True)
    assert binding_value_support(binding, fact, source_map) is None
    wrong = {**fact, "value": "Ordine degli Architetti di Bari"}
    assert binding_value_support(binding, wrong, source_map, typed=True) is None


@pytest.mark.parametrize("prop, first, second, same", [
    ("provincia", "Bari (BA)", "Bari", True),
    ("provincia_albo", "bari", "Bari (BA)", True),
    ("provincia", "Bari", "Lecce (LE)", False),
    ("data_iscrizione", "18/05/2015", "18 maggio 2015", True),
    ("data_nascita", "14/11/1982", "14 novembre 1982", True),
    ("data_iscrizione", "18/05/2015", "19/05/2015", False),
    ("nome", "Ing. Elisa Romano", "Elisa Romano", True),
    ("nome", "Elisa Romano", "Elisa Rossi", False),
    ("numero_iscrizione_registro_imprese", "01234560981", "99999999901", False),
    ("sede", "Bari (BA)", "Bari", False),
    ("qualifica_professionale", "Ing.", "Ingegnere", False),
])
def test_only_the_same_datum_in_another_format_is_the_same_value(prop, first, second, same):
    assert same_typed_value(prop, first, second) is same


def conflicts(values, *, typed=True, prop="provincia"):
    facts = {f"s{i}_f": {"subject": NAME, "entity": "person", "property": prop, "value": v}
             for i, v in enumerate(values, 1)}
    fields = {f"p{i}.s0": {"label": "x", "kind": "data", "fact_id": f"s{i}_f"}
              for i in range(1, len(values) + 1)}
    merged, report = {"facts": facts, "fields": fields}, {"conflicts": []}
    _mark_conflicts(merged, report, typed=typed)
    return merged, report


def test_a_format_of_one_datum_is_not_a_conflict_between_segments():
    merged, report = conflicts(["Bari (BA)", "Bari"])
    assert not report["conflicts"]
    assert merged["fields"]["p1.s0"]["fact_id"] == "s1_f"
    assert merged["fields"]["p2.s0"]["fact_id"] == "s2_f"
    _, dates = conflicts(["18/05/2015", "18 maggio 2015"], prop="data_iscrizione")
    assert not dates["conflicts"]


def test_two_real_values_stay_a_conflict_between_segments():
    merged, report = conflicts(["Bari (BA)", "Lecce (LE)"])
    assert report["conflicts"]
    assert merged["fields"]["p1.s0"]["review_kind"] == "conflicting"
    assert merged["fields"]["p2.s0"]["alternative_fact_ids"] == ["s1_f", "s2_f"]
    _, numbers = conflicts(["01234560981", "99999999901"], prop="numero_iscrizione")
    assert numbers["conflicts"]


def test_the_previous_profile_keeps_the_format_conflict():
    merged, report = conflicts(["Bari (BA)", "Bari"], typed=False)
    assert report["conflicts"] and merged["fields"]["p1.s0"]["review_kind"] == "conflicting"


def siblings(values, *, typed=True):
    doc = Document()
    doc.add_paragraph("Direttore tecnico")
    doc.add_paragraph("della provincia di: ________")
    doc.add_paragraph("della provincia di: ________")
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue())
    lines = [f"- Provincia {i}: {value}." for i, value in enumerate(values)]
    payload = proposal("provincia_albo", "della provincia di", values[0], lines[0])
    payload["facts"].update({f"g{i}": {**payload["facts"]["f"], "value": value, "evidence": [
        {"chunk_id": -7, "quote": lines[i]}]} for i, value in enumerate(values) if i})
    # In the real run each value was the proposal of another destination of the same person.
    payload["fields"]["p2.s0"] = {
        **payload["fields"]["p1.s0"], "fact_id": "g1", "form": {
            "paragraph_id": "paragraph:2", "quote": "della provincia di: [[p2.s0]]"}}
    sources = [source("\n".join(lines), -7), source(ROLE_LINE, -9)]
    audit = validate_global_proposal(json.dumps(payload), layout, "alpha", sources,
                                     typed_siblings=typed)
    return next(f for f in audit["fields"] if f["candidate_id"] == "p1.s0")


def test_the_same_province_with_its_abbreviation_asks_nothing():
    field = siblings(["Bari", "Bari (BA)"])
    assert not field.get("alternatives") and field["validation"] != "REJECTED"
    assert field["proposal"]["fact_id"] == "f" and "review_kind" not in field


def test_two_provinces_are_still_a_choice_and_the_previous_profile_keeps_the_format_one():
    assert len(siblings(["Bari", "Lecce (LE)"])["alternatives"]) == 2
    assert len(siblings(["Bari", "Bari (BA)"], typed=False)["alternatives"]) == 2
