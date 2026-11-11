# Compilazione DOCX per sezioni come sistema predefinito (24 ottobre 2026)

**Decisione dell'utente:** la compilazione DOCX per sezioni diventa il sistema ordinario
dell'applicazione. Un solo percorso, chiamato nell'interfaccia «Compilazione DOCX», senza
selettori, variabili d'ambiente o etichette sperimentali. La compilazione monolitica resta nel
codice e in Git per le sessioni storiche e per un rollback di emergenza, ma non è offerta.

Il DOCX prodotto resta una **bozza da verificare** da una persona. Le verifiche qui elencate
sono deterministiche o con provider simulati: non dimostrano un'accuratezza semantica, che resta
misurata solo dalle campagne E2E già registrate (`docs/campagna-e2e-incrementale-2026-10-24.md`).

**Branch:** `integrazione/2026-10-24-compilazione-sezioni`, worktree
`/home/montesano/tesi-integrazione-sezioni`, base `670e69c` (candidata incrementale con il
rapporto della campagna). Nessun merge in `main`.

## Profilo canonico

Definito in un solo punto, `backend/app/compilation_profile.py` (`SECTIONS`, nome
`sezioni-2026-10-24`). `initial_state` lo scrive in ogni **nuova** sessione globale, insieme a
`compilation_profile`. Le sessioni esistenti conservano i flag con cui sono state create: nessun
aggiornamento a runtime, nessuna migrazione.

| Flag | Valore | Controllo |
|---|---|---|
| `backend_revision` | 13 | contratto del backend globale |
| `option_authorization_revision` | 1 | V14: assenso alle clausole d'opzione prestampate |
| `attribution_safety_revision` | 1 | K3: soggetto, ruolo e organizzazione |
| `derivation_revision` | 1 | stato derivato coerente dopo le risposte USER |
| `dialogue_revision` | 1 | dialogo P3 e guardia semantica delle risposte |
| `generation_revision` | 3 | sezioni con FORM completo, destinazioni di competenza, validazione per segmento, retry e cache, ricevute d'ambito e rivalidazione finale |
| `narration_recovery_revision` | 1 | un solo nuovo tentativo del narratore, poi sintesi degradata |
| `branch_scope_revision` | 1 | R1: condizioni d'opzione estese alla continuazione |
| `table_scope_revision` | 1 | sezioni tabellari condizionali solo con applicabilità |
| `hold_rereview_revision` | 2 | un riesame delle sospensioni mal attribuite o di ruolo SOURCE |

**Dipendenze verificate** (`test_every_control_of_the_profile_is_actually_enabled_by_these_flags`):
- `compilation_scope_review.enabled`: generazione 3;
- R1 e tabelle: generazione 3 più il rispettivo flag;
- riesame: generazione 3 e revisione 1 o 2; il riesame SOURCE richiede la 2;
- recupero del narratore: limite di due tentativi;
- il riesame usa il pool di domande P3, quindi `dialogue_revision` 1.

Il veto API generale della bozza esplicita (`4554ae1`) non dipende da flag: vale per ogni
sessione.

**Ambiente obsoleto:** senza l'interruttore di emergenza, le vecchie variabili
`MAPI_*_REVISION` sono ignorate. Un `.env` rimasto da una campagna non può quindi produrre
combinazioni parziali.

**Interruttore di emergenza** `MAPI_COMPILATION_PROFILE=storico`, solo lato server: le nuove
sessioni seguono le regole di creazione precedenti al 24 ottobre, invariate (monolitica in
assenza di variabili). Non è un'opzione dell'utente e non compare nell'interfaccia.

## Interfaccia

Stati letti dalla sessione, senza percentuali (`frontend/src/compilationStatus.ts`):

- **Durante l'elaborazione:**
  - «Avvio della Compilazione DOCX…»;
  - «Analisi del documento e compilazione delle sezioni…», solo per le sessioni rev 3;
    «Analisi del documento…» per le altre;
  - «Verifica dei dati…»;
  - «Preparazione del DOCX…».
- **Sotto la risposta:**
  - «Compilazione DOCX · attesa di chiarimenti»;
  - «… · verifica dei dati completata»;
  - «… · bozza completata» o «… · bozza incompleta», incompleta se un segmento non è stato
    analizzato o restano campi da verificare, sempre con la nota «Il DOCX è una bozza: va
    verificato prima dell'uso.»;
  - «… · compilazione interrotta».
- **Segmento fallito:** «Una parte del documento non è stata analizzata: i relativi campi
  restano vuoti e la compilazione è incompleta.»
- **Ripresa:** con il meccanismo esistente («Riprendi la compilazione interrotta.» nella chat).

**Lease dopo un crash.** Una compilazione interrotta resta bloccata fino alla scadenza del
lease, 25-34 minuti. Una correzione minima e sicura non c'è: il lease protegge dalle mutazioni
concorrenti con lo stesso codice usato da tutte le sessioni. L'interfaccia mostra quindi
l'orario dal quale si potrà riprendere: «Se il servizio è stato interrotto, potrai riprendere la
compilazione dalle HH:MM: le sezioni già validate restano conservate.»

## Commit

| SHA | Responsabilità | File | Test | Dipende da | Rollback |
|---|---|---|---|---|---|
| `6d7477c` | profilo canonico per le nuove sessioni | `backend/app/compilation_profile.py` (nuovo), `compilation_global_sessions.py`, `tests/conftest.py` (nuovo), `tests/test_compilation_profile.py` (nuovo, 18 test), `tests/test_compilation_rev3_resumption.py` (variante «predefinito») | suite 3860 PASS, Ruff PASS | `670e69c` | `git revert 6d7477c` |
| `0933353` | interfaccia «Compilazione DOCX» e stati reali | `frontend/src/compilationStatus.ts` e `.test.ts` (nuovi), `CompilationReply.tsx`, `ProjectWorkspacePage.tsx`, `compilationReply.ts`, `types.ts`, `App.css`, 3 asserzioni di etichetta | vitest 152 PASS, oxlint, build | `6d7477c` per il significato delle etichette | `git revert 0933353` |
| `dc640fc` | etichetta delle sezioni solo per sessioni rev 3 | `compilationStatus.ts` e `.test.ts`, `types.ts`, mock di `e2e/global-compilation.spec.ts` | vitest 152 PASS, oxlint, build, E2E simulati 18/18 | `0933353` | `git revert dc640fc` |
| (questo) | documentazione | `README.md`, `STATUS.md`, `relazioni.md`, una nota in `AGENTS.md`, questo file | controllo di diff e riferimenti | — | `git revert` |

`tests/conftest.py` imposta `MAPI_COMPILATION_PROFILE=storico` per i test preesistenti, che
continuano a esercitare i profili espliciti con le vecchie variabili. Il nuovo predefinito è
coperto da `test_compilation_profile.py` e dalla terza variante dei test di ripresa.

## Verifiche

Grezzi in `backend/data/compilation-audit/integrazione-sezioni-20261024-01/`, esclusi da Git.

| # | Verifica | Esito | Evidenza |
|---|---|---|---|
| 1 | suite backend e Ruff | 3860 PASS, Ruff PASS: 403 s sul branch, 409 s nel working tree ordinario | `out/suite-commit-profilo.log`, `out/suite-working-tree-ordinario.log` |
| 2 | test e build frontend | vitest 152 PASS, oxlint 0, build OK (branch e working tree ordinario) | `out/frontend-working-tree-ordinario.log` |
| 3 | una nuova sessione usa tutte le revisioni | flag = `SECTIONS`, anche nel processo reale (vedi Attivazione); 3 segmenti, ognuno con tutti i blocchi del FORM e solo le proprie destinazioni; ricevute R1 e tabelle nell'audit | `test_compilation_profile.py` |
| 4 | le sessioni esistenti conservano il profilo | sessione monolitica creata prima e risolta dopo il cambio: flag invariati, analisi monolitica; 29 sessioni live con la stessa selezione d'export, domande e finestra di revisione su base e integrazione | `test_an_existing_session_keeps…`, `out/confronto-{base,integrazione}.json` |
| 5 | rigioco dei controesempi dei rami | 25 scritture storiche sbagliate: con R1 e controllo delle tabelle ne restano esportabili 13 con la guardia simulata (7 con le sole ricevute registrate); 245/245 corrette conservate con la guardia simulata; 0 nuovi falsi rifiuti | `out/p2-current-replay.json` |
| 6 | V14 e K3 | flag nel profilo e test esistenti PASS nella suite | suite |
| 7 | veto API della bozza globale | sospesi → 409, rivisti → 200 nel flusso per sezioni; 162 esportazioni storiche rivalutate, 0 rifiuti | `test_a_new_ordinary_session…`, `out/storico-bozza.json` |
| 8 | retry, cache e ripresa | 10 scenari su tre profili (sprint, incrementale, predefinito) PASS | `test_compilation_rev3_resumption.py` |
| 9 | export dei rivisti, rifiuto dei sospesi | come al punto 7 | — |
| 10 | integrità degli originali DOCX | 273 file archiviati (49 DOCX) e 29 DOCX di sessione con hash identici prima dell'avvio e dopo la verifica dal vivo | `attivazione/confronto-prima-dopo.json` |
| 11 | nessuna opzione sperimentale visibile | bundle di produzione: 0 occorrenze di «sperimental», «rev 3», «beta», «monolitic», «P3», nome del profilo, `MAPI_`, «storico»; nessun selettore | `out/bundle-etichette.txt` |

Su tutti i 90 stati confrontati, l'integrazione produce gli stessi esiti della candidata
`3ec0af0`. Rispetto alla base `dd41e2e` differiscono soltanto gli stati delle campagne rev 3,
dove la base non ha i controlli dello sprint.

**E2E simulati:** composer-model-menu, compilation-chat, global-compilation, document-review e
project-forms 18/18; compilation-continuation 4/4. `compilation-clarifications.spec.ts` fallisce
2/2 in modo identico anche sulla base: cerca `.compilation-question`, assente in ogni versione.
È un fallimento preesistente, non una regressione.

## Attivazione nel working tree ordinario

Il working tree `/home/montesano/tesi` (branch `prune-backend`, con 432 modifiche dell'utente
non committate) aveva il codice di `dd41e2e`. L'integrazione è stata applicata così:

- **Salvataggio:** i 12 file esistenti da modificare sono stati salvati in
  `rollback-working-tree/codice-prima-integrazione.tar`, con hash verificati.
- **Applicazione:** `git apply` delle due patch, ciascuna preceduta da `--check`. Nessun commit
  sul branch dell'utente e nessuna modifica fuori da `backend/` e `frontend/`.
- **Controllo:** tutti i 370 file tracciati di `backend/`, `frontend/` e `start.sh` coincidono
  con `dc640fc`.

**Verifiche nel working tree ordinario:**
- backend: 3860 PASS in 409 s, Ruff PASS;
- frontend: vitest 152 PASS, oxlint 0, build OK.

**Avvio:** `./start.sh` su 8000 e 5173.
- I processi uvicorn e vite girano da `/home/montesano/tesi/backend` e `/frontend`.
- Il proxy `/api` della 5173 raggiunge la 8000.
- Nella shell di avvio non c'è `MAPI_COMPILATION_PROFILE`.

**Profilo caricato dal processo reale** (`attivazione/verifica_processo_reale.py`, zero LLM), in
cinque passi, tutti attraverso il proxy del frontend:
1. creato un progetto temporaneo;
2. caricato il modulo della fixture benchmark (55 destinazioni);
3. creata una sessione globale **senza** analisi;
4. riletti i flag persistiti, uguali a `SECTIONS`, con `compilation_profile` «sezioni-2026-10-24»;
   la sessione è in stato `CREATED`, con 0 tentativi;
5. eliminato il progetto: 204, poi 404.

**Dati invariati** (`attivazione/confronto-prima-dopo.json`):
- 3 progetti;
- 29 sessioni con `state_json` e DOCX originale identici;
- 273 file archiviati identici.

**Interfaccia reale** (`attivazione/ui-sola-lettura.json`, `ui-select.json`, screenshot):
- **Navigazione:** in sola lettura, con ogni richiesta `/api` non GET annullata, così nessuna
  sessione può avanzare.
- **Pagine:** elenco progetti, i tre workspace e impostazioni: nessun termine sperimentale e
  nessun selettore di modalità.
- **Select presenti:** solo l'ordinamento dei progetti e le impostazioni di embedding e
  ricerca.

## Rollback di emergenza

È una possibilità tecnica, non una modalità visibile.

**Livello 1, preferito, senza toccare il codice.** Avviare il backend con
`MAPI_COMPILATION_PROFILE=storico`, per esempio `MAPI_COMPILATION_PROFILE=storico ./start.sh`,
e riavviarlo.
- Le nuove sessioni tornano alle regole precedenti: monolitica senza altre variabili.
- Le sessioni già create per sezioni conservano i loro flag e continuano con tutti i controlli,
  perché il codice resta.
- Il veto API resta attivo.
- Per tornare al profilo per sezioni basta togliere la variabile e riavviare.
- Verificato da `test_the_historical_switch_reproduces_the_previous_creation_rules`.

**Livello 2, revert del codice sul branch:** `git revert dc640fc 0933353 6d7477c`.
- Verificato sul worktree `/home/montesano/tesi-integrazione-rollback`, branch
  `verifica-rollback/2026-10-24-integrazione-3`: codice di `backend/`, `frontend/` e `start.sh`
  identico a `670e69c`.
- Test sull'albero ripristinato: 105 test backend mirati (sessioni globali, ripresa, veto API,
  tabelle) e 147 test frontend PASS (`out/rollback-tre-commit.log`).

**Working tree ordinario.** Prima dell'integrazione c'erano 12 file esistenti, salvati in
`rollback-working-tree/codice-prima-integrazione.tar` con `SHA256SUMS`, e 14 file nuovi,
elencati in `file-nuovi.txt`. Le patch sono in `PATCH-SHA256SUMS`:
- `integrazione.patch`;
- `integrazione-2-etichetta.patch`;
- `integrazione-completa.patch`, cioè `dd41e2e`→`dc640fc`.

Ripristino in un passo, dalla radice, a servizi fermi:

```bash
git apply -R backend/data/compilation-audit/integrazione-sezioni-20261024-01/rollback-working-tree/integrazione-completa.patch
```

Il controllo a secco `git apply -R --check` della patch completa riesce sullo stato attivato. In
alternativa: estrarre il tar e rimuovere i 14 file nuovi.

**Attenzione:** il codice precedente del working tree ordinario (`dd41e2e`) non contiene R1, il
controllo delle tabelle, il riesame rev 2 né il veto API. Le sessioni create nel frattempo per
sezioni proseguirebbero quindi senza quei controlli, cioè con una combinazione parziale, e il
fix di sicurezza sparirebbe. Per questo il livello 2 nel working tree ordinario va usato solo
se il livello 1 non basta, e dopo aver chiuso o archiviato quelle sessioni.

## Limiti

- **Controesempi:** 13 dei 25 errori storici dei rami non sono bloccati deterministicamente.
  Dal vivo dipendono dalla revisione del modello e dalle domande.
- **Riesame e tabelle:** l'efficacia è dimostrata solo offline. Nella campagna E2E nessun
  recupero e nessun veto sono stati esercitati.
- **Costo:** la generazione per sezioni costa da 1,8 a 4,1 volte i token della monolitica.
- **Copertura:** nessun lavoro su Catanzaro e So.Re.Sa. in questa integrazione.
  - So.Re.Sa. conserva le sospensioni non fondate sulla partecipazione singola.
- **Lease:** attesa del lease dopo un crash.
- **E2E:** `compilation-clarifications.spec.ts` resta da aggiornare.
- **Garanzie:** nessuna infallibilità semantica. Citazioni valide e stato completato non
  provano che il contenuto sia pertinente.
