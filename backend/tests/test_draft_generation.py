import json

import pytest

from app.call_facts import CallFact, CallFactSource
from app.draft_generation import _build_user_prompt, parse_generated_draft, render_draft_markdown
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


@pytest.mark.parametrize("reference", [
    "4c6531d9c3a4",
    "cf-4c6531d9c3a4",
    " CF-4C6531D9C3A4 ",
])
def test_generated_draft_normalizes_references_to_existing_verified_ids(reference):
    fact_id = "cf-4c6531d9c3a4"
    payload = json.dumps({
        "markdown": f"# Candidatura\n\nOggetto [CF:{reference}]. Dettaglio [CF:{reference}].",
        "used_fact_ids": [fact_id],
        "missing_information": [],
    })

    generated = parse_generated_draft(payload, {fact_id})

    assert generated.markdown == (
        "# Candidatura\n\nOggetto [CF:cf-4c6531d9c3a4]. Dettaglio [CF:cf-4c6531d9c3a4]."
    )
    assert generated.used_fact_ids == [fact_id]


@pytest.mark.parametrize("declared_ids", [[], ["cf-deadline"]])
def test_generated_draft_rejects_unknown_short_references(declared_ids):
    payload = json.dumps({
        "markdown": "# Candidatura\n\nDato [CF:non-verificato]",
        "used_fact_ids": declared_ids,
        "missing_information": [],
    })

    with pytest.raises(GenerationError, match="esclusi o inesistenti"):
        parse_generated_draft(payload, {"cf-deadline"})


@pytest.mark.parametrize("markdown, declared_ids", [
    ("Dato [CF:deadline]", []),
    ("Dato senza citazione", ["cf-deadline"]),
    ("Dato [CF:deadline]", ["cf-deadline", "cf-other"]),
])
def test_generated_draft_keeps_rejecting_actual_reference_mismatches(markdown, declared_ids):
    payload = json.dumps({"markdown": markdown, "used_fact_ids": declared_ids})

    with pytest.raises(GenerationError, match="non coincidono"):
        parse_generated_draft(payload, {"cf-deadline", "cf-other"})


def test_draft_prompt_supplies_the_exact_citation_to_copy_for_each_fact():
    prompt = _build_user_prompt("Progetto test", "# Template", [], "# Dati", [verified_fact()])

    assert "FACT ID: cf-deadline" in prompt
    assert "Riferimento da copiare: [CF:cf-deadline]" in prompt
