"""A value belongs to a subject: read from the SOURCE and the FORM, never from the model's claim.

Real guard (e9a374e): «La Camera di Commercio di Studio Rossi S.r.l. ha iscrizione n. …» accepted
2/2 on the operator's field, before and after the fix. The validators read the value in the
citation and the entity type of the FORM; nobody checked whose line it was. Synthetic subjects.
"""

import json
import re
from io import BytesIO

import pytest
from docx import Document
from test_clarification_loop import (
    NAMED,
    NUMBER,
    SOURCE,
    analysis,
    analyzed,
    confirmed,
    draft,
    number_edit,
    route,
    text_of,
    values,
)
from test_compilation_global_sessions import BASE, api, provider, resolve
from test_compilation_sessions import source

from app import compilation_chat as chat
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_conversation import targets
from app.compilation_scope_review import session_data
from app.compilation_subject_check import (
    apply,
    destination_subject,
    evidence_owner,
    foreign_reply,
    known_subjects,
)

__all__ = ["api", "provider"]

KNOWN = {"person": ["Elisa Romano", "Luca Ferri"], "company": ["Aurora S.r.l."]}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def ordinary_profile(monkeypatch):
    monkeypatch.delenv("MAPI_COMPILATION_PROFILE", raising=False)


def owner(content, quote, subject, value, entity="person", known=KNOWN):
    fact = {"subject": subject, "entity": entity, "value": value,
            "source_evidence": [{"chunk_id": 1, "quote": quote}]}
    return evidence_owner(fact, {1: {"content": content}}, known)


PERSON_SECTION = "### Ing. Elisa Romano - direttore tecnico\n\n- Numero di iscrizione: 8421.\n"


def test_correct_evidence_is_verified_by_its_section_lead_or_row():
    assert owner(PERSON_SECTION, "- Numero di iscrizione: 8421.", "Elisa Romano", "8421")[
        "result"] == "verified"
    lead = "- **Elisa Romano:** direttore tecnico; iscritta con numero 8421."
    assert owner(lead, lead, "Elisa Romano", "8421")["result"] == "verified"
    row = "| Elisa Romano | 40% | Ingegnere | 8421 |"
    assert owner(row, row, "Elisa Romano", "8421")["result"] == "verified"
    assert owner("Denominazione: Aurora S.r.l.", "Denominazione: Aurora S.r.l.", "Aurora S.r.l.",
                 "Aurora S.r.l.", "company")["result"] == "verified"


@pytest.mark.parametrize("content, quote, subject, value, entity, named", [
    # Different people: section, bold lead, table row.
    (PERSON_SECTION, "- Numero di iscrizione: 8421.", "Luca Ferri", "8421", "person",
     "Elisa Romano"),
    ("- **Elisa Romano:** direttore tecnico.", "- **Elisa Romano:** direttore tecnico.",
     "Luca Ferri", "direttore tecnico", "person", "Elisa Romano"),
    ("| Elisa Romano | 8421 |", "| Elisa Romano | 8421 |", "Luca Ferri", "8421", "person",
     "Elisa Romano"),
    # A company's data from another company, in the line or the section.
    ("- **Studio Rossi S.r.l.:** Partita IVA IT999.",
     "- **Studio Rossi S.r.l.:** Partita IVA IT999.",
     "Aurora S.r.l.", "IT999", "company", "Studio Rossi S.r.l."),
    ("## Studio Rossi S.r.l.\n\n- Partita IVA: IT999.", "- Partita IVA: IT999.",
     "Aurora S.r.l.", "IT999", "company", "Studio Rossi S.r.l."),
    # A person's own record is not the company's, and vice versa.
    ("- **Elisa Romano:** PEC elisa@pec.it", "- **Elisa Romano:** PEC elisa@pec.it",
     "Aurora S.r.l.", "elisa@pec.it", "company", "Elisa Romano"),
    (PERSON_SECTION, "- Numero di iscrizione: 8421.", "Aurora S.r.l.", "8421", "company",
     "Elisa Romano"),
    ("- **Aurora S.r.l.:** PEC aurora@pec.it", "- **Aurora S.r.l.:** PEC aurora@pec.it",
     "Elisa Romano", "aurora@pec.it", "person", "Aurora S.r.l."),
])
def test_evidence_of_another_subject_is_a_mismatch(content, quote, subject, value, entity, named):
    check = owner(content, quote, subject, value, entity)
    assert check["result"] == "mismatch"
    assert any(named in o for o in check["owners"])


def test_a_role_of_another_person_is_a_mismatch_and_ones_own_is_verified():
    text = "- **Luca Ferri:** amministratore unico.\n- **Elisa Romano:** direttore tecnico."
    assert owner(text, "- **Luca Ferri:** amministratore unico.", "Elisa Romano",
                 "amministratore unico")["result"] == "mismatch"
    assert owner(text, "- **Luca Ferri:** amministratore unico.", "Luca Ferri",
                 "amministratore unico")["result"] == "verified"


def test_homonyms_and_several_candidates_are_ambiguous_not_matched():
    known = {"person": ["Mario Rossi"], "company": []}
    text = ("- **Mario Rossi:** ingegnere, CF RSSMRA80A01H501U.\n"
            "- **Mario Rossi:** geometra, CF RSSMRA75B02F205Z.")
    assert owner(text, "- **Mario Rossi:** ingegnere, CF RSSMRA80A01H501U.", "Mario Rossi",
                 "ingegnere", known=known)["result"] == "ambiguous"
    both = "Referenti: Elisa Romano e Luca Ferri, numero 8421."
    assert owner(both, both, "Elisa Romano", "8421")["result"] == "ambiguous"


def test_a_company_named_in_a_persons_record_is_not_against_that_person():
    line = "- Ruolo in Aurora S.r.l.: direttore tecnico."
    text = "### Elisa Romano\n" + line
    assert owner(text, line, "Elisa Romano", "direttore tecnico")["result"] != "mismatch"
    assert owner("## Aurora S.r.l.\n- Nome: Elisa Romano", "- Nome: Elisa Romano", "Elisa Romano",
                 "Elisa Romano")["result"] == "verified"


def test_no_owner_written_stays_unverifiable_and_is_not_blocked():
    assert owner("- Partita IVA: IT123.", "- Partita IVA: IT123.", "Aurora S.r.l.", "IT123",
                 "company")["result"] == "unverifiable"


def data_for(fields, facts, *, revision=1):
    return {"subject_check_revision": revision, "catalog": {"candidates": {}},
            "audit": {"fields": fields, "facts": facts}}


def test_a_mismatch_loses_its_grounding_and_the_previous_profile_is_untouched():
    fact = {"subject": "Aurora S.r.l.", "entity": "company", "value": "IT999", "source_evidence": [
        {"chunk_id": 1, "quote": "- Partita IVA: IT999."}]}
    field = {"candidate_id": "a", "validation": "REVIEW_REQUIRED", "validation_errors": [],
             "proposal_grounding": "GROUNDED_PROPOSAL", "proposed_value": "IT999",
             "proposal": {"fact_id": "f"}}
    sources = {1: {"content": "## Studio Rossi S.r.l.\n- Partita IVA: IT999."}}
    data = data_for([field], {"f": fact})
    [checked] = apply(data, data["audit"], sources)["fields"]
    assert checked["validation"] == "REJECTED" and "proposed_value" not in checked
    assert "Studio Rossi" in checked["validation_errors"][0]
    data = data_for([field], {"f": fact}, revision=None)
    assert apply(data, data["audit"], sources)["fields"] == [field]


def operator_field(cid, fact_id, chain="paragraph:1"):
    return {"candidate_id": cid, "validation": "REVIEW_REQUIRED", "validation_errors": [],
            "proposal_grounding": "GROUNDED_PROPOSAL", "proposal": {"fact_id": fact_id},
            "chain": chain}


def test_one_form_block_has_one_company_owner():
    facts = {"name": {"subject": "Aurora S.r.l.", "entity": "company", "value": "Aurora S.r.l.",
                      "source_evidence": []},
             "vat": {"subject": "Studio Rossi S.r.l.", "entity": "company", "value": "IT999",
                     "source_evidence": []}}
    data = data_for([operator_field("a", "name"), operator_field("b", "vat")], facts)
    data["catalog"]["candidates"] = {"a": {"context_id": "paragraph:1"},
                                     "b": {"context_id": "paragraph:1"}}
    fields = {f["candidate_id"]: f for f in apply(data, data["audit"], {})["fields"]}
    assert fields["a"]["validation"] == "REVIEW_REQUIRED"
    assert fields["b"]["validation"] == "REJECTED"
    assert "riguarda «Aurora S.r.l.»" in fields["b"]["validation_errors"][0]


EXPECTED = {"expected": {"name": "Aurora S.r.l.", "entity": "company",
                         "candidates": ["Aurora S.r.l."]},
            "known": known_subjects({"facts": {
                "a": {"subject": "Aurora S.r.l.", "entity": "company"},
                "b": {"subject": "Luca Ferri", "entity": "person"}}}),
            "user_values": [], "form_scope": None}


@pytest.mark.parametrize("message, value, code", [
    ("La Camera di Commercio di Studio Rossi S.r.l. ha iscrizione n. 123.", "123", "subject"),
    ("Il numero di Beta S.p.A. è 123.", "123", "subject"),
    ("Il codice fiscale di Luca Ferri è 123.", "123", "subject"),
    ("Il codice fiscale di Mario Bianchi è 123.", "123", "subject"),
    # A place or an institution is not a person.
    ("Il numero alla Camera di Commercio di Reggio Calabria è 123.", "123", None),
    ("Il numero alla Provincia di Reggio Emilia è 123.", "123", None),
    ("Il numero di Aurora è 123.", "123", None),
    # The expected subject named, no other subject, or the new subject as the value: no veto.
    ("Il numero di Aurora S.r.l. è 123.", "123", None),
    ("Il numero corretto è 123.", "123", None),
    ("Aurora S.r.l., e non Studio Rossi S.r.l., ha il numero 123.", "123", None),
    ("La denominazione corretta è Beta S.p.A.", "Beta S.p.A.", None),
])
def test_a_message_attributing_the_value_to_another_subject_is_vetoed(message, value, code):
    found = foreign_reply(message, value, EXPECTED)
    assert (found or {}).get("code") == code


def test_a_registered_correction_of_the_owner_is_the_expected_subject():
    check = {**EXPECTED, "user_values": ["Studio Rossi S.r.l."]}
    assert foreign_reply("Il numero di Studio Rossi S.r.l. è 123.", "123", check) is None


@pytest.mark.parametrize("scope, message, refused", [
    ("company_seat", "Il mio domicilio è in Via Roma 1.", True),
    ("company_seat", "Il mio studio personale è in Via Roma 1.", True),
    ("company_seat", "La sede legale è in Via Roma 1.", False),
    ("company_seat", "L'indirizzo è Via Roma 1.", False),
    ("personal_place", "La sede legale è in Via Roma 1.", True),
    ("personal_place", "La residenza è in Via Roma 1.", False),
])
def test_company_seat_and_personal_place_are_not_interchangeable(scope, message, refused):
    found = foreign_reply(message, "Via Roma 1", {**EXPECTED, "form_scope": scope})
    assert bool(found) is refused


@pytest.mark.anyio
async def test_a_value_of_another_company_is_refused_before_any_write_and_says_why(
    api, provider, monkeypatch,
):
    s = await confirmed(api, monkeypatch)
    version = s["version"]
    message = "La Camera di Commercio di Studio Rossi S.r.l. ha iscrizione n. 01234560981."
    _, plan = number_edit(s, message)
    s, calls, routed = await route(s, monkeypatch, message, plan)
    assert not calls  # Deterministic: the model is not asked to overrule it.
    assert "«Studio Rossi S.r.l.»" in routed.decision.answer
    assert "«Aurora S.r.l.»" in routed.decision.answer
    assert not values(s) and s["version"] == version


@pytest.mark.anyio
async def test_the_guard_receives_the_expected_subject_outside_the_receipt_digest(
    api, provider, monkeypatch,
):
    s = await confirmed(api, monkeypatch)
    cid, plan = number_edit(s)
    s, calls, _ = await route(s, monkeypatch, NAMED, plan)
    target = next(iter(json.loads(calls[0]["messages"][1]["content"])["form_scope"][
        "slots"].values()))
    assert target["subject"]["expected"]["name"] == "Aurora S.r.l."
    assert "subject" not in target.get("digest_material", {})
    assert values(s)[cid]["value"] == "01234560981"  # A correct reply still passes.


@pytest.mark.anyio
async def test_source_data_of_another_company_are_not_written_and_the_rest_are(
    api, provider, monkeypatch,
):
    doc = Document()
    doc.add_paragraph("Denominazione ____________")
    doc.add_paragraph("Partita IVA ____________")
    stream = BytesIO()
    doc.save(stream)
    form = (await api.post("/api/projects/alpha/forms",
                           files={"file": ("modulo.docx", stream.getvalue())})).json()
    await source(api, "# Aurora S.r.l.\n\nDenominazione: Aurora S.r.l.\n\n"
                      "## Studio Rossi S.r.l.\n\nPartita IVA: IT999", name="fonti.md")

    async def model(client, settings, body, timeout, **kwargs):
        inp = json.loads(body["messages"][1]["content"])
        paragraphs = [p for b in inp["form"]["blocks"] for p in b["paragraphs"]]
        chunk = inp["sources"][0]["chunk_id"]
        fields = {}
        for paragraph, fact_id, prop in zip(paragraphs, ("n", "v"),
                                            ("denominazione", "partita_iva")):
            cid = re.search(r"\[\[(.+?)\]\]", paragraph["text_with_fields"])[1]
            fields[cid] = {"label": prop, "kind": "data", "disposition": "value", "conditions": [],
                           "fact_id": fact_id, "property": prop,
                           "form": {"paragraph_id": paragraph["id"],
                                    "quote": paragraph["text_with_fields"]}}
        return json.dumps({
            "version": 12, "uncertain_paragraph_ids": [], "bindings": {}, "choice_groups": {},
            "clarifications": {}, "coverage": [], "conditions": {}, "fields": fields, "facts": {
                "n": {"subject": "Aurora S.r.l.", "entity": "company", "aspect": "identity",
                      "property": "denominazione", "value": "Aurora S.r.l.", "evidence": [
                          {"chunk_id": chunk, "quote": "Denominazione: Aurora S.r.l."}]},
                # The model claims Aurora, the line is in Studio Rossi's section.
                "v": {"subject": "Aurora S.r.l.", "entity": "company", "aspect": "identity",
                      "property": "partita_iva", "value": "IT999", "evidence": [
                          {"chunk_id": chunk, "quote": "Partita IVA: IT999"}]}}}), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", model)
    s = await resolve(api, (await api.post(BASE, json={
        "form_id": form["id"], "engine": "global", "start_in_chat": True})).json())
    s = await draft(api, s)
    text = text_of((await api.get(s["last_generation"]["downloads"]["docx"])).content)
    assert "Aurora S.r.l." in text and "IT999" not in text
    report = (await api.get(s["last_generation"]["downloads"]["report"])).json()
    assert report["written_field_count"] == 1


@pytest.mark.anyio
async def test_an_ambiguous_subject_gets_a_targeted_question_and_no_value(
    api, provider, monkeypatch,
):
    doc = Document()
    doc.add_paragraph("Partita IVA ____________ PEC ____________")
    stream = BytesIO()
    doc.save(stream)
    form = (await api.post("/api/projects/alpha/forms",
                           files={"file": ("modulo.docx", stream.getvalue())})).json()
    await source(api, "Partita IVA: IT123\nPEC: info@pec.it", name="dati.md")

    async def model(client, settings, body, timeout, **kwargs):
        inp = json.loads(body["messages"][1]["content"])
        paragraph = inp["form"]["blocks"][0]["paragraphs"][0]
        ids = re.findall(r"\[\[(.+?)\]\]", paragraph["text_with_fields"])
        chunk = inp["sources"][0]["chunk_id"]

        def fact(subject, prop, value, quote):
            return {"subject": subject, "entity": "company", "aspect": "identity",
                    "property": prop, "value": value,
                    "evidence": [{"chunk_id": chunk, "quote": quote}]}

        def field(cid, fact_id, prop, label):
            part = next(p for p in re.split(r"(?<=\]\])", paragraph["text_with_fields"])
                        if f"[[{cid}]]" in p).strip()
            return {"label": label, "kind": "data", "disposition": "value", "conditions": [],
                    "fact_id": fact_id, "property": prop,
                    "form": {"paragraph_id": paragraph["id"], "quote": part}}

        return json.dumps({
            "version": 12, "uncertain_paragraph_ids": [], "bindings": {}, "choice_groups": {},
            "clarifications": {}, "coverage": [], "conditions": {},
            "fields": {ids[0]: field(ids[0], "v", "partita_iva", "Partita IVA"),
                       ids[1]: field(ids[1], "p", "pec", "Indirizzo PEC")},
            "facts": {"v": fact("Aurora S.r.l.", "partita_iva", "IT123", "Partita IVA: IT123"),
                      "p": fact("Beta S.p.A.", "pec", "info@pec.it", "PEC: info@pec.it")},
        }), "simulated", {}

    monkeypatch.setattr(adapter, "request_model_content", model)
    s = await resolve(api, (await api.post(BASE, json={
        "form_id": form["id"], "engine": "global", "start_in_chat": True})).json())
    data = session_data(s)
    suspended = [f for f in data["audit"]["fields"]
                 if f.get("review_kind") == "subject_uncertain"]
    assert len(suspended) == 2 and not any(f.get("proposed_value") for f in suspended)
    question = data["dialogue"]["question"]["slots"][0]["question"]
    assert "«IT123»" in question or "«info@pec.it»" in question
    assert "Aurora S.r.l." in question and "Beta S.p.A." in question
    ids, _, _ = dialogue.export_selection(s)
    assert not set(ids) & {f["candidate_id"] for f in suspended}


def test_homonyms_suspend_the_proposal_and_ask_which_person():
    fact = {"subject": "Mario Rossi", "entity": "person", "value": "ingegnere", "source_evidence": [
        {"chunk_id": 1, "quote": "- **Mario Rossi:** ingegnere, CF RSSMRA80A01H501U."}]}
    field = {"candidate_id": "a", "validation": "REVIEW_REQUIRED", "validation_errors": [],
             "proposal_grounding": "GROUNDED_PROPOSAL", "proposed_value": "ingegnere",
             "disposition": "value", "label": "Qualifica", "form_evidence": {"quote": "Qualifica"},
             "proposal": {"fact_id": "f"}}
    sources = {1: {"content": "- **Mario Rossi:** ingegnere, CF RSSMRA80A01H501U.\n"
                              "- **Mario Rossi:** geometra, CF RSSMRA75B02F205Z."}}
    data = data_for([field], {"f": fact})
    [checked] = apply(data, data["audit"], sources)["fields"]
    assert checked["review_kind"] == "subject_uncertain"
    assert not checked.get("proposed_value") and not dialogue.documented_proposal(checked)
    question = dialogue._subject_question({"slot": 1, "label": "Qualifica",
                                           "subject_uncertain": checked["subject_check"]})
    assert "«ingegnere»" in question.question and "più soggetti chiamati Mario Rossi" in (
        question.question)


@pytest.mark.anyio
async def test_a_correct_clarification_on_the_same_session_still_writes_the_docx(
    api, provider, monkeypatch,
):
    s = await confirmed(api, monkeypatch)
    cid, plan = number_edit(s)
    s, _, _ = await route(s, monkeypatch, NAMED, plan)
    s = await draft(api, await resolve(api, s))
    text = text_of((await api.get(s["last_generation"]["downloads"]["docx"])).content)
    assert "01234560981" in text and "Aurora S.r.l." in text
    assert destination_subject(session_data(s), cid)["name"] == "Aurora S.r.l."
    assert any(q["key"] == "field:" + cid for q in targets(session_data(s)))
    assert NUMBER and SOURCE and analysis and analyzed and chat


def chain_data(text, facts, proposals):
    """Two destinations of one FORM sentence; only the second is documented."""
    candidates = {cid: {"type": "text", "context_id": "paragraph:1", "range": [0, 1]}
                  for cid in ("p1.s0", "p1.s1")}
    fields = [{"candidate_id": cid, "validation": "REVIEW_REQUIRED", "validation_errors": [],
               **({"proposal_grounding": "GROUNDED_PROPOSAL",
                   "proposal": {"fact_id": proposals[cid]}} if cid in proposals else {})}
              for cid in candidates]
    return {"subject_check_revision": 1, "audit": {"fields": fields, "facts": facts}, "catalog": {
        "candidates": candidates, "blocks": [{"paragraphs": [
            {"id": "paragraph:1", "text_with_fields": text}]}]}}


COMPANY_FACT = {"operator": {"subject": "Aurora S.r.l.", "entity": "company",
                             "value": "Aurora S.r.l.", "source_evidence": []}}


def test_a_persons_destination_has_no_company_owner_from_its_sentence():
    # Real run: the signatory's name refused because the destination «belonged» to the operator.
    data = chain_data("Il sottoscritto [[p1.s0]] della società [[p1.s1]]", COMPANY_FACT,
                      {"p1.s1": "operator"})
    assert destination_subject(data, "p1.s0") == {"name": None, "entity": "person",
                                                  "candidates": []}
    assert destination_subject(data, "p1.s1")["name"] == "Aurora S.r.l."


def test_the_signatory_name_is_not_refused_and_a_foreign_owner_of_a_company_field_still_is():
    data = chain_data("Il sottoscritto [[p1.s0]] della società [[p1.s1]]", COMPANY_FACT,
                      {"p1.s1": "operator"})
    message = "Leonardo Montemurro è il firmatario."
    assert foreign_reply(message, "Leonardo Montemurro", {
        "expected": destination_subject(data, "p1.s0"),
        "known": known_subjects(data["audit"]), "user_values": [], "form_scope": None}) is None
    refused = foreign_reply("La denominazione di Beta S.p.A. è 123.", "123", {
        "expected": destination_subject(data, "p1.s1"),
        "known": known_subjects(data["audit"]), "user_values": [], "form_scope": None})
    assert refused["code"] == "subject"


def test_a_destination_whose_kind_is_not_written_takes_no_owner_from_its_neighbours():
    data = chain_data("Dati: [[p1.s0]] e [[p1.s1]]", COMPANY_FACT, {"p1.s1": "operator"})
    assert destination_subject(data, "p1.s0") is None
