"""Matcher output is scoped to searched fields without discarding valid siblings."""

import json
from copy import deepcopy

import pytest
from test_compilation_controls import current
from test_compilation_conversation import chat as chat
from test_compilation_conversation import start, step
from test_compilation_sessions import docx, simulate, source

from app import compilation_session_resolution as resolution
from app.compilation_session_models import CandidateMatches
from app.compilation_sessions import candidate_snapshots
from app.docx_templates import inspect_docx
from app.generation import GenerationError


@pytest.fixture
def anyio_backend():
    return "asyncio"


def match(ident, value="Via Roma 12, Bari"):
    return {"candidate_id": ident, "reason": "Riscontro da verificare", "supports": [
        {"source_id": 1, "quote": f"Sede legale: {value}.", "value": value},
    ]}


@pytest.mark.anyio
@pytest.mark.parametrize("extra", ["unknown", "decided", "malformed_unknown"])
async def test_out_of_batch_item_keeps_valid_source_result_and_prior_decisions(
    chat, monkeypatch, extra,
):
    state, _ = await start(chat, content=docx(("Denominazione sociale", "Sede legale")))
    await source(chat[0], "Denominazione sociale: Aurora Progetti S.r.l.\n"
                 "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch, {"t0.r0.c1": ["Aurora Progetti S.r.l."],
                                  "t0.r1.c1": ["Via Roma 12, Bari"]})
    matcher = resolution.match_candidates

    async def first_invalid(*args):
        result = await matcher(*args)
        result.fields[1].supports[0].quote = "Estratto non presente nella SOURCE"
        return result

    monkeypatch.setattr(resolution, "match_candidates", first_invalid)
    state = await step(chat[0], state)
    first = deepcopy(state["fields"][0])
    assert first["status"] == "RESOLVED"
    assert state["fields"][1]["status"] == "MISSING"

    async def contaminated(fields, sources, coverage):
        valid = (await matcher(fields, sources, coverage)).model_dump()["fields"][0]
        ident = first["id"] if extra == "decided" else "outside-current-batch"
        unexpected = {"candidate_id": ident, "reason": "Fuori ambito", "supports": []}
        if extra == "malformed_unknown":
            unexpected["supports"] = "invalid"
        return resolution.parse_structured(json.dumps({"fields": [valid, unexpected]}),
                                           CandidateMatches)

    monkeypatch.setattr(resolution, "match_candidates", contaminated)
    state = await step(chat[0], state)
    assert state["status"] != "FAILED" and state["last_error"] is None
    assert state["fields"][0] == first
    assert calls["classify"] == 1
    assert state["fields"][1]["status"] == "RESOLVED"
    assert state["fields"][1]["provenance"] == "SOURCE"
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1, "t0.r1.c1": 1}
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 1, "t0.r1.c1": 2}
    assert state["last_resolution"]["matcher_rejections"]
    assert not state["chat"]["auto_continue"]
    assert await current(chat[0], state) == state


@pytest.mark.anyio
async def test_valid_sibling_resolves_despite_unknown_match(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    simulate(monkeypatch, {"t0.r0.c1": ["Via Roma 12, Bari"]})
    matcher = resolution.match_candidates
    review = resolution.review_sources
    reviewed = []

    async def contaminated(*args):
        payload = (await matcher(*args)).model_dump()
        payload["fields"].append(match("outside-current-batch", "Valore inventato"))
        return resolution.parse_structured(json.dumps(payload), CandidateMatches)

    async def scoped_review(fields, matches, sources, coverage, request):
        assert [m.candidate_id for m in matches.fields] == [fields[0]["id"]]
        reviewed.append(fields[0]["id"])
        return await review(fields, matches, sources, coverage, request)

    monkeypatch.setattr(resolution, "match_candidates", contaminated)
    monkeypatch.setattr(resolution, "review_sources", scoped_review)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "RESOLVED"
    assert state["fields"][0]["value"] == "Via Roma 12, Bari"
    assert state["fields"][0]["provenance"] == "SOURCE"
    assert reviewed == [state["fields"][0]["id"]]
    assert state["last_resolution"]["matcher_rejections"]["outside-current-batch"]


@pytest.mark.parametrize("duplicates", [2, 3])
def test_duplicate_match_ids_reject_all_versions_and_keep_valid_sibling(duplicates):
    payload = {"fields": [match("duplicated", "Prima sede"), match("valid")]
               + [match("duplicated", f"Altra sede {n}") for n in range(duplicates - 1)]}
    result = resolution.parse_structured(json.dumps(payload), CandidateMatches)
    assert [m.candidate_id for m in result.fields] == ["valid"]
    assert "duplicated" in result._item_errors


def test_match_without_coverage_never_changes_unsearched_field():
    layout = inspect_docx(docx(("Sede legale", "Forma giuridica")))
    fields = candidate_snapshots(layout, "alpha", 1, "modulo.docx")
    untouched = deepcopy(fields[1])
    result = CandidateMatches(fields=[{"candidate_id": f["id"], "supports": [],
                                      "reason": "Nessun riscontro"} for f in fields])
    result._item_errors[fields[1]["id"]] = "Schema invalido su campo non ricercato"
    resolution.apply_matches(layout, fields, result, [], {fields[0]["id"]: []})
    assert fields[0]["status"] == "MISSING"
    assert fields[1] == untouched
    assert fields[1]["id"] in result._item_errors


@pytest.mark.anyio
async def test_only_out_of_batch_matches_exhaust_retry_without_loop(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch)

    async def outside(*args):
        return CandidateMatches(fields=[match("outside-current-batch")])

    monkeypatch.setattr(resolution, "match_candidates", outside)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "MISSING"
    state = await step(chat[0], state)
    assert not state["chat"]["auto_continue"]
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 2}
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1}
    assert calls["classify"] == 1


@pytest.mark.parametrize("payload", ["{", '{"fields":[{}]}', '{"fields":null}',
                                     '{"fields":[],"unexpected":true}'])
def test_global_matcher_schema_failures_remain_explicit(payload):
    with pytest.raises(GenerationError, match="Output strutturato"):
        resolution.parse_structured(payload, CandidateMatches)


@pytest.mark.anyio
async def test_provider_failure_remains_explicit(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    simulate(monkeypatch)

    async def unavailable(*args):
        raise GenerationError("Provider non disponibile")

    monkeypatch.setattr(resolution, "match_candidates", unavailable)
    response = await chat[0].post(f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
                                json={"version": state["version"], "automatic": True})
    assert response.status_code == 502
    assert (await current(chat[0], state))["status"] == "FAILED"
