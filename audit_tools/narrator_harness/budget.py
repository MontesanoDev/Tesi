"""Campaign-only atomic reservations. No mutation of provider requests."""
import contextlib
import fcntl
import json
import os
from pathlib import Path

LIMIT=900_000

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
        data=json.loads(path.read_text()) if path.exists() else {'limit':LIMIT,'calls':{}}
        yield data
        tmp=path.with_suffix(f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.replace(path)

def reserve(path,key,body):
    amount=bound(body)
    with locked(path) as data:
        assert key not in data['calls']
        if data.get('stop') or sum(c['charged'] for c in data['calls'].values())+amount>LIMIT:
            raise RuntimeError('Budget reservation refused before network request')
        data['calls'][key]={'reserved':amount,'charged':amount,'status':'pending'}
    return amount

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

def totals(path):
    with locked(path) as data:
        return {'charged':sum(c['charged'] for c in data['calls'].values()),
                'calls':len(data['calls']),'stop':data.get('stop')}
