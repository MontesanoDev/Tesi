"""Bounded automatic work and persistent, backend-owned clarification slots."""

from copy import deepcopy

from app.compilation_applicability import known_applicability
from app.compilation_conditions import expression, implication, key, owner, proven_relations

MAX_CLARIFICATIONS = 4
MAX_ANALYSIS_ATTEMPTS = 2


def grouped(state):
    return (state.get("chat_workflow") or {}).get("clarification_mode") == "grouped"


def resolution_phase(field):
    return "source" if field.get("requirement") else "interpretation"


def phase_attempts(state, phase):
    workflow = state.get("chat_workflow") or {}
    if phase == "interpretation":
        return workflow.get("analysis_attempts", {})
    if "source_attempts" in workflow:
        return workflow["source_attempts"]
    # Old snapshots shared a counter: preserve their spent SOURCE budget.
    legacy = workflow.get("analysis_attempts", {})
    return {f["id"]: legacy.get(f["id"], 0) for f in state["fields"]
            if f.get("requirement")}


def reopen_phase_attempts(state, field):
    """A new applicability fact reopens only the phase still needed by this field."""
    phase = resolution_phase(field)
    key = "source_attempts" if phase == "source" else "analysis_attempts"
    state["chat_workflow"].setdefault(key, dict(phase_attempts(state, phase))).pop(
        field["id"], None)


def automatic_fields(state):
    from app.compilation_chat import is_deferred

    def eligible(field):
        return (field["status"] == "PENDING" or (
            field["status"] == "MISSING" and field.get("validation_errors")
            and field.get("requirement") and not is_deferred(field)
            and (not field.get("condition") or known_applicability(field) is True)
        )) and phase_attempts(state, resolution_phase(field)).get(field["id"], 0) \
            < MAX_ANALYSIS_ATTEMPTS

    return sorted((f for f in state["fields"] if eligible(f)),
                  key=lambda f: (not f.get("awaiting_dependency_resolution", False),
                                 resolution_phase(f) != "source",
                                 not bool(f.get("validation_errors") and f["last_attempt_at"]),
                                 not bool(f["label_hint"].strip()),
                                 phase_attempts(state, resolution_phase(f)).get(f["id"], 0),
                                 f["last_attempt_at"] or ""))


def condition_key(field):
    return key(field)


def pending_slots(state):
    from app.compilation_chat import field_fingerprint, field_label, is_deferred
    from app.compilation_form_conditions import question_condition

    slots = {}
    for field in state["fields"]:
        if field["status"] not in {"MISSING", "AMBIGUOUS", "CONFLICTING"} or is_deferred(field):
            continue
        if (field.get("kind", "data") == "data" and (
            not field.get("requirement") or field.get("search", {}).get("status") != "searched"
        )):
            continue  # An interpretation/retrieval not attempted is NOT a USER question.
        condition = question_condition(field)
        if not condition and field.get("validation_errors") and not field.get("alternatives"):
            continue  # A failed check is not evidence that the user lacks this fact.
        kind = "applicability" if condition else "value"
        key = condition_key({**field, "condition": condition}) if kind == "applicability" \
            else field["id"]
        if key not in slots:
            slots[key] = {"kind": kind, "label": field_label(field), "condition": condition,
                          "field_ids": [], "fingerprints": {}, "alternatives": [],
                          "subject": owner({**field, "condition": condition})
                          if kind == "applicability" else (
                              field.get("entity"),
                              (field.get("requirement") or {}).get("person_role", "")),
                          "context": field["context"]}
        slot = slots[key]
        slot["field_ids"].append(field["id"])
        slot["fingerprints"][field["id"]] = field_fingerprint(field)
        slot["alternatives"] = list(dict.fromkeys([
            *slot["alternatives"], *[a["value"] for a in field["alternatives"]],
        ]))
    result = list(slots.values())
    by_id = {f["id"]: f for f in state["fields"]}
    # Ask the explicit parent first. A denial excludes its children; a positive
    # reply still leaves genuinely different qualifiers to be established.
    result = [s for s in result if s["kind"] != "applicability" or not any(
        p["kind"] == "applicability" and owner({**by_id[p["field_ids"][0]],
                                               "condition": p["condition"]})
        == owner({**by_id[s["field_ids"][0]], "condition": s["condition"]})
        and expression(p["condition"])
        < expression(s["condition"]) for p in result
    )]
    for slot in result:
        slot["impact"] = len(slot["field_ids"])
    return sorted(result, key=lambda s: (-s["impact"], s["kind"] != "applicability"))


def clarification_question(state):
    from app.compilation_chat import budget_available
    from app.compilation_document_plan import needs_document_plan

    workflow = state.get("chat_workflow") or {}
    if (workflow.get("user_paused") or workflow.get("paused_reason") == "model_error"
            or state["status"] in {"ANALYZING", "FAILED", "GENERATED"}):
        return None
    if (automatic_fields(state) or needs_document_plan(state)) and budget_available(workflow):
        return None
    pending = pending_slots(state)
    eligible = {field_id: slot for slot in pending for field_id in slot["field_ids"]}
    active = []
    saved = workflow.get("active_clarifications", [])
    if any(i in eligible and (eligible[i]["fingerprints"].get(i) != s["fingerprints"].get(i)
                             or set(eligible[i]["field_ids"]) != set(s["field_ids"]))
           for s in saved for i in s["field_ids"]):
        saved = []  # A changed dependency needs a newly prioritized checkpoint.
    for slot in saved:
        # Stable slot positions across partial replies; never bind a changed field.
        ids = [i for i in slot["field_ids"] if i in eligible
               and eligible[i]["fingerprints"].get(i) == slot["fingerprints"].get(i)]
        if ids:
            active.append({**slot, "field_ids": ids})
    if not active and pending:
        first = pending[0]
        coherent = [s for s in pending if s["kind"] == first["kind"] and (
            s["subject"] == first["subject"] or s["context"] == first["context"]
        )]
        active = [{**slot, "slot": index} for index, slot in enumerate(
            coherent[:MAX_CLARIFICATIONS], 1,
        )]
    if not active:
        return None
    if (len(active) == 1 and len(active[0]["field_ids"]) == 1
            and not next(f for f in state["fields"]
                         if f["id"] == active[0]["field_ids"][0]).get("form_dependency")):
        # Preserve the proven single-active-field semantic contract.
        slot = active[0]
        message = (f"Per «{slot['label']}», il modulo specifica «{slot['condition']}». "
                   "Questa condizione si applica al tuo caso?" if slot["kind"] == "applicability"
                   else f"Mi manca un valore verificato per «{slot['label']}». Qual è?")
        return {"kind": slot["kind"], "field_ids": slot["field_ids"], "message": message,
                "slots": active}
    verified = sum(f["status"] == "RESOLVED" for f in state["fields"])
    lines = []
    for slot in active:
        question = (f"La condizione «{slot['condition']}» si applica al tuo caso?"
                    if slot["kind"] == "applicability" else
                    f"Quale valore devo usare per «{slot['label']}»?")
        if slot["alternatives"] and slot["kind"] == "value":
            question += " Alternative nelle fonti: " + "; ".join(slot["alternatives"])
        if slot.get("clarify"):
            question = f"Per «{slot['label']}» serve un'indicazione univoca. " + question
        lines.append(f"{slot['slot']}. {question}")
    intro = ("Per proseguire, chiarisco questo punto:" if len(active) == 1
             else f"Per proseguire, chiarisco questi {len(active)} punti:")
    return {"kind": "clarifications",
            "field_ids": [i for s in active for i in s["field_ids"]], "slots": active,
            "message": f"Ho compilato {verified} campi con dati verificati nelle fonti. {intro}\n"
                       + "\n".join(lines) + "\nPuoi rispondere anche in un unico messaggio."}


def synchronize(state):
    """Called inside the existing transaction; no new table or in-memory state."""
    from app.compilation_document_plan import attach_document_plan
    from app.compilation_form_conditions import synchronize_form_dependencies

    attach_document_plan(state)

    if not grouped(state):
        synchronize_form_dependencies(state)
        return
    from app.compilation_chat import budget_available, explicit_finish_request

    workflow = state["chat_workflow"]
    from app.compilation_semantics import propagate_section_exclusions

    # Older routing could store the leading 'no' of a finish command as a USER
    # denial. That command proves no predicate. Retain it for audit, not as a fact.
    for field in state["fields"]:
        proof = field.get("applicability") or {}
        quote = proof.get("user_quote") or proof.get("reason", "").removeprefix(
            "Indicazione USER:").strip()
        if (field["status"] == "NOT_APPLICABLE" and field.get("value") is None
                and proof.get("provenance") == "USER" and explicit_finish_request(quote)):
            field["invalidated_applicability"] = field.pop("applicability")
            field.pop("applicability_confirmed", None)
            field.update(status="AMBIGUOUS", provenance=None, source_evidence=[],
                         reason="La richiesta di terminare non dimostra questa condizione.")
    synchronize_form_dependencies(state)
    propagate_section_exclusions(state)
    facts = proven_relations(state["fields"])
    for field in state["fields"]:
        if (field.get("provenance") == "USER" or field["status"] in {"RESOLVED", "USER_PROVIDED"}
                or not field.get("condition") or known_applicability(field) is not None):
            continue
        relation = implication(field, facts)
        if relation is None:
            continue
        applies, origin = relation
        proof = {**origin["applicability"], "condition": field["condition"], "applies": applies,
                 "dependency": {"field_id": origin["id"], "condition": origin["condition"],
                                "rule": "verified_predicate_implication"}}
        field["applicability"] = deepcopy(proof)
        if proof["applies"] is False:
            field.update(status="NOT_APPLICABLE", value=None, provenance=proof["provenance"],
                         source_evidence=deepcopy(proof.get("evidence", [])), alternatives=[])
        elif field["status"] in {"MISSING", "AMBIGUOUS", "CONFLICTING"}:
            field.update(status="PENDING", last_attempt_at=None,
                         awaiting_dependency_resolution=True)
            reopen_phase_attempts(state, field)
    synchronize_form_dependencies(state)
    workflow["pending_clarifications"] = pending_slots(state)
    if state["status"] not in {"ANALYZING", "FAILED", "GENERATED"}:
        if (automatic_fields(state) and budget_available(workflow)
                and not workflow.get("user_paused")):
            state["status"] = "CREATED"
        elif workflow["pending_clarifications"]:
            state["status"] = "WAITING_FOR_USER"
        elif any(f.get("write_blockers") for f in state["fields"]):
            state["status"] = "WAITING_FOR_USER"
        elif not any(f["status"] in {"PENDING", "MISSING", "AMBIGUOUS", "CONFLICTING"}
                     for f in state["fields"]):
            state["status"] = "READY"
    question = clarification_question(state)
    if question:
        workflow["active_clarifications"] = question["slots"]


def active_group(context):
    if not context or not context.get("enabled") or context.get("paused_by_user"):
        return False
    question = context.get("question") or {}
    return question.get("kind") == "clarifications" and bool(question.get("slots"))
