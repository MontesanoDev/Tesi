"""Sources over the analysis budget stop the session with the reason, never a silent loop.

E2E campaign (29 Oct), real Catanzaro tender: bando and disciplinare gave 200 chunks; every
automatic /resolve answered 422 while the session stayed CREATED with auto_continue on and
no reason the chat could show. Provider outputs simulated; no analysis call is made.
"""

import pytest
import test_compilation_resilient_segments as rev2
from test_compilation_global_sessions import api, provider
from test_compilation_sessions import source

from app import compilation_global

__all__ = ["api", "provider"]


@pytest.mark.anyio
async def test_over_budget_sources_fail_the_session_with_an_explanation(
        api, provider, monkeypatch):
    session = await rev2.started(api, monkeypatch, rev2.form_docx(2), rev2.Model())
    await source(api, "Seconda fonte del progetto.", name="altra.md")
    monkeypatch.setattr(compilation_global, "MAX_SOURCES", 1)
    response = await rev2.analyze(api, session)
    assert response.status_code == 422
    assert "superano il limite dell'analisi" in response.json()["detail"]
    after = (await api.get(f"{rev2.BASE}/{session['id']}")).json()
    assert after["status"] == "FAILED" and "superano il limite" in after["last_error"]
    assert not after["chat"]["auto_continue"]
