"""Real semantic router replay on a frozen, read-only dialogue checkpoint."""

import argparse
import asyncio
import copy
import json
import time
from pathlib import Path

from app import compilation_chat, intents
from app.config import use_ai_settings
from scripts.benchmark_compilation_dialogue import real_settings

ROOT = (Path(__file__).resolve().parents[2]
        / "backend/data/compilation-audit/conversation-flow-20261013")


async def main(args):
    settings = real_settings("minervino-di-lecce-elenco-sia")
    args.output.mkdir(parents=True, exist_ok=False)
    state = json.loads((ROOT / "diagnosis/session-payload.json").read_text())
    saved = sorted((ROOT / "diagnosis/analysis/dialogue").glob("*/result.json"),
                   key=lambda p: p.stat().st_mtime)
    # Preserve the actual asked group. It is not an invented gold or new analysis.
    context = json.loads(saved[0].read_text())
    state["chat"].update(question=context["question"], auto_continue=False, paused=False)
    state["global_compilation"]["dialogue"] = context
    calls = []
    original = intents.request_model_content

    def save(name, data):
        raw = json.dumps(data, ensure_ascii=False, indent=2)
        (args.output / name).write_text(raw.replace(settings.api_key, "[REDACTED]") + "\n")

    async def capture(client, config, body, timeout, **kwargs):
        index = len(calls) + 1
        entry = {"request": body, "schema": kwargs.get("response_schema")}
        calls.append(entry)
        start = time.perf_counter()
        raw, model, usage = await original(client, config, body, timeout, **kwargs)
        entry.update(raw=raw, model=model, usage=usage, seconds=time.perf_counter() - start)
        save(f"call-{index}.json", entry)
        return raw, model, usage

    intents.request_model_content = capture
    save("context.json", copy.deepcopy(state))
    with use_ai_settings(settings):
        result = await intents.plan_chat_turn("1 si 2 si e 3 lascia in bianco", [], [],
            compilation=compilation_chat.planner_context(state))
    save("result.json", {"intent": result.intent, "decision": result.decision.model_dump(),
                         "new_analysis_calls": 0, "persistence_mutations": 0})
    print(json.dumps({"calls": len(calls), "decision": result.decision.model_dump()},
                     ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(main(parser.parse_args()))
