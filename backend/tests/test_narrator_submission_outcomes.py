"""A rejected router destination is not a refused USER value or a new USER decision."""

import pytest
from docx import Document
from test_compilation_global_sessions import api, provider, resolve
from test_compilation_incremental_conversation import conversational

from app import compilation_conversation as conversation
from app import compilation_global_dialogue as dialogue
from app import compilation_sessions as sessions
from app import main
from app.compilation_chat import ClarificationDecision, ClarificationReply
from app.compilation_scope_review import proof, session_data, target
from app.intents import PlannedTurn

__all__ = ["api", "provider"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_unrelated_router_guess_does_not_reask_or_close_an_unrequested_field(
    api, provider, monkeypatch,
):
    doc = Document()
    for title in ["Dati del sottoscrittore", "Altro referente"]:
        doc.add_paragraph(title)
        table = doc.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Il sottoscritto — Nome e cognome"
        table.cell(1, 0).text = "Codice fiscale personale"
    session = await conversational(api, monkeypatch, doc)
    keys = ["field:t0.r0.c1", "field:t1.r0.c1"]
    message = "Metti Giulia Ferri nel campo Il sottoscritto della prima sezione."
    for _ in range(2):
        data = session_data(session)
        q = next(q for q in conversation.targets(data) if q["key"] == keys[0])
        reply = ClarificationReply(slot=1, action="VALUE", value="Giulia Ferri", user_quote=message)
        checked = proof(target(data, q["key"], q["field_ids"]), reply)
        session, _ = dialogue.apply_replies("alpha", session["id"], session["version"],
            [reply], message, unaccepted_slots=[2], scope_verifications={1: checked},
            unaccepted_reasons={2: "UNRELATED"}, addressed_keys=keys)
        data = session_data(session)
        latest = data["dialogue"]["latest_turn"]
        assert not latest["unaccepted"]
        assert latest["discarded_proposals"][0]["key"] == keys[1]
        assert keys[1] not in data["dialogue"]["answers"]
        assert keys[1] not in data["dialogue"].get("unaccepted_attempts", {})
        assert latest["accepted"][0]["usable_for_draft"] is True
        receipt = dialogue.continuation_receipt(data["dialogue"])
        assert "Dati acquisiti per la bozza" in receipt
        assert "nulla è stato scritto" not in receipt and "Te la richiedo" not in receipt
        assert not any(q.get("retry") for q in dialogue.question_pool(data))
        session = await resolve(api, session)
    assert dialogue.export_selection(session)[2] == ["t0.r0.c1"]


@pytest.mark.anyio
@pytest.mark.parametrize("after_chat_commit", [False, True])
async def test_lost_response_after_actual_receipt_never_applies_user_decision_twice(
    api, provider, monkeypatch, after_chat_commit,
):
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Il sottoscritto — Nome e cognome"
    table.cell(1, 0).text = "Codice fiscale personale"
    s = await conversational(api, monkeypatch, doc)
    data = session_data(s)
    q = next(q for q in conversation.targets(data) if q["key"] == "field:t0.r0.c1")
    message = "Il sottoscritto è Giulia Ferri"
    reply = ClarificationReply(slot=1, action="VALUE", value="Giulia Ferri", user_quote=message)
    checked = proof(target(data, q["key"], q["field_ids"]), reply)
    calls = []

    async def plan(*args, **kwargs):
        calls.append(args)
        return PlannedTurn(ClarificationDecision(action="ANSWER", replies=[reply],
            scope_verifications={1: checked}, addressed_keys=[q["key"]]), "simulated", 0)

    monkeypatch.setattr(main, "plan_chat_turn", plan)
    save = main.save_conversation_turn

    def lost(*args):
        if after_chat_commit:
            save(*args)
        raise RuntimeError("simulated interruption after session commit")

    monkeypatch.setattr(main, "save_conversation_turn", lost)
    payload = {"question": message, "conversation_id": s["conversation_id"],
        "compilation_session_id": s["id"], "compilation_version": s["version"],
        "request_id": "actual-user-receipt"}
    with pytest.raises(RuntimeError):
        await api.post("/api/projects/alpha/answer", json=payload)
    first = sessions.get_session("alpha", s["id"])
    assert first["global_compilation"]["dialogue"]["user_values"]["t0.r0.c1"][
        "value"] == "Giulia Ferri"
    repeated = await api.post("/api/projects/alpha/answer", json=payload)
    assert repeated.status_code == (200 if after_chat_commit else 409)
    assert len(calls) == 1
    second = sessions.get_session("alpha", s["id"])
    assert second["version"] == first["version"]
    assert second["global_compilation"]["dialogue"] == first["global_compilation"]["dialogue"]
