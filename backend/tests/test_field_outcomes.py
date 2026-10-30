"""Each empty documented field has one structured reason (stabilization, 30 Oct).

The E2E campaign could tell why values were lost only by reading narrator messages and
receipts by hand. The draft report now records, per field, the first stage that stopped it,
from backend state only. Synthetic FORM.
"""

from test_documented_conditions_not_skipped import case
from test_signatory_hold_shared_clause import OPERATOR

from app.compilation_field_outcomes import field_outcomes


def outcome(data, written=()):
    return field_outcomes(data, set(written))["campi"][OPERATOR]["esito"]


def test_each_stage_has_its_own_outcome():
    data = case()
    assert outcome(data) == "condizione_aperta"
    assert outcome(data, {OPERATOR}) == "scritto"
    data["dialogue"]["unaccepted_attempts"] = {"condition:c_firm": 1}
    assert outcome(data) == "rifiuto_guardia"
    data["dialogue"]["answers"]["condition:c_firm"] = {"action": "SKIP", "provenance": "USER"}
    assert outcome(data) == "rinvio_USER"
    data["dialogue"]["held_candidate_ids"] = [OPERATOR]
    data["dialogue"]["hold_records"] = {OPERATOR: {"blocker": "source"}}
    entry = field_outcomes(data, set())["campi"][OPERATOR]
    assert entry["esito"] == "sospeso_narratore" and entry["blocker"] == "source"
    data["dialogue"]["answers"]["condition:c_firm"] = {"action": "CONDITION_FALSE",
                                                       "applies": False, "provenance": "USER"}
    assert outcome(data) == "escluso_USER"


def test_the_summary_counts_every_outcome():
    summary = field_outcomes(case(), set())["riepilogo"]
    assert summary.get("condizione_aperta", 0) >= 1 and sum(summary.values()) >= 1
