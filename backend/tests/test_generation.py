import asyncio
import json

import httpx
import pytest

from app import generation
from app.config import DeepSeekSettings, use_ai_settings
from app.generation import GenerationError, _build_user_prompt, _parse_content


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _settings(provider):
    return DeepSeekSettings(
        api_key=None if provider == "ollama" else "test-key",
        model="test-model",
        base_url="http://provider.test",
        provider=provider,
    )


@pytest.fixture
def mock_transport(monkeypatch):
    client_class = httpx.AsyncClient

    def install(handler):
        monkeypatch.setattr(
            generation.httpx,
            "AsyncClient",
            lambda **kwargs: client_class(transport=httpx.MockTransport(handler), **kwargs),
        )

    return install


@pytest.mark.anyio
@pytest.mark.parametrize("provider,read_timeout", [("ollama", 180), ("deepseek", 30)])
async def test_chat_allows_ollama_loading_and_parses_answer(mock_transport, provider, read_timeout):
    requests = []
    content = json.dumps({"answer": "La scadenza e il 15 settembre [1].", "citation_ids": [1]})

    def handler(request):
        requests.append(request)
        assert request.extensions["timeout"] == {
            "connect": 10,
            "read": read_timeout,
            "write": 30,
            "pool": 30,
        }
        if provider == "ollama":
            assert request.url.path == "/api/chat"
            assert json.loads(request.content)["stream"] is False
            return httpx.Response(
                200,
                json={
                    "message": {"content": content},
                    "done": True,
                    "done_reason": "stop",
                    "prompt_eval_count": 100,
                    "eval_count": 20,
                },
            )
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"total_tokens": 120},
            },
        )

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        answer = await generation.generate_grounded_answer(
            "Qual e la scadenza?",
            [{"source_name": "bando.pdf", "chunk_index": 0, "content": "Scadenza: 15 settembre"}],
        )
    assert answer.citations == [1]
    assert answer.total_tokens == 120
    assert len(requests) == 1


@pytest.mark.anyio
@pytest.mark.parametrize("provider,read_timeout", [("ollama", 180), ("deepseek", 30)])
@pytest.mark.parametrize(
    "error,expected",
    [
        (httpx.ReadTimeout, "non ha inviato dati entro {read_timeout} secondi"),
        (httpx.ConnectTimeout, "non riuscito entro 10 secondi"),
        (httpx.WriteTimeout, "Tempo di attesa scaduto"),
        (httpx.PoolTimeout, "Tempo di attesa scaduto"),
        (httpx.ConnectError, "non e raggiungibile"),
    ],
)
async def test_chat_distinguishes_timeouts_without_retry(
    mock_transport, provider, read_timeout, error, expected
):
    requests = []

    def handler(request):
        requests.append(request)
        raise error("synthetic failure", request=request)

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        with pytest.raises(GenerationError, match=expected.format(read_timeout=read_timeout)):
            await generation.generate_grounded_answer("riassumi il bando", [])
    assert len(requests) == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "provider,deadline_setting",
    [("ollama", "OLLAMA_CHAT_TIMEOUT_SECONDS"), ("deepseek", "CHAT_TIMEOUT_SECONDS")],
)
async def test_chat_total_deadline_cancels_request(
    monkeypatch, mock_transport, provider, deadline_setting
):
    monkeypatch.setattr(generation, deadline_setting, 0.01)
    cancelled = asyncio.Event()
    requests = []

    async def handler(request):
        requests.append(request)
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        with pytest.raises(
            GenerationError, match="non ha completato la risposta entro 0.01 secondi"
        ):
            await generation.generate_grounded_answer("riassumi il bando", [])
    assert cancelled.is_set()
    assert len(requests) == 1


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


def test_generation_prompt_includes_evidence_and_recent_history():
    prompt = _build_user_prompt(
        "Mapi puo presentare domanda?",
        [
            {
                "source_name": "bando.pdf",
                "chunk_index": 4,
                "content": "Sono ammessi esclusivamente gli Enti locali.",
            },
            {
                "source_name": "profilo-mapi.md",
                "chunk_index": 0,
                "content": "Mapi e una societa privata di ingegneria civile.",
            },
        ],
        [
            {
                "question": "Quali soggetti sono ammessi?",
                "answer": "Sono ammessi gli enti locali [1].",
            }
        ],
    )

    assert "EVIDENZE DISPONIBILI" in prompt
    assert "profilo-mapi.md" in prompt
    assert "CRONOLOGIA RECENTE NON FATTUALE" in prompt
    assert "Quali soggetti sono ammessi?" in prompt
