"""Four frozen USER messages on a prepared FORM choice checkpoint, real routing/guard.

This is not a new SOURCE analysis or an HTTP session benchmark. No provider is
simulated. Validated semantic replies feed the same pure USER choice operation.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from app import intents
from app.compilation_choices import user_choice
from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_dialogue import question_pool
from app.compilation_global_sessions import initial_state
from app.config import use_ai_settings
from app.docx_templates import inspect_docx
from scripts.benchmark_compilation_dialogue import real_settings

FIXTURE = Path(__file__).resolve().parents[2] / "demo-documents/benchmark-checkbox/v1"


async def main(args):
    settings = real_settings("prova")
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, value):
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=2)
        path.write_text(raw.replace(settings.api_key, "[REDACTED]") + "\n")

    layout = inspect_docx((FIXTURE / "modulo.docx").read_bytes(), require_candidates=False)
    catalog = build_global_input(layout, "checkbox-lab", [])["form"]
    paragraphs = {p["id"]: p for b in catalog["blocks"] for p in b["paragraphs"]}
    # Authored checkpoint derived from this fixture's literal FORM, no gold values.
    origin = next(p for p in paragraphs.values() if p["text"] ==
                  "Partecipazione: selezionare una sola opzione.")
    options = {}
    for cid, c in catalog["candidates"].items():
        p = paragraphs.get(c["context_id"], {})
        if c["type"] == "checkbox" and any(label in p.get("text", "") for label in (
            "Partecipazione individuale", "In raggruppamento"
        )):
            label = p["text"].strip().removeprefix("☐").strip()
            options[cid] = {"label": label, "form": {"paragraph_id": p["id"],
                                                      "quote": p["text_with_choices"]}}
    raw = json.dumps({"version": 11, "fields": {}, "facts": {}, "bindings": {}, "conditions": {},
                      "choice_groups": {"g": {"label": "Forma di partecipazione",
                      "subject": "Richiedente", "property": "forma di partecipazione",
                      "selection": "single", "min_selected": 1, "options": options,
                      "form": {"paragraph_id": origin["id"], "quote": origin["text"]}}}})
    data = initial_state(layout)
    data.update(audit=validate_global_proposal(raw, layout, "checkbox-lab", [],
                                              expected_version=11),
                catalog=catalog)
    slot = question_pool(data)[0]
    slot["question"] = ("Come partecipa il richiedente: partecipazione individuale "
                        "oppure in raggruppamento?")
    context = {"enabled": True, "engine": "global", "status": "WAITING_FOR_USER",
               "paused": False, "paused_by_user": False, "fields": [],
               "question": {"kind": "clarifications", "field_ids": [], "slots": [slot],
                            "message": slot["question"]}}
    cases = json.loads((FIXTURE / "gold.json").read_text())["user_messages"]
    save("protocol.json", {"cases": cases, "gold_in_prompt": False, "context": context,
                           "provider": settings.model, "prepared_checkpoint": True,
                           "max_router_attempts": 2, "max_guard_calls": 1})
    original, calls, current = intents.request_model_content, [], ""

    async def observe(client, config, body, timeout, **kwargs):
        prefix = current + f"/call-{len(calls) + 1:02d}"
        save(prefix + "-request.json", {"body": body, "schema": kwargs.get("response_schema")})
        start = time.perf_counter()
        raw, model, usage = await original(client, config, body, timeout, **kwargs)
        record = {"raw": raw, "model": model, "usage": usage,
                  "seconds": time.perf_counter() - start}
        calls.append(record)
        save(prefix + "-response.json", record)
        return raw, model, usage

    intents.request_model_content = observe
    results = []
    for index, case in enumerate(cases):
        current, calls = f"case-{index + 1:02d}", []
        with use_ai_settings(settings):
            turn = await intents.plan_chat_turn(case["message"], [], compilation=context)
        decision = turn.decision
        updates = {}
        replies = getattr(decision, "replies", [])
        for reply in replies:
            if reply.action == "VALUE":
                updates = user_choice(data, slot, reply)
        chosen = next((r.selected_options for r in replies if r.action == "VALUE"), None)
        passed = (chosen == case.get("expected_options") if "expected_options" in case else
                  bool(replies) and replies[0].action == case["expected_action"])
        result = {"case": case, "decision": decision.model_dump(), "updates": updates,
                  "pass": passed, "calls": calls}
        results.append(result)
        save(current + "/result.json", result)
        save("results.json", results)
        print(json.dumps({"case": index + 1, "pass": passed,
                          "selected_options": chosen}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
