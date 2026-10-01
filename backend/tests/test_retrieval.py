from app.db import connection, init_database
from app.repository import (
    _expand_neighbor_evidence,
    _neighbor_excerpt,
    _rerank_evidence,
)
from app.retrieval import expand_evidence_context, merge_evidence_results
from app.seed import seed_database


def test_multiple_queries_share_context_without_duplicates():
    groups = [
        [{"chunk_id": i} for i in range(1, 9)],
        [{"chunk_id": i} for i in [1, -1, -2, -3, -4, -5, -6, -7]],
        [{"chunk_id": i} for i in range(20, 28)],
    ]
    merged = merge_evidence_results(groups)
    assert [item["chunk_id"] for item in merged] == [1, 20, 2, -1, 21, 3, -2, 22]
    assert merge_evidence_results([[], groups[0]]) == groups[0]
    assert merge_evidence_results([]) == []


def test_merged_queries_preserve_neighbors_and_revalidate_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "merge.db"))
    init_database()
    seed_database()
    project = "fondo-riqualificazione-2027"
    groups = []
    with connection() as db:
        for name in ("riepilogo.txt", "contatti.txt"):
            file_id = db.execute(
                "INSERT INTO project_files(project_id,name,metadata,kind,status) "
                "VALUES (?,?, '', 'source', 'Indicizzato')", (project, name),
            ).lastrowid
            group = []
            for index in range(8):
                text = f"Contenuto {name} {index}"
                chunk_id = db.execute(
                    "INSERT INTO document_chunks"
                    "(project_id,file_id,chunk_index,content,char_count) "
                    "VALUES (?,?,?,?,?)", (project, file_id, index, text, len(text)),
                ).lastrowid
                if index % 2:
                    group.append({
                        "chunk_id": chunk_id, "file_id": file_id, "chunk_index": index,
                        "source_name": name, "content": "OBSOLETO", "excerpt": "OBSOLETO",
                        "relevance": 0.9,
                    })
            groups.append(group)
    anchors = merge_evidence_results(groups, limit=4)
    result = expand_evidence_context(project, anchors)
    assert len(result) == 8
    assert {item["source_name"] for item in result} == {"riepilogo.txt", "contatti.txt"}
    assert [(item["source_name"], item["chunk_index"]) for item in result[4:]] == [
        ("riepilogo.txt", 0), ("contatti.txt", 0), ("riepilogo.txt", 2), ("contatti.txt", 2),
    ]
    assert all(item["content"] != "OBSOLETO" for item in result)
    with connection() as db:
        db.execute("DELETE FROM project_files WHERE id=?", (groups[1][0]["file_id"],))
    remaining = expand_evidence_context(project, anchors)
    assert all(item["source_name"] == "riepilogo.txt" for item in remaining)
    assert expand_evidence_context("adeguamento-sismico-edificio-b", anchors) == []


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


def test_cross_index_reranking_prioritizes_query_coverage():
    candidates = [
        {
            "chunk_id": 1,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": 12,
            "content": "Requisiti tecnici e certificazione di sostenibilita del progetto.",
            "excerpt": "Requisiti tecnici...",
            "rank": -14.0,
        },
        {
            "chunk_id": -1,
            "file_id": -1,
            "source_name": "visura.pdf",
            "chunk_index": 2,
            "content": (
                "Mapi Ingegneria. Direttore tecnico Ing. Elisa Romano. "
                "Certificazione del sistema di gestione qualita ISO 9001:2015."
            ),
            "excerpt": "Direttore tecnico...",
            "rank": -2.6,
        },
    ]

    results = _rerank_evidence(
        "Chi e il direttore tecnico di Mapi Ingegneria e quale certificazione di qualita possiede?",
        candidates,
        limit=2,
    )

    assert results[0]["source_name"] == "visura.pdf"
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
