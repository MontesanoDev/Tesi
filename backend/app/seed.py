from __future__ import annotations

from app.db import connection

PROJECTS = [
    (
        "fondo-riqualificazione-2027",
        "Fondo Riqualificazione 2027",
        "Candidatura per interventi di riqualificazione edilizia",
        "Bozza pronta",
        "success",
        "Aggiornato ora",
        "Usa solo informazioni presenti nelle fonti e segnala sempre i dati mancanti.",
        12,
        4,
        14,
        1,
    ),
    (
        "adeguamento-sismico-edificio-b",
        "Adeguamento sismico - Edificio B",
        "Intervento strutturale e adeguamento dell'accessibilita",
        "Da verificare",
        "warning",
        "Aggiornato ieri",
        "Cita le fonti tecniche e separa sempre i dati confermati dalle ipotesi.",
        8,
        2,
        9,
        3,
    ),
    (
        "efficientamento-rete-idrica",
        "Efficientamento rete idrica",
        "Monitoraggio perdite e riabilitazione della rete",
        "In analisi",
        "info",
        "Aggiornato 3 giorni fa",
        "Evidenzia i requisiti mancanti prima di proporre una bozza.",
        7,
        3,
        6,
        4,
    ),
]

COMPANY_FACTS = [
    (
        "legal_name",
        "Ragione sociale",
        "Mapi Ingegneria S.r.l.",
        1,
        1,
    ),
    (
        "organization_type",
        "Tipo di soggetto",
        "Societa privata di ingegneria civile",
        1,
        2,
    ),
    (
        "operating_role",
        "Ruolo operativo",
        "Consulenza tecnica e supporto alla progettazione per enti committenti",
        1,
        3,
    ),
]


def seed_database() -> None:
    with connection() as db:
        db.executemany(
            """
            INSERT OR IGNORE INTO company_facts (
                key, label, value, verified, sort_order
            ) VALUES (?, ?, ?, ?, ?)
            """,
            COMPANY_FACTS,
        )
        if db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] > 0:
            return

        db.executemany(
            """
            INSERT INTO projects (
                id, title, description, status, status_tone, updated_label,
                instructions, shared_source_count, model_count,
                call_fact_count, missing_fact_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            PROJECTS,
        )

        project_id = "fondo-riqualificazione-2027"
        db.executemany(
            """
            INSERT INTO project_files (
                project_id, name, metadata, kind, status, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    project_id,
                    "Fondo_Riqualificazione_2027.pdf",
                    "PDF · 2,4 MB · fonte del progetto",
                    "source",
                    "Indicizzato",
                    1,
                ),
                (
                    project_id,
                    "Modulo_Candidatura_A.pdf",
                    "PDF · modello di compilazione",
                    "template",
                    "Modello",
                    2,
                ),
            ],
        )

        db.executemany(
            """
            INSERT INTO knowledge_sources (
                project_id, name, detail, scope, tone, item_count, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    project_id,
                    "Dati estratti dal bando",
                    "Call Facts verificati",
                    "project",
                    "success",
                    14,
                    1,
                ),
                (project_id, "Dati aziendali", "Mapi Ingegneria S.r.l.", "global", "info", 28, 2),
                (project_id, "Modelli", "Modelli di candidatura", "project", "purple", 4, 3),
            ],
        )

        db.executemany(
            """
            INSERT INTO conversations (
                id, project_id, title, metadata, target, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "requisiti-ammissibilita",
                    project_id,
                    "Requisiti e ammissibilita",
                    "5 minuti fa · 3 fonti citate",
                    None,
                    1,
                ),
                (
                    "compilazione-modulo-a",
                    project_id,
                    "Compilazione Modulo A",
                    "Ieri · bozza da verificare",
                    "review",
                    2,
                ),
            ],
        )

        db.executemany(
            """
            INSERT INTO document_fields (
                project_id, section, label, value, provenance,
                source_kind, status, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    project_id,
                    "Dati del proponente",
                    "Ragione sociale",
                    "Mapi Ingegneria S.r.l.",
                    "Profilo aziendale · p.1",
                    "company",
                    "verified",
                    1,
                ),
                (
                    project_id,
                    "Dati del proponente",
                    "Partita IVA",
                    "IT01234567890",
                    "Profilo aziendale · p.1",
                    "company",
                    "verified",
                    2,
                ),
                (
                    project_id,
                    "Dati del proponente",
                    "Sede legale",
                    "Bari, Italia",
                    "Profilo aziendale · p.1",
                    "company",
                    "verified",
                    3,
                ),
                (
                    project_id,
                    "Dati del progetto",
                    "Titolo del progetto",
                    "Riqualificazione energetica scuola",
                    "Scheda progetto · p.1",
                    "project",
                    "verified",
                    4,
                ),
                (
                    project_id,
                    "Dati del progetto",
                    "Budget totale del progetto",
                    None,
                    "Non presente nelle fonti collegate",
                    "user",
                    "missing",
                    5,
                ),
                (
                    project_id,
                    "Dati del progetto",
                    "Durata prevista",
                    "18 mesi",
                    "Scheda candidatura · p.2",
                    "project",
                    "verified",
                    6,
                ),
            ],
        )
