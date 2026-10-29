"""The reply guard's raw verdicts are kept in the private routing trace (E2E, 29 Oct).

Real Trapani run: an explicit «Sì, confermo che si applica: …» was refused twice for its
scope, and nothing recorded what the guard had answered. The verdicts are now traced for
diagnosis only: they are never shown to the USER and never decide anything.
"""

import json

import pytest

from app.compilation_chat import ClarificationReply
from app.compilation_reply_guard import verify_field_replies
from app.compilation_routing_trace import RoutingTrace
from app.config import AISettings, use_ai_settings

RAW = json.dumps({"checks": [{"slot": 1, "result": "AMBIGUOUS", "rationale": "Motivo"}]})
CONTEXT = {"question": "Confermi?", "slots": [{"slot": 1, "kind": "applicability",
                                               "label": "Ramo", "field_ids": ["p0.s0"]}]}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_the_guard_verdict_is_traced_and_survives_the_routing_result(tmp_path):
    async def request(client, settings, body, timeout, **kwargs):
        return RAW, "fake", {"total_tokens": 3}

    reply = ClarificationReply(slot=1, action="CONDITION_TRUE", user_quote="Sì, confermo")
    with use_ai_settings(AISettings(api_key="k", model="m", base_url="https://x.invalid")):
        result = await verify_field_replies("Sì, confermo", CONTEXT, [reply], request=request)
    assert result.raw == RAW and not result.allowed_slots
    trace = RoutingTrace(tmp_path, None)
    trace.guard(result)
    trace.complete("answer_fields")
    saved = json.loads((tmp_path / "trace.json").read_text())["result"]
    assert saved["intent"] == "answer_fields" and saved["guard"]["raw"] == RAW
    assert saved["guard"]["reasons"] == {"1": "AMBIGUOUS"}
