"""Single-call chat compilation, with explicit review before a partial DOCX export.

The pure V10 audit remains authoritative for local grounding. Reviewing a
proposal does not turn it into RESOLVED or replace SOURCE provenance with USER.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
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
    # Ordinary profile: V14 + K3, plus coherent derived state after USER replies.
    # P3 candidate (not adopted): dialogue state and generation by FORM segments are
    # opt-in, separately, for a private experiment runtime (no UI); by default new
    # sessions keep the ordinary profile. Existing sessions keep their stored flags.
    experiment = {revision: 1 for revision, variable in (
        ("dialogue_revision", "MAPI_DIALOGUE_REVISION"),
        ("narration_recovery_revision", "MAPI_NARRATION_RECOVERY_REVISION"),
        ("generation_revision", "MAPI_GENERATION_REVISION")) if os.environ.get(variable) == "1"}
    # Promoted independently of P3. Explicit 0 preserves the previous creation profile
    # for comparisons; no missing flag in an existing session is upgraded at runtime.
    if os.environ.get("MAPI_DERIVATION_REVISION", "1") == "1":
        experiment["derivation_revision"] = 1
    # Resilient segments (candidate, not adopted): a separate opt-in revision.
    if os.environ.get("MAPI_GENERATION_REVISION") in {"2", "3"}:
        experiment["generation_revision"] = int(os.environ["MAPI_GENERATION_REVISION"])
    # Option continuations (rev 3 candidate only, not adopted): a separate opt-in revision.
    if (experiment.get("generation_revision") == 3
            and os.environ.get("MAPI_BRANCH_SCOPE_REVISION") == "1"):
        experiment["branch_scope_revision"] = 1
    if (experiment.get("generation_revision") == 3
            and os.environ.get("MAPI_HOLD_REREVIEW_REVISION") in {"1", "2"}):
        experiment["hold_rereview_revision"] = int(os.environ["MAPI_HOLD_REREVIEW_REVISION"])
    if (experiment.get("generation_revision") == 3
            and os.environ.get("MAPI_TABLE_SCOPE_REVISION") == "1"):
        experiment["table_scope_revision"] = 1
    return {"phase": "PENDING", "backend_revision": 13, "option_authorization_revision": 1,
            "attribution_safety_revision": 1, **experiment,
            "candidate_count": len(catalog["candidates"]),
            "catalog": catalog,
            "writable_ids": sorted(catalog["candidates"]), "paused": False,
            "attempts": 0, "audit": None, "artifact_path": None}


def grounded(field):
    return (field.get("validation") == "GROUNDED_PROPOSAL"
            or field.get("proposal_grounding") == "GROUNDED_PROPOSAL")


def review_fields(data):
    from app.compilation_form_applicability import blocked_fields as inapplicable
    from app.compilation_procedural_consent import accepted, requirements
    from app.compilation_scope_review import blocked_source_fields
    from app.compilation_segments import unassessed_fields, unverified_fields
    from app.compilation_table_scope import blocked_fields as table_scope_blocked
    from app.compilation_value_completeness import blocked_fields as incomplete

    table_unknown = table_scope_blocked(data)
    form_blocked = inapplicable(data)
    # Owner section not analyzed or local clause uncertain: no SOURCE write, but no FORM
    # verdict either (USER may fill).
    unverified, unassessed = unverified_fields(data), unassessed_fields(data)
    scope_blocked = blocked_source_fields(data)
    incomplete_fields = incomplete(data)
    consents = {cid: {"required": True, "confirmed": accepted(data, r),
                     "form_quote": r["authorization"]["form_evidence"]["quote"],
                     "question": r["question"]}
                for r in requirements(data) for cid in r["authorization"]["field_ids"]}
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
        recovered_context = ((field.get("destination_check") or {}).get("recovery") or {}).get(
            "form_evidence", [])
        recovered_context = [*recovered_context,
                             *(field.get("form_table_link") or {}).get("form_evidence", [])]
        result.append({
            "candidate_id": field["candidate_id"],
            "label": field.get("label", field["candidate_id"]), "value": value,
            "validation": field["validation"], "conditional": bool(unknown),
            "conditions": unknown,
            "form_quote": field.get("form_evidence", {}).get("quote", ""),
            "form_context": "\n".join([
                *(proof["quote"] for proof in recovered_context),
                *(text for key, text in paragraphs.items()
                  if key in context_ids and text.strip())])[:3000],
            "selectable": bool(grounded(field) and (isinstance(value, str) or (
                type(value) is bool and (data.get("audit") or {}).get("version") in {11, 12}))
                               and field["candidate_id"] in writable
                               and field["candidate_id"] not in form_blocked
                               and field["candidate_id"] not in unverified
                               and field["candidate_id"] not in incomplete_fields
                               and field.get("disposition") in {"value", "conditional"}),
            "source_evidence": field.get("source_evidence", []),
            **({"procedural_authorization": consents[field["candidate_id"]]}
               if field["candidate_id"] in consents else {}),
            **({"form_applicability": (data["audit"].get("form_applicability", {}).get(
                field["candidate_id"]) or {"result": "unknown", "basis": "requires_reanalysis"})}
               if field["candidate_id"] in form_blocked or field["candidate_id"] in
               data["audit"].get("form_applicability", {}) else {}),
            **({"value_completeness": (data["audit"].get("value_completeness", {}).get(
                field["candidate_id"]) or {"result": "UNKNOWN", "basis": "requires_reanalysis"})}
               if field["candidate_id"] in incomplete_fields else {}),
            "issues": field.get("validation_errors", []) + (
                ["Completezza delle componenti richieste dal campo non dimostrata"]
                if field["candidate_id"] in incomplete_fields else []) + (
                ["Sezione del modulo non analizzata: applicabilità non accertata"]
                if field["candidate_id"] in unassessed else
                ["Applicabilità dell’intestazione FORM non accertata: "
                 "condizione assente o non collegata"]
                if field["candidate_id"] in table_unknown else
                ["Ambito della decisione USER non verificato o non più coerente con il modulo"]
                if field["candidate_id"] in scope_blocked else
                ["Condizioni del paragrafo FORM dichiarate incerte dal modello"]
                if field["candidate_id"] in unverified else []) + (
                ["Scrittura checkbox non ancora supportata"]
                if field["candidate_id"] not in writable else []),
        })
    return result


def chat_view(state):
    from app.compilation_branch_evidence import effective_user_values

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
            "verified": 0, "user_provided": len(effective_user_values(data)),
            "remaining_questions": len((dialogue.get("question") or {}).get("slots", [])),
            "steps_used": data["attempts"], "max_steps": 1}


def session_payload(row, state):
    from app.compilation_branch_evidence import effective_user_values

    data, audit = state["global_compilation"], state["global_compilation"].get("audit") or {}
    fields = review_fields(data)
    view = {k: v for k, v in data.items() if k not in {
        "audit", "writable_ids", "catalog", "review_audit_name"}}
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
    dialogue = data.get("dialogue") or {}
    view["dialogue"] = {**dialogue, "user_values": effective_user_values(data)}
    if audit.get("version") == 12 and "reviewed_candidate_fingerprints" in dialogue:
        from app.compilation_global_dialogue import reviewed_candidates

        # The public session omits the full audit. Filter against it here before
        # the conversational export can consume the persisted review IDs.
        view["dialogue"]["reviewed_candidate_ids"] = list(reviewed_candidates(data))
    if "coverage_summary" in audit:
        view["coverage_summary"] = audit["coverage_summary"]
    return {**{k: v for k, v in state.items() if k != "global_compilation"},
            "global_compilation": view, "chat": chat_view(state),
            **{k: row[k] for k in ["id", "project_id", "form_id", "conversation_id", "version",
                                   "created_at", "updated_at"]},
            "blocked_previous_writes": [], "open_issues": [],
            "summary": {"total": data["candidate_count"], "pending": (
                audit.get("unassigned_count", 0) if audit else data["candidate_count"]),
                "resolved": 0, "missing": 0, "ambiguous": 0, "conflicting": 0,
                "not_applicable": 0, "user_provided": len(effective_user_values(data))}}


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
        from app.compilation_user_context import registered_user_context

        try:
            model_input = build_global_input(layout, project_id, sources,
                user_context=registered_user_context(db, row, state))
        except ValueError as exc:
            raise DocumentInputError(str(exc)) from exc
        if data.get("dialogue_revision") == 1:
            # Context to tell current from past offices; never a SOURCE fact.
            model_input["reference_date"] = datetime.now(UTC).date().isoformat()
        attempt = uuid4().hex
        data.update(phase="ANALYZING", attempts=data["attempts"] + 1,
                    user_context=model_input.get("user_context", []),
                    contract_version=model_input["schema_output"]["properties"]["version"]["const"],
                    catalog=model_input["form"],
                    artifact_path=str(_folder(project_id, session_id, attempt).relative_to(
                        get_storage_path().resolve())))
        data.pop("last_review", None)
        # Segment calls run in at most three waves (first segment, then batches).
        waves = {1: 3, 2: 5, 3: 5}.get(data.get("generation_revision"), 1)
        from app.compilation_global_dialogue import NARRATION_SECONDS, narration_attempt_limit

        state.update(status="ANALYZING", last_error=None, lease_until=(
            datetime.now(UTC) + timedelta(seconds=waves * TIMEOUT_SECONDS + 60
                + NARRATION_SECONDS * (narration_attempt_limit(data) - 1))).isoformat())
        claimed = sessions.save_state(db, row, state, "global_analysis_start")
    return layout, sources, model_input, claimed


def validated_audit(raw, layout, project_id, sources, data, folder, *, expected_version):
    """The same V12 validation for monolithic and merged envelopes, plus segment status."""
    report = folder / "segments" / "report.json"
    if data.get("generation_revision") in {2, 3}:
        from app.compilation_segments import attach_resilient_status

        # Each merged segment already passed the ordinary per-call budgets on its own.
        summary = json.loads(report.read_text())
        audit = validate_global_proposal(raw, layout, project_id, sources,
                                         expected_version=expected_version,
                                         budget_scale=max(1, summary["merged_segments"]))
        audit = attach_resilient_status(audit, summary)
        from app.compilation_branch_scope import enabled, propagate

        # The claimed public state omits the catalog: rebuild it from the same original.
        catalog = build_compilation_catalog(layout)
        if enabled(data):
            audit = propagate(audit, catalog)
        from app import compilation_table_scope

        return compilation_table_scope.apply(audit, catalog) if (
            compilation_table_scope.enabled(data)) else audit
    audit = validate_global_proposal(raw, layout, project_id, sources,
                                     expected_version=expected_version)
    if data.get("generation_revision") == 1 and report.is_file():
        from app.compilation_segments import attach_status

        audit = attach_status(audit, json.loads(report.read_text()))
    return audit


async def _resilient_proposal(settings, data, root, metadata, layout, project_id, sources,
                              *, revision=2):
    """Segments by dependency, validated one by one, cached by request digest (resumption).

    Bounded retries (MAX_RETRIES_PER_SEGMENT, MAX_RETRIES_PER_ANALYSIS) only for transport,
    truncation, unparsable or structurally invalid output; never a JSON repair. A failed
    segment leaves its destinations unanalyzed; independent validated segments are merged.
    """
    from app.compilation_segments import (
        MAX_CONCURRENT_SEGMENTS,
        MAX_RETRIES_PER_ANALYSIS,
        MAX_RETRIES_PER_SEGMENT,
        parse,
        request_digest,
        resilient_instruction,
        resilient_merge,
        resilient_partition,
        segment_input,
    )

    segments = resilient_partition(data["form"])
    if revision == 3:
        for segment in segments:
            segment["context_block_ids"] = [b["id"] for b in data["form"]["blocks"]]
    folder, cache = root / "segments", root.parent / "segment-cache"
    folder.mkdir()
    cache.mkdir(exist_ok=True)
    thinking = settings.provider == "deepseek"
    inputs = {s["index"]: segment_input(data, s, revision=revision) for s in segments}
    bodies = {s["index"]: global_request(settings, inputs[s["index"]], thinking=thinking,
                                         segment=resilient_instruction(
                                             s, len(segments), revision=revision))
              for s in segments}

    def sha(value):
        return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
                              ).hexdigest()

    # Explicit references of the input revision; the request digest covers all of them.
    references = {i: {"contract_version": inp["schema_output"]["properties"]["version"]["const"],
                      "sources": sha(inp["sources"]), "user_context": sha(inp.get("user_context")),
                      "user_values": sha(inp.get("user_values")),
                      "reference_date": inp.get("reference_date"), "form_segment": sha(inp["form"])}
                  for i, inp in inputs.items()}
    results, gate, budget = {}, asyncio.Semaphore(MAX_CONCURRENT_SEGMENTS), {"retries": 0}

    def structural(raw, segment):
        payload = parse(raw)
        if revision == 3:
            own = set(segment["candidate_ids"])
            for group in (payload.get("choice_groups") or {}).values():
                if isinstance(group, dict) and isinstance(group.get("options"), dict):
                    if set(group["options"]) - own:
                        raise ValueError("Gruppo di scelta oltre le destinazioni del segmento")
        validate_global_proposal(json.dumps(payload, ensure_ascii=False), layout, project_id,
                                 sources, expected_version=12)
        return payload

    async def run(segment):
        index, body = segment["index"], bodies[segment["index"]]
        digest = request_digest(body)
        target = folder / str(index)
        target.mkdir()
        _save(target / "request.json", body, settings.api_key)
        cached = cache / f"{digest}.json"
        record = {"status": "failed", "source": "called", "digest": digest, "attempts": [],
                  "payload": None, "error": None}
        if cached.is_file():
            try:  # Same request digest: the validated work of an earlier analysis is reused.
                entry = json.loads(cached.read_text())
                record.update(status="analyzed", source="cache",
                              payload=structural(entry["raw"], segment),
                              model=entry.get("model"))
                results[index] = record
                return
            except (OSError, ValueError, KeyError):
                record["cache_error"] = "Voce di cache illeggibile o non valida: ignorata"
        while True:
            started, attempt = time.perf_counter(), len(record["attempts"]) + 1

            async def capture(response, attempt=attempt):
                metadata["http_calls"] += 1
                await response.aread()
                _save(target / f"http-response-{attempt}.txt", response.text, settings.api_key)

            try:
                async with gate, httpx.AsyncClient(
                    timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=15),
                    event_hooks={"response": [capture]},
                ) as client:
                    raw, model, usage = await asyncio.wait_for(request_model_content(
                        client, settings, body, TIMEOUT_SECONDS,
                        response_schema=data["schema_output"]), timeout=TIMEOUT_SECONDS)
                _save(target / f"response-{attempt}.txt", raw, settings.api_key)
                record["attempts"].append({"result": "analyzed", "usage": usage,
                                           "seconds": time.perf_counter() - started})
                payload = structural(raw, segment)
                record.update(status="analyzed", payload=payload, model=model, error=None)
                tmp = cache / f"{digest}.tmp"
                tmp.write_text(json.dumps({"digest": digest, "segment": index, "raw": raw,
                                           "model": model, "attempts": record["attempts"],
                                           "inputs": references[index]}, ensure_ascii=False))
                tmp.replace(cached)
                break
            except (GenerationError, ValueError, TimeoutError, httpx.HTTPError) as exc:
                error = f"{type(exc).__name__}: {str(exc)[:200]}"
                if len(record["attempts"]) == attempt:  # Answered, then rejected.
                    record["attempts"][-1].update(result="failed", error=error)
                else:
                    record["attempts"].append({"result": "failed", "error": error,
                                               "usage": None,
                                               "seconds": time.perf_counter() - started})
                record["error"] = error
                retry = (len(record["attempts"]) <= MAX_RETRIES_PER_SEGMENT
                         and budget["retries"] < MAX_RETRIES_PER_ANALYSIS)
                if not retry:
                    break
                budget["retries"] += 1
        results[index] = record

    await run(segments[0])  # Warms the shared, cacheable prompt prefix.
    await asyncio.gather(*(run(segment) for segment in segments[1:]))
    analyzed = sorted(i for i, r in results.items() if r["status"] == "analyzed")

    def summary(merged_ids, report=None):
        return {**(report or {}), "revision": revision, "retries": budget["retries"],
                "merged_segments": len(merged_ids), "segments": [
                    {"index": s["index"], "status": results[s["index"]]["status"],
                     "candidate_count": len(s["candidate_ids"]),
                     "candidate_ids": s["candidate_ids"], "block_ids": s["block_ids"],
                     "context_block_ids": s["context_block_ids"],
                     "source": results[s["index"]]["source"],
                     "digest": results[s["index"]]["digest"],
                     "inputs": references[s["index"]],
                     "attempts": results[s["index"]]["attempts"],
                     "error": results[s["index"]]["error"]} for s in segments]}

    def valid(ids):
        merged, report = resilient_merge(segments, {i: results[i]["payload"] for i in ids},
                                         revision=revision)
        validate_global_proposal(json.dumps(merged, ensure_ascii=False), layout, project_id,
                                 sources, expected_version=12, budget_scale=max(1, len(ids)))
        return merged, report

    if not analyzed:
        _save(folder / "report.json", summary([]), settings.api_key)
        raise GenerationError("Nessuna sezione del modulo analizzata; nessun valore applicato")
    try:
        merged, report = valid(analyzed)
        included = analyzed
    except ValueError:
        # Deterministic search, no data change: add segments in order, exclude any segment
        # whose addition breaks the union, and record it.
        included = []
        for index in analyzed:
            try:
                valid([*included, index])
                included.append(index)
            except ValueError as exc:
                results[index].update(status="excluded_at_merge",
                                      error=f"{type(exc).__name__}: {str(exc)[:200]}")
        if not included:
            _save(folder / "report.json", summary([]), settings.api_key)
            raise GenerationError("Unione delle sezioni non valida; nessun valore applicato")
        merged, report = valid(included)
    _save(folder / "report.json", summary(included, report), settings.api_key)
    usage = {}
    for record in results.values():
        for attempt in record["attempts"]:
            for key, value in (attempt.get("usage") or {}).items():
                # Reasoning tokens are nested in completion_tokens_details.
                for name, count in (value.items() if isinstance(value, dict) else
                                    [(None, value)]):
                    name = f"{key}.{name}" if name else key
                    if isinstance(count, int):
                        usage[name] = usage.get(name, 0) + count
    metadata["segments"] = [{"index": s["index"], "status": results[s["index"]]["status"],
                             "source": results[s["index"]]["source"],
                             "attempts": len(results[s["index"]]["attempts"]),
                             "error": results[s["index"]]["error"]} for s in segments]
    metadata["segment_retries"] = budget["retries"]
    model = next((r.get("model") for r in results.values() if r.get("model")), settings.model)
    return json.dumps(merged, ensure_ascii=False, separators=(",", ":")), model, usage


async def _segmented_proposal(settings, data, root, metadata):
    """One call per FORM segment with the full context; no retries, no partial repair."""
    from app.compilation_segments import (
        MAX_CONCURRENT_SEGMENTS,
        instruction,
        merge,
        parse,
        partition,
    )

    segments = partition(data["form"])
    folder = root / "segments"
    folder.mkdir()
    results, gate = {}, asyncio.Semaphore(MAX_CONCURRENT_SEGMENTS)

    async def run(segment):
        target = folder / str(segment["index"])
        target.mkdir()
        # One segment is the whole FORM: the request stays the monolithic one.
        body = global_request(settings, data, thinking=settings.provider == "deepseek",
                              segment=instruction(segment, len(segments))
                              if len(segments) > 1 else None)
        _save(target / "request.json", body, settings.api_key)
        started = time.perf_counter()

        async def capture(response):
            metadata["http_calls"] += 1
            await response.aread()
            _save(target / "http-response.txt", response.text, settings.api_key)

        try:
            async with gate, httpx.AsyncClient(
                timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=15),
                event_hooks={"response": [capture]},
            ) as client:
                raw, model, usage = await asyncio.wait_for(request_model_content(
                    client, settings, body, TIMEOUT_SECONDS,
                    response_schema=data["schema_output"]), timeout=TIMEOUT_SECONDS)
            _save(target / "response.txt", raw, settings.api_key)
            results[segment["index"]] = {"status": "analyzed", "payload": parse(raw),
                                         "model": model, "usage": usage, "error": None}
        except (GenerationError, ValueError, TimeoutError, httpx.HTTPError) as exc:
            results[segment["index"]] = {"status": "failed", "payload": None, "model": None,
                                         "usage": None, "error": f"{type(exc).__name__}: "
                                         f"{str(exc)[:200]}"}
        results[segment["index"]]["seconds"] = time.perf_counter() - started

    await run(segments[0])  # Warms the shared prompt prefix for the other calls.
    await asyncio.gather(*(run(segment) for segment in segments[1:]))
    analyzed = {i: r["payload"] for i, r in results.items() if r["status"] == "analyzed"}
    summary = [{"index": s["index"], "status": results[s["index"]]["status"],
                "candidate_count": len(s["candidate_ids"]), "candidate_ids": s["candidate_ids"],
                "block_ids": s["block_ids"], "error": results[s["index"]]["error"],
                "usage": results[s["index"]]["usage"],
                "seconds": results[s["index"]]["seconds"]} for s in segments]
    if not analyzed:
        _save(folder / "report.json", {"segments": summary}, settings.api_key)
        raise GenerationError("Nessuna sezione del modulo analizzata; nessun valore applicato")
    merged, report = merge(segments, analyzed)
    report["segments"] = summary
    _save(folder / "report.json", report, settings.api_key)
    if report["over_limits"]:
        raise GenerationError("Proposte unite oltre i limiti del contratto: nessun valore")
    usage = {}
    for item in results.values():
        for key, value in (item["usage"] or {}).items():
            if isinstance(value, int):
                usage[key] = usage.get(key, 0) + value
    metadata["segments"] = [{k: s[k] for k in ("index", "status", "candidate_count", "error",
                                               "usage", "seconds")} for s in summary]
    model = next(r["model"] for r in results.values() if r["model"])
    return json.dumps(merged, ensure_ascii=False, separators=(",", ":")), model, usage


def registered_audit(data, layout, project_id, sources):
    """Validated audit plus receipts, derived as refreshed_audit does after a reply."""
    from app.compilation_branch_evidence import reconcile_branches
    from app.compilation_source_reuse import reuse_selected_person

    reused = reuse_selected_person(data, layout, project_id, sources)
    return reconcile_branches({**data, "audit": reused}, layout, project_id, sources)


def _save(path, value, secret):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    path.write_text((text.replace(secret, "[REDACTED]") if secret else text) + "\n",
                    encoding="utf-8", errors="backslashreplace")


def _complete(project_id, session_id, version, raw, audit, metadata):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, state = _row_state(db, project_id, session_id, version, allow_busy=True)
        version = state["global_compilation"].get("contract_version", 10)
        fresh = validated_audit(raw, sessions.read_original(row), project_id,
                                load_document_corpus(db, project_id),
                                state["global_compilation"],
                                get_storage_path().resolve()
                                / state["global_compilation"]["artifact_path"],
                                expected_version=version)
        base = {**state["global_compilation"], "audit": fresh}
        registered = {k: a for k, a in (metadata.get("dialogue") or {}).get("answers", {}).items()
                      if a.get("origin") == "initial_request"}
        if registered:
            base["dialogue"] = {"answers": registered}
            fresh = registered_audit(base, sessions.read_original(row), project_id,
                                     load_document_corpus(db, project_id))
        else:
            from app.compilation_source_reuse import reuse_selected_person

            fresh = reuse_selected_person(base, sessions.read_original(row), project_id,
                                          load_document_corpus(db, project_id))
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

        if claimed["global_compilation"].get("generation_revision") in {2, 3}:
            raw, model, usage = await _resilient_proposal(settings, data, root, metadata,
                                                          layout, project_id, sources,
                revision=claimed["global_compilation"]["generation_revision"])
        elif claimed["global_compilation"].get("generation_revision") == 1:
            raw, model, usage = await _segmented_proposal(settings, data, root, metadata)
        else:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=15),
                event_hooks={"response": [capture]},
            ) as client:
                raw, model, usage = await asyncio.wait_for(request_model_content(
                    client, settings, body, TIMEOUT_SECONDS,
                    response_schema=data["schema_output"]), timeout=TIMEOUT_SECONDS)
        _save(root / "response.txt", raw, settings.api_key)
        try:
            audit = validated_audit(raw, layout, project_id, sources,
                                    claimed["global_compilation"], root,
                                    expected_version=CURRENT_VERSION)
        except ValueError as exc:
            raise GenerationError("Proposta globale non valida; nessun valore applicato") from exc
        metadata.update(model=model, usage=usage, ai_seconds=time.perf_counter() - started)
        _save(root / "audit.json", audit, settings.api_key)
        from app.compilation_global_dialogue import narrate
        from app.compilation_source_reuse import reuse_selected_person

        metadata["reading_plan"] = data["reading_plan"]
        effective_data = {**initial_state(layout), "user_context": data.get("user_context", []),
                                            "catalog": data["form"], "audit": audit,
                                            "artifact_path": claimed["global_compilation"][
                                                "artifact_path"],
                                            "reading_plan": data["reading_plan"]}
        for revision in ("backend_revision", "option_authorization_revision",
                         "attribution_safety_revision", "dialogue_revision",
                         "generation_revision", "derivation_revision",
                         "narration_recovery_revision", "branch_scope_revision",
                         "hold_rereview_revision", "table_scope_revision"):
            if revision in claimed["global_compilation"]:
                effective_data[revision] = claimed["global_compilation"][revision]
            else:
                effective_data.pop(revision, None)
        audit = reuse_selected_person(effective_data, layout, project_id, sources)
        if effective_data.get("dialogue_revision") == 1:
            from app.compilation_decision_registry import register_initial_decisions
            from app.compilation_global_dialogue import question_pool

            current = {**effective_data, "audit": audit}
            registered = await register_initial_decisions(current, question_pool(current), root)
            if registered:
                # Applied like an ordinary reply: the audit is re-derived with the receipts.
                effective_data["dialogue"] = {"answers": registered}
                audit = registered_audit(effective_data, layout, project_id, sources)
        if audit != effective_data["audit"]:
            _save(root / "effective-audit.json", audit, settings.api_key)
            metadata["review_audit_name"] = "effective-audit.json"
        metadata["dialogue"] = await narrate({**effective_data, "audit": audit}, root)
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
            was_paused = data["paused"]
            data["paused"] = False
            from app.compilation_global_dialogue import PRESENTATION_VERSION

            dialogue = data.get("dialogue") or {}
            if (data.get("narration_recovery_revision") == 1
                    and dialogue.get("narration_recovery", {}).get("mode") == "degraded"):
                dialogue.update(phase="PENDING", question=None, resuming=True)
            if (not was_paused and data["phase"] == "REVIEW" and dialogue.get("question") and
                    dialogue.get("presentation_version") != PRESENTATION_VERSION):
                # Explicit resume refreshes old wording, never the underlying SOURCE audit.
                dialogue.update(phase="PENDING", question=None, latest_turn=None, resuming=True)
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
        if empty and (dialogue.get("phase") != "READY" or dialogue.get("error") or not (
            (session["chat"].get("question") or {}).get("kind") == "generate"
            or dialogue.get("empty_export_offered") is True
        )):
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


def refreshed_audit(db, row, state):
    """Revalidate the immutable model output and derive receipt-bound SOURCE reuse."""
    from app.compilation_branch_evidence import reconcile_branches
    from app.compilation_source_reuse import reuse_selected_person

    data = state["global_compilation"]
    folder = get_storage_path().resolve() / data["artifact_path"]
    layout, sources = sessions.read_original(row), load_document_corpus(db, row["project_id"])
    fresh = validated_audit(
        (folder / "response.txt").read_text(), layout, row["project_id"], sources, data, folder,
        expected_version=data["audit"].get("version", 10))
    reused = reuse_selected_person({**data, "audit": fresh}, layout, row["project_id"], sources)
    return reconcile_branches({**data, "audit": reused}, layout, row["project_id"], sources)


def _selected(row, state, request, db):
    if not request.allow_unresolved:
        raise HTTPException(409, "Conferma esplicitamente la generazione di una bozza parziale")
    data = state["global_compilation"]
    if data["phase"] != "REVIEW":
        raise HTTPException(409, "Completa l'analisi prima di rivedere le proposte")
    ids, conditions = request.candidate_ids, request.confirmed_condition_ids
    recovering = (data.get("narration_recovery_revision") == 1 and
                  (data.get("dialogue") or {}).get("narration_recovery", {}).get("mode")
                  == "degraded")
    if recovering:
        from app.compilation_global_dialogue import narration_source_ids

        if set(ids) - narration_source_ids(data):
            raise HTTPException(409, "Sintesi incompleta: proposta non revisionata o sospesa")
    if data.get("generation_revision") == 3:
        from app.compilation_global_dialogue import reviewed_unheld_ids

        # Rev 3 candidate: an explicit client selection cannot pass a proposal that the
        # chat export would exclude because it is unreviewed or held by the narrator.
        if set(ids) - reviewed_unheld_ids(data):
            raise HTTPException(409, "Proposta non revisionata dalla sintesi o sospesa")
    from app.compilation_form_applicability import blocked_fields as inapplicable
    from app.compilation_procedural_consent import blocked_fields
    from app.compilation_value_completeness import blocked_fields as incomplete

    if (set(ids) | set(request.user_candidate_ids)) & incomplete(data):
        raise HTTPException(409, "Completezza del valore composto incompleta o non dimostrata")
    if (set(ids) | set(request.user_candidate_ids)) & inapplicable(data):
        raise HTTPException(409, "Applicabilità FORM falsa o non dimostrata per la destinazione")
    if (set(ids) | set(request.user_candidate_ids)) & blocked_fields(data):
        raise HTTPException(409, "Dichiarazione procedurale senza conferma USER pertinente")
    # Only a USER value for the same destination may fill a section that was not analyzed
    # or whose local clause the model declared uncertain. Rev 3 also verifies its FORM scope.
    from app.compilation_scope_review import blocked_user_fields
    from app.compilation_segments import unverified_fields

    if (set(ids) & unverified_fields(data)
            or set(request.user_candidate_ids) & blocked_user_fields(data)):
        raise HTTPException(409, "Applicabilità non accertata: sezione del modulo non analizzata "
                            "o paragrafo FORM incerto")
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
    from app.compilation_branch_evidence import effective_user_values

    if any(cid not in effective_user_values(data)
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
    fresh = refreshed_audit(db, row, state)
    if recovering and set(ids) - narration_source_ids({**data, "audit": fresh}):
        raise HTTPException(409, "Sintesi incompleta: revisione della proposta non più valida")
    if data.get("generation_revision") == 3 and (
        set(ids) & unverified_fields({**data, "audit": fresh})
        or set(request.user_candidate_ids) & blocked_user_fields({**data, "audit": fresh})
    ):
        raise HTTPException(409, "Ambito FORM cambiato o non verificato alla rivalidazione")
    if (set(ids) | set(request.user_candidate_ids)) & incomplete({**data, "audit": fresh}):
        raise HTTPException(409, "Completezza del valore composto cambiata o non dimostrata")
    if (set(ids) | set(request.user_candidate_ids)) & inapplicable({**data, "audit": fresh}):
        raise HTTPException(409, "Applicabilità FORM cambiata o non dimostrata")
    refreshed = {f["candidate_id"]: f for f in fresh["fields"]}
    if any(refreshed[i] != fields[i] for i in ids):
        raise HTTPException(409, "Una SOURCE o una condizione è cambiata: ripeti l'analisi")
    if data.get("dialogue"):
        from app.compilation_global_dialogue import reviewed_unheld_ids

        # The chat builds this selection from its persisted state; no manual selection may
        # pass a proposal the chat export excludes as held or not reviewed by the summary.
        # A hold is released only through its recorded USER answer or a narrator review.
        if set(ids) - reviewed_unheld_ids(data):
            raise HTTPException(409, "Proposta sospesa o non revisionata dalla sintesi")
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
                               "source_evidence": [], **({"receipt_key": user["receipt_key"],
                                   "choice_group_id": user["choice_group_id"]}
                                   if user.get("receipt_key") else {})})
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
    with connection() as db:
        state = json.loads(sessions._row(db, project_id, session_id)["state_json"])
    data = state["global_compilation"]
    path = (root / data["artifact_path"] / data.get("review_audit_name", "audit.json")).resolve()
    if root not in path.parents or not path.is_file():
        raise HTTPException(404, "Report non trovato")
    return path
