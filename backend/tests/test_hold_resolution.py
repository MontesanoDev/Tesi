"""Every narrator hold has a cause and a USER resolution; none is silent (30 Oct).

E2E campaign, 63 real runs: all 139 narrator holds left at the end of a run had never been
asked to the USER and could never be released (no verifiable link), so the same FORM gave 1 or
33 held values depending on the narrator. A held checkbox option is settled by the explicit
choice of its group; any other hold by one backend verification question, released only by an
explicit USER confirmation; a denial excludes the data, a deferral stays a deferral. A verified
blocker link keeps its own release and every export gate is unchanged. Simulated provider.
"""

import pytest
from test_compilation_global_sessions import api, provider, resolve, start
from test_compilation_p3_hold_validation import FIRST, SECOND, SUMMARY, hold, narrator, state
from test_compilation_resilient_segments import state_of

from app import compilation_global_dialogue as dialogue
from app.compilation_chat import ClarificationReply
from app.compilation_field_outcomes import field_outcomes
from app.compilation_global_dialogue import question_pool
from app.compilation_scope_review import scope_receipt

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def resolution_profile(monkeypatch):
    """The profile that introduced structured holds: an unverifiable doubt on a valid value is
    a verification question there. From sezioni-2026-10-30-r2 the deterministic review settles
    it (test_hold_review)."""
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30")


def verification(session):
    return [s for s in session["chat"]["question"]["slots"] if s["key"].startswith("hold:")]


def reply(session, slot, action):
    data = state_of(session)["global_compilation"]  # The stored state, as the guard sees it.
    message = {"CONDITION_TRUE": "Sì, usa questi dati.", "CONDITION_FALSE": "No, non usarli.",
               "SKIP": "Rinvio questa verifica."}[action]
    answer = ClarificationReply(slot=slot["slot"], action=action, user_quote=message)
    proof = scope_receipt(data, slot["key"], slot["field_ids"], answer).get("scope_validation")
    session, errors = dialogue.apply_replies(
        "alpha", session["id"], session["version"], [answer], message,
        scope_verifications={slot["slot"]: proof} if proof else None)
    assert not errors
    return session


async def held(api, monkeypatch):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Via del Sole 9")]},
             {"questions": []})
    return await resolve(api, await start(api))


@pytest.mark.anyio
async def test_a_source_hold_gets_a_cause_and_one_verification_question(
    api, provider, monkeypatch,
):
    s = await held(api, monkeypatch)
    record = state(s)["hold_records"][SECOND]
    assert record["cause"] == "fonte_insufficiente"
    assert record["resolution"]["kind"] == "verification"
    [slot] = verification(s)
    assert slot["field_ids"] == [SECOND]
    assert slot["question"].startswith("Confermi che posso usare questi dati trovati nelle fonti")
    assert "Via del Sole 9" in slot["question"]  # The documented value, not a model reason.
    assert dialogue.export_selection(s)[0] == [FIRST]  # Still held until the USER answers.


@pytest.mark.anyio
async def test_only_an_explicit_confirmation_releases_it(api, provider, monkeypatch):
    s = await held(api, monkeypatch)
    s = await resolve(api, reply(s, verification(s)[0], "CONDITION_TRUE"))
    assert state(s)["held_candidate_ids"] == []
    assert state(s)["hold_records"][SECOND]["release_reason"] == "USER_RESOLUTION"
    assert dialogue.export_selection(s)[0] == [FIRST, SECOND]


@pytest.mark.anyio
@pytest.mark.parametrize(("action", "outcome"), [("CONDITION_FALSE", "escluso_USER"),
                                                  ("SKIP", "rinvio_USER")])
async def test_a_denial_excludes_and_a_deferral_defers_without_asking_again(
    api, provider, monkeypatch, action, outcome,
):
    s = await held(api, monkeypatch)
    s = await resolve(api, reply(s, verification(s)[0], action))
    assert state(s)["held_candidate_ids"] == [SECOND]
    assert not verification(s)  # Answered once: never asked again.
    data = state_of(s)["global_compilation"]
    assert field_outcomes(data, written={FIRST})["campi"][SECOND]["esito"] == outcome


def test_a_held_checkbox_option_is_settled_by_its_group_choice_only():
    data = {"audit": {"choice_groups": {"g": {"validation": "GROUNDED_GROUP",
                                              "options": {"p1.cb0": {}, "p2.cb0": {}}}}}}
    resolution = dialogue._hold_resolution(data, "p1.cb0", {"cause": "scelta_USER"})
    assert resolution == {"kind": "selection", "key": "choice:g"}
    assert not dialogue._resolution_settled(resolution, {"choice:g": {"action": "SKIP"}})
    assert dialogue._resolution_settled(resolution, {"choice:g": {"action": "VALUE"}})


@pytest.mark.anyio
async def test_the_previous_profile_keeps_the_silent_hold(api, provider, monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-25")
    s = await held(api, monkeypatch)
    assert "resolution" not in state(s)["hold_records"][SECOND] and not verification(s)



def window(quote, slot=1):
    """A hold on p5.s0 (own condition «own») naming condition k, which does not gate it."""
    from test_compilation_hold_rereview import empty_context, window_data

    data = window_data()
    data["hold_resolution_revision"] = 1
    pool = [{"key": "condition:k", "kind": "applicability", "field_ids": ["p10.s0"],
             "condition": "Dato 10", "context": "Dato 10"}]
    context = empty_context(["ABC123"])
    context["applicability_contexts"] = [{"slot": 1, "condition_key": "own", "result": "unknown",
                                          "form_evidence": {"quote": "Dato 5"}}]
    context["document_values"][0]["applicability_slots"] = [1]
    plan = dialogue.ContinuationPlan(held_proposal_slots=[1], hold_reviews=[
        dialogue.ProposalHoldReview(proposal_slot=1, blocker="applicability",
                                    reason="Dubbio del narratore", evidence_quote=quote,
                                    condition_slot=slot)])
    proposals = [{"candidate_id": "p5.s0", "conditions": ["own"], "selectable": True}]
    data["dialogue"].update(dialogue._hold_updates(data, proposals, context, plan, "r1",
                                                   pool=pool))
    return data, pool


def again(data, pool):
    from test_compilation_hold_rereview import empty_context

    update = dialogue._hold_updates(data, [], empty_context([]), dialogue.ContinuationPlan(),
                                    "r2", pool=pool)
    data["dialogue"].update(update)
    return update["held_candidate_ids"]


def test_unrelated_answers_never_release_it_only_its_verification_does():
    """C8 of the P3 preregistration with structured holds."""
    data, pool = window("ABC123")
    record = data["dialogue"]["hold_records"]["p5.s0"]
    assert "blocker_key" not in record and record["resolution"]["kind"] == "verification"
    answers = data["dialogue"]["answers"]
    answers.update({"condition:k": {"applies": True, "action": "CONDITION_TRUE"},
                    "condition:own": {"applies": True, "action": "CONDITION_TRUE"}})
    assert again(data, pool) == ["p5.s0"]
    answers[record["resolution"]["key"]] = {"action": "SKIP"}
    assert again(data, pool) == ["p5.s0"]  # A deferral never releases.
    answers[record["resolution"]["key"]] = {"applies": True, "action": "CONDITION_TRUE"}
    assert again(data, pool) == []


def test_a_verified_blocker_link_keeps_its_own_release_and_no_extra_question():
    data, pool = window("Dato 5", slot=None)  # The quote of its own condition: C9.
    record = data["dialogue"]["hold_records"]["p5.s0"]
    assert record["blocker_key"] == "condition:own" and "resolution" not in record
    assert dialogue.hold_questions(data) == []


def held_options_case():
    """A valid single-choice group whose options the narrator held (real checkbox run 3)."""
    from test_compilation_hold_rereview import window_data

    data = window_data()
    data.update(hold_resolution_revision=1, writable_ids=["p8.cb0", "p9.cb0"])
    group = {"validation": "GROUNDED_GROUP", "selection": "single", "min_selected": 1,
             "conditions": [], "label": "Tipologia del partner",
             "form_evidence": {"paragraph_id": "paragraph:7", "quote": "Tipologia del partner"},
             "options": {"p8.cb0": {"label": "Organizzazione tecnica"},
                         "p9.cb0": {"label": "Studio collettivo"}}}
    data["audit"]["choice_groups"] = {"g": group}
    data["audit"]["fields"] += [{"candidate_id": c, "conditions": [], "choice_group_id": "g",
                                 "kind": "choice", "validation": "GROUNDED_PROPOSAL",
                                 "proposed_value": c == "p9.cb0", "label": o["label"],
                                 "form_evidence": {"paragraph_id": "paragraph:" + c[1],
                                                   "quote": o["label"]}}
                                for c, o in group["options"].items()]
    resolution = {"kind": "selection", "key": "choice:g"}
    data["dialogue"].update(held_candidate_ids=["p8.cb0", "p9.cb0"], hold_records={
        c: {"status": "held", "cause": "applicabilita_incerta", "resolution": resolution}
        for c in ("p8.cb0", "p9.cb0")})
    return data


def test_a_held_group_is_asked_as_an_explicit_choice_even_when_the_narrator_asks_nothing():
    pool = question_pool(held_options_case())
    [choice] = [q for q in pool if q["key"] == "choice:g"]
    assert choice.get("hold_selection")  # Asked although SOURCE documents an option.
    plan = dialogue.DialoguePlan(message="Posso preparare la bozza.", questions=[])
    [slot] = dialogue.render_dialogue(plan, pool)["question"]["slots"]
    assert slot["key"] == "choice:g"
    assert "1) Organizzazione tecnica" in slot["question"] and "2) Studio collettivo" in slot[
        "question"]
