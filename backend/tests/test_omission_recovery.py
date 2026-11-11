"""Destinations the model declared not assessed go back to it once, with the segment recovery.

Real campaign on 94e8726, Minervino run 1: 19 member destinations had no proposal, declared
«unassessed» («il FORM non indica quale nominativo occupi lo slot 1») although SOURCE documents
them. Only a text destination with no proposal, no rejection, a FORM anchor and the model's own
«unassessed» is sent; justified empties («source_not_found», manual input, conditions) and
layout cells are never touched; every new proposal passes the ordinary validators.
"""

import json

import pytest
from test_compilation_global_sessions import api, provider
from test_compilation_resilient_segments import (
    Model,
    analyze,
    dato_ids,
    envelope,
    form_docx,
    paragraph_of,
    segments_of,
    slot,
    started,
    state_of,
)

from app.compilation_omissions import omitted_destinations

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def coverage(inp, cid, outcome):
    paragraph = paragraph_of(inp, cid)
    return {"candidate_ids": [cid], "outcome": outcome, "reason": "Abbinamento non determinabile",
            "form": {"paragraph_id": paragraph["id"], "quote": paragraph["text"][:20]}}


def first(outcome="unassessed"):
    def answer(inp, ids):
        chosen = dato_ids(inp, ids)
        payload = envelope(inp, {c: slot(inp, c) for c in (chosen[0], chosen[-1])})
        payload["coverage"] = [coverage(inp, chosen[1], outcome)]
        return json.dumps(payload)
    return answer


def recovery(seen):
    def answer(inp, ids):
        seen.append(ids)
        return json.dumps(envelope(inp, {c: slot(inp, c) for c in ids}))
    return answer


def entry(session):
    return segments_of(session)["segments"][0].get("recovery")


@pytest.mark.anyio
async def test_a_destination_the_model_did_not_assess_is_recovered_once(
    api, provider, monkeypatch,
):
    seen = []
    model = Model({1: [first(), recovery(seen)]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    report = entry(session)
    [cid] = report["omitted"]
    assert seen == [[cid]] and report["recovered"] == [cid]
    fields = {f["candidate_id"]: f for f in state_of(session)["global_compilation"]["audit"][
        "fields"]}
    assert fields[cid]["value"] == "ABC123" and not fields[cid].get("validation_errors")


@pytest.mark.anyio
async def test_the_recovery_request_says_why_and_how_repeated_slots_are_ordered(
    api, provider, monkeypatch,
):
    bodies = []
    model = Model({1: [first(), recovery([])]})
    original = model.__call__

    async def call(client, settings, body, timeout, **kwargs):
        bodies.append(body)
        return await original(client, settings, body, timeout, **kwargs)

    session = await started(api, monkeypatch, form_docx(3), call)
    await analyze(api, session)
    text = bodies[-1]["messages"][-1]["content"]
    assert "Destinazioni non valutate" in text and "Abbinamento non determinabile" in text
    assert "ordine in cui le SOURCE" in text


@pytest.mark.anyio
async def test_a_justified_empty_is_never_sent_back(api, provider, monkeypatch):
    model = Model({1: [first("source_not_found"), "ok"]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    assert entry(session) is None and len(model.calls) == 1


def test_a_layout_cell_without_a_FORM_anchor_is_not_an_omission():
    audit = {"fields": [{"candidate_id": c, "coverage": {"state": "UNASSESSED",
                                                         "origin": "MODEL"}} for c in "ab"]}
    catalog = {"candidates": {
        "a": {"type": "text", "anchor_paragraph_ids": [], "slot_context": {}},
        "b": {"type": "text", "anchor_paragraph_ids": ["paragraph:3"],
              "slot_context": {"before": "1) nome e cognome "}}}}
    assert list(omitted_destinations({}, audit, "ab", catalog)) == ["b"]
    assert omitted_destinations({}, audit, "ab", catalog)["b"]["label"] == "1) nome e cognome"


@pytest.mark.anyio
async def test_the_previous_profile_recovers_no_omission(api, provider, monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30")
    model = Model({1: [first(), "ok"]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    assert entry(session) is None and len(model.calls) == 1
