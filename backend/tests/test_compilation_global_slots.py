"""Physical slot grounding; deterministic checks, not real-provider quality."""

import copy
import json
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document
from docx.oxml import OxmlElement

from app.compilation_catalog import build_compilation_catalog
from app.compilation_global import build_global_input, validate_global_proposal
from app.docx_templates import DocumentInputError, inspect_docx


def layout_for(text):
    doc = Document()
    doc.add_paragraph(text)
    stream = BytesIO()
    doc.save(stream)
    return inspect_docx(stream.getvalue())


@pytest.fixture
def case():
    layout = layout_for(
        "prov. ........ via/piazza ........ n. ........, tel ........ e-mail ........ pec ........"
    )
    source = {"chunk_id": -7, "file_id": -3, "chunk_index": 0,
              "source_name": "recapiti.txt", "role": "source", "scope": "global",
              "category": "company", "project_id": None,
              "content": "Alba: PD; Via Seta; 42; +39 049 000 6789; "
                         "info@alba.example; alba@pec.example."}
    facts, fields = {}, {}
    for i, (label, value) in enumerate(zip(
        ["prov.", "via/piazza", "n.", "tel", "e-mail", "pec"],
        ["PD", "Via Seta", "42", "+39 049 000 6789", "info@alba.example", "alba@pec.example"],
        strict=True,
    )):
        facts[f"f{i}"] = {"subject": "Alba", "entity": "company", "aspect": "identity",
                          "property": label, "value": value,
                          "evidence": [{"chunk_id": -7, "quote": source["content"]}]}
        fields[f"p0.s{i}"] = {
            "label": label, "kind": "data", "disposition": "value", "fact_id": f"f{i}",
            "property": label, "conditions": [],
            "form": {"paragraph_id": "paragraph:0", "quote": f"{label} [[p0.s{i}]]"},
        }
    return layout, [source], {"version": 9, "fields": fields, "facts": facts,
                              "conditions": {}, "bindings": {}}


def audit(case):
    return validate_global_proposal(json.dumps(case[2]), case[0], "alpha", case[1])


def fields(result):
    return {f["candidate_id"]: f for f in result["fields"]}


def test_catalog_reuses_parser_markers_and_slices_only_between_adjacent_slots(case):
    layout = case[0]
    catalog = build_compilation_catalog(layout)
    paragraph = catalog["blocks"][0]["paragraphs"][0]
    assert catalog["version"] == 5
    assert paragraph["text_with_fields"] == layout.paragraph_catalog[0]["text_with_fields"]
    assert paragraph["text"] == layout.paragraph_catalog[0]["text"]
    assert catalog["candidates"]["p0.s2"]["slot_context"] == {"before": " n. ", "after": ", tel "}
    for key, slot in layout.slots.items():
        assert catalog["candidates"][key]["range"] == [slot.start, slot.end]


def test_all_six_slots_keep_positions_and_original_source_references(case):
    result = audit(case)
    assert result["counts"] == {"GROUNDED_PROPOSAL": 6}
    for key, field in fields(result).items():
        slot = case[0].slots[key]
        proof = field["destination_check"]
        assert proof["range"] == [slot.start, slot.end]
        assert proof["result"] == "literal_slot_match"
        assert f"[[{key}]]" in proof["marked_quote"]
        assert f"[[{key}]]" not in field["form_evidence"]["quote"]
        assert slot.placeholder in field["form_evidence"]["quote"]
        source = field["source_evidence"][0]
        assert (source["role"], source["scope"], source["file_id"], source["chunk_id"],
                source["chunk_index"]) == ("source", "global", -3, -7, 0)
        assert source["content_sha256"]
    assert result["writes"] == result["resolved"] == 0


def test_shifted_contact_proposals_cannot_cite_the_next_slot(case):
    original = copy.deepcopy(case[2]["fields"])
    for i in [2, 3, 4]:
        case[2]["fields"][f"p0.s{i}"] = original[f"p0.s{i + 1}"]
    result = fields(audit(case))
    for i in [2, 3, 4]:
        assert result[f"p0.s{i}"]["validation"] == "REJECTED"
        assert "marker" in result[f"p0.s{i}"]["validation_errors"][0]
        assert result[f"p0.s{i}"]["destination_check"]["result"] == "rejected"
        assert "proposed_value" not in result[f"p0.s{i}"]
    assert result["p0.s0"]["validation"] == result["p0.s1"]["validation"] == "GROUNDED_PROPOSAL"
    assert result["p0.s5"]["validation"] == "GROUNDED_PROPOSAL"


@pytest.mark.parametrize("quote", [
    "tel", "tel [[p0.s3]]", "tel [[p0.s2]]", "[[p0.s2]]", "[[p0.s2]],",
    "n. [[invented]]", "n. [[p0.s2]], tel [[p0.s3]]",
])
def test_unanchored_fabricated_or_multiple_slot_quotes_rejected_locally(case, quote):
    case[2]["fields"]["p0.s2"]["form"]["quote"] = quote
    result = fields(audit(case))
    assert result["p0.s2"]["validation"] == "REJECTED"
    assert result["p0.s3"]["validation"] == "GROUNDED_PROPOSAL"


def test_another_paragraph_cannot_supply_inline_destination_quote(case):
    case[2]["fields"]["p0.s2"]["form"]["paragraph_id"] = "paragraph:99"
    field = fields(audit(case))["p0.s2"]
    assert field["validation"] == "REJECTED"
    assert "paragrafo" in field["validation_errors"][0]


def test_label_after_slot_and_conservative_typography_are_supported(case):
    case = (layout_for("________ (Recapito principale)"), case[1], case[2])
    item = case[2]["fields"]["p0.s3"]
    item["form"]["quote"] = "[[p0.s0]]   (RECAPITO PRINCIPALE)"
    case[2]["fields"] = {"p0.s0": item}
    field = audit(case)["fields"][0]
    assert field["validation"] == "GROUNDED_PROPOSAL"
    assert field["form_evidence"]["quote"] == "________ (Recapito principale)"


@pytest.mark.parametrize("mutation", ["form", "user", "foreign", "wrong_value"])
def test_slot_anchor_never_relaxes_source_provenance_or_value_grounding(case, mutation):
    if mutation == "foreign":
        case[1][0].update(chunk_id=7, file_id=3, project_id="beta", scope="project:beta")
        with pytest.raises(ValueError):
            audit(case)
        return
    if mutation == "wrong_value":
        case[2]["facts"]["f2"]["value"] = "99999"
    else:
        case[1][0]["role"] = mutation
        with pytest.raises(ValueError):
            audit(case)
        return
    assert fields(audit(case))["p0.s2"]["validation"] == "REJECTED"


def test_historical_v8_keeps_its_original_paragraph_grounding_for_replay(case):
    case[2]["version"] = 8
    for field in case[2]["fields"].values():
        field["form"]["quote"] = field["label"]
    result = audit(case)
    assert result["counts"] == {"GROUNDED_PROPOSAL": 6}
    assert all("destination_check" not in f for f in result["fields"])


def test_anchor_does_not_claim_independent_semantic_entailment(case):
    item = case[2]["fields"]["p0.s2"]
    item.update(fact_id="f3", property="tel", label="tel")
    field = fields(audit(case))["p0.s2"]
    assert field["destination_check"]["result"] == "literal_slot_match"
    assert field["semantic_review_required"]
    assert field["written_value"] is None
    assert audit(case)["resolved"] == 0


def test_literal_marker_collision_in_original_is_not_silently_reinterpreted():
    layout = layout_for("Testo [[p0.s0]] altro __________")
    with pytest.raises(DocumentInputError, match="Marker"):
        build_compilation_catalog(layout)


def test_source_backed_conditional_retains_value_after_restoring_target_quote(case):
    case = (layout_for("Se incaricata: Recapito ________"), case[1], case[2])
    item = case[2]["fields"]["p0.s3"]
    item.update(disposition="conditional", conditions=["c"], reason="Incarico sconosciuto")
    item["form"]["quote"] = "Recapito [[p0.s0]]"
    case[2]["fields"] = {"p0.s0": item}
    case[2]["conditions"] = {"c": {
        "form": {"paragraph_id": "paragraph:0", "quote": "Se incaricata"},
        "aspect": "other", "operator": "semantic", "fact_ids": [], "reason": "Da confermare",
        "scope": [{"kind": "paragraph", "id": "paragraph:0"}],
    }}
    field = audit(case)["fields"][0]
    assert field["proposed_value"] == "+39 049 000 6789"
    assert field["value"] is field["written_value"] is None
    assert field["condition_checks"]["c"]["result"] == "unknown"


def test_real_minervino_line_exposes_six_distinct_parser_markers():
    path = Path(__file__).resolve().parents[2] / (
        "demo-documents/bandi/minervino-elenco-sia/originali/domanda-iscrizione.docx"
    )
    catalog = build_compilation_catalog(inspect_docx(path.read_bytes()))
    candidates = catalog["candidates"]
    assert candidates["p42.s2"]["slot_context"]["before"].strip() == "n."
    assert candidates["p42.s3"]["slot_context"]["before"].strip() == ", tel"
    assert candidates["p42.s4"]["slot_context"]["before"].strip() == "e-mail"
    assert candidates["p42.s5"]["slot_context"]["before"].strip() == "pec"
    assert len([key for key in candidates if key.startswith("p42.s")]) == 6


def test_current_schema_requires_version_nine_but_keeps_one_request(case):
    data = build_global_input(case[0], "alpha", case[1])
    assert data["schema_output"]["properties"]["version"]["const"] == 10
    assert data["schema_output"]["properties"]["fields"]["maxProperties"] == 400


@pytest.mark.parametrize("version", [5, 6, 7, 8, True])
def test_active_contract_cannot_be_downgraded_to_skip_slot_validation(case, version):
    case[2]["version"] = version
    for field in case[2]["fields"].values():
        field["form"]["quote"] = field["label"]
    with pytest.raises(ValueError, match="contratto richiesto V9"):
        validate_global_proposal(json.dumps(case[2]), case[0], "alpha", case[1],
                                 expected_version=9)


def test_expected_contract_preserves_current_grounding_and_historical_replay(case):
    assert validate_global_proposal(json.dumps(case[2]), case[0], "alpha", case[1],
                                    expected_version=9) == audit(case)
    case[2]["version"] = 8
    for field in case[2]["fields"].values():
        field["form"]["quote"] = field["label"]
    assert audit(case)["counts"] == {"GROUNDED_PROPOSAL": 6}


def test_context_windows_are_bounded_without_truncating_original_paragraph():
    text = "Prefisso " + "a" * 150 + " ________ " + "b" * 150
    catalog = build_compilation_catalog(layout_for(text))
    assert catalog["blocks"][0]["paragraphs"][0]["text"] == text
    context = catalog["candidates"]["p0.s0"]["slot_context"]
    assert len(context["before"]) == len(context["after"]) == 120


def test_blank_table_cells_keep_existing_row_anchors(case):
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Recapito"
    stream = BytesIO()
    doc.save(stream)
    item = case[2]["fields"]["p0.s3"]
    item["form"] = {"paragraph_id": "paragraph:0", "quote": "Recapito"}
    case[2]["fields"] = {"t0.r0.c1": item}
    case = (inspect_docx(stream.getvalue()), case[1], case[2])
    field = audit(case)["fields"][0]
    assert field["validation"] == "GROUNDED_PROPOSAL"
    assert field["destination_check"]["result"] == "not_required"


def test_non_text_object_does_not_shift_parser_coordinates_or_restored_placeholder(case):
    doc = Document()
    p = doc.add_paragraph()
    p.add_run()._r.append(OxmlElement("w:noBreakHyphen"))
    p.add_run("n. ________")
    stream = BytesIO()
    doc.save(stream)
    layout = inspect_docx(stream.getvalue())
    item = case[2]["fields"]["p0.s2"]
    item["form"] = {"paragraph_id": "paragraph:0", "quote": "n. [[p0.s0]]"}
    case[2]["fields"] = {"p0.s0": item}
    case = (layout, case[1], case[2])
    catalog = build_compilation_catalog(layout)
    paragraph = catalog["blocks"][0]["paragraphs"][0]
    assert paragraph["text"] == "n. ________"
    assert paragraph["text_with_fields"] == "\ufffcn. [[p0.s0]]"
    assert catalog["candidates"]["p0.s0"]["range"] == [4, 12]
    field = audit(case)["fields"][0]
    assert field["form_evidence"]["quote"] == "n. ________"
    assert field["validation"] == "GROUNDED_PROPOSAL"


def test_anchored_alternatives_remain_alternatives_without_selecting_a_value(case):
    case[1][0]["content"] += " Altro civico: 43."
    other = copy.deepcopy(case[2]["facts"]["f2"])
    other.update(value="43", evidence=[{"chunk_id": -7, "quote": case[1][0]["content"]}])
    case[2]["facts"]["other"] = other
    item = case[2]["fields"]["p0.s2"]
    item.update(disposition="review", fact_id=None, alternative_fact_ids=["f2", "other"],
                review_kind="ambiguous", reason="Due valori documentati")
    field = fields(audit(case))["p0.s2"]
    assert field["destination_check"]["result"] == "literal_slot_match"
    assert {a["value"] for a in field["alternatives"]} == {"42", "43"}
    assert field["value"] is field["written_value"] is None
