"""Reuse an unchanged condition receipt, never invent a checkbox USER answer."""

from copy import deepcopy
from io import BytesIO

import pytest
from docx import Document
from docx.oxml.ns import qn
from test_compilation_catalog import W14, encoded, native_checkbox

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_choices import materialize_choices
from app.compilation_global import build_global_input, validate_global_proposal
from app.docx_templates import fill_docx, inspect_docx

LABEL = 'Legale rappresentante di società di ingegneria'
CID = 'p3.cb0'


def case(tail=' avente la seguente'):
    import json

    doc = Document()
    doc.add_paragraph('IN QUALITÀ DI')
    for option, text in [('Professionista singolo', 'Recapito: ________'),
                         (LABEL + tail, 'Denominazione: ________'),
                         ('Mandatario di raggruppamento', None)]:
        p = doc.add_paragraph()
        native_checkbox(p, legacy=False, checked=False)
        p.add_run(' ' + option)
        if text:
            doc.add_paragraph(text)
    doc.add_paragraph('CHIEDE')
    layout = inspect_docx(encoded(doc))
    catalog = build_global_input(layout, 'alpha', [])['form']
    payload = {'version': 12, 'facts': {}, 'fields': {}, 'bindings': {}, 'coverage': [],
        'clarifications': {}, 'choice_groups': {}, 'conditions': {'company': {
            'form': {'paragraph_id': 'paragraph:3', 'quote': LABEL},
            'aspect': 'representation', 'operator': 'semantic', 'fact_ids': [],
            'reason': 'Qualità del dichiarante', 'scope': [
                {'kind': 'candidate', 'id': c} for c in [CID, 'p4.s0']]}}}
    audit = validate_global_proposal(json.dumps(payload), layout, 'alpha', [])
    field = next(f for f in audit['fields'] if f['candidate_id'] == 'p4.s0')
    field.update(label='Denominazione', form_evidence={
        'paragraph_id': 'paragraph:4', 'quote': 'Denominazione: ________'})
    data = {'generation_revision': 3, 'catalog': catalog, 'audit': audit,
            'writable_ids': list(catalog['candidates']), 'dialogue': {
                'answers': {}, 'user_values': {}}}
    receipt = {'provenance': 'USER', 'action': 'CONDITION_TRUE', 'applies': True,
        'ambiguity_check': 'SEMANTIC_GUARD', 'question': 'Confermi questa qualità: ' + LABEL + '?',
        'user_quote': 'Confermo: società di ingegneria tramite il suo legale rappresentante.',
        'affected_fields': ['p4.s0']}
    data['dialogue']['answers']['condition:company'] = receipt
    sign(data)
    return data, layout


def sign(data):
    r = data['dialogue']['answers']['condition:company']
    r['scope_validation'] = scope.proof(scope.target(data, 'condition:company',
                                                    r['affected_fields']), r)


def derive(data, layout):
    return {**data, 'audit': branches.reconcile_branches(data, layout, 'alpha', [])}


def test_explicit_representation_reuses_exact_receipt_and_writes_only_its_native_control():
    data, layout = case()
    old = deepcopy(data)
    after = derive(data, layout)
    users = branches.effective_user_values(after)
    assert users[CID]['value'] is True
    assert CID not in scope.blocked_user_fields(after)
    assert data == old
    assert after['dialogue']['answers'] == old['dialogue']['answers']
    assert CID not in old['dialogue']['answers']['condition:company']['affected_fields']
    values, effects = materialize_choices(after, [], [CID])
    assert values == {CID: True} and effects == []
    result = Document(BytesIO(fill_docx(layout, {}, checkbox_values=values)))
    controls = list(result.element.iter(qn('w:sdt')))
    states = [next(c.iter(f'{{{W14}}}checked')).get(f'{{{W14}}}val') for c in controls]
    assert states == ['0', '1', '0']
    glyphs = [''.join(t.text or '' for n in c.iter(qn('w:sdtContent'))
                     for t in n.iter(qn('w:t'))) for c in controls]
    assert glyphs == ['☐', '☒', '☐']


@pytest.mark.parametrize('change', ['generic_company', 'no_receipt', 'source_only', 'false',
    'skip', 'no_proof', 'changed_quote', 'wrong_scope', 'legal_declaration', 'other_branch',
    'initial_peer', 'different_form'])
def test_no_selection_from_generic_unchecked_or_incompatible_decisions(change):
    data, layout = case(' e dichiara tutti i requisiti' if change == 'legal_declaration'
                        else ' avente la seguente')
    r = data['dialogue']['answers']['condition:company']
    condition = data['audit']['conditions']['company']
    if change == 'generic_company':
        r['user_quote'] = 'Confermo i dati della società.'
        sign(data)  # Even a simulated positive guard does not supply the missing role choice.
    elif change == 'no_receipt':
        data['dialogue']['answers'].clear()
    elif change == 'source_only':
        r['provenance'] = 'SOURCE'
    elif change == 'false':
        r.update(action='CONDITION_FALSE', applies=False)
        sign(data)
    elif change == 'skip':
        r.update(action='SKIP')
    elif change == 'no_proof':
        r.pop('scope_validation')
    elif change == 'changed_quote':
        r['user_quote'] += ' non confermo il rappresentante'
    elif change == 'wrong_scope':
        condition['scope'] = [{'kind': 'candidate', 'id': 'p4.s0'}]
        sign(data)
    elif change == 'other_branch':
        condition['form_evidence']['paragraph_id'] = 'paragraph:1'
        sign(data)
    elif change == 'initial_peer':
        data['catalog']['candidates']['p1.cb0']['initial_checked'] = True
        sign(data)
    elif change == 'different_form':
        data['catalog']['blocks'][0]['paragraphs'][0]['text'] = 'ALTRO GRUPPO'
    assert CID not in branches.effective_user_values(derive(data, layout))


def test_link_does_not_release_another_unresolved_condition():
    data, layout = case()
    after = derive(data, layout)
    field = next(f for f in after['audit']['fields'] if f['candidate_id'] == CID)
    field['conditions'].append('additional')
    after['audit']['conditions']['additional'] = {'result': 'unknown'}
    assert branches.linked_receipt_valid(after, CID)
    assert CID in scope.blocked_user_fields(after)
    assert CID in scope.blocked_source_fields(after)


def test_persisted_link_is_invalid_after_receipt_revocation():
    data, layout = case()
    after = derive(data, layout)
    assert branches.linked_receipt_valid(after, CID)
    after['dialogue']['answers']['condition:company']['action'] = 'SKIP'
    assert not branches.linked_receipt_valid(after, CID)
    assert CID not in branches.effective_user_values(after)
    assert CID in scope.blocked_user_fields(after)


def test_derived_link_cannot_be_redirected_to_another_control():
    data, layout = case()
    after = derive(data, layout)
    after['audit']['receipt_choice_values']['p1.cb0'] = deepcopy(
        after['audit']['receipt_choice_values'][CID])
    assert not branches.linked_receipt_valid(after, 'p1.cb0')
    assert 'p1.cb0' not in branches.effective_user_values(after)
