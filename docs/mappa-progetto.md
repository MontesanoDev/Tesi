# Mappa e audit di Mapi RAG

Verifica del 3 ottobre 2026, sul codice del repository e sulle fixture versionate.
Punto di partenza: commit `6307952`. Le correzioni dell'audit sono conservate nel
commit `2e4e946`; la compilazione è stata poi semplificata a un unico percorso.

La base è utilizzabile per il prototipo, con una suite di regressione ampia e
buone separazioni fra originali, fonti e documenti generati. Non era però priva
di difetti: l'audit ha riprodotto problemi nella navigazione della chat, nella
validazione delle email, nel salvataggio degli artefatti e nel replay delle prove.
Questi punti sono stati corretti. Gli aggiornamenti successivi della compilazione
sono riportati qui sotto; i risultati dell'audit restano storici.

Aggiornamento del 5 ottobre 2026: i moduli sono ora indicizzati con ruolo `form`
e interrogabili dalla chat tramite un target distinto dalle fonti fattuali.
Le richieste miste confrontano ora requisiti e informazioni documentate in
contesti separati, con controllo backend del ruolo delle citazioni.
Il passaggio dei dati e le responsabilità qui sotto riflettono queste modifiche;
i conteggi delle verifiche dell'audit rimangono storici. Lo stato corrente e i
comandi di reindicizzazione sono in [STATUS.md](../STATUS.md) e nel README.

Aggiornamento del 6 ottobre: implementata la CompilationSession V1 backend,
con candidate persistiti, risoluzione SOURCE limitata, correzioni utente e
generazioni dall'originale. Guida e limiti in
[compilation-session-v1.md](compilation-session-v1.md). Il collegamento alla
chat e il menu `@` usano una selezione singola e routing semantico per avvio/ripresa.
L'avanzamento è automatico ma limitato da un budget persistito. La chat interpreta
risposte libere soltanto sul campo chiesto, con grounding USER e validazione;
le ambiguità richiedono chiarimento. I controlli tecnici sono nei dettagli.

## Struttura del repository

| Percorso | Responsabilità |
|---|---|
| `backend/app/` | 30 moduli Python, incluso `__init__.py`: API, persistenza, AI, retrieval, compilazione. Circa 8.800 righe prima degli interventi. |
| `backend/tests/` | Regressioni API e di dominio, provider simulati, fixture DOCX reali, Qdrant locale con embedding simulati. |
| `backend/scripts/` | Tre strumenti per creare progetti/fixture e reindicizzare i moduli archiviati. |
| `frontend/src/` | React e TypeScript: pagine, componenti, hook, client API, tipi, CSS e test. |
| `frontend/e2e/` | Dieci file di scenari Playwright e una fixture JSON; progetti desktop e mobile. |
| `demo-documents/` | 27 file versionati: bandi, moduli, fonti aziendali simulate e conoscenza tecnica. Input di test e script, da conservare. |
| `backend/data/` | Database, originali, artefatti e risultati locali; escluso da Git. |
| `.tools/`, `.uv-cache/`, `.npm-cache/`, altre cache | Strumenti e cache locali; non sono codice applicativo. |
| `start.sh` | Avvio coordinato di Uvicorn e Vite in sviluppo, porte configurabili, arresto dei processi. |
| `README.md`, `LICENSE`, `.gitignore` | Istruzioni operative, licenza e confini dei file versionati. |

Python e dipendenze sono dichiarati in `backend/pyproject.toml` e bloccati in
`backend/uv.lock`; le dipendenze JavaScript in `frontend/package.json` e
`frontend/package-lock.json`. La build frontend esegue TypeScript e poi Vite.
Il backend viene eseguito da Python: non ha un passaggio di compilazione analogo.

## Percorsi dei dati

```mermaid
flowchart TD
    UI[Interfaccia React] --> API[FastAPI]
    API --> DB[(SQLite)]
    API --> FILE[Originali e artefatti su disco]
    FONTI[PDF, TXT e Markdown come fonti] --> ING[Estrazione e frammentazione]
    ING --> DB
    DB --> FTS[FTS5]
    DB --> QDRANT[Qdrant con embedding Ollama]
    CHAT[Messaggio chat] --> PLAN[Decisione del modello]
    PLAN --> DIRETTA[Risposta diretta]
    PLAN --> RICERCA[Ricerca e selezione delle evidenze]
    FTS --> RICERCA
    QDRANT --> RICERCA
    RICERCA --> CONTESTI[Contesti filtrati form e source]
    CONTESTI --> RISPOSTA[Generazione e controllo delle citazioni e dei ruoli]
    RISPOSTA --> DB
    MODULI[Moduli caricati dalla UI] --> ARCHIVIO[Archivio con ruolo form]
    ARCHIVIO --> TESTO[Testo documentale DOCX o TXT]
    TESTO --> ING
    DOCX[Upload DOCX alla API di compilazione] --> PARSER[Catalogo di celle e segnaposti]
    PARSER --> PROPOSTE[Proposte del modello]
    DB --> CONTESTO[Selezione delle fonti per budget di caratteri]
    CONTESTO --> PROPOSTE
    PROPOSTE --> VALIDAZIONE[Validazione delle proposte]
    VALIDAZIONE --> BOZZA[Bozza DOCX e report]
    BOZZA --> FILE
```

L'API DOCX a chiamata unica è stata rimossa il 9 ottobre 2026; restano elenco,
dettaglio e download delle compilazioni salvate. Le nuove sessioni partono
invece dal `form_id` archiviato e riusano planner/retrieval SOURCE. La guida
delle sessioni contiene il nuovo flusso persistente.
La generazione Markdown costituisce un terzo percorso, distinto da chat e DOCX.
La chat seleziona `form` con un identificativo del modulo oppure `source`; FTS5,
Qdrant e rilettura delle evidenze applicano ruolo e progetto. I moduli non sono
ammessi nelle ricerche fattuali. Il target `mixed` usa query distinte nei due
ruoli, nello stesso motore, e mantiene separati i contesti fino alla generazione.
Le richieste esplicite di disponibilità hanno una protezione backend contro
la classificazione form errata. Dopo il retrieval FORM, il planner individua
etichette/estratti dei requisiti; il backend ne deriva le query SOURCE. Una
risposta anticipata nella decisione retrieve viene ignorata per queste richieste.
L'estrazione usa un prompt documentale dedicato e uno schema esplicito, con
campo e ruolo personale separati. Accetta fino a 32 proposte, verifica estratti
contigui nel FORM citato, deduplica e seleziona fino a 16 requisiti del turno.
Il solo retry usa gli stessi chunk e riporta gli errori concreti; una lista
ancora vuota non avvia SOURCE. I limiti di output non sostituiscono il grounding.
`source_planning.py` aggiunge una sola pianificazione in batch per più di due
requisiti: massimo sei gruppi semantici di quattro requisiti, due query e quattro
evidenze SOURCE per gruppo. Query costruite dalle etichette validate, budget
separati e deduplicazione conservano una mappa requisito/fonti ammesse. Gli
esclusi dal budget vengono distinti come non ricercati; non diventano mancanti
per assenza di dati. Le proposte coerenti troppo grandi sono suddivise, quelle
invalide usano un fallback limitato per ruolo personale/campo, senza retry AI.
`requirement_checks.py` conserva solo strutture temporanee del turno: requisiti,
proposte di valori con estratti e controllo della provenienza; nessuna sessione
o posizione DOCX. La risposta è composta da requisiti citati con `form`, valori
letterali sostenuti da `source`, requisiti non verificati e non ricercati.
Il matcher SOURCE ha un compito stabile indipendente dalla domanda originale.
Il controllo del numero di iscrizione professionale riconosce la relazione
locale fra iscrizione e numero, senza imporre la label FORM letterale; non
promuove numeri estranei nello stesso chunk. Dopo una correzione,
supporti del ruolo errato o senza riscontro vengono scartati senza perdere
quelli validi. L'assenza di source
pertinenti non rende compilabili i campi del form; l'assenza del form interrompe
il confronto senza sostituirlo con fonti aziendali.
La rappresentazione strutturale DOCX resta indipendente
da quella documentale usata per la chat.

Il modello dati conserva `project_files.kind` per il ruolo locale e
`global_documents.category` (`company`/`general`) per la KB globale. Lo scope
del retrieval è `project:ID` oppure `global`: entrambe le KB globali restano
condivise fra progetti e ammesse per source. I collegamenti globali per progetto
restano compatibilità; non restringono questa disponibilità. Il contesto
`get_company_context()` usato dalla generazione Markdown seleziona invece
soltanto company e non è cambiato. Nessuna categoria garantisce che un testo
documenti un valore dell'operatore. Scope e categoria sono conservati nei
payload Qdrant, nei `Document` LangChain, nei vicini, nella rilettura SQLite,
nelle evidenze API e nello storico; non sono nuove colonne del database.

## Backend: responsabilità dei moduli

Tutti i percorsi della tabella sono relativi a [backend/app](../backend/app).

| Modulo | Responsabilità e collegamenti |
|---|---|
| `main.py` | Applicazione FastAPI, inizializzazione, CORS, 28 operazioni HTTP, orchestrazione chat, upload fonti, artefatti e bozze Markdown. Registra quattro router. |
| `db.py` | Percorsi dati, connessioni SQLite, schema, migrazioni compatibili con installazioni precedenti, trigger FTS e timestamp dei progetti. |
| `repository.py` | CRUD e query, conversazioni, fonti globali/progetto, ricerca lessicale, selezione dei vicini, ricaricamento delle evidenze e metriche. |
| `schemas.py` | Contratti Pydantic di richieste e risposte pubbliche. |
| `seed.py` | Inizializzazione una tantum dei progetti e dei dati dimostrativi. |
| `ingestion.py` | Limite upload 20 MB, estrazione PDF/testo, frammenti da circa 1.200 caratteri con sovrapposizione di 200. |
| `artifacts.py` | File Markdown, hash, versioni, legami al progetto, reindicizzazione, migrazione dei vecchi artefatti. |
| `call_facts.py` | Lettura/scrittura dei fatti estratti, provenienza, revisione e stati dei fatti. |
| `fact_extraction.py` | Selezione delle fonti, richiesta AI e validazione dell'estrazione dei fatti del bando. |
| `draft_generation.py` | Generazione Markdown da template, fonti aziendali, dati di progetto e fatti; controlli sui riferimenti ai fatti. |
| `intents.py` | Decisione della chat, protezione delle richieste di disponibilità e lettura dei requisiti dopo retrieval FORM. Schemi e un tentativo di correzione per fase. |
| `requirement_checks.py` | Requisiti documentali del singolo turno, query SOURCE da etichette verificate, controllo di ruolo/estratti/valori/associazione e composizione della risposta informativa. Nessuna compilazione persistente. |
| `generation.py` | Contratti, timeout, troncamento, citazioni e conteggio token. Mixed chiede solo proposte strutturate di valori source; dopo la correzione conserva i riscontri validi e rende gli altri non verificati. |
| `retrieval.py` | Interfaccia LangChain comune a FTS5/Qdrant, fusione dei risultati e ampliamento del contesto. |
| `retrieval_documents.py` | Conversione fra evidenze applicative e `Document` LangChain. |
| `retrieval_settings.py` | Configurazione del retrieval, segreti cifrati e lock dell'indice locale. |
| `retrieval_routes.py` | Quattro operazioni HTTP: lettura/salvataggio impostazioni, verifica connessione e indicizzazione. |
| `retrieval_embeddings.py` | Adapter Ollama con divieto di troncamento degli input, controlli sui vettori e sull'identità del modello. |
| `vector_retrieval.py` | Corpus SQLite, sincronizzazione Qdrant per hash, filtri per progetto, rilettura dei risultati dalla fonte corrente. |
| `project_forms.py` | Quattro operazioni HTTP per upload, elenco, download e rimozione di originali DOCX/TXT; estrazione documentale, frammenti form e reindicizzazione esplicita dagli originali. |
| `docx_templates.py` | Validazione del contenitore DOCX, scoperta delle posizioni scrivibili, riconoscimento dei campi protetti e scrittura dall'originale. |
| `document_compilation.py` | Validatori condivisi delle proposte DOCX: schemi, citazioni, controlli numerici/email e protezioni. Il motore a chiamata unica è stato rimosso il 9 ottobre 2026. |
| `document_compilation_routes.py` | Storico delle compilazioni: elenco, dettaglio e download di originale, bozza e report; `_persist` è condiviso con la finalizzazione delle sessioni. La creazione dalla API è stata rimossa il 9 ottobre 2026. |
| `compilation_sessions.py` | Snapshot dell'originale/candidate, revisioni/versioni, aggiornamenti USER, finalizzazione con validatore e renderer esistenti. |
| `compilation_session_models.py`, `compilation_session_resolution.py`, `compilation_session_routes.py` | Contratti, risoluzione di massimo 12 candidate per richiesta tramite SOURCE e API della V1 backend. |
| `config.py` | Impostazioni AI e `ContextVar` per mantenere provider e modello durante un'operazione; importazione della configurazione ambiente preesistente. |
| `ai_providers.py` | Catalogo provider, protocolli, metadati per la UI e header di autenticazione. |
| `ai_profiles.py` | CRUD profili, selezione per progetto, cifratura delle chiavi e importazione della configurazione precedente. |
| `ai_transport.py` | Adapter dei protocolli AI; normalizza risposte, token e ragioni di arresto. Supporta schema JSON nativo su Ollama. |
| `ai_discovery.py` | Recupero dell'elenco modelli dal servizio configurato. |
| `ai_login.py` | Collegamento OpenRouter con PKCE e credenziali temporanee sul server. |
| `ai_routes.py` | Dieci operazioni HTTP per profili, login, selezione e verifica; errori di validazione privati senza ripetere i segreti inviati. |
| `__init__.py` | Inizializzazione del package. |

[backend/main.py](../backend/main.py) riesporta l'app come entry point compatibile;
`start.sh` usa invece `app.main:app`.

## API e persistenza

Sono dichiarate **49 operazioni HTTP applicative**, oltre alle route generate
da FastAPI per la documentazione.

| Prefisso o risorsa | Operazioni |
|---|---|
| `/api/health` | Stato del processo. |
| `/api/projects` e `/{project_id}` | Elenco, creazione, dettaglio, rinomina, eliminazione. |
| `/api/global-knowledge` e `/files` | Fonti globali, caricamento, rimozione e modifica testuale. |
| `/api/projects/{id}/files` | Fonti di progetto, caricamento, rimozione e modifica testuale. |
| `/api/projects/{id}/global-knowledge` | API conservata per l'accesso alle fonti globali; oggi sono condivise con tutti i progetti. |
| `/api/projects/{id}/artifacts` | Lettura e modifica degli artefatti Markdown. |
| `/api/projects/{id}/call-facts` | Estrazione, lettura e revisione dei fatti. |
| `/api/projects/{id}/draft/generate` | Bozza Markdown. |
| `/api/projects/{id}/answer`, `/evidence`, `/conversations/{conversation_id}` | Chat, ricerca esplicita e cronologia. |
| `/api/projects/{id}/forms` | Archivio degli originali da compilare. |
| `/api/projects/{id}/document-compilations` | Generazione DOCX e accesso ai risultati precedenti. |
| `/api/projects/{id}/document-review` | Vista dei campi dimostrativi. |
| `/api/settings/ai`, `/api/projects/{id}/ai-model` | Connessioni e selezione del modello. |
| `/api/settings/retrieval` | Configurazione e manutenzione del retrieval. |

Lo schema comprende 18 tabelle ordinarie e due tabelle virtuali FTS5:

| Gruppo | Tabelle |
|---|---|
| Progetti | `projects`, `project_files`, `knowledge_sources` |
| Fonti e indice | `document_chunks`, `document_chunks_fts`, `global_documents`, `global_document_chunks`, `global_document_chunks_fts`, `project_global_document_links` |
| Conversazioni | `conversations`, `conversation_turns` |
| Artefatti e risultati | `knowledge_artifacts`, `project_artifact_links`, `document_fields`, `document_compilations` |
| Stato iterativo DOCX | `compilation_sessions`, `compilation_session_revisions` |
| Configurazione | `app_metadata`, `ai_profiles`, `ai_preferences`, `ai_login_flows`, `project_ai_settings` |

`project_files.kind` distingue fonti, moduli e contenitori degli artefatti; esiste
anche il ruolo storico `template`. Template e output generati sono esclusi dalle
evidenze fattuali. Le fonti globali sono condivise; le fonti degli altri progetti
non vengono incluse nella ricerca del progetto corrente. Gli ID negativi delle
evidenze globali evitano collisioni con quelli delle evidenze di progetto.

I DOCX generati conservano hash di originale e output, provenienza e report di
validazione. Le nuove sessioni conservano lo stato modificabile e le revisioni;
i record `document_compilations` continuano a rappresentare risultati immutabili.

## Frontend

| File o gruppo | Funzione |
|---|---|
| `src/main.tsx`, `src/App.tsx` | Bootstrap React, router e associazione delle pagine agli URL. |
| `pages/ProjectsPage.tsx` | Elenco, ricerca, ordinamento e creazione dei progetti. |
| `pages/ProjectWorkspacePage.tsx` | Chat, cronologia, evidenze, rinomina/rimozione progetto e pannello documenti. |
| `components/ProjectKnowledgePanel.tsx` | Caricamento e modifica delle fonti testuali, rimozione fonti. |
| `components/ProjectFormsPanel.tsx` | Caricamenti multipli, download originali e rimozione moduli. |
| `pages/CompanyKnowledgePage.tsx` | Gestione delle fonti globali aziendali e tecniche. |
| `pages/GeneralSettingsPage.tsx`, `components/AiSettingsPanel.tsx`, `components/RetrievalSettingsPanel.tsx` | Configurazione AI e ricerca. |
| `components/ProjectModelSelector.tsx` | Selezione del modello dal compositore della chat. |
| `pages/DocumentReviewPage.tsx` | Revisione dimostrativa in sola lettura; non è l'editor del DOCX generato. |
| `pages/CandidatureDemoPage.tsx`, `pages/candidatureDemo.ts` | Demo concettuale autonoma: dati fittizi, file non elaborati, esportazione HTML. |
| `pages/KnowledgeArtifactsPage.tsx` | Redirect per vecchi segnalibri alla pagina del progetto. |
| `components/AppShell.tsx`, `LoadingState.tsx`, `StatusPill.tsx` | Navigazione e componenti condivisi. |
| `hooks/useProject.ts`, `hooks/useDismissibleMenu.ts` | Caricamento del progetto e gestione dei menu. |
| `api.ts`, `types.ts`, `sourceText.ts` | Trasporto HTTP, contratti TypeScript, nomi dei file e descrizione dei frammenti. |
| `App.css`, `index.css`, CSS dei componenti/pagine | Stili globali e delle aree funzionali. |
| `*.test.ts(x)`, `test/setup.ts` | Test Vitest/Testing Library. |

Gli URL principali sono `/projects`, `/projects/:id`,
`/projects/:id/conversations/:conversationId`, `/company-knowledge`, `/settings`,
`/projects/:id/review` e `/demo/candidatura`. `/projects/:id/knowledge` è un redirect.

## Script e fixture

| Script | Uso e stato |
|---|---|
| `create_tender_projects.py` | Crea i progetti di studio Catanzaro/Minervino nel database configurato. |
| `create_paragraph_template.py` | Genera una fixture DOCX con tabelle e segnaposti; non sovrascrive file esistenti. |
| `reindex_project_forms.py` | Riestrae/suddivide gli originali DOCX/TXT di un progetto o singolo modulo; aggiorna SQLite/FTS5 senza modificare i file. Sincronizzazione Qdrant opzionale con `--sync-vectors`. |

`demo-documents/bandi/` contiene Catanzaro, Minervino e Trapani; `general-kb/`
contiene la conoscenza tecnica. La visura e le generalità aziendali sono simulate.
La mappa campi di Catanzaro serve alle prove: il motore applicativo non la usa per
codificare risposte specifiche del bando.

## Codice morto e compatibilità

**Rimosso:** `react-markdown`, `remark-frontmatter` e `remark-gfm`. Nessun import
applicativo li utilizzava. La rimozione elimina 103 voci del grafo dei pacchetti
installati/bloccati, senza aggiungerne altre. Il bundle già non li utilizzava:
questo intervento alleggerisce le dipendenze, non dimostra un guadagno di velocità
durante l'uso della pagina.

**Rimosso il 9 ottobre 2026 (primo taglio di potatura, branch `prune-backend`):**
il prototipo globale a chiamata unica (`global_compilation.py`, CLI e test), il
vecchio motore DOCX (`compile_document`, prompt e trasporto in
`document_compilation.py`, endpoint POST `/document-compilations`), gli script
`compile_docx_demo.py`, `compile_docx_ollama.py`, `replay_docx_audit.py` con i
relativi test, e gli otto metodi client morti (`projectArtifacts`,
`projectArtifact`, `updateProjectArtifact`, `generateDraft`,
`documentCompilations`, `documentCompilation`, `compileDocument`,
`projectEvidence`) con i tipi collegati. Conservati i validatori condivisi
(`StrictModel`, `CompilationSources`, `validate_proposals`), lo storico con
download e `_persist`.

**Da conservare:** il parser/writer DOCX, i validatori condivisi, la persistenza
delle sessioni e lo storico delle compilazioni restano raggiungibili da API,
sessioni e test. La modalità a gruppi da 32 era già stata rimossa; i test dei
controlli sui valori restano attivi. Le API Markdown sono ancora esposte. La
demo e la revisione hanno route attive. Il redirect e la migrazione dei template
legacy gestiscono compatibilità reale. La mancanza di una voce visibile nel menu
non prova che questi moduli siano morti.

La ricerca dei riferimenti non ha trovato funzioni top-level Python prive di
riferimenti tra applicazione e script dopo aver escluso gli entry point
decorati. È un controllo statico orientativo, non una prova di raggiungibilità
di ogni ramo. Non è stata misurata la copertura dei selettori CSS nel browser.

## Problemi riprodotti e interventi

| Priorità | Difetto osservato | Intervento e prova |
|---|---|---|
| Alta | Una risposta chat tardiva poteva riaprire il progetto/conversazione lasciato; un errore tardivo poteva contaminare il nuovo turno e sbloccare un'altra richiesta. | Annullamento della richiesta e controllo dell'identità dell'operazione. Quattro test comprendono cambio progetto, cambio conversazione, errore e percorso normale. Prima della correzione tre fallivano. |
| Alta | Una citazione abbreviata poteva nascondere parti di un indirizzo email e autorizzare la scrittura di un recapito diverso. | Verifica dei confini nell'intera fonte, all'interno del passaggio citato. Quattro regressioni fallivano prima della correzione; coperto anche il caso valido con spazi/punteggiatura. |
| Alta | Un errore SQL o di indicizzazione poteva lasciare l'artefatto modificato con hash/versione/indice precedenti. | Transazione di scrittura prima della lettura, sostituzione del file dopo l'indicizzazione e ripristino dei byte se il commit fallisce. File temporanei univoci e ripuliti. Quattro prove di guasto coprono metadati, indice, commit e sostituzione file. |
| Media | Il replay non inoltrava `max_tokens`/`timeout_seconds` e cercava il template solo nella vecchia cartella. | Opzioni inoltrate e supporto per layout corrente e storico, con due prove complete senza provider reale. |

Inoltre sono stati abilitati i controlli TypeScript `strict` per applicazione e
configurazione Vite. Il codice esistente li superava già. Ollama riceve ora anche
per il DOCX lo schema JSON di `ModelProposals`, derivato dal validatore effettivo.
La versione del prompt è ora `docx-fields-v14-whole-document`: tutte le posizioni
candidate del DOCX appartengono alla stessa richiesta. I nuovi report usano lo
schema 4 e descrivono l'esecuzione con `strategy`, `candidate_count` e `requests`,
senza contatori di gruppi o correzioni. I report già salvati restano consultabili
e scaricabili nella forma originale.

Annullare la richiesta browser impedisce effetti tardivi sulla UI; non garantisce
che il provider o il server interrompano una generazione già iniziata. Il ripristino
degli artefatti copre le eccezioni provate, non rende file e SQLite una transazione
unica resistente a un arresto improvviso del processo o del sistema.

## Questioni aperte

| Priorità | Punto | Implicazione |
|---|---|---|
| Alta per la nuova compilazione | Workflow conversazionale e chiarimento USER sul campo chiesto implementati. | Valutare con provider reale routing, classificazione dei candidate e domande condizionali; non confondere test software con qualità semantica. |
| Alta per affidabilità dei dati | Controlli prevalentemente sintattici e letterali. | Un valore autentico può essere assegnato al soggetto/sezione sbagliati; una citazione valida non prova l'affermazione. |
| Media | Il percorso DOCX precedente seleziona fonti distribuite per budget: 40.000 caratteri aziendali, 90.000 di progetto e 20.000 generali. | Le sessioni usano invece retrieval SOURCE mirato; rimangono falsi negativi conservativi e limiti del contesto. |
| Media | Il percorso DOCX precedente mantiene la chiamata unica da 1.800 secondi/32.768 token. | Le sessioni offrono passi da massimo 180 secondi e stato riprendibile; non è ancora misurata la qualità con provider reali del nuovo workflow. |
| Media | `repository.py` e `main.py` concentrano molte responsabilità. | Separare routing/orchestrazione, persistenza e validatori durante gli interventi funzionali; evitare una riscrittura generale solo per ridurre le righe. |
| Media | `_finish_ingestion` estrae PDF e suddivide il testo sincronicamente dentro una funzione async. | Un PDF impegnativo può occupare l'event loop; da spostare in un worker/thread con limiti espliciti. È una valutazione del percorso, non un benchmark di carico. |
| Media | File caricati come fonti vengono scritti prima dell'inserimento nel database; la compensazione non copre ogni errore successivo. | Possibili file orfani su errore di persistenza. Da uniformare al salvataggio dei moduli. |
| Media | Qdrant riconcilia l'intero corpus prima di ogni ricerca e serializza il lavoro con un lock. | Adeguato al corpus del prototipo; costo e contesa crescono con documenti e utenti. Non misurati sotto carico. |
| Media | Nessuna autenticazione applicativa; `start.sh` ascolta su `0.0.0.0`. | Il modello di utilizzo attuale è locale/rete fidata; un accesso condiviso richiederebbe una decisione esplicita su identità e autorizzazioni. |
| Bassa | Creazione progetto nel frontend senza gestione esplicita del rifiuto della richiesta e senza blocco di invii ripetuti. | Un errore API non viene presentato nel modulo di creazione; da correggere nel prossimo intervento sulla pagina. |
| Bassa | Nessuna pipeline CI versionata; E2E misti fra API simulate e backend reale. | Le verifiche dipendono dai comandi locali; conviene separare i gruppi di test e automatizzare quelli isolati. |

La suite non misura una percentuale di accuratezza del modello. Le prove con
provider simulati verificano il software; una valutazione semantica richiede
risposte reali e campi attesi annotati.

## Passo successivo per la compilazione

La V1 backend e il workflow conversazionale realizzano i punti seguenti.
Il prossimo passo è valutarli con provider reale: un DOCX, una sezione ambigua
e un chiarimento utente, conservando gli errori di associazione osservati.

1. Collegare una sessione al `form_id` e all'hash dell'originale, verificando progetto e formato.
2. Conservare mappa dei campi, proposte, fonti, problemi aperti e versioni della sessione.
3. Separare informazioni da cercare nelle fonti e scelte da chiedere all'utente.
4. Cercare evidenze mirate per i campi irrisolti, con budget e condizioni di arresto.
5. Registrare le correzioni come dati dell'utente e preservarle nei passaggi successivi.
6. Rigenerare ogni versione dall'originale e dallo stato; non reinterpretare una bozza come template.
7. Esporre stato, chiarimenti, report e download nella chat, misurando errori di soggetto/posizione oltre ai campi riempiti.

Parser, validatori, writer DOCX, profili AI e retrieval sono riutilizzati dalle
sessioni. La V1 e il collegamento conversazionale chat/`@` sono implementati,
inclusi chiarimenti liberi sul campo chiesto. Correzioni arbitrarie di altri campi
e interpretazione di risposte su più campi restano fuori da questo percorso.

## Verifiche

Il punto di partenza superava 659 test backend e 57 test frontend, Ruff, Oxlint e
build Vite. I nuovi test hanno esposto difetti che non erano coperti dalla suite.

| Verifica al termine dell'audit | Esito |
|---|---|
| Pytest backend | 671 test superati. |
| Vitest frontend | 61 test superati, in 11 file. |
| Playwright selezionato | 10 test superati, su desktop e mobile. |
| Ruff e Oxlint | Nessun errore. |
| TypeScript strict e build Vite | Completati. |
| `bash -n start.sh`, `./start.sh --help` | Completati. |
| `git diff --check` | Nessun errore di whitespace. |

Nessuna chiamata reale ai provider è stata necessaria per questi test.

Dopo la rimozione della modalità a gruppi, l'intera suite backend supera
637 test. Sono stati rimossi i casi dedicati al comportamento abbandonato e
conservate le verifiche sui valori, aggiungendo controlli sul percorso unico e
sull'accesso ai report storici. I moduli Catanzaro e Minervino inviano tutti i
279 e 254 candidati in una sola richiesta nelle prove con provider simulato.
Ruff, Oxlint, TypeScript strict e build Vite passano anche dopo la semplificazione.
Queste prove verificano il percorso software; non misurano la qualità delle
proposte prodotte da un modello reale.

```bash
cd backend
uv run --locked pytest -q
uv run --locked ruff check .
cd ../frontend
npm test
npm run lint
npm run build
# Con Vite avviato su una porta dedicata:
PLAYWRIGHT_BASE_URL=http://127.0.0.1:5179 npm run test:e2e -- \
  e2e/composer-model-menu.spec.ts e2e/document-review.spec.ts e2e/project-forms.spec.ts
```

Le verifiche API usano database/cartelle temporanei. I dieci scenari browser
selezionati usano API simulate su desktop/mobile. Gli altri E2E e i benchmark con
modelli reali non fanno parte di questa esecuzione.
