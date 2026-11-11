"""Software tests only. No real provider or inference of initial USER decisions."""

import json
import sqlite3
from types import SimpleNamespace

import pytest
from test_compilation_global_sessions import api as global_api
from test_compilation_global_sessions import provider as simulated_provider
from test_compilation_global_sessions import resolve, start

from app.compilation_global import TASK, build_global_input, global_request
from app.compilation_user_context import registered_user_context
from app.db import connection
from app.docx_templates import inspect_docx
from app.repository import save_conversation_turn

api = global_api
provider = simulated_provider


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def receipts():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE conversations(id TEXT, project_id TEXT);
        CREATE TABLE conversation_turns(id INTEGER PRIMARY KEY, conversation_id TEXT,
            question TEXT, answer TEXT, compilation_json TEXT);
        INSERT INTO conversations VALUES('ca','alpha'),('cb','beta');
    """)
    row = {"id": "session-a", "project_id": "alpha", "form_id": 1,
           "conversation_id": "ca"}
    state = {"engine": "global", "global_compilation": {}}

    def add(question, *, conversation="ca", session="session-a", action="start", raw=None):
        db.execute("INSERT INTO conversation_turns(conversation_id,question,answer,"
                   "compilation_json) VALUES(?,?,?,?)", (conversation, question,
                   "AI: il firmatario è Inventato", raw if raw is not None else
                   json.dumps({"session_id": session, "action": action})))

    yield db, row, state, add
    db.close()


def test_no_registered_request_does_not_create_user_context(receipts):
    db, row, state, _ = receipts
    assert registered_user_context(db, row, state) == []


@pytest.mark.parametrize("message", [
    "Compila il modulo.",
    "Per questa domanda il firmatario è Leonardo Montemurro.",
    "Non ho ancora scelto chi firma; non partecipiamo come società di ingegneria.",
    "Potrebbe firmare Leonardo oppure Elisa, devo decidere.",
])
def test_start_text_is_only_a_literal_utterance(receipts, message):
    db, row, state, add = receipts
    add(message)
    records = registered_user_context(db, row, state)
    assert records == [{"kind": "recorded_request", "provenance": "USER",
                        "turn_id": 1, "user_quote": message}]
    assert state == {"engine": "global", "global_compilation": {}}


@pytest.mark.parametrize("change", ["project", "session", "action", "invalid", "null"])
def test_other_projects_sessions_and_ordinary_turns_are_excluded(receipts, change):
    db, row, state, add = receipts
    kwargs = {"conversation": "cb"} if change == "project" else {
        "session": "other-session"} if change == "session" else {
        "action": "updated"} if change == "action" else {
        "raw": "not-json"} if change == "invalid" else {"raw": "null"}
    add("Fatto da non importare", **kwargs)
    assert registered_user_context(db, row, state) == []


def test_contradictory_registered_requests_preserve_order_without_deciding(receipts):
    db, row, state, add = receipts
    add("Firma Leonardo.")
    add("Rettifico: il firmatario è da decidere.")
    assert [r["user_quote"] for r in registered_user_context(db, row, state)] == [
        "Firma Leonardo.", "Rettifico: il firmatario è da decidere."]


def test_only_accepted_scoped_decisions_are_forwarded(receipts):
    db, row, state, _ = receipts
    state["global_compilation"] = {
        "audit": {"conditions": {"c": {"validation": "GROUNDED_PROPOSAL"}},
                  "fields": [{"candidate_id": "p1.s0"}],
                  "choice_groups": {"g": {"validation": "GROUNDED_GROUP"}}},
        "dialogue": {"answers": {
            "condition:c": {"action": "CONDITION_FALSE", "applies": False,
                            "user_quote": "Questo ramo non si applica", "provenance": "USER"},
            "field:p1.s0": {"action": "VALUE", "value": "Bari", "user_quote": "Bari",
                            "provenance": "USER"},
            "choice:g": {"action": "VALUE", "value": "Seconda opzione", "selected_options": [2],
                         "user_quote": "Seconda opzione", "provenance": "USER"},
        }, "user_values": {"p1.s0": {"value": "Bari", "user_quote": "Bari",
                                       "provenance": "USER"}}},
    }
    records = registered_user_context(db, row, state)
    assert len(records) == 3
    assert all(r["kind"] == "registered_decision" for r in records)
    assert records[0]["applies"] is False
    assert records[2]["selected_options"] == [2]


@pytest.mark.parametrize("failure", ["not_user", "skip", "unknown_scope", "wrong_boolean",
                                     "rejected_condition", "wrong_value_quote", "no_quote"])
def test_rejected_or_unscoped_decisions_are_not_forwarded(receipts, failure):
    db, row, state, _ = receipts
    answer = {"action": "CONDITION_TRUE", "applies": True, "user_quote": "Confermo",
              "provenance": "USER"}
    state["global_compilation"] = {"audit": {"conditions": {
        "c": {"validation": "GROUNDED_PROPOSAL"}}}, "dialogue": {"answers": {
            "condition:c": answer}}}
    if failure == "not_user":
        answer["provenance"] = "MODEL"
    elif failure == "skip":
        answer["action"] = "SKIP"
    elif failure == "unknown_scope":
        state["global_compilation"]["audit"]["conditions"] = {}
    elif failure == "wrong_boolean":
        answer["applies"] = False
    elif failure == "rejected_condition":
        state["global_compilation"]["audit"]["conditions"]["c"]["validation"] = "REJECTED"
    elif failure == "wrong_value_quote":
        answer.update(action="VALUE", value="Bari")
        data = state["global_compilation"]
        data["audit"]["fields"] = [{"candidate_id": "p1.s0"}]
        data["dialogue"]["answers"] = {"field:p1.s0": answer}
        data["dialogue"]["user_values"] = {"p1.s0": {
            "value": "Bari", "user_quote": "altra frase", "provenance": "USER"}}
    elif failure == "no_quote":
        answer["user_quote"] = ""
    assert registered_user_context(db, row, state) == []


@pytest.mark.anyio
async def test_persisted_chat_request_reaches_actual_global_request(api, provider):
    session = await start(api)
    message = "Compila questa domanda. Il firmatario non è ancora stato scelto."
    turn = save_conversation_turn(session["conversation_id"], {
        "question": message, "answer": "Non usare il contenuto AI come prova",
        "generation_status": "direct",
        "compilation": {"session_id": session["id"], "action": "start"},
    })
    await resolve(api, session)
    sent = provider[0]
    assert sent["user_context"] == [{"kind": "recorded_request", "provenance": "USER",
                                    "turn_id": turn, "user_quote": message}]
    assert sent["user_values"] == []
    assert all(s["role"] == "source" for s in sent["sources"])
    assert all("contenuto AI" not in s["content"] for s in sent["sources"])
    body = global_request(SimpleNamespace(model="simulated"), sent)
    assert "Non ci sono valori USER." not in body["messages"][0]["content"]
    assert "CONTESTO USER REGISTRATO" in body["messages"][0]["content"]


@pytest.mark.anyio
@pytest.mark.parametrize("legacy", [True, False])
async def test_no_user_benchmark_input_and_prompt_remain_exact(
    api, provider, monkeypatch, legacy,
):
    if not legacy:
        monkeypatch.setenv("MAPI_DIALOGUE_REVISION", "1")  # P3 is opt-in.
    session = await start(api)
    if legacy:
        from app import compilation_global_sessions as adapter
        from app import compilation_sessions as sessions

        with connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row, state = adapter._row_state(db, "alpha", session["id"], session["version"])
            state["global_compilation"].pop("dialogue_revision", None)
            session = sessions.save_state(db, row, state, "test_previous_revision")
    await resolve(api, session)
    assert "user_context" not in provider[0]
    assert provider[0]["user_values"] == []
    prompt = global_request(SimpleNamespace(model="simulated"), provider[0])[
        "messages"][0]["content"]
    if legacy:
        assert "reference_date" not in provider[0] and prompt == TASK
    else:
        # P3: the only change is the current date, declared as context, never SOURCE.
        assert provider[0]["reference_date"] and prompt.startswith(TASK)
        assert prompt[len(TASK):].strip().startswith("DATA DI RIFERIMENTO.")


@pytest.mark.anyio
async def test_user_context_changes_no_form_sources_schema_or_reading_plan(api, provider):
    session = await start(api)
    from app import compilation_global_sessions as adapter
    from app import compilation_sessions as sessions

    with connection() as db:
        row = sessions._row(db, "alpha", session["id"])
        layout = inspect_docx(bytes(row["original"]), require_candidates=False)
        sources = adapter.load_document_corpus(db, "alpha")
    before = build_global_input(layout, "alpha", sources)
    context = [{"kind": "recorded_request", "provenance": "USER", "turn_id": 1,
                "user_quote": "Firma Leonardo; usa solo prove SOURCE per i dati."}]
    after = build_global_input(layout, "alpha", sources, user_context=context)
    assert {k: v for k, v in after.items() if k != "user_context"} == before
    context[0]["user_quote"] = "mutazione del chiamante"
    assert after["user_context"][0]["user_quote"].startswith("Firma Leonardo")
    assert after["user_values"] == []
