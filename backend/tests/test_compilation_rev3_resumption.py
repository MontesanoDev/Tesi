"""Rev 3 candidate profile, offline: interrupted and resumed segmented compilations.

Scenarios 1-10 of the sprint (PASSO3-ATTESI.md), with every candidate revision enabled.
No new orchestrator: the request-digest cache, bounded retries, narrator recovery and the
unchanged export gates are exercised as they are.
"""

import asyncio
import json

import pytest
import test_compilation_resilient_segments as rev2
from test_compilation_global_sessions import api, provider
from test_compilation_p3 import fact
from test_compilation_p3_hold_validation import SUMMARY, hold, narrator
from test_compilation_sessions import source

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_scope_review as scope
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.compilation_segments import (
    MAX_RETRIES_PER_ANALYSIS,
    applicability_states,
    request_digest,
    resilient_instruction,
    resilient_partition,
    segment_input,
    unverified_fields,
)
from app.db import connection, get_storage_path
from app.generation import GenerationTruncatedError

__all__ = ["api", "provider"]

PROFILE = {"MAPI_GENERATION_REVISION": "3", "MAPI_DIALOGUE_REVISION": "1",
           "MAPI_DERIVATION_REVISION": "1", "MAPI_NARRATION_RECOVERY_REVISION": "1",
           "MAPI_BRANCH_SCOPE_REVISION": "1", "MAPI_HOLD_REREVIEW_REVISION": "1"}


@pytest.fixture(autouse=True, params=["sprint", "incrementale", "predefinito"])
def candidate_profile(monkeypatch, request):
    if request.param == "predefinito":
        # The ordinary «Compilazione DOCX» profile: no variable at all, canonical defaults.
        monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)
        for variable in PROFILE:
            monkeypatch.delenv(variable, raising=False)
        return {}
    profile = dict(PROFILE)
    if request.param == "incrementale":
        profile.update(MAPI_HOLD_REREVIEW_REVISION="2", MAPI_TABLE_SCOPE_REVISION="1")
    for variable, value in profile.items():
        monkeypatch.setenv(variable, value)
    return profile


def flags(session):
    data = rev2.state_of(session)["global_compilation"]
    return {k: v for k, v in data.items() if k.endswith("revision")}


def cache_of(session):
    folder = get_storage_path().resolve() / "alpha" / "_global_compilations" / session["id"]
    return folder / "segment-cache"


def reanalysis(session):
    """Same persisted session asked for a new analysis (as after a SOURCE change)."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = adapter._row_state(db, "alpha", session["id"],
                                        rev2.state_of_version(session))
        state["global_compilation"].update(phase="PENDING")
        state.update(status="CREATED")
        return sessions.save_state(db, row, state, "test_reanalysis")


async def interrupted(api, monkeypatch):
    """Segments 1 and 2 validated and cached; segment 3 interrupted by a process crash."""
    async def late_crash(inp, ids):
        await asyncio.sleep(0.05)
        raise rev2.Interrupted("processo interrotto")

    model = rev2.Model({3: [late_crash]})
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    with pytest.raises(rev2.Interrupted):
        await rev2.analyze(api, session)
    return session, model


async def resumed(api, session, model):
    current = (await api.get(f"{rev2.BASE}/{session['id']}")).json()
    resumed = adapter.control_session("alpha", session["id"], current["version"], "resume")
    model.plan, model.calls = {}, []
    response = await rev2.analyze(api, resumed)
    assert response.status_code == 200, response.text
    return response.json()


# 1-3: interruption, resumption, no duplication.


@pytest.mark.anyio
async def test_1_interruption_after_validated_segments_keeps_work_but_exports_nothing(
    api, provider, monkeypatch, candidate_profile,
):
    session, _ = await interrupted(api, monkeypatch)
    stored = rev2.state_of(session)
    assert stored["status"] == "FAILED" and stored["global_compilation"]["audit"] is None
    assert len(list(cache_of(session).glob("*.json"))) == 2  # Only validated segments.
    assert {"generation_revision", "branch_scope_revision",
            "hold_rereview_revision"} <= set(flags(session))
    for variable, value in candidate_profile.items():
        assert flags(session)[variable.removeprefix("MAPI_").lower()] == int(value)
    if not candidate_profile:  # Ordinary default: the complete canonical profile.
        from app.compilation_profile import SECTIONS

        assert flags(session) == SECTIONS
    current = (await api.get(f"{rev2.BASE}/{session['id']}")).json()
    assert dialogue.export_selection(current) == ([], [], [])
    assert (await rev2.draft(api, current, ["p0.s0"])).status_code == 409


@pytest.mark.anyio
async def test_2_resumption_reuses_the_still_valid_segments(api, provider, monkeypatch):
    session, model = await interrupted(api, monkeypatch)
    session = await resumed(api, session, model)
    report = rev2.segments_of(session)
    assert [s["source"] for s in report["segments"]] == ["cache", "cache", "called"]
    assert all(s["status"] == "analyzed" for s in report["segments"])
    ids, _, _ = dialogue.export_selection(session)
    assert (await rev2.draft(api, session, ids)).status_code == 200  # Same final gates.


@pytest.mark.anyio
async def test_3_no_call_or_proposal_is_duplicated_on_resumption(api, provider, monkeypatch):
    session, model = await interrupted(api, monkeypatch)
    session = await resumed(api, session, model)
    assert model.calls == [(3, 0)]  # One call, for the missing segment only.
    data = rev2.state_of(session)["global_compilation"]
    fields = [f["candidate_id"] for f in data["audit"]["fields"]]
    assert len(fields) == len(set(fields))
    ids, _, _ = dialogue.export_selection(session)
    assert len(ids) == len(set(ids)) == 6  # Two proposals per segment, each once.


# 4-5: invalidation by SOURCE and USER decisions.


@pytest.mark.anyio
async def test_4_a_modified_source_invalidates_every_cached_segment(api, provider, monkeypatch):
    session, model = await interrupted(api, monkeypatch)
    await source(api, "Codice: ABC123\nNumero: 4455", name="altri.md")
    session = await resumed(api, session, model)
    assert [s["source"] for s in rev2.segments_of(session)["segments"]] == ["called"] * 3
    assert sorted(i for i, _ in model.calls) == [1, 2, 3]


def test_5a_registered_user_decisions_are_part_of_every_segment_digest(provider):
    from app.compilation_global import build_global_input
    from app.docx_templates import inspect_docx

    evidence = {"chunk_id": -1, "file_id": -21, "chunk_index": 0, "source_name": "dati.md",
                "role": "source", "scope": "global", "category": "company", "project_id": None,
                "content": "Codice: ABC123"}
    layout = inspect_docx(rev2.form_docx(150))

    def digests(context):
        data = build_global_input(layout, "alpha", [evidence], user_context=context)
        segments = resilient_partition(data["form"])
        return [request_digest(adapter.global_request(
            adapter.get_ai_settings(), segment_input(data, s, revision=3),
            segment=resilient_instruction(s, len(segments), revision=3))) for s in segments]

    decision = {"kind": "registered_decision", "provenance": "USER", "key": "condition:c",
                "action": "CONDITION_TRUE", "applies": True, "user_quote": "Sì, si applica"}
    revoked = {**decision, "action": "CONDITION_FALSE", "applies": False, "user_quote": "No"}
    none, confirmed, denied = digests([]), digests([decision]), digests([revoked])
    assert digests([decision]) == confirmed  # Same decisions: the cache stays usable.
    for a, b, c in zip(none, confirmed, denied, strict=True):
        assert len({a, b, c}) == 3  # Any change of decision misses the cache in every segment.


def two_branches(inp, ids):
    """A free value and a value that depends on an open condition, in the first segment."""
    first = rev2.dato_ids(inp, ids)
    if "p0.s0" not in ids:
        return rev2.ordinary(inp, ids)
    condition = rev2.condition(inp, "paragraph:10", "Dato 10",
                               scope=[{"kind": "candidate", "id": "p10.s0"}])
    return json.dumps(rev2.envelope(inp, {first[0]: rev2.slot(inp, first[0]),
                                          "p10.s0": rev2.slot(inp, "p10.s0", conditions=["k"])},
                                    conditions={"k": condition}))


def reply_with_scope(session, key, action, quote):
    """A USER reply bound to its FORM scope, as the rev 3 guard would verify it."""
    slot = next(s for s in session["chat"]["question"]["slots"] if s["key"] == key)
    reply = ClarificationReply(slot=slot["slot"], action=action, user_quote=quote)
    data = scope.session_data(session)
    proof = scope.proof(scope.target(data, key, slot["field_ids"]), reply)
    session, errors = dialogue.apply_replies("alpha", session["id"], session["version"],
                                             [reply], quote, scope_verifications={
                                                 slot["slot"]: proof})
    assert not errors
    return session


def replace_answer(session, key, record):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = adapter._row_state(db, "alpha", session["id"],
                                        rev2.state_of_version(session))
        state["global_compilation"]["dialogue"]["answers"][key] = record
        return sessions.save_state(db, row, state, "test_revocation")


@pytest.mark.anyio
@pytest.mark.parametrize("change", ["revoked", "condition_changed"])
async def test_5b_a_revoked_or_changed_decision_blocks_only_its_dependent_writes(
    api, provider, monkeypatch, change,
):
    session = await rev2.started(api, monkeypatch, rev2.form_docx(12),
                                 rev2.Model({0: [two_branches], 1: [two_branches]}))
    session = (await rev2.analyze(api, session)).json()
    key = next(q["key"] for q in session["chat"]["question"]["slots"]
               if q["key"].startswith("condition:"))
    session = reply_with_scope(session, key, "CONDITION_TRUE", "Sì, si applica.")
    session = (await rev2.analyze(api, session)).json()
    ids, _, _ = dialogue.export_selection(session)
    assert {"p0.s0", "p10.s0"} <= set(ids)
    record = rev2.state_of(session)["global_compilation"]["dialogue"]["answers"][key]
    if change == "revoked":
        session = replace_answer(session, key, {
            **record, "action": "CONDITION_FALSE", "applies": False, "user_quote": "No."})
    else:
        with connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row, state = adapter._row_state(db, "alpha", session["id"],
                                            rev2.state_of_version(session))
            state["global_compilation"]["audit"]["conditions"][key.removeprefix(
                "condition:")]["reason"] = "Altro"
            session = sessions.save_state(db, row, state, "test_changed_condition")
    data = rev2.state_of(session)["global_compilation"]
    assert "p10.s0" in unverified_fields(data) and "p0.s0" not in unverified_fields(data)
    ids, _, _ = dialogue.export_selection(session)
    assert "p0.s0" in ids and "p10.s0" not in ids
    assert (await rev2.draft(api, session, [*ids, "p10.s0"],
                             conditions=[key.removeprefix("condition:")])).status_code == 409
    assert (await rev2.draft(api, session, ids)).status_code == 200


# 6-8: local failures.


@pytest.mark.anyio
async def test_6_invalid_json_fails_only_its_segment_without_repair(api, provider, monkeypatch):
    model = rev2.Model({2: ['{"version":12,']})
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    session = (await rev2.analyze(api, session)).json()
    report = rev2.segments_of(session)
    assert [s["status"] for s in report["segments"]] == ["analyzed", "failed", "analyzed"]
    failed = set(report["unanalyzed_candidate_ids"])
    data = rev2.state_of(session)["global_compilation"]
    assert failed and all(not f.get("proposal") for f in data["audit"]["fields"]
                          if f["candidate_id"] in failed)
    ids, _, _ = dialogue.export_selection(session)
    assert len(ids) == 4 and not set(ids) & failed
    assert (await rev2.draft(api, session, [*ids, sorted(failed)[0]])).status_code == 409
    assert (await rev2.draft(api, session, ids)).status_code == 200


@pytest.mark.anyio
async def test_7_a_conflict_between_segments_stays_in_review(api, provider, monkeypatch):
    def conflicting(value):
        def answer(inp, ids):
            cid = rev2.dato_ids(inp, ids)[0]
            evidence = next(s for s in inp["sources"] if value in s["content"])
            payload = rev2.envelope(inp, {cid: rev2.slot(inp, cid)})
            payload["facts"] = {"f": fact(value, evidence["chunk_id"])}
            return json.dumps(payload)
        return answer

    def independent(inp, ids):
        """Another property of the same company: no conflict with the code."""
        cid = rev2.dato_ids(inp, ids)[0]
        evidence = next(s for s in inp["sources"] if "4455" in s["content"])
        payload = rev2.envelope(inp, {cid: {**rev2.slot(inp, cid, fact_id="n"),
                                            "property": "numero", "label": "Numero"}})
        payload["facts"] = {"n": {**fact("4455", evidence["chunk_id"], "Numero: 4455"),
                                  "property": "numero"}}
        return json.dumps(payload)

    model = rev2.Model({1: [conflicting("ABC123")], 2: [conflicting("XYZ789")],
                        3: [independent]})
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model,
                                 content="Codice: ABC123\nCodice: XYZ789\nNumero: 4455")
    session = (await rev2.analyze(api, session)).json()
    data = rev2.state_of(session)["global_compilation"]
    report = data["audit"]["generation_segments"]
    assert len(report["conflicts"]) == 1
    disputed = [f["candidate_id"] for f in data["audit"]["fields"]
                if (f.get("proposal") or {}).get("review_kind") == "conflicting"]
    assert len(disputed) == 2
    ids, _, _ = dialogue.export_selection(session)
    assert ids and not set(ids) & set(disputed)  # Segment 3 is untouched by the conflict.
    # Refused either as unreviewed (rev 3 final gate) or as not selectable (review disposition).
    assert (await rev2.draft(api, session, [*ids, disputed[0]])).status_code in {409, 422}


@pytest.mark.anyio
async def test_8_exhausted_retries_leave_independent_segments_valid(api, provider, monkeypatch):
    truncated = GenerationTruncatedError(49152, 49152)
    model = rev2.Model({1: [truncated], 2: [truncated]})
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    session = (await rev2.analyze(api, session)).json()
    report = rev2.segments_of(session)
    assert report["retries"] == MAX_RETRIES_PER_ANALYSIS == 2
    assert [s["status"] for s in report["segments"]] == ["failed", "failed", "analyzed"]
    assert [s["attempts"] for s in report["segments"]] == [2, 2, 1]
    ids, _, _ = dialogue.export_selection(session)
    assert len(ids) == 2 and not set(ids) & set(report["unanalyzed_candidate_ids"])
    states = applicability_states(rev2.state_of(session)["global_compilation"])
    assert all(states.get(c, {}).get("state") in {None, "NON_ACCERTATA"}
               for c in report["unanalyzed_candidate_ids"])
    # Every segment failing: no values, no partial recovery.
    model = rev2.Model({i: [truncated] for i in (1, 2, 3)})
    other = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    response = await rev2.analyze(api, other)
    assert response.status_code != 200 or rev2.state_of(other)["global_compilation"][
        "audit"] is None
    assert rev2.state_of(other)["global_compilation"]["audit"] is None


# 9-10: narrator recovery and safe partial export.


@pytest.mark.anyio
async def test_9_narrator_failing_twice_then_only_the_summary_is_resumed(
    api, provider, monkeypatch,
):
    seen = narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [
        hold([2], "Dato 9", "source")]}, {"questions": []})
    model = rev2.Model()
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    session = (await rev2.analyze(api, session)).json()
    before = rev2.state_of(session)["global_compilation"]
    held = before["dialogue"]["held_candidate_ids"]
    assert len(held) == 1 and len(model.calls) == 3  # One call per segment.
    session = reanalysis_of_dialogue(session)
    narrator(monkeypatch, "not JSON")
    session = (await rev2.analyze(api, session)).json()
    after = rev2.state_of(session)["global_compilation"]
    assert after["dialogue"]["narration_recovery"]["mode"] == "degraded"
    assert after["audit"] == before["audit"] and after["dialogue"]["held_candidate_ids"] == held
    assert not set(held) & set(dialogue.export_selection(session)[0])
    resumed = adapter.control_session("alpha", session["id"], session["version"], "resume")
    seen = narrator(monkeypatch, {"questions": []})
    calls = len(model.calls)
    resumed = (await rev2.analyze(api, resumed)).json()
    assert len(model.calls) == calls  # No new analysis and no segment regenerated.
    assert seen and resumed["global_compilation"]["dialogue"]["narration_recovery"][
        "mode"] == "completed"
    assert rev2.state_of(resumed)["global_compilation"]["dialogue"][
        "held_candidate_ids"] == held  # The hold is never dropped by the recovery.
    ids = dialogue.export_selection(resumed)[0]
    assert ids and not set(ids) & set(held)
    assert (await rev2.draft(api, resumed, ids)).status_code == 200


def reanalysis_of_dialogue(session):
    """The summary is asked again (a new USER turn), the SOURCE audit is unchanged."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = adapter._row_state(db, "alpha", session["id"],
                                        rev2.state_of_version(session))
        state["global_compilation"]["dialogue"].update(phase="PENDING", question=None,
                                                     resuming=True)
        return sessions.save_state(db, row, state, "test_new_summary")


@pytest.mark.anyio
async def test_10_partial_export_is_revalidated_by_the_server(api, provider, monkeypatch):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([1], "Dato 0", "source")]},
             {"questions": []})
    model = rev2.Model({2: ['{"version":12,'], 1: [two_branches]})
    session = await rev2.started(api, monkeypatch, rev2.form_docx(150), model)
    session = (await rev2.analyze(api, session)).json()
    data = rev2.state_of(session)["global_compilation"]
    held = set(data["dialogue"]["held_candidate_ids"])
    failed = set(data["audit"]["generation_segments"]["unanalyzed_candidate_ids"])
    ids, _, _ = dialogue.export_selection(session)
    assert held and failed and ids
    key = next(k for k, c in data["audit"]["conditions"].items()
               if c["form_evidence"]["paragraph_id"] == "paragraph:10")
    blocked = {"held": sorted(held)[0], "unanalyzed": sorted(failed)[0],
               "open_condition": "p10.s0"}
    assert not set(ids) & set(blocked.values())
    for cid in blocked.values():
        # The client may claim anything: the server recomputes every gate from private state.
        response = await rev2.draft(api, session, [*ids, cid], conditions=[key])
        assert response.status_code == 409, (cid, response.text)
    exported = await rev2.draft(api, session, ids)
    assert exported.status_code == 200, exported.text
    body = exported.json()
    # The limits stay explicit in the exported session: unresolved destinations, the failed
    # segment, BACKEND-unassessed coverage and the downloadable audit report.
    assert body["summary"]["total"] == 150 and body["summary"]["pending"] > 0
    view = body["global_compilation"]
    assert any(s["status"] == "failed" for s in view["segments"])
    assert view["coverage_summary"]["explicitly_unassessed"] >= len(failed)
    assert view["report_url"]
