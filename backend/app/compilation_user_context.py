"""Session-bound USER receipts, never inferred facts or automatic field updates."""

import json


def registered_user_context(db, row, state):
    """Read only this session's persisted start requests and accepted decisions.

    Request text is an uninterpreted utterance, not a confirmed participation,
    signatory or factual claim. Assistant answers and unrelated history never
    enter the global analysis. No migration/backfill of historical sessions.
    """
    if state.get("engine") != "global":
        return []
    context = []
    if row["conversation_id"]:
        turns = db.execute(
            "SELECT t.id,t.question,t.compilation_json FROM conversation_turns t "
            "JOIN conversations c ON c.id=t.conversation_id "
            "WHERE c.id=? AND c.project_id=? ORDER BY t.id",
            (row["conversation_id"], row["project_id"]),
        ).fetchall()
        for turn in turns:
            try:
                command = json.loads(turn["compilation_json"] or "null")
            except (ValueError, TypeError):
                continue
            if (not isinstance(command, dict) or command.get("session_id") != row["id"]
                    or command.get("action") != "start"
                    or not isinstance(turn["question"], str) or not turn["question"].strip()):
                continue
            context.append({"kind": "recorded_request", "provenance": "USER",
                            "turn_id": turn["id"], "user_quote": turn["question"]})
    data = state.get("global_compilation") or {}
    audit = data.get("audit") or {}
    fields = {f["candidate_id"] for f in audit.get("fields", [])}
    dialogue = data.get("dialogue") or {}
    for key, answer in dialogue.get("answers", {}).items():
        if (not isinstance(answer, dict) or answer.get("provenance") != "USER"
                or not isinstance(answer.get("user_quote"), str) or not answer["user_quote"].strip()
                or answer.get("action") not in {"VALUE", "CONDITION_TRUE", "CONDITION_FALSE"}):
            continue
        kind, _, target = key.partition(":")
        if kind == "condition":
            if (audit.get("conditions", {}).get(target, {}).get("validation") !=
                    "GROUNDED_PROPOSAL" or
                    answer.get("action") not in {"CONDITION_TRUE", "CONDITION_FALSE"}
                    or answer.get("applies") is not (answer["action"] == "CONDITION_TRUE")):
                continue
        elif kind == "field":
            value = dialogue.get("user_values", {}).get(target, {})
            if (answer.get("action") != "VALUE" or target not in fields
                    or value.get("provenance") != "USER"
                    or value.get("user_quote") != answer["user_quote"]
                    or value.get("value") != answer.get("value")):
                continue
        elif kind == "choice":
            if (audit.get("choice_groups", {}).get(target, {}).get("validation") !=
                    "GROUNDED_GROUP" or
                    answer.get("selected_options") is None or answer.get("action") != "VALUE"):
                continue
        else:
            continue
        context.append({"kind": "registered_decision", "provenance": "USER", "key": key,
                        **{k: answer[k] for k in ["action", "user_quote", "question", "label",
                                                 "value", "applies", "selected_options"]
                           if k in answer}})
    return context
