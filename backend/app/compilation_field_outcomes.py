"""Why each FORM destination was written or left empty: one structured outcome per field.

Private diagnostics stored with the draft report (never sent to the provider, never shown as
model text). The first stage that stopped a value is recorded, from backend state only:
receipts, conditions, holds, validators and the export selection, not the narrator's notes.
"""

from collections import Counter

# Ordered stages: the first that applies explains the empty field.
OUTCOMES = (
    "scritto",  # In the DOCX.
    "escluso_USER",  # A governing condition answered false by the USER.
    "condizione_falsa",  # A governing condition false from SOURCE/FORM.
    "errore_validazione",  # The validator rejected the proposal.
    "dichiarazione_non_autorizzata",  # Printed in a declaration not authorized by the USER.
    "sospeso_narratore",  # Held by the narrator (blocker recorded).
    "rinvio_USER",  # The USER deferred a governing condition or the field itself.
    "rifiuto_guardia",  # A reply to a governing question was refused by the guard.
    "condizione_aperta",  # A governing condition never answered.
    "bloccato_altro_controllo",  # Scope, table, option or completeness gate.
    "non_selezionato",  # Exportable but not in the export selection.
    "nessuna_proposta",  # No documented proposal (absent from SOURCE or model omission).
)


def field_outcomes(data, written, *, selected=()):
    """{candidate_id: {"esito", ...}} plus counts, for documented or USER-answered fields."""
    from app.compilation_global_dialogue import documented_proposal
    from app.compilation_procedural_consent import blocked_fields as unauthorized
    from app.compilation_scope_review import blocked_source_fields

    audit, dialogue = data.get("audit") or {}, data.get("dialogue") or {}
    answers, conditions = dialogue.get("answers", {}), audit.get("conditions", {})
    held, records = set(dialogue.get("held_candidate_ids", [])), dialogue.get("hold_records", {})
    attempts = dialogue.get("unaccepted_attempts", {})
    declared, gated = unauthorized(data), blocked_source_fields(data)
    result = {}
    for field in audit.get("fields", []):
        cid, keys = field["candidate_id"], field.get("conditions", [])
        if not documented_proposal(field) and "field:" + cid not in answers and cid not in written:
            if field.get("disposition") in {"missing", "review"}:
                result[cid] = {"esito": "nessuna_proposta"}
            continue
        state = {c: answers.get("condition:" + c, {}).get("action") or conditions.get(
            c, {}).get("result") for c in keys}
        outcome = (
            "scritto" if cid in written else
            "escluso_USER" if any(answers.get("condition:" + c, {}).get("applies") is False
                                  for c in keys) else
            "condizione_falsa" if any(conditions.get(c, {}).get("result") == "false"
                                      for c in keys) else
            "errore_validazione" if field.get("validation_errors") else
            "dichiarazione_non_autorizzata" if cid in declared else
            "sospeso_narratore" if cid in held else
            "rinvio_USER" if any(answers.get("condition:" + c, {}).get("action") in {
                "SKIP", "UNKNOWN", "REFUSE"} for c in keys) or answers.get(
                "field:" + cid, {}).get("action") in {"SKIP", "UNKNOWN", "REFUSE"} else
            "rifiuto_guardia" if any(attempts.get("condition:" + c) for c in keys
                                     if "condition:" + c not in answers) else
            "condizione_aperta" if any(conditions.get(c, {}).get("result") != "true"
                                       and "condition:" + c not in answers for c in keys) else
            "bloccato_altro_controllo" if cid in gated else
            "non_selezionato")
        entry = {"esito": outcome, "condizioni": state}
        if outcome == "sospeso_narratore":
            record = records.get(cid, {})
            entry.update(blocker=record.get("blocker"), blocker_key=record.get("blocker_key"),
                         reason_validation=record.get("reason_validation"))
        if outcome == "non_selezionato" and cid in selected:
            entry["esito"] = "errore_scrittura"  # Selected for export, absent from the DOCX.
        result[cid] = entry
    return {"riepilogo": dict(Counter(e["esito"] for e in result.values())), "campi": result}
