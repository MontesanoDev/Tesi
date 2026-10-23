"""A grounded contact is not assent to a procedural commitment. No provider."""

import json
from copy import deepcopy
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document
from test_compilation_source_attribution import case

from app import compilation_global_dialogue as dialogue
from app.compilation_global import build_global_input, validate_global_proposal
from app.compilation_global_sessions import initial_state, review_fields
from app.docx_templates import fill_docx, inspect_docx

FIXTURES = Path(__file__).parent / "fixtures"


def prepared(text="PEC aziendale ________; di accettare comunicazioni alla PEC ________"):
    layout, sources, raw = case(text, prop="pec")
    data = initial_state(layout)
    data.update(artifact_path="alpha/_global_compilations/session-a/attempt-a",
                audit=validate_global_proposal(json.dumps(raw), layout, "alpha", sources),
                dialogue={"phase": "READY", "answers": {}, "user_values": {}})
    data["fields"] = review_fields(data)
    data["dialogue"]["reviewed_candidate_ids"] = list(data["writable_ids"])
    return layout, data


def test_actual_trapani_source_pec_survives_but_its_procedural_use_needs_user():
    frozen = json.loads((FIXTURES / "procedural-consent-v1/trapani-real.json").read_text())
    layout = inspect_docx((FIXTURES / "formtext-v1/trapani/original.docx").read_bytes())
    data = initial_state(layout)
    data.update(artifact_path=frozen["artifact_path"], dialogue=frozen["dialogue"],
                audit=validate_global_proposal(json.dumps(frozen["proposal"]), layout,
                                               frozen["project_id"], frozen["sources"]))
    data["catalog"] = build_global_input(layout, frozen["project_id"], frozen["sources"])["form"]
    data["fields"] = review_fields(data)
    ids, _, _ = dialogue.export_selection({"global_compilation": data})
    assert "p75.s8" in ids  # Factual company contact remains grounded and exportable.
    assert "p107.s0" not in ids
    assert len(ids) == 9
    field = next(f for f in data["audit"]["fields"] if f["candidate_id"] == "p107.s0")
    assert field["validation"] == "GROUNDED_PROPOSAL"
    assert field["source_evidence"][0]["chunk_id"] == -44
    assert field["kind"] == "data" and not field["conditions"]


@pytest.mark.parametrize("text", [
    "di accettare che le comunicazioni siano inviate alla PEC ________",
    "Accetto comunicazioni al recapito ________",
    "Il dichiarante autorizza l'invio a ________",
    "Acconsento all'utilizzo della PEC ________",
    "Si impegna a mantenere operativo il recapito ________",
    "Elegge domicilio per le notifiche presso ________",
    "PEC ________ alla quale accetta l'invio delle comunicazioni",
])
def test_explicit_commitment_is_derived_from_actual_form_not_model_label(text):
    _, data = prepared(text)
    assert dialogue.export_selection({"global_compilation": data})[0] == []


@pytest.mark.parametrize("text", [
    "PEC dell'impresa ________", "Recapito per comunicazioni ________",
    "Dichiara che la PEC aziendale è ________",
    "Dato disponibile dopo accettazione dell'istanza: PEC ________",
    "Email dell'ufficio autorizzazioni ________",
])
def test_factual_contacts_are_not_blocked_by_a_blanket_declaration_rule(text):
    _, data = prepared(text)
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]


def authorization(data):
    return next(q for q in dialogue.question_pool(data) if q["key"].startswith("authorization:"))


def consent(data, *, action="CONDITION_TRUE", quote="Sì, autorizzo questa dichiarazione"):
    slot = authorization(data)
    data["dialogue"]["answers"][slot["key"]] = {
        "action": action, "provenance": "USER", "applies": action == "CONDITION_TRUE",
        "user_quote": quote, "question": slot["question"],
        "authorization": slot["authorization"],
    }
    return slot


def test_positive_assent_is_separate_from_the_source_value_and_from_export():
    layout, data = prepared()
    slot = authorization(data)
    assert slot["field_ids"] == ["p0.s1"]
    assert "ufficio@alba.demo" in slot["question"] and "accettare" in slot["question"]
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]
    consent(data)
    assert set(dialogue.export_selection({"global_compilation": data})[0]) == {"p0.s0", "p0.s1"}
    assert not data["dialogue"]["user_values"]  # No SOURCE contact becomes a USER fact.
    assert not [q for q in dialogue.question_pool(data) if q["key"].startswith("authorization:")]
    out = fill_docx(layout, {"p0.s1": "ufficio@alba.demo"})
    assert "accettare comunicazioni alla PEC ufficio@alba.demo" in "\n".join(
        p.text for p in Document(BytesIO(out)).paragraphs)


@pytest.mark.parametrize("action", ["UNKNOWN", "SKIP", "REFUSE", "CONDITION_FALSE", "VALUE"])
def test_non_assent_does_not_authorize_writing(action):
    _, data = prepared()
    consent(data, action=action)
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]


@pytest.mark.parametrize("change", ["value", "template", "session", "question", "source",
                                    "uncertain", "fields", "scope"])
def test_receipt_cannot_be_reused_for_another_value_scope_or_unverified_assent(change):
    _, data = prepared()
    slot = consent(data)
    record = data["dialogue"]["answers"][slot["key"]]
    if change == "value":
        data["dialogue"]["user_values"]["p0.s1"] = {"value": "altro@alba.demo",
            "user_quote": "altro@alba.demo", "provenance": "USER"}
    elif change == "template":
        data["catalog"]["template_sha256"] = "different"
    elif change == "session":
        data["artifact_path"] = "alpha/_global_compilations/other/attempt"
    elif change == "question":
        record["question"] = "Confermi l'export?"
    elif change == "source":
        record["provenance"] = "SOURCE"
    elif change == "uncertain":
        record["user_quote"] = "Forse sì, non so"
    elif change == "fields":
        record["authorization"]["field_ids"] = ["p0.s0"]
    else:
        record["authorization"]["form_evidence"]["quote"] = "Altra dichiarazione"
    ids, _, users = dialogue.export_selection({"global_compilation": data})
    assert "p0.s1" not in ids + users


def test_unrelated_condition_or_export_confirmation_is_not_procedural_assent():
    _, data = prepared()
    data["dialogue"]["answers"] = {"condition:c": {"action": "CONDITION_TRUE",
        "provenance": "USER", "applies": True, "question": "Confermi l'export?",
        "user_quote": "Sì"}}
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]


def test_canonical_question_keeps_full_commitment_even_if_narrator_truncates_it():
    _, data = prepared()
    slot = authorization(data)
    plan = dialogue.DialoguePlan(message="I dati disponibili restano da verificare.",
        questions=[dialogue.DialogueQuestion(slot=slot["slot"], confirmation="la PEC è corretta")])
    result = dialogue.render_dialogue(plan, dialogue.question_pool(data), require_confirmation=True)
    assert result["question"]["slots"][0]["question"] == slot["question"]
    assert "accettare" in result["message"]


def test_authorization_does_not_override_a_legitimate_hold_or_unknown_branch():
    _, data = prepared()
    consent(data)
    data["dialogue"]["held_candidate_ids"] = ["p0.s1"]
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]
    data["dialogue"]["held_candidate_ids"] = []
    next(f for f in data["fields"] if f["candidate_id"] == "p0.s1")["conditions"] = ["c"]
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]


def test_only_fields_in_commitment_clause_are_affected():
    _, data = prepared("Accetto comunicazioni alla PEC ________; PEC societaria ________")
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s1"]
    assert authorization(data)["field_ids"] == ["p0.s0"]


def test_source_fact_and_model_audit_are_never_rewritten_by_consent():
    _, data = prepared()
    original = deepcopy(data["audit"])
    consent(data)
    dialogue.export_selection({"global_compilation": data})
    assert data["audit"] == original


@pytest.mark.parametrize("quote", ["Genera la bozza", "La PEC è corretta", "Non autorizzo",
    "Non lo so", "Sì, ma non confermo la dichiarazione", "Confermo la società di ingegneria"])
def test_model_cannot_turn_an_unrelated_or_negative_quote_into_assent(quote):
    _, data = prepared()
    consent(data, quote=quote)
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s0"]


def test_mandatory_consent_question_is_shown_even_when_narrator_asks_nothing():
    _, data = prepared()
    plan = dialogue.DialoguePlan(message="Ho conservato i dati documentati.", questions=[])
    result = dialogue.render_dialogue(plan, dialogue.question_pool(data), require_confirmation=True)
    assert result["question"]["slots"][0]["question"] == authorization(data)["question"]


def test_commitment_does_not_spread_to_next_paragraph_or_next_sentence():
    _, data = prepared("Accetto comunicazioni alla PEC ________. PEC aziendale ________")
    assert dialogue.export_selection({"global_compilation": data})[0] == ["p0.s1"]


def test_chat_public_view_retains_the_gate_without_exposing_the_full_audit():
    _, data = prepared()
    public = {k: v for k, v in data.items() if k != "audit"}
    assert dialogue.export_selection({"global_compilation": public})[0] == ["p0.s0"]
    consent(data)
    public["fields"] = review_fields(data)
    assert dialogue.export_selection({"global_compilation": public})[0] == ["p0.s0", "p0.s1"]
