import asyncio
import hashlib
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import httpx
import pytest
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app import document_compilation as compilation
from app import document_compilation_routes as routes
from app.artifacts import seed_markdown_artifacts
from app.db import connection, get_storage_path, init_database
from app.docx_templates import (
    DRAFT_NOTICE,
    DocumentInputError,
    DocxTooLargeError,
    fill_docx,
    inspect_docx,
    text_of,
)
from app.generation import GenerationError
from app.main import app
from app.seed import seed_database

CASE = Path(__file__).resolve().parents[2] / "demo-documents/bandi/catanzaro-dl-cse"


def template_bytes(labels=("Ragione sociale", "Codice fiscale", "Firma")):
    document = Document()
    document.add_paragraph("Domanda di partecipazione")
    document.sections[0].header.paragraphs[0].text = "Intestazione originale"
    table = document.add_table(rows=len(labels), cols=2)
    for index, label in enumerate(labels):
        table.cell(index, 0).text = label
    target = BytesIO()
    document.save(target)
    return target.getvalue()


def replace_part(data, name, content):
    target = BytesIO()
    with ZipFile(BytesIO(data)) as source, ZipFile(target, "w", ZIP_DEFLATED) as result:
        for entry in source.infolist():
            result.writestr(entry, content if entry.filename == name else source.read(entry))
    return target.getvalue()


def sources(text="Denominazione: Mapi Ingegneria S.r.l."):
    return compilation.CompilationSources(
        [
            {
                "id": "company:1",
                "document_id": 1,
                "source_name": "azienda.txt",
                "chunk_index": 0,
                "content": text,
                "scope": "company",
                "source_kind": "source",
            }
        ],
        1,
        len(text),
    )


def proposal(**overrides):
    return {
        "cell_id": "t0.r0.c1",
        "label": "Ragione sociale",
        "entity": "company",
        "kind": "data",
        "status": "proposed",
        "value": "Mapi Ingegneria S.r.l.",
        "evidence": [{"source_id": "company:1", "quote": "Denominazione: Mapi Ingegneria S.r.l."}],
        "reason": "Fonte aziendale",
        **overrides,
    }


def result(*fields):
    return json.dumps({"fields": list(fields), "warnings": []})


def test_writer_changes_only_authorized_cells_and_main_part():
    original = template_bytes()
    layout = inspect_docx(original)
    output = fill_docx(layout, {"t0.r0.c1": "Societa D'Amico & Figli <S.r.l.>\nBari"})
    doc = Document(BytesIO(output))
    assert doc.tables[0].cell(0, 1).text == "Societa D'Amico & Figli <S.r.l.>\nBari"
    assert doc.tables[0].cell(1, 1).text == ""
    assert doc.tables[0].cell(2, 1).text == ""
    assert doc.tables[0].cell(0, 0).text == "Ragione sociale"
    assert doc.paragraphs[0].text == DRAFT_NOTICE
    assert original == layout.original
    with ZipFile(BytesIO(original)) as before, ZipFile(BytesIO(output)) as after:
        assert before.namelist() == after.namelist()
        for name in before.namelist():
            if name != "word/document.xml":
                assert before.read(name) == after.read(name)
    with pytest.raises(DocumentInputError, match="non autorizzato"):
        fill_docx(layout, {"t0.r0.c0": "Sovrascrittura etichetta"})
    with pytest.raises(DocumentInputError, match="bozza gia generata"):
        inspect_docx(output)


def test_catanzaro_real_cells_and_package_are_preserved():
    data = (CASE / "modello/domanda-partecipazione.docx").read_bytes()
    mapping = json.loads((CASE / "mappa-campi.json").read_text())
    layout = inspect_docx(data)
    assert len(layout.catalog) == 50
    values = {}
    for field in mapping["fields"]:
        target = field["target"]
        cell_id = f"t{target['table']}.r{target['row']}.c{target['column']}"
        assert cell_id in layout.candidate_ids
        if field["state"] == "proposed_demo":
            values[cell_id] = field["suggested_value"]
    output = fill_docx(layout, values)
    with ZipFile(BytesIO(data)) as before, ZipFile(BytesIO(output)) as after:
        for name in before.namelist():
            if name != "word/document.xml":
                assert before.read(name) == after.read(name)
    doc = Document(BytesIO(output))
    assert len(list(doc.element.body.iter(qn("w:tbl")))) == 50
    assert len(list(doc.element.body.iter(qn("w:checkBox")))) == 28
    # Tests use the fixture, but the production discovery/prompt never imports it.
    assert "Mapi Ingegneria S.r.l." in text_of(doc.element)
    assert "Elisa Romano" in text_of(doc.element)


def test_controls_and_vertical_merge_continuations_are_not_writable():
    document = Document(BytesIO(template_bytes()))
    cell = document.tables[0].cell(0, 1)
    field = OxmlElement("w:fldChar")
    field.set(qn("w:fldCharType"), "begin")
    cell.paragraphs[0].add_run()._r.append(field)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    cell.paragraphs[0].add_run()._r.append(end)
    document.tables[0].cell(1, 1).merge(document.tables[0].cell(2, 1))
    output = BytesIO()
    document.save(output)
    layout = inspect_docx(output.getvalue())
    assert "t0.r0.c1" not in layout.candidate_ids
    assert "t0.r1.c1" in layout.candidate_ids
    assert "t0.r2.c1" not in layout.candidate_ids


@pytest.mark.parametrize("data", [b"", b"%PDF-1.4", b"not a docx"])
def test_invalid_docx_is_rejected(data):
    with pytest.raises(DocumentInputError):
        inspect_docx(data)


def test_active_content_external_resources_and_dtd_are_rejected():
    data = template_bytes()
    target = BytesIO()
    with ZipFile(BytesIO(data)) as original, ZipFile(target, "w") as archive:
        for entry in original.infolist():
            archive.writestr(entry, original.read(entry))
        archive.writestr("word/vbaProject.bin", b"macro")
    with pytest.raises(DocumentInputError, match="macro"):
        inspect_docx(target.getvalue())
    malicious = b'<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><x>&a;</x>'
    with pytest.raises(DocumentInputError, match="DTD"):
        inspect_docx(replace_part(data, "word/document.xml", malicious))
    relationships = (
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="r1" Type="attachedTemplate" '
        b'TargetMode="External" Target="http://example.invalid/remote.dotm"/></Relationships>'
    )
    with pytest.raises(DocumentInputError, match="esterne"):
        inspect_docx(replace_part(data, "word/_rels/document.xml.rels", relationships))


def test_archive_limits_and_no_empty_fields(monkeypatch):
    from app import docx_templates

    data = template_bytes()
    monkeypatch.setattr(docx_templates, "MAX_UNPACKED_BYTES", 100)
    with pytest.raises(DocxTooLargeError):
        inspect_docx(data)
    monkeypatch.undo()
    document = Document()
    document.add_paragraph("Modello soltanto narrativo")
    output = BytesIO()
    document.save(output)
    with pytest.raises(DocumentInputError, match="Nessun campo"):
        inspect_docx(output.getvalue())


def test_proposals_have_checked_sources_and_missing_fields_remain_empty():
    layout = inspect_docx(template_bytes())
    missing = proposal(
        cell_id="t0.r1.c1",
        label="Codice fiscale",
        status="missing",
        value=None,
        evidence=[],
        reason="Non presente",
    )
    parsed = compilation.validate_proposals(result(proposal(), missing), layout, sources())
    assert parsed["fields"][0]["written_value"] == "Mapi Ingegneria S.r.l."
    assert parsed["fields"][0]["evidence"][0]["fragment"] == 1
    assert parsed["fields"][0]["evidence"][0]["page"] is None
    assert parsed["fields"][1]["written_value"] is None
    assert parsed["unclassified_cells"] == ["t0.r2.c1"]


@pytest.mark.parametrize(
    "field",
    [
        proposal(cell_id="t0.r0.c0"),
        proposal(cell_id="t999.r0.c1"),
        proposal(status="missing"),
        proposal(value={"text": "Mapi"}),
        proposal(kind="unsupported"),
    ],
)
def test_invalid_proposals_fail_closed(field):
    with pytest.raises(GenerationError):
        compilation.validate_proposals(result(field), inspect_docx(template_bytes()), sources())


@pytest.mark.parametrize("payload", ["[]", "null", "{}", "not json", '{"fields":"oops"}'])
def test_invalid_model_json_is_rejected(payload):
    with pytest.raises(GenerationError):
        compilation.validate_proposals(payload, inspect_docx(template_bytes()), sources())


def test_duplicate_cells_are_rejected():
    with pytest.raises(GenerationError, match="duplicato"):
        compilation.validate_proposals(
            result(proposal(), proposal()), inspect_docx(template_bytes()), sources()
        )


@pytest.mark.parametrize(
    "field",
    [
        proposal(value="Dato inventato"),
        proposal(evidence=[]),
        proposal(kind="declaration"),
        proposal(kind="choice"),
        proposal(cell_id="t0.r2.c1", label="Nome", kind="data"),
    ],
)
def test_unsupported_values_declarations_and_disguised_signatures_are_not_written(field):
    parsed = compilation.validate_proposals(
        result(field), inspect_docx(template_bytes()), sources()
    )
    assert parsed["fields"][0]["written_value"] is None
    assert parsed["fields"][0]["status"] == "needs_review"
    assert parsed["fields"][0]["validation_notes"]


def test_general_knowledge_is_not_company_evidence():
    context = sources()
    context.selected[0]["scope"] = "general"
    parsed = compilation.validate_proposals(
        result(proposal()), inspect_docx(template_bytes()), context
    )
    assert parsed["fields"][0]["written_value"] is None


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    init_database()
    seed_database()
    seed_markdown_artifacts()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


async def add_company(client):
    response = await client.post(
        "/api/global-knowledge/files",
        files={"file": ("azienda.txt", b"Denominazione: Mapi Ingegneria S.r.l.", "text/plain")},
        data={"category": "company"},
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_api_compiles_downloads_and_keeps_output_out_of_retrieval(client, monkeypatch):
    project_id = "fondo-riqualificazione-2027"
    await add_company(client)
    before = (await client.get(f"/api/projects/{project_id}")).json()
    captured = {}

    async def model(prompt, **_request_options):
        captured.update(json.loads(prompt))
        company = next(s for s in captured["sources"] if s["scope"] == "company")
        return (
            result(proposal(evidence=[{"source_id": company["id"], "quote": company["content"]}])),
            "test-model",
            100,
        )

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    original = template_bytes()
    response = await client.post(
        f"/api/projects/{project_id}/document-compilations",
        files={"file": ("modulo.docx", original, routes.DOCX_MIME)},
        data={"instructions": "Compila soltanto l'anagrafica"},
    )
    assert response.status_code == 201, response.text
    run = response.json()
    assert captured["user_instructions"] == "Compila soltanto l'anagrafica"
    assert "mappa-campi" not in json.dumps(captured)
    assert run["report"]["written_field_count"] == 1
    assert run["report"]["ready_for_submission"] is False
    downloaded = await client.get(run["downloads"]["docx"])
    assert downloaded.status_code == 200
    assert downloaded.headers["content-type"] == routes.DOCX_MIME
    document = Document(BytesIO(downloaded.content))
    assert document.tables[0].cell(0, 1).text == "Mapi Ingegneria S.r.l."
    assert document.paragraphs[0].text == DRAFT_NOTICE
    assert hashlib.sha256(downloaded.content).hexdigest() == run["report"]["output_sha256"]
    assert (await client.get(run["downloads"]["template"])).content == original
    assert (await client.get(run["downloads"]["report"])).json() == run["report"]
    assert len((await client.get(f"/api/projects/{project_id}/document-compilations")).json()) == 1
    detail = await client.get(f"/api/projects/{project_id}/document-compilations/{run['id']}")
    assert detail.json()["report"] == run["report"]
    assert (await client.get(f"/api/projects/{project_id}")).json()["files"] == before["files"]
    with connection() as db:
        assert (
            db.execute(
                "SELECT COUNT(*) FROM knowledge_artifacts WHERE kind = 'output_draft'"
            ).fetchone()[0]
            == 3
        )
        assert not db.execute(
            "SELECT id FROM document_chunks WHERE content LIKE ?", (f"%{DRAFT_NOTICE}%",)
        ).fetchall()
    wrong_project = await client.get(
        f"/api/projects/intervento-polo-scolastico/document-compilations/{run['id']}/download/docx"
    )
    assert wrong_project.status_code == 404
    await client.delete(f"/api/projects/{project_id}")
    assert (await client.get(run["downloads"]["docx"])).status_code == 404
    assert not (get_storage_path() / project_id).exists()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "name,data,status",
    [
        ("modello.pdf", b"pdf", 415),
        ("modello.doc", b"doc", 415),
        ("modello.docx", b"bad zip", 422),
    ],
)
async def test_api_invalid_inputs_do_not_call_model(client, monkeypatch, name, data, status):
    async def unexpected(_):
        pytest.fail("Il modello non deve essere chiamato")

    monkeypatch.setattr(compilation, "request_field_proposals", unexpected)
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/document-compilations",
        files={"file": (name, data)},
    )
    assert response.status_code == status


@pytest.mark.anyio
async def test_api_missing_key_and_invalid_model_do_not_persist_runs(client, monkeypatch):
    await add_company(client)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(url, files={"file": ("modulo.docx", template_bytes())})
    assert response.status_code == 503

    async def invalid(_, **_request_options):
        return "[]", "test", None

    monkeypatch.setattr(compilation, "request_field_proposals", invalid)
    response = await client.post(url, files={"file": ("modulo.docx", template_bytes())})
    assert response.status_code == 502
    assert (await client.get(url)).json() == []
    assert not list(get_storage_path().rglob("bozza.docx"))


@pytest.mark.anyio
async def test_sources_exclude_other_projects_templates_and_drafts(client):
    await add_company(client)
    created = await client.post(
        "/api/projects", json={"title": "Secondo progetto", "description": "Fonte riservata"}
    )
    one, two = "fondo-riqualificazione-2027", created.json()["id"]
    for project, content in ((one, b"fonte permessa"), (two, b"segreto altro progetto")):
        response = await client.post(
            f"/api/projects/{project}/files", files={"file": ("fonte.txt", content, "text/plain")}
        )
        assert response.status_code == 201
    loaded = compilation.load_compilation_sources(one)
    text = " ".join(source["content"] for source in loaded.selected)
    assert "fonte permessa" in text
    assert "segreto altro progetto" not in text
    assert all(
        source["source_kind"] not in {"template", "output_draft"} for source in loaded.selected
    )
    assert len({source["id"] for source in loaded.selected}) == len(loaded.selected)


@pytest.mark.anyio
async def test_deletion_during_generation_prevents_persistence(client, monkeypatch):
    await add_company(client)
    project = "fondo-riqualificazione-2027"

    async def model(prompt, **_request_options):
        company = next(s for s in json.loads(prompt)["sources"] if s["scope"] == "company")
        await client.delete(f"/api/projects/{project}")
        return (
            result(proposal(evidence=[{"source_id": company["id"], "quote": company["content"]}])),
            "test",
            1,
        )

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    response = await client.post(
        f"/api/projects/{project}/document-compilations",
        files={"file": ("modulo.docx", template_bytes())},
    )
    assert response.status_code == 404
    assert not list(get_storage_path().rglob("bozza.docx"))


@pytest.mark.anyio
async def test_transport_uses_dedicated_prompt_and_rejects_truncation(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    captured = {}

    def handler(request):
        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "model": "test",
                "choices": [{"finish_reason": "length", "message": {"content": "{}"}}],
            },
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        compilation.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    with pytest.raises(GenerationError, match="incompleta"):
        await compilation.request_field_proposals("JSON di prova")
    assert captured["messages"][0]["content"] == compilation.SYSTEM_PROMPT
    assert captured["response_format"] == {"type": "json_object"}
    assert "non firmare" in compilation.SYSTEM_PROMPT.casefold()


def missing_proposals(targets):
    return result(
        *(
            proposal(
                cell_id=target, status="missing", value=None, evidence=[], reason="Dato assente"
            )
            for target in targets
        )
    )


@pytest.mark.anyio
async def test_ollama_compilation_receives_the_proposal_schema(monkeypatch):
    from app.config import AISettings, use_ai_settings

    captured = {}

    def handler(request):
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={
            "model": "local", "done": True, "done_reason": "stop",
            "message": {"content": result(proposal())},
            "prompt_eval_count": 12, "eval_count": 6,
        })

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        compilation.httpx, "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    with use_ai_settings(AISettings(
        api_key=None, model="local", base_url="http://ollama.test", provider="ollama",
    )):
        content, model, tokens = await compilation.request_field_proposals("JSON di prova")
    assert captured["format"] == compilation.ModelProposals.model_json_schema()
    assert captured["stream"] is False
    assert model == "local"
    assert tokens == 18
    report = compilation.validate_proposals(content, inspect_docx(template_bytes()), sources())
    assert report["fields"][0]["written_value"] == "Mapi Ingegneria S.r.l."


@pytest.mark.parametrize("template_path", [
    CASE / "modello/domanda-partecipazione.docx",
    CASE.parent / "minervino-elenco-sia/originali/domanda-iscrizione.docx",
])
@pytest.mark.parametrize("repair", [False, True])
def test_compact_prompt_preserves_context_and_evidence(template_path, repair):
    layout = inspect_docx(template_path.read_bytes())
    original_catalog = json.dumps([layout.catalog, layout.paragraph_catalog])
    evidence = sources('Società: D\'Amico & Figli\nSede: Bari  (BA)\t"Italia"')
    instructions = "  Partecipazione singola.\nSottoscrittore: da confermare.  "
    targets = (*layout.cells, *layout.slots)[-32:]
    corrections = [{"proposal": proposal(cell_id=targets[0]), "errors": [
        {"code": "invalid_quote", "message": "Citazione non presente nella fonte."},
    ]}] if repair else None

    prompt = compilation.build_prompt(
        layout, evidence, "Società – domanda", instructions, targets, corrections=corrections
    )
    body = json.loads(prompt)

    assert body["sources"] == compilation.source_catalog(evidence, instructions)
    assert body["source_coverage"] == evidence.coverage()
    assert body["user_instructions"] == instructions
    assert body["user_instructions_source_id"] == "user:instructions"
    assert body["project_title"] == "Società – domanda"
    assert body["template_sha256"] == layout.sha256
    assert body["template_text"] == text_of(layout.document.element.body)
    assert body["unsupported_locations"] == layout.unsupported_locations
    assert body["target_ids"] == list(targets)
    if repair:
        assert body["correction_request"] == corrections
    else:
        assert "correction_request" not in body

    # The annotated text plus original placeholders must reconstruct every paragraph.
    for original, sent in zip(layout.paragraph_catalog, body["paragraphs"], strict=True):
        assert sent["text"] == original["text"]
        reconstructed = sent["text_with_fields"]
        for field in sent["fields"]:
            reconstructed = reconstructed.replace(f"[[{field['id']}]]", field["placeholder"])
            assert field["writable"] == (field["id"] in targets)
        assert reconstructed == original["text"]
        for key, value in original.items():
            if key not in {"text", "fields"}:
                assert sent[key] == value
        for before, after in zip(original["fields"], sent["fields"], strict=True):
            assert {k: v for k, v in after.items() if k != "writable"} == {
                k: v for k, v in before.items() if k != "writable"
            }

    assert len(prompt) < len(json.dumps(body, ensure_ascii=False))
    assert json.dumps([layout.catalog, layout.paragraph_catalog]) == original_catalog


@pytest.mark.anyio
async def test_real_template_is_batched_without_losing_context_or_mutating_layout(monkeypatch):
    layout = inspect_docx((CASE / "modello/domanda-partecipazione.docx").read_bytes())
    original_catalog = json.dumps([layout.catalog, layout.paragraph_catalog])
    captured = []

    async def model(prompt, **_request_options):
        body = json.loads(prompt)
        captured.append(body)
        targets = body["target_ids"]
        assert len(targets) <= 32
        writable = {
            cell["id"]
            for table in body["tables"]
            for row in table["rows"]
            for cell in row
            if cell["writable"]
        } | {
            field["id"]
            for paragraph in body["paragraphs"]
            for field in paragraph["fields"]
            if field["writable"]
        }
        assert writable == set(targets)
        assert len(body["tables"]) == 50
        assert body["template_text"] == text_of(layout.document.element.body)
        assert body["sources"] == compilation.source_catalog(sources())
        return missing_proposals(targets), "test", 100

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    report, model_name, tokens, execution = await compilation.compile_field_batches(
        layout, sources(), "Catanzaro", ""
    )
    assert len(captured) == 9
    assert [target for body in captured for target in body["target_ids"]] == [
        *layout.cells,
        *layout.slots,
    ]
    assert len(report["fields"]) == 279
    assert report["unclassified_fields"] == []
    assert model_name == "test"
    assert tokens == 900
    assert execution == {
        "batch_size": 32,
        "requests": 9,
        "completed_batches": 9,
        "truncated_responses": 0,
        "repair_requests": 0,
        "repair_attempted_fields": 0,
        "repaired_fields": 0,
        "repair_skipped_fields": 0,
        "out_of_batch_proposals": 0,
    }
    assert json.dumps([layout.catalog, layout.paragraph_catalog]) == original_catalog


@pytest.mark.anyio
async def test_truncated_batch_is_split_and_valid_results_are_combined(monkeypatch):
    layout = inspect_docx(template_bytes(("Societa", "CF", "Sede", "PEC")))
    captured = []

    async def model(prompt, **_request_options):
        targets = json.loads(prompt)["target_ids"]
        captured.append(targets)
        if len(targets) > 2:
            raise compilation.TruncatedCompilationError(tokens=30)
        return missing_proposals(targets), "test", 20

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    report, _, tokens, execution = await compilation.compile_field_batches(
        layout, sources(), "Test", ""
    )
    assert [len(batch) for batch in captured] == [4, 2, 2]
    assert [field["cell_id"] for field in report["fields"]] == list(layout.cells)
    assert tokens == 70  # Includes the discarded, paid-for truncated response.
    assert execution["requests"] == 3
    assert execution["completed_batches"] == 2
    assert execution["truncated_responses"] == 1


@pytest.mark.anyio
async def test_single_call_includes_all_catanzaro_candidates(monkeypatch):
    layout = inspect_docx((CASE / "modello/domanda-partecipazione.docx").read_bytes())
    captured = []

    async def model(prompt, **_request_options):
        body = json.loads(prompt)
        captured.append(body)
        writable = {
            cell["id"]
            for table in body["tables"]
            for row in table["rows"]
            for cell in row
            if cell["writable"]
        } | {
            field["id"]
            for paragraph in body["paragraphs"]
            for field in paragraph["fields"]
            if field["writable"]
        }
        assert writable == layout.candidate_ids == set(body["target_ids"])
        assert body["sources"] == compilation.source_catalog(sources())
        return missing_proposals(body["target_ids"]), "local-test", 100

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    report, model_name, tokens, execution = await compilation.compile_fields_once(
        layout, sources(), "Catanzaro", ""
    )
    assert len(captured) == 1
    assert len(report["fields"]) == execution["batch_size"] == 279
    assert report["unclassified_fields"] == []
    assert model_name == "local-test"
    assert tokens == 100
    assert execution["requests"] == execution["completed_batches"] == 1
    assert execution["repair_requests"] == 0


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["truncated", "empty_quote", "duplicate_id", "timeout"])
async def test_single_call_failure_never_retries_or_saves_a_draft(client, monkeypatch, failure):
    await add_company(client)
    calls = 0
    if failure == "timeout":
        monkeypatch.setattr(compilation, "SINGLE_CALL_TIMEOUT_SECONDS", 0.01)

    async def model(prompt, **_request_options):
        nonlocal calls
        calls += 1
        if failure == "timeout":
            await asyncio.sleep(10)
            pytest.fail("La richiesta deve essere annullata al timeout")
        if failure == "truncated":
            raise compilation.TruncatedCompilationError(tokens=100)
        if failure == "empty_quote":
            # Reproduce Gemma's invalid citation: readable JSON is insufficient.
            return result(proposal(evidence=[{"source_id": "company:1", "quote": ""}])), "test", 100
        return result(proposal(), proposal()), "test", 100

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(url, files={"file": ("modulo.docx", template_bytes())})
    assert response.status_code == 502, response.text
    assert calls == 1
    assert (await client.get(url)).json() == []
    assert not list(get_storage_path().rglob("bozza.docx"))


@pytest.mark.anyio
async def test_single_call_unknown_id_does_not_persist_partial_document(client, monkeypatch):
    await add_company(client)
    calls = []

    async def model(prompt, **_request_options):
        targets = json.loads(prompt)["target_ids"]
        calls.append(targets)
        return missing_proposals([*targets, "t999.r0.c1"]), "test", 10

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    project = "fondo-riqualificazione-2027"
    response = await client.post(
        f"/api/projects/{project}/document-compilations",
        files={"file": ("grande.docx", template_bytes(["Societa"] * 33))},
    )
    assert response.status_code == 502
    assert "sconosciuto" in response.json()["detail"]
    assert len(calls) == 1
    assert (await client.get(f"/api/projects/{project}/document-compilations")).json() == []
    assert not list(get_storage_path().rglob("bozza.docx"))


@pytest.mark.anyio
@pytest.mark.parametrize("include_assigned_field", [False, True])
async def test_explicit_legacy_batches_discard_out_of_batch_proposals_without_losing_valid_work(
    client, monkeypatch, include_assigned_field,
):
    await add_company(client)
    calls = []
    # Exercise the retained comparison strategy explicitly; the API defaults to one call.
    async def legacy_compile(*args):
        return await compilation.compile_document(*args, strategy="batches")

    monkeypatch.setattr(routes, "compile_document", legacy_compile)

    async def model(prompt, **_request_options):
        body = json.loads(prompt)
        calls.append(body["target_ids"])
        company = next(item for item in body["sources"] if item["scope"] == "company")

        def field(target, value="Mapi Ingegneria S.r.l."):
            return proposal(
                cell_id=target, value=value,
                evidence=[{"source_id": company["id"], "quote": company["content"]}],
            )

        if len(calls) == 1:
            # Future-group proposal must not fill/classify an omitted field later.
            return result(field(calls[0][0]), field("t0.r32.c1")), "test", 10
        # Even a supported value must not overwrite an already accepted field.
        extra = field(calls[0][0], value="Mapi")
        own = [field(body["target_ids"][0])] if include_assigned_field else []
        return result(extra, *own), "test", 12

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(
        url, files={"file": ("grande.docx", template_bytes(["Societa"] * 33))},
    )
    assert response.status_code == 201, response.text
    run = response.json()
    report = run["report"]
    assert len(calls) == 2
    assert report["total_tokens"] == 22
    assert report["written_field_count"] == (2 if include_assigned_field else 1)
    assert report["ready_for_submission"] is False
    assert report["execution"]["out_of_batch_proposals"] == 2
    assert report["execution"]["repair_requests"] == 0
    assert ("t0.r32.c1" in report["unclassified_fields"]) is not include_assigned_field
    assert len(report["fields"]) == report["written_field_count"]
    rejected = report["rejected_proposals"]
    assert [item["proposal"]["cell_id"] for item in rejected] == ["t0.r32.c1", calls[0][0]]
    assert [item["request"] for item in rejected] == [1, 2]
    assert all(item["validation_code"] == "outside_batch" for item in rejected)
    assert all(item["phase"] == "initial" for item in rejected)
    assert all(item["proposal"]["cell_id"] not in item["target_ids"] for item in rejected)
    assert any("2 proposte fuori dal gruppo" in warning for warning in report["warnings"])
    saved = (await client.get(f"{url}/{run['id']}")).json()
    assert saved["report"] == report
    assert (await client.get(run["downloads"]["report"])).json() == report
    output = Document(BytesIO((await client.get(run["downloads"]["docx"])).content))
    assert output.tables[0].cell(0, 1).text == "Mapi Ingegneria S.r.l."
    assert output.tables[0].cell(32, 1).text == (
        "Mapi Ingegneria S.r.l." if include_assigned_field else ""
    )
    assert all(output.tables[0].cell(row, 1).text == "" for row in range(1, 32))


@pytest.mark.anyio
async def test_api_compiles_all_fields_in_one_call_and_saves_one_document(client, monkeypatch):
    await add_company(client)
    calls = []

    async def model(prompt, **request_options):
        body = json.loads(prompt)
        calls.append(body["target_ids"])
        assert len(body["target_ids"]) == 33
        assert request_options == {
            "max_tokens": compilation.SINGLE_CALL_MAX_OUTPUT_TOKENS,
            "timeout_seconds": compilation.SINGLE_CALL_TIMEOUT_SECONDS,
        }
        company = next(item for item in body["sources"] if item["scope"] == "company")
        fields = [
            proposal(
                cell_id=target,
                evidence=[{"source_id": company["id"], "quote": company["content"]}],
            )
            for target in body["target_ids"]
        ]
        return json.dumps({"fields": fields, "warnings": ["Dati simulati"]}), "test", 10

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(
        url, files={"file": ("grande.docx", template_bytes(["Societa"] * 33))}
    )
    assert response.status_code == 201, response.text
    run = response.json()
    report = run["report"]
    assert len(calls) == 1
    assert report["written_field_count"] == 33
    assert report["total_tokens"] == 10
    assert report["execution"]["strategy"] == "single_call"
    assert report["execution"]["requests"] == 1
    assert report["execution"]["completed_batches"] == 1
    assert report["warnings"].count("Dati simulati") == 1
    assert len((await client.get(url)).json()) == 1
    output = await client.get(run["downloads"]["docx"])
    document = Document(BytesIO(output.content))
    assert all(row.cells[1].text == "Mapi Ingegneria S.r.l." for row in document.tables[0].rows)


@pytest.mark.anyio
async def test_api_keeps_valid_fields_and_reports_unrepaired_citations(client, monkeypatch):
    await add_company(client)
    calls = 0

    async def model(prompt, **_request_options):
        nonlocal calls
        calls += 1
        body = json.loads(prompt)
        company = next(item for item in body["sources"] if item["scope"] == "company")
        good = proposal(evidence=[{"source_id": company["id"], "quote": company["content"]}])
        bad = proposal(
            cell_id="t0.r1.c1", label="Codice fiscale",
            evidence=[{"source_id": "project:non-fornito", "quote": "Dato non documentato"}],
        )
        return result(good, bad), "test", 10

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(url, files={"file": ("modulo.docx", template_bytes())})
    assert response.status_code == 201, response.text
    report = response.json()["report"]
    assert calls == 1
    assert report["schema_version"] == 3
    assert report["written_field_count"] == report["blocked_field_count"] == 1
    assert report["ready_for_submission"] is False
    assert report["total_tokens"] == 10
    assert report["execution"]["repair_requests"] == 0
    assert report["execution"]["repair_skipped_fields"] == 1
    blocked = report["fields"][1]
    assert blocked["status"] == "needs_review"
    assert blocked["evidence"] == []
    assert blocked["rejected_evidence"][0]["source_id"] == "project:non-fornito"
    assert "repair" not in blocked
    saved = (await client.get(f"{url}/{response.json()['id']}")).json()
    assert saved["report"] == report
    output = await client.get(response.json()["downloads"]["docx"])
    document = Document(BytesIO(output.content))
    assert document.tables[0].cell(0, 1).text == "Mapi Ingegneria S.r.l."
    assert document.tables[0].cell(1, 1).text == ""
    assert document.tables[0].cell(2, 1).text == ""


@pytest.mark.anyio
async def test_api_preserves_user_provenance_without_a_fictitious_document(client, monkeypatch):
    await add_company(client)

    async def model(prompt, **_request_options):
        body = json.loads(prompt)
        user = next(item for item in body["sources"] if item["origin"] == "user"
                    and item["source_kind"] == "user_instructions")
        assert user["document_id"] is None
        return result(proposal(
            label="Referente", entity="person", value="Giulia Bianchi",
            evidence=[{"source_id": user["id"], "quote": user["content"]}],
        )), "test", 10

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/document-compilations",
        files={"file": ("referente.docx", template_bytes(("Referente", "Firma")))},
        data={"instructions": "Referente per questa pratica: Giulia Bianchi"},
    )
    assert response.status_code == 201, response.text
    report = response.json()["report"]
    assert report["written_field_count"] == 1
    assert report["ready_for_submission"] is False
    citation = report["fields"][0]["evidence"][0]
    assert citation["origin"] == citation["scope"] == "user"
    assert citation["document_id"] is citation["fragment"] is citation["page"] is None
    assert citation["source_kind"] == "user_instructions"
    assert report["execution"]["repair_requests"] == 0


@pytest.mark.anyio
async def test_decorative_batch_can_be_empty_and_missing_usage_is_not_undercounted(monkeypatch):
    layout = inspect_docx(template_bytes(["Societa"] * 33))
    calls = 0

    async def model(prompt, **_request_options):
        nonlocal calls
        calls += 1
        targets = json.loads(prompt)["target_ids"]
        if calls == 1:
            return result(), "test", None
        return missing_proposals(targets), "test", 10

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    report, _, tokens, execution = await compilation.compile_field_batches(
        layout, sources(), "Test", ""
    )
    assert len(report["fields"]) == 1
    assert len(report["unclassified_fields"]) == 32
    assert tokens is None
    assert execution["completed_batches"] == 2


@pytest.mark.anyio
@pytest.mark.parametrize(
    "failure", ["json", "filter", "empty", "single", "budget", "timeout"]
)
async def test_batch_failures_are_bounded_and_do_not_retry_unrelated_errors(monkeypatch, failure):
    layout = inspect_docx(template_bytes(("Societa",)))
    calls = 0
    if failure == "budget":
        monkeypatch.setattr(compilation, "MAX_BATCH_REQUESTS", 0)
    if failure == "timeout":
        monkeypatch.setattr(compilation, "COMPILATION_TIMEOUT_SECONDS", 0.01)

    async def model(prompt, **_request_options):
        nonlocal calls
        calls += 1
        if failure == "timeout":
            await asyncio.sleep(10)
        if failure == "single":
            raise compilation.TruncatedCompilationError()
        if failure == "filter":
            raise GenerationError("Filtro contenuti")
        if failure == "empty":
            return result(), "test", 5
        return '{"fields": [', "test", 5

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    with pytest.raises(GenerationError):
        await compilation.compile_field_batches(layout, sources(), "Test", "")
    assert calls == (0 if failure == "budget" else 1)


@pytest.mark.anyio
async def test_repeated_truncations_stop_at_request_budget(monkeypatch):
    layout = inspect_docx(template_bytes(["Societa"] * 8))
    monkeypatch.setattr(compilation, "MAX_BATCH_REQUESTS", 2)
    calls = 0

    async def model(prompt, **_request_options):
        nonlocal calls
        calls += 1
        raise compilation.TruncatedCompilationError()

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    with pytest.raises(GenerationError, match="limite di tentativi"):
        await compilation.compile_field_batches(layout, sources(), "Test", "")
    assert calls == 2


@pytest.mark.anyio
@pytest.mark.parametrize("reason", ["length", "content_filter", "tool_calls", None])
async def test_transport_preserves_truncation_usage_and_reports_other_stops(monkeypatch, reason):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def handler(request):
        return httpx.Response(
            200,
            json={
                "choices": [{"finish_reason": reason, "message": {"content": "{}"}}],
                "usage": {"total_tokens": 123},
            },
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        compilation.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    with pytest.raises(GenerationError) as raised:
        await compilation.request_field_proposals("JSON")
    if reason == "length":
        assert isinstance(raised.value, compilation.TruncatedCompilationError)
        assert raised.value.tokens == 123
        assert "token" in str(raised.value)
    else:
        assert not isinstance(raised.value, compilation.TruncatedCompilationError)
        assert "nessun file prodotto" in str(raised.value)


def test_persistence_rolls_back_files_if_write_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    init_database()
    seed_database()
    original_write = Path.write_bytes

    def write(path, data):
        if path.name == "bozza.docx":
            raise OSError("Disk full")
        return original_write(path, data)

    monkeypatch.setattr(Path, "write_bytes", write)
    with pytest.raises(OSError):
        routes._persist(
            "fondo-riqualificazione-2027",
            "modulo.docx",
            b"original",
            b"draft",
            {"created_at": "now"},
        )
    assert not list(get_storage_path().rglob("template.docx"))
    with connection() as db:
        assert db.execute("SELECT COUNT(*) FROM document_compilations").fetchone()[0] == 0


@pytest.mark.anyio
async def test_api_compiles_paragraphs_and_reports_mixed_coverage(client, monkeypatch):
    await add_company(client)
    document = Document()
    document.add_paragraph("Ragione sociale: {{ragione_sociale}}. Sede: ____.")
    document.add_paragraph("Firma: ____")
    document.add_paragraph("Nome: ____")._p.append(OxmlElement("w:sdt"))
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Codice fiscale"
    data = BytesIO()
    document.save(data)
    captured = {}

    async def model(prompt, **_request_options):
        captured.update(json.loads(prompt))
        company = next(s for s in captured["sources"] if s["scope"] == "company")
        return (
            result(
                proposal(
                    cell_id="p0.s0",
                    evidence=[{"source_id": company["id"], "quote": company["content"]}],
                ),
                proposal(
                    cell_id="p1.s0",
                    label="Nome",
                    evidence=[{"source_id": company["id"], "quote": company["content"]}],
                ),
            ),
            "test-model",
            120,
        )

    monkeypatch.setattr(compilation, "request_field_proposals", model)
    url = "/api/projects/fondo-riqualificazione-2027/document-compilations"
    response = await client.post(url, files={"file": ("paragrafi.docx", data.getvalue())})
    assert response.status_code == 201, response.text
    run = response.json()
    report = run["report"]
    assert report["schema_version"] == 3
    assert report["prompt_version"] == "docx-fields-v13-source-boundaries"
    assert report["execution"]["completed_batches"] == 1
    assert report["written_field_count"] == 1
    assert report["fields"][0]["location"] == {
        "kind": "paragraph",
        "paragraph": 1,
        "slot": 1,
        "placeholder": "{{ragione_sociale}}",
    }
    assert report["fields"][1]["written_value"] is None
    assert report["fields"][1]["status"] == "needs_review"
    assert report["unclassified_cells"] == ["t0.r0.c1"]
    assert report["unclassified_fields"] == ["p0.s1", "t0.r0.c1"]
    assert report["unsupported_locations"][0]["paragraph"] == 3
    assert (
        captured["paragraphs"][0]["text_with_fields"]
        == "Ragione sociale: [[p0.s0]]. Sede: [[p0.s1]]."
    )
    assert captured["paragraphs"][1]["fields"][0]["signature"] is True
    output = Document(BytesIO((await client.get(run["downloads"]["docx"])).content))
    assert output.paragraphs[1].text == "Ragione sociale: Mapi Ingegneria S.r.l.. Sede: ____."
    assert output.paragraphs[2].text == "Firma: ____"
    assert output.paragraphs[3].text == "Nome: ____"
    assert (await client.get(run["downloads"]["template"])).content == data.getvalue()


def test_person_data_label_is_not_treated_as_a_signature():
    document = Document()
    document.add_paragraph("Nome del firmatario: ____")
    data = BytesIO()
    document.save(data)
    parsed = compilation.validate_proposals(
        result(proposal(cell_id="p0.s0", label="Nome del firmatario")),
        inspect_docx(data.getvalue()),
        sources(),
    )
    assert parsed["fields"][0]["written_value"] is not None


@pytest.mark.anyio
async def test_api_paragraphs_without_placeholders_do_not_call_model(client, monkeypatch):
    async def unexpected(_):
        pytest.fail("Il modello non deve essere chiamato senza campi supportati")

    document = Document()
    document.add_paragraph("Nome:     Cognome:     ")
    data = BytesIO()
    document.save(data)
    monkeypatch.setattr(compilation, "request_field_proposals", unexpected)
    response = await client.post(
        "/api/projects/fondo-riqualificazione-2027/document-compilations",
        files={"file": ("senza-segnaposti.docx", data.getvalue())},
    )
    assert response.status_code == 422
    assert "Nessun campo supportato" in response.json()["detail"]
