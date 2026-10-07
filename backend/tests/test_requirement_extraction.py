"""Extraction contracts with simulated providers, not a semantic model benchmark."""

import json

import httpx
import pytest

from app import intents
from app.config import AISettings, use_ai_settings
from app.generation import GenerationError
from app.requirement_checks import Requirement, RequirementPlan, validate_requirements

QUESTIONS = [
    "Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti?",
    "Quali dati possiamo già compilare?",
    "Con i documenti disponibili, cosa possiamo compilare?",
    "Abbiamo abbastanza informazioni per iniziare?",
    "Cosa ci manca per completare questa sezione?",
    "Possiamo completare oggi il modulo?",
    "Quali informazioni risultano già disponibili?",
]
FIELDS = [
    "Denominazione sociale", "iscrizione alla CCIAA", "numero e data d’iscrizione",
    "forma giuridica", "sede legale", "Nome e cognome", "qualifica professionale",
    "Data di abilitazione", "Ordine professionale", "numero di iscrizione all’Albo",
    "organigramma",
]
FORM = {
    "role": "form", "source_name": "domanda.txt", "file_id": 10, "chunk_id": 100,
    "content": "5.d) SOCIETÀ DI INGEGNERIA\n" + ":\n".join(FIELDS[:5]) + ":\n"
    + "direttore tecnico:\n" + ":\n".join(FIELDS[5:10]) + ":\nsi allega l’organigramma",
}


def extraction_response():
    result = {"requirements": [
        {"name": name, "form_citation_id": 1,
         "person_role": "direttore tecnico" if 5 <= i < 10 else "",
         "form_quote": name}
        for i, name in enumerate(FIELDS)
    ]}
    for item in result["requirements"]:
        if item["person_role"]:
            start = FORM["content"].index("direttore tecnico:")
            end = FORM["content"].index(item["name"], start) + len(item["name"])
            item["form_quote"] = FORM["content"][start:end]
    return result


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def provider(monkeypatch):
    original = httpx.AsyncClient
    def install(kind, replies):
        requests = []
        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            assert replies, "Extraction exceeded its bounded attempts"
            content = json.dumps(replies.pop(0), ensure_ascii=False)
            if kind == "ollama":
                return httpx.Response(200, json={
                    "message": {"content": content}, "done": True, "done_reason": "stop",
                    "prompt_eval_count": 20, "eval_count": 10,
                })
            return httpx.Response(200, json={
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"total_tokens": 30},
            })
        monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(
            transport=httpx.MockTransport(handler), **kw,
        ))
        settings = AISettings(provider=kind, model="simulated", api_key="test",
                              base_url="http://provider.test")
        return settings, requests
    return install


@pytest.mark.anyio
@pytest.mark.parametrize("kind", ["deepseek", "ollama"])
@pytest.mark.parametrize("question", QUESTIONS)
async def test_equivalent_mixed_requests_keep_grounded_atomic_requirements(
    provider, kind, question,
):
    settings, requests = provider(kind, [extraction_response()])
    with use_ai_settings(settings):
        result = await intents.plan_requirement_checks(question, [FORM])
    assert {r.name for r in result.plan.requirements} == set(FIELDS)
    assert len(result.plan.requirements) == 11  # The old max-eight contract rejected this section.
    assert result.attempts == 1
    prompt = json.loads(requests[0]["messages"][1]["content"])
    assert prompt["evidenze_FORM"][0]["testo"] == FORM["content"]
    assert prompt["schema_output"]["properties"]["requirements"]["maxItems"] >= 11
    assert "A CUI RISPONDERE" not in requests[0]["messages"][1]["content"]
    if kind == "ollama":
        assert requests[0]["format"] == prompt["schema_output"]


@pytest.mark.anyio
async def test_empty_extraction_has_one_focused_retry_with_same_form(provider):
    settings, requests = provider("deepseek", [{"requirements": []}, extraction_response()])
    with use_ai_settings(settings):
        result = await intents.plan_requirement_checks(QUESTIONS[0], [FORM])
    assert result.attempts == 2 and result.total_tokens == 60
    assert len(result.plan.requirements) == 11
    assert requests[1]["messages"][1] == requests[0]["messages"][1]
    assert "L'elenco è vuoto" in requests[1]["messages"][-1]["content"]


@pytest.mark.anyio
async def test_retry_reports_actual_schema_violation_instead_of_generic_quote_error(provider):
    invalid = {"requirements": extraction_response()["requirements"] * 3}
    settings, requests = provider("deepseek", [invalid, extraction_response()])
    with use_ai_settings(settings):
        result = await intents.plan_requirement_checks(QUESTIONS[0], [FORM])
    assert result.attempts == 2
    repair = requests[1]["messages"][-1]["content"]
    assert "at most 32" in repair and "requirements" in repair


@pytest.mark.anyio
@pytest.mark.parametrize("change", [
    {"form_citation_id": 99}, {"form_quote": "ISO 9001", "name": "ISO 9001"},
    {"person_role": "responsabile non documentato"},
])
async def test_two_ungrounded_extractions_stop_without_inventing_requirements(provider, change):
    item = {**extraction_response()["requirements"][0], **change}
    settings, requests = provider("deepseek", [{"requirements": [item]}] * 2)
    with use_ai_settings(settings), pytest.raises(
        GenerationError, match="disponibilità non è stata valutata",
    ):
        await intents.plan_requirement_checks("Il modulo richiede ISO 9001: la possediamo?", [FORM])
    assert len(requests) == 2


@pytest.mark.parametrize("name,quote,text", [
    ("Denominazione sociale", "Denominazione sociale:", "DENOMINAZIONE\n SOCIALE"),
    ("società", "SOCIETÀ:", "societa\u0300:\u00a0"),
    ("numero d'iscrizione", "numero d'iscrizione:", "numero d’iscrizione:\n"),
])
def test_conservative_form_normalization_accepts_typography(name, quote, text):
    plan = RequirementPlan(requirements=[Requirement(
        name=name, form_quote=quote, form_citation_id=1,
    )])
    assert validate_requirements(plan, [{"role": "form", "content": text}]).requirements


@pytest.mark.parametrize("quote", ["ISO 9001", "non richiesta ISO 90010", "ISO 90010 richiesta"])
def test_form_normalization_does_not_change_words_numbers_or_order(quote):
    plan = RequirementPlan(requirements=[Requirement(
        name=quote, form_quote=quote, form_citation_id=1,
    )])
    with pytest.raises(ValueError):
        validate_requirements(plan, [{"role": "form", "content": "richiesta ISO 90010"}])


def test_same_label_from_another_evidence_cannot_ground_the_selected_section():
    plan = RequirementPlan(requirements=[Requirement(
        name="Sede legale", form_quote="Sede legale", form_citation_id=1,
    )])
    with pytest.raises(ValueError):
        validate_requirements(plan, [
            {"role": "form", "content": "Sezione persone: Residenza"},
            {"role": "form", "content": "Sezione società: Sede legale"},
        ])


def test_deduplication_preserves_same_field_for_different_subjects():
    forms = [{"role": "form", "content": "Direttore tecnico: Nome\nAmministratore: Nome"}]
    requirements = [Requirement(
        name="Nome", person_role=person_role, form_quote=f"{person_role}: Nome", form_citation_id=1,
    ) for person_role in ("Direttore tecnico", "Amministratore")]
    plan = validate_requirements(RequirementPlan(requirements=requirements * 2), forms)
    assert len(plan.requirements) == 2


def test_valid_requirements_exceeding_context_budget_do_not_invalidate_extraction():
    requirements = [Requirement(name=f"Campo {i}", form_quote=f"Campo {i}", form_citation_id=1)
                    for i in range(17)]
    forms = [{"role": "form", "content": "\n".join(r.name for r in requirements)}]
    plan = validate_requirements(RequirementPlan(requirements=requirements), forms)
    assert plan.requirements == requirements[:16]


def test_grounding_retry_feedback_includes_all_invalid_fields():
    requirements = [Requirement(name=name, form_quote=name, form_citation_id=1,
                                person_role="direttore tecnico")
                    for name in ("Nome e cognome", "Data di abilitazione")]
    with pytest.raises(ValueError) as caught:
        validate_requirements(RequirementPlan(requirements=requirements), [FORM])
    assert "Nome e cognome" in str(caught.value) and "Data di abilitazione" in str(caught.value)


def test_long_contiguous_context_is_valid_without_dropping_person_role_grounding():
    content = "Direttore tecnico: " + ("Istruzioni del modulo. " * 25) + "Data di abilitazione"
    requirement = Requirement(
        name="Data di abilitazione", person_role="Direttore tecnico", form_quote=content,
        form_citation_id=1,
    )
    assert len(content) > 500
    plan = validate_requirements(RequirementPlan(requirements=[requirement]), [
        {"role": "form", "content": content},
    ])
    assert plan.requirements == [requirement]
