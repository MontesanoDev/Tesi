import asyncio
import json

import httpx
import pytest

from app.fact_extraction import (
    OUTPUT_TOKEN_BUDGETS,
    ExtractedFact,
    extract_call_facts,
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

    assert "status: available" in markdown
    assert "## Soggetto ammesso" in markdown
    assert "document.pdf, frammento 9" in markdown
    assert "**Stato:** Disponibile" in markdown
    assert "- Codice CUP" in markdown


@pytest.fixture
def anyio_backend():
    return "asyncio"


def source_chunks():
    return [{
        "source_name": "avviso.pdf", "chunk_index": 17,
        "content": "La scadenza e il 15 settembre 2025.",
    }]


def valid_content(title="Scadenza", value="15 settembre 2025"):
    return json.dumps({
        "facts": [{"title": title, "value": value, "evidence_ids": [1]}],
        "missing_information": [],
    })


def response_payload(content=None, reason="stop", tokens=123):
    return {
        "model": "deepseek-test",
        "choices": [{"finish_reason": reason, "message": {
            "content": valid_content() if content is None else content,
        }}],
        "usage": {"total_tokens": tokens},
    }


def provider(monkeypatch, handler):
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(
        transport=httpx.MockTransport(handler), **kwargs,
    ))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://provider.test")


@pytest.mark.anyio
async def test_extraction_accepts_complete_json_with_a_larger_output_budget(monkeypatch):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=response_payload())

    provider(monkeypatch, handler)
    result = await extract_call_facts("test", "Progetto test", source_chunks())
    assert len(requests) == 1
    assert requests[0]["max_tokens"] == OUTPUT_TOKEN_BUDGETS[0] == 12_000
    assert requests[0]["response_format"] == {"type": "json_object"}
    assert result.fact_count == 1
    assert result.total_tokens == 123
    assert "avviso.pdf, frammento 18" in result.markdown


@pytest.mark.anyio
@pytest.mark.parametrize("truncated", ['{"facts":[{"title":"Scadenza', valid_content("Parziale")])
async def test_length_retries_once_without_parsing_or_salvaging_partial_facts(
    monkeypatch, truncated,
):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        payload = response_payload(truncated, reason="length", tokens=400)
        if len(requests) == 2:
            payload = response_payload(tokens=600)
        return httpx.Response(200, json=payload)

    provider(monkeypatch, handler)
    result = await extract_call_facts("test", "Progetto test", source_chunks())
    assert [item["max_tokens"] for item in requests] == list(OUTPUT_TOKEN_BUDGETS)
    assert requests[0]["messages"] == requests[1]["messages"]
    assert result.total_tokens == 1000
    assert result.fact_count == 1
    assert result.facts[0].title == "Scadenza"
    assert "Parziale" not in result.markdown


@pytest.mark.anyio
async def test_two_truncations_stop_even_when_json_happens_to_be_complete(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=response_payload(reason="length"))

    provider(monkeypatch, handler)
    with pytest.raises(GenerationError, match="ancora troppo lunga"):
        await extract_call_facts("test", "Progetto test", source_chunks())
    assert len(requests) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("payload", [
    [], {"choices": []}, {"choices": [{}]},
    response_payload(reason=None), response_payload(reason="content_filter"),
    response_payload(reason="aborted"), response_payload(reason="tool_calls"),
    response_payload(reason="insufficient_system_resource"),
    response_payload(content='{"facts":[{"title":"interrotto'),
    response_payload(content=[]), response_payload(content='{"facts":false}'),
])
async def test_extraction_does_not_retry_other_provider_or_format_errors(monkeypatch, payload):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=payload)

    provider(monkeypatch, handler)
    with pytest.raises(GenerationError):
        await extract_call_facts("test", "Progetto test", source_chunks())
    assert len(requests) == 1


@pytest.mark.anyio
@pytest.mark.parametrize("tokens", [None, True, "123", -1])
async def test_retry_usage_is_unknown_if_any_attempt_has_invalid_usage(monkeypatch, tokens):
    count = 0

    def handler(_request):
        nonlocal count
        count += 1
        return httpx.Response(200, json=response_payload(
            reason="length" if count == 1 else "stop", tokens=tokens if count == 1 else 123,
        ))

    provider(monkeypatch, handler)
    result = await extract_call_facts("test", "Progetto test", source_chunks())
    assert count == 2
    assert result.total_tokens is None


@pytest.mark.anyio
async def test_extraction_has_a_total_deadline(monkeypatch):
    async def handler(_request):
        await asyncio.sleep(1)
        return httpx.Response(200, json=response_payload())

    provider(monkeypatch, handler)
    monkeypatch.setattr("app.fact_extraction.EXTRACTION_TIMEOUT_SECONDS", 0.01)
    with pytest.raises(GenerationError, match="tempo massimo"):
        await extract_call_facts("test", "Progetto test", source_chunks())


def test_json_diagnostics_do_not_log_response_content(caplog):
    with pytest.raises(GenerationError, match="JSON non valida"):
        parse_extracted_facts('{"facts":[{"title":"SEGRETO-DI-PROGETTO', 1)
    assert "Invalid extraction JSON" in caplog.text
    assert "SEGRETO-DI-PROGETTO" not in caplog.text
