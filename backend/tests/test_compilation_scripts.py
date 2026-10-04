import asyncio
import json

import pytest

from app import document_compilation as compilation
from app.docx_templates import inspect_docx
from scripts.create_paragraph_template import create_template
from scripts.replay_docx_audit import replay


@pytest.mark.parametrize("legacy_layout", [False, True])
@pytest.mark.parametrize("prompt_name", ["request-01.prompt.json", "batch-01.prompt.json"])
def test_replay_preserves_request_options_and_accepts_current_and_legacy_audits(
    tmp_path, monkeypatch, legacy_layout, prompt_name,
):
    audit = tmp_path / "audit"
    template_path = audit / "output/template.docx" if legacy_layout else audit / "template.docx"
    create_template(template_path)
    layout = inspect_docx(template_path.read_bytes())
    sources = compilation.CompilationSources([{
        "id": "company:1", "document_id": 1, "source_name": "societa.txt",
        "chunk_index": 0, "content": "Societa: Impresa", "scope": "company",
    }], 1, len("Societa: Impresa"))
    frozen = compilation.build_prompt(layout, sources, "Prova ripetibile", "")
    (audit / prompt_name).write_text(frozen, encoding="utf-8")
    calls = []

    async def model(prompt, **options):
        calls.append(options)
        payload = json.loads(prompt)
        return json.dumps({"fields": [{
            "cell_id": payload["target_ids"][0], "label": "Dato da verificare",
            "entity": "person", "kind": "data", "status": "missing", "value": None,
            "evidence": [], "reason": "Informazione assente",
        }], "warnings": []}), "test", 20

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    output = tmp_path / "replayed"
    asyncio.run(replay(audit, output))
    assert calls == [{
        "max_tokens": compilation.SINGLE_CALL_MAX_OUTPUT_TOKENS,
        "timeout_seconds": compilation.SINGLE_CALL_TIMEOUT_SECONDS,
    }]
    assert (output / "output/template.docx").read_bytes() == template_path.read_bytes()
    report = json.loads((output / "output/report.json").read_text())
    assert report["template_sha256"] == layout.sha256
    assert report["source_coverage"] == sources.coverage()
    assert report["execution"]["requests"] == 1
    assert (output / "request-01.prompt.json").is_file()
    assert not list(output.glob("batch-*"))
    assert json.loads((output / "result.json").read_text())["success"]
