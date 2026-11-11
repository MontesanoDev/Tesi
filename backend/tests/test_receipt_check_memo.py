"""One check of the receipts reads one frozen state: same outcome, without one derivation per field.

Real Minervino dialogue: a confirmation covering about ninety fields made every session read cost
hundreds of scope derivations and a draft turn more than the ninety seconds of the chat timeout.
"""

import test_repeated_confirmation as base

from app import compilation_scope_review as scope


def naive(data, monkeypatch, **kwargs):
    original = scope.valid_receipt
    with monkeypatch.context() as patch:
        patch.setattr(scope, "valid_receipt",
                      lambda d, key, receipt, cid, memo=None: original(d, key, receipt, cid))
        return scope.blocked_source_fields(data, **kwargs)


def under_condition(data):
    return {f["candidate_id"] for f in data["audit"]["fields"]
            if "seg1" in f.get("conditions", [])}


def test_the_same_fields_are_blocked_with_or_without_the_memo(monkeypatch):
    data, _ = base.case()
    for linked in (False, True):
        kept = scope.blocked_source_fields(data, linked_user_controls=linked)
        assert kept == naive(data, monkeypatch, linked_user_controls=linked)


def test_a_stale_receipt_is_still_caught_for_every_field_it_covers(monkeypatch):
    data, _ = base.case()
    receipt = data["dialogue"]["answers"]["condition:seg1"]
    covered = under_condition(data)
    assert covered and covered - scope.blocked_source_fields(data)
    receipt["scope_validation"] = "altro"
    blocked = scope.blocked_source_fields(data)
    assert covered <= blocked and blocked == naive(data, monkeypatch)


def test_a_changed_description_voids_the_receipt_as_before(monkeypatch):
    data, _ = base.case()
    covered = under_condition(data)
    next(f for f in data["audit"]["fields"] if f["candidate_id"] in covered)["label"] = "cambiata"
    blocked = scope.blocked_source_fields(data)
    assert covered <= blocked and blocked == naive(data, monkeypatch)


def test_a_refused_condition_is_not_shared_with_the_others(monkeypatch):
    data, _ = base.case()
    data["dialogue"]["answers"]["condition:seg1"]["applies"] = False
    blocked = scope.blocked_source_fields(data)
    assert blocked == naive(data, monkeypatch)
    assert under_condition(data) <= blocked


def test_one_check_derives_the_targets_once_however_many_fields_a_receipt_covers(monkeypatch):
    data, _ = base.case()
    calls = []
    original = scope.derived_targets
    monkeypatch.setattr(scope, "derived_targets",
                        lambda d: calls.append(1) or original(d))
    scope.blocked_source_fields(data)
    assert len(calls) <= 1
