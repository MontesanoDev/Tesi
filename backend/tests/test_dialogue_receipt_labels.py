"""A multi-answer receipt distinguishes decisions from writable values, without an LLM."""

from app.compilation_global_dialogue import continuation_receipt


def test_mixed_answers_identify_the_pending_decision_and_rejected_point():
    message = continuation_receipt({'latest_turn': {'accepted': [
        {'action': 'CONDITION_TRUE', 'label': 'Rappresentanza'},
        {'action': 'VALUE', 'label': 'Nominativo'},
        {'action': 'VALUE', 'label': 'Luogo e data', 'write_authorized': False},
        {'action': 'SKIP', 'label': 'Professionista esecutore'},
    ], 'unaccepted': [{'label': 'Forma di partecipazione', 'kind': 'applicability'}]}})
    for label in ['Rappresentanza', 'Nominativo', 'Luogo e data', 'Professionista esecutore',
                  'Forma di partecipazione']:
        assert label in message
    assert 'Non ho aggiunto valori né selezionato caselle per questa risposta' not in message
    assert 'non autorizza ancora scritture' in message


def test_receipt_does_not_promise_export_for_a_registered_value():
    message = continuation_receipt({'latest_turn': {'accepted': [
        {'action': 'VALUE', 'label': 'Nominativo'}]}})
    assert 'registrato' in message
    assert 'aggiornato i dati' not in message
