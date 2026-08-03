from app.repository import _is_eligibility_query, _rerank_evidence


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


def test_eligibility_reranking_prioritizes_proponent_rules():
    candidates = [
        {
            "chunk_id": 1,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": 222,
            "content": (
                "Il Beneficiario puo presentare contestuale domanda di erogazione "
                "senza attendere il periodo di rendicontazione."
            ),
            "excerpt": "Il Beneficiario puo presentare domanda di erogazione...",
            "rank": -10.0,
        },
        {
            "chunk_id": 2,
            "file_id": 1,
            "source_name": "bando.pdf",
            "chunk_index": 76,
            "content": (
                "Possono presentare proposta progettuale in qualita di Soggetti proponenti "
                "esclusivamente gli Enti locali: Comuni, Citta metropolitana e Province."
            ),
            "excerpt": "Possono presentare proposta esclusivamente gli Enti locali...",
            "rank": -4.0,
        },
    ]

    results = _rerank_evidence(
        "Mapi puo presentare domanda direttamente?", candidates, limit=2
    )

    assert results[0]["chunk_id"] == 2
    assert results[0]["relevance"] > results[1]["relevance"]


def test_post_award_question_is_not_classified_as_eligibility():
    assert not _is_eligibility_query(
        "Il beneficiario puo presentare domanda di erogazione direttamente?"
    )
