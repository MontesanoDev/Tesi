"""Equivalent FORM clauses declared by several segments are asked once, with one receipt each.

Manual Minervino test (29 Oct): segment 1 and segment 2 each declared the company option
(same FORM paragraph) as their own condition, so the USER confirmed the same clause twice.
Here a synthetic FORM.
"""

import json
from copy import deepcopy

import pytest
from test_compilation_catalog import encoded, native_checkbox

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_chat import ClarificationReply
from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_dialogue import condition_receipts, question_pool
from app.docx_templates import inspect_docx

LABEL = 'Legale rappresentante di società di ingegneria avente la seguente'
CID = 'p3.cb0'
QUOTE = 'Confermo: la domanda è presentata come legale rappresentante della società di ingegneria.'


def case(second=True, paragraph='paragraph:3', operator='semantic'):
    from docx import Document

    doc = Document()
    doc.add_paragraph('IN QUALITÀ DI')
    for option, text in [('Professionista singolo', 'Recapito: ________'),
                         (LABEL, 'Denominazione: ________'),
                         ('Mandatario di raggruppamento', None)]:
        p = doc.add_paragraph()
        native_checkbox(p, legacy=False, checked=False)
        p.add_run(' ' + option)
        if text:
            doc.add_paragraph(text)
    doc.add_paragraph('Sede della società: ________')
    doc.add_paragraph('CHIEDE')
    layout = inspect_docx(encoded(doc))
    catalog = build_global_input(layout, 'alpha', [])['form']
    conditions = {'seg1': {
        'form': {'paragraph_id': 'paragraph:3', 'quote': LABEL}, 'aspect': 'representation',
        'operator': 'semantic', 'fact_ids': [], 'reason': 'Ramo società (segmento 1)',
        'scope': [{'kind': 'candidate', 'id': 'p4.s0'}]}}
    if second:
        conditions['seg2'] = {
            'form': {'paragraph_id': paragraph, 'quote': LABEL if paragraph == 'paragraph:3'
                     else 'Recapito: ________'},
            'aspect': 'participation', 'operator': operator, 'fact_ids': [],
            'reason': 'Ramo società (segmento 2)',
            'scope': [{'kind': 'candidate', 'id': c} for c in [CID, 'p6.s0']]}
    payload = {'version': 12, 'facts': {}, 'fields': {}, 'bindings': {}, 'coverage': [],
               'clarifications': {}, 'choice_groups': {}, 'conditions': conditions}
    audit = validate_global_proposal(json.dumps(payload), layout, 'alpha', [])
    for cid, label, quote in [('p4.s0', 'Denominazione', 'Denominazione: ________'),
                              ('p6.s0', 'Sede della società', 'Sede della società: ________')]:
        field = next(f for f in audit['fields'] if f['candidate_id'] == cid)
        field.update(label=label, form_evidence={'paragraph_id': 'paragraph:' + cid[1],
                                                 'quote': quote})
    data = {'generation_revision': 3, 'catalog': catalog, 'audit': audit,
            'writable_ids': list(catalog['candidates']),
            'dialogue': {'answers': {}, 'user_values': {}}}
    return data, layout


def confirm(data, layout, slot, action='CONDITION_TRUE', quote=QUOTE):
    """The records apply_replies stores for one guarded reply (scope proof by the backend)."""
    reply = ClarificationReply(slot=1, action=action, user_quote=quote)
    record = {'action': action, 'user_quote': quote, 'provenance': 'USER',
              'label': slot['label'], 'ambiguity_check': 'SEMANTIC_GUARD',
              'question': 'Confermi che si applica: ' + LABEL + '?',
              'affected_fields': list(slot['field_ids'])}
    if action in {'CONDITION_TRUE', 'CONDITION_FALSE'}:
        record.update(applies=action == 'CONDITION_TRUE', scope_validation=scope.proof(
            scope.target(data, slot['key'], slot['field_ids']), reply))
    data['dialogue']['answers'].update(condition_receipts(data, slot, record, reply))
    return {**data, 'audit': branches.reconcile_branches(data, layout, 'alpha', [])}


def applicability(data):
    return [q for q in question_pool(data) if q['kind'] == 'applicability']


def test_one_question_covers_the_destinations_of_both_segments():
    data, _ = case()
    slots = applicability(data)
    assert len(slots) == 1 and slots[0]['condition_ids'] == ['seg1', 'seg2']
    assert set(slots[0]['field_ids']) == {'p4.s0', 'p6.s0'}


def test_one_confirmation_gives_each_condition_its_own_valid_receipt():
    data, layout = case()
    slot = applicability(data)[0]
    after = confirm(data, layout, slot)
    answers = after['dialogue']['answers']
    assert answers['condition:seg1']['scope_validation'] != answers['condition:seg2'][
        'scope_validation']  # Each proof is bound to its own key.
    for key in ('condition:seg1', 'condition:seg2'):
        assert answers[key]['applies'] is True
        assert all(scope.valid_receipt(after, key, answers[key], cid)
                   for cid in slot['field_ids'])
    assert applicability(after) == []  # Neither is asked again.
    assert not {'p4.s0', 'p6.s0'} & scope.blocked_source_fields(after)


def test_deferral_covers_the_group_and_marks_nothing():
    data, layout = case()
    after = confirm(data, layout, applicability(data)[0], action='SKIP',
                    quote='Rinvio questa conferma.')
    assert {k: v['action'] for k, v in after['dialogue']['answers'].items()} == {
        'condition:seg1': 'SKIP', 'condition:seg2': 'SKIP'}
    assert applicability(after) == [] and branches.effective_user_values(after) == {}


@pytest.mark.parametrize('change', ['revoked', 'changed_scope'])
def test_a_revoked_or_stale_grouped_receipt_blocks_again(change):
    data, layout = case()
    after = confirm(data, layout, applicability(data)[0])
    stale = deepcopy(after)
    if change == 'revoked':
        stale['dialogue']['answers']['condition:seg2'].update(action='SKIP', applies=None)
    else:  # The destinations confirmed are no longer those of the receipt.
        stale['dialogue']['answers']['condition:seg2']['affected_fields'].remove('p6.s0')
    stale = {**stale, 'audit': branches.reconcile_branches(stale, layout, 'alpha', [])}
    assert 'p6.s0' in scope.blocked_source_fields(stale)
    assert 'p4.s0' not in scope.blocked_source_fields(stale)  # Only seg1 governs it.


@pytest.mark.parametrize('kwargs', [{'paragraph': 'paragraph:2'}, {'operator': 'equals'},
                                    {'second': False}])
def test_different_clauses_or_non_semantic_conditions_are_not_grouped(kwargs):
    data, _ = case(**kwargs)
    slots = applicability(data)
    assert [s['condition_ids'] for s in slots][0] == ['seg1']
    assert all(len(s['condition_ids']) == 1 for s in slots)
    if 'paragraph' in kwargs:  # A different clause stays its own question.
        assert [s['condition_ids'] for s in slots] == [['seg1'], ['seg2']]
