from app.repository import _rerank_evidence


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
