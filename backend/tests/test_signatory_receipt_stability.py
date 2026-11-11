"""Synthetic reproduction: SOURCE derivation must not rewrite a checked USER target."""

from copy import deepcopy

import pytest
from test_compilation_selected_person import case

from app import compilation_scope_review as scope
from app.compilation_global_dialogue import export_selection, question_pool
from app.compilation_global_sessions import review_fields
from app.compilation_source_reuse import reuse_selected_person, signatory_fields


def checked_case(*, missing=False):
    data, layout, sources = case()
    data['generation_revision'] = 3
    field = next(f for f in data['audit']['fields'] if f['candidate_id'] == 'p0.s0')
    field.update(label='Nome del sottoscrittore', kind='data', disposition='review',
                 form_evidence={'paragraph_id': 'paragraph:0',
                                'quote': 'Il sottoscritto ________, nato a'})
    if missing:
        field.pop('label')
        field.pop('form_evidence')
    receipt = data['dialogue']['answers']['field:p0.s0']
    receipt['affected_fields'] = ['p0.s0']
    receipt['scope_validation'] = scope.proof(scope.target(data, 'field:p0.s0', ['p0.s0']),
                                             receipt)
    return data, layout, sources, receipt


@pytest.mark.parametrize('missing', [False, True])
def test_derivation_preserves_checked_target_and_user_export_without_another_question(missing):
    data, layout, sources, receipt = checked_case(missing=missing)
    before = deepcopy(data)
    assert scope.valid_receipt(data, 'field:p0.s0', receipt, 'p0.s0')
    data['audit'] = reuse_selected_person(data, layout, 'alpha', sources)
    assert scope.valid_receipt(data, 'field:p0.s0', receipt, 'p0.s0')
    assert data['dialogue'] == before['dialogue']  # No new or reminted authorization.
    data['dialogue']['phase'] = 'READY'
    data['fields'] = review_fields(data)
    assert export_selection({'global_compilation': data})[2] == ['p0.s0']
    assert 'field:p0.s0' not in {q['key'] for q in question_pool(data)}


@pytest.mark.parametrize('change', ['form', 'condition', 'value', 'quote', 'target', 'revoke'])
def test_real_scope_or_answer_changes_still_block_the_name(change):
    data, layout, sources, receipt = checked_case()
    data['audit'] = reuse_selected_person(data, layout, 'alpha', sources)
    field = next(f for f in data['audit']['fields'] if f['candidate_id'] == 'p0.s0')
    if change == 'form':
        field['form_evidence']['quote'] = 'Altra destinazione'
    elif change == 'condition':
        field['conditions'] = ['other']
    elif change in {'value', 'quote'}:
        receipt['value' if change == 'value' else 'user_quote'] = 'Bea Mori'
    elif change == 'target':
        receipt['affected_fields'] = ['p1.s0']
    else:
        receipt['action'] = 'SKIP'
    assert 'p0.s0' in scope.blocked_user_fields(data)


def test_missing_signatory_form_still_gets_a_backend_question():
    data, _, _, _ = checked_case()
    field = next(f for f in data['audit']['fields'] if f['candidate_id'] == 'p0.s0')
    field.pop('form_evidence')
    field.pop('label')
    prepared = signatory_fields(data)['p0.s0']
    assert prepared['label'] == 'Il sottoscritto'
    assert prepared['form_evidence']['paragraph_id'] == 'paragraph:0'
