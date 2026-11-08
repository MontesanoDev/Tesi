"""Invalid JSON syntax in a segment gets bounded retries that say where it broke (30 Oct).

Real run on 4dd1087 (compilazione): the model closed segment 1 with one brace too few twice
(«Expecting ',' delimiter», finish_reason stop); the single structural retry was spent and 14
destinations stayed unassessed. Up to two more attempts, only for JSON syntax, each saying
where the previous answer stopped being valid; never a JSON repair. Other segments and their
validated results are untouched; a segment that still fails stays visibly unassessed.
"""

import json

import pytest
from test_compilation_global_sessions import api, provider
from test_compilation_resilient_segments import (
    Model,
    analyze,
    form_docx,
    ordinary,
    segments_of,
    started,
    state_of,
)

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def broken(inp, ids):
    return ordinary(inp, ids)[:-1]  # One closing brace too few, as in the real answer.


class Recorder(Model):
    def __init__(self, plan):
        super().__init__(plan)
        self.bodies = []

    async def __call__(self, client, settings, body, timeout, **kwargs):
        self.bodies.append(body)
        return await super().__call__(client, settings, body, timeout, **kwargs)


def segment(session, index=1):
    return next(s for s in segments_of(session)["segments"] if s["index"] == index)


@pytest.mark.anyio
async def test_invalid_json_twice_then_valid_is_analyzed_with_the_error_said(
    api, provider, monkeypatch,
):
    model = Recorder({1: [broken, broken, "ok"]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    report = segment(session)
    assert report["status"] == "analyzed" and report["attempts"] == 3
    assert report["format_retries"] == 1
    notes = ["FORMATO NON VALIDO" in b["messages"][-1]["content"] for b in model.bodies]
    assert notes == [False, True, True]  # Every retry after a syntax error says where.
    assert "carattere" in model.bodies[1]["messages"][-1]["content"]


@pytest.mark.anyio
async def test_a_segment_still_invalid_stays_unassessed_and_others_are_kept(
    api, provider, monkeypatch,
):
    model = Recorder({2: [broken]})  # Always invalid; segments 1 and 3 answer normally.
    session = (await analyze(api, await started(api, monkeypatch, form_docx(150), model))).json()
    report = segments_of(session)
    assert [s["status"] for s in report["segments"]] == ["analyzed", "failed", "analyzed"]
    assert segment(session, 2)["attempts"] == 4  # 1 + 1 structural + 2 for syntax only.
    audit = state_of(session)["global_compilation"]["audit"]
    unassessed = set(report["unanalyzed_candidate_ids"])
    assert unassessed and all(f["coverage"]["state"] == "UNASSESSED" for f in audit["fields"]
                              if f["candidate_id"] in unassessed)


@pytest.mark.anyio
async def test_an_invalid_envelope_is_not_a_syntax_error_and_gets_no_extra_retry(
    api, provider, monkeypatch,
):
    model = Recorder({1: [json.dumps({"version": 11})]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(150), model))).json()
    assert segment(session)["attempts"] == 2 and segment(session)["format_retries"] == 0


@pytest.mark.anyio
async def test_the_previous_profile_keeps_a_single_retry(api, provider, monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30")
    model = Recorder({1: [broken, broken, "ok"]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(150), model))).json()
    assert segment(session)["status"] == "failed" and segment(session)["attempts"] == 2
