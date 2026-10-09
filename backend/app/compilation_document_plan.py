"""A reviewed map of conditional sections, grounded in the immutable DOCX.

The map describes the form, never facts about an applicant. Physical block IDs,
literal conditions and a separate review bind its scope before any propagation.
There are no tender names, legal-type equivalences or candidate IDs in the rules.
"""

import json
from copy import deepcopy
from hashlib import sha256
from typing import Literal

from pydantic import Field, PrivateAttr

from app.document_compilation import StrictModel
from app.docx_templates import text_of
from app.requirement_checks import contains_form_span

PLAN_VERSION = 1


def needs_document_plan(state):
    return bool(state.get("template_sha256") and state.get("chat_workflow")
                and not state.get("document_plan"))


class ConditionalSection(StrictModel):
    start_id: str
    end_before_id: str | None
    condition: str = Field(min_length=2, max_length=500)
    kind: Literal["subject_type", "participation", "other"]
    reason: str = Field(min_length=2, max_length=1000)


class ExclusiveChoice(StrictModel):
    instruction_id: str
    quote: str = Field(min_length=2, max_length=1500)
    section_ids: list[str] = Field(min_length=2, max_length=64)
    reason: str = Field(min_length=2, max_length=1000)


class DocumentPlan(StrictModel):
    sections: list[ConditionalSection] = Field(max_length=64)
    choices: list[ExclusiveChoice] = Field(max_length=24)
    _item_errors: list[str] = PrivateAttr(default_factory=list)


class DocumentPlanReview(StrictModel):
    accepted_sections: list[str] = Field(max_length=64)
    accepted_choices: list[str] = Field(max_length=24)
    revised_sections: list[ConditionalSection] = Field(default_factory=list, max_length=64)
    revised_choices: list[ExclusiveChoice] = Field(default_factory=list, max_length=24)
    reason: str = Field(min_length=2, max_length=3000)


def document_blocks(layout):
    from docx.oxml.ns import qn

    paragraphs = list(layout.document.element.body.iter(qn("w:p")))
    positions = {p: i for i, p in enumerate(paragraphs)}
    locations, blocks = {}, []
    for element in layout.document.element.body:
        elements = list(element.iter(qn("w:p")))
        if not elements:
            continue
        block_id = f"paragraph:{positions[elements[0]]}"
        text = "\n".join(text_of(p) for p in elements if text_of(p).strip())
        for p in elements:
            locations[p] = block_id
        blocks.append({"id": block_id, "text": text, "candidate_ids": []})
    by_id = {b["id"]: b for b in blocks}
    for candidate_id in sorted(layout.candidate_ids):
        element = (layout.slots[candidate_id].paragraph if candidate_id in layout.slots
                   else layout.cells[candidate_id])
        first = next(element.iter(qn("w:p")))
        by_id[locations[first]]["candidate_ids"].append(candidate_id)
    return blocks


def verified_plan(layout, proposed, review):
    """Validate boundaries, provenance, duplicates and disjointness, fail closed."""
    blocks = document_blocks(layout)
    by_id = {b["id"]: b for b in blocks}
    order = {b["id"]: i for i, b in enumerate(blocks)}
    sections, rejected = [], list(proposed._item_errors)
    # The reviewer may supply a complete literal condition, just like the local
    # FORM reviewer. It cannot create a new section or introduce factual values.
    proposed = proposed.model_copy(deep=True)
    for revised in review.revised_sections:
        matching = [i for i, s in enumerate(proposed.sections) if s.start_id == revised.start_id]
        if len(matching) == 1:
            proposed.sections[matching[0]] = revised
    for revised in review.revised_choices:
        matching = [i for i, c in enumerate(proposed.choices)
                    if set(c.section_ids) == set(revised.section_ids)]
        if len(matching) == 1:
            proposed.choices[matching[0]] = revised
    ids = [s.start_id for s in proposed.sections]
    for section in proposed.sections:
        start, end = section.start_id, section.end_before_id
        if (ids.count(start) != 1 or review.accepted_sections.count(start) != 1
                or start not in order or end is not None and end not in order
                or not contains_form_span(by_id[start]["text"], section.condition)
                or (order[end] if end else len(blocks)) <= order[start]):
            rejected.append(start)
            continue
        covered = blocks[order[start]:order[end] if end else len(blocks)]
        sections.append({**section.model_dump(), "quote": by_id[start]["text"],
                         "field_ids": [i for b in covered for i in b["candidate_ids"]]})
    overlapping = {s["start_id"] for s in sections for other in sections if s is not other
                   and set(s["field_ids"]) & set(other["field_ids"])}
    sections = [s for s in sections if s["start_id"] not in overlapping]
    rejected.extend(sorted(overlapping))
    choices = []
    section_ids = {s["start_id"] for s in sections}
    seen = set()
    for choice in proposed.choices:
        key = choice.instruction_id
        members = set(choice.section_ids)
        if (key in seen or review.accepted_choices.count(key) != 1 or key not in by_id
                or len(members) != len(choice.section_ids) or not members <= section_ids
                or not contains_form_span(by_id[key]["text"], choice.quote)
                or any(order[key] > order[i] for i in members)
                or any(members & set(c["section_ids"]) for c in choices)):
            continue
        seen.add(key)
        choices.append(choice.model_dump())
    result = {"version": PLAN_VERSION, "template_sha256": layout.sha256,
              "sections": sections, "choices": choices, "rejected_sections": rejected,
              "review": review.model_dump()}
    result["digest"] = plan_digest(result)
    return result


def plan_digest(plan):
    return sha256(json.dumps({k: v for k, v in plan.items() if k != "digest"},
                             sort_keys=True, ensure_ascii=False).encode()).hexdigest()


async def plan_document(layout, request):
    blocks = document_blocks(layout)
    material = {"blocks": [b for b in blocks if b["text"].strip() or b["candidate_ids"]]}
    if len(json.dumps(material, ensure_ascii=False)) > 180_000:
        raise ValueError("Modulo troppo ampio per la mappa delle sezioni: revisione necessaria")
    proposal = await request(
        "Leggi la struttura COMPLETA di un modulo DOCX. Costruisci una mappa delle sole "
        "sezioni condizionali, senza compilare valori né decidere fatti aziendali. "
        "I blocks sono in ordine fisico, con ID immutabili. Ogni sezione usa start_id "
        "del blocco che introduce la condizione e end_before_id del primo blocco esterno "
        "alla sezione (null solo se arriva alla fine del documento). Comprendi le tabelle "
        "dipendenti, anche distanti. Le sezioni devono essere disgiunte: scegli il ramo "
        "principale; le condizioni locali rimarranno ai singoli campi. condition è un "
        "estratto LETTERALE breve del blocco iniziale. ATTENZIONE: non copiare tutta "
        "l'intestazione. In un'intestazione 'delegato di Ente culturale ... con sede ...' "
        "condition='Ente culturale', NON 'delegato di Ente culturale': i dati del ramo "
        "descrivono l'ente e la scelta del delegato è distinta. Analogamente per un "
        "legale rappresentante o professionista con rappresentanza di un'organizzazione. "
        "Non aggiungere 'con studio', 'con sede' o il ruolo personale alla tipologia; "
        "conserva invece qualificatori della tipologia, per esempio stabilimento estero. "
        "Separa la tipologia dell'operatore "
        "dalla designazione del firmatario: per i dati dell'organizzazione e dei suoi membri "
        "la condizione principale è la tipologia; poteri personali e partecipazione non "
        "sono provati dalla tipologia. kind=subject_type per tipologie dell'operatore, "
        "participation per ruolo/modalità nella pratica, other negli altri casi. "
        "choices contiene solo alternative che il FORM impone allo STESSO soggetto nello "
        "STESSO ambito: cita l'istruzione e tutti gli start_id delle alternative esclusive. "
        "Cita l'istruzione di scelta/eliminazione delle opzioni, non il semplice titolo "
        "che la precede. Per categorie con qualificatori in parentesi copia anche quelli "
        "nella condition, senza abbreviare il passaggio che definisce la categoria. "
        "Non inventare esclusività da norme o conoscenze giuridiche. Una società può anche "
        "essere membro di un raggruppamento/consorzio: non mettere partecipazione e tipologia "
        "nello stesso gruppo. Non raggruppare persone/ruoli diversi. I titoli generici, "
        "i dati anagrafici senza condizioni e le dichiarazioni non sono rami condizionali. "
        "Non creare condizioni per ogni cella. sections=[] e choices=[] se non presenti.",
        material, DocumentPlan,
    )
    review = await request(
        "Verifica la mappa delle sezioni contro l'originale FORM completo. Approva uno "
        "start_id solo se condizione, soggetto, tipo e confine finale governano davvero "
        "tutti i blocchi dell'intervallo. Non estendere un ramo ai dati successivi comuni. "
        "RIFIUTA kind=subject_type se la condition include il ruolo di chi rappresenta "
        "l'ente ('delegato', 'legale rappresentante', 'con potere di rappresentanza') "
        "anziché la sola tipologia con i suoi qualificatori. Rifiuta anche condizioni "
        "tronche che perdono lo stabilimento estero o altri requisiti della categoria. "
        "La condizione principale di tipologia può governare dati dell'operatore e membri "
        "elencati, ma non prova i poteri o la designazione del firmatario. "
        "Approva un instruction_id solo se la citazione esprime alternative esclusive "
        "per il medesimo soggetto/ambito e tutte le sezioni elencate sono pertinenti. "
        "Non dedurre esclusività fra una tipologia societaria e un ruolo di partecipazione. "
        "Un elenco di requisiti o documenti non è un gruppo di alternative. "
        "Se un ramo è reale ma la condition è tronca o include il ruolo invece dell'ente, "
        "puoi restituire revised_sections con la condizione LETTERALE completa corretta "
        "e gli estremi verificati, mantenendo lo start_id proposto. Per una scelta reale "
        "citata tramite un titolo generico, puoi fornire revised_choices con la vera "
        "istruzione di scelta/eliminazione presente nel FORM, mantenendo esattamente "
        "gli stessi section_ids. accepted_sections/accepted_choices si riferiscono "
        "alle versioni finali che hai verificato. Non creare nuovi rami o nuovi gruppi, "
        "né fatti o valori. Ometti gli ID che non riesci a verificare.",
        {**material, "proposal": proposal.model_dump()}, DocumentPlanReview,
    )
    return verified_plan(layout, proposal, review)


def attach_document_plan(state):
    plan = state.get("document_plan")
    if not plan:
        return
    if (plan.get("version") != PLAN_VERSION or plan.get("digest") != plan_digest(plan)
            or plan.get("template_sha256") != state.get("template_sha256")):
        raise ValueError("Mappa delle sezioni non coerente con l'originale")
    groups = {i: choice for choice in plan["choices"] for i in choice["section_ids"]}
    fields = {f["id"]: f for f in state["fields"]}
    for section in plan["sections"]:
        choice = groups.get(section["start_id"])
        for field_id in section["field_ids"]:
            if field_id not in fields:
                raise ValueError("La mappa contiene un campo estraneo all'originale")
            field = fields[field_id]
            dependency = {"version": PLAN_VERSION, "origin": "reviewed_document_plan",
                          "template_sha256": plan["template_sha256"],
                          "id": section["start_id"], "condition": section["condition"],
                          "quote": section["quote"], "kind": section["kind"],
                          "family": choice["instruction_id"] if choice else section["start_id"],
                          "group": {"id": choice["instruction_id"], "quote": choice["quote"]}
                          if choice else None, "plan_digest": plan["digest"]}
            field["document_branch"] = deepcopy(dependency)
            field["form_dependency"] = dependency
            sections = field["structural"].setdefault("form_sections", [])
            if not any(s["id"] == section["start_id"] for s in sections):
                sections.append({"id": section["start_id"], "text": section["quote"]})
