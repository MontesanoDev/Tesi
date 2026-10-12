"""Replay the recorded real checkpoint in a private snapshot; no new analysis.

Run from backend with PYTHONPATH=.; never touches live sessions or stored facts.
The archived analysis is real DeepSeek output, not a simulated provider response.
Routing, independent USER verification and narration use real DeepSeek again.
"""

import argparse
import asyncio
import copy
import importlib.util
import json
import shutil
from pathlib import Path

from app import compilation_sessions as sessions
from app.compilation_global import load_document_corpus, validate_global_proposal
from app.db import connection, get_storage_path

ARCHIVED = Path("data/compilation-audit/full-conversation-20261012").resolve()
ROOT = Path("data/compilation-audit/group-confirmations-20261012/replay").resolve()
spec = importlib.util.spec_from_file_location(
    "conversation_observer", ARCHIVED / "real-conversation.py")
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
observer.ROOT = ROOT
observer.RUNTIME = ROOT / "private-runtime"


def prepare():
    ROOT.mkdir(parents=True, exist_ok=False)
    observer.initialize()
    protocol = json.loads((ROOT / "protocol.json").read_text())
    protocol.update(prepared_checkpoints=True, new_analysis_calls=0, max_turns=3,
                    checkpoint_origin=str(ARCHIVED / "turn-03/state.json"),
                    analysis_reused_not_simulated=True,
                    planned_messages=[
                        "Confermo entrambe: la sezione delle società di ingegneria si applica "
                        "e il partecipante è quello indicato nelle fonti.",
                        "Sì, genera una bozza parziale con i dati disponibili, "
                        "lasciando vuote le parti irrisolte.",
                    ])
    observer.save("protocol.json", protocol)
    archived = json.loads((ARCHIVED / "turn-03/state.json").read_text())
    before = sessions.create_session("prova", protocol["form"]["id"],
                                     start_in_chat=True, engine="global")
    artifact = get_storage_path() / "prova/_global_compilations" / before["id"] / "replay"
    shutil.copytree(ARCHIVED / "analysis", artifact)
    with connection() as db:
        row = sessions._row(db, "prova", before["id"])
        state = json.loads(row["state_json"])
        fresh = validate_global_proposal((artifact / "response.txt").read_text(),
            sessions.read_original(row), "prova", load_document_corpus(db, "prova"),
            expected_version=10)
        assert fresh == json.loads((artifact / "audit.json").read_text())
        data = state["global_compilation"]
        data.update(phase="REVIEW", attempts=1, audit=fresh, paused=False,
                    artifact_path=str(artifact.relative_to(get_storage_path())),
                    dialogue=copy.deepcopy(archived["global_compilation"]["dialogue"]))
        assert not data["dialogue"].get("answers") and not data["dialogue"].get("user_values")
        assert len(data["dialogue"]["question"]["slots"]) == 2
        state.update(status="WAITING_FOR_USER", lease_until=None, last_error=None)
        prepared = sessions.save_state(db, row, state, "benchmark_real_checkpoint_replay")
    observer.save("checkpoint.json", prepared)
    observer.save("latest-state.json", prepared)
    observer.save("checkpoint-validation.json", {
        "original_sha256": prepared["template_sha256"],
        "fresh_audit_equals_archived": True,
        "source_proposals": prepared["global_compilation"]["proposal_count"],
        "active_questions": prepared["chat"]["question"],
        "new_analysis_calls": 0, "new_user_factual_values": 0,
    })


async def main(args):
    if args.operation == "prepare":
        prepare()
    elif args.operation == "turn":
        protocol = json.loads((ROOT / "protocol.json").read_text())
        await observer.run(argparse.Namespace(operation="turn", message=(
            protocol["planned_messages"][args.turn - 1])))
    else:
        spec = importlib.util.spec_from_file_location("verify_word", ARCHIVED / "verify-results.py")
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(ROOT)
        assert result["source_written"] == 12 and result["user_written"] == 0
        assert result["user_turns_including_start"] == 2
        answers = json.loads((ROOT / "turn-01/state.json").read_text())[
            "global_compilation"]["dialogue"]["answers"]
        assert len(answers) == 2
        assert all(a["action"] == "CONDITION_TRUE" and a["provenance"] == "USER"
                   for a in answers.values())
        assert all(result["integrity"].values())
        assert not any(c["stage"] == "analysis" for t in result["turns"] for c in t["calls"])
        shutil.rmtree(observer.RUNTIME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "turn", "verify"])
    parser.add_argument("--turn", type=int, choices=[1, 2])
    asyncio.run(main(parser.parse_args()))
