"""Alternatives of a decided capacity option are not asked: no answer could change a box.

Manual Minervino test (29 Oct): after the company option was decided, the USER was asked
whether the «studio associato» and «consorzio stabile» options applied. A positive answer is
never silently combined with the decided option and a negative one marks nothing; each answer
only made the decided choice unverifiable. Their conditions stay open, nothing is excluded.
Synthetic FORM, no Minervino data.
"""

import json
from copy import deepcopy

from docx import Document
from test_compilation_catalog import encoded, native_checkbox

from app import compilation_branch_evidence as branches
from app import compilation_scope_review as scope
from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_dialogue import question_pool
from app.docx_templates import inspect_docx

LABEL = 'Legale rappresentante di società di ingegneria'
CID = 'p3.cb0'


def case():
    doc = Document()
    doc.add_paragraph('IN QUALITÀ DI')
    for option, text in [('Professionista singolo', 'Recapito: ________'),
                         (LABEL + ' avente la seguente', 'Denominazione: ________'),
                         ('Mandatario di raggruppamento', None)]:
        p = doc.add_paragraph()
        native_checkbox(p, legacy=False, checked=False)
        p.add_run(' ' + option)
        if text:
            doc.add_paragraph(text)
    doc.add_paragraph('CHIEDE')
    layout = inspect_docx(encoded(doc))
    catalog = build_global_input(layout, 'alpha', [])['form']

    def condition(paragraph, quote, aspect, ids):
        return {'form': {'paragraph_id': paragraph, 'quote': quote}, 'aspect': aspect,
                'operator': 'semantic', 'fact_ids': [], 'reason': quote,
                'scope': [{'kind': 'candidate', 'id': c} for c in ids]}

    payload = {'version': 12, 'facts': {}, 'fields': {}, 'bindings': {}, 'coverage': [],
               'clarifications': {}, 'choice_groups': {}, 'conditions': {
                   'company': condition('paragraph:3', LABEL, 'representation', [CID, 'p4.s0']),
                   'single': condition('paragraph:1', 'Professionista singolo', 'participation',
                                       ['p1.cb0']),
                   'group': condition('paragraph:5', 'Mandatario di raggruppamento',
                                      'participation', ['p5.cb0', 'p2.s0'])}}
    audit = validate_global_proposal(json.dumps(payload), layout, 'alpha', [])
    labels = {'p4.s0': ('Denominazione', 'paragraph:4', 'Denominazione: ________'),
              'p2.s0': ('Recapito', 'paragraph:2', 'Recapito: ________'),
              'p1.cb0': ('Professionista singolo', 'paragraph:1', '☐ Professionista singolo'),
              'p5.cb0': ('Mandatario', 'paragraph:5', '☐ Mandatario di raggruppamento')}
    for field in audit['fields']:
        if field['candidate_id'] in labels:
            label, paragraph, quote = labels[field['candidate_id']]
            field.update(label=label, form_evidence={'paragraph_id': paragraph, 'quote': quote})
    data = {'generation_revision': 3, 'catalog': catalog, 'audit': audit,
            'writable_ids': list(catalog['candidates']),
            'dialogue': {'answers': {}, 'user_values': {}}}
    return data, layout, deepcopy(audit)


def decide(data, layout, validated, action='CONDITION_TRUE'):
    receipt = {'provenance': 'USER', 'action': action, 'applies': action == 'CONDITION_TRUE',
               'ambiguity_check': 'SEMANTIC_GUARD', 'question': 'Confermi: ' + LABEL + '?',
               'user_quote': 'Confermo: società di ingegneria tramite il suo legale '
                             'rappresentante.', 'affected_fields': ['p4.s0']}
    receipt['scope_validation'] = scope.proof(
        scope.target(data, 'condition:company', ['p4.s0']), receipt)
    data['dialogue']['answers']['condition:company'] = receipt
    return {**data, 'audit': branches.reconcile_branches(
        {**data, 'audit': deepcopy(validated)}, layout, 'alpha', [])}


def asked(data):
    return sorted(q['key'] for q in question_pool(data) if q['kind'] == 'applicability')


def test_before_a_decision_the_alternatives_are_asked():
    data, _, _ = case()
    assert asked(data) == ['condition:company', 'condition:group', 'condition:single']


def test_after_the_decision_only_alternatives_governing_data_are_asked():
    data, layout, validated = case()
    after = decide(data, layout, validated)
    assert branches.effective_user_values(after)[CID]['value'] is True
    assert branches.decided_peers(after) == {'p1.cb0', 'p5.cb0'}
    # «single» governs only its own box: no question. «group» also governs a data field.
    assert asked(after) == ['condition:group']
    assert after['audit']['conditions']['single']['result'] == 'unknown'  # Not excluded.
    assert 'condition:single' not in after['dialogue']['answers']


def test_revoking_the_decision_reopens_the_alternatives():
    data, layout, validated = case()
    after = decide(data, layout, validated)
    revoked = decide(deepcopy(after), layout, validated, action='SKIP')
    assert branches.decided_peers(revoked) == set()
    assert asked(revoked) == ['condition:group', 'condition:single']


def test_incompatible_positive_answers_mark_nothing_and_ask_one_explicit_choice():
    data, layout, validated = case()
    after = decide(data, layout, validated)
    receipt = {'provenance': 'USER', 'action': 'CONDITION_TRUE', 'applies': True,
               'ambiguity_check': 'SEMANTIC_GUARD', 'question': 'Confermi: Mandatario?',
               'user_quote': 'Sì, partecipiamo anche come mandatario.',
               'affected_fields': ['p2.s0']}
    receipt['scope_validation'] = scope.proof(
        scope.target(after, 'condition:group', ['p2.s0']), receipt)
    after['dialogue']['answers']['condition:group'] = receipt
    both = {**after, 'audit': branches.reconcile_branches(
        {**after, 'audit': deepcopy(validated)}, layout, 'alpha', [])}
    assert branches.effective_user_values(both) == {}  # Never silently combined.
    [choice] = [q for q in question_pool(both) if q['kind'] == 'choice']
    assert [line for line in choice['question'].splitlines()
            if line.endswith('(ramo già confermato)')] == [
        '2. Legale rappresentante di società di ingegneria (ramo già confermato)',
        '3. Mandatario di raggruppamento (ramo già confermato)']
