"""Closed calendar contradiction, synthetic SOURCE/FORM; other SOURCE holds remain vetoes."""

from copy import deepcopy

import pytest
from test_signatory_receipt_stability import checked_case

from app import compilation_global_dialogue as dialogue
from app.compilation_global_sessions import review_fields
from app.compilation_source_reuse import reuse_selected_person

ROLE = 'amministratrice unica'
START = '3 settembre 2025'
MISSING = ('Conferma che la carica sia effettivamente in essere alla data odierna '
           'e non solo nello scenario futuro.')


def case(start=START):
    data, layout, sources, _ = checked_case()
    sources[0]['content'] = sources[0]['content'].replace(
        'amministratrice unica della società**',
        f'amministratrice unica della società nello scenario dal {start}**')
    data['audit'] = reuse_selected_person(data, layout, 'alpha', sources)
    proposal = next(f for f in review_fields(data) if f['candidate_id'] == 'p2.s0')
    quote = proposal['source_evidence'][0]['quote']
    reason = (f'La carica di {ROLE} risulta attestata solo a partire dal {start}, '
              'mentre il ruolo richiesto nel modulo è quello attuale del sottoscrittore.')
    plan = dialogue.DialoguePlan(message='Conservo la proposta in attesa di verifica.',
        held_proposal_slots=[1], hold_reviews=[{'proposal_slot': 1, 'blocker': 'source',
            'reason': reason, 'missing_information': MISSING, 'evidence_quote': quote}])
    context = {'document_values': [{'sources': [{'quote': quote}], 'applicability_slots': []}],
        'role_contexts': [], 'previous_answers': [], 'applicability_contexts': [],
        'reference_date': '2025-09-24', '_validation_sources': sources,
        '_validation_project_id': 'alpha'}
    return data, layout, sources, proposal, context, plan


def run(parts):
    data, _, _, proposal, context, plan = parts
    return dialogue._hold_updates(data, [proposal], context, plan, 'offline-review', pool=[])


def test_past_start_cannot_be_held_as_a_future_scenario():
    parts = case()
    before = deepcopy(parts[0])
    result = run(parts)
    assert result['held_candidate_ids'] == []
    assert result['hold_records']['p2.s0']['reason_validation'] == 'REJECTED_TEMPORAL_COMPARISON'
    assert parts[0] == before


@pytest.mark.parametrize('mutation', ['future', 'ceased', 'other_person', 'contradictory',
    'missing_date', 'ambiguous_date', 'no_reference', 'other_reason', 'mixed_reason',
    'revoked_user', 'changed_form', 'stale_source'])
def test_no_release_without_the_whole_closed_proof(mutation):
    parts = case('3 ottobre 2025' if mutation == 'future' else START)
    data, _, sources, _, context, plan = parts
    if mutation == 'ceased':
        sources[0]['content'] += '\nAda Neri ha cessato la carica di amministratrice unica.'
    elif mutation == 'other_person':
        sources[0]['content'] = sources[0]['content'].replace('**Ada Neri**:', '**Bea Mori**:')
    elif mutation == 'contradictory':
        sources.append({**sources[0], 'chunk_id': -8, 'file_id': -4,
                        'content': 'Ada Neri non ricopre la carica di amministratrice unica.'})
    elif mutation in {'missing_date', 'ambiguous_date'}:
        sources[0]['content'] = sources[0]['content'].replace(
            START, '' if mutation == 'missing_date' else 'settembre 2025')
    elif mutation == 'no_reference':
        context.pop('reference_date')
    elif mutation in {'other_reason', 'mixed_reason'}:
        extra = 'La fonte è contraddittoria sulla persona designata.'
        plan.hold_reviews[0].reason = extra if mutation == 'other_reason' else (
            plan.hold_reviews[0].reason + ' ' + extra)
    elif mutation == 'revoked_user':
        data['dialogue']['answers']['field:p0.s0']['action'] = 'SKIP'
    elif mutation == 'changed_form':
        data['catalog']['blocks'][0]['paragraphs'][0]['text'] += ' Altra condizione.'
    elif mutation == 'stale_source':
        sources[0]['content'] += '\nInformazione aggiuntiva.'
    assert run(parts)['held_candidate_ids'] == ['p2.s0']


def test_released_comparison_is_revalidated_against_current_source():
    from fastapi import HTTPException

    from app.compilation_temporal_hold import validate_releases

    parts = case()
    data, _, sources, _, _, _ = parts
    data['dialogue'].update(run(parts))
    validate_releases(data, ['p2.s0'], sources, 'alpha')
    changed = deepcopy(sources)
    changed.append({**changed[0], 'chunk_id': -99, 'file_id': -99,
                    'content': 'Ada Neri ha cessato la carica di amministratrice unica.'})
    with pytest.raises(HTTPException, match='409'):
        validate_releases(data, ['p2.s0'], changed, 'alpha')
    validate_releases(data, ['p2.s1'], changed, 'alpha')  # Unrelated writes remain possible.


def test_a_different_preexisting_hold_is_never_erased_by_the_calendar_comparison():
    parts = case()
    parts[0]['dialogue'].update(held_candidate_ids=['p2.s0'], hold_records={
        'p2.s0': {'status': 'held', 'blocker': 'source', 'reason': 'Fonte revocata.'}})
    assert run(parts)['held_candidate_ids'] == ['p2.s0']


def test_additional_source_qualifier_is_not_discarded():
    assert run(case(START + ' fino al 4 settembre 2025'))['held_candidate_ids'] == ['p2.s0']
