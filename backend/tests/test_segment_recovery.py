"""Targeted recovery of the proposals the validators rejected in one segment (30 Oct).

E2E campaign, real runs on f0c48ba: an analyzed segment lost up to 26 destinations to
validator rejections (Minervino: required role «socio», attested «Soci»; checkbox: «SOURCE
riferita a soggetto/proprietà differenti»; Catanzaro: option polarity). Structural retries
existed, field rejections were never retried. One second call per segment, limited to the
rejected destinations and with the backend reasons; the validators are unchanged and a
recovery is discarded if it would change any destination already accepted. Simulated provider.
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

from app.compilation_segments import apply_recovery

__all__ = ["api", "provider"]


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def first(inp, ids, wrong=1):
    """Valid first and last destinations, plus `wrong` destinations with the wrong property."""
    chosen = dato_ids(inp, ids)
    fields = {c: slot(inp, c) for c in (chosen[0], chosen[-1])}
    for cid in chosen[1:1 + wrong]:
        fields[cid] = {**slot(inp, cid), "property": "partita_iva"}
    return json.dumps(envelope(inp, fields))


def corrected(inp, ids):
    return json.dumps(envelope(inp, {c: slot(inp, c) for c in ids}))


def fields_of(session):
    return {f["candidate_id"]: f for f in state_of(session)["global_compilation"]["audit"][
        "fields"]}


def rejected_and_kept(session):
    report = segments_of(session)["segments"][0]
    return report.get("recovery"), fields_of(session)


@pytest.mark.anyio
async def test_a_rejected_destination_is_recovered_once_with_the_backend_reason(
    api, provider, monkeypatch,
):
    seen = []

    def recovery(inp, ids):
        seen.append(ids)
        return corrected(inp, ids)

    model = Model({1: [first, recovery]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    entry, fields = rejected_and_kept(session)
    [cid] = entry["rejected"]
    assert seen == [[cid]] and len(model.calls) == 2  # Only the rejected destination.
    assert "proprietà" in entry["rejected"][cid]["reasons"][0]
    assert entry["status"] == "applied" and entry["recovered"] == [cid]
    assert not fields[cid].get("validation_errors") and fields[cid]["value"] == "ABC123"


@pytest.mark.anyio
async def test_the_recovery_never_touches_accepted_destinations_or_widens_them(
    api, provider, monkeypatch,
):
    def recovery(inp, ids):
        payload = json.loads(corrected(inp, ids))
        accepted = dato_ids(inp, list(inp["form"]["candidates"]))
        # Extra destinations and a condition over all of them: neither may be taken.
        payload["fields"].update({c: {**slot(inp, c), "label": "Altro"} for c in accepted})
        payload["conditions"] = {"c": {
            "form": {"paragraph_id": paragraph_of(inp, ids[0])["id"], "quote": "Dato"},
            "aspect": "participation", "operator": "semantic", "fact_ids": [],
            "reason": "Applicabilità", "scope": [{"kind": "candidate", "id": c}
                                                  for c in accepted]}}
        return json.dumps(payload)

    model = Model({1: [first, recovery]})
    session = await started(api, monkeypatch, form_docx(3), model)
    session = (await analyze(api, session)).json()
    entry, fields = rejected_and_kept(session)
    accepted = [c for c, f in fields.items() if c not in entry["rejected"] and f.get("value")]
    assert accepted and all(fields[c]["label"] != "Altro" for c in accepted)
    assert all(not fields[c].get("conditions") for c in accepted)


@pytest.mark.anyio
async def test_a_recovery_still_rejected_leaves_the_destination_rejected(
    api, provider, monkeypatch,
):
    def again(inp, ids):  # The same wrong property again.
        return json.dumps(envelope(inp, {c: {**slot(inp, c), "property": "partita_iva"}
                                         for c in ids}))

    model = Model({1: [first, again]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    entry, fields = rejected_and_kept(session)
    [cid] = entry["rejected"]
    assert entry["still_rejected"] == [cid] and entry["recovered"] == []
    assert fields[cid].get("validation_errors") and len(model.calls) == 2
    # The original rejected proposal is kept, not the recovery's (later repairs see it).
    assert fields[cid]["proposal"]["property"] == "partita_iva"
    assert fields[cid]["proposal"]["fact_id"] == "f"  # Not the recovery fact «r_f».


@pytest.mark.anyio
async def test_no_rejection_no_second_call(api, provider, monkeypatch):
    model = Model({1: [lambda inp, ids: first(inp, ids, wrong=0)]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    assert "recovery" not in segments_of(session)["segments"][0] and len(model.calls) == 1


@pytest.mark.anyio
async def test_the_previous_profile_has_no_recovery(api, provider, monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-25")
    model = Model({1: [first, "ok"]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    assert "recovery" not in segments_of(session)["segments"][0] and len(model.calls) == 1


def test_recovered_fields_keep_their_conditions_and_groups_stay_within_the_rejected():
    original = {"fields": {"a": {"fact_id": "f", "conditions": ["c"]}, "b": {"fact_id": "f"}},
                "facts": {"f": {}}, "conditions": {"c": {}}, "choice_groups": {},
                "bindings": {}, "coverage": [{"candidate_ids": ["a", "b"]}]}
    recovery = {"fields": {"a": {"fact_id": "g", "conditions": []},
                           "x": {"choice_group_id": "grp"}},
                "facts": {"g": {"value": 1}, "h": {"value": 2}}, "conditions": {},
                "choice_groups": {"grp": {"options": {"x": {}, "b": {}}}}, "bindings": {}}
    patched, report = apply_recovery(original, recovery, {"a", "x"})
    assert patched["fields"]["a"] == {"fact_id": "r_g", "conditions": ["c"]}
    assert patched["fields"]["b"] == original["fields"]["b"]
    assert set(patched["facts"]) == {"f", "r_g"}  # Unreferenced recovery facts stay out.
    assert report == {"recovered_fields": ["a"], "skipped": {
        "x": "Gruppo di scelta oltre le destinazioni respinte"}}
    assert patched["coverage"] == [{"candidate_ids": ["b"]}]


@pytest.mark.anyio
async def test_a_recovery_that_would_change_an_accepted_value_is_discarded(
    api, provider, monkeypatch,
):
    def sibling(inp, ids):
        # A grounded fact for the same subject and property with another value: the accepted
        # destinations would become unselected alternatives without any validation error.
        payload = json.loads(corrected(inp, ids))
        evidence = next(s for s in inp["sources"] if "XYZ789" in s["content"])
        payload["facts"]["g"] = {**payload["facts"]["f"], "value": "XYZ789",
                                 "evidence": [{"chunk_id": evidence["chunk_id"],
                                               "quote": "Codice alternativo: XYZ789"}]}
        payload["fields"][ids[0]]["fact_id"] = "g"
        return json.dumps(payload)

    model = Model({1: [first, sibling]})
    session = await started(api, monkeypatch, form_docx(3), model,
                            content="Codice: ABC123\nCodice alternativo: XYZ789")
    session = (await analyze(api, session)).json()
    entry, fields = rejected_and_kept(session)
    assert entry["status"] == "failed" and "già valide" in entry["error"]
    assert [f["value"] for c, f in fields.items() if c not in entry["rejected"]] == [
        "ABC123", "ABC123"]


def test_rejections_the_deterministic_recovery_repairs_are_left_to_it():
    from app.compilation_factual_recovery import OWNER_FAILURE, ROLE_FAILURE
    from app.compilation_segments import rejected_destinations

    payload = {"fields": {c: {"fact_id": "f", "label": c} for c in "abc"}}
    audit = {"fields": [{"candidate_id": "a", "validation_errors": [ROLE_FAILURE]},
                        {"candidate_id": "b", "validation_errors": [OWNER_FAILURE]},
                        {"candidate_id": "c", "validation_errors": ["Ruolo FORM esterno"]}]}
    assert list(rejected_destinations(payload, audit, "abc")) == ["c"]


def test_the_destinations_of_the_signatory_block_are_never_recovered_by_the_model():
    from test_signatory_question_blocked_proposal import BLOCK, blocked_case

    from app.compilation_segments import signatory_destinations

    data, _, _ = blocked_case()
    assert set(BLOCK) <= signatory_destinations(data["catalog"])


@pytest.mark.anyio
async def test_only_the_rejected_component_is_replaced_the_grounded_value_stays(
    api, provider, monkeypatch,
):
    """Real Minervino run (ee80067): the recovery fixed the rejected role binding of 24 members
    but cited their facts with a heading absent from SOURCE; the original facts were grounded.
    Here the property was wrong and the recovered fact cites text absent from SOURCE."""
    def broken_fact(inp, ids):
        payload = json.loads(corrected(inp, ids))
        payload["facts"]["f"]["evidence"][0]["quote"] = "## Codici aziendali"
        return json.dumps(payload)

    model = Model({1: [first, broken_fact]})
    session = (await analyze(api, await started(api, monkeypatch, form_docx(3), model))).json()
    entry, fields = rejected_and_kept(session)
    [cid] = entry["rejected"]
    assert entry["recovered"] == [cid] and not fields[cid].get("validation_errors")
    assert fields[cid]["value"] == "ABC123"  # The value SOURCE had already grounded.


def test_a_recovery_condition_on_the_same_FORM_clause_is_the_original_condition():
    """Real Trapani run (c8413ed): the recovery re-declared the company condition on the same
    option paragraph under a new name; the validator linked it to the accepted destinations of
    that paragraph and the whole recovery was discarded (3 values lost)."""
    original = {"fields": {"a": {"fact_id": "f", "conditions": ["c"]},
                           "b": {"fact_id": "f", "conditions": ["c"]}},
                "facts": {"f": {}}, "bindings": {}, "choice_groups": {}, "coverage": [],
                "conditions": {"c": {"form": {"paragraph_id": "paragraph:5", "quote": "Società"},
                                     "operator": "semantic", "scope": []}}}
    recovery = {"fields": {"b": {"fact_id": "g", "conditions": ["k"]}}, "facts": {"g": {}},
                "conditions": {"k": {"form": {"paragraph_id": "paragraph:5",
                                              "quote": "Legale rappresentante di Società"},
                                     "operator": "semantic", "scope": []}},
                "bindings": {}, "choice_groups": {}}
    patched, _ = apply_recovery(original, recovery, {"b"})
    assert patched["fields"]["b"]["conditions"] == ["c"]
    assert set(patched["conditions"]) == {"c"}  # No second condition on the same clause.
    other = {**recovery, "conditions": {"k": {**recovery["conditions"]["k"],
                                              "form": {"paragraph_id": "paragraph:9"}}}}
    patched, _ = apply_recovery(original, other, {"b"})
    assert patched["fields"]["b"]["conditions"] == ["c", "r_k"]  # Another clause stays its own.
