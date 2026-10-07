"""Control turns and dependencies: isolated persistence, simulated semantic providers."""

import copy

import pytest
from fastapi import HTTPException
from test_compilation_conversation import (
    BASE,
    command,
    mutate_state,
    say,
    start,
    step,
)
from test_compilation_conversation import (
    anyio_backend as anyio_backend,
)
from test_compilation_conversation import (
    chat as retrieval_chat,
)
from test_compilation_sessions import docx, simulate, source

from app import compilation_session_resolution as resolution
from app import compilation_sessions as sessions
from app.compilation_session_models import CandidateMatches, CandidateMeanings

chat = retrieval_chat


async def current(client, state):
    return (await client.get(f"{BASE}/{state['id']}")).json()


def control(kind, message, field_id=None):
    return command("compilation_control", control={
        "kind": kind, "user_quote": message, "field_id": field_id,
    })


@pytest.mark.anyio
@pytest.mark.parametrize("kind,message", [
    ("skip", "salta"), ("skip", "vediamolo dopo"),
    ("unknown", "non lo so"), ("unknown", "non ne sono sicuro"),
    ("refuse", "preferisco non fornire questo dato"),
])
async def test_defer_preserves_facts_moves_question_and_survives_reload(
    chat, monkeypatch, kind, message,
):
    client, _, requests, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    asked = state["chat"]["question"]["field_ids"][0]
    before = copy.deepcopy(state["fields"][0])
    answer = await say(chat, state, message, control(kind, message, asked))
    assert answer.status_code == 200, answer.text
    assert answer.json()["compilation"]["action"] == "deferred"
    assert "UNKNOWN" in requests[-1]["messages"][0]["content"]
    state = await current(client, state)
    after = dict(state["fields"][0])
    note = after.pop("conversation_disposition")
    assert after == before  # No factual status/value/provenance mutation.
    assert note["kind"] == kind and note["user_quote"] == message
    assert state["chat"]["question"]["field_ids"] != [asked]
    assert (await current(client, state))["chat"] == state["chat"]
    other = state["chat"]["question"]["field_ids"][0]
    await say(chat, state, "passa oltre", control("skip", "passa oltre", other))
    state = await current(client, state)
    assert state["chat"]["question"]["kind"] == "deferred_summary"
    assert state["chat"]["question"]["field_ids"] == []
    assert not state["chat"]["auto_continue"] and state["last_generation"] is None
    assert state["status"] == "WAITING_FOR_USER" and state["summary"]["missing"] == 2


@pytest.mark.anyio
async def test_skipping_all_current_issues_allows_next_pending_batch(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(tuple(f"Dato {i}" for i in range(13))))
    simulate(monkeypatch)
    state = await step(client, state)
    assert state["chat"]["auto_continue"] and state["chat"]["question"] is None
    state = await step(client, state)
    for _ in range(12):
        field_id = state["chat"]["question"]["field_ids"][0]
        answer = await say(chat, state, "salta", control("skip", "salta", field_id))
        assert answer.status_code == 200
        state = await current(client, state)
    assert not state["chat"]["auto_continue"] and state["status"] == "WAITING_FOR_USER"
    assert state["chat"]["question"]["field_ids"] == [state["fields"][-1]["id"]]
    assert state["chat"]["deferred"] == 12


@pytest.mark.anyio
@pytest.mark.parametrize("message", ["basta", "fermati", "metti in pausa", "riprendiamo dopo"])
async def test_pause_hides_question_resume_reuses_session(chat, monkeypatch, message):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    original_fields, question = state["fields"], state["chat"]["question"]
    answer = await say(chat, state, message, control("pause", message))
    assert answer.status_code == 200, answer.text
    assert answer.json()["compilation"] == {"session_id": state["id"], "action": "paused"}
    assert "metto in pausa" in answer.json()["answer"]
    state = await current(client, state)
    assert state["chat"]["paused_by_user"] and state["chat"]["question"] is None
    assert not state["chat"]["auto_continue"] and state["fields"] == original_fields
    assert (await current(client, state))["chat"]["question"] is None
    answer = await say(chat, state, "riprendi", control("resume", "riprendi"))
    assert answer.json()["compilation"]["session_id"] == state["id"]
    state = await current(client, state)
    assert not state["chat"]["paused_by_user"]
    assert state["chat"]["question"] == question and state["fields"] == original_fields
    assert len((await client.get(BASE)).json()) == 1


@pytest.mark.anyio
async def test_pause_during_analysis_invalidates_late_results(chat):
    client, _, _, _ = chat
    state, _ = await start(chat)
    claimed, _, fields = sessions.claim_resolution(
        "alpha", state["id"], state["version"], None, automatic=True,
    )
    # Composer still has the pre-claim snapshot; stopping may safely accept it.
    answer = await say(chat, state, "basta", control("pause", "basta"))
    assert answer.status_code == 200, answer.text
    paused = await current(client, state)
    with pytest.raises(HTTPException, match="409"):
        sessions.complete_resolution("alpha", state["id"], claimed["version"], fields, {})
    sessions.mark_failed("alpha", state["id"], claimed["version"], "late provider error")
    assert (await current(client, state)) == paused
    assert paused["lease_until"] is None and paused["chat"]["paused_by_user"]


@pytest.mark.anyio
async def test_second_uninterpretable_reply_is_deferred_without_loop(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat)
    simulate(monkeypatch)
    state = await step(client, state)
    asked = state["chat"]["question"]["field_ids"]
    decision = command("compilation_clarify", answer="Serve un'indicazione univoca")
    first = await say(chat, state, "boh, uno dei due", decision)
    assert first.json()["compilation"]["action"] == "clarify"
    state = await current(client, state)
    second = await say(chat, state, "non capisco la domanda", decision)
    assert second.json()["compilation"]["action"] == "deferred"
    state = await current(client, state)
    assert state["chat"]["question"]["field_ids"] != asked
    assert state["fields"][0]["conversation_disposition"]["kind"] == "uninterpretable"


def conditional_meanings(fields):
    return CandidateMeanings(fields=[{
        "candidate_id": f["id"], "classification": "data", "kind": "data",
        "requirement": {"name": "Estremi procura", "form_quote": f["context"],
                        "form_citation_id": 1, "person_role": "procuratore"},
        "condition": "se procuratore", "form_quote": f["context"],
        "reason": "Il campo dipende dalla condizione indicata nel modulo",
    } for f in fields])


@pytest.mark.anyio
@pytest.mark.parametrize("reply", ["No", "non sono procuratore", "non siamo procuratori"])
async def test_unknown_condition_is_asked_before_value_and_user_false_excludes(
    chat, monkeypatch, reply,
):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    simulate(monkeypatch, classify_hook=conditional_meanings)
    state = await step(client, state)
    assert state["chat"]["question"]["kind"] == "applicability"
    assert state["fields"][0]["value"] is None
    response = await say(chat, state, reply, command("compilation_input", field_replies=[{
        "field_id": state["fields"][0]["id"], "action": "not_applicable", "user_quote": reply,
    }]))
    assert response.status_code == 200, response.text
    state = await current(client, state)
    field = state["fields"][0]
    assert field["status"] == "NOT_APPLICABLE" and field["provenance"] == "USER"
    assert field["applicability"]["applies"] is False and field["value"] is None
    assert state["summary"]["missing"] == 0 and state["status"] == "READY"


@pytest.mark.anyio
@pytest.mark.parametrize("has_source", [False, True])
async def test_true_user_condition_triggers_factual_resolution_then_value_if_missing(
    chat, monkeypatch, has_source,
):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    values = {state["fields"][0]["id"]: ["REP-2040"]} if has_source else {}
    if has_source:
        await source(client, "Procuratore: Estremi procura: REP-2040")
    simulate(monkeypatch, values, classify_hook=conditional_meanings)
    state = await step(client, state)
    # Even a valid factual value cannot establish an unknown dependency.
    assert state["chat"]["question"]["kind"] == "applicability"
    assert state["fields"][0]["status"] != "RESOLVED"
    response = await say(chat, state, "Sì", command("compilation_input", field_replies=[{
        "field_id": state["fields"][0]["id"], "action": "applicable", "user_quote": "Sì",
    }]))
    assert response.status_code == 200, response.text
    state = await current(client, state)
    assert state["chat"]["auto_continue"]
    state = await step(client, state)
    field = state["fields"][0]
    assert field["applicability"]["provenance"] == "USER"
    if has_source:
        assert field["status"] == "RESOLVED" and field["value"] == "REP-2040"
        assert field["provenance"] == "SOURCE" and field["source_evidence"]
    else:
        assert field["status"] == "MISSING"
        assert state["chat"]["question"]["kind"] == "value"
        response = await say(chat, state, "REP-USER", command("compilation_input", field_replies=[{
            "field_id": field["id"], "action": "set", "value": "REP-USER", "user_quote": "REP-USER",
        }]))
        assert response.status_code == 200, response.text
        state = await current(client, state)
        assert state["fields"][0]["status"] == "USER_PROVIDED"
        assert state["fields"][0]["provenance"] == "USER"


@pytest.mark.anyio
@pytest.mark.parametrize("applies", [True, False])
async def test_source_can_explicitly_establish_condition(chat, monkeypatch, applies):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    assertion = "Il sottoscrittore " + ("agisce" if applies else "non agisce") + " come procuratore"
    await source(client, assertion + ". Procuratore: Estremi procura: REP-2040")
    simulate(monkeypatch, {state["fields"][0]["id"]: ["REP-2040"]},
             classify_hook=conditional_meanings)
    old_match = resolution.match_candidates
    async def match(fields, sources, coverage):
        result = await old_match(fields, sources, coverage)
        for item in result.fields:
            sid = next(i for i in coverage[item.candidate_id]
                       if assertion in sources[i - 1]["content"])
            data = item.model_dump()
            data["applicability"] = [{"applies": applies, "source_id": sid,
                                      "quote": assertion, "value": assertion}]
            item_index = result.fields.index(item)
            result.fields[item_index] = CandidateMatches(fields=[data]).fields[0]
        return result
    monkeypatch.setattr(resolution, "match_candidates", match)
    state = await step(client, state)
    assert state["fields"][0]["status"] == ("RESOLVED" if applies else "NOT_APPLICABLE")
    assert state["fields"][0]["provenance"] == "SOURCE"
    assert state["fields"][0]["applicability"]["evidence"][0]["role"] == "source"


@pytest.mark.anyio
async def test_existing_missing_condition_and_legacy_clarification_are_projected_safely(
    chat, monkeypatch,
):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    simulate(monkeypatch, classify_hook=conditional_meanings)
    state = await step(client, state)
    def legacy(s):
        s["fields"][0]["status"] = "MISSING"
        s["chat_workflow"]["clarification"] = "Mi manca Estremi procura. Qual è?"
    mutate_state(state, legacy)
    state = await current(client, state)
    assert state["chat"]["question"]["kind"] == "applicability"
    assert "se procuratore" in state["chat"]["question"]["message"]
    assert "Qual è?" not in state["chat"]["question"]["message"]


@pytest.mark.anyio
@pytest.mark.parametrize("bad_proof", [
    "form", "invented", "hypothetical", "wrong_polarity", "distant_negation",
    "cut_negation", "cut_hypothesis",
])
async def test_invalid_applicability_proof_never_resolves(chat, monkeypatch, bad_proof):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    text = {
        "form": "Il sottoscrittore agisce come procuratore",
        "invented": "Il sottoscrittore agisce come procuratore",
        "hypothetical": "Se il sottoscrittore agisce come procuratore",
        "wrong_polarity": "Il sottoscrittore non agisce come procuratore",
        "distant_negation": ("Il recapito non è disponibile; "
                             "il sottoscrittore agisce come procuratore"),
        "cut_negation": "agisce come procuratore",
        "cut_hypothesis": "Il sottoscrittore agisce come procuratore",
    }[bad_proof]
    source_text = {
        "cut_negation": "Il sottoscrittore non agisce come procuratore",
        "cut_hypothesis": "Se Il sottoscrittore agisce come procuratore",
        "invented": "Altri dati",
    }.get(bad_proof, text)
    await source(client, source_text + ". Procuratore: Estremi procura: REP-2040")
    simulate(monkeypatch, {state["fields"][0]["id"]: ["REP-2040"]},
             classify_hook=conditional_meanings)
    original = resolution.match_candidates
    async def match(fields, sources, coverage):
        result = await original(fields, sources, coverage)
        sid = coverage[fields[0]["id"]][0]
        if bad_proof == "form":
            sources[sid - 1]["role"] = "form"  # Corrupt the provider proposal, not the DB.
        data = result.fields[0].model_dump()
        data["applicability"] = [{"applies": True, "source_id": sid, "quote": text, "value": text}]
        return CandidateMatches(fields=[data])
    monkeypatch.setattr(resolution, "match_candidates", match)
    state = await step(client, state)
    assert state["fields"][0]["status"] == "AMBIGUOUS"
    assert state["fields"][0]["value"] is None
    assert state["chat"]["question"]["kind"] == "applicability"


@pytest.mark.anyio
async def test_deferred_field_reappears_only_after_meaningful_change_or_explicit_review(
    chat, monkeypatch,
):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Sede legale",)))
    simulate(monkeypatch)
    state = await step(client, state)
    fid = state["fields"][0]["id"]
    await say(chat, state, "non lo so", control("unknown", "non lo so", fid))
    state = await current(client, state)
    assert state["chat"]["question"]["kind"] == "deferred_summary"
    await say(chat, state, "riprendi", control("resume", "riprendi"))
    state = await current(client, state)
    assert state["chat"]["question"]["field_ids"] == [fid]
    await say(chat, state, "salta", control("skip", "salta", fid))
    state = await current(client, state)
    mutate_state(state, lambda s: s["fields"][0].update(status="CONFLICTING"))
    state = await current(client, state)
    assert state["chat"]["question"]["field_ids"] == [fid]


@pytest.mark.anyio
async def test_dependency_is_not_erased_when_retry_omits_condition(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    simulate(monkeypatch, classify_hook=conditional_meanings)
    state = await step(client, state)
    await say(chat, state, "Sì", command("compilation_input", field_replies=[{
        "field_id": state["fields"][0]["id"], "action": "applicable", "user_quote": "Sì",
    }]))
    state = await current(client, state)
    def without_condition(fields):
        meanings = conditional_meanings(fields)
        meanings.fields[0].condition = ""
        return meanings
    simulate(monkeypatch, classify_hook=without_condition)
    state = await step(client, state)
    assert state["fields"][0]["condition"] == "se procuratore"
    assert state["fields"][0]["applicability"]["provenance"] == "USER"
    assert state["chat"]["question"]["kind"] == "value"


@pytest.mark.anyio
@pytest.mark.parametrize("message,expected", [
    ("salta", "deferred"), ("non lo so", "deferred"), ("basta", "paused"),
])
@pytest.mark.parametrize("misroute", ["reply", "input"])
async def test_explicit_control_guard_prevents_rag_reply_or_user_value(
    chat, monkeypatch, message, expected, misroute,
):
    client, _, requests, _ = chat
    state, _ = await start(chat, content=docx(("Sede legale",)))
    simulate(monkeypatch)
    state = await step(client, state)
    before = copy.deepcopy(state["fields"])
    if misroute == "reply":
        decision = {"action": "reply", "target": "source", "queries": [],
                    "answer": "Va bene, mi fermo qui"}
    else:
        decision = command("compilation_input", field_replies=[{
            "field_id": state["fields"][0]["id"], "action": "set",
            "value": message, "user_quote": message,
        }])
    calls = len(requests)
    answer = await say(chat, state, message, decision)
    assert answer.status_code == 200, answer.text
    assert answer.json()["compilation"]["action"] == expected
    assert len(requests) == calls + 1  # Existing bounded planner, no second classifier.
    state = await current(client, state)
    assert all(f["value"] == old["value"] and f["provenance"] == old["provenance"]
               for f, old in zip(state["fields"], before, strict=True))
    if expected == "paused":
        assert state["chat"]["paused_by_user"] and state["chat"]["question"] is None
    else:
        assert state["chat"]["question"]["kind"] == "deferred_summary"


def test_condition_reply_is_generic_and_unknown_cannot_be_sliced_into_no():
    from app.compilation_applicability import explicit_condition_reply
    from app.compilation_chat import contains_span

    assert explicit_condition_reply("se consorzio stabile", "non siamo un consorzio stabile",
                                    applies=False)
    assert explicit_condition_reply("in caso di studio associato", "siamo uno studio associato",
                                    applies=True)
    assert not explicit_condition_reply("se consorzio stabile", "non siamo procuratori",
                                        applies=False)
    assert not explicit_condition_reply("se procuratore", "non so se sono procuratore",
                                        applies=False)
    assert not contains_span("Non lo so", "No")


@pytest.mark.anyio
async def test_partial_user_affirmation_cannot_remove_uncertainty_or_negation(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    simulate(monkeypatch, classify_hook=conditional_meanings)
    state = await step(client, state)
    message = "Non so se sono procuratore"
    response = await say(chat, state, message, {"action": "UNKNOWN"})
    assert response.status_code == 200, response.text
    after = await current(client, state)
    after_field = dict(after["fields"][0])
    assert after_field.pop("conversation_disposition")["kind"] == "unknown"
    assert after_field == state["fields"][0] and not after_field.get("applicability")
    assert after["chat"]["question"]["kind"] == "deferred_summary"


@pytest.mark.anyio
async def test_pause_resume_preserves_generated_document_and_domain_status(chat, monkeypatch):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Denominazione sociale",)))
    await source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.")
    simulate(monkeypatch, {state["fields"][0]["id"]: ["Mapi Ingegneria S.r.l."]})
    state = await step(client, state)
    response = await say(chat, state, "Genera il DOCX", command("compilation_generate"))
    assert response.status_code == 200, response.text
    state = await current(client, state)
    assert state["status"] == "GENERATED"
    generation, fields = state["last_generation"], state["fields"]
    await say(chat, state, "basta", control("pause", "basta"))
    state = await current(client, state)
    assert state["status"] == "GENERATED" and state["last_generation"] == generation
    await say(chat, state, "riprendi", control("resume", "riprendi"))
    state = await current(client, state)
    assert state["status"] == "GENERATED" and state["last_generation"] == generation
    assert state["fields"] == fields


@pytest.mark.anyio
@pytest.mark.parametrize("has_value", [False, True])
async def test_legacy_exclusion_cannot_override_a_conflicting_true_source_condition(
    chat, monkeypatch, has_value,
):
    client, _, _, _ = chat
    state, _ = await start(chat, content=docx(("Estremi procura (se procuratore)",)))
    assertion = "Il sottoscrittore agisce come procuratore"
    exclusion = "se procuratore: non applicabile"
    await source(client, assertion + ". Estremi procura: REP-2040", name="condizione.txt")
    await source(client, exclusion + ". Estremi procura", name="esclusione.txt")
    simulate(monkeypatch, classify_hook=conditional_meanings)
    async def match(fields, sources, coverage):
        fid = fields[0]["id"]
        affirmative = next(i for i in coverage[fid] if assertion in sources[i - 1]["content"])
        negative = next(i for i in coverage[fid] if exclusion in sources[i - 1]["content"])
        return CandidateMatches(fields=[{
            "candidate_id": fid, "supports": [{"source_id": affirmative,
                "quote": sources[affirmative - 1]["content"], "value": "REP-2040"}]
                if has_value else [], "reason": "Dichiarazioni incompatibili",
            "applicability": [{"source_id": affirmative, "quote": assertion,
                               "value": assertion, "applies": True}],
            "exclusion": {"source_id": negative, "quote": exclusion, "value": "non applicabile"},
        }])
    monkeypatch.setattr(resolution, "match_candidates", match)
    state = await step(client, state)
    assert state["fields"][0]["status"] == "AMBIGUOUS"
    assert state["fields"][0]["applicability"]["applies"] is None
    assert state["chat"]["question"]["kind"] == "applicability"
