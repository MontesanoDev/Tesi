import pytest

from app.generation import GenerationError, _parse_content


def test_generation_parser_accepts_only_available_citations():
    parsed = _parse_content(
        '{"answer":"La scadenza e il 15 settembre [2].",'
        '"citation_ids":[2],"missing_information":[]}',
        evidence_count=3,
        model="deepseek-test",
        usage={"total_tokens": 24},
    )

    assert parsed.citations == [2]
    assert parsed.total_tokens == 24


def test_generation_parser_rejects_unknown_citations():
    with pytest.raises(GenerationError, match="fonte non presente"):
        _parse_content(
            '{"answer":"Dato non supportato [9].","citation_ids":[9]}',
            evidence_count=2,
            model="deepseek-test",
            usage={},
        )
