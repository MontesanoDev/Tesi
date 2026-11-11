"""Shared test configuration.

The existing tests exercise explicit creation profiles through the former MAPI_*_REVISION
variables (monolithic by default), so they run with the server-side historical switch. The
ordinary default, the canonical «Compilazione DOCX» profile, is covered explicitly by
test_compilation_profile.py and by the resumption tests, which remove this switch.
"""

import pytest


@pytest.fixture(autouse=True)
def historical_creation_profile(monkeypatch):
    monkeypatch.setenv("MAPI_COMPILATION_PROFILE", "storico")
