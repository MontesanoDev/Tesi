"""USER policy matching on the 7 questions recorded in attempt 03 and on boundary slots.

AUDIT_USER_POLICY selects another policy file (e.g. the revision 1 of attempts 01-03) to
show the previous matching on the same slots; by default the tracked revision 2 runs.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).parent
POLICY = Path(os.environ.get('AUDIT_USER_POLICY',
                             HERE.parent / 'narrator_harness/user_policy.cjs')).resolve()
RECORDED = json.loads((HERE / 'fixtures/minervino-03-slots.json').read_text())
COMPANY = ('☐ Legale rappresentante di società di professionisti (art. 66, comma 1, lett. b '
           'D. Lgs. n. 36/2023) o di società di ingegneria (art.66, comma 1, lett. c D.lgs. '
           'n. 36/2023.) avente la seguente')


def rules(slots):
    script = """
const m=require(process.argv[1]);
const reply=m.policy?m.policy(new Proxy({},{get:(_,k)=>'<'+String(k)+'>'})).reply:m.reply;
const slots=JSON.parse(require('fs').readFileSync(0,'utf8'));
console.log(JSON.stringify(slots.map((s,i)=>reply({chat:{question:{slots:[{...s,slot:i+1}]}}}).rows[0].rule)));
"""
    out = subprocess.run(['node', '-e', script, str(POLICY)], input=json.dumps(slots),
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_recorded_attempt_03_questions():
    expected = {'condition:s2_c_soc': 'corporate', 'condition:s1_c_op': 'company'}
    got = dict(zip([s['key'] for s in RECORDED], rules(RECORDED)))
    assert got == {s['key']: expected.get(s['key'], 'defer') for s in RECORDED}
    # The record itself is unchanged: attempt 03 sent dates/defer for these two slots.
    assert [s['policy_03_rule'] for s in RECORDED[:2]] == ['dates', 'defer']


def slot(kind, ids, label='', question='', condition='', context=None):
    return {'kind': kind, 'key': f'{kind}:x', 'field_ids': ids, 'label': label,
            'question': question, 'condition': condition,
            'context': condition if context is None else context, 'alternatives': []}


@pytest.mark.parametrize('case,expected', [
    (slot('value', ['p46.s1'], 'dal'), 'dates'),
    (slot('value', ['p49.s3'], 'Data', "Da quando è iscritto? Indica la data di iscrizione"),
     'dates'),
    (slot('value', ['p12.s0'], 'Il sottoscritto'), 'name'),
    (slot('value', ['p14.s0'], 'Carica documentata'), 'role'),
    (slot('value', ['p14.s1'], 'operatore economico'), 'company'),
    (slot('value', ['p242.s0'], 'Luogo e data'), 'defer'),
    (slot('applicability', ['p12.s0', 'p12.s1', 'p14.s0'], 'Sottoscrittore non confermato',
          condition='Il sottoscritto _____________________________, nato a'), 'name'),
    (slot('applicability', ['p40.s0', 'p46.s1', 'p49.s3'], condition=COMPANY), 'corporate'),
    (slot('choice', ['p39.cb0', 'p39.cb1'], 'IN QUALITÀ DI', context=COMPANY), 'corporate'),
    (slot('applicability', ['p20.s0'], condition='☐ Capogruppo di raggruppamento temporaneo '
          'di professionisti (R.T.P.)'), 'defer'),
    (slot('condition', ['p60.s0'], 'Forma di partecipazione',
          condition='partecipazione in forma singola o in raggruppamento'), 'single'),
    (slot('applicability', ['p30.s0'], condition='Legale rappresentante dello studio '
          'professionale associato avente la seguente denominazione'), 'defer'),
    (slot('applicability', ['p14.s1', 'p15.s0'], condition='dell’operatore economico'), 'company'),
    (slot('applicability', ['p70.s0'], condition='dell’operatore economico'), 'defer'),
    (slot('decision', ['p39.cb0'], 'Scelta', context=COMPANY), 'defer'),
    (slot('authorization', ['p217.cb0'], 'Dichiarazioni'), 'defer'),
])
def test_boundaries(case, expected):
    assert rules([case]) == [expected]
