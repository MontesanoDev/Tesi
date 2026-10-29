"""The initial summary attributes an office to a person only when a grounded binding attests it.

Manual Minervino test 2 (29 Oct): «con amministratore unico Luca Ferri» (an office ceased before
the application date; his grounded binding was «socio») next to the real signatory. Model prose
only; no validator, proposal or receipt depends on this text. Synthetic names.
"""

from app.compilation_global_dialogue import ROLE_CAVEAT, attested_roles, role_safe_message


def data():
    facts = {'f1': {'entity': 'person', 'subject': 'Marta Bianchi', 'property': 'nome'},
             'f2': {'entity': 'person', 'subject': 'Paolo Neri', 'property': 'nome'}}
    bindings = {
        'b_socio': {'validation': 'GROUNDED_PROPOSAL', 'source_role': 'socio',
                    'record_attributions': [{'subject': 'Paolo Neri'}]},
        'b_dt': {'validation': 'GROUNDED_PROPOSAL', 'source_role': 'direttore tecnico',
                 'source_evidence': [{'quote': '### Ing. Marta Bianchi - direttore tecnico'}]},
        'b_rejected': {'validation': 'REJECTED', 'source_role': 'amministratore unico',
                       'record_attributions': [{'subject': 'Paolo Neri'}]}}
    return {'audit': {'facts': facts, 'bindings': bindings, 'fields': []}}


def test_roles_come_only_from_grounded_bindings():
    assert attested_roles(data()) == {'marta bianchi': {'direttore tecnico'},
                                      'paolo neri': {'socio'}}


def test_an_unattested_office_is_dropped_with_the_caveat():
    message = ('Ho trovato i dati della società, con amministratore unico Ing. Paolo Neri; '
               'per Marta Bianchi risultano i dati di iscrizione. Restano da chiarire due scelte.')
    assert role_safe_message(message, data()) == (
        'Per Marta Bianchi risultano i dati di iscrizione. Restano da chiarire due scelte. '
        + ROLE_CAVEAT)


def test_attested_or_role_free_text_is_unchanged():
    for message in ['Marta Bianchi risulta direttore tecnico della società.',
                    'Paolo Neri compare tra i soci; i suoi dati sono proposti.',
                    'Ho trovato sede, partita IVA e contatti della società.',
                    'Il legale rappresentante firmerà la domanda.']:  # No known person named.
        assert role_safe_message(message, data()) == message
