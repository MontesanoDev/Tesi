# Mappa del codice morto e del debito tecnico

**Verifica successiva alla pulizia**

La pulizia è stata riesaminata e salvata nel commit `b2e4687`. Il controllo
ha incluso backend, frontend, persistenza, provider AI, retrieval, compilazione
e avvio dell'applicazione. Non sono emerse regressioni nei flussi verificati;
sono stati riprodotti e corretti questi problemi aggiuntivi:

| Problema | Correzione | Verifica |
| --- | --- | --- |
| La cancellazione di una fonte globale eliminava prima il record dal database. Un errore nella rimozione del file lasciava persi anche i frammenti indicizzati. | La transazione termina dopo la rimozione del file. Un errore ripristina record, frammenti e indice FTS; i percorsi esterni alla cartella dei file vengono rifiutati. | Sei casi per Company KB e General KB: file già assente, permessi insufficienti e percorso non valido. |
| Un progetto eliminato mentre la chat lavorava poteva causare un errore interno o una violazione delle chiavi esterne al salvataggio della risposta. | Il salvataggio verifica la conversazione nella stessa transazione della scrittura. Se il progetto o la conversazione non esistono più, la richiesta termina con un 404 spiegato. | Tre casi: eliminazione durante la ricerca, durante una generazione riuscita e durante una generazione fallita. |
| `start.sh` accettava una porta backend diversa, ma Vite continuava a inoltrare le API alla 8000. Anche le origini CORS erano fissate alla 5173. | Proxy e origini locali seguono le porte configurate. Le porte vengono validate; Vite non ne sceglie un'altra se quella richiesta è occupata. | Avvio completo su backend 8096 e frontend 5197, richiesta `/api/health` attraverso il proxy, verifica CORS e sei valori di porta non validi. |
| D16: tre librerie importate dall'app erano disponibili solo come dipendenze transitive. | Dichiarati direttamente `lxml`, `pydantic` e `starlette`, con lockfile aggiornato. | Le versioni installate sono rimaste invariate; suite backend e lint superati. |

La transazione sulla cancellazione gestisce gli errori della rimozione del
file; non rende atomici filesystem e SQLite in caso di arresto del processo
fra rimozione e commit. L'indice vettoriale continua a essere riconciliato con
SQLite al momento della ricerca, secondo il comportamento già esistente.

**Esito delle verifiche**

- 570 test backend superati, inclusi i nove nuovi casi di regressione.
- 108 test frontend superati; TypeScript, lint Python/TypeScript e build superati.
- 58 scenari Playwright superati tra desktop e mobile: menu e profili AI,
  impostazioni retrieval, fonti, chat, revisione dimostrativa, template Word e
  testuali, ordinamento progetti e demo candidatura.
- Prove browser svolte con API simulate oppure con backend reale su database
  temporaneo. La configurazione dei profili e la scelta del modello sono state
  salvate e rilette dal backend; discovery e risposte dei modelli erano simulate.
- Nessuna chiamata a provider AI reali e nessuna modifica ai dati applicativi
  dell'utente. Non è stata rieseguita la generazione del PDF di presentazione.

Queste prove verificano il software e i suoi controlli, non la qualità delle
interpretazioni del modello: un dato presente nella fonte può ancora essere
proposto per la persona o la sezione sbagliata. Non costituiscono un benchmark
RAG o una valutazione comparativa dei modelli.

Restano aperti i contratti legacy D02–D04, la strategia a gruppi conservata
per confronto D05 e il refactoring dei moduli e delle operazioni duplicate
D10–D11. Non sono stati eliminati percorsi ancora utilizzati da API, dati
storici o test. La build segnala ancora un bundle JavaScript di circa 504 kB:
è un intervento di ottimizzazione separato, non un errore di compilazione.

**Audit e prima pulizia**

Audit del 1 ottobre 2026, sul commit `ae16cb9`, seguito dalla pulizia autorizzata
descritta sotto. La mappa e i numeri di riga dell'audit fotografano la versione
precedente alla pulizia.

**Pulizia eseguita il 1 ottobre 2026**

FTS5 e l'integrazione LangChain/Qdrant sono rimasti invariati, come richiesto.
Il confronto dei file e delle funzioni conferma che non sono cambiati schema,
trigger, ingestion, indicizzazione attiva, query, ranking, embedding, retriever
e impostazioni della ricerca. Non sono state eseguite migrazioni dei dati.

| Rilievo | Stato dopo la pulizia |
| --- | --- |
| D01 | La revisione è ora esplicitamente una demo. Rimossi comandi senza azione, firmatario fisso e contatore di conferma inventato; aggiunto il collegamento al Template. Conservati URL, endpoint e dati storici. |
| D02 | Rimossi i due wrapper frontend inutilizzati. Endpoint e schema legacy conservati per compatibilità; il contratto backend resta da dismettere separatamente. |
| D03 | Tolto il contatore dei modelli dalle schede progetto. Il campo API/DB resta compatibile con i client esistenti. |
| D06–D07 | Rimossi i due helper per gli artefatti globali e il formatter dei soli fatti verificati. Adattato il test delle azioni di revisione al formatter già usato dall'app, senza modificarne il comportamento. |
| D08 | Rimossi cinque wrapper e i relativi tipi orfani. Conservato `projectEvidence`, insieme al resto del client di ricerca, per rispettare il perimetro escluso dall'intervento. |
| D09 | Rimossa la variante inline del selettore AI e i suoi stili. Le verifiche di salvataggio, errori, operazioni in corso e risposte obsolete sono state trasferite al menu effettivamente usato. |
| D10 | Accorpati `markdownFilename()` e `fragmentCountLabel()` in `frontend/src/sourceText.ts`. La gestione delle fonti nel backend resta invariata. |
| D12 | Rimossi i parametri interni inutilizzati `verified_count` e `pending_count` e aggiornati i chiamanti. I contatori dei formati pubblici sono conservati. |
| D13–D14 | Rimossi i nove gruppi di classi senza consumatori, gli stili della variante inline e del firmatario dimostrativo, e i quattro asset inutilizzati. Preservati i selettori condivisi ancora usati. |
| D15 | Riscritte README principale e frontend con avvio, verifiche e collegamenti alla documentazione del progetto. |
| D04–D05, D11, D16 | Restano aperti: compatibilità dei fatti, strategia a gruppi, separazione dei grandi moduli e dichiarazioni delle dipendenze. La pulizia non cambia questi contratti o lo stack installato. |

Verifiche dopo le modifiche: **561 test backend**, **108 test frontend**,
controllo TypeScript e lint superati. **12 scenari Playwright** su desktop e
mobile superati, con tutte le API simulate: menu AI, revisione, eliminazione
delle fonti e template testuale. Ispezionati anche gli screenshot della revisione.
La build di produzione riesce; Vite segnala il chunk JavaScript sopra 500 kB,
una voce separata di ottimizzazione rimasta aperta.

L'esecuzione browser nella sandbox fallisce all'avvio di Chromium; la verifica
conclusiva è stata eseguita fuori dalla sandbox. Le prove non hanno usato un
backend applicativo reale. I risultati dell'audit originale sono conservati
nella sezione finale per distinguere lo stato prima e dopo l'intervento.

**Valutazione: codice morto limitato, debito di manutenzione significativo ma
concentrato.** Il progetto non contiene interi sottosistemi TypeScript
abbandonati: tutti i 25 moduli applicativi TS/TSX risultano raggiungibili dagli
import di `src/main.tsx`. Restano però piccoli rami inutilizzati, contratti
obsoleti e una revisione dimostrativa che si presenta come funzione operativa.
Il costo maggiore di pulizia sta nel chiarire questi confini e separare le
responsabilità, più che nel cancellare grandi quantità di codice.

Il perimetro applicativo conta **8.320 righe Python in 29 file**, **4.537 righe
TS/TSX in 25 file** e **2.682 righe CSS in 6 file**. Sono righe fisiche, inclusi
commenti, stringhe e spazi; sono esclusi test, script, dipendenze e build.
Non sono una misura della qualità o della percentuale eliminabile.

**Come leggere la mappa**

- **Morto nel repository:** non ha chiamanti applicativi; eventuali test o
  riferimenti interni a un gruppo isolato sono indicati separatamente.
- **Compatibilità attiva:** è fuori dal percorso principale ma può ancora
  gestire dati, URL, API o prove precedenti. Richiede una scelta di dismissione.
- **Debito attivo:** viene eseguito, ma contiene duplicazioni, responsabilità
  mescolate o comportamenti incompleti.
- **P1:** chiarire comportamenti esposti; **P2:** semplificare e isolare;
  **P3:** pulizia a basso impatto. La priorità misura l'utilità dell'intervento,
  non la gravità di un incidente.

**Mappa ordinata per impatto**

| ID | Priorità / stato | Posizione | Evidenza e conseguenza | Intervento suggerito |
| --- | --- | --- | --- | --- |
| D01 | P1 · Debito attivo | `frontend/src/pages/DocumentReviewPage.tsx:73`, `:115`, `:120`; `backend/app/repository.py:1173`; `backend/app/seed.py:147` | La pagina di revisione espone **Salva** e **Inserisci valore** senza gestori. Mostra il firmatario fisso «Giulia Bianchi» e «1 campo richiede conferma» indipendentemente dai dati. Legge `document_fields`, popolata dal seed; il compilatore reale salva in `document_compilations`. | Collegare la revisione ai report reali, oppure identificarla e isolarla come demo. Rimuovere/disabilitare i comandi privi di azione. Trattare insieme pagina, endpoint, seed, schema e CSS. |
| D02 | P1 · Contratto obsoleto | `backend/app/repository.py:417`, `:462`; `backend/app/main.py:341`; `backend/app/db.py:219`; `frontend/src/api.ts:191` | L'API di collegamento delle KB globali restituisce sempre `linked=true`. `set_project_global_document_link()` ignora il parametro `linked`; la tabella `project_global_document_links` non è letta/scritta dal percorso applicativo, oltre alla creazione dello schema. I test ne controllano il conteggio nullo. | Deprecare esplicitamente il contratto, poi eliminare client e handler superflui. L'eventuale rimozione della tabella va gestita come migrazione, verificando prima i consumatori esterni. |
| D03 | P1 · Dato esposto ma non mantenuto | `backend/app/repository.py:244`, `:796`; `backend/app/seed.py:66`; `frontend/src/pages/ProjectsPage.tsx:100` | `model_count` viene inizializzato nel seed o a zero nella creazione del progetto e mostrato nelle schede. Non risultano aggiornamenti applicativi del contatore quando si configurano template o si salvano compilazioni. | Definire che cosa rappresenta «modelli» e calcolarlo dalla fonte corretta, oppure togliere il contatore dal contratto e dalla UI. Non è una variabile inutilizzata: il valore obsoleto arriva all'utente. |
| D04 | P2 · Compatibilità attiva senza UI | `backend/app/main.py:423`, `:478`, `:489`; `backend/app/call_facts.py`; `backend/app/artifacts.py:15`; `backend/docs/dati-progetto.md:3` | Estrazione e revisione dei fatti non sono più accessibili dalla UI. Restano endpoint, quattro artefatti iniziali per progetto, indicizzazione e metriche. I fatti già salvati possono ancora alimentare chat e compilazione. | Separare questa compatibilità dal flusso principale e documentarne la durata. Non cancellare `call_facts.py`, `fact_extraction.py` o gli artefatti come se fossero morti. |
| D05 | P2 · Strategia sperimentale conservata | `backend/app/document_compilation.py:630`, `:830` | `compile_field_batches()` occupa **198 righe** e contiene richieste a gruppi, correzioni e gestione dei retry. L'API usa la chiamata unica; `strategy="batches"` resta invocabile in Python ed è esercitata da numerosi test di confronto. | Se il confronto serve alla tesi, spostare la strategia in un modulo dedicato mantenendo i controlli condivisi. Se non serve più, ritirarla insieme ai test specifici. Non è codice irraggiungibile. |
| D06 | P2 · Gruppo morto | `backend/app/artifacts.py:502`, `:522` | `update_global_artifact()` non ha chiamanti in app, script o test; `get_global_artifact()` è chiamata solo da quella funzione. **56 righe di funzioni** rimaste dalla gestione degli artefatti globali. All'avvio viene invece eseguita la rimozione dei vecchi artefatti globali (`:331`). | Eliminare la coppia. Conservare separatamente la migrazione che rimuove i dati legacy. |
| D07 | P2 · Helper vivo solo nei test | `backend/app/call_facts.py:303`; `backend/tests/test_call_facts.py:52`, `:65` | `verified_call_facts_markdown()` non ha chiamanti applicativi o negli script. L'indicizzazione usa `available_project_facts_markdown()` (`:316`), che riflette la semantica corrente. | Rimuovere l'helper di 11 righe dopo aver conservato nei test del percorso corrente le verifiche ancora pertinenti. I suoi test non dimostrano un utilizzo applicativo. |
| D08 | P2 · Client inutilizzato | `frontend/src/api.ts:191`, `:196`, `:216`, `:220`, `:222`, `:252` | Sei metodi del client non hanno chiamanti nella UI: elenco sotto. Uno è ancora presente nei mock e nelle asserzioni che verificano che non venga chiamato. | Eliminare i wrapper inutilizzati e i tipi che diventano orfani. Valutare separatamente gli endpoint backend, pubblici e ancora testati/documentati. |
| D09 | P2 · Ramo vivo solo nei test | `frontend/src/components/ProjectModelSelector.tsx:9`, `:153`; `frontend/src/pages/ProjectWorkspacePage.tsx:343` | L'unico utilizzo applicativo passa `variant="menu"`. La variante predefinita `inline` e i suoi stili sono esercitati solo dai test in `AiSettings.test.tsx`. | Semplificare il componente al menu corrente. Spostare sul menu le verifiche condivise prima di togliere i test della variante inline. |
| D10 | P2 · Duplicazione attiva | `frontend/src/pages/CompanyKnowledgePage.tsx:36`; `frontend/src/components/ProjectKnowledgePanel.tsx:23`; `backend/app/main.py:274`, `:823` | Le due UI duplicano `markdownFilename()` e `fragmentCountLabel()`, oltre a parti della gestione degli editor. I due endpoint di modifica delle fonti duplicano controlli MIME, chunking, scrittura temporanea, sostituzione e ripristino del file in caso d'errore. | Estrarre prima gli helper e l'operazione comune di aggiornamento delle fonti. Conservare esplicite le differenze di scope globale/progetto. |
| D11 | P2 · Responsabilità concentrate | `backend/app/repository.py`, `backend/app/main.py`, `backend/app/document_compilation.py`; grandi componenti frontend elencati sotto | CRUD, ricerca, metriche e conversazioni convivono nel repository; molte route e logica applicativa nel main; prompt, validazione e strategie nel compilatore. Nel frontend stato, richieste, eventi e rendering convivono in componenti di centinaia di righe. | Suddividere per responsabilità e lavorare sui flussi che cambiano più spesso, usando le suite esistenti. Le dimensioni da sole non giustificano riscritture. |
| D12 | P3 · Parametri residui | `backend/app/repository.py:1023` | `update_call_fact_review_metrics()` riceve `verified_count` e `pending_count` ma non li usa. Sono ancora calcolati e passati dai chiamanti. | Rimuovere questi parametri dalla funzione interna e aggiornare i chiamanti. Non eliminare i contatori dai formati pubblici senza valutarne la compatibilità. |
| D13 | P3 · CSS senza consumatori | `frontend/src/App.css`, selettori elencati sotto | Nove nomi di classe non risultano emessi dalla UI corrente, inclusi vecchi controlli e footer degli artefatti. | Rimuovere regole e parti di selettori inutilizzate, preservando gli eventuali selettori condivisi. Verificare il risultato visivamente quando si modifica il CSS. |
| D14 | P3 · Asset inutilizzati | `frontend/src/assets/react.svg`, `vite.svg`, `hero.png`; `frontend/public/icons.svg` | Nessun riferimento in codice, HTML o CSS. Totale **30.923 byte**, circa 30,2 KiB. | Eliminabili dal repository. Non equivale a risparmiare tutto quel peso nel bundle: gli asset non importati in `src` non sono automaticamente inclusi; `public` ha un trattamento diverso. |
| D15 | P3 · Documentazione iniziale residua | `README.md:1`; `frontend/README.md:1` | La README principale contiene solo il titolo; quella frontend descrive ancora il template React/Vite. Le istruzioni effettive sono distribuite altrove. | Scrivere un ingresso breve con avvio, test e collegamenti ai documenti correnti. Conservare i resoconti storici della tesi con la loro data/versione. |
| D16 | P3 · Dipendenze implicite | `backend/pyproject.toml`; `backend/app/docx_templates.py:16`; `backend/app/schemas.py:5`; `backend/app/main.py:11` | L'app importa direttamente `lxml`, `pydantic` e `starlette`, ma il progetto non li dichiara direttamente: sono disponibili attraverso altre dipendenze. | Dichiarare le dipendenze dirette necessarie con vincoli coerenti. È debito di dichiarazione, non un errore d'installazione riprodotto. |

**Dettaglio del client inutilizzato — D08**

| Metodo | Riga di `frontend/src/api.ts` | Stato del backend |
| --- | ---: | --- |
| `projectGlobalKnowledge` | 191 | Endpoint legacy, tutti i documenti risultano collegati. |
| `updateProjectGlobalKnowledge` | 196 | Endpoint legacy, il flag richiesto non modifica la selezione. |
| `extractCallFacts` | 216 | Estrazione ancora disponibile via API. |
| `callFactsReview` | 220 | Revisione ancora disponibile via API; nei test frontend si verifica che non venga invocata. |
| `reviseCallFact` | 222 | Mutazione ancora disponibile via API. |
| `projectEvidence` | 252 | Ricerca ancora disponibile via API; il retrieval usato dalla chat resta attivo. |

I gruppi di tipi collegati in `frontend/src/types.ts` comprendono
`ProjectGlobalKnowledgeDocument`, `CallFactsExtractionResult`, `CallFactsReview`,
`CallFactRevision` ed `EvidenceSearch`. Vanno rivalutati dopo la rimozione dei
wrapper, seguendo anche i riferimenti tra tipi. L'assenza di import diretti di
un'interfaccia non basta a definirla morta.

**Dettaglio CSS — D13**

| Classe | Prima posizione in `frontend/src/App.css` | Osservazione |
| --- | ---: | --- |
| `.activity-dot--idle` | 519 | La logica corrente usa altre varianti o la classe base. |
| `.artifact-metadata` | 1226 | Nessun elemento corrente la emette. |
| `.artifact-editor-footer` | 1265 | Anche regole discendenti e variante responsive. |
| `.artifact-actions` | 1296 | Anche variante responsive. |
| `.artifact-extract` | 1302 | Condivide blocchi con `.artifact-generate`, che è ancora usata. |
| `.value-control` | 1313 | Vecchio controllo senza consumatori. |
| `.settings-actions` | 1325 | Nessun elemento corrente la emette. |
| `.company-kb-section` | 1416 | Anche regole discendenti e responsive. |
| `.toggle` | 1506 | Comprende `:disabled`, `span` e `.is-on`. |

A questi si aggiungono gli stili `.project-ai-control` / `.project-ai-row` in
`frontend/src/components/AiSettings.css:20`, `:39` e `:69`, se si ritira la
variante inline di D09. Non sono conteggiati nei nove nomi sopra.

Sono state escluse dai falsi positivi le classi composte dinamicamente, per
esempio `status-pill--${tone}` e `source-dot--${tone}`. Questa è una mappa
statica dei consumatori, non una misura di copertura CSS nel browser.

**Concentrazioni da affrontare — D11**

| File | Righe | Confine di separazione utile |
| --- | ---: | --- |
| `backend/app/repository.py` | 1.193 | Progetti/fonti, conversazioni, ricerca lessicale e metriche. Il nome attuale nasconde logica di ricerca e di presentazione oltre alla persistenza. |
| `backend/app/document_compilation.py` | 899 | Prompt e contratto del modello, validazione, orchestrazione a chiamata unica, strategia di confronto a gruppi. |
| `backend/app/main.py` | 874 | Router progetti/fonti, artefatti/fatti, conversazioni. Le route AI, retrieval e DOCX sono già separate e offrono un precedente. |
| `backend/app/docx_templates.py` | 616 | Ispezione ZIP/XML, riconoscimento degli slot e scrittura. Separare con cautela: condividono invarianti sul documento. |
| `frontend/src/pages/ProjectWorkspacePage.tsx` | 579 | Caricamento conversazioni, invio e stato della chat, compositore, pannelli. |
| `frontend/src/components/ProjectKnowledgePanel.tsx` | 448 | Operazioni sulle fonti, editor testuale, conferma eliminazione e rendering. |
| `frontend/src/pages/CompanyKnowledgePage.tsx` | 404 | Gestione delle fonti globali ed editor, in parte duplicati con il pannello di progetto. |
| `frontend/src/components/DocxTemplateWorkspace.tsx` | 382 | Caricamento modello, generazione, storico, dettaglio report e download. |
| `frontend/src/App.css` | 2.187 | Circa l'82% del CSS applicativo: spostare gli stili specifici nelle rispettive funzionalità, dopo aver tolto quelli orfani. |

Un'ulteriore duplicazione, di priorità inferiore, è la rimozione dei blocchi
Markdown e il parsing JSON nelle risposte AI: `generation.py:89`,
`fact_extraction.py:167`, `draft_generation.py:73`,
`document_compilation.py:440`. Si può condividere la normalizzazione di base;
messaggi d'errore, diagnostica e validazione di dominio hanno differenze utili
e non vanno uniformati meccanicamente.

**Cosa conservare e perché**

- La compilazione Markdown è ancora selezionabile in
  `frontend/src/components/TemplateWorkspace.tsx:38`: `draft_generation.py`
  non è sostituito integralmente dal flusso DOCX.
- La pagina `/demo/candidatura` è una demo esplicita, con esportazione propria
  e test. La sua indipendenza dal backend non la rende morta. È distinta
  dalla pagina `/projects/:projectId/review` di D01, ancora raggiungibile dalla
  conversazione dimostrativa (`ProjectWorkspacePage.tsx:415`).
- Le migrazioni dei template, dei profili AI e degli indici riconoscono dati
  precedenti. Non rimuoverle in base al solo termine `legacy`.
- I due argomenti `run_manager` non usati nei retriever sono parte della firma
  LangChain, non residui equivalenti al parametro `linked`.
- I validator Pydantic, i callback dei framework e le route registrate tramite
  decoratori possono essere eseguiti senza chiamate testuali esplicite.
- Gli script sotto `backend/scripts` sono entry point autonomi; i documenti
  sotto `demo-documents` includono fixture usate dai test. I DOCX nella radice
  sono artefatti da catalogare, non codice morto dimostrato.
- Non emerge una dipendenza dichiarata certamente inutile da eliminare sulla
  sola base degli import; alcune supportano i framework e le integrazioni.

**Sequenza di pulizia proposta**

1. Risolvere i comportamenti esposti di **D01–D03**: revisione, collegamenti
   globali e contatore dei modelli. Qui si elimina ambiguità per l'utente.
2. Togliere **D06–D09, D12–D14**, aggiornando test e tipi interessati. È la
   parte più circoscritta e verificabile della pulizia.
3. Isolare **D04–D05** come compatibilità o sperimentazione, con una decisione
   esplicita sul loro mantenimento. Evitare cancellazioni implicite di dati.
4. Ridurre **D10–D11** per funzionalità, conservando gli invarianti coperti dai
   test. Completare README e dichiarazioni delle dipendenze.

**Verifiche dell'audit iniziale e limiti**

| Verifica | Esito |
| --- | --- |
| `backend/.venv/bin/ruff check backend --output-format concise` | Passa. |
| Ruff aggiuntivo con `--select ARG001,ARG002` su `backend/app` | Cinque segnalazioni: `linked`, `verified_count`, `pending_count` e due `run_manager`. Le ultime due sono firme di framework. Queste regole non sono abilitate nel lint ordinario. |
| `../.tools/node/bin/node node_modules/oxlint/bin/oxlint`, da `frontend` | Passa. |
| `../.tools/node/bin/node node_modules/typescript/bin/tsc -b --pretty false`, da `frontend` | Passa. |
| `.venv/bin/python -m pytest -q`, da `backend` | **561 test superati**, 24,78 secondi nell'esecuzione conclusiva. |
| `../.tools/node/bin/node node_modules/vitest/vitest.mjs run`, da `frontend` | **108 test superati**, 14 file. |

La suite backend nella sandbox si è bloccata al primo test asincrono; la
diagnostica mostrava AnyIO/event loop in attesa. L'esecuzione autorizzata fuori
dalla sandbox ha completato la suite. Il blocco non è stato classificato come
difetto applicativo.

Sono stati esaminati import, definizioni AST Python, riferimenti in app/test/
script, chiamanti dei metodi API, classi CSS, schema e flussi di scrittura.
Non sono state eseguite prove E2E, chiamate live a modelli AI, misure di
copertura o profilazione. Non sono stati interrogati database applicativi né
modificati i dati dell'utente. Per gli endpoint pubblici non si può escludere
la presenza di client esterni al repository.

I test verdi descrivono lo stato della base esistente: non attestano che tutte
le azioni mostrate dalla UI siano implementate e non provano l'assenza di altro
codice morto. La mappa distingue appositamente i casi confermati dalle decisioni
di compatibilità e dalle opportunità di refactoring.
