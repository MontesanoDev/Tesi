"""Readable receipts and fewer turns: what the USER confirmed, in plain words.

Manual Minervino test 2 (29 Oct): «Confermato: …; Il sottoscritto , nato a.» (a FORM clause
made of field placeholders), long fixed formulas in every turn, and decisions spread over four
turns at three questions each.
"""

import pytest

from app.compilation_chat import ClarificationDecision, ClarificationReply
from app.compilation_global_dialogue import (
    MAX_QUESTIONS,
    ContinuationPlan,
    DialoguePlan,
    confirmed_text,
    continuation_receipt,
)


@pytest.mark.parametrize('slot,text', [
    ({'question': 'Confermi che il sottoscritto della domanda è Leonardo Montemurro?',
      'condition': 'Il sottoscritto ________, nato a ________'},
     'Il sottoscritto della domanda è Leonardo Montemurro'),
    ({'question': 'Confermi che si applica al vostro caso quanto indicato nel modulo: '
                  '«Mandatario di raggruppamento temporaneo»?', 'condition': 'x'},
     'Mandatario di raggruppamento temporaneo'),
    ({'question': 'Confermi che questa situazione si applica?',
      'condition': '☐ Libero professionista singolo (art. 66)', 'label': 'Ramo'},
     'Libero professionista singolo'),
    ({'question': 'Confermi che questa situazione si applica?',
      'condition': 'Il sottoscritto [[p0.s0]], nato a [[p0.s1]]', 'label': 'Sottoscrittore'},
     'Sottoscrittore'),
])
def test_the_receipt_says_what_was_confirmed(slot, text):
    assert confirmed_text(slot) == text


def test_the_turn_receipt_is_short():
    message = continuation_receipt({'latest_turn': {'accepted': [
        {'action': 'CONDITION_TRUE', 'label': 'Identità non confermata',
         'form_clause': 'Il sottoscritto della domanda è Leonardo Montemurro'},
        {'action': 'VALUE', 'label': 'Sottoscritto'},
        {'action': 'SKIP', 'label': 'Luogo e data della domanda'}]}})
    assert message == ('Confermato: Il sottoscritto della domanda è Leonardo Montemurro. '
                       'Ho registrato: Sottoscritto. Rinviato, lascio vuoto: Luogo e data della '
                       'domanda.')


def test_four_questions_per_turn_are_accepted_by_narrator_and_planner():
    assert MAX_QUESTIONS == 4
    questions = [{'slot': n, 'question': f'Domanda numero {n}?'} for n in range(1, 5)]
    DialoguePlan(message='Riepilogo del turno.', questions=questions)
    ContinuationPlan(questions=questions)
    ClarificationDecision(action='ANSWER', replies=[
        ClarificationReply(slot=n, action='SKIP', user_quote='Rinvio') for n in range(1, 5)])


def test_the_signatory_name_is_asked_with_the_backend_text_not_a_vague_one():
    """Manual test 2: the narrator asked the name as «Quale dato o decisione vuoi indicare?»."""
    from test_signatory_order_and_extension import open_name_case

    from app.compilation_global_dialogue import question_pool, render_dialogue

    data, _, _ = open_name_case()
    pool = question_pool(data)
    [name] = [q for q in pool if q['key'] == 'field:p0.s0']
    plan = DialoguePlan(message='Riepilogo dei punti aperti.', questions=[
        {'slot': name['slot'], 'question': 'Quale dato o decisione vuoi indicare?'}])
    [slot] = render_dialogue(plan, pool)['question']['slots']
    assert slot['question'] == 'Chi sottoscrive la domanda? Indica nome e cognome del firmatario.'
