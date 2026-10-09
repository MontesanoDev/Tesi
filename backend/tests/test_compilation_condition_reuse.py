"""Verified branch facts apply to dependents, not to unrelated subjects/predicates."""

from copy import deepcopy

import pytest

from app.compilation_chat import chat_view, new_cycle
from app.compilation_clarifications import pending_slots, synchronize
from app.compilation_semantics import interpretation_digest


def branch_field(name, condition, *, entity="company", section="branch-a", proof=None,
                 heading=None, role=""):
    heading = heading or f"dati identificativi da compilare in caso di {condition}"
    requirement = {"name": "Nome", "person_role": role, "form_quote": "Nome"}
    semantic = {"section_id": section, "condition_kind": "subject_type",
                "subject_relation": "professional" if entity == "person" else "organization"}
    field = {
        "id": name, "condition": condition, "entity": entity, "requirement": requirement,
        "semantic": semantic, "semantic_validation": {
            "accepted": True, "condition_complete": True,
            "digest": interpretation_digest(requirement, semantic, entity, condition),
        }, "structural": {"form_sections": [{"id": section, "text": heading}]},
        "form_evidence": {"role": "form", "template_sha256": "immutable-original",
                          "project_id": "alpha", "file_id": 7},
        "status": "AMBIGUOUS", "value": None, "provenance": None, "source_evidence": [],
        "label": "Nome", "label_hint": "Nome", "kind": "data", "context": heading,
        "search": {"status": "searched"}, "alternatives": [], "last_attempt_at": None,
        "validation_errors": [],
    }
    if proof is not None:
        field.update(status="NOT_APPLICABLE" if not proof else "PENDING", provenance="USER",
                     applicability={"condition": condition, "applies": proof,
                                    "provenance": "USER", "user_quote": "risposta verificata"})
    return field


def state(*fields):
    return {"fields": list(fields), "status": "WAITING_FOR_USER", "lease_until": None,
            "chat_workflow": new_cycle()}


ROOT = "professionisti associati (studio associato)"
WITH = ROOT + " nel caso di rappresentante munito di idonei poteri"
WITHOUT = ROOT + " in assenza di rappresentante munito di idonei poteri"


def test_verified_parent_denial_reaches_alias_other_sections_and_person_cells():
    decision = branch_field("decision", ROOT, proof=False)
    dependents = [branch_field("name", "STUDIO ASSOCIATO", entity="person", section="other"),
                  branch_field("with", WITH, section="with"),
                  branch_field("without", WITHOUT, entity="person", section="without")]
    s = state(decision, *dependents)
    before = deepcopy(decision)
    synchronize(s)
    assert decision == before
    assert all(f["status"] == "NOT_APPLICABLE" and f["value"] is None for f in dependents)
    assert all(f["applicability"]["condition"] == f["condition"] for f in dependents)
    assert all(f["applicability"]["dependency"]["field_id"] == "decision" for f in dependents)
    assert pending_slots(s) == []


@pytest.mark.parametrize("provenance", ["USER", "SOURCE"])
def test_verified_facts_reused_but_independent_values_never_overwritten(provenance):
    origin = branch_field("decision", ROOT, proof=False)
    origin["applicability"]["provenance"] = provenance
    origin["applicability"]["evidence"] = [{"role": "source", "chunk_id": 12,
                                          "quote": "non è uno studio associato"}]
    kept = branch_field("independent", WITHOUT)
    kept.update(status="RESOLVED", provenance="SOURCE", value="Persona verificata",
                source_evidence=[{"role": "source", "quote": "Persona verificata"}])
    unresolved = branch_field("unresolved", WITHOUT)
    before = deepcopy(kept)
    synchronize(state(origin, kept, unresolved))
    assert {k: v for k, v in kept.items() if k != "write_blockers"} == before
    assert kept["write_blockers"]  # Value retained; uncertain placement now reported.
    assert unresolved["status"] == "NOT_APPLICABLE"
    assert unresolved["applicability"]["provenance"] == provenance


@pytest.mark.parametrize("alter", ["project", "template", "member", "digest", "incomplete"])
def test_no_cross_subject_or_unreviewed_cross_section_inference(alter):
    origin = branch_field("decision", ROOT, proof=False)
    dependent = branch_field("dependent", WITHOUT, section="another")
    if alter == "project":
        dependent["form_evidence"]["project_id"] = "beta"
    elif alter == "template":
        dependent["form_evidence"]["template_sha256"] = "another-original"
    elif alter == "member":
        dependent["structural"]["form_sections"][0]["text"] = (
            f"Dati della consorziata in caso di {WITHOUT}")
    elif alter == "digest":
        dependent["semantic_validation"]["digest"] = "stale"
    else:
        dependent["semantic_validation"]["condition_complete"] = False
    synchronize(state(origin, dependent))
    assert dependent["status"] == "AMBIGUOUS"
    assert not dependent.get("applicability")


def test_true_parent_does_not_decide_qualifiers_and_false_child_does_not_deny_parent():
    parent = branch_field("parent", ROOT, proof=True)
    with_power, without_power = branch_field("with", WITH), branch_field("without", WITHOUT)
    synchronize(state(parent, with_power, without_power))
    assert with_power["status"] == without_power["status"] == "AMBIGUOUS"
    denied_child = branch_field("denied-child", WITH, proof=False)
    undecided_parent, other_child = branch_field("root", ROOT), branch_field("other", WITHOUT)
    synchronize(state(denied_child, undecided_parent, other_child))
    assert undecided_parent["status"] == other_child["status"] == "AMBIGUOUS"


def test_true_qualified_branch_excludes_opposite_qualifier_but_not_other_legal_types():
    origin = branch_field("origin", WITH, proof=True)
    parent, opposite = branch_field("parent", ROOT), branch_field("opposite", WITHOUT)
    other_type = branch_field("another", "società di professionisti")
    synchronize(state(origin, parent, opposite, other_type))
    assert parent["applicability"]["applies"] is True
    assert opposite["status"] == "NOT_APPLICABLE"
    assert other_type["status"] == "AMBIGUOUS"


def test_contradictory_verified_facts_leave_dependency_unknown_and_preserve_decisions():
    no = branch_field("no", ROOT, proof=False)
    yes = branch_field("yes", WITH, proof=True)
    dependent = branch_field("dependent", WITHOUT)
    # The contradiction concerns the parent, even when the target has a qualifier.
    parent = branch_field("parent", ROOT)
    before = deepcopy([no, yes])
    synchronize(state(no, yes, parent, dependent))
    assert [no, yes] == before
    assert parent["status"] == "AMBIGUOUS"
    assert dependent["status"] == "AMBIGUOUS"


def test_repeated_branch_questions_deduplicate_cells_then_ask_parent_before_children():
    fields = [branch_field("one", ROOT, entity="person"),
              branch_field("two", "STUDIO ASSOCIATO", section="second"),
              branch_field("child", WITHOUT, section="third")]
    s = state(*fields)
    synchronize(s)
    slots = s["chat_workflow"]["pending_clarifications"]
    assert len(slots) == 1
    assert set(slots[0]["field_ids"]) == {"one", "two"}
    question = chat_view(s)["question"]
    assert len(question["slots"]) == 1 and "1 chiarimenti" not in question["message"]


def test_engineering_value_without_applicability_proof_does_not_deny_other_branches():
    company = branch_field("company", "società di ingegneria")
    company.update(status="RESOLVED", provenance="SOURCE", value="società di ingegneria")
    studio = branch_field("studio", ROOT)
    synchronize(state(company, studio))
    assert studio["status"] == "AMBIGUOUS"


def test_historical_finish_command_is_invalidated_and_cannot_prove_an_exclusion():
    invalid = branch_field("old", "amministratore di fatto", proof=False)
    invalid["applicability"] = {"condition": invalid["condition"], "applies": False,
                                "provenance": "USER",
                                "reason": "Indicazione USER: no, finisci la compilazione"}
    dependent = branch_field("dependent", "amministratore di fatto", section="another")
    verified = branch_field("verified", ROOT, proof=False)
    before = deepcopy(verified)
    s = state(invalid, dependent, verified)
    synchronize(s)
    assert invalid["status"] == dependent["status"] == "AMBIGUOUS"
    assert invalid["invalidated_applicability"]["applies"] is False
    assert not invalid.get("applicability") and not dependent.get("applicability")
    assert verified == before
    once = deepcopy(s)
    synchronize(s)
    assert s == once


def test_parenthetical_qualifiers_are_not_arbitrary_aliases():
    origin = branch_field("origin", "società di ingegneria (società controllata)", proof=False)
    dependent = branch_field("dependent", "società controllata")
    synchronize(state(origin, dependent))
    assert dependent["status"] == "AMBIGUOUS"


@pytest.mark.parametrize("evidence", [[], [{"role": "form", "quote": "studio associato"}]])
def test_missing_or_form_evidence_cannot_propagate_source_condition(evidence):
    origin = branch_field("origin", ROOT, proof=False)
    origin["applicability"].update(provenance="SOURCE", evidence=evidence)
    dependent = branch_field("dependent", WITHOUT)
    synchronize(state(origin, dependent))
    assert dependent["status"] == "AMBIGUOUS"


def test_local_representative_and_technical_director_conditions_have_distinct_owners():
    origin = branch_field("origin", "soggetto residente in Italia", entity="person",
                          role="legale rappresentante", proof=False, heading="Persone con poteri")
    director = branch_field("director", origin["condition"], entity="person",
                            role="direttore tecnico", heading="Persone con poteri")
    synchronize(state(origin, director))
    assert director["status"] == "AMBIGUOUS"
