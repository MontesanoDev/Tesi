"""FORM-owned subject constraints; real captured proposals, no provider or DB."""

import json
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document

from app.compilation_attribution import check_source_target
from app.compilation_catalog import build_compilation_catalog
from app.compilation_global import validate_global_proposal
from app.compilation_global_sessions import review_fields
from app.docx_templates import inspect_docx

FIXTURES = Path(__file__).parent / "fixtures"
UNPROVED = [f"p12.ft{i}" for i in [3, 4, 5, 6, 10, 11, 12]]


def test_real_seven_company_facts_cannot_become_personal_studio_or_contacts():
    case = json.loads((FIXTURES / "source-attribution-v1/cesano-real.json").read_text())
    layout = inspect_docx((FIXTURES / "formtext-v1/cesano/original.docx").read_bytes())
    audit = validate_global_proposal(json.dumps(case["proposal"]), layout,
                                     case["project_id"], case["sources"])
    fields = {f["candidate_id"]: f for f in audit["fields"]}
    for cid in UNPROVED:
        field = fields[cid]
        assert field["validation"] == "REJECTED"
        assert field.get("proposed_value") is field.get("value") is None
        assert "proposal_grounding" not in field
        assert "source_subject_type_mismatch" in field["source_target_check"]["validation_codes"]
        assert field["source_target_check"]["expected_entity"] == "person"
        assert field["source_evidence"]  # Provenance survives rejection.
    assert fields["p19.ft0"]["proposal_grounding"] == "GROUNDED_PROPOSAL"
    assert fields["p19.ft0"]["proposed_value"] == "Mapi Ingegneria S.r.l."
    assert all(f["validation"] == "GROUNDED_PROPOSAL" for f in audit["facts"].values())
    data = {"audit": audit, "catalog": build_compilation_catalog(layout),
            "writable_ids": list(fields)}
    assert {f["candidate_id"] for f in review_fields(data) if f["selectable"]} == {"p19.ft0"}


def case(text, *, entity="company", prop="email", value="ufficio@alba.demo", proof=None,
         binding=False, conditional=False):
    doc = Document()
    doc.add_paragraph(text)
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue(), require_candidates=False)
    catalog = build_compilation_catalog(layout)
    quote = proof or f"Società Alba; Email aziendale: {value}."
    source = {"chunk_id": -7, "file_id": -3, "chunk_index": 0,
              "source_name": "anagrafica.txt", "role": "source", "scope": "global",
              "category": "company", "project_id": None, "content": quote}
    fields = {}
    for cid in layout.slots:
        context = catalog["candidates"][cid]["slot_context"]
        marked = context["before"] + f"[[{cid}]]" + context["after"]
        fields[cid] = {"label": "Etichetta modello deliberatamente generica", "kind": "data",
                       "disposition": "conditional" if conditional else "value",
                       "conditions": ["c"] if conditional else [],
                       "form": {"paragraph_id": "paragraph:0", "quote": marked},
                       "property": prop, "fact_id": "f"}
        if conditional:
            fields[cid]["reason"] = "Decisione non disponibile"
        if binding:
            fields[cid]["binding_id"] = "b"
    proposal = {"version": 12, "uncertain_paragraph_ids": [], "coverage": [],
                "choice_groups": {}, "clarifications": {}, "conditions": {}, "bindings": {},
                "facts": {"f": {"entity": entity, "subject": "Ada Neri" if entity == "person"
                                 else "Alba", "aspect": "identity", "property": prop,
                                 "value": value, "evidence": [{"chunk_id": -7, "quote": quote}]}},
                "fields": fields}
    if conditional:
        proposal["conditions"]["c"] = {
            "form": {"paragraph_id": "paragraph:0", "quote": text}, "aspect": "participation",
            "operator": "semantic", "fact_ids": [],
            "scope": [{"kind": "candidate", "id": cid} for cid in fields], "reason": "Da decidere"}
    if binding:
        proposal["bindings"]["b"] = {
            "form": {"paragraph_id": "paragraph:0", "quote": "Firmatario"},
            "required_role": "Firmatario", "source_role": "Firmatario",
            "evidence": [{"chunk_id": -7, "quote": quote}]}
    return layout, [source], proposal


def audit(data):
    return validate_global_proposal(json.dumps(data[2]), data[0], "alpha", data[1])


@pytest.mark.parametrize("text", [
    "Il sottoscritto ________ con studio in ________ email ________",
    "Il/la sottoscritto/a ________ Partita IVA ________",
    "PEC del firmatario ________", "Telefono del professionista ________",
    "Direttore tecnico: nome e cognome ________ email ________",
])
@pytest.mark.parametrize("entity", ["company", "other", "authority", "project"])
def test_model_entity_or_label_cannot_override_explicit_personal_subject(text, entity):
    result = audit(case(text, entity=entity))
    assert all(f["validation"] == "REJECTED" for f in result["fields"])


def test_company_properties_remain_available_after_explicit_inline_subject_transition():
    data = case("Il sottoscritto ________ della società ________ email ________")
    data[2]["facts"]["name"] = {**data[2]["facts"]["f"], "property": "denominazione",
                                "value": "Alba"}
    data[2]["fields"]["p0.s1"].update(property="denominazione", fact_id="name")
    fields = {f["candidate_id"]: f for f in audit(data)["fields"]}
    assert fields["p0.s0"]["validation"] == "REJECTED"
    for cid in ["p0.s1", "p0.s2"]:
        assert fields[cid]["validation"] == "GROUNDED_PROPOSAL"
        assert fields[cid]["value"] == ("Alba" if cid == "p0.s1" else "ufficio@alba.demo")


@pytest.mark.parametrize("text,prop,value,proof", [
    ("PEC dell'impresa ________", "pec", "ufficio@alba.demo",
     "Società Alba; PEC: ufficio@alba.demo."),
    ("Della Società di Ingegneria ________", "denominazione", "Alba", "Denominazione: Alba."),
    ("Denominazione/ragione sociale ________", "denominazione", "Alba", "Denominazione: Alba."),
    ("Sede legale ________", "sede_legale", "Via Roma 24",
     "Società Alba; Sede legale: Via Roma 24."),
    ("Il sottoscritto, legale rappresentante dell’operatore economico ________",
     "denominazione", "Alba", "Denominazione: Alba."),
])
def test_explicit_company_targets_preserve_company_facts(text, prop, value, proof):
    field = audit(case(text, prop=prop, value=value, proof=proof))["fields"][0]
    assert field["validation"] == "GROUNDED_PROPOSAL"


def test_personal_value_keeps_original_and_citations_when_existing_role_binding_passes():
    data = case("Firmatario: PEC ________", entity="person", binding=True,
                proof="Firmatario: Ada Neri; PEC personale: ufficio@alba.demo.")
    field = audit(data)["fields"][0]
    assert field["value"] == "ufficio@alba.demo"
    assert field["subject_binding"]["result"] == "literal_match"
    assert field["source_evidence"][0]["quote"] == data[1][0]["content"]


def test_valid_personal_binding_does_not_resolve_unknown_applicability():
    field = audit(case("Firmatario: PEC ________", entity="person", binding=True,
                       conditional=True,
                       proof="Firmatario: Ada Neri; PEC personale: ufficio@alba.demo."))[
        "fields"][0]
    assert field["proposal_grounding"] == "GROUNDED_PROPOSAL"
    assert field["condition_checks"]["c"]["result"] == "unknown"
    assert field["value"] is field["written_value"] is None


@pytest.mark.parametrize("variant", ["no_binding", "other_person", "other_role", "invented_quote"])
def test_personal_entity_is_not_a_substitute_for_demonstrated_identity_role_and_value(variant):
    data = case("Firmatario: PEC ________", entity="person", binding=True,
                proof="Firmatario: Ada Neri; PEC personale: ufficio@alba.demo.")
    if variant == "no_binding":
        data[2]["fields"]["p0.s0"].pop("binding_id")
    elif variant == "other_person":
        data[2]["facts"]["f"]["subject"] = "Bea Mori"
    elif variant == "other_role":
        data[2]["bindings"]["b"]["source_role"] = "Socio"
    else:
        data[2]["facts"]["f"]["evidence"][0]["quote"] = "Falso: ufficio@alba.demo"
    field = audit(data)["fields"][0]
    assert not field.get("value") and "proposal_grounding" not in field


def test_same_person_residence_is_not_evidence_of_professional_studio():
    field = audit(case("Firmatario: con studio in ________", entity="person", binding=True,
                       prop="comune", value="Torino",
                       proof="Firmatario: Ada Neri; Comune di residenza: Torino."))["fields"][0]
    assert field["validation"] == "REJECTED"
    assert "source_property_scope_mismatch" in field["source_target_check"]["validation_codes"]


def test_scope_compatibility_is_not_inferred_from_identical_city_or_email():
    field = audit(case("Firmatario: con studio in ________", prop="comune", value="Torino",
                       proof="Società Alba; Sede legale: Torino."))["fields"][0]
    assert field["validation"] == "REJECTED"


def test_unrecognised_form_context_is_not_turned_into_positive_subject_evidence():
    data = case("Recapito ________")
    result = audit(data)
    check = check_source_target("p0.s0", build_compilation_catalog(data[0]), result["facts"]["f"])
    assert check["result"] == "not_determined"
    # Do not invalidate persisted narrator fingerprints for unchanged proposals.
    assert "source_target_check" not in result["fields"][0]


def test_company_with_same_name_as_person_does_not_prove_personal_contact():
    data = case("Firmatario: PEC ________", proof="Impresa Ada Neri; PEC: ufficio@alba.demo.")
    data[2]["facts"]["f"]["subject"] = "Ada Neri"
    field = audit(data)["fields"][0]
    assert field["validation"] == "REJECTED"
    assert "source_subject_type_mismatch" in field["source_target_check"]["validation_codes"]


def test_homonyms_with_conflicting_identifiers_are_not_merged_by_subject_compatibility():
    from test_compilation_binding_identity import ROW
    from test_compilation_binding_identity import case as identity_case

    data = identity_case()
    data[1][0]["content"] += "\n" + ROW.replace("NREADA85A41L219R", "NREADA86A41L219R")
    field = audit(data)["fields"][0]
    assert field["subject_binding"]["result"] == "review_required"
    assert field.get("value") is None and "proposal_grounding" not in field


def test_unknown_target_and_person_entity_still_require_historical_role_binding():
    field = audit(case("Recapito ________", entity="person"))["fields"][0]
    assert "source_target_check" not in field
    assert field["subject_binding"]["result"] == "review_required"
    assert not field.get("value") and "proposal_grounding" not in field

