import asyncio
import json

import httpx
import pytest

from app import generation
from app.config import AISettings, use_ai_settings
from app.generation import GenerationError, _build_user_prompt, _parse_content, _parse_mixed_content
from app.requirement_checks import Requirement


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


FORM_CONTEXT = [{
    "role": "form", "source_name": "domanda.txt", "content": "Certificazione ISO 9001: ______",
    "scope": "project:alpha", "category": None,
}]
FACTUAL_CONTEXT = [{
    "role": "source", "source_name": "dati.txt",
    "content": "Certificazione ISO 9001 di Mapi: MAPI-QMS-2024-001.",
    "scope": "global", "category": "general",
}]
REQUIREMENTS = [Requirement(
    name="Certificazione ISO 9001", form_quote="Certificazione ISO 9001:", form_citation_id=1,
)]


def mixed_support(citation=2):
    return {"requirement_id": 1, "source_citation_id": citation,
            "source_quote": FACTUAL_CONTEXT[0]["content"], "value": "MAPI-QMS-2024-001"}


def test_mixed_parser_keeps_requirements_and_facts_with_their_own_citations():
    response = {"supports": [mixed_support()]}
    answer = _parse_mixed_content(
        json.dumps(response), FORM_CONTEXT, FACTUAL_CONTEXT, "test", {}, requirements=REQUIREMENTS,
    )
    assert answer.citations == [1, 2]
    requirement_position = answer.answer.index("Requisiti del modulo")
    assert requirement_position < answer.answer.index("Informazioni verificate")
    assert "non certifica la completezza" in answer.answer


@pytest.mark.parametrize("citation", [1, 0, 9])
def test_mixed_parser_rejects_form_and_unavailable_source_citations(citation):
    with pytest.raises(GenerationError):
        _parse_mixed_content(
            json.dumps({"supports": [mixed_support(citation)]}),
            FORM_CONTEXT, FACTUAL_CONTEXT, "test", {}, requirements=REQUIREMENTS,
        )


def test_mixed_parser_cannot_create_fact_when_only_form_exists():
    invalid = {"supports": [mixed_support(1)]}
    with pytest.raises(GenerationError):
        _parse_mixed_content(
            json.dumps(invalid), FORM_CONTEXT, [], "test", {}, requirements=REQUIREMENTS,
        )


def test_mixed_parser_rejects_free_answer_outside_checked_statements():
    invalid = {"supports": [], "answer": "Tutti i dati sono disponibili: Mapi possiede ISO 9001."}
    with pytest.raises(GenerationError, match="contratto"):
        _parse_mixed_content(
            json.dumps(invalid), FORM_CONTEXT, [], "test", {}, requirements=REQUIREMENTS,
        )


@pytest.mark.anyio
@pytest.mark.parametrize("provider", ["ollama", "deepseek"])
async def test_mixed_generation_uses_existing_transport_and_role_contract(mock_transport, provider):
    calls = []
    content = json.dumps({"supports": [mixed_support()]})
    def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        if provider == "ollama":
            assert "supports" in body["format"]["properties"]
        return _provider_response(provider, content)
    mock_transport(handler)
    with use_ai_settings(_settings(provider)):
        answer = await generation.generate_grounded_answer(
            "Abbiamo i dati richiesti?", FORM_CONTEXT, factual_evidence=FACTUAL_CONTEXT,
            requirements=REQUIREMENTS,
        )
    assert answer.citations == [1, 2] and len(calls) == 1
    prompt = calls[0]["messages"][1]["content"]
    assert "REQUISITI DEL MODULO (role=form)" in prompt
    assert "FONTI FATTUALI (role=source)" in prompt
    assert "Scope: global; KB category: general" in prompt


@pytest.mark.anyio
async def test_mixed_generation_rejects_misrouted_context_before_any_model_call(mock_transport):
    mock_transport(lambda *args: pytest.fail("No generation with misrouted contexts"))
    with use_ai_settings(_settings("deepseek")):
        with pytest.raises(GenerationError, match="Contesti form/source"):
            await generation.generate_grounded_answer(
                "Abbiamo i dati richiesti?", FORM_CONTEXT, factual_evidence=FORM_CONTEXT,
            )


@pytest.mark.anyio
async def test_mixed_repair_keeps_valid_denomination_and_discards_wrong_director(mock_transport):
    forms = [{"role": "form", "source_name": "domanda.txt",
              "content": "Denominazione sociale: ____\nDirettore tecnico: ____"}]
    sources = [{"role": "source", "source_name": "azienda.txt",
                "content": "Mapi Ingegneria S.r.l."}]
    requirements = [Requirement(name=name, form_quote=name, form_citation_id=1)
                    for name in ("Denominazione sociale", "Direttore tecnico")]
    calls = []
    def handler(request):
        calls.append(json.loads(request.content))
        return _provider_response("deepseek", json.dumps({"supports": [
            {"requirement_id": index, "source_citation_id": 2,
             "source_quote": "Mapi Ingegneria S.r.l.", "value": "Mapi Ingegneria S.r.l."}
            for index in (1, 2)
        ]}))
    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        answer = await generation.generate_grounded_answer(
            "Abbiamo i dati richiesti?", forms, factual_evidence=sources, requirements=requirements,
        )
    assert len(calls) == 2 and answer.total_tokens == 240
    assert calls[1]["messages"][:2] == calls[0]["messages"]
    assert "Denominazione sociale: Mapi Ingegneria S.r.l. [2]" in answer.answer
    assert "Direttore tecnico: disponibilità non verificata" in answer.answer
    assert answer.missing_information == ["Direttore tecnico"]


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
async def test_mixed_accepts_registration_number_without_literal_albo_or_repair(
    mock_transport,
):
    form = {"role": "form", "source_name": "modulo.txt",
            "content": "Direttore tecnico: numero di iscrizione all’Albo professionale"}
    short = "Direttore tecnico: numero di iscrizione professionale: 8421."
    source = {"role": "source", "source_name": "scheda.txt",
              "content": short}
    requirement = Requirement(
        name="numero di iscrizione all’Albo professionale", person_role="Direttore tecnico",
        form_quote=form["content"], form_citation_id=1,
    )
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        quote = short if len(requests) == 1 else source["content"]
        return _provider_response("deepseek", json.dumps({"supports": [{
            "requirement_id": 1, "source_citation_id": 2,
            "source_quote": quote, "value": "8421",
        }]}))
    mock_transport(handler)
    with use_ai_settings(_settings("deepseek")):
        result = await generation.generate_grounded_answer(
            "Abbiamo il dato richiesto?", [form], factual_evidence=[source],
            requirements=[requirement],
        )
    assert len(requests) == 1
    assert "8421" in result.answer and result.missing_information == []


def test_source_matching_task_is_independent_of_question_and_history_wording():
    forms = [{"role": "form", "source_name": "modulo", "content": "Denominazione sociale"}]
    sources = [{"role": "source", "source_name": "fonte", "content": "Mapi S.r.l."}]
    prompts = [generation._build_user_prompt(
        question, forms, [{"question": "Abbiamo tutto?", "answer": "Sì, tutto compilabile [1]."}],
        factual_evidence=sources,
    ) for question in ("Quali dati mancano?", "Quali dati possiamo compilare?", "Abbiamo tutto?")]
    assert len(set(prompts)) == 1
    assert "Sì, tutto compilabile" not in prompts[0]
    assert "TUTTI i requisiti" in prompts[0]
    assert "REQUISITI DEL MODULO (role=form)" in prompts[0]
    assert "FONTI FATTUALI (role=source)" in prompts[0]
    # JSON-mode providers reject the request before generation without this word.
    assert "json" in prompts[0].casefold()
    assert "json" in generation.MIXED_SYSTEM_PROMPT.casefold()


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
