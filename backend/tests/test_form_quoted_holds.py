"""A narrator hold that cites FORM text is an applicability doubt the USER can settle (30 Oct).

E2E campaign, real Minervino runs: up to 31 documented values per run were held with blocker
«source» while their evidence quote was FORM text («e composta da (riportare nominativo…)»,
«la quale ha come Responsabile della Progettazione…»): no USER answer could release them, even
after the branch was confirmed. A hold quoting SOURCE text keeps its meaning. Simulated
provider, real session (P3 helpers).
"""

import pytest
from test_compilation_global_sessions import api, provider, resolve
from test_compilation_p3_hold_validation import (
    FIRST,
    SECOND,
    SUMMARY,
    answer,
    conditional_session,
    hold,
    narrator,
    slot_of,
    state,
)

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def p3_dialogue(monkeypatch):
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    monkeypatch.delenv("MAPI_GENERATION_REVISION", raising=False)


def holding(quote):
    def first(context):
        return {"message": SUMMARY, "questions": [
            {"slot": slot_of(context, f"Condizione {k}"), "confirmation": "si applica"}
            for k in "cd"], "hold_groups": [hold([2], quote, "source")]}
    return first


@pytest.mark.anyio
async def test_a_source_hold_quoting_the_form_waits_for_the_proposal_s_own_conditions(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, holding("Dati aziendali"), {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["d"]}))
    record = state(s)["hold_records"][SECOND]
    assert record["blocker_key"] == "conditions:d" and record["blocker_reclassified"] == "source"
    s = await resolve(api, answer(s, "Condizione d"))
    assert state(s)["held_candidate_ids"] == []


@pytest.mark.anyio
async def test_a_source_hold_quoting_source_text_is_kept(api, provider, monkeypatch):
    narrator(monkeypatch, holding("Via del Sole 9"), {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["d"]}))
    assert "blocker_key" not in state(s)["hold_records"][SECOND]
    s = await resolve(api, answer(s, "Condizione d"))
    assert state(s)["held_candidate_ids"] == [SECOND]
