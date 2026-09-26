"""Run a public DOCX case with synthetic company data and an isolated database."""

import argparse
import asyncio
import hashlib
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx

from app import document_compilation as compilation
from app.db import init_database
from app.document_compilation import SINGLE_CALL_TIMEOUT_SECONDS
from app.ingestion import SUPPORTED_EXTENSIONS
from app.main import app

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "catanzaro": {
        "directory": "catanzaro-dl-cse",
        "title": "Catanzaro DL CSE - prova isolata",
        "sources": ("originali/bando.pdf", "originali/disciplinare.pdf"),
        "template": "modello/domanda-partecipazione.docx",
    },
    "minervino": {
        "directory": "minervino-elenco-sia",
        "title": "Minervino elenco SIA - prova isolata",
        "sources": ("originali/avviso.pdf",),
        "template": "originali/domanda-iscrizione.docx",
    },
    "trapani": {
        "directory": "trapani-green",
        "title": "Trapani Green - prova isolata",
        "sources": ("originali/avviso.pdf", "originali/disciplinare.pdf"),
        "template": "originali/manifestazione-interesse.docx",
    },
}


def case_instructions(case: str) -> str:
    if case != "catanzaro":
        path = ROOT / "demo-documents/bandi" / CASES[case]["directory"] / "istruzioni.txt"
        return path.read_text(encoding="utf-8").strip()
    return (
        "Prova esclusivamente didattica con le fonti aziendali simulate Mapi. "
        "Per questa prova scegliamo il ramo societa di ingegneria, "
        "partecipazione singola, sottoscrittore Luca Ferri. "
        "Proponi i dati anagrafici nella prima tabella e nella sezione 5.d; "
        "segnala i mancanti. Non compilare altri rami, firme o dichiarazioni. "
        "Non attestare requisiti alla data della gara: "
        "la fonte e simulata e successiva."
    )


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


async def run(output: Path, company_file: Path | None = None, case: str = "catanzaro") -> None:
    config = CASES[case]
    folder = ROOT / "demo-documents/bandi" / config["directory"]
    source_paths = [folder / name for name in config["sources"]]
    template = folder / config["template"]
    company = company_file or ROOT / "demo-documents/visura-mapi-ingegneria-simulata.pdf"
    instructions = case_instructions(case)
    input_hashes = {
        str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path):
            hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [*source_paths, template, company]
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "template.docx").write_bytes(template.read_bytes())
    (output / "system-prompt.txt").write_text(compilation.SYSTEM_PROMPT, encoding="utf-8")
    dump(output / "inputs.json", {
        "case": case, "started_at": datetime.now(UTC).isoformat(),
        "instructions": instructions, "input_sha256": input_hashes,
        "prompt_version": compilation.PROMPT_VERSION,
        "code_sha256": {
            name: hashlib.sha256((ROOT / "backend/app" / name).read_bytes()).hexdigest()
            for name in ("document_compilation.py", "docx_templates.py")
        },
    })
    request = compilation.request_field_proposals
    call_count = 0

    async def recorded(prompt: str, **request_options):
        nonlocal call_count
        call_count += 1
        base = output / f"batch-{call_count:02d}"
        dump(base.with_suffix(".prompt.json"), json.loads(prompt))
        started = time.monotonic()
        try:
            content, model, tokens = await request(prompt, **request_options)
        except Exception as exc:
            dump(base.with_suffix(".error.json"), {"error": str(exc)})
            raise
        base.with_suffix(".response.json").write_text(content, encoding="utf-8")
        dump(base.with_suffix(".meta.json"), {
            "model": model, "total_tokens": tokens,
            "elapsed_seconds": time.monotonic() - started,
        })
        print(f"Chiamata {call_count}: {tokens} token", flush=True)
        return content, model, tokens

    # Scope environment changes to this run, also when called from tests.
    with TemporaryDirectory(prefix="mapi-docx-demo-") as temporary, patch.dict(os.environ):
        root = Path(temporary)
        os.environ["MAPI_DB_PATH"] = str(root / "demo.db")
        os.environ["MAPI_STORAGE_PATH"] = str(root / "uploads")
        os.environ["MAPI_KNOWLEDGE_PATH"] = str(root / "knowledge")
        init_database()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://demo",
            timeout=SINGLE_CALL_TIMEOUT_SECONDS + 60,
        ) as client:
            response = await client.post(
                "/api/projects",
                json={
                    "title": config["title"],
                    "description": "Compilazione dimostrativa, non una candidatura reale",
                },
            )
            response.raise_for_status()
            project = response.json()["id"]
            for path in source_paths:
                response = await client.post(
                    f"/api/projects/{project}/files",
                    files={"file": (path.name, path.read_bytes(), "application/pdf")},
                )
                response.raise_for_status()
            response = await client.post(
                "/api/global-knowledge/files",
                data={"category": "company"},
                files={"file": (
                    company.name,
                    company.read_bytes(),
                    SUPPORTED_EXTENSIONS[company.suffix.lower()],
                )},
            )
            response.raise_for_status()
            print(
                "Generazione DeepSeek sul caso demo, senza modificare il database dell'app...",
                flush=True,
            )
            started = time.monotonic()
            with patch.object(compilation, "request_field_proposals", side_effect=recorded):
                response = await client.post(
                    f"/api/projects/{project}/document-compilations",
                    files={
                        "file": (
                            template.name,
                            template.read_bytes(),
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                    },
                    data={"instructions": instructions},
                )
            elapsed = time.monotonic() - started
            if response.status_code != 201:
                dump(output / "result.json", {
                    "success": False, "status_code": response.status_code,
                    "error": response.text, "elapsed_seconds": elapsed,
                })
                raise RuntimeError(
                    f"Compilazione fallita ({response.status_code}): {response.text}"
                )
            run = response.json()
            files = {}
            for kind, url in run["downloads"].items():
                downloaded = await client.get(url)
                downloaded.raise_for_status()
                files[kind] = downloaded.content
            for kind, name in (
                ("docx", "bozza.docx"),
                ("template", "template.docx"),
                ("report", "report.json"),
            ):
                (output / name).write_bytes(files[kind])
            report = run["report"]
            dump(output / "result.json", {
                "success": True, "elapsed_seconds": elapsed,
                "written_fields": report["written_field_count"],
                "total_tokens": report["total_tokens"], "execution": report["execution"],
            })
            print(
                json.dumps(
                    {
                        "output": str(output.resolve()),
                        "model": report["model"],
                        "written_fields": report["written_field_count"],
                        "unresolved_fields": report["unresolved_field_count"],
                        "source_coverage": report["source_coverage"],
                        "total_tokens": report["total_tokens"],
                        "execution": report["execution"],
                        "ready_for_submission": False,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="catanzaro")
    parser.add_argument("--live", action="store_true", help="Consenti chiamate DeepSeek a consumo")
    parser.add_argument(
        "--company-file", type=Path,
        help="Fonte aziendale simulata PDF, TXT o MD; di default usa la visura demo",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "backend/data/docx-demo" / datetime.now(UTC).strftime("%Y%m%d-%H%M%S"),
    )
    args = parser.parse_args()
    if not args.live:
        parser.error(
            "Usa --live per autorizzare le chiamate API a consumo con soli dati dimostrativi"
        )
    if args.output.exists():
        parser.error("La cartella di output esiste gia; scegline una nuova")
    if args.company_file is not None and (
        not args.company_file.is_file()
        or args.company_file.suffix.lower() not in SUPPORTED_EXTENSIONS
    ):
        parser.error("La fonte aziendale deve essere un file PDF, TXT o MD esistente")
    asyncio.run(run(args.output, args.company_file, args.case))


if __name__ == "__main__":
    main()
