"""An accepted capacity branch whose checkbox no receipt can mark gets an explicit FORM choice.

Attempt 03: the company branch was confirmed, but the model scope omitted the «IN QUALITÀ DI»
checkbox. The receipt link (test_representation_checkbox_receipt) correctly refuses to extend
that scope, so the checkbox stayed empty without any question. The backend now asks one choice
among the FORM options of the region. Nothing is selected without that explicit USER choice;
only an option made applicable by an accepted condition can be chosen, exactly one, and the
other options are neither marked nor cleared (unknown cardinality).
"""

from copy import deepcopy
from io import BytesIO

import pytest
import test_representation_checkbox_receipt as base
from docx import Document
from docx.oxml.ns import qn
from test_compilation_catalog import W14

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_chat import ClarificationReply
from app.compilation_choices import materialize_choices, user_choice
from app.compilation_global_dialogue import (
    DialoguePlan,
    open_condition_questions,
    question_pool,
    render_dialogue,
)
from app.docx_templates import fill_docx

CID, KEY = base.CID, 'choice:form_capacity_0'
OPTIONS = ['p1.cb0', CID, 'p5.cb0']
CHOSEN = 'Legale rappresentante di società di ingegneria'
QUOTE = f'Scelgo «{CHOSEN}» per Mapi Ingegneria S.r.l.'


def capacity_case():
    """The receipt is accepted, but the condition scope omits its checkbox (attempt 03)."""
    data, layout = base.case()
    data['audit']['conditions']['company']['scope'] = [{'kind': 'candidate', 'id': 'p4.s0'}]
    base.sign(data)
    return base.derive(data, layout), layout


def slot_of(data):
    slots = [q for q in question_pool(data) if q['kind'] == 'choice']
    return slots[0] if slots else None


def reply(selected=(2,), action='VALUE', quote=QUOTE, value=CHOSEN, **extra):
    if action != 'VALUE':
        return ClarificationReply(slot=1, action=action, user_quote=quote)
    return ClarificationReply(slot=1, action=action, user_quote=quote, value=value,
                              selected_options=None if selected is None else list(selected),
                              **extra)


def answer(data, layout, response):
    """The receipt apply_replies records for a guarded reply, then the refreshed audit."""
    slot = slot_of(data)
    record = {'action': response.action, 'user_quote': response.user_quote,
              'provenance': 'USER', 'label': slot['label'], 'ambiguity_check': 'SEMANTIC_GUARD',
              'question': slot['question'], 'affected_fields': list(slot['field_ids'])}
    if response.action == 'VALUE':
        record['scope_validation'] = scope.proof(
            scope.target(data, KEY, slot['field_ids']), response)
        for cid, chosen in user_choice(data, slot, response).items():
            data['dialogue']['user_values'][cid] = {**chosen, 'previous': None}
        record.update(selected_options=response.selected_options, value=response.value)
    data['dialogue']['answers'][KEY] = record
    return base.derive(data, layout)


def states(layout, values):
    result = Document(BytesIO(fill_docx(layout, {}, checkbox_values=values)))
    return [next(c.iter(f'{{{W14}}}checked')).get(f'{{{W14}}}val')
            for c in result.element.iter(qn('w:sdt'))]


def test_form_options_are_asked_and_nothing_is_selected_before_the_choice():
    data, layout = capacity_case()
    assert CID not in data['audit'].get('receipt_choice_values', {})
    slot = slot_of(data)
    assert slot['key'] == KEY and slot['field_ids'] == OPTIONS and slot['form_owned']
    assert slot['question'].splitlines()[1:] == [
        'IN QUALITÀ DI', '☐ Professionista singolo',
        '☐ Legale rappresentante di società di ingegneria avente la seguente',
        '☐ Mandatario di raggruppamento']
    # Backend text, also when the narrator asks nothing; never a vague assent.
    fallback = open_condition_questions(question_pool(data))
    rendered = render_dialogue(DialoguePlan(message='Riepilogo.', questions=fallback),
                               question_pool(data))
    assert rendered['question']['slots'][0]['question'] == slot['question']
    assert branches.effective_user_values(data) == {}
    assert materialize_choices(data, [], []) == ({}, [])


def test_explicit_choice_marks_only_its_option():
    data, layout = capacity_case()
    receipt = deepcopy(data['dialogue']['answers']['condition:company'])
    after = answer(data, layout, reply())
    assert list(after['dialogue']['user_values']) == [CID]  # Peers neither marked nor cleared.
    assert branches.capacity_choice_valid(after, CID, 'company')
    assert CID not in scope.blocked_user_fields(after)
    assert materialize_choices(after, [], [CID]) == ({CID: True}, [])
    assert states(layout, {CID: True}) == ['0', '1', '0']
    assert after['dialogue']['answers']['condition:company'] == receipt  # Never re-signed.
    assert CID not in receipt['affected_fields']
    assert slot_of(after) is None  # Answered: not asked again.


def test_deferral_leaves_the_region_empty_and_is_not_asked_again():
    data, layout = capacity_case()
    after = answer(data, layout, reply(action='SKIP', quote='Rinvio questa scelta.'))
    assert after['dialogue']['user_values'] == {}
    assert branches.effective_user_values(after) == {}
    assert materialize_choices(after, [], []) == ({}, [])
    assert slot_of(after) is None


@pytest.mark.parametrize('selected,extra', [
    ((2, 3), {}), ((2, 2), {}), ((), {}), (None, {}), ((4,), {}),
    ((2,), {'normalized_value': CHOSEN}),
])
def test_ambiguous_or_malformed_choices_are_refused(selected, extra):
    data, _ = capacity_case()
    with pytest.raises(ValueError, match='ambigua'):
        user_choice(data, slot_of(data), reply(selected, **extra))


@pytest.mark.parametrize('index', [1, 3])
def test_an_option_without_an_accepted_condition_is_not_applicable(index):
    data, _ = capacity_case()
    with pytest.raises(ValueError, match='non applicabile'):
        user_choice(data, slot_of(data), reply((index,)))


def test_a_value_not_obtained_from_the_choice_is_never_exported():
    data, layout = capacity_case()
    after = answer(data, layout, reply())
    forged = deepcopy(after)
    forged['dialogue']['user_values']['p1.cb0'] = {
        **forged['dialogue']['user_values'][CID], 'label': 'Professionista singolo'}
    assert not branches.capacity_choice_valid(forged, 'p1.cb0')
    assert 'p1.cb0' in scope.blocked_user_fields(forged)
    with pytest.raises(ValueError, match='Cardinalità ignota'):
        materialize_choices(forged, [], [CID, 'p1.cb0'])
    unproved = deepcopy(after)
    unproved['dialogue']['answers'][KEY].pop('scope_validation')
    assert not branches.capacity_choice_valid(unproved, CID)
    assert CID in scope.blocked_user_fields(unproved)


@pytest.mark.parametrize('change', ['no_receipt', 'false', 'skip', 'source_only', 'no_guard',
                                    'initial_peer', 'initial_self', 'revision', 'other_aspect',
                                    'different_form'])
def test_no_question_without_an_applicable_accepted_branch(change):
    data, layout = base.case()
    data['audit']['conditions']['company']['scope'] = [{'kind': 'candidate', 'id': 'p4.s0'}]
    r = data['dialogue']['answers']['condition:company']
    if change == 'no_receipt':
        data['dialogue']['answers'].clear()
    elif change == 'false':
        r.update(action='CONDITION_FALSE', applies=False)
    elif change == 'skip':
        r.update(action='SKIP')
    elif change == 'source_only':
        r['provenance'] = 'SOURCE'
    elif change == 'no_guard':
        r.pop('ambiguity_check')
        r['user_quote'] = 'Confermo, oppure no.'
    elif change == 'initial_peer':
        data['catalog']['candidates']['p5.cb0']['initial_checked'] = True
    elif change == 'initial_self':
        data['catalog']['candidates'][CID]['initial_checked'] = True
    elif change == 'revision':
        data['generation_revision'] = 2
    elif change == 'other_aspect':
        data['audit']['conditions']['company']['aspect'] = 'identity'
    elif change == 'different_form':
        data['catalog']['blocks'][0]['paragraphs'][0]['text'] = 'ALTRO GRUPPO'
    if data['dialogue']['answers']:
        base.sign(data)
    after = base.derive(data, layout)
    assert not after['audit'].get('choice_groups') and slot_of(after) is None


def test_no_duplicate_when_the_receipt_link_or_a_model_group_owns_the_region():
    data, layout = base.case()  # Scope with the checkbox: the existing receipt link marks it.
    derived = base.derive(data, layout)
    assert list(derived['audit']['choice_groups']) == ['form_receipt_' + CID]
    assert slot_of(derived) is None
    data, layout = capacity_case()
    model = deepcopy(data['audit']['choice_groups'][KEY.removeprefix('choice:')])
    model.update(origin='MODEL', selection='single', min_selected=1)
    data['audit'] = deepcopy(data['audit'])
    data['audit']['choice_groups'] = {'model_group': model}
    again = branches.reconcile_branches(data, layout, 'alpha', [])
    assert list(again['choice_groups']) == ['model_group']


def test_revoked_or_changed_condition_invalidates_the_choice():
    data, layout = capacity_case()
    after = answer(data, layout, reply())
    revoked = deepcopy(after)
    revoked['dialogue']['answers']['condition:company']['action'] = 'SKIP'
    revoked = base.derive(revoked, layout)
    assert not branches.capacity_choice_valid(revoked, CID)
    assert CID in scope.blocked_user_fields(revoked)
    changed = deepcopy(after)  # Still accepted, but not the answer bound to the choice.
    changed['dialogue']['answers']['condition:company']['user_quote'] += ' Confermo.'
    base.sign(changed)
    changed = base.derive(changed, layout)
    assert not branches.capacity_choice_valid(changed, CID)
    assert CID in scope.blocked_user_fields(changed)


def test_choice_does_not_release_another_unresolved_condition():
    data, layout = capacity_case()
    after = answer(data, layout, reply())
    field = next(f for f in after['audit']['fields'] if f['candidate_id'] == CID)
    field['conditions'].append('additional')
    after['audit']['conditions']['additional'] = {'result': 'unknown'}
    assert CID in scope.blocked_user_fields(after)
