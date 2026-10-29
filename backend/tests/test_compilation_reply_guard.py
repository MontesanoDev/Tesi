"""Independent semantic verdicts gate actual writes; provider outputs are simulated."""

import copy
import json

import httpx
import pytest
from test_dialogue_benchmark import checkpoint as checkpoint

from app import compilation_chat, compilation_sessions, intents
from app.compilation_reply_guard import ReplyScopeChecks, accepted_slots
from app.config import AISettings, use_ai_settings
from app.generation import GenerationError
from app.main import app
from scripts.benchmark_compilation_dialogue import FIXTURE, changed_state, seed_checkpoint
from scripts.benchmark_compilation_reply_guard import load_guard_fixture


@pytest.fixture
def anyio_backend():
    return "asyncio"


def proposal(slot, value, *, action="VALUE", normalized_value=None):
    return {"slot": slot, "action": action, "value": value,
            "normalized_value": normalized_value}


def checker(monkeypatch, replies, checks):
    calls = []

    async def request(client, settings, body, timeout, **kwargs):
        calls.append(copy.deepcopy(body))
        if kwargs["response_schema"]["title"] == "ReplyScopeChecks":
            assert timeout <= 15 and body["max_tokens"] == 768
            data = json.loads(body["messages"][1]["content"])
            assert data["operation"] == "check_field_reply_scope"
            assert "field_id" not in json.dumps(data) and "session_id" not in json.dumps(data)
            assert len(data["proposals"]) <= 4
            assert all("rationale" not in p for p in data["proposals"])
            if isinstance(checks, Exception):
                raise checks
            raw = checks if isinstance(checks, str) else json.dumps({"checks": checks})
        else:
            message = body["messages"][1]["content"].split("ULTIMO MESSAGGIO:\n")[-1]
            raw = json.dumps({"intent": "answer_fields", "answer": "", "queries": [],
                              "target": "form", "replies": [
                                  {**r, "user_quote": r.get("user_quote", message)}
                                  for r in replies]})
        return raw, "simulated", {"total_tokens": 10}

    monkeypatch.setattr(intents, "request_model_content", request)
    return calls


async def plan(before, message):
    with use_ai_settings(AISettings(api_key="simulated-key", model="simulated",
                                   base_url="https://provider.invalid")):
        return await intents.plan_chat_turn(message, [],
            compilation=compilation_chat.planner_context(before))


@pytest.mark.parametrize("checks,allowed", [
    ([{"slot": 1, "result": "SUPPORTED"}], {1}),
    ([{"slot": 1, "result": "UNRELATED"}], set()),
    ([{"slot": 1, "result": "AMBIGUOUS"}], set()),
    ([], set()),
    ([{"slot": 2, "result": "SUPPORTED"}], set()),
    ([{"slot": 1, "result": "SUPPORTED"}, {"slot": 1, "result": "SUPPORTED"}], set()),
])
def test_only_unique_matching_slots_can_authorize(checks, allowed):
    assert accepted_slots(json.dumps({"checks": checks}), {1}) == allowed


@pytest.mark.parametrize("raw", [
    "not JSON", '{"checks":[{"slot":1,"result":"SUPPORTED","field_id":"invented"}]}',
    '{"checks":[{"slot":1,"result":true}]}',
])
def test_invalid_verification_does_not_authorize(raw):
    with pytest.raises(ValueError):
        accepted_slots(raw, {1})


@pytest.mark.anyio
@pytest.mark.parametrize("context,message,value,action", [
    ("email", "Correggi la denominazione aziendale in Aurora Servizi S.r.l.",
     "Aurora Servizi S.r.l.", "VALUE"),
    ("date", "Il riferimento della pratica è QR-17.", "QR-17", "VALUE"),
    ("condition", "No, la nostra polizza non copre questo rischio.", None, "CONDITION_FALSE"),
])
async def test_wrong_subject_is_rejected_through_actual_http_and_state_preserved(
    checkpoint, monkeypatch, context, message, value, action,
):
    project, _, make = checkpoint
    before = make(context)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "simulated-key")
    calls = checker(monkeypatch, [proposal(1, value, action=action)], [
        {"slot": 1, "result": "UNRELATED"}])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test",
    ) as c:
        response = await c.post(f"/api/projects/{project}/answer", json={
            "question": message, "conversation_id": before["conversation_id"],
            "compilation_session_id": before["id"], "compilation_version": before["version"],
        })
    assert response.status_code == 200, response.text
    assert response.json()["compilation"] is None
    assert "Non posso associare" in response.json()["answer"]
    assert compilation_sessions.get_session(project, before["id"]) == before
    assert len(calls) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("context,message,value,normalized", [
    ("email", "Usa contatti@aurora.example", "contatti@aurora.example", None),
    ("date", "12 giugno 2014", "12 giugno 2014", "12/06/2014"),
])
async def test_real_domain_accepts_pertinent_bare_or_natural_value(
    checkpoint, monkeypatch, context, message, value, normalized,
):
    project, _, make = checkpoint
    before = make(context)
    calls = checker(monkeypatch, [proposal(1, value, normalized_value=normalized)], [
        {"slot": 1, "result": "SUPPORTED"}])
    planned = await plan(before, message)
    await compilation_chat.handle_group_decision(project, before["conversation_id"],
        planned.decision, before, message, before["version"])
    after = compilation_sessions.get_session(project, before["id"])
    values = after["global_compilation"]["dialogue"]["user_values"]
    assert [v["value"] for v in values.values()] == [normalized or value]
    assert all(v["provenance"] == "USER" for v in values.values())
    assert len(calls) == 2 and planned.total_tokens == 20


@pytest.mark.anyio
async def test_batch_keeps_pertinent_parts_and_drops_wrong_condition(checkpoint, monkeypatch):
    project, _, make = checkpoint
    before = make("group")
    message = "La polizza non copre il rischio. Usa contatti@aurora.example."
    calls = checker(monkeypatch, [
        {**proposal(1, None, action="CONDITION_FALSE"),
         "user_quote": "La polizza non copre il rischio."},
        {**proposal(2, "contatti@aurora.example"), "user_quote": "Usa contatti@aurora.example."},
    ], [{"slot": 1, "result": "UNRELATED"}, {"slot": 2, "result": "SUPPORTED"}])
    planned = await plan(before, message)
    assert [r.slot for r in planned.decision.replies] == [2]
    await compilation_chat.handle_group_decision(project, before["conversation_id"],
        planned.decision, before, message, before["version"])
    after = compilation_sessions.get_session(project, before["id"])
    answers = after["global_compilation"]["dialogue"]["answers"]
    assert set(answers) == {"field:t0.r1.c1"}
    assert answers["field:t0.r1.c1"]["value"] == "contatti@aurora.example"
    assert len(calls) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("checks", [
    [], [{"slot": 1, "result": "AMBIGUOUS"}], "bad JSON",
    GenerationError("Provider unavailable"),
])
async def test_missing_ambiguous_invalid_or_failed_verdict_never_writes(
    checkpoint, monkeypatch, checks,
):
    project, _, make = checkpoint
    before = make("email")
    calls = checker(monkeypatch, [proposal(1, "contatti@aurora.example")], checks)
    planned = await plan(before, "contatti@aurora.example")
    assert planned.intent == "explain" and planned.decision.action == "reply"
    assert compilation_sessions.get_session(project, before["id"]) == before
    assert len(calls) == 2  # No semantic retries or new analysis.


@pytest.mark.anyio
@pytest.mark.parametrize("action", ["UNKNOWN", "SKIP", "REFUSE", "CLARIFY"])
async def test_non_value_controls_need_no_additional_call(checkpoint, monkeypatch, action):
    _, _, make = checkpoint
    before = make("email")
    calls = checker(monkeypatch, [proposal(1, None, action=action)], [])
    planned = await plan(before, "Una risposta di controllo")
    assert planned.intent == "answer_fields" and len(calls) == 1
    assert planned.total_tokens == 10


def test_guard_schema_has_no_identity_or_value_writing_capability():
    schema = json.dumps(ReplyScopeChecks.model_json_schema())
    assert "field_id" not in schema and "session_id" not in schema
    assert "normalized_value" not in schema and '"value"' not in schema


GROUP_CONTEXTS, GROUP_CASES = load_guard_fixture(
    FIXTURE.parent / "group-confirmations-v1")[1:]


@pytest.mark.anyio
@pytest.mark.parametrize("case", GROUP_CASES, ids=lambda case: case["id"])
async def test_group_verdicts_gate_only_backend_owned_recipients(
    checkpoint, monkeypatch, case,
):
    """Simulated verdicts test state boundaries, not model semantic quality."""
    project, _, make = checkpoint
    initial = make("conditions")
    context = GROUP_CONTEXTS[case["context"]]
    before = seed_checkpoint(project, {"id": initial["form_id"]}, context,
                             case["id"], FIXTURE / "modulo-dialogo.docx")
    expected = set(case["expected_allowed_slots"])
    checks = [{"slot": r["slot"], "result": (
        "SUPPORTED" if r["slot"] in expected else "AMBIGUOUS")}
        for r in case["proposals"]]
    calls = checker(monkeypatch, case["proposals"], checks)
    planned = await plan(before, case["message"])
    payload = json.loads(calls[1]["messages"][1]["content"])
    assert [s["question"] for s in payload["slots"]] == [
        s["question"] for s in context["slots"]]
    assert payload["message"] == case["message"]
    assert "expected" not in json.dumps(payload)
    if expected:
        assert {r.slot for r in planned.decision.replies} == expected
        await compilation_chat.handle_group_decision(project, before["conversation_id"],
            planned.decision, before, case["message"], before["version"])
    else:
        assert planned.intent == "explain"
    after = compilation_sessions.get_session(project, before["id"])
    effects = changed_state(before, after, context["slots"])
    assert set(effects["actions"]) == {str(s) for s in expected}
    assert effects["provenance_ok"] and not effects["unexpected_recipients"]
    if not expected:
        assert after == before  # No revision on a rejected semantic proposal.
    assert not after["last_generation"]
    assert after["global_compilation"]["attempts"] == before["global_compilation"]["attempts"]
    assert all(f["status"] != "RESOLVED" for f in after["fields"])
    assert len(calls) == 2  # Same one routing + one verification, no retry.
