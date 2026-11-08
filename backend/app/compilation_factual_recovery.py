"""V13 bounded recovery of factual proposals, never authorization or composition.

The MODEL response, literal facts, bindings and UNKNOWN conditions stay intact.
Use existing validators and record joins; FORM owns each physical property.
Historical sessions without backend_revision=13 retain the V12 behaviour.
"""

import re
from collections import Counter
from copy import deepcopy

from app.compilation_attribution import check_source_target
from app.compilation_global import _binding_check, _form_bindings, _role_contexts
from app.compilation_role_records import _property, _text
from app.compilation_sessions import validate_value

ROLE_FAILURE = ("SOURCE non attribuisce esplicitamente ruolo e soggetto "
                "nello stesso chunk del valore")
OWNER_FAILURE = "Continuità FORM senza operatore verificato"
EXPLICIT_PERSON_ROLE = re.compile(
    r"\b(?:vice\s+direttore\s+tecnico|direttore\s+tecnico|socio|associato|"
    r"amministratore(?:\s+unico)?|rappresentante\s+legale|legale\s+rappresentante|"
    r"procuratore|sottoscritt[oa]|firmatari[oa]|responsabile\s+della\s+progettazione|"
    r"professionista\s+(?:designato|incaricato))\b", re.I)


def blocked_conditions(data, audit, conditions):
    answers = (data.get('dialogue') or {}).get('answers', {})
    return any(audit.get('conditions', {}).get(key, {}).get('result') == 'false'
               or answers.get('condition:' + key, {}).get('applies') is False
               for key in conditions)


def _same_form_role(candidate, binding, paragraphs):
    required = _text(binding.get('required_role', ''))
    form = binding.get('form_evidence') or {}
    if not required or not re.search(r'(?<!\w)' + re.escape(required) + r'(?!\w)',
                                     _text(form.get('quote', ''))):
        return False
    paragraph = paragraphs.get(candidate.get('context_id'), {})
    marker = '[[' + candidate.get('id', '') + ']]'
    prefix = (candidate.get('slot_context') or {}).get('before', '')
    if marker in paragraph.get('text_with_fields', ''):
        prefix = paragraph['text_with_fields'].split(marker)[0]
    roles = list(EXPLICIT_PERSON_ROLE.finditer(prefix))
    return not roles or _text(roles[-1][0]) == required


def canonical_property(value):
    prop = _property(value)
    return {"nomecompleto": "nome", "nomeecognome": "nome",
            "sezioneordine": "sezione", "sezionealbo": "sezione",
            "provinciaordine": "provincia", "provinciaalbo": "provincia",
            "numeroiscrizioneordine": "numeroiscrizione",
            "numeroiscrizionealbo": "numeroiscrizione",
            "codicefiscalepersonale": "codicefiscale",
            "dataiscrizionealbo": "iscrizionedal"}.get(prop, prop)


def form_property(candidate, paragraphs):
    """Typed local labels, never the MODEL label or arbitrary table proximity."""
    paragraph = paragraphs.get(candidate.get("context_id"), {})
    prefix = (candidate.get("slot_context") or {}).get("before", "").strip(" ,:;")
    if not prefix or not paragraph:
        return None
    registration = bool(re.search(r"\b(?:ordine|collegio|albo)\b", paragraph["text"], re.I))
    for prop, pattern in [
        ("nome", r"(?:nome\s+e\s+cognome|nominativo)$"),
        ("qualificaprofessionale", r"qualifica\s+professionale$"),
        ("codicefiscale", r"(?:C\.?\s*F\.?|codice\s+fiscale(?:\s+personale)?)$"),
        ("ordineprofessionale", r"(?:Ordine(?:/Collegio)?|Collegio|albo)\s+professionale$"),
    ]:
        if re.search(pattern, prefix, re.I):
            return prop
    if registration:
        for prop, pattern in [("sezione", r"\bsezione$"),
                              ("provincia", r"\bprovincia\s+di$"),
                              ("iscrizionedal", r"\bdal$"),
                              ("numeroiscrizione", r"\b(?:con\s+il\s+)?(?:n\.|numero)$")]:
            if re.search(pattern, prefix, re.I):
                return prop
    return None


def _grounded(field):
    return (field.get('validation') == 'GROUNDED_PROPOSAL' or
            field.get('proposal_grounding') == 'GROUNDED_PROPOSAL')


def recover(data, audit, layout, project_id, sources):
    """Pure derivation; actual review/conditions/applicability remain downstream."""
    result = deepcopy(audit)
    if data.get('backend_revision') != 13 or result.get('version') != 12:
        return result
    catalog = data['catalog']
    if any(not c.get('location', {}).get('block_id') for c in catalog['candidates'].values()):
        return result  # Incomplete structural evidence cannot support a new recovery.
    paragraphs = {p['id']: p for b in catalog['blocks'] for p in b['paragraphs']}
    _, local = _form_bindings(catalog)
    contexts = _role_contexts(catalog, local, continuations=True)
    fields = {f['candidate_id']: f for f in result['fields']}
    recovered = dict(result.get('factual_recovery', {}).get('fields', {}))
    for cid, field in fields.items():
        if (_grounded(field) or cid not in data['writable_ids'] or
                cid in (data.get('dialogue') or {}).get('user_values', {}) or
                blocked_conditions(data, result, field.get('conditions', []))):
            continue
        proposal = field.get('proposal') or {}
        fact = result.get('facts', {}).get(proposal.get('fact_id'), {})
        if (proposal.get('disposition') not in {'value', 'conditional'} or
                fact.get('validation') != 'GROUNDED_PROPOSAL' or
                field.get('alternatives') or proposal.get('alternative_fact_ids') or
                (field.get('source_target_check') or {}).get('result') == 'rejected'):
            continue
        errors = field.get('validation_errors', [])
        method, details = None, None
        if errors == [ROLE_FAILURE] and fact.get('entity') == 'person':
            expected = form_property(catalog['candidates'][cid], paragraphs)
            if expected != canonical_property(fact.get('property', '')):
                continue
            binding = result.get('bindings', {}).get(proposal.get('binding_id'), {})
            if (binding.get('validation') != 'GROUNDED_PROPOSAL' or not _same_form_role(
                    {**catalog['candidates'][cid], 'id': cid}, binding, paragraphs)):
                continue
            check = _binding_check(proposal.get('binding_id'), fact, cid, contexts,
                result['bindings'], sources, personal_records=True,
                evidence_recovery=True, verified_properties=True)
            if check['result'] != 'literal_match' or check['validation_errors']:
                continue
            method, details = 'typed_verified_person_records', check
        elif errors == [OWNER_FAILURE]:
            original = (field.get('destination_check') or {}).get('recovery', {})
            owner_id = original.get('owner_candidate_id')
            owner = fields.get(owner_id, {})
            owner_proposal = owner.get('proposal') or {}
            owner_fact = result['facts'].get(owner.get('fact_id') or owner.get(
                'proposed_fact_id') or owner_proposal.get('fact_id'), {})
            if (original.get('method') != 'adjacent_operator_location' or not _grounded(owner)
                    or blocked_conditions(data, result, owner.get('conditions', []))
                    or any(c.get('result') == 'false'
                           for c in owner.get('condition_checks', {}).values())
                    or owner_fact.get('validation') != 'GROUNDED_PROPOSAL'
                    or owner_fact.get('entity') != 'company' or fact.get('entity') != 'company'
                    or _text(owner_fact.get('subject', '')) != _text(fact.get('subject', ''))
                    or _text(owner_fact.get('subject', '')) != _text(owner_fact.get('value', ''))):
                continue
            method = 'grounded_conditional_operator_continuity'
            details = {'owner_candidate_id': owner_id, 'FORM': deepcopy(original),
                       'owner_SOURCE': deepcopy(owner_fact.get('source_evidence', [])),
                       'owner_conditions_preserved': deepcopy(owner.get('condition_checks', {}))}
        if method is None:
            continue
        target = check_source_target(cid, catalog, fact)
        if target['validation_codes'] or not fact.get('source_evidence'):
            continue
        proof = fact['source_evidence'][0]
        checked = validate_value(layout, {'id': cid, 'label': field['label'],
            'entity': fact['entity']}, fact['value'], sources[proof['chunk_id']], proof['quote'])
        if checked['validation_codes'] or checked['written_value'] != fact['value']:
            continue
        recovered[cid] = {'method': method, 'original_validation_errors': list(errors),
                          'proof': deepcopy(details)}
        if method == 'typed_verified_person_records':
            field['subject_binding'] = details
        field.update(validation='REVIEW_REQUIRED', proposal_grounding='GROUNDED_PROPOSAL',
                     proposed_value=fact['value'], proposed_fact_id=proposal['fact_id'],
                     value=None, written_value=None, validation_errors=[],
                     source_evidence=deepcopy(fact['source_evidence']),
                     factual_recovery=deepcopy(recovered[cid]),
                     coverage={'state': 'PROPOSED', 'origin': 'BACKEND',
                               'reason': 'Recupero fattuale V13 con prove verificabili'})
    result['factual_recovery'] = {'backend_revision': 13, 'fields': recovered,
                                 'MODEL_conditions_and_proposals_unchanged': True}
    result['counts'] = dict(Counter(f['validation'] for f in result['fields']))
    result['binding_checks'] = dict(Counter(f['subject_binding']['result']
        for f in result['fields'] if 'subject_binding' in f))
    return result
