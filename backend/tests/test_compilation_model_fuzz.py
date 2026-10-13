"""Seeded malformed-model fuzzing: reject safely, never leak mapping exceptions."""

import copy
import json
import random

import pytest
from test_compilation_choices import choice_case as generic_case

from app.compilation_global import validate_global_proposal
from app.intents import parse_turn_plan

choice_case = generic_case
SCALARS = [None, True, False, -999, 0, 1.5, "", "sì", "salta", "🧪", "' OR 1=1 --"]


def noise(rng, depth=0):
    if depth == 3 or rng.random() < .6:
        return rng.choice(SCALARS)
    if rng.random() < .5:
        return [noise(rng, depth + 1) for _ in range(rng.randrange(4))]
    return {rng.choice(["id", "quote", "kind", "value", "conditions"]): noise(rng, depth + 1)
            for _ in range(rng.randrange(4))}


@pytest.mark.parametrize("seed", range(24))
def test_seeded_global_output_mutations_are_safe(choice_case, seed):
    rng = random.Random(seed)
    layout, sources, base = choice_case
    for index in range(40):
        payload = copy.deepcopy(base)
        payload.setdefault("clarifications", {})
        target = rng.choice(["fields", "facts", "conditions", "bindings", "choice_groups",
                             "clarifications"])
        if rng.random() < .3:
            payload[target] = noise(rng)
        else:
            key = rng.choice(list(payload[target]) or ["new"])
            record = payload[target].setdefault(key, {})
            if rng.random() < .4:
                payload[target][key] = noise(rng)
            else:
                record[rng.choice(["form", "scope", "fact_ids", "fact_id", "conditions",
                                   "value", "options", "evidence", "property"])] = noise(rng)
        try:
            result = validate_global_proposal(json.dumps(payload), layout, "alpha", sources,
                                              expected_version=11)
        except ValueError:
            continue
        except Exception as exc:
            pytest.fail(f"seed={seed} sample={index} payload={payload!r} exception={exc!r}")
        assert result["resolved"] == result["writes"] == 0


@pytest.mark.parametrize("seed", range(12))
def test_seeded_chat_plan_shapes_are_safe(seed):
    rng = random.Random(seed)
    base = {"intent": "answer_fields", "answer": "", "queries": [], "target": "form",
            "replies": [{"slot": 1, "action": "SKIP", "user_quote": "salta"}]}
    for index in range(40):
        payload = copy.deepcopy(base)
        if rng.random() < .3:
            payload = noise(rng)
        else:
            payload[rng.choice(list(base))] = noise(rng)
        try:
            parse_turn_plan(payload, {1})
        except ValueError:
            continue
        except Exception as exc:
            pytest.fail(f"seed={seed} sample={index} payload={payload!r} exception={exc!r}")


@pytest.mark.parametrize("payload", [None, [], True, 42, "no"])
def test_global_root_must_be_an_object(choice_case, payload):
    with pytest.raises(ValueError):
        validate_global_proposal(json.dumps(payload), choice_case[0], "alpha", choice_case[1])


def test_excessively_nested_global_json_is_rejected(choice_case):
    with pytest.raises(ValueError):
        validate_global_proposal("[" * 10000 + "]" * 10000, choice_case[0], "alpha", choice_case[1])


@pytest.mark.parametrize("bad_value", ["\ud800", float("nan"), float("inf")])
def test_unserializable_model_diagnostics_are_rejected(choice_case, bad_value):
    payload = copy.deepcopy(choice_case[2])
    payload["fields"]["p2.cb0"]["reason"] = bad_value
    with pytest.raises(ValueError):
        validate_global_proposal(json.dumps(payload), choice_case[0], "alpha", choice_case[1],
                                 expected_version=11)
