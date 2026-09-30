"""Replay a recorded DOCX compilation with frozen sources, without opening the app database."""

import argparse
import asyncio
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from app import document_compilation as compilation
from app.config import get_ai_settings
from app.docx_templates import inspect_docx


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


async def replay(audit: Path, output: Path):
    frozen = json.loads((audit / "batch-01.prompt.json").read_text())
    template = (audit / "output/template.docx").read_bytes()
    if hashlib.sha256(template).hexdigest() != frozen["template_sha256"]:
        raise ValueError("Il template non corrisponde al prompt registrato")
    coverage = frozen["source_coverage"]
    sources = compilation.CompilationSources(
        [item for item in frozen["sources"] if item["id"] != "user:instructions"],
        coverage["total_chunks"], coverage["total_characters"],
    )
    if sources.coverage() != coverage:
        raise ValueError("Le fonti non corrispondono alla copertura registrata")
    layout = inspect_docx(template)
    output.mkdir(parents=True, exist_ok=False)
    settings = get_ai_settings()
    dump(output / "inputs.json", {
        "previous_audit": str(audit.resolve()),
        "started_at": datetime.now(UTC).isoformat(),
        "mode": "frozen sources; no ingestion, database, API routes or project mutations",
        "prompt_version": compilation.PROMPT_VERSION,
        "configured_model": settings.model,
        "template_sha256": layout.sha256,
        "source_coverage": coverage,
        "source_catalog_sha256": hashlib.sha256(json.dumps(
            frozen["sources"], ensure_ascii=False, sort_keys=True,
        ).encode()).hexdigest(),
        "candidates": {"cells": len(layout.cells), "slots": len(layout.slots)},
        "code_sha256": {
            name: hashlib.sha256(
                (Path(compilation.__file__).parent / name).read_bytes()
            ).hexdigest()
            for name in ("document_compilation.py", "docx_templates.py")
        },
    })
    (output / "system-prompt.txt").write_text(compilation.SYSTEM_PROMPT, encoding="utf-8")
    request = compilation.request_field_proposals
    call_count = 0

    async def recorded(prompt):
        nonlocal call_count
        call_count += 1
        base = output / f"batch-{call_count:02d}"
        dump(base.with_suffix(".prompt.json"), json.loads(prompt))
        started = time.monotonic()
        try:
            content, model, tokens = await request(prompt)
        except Exception as exc:
            dump(base.with_suffix(".error.json"), {
                "error": str(exc), "elapsed_seconds": time.monotonic() - started,
            })
            raise
        base.with_suffix(".response.json").write_text(content, encoding="utf-8")
        dump(base.with_suffix(".meta.json"), {
            "model": model, "total_tokens": tokens,
            "elapsed_seconds": time.monotonic() - started,
        })
        print(f"Chiamata {call_count}: {tokens} token", flush=True)
        return content, model, tokens

    started = time.monotonic()
    try:
        with (
            patch.object(compilation, "load_compilation_sources", return_value=sources),
            patch.object(compilation, "request_field_proposals", side_effect=recorded),
        ):
            docx, report = await compilation.compile_document(
                "frozen-audit", frozen["project_title"], template, frozen["user_instructions"],
            )
    except Exception as exc:
        dump(output / "result.json", {
            "success": False, "error": str(exc), "seconds": time.monotonic() - started,
        })
        raise
    files = output / "output"
    files.mkdir()
    (files / "bozza.docx").write_bytes(docx)
    (files / "template.docx").write_bytes(template)
    dump(files / "report.json", report)
    result = {
        "success": True, "seconds": time.monotonic() - started,
        "model": report["model"], "total_tokens": report["total_tokens"],
        "written_fields": report["written_field_count"],
        "blocked_fields": report["blocked_field_count"], "execution": report["execution"],
        "output": str(output.resolve()),
    }
    dump(output / "result.json", result)
    print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live autorizza chiamate al modello configurato con le fonti registrate")
    if args.output.exists():
        parser.error("L'output esiste gia: non sovrascrivere prove precedenti")
    asyncio.run(replay(args.audit, args.output))


if __name__ == "__main__":
    main()
