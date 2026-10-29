"""The explicit FORM capacity choice is not lost to a link that can never be written.

Manual Minervino test (29 Oct): the company option was governed by a representation
condition (box outside its scope) and a participation condition (box in scope). Once the
participation one was confirmed, its receipt link occupied the region, but only a
representation link is ever exported: the USER's explicit choice of the 4th box lost its
group and the box stayed empty in the DOCX, silently. Synthetic FORM, no Minervino data.
"""

from copy import deepcopy

import test_equivalent_conditions_question as base

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_chat import ClarificationReply
from app.compilation_choices import materialize_choices, user_choice
from app.compilation_global_dialogue import question_pool

CID, KEY = base.CID, 'choice:form_capacity_0'
CHOSEN = 'Legale rappresentante di società di ingegneria'
QUOTE = f'Scelgo «{CHOSEN}».'


def kind(data, value):
    return [q for q in question_pool(data) if q['kind'] == value]


def only(slot, key):
    """The question of one condition alone, as when the other was not yet open."""
    return {**slot, 'key': 'condition:' + key, 'condition_ids': [key]}


def choose(data, layout, selected=2, action='VALUE', quote=QUOTE):
    slot = kind(data, 'choice')[0]
    reply = (ClarificationReply(slot=1, action='VALUE', user_quote=quote, value=CHOSEN,
                                selected_options=[selected]) if action == 'VALUE'
             else ClarificationReply(slot=1, action=action, user_quote=quote))
    record = {'action': action, 'user_quote': quote, 'provenance': 'USER',
              'label': slot['label'], 'ambiguity_check': 'SEMANTIC_GUARD',
              'question': slot['question'], 'affected_fields': list(slot['field_ids'])}
    if action == 'VALUE':
        record.update(scope_validation=scope.proof(scope.target(data, KEY, slot['field_ids']),
                                                   reply),
                      selected_options=[selected], value=CHOSEN)
        for cid, chosen in user_choice(data, slot, reply).items():
            data['dialogue']['user_values'][cid] = chosen
    data['dialogue']['answers'][KEY] = record
    return base.derive(data, layout)


def test_grouped_confirmation_then_one_explicit_choice_writes_the_box():
    data, layout = base.case()
    after = base.confirm(data, layout, base.applicability(data)[0])
    assert not after['audit'].get('receipt_choice_values')  # No unwritable link.
    group = after['audit']['choice_groups']['form_capacity_0']
    assert group['applicable'] == {CID: ['seg1', 'seg2']}
    assert len(kind(after, 'choice')) == 1 and not kind(after, 'applicability')
    chosen = choose(after, layout)
    assert branches.capacity_choice_valid(chosen, CID, 'seg1')
    assert branches.capacity_choice_valid(chosen, CID, 'seg2')
    assert CID not in scope.blocked_user_fields(chosen)
    assert materialize_choices(chosen, [], [CID]) == ({CID: True}, [])
    assert not kind(chosen, 'choice') and not kind(chosen, 'applicability')


def test_a_later_confirmation_does_not_displace_the_choice_and_explains_a_new_request():
    data, layout = base.case()
    slot = base.applicability(data)[0]
    after = base.confirm(data, layout, only(slot, 'seg1'))
    chosen = choose(after, layout)
    assert branches.capacity_choice_valid(chosen, CID, 'seg1')
    later = base.confirm(chosen, layout, only(slot, 'seg2'))
    assert 'form_capacity_0' in later['audit']['choice_groups']  # Still the explicit choice.
    assert not later['audit'].get('receipt_choice_values')
    # The choice receipt bound the old answers of the options' conditions: unverifiable now,
    # so it is asked again with the reason, never kept silently or written.
    assert not branches.capacity_choice_valid(later, CID)
    assert CID in scope.blocked_user_fields(later)
    again = kind(later, 'choice')
    assert len(again) == 1 and again[0]['question'].startswith(
        'La scelta registrata non è più verificabile')
    renewed = choose(later, layout)
    assert branches.capacity_choice_valid(renewed, CID, 'seg2')
    assert not kind(renewed, 'choice')


def test_a_deferred_choice_is_never_asked_again():
    data, layout = base.case()
    after = base.confirm(data, layout, base.applicability(data)[0])
    deferred = choose(after, layout, action='SKIP', quote='Rinvio questa scelta.')
    later = deepcopy(deferred)
    later['dialogue']['answers']['condition:seg2']['user_quote'] += ' Confermo.'
    later = base.derive(later, layout)
    assert not kind(later, 'choice') and branches.effective_user_values(later) == {}


def test_a_representation_link_still_owns_the_region_without_a_question():
    import test_representation_checkbox_receipt as receipt

    data, layout = receipt.case()
    derived = receipt.derive(data, layout)
    assert branches.effective_user_values(derived)[receipt.CID]['value'] is True
    assert not kind(derived, 'choice')
