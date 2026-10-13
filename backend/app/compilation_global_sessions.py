"""Single-call chat compilation, with explicit review before a partial DOCX export.

The pure V10 audit remains authoritative for local grounding. Reviewing a
proposal does not turn it into RESOLVED or replace SOURCE provenance with USER.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from app import compilation_sessions as sessions
from app.compilation_catalog import build_compilation_catalog
from app.compilation_global import (
    CURRENT_VERSION,
    build_global_input,
    global_request,
    load_document_corpus,
    validate_global_proposal,
)
from app.config import get_ai_settings
from app.db import connection, get_storage_path
from app.document_compilation_routes import _persist
from app.docx_templates import DocumentInputError, fill_docx
from app.generation import GenerationError, GenerationNotConfiguredError, request_model_content

TIMEOUT_SECONDS = 300


def initial_state(layout):
    catalog = build_compilation_catalog(layout)
    return {"phase": "PENDING", "candidate_count": len(catalog["candidates"]),
            "catalog": catalog,
            "writable_ids": sorted(catalog["candidates"]), "paused": False,
            "attempts": 0, "audit": None, "artifact_path": None}


def grounded(field):
    return (field.get("validation") == "GROUNDED_PROPOSAL"
            or field.get("proposal_grounding") == "GROUNDED_PROPOSAL")


def review_fields(data):
    writable = set(data["writable_ids"])
    catalog = data["catalog"]
    paragraphs = {p["id"]: p["text"] for b in catalog["blocks"] for p in b["paragraphs"]}
    result = []
    for field in (data.get("audit") or {}).get("fields", []):
        if not field.get("proposal") and not field.get("form_evidence"):
            continue
        value = field.get("proposed_value", field.get("value"))
        unknown = [c for c, check in field.get("condition_checks", {}).items()
                   if check["result"] == "unknown"]
        candidate = catalog["candidates"].get(field["candidate_id"], {})
        context_ids = set(candidate.get("anchor_paragraph_ids", []))
        if candidate.get("continuation_origin_paragraph_id"):
            context_ids.add(candidate["continuation_origin_paragraph_id"])
        result.append({
            "candidate_id": field["candidate_id"],
            "label": field.get("label", field["candidate_id"]), "value": value,
            "validation": field["validation"], "conditional": bool(unknown),
            "conditions": unknown,
            "form_quote": field.get("form_evidence", {}).get("quote", ""),
            "form_context": "\n".join(text for key, text in paragraphs.items()
                                       if key in context_ids and text.strip())[:3000],
            "selectable": bool(grounded(field) and (isinstance(value, str) or (
                type(value) is bool and (data.get("audit") or {}).get("version") == 11))
                               and field["candidate_id"] in writable
                               and field.get("disposition") in {"value", "conditional"}),
            "source_evidence": field.get("source_evidence", []),
            "issues": field.get("validation_errors", []) + (
                ["Scrittura checkbox non ancora supportata"]
                if field["candidate_id"] not in writable else []),
        })
    return result


def chat_view(state):
    data = state["global_compilation"]
    stale = state["status"] == "ANALYZING" and (
        not state.get("lease_until") or state["lease_until"] <= sessions.now()
    )
    dialogue = data.get("dialogue") or {}
    auto = (data["phase"] == "PENDING" and state["status"] == "CREATED" or
            data["phase"] == "REVIEW" and dialogue.get("phase") != "READY"
            and state["status"] == "WAITING_FOR_USER")
    return {"enabled": True, "auto_continue": auto and not data["paused"],
            "paused": data["paused"] or stale or state["status"] == "FAILED",
            "paused_by_user": data["paused"], "question": (dialogue.get("question")
                if not data["paused"] and not auto and not stale else None),
            "analyzed": data["candidate_count"] if data["phase"] == "REVIEW" else 0,
            "verified": 0, "user_provided": len(dialogue.get("user_values", {})),
            "remaining_questions": len((dialogue.get("question") or {}).get("slots", [])),
            "steps_used": data["attempts"], "max_steps": 1}


def session_payload(row, state):
    data, audit = state["global_compilation"], state["global_compilation"].get("audit") or {}
    fields = review_fields(data)
    view = {k: v for k, v in data.items() if k not in {"audit", "writable_ids", "catalog"}}
    view.update(fields=fields, proposal_count=sum(f["selectable"] for f in fields),
                omitted=audit.get("unassigned_count", 0),
                rejected=sum(bool(f["issues"]) for f in fields),
                conditions=[{"id": key, "quote": item.get("form_evidence", {}).get(
                    "quote", item.get("form", {}).get("quote", "")),
                             "result": item.get("result", "unknown"),
                             "reason": item.get("reason", "")}
                            for key, item in audit.get("conditions", {}).items()],
                report_url=(f"/api/projects/{row['project_id']}/compilation-sessions/"
                            f"{row['id']}/global-report" if audit else None))
    return {**{k: v for k, v in state.items() if k != "global_compilation"},
            "global_compilation": view, "chat": chat_view(state),
            **{k: row[k] for k in ["id", "project_id", "form_id", "conversation_id", "version",
                                   "created_at", "updated_at"]},
            "blocked_previous_writes": [], "open_issues": [],
            "summary": {"total": data["candidate_count"], "pending": (
                audit.get("unassigned_count", 0) if audit else data["candidate_count"]),
                "resolved": 0, "missing": 0, "ambiguous": 0, "conflicting": 0,
                "not_applicable": 0, "user_provided": len(
                    (data.get("dialogue") or {}).get("user_values", {}))}}


def _row_state(db, project_id, session_id, version, *, allow_busy=False):
    row = sessions._row(db, project_id, session_id)
    state = sessions.check_revision(row, version, allow_busy=allow_busy)
    if state.get("engine") != "global":
        raise HTTPException(409, "Questa operazione richiede una compilazione globale")
    return row, state


def _folder(project_id, session_id, attempt):
    root = get_storage_path().resolve()
    folder = (root / project_id / "_global_compilations" / session_id / attempt).resolve()
    if root not in folder.parents:
        raise DocumentInputError("Percorso del progetto non valido")
    return folder


def _prepare(project_id, session_id, version):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = _row_state(db, project_id, session_id, version)
        data = state["global_compilation"]
        if data["phase"] != "PENDING" or data["paused"]:
            raise HTTPException(409, "La proposta è già analizzata o la compilazione è in pausa")
        layout = sessions.read_original(row)
        sources = load_document_corpus(db, project_id)
        try:
            model_input = build_global_input(layout, project_id, sources)
        except ValueError as exc:
            raise DocumentInputError(str(exc)) from exc
        attempt = uuid4().hex
        data.update(phase="ANALYZING", attempts=data["attempts"] + 1,
                    contract_version=model_input["schema_output"]["properties"]["version"]["const"],
                    catalog=model_input["form"],
                    artifact_path=str(_folder(project_id, session_id, attempt).relative_to(
                        get_storage_path().resolve())))
        data.pop("last_review", None)
        state.update(status="ANALYZING", last_error=None, lease_until=(
            datetime.now(UTC) + timedelta(seconds=TIMEOUT_SECONDS + 60)).isoformat())
        claimed = sessions.save_state(db, row, state, "global_analysis_start")
    return layout, sources, model_input, claimed


def _save(path, value, secret):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    path.write_text((text.replace(secret, "[REDACTED]") if secret else text) + "\n")


def _complete(project_id, session_id, version, raw, audit, metadata):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = _row_state(db, project_id, session_id, version, allow_busy=True)
        version = state["global_compilation"].get("contract_version", 10)
        fresh = validate_global_proposal(raw, sessions.read_original(row), project_id,
                                        load_document_corpus(db, project_id),
                                        expected_version=version)
        if fresh != audit:
            raise HTTPException(409, "Le fonti sono cambiate durante l'analisi: "
                                "riprova esplicitamente")
        state["global_compilation"].update(phase="REVIEW", audit=audit, **metadata)
        state.update(status="WAITING_FOR_USER", lease_until=None, last_error=None)
        return sessions.save_state(db, row, state, "global_analysis_complete")


async def resolve_global(project_id, session_id, version, field_ids=None):
    if field_ids is not None:
        raise HTTPException(422, "Il motore globale analizza l'intero modulo in una chiamata")
    settings = get_ai_settings()
    if not settings.configured:
        raise GenerationNotConfiguredError("Configura un modello AI per compilare il modulo")
    current = await run_in_threadpool(sessions.get_session, project_id, session_id)
    if current["global_compilation"]["phase"] == "REVIEW":
        from app.compilation_global_dialogue import refresh_dialogue

        return await refresh_dialogue(project_id, session_id, version)
    layout, sources, data, claimed = await run_in_threadpool(
        _prepare, project_id, session_id, version)
    root = get_storage_path().resolve() / claimed["global_compilation"]["artifact_path"]
    started = time.perf_counter()
    metadata = {"model": settings.model, "provider": settings.provider, "http_calls": 0}
    try:
        root.mkdir(parents=True, exist_ok=False)
        body = global_request(settings, data, thinking=settings.provider == "deepseek")
        _save(root / "input.json", data, settings.api_key)
        _save(root / "request.json", body, settings.api_key)
        (root / "original.docx").write_bytes(layout.original)

        async def capture(response):
            metadata["http_calls"] += 1
            await response.aread()
            _save(root / "http-response.txt", response.text, settings.api_key)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=15),
            event_hooks={"response": [capture]},
        ) as client:
            raw, model, usage = await asyncio.wait_for(request_model_content(
                client, settings, body, TIMEOUT_SECONDS, response_schema=data["schema_output"]),
                timeout=TIMEOUT_SECONDS)
        _save(root / "response.txt", raw, settings.api_key)
        try:
            audit = validate_global_proposal(raw, layout, project_id, sources,
                                             expected_version=CURRENT_VERSION)
        except ValueError as exc:
            raise GenerationError("Proposta globale non valida; nessun valore applicato") from exc
        metadata.update(model=model, usage=usage, ai_seconds=time.perf_counter() - started)
        _save(root / "audit.json", audit, settings.api_key)
        from app.compilation_global_dialogue import narrate

        metadata["dialogue"] = await narrate({**initial_state(layout),
                                            "catalog": data["form"], "audit": audit}, root)
        return await run_in_threadpool(_complete, project_id, session_id, claimed["version"],
                                      raw, audit, metadata)
    except BaseException as exc:
        await run_in_threadpool(sessions.mark_failed, project_id, session_id, claimed["version"],
                                "Analisi globale interrotta; nessun valore applicato")
        metadata.update(error_type=type(exc).__name__, ai_seconds=time.perf_counter() - started)
        raise
    finally:
        if root.is_dir():
            _save(root / "metrics.json", metadata, settings.api_key)


def control_session(project_id, session_id, version, kind):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        current = sessions._row(db, project_id, session_id)
        if kind == "pause" and version <= current["version"]:
            version = current["version"]  # An explicit pause wins over an in-flight claim.
        row, state = _row_state(db, project_id, session_id, version, allow_busy=kind == "pause")
        data = state["global_compilation"]
        if kind == "pause":
            data["paused"] = True
            if data["phase"] == "ANALYZING":
                data["phase"] = "PENDING"  # Explicit resume can authorize one new call.
            state.update(status="WAITING_FOR_USER", lease_until=None)
        elif kind == "resume":
            data["paused"] = False
            if (data.get("dialogue") or {}).get("error"):
                data["dialogue"].update(phase="PENDING", question=None)
                data["dialogue"].pop("error", None)
            if (data["phase"] == "ANALYZING"
                    or state["status"] == "FAILED" and not data.get("audit")):
                data["phase"] = "PENDING"
            elif state["status"] == "FAILED":
                data.setdefault("dialogue", {}).update(phase="PENDING", question=None)
            state.update(status="CREATED" if data["phase"] == "PENDING" else "WAITING_FOR_USER",
                         lease_until=None, last_error=None)
        else:
            raise HTTPException(422, "Controllo globale non supportato")
        return sessions.save_state(db, row, state, f"global_{kind}")


async def handle_chat_action(session, decision, expected_version, message):
    from app.compilation_chat import contains_span

    if decision.action == "compilation_control" and decision.control.kind in {"pause", "resume"}:
        if not contains_span(message, decision.control.user_quote):
            raise HTTPException(422, "Controllo non grounded nell'ultimo messaggio USER")
        kind = decision.control.kind
        after = await run_in_threadpool(control_session, session["project_id"], session["id"],
                                       expected_version or session["version"], kind)
        return ("Metto in pausa la compilazione." if kind == "pause" else
                "Riprendo la stessa compilazione globale."), {
                    "session_id": after["id"], "action": "paused" if kind == "pause" else "resumed"}
    if decision.action == "compilation_generate" or (
        decision.action == "compilation_control" and decision.control.kind == "finish"
    ):
        from app.compilation_global_dialogue import export_selection
        from app.compilation_session_models import GlobalDraftRequest

        if session["chat"]["paused"]:
            return "La compilazione è in pausa. Chiedimi di riprenderla prima di generare.", {
                "session_id": session["id"], "action": "clarify"}
        ids, conditions, user_ids = export_selection(session)
        empty = not ids and not user_ids
        dialogue = session["global_compilation"].get("dialogue") or {}
        if empty and (dialogue.get("phase") != "READY" or dialogue.get("error")
                      or (session["chat"].get("question") or {}).get("kind") != "generate"):
            return ("Non ho ancora valori utilizzabili per la bozza. "
                    "Prima dobbiamo chiarire le informazioni o le condizioni rimaste aperte.",
                    {"session_id": session["id"], "action": "clarify"})
        after = await run_in_threadpool(generate_draft, session["project_id"], session["id"],
                               GlobalDraftRequest(version=expected_version or session["version"],
                                   candidate_ids=ids, confirmed_condition_ids=conditions,
                                   user_candidate_ids=user_ids, allow_unresolved=True,
                                   allow_empty=empty, user_quote=message))
        return (after["global_compilation"]["dialogue"]["message"],
                {"session_id": session["id"], "action": "generated"})
    return ((session["global_compilation"].get("dialogue") or {}).get("message")
            or "Sto conservando l'analisi. Puoi chiedermi di riprendere la compilazione.",
            {"session_id": session["id"], "action": "clarify"})


def _selected(row, state, request, db):
    if not request.allow_unresolved:
        raise HTTPException(409, "Conferma esplicitamente la generazione di una bozza parziale")
    data = state["global_compilation"]
    if data["phase"] != "REVIEW":
        raise HTTPException(409, "Completa l'analisi prima di rivedere le proposte")
    ids, conditions = request.candidate_ids, request.confirmed_condition_ids
    if not ids and not request.user_candidate_ids and not (
        request.allow_empty and request.user_quote.strip()
    ):
        raise HTTPException(422, "Conferma esplicitamente la copia senza valori inseriti")
    if len(set(ids)) != len(ids) or len(set(conditions)) != len(conditions):
        raise HTTPException(422, "Selezioni duplicate")
    allowed = {f["candidate_id"]: f for f in review_fields(data) if f["selectable"]}
    if any(i not in allowed for i in ids):
        raise HTTPException(422, "Selezione non scrivibile o senza grounding SOURCE valido")
    if any(c not in data["audit"].get("conditions", {}) for c in conditions):
        raise HTTPException(422, "Condizione sconosciuta")
    fields = {f["candidate_id"]: f for f in data["audit"]["fields"]}
    if any(cid not in (data.get("dialogue") or {}).get("user_values", {})
           for cid in request.user_candidate_ids):
        raise HTTPException(422, "Valore USER non acquisito per un campo valido")
    answers = (data.get("dialogue") or {}).get("answers", {})
    selected = [fields[i] for i in ids]
    for field in selected:
        if any(answers.get("condition:" + c, {}).get("applies") is False
               for c in field.get("conditions", [])):
            raise HTTPException(409, "Il valore appartiene a una condizione esclusa dall'utente")
        unknown = {c for c, check in field.get("condition_checks", {}).items()
                   if check["result"] == "unknown"}
        if not unknown <= set(conditions):
            raise HTTPException(409, "Conferma l'applicabilità delle condizioni "
                                "dei valori selezionati")
    folder = get_storage_path().resolve() / data["artifact_path"]
    raw = (folder / "response.txt").read_text()
    fresh = validate_global_proposal(
        raw, sessions.read_original(row), row["project_id"],
        load_document_corpus(db, row["project_id"]),
        expected_version=data["audit"].get("version", 10))
    refreshed = {f["candidate_id"]: f for f in fresh["fields"]}
    if any(refreshed[i] != fields[i] for i in ids):
        raise HTTPException(409, "Una SOURCE o una condizione è cambiata: ripeti l'analisi")
    from app.compilation_choices import materialize_choices

    try:
        materialize_choices(data, ids, request.user_candidate_ids)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return selected


def generate_draft(project_id, session_id, request):
    with connection() as db:
        row, state = _row_state(db, project_id, session_id, request.version)
        selected = _selected(row, state, request, db)
        source_map = {s["chunk_id"]: s for s in load_document_corpus(db, project_id)}
    layout = sessions.read_original(row)
    values, checked_fields = {}, []
    for field in selected:
        value = field.get("proposed_value", field.get("value"))
        proof = field["source_evidence"][0]
        source = source_map[proof["chunk_id"]]
        checkbox = state["global_compilation"]["catalog"]["candidates"][
            field["candidate_id"]]["type"] == "checkbox"
        checked = ({"cell_id": field["candidate_id"], "label": field["label"],
                    "kind": "choice", "written_value": value, "validation_codes": [],
                    "validation_notes": [], "status": "proposed"} if checkbox else
                   sessions.validate_value(layout, {"id": field["candidate_id"], **field}, value,
                                           source, proof["quote"]))
        if checked["validation_codes"] or checked["written_value"] != value:
            raise DocumentInputError("Il validatore DOCX rifiuta una proposta selezionata")
        if not checkbox:
            values[field["candidate_id"]] = value
        checked_fields.append({**checked, "provenance": "SOURCE",
                               "reviewed_by": "USER", "source_evidence": field["source_evidence"],
                               "confirmed_conditions": [c for c in field.get("conditions", [])
                                                        if c in request.confirmed_condition_ids]})
    from app.compilation_global_dialogue import checked_user_fields

    for cid, checked, user in checked_user_fields(row, state, request):
        if cid in values:
            raise HTTPException(422, "Lo stesso campo non può essere SOURCE e USER")
        if type(checked["written_value"]) is not bool:
            values[cid] = checked["written_value"]
        checked_fields.append({**checked, "provenance": "USER", "user_quote": user["user_quote"],
                               "source_evidence": []})
    from app.compilation_choices import materialize_choices

    checkbox_values, checkbox_effects = materialize_choices(
        state["global_compilation"], request.candidate_ids, request.user_candidate_ids)
    draft = fill_docx(layout, values, checkbox_values=checkbox_values)
    written_count = len(values) + len(checkbox_values)
    message = ("Ho preparato una copia del modulo senza inserire alcun valore. "
               "I campi irrisolti e quelli con condizioni non confermate restano vuoti. "
               "Puoi scaricarla e controllarla." if not written_count else
               "Ho preparato una bozza parziale con i dati disponibili. "
               "Le informazioni non verificate restano vuote. Puoi scaricarla e controllarla.")
    report = {"schema_version": 7, "created_at": sessions.now(), "project_id": project_id,
              "session_id": session_id, "session_version": request.version,
              "status": "needs_review", "ready_for_submission": False,
              "execution": {"strategy": "global_proposal_user_review", "allow_unresolved": True,
                            "allow_empty": request.allow_empty},
              "template_sha256": layout.sha256, "output_sha256": hashlib.sha256(draft).hexdigest(),
              "fields": checked_fields, "written_field_count": written_count, "resolved": 0,
              "checkbox_values": checkbox_values, "checkbox_effects": checkbox_effects,
              "global_audit": state["global_compilation"]["audit"],
              "conversation_review": {k: (state["global_compilation"].get("dialogue") or {}).get(
                  k, {}) for k in ["answers", "user_values"]},
              "user_review": {"candidate_ids": request.candidate_ids,
                              "user_candidate_ids": request.user_candidate_ids,
                              "confirmed_condition_ids": request.confirmed_condition_ids,
                              "provenance": "USER", "user_quote": request.user_quote,
                              "allow_empty": request.allow_empty},
              "warnings": ["Nessun valore inserito: copia non compilata del modulo."
                           if not written_count else
                           "Bozza parziale: valori selezionati e condizioni "
                           "confermati dall'utente.",
                           "Le proposte non attestano completezza, allegati o ammissibilità.",
                           "Solo checkbox native con gruppo validato; verificare le altre scelte."]}

    def on_saved(db, generated):
        current, latest = _row_state(db, project_id, session_id, request.version)
        _selected(current, latest, request, db)  # Sources and revision atomically checked again.
        checked_user_fields(current, latest, request)
        latest.update(status="GENERATED", last_generation={"session_version": request.version,
                                                          **generated})
        latest["last_generation"].pop("report", None)
        latest["global_compilation"]["last_review"] = report["user_review"]
        if latest["global_compilation"].get("dialogue"):
            latest["global_compilation"]["dialogue"].update(phase="READY", question=None,
                message=message)
        sessions.save_state(db, current, latest, "global_draft_generate")

    _persist(project_id, state["template_name"], layout.original, draft, report, on_saved=on_saved)
    return sessions.get_session(project_id, session_id)


def report_path(project_id, session_id):
    session = sessions.get_session(project_id, session_id)
    if session.get("engine") != "global" or not session["global_compilation"]["report_url"]:
        raise HTTPException(404, "Report globale non disponibile")
    root = get_storage_path().resolve()
    path = (root / session["global_compilation"]["artifact_path"] / "audit.json").resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(404, "Report non trovato")
    return path
