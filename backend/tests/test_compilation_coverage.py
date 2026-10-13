"""Coverage is grounded model reasoning, never proof of facts or writable values."""

import copy
import json
import random

import pytest
from test_compilation_global_sparse import case as sparse_case

from app.compilation_coverage import coverage_notice, narration_coverage
from app.compilation_global import build_global_input, validate_global_proposal

case = sparse_case


def prepare(case):
    payload = case[2]
    payload.update(version=12, bindings={}, choice_groups={}, clarifications={}, coverage=[])
    payload["fields"] = {"t0.r0.c1": payload["fields"]["t0.r0.c1"]}
    payload["conditions"] = {}
    return payload


def explanation(ids=None, **changes):
    return {"candidate_ids": ids or ["t0.r1.c1", "t0.r2.c1"], "outcome": "source_not_found",
            "reason": "Non ho trovato supporto sufficiente per i recapiti richiesti",
            "form": {"paragraph_id": "paragraph:0", "quote": "Informazioni dell'organizzazione"},
            **changes}


def audit(case):
    return validate_global_proposal(json.dumps(case[2]), case[0], "alpha", case[1],
                                    expected_version=12)


def fields(result):
    return {f["candidate_id"]: f for f in result["fields"]}


def test_new_request_requires_explanations_in_the_same_call(case):
    schema = build_global_input(case[0], "alpha", case[1])["schema_output"]
    assert schema["properties"]["version"]["const"] == 12
    assert "coverage" in schema["required"]
    assert schema["properties"]["coverage"]["maxItems"] == 400
    assert "value" not in schema["$defs"]["UnfilledExplanation"]["properties"]


def test_grouped_explanations_account_for_omissions_but_never_resolve_or_authorize_writes(case):
    p = prepare(case)
    p["coverage"] = [explanation()]
    result = audit(case)
    assert result["coverage_summary"]["explicit_decisions_complete"]
    assert result["coverage_summary"]["proposed"] == 1
    assert result["coverage_summary"]["explained_unfilled"] == 2
    assert result["coverage_summary"]["unexplained"] == 0
    assert not result["coverage_summary"]["semantic_completeness_verified"]
    assert result["unassigned_count"] == 2  # Omitted assignments are not fabricated.
    assert result["fields"][0]["validation"] == "GROUNDED_PROPOSAL"
    for field in result["fields"][1:]:
        assert field["coverage"]["state"] == "EXPLAINED_UNFILLED"
        assert field["coverage"]["origin"] == "MODEL"
        assert field["coverage"]["form_evidence"]["role"] == "form"
        assert field["written_value"] is None and field["source_evidence"] == []
        assert "value" not in field and "disposition" not in field
    assert result["resolved"] == result["writes"] == 0


@pytest.mark.parametrize("records,unexplained,rejected", [(None, 2, 0), ({}, 2, 0),
    ([], 2, 0), ([None], 2, 0), ([explanation(form=None)], 0, 2),
    ([explanation(form={"paragraph_id": "paragraph:0", "quote": "Testo inventato"})], 0, 2),
    ([explanation(value="Valore inventato")], 0, 2)])
def test_invalid_and_missing_explanations_are_distinct(case, records, unexplained, rejected):
    p = prepare(case)
    p["coverage"] = records
    result = audit(case)
    assert result["coverage_summary"]["unexplained"] == unexplained
    assert result["coverage_summary"]["rejected_explanations"] == rejected
    assert not result["coverage_summary"]["coverage_checks_passed"]
    assert result["fields"][0]["validation"] == "GROUNDED_PROPOSAL"
    assert result["fields"][0]["source_evidence"][0]["chunk_id"] == -7


def test_explicit_unassessed_is_distinct_from_unexplained_and_no_source(case):
    p = prepare(case)
    p["coverage"] = [explanation(["t0.r1.c1"], outcome="unassessed", form=None,
        reason="Non ho determinato quale recapito sia richiesto")]
    result = audit(case)
    assert result["coverage_summary"]["explicitly_unassessed"] == 1
    assert result["coverage_summary"]["unexplained"] == 1
    assert fields(result)["t0.r2.c1"]["coverage"]["origin"] == "BACKEND"


def test_only_covered_known_positions_are_accepted_no_last_group_wins(case):
    p = prepare(case)
    p["coverage"] = [explanation(["t0.r1.c1", "t0.r2.c1", "invented"]),
                     explanation(["t0.r1.c1"], outcome="manual_input")]
    result = audit(case)
    assert fields(result)["t0.r1.c1"]["coverage"]["state"] == "REJECTED_EXPLANATION"
    assert fields(result)["t0.r2.c1"]["coverage"]["state"] == "EXPLAINED_UNFILLED"
    assert result["coverage_groups"][0]["validation"] == "PARTIAL"
    assert len(result["fields"]) == 3


def test_no_explanation_overrides_or_contaminates_a_source_proposal(case):
    p = prepare(case)
    before = audit(case)["fields"][0]
    p["coverage"] = [explanation(["t0.r0.c1", "t0.r1.c1", "t0.r2.c1"])]
    after = audit(case)
    assert after["fields"][0] == before
    assert after["coverage_summary"]["proposed"] == 1
    assert after["coverage_summary"]["explained_unfilled"] == 2
    assert after["coverage_groups"][0]["validation_errors"]


def test_quote_from_a_different_section_cannot_explain_a_position(case):
    p = prepare(case)
    p["coverage"] = [explanation(["t0.r2.c1"], form={
        "paragraph_id": "paragraph:3", "quote": "Recapito principale"})]
    result = audit(case)
    assert result["coverage_summary"]["rejected_explanations"] == 1
    assert result["coverage_summary"]["unexplained"] == 1


@pytest.mark.parametrize("operator,expected", [("different", "EXPLAINED_UNFILLED"),
                                             ("semantic", "REJECTED_EXPLANATION")])
def test_not_applicable_requires_a_false_local_condition(case, operator, expected):
    condition = copy.deepcopy(case[2]["conditions"]["different"])
    p = prepare(case)
    p["conditions"] = {"different": {**condition, "operator": operator}}
    p["coverage"] = [explanation(["t0.r2.c1"], outcome="not_applicable", conditions=["different"])]
    result = audit(case)
    assert fields(result)["t0.r2.c1"]["coverage"]["state"] == expected
    assert fields(result)["t0.r2.c1"]["written_value"] is None


def test_unknown_condition_is_explained_without_becoming_missing_or_not_applicable(case):
    condition = copy.deepcopy(case[2]["conditions"]["different"])
    p = prepare(case)
    p["conditions"] = {"different": {**condition, "operator": "semantic"}}
    p["coverage"] = [explanation(["t0.r2.c1"], outcome="condition_unknown",
                                 conditions=["different"])]
    result = audit(case)
    assert fields(result)["t0.r2.c1"]["coverage"]["outcome"] == "condition_unknown"
    assert "disposition" not in fields(result)["t0.r2.c1"]
    assert result["conditions"]["different"]["result"] == "unknown"


def test_narrator_gets_reasons_and_separate_counts_not_xml_recipients(case):
    p = prepare(case)
    p["coverage"] = [explanation()]
    context = narration_coverage(audit(case))
    assert context["explained_unfilled"] == 2 and context["unexplained"] == 0
    assert context["groups"][0]["positions"] == 2
    assert "t0.r" not in json.dumps(context)
    assert "non prova" not in context["groups"][0]["reason"]
    assert narration_coverage({"unassigned_count": 5})["recorded"] is False


def test_v11_revalidation_stays_identical_without_new_metadata(case):
    p = case[2]
    p.update(version=11, bindings={}, choice_groups={}, clarifications={})
    result = validate_global_proposal(json.dumps(p), case[0], "alpha", case[1])
    assert "coverage_summary" not in result and "coverage" not in result["fields"][0]


def test_same_table_can_ground_a_shared_explanation_but_not_a_single_wrong_destination(case):
    p = prepare(case)
    p["coverage"] = [explanation(form={"paragraph_id": "paragraph:3",
                                       "quote": "Recapito principale"})]
    result = audit(case)
    assert result["coverage_summary"]["explained_unfilled"] == 2
    assert result["fields"][0]["validation"] == "GROUNDED_PROPOSAL"
    p["coverage"] = [explanation(["t0.r2.c1", "invented"], form={
        "paragraph_id": "paragraph:3", "quote": "Recapito principale"})]
    assert audit(case)["coverage_summary"]["rejected_explanations"] == 1


def test_shared_table_context_does_not_cross_to_another_table(case):
    from io import BytesIO

    from app.docx_templates import inspect_docx

    doc = case[0].document
    doc.add_heading("Sezione indipendente", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Altro riferimento"
    encoded = BytesIO()
    doc.save(encoded)
    extended = inspect_docx(encoded.getvalue()), case[1], case[2]
    p = prepare(extended)
    p["coverage"] = [explanation(["t0.r2.c1", "t1.r0.c1"], form={
        "paragraph_id": "paragraph:3", "quote": "Recapito principale"})]
    result = audit(extended)
    assert result["coverage_summary"]["rejected_explanations"] == 2
    assert result["fields"][0]["validation"] == "GROUNDED_PROPOSAL"


@pytest.mark.parametrize("summary,fragment", [
    ({"unexplained": 2}, "manca ancora un esito"),
    ({"explicitly_unassessed": 1}, "copertura del modulo resta incompleta"),
    ({"rejected_explanations": 3}, "non sono state validate"),
    ({"explained_unfilled": 9}, ""),
])
def test_initial_notice_uses_backend_counts_never_claims_the_model_did_not_read(summary, fragment):
    notice = coverage_notice({"coverage_summary": summary})
    assert fragment in notice.casefold()
    assert "non valutate" not in notice and "fonti non contengono" not in notice


def test_notice_does_not_hide_rejected_reasons_behind_unexplained_positions():
    notice = coverage_notice({"coverage_summary": {"unexplained": 7,
                                                   "rejected_explanations": 105}})
    assert "manca ancora un esito" in notice and "motivazioni non sono state validate" in notice


@pytest.mark.parametrize("seed", range(12))
def test_seeded_malformed_coverage_cannot_crash_or_write(case, seed):
    rng = random.Random(seed)
    original = copy.deepcopy(case[2])
    values = [None, True, 42, {}, [], "🧪", "\ud800", float("nan")]
    for _ in range(30):
        case[2].clear()
        case[2].update(copy.deepcopy(original))
        p = prepare(case)
        record = explanation()
        record[rng.choice(list(record))] = rng.choice(values)
        p["coverage"] = [record]
        try:
            result = audit(case)
        except ValueError:
            continue
        assert result["resolved"] == result["writes"] == 0
        assert result["fields"][0]["validation"] == "GROUNDED_PROPOSAL"
