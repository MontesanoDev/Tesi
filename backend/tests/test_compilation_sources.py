"""Compilation SOURCE associations: isolated storage and simulated semantic plans."""

import pytest
from test_compilation_sessions import anyio_backend as anyio_backend
from test_compilation_sessions import api as api
from test_compilation_sessions import create, docx, resolve, simulate, source

from app import compilation_session_resolution as resolution
from app.compilation_sources import (
    CompilationSourcePlan,
    company_property,
    compilation_queries,
    plan_compilation_search,
    source_span,
)
from app.generation import GenerationError
from app.requirement_checks import Requirement
from app.source_planning import SourceCluster

LABELS = ("Entità richiedente", "Assetto dell'ente")
PROFILE = (
    "Denominazione: Aurora Progetti S.r.l.\n"
    "Organizzazione giuridica: Societa a responsabilita limitata.\n"
    "Telefono: 05599999"
)
VALUES = {"t0.r0.c1": ["Aurora Progetti S.r.l."],
          "t0.r1.c1": ["Societa a responsabilita limitata"]}


def semantic_planner(monkeypatch, *, split=False):
    async def request(task, data, schema):
        assert schema is CompilationSourcePlan
        assert "Non proporre valori" in task
        assert data["requirements"][0]["requirement"]["name"] == LABELS[0]
        return CompilationSourcePlan(
            clusters=[{"requirement_ids": [1]}, {"requirement_ids": [2]}] if split else [
                {"requirement_ids": [1, 2]},
            ],
            fields=[
                {"requirement_id": 1, "source_names": ["Denominazione"]},
                {"requirement_id": 2, "source_names": ["Organizzazione giuridica"]},
            ],
        )

    monkeypatch.setattr(resolution, "request_structured", request)
    monkeypatch.setattr(resolution, "plan_compilation_search", plan_compilation_search)


@pytest.mark.anyio
async def test_equivalent_source_properties_resolve_and_preserve_provenance(api, monkeypatch):
    state = await create(api, docx(LABELS))
    uploaded = await source(api, PROFILE)
    simulate(monkeypatch, VALUES)
    semantic_planner(monkeypatch)
    result = await resolve(api, state)
    assert result["summary"]["resolved"] == 2
    for index, field in enumerate(result["fields"]):
        assert field["requirement"]["name"] == LABELS[index]  # FORM is never rewritten.
        assert field["provenance"] == "SOURCE"
        evidence = field["source_evidence"][0]
        assert evidence["role"] == "source"
        assert evidence["scope"] == "global" and evidence["category"] == "company"
        assert evidence["file_id"] == -uploaded["id"]
        assert evidence["source_name"] == "fonte.txt" and evidence["chunk_id"] < 0
        assert evidence["chunk_index"] == 0
    # Both independently validated properties may be supported by the same chunk.
    assert (result["fields"][0]["source_evidence"][0]["chunk_id"] ==
            result["fields"][1]["source_evidence"][0]["chunk_id"])
    url = f"/api/projects/alpha/compilation-sessions/{state['id']}"
    assert (await api.get(url)).json() == result
    # The persisted association is revalidated on generation, not just retrieval.
    generated = await api.post(url + "/finalize", json={"version": result["version"]})
    assert generated.status_code == 200, generated.text


@pytest.mark.anyio
async def test_retrieved_value_of_another_property_cannot_resolve(api, monkeypatch):
    state = await create(api, docx(LABELS))
    await source(api, PROFILE)
    simulate(monkeypatch, {"t0.r0.c1": ["Societa a responsabilita limitata"],
                           "t0.r1.c1": ["05599999"]})
    semantic_planner(monkeypatch)
    result = await resolve(api, state)
    assert result["summary"]["resolved"] == 0
    for field in result["fields"]:
        assert field["status"] == "MISSING" and field["value"] is None
        assert field["provenance"] is None
        assert any("altra proprietà" in error for error in field["validation_errors"])


@pytest.mark.anyio
async def test_reassociate_only_pertinent_properties_from_other_search_bucket(api, monkeypatch):
    state = await create(api, docx(LABELS))
    await source(api, PROFILE)
    await source(api, "Oggetto procedura: Servizi.", project="alpha", name="avviso.txt")
    # Actual indexed evidence and SQL provenance; force disjoint search cohorts
    # to exercise the admission rule independently of ranking/provider quality.
    original_search = resolution.search_project_evidence
    profile = original_search("alpha", "Organizzazione giuridica", 4, target="source")
    notice = original_search("alpha", "Oggetto procedura", 4, target="source")
    profile = [s for s in profile if s["scope"] == "global"]
    notice = [s for s in notice if s["scope"] == "project:alpha"]
    assert profile and notice

    def search(project_id, query, limit, **kwargs):
        assert project_id == "alpha" and kwargs["target"] == "source"
        return profile if ("Organizzazione giuridica" in query or LABELS[1] in query) else notice

    simulate(monkeypatch, VALUES)
    semantic_planner(monkeypatch, split=True)
    monkeypatch.setattr(resolution, "search_project_evidence", search)
    result = await resolve(api, state)
    first, second = result["fields"]
    assert first["status"] == second["status"] == "RESOLVED"
    assert all(chunk_id > 0 for chunk_id in first["search"]["source_chunk_ids"])
    assert first["source_evidence"][0]["chunk_id"] < 0
    assert first["source_evidence"][0]["chunk_id"] in first["search"]["allowed_source_chunk_ids"]
    # Unrelated pooled evidence is NOT admitted to the other candidate.
    assert all(chunk_id < 0 for chunk_id in second["search"]["allowed_source_chunk_ids"])


@pytest.mark.anyio
async def test_irrelevant_source_cannot_resolve_equivalent_company_requirement(api, monkeypatch):
    state = await create(api, docx(LABELS))
    await source(api, "Telefono: 05599999")
    simulate(monkeypatch, {"t0.r0.c1": ["05599999"]})
    semantic_planner(monkeypatch)
    result = await resolve(api, state)
    assert result["summary"]["resolved"] == 0
    assert all(f["value"] is None for f in result["fields"])


@pytest.mark.anyio
async def test_invalid_semantic_plan_preserves_literal_fallback():
    field = {"context": LABELS[0], "requirement": {
        "name": LABELS[0], "form_quote": LABELS[0], "form_citation_id": 1,
    }}
    calls = []

    async def request(*args):
        calls.append(args)
        raise GenerationError("Invalid provider output")

    result = await plan_compilation_search([field], request)
    assert result.names == {1: [LABELS[0]]} and len(calls) == 1


def test_local_property_does_not_borrow_another_values_or_subjects():
    field = {"entity": "company", "requirement": {
        "name": LABELS[0], "form_quote": LABELS[0], "form_citation_id": 1,
    }, "search": {"source_names": ["Denominazione"]}}
    assert company_property(field, PROFILE, "Aurora Progetti S.r.l.") == "Denominazione"
    assert company_property(field, PROFILE, "05599999") is None
    field["requirement"]["person_role"] = "Referente"
    assert company_property(field, PROFILE, "Aurora Progetti S.r.l.") is None


def test_canonical_source_span_is_conservative_and_restores_source_spelling():
    text = "Forma: Societa a responsabilita limitata.\nSede: Via Roma 7."
    assert source_span(text, "società a responsabilità limitata") == (
        "Societa a responsabilita limitata"
    )
    assert source_span(text, "limitata. sede: Via Roma 7") == "limitata.\nSede: Via Roma 7"
    with pytest.raises(ValueError):
        source_span(text, "Societa cooperativa")


def test_source_span_uses_whole_tokens_not_city_prefix_for_province():
    assert source_span("70126 Bari (BA), Italia", "BA") == "BA"
    assert source_span("16100 GENOVA (GE), Italia", "ge") == "GE"
    with pytest.raises(ValueError):
        source_span("Sede: Bari, Italia", "BA")


def test_query_names_are_bounded_without_repeating_long_form_descriptors():
    requirement = Requirement(name="Identità dell'entità che richiede la partecipazione",
                              form_quote="Identità dell'entità che richiede la partecipazione",
                              form_citation_id=1)
    cluster = SourceCluster(requirement_ids=[1])
    queries = compilation_queries(cluster, [requirement], {
        1: [requirement.name, "Denominazione", "Nome dell'ente"],
    })
    assert queries == ["Denominazione", "Nome dell'ente"]
    requirements = [requirement] * 4
    queries = compilation_queries(SourceCluster(requirement_ids=[1, 2, 3, 4]), requirements,
                                  {i: ["Denominazione", "Nome dell'ente"] for i in range(1, 5)})
    assert len(queries) <= 2
