"""Create the Catanzaro and Minervino study projects in the configured app database."""

from pathlib import Path

from dotenv import load_dotenv

from app.artifacts import ensure_project_artifacts
from app.db import init_database
from app.repository import create_project, list_projects
from app.schemas import ProjectCreate

PROJECTS = (
    (
        "catanzaro-direzione-lavori-e-sicurezza",
        ProjectCreate(
            title="Catanzaro - Direzione lavori e sicurezza",
            description=(
                "Domanda per i servizi di direzione lavori e coordinamento della sicurezza "
                "in esecuzione delle nuove residenze universitarie della Fondazione Università "
                "Magna Graecia, III lotto. Caso didattico con dati aziendali simulati."
            ),
        ),
    ),
    (
        "minervino-di-lecce-elenco-sia",
        ProjectCreate(
            title="Minervino di Lecce - Elenco SIA",
            description=(
                "Domanda di iscrizione all'elenco del Comune di Minervino di Lecce per "
                "l'affidamento di servizi di ingegneria e architettura. "
                "Caso didattico con dati aziendali simulati."
            ),
        ),
    ),
)


def create_tender_projects() -> list[dict]:
    init_database()
    existing = list_projects()
    results = []
    for project_id, payload in PROJECTS:
        project = next(
            (
                item for item in existing
                if item["id"] == project_id or item["title"] == payload.title
            ),
            None,
        )
        created = project is None
        if created:
            project = create_project(payload)
        ensure_project_artifacts(project["id"])
        results.append({"id": project["id"], "title": project["title"], "created": created})
    return results


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    load_dotenv(root / "backend" / ".env")
    for result in create_tender_projects():
        action = "Creato" if result["created"] else "Già presente"
        print(f"{action}: {result['title']} ({result['id']})")


if __name__ == "__main__":
    main()
