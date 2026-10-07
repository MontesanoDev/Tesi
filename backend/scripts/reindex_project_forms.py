"""Explicitly extract/rechunk archived DOCX/TXT forms without changing originals."""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from app.db import get_db_path
from app.project_forms import list_forms, reindex_form
from app.retrieval_settings import resolve_settings
from app.vector_retrieval import run_vector_search


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="ID del progetto da reindicizzare")
    parser.add_argument("--form-id", type=int, help="Limita l'operazione a questo modulo")
    parser.add_argument(
        "--sync-vectors", action="store_true", help="Sincronizza anche Qdrant dopo l'estrazione",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    load_dotenv(root / "backend" / ".env")
    if not get_db_path().is_file():
        parser.error("Database non trovato: avvia prima l'applicazione/configura MAPI_DB_PATH")
    settings = resolve_settings() if args.sync_vectors else None
    if settings is not None and settings.backend != "qdrant":
        parser.error("--sync-vectors richiede la ricerca Qdrant configurata")
    forms = list_forms(args.project)
    if args.form_id is not None:
        forms = [form for form in forms if form["id"] == args.form_id]
        if not forms:
            parser.error("Modulo non presente nel progetto selezionato")
    for form in forms:
        count = reindex_form(args.project, form["id"])
        print(f"{form['id']}: {form['name']} — {count} frammenti")
    if settings is not None:
        status = run_vector_search(settings)
        print(f"Qdrant: {status['indexed_chunks']} frammenti sincronizzati")


if __name__ == "__main__":
    main()
