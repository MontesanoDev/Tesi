"""P3 narrator holds: a doubtful hold never discards the narration nor frees a proposal.

Counterexamples C1-C11 of the preregistration (narratore-p3-20261022-01), simulated provider.
"""

import json
from io import BytesIO

import pytest
from test_compilation_global_sessions import BASE, api, proposal, provider, resolve, start
from test_compilation_option_authorization import ASSENT, cciaa_doc
from test_compilation_sessions import docx, source

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.db import connection
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]

SUMMARY = "Ho trovato i dati della società nelle fonti."
FIRST, SECOND = "t0.r0.c1", "t0.r1.c1"


@pytest.fixture(autouse=True)
def p3_dialogue(monkeypatch):
    """The private P3 runtime: dialogue revision, monolithic generation."""
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    monkeypatch.delenv("MAPI_GENERATION_REVISION", raising=False)


def narrator(monkeypatch, *responses):
    """Narration n returns responses[n] (the last one repeats); callables get the context."""
    seen = []

    async def request(client, settings, body, timeout, **kwargs):
        context = json.loads(body["messages"][1]["content"])
        seen.append(context)
        response = responses[min(len(seen), len(responses)) - 1]
        return json.dumps(response(context) if callable(response) else response), \
            "simulated", {}

    monkeypatch.setattr(dialogue, "request_model_content", request)
    return seen


def hold(slots, quote, blocker="source", condition_slot=None):
    return {"proposal_slots": slots, "blocker": blocker, "reason": "Dubbio del narratore",
            "evidence_quote": quote,
            **({"condition_slot": condition_slot} if condition_slot else {})}


def slot_of(context, label):
    return next(q["slot"] for q in context["question_pool"] if q["label"] == label)


async def conditional_session(api, monkeypatch, conditions):
    """Each proposal depends on its own FORM condition: c = 'Dati aziendali', d = 'Sede legale'."""
    quotes = {"c": ("paragraph:0", "Dati aziendali"), "d": ("paragraph:3", "Sede legale")}

    async def request(client, settings, body, timeout, **kwargs):
        result = proposal(json.loads(body["messages"][1]["content"]), conditional=True)
        result["conditions"] = {key: {
            "form": {"paragraph_id": quotes[key][0], "quote": quotes[key][1]},
            "aspect": "participation", "operator": "semantic", "fact_ids": [],
            "scope": [{"kind": "candidate", "id": cid} for cid, keys in conditions.items()
                      if key in keys], "reason": f"Condizione {key}"}
            for key in sorted({k for keys in conditions.values() for k in keys})}
        for cid, keys in conditions.items():
            result["fields"][cid]["conditions"] = keys
        return json.dumps(result), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", request)
    return await start(api)


def answer(session, label, action="CONDITION_TRUE"):
    slot = next(s for s in session["chat"]["question"]["slots"] if s["label"] == label)
    message = "Sì, si applica al nostro caso."
    session, errors = dialogue.apply_replies("alpha", session["id"], session["version"], [
        ClarificationReply(slot=slot["slot"], action=action, user_quote=message)], message)
    assert not errors
    return session


def state(session):
    return session["global_compilation"]["dialogue"]


@pytest.mark.anyio
async def test_c1_anchored_hold_is_recorded_and_only_that_proposal_waits(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], "Via del Sole 9")]})
    s = await resolve(api, await start(api))
    record = state(s)["hold_records"][SECOND]
    assert state(s)["held_candidate_ids"] == [SECOND] and not state(s).get("error")
    assert (record["reason_validation"], record["reason_status"]) == ("RECORDED", "recorded")
    assert dialogue.export_selection(s)[0] == [FIRST]


@pytest.mark.anyio
@pytest.mark.parametrize(("quote", "location"), [
    ("Aurora Servizi S.r.l.", "document_values"),  # C4: literal, but another proposal's.
    ("La sede non risulta da alcuna fonte", "not_found"),  # C5: paraphrase.
])
async def test_c4_c5_unanchored_hold_keeps_the_proposal_and_the_narration(
    api, provider, monkeypatch, quote, location,
):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [hold([2], quote)]})
    s = await resolve(api, await start(api))
    record = state(s)["hold_records"][SECOND]
    assert not state(s).get("error") and s["chat"]["question"]["kind"] == "generate"
    assert state(s)["held_candidate_ids"] == [SECOND]
    assert record["reason_validation"] == "UNANCHORED_QUOTE"
    assert record["reason_status"] == "unverified" and record["quote_location"] == location
    assert "blocker_key" not in record
    assert dialogue.export_selection(s)[0] == [FIRST]


@pytest.mark.anyio
async def test_c4_unanchored_hold_is_not_released_by_the_slot_it_names(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, lambda context: {"message": SUMMARY, "questions": [
        {"slot": slot_of(context, "Condizione c"), "confirmation": "la sezione si applica"}],
        "hold_groups": [hold([2], "Aurora Servizi S.r.l.", "applicability",
                             slot_of(context, "Condizione c"))]}, {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["c"]}))
    s = await resolve(api, answer(s, "Condizione c"))
    assert state(s)["held_candidate_ids"] == [SECOND]
    assert dialogue.export_selection(s)[0] == [FIRST]


@pytest.mark.anyio
async def test_c2_reference_outside_an_empty_window_is_recorded_without_effect(
    api, provider, monkeypatch,
):
    seen = narrator(monkeypatch, lambda context: {"message": SUMMARY, "questions": [
        {"slot": slot_of(context, "Condizione c"), "confirmation": "la sezione si applica"}]},
        {"questions": [], "hold_groups": [hold([1, 2], "Dati aziendali", "applicability", 1)]})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["c"]}))
    s = await resolve(api, answer(s, "Condizione c"))
    assert seen[-1]["document_values"] == []  # Everything was already reviewed.
    transition = state(s)["hold_transition"]
    assert not state(s).get("error") and state(s)["held_candidate_ids"] == []
    assert [r["proposal_slot"] for r in transition["invalid_references"]] == [1, 2]
    assert transition["invalid_references"][0]["evidence_quote"] == "Dati aziendali"
    assert sorted(dialogue.export_selection(s)[0]) == [FIRST, SECOND]


@pytest.mark.anyio
async def test_c3_unresolvable_reference_keeps_the_whole_window_held(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [
        hold([1], "Aurora Servizi S.r.l."), hold([3], "Via del Sole 9")]})
    s = await resolve(api, await start(api))
    records = state(s)["hold_records"]
    assert not state(s).get("error")
    assert state(s)["held_candidate_ids"] == [FIRST, SECOND]
    assert records[FIRST]["reason_validation"] == "RECORDED"  # Its own reason is kept.
    assert records[SECOND]["reason_validation"] == "UNRESOLVED_REFERENCE"
    assert not any("blocker_key" in r for r in records.values())
    assert dialogue.export_selection(s)[0] == []


@pytest.mark.anyio
async def test_c6_repeated_reference_is_held_with_every_reason(api, provider, monkeypatch):
    narrator(monkeypatch, {"message": SUMMARY, "hold_groups": [
        hold([2], "Via del Sole 9", "form"), hold([1, 2], "Aurora Servizi S.r.l.")]})
    s = await resolve(api, await start(api))
    records = state(s)["hold_records"]
    assert state(s)["held_candidate_ids"] == [FIRST, SECOND]
    assert records[SECOND]["reason_validation"] == "REPEATED_REFERENCE"
    assert records[SECOND]["other_reviews"][0]["evidence_quote"] == "Aurora Servizi S.r.l."
    assert records[FIRST]["reason_validation"] == "RECORDED"
    assert dialogue.export_selection(s)[0] == []


@pytest.mark.anyio
@pytest.mark.parametrize("action", ["SKIP", "CONDITION_TRUE"])
async def test_c7_procedural_hold_release_never_bypasses_the_authorization(
    api, provider, monkeypatch, action,
):
    stream = BytesIO()
    cciaa_doc().save(stream)
    uploaded = await api.post("/api/projects/alpha/forms", files={
        "file": ("modulo.docx", stream.getvalue())})
    await source(api, "Mapi Demo S.r.l.; Camera di Commercio competente: Bari. Numero di "
                      "iscrizione al Registro delle Imprese: 01234560981.", name="visura.md")

    async def global_proposal(client, settings, body, timeout, **kwargs):
        inp = json.loads(body["messages"][1]["content"])
        cells = sorted(cid for cid, c in inp["form"]["candidates"].items() if c["type"] == "text")
        labels = {p["id"]: p["text"] for b in inp["form"]["blocks"] for p in b["paragraphs"]}
        label = {cell: next(p for p in labels if labels[p].startswith(text))
                 for cell, text in zip(cells, ["Provincia", "numero"], strict=True)}
        evidence = next(s for s in inp["sources"] if "01234560981" in s["content"])
        facts = {name: {"subject": "Mapi Demo S.r.l.", "entity": "company",
                        "aspect": "identity", "property": name, "value": value,
                        "evidence": [{"chunk_id": evidence["chunk_id"], "quote": quote}]}
                 for name, value, quote in [
                     ("provincia", "Bari", "Camera di Commercio competente: Bari"),
                     ("numero", "01234560981", "Registro delle Imprese: 01234560981")]}
        return json.dumps({"version": 12, "facts": facts, "conditions": {}, "fields": {
            cell: {"label": name, "kind": "data", "disposition": "value", "conditions": [],
                   "property": name, "fact_id": name,
                   "form": {"paragraph_id": label[cell], "quote": labels[label[cell]].strip()}}
            for cell, name in zip(cells, ["provincia", "numero"], strict=True)},
            "bindings": {}, "choice_groups": {}, "coverage": [], "clarifications": {}}), \
            "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", global_proposal)
    narrator(monkeypatch, lambda context: {"message": SUMMARY, "hold_groups": [
        hold([1, 2], "attività coerente", "user_decision", next(
            q["slot"] for q in context["question_pool"]
            if "attività coerente" in q["context"] + q["condition"]))]}, {"questions": []})
    session = (await api.post(BASE, json={"form_id": uploaded.json()["id"], "engine": "global",
                                         "start_in_chat": True})).json()
    session = await resolve(api, session)
    cells = sorted(f["candidate_id"] for f in session["global_compilation"]["fields"])
    records = state(session)["hold_records"]
    assert state(session)["held_candidate_ids"] == cells
    assert all(records[c]["blocker_key_basis"] == "GOVERNING_SLOT" and
               records[c]["blocker_key"].startswith("authorization:") for c in cells)
    slot = next(s for s in session["chat"]["question"]["slots"]
                if s["key"].startswith("authorization:"))
    quote = ASSENT if action == "CONDITION_TRUE" else "Rinvia questa dichiarazione"
    session, errors = dialogue.apply_replies("alpha", session["id"], session["version"], [
        ClarificationReply(slot=slot["slot"], action=action, user_quote=quote)], quote)
    assert not errors
    session = await resolve(api, session)
    assert state(session)["held_candidate_ids"] == []  # The narrator doubt was answered...
    ids = dialogue.export_selection(session)[0]
    assert set(ids) == (set(cells) if action == "CONDITION_TRUE" else set())  # ...V14 decides.


@pytest.mark.anyio
async def test_c8_hold_naming_a_slot_that_does_not_gate_the_proposal_stays(
    api, provider, monkeypatch,
):
    narrator(monkeypatch, lambda context: {"message": SUMMARY, "questions": [
        {"slot": slot_of(context, f"Condizione {k}"), "confirmation": "la sezione si applica"}
        for k in "cd"], "hold_groups": [hold([2], "Via del Sole 9", "applicability",
                                              slot_of(context, "Condizione c"))]},
        {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["d"]}))
    record = state(s)["hold_records"][SECOND]
    assert record["reason_validation"] == "RECORDED" and "blocker_key" not in record
    s = await resolve(api, answer(s, "Condizione c"))
    s = await resolve(api, answer(s, "Condizione d"))
    assert state(s)["held_candidate_ids"] == [SECOND]
    assert dialogue.export_selection(s)[0] == [FIRST]


@pytest.mark.anyio
async def test_c9_hold_citing_its_own_condition_waits_for_that_condition_only(
    api, provider, monkeypatch,
):
    def first(context):
        return {"message": SUMMARY, "questions": [
            {"slot": slot_of(context, f"Condizione {k}"), "confirmation": "si applica"}
            for k in "cd"], "hold_groups": [hold([2], "Sede legale", "applicability",
                                                  slot_of(context, "Condizione c"))]}

    narrator(monkeypatch, first, {"questions": []})
    s = await resolve(api, await conditional_session(
        api, monkeypatch, {FIRST: ["c"], SECOND: ["d"]}))
    record = state(s)["hold_records"][SECOND]
    assert (record["blocker_key"], record["blocker_key_basis"]) == (
        "condition:d", "OWN_CONDITION_QUOTE")
    s = await resolve(api, answer(s, "Condizione c"))
    assert state(s)["held_candidate_ids"] == [SECOND]  # Another answer does not free it.
    s = await resolve(api, answer(s, "Condizione d"))
    assert state(s)["held_candidate_ids"] == []
    assert state(s)["hold_transition"]["released_blocker_answered"] == [SECOND]
    assert sorted(dialogue.export_selection(s)[0]) == [FIRST, SECOND]
    # The same doubt raised again after its condition was answered is suppressed, visibly.
    narrator(monkeypatch, {"questions": [], "hold_groups": [
        hold([1], "Sede legale", "applicability", 1)]})
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, saved = adapter._row_state(db, "alpha", s["id"], s["version"])
        saved["global_compilation"]["dialogue"].update(
            phase="PENDING", question=None, reviewed_candidate_ids=[FIRST],
            reviewed_candidate_fingerprints={
                FIRST: saved["global_compilation"]["dialogue"][
                    "reviewed_candidate_fingerprints"][FIRST]})
        s = sessions.save_state(db, row, saved, "test_rereview")
    s = await resolve(api, s)
    assert state(s)["held_candidate_ids"] == []
    assert state(s)["hold_transition"]["suppressed_blocker_answered"] == [SECOND]


@pytest.mark.anyio
async def test_c10_legacy_session_still_rejects_an_unanchored_quote(api, provider, monkeypatch):
    narrator(monkeypatch, {"message": SUMMARY, "questions": [], "held_proposal_slots": [2],
                           "hold_reviews": [{"proposal_slot": 2, "blocker": "source",
                                             "reason": "Dubbio",
                                             "evidence_quote": "Aurora Servizi S.r.l."}]})
    monkeypatch.delenv("MAPI_DIALOGUE_REVISION")
    s = await resolve(api, await start(api))
    assert "dialogue_revision" not in s["global_compilation"]
    assert state(s)["error"] == "ValueError"
    assert dialogue.export_selection(s) == ([], [], [])


def test_c3_c11_invalid_reference_never_frees_inherited_or_outside_holds():
    proposals = [{"candidate_id": "a"}, {"candidate_id": "b"}]
    context = {"document_values": [
        {"proposal_slot": i, "label": c, "value": c, "applicability_slots": []}
        for i, c in enumerate("ab", 1)], "role_contexts": [], "previous_answers": [],
        "applicability_contexts": []}
    data = {"dialogue": {"held_candidate_ids": ["old"], "answers": {},
                         "hold_records": {"old": {"status": "held", "reason_status": "recorded",
                                                  "blocker_key": "condition:k"}}}}
    irregular = {"invalid_references": [{"proposal_slot": 7}], "repeated_references": {}}
    update = dialogue._hold_updates(data, proposals, context, dialogue.ContinuationPlan(), "r",
                                    pool=[], irregular=irregular)
    assert update["held_candidate_ids"] == ["a", "b", "old"]
    assert {update["hold_records"][c]["reason_validation"] for c in "ab"} == {
        "UNRESOLVED_REFERENCE"}
    assert update["hold_transition"]["invalid_references"] == [{"proposal_slot": 7}]
    empty = dialogue._hold_updates(data, [], {**context, "document_values": []},
                                   dialogue.ContinuationPlan(), "r", pool=[],
                                   irregular=irregular)
    assert empty["held_candidate_ids"] == ["old"]  # Nothing to protect, nothing freed.


def test_new_sessions_default_to_the_v14_k3_profile_and_p3_is_opt_in(monkeypatch):
    layout = inspect_docx(docx())
    monkeypatch.delenv("MAPI_DIALOGUE_REVISION")
    default = adapter.initial_state(layout)
    assert {k: v for k, v in default.items() if k.endswith("revision")} == {
        "backend_revision": 13, "option_authorization_revision": 1,
        "attribution_safety_revision": 1, "derivation_revision": 1}
    for variable, revision in [("MAPI_DIALOGUE_REVISION", "dialogue_revision"),
                               ("MAPI_GENERATION_REVISION", "generation_revision")]:
        monkeypatch.setenv(variable, "1")
        state = adapter.initial_state(layout)
        assert state[revision] == 1 and {k for k in state if k.endswith("revision")} == {
            *(k for k in default if k.endswith("revision")), revision}
        monkeypatch.delenv(variable)
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "0")
    assert adapter.initial_state(layout) == default


@pytest.mark.anyio
@pytest.mark.parametrize("created_with_p3", [True, False])
async def test_runtime_default_never_changes_an_existing_session(
    api, provider, monkeypatch, created_with_p3,
):
    prompts = []

    async def summary(client, settings, body, timeout, **kwargs):
        prompts.append(body["messages"][0]["content"])
        return json.dumps({"message": SUMMARY, "questions": []}), "simulated", {}

    monkeypatch.setattr(dialogue, "request_model_content", summary)
    if not created_with_p3:
        monkeypatch.delenv("MAPI_DIALOGUE_REVISION")
    s = await start(api)
    if created_with_p3:
        monkeypatch.delenv("MAPI_DIALOGUE_REVISION")  # The runtime default changes later.
    else:
        monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    s = await resolve(api, s)
    assert s["global_compilation"].get("dialogue_revision") == (1 if created_with_p3 else None)
    assert ("VERSIONE CON SOSPENSIONI RAGGRUPPATE" in prompts[-1]) is created_with_p3
    assert ("reference_date" in provider[-1]) is created_with_p3
