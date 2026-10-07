"""Role routing with real FTS5/local Qdrant and simulated planning/embeddings."""

import json
import re
from contextlib import closing
from pathlib import Path

import httpx
import pytest
from ollama import Client, ListResponse
from qdrant_client import QdrantClient

from app import main, retrieval, vector_retrieval
from app.db import connection, get_db_path, get_storage_path, init_database
from app.project_forms import _form_chunks
from app.repository import create_project, reload_evidence
from app.retrieval_settings import RetrievalInput, resolve_settings, save_settings
from app.schemas import ProjectCreate

FIXTURE = (Path(__file__).resolve().parents[2] / "demo-documents/bandi/"
           "catanzaro-dl-cse/modello/domanda-partecipazione.docx")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(params=["fts5", "qdrant"])
async def chat(tmp_path, monkeypatch, request):
    monkeypatch.setenv("MAPI_DB_PATH", str(tmp_path / "forms.db"))
    monkeypatch.setenv("MAPI_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setenv("MAPI_KNOWLEDGE_PATH", str(tmp_path / "knowledge"))
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "http://provider.test")
    monkeypatch.setenv("DEEPSEEK_MODEL", "test-model")
    init_database()
    for title in ("Alpha", "Beta"):
        create_project(ProjectCreate(title=title, description="Progetto di prova"))
    monkeypatch.setattr(Client, "list", lambda *args: ListResponse(models=[
        {"model": "bge-m3", "digest": "simulated-forms-v1"},
    ]))
    # Constant embeddings deliberately make irrelevant/other-project chunks competitive.
    monkeypatch.setattr(Client, "embed", lambda *args, **kw: {
        "embeddings": [[1.0, 0.5, 0.1] for _ in kw["input"]],
    })
    save_settings(RetrievalInput(backend=request.param))
    original = httpx.AsyncClient
    async with original(
        transport=httpx.ASGITransport(app=main.app), base_url="http://test",
    ) as client:
        replies, requests = [], []
        def handler(req):
            body = json.loads(req.content)
            requests.append(body)
            assert replies, "Unexpected generation instead of a backend stop"
            reply = replies.pop(0)
            if callable(reply):
                reply = reply(body)
            return httpx.Response(200, json={
                "model": "test-model", "usage": {"total_tokens": 10},
                "choices": [{"message": {"content": json.dumps(reply)},
                             "finish_reason": "stop"}],
            })
        monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(
            transport=httpx.MockTransport(handler), **kw,
        ))
        yield client, replies, requests, request.param


async def upload(client, project="alpha", name="domanda-partecipazione.docx", text=None):
    content = FIXTURE.read_bytes() if text is None else text.encode()
    response = await client.post(f"/api/projects/{project}/forms", files={"file": (name, content)})
    assert response.status_code == 201, response.text
    return response.json()


async def global_source(client, text, category="company"):
    response = await client.post("/api/global-knowledge/files", data={"category": category},
                                 files={"file": ("azienda.txt", text.encode())})
    assert response.status_code == 201, response.text
    return response.json()


def plan(target, form_id=None, query="Domanda partecipazione requisiti dichiarazioni allegati"):
    return {"action": "retrieve", "target": target, "form_id": form_id,
            "answer": "", "queries": [query]}


def requirements(*names):
    return {"requirements": [
        {"name": name, "form_quote": name, "form_citation_id": 1} for name in names
    ]}


def supports_from_prompt(body, values):
    prompt = body["messages"][1]["content"]
    parts = re.split(r"EVIDENZA \[(\d+)]", prompt)
    supports = []
    for requirement_id, quote, value in values:
        citation = next(int(index) for index, block in zip(parts[1::2], parts[2::2], strict=True)
                        if "Ruolo: source" in block and quote in block)
        supports.append({"requirement_id": requirement_id, "source_citation_id": citation,
                         "source_quote": quote, "value": value})
    return {"supports": supports}


@pytest.mark.anyio
async def test_summary_of_only_archived_docx_uses_form_and_never_global_sources(chat):
    client, replies, requests, _ = chat
    form = await upload(client)
    await global_source(client, "Domanda partecipazione: dati aziendali mancanti; partita IVA 999.")
    other = await upload(client, "beta")
    replies.extend([plan("form", form["id"]), {
        "answer": "Il modulo contiene dati del sottoscrittore e dichiarazioni [1].",
        "citation_ids": [1],
    }])
    response = await client.post("/api/projects/alpha/answer", json={
        "question": "riassumi la domanda di partecipazione",
    })
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["generation_status"] == "completed"
    assert result["evidence"]
    assert {item["file_id"] for item in result["evidence"]} == {form["id"]}
    assert all(item["role"] == "form" and item["project_id"] == "alpha"
               for item in result["evidence"])
    inventory = requests[0]["messages"][1]["content"]
    assert f'"id": {form["id"]}' in inventory and form["name"] in inventory
    assert f'"id": {other["id"]}' not in inventory
    prompt = requests[1]["messages"][1]["content"]
    assert "Ruolo: form" in prompt and "MODULO DA ANALIZZARE" in prompt
    assert "dati aziendali mancanti" not in prompt and "Ruolo: source" not in prompt
    assert "partecipazione" in prompt.lower()
    history = (await client.get(
        f"/api/projects/alpha/conversations/{result['conversation_id']}",
    )).json()["turns"]
    assert history[0]["evidence"] == result["evidence"]


@pytest.mark.anyio
async def test_factual_query_cannot_use_value_or_declaration_from_form(chat):
    client, replies, requests, _ = chat
    await upload(client, name="domanda.txt", text=(
        "Partita IVA dell'azienda 999999. L'operatore dichiara di possedere ISO 9001."
    ))
    replies.append(plan("source", query="partita IVA azienda ISO 9001"))
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "qual è la partita IVA dell'azienda?",
    })).json()
    assert result["generation_status"] == "no_evidence"
    assert result["evidence"] == [] and len(requests) == 1
    assert "999999" not in result["answer"]


@pytest.mark.anyio
async def test_factual_query_still_uses_global_source_and_not_form(chat):
    client, replies, requests, _ = chat
    await upload(client, name="domanda.txt", text="Partita IVA di Mapi: 999999, da dichiarare.")
    source = await global_source(client, "Partita IVA di Mapi: 01234567890.")
    replies.extend([plan("source", query="partita IVA Mapi"), {
        "answer": "Partita IVA 01234567890 [1].", "citation_ids": [1],
    }])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "qual è la partita IVA di Mapi?",
    })).json()
    assert result["generation_status"] == "completed"
    assert {item["file_id"] for item in result["evidence"]} == {-source["id"]}
    assert all(item["role"] == "source" for item in result["evidence"])
    assert "999999" not in requests[1]["messages"][1]["content"]


@pytest.mark.anyio
@pytest.mark.parametrize("missing", [
    "legacy", "wrong_role", "other_project", "unknown", "ambiguous",
])
async def test_missing_form_evidence_has_no_factual_fallback_or_generation(
    chat, missing, monkeypatch,
):
    client, replies, requests, _ = chat
    form = await upload(client, "beta" if missing == "other_project" else "alpha",
                        name="domanda.txt", text="Domanda partecipazione requisiti allegati.")
    if missing == "legacy":
        with connection() as db:
            db.execute("DELETE FROM document_chunks WHERE file_id=?", (form["id"],))
    selected = 99999 if missing == "unknown" else form["id"]
    if missing == "ambiguous":
        await upload(client, name="altro.txt", text="Altro modulo")
        selected = None
    await global_source(client, "Domanda partecipazione requisiti allegati: dati Mapi.")
    if missing == "wrong_role":
        wrong = retrieval.search_project_evidence("alpha", "Domanda partecipazione")
        assert wrong and all(item["role"] == "source" for item in wrong)
        monkeypatch.setattr(main, "search_project_evidence", lambda *a, **kw: wrong)
    replies.append(plan("form", selected))
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "riassumi la domanda di partecipazione",
    })).json()
    assert result["generation_status"] == "no_evidence"
    assert result["evidence"] == [] and result["citations"] == []
    assert "Non riesco a recuperare il contenuto del modulo richiesto" in result["answer"]
    assert len(requests) == 1


@pytest.mark.anyio
async def test_mixed_request_without_sources_analyzes_only_requirements(chat):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ______")
    replies.extend([
        {**plan("mixed", form["id"], "denominazione sociale"),
         "source_queries": ["denominazione sociale operatore"]},
        requirements("Denominazione sociale"),
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "Cosa richiede il modulo e abbiamo i dati per soddisfarlo?",
    })).json()
    assert result["generation_status"] == "completed"
    assert "non ho trovato fonti fattuali" in result["answer"]
    assert "Denominazione sociale: disponibilità non verificata" in result["answer"]
    assert all(item["role"] == "form" for item in result["evidence"])
    assert len(requests) == 2
    prompt = requests[1]["messages"][1]["content"]
    assert all(item["role"] == "form" for item in json.loads(prompt)["evidenze_FORM"])
    assert result["missing_information"] == ["Denominazione sociale"]


@pytest.mark.anyio
@pytest.mark.parametrize("category", ["company", "general"])
async def test_mixed_request_supports_value_from_actual_kb_not_from_module(
    chat, monkeypatch, category,
):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ______")
    source = await global_source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.", category)
    searches = []
    original = main.search_project_evidence
    def recorded(project, query, **kwargs):
        searches.append((kwargs["target"], kwargs["form_id"], query))
        return original(project, query, **kwargs)
    monkeypatch.setattr(main, "search_project_evidence", recorded)
    replies.extend([
        {**plan("mixed", form["id"], "denominazione sociale richiesta"),
         "source_queries": ["denominazione sociale Mapi", "DENOMINAZIONE SOCIALE MAPI"]},
        requirements("Denominazione sociale"),
        {"supports": [{"requirement_id": 1, "source_citation_id": 2,
                       "source_quote": "Denominazione sociale: Mapi Ingegneria S.r.l.",
                       "value": "Mapi Ingegneria S.r.l."}]},
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "abbiamo i dati per compilare questa parte?",
    })).json()
    assert result["generation_status"] == "completed"
    assert searches == [
        ("form", form["id"], "denominazione sociale richiesta"),
        ("source", None,
         "Denominazione sociale ragione sociale S.r.l. S.p.A. dati effettivi operatore economico"),
    ]
    assert result["citations"] == [1, 2] and result["total_tokens"] == 30
    assert "Mapi Ingegneria S.r.l." in result["answer"]
    assert [(item["role"], item["scope"], item["category"]) for item in result["evidence"]] == [
        ("form", "project:alpha", None), ("source", "global", category),
    ]
    assert result["evidence"][1]["file_id"] == -source["id"]
    prompt = requests[2]["messages"][1]["content"]
    form_part, factual_part = prompt.split("FONTI FATTUALI (role=source):")
    assert "Mapi Ingegneria S.r.l." not in form_part
    assert "Mapi Ingegneria S.r.l." in factual_part and f"KB category: {category}" in factual_part
    history = (await client.get(
        f"/api/projects/alpha/conversations/{result['conversation_id']}",
    )).json()["turns"]
    assert history[0]["evidence"] == result["evidence"]


@pytest.mark.anyio
@pytest.mark.parametrize("category", ["company", "general"])
async def test_mixed_request_does_not_treat_general_instructions_as_operator_data(chat, category):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text=(
        "L'operatore dichiara di possedere la certificazione ISO 9001. F_ORIGIN"
    ))
    await global_source(
        client, "ISO 9001: norme e criteri generali di certificazione. S_ORIGIN", category,
    )
    replies.extend([
        {**plan("mixed", form["id"], "certificazione ISO 9001"),
         "source_queries": ["Mapi certificazione ISO 9001 posseduta"]},
        requirements("certificazione ISO 9001"),
        {"supports": []},
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "possiamo compilare questo requisito?",
    })).json()
    assert result["generation_status"] == "completed"
    assert "non ho trovato fonti fattuali" in result["answer"]
    assert "Mapi possiede" not in result["answer"] and result["citations"] == [1]
    assert {item["role"] for item in result["evidence"]} == {"form", "source"}
    prompt = requests[2]["messages"][1]["content"]
    form_part, factual_part = prompt.split("FONTI FATTUALI (role=source):")
    assert "S_ORIGIN" not in form_part and "F_ORIGIN" not in factual_part
    assert result["missing_information"] == ["certificazione ISO 9001"]


@pytest.mark.anyio
async def test_mixed_request_keeps_project_and_global_sources_and_excludes_other_project(chat):
    client, replies, _, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale e PEC: ______")
    for project, text in (
        ("alpha", "PEC di Mapi: mapi@example.test."),
        ("beta", "Denominazione sociale di Mapi: AZIENDA_ALTRO_PROGETTO. PEC privata."),
    ):
        response = await client.post(f"/api/projects/{project}/files", files={
            "file": ("fonte.txt", text.encode()),
        })
        assert response.status_code == 201
    await global_source(client, "Denominazione sociale di Mapi: Mapi Ingegneria S.r.l.", "general")
    replies.extend([
        {**plan("mixed", form["id"], "denominazione sociale PEC"),
         "source_queries": ["denominazione sociale Mapi PEC"]},
        requirements("Denominazione sociale", "PEC"),
        lambda body: supports_from_prompt(body, [
            (1, "Denominazione sociale di Mapi: Mapi Ingegneria S.r.l.", "Mapi Ingegneria S.r.l."),
            (2, "PEC di Mapi: mapi@example.test.", "mapi@example.test"),
        ]),
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "con i documenti che ho posso iniziare a compilarlo?",
    })).json()
    assert result["generation_status"] == "completed"
    factual = [item for item in result["evidence"] if item["role"] == "source"]
    assert {(item["scope"], item["category"]) for item in factual} == {
        ("project:alpha", None), ("global", "general"),
    }
    assert all("AZIENDA_ALTRO_PROGETTO" not in item["excerpt"] for item in result["evidence"])


@pytest.mark.anyio
@pytest.mark.parametrize("unavailable", ["unknown", "unindexed"])
async def test_mixed_request_missing_form_does_not_substitute_global_sources(chat, unavailable):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale richiesta: ______")
    if unavailable == "unindexed":
        with connection() as db:
            db.execute("DELETE FROM document_chunks WHERE file_id=?", (form["id"],))
    await global_source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.")
    replies.append({
        **plan("mixed", 99999 if unavailable == "unknown" else form["id"], "denominazione sociale"),
        "source_queries": ["denominazione sociale Mapi"],
    })
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "con i documenti che ho posso iniziare a compilarlo?",
    })).json()
    assert result["generation_status"] == "no_evidence"
    assert result["evidence"] == [] and len(requests) == 1
    assert "Non riesco a recuperare il contenuto del modulo richiesto" in result["answer"]


@pytest.mark.anyio
async def test_mixed_fact_citing_form_becomes_unverified_after_unsuccessful_repair(chat):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ______")
    await global_source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.")
    invalid = {"supports": [{"requirement_id": 1, "source_citation_id": 1,
                             "source_quote": "Denominazione sociale: ______",
                             "value": "Mapi Ingegneria S.r.l."}]}
    replies.extend([
        {**plan("mixed", form["id"], "denominazione sociale"),
         "source_queries": ["denominazione sociale Mapi"]},
        requirements("Denominazione sociale"), invalid, invalid,
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "abbiamo i dati per compilare questa parte?",
    })).json()
    assert result["generation_status"] == "completed"
    assert "Mapi Ingegneria S.r.l." not in result["answer"]
    assert "Denominazione sociale: disponibilità non verificata" in result["answer"]
    assert result["citations"] == [1] and result["missing_information"] == ["Denominazione sociale"]
    assert len(requests) == 4
    assert requests[3]["messages"][:2] == requests[2]["messages"]
    assert "ruolo source" in requests[3]["messages"][-1]["content"]


@pytest.mark.anyio
async def test_factual_iva_question_cannot_use_blank_form_field(chat):
    client, replies, requests, _ = chat
    await upload(client, name="domanda.txt", text="Partita IVA operatore economico ______")
    replies.append(plan("source", query="partita IVA"))
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "qual è la partita IVA?",
    })).json()
    assert result["generation_status"] == "no_evidence" and result["evidence"] == []
    assert len(requests) == 1


@pytest.mark.anyio
async def test_real_gemma_misrouting_is_upgraded_before_search_and_empty_sources_stop_claims(chat):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ____")
    replies.extend([
        {**plan("form", form["id"], "denominazione sociale"),
         "answer": "Con i documenti forniti è possibile compilare la denominazione sociale."},
        requirements("Denominazione sociale"),
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "posso compilare la denominazione sociale?",
    })).json()
    assert result["generation_status"] == "completed"
    assert "Denominazione sociale: disponibilità non verificata" in result["answer"]
    assert "non posso ancora considerarli compilabili" in result["answer"]
    assert "utilizzabile per una prima compilazione" not in result["answer"]
    assert "Con i documenti forniti è possibile" not in result["answer"]
    assert len(requests) == 2  # With zero SOURCE the backend renders without a final LLM call.


@pytest.mark.anyio
async def test_generic_availability_queries_come_from_form_and_verify_only_supported_field(
    chat, monkeypatch,
):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text=(
        "Denominazione sociale: ____\nDirettore tecnico: ____"
    ))
    await global_source(client, "Mapi Ingegneria S.r.l.")
    searches = []
    original = main.search_project_evidence
    def recorded(project, query, **kwargs):
        searches.append((kwargs["target"], query))
        return original(project, query, **kwargs)
    monkeypatch.setattr(main, "search_project_evidence", recorded)
    replies.extend([
        plan("form", form["id"], "denominazione sociale direttore tecnico"),
        requirements("Denominazione sociale", "Direttore tecnico"),
        {"supports": [{"requirement_id": 1, "source_citation_id": 2,
                       "source_quote": "Mapi Ingegneria S.r.l.",
                       "value": "Mapi Ingegneria S.r.l."}]},
    ])
    question = "con i documenti che ho posso iniziare a compilarlo?"
    result = (await client.post("/api/projects/alpha/answer", json={"question": question})).json()
    assert result["generation_status"] == "completed"
    assert "Denominazione sociale: Mapi Ingegneria S.r.l. [2]" in result["answer"]
    assert "Direttore tecnico: disponibilità non verificata" in result["answer"]
    assert result["missing_information"] == ["Direttore tecnico"]
    assert searches == [
        ("form", "denominazione sociale direttore tecnico"),
        ("source",
         "Denominazione sociale ragione sociale S.r.l. S.p.A. dati effettivi operatore economico"),
        ("source", "Direttore tecnico dati effettivi operatore economico"),
    ]
    assert question not in [query for target, query in searches if target == "source"]
    prompt = requests[2]["messages"][1]["content"]
    assert "REQUISITI DA VERIFICARE" in prompt and "FONTI FATTUALI (role=source)" in prompt


@pytest.mark.anyio
async def test_separate_budgets_keep_sources_when_form_candidates_outnumber_them(chat, monkeypatch):
    client, replies, _, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ____ " * 400)
    for index in range(4):
        await global_source(client, f"Denominazione sociale: Mapi {index} S.r.l.")
    original = main.search_project_evidence
    counts = {}
    def extra_candidates(project, query, **kwargs):
        kwargs["limit"] = 8 if kwargs["target"] == "form" else 4
        rows = original(project, query, **kwargs)
        counts[kwargs["target"]] = len(rows)
        return rows
    monkeypatch.setattr(main, "search_project_evidence", extra_candidates)
    replies.extend([plan("mixed", form["id"], "denominazione sociale"),
                    requirements("Denominazione sociale"), {"supports": []}])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "con i documenti che ho posso iniziare a compilarlo?",
    })).json()
    assert result["generation_status"] == "completed"
    assert counts == {"form": 8, "source": 4}
    assert len([item for item in result["evidence"] if item["role"] == "form"]) == 4
    assert len([item for item in result["evidence"] if item["role"] == "source"]) == 4


@pytest.mark.anyio
async def test_form_only_generation_cannot_publish_compilability_from_valid_form_citation(chat):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ____")
    invalid = {"answer": "Possiamo compilare la denominazione sociale [1].", "citation_ids": [1]}
    replies.extend([plan("form", form["id"], "denominazione sociale"), invalid, invalid])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "quali dati richiede il modulo?",
    })).json()
    assert result["generation_status"] == "failed" and result["answer"] is None
    assert len(requests) == 3


def engineering_requirements(body, *, director_only=False):
    # Ground truth from the actual fixture section, never from the user question.
    evidence = json.loads(body["messages"][1]["content"])["evidenze_FORM"]
    row = next(item for item in evidence
               if "5.d)" in item["testo"] and "Data di abilitazione" in item["testo"])
    section = row["testo"].split("5.d)")[1].split("5.e)")[0]
    company = ["Denominazione sociale", "iscrizione alla CCIAA", "numero e data d’iscrizione",
               "forma giuridica", "sede legale"]
    personal = ["Nome e cognome", "qualifica professionale", "Data di abilitazione",
                "Ordine professionale", "numero di iscrizione all’Albo professionale"]
    result = []
    for name in (personal if director_only else company + personal + ["organigramma"]):
        person_role = "direttore tecnico" if name in personal else ""
        start = section.index(person_role) if person_role else section.index(name)
        end = section.index(name, start) + len(name)
        result.append({"name": name, "person_role": person_role, "form_quote": section[start:end],
                       "form_citation_id": row["form_citation_id"]})
    return {"requirements": result}


async def engineering_form(client):
    # Hold the relevant FORM context constant across real FTS5/Qdrant with mock embeddings.
    chunk = next(text for text in _form_chunks(FIXTURE.read_bytes(), ".docx")
                 if "5.d)" in text and "Data di abilitazione" in text)
    section = "5.d)" + chunk.split("5.d)")[1].split("5.e)")[0]
    return await upload(client, name="sezione-ingegneria.txt", text=section)


@pytest.mark.anyio
@pytest.mark.parametrize("retry", [False, True])
async def test_engineering_section_more_than_eight_requirements_reaches_sources(
    chat, monkeypatch, retry,
):
    client, replies, requests, _ = chat
    form = await engineering_form(client)
    await global_source(client, "Denominazione sociale: Mapi Ingegneria S.r.l.")
    queries = []
    search = main.search_project_evidence
    def record(project, query, **kwargs):
        queries.append((kwargs["target"], query))
        return search(project, query, **kwargs)
    monkeypatch.setattr(main, "search_project_evidence", record)
    replies.append(plan("mixed", form["id"], "società di ingegneria direttore tecnico"))
    if retry:
        replies.append({"requirements": []})
    replies.extend([engineering_requirements, {"clusters": [
        {"requirement_ids": ids} for ids in ([1, 2, 3, 4], [5], [6, 7, 8, 9], [10], [11])
    ]}, lambda body: supports_from_prompt(body, [
        (1, "Denominazione sociale: Mapi Ingegneria S.r.l.", "Mapi Ingegneria S.r.l."),
    ])])
    response = (await client.post("/api/projects/alpha/answer", json={
        "question": ("Con i documenti disponibili, quali dati della sezione società di ingegneria "
                     "possiamo già compilare?"),
    })).json()
    assert response["generation_status"] == "completed", response["notice"]
    assert len(response["missing_information"]) == 10
    assert "Denominazione sociale: Mapi Ingegneria S.r.l." in response["answer"]
    assert "direttore tecnico: Data di abilitazione" in response["missing_information"]
    assert len([q for target, q in queries if target == "source"]) == 7
    assert any("direttore tecnico" in q for target, q in queries if target == "source")
    assert {e["role"] for e in response["evidence"]} == {"form", "source"}
    assert len(requests) == (5 if retry else 4)
    if retry:
        assert requests[1]["messages"][1] == requests[2]["messages"][1]


@pytest.mark.anyio
@pytest.mark.parametrize("invalid", [False, True])
async def test_false_user_premise_cannot_start_sources_after_two_unsupported_extractions(
    chat, monkeypatch, invalid,
):
    client, replies, requests, _ = chat
    form = await upload(client, name="domanda.txt", text="Denominazione sociale: ____")
    await global_source(client, "Mapi possiede ISO 9001: identificativo MAPI-001.")
    search = main.search_project_evidence
    def only_form(project, query, **kwargs):
        assert kwargs["target"] == "form", "An unsupported user premise started factual search"
        return search(project, query, **kwargs)
    monkeypatch.setattr(main, "search_project_evidence", only_form)
    extraction = requirements("ISO 9001") if invalid else {"requirements": []}
    replies.extend([plan("mixed", form["id"], "denominazione sociale"), extraction, extraction])
    response = (await client.post("/api/projects/alpha/answer", json={
        "question": "Il modulo richiede la ISO 9001: Mapi la possiede?",
    })).json()
    assert response["generation_status"] == ("failed" if invalid else "no_evidence")
    assert "non è stata valutata" in (response["answer"] or response["notice"])
    assert {e["role"] for e in response["evidence"]} == {"form"}
    assert len(requests) == 3


@pytest.mark.anyio
async def test_director_data_are_checked_individually_against_demo_source(chat):
    client, replies, _, _ = chat
    form = await engineering_form(client)
    text = (Path(__file__).resolve().parents[2] / "demo-documents/generalita-mapi.md").read_text()
    director = text.split("### Ing. Elisa Romano")[1].split("### Arch.")[0]
    director = "Ing. Elisa Romano" + director
    await global_source(client, director)
    replies.extend([
        plan("mixed", form["id"], "società di ingegneria direttore tecnico"),
        lambda body: engineering_requirements(body, director_only=True),
        {"clusters": [{"requirement_ids": [1, 2, 3, 4]}, {"requirement_ids": [5]}]},
        lambda body: supports_from_prompt(body, [
            (1, director, "Elisa Romano"), (2, director, "Ingegnere"),
            (4, director, "Ordine degli Ingegneri di Bari"), (5, director, "8421"),
        ]),
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": ("Il modulo richiede i dati del direttore tecnico. Con le fonti disponibili "
                     "abbiamo tutto ciò che serve per compilare quella parte?"),
    })).json()
    assert result["generation_status"] == "completed", result["notice"]
    assert result["missing_information"] == ["direttore tecnico: Data di abilitazione"]
    for value in ("Elisa Romano", "Ingegnere", "Ordine degli Ingegneri di Bari", "8421"):
        assert value in result["answer"]
    assert result["answer"].count("utilizzabile per una prima compilazione") == 4


@pytest.mark.anyio
@pytest.mark.parametrize("budget_limited", [False, True])
async def test_general_question_searches_each_group_without_global_top_k_loss(
    chat, monkeypatch, budget_limited,
):
    client, replies, requests, backend = chat
    names = [f"Campo{index:02}" for index in range(1, 17)]
    if backend == "qdrant":
        # A deterministic semantic space: each field has its own dimension.
        # This exercises real vector filtering/ranking without a real provider.
        monkeypatch.setattr(Client, "embed", lambda *args, **kw: {
            "embeddings": [[1.0 if name.casefold() in text.casefold() else 0.01 for name in names]
                           for text in kw["input"]],
        })
    form = await upload(
        client, name="modulo.txt", text="\n".join(f"{name}: ____" for name in names),
    )
    for index, name in enumerate(names, 1):
        await global_source(client, f"{name}: Valore{index:02}")
    cluster_ids = [] if budget_limited else [list(range(i, i + 4)) for i in (1, 5, 9, 13)]
    verified_ids = range(1, 7 if budget_limited else 17)
    replies.extend([
        plan("mixed", form["id"], " ".join(names)), requirements(*names),
        {"clusters": [{"requirement_ids": ids} for ids in cluster_ids]},
        lambda body: supports_from_prompt(body, [
            (i, f"Campo{i:02}: Valore{i:02}", f"Valore{i:02}") for i in verified_ids
        ]),
    ])
    result = (await client.post("/api/projects/alpha/answer", json={
        "question": "Possiamo completare oggi la domanda senza chiedere nulla all'utente?",
    })).json()
    assert result["generation_status"] == "completed", result["notice"]
    assert result["answer"].count("utilizzabile per una prima compilazione") == len(verified_ids)
    assert len(requests) == 4  # One grouping batch, not one LLM call per field.
    if budget_limited:
        assert len(result["missing_information"]) == 10
        assert all("non ricercato" in item for item in result["missing_information"])
        assert "Campo07: disponibilità non verificata" not in result["answer"]
    else:
        assert result["missing_information"] == []
        assert len([item for item in result["evidence"] if item["role"] == "source"]) == 16
        assert "non ricercati" not in result["answer"]


@pytest.mark.anyio
async def test_form_filters_neighbors_and_reload_keep_project_document_and_role(chat):
    client, _, _, _ = chat
    text = ("Domanda partecipazione: dati del sottoscrittore e allegati. " * 100)
    form = await upload(client, name="domanda.txt", text=text)
    sibling = await upload(client, name="altro.txt", text=text)
    await upload(client, "beta", name="domanda.txt", text=text)
    await global_source(client, text)
    results = retrieval.search_project_evidence(
        "alpha", "partecipazione", include_neighbors=True, target="form", form_id=form["id"],
    )
    assert results and {item["file_id"] for item in results} == {form["id"]}
    assert all(item["role"] == "form" and item["project_id"] == "alpha" for item in results)
    assert all(item["scope"] == "project:alpha" and item["category"] is None for item in results)
    assert reload_evidence("beta", results, target="form") == []
    assert reload_evidence("alpha", results, target="source") == []
    assert reload_evidence("alpha", results, target="form", form_id=sibling["id"]) == []
    forged = [{**item, "role": "source"} for item in results]
    assert reload_evidence("alpha", forged, target="source") == []


@pytest.mark.anyio
@pytest.mark.parametrize("category", ["company", "general"])
async def test_global_scope_and_category_survive_neighbors_and_reload(chat, category):
    client, _, _, _ = chat
    source = await global_source(
        client, "Denominazione sociale: Mapi Ingegneria S.r.l. " * 100, category,
    )
    results = retrieval.search_project_evidence(
        "alpha", "denominazione sociale", limit=1, include_neighbors=True,
    )
    assert len(results) >= 2
    reloaded = reload_evidence("beta", results)
    assert len(reloaded) == len(results)  # Both KBs remain shared between projects.
    for item in [*results, *reloaded]:
        assert item["role"] == "source" and item["project_id"] is None
        assert item["file_id"] == -source["id"] and item["source_name"] == "azienda.txt"
        assert item["scope"] == "global" and item["category"] == category
        assert item["document_metadata"] == source["metadata"]


@pytest.mark.anyio
async def test_delete_form_cleans_original_chunks_fts_and_vectors_on_reconciliation(chat):
    client, _, _, backend = chat
    form = await upload(client, name="domanda.txt", text="Domanda partecipazione requisiti.")
    other = await upload(
        client, "beta", name="domanda.txt", text="Domanda partecipazione requisiti.",
    )
    status = vector_retrieval.run_vector_search(resolve_settings()) if backend == "qdrant" else None
    response = await client.delete(f"/api/projects/alpha/forms/{form['id']}")
    assert response.status_code == 204
    assert not list((get_storage_path() / "alpha" / "_forms").glob("*.txt"))
    with connection() as db:
        for table in ("document_chunks", "document_chunks_fts"):
            assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE file_id=?",
                              (form["id"],)).fetchone()[0] == 0
    assert retrieval.search_project_evidence(
        "alpha", "Domanda", target="form", form_id=form["id"],
    ) == []
    assert retrieval.search_project_evidence("beta", "Domanda", target="form")
    if status:
        with closing(QdrantClient(path=str(get_db_path()) + ".qdrant")) as qdrant:
            points, _ = qdrant.scroll(status["collection"], with_payload=True)
            assert {point.payload["metadata"]["file_id"] for point in points} == {other["id"]}
            assert all(point.payload["metadata"]["role"] == "form" for point in points)
