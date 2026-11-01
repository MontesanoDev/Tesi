"""USER facts stay atomic, guarded and separate from applicability/authorization."""

import json
from copy import deepcopy
from io import BytesIO

import pytest
from docx import Document
from test_compilation_global_sessions import BASE, api, provider, resolve

from app import compilation_chat, intents
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_scope_review as scope
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.config import use_ai_settings
from app.db import connection

__all__ = ["api", "provider"]
REAL_QUOTE = ("Il sottoscrittore è Leonardo Montemurro, nato a Lecce (LE) il 14/11/1982, "
              "residente a Bari (BA), via Amedeo 24.")
REAL_VALUE = REAL_QUOTE.removeprefix("Il sottoscrittore è ").removesuffix(".")


@pytest.fixture
def anyio_backend():
    return "asyncio"


def document():
    doc = Document()
    doc.add_paragraph("Il sottoscritto ________, nato a ________ (____) il ________, residente")
    doc.add_paragraph("in ________ (____), via ________, C.F. ________, in qualità di")
    doc.add_paragraph("________ dell’operatore economico ________ con sede in ________")
    doc.add_paragraph("Dichiaro il possesso dei requisiti: [ ] sì [ ] no")
    return doc


async def ready(api, monkeypatch, doc=None):
    monkeypatch.setenv("MAPI_GENERATION_REVISION", "3")
    monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")
    stream = BytesIO()
    (doc or document()).save(stream)
    form = (await api.post("/api/projects/alpha/forms", files={
        "file": ("domanda.docx", stream.getvalue())})).json()

    async def empty(client, settings, body, timeout, **kwargs):
        return json.dumps({"version": 12, "fields": {}, "facts": {}, "conditions": {},
                           "bindings": {}, "choice_groups": {}, "clarifications": {},
                           "coverage": []}), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", empty)
    session = (await api.post(BASE, json={"form_id": form["id"], "engine": "global",
                                        "start_in_chat": True})).json()
    session = await resolve(api, session)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        data = state["global_compilation"]
        data.update(user_extraction_revision=1, generation_revision=3, dialogue_revision=1)
        slot = next(q for q in dialogue.question_pool(data) if q["key"] == "field:p0.s0")
        slot.update(slot=1, question="Nome, nascita e residenza del sottoscrittore?")
        data["dialogue"].update(phase="READY", error=None, question={
            "kind": "clarifications", "message": slot["question"], "slots": [slot],
            "field_ids": []})
        session = sessions.save_state(db, row, state, "test_atomic_user_question")
    return session, deepcopy(data), slot


@pytest.mark.anyio
async def test_recorded_compound_value_cannot_be_saved_as_name_even_with_guard_proof(
    api, provider, monkeypatch,
):
    session, data, slot = await ready(api, monkeypatch)
    reply = ClarificationReply(slot=1, action="VALUE", value=REAL_VALUE, user_quote=REAL_QUOTE)
    proof = scope.proof(scope.target(data, slot["key"], slot["field_ids"]), reply)
    after, errors = dialogue.apply_replies("alpha", session["id"], session["version"],
        [reply], REAL_QUOTE, scope_verifications={1: proof})
    assert errors == [1]
    saved = after["global_compilation"]["dialogue"]
    assert "p0.s0" not in saved.get("user_values", {})
    assert "Ho registrato" not in dialogue.continuation_receipt(saved)


@pytest.mark.anyio
@pytest.mark.parametrize("name", ["Ada Neri", "Jean-Luc D’Amico", "Liam O’Connor"])
async def test_a_name_alone_remains_a_guarded_literal_value(api, provider, monkeypatch, name):
    session, data, slot = await ready(api, monkeypatch)
    reply = ClarificationReply(slot=1, action="VALUE", value=name, user_quote=name)
    proof = scope.proof(scope.target(data, slot["key"], slot["field_ids"]), reply)
    after, errors = dialogue.apply_replies("alpha", session["id"], session["version"],
        [reply], name, scope_verifications={1: proof})
    assert not errors
    assert after["global_compilation"]["dialogue"]["user_values"]["p0.s0"]["value"] == name


async def routed(session, monkeypatch, quote=REAL_QUOTE, value=REAL_VALUE, refuse=()):
    calls = []

    async def model(client, settings, body, timeout, **kwargs):
        if kwargs["response_schema"]["title"] == "FormScopeChecks":
            sent = json.loads(body["messages"][1]["content"])
            calls.append(sent)
            assert len(sent["proposals"]) <= 4
            checks = []
            for p in sent["proposals"]:
                target = sent["form_scope"]["slots"][str(p["slot"])]
                assert len(target["destinations"]) == 1
                cid = target["destinations"][0]["candidate_id"]
                checks.append({"slot": p["slot"], "result": "SUPPORTED",
                               "scope_result": "AMBIGUOUS" if cid in refuse else "SUPPORTED"})
            raw = {"checks": checks}
        else:
            raw = {"intent": "answer_fields", "answer": "", "queries": [], "target": "form",
                   "replies": [{"slot": 1, "action": "VALUE", "value": value,
                                "user_quote": quote}]}
        return json.dumps(raw), "fake", {"total_tokens": 10}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        planned = await intents.plan_chat_turn(quote, [],
            compilation=compilation_chat.planner_context(session))
    return planned.decision, calls


def apply(session, decision, message):
    return dialogue.apply_replies("alpha", session["id"], session["version"], decision.replies,
        message, decision.unaccepted_slots, decision.scope_verifications,
        decision.unaccepted_reasons, decision.value_extractions)


@pytest.mark.anyio
async def test_recorded_reply_is_split_guarded_persisted_and_exported_as_seven_facts(
    api, provider, monkeypatch,
):
    session, data, slot = await ready(api, monkeypatch)
    decision, calls = await routed(session, monkeypatch)
    assert decision.replies[0].value == "Leonardo Montemurro"
    assert len(calls) == 3  # Ordinary name check plus two bounded batches of extra facts.
    assert {p["value"] for c in calls for p in c["proposals"]} == {
        "Leonardo Montemurro", "Lecce", "LE", "14/11/1982", "Bari", "BA", "Amedeo 24"}
    after, errors = apply(session, decision, REAL_QUOTE)
    assert not errors
    saved = after["global_compilation"]["dialogue"]
    expected = {"p0.s0": "Leonardo Montemurro", "p0.s1": "Lecce", "p0.s2": "LE",
                "p0.s3": "14/11/1982", "p1.s0": "Bari", "p1.s1": "BA", "p1.s2": "Amedeo 24"}
    assert {cid: v["value"] for cid, v in saved["user_values"].items()} == expected
    assert saved["user_extractions"][0]["message"] == REAL_QUOTE
    assert saved["user_extractions"][0]["original_reply"]["value"] == REAL_VALUE
    assert not any(k.startswith(("choice:", "condition:")) for k in saved["answers"])
    assert "Ho registrato" not in dialogue.continuation_receipt(saved)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", after["id"], after["version"])
        live = state["global_compilation"]
        assert all(scope.valid_receipt(live, "field:" + cid, saved["answers"]["field:" + cid], cid)
                   for cid in expected)
        live["dialogue"]["phase"] = "READY"
        after = sessions.save_state(db, row, state, "test_export_after_review")
    ids, conditions, users = dialogue.export_selection(after)
    assert set(users) == set(expected)
    generated = await api.post(f"{BASE}/{after['id']}/global-draft", json={
        "version": after["version"], "candidate_ids": ids, "confirmed_condition_ids": conditions,
        "user_candidate_ids": users, "allow_unresolved": True, "user_quote": "Genera la bozza"})
    assert generated.status_code == 200, generated.text
    downloads = generated.json()["last_generation"]["downloads"]
    report = (await api.get(downloads["report"])).json()
    assert {f["cell_id"]: f["written_value"] for f in report["fields"]} == expected
    output = Document(BytesIO((await api.get(downloads["docx"])).content))
    assert "Il sottoscritto Leonardo Montemurro, nato a Lecce (LE) il 14/11/1982" in (
        "\n".join(p.text for p in output.paragraphs))
    assert "[X]" not in "\n".join(p.text for p in output.paragraphs)


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["refused", "missing_proof", "changed_value", "changed_form"])
async def test_one_extra_value_needs_its_own_unchanged_proof(api, provider, monkeypatch, failure):
    session, _, _ = await ready(api, monkeypatch)
    cid = "p0.s3"
    decision, _ = await routed(session, monkeypatch, refuse=[cid] if failure == "refused" else [])
    record = decision.value_extractions[0]
    if failure == "missing_proof":
        record["proofs"].pop(cid)
    elif failure == "changed_value":
        record["values"][cid]["value"] = "01/01/2000"
        with pytest.raises(ValueError, match="Estrazione USER"):
            apply(session, decision, REAL_QUOTE)
        assert not sessions.get_session("alpha", session["id"])["global_compilation"][
            "dialogue"].get("user_values")
        return
    elif failure == "changed_form":
        record["proofs"][cid] = record["proofs"]["p1.s0"]
    after, errors = apply(session, decision, REAL_QUOTE)
    saved = after["global_compilation"]["dialogue"]
    assert cid not in saved["user_values"]
    assert saved["user_values"]["p0.s0"]["value"] == "Leonardo Montemurro"
    assert cid in saved["extraction_pending"]
    assert any(r["key"] == "field:" + cid for r in saved["latest_turn"]["unaccepted"])


@pytest.mark.anyio
async def test_identity_confirmation_is_not_inferred_from_seven_explicit_values(
    api, provider, monkeypatch,
):
    session, data, _ = await ready(api, monkeypatch)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        data = state["global_compilation"]
        for f in data["audit"]["fields"]:
            if f["candidate_id"].startswith(("p0.", "p1.")):
                f["conditions"] = ["identity"]
        data["audit"]["conditions"]["identity"] = {"result": "unknown",
            "form_evidence": {"paragraph_id": "paragraph:0", "quote": "Il sottoscritto"},
            "reason": "Identità da confermare"}
        session = sessions.save_state(db, row, state, "test_open_identity")
    # Keep the synthetic condition during revalidation; actual recovery is exercised separately.
    monkeypatch.setattr(adapter, "refreshed_audit", lambda db, row, state:
                        deepcopy(state["global_compilation"]["audit"]))
    decision, _ = await routed(session, monkeypatch)
    after, _ = apply(session, decision, REAL_QUOTE)
    saved = after["global_compilation"]["dialogue"]
    assert len(saved["user_values"]) == 7
    assert "condition:identity" not in saved["answers"]
    notice = dialogue.continuation_receipt(saved)
    assert "Risposte conservate" in notice and "Ho registrato" not in notice
    assert all(r["usable_for_draft"] is False for r in saved["latest_turn"]["accepted"])
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", after["id"], after["version"])
        state["global_compilation"]["dialogue"]["phase"] = "READY"
        after = sessions.save_state(db, row, state, "test_still_blocked")
    assert dialogue.export_selection(after)[2] == []


def extraction_case(doc):
    from test_compilation_signatory_layouts import prepare

    from app.compilation_user_extraction import frames

    data, _, _ = prepare(doc)
    data.update(user_extraction_revision=1, user_context=[])
    slot = next(q for q in dialogue.question_pool(data) if q["kind"] == "value")
    slot.update(slot=1, question="Dati del sottoscrittore?")
    return frames(data, [slot])["1"]


@pytest.mark.parametrize("shape", ["inline", "rows", "paragraphs", "contact"])
def test_different_form_and_person_keep_property_ownership(shape):
    from app.compilation_user_extraction import extract

    labels = ["La firmataria", "Luogo di nascita", "Provincia di nascita", "Data di nascita",
              "Comune di residenza", "Provincia di residenza", "Indirizzo di residenza",
              "Codice fiscale personale"]
    doc = Document()
    if shape == "contact":
        labels[0] = "Nome e cognome del referente"
    if shape == "inline":
        doc.add_paragraph("La firmataria ________, nata a ________ (____) il ________, "
                          "residente a ________ (____), indirizzo di residenza ________, "
                          "codice fiscale ________")
    elif shape in {"rows", "contact"}:
        table = doc.add_table(rows=0, cols=2)
        for label in labels:
            table.add_row().cells[0].text = label
    else:
        for label in labels:
            doc.add_paragraph(label + ": ________")
    doc.add_paragraph("Direttore tecnico ________ nato a ________")
    if shape == "contact":
        from test_compilation_signatory_layouts import prepare

        from app.compilation_user_extraction import frames

        data, _, _ = prepare(doc)
        data.update(user_extraction_revision=1, user_context=[])
        frame = frames(data, [{"slot": 1, "key": "field:t0.r0.c1", "kind": "value",
                               "field_ids": ["t0.r0.c1"]}])["1"]
    else:
        frame = extraction_case(doc)
    quote = ("La firmataria è Ada Neri, nata a Torino (TO) il 12/01/1985, "
             "residente a Milano (MI), via Roma 24, codice fiscale: NREADA85A52L219R.")
    result = extract(frame, quote)
    got = {frame["members"][cid]["property"]: v["value"] for cid, v in result["values"].items()}
    assert got == {"name": "Ada Neri", "birth": "Torino", "birth_province": "TO",
        "date": "12/01/1985", "residence": "Milano", "residence_province": "MI",
        "address": "via Roma 24", "cf": "NREADA85A52L219R"}
    assert not result["issues"]
    assert all(v["value"] in v["user_quote"] for v in result["values"].values())


@pytest.mark.parametrize("text,expected", [
    ("Ada Neri, nata a Torino oppure Roma il 12/01/1985", {"name", "date"}),
    ("Ada Neri, nata a Torino (TO) il 31/02/1985", {"name", "birth", "birth_province"}),
    ("Ada Neri oppure Bea Mori, nata a Torino", set()),
    ("Forse Ada Neri, nata a Torino", set()),
    ("Ada Neri, il direttore tecnico è Bea Mori, nata a Torino", {"name"}),
])
def test_ambiguous_parts_are_preserved_but_not_distributed(text, expected):
    from app.compilation_user_extraction import extract

    frame = extraction_case(document())
    result = extract(frame, text)
    assert {frame["members"][cid]["property"] for cid in result["values"]} == expected
    assert result["issues"]


@pytest.mark.anyio
async def test_refused_extra_can_be_clarified_later_without_losing_its_target(
    api, provider, monkeypatch,
):
    session, _, _ = await ready(api, monkeypatch)
    decision, _ = await routed(session, monkeypatch, refuse=["p0.s3"])
    session, _ = apply(session, decision, REAL_QUOTE)
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
        data = state["global_compilation"]
        slot = next(q for q in dialogue.question_pool(data) if q["key"] == "field:p0.s3")
        slot.update(slot=1, question="Qual è la data di nascita?")
        data["dialogue"].update(phase="READY", question={
            "kind": "clarifications", "message": slot["question"], "slots": [slot],
            "field_ids": []})
        session = sessions.save_state(db, row, state, "test_followup_date")
    reply = ClarificationReply(slot=1, action="VALUE", value="14/11/1982", user_quote="14/11/1982")
    proof = scope.proof(scope.target(data, slot["key"], slot["field_ids"]), reply)
    after, errors = dialogue.apply_replies("alpha", session["id"], session["version"],
        [reply], reply.user_quote, scope_verifications={1: proof})
    assert not errors
    assert not after["global_compilation"]["dialogue"]["extraction_pending"]
    with connection() as db:
        row, state = adapter._row_state(db, "alpha", after["id"], after["version"])
        from app.compilation_session_models import GlobalDraftRequest

        checked = dialogue.checked_user_fields(row, state, GlobalDraftRequest(
            version=after["version"], user_candidate_ids=["p0.s3"], allow_unresolved=True,
            user_quote="Genera"))
    assert checked[0][1]["written_value"] == "14/11/1982"


@pytest.mark.anyio
async def test_ambiguous_user_property_is_not_silently_replaced_by_source(
    api, provider, monkeypatch,
):
    from test_compilation_selected_person import PROFILE
    from test_compilation_sessions import source

    await source(api, PROFILE, name="persone.md")
    session, _, _ = await ready(api, monkeypatch)
    quote = "Ada Neri, nata a Torino oppure Roma il 12/01/1985"
    decision, _ = await routed(session, monkeypatch, quote=quote, value=quote)
    after, _ = apply(session, decision, quote)
    saved = after["global_compilation"]["dialogue"]
    assert saved["user_values"]["p0.s0"]["value"] == "Ada Neri"
    assert "p0.s1" in saved["extraction_pending"]
    assert "p0.s1" not in saved["user_values"]
    denied = await api.post(f"{BASE}/{after['id']}/global-draft", json={
        "version": after["version"], "candidate_ids": ["p0.s1"], "allow_unresolved": True,
        "user_quote": "Genera"})
    assert denied.status_code == 409 and "risposta USER" in denied.text


def test_the_new_revision_does_not_upgrade_old_sessions(monkeypatch):
    from app.compilation_profile import new_session_flags
    from app.compilation_user_extraction import enabled, frames

    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30-r2")
    assert new_session_flags()["user_extraction_revision"] == 1
    assert not enabled({"compilation_profile": "sezioni-2026-10-30-r2"})
    assert frames({}, []) == {}
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-30")
    assert "user_extraction_revision" not in new_session_flags()
