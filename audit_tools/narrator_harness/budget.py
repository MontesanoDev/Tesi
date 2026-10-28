"""Campaign-only atomic reservations. No mutation of provider requests.

Three quantities never mix: a reservation is a proven upper bound held while a request may
be in flight; the provider-reported usage replaces it once known; estimates (expected usage,
cost) never enter this ledger. Requests that do not fit wait in FIFO order, and calls of the
initial analysis can never commit the reserve kept for the later phases. A request waits only
while live reservations of this process can still settle; if it could not fit even with all of
them settled at zero, the campaign stops at once. Reservations left pending by another process
stay charged and are never awaited.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

LIMIT=900_000
CAP=3_000_000  # Largest authorized campaign budget (attempt 03, 28 Oct 2026); limit from config.
LIVE={'pending','ticket'}
OWNER=f'{os.getpid()}-{uuid4().hex}'  # This process: only its reservations can still settle.


class Refused(RuntimeError):
    """Refused before any transport: nothing was sent and nothing is charged."""
    def __init__(self,kind,detail=''):
        super().__init__('Budget reservation refused before network request: '+kind
                         +(f' ({detail})' if detail else ''))
        self.kind=kind


def bound(body):
    # Official V4 tokenizer: ByteLevel BPE, no expanding normalizer. Text tokens
    # cannot exceed their UTF-8 bytes. Double the entire serialized request,
    # plus 32768 framing tokens: deliberately much larger than a token estimate.
    # Only bounded, non-streaming text chat requests without tools/images qualify.
    assert body.get('model')=='deepseek-flash'
    assert body.get('stream',False) is False
    assert not body.get('tools') and not body.get('functions')
    assert type(body.get('max_tokens')) is int and 0<body['max_tokens']<=393216
    assert body.get('messages') and len(body['messages'])<=100
    assert all(isinstance(m.get('content'),str) and m.get('role') in
               {'system','user','assistant'} and set(m)<={'role','content'} for m in body['messages'])
    return 2*len(json.dumps(body,ensure_ascii=False).encode('utf-8'))+32768+body['max_tokens']

@contextlib.contextmanager
def locked(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        before=path.read_text() if path.exists() else None
        data=json.loads(before) if before else {'limit':LIMIT,'calls':{}}
        yield data
        text=json.dumps(data,indent=2)
        if text!=before:  # Polling waiters read without rewriting the ledger.
            tmp=path.with_suffix(f'.{os.getpid()}.tmp');tmp.write_text(text);tmp.replace(path)

def _entries(data):
    return [*data['calls'].values(),*data.get('tickets',{}).values()]

def accounts(data):
    """Held tokens by kind: live and stale reservations, measured usage, carried and uncertain
    charges. Stale: pending for a process that is gone, so never released and never awaited."""
    held=dict.fromkeys(('reserved_live','reserved_stale','consumed','carried','unknown_held'),0)
    for c in _entries(data):
        if c['status'] in LIVE:
            held['reserved_live' if c.get('owner')==OWNER else 'reserved_stale']+=c['reserved']
        elif c['status']=='measured':held['consumed']+=c['charged']
        elif c['status']=='carried':held['carried']+=c['charged']
        elif c['status']=='unknown_fully_charged':held['unknown_held']+=c['charged']
    return {**held,'committed':sum(held.values())}

def _configure(data,limit,reserve_tokens):
    assert type(limit) is int and 0 < limit <= CAP
    assert type(reserve_tokens) is int and 0 <= reserve_tokens < limit
    assert not data['calls'] or data['limit'] == limit, 'Budget limit changed'
    assert not data['calls'] or data.get('reserve',0) == reserve_tokens, 'Budget reserve changed'
    data.update(limit=limit,reserve=reserve_tokens);data.setdefault('queue',[])

def _admit(data,key,amount,analysis,waiting,ticket=False):
    """True when reserved, False while queued, None for a ticket that can never fit, else the
    refusal kind. No request overtakes an earlier waiter; analysis calls stop below the
    reserve for the later phases."""
    assert key not in data['calls'] and key not in data.get('tickets',{})
    if data.get('stop'):
        return 'stopped'
    held=accounts(data);ceiling=data['limit']-(data['reserve'] if analysis else 0)
    line=data['queue']=[q for q in data['queue'] if q.get('owner')==OWNER]  # Dead waiters.
    position=next((i for i,q in enumerate(line) if q['key']==key),len(line))
    if held['committed']-held['reserved_live']+amount>ceiling:
        # Not even with every live reservation settled at zero: no progress is possible.
        line[:]=[q for q in line if q['key']!=key]
        if ticket:
            return None  # The exact request may still fit: it decides at its own reservation.
        data['stop']=(f'Budget insufficient: {amount} tokens over a ceiling of {ceiling} with '
                      f'{held["committed"]-held["reserved_live"]} irreversibly charged')
        return 'impossible'
    if not line[:position] and held['committed']+amount<=ceiling:
        line[:]=[q for q in line if q['key']!=key]
        (data.setdefault('tickets',{}) if ticket else data['calls'])[key]={
            'reserved':amount,'charged':amount,'status':'ticket' if ticket else 'pending',
            'owner':OWNER,'analysis':analysis,
            'admission':{'committed_before':held['committed'],'ceiling':ceiling}}
        return True
    if not waiting:
        return 'busy'
    if position==len(line):
        line.append({'key':key,'amount':amount,'analysis':analysis,'owner':OWNER})
    return False

def _refused(data,key,amount,analysis,kind):
    data.setdefault('refusals',[]).append({'key':key,'tokens':amount,'analysis':analysis,
                                          'kind':kind,'stop':data.get('stop')})
    return Refused(kind,data.get('stop') or '')

def reserve(path,key,body,limit=LIMIT,*,reserve_tokens=0,analysis=False):
    """Immediate reservation, refused if it would have to wait (redirect hops, sync calls)."""
    amount=bound(body);refusal=None
    with locked(path) as data:
        _configure(data,limit,reserve_tokens)
        outcome=_admit(data,key,amount,analysis,waiting=False)
        if outcome is not True:
            refusal=_refused(data,key,amount,analysis,outcome)
    if refusal:  # Raised after the write: the refusal and any stop are recorded.
        raise refusal
    return amount

def enqueue(path,key,amount,*,limit=LIMIT,reserve_tokens=0,analysis=False,ticket=False):
    """One FIFO step: True once reserved, False while waiting in line, None for a ticket that
    can never fit."""
    refusal=None
    with locked(path) as data:
        _configure(data,limit,reserve_tokens)
        outcome=_admit(data,key,amount,analysis,waiting=True,ticket=ticket)
        if isinstance(outcome,str):
            refusal=_refused(data,key,amount,analysis,outcome)
    if refusal:
        raise refusal
    return outcome

def convert(path,ticket,key,body):
    """Exact reservation in place of a ticket admitted earlier: never larger, so the earlier
    admission still holds. None, with nothing changed, if it does not fit in the ticket."""
    amount=bound(body);refusal=None
    with locked(path) as data:
        t=data['tickets'][ticket]
        assert t['status']=='ticket' and t['owner']==OWNER and key not in data['calls']
        if data.get('stop'):
            t.update(status='released',charged=0)
            refusal=_refused(data,key,amount,True,'stopped')
        elif amount>t['reserved']:
            return None
        else:
            t.update(status='converted',charged=0,call=key)
            data['calls'][key]={'reserved':amount,'charged':amount,'status':'pending',
                                'owner':OWNER,'analysis':True,
                                'admission':{**t['admission'],'ticket':ticket}}
    if refusal:
        raise refusal
    return amount

def release(path,ticket):
    """A ticket never converted (its client closed without a request) frees its bound."""
    with locked(path) as data:
        t=data['tickets'][ticket]
        if t['status']=='ticket':
            t.update(status='released',charged=0)

def withdraw(path,key):
    """Leave the line without a reservation (refusal or cancellation while waiting)."""
    if Path(path).exists():
        with locked(path) as data:
            data['queue']=[q for q in data.get('queue',[]) if q['key']!=key]

def carry(path,source,*,limit=LIMIT,reserve_tokens=0):
    """Open a new ledger from an earlier attempt's charges, never from its credit: measured
    usage, plus full reservations of anything pending or uncertain there."""
    raw=Path(source).read_bytes();old=json.loads(raw)
    held=sum(c['charged'] for c in old['calls'].values())
    with locked(path) as data:
        assert not data['calls'],'Carry-over only into a new ledger'
        _configure(data,limit,reserve_tokens)
        data['calls']['carried:'+hashlib.sha256(raw).hexdigest()[:16]]={
            'reserved':held,'charged':held,'status':'carried','source':str(source),
            'source_sha256':hashlib.sha256(raw).hexdigest(),'source_stop':old.get('stop'),
            'source_statuses':sorted({c['status'] for c in old['calls'].values()})}
    return held

def cancel_unstarted(path,key):
    """Only a request known not to have entered any transport can release its bound."""
    with locked(path) as data:
        call=data['calls'][key]
        assert call['status']=='pending', 'Reservation already settled'
        call.update(charged=0,status='not_dispatched',usage=None)

def settle(path,key,usage):
    with locked(path) as data:
        c=data['calls'][key]
        known=(isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0
            for k in ['prompt_tokens','completion_tokens','total_tokens'])
            and usage['total_tokens']==usage['prompt_tokens']+usage['completion_tokens'])
        if known:
            c.update(charged=usage['total_tokens'],status='measured',usage=usage)
            if usage['total_tokens']>c['reserved']:
                data['stop']='Provider violated conservative reservation'
        else:
            c.update(status='unknown_fully_charged')
            data['stop']='Missing or incoherent usage: no further calls'

def verify(path):
    """Admissions recheckable from the ledger alone: each fitted under its ceiling, and the
    ceiling of every analysis call excluded the reserve."""
    with locked(path) as data:
        reserve=data.get('reserve',0);violations=[]
        for key,c in [*data['calls'].items(),*data.get('tickets',{}).items()]:
            a=c.get('admission')
            if a is None:
                continue
            if a['committed_before']+c['reserved']>a['ceiling']:
                violations.append(f'{key}: admitted over its ceiling')
            if a['ceiling']!=data['limit']-(reserve if c['analysis'] else 0):
                violations.append(f'{key}: ceiling does not match the reserve rule')
        return violations

def totals(path):
    with locked(path) as data:
        held=accounts(data)
        return {'charged':held['committed'],**held,'available':data['limit']-held['committed'],
                'limit':data['limit'],'reserve':data.get('reserve',0),
                'queued':len(data.get('queue',[])),'tickets':len(data.get('tickets',{})),
                'refusals':len(data.get('refusals',[])),
                'provider_reported':sum(c.get('usage',{}).get('total_tokens',0)
                    for c in data['calls'].values() if c.get('usage')),
                'unknown':sum(c['status']=='unknown_fully_charged' for c in data['calls'].values()),
                'calls':len(data['calls']),'stop':data.get('stop')}
