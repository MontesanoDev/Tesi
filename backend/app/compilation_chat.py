"""Conversational projection and USER grounding, sharing the existing session domain."""

import hashlib
import json
import re
import unicodedata
from datetime import UTC, date, datetime
from typing import Literal

from pydantic import Field, model_validator

from app.compilation_applicability import explicit_condition_reply, known_applicability
from app.compilation_session_models import UserFieldInput
from app.document_compilation import StrictModel

MAX_AUTO_STEPS = 36
MAX_AUTO_SECONDS = 600


class ChatFieldReply(StrictModel):
    field_id: str = Field(min_length=1, max_length=80)
    action: str = Field(pattern="^(set|not_applicable|applicable)$")
    value: str | None = Field(default=None, max_length=1500)
    user_quote: str = Field(min_length=1, max_length=2000)


class ChatControl(StrictModel):
    kind: str = Field(pattern="^(unknown|skip|refuse|pause|resume|finish)$")
    field_id: str | None = Field(default=None, max_length=80)
    user_quote: str = Field(min_length=1, max_length=2000)


class ActiveFieldDecision(StrictModel):
    """Semantic reply only: recipient and USER excerpt belong to the backend."""

    action: Literal[
        "VALUE", "CONDITION_TRUE", "CONDITION_FALSE", "UNKNOWN", "SKIP",
        "REFUSE", "PAUSE", "FINISH", "CLARIFY",
    ]
    value: str | None = Field(default=None, min_length=1, max_length=1500)
    normalized_value: str | None = Field(default=None, min_length=1, max_length=1500)
    rationale: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def value_only_for_value(self):
        if self.action == "VALUE":
            if self.value is None:
                raise ValueError("VALUE richiede il valore letterale USER")
        elif self.value is not None or self.normalized_value is not None:
            raise ValueError("Solo VALUE può proporre un valore")
        return self


class ClarificationReply(ActiveFieldDecision):
    slot: int = Field(ge=1, le=4)
    user_quote: str = Field(min_length=1, max_length=2000)


class ClarificationDecision(StrictModel):
    action: Literal["ANSWER", "PAUSE", "FINISH"]
    replies: list[ClarificationReply] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def distinct_slots(self):
        if len({r.slot for r in self.replies}) != len(self.replies):
            raise ValueError("Slot duplicato")
        if self.action in {"PAUSE", "FINISH"} and self.replies:
            raise ValueError("PAUSE/FINISH non aggiorna campi")
        if any(r.action in {"PAUSE", "FINISH"} for r in self.replies):
            raise ValueError("PAUSE/FINISH riguarda la sessione, non un singolo elemento")
        return self


async def handle_group_decision(project_id, conversation_id, decision, session, message,
                                expected_version=None):
    from starlette.concurrency import run_in_threadpool

    from app import compilation_sessions as sessions
    from app.compilation_session_routes import api_errors
    from app.intents import ChatDecision, route_compilation_control

    protected = route_compilation_control(ChatDecision(
        action="reply", answer="Controllo", queries=[], target="source",
    ), message, session)
    literal = normalized(message).strip(" .!?")
    unknown = literal in {"non so", "non lo so"}
    if protected.action == "compilation_control" and protected.control.kind == "resume":
        return await handle_decision(project_id, conversation_id, protected, None, session,
                                     message, expected_version)
    if (decision.action == "FINISH" and not unknown) or (
        protected.action == "compilation_control" and protected.control.kind == "finish"
    ):
        return await handle_decision(
            project_id, conversation_id, ChatDecision(
                action="compilation_control", answer="", target="form", queries=[],
                control=ChatControl(kind="finish", user_quote=message),
            ), None, session, message, expected_version,
        )
    if protected.action == "compilation_control" and protected.control.kind == "pause":
        decision = ClarificationDecision(action="PAUSE")

    slots = ((session.get("chat") or {}).get("question") or {}).get("slots", [])
    collective = literal in {"no a entrambe", "no ad entrambe", "no a entrambi", "no ad entrambi"}
    all_negative = (collective and len(slots) == 2
                    and all(s["kind"] == "applicability" for s in slots))
    if slots and (unknown or decision.action == "ANSWER" and all_negative):
        targets = slots if all_negative or not decision.replies else [
            s for s in slots if any(r.slot == s["slot"] for r in decision.replies)
        ]
        decision = ClarificationDecision(action="ANSWER", replies=[
            ClarificationReply(slot=s["slot"], action="UNKNOWN" if unknown else "CONDITION_FALSE",
                               user_quote=message) for s in targets
        ])

    if decision.action == "PAUSE":
        after = await run_in_threadpool(
            sessions.chat_control, project_id, session["id"],
            expected_version or session["version"],
            ChatControl(kind="pause", user_quote=message),
        )
        return "Va bene, metto in pausa la compilazione. Potrai riprenderla quando vuoi.", {
            "session_id": after["id"], "action": "paused",
        }
    with api_errors():
        after, errors = await run_in_threadpool(
            sessions.apply_clarification_group, project_id, session["id"],
            expected_version or session["version"], decision.replies, message,
        )
    text = ("Ho registrato le tue risposte. " if decision.replies else "")
    if errors:
        text += "Restano da chiarire solo le risposte non univoche. "
    if after["chat"]["auto_continue"]:
        text += "Continuo a verificare le informazioni disponibili."
    elif after["chat"]["question"]:
        text += after["chat"]["question"]["message"]
    else:
        text += "Conservo le informazioni ancora aperte senza inventare valori."
    outcome = "clarify" if errors else "updated"
    if after["chat"]["deferred"] > session["chat"]["deferred"] and errors:
        outcome = "deferred"
    if decision.replies and all(r.action in {"UNKNOWN", "SKIP", "REFUSE"}
                               for r in decision.replies) and not errors:
        outcome = "deferred"
    return text, {"session_id": after["id"], "action": outcome}


def single_active_target(context):
    """Use a single, coherent backend question; never pick from multiple fields."""
    if not context or not context.get("enabled") or context.get("paused_by_user"):
        return None
    question = context.get("question") or {}
    ids, fields = question.get("field_ids", []), context.get("fields", [])
    if (question.get("kind") not in {"value", "applicability"} or len(ids) != 1
            or len(fields) != 1 or fields[0].get("id") != ids[0]):
        return None
    return ids[0]


def new_cycle(previous=None):
    return {
        **(previous or {}),
        "steps": 0,
        "started_at": datetime.now(UTC).isoformat(),
        "paused_reason": None,
        "clarification": None,
        "recovery_notice": None,
        "user_paused": False,
        "finish_requested": False,
        "clarification_mode": "grouped",
        "analysis_attempts": (previous or {}).get("analysis_attempts", {}).copy(),
        "active_clarifications": (previous or {}).get("active_clarifications", []),
    }


def field_fingerprint(field):
    relevant = {key: field.get(key) for key in (
        "status", "value", "requirement", "condition", "applicability",
        "applicability_confirmed", "alternatives", "source_evidence",
    )}
    return hashlib.sha256(json.dumps(relevant, sort_keys=True).encode()).hexdigest()


def is_deferred(field):
    disposition = field.get("conversation_disposition") or {}
    return disposition.get("fingerprint") == field_fingerprint(field)


def budget_available(workflow):
    return bool(
        workflow
        and workflow["steps"] < MAX_AUTO_STEPS
        and (datetime.now(UTC) - datetime.fromisoformat(workflow["started_at"])).total_seconds()
        < MAX_AUTO_SECONDS
        and not workflow.get("paused_reason")
        and not workflow.get("user_paused")
    )


def field_label(field):
    requirement = field.get("requirement") or {}
    name = requirement.get("name") or field["label"] or "questa voce del modulo"
    name = name.replace("_", " ")
    role = requirement.get("person_role")
    return f"{name} ({role})" if role else name


def chat_view(state):
    from app.compilation_clarifications import (
        automatic_fields,
        clarification_question,
        grouped,
        pending_slots,
    )
    from app.compilation_document_plan import needs_document_plan

    workflow = state.get("chat_workflow")
    fields = state["fields"]
    pending = sum(f["status"] == "PENDING" for f in fields)
    issues = [f for f in fields if f["status"] in {"MISSING", "AMBIGUOUS", "CONFLICTING"}]
    available = [f for f in issues if not is_deferred(f)]
    if grouped(state):
        eligible = {i for slot in pending_slots(state) for i in slot["field_ids"]}
        available = [f for f in available if f["id"] in eligible]
    dependency_pending = any(f["status"] == "PENDING" and f.get("awaiting_dependency_resolution")
                             for f in fields)
    technical_issues = [f for f in fields if f["status"] in {"PENDING", "MISSING"}
                        and f.get("validation_errors") and not is_deferred(f)]
    user_paused = bool(workflow and workflow.get("user_paused"))
    expired_lease = bool(
        state["status"] == "ANALYZING" and state.get("lease_until")
        and datetime.fromisoformat(state["lease_until"]) <= datetime.now(UTC)
    )
    question = None
    if grouped(state):
        question = clarification_question(state)
    if not grouped(state) and available and not user_paused and not dependency_pending:
        field = available[0]  # One question at a time; no association across unrelated fields.
        label, condition = field_label(field), field.get("condition")
        alternatives = list(dict.fromkeys(a["value"] for a in field["alternatives"]))
        if condition and known_applicability(field) is None:
            kind = "applicability"
            message = (f"Per «{label}», il modulo specifica «{condition}». "
                       "Questa condizione si applica al tuo caso?")
        elif alternatives:
            kind = "value"
            message = (
                f"Ho trovato valori diversi per «{label}»:\n"
                + "\n".join(f"• {value}" for value in alternatives)
                + "\nQuale devo utilizzare?"
            )
        elif field["status"] == "MISSING":
            kind = "value"
            message = f"Mi manca un valore verificato per «{label}». Qual è?"
        else:
            kind = "value"
            message = f"Devo chiarire la voce «{label}» del modulo. Che valore devo usare?"
        question = {"kind": kind, "field_ids": [field["id"]], "message": message}
    automatic_pending = grouped(state) and (
        automatic_fields(state) or needs_document_plan(state)) and budget_available(workflow)
    if not question and issues and not automatic_pending \
            and (not pending or grouped(state) and not automatic_fields(state)) \
            and not user_paused and not available:
        question = {
            "kind": "deferred_summary", "field_ids": [],
            "message": "Ho lasciato aperte le informazioni rinviate: "
            + ", ".join(field_label(f) for f in issues[:5])
            + (f" e altre {len(issues) - 5}" if len(issues) > 5 else "")
            + ". Non sono verificate. Potrai riprenderle quando avrai i dati.",
        }
        if technical_issues:
            question["message"] = (
                "Alcuni campi restano aperti perché non sono riuscito a interpretarli o "
                "a verificarli. Sono indicati nei dettagli della compilazione; puoi "
                "rivederli oppure esportare una bozza con le informazioni già verificate.")
    elif not question and state["status"] == "READY" and not user_paused:
        question = {
            "kind": "generate",
            "field_ids": [],
            "message": "Ho completato i campi valutati. Vuoi che generi il DOCX?",
        }
    if (question and workflow and workflow.get("clarification")
            and workflow.get("clarification_question") == {
                "kind": question["kind"], "field_ids": question["field_ids"],
            }):
        question = {**question, "message": workflow["clarification"]}
    return {
        "enabled": workflow is not None,
        "auto_continue": state["status"] in {"CREATED", "WAITING_FOR_USER"}
        and (bool(automatic_fields(state)) or needs_document_plan(state) if grouped(state)
             else pending > 0)
        and (bool(automatic_fields(state)) or needs_document_plan(state) if grouped(state) else
             not available or dependency_pending)
        and budget_available(workflow),
        "notice": (workflow or {}).get("recovery_notice") or (
            f"{len(technical_issues)} campi richiedono revisione per problemi di interpretazione "
            "o verifica. I dettagli indicano il motivo."
            if technical_issues and not automatic_fields(state) else None),
        "paused": user_paused or expired_lease or bool(
            workflow and workflow.get("paused_reason") == "model_error"
        ) or bool(
            pending
            and not available
            and state["status"] in {"CREATED", "WAITING_FOR_USER"}
            and not budget_available(workflow)
        ),
        "paused_by_user": user_paused,
        "finish_requested": bool(workflow and workflow.get("finish_requested")),
        "deferred": sum(is_deferred(f) for f in issues),
        "question": question,
        "analyzed": len(fields) - pending,
        "verified": sum(f["status"] == "RESOLVED" for f in fields),
        "user_provided": sum(f["status"] == "USER_PROVIDED" for f in fields),
        "remaining_questions": len(issues),
        "steps_used": workflow["steps"] if workflow else 0,
        "max_steps": MAX_AUTO_STEPS,
        "metrics": {"automatic_resolved": sum(f["status"] == "RESOLVED" for f in fields),
                    "user_required_fields": sum(
                        f.get("kind", "data") != "data" or (
                            bool(f.get("requirement"))
                            and f.get("search", {}).get("status") == "searched"
                        ) for f in issues
                    ) if grouped(state) else len(issues),
                    "user_turns": state.get("clarification_user_turns", 0)},
    }


def planner_context(session):
    view = chat_view(session)
    question = view["question"]
    asked = set(question["field_ids"]) if question else set()
    return {
        "session_id": session["id"],
        "enabled": view["enabled"],
        "version": session["version"],
        "status": session["status"],
        "paused": view["paused"],
        "paused_by_user": view["paused_by_user"],
        "question": question,
        "fields": [
            {
                "id": f["id"],
                "label": field_label(f),
                "kind": f.get("kind"),
                "condition": f.get("condition"),
                "alternatives": [a["value"] for a in f["alternatives"]],
            }
            for f in session["fields"]
            if f["id"] in asked
        ],
    }


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def explicit_finish_request(message):
    return bool(re.fullmatch(
        r"(?:no[,;]?\s+)?(?:per favore[,;]?\s+)?(?:"
        r"(?:finisci|termina|concludi) (?:la )?compilazione|"
        r"(?:fermati (?:ed? )?)?esporta (?:una |la )?bozza parziale"
        r")(?:[,;]? per favore)?", normalized(message).strip(" .!?"),
    ))


def contains_span(container, span):
    text, excerpt = normalized(container), normalized(span)
    if not excerpt:
        return False
    # A short quote cannot be cut out of another word ("No" inside "Non so",
    # or an identifier inside a different number). No fuzzy matching.
    left = r"(?<!\w)" if excerpt[0].isalnum() or excerpt[0] == "_" else ""
    right = r"(?!\w)" if excerpt[-1].isalnum() or excerpt[-1] == "_" else ""
    return re.search(left + re.escape(excerpt) + right, text) is not None


def numbered_answers(message):
    matches = list(re.finditer(r"(?:^|[;\n])\s*([1-4])[.):]\s+", message))
    return {int(match[1]): message[match.start():
            matches[index + 1].start() if index + 1 < len(matches) else len(message)]
            for index, match in enumerate(matches)}


def normalize_date(text):
    months = (
        "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre "
        "novembre dicembre"
    ).split()
    value = normalized(text)
    match = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", value)
    if match:
        day, month, year = map(int, match.groups())
    else:
        match = re.fullmatch(r"(\d{1,2}) (" + "|".join(months) + r") (\d{4})", value)
        if not match:
            return None
        day, month, year = int(match[1]), months.index(match[2]) + 1, int(match[3])
    try:
        return date(year, month, day).strftime("%d/%m/%Y")
    except ValueError:
        return None


def has_user_alternatives(message):
    return bool(re.search(r"\b(?:oppure|forse)\b|\s+o\s+", normalized(message)))


def user_updates(session, replies, message, *, question=None):
    question = question or chat_view(session)["question"]
    if not question or question["kind"] in {"generate", "deferred_summary"} or len(replies) != 1:
        raise ValueError("La risposta non individua un solo campo tra quelli chiesti")
    reply = replies[0]
    if reply.field_id not in question["field_ids"]:
        raise ValueError("La risposta si riferisce a un campo diverso da quello chiesto")
    quote = normalized(reply.user_quote)
    if not contains_span(message, reply.user_quote):
        raise ValueError("L'estratto USER non appartiene al messaggio")
    field = next(f for f in session["fields"] if f["id"] == reply.field_id)
    if reply.action == "not_applicable":
        negative = explicit_condition_reply(field.get("condition", ""), quote, applies=False)
        if question["kind"] == "applicability":
            negative = negative and explicit_condition_reply(
                field.get("condition", ""), message, applies=False,
            )
        if reply.value is not None or not (
            question["kind"] == "applicability"
            or re.search(r"non (?:è |e )?(?:applicabile|pertinente|riguarda)", quote)
        ):
            raise ValueError("La non applicabilità deve essere confermata esplicitamente")
        if not negative:
            raise ValueError("La risposta non conferma la non applicabilità")
        return [
            UserFieldInput(
                field_id=reply.field_id,
                action="not_applicable",
                reason=f"Indicazione USER: {reply.user_quote}",
            )
        ]
    if reply.action == "applicable":
        if (reply.value is not None or question["kind"] != "applicability"
                or not explicit_condition_reply(field.get("condition", ""), quote, applies=True)
                or not explicit_condition_reply(field.get("condition", ""), message, applies=True)):
            raise ValueError("L'applicabilità non è stata confermata esplicitamente")
        return []  # A confirmed condition is not a factual value for the field.
    if has_user_alternatives(message):
        # Even a literal proposal is not an authorized selection from an answer
        # that still expresses alternatives/uncertainty. Request a single value.
        raise ValueError("La risposta contiene alternative o incertezza")
    is_date = bool(re.search(r"\b(?:data|date)\b", field_label(field).casefold()))
    if is_date:
        # Multiple literal dates are not an authorized choice, even if the planner
        # proposes one of them. Ask for a single answer instead of guessing.
        spans = re.findall(
            r"\b\d{1,2}(?:[./-]\d{1,2}[./-]| [a-z]+ )\d{4}\b", normalized(message),
        )
        dates = {normalize_date(span) for span in spans} - {None}
        if len(dates) > 1:
            raise ValueError("Più date possibili: serve una scelta univoca")
    if not reply.value or not contains_span(reply.user_quote, reply.value):
        # Only a deterministically equivalent full date may differ from the USER span.
        if not is_date or not reply.value or normalize_date(reply.user_quote) != reply.value:
            raise ValueError("Il valore proposto non è presente nell'indicazione USER")
    if question["kind"] == "applicability":
        raise ValueError("Conferma di applicabilità: serve chiarire il valore della voce")
    if normalized(reply.value) in {"si", "sì", "no"} and field.get("kind", "data") == "data":
        raise ValueError("Una conferma generica non indica il valore del campo")
    value = reply.value
    if is_date:
        value = normalize_date(reply.value) or normalize_date(reply.user_quote) or value
    return [
        UserFieldInput(
            field_id=reply.field_id,
            action="set",
            value=value,
            reason=f"Indicazione USER: {reply.user_quote}",
        )
    ]


def active_session(project_id, conversation_id, form_id=None, session_id=None):
    from fastapi import HTTPException

    from app import compilation_sessions as sessions

    if session_id:
        session = sessions.get_session(project_id, session_id)
        if session["conversation_id"] != conversation_id or (
            form_id is not None and session["original_file_id"] != form_id
        ):
            raise HTTPException(404, "Sessione non appartenente a questa conversazione/modulo")
        return session
    summaries = sessions.list_sessions(project_id, conversation_id)
    match = next(
        (s for s in summaries if form_id is None or s["original_file_id"] == form_id), None
    )
    return sessions.get_session(project_id, match["id"]) if match else None


async def handle_decision(
    project_id, conversation_id, decision, selected_form, session, message, expected_version=None,
    *, semantic_condition=False,
):
    from fastapi import HTTPException
    from starlette.concurrency import run_in_threadpool

    from app import compilation_sessions as sessions
    from app.compilation_session_routes import api_errors

    action = decision.action
    pausing = action == "compilation_control" and decision.control.kind == "pause"
    if (session and expected_version is not None and session["version"] != expected_version
            and not pausing):
        raise HTTPException(409, "La domanda di compilazione è cambiata: rileggi la conversazione")
    with api_errors():
        if action == "compile":
            form_id = (
                selected_form["form_id"]
                if selected_form
                else session["form_id"]
                if session
                else None
            )
            if form_id is None:
                return "Seleziona con @ il modulo DOCX da compilare.", None
            session = await run_in_threadpool(
                sessions.create_session,
                project_id,
                form_id,
                conversation_id,
                start_in_chat=True,
            )
            return "Certo. Analizzo il modulo e verifico le informazioni disponibili.", {
                "session_id": session["id"],
                "action": "start",
            }
        if session is None:
            return "Seleziona il modulo e chiedimi di iniziare la compilazione.", None
        if action == "compilation_control":
            control = decision.control
            if not contains_span(message, control.user_quote):
                raise HTTPException(422, "Il controllo non è grounded nell'ultimo messaggio USER")
            if control.kind in {"pause", "resume", "finish"} and control.field_id is not None:
                raise HTTPException(422, "Pausa/ripresa riguarda la sessione, non un valore")
            after = await run_in_threadpool(
                sessions.chat_control, project_id, session["id"],
                expected_version if expected_version is not None else session["version"], control,
            )
            if control.kind == "finish":
                # Persist the stop first: a failed export must not start new questions.
                from app.docx_templates import DocumentInputError

                try:
                    after = await run_in_threadpool(
                        sessions.finalize_session, project_id, session["id"],
                        after["version"], True,
                    )
                except DocumentInputError:
                    return ("Mi fermo qui e conservo i dati. Una verifica sui valori blocca "
                            "l’export: puoi controllarli nei dettagli compilazione e riprovare.",
                            {"session_id": after["id"], "action": "paused"})
                return ("Va bene, mi fermo qui. Ho preparato una bozza parziale con i dati "
                        "verificati; i campi irrisolti restano aperti. Puoi scaricare il DOCX "
                        "e il report e revisionarli.",
                        {"session_id": after["id"], "action": "generated"})
            if control.kind == "pause":
                text = "Va bene, metto in pausa la compilazione. Potrai riprenderla quando vuoi."
                outcome = "paused"
            elif control.kind == "resume":
                text = "Riprendo la stessa compilazione dal punto in cui eravamo."
                outcome = "resumed"
            else:
                text = "Va bene, lascio questa voce non verificata e continuo con il resto."
                outcome = "deferred"
            if after["chat"]["question"] and control.kind != "pause":
                text += " " + after["chat"]["question"]["message"]
            return text, {"session_id": session["id"], "action": outcome}
        if session["chat"].get("paused_by_user"):
            return "La compilazione è in pausa. Chiedimi di riprenderla per proseguire.", {
                "session_id": session["id"], "action": "paused",
            }
        if action == "compilation_generate":
            if session["status"] not in {"READY", "GENERATED"} or session["open_issues"]:
                return "Ci sono ancora informazioni da chiarire prima di generare il documento.", {
                    "session_id": session["id"],
                    "action": "clarify",
                }
            await run_in_threadpool(
                sessions.finalize_session,
                project_id,
                session["id"],
                session["version"],
                False,
            )
            return "Ho terminato la compilazione. Puoi scaricare il DOCX e il report.", {
                "session_id": session["id"],
                "action": "generated",
            }
        try:
            if action == "compilation_clarify":
                raise ValueError("La risposta richiede un chiarimento")
            if semantic_condition:
                if has_user_alternatives(message):
                    raise ValueError("La risposta contiene alternative o incertezza")
                # The semantic planner answers the current condition. It does not
                # choose a field or a factual value; the backend bound this reply.
                reply = decision.field_replies[0]
                updates = [] if reply.action == "applicable" else [UserFieldInput(
                    field_id=reply.field_id, action="not_applicable",
                    reason=f"Indicazione USER: {message}",
                )]
            else:
                updates = user_updates(session, decision.field_replies, message)
            if not updates:
                await run_in_threadpool(
                    sessions.chat_clarification,
                    project_id,
                    session["id"],
                    session["version"],
                    None,
                    applicable_field=decision.field_replies[0].field_id,
                    user_quote=decision.field_replies[0].user_quote,
                )
                text = "Questa voce è applicabile. Verifico il valore nelle fonti."
            else:
                await run_in_threadpool(
                    sessions.update_fields,
                    project_id,
                    session["id"],
                    session["version"],
                    updates,
                    from_chat=True,
                )
                text = ("Questa voce non è applicabile. Continuo con il resto."
                        if updates[0].action == "not_applicable"
                        else "Ho registrato la tua indicazione. Proseguo con la compilazione.")
            return text, {"session_id": session["id"], "action": "updated"}
        except (ValueError, HTTPException) as error:
            if isinstance(error, HTTPException) and error.status_code != 422:
                raise
            clean = {**session, "chat_workflow": {
                **(session.get("chat_workflow") or {}), "clarification": None,
            }}
            question = chat_view(clean)["question"]
            if not question:
                text = "Non è chiaro quale campo vuoi aggiornare. Indica la voce del modulo."
            else:
                text = (
                    "Non ho modificato i valori: ho bisogno di un'indicazione univoca. "
                    + question["message"]
                )
            if isinstance(error, HTTPException):
                details = error.detail
                problems = (
                    details.get("errors", []) if isinstance(details, dict) else [str(details)]
                )
                text = "Il valore richiede una correzione: " + "; ".join(problems) + ". " + text
            after = await run_in_threadpool(
                sessions.chat_clarification,
                project_id,
                session["id"],
                session["version"],
                text,
                user_quote=message,
            )
            if after["chat"]["deferred"] > session["chat"]["deferred"]:
                text = "Non ho un'indicazione univoca: lascio questa voce aperta e passo oltre."
                if after["chat"]["question"]:
                    text += " " + after["chat"]["question"]["message"]
                return text, {"session_id": session["id"], "action": "deferred"}
            return text, {"session_id": session["id"], "action": "clarify"}


async def handle_active_decision(
    project_id, conversation_id, decision, selected_form, session, message, expected_version=None,
):
    """Bind a semantic decision to the persisted question, then reuse the domain."""
    from fastapi import HTTPException

    from app.intents import ChatDecision, route_compilation_control

    protected = route_compilation_control(ChatDecision(
        action="reply", answer="Controllo", target="source", queries=[],
    ), message, session)
    if protected.action == "compilation_control":
        return await handle_decision(project_id, conversation_id, protected, selected_form,
                                     session, message, expected_version)
    if decision.action == "FINISH":
        return await handle_decision(
            project_id, conversation_id, ChatDecision(
                action="compilation_control", answer="", target="form", queries=[],
                control=ChatControl(kind="finish", user_quote=message),
            ), selected_form, session, message, expected_version,
        )
    target = single_active_target(planner_context(session)) if session else None
    if target is None:
        raise HTTPException(409, "Non esiste una sola domanda attiva: rileggi la conversazione")
    semantic_condition = decision.action in {"CONDITION_TRUE", "CONDITION_FALSE"}
    if semantic_condition and chat_view(session)["question"]["kind"] != "applicability":
        decision = ActiveFieldDecision(action="CLARIFY")
        semantic_condition = False
    common = {"answer": "", "target": "form", "queries": []}
    if decision.action in {"UNKNOWN", "SKIP", "REFUSE", "PAUSE"}:
        internal = ChatDecision(**common, action="compilation_control", control=ChatControl(
            kind=decision.action.lower(), field_id=None if decision.action == "PAUSE" else target,
            user_quote=message,
        ))
    elif decision.action == "CLARIFY":
        internal = ChatDecision(**{**common, "answer": "Serve un'indicazione univoca"},
                                action="compilation_clarify")
    else:
        if (decision.normalized_value is not None
                and decision.normalized_value != decision.value
                and decision.normalized_value != normalize_date(decision.value)):
            # Never accept an arbitrary transformation of a USER value.
            internal = ChatDecision(**{**common, "answer": "Normalizzazione non verificabile"},
                                    action="compilation_clarify")
        else:
            internal = ChatDecision(**common, action="compilation_input", field_replies=[
                ChatFieldReply(
                    field_id=target, user_quote=message, value=decision.value,
                    action={"VALUE": "set", "CONDITION_TRUE": "applicable",
                            "CONDITION_FALSE": "not_applicable"}[decision.action],
                ),
            ])
        # Preserve the existing standalone-control safety boundary. It never
        # interprets applicability and gains no new keywords from this change.
        internal = route_compilation_control(internal, message, session)
    return await handle_decision(
        project_id, conversation_id, internal, selected_form, session, message, expected_version,
        semantic_condition=semantic_condition,
    )
