"""Ordinary profile: an explicit global-draft selection cannot bypass the summary.

The documented contract builds the selection from the chat's persisted state, without manual
selection. A held or unreviewed proposal requested by id is refused (409); the explicit,
recorded release of a hold remains the USER answer to its linked doubt.
"""

import json

import pytest
from test_compilation_global_sessions import BASE, api, provider, resolve, start
from test_compilation_p3_hold_validation import (
    FIRST,
    SECOND,
    SUMMARY,
    answer,
    conditional_session,
    hold,
    narrator,
    slot_of,
)

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.db import connection

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    for variable in ("MAPI_DIALOGUE_REVISION", "MAPI_GENERATION_REVISION",
                     "MAPI_NARRATION_RECOVERY_REVISION"):
        monkeypatch.delenv(variable, raising=False)


async def draft(api, session, ids, conditions=()):
    return await api.post(f"{BASE}/{session['id']}/global-draft", json={
        "version": session["version"], "candidate_ids": list(ids),
        "confirmed_condition_ids": list(conditions), "allow_unresolved": True,
        "user_quote": "Genera la bozza parziale"})


def edit(session, change):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        change(state["global_compilation"])
        return sessions.save_state(db, row, state, "test_explicit_draft")


@pytest.mark.anyio
@pytest.mark.parametrize("profile", ["ordinary", "p3"])
async def test_a_held_proposal_requested_by_id_is_refused(api, provider, monkeypatch, profile):
    if profile == "p3":
        monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
        narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Via del Sole 9")]})
    else:
        narrator(monkeypatch, {"message": SUMMARY, "questions": [], "held_proposal_slots": [2],
                               "hold_reviews": [{"proposal_slot": 2, "blocker": "source",
                                                 "reason": "Dubbio sulla sede",
                                                 "evidence_quote": "Via del Sole 9"}]})
    s = await resolve(api, await start(api))
    assert ("dialogue_revision" in s["global_compilation"]) is (profile == "p3")
    assert s["global_compilation"]["dialogue"]["held_candidate_ids"] == [SECOND]
    assert dialogue.export_selection(s)[0] == [FIRST]
    for ids in ([FIRST, SECOND], [SECOND]):
        refused = await draft(api, s, ids)
        assert refused.status_code == 409 and "sospesa" in refused.json()["detail"]
    exported = await draft(api, s, [FIRST])
    assert exported.status_code == 200, exported.text


@pytest.mark.anyio
async def test_a_proposal_whose_review_is_no_longer_current_is_refused(api, provider):
    s = await resolve(api, await start(api))
    assert sorted(dialogue.export_selection(s)[0]) == [FIRST, SECOND]

    def stale(data):
        data["dialogue"]["reviewed_candidate_fingerprints"][SECOND] = "impronta non corrente"

    s = edit(s, stale)
    assert dialogue.export_selection(s)[0] == [FIRST]
    assert (await draft(api, s, [FIRST, SECOND])).status_code == 409
    assert (await draft(api, s, [FIRST])).status_code == 200


@pytest.mark.anyio
async def test_the_recorded_answer_to_the_linked_doubt_is_the_explicit_release(
    api, provider, monkeypatch,
):
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")

    def first(context):
        return {"message": SUMMARY, "questions": [
            {"slot": slot_of(context, f"Condizione {k}"), "confirmation": "si applica"}
            for k in "cd"], "hold_groups": [hold([2], "Sede legale", "applicability",
                                                  slot_of(context, "Condizione c"))]}

    narrator(monkeypatch, first, {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["d"]}))
    s = await resolve(api, answer(s, "Condizione c"))
    assert (await draft(api, s, [FIRST, SECOND], ["c", "d"])).status_code == 409
    s = await resolve(api, answer(s, "Condizione d"))
    record = s["global_compilation"]["dialogue"]["hold_records"][SECOND]
    assert record["release_reason"] == "BLOCKER_ANSWERED"
    exported = await draft(api, s, [FIRST, SECOND], ["c", "d"])
    assert exported.status_code == 200, exported.text


@pytest.mark.anyio
async def test_a_session_without_any_dialogue_keeps_its_previous_behaviour(api, provider):
    s = await resolve(api, await start(api))
    s = edit(s, lambda data: data.pop("dialogue"))
    with connection() as db:
        stored = json.loads(sessions._row(db, "alpha", s["id"])["state_json"])
    assert "dialogue" not in stored["global_compilation"]
    exported = await draft(api, s, [FIRST, SECOND])
    assert exported.status_code == 200, exported.text
