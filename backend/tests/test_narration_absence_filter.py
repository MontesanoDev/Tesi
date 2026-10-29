"""The initial summary keeps what the model found and drops only its claims of absence.

Attempt 03: any «non», «nessun», «manca» replaced the whole initial summary with a generic
text, although only one sentence claimed something absent from the sources. A model
explanation still cannot certify absence: those sentences are removed, the rest stays, and
the caveat says that a missing proposal does not prove absence.
"""

import pytest

from app.compilation_global_dialogue import ABSENCE_CAVEAT, absence_safe_message

FOUND = ("Ho trovato i dati anagrafici e societari della società (sede a Bari, P.IVA e "
         "riferimenti dello studio) e i nominativi del direttore tecnico.")
OPEN = ("Restano però da chiarire alcune scelte di fondo: la qualità con cui si partecipa e "
        "le categorie e fasce d'incarico da indicare, che non risultano dalle fonti.")
STATUS = "Le proposte dipendenti da rami non confermati restano sospese."
ATTEMPT_03 = " ".join([FOUND, OPEN,
                       "Per il direttore tecnico non ho proposte accettate: i dati di iscrizione "
                       "all'albo non sono trasferibili da altri soggetti.", STATUS])


def test_attempt_03_summary_keeps_found_data_and_drops_the_absence_claim():
    message = absence_safe_message(ATTEMPT_03)
    assert message.startswith(FOUND) and STATUS in message
    assert "non risultano dalle fonti" not in message and "trasferibili" not in message
    assert message.endswith(ABSENCE_CAVEAT)


@pytest.mark.parametrize("claim", [
    "Il codice fiscale non risulta nelle fonti.",
    "Non ho trovato la PEC della società.",
    "Mancano i dati del direttore tecnico.",
    "Nessun documento indica la sede operativa.",
    "Le fonti non contengono la data di iscrizione all'albo.",
    "Il numero REA è assente dai documenti caricati.",
])
def test_absence_claims_are_removed(claim):
    message = absence_safe_message(f"{FOUND} {claim}")
    assert claim not in message and message == f"{FOUND} {ABSENCE_CAVEAT}"


@pytest.mark.parametrize("lawful", [
    FOUND,
    "Ho preparato le proposte verificabili per la società e per l'Ing. Rossi.",
    "Restano da confermare la qualità di partecipazione e le categorie d'incarico.",
])
def test_messages_without_absence_claims_are_unchanged(lawful):
    assert absence_safe_message(lawful) == lawful


def test_status_negation_without_a_presence_claim_is_kept_verbatim():
    assert absence_safe_message(f"{FOUND} {STATUS}") == f"{FOUND} {STATUS}"


def test_only_absence_claims_fall_back_to_the_generic_summary():
    message = absence_safe_message("Non ho trovato i dati del firmatario. Mancano le fonti.")
    assert message.startswith("Ho conservato le proposte verificabili.")
    assert ABSENCE_CAVEAT in message and "firmatario" not in message


def test_abbreviations_do_not_split_a_claim_into_an_innocent_half():
    claim = "Per l'Ing. Elisa Romano non risulta nelle fonti la sezione dell'albo."
    message = absence_safe_message(f"{FOUND} {claim}")
    assert "Elisa Romano" not in message and "Ing." not in message.removeprefix(FOUND)
