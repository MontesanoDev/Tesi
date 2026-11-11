"""The scope of a closed confirmation is the destinations the backend shows (30 Oct).

E2E campaign: real guard verdicts SUPPORTED/AMBIGUOUS refused explicit «Sì, confermo …»
replies because the model's condition was a fragment («dell'operatore economico»), held two
alternatives or grouped heterogeneous data; the same FORM gave 0 or 9 writes from run to run.
The question now lists what the confirmation concerns; a relevant yes/no to it has exactly that
scope. An ambiguous or unrelated reply is still refused; a deferral of a shown question needs
no scope check. Synthetic FORM.
"""

import json

import pytest
from test_documented_conditions_not_skipped import case

from app.compilation_chat import ClarificationReply
from app.compilation_global_dialogue import DialoguePlan, question_pool, render_dialogue
from app.compilation_reply_guard import verify_field_replies
from app.config import AISettings, use_ai_settings


def test_every_applicability_question_lists_its_destinations():
    pool = question_pool(case())
    [condition] = [q for q in pool if q["kind"] == "applicability"]
    plan = DialoguePlan(message="Riepilogo dei punti aperti.", questions=[
        {"slot": condition["slot"], "confirmation": "il ramo della società si applica"}])
    [slot] = render_dialogue(plan, pool, require_confirmation=True)["question"]["slots"]
    assert slot["question"].startswith("Confermi che il ramo della società si applica (riguarda: ")
    assert slot["destinations_shown"] is True


CONTEXT = {"question": "Confermi?", "slots": [
    {"slot": 1, "kind": "applicability", "label": "Ramo", "destinations_shown": True,
     "affected_field_count": 2}],
    "form_scope": {"slots": {"1": {"digest": "d", "destinations": [
        {"candidate_id": "p0.s0", "candidate": {"type": "text"}}]}}}}


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def verdict(result, scope, shown=True, action="CONDITION_TRUE"):
    context = {**CONTEXT, "slots": [{**CONTEXT["slots"][0], "destinations_shown": shown}]}

    async def request(client, settings, body, timeout, **kwargs):
        checks = {"checks": [{"slot": 1, "result": result, "scope_result": scope}]}
        return json.dumps(checks), "fake", {}

    reply = ClarificationReply(slot=1, action=action, user_quote="Sì, confermo")
    with use_ai_settings(AISettings(api_key="k", model="m", base_url="https://x.invalid")):
        return (await verify_field_replies("Sì, confermo", context, [reply],
                                           request=request)).allowed_slots


@pytest.mark.anyio
async def test_a_relevant_yes_to_a_shown_question_has_the_shown_scope():
    assert await verdict("SUPPORTED", "AMBIGUOUS") == {1}
    assert await verdict("SUPPORTED", "AMBIGUOUS", action="CONDITION_FALSE") == {1}


@pytest.mark.anyio
async def test_ambiguous_unrelated_or_unshown_replies_are_still_refused():
    assert await verdict("AMBIGUOUS", "AMBIGUOUS") == frozenset()
    assert await verdict("UNRELATED", "SUPPORTED") == frozenset()
    assert await verdict("SUPPORTED", "AMBIGUOUS", shown=False) == frozenset()
