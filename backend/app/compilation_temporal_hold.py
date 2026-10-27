"""Refute one closed calendar claim, never general SOURCE doubts or current legal powers.

Only the existing named role reuse grammar and an explicit open start date qualify.
Unrecognised wording remains held. A released comparison is re-proved at export.
"""

import hashlib
import re
from datetime import date

from app.compilation_role_records import _text

MONTHS = ('gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre '
          'novembre dicembre').split()
MISSING = ('Conferma che la carica sia effettivamente in essere alla data odierna '
           'e non solo nello scenario futuro.')


def comparison_proof(data, cid, review, sources, project_id, reference):
    from app.compilation_global import _allowed_sources
    from app.compilation_scope_review import blocked_source_fields, valid_receipt
    from app.compilation_segments import request_digest
    from app.compilation_source_reuse import _form_groups, _identity, _role

    if data.get('generation_revision') != 3 or review.get('blocker') != 'source':
        return None
    try:
        as_of = date.fromisoformat(reference)
    except (TypeError, ValueError):
        return None
    fields = {f['candidate_id']: f for f in data['audit']['fields']}
    field = fields.get(cid, {})
    reuse = field.get('source_reuse') or {}
    if (reuse.get('property') != 'role' or field.get('kind') != 'data'
            or field.get('proposal_grounding') != 'GROUNDED_PROPOSAL'
            or field.get('validation_errors') or cid in blocked_source_fields(data)):
        return None
    groups = [ids for ids, _, _ in _form_groups(data['catalog']) if ids[8] == cid]
    if len(groups) != 1 or reuse.get('selection_candidate_id') != groups[0][0]:
        return None
    name_id, operator_id = groups[0][0], groups[0][9]
    answer = data.get('dialogue', {}).get('answers', {}).get('field:' + name_id, {})
    if (not valid_receipt(data, 'field:' + name_id, answer, name_id)
            or answer.get('value') != reuse.get('subject')
            or answer != reuse.get('selection_receipt')
            or data.get('dialogue', {}).get('answers', {}).get('field:' + cid, {}).get(
                'action') in {'SKIP', 'UNKNOWN', 'REFUSE'}):
        return None
    op = fields.get(operator_id, {})
    fact = data['audit'].get('facts', {}).get(op.get('fact_id') or op.get('proposed_fact_id'), {})
    if fact.get('entity') != 'company' or operator_id in blocked_source_fields(data):
        return None
    operator = op.get('proposed_value', op.get('value'))
    source_map = _allowed_sources(project_id, sources)
    profile = _identity(source_map.values(), reuse['subject'])
    role = _role(source_map.values(), profile, reuse['subject'], operator) if profile else None
    if not role or role[0][0] != field.get('proposed_value'):
        return None
    value, source, quote = role[0]
    if quote != review.get('evidence_quote'):
        return None
    proof = next((e for e in field.get('source_evidence', [])
                  if e.get('chunk_id') == source['chunk_id'] and e.get('quote') == quote), {})
    if proof.get('content_sha256') != hashlib.sha256(source['content'].encode()).hexdigest():
        return None
    # No end date, uncertainty or unparsed qualifier may be discarded here.
    pattern = (r'-\s+\*\*' + re.escape(reuse['subject']) + r'\*\*:\s*\*\*'
               + re.escape(value) + r' della società(?: nello scenario)? dal '
               r'(\d{1,2}) (' + '|'.join(MONTHS) + r') (\d{4})\*\*')
    match = re.fullmatch(pattern, quote.strip(), re.I)
    if not match:
        return None
    try:
        start = date(int(match[3]), MONTHS.index(match[2].lower()) + 1, int(match[1]))
    except ValueError:
        return None
    if start > as_of:
        return None
    date_text = ' '.join(match.groups())
    reason = (f'La carica di {value} risulta attestata solo a partire dal {date_text}, '
              'mentre il ruolo richiesto nel modulo è quello attuale del sottoscrittore.')
    if (_text(review.get('reason', '')) != _text(reason)
            or _text(review.get('missing_information', '')) != _text(MISSING)):
        return None  # Other/mixed doubts are not a closed calendar contradiction.
    # Re-read all authorised SOURCE, not just the cited positive span. Extra named role
    # assertions, revocations and uncertain statuses defeat this bounded proof.
    subject = _text(reuse['subject'])
    for item in source_map.values():
        for line in item['content'].splitlines():
            text = _text(line)
            if subject not in text:
                continue
            if re.search(r'\b(?:cessat\w*|revocat\w*|scadut\w*|sospes\w*|ex|forse)\b|'
                         r'\bnon\b.{0,40}\b(?:ricopr\w*|rivest\w*|rappresent\w*|'
                         r'amministr\w*|attual\w*|in essere)\b', text):
                return None
            if (_text(value) in text or re.match(r'-\s*' + re.escape(subject) + r'\s*:', text)):
                if not text.startswith(_text(quote)):
                    return None
    return {'revision': 1, 'candidate_id': cid, 'subject': reuse['subject'],
            'role': value, 'operator': operator, 'start_date': start.isoformat(),
            'reference_date': as_of.isoformat(), 'comparison': 'start_not_after_reference',
            'source_evidence': proof, 'selection_receipt': answer,
            'source_corpus_digest': request_digest([
                {k: s.get(k) for k in ('chunk_id', 'file_id', 'role', 'scope', 'project_id',
                                      'category', 'content')}
                for _, s in sorted(source_map.items())])}


def validate_releases(data, selected, sources, project_id):
    """A persisted dismissal of a MODEL date claim is not a permanent export waiver."""
    from fastapi import HTTPException

    records = (data.get('dialogue') or {}).get('hold_records', {})
    for cid in selected:
        record = records.get(cid, {})
        if record.get('reason_validation') != 'REJECTED_TEMPORAL_COMPARISON':
            continue
        saved = record.get('temporal_comparison') or {}
        current = comparison_proof(data, cid, record, sources, project_id,
                                   saved.get('reference_date'))
        if not current or current != saved or record.get('status') != 'released':
            raise HTTPException(409, 'Prova temporale della carica cambiata o non verificabile')
