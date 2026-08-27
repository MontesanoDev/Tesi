import json

import pytest

from app.call_facts import CallFact, CallFactSource
from app.draft_generation import parse_generated_draft, render_draft_markdown
from app.generation import GenerationError


def verified_fact() -> CallFact:
    return CallFact(
        id="cf-deadline",
        title="Termine di candidatura",
        value="15 settembre 2025",
        status="verified",
        sources=[CallFactSource(name="avviso.pdf", fragment=18)],
    )


def test_generated_draft_is_validated_and_rendered_with_provenance():
    fact = verified_fact()
    payload = json.dumps(
        {
            "markdown": "# Candidatura\n\nScadenza: 15 settembre 2025 [CF:cf-deadline]",
            "used_fact_ids": ["cf-deadline"],
            "missing_information": ["Importo richiesto"],
        }
    )

    generated = parse_generated_draft(payload, {fact.id})
    generated = generated.__class__(
        markdown=generated.markdown,
        used_fact_ids=generated.used_fact_ids,
        missing_information=generated.missing_information,
        model="deepseek-test",
        total_tokens=81,
    )
    company_sources = [
        {
            "source_name": "profilo-mapi.md",
            "chunk_index": 0,
            "content": "Mapi Ingegneria supporta enti committenti.",
        }
    ]
    markdown = render_draft_markdown(
        "progetto-demo",
        generated,
        [fact],
        company_sources,
    )

    assert "status: pending_review" in markdown
    assert "[TODO" not in markdown
    assert "- Importo richiesto" in markdown
    assert "[CF:cf-deadline] Termine di candidatura - avviso.pdf, frammento 18" in markdown
    assert "[COMPANY] Fonti Company KB collegate: profilo-mapi.md." in markdown


@pytest.mark.parametrize(
    "used_ids, reference",
    [
        (["cf-unknown"], "cf-unknown"),
        (["cf-deadline"], "cf-other"),
        ([], "cf-deadline"),
    ],
)
def test_generated_draft_rejects_unverified_or_inconsistent_references(used_ids, reference):
    payload = json.dumps(
        {
            "markdown": f"# Candidatura\n\nDato [CF:{reference}]",
            "used_fact_ids": used_ids,
            "missing_information": [],
        }
    )

    with pytest.raises(GenerationError):
        parse_generated_draft(payload, {"cf-deadline"})
