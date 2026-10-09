"""Bounded semantic reviews grounded in immutable structural FORM and literal SOURCE.

The generator proposes a meaning. A separate review can reject it or identify a
literal section condition, never add requirements or values. Anchors and quotations are checked
deterministically before a semantic verdict can be used.
"""

import hashlib
import json
import logging
import re
from collections import Counter
from copy import deepcopy
from typing import Literal

from pydantic import Field

from app.document_compilation import StrictModel
from app.docx_templates import text_of
from app.requirement_checks import contains_form_span

logger = logging.getLogger(__name__)


class SectionCondition(StrictModel):
    condition: str = Field(min_length=1, max_length=500)
    section_id: str = Field(min_length=1, max_length=80)
    condition_kind: Literal["subject_type", "participation", "other"]


class FormVerdict(StrictModel):
    candidate_id: str
    accepted: bool
    condition_complete: bool
    reason: str = Field(min_length=1, max_length=1000)
    section_condition: SectionCondition | None = None


class FormReview(StrictModel):
    fields: list[FormVerdict] = Field(max_length=12)


class SourceVerdict(StrictModel):
    candidate_id: str
    kind: Literal["value", "applicability", "exclusion"]
    index: int = Field(ge=0, le=3)
    accepted: bool
    # Literal evidence of the relationship, mandatory for historical services.
    relation_quote: str = Field(default="", max_length=1500)
    reason: str = Field(min_length=1, max_length=1000)


class SourceReview(StrictModel):
    supports: list[SourceVerdict] = Field(max_length=108)


class HistoricalServiceFact(StrictModel):
    source_id: int = Field(ge=1)
    performer_quote: str = Field(min_length=2, max_length=500)
    service_quote: str = Field(min_length=2, max_length=1000)
    performance_quote: str = Field(min_length=4, max_length=2500)


class HistoricalServices(StrictModel):
    facts: list[HistoricalServiceFact] = Field(max_length=96)


def enrich_structure(layout, fields):
    """Read existing XML objects; no parser/catalog or rendering changes."""
    from docx.oxml.ns import qn

    paragraphs = list(layout.document.element.body.iter(qn("w:p")))
    indices = {p: i for i, p in enumerate(paragraphs)}
    tables = {t["table"]: t for t in layout.catalog}
    for field in fields:
        field_id = field["id"]
        element = (layout.slots[field_id].paragraph if field_id in layout.slots
                   else layout.cells[field_id])
        first = element if element.tag == qn("w:p") else next(element.iter(qn("w:p")))
        position = indices[first]
        if field_id in layout.cells:
            # Section context precedes the table, not each later empty row.
            table = next(first.iterancestors(qn("w:tbl")))
            position = indices[next(table.iter(qn("w:p")))]
        previous = [(i, text_of(p).strip()) for i, p in enumerate(paragraphs[:position])]
        previous = [(i, t) for i, t in previous if t][-12:]
        sections, size = [], 0
        for i, text in reversed(previous):
            if size + len(text) > 6500:
                break
            sections.insert(0, {"id": f"paragraph:{i}", "text": text})
            size += len(text)
        sections.append({"id": f"paragraph:{position}", "text": text_of(first)})
        structural = field["structural"]
        if field["location"]["kind"] == "table_cell":
            location = field["location"]
            table_id = f"table:{location['table']}"
            row_id = f"{table_id}:row:{location['row']}"
            structural["table_section_id"] = table_id
            structural["row_section_id"] = row_id
            sections.extend([
                {"id": table_id, "text": "\n".join(
                    " | ".join(c["text"] for c in row)
                    for row in tables[location["table"]]["rows"]
                )},
                {"id": row_id, "text": " | ".join(c["text"] for c in structural["row"])},
            ])
        structural["form_sections"] = sections
        if "text_with_fields" in structural:
            structural["slot_anchor"] = structural["text_with_fields"]
        else:
            structural["slot_anchor"] = " | ".join(
                f"[[{cell['id']}]]" if cell["id"] == field_id else cell["text"]
                for cell in structural["row"]
            )

    from app.compilation_form_conditions import attach_form_dependencies

    attach_form_dependencies(layout, fields)

def form_material(field):
    return "\n".join([field["context"], *[
        section["text"] for section in field["structural"].get("form_sections", [])
    ]])


def validate_anchor(field, meaning, *, review_pending=False):
    semantic = meaning.semantic
    if not semantic or not meaning.requirement:
        raise ValueError("Interpretazione semantica senza requisito/anchor")
    anchor = field["structural"].get("slot_anchor", "")
    if f"[[{field['id']}]]" not in semantic.form_anchor or not contains_form_span(
        anchor, semantic.form_anchor,
    ):
        raise ValueError("Anchor non associato allo slot strutturale")
    material = form_material(field)
    for quote in [meaning.form_quote, meaning.requirement.form_quote,
                  semantic.subject_anchor, semantic.context_quote, meaning.condition]:
        if quote and not contains_form_span(material, quote):
            raise ValueError("Anchor/soggetto/contesto semantico assente nel FORM")
    sections = {s["id"]: s["text"] for s in field["structural"].get("form_sections", [])}
    for section_id in [semantic.section_id, semantic.exclusive_group_id]:
        if section_id and section_id not in sections:
            raise ValueError("Sezione semantica non presente nel contesto strutturale")
    if meaning.condition and (not semantic.section_id or not contains_form_span(
        sections[semantic.section_id], meaning.condition,
    )):
        raise ValueError("Condizione non ancorata alla sezione FORM")
    if (not review_pending and meaning.condition and semantic.condition_kind == "subject_type"
            and semantic.subject_relation == "represented_organization"
            and not contains_form_span(semantic.subject_anchor, meaning.condition)):
        raise ValueError("La condizione di tipologia riguarda l'entità, senza ruolo personale")
    if semantic.context_role == "PAST_SERVICE" and not semantic.context_quote:
        raise ValueError("Servizio pregresso senza contesto FORM")
    if semantic.subject_relation in {"organization", "represented_organization"} and (
        meaning.entity not in {"company", "authority", "other"} or meaning.requirement.person_role
    ):
        raise ValueError("Organizzazione rappresentata confusa con una persona")


def interpretation_digest(requirement, semantic, entity, condition):
    return hashlib.sha256(json.dumps(
        [requirement, semantic, entity, condition], sort_keys=True, ensure_ascii=False,
    ).encode()).hexdigest()


async def review_meanings(fields, meanings, request):
    by_id = {f["id"]: f for f in fields}
    proposals = []
    contexts = list(dict.fromkeys(f["context"] for f in fields))
    sections = {s["id"]: s["text"] for f in fields
                for s in f["structural"].get("form_sections", [])}
    for meaning in meanings.fields:
        if not meaning.semantic:
            continue  # Older contracts retain their literal FORM validation.
        if meaning.candidate_id not in by_id:
            raise ValueError("Mapping interno: interpretazione FORM non legata al gruppo")
        field = by_id[meaning.candidate_id]
        if not meaning.semantic.form_anchor:
            meaning.semantic.form_anchor = field["structural"].get("slot_anchor", "")
        table_cell = field["location"]["kind"] == "table_cell"
        if (not table_cell and not meaning.condition and meaning.semantic.section_id
                and meaning.semantic.subject_relation == "represented_organization"
                and meaning.semantic.context_role == "ORGANIZATION_PROFILE"
                and len(meaning.semantic.subject_anchor) <= 120):
            # A typed represented entity is itself a section prerequisite, not
            # a choice of signatory. Its completeness is reviewed below, so a
            # generic entity name never silently drops foreign/other qualifiers.
            meaning.condition = meaning.semantic.subject_anchor
            meaning.semantic.condition_kind = "subject_type"
        if meaning.condition:
            # Repair only a uniquely located literal condition. An independent
            # review must still establish that it actually governs this slot.
            row_id = field["structural"].get("row_section_id")
            local_sections = {s["id"]: s["text"]
                              for s in field["structural"].get("form_sections", [])}
            if not contains_form_span(
                local_sections.get(meaning.semantic.section_id, ""), meaning.condition,
            ):
                matches = [key for key, text in local_sections.items()
                           if contains_form_span(text, meaning.condition)]
                if row_id in matches:
                    meaning.semantic.section_id = row_id
                elif len(matches) == 1:
                    meaning.semantic.section_id = matches[0]
        try:
            # The reviewer may distinguish a parent participation condition from
            # the type of an entity listed below it. Final validation is strict.
            validate_anchor(field, meaning, review_pending=True)
        except ValueError as exc:
            meanings._semantic_reviews[field["id"]] = {"accepted": False, "reason": str(exc)}
            continue
        proposals.append({"candidate": {
            "id": field["id"], "context_index": contexts.index(field["context"]),
            "structural": {k: v for k, v in field["structural"].items() if k != "form_sections"},
            "section_ids": [s["id"] for s in field["structural"].get("form_sections", [])],
        }, "interpretation": meaning.model_dump()})
    if not proposals:
        return 0
    review = await request(
        "Verifica indipendente FORM: approva soltanto se la proprietà semantica, il soggetto, "
        "il ruolo relazionale/temporale e la condizione proposti corrispondono proprio allo "
        "slot [[candidate_id]]. Leggi prima/dopo lo slot, altri slot, frase e sezioni. "
        "Una label normalizzata NON deve essere una substring del FORM. Sono ammesse "
        "espansioni di abbreviazioni e nomi di proprietà impliciti nella sintassi. "
        "Un ruolo riferito a un'organizzazione seguito dal blank e dalla sua sede chiede "
        "l'organizzazione rappresentata, non il nome della persona. Distingui la persona "
        "che firma, l'organizzazione, il professionista specifico e i suoi dati. "
        "Non approvare proprietà assenti o prese da un altro slot. "
        "In una tabella etichetta/cella vuota, la riga identifica la proprietà e il blank. "
        "La tabella può alternare dati personali e aziendali: valuta il soggetto di ogni riga. "
        "Un soggetto aziendale generico NON è una condizione di applicabilità; un titolo "
        "del documento o section_id non rende condizionati i normali dati anagrafici. "
        "Le parentesi condizionali della riga vanno invece conservate: restituisci "
        "section_condition riferita al row_section_id se omesse, oppure condition_complete=false. "
        "Le sezioni disponibili "
        "determinano se una tabella riepiloga esperienze/contratti già eseguiti: in quel caso "
        "context_role deve essere PAST_SERVICE, non CURRENT_PROCEDURE. La tipologia "
        "aziendale è una condizione subject_type distinta da firma/partecipazione. "
        "Controlla ANCHE condizioni omesse: se lo slot appartiene a un blocco relativo "
        "a una tipologia/qualifica di soggetto, restituisci section_condition con la "
        "tipologia letterale e il section_id che la introduce, anche se interpretation.condition "
        "è vuota. Includi tutti i qualificatori necessari (es. giurisdizione estera), "
        "non solo il generico ruolo. Non confondere l'appartenenza alla tipologia con "
        "la designazione personale del firmatario. Per subject_type di un'organizzazione "
        "rappresentata usa solo la tipologia contenuta in semantic.subject_anchor, senza "
        "anteporre il ruolo della persona che la rappresenta. condition_complete è "
        "verificata sul soggetto della condizione: se riguarda il compilatore ma lo slot "
        "descrive un'altra entità elencata, restituisci section_condition con lo stesso "
        "predicato letterale e condition_kind=participation o other. Non attribuire la "
        "tipologia del compilatore alle entità elencate. condition_complete è "
        "OBBLIGATORIO: true solo se la "
        "condizione finale include TUTTI i qualificatori necessari del blocco FORM; "
        "false se un generico nome di organizzazione perde limiti geografici, giuridici "
        "o di partecipazione. Per blocchi senza condizioni condition_complete=true. "
        "Nessuna correzione di condizione necessaria = section_condition null. "
        "exclusive_group_id è lecito solo con un'istruzione FORM esplicita di scelta "
        "mutuamente esclusiva, non dalla sola diversità delle opzioni. In caso di dubbio "
        "rifiuta. Non modificare proprietà/soggetto, non cercare valori. Ogni ID una volta.",
        {"proposals": proposals, "form_contexts": contexts, "form_sections": sections}, FormReview,
    )
    expected = {p["candidate"]["id"] for p in proposals}
    counts = Counter(v.candidate_id for v in review.fields)
    for verdict in review.fields:
        if verdict.candidate_id not in expected or counts[verdict.candidate_id] > 1:
            logger.warning("DOCX FORM verdict rejected candidate=%s duplicate=%s",
                           verdict.candidate_id, counts[verdict.candidate_id] > 1)
            if verdict.candidate_id in expected:
                meanings._semantic_reviews[verdict.candidate_id] = {
                    "accepted": False,
                    "reason": "Verdetto FORM duplicato: interpretazione respinta",
                }
            continue
        meaning = next(m for m in meanings.fields if m.candidate_id == verdict.candidate_id)
        if verdict.accepted:
            if not verdict.condition_complete:
                verdict.accepted = False
                verdict.reason = "Condizione di sezione priva dei qualificatori FORM necessari"
                meanings._semantic_reviews[verdict.candidate_id] = verdict.model_dump()
                continue
            if verdict.section_condition:
                condition = verdict.section_condition
                meaning.condition = condition.condition
                meaning.semantic.section_id = condition.section_id
                meaning.semantic.condition_kind = condition.condition_kind
            try:
                validate_anchor(by_id[verdict.candidate_id], meaning)
                if (by_id[verdict.candidate_id]["location"]["kind"] != "table_cell"
                        and meaning.semantic.subject_relation == "represented_organization"
                        and meaning.semantic.section_id and not meaning.condition):
                    raise ValueError("Sezione di organizzazione senza condizione verificata")
            except ValueError as exc:
                verdict.accepted = False
                verdict.reason = str(exc)
        meanings._semantic_reviews[verdict.candidate_id] = verdict.model_dump()
    return 1


def validate_persisted_semantics(field):
    from app.compilation_session_models import CandidateMeaning

    semantic = field.get("semantic")
    checked = field.get("semantic_validation") or {}
    digest = interpretation_digest(field["requirement"], semantic,
                                   field.get("entity"), field.get("condition", ""))
    if not checked.get("accepted") or checked.get("digest") != digest:
        raise ValueError("Interpretazione semantica non verificata")
    validate_anchor(field, CandidateMeaning(
        candidate_id=field["id"], classification="data", requirement=field["requirement"],
        form_quote=field["form_evidence"]["quote"], entity=field["entity"],
        condition=field.get("condition", ""), semantic=semantic, reason="Persisted review",
    ))


async def review_sources(fields, matches, sources, coverage, request):
    """Review only proposals for the new semantic contract; no extra retry loop."""
    by_id = {f["id"]: f for f in fields}
    for field in fields:
        field.pop("source_review_errors", None)
    offers, indexed = [], {}
    for match in matches.fields:
        field = by_id.get(match.candidate_id)
        if not field or not field.get("semantic"):
            continue
        validate_persisted_semantics(field)
        for kind, supports in [("value", match.supports), ("applicability", match.applicability),
                               ("exclusion", [match.exclusion] if match.exclusion else [])]:
            for index, support in enumerate(supports):
                if support.source_id not in coverage.get(field["id"], []):
                    continue
                source = sources[support.source_id - 1]
                key = (field["id"], kind, index)
                indexed[key] = (support, source)
                offers.append({"candidate_id": field["id"], "kind": kind, "index": index,
                               "requirement": field["requirement"], "entity": field["entity"],
                               "semantic": field["semantic"],
                               "condition": field.get("condition", ""),
                               "support": support.model_dump(), "source": source})
    if not offers:
        return 0
    # Classify factual relationships without showing candidate labels or proposed
    # values: otherwise an amount matching the property can bias the temporal review.
    historical_ids = {p["support"]["source_id"] for p in offers
                      if p["semantic"]["context_role"] == "PAST_SERVICE"}
    historical_facts = []
    if historical_ids:
        facts = await request(
            "Estrai soltanto fatti SOURCE su specifici servizi/contratti già ESEGUITI "
            "da un soggetto nominato. Non hai requisiti da soddisfare o valori da trovare. "
            "La procedura descritta da un avviso/disciplinare è corrente: il suo importo, "
            "oggetto e committente NON sono un servizio pregresso. Le istruzioni che "
            "richiedono esperienza pregressa, i requisiti di partecipazione e le attività "
            "offerte dall'impresa NON dimostrano prestazioni eseguite. facts=[] se manca "
            "un rapporto concreto già svolto. Per ogni fatto copia performer_quote "
            "(nome dell'esecutore), service_quote (specifica prestazione), performance_quote "
            "(passaggio letterale completo che lega esecutore e servizio già svolto, "
            "includendo committente/periodo/importo quando presenti). I due estratti brevi "
            "devono essere contenuti nel passaggio completo. Non creare collegamenti "
            "fra frasi o documenti separati e non trasformare il futuro in passato.",
            {"sources": [{"source_id": i, **sources[i - 1]} for i in sorted(historical_ids)]},
            HistoricalServices,
        )
        for fact in facts.facts:
            if fact.source_id not in historical_ids:
                logger.warning("DOCX historical fact rejected source_id=%s", fact.source_id)
                continue
            if (contains_form_span(sources[fact.source_id - 1]["content"], fact.performance_quote)
                    and contains_form_span(fact.performance_quote, fact.performer_quote)
                    and contains_form_span(fact.performance_quote, fact.service_quote)):
                historical_facts.append(fact)
        retained = []
        for offer in offers:
            if offer["semantic"]["context_role"] != "PAST_SERVICE":
                retained.append(offer)
                continue
            proof = [fact.model_dump() for fact in historical_facts
                     if fact.source_id == offer["support"]["source_id"]
                     and contains_form_span(fact.performance_quote, offer["support"]["value"])
                     and contains_form_span(fact.performance_quote, offer["support"]["quote"])]
            if proof:
                retained.append({**offer, "historical_facts": proof})
            else:
                support, _ = indexed[(offer["candidate_id"], offer["kind"], offer["index"])]
                support._semantic_review = {
                    "accepted": False, "reason": "SOURCE senza fatto di servizio già eseguito",
                }
        offers = retained
    if not offers:
        return int(bool(historical_ids))
    review = await request(
        "Verifica SOURCE indipendente. Per ciascuna proposta approva solo proprietà, "
        "soggetto e contesto relazionale effettivamente attestati dalla fonte. "
        "ORGANIZATION_PROFILE richiede dati della società candidata, non dell'ente "
        "appaltante. PARTI di indirizzo (via, comune, CAP, provincia) possono provenire "
        "dalla stessa sede completa, senza cambiare soggetto. Sigle e sinonimi della "
        "proprietà sono ammessi. PAST_SERVICE richiede uno specifico servizio/contratto "
        "pregresso effettivamente eseguito dalla società/persona: l'avviso, il disciplinare, "
        "l'oggetto, l'importo, il committente o il CIG della procedura corrente NON lo "
        "attestano. Per PAST_SERVICE accepted=true richiede relation_quote letterale "
        "che documenti quel rapporto pregresso nella SOURCE. Attività offerte o requisiti "
        "di gara non sono esperienze eseguite. Non usare un amministratore come firmatario "
        "della pratica o un direttore tecnico come professionista designato. "
        "Per applicability verifica la condition FORM: una tipologia aziendale dichiarata "
        "può attestare subject_type, ma non firma o forma di partecipazione. Per exclusion "
        "e applicability verifica tutti i qualificatori della condizione, inclusa la "
        "giurisdizione: un recapito locale non attesta lo stabilimento all'estero. Per exclusion "
        "serve negazione esplicita o incompatibilità in un gruppo FORM esplicitamente "
        "mutuamente esclusivo. Non dedurre false da assenza di prova. Rifiuta valori "
        "vuoti, segnaposti, etichette senza dato, dati appartenenti ad altra persona o "
        "altro incarico. Usa ESATTAMENTE le tuple candidate_id/kind/index presenti in "
        "proposals: gli indici possono avere buchi. Non estendere un verdetto ad altre "
        "proposte dello stesso candidate. Ogni proposta una volta; non proporre nuovi valori.",
        {"proposals": offers}, SourceReview,
    )
    requested = {(p["candidate_id"], p["kind"], p["index"]): p for p in offers}
    counts = Counter((v.candidate_id, v.kind, v.index) for v in review.supports)
    for verdict in review.supports:
        key = (verdict.candidate_id, verdict.kind, verdict.index)
        if key not in requested or counts[key] > 1:
            logger.warning("DOCX SOURCE verdict rejected identity=%s duplicate=%s",
                           key, counts[key] > 1)
            if verdict.candidate_id in coverage:
                by_id[verdict.candidate_id].setdefault("source_review_errors", []).append(
                    f"Verifica SOURCE ignorata: proposta non richiesta/duplicata {verdict.kind} "
                    f"indice {verdict.index}",
                )
            if key in requested and counts[key] > 1:
                indexed[key][0]._semantic_review = {
                    "accepted": False, "reason": "Verdetto SOURCE duplicato: proposta respinta",
                }
            continue
        support, source = indexed[key]
        result = verdict.model_dump()
        offer = requested[key]
        if "historical_facts" in offer:
            result["historical_facts"] = offer["historical_facts"]
        if by_id[verdict.candidate_id]["semantic"]["context_role"] == "PAST_SERVICE" and (
            not verdict.relation_quote
            or not contains_form_span(source["content"], verdict.relation_quote)
        ):
            result.update(accepted=False, reason="SOURCE senza relazione a un servizio pregresso")
        support._semantic_review = result
    return 1 + int(bool(historical_ids))


def require_source_review(support):
    review = support._semantic_review or {}
    if not review.get("accepted"):
        raise ValueError("SOURCE semanticamente non verificata: " + review.get(
            "reason", "verifica della proprietà/soggetto/contesto assente",
        ))


def propagate_section_exclusions(state):
    """Only reviewed FORM choice groups can propagate a factual exclusion."""
    from app.compilation_applicability import known_applicability

    groups = {}
    for field in state["fields"]:
        semantic = field.get("semantic") or {}
        group = semantic.get("exclusive_group_id")
        if not group or not (field.get("semantic_validation") or {}).get("accepted"):
            continue
        key = (field["form_evidence"]["template_sha256"], group)
        groups.setdefault(key, []).append(field)
    for fields in groups.values():
        positives = [f for f in fields if known_applicability(f) is True]
        sections = {f["semantic"]["section_id"] for f in positives}
        if len(sections) != 1:
            continue  # Conflicting facts never select an arbitrary branch.
        for field in fields:
            if (field.get("provenance") == "USER"
                    or field["status"] in {"RESOLVED", "USER_PROVIDED"}
                    or not field.get("condition")
                    or known_applicability(field) is not None
                    or field["semantic"]["section_id"] in sections):
                continue
            proof = deepcopy(positives[0]["applicability"])
            proof.update(condition=field["condition"], applies=False,
                         exclusive_group_id=field["semantic"]["exclusive_group_id"],
                         selected_section_id=positives[0]["semantic"]["section_id"])
            field.update(applicability=proof, status="NOT_APPLICABLE", value=None,
                         provenance=proof["provenance"], source_evidence=proof.get("evidence", []),
                         alternatives=[], reason="Alternativa esclusa dal gruppo FORM verificato")


def empty_value_reason(value, label=""):
    """Reject non-information, regardless of the field identifier or provenance."""
    text = value.strip()
    if re.search(r"_{3,}|\.{3,}|…{2,}|\{\{[^}]*\}\}|\[\s*\]", text):
        return "Il valore contiene un segnaposto non compilato"
    normalized = re.sub(r"\s+", " ", text.casefold()).strip(" .:;-")
    if not re.search(r"\w", text) or normalized in {
        "n/a", "n.a", "non applicabile", "non pertinente", "non disponibile", "da compilare",
        "non compilato", "campo vuoto", "vuoto", "da inserire", "tbd", "tbc", "null",
    } or re.search(r"\b(?:campo|dato|valore)\s+(?:vuoto|non compilato|da (?:inserire|compilare))\b",
                   normalized):
        return "Il valore non contiene un'informazione effettiva"
    if text.rstrip().endswith(":") or (label and normalized == label.casefold().strip(" .:;-")):
        return "Etichetta senza valore"
    if ":" in text and empty_value_reason(text.rsplit(":", 1)[1]):
        return "Etichetta seguita da un valore vuoto/non compilato"
    return None
