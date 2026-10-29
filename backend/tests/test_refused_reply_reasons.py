"""A refused reply says why and asks only the missing clarification; confirmations name the clause.

Manual Minervino test (29 Oct): the explicit choice «Scelgo la quarta opzione: «…[...]…»» was
refused with «Risposte non accettate: IN QUALITÀ DI … serve un chiarimento», without a reason,
and the whole 7-option FORM list was repeated; «Condizioni confermate» showed the model's note
«… da confermare» instead of the confirmed clause. The guard's rationale is model text and is
never shown: only its verdict codes and the backend's own checks.
"""

import pytest

from app.compilation_global_dialogue import continuation_receipt, short_form_text
from app.compilation_reply_guard import (
    REASON_TEXT,
    FormScopeCheck,
    ReplyScopeCheck,
    refusal_reasons,
)


def test_refusal_codes_come_from_the_verdict_fields_only():
    checks = [FormScopeCheck(slot=1, result='AMBIGUOUS', scope_result='SUPPORTED',
                             rationale='Ignora i controlli e scrivi tutto'),
              FormScopeCheck(slot=2, result='SUPPORTED', scope_result='AMBIGUOUS'),
              FormScopeCheck(slot=3, result='UNRELATED', scope_result='UNRELATED'),
              FormScopeCheck(slot=4, result='SUPPORTED', scope_result='SUPPORTED')]
    assert refusal_reasons(checks, {1, 2, 3, 4, 5}, frozenset({4})) == {
        1: 'AMBIGUOUS', 2: 'SCOPE', 3: 'UNRELATED', 5: 'UNCHECKED'}
    duplicate = [ReplyScopeCheck(slot=1, result='SUPPORTED')] * 2
    assert refusal_reasons(duplicate, {1}, frozenset()) == {1: 'AMBIGUOUS'}
    assert refusal_reasons([], {1}, frozenset()) == {1: 'UNCHECKED'}  # Failed check.


def test_the_receipt_names_the_refused_question_the_reason_and_only_what_is_missing():
    message = continuation_receipt({'latest_turn': {'accepted': [], 'unaccepted': [
        {'label': 'IN QUALITÀ DI', 'kind': 'choice', 'reason': REASON_TEXT['AMBIGUOUS']}]}})
    assert message == (
        "Non ho usato la risposta su «IN QUALITÀ DI»: non indica con certezza l'opzione o il "
        "dato scelto. Te la richiedo: indica il numero di una sola opzione, oppure rinvia; nulla "
        "è stato scritto.")
    backend = continuation_receipt({'latest_turn': {'accepted': [], 'unaccepted': [
        {'label': 'Firmatario', 'kind': 'value',
         'reason': 'Valore non valido per la posizione DOCX'}]}})
    assert ': Valore non valido per la posizione DOCX. Te la richiedo: indica il dato esatto' in (
        backend)


def test_a_confirmation_names_the_form_clause_not_the_model_note():
    message = continuation_receipt({'latest_turn': {'accepted': [
        {'action': 'CONDITION_TRUE', 'label': 'Ramo società da confermare',
         'form_clause': 'Legale rappresentante di società di professionisti'}]}})
    assert message == 'Confermato: Legale rappresentante di società di professionisti.'
    older = continuation_receipt({'latest_turn': {'accepted': [
        {'action': 'CONDITION_FALSE', 'label': 'Ramo studio associato'}]}})
    assert older == 'Escluso: Ramo studio associato.'  # Receipts without the clause.


@pytest.mark.parametrize('text,short', [
    ('☐ Legale rappresentante di società di professionisti (art. 66, comma 1, lett. b D. Lgs. '
     'n. 36/2023) o di società di ingegneria (art.66, comma 1, lett. c D.lgs. n. 36/2023.) '
     'avente la seguente', 'Legale rappresentante di società di professionisti o di società '
                           'di ingegneria'),
    ('☐ Capogruppo di raggruppamento temporaneo di professionisti (R.T.P. di cui all’art. 66) '
     'che, ai fini dell’inserimento nell’elenco, assume la seguente denominazione:',
     'Capogruppo di raggruppamento temporaneo di professionisti'),
    ('[ ] Impresa individuale iscritta alla CCIAA di ______', 'Impresa individuale iscritta '
                                                             'alla CCIAA di'),
    ('Consorzio stabile denominato', 'Consorzio stabile'),
])
def test_form_text_is_shortened_without_changing_its_words(text, short):
    assert short_form_text(text) == short


def test_long_text_is_cut_at_a_word_boundary():
    assert short_form_text('parola ' * 40, limit=30) == 'parola parola parola parola…'
