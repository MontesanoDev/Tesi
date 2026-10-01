import json
from functools import partial

import pytest

from app.draft_generation import parse_generated_draft
from app.fact_extraction import ExtractedFact, parse_extracted_facts
from app.generation import GenerationError, _parse_content


@pytest.mark.parametrize(
    "parser",
    [
        partial(_parse_content, evidence_count=2, model="test", usage={}),
        partial(parse_extracted_facts, evidence_count=2),
        partial(parse_generated_draft, available_fact_ids={"cf-deadline"}),
    ],
    ids=["answer", "facts", "draft"],
)
@pytest.mark.parametrize(
    "content",
    [
        "[]",
        "null",
        "true",
        "false",
        "42",
        '"testo"',
        '{"incompleto":',
        "[" * 2_000 + "]" * 2_000,
        '{"numero":' + "9" * 5_000 + "}",
    ],
    ids=[
        "array",
        "null",
        "true",
        "false",
        "number",
        "string",
        "truncated",
        "excessive-nesting",
        "oversized-integer",
    ],
)
def test_model_parsers_report_unusable_json_as_generation_errors(parser, content):
    with pytest.raises(GenerationError):
        parser(content)


def test_answer_parser_ignores_non_integer_citation_ids():
    parsed = _parse_content(
        json.dumps(
            {
                "answer": "Risposta dalle fonti.",
                "citation_ids": [True, False, "1", 1.0, None, {}, [], 2, 2, 1],
            }
        ),
        evidence_count=2,
        model="test",
        usage={},
    )

    assert parsed.citations == [2, 1]
    assert all(type(citation) is int for citation in parsed.citations)
    assert parsed.answer.endswith("Fonti: [2], [1].")


@pytest.mark.parametrize("reference", [0, -1, 99])
@pytest.mark.parametrize("location", ["answer", "citation_ids"])
def test_answer_parser_rejects_unavailable_references(reference, location):
    payload = {"answer": "Dato [1].", "citation_ids": [1]}
    payload[location] = f"Dato [{reference}]." if location == "answer" else [reference]
    with pytest.raises(GenerationError, match="fonte non presente"):
        _parse_content(json.dumps(payload), evidence_count=2, model="test", usage={})


def test_answer_parser_reports_an_oversized_inline_reference():
    with pytest.raises(GenerationError, match="fonte non presente"):
        _parse_content(
            json.dumps({"answer": "Dato [" + "9" * 5_000 + "]."}),
            evidence_count=2,
            model="test",
            usage={},
        )


def test_fact_parser_ignores_non_integer_source_ids():
    facts, missing = parse_extracted_facts(
        json.dumps(
            {
                "facts": [
                    {"title": "Senza fonte", "value": "Da ignorare", "evidence_ids": [True]},
                    {
                        "title": "Scadenza",
                        "value": "15 settembre",
                        "evidence_ids": [
                            True,
                            False,
                            "1",
                            1.0,
                            None,
                            {},
                            [],
                            2,
                            2,
                            1,
                            0,
                            -1,
                            99,
                        ],
                    },
                ]
            }
        ),
        evidence_count=2,
    )

    assert facts == [ExtractedFact("Scadenza", "15 settembre", [2, 1])]
    assert all(type(source_id) is int for source_id in facts[0].evidence_ids)
    assert missing == []


def test_model_parsers_still_accept_fenced_json():
    answer = _parse_content(
        '```JSON\n{"answer":"Dato [1].", "citation_ids":[1]}\n```',
        evidence_count=1,
        model="test",
        usage={"total_tokens": 24},
    )
    facts, _ = parse_extracted_facts(
        '```json\n{"facts":[{"title":"Scadenza","value":"15 settembre","evidence_ids":[1]}]}\n```',
        evidence_count=1,
    )
    draft = parse_generated_draft(
        '```json\n{"markdown":"Scadenza [CF:cf-deadline]","used_fact_ids":["cf-deadline"]}\n```',
        available_fact_ids={"cf-deadline"},
    )

    assert answer.citations == [1]
    assert answer.total_tokens == 24
    assert facts == [ExtractedFact("Scadenza", "15 settembre", [1])]
    assert draft.used_fact_ids == ["cf-deadline"]
