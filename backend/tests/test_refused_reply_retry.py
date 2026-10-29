"""A refused reply is asked again in the next turn, as the receipt promises, then closed.

Manual Minervino test 2 (29 Oct): the date reply for «dal» was refused (scope not verifiable)
and the message said a clarification was needed, but the narrator never asked it again: the
documented value stayed out of the DOCX without a second chance. Synthetic signatory FORM.
"""

from test_signatory_order_and_extension import open_name_case

from app.compilation_global_dialogue import (
    DialoguePlan,
    continuation_receipt,
    question_pool,
    render_dialogue,
)

SHOWN = 'Chi sottoscrive la domanda? Indica nome e cognome del firmatario.'


def refused(data, key='field:p0.s0'):
    data['dialogue']['latest_turn'] = {'accepted': [], 'unaccepted': [
        {'key': key, 'label': 'Il sottoscritto', 'kind': 'value', 'question': SHOWN,
         'reason': "non riesco a verificare a quali campi del modulo si applica"}]}
    return data


def test_the_refused_question_comes_first_even_if_the_narrator_skips_it():
    data, _, _ = open_name_case()
    pool = question_pool(refused(data))
    assert pool[0]['key'] == 'field:p0.s0' and pool[0]['retry']
    others = [q for q in pool if q['key'] != 'field:p0.s0']
    plan = DialoguePlan(message='Riprendo dal punto aperto.', questions=[])
    if others:  # The narrator chose another question only.
        plan = DialoguePlan(message='Riprendo dal punto aperto.', questions=[{'slot': others[0]['slot'],
                                                              'question': 'Altro dato?'}])
    slots = render_dialogue(plan, pool, follow_up=True)['question']['slots']
    assert slots[0]['key'] == 'field:p0.s0' and slots[0]['question'] == SHOWN


def test_after_the_loop_guard_it_is_not_asked_again_and_the_user_is_told():
    data, _, _ = open_name_case()
    refused(data)['dialogue']['answers']['field:p0.s0'] = {
        'action': 'UNKNOWN', 'provenance': 'BACKEND', 'origin': 'BACKEND_LOOP_GUARD'}
    assert all(not q.get('retry') for q in question_pool(data))
    data['dialogue']['latest_turn']['loop_guard'] = ['Il sottoscritto']
    message = continuation_receipt(data['dialogue'])
    assert message.startswith('Lascio vuoto «Il sottoscritto»') and 'non lo richiedo' in message


def test_without_a_refusal_nothing_is_forced():
    data, _, _ = open_name_case()
    assert not any(q.get('retry') for q in question_pool(data))
