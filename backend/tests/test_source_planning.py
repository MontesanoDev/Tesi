"""Bounded SOURCE planning and per-requirement provenance, with simulated AI."""

import json

import pytest

from app import source_planning
from app.requirement_checks import (
    Requirement,
    RequirementChecks,
    SourceSupport,
    render_requirement_checks,
    validated_supports,
)
from app.source_planning import (
    MAX_CLUSTER_EVIDENCE,
    MAX_SOURCE_CLUSTERS,
    SourceClusters,
    cluster_queries,
    plan_source_search,
    validate_source_plan,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


def requirements(count=16):
    return [Requirement(name=f"Campo{n:02}", form_quote=f"Campo{n:02}", form_citation_id=1)
            for n in range(1, count + 1)]


def test_sixteen_requirements_have_explicit_coverage_and_bounded_queries():
    reqs = requirements()
    plan = validate_source_plan(SourceClusters(clusters=[
        {"requirement_ids": list(range(start, start + 4))} for start in (1, 5, 9, 13)
    ]), reqs)
    queries = [query for cluster in plan.clusters for query in cluster_queries(cluster, reqs)]
    assert plan.not_searched == set()
    assert len(plan.clusters) <= MAX_SOURCE_CLUSTERS
    assert len(queries) == 8
    for req in reqs:
        assert any(req.name in query for query in queries)
    assert MAX_SOURCE_CLUSTERS * MAX_CLUSTER_EVIDENCE == 24


def test_budget_exclusions_are_not_silently_unverified_or_verified():
    reqs = requirements()
    plan = validate_source_plan(SourceClusters(clusters=[]), reqs)
    assert plan.not_searched == set(range(7, 17))
    searched = set(range(1, 17)) - plan.not_searched
    answer, _, missing = render_requirement_checks(reqs, {}, searched_ids=searched)
    assert "Campo06: disponibilità non verificata" in answer
    assert "Campo07: non ricercato per limite" in answer
    assert "Campo07: disponibilità non verificata" not in answer
    assert len(missing) == 16


def test_oversized_valid_group_is_split_without_losing_coverage():
    reqs = requirements(11)
    plan = validate_source_plan(SourceClusters(clusters=[
        {"requirement_ids": list(range(1, 6))}, {"requirement_ids": list(range(6, 11))},
        {"requirement_ids": [11]},
    ]), reqs)
    assert len(plan.clusters) == 5
    assert plan.not_searched == set()
    assert all(len(cluster.requirement_ids) <= 4 for cluster in plan.clusters)
    assert {i for cluster in plan.clusters for i in cluster.requirement_ids} == set(range(1, 12))


@pytest.mark.parametrize("groups", [[[1, 99]], [[1, 1]], [[1], [1]]])
def test_unknown_and_duplicate_requirement_ids_are_rejected(groups):
    with pytest.raises(ValueError):
        validate_source_plan(SourceClusters(clusters=[{"requirement_ids": ids} for ids in groups]),
                             requirements())


def test_people_with_different_roles_cannot_share_cluster():
    reqs = [r.model_copy(update={"person_role": role}) for r, role in
            zip(requirements(2), ("Presidente", "Tesoriere"), strict=True)]
    with pytest.raises(ValueError):
        validate_source_plan(SourceClusters(clusters=[{"requirement_ids": [1, 2]}]), reqs)


@pytest.mark.anyio
@pytest.mark.parametrize("raw", [
    '{"clusters":[]}', '{"clusters":[{"requirement_ids":[999]}]}', 'bad',
])
async def test_planner_has_one_batch_only_and_explicit_fallback(monkeypatch, raw):
    calls = []
    async def provider(client, settings, body, *args, **kwargs):
        calls.append(body)
        assert json.loads(body["messages"][1]["content"])["schema_output"]
        return raw, "mock", {"total_tokens": 7}
    monkeypatch.setattr(source_planning, "request_model_content", provider)
    result = await plan_source_search(requirements())
    assert len(calls) == 1 and result.total_tokens == 7
    assert len(result.clusters) == 6 and len(result.not_searched) == 10


def test_source_from_another_cluster_or_unsearched_requirement_cannot_verify():
    reqs = requirements(2)
    form = {"role": "form", "content": "Campo01 Campo02"}
    source = {"role": "source", "content": "Campo02: Valore reale"}
    check = RequirementChecks(supports=[SourceSupport(
        requirement_id=2, source_citation_id=2,
        source_quote=source["content"], value="Valore reale",
    )])
    for coverage in ({1: {2}}, {1: {2}, 2: set()}):
        with pytest.raises(ValueError):
            validated_supports(check, reqs, [form], [source], source_coverage=coverage)
        assert validated_supports(check, reqs, [form], [source], source_coverage=coverage,
                                  discard_invalid=True) == {}


@pytest.mark.parametrize("text", [
    "Direttore tecnico: Elisa Romano. Numero di iscrizione professionale simulato: 8421.",
    "DIRETTORE TECNICO Ing. Elisa Romano - iscrizione professionale simulata n. 8421, "
    "Ordine degli Ingegneri di Bari",
    "Direttore tecnico: Elisa Romano; iscrizione all'Albo professionale n. 8421.",
])
def test_professional_number_has_grounded_equivalent_label(text):
    form = {"role": "form",
            "content": "Direttore tecnico: numero di iscrizione all’Albo professionale"}
    req = Requirement(name="numero di iscrizione all’Albo professionale",
                      person_role="Direttore tecnico",
                      form_quote=form["content"], form_citation_id=1)
    check = RequirementChecks(supports=[SourceSupport(
        requirement_id=1, source_citation_id=2, source_quote=text, value="8421",
    )])
    result = validated_supports(check, [req], [form], [{"role": "source", "content": text}])
    assert result[1].value == "8421" and result[1].source_citation_id == 2


@pytest.mark.parametrize("text", [
    "Direttore tecnico: numero di iscrizione all'Albo professionale: 7777; telefono 8421.",
    "Direttore tecnico: iscrizione professionale n. 7777. Codice fattura 8421.",
    "Direttore tecnico: Ordine professionale non indicato. Codice aziendale: 8421.",
    "Amministratore: iscrizione professionale n. 8421.",
    "Direttore tecnico: iscrizione alla CCIAA n. 8421.",
    "Direttore tecnico: non ha iscrizione professionale n. 8421.",
])
def test_unrelated_number_cannot_become_professional_registration(text):
    req = Requirement(name="numero di iscrizione all’Albo professionale",
                      person_role="Direttore tecnico",
                      form_quote="Direttore tecnico: numero di iscrizione all’Albo professionale",
                      form_citation_id=1)
    check = RequirementChecks(supports=[SourceSupport(
        requirement_id=1, source_citation_id=2, source_quote=text, value="8421",
    )])
    with pytest.raises(ValueError):
        validated_supports(check, [req], [{"role": "form", "content": req.form_quote}],
                           [{"role": "source", "content": text}])


@pytest.mark.parametrize("label", [
    "Nome e cognome", "qualifica professionale", "Data di abilitazione",
])
@pytest.mark.parametrize("separator", [".\n", "\n"])
def test_number_in_full_person_record_cannot_support_another_personal_field(label, separator):
    text = separator.join((
        "Direttore tecnico: Nome e cognome: Elisa Romano",
        "qualifica professionale: Ingegnere",
        "Numero di iscrizione professionale: 8421",
        "Data di abilitazione: non disponibile",
    ))
    req = Requirement(
        name=label, person_role="Direttore tecnico", form_quote=label, form_citation_id=1,
    )
    checks = RequirementChecks(supports=[SourceSupport(
        requirement_id=1, source_citation_id=2, source_quote=text, value="8421",
    )])
    with pytest.raises(ValueError):
        validated_supports(checks, [req], [{"role": "form", "content": label}],
                           [{"role": "source", "content": text}])
