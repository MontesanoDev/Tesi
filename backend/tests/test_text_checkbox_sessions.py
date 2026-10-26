"""Actual session/API/export gates; model and USER-scope interpretations are simulated."""
import json
from io import BytesIO

import pytest
import test_compilation_resilient_segments as rev2
from docx import Document
from test_compilation_global_sessions import api, provider
from test_compilation_p3_hold_validation import narrator
from test_text_checkboxes import form_bytes

from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app import compilation_scope_review as scope
from app import compilation_sessions as sessions
from app.compilation_chat import ClarificationReply
from app.db import connection

__all__ = ['api', 'provider']
CID = 'p0.txcb0'


@pytest.fixture
def anyio_backend():
    return 'asyncio'


def model_response(inp, ids, *, conditional=False):
    p = inp['form']['blocks'][0]['paragraphs'][0]
    group = {'label': 'Scelta della clausola', 'subject': 'Concorrente', 'property': 'scelta',
             'form': {'paragraph_id': p['id'], 'quote': p['text']},
             'selection': 'multiple', 'min_selected': 0, 'conditions': [],
             'options': {CID: {'label': p['text'][2:].strip(),
                               'form': {'paragraph_id': p['id'], 'quote': p['text_with_choices']}}}}
    conditions = {}
    if conditional:
        group['conditions'] = ['c']
        conditions['c'] = {'form': {'paragraph_id': p['id'], 'quote': p['text']},
                           'aspect': 'participation', 'operator': 'semantic', 'fact_ids': [],
                           'scope': [{'kind': 'candidate', 'id': CID}],
                           'reason': 'La clausola si applica solo se confermata.'}
    return json.dumps(rev2.envelope(inp, {}, facts={}, choice_groups={'g': group},
                                    conditions=conditions))


async def analyzed(api, monkeypatch, *, conditional=False):
    monkeypatch.setenv('MAPI_COMPILATION_PROFILE', 'checkbox-testuali-2026-10-26')
    narrator(monkeypatch, {'message': 'La clausola richiede una scelta.', 'hold_groups': []},
             {'questions': []})
    def response(inp, ids):
        return model_response(inp, ids, conditional=conditional)

    s = await rev2.started(api, monkeypatch, form_bytes(), rev2.Model({1: [response]}))
    response = await rev2.analyze(api, s)
    assert response.status_code == 200, response.text
    s = response.json()
    with connection() as db:
        row, state = adapter._row_state(db, 'alpha', s['id'], s['version'])
        data = state['global_compilation']
        assert len(data['audit']['choice_groups']) == 1
        key, group = next(iter(data['audit']['choice_groups'].items()))
        assert group['validation'] == 'GROUNDED_GROUP'
        # Present the already backend-validated group. No model call is made here.
        q = {'slot': 1, 'key': 'choice:' + key, 'kind': 'choice', 'field_ids': [CID],
             'choice_group_id': key, 'label': 'Avvalimento',
             'question': 'Vuoi selezionare la clausola di avvalimento?'}
        data['dialogue'].update(phase='READY', error=None, question={
            'kind': 'clarifications', 'message': q['question'], 'slots': [q], 'field_ids': [CID]})
        s = sessions.save_state(db, row, state, 'test_present_validated_group')
    return s, data, q


@pytest.mark.anyio
@pytest.mark.parametrize('action', ['VALUE', 'SKIP', 'UNKNOWN', 'OTHER_SLOT', 'NO_SCOPE'])
async def test_only_the_verified_user_choice_marks_the_docx(api, provider, monkeypatch, action):
    s, data, q = await analyzed(api, monkeypatch)
    assert (await rev2.draft(api, s, [], users=[CID])).status_code in {409, 422}
    message = 'Seleziono la clausola di avvalimento.'
    reply = ClarificationReply(slot=2 if action == 'OTHER_SLOT' else 1,
        action=action if action in {'SKIP', 'UNKNOWN'} else 'VALUE',
        value=message if action not in {'SKIP', 'UNKNOWN'} else None,
        selected_options=[1] if action not in {'SKIP', 'UNKNOWN'} else None, user_quote=message)
    proofs = {} if action == 'NO_SCOPE' else {
        reply.slot: scope.proof(scope.target(data, q['key'], [CID]), reply)}
    s, errors = dialogue.apply_replies('alpha', s['id'], s['version'], [reply], message,
                                       scope_verifications=proofs)
    if action == 'VALUE':
        assert not errors
        response = await rev2.draft(api, s, [], users=[CID])
        assert response.status_code == 200, response.text
        downloads = response.json()['last_generation']['downloads']
        doc = Document(BytesIO((await api.get(downloads['docx'])).content))
        assert doc.paragraphs[1].text.startswith('[X] di avvalersi')
        assert (await api.get(downloads['template'])).content == form_bytes_from_row(s)
        report = (await api.get(downloads['report'])).json()
        assert report['checkbox_values'] == {CID: True}
        assert report['fields'][0]['provenance'] == 'USER'
    else:
        assert (await rev2.draft(api, s, [], users=[CID])).status_code in {409, 422}
        assert not rev2.state_of(s)['global_compilation']['dialogue'].get('user_values')


def form_bytes_from_row(s):
    with connection() as db:
        return bytes(sessions._row(db, 'alpha', s['id'])['original'])


@pytest.mark.anyio
@pytest.mark.parametrize('answer', ['unknown', 'false', 'true'])
async def test_user_checkbox_choice_does_not_override_its_condition(
    api, provider, monkeypatch, answer,
):
    s, data, choice = await analyzed(api, monkeypatch, conditional=True)
    key = next(iter(data['audit']['conditions']))
    if answer != 'unknown':
        q = {'slot': 1, 'key': 'condition:' + key, 'kind': 'applicability', 'field_ids': [CID],
             'label': 'Applicabilità', 'question': 'La clausola si applica?'}
        with connection() as db:
            row, state = adapter._row_state(db, 'alpha', s['id'], s['version'])
            data = state['global_compilation']
            data['dialogue'].update(phase='READY', question={'kind': 'clarifications',
                'message': q['question'], 'slots': [q], 'field_ids': [CID]})
            s = sessions.save_state(db, row, state, 'test_condition_question')
        message = 'Confermo la condizione.' if answer == 'true' else 'La condizione non si applica.'
        reply = ClarificationReply(slot=1, action='CONDITION_TRUE' if answer == 'true'
                                   else 'CONDITION_FALSE', user_quote=message)
        s, errors = dialogue.apply_replies('alpha', s['id'], s['version'], [reply], message,
            scope_verifications={1: scope.proof(scope.target(data, q['key'], [CID]), reply)})
        assert not errors
    with connection() as db:
        row, state = adapter._row_state(db, 'alpha', s['id'], s['version'])
        data = state['global_compilation']
        data['dialogue'].update(phase='READY', question={'kind': 'clarifications',
            'message': choice['question'], 'slots': [choice], 'field_ids': [CID]})
        s = sessions.save_state(db, row, state, 'test_choice_after_condition')
    message = 'Seleziono la casella.'
    reply = ClarificationReply(slot=1, action='VALUE', value=message, user_quote=message,
                               selected_options=[1])
    s, errors = dialogue.apply_replies('alpha', s['id'], s['version'], [reply], message,
        scope_verifications={1: scope.proof(scope.target(data, choice['key'], [CID]), reply)})
    assert not errors
    result = await rev2.draft(api, s, [], users=[CID], conditions=[key])
    assert result.status_code == (200 if answer == 'true' else 409), result.text
