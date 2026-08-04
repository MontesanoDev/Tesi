import json

import pytest

from app.fact_extraction import (
    ExtractedFact,
    parse_extracted_facts,
    render_call_facts_markdown,
    select_source_chunks,
)
from app.generation import GenerationError


def test_select_source_chunks_samples_the_whole_document():
    chunks = [
        {
            "chunk_id": index,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": index,
            "content": str(index).ljust(20, "x"),
            "char_count": 20,
        }
        for index in range(20)
    ]

    selected = select_source_chunks(chunks, max_characters=100)

    assert len(selected) == 5
    assert selected[0]["chunk_index"] == 0
    assert selected[-1]["chunk_index"] == 19
    assert sum(len(item["content"]) for item in selected) <= 100


def test_parse_extracted_facts_requires_valid_provenance_and_deduplicates():
    payload = {
        "facts": [
            {
                "title": "Scadenza",
                "value": "15 settembre 2025",
                "evidence_ids": [2, 2, 99],
            },
            {
                "title": "Scadenza",
                "value": "15 settembre 2025",
                "evidence_ids": [2],
            },
            {"title": "Dato inventato", "value": "Assente", "evidence_ids": [99]},
        ],
        "missing_information": ["PEC del referente", "PEC del referente", ""],
    }

    facts, missing = parse_extracted_facts(json.dumps(payload), evidence_count=3)

    assert facts == [
        ExtractedFact(
            title="Scadenza",
            value="15 settembre 2025",
            evidence_ids=[2],
        )
    ]
    assert missing == ["PEC del referente"]


def test_parse_extracted_facts_rejects_an_empty_result():
    with pytest.raises(GenerationError):
        parse_extracted_facts('{"facts": [], "missing_information": []}', evidence_count=2)


def test_render_call_facts_markdown_keeps_source_locations():
    evidence = [
        {
            "source_name": "document.pdf",
            "chunk_index": 8,
        }
    ]

    markdown = render_call_facts_markdown(
        "progetto-test",
        [ExtractedFact("Soggetto ammesso", "Comune", [1])],
        ["Codice CUP"],
        evidence,
        "deepseek-test",
    )

    assert "status: pending_review" in markdown
    assert "## Soggetto ammesso" in markdown
    assert "document.pdf, frammento 9" in markdown
    assert "**Stato:** Da verificare" in markdown
    assert "- Codice CUP" in markdown
