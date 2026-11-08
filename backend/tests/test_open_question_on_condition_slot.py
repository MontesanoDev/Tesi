"""An open question on a condition slot is replaced by the backend's closed confirmation.

E2E campaign, real Minervino run (30 Oct): the narrator wrote «In quale qualità partecipa il
sottoscrittore…?» for the applicability slot «IN QUALITÀ DI»; render_dialogue rejected the
whole narration twice («La domanda di applicabilità richiede una proposizione chiusa»), the
dialogue fell back to degraded mode and the draft was empty. Synthetic FORM.
"""

import pytest
from test_documented_conditions_not_skipped import CLAUSE, case

from app.compilation_global_dialogue import DialoguePlan, question_pool, render_dialogue


def test_the_backend_confirmation_replaces_an_open_question():
    pool = question_pool(case())
    [condition] = [q for q in pool if q["kind"] == "applicability"]
    plan = DialoguePlan(message="Riepilogo dei punti aperti.", questions=[
        {"slot": condition["slot"], "question": "In quale qualità partecipa il sottoscrittore?"}])
    [slot] = render_dialogue(plan, pool, require_confirmation=True)["question"]["slots"]
    assert slot["question"].startswith(
        f"Confermi che si applica al vostro caso quanto indicato nel modulo: «{CLAUSE}»")


def test_without_a_safe_backend_text_the_narration_is_still_rejected():
    pool = question_pool(case())
    for q in pool:
        if q["kind"] == "applicability":
            q["condition"] = "[["  # No readable FORM clause to confirm.
    [condition] = [q for q in pool if q["kind"] == "applicability"]
    plan = DialoguePlan(message="Riepilogo dei punti aperti.", questions=[
        {"slot": condition["slot"], "question": "In quale qualità partecipa?"}])
    with pytest.raises(ValueError, match="proposizione chiusa"):
        render_dialogue(plan, pool, require_confirmation=True)
