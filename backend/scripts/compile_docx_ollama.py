"""Measure one real DOCX compilation using the project's saved Ollama profile.

Requests, raw responses and metrics stay in the ignored data directory. No
cloud fallback or second generation is allowed; errors are recorded as results.
"""

import argparse
import asyncio
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from app import ai_transport
from app import document_compilation as compilation
from app.ai_profiles import project_ai_context
from app.config import get_deepseek_settings
from app.document_compilation_routes import _persist
from app.docx_templates import inspect_docx
from app.repository import get_project


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


async def run(project_id: str, template: Path, output: Path, instructions: str, save: bool) -> bool:
    project = get_project(project_id)
    if not project:
        raise ValueError("Progetto non trovato")
    with project_ai_context(project_id):
        settings = get_deepseek_settings()
        if settings.provider != "ollama":
            raise ValueError("Seleziona un profilo Ollama nel progetto: nessuna API cloud ammessa")
        data = template.read_bytes()
        layout = inspect_docx(data)
        sources = compilation.load_compilation_sources(project_id)
        output.mkdir(parents=True, exist_ok=False)
        (output / "template.docx").write_bytes(data)
        (output / "system-prompt.txt").write_text(compilation.SYSTEM_PROMPT, encoding="utf-8")
        dump(
            output / "inputs.json",
            {
                "project_id": project_id,
                "model": settings.model,
                "base_url": settings.base_url,
                "context_window": settings.context_window,
                "prompt_version": compilation.PROMPT_VERSION,
                "max_output_tokens": compilation.SINGLE_CALL_MAX_OUTPUT_TOKENS,
                "timeout_seconds": compilation.SINGLE_CALL_TIMEOUT_SECONDS,
                "candidate_count": len(layout.candidate_ids),
                "instructions": instructions,
                "template_sha256": hashlib.sha256(data).hexdigest(),
                "source_coverage": sources.coverage(),
            },
        )
        dump(output / "context.json", sources.selected)
        print(f"Output: {output.resolve()}", flush=True)
        print(
            f"Modello: {settings.model}; candidati: {len(layout.candidate_ids)}; "
            f"contesto: {settings.context_window}; una sola richiesta",
            flush=True,
        )
        request = compilation.request_field_proposals
        original_object = ai_transport._object
        calls = 0

        async def recorded(prompt: str, **kwargs):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise RuntimeError("La prova consente una sola richiesta")
            dump(output / "request.json", json.loads(prompt))
            return await request(prompt, **kwargs)

        def recorded_response(response):
            dump(output / "provider-request.json", json.loads(response.request.content))
            (output / "provider-response.txt").write_text(response.text, encoding="utf-8")
            payload = original_object(response)
            dump(
                output / "provider-metrics.json",
                {
                    key: payload.get(key)
                    for key in (
                        "model",
                        "done",
                        "done_reason",
                        "total_duration",
                        "load_duration",
                        "prompt_eval_count",
                        "prompt_eval_cached_count",
                        "prompt_eval_duration",
                        "eval_count",
                        "eval_duration",
                    )
                },
            )
            return payload

        started = time.monotonic()
        try:
            with (
                patch.object(compilation, "request_field_proposals", side_effect=recorded),
                patch.object(ai_transport, "_object", side_effect=recorded_response),
            ):
                draft, report = await compilation.compile_document(
                    project_id,
                    project["title"],
                    data,
                    instructions,
                )
            (output / "bozza.docx").write_bytes(draft)
            dump(output / "report.json", report)
            result = {
                "success": True,
                "requests": calls,
                "elapsed_seconds": round(time.monotonic() - started, 2),
                "written_fields": report["written_field_count"],
                "blocked_fields": report["blocked_field_count"],
                "unclassified_fields": len(report["unclassified_fields"]),
                "total_tokens": report["total_tokens"],
                "execution": report["execution"],
            }
            if save:
                saved = _persist(project_id, template.name, data, draft, report)
                result["saved_run_id"] = saved["id"]
        except Exception as exc:
            result = {
                "success": False,
                "requests": calls,
                "elapsed_seconds": round(time.monotonic() - started, 2),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        dump(output / "result.json", result)
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        return result["success"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--instructions-file", type=Path)
    parser.add_argument("--save-in-project", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            Path(__file__).resolve().parents[1]
            / "data/single-call-gemma"
            / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        ),
    )
    args = parser.parse_args()
    instructions = (
        args.instructions_file.read_text(encoding="utf-8").strip() if args.instructions_file else ""
    )
    success = asyncio.run(
        run(
            args.project_id,
            args.template,
            args.output,
            instructions,
            args.save_in_project,
        )
    )
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()
