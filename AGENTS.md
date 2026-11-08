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
  Dal 24 ottobre le nuove sessioni usano un solo profilo per sezioni, definito in
  `compilation_profile.py` (la UI lo chiama soltanto «Compilazione DOCX»); le sessioni
  esistenti conservano il loro profilo e `MAPI_COMPILATION_PROFILE=storico` è solo
  un rollback di emergenza lato server, non una modalità da esporre.
  Dal 13 ottobre le nuove compilazioni della chat usano il motore globale V12:
  una chiamata per il catalogo, proposta persistita, dialogo USER ed export
  esplicito di una bozza parziale dall'originale. La breve sintesi AI è separata
  dall'analisi; solo domande e risposte nel composer, niente checklist/ID XML.
  Il backend possiede gli slot attivi e conserva rinvii, condizioni e provenance.
  La sintesi può escludere proposte dubbie, mai rilassare il grounding SOURCE. Non promuovere automaticamente
  GROUNDED_PROPOSAL a RESOLVED. V12 conserva anche motivazioni MODEL dei vuoti
  ancorate al FORM, omissioni e spiegazioni respinte distinte: non sono prove
  di assenza nelle SOURCE, decisioni di scrittura o stato live dopo risposte USER.
  Le checkbox native legacy/content control usano
  gruppi FORM ancorati e cardinalità rivalidata; SOURCE o scelta USER del gruppo
  attivo sostengono i booleani. Deselezioni di alternative esclusive sono effetti
  tracciati, non nuovi fatti. Gruppi incompleti/ambigui non vengono esportati;
  la copertura dei gruppi senza SOURCE resta un limite del modello. Versioni
  precedenti restano leggibili, senza upgrade delle sessioni o migrazioni implicite.
  V1 resta nelle API/sessioni legacy, senza avanzamento automatico della UI.
  Non reintrodurre il vecchio motore a gruppi. La chat usa una mention `@` singola,
  routing semantico e avanzamento automatico con budget persistito. Nel percorso
  legacy le risposte libere riguardano soltanto il campo chiesto, con estratto USER e validazione;
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
- Per il nuovo motore usare la fixture dedicata
  `demo-documents/benchmark-compilazione/v1/` e registrare ogni esperimento in
  [relazioni.md](relazioni.md), incluse prove fallite e limiti delle misure.
  Gold e risultati attesi non entrano nel prompt. Congelare fixture/fonti/gold
  nei confronti; nuovi scenari richiedono una nuova versione, senza adattare
  le aspettative agli output del modello.
- Affiancare ogni tanto al benchmark fisso una prova su un altro bando reale
  scelto a caso, come richiesto dall'utente. Registrare pool, estrazione e tutti
  gli esiti, senza ripetere l'estrazione per ottenere un risultato migliore.
  Tenere queste prove separate dai confronti sulla fixture congelata; senza
  gold non dichiarare percentuali di accuratezza. Non serve farle a ogni passo.
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
`composer-model-menu.spec.ts`, `compilation-chat.spec.ts`, `global-compilation.spec.ts`,
`document-review.spec.ts` e `project-forms.spec.ts`
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

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

### Perimetro Graphify di questo progetto

- La mappa ordinaria comprende soltanto `backend/app/**/*.py` e il codice
  TypeScript/TSX di `frontend/src/`, esclusi i test. La lista ammessa è in
  `.graphifyignore`: non allargarla a dati, documenti, audit, fixture o benchmark.
- Prima costruzione: `graphify extract . --code-only`. Aggiornamento dopo
  modifiche o cambio branch: `graphify update .`; conserva lo stesso perimetro.
- Per simboli noti preferire `graphify explain "nome"`; per esplorazione usare
  `graphify query "termini del codice" --budget 1000`. I risultati possono essere
  troncati o incompleti: verificare nel sorgente i passaggi rilevanti prima dei fix.
- `graphify-out/` è locale e ignorata da Git. Ogni worktree deve avere la propria
  mappa; non copiare quella dell'app in una candidata con codice diverso.
- Nessuna estrazione semantica, chiamata LLM, cloud, hook Git o modalità watch
  è necessaria per questa configurazione. Guida: `docs/graphify-app-2026-10-28.md`.
