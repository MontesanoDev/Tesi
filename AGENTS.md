# Indicazioni per lavorare su Mapi RAG

## Riprendere il lavoro

1. Leggere [STATUS.md](STATUS.md): contiene il punto di ripresa, le richieste
   dell'utente, le modifiche pendenti e le questioni ancora aperte.
2. Controllare `git status --short --branch` e gli ultimi commit prima di
   modificare file: il repository può essere cambiato fra due conversazioni.
3. Consultare [README.md](README.md) per avvio e comandi e
   [docs/mappa-progetto.md](docs/mappa-progetto.md) per l'audit e la mappa estesa.
   I conteggi e gli esiti dell'audit sono storici; verificare nel codice ciò che
   serve al lavoro corrente.

Lavorare e comunicare in italiano. Qui «compilazione» indica soprattutto la
compilazione dei moduli con dati e fonti, non la build del frontend.
Le ipotesi in STATUS.md sono contesto di progetto, non istruzioni per avviare
automaticamente tutte le funzionalità proposte. Seguire la richiesta corrente.

## Prima di implementare

Se STATUS.md indica che una scelta architetturale o di prodotto è ancora
"da discutere", non trasformarla autonomamente in una decisione.

Presentare prima alternative e trade-off all'utente, salvo richiesta esplicita
di implementazione.

Prima di scrivere codice per il nuovo motore di compilazione, comunicare le
scelte progettuali concrete, i trade-off e i criteri di verifica. Procedere
per passi misurati, conservando una baseline recuperabile del sistema attuale.

## Struttura e punti di ingresso

Prototipo di tesi per consultare fonti aziendali/documenti di gara e compilare
bozze verificabili. Stack: FastAPI, Python, SQLite, React/TypeScript/Vite,
LangChain con FTS5 o Qdrant. I provider AI si configurano dalla UI; la chat e gli
embedding hanno configurazioni distinte. Il modello predefinito degli embedding
è BGE-M3 tramite Ollama.

| Area | File principali |
|---|---|
| API, schema e persistenza | `backend/app/main.py`, `schemas.py`, `db.py`, `repository.py` |
| Upload fonti e frammentazione | `backend/app/ingestion.py` |
| Archivio originali da compilare | `backend/app/project_forms.py` |
| Chat, pianificazione e risposta | `backend/app/intents.py`, `generation.py` |
| Retrieval e indice vettoriale | `backend/app/retrieval.py`, `retrieval_documents.py`, `vector_retrieval.py`, `retrieval_embeddings.py` |
| Parser, validatori e compilazione DOCX | `backend/app/docx_templates.py`, `document_compilation.py`, `document_compilation_routes.py` |
| Sessioni DOCX persistenti e chat | `backend/app/compilation_chat.py`, `backend/app/compilation_sessions.py`, `compilation_session_models.py`, `compilation_session_resolution.py`, `compilation_session_routes.py` |
| Artefatti e bozze testuali | `backend/app/artifacts.py`, `call_facts.py`, `fact_extraction.py`, `draft_generation.py` |
| Workspace e moduli nella UI | `frontend/src/pages/ProjectWorkspacePage.tsx`, `frontend/src/components/ProjectFormsPanel.tsx` |
| Contratti frontend | `frontend/src/api.ts`, `frontend/src/types.ts` |
| Test e fixture | `backend/tests/`, `frontend/src/**/*.test.*`, `frontend/e2e/`, `demo-documents/` |

## Regole di progetto

- Conservare le modifiche dell'utente già presenti. Evitare ripristini, commit
  e push non richiesti e riscritture generali estranee al lavoro in corso.
- Distinguere il **modulo**, che descrive richieste e campi, dalle **fonti**, che
  documentano i dati da inserire. Una dichiarazione prestampata non dimostra il
  possesso di un requisito da parte dell'azienda. Conservare provenienza,
  progetto e ruolo del documento nei percorsi che utilizzano le evidenze.
- Preservare gli originali e l'isolamento fra progetti. Template e bozze generate
  non devono diventare automaticamente prove fattuali. Quando si modifica il
  retrieval, considerare FTS5, Qdrant, espansione dei vicini e rilettura delle
  evidenze, non soltanto il prompt.
- L'upload dei moduli accetta attualmente DOCX/TXT. La API DOCX precedente usa
  una sola chiamata; la vecchia modalità a gruppi e le riparazioni automatiche
  sono state rimosse. La CompilationSession V1, autorizzata successivamente,
  itera sullo stato persistente con passi limitati, sempre da un solo originale.
  Non reintrodurre il vecchio motore a gruppi. La chat usa una mention `@` singola,
  routing semantico e avanzamento automatico con budget persistito. Le risposte
  libere riguardano soltanto il campo chiesto, con estratto USER e validazione;
  ambiguità e valori non grounded richiedono chiarimento. Non estendere questo
  percorso a modifiche arbitrarie di campi o generazioni incomplete implicite.
- Non eliminare funzioni soltanto perché non sono raggiungibili dal menu:
  possono servire alle API, agli script, ai test o alla compatibilità. Consultare
  la sezione sul codice morto nella mappa del progetto.
- `backend/data/` contiene dati locali ed è esclusa da Git. Per le diagnosi sui
  dati esistenti preferire letture senza modifiche; per i test usare database e
  storage temporanei. Non riportare credenziali, contenuti di `.env` o `.ai-key`
  nei documenti di passaggio. Conservare le fixture di `demo-documents/`.
- Salvare diagnosi e benchmark in modo durevole: report e riepiloghi in `docs/`,
  acquisizioni grezze in `backend/data/compilation-audit/`, con riferimenti nel
  report. Non lasciare gli unici risultati in `/tmp`. Conservare prompt/schema,
  output reali, tempi, validazioni e stato quando acquisiti, senza credenziali;
  dichiarare eventuali dati non acquisiti. Gli artefatti locali esclusi da Git
  richiedono un backup separato e non vengono pubblicati con il solo push.
- Distinguere sempre test del software con provider simulati da valutazioni
  della qualità delle risposte reali. Citazioni formalmente valide e stato
  `completed` non garantiscono una risposta pertinente o supportata dalle fonti.

## Avvio e verifiche

Requisiti e installazione sono nel README. Avvio dalla radice: `./start.sh`.
Porte predefinite: frontend 5173, backend 8000. Lo script supporta il Node locale
in `.tools/node/bin`; se npm usa un Node incompatibile, verificare questo percorso.

Backend, da `backend/`:

```bash
uv run --locked pytest -q
uv run --locked ruff check .
```

Frontend, da `frontend/`:

```bash
npm test
npm run lint
npm run build
```

Eseguire controlli proporzionati alla modifica. Per sole modifiche documentali
controllare diff, riferimenti e coerenza; non occorre ripetere tutte le suite.
Per gli E2E serve il frontend avviato e Chromium installato. Gli scenari
`composer-model-menu.spec.ts`, `compilation-chat.spec.ts`, `document-review.spec.ts` e `project-forms.spec.ts`
usano API simulate. Altri scenari usano il backend e possono modificare dati:
configurare un ambiente temporaneo prima di eseguirli. `PLAYWRIGHT_BASE_URL`
permette di scegliere l'istanza frontend.

## Mantenere la continuità

Al termine di un intervento significativo aggiornare STATUS.md con modifiche,
verifiche effettivamente eseguite, limiti e prossimo punto di ripresa. Tenere
separate funzionalità implementate, preferenze dell'utente e proposte da valutare.
Indicare quando una correzione richiede una migrazione o una reindicizzazione
ancora non effettuata. Non presentare test precedenti come appena rieseguiti.
AGENTS.md contiene indicazioni stabili; STATUS.md contiene lo stato che cambia.
