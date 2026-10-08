"""Persistent state, optimistic revisions and exports from one immutable original.

Fields live in a bounded JSON snapshot (the parser allows at most 400 candidates).
Revision events store changed fields before/after, never a second mutable DOCX.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import get_args
from uuid import uuid4

from fastapi import HTTPException

from app.compilation_chat import budget_available, chat_view, field_fingerprint, new_cycle
from app.compilation_clarifications import (
    automatic_fields,
    grouped,
    phase_attempts,
    reopen_phase_attempts,
    resolution_phase,
    synchronize,
)
from app.compilation_session_models import BATCH_SIZE, LEASE_SECONDS, FieldStatus, UserFieldInput
from app.db import connection, touch_project
from app.document_compilation import CompilationSources, validate_proposals
from app.document_compilation_routes import _persist
from app.docx_templates import DocumentInputError, fill_docx, inspect_docx
from app.project_forms import _form_path
from app.repository import create_conversation_record, reload_evidence

UNRESOLVED = {"PENDING", "MISSING", "AMBIGUOUS", "CONFLICTING"}
FIELD_STATUSES = get_args(FieldStatus)


def now() -> str:
    return datetime.now(UTC).isoformat()


def candidate_snapshots(layout, project_id: str, form_id: int, name: str) -> list[dict]:
    snapshots = []

    def append(candidate_id, context, label, location, structural):
        snapshots.append(
            {
                "id": candidate_id,
                "candidate_id": candidate_id,
                "location": location,
                "label": label,
                "label_hint": label,
                "context": context,
                "structural": structural,
                "requirement": None,
                "value": None,
                "status": "PENDING",
                "provenance": None,
                "form_evidence": {
                    "role": "form",
                    "project_id": project_id,
                    "file_id": form_id,
                    "source_name": name,
                    "scope": f"project:{project_id}",
                    "chunk_id": None,
                    "candidate_id": candidate_id,
                    "template_sha256": layout.sha256,
                },
                "source_evidence": [],
                "alternatives": [],
                "validation_errors": [],
                "search": {"status": "not_searched"},
                "reason": "Candidate strutturale non analizzato",
                "updated_at": now(),
                "last_attempt_at": None,
            }
        )

    for table in layout.catalog:
        # Context is structural, not vector-selected. Include the entire table so
        # role/header relationships do not disappear on later rows of a batch.
        context = "\n".join(
            [
                *table["preceding_context"],
                *[" | ".join(cell["text"] for cell in row) for row in table["rows"]],
            ]
        )
        for ri, row in enumerate(table["rows"]):
            for ci, cell in enumerate(row):
                if cell["id"] not in layout.cells:
                    continue
                label = next((c["text"] for c in reversed(row[:ci]) if c["text"].strip()), "")
                if not label and ri > 0:
                    # Blank rows below labels, or ordinary column headers. Physical
                    # XML coordinates still decide the target, never embeddings.
                    preceding = table["rows"][ri - 1]
                    header = table["rows"][0]
                    for labels in (preceding, header):
                        if (
                            ci < len(labels)
                            and all(not c["writable"] for c in labels)
                            and labels[ci]["text"].strip()
                        ):
                            label = labels[ci]["text"]
                            break
                append(
                    cell["id"],
                    context,
                    label,
                    {
                        "kind": "table_cell",
                        "table": table["table"],
                        "row": ri,
                        "column": ci,
                    },
                    {"row": row, "header": table["rows"][0], "signature": cell["signature"]},
                )
    for paragraph in layout.paragraph_catalog:
        context = "\n".join(
            paragraph[key]
            for key in (
                "preceding_context",
                "text",
                "following_context",
            )
        )
        for slot in paragraph["fields"]:
            append(
                slot["id"],
                context,
                paragraph["text"],
                layout.location(slot["id"]),
                {
                    "text_with_fields": paragraph["text_with_fields"],
                    **slot,
                },
            )
    from app.compilation_semantics import enrich_structure

    enrich_structure(layout, snapshots)
    return snapshots


def session_status(fields: list[dict]) -> str:
    states = {field["status"] for field in fields}
    if states & {"MISSING", "AMBIGUOUS", "CONFLICTING"}:
        return "WAITING_FOR_USER"
    return "CREATED" if "PENDING" in states else "READY"


def _row(db, project_id: str, session_id: str):
    row = db.execute(
        "SELECT * FROM compilation_sessions WHERE project_id=? AND id=?",
        (project_id, session_id),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Sessione non trovata nel progetto")
    return row


def payload(row) -> dict:
    state = json.loads(row["state_json"])
    counts = Counter(field["status"] for field in state["fields"])
    return {
        **state,
        "chat": chat_view(state),
        "id": row["id"],
        "project_id": row["project_id"],
        "form_id": row["form_id"],
        "conversation_id": row["conversation_id"],
        "version": row["version"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "summary": {
            "total": len(state["fields"]),
            **{status.lower(): counts[status] for status in FIELD_STATUSES},
        },
        "open_issues": [
            {
                "field_id": f["id"],
                "status": f["status"],
                "label": f["label"],
                "reason": f["reason"],
                "validation_errors": f["validation_errors"],
            }
            for f in state["fields"]
            if f["status"] in UNRESOLVED
        ],
    }


def get_session(project_id: str, session_id: str) -> dict:
    with connection() as db:
        return payload(_row(db, project_id, session_id))


def list_sessions(project_id: str, conversation_id: str | None = None) -> list[dict]:
    with connection() as db:
        if not db.execute("SELECT id FROM projects WHERE id=?", (project_id,)).fetchone():
            raise HTTPException(404, "Progetto non trovato")
        if conversation_id is not None and not db.execute(
            "SELECT id FROM conversations WHERE id=? AND project_id=?",
            (conversation_id, project_id),
        ).fetchone():
            raise HTTPException(404, "Conversazione non trovata nel progetto")
        rows = db.execute(
            "SELECT * FROM compilation_sessions WHERE project_id=? "
            "AND (? IS NULL OR conversation_id=?) ORDER BY updated_at DESC, id DESC",
            (project_id, conversation_id, conversation_id),
        ).fetchall()
        return [
            {
                key: value
                for key, value in payload(row).items()
                if key not in {"fields", "open_issues"}
            }
            for row in rows
        ]


def revisions(project_id: str, session_id: str) -> list[dict]:
    with connection() as db:
        _row(db, project_id, session_id)
        return [
            {
                "version": row["version"],
                "created_at": row["created_at"],
                **json.loads(row["event_json"]),
            }
            for row in db.execute(
                "SELECT * FROM compilation_session_revisions WHERE session_id=? ORDER BY version",
                (session_id,),
            )
        ]


def create_session(
    project_id: str, form_id: int, conversation_id: str | None = None,
    *, start_in_chat: bool = False,
) -> dict:
    # Original + all candidates are committed together. No output, indexing or LLM.
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        form = db.execute(
            "SELECT * FROM project_files WHERE id=? AND project_id=? AND kind='form'",
            (form_id, project_id),
        ).fetchone()
        if form is None:
            raise HTTPException(404, "Modulo non trovato nel progetto")
        if Path(form["name"]).suffix.lower() != ".docx":
            raise HTTPException(415, "La sessione richiede un originale DOCX")
        if (
            conversation_id is not None
            and not db.execute(
                "SELECT id FROM conversations WHERE id=? AND project_id=?",
                (conversation_id, project_id),
            ).fetchone()
        ):
            raise HTTPException(404, "Conversazione non trovata nel progetto")
        if start_in_chat and conversation_id is None:
            conversation_id = create_conversation_record(
                db, project_id, f"Compilazione {form['name']}",
            )["id"]
        if conversation_id is not None:
            existing = db.execute(
                "SELECT * FROM compilation_sessions "
                "WHERE project_id=? AND conversation_id=? AND form_id=? "
                "ORDER BY updated_at DESC, id DESC LIMIT 1",
                (project_id, conversation_id, form_id),
            ).fetchone()
            # BEGIN IMMEDIATE serializes starts, preserving any historical duplicates.
            if start_in_chat:
                db.execute(
                    "UPDATE conversations SET selected_form_id=?, updated_at=CURRENT_TIMESTAMP "
                    "WHERE id=? AND project_id=?", (form_id, conversation_id, project_id),
                )
                touch_project(db, project_id)
            if existing:
                existing_state = json.loads(existing["state_json"])
                if start_in_chat and (not budget_available(existing_state.get("chat_workflow"))
                                      or existing_state["status"] == "FAILED"
                                      or chat_view(existing_state)["paused"]):
                    check_revision(existing, existing["version"])
                    existing_state["chat_workflow"] = new_cycle(existing_state.get("chat_workflow"))
                    if existing_state["status"] in {"FAILED", "ANALYZING"}:
                        existing_state["status"] = session_status(existing_state["fields"])
                    existing_state.update(lease_until=None, last_error=None)
                    return save_state(db, existing, existing_state, "chat_resume")
                return payload(existing)
        original = _form_path(project_id, form["storage_path"]).read_bytes()
        layout = inspect_docx(original)
        session_id, timestamp = uuid4().hex, now()
        state = {
            "chat_workflow": new_cycle() if start_in_chat else None,
            "status": "CREATED",
            "template_name": form["name"],
            "template_sha256": layout.sha256,
            "original_file_id": form_id,
            "original_storage_path": form["storage_path"],
            "fields": candidate_snapshots(layout, project_id, form_id, form["name"]),
            "unsupported_locations": layout.unsupported_locations,
            "last_generation": None,
            "last_error": None,
            "lease_until": None,
            "last_resolution": None,
        }
        db.execute(
            "INSERT INTO compilation_sessions "
            "(id,project_id,form_id,conversation_id,original,state_json,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                session_id,
                project_id,
                form_id,
                conversation_id,
                original,
                json.dumps(state),
                timestamp,
                timestamp,
            ),
        )
        db.execute(
            "INSERT INTO compilation_session_revisions VALUES (?,?,?,?)",
            (
                session_id,
                1,
                json.dumps({"action": "create", "template_sha256": layout.sha256}),
                timestamp,
            ),
        )
        return payload(_row(db, project_id, session_id))


def check_revision(row, version: int, *, allow_busy: bool = False) -> dict:
    if row["version"] != version:
        raise HTTPException(409, "Versione superata: rileggi la sessione prima di modificarla")
    state = json.loads(row["state_json"])
    if (
        not allow_busy
        and state["status"] == "ANALYZING"
        and (state["lease_until"] and state["lease_until"] > now())
    ):
        raise HTTPException(409, "Risoluzione già in corso")
    return state


def save_state(db, row, state: dict, action: str) -> dict:
    synchronize(state)
    before = {f["id"]: f for f in json.loads(row["state_json"])["fields"]}
    changes = [
        {"field_id": f["id"], "before": before[f["id"]], "after": f}
        for f in state["fields"]
        if f != before[f["id"]]
    ]
    timestamp, version = now(), row["version"] + 1
    db.execute(
        "UPDATE compilation_sessions SET state_json=?,version=?,updated_at=? WHERE id=?",
        (json.dumps(state, ensure_ascii=False), version, timestamp, row["id"]),
    )
    db.execute(
        "INSERT INTO compilation_session_revisions VALUES (?,?,?,?)",
        (
            row["id"],
            version,
            json.dumps(
                {
                    "action": action,
                    "changes": changes,
                    "status": state["status"],
                    "last_generation": state["last_generation"],
                    "last_error": state["last_error"],
                    "chat_workflow": state.get("chat_workflow"),
                },
                ensure_ascii=False,
            ),
            timestamp,
        ),
    )
    return payload(_row(db, row["project_id"], row["id"]))


def read_original(row):
    original = bytes(row["original"])
    if hashlib.sha256(original).hexdigest() != json.loads(row["state_json"])["template_sha256"]:
        raise DocumentInputError("Lo snapshot originale non coincide con il suo hash")
    return inspect_docx(original)


def claim_resolution(project_id: str, session_id: str, version: int, ids: list[str] | None,
                     *, automatic=False):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version)
        if automatic:
            if not chat_view(state)["auto_continue"] or ids is not None:
                raise HTTPException(409, "L'analisi automatica è ferma: rileggi la conversazione")
            state["chat_workflow"]["steps"] += 1
        fields = state["fields"]
        if ids is None:
            pending = automatic_fields(state) if automatic and grouped(state) else sorted(
                (f for f in fields if f["status"] == "PENDING"),
                key=lambda f: (not f.get("awaiting_dependency_resolution", False),
                               f["last_attempt_at"] or ""),
            )
            if automatic and grouped(state) and pending:
                phase = resolution_phase(pending[0])
                pending = [f for f in pending if resolution_phase(f) == phase]
            retry = bool(automatic and grouped(state) and pending
                         and pending[0].get("validation_errors") and pending[0]["last_attempt_at"])
            # A smaller second pass narrows interpretation without a per-field
            # model call. The 36-step/time budget still bounds the whole cycle.
            selected = [f["id"] for f in pending[:BATCH_SIZE // 2 if retry else BATCH_SIZE]]
        else:
            selected = ids
        if not selected or len(set(selected)) != len(selected) or len(selected) > BATCH_SIZE:
            raise HTTPException(422, "Indica da 1 a 12 candidate distinti da analizzare")
        by_id = {f["id"]: f for f in fields}
        if any(
            i not in by_id or by_id[i]["status"] in {"USER_PROVIDED", "RESOLVED", "NOT_APPLICABLE"}
            for i in selected
        ):
            raise HTTPException(422, "Campo sconosciuto o già deciso: usa reset per riesaminarlo")
        if automatic and grouped(state):
            workflow = state["chat_workflow"]
            workflow.setdefault("source_attempts", dict(phase_attempts(state, "source")))
            workflow["last_analysis_field_ids"] = selected
            workflow["last_analysis_requested_version"] = version
            workflow["last_analysis_phase"] = resolution_phase(by_id[selected[0]])
            for field_id in selected:
                key = ("source_attempts" if by_id[field_id].get("requirement")
                       else "analysis_attempts")
                attempts = workflow.setdefault(key, {})
                attempts[field_id] = attempts.get(field_id, 0) + 1
        state.update(
            status="ANALYZING",
            last_error=None,
            lease_until=(datetime.now(UTC) + timedelta(seconds=LEASE_SECONDS)).isoformat(),
        )
        claimed = save_state(db, row, state, "analyze_start")
        return claimed, bytes(row["original"]), [by_id[i] for i in selected]


def claim_source_attempts(project_id, session_id, version, fields, source_ids):
    """Persist SOURCE attempts and interpreted FORM data before retrieval."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version, allow_busy=True)
        replacements = {f["id"]: f for f in fields}
        state["fields"] = [replacements.get(f["id"], f) for f in state["fields"]]
        workflow = state.get("chat_workflow") or {}
        if grouped(state):
            attempts = workflow.setdefault("source_attempts", dict(phase_attempts(state, "source")))
            for field_id in source_ids:
                attempts[field_id] = attempts.get(field_id, 0) + 1
            workflow["last_analysis_field_ids"] = source_ids
            workflow["last_analysis_phase"] = "source"
        return save_state(db, row, state, "source_start")


def complete_resolution(project_id, session_id, version, changed, diagnostics):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version, allow_busy=True)
        check_current_sources(project_id, changed)
        replacements = {f["id"]: f for f in changed}
        state["fields"] = [replacements.get(f["id"], f) for f in state["fields"]]
        state.update(
            status=session_status(state["fields"]),
            lease_until=None,
            last_resolution=diagnostics,
            last_error=None,
        )
        if state.get("chat_workflow") and all(f["status"] == "PENDING" for f in changed):
            if not any(
                f["status"] == "PENDING" and not f["last_attempt_at"] for f in state["fields"]
            ) and (not grouped(state) or not automatic_fields(state)):
                state["chat_workflow"]["paused_reason"] = "interpretation"
        return save_state(db, row, state, "analyze_complete")


def mark_failed(project_id, session_id, version, message):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM compilation_sessions WHERE id=? AND project_id=?",
            (session_id, project_id),
        ).fetchone()
        # A stale operation must never overwrite a newer correction/recovery.
        if row is not None and row["version"] == version:
            state = json.loads(row["state_json"])
            state.update(status="FAILED", last_error=message, lease_until=None)
            save_state(db, row, state, "failed")


def recover_invalid_automatic_step(project_id, session_id, requested_version):
    """Recover a global schema failure within the budget of its active phase."""
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = json.loads(row["state_json"])
        # SOURCE reservation adds a revision. A newer pause/correction must win.
        if (not grouped(state) or state["status"] != "FAILED"
                or (state["chat_workflow"].get("last_analysis_requested_version")
                    != requested_version)
                or state["chat_workflow"].get("user_paused")):
            return None
        selected = state["chat_workflow"].get("last_analysis_field_ids", [])
        if not selected:
            return None
        for field in state["fields"]:
            if field["id"] in selected:
                field.update(last_attempt_at=now())
                field["validation_errors"] = list(dict.fromkeys([
                    *field["validation_errors"],
                    "Output strutturato non valido: nessun dato applicato",
                ]))
        workflow = state["chat_workflow"]
        workflow["output_rejections"] = workflow.get("output_rejections", 0) + 1
        workflow["last_output_rejection"] = {"field_ids": selected, "at": now()}
        state.update(status=session_status(state["fields"]), last_error=None, lease_until=None)
        synchronize(state)
        if not automatic_fields(state) and not workflow["pending_clarifications"] \
                and any(f["status"] == "PENDING" for f in state["fields"]):
            state.update(status="FAILED", last_error=(
                "Tentativi automatici esauriti sulle posizioni rimaste "
                "(interpretazione o SOURCE). Nessun valore inventato."
            ))
        return save_state(db, row, state, "automatic_output_rejected")


def source_catalog_item(source: dict) -> dict:
    return {
        "id": f"chunk:{source['chunk_id']}",
        "document_id": source["file_id"],
        "source_name": source["source_name"],
        "chunk_index": source["chunk_index"],
        "content": source["content"],
        "scope": source.get("category") or "project",
        "source_kind": "source",
    }


def validate_value(layout, field, value, source=None, quote=None, *, user=False) -> dict:
    catalog = [source_catalog_item(source)] if source is not None else []
    evidence = (
        [{"source_id": catalog[0]["id"], "quote": quote}]
        if catalog
        else [{"source_id": "user:instructions", "quote": value}]
        if user
        else []
    )
    content = json.dumps(
        {
            "fields": [
                {
                    "cell_id": field["id"],
                    "label": field["label"][:250] or field["id"],
                    "entity": field.get("entity", "other"),
                    "kind": field.get("kind", "data"),
                    "status": "proposed",
                    "value": value,
                    "evidence": evidence,
                    "reason": "Valore esplicito dell'utente"
                    if user
                    else "Valore da SOURCE pertinente",
                }
            ],
            "warnings": [],
        }
    )
    return validate_proposals(
        content,
        layout,
        CompilationSources(catalog, len(catalog), sum(len(s["content"]) for s in catalog)),
        instructions=value if user else "",
        explicit_user_values={field["id"]: value} if user else None,
    )["fields"][0]


def apply_field_input(field, item):
    field.update(value=item.value,
                 status={"set": "USER_PROVIDED", "reset": "PENDING",
                         "not_applicable": "NOT_APPLICABLE"}[item.action],
                 provenance="USER" if item.action != "reset" else None,
                 source_evidence=[], alternatives=[], validation_errors=[], updated_at=now(),
                 reason=item.reason or "Aggiornamento esplicito dell'utente",
                 search={"status": "not_searched"})
    field.pop("conversation_disposition", None)
    if item.action == "reset":
        field.pop("applicability", None)
        field.pop("applicability_confirmed", None)
    elif item.action == "not_applicable" and field.get("condition"):
        field["applicability"] = {"condition": field["condition"], "applies": False,
                                  "provenance": "USER", "reason": item.reason}


def update_fields(project_id, session_id, version, updates: list[UserFieldInput],
                  *, from_chat=False) -> dict:
    if len({item.field_id for item in updates}) != len(updates):
        raise HTTPException(422, "Campo duplicato nell'aggiornamento")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version)
        layout, fields = read_original(row), {f["id"]: f for f in state["fields"]}
        for item in updates:
            if item.field_id not in fields:
                raise HTTPException(422, "Candidate inesistente nella sessione")
            field = fields[item.field_id]
            if item.action == "set":
                checked = validate_value(layout, field, item.value, user=True)
                if checked["validation_codes"]:
                    raise HTTPException(
                        422, {"field_id": field["id"], "errors": checked["validation_notes"]}
                    )
            apply_field_input(field, item)
        state.update(status=session_status(state["fields"]), lease_until=None, last_error=None)
        if from_chat or state.get("chat_workflow"):
            state["chat_workflow"] = new_cycle(state.get("chat_workflow"))
        if from_chat:
            state["clarification_user_turns"] = state.get("clarification_user_turns", 0) + 1
        return save_state(db, row, state, "user_update")


def chat_clarification(project_id, session_id, version, message, *, applicable_field=None,
                       user_quote=None):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version)
        state["chat_workflow"] = state.get("chat_workflow") or new_cycle()
        question = chat_view(state)["question"]
        if applicable_field:
            field = next(f for f in state["fields"] if f["id"] == applicable_field)
            field["applicability_confirmed"] = {"provenance": "USER"}
            field["applicability"] = {
                "condition": field["condition"], "applies": True,
                "provenance": "USER", "user_quote": user_quote,
            }
            # Seek factual values again, now that the dependency is established.
            field.update(status="PENDING", last_attempt_at=None, updated_at=now(),
                         awaiting_dependency_resolution=True)
            field.pop("conversation_disposition", None)
            state["chat_workflow"] = new_cycle(state["chat_workflow"])
            reopen_phase_attempts(state, field)
            state["status"] = session_status(state["fields"])
        elif question and question["field_ids"]:
            field = next(f for f in state["fields"] if f["id"] == question["field_ids"][0])
            key = field["id"] + ":" + field_fingerprint(field)
            attempts = state["chat_workflow"].setdefault("clarification_attempts", {})
            attempts[key] = attempts.get(key, 0) + 1
            if attempts[key] > 1:
                defer_field(field, "uninterpretable", user_quote or "")
                state["chat_workflow"]["clarification"] = None
            else:
                state["chat_workflow"]["clarification"] = message
                state["chat_workflow"]["clarification_question"] = {
                    "kind": question["kind"], "field_ids": question["field_ids"],
                }
        state["clarification_user_turns"] = state.get("clarification_user_turns", 0) + 1
        return save_state(db, row, state, "chat_clarification")


def defer_field(field, kind, user_quote):
    # Separate conversation disposition from factual state/provenance.
    field["conversation_disposition"] = {
        "kind": kind, "user_quote": user_quote, "at": now(),
        "fingerprint": field_fingerprint(field),
    }


def apply_clarification_group(project_id, session_id, version, replies, message):
    """One transaction; valid slots survive ambiguity/validation in other slots."""
    from app.compilation_chat import (
        ChatFieldReply,
        ClarificationReply,
        contains_span,
        has_user_alternatives,
        normalize_date,
        numbered_answers,
        user_updates,
    )

    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        state = check_revision(row, version)
        question = chat_view(state)["question"]
        if not question or question["kind"] != "clarifications":
            raise HTTPException(409, "Il gruppo è cambiato: rileggi la conversazione")
        slots = {s["slot"]: s for s in question["slots"]}
        if (len({r.slot for r in replies}) != len(replies)
                or any(r.slot not in slots for r in replies)):
            raise HTTPException(422, "Slot estraneo/duplicato: nessun campo aggiornato")
        fields, layout, errors = {f["id"]: f for f in state["fields"]}, read_original(row), []
        numbered = numbered_answers(message)
        if not replies:
            replies = [ClarificationReply(slot=index, action="CLARIFY", user_quote=message)
                       for index in slots]
        for reply in replies:
            slot = slots[reply.slot]
            try:
                if not contains_span(message, reply.user_quote):
                    raise ValueError("Estratto USER assente nell'ultimo messaggio")
                if numbered and (reply.slot not in numbered or not contains_span(
                    numbered[reply.slot], reply.user_quote,
                )):
                    raise ValueError("La risposta numerata appartiene a un altro slot")
                if reply.action in {"UNKNOWN", "SKIP", "REFUSE"}:
                    for field_id in slot["field_ids"]:
                        defer_field(fields[field_id], reply.action.lower(), reply.user_quote)
                    continue
                if reply.action == "CLARIFY" or has_user_alternatives(
                    numbered.get(reply.slot, reply.user_quote),
                ):
                    raise ValueError("Risposta ambigua: nessun valore scelto")
                if reply.normalized_value is not None and reply.normalized_value not in {
                    reply.value, normalize_date(reply.value or ""),
                }:
                    raise ValueError("Normalizzazione USER non verificabile")
                if reply.action in {"CONDITION_TRUE", "CONDITION_FALSE"}:
                    if len(slots) > 1 and not numbered and len(message.split()) <= 1:
                        raise ValueError("Conferma breve senza destinatario univoco nel gruppo")
                    if slot["kind"] != "applicability":
                        raise ValueError("Questo slot chiede un valore, non una condizione")
                    for field_id in slot["field_ids"]:
                        field = fields[field_id]
                        if reply.action == "CONDITION_FALSE":
                            apply_field_input(field, UserFieldInput(
                                field_id=field_id, action="not_applicable",
                                reason=f"Indicazione USER: {reply.user_quote}",
                            ))
                        else:
                            field["applicability"] = {
                                "condition": field["condition"], "applies": True,
                                "provenance": "USER", "user_quote": reply.user_quote,
                            }
                            field.update(status="PENDING", last_attempt_at=None,
                                         awaiting_dependency_resolution=True)
                            reopen_phase_attempts(state, field)
                    continue
                updates = user_updates(state, [ChatFieldReply(
                    field_id=slot["field_ids"][0], action="set", value=reply.value,
                    user_quote=reply.user_quote,
                )], reply.user_quote, question={"kind": slot["kind"],
                                               "field_ids": slot["field_ids"]})
                item = updates[0]
                field = fields[item.field_id]
                checked = validate_value(layout, field, item.value, user=True)
                if checked["validation_codes"]:
                    raise ValueError("; ".join(checked["validation_notes"]))
                apply_field_input(field, item)
            except ValueError as exc:
                errors.append({"slot": reply.slot, "reason": str(exc)})
                key = ":".join(f"{i}/{fp}" for i, fp in slot["fingerprints"].items())
                attempts = state["chat_workflow"].setdefault("group_clarification_attempts", {})
                attempts[key] = attempts.get(key, 0) + 1
                if attempts[key] > 1:
                    for field_id in slot["field_ids"]:
                        defer_field(fields[field_id], "uninterpretable", reply.user_quote)
                for active in state["chat_workflow"].get("active_clarifications", []):
                    if active["slot"] == reply.slot:
                        active["clarify"] = True
        state["clarification_user_turns"] = state.get("clarification_user_turns", 0) + 1
        state["chat_workflow"] = new_cycle(state["chat_workflow"])
        state["status"] = session_status(state["fields"])
        return save_state(db, row, state, "chat_group_reply"), errors


def chat_control(project_id, session_id, version, control):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = _row(db, project_id, session_id)
        if control.kind == "pause":
            # A pause may arrive while a claim increments the version. It can only
            # stop orchestration, never apply an old value. Late results fail CAS.
            if version > row["version"]:
                raise HTTPException(409, "Versione di pausa non valida")
            state = check_revision(row, row["version"], allow_busy=True)
            state["chat_workflow"] = state.get("chat_workflow") or new_cycle()
            state["chat_workflow"].update(user_paused=True, clarification=None)
            if state["status"] == "ANALYZING":
                state["status"] = session_status(state["fields"])
            state["lease_until"] = None
        else:
            state = check_revision(row, version)
            if control.kind == "resume":
                if not state.get("chat_workflow"):
                    raise HTTPException(409, "Avvia prima la compilazione nella chat")
                clean = {**state, "chat_workflow": {
                    **state["chat_workflow"], "user_paused": False,
                }}
                view = chat_view(clean)
                if view["question"] and view["question"]["kind"] == "deferred_summary":
                    # An explicit request to revisit the summary reopens one issue.
                    field = next(f for f in state["fields"] if f.get("conversation_disposition"))
                    field.pop("conversation_disposition", None)
                state["chat_workflow"] = new_cycle(state["chat_workflow"])
                if state["status"] in {"ANALYZING", "FAILED"}:
                    state["status"] = session_status(state["fields"])
                state.update(lease_until=None, last_error=None)
            else:
                question = chat_view(state)["question"]
                if not question or control.field_id not in question["field_ids"]:
                    raise HTTPException(422, "Puoi rinviare soltanto la voce appena chiesta")
                field = next(f for f in state["fields"] if f["id"] == control.field_id)
                defer_field(field, control.kind, control.user_quote)
                state["chat_workflow"] = new_cycle(state["chat_workflow"])
                state["clarification_user_turns"] = state.get("clarification_user_turns", 0) + 1
        return save_state(db, row, state, "chat_" + control.kind)


def check_current_sources(
    project_id: str, fields: list[dict], *, db: sqlite3.Connection | None = None,
):
    snapshots = [e for f in fields if f["provenance"] == "SOURCE" for e in f["source_evidence"]]
    snapshots += [e for f in fields for e in (f.get("applicability") or {}).get("evidence", [])]
    if not snapshots:
        return
    current = {
        e["chunk_id"]: e for e in reload_evidence(project_id, snapshots, target="source", db=db)
    }
    for evidence in snapshots:
        actual = current.get(evidence["chunk_id"])
        if actual is None or any(
            actual.get(key) != evidence.get(key)
            for key in (
                "content",
                "file_id",
                "role",
                "project_id",
                "scope",
                "category",
            )
        ):
            raise HTTPException(
                409,
                "Una SOURCE è cambiata o non è più ammessa: reset e risolvi il campo",
            )


def finalize_session(project_id, session_id, version, allow_unresolved=False) -> dict:
    with connection() as db:
        row = _row(db, project_id, session_id)
        state = check_revision(row, version)
    try:
        layout = read_original(row)
        if not allow_unresolved and any(f["status"] in UNRESOLVED for f in state["fields"]):
            raise HTTPException(409, "Problemi aperti: risolvi i campi o richiedi allow_unresolved")
        check_current_sources(project_id, state["fields"])
        values, checks = {}, []
        for field in state["fields"]:
            if field["status"] not in {"RESOLVED", "USER_PROVIDED"}:
                continue
            user = field["status"] == "USER_PROVIDED" and field["provenance"] == "USER"
            if not user and (field["provenance"] != "SOURCE" or not field["source_evidence"]):
                raise DocumentInputError("Valore senza provenienza fattuale o utente")
            source = field["source_evidence"][0] if not user else None
            if source is not None:
                # Reapply the same requirement-specific gate, not just literal citation checks.
                from app.compilation_session_resolution import validate_support

                validate_support(field, source, source["quote"], field["value"])
            checked = validate_value(
                layout,
                field,
                field["value"],
                source,
                source["quote"] if source else None,
                user=user,
            )
            if checked["validation_codes"]:
                raise DocumentInputError(
                    "Proposta rifiutata: " + "; ".join(checked["validation_notes"]),
                )
            checks.append(checked)
            values[field["id"]] = checked["written_value"]
        draft = fill_docx(layout, values)
        report = {
            "schema_version": 5,
            "created_at": now(),
            "project_id": project_id,
            "session_id": session_id,
            "session_version": version,
            "status": "needs_review",
            "ready_for_submission": False,
            "template_sha256": layout.sha256,
            "output_sha256": hashlib.sha256(draft).hexdigest(),
            "execution": {"strategy": "compilation_session", "allow_unresolved": allow_unresolved},
            "fields": checks,
            "session_fields": state["fields"],
            "summary": payload(row)["summary"],
            "open_issues": payload(row)["open_issues"],
            "written_field_count": len(values),
            "unsupported_locations": layout.unsupported_locations,
            "warnings": [
                "Bozza da revisionare: verificare applicabilità, allegati e impaginazione.",
                "I candidate non rappresentano una lista completa di obblighi del modulo.",
            ],
        }

        def save_generation(db, generated):
            current = _row(db, project_id, session_id)
            check_revision(current, version)
            # A second connection can block on this transaction's spilled report pages.
            check_current_sources(project_id, state["fields"], db=db)
            state.update(
                status="GENERATED",
                lease_until=None,
                last_error=None,
                last_generation={"session_version": version, **generated},
            )
            # The full report is already persisted in document_compilations.
            state["last_generation"].pop("report", None)
            save_state(db, current, state, "generate")

        _persist(
            project_id,
            state["template_name"],
            layout.original,
            draft,
            report,
            on_saved=save_generation,
        )
    except HTTPException:
        raise
    except Exception:
        mark_failed(
            project_id, session_id, version, "Finalizzazione fallita; stato dei campi conservato"
        )
        raise
    return get_session(project_id, session_id)
