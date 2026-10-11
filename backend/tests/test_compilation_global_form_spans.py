"""FORM typography may differ; SOURCE values and physical anchors stay strict."""

import pytest

from app.compilation_global import _form_quote
from app.compilation_sources import source_span


@pytest.mark.parametrize("text,quote,restored", [
    ("Società tecnica ____", "Societa' tecnica", "Società tecnica"),
    ("CITTA' DI RESIDENZA ____", "città di residenza", "CITTA' DI RESIDENZA"),
    ("Telefono ______ Fax________", "Telefono ______ Fax", "Telefono ______ Fax"),
    ("____Identificativo____", "Identificativo", "Identificativo"),
    ("Località\n  operativa: ____", "LOCALITA' operativa:", "Località\n  operativa:"),
    ("Denominazione dell’ente: ____", "Denominazione dell'ente", "Denominazione dell’ente"),
    ("Unità\u00a0territoriale: ____", "unita territoriale", "Unità\u00a0territoriale"),
])
def test_form_typography_restores_original_contiguous_text(text, quote, restored):
    assert _form_quote(text, quote) == restored


@pytest.mark.parametrize("text,quote", [
    ("Registro ISO 12345 ____", "Registro ISO 1234"),
    ("Codice X9876 ____", "9876"),
    ("Numero aziendale ____", "Numero personale"),
    ("Codice A-12 ____", "Codice A12"),
    ("sede legale ____", "sede operativa"),
    ("Numero ____", "Numero __"),
    ("Denominazione dell'ente", "Denominazione dellente"),
    ("ABC", ""),
])
def test_form_matching_does_not_allow_fuzzy_or_partial_words_numbers(text, quote):
    with pytest.raises(ValueError):
        _form_quote(text, quote)


@pytest.mark.parametrize("text,quote", [
    ("Società tecnica", "Societa' tecnica"),
    ("Telefono ______ Fax________", "Telefono ______ Fax"),
    ("____Identificativo____", "Identificativo"),
    ("Registro ISO 12345", "Registro ISO 1234"),
])
def test_form_normalization_does_not_weaken_source_span_matching(text, quote):
    with pytest.raises(ValueError):
        source_span(text, quote)
