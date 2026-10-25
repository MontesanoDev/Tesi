"""Creation profile of NEW global compilation sessions, defined in one place.

«Compilazione DOCX» has a single ordinary path: generation by FORM segments (rev 3), every
segment reading the complete FORM and owning only its destinations, with all verified controls.
The revisions below are persisted in each new session for audit; an existing session keeps the
flags it was created with and is never upgraded at runtime.

MAPI_COMPILATION_PROFILE=storico is a server-side emergency rollback and reproduction switch,
not a user option: new sessions then follow the previous creation rules, driven by the former
MAPI_*_REVISION variables (monolithic generation when they are absent). Without it, those
experiment variables are ignored, so a stale environment cannot alter the ordinary profile.
"""

from __future__ import annotations

import os

PROFILE_NAME = "sezioni-2026-10-24"
SECTIONS = {
    "backend_revision": 13,
    "option_authorization_revision": 1,   # V14: assent to printed option clauses.
    "attribution_safety_revision": 1,     # K3: subject, role and organization attribution.
    "derivation_revision": 1,             # Coherent derived state after USER replies.
    "dialogue_revision": 1,               # P3 dialogue and semantic reply guard.
    "generation_revision": 3,             # Segments with the complete FORM, scope checks.
    "narration_recovery_revision": 1,     # One bounded retry, then a degraded summary.
    "branch_scope_revision": 1,           # R1: option conditions cover their continuation.
    "table_scope_revision": 1,            # Conditional table sections need applicability.
    "hold_rereview_revision": 2,          # One re-review of misattributed or role holds.
}


def new_session_flags():
    if os.environ.get("MAPI_COMPILATION_PROFILE") == "storico":
        return historical_flags()
    # Isolated offline candidate; no implicit upgrade of previously stored sessions.
    if os.environ.get("MAPI_FORM_OPTION_SCOPE_REVISION") == "1":
        return {**SECTIONS, "form_option_scope_revision": 1,
                "compilation_profile": "sezioni-opzioni-2026-10-25"}
    return {**SECTIONS, "compilation_profile": PROFILE_NAME}


def historical_flags():
    """The creation rules in force before 24 October 2026, unchanged."""
    flags = {"backend_revision": 13, "option_authorization_revision": 1,
             "attribution_safety_revision": 1}
    flags.update({revision: 1 for revision, variable in (
        ("dialogue_revision", "MAPI_DIALOGUE_REVISION"),
        ("narration_recovery_revision", "MAPI_NARRATION_RECOVERY_REVISION"),
        ("generation_revision", "MAPI_GENERATION_REVISION")) if os.environ.get(variable) == "1"})
    # Explicit 0 preserves the profile before the derived-state fix, for comparisons.
    if os.environ.get("MAPI_DERIVATION_REVISION", "1") == "1":
        flags["derivation_revision"] = 1
    if os.environ.get("MAPI_GENERATION_REVISION") in {"2", "3"}:
        flags["generation_revision"] = int(os.environ["MAPI_GENERATION_REVISION"])
    if flags.get("generation_revision") == 3:
        if os.environ.get("MAPI_BRANCH_SCOPE_REVISION") == "1":
            flags["branch_scope_revision"] = 1
        if os.environ.get("MAPI_HOLD_REREVIEW_REVISION") in {"1", "2"}:
            flags["hold_rereview_revision"] = int(os.environ["MAPI_HOLD_REREVIEW_REVISION"])
        if os.environ.get("MAPI_TABLE_SCOPE_REVISION") == "1":
            flags["table_scope_revision"] = 1
    return flags
