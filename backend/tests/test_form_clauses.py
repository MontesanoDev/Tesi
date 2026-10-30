"""Conditions, questions and answers bound to identifiable FORM clauses (30 Oct).

E2E Trapani, real runs on 381ed63/cd47147/f0c48ba: under «IN QUALITA' DI» the FORM lists the
alternatives «(eliminare le opzioni non pertinenti)». In 4 runs of 11 the model anchored the
company-data condition on that instruction: the question showed «(eliminare le opzioni non
pertinenti)», the simulated USER could not relate it to a choice and deferred it, and 8 values
were lost; in the other runs the same condition was anchored on «Legale rappresentante di
Società di Ingegneria» and confirmed. Synthetic FORM, simulated provider.
"""

import json

import pytest
from docx import Document
from test_compilation_catalog import encoded, native_checkbox
from test_compilation_global_sessions import api, provider
from test_compilation_resilient_segments import Model, analyze, envelope, slot, started, state_of

from app.compilation_catalog import build_compilation_catalog
from app.compilation_form_clauses import apply, clauses, prune_lists
from app.compilation_global_dialogue import DialoguePlan, question_pool, render_dialogue
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]
ENGINEERING = "Legale rappresentante di Società di Ingegneria"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def form(box=False):
    doc = Document()
    doc.add_paragraph("Dato iniziale: ____________")
    doc.add_paragraph().add_run("IN QUALITÀ DI").bold = True
    doc.add_paragraph().add_run("(eliminare le opzioni non pertinenti)").bold = True
    doc.add_paragraph("Professionista singolo con studio in ____________")
    doc.add_paragraph("")
    doc.add_paragraph(f"{ENGINEERING} ____________ con sede in ____________")
    if box:
        native_checkbox(doc.add_paragraph(), legacy=False)
    doc.add_paragraph("")
    doc.add_paragraph("Prestatore di servizi stabilito in altri Stati membri")
    doc.add_paragraph("____________ con sede in ____________")
    doc.add_paragraph().add_run("DICHIARA").bold = True
    doc.add_paragraph("Dato finale: ____________")
    return encoded(doc)


def paragraph_id(inp, text):
    return next(p["id"] for b in inp["form"]["blocks"] for p in b["paragraphs"]
                if p["text"].startswith(text))


def answer(anchor, quote):
    """One model condition over the data of every alternative, anchored on `anchor`."""
    def outcome(inp, ids):
        listed = [c for c in ids if inp["form"]["candidates"][c]["type"] == "text"]
        first, last = listed[0], listed[-1]
        governed = listed[1:-1]
        condition = {"form": {"paragraph_id": paragraph_id(inp, anchor), "quote": quote},
                     "aspect": "participation", "operator": "semantic", "fact_ids": [],
                     "reason": "Qualità del partecipante da confermare",
                     "scope": [{"kind": "candidate", "id": c} for c in governed]}
        fields = {c: slot(inp, c, conditions=["k"]) for c in governed}
        fields.update({c: slot(inp, c) for c in (first, last)})
        return json.dumps(envelope(inp, fields, conditions={"k": condition}))
    return outcome


async def analyzed(api, monkeypatch, anchor, quote):
    model = Model({1: [answer(anchor, quote)]})
    session = (await analyze(api, await started(api, monkeypatch, form(), model))).json()
    return state_of(session)["global_compilation"]


def applicability(data):
    return {q["condition"]: sorted(q["field_ids"]) for q in question_pool(data)
            if q["kind"] == "applicability"}


def test_the_alternatives_of_a_pruned_list_are_clauses_with_their_own_data():
    catalog = build_compilation_catalog(inspect_docx(form()))
    [listing] = prune_lists(catalog)
    assert [m["label"] for m in listing["members"]] == [
        "Professionista singolo con studio in", ENGINEERING,
        "Prestatore di servizi stabilito in altri Stati membri"]
    assert [len(m["candidate_ids"]) for m in listing["members"]] == [1, 2, 2]
    assert len(listing["header_ids"]) == 2  # The instruction and the bold heading before it.
    assert {c["kind"] for c in clauses(catalog).values()} == {"alternative"}


@pytest.mark.anyio
async def test_a_condition_on_the_instruction_becomes_one_question_per_alternative(
    api, provider, monkeypatch,
):
    data = await analyzed(api, monkeypatch, "(eliminare", "(eliminare le opzioni non pertinenti)")
    questions = applicability(data)
    # One question per alternative with valid data (the single professional's value is
    # rejected by the validator: a company fact for a person field, so nothing to confirm).
    assert questions == {ENGINEERING: ["p5.s0", "p5.s1"],
                         "Prestatore di servizi stabilito in altri Stati membri": ["p8.s1"]}
    split = data["audit"]["form_clauses"]["split"]["k"]
    assert list(split.values()) == [["p3.s0"], ["p5.s0", "p5.s1"], ["p8.s0", "p8.s1"]]
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    for key, ids in split.items():
        # Same restriction, renamed (a field rejected by the validator has no conditions).
        assert all(fields[c]["conditions"] == [key] for c in ids if fields[c]["conditions"])
    assert data["audit"]["conditions"]["k"]["applies_to"] == []


@pytest.mark.anyio
async def test_the_same_clause_gives_the_same_question_whatever_the_model_anchored(
    api, provider, monkeypatch,
):
    on_instruction = await analyzed(api, monkeypatch, "(eliminare",
                                    "(eliminare le opzioni non pertinenti)")
    pool = [q for q in question_pool(on_instruction) if q["condition"] == ENGINEERING]
    plan = DialoguePlan(message="Riepilogo dei punti aperti.", questions=[
        {"slot": pool[0]["slot"], "confirmation": "la domanda è presentata da una società"}])
    [rendered] = render_dialogue(plan, pool)["question"]["slots"]
    assert rendered["question"].startswith(
        f"Confermi che si applica al vostro caso quanto indicato nel modulo: «{ENGINEERING}»")
    assert rendered["form_clause"]["kind"] == "alternative"


@pytest.mark.anyio
async def test_a_split_part_and_a_model_condition_on_the_same_clause_are_one_question(
    api, provider, monkeypatch,
):
    def both(inp, ids):
        payload = json.loads(answer("(eliminare", "(eliminare le opzioni non pertinenti)")(
            inp, ids))
        engineering = [c for c in ids if paragraph_id(inp, ENGINEERING) == inp["form"][
            "candidates"][c]["context_id"]]
        payload["conditions"]["k2"] = {**payload["conditions"]["k"], "form": {
            "paragraph_id": paragraph_id(inp, ENGINEERING), "quote": "Società di Ingegneria"},
            "scope": [{"kind": "candidate", "id": c} for c in engineering]}
        return json.dumps(payload)

    model = Model({1: [both]})
    session = (await analyze(api, await started(api, monkeypatch, form(), model))).json()
    data = state_of(session)["global_compilation"]
    [question] = [q for q in question_pool(data) if q["condition"] == ENGINEERING]
    assert sorted(question["condition_ids"]) == ["k2", "k__5"]


@pytest.mark.anyio
async def test_a_condition_on_the_alternative_itself_shows_its_label(api, provider, monkeypatch):
    data = await analyzed(api, monkeypatch, ENGINEERING, "Società di Ingegneria")
    questions = applicability(data)
    assert list(questions) == [ENGINEERING]  # Not the fragment «Società di Ingegneria».
    assert not data["audit"]["form_clauses"]["split"]


def test_a_checkbox_is_never_turned_into_an_applicability_confirmation():
    catalog = build_compilation_catalog(inspect_docx(form(box=True)))
    [listing] = prune_lists(catalog)
    box = next(c for c, x in catalog["candidates"].items() if x["type"] == "checkbox")
    member = next(m for m in listing["members"] if box in m["candidate_ids"])
    data = [c for c in member["candidate_ids"] if c != box]
    instruction = listing["header_ids"][-1]
    audit = {"fields": [{"candidate_id": c, "conditions": ["k"]} for c in [*data, box]],
             "conditions": {"k": {"form_evidence": {"paragraph_id": instruction, "quote": "x"},
                                  "applies_to": [*data, box], "operator": "semantic"}}}
    apply(audit, catalog)
    assert audit["conditions"]["k"]["applies_to"] == [box]
    assert next(f for f in audit["fields"] if f["candidate_id"] == box)["conditions"] == ["k"]


@pytest.mark.anyio
async def test_the_previous_profile_keeps_the_model_anchor(api, provider, monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "sezioni-2026-10-25")
    data = await analyzed(api, monkeypatch, "(eliminare", "(eliminare le opzioni non pertinenti)")
    assert "form_clauses" not in data["audit"]
    assert list(applicability(data)) == ["(eliminare le opzioni non pertinenti)"]
