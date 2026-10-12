"""Frozen command scenarios; no model responses or live data."""

from scripts.benchmark_compilation_dialogue import FIXTURE, load_fixture


def test_command_fixture_is_separate_and_frozen_with_real_slot_references():
    manifest, contexts, cases = load_fixture(FIXTURE.parent / "commands-v1")
    assert manifest["gold_in_prompt"] is False and len(cases) == 28
    assert len(load_fixture(FIXTURE)[2]) == 43
    assert all(c["expected"]["values"].keys() <= c["expected"]["actions"].keys()
               for c in cases)
    assert all(c["context"] in contexts for c in cases)


def test_session_commands_never_update_fields_in_command_gold():
    for case in load_fixture(FIXTURE.parent / "commands-v1")[2]:
        expected = case["expected"]
        if set(expected["intents"]) <= {"pause", "resume", "finish", "generate"}:
            assert not expected["actions"] and not expected["values"]
