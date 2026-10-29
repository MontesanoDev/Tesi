"""Short, specific questions: the indispensable FORM lines in the question, the rest as details.

Manual Minervino test (29 Oct): one message carried the 7 capacity options with their legal
references, the whole preferences table (2,846 characters) and all the general declarations
(2,107). The full FORM text is now kept as separate details; nothing is reworded or chosen,
and decisions still never authorize writes.
"""

from app.compilation_global_dialogue import open_condition_questions
from app.compilation_user_decisions import HEAD_CHARS, compact_question

DECLARATIONS = ['☐ che i fatti e le qualità dei paragrafi seguenti corrispondono a verità:',
                *(f'di dichiarare il requisito generale numero {n} previsto dal bando;'
                  for n in range(1, 11))]


def test_a_long_excerpt_keeps_its_first_line_and_moves_the_rest_to_details():
    text, details = compact_question('Quali dichiarazioni puoi confermare espressamente?',
                                     DECLARATIONS)
    assert text.splitlines() == [
        'Quali dichiarazioni puoi confermare espressamente?', DECLARATIONS[0],
        'Seguono altre 10 righe del modulo. Il testo completo è nei dettagli.']
    assert details == DECLARATIONS  # Complete and literal.


def test_an_option_table_is_summarized_with_its_entries_and_columns():
    lines = ['barrare le tipologie interessate (max. 3):', 'Servizi', 'Voce | Lotto 1 | Lotto 2',
             *(f'Servizio {n}: Lotto 1, Lotto 2' for n in range(1, 9))]
    entries = [(f'Servizio {n}', ['Lotto 1', 'Lotto 2']) for n in range(1, 9)]
    text, details = compact_question('Quali servizi scegli?', lines, entries)
    assert text.splitlines()[1:] == [
        'barrare le tipologie interessate (max. 3):',  # The instruction keeps its limit.
        '8 voci, colonne: Lotto 1, Lotto 2. Il testo completo è nei dettagli.']
    assert details == lines


def test_columns_differing_only_by_spaces_are_named_once():
    entries = [('Edilizia', ['Fascia A ', 'Fascia B ']), ('CSP/CSE', ['Fascia A', 'Fascia  B'])]
    lines = ['istruzione:', *(f'riga {n}' for n in range(8))]
    text, _ = compact_question('Quali scegli?', lines, entries)
    assert '2 voci, colonne: Fascia A, Fascia B.' in text


def test_a_short_excerpt_is_unchanged_and_has_no_details():
    text, details = compact_question('Quali luogo e data indichi?', ['Luogo e data, ______'])
    assert text == 'Quali luogo e data indichi?\nLuogo e data, ______' and details == []


def test_a_very_long_first_line_is_cut_at_a_word():
    text, _ = compact_question('Domanda?', ['parola ' * 80, *DECLARATIONS])
    head = text.splitlines()[1]
    assert head.endswith('…') and len(head) <= HEAD_CHARS and not head.endswith(' …')


def test_the_backend_confirmation_quotes_the_clause_without_legal_references():
    pool = [{'slot': 1, 'kind': 'applicability', 'key': 'condition:c1', 'condition':
             '☐ Mandatario di raggruppamento temporaneo (art. 66, comma 1, lett. f) che, ai fini '
             'dell’inserimento nell’elenco, assume la seguente denominazione:'}]
    [question] = open_condition_questions(pool)
    assert question.confirmation == ('si applica al vostro caso quanto indicato nel modulo: '
                                     '«Mandatario di raggruppamento temporaneo»')
