"""Provenance gates, independent of the quality of a real model."""

import pytest

from app.intents import ChatDecision, route_availability_request
from app.requirement_checks import (
    Requirement,
    RequirementChecks,
    RequirementPlan,
    availability_requested,
    claims_availability,
    render_requirement_checks,
    requirement_source_queries,
    validate_requirements,
    validated_supports,
)

FORM = {"role": "form", "content": "Denominazione sociale: ____\nDirettore tecnico: ____"}
SOURCE = {"role": "source", "content": "Mapi Ingegneria S.r.l."}
REQUIREMENTS = [
    Requirement(name=name, form_quote=name, form_citation_id=1)
    for name in ("Denominazione sociale", "Direttore tecnico")
]


@pytest.mark.parametrize("question", [
    "con i documenti che ho posso iniziare a compilarlo?",
    "posso compilare la denominazione sociale?",
    "Abbiamo i dati richiesti dal modulo?",
    "Cosa mi manca per completare la domanda?",
    "Possiamo soddisfare questo requisito?",
    "Questo campo può essere valorizzato?",
])
def test_explicit_availability_is_mixed_even_when_planner_selects_form(question):
    decision = ChatDecision(action="retrieve", target="form", answer="", queries=["requisiti"])
    result = route_availability_request(decision, question, [{"id": 4, "name": "domanda.docx"}])
    assert availability_requested(question)
    assert result.target == "mixed" and result.form_id == 4
    assert result.source_queries == []  # They can only be built after reading FORM.


@pytest.mark.parametrize("question", [
    "riassumi la domanda di partecipazione", "quali sezioni devo compilare?",
    "qual è la partita IVA di Mapi?", "cosa richiede il modulo sul direttore tecnico?",
])
def test_normal_documental_and_factual_requests_keep_planned_target(question):
    decision = ChatDecision(action="retrieve", target="source", answer="", queries=["dato"])
    assert route_availability_request(decision, question, []) is decision


@pytest.mark.parametrize("text", [
    "è possibile compilare la denominazione sociale [1]",
    "Abbiamo la sede legale [1]", "Questo dato è disponibile [1]",
    "Possiamo compilare X [1]", "Abbiamo la sede legale disponibile [1]",
    "Il direttore tecnico è disponibile [1]", "Questo campo può essere valorizzato [1]",
    "I documenti disponibili contengono questo dato [1]",
])
def test_availability_language_is_not_a_requirement(text):
    assert claims_availability(text)


def test_requirements_and_queries_are_grounded_in_actual_form():
    plan = validate_requirements(RequirementPlan(requirements=REQUIREMENTS), [FORM])
    queries = requirement_source_queries(plan.requirements)
    assert queries == [
        "Denominazione sociale ragione sociale S.r.l. S.p.A. dati effettivi operatore economico",
        "Direttore tecnico dati effettivi operatore economico",
    ]
    invalid = Requirement(name="Sede legale", form_quote="Sede legale", form_citation_id=1)
    with pytest.raises(ValueError):
        validate_requirements(RequirementPlan(requirements=[invalid]), [FORM])


def test_repeated_grounded_requirement_is_deduplicated_before_source_queries():
    plan = validate_requirements(RequirementPlan(requirements=[
        REQUIREMENTS[0], REQUIREMENTS[0], REQUIREMENTS[0].model_copy(update={
            "form_quote": "Duplice proposta ignorata, senza riscontro",
        }),
    ]), [FORM])
    assert plan.requirements == [REQUIREMENTS[0]]
    assert len(requirement_source_queries(plan.requirements)) == 1


def test_generic_personal_field_without_same_role_in_both_quotes_is_unverified():
    requirement = Requirement(
        name="Nome e cognome", form_quote="Nome e cognome", form_citation_id=1,
    )
    form = {"role": "form", "content": "Nome e cognome: ____"}
    source = {"role": "source", "content": "Nome e cognome: Luca Ferri, amministratore"}
    with pytest.raises(ValueError):
        validated_supports(RequirementChecks(supports=[support(
            source_quote=source["content"], value="Luca Ferri",
        )]), [requirement], [form], [source])


def test_empty_sources_never_prove_availability():
    verified = validated_supports(RequirementChecks(supports=[]), REQUIREMENTS, [FORM], [])
    answer, citations, missing = render_requirement_checks(REQUIREMENTS, verified)
    assert "non posso ancora considerarli compilabili" in answer
    assert "Denominazione sociale: disponibilità non verificata" in answer
    assert "Direttore tecnico: disponibilità non verificata" in answer
    assert "utilizzabile per una prima compilazione" not in answer
    assert citations == [1] and missing == [r.name for r in REQUIREMENTS]


def support(**changes):
    return {"requirement_id": 1, "source_citation_id": 2,
            "source_quote": SOURCE["content"], "value": SOURCE["content"], **changes}


def test_value_support_is_per_requirement_not_global_availability():
    checks = RequirementChecks(supports=[support()])
    verified = validated_supports(checks, REQUIREMENTS, [FORM], [SOURCE])
    answer, citations, missing = render_requirement_checks(REQUIREMENTS, verified)
    assert "Denominazione sociale: Mapi Ingegneria S.r.l. [2]" in answer
    assert "Direttore tecnico: disponibilità non verificata" in answer
    assert citations == [1, 2] and missing == ["Direttore tecnico"]


def test_after_repair_only_proved_values_survive_and_other_requirements_are_unverified():
    checks = RequirementChecks(supports=[support(), support(requirement_id=2)])
    verified = validated_supports(checks, REQUIREMENTS, [FORM], [SOURCE], discard_invalid=True)
    assert set(verified) == {1}
    answer, citations, missing = render_requirement_checks(REQUIREMENTS, verified)
    assert "Denominazione sociale: Mapi Ingegneria S.r.l." in answer
    assert "Direttore tecnico: disponibilità non verificata" in answer
    assert missing == ["Direttore tecnico"] and citations == [1, 2]


def test_competing_values_after_repair_are_not_arbitrarily_verified():
    checks = RequirementChecks(supports=[support(), support()])
    assert validated_supports(checks, REQUIREMENTS, [FORM], [SOURCE], discard_invalid=True) == {}


@pytest.mark.parametrize("changes", [
    {"source_citation_id": 1}, {"source_citation_id": 999}, {"requirement_id": 999},
    {"requirement_id": 2}, {"value": "Mario Rossi"}, {"source_quote": "Testo inventato"},
])
def test_form_wrong_requirement_and_unquoted_values_cannot_pass_gate(changes):
    with pytest.raises(ValueError):
        validated_supports(
            RequirementChecks(supports=[support(**changes)]), REQUIREMENTS, [FORM], [SOURCE],
        )


def test_a_general_iso_rule_is_not_a_certification_value():
    requirement = Requirement(
        name="Certificazione ISO 9001", form_quote="Certificazione ISO 9001", form_citation_id=1,
    )
    form = {"role": "form", "content": "Certificazione ISO 9001: ____"}
    source = {"role": "source", "content": "Certificazione ISO 9001: norme e criteri generali"}
    with pytest.raises(ValueError):
        validated_supports(RequirementChecks(supports=[support(
            source_quote=source["content"], value="ISO 9001",
        )]), [requirement], [form], [source])


@pytest.mark.parametrize("quote,value", [
    ("Direttore tecnico: Numero di iscrizione: 8421", "8421"),
    ("Amministratore: Data di abilitazione: 01/01/2000", "01/01/2000"),
    ("Direttore tecnico: Data di abilitazione: non disponibile", "non disponibile"),
])
def test_other_director_field_other_subject_and_explicit_missing_value_cannot_verify_date(
    quote, value,
):
    form = {"role": "form", "content": "Direttore tecnico: Data di abilitazione"}
    requirement = Requirement(
        name="Data di abilitazione", person_role="Direttore tecnico", form_quote=form["content"],
        form_citation_id=1,
    )
    with pytest.raises(ValueError):
        validated_supports(RequirementChecks(supports=[support(
            source_quote=quote, value=value,
        )]), [requirement], [form], [{"role": "source", "content": quote}])
