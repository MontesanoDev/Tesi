"""A role binding with one attesting SOURCE citation is not poisoned by a supporting one.

Attempt 03: the technical director binding cited the heading «Ing. Elisa Romano - direttore
tecnico» and, as a second citation, the person's row of the partners table (no role there).
Every citation had to contain the role, so the whole binding was rejected and the director's
destinations and condition left the question pool. A citation without the role now proves
nothing (recorded as not attesting); at least one attesting citation is still required, and
fabricated quotes, General KB and the FORM-side role check reject as before.
"""

import pytest

from app.compilation_global import _subject_bindings

HEADING = "### Ing. Elisa Romano - direttore tecnico"
ROW = "| Elisa Romano | 40% | Ingegnere | Ordine degli Ingegneri di Bari | A | 18/05/2015 |"
FORM = ("la quale ha come Responsabile della Progettazione (per le società di professionisti) "
        "o Direttore Tecnico (per le società di ingegneria):")


def source(chunk_id, content, category="company"):
    return {"chunk_id": chunk_id, "file_id": -chunk_id, "chunk_index": 0,
            "source_name": f"fonte-{-chunk_id}.md", "role": "source", "scope": "global",
            "category": category, "project_id": None, "content": content}


SOURCES = {-45: source(-45, "Organigramma\n" + HEADING + "\nResponsabile tecnico."),
           -54: source(-54, "## Soci\n" + ROW + "\n"),
           -9: source(-9, "### Ing. Elisa Romano - direttore tecnico", "general")}


def binding(*evidence, required="Direttore Tecnico", source_role="direttore tecnico",
            form=FORM, structural=False):
    record = {"form": {"paragraph_id": "paragraph:50", "quote": form},
              "required_role": required, "source_role": source_role,
              "evidence": [{"chunk_id": c, "quote": q} for c, q in evidence]}
    return _subject_bindings({"dt": record}, {"paragraph:50": FORM}, SOURCES,
                             structural=structural)["dt"]


@pytest.mark.parametrize("structural", [False, True])  # The V12 pipeline uses structural.
def test_supporting_row_no_longer_rejects_an_attested_role(structural):
    result = binding((-45, HEADING), (-54, ROW), structural=structural)
    assert result["validation"] == "GROUNDED_PROPOSAL", result["validation_errors"]
    assert [p["quote"] for p in result["source_evidence"]] == [HEADING]
    assert result["non_attesting_citations"] == [{"chunk_id": -54, "quote": ROW}]


@pytest.mark.parametrize("evidence,kwargs", [
    (((-54, ROW),), {}),  # No citation attests the role.
    (((-45, HEADING), (-54, ROW)), {"source_role": "responsabile qualità"}),
    (((-45, HEADING), (-54, "| Elisa Romano | 50% | inventata |")), {}),  # Fabricated quote.
    (((-45, HEADING), (-9, HEADING)), {}),  # General KB never attests a personal role.
    (((-45, HEADING), (-54, ROW)), {"required": "Legale rappresentante"}),  # Not in FORM.
])
@pytest.mark.parametrize("structural", [False, True])
def test_unsupported_bindings_stay_rejected(evidence, kwargs, structural):
    assert binding(*evidence, **kwargs, structural=structural)["validation"] == "REJECTED"


def test_single_attesting_citation_unchanged():
    result = binding((-45, HEADING))
    assert result["validation"] == "GROUNDED_PROPOSAL"
    assert "non_attesting_citations" not in result
