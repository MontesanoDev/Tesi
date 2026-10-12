"""Session command boundaries; providers simulated, semantics evaluated separately."""

import json

import httpx
import pytest
from test_dialogue_benchmark import checkpoint as checkpoint

from app import compilation_chat, compilation_sessions, intents
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


def turn(intent, **extra):
    return intents.TurnPlan(intent=intent, target="form", answer="", queries=[], **extra)


@pytest.mark.parametrize("engine,kind,expected", [
    ("global", "clarifications", "finish"),
    ("global", "value", "finish"),
    ("global", None, "finish"),
    ("global", "generate", "generate"),
    ("legacy", "clarifications", "generate"),
    ("legacy", "value", "generate"),
])
def test_only_validated_global_export_uses_backend_checkpoint(engine, kind, expected):
    plan = turn("generate")
    context = {"engine": engine, "question": {"kind": kind}}
    assert intents.canonical_turn_plan(plan, context).intent == expected
    assert plan.intent == "generate"  # No mutation of the raw validated plan.


@pytest.mark.parametrize("intent", ["pause", "resume", "finish", "answer_fields"])
def test_canonicalization_does_not_invent_an_export_from_other_intents(intent):
    plan = turn(intent)
    assert intents.canonical_turn_plan(plan, {"engine": "global"}) is plan


@pytest.mark.parametrize("context", [None, {"engine": "global", "enabled": False}])
def test_canonical_export_does_not_authorize_a_missing_or_disabled_session(context):
    plan = intents.canonical_turn_plan(turn("generate"), context)
    with pytest.raises(ValueError):
        intents.bind_turn_plan(plan, context, "Genera la bozza")


@pytest.mark.parametrize("intent", ["pause", "resume", "finish", "generate"])
def test_command_with_field_writes_is_invalid_before_normalization(intent):
    with pytest.raises(ValueError):
        turn(intent, replies=[intents.TurnReply(
            slot=1, action="VALUE", value="nuovo valore", user_quote="nuovo valore")])


def fake_router(monkeypatch, plan):
    calls = []
    monkeypatch.setenv("DEEPSEEK_API_KEY", "simulated-key")

    async def request(client, settings, body, timeout, **kwargs):
        calls.append(body)
        return json.dumps(plan), "simulated", {"total_tokens": 10}

    monkeypatch.setattr(intents, "request_model_content", request)
    return calls


async def send(before, message):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test",
    ) as client:
        response = await client.post(f"/api/projects/{before['project_id']}/answer", json={
            "question": message, "conversation_id": before["conversation_id"],
            "compilation_session_id": before["id"], "compilation_version": before["version"],
        })
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.anyio
@pytest.mark.parametrize("kind,message,slot,action", [
    ("condition", "La conferma richiesta la verificheremo più avanti.", 1, "SKIP"),
    ("condition", "Lascia vuota questa voce, senza negare la condizione.", 1, "SKIP"),
    ("group", "Per il recapito rimandiamo, continuiamo con il resto.", 2, "SKIP"),
    ("email", "Non conosco il recapito, ma andiamo avanti.", 1, "UNKNOWN"),
])
async def test_local_control_only_defers_target_not_whole_session(
    checkpoint, monkeypatch, kind, message, slot, action,
):
    project, _, make = checkpoint
    before = make(kind)
    calls = fake_router(monkeypatch, {**turn("answer_fields").model_dump(), "replies": [
        {"slot": slot, "action": action, "user_quote": message}]})
    result = await send(before, message)
    after = compilation_sessions.get_session(project, before["id"])
    assert result["compilation"]["action"] == "updated"
    assert after["global_compilation"]["dialogue"]["phase"] == "PENDING"
    assert not after["chat"]["paused_by_user"]
    answers = after["global_compilation"]["dialogue"]["answers"]
    assert len(answers) == 1 and next(iter(answers.values()))["action"] == action
    assert next(iter(answers.values()))["provenance"] == "USER"
    assert after["global_compilation"]["dialogue"]["user_values"] == {}
    assert len(calls) == 1  # No extra command classifier or relevance check.


@pytest.mark.anyio
async def test_mixed_pause_preserves_values_and_resume_preserves_question(checkpoint, monkeypatch):
    project, _, make = checkpoint
    before = make("group")
    saved = before["global_compilation"]["dialogue"]
    calls = fake_router(monkeypatch, turn("pause").model_dump())
    result = await send(before, "Il recapito è tecnico@studio.example, ma sospendi il lavoro.")
    paused = compilation_sessions.get_session(project, before["id"])
    assert result["compilation"]["action"] == "paused"
    assert paused["chat"]["question"] is None and paused["chat"]["paused_by_user"]
    assert paused["global_compilation"]["dialogue"] == saved
    assert len(calls) == 1
    fake_router(monkeypatch, turn("resume").model_dump())
    result = await send(paused, "Possiamo ripartire da dove ci eravamo fermati.")
    after = compilation_sessions.get_session(project, before["id"])
    assert result["compilation"]["action"] == "resumed"
    assert after["id"] == before["id"] and after["version"] == before["version"] + 2
    assert after["chat"]["question"] == before["chat"]["question"]
    assert after["global_compilation"]["dialogue"] == saved


@pytest.mark.anyio
async def test_export_alias_does_not_acquire_mixed_value_or_force_empty_draft(
    checkpoint, monkeypatch,
):
    project, _, make = checkpoint
    before = make("group")
    fake_router(monkeypatch, turn("generate").model_dump())
    result = await send(before,
        "Il recapito è tecnico@studio.example; genera con i dati già acquisiti.")
    assert result["compilation"]["action"] == "clarify"
    assert compilation_sessions.get_session(project, before["id"]) == before
    context = compilation_chat.planner_context(before)
    assert context["engine"] == "global"


@pytest.mark.anyio
@pytest.mark.parametrize("intent", ["generate", "finish"])
async def test_both_export_aliases_preserve_user_provenance_at_export_checkpoint(
    checkpoint, monkeypatch, intent,
):
    project, _, make = checkpoint
    before = make("generate")
    fake_router(monkeypatch, turn(intent).model_dump())
    result = await send(before, "Puoi procedere con la generazione.")
    assert result["compilation"]["action"] == "generated"
    after = compilation_sessions.get_session(project, before["id"])
    assert after["status"] == "GENERATED"
    assert after["global_compilation"]["dialogue"]["user_values"] == before[
        "global_compilation"]["dialogue"]["user_values"]
