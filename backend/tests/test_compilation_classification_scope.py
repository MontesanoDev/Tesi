"""Interpretation output stays within the selected FORM slots, with bounded retries."""

import json
from copy import deepcopy

import pytest
from test_compilation_controls import current
from test_compilation_conversation import chat as chat
from test_compilation_conversation import start, step
from test_compilation_sessions import docx, simulate, source

from app import compilation_session_resolution as resolution
from app.compilation_session_models import CandidateMeanings
from app.generation import GenerationError


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
@pytest.mark.parametrize("extra", ["unknown", "malformed_unknown", "semantic_unknown", "decided"])
async def test_foreign_interpretation_keeps_valid_sibling_and_previous_source(
    chat, monkeypatch, extra,
):
    state, _ = await start(chat, content=docx(("Denominazione sociale", "Sede legale")))
    await source(chat[0], "Denominazione sociale: Aurora Progetti S.r.l.\n"
                 "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch, {"t0.r0.c1": ["Aurora Progetti S.r.l."],
                                  "t0.r1.c1": ["Via Roma 12, Bari"]})
    classifier = resolution.classify_candidates

    async def first_only(fields):
        meanings = await classifier(fields)
        meanings.fields = meanings.fields[:1]
        return meanings

    monkeypatch.setattr(resolution, "classify_candidates", first_only)
    state = await step(chat[0], state)
    previous = deepcopy(state["fields"][0])
    assert previous["status"] == "RESOLVED"
    assert state["fields"][1]["status"] == "PENDING"
    review = resolution.review_meanings
    unexpected_id = previous["id"] if extra == "decided" else "outside-current-batch"

    async def contaminated(fields):
        payload = (await classifier(fields)).model_dump()
        foreign = deepcopy(payload["fields"][0])
        foreign["candidate_id"] = unexpected_id
        if extra == "malformed_unknown":
            foreign["classification"] = "invalid"
        elif extra == "semantic_unknown":
            foreign["semantic"] = {"subject_anchor": "Dati aziendali",
                                   "subject_relation": "organization",
                                   "context_role": "ORGANIZATION_PROFILE"}
        payload["fields"].append(foreign)
        return resolution.parse_structured(json.dumps(payload), CandidateMeanings)

    async def scoped_review(fields, meanings, request):
        assert [m.candidate_id for m in meanings.fields] == [fields[0]["id"]]
        return await review(fields, meanings, request)

    monkeypatch.setattr(resolution, "classify_candidates", contaminated)
    monkeypatch.setattr(resolution, "review_meanings", scoped_review)
    state = await step(chat[0], state)
    assert state["last_error"] is None and state["status"] != "FAILED"
    assert state["fields"][0] == previous
    assert state["fields"][1]["status"] == "RESOLVED"
    assert state["fields"][1]["value"] == "Via Roma 12, Bari"
    assert state["fields"][1]["provenance"] == "SOURCE"
    assert calls["classify"] == 2
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1, "t0.r1.c1": 2}
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 1, "t0.r1.c1": 1}
    assert state["last_resolution"]["interpretation_rejections"][unexpected_id]
    assert not state["chat"]["auto_continue"]
    assert await current(chat[0], state) == state


@pytest.mark.anyio
@pytest.mark.parametrize("parse", [True, False])
async def test_duplicate_interpretation_rejects_all_versions_without_blocking_sibling(
    chat, monkeypatch, parse,
):
    state, _ = await start(chat, content=docx(("Forma giuridica", "Sede legale")))
    await source(chat[0], "Forma giuridica: Societa limitata.\nSede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch, {"t0.r0.c1": ["Societa limitata"],
                                  "t0.r1.c1": ["Via Roma 12, Bari"]})
    classifier = resolution.classify_candidates

    async def duplicate(fields):
        payload = (await classifier(fields)).model_dump()
        payload["fields"].append(deepcopy(payload["fields"][0]))
        return (resolution.parse_structured(json.dumps(payload), CandidateMeanings) if parse
                else CandidateMeanings.model_validate(payload))

    monkeypatch.setattr(resolution, "classify_candidates", duplicate)
    state = await step(chat[0], state)
    assert [f["status"] for f in state["fields"]] == ["PENDING", "RESOLVED"]
    assert state["fields"][0]["requirement"] is None
    assert "duplicato" in state["fields"][0]["validation_errors"][0]
    sibling = deepcopy(state["fields"][1])
    state = await step(chat[0], state)
    assert state["fields"][1] == sibling
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 2, "t0.r1.c1": 1}
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 1}
    assert calls["classify"] == 2
    assert not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_only_foreign_interpretations_exhaust_without_source_attempts_or_loop(
    chat, monkeypatch,
):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    calls = simulate(monkeypatch)
    classifier = resolution.classify_candidates

    async def foreign(fields):
        meanings = await classifier(fields)
        meanings.fields[0].candidate_id = "outside-current-batch"
        return meanings

    monkeypatch.setattr(resolution, "classify_candidates", foreign)
    state = await step(chat[0], state)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "PENDING"
    assert state["fields"][0]["requirement"] is None
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 2}
    assert state["chat_workflow"]["source_attempts"] == {}
    assert calls["planner"] == calls["match"] == 0
    assert not state["chat"]["auto_continue"]
    response = await chat[0].post(f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
                                json={"version": state["version"], "automatic": True})
    assert response.status_code == 409


@pytest.mark.anyio
async def test_foreign_item_does_not_bypass_form_grounding(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Forma giuridica", "Sede legale")))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    simulate(monkeypatch, {"t0.r1.c1": ["Via Roma 12, Bari"]})
    classifier = resolution.classify_candidates

    async def unsupported(fields):
        payload = (await classifier(fields)).model_dump()
        payload["fields"][0]["form_quote"] = "Richiesta assente nel modulo"
        foreign = deepcopy(payload["fields"][1])
        foreign["candidate_id"] = "outside-current-batch"
        payload["fields"].append(foreign)
        return resolution.parse_structured(json.dumps(payload), CandidateMeanings)

    monkeypatch.setattr(resolution, "classify_candidates", unsupported)
    state = await step(chat[0], state)
    assert [f["status"] for f in state["fields"]] == ["PENDING", "RESOLVED"]
    assert state["fields"][0]["validation_errors"] == ["Estratto strutturale non presente nel FORM"]
    assert state["fields"][0]["search"]["status"] == "not_searched"
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 1}


@pytest.mark.anyio
async def test_classification_provider_failure_remains_explicit(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    simulate(monkeypatch)

    async def unavailable(*args):
        raise GenerationError("Provider non disponibile")

    monkeypatch.setattr(resolution, "classify_candidates", unavailable)
    response = await chat[0].post(f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
                                json={"version": state["version"], "automatic": True})
    assert response.status_code == 502
    state = await current(chat[0], state)
    assert state["status"] == "FAILED"
    assert state["chat_workflow"]["source_attempts"] == {}
