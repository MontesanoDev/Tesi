# Ripresa di Mapi RAG sull'altro PC



## Stato Git da cui ripartire

Al controllo sul PC di origine:

- repository principale: /home/montesano/Tesi;
- branch: prune-backend, HEAD 26976fa, allineato al riferimento locale
  origin/prune-backend;
- ultimo commit: 26976fa, feat: select project sources and forms in chat;
- precedenti: b543fd7, f315d52, f677aff, 1d7f868;
- baseline demo: tag locale demo-baseline-20261010, commit 1d7f868;
- checkpoint pre-potatura: 2510418.

**Selezione multipla e correzione dello scroll erano ancora NON committate
e NON pushate.** Il solo clone di GitHub al commit 26976fa non le recupera.
Non confondere “implementato sul PC di origine” con “disponibile su GitHub”.

Prima di lasciare il PC di origine, per conservare queste modifiche tramite
GitHub occorre consolidarle in un commit e pusharle su prune-backend.
Questo documento non esegue commit o push. Se non vengono pubblicate né
copiate, la nuova chat dovrà ricostruire il task descritto sotto.

Esiste anche /home/montesano/Tesi-one-shot, worktree sul branch
feat/compilation-one-shot, HEAD 1d7f868, con prototipo a chiamata unica e
modifiche/file non tracciati. Anche quel working tree non è recuperabile
integralmente da GitHub senza copiarlo o pubblicarne lo stato.
Le ultime modifiche alla selezione multipla e allo scroll NON erano state
allineate in questa worktree. Non usarla come versione più aggiornata della UI.

## Ripristinare il progetto da GitHub

Se il repository manca, usare il suo URL GitHub reale:

```bash
git clone --branch prune-backend <URL_GITHUB_DEL_REPOSITORY> ~/Tesi
cd ~/Tesi
git status --short --branch
git log -6 --oneline
```

Se il repository esiste già, controllare prima branch e modifiche locali.
Non eseguire reset, clean o checkout che scartino il lavoro presente.
Fare fetch e aggiornare il branch solo dopo aver verificato lo stato locale.
Non presumere che main contenga gli ultimi interventi: il branch usato era
prune-backend. Verificare quali commit sono realmente arrivati sul remoto.

Per l'avvio, dalla radice:

```bash
./start.sh
```

start.sh prepara le dipendenze Node/Python con i lockfile, usando anche gli
strumenti locali in .tools se necessario. Serve Internet al primo avvio.
Frontend: http://localhost:5173. Backend/OpenAPI: http://localhost:8000/docs.

Ollama e BGE-M3 si installano separatamente se si vuole usare il retrieval
vettoriale. Provider chat e provider embedding hanno configurazioni distinte.
Le chiavi AI si configurano dalla UI. Non leggere o stampare credenziali
nei messaggi o nei documenti di passaggio.

## Dati che GitHub non contiene

Un nuovo clone non contiene i progetti caricati, le conversazioni Mapi,
gli originali, le bozze e i profili AI locali.

Per ritrovare questi dati, dal PC di origine conservare almeno, come insieme:

- backend/data/mapi.db e gli eventuali file SQLite -wal / -shm;
- backend/data/mapi.ai-key, necessaria alle chiavi AI cifrate nel database;
- backend/data/uploads/;
- backend/data/knowledge/;
- backend/data/mapi.db.qdrant/ se si vuole conservare l'indice locale.

Fermare il backend prima della copia, oppure acquisire il database con la API
SQLite backup; evitare una copia incoerente di un database in scrittura.
Ripristinare in un ambiente nuovo, senza sovrascrivere un database già usato
sull'altro PC. All'avvio il backend applica le migrazioni additive necessarie.
Verificare progetti, documenti, conversazioni e funzionamento dei download.

Sul PC di origine il database principale pesava circa 163 MiB, gli upload
9 MiB e Qdrant 1,6 MiB. Circa 3,3 GiB erano in compilation-audit:
sono acquisizioni e report degli esperimenti, separati dai dati di utilizzo.
Non sono necessari per ritrovare la chat Mapi corrente; trasferirli soltanto
se servono i vecchi benchmark. Non cancellarli automaticamente.
Anche il database della worktree sperimentale è separato.

Per il lavoro sul codice si può partire anche senza i dati personali locali,
usando fixture demo e database temporanei; non ricreare silenziosamente
i progetti originali fingendo di averli ripristinati.

## Funzionalità già consolidate nel commit 26976fa

- Compilazione integrata nelle normali risposte di Mapi: niente pannello nero
  separato, contatori dei candidate o dettagli tecnici nel flusso utente.
- Storico delle risposte preservato durante avanzamento/risposte/stop.
- Routing semantico condiviso per chat e compilazione, tramite TurnPlan:
  una spiegazione come “spiegati meglio” deve conservare la domanda attiva
  e spiegare, senza registrare il testo come dato del campo.
- Menu unico @ / + per fonti/bandi e moduli, inizialmente a selezione singola,
  con ruoli distinti e riferimenti persistiti.
- Una fonte selezionata limita retrieval FTS5/Qdrant, vicini e rilettura.
  Consultare il bando non deve avviare la compilazione.
- Thinking opzionale per progetto, anche con modello predefinito ereditato.
  L'ambito implementato era la risposta finale RAG, non tutte le fasi interne.
- Download dell'originale rimosso dalla lista moduli; download della bozza
  mantenuto nella risposta della chat.
- Font della chat aumentato di 1 px.

Queste sono funzionalità da preservare, non task da ricominciare.

## Task interrotto: selezione multipla dei file

Richiesta: poter selezionare quanti documenti servono tramite @ / +.
Se si chiede “compila questo bando” selezionando PDF di gara e un modulo DOCX,
procedere sul modulo e spiegare nella risposta che i PDF restano riferimenti.

Non introdurre comandi ridondanti “Analizza bando” o “Report”.
Per ora una sola compilazione per originale/sessione, senza coda automatica
di tanti moduli. Più DOCX ambigui richiedono di identificare l'originale.

Implementazione presente nel working tree di origine:

- contratti canonici document_ids e document_references, mantenendo document_id,
  document_reference e form_id per compatibilità;
- selezione multipla persistita, chip rimovibili e ripristino dopo ricarica;
- [] significa selezione esplicitamente vuota, senza ricadere sul vecchio
  riferimento singolo; NULL conserva la compatibilità;
- controllo di appartenenza al progetto e ruolo di tutti gli ID prima
  di creare conversazioni o chiamare AI;
- target semantico documents per consultare insieme FORM e SOURCE conservando
  i ruoli; target mixed resta il confronto requisiti/fatti;
- filtri multipli coerenti su FTS5, Qdrant, espansione dei vicini e rilettura;
  una selezione esplicita non include file estranei o KB globali;
- un solo DOCX compilabile fra PDF/TXT può partire; più DOCX richiedono un target
  identificato dal planner; nessun modulo alternativo avviato implicitamente;
- la risposta iniziale nomina il modulo e i documenti lasciati come riferimenti;
  quel messaggio deve restare visibile anche quando compare una domanda;
- la risoluzione dei dati aziendali della compilazione mantiene il retrieval
  preesistente: non è stata aggiunta la lettura integrale dei PDF selezionati
  né imposto un filtro che escluda tutta la conoscenza aziendale.

Migrazione additiva nel working tree:
conversations.selected_document_ids_json e
conversation_turns.document_references_json.
Entrambe erano già presenti nel database locale principale, verificate in
sola lettura. Nessuna reindicizzazione richiesta per questi cambiamenti.

File principali coinvolti:

- backend/app/schemas.py, db.py, repository.py;
- backend/app/main.py, intents.py, retrieval.py, vector_retrieval.py;
- backend/app/compilation_sessions.py;
- frontend/src/types.ts, api.ts, compilationReply.ts;
- frontend/src/pages/ProjectWorkspacePage.tsx;
- frontend/src/components/ChatComposer.css;
- backend/tests/test_document_mentions.py;
- frontend/src/api.test.ts;
- frontend/src/pages/ProjectWorkspaceCompilation.test.tsx;
- frontend/e2e/document-mentions.spec.ts e compilation-chat.spec.ts;
- AGENTS.md, README.md, docs/mappa-progetto.md,
  docs/compilation-session-v1.md e STATUS.md.

## Ultima correzione richiesta: niente scroll della pagina chat

L'utente ha mostrato screenshot con la scrollbar esterna della pagina.
Richiesta: la conversazione deve occupare la viewport, con composer visibile.
La cronologia deve continuare a scorrere internamente.

Implementazione presente nel working tree di origine:

- AppShell accetta una classe specifica del layout chat;
- shell/contenuto della conversazione limitati a 100dvh, min-height: 0 e
  overflow nascosto sulla pagina;
- rimossa l'altezza minima di 620 px che produceva overflow;
- cronologia e pannello documenti con scroll proprio;
- sui dispositivi stretti il contesto documentale è richiudibile;
- il layout delle altre pagine e del workspace iniziale resta quello esistente.

File: frontend/src/App.css, components/AppShell.tsx,
pages/ProjectWorkspacePage.tsx e scenario E2E document-mentions.spec.ts.

Provato su desktop 1440 px e mobile 412 px, anche con viewport alte 700 px.
Verificare che l'altezza globale non superi la viewport, window.scrollY resti
zero, la cronologia scorra e il composer sia raggiungibile.

## Verifiche già eseguite sul PC di origine

Questi sono risultati precedenti, non test appena eseguiti sul nuovo PC.

- Backend: 88 test mention/routing/chat passati; poi 188 test
  mention/retrieval/chat passati; infine 172 test
  compilation_conversation/controls/active_question passati.
  I primi due blocchi hanno casi sovrapposti. Ruff completo passato.
- Frontend: run completo con 99 passati e 1 fallito per indici del mock API.
  Corretto quel test, poi 7 test API passati. Suite completa aggiornata
  NON ancora rieseguita in un unico run. Lint e build finali passati.
- E2E desktop/mobile con API simulate: 9/10 passati al primo run.
  Il caso mobile rimanente anticipava lo scroll iniziale animato.
  Corretto il sincronismo del test; entrambi i casi layout ripetuti e passati.
  Non c'è ancora un unico run finale con tutti gli E2E aggiornati.
- Nessun nuovo benchmark AI reale completato per la selezione multipla.
  Il tentativo saltò le chiamate perché il default di ambiente non era
  il profilo DeepSeek configurato nel progetto. Nessuna chiamata a pagamento
  eseguita in questo intervento.

Non presentare test con provider simulati come prova di qualità del modello.

## Cosa deve fare la nuova chat

1. Verificare il repository realmente disponibile e gli eventuali dati copiati.
   Confrontare HEAD/diff con questo documento: capire se multipla e scroll
   sono arrivati tramite un commit successivo a 26976fa.
2. Se presenti, revisionare e completare le modifiche esistenti.
   Se mancanti perché mai trasferite, ricostruirle nei file indicati, preservando
   le funzionalità già consolidate. Evitare di duplicare un'implementazione
   che sia già nel repository.
3. Finire la revisione del diff e provare manualmente: selezione di due PDF
   e un DOCX, consultazione congiunta, avvio del solo DOCX, domanda attiva,
   “spiegati meglio”, stop, ripresa, cambio selezione, ricarica e download.
4. Rieseguire la suite frontend completa; lint/build e gli E2E mirati.
   Backend: controlli proporzionati alle modifiche. Sul PC di origine la suite
   completa in un unico processo esauriva la memoria: usare blocchi separati.
5. Aggiornare STATUS con verifiche effettive, limiti e prossimo punto.
   Non eseguire commit o push senza istruzioni dell'utente applicabili.
   L'utente preferisce fare personalmente il push.
6. L'eventuale allineamento del prototipo one-shot e la valutazione semantica
   con modello reale sono passi distinti, ancora da completare.

Comandi di verifica, nelle rispettive directory:

```bash
# frontend/
npm test
npm run lint
npm run build
npx playwright test e2e/document-mentions.spec.ts e2e/compilation-chat.spec.ts

# backend/
uv run --locked ruff check .
uv run --locked pytest -q tests/test_document_mentions.py tests/test_unified_routing.py tests/test_compilation_chat.py
uv run --locked pytest -q tests/test_form_retrieval.py tests/test_vector_retrieval.py tests/test_retrieval.py tests/test_chat_flow.py
uv run --locked pytest -q tests/test_compilation_conversation.py tests/test_compilation_controls.py tests/test_compilation_active_question.py
```

Per gli E2E serve Vite avviato e Chromium installato. I due scenari indicati
usano API simulate. Sul PC di origine si usavano Node in .tools/node/bin e
le librerie Chromium in .tools/playwright-libs/usr/lib/x86_64-linux-gnu.
Sul nuovo PC verificare gli strumenti effettivi, senza presumere che esistano.

## Vincoli e direzione del progetto

Conservare la base dimostrabile e le modifiche dell'utente. Nessun reset
distruttivo, nessuna riscrittura generale fuori dal task corrente.
Mantenere isolati progetti, originali e fonti: un modulo prestampato non prova
i dati o i requisiti dell'azienda. Le risposte utente restano distinte dai dati
verificati nelle fonti.

L'utente vuole semplificazione del backend, routing semantico e nessun
hardcoding di nomi di bandi o frasi. Non reintrodurre il vecchio motore a gruppi.
La compilazione attiva rimane la V1 iterativa persistente; il prototipo a chiamata
unica non è diventato il motore attuale. Non avviare automaticamente un nuovo
rifacimento dell'architettura per questa ripresa.
