import asyncio
import json

import httpx
import pytest

from app import generation
from app.config import AISettings, use_ai_settings
from app.generation import GenerationError, _build_user_prompt, _parse_content


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _settings(provider):
    return AISettings(
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
    assert "CITAZIONI AMMESSE: [1], [2]" in prompt
    assert "EVIDENZA [1]" in prompt
    assert "EVIDENZA [2]" in prompt
    assert "Frammento: 5" not in prompt


def _provider_response(provider, content, tokens=120, finish="stop"):
    if provider == "ollama":
        return httpx.Response(200, json={
            "message": {"content": content},
            "done": True,
            "done_reason": finish,
            "prompt_eval_count": tokens - 20,
            "eval_count": 20,
        })
    return httpx.Response(200, json={
        "choices": [{"message": {"content": content}, "finish_reason": finish}],
        "usage": {"total_tokens": tokens},
    })


_EVIDENCE = [{
    "source_name": "bando.pdf", "chunk_index": 23, "content": "Scadenza: 15 settembre",
}]
_INVALID_ANSWER = '{"answer":"La scadenza e il 15 settembre [24].","citation_ids":[24]}'
_VALID_ANSWER = '{"answer":"La scadenza e il 15 settembre [1].","citation_ids":[1]}'


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["ollama", "deepseek"])
@pytest.mark.parametrize("during_repair", [False, True])
async def test_length_retry_preserves_context_and_counts_every_call(
    mock_transport, provider, during_repair,
):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        if during_repair and len(requests) == 1:
            return _provider_response(provider, _INVALID_ANSWER)
        if len(requests) == (2 if during_repair else 1):
            return _provider_response(provider, '{"answer":"parziale', finish="length")
        return _provider_response(provider, _VALID_ANSWER)

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        answer = await generation.generate_grounded_answer("Scadenza?", _EVIDENCE)
    assert len(requests) == (3 if during_repair else 2)
    assert answer.total_tokens == 120 * len(requests)
    assert answer.citations == [1]
    assert requests[-1]["messages"] == requests[-2]["messages"]
    budgets = [
        r["options"]["num_predict"] if provider == "ollama" else r["max_tokens"]
        for r in requests
    ]
    assert budgets == ([2048, 2048, 4096] if during_repair else [2048, 4096])


@pytest.mark.anyio
@pytest.mark.parametrize("with_citation_repair", [False, True])
async def test_only_one_length_retry_across_answer_and_citation_repair(
    mock_transport, with_citation_repair,
):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        if with_citation_repair and len(requests) == 2:
            return _provider_response("deepseek", _INVALID_ANSWER)
        # Even complete-looking content must be rejected if the provider truncated it.
        return _provider_response("deepseek", _VALID_ANSWER, finish="length")

    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        with pytest.raises(GenerationError, match="limite di 4096 token"):
            await generation.generate_grounded_answer("Scadenza?", _EVIDENCE)
    assert len(requests) == (3 if with_citation_repair else 2)


@pytest.mark.anyio
async def test_unknown_truncated_usage_does_not_report_partial_cost(mock_transport):
    requests = []

    def handler(request):
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(200, json={
                "choices": [{"message": {"content": '{"answer":'}, "finish_reason": "length"}],
            })
        return _provider_response("deepseek", _VALID_ANSWER)

    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        answer = await generation.generate_grounded_answer("Scadenza?", _EVIDENCE)
    assert answer.total_tokens is None
    assert len(requests) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("reason", ["content_filter", "incomplete", "tool_calls"])
async def test_other_finish_reasons_do_not_trigger_length_retry(mock_transport, reason):
    requests = []

    def handler(request):
        requests.append(request)
        return _provider_response("deepseek", _VALID_ANSWER, finish=reason)

    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        with pytest.raises(GenerationError):
            await generation.generate_grounded_answer("Scadenza?", _EVIDENCE)
    assert len(requests) == 1


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["ollama", "deepseek"])
@pytest.mark.parametrize("location", ["answer", "citation_ids"])
async def test_chat_repairs_citations_with_same_context_and_sums_tokens(
    mock_transport, provider, location,
):
    requests = []
    invalid = json.loads(_VALID_ANSWER)
    invalid[location] = "La scadenza e il 15 settembre [24]." if location == "answer" else [24]
    rejected = json.dumps(invalid)

    def handler(request):
        requests.append(json.loads(request.content))
        return _provider_response(
            provider, rejected if len(requests) == 1 else _VALID_ANSWER,
        )

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        answer = await generation.generate_grounded_answer("Qual e la scadenza?", _EVIDENCE)

    assert len(requests) == 2
    first, repair = requests
    assert repair["messages"][:2] == first["messages"]
    assert repair["messages"][2] == {"role": "assistant", "content": rejected}
    assert repair["messages"][3]["role"] == "user"
    assert "CITAZIONI AMMESSE: [1]." in repair["messages"][3]["content"]
    assert {k: v for k, v in repair.items() if k != "messages"} == {
        k: v for k, v in first.items() if k != "messages"
    }
    assert answer.answer == json.loads(_VALID_ANSWER)["answer"]
    assert answer.citations == [1]
    assert answer.total_tokens == 240
    assert answer.model == "test-model"


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["ollama", "deepseek"])
async def test_chat_stops_after_one_failed_citation_repair(mock_transport, provider):
    requests = []

    def handler(request):
        requests.append(request)
        return _provider_response(provider, _INVALID_ANSWER)

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        with pytest.raises(GenerationError, match="anche dopo un tentativo di correzione") as error:
            await generation.generate_grounded_answer("Qual e la scadenza?", _EVIDENCE)
    assert "Puoi consultare le evidenze recuperate" in str(error.value)
    assert len(requests) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["json", "schema", "http", "timeout"])
@pytest.mark.parametrize("during_repair", [False, True])
async def test_chat_does_not_retry_other_failures(mock_transport, failure, during_repair):
    requests = []

    def handler(request):
        requests.append(request)
        if during_repair and len(requests) == 1:
            return _provider_response("deepseek", _INVALID_ANSWER)
        if failure == "timeout":
            raise httpx.ReadTimeout("synthetic failure", request=request)
        if failure == "http":
            return httpx.Response(503)
        return _provider_response("deepseek", '{"answer":' if failure == "json" else "[]")

    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        with pytest.raises(GenerationError) as error:
            await generation.generate_grounded_answer("Qual e la scadenza?", _EVIDENCE)
    assert len(requests) == (2 if during_repair else 1)
    assert ("La correzione non e riuscita" in str(error.value)) is during_repair
    assert ("Puoi consultare le evidenze recuperate" in str(error.value)) is during_repair


@pytest.mark.anyio
@pytest.mark.parametrize("unknown_call", [1, 2])
@pytest.mark.parametrize("unknown_usage", [{}, None, {"total_tokens": True}, {"total_tokens": -1}])
async def test_repaired_answer_does_not_report_partial_token_cost(
    mock_transport, unknown_call, unknown_usage,
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={
            "choices": [{"message": {
                "content": _INVALID_ANSWER if len(requests) == 1 else _VALID_ANSWER,
            }}],
            "usage": unknown_usage if len(requests) == unknown_call else {"total_tokens": 120},
        })

    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        answer = await generation.generate_grounded_answer("Qual e la scadenza?", _EVIDENCE)
    assert answer.citations == [1]
    assert answer.total_tokens is None
    assert len(requests) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["ollama", "deepseek"])
@pytest.mark.parametrize("first_failure", ["citation", "length"])
async def test_retries_share_original_deadline(
    monkeypatch, mock_transport, provider, first_failure,
):
    # Record timeout scopes as well as cancellation: a second full deadline must
    # never be granted to the repair, even when the first call was fast.
    timeout = asyncio.timeout
    deadlines = []

    def bounded_timeout(delay):
        deadlines.append(delay)
        return timeout(0.03)

    monkeypatch.setattr(generation.asyncio, "timeout", bounded_timeout)
    requests = []
    cancelled = asyncio.Event()

    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            if first_failure == "length":
                return _provider_response(provider, '{"answer":"parziale', finish="length")
            return _provider_response(provider, _INVALID_ANSWER)
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()

    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        with pytest.raises(GenerationError, match="secondi"):
            await generation.generate_grounded_answer("Qual e la scadenza?", _EVIDENCE)
    assert deadlines == [180 if provider == "ollama" else 90]
    assert cancelled.is_set()
    assert len(requests) == 2
