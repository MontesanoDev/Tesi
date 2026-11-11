"""A clarification on a named FORM slot is accepted, or the refusal says what blocks it.

Real Minervino session (65c252e8, turns 18-19): a value on one destination, governed by a
condition the USER had already confirmed, was refused twice with the same «Puoi precisare?».
The router had bound the right destination; the guard verdict was SUPPORTED with an AMBIGUOUS
scope, read from the list of the other fields of that condition, and its contract never said
what user_conditions are. The simulated guard answers as the real one did under each contract.
"""

import json
import re
from copy import deepcopy
from io import BytesIO

import pytest
from docx import Document
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_sessions import source

from app import compilation_chat as chat
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_reply_guard as guard
from app import compilation_sessions as sessions
from app import intents
from app.compilation_conversation import targets
from app.compilation_scope_review import session_data
from app.config import use_ai_settings

__all__ = ["api", "provider"]

CLAUSE = "Il sottoscritto partecipa come società di ingegneria"
LINE = ("Camera di Commercio di ____________ al n. ____________ / all'albo professionale della "
        "Provincia di ____________ al n. ____________")
SOURCE = "Denominazione: Aurora S.r.l.\nCodice sede: 01234560981\nCodice pratica: BA-654321"
NUMBER = "Numero iscrizione Camera di Commercio"
NAMED = ("Mi riferisco al campo «al n.» subito dopo «Camera di Commercio di»: è il numero del "
         "Registro Imprese, il valore è 01234560981.")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def analysis(inp):
    paragraphs = [p for b in inp["form"]["blocks"] for p in b["paragraphs"]]
    clause = next(p for p in paragraphs if p["text"].startswith("Il sottoscritto"))
    name_p = next(p for p in paragraphs if p["text"].startswith("Denominazione"))
    line = next(p for p in paragraphs if p["text"].startswith("Camera"))
    name = re.search(r"\[\[(.+?)\]\]", name_p["text_with_fields"])[1]
    number = re.findall(r"\[\[(.+?)\]\]", line["text_with_fields"])[1]
    chunk = next(s["chunk_id"] for s in inp["sources"] if "BA-654321" in s["content"])

    def fact(prop, value, quote):
        return {"subject": "Aurora S.r.l.", "entity": "company", "aspect": "identity",
                "property": prop, "value": value,
                "evidence": [{"chunk_id": chunk, "quote": quote}]}

    def part(paragraph, cid):
        return next(p for p in re.split(r"(?<=\]\])", paragraph["text_with_fields"])
                    if f"[[{cid}]]" in p).strip()

    return {"version": 12, "uncertain_paragraph_ids": [], "bindings": {}, "choice_groups": {},
            "clarifications": {}, "coverage": [],
            "facts": {"f_name": fact("denominazione", "Aurora S.r.l.",
                                     "Denominazione: Aurora S.r.l."),
                      "f_reg": fact("numero_identificativo", "01234560981",
                                    "Codice sede: 01234560981"),
                      "f_rea": fact("numero_identificativo", "BA-654321",
                                    "Codice pratica: BA-654321")},
            "conditions": {"c": {
                "form": {"paragraph_id": clause["id"], "quote": clause["text"]},
                "aspect": "participation", "operator": "semantic", "fact_ids": [],
                "reason": "Partecipazione da confermare",
                "scope": [{"kind": "candidate", "id": name},
                          {"kind": "candidate", "id": number}]}},
            "fields": {
                name: {"label": "Denominazione", "kind": "data", "disposition": "conditional",
                       "conditions": ["c"], "fact_id": "f_name", "property": "denominazione",
                       "reason": "Da confermare",
                       "form": {"paragraph_id": name_p["id"], "quote": part(name_p, name)}},
                number: {"label": NUMBER, "kind": "data", "disposition": "review",
                         "conditions": ["c"], "property": "numero_identificativo",
                         "reason": "Il modulo non distingue gli identificativi",
                         "review_kind": "ambiguous", "alternative_fact_ids": ["f_rea", "f_reg"],
                         "form": {"paragraph_id": line["id"], "quote": part(line, number)}}}}


async def analyzed(api, monkeypatch):
    doc = Document()
    doc.add_paragraph(CLAUSE)
    doc.add_paragraph("Denominazione ____________")
    doc.add_paragraph(LINE)
    stream = BytesIO()
    doc.save(stream)
    form = (await api.post("/api/projects/alpha/forms",
                           files={"file": ("modulo.docx", stream.getvalue())})).json()
    await source(api, SOURCE, name="societa.md")

    async def model(client, settings, body, timeout, **kwargs):
        return json.dumps(analysis(json.loads(body["messages"][1]["content"]))), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", model)
    return await resolve(api, (await api.post(BASE, json={
        "form_id": form["id"], "engine": "global", "start_in_chat": True})).json())


def verdicts(body, *, identified, fixed=None):
    """The real guard: without a contract the condition's other fields read as a missing scope."""
    if fixed:
        return {"checks": [{"slot": p["slot"], "result": fixed[0], "scope_result": fixed[1]}
                           for p in json.loads(body["messages"][1]["content"])["proposals"]]}
    system, context = body["messages"][0]["content"], json.loads(body["messages"][1]["content"])
    checks = []
    for proposal in context["proposals"]:
        target = context["form_scope"]["slots"][str(proposal["slot"])]
        confirmed = all(target["user_conditions"].get(c, {}).get("applies") is True
                        for c in target["conditions"])
        value = proposal["action"] == "VALUE"
        scope = ("AMBIGUOUS" if value and not (
            "user_conditions" in system and confirmed and identified
            and len(target["destinations"]) == 1) else "SUPPORTED")
        checks.append({"slot": proposal["slot"], "result": "SUPPORTED", "scope_result": scope})
    return {"checks": checks}


async def route(session, monkeypatch, message, plan, history=(), identified=True, fixed=None):
    calls = []

    async def model(client, settings, body, timeout, **kwargs):
        if kwargs["response_schema"]["title"] == "FormScopeChecks":
            calls.append(body)
            return json.dumps(verdicts(body, identified=identified, fixed=fixed)), "simulated", {}
        return json.dumps({"answer": "", "queries": [], "target": "form", **plan}), "simulated", {}

    monkeypatch.setattr(intents, "request_model_content", model)
    with use_ai_settings(adapter.get_ai_settings()):
        routed = await intents.plan_chat_turn(message, list(history),
                                              compilation=chat.planner_context(session))
    if isinstance(routed.decision, chat.ClarificationDecision):
        await chat.handle_group_decision("alpha", None, routed.decision, session, message)
    return sessions.get_session("alpha", session["id"]), calls, routed


def number_edit(session, quote=NAMED):
    number = next(q for q in targets(session_data(session)) if q["label"] == NUMBER)
    return number["field_ids"][0], {"intent": "edit_fields", "edits": [{
        "target": number["target"], "action": "VALUE", "value": "01234560981",
        "user_quote": quote}]}


async def confirmed(api, monkeypatch):
    s = await analyzed(api, monkeypatch)
    question = chat.planner_context(s)["question"]["slots"]
    slot = next(q["slot"] for q in question if q["kind"] == "applicability")
    message = "Sì, confermo che partecipiamo come società di ingegneria."
    s, _, _ = await route(s, monkeypatch, message, {"intent": "answer_fields", "replies": [
        {"slot": slot, "action": "CONDITION_TRUE", "user_quote": message}]})
    return await resolve(api, s)


async def draft(api, s):
    ids, conditions, users = dialogue.export_selection(s)
    response = await api.post(f"{BASE}/{s['id']}/global-draft", json={
        "version": s["version"], "candidate_ids": ids, "confirmed_condition_ids": conditions,
        "user_candidate_ids": users, "allow_unresolved": True, "user_quote": "Fammi la bozza"})
    assert response.status_code == 200, response.text
    return response.json()


def values(s):
    return s["global_compilation"]["dialogue"].get("user_values") or {}


def text_of(data):
    return "\n".join(p.text for p in Document(BytesIO(data)).paragraphs)


@pytest.mark.anyio
async def test_a_clarification_naming_the_slot_is_accepted_after_the_condition_was_confirmed(
    api, provider, monkeypatch,
):
    s = await confirmed(api, monkeypatch)
    s = await draft(api, s)  # The real dialogue: a first draft, the number still empty.
    url = s["last_generation"]["downloads"]["docx"]
    first = (await api.get(url)).content
    assert "01234560981" not in text_of(first)
    cid, plan = number_edit(s)
    s, calls, routed = await route(s, monkeypatch, NAMED, plan)
    # The guard received one destination and the confirmation already on record.
    target = next(iter(json.loads(calls[0]["messages"][1]["content"])["form_scope"][
        "slots"].values()))
    assert [d["candidate_id"] for d in target["destinations"]] == [cid]
    assert target["user_conditions"]["c"]["applies"] is True
    assert isinstance(routed.decision, chat.ClarificationDecision)
    assert values(s)[cid]["value"] == "01234560981" and set(values(s)) == {cid}
    assert values(s)[cid]["provenance"] == "USER"
    s = await draft(api, await resolve(api, s))
    second = (await api.get(s["last_generation"]["downloads"]["docx"])).content
    assert "01234560981" in text_of(second) and "BA-654321" not in text_of(second)
    assert (await api.get(url)).content == first  # The previous draft is preserved.


@pytest.mark.anyio
async def test_a_really_ambiguous_destination_is_refused_and_not_asked_again(
    api, provider, monkeypatch,
):
    s = await confirmed(api, monkeypatch)
    before, version = deepcopy(s["global_compilation"]["dialogue"]), s["version"]
    vague = "Metti pure quel numero lì, tanto è uno dei due."  # Real verdict: AMBIGUOUS twice.
    _, plan = number_edit(s, vague)
    both = ("AMBIGUOUS", "AMBIGUOUS")
    s, _, routed = await route(s, monkeypatch, vague, plan, fixed=both)
    first = routed.decision.answer
    assert first.startswith(f"Non ho usato la risposta su «{NUMBER}»")
    assert first.count("Puoi precisare soltanto") == 1
    s, _, routed = await route(s, monkeypatch, vague, plan,
                               [{"question": vague, "answer": first}], fixed=both)
    second = routed.decision.answer
    assert second != first and "Puoi precisare" not in second
    assert "ripeterla non cambia l'esito" in second and "Nulla è stato modificato" in second
    assert "non indica con certezza" in second
    # Refused twice: no value, no receipt, the same session revision.
    assert s["version"] == version and s["global_compilation"]["dialogue"] == before
    assert not values(s)
    s, _, routed = await route(s, monkeypatch, vague, plan, [
        {"question": vague, "answer": second}], fixed=both)
    assert "Puoi precisare" not in routed.decision.answer and s["version"] == version


@pytest.mark.anyio
async def test_a_scope_refusal_on_a_confirmed_condition_names_the_field_when_repeated(
    api, provider, monkeypatch,
):
    """The verdict the real session received, if the model still returned it: no loop."""
    s = await confirmed(api, monkeypatch)
    version = s["version"]
    _, plan = number_edit(s)
    s, _, routed = await route(s, monkeypatch, NAMED, plan, identified=False)
    first = routed.decision.answer
    assert "a quali campi del modulo si applica" in first
    s, _, routed = await route(s, monkeypatch, NAMED, plan,
                               [{"question": NAMED, "answer": first}], identified=False)
    second = routed.decision.answer
    assert "il controllo non accetta che il messaggio riguardi proprio il campo «al n" in second
    assert "Puoi precisare" not in second and "manca prima la conferma" not in second
    assert not values(s) and s["version"] == version


@pytest.mark.anyio
async def test_a_value_on_an_unconfirmed_condition_stays_refused_and_names_the_clause(
    api, provider, monkeypatch,
):
    s = await analyzed(api, monkeypatch)
    version = s["version"]
    _, plan = number_edit(s)
    s, calls, routed = await route(s, monkeypatch, NAMED, plan)
    target = next(iter(json.loads(calls[0]["messages"][1]["content"])["form_scope"][
        "slots"].values()))
    assert target["user_conditions"]["c"] == {}
    s, _, routed = await route(s, monkeypatch, NAMED, plan, [
        {"question": NAMED, "answer": routed.decision.answer}])
    assert f"manca prima la conferma di «{CLAUSE}»" in routed.decision.answer
    assert "confermare prima quella clausola" in routed.decision.answer
    assert not values(s) and s["version"] == version


def test_the_guard_contract_says_a_confirmation_counts_and_a_bare_value_does_not():
    contract = " ".join(guard.FORM_SCOPE_TASK.split())
    assert "applies=true è un'indicazione USER esplicita" in contract
    assert "assente da user_conditions resta non confermata" in contract
    assert "Il solo valore non identifica una destinazione" in contract
    assert "«Il numero è 123» ha scope_result AMBIGUOUS" in contract
    assert "SUPPORTED richiede che UNA STESSA proposizione" in contract  # Condition rule kept.
