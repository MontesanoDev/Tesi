"""Observable holds; explicit bounded reassessment never replaces SOURCE gates."""

import copy
import json

import pytest
from test_compilation_branch_evidence import case

from app import compilation_global_dialogue as dialogue
from app.compilation_branch_evidence import reconcile_branches
from app.config import AISettings


@pytest.fixture
def anyio_backend():
    return "asyncio"


def prepared():
    data, layout, sources = case()
    data["audit"] = reconcile_branches(data, layout, "alpha", sources)
    return data


@pytest.fixture
def transport(monkeypatch):
    calls = []
    replies = []
    monkeypatch.setattr(
        dialogue,
        "get_ai_settings",
        lambda: AISettings(api_key="simulated", model="offline", base_url="https://invalid"),
    )

    async def request(client, settings, body, timeout, **kwargs):
        context = json.loads(body["messages"][1]["content"])
        calls.append(context)
        return json.dumps(replies.pop(0)), "simulated", {}

    monkeypatch.setattr(dialogue, "request_model_content", request)
    return calls, replies


def note(decision="hold", **changes):
    return {
        "proposal_slot": 2,
        "decision": decision,
        "blocker": "applicability",
        "reason": "Verifica della condizione documentale del responsabile.",
        "missing_information": "Applicabilità del ramo" if decision == "hold" else "",
        "condition_slot": 2,
        "evidence_quote": "la quale ha come Responsabile Tecnico (per le società di ingegneria) "
        "o Responsabile Progettazione (per le società di professionisti):",
        **changes,
    }


def plan(*reviews, held=()):
    return {"questions": [], "held_proposal_slots": list(held), "hold_reviews": list(reviews)}


def redundant_note(**changes):
    return note(missing_information="Conferma del ruolo attuale di Responsabile Tecnico", **changes)


def test_context_carries_true_condition_complete_proof_and_separate_user_skip():
    data = prepared()
    original = copy.deepcopy(data)
    context = dialogue.model_context(data, [])
    technical = context["applicability_contexts"][1]
    assert technical["result"] == "true" and technical["user_receipt"]["action"] == "SKIP"
    assert (
        technical["branch_evidence"] == data["audit"]["conditions"]["technical"]["branch_evidence"]
    )
    assert technical["branch_evidence"]["subject"] == "Nora Serra"
    assert context["document_values"][1]["applicability_slots"] == [1, 2]
    assert context["document_values"][1]["conditional"] is False
    assert data == original


@pytest.mark.anyio
async def test_new_confirmed_inherited_holds_are_distinct(transport, tmp_path):
    data = prepared()
    calls, replies = transport
    replies.append(plan(note(), held=[2]))
    data["dialogue"] = await dialogue.narrate(data, tmp_path)
    review = data["dialogue"]["hold_transition"]
    assert review["new"] == ["p6.s0"] and not review["inherited"] and not review["confirmed"]
    assert data["dialogue"]["hold_records"]["p6.s0"]["reason_status"] == "recorded"
    data["dialogue"]["reviewed_candidate_ids"].remove("p6.s0")
    # One current proposal: local slots are reconstructed, never reused as IDs.
    replies.append(plan(note(proposal_slot=1), held=[1]))
    data["dialogue"] = await dialogue.narrate(data, tmp_path)
    assert data["dialogue"]["hold_transition"]["confirmed"] == ["p6.s0"]
    replies.append(plan())
    data["dialogue"] = await dialogue.narrate(data, tmp_path)
    assert data["dialogue"]["hold_transition"]["inherited"] == ["p6.s0"]
    assert not data["dialogue"]["hold_transition"]["confirmed"]
    assert data["dialogue"]["held_candidate_ids"] == ["p6.s0"]
    assert calls[-1]["document_values"] == []


@pytest.mark.anyio
async def test_legacy_unexplained_holds_are_preserved_not_given_an_invented_reason(
    transport, tmp_path
):
    data = prepared()
    transport[1].append({"questions": [], "held_proposal_slots": [2]})
    result = await dialogue.narrate(data, tmp_path)
    assert result["held_candidate_ids"] == ["p6.s0"]
    assert result["hold_records"]["p6.s0"]["reason_status"] == "not_recorded"
    assert not result["hold_records"]["p6.s0"].get("reason")


@pytest.mark.anyio
async def test_only_proven_redundant_confirmation_is_rejected_without_changing_facts(
    transport,
    tmp_path,
):
    data = prepared()
    data["dialogue"]["held_candidate_ids"] = ["p6.s0"]
    original = copy.deepcopy(data)
    transport[1].append(plan(redundant_note(), held=[2]))
    result = await dialogue.narrate(data, tmp_path)
    assert result["held_candidate_ids"] == [] and result["hold_transition"]["released"] == ["p6.s0"]
    assert result["hold_records"]["p6.s0"]["status"] == "released"
    assert result["hold_transition"]["model_confirmed"] == ["p6.s0"]
    assert result["hold_records"]["p6.s0"]["decision"] == "hold"
    assert (
        result["hold_records"]["p6.s0"]["reason_validation"]
        == "REJECTED_REDUNDANT_ROLE_CONFIRMATION"
    )
    assert data == original
    assert result["answers"] == original["dialogue"]["answers"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "change",
    [
        "unknown",
        "no_branch_proof",
        "other_condition",
        "bad_quote",
        "unresolved_other_condition",
        "source_rejected",
        "wrong_subject",
        "user_denied",
        "user_field_deferred",
        "declaration",
        "previous_source_blocker",
        "condition_refused",
        "previous_user_blocker",
        "missing_different_information",
        "missing_different_role",
        "source_blocker",
        "outside_condition_scope",
        "previous_different_applicability_requirement",
    ],
)
async def test_unresolved_or_unrelated_requirement_cannot_be_released(transport, tmp_path, change):
    data = prepared()
    data["dialogue"]["held_candidate_ids"] = ["p6.s0"]
    field = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p6.s0")
    review = redundant_note()
    if change == "unknown":
        data["audit"]["conditions"]["technical"]["result"] = "unknown"
        field["condition_checks"]["technical"]["result"] = "unknown"
    elif change == "no_branch_proof":
        data["audit"]["conditions"]["technical"].pop("branch_evidence")
    elif change == "other_condition":
        review["condition_slot"] = 1
    elif change == "bad_quote":
        review["evidence_quote"] = "Un consenso mai fornito"
    elif change == "unresolved_other_condition":
        data["dialogue"]["answers"].pop("condition:company")
    elif change == "source_rejected":
        field.update(proposal_grounding=None, validation="REJECTED")
    elif change == "wrong_subject":
        data["audit"]["conditions"]["technical"]["branch_evidence"]["subject"] = "Altra Persona"
    elif change == "user_denied":
        data["dialogue"]["answers"]["condition:technical"].update(
            action="CONDITION_FALSE", applies=False
        )
    elif change == "user_field_deferred":
        data["dialogue"]["answers"]["field:p6.s0"] = {"action": "SKIP", "provenance": "USER"}
    elif change == "declaration":
        field["kind"] = "declaration"
    elif change == "previous_source_blocker":
        data["dialogue"]["hold_records"] = {
            "p6.s0": {
                "status": "held",
                "blocker": "source",
                "reason_status": "recorded",
                "reason": "Ruolo cessato nella SOURCE",
            }
        }
    elif change == "condition_refused":
        data["dialogue"]["answers"]["condition:technical"]["action"] = "REFUSE"
    elif change == "previous_user_blocker":
        data["dialogue"]["hold_records"] = {"p6.s0": {"blocker": "user_decision", "status": "held"}}
    elif change == "missing_different_information":
        review["missing_information"] = "Data della nomina ancora da dimostrare"
    elif change == "missing_different_role":
        review["missing_information"] = "Conferma del ruolo attuale di Rappresentante legale"
    elif change == "outside_condition_scope":
        data["audit"]["conditions"]["technical"]["applies_to"] = ["p3.s0"]
    elif change == "previous_different_applicability_requirement":
        data["dialogue"]["hold_records"] = {
            "p6.s0": {"blocker": "applicability", "status": "held",
                      "missing_information": "Data della nomina non dimostrata"}
        }
    elif change == "source_blocker":
        review["blocker"] = "source"
    transport[1].append(plan(review, held=[2]))
    result = await dialogue.narrate(data, tmp_path)
    assert not result.get("hold_transition", {}).get("released")
    assert "p6.s0" in result.get("held_candidate_ids", [])


@pytest.mark.anyio
async def test_false_new_hold_is_not_introduced_only_for_exact_proved_requirement(
    transport, tmp_path
):
    data = prepared()
    transport[1].append(plan(redundant_note(), held=[2]))
    result = await dialogue.narrate(data, tmp_path)
    assert not result["held_candidate_ids"]
    assert result["hold_transition"]["suppressed_new"] == ["p6.s0"]


@pytest.mark.anyio
async def test_silent_model_release_is_not_an_authorization(transport, tmp_path):
    data = prepared()
    data["dialogue"]["held_candidate_ids"] = ["p6.s0"]
    transport[1].append(plan(note("release")))
    result = await dialogue.narrate(data, tmp_path)
    assert result.get("error") and result["held_candidate_ids"] == ["p6.s0"]


@pytest.mark.anyio
async def test_empty_hold_list_does_not_release_previous_protection(transport, tmp_path):
    data = prepared()
    data["dialogue"]["held_candidate_ids"] = ["p6.s0"]
    transport[1].append(plan())
    result = await dialogue.narrate(data, tmp_path)
    assert result["held_candidate_ids"] == ["p6.s0"] and not result["hold_transition"]["released"]


def test_new_llm_contract_requests_reasons_without_rewriting_old_output():
    schema = dialogue.narration_schema(dialogue.ContinuationPlan, [])
    assert "hold_reviews" in schema["required"]
