import pytest

from app.call_facts import (
    CallFactsFormatError,
    available_project_facts_markdown,
    parse_call_facts_markdown,
    render_call_facts_document,
    revise_call_fact,
)
from app.fact_extraction import ExtractedFact, render_call_facts_markdown


def extracted_markdown() -> str:
    return render_call_facts_markdown(
        "progetto-test",
        [
            ExtractedFact("Scadenza", "15 settembre 2025", [1]),
            ExtractedFact("Soggetto ammesso", "Comune", [2]),
        ],
        ["Codice CUP"],
        [
            {"source_name": "bando.pdf", "chunk_index": 8},
            {"source_name": "bando.pdf", "chunk_index": 10},
        ],
        "deepseek-test",
    )


def test_call_facts_round_trip_preserves_ids_sources_and_missing_information():
    document = parse_call_facts_markdown(extracted_markdown())

    assert document.project_id == "progetto-test"
    assert document.model == "deepseek-test"
    assert document.pending_count == 2
    assert document.verified_count == 0
    assert document.facts[0].id.startswith("cf-")
    assert document.facts[0].sources[0].fragment == 9
    assert document.missing_information == ["Codice CUP"]

    rendered = render_call_facts_document(document)
    reparsed = parse_call_facts_markdown(rendered)
    assert reparsed == document
    assert f"<!-- fact-id: {document.facts[0].id} -->" in rendered


def test_review_actions_control_which_facts_are_indexable():
    document = parse_call_facts_markdown(extracted_markdown())
    first, second = document.facts

    verified = revise_call_fact(document, first.id, "verify")
    indexed = available_project_facts_markdown(render_call_facts_document(verified))
    assert "15 settembre 2025" in indexed
    assert "Soggetto ammesso" in indexed
    assert verified.facts[0].status == "verified"

    edited = revise_call_fact(
        verified,
        first.id,
        "edit",
        title="Termine candidatura",
        value="Ore 12 del 15 settembre 2025",
    )
    assert edited.facts[0].status == "pending"
    assert edited.facts[0].id == first.id
    indexed = available_project_facts_markdown(render_call_facts_document(edited))
    assert "Ore 12 del 15 settembre 2025" in indexed
    assert "Corretto dall'utente" in indexed

    discarded = revise_call_fact(edited, first.id, "discard")
    assert discarded.discarded_count == 1
    indexed = available_project_facts_markdown(render_call_facts_document(discarded))
    assert "Termine candidatura" not in indexed
    assert "Soggetto ammesso" in indexed
    restored = revise_call_fact(discarded, first.id, "restore")
    assert restored.facts[0].status == "pending"
    assert "Termine candidatura" in available_project_facts_markdown(
        render_call_facts_document(restored)
    )

    with pytest.raises(CallFactsFormatError):
        revise_call_fact(restored, second.id, "edit", title="", value="Dato")


def test_fact_without_sources_cannot_be_verified():
    markdown = (
        "# Call Facts\n\n"
        "## Dato manuale\n\n"
        "**Valore:** Da controllare\n\n"
        "**Stato:** Da verificare\n\n"
        "**Fonti:**\n"
    )
    document = parse_call_facts_markdown(markdown)

    with pytest.raises(CallFactsFormatError, match="senza fonti"):
        revise_call_fact(document, document.facts[0].id, "verify")
    assert available_project_facts_markdown(markdown) == ""


def test_unverified_extractions_and_corrections_are_available_with_provenance():
    document = parse_call_facts_markdown(extracted_markdown())
    first = document.facts[0]
    indexed = available_project_facts_markdown(extracted_markdown())
    assert "15 settembre 2025" in indexed
    assert "Comune" in indexed
    assert "Estratto automaticamente" in indexed
    assert "bando.pdf, frammento 9" in indexed
    assert "verificati" not in indexed

    edited = revise_call_fact(
        document, first.id, "edit", title=first.title, value="16 settembre 2025"
    )
    rendered = render_call_facts_document(edited)
    assert parse_call_facts_markdown(rendered).facts[0].origin == "user_corrected"
    indexed = available_project_facts_markdown(rendered)
    assert "16 settembre 2025" in indexed
    assert "15 settembre 2025" not in indexed
    assert "Corretto dall'utente" in indexed
    assert "bando.pdf, frammento 9" in indexed

    discarded = revise_call_fact(edited, first.id, "discard")
    indexed = available_project_facts_markdown(render_call_facts_document(discarded))
    assert "16 settembre 2025" not in indexed
    restored = revise_call_fact(discarded, first.id, "restore")
    assert restored.facts[0].origin == "user_corrected"
    indexed = available_project_facts_markdown(render_call_facts_document(restored))
    assert "16 settembre 2025" in indexed


def test_legacy_pending_and_verified_states_keep_ids_and_values():
    legacy = extracted_markdown().replace("**Stato:** Disponibile", "**Stato:** Da verificare", 1)
    legacy = legacy.replace("**Stato:** Disponibile", "**Stato:** Verificato", 1)
    document = parse_call_facts_markdown(legacy)
    assert document.pending_count == 1
    assert document.verified_count == 1
    assert len(document.available_facts) == 2
    assert parse_call_facts_markdown(render_call_facts_document(document)) == document
