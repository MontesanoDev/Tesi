from app.db import connection, init_database
from app.repository import (
    _expand_neighbor_evidence,
    _neighbor_excerpt,
    _rerank_evidence,
)
from app.seed import seed_database


def test_temporal_reranking_prioritizes_explicit_dates():
    candidates = [
        {
            "chunk_id": 1,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": 4,
            "content": "Le scadenze di monitoraggio sono definite nel disciplinare.",
            "excerpt": "Le scadenze di monitoraggio...",
            "rank": -5.0,
        },
        {
            "chunk_id": 2,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": 12,
            "content": "Il termine e fissato alle ore 12.00 del 15.09.2025.",
            "excerpt": "Il termine e fissato...",
            "rank": -4.0,
        },
    ]

    results = _rerank_evidence("Qual e la scadenza?", candidates, limit=2)

    assert results[0]["chunk_id"] == 2
    assert results[0]["relevance"] > results[1]["relevance"]


def test_previous_neighbor_excerpt_preserves_section_boundary():
    content = (
        "Premessa generale. " * 30
        + "Possono presentare proposta esclusivamente gli Enti locali. "
        + "Altre disposizioni. " * 20
    )

    excerpt = _neighbor_excerpt(content, offset=-1)

    assert "Possono presentare proposta" in excerpt
    assert len(excerpt) <= 484


def test_neighbor_expansion_adds_previous_document_context(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "retrieval.db"))
    init_database()
    seed_database()
    project_id = "fondo-riqualificazione-2027"
    with connection() as db:
        file_id = db.execute(
            """
            INSERT INTO project_files (
                project_id, name, metadata, kind, status, sort_order
            ) VALUES (?, 'bando.txt', 'TXT', 'source', 'Indicizzato', 99)
            """,
            (project_id,),
        ).lastrowid
        db.executemany(
            """
            INSERT INTO document_chunks (
                project_id, file_id, chunk_index, content, char_count
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (project_id, file_id, 0, "Definizione del soggetto ammesso.", 33),
                (project_id, file_id, 1, "Il soggetto presenta la domanda.", 32),
            ],
        )
        anchor = db.execute(
            """
            SELECT
                c.id AS chunk_id, c.file_id, f.name AS source_name,
                c.chunk_index, c.content
            FROM document_chunks c
            JOIN project_files f ON f.id = c.file_id
            WHERE c.file_id = ? AND c.chunk_index = 1
            """,
            (file_id,),
        ).fetchone()

    expanded = _expand_neighbor_evidence(
        project_id,
        [{**dict(anchor), "excerpt": "domanda", "relevance": 5.0}],
        max_results=2,
    )

    assert [item["chunk_index"] for item in expanded] == [1, 0]
    assert expanded[1]["content"] == "Definizione del soggetto ammesso."
