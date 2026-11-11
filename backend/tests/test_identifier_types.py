"""REA, Register, VAT and tax codes are different data, not alternatives of one field.

Real Minervino run: the model gave a Register number and a REA number one property and marked
«al n.» ambiguous; the USER was asked to choose, then to transcribe, what the SOURCE labels.
"""

import json
import re
from io import BytesIO

import pytest
from docx import Document
from test_clarification_loop import draft, text_of, values
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_sessions import source

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_identifiers import destination_type, evidence_types
from app.compilation_identifiers import resolve as typed
from app.compilation_scope_review import session_data

__all__ = ["api", "provider"]

LINE = "Camera di Commercio di [[a]] al n. [[b]] / all'albo professionale di [[c]] al n. [[d]]"
TYPED = ("- **Numero REA:** BA-654321 (non è il numero di iscrizione al Registro delle Imprese).\n"
         "- **Numero di iscrizione al Registro delle Imprese, identificativo:** 01234560981.\n"
         "- Partita IVA: IT01234567890.\n- Codice fiscale e Partita IVA: 99887766554")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


@pytest.mark.parametrize("before, kind", [
    ("P.IVA ", "partita_iva"), (", C.F. ", "codice_fiscale"),
    ("codice fiscale n ", "codice_fiscale"), (", partita IVA n", "partita_iva"),
    ("REA n. ", "rea"), ("Registro Imprese n. ", "registro_imprese"),
    ("relativo Ordine Professionale con il n°", "albo"),
    # A label not right before the blank, or no label: the FORM does not say.
    (" / all'albo professionale della Provincia di ", None), ("Denominazione ", None),
    ("via ", None), ("tel. ", None), (" al n. ", None),
])
def test_the_form_type_is_the_label_right_before_the_destination(before, kind):
    assert destination_type({"id": "z", "context_id": "q", "slot_context": {"before": before}},
                            {}, {}) == kind


def test_a_bare_number_takes_the_nearest_institution_of_its_line():
    paragraphs = {"p": {"text_with_fields": LINE}}

    def kind(cid):
        return destination_type({"id": cid, "context_id": "p", "slot_context": {
            "before": " al n. "}}, paragraphs, {})

    assert kind("b") == "registro_imprese" and kind("d") == "albo"


@pytest.mark.parametrize("value, kinds", [
    ("BA-654321", {"rea"}), ("01234560981", {"registro_imprese"}),
    ("IT01234567890", {"partita_iva"}), ("99887766554", {"codice_fiscale", "partita_iva"}),
    ("012345", set()),  # A piece of another number is not that number.
])
def test_the_source_type_is_the_label_before_the_value(value, kinds):
    fact = {"value": value, "evidence": [{"chunk_id": 1, "quote": value}]}
    assert evidence_types(fact, {1: {"content": TYPED}}) == kinds


def test_a_company_tax_code_and_vat_number_can_be_the_same_figure():
    """Real compilazione-v1 line: measured against the gold, an early version lost this value."""
    line = "Codice fiscale operatore: 01234567897. Partita IVA: 01234567897."
    fact = {"value": "01234567897", "evidence": [{"chunk_id": 1,
                                                  "quote": "Partita IVA: 01234567897."}]}
    assert evidence_types(fact, {1: {"content": line}}) == {"codice_fiscale", "partita_iva"}
    field, report = resolved({"v": fact},
                             {"fact_id": "v", "conditions": [], "disposition": "value"},
                             line, before="Partita IVA ")
    assert field["fact_id"] == "v" and not report


def test_a_far_label_with_other_figures_in_between_does_not_type_the_value():
    content = "Partita IVA IT123 sede via Roma 10 protocollo 555"
    fact = {"value": "555", "evidence": [{"chunk_id": 1, "quote": "555"}]}
    assert evidence_types(fact, {1: {"content": content}}) == set()


def catalog(before=" al n. "):
    return {"blocks": [{"paragraphs": [{"id": "p", "text_with_fields": LINE}]}],
            "candidates": {"b": {"type": "text", "context_id": "p",
                                 "slot_context": {"before": before}}}}


def fact(value, quote, subject="Aurora S.r.l."):
    return {"subject": subject, "value": value, "property": "numero",
            "evidence": [{"chunk_id": 1, "quote": quote}]}


def resolved(facts, field, content=TYPED, before=" al n. "):
    raw = json.dumps({"facts": facts, "fields": {"b": field}})
    new, report = typed(raw, catalog(before), [{"chunk_id": 1, "content": content}])
    return json.loads(new)["fields"]["b"], report


FACTS = {"r": fact("BA-654321", "Numero REA"), "i": fact("01234560981", "Registro delle Imprese"),
         "v": fact("IT01234567890", "Partita IVA")}


def test_rea_register_and_vat_are_not_alternatives_of_the_register_number():
    field, report = resolved(FACTS, {"alternative_fact_ids": ["r", "i", "v"], "conditions": ["c"],
                                     "disposition": "review", "review_kind": "ambiguous"})
    assert field["fact_id"] == "i" and field["disposition"] == "conditional"
    assert "alternative_fact_ids" not in field and "review_kind" not in field
    assert report["b"]["action"] == "selected"
    assert set(report["b"]["excluded"]) == {"r", "v"}


def test_a_form_asking_for_the_rea_gets_the_rea():
    field, _ = resolved(FACTS, {"alternative_fact_ids": ["r", "i"], "conditions": [],
                                "disposition": "review", "review_kind": "ambiguous"},
                        before="REA n. ")
    assert field["fact_id"] == "r" and field["disposition"] == "value"


def test_two_values_of_the_same_type_stay_a_conflict():
    content = ("- Numero Registro Imprese: 01234560981.\n- Numero Registro Imprese: 09998887776.\n"
               "- Numero REA: BA-654321.")
    facts = {"a": fact("01234560981", "01234560981"), "b": fact("09998887776", "09998887776"),
             "r": fact("BA-654321", "BA-654321")}
    field, report = resolved(facts, {"alternative_fact_ids": ["a", "b", "r"], "conditions": [],
                                     "disposition": "review", "review_kind": "ambiguous"}, content)
    assert field["alternative_fact_ids"] == ["a", "b"] and "fact_id" not in field
    assert field["review_kind"] == "ambiguous" and report["b"]["action"] == "conflict"


def test_a_value_with_an_unreadable_type_changes_nothing():
    content = "- Numero Registro Imprese: 01234560981.\n- Codice sede: BA-654321."
    facts = {"a": fact("01234560981", "01234560981"), "b": fact("BA-654321", "BA-654321")}
    original = {"alternative_fact_ids": ["a", "b"], "conditions": [], "disposition": "review",
                "review_kind": "ambiguous"}
    field, report = resolved(facts, dict(original), content)
    assert field == original and not report


def test_a_single_proposal_of_another_type_is_replaced_or_dropped_never_written():
    field, report = resolved({"r": FACTS["r"], "i": FACTS["i"]},
                             {"fact_id": "r", "conditions": [], "disposition": "value"})
    assert field["fact_id"] == "i" and report["b"]["action"] == "replaced"
    field, report = resolved({"r": FACTS["r"]},
                             {"fact_id": "r", "conditions": [], "disposition": "value"})
    assert "fact_id" not in field and field["disposition"] == "missing"
    assert report["b"]["action"] == "dropped"
    other = fact("01234560981", "Registro delle Imprese", subject="Beta S.p.A.")
    field, _ = resolved({"r": FACTS["r"], "x": other},
                        {"fact_id": "r", "conditions": [], "disposition": "value"})
    assert "fact_id" not in field  # Never the number of another subject.


def test_a_correct_type_and_a_destination_that_asks_nothing_are_left_alone():
    field, report = resolved({"i": FACTS["i"]}, {"fact_id": "i", "conditions": [],
                                                 "disposition": "value"})
    assert field["fact_id"] == "i" and not report
    field, report = resolved({"r": FACTS["r"]}, {"fact_id": "r", "conditions": [],
                                                 "disposition": "value"}, before="Sede ")
    assert field["fact_id"] == "r" and not report


async def session(api, monkeypatch, content, profile=None):
    if profile:
        monkeypatch.setenv("MAPI_COMPILATION_PROFILE", profile)
    doc = Document()
    doc.add_paragraph("Camera di Commercio di ____________ al n. ____________")
    stream = BytesIO()
    doc.save(stream)
    form = (await api.post("/api/projects/alpha/forms",
                           files={"file": ("modulo.docx", stream.getvalue())})).json()
    await source(api, content, name="societa.md")

    async def model(client, settings, body, timeout, **kwargs):
        inp = json.loads(body["messages"][1]["content"])
        paragraph = inp["form"]["blocks"][0]["paragraphs"][0]
        cid = re.findall(r"\[\[(.+?)\]\]", paragraph["text_with_fields"])[1]
        chunk = next(s["chunk_id"] for s in inp["sources"] if "BA-654321" in s["content"])
        values_ = re.findall(r"^(.*?: )(\S+?)$", content, re.M)
        facts = {f"f{i}": {"subject": "Aurora S.r.l.", "entity": "company", "aspect": "identity",
                           "property": "numero_identificativo", "value": v, "evidence": [
                               {"chunk_id": chunk, "quote": label + v}]}
                 for i, (label, v) in enumerate(values_)}
        return json.dumps({
            "version": 12, "uncertain_paragraph_ids": [], "bindings": {}, "choice_groups": {},
            "clarifications": {}, "coverage": [], "conditions": {}, "facts": facts,
            "fields": {cid: {
                "label": "Numero iscrizione Camera di Commercio", "kind": "data",
                "disposition": "review", "conditions": [], "property": "numero_identificativo",
                "reason": "Il modulo non distingue gli identificativi",
                "review_kind": "ambiguous", "alternative_fact_ids": list(facts),
                "form": {"paragraph_id": paragraph["id"], "quote": f"al n. [[{cid}]]"}}},
        }), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", model)
    return await resolve(api, (await api.post(BASE, json={
        "form_id": form["id"], "engine": "global", "start_in_chat": True})).json())


TWO_TYPES = "Numero Registro Imprese: 01234560981\nNumero REA: BA-654321"
SAME_TYPE = "Numero Registro Imprese: 01234560981\nNumero Registro Imprese: BA-654321"


@pytest.mark.anyio
async def test_no_question_and_the_register_number_in_the_docx(api, provider, monkeypatch):
    s = await session(api, monkeypatch, TWO_TYPES)
    assert not [q for q in session_data(s)["dialogue"]["question"]["slots"]
                if "Numero iscrizione" in str(q.get("label"))]
    s = await draft(api, s)
    text = text_of((await api.get(s["last_generation"]["downloads"]["docx"])).content)
    assert "01234560981" in text and "BA-654321" not in text and not values(s)


@pytest.mark.anyio
async def test_a_real_conflict_is_kept_asked_with_its_values_and_not_written(
    api, provider, monkeypatch,
):
    s = await session(api, monkeypatch, SAME_TYPE)
    [slot] = [q for q in session_data(s)["dialogue"]["question"]["slots"]
              if "Numero iscrizione" in str(q.get("label"))]
    assert "«01234560981» oppure «BA-654321»" in slot["question"]
    assert "stesso tipo (Registro Imprese)" in slot["question"]
    data = session_data(s)
    field = next(f for f in data["audit"]["fields"] if f.get("identifier_resolution"))
    assert not field.get("proposed_value") and len(field["alternatives"]) == 2
    assert field["candidate_id"] not in dialogue.export_selection(s)[0]


@pytest.mark.anyio
async def test_the_previous_profile_keeps_the_model_alternatives(api, provider, monkeypatch):
    s = await session(api, monkeypatch, TWO_TYPES, profile="sezioni-2026-10-30-r2")
    data = session_data(s)
    field = next(f for f in data["audit"]["fields"] if f.get("alternatives"))
    assert len(field["alternatives"]) == 2 and not data["audit"].get("identifier_resolution")
