"""Run the Catanzaro DOCX flow with public/synthetic inputs and an isolated database."""

import argparse
import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx

from app.db import init_database
from app.document_compilation import COMPILATION_TIMEOUT_SECONDS
from app.ingestion import SUPPORTED_EXTENSIONS
from app.main import app

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "demo-documents/bandi/catanzaro-dl-cse"


async def run(output: Path, company_file: Path | None = None) -> None:
    with TemporaryDirectory(prefix="mapi-docx-demo-") as temporary:
        root = Path(temporary)
        os.environ["MAPI_DB_PATH"] = str(root / "demo.db")
        os.environ["MAPI_STORAGE_PATH"] = str(root / "uploads")
        os.environ["MAPI_KNOWLEDGE_PATH"] = str(root / "knowledge")
        init_database()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://demo",
            timeout=COMPILATION_TIMEOUT_SECONDS + 60,
        ) as client:
            response = await client.post(
                "/api/projects",
                json={
                    "title": "Catanzaro DL CSE - prova isolata",
                    "description": "Compilazione dimostrativa, non una candidatura reale",
                },
            )
            response.raise_for_status()
            project = response.json()["id"]
            for path in (CASE / "originali/bando.pdf", CASE / "originali/disciplinare.pdf"):
                response = await client.post(
                    f"/api/projects/{project}/files",
                    files={"file": (path.name, path.read_bytes(), "application/pdf")},
                )
                response.raise_for_status()
            company = company_file or ROOT / "demo-documents/visura-mapi-ingegneria-simulata.pdf"
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
            template = CASE / "modello/domanda-partecipazione.docx"
            print(
                "Generazione DeepSeek sul caso demo, senza modificare il database dell'app...",
                flush=True,
            )
            response = await client.post(
                f"/api/projects/{project}/document-compilations",
                files={
                    "file": (
                        template.name,
                        template.read_bytes(),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
                data={
                    "instructions": (
                        "Prova esclusivamente didattica con le fonti aziendali simulate Mapi. "
                        "Per questa prova scegliamo il ramo societa di ingegneria, "
                        "partecipazione singola, sottoscrittore Luca Ferri. "
                        "Proponi i dati anagrafici nella prima tabella e nella sezione 5.d; "
                        "segnala i mancanti. Non compilare altri rami, firme o dichiarazioni. "
                        "Non attestare requisiti alla data della gara: "
                        "la fonte e simulata e successiva."
                    )
                },
            )
            if response.status_code != 201:
                raise RuntimeError(
                    f"Compilazione fallita ({response.status_code}): {response.text}"
                )
            run = response.json()
            files = {}
            for kind, url in run["downloads"].items():
                downloaded = await client.get(url)
                downloaded.raise_for_status()
                files[kind] = downloaded.content
            output.mkdir(parents=True, exist_ok=False)
            for kind, name in (
                ("docx", "bozza.docx"),
                ("template", "template.docx"),
                ("report", "report.json"),
            ):
                (output / name).write_bytes(files[kind])
            report = run["report"]
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
    asyncio.run(run(args.output, args.company_file))


if __name__ == "__main__":
    main()
