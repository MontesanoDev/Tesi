"""Clearer questions and summaries, wording only (real transcripts, 30 October campaigns).

Each case is a formulation USERs actually received: a FORM line to fill in asked as a
condition («Il sottoscritto , nato a il , residente»), «Carica documentata» with no person
or role, «riguarda: … e altri 43», confirmation summaries cut mid-word and repeating the scope
list, two identical «Chi designi per questo incarico?» for different roles. Conditions,
receipts, scope proofs, the guard input flags and decision keys are unchanged.
"""

from test_compilation_residual_decisions import data as decisions_data
from test_compilation_residual_decisions import decisions
from test_documented_conditions_not_skipped import case as condition_case
from test_documented_conditions_not_skipped import rendered

from app.compilation_global_dialogue import (
    _extension,
    _open_confirmation,
    confirmed_text,
    continuation_receipt,
    destinations_about,
    shown_label,
)

LABELS = ["Carica", "Operatore economico", "Comune sede operatore", "Provincia", "Telefono",
          "Fax", "Indirizzo e-mail", "P.E.C."]


def test_a_large_scope_says_how_many_data_and_names_some_never_e_altri():
    about = destinations_about({"affected_fields": LABELS,
                                "field_ids": [f"p{i}.s0" for i in range(49)]})
    assert about == (" (riguarda: 49 dati del modulo, tra cui Carica, Operatore economico, "
                     "Comune sede operatore, Provincia, Telefono e Fax)")
    assert destinations_about({"affected_fields": LABELS[:3], "field_ids": ["a", "b", "c"]}) \
        == " (riguarda: Carica, Operatore economico, Comune sede operatore)"
    extension = _extension(LABELS, "Legale rappresentante di società di ingegneria")
    assert "e altri" not in extension["question"]
    assert "(8 dati, tra cui Carica; Operatore economico" in extension["question"]


def test_the_rendered_question_keeps_one_scope_list_and_its_guard_flag():
    data = condition_case()
    [slot] = [s for s in rendered(data, "value") if s["kind"] == "applicability"]
    assert slot["question"].count("(riguarda:") == 1 and slot["destinations_shown"] is True


def test_a_reused_person_role_is_shown_with_person_and_role():
    field = {"label": "Carica documentata", "proposed_value": "amministratore unico e "
             "rappresentante legale", "source_reuse": {"property": "role",
                                                       "subject": "Leonardo Montemurro"}}
    assert shown_label(field) == ("Carica di Leonardo Montemurro: amministratore unico e "
                                  "rappresentante legale")
    assert shown_label({"label": "Comune sede legale"}) == "Comune sede legale"
    assert shown_label({**field, "proposed_value": None}) == "Carica di Leonardo Montemurro"


def test_a_confirmation_summary_names_the_statement_without_its_scope_or_a_cut_word():
    question = ("Confermi che la manifestazione di interesse è presentata da Mapi Ingegneria "
                "S.r.l. per la selezione degli operatori economici (riguarda: Denominazione "
                "dell'operatore economico, Comune sede legale, Indirizzo sede legale, Comune "
                "sede operativa, Indirizzo sede operativa, Codice fiscale operatore e altri 3)?")
    stored = confirmed_text({"question": question})  # The answer record keeps this string.
    receipt = continuation_receipt({"latest_turn": {"accepted": [
        {"action": "CONDITION_TRUE", "label": "Partecipazione", "form_clause": stored}]}})
    assert receipt == ("Confermato: La manifestazione di interesse è presentata da Mapi "
                       "Ingegneria S.r.l. per la selezione degli operatori economici.")
    long = "Dichiarazione " + " ".join(["dell'operatore economico partecipante"] * 8)
    receipt = continuation_receipt({"latest_turn": {"accepted": [
        {"action": "SKIP", "label": long}]}})
    shown = receipt.removeprefix("Rinviato, lascio vuoto: ").removesuffix(".")
    assert shown.endswith("…") and long.startswith(shown[:-1].rstrip())
    assert len(shown) <= 180


def test_a_FORM_line_to_fill_in_is_asked_as_a_part_to_compile_not_as_a_condition():
    q = {"slot": 1, "condition": "Il sottoscritto _____________________________, nato a "
         "__________________ (__) il __________, residente",
         "affected_fields": ["Nome e cognome del sottoscritto", "Comune di nascita"],
         "field_ids": ["p12.s0", "p12.s1"]}
    confirmation = _open_confirmation(q).confirmation
    assert confirmation == ("la parte del modulo «Il sottoscritto …, nato a … il …, "
                            "residente» va compilata (riguarda: Nome e cognome del "
                            "sottoscritto, Comune di nascita)")
    stored = confirmed_text({"question": "Confermi che " + confirmation + "?"})
    receipt = continuation_receipt({"latest_turn": {"accepted": [
        {"action": "CONDITION_TRUE", "label": "Identità", "form_clause": stored}]}})
    assert receipt == ("Confermato: la parte del modulo «Il sottoscritto …, nato a … il …, "
                       "residente».")
    # A clause the backend could not word before (technical markers) stays unworded.
    assert _open_confirmation({**q, "condition": "Il sottoscritto [[p12.s0]], nato a "
                               "[[p12.s1]]"}) is None


def test_two_designations_name_their_own_role():
    current = decisions_data()
    designations = [q for q in decisions(current) if q["decision_type"] == "designation"]
    first = [q["question"].split("\n", 1)[0] for q in designations]
    assert len(set(first)) == 2
    assert first == ["Chi designi come professionisti esecutori? Non lo ricavo dai ruoli "
                     "aziendali.", "Chi designi come professionista incaricato "
                     "dell'integrazione? Non lo ricavo dai ruoli aziendali."]
    keys = [q["key"] for q in designations]
    assert len(set(keys)) == 2  # Keys come from FORM material only, never from the wording.
