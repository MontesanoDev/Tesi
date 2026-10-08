"""Independent bounded retry budgets, real persistence and provenance gates."""
import json

import pytest
from test_compilation_controls import current
from test_compilation_conversation import chat as chat
from test_compilation_conversation import mutate_state, start, step
from test_compilation_sessions import docx, simulate, source

from app import compilation_session_resolution as resolution
from app.compilation_clarifications import automatic_fields, phase_attempts
from app.compilation_session_models import CandidateMatches, CandidateMeanings
from app.generation import GenerationError


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def mixed(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Dato sconosciuto", "Sede legale")))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch, {"t0.r1.c1": ["Via Roma 12, Bari"]})
    original = resolution.classify_candidates

    async def classify(fields):
        batch = (await original(fields)).model_dump()
        for item in batch["fields"]:
            if item["candidate_id"] == "t0.r0.c1":
                item["classification"] = "invalid"
        return resolution.parse_structured(json.dumps(batch), CandidateMeanings)

    monkeypatch.setattr(resolution, "classify_candidates", classify)
    matcher = resolution.match_candidates

    async def invalid_support(*args):
        batch = (await matcher(*args)).model_dump()
        for item in batch["fields"]:
            for support in item["supports"]:
                support["quote"] = "Estratto inventato"
        return CandidateMatches.model_validate(batch)

    monkeypatch.setattr(resolution, "match_candidates", invalid_support)
    state = await step(chat[0], state)
    assert [f["status"] for f in state["fields"]] == ["PENDING", "MISSING"]
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1, "t0.r1.c1": 1}
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 1}
    monkeypatch.setattr(resolution, "match_candidates", matcher)
    return state, calls


@pytest.mark.anyio
async def test_bad_pending_does_not_consume_valid_missing_source_retry(chat, monkeypatch):
    state, calls = await mixed(chat, monkeypatch)
    state = await step(chat[0], state)
    assert state["fields"][1]["status"] == "RESOLVED"
    assert state["fields"][1]["provenance"] == "SOURCE"
    assert state["fields"][1]["value"] == "Via Roma 12, Bari"
    assert calls["classify"] == 1
    assert state["chat_workflow"]["analysis_attempts"]["t0.r0.c1"] == 1
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 2}
    state = await step(chat[0], state)
    assert state["chat_workflow"]["analysis_attempts"]["t0.r0.c1"] == 2
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 2}
    assert not state["chat"]["auto_continue"] and not automatic_fields(state)
    response = await chat[0].post(
        f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
        json={"version": state["version"], "automatic": True},
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_global_source_failure_does_not_spend_other_interpretation_retry(chat, monkeypatch):
    state, _ = await mixed(chat, monkeypatch)

    async def failed(*args):
        raise GenerationError("Output strutturato della risoluzione non valido")

    monkeypatch.setattr(resolution, "match_candidates", failed)
    state = await step(chat[0], state)
    assert state["chat_workflow"]["analysis_attempts"]["t0.r0.c1"] == 1
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 2}
    assert state["chat_workflow"]["last_output_rejection"]["field_ids"] == ["t0.r1.c1"]
    state = await step(chat[0], state)
    assert state["chat_workflow"]["analysis_attempts"]["t0.r0.c1"] == 2
    assert not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_exhausted_interpretation_does_not_block_other_source_retry(chat, monkeypatch):
    state, _ = await mixed(chat, monkeypatch)
    mutate_state(state, lambda s: s["chat_workflow"]["analysis_attempts"].update({"t0.r0.c1": 2}))
    state = await step(chat[0], await current(chat[0], state))
    assert state["fields"][1]["status"] == "RESOLVED"
    assert state["chat_workflow"]["analysis_attempts"]["t0.r0.c1"] == 2
    assert not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_partial_match_schema_preserves_valid_source_item(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale", "Forma giuridica")))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.\nForma giuridica: Societa limitata.")
    simulate(monkeypatch, {"t0.r0.c1": ["Via Roma 12, Bari"],
                           "t0.r1.c1": ["Societa limitata"]})
    original = resolution.match_candidates

    async def partial(*args):
        batch = (await original(*args)).model_dump()
        batch["fields"][1]["supports"] = "not a list"
        return resolution.parse_structured(json.dumps(batch), CandidateMatches)

    monkeypatch.setattr(resolution, "match_candidates", partial)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "RESOLVED"
    assert state["fields"][1]["status"] == "MISSING"
    assert state["fields"][1]["validation_errors"]


@pytest.mark.anyio
async def test_first_source_failure_keeps_form_and_source_retry(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch, {"t0.r0.c1": ["Via Roma 12, Bari"]})
    original = resolution.match_candidates

    async def failed(*args):
        raise GenerationError("Output strutturato della risoluzione non valido")

    monkeypatch.setattr(resolution, "match_candidates", failed)
    state = await step(chat[0], state)
    assert state["fields"][0]["requirement"]
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 1}
    monkeypatch.setattr(resolution, "match_candidates", original)
    state = await step(chat[0], state)
    assert state["fields"][0]["status"] == "RESOLVED"
    assert calls["classify"] == 1
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1}
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 2}


@pytest.mark.parametrize("payload", ["{", '{"fields":null}', '{"fields":[{}]}',
                                     '{"fields":[],"extra":true}',
                                     '{"fields":[{"candidate_id":"x"},{"candidate_id":"x"}]}'])
def test_global_schema_errors_remain_explicit(payload):
    with pytest.raises(GenerationError, match="Output strutturato"):
        resolution.parse_structured(payload, CandidateMeanings)


def test_legacy_spent_budget_is_preserved_without_mutating_state():
    state = {"fields": [{"id": "old", "requirement": {"name": "Sede"}}],
             "chat_workflow": {"analysis_attempts": {"old": 2}}}
    assert phase_attempts(state, "source") == {"old": 2}
    assert "source_attempts" not in state["chat_workflow"]


@pytest.mark.anyio
async def test_partial_interpretation_resolves_valid_item_in_same_step(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Dato sconosciuto", "Sede legale")))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    simulate(monkeypatch, {"t0.r1.c1": ["Via Roma 12, Bari"]})
    original = resolution.classify_candidates

    async def partial(fields):
        batch = (await original(fields)).model_dump()
        batch["fields"][0]["form_quote"] = ""
        return resolution.parse_structured(json.dumps(batch), CandidateMeanings)

    monkeypatch.setattr(resolution, "classify_candidates", partial)
    state = await step(chat[0], state)
    assert [f["status"] for f in state["fields"]] == ["PENDING", "RESOLVED"]
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 1}
    state = await step(chat[0], state)
    assert state["chat_workflow"]["source_attempts"] == {"t0.r1.c1": 1}
    assert not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_source_schema_retries_exhaust_without_reinterpretation(chat, monkeypatch):
    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    calls = simulate(monkeypatch)

    async def failed(*args):
        raise GenerationError("Output strutturato della risoluzione non valido")

    monkeypatch.setattr(resolution, "match_candidates", failed)
    state = await step(chat[0], state)
    state = await step(chat[0], state)
    assert state["chat_workflow"]["source_attempts"] == {"t0.r0.c1": 2}
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 1}
    assert calls["classify"] == 1 and not state["chat"]["auto_continue"]


@pytest.mark.anyio
async def test_pause_during_source_phase_wins_over_recovery(chat, monkeypatch):
    from app.compilation_chat import ChatControl
    from app.compilation_sessions import chat_control

    state, _ = await start(chat, content=docx(("Sede legale",)))
    await source(chat[0], "Sede legale: Via Roma 12, Bari.")
    simulate(monkeypatch)

    async def failed(*args):
        chat_control("alpha", state["id"], state["version"],
                     ChatControl(kind="pause", user_quote="basta"))
        raise GenerationError("Output strutturato della risoluzione non valido")

    monkeypatch.setattr(resolution, "match_candidates", failed)
    response = await chat[0].post(
        f"/api/projects/alpha/compilation-sessions/{state['id']}/resolve",
        json={"version": state["version"], "automatic": True},
    )
    assert response.status_code == 502
    state = await current(chat[0], state)
    assert state["chat"]["paused_by_user"] and not state["chat"]["auto_continue"]
    assert not state["chat_workflow"].get("output_rejections")


@pytest.mark.anyio
async def test_matcher_uses_strict_candidate_schema_and_allowed_ids(monkeypatch):
    calls = []

    async def request(task, data, schema):
        calls.append((data, schema))
        return schema(fields=[])

    monkeypatch.setattr(resolution, "request_structured", request)
    result = await resolution.match_candidates(
        [{"id": "candidate", "requirement": {"name": "Sede"}}],
        [{"content": "Sede: Bari"}], {"candidate": [1]},
    )
    assert isinstance(result, CandidateMatches)
    assert calls[0][1] is CandidateMatches
    assert calls[0][0]["requirements"][0]["allowed_source_ids"] == [1]


@pytest.mark.anyio
async def test_five_verified_company_properties_keep_source_provenance(chat, monkeypatch):
    labels = ("Operatore economico", "Forma giuridica", "Sede legale",
              "Codice fiscale operatore", "Partita IVA operatore")
    values = ("Mapi Ingegneria S.r.l.", "Societa a responsabilita limitata",
              "Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia",
              "IT01234567890", "IT01234567890")
    state, _ = await start(chat, content=docx(labels))
    await source(chat[0],
        "Ragione sociale: Mapi Ingegneria S.r.l.\n"
        "Forma giuridica: Societa a responsabilita limitata.\n"
        "Sede legale di Mapi Ingegneria S.r.l.: "
        "Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia.\n"
        "Codice fiscale e Partita IVA riportati nella visura demo: IT01234567890.")
    simulate(monkeypatch,
             {f['id']: [value] for f, value in zip(state['fields'], values, strict=True)})
    planner = resolution.plan_compilation_search

    async def aliases(fields, request):
        search = await planner(fields, request)
        # Simulate the semantic planner's property alias, preserving SOURCE gates.
        search.names[1].append("Ragione sociale")
        return search

    monkeypatch.setattr(resolution, "plan_compilation_search", aliases)
    state = await step(chat[0], state)
    assert all(f['status'] == 'RESOLVED' and f['provenance'] == 'SOURCE'
               for f in state['fields']), [(f['label'], f['status'], f['validation_errors'])
                                         for f in state['fields']]
    assert all(e['role'] == 'source' and e['scope'] == 'global' and e['category'] == 'company'
               for f in state['fields'] for e in f['source_evidence'])
    assert state['chat']['metrics']['user_turns'] == 0


@pytest.mark.anyio
async def test_applicability_confirmation_reopens_interpretation_for_review_candidate(
    chat, monkeypatch,
):
    from test_compilation_conversation import say

    state, _ = await start(chat, content=docx(("Estremi procura",), context="Se procuratore"))
    calls = 0

    def classify(fields):
        nonlocal calls
        calls += 1
        if calls == 1:
            return CandidateMeanings(fields=[])
        return CandidateMeanings(fields=[{
            "candidate_id": fields[0]["id"], "classification": "review", "requirement": None,
            "form_quote": fields[0]["context"], "condition": "Se procuratore",
            "entity": "person", "kind": "choice", "reason": "Confermare l'applicabilità",
        }])

    simulate(monkeypatch, classify_hook=classify)
    state = await step(chat[0], state)
    state = await step(chat[0], state)
    assert state["chat_workflow"]["analysis_attempts"] == {"t0.r0.c1": 2}
    assert state["chat"]["question"]["kind"] == "applicability"
    response = await say(chat, state, "sì", {"action": "CONDITION_TRUE"})
    assert response.status_code == 200
    state = await current(chat[0], state)
    assert state["chat"]["auto_continue"]
    assert state["chat_workflow"]["analysis_attempts"] == {}
    assert state["chat_workflow"]["source_attempts"] == {}
