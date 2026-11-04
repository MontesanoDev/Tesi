"""Creation profile of NEW global compilation sessions, defined in one place.

«Compilazione DOCX» has a single ordinary path: generation by FORM segments (rev 3), every
segment reading the complete FORM and owning only its destinations, with all verified controls.
The revisions below are persisted in each new session for audit; an existing session keeps the
flags it was created with and is never upgraded at runtime.

MAPI_COMPILATION_PROFILE=storico is a server-side emergency rollback and reproduction switch,
not a user option: new sessions then follow the previous creation rules, driven by the former
MAPI_*_REVISION variables (monolithic generation when they are absent). Without it, those
experiment variables are ignored, so a stale environment cannot alter the ordinary profile.
MAPI_COMPILATION_PROFILE=sezioni-2026-10-24 recreates the canonical profile in force before the
FORM option/instruction scope was adopted (25 October 2026), also only as an emergency switch;
sezioni-2026-10-25 the one before the structural stabilization of 30 October 2026, and
sezioni-2026-10-30 the one before the omission and SOURCE-hold revisions of the same day.
"""

from __future__ import annotations

import os

PROFILE_NAME = "sezioni-2026-11-05"
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
    "form_option_scope_revision": 2,      # Data bound to their FORM option or instruction.
    "text_checkbox_revision": 1,          # Supported ASCII markers; verified USER choice.
    "segment_recovery_revision": 1,       # One targeted retry of validator-rejected proposals.
    "form_clause_revision": 1,            # Conditions anchored on identifiable FORM clauses.
    "hold_resolution_revision": 1,        # Every hold has a cause and a USER resolution.
    "format_retry_revision": 1,           # Invalid JSON: bounded retries saying where.
    "hold_review_revision": 1,            # Deterministic review of narrator SOURCE doubts.
    "omission_recovery_revision": 1,      # Declared-unassessed destinations: one recovery.
    "user_extraction_revision": 1,        # Atomic USER facts, individually scope-checked.
    "conversation_revision": 1,          # Selective questions and explicit free instructions.
    "subject_check_revision": 1,          # Evidence, destination and USER reply owners verified.
    "identifier_type_revision": 1,        # REA, Register, VAT and tax codes are not alternatives.
    "role_proof_revision": 1,             # The role stated by the value's own personal record.
}
# Earlier canonical profiles, recreated only by the server-side emergency switch.
NEW_2026_10_30 = {"segment_recovery_revision", "form_clause_revision",
                  "hold_resolution_revision"}
NEW_2026_10_30_R2 = {"format_retry_revision", "hold_review_revision",
                     "omission_recovery_revision"}
NEW_USER_EXTRACTION = {"user_extraction_revision", "conversation_revision"}
NEW_2026_11_05 = {"subject_check_revision", "identifier_type_revision", "role_proof_revision"}
PREVIOUS = {
    "sezioni-2026-10-24": {k: v for k, v in SECTIONS.items() if k not in {
        "form_option_scope_revision", "text_checkbox_revision", *NEW_2026_10_30,
        *NEW_2026_10_30_R2, *NEW_USER_EXTRACTION, *NEW_2026_11_05}},
    "sezioni-2026-10-25": {k: v for k, v in SECTIONS.items()
                           if k not in NEW_2026_10_30 | NEW_2026_10_30_R2 | NEW_USER_EXTRACTION
                           | NEW_2026_11_05},
    "sezioni-2026-10-30": {k: v for k, v in SECTIONS.items()
                           if k not in NEW_2026_10_30_R2 | NEW_USER_EXTRACTION | NEW_2026_11_05},
    "sezioni-2026-10-30-r2": {k: v for k, v in SECTIONS.items() if k not in NEW_2026_11_05}}


def new_session_flags():
    profile = os.environ.get("MAPI_COMPILATION_PROFILE")
    if profile == "checkbox-testuali-2026-10-26":
        return {**{k: v for k, v in SECTIONS.items() if k not in NEW_USER_EXTRACTION},
                "compilation_profile": profile, "text_checkbox_revision": 1}
    if profile == "storico":
        return historical_flags()
    if profile in PREVIOUS:
        return {**PREVIOUS[profile], "compilation_profile": profile}
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
