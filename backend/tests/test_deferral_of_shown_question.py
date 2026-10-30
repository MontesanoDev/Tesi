"""Deferring a question that shows its destinations needs no scope check (30 Oct).

E2E campaign, real Minervino run: «Rinvio questa conferma: lascia vuoti i dati collegati» was
turned into «Il rinvio di questa conferma lascerebbe in bianco più dati collegati…» and asked
again, the same reply refused again: three turns lost. A shown question defers what it shows.
"""

from test_displayed_scope import CONTEXT

from app.compilation_chat import ClarificationReply
from app.compilation_reply_guard import requires_scope_check


def test_a_deferral_of_a_shown_question_needs_no_scope_check():
    skip = ClarificationReply(slot=1, action="SKIP", user_quote="Rinvio")
    assert not requires_scope_check(skip, CONTEXT)
    hidden = {**CONTEXT, "slots": [{**CONTEXT["slots"][0], "destinations_shown": False}]}
    assert requires_scope_check(skip, hidden)
