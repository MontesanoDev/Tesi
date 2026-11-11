"""No box from the SOURCE alone, but the branch choice is asked and an empty group is never silent.

Real campaign on the new profile: the FORM capacity choice, asked in 24 runs of 24 before the
selective questions, was asked in 0 of 4, with up to 27 documented values suspended on it. On
another FORM a box already marked in the original stayed marked, unconfirmed, and nobody said so.
"""

from io import BytesIO

import pytest
from docx import Document
from docx.oxml.ns import qn
from test_compilation_catalog import encoded, native_checkbox
from test_compilation_global_sessions import api, provider
from test_compilation_incremental_conversation import conversational
from test_docx_checkboxes import states

from app import compilation_branch_evidence as branches
from app import compilation_global_dialogue as dialogue
from app import compilation_global_sessions as adapter
from app.compilation_choices import unconfirmed_initial_boxes
from app.compilation_conversation import (
    MIN_BRANCH_UNLOCKS,
    branch_choice_unlocks,
    selective_pool,
)
from app.compilation_global_dialogue import (
    _blocker_answered,
    checkbox_review,
    checkbox_review_notice,
)
from app.docx_checkboxes import clearable_controls
from app.docx_templates import inspect_docx

__all__ = ["api", "provider"]

KEY = "choice:g"


@pytest.fixture
def anyio_backend():
    return "asyncio"


def question(key=KEY, **extra):
    return {"key": key, "kind": "choice", "choice_group_id": key.removeprefix("choice:"),
            "field_ids": ["a", "b"], "impact": 2, **extra}


def state(*, origin="FORM_capacity_choice", governed=3, held=0, revision=1):
    fields = [{"candidate_id": f"f{i}", "conditions": ["branch"], "proposed_value": "v"}
              for i in range(governed)]
    data = {"audit": {"fields": fields, "choice_groups": {"g": {
                "origin": origin, "options": {"a": {}, "b": {}}, "applicable": {"a": ["branch"]}}}},
            "dialogue": {"held_candidate_ids": [f"h{i}" for i in range(held)],
                         "hold_records": {f"h{i}": {"blocker_key": KEY} for i in range(held)},
                         "answers": {}}}
    if revision:
        data["checkbox_policy_revision"] = revision
    return data


def test_the_branch_choice_is_asked_when_it_settles_many_destinations():
    data = state(governed=MIN_BRANCH_UNLOCKS)
    assert [q["key"] for q in selective_pool(data, [question()])] == [KEY]


def test_a_choice_settling_few_destinations_stays_a_free_instruction():
    data = state(governed=MIN_BRANCH_UNLOCKS - 1)
    assert selective_pool(data, [question()]) == []


def test_proposals_held_on_a_choice_count_even_without_a_form_branch():
    data = state(origin=None, governed=0, held=MIN_BRANCH_UNLOCKS)
    assert branch_choice_unlocks(data, question()) == MIN_BRANCH_UNLOCKS
    assert selective_pool(data, [question()])


def test_a_plain_group_is_not_a_questionnaire():
    data = state(origin=None, governed=10)
    assert selective_pool(data, [question()]) == []


def test_one_question_at_a_time_and_the_one_unlocking_more_first():
    data = state(governed=9)
    other = {"key": "condition:c", "kind": "applicability", "field_ids": ["x"], "impact": 1,
             "documented": 2, "condition": "Clausola"}
    assert [q["key"] for q in selective_pool(data, [other, question()])] == [KEY]
    bigger = {**other, "documented": 40}
    assert [q["key"] for q in selective_pool(data, [question(), bigger])] == ["condition:c"]


def test_the_previous_profile_keeps_its_selective_questions():
    data = state(governed=30, revision=None)
    assert branch_choice_unlocks(data, question()) == 0
    assert selective_pool(data, [question()]) == []


@pytest.mark.parametrize("action", ["SKIP", "UNKNOWN", "REFUSE"])
def test_a_deferred_choice_settles_nothing_but_only_with_the_new_policy(action):
    answers = {KEY: {"action": action}}
    assert not _blocker_answered(KEY, answers, explicit_choice=True)
    assert _blocker_answered(KEY, answers)


def test_an_explicit_choice_settles_it_and_other_keys_are_unchanged():
    assert _blocker_answered(KEY, {KEY: {"action": "VALUE"}}, explicit_choice=True)
    assert not _blocker_answered(KEY, {}, explicit_choice=True)
    answered = {"condition:c": {"action": "SKIP"}}
    assert _blocker_answered("condition:c", answered, explicit_choice=True)


def capacity_data(revision):
    catalog = {"blocks": [], "candidates": {
        "p1.cb0": {"type": "checkbox", "context_id": "paragraph:1", "initial_checked": True},
        "p2.cb0": {"type": "checkbox", "context_id": "paragraph:2", "initial_checked": False}}}
    data = {"catalog": catalog, "audit": {"choice_groups": {}, "fields": []}, "dialogue": {}}
    if revision:
        data["checkbox_policy_revision"] = revision
    return data


def test_unconfirmed_marks_are_found_only_with_the_new_policy():
    assert unconfirmed_initial_boxes(capacity_data(1), {}) == ["p1.cb0"]
    assert unconfirmed_initial_boxes(capacity_data(None), {}) == []


def test_a_mark_the_user_decided_on_is_not_unconfirmed():
    assert unconfirmed_initial_boxes(capacity_data(1), {"p1.cb0": True}) == []
    assert unconfirmed_initial_boxes(capacity_data(1), {"p1.cb0": False}) == []


def form_with_mark(*, locked=False):
    doc = Document()
    doc.add_paragraph("Denominazione: ________")
    p = doc.add_paragraph()
    native_checkbox(p, legacy=False, checked=True)
    p.add_run(" Opzione già segnata")
    if locked:
        sdt = next(p._p.iter(qn("w:sdt")))
        props = sdt.find(qn("w:sdtPr"))
        lock = props.makeelement(qn("w:lock"), {qn("w:val"): "sdtContentLocked"})
        props.insert(0, lock)
    return doc


def test_only_a_protected_control_cannot_be_cleared():
    layout = inspect_docx(encoded(form_with_mark()))
    assert clearable_controls(layout, ["p1.cb0"]) == {"p1.cb0"}
    locked = inspect_docx(encoded(form_with_mark(locked=True)))
    assert clearable_controls(locked, ["p1.cb0"]) == set()


def review_data():
    return {"checkbox_policy_revision": 1,
            "catalog": {"candidates": {"a": {"type": "checkbox", "label": "Opzione A"},
                                       "b": {"type": "checkbox", "label": "Opzione B"},
                                       "s": {"type": "checkbox", "label": "Sola"}}},
            "dialogue": {"answers": {"choice:rinviata": {"action": "SKIP"}}},
            "audit": {"fields": [{"candidate_id": "a", "proposed_value": True}],
                      "choice_groups": {
                          "g": {"validation": "GROUNDED_GROUP", "label": "Tipologia",
                                "options": {"a": {"label": "Opzione A"},
                                            "b": {"label": "Opzione B"}}},
                          "rinviata": {"validation": "GROUNDED_GROUP", "label": "Qualità",
                                       "options": {"c": {"label": "Opzione C"}}},
                          "fatta": {"validation": "GROUNDED_GROUP", "label": "Scelta fatta",
                                    "options": {"d": {"label": "Opzione D"}}},
                          "scartato": {"validation": "REJECTED", "label": "Non valido",
                                       "options": {"e": {"label": "Opzione E"}}}}}}


def test_the_draft_names_the_groups_left_without_a_selection():
    review = checkbox_review(review_data(), {"d": True}, set(), [])
    shown = {g["label"]: g["state"] for g in review["groups_without_selection"]}
    assert shown == {"Tipologia": "non_scelta", "Qualità": "rinviata"}
    notice = checkbox_review_notice(review)
    assert "«Tipologia» (le fonti indicano «Opzione A»)" in notice
    assert "«Qualità» (scelta rinviata)" in notice
    assert "Scelta fatta" not in notice and "Non valido" not in notice
    assert "Nessuna casella viene spuntata senza la tua scelta" in notice


def test_a_group_with_a_false_value_only_is_still_without_selection():
    review = checkbox_review(review_data(), {"d": True, "a": False, "b": False}, set(), [])
    assert "Tipologia" in {g["label"] for g in review["groups_without_selection"]}


def test_the_draft_names_the_marks_of_the_original_and_what_it_did():
    review = checkbox_review(review_data(), {}, {"a", "s"}, ["b"])
    notice = checkbox_review_notice(review)
    assert "era già spuntata «Opzione A»: non è una tua scelta" in notice
    assert "Se vale, dimmelo" in notice
    assert "«Sola»" in notice and "rimettila nel documento" in notice
    assert "è spuntata «Opzione B» e non posso modificarla" in notice


def test_nothing_to_say_says_nothing_and_the_previous_profile_has_no_review():
    data = review_data()
    data["audit"]["choice_groups"] = {}
    assert checkbox_review_notice(checkbox_review(data, {}, set(), [])) == ""
    data.pop("checkbox_policy_revision")
    assert checkbox_review(data, {}, set(), []) is None


async def draft_of(api, s):
    report = (await api.get(s["last_generation"]["downloads"]["report"])).json()
    docx = (await api.get(s["last_generation"]["downloads"]["docx"])).content
    return report, docx


async def export(api, monkeypatch, doc, *, revision=1):
    from app.compilation_chat import ChatControl
    from app.db import connection
    from app.intents import ChatDecision

    s = await conversational(api, monkeypatch, doc=doc)
    with connection() as db:
        row, state_ = adapter._row_state(db, "alpha", s["id"], s["version"])
        if revision:
            state_["global_compilation"]["checkbox_policy_revision"] = revision
        else:
            state_["global_compilation"].pop("checkbox_policy_revision", None)
        from app import compilation_sessions as sessions

        s = sessions.save_state(db, row, state_, "test_policy")
    answer, command = await adapter.handle_chat_action(s, ChatDecision(
        action="compilation_control", answer="", queries=[], target="form",
        control=ChatControl(kind="finish", user_quote="Bozza")), s["version"], "Bozza")
    assert command["action"] == "generated"
    from app import compilation_sessions as sessions

    return answer, sessions.get_session("alpha", s["id"])


@pytest.mark.anyio
async def test_export_clears_an_unconfirmed_mark_and_says_so(api, provider, monkeypatch):
    original = encoded(form_with_mark())
    assert states(original) == {"p1.cb0": True}
    answer, s = await export(api, monkeypatch, Document(BytesIO(original)))
    report, docx = await draft_of(api, s)
    assert list(states(docx).values()) == [False]  # The draft banner shifts the paragraph ids.
    assert report["checkbox_values"] == {"p1.cb0": False}
    assert report["checkbox_effects"] == [{
        "candidate_id": "p1.cb0", "value": False, "provenance": "BACKEND",
        "effect": "unconfirmed_initial_mark_cleared"}]
    assert [m["candidate_id"] for m in report["checkbox_review"]["initial_marks_cleared"]] == [
        "p1.cb0"]
    assert report["written_field_count"] == 0
    assert "era già spuntata" in answer and "rimettila nel documento" in answer


@pytest.mark.anyio
async def test_export_of_a_protected_mark_works_and_says_it_could_not_touch_it(
    api, provider, monkeypatch,
):
    original = encoded(form_with_mark(locked=True))
    answer, s = await export(api, monkeypatch, Document(BytesIO(original)))
    report, docx = await draft_of(api, s)
    assert list(states(docx).values()) == [True]
    assert report["checkbox_values"] == {}
    assert [m["candidate_id"] for m in report["checkbox_review"]["initial_marks_kept"]] == [
        "p1.cb0"]
    assert "non posso modificarla" in answer


@pytest.mark.anyio
async def test_the_previous_profile_leaves_the_mark_as_before(api, provider, monkeypatch):
    original = encoded(form_with_mark())
    answer, s = await export(api, monkeypatch, Document(BytesIO(original)), revision=None)
    report, docx = await draft_of(api, s)
    assert list(states(docx).values()) == [True]
    assert "checkbox_review" not in report and report["checkbox_effects"] == []
    assert "era già spuntata" not in answer


def test_the_gate_on_other_branches_is_untouched_by_a_deferred_choice():
    data = state(governed=3)
    data["conversation_turn_revision"] = 1
    data["dialogue"]["answers"][KEY] = {"action": "SKIP"}
    assert branches.other_capacity_branches(data) == set()


def test_dialogue_module_exposes_the_review_used_by_the_export():
    assert dialogue.checkbox_review is checkbox_review


def branch_session(*, initial_peer=False, revision=1):
    """The real capacity path: accepted condition, FORM region, three values held on the choice."""
    import test_capacity_choice_question as capacity

    data, layout = capacity.capacity_case()
    data.update(conversation_revision=1, conversation_turn_revision=1, phase="REVIEW")
    if revision:
        data["checkbox_policy_revision"] = revision
    if initial_peer:
        data["catalog"]["candidates"]["p5.cb0"]["initial_checked"] = True
    capacity.base.sign(data)
    data = capacity.base.derive(data, layout)
    group = "choice:form_capacity_0"
    dialogue_ = data.setdefault("dialogue", {})
    dialogue_["held_candidate_ids"] = ["x", "y", "z"]
    dialogue_["hold_records"] = {c: {"blocker_key": group, "status": "held"} for c in "xyz"}
    return capacity, data, layout


def asked(data):
    return [q["key"] for q in dialogue.question_pool(data, selective=True)]


def test_the_real_pool_asks_the_branch_choice_only_with_the_new_policy():
    _, data, _ = branch_session()
    assert "choice:form_capacity_0" in asked(data)
    _, old, _ = branch_session(revision=None)
    assert "choice:form_capacity_0" not in asked(old)


@pytest.mark.parametrize("deferred", [False, True])
def test_a_branch_choice_given_or_deferred_is_not_asked_again(deferred):
    capacity, data, layout = branch_session()
    response = (capacity.reply(action="SKIP", quote="Rinvio questa scelta.") if deferred
                else capacity.reply())
    after = capacity.answer(data, layout, response)
    assert "choice:form_capacity_0" not in asked(after)


def test_a_mark_of_the_original_no_longer_hides_the_branch_choice():
    _, data, _ = branch_session(initial_peer=True)
    assert "choice:form_capacity_0" in asked(data)
    _, old, _ = branch_session(initial_peer=True, revision=None)
    assert "choice:form_capacity_0" not in asked(old)
