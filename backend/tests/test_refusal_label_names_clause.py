"""A refused confirmation names the FORM clause, not the model's note (E2E, 29 Oct).

Real Minervino run: «Non ho usato la risposta su «La qualità di legale rappresentante della
società non è confermata; …»»: the refused item was the model's note on the condition.
"""

from app.compilation_global_dialogue import refusal_label


def test_a_refused_confirmation_names_the_form_clause_not_the_model_note():
    slot = {"kind": "applicability", "label": "La qualità di legale rappresentante non è "
            "confermata; i dati restano condizionati.",
            "condition": "☐ Legale rappresentante di società di ingegneria avente la seguente"}
    assert refusal_label(slot) == "Legale rappresentante di società di ingegneria"
    assert refusal_label({"kind": "value", "label": "Sottoscritto"}) == "Sottoscritto"
