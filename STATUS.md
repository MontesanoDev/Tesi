# Stato di Mapi RAG

## Checkbox testuali integrate nell'app ordinaria — 27 ottobre 2026

Profilo predefinito sempre `sezioni-2026-10-25`, ora con `text_checkbox_revision=1`
nelle nuove sessioni. Sezioni e protezioni FORM preservate, nessun cambio ai prompt,
al narratore o al retrieval. Sessioni precedenti non aggiornate.

- Branch `integrazione/2026-10-26-checkbox-testuali`: UI `e47b817`, supporto
  checkbox `f5f6bd5`, attivazione `59a2dcd`. Port selettivo da base pubblica;
  snapshot privati esclusi dalla cronologia nuova.
- Backend 3940 PASS prima / 3989 PASS dopo, Ruff PASS; frontend 154 PASS,
  lint/build PASS. Replay 0/25 errori, 243/245 positivi con guardia simulata.
- Worker reale: 4 prove API su dati temporanei, `[X]` e `[]` nei DOCX/PDF;
  nessuna connessione esterna. App raggiungibile su 5173 e 8000.
- 29 sessioni e 273 uploads invariati. All'avvio una routine preesistente ha
  rigenerato 82 ID di frammenti degli artefatti: riprodotto su base, ripristinati
  i soli ID/timestamp. Nessuna perdita di dati; differenze fisiche FTS dichiarate.
- Rollback selettivi verificati, backup aggiornati anche su D.
- [Rapporto, limiti e procedure](docs/integrazione-checkbox-testuali-2026-10-27.md).

Intervento concluso: non avviare ulteriori campagne o sprint automaticamente.

## Protezione dei rami FORM adottata nell'app e prova E2E reale — 25 ottobre 2026

**Punto di ripresa: fermarsi.** Decisione dell'utente («fai tutti e 3»). Rapporto:
`docs/rami-e2e-2026-10-25.md`.

- **Adozione `a152d7f`:** le nuove sessioni nascono con il profilo `sezioni-2026-10-25`, cioè
  `sezioni-2026-10-24` più `form_option_scope_revision 2`.
  - Le sessioni esistenti sono invariate.
  - Emergenza lato server: `MAPI_COMPILATION_PROFILE=sezioni-2026-10-24` oppure `storico`.
  - Suite 3940 PASS, Ruff PASS.
- **App ordinaria:**
  - patch nel working tree, 373 file uguali ad `a152d7f`, suite 3940 PASS;
  - riavvio con `./start.sh`;
  - profilo del processo reale `sezioni-2026-10-25`, verificato senza LLM;
  - 29 sessioni e 273 file identici.
- **Push:** `origin/miglioramenti/2026-10-25-ambiti-form`; `main` remoto invariato.
- **Prova reale**, 2 tentativi in runtime isolati, 247.443 token su 750.000, circa 0,043 USD:
  - **So.Re.Sa.:** DOCX, 7 scritture DIMOSTRATA, nucleo v3 7/15; dati del concorrente scritti;
    4 proposte nelle schede RT non scritte (veto concorrente, non determinante).
  - **Sintetico:** DOCX, 8/8 attese corrette; trappola della scheda singola vuota; nessun falso
    rifiuto.
- **Limiti:**
  - n = 2, revisione non indipendente;
  - nessun caso dal vivo in cui la sola protezione abbia impedito una scrittura: lo dimostra il
    rigioco;
  - A2 non esercitata dal vivo;
  - la casella ASCII dell'avvalimento non viene spuntata.
- **Grezzi:** `backend/data/compilation-audit/rami-e2e-20261025-01/`.
- **Risultati:** `benchmark ufficiale/rami-e2e-20261025-01/`.

## Istruzioni condizionali del FORM (revisione 2) — intervento offline del 25 ottobre 2026

**Punto di ripresa: fermarsi.** Continuazione dell'intervento di Astra sui tredici controesempi,
completata da Claude dopo l'interruzione per limiti. Rapporto:
`docs/istruzioni-form-2026-10-25.md`.

- **Chiusura del lavoro di Astra:** il backup previsto, mancante, è stato creato in
  `…/ambiti-form-backup-20261025/` e su `D:`; i 38 test sono stati rieseguiti con esito PASS.
  Nessun push.
- **Correzione `9711030`**, revisione 2 opt-in (`MAPI_FORM_OPTION_SCOPE_REVISION=2`, profilo
  `sezioni-istruzioni-2026-10-25`): un paragrafo in grassetto «(da compilare in/nel caso di …)»
  governa i campi di testo delle schede successive fino al titolo seguente.
  - Servono una condizione ancorata all'istruzione e una conferma USER verificata.
  - Citazione: istruzione intera, oppure prefisso fino alla prima alternativa (regola A2,
    scelta dall'utente dopo l'arresto preregistrato).
- **Rigioco:**
  - errori residui 6/25 → **0/25** con guardia simulata e 4/25 → **0/25** con ricevute
    registrate;
  - corrette 243/245: i 2 `p31.s0` USER nella scheda di un componente RT sono una
    discrepanza dichiarata, con giudizio storico invariato;
  - positive estese 236/240, come la base.
- **Verifiche:** 39 test nuovi; suite **3937 PASS**, Ruff PASS; K3 identico; 29 sessioni live e
  1244 file invariati; rollback verificato.
- **Limiti:**
  - la regola dipende dal grassetto e dal marcatore letterale;
  - possibile rischio di omissione se il modello non cita l'istruzione;
  - nessuna misura dal vivo.
- **Grezzi e backup:** `backend/data/compilation-audit/ambiti-istruzioni-20261025-01/`, backup
  `…/ambiti-istruzioni-backup-20261025/` e su `D:`.
- **Non eseguiti:** nessuna adozione nell'app, nessuna inferenza, nessun push.

## Sicurezza dei rami FORM — intervento offline del 25 ottobre 2026

**Punto di ripresa: fermarsi dopo il rapporto.** L'utente ha autorizzato il solo
lavoro sui tredici controesempi residui. Nessuna inferenza, adozione o modifica
all'app ordinaria. Rapporto: `docs/ambiti-form-2026-10-25.md`.

- Base reale `9cb3129`, branch `miglioramenti/2026-10-25-ambiti-form`, worktree
  `/home/montesano/tesi-ambiti-form`; preservata l'integrazione ordinaria recente.
- Fix `ddb8cb764bcb8dece4a43f80499b4933e759ed08`: dati introdotti da un'opzione
  ASCII locale `OPPURE ...:` richiedono una condizione propria valida e una
  scelta USER verificata. Nessuna inferenza su nomi di impresa o tipo di bando.
- Rigioco negativo: residui **13 -> 6 su 25** con guardia simulata SUPPORTED;
  **7 -> 4** con ricevute registrate. Sette ulteriori blocchi nell'ausiliaria;
  sei casi dei componenti RT ancora aperti.
- Positive: **245/245** con condizioni soddisfatte, **211/245** con sole ricevute
  storiche, invariati. Nessun falso rifiuto nuovo in questo insieme.
- 38 test nuovi PASS; suite **3898 PASS**, Ruff PASS. 26 casi K3 identici alla
  base. Revisione autoriale, nessuna nuova misura di qualità LLM.
- Rollback verificato: revert `c16d2a3`, albero esatto della base, difetto
  originale riprodotto (2 FAIL / 2 PASS). Nessuna migrazione o dipendenza.
- Opt-in **solo candidato**, `MAPI_FORM_OPTION_SCOPE_REVISION=1`; profilo
  `sezioni-opzioni-2026-10-25`. Il default e le sessioni precedenti non cambiano.
- 1244 file controllati e 29 sessioni live invariati; V12 preservata.
- Audit: `backend/data/compilation-audit/ambiti-form-20261025-01/` nel repository
  originario. Backup separato: `…/ambiti-form-backup-20261025/`.
- Il rapporto propone soltanto un micro-test futuro di due tentativi, massimo
  750.000 token: **non autorizzato e non avviato**. Nessun altro filone iniziato.

## Micro-test E2E della Compilazione DOCX predefinita (Cesano) — concluso, 24 ottobre 2026

**Punto di ripresa: fermarsi.** Un solo tentativo autorizzato, nessun altro test. Rapporto:
`docs/microtest-e2e-predefinito-2026-10-24.md`.

- **Esito:** DOCX prodotto dall'interfaccia ordinaria, profilo `sezioni-2026-10-24` verificato a
  ogni chiamata.
  - **Scritture:** 10 destinazioni, tutte DIMOSTRATA: 4 testi, 1 checkbox scelta dall'USER, 5
    deselezioni come effetto della scelta esclusiva. Revisione autoriale, non indipendente.
  - **Nucleo v3:** 4/4, più la decisione USER attesa `p19.cb0`, che in cesano-1 mancava.
  - **Costi e tempi:** 163.006 token su 300.000, circa 0,033 USD, 189 s; 2 segmenti, 0 retry.
- **Differenze d'interfaccia:**
  - «Sto lavorando…» per 2-6 s durante l'interpretazione di ogni messaggio;
  - «Preparazione del DOCX…» non compare, perché l'export avviene nella stessa richiesta.
- **Controlli non esercitati da Cesano:** R1, tabelle, riesame, ripresa.
- **Scostamento dichiarato:** backend avviato da un osservatore (stesso codice, `.env` e database;
  senza `--reload`) per il budget vincolante; poi app riportata a `./start.sh`.
- **Pulizia:** progetto temporaneo copiato ed eliminato; 29 sessioni e 273 file invariati.
- **Grezzi:** `backend/data/compilation-audit/microtest-predefinito-20261024-01/`.
- **Risultati:** `benchmark ufficiale/microtest-predefinito-20261024-01/`.

## Compilazione DOCX per sezioni come sistema predefinito — 24 ottobre 2026

**Punto di ripresa: fermarsi.** Decisione definitiva dell'utente, integrata e attivata. Rapporto,
verifiche e rollback: `docs/integrazione-compilazione-sezioni-2026-10-24.md`.

- **Profilo:**
  - un solo profilo canonico per le nuove sessioni, `backend/app/compilation_profile.py`
    (`sezioni-2026-10-24`);
  - contenuto: sezioni rev 3, V14, K3, stato derivato, dialogo P3, recupero del narratore, R1,
    tabelle condizionali, riesame rev 2, veto API;
  - nessuna variabile necessaria; le vecchie `MAPI_*_REVISION` sono ignorate;
  - le sessioni esistenti conservano i loro flag.
- **Interfaccia:**
  - solo «Compilazione DOCX», stati reali senza percentuali;
  - segmenti falliti dichiarati incompleti;
  - orario di ripresa dopo un crash, quando il lease non è ancora scaduto.
- **Commit** sul branch `integrazione/2026-10-24-compilazione-sezioni`, base `670e69c`:
  - `6d7477c` profilo;
  - `0933353` interfaccia;
  - `dc640fc` etichetta delle sezioni solo per sessioni rev 3;
  - più la documentazione.
- **Verifiche:**
  - backend 3860 PASS, Ruff PASS; frontend 152 PASS, oxlint, build;
  - E2E simulati 18/18 e continuation 4/4; `compilation-clarifications` 2 fallimenti
    preesistenti;
  - rigioco 25 controesempi: 13 ancora esportabili con guardia simulata, 245/245 corrette;
  - 162 esportazioni storiche senza rifiuti;
  - 29 sessioni live invariate;
  - bundle senza etichette sperimentali.
- **Attivazione nel working tree ordinario** (`/home/montesano/tesi`, senza commit
  sul branch dell'utente):
  - patch applicate, 370 file uguali a `dc640fc`, suite ripetute;
  - `./start.sh` su 8000 e 5173;
  - il processo reale crea sessioni con `SECTIONS`, verificato via API senza LLM con un progetto
    temporaneo eliminato;
  - dati e originali invariati.
- **Rollback di emergenza:** `MAPI_COMPILATION_PROFILE=storico` e riavvio. Il revert del codice
  nel working tree ordinario toglie anche il veto API e va usato solo dopo aver chiuso le
  sessioni create per sezioni.
- **Limiti:**
  - 13/25 errori storici dei rami non bloccati deterministicamente;
  - attesa del lease dopo un crash;
  - riesame e tabelle dimostrati solo offline;
  - costo da 1,8 a 4,1 volte la monolitica;
  - So.Re.Sa. invariata.
- **Non eseguiti:**
  - nessuna inferenza, campagna o micro-test DeepSeek, solo proposto;
  - nessun merge in `main`.
- **Grezzi:** `backend/data/compilation-audit/integrazione-sezioni-20261024-01/`.

## Campagna E2E della candidata incrementale — conclusa, 24 ottobre 2026

**Punto di ripresa: fermarsi.** Nessun nuovo sprint senza decisione dell'utente. Candidata non
adottata, nessun merge in `main`, app live invariata. Rapporto:
`docs/campagna-e2e-incrementale-2026-10-24.md`.

- **Svolgimento:**
  - 6/6 tentativi, 5 DOCX: minervino-1 è un fallimento infrastrutturale, frontend spento, 0
    chiamate;
  - 101 scritture, tutte DIMOSTRATA (revisione autoriale, non indipendente: Codex e poi Claude);
  - 0 aggiramenti, 0 rami sbagliati, 0 risposte 409;
  - 1.959.366 token su un tetto di 3,0 M, circa 0,31 USD.
- **Controllo delle tabelle:** non esercitato, il modello non ha proposto la sezione 5.c.
- **Riesame SOURCE:** 0 campi recuperati; 1 marcatura senza revisione successiva.
- **Ripresa dopo l'interruzione programmata:** riuscita, con cache riusata e senza duplicazioni;
  attesa del lease circa 25 minuti.
- **Copertura mediana:** Catanzaro 52%, Minervino 92% (1 DOCX), So.Re.Sa. 13%, Cesano 100%.
- **Grezzi:**
  - `backend/data/compilation-audit/incrementale-e2e-20261024-01/`;
  - `…-rapporto/`.
- **Risultati:** `benchmark ufficiale/incrementale-e2e-20261024-01/`.
- **Backup:** `backend/data/compilation-audit/incrementale-e2e-backup-20261024/` e
  `D:\Backup-tesi-2026-10-23\incrementale-e2e-20261024\`.

## Interventi incrementali offline — aggiornamento 24 ottobre 2026

Nuovo lavoro autorizzato su `miglioramenti/2026-10-23-docx-offline`, worktree
`/home/montesano/tesi-docx-offline`, base sprint `ff0d4f9`. Priorità 1: integrato
il codice dell’hotfix API già esistente (`4890daa`); 62 test mirati PASS, suite 3747 PASS + 3 casi storici PASS separati, Ruff PASS.
Commit priorità 1: `4554ae1`; rollback verificato (albero identico a `ff0d4f9`).
Priorità 2: nuova protezione opt-in `MAPI_TABLE_SCOPE_REVISION=1` sulle intestazioni
condizionali di tabella: controesempi bloccati 7 → 12 su 25, corrette 245/245.
Suite 3775 PASS, Ruff PASS; commit `480e7e5`, rollback verificato
(albero identico a `4554ae1`).
Priorità 3: nuova revisione opt-in `MAPI_HOLD_REREVIEW_REVISION=2` per rileggere
una sola volta alcuni dubbi SOURCE con fatto/ruolo già collegati. 123 test mirati
PASS; rigioco: 6 campi soci e 8 tecnici di Minervino riesaminabili, nessun
rilascio del backend. Il recupero reale dipenderà dal narratore e non è misurato.
Commit `3ec0af0`, suite 3796 PASS, Ruff PASS; rollback verificato.
Priorità 4: stessi dieci scenari di ripresa su entrambi i profili, 46 PASS,
nessuna modifica applicativa. Suite finale 3819 PASS, Ruff PASS.
Revert selettivi: rimosso ciascun fix, gli altri superano rispettivamente
69 / 54 / 58 test; nel revert delle tabelle è documentato il conflitto locale
fra i due flag adiacenti. Nessuna migrazione o perdita di sessioni.
Restano 13/25 errori storici non bloccati deterministicamente; il recupero reale
del narratore non è dimostrato. Ripresa offline positiva, invalidazione cache
conservativa su tutto il contesto SOURCE/USER.
**Punto di ripresa: decisione dell'utente sulla sola proposta E2E**,
`docs/proposta-e2e-incrementale-2026-10-24.md` (6 tentativi, tetto 3 M token).
Non avviare altre correzioni, inferenze o adozioni automaticamente.
Nessuna chiamata LLM, E2E o adozione live. Rapporto: `docs/docx-incrementale-2026-10-23.md`.


## Campagna E2E dopo lo sprint — conclusa, esito favorevole, 23 ottobre 2026

**Punto di ripresa: fermarsi.** Nessun altro sprint. Le decisioni spettano all'utente:
- adozione della candidata, mai automatica;
- integrazione della correzione ordinaria;
- push, solo con autorizzazione.

Rapporto: `docs/campagna-e2e-sprint-2026-10-23.md`.

- **Svolgimento:** 6/6 tentativi, 6 DOCX, 139 scritture riviste (revisione autoriale, non
  indipendente), 0 non dimostrate.
- **Sicurezza:** 0 aggiramenti; 0 scritture e 0 proposte nelle 25 destinazioni storiche; 0
  risposte 409.
- **Costi:** 2.559.649 token su un tetto di 2,9 M, circa 0,38 USD.
- **R1:** esercitato su Minervino senza falsi rifiuti.
- **Revisione mirata delle sospensioni:** non esercitata, 0 casi M. I 21 campi dei soci sono
  scritti in minervino-2 perché il narratore non li ha sospesi.
- **Nuovi falsi rifiuti rispetto ai gemelli:** 33, nessuno dovuto allo sprint:
  - 19 proposte non fatte o respinte;
  - 14 sospensioni del narratore fuori dal criterio M (citazione ancorata solo alla finestra, o
    blocco `source`).
- **Copertura mediana:** Minervino 81%, Catanzaro 39%, So.Re.Sa. 30%.

**Correzione di sicurezza del profilo ordinario, separata:**
- branch `fix/2026-10-23-bozza-esplicita` (`c7c3492`), worktree `/home/montesano/tesi-fix-bozza`;
- `global-draft` rifiuta per id le proposte sospese o non revisionate;
- suite 3.687 PASS;
- non attiva nell'app live e non inclusa nella candidata.

**Grezzi:**
- `backend/data/compilation-audit/sprint-e2e-20261023-01/`;
- `backend/data/compilation-audit/bozza-esplicita-20261023-01/`.

**Risultati:** `benchmark ufficiale/sprint-e2e-20261023-01/`.

## Sprint sulla compilazione per sezioni (rev 3) — 23 ottobre 2026, offline

**Punto di ripresa: decisione dell'utente sulla proposta E2E**
(`docs/proposta-e2e-sprint-2026-10-23.md`). Nessuna chiamata LLM, nessun push.

- **Branch:** `sprint/2026-10-23-sezioni`, worktree `/home/montesano/tesi-sprint`, base
  `dd41e2e`.
- **Commit locali:** uno per passo.
- **App live:** invariata; profilo ordinario, nessuna variabile `MAPI_*REVISION`.
- **Rapporto:** `docs/sprint-sezioni-2026-10-23.md`.
- **Grezzi:** `backend/data/compilation-audit/sprint-sezioni-20261023-01/`.

**Implementato** (opt-in, solo nuove sessioni con `MAPI_GENERATION_REVISION=3` e il proprio flag):
- **PASSO 1, R1 `branch_scope_revision 1`** (`MAPI_BRANCH_SCOPE_REVISION=1`): una condizione
  del modello ancorata a un'opzione (casella nativa o simbolo V14) si estende alla continuazione
  dell'opzione.
  - **Rigioco:** sbagliate rev 2 esportabili da 25 a 18 (guardia simulata), 245/245 corrette
    preservate, 0 nuovi falsi rifiuti.
  - **Limite:** le altre 18 richiedono una semantica delle sezioni, quindi sono documentate come
    limite.
- **PASSO 2, `hold_rereview_revision 1`** (`MAPI_HOLD_REREVIEW_REVISION=1`): una sospensione di
  applicabilità che cita la clausola di un'altra condizione torna una sola volta alla revisione
  del narratore. Il backend non rilascia nulla.
  - **minervino-2:** 21/21 sospensioni non fondate marcate, 0 falsi positivi su 145.
  - **Se non risospese:** l'export aggiunge esattamente le 21.
- **PASSO 3:** 10 scenari di ripresa testati.
  - **Difetto trovato e corretto solo in rev 3:** la bozza esplicita via API accettava proposte
    sospese o non revisionate.

**Verifiche eseguite:**
- **Suite:** 3.740 PASS alla fine (3.703 dopo il passo 1, 3.717 dopo il passo 2); Ruff PASS.
- **Rigiochi:** con il codice finale.
- **Confronto base/sprint:** 79 stati salvati (29 sessioni live, campagne), nessuna differenza.
- **Test V14, K3, rev 3 e narratore:** 185/185 con entrambi i profili.
- **Originali DOCX:** 17/17 intatti.

**Rischi residui:**
- la sicurezza dei rami resta empirica per 18 dei 25 casi;
- la revisione unica dipende dal modello;
- la lacuna della bozza esplicita resta nel profilo ordinario: è segnalata, non corretta.

## Campagna sulla candidata corretta — conclusa, esito favorevole, 23 ottobre 2026

**Punto di ripresa: fermarsi; decisione dell'utente sulla chiusura del lavoro sperimentale.**
Candidata non adottata, app live invariata (29 sessioni, nessun flag sperimentale), nessun commit
né push. Come deciso dall'utente, nessun nuovo ciclo di correzioni. Rapporto:
`docs/candidata-corretta-2026-10-23.md`.

- **Profilo:**
  - V14 + K3, stato derivato, dialogo P3;
  - `generation_revision 3` (FORM completo nei segmenti, controllo d'ambito USER);
  - recupero del narratore;
  - guardia rev 3 con motivazione fino a 1000 caratteri.
- **Prima delle inferenze:**
  - preregistrazione congelata alle 12:54:15 UTC, harness e codice congelati;
  - verifiche offline sui 25 controesempi rev 2 e sulla preservazione delle scritture corrette,
    Cesano compreso (`out/controesempi-rev2.json`);
  - 28 test sulle motivazioni lunghe; suite 3.677 PASS.
- **Esiti, 6/6 tentativi eseguiti:**
  - 6 DOCX;
  - 142 scritture riviste, 0 non dimostrate (revisione autoriale, non indipendente);
  - 0 scritture o proposte nelle 25 destinazioni sbagliate della rev 2;
  - 0 risposte 409, 0 errori del narratore, 0 verifiche respinte;
  - 2 segmenti recuperati con il retry dopo un JSON non valido.
- **Copertura mediana:** Minervino 72% (93% e 50%), Catanzaro 39%, So.Re.Sa. 47%.
- **Costi:** 2.570.195 token su un tetto di 2,8 M, circa 0,40 USD; 2-4,4 volte i token della
  monolitica e circa 1,6-1,7 volte il tempo.
- **Limiti:**
  - lo zero nei rami sbagliati è osservato, non garantito dai controlli deterministici;
  - sospensioni eccessive del narratore in minervino-2 (blocco tecnici incompleto);
  - copertura bassa su Catanzaro e So.Re.Sa.

Grezzo: `backend/data/compilation-audit/candidata-corretta-20261023-01/`. Risultati:
`benchmark ufficiale/candidata-corretta-20261023-01/` (compreso `CONFRONTO.json`). Backup:
`backend/data/compilation-audit/candidata-corretta-backup-20261023/`, escluso da Git e senza runtime
con chiave.

## Correzione della guardia rev 3 — 23 ottobre 2026, dopo l'arresto della campagna

**Punto di ripresa: decisione dell'utente su una nuova campagna preregistrata.** Applicata la
correzione autorizzata: in `FormScopeCheck` (solo rev 3) la `rationale` passa da 250 a 1000
caratteri. Gli altri vincoli della verifica d'ambito e la guardia ordinaria (250) sono invariati.
Nessuna inferenza, nessun commit; app live invariata (nessuna sessione rev 3).

- **Test nuovi:**
  - le tre motivazioni registrate mantengono la decisione del modello;
  - i rifiuti attesi restano;
  - limite ordinario invariato;
  - schema dichiarato.
- **Sensibilità:** sulla versione precedente falliscono solo i due casi SUPPORTED registrati e il
  test dello schema.
- **Rivalidazione:** le 7 verifiche registrate sono ora tutte valide e le 4 già valide hanno la
  stessa decisione.
- **Suite:** 3.649 PASS, Ruff PASS.

Rapporto: `docs/correzione-guardia-rev3-2026-10-23.md`. Audit:
`backend/data/compilation-audit/guardia-rationale-rev3-20261023-01/` (piano congelato, before/after,
patch, log). Backup: `backend/data/compilation-audit/guardia-rationale-rev3-backup-20261023/`.

## Campagna sulla candidata completa — arrestata, 23 ottobre 2026

**Punto di ripresa superato:** correzione della guardia applicata (sezione sopra). Campagna arrestata alle 11:06 UTC per la regola preregistrata «difetto grave del nuovo
backend» (`e2e/STOP.json`). Gate chiuso, server fermati. Nessuna modifica al codice applicativo,
nessun commit. Rapporto: `docs/candidata-completa-2026-10-23.md`.

- **Preparazione:** di Astra, interrotta prima delle inferenze; ripresa con l'addendum 2
  (harness ricongelato, ordine con Cesano in fondo). Revisione autoriale, non indipendente.
- **minervino-1:**
  - DOCX, 39 scritture tutte uguali al riferimento, 0 non dimostrate;
  - nessuna in `p37.*` (rev 2: 7);
  - copertura 65%, 484.353 token.
- **catanzaro-1:**
  - DOCX, 11 scritture, 0 non dimostrate;
  - nessuna in `t19.*`, la sezione 5.c (rev 2: 5);
  - copertura 35%, 536.892 token.
- **soresa2023-1:**
  - **senza DOCX**;
  - la guardia rev 3 ha respinto due conferme corrette (SUPPORTED/SUPPORTED) perché la
    `rationale` superava i 250 caratteri; la sessione non avanza e il driver va in timeout;
  - l'analisi non ha proposto nulla nei rami sbagliati della rev 2 (avvalimento, blocchi dei
    componenti RT).
- **Esiti complessivi:** 13/13 segmenti analizzati, 0 retry, 0 risposte 409, 0 errori del narratore.
- **Non avviati per arresto:** minervino-2, catanzaro-2, soresa2023-2, cesano-1, cesano-2.
- **Budget:** speso 1.184.239 token su 3.000.000.

**Proposta da valutare (non implementata):** nella sola verifica d'ambito rev 3 non respingere per
la lunghezza della motivazione, che nessuna logica usa; aggiungere test con i tre output
registrati; poi una nuova campagna preregistrata con nuovo congelamento.

Grezzo: `backend/data/compilation-audit/candidata-completa-20261023-01/`. Risultati:
`benchmark ufficiale/candidata-completa-20261023-01/`. Backup:
`backend/data/compilation-audit/candidata-completa-backup-20261023/`, escluso da Git e senza
runtime con chiave.

## Passo 3 — recupero del narratore, opt-in — 23 ottobre 2026

L'utente ha autorizzato il terzo passo. Implementato il flag persistito separato
`narration_recovery_revision=1`, selezionabile per nuove sessioni con
`MAPI_NARRATION_RECOVERY_REVISION=1`. **Non attivato nel runtime ordinario**;
le sessioni senza flag mantengono il comportamento precedente, incluse rev 3.

- Un solo retry della sintesi, stesso input, massimo 45 s / 2048 token per
  tentativo; niente riparazioni o recupero di parti del JSON fallito.
- Nessuna proposta nella finestra: lo schema richiede liste di sospensioni vuote.
- Dopo due errori: messaggio backend, analisi e decisioni conservate, nessuna
  revisione nuova. La bozza parziale usa solo revisioni ancora valide, rispetta
  hold e tutti i controlli esistenti; può essere vuota. Nessun export automatico.
- Ripresa esplicita della sola sintesi, lease adeguate, tentativi e consumi
  separati. Metriche mancanti restano sconosciute, non vengono contate come zero.
- Veto anche sull'API per forzature SOURCE non revisionate o sospese durante il
  fallback, ripetuto sull'audit ricalcolato. Parser/writer/segmentazione invariati.

Verifiche mirate: 121 PASS; 33 PASS sui casi del recupero; 2 PASS sul veto V14.
**Suite completa finale: 3.640 PASS in 353,53 s; Ruff PASS.**
Rete bloccata, provider simulati,
DB/storage temporanei; nessuna inferenza reale o nuova E2E.

Riprodotto l'errore minervino-2 con la risposta registrata. Controprova sullo
stato originale, **solo in memoria**: conservate 63 revisioni, 15 sospensioni e
quattro risposte; selezione riaccessibile di 48 SOURCE + 1 USER nel vecchio
profilo. Non è un nuovo DOCX né una verifica della correttezza di quei valori;
non cambia il 7/8 della campagna congelata. Il test con 45 proposte conserva
le 40 revisionate quando la finestra successiva fallisce, escludendo le altre 5.

Rapporto: `docs/compilazione-passo3-narratore-2026-10-23.md`.
Audit: `backend/data/compilation-audit/recupero-narratore-passo3-20261023-01/`.
Backup verificato del passo, separato da Git:
`backend/data/compilation-audit/recupero-narratore-passo3-backup-20261023.tar.gz`.
La candidata completa resta non adottata. Restano i limiti semantici e le
25 scritture rev 2 non ancora dimostrate risolte. Prossimo passo: valutazione
reale limitata e preregistrata dei tre interventi insieme, senza altri filoni.

## Passo 2 — contesto e ambito USER, candidata rev 3 — 23 ottobre 2026

L'utente ha autorizzato il secondo passo. Implementata **solo nella candidata
`MAPI_GENERATION_REVISION=3`**, non adottata nell'app ordinaria:

- ogni segmento legge tutti i blocchi del catalogo FORM; output e piano locale
  restano limitati alle destinazioni proprietarie;
- mantenuti partizione, retry limitati, cache e ripresa rev 2. Il FORM condiviso
  precede i dati specifici nel prefisso; modifiche anche lontane invalidano cache;
- disattivata in rev 3 l'unificazione delle condizioni che ignorava differenze
  di significato/scope; resta la deduplica esatta. Possibili conferme ridondanti;
- il guard USER esistente richiede anche un esito distinto sull'ambito effettivo,
  ricevendo FORM completo e destinazioni. Le ricevute interne legano risposta,
  campi e condizioni; export e rivalidazione rifiutano ricevute assenti/obsolete;
- un valore USER da solo non aggira un segmento fallito. Una catena USER verificata
  indipendentemente può sostenere quel valore, senza sbloccare il riuso SOURCE;
- il profilo ordinario rimane V14 + K3 + derivation_revision 1; rev 1/2 e sessioni
  storiche non migrate. Parser, writer, retrieval e contratto V12 invariati.

Verifiche: prima suite completa **3.603 PASS**; due ulteriori controesempi finali
riprodotti e corretti (prefisso e condizione diventata falsa). **Suite finale:
3.605 PASS in 327,91 s; Ruff PASS.** Tutti i test usano provider simulati,
rete bloccata e storage
temporaneo. Nessuna inferenza reale, nuova campagna E2E, commit/tag/push.

**Non dichiarare risolte le 25 scritture rev 2.** La presenza del FORM completo
e il nuovo schema di controllo non provano che il modello riconosca tutte le
condizioni. Il controesempio di condizione non riconosciuta resta nei test.
Input JSON più grandi: 1,21–2,09× in caratteri sui quattro input storici esaminati;
nessuna nuova misura di token, cache reale, costo o latenza. Candidata non pronta
per l'adozione ordinaria sulla sola base delle prove offline.

Rapporto e preregistrazione: `docs/compilazione-passo2-contesto-2026-10-22.md`.
Audit: `backend/data/compilation-audit/contesto-sezioni-passo2-20261022-01/`.
Backup del passo, separato da Git:
`backend/data/compilation-audit/contesto-sezioni-passo2-backup-20261023.tar.gz`.
Prossimo passo distinto: recupero limitato degli errori del narratore; poi
eventuale piccola verifica reale preregistrata, senza nuova campagna da 35.

## Passo 1 — fix dello stato derivato promosso separatamente — 22 ottobre 2026

L'utente ha autorizzato di procedere per passi dopo la revisione della candidata
di Opus. **Completato il primo passo:** nelle nuove sessioni il profilo predefinito
è V14 + K3 + `derivation_revision=1`. La correzione del 409 è promossa da sola;
dialogo P3 e generazione per sezioni restano opt-in e non adottati.

- Cambiata soltanto `initial_state` nel codice applicativo. Il ricalcolo dopo
  ogni mutazione USER e il veto finale di Opus restano identici.
- `MAPI_DERIVATION_REVISION=0` permette il confronto col profilo precedente
  sulle nuove sessioni. Le sessioni già salvate mantengono i propri flag, senza
  migrazioni: quelle prive del flag possono ancora manifestare il vecchio 409.
- Verifiche nuove, con rete bloccata e provider simulati: 39 test prima della
  modifica; 72 mirati dopo; 76 del dialogo/derivazione dopo l'adeguamento di una
  fixture; **suite finale 3.564 PASS in 309,90 s; Ruff PASS**.
- La prima suite completa ha avuto 2 FAIL nella stessa fixture FTS5/Qdrant:
  alterava soltanto l'audit, lasciando un diverso output MODEL immutabile.
  Ora il provider simulato restituisce i chiarimenti da testare; le aspettative
  sulla risposta parziale USER sono rimaste identiche.
- I test AnyIO si bloccavano nel sandbox anche in un programma minimo; esecuzione
  fuori sandbox autorizzata, con rete ancora bloccata dal runner e storage
  temporaneo. Nessuna chiamata LLM reale, nuova E2E o modifica dei dati live.
- Non rieseguito il replay HTTP storico di minervino-1; resta evidenza precedente.
- Nessun commit/tag/push; baseline e risultati congelati preservati.

Rapporto: `docs/compilazione-passo1-stato-derivato-2026-10-22.md`.
Audit: `backend/data/compilation-audit/stato-derivato-passo1-20261022-01/`.
Backup verificato, separato da Git:
`backend/data/compilation-audit/stato-derivato-passo1-backup-20261022.tar.gz`.

**Prossimo punto di ripresa:** passo 2, disegno minimo del FORM completo in
lettura per ogni segmento, output limitato alle destinazioni proprietarie e
verifica distinta dell'ambito delle condizioni/decisioni USER. Il recupero del
narratore è il passo successivo. Questi interventi non sono ancora implementati;
non considerare risolte le 25 scritture non dimostrate della candidata rev 2.

## Sezioni resilienti e coerenza dello stato derivato — 22 ottobre 2026, sera

**Punto di ripresa: fermarsi; decisione dell'utente.** Due candidate opt-in, **non adottate**.
Nessun commit, tag o push. V12 resta la baseline congelata; l'app live è invariata (29 sessioni,
nessun flag sperimentale, ultima modifica al 17 ottobre). Rapporto:
docs/sezioni-resilienti-2026-10-22.md.

### Implementato (opt-in, nuove sessioni)

- **`derivation_revision 1`** (`MAPI_DERIVATION_REVISION=1`):
  - `apply_replies` ricalcola l'audit derivato dopo ogni mutazione USER accettata;
  - il veto finale dell'export resta invariato;
  - indipendente dalla segmentazione.
- **`generation_revision 2`** (`MAPI_GENERATION_REVISION=2`):
  - **Funzioni nuove** in `backend/app/compilation_segments.py`:
    - partizione per unità di dipendenza (blocco, paragrafi locali, regioni V14);
    - contesto locale del segmento;
    - cache per digest della richiesta;
    - unificazione delle condizioni condivise;
    - stati di applicabilità VERIFICATA / CONDIZIONATA / NON ACCERTATA.
  - **Integrazione** in `_resilient_proposal`, in `compilation_global_sessions.py`:
    - validazione V12 per segmento prima del merge;
    - retry limitati (1 per segmento, 2 per analisi);
    - merge con `budget_scale`;
    - veto ed esclusione dall'export delle destinazioni NON ACCERTATE o con paragrafo incerto.
- **Modifica condivisa:** `budget_scale=1` in `validate_global_proposal`. Compatibilità verificata:
  193/193 risposte registrate rivalidate in modo identico al validatore congelato.
- **Test:** `backend/tests/test_compilation_derivation.py` e
  `test_compilation_resilient_segments.py`.

### Verifiche eseguite

- **409:** replay deterministico di minervino-1: 409 senza flag, export riuscito con il flag.
- **Suite:** 3.560 PASS, Ruff PASS.
- **Replay:** 247/247 sintesi e 16/16 catene P3 identiche.
- **Strumenti di valutazione (T11):** verificati; rianalisi della valutazione finale identica.
- **Campagna E2E esplorativa preregistrata** (8 tentativi):
  - 7/8 DOCX; minervino-2 fallito per errore di schema del narratore, che con il dialogo P3 blocca
    l'export;
  - 30/30 segmenti analizzati, 0 retry, 0 risposte 409;
  - 1,85 M token su un tetto di 3 M, 0,37 USD.

### Esito

- **Non pronta** per il criterio preregistrato (a): 25 scritture SOURCE non dimostrate (revisione
  autoriale, non indipendente) in 4 DOCX su 7, contro 0 su 423 della monolitica.
- **Causa:** sono in rami non pertinenti (studio associato, sezione 5.c, avvalimento, blocchi dei
  componenti RT), perché il paragrafo che governa il ramo non era nel contesto del segmento.
- La resilienza a fallimenti e la ripresa sono verificate **solo offline**: nell'E2E nessun
  segmento è fallito.

### Proposta da valutare (non implementata)

Passo eventuale, da approvare, seguito da test offline e da una nuova piccola campagna:
- contesto del segmento esteso a tutti i blocchi del suo span e all'intestazione o opzione che lo
  governa;
- tagli solo su intestazioni di sezione.

La correzione del 409 è promuovibile separatamente, se l'utente lo decide.

### Dati

- **Grezzo:** `backend/data/compilation-audit/sezioni-resilienti-20261022-01/`, con piano,
  addendum e preregistrazione congelati.
- **Risultati:** `benchmark ufficiale/sezioni-resilienti-20261022-01/`.
- **Runtime privati con chiave:** `.tools/sezioni-resilienti-20261022-01/`, esclusi dal backup.
- **Backup:** `backend/data/compilation-audit/sezioni-resilienti-backup-20261022/`, escluso da Git.

## Valutazione finale del candidato — 22 ottobre 2026, pomeriggio

**Punto di ripresa: fermarsi; decisione dell'utente sul candidato.** Candidato non adottato,
V12 resta la baseline congelata. Nessun commit, tag o push; codice applicativo invariato durante e
dopo la campagna.

Profilo valutato: V14 + K3, dialogo P3 corretto (`MAPI_DIALOGUE_REVISION=1` solo nei runtime
sperimentali), generazione monolitica, sezioni disattivate. L'app live è invariata (V14 + K3).

Criteri v1 applicati senza modifiche, preregistrazione congelata alle 10:53:06 UTC.
- **Moduli:** 6 storici (Minervino, Cesano, CRAA, Catanzaro, Bella, Trapani) più il modulo nuovo
  So.Re.Sa. 2023, estratto con seme. Cannara, estratto per primo, è fuori ambito: nessuna
  destinazione del nucleo riconosciuta (spazi resi con tabulazioni).
- **SOURCE in formato diverso** per il modulo nuovo: scheda tabellare DOCX→PDF in un runtime
  separato.
- **Tentativi:** 35 (5 per modulo), nessuna sostituzione; 4,15 milioni di token, circa 0,92 USD
  stimati.

Esiti rispetto alle soglie:
- **DOCX:** 32/35 (91,4%), ogni modulo almeno 4/5 → raggiunto;
- **copertura mediana ≥ 70%:** raggiunta su 5 moduli su 7 (Minervino 79%, Cesano 100%, CRAA 100%,
  Bella 88%, Trapani 94%); non raggiunta su Catanzaro (32%) e So.Re.Sa. (47%: binding di ruolo
  respinto perché il FORM chiede solo «in qualità di»; i dati dalla scheda PDF sono scritti
  correttamente);
- **sicurezza:** revisione indipendente non disponibile, quindi criterio non verificabile;
  revisione autoriale e automatica: 0 scritture non dimostrate su 423; pacchetto cieco pronto
  (`REVISIONE-CIECA/`);
- **dialogo:** 19 conferme ridondanti → non raggiunto;
- **vuoti con motivo:** 352/354 (2 in CRAA, solo il motivo generico) → non raggiunto;
- **visibilità:** 0 warning;
- **fallimenti:** MODEL 2 (JSON non valido), EXPORT 1 (409: ricevuta SKIP del firmatario senza
  riallineamento dell'audit), narratore 0, backend 0.

Rapporto: docs/valutazione-finale-2026-10-22.md. Dati in
`benchmark ufficiale/valutazione-finale-20261022-01/`, grezzo in
`backend/data/compilation-audit/valutazione-finale-20261022-01/`. Backup verificato in
`backend/data/compilation-audit/valutazione-finale-backup-20261022/` (escluso da Git). I runtime
privati con chiave sono in `.tools/valutazione-finale-20261022-01/`, esclusi dal backup.

## Strategia di generazione — 22 ottobre 2026, dopo la decisione sul profilo P3

**Punto di ripresa: valutazione finale con i criteri congelati, dopo la scelta dell'utente
sull'esperimento proposto.** Nessuna modifica al codice, nessuna chiamata LLM, nessun commit.

Decisioni dell'utente (22 ottobre):
- il dialogo P3 corretto è una candidata sperimentale, disattivata nelle nuove sessioni
  ordinarie e attivabile solo esplicitamente (`MAPI_DIALOGUE_REVISION=1`, usato dai test);
- la segmentazione è disattivata per impostazione predefinita;
- nessuna ulteriore modifica al narratore per le singole conferme ridondanti;
- i criteri di conclusione restano invariati;
- nessuna campagna massiva.

Stato verificato: le nuove sessioni live sono V14 + K3.

Analisi offline sulle 158 chiamate globali registrate (132 monolitiche, 6 moduli reali, stessa
configurazione):
- tutti i 5 troncamenti sono in un solo modulo (267 posizioni; 5 su 28);
- 0 troncamenti nei moduli fino a 115 posizioni e in quello da 307;
- il pool casuale di 8 bandi va da 35 a 88 posizioni.

Esito:
- **criterio a priori per dimensione: respinto.** Il segnale esiste (R² 0,72), ma inverte
  l'ordine di rischio dei due moduli grandi, la soglia non si può localizzare e il costo sarebbe
  3,9-5× i token;
- **criterio a posteriori (sezioni solo dopo un troncamento): promettente ma limitato.** Costo
  atteso 169k token contro 98k del monolitico e 382k delle sezioni sempre attive. Esperimento
  proposto e non eseguito (3 sessioni con troncamento forzato da replay, circa 1,3 milioni di
  token).

Raccomandazione: valutazione finale con generazione monolitica, troncamenti contati come classe di
fallimento separata e dichiarata.

Rapporto: docs/strategia-generazione-2026-10-22.md. Dati in
`backend/data/compilation-audit/strategia-generazione-20261022-01/`.

## Narratore P3 e fallback dell'app live — 22 ottobre 2026, mattina

**Punto di ripresa: fermarsi; spetta all'utente decidere sul profilo P3.** La V12 resta la
baseline. Nessuna adozione, nessun commit o push.

**P3 è ora opt-in.** Prima della modifica, l'app live (uvicorn `--reload` sul working tree)
avrebbe creato le nuove sessioni con P3. Nessuna delle 29 sessioni salvate ha flag P3.
`initial_state` crea ora le nuove sessioni con il profilo V14 + K3 (`backend_revision 13`,
`option_authorization_revision 1`, `attribution_safety_revision 1`). Il dialogo P3 si attiva
solo con `MAPI_DIALOGUE_REVISION=1`, la segmentazione solo con `MAPI_GENERATION_REVISION=1`.
Le sessioni esistenti conservano i propri flag. Verifiche del fallback:
- worker live ricaricato;
- profilo e richiesta globale identici all'albero pre-P3 ricostruito (4 FORM);
- 215 sintesi legacy identiche al pre-P3.

**Correzione del narratore** (solo `dialogue_revision 1`, `compilation_global_dialogue.py`):
- una sospensione con citazione non ancorata, ripetuta o con riferimento inesistente non
  respinge più l'intera sintesi;
- la proposta resta sospesa, senza rilascio automatico;
- con un riferimento non risolvibile resta sospesa l'intera finestra;
- il rilascio per risposta richiede uno slot che governi la proposta, oppure la citazione della
  sua stessa condizione.

Il percorso legacy è invariato.

Verifiche:
- **offline** (zero LLM): le 4 risposte reali respinte sono ora accettate come preregistrato,
  tranne la fase di minervino-B1 (errore di previsione, addendum 2); 13 test nuovi
  (`test_compilation_p3_hold_validation.py`); suite 3.509 PASS; Ruff PASS;
- **E2E** (8 prove, dialogo P3 + generazione monolitica, appaiate al braccio A di P3,
  1,01 milioni di token): 7 DOCX su 8, contro 6 su 8; 0 sintesi respinte; 0 scritture non
  dimostrate (revisione dell'autore); V14 rispettato. L'unico fallimento è minervino-N2:
  troncamento della chiamata globale monolitica (49.152 token), estraneo al narratore.
  I percorsi nuovi delle sospensioni non sono stati esercitati da risposte reali (16 sospensioni,
  tutte ancorate). Conferme ridondanti: 1 (scelta della casella di partecipazione in Cesano).

Raccomandazione: dialogo P3 disattivato nell'app live; usarlo come candidata nella
valutazione finale con i criteri congelati. Segmentazione da decidere a parte.

Rapporto: docs/narratore-p3-2026-10-22.md. Backup locale (escluso da Git):
`backend/data/compilation-audit/narratore-p3-backup-20261022/` (SHA256 `aaaff81d…`, 1.046 file,
verificato per estrazione). Runtime privato con chiave:
`.tools/narratore-p3-verifica-20261022-01/` (escluso dal backup).

## P3, dialogo e generazione per sezioni — 22 ottobre 2026

**Punto di ripresa: fermarsi; spetta all'utente decidere.** La candidata P3 non è pronta e
non è adottata; la V12 resta la baseline. Nessun commit o push.

**Superato dalla sezione precedente:** P3 è ora opt-in e le nuove sessioni usano il profilo
V14 + K3. In origine, nel working tree le nuove sessioni usavano P3.

Diagnosi e preregistrazione: `backend/data/compilation-audit/p3-20261021-01/`
(PREREG SHA256 `7bf79973…`).

Codice:
- moduli nuovi `compilation_segments.py` e `compilation_decision_registry.py`;
- file modificati `compilation_global.py`, `compilation_global_sessions.py`,
  `compilation_global_dialogue.py`, `compilation_chat.py`, `compilation_branch_evidence.py`,
  `compilation_source_reuse.py`;
- test nuovo `tests/test_compilation_p3.py` (34); tre test esistenti estesi con la variante
  per le sessioni precedenti.

Verifiche:
- suite backend 3.479 PASS, Ruff PASS;
- proiezione: 0 differenze su 12.677 candidate;
- replay sospensioni: 36 rilasci su 47;
- replay filtro « o »: 110 proposte su 110 accettate.

Campagna E2E preregistrata (16 prove; braccio A = dialogo nuovo, braccio B = dialogo nuovo
+ sezioni; 3,62 milioni di token):
- **12 DOCX su 16** (6/8 per braccio). I 4 fallimenti (Minervino 3, Catanzaro 1) hanno tutti
  la stessa causa introdotta da P3: il narratore viene respinto per sospensioni non ancorate
  o fuori finestra, così senza domande non c'è export;
- B contro A: 0 troncamenti; 25/28 chiamate sotto il 50% del limite; output mediano 12k
  contro 30k; token 2,7×; 2 segmenti persi per JSON non valido, visibili come «sezione non
  analizzata»; nessun guadagno dimostrato sul nucleo;
- Cesano: `p19.ft0` scritto 4 volte su 4. CRAA: CCIAA scritte solo con ramo confermato e
  autorizzazione accettata (2/2), vuote nella variante «ramo» (2/2);
- 0 scritture non dimostrate (revisione dell'autore), 0 aggiramenti V14/K3;
- domande ridondanti ancora 10 (obiettivo 0).

Prossime attività:
1. correggere la validazione delle sospensioni del narratore, con verifica offline sulle 4
   risposte respinte e una nuova breve verifica E2E;
2. decidere se attivare le sezioni solo oltre una soglia di dimensione.

Rapporto: docs/p3-dialogo-generazione-2026-10-22.md. Campagna in
`benchmark ufficiale/p3-verifica-20261022-01/`, grezzo in
`backend/data/compilation-audit/p3-verifica-20261022-01/`. Backup verificato in
`backend/data/compilation-audit/p3-backup-20261022/p3-audit-completo.tar.gz`
(SHA256 `9e4c76f1…`, 1.885 file, 164 MB; escluso da Git, non includere in un commit senza
decisione). Il runtime privato `.tools/p3-verifica-20261022-01/` contiene la chiave ed è
escluso dal backup.

## Controllo di attribuzione condiviso — 21 ottobre 2026, notte

**Punto di ripresa: fermarsi; il prossimo intervento principale è P3.** La V12 resta
adottata. V13, V14 e tutti gli audit sono conservati. Nessuna adozione, nessun commit
o push, nessuna chiamata LLM.

Preregistrazione alle 21:11:57 UTC (SHA256 `2772f511…`), prima del codice. Tre controlli,
decisi separatamente:
- **K1, classe del codice fiscale: escluso.** Nel replay perde 39 proposte corrette (la
  partita IVA `IT01234567890` registrata come CF aziendale).
- **K2, coerenza «in chiusura» delle attestazioni di carica: escluso.** Perde 147
  corrette (15,5%) per una sola frase affermativa della KB su Elisa Romano.
- **K3, organizzazione nominata nell'attestazione di ruolo: implementato.** Una voce
  SOURCE certa «- **P:** R di X» con X diversa dalle imprese documentate dalla bozza
  toglie il grounding alla proposta personale. Nel replay: 0 perdite e 0 modifiche;
  ferma il controesempio 3 di P2.
- **K4, appartenenza lato FORM: escluso a priori.** Rischio residuo.

Codice: `backend/app/compilation_attribution_safety.py` (nuovo), chiamata alla fine di
`reuse_selected_person`. Il flag `attribution_safety_revision: 1` è in `initial_state` e
viene copiato in `resolve_global`, quindi vale solo per le nuove sessioni; le sessioni
esistenti restano identiche. Nessuna ricevuta USER annulla il blocco.

Verifiche:
- 26 casi sintetici: conformi, salvo 2 esclusi perché il gate attuale non li accetta;
- equivalenza fra modulo e candidato valutato: 26 casi, 92 audit, 0 differenze;
- 13 test nuovi;
- suite backend completa PASS: arrivata al 100% con arresto al primo errore,
  3.439 test raccolti;
- Ruff PASS.

Rischio residuo aperto: ruolo FORM di un partner (controesempi 1-2), carica cessata
scritta in prosa altrove (5), CF societario come personale (4), documenti di terzi senza
organizzazione esplicita. Nelle prove registrate nessuno si è attivato; vanno controllati
nella revisione indipendente finale.

Rapporto: docs/controllo-attribuzione-2026-10-21.md. Grezzo in
backend/data/compilation-audit/attribution-safety-20261021-01/; backup
docs/benchmarks/2026-10-21-controllo-attribuzione-audit.tar.gz.

## Provider embedding e ordine delle impostazioni — 21 ottobre 2026

Richiesta UI/RAG autonoma: ordine **Modelli AI → Modelli di embedding → Ricerca
nelle fonti**. Provider embedding selezionabili: Ollama, OpenAI, Mistral e API
compatibili OpenAI; un servizio/modello attivo, indipendente dai profili chat.
Catalogo, credenziali e protocollo effettivo implementati; non solo etichette UI.

Campo JSON aggiuntivo `embedding_provider`, default Ollama per i dati precedenti,
nessuna migrazione o riscrittura implicita. Credenziali nuove al cambio provider,
nessun riuso delle chiavi chat/Qdrant. Adattatore remoto con controlli di ordine,
conteggio e integrità dei vettori; nessun retry/fallback. Digest Ollama conservato,
identità degli indici remoti distinta per provider. Nessun comando indice Qdrant live,
prova provider a pagamento o modifica della compilazione. I limiti del digest
remoto sono espliciti nel [rapporto](docs/provider-embedding-2026-10-21.md).
Log e preservazione: backend/data/compilation-audit/embedding-providers-ui-20261021-01/.
Il backend preesistente in auto-reload riesegue l'avvio quando cambiano i file:
ricostruiti FTS e ID/timestamp dei frammenti artifact. Non dichiarare il file DB
identico; copia privata precedente e confronti logici conservati, nessun ripristino.
Le 29 sessioni e le SOURCE sono identiche; 82 frammenti artifact hanno contenuto e
posizione conservati, ma ID/timestamp ricreati. Rilevate modifiche concorrenti a
compilation_global_sessions.py e compilation_source_reuse.py, non toccate da questo
intervento: il working tree condiviso non costituisce un freeze di compilazione.
Le decisioni P2/V12/V13/V14 qui sotto restano invariate. Nessun commit o push.
Verifiche eseguite: 3.426 test backend PASS, 147 frontend PASS (25 del pannello),
sei E2E desktop/mobile con API simulate PASS; Ruff, lint e build PASS. Nessuna
prova del provider reale. Backup dedicato con estrazione separata e manifest
nel rapporto; copia privata del DB iniziale esclusa dall'archivio condivisibile.

## P2, attribuzione di ruolo a livello di record — 21 ottobre 2026, sera

**Punto di ripresa: fermarsi.** L'utente deve scegliere fra le opzioni del rapporto.
L'utente ha approvato la V14 come base tecnica per P2, non come baseline: la V12 resta
adottata. V13, V14 e i loro artefatti restano intatti. P3 non è avviata. Nessuna modifica
applicativa, commit o push; UI e configurazioni RAG di Codex non toccate. I file applicativi
e di test hanno gli stessi hash dello snapshot pre-P2.

Esperimento offline preregistrato (20:44:06 UTC), zero chiamate LLM:
- **simulazione** sulle risposte registrate: 47 recuperi, tutti corretti (Minervino 43,
  Catanzaro 4), 0 errati, 0 regressioni. Preservati i rifiuti azienda→persona di Cesano
  (8 prove) e i blocchi dell'amministratore cessato (5); nessun recupero in regioni d'opzione V14;
- **controesempi**: prima serie 15/15 conforme; nella seconda serie 5 negativi su 11 sono
  recuperati: ruolo FORM dell'impresa ausiliaria, ruolo della mandante, DT di un'altra
  azienda grounded, CF societario nel record della persona, carica lasciata con un verbo
  non in elenco. **Regola non implementata**, come prevede la regola di decisione;
- **gate attuale**: gli stessi 5 casi passano anche il controllo V12/V14 quando il modello
  cita bene. Nelle 719 proposte personali accettate registrate non si sono mai attivati.
  Le falle restano strutturali; possibile esposizione su moduli nuovi con imprese partner.

Opzioni non implementate:
1. nessun P2 autonomo;
2. conferma USER per persona e ruolo, raccomandata e da pianificare con P3;
3. rafforzamento del gate condiviso e poi P2 v2, con una nuova candidata.

Tutte e tre le opzioni presuppongono che le falle condivise siano segnalate alla revisione
indipendente finale. Rapporto: docs/p2-attribuzione-record-2026-10-21.md. Grezzo in
backend/data/compilation-audit/p2-record-binding-20261021-01/; backup verificato
docs/benchmarks/2026-10-21-p2-record-binding-audit.tar.gz (SHA256 `57ba6489…`, 21 file).

## Verifica E2E della candidata V14 — 21 ottobre 2026, sera

**Punto di ripresa: fermarsi.** Spetta all'utente decidere sull'adozione della V14 come
base per P2. P2 e P3 non sono avviati. Nessuna modifica di codice, commit o push.

Sei tentativi reali preregistrati (protocollo 19:30:07 UTC, dopo i criteri congelati),
eseguiti dalla UI ordinaria in un runtime privato. Esiti:
- 6 DOCX su 6, 55 chiamate, 802.062 token, nessun errore del provider;
- **craa-ramo**: la ricevuta del solo ramo è accettata ma non scrive le celle CCIAA; con le
  stesse ricevute e la stessa revisione la V13 le avrebbe scritte;
- **craa-autorizza**: autorizzazione accettata, ma la condizione di ramo del modello non è
  stata chiesta dal narratore, quindi celle vuote;
- **Cesano**: `p19.ft0` recuperato in 1 tentativo su 2; nell'altro le trattenute del
  narratore, presenti anche in 4 prove V13 su 20, hanno bloccato tutto;
- **Minervino**: 51/60 e 26/60; in minervino-b 33 proposte respinte dal binding di ruolo.

Costo di dialogo: una domanda di autorizzazione al primo turno nelle prove CRAA e Cesano,
una sola domanda slittata al turno successivo, nessuna risposta rifiutata. Sicurezza: zero
scritture in regioni d'opzione senza autorizzazione e zero scritture non dimostrate nella
revisione dell'autore (non indipendente); nessun valore invisibile nei PDF. Conferme
ridondanti da 0 a 3 per tentativo (preesistenti, area P3).

Limiti per P3: l'autorizzazione dell'intera clausola non soddisfa la condizione di ramo
ancorata alla stessa clausola; le trattenute del narratore non si rilasciano dopo una
risposta che ne rimuove il motivo.

Attività concorrente: dopo la campagna un'altra sessione ha modificato sette file delle
impostazioni retrieval e il database live (app su 8000/5173). Le prove avevano già
verificato gli hash V14 a ogni chiamata; percorso di compilazione non coinvolto; lavoro
altrui non toccato.

Rapporto: docs/v14-verifica-e2e-2026-10-21.md. Materiali in
benchmark ufficiale/v14-verifica-20261021-01/, con archivio verificato (SHA256 `2c317d72…`,
894 file, da non aggiungere a un commit senza decisione). Grezzo in
backend/data/compilation-audit/v14-verifica-20261021-01/. Il runtime privato con la chiave
in .tools/ è escluso dal backup.

## UX/UI ricerca: due riquadri e modelli Ollama — 21 ottobre 2026

Rifinitura richiesta dall'utente: «Ricerca nelle fonti» con metodo «Semantica»
e «Impostazioni avanzate» per archivio/manutenzione; sotto «Modelli di embedding»
con selettore dei modelli installati su Ollama e proprie impostazioni avanzate
per indirizzo e chiave. Rimosse le descrizioni indicate dall'utente. Un solo
salvataggio applica i due riquadri senza modificare il formato persistito.

Aggiunta la sola lettura `/api/settings/retrieval/models`, con credenziali
embedding e filtro sulla capacità `embedding` dichiarata da Ollama. Riutilizzata
la discovery AI, con default `completion` conservato per la chat; nessun download,
generazione o accesso a Qdrant. Elenco non disponibile/vuoto o risposte obsolete
non modificano il modello configurato. Nessun algoritmo di retrieval/embedding,
indice live, sessione o pipeline DOCX modificato. Nessun commit o push.

Verifiche, limiti e file nel rapporto
[revisione UI ricerca](docs/revisione-ui-ricerca-2026-10-21.md), sezione revisione 2;
143 test frontend (21 del pannello), quattro E2E desktop/mobile con API simulate,
76 test backend pertinenti (14 nuovi) PASS; lint, build e Ruff PASS.
Log separati in backend/data/compilation-audit/retrieval-settings-ui-20261021-02/.
La revisione precedente e il relativo backup qui sotto restano storici e intatti.

## UX/UI ricerca nei documenti — 21 ottobre 2026

Intervento richiesto solo sulle impostazioni di ricerca, indipendente da V12,
V13, V14 e dal percorso sperimentale sottostante. Schermata riorganizzata in
metodo e riepilogo, configurazione tecnica richiudibile (embedding Ollama e
archivio Qdrant separati), manutenzione dell'indice distinta. «Locale» verificato
come Qdrant integrato nel backend; bge-m3 è un predefinito configurabile, non un
vincolo del backend. Chiavi password, azioni e stati espliciti, conservazione
delle configurazioni nascoste; nessuna indicizzazione al salvataggio.

Modificati solo pannello frontend, CSS dedicato, test UI e documentazione.
Backend, contratti, formato persistito, algoritmi, pipeline DOCX e snapshot
sperimentali non modificati. Nessuna chiamata LLM o operazione sull'indice live.
Verifiche: 138 test frontend PASS, inclusi 16 casi del pannello; quattro E2E
desktop/mobile con API simulate PASS; lint e build PASS. Test backend pertinenti:
35 PASS su dati temporanei. Esiti e preservazione sono registrati nel rapporto
[revisione UI ricerca](docs/revisione-ui-ricerca-2026-10-21.md) e nell'audit
backend/data/compilation-audit/retrieval-settings-ui-20261021-01/.
Tema chiaro verificato con token simulati: l'app non ha un selettore globale.
Le decisioni e i punti di ripresa V12/V13/V14 qui sotto restano invariati.
Nessun commit o push.

## Criteri di conclusione congelati — 21 ottobre 2026, 19:27 UTC

Approvati dall'utente e congelati prima delle prove V14: docs/criteri-conclusione-2026-10-21.md,
copia in sola lettura in benchmark ufficiale/criteri-conclusione-v1/ (SHA256 `f3ec66be…`).

Soglie:
- DOCX ≥ 4/5 per modulo compatibile e ≥ 90% sul totale;
- copertura del nucleo, mediana ≥ 70% per modulo sui DOCX esportati;
- zero scritture non dimostrate alla revisione indipendente (valore, soggetto, applicabilità,
  autorizzazione);
- nessuna conferma ridondante;
- ogni vuoto pertinente con motivo tracciato;
- almeno un modulo nuovo e una SOURCE in formato diverso, riportati separatamente;
- warning per valori invisibili nel PDF.

«Modulo compatibile» è definito da criteri tecnici di DOCX e parser, valutati prima delle
prove. La valutazione finale prevede 5 tentativi per modulo, tutti conteggiati. Sono soglie
sperimentali: se non sono raggiunte dopo gli interventi pianificati si documenta il limite,
senza sviluppo indefinito né aggiustamenti retroattivi. Percorso approvato: verifica V14 → P2 → P3 →
valutazione finale e congelamento.

## Candidata V14: autorizzazione delle clausole d'opzione — 21 ottobre 2026, sera

**Punto di ripresa: fermarsi.** Candidata V14 implementata e verificata offline, **non
adottata**. Spetta all'utente:
- valutarla, decidendo se accettare il costo su Cesano;
- decidere se misurarla con prove reali preregistrate;
- in seguito, passare a P2.

Baseline V12 e snapshot V13 invariati; nessun commit, tag o push.

V14 = V13/S1 congelata + `option_authorization_revision = 1` nelle sole nuove sessioni
(modulo nuovo `compilation_option_regions.py`; due file modificati:
`compilation_procedural_consent.py`, `compilation_global_sessions.py`; freeze di 121 hash).
Una regione d'opzione è il paragrafo con casella nativa o glifo, più la tabella adiacente
se l'opzione è nel corpo. Un valore in una regione richiede l'assenso esplicito alla
domanda del backend con la clausola integrale e i dati. Le ricevute di ramo o di scelta
non sbloccano mai; i FALSE di gruppo non vanno autorizzati.

Rischio verificato prima del codice: con V13 una sola ricevuta «è una società» esporta le
celle CCIAA in 21/21 prove CRAA, anche quando la domanda non citava l'attestazione; in V14
in 0/21. Il disegno R1T con sblocco U2 è stato corretto per questo.

Verifiche eseguite:
- T0 preregistrazione;
- T1, 16 test nuovi;
- T2, replay offline di 82 DOCX: rimosse solo 4 CCIAA e 9 `p19.ft0` Cesano, nessun'altra
  modifica, V13 rigenerato identico in 82/82;
- requisiti senza flag identici in 93/93 stati;
- T3, selezione: nessuna aggiunta;
- T4, 13 moduli: nessuna attribuzione in eccesso secondo la revisione dell'autore;
- T5, suite 3.380 PASS e Ruff PASS. Frontend non rieseguito.

Limiti: le 9 scritture Cesano (selezione di partecipazione) richiedono ora una domanda di
autorizzazione con costo di dialogo non misurato; seguiti in paragrafi successivi, «[ ]»,
U+F06F, `w:sym` e condizioni solo testuali restano scoperti; revisione non indipendente.

Rapporto: docs/v14-autorizzazione-clausole-opzione-2026-10-21.md. Grezzo:
backend/data/compilation-audit/v14-option-authorization-20261021-01/; backup
docs/benchmarks/2026-10-21-v14-option-authorization-audit.tar.gz (SHA256 `b740e151…`).

## Esperimento P1 e diagnosi CCIAA/R2 — 21 ottobre 2026, sera

**Punto di ripresa: fermarsi.** Nessun fix avviato. Spetta all'utente decidere se
implementare il veto d'export R1T proposto in docs/cciaa-r2-veto-opzioni-2026-10-21.md,
su quale profilo (baseline V12 adottata o candidata V13 non adottata) e con quale
revisione backend per le sole nuove sessioni. Prima del codice: preregistrazione T0 del
piano di test dello stesso documento. P2 viene dopo questo intervento di sicurezza.

Decisione dell'utente: accettata la revisione della priorità P1 alla luce
dell'esperimento offline A. La diagnosi P1 è falsificata in parte: con protocollo USER
corretto il dialogo attuale ottiene 262 scritture Minervino contro un tetto oracolo di
268. Raggruppare per decisione le condizioni LLM produce autorizzazioni improprie in
17/17 risposte nei casi controfattuali e non ferma le CCIAA. La «frammentazione»
indicata dalla revisione indipendente era sbagliata: le condizioni rilevanti sono 1–3
per risposta. Per le omissioni P2 ha il margine misurato più ampio (55 proposte corrette
respinte con V13, 147 con V12), ma il suo effetto non è ancora simulato.

CCIAA: soggetto corretto e valore citato dalla SOURCE (numero RI, lettura condivisa dal
gold Minervino), autorizzazione della dichiarazione «attività coerente con la classe
merceologica» mancante. I riferimenti V12/V13 hanno un solo campo
`applicability` (TRUE_IN_SCENARIO) senza dimensione di autorizzazione. I giudizi sono
coerenti: baseline LEGITIMATELY_OPEN, 18 prove V13 aperte dopo SKIP, 2 scritte senza
condizione. Gold, riferimenti e giudizi non modificati; separazione delle dimensioni
proposta solo per riferimenti futuri.

R2 non generalizza: struttura Word piatta (rientro 0, nessuna numerazione); figli senza
«:» (Minervino «☐ in caso di RTP», Calabria); contenuto condiviso dopo l'ultima opzione
(Soresa); marcatori «[ ]» e U+F06F non riconosciuti; condizioni solo testuali. Nucleo
proposto R1T (segmento più tabella adiacente, confine di cella), con sblocco solo da
ricevuta USER ancorata all'opzione: 4/4 CCIAA bloccate e 0 su 802 scritture corrette
bloccate sulle 82 prove esportate. Volutamente incompleto: figli nei paragrafi
successivi e condizioni testuali restano coperti solo dalle condizioni del modello.

Verifiche eseguite in questa sessione: script offline sui dati registrati; controllo
`find -newer` su V12, V13, 90 tentativi, backup, app, test, docs e dati (nessun file
preesistente modificato prima della scrittura dei nuovi documenti); due backup
verificabili, ciascuno estratto due volte con manifest, hash degli input e
riesecuzione degli script con output identici. Nessuna chiamata LLM, compilazione,
campagna E2E, test suite, migrazione, commit, tag o push. Suite e Ruff non rieseguiti:
codice applicativo invariato.

Limiti: un solo documento con gold e un solo scenario; annotazioni e revisione dei
moduli esterni dell'autore, non indipendenti; narratore non simulato; cattura delle
decisioni assunta perfetta; sette moduli esterni senza riferimento.

Rapporti: docs/p1-esperimento-offline-a-2026-10-21.md e
docs/cciaa-r2-veto-opzioni-2026-10-21.md. Grezzi (esclusi da Git, con backup in
docs/benchmarks/2026-10-21-p1-offline-a-audit.tar.gz e
docs/benchmarks/2026-10-21-cciaa-r2-diagnosi-audit.tar.gz):
backend/data/compilation-audit/p1-offline-a-20261021-01/ e
backend/data/compilation-audit/cciaa-r2-diagnosi-20261021-01/.

## V13 S1 — campagne concluse, candidata non adottata — 21 ottobre 2026

**Punto di ripresa: fermarsi.** Nessun fix avviato. Spetta all'utente decidere
sulla candidata V13/S1: adottarla come nuova baseline sperimentale conservativa,
dichiarando il limite CCIAA ereditato, oppure mantenere la V12 e affrontare prima,
in un intervento separato preregistrato, il controllo di applicabilità FORM.
Rapporto conclusivo: docs/v13-s1-omissioni-fattuali-2026-10-21.md; consegna:
benchmark ufficiale/v13-s1-20261021-01/README.md.

Ripresa dopo l'interruzione di Codex. Erano già completi campagne, revisione
documentale, replay appaiati, codice before/ eseguito, fallimenti e preservazione
delle 19:31. Mancavano otto PDF della coorte 2, perché il render si era fermato
su craa-03, poi aggregato PDF, confronto finale e backup (backup.py scritto ma
non eseguito), oltre a rapporto e STATUS. Chiusi senza compilazioni né chiamate
LLM, senza modifiche a codice, prompt, test, validatori, DB live o sessioni.
Nessun commit, tag o push.

Esiti: **90 tentativi, 79 DOCX, 11 senza DOCX**. Coorte 1: 41/4, 217 testi.
Coorte 2, con protocollo USER corretto dopo la coorte 1: 38/7, 526 testi e tre
checkbox USER. Fallimenti: quattro troncamenti globali, tre JSON non validi, tre
narratori troncati al primo turno, prima di risposte USER alle domande, e un
dialogo Minervino bloccato. Minervino senza DOCX in 2/10 e 6/10 tentativi.

Codice, a parità di risposta e ricevute: V12 → V13 98 → 217 e 407 → 526, cioè
**238 aggiunte corrette, zero rimozioni o cambi**, checkbox identiche. 233 vengono
dalla selezione USER esplicita del firmatario, quattro dai record DT e una dalla
continuità dell'operatore. Fra le coorti, a parità di codice, l'aumento è
soprattutto del protocollo: con codice V12 98 → 407. Sulle 17 destinazioni
baseline la V13 scrive 55/138 e 58/74 opportunità, di cui 45 e 37 per il codice.

**Quattro scritture CCIAA non dimostrate** in craa-03/04 della coorte 2:
provincia «Bari» e numero di iscrizione. Il modello omette la condizione
societaria, presente nelle altre 18 risposte CRAA. Il backend accetta le prove
locali e il codice V12 scrive gli stessi valori: non sono effetto di S1 o del
protocollo. Nelle celle da 66 e 81 twip il numero non si vede: due PDF FAIL su 79.
Restano 62 e 56 omissioni ingiustificate (Catanzaro senza proposta MODEL,
rifiuti Minervino) e il gruppo checkbox Cesano non viene mai scritto.

Verifiche eseguite in questa chiusura: rendering offline di otto DOCX con il
renderer V12 congelato (render_remaining.py) e pdf_final.py invariato. Risultato:
79 PDF, 553 pagine, 77 PASS_WITH_LIMITS e due FAIL. I 14.763 file preesistenti
delle consegne V13/V12 restano identici. Confronto finale
CONFRONTO-FINALE-V12-V13.json da soli JSON registrati.

Backup: audit-completo.tar.gz, 828.506.206 byte, SHA256 75d60b93a607462642e23c3c275e0ef8a16c1b2bde5365e622e9142bb4b42cbc,
con 14.091 file. VERIFICA-BACKUP.json PASS: estrazione indipendente, 120 hash,
replay offline 41+38 DOCX esatti, misure identiche, credenziali assenti. Scansione
aggiuntiva dei membri ZIP PASS. Addendum documentale con CONSEGNA-MANIFEST.json.
120/120 hash applicativi uguali al congelamento. Suite 3.364 PASS storica, non
rieseguita perché il codice è invariato.

Limiti: revisione autoriale non indipendente, SOURCE sintetiche, riferimento
non gold. La correzione del protocollo è stata decisa dopo la coorte 1. Budget
USER 4 contro 2 della V12. Ricevute appaiate nate in dialoghi V13. Nessuna
percentuale di accuratezza.
L'archivio da 828 MB è in benchmark ufficiale/, che Git non ignora: non
aggiungerlo a un commit senza decisione. Grezzi: backend/data/compilation-audit/
v13-s1-20261021-01/ e v13-s1-validation-20261021-02/.

## V13 S1 — stato intermedio delle 18:41 (superato dalla sezione precedente)

Richiesta corrente: ridurre le 17 omissioni fattuali della baseline senza nuove
scritture indebite; almeno 100 casi mirati, suite completa, regressioni e poi
45 nuove compilazioni reali (10 Minervino/Cesano/CRAA, cinque Trapani/Catanzaro/Bella).
Nessuna adozione automatica, commit/tag/push; nessun intervento indipendente.

Snapshot recuperabile dello stato effettivo dopo la neutralizzazione del nome:
benchmark ufficiale/v13-s1-20261021-01/before/, 323 file, 13.204 file preesistenti
protetti. DB live e storage fotografati; snapshot e backup V12 intatti.
Suite prima della modifica: **3.180 PASS in 255,06 s**.

Diagnosi causale prima del codice riprodotta esattamente con rete/SQLite vietati:
DIAGNOSI-17-PRIMA.json nella consegna. Nove binding firmatario citano il paragrafo
sbagliato; il riuso non riconosce «scelto per questa domanda». Sei proprietà DT
non coperte dal collegamento tipizzato esistente o dai suoi alias. Un dato sede
è respinto perché il gate scambia una proposta societaria condizionata grounded
per un operatore non verificato. Nome CRAA non proposto, dentro una cella inline
non riconosciuta dal riuso. Nessuna SOURCE fattuale mancante nei 17 casi.

Prima implementazione: nuove sessioni con backend_revision=13, mantenendo il
contratto MODEL versione 12 e il prompt globale B0. Riutilizzati SOURCE reuse,
catalogo e validatori; collegamenti con identità/ruolo/proprietà verificabili,
nessuna composizione di valori né modifica alle condizioni UNKNOWN. Sessioni
precedenti senza revisione conservano V12. Primo confronto sugli stessi output:
17/17 ora validabili; sette trasferimenti Cesano ancora respinti. Validabilità
non equivale ad autorizzazione/export: i vincoli conversazionali restano.

Test finali: **3.364 PASS in 281,92 s**, Ruff PASS; **184 nuovi casi** (154 unitari,
30 API FTS5/Qdrant). Log intermedi conservati, inclusi due rifiuti della prima
suite completa: intestazione condizionale aggirata dal riconoscimento inline e
catalogo incompleto. Entrambi corretti prima del congelamento, aggiunti tre
controesempi condizionali. 69 replay legacy e 69 con profilo V13 conservano tutti
i DOCX; 213 validator storici identici. Sette rifiuti Cesano conservati.
Sulle tre risposte baseline, 17 proposte diventano SOURCE-validabili ma i DOCX
restano identici con le vecchie ricevute di revisione/autorizzazione.

Candidata congelata con 120 hash in candidate-code/ e PROTOCOLLO.json della
consegna; B0/modello/parametri invariati. **Campagna reale avviata il 21 ottobre
alle 16:04 UTC**, 45 tentativi preregistrati su clone privato, sei contesti browser
isolati, nessuna modifica applicativa o retry selettivo. Massimo quattro risposte
USER per prova (V12: due): confronto indipendente non causale; previsto replay
appaiato sulle stesse risposte. POLICY USER congelata prima delle inferenze.
Prima campagna conclusa: **45 tentativi, 41 DOCX, quattro fallimenti** (due
troncamenti Minervino, JSON non valido Cesano/Catanzaro), nessun retry sostitutivo.
217 testi (216 SOURCE/uno USER), zero booleani; revisione documentale di 103
combinazioni distinte, zero scritture non dimostrate osservate. 455 chiamate,
5.752.241 token, 1,209172224 USD stimati. Replay appaiato su 41 risposte/ricevute:
98→217 testi, 119 aggiunte corrette, nessuna rimozione/cambio/checkbox; risultati
V12 verificati anche eseguendo davvero il codice before/. 194 prove recuperate.

**Errore nel protocollo USER della prima campagna:** «senza raggruppamenti o
consorzi» attiva has_user_alternatives; la policy rinvia inoltre «dell’impresa»
e «di partecipare … come» benché lo scenario scelga già società/partecipazione.
Questo limita i conteggi E2E: non attribuire i molti vuoti automaticamente a S1.
Prima campagna interamente conservata. Per completare una verifica utilizzabile,
avviata una **seconda campagna completa di 45**, non selezione dei casi peggiori,
in v13-s1-validation-20261021-02. Stessi 120 hash, B0/modello/SOURCE/FORM/scenari
e budget; cambiano solo formulazioni e riconoscimento delle scelte USER già
preregistrate. Policy verificata prima delle inferenze su 58 contesti; prima
preflight aveva ancora una disgiunzione in un’etichetta di opzione, corretta
prima di qualunque chiamata e protocollo originario conservato. Nessun dato
fattuale nuovo o attestazione, nessuna modifica applicativa.

Seconda campagna in corso su clone separato, servizi 8002/5175; primi quattro
export 17 testi Trapani, sette Bella, quattro Cesano e otto CRAA. Restano tutte
le altre prove, revisione, confronti delle due coorti tenuti separati e backup
finale verificato. Servizi prima coorte arrestati, DB live verificato invariato.
Campagne autonome in campaign.cjs; progresso campaign.log/campaign-progress.json.
Nessuna adozione della V13. Grezzo e script prima coorte:
backend/data/compilation-audit/v13-s1-20261021-01/.
Seconda: backend/data/compilation-audit/v13-s1-validation-20261021-02/.

## Nome neutro nell’applicazione — 21 ottobre 2026

Rimosso il nome del progetto dall’interfaccia su richiesta dell’utente:
scheda e applicazione «Assistente documentale», messaggi «Risposta», composer
«Messaggio per l’assistente». Aggiornati navigazione, profilo, testi di aiuto,
demo, titolo API, etichetta di accesso OpenRouter e metadati dei pacchetti.
Le presentazioni nei prompt di chat/router sono ora generiche; prompt globale
B0, catalogo, validatori e writer non cambiano. Documenti, nomi dei file e dati
aziendali nelle fonti conservati. Identificatori di storage/cache e variabili
MAPI_* restano compatibili con i dati precedenti.

Verifiche: 126 test frontend, 232 test backend mirati, quattro E2E con API
simulate desktop/mobile PASS; lint frontend, build, Ruff e sintassi shell PASS.
Verificati nel browser titolo, navigazione, composer e demo; zero chiamate LLM.
La prima ispezione aggiuntiva assumeva erroneamente il pulsante del drawer anche
su mobile: corretto solo lo script di verifica, senza cambiare la navigazione.

La baseline sperimentale adottata resta nello snapshot e nei backup originali,
immutati. Questa successiva ridenominazione del codice corrente non riscrive i
119 hash della baseline e rende il working tree diverso dal riferimento congelato.
Audit: backend/data/compilation-audit/ui-neutral-naming-20261021-01/;
riepilogo e backup separato in docs/benchmarks/2026-10-21-ui-neutral-naming*.
Nessun commit o push.

## Baseline V12 adottata per confronti sperimentali — 21 ottobre 2026

**Decisione esplicita dell'utente: adottata la V12 corrente come baseline
sperimentale conservativa per compilazione assistita di bozze DOCX parziali,
con revisione umana obbligatoria.** Non definitiva/completa, non pronta per
pratiche ufficiali senza verifica. Manifesto: [BASELINE-V12.md](BASELINE-V12.md).
ID documentale V12-B0-conservativa-20261021, stato
ADOPTED_FOR_EXPERIMENTAL_COMPARISONS nel candidato aggiornato; proposta originale,
rapporto e archivio preesistenti conservati con cronologia esplicita.

Identità: snapshot e patch locali, 119 hash applicativi invariati, configurazione,
prompt/parametri B0, modello, SOURCE, FORM, scenari e criteri già preregistrati.
HEAD da solo non basta. I tre riferimenti sono Minervino/Cesano/CRAA: 54 testi e
sei booleani, zero scritture non dimostrate osservate nella revisione autoriale;
17 omissioni fattuali, una checkbox omessa, un campo fermo per budget del dialogo.
28 chiamate/397.982 token e 0,086193018 USD stimati appartengono alle prove
precedenti, non a questa formalizzazione. Minervino storico 61 = 60 testi più
una checkbox con proposta congelata; nuova prova indipendente 43 testi, zero
checkbox: protocolli diversi, nessuna regressione causale 61→43 dimostrata.

Restano variabilità LLM, corpus sintetico, una prova per documento, revisione non
indipendente, grammatica FORM limitata, assenza di composizione multi-SOURCE,
copertura incompleta di checkbox e record distribuiti. Non correggere ora le
omissioni. Verificati riferimenti, 119 hash e backup originale; addendum solo
documentale. Nessuna nuova compilazione/export/LLM o modifica a codice, prompt,
test, DB live e sessioni storiche. Nessun commit, tag o push. **Fermarsi qui.**

Le sezioni seguenti registrano la proposta e il lavoro precedenti, non lo stato
corrente di adozione. Verifiche e preservazione in
[ADOZIONE-VERIFICHE.json](<benchmark ufficiale/baseline-v12-20261021-01/ADOZIONE-VERIFICHE.json>).


## Valutazione candidata baseline V12 — tre prove reali del 21 ottobre

[Rapporto comparativo](docs/valutazione-baseline-v12-2026-10-21.md),
[tre DOCX/PDF e riproduzione](<benchmark ufficiale/baseline-v12-20261021-01/README.md>).

Tre documenti preregistrati: Minervino inline, Cesano FORMTEXT/checkbox, CRAA
con tabelle estratto una sola volta dal pool residuo. Tre nuove sessioni e
proposte globali reali DeepSeek, percorso chat/export/download ordinario,
nessun riuso di risposte congelate o retry selettivo. SOURCE e scenari fissati
prima delle inferenze, massimo due risposte agli slot per pratica: 2/2/1.
**119 file applicativi invariati**: nessuna modifica al fix dei valori composti,
né a prompt, B0, modello, parser, writer o protezioni. Working tree preesistente
preservato: HEAD da solo non identifica questa versione.

Esportati 43/4/7 testi: **54 testi (53 SOURCE, uno USER)** e sei booleani USER
Cesano di un solo gruppo (uno TRUE, cinque FALSE). Revisione documentale per
ogni scrittura: zero non dimostrate osservate. Classificate tutte le 406
destinazioni: 17 omissioni fattuali, una scelta USER omessa, un campo aperto
per budget dialogo; 177 legittimamente aperti, 148 non applicabili e due ambigui.
Nucleo preregistrato 74 fatti: 54 scritti, 17 omissioni, uno fermo per dialogo,
due per attestazione esplicitamente rinviata. Sette trasferimenti azienda→persona
proposti dal modello Cesano sono respinti, senza scritture indebite.

28 chiamate reali, tre globali, **397.982 token**, costo a tariffa stimato
**0,086193018 USD** (non fattura). Audit/export e download ricostruiti esatti
senza rete/SQLite; integrità DOCX e 19 pagine PDF leggibili. Nessun nuovo
positivo numero+data o scrittura tabellare fattuale autorizzata in questo pannello:
non attribuire a queste tre prove una copertura che non hanno. Suite precedente
3.180 PASS/Ruff PASS non rieseguita; codice identico al precedente verificato.

**Proposta PROPOSED_NOT_ADOPTED:** congelabile come riferimento sperimentale
conservativo per bozze parziali, non come compilatore completo o versione
definitiva. Firmatario omesso, record DT incompleto, checkbox Minervino e
conferme ripetute restano limiti bloccanti per uso senza revisione. Grammatica
FORM limitata e nessuna composizione multi-SOURCE restano invariati. Una prova
per documento, SOURCE sintetiche e revisione autoriale non misurano accuratezza
generale o variabilità. L'adozione resta da decidere: **fermarsi qui**, nessun
intervento successivo, commit o push. Servizi di prova arrestati; preservazione
e backup con estrazione e tre ricostruzioni offline nei JSON della consegna.


## Completezza valori composti V12 — intervento del 21 ottobre

[Rapporto](docs/completezza-valori-composti-v12-2026-10-21.md),
[consegna e riproduzione](<benchmark ufficiale/compound-values-20261021-01/README.md>).

Riprodotta prima del codice la scrittura UI congelata `t25.r3.c1`: FORM p441
richiede numero e data, SOURCE -52 dimostra soltanto il numero proposto.
Il grounding era corretto ma mancava la sufficienza del valore per il campo.
Nuovo controllo backend `value_completeness` COMPLETE/INCOMPLETE/UNKNOWN,
ancorato a FORM e destinazione, con componenti e provenienza. Veto distinto
su revisione, dialogo, selezioni persistite e ricalcolo prima dell'export.
Ricalcolo dopo il riuso SOURCE esistente; nessun nuovo valore sintetizzato.
Contratto letterale, prompt, modello B0, FORM, parser e writer invariati;
applicabilità, ruoli e autorizzazioni restano indipendenti. Nessuna E1/E2 integrata.

132 nuovi test permanenti (98 unitari, 34 API FTS5/Qdrant) e fixture originale.
Baseline 3.048 PASS; suite finale **3.180 PASS in 287,83s**, Ruff PASS.
69 replay export: 56 DOCX identici, 13 con sole 15 esclusioni preregistrate:
cinque numeri senza data e dieci telefoni sotto «Cellulare + Telefono» UNKNOWN.
Nessun altro valore, posizione o checkbox cambia; Minervino, Trapani, Bella,
Cesano e CRAA conservati. Audit uguali salvo la nuova dimensione.
213 validator V2–V12: 207 validati e sei rifiuti precedenti conservati.
XML/CRC/geometria/controlli verificati; 31 PDF storici prima/dopo leggibili.
Inventario: nove originali distinti, 159 requisiti riconosciuti; nei replay 160
proposte interessate, 118 COMPLETE, sei INCOMPLETE, 36 UNKNOWN; nessuna pretesa
che i 1.312 controlli senza proposta dimostrino assenza nelle SOURCE.

E2E reale su clone isolato: sessione `e81df1cca6b34606a923857c5605d325`,
progetto `completezza-valori-catanzaro`, versione finale 8 GENERATED, una globale reale
118,06s, otto chiamate totali, 155.285 token, nessun retry. Scenario preregistrato,
22 SOURCE e FORM/prompt/parametri B0 uguali. Due ricevute confermano soltanto i
rami societari già scelti; MODEL condizioni ancora UNKNOWN. Export/download
ordinari: 16 valori SOURCE, zero USER/checkbox; DOCX ricostruito esattamente,
PDF 17 pagine e campioni p2/p11/p17 leggibili. Dieci GET abortite per acquisizione browser (20 totali),
zero POST/console/driver/provider fallite. Servizi arrestati. Dopo la prima UI, quattro casi di maiuscole nei qualificatori
hanno motivato due sole opzioni re.I; risposta reale acquisita invariata,
regressione finale 3.180 PASS e nuovo export UI ordinario sulla stessa analisi,
senza seconda globale. Codice e acquisizioni di entrambi i passaggi conservati.

La nuova risposta omette numero/data: **zero nuove proposte parziali intercettate
in questa singola E2E**. Confronto stessi MODEL/USER sul nuovo output: 16→16.
Prova causale sull'output reale originale congelato: **17→15**, numero incompleto
rimosso e telefono ambiguo escluso; non attribuire al backend l'omissione MODEL.

Grammatica FORM limitata alle famiglie dichiarate, non comprensione universale.
Composizione multi-span non implementata: richiederebbe un contratto coordinato
con provenienza per componente e chiave SOURCE del record, proposto nel rapporto
senza implementarlo. Proposte complete restano soggette agli altri gate; nessuna
correzione indipendente a narratore, ruoli, preferenze o copertura del modello.
Sessioni V12 senza il controllo richiedono nuova analisi per i campi composti,
senza migrazione implicita; versioni storiche conservate. Backup e verifica
estratta offline nei manifest della consegna; DB live e sessioni/storage
precedenti protetti. Nessun commit o push.

## Relazioni tabellari FORM V12 — intervento concluso del 20 ottobre

[Rapporto](docs/relazioni-tabellari-form-v12-2026-10-20.md),
[consegna e backup](<benchmark ufficiale/table-form-links-20261020-01/README.md>).
Nuova richiesta esplicita successiva all'applicabilità: supporto generale delle
relazioni etichetta–valore nelle tabelle, preservando il veto già verificato.

Riprodotte prima del codice tutte le 13 barriere Catanzaro e il controesempio
CCIAA p439 → t25.r2.c0/p440 vuoto. Nuovo `compilation_table_form.py`: archi
backend da griglia XML originale e ID del catalogo, coppie adiacenti univoche,
righe precedenti, prima riga senza tblHeader, paragrafi multipli e unioni con
copertura/estensione univoca. Tabelle annidate isolate; ambiguità senza arco.
13/13 legami del riferimento ora dimostrati, zero ambiguità fisiche fra essi;
nessuna pretesa che 13 valori abbiano SOURCE, ruolo o autorizzazione sufficienti.
Il nuovo arco non estende il contesto di ruolo; coerenza SOURCE della riga e
autorizzazione delle dichiarazioni restano gate distinti. Applicabilità legge
anche le nuove etichette: FALSE/UNKNOWN vietano la scrittura. Scope delle
condizioni conservato separatamente dalle prove della proprietà.

Modifiche: nuovo modulo, integrazione in compilation_global, contesto della
revisione in global_sessions, contesti verificati in form_applicability;
52 test permanenti (40 unitari e 12 API temporanee FTS5/Qdrant) e fixture.
Suite backend finale 3.048 PASS in 234,16s; Ruff PASS. Prima suite 2 FAIL/3.028
PASS su celle a underscore, corretta riusando il parser. Primo replay CRAA
negativo per restringimento dello scope, corretto e coperto da test permanente.
Acquisizioni e fallimenti conservati nel nuovo grezzo.

68 replay di export PASS, tutti i DOCX identici byte per byte alla baseline
corrente, comprese le 61 scritture Minervino e le 17 Trapani; anche Bella,
Cesano, CRAA e Catanzaro invariati. B0-3/E1-3 rimangono 6/8 testi e sede
operativa vuota. 213 confronti dei validator V2–V12: 207 validazioni e 6 rifiuti
root pregressi, 199 risultati esatti e 14 con nuovi archi, nessuna perdita
grounded, fatti/binding/verità MODEL invariati. Sono confronti deterministici,
non 213 export completi o nuove inferenze. 29 occorrenze di proposta ora
grounded nei 68 replay, su tre destinazioni distinte; 17 nelle nove repliche
Catanzaro dello studio. Le 21 promozioni nel protocollo validator si
sovrappongono e non vanno sommate. Nessuna revisione USER/narratore inventata.

Una sola prova UI reale dopo la regressione: sessione
`343d6caf16d442ed88ef174ebaf4aae0`, conv `conv-3824c2d370f143e4`, v7 GENERATED,
clone isolato. Modello/prompt/FORM/SOURCE/parametri invariati, 69 moduli
applicativi congelati. Un turno USER ripete solo società/firmatario già
preregistrati; export e download ordinari. 26 proposte, 18 grounded anche
condizionate, una vietata da FALSE; 17 testi SOURCE, zero USER/checkbox scritti.
Dei 13 campi, 7 proposti: CCIAA Bari scritta, 6 bloccati da altre prove; 6
omessi. Sulla stessa nuova risposta e ricevute il vecchio backend scrive 16:
unica aggiunta causale Bari in t25.r2.c0, altri sedici conservati. DOCX/audit/
download ricostruiti esattamente offline. Rimane il solo numero senza data in
t25.r3.c1, problema indipendente noto; 17 non significa 17 risposte complete.

XML/CRC/posizioni/struttura/checkbox verificati su tutti gli export. Otto PDF
storici (sei famiglie) e il reale PASS: valori osservati, zero parole fuori
pagina, ispezioni campionate. Reale 17 pagine, CCIAA leggibile a p11 e ramo
sede operativa vuoto a p2. Nessuna prova Word desktop. Sette chiamate reali,
una globale 146,30s, 156.322 token, stesso fingerprint dello studio, nessun
retry. Dieci GET abortite al mount/reload, nessuna POST/provider/console fallita.

Snapshot prima/dopo, replay separati, protocollo, trace/video/audit in
`benchmark ufficiale/table-form-links-20261020-01/` e
`backend/data/compilation-audit/table-form-links-20261020-01/`.
Manifest di preservazione e verifica del backup estratto nella consegna;
DB/chiavi/env privati esclusi. 29 sessioni/273 file live e DB logico intatti,
38 sessioni/490 file precedenti del clone conservati, una nuova. Servizi
isolati arrestati. Nessuna migrazione/reindicizzazione/commit/push.

Limiti: schemi non univoci restano senza prova; equivalenze di ruolo e date,
valori composti, decisioni USER e narratore non corretti. Dichiarazioni
tabellari senza flusso USER supportato restano bloccate. Nessuna nuova pipeline,
integrazione E1/E2, modifica di modello/prompt globale, writer o frontend;
input LLM invariato, nessun obbligo al modello di proporre i campi recuperati.
Sessioni vecchie leggibili senza upgrade implicito. Punto di ripresa: questa
fase tabellare è chiusa nel perimetro dimostrato; altri interventi richiedono
una nuova richiesta. Le sezioni seguenti conservano gli esiti precedenti.

## Applicabilità locale FORM V12 — intervento del 20 ottobre

[Rapporto](docs/applicabilita-form-v12-2026-10-20.md),
[consegna e backup](<benchmark ufficiale/form-applicability-20261020-01/README.md>).
Unico intervento autorizzato dopo lo studio: impedire l'indirizzo nel ramo
«Sede operativa, se diversa dalla sede legale». B0 globale resta riferimento;
E1/E2-A non integrati, nessun cambio di rappresentazione FORM/modello/provider.

Riprodotti i due output originali Catanzaro B0-3/E1-3: condizioni MODEL omesse,
valore SOURCE vero e ancore p34/p35 già nella stessa cella etichetta. Aggiunto
`compilation_form_applicability.py`: comparazioni locali di uguaglianza/diversità,
negazioni e ramo complementare ancorati al FORM; prove SOURCE esplicitamente
attribuite allo stesso soggetto. Valori identici provano coincidenza; stringhe
diverse non provano diversità. Prove insufficienti, conflitti e ambiguità restano
UNKNOWN. Separati fatto grounded, predicato FORM e assenso USER. Veto di FALSE e
UNKNOWN in vista/chat, API ed export rivalutato, anche per valori USER/cache
obsolete. Proposte/fatti/condizioni MODEL non riscritti, nessun RESOLVED automatico.

91 test nuovi; 2.996 backend PASS 281,80 s, Ruff PASS. Prima suite negativa
13 FAIL/2.980 PASS per cataloghi ridotti dei test di revisione, corretta nel
solo nuovo controllo; 107 mirati PASS. 67 replay di export: 65 DOCX esatti,
solo due delta previsti, B0-3 7→6 ed E1-3 9→8, esclusivamente `t0.r8.c1` vuota;
Minervino 61 e Trapani 17 conservati. 213 ulteriori confronti di validatori
V2–V12, incluso Labirinto: 207 validazioni/sei rifiuti pregressi esatti tolta
la nuova dimensione FORM. Non sono nuove inferenze o valutazioni di qualità.

Una sola sessione UI reale isolata `196e0ac512b0410e9b7d71cea6cf04a8`, versione7
GENERATED: il modello ripete value/conditions=[] sulla sede; backend FALSE,
nessuna scrittura lì. 18 proposte, 16 grounded, 15 testi SOURCE scritti, zero
USER/checkbox. Un turno USER conferma solo il ramo societario già scelto;
export esplicito successivo e download ricostruiti esattamente offline.
Resta il problema indipendente noto del solo numero senza data in `t25.r3.c1`:
non corretto, 15 non equivale a 15 risposte complete. Nessun nuovo potere o esecutore.

XML/posizioni/CRC/tabelle/prestampato verificati; PDF dei due prima/dopo e del
reale:17 pagine, valori leggibili,0 parole fuori pagina; ispezione campionata,
non Word desktop.7 chiamate reali,1 globale,150.364 token,122,05s globale;
stesso deepseek-flash enabled/low e fingerprint dello studio. Nessun retry.
Dieci GET abortite al mount/reload; nessuna POST/console/provider fallita.

68 hash applicativi finali congelati, originali e working tree preservati.
29 sessioni e 273 file storage live intatti, DB interamente logicamente identico;
38 sessioni/490 file del clone precedenti conservati, una nuova. Grezzi sotto
`backend/data/compilation-audit/form-applicability-20261020-01/`; codice prima/dopo,
replay e audit nel backup separato. Esito della ricostruzione dal pacchetto
estratto in `VERIFICA-BACKUP.json`; niente chiavi/DB privati/env nel pacchetto.
Servizi isolati arrestati. Nessuna migrazione/reindicizzazione/commit/push.

Limiti: grammatica locale supportata, non tutte le condizioni naturali o i
rinvii remoti. UNKNOWN bloccati, nessun nuovo assenso USER sostitutivo. Sessioni
V12 pregresse prive del controllo restano leggibili, senza upgrade implicito;
le destinazioni comparative richiedono nuova analisi/nuova sessione per essere
autorizzate. I 13 collegamenti tabellari e gli altri problemi restano intatti.
Punto di ripresa: intervento di applicabilità verificato nel perimetro dichiarato;
arresto alla consegna, nessun avvio del successivo lavoro tabellare.

## Indagine architetturale V12 / E1 / E2-A — conclusa, 20 ottobre

Richiesta conclusa: confronto controllato della globale B0, del FORM compatto E1
e dell'analisi circoscritta E2-A. Nessuna variante integrata; nessuna correzione
applicativa, commit o push. Arresto alla consegna: i problemi emersi sono diagnosi
e proposte per una fase separata, non autorizzazioni a implementarli.

[Rapporto completo](docs/diagnosi-architetturale-v12-2026-10-20.md),
[indice di tutte le repliche e DOCX/PDF](<benchmark ufficiale/diagnosi-architetturale-v12-20261020/README.md>),
[esito strutturato](docs/benchmarks/2026-10-20-architecture-diagnosis.json).

Consegna e codice sperimentale: `benchmark ufficiale/diagnosi-architetturale-v12-20261020/`.
Acquisizioni/log: `backend/data/compilation-audit/diagnosi-architetturale-v12-20261020/`.
Snapshot applicativo e test nel primo percorso, configurazione privata esclusa
dagli artefatti in `.tools/diagnosi-architetturale-v12-20261020/`.
HEAD 99ab052 con working tree preservato: manifest degli hash, non soltanto Git.
Nuova verifica baseline: 2.905 PASS in 225,54 s; 23 audit/DOCX esatti, Minervino61.
29 test sperimentali PASS in 0,24 s su proiezioni, ambiti, merge ed equivalenze;
tre test diagnostici PASS in 0,88 s sulle barriere FORM dimostrate.

Protocollo preregistrato prima delle chiamate: 4 documenti, 3 repliche indipendenti
per ciascuna variante, 36 confronti e 57 chiamate di analisi reali (24 globali,
33 locali). Deepseek-flash, thinking enabled/low, temperatura 0,1 e limite 49.152
invariati. Nessun retry di qualità o riparazione degli output. Ordine bilanciato
con seed 20261020, due chiamate concorrenti. SOURCE: 22 chunk identici alla KB live,
4 originali e hash archiviati. Scenario sintetico distinto per ogni procedura,
stesse decisioni iniziali nelle tre varianti, senza nuove attestazioni.

Riferimento fissato prima delle risposte: 60/17/31/8 occorrenze SOURCE rispettivamente
Minervino/Trapani/Catanzaro/Bella, 116 totali; censite tutte le 756 destinazioni.
GOLD e valori attesi esclusi dai prompt. E1 riusa la proiezione sperimentale con
indice diretto, senza integrazione. E2-A partiziona le destinazioni in sezioni
coerenti e conserva TUTTI i blocks come contesto esterno; non misura ancora
la riduzione del contesto globale. Test: nessuna tabella/unità condivisa spezzata.

Completate 57 analisi e 42 revisioni reali del narratore: 99 chiamate, 4.743.461
token, 0,931729 USD stimati (non fattura). Stesso fingerprint in tutte le risposte.
Nessun retry. Un narratore Minervino B0 troncato a 2.048 token: copia vuota,
fallimento operativo conservato. Nessun fallimento root delle 57 analisi.
È un harness isolato con stato JSON, non una nuova prova UI: checkpoint dopo
le indicazioni iniziali e prima di ulteriori risposte USER, senza ricevute inventate.
I conteggi non sostituiscono le 61 scritture dopo dialogo del precedente Minervino.

Su 348 occorrenze valutate per variante, proposte semanticamente corrette:
B0 282, E1 278, E2-A 296; corrette grounded prima del riuso: 198 / 135 / 201;
dopo il riuso: 262 / 199 / 265; scritture conformi: 54 / 88 / 52.
Le differenze nelle condizioni impediscono di usare il solo conteggio DOCX come
misura della qualità dell'analisi. E1 riduce input del 9,5% ma aumenta il costo
di analisi del 6,9%; E2-A costa il 57,2% in più. Nessun vantaggio globale robusto.
E2-A: segnale locale Catanzaro (13 grounded in tutte le repliche contro 9/13/8),
senza recupero stabile di omissioni presenti in tutte e tre le B0.

Cause dimostrate: 13 destinazioni Catanzaro prive di prova FORM locale utilizzabile;
sei falsi conflitti di date, due di provincia, quattro perdite per ownership
condizionale; 113 omissioni con input disponibile fuori dalla barriera FORM;
errori di prove e condizioni del modello. Due scope E1 Minervino inventano ID
inesistenti e bloccano 41 campi ciascuno. Nessuna riparazione eseguita.
Due SCRITTURE INDEBITE Catanzaro B0/E1 replica 3: sede operativa compilata benché
il FORM la richieda soltanto se diversa e SOURCE la dichiari coincidente.
Predicato omesso dal modello e non rilevato a valle: priorità di sicurezza per
un intervento distinto. Le otto proposte PEC Trapani senza assenso restano bloccate.

36 DOCX/PDF nuovi: 14 copie senza valori (una per errore del narratore), 22 non
vuote; due di queste con errore di ramo. 196 scritture SOURCE, 194 conformi;
nessuna scrittura USER o checkbox. XML/posizioni verificati; tutti i valori
osservabili nel PDF, sette pagine ispezionate visivamente, non tutte le pagine.
36 DOCX e 72 audit ricostruiti esattamente offline, vietando rete/SQLite.
Backup separato e verifica dal pacchetto estratto nella consegna; nessuna chiave,
database privato o .env incluso. Preservati 1.560 altri file protetti, 29 sessioni,
285 file storage, l'intero DB live logicamente e i 67 moduli applicativi.

Conclusione: causalità della sola lunghezza JSON NON DIMOSTRATA. Mantenere B0
come controllo sperimentale; non adottare E1/E2 né dichiarare V12 baseline
affidabile. Proposte da discutere: predicati FORM locali, relazioni tabellari,
ownership separata dall'applicabilità, equivalenze documentate, budget narratore.
Nessun refactor, nuovo agente/framework, migrazione o reindicizzazione.

## CRAA: motivazione MODEL troppo lunga — concluso il 20 ottobre

[Rapporto](docs/craa-motivazione-model-2026-10-20.md),
[controlli](docs/benchmarks/2026-10-20-model-reason-checks.json),
[consegna](<benchmark ufficiale/craa-model-reason-20261020-01/README.md>).

Diagnosi offline del caso storico: il solo `reason` da 225 caratteri, contro
200 nel contratto, escludeva un chiarimento altrimenti valido per il nominativo
del sottoscrittore. Controfattuale a un solo fattore e cinque transizioni
persistite: richiesta recuperabile nel pool, senza alterare le ricevute USER.
Non risulta cancellata una decisione già accettata. Il nome compare in tre
messaggi USER originali: il suo mancato collegamento rimane un problema distinto.
Le due risposte salvate del narratore, rieseguite esattamente, non scelgono la
domanda recuperata; nessuna nuova domanda reale o scrittura DOCX dimostrata.

Correzione generale circoscritta a `compilation_user_requests.py`: per il solo
metadato descrittivo stringa non vuota oltre il limite, nota operativa neutra e
warning osservabile; testo integrale invariato in `proposal.reason` e nel grezzo.
Schema 200, budget globale, prompt, FORM, grounding, condizioni, API, database,
writer e narratore invariati. Tipi errati e altri vincoli continuano a respingere.
Un chiarimento accettato rende disponibile una domanda, senza autorizzare valori,
applicabilità o checkbox. Nessun aggiornamento implicito delle vecchie sessioni.

28 nuovi test permanenti, incluse due sessioni FTS5/Qdrant con provider simulati;
101 mirati PASS in 14,32 s; 2.905 backend PASS in 225,72 s; Ruff PASS.
23 DOCX riesportati identici, Minervino 61/61 conservate. 21 audit identici;
due copie CRAA variano soltanto nel chiarimento/campo descrittivo e nei relativi
contatori, senza variazioni di fatti, condizioni, binding o checkbox.
CRAA storico resta a 9 scritture; ultimo reale a 7. Frontend e PDF non riprovati:
nessun cambiamento in quei percorsi e DOCX byte per byte identici.

Zero nuove chiamate LLM, token o costi provider. Grezzi e codice prima/dopo in
`backend/data/compilation-audit/craa-model-reason-20261020-01/`; backup separato
verificabile nella consegna. Preservati gli altri file, sessioni e storage live.
Nessuna migrazione, reindicizzazione, nuova sessione reale, commit o push.
Backlog intatto: nome firmatario CRAA, CCIAA invisibili nel PDF, copertura dei
campi composti e domande ridondanti. Effetto su una nuova inferenza del narratore
non misurato. Nessuna baseline generale adottata. Arresto alla consegna.

## CRAA: conservazione delle risposte USER — concluso il 20 ottobre

[Rapporto](docs/craa-risposte-user-2026-10-20.md),
[controlli](docs/benchmarks/2026-10-20-craa-user-checks.json),
[consegna](<benchmark ufficiale/craa-user-20261020-01/README.md>),
[DOCX reale](<benchmark ufficiale/craa-user-20261020-01/e2e/craa/bozza.docx>).

Distinzione dimostrata: il vecchio caso225>200 è reason di un chiarimento MODEL,
non una rispostaUSER lunga persa. Metadato globale invariato;test permanente.
Individuati separatamente taglio nativo4000/trim nel composer,copia soloReact
dopo errore di rete,estratti V12/controlli2000contro ingressoAPI4000.
Allineati soltanto gli estratti a4000;valori1500,pertinenza,slot,citazioni e
grounding invariati. UI invia originale,blocca oltre4000senza tagli,contaUnicode,
mantiene copia nella scheda per progetto/conversazione e consente recupero
manuale/riuso dei turni server. Nessun reinvio automatico o nuova persistenzaDB.
Storage non disponibile segnalato;prima della ricezione la copia è limitata
alla scheda,poi la cronologia server conserva l'originale. Nuove bozze protette.

53nuovi test(33backend+20frontend),2.877backend PASS217,26s,126frontend PASS6,70s,
Ruff/lint/build PASS. Testlimiti,Unicode,spazi,righe,errori,scope,attribuzioni,
valori1501,storage/reload/cambiochat/nuovachat/bozza durante richiesta.
22audit/DOCX precedenti identici senza rete/SQLite,Minervino61/61,CRAA9XML.
RED e difetti harness conservati e distinti dagli errori del prodotto.

Nuova sessione realeUI bc286f4fd88d46d89d55edf0595d68e7,versione7 GENERATED:
risposta3113caratteri recuperata dopo reload e identica inHTTP,router,guard,
cronologia eSQLite. Tre ricevute:ruolo firmatarioTRUE,coerenzaCCIAA SKIP,
fatturato SKIP. Nessuna attestazione implicita o nuovo dato personaleUSER.
13fatti grounded/13assegnazioniMODEL;2anni rifiutatiFORM,2fatturati come
alternative nonselezionate,9proposte singole grounded/revisionate,7applicabili/
scritteSOURCE,0USER/checkbox/indebite rilevate. Due CCIAA rinviati e nomefirmatario
omesso restano vuoti. Il reale non esercita il vecchio reason225:non dichiararlo
corretto. Quote4000provate nel software;nel reale estratti decisionali brevi.

DOCX/XML/posizioni/8tabelle/prestampato/stili/download verificati;tcPr/trPr/tblPr/
tblGrid intatti. PDF7pagine,7valori leggibili,viste1/4/7,0fuoribordo. CCIAA
invisibili non toccati:nuove celle vuote non verificano la visibilità. Unioni
etichette/valori restano;Worddesktop nonprovato. Primo driver senzaPTY:
stessa conversazione riaperta,nessuna nuova globale;primo trace incompleto,
secondotrace/video finalizzati.15GETabortite finali,nessunPOSTfallito/providererror.

Una globale reale nuova,7chiamatetotali,95.674token,87,21sglobale,96,42sHTTP,
0,021002USD stimati. StessiFORM/22SOURCE/modello/thinking/promptglobale.
Codice invariato durante la prova;nessun retryqualità o stato manipolato.
Modificati compilation_chat.py e ProjectWorkspacePage.tsx,nuovo helper frontend;
API/DB/FORM/writer/parser/grounding/binding/modello invariati. Nessun framework.

Preservati1.358altrifile,29sessionilive,285filestorage,37sessionipregresseclone,
una nuova isolata.116hashbackend/frontend congelati. Backup verificabile delle
acquisizioni con codice prima/dopo,senzaDB/chiavi/env;23ricostruzioni offline e
contratto estratti prima/dopo. Grezzi backend/data/compilation-audit/craa-user-20261020-01.
Servizi isolati fermati. Nessuna migrazione/reindicizzazione/commit/push/baseline
adottata. Arresto dopo consegna. Residui:metadato MODEL225,nomefirmatarioCRAA,
visibilitàCCIAA e dialogo restano interventi distinti,non avviati automaticamente.

## Generalità del firmatario fra moduli — concluso il 20 ottobre

[Rapporto](docs/firmatario-generale-2026-10-20.md),
[controlli](docs/benchmarks/2026-10-20-signatory-checks.json),
[consegna](<benchmark ufficiale/firmatario-generale-20261020-01/README.md>),
[DOCX finale reale](<benchmark ufficiale/firmatario-generale-20261020-02/e2e/trapani/bozza.docx>).

Cause: vecchio riuso legato a una sola sequenza completa di campi e nessun
collegamento backend dalla scelta nominativa esplicita nel turno iniziale.
Nuovo riconoscitore FORM di blocchi personali ancorati, etichette individuali,
paragrafi di continuazione e tabelle semplici contigue; arresto su ambiguità,
altri soggetti o strutture non supportate. Nessuna regola per nomi di bandi/aziende.
Scelta USER registrata nella stessa sessione identifica la persona, non ne prova
i dati. Profilo SOURCE univoco con nome/cognome/CF, proprietà e citazioni separate,
validatori e attribuzione esistenti. Nessuna inferenza di poteri o partecipazione.
Veto aggiunto nel collegamento per fatti già grounded di società/altra persona
in quelle destinazioni. Fonte rimane documentata, associazione respinta.

Modificati soltanto source_reuse/global_sessions e nuovo signatory_form;
contesto USER persistito nelle nuove sessioni, audit MODEL intatto e audit
effettivo distinto, riuso prima della sintesi e rivalidato all'export. Nessuna
approvazione o applicabilità automatica; vecchie sessioni non aggiornate.
FORM B0, grounding/binding fattuali, modello, prompt, API, DB, parser e writer invariati.

51 nuovi test permanenti (45 locali+6 sessioni FTS5/Qdrant),327 mirati PASS47,55s,
2.844 backend PASS321,95s,Ruff PASS. Insuccessi intermedi conservati. Dieci replay
storici con DOCX identici, Minervino61/61. Con contesto USER già registrato:
8 proposte Trapani,4 Bella,2 Catanzaro;9 proprietà Minervino preservate.
Nuove proposte non esportate con vecchie revisioni. Catanzaro celle composte
nascita/residenza e carica non collegata restano irrisolte, senza concatenazioni.

Due nuove prove reali UI distinte: prima17SOURCE,poi17SOURCE dopo veto sui
controesempi; nessuna modifica dentro le prove e nessun retry per qualità.
Finale sessione b7d40c2449ad421580fe267547ac7964,versione7 GENERATED:9 proposte MODEL
grounded+8 personali riusate,17 applicabili/revisionate/scritte,0USER/checkbox,
0 scritture indebite rilevate. Recuperate8/8 generalità di Trapani. PEC dichiarativa,
firma,data e altri dati procedurali non verificati vuoti. Quattro rami alternativi
UNKNOWN conservati. Resta una conferma duplicata dell'identità iniziale.
PDF5pagine,XML/posizioni/prestampato/stili/tabelle/download verificati; viste1/2/3/5.
Difetto cosmetico aLecce conservato, Word desktop non provato.

Finale7chiamate(1globale),95.023token,globale70,76s,HTTP79,89s,0,019047USD stimati.
Due prove16chiamate/210.373token/0,042370USD stimati,non fattura. Stessi22SOURCE,
deepseek-flash enabled/low globale,prompt e hash congelati. Controfattuale stesso
output della prima prova:codice precedente9→finale17 senza nuove inferenze.
Il civico aziendale completo nella seconda prova è variazione MODEL, non effetto
del riuso. Valori SOURCE e scelte procedurali USER sempre distinti.

Preservati1.426 altri file,29sessioni live,285file storage,35/36sessioni precedenti
nei due cloni;2nuove isolate.67hash applicativi finali invariati durante la prova.
Backup separato delle due acquisizioni con verifica estratta senza rete/DB nella
consegna; grezzi sotto backend/data/compilation-audit/firmatario-generale-20261020-01
e -02. Servizi isolati fermati. Nessuna migrazione/reindicizzazione/commit/push.
Nessuna baseline adottata. Arresto dopo rapporto; limiti di copertura e dialogo
documentati per la prossima decisione, nessun lavoro ulteriore avviato.

## PEC Trapani: dato SOURCE separato dall'impegno USER — concluso il 20 ottobre

[Rapporto](docs/pec-consenso-procedurale-2026-10-19.md),
[controlli](docs/benchmarks/2026-10-20-pec-consent-checks.json),
[consegna](<benchmark ufficiale/pec-consenso-20261019-01/README.md>),
[DOCX reale](<benchmark ufficiale/pec-consenso-20261019-01/e2e/trapani/bozza.docx>).

Causa dimostrata: PEC corretta in SOURCE ma riusata in «di accettare…» senza
consenso USER. Il MODEL la trattava come data, senza condizioni, con citazione
FORM abbreviata. Il narratore disponeva della clausola intera e non chiedeva
consenso: non bastava allargare la citazione. Nuovo gate circoscritto sul FORM
fisico per impegni espliciti nella stessa clausola marcata; dato, applicabilità,
revisione e consenso restano distinti. Non cambia il grounding o i binding.

Domanda deterministica con dichiarazione e valore; ricevuta legata a template,
clausola, destinazioni, valori e sessione. Solo assenso USER esplicito pertinente
autorizza l'uso procedurale; SKIP/UNKNOWN/diniego/export non lo fanno. Vincolo
anche nell'export diretto e nella vista pubblica chat, per valori SOURCE/USER.
Nessun nuovo schema globale, endpoint o sistema di orchestrazione. Modificati
solo global_dialogue/global_sessions e nuovo compilation_procedural_consent.py.
Parser FORMTEXT, writer, modello, API, DB e prompt applicativi invariati.

49 test permanenti nuovi, 248 mirati PASS in36,96s, 2.793 backend PASS in218,66s,
Ruff PASS. Test iniziali RED e insuccessi intermedi conservati. Nove replay:
Trapani10→9, p107 ripristinato all'XML originale; gli altri otto DOCX identici,
compreso Minervino V12 61→61. Nove audit fattuali identici. Nessuna perdita di
scritture corrette nel confronto congelato. PDF Trapani prima/dopo cinque pagine.

Una nuova chat reale, sessione331f4362017a42dc86f223ea0c8c46c7, finale10 GENERATED:
una globale, nove fatti grounded, dieci proposte grounded/applicabili/revisionate,
nove testi SOURCE effettivi, zero USER/checkbox. La PEC resta nei dati aziendali;
la dichiarazione resta vuota dopo ricevuta USER SKIP, pur senza hold del narratore.
Zero scritture non supportate o in sezione errata rilevate; otto proprietà complete,
una via corretta senza civico172/C disponibile ma omesso dalla nuova risposta.
Otto generalità del firmatario ancora omesse; data/firma volutamente vuote.

Due turni USER, tre decisioni/quattro domande: un duplicato societario preesistente,
per has_user_alternatives che scambia «o» in «senza raggruppamenti o consorzi» per
un'alternativa; guard aveva risposto SUPPORTED. Seconda conferma accettata.
Non corretto altro durante la prova. DOCX/XML/posizioni/stili/tabelle/download
verificati; PDF cinque pagine, nove valori leggibili a pagina2, viste1/2/3/5,
nessuna parola oltre bordo. Dieci GET abortite a mount/refresh, nessun errore provider.

Stessi22SOURCE, deepseek-flash enabled/low globale, prompt e configurazione
congelati prima della chiamata; nessun riuso/retry qualità. 10 chiamate totali,
109.176token, globale65,86s, somma HTTP77,22s, 0,019564USD stimati sul tariffario
congelato, non fattura. Caso positivo di assenso provato nei test simulati;
la singola nuova prova reale usa il rinvio dello scenario, non un consenso inventato.

Preservati1.333 altri file,29 sessioni live,285file storage e34sessioni precedenti
nel clone; una sola nuova sessione. Hash66file applicativi intatti durante la prova.
Grezzi in backend/data/compilation-audit/pec-consenso-20261019-01/; backup separato
nella consegna. Porte isolate8001/5174 libere. Nessun commit/push o adozione baseline.
Copertura dichiarata limitata a verbi e clausole riconosciuti: impegni impliciti o
fra paragrafi/celle distinti non certificati. Nessuna migrazione/reindicizzazione.
Arresto dopo rapporto; residui di copertura/dialogo documentati per decisione futura.

## Attribuzioni tabellari: verifica e veto circoscritto conclusi — 19 ottobre

[Rapporto](docs/attribuzioni-tabellari-2026-10-19.md),
[consegna](<benchmark ufficiale/tabelle-attribuzione-20261019-01/README.md>),
[esito](<benchmark ufficiale/tabelle-attribuzione-20261019-01/ESITO.json>).

Nessuna nuova attribuzione indebita rilevata nei valori tabellari degli output
reali salvati. Riprodotti invece quattro controesempi controllati sul FORM e
sulle SOURCE reali Catanzaro: denominazione/CF societari in celle personali e
denominazione/forma giuridica nei dati del direttore tecnico. Non sono nuove
risposte LLM. Prima 4/4 proposte errate grounded, dopo 0/4; applicabilità e
revisione distinte, nessuna pretesa di quattro scritture reali osservate.

Esteso solo compilation_attribution.py alle righe etichetta–valore riconoscibili,
con due celle fisiche. Soggetto dalle etichette FORM, non da label/entity MODEL.
Confini per righe vuote/sconosciute, etichette compilabili, checkbox, annidamenti,
merge verticali e altre tabelle. Operatore economico da solo resta ambiguo,
non diventa automaticamente azienda. Nessuna ricostruzione generale di record
multicolonna o identità per somiglianza del nome. Un header non ripetuto non
viene promosso a citazione valida per il binding. UNKNOWN e citazioni invariati.

23 test tabellari permanenti nuovi, fixture reale Catanzaro e guida aggiornata.
347 mirati PASS in 28,75 s, 23 tabellari finali PASS in 3,16 s; intera suite
backend 2.744 PASS in 209,28 s; Ruff PASS. Nove audit e DOCX ricostruiti identici:
sei riferimenti 55/10/13/4/9/0, Minervino V12 61, Cesano corretto 1, ultimo
Catanzaro reale 15. Nessuna perdita o nuova accettazione nei replay.
Non ripetuto il rendering: stessi byte dei DOCX precedenti già ispezionati.

Esaminate 37 scritture in tabelle: 35 SOURCE, due USER, con ripetizioni fra i
riferimenti. Il vincolo di tipo soggetto determina 13 SOURCE, non determina 22.
Non è una verifica semantica universale; strutture non determinate restano
sotto i controlli storici e la revisione. Residui, checkbox e difetti storici
Trapani/CRAA non corretti. Nessuna nuova adozione baseline.

Preservati 1.085 altri file precedenti, 29 sessioni live e 285 file storage.
Zero chiamate/provider, costi LLM o nuove sessioni. Parser FORMTEXT, writer,
FORM B0, modello, API, prompt e dialogo invariati. Grezzi in
backend/data/compilation-audit/tabelle-attribuzione-20261019-01/; consegna con
backup e verifica separati. Nessun commit/push. Arresto alla verifica richiesta;
chiusa la lacuna per questa famiglia, non dichiarate sicure tutte le tabelle.

## Attribuzione SOURCE: sette falsi trasferimenti bloccati, regressione e prova casuale concluse — 19 ottobre

[Rapporto](docs/attribuzione-source-soggetto-campo-2026-10-19.md),
[consegna](<benchmark ufficiale/source-attribuzione-20261019-01/README.md>),
[prima/dopo e regressione](<benchmark ufficiale/source-attribuzione-20261019-01/regressione.json>),
[risultato reale](<benchmark ufficiale/source-attribuzione-20261019-01/E2E-RISULTATO.json>).

Aggiunto un veto V12 per soggetti espliciti nel FORM inline, indipendente da
etichette MODEL: non trasferire dati aziendali nel periodo del sottoscrittore.
Mantiene i passaggi espliciti alla società, non inferisce identità/poteri e non
unisce persone. Rifiuta anche qualificazioni di luogo esplicitamente incompatibili
(es. residenza/studio). Ambito limitato ai paragrafi inline riconoscibili; non è
un risolutore semantico universale o nuovo controllo dei soggetti nelle tabelle.
Nessun allentamento dei binding/grounding. Modificati solo il verificatore globale
e il nuovo helper applicativo; parser FORMTEXT, writer, API, modello, prompt e
dialogo invariati. Audit compatibili intatti per conservare le revisioni.

Cesano stesso output reale: 8 fatti societari grounded conservati; proposte
grounded e scritture 8→1, esattamente sette trasferimenti non dimostrati esclusi.
Denominazione aziendale conservata. Nessun nuovo valore o spunta; tre generalità
SOURCE e checkbox societaria restano omesse. DOCX/PDF prima/dopo separati.
Sei riferimenti: 55/10/13/4/9/0 invariati; Minervino V12 chat 61→61, DOCX identico.
Nessuna nuova accettazione o perdita di scritture corrette. Render di otto replay,
57 pagine, bordi controllati; PDF invariati con stesse parole/coordinate.
PEC Trapani e due CCIAA CRAA invisibili restano difetti storici, non corretti.

39 test permanenti nuovi più fixture reale; 324 mirati PASS, 2.721 backend PASS
in 211,25 s, Ruff PASS. Prima riproduzione negativa, poi correzione, poi freeze.
Nuova estrazione tra dieci originali disponibili escluso Cesano: Catanzaro,
seed 13243375443350163391, nessuna riestrazione. Versione e configurazione
registrate prima della chiamata. Stessi 22 SOURCE, deepseek-flash, globale
thinking enabled/low e system prompt invariati, fingerprint e72d3c7f663d3e1383b00b3884cb4501.

Una sessione UI nuova b47a62f824894850bab0c058b322051a, versione10 GENERATED.
Una globale reale: 15 proposte valore, 13 grounded/applicabili/revisionate/scritte
SOURCE; due valori USER scritti (firmatario e titolo), con riscontro SOURCE.
15 totali leggibili nel PDF17 pagine. Zero attribuzioni indebite o sezioni errate
rilevate, zero nuove checkbox; numero registro corretto ma senza data richiesta.
Riferimento autoriale storico: 31 posizioni SOURCE, 15 scritte,16 vuote
(14 omesse,2 respinte per FORM/binding locale), oltre alla data parziale.
Non è un GOLD indipendente o percentuale di accuratezza. Nessun riuso automatico
dell'anagrafica tabellare; UNKNOWN Parte terza/forma partecipazione non collegati
a dati/decisioni già disponibili. Zero gruppi checkbox proposti. Quattro domande
ridondanti col messaggio iniziale, una procura condizionata rinviata; due risposte
USER poi export ordinario. Cinque gruppi di decisioni non inventati e UNKNOWN.

10 chiamate, 181.386 token,193,16 s HTTP sommati,0,043697 USD stimati, non fattura.
Globale 181,33 s, 45.115 output inclusi 35.332 reasoning. Nessun retry o correzione
durante la prova. XML/ZIP/posizioni/prestampato/stili/tabelle/checkbox controllati;
viste pagine1,2,11,17, tutti i 15 valori leggibili. Dieci GET abortite su mount/refresh,
nessun altro errore registrato; trace/video finalizzati, download identico.

967 altri file precedenti, 279 file audit precedente,29 sessioni live e 285 file
storage invariati. Clone: 33 sessioni precedenti intatte, una nuova; servizi isolati
fermati. Grezzi in backend/data/compilation-audit/source-attribuzione-20261019-01/;
backup distribuibile con hash nella consegna, senza DB/chiavi. Nessun commit/push.
Correzione mirata PASS; bozza Catanzaro parziale utilizzabile nei limiti osservati.
Non adottata la baseline né certificata affidabilità generale. Arresto dopo
replay, prova e rapporto; nessuna nuova correzione o compattazione avviata.

## Regressione FORMTEXT PASS, qualità E2E Cesano FAIL — 19 ottobre

Verifiche e prova richieste concluse, funzionalità complessiva non dichiarata
chiusa. [Rapporto](docs/regressione-formtext-e2e-2026-10-19.md),
[controlli](docs/benchmarks/2026-10-19-formtext-e2e-checks.json),
[metriche](docs/benchmarks/2026-10-19-formtext-e2e.json),
[consegna e file modificati](<benchmark ufficiale/formtext-cesano-20261019-01/README.md>).

Nessun file applicativo cambiato in questa fase. Estesa la conservazione XML
nei 15 negativi esistenti; aggiunti test reali e 26 file di fixture congelate.
55 casi permanenti nei due file FORMTEXT, 28 aggiunti. 258 mirati in 22,25 s,
2.682 backend in 205,02 s e Ruff passati prima della nuova globale.
20 ID e risultati reali verificati tutti insieme e singolarmente, ordine
rimescolato, nomi duplicati, run multipli, malformati/annidati/precompilati,
firme, stili e parti del pacchetto protetti.

Sei cataloghi, audit ed export precedenti ricostruiti identici; PDF nuovi con
testo/coordinate identici. Tutti i 20 sentinella Cesano leggibili.
Due CCIAA CRAA invisibili ed errore PEC Trapani conservati, non regressioni.
Indirizzi Catanzaro leggibili a pagina 1/11 nonostante intercalazione delle
etichette nel testo estratto. Controllati i bordi delle 48 pagine preflight,
viste pagine selezionate; nessuna verifica Word desktop, non richiesta.

Una nuova sessione reale 226639266b2c4b4a8aaacc2e1f25b65d, conversazione
conv-436e1eb7ce2d4b6d, progetto verifica-formtext-v12-cesano, FORM176,
versione finale10 GENERATED. Stesso originale/scenario e 22 SOURCE;
modello, parametri globali e system prompt confrontati prima dell'inoltro.
Una globale reale, nessun riuso/retry qualità, nessuna manipolazione dello stato.
Due risposte USER sul ramo societario e data UNKNOWN; export/download/refresh
ordinari. Primo avvio browser a server spenti dopo riprendi, prima di ogni
LLM/sessione, conservato; riavviato stesso progetto.

Otto proposte/grounded/applicabili/revisionate/scritte; tutti gli otto valori
nelle posizioni XML previste e leggibili nel PDF di tre pagine. Una sola
corrispondenza soggetto/campo dimostrata: denominazione p19.ft0. Sette dati
societari nello studio/PIVA/recapiti del sottoscrittore senza prova o conferma
di quella pertinenza: non falsi fatti aziendali, ma scritture non certificabili.
Tutti entity=company, nessun binding: il gate personale si attiva con person
o binding_id, non verifica autonomamente il soggetto richiesto da questi campi.
Tre dati personali disponibili omessi, spiegazione MODEL su c_firmatario
inesistente fra le condizioni effettive. Il riuso inline non riconosce la
grammatica di Cesano; scelta nominativa solo nel messaggio iniziale, nessuna
ricevuta sul campo. Zero choice_groups, checkbox societaria non selezionata.
Data rinviata e altri 12 testi vuoti intatti; zero spunte/firme inventate.
Problemi distinti da FORMTEXT, documentati e non corretti.

10 chiamate reali (1 globale, 4 router, 2 guard, 3 sintesi), 111.691 token,
99,90 s HTTP sommati, 0,022380 USD stimati, non fattura. Deepseek-flash,
globale enabled/low, fingerprint e72d3c7f663d3e1383b00b3884cb4501.
Tutte HTTP200/stop. Trace/video finalizzati, dieci GET abortite su mount/reload.
XML/CRC/posizioni/68 checkbox/stili/prestampato verificati, download e
ricostruzione writer identici, nessun altro cambiamento alle parti del DOCX.

328 altri file protetti, 632 artefatti precedenti, 29 sessioni live e 285 file
storage invariati. Nel clone 32 sessioni precedenti intatte, una nuova.
Grezzi in backend/data/compilation-audit/formtext-chiusura-20261019-01/.
Backup con codice/fixture/audit/browser senza DB/chiavi nella consegna;
servizi isolati fermati. Nessun commit/push o modifica agli altri componenti.

Tutti i controlli obbligatori eseguiti. Supporto tecnico FORMTEXT PASS;
qualità funzionale FAIL, quindi nessuna chiusura complessiva o adozione baseline.
Prossima fase da decidere: associazione soggetto/campo, firmatario e gruppi di
scelta. Nessuna correzione indipendente, nuova generazione o E1 avviati.

## FORMTEXT: riconosciuti i 20 campi testuali legacy — 19 ottobre

Concluso l'intervento strutturale richiesto, senza nuove chiamate LLM.
[Rapporto](docs/legacy-formtext-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-legacy-formtext.json),
[controlli](docs/benchmarks/2026-10-19-legacy-formtext-checks.json).
Word/PDF tecnici in `nuovi dati`, suffisso Cesano.FORMTEXT-PROVA-TECNICA-20261019;
[limiti della prova](<nuovi dati/LEGGIMI-CESANO-FORMTEXT.md>).

Unico file applicativo modificato in questa fase: docx_templates.py.
Il parser prima scartava ogni paragrafo con fldChar/instrText. Ora riconosce
FORMTEXT semplici, completi, vuoti, abilitati e non annidati nello stesso
paragrafo, con ID p{paragrafo}.ft{indice}. I nomi interni duplicati non sono
chiavi: tutti i 20 Cesano si chiamano Testo1. Quindici campi iniziali, quattro
nei rami e una data: catalogo da 68 a 88 candidati, tutte le 68 checkbox
preesistenti conservate. Contesto e prove FORM usano il contratto attuale.

Writer sul solo risultato del campo; proprietà, bookmark, istruzioni e stili
preservati. Supportati anche risultati senza nodi di testo. Test aggiuntivo
riproduce un conflitto di offset fra risultati vuoti adiacenti; corretto con
precedenza per start/end decrescenti. Firme, email divise/incomplete e limiti
restano controllati; maxLength Word esplicito rispettato senza troncamento.
Campi malformati, annidati, su più paragrafi, precompilati, disabilitati/bloccati,
con formato/tipo speciale o in contenitori non sicuri restano esclusi.
Non è supporto universale a qualsiasi controllo Word.

Prova meccanica su tutte le 20 destinazioni con sentinella distinti, più quattro
dati SOURCE dello scenario assegnati esplicitamente nel test. Valori controllati
localmente, posizioni e XML verificati; entrambi i PDF hanno tre pagine e tutti
i valori leggibili, nessuna parola fuori pagina. Viste pagine 1 e 3 di entrambi;
nessuna prova Word desktop. Zero checkbox spuntate, nessuna firma/attestazione.
**Non sono proposte LLM o nuova compilazione chat**: non si dichiarano verificate
automaticamente scelta del firmatario e applicabilità. I restanti 16 campi
sono vuoti nella prova SOURCE; quella con 20 sentinella non è una domanda valida.

Replay senza rete sui sei documenti: Minervino/Trapani/Catanzaro/Bella/CRAA
conservano cataloghi e audit identici, export byte per byte identici con
54+1 checkbox/10/13/4/9 scritture. Riferimenti: benchmark ufficiali nuovi,
non il precedente replay Minervino61. L'errore PEC Trapani e i due dati CCIAA
invisibili CRAA restano intatti. Cesano conserva tutti i precedenti 68 candidati
e la vecchia risposta scrive ancora zero; 20 nuovi campi irrisolti nell'audit,
nessun recupero automatico o nuova accettazione dal replay.

27 nuovi casi, 230 test mirati in 15,00 s, 2.654 backend in 197,46 s e Ruff
passati sulla versione finale. RED e primi errori degli assert separati;
la suite da 2.651 casi precedente all'ultimo caso limite non è l'esito finale.
317 altri file protetti, 546 artefatti precedenti, 29 sessioni e 285 file storage
invariati, nessuna sessione nuova. Prompt globale, grounding, dialogo, API,
database, modello e FORM originali invariati. Nessun commit/push o refactor.
Grezzi in backend/data/compilation-audit/legacy-formtext-20261019-01/; backup
separato con codice prima/dopo, originali, replay e DOCX/PDF in docs/benchmarks.

Le sessioni esistenti non sono migrate. Le nuove destinazioni sono disponibili
alle nuove sessioni; non si rivaluta retroattivamente il benchmark casuale.
Prossimo passo da decidere: nuova prova controllata di Cesano dalla chat con
stessa KB/scenario per misurare proposte e scritture reali. Non avviata in
questa fase. Nessun E1 o adozione di baseline; arresto dopo rapporto e artefatti.

## V12 invariata su tre bandi nuovi estratti da un pool — 19 ottobre

Conclusa la prova esplorativa autorizzata dopo il benchmark storico.
[Rapporto completo](<benchmark ufficiale/casuali-v12-20261019-01/RAPPORTO.md>),
[consegna e backup](<benchmark ufficiale/casuali-v12-20261019-01/README.md>),
[riepilogo](docs/benchmark-casuale-v12-2026-10-19.md). Grezzi in
`backend/data/compilation-audit/casuali-v12-20261019-01/`.

Protocollo, criteri, pool obiettivo di otto e seed fissati prima della ricerca;
ricerche estese prima del sorteggio. Una sola estrazione: CRAA, Bella, Cesano
Maderno. Pool di convenienza con estrazione casuale interna, non campione
rappresentativo nazionale. Nessun GOLD indipendente, percentuale di accuratezza
globale o sostituzione dei casi difficili. Tre nuove CompilationSession dalla
UI, una globale nuova per FORM, stessi 22 chunk Company/General, scenari USER
separati preregistrati e normale export, senza manipolazioni dello stato.

CRAA: nove testi SOURCE corretti nell'XML, soltanto sette leggibili nel PDF;
due dati CCIAA in celle originali di 66/81 twip non sono visibili in LibreOffice.
Un nome documentato omesso; il chiarimento proposto è respinto per motivazione
di 225 caratteri, oltre il massimo 200. Bella: quattro testi aziendali scritti,
quattro proprietà documentate del firmatario omesse, gruppo della partecipazione
respinto per etichette FORM incomplete. Cesano: zero valori aggiunti, copia
ordinaria tecnicamente valida ma fallimento funzionale della compilazione.
La chat espone 68 checkbox e nessuno dei 20 campi legacy FORMTEXT; il chiarimento
societario sulla checkbox è respinto. Il preflight generico aveva previsto
il rifiuto prima della sessione: addendum separato documenta la smentita reale,
senza riscrivere gli input congelati.

Tredici valori corretti nell'XML, undici leggibili nel PDF. Zero nuove scritture
fattuali/decisioni indebite rilevate, zero nuove checkbox o testi USER, nessun
hold finale. Questo non annulla il precedente errore PEC. Nucleo SOURCE vuoto:
1/4/4 occorrenze, tutte con dati nell'input; cinque omissioni e quattro senza
destinazioni supportate. Nessuna proposta di valore SOURCE respinta nei tre
casi. CRAA/Bella ripetono una domanda per il falso riconoscimento di alternative
nella negazione “senza raggruppamenti o consorzi”. Preferenze, attestazioni,
esecutori, integrazione e luogo/data restano distinti e UNKNOWN.

22 chiamate reali, tre globali nuove, nessun retry di qualità: 271.084 token,
291,57 secondi provider sommati, 0,060070 USD stimati, non fattura. Modello
deepseek-flash, globale thinking enabled/low e codice invariati rispetto alla
V12 precedente. Nessuna conclusione comparativa di latenza.

Verificati XML/ZIP, posizioni, prestampato, checkbox, download e PDF di 7/4/3
pagine; controllo bordi su tutte le 14, ispezione visiva di pagine selezionate.
Due difetti di visibilità CRAA distinti dalle scritture XML. Replay con rete
vietata ricostruisce audit e DOCX identici; backup con codice congelato e
verifica indipendente, senza database privati o credenziali.
Invariati 318 file protetti, 41 input, 422 artefatti precedenti, 29 sessioni
originali e 285 file storage; tre sole sessioni nuove, schema DB intatto.
Servizi isolati arrestati, nessuna suite completa rieseguita o modifica al
codice applicativo, prompt, grounding, writer, FORM o modello; nessun commit/push.

**Baseline non adottata.** Prima di un altro E1 propongo verifiche mirate sulle
destinazioni Word, sui chiarimenti e sulla scelta della persona; nessuna
correzione è stata avviata. Se questi casi saranno usati per lo sviluppo,
la futura valutazione finale richiederà un lotto nuovo. Arresto alla consegna.

## Benchmark ufficiale V12: tre globali nuove, baseline non adottata — 19 ottobre

Conclusa la prova controllata sui tre moduli storici, senza correzioni alla
pipeline o ripetizioni selettive. [Rapporto](<benchmark ufficiale/RAPPORTO-CONCLUSIVO.md>),
[consegna](<benchmark ufficiale/README.md>), [riepilogo](docs/benchmark-ufficiale-v12-2026-10-19.md).
Risultati in `benchmark ufficiale/`; grezzi in
`backend/data/compilation-audit/ufficiale-v12-20261019-01/`, con backup completo
nella directory di consegna, senza database o credenziali.

Tre nuove CompilationSession dalla UI reale, una globale DeepSeek nuova per
FORM, medesimi 22 chunk Company/General, scenari USER distinti preregistrati,
massimo due turni USER e normale export. Minervino: 55 scritture, ossia 54 testi
SOURCE corretti e una checkbox USER. Trapani: 10 testi, nove corretti e una PEC
che completa un'accettazione senza decisione USER. Catanzaro: 13 testi SOURCE
corretti, nessuna checkbox. Nessuna firma o altra nuova attestazione; zero hold
finali. Copertura SOURCE documentata: 60/17/31 posizioni; vuoti: 6/8/18, dei quali
6/0/2 rifiuti e 0/8/16 omissioni. Tutte le prove di questi vuoti erano nell'input.
Sono occorrenze in campi, non fatti atomici distinti o accuratezza globale:
il totale degli adempimenti ancora UNKNOWN non è definito.

Minervino conserva i 24 campi soci e recupera nove generalità/carica SOURCE
dalla scelta USER del firmatario. Quattro campi del direttore sono respinti
per le prove del nuovo binding, prima del narratore; anche provincia con solo
marker FORM e Comune con indirizzo proposto sono respinti. Trapani/Catanzaro
non riusano le generalità: la grammatica inline specifica non riconosce i loro
FORM. Catanzaro ha zero choice_groups, 18 vuoti SOURCE fra parte terza/CCIAA e
anagrafica; tre checkbox autorizzate restano vuote. In tutti i casi la negazione
“senza raggruppamenti o consorzi” è respinta come alternativa, nonostante router
e guard favorevoli: una domanda ripetuta per documento. Nessun fix effettuato.

30 chiamate reali, tre globali, 463.201 token, 399,32 s di tempi HTTP sommati,
0,099946 USD stimati da usage/cache e tariffa ufficiale, non fattura. Globale
con thinking enabled/low invariato; alias deepseek-flash, fingerprint comune
`e72d3c7f663d3e1383b00b3884cb4501`. Trapani ripresa nella stessa sessione alla
versione 6 dopo interruzione del runtime, senza reinvio o nuova globale;
wall time comprensivo della pausa, primo trace browser non finalizzato.

ZIP/XML/posizioni/prestampato/checkbox/download verificati; PDF di 9/5/17
pagine, nessuna parola fuori pagina sulle 31 pagine. Ispezionate visivamente
pagine scritte, iniziali e finali selezionate. Replay con rete vietata: audit
finali e tre DOCX identici, incluso l'errore di Trapani. Invariati 318 file
protetti, 26 input, 645 artefatti precedenti, 29 sessioni live e 285 file storage;
soltanto tre sessioni nuove, schema DB intatto. Servizi isolati arrestati.
Nessuna nuova suite completa, commit/push, E1 o adozione della baseline.
**Non propongo il congelamento come baseline affidabile**, per la scrittura
indebita di Trapani. Prossimo passo da decidere: confine fra SOURCE e consenso
procedurale, prima di E1. Arresto alla consegna richiesta.

## Prova reale della chat V12: confermate61 scritture — 19 ottobre

Richiesta conclusa: una sola nuova sessione isolata, nessuna correzione durante
la prova e nessun commit/push. [Rapporto](docs/prova-chat-v12-hold-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-holds-chat.json),
[otto tracciati](docs/benchmarks/2026-10-19-v12-holds-chat-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-holds-chat-checks.json).
Word/PDF/report/conversazione: nuovi dati, V12-CHAT-REALE-20261019.

Sessione9bd60112c34247f799d320137d81831f,conv-5037d9a1b3554423,versione9GENERATED.
Come nel riferimento, una risposta globale congelata riusata su FORM/56SOURCE/
schema identici; router,guard,narratore reali,UI senza mock. Non una nuova
valutazione della qualità globale. Gli stessi3messaggiUSER letterali inviati
dalla chat, nessuna ricevuta copiata: CONDITION_TRUE societaria e SKIP tecnico,
nessun valore testualeUSER. Firmatario e dati personali sempre SOURCE.

**60testiSOURCE+1checkboxUSER=61**, rispetto a53 della precedenteUI e61replay.
Tutti52precedenti e24soci conservati;8DT scritti e conformiGOLD. Narratore in
tutte3risposte non proponehold: non interviene la regola di rifiuto dei motivi
ridondanti. Questo differisce dalreplayB, doveMODELmanteneva8hold. AuditSOURCE
identico,60revisionate,nessun aggiornamento artificialeUNKNOWN o consensoSKIP.
DOCXscaricato e salvato identico byteperbyte alreplay61(SHA84e33e...feddd).
Solap39.cb0 selezionata,12altreintatte,0deselezioni/nuove indebite osservate.

CinquegruppiUSER ancora aperti,nessuna preferenza/attestazione/designazione/
luogo-data inventata.4testiUSER attesidalGOLD restanovuoti. Nello scenario0hold
fattualilegittimi osservati: protezioni verificate separatamente dai18negativi
esistenti,18passati1,43s,senzaLLM. Nessuna suitecompleta oRuff rieseguiti per
questa prova; i2627test del precedente intervento restano misure storiche.

7chiamate provider reali(3router,3sintesi,1guard),69815token(68766input+1049output),
13,171s richieste sommate,0nuoveglobali/1riuso,0retry qualità;USDnonstimato.
Durata wall include operatore/driver,nessuna conclusione sulle prestazioni.
Incidentestdin driver: prima fase poi reload della stessa conversazione conPTY,
nessuna seconda sessione o reinvio. Primo trace/video e dettagli5segnalazioni
nonfinalizzati;DOM/rete/trasporti disponibili. Continuazione trace/video e10GET
abortite su mount/reload,0pageerror/HTTPerroriacquisiti;download/refresh riusciti.
Errori lettori di audit corretti soltanto negli script,mai nell'applicazione.

XML/CRC/posizioni/prestampato/report,4tabelle/13controlli verificati;59/60testi
conformiGOLD,carica completa attestata giànota. NuovoPDF9pagine,viste3e9,
firma conlinea nell'ultima,giunzioniwriter note intatte;warningregistrylinguistico
locale LO conservato,conversione riuscita/DOCXimmutato. Bundle con codice
archiviato rigenera audit/Word senzaDB/chiavi/rete.249file app/test/frontend/
fixture invariati,29sessionilive/285file e artefatti precedenti preservati.
Servizi isolati arrestati,nessunanuova architettura/migrazione/esperimento.
Arresto al termine del rapporto e consegna delDOCX.

## Hold del narratore V12: recuperati 8 testi nel replay — 19 ottobre

Conclusa la richiesta sulla sola divergenza replay61/chat53.
[Rapporto](docs/hold-narratore-v12-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-narrator-holds.json),
[otto tracciati](docs/benchmarks/2026-10-19-v12-narrator-holds-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-narrator-holds-checks.json).
Word/PDF/report in nuovi dati, suffisso V12-HOLD-VERIFICATO-20261019.
Nessun commit/push. Conservati lavoro precedente, sessioni e artefatti originali.

Cronologia certa: prime2sintesi senza hold; terza, dopo USER,17proposte e8hold
nuovi del direttore. Export eredita8, non li riconferma con nuova LLM.
Schema originale senza motivi/HTTP senza motivo separato: ragione privata
storica non recuperabile. Fonte del blocco: MODEL, non validatori SOURCE.
Nel vecchio contesto mancava la prova composta branch_evidence, benché ruolo,
USER e indicatori di applicabilità fossero presenti.

Esaurite le prove salvate,2sole chiamate reali ristrette agli8valori esistenti,
0nuoveglobali/USER: confronto senza/con prova completa di applicabilità.
Entrambe mantengono8hold. B esplicita «Conferma del ruolo attuale di Direttore
Tecnico», rinviata dall'utente. È una conferma aggiuntiva non richiesta dalFORM,
con stesso ruolo già SOURCE e ramo verificato. Passaggio del contesto da solo
insufficiente, fallimento conservato. Non attribuire queste motivazioni alle
vecchie risposte prive di spiegazione. Totale22140token(19729input+2411output),
8,425s complessivi delle2richieste; modello e impostazioni invariati,USDnonstimato.

Unico file applicativo cambiato in questa fase: compilation_global_dialogue.py.
Contesto con condizioni effettive/ricevute/prove; hold_reviews ancorate;
hold_records/transizioni distinguono nuovi,confermati,ereditati,liberati.
Vecchi motivi assenti conservati come not_recorded. Verifica deterministica
rifiuta solo la richiesta letterale «Conferma del ruolo attuale di {ruolo}»
per lo stesso soggetto/binding,clausolaFORM integrale,scope,prova composta e
tutte condizioniTRUE. Altra prova/decisione mancante,UNKNOWN,diniego,rinvio
campo,attestazione o motivo precedente diverso mantengono hold. MODEL inB
conferma8; backend respinge8motivi ridondanti, non accetta nuove prove MODEL.
Nessun cambiamento a grounding,FORM B0,writer,API/DB,modello o regole fattuali.
Nessun hardcoding o nuovo sistema di orchestrazione. Versione narratore4;
fingerprint aggiorna soltanto valori con branch_evidence e non cancella hold.

Quattro replay con rete vietata/DB-storageclonati/validatori-persistenza-export
reali: storico53 stessoSHA; codiceattuale+vecchierispostesenzamotivi53; risposta
realeB motivata61=60SOURCEtesti+1USERcheckbox; controllo negativo simulato con
ostacoloSOURCE53 e8hold protetti. Audit e ricevute identici. Tutti52testi e24soci
conservati,solap39.cb0,intatte12altre,0deselezioni/nuoveaccettazioni indebite
osservate. OttoDT nelDOCX conformiGOLD;59/60testi conformi,carica più completa
attestata già nota. QuattrotestiUSER e5gruppi decisionali restano aperti.
**61 è replay offline con risposta motivata reale, non nuova UI.** La chat
originale resta53. Replay B aggiunge i soli metadati preesistenti availability
nel percorso narrate: valori/prove/condizioni/USER identici, non intero input
byteidentico. Primo confronto troppo rigido fermato prima della valutazione.

26nuovi test,18negativi parametrizzati;210mirati22,61s,2627suite186,99s,Ruff
passati. Red e tentativi intermedi conservati. XML/CRC/posizioni/prestampato,
4tabelle/13controlli verificati. DOCX61 stessoSHA84e33e... del precedente61;
altri53stessoSHA4ff926... della UI. PDF precedente riusato dopo identitàDOCX:
9pagine e medesima impaginazione,nessuna nuova certificazioneWorddesktop.
Bundle senzaDB/chiavi ricostruisce audit e4DOCX con codice archiviato.
29sessioni live e285file originali invariati;210altrifile protetti immutati.
Raw v12-narrator-holds-20261019-01/,backup separato docs/benchmarks.
Nessuna migrazione/upgrade implicito. Export conclusi non riaperti automaticamente;
un'eventuale nuova provaUI col contratto finale resta da autorizzare a parte.
Arresto dopo rapporto eDOCX,nessun avvio automatico E1 o altra fase.

## Rami V12: direttore e checkbox, replay 61 / chat 53 — 19 ottobre

Richiesta limitata ai due blocchi residui, completata con replay prima della UI.
[Rapporto](docs/rami-v12-direttore-checkbox-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-branches.json),
[otto tracciati](docs/benchmarks/2026-10-19-v12-branches-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-branches-checks.json).
Word/PDF/report in nuovi dati: V12-RAMI-REPLAY-61-20261019 e
V12-RAMI-CHAT-53-20261019. Nessun commit/push, refactor generale o framework.
FORM B0, fonti/gold, modello, prompt/schema globale, API/DB e writer invariati.

Condizione tecnica composta verificata con grammatica FORM esplicita
ruolo(per le società...) o altro ruolo(per le società...), scelta nominativa
della categoria della pratica nella ricevuta USER positiva pertinente e
asserzione SOURCE completa persona:ruolo di azienda. Stesso operatore già
grounded nel blocco confermato, stesso soggetto/binding per tutti i valori.
Non si riusa c_societa come se fosse c_dt: prove separate in branch_evidence.
S.r.l./partecipazione/ruolo/poteri distinti. Diniego, ruolo non provato,
persona/azienda diversa, conflitti o grammatica non supportata restano bloccati.
c_dt SKIP storico conservato, nessuna attestazione inventata o cambio del MODEL.

Checkbox: gruppo FORM completo di7controlli sotto IN QUALITÀ DI, attraversando
solo i blocchi pertinenti fino all'intestazione successiva. Validatore esistente;
cardinalità ancoraUNKNOWN, nessuna single/multiple inventata. Sola spunta positiva
da ricevuta CONDITION_TRUE esattamente corrispondente all'intera opzione/casella;
nessuna falsa rispostachoice, deselezione o altra spunta. Valore USER effettivo
derivato e rivalutato, non nuovo fatto SOURCE né nuova decisione. Grammatica CF
in maiuscolo non chiude la lista. Liste/controlli ambigui restano irrisolti.

Baseline52 riprodotta stessoSHA, offline rete vietata e narratore simulato:
60grounded invariate,8UNKNOWN→0 tramite prove, SOURCEtext51→59, USERtext1
conservato, checkboxUSER1. **60testi+1casella=61**, tutti52precedenti identici,
24soci conservati,0nuove scritture indebite osservate. OttoDT conformi alGOLD;
59/60testi conformi, sola carica completa attestata già nota.9pagine.

Una nuova UI isolata, sessione133483f76343416082b954f6f7bfd777, globale salvata
riusata suFORM/SOURCE/schema identici, conversazione/provider reali. Decisioni
storiche risomministrate soltanto sulle due domande effettive; niente preferenze/
attestazioni/designazioni/luogo-data. **Chat:52testi+1casella=53**,52precedenti
identici,24soci. In questa sessione tutti52testiSOURCE, nessuna domanda ridondante
qualifica. Backendc_dtTRUE e60reviewed, ma narratore sospende8DT dopo la risposta:
non scritti. Non sono più rifiutiSOURCE oUNKNOWN. Schemahold privo di motivi;
interpretazione delloSKIP/mancata esposizione branch_evidence sono ipotesi,
non causa certa. Hold non cancellati, nessun retry per migliorare il risultato.
Resta questo limite end-to-end da trattare separatamente, senza avvio automatico.

34test nuovi(31negativi),243mirati32,75s,**2601suite185,70s**,Ruff passati.
Setup errati/test preparati male conservati e distinti da riproduzioni valide.
Ultimo veto:2negativi «lascia il campo vuoto» prima falliscono, poi corretti;
rinvio della conferma distinto da richiesta di non compilare. Nessuna nuovaUI/
LLM: verifica indipendente finale conferma stessi audit e hashWord.
XML/CRC/posizioni/prestampato/report,4tabelle e13controlli verificati; solo p39.cb0
selezionata,12altre intatte,0deselezioni.9pagine in tutte le copie; viste3prima/
replay/chat e9replay, firma con linea nell'ultima. Giunzioni writer preesistenti
restano. Bundle indipendente senzaDB/chiavi rigenera audit eWord di entrambi.

Offline0LLM. Chat7chiamate reali(3router,3sintesi,1guard),61977token,
0nuoveglobali/1riuso. CostoUSDnonstimato. Primo router/guard trasportocompleto
nonacquisito, totali telemetria inclusi. Alias osservatore corretto soloharness
primaexport, checkpoint persistente conservato.10GET annullate su mount/reload,
0HTTPerrori acquisiti/0eccezioni pagina; download e refresh riusciti.
29sessioni live e285file originali immutati,207altrifile protetti invariati.
Raw v12-branches-20261019-01/, backup separato docs/benchmarks,DB/chiavi esclusi.
Nessuna migrazione/upgrade implicito, E1 fermo. Arresto dopo rapporto e DOCX.

## Copertura SOURCE V12: 42 → 52 scritture — 18 ottobre

Completata la richiesta sui 18 vuoti SOURCE, conservando le correzioni precedenti.
[Rapporto](docs/copertura-source-v12-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-source-coverage.json),
[18 tracciati](docs/benchmarks/2026-10-18-v12-source-coverage-trace.json),
[controlli](docs/benchmarks/2026-10-18-v12-source-coverage-checks.json).
Word/PDF/report in nuovi dati, suffisso V12-SOURCE-52-20261018.
Nessuna nuova LLM/UI, decisione USER, modifica FORM B0/modello/thinking/prompt
globale/schema/API/DB/retrieval/writer. Nessun framework, hardcoding, commit/push.

Tutti i 18 dati erano nelle SOURCE e nell'input, tutti proposti: zero omissioni.
Firmatario9: binding MODEL con citazione FORM nel paragrafo errato; riuso prima
attivo solo da VALUE e bloccato anche da proposte respinte. Ora la clausola
nominativa esplicita nella ricevuta CONDITION_TRUE accettata può attivare il
riuso, senza fabbricare altre decisioni. Identità SOURCE con nome completo/CF,
conflitti/omonimie controllati; carica SOURCE nominativa riferita allo stesso
operatore. Proposte fallite sostituibili solo per stesso soggetto/valore provato;
vecchio binding rifiutato e audit conservati. Nessun dato personale provato da USER.

Comune iniziale: prova FORM solo marker, ricostruita dalla continuità fisica
adiacente «con sede in», stesso operatore finale grounded e senza barriere.
CF direttore: prefisso CF letterale del proprio campo, eliminata dalla nuova
prova la parola citata nel paragrafo sbagliato, originale conservato. Tre proprietà
di albo riconosciute da identificatori deterministici e stessa iscrizione
(Ordine e numero), mai dal solo nome. Nessun ruolo/potere trasferito.
Controlli località estesi al medesimo contesto per respingere indirizzi completi;
operatore rivalutato dopo tutti i controlli, anche se viene dopo nel catalogo.
Sintesi tollera il form_evidence nullo del binding rifiutato conservato.

Replay isolato, rete vietata, narratore simulato; grounding/persistenza/export
reali e verifica manuale dei nuovi valori. Baseline42 riprodotta stessoSHA;
SOURCE grounded/revisionate46→60, applicabili42→52, fisicamente41SOURCE+1USER
→51SOURCE+1USER=52. Dieci nuovi dati:9firmatario+Comune. Tutti42precedenti
identici,24soci conservati,0nuove scritture indebite osservate. UNKNOWN4→8:
ottoDT ora grounded ma rinvio c_dt invariato, nessuna scrittura automatica.
Quattro testi USER e cinque gruppi preferenze/attestazioni/esecutori/integrazione/
luogo-data invariati e ancora da decidere; nessun nuovo firmatario o attestazione.

Società: ricevuta positiva congruente con casella p39.cb0 dimostrata. Manca un
gruppo checkbox valido nella risposta MODEL. La lista fisica distribuita contiene
sette alternative: validazione single la rifiuta per incompletezza locale;
multiple strutturalmente accettabile non dimostra cardinalità semantica. Nessuna
ipotesi diagnostica persistita o spunta aggiunta. Limite tecnico ancora aperto.

GOLD:51/52 scritture conformi allo scorer, una carica completa attestata
«amministratore unico e rappresentante legale» contro «rappresentante legale».
Aspettative congelate, differenza dichiarata. XML/CRC/posizioni/report coerenti,
4tabelle/13controlli intatti,9pagine prima/dopo. Viste1/3/9; pagine3/9 raster
identiche; firma con linea nell'ultima pagina. Verifica LibreOffice, non Word.
SHA DOCX58f1179d4cff7c6c1de4f2e886c524906c1be618e1025a67d97288f7c7323f2b.

43 nuovi casi generici,304mirati32,57s e2567suite finale185,17s passati,Ruff.
Red/fallimenti intermedi e primo replay interrotto conservati. Verifica bundle
senza DB/chiavi ricostruisce stesso audit e DOCX.29sessioni e285file live invariati;
raw v12-source-coverage-20261018-01/, backup separato in docs/benchmarks.
Zero token/costi provider aggiuntivi, nessuna misura di accelerazione o qualità
autonoma di una nuova risposta LLM. Nessuna migrazione/upgrade implicito:
rivalidazione e nuova revisione necessarie sui campi cambiati. E1 fermo.
Arresto dopo questo DOCX e rapporto; non avviare altre fasi automaticamente.

## Residui V12: equivalenza tipografica e domande USER — 18 ottobre

Completata la richiesta sui soli residui, senza rifare revisioni/citazioni.
[Rapporto](docs/residui-v12-dialogo-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-residui.json),
[controlli](docs/benchmarks/2026-10-18-v12-residui-checks.json).
Word/report/domande in nuovi dati, suffisso V12-RESIDUI-20261018.
Nessuna nuova LLM, UI o modifica FORM B0/modello/thinking/prompt globale/schema/
API/DB/writer. E1 fermo; nessun framework, hardcoding, commit o push.

Chiave dei soli valori con NFC/spazi/lower(), dopo identità esatta soggetto/
entità/dimensione/proprietà; valori originali e citazioni conservati. Niente
casefold espansivo, sinonimi, accenti eliminati, unione persone o ruoli trasferiti.
Due falsi conflitti Elisa eliminati: p45.s1 socio e p52.s0 direttore. Una REVIEW
esplicita con alternative soltanto ridondanti è rifiutata, non promossa a VALUE.
Binding SOURCE e validatori valori identici; differenze AST globali limitate
ai due punti di confronto delle alternative e alla nuova chiave dei valori.

Nuovo helper ristretto alle istruzioni FORM esplicite, non alle affermazioni
coverage del modello: cinque decisioni su categorie/fasce, attestazioni complete,
esecutori, integrazione, luogo/data. 67 celle preferenze raggruppate; firma esclusa,
campi/proposte SOURCE e risposte acquisite/rinviate non richiesti di nuovo.
Fallback massimo3 domande se il narratore le omette. Nessun gruppo checkbox
inventato. Le risposte raggruppate sono ricevute USER con write_authorized=false:
nessuna scrittura/spunta/applicabilità automatica. La distribuzione verificata
delle risposte nelle destinazioni rimane un limite esplicito, non implementato.

Offerta export parziale anche a domande aperte. Con zero valori l'avviso esplicito
della copia vuota è tracciato; READY/errore/consenso restano controllati. Prima
suite individuava una regressione sull'export vuoto generico, corretta conservando
il test precedente. PRESENTATION_VERSION=3 su nuove sintesi/ripresa esplicita;
nessuna migrazione o aggiornamento implicito delle sessioni storiche.

Replay isolati con rete vietata e narratore simulato, validatori/persistenza/
export reali: baseline44→46grounded/reviewed, applicabili41→42, UNKNOWN3→4
(nuova qualifica DT comunque rinviata). Storico immutato41SOURCE+1USER=42;
0valori persi/cambiati,0nuovi indebiti,24soci,0spunte. DOCX con stesso SHA
4a29f7d306a6664b88208f8ba88bff5738123310a84853ff4e770f69dae126c8.
Replay snapshot prima della risposta sulla qualifica:42SOURCE/0valoriUSER,
stesso Word, senza quel chiarimento; restano societàTRUE e DT SKIP, non senzaUSER.
Verifica indipendente del bundle senza DB/chiavi ricostruisce stesso audit/Word.

Restano18vuoti SOURCE:9firmatario(binding/riuso non attivato da ricevuta VALUE),
Comune iniziale(FORM solo marker),8DT(4UNKNOWN/rinviati,1FORM,3attribuzioni).
Non equivalgono a dati assenti dalla KB. Quattro testi USER, preferenze e due
caselle attendono decisioni reali; casella società già decisa ma senza gruppo
validato resta limite tecnico. Allegati/dichiarazioni personali e firma separati.

45test nuovi;221mirati passati29,69s;**2524pass181,97s** suite finale,Ruff passato.
Red corretto sul codice originale33fail/12pass; errori di setup e suite intermedie
conservati.29sessioni live/versioni/stati e285file uploads+knowledge invariati;
206file protetti salvo4modifiche previste,più helper/test nuovi. Raw
v12-residui-20261018-01/, backup separato in docs/benchmarks, DB/chiavi esclusi.
Zero token/costi provider aggiuntivi; nessuna misura di accelerazione o nuova
valutazione di qualità del narratore. Arresto dopo replay e rapporto.

## Revisioni conservate, citazioni e nuovo export soci — 18 ottobre

Implementati i primi due interventi autorizzati, poi prova UI/provider reale.
[Rapporto](docs/correzione-revisioni-soci-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-review-soci.json),
[24 tracciati](docs/benchmarks/2026-10-18-v12-review-soci-trace.json).
Word/PDF/report/conversazione in nuovi dati, suffisso V12-SOCI-24-20261018.
FORM, modello/thinking, schema globale, validatori SOURCE, API e writer invariati;
nessun commit/push, framework o E1. Modifiche locali precedenti conservate.

V12 conserva impronte delle revisioni su proposta, fatto/soggetto, binding/prove,
destinazione FORM, condizioni e dipendenze. Solo ricevute immutate riusabili;
nuove/cambiate nelle finestre successive da40. PENDING/auto_continue esistente
fino a revisione completa, errore ferma export/avanzamento. Hold persistenti;
applicabilità USER separata, nessuna UNKNOWN→TRUE o RESOLVED automatica.
Sessione pubblica filtra le revisioni rispetto all'audit completo. Nessuna
migrazione/upgrade implicito di sessioni storiche; vecchie V12 senza impronte
vengono riesaminate solo se si richiede una nuova sintesi. Metadati non nel prompt.

Prompt tabelle corretto: massimo2span letterali separati titolo+riga della
persona, stessa tabella; vietate quote concatenate saltando righe. Funzioni e
classi dei validatori identiche per confronto AST. Nessuna riparazione fuzzy.

Replay controllati offline, narratore simulato, persistenza/export reali:
vecchio41→54(53SOURCE+nomeUSER), soci16→24SOURCE; finestre40/5/0/8. Dopo8riusi
Leonardo nessuna review persa e5DT prima fuori finestra finalmente esaminati.
Altrooutput27→43SOURCE correggendo solo quote binding; soci8→24SOURCE, 0valori
indebiti nuovi. Baseline27 riprodotta con stesso SHA; rifiuti necessari mantenuti.
Nel54 una differenza gold stretta su carica più completa attestata, già nota.

Nuova UI isolata sessione19be5edcf19e49acb2e25a7dab370000, export09ffd84febfb48d6a8b64f00bb8d1656.
JSONinputglobale interamente identico al precedente T0V1/56SOURCE/FORM/schema;
diverso solo system prompt.55fatti/60assegnazioni,44grounded/reviewed,0held,
finestre40/4/0/0. Tre DT restanoUNKNOWN/rinviati e non scritti.42scritture:
41SOURCE+1USER,42/42 conformi al gold,18target fattuali vuoti. Soci24nelDOCX,
ma **23SOURCE+1USER**, non24SOURCE autonome. Tutti24binding verificati; due
forme Ingegnere/ingegnere generano alternative per Elisa. Solo dopo domanda
effettiva scelta USER della forma documentata, qualificazione non inventata.
Rinvio separato della confermaDT, non nuova attestazione o nomina dedotta.
Chiarimenti aggiuntivi registrati e distinti dal copione. T1completo non raggiunto.

Prima/dopo reale27→42:16nuovi campi soci,1CFDT perso per nuova quoteFORM
inesatta,26valori comuni identici. Campione singolo, risposta/dialogo diversi:
nessuna stabilità o causalità generale dimostrata.18vuoti:9firmatario,Comune
iniziale,8DT. Gruppicheckbox assenti;0spunte. Preferenze/designazioni/attestazioni/
luogo-data mai chiesti; dialogo resta fase separata descritta nel rapporto.
Falso conflitto tipografico non corretto qui. Niente normalizzazioni indiscriminate.

XML/CRC/posizioni/report esatti;4tabelle,13controlli,123vuoti prescritti intatti.
PDF9pagine contro10prima; viste1/3/9,soci completi,firma vuota con testofinale;
giunzioni prestampato e limiti Word persistono, writer invariato.
11chiamate(1globale,4narratori,4router,2guard),usage/HTTP completi.181.776token:
133.102input+48.674output,32.433reasoning. Globale174,83s,POST194,96s;
costo stimato0,04563USD, non fattura. Nessuna accelerazione dimostrata;
reasoning maggiore e chiarimento extra distinti dall'inputFORM invariato.

20casi nuovi. Red iniziale11fail/2pass; prima suite2477pass/2fail per vecchia
attesa di ripetere proposte già esaminate, aggiornata preservando verifica prove.
**Suite finale2479pass in288,71s; Ruff passato.** Setup falliti conservati,
nessun retry qualitativo. 29sessioni live/versioni/stati e273file storage originali
immutati;205file protetti salvo modifiche previste. Raw v12-review-soci-20261018-01/.
Runtime isolati arrestati;istanza originale8000/5173 conserva reload e resta
disponibile per nuove conversazioni. DB/chiavi privati fuori dal backup.
Backup verificato:246file,67.273.364byte non compressi,35.108.391compressi;
SHA256 `3d5d90eee93a8ca4e74c7be7a165ba3351674a1eb19dfd9ffc3adce037f40876`.
Video/trace completi inclusi, scan credenziale negativo, link e diff--check validi.
Terminati correzioni e verifica; prossima fase separata: domande della pratica.

## Prova reale UI Minervino V12 e diagnosi — 18 ottobre

Eseguita la prova richiesta su copia isolata di DB/storage/Company KB, UI reale
Chromium e provider reale, senza mock. Nessuna modifica applicativa, prompt,
validatori, writer o FORM; nessun commit/push. V12 corretta resta il riferimento,
E1 non avviato. [Diagnosi](docs/diagnosi-e2e-v12-minervino-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-e2e-minervino.json),
[24 tracciati soci](docs/benchmarks/2026-10-18-v12-e2e-soci.json).
Word/PDF/report/conversazione in nuovi dati, suffisso V12-E2E-REALE-20261018.

Nuova sessione isolata d538c77c599a4860aa0114c534ce6f0c, originale live intatto.
T0 congelato Minervino V1 con società di ingegneria e Leonardo già scelti;
diverso dal solo compila precedente. Il sistema chiede solo conferma della
partecipazione/rappresentanza, poi export. Nessuna delle quattro risposte del
copione somministrata perché non richiesta: T1 completo non raggiunto. Non è
un confronto controllato del solo prompt e non va presentato come tale.

46 fatti,60 assegnazioni SOURCE, tutti60target proposti:58valori conformi stretti
al gold,1carica più estesa attestata,1Via già stampato da evitare.27grounded,
27reviewed,27SOURCE scritte,0USER,0held,0grounded ancoraUNKNOWN dopo ricevuta.
27/27scritture conformi al gold;33SOURCE vuoti:24binding rifiutati(8firmatario,
16soci),2FORM marker-only(Comuneiniziale,provinciaresidenza),7direttore con
valori citati come socio/property non supportate. Zero valori indebiti osservati
nelle scritture non significa copertura o accuratezza generale.

Soci nuovi24proposti corretti,8grounded/reviewed/scritti(Luca). Per Elisa/Andrea
quote binding concatenate saltano righe e non sono estratti letterali SOURCE;
rifiuto corretto della citazione, dati effettivamente presenti. Controprova
offline con sole citazioni titolo+riga, schema/validatori/fatti invariati:
27→43grounded,+16corretti,0perse. Nessuna sessione/export cambiata. Tentativo
diagnostico iniziale con4span respinto(max2),27→19; fallimento conservato.

Vecchio16 spiegato più precisamente: tutti24soci giàgrounded e revisionati;
dopo8riusiSOURCE le8destinazioni Andrea passano33–40→41–48. Narratore ricrea
prime40 e sovrascrive reviewed_candidate_ids:8review giàvalide perse,0held.
Proposte persistono, condizioni confermate, export coerentemente le esclude.
Altri5DTgrounded mai revisionati. Correzione proposta: revisioni con impronta
e finestra nuove/nonrevisionate, non union cieca o accettazione automatica.

Bari iniziale sempre respinto per FORM;BA iniziale questa volta passa citando
tel.dopo marker;Bari/BA societari scritti corretti. Choice_groups vuoti,checkbox
0:casella società manca pur avendo USER;veridicità/esecutori e6preferenze/4testi
USER attendono risposte mai chieste. Pool1→0:non limite3domande. Coverage
manual_input non crea slot interrogabili. Firmatario presente T0 e ricevuta
condizione, ma senza VALUE nominativo; proposta respinta impedisce fallback
e riuso. Non certificare positivamente questo percorso UI dal solo replay.
Natura giuridica/partecipazione/poteri distinti nel rapporto;nessuna procura
o designazione dedotta. Interventi minimi solo proposti, non implementati.

Sette chiamate(1globale,2narratore,3routing,1guard),153.384token totali.
Globale142,10s,76.616input/40.083output,24.507reasoning. CinquePOST154,76s;
browser235,50s include attese. Costo stimato0,0390–0,0427USD, non fattura;
6.122token(routeriniziale+guard) senza split/grezziHTTP, limite dichiarato.
No nuoveLLM per le controprove. XML/CRC/posizioni/report esatti;4tabelle,
13controlli e123testi da lasciarevuoti preservati. PDF10pagine contro9gold;
viste1/3/10 e blocco soci gold. Firma isolataa10 e giunzioni restano.

205file protetti,29sessioni live/versioni/stati,273file storageoriginali
invariati. Suite2459 precedente non rieseguita per questa diagnosi. Servizi
isolati arrestati, originali8000/5173 ancora200. Backup pubblicabile conserva
video completo/trace campionata5s;trace originale936MiB solo locale,hash nel
descrittore;DB/chiavi privati esclusi. Raw ui-v12-e2e-20261018-01/.
Backup verificato:115file,40.694.164byte non compressi,22.891.729compressi;
SHA256 `34c52bafb88e302f7e6ce4422af49c21fd28d1d8e8e6c94c374f0e7e034e9209`.
Scan della credenziale attiva negativo, link del rapporto e git diff--check passati.
Terminato dopo diagnosi. Prossimo passo da concordare: difetto review e prove
letterali, poi confronto E1 con T0 e protocollo identici; nessun avvio implicito.

## Correzioni mirate compilato(6), consegna parziale — 18 ottobre

Implementazione richiesta dopo la diagnosi; questa sezione sostituisce il
precedente punto «fermarsi dopo diagnosi». Nessun commit/push, architettura
globale B0 conservata, E1 non integrato. [Rapporto e prima/dopo](docs/correzioni-ui-compilato6-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-ui-compilato6-fix.json).

Prompt SOURCE allineato a titolo/intestazioni/riga e ai collegamenti realmente
supportati dai binding, senza modificare il verificatore. Una sola nuova
chiamata globale con input/schema/modello/thinking identici a compilato6:
45fatti/51assegnazioni/45grounded, contro19/26/24; soci24/24proposti e grounded,
CFdirettore proposto. Campione singolo, non dimostra stabilità. Dopo la prova
precisato ulteriormente il limite cross-record CF/provincia e propertycanoniche;
la precisazione finale non è stata rigenerata. Entrambi i prompt conservati.

Riuso locale dopo nomeUSER: blocco FORM esplicito, profilo nominativo completo
con CF, controlli conflitti/omonimie anche in tabelle, citazioni distinte di
identità/valore e società per carica. Otto nuove proposte dopo Leonardo senza
LLM; USER identifica la persona, non prova la biografia. Componenti letterali
Lecce/LE, Bari/BA, indirizzo Amedeo24 dopo via prestampato. Carica attestata
solo se il documento identifica lo stesso operatore SOURCE grounded. Nessun
recapito personale inventato, ruolo trasferito o potere speciale dedotto.
Fallback della sola domanda sul firmatario quando il modello la omette e il
blocco è riconosciuto. Altri layout/identità incomplete restano irrisolti.
Solo V12; versioni precedenti conservate senza nuove domande/riuso impliciti.

Proposte derivate ancora REVIEW_REQUIRED/GROUNDED_PROPOSAL, zero RESOLVED.
Rivalidazione output originale+riuso prima export e al salvataggio, nessun
bypass SOURCE, condizioni preservate. Audit originali intatti, revisioni in
file separati sul medesimo endpoint di report; nessuna API/colonna DB nuova.
Narratore riceve indizi SOURCE distinti da omissioni, scarti e atteseUSER;
assenza/recupero non dimostrati restano tali. Formulazioni di assenza riprodotte
attivano riepilogo backend prudente: filtro lessicale, non giudice universale.
Motivazioni storiche dei vuoti non riproposte per valori recuperati/USER.

Export reali da copie isolate, narratore simulato e routing storico rigiocato:
compilato6 25→33scritture(32SOURCE+nomeUSER), B0manuale48→56(55SOURCE+nomeUSER),
nuova proposta41(40SOURCE+nomeUSER). Nuova proposta53grounded dopoUSER, ma review
limita40:13grounded non revisionate, soci16/24scritti; limite non modificato.
Grounded ancoraUNKNOWN dopo ricevuteUSER:0 nei tre replay; condizioni originali
semanticUNKNOWN non trasformate in TRUE. B0 conserva reviewmanuale propria,
nessuna ricevuta importata dalla sessione UI. Non sono tre nuove prove UI reali.

Word/PDF/report in nuovi dati: UI-CORRETTA-PARZIALE, B0-03-RIUSO-SOURCE e
PROMPT-SOCI-PARZIALE, suffisso20261018. Target SOURCE testuali vuoti27/4/19.
Una discordanza gold per ogniexport: carica completa attestata anziché il solo
rappresentante legale. Scorer/gold congelati:32/33,55/56,40/41 conformi stretti,
zero nuove accettazioni fattuali indebite osservate, non accuratezza generale.
Difetto intermedio viaVia riprodotto e corretto per componente letterale;
nessun ritocco al writer.

Irrisolti:2FORM marker-only Bari/BA iniziali; checkbox società senza gruppo
grounded;3legami professionali nuovi non supportati dalle citazioni/property
usate. Comune-indirizzo respinto correttamente. Fax+390800002041 esplicito
SOURCE-53 integrazione-company, aziendale/sintetico. Non scambiare queste
lacune per assenza KB. Nessuna spunta automatica. Writer/FORM B0, API routes,
schema DB e fixture/gold invariati; giunzioni di testo e firma a pagina10
restano limiti di presentazione.

XML/CRC/posizioni/report esatti, solo word/document.xml modificato;4tabelle e
13controlli invariati. RenderingLO10/9/9pagine, visteUI1/3/10,B0p3,promptp3;
MSWord non verificato. Nuovo provider136,7s,76.408input/37.735output di cui
24.441reasoning; costo/tempo totaleUI non misurati. RiutilizzoUSER zeroLLM.

Test prima delle correzioni e tentativi falliti conservati nel raw
ui-compilato6-fix-20261017-01/. Suite finale **2459pass in172,68s**, Ruff e
git diff--check passati. Ultimo guard V12 verificato anche contro versioni
precedenti. Frontend invariato/non ritestato. Tre export finali superano
nuovamente i controlli di freschezza col codice definitivo, senza scritture.
29sessioni live/versioni/stati, schemaDB e22artefatti originali invariati;
downloadcompilato6 originale intatto. Controlli e backup collegati nel rapporto.

Backup verificato:349file,32.512.735byte non compressi; SHA256
`8cba065a6d3925e9844f80a99bb5ffb62ee2ae27e9d63658210345d51d92af54`.
DB/credenziali esclusi. Valori precedenti conservano anche i limiti originari
delle citazioni, tra cui provinciaDT citata nel nome dell'Ordine: nessuna
ricertificazione implicita di tutte le vecchie proposte.

Fermarsi dopo consegna. Restano da concordare separatamente limite40,
ancoraggiFORM iniziali, gruppi checkbox e ulteriori formati SOURCE/FORM.

## Diagnosi della prova UI compilato(6), nessuna modifica — 17 ottobre

Utente ha provato la UI e chiesto solo analisi. Download root domanda-iscrizione.compilato(6).docx
identico all'export850ebea2fa464ba0aa6a881d5d8313d4; sessione f06e75dd1ecf4c0fae668668c153a9df,
conversazione conv-423c9cc6f0f3438d. [Rapporto](docs/analisi-ui-compilato6-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-ui-compilato6.json).

25 scritture fisiche:24SOURCE+nomeUSER.25 valori conformi al gold, nessuna
discordanza di valore osservata, senza equiparare gold a prova delle citazioni.
35 target SOURCE vuoti:8anagrafica/carica firmatario,24soci,1CFdirettore omessi;
2Comune/provincia generali proposti correttamente ma FORM marker-only respinto.
Leonardo ha nascita/residenza/CF/carica nella SOURCE -53/-54 già nell'input.
Mancano recapiti personali telefono/email/PEC, distinti da quelli aziendali.

T0 era solo compila, trasmesso correttamente. Firma scelta dopo la globale:
prima nome incompleto Leonardo [COGNOME DA COMPLETARE], poi Leonardo Montemurro.
apply_replies aggiorna solo p12.s0; nessuna ricerca della persona nella KB o
nuove proposte per gli8campi. Nelle sintesi successive manca il recordSOURCE
anagrafico, resta l'audit congelato e il pool infine vuoto.3domande è limite
perturno, non causa diretta del mancato completamento.

Modello riconosce tabella soci ma non emette fatti/assegnazioni/binding:
"Soci presenti in tabella aziendale, ma il ruolo 'socio' non è attestato nel
formato richiesto per il binding". Prompt attuale ancora descrive vecchi
formati e richiede ruolo/valore nello stesso chunk: disallineamento con
verificatore più capace, causa probabile ma non isolata con nuova provaLLM.
ElisaDT7/8; CF omesso perché non nella rigaDT, pur essendo in riga soci-54
con stessa persona/ordine/8421.7recuperi fact_source_record registrati nel
run reale confermano che le correzioni sono operative, non codice vecchio.

Narratore dichiara erroneamente assenti soci eCFdirettore. ROLEhint soloDT
con proposte, nessuno per soci; unassessed_source_roles vuoto.24grounded tutte
revisionate/scritte, held0: limite40 non raggiunto.2condizioni audit UNKNOWN
entrambe confermateUSER, non causano scarti. Fonte56/FORM/schema identici a B0;
nuova risposta reale diversa dal replay48manuale, confronto non controllato.

XML/report/slot esatti, altrepartiZIP/4tabelle/13controlli invariati. PDF10pagine,
viste1/3/4/10:2giunzioni senza spazio, firma vuota isolata a10. Non modificare
il Word, prompt, writer o controlli automaticamente. Analisi storica125,8s,
3sintesi6,6s; usage globale76.163input/32.252output, di cui23.325reasoning.
Zero nuove chiamate, replayvalidatore, scritture DB, codice applicativo o test;
raw ui-compilato6-20261017-01/. Nessun commit/push. Fermarsi dopo diagnosi.

Integrità verificata: 216 file di codice/test e 29 sessioni invariati, 22
artefatti originali identici alle copie. [Backup](docs/benchmarks/2026-10-17-ui-compilato6-audit.tar.gz)
con 64 file, 4.672.942 byte non compressi; SHA-256
`06cde9948a3751105511866cf26f673ed1a9864b938d48d2bd567986a192c0ef`.

## Versione corretta disponibile per la prova UI — 17 ottobre

Richiesta successiva: usare il sistema dalla UI. Avviato ./start.sh con il
codice corrente, frontend5173/backend8000; servizi lasciati attivi.
[Apri Minervino](http://localhost:5173/projects/minervino-di-lecce-elenco-sia),
[guida e verifiche](docs/prova-ui-compilazione-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-ui-binding.json).

Le correzioni sono già nei moduli del motore globale usato dalla chat, non
in un secondo motore da sostituire. Nessun codice applicativo nuovo: attivi
binding, Comune, FORM e trasporto USER già implementati. Form completo B0,
E1 compatto/indice non collegati. UI reale apre progetto e mention; health,
frontend e proxy200. Modulo live e56SOURCE identici al benchmark, input
canonico senzaUSER uguale a B0. Nessun dato del gold importato.

298 test backend mirati passati36,28s e8 E2E desktop/mobile23,9s con provider/API
simulati. Prima E2E7pass/1fail per vecchia scritta attesa; corretta soltanto
l'asserzione in frontend/e2e/global-compilation.spec.ts sullo status accessibile
Analizzo il modulo. Lint frontend passato. Smoke browser live in sola lettura,
nessun messaggio/provider, nuova sessione o export creato durante le verifiche.

28 sessioni originali/versioni/stati invariati, conteggi principali invariati.
Backup preventivo DB privato .tools/ui-binding-20261017-01/before-start.db;
raw ui-binding-20261017-01/. Nessun commit/push o modifica writer/modello/thinking.

Per la prova partire da NUOVA conversazione e @domanda-iscrizione.docx, fornendo
le decisioni della pratica; le vecchie sessioni mantengono l'audit storico.
Le48scritture offline includevano revisione manuale: ricevute/review non
trasferite alla UI. Narratore attuale limita a40proposte SOURCE per passo;
limite registrato, non corretto in questa attivazione. UNKNOWN, scope c_p39,
checkbox e spaziatura non aggirati. La prossima prova qualitativa è dell'utente,
non è ancora un nuovo risultato con provider reale. Non avviare chiamate AI
automaticamente in risposta a questo punto di ripresa.

[Backup verificato](docs/benchmarks/2026-10-17-ui-binding-audit.tar.gz):22file,
783.192byte non compressi, SHA256
`cc25fbe50c3dad5253a525f5184a36b0fe97be297f0251a885a6d16fa8cf18a9`.
Esclusi DB privato e log server ancora in scrittura; incluso snapshot del log.

## B0-03: export parziale reale e verificato — 17 ottobre

Piano operativo eseguito su copia isolata; sostituisce il precedente punto
«piano non eseguito». [Word](<nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.docx>),
[PDF](<nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.pdf>),
[rapporto](docs/export-b0-03-verificato-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-b0-docx-verified.json).

Esito fisico: 48 valori, 47 SOURCE e nome USER della stessa sessione.
47 grounded attuali; 21 vecchie review ancora valide +26 pendenti riesaminate
manualmente con FORM/SOURCE/validatori esistenti. Nessun valore corretto per
avvicinarsi al gold, aperto solo dopo export. Tre rifiuti conservati: Comune
p41.s1 e province Elisa p46.s0/p53.s2. Precedente Word 23 valori, 22 conformi;
ora 48 conformi ai target sintetici, 26 aggiunti e 1 Comune errato rimosso.
Revisione manuale assistita, non nuova misura dell'autonomia del modello.

Ricevute proprie di ee86e66383ac4e5d9df90cf2b3ea3454: c_p39, nome p12.s0,
consenso storico all'export, identiche prima/dopo. Nessun trasferimento INDEX.
Audit attuale riprodotto esattamente e conservato nel report; audit storico
intatto. UNKNOWN audit 1 condizione/47 SOURCE ancora conditional; overlay
USER conferma c_p39, selezionati con condizioni non confermate 0. Il T0
identifica l'operatore; p39 non è clausola letterale dei nove dati generali.
La dipendenza tecnica aggiunta dal modello resta nell'audit, non corretta:
il guard senza conferma continua a rifiutare409 anche quei nove campi.
In questo scenario la conferma pertinente esiste, verificata insieme a
natura S.r.l., partecipazione, rappresentanza e sottoalternativa direttore.
Non dedurre da questo una regola generale o la risoluzione del limite.

Export generate_draft esistente su .tools/b0-docx-verified-20261017-01/export-01;
sessioni originali/live intatte. Zero nuove chiamate, risposte USER, checkbox,
modifiche applicative/writer/FORM/fixture, framework, commit/push. La nuova
review è manuale di Codex su istruzione utente; il report standard scrive
reviewed_by=USER, con autore/metodo reali chiariti in completed-review.json.

Controlli: 48 valori estratti esattamente dai propri slot, altri segnaposti
invariati; ZIP/CRC, 12 relazioni, 246 paragrafi+avviso, 4 tabelle e 13 controlli
conservati; sola word/document.xml modificata. Guard409 senza conferma e422
sui3 rifiuti. PDF9 pagine contro10 originale, tutte9 viste; firma vuota e
unita all'etichetta a pagina9, a/b/c/d preservati. Cinque giunzioni senza
spazio su4 paragrafi (professionaleOrdine, Adella) registrate e non corrette.
Stato needs_review; 12 target SOURCE ancora vuoti, T1 e scelte native separati.
Nessuna dichiarazione di documento completo/presentabile o paginazione MS Word.

Raw b0-docx-verified-20261017-01/, con log preliminari falliti conservati;
nessuna suite/Ruff nuova, ma verifiche dirette dell'export e del documento.
DOCX SHA256 6605dcc91ab823cc21d77618c2991feade366cce1137d4b8138600f1c051a889.
Fermarsi dopo consegna; prossimi interventi da concordare separatamente.

Integrità finale: 11.455/11.455 file protetti invariati, nessun codice/test
aggiunto. [Controlli](docs/benchmarks/2026-10-17-b0-docx-verified-checks.json),
[backup](docs/benchmarks/2026-10-17-b0-docx-verified-audit.tar.gz): 75 file,
10.911.253 byte non compressi; SHA256
`b396c7d7ba20d80463466ae03f492279585d26e5a930d8d81bd1ab61538172e2`.

## Applicabilità UNKNOWN: diagnosi e piano, nessuna modifica — 17 ottobre

Fase binding conclusa, non riaperta. Nuova richiesta: spiegare applicabilità,
SOURCE/USER e proporre percorso minimo offline al DOCX, senza cambiare controlli.
[Rapporto](docs/applicabilita-b0-index-2026-10-17.md),
[registro e misure](docs/benchmarks/2026-10-17-applicability.json),
[bundle](docs/benchmarks/2026-10-17-applicability-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-applicability-checks.json).

Tre condizioni MODEL, tutte semantic/fact_ids=[] e UNKNOWN: B0 c_p39 copre
47 proposte (9 generali operatore, 8 società, 23 soci, 7 direttore); INDEX c_op
9 generali e c_branch_soc 16 società/direttore. B0 mescola identità operatore,
qualità rappresentante e ramo societario: p14–p17 non hanno come clausola
letterale p39. Sottoalternativa p50 distingue responsabile progettazione
per società professionisti e direttore tecnico per società ingegneria.
Forma S.r.l., attività, partecipazione e rappresentanza non equivalenti.

Ritrovato USER proprio di B0-03: sessione ee86e66383ac4e5d9df90cf2b3ea3454,
c_p39=true e nome Leonardo in p12.s0, più consenso storico all'export parziale.
Audit ancora UNKNOWN per disegno: apply_replies salva dialogue.answers,
export_selection usa l'overlay USER. Gli ultimi replay puri non includevano
questo dialogo. INDEX-01 originario fallisce prima delle scritture di sessione;
il replay con USER prendeva c_soc/c_oe da INDEX-03 tramite mapping esplicito,
solo test separato. Non trasferire ricevute automaticamente fra sessioni.

SOURCE -43 prova forma S.r.l. e descrizione attività; -53 prova Leonardo
amministratore/rappresentante dal 2 ottobre e cessazione Luca il 1 ottobre;
-54 soci, -45/-55 Elisa direttore. Sono ruoli, non scelta del firmatario,
mandati RTP o poteri speciali. La scelta di Leonardo è USER, la carica SOURCE.
Requisiti normativi e dichiarazioni personali non certificati da questi dati.

Controlli puri nuovi, senza writer/DB: 47/47 valori B0 e 25/25 INDEX passano
il validatore usato prima della scrittura senza trasformazioni; passa anche
il nome USER B0. Proiezione read-only del nuovo audit sul suo dialogo: vecchie
22 SOURCE revisionate diventano 21 valide (Comune p41.s1 respinto); altre 26
grounded non ancora revisionate. Nessuna nuova review o conferma creata.
Due output senza choice_groups, checkbox p39.cb0 priva di proposta: una
conferma di applicabilità non spunta un controllo Word. T1 non chiesti/registrati.

Piano proposto, non eseguito: copia isolata B0 con stessi artefatti e ricevute,
verifica manuale del significato/ambito c_p39, revisione 26 nuove proposte,
export tramite servizi esistenti e consenso storico del test, controllo XML,
report, PDF e hash. Obiettivo pianificato 47 SOURCE + 1 nome USER, non una
nuova misura DOCX; nessuna firma o checkbox forzata. Restano 12 destinazioni
SOURCE vuote dopo quel nome, scelte native e T1 da trattare separatamente.
Per i target SOURCE del modello, lacune B0 13 (10 omissioni/3 rifiuti), INDEX
35 (33 omissioni/2 rifiuti): gold solo valutazione, nessuna nuova proposta.

Nessuna chiamata LLM, modifica ai controlli, sessione live, valore UNKNOWN,
modello/API/writer/FORM/fixture o output precedente. Nessun DOCX, commit/push
o nuovo framework. Suite/Ruff precedenti non rieseguiti; verifiche documentali,
73 controlli puri di valore, proiezione, JSON/diff/hash. Raw applicability-20261017-01/.
Non avviare automaticamente l'export o l'implementazione del piano.

Integrità: 11.092/11.092 file protetti invariati, nessun file aggiunto nei
percorsi protetti; 14 artefatti letti invariati. Backup verificato: 21 file,
2.573.411 byte non compressi; SHA-256
`4c7d1f1f6e20d024d7c9193f94f25a5e060fea68189c44dc97b6c9659a78b2a7`.

## Ultima correzione SOURCE: replay concluso e arresto — 17 ottobre

Richiesta successiva alla diagnosi: recuperare prima le quattro prove complete
del binding e poi affrontare titoli/date/identità, con negativi e replay dei
due output fissi. Implementazione confinata a compilation_global.py e
compilation_role_records.py; nuovo test_compilation_binding_identity.py.
Writer, API, modello, FORM B0 e prompt invariati. Nessun commit/push.
[Rapporto](docs/correzione-binding-source-finale-2026-10-17.md),
[misure e tracciati](docs/benchmarks/2026-10-17-binding-final.json),
[bundle](docs/benchmarks/2026-10-17-binding-final-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-binding-final-checks.json).

Baseline degli ultimi audit riprodotta esattamente. Primo passo già misurato:
B0 38→42 grounded, quattro recuperi conformi; INDEX 23→23, zero recuperi.
Tutti ancora condizionati, 0 RESOLVED/0 scritture. Raw durevoli:
backend/data/compilation-audit/binding-final-20261017-01/.

Implementati confronti di titoli solo per nominativi e date calendariali
equivalenti, senza riscrivere i valori. Collegamento tra record limitato a
CF e provincia dell'iscrizione; nome completo e CF condiviso oppure ordine
e numero condivisi, con conflitti/omonimie controllati nei record strutturati.
Per la provincia è richiesta la stessa iscrizione anche con CF concordante.
Identità/ruolo/valore tracciati separatamente; applicabilità invariata.
SOURCE aziendali e del progetto autorizzato ammesse, General esclusa; scope
e ruolo preservati. Nessuna unione basata sulla sola somiglianza del nome.

57 nuovi casi, 274 mirati passati in 18,92 s; Ruff passato. Log red e
controesempi conservati: quote, conflitti, record di altra persona e limite
800 caratteri delle citazioni. Prima suite completa interrotta volontariamente
per gli ultimi due controlli sulle citazioni, non conteggiata come passata.
Suite intermedia 2.427 passata in 217,18 s, prima degli ultimi controlli su
SOURCE del progetto e conflitti delle righe nominative. Suite completa finale
passata: 2.431 test in 219,46 s. Nessuna chiamata LLM o DOCX esportato.

Replay finale B0 38→47 grounded, +9 conformi; INDEX 23→25, +2 conformi.
11 recuperi/10 destinazioni, tutti conformi al gold: 4 esatti nella riga,
3 nominativi, 1 data e 3 collegamenti con ordine+numero condivisi. Otto
binding_source_record e tre verified_person_records; nessun valore o fatto
riscritto, fatti/condizioni identici. Zero nuove accettazioni non conformi e
nessuna grounded persa; anche totale grounded finale senza valori non conformi.
Cinque rifiuti necessari mantenuti: due Comune con indirizzo completo, due
destinazioni B0 con lo stesso Bari (BA) assente nella propria quote, un marker
FORM INDEX insufficiente. La provincia INDEX recuperata cita invece la riga giusta.

Tutti gli undici ancora conditional/REVIEW_REQUIRED e condizioni unknown:
0 RESOLVED/0 scritture. Non è una misura di undici campi esportati. INDEX
originale resta respinto allo schema root, nessun filtro produzione.
11.021/11.023 file protetti invariati, soli due file verificatore diversi;
nuovo file test. Altre trenta funzioni di compilation_global identiche AST.
Frontend invariato/non ritestato. Nessun aggiornamento sessioni live o migrazione.
Arresto dopo replay e rapporto, nessun ulteriore intervento sull'applicabilità.
B0 riferimento, FORM compatto/coverage/thinking ancora sospesi; nessun commit/push.
Bundle verificato: 68 file, 6.634.686 byte non compressi; SHA-256
`efd1a6f0292443c19fae1459cdf8b04a36b69fc9bfc7132643b03a42a68b1087`.

## Diagnosi degli undici SOURCE residui, nessuna implementazione — 17 ottobre

Richiesta corrente: stabilire se i rifiuti residui hanno una causa comune,
distinguendo dati mancanti e collegamenti non ricostruiti, prima di decidere
altre correzioni. [Rapporto](docs/diagnosi-undici-source-2026-10-17.md),
[tracciati e misure](docs/benchmarks/2026-10-17-residual-source-diagnosis.json),
[bundle](docs/benchmarks/2026-10-17-residual-source-diagnosis-audit.tar.gz).

Sola lettura degli ultimi audit: 9 B0-03 + 2 INDEX-01, dieci destinazioni
distinte perché il CF del direttore compare due volte. Non sono gli undici
recuperi KISS. Stesso errore locale di attribuzione nello stesso chunk, ma
quattro sottocasi: 4 valori esatti già nella riga verificata del binding,
3 nominativi con onorifico in un altro record rispetto ai soci, 1 data in
lettere contro formato numerico, 3 associazioni socio/direttore (due CF e
una provincia albo). Nessun valore o ruolo richiesto assente dall'intero input.
Per quattro è già disponibile una prova congiunta esatta; per sette resta
da definire/verificare associazione fra record o equivalenza di rappresentazione.
Non sono undici nuove accettazioni dimostrate o autorizzate.

Cause comuni: fatto condiviso fra ruoli con un'unica serie di citazioni;
_binding_check non riusa il valore nella riga del binding, fallback solo sui
record citati dal fatto, nessun join fra chunk. Elisa è corroborata da nome,
ordine e numero 8421 fra tabella e direttore, anche nello stesso documento
integrativo. Nessuna prova di unicità universale o nuova regola di identità.
I tre nomi non falliscono perché il parser ignora Ing./Arch.: il confronto
sintattico già li ammette nel record; manca l'associazione tra record/ruoli.

Cinque rifiuti esterni invariati: due Comune, due destinazioni B0 con Bari (BA)
non presente nella propria quote di Elisa, un marker FORM INDEX. La provincia
INDEX negli undici ha invece citazione esatta nella riga di Elisa: difetto diverso.
Nessuna modifica a codice, test, prompt, schema, FORM B0, provider/thinking,
validatori, API, writer, fixture o vecchi raw. Nessuna nuova chiamata, replay
dei validatori o esportazione. I 38/23 grounded sono esiti precedenti, nessun
nuovo recupero o misura dei falsi positivi. Suite/Ruff precedenti non rieseguiti.
Controllati JSON, citazioni, celle, conteggi, provenienza, riferimenti e hash.
Raw residual-source-20261017-01/, script diagnostico senza dipendenze.
11.006/11.006 file protetti invariati. Bundle verificato: 17 file,
2.458.181 byte non compressi; SHA-256
`def45875b6d6aa31d524f229cf1657e2ff3bc079e4541c8e0dd2a2c8bee12c37`.

Applicabilità non affrontata: condizioni degli undici unknown, entrambi senza
USER. Prossimo studio separato con sole condizioni FORM e SOURCE/USER dimostrati;
nessuna implementazione autorizzata da questa diagnosi. Conservare le date:
Luca cessa amministratore il 1 ottobre nell'integrazione; Leonardo subentra
il 2 ottobre. La vecchia carica non determina firmatario o ramo attuale,
né invalida il nominativo di Luca come socio. Nessun commit/push, migrazione
o aggiornamento sessioni. B0 riferimento, compattazione/coverage/thinking sospesi.

## Comune e contesto FORM: correzioni e replay — 17 ottobre

Richiesta autorizzata: eliminare l'indirizzo completo accettato nel Comune e
analizzare i 18 contesti FORM, correggendo soltanto una causa comune provata.
[Rapporto](docs/comune-contesto-form-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-field-context.json),
[bundle](docs/benchmarks/2026-10-17-field-context-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-field-context-checks.json).

Mantenuta integralmente la correzione KISS SOURCE. Nuovo controllo nel
validatore condiviso: tipo Comune dalla label fisica o sede/residenza con
componenti separati provincia/via/civico. Non usa la label del modello come
autorità, non estrae la città né riscrive il valore. Indirizzi espliciti,
richieste composite e località come Piazza Armerina restano ammessi.

Diagnosi 18: tutti con prova FORM sufficiente non riconosciuta; zero quote
FORM realmente insufficienti, zero sezioni dimostrate false, zero associazioni
del modello a un ruolo FORM diverso. Applicabilità unknown in tutti. Backend
perde introduzione del ruolo in paragrafo che contiene già campi; elenco di
sette paragrafi, tre schede letteralmente identiche su 2/2/3 paragrafi. Sei
campi all'inizio di membri successivi, dodici in continuazione. Diciannovesimo
caso p46.s0 separato per fatto SOURCE già respinto.
V12 riconosce ora elenco numerato consecutivo, quote di ruolo dopo ultimo
placeholder, almeno due schede identiche, max 12 paragrafi e subject coerente
in ogni membro. Barriere conservate, contesto aggiunto solo al campo verificato.
FORM/catalogo/input non modificati; B0 completo riprodotto esattamente.

Replay rispetto a KISS: B0 grounded 28→38 e conformi 27→38: +11 corretti,
-1 errato. INDEX root isolato 24→23, conformi 23→23: -1 errato. Nessuna proposta
corretta persa, tutti i precedenti recuperi KISS conservati. Zero grounded
non conformi al gold nei due replay finali. Tutti i 18 collegamenti FORM passano,
11 proposte recuperate e sette ancora bloccate dal record SOURCE. Anche p46.s0
ha ora contesto corretto, ma il suo valore resta respinto. Fatti e condizioni
identici, valori nuovi tutti conditional/REVIEW_REQUIRED, 0 RESOLVED/0 scritture.

Residui B0 12: 1 Comune incompatibile, 2 quote insufficienti (un fatto/due
destinazioni), 9 record SOURCE senza il ruolo richiesto. INDEX 4: 1 marker FORM
insufficiente, 1 Comune incompatibile, 2 record SOURCE. Nessun join arbitrario
per recuperare nomi/CF o ruoli in chunk diversi. INDEX originale resta respinto
allo schema root: replay della copia isolata già esistente, nessun filtro produzione.

30 nuovi casi, 211 mirati passati in 9,78 s; 2.374 backend in 206,57 s; Ruff.
Controesempi intermedi: eredità di ruolo su campo aggiunto senza heading e
rifiuto eccessivo di Comune+indirizzo, corretti e log conservati. Primo audit
diagnostico con form_evidence mancante su campo respinto corretto usando FORM
originale; E501 di un test corretto. Zero nuove richieste provider o export;
frontend non ritestato. 10.793/10.795 file protetti invariati, soltanto i due
file produzione autorizzati diversi e nuovo test. Schema, API, writer, modello,
thinking, fixture e vecchi artefatti preservati. Raw field-context-20261017-01/.
Bundle verificato: 47 file, 5.515.935 byte non compressi, SHA-256
`f3d9bdc6f22b0b3837695090ce4ca0a9b8f2347d7011f4cf5517f38071c6fba7`.

Nessun commit/push, migrazione o rianalisi sessioni live. Limiti residui SOURCE
da discutere; nessuna nuova modifica automaticamente avviata. B0 riferimento,
compattazione FORM/coverage/pilot thinking sospesi.

## Correzione KISS dei binding e stop dopo replay — 17 ottobre

Implementazione espressamente autorizzata dall'utente: prova tabellare SOURCE
strutturale e fallback sulle sole citazioni del fatto, senza allentare fatti,
citazioni, soggetti, ruoli o applicabilità. [Rapporto](docs/correzione-binding-kiss-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-binding-kiss.json),
[bundle](docs/benchmarks/2026-10-17-binding-kiss-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-binding-kiss-checks.json).

Modificati solo compilation_global.py e compilation_role_records.py; nuovo
test_compilation_binding_evidence.py. Nuovi percorsi solo V12, nessun framework
o caso Mapi/ID specifico. Tabella Markdown completa con titolo/colonne/riga,
persona esatta e non duplicata; flessione grammaticale nel solo titolo.
Fallback con record del fatto che attesta direttamente persona/ruolo/valore;
nessun join fra chunk e nessuna nuova quote di valore. Prove ed errore originario
conservati nell'audit. FORM, prompt, thinking, schema, API, writer invariati.

Audit prima esattamente riprodotti; replay sugli stessi output senza USER:
- B0-03: grounded 22→28, recuperati 6 conformi (4 soci Luca, 2 direttore Elisa).
- INDEX-01 root già isolato: 19→24, recuperati 5 conformi del direttore.
11 occorrenze/9 destinazioni distinte; nessun recupero non conforme, nessuna
proposta grounded persa. Tutti recuperi restano condizionati REVIEW_REQUIRED,
valori non selezionati, 0 RESOLVED/0 scritture. Fatti e condizioni identici.
INDEX originale continua a fallire i due metadati root, senza filtro produzione.

Residui disgiunti: B0 22 (2 quote insufficienti, 18 contesti FORM, 2 record
SOURCE); INDEX 3 (1 quote destinazione FORM, 2 record SOURCE). Bari (BA) B0
resta respinto in p46.s0 e p53.s2: un fatto/due campi. Il gate FORM esterno
ora emerge su 19 soci, uno già contato per quote errata; 7294 resta bloccato
da questo contesto. Non equivale a prova che i dati o ruoli manchino nella KB.
Quattro record SOURCE residui non attestano il ruolo nel chunk del valore.
Resta anche p41.s1 già accettato con indirizzo completo al posto del Comune,
in entrambe le risposte: 2 occorrenze preesistenti, nessun nuovo errore di questo tipo.
Non dichiarare zero accettazioni indebite nell'intero sistema.

40 nuovi casi, 133 mirati passati in 5,65 s; 2.344 backend passati in 188,62 s,
Ruff passato. Red iniziale corretto per tre difetti fixture; quattro fallimenti
positivi attesi. Primo codice aveva due fallimenti plurale -io, risolti con
regola generica. Log conservati. Primo comando replay senza PYTHONPATH fermato
prima delle analisi, corretto solo l'ambiente. Zero richieste provider/export.
10.752/10.754 file protetti invariati, soli due file produzione autorizzati
diversi; vecchi audit e fixture preservati. Frontend non ritestato.
Raw: backend/data/compilation-audit/binding-kiss-20261017-01/.
Bundle verificato: 40 file, 5.292.563 byte non compressi, SHA-256
`79ea9798c5fa744732e81203226a3f2ae290325cba633028745d20f6ddacd3cb`.

**Fermato dopo replay e rapporto**, nessun commit o push. Nessuna migrazione
o aggiornamento sessioni live. Contesto FORM e attribuzioni residue sono limiti
da discutere, non correzioni automaticamente autorizzate. B0 riferimento;
compattazione, coverage e pilot thinking restano sospesi.

## Chiarimento persona–ruolo e rifiuti — 17 ottobre

Ricostruite le cinque domande dell'utente su proposte, SOURCE, costruzione
del binding e natura del rifiuto. [Analisi con esempi e codice](docs/analisi-binding-persona-ruolo-2026-10-17.md),
[estratti e hash](docs/benchmarks/2026-10-17-binding-persona-ruolo.json).
Sola lettura degli artefatti già acquisiti: zero richieste provider, nessun
nuovo replay, export o modifica a codice/prompt/schema/validatori/writer.

Il modello propone fact_id/binding_id e rispettivi record; SubjectBinding non
contiene subject, recuperato dal fatto durante la verifica backend. I tre
binding dei soci falliscono sul ruolo letterale in ogni quote: Soci != socio,
e la riga non contiene il ruolo. Il primo errore interrompe il ciclo già sul
titolo. 24 valori conformi, 23 fatti grounded; campi 23 REVIEW_REQUIRED/1 REJECTED.
Non è assenza dei soci nella SOURCE, ma limite del formato proposto e verificato.
INDEX-01 p53.s0: ruolo -45 e valore -55, binding e fatto separatamente grounded;
nessuna attribuzione valida registrata per il chunk del valore. Persona, ruolo
e ordine sono espliciti nella frase -55, e l'ordine è disponibile anche in -45:
catena di citazioni incompleta, non dato mancante. Esito osservato nel replay
precedente, non nella chiamata originale fermata allo schema root.
p46.s0 B0-03: Bari (BA) manca nella quote scelta per Elisa; il controllo corretto
è source_span(quote, value). La stessa stringa nel troncone di Andrea in -55
non è prova per Elisa. Non indebolire la citazione per recuperare questo caso.
Applicabilità del ramo senza USER resta un vincolo indipendente.

Verificati solo estratti/conteggi, SOURCE identiche e hash dei dodici file
consultati; nessuna suite rieseguita. Nessun guadagno controfattuale attribuito
a fix non eseguiti. B0 resta riferimento, FORM/coverage sospesi, nessun commit.
Prossimo passo da discutere: rappresentazione verificabile delle relazioni,
senza trasformare questi rifiuti diversi in un'accettazione generalizzata.

## Replay INDEX-01, contesto USER e reasoning — 17 ottobre

Richiesta dell'utente: affrontare i fallimenti prima di cambiare coverage;
replay dei soli metadati root, trasporto USER registrati, opzioni thinking e
soci B0-03. **Coverage invariato, B0 riferimento, compattazione FORM ferma.
Zero nuove generazioni**, un solo GET /models non generativo. Nessun commit.
Il trasporto USER è autorizzato da questa richiesta specifica; i precedenti
punti di ripresa qui sotto sono storici.
[Rapporto](docs/replay-index01-user-reasoning-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-root-user-reasoning.json),
[bundle](docs/benchmarks/2026-10-17-root-user-reasoning-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-root-user-reasoning-checks.json).

INDEX-01: originale preservato, riprodotti due extra_forbidden. Isolati solo
proposal_stage/project_id; tutti gli altri record esattamente uguali. Schema
pieno passa, 27 proposte/20 fatti; 19 grounded ma solo 18 conformi al gold.
Restano p15.s0 rifiutato FORM e sette dati del direttore bloccati dal binding.
p41.s1 contiene indirizzo intero al posto del comune e passa i gate letterali.
Nessun filtro root aggiunto in produzione, nessun successo storico riscritto.

Due scenari software con analisi originaria sempre senza USER:
- Nessuna conferma di partecipazione: export dei 19 respinto 409; copia vuota
  soltanto con export parziale/allow_empty esplicito.
- Test distinto con due risposte USER archiviate e apply_replies: selezione
  manuale dei 19, DOCX con 19 SOURCE e 18 conformi, zero valori USER nei campi.
  Mapping condizioni dichiarato nella fixture, mai trasferimento fra sessioni
  in produzione. Narratore e interprete LLM non valutati.
Copie Word/PDF INDEX01-ROOT-REPLAY-SENZA/CON-CONFERME in nuovi dati. Controllate
534 destinazioni e 220 celle, altre 15 parti ZIP preservate; dieci pagine
LibreOffice ciascuno, visione 1/3/10 con conferme. Firma su pagina quasi vuota.

Trasporto USER implementato in compilation_user_context.py: legge solo turni
start salvati con session_id esatto e conversazione/progetto della sessione.
recorded_request è citazione letterale, non scelta estratta; registered_decision
è risposta già accettata, con provenienza e ambito coerenti nel proprio registro.
Nessuna risposta AI, cronologia generica o inferenza di firmatario/partecipazione.
_prepare aggiunge user_context separato, user_values resta [], fatti solo SOURCE.
Istruzioni aggiuntive soltanto con USER. Senza ricevute, input e request B0
riprodotti esattamente sul Minervino. Caso T0 registrato salvato NOT-SENT;
qualità generativa con USER non misurata. Nessuna migrazione/rianalisi implicita.

Thinking: GET ufficiale HTTP200, deepseek-flash oggi DeepSeek-V4.1-Flash,
low/high/max, default high; contesto 1.048.576, output massimo dichiarato
393.216. B0 già enabled/low, minimal è alias low; nessun livello attivo più
basso o budget indipendente di soli token reasoning documentato. API permette
disabled/none. Runtime globale forza ancora thinking DeepSeek, invariato.
Pilot minimo solo proposto: due chiamate fresche A enabled/low e B disabled
con effort omesso; stesso B0 senza USER, messaggi/schema/coverage, max_tokens
49.152, timeout 300 s. Body pronti NON inviati. Cache/backend/campionamento
e due soli campioni limitano le conclusioni; USER resta un confronto distinto.

Soci B0-03: 24 valori conformi, 23 fatti localmente grounded, una citazione
insufficiente p46.s0 (Bari (BA) da -55 senza valore completo). Tre binding
respinti: ogni quote deve contenere il ruolo letterale; titolo Soci vs socio
e righe prive del ruolo. Tutti i 24 bloccati; nove valori con prove in chunk
esterni al binding, 15 negli stessi chunk grezzi. Questi 15 non sono scritture
già consentite e correggere il plurale non risolve tutto. Nessun gate allentato.

Verifiche: **79 mirati passati in 9,33 s; 2.304 backend in 168,46 s; Ruff passato.**
Iniziali otto diagnostiche import fixture risolte con alias, log conservato.
Acquisizione offline con AISettings senza api_key corretta con oggetto minimo;
sessione abbandonata solo nel DB privato, nessuna generazione ripetuta.
Frontend invariato/non ritestato. Funzioni gate AST identiche; schema, coverage,
role-record, validatori e writer invariati. Cambiano solo due file esistenti
per input/request e _prepare, più lettore USER e test nuovi. Vecchi audit/fixture
invariati; entità live 49 conversazioni/28 sessioni/464 revisioni/16 compilazioni
e cinque file SOURCE uguali al riferimento. Nessuna immutabilità binaria DB
asserita. Runtime privato escluso dal bundle, richiesto dallo script exporter.
Raw: backend/data/compilation-audit/root-user-reasoning-20261017-01/.

Archivio: 149 file, 3.516.747 byte; SHA-256
`24799ce17ac5baa66c63367ddda807e97cf72f0a13eaab90f71b7770021c987f`.

**Ripresa:** discutere eventualmente il pilot thinking, senza eseguirlo
implicitamente. Coverage resta sospeso. Qualità USER non misurata; binding,
soci e selezione del firmatario non risolti dal solo trasporto dei messaggi.

## Stop compattazione FORM; diagnosi offline del contratto — 17 ottobre

**Decisione esplicita dell'utente:** fermare gli esperimenti di compattazione
FORM. B0 resta il riferimento; E1 compact-v1 e compact-index-v2 non vanno
integrate. Nessuna nuova chiamata LLM, modifica di codice/prompt/validatori/
writer o commit autorizzati per questa attività. E2 non avviato. Le precedenti
proposte di ripresa nelle sezioni storiche qui sotto sono superate da questo stop.

[Diagnosi dettagliata](docs/diagnosi-contratto-risposta-b0-e1-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-output-diagnosis.json),
[bundle derivati](docs/benchmarks/2026-10-17-output-diagnosis-audit.tar.gz),
[controlli](docs/benchmarks/2026-10-17-output-diagnosis-checks.json).

Analizzati gli HTTP/request/input/risposte/metriche e audit esistenti delle
nove analisi globali, senza rieseguirle o rivalidare risposte riparate.
INDEX-01: HTTP200 stop e JSON completo, ma envelope rifiutato per due chiavi
extra proposal_stage/project_id; nessun audit di campo o writer raggiunto.
25 valori grezzi conformi persi al gate globale, non 25 rifiuti locali.
INDEX-02: HTTP200 length a 49.152 token, di cui 44.316 reasoning e 4.836 non
reasoning; JSON tronco dentro facts, prima di coverage; errore sollevato nel
trasporto. Nessun timeout in entrambi; nessuna prova di un problema del writer.

Output nove chiamate: 349.460 token, 273.801 reasoning (78,35%), 75.659 non
reasoning per differenza. Non comprende successivi router/narratore; reasoning
non consumato come proposta dal backend. Otto JSON completi già minificati:
634 record, zero duplicati esatti, 162 fatti tutti referenziati e nessuna
coppia con identici subject/entity/aspect/property/value. Un ID coverage
ripetuto (p64.cb0 B0-02). 210 record coverage / 1.907 occorrenze ID: spiegazioni
ausiliarie, non duplicati inutili; 75.296/220.034 caratteri (34,22%).
Nessuna tokenizzazione per sezione o causalità della sola lunghezza dichiarata.

Verifica delle prove congelate contro i messaggi USER effettivamente inviati:
60 target SOURCE ×9 =540 controlli positivi. Identici 56 chunk, 63.655 caratteri
SOURCE, cinque file; nessuna evidenza esclusa prima dell'LLM per questi target.
Righe soci assenti dal solo indice source_property_lines, presenti complete
nel chunk -54. user_values=[] anche se T0 della chat sceglie firmatario e
partecipante: dati SOURCE presenti non dimostrano assegnazione USER della pratica.
Omissioni distinte da rifiuti; le motivazioni MODEL di assenza non sono prove.

Sette audit reali: 49 occorrenze corrette bloccate, 32 destinazioni distinte.
B0 1/5/28, E1 5/6/2, INDEX-03 due. Cause primarie disgiunte: 8 FORM, 23
binding ruolo, 16 collegamenti ruolo/valore in chunk/record differenti, 2 quote
SOURCE senza valore completo. B0-03 propone tutti i 24 campi soci ma li blocca;
uno ha anche errore SOURCE, quindi non contarlo due volte. Corretto rispetto al
gold non equivale a citazione/provenienza/ruolo validi, né a errore del validatore.

**Minima proposta documentata, non implementata:** stessa vista B0 e una sola
chiamata globale, rendere coverage sparsa invece di esaustiva. Conservare
chiave coverage=[] e tutto il contratto fattuale/condizioni/binding invariato.
Posizioni residue UNEXPLAINED/da valutare, mai SOURCE assente o risolte;
trade-off esplicito sulla spiegazione delle omissioni. Lista vuota già ammessa
dallo schema, richiesta di esaustività nel compito attuale. Controfattuale solo
in caratteri B0: -35,67%/-31,01%/-24,71% JSON visibile; nessun risparmio token,
reasoning o miglioramento qualità misurati. Non risolve da sola citazioni,
binding, USER iniziali o troncamento prima di coverage. Nessun parametro cambiato.

Raw nuovi: backend/data/compilation-audit/diagnosi-output-b0-e1-20261017-01/.
Conservati tabelle token/sezioni, ogni omissione/prova, 49 rifiuti dettagliati,
rifiuto globale separato, metodi e hash. Un primo controllo offline fallito
per newline aggiunto in response.txt corretto solo nel confronto; originali
invariati. Verificati hash di 1.227 file protetti, artefatti originali compresi;
JSON/CSV/link/diff e archivio controllati. Nessuna suite applicativa ripetuta,
nessun nuovo provider, codice, fixture o dato live modificato. Nessun commit.

Archivio dei derivati: 18 file, 99.771 byte, SHA-256
`080bb3190e05e1c7b68a36e40a5a37056683af42b99074dfd1b06c6f1380ec65`.

**Ripresa:** discutere la sola proposta sul contratto di uscita nel rapporto.
Non avviare altre prove o modifiche automaticamente; B0 e stop FORM persistono.

## E1 compact-index-v2 concluso: due fallimenti, un Word — 17 ottobre

L'utente ha approvato la seconda variante con indice diretto dei campi.
Implementati indexed_form/indexed_input e controllo strutturale indipendente;
--form-view compact-index-v2 soltanto nel runner. Type/context_id espliciti,
contesti condivisi, blocchi invariati. compact-v1/default full conservati;
nessuna integrazione nel motore operativo, migrazione, commit o push.
[Rapporto completo](docs/esperimento-e1-index-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-e1-index.json),
[bundle](docs/benchmarks/2026-10-17-e1-index-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-17-e1-index-checks.json).

Input canonico B0 identico prima di ogni chiamata: FORM 126.928→88.522
caratteri (-30,26%), messaggi 264.951→227.803, istruzioni di lettura +1.258.
267 destinazioni, 142 contesti; SOURCE/USER/schema/reading plan/parametri uguali.
Input e istruzioni v1 riprodotti esattamente dai precedenti artefatti.
Protocollo/hash congelati prima dei risultati; tre analisi sequenziali,
DeepSeek flash/thinking, timeout 300 s e output massimo 49.152, zero retry.

- Run 01: JSON completo rifiutato per proprietà extra proposal_stage/project_id;
  173,44 s, 39.871 output di cui 32.272 reasoning. Grezzo 25 conformi su 27,
  indirizzo intero nei due campi del comune; nessun audit/sessione/Word.
- Run 02: HTTP 200 finish_reason=length, JSON tronco; 214,62 s, 49.152 output
  di cui 44.316 reasoning. Nessuna riparazione, audit/sessione/Word o score campo.
- Run 03: 23 proposte conformi, 21 grounded; due rifiuti FORM p15.s0/p15.s1.
  159,94 s, 36.508 output di cui 29.806 reasoning. Unica continuazione isolata
  fino al Word: 21/60 conformi, tutti SOURCE, nessun campo USER scritto.

Input 65.770 token ogni chiamata (-13,31% B0; +3,31% v1). Media output
41.843,67 (+4,42% B0), totale analisi 107.613,67 (-7,18%), tempo 182,67 s
contro 170,14 B0. Cache prima 6.400 hit/59.370 miss, poi 65.536/234;
serie storiche del giorno precedente, backend provider non fissato. Nessuna
causalità dei tempi, equivalenza statistica, costo monetario o media di qualità
sui soli successi dichiarati. N/D espliciti per i due fallimenti, non zeri imputati.

Run 03: 8/19 dati iniziali, 9/9 societari, 0/24 soci, 4/8 direttore conservati.
Due condizioni di partecipazione chieste e risposta limitata a ripetere T0;
nessuno dei quattro argomenti USER del copione chiesto. Zero quattro testi
USER, sei preferenze e tre native true attese; preservati 123 vuoti, 61
preferenze false e dieci native false. Export parziale esplicito, GENERATED,
ready_for_submission=false; nessuna promozione automatica a RESOLVED.
Nove chiamate totali, 353.942 token: minor totale dovuto anche ai fallimenti
precoci, non miglior costo per pratica. Servizi isolati con risposta reale
riusata dopo uguaglianza input/proiezione/audit, non browser/endpoint/ingestion.

**Verifiche eseguite:** 137 test mirati passati in 7,61 s; **2.279 backend
passati in 170,27 s**; Ruff completo passato. Iniziale E501 corretto prima
del freeze e conservato; nessun fallimento pytest. Software simulato distinto
da qualità reale. Frontend invariato, suite non ripetute. Tutte le 267
destinazioni Word/report e 110 celle incluse intestazioni controllate;
insiemi ZIP uguali, altre 15 parti preservate. LibreOffice dieci pagine,
viste 1/3/10: firma su ultima pagina quasi vuota, Microsoft Word non verificato.
18 hash Minervino e 11 Labirinto, cinque SOURCE live identiche; preesistenti
49 conversazioni/28 sessioni/464 revisioni/16 compilazioni uguali alla copia
isolata esclusi i nuovi oggetti del run 03. Nessuna immutabilità binaria DB
asserita. Fixture/fonti/gold/schema/validatori/writer invariati.

Raw: backend/data/compilation-audit/e1-index-20261017-01/.
Word/PDF: nuovi dati/domanda-iscrizione.E1INDEX-RUN-03.*; nessun output 01/02.
Bundle senza DB/credenziali: 250 file, 3.250.464 byte, SHA-256
e0f586cf03775c9a699be31b7d75d704af5b61609411fbbdb13d74284dda33fc.
Tutti gli output/errori/test e comparison.csv conservati. Modifiche e
cancellazioni preesistenti preservate; niente ripristini o pubblicazioni Git.

**Decisione:** indice diretto misurato, non adottato: 1/3 analisi utilizzabili
contro 3/3 B0/v1. Risparmio input confermato, affidabilità non migliorata.
Non conclude che l'indice causi da solo gli errori o che ogni formato compatto
sia inefficace. E2 non avviato. **Ripresa proposta, da discutere:** esperimento
separato su contratto di uscita e budget reasoning, una variabile per serie,
prima di altra riduzione; nessuna implementazione già autorizzata di questa
nuova ipotesi. Collegamento USER iniziali, binding, soci e domande restano
interventi distinti. Il precedente punto di ripresa v1 qui sotto è storico.

## E1 compact-v1 completato: meno token, qualità non stabilizzata — 16 ottobre

L'utente ha approvato E1 e tutte le prove sperimentali. Implementata la proiezione
compact-v1 in backend/app/compilation_form_view.py, selezionabile solo nel runner
con --form-view compact-v1. Default full e motore di chat invariati. Runner con
--prepare-only e --reference-input per impedire chiamate su corpus diverso da B0.
[Rapporto E1](docs/esperimento-e1-form-compatto-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-e1-form.json),
[bundle](docs/benchmarks/2026-10-16-e1-form-audit.tar.gz).

Preflight E1: FORM 126.928 → 81.209 caratteri (-36,02%); messaggi
264.951 → 220.519 (-16,77%), incluso adattamento prompt +1.287 caratteri.
267 destinazioni in 142 contesti, testi/tabelle e proprietà logiche equivalenti;
SOURCE, USER, schema e reading plan identici a B0. Tre chiamate effettive:
63.661 token input ciascuna contro 75.864 (-16,09%). Output medio 34.569 contro
40.074; totale analisi medio 98.230 contro 115.938 (-15,27%). Tempi analisi
150,96/102,40/166,16 s; media 139,84 contro 170,14, con cache non uniforme:
prima E1 6.400 hit, poi 63.488; B0 tutto caldo. Nessun risparmio monetario provato.

Valori conformi nelle proposte 18/25/23, con grounding 13/19/21 contro B0
21/17/21. Word E1 14/11/23 conformi sui 60 target documentati, B0 23/17/22.
Provenienza distinta: 13 SOURCE+1 USER, 11 SOURCE, 21 SOURCE+2 USER conformi.
Nuova omissione dei nove campi societari nel primo; tutti i 24 soci omessi
in tutte le analisi E1. Comune Bari corretto nel terzo, indirizzo intero nel
secondo. Rifiuti FORM/ruolo e gruppi checkbox restano. Nessuno dei quattro
argomenti USER chiesto: zero quattro testi USER, sei preferenze e tre native
true; preservati i 123 vuoti, 61 preferenze false e dieci native false.

Tre continuazioni isolate completate e tre export espliciti, tutti parziali.
Run 2 fermato dopo due risposte ammesse sulla richiesta di riconfermare dati
SOURCE fuori dal copione; nessuna attestazione inventata per sbloccarlo.
27 chiamate totali, 413.624 token, incluso dialogo: percorsi diversi da B0,
non costo/tempo end-to-end comparabile direttamente. Analisi vere riusate dopo
input canonico, proiezione e audit uguali: non browser/endpoint/ingestion.

Test: 116 mirati passati in 5,84 s; **2.258 backend passati in 166,87 s**,
Ruff completo passato. Prima serie 110 passati/quattro falliti per aspettativa
errata dei nuovi test su slot inline accanto a checkbox native: il parser già
li omette. Corretti i soli test, parser e gold invariati; log conservati.
Verificate tutte le 267 destinazioni contro Word/report, altre 15 parti ZIP
preservate, 18 hash Minervino e 11 Labirinto, cinque SOURCE live identiche.
Rendering LibreOffice dieci pagine, visione campionata 1/3/10 per ogni run,
firma su pagina quasi vuota. Nessuna certificazione Microsoft Word.
Controlli finali: tutti i 330 contenuti di cella dei tre Word, incluse le
intestazioni, conformi; copie Word/PDF identiche ai raw, manifest raw/bundle
e diff verificati. [Esiti](docs/benchmarks/2026-10-16-e1-form-checks.json).
Entità live preesistenti uguali (49 conversazioni, 28 sessioni, 464 revisioni,
16 compilazioni); nessuna pretesa di DB interamente immutato.

Raw e protocollo: backend/data/compilation-audit/e1-form-20261016-01/.
Bundle senza DB/credenziali: 386 file, 6.711.650 byte, SHA-256
9cafd05bb2db9d4180aa37d9d47cfb79ad88b9b8bb7bd4a26bdf2215af6516d5.
Word/PDF in nuovi dati/domanda-iscrizione.E1-RUN-01/02/03.*.
Nessun retry, risultato escluso, modifica a fixture/validatori/writer, migrazione,
commit o push. Frontend non modificato, suite non ripetute.

**Decisione: compact-v1 resta nel banco di prova. Risparmio input misurato,
qualità non sufficiente per promuoverlo; nessuna equivalenza da tre campioni.
Ripresa proposta: nuova variante E1 con indice diretto candidate_id e contesti
condivisi, protocollo/versione nuovi. Non implementata. E2 non avviato;
scelte USER, binding e narratore restano interventi separati.**

## E1: primo intervento proposto, ancora senza implementazione — 16 ottobre

L'utente chiede da dove iniziare E1 e cosa fare. Ispezionato il catalogo e
l'input reale B0; registrato il [contratto proposto](docs/contratto-e1-form-compatto.md).
FORM 126.928 caratteri: blocks 63.758, candidates 62.947. Metadati per campo
ridondanti: location, slot_context, ancore; 267 section_ids vuoti. Misura offline
in caratteri, nessun nuovo risparmio token o esito LLM misurato.

Proposta: proiezione deterministica dal catalogo completo, ID invariati,
metadati condivisi per contesto, coordinate writer nel backend. Prima versione
conserva testo originale e viste marcate dove servono alle citazioni. Mantenere
tabelle/intestazioni, tipi/protezioni, controlli e relazioni; i 267 ID da soli
non garantiscono fedeltà. Prima contratto e confronto offline, poi serializzatore
nel solo banco di prova e tre run completi comparabili con B0. Schema output,
fonti, thinking, validatori e copione invariati; adattamenti del prompt dichiarati.

Scelte USER iniziali, binding SOURCE, pool domande, layout e riduzione dello
schema output restano interventi distinti da discutere. E2 successivo a E1
fissato. Nessun codice applicativo, nuova chiamata provider, fixture o DB
modificati. Nessuna decisione aperta promossa a implementazione; controlli
documentali soltanto, nessuna suite applicativa necessaria.

**Ripresa: discutere il contratto minimo E1; primo risultato implementativo
proposto input compatto completo con verifica strutturale, nel banco di prova.**

## B0 misurata con provider reale: tre Word acquisiti — 16 ottobre

L'utente ha autorizzato il provider per compilare e misurare il sistema prima
dei lavori architetturali. Eseguite tre analisi DeepSeek reali e tre continuazioni
dei servizi applicativi su copie isolate, fino all'export esplicito di bozze
parziali. Codice attuale 99ab052 invariato, Minervino V1/fonti/gold congelati.
[Rapporto](docs/baseline-minervino-b0-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-b0.json),
[bundle](docs/benchmarks/2026-10-16-minervino-b0-audit.tar.gz).
Raw b0-minervino-20261016T154354Z/; archivio 348 file, 6.423.265 byte,
SHA-256 85d2d441e0edb297a4d4955929eca8c8ca3c61545fef1be6de5f9575c69009ee.
Tre Word e PDF in nuovi dati/domanda-iscrizione.B0-RUN-01/02/03.*.

Analisi: 23/23/50 valori proposti, 22/22/49 conformi al gold e 21/17/21
conformi con grounding passato sui 60 target SOURCE. Word: 24/18/23 scritture
totali, 23/17/22 valori conformi sui 60 target; provenienza effettiva distinta
(21+2 USER / 15+2 USER / 21+1 USER). Non è una misura unica su 267.
Nessuno dei quattro argomenti USER del copione chiesto; zero dei quattro testi,
delle sei preferenze e delle tre checkbox attese true. Conservati i 123 vuoti,
61 preferenze non selezionate e dieci controlli false, senza dedurne comprensione.

Cause osservate: soci omessi nei primi due run, tutti proposti nel terzo ma
bloccati dal binding letterale; altri dati del direttore respinti per attribuzione
nello stesso chunk; scelte iniziali assenti dall'input analisi (user_values=[])
e richieste di nuovo; pool domande incompleto; indirizzo completo nel campo comune;
gruppo checkbox respinto o assente. Run 2 fermato sulla riconferma del direttore,
fuori dal copione USER: export parziale esplicito, nessun fatto aggiunto per sbloccare.

30 chiamate, 481.199 token totali (357.871 input, 123.328 output, incluso
89.725 reasoning). Ogni analisi 75.864 input, cache 75.648 hit/216 miss;
146,73/179,84/183,85 s. Nessun costo monetario acquisito. Continuazioni da risposte
reali riusate dopo input identico e audit rivalidato: non misurati browser,
endpoint HTTP o ingestion; somma tempi provider non è latenza UI.

Verifiche: tutte le destinazioni contro Word/report, altre 15 parti ZIP
preservate, manifest/hash e segreti nel bundle, rendering LibreOffice e controllo
visuale campionato. Dieci pagine per bozza, firma su pagina quasi vuota; Word
Microsoft non verificato. Confronti dominio conservano sessioni/compilazioni
preesistenti; chunk derivati live fuori dalle SOURCE rigenerati con stessi contenuti,
quindi nessuna affermazione di DB interamente immutato. Errori offline del
fingerprint/aggregazione corretti e registrati, senza ripetere chiamate provider.
Nessuna suite applicativa, modifica al motore, migrazione, reindicizzazione
richiesta, commit o push. Modifiche/cancellazioni preesistenti conservate.

**Ripresa: B0 acquisita. Prima di scrivere il nuovo motore, fissare il contratto
minimo E1 della proiezione deterministica del FORM completo e i criteri;
poi tre run comparabili mantenendo fonti, modello/thinking, schema e validatori.
E1/E2 non implementati né misurati. Passaggio delle scelte USER, pool domande
e binding SOURCE sono problemi distinti da valutare separatamente.**

## B0: acquisito input attuale, qualità ancora da misurare — 16 ottobre

L'utente chiede se occorra misurare il sistema prima di E1/E2.
Eseguito un preflight offline del codice attuale, senza chiamate provider:
[report](docs/b0-preflight-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-b0-preflight.json),
[backup](docs/benchmarks/2026-10-16-b0-preflight-audit.tar.gz).
Raw b0-preflight-20261016-01/. È una misura di input, non una baseline di qualità.

Originale e cinque file SOURCE backend corrispondono alla fixture congelata;
56 chunk, 267 destinazioni. JSON già senza indentazione: 240.276 caratteri,
di cui FORM 126.928; system prompt 24.675, totale messaggi 264.951. Token
consumati, tempi provider, accuratezza, dialogo e Word non misurati qui.

Punto emerso: progetto deepseek-flash con preferenza thinking falsa, ma
resolve_global forza thinking per DeepSeek. B0 deve conservare il comportamento
effettivo con thinking attivo, non la sola impostazione UI. Prima ricostruzione
erroneamente senza thinking conservata separatamente, poi corretta; nessuna
richiesta inviata. Primo avvio senza PYTHONPATH fallito, avvio corretto riuscito.
La disattivazione del thinking sarebbe un altro esperimento.

Runner globale disponibile per proposta/audit, con scoring Minervino da raccordare
senza cambiare il gold; non copre dialogo/export. Il runner di latenza copre
solo creazione/risoluzione automatica, senza USER o Word. Misure delle fasi
da distinguere; nessun nuovo motore necessario per la misura della proposta.

Verificati hash, link e diff; fixture/fonti/gold invariati. Nessuna suite
applicativa, scrittura DB/KB, sessione, commit o push in questo aggiornamento.
Conservate modifiche e cancellazioni preesistenti dell'utente.

**Ripresa: acquisire tre run B0 della proposta completa con configurazione
effettiva congelata e confronto indipendente Minervino; poi E1. Per misurare
il sistema fino al Word serve anche il percorso integrato con copione USER.
Il preflight non autorizza conclusioni sulla qualità o sul risparmio di token.**

## Discussione E1/E2 e continuità per la tesi — 16 ottobre

L'utente chiede di continuare ad aggiornare STATUS.md per la tesi e propone
due esperimenti distinti: E1 FORM compatto sul Minervino completo, E2 stessa
vista compatta limitata a gruppi di requisiti per accelerare lo sviluppo.
Registrato il [piano proposto](docs/piano-esperimenti-e1-e2.md), con riferimenti
nel benchmark e nella proposta architetturale. È una discussione del disegno,
non un'implementazione o una nuova prova di qualità.

Confronti: B0 attuale completo contro E1 compatto completo; E2 contro E1
completo sulle stesse destinazioni e checkpoint, entrambi contro il gold.
Il tag 99ab052/baseline-minervino-v1-20261016 è una base recuperabile già
pubblicata e verificata nel turno precedente, non una baseline LLM misurata.
E2 valuta efficienza e differenze locali, senza dimostrare qualità globale.

Orientamento proposto: prima E1, poi versione compatta fissata e gruppi E2
distribuiti fra anagrafica, soci/direttore, rami, preferenze e dichiarazioni.
Conservare dipendenze FORM, condizioni e informazioni USER; niente gold o
indizi dalle risposte nel prompt. SOURCE e chunk inizialmente uguali fra le
varianti. Misurare costo per gruppo e totale della suite, inclusa cache e
contesto ripetuto. Scelta degli estratti da congelare prima dei risultati.
Gli estratti sono prove di sviluppo; non reintroducono compilazione a gruppi
nel prodotto. Margini di qualità locale e criteri vanno fissati prima dei run;
nessun nuovo errore critico come orientamento, nessuna equivalenza promessa.

Aggiornati soltanto documenti; controllati diff, riferimenti, tabelle e hash
dei manifest Minervino/Labirinto. Nessuna suite applicativa, chiamata provider,
scrittura DB/KB, modifica a fixture/gold o nuova baseline. Nessun commit/push
in questo aggiornamento; modifiche preesistenti dell'utente conservate.

**Ripresa: fissare il contratto minimo della vista compatta e il perimetro
della prima misura E1, configurare ambiente/provider e acquisire B0. Dopo E1
definire e congelare il manifest dei gruppi E2 fuori dalla fixture V1. La
riduzione delle fonti e l'invio file ai provider restano confronti separati.**

## Minervino V1 congelato come base della nuova architettura — 16 ottobre

L'utente ha autorizzato correzioni finali, adozione del caso, tag e push su
GitHub. Questa richiesta supera l'attesa dell'OK sul candidato. Creati
[Word finale](<nuovi dati/domanda-iscrizione.GOLD-V1.docx>) e
[PDF LibreOffice](<nuovi dati/domanda-iscrizione.GOLD-V1.pdf>) nella stessa
cartella, con [fixture canonica Minervino V1](demo-documents/benchmark-minervino/v1/README.md).
Riferimento Git: tag annotato **baseline-minervino-v1-20261016**, ramo
**prune-backend**, pubblicazione autorizzata su origin/GitHub.

Gold ricostruito dal pacchetto originale con valori/scelte autoriali revisionati:
note rimosse dalle righe compilabili, placeholder delle continuazioni ripristinati,
blocco firma con keepNext/keepLines. Numerazione originale conservata e confermata
visivamente. Originale, candidato utente e revisione 1 invariati. Cambia solo
word/document.xml, altre 15 parti ZIP identiche all'originale. SHA-256 gold:
94e77ce5d04585c4d62d858bec1ec2d6c0af2e4aa5c062e7af6cb32a474c4db3.

Congelati cinque documenti di fonte (tre Company attuali, General distrattore,
avviso), richiesta iniziale, scenario, quattro argomenti USER e checkpoint
T0/T1/T2, policy identificativi demo e perimetro di firma/allegati/abilitazioni.
Gold JSON e inventario coprono 267 destinazioni: 187 testi, 67 preferenze e
13 controlli nativi. Attesi 60 testi SOURCE, quattro USER, 123 vuoti, sei X e
tre controlli true. Gold/copione esclusi dagli input LLM con allowlist esplicita.
Questi sono denominatori autoriali, non risultati di qualità del modello.

Verifica indipendente passata per tutte le destinazioni, quote, stati/simboli,
ZIP/XML, caricamento python-docx e 18 hash del manifest. MuPDF separa ancora
la linea della firma; acquisizione conservata. Preparato LibreOffice 26.2.6.3
locale sotto .tools, senza installare pacchetti di sistema: gold di nove pagine,
tutte ispezionate, firma e linea insieme a pagina 9. Errori iniziali del tool
ricollocato e Python di sistema senza docx conservati; controllo finale con
ambiente backend riuscito. Warning liblangtag nei log, nessuna certificazione
di paginazione Microsoft Word. Labirinto V1 preservato e hash verificati.

[Rapporto](docs/minervino-base-v1-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-freeze.json),
[backup](docs/benchmarks/2026-10-16-minervino-freeze-audit.tar.gz).
Raw minervino-freeze-20261016T144815Z/. Aggiornati benchmark, proposta e registro.
Nessuna modifica a motore/frontend o DB/KB live, migrazione/reindicizzazione,
nuova chiamata provider o suite applicativa completa. Le cancellazioni locali
preesistenti dell'utente restano fuori da questo commit; sidecar Zone.Identifier
e tool locali non vengono pubblicati.

**Ripresa: configurare istanza isolata e provider della baseline integrata,
tre run a materiali fissi; poi confrontare le proposte architetturali. Il
pacchetto è congelato, l'architettura concettuale resta da validare. Nessuna
implementazione del nuovo motore avviata. Il runner Labirinto non è compatibile
automaticamente con lo schema Minervino: non adattare il gold al suo parser.**

## Verificato il verdetto sulla revisione 1 — 16 ottobre

Su richiesta dell'utente verificati i quattro rilievi nel
[report](docs/minervino-verifica-verdetto-2026-10-16.md). Numerazione alfabetica
dei quattro titoli conservata nell'XML come nell'originale; non risulta da
ripristinare. Firma isolata a pagina 10 non confermata: MuPDF/mutool 1.27.0
reimpagina il gold in 15 pagine e mantiene dicitura e linea insieme nell'ultima,
anche visivamente. Non è una verifica della paginazione Microsoft Word.
Assegnazioni già nella scheda scenario; rimane da definire quando fornirle come
input USER. Confermate due spiegazioni autoriali nelle aree compilabili,
opportuno spostarle nello scenario.

[Controlli](docs/benchmarks/2026-10-16-minervino-verdetto.json),
[immagine MuPDF](docs/benchmarks/2026-10-16-minervino-verdetto-last-page-mupdf.png),
[backup](docs/benchmarks/2026-10-16-minervino-verdetto-audit.tar.gz).
Raw minervino-verdetto-20261016T143707Z/. Hash input, manifest, link e diff
verificati; nessuna suite applicativa o nuova chiamata provider. Word e scenario
invariati, nessuna modifica a codice/DB/KB/fixture, commit o push.

**Prossimo: eventuale revisione delle note e verifica della firma in Word;
attendere l'OK sul candidato prima di congelarlo. Per il benchmark completo
restano anche checkpoint, aspettative strutturate e policy dello scenario.**

## Word gold revisione 1 pronto per l'utente — 16 ottobre

L'utente ha chiesto di correggere il gold e lasciare il Word nella stessa
cartella; congelamento solo dopo il suo OK. Creato
[domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx](<nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>),
SHA-256 5bd34a43b22dff44d5a280b690f4187d345e6664619d42272bbe2c590b5c8d67.
File originale dell'utente e modulo vuoto conservati invariati.

Ripristinati dall'originale i tre paragrafi del direttore con gli otto dati di
Elisa, e le etichette originali nei paragrafi 42–49 della società/soci, inserendo
spazi alle giunzioni senza cambiare i valori. Scelte e note dell'utente conservate.
Creata [scheda scenario](<nuovi dati/SCENARIO_GOLD_MINERVINO.md>) dalle decisioni
del suo gold, separata dalla KB; checkpoint e policy restano da completare.

Generazione con modifica XML autonoma del documento, senza usare il writer
applicativo o LLM. Gli intervalli fisici acquisiti in precedenza sono stati
controllati contro i placeholder originali. Verificate tutte le 52 occorrenze
precedenti e gli otto campi ripristinati, 130 paragrafi corpo/246 totali, quattro
tabelle, sei X, 13 controlli nativi/tre true identici al candidato dell'utente.
Solo word/document.xml differisce rispetto al suo DOCX; pacchetto/XML validi
e apertura con python-docx riuscita. Rendering visuale non eseguito: lo controlla
l'utente in Word. Nessuna suite applicativa necessaria per l'artefatto.

[Controlli](docs/benchmarks/2026-10-16-minervino-gold-revision-1.json),
[backup](docs/benchmarks/2026-10-16-minervino-gold-revision-1-audit.tar.gz).
Raw minervino-gold-revision-1-20261016T141521Z/. Verificati link, tabelle, hash,
manifest e diff. Nessuna modifica al motore, DB/KB o fixture V1, nuova chiamata
provider, commit o push. Aggiornati benchmark, relazioni e indice.

**Prossimo: attendere l'OK o le correzioni dell'utente sul Word. Non congelare
il gold né avviare benchmark prima di tale conferma.**

## Gold sintetico Minervino ricevuto e revisionato — 16 ottobre

L'utente ha fornito nuovi dati/domanda-iscrizione.GOLD-SINTETICO.docx e chiede
confronto con originale e KB prima di usarlo come benchmark. Creati
[report](docs/minervino-gold-review-2026-10-16.md),
[confronto documentale](docs/benchmarks/2026-10-16-minervino-gold-review.json) e
[bundle](docs/benchmarks/2026-10-16-minervino-gold-review-audit.tar.gz).
Gold SHA-256 c4dbd36e5d1a02f987bdabde3f3cd67ab4e47291aff9d737666bfd4d875991bf.

52 occorrenze testuali confrontate con le fonti attuali: 19 iniziali, nove
società, 24 soci; valori coerenti con KB, incluse equivalenze dichiarate di
date, titoli, indirizzo e provincia. Originale uguale al modulo backend.
13 controlli nativi conservati con gli stessi ID, tre selezionati e simboli
coerenti. Sei X nelle tabelle, nessun'altra differenza testuale nelle celle.

Correzione necessaria: dopo l'intestazione del direttore eliminati i tre
paragrafi originali 51–53 con otto destinazioni. Ripristinare e compilare Elisa
anche in quel ruolo; la compilazione come socia non sostituisce l'occorrenza.
Gold da non congelare ancora. Preferenze, incarichi nominativi, attestazioni e
luogo/data non sono fatti della KB: formalizzare scheda USER/checkpoint.
Annotare policy sugli identificativi sintetici già presenti nelle fonti;
validità formale/checksum non controllati. Firma e rami alternativi vuoti coerenti.

Rilevate anche riscritture delle etichette prestampate; consigliato preservarle
o dichiarare le tolleranze del confronto. Rendering visuale non eseguito;
nessuna percentuale di accuratezza. Testi dei documenti Company MD ricomposti
integralmente dai chunk: per generalita il partizionamento storico differisce
dal corrente, senza perdita di testo; nessuna reindicizzazione effettuata.

Raw in minervino-gold-review-20261016T135700Z/, bundle 17 file. Primo raccordo
delle prove interrotto per spazi Markdown normalizzati, completato e dichiarato
nelle acquisizioni. Controllati link, tabelle, manifest, hash e diff. File gold,
originale e integrazione invariati; nessuna modifica al motore/KB/fixture,
nuova API LLM, compilazione o suite applicativa. Nessun commit/push.
Aggiornati BENCHMARK_COMPILAZIONE.md, relazioni e indice benchmark.

Prossimo: ripristinare il blocco direttore in una revisione del candidato.
Poi scheda delle scelte USER, aspettative strutturate,
controllo visuale e congelamento del pacchetto prima della baseline.

## Integrazione già nella KB: perdite dopo la lettura — 16 ottobre

L'utente segnala nuovi dati già caricati e compilazione ancora insufficiente;
chiede l'analisi di nuovi dati/ e propone gold manuale o bozza da revisionare.
Analizzati integrazione.md e domanda-iscrizione.compilato(5)(1).docx.
[Diagnosi](docs/minervino-integrazione-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-integrazione.json) e
[bundle](docs/benchmarks/2026-10-16-minervino-integrazione-audit.tar.gz).

Il file coincide con la generazione a4231f73 della sessione 607eda67, analisi
211598d4 del 15 ottobre. Integrazione ID10 presente nei cinque chunk -52…-56
su 56 inviati; testo identico al file dell'utente salvo newline CRLF/LF.
Input ricostruito e audit rivalidato identici; corpus DB uguale nei campi inviati
(il reload aggiunge metadata). 27 proposte, 21 grounded, due rifiuti FORM per
comune/provincia iniziali e quattro sospensioni del direttore per binding su
chunk diverso. Nessuna proposta per 24 posizioni soci; scope c_soc omette quel
blocco. Un gruppo checkbox respinto per etichette non letterali, zero booleani.

Dialogo ricostruito: pool 3→1→0. Il router ricompone nome+qualifica fuori dalla
quote letterale e fa ripetere il nome; poi aggiorna solo p12.s0, senza risolvere
gli attributi del firmatario dalla KB. Le ragioni coverage non formano una coda
completa di domande. 22 scritture, 21 SOURCE + un nome USER; tutte corrispondono
alla ricostruzione del testo dal report, altre 15 parti ZIP identiche. Rendering
visuale non eseguito; nessun gold completo o percentuale di accuratezza.

Archiviati raw, dialogo, stato/revisioni, report e snapshot del codice, senza
DB/credenziali; raw locali minervino-integrazione-20261016T133808Z/, bundle di
92 file. File osservati e sessione invariati. Verificati manifest, riferimenti,
tabelle e diff; nessuna nuova chiamata LLM, suite applicativa, codice modificato,
scrittura nel DB o fixture alterata. Preservati gli spostamenti/cancellazioni
dell'utente, nessun commit/push. Aggiornati benchmark e relazioni.

Prossimo: usare modulo, fonti già integrate e scelte esplicite per annotare il
gold di Minervino; l'utente può compilarlo o revisionarne una bozza indipendente.
Non serve presumere che manchino ancora tutti i dati personali/professionali.
Le nuove fonti sono condivisibili col backend isolato; gold/aspettative esclusi
dal prompt. Nessuna implementazione autorizzata da questa diagnosi.

## Minervino scelto come caso iniziale — 16 ottobre

L'utente ha scelto Minervino e chiede come ottenere il Word gold compilato.
Aggiornato [BENCHMARK_COMPILAZIONE.md](BENCHMARK_COMPILAZIONE.md): scelta del
bando registrata, scenario/azienda/data ancora da fissare, passaggi per il
gold in sezione 6.4. Le istruzioni storiche della demo non decidono il perimetro
del nuovo scenario. Per una compilazione estesa occorrono fonti più complete
e scelte USER definite prima delle aspettative, senza modificare le fixture.

Verificati hash di originale Minervino e avviso rispetto a fonti.json, entrambi
conformi. La bozza domanda-iscrizione.compilato(2).docx ha lo stesso hash della
diagnosi del 13 ottobre: output parziale di 20 posizioni con limiti già noti,
non un Word gold indipendente. Nessun nuovo gold, dato o esperimento creato.

Controlli documentali di link, tabelle e diff; nessuna suite applicativa,
nuova chiamata provider, modifica al codice, DB, fonti o fixture; nessun commit
o push. Prossimo: leggere il modulo per l'inventario umano dei requisiti,
definire lo scenario e completare un fascicolo simulato separato, quindi
compilare e revisionare il gold dall'originale prima della baseline.

## Preparare il benchmark prima dell'architettura — 15 ottobre

Richiesta corrente: nessun codice; prima di discutere l'implementazione,
inventariare ciò che serve per un ambiente di test con KB sensata, Word gold
e Markdown aggiornabile. Creato
[BENCHMARK_COMPILAZIONE.md](BENCHMARK_COMPILAZIONE.md): inventario P01–P13,
materiali disponibili/mancanti, contenuti del fascicolo aziendale, scelte USER,
gold Word/strutturato, checkpoint, isolamento e protocollo proposto.

Verificati sui file 55 posizioni del gold Labirinto V1 (44 testuali, 11 checkbox),
sette fonti e 11 hash del manifest, tutti corrispondenti. Il runner principale
legge direttamente la fixture, senza ingestion/sessioni/Word: non misura da
solo l'intero percorso. Esistono fixture complementari per dialogo, sintesi e
checkbox; non individuato un DOCX gold dedicato nei demo-documents inventariati.
Le bozze generate non sono un gold. V1 conservata; nuovi dati/scenari richiedono
versioni separate. Minervino come primo caso completo è una proposta, non una
scelta già concordata. Architettura e configurazione del benchmark restano aperte.

Controllati riferimenti locali, tabelle Markdown, hash e diff; nessuna suite
applicativa, nuova chiamata LLM o compilazione Word. Nessuna modifica al codice,
DB live, fonti o fixture; nessun ambiente avviato, dato inventato o gold creato.
Nessun nuovo esperimento da aggiungere a relazioni.md, che resta il registro
completo delle prove. Preservate le modifiche precedenti e dell'utente;
nessun commit o push.

Prossimo: concordare bando, scenario e data di riferimento, censire le richieste
manualmente, preparare fonti coerenti e gold indipendenti; quindi congelare
il pacchetto e predisporre l'istanza isolata per la baseline del sistema attuale.
Il nuovo documento raccoglierà gli aggiornamenti di preparazione e l'indice
delle esecuzioni; i report completi degli esperimenti rimangono in relazioni.md.

## Proposta da validare prima del codice — 15 ottobre

Richiesta corrente: descrivere l'architettura a livello concettuale, indipendente
dall'applicazione, e validarla prima di modificare qualsiasi linea di codice.
Creato [ARCHITETUTTURA_PROPOSTA.md](ARCHITETUTTURA_PROPOSTA.md), versione 0.1
da discutere. Il nome del file riprende quello richiesto dall'utente.

Proposti rappresentazione strutturale interna, proiezione JSON deterministica
per l'LLM e piano globale dei requisiti; distinti fatti, decisioni, assegnazioni,
stato, narratore e scrittura sull'originale. Inclusi alternative e compromessi,
esempio inventato completo, matrice di casi per revisione concettuale e decisioni
aperte. Gli esempi non sono contratti API definitivi; i casi non sono test
eseguiti. La proposta non è ancora validata e non autorizza implementazioni.

Intervento documentale: nessuna modifica al codice, database, sessioni,
originali o fixture; nessuna nuova chiamata provider o prova sperimentale.
Controllati riferimenti locali, parsing dell'esempio JSON, delimitatori dei
blocchi e diff. Suite software non rieseguite. Preservate le modifiche pendenti
dell'utente e i materiali dello studio precedente; nessun commit o push.

Prossimo: discutere il contratto del layer intermedio e percorrere i casi
della sezione 13, registrando le decisioni concordate nel documento prima
di intervenire sul codice. Le fasi di astra.md restano proposte successive,
subordinate a questa revisione concettuale.

## Studio architetturale approfondito — 15 ottobre

Richiesta corrente: mappare il progetto, spiegare i pochi campi compilati,
studiare prompt/input/output e narratore, confrontare le API file dei provider
e proporre un'architettura affidabile. Creato [astra.md](astra.md), baseline
`4b7d828`: diagnosi, alternative, proposta per fasi e protocollo di valutazione.
È uno studio, non autorizzazione o implementazione di una nuova architettura.

Minervino a067b0ab/e8ad0f46: copie dell'utente equivalenti alle acquisizioni;
input ricostruito e audit rivalidato identici. Corpus SQLite in sola lettura
identico ai 51 chunk inviati; 267 candidate, 21 proposte grezze, 20 condizionate
grounded e scritte nell'ultima bozza aca0a0dd, una rifiutata (Bari). Dati personali
e varie informazioni della pratica realmente assenti. Il replay in memoria del
pool passa da una domanda a zero dopo la conferma; nessuna mutazione live.

Limiti aggiuntivi dedotti dal codice: revisione del narratore sulle prime40
proposte selezionabili e export SOURCE vincolato agli ID così rivisti, senza
paginazione; non è la causa dei20 valori attuali.67 celle delle preferenze sono
testuali; ChoiceGroup gestisce checkbox native, senza massimo generale di
selezioni. Distinti da limiti dei dati, grounding tra paragrafi e granularità.
JSON compatto229.253 caratteri, system24.675; metriche AI storiche chiaramente
separate da nuove misure. Documentazione ufficiale provider consultata; nessun
upload esterno o nuova chiamata generativa.

[Metriche](docs/benchmarks/2026-10-15-astra-metrics.json),
[runner offline](docs/benchmarks/astra_inspect.py),
[backup diagnosi](docs/benchmarks/2026-10-15-astra-offline-audit.tar.gz).
Raw in backend/data/compilation-audit/astra-20261015-02/; primo errore nello
script di misura conservato in astra-20261015-01/. Registrato anche in relazioni.
Verificati parsing/equivalenza, replay, hash/sessione invariati, link locali,
esempi JSON, Ruff del solo runner e diff. Suite applicative/browser non
rieseguite; nessun nuovo gold, benchmark LLM o rendering visuale.

Preservate cancellazioni/rinomine RELATORI e altri materiali dell'utente.
Nessuna modifica al motore, DB, originali, fixture, migrazione o reindex;
nessun commit/push. Prossimo: discutere priorità e criteri dello studio, partendo
dal denominatore dei campi realmente compilabili e dalle perdite per fase.
Le nuove responsabilità proposte non sono decisioni già prese.

## Input del narratore nella radice — 14 ottobre

Creato [json narratore.json](<json narratore.json>), estrazione leggibile del
JSON in `body.messages[1].content` della richiesta iniziale del narratore
Minervino, sessione `a067b0ab`, analisi `e8ad0f46`, dialogo `495c42b3`.
Contiene 20 proposte e uno slot nel question_pool, con ruoli, risposte e copertura.
È il contesto USER del narratore, non il system prompt o l'analisi globale.

Verificati parsing, equivalenza con l'acquisizione e originale invariato;
nessuna chiamata provider o suite software. Preservate le cancellazioni e
rinomine locali dell'utente dei materiali RELATORI. Snapshot documentale,
nessun cambiamento al motore; prossimo punto di ripresa invariato.

## Guida di studio dell'architettura — 13 ottobre

Creato [ARCHITETTURA.md](ARCHITETTURA.md) nella radice, con baseline `1fd0d72`:
percorso globale V12, distinzione dal RAG e dalle sessioni legacy, parser/catalogo,
ruolo dei diversi prompt LLM, grounding, condizioni, dialogo USER, persistenza,
budget e renderer dall'originale. Esempio 8421 ripreso dai JSON reali Minervino,
con proposte/valori scritti distinti e limiti concreti. Collegata da README e
RELATORI_00_GUIDA; nessuna nuova scelta architetturale implementata.

Intervento soltanto documentale: nessuna chiamata provider, modifica di codice,
database, sessioni, originali o benchmark. Verificati nuovi riferimenti, esempi
JSON, coerenza con codice/acquisizioni e diff; suite software non rieseguite.
Riferimenti storici già mancanti in STATUS a raw locali/report non modificati.
Il documento è una fotografia del 13 ottobre, non una certificazione della
completezza della compilazione. Prossimo punto di ripresa invariato: discutere
i limiti di destinazione fra paragrafi, granularità indirizzi e spazi emersi
nel controllo Minervino. Commit locale, nessun push.

## JSON per i relatori nella radice — 13 ottobre

Copiate le acquisizioni già citate con nomi RELATORI_01…09: input, richiesta,
risposta e audit della sessione reale Minervino a067b0ab (V12), report dell'ultima
esportazione aca0a0dd, input/risposte dei benchmark finali Labirinto e Minervino.
System prompt estratto letteralmente in RELATORI_02A_MINERVINO_SYSTEM_PROMPT.txt;
guida RELATORI_00_GUIDA.md e manifest RELATORI_10_PROVENIENZA_FILE.json.

JSON riformattati per leggibilità, contenuto verificato identico; nessuna nuova
analisi/provider call, modifica di codice, database o acquisizioni originali.
Controllati parsing, riferimenti, hash, assenza delle chiavi configurate e diff.
Nessuna suite software rieseguita per questa esportazione documentale.
Sono snapshot per presentazione: future compilazioni non li aggiornano.
Il report05 è dell'ultima esportazione; il compilato(2) esaminato in precedenza
era della generazione6cb97f7b della medesima analisi. La guida lo distingue.
Prossimo punto architetturale invariato; nessun push.

## Verifica compilato(2): buona bozza testuale, tre limiti — 13 ottobre

Controllato il file utente `domanda-iscrizione.compilato(2).docx`, identico alla
generazione reale6cb97f7b/sessionea067b0ab versione7 (distinta dal replay privato
e dalla vecchia sessione0ce44c51).20 posizioni SOURCE Company KB scritte,
nessun valore USER: operatore/recapiti/PIVA, dati societari e nome/qualifica/
Ordine/8421 del direttore tecnico nel ramo corretto. Quote/valori/digest
verificati nell’input reale. Tutti i paragrafi corrispondono a originale+valori,
15 altre parti ZIP invariate; sessione/originale/file utente preservati.

Tre limiti concreti: Bari omesso nella sede iniziale per quote FORM composta
solo da marker/punteggiatura («con sede in» termina nel paragrafo precedente);
indirizzo completo ridondante rispetto a via/civico separati nel ramo societario;
spazio mancante fra etichetta Ordine e valore. Sottoscrittore/soci/dati personali
non inventati; REA non scambiato con numero Registro Imprese, data societaria
non usata per iscrizione all’Ordine. Bozza buona, non completa;20 posizioni non
sono20 fatti distinti.99 motivazioni respinte non dimostrano assenza di dati.

Diagnosi in sola lettura, zero chiamate provider/generazioni/cambi codice.
Verificati XML/ZIP/fonti/integrità e diff; nessuna suite software o rendering
visuale della paginazione rieseguiti. Checkbox fuori scope come chiesto.
[Report](docs/minervino-output-2-2026-10-13.md), raw in
backend/data/compilation-audit/minervino-output-2-20261013/, bundle/manifest
in docs/benchmarks/2026-10-13-minervino-output-2-*.
Prossimo da discutere: ancoraggio attraversamento paragrafi, granularità indirizzi,
rifinitura spazi. Nessuna implementazione iniziata, nessun push.


## Consenso alla bozza: diagnosi persistente e riprova — 13 ottobre

Backend: decc725.

Caso utente: due conferme USER salvate, poi `si` alla bozza parziale fallisce
con messaggio generico. Sessione0ce44c51 alla versione6, domanda generate
conservata,20 proposte SOURCE esportabili, nessuna generazione live.
**Causa esatta storica non acquisita**: vecchio catch unificava GenerationError
con timeout e scartava il dettaglio. Non dichiarare il bug intermittente risolto:
6 replay planner e1 HTTP prima delle modifiche già riuscivano con DeepSeek.

Corretto il limite osservabile: trace locale del routing per sessione globale
con artefatto, prompt/schema/raw HTTP/output/errori/retry/usage/tempi, massimo2
attempt come prima. Nessuna credenziale/header; errore storage trace non blocca
export. Chat distingue interpretazione fallita da bozza generata e mantiene la
richiesta aperta, con motivo pubblico controllato per classe di errore.
Dettagli tecnici restano locali, non testo arbitrario di eccezioni nella UI.
Nessuna modifica a prompt/schema/routing semantico, gate SOURCE, parser,
renderer, UI o persistenza dei valori. Nessuna nuova analisi o migrazione/reindex.

Verifiche finali: **191 mirati/28,47s**, **2233 backend/161,53s**, Ruff backend e
runner, diff check. Suite intermedia ha trovato2 errori nel nuovo messaggio che
esponeva testo tecnico: corretto senza allentare i test. Software con provider
simulati. Frontend/browser/build non rieseguiti perché invariati.

DeepSeek reale:3 replay intermedi+3 finali sul checkpoint isolato. `si`,
`ok sì va bene`, `siii` → generate,1 chiamata/zero retry,20 valori SOURCE
materializzati correttamente (Elisa Romano/Ordine/8421 inclusi), spazi irrisolti
invariati, originale identico, proposte e conferme conservate. Totale diagnosi
incluse:13 chiamate/55.616 token. Non è una nuova analisi da zero né una misura
di completezza del modulo. Sessione live/versione6/stato/originale verificati
invariati; DB privati e chiavi temporanee eliminati. Nessuna riparazione manuale.

Prossimo: ritentare **nella stessa conversazione**, senza rifare compila o le
conferme. Se il guasto ricompare, acquisire nuova trace per localizzare realmente
schema/provider/timeout/percorso diverso. Limiti precedenti V12 invariati.
[Report](docs/compilazione-consenso-bozza-2026-10-13.md), raw in
backend/data/compilation-audit/generate-consent-20261013/, bundle/manifest e
metriche in docs/benchmarks/2026-10-13-draft-consent-*. Commit locali, nessun push.


## Esiti motivati dei vuoti: contratto globale V12 — 13 ottobre

Baseline fceedfc; feature backend5e50021. Causa verificata: V11 chiedeva
esplicitamente di omettere posizioni senza SOURCE senza motivarne i vuoti.
Nuove analisi V12 mantengono proposte sparse e aggiungono coverage: gruppi di ID
con motivo, esito, quote FORM e condizioni pertinenti. Backend conserva per ogni
candidate proposta/domanda, spiegazione valida, motivazione respinta, unassessed
esplicito oppure omissione. Nessuna conversione automatica in MISSING/NA/RESOLVED
e nessun nuovo valore o domanda da una motivazione. SOURCE/FORM/USER invariati.

Contesti condivisi: stessa tabella e suoi paragrafi introduttivi già catalogati,
clausole di condizioni valide con scope sul candidate, istruzioni di choice_group
già validato. Nessun allargamento dei contesti per i valori SOURCE. Quote fuori
contesto/lunghe, condizioni assenti, sovrapposizioni non approvate; errori locali
non eliminano proposte indipendenti. reading_plan.units include tutti i tipi,
con riferimenti dei contesti condivisi; non contiene significati inventati.

Sintesi iniziale riceve motivazioni e contatori distinti; il backend aggiunge
avviso veritiero su omissioni/esiti non determinati e motivazioni non validate.
Non deduce «non letto» da «omesso». Nessuna ripetizione del riepilogo nei follow-up.
coverage_summary è la copertura della **prima analisi**, non lo stato dei valori
dopo USER: per quello restano dialogue/answers/user_values e report di generazione.
Dettagli in global-report e global_audit del report DOCX; API additiva, UI invariata.
V11 archiviata rivalidata identica su due sessioni reali, nessuna migrazione/reindex.
Usare nuova conversazione per V12: non riscrive analisi vecchie in silenzio.

Test finali: **277 mirati/19,91s**, **2219 backend/162,60s**,360 mutazioni nuove
dei resoconti, Ruff backend/runner e diff check. Provider simulati/DB temporanei,
FTS5/Qdrant dove applicabile. Frontend/browser/lint/build frontend non rieseguiti:
nessun frontend/contratto consumato dalla UI modificato. Fallimento intermedio
della suite: provider del runner fixture rispondeva ancora V11, aggiornato al
contratto richiesto; le prove storiche V11 rimangono tali.

DeepSeek reale: baseline e due serie di2 prove su Labirinto e Minervino, fonti e
originali congelati, gold escluso dal prompt. Ogni prova: una sola analisi globale,
poi una sintesi nelle serie nuove; zero sessioni live/Word scritti. Finali Labirinto:
55/55 esiti,28 spiegazioni ancorate,zero omissioni/rifiuti in entrambe. Minervino:
19/17 proposte SOURCE (nome/qualifica/Ordine/8421 presenti),159/135 spiegazioni
ancorate,88/105 spiegazioni respinte,0/7 vere omissioni. **Non dichiarare completa
o semanticamente affidabile tutta la copertura Minervino.** Serie iniziale conserva
anche una prova con sole5 proposte SOURCE: variabilità reale, non nascosta.
10 analisi+8 sintesi,811.409 token acquisiti; nessun risparmio dimostrato.

Prossimo: correggere associazione dei motivi ai blocchi ripetuti e dei predicati
di sezione, senza allentare quote/scope né promuovere claims MODEL. Controllare
perché i7 controlli nativi di scelta del ruolo vengono ancora omessi in una prova.
Le condizioni «IN QUALITÀ DI» e le domande ridondanti restano un limite distinto.
[Report](docs/compilazione-esiti-vuoti-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-field-decisions.json), raw locali in
backend/data/compilation-audit/field-decisions-20261013/; bundle/manifest in docs.
Commit per passi, nessun push. Originali e checkpoint sessioni live preservati.

## Dialogo di compilazione: aggiornamenti brevi e feedback stabile — 13 ottobre

Corretto il percorso conversazionale globale: ricevuta provvisoria/vecchia sintesi
non lampeggiano durante refresh/resolve; un solo indicatore contestuale. Riepilogo
AI iniziale separato dalla prosecuzione: ContinuationPlan contiene soltanto
questions/held_proposal_slots; il backend conferma le mutazioni realmente accettate,
senza rigenerare ogni volta l'inventario SOURCE. Domande booleano/valore distinte
anche nello schema inviato al provider, slot assegnati dal backend. Guard respinge
semplice assenso a domanda aperta; aggiornamenti parziali conservati, senza
nascondere quelli scartati. Rimossi contatori tecnici dalla domanda primaria.

Narrazione finale globale salvata nel turno corretto della cronologia. Vecchie
domande non in pausa aggiornabili con `riprendi`, solo presentazione, nessuna nuova
analisi; pausa/ripresa conserva il gruppo sospeso. Nessuna migrazione/reindex,
modifica RAG/parser/renderer o upgrade fattuale delle proposte.

Verifiche finali: **203 mirati/28,42s**, **2178 backend/162,97s**, **106 frontend**,
**8 browser desktop/mobile/reduced-motion**,320 mutazioni domande strutturate,
Ruff backend/runner, Oxlint, build e diff check. Provider simulati nelle suite.
DeepSeek reale: replay HTTP privati sul medesimo checkpoint SOURCE,
due conferme+rinvio accettati, ricevuta13 parole,18 proposte SOURCE preservate,
zero nuove analisi/export. Conservati esperimenti intermedi falliti: il solo
prompt non bastava. Sessione live/versione9/stato/originale verificati invariati.
Ultima replica after10 conferma anche fingerprint globale DB invariato; after09
ha invece fallito quel controllo globale (differenza non localizzata, possibile
reload/FTS), con sessione/originale invariati. Conservato, non nascosto. Il runner
ora acquisisce hash prima/dopo per tabella. La selezione di domande locali resta
variabile, anche se la ricevuta non ricapitola più l'inventario aziendale.

**Limite non risolto:** condizione storica c.qualita ancorata soltanto a
«IN QUALITÀ DI». Nel replay di ripresa il modello chiede un ruolo troppo specifico;
risposta USER di ruolo diverso respinta dal validator booleano, senza mutazione.
Contratto chiuso non certifica correttezza semantica delle condizioni iniziali.
Prossimo: separare queste condizioni/scelte/valori nel primo output, mantenendo
SOURCE/USER rigorosi. Non dichiarare compilazione completa o qualità perfetta.

[Report](docs/compilazione-dialogo-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-conversation-flow.json), raw locali in
backend/data/compilation-audit/conversation-flow-20261013/ e bundle/manifest
in docs/benchmarks/2026-10-13-conversation-flow-*. Commit piccoli, nessun push.

## Chat: tolto il riquadro «Informazioni mancanti» — 13 ottobre 2026

Feedback utente: nel riassunto del modulo il riquadro confonde sezioni non
recuperate, dati aziendali assenti e campi da compilare. Rimosso dalla chat,
anche per i turni storici, con relativo CSS orfano. Rimangono testo assistant,
limitazioni espresse nella risposta e disclosure delle evidenze con ruolo.
missing_information resta invariato in API/DB/report e nei percorsi MIXED;
nessuna migrazione o modifica del workflow di compilazione.

Istruzione del generatore normale: limiti pertinenti direttamente in answer;
riassunto FORM senza elenco inventato di sezioni assenti/non recuperate e
missing_information vuoto. Prompt MIXED/retrieval/parser/renderer invariati.
Non rende esaustivo il retrieval né garantisce ogni affermazione del modello:
testo storico salvato invariato, sola lista UI eliminata.

Verifiche effettive:9 test pagina mirati (inclusi nei **105 frontend completi**),
**136 backend mirati** generation/form_retrieval, **10 browser Chromium** su
desktop/mobile (8 chat-limitations+document-mentions,2 visual/no-evidence),
Oxlint, build TypeScript/Vite, Ruff e diff check. Provider/API simulati,
nessun benchmark AI reale né suite backend completa rieseguita per questo
intervento circoscritto. Un filtro browser iniziale non selezionava test;
il vecchio scenario visual falliva sul placeholder obsoleto: aggiornato solo
quel caso, poi passato insieme alla rimozione della lista. Log conservati.

[Report](docs/chat-limiti-risposta-2026-10-13.md),
[acquisizioni software](docs/benchmarks/2026-10-13-chat-limitations-checks.txt).
Commit locale, nessun push. Prossimo: riprovare il riassunto nella chat; la
copertura e le condizioni della compilazione restano il punto tecnico sotto.

## Copertura testuale e rinvii locali — 13 ottobre 2026

Richiesta: correggere i tre problemi testuali Minervino; miglioramento checkbox
rinviato. Due passi implementati, c9a28fe/052c473: stessa analisi globale con
reading_plan di riferimenti strutturali/ruoli e indice letterale proprietà SOURCE;
clarifications locali grounded FORM (max16), nessun valore senza SOURCE/USER.
Rinvio locale non sospende altri field; rinvio di conferme condivise esplicita
perimetro e passa dal verificatore semantico esistente. Sintesi distingue rinviati
e indizi SOURCE non ancora valutati. V11 additivo, vecchi raw senza nuovo campo
compatibili. Nessuna migrazione/reindex, nuova UI o modifica RAG/parser/renderer.

**Copertura migliorata, non chiusa:** sei analisi reali Minervino propongono
nome, qualifica, Ordine e8421; serie finale18/19/19 proposte SOURCE contro9/16/4
nella prima, con stesse fonti. Non sono RESOLVED. Una prima conversazione chiede
ancora denominazione già in KB; dato negativo conservato. Il modello può ancora
creare conferme troppo ampie sulla qualità/identità: non eliminare condizioni per
esportare più valori. Chiarimenti locali corretti nei test, decomposizione semantica
non garantita in tutti gli output. Indirizzi ripartiti ancora variabili.

Due conversazioni HTTP ASGI nuove/private, provider reale, quattro turni ciascuna.
Prima scrive quattro dati professionali senza valori USER; seconda recupera19
proposte ma rinvia la conferma rimasta e genera, con consenso esplicito, una copia
vuota. Non presentarla come compilazione riuscita. Labirinto V1: undici testi e
cinque booleani già supportati per entrambe le serie.43 checkpoint comandi:42/43,
limite export-no già noto, nessun export non autorizzato.87 chiamate/8 analisi,
934.320 token,1.245,68s AI sommati, nessun risparmio di costo/latency dimostrato.
Verificati otto DOCX/26 valori per posizione, tutte le altre posizioni e parti ZIP;
DB/originali live invariati, credenziali/DB privati eliminati. Gold escluso dai prompt.

Fuzzing:960 mutazioni globali+480 piani chat e boundary HTTP. Riprodotti e corretti
formatter422 che causava500 su Unicode/NaN/infinito, diagnostici non serializzabili,
retry router con Unicode invalido. Escape solo diagnostico, nessuna riparazione
fattuale/catch generale. JSON modello invalido->502 controllato/FAILED, nessuna
scrittura. Finali **214 mirati/25,74s**, **2146 backend/152,53s**, Ruff/diff check;
provider simulati/FTS5/Qdrant nei test. Frontend/browser non rieseguiti, UI invariata.
Ultimo fix Unicode dopo le API, nessun prompt valido misurato cambiato.

[Report](docs/compilazione-copertura-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-text-coverage.json), raw in
backend/data/compilation-audit/text-coverage-20261013/,
[bundle](docs/benchmarks/2026-10-13-text-coverage-audit.tar.gz) e
[manifest](docs/benchmarks/2026-10-13-text-coverage-manifest.json).
Conservati anche fallimenti/runner/vecchie aspettative software corrette.
Originale utente domanda-iscrizione.compilato.docx preservato. Commit piccoli,
nessun push. Per provare l'input aggiornato usare una nuova conversazione.
Prossimo: separazione semantica identità del partecipante/qualità del firmatario
e copertura residua; non dichiarare risolti completamente tutti e tre i limiti.
Checkbox restano rinviate secondo la richiesta corrente.

## Minervino: bozza reale fornita dall'utente — 13 ottobre, diagnosi

Verificato domanda-iscrizione.compilato.docx, identico al file della sessione
e484f26a4d02493185d76606215f0bf2/versione 7. **Nove valori SOURCE scritti** nel
ramo societario, ai candidate indicati nel JSON; **tutte le tredici checkbox vuote**.
Il campo «sede legale in» riceve l'intero indirizzo e ripete via/civico presenti
nei campi successivi: associazione semantica da rivedere, non slittamento del writer.
Stato GENERATED indica export parziale autorizzato. Originale/file/sessione
invariati, quindici parti ZIP non body invariate. Nessuna nuova API o modifica
al codice applicativo/database, soltanto diagnosi e documentazione.

Output DeepSeek: choice_groups={} e zero assegnazioni checkbox. 267 candidate,
16 proposte, 15 grounded conditional, una rifiutata (Bari: quote con due marker),
251 omesse. Non chiamarle 251 campi obbligatori/mancanti. Direttore tecnico
Elisa Romano/qualifica/Ordine/8421 presenti nell'input SOURCE effettivo, ma
nessuna proposta per i relativi field: omissione nella generazione JSON.

«società di ingegneria» -> CONDITION_TRUE c2 sui dati societari, non selezione
USER di una checkbox: nessun gruppo attivo. «la seconda lascia vuoto» -> SKIP
c1, rinvia sei proposte aziendali dell'intestazione oltre alla domanda sul
titolo del sottoscrittore. Sintesi «li propongo in entrambe» poco chiara rispetto
al rinvio; export scrive correttamente solo nove valori. Tipo societario e
rappresentanza sono uniti nella stessa condizione: modellazione da affinare.

[Report](docs/minervino-output-2026-10-13.md), raw in
backend/data/compilation-audit/minervino-output-20261013/. Confronto read-only
stato/report/XML/quote SOURCE passato; suite/provider/browser non rieseguiti,
non necessari alla sola diagnosi documentale. Diff/riferimenti controllati.
**Prossimo intervento da discutere, non implementato:** copertura verificabile
di sezioni/scelte, collegamento a gruppi checkbox validati, separazione di
tipologia/ruolo e perimetro dei rinvii. Preferenza per migliorare il primo
passaggio globale; recupero bounded con chiamata aggiuntiva è un'alternativa,
con costi/tempi maggiori. Nessun ritorno ai batch da 12, nessun push.
Acquisizioni: [bundle](docs/benchmarks/2026-10-13-minervino-output-audit.tar.gz),
[manifest](docs/benchmarks/2026-10-13-minervino-output-manifest.json), 24 file
/1.573.365 byte grezzi, verificati byte per byte e senza chiavi/DB.

## Crash su gruppo checkbox rifiutato — 13 ottobre 2026, corretto

Il test manuale Minervino ha trovato un KeyError in export_selection durante
la sintesi: un gruppo rifiutato per label oltre 250 caratteri conservava solo
diagnostica/proposta, ma veniva letto come GROUNDED_GROUP con min_selected.
Corretto il consumer: regole solo per gruppi validati, quarantena invariata,
proposte indipendenti conservate. Nessun aumento dei limiti o catch generico,
modifica RAG/UI/parser/renderer o promozione FORM/USER a SOURCE.

Riproduzione con l'esatto audit e output reale prima del fix; dieci regressioni
software prima fallite e ora passate. **136 mirati /22,84 s**, **2.061 backend
/153,38 s**, Ruff backend/runner e diff check. Provider simulati/FTS5/Qdrant nei
test, nessun frontend/browser ripetuto (contratti/UI invariati).
Replay della risposta registrata ora valido, più **una nuova sintesi DeepSeek
Flash /3,81 s /3.845 token**, nessuna nuova analisi o retry: tredici proposte
SOURCE conditional conservate e due domande, nessun DOCX/valore inventato.
Sessione/versione/originale live verificati invariati; non è un nuovo E2E.

La sessione dell'errore resta FAILED: «riprendi» dopo aggiornamento backend
autorizza il normale nuovo tentativo; il vecchio audit era su disco, non ancora
nel DB. Nessuna riparazione manuale o migrazione/reindex.
[Diagnosi e verifica](docs/checkbox-crash-2026-10-13.md); raw locali in
backend/data/compilation-audit/rejected-checkbox-20261013/. Commit piccoli,
nessun push. [Bundle](docs/benchmarks/2026-10-13-checkbox-crash-audit.tar.gz) e
[manifest](docs/benchmarks/2026-10-13-checkbox-crash-manifest.json): 81 file,
1.818.061 byte grezzi, senza chiavi/DB, verificati byte per byte.
Prossimo: verificare la ripresa manuale; copertura dei gruppi
complessi/senza SOURCE ancora da discutere, non risolta da questo fix.

## Checkbox V11 — 13 ottobre 2026, implementate e misurate

Nuove analisi V11: gruppi FORM e opzioni con marker fisici, assegnazioni bool,
SOURCE positiva pertinente o scelta USER nel gruppo attivo. Renderer per controlli
legacy/content control dall'originale, cardinalità finale e deselezioni esclusive
tracciate. Una chiamata di analisi, nessuna nuova UI/checklist o promozione a
RESOLVED. Versioni precedenti leggibili/rivalidabili, nessuna migrazione/reindex:
provare in conversazione nuova. RAG e collegamento SOURCE testuale invariati.

Correzioni misurate: confronto locale NFC/case/spazi, prova positiva SOURCE
completa anche per attributi inline, riuso del binding strutturale del gruppo
senza esigere il marker duplicato nel field. Quote/label/paragrafo restano coerenti.
Riprodotte omissioni ai bordi dei gruppi esclusivi: ora richiesta la lista fisica
completa, conservativamente la tabella o riga locale. Nessuna regola del demo.

DeepSeek reale, fixture/gold congelati e tutti gli esiti conservati: nove analisi
sul set dedicato. Serie finale: dieci booleani grezzi corretti in ciascuna prova;
**10/10/7 checkbox e 2/2/2 testi scritti**. Tre scelte partner del terzo run restano
conditional, non scritte; nessun valore inventato nelle quattro caselle senza
prove. Tempi analisi 46,81/27,21/62,48 s, nessuna conclusione causale sulla latenza.
Labirinto V1: cinque checkbox e undici testi scritti, altri sei testi conditional.
Primo Labirinto con zero checkbox conservato con diagnosi case-sensitive.

Due sessioni HTTP ASGI nuove/private con provider reale: prima solo due testi
per marker duplicato richiesto; dopo fix **dieci checkbox e due testi SOURCE**
nel Word, zero valori USER. Verificati 14 DOCX/50 valori testuali per posizione,
stati checkbox, celle non selezionate e parti ZIP estranee. Originali/DB live
preservati, DB e chiavi private eliminati. Dialoghi USER preparati: **4/4**;
persistenza/export USER testati software, non dichiarati nuovo E2E completo.
Rivalidazione finale di 13 raw senza nuove API conserva tutti i gruppi accettati.

**Limiti reali:** gruppi senza SOURCE possono essere omessi e non diventare
chiarimenti; nella nuova sessione non ci sono valori USER accettati. Risposte
fuori dal gruppo attivo falliscono il router senza scritture. Dialogo V1 reale
**42/43**: export-no respinto due volte per answer_fields senza slot, zero export
non autorizzati. Resa desktop Word legacy non verificata, simboli non nativi
esclusi. Non dichiarare completa la compilazione automatica.

Unica estrazione da tre bandi: **Trapani**, 115 candidate/zero checkbox native;
otto testi conditional, 107 posizioni omesse, zero valori scritti senza conferme.
Nessun gold, percentuale o redraw. Totale prove: **100 chiamate /14 analisi
/651.258 token /1.199,90 s AI sommati**, non tempo wall o prezzo fatturato.
Software finale **2.051 backend /151,19 s**, 109 mirati /16,41 s e 41 scelte
/2,53 s (sottoinsiemi sovrapposti), Ruff backend/runner e diff check. Provider
simulati/FTS5/Qdrant nei test; frontend/browser non ripetuti, contratti/UI invariati.

Commit piccoli autorizzati, nessun push. [Report](docs/checkbox-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-checkboxes.json),
[bundle sanificato](docs/benchmarks/2026-10-13-checkboxes-audit.tar.gz),
[manifest](docs/benchmarks/2026-10-13-checkboxes-audit-manifest.json).
Raw in backend/data/compilation-audit/checkboxes-20261013/; bundle di 917 file,
13.240.541 byte grezzi, verificato byte per byte e senza chiavi/DB.
SHA256 84ad2b3900dfe96901775a1ca936bfb490e118258ca86f3323a78f813498bd04.
**Prossimo punto:** discutere/misurare la copertura dei gruppi senza SOURCE,
senza aggiornare destinatari mai domandati. Turni composti ancora da discutere.

## Sintesi e contesto SOURCE dei ruoli — 12 ottobre 2026, verificato

La sintesi perdeva la prova SOURCE persona–ruolo conservata dall'audit, e vedeva
solo ruolo FORM e prove dei singoli valori. Corretto solo il JSON/task in
`compilation_global_dialogue.py`: mappa condivisa di contesti di ruolo per
binding/soggetto/entity e riferimento per proposta. Conserva quote del ruolo,
compresi limiti temporali; nessuna deduzione di ruolo da altri campi/USER.
Mappa solo per fact/binding GROUNDED_PROPOSAL e relazione del field literal_match,
senza errori, prove SOURCE non General KB. Massimo40 contesti, due quote800,
flag di troncamento, stessa singola chiamata di sintesi. Nessun API/UI/RAG/parser/
renderer modificato, nessuna keyword del demo, migrazione o reindex.

**Rettifica del precedente 8/12:** il runner del replay usava il catalogo grezzo
senza anchor; `form_context` era vuoto. Corretto il setup con `build_global_input`,
come l'applicazione reale. La baseline fedele esporta già12: non rivendicare
un miglioramento applicativo 8->12. Raw/gold storici conservati e annotati.

Set separato congelato prima delle API: sette audit reali/autoriali, **DeepSeek
Flash BEFORE5/7 ->AFTER7/7**. Sei campi impropriamente ammessi in due casi di
incarichi cessati ora sospesi. Catanzaro12 e Labirinto17 mantenuti; condizioni
non confermate restano bloccanti. Gold mai nel prompt o adattato agli output.
Nessuna nuova analisi SOURCE; non è accuratezza di compilazioni complete.
Input medio +455 token/sintesi, chiamate invariate. Due replay HTTP ASGI da
snapshot nuovi: conferme in un turno +consenso alla bozza nel secondo;12 SOURCE
realmente scritti, incluso8421, zero valori fattuali USER. Originali/altre celle/
checkbox e tabelle live invariati, snapshot e chiavi eliminati. Totale prove:
**22 chiamate /59.025 token /32,65s AI**.

Software: quattro controlli protocollo /1,97s, **143 mirati /21,30s**, **1.985
backend /144,54s**, Ruff backend/runner, diff check. Test software con provider
simulati distinti dal benchmark reale. Primo test incompleto sui campi omessi e
stile Ruff corretti prima delle API. Frontend/browser non ripetuti: nessun
contratto/UI toccato. Commit piccoli autorizzati; nessun push in questo intervento.

[Report](docs/sintesi-ruoli-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-narration-roles.json).
Raw in backend/data/compilation-audit/narration-roles-20261012/; bundle sanificato
e manifest in docs/benchmarks/2026-10-12-narration-roles-*.
Bundle218 file /1.143.542 byte, verificato byte per byte e senza chiavi/DB;
SHA256 be28938aa7c3bd0aa98b69d0e0c01ce60c4427c3615245da2e15910b3588675b.
Restano revisione semantica probabilistica e cautele generiche nel testo libero,
informazioni esterne alle quote non disponibili, sparse coverage e checkbox.
**Le sospensioni già persistite restano cumulative**: usare una nuova sessione
per osservare il comportamento, nessuna revoca automatica o modifica ai dati live.
**Prossimo punto:** scegliere con l'utente fra copertura dei campi omessi e comandi
composti «salva valore e poi pausa/export», ancora da discutere; nessuna decisione
presa. Il RAG generale e il collegamento SOURCE restano invariati.

## Conferme del gruppo attivo — 12 ottobre 2026, fix verificato

Nota successiva: il replay8/12 descritto qui sotto aveva un errore del catalogo
nel runner (anchor mancanti). Vedi rettifica e baseline fedele nella sezione
precedente; risultati storici conservati, attribuzione non più applicativa.

Corretto il falso negativo Catanzaro del turno «Confermo entrambe ... il
partecipante è quello indicato nelle fonti». Il router era corretto; il gate
indipendente perdeva la domanda naturale per slot, già persistita, e non
esplicitava l'ambito dei riferimenti al gruppo. `routing_context` conserva
ora question (600 caratteri massimo, default vuoto per i checkpoint storici);
il task del verificatore distingue riferimenti univoci, conferme estese al
gruppo, eccezioni locali e richieste di valori mai forniti. Nessuna keyword
USER, ID/label del demo hardcodati, nuovo schema/API o chiamata aggiuntiva.
Restano guard indipendente, solo SUPPORTED, quote USER, validator DOCX e CAS;
un sì senza ambito a più condizioni resta ambiguo. SOURCE/FORM/RAG/parser/
renderer/UI invariati; nessuna promozione a RESOLVED o migrazione/reindex.

Congelati 16 casi separati prima delle API: DeepSeek Flash reale **BEFORE
14/16**, **AFTER 15/16**, precisazione sul gruppo misto **AFTER-2 16/16**.
Conservati tutti gli esiti intermedi; gold mai cambiato, niente ripetizioni
selettive. Regressioni reali: **9/9** guard storico, **43/43** Dialogo V1,
un retry strutturale export-no rifiutato prima di qualsiasi scrittura/export.
Sono proposte/checkpoint preparati, non accuratezza di moduli completi.

Replay dichiarato del checkpoint reale Catanzaro, nuova sessione in snapshot
privato, raw dell'analisi precedente rivalidato contro originale e corpus:
due conferme USER salvate in **un turno anziché due**, nessun valore fattuale
USER, nessuna nuova analisi. Quattro chiamate reali routing/gate/sintesi nei
due turni (conferma + richiesta esplicita di bozza), 12.810 token /5,83 s AI.
Bozza generata con **otto valori SOURCE** correttamente scritti, inclusi i
cinque aziendali. **Criterio dei 12 export NON superato**: sintesi indipendente
sospende quattro proposte del direttore tecnico per dubbio sul ruolo. Tutte
le 12 proposte SOURCE restano persistite, zero RESOLVED. Limite conservativo
distinto, non corretto o attribuito causalmente al fix dei riferimenti.
Originali, tabelle live e codice invariati durante il replay; nessuna cella
aggiuntiva modificata, parti Word/checkbox inalterate salvo banner. Snapshot
e chiavi private eliminati; errore iniziale del setup prima delle API archiviato.

Totale prove: 100 casi indipendenti +2 turni replay, **117 chiamate /282.267
token /142,30 s AI**. Nessuna chiamata aggiunta nel percorso applicativo;
prompt più esplicito costa 500 token input in più per verifica del caso
reale. Singole serie, affinamento sullo stesso set: non valutazione held-out.
Software (provider simulati): **270 mirati /47,74 s**, **1.972 backend finali
/151,49 s**, Ruff backend/runner e diff check. Prima suite completa sul codice
intermedio: 1.972 /146,40 s; mirati iniziali 72 /7,39 s; quattro test protocollo
/0,54 s. Errore di path in un comando mirato senza test eseguiti conservato.
Frontend/browser non ripetuti: nessun contratto/UI cambiato; HTTP del replay ASGI.

[Report](docs/conferme-gruppo-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-group-confirmations.json),
[acquisizioni sanificate](docs/benchmarks/2026-10-12-group-confirmations-audit.tar.gz).
Grezzi backend/data/compilation-audit/group-confirmations-20261012/.
Commit piccoli con protocollo/fix/prove; nessun push in questo intervento.
**Prossimo punto:** valutare separatamente i falsi negativi della sintesi sulle
proposte già grounded, soprattutto ruolo del direttore tecnico. Composizione
«salva valore e poi pausa/export» ancora da discutere; nessuna scelta presa.
Copertura sparse, checkbox e separazione Ordine/numero restano limiti noti.

## Conversazioni complete reali — 12 ottobre 2026, prima dei turni composti

Eseguito il passo autorizzato: nuove conversazioni con DeepSeek Flash reale,
analisi globale, chiarimenti, pausa/ripresa da nuovi processi e richiesta
esplicita di bozza parziale. Nessuna modifica applicativa durante le prove.
Baseline fb2894e già su origin/prune-backend; nuovi commit solo diagnostici,
nessun push in questo intervento. Nessuna decisione sui turni composti.

**Catanzaro: 12 valori SOURCE realmente scritti**, inclusi i cinque campi
aziendali, direttore tecnico, qualifica, Ordine e numero albo 8421. 307 candidate,
293 posizioni omesse; 0 RESOLVED, sono proposte globali revisionate, non una
compilazione completa. Due chiarimenti raggruppati; la frase «confermo entrambe
... il partecipante è quello indicato nelle fonti» salva soltanto il primo:
gate USER SUPPORTED/AMBIGUOUS. «Sì, confermo» nel turno seguente sblocca il secondo.
Questo falso negativo conservativo resta aperto, nessuna source trasformata in USER.
Sei turni inclusi avvio/pausa/ripresa/export, 12 chiamate /128.420 token;
analisi 133,47 s, dialogo successivo circa 1–6 s AI/turno, nessuna nuova analisi.

**Labirinto R2: 17 valori SOURCE scritti**, coerenti con valore e fonte gold
per i soli campi esportati. Una risposta unica -> CONDITION_TRUE, SKIP recapito,
UNKNOWN polizza; rinvii persistiti, nessuna domanda ripetuta, nessun valore
inventato. Pausa/ripresa della stessa sessione e consenso naturale alla bozza.
Cinque turni, nove chiamate /60.200 token, analisi 70,96 s, 34 posizioni omesse.
Prima serie R1 conservata ma esclusa dal confronto congelato: errore harness,
fonte della procedura caricata globale invece che di progetto. 16 valori, Ordine
includeva anche numero albo e campo numero omesso; R2 li separa, ma una singola
esecuzione non dimostra corretto quel limite. Corretto solo il setup del runner,
nuovo DB/conversazione, mai gold/motore nel corso delle serie.

Totale incluso R1: **16 turni /30 chiamate /248.535 token**, tre analisi,
zero retry/errori schema. Confrontati 45 valori in stato/report/Word; altre celle,
paragrafi salvo banner, checkbox e originali invariati. Nessun valore fattuale
USER inserito. HTTP reali ASGI, non browser reale; non è accuratezza di moduli
completi. **109 test software mirati /17,07 s**, Ruff completo/harness e diff
check. Suite completa/frontend/browser non ripetuti, applicazione invariata.

Nota isolamento: uvicorn --reload già acceso ha reagito ai nuovi script .py
ricostruendo gli indici di 82 frammenti di quattro artefatti live. Rilevato e
documentato: contenuti/SOURCE/conversazioni/sessioni/originali invariati, ID e
FTS cambiati. Nessun ripristino manuale; R2 usa script .txt per evitare il watcher.
Le API del benchmark hanno usato solo DB/storage isolati; snapshot/chiavi private
eliminati dopo verifiche. Per i prossimi runner evitare file .py nel watch root.

[Report completo](docs/test-conversazione-completa-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-full-conversation.json),
[bundle](docs/benchmarks/2026-10-12-full-conversation-audit.tar.gz).
Grezzi full-conversation-20261012/, registrazione anche in relazioni.md.
**Ripresa proposta:** conferme anaforiche del gruppo attivo, senza indebolire
il gate USER. Poi discutere policy «salva il valore e poi pausa/export»;
la precedenza del comando resta invariata. Copertura sparse/checkbox e separazione
Ordine/numero ancora limiti della compilazione, non risolti dai test dei comandi.

## Comandi conversazionali — 12 ottobre 2026, verificati

Intervento circoscritto al routing dei comandi, senza modifiche a UI, parser,
renderer, RAG o gate SOURCE/USER. Prompt unico esplicita oggetto e polarità:
rinvio locale SKIP, dato non conosciuto UNKNOWN, sospensione del lavoro PAUSE,
negazioni e richieste di spiegazione. PAUSE/FINISH mantengono la precedenza sui
nuovi dati nel turno. Solo nel motore globale generate fuori dal checkpoint
di generazione diventa finish, stessa operazione e stessi gate già esistenti.
Il backend usa engine/checkpoint già noti, senza matching USER o nuovi permessi;
legacy preservato perché quei due comandi lì hanno effetti diversi.
Nessuna chiamata AI o schema pubblico aggiunto, nessuna migrazione/reindex.

Congelati **28 scenari** separati in benchmark-dialogo/commands-v1 prima delle
API. BEFORE su b468ea5: **24/28**, 31 chiamate, 96.019 token /35,54 s. AFTER
su **802c483: 28/28**, 30 chiamate, 105.035 token /35,78 s, nessun retry.
Tre FAIL precedenti di nomenclatura generate/finish; un rinvio con negazione:
il router proponeva CONDITION_FALSE, il gate indipendente lo respingeva e
chiedeva chiarimento. Ora registra SKIP senza negare l'applicabilità.
I 43 Dialogo V1 originali, gold invariato: **43/43** (prima 40/43), 44 routing
+12 gate, 173.265 token /66,77 s. Un primo output answer_fields senza slot in
export-no rifiutato; unico retry -> reply, nessuna scrittura/export. Nessuna
regressione dei casi già conformi, né del blocco della denominazione nel recapito.
La correzione di due intent è in parte normalizzazione, non nuova copertura.

Stesso codice durante ogni serie, nessun caso selettivamente ripetuto. 99 turni
indipendenti /117 chiamate reali complessive; non una compilazione completa.
Checkpoint autoriali e DB/storage temporanei; profilo live solo in lettura.
Sette export confrontati realmente con Word/stato/report: sei con recapito
USER preesistente, uno vuoto. Originali/altre posizioni invariati salvo banner,
nessuna SOURCE inventata. Prompt +353 token input/router nei casi originari;
nessuna nuova chiamata: costo e singola variabilità dichiarati, nessuna
pretesa di risparmio o misura di accuratezza dei moduli interi.

Verifiche effettive: **248 mirati /37,67 s**, **1.950 backend completi /145,97 s**,
Ruff e diff check. Provider simulati nei test software; otto test fixture/harness
senza provider /1,11 s. Prime due righe lunghe Ruff del test corrette, log
conservato. Frontend/browser non ripetuti: nessuna UI/contratto cambiato.
Codice in 802c483, protocollo in b468ea5, commit locali; nessun push.

[Report](docs/comandi-conversazionali-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-commands.json),
[bundle](docs/benchmarks/2026-10-12-commands-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-commands-final-checks.json).
Grezzi backend/data/compilation-audit/commands-20261012/ e archivio sanificato.

**Limiti e ripresa:** interpretazione LLM ancora fallibile, retry osservato;
altri provider non valutati. Composizione «salva il valore e poi pausa/export»
ancora **da discutere**: per ora il comando prevale e non acquisisce il valore.
Nessuna nuova misura SOURCE/copertura/checkbox. Passo sui comandi concluso;
concordare il prossimo cambiamento prima di estendere il dominio.

## Pertinenza delle risposte USER — 12 ottobre 2026, fix verificato

Implementato un controllo semantico indipendente dopo il routing e prima delle
scritture conversazionali VALUE / CONDITION_TRUE / CONDITION_FALSE. Lo slot
attivo e la quote USER non bastavano: una correzione esplicita a un altro campo
poteva essere salvata nel recapito appena chiesto. Il nuovo verificatore valuta
messaggio, domanda, slot e proposta senza scegliere ID o inventare valori.
Massimo una chiamata breve per gruppo di quattro slot, 768 token di output,
timeout 15 s, nessun retry. Solo SUPPORTED ammette la proposta; ambiguità,
schema invalido o errore provider lasciano i dati invariati. In un gruppo si
conservano le altre risposte valide. Restano quote/validator DOCX/CAS/provenance
USER; nessuna promozione a SOURCE. Controlli di sessione, RAG, parser, renderer,
UI e analisi globale invariati.

Verifiche effettive: **277 test mirati /46,40 s**, **1.924 backend completi
/146,27 s**, Ruff e diff check passati. Test software con provider simulati;
non sono prove della qualità semantica del modello. Prima esecuzione mirata:
14 failure di asserzioni storiche su numero/ultimo prompt, corrette per la nuova
chiamata senza allentare i gate. Log sotto
backend/data/compilation-audit/reply-scope-20261012/checks/.

Prima delle API congelato un secondo set separato di nove proposte da verificare,
inclusa la proposta errata reale della baseline: benchmark-dialogo/guard-v1.
Dialogo V1 e il suo gold rimangono invariati. Serie reale su **132bc6a**:
**40/43 conformi** contro 39/43 della baseline. Sul caso critico il router
propone nuovamente di inserire la denominazione nel recapito; il verificatore
restituisce UNRELATED e il backend chiede chiarimento, senza cambiare neppure
la versione della sessione. **9/9** controlli indipendenti conformi, inclusi
il replay del vecchio raw errato, un gruppo con due parti valide e una estranea,
risposte brevi corrette e ambiguità. Nessuna regressione dei 39 casi già conformi.
Le due serie restano distinte: non sono 52 compilazioni complete.

43 routing +12 verifiche, zero retry/errori schema/eccezioni, **154.371 token
/66,20 s** turni; la sola verifica aggiunge **11.594 token /13,81 s** AI,
mediana 1,14 s per chiamata. Baseline 142.816 token /47,92 s: latenza più alta,
non un risparmio; variazioni del router non sono attribuite causalmente al fix.
I nove controlli separati consumano 8.366 token /9,68 s AI. Cinque export
confrontati realmente: quattro con recapito USER preesistente e uno vuoto,
originali/altre celle invariati salvo banner, nessuna SOURCE inventata.
Checkpoint autoriali in DB/storage temporanei; profilo live solo in lettura.
Codice immutato durante entrambe le serie, nessun caso selettivamente ripetuto.

Limiti: la verifica semantica resta basata su LLM, non è una prova matematica;
timeout/provider possono comportare falsi negativi conservativi. Restano SKIP
locale scambiato per pausa e due divergenze generate/finish. Nel messaggio misto
questa volta non è stato scritto il valore ignorando finish, ma il contratto
non è stato corretto e quel miglioramento non è attribuito al gate. RAG e
copertura SOURCE non misurati di nuovo. Nessun test frontend/browser richiesto:
UI e contratti invariati. Nessuna migrazione/reindicizzazione o push.

[Report](docs/fix-pertinenza-user-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-reply-scope.json),
[bundle dei grezzi](docs/benchmarks/2026-10-12-reply-scope-audit.tar.gz).
**Prossima ripresa:** priorità dei comandi misti ed effetto locale SKIP/globale
PAUSE, misurati sullo stesso benchmark prima di altri cambiamenti.

## Benchmark del dialogo V1 — 12 ottobre 2026, baseline reale conclusa

Richiesto misurare l'interpretazione prima di altre correzioni. Fixture/gold
congelati in e16f87e: 43 casi su checkpoint autoriali, separati da Labirinto
DOCX V1. Primo avvio interrotto PRIMA delle API per descrizione del progetto
temporaneo troppo corta; corretto solo il runner. Serie reale sul commit
4820b95, produzione invariata: **39/43 conformi**, 43 chiamate deepseek-flash,
zero retry/errori schema/eccezioni backend, **142.816 token /47,92 s** totali
(46,41 s API, mediana turno 1,10 s). Una serie, non una misura di compilazione
completa, qualità SOURCE o varianza del modello. Nessuna modifica motore/gold
nel corso della serie, nessun caso fallito ripetuto per selezionare un esito.

Problemi osservati e persistiti:

1. «Correggi la denominazione aziendale in Aurora Servizi S.r.l.» con recapito
   attivo -> VALUE sul recapito, USER: destinatario semanticamente errato.
   Il gate verifica slot, estratto letterale e validità DOCX; manca un controllo
   indipendente della pertinenza messaggio->campo. Label generica non tipizzata
   email. Era la PRIORITÀ della baseline, ora corretta dal gate sopra e
   verificata nella nuova serie reale.
2. Valore + «prepara una bozza con quello che hai già» -> salva il valore e
   ignora la conclusione, violando la priorità attuale finish sui field.
3. «Lasciamo questa conferma per dopo» -> pausa globale invece di SKIP locale.
4. Richiesta esplicita di bozza -> generate invece di finish: divergenza di
   contratto, stessa richiesta al servizio, nessuna scrittura impropria.

Consensi «sì», «ok sì va bene», «siii» e consenso esteso: quattro export reali
con un valore USER autoriale preesistente correttamente scritto; consenso alla
copia vuota: zero valori scritti. Cinque report/DOCX confrontati offline,
originale/altre celle invariati salvo banner. Nessuna SOURCE fittizia o promozione
RESOLVED. DB live solo in lettura per il profilo; DB/storage temporanei,
nessun intervento sui dati/sessioni locali. Nessuna nuova analisi, retrieval o
sintesi AI: gli intent normali sono misurati soltanto per routing. Una provenance
USER corretta non garantisce da sola l'associazione al campo giusto.

Verifiche effettive: **79 backend mirati /12,30 s**, Ruff completo, diff check.
Sei test dell'harness senza provider; gli altri software con provider simulati.
Nessuna suite completa/frontend/browser rieseguita, applicazione invariata.
Preflight e failure del runner/import/catalogo/Ruff conservati e distinti
dagli esiti DeepSeek. Grezzi: backend/data/compilation-audit/dialogue-v1-20261012-r1/.
Bundle pubblico verificato: 251 file /715.315 byte, SHA-256
42d6d271e6a313d7eda40c6c1f19feb3f2b1d3bc72c920a9d191e33c8091c669,
nessun DB/credenziali, runtime privato eliminato. Commit piccoli eseguiti;
nessun push di questo intervento.

[Report con tutti i casi](docs/benchmark-dialogo-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-dialogue-v1.json),
[bundle](docs/benchmarks/2026-10-12-dialogue-v1-audit.tar.gz),
[fixture](demo-documents/benchmark-dialogo/v1/README.md), registro relazioni.md.
**Ripresa della baseline:** verificare il gate semantico sopra, poi
priorità dei messaggi misti e SKIP locale/PAUSE. Benchmark ripetibile con lo
stesso gold; modifiche di scenario in V2. UI, parser, renderer e RAG congelati.

## Consenso alla bozza senza loop — 12 ottobre 2026

Diagnosi read-only della sessione segnalata: «si» e «siii» arrivavano già a
compilation_generate. «Lascia in bianco» aveva rinviato entrambe le condizioni,
escludendo tutti i valori dall'export. Il backend rifiutava una bozza senza
valori; il frontend sostituiva la risposta clarify con il riepilogo persistito,
ripetendo la stessa domanda di generazione. Nessun bug di interpretazione del sì.

Correzione: la UI conserva la risposta clarify reale. La proposta di export
distingue una bozza con valori utilizzabili da una copia senza valori inseriti.
Quest'ultima richiede consenso esplicito: allow_empty=false di default nella API,
allow_unresolved e user_quote non vuota; in chat consentita solo al checkpoint
di generazione, con sintesi valida e sessione non in pausa. Il consenso NON
conferma condizioni rinviate, non inventa valori e non modifica la provenance.
Report/messaggio dichiarano zero scritture quando tutti i valori sono esclusi.
Ogni generazione continua a partire dall'originale, con renderer e gate invariati.

Verifiche software effettive: **71 backend mirati /16,20 s**, **1.894 backend
completi /141,32 s**, **102 frontend /9,03 s**, **2 Playwright desktop/mobile
/7,8 s**, Ruff/lint/build/diff check passati. Provider simulati nei test.
Regressioni su consenso breve, condizioni saltate, export vuoto non implicito,
SOURCE ammessa accanto a un valore condizionale escluso e risposta backend
visibile invece del riepilogo obsoleto. FTS5/Qdrant coperti dai test parametrizzati;
nessuna modifica al retrieval. Prime asserzioni corrette per rispettare il banner
del renderer, il formato cell_id del report e lo scope della fixture condizionale.

Prova DeepSeek reale conclusa su **fb30ff5**, senza cambiare codice durante
la serie: replay del checkpoint persistito «si» e «siii» -> GENERATED, copia
senza valori in 2,22/2,18 s. Dal dialogo iniziale archiviato: «lascia in bianco»
-> «si» -> copia senza valori /5,17 s; conferma esplicita delle due condizioni
-> «si» -> **13/13 valori SOURCE materializzati** /5,03 s, inclusi i cinque
societari e 8421. Zero valori fattuali USER. Sei routing +2 sintesi /29.205
token, nessuna nuova analisi globale o retry automatico: non è un benchmark
di copertura o della latenza di una compilazione nuova. SQLite/storage privati;
sessione live e originale invariati. Harness iniziale fallito per PYTHONPATH
prima delle chiamate, log conservato. Copie private rimosse dopo backup
verificato dei grezzi senza DB/chiavi: 142 file /1.816.941 byte, SHA-256
e5f574f4832997f6fb543164c0e75f0218c128eda7d5ce41c0b4829e2bd7da5b.

[Report](docs/test-consenso-bozza-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-blank-draft-consent.json),
[bundle](docs/benchmarks/2026-10-12-blank-draft-consent-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-blank-draft-consent-final-checks.json).
Grezzi in backend/data/compilation-audit/blank-consent-20261012/.
Non occorre rifare l'analisi delle chat già in attesa. Richiesti dall'utente
commit e push. Limiti invariati: troppe condizioni ancora da confermare,
copertura incompleta, checkbox e correzioni libere. Prossimo punto: revisione
semantica dei campi ancora aperti; comandi UI da discutere separatamente.

## Report tecnico rimosso dalle risposte chat — 12 ottobre 2026

Rimosso il pulsante automatico «Scarica report proposte/bozza»: veniva mostrato
ogni volta che la sessione globale aveva report_url, anche sotto risposte
successive di normale conversazione. CompilationReply conserva il download
del DOCX generato; report, client API e endpoint backend rimangono disponibili.
La futura gestione UI dei comandi resta da discutere, senza nuovi menu.

Verifiche effettive: **101 test frontend /6,07 s**, **2 Playwright
desktop/mobile /4,3 s** (API simulate, compresi refresh e download DOCX),
lint, build e diff check passati. Aggiornate le asserzioni degli scenari
esistenti per l'assenza dei pulsanti report. Backend e motore invariati:
nessun test backend o benchmark AI rieseguito, nessuna modifica ai dati locali.
Prossimo punto: riprendere il ciclo di revisione della compilazione descritto
sotto; comandi UI ancora da progettare con l'utente.

## Revisione globale conversazionale — 12 ottobre 2026, pronta da provare

Richiesta: eliminare la checklist e i nomi XML dalla chat. La vecchia UI
mostrava direttamente l'audit; inoltre il filtro `disposition=unassigned` non
corrispondeva ai record realmente omessi (proposal=None), lasciando passare
centinaia di pseudo-campi senza etichetta.

Implementato: componente di review manuale rimosso. Una breve sintesi AI
sull'audit validato spiega informazioni/dubbi e pone massimo tre domande.
`global_compilation.dialogue` persiste messaggio, slot backend, risposte,
rinvii, USER values e proposte trattenute. Il planner esistente associa solo
slot attivi, mai ID inventati. Risposte parziali salvano solo le parti valide;
UNKNOWN/SKIP/REFUSE differiscono, pausa/ripresa conservano stato. Il consenso
alla bozza avviene nel composer, nessuna generazione implicita. Report tecnico
e download restano; SOURCE/USER distinti e validatore/renderer/CAS invariati.

L'analisi V10/catalogo V5 non cambia. Sintesi aggiuntiva: una chiamata per
passaggio, 45 s, 2.048 token output, max 40 proposte /24 questioni candidate /
3 domande. Può soltanto trattenere proposte, non convalidare rifiuti. Fonte
mutata o condizione non confermata blocca il relativo export. Nessuna nuova
analisi dopo chiarimenti; sessioni globali precedenti ricevono solo sintesi.
Nessuna migrazione/reindicizzazione. Native checkbox Word ancora non scritte.

Verifiche finali: **59 backend mirati**, **1.882 completi /136,02 s**,
**101 frontend**, **12 browser desktop/mobile**, Ruff/lint/build/diff check.
Completa dopo modifiche funzionali; dopo soli contatori/tempi sintesi: 59 mirati
e Ruff. Software con provider simulati, non misura qualità DeepSeek. Log in
backend/data/compilation-audit/conversation-review-20261012/checks/.

Prima serie reale fe73786: 13 proposte SOURCE Catanzaro, sintesi rifiutata
per questions[].text anziché question. JSON mode DeepSeek non applica il
response_schema del trasporto: schema aggiunto nel prompt (d6f9991), nessun
alias/gate rilassato. Seconda serie: ripresa della sola sintesi, dialogo,
pausa/ripresa, conferma USER del ramo ingegneria ed export in chat. 13/13 valori
SOURCE Catanzaro +17/17 Labirinto materializzati correttamente, nessun valore
fattuale USER. Nel Labirinto tre chiarimenti risposti in un messaggio
(CONDITION_TRUE/SKIP/UNKNOWN), nessun loop. Cinque dati societari e 8421 presenti.

Limite reale di sintesi: «professionista che firma» non giustificato, pur senza
scritture di firmatari. Serie chiusa prima del refinement: ora la sintesi riceve
anche il contesto del binding personale già validato e deve evitare relazioni
non attestate. UNKNOWN/SKIP con espressioni incerte possono deferire senza
essere bloccati dal guard sulle alternative, riservato a valori/condizioni.
Terza serie 8f82c59: due replay reali della sola sintesi sugli audit esistenti,
nessuna rianalisi o modifica delle sessioni: 1,87/2,02 s, schema valido,
nessuna attribuzione di firmatario. 18 chiamate totali /177.970 token,
compresa la sintesi rifiutata; prime sintesi non cronometrate separatamente.
L'analisi completa resta 108,25/88,13 s: nessun miglioramento causale di latenza
misurato. Non dichiarare una compilazione completa o un miglioramento di copertura.

Limiti: campi omessi non ancora interpretati, checkbox native non scritte,
correzioni libere fuori dagli slot/riapertura rinvii non ancora supportate.
La sintesi AI può ancora essere imprecisa; non sostituisce i gate backend.
Byte del DB live cambiati: confronto read-only conserva fonti/moduli e record
preesistenti di conversazioni/sessioni rispetto alla copia. Non dichiarare
byte-identità dell'intero DB. Originali invariati; benchmark su copie temporanee.

[Report](docs/test-chat-conversazionale-globale-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-conversational-review.json),
[bundle senza DB/chiavi](docs/benchmarks/2026-10-12-conversational-review-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-conversational-review-final-checks.json),
registro relazioni.md. Bundle: 193 file /1,039,762 byte, verificato
byte per byte senza credenziali; copie DB/chiavi temporanee rimosse. Grezzi in
backend/data/compilation-audit/conversation-review-20261012/.

**Ripresa:** ./start.sh, ricaricare la chat (anche quella già in REVIEW),
rispondere nel composer; nessuna selezione di valori/checklist. Chiedere
«genera la bozza parziale» per esportare. Prossimo passo: osservare il dialogo
reale e discutere la riapertura/correzione dei punti rinviati, poi copertura
semantica e checkbox Word. Non riattivare i vecchi batch né rimuovere API legacy.
Nessun push. Le sezioni successive documentano la baseline precedente:
le istruzioni con checkbox sono storiche, superate dal dialogo descritto sopra.

## Motore globale predefinito nella chat — 12 ottobre 2026, disponibile con start.sh

Richiesta corrente: rendere provabile con `./start.sh` la nuova compilazione e
mettere da parte il percorso precedente. «Main» indica il motore predefinito
nell'applicazione: nessun cambio di branch Git o push.

Le nuove richieste `@modulo DOCX` + «me lo compili?» creano sessioni
`engine=global`, riusando persistenza, routing e renderer. Un solo resolve
analizza tutto il catalogo V5/contratto V10; nessun batch da 12, retry automatico
o domanda V1. Le sessioni precedenti restano `legacy`, conservate e senza
avanzamento automatico dalla UI; nuova conversazione consigliata per provare.
API V1 mantenute per compatibilità, creazione diretta senza engine resta legacy.

Il risultato è una proposta da rivedere, NON RESOLVED. Disclosure nella chat:
selezione esplicita dei valori, contesto FORM/SOURCE, conferma USER delle sole
condizioni unknown dei valori selezionati, consenso esplicito alla bozza
parziale. Solo valori testuali grounded e scrivibili; alternative/rifiuti e
checkbox esclusi. Export da originale, ricontrollo SOURCE e revisione CAS anche
nella transazione di salvataggio, validatore DOCX esistente. Provenienza dei
valori SOURCE distinta da reviewed_by USER e dalle conferme di applicabilità.
Nessuna promozione automatica a RESOLVED o certificazione di completezza.

Budget: una chiamata di analisi/modulo, timeout 300 s, lease 360 s, nessun retry
implicito; il routing semantico esistente può richiedere una chiamata separata.
Max 400 candidate, 96 chunk SOURCE, 100.000 caratteri SOURCE, 350.000 input;
corpus autorizzato piccolo completo, non nuovo retrieval e non equivalente al
benchmark FTS5/Qdrant. Limite superato -> errore esplicito. Pausa, errore e
refresh non ripetono l'analisi; ripresa esplicita autorizza un nuovo tentativo.
Nessuna migrazione/reindicizzazione o modifica agli originali/dati live.

Verifiche: 58 backend mirati, 101 frontend, 8 browser desktop/mobile (compreso
movimento ridotto), 1.847 backend completi /126,81 s, Ruff e frontend lint/build
passati.
Smoke API reale deepseek-flash completato su codice congelato 449b109:
Catanzaro 14 proposte selezionabili /90,11 s AI; Labirinto V1 17 /70,05 s AI.
Quattro chiamate complessive (due routing, due analisi), zero retry, 124.772 token.
Con review USER controllata: 9/9 valori Catanzaro e 17/17 Labirinto scritti nelle
celle XML corrette; nessun valore fattuale USER, zero RESOLVED. Cinque dati
societari più direttore/qualifica/ordine/8421 presenti a Catanzaro. Originali,
DB live, celle non selezionate e checkbox invariati. API ASGI reali + provider
reale; browser separato con API simulate. Nessuna modifica applicativa durante
la serie. File live Catanzaro diverso dai confronti congelati precedenti e
fonti fixture reingestite: smoke d’integrazione, non confronto causale.
Failure intermedie di fixture legacy, tipi/mock frontend e lint conservate in
backend/data/compilation-audit/global-main-20261012/. Documentazione di uso:
[CompilationSession](docs/compilation-session-v1.md).

Limiti osservati: sede operativa uguale alla legale proposta senza condizione
locale «se diversa», esclusa dalla selezione; firmatario in altra sezione
rifiutato. Omissioni/alternative/applicabilità non complete; niente iterazione
libera globale sui valori USER. Una chiamata può durare ancora ~90 s.

[Report](docs/test-globale-chat-2026-10-12.md),
[JSON](docs/benchmarks/2026-10-12-global-chat.json),
[bundle 110 file](docs/benchmarks/2026-10-12-global-chat-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-global-chat-final-checks.json),
registro in relazioni.md. Backup pubblico verificato senza credenziali/DB;
copie temporanee con chiavi rimosse dopo la verifica.
Prompt/schema/raw/audit/stati/DOCX/log in
backend/data/compilation-audit/global-main-20261012/, anche nel bundle pubblico
senza DB/chiavi. Errori dell’harness di materializzazione conservati (cell_id,
griglia espansa, nodi lxml), corretti senza ripetere chiamate AI/export riusciti.

**Come riprendere:** ./start.sh -> modello DeepSeek -> nuova conversazione ->
@modulo DOCX + «me lo compili?» -> Rivedi proposte e condizioni -> selezione/
conferme applicabilità/consenso bozza parziale -> genera/download. Provare
questa UX e misurare copertura/applicabilità prima di estendere scritture.
Il vecchio motore non va rimosso fisicamente mentre serve alla compatibilità.


## Ruolo fra paragrafi — 12 ottobre 2026, passo V10 verificato

Catalogo V5 / contratto V10, prototipo a una chiamata. Diagnosi concreta:
Minervino perdeva il ruolo in paragraph:50 per candidate 52/53; SOURCE con
heading persona-ruolo o riga maiuscola respinte dal solo formato ruolo:persona.
Ora continuation_origin_paragraph_id conserva l'introduzione letterale per max
sei paragrafi consecutivi con candidate. Prosa nuova, blank, outline, tabelle
e checkbox interrompono il riferimento; non inferisce ruoli/sezioni e non
amplia le ancore field.form. Il binding V10 accetta due formati personali
letterali aggiuntivi, ruolo/persona completi, valori nello stesso record/chunk.
Negazioni/narrative, altri record/ruoli/persone e General KB non li attestano.
Join personale fra chunk sempre bloccato, titoli non inferiscono qualifiche.

**12 prove reali deepseek-flash**, seriali/thinking low, tutte HTTP200/stop:
sette congelate su 660bf0e, poi cinque su a037314. Dopo la prima serie, solo
TASK ricorda la copertura di tutte le occorrenze compatibili, senza cambiare
schema/gate. Nessuna modifica durante ciascuna serie; nessun retry/batch/reviewer
nuovo. V2–V9 conservano replay storico, runner attivo impone V10. Stessi fonti/
gold/originali, gold mai nel prompt. Chat/V1/RAG/parser/renderer/UI invariati.

Esiti circoscritti, inclusi gli insuccessi:

- Minervino: dati personali conservati 5/0/4/5, 8421 incluso nelle tre prove
  con direttore, contro zero personali conservati nella baseline V9. La seconda
  omette il direttore, non rifiuto SOURCE. Tre recapiti corretti 4/4, nessuno
  slittamento osservato; riga critica sei/quattro/tre/sei componenti corretti.
  Via+civico uniti in una prova e due indirizzi nel campo città da rivedere.
  Quote p16.s0 resta semanticamente debole, sebbene marker/valore siano corretti.
- Catanzaro: prima serie omette cinque dati iniziali (criterio NON passato).
  Dopo TASK conserva operatore/forma/sede/CF/PIVA in 3/3. Direttore/ordine/8421
  proposti sempre ma conservati solo nella prima di ciascuna serie. Seconda
  successiva: binding SOURCE valido, disposition=value con condizione unknown
  respinta. Terza: quote FORM «i requisiti» invece di «dei requisiti» non passa
  il confine di parola, binding respinto. Non nascondere questi falsi negativi.
- Labirinto V1: 18/22 target letterali in 4/4, dopo tutti i gate 18/18/17/18.
  Terza iniziale perde 5739 perché una citation aggiuntiva reale non contiene
  quel valore: gate SOURCE invariato. Alternative conservate, ma polizza
  ambiguous invece di conflicting in due prove, quattro checkbox omesse 4/4.
  NA sede operativa grounded solo 2/4, non dichiarare il benchmark tutto passato.

201 record, **170 ipotesi SOURCE** (62 senza condizioni unknown, 108 conditional),
due NA locali, otto review alternative, 21 rifiuti. **Zero RESOLVED/USER/sessioni/
scritture DOCX**; il prototipo resta review-only. 765.186 token /1.093,31 s AI
sommati, non E2E. Nessun risparmio input o causalità sulla latenza dimostrati.
Corpus piccolo completo (17 chunk reali autorizzati; sette fixture Labirinto),
non misura retrieval FTS5/Qdrant né completezza di compilazione. Nessuna % sui
bandi reali senza gold. Non promuovere GROUNDED_PROPOSAL a valore scrivibile.

Test eseguiti: **417 mirati /19,74 s e 1.823 backend /121,23 s**, Ruff/fixture
passati prima della prima serie; **417 mirati /19,19 s e Ruff** dopo il solo TASK.
Completa non ripetuta dopo quel refinement; frontend invariato/non eseguito.
17 replay storici esatti, 12 V10 esatti, body/input ricostruiti identici agli
snapshot, cataloghi invariati eccetto versione/continuazione. Intero DB live e
originali invariati fra entrambe le serie e verifica finale. Nessuna migrazione
o reindicizzazione. Errori Ruff/import/cwd e stdout del protocollo conservati
e distinti dagli esiti reali. Commit piccoli autorizzati, nessun push.

[Report completo](docs/benchmark-contesto-ruoli-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-role-context.json),
[verifiche finali](docs/benchmarks/2026-10-12-role-context-final-checks.json),
[registro](relazioni.md). Bundle pubblico **431 file /3.900.981 byte**, SHA-256
`dca4599fa9b17928a4799ef39dc4b548bac903dab024500fdc1835e1e8590066`.
Grezzi locali role-context-20261012/ e role-coverage-20261012/ sotto
backend/data/compilation-audit/, anche archiviati in Git senza credenziali/DB.

**Prossimo punto da discutere:** derivare dal backend la distinzione proposta/
utilizzabilità invece di affidare value/conditional al modello; stabilizzare
quote/etichette fra paragrafi, granularità e copertura prima dell'adapter
scrivibile. Non reinterpretare ora rifiuti unknown come valori validi. Il ruolo
è migliorato, il prototipo non è pronto per compilazione completa automatica.


## Destinazioni inline — 12 ottobre 2026, primo passo misurato concluso

Catalogo V4 riusa i marker strutturali del parser e aggiunge contesto prima/dopo
(max 120 caratteri per lato fra slot adiacenti). Contratto V9 vincola la quote
FORM al solo marker della destinazione, poi ripristina il placeholder originale
ed esegue i gate precedenti. Una chiamata globale, zero nuovi batch/retry.
SOURCE/ruoli/condizioni/checkbox, parser generale, renderer, V1/chat/UI invariati.
Il runner attivo impone la versione richiesta V9; V2–V8 restano per replay storico.
Quest'ultimo controllo è stato aggiunto dopo le API: sette rivalidazioni e body
ricostruiti identici, nessuna chiamata aggiuntiva né modifica durante la serie.

**Sette chiamate reali deepseek-flash** sul codice congelato `d86953b`, seriali,
thinking low, timeout 300 s: tre Minervino, tre Labirinto V1, un Catanzaro.
Tutte complete, zero timeout, gold fuori dal prompt/fonti congelate.
Minervino: sei/tre/sei proposte corrette nella riga critica; telefono/e-mail/PEC
corretti in 3/3, nessuno slittamento osservato. Tre componenti indirizzo omesse
nella prova 2: posizione migliorata, completezza ancora variabile.
Labirinto: 18/22 corrispondenze letterali valore/SOURCE in 3/3 (ultima V8: 17/22),
cinque dati societari conservati, ordine/numero distinti nelle tre risposte.
Alternative recapito/polizza conservate senza scelta; quattro checkbox omesse.
Catanzaro: operatore/forma/sede/CF/PIVA presenti con SOURCE; ramo ingegneria e
direttore omessi in questo controllo. Nessuna accuratezza % sui moduli senza gold.

106 record: 89 ipotesi di valore grounded SOURCE (42 senza condizioni, 47
conditional), quattro NA locali, sei review alternative, sette proposte personali
bloccate. **Zero RESOLVED/USER/scritture DOCX/sessioni create.** 368.132 token,
505,02 s AI sommati, non E2E. Input più grande: nessun risparmio input dimostrato.

Limiti espliciti: marker corretto non prova entailment proprietà/valore;
`p16.s0` prova 2 cita la label P.E.C. dello spazio successivo, pur proponendo
l'e-mail nella posizione corretta. Due indirizzi con granularità da rivedere;
ruoli ereditati fra paragrafi ancora bloccati; Cellulare + Telefono solo parziale.
Tutto resta review-only. Non attivare il prototipo nella chat/renderer ora.

Verifiche finali: **391 mirati / 18,40 s e 1.797 backend / 119,09 s passati**,
Ruff/fixture/diff, undici replay storici,
sette replay V9 con versione attesa, body/input identici, coordinate/sezioni/testo
originale invariati. Failure intermedie e log conservati (placeholder oggetti
Word, import order, assertion catalogo, mock runner V5 aggiornato a V9 dopo una
prima modifica alla fixture sbagliata). Frontend invariato/non eseguito.
Intero DB live e originali invariati in questa serie e dopo il guard. Nessuna
migrazione o reindicizzazione richiesta. Commit piccoli autorizzati, nessun push.

[Report completo](docs/benchmark-destinazioni-inline-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-slot-anchors.json),
[verifiche finali](docs/benchmarks/2026-10-12-slot-anchors-final-checks.json),
[registro](relazioni.md). Bundle: **259 file / 2.066.565 byte**, SHA-256
`414f43a52018547d3e317dc784910b2c0565074684e115a15f347d70abd13fd7`.
Grezzi anche in `backend/data/compilation-audit/slot-anchors-20261012/`.

**Prossimo punto da discutere:** ruolo/etichetta semantica ereditati lungo il
blocco, associazione soggetto e applicabilità prima di un adapter scrivibile.
Il passo sulla posizione ha risultati soddisfacenti, non chiude la completezza
né il problema delle citazioni semanticamente deboli. Conservare baseline/gate.

## Tre bandi reali — 12 ottobre 2026, recupero utile ma affidabilità insufficiente

Richiesta corrente: provare tutti e tre i bandi senza risparmiare sulle API;
rimandare la rifinitura di checkbox e ordine professionale. Eseguito sul solo
compilatore globale sperimentale congelato `6a33c85`, contratto V8/catalogo V3,
thinking low, una chiamata per prova. **Nessuna modifica applicativa**, sessione,
valore USER o DOCX generato. V1/chat/RAG/parser/renderer/UI invariati.

**Dodici chiamate reali deepseek-flash:** nove preregistrate, tre per documento,
massimo tre concorrenti; poi tre controlli seriali preregistrati separatamente,
stessi body/fonti/timeout 300 s. Dieci output completi, due timeout conservati.
Stessi 17 chunk SOURCE autorizzati del workspace `prova` (13 Company/4 General),
corpus piccolo completo: non misura il retrieval FTS/Qdrant o la chat V1.
Nessun gold per questi bandi, nessuna percentuale di accuratezza.

Esiti concreti:

- **Catanzaro:** cinque dati societari conservati nelle tre risposte complete
  su quattro tentativi: operatore, forma giuridica, sede, CF e PIVA. Direttore,
  qualifica, ordine e 8421 proposti ma bloccati: gate persona/ruolo troppo
  letterale nelle prove 2/3, quote non contigua nella prova 4. Non è assenza SOURCE.
- **Minervino:** 4/8/7/16 ipotesi conservate nelle quattro prove. Nella seconda,
  telefono nel civico, e-mail nel telefono, PEC nell'e-mail: tre destinazioni
  errate pur con grounding SOURCE valido. Quote FORM verificata nel paragrafo,
  non nello slot; il catalogo ha i range corretti. Prova seriale migliore ma
  non prova un effetto causale; eredità del ruolo ancora insufficiente.
- **Trapani:** stessi otto dati aziendali nelle tre risposte complete su quattro
  tentativi; PEC comunicazioni aggiuntiva solo in due. Nessuna applicabilità
  approvata. Un timeout anche qui.

109 record emessi, **91 ipotesi conditional / REVIEW_REQUIRED**, 17 proposte
personali bloccate e una NA rifiutata. Zero RESOLVED/scritture. Omissioni non
equivalgono automaticamente a MISSING o NOT_APPLICABLE; 689 candidate strutturali
non sono 689 campi obbligatori. Problemi di destinazione presenti anche ignorando
checkbox/ordine: **non ancora affidabile per compilazione completa automatica**.

597.919 token osservati; usage dei due timeout non acquisito, non consumo zero.
1.348,98 s sommati per chiamata, inclusi 600,23 s dei timeout; non durata E2E
perché la prima serie è concorrente. Nessun risparmio/costo monetario completo
dimostrato. Tre controlli seriali riusciti non spiegano da soli i due timeout.

Verifiche realmente eseguite: **314 mirati / 14,42 s**, Ruff backend, fixture
Labirinto --check, **otto verifiche fixture Catanzaro / 0,583 s**, dodici manifest,
dieci replay esatti, snapshot codice/body/fonti/originali, archivio verificato
byte per byte, scan credenziale e diff/link. Suite backend completa/frontend
non ripetute, codice invariato. Conservata failure di Ruff sui soli helper locali
di acquisizione ignorati (dieci errori di stile), non sul backend applicativo.

**Integrità:** originali, sessioni/revisioni, conversazioni/turni, progetti/file,
profili e corpus Company/General invariati. Non è invariato l'intero DB: chunk
derivati, FTS e sequenze cambiano. Osservato reload del server di sviluppo dopo
creazione helper .py nel backend; startup ricostruisce gli indici/artefatti,
riscontro coerente ma senza traccia SQL per attribuzione esclusiva. Nessun
ripristino o modifica manuale DB. Corpus della prova già congelato e identico.
Per future acquisizioni evitare helper Python nel percorso sorvegliato live.

[Report completo](docs/benchmark-tre-bandi-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-tre-bandi.json), [registro](relazioni.md).
[Verifiche finali](docs/benchmarks/2026-10-12-tre-bandi-final-checks.json),
inclusa la correzione del checker documentale che inizialmente non distingueva
righe NOT_VALIDATED dei timeout e la NA rifiutata dalle ipotesi REVIEW_REQUIRED.
Bundle `docs/benchmarks/2026-10-12-tre-bandi-audit.tar.gz`: **333 file / 3.395.750
byte**, SHA-256 `70df9a7b8bd489383d62469aa7a61769e322ffc7135d5ab4939d7eb5e07f5d69`.
Include tutti i dodici tentativi, protocolli, input/copie originali, codice,
prompt/schema/body, raw quando acquisiti, usage/audit/replay/annotazioni e failure.
Nessun DB/config privata/chiave API/bytecode. Grezzi locali anche in
`backend/data/compilation-audit/tre-bandi-20261011/`. Commit risultati autorizzato,
nessun push; nessuna migrazione o reindicizzazione applicativa richiesta.

**Prossimo passo da discutere prima di implementare:** ancorare semanticamente
la proprietà alla singola destinazione/slot, conservare il ruolo lungo il blocco
e verificare le condizioni prima dell'adapter. Partire dall'errore Minervino
telefono/civico, mantenendo test congelati e gate SOURCE. Non attivare ancora
il prototipo nella chat e non considerare le 91 ipotesi valori compilabili.

## Trapani — proposte SOURCE recuperate, 11 ottobre 2026

Intervento autorizzato sul compilatore globale sperimentale, Git iniziale pulito
`02524d8`. V1/chat/RAG/parser/renderer e dati live invariati, nessuna migrazione,
reindicizzazione, sessione creata o DOCX generato. Commit piccoli, nessun push.

Cause concrete e correzioni:
- V7 accoppiava disponibilità del dato e applicabilità del ramo, perdendo dati
  SOURCE quando il ramo era sconosciuto. V8 aggiunge conditional: conserva solo
  proposed_value/proposed_fact_id, value e written_value restano null.
- TASK ambiguo su dati completi/componenti: ora granularità della destinazione
  FORM; fatti separati solo quando il modulo separa le posizioni.
- Falsi negativi quote FORM (accento con apostrofo, whitespace/Unicode, underscore
  adiacenti/larghezza). Normalizzazione deterministica con ripristino originale,
  niente fuzzy/prefissi numerici/identificativi interni/cambio di ancora.
- Compito non esplicito su template bianco: proposal_stage=source_backed_hypotheses,
  non attesta scelta dell'operatore o rappresentanza. Semantic resta SEMPRE unknown.
- Supporto SOURCE errato della condizione contaminava campi con prove corrette.
  Solo V8: clausola FORM grounded rimane unknown; supporto opzionale invalido
  resta REJECTED con errori visibili. Ogni valore mantiene il proprio grounding
  SOURCE. FORM invalido, same/different invalidi, ruoli/fonti/valori errati e
  value+unknown restano rifiutati. V2–V7 preservati.

Misure: tre output reali hypothesis-stage rivalidati sul gate finale -> 9/8/9
conditional grounded, **gli stessi otto dati del ramo ingegneria in 3/3**.
Nuova chiamata reale congelata `396e7a6`: **nove** proposte (otto dati più PEC
comunicazioni), **39.318 token/53,5899 s**. Tutti REVIEW_REQUIRED, zero RESOLVED/
scritture. Otto dati: denominazione, via, comune, CAP, provincia, PIVA, telefono,
PEC. Fax, CF personale, firmatario, altri albi e firma omessi. Non sono 115 campi
obbligatori mancanti; 115 è l'inventario, posizioni omesse restano da valutare.

Labirinto V1 congelato: nuova chiamata 13 grounded + sei conditional,
17 target letterali, 32.419 token/62,8407 s. Cinque dati societari e alternative
recapito/polizza conservati. Limiti concreti: ordine direttore ancora unito al
numero, quattro checkbox di tipologia omessi. Nessun progresso generale di
completezza/entailment dichiarato e nessun gold modificato o inviato al modello.

**38 nuove chiamate reali**, incluse ablation fallite e controlli vuoti:
**1.223.138 token/1.484,92 s AI aggregati**, non durata E2E. Senza ragionamento
Trapani resta vuoto nei controlli: ora il SOLO prototipo/runner usa thinking low
come default, --no-thinking per il confronto. Nessuna modifica a profilo UI/V1.
Una chiamata/documento, zero retry/fallback automatici. Più token/latenza della
risposta vuota: nessun risparmio dimostrato. Richieste default identiche alle
ultime due reali acquisite con flag esplicito; equivalenza salvata.

Verifiche finali realmente eseguite dopo il default: **338 mirati/14,08 s**,
**1.765 backend/110,03 s**, Ruff, fixture --check, manifest/codice/replay,
uguaglianza richieste default e cinque fingerprint live passati. Frontend
invariato/non eseguito. Failure e controlli intermedi conservati nel registro.

[Report completo](docs/diagnosi-trapani-compilazione-2026-10-11.md),
[JSON di tutti i candidate/esiti](docs/benchmarks/2026-10-11-trapani-diagnosis.json),
[registro](relazioni.md). Bundle docs/benchmarks/2026-10-11-trapani-diagnosis-audit.tar.gz:
**1.211 file/7.976.279 byte**, SHA-256
`7035ffc9c7701e69fe5ec9c08a5616c76d6ad10ff2df7ae25991cd2ca3a66d2b`.
Include tutti i 38 raw più tre storici, protocolli/input/schema/HTTP/code/fixture/
usage/validazioni/replay/log/default-patch; verificato byte per byte e senza DB,
config o chiave API. Grezzi in backend/data/compilation-audit/trapani-*/;
non affidarsi al solo data ignorato da Git. Nessun push.

**Prossimo punto da discutere prima del codice:** verifica semantica indipendente
applicabilità/soggetto/proprietà prima dell'adapter o attivazione in chat. Questo
passo recupera proposte, non produce un DOCX pronto o valori RESOLVED. Conservare
anche i risultati negativi e tenere distinta la prova casuale dal gold Labirinto.

## Prova occasionale su un altro bando — 11 ottobre 2026, nessuna proposta

Preferenza dell'utente registrata in AGENTS.md: benchmark fisso congelato per
i confronti, più prove occasionali su altri bandi scelti a caso, separate
e salvate anche quando falliscono. Non necessarie a ogni passo. Nessuna modifica
a codice applicativo, V1/chat/RAG/parser/renderer o contratti.

Estrazione uniforme fra gli originali Minervino e Trapani, seed
`2732483673986547453`, zero nuove estrazioni: **Trapani Green**, 115 candidate
testuali. Non esiste un progetto locale Trapani: preflight con quel scope
restituisce zero fonti, **nessuna chiamata AI**. Stesso originale poi provato
nel corpus autorizzato `prova`: 17 chunk globali, 13 Company/4 General,
nessuna fonte di progetto o bypass di isolamento. Nessun upload/sessione/USER.

Una chiamata reale deepseek-flash sul codice `eacecbc`, identico prompt/schema
V7/catalogo V3: **JSON interamente vuoto**, zero fatti/condizioni/binding/valori.
HTTP 200/stop, 25.332 input + 30 output = **25.362 token**, **1,4473 s AI**.
Il modello non propone nulla PRIMA del validator; non sono 115 valori rifiutati.
Tutte le posizioni restano REVIEW_REQUIRED/non valutate; zero RESOLVED/scritture.
Il contratto sparso consente il vuoto ma non certifica completezza. Non acquisita
motivazione interna del modello: causa semantica dell'omissione non stabilita.
Nessun gold per Trapani: score del runner ignorato, nessuna percentuale di qualità.
SOURCE demo del 2026 e bando storico non dimostrano requisiti alla data della gara.

Questo conferma che migliori controlli **non equivalgono a maggiore copertura
generale**. Dati societari nelle SOURCE, ramo ingegneria non valutato; non
attribuire automaticamente l'omissione al retrieval né dichiarare corretta
l'applicabilità. Nessun codice corretto o prova ripetuta per migliorare l'esito.

Verifiche eseguite: replay identico, manifest, dieci file congelati contro commit,
estrazione riprodotta, input/corpus canonico, originali invariati, cinque
fingerprint tabelle live prima/dopo identici, Ruff, fixture fissa --check,
diff/link. Non rieseguite suite pytest/frontend/browser, codice invariato.
Conservata failure iniziale del confronto offline di metadata non inviati,
poi corretto alla proiezione canonica. Nessuna migrazione/reindicizzazione.

[Report](docs/benchmark-trapani-casuale-2026-10-11.md),
[audit delle posizioni](docs/benchmarks/2026-10-11-trapani-casuale.json),
[registro](relazioni.md). Bundle `docs/benchmarks/2026-10-11-trapani-casuale-audit.tar.gz`:
46 file/227.201 byte, SHA-256
`dbfced38011073f2c67eede173b30dbab565073945d9009a500a305c259a7886`;
raw/prompt/schema/codice/usage/replay/preflight/log, verificato byte per byte,
senza DB/credenziali. Grezzi `backend/data/compilation-audit/bando-casuale-20261011/`.
Commit piccoli autorizzati, nessun push.

**Prossima ripresa, da discutere prima del codice:** copertura e applicabilità
dei rami, includendo l'output vuoto. Non dedurre la causa da una sola risposta,
non abbassare i gate e non attivare il prototipo nella chat. Ripetere confronti
sulla fixture fissa; tenere Trapani come prova supplementare, senza adattare
le aspettative al modello.

## Legame persona/ruolo — 11 ottobre 2026, gate utile e copertura ancora limitata

Implementato il passo autorizzato nel solo compilatore globale sperimentale:
contratto V7, binding condiviso FORM ruolo / SOURCE ruolo / soggetto del fatto,
massimo 128 binding e 1–2 prove ciascuno. `value` da person richiede binding;
ruoli letterali uguali, coppia esplicita «ruolo: persona» nel chunk SOURCE reale,
origine FORM strutturalmente pertinente e stesso chunk del valore. Nessun elenco
di nomi/cariche/campi hardcoded, nuova chiamata, retry o reviewer. Binding invalido
blocca il valore, senza promuovere altri rifiuti/applicabilità unknown. Preservati
raw, prove/identità SOURCE e replay V5/V6. Mai RESOLVED/scrittura/attivazione chat.

Tre iterazioni, **nove chiamate reali deepseek-flash**, tre per commit congelato,
stessa fixture Labirinto V1/fonti/gold fuori dal prompt. `97d84fb`: 17/16/13
valori attesi, ruolo completo/breve non coincide. `c2b30b0`: 17/16/17, tutti
binding omessi. Finale `5962cb6`, esempio JSON generico al posto di istruzioni
verbose, stesso schema/validator: **17/17/17 target, 11/11/11 grounded corretti**;
quattro dati direttore incluso **5739** con ruolo literal_match in **3/3**.
Firmatario/carica inferiti nei run 2/3 sono bloccati, non valori accettati.
Cinque dati societari e alternative recapito/polizza conservati in tutte le nove.

**Regressione non nascosta:** V6b aveva 22/17/22 target; ultima serie omette
cinque checkbox tipologia. Sede coincidente NA soltanto 1/3; applicabilità
blocca ancora direttore/ramo. Literal_match NON è entailment indipendente:
entity/property, completezza del ruolo/qualificatori e condizioni restano proposte
AI; narrativa/sinonimi/altro chunk possono essere falsi negativi. Lo stesso chunk
non prova da solo ogni proprietà di una persona. semantic_review_required=true
rimane obbligatorio. Positivo firmatario esplicito testato soltanto nel software;
positivo reale direttore verificato. Nessun miglioramento generale di completezza.

Ultima serie **57.683 token/37,18 s AI**; intero intervento **172.848/110,30 s**.
−1,47% token totali medi vs V6b, input +5,15%, copertura inferiore/cache diversa:
nessun risparmio E2E dimostrato. Finali realmente eseguiti: **295 mirati/11,95 s,
1.701 backend/105,41 s**, Ruff, fixture check, CLI help, diff, nove replay identici,
manifest/codice congelato e bundle verificati. Failure iniziali di aspettativa
schema e Ruff conservate. Frontend invariato/non eseguito, nessuna migrazione/
reindicizzazione. V1/chat/RAG/parser/renderer/catalogo V3 e dati locali invariati.

[Report completo](docs/benchmark-persona-ruolo-2026-10-11.md), [registro](relazioni.md),
JSON per tutte le posizioni `docs/benchmarks/2026-10-11-labirinto-subject-binding-v7{,b,c}.json`.
Bundle `docs/benchmarks/2026-10-11-labirinto-subject-binding-audit.tar.gz`:
**361 file/1.904.168 byte**, SHA-256
`e3fff5dca5ebcfd867e2ddc3ff99f2914c35f0f6eca2d7a6019415b199a07c78`.
Include nove raw/codice/fixture/prompt/schema/HTTP/usage/audit, risposta storica
usata nel controfattuale, replay e log; esclude credenziali/DB. Nessun push.

**Prossimo punto da discutere prima del codice:** legame condizioni/ramo e SOURCE,
con verifica della copertura checkbox. Non passare all'adapter, non attivare il
prototipo nella chat, non sostituire revisione semantica con literal_match.
Il gate persona/ruolo è una protezione concreta; l'intero compilatore resta
incompleto. Commit piccoli autorizzati; preservare tutti gli esiti anche negativi.

## Alternative SOURCE — 11 ottobre 2026, esito circoscritto positivo

Autorizzato il passo successivo: una sola proposta globale può esprimere due o
più alternative grounded senza scegliere arbitrariamente. Contratto sperimentale
6: review con 2–4 fact ID, stesso soggetto/dimensione/proprietà dichiarati,
prove individuali e nessun valore scelto. Il backend blocca anche una scelta
value quando nella proposta esistono altri fatti referenziati e grounded della
stessa proprietà con valori differenti. Gate FORM/SOURCE e applicabilità invariati;
nessuna promozione a RESOLVED, scrittura, attivazione nella V1 o migrazione.

Sei chiamate reali deepseek-flash su due commit congelati `fd016dd`/`a405f3d`,
tre per iterazione, stessi Word/fonti/gold: **recapiti e polizze separati in 6/6**,
nessuna scelta/concatenazione. Cinque dati societari corretti in tutte le prove;
direttore e **5739** corretti grezzi ma applicabilità blocca il valore. Finale:
22/17/22 target proposti, 16/11/16 grounded. Run 2 omette cinque checkbox tipologia;
non sono valori false verificati. Sede coincidente NA in 3/3 finali, 5/6 totali.

Restano NA impropri rifiutati e, in 1/3 finali, firmatario inferito/grounded con
sola attestazione dell'amministratore. La seconda iterazione rafforza soltanto
istruzioni di emissione/ruolo, beneficio non stabile. **Non risolti soggetto,
applicabilità e completezza dei rami**; semantic_review_required=true resta
obbligatorio. Il backend non scopre alternative omesse dal modello; review_kind
non è un verdetto. Nessun RESOLVED, scrittura/sessione o attivazione chat.

Ultima serie 10,59–16,44 s, token totali medi **+14,67%** vs V3; nessun risparmio
E2E dimostrato. Intervento totale **119.273 token/93,11 s AI**, zero USER/retry.
Finali realmente eseguiti: **264 mirati in 10,50 s, 1.670 backend in 106,64 s**,
Ruff, fixture check, CLI help, replay/manifest/diff. Frontend invariato/non eseguito.
V1/RAG/parser/renderer/catalogo V3 invariati; nessuna migrazione/reindicizzazione.

[Report e limiti](docs/benchmark-alternative-source-2026-10-11.md),
[registro](relazioni.md), JSON per tutte le posizioni
`docs/benchmarks/2026-10-11-labirinto-alternatives-v6{,b}.json` e bundle
`docs/benchmarks/2026-10-11-labirinto-alternatives-audit.tar.gz` con checksum,
sei acquisizioni/codice congelato/raw/usage/validator/log, senza DB/credenziali.

**Prossimo punto da discutere prima del codice:** legame fra SOURCE,
soggetto/ruolo richiesto dal FORM e applicabilità del ramo nella stessa chiamata.
Non sostituire semantic_review_required con l'autodichiarazione del modello,
né passare all'adapter/rendering. Commit piccoli autorizzati, nessun push.

## Contesto JSON dei candidate — 11 ottobre 2026, esito misurato

Primo intervento autorizzato sul contesto in ingresso. Corretta l'assunzione
che ogni prima riga sia un header: il grounding locale ammette riga corrente
e sole intestazioni Word esplicite. Catalogo corrente **V3**, commit `971c5d8`:
`location` diretta blocco/tabella/riga, tabelle annidate via `parent_cell_id`,
fino a sei paragrafi precedenti per blocchi con candidate e grassetto diretto
come segnale visuale. Nessuna sezione/applicabilità semantica inventata dal backend.

Due iterazioni e **sei chiamate reali deepseek-flash**, tre per commit congelato,
con stessi Word/fonti/gold, prompt/schema output/budget. V2 (`d14fa9d`), con
seconda mappa di righe: 22/18/17 valori attesi e +30,68% token input, risultato
non stabile. V3 elimina quella ripetizione: **18/22 valori attesi in tutte le
prove**, come baseline; 12 passano i gate, zero RESOLVED/scritture. Tempi
**9,96–10,17 s**, 16.972–17.097 token. Token input +16,31% vs baseline, −10,99%
vs V2; non è dimostrato un risparmio E2E o un aumento generale della precisione.

Cinque dati societari corretti nelle sei prove senza USER. V3: sede operativa
coincidente riconosciuta NA in 2/3, ancora proposta impropriamente nella terza
e bloccata. Direttore e **5739** sempre corretti come proposta, bloccati da
applicabilità unknown. Polizza arbitraria ancora presente in tutte le prove;
terza V3 concatena due recapiti alternativi. Questi due casi possono superare
grounding letterale: NON sono valori semanticamente verificati o scrivibili.
Restano soggetto, completezza dei rami e conflitti/ambiguità da verificare.

Verifiche finali realmente eseguite: **230 mirati in 10,00 s, 1.636 backend
in 105,70 s**, Ruff completo, fixture `--check`, CLI help e diff check. Prima
iterazione fallita per budget Catanzaro e correzione namespace Word alternativo
documentate, con controlli intermedi separati in `relazioni.md`. Confronto in
sola lettura su Catanzaro/Minervino: testo/posizioni/originali invariati e budget
rispettati. Frontend invariato, non rieseguito. Nessuna migrazione/reindicizzazione.

Registro e per-candidate: [relazioni.md](relazioni.md),
`docs/benchmarks/2026-10-11-labirinto-context-v{2,3}.json`; grezzi, codice,
request/HTTP/raw/quote/usage/validator e log nel bundle
`docs/benchmarks/2026-10-11-labirinto-context-audit.tar.gz`. V1/chat/RAG/parser/
renderer invariati. Questo è un miglioramento strutturale verificato con
benefici semantici parziali; NON considerare completata la compilazione globale.

**Prossimo punto da discutere prima del codice:** rapporto fra ramo/soggetto,
applicabilità e SOURCE discordanti nella stessa proposta globale. Non continuare
ad aggiungere metadati né allentare i gate per aumentare i grounded. Non attivare
il prototipo nella chat o passare al renderer con questi risultati.
Commit piccoli autorizzati, nessun push; nessuna modifica durante i benchmark.

## Benchmark dedicato — 11 ottobre 2026, completato

Richiesta corrente: un documento complesso dedicato al nuovo compilatore e
registro permanente [relazioni.md](relazioni.md). Creato
`demo-documents/benchmark-compilazione/v1/`: Word sintetico con 55 posizioni
(44 testo/11 checkbox), sette SOURCE fittizie, gold autoriale e manifest.
Titoli visuali, rami e soggetti omonimi, condizioni ignote/annidate, ambiguità,
conflitti e fonti distrattore. Nessun caricamento nei dati locali.

Il runner globale accetta `--fixture` senza documenti/ingestion nel DB e
conserva gold soltanto nell'audit; confronto automatico limitato a valori e
ID SOURCE, non un gate semantico. Motore/V1/RAG/UI/parser/renderer invariati.
Baseline congelata `5e8cecc`: **tre chiamate reali deepseek-flash**, stesso
input/request, 9,49–12,01 s e 15.003–16.040 token. Ogni prova propone 18/22
valori/booleani con valore e ID SOURCE attesi; solo 12 di questi superano i gate.
GROUNDED totali 13/15/13 includono 1/3/1 errori semantici: polizza scelta fra
attestazioni discordanti e, nel run 2, firmatario/carica inferiti. Il run 2
riempie anche rami esclusi e secondo direttore ignoto: bloccati dalle condizioni.
Otto condizioni semantic/unknown per prova; direttore e **5739** proposti
correttamente ma ancora bloccati. Zero RESOLVED/scritture/sessioni modificate.
Non confondere omissioni con MISSING/NA verificati o tempi con E2E completo.

Verifiche effettive: **209 mirati, 1.615 backend**, Ruff completo, fixture
`--check`, CLI help, riferimenti/diff. Frontend invariato/non rieseguito.
Codice/gold/input/raw/HTTP/usage/validazioni/confronti/log conservati nei grezzi
locali e nel bundle `docs/benchmarks/2026-10-11-labirinto-v1-audit.tar.gz`;
[registro](relazioni.md) e riepilogo JSON adiacente. Nuova regola in AGENTS:
ogni benchmark futuro del nuovo motore va registrato in `relazioni.md`.

La mappa semantica condivisa e l'accettazione di soggetto/applicabilità rimangono
**da discutere** prima del codice. Prossimo punto: scegliere un solo cambiamento
e confrontarlo con questa fixture/hash, senza nuovi reviewer per gruppi né gate
allentati. Commit piccoli autorizzati, nessun push.

## Esito finale proposte sparse — 11 ottobre 2026

[Report completo](docs/benchmark-proposte-sparse-2026-10-11.md) e
`docs/benchmarks/2026-10-11-compilation-global-sparse.json`.
Commit `7190d2d` inventario backend/quarantena locale, `46128f5` schema value/NA
e tetto delle proposte coerente con il catalogo. V1/chat/RAG/parser/renderer
ancora invariati; nessuna migrazione/reindicizzazione, originali/sessioni locali invariati.

Quattro chiamate DeepSeek reali, due coppie congelate, stesso originale/307
candidate/51 SOURCE delle prove precedenti, zero USER/retry. Le prime due sono
rifiutate per tetto 128 e numerosi value senza fact_id; sono conservate come
fallimenti, non corrette retroattivamente. Nelle due finali il JSON arriva alla
validazione locale: **9/8 grounded, 40/75 rifiuti locali, 258/224 non valutati**.
ID inventati e value senza fact_id: zero. Cinque dati societari e telefono
correttamente proposti da SOURCE in entrambe; nessun RESOLVED o valore scritto.

Ultime prove **20,26/31,00 s, 76.611/81.160 token**. Medie rispetto alle ultime
due compatte: −45,24% tempo, −11,10% token totali, −49,42% output nel campione.
Non è un risparmio dimostrato di compilazione completa/produzione: schema e
cache diversi, due risposte stocastiche. Totale quattro prove: 336.553 token,
153,03 s AI; originali e input di ogni coppia verificati, codice congelato.

Inventario non ripetuto dall'IA; omissioni restano non valutate. Destinazioni
inventate e proposte invalide isolate, dipendenze da fatti/condizioni invalidi
bloccate. Scope candidate/paragrafo/tabella/outline verificati nel catalogo.
Limiti: 400 posizioni/proposte, 128 fatti/condizioni, 96 SOURCE/100.000 caratteri,
350.000 input, 49.152 token output/300 s. Nessuna chiamata per campo/reviewer.

**Non attivare ancora nella chat:** la revisione umana di tutti i grounded
trova 3/2 assegnazioni semanticamente improprie (sottoscrittore/carica inferiti,
più sede operativa «se diversa» omessa in una prova). Grounding non è RESOLVED;
semantic_review_required=true e written_value=null restano invarianti.
Le 9/19 condizioni sono grounded ma tutte semantic/unknown. Direttore tecnico,
qualifica, ordine e **8421** sono fatti SOURCE atomici proposti ma bloccati per
applicabilità del ramo non verificata; data abilitazione non proposta. Restano
false negative conservativi e completezza delle condizioni non dimostrata.

Verifiche finali realmente concluse: **188 mirati, 1.594 backend completi**,
Ruff, CLI help e diff check. Prima revisione 185/1.591 conservata separatamente;
primo Ruff con una riga lunga poi corretto. Provider simulati nei test software,
DB/storage temporanei; frontend invariato/non rieseguito. Grezzi e log in
`backend/data/compilation-audit/global-sparse-20261011-*`, anche nel bundle
versionato del report, con manifest/hash e senza credenziali/database.

**Prossimo punto da discutere prima del codice:** accettazione semantica di
soggetto/ruolo e applicabilità sulla proposta globale, senza reintrodurre
reviewer per gruppi o allentare SOURCE. Non passare all'adapter/export solo
perché il JSON ora è valido. Commit piccoli autorizzati; nessun push.

## Esito finale proposta compatta — 10 ottobre 2026

[Report completo](docs/benchmark-proposta-compatta-2026-10-10.md) e
`docs/benchmarks/2026-10-10-compilation-global-compact.json`.
Commit piccoli: `c2ec520` contratto compatto, `0972077` facts solo referenziati
/fields value-NA, `bb41dcc` origine canonica delle condizioni, `cc0485e` guard
plurali di indisponibilità (solo test software dopo il benchmark).

Sei chiamate reali DeepSeek, tre coppie a codice congelato, input identico dentro
ogni coppia; stesso originale/307 candidate/51 SOURCE, zero USER. Tutte e sei
rifiutate integralmente: troncamento, budget superato, mappa duplicata incoerente,
poi ID mancanti/inventati/sovrapposti. Nessun output riparato o accettato in parte.
Ultime due: **46,73/46,88 s e 88.650/88.816 token**, circa −38% tempo/−11% token
vs precedente V2 run2, ma non compilazioni utilizzabili. Totale sei esperimenti:
**571.502 token/376,20 s AI**. Nessuna promessa di risparmio in produzione.

Le condizioni sono ora presenti (24/19 ultime prove), origine derivata dal
backend senza mappa inversa duplicata. Non sono semantiche verificate: tutte
operator=semantic/unknown. Cinque valori societari ancora proposti correttamente
nelle SOURCE; direttore tecnico/qualifica/ordine/**8421** separati invece del
profilo composito. Restano sottoscrittore inferito, rami di partecipazione non
attestati, sede operativa proposta ignorando coincidenza e qualche value senza
fact_id/di indisponibilità. **Grounding/provenance non allentati. Nessun RESOLVED,
nessuna scrittura, nessun adapter di sessione o attivazione chat.** V1 invariata.

Controlli finali realmente eseguiti: **148 mirati, 1.544 backend completi**,
Ruff, help CLI con PYTHONPATH e diff check, DB/storage temporanei. Controlli
intermedi salvati separatamente, frontend invariato/non rieseguito. Tutti gli
originali invariati, nessuna migrazione/reindicizzazione, nessun push.
Grezzi permanenti `backend/data/compilation-audit/global-compact-20261010-*`,
più bundle versionato con codice/prompt/output/HTTP/usage/diagnosi/log e checksum
nel report; escluse chiavi, DB e configurazioni private.

**Prossimo punto da discutere prima del codice:** eliminare altre ripetizioni
che il backend conosce già (partizione degli ID) e distinguere scope strutturali
reali delle condizioni da destinazioni compilabili. Mantenere unresolved ogni
posizione non assegnata e rifiutare ID inventati; nessun nuovo reviewer a gruppi.
Completezza dell'inventario e correttezza di proprietà/soggetto/ramo restano
limiti semantici da misurare prima dell'adapter. Chat/parser/renderer/RAG intatti.

## Risultato del secondo esperimento globale — 10 ottobre 2026

Commit `a29b6f2` (fatti/condizioni condivisi e guard backend), `e7d9e1a`
(opzione isolata thinking low). Le tre nuove chiamate DeepSeek sono terminate,
codice congelato durante ogni prova, stesso originale e 51 SOURCE, zero USER.
[Report completo](docs/benchmark-condizioni-globali-2026-10-10.md) e
`docs/benchmarks/2026-10-10-compilation-global-conditions.json`.

- Senza thinking: 80,79 s/103.002 token e 76,01 s/99.462 token. Entrambe
  omettono tutte le condizioni; 247/202 grounded non misurano correttezza.
  I cinque dati aziendali restano corretti, ma il fatto composito del direttore
  tecnico è riutilizzato per nome/qualifica/ordine/numero e rami non attestati.
  NA senza condizioni rifiutate; sede operativa ancora impropria, rifiutata per
  quote FORM errata, non per il vincolo omesso. Nessun risparmio dimostrato.
- Con thinking low, stesso input/schema/validator: **156,10 s/118.242 token**,
  `finish_reason=length` a 49.152 output (37.418 reasoning). Tutta la risposta
  rifiutata. Il prefisso contiene 16 fatti/20 condizioni ma non è utilizzabile
  né accettato parzialmente. Nessun retry/aumento automatico del budget.
- Conservati prompt/schema/HTTP/output/usage, validazioni disponibili, codice,
  originale e 16 annotazioni manuali per risposta completa. Grezzi permanenti
  `backend/data/compilation-audit/global-conditions-20261010-*`, anche nel
  bundle versionato documentato nel report, con manifest/checksum e senza chiavi/DB.
- Verifiche finali effettive: **110 mirati, 1.506 backend completi**, Ruff,
  CLI help con PYTHONPATH e diff check. DB/storage temporanei; frontend intatto.
  I primi controlli 108/1.504 e il primo help fallito sono archiviati separatamente.
  Originale invariato. Nessuna migrazione/reindicizzazione, nessun push.

**Decisione: prototipo ancora isolato; nessuna promozione a RESOLVED/scrittura,
nessun adapter alla sessione.** Controlli locali aggiunti, miglioramento semantico
reale non ancora dimostrato. RAG/chat/parser/renderer/V1 invariati. I confronti
dipendono dalla mappa semantica del modello; conditions=[] non dimostra assenza
di condizioni. Anche un valore dichiarato indisponibile nella SOURCE non deve
diventare un fatto utilizzabile: rafforzare questo caso prima dell'attivazione.

Prossimo piccolo passo da spiegare prima del codice: output più essenziale,
fatti atomici e inventario di sezioni/condizioni effettivamente estratto nella
stessa chiamata. Prima regressioni per condizioni omesse, proprietà diverse,
valori indisponibili e fatti compositi, poi nuovo confronto congelato.
Non aggiungere catene/reviewer per gruppi e non allentare grounding/provenance.
Commit piccoli/API autorizzati; push solo se richiesto.

## Condizioni esplicite della proposta unica — 10 ottobre 2026

Prime due prove reali sul commit `a29b6f2`, input identico, thinking disabilitato:
80,79 s/103.002 token e 76,01 s/99.462 token. Cinque dati aziendali ancora
corretti, ma entrambe propongono **zero condizioni**. Fatti compositi del
direttore tecnico riutilizzati impropriamente fra proprietà; dati trasferiti a
rami non verificati. Le NA senza condizioni sono rifiutate; la sede operativa
è rifiutata per estratto FORM errato, non per valutazione del vincolo omesso.
**Nessun miglioramento semantico/costo dimostrato.** Audit e output completi in
`backend/data/compilation-audit/global-conditions-20261010-run{1,2}/`.

Prossimo confronto annunciato: stessa chiamata/contratto/input/validator con
ragionamento DeepSeek low, già supportato dalla V1. Solo opzione `--thinking`
del runner, default disabilitato invariato; stesso timeout/limite output.
Non è un reviewer aggiuntivo. Costi/latenza potrebbero aumentare. Congelare
prima il codice, conservare anche l'eventuale fallimento; nessuna attivazione.

Autorizzato proseguire dopo il confronto: stessa chiamata globale, fatti SOURCE
condivisi, condizioni FORM e riferimenti dai candidate. Implementato contratto
sperimentale versione 2; il primo resta leggibile per gli audit storici.
Confronti conservativi su fatti grounded dello stesso soggetto/dimensione:
valori identici possono provare same/different; grafie differenti, condizioni
semantiche e ambiti di sezione non verificati restano unknown/review. Valore
vietato se condizione falsa o ignota; NA richiede condizione calcolabile falsa
locale. Tipologia/partecipazione/poteri sono dimensioni distinte. Dettagli in
[proposta globale](docs/proposta-globale-compilazione.md).

Budget: 128 fatti, 128 condizioni, 8 riferimenti per candidate; invariati
400 candidate, 96 chunk/100.000 caratteri SOURCE, 350.000 caratteri input,
49.152 token output/300 s. Un'unica chiamata, nessun retry o reviewer aggiunto.
RAG, chat, parser/renderer e sessioni V1 invariati; zero valori scrivibili,
nessuna migrazione/reindicizzazione. La classificazione di soggetto/proprietà,
la completezza delle condizioni e il legame semantico col FORM richiedono
ancora valutazione: il risultato del confronto non sostituisce questi controlli.

Verifiche effettive prima della prova reale: **108 mirati, 1.504 backend
completi**, Ruff completo, diff check; DB/storage temporanei. CLI help riuscito
con `PYTHONPATH=.` (primo comando senza questo parametro fallito in import;
entrambi i log conservati). Acquisizioni in
`backend/data/compilation-audit/global-conditions-20261010-checks/`.
Prossimo punto: congelare il codice, ripetere DeepSeek sullo stesso originale
e corpus, annotare condizioni/valori, confrontare usage e latenza e archiviare
anche gli errori. Non attivare ancora adapter di sessione o scrittura checkbox.
Commit piccoli autorizzati; nessun push automatico richiesto.

## Proposta unica: risultati reali e punto di ripresa — 10 ottobre 2026

Autorizzati commit piccoli e API DeepSeek. Commit intermedi: `b0c0ef4` catalogo,
`79e6950` contratto/runner isolato, `6ceff03` prima misura, `2954034` riferimenti
FORM espliciti e correzione conservativa dei puntatori a chunk dello stesso file.
RAG, UI, parser/renderer operativi e CompilationSession V1 restano invariati.

- Tre chiamate reali, stesso originale upload 153 della baseline, 307 posizioni
  e tutte le 51 SOURCE documentali ammesse nel corpus piccolo, nessun USER/retry.
  Prima proposta: 71,72 s/91.517 token. Ultime due prove a codice congelato e
  input identico: 81,24 s/101.499 token (JSON rifiutato per `}` extra) e
  75,69 s/98.751 token (306 grounded, una proposta locale rifiutata).
- V1 storica: 7 chiamate/116.741 token/141,14 s AI (151,25 s service) per mappa
  e primi 12, non un documento completo. Ultima proposta globale: -15,41% token
  e -46,37% tempo AI nel campione; differiscono lavoro e selezione/cache SOURCE,
  non è una stima del risparmio per compilazione completa. Stima delle tre prove
  ~0,0855 USD alle tariffe consultate; usage completo conservato.
- Cinque dati aziendali corretti nelle proposte senza USER; nella prova valida
  finale anche direttore tecnico, qualifica, ordine e albo **8421**. Data di
  abilitazione resta missing. Valutazione manuale dei 15 valori: 14 supportati,
  uno improprio per condizione falsa (sede operativa richiesta solo se diversa).
  Quattro esclusioni della sezione consorziata esecutrice non supportate dalla
  sola tipologia aziendale. Checkbox riconosciute ma ancora senza selezione.
- **Non promuovere ancora il prototipo alla chat**: grounded non è RESOLVED.
  Tutti i valori restano non scrivibili/da valutare semanticamente, nessun
  verdetto V1 fabbricato, nessuna sessione locale modificata, zero DOCX generati.
  Il JSON invalido non viene riparato né accettato parzialmente.
- Verifiche finali effettive: **74 mirati, 1.470 backend completi**, Ruff,
  help CLI, diff check; DB/storage temporanei nei test software. Frontend intatto.
  Originali invariati; ultimi input identici, quote/chunk/provenance conservati.
- [Report](docs/benchmark-proposta-globale-2026-10-10.md), riepilogo/annotazioni
  `docs/benchmarks/2026-10-10-compilation-global.json`, raw persistenti in
  `backend/data/compilation-audit/global-20261010-run{1,2,3}/` e log/replay separati.
  Il bundle versionato indicato nell'archivio benchmark conserva le acquisizioni
  senza credenziali/database. Nessuna migrazione/reindicizzazione. Nessun push.

Prossimo passo concreto, da spiegare prima del codice: output più compatto con
fatti/condizioni condivisi e riferimenti espliciti per l'applicabilità di ogni
assegnazione. Prima test negativi per i falsi positivi rilevati, poi nuova prova
congelata; soltanto dopo adapter alla sessione/checkbox/export e rimozione V1.
Non aggiungere reviewer per gruppi né allentare il gate semantico per attivarla.

## Secondo passo misurato: riferimenti della proposta globale — 10 ottobre 2026

Dalla prima prova, senza toccare V1/RAG: anchor FORM non vuoti esplicitati per
candidate; vuoto consentito solo a posizioni decorative non scrivibili;
normalizzazione conservativa delle virgolette FORM; riferimento SOURCE recuperato
solo da quote letterale univoca nello stesso file già fornito, con puntatore
originale/effettivo entrambi conservati. Nessuna approvazione semantica automatica.
Prompt generale più esplicito su condizioni e distinzione tipologia/partecipazione.
Verifiche: **71 test mirati**, Ruff completo; replay offline della prima risposta
da 156 a 212 grounded (95 rifiutate), inclusi nome/ordine/albo del direttore tecnico.
Il replay non è una nuova risposta DeepSeek e non autorizza scritture.
Grezzi replay in `backend/data/compilation-audit/global-20261010-replay1/`.
Prossimo punto: seconda prova reale a codice congelato e confronto semantico.

## Prima proposta globale reale DeepSeek — 10 ottobre 2026

Codice congelato `79e6950`, originale upload 153 SHA `aeb1bda3…`, 307 posizioni
(279 testo/28 checkbox), tutte le 51 SOURCE documentali ammesse del corpus piccolo.
Una chiamata reale, zero USER/retry/scritture: **71,72 s**, input 62.588 token,
output 28.929, totale **91.517**. La V1 storica: 7 chiamate/116.741 token/151,25 s
per mappa e primi 12, non l'intero documento; selezione SOURCE diversa.
Cinque proposte aziendali controllate manualmente corrette e grounded, non ancora
RESOLVED di sessione. 307 ID coperti; 156 proposte grounded, 151 rifiutate.
Difetti osservati: quote FORM vuote (145, di cui 52 decorative); citazioni del
direttore tecnico attribuite al primo chunk della visura anziché quello reale;
sede operativa proposta ignorando «se diversa»; checkbox tipologia ancora incerte
nonostante SOURCE e condizione procura non distinta da valore assente.
Report versionato `docs/benchmarks/2026-10-10-compilation-global-run1.json`;
grezzi permanenti `backend/data/compilation-audit/global-20261010-run1/`.
Controlli effettivi: 62 mirati, **1.458 backend completi** con DB/storage temporanei,
Ruff, help CLI e diff. Prossimo passo circoscritto: migliorare riferimenti/contratto
del prototipo e ripetere la misura, senza ridurre i gate semantici V1.

## Proposta globale isolata: contratto e runner — 10 ottobre 2026

Salvato il catalogo nel commit `b0c0ef4`. Implementati contratto/input globale,
validator di struttura/grounding e runner a una chiamata DeepSeek, in isolamento:
[dettagli](docs/proposta-globale-compilazione.md). Completo corpus documentale
piccolo, FORM/SOURCE distinti, zero USER, nessuna modifica a chat/sessioni/renderer.
Coverage esatta; errori locali isolati. Limiti espliciti e nessun retry AI.
Verifiche realmente eseguite: 62 test mirati catalogo/mappa/proposta globale
(30 nuovi test globali), Ruff completo, CLI `--help` e diff check. Test software,
nessuna prova semantica DeepSeek ancora eseguita in questo checkpoint.
Le proposte letteralmente grounded NON diventano RESOLVED senza valutazione
semantica: tutti i valori restano non scrivibili. Nessun reviewer V1 bypassato.
Prossimo punto: congelare questo codice ed eseguire la prova reale autorizzata,
salvando usage, tempi, risposta e confronto annotato con la baseline V1.

## Passi piccoli e prove DeepSeek autorizzati — 10 ottobre 2026

L'utente ha autorizzato commit per ogni passo e uso delle API DeepSeek per
misurare token, tempi e correttezza. Primo checkpoint: catalogo strutturale
già verificato, senza attivare un nuovo resolver nella chat. Passo successivo:
proposta globale sperimentale isolata, con input FORM/SOURCE distinti,
validazioni locali esplicite e acquisizione durevole di prompt, risposte e usage.
La V1 resta la baseline fino al confronto; nessun push automatico richiesto.

## Avvio del pruning: catalogo strutturale condiviso — 10 ottobre 2026

Richiesta corrente: «iniziamo a sfoltire», dopo il confronto sulla mappa globale
del Word e sulle condizioni già determinabili dalle SOURCE. Autorizzato l'avvio
graduale; spiegate prima del codice le scelte della prima milestone.

- Implementato `compilation_catalog.py`: contesto FORM presente una volta,
  ordine dei paragrafi, righe/celle fisiche, merge, tabelle annidate, gerarchia
  esplicita degli outline, richiami alle note e parti accessorie in sola lettura.
  Candidate testuali con ID esistenti e checkbox native legacy/content control,
  inline o a blocco, con ID stabili e stato originale distinto da qualsiasi fatto.
  Titoli/condizioni non strutturati restano testo completo, senza euristiche legali.
- Riutilizzata la proiezione `document_blocks` dalla mappa V1, eliminando la
  vecchia implementazione locale. Stesso contratto verificato: nessun reviewer
  bypassato. Il parser ammette `require_candidates=False` per ispezionare anche
  moduli con sole checkbox; default, sicurezza e insieme scrivibile invariati.
- Nuova CLI esplicita `export_compilation_catalog.py`, senza provider/DB/retrieval,
  output in una directory nuova. Originali verificati invariati. Catanzaro:
  **279 testuali + 28 checkbox**, JSON **124.175 caratteri**, contro 418.910 dei
  contesti FORM ripetuti di tutti i candidate V1. Minervino: **254 + 13**,
  **67.594** contro 1.018.482. Non sono token né risparmi di latenza AI;
  il confronto non rappresenta il payload di una singola richiesta V1.
- Report: [catalogo e limiti](docs/catalogo-compilazione.md); misure versionabili
  in `docs/benchmarks/2026-10-10-compilation-catalog.json`; grezzi/log permanenti
  in `backend/data/compilation-audit/catalog-20261010/`, esclusi da Git.
- Verifiche effettivamente eseguite sulla versione finale: **32 test mirati**
  catalogo/mappa, **1.428 test backend completi**, Ruff completo, `--help` CLI,
  esportazione delle due fixture, integrità dei riferimenti/ID e originali,
  diff/whitespace. Suite con provider simulati e DB/storage temporanei; le
  esportazioni sono prove strutturali senza AI. Nessun nuovo benchmark semantico
  o misura DeepSeek. Frontend non toccato, quindi non rieseguito.
- **Limite attuale**: nessun nuovo resolver globale o adapter di sessione attivo,
  nessuna chiamata AI ancora eliminata dalla chat. Checkbox catalogate ma non
  scritte (`checkbox_write_supported=false`). RAG/SOURCE, chat, sessioni persistite
  e renderer invariati. Nessuna migrazione/reindicizzazione o modifica dei dati
  locali; preservate le modifiche documentali preesistenti. Nessun commit/push.
- Prossimo punto: contratto della proposta globale e validazione di applicabilità,
  soggetto/ruolo e prove SOURCE/USER; poi scrittura mirata checkbox, adapter della
  sessione e confronto reale congelato prima della rimozione della catena V1.

## Brainstorming catalogo compatto e checkbox — 10 ottobre 2026

L'utente propone di ridurre chiamate/token, concentrare il JSON sui candidate e
includere le checkbox nel nuovo motore. Registrata la discussione in
[strategia bottom-up](docs/strategia-bottom-up-compilazione.md#brainstorming-catalogo-compatto-e-checkbox--10-ottobre-2026):
candidate tipizzati con contesti condivisi, senza XML/formattazione ripetuti;
istruzioni, condizioni e provenienza restano necessarie. Dettagli **da discutere**.
Lettura effettiva delle fixture: 28 checkbox Word legacy nel modulo Catanzaro,
13 content control nel modulo Minervino; oggi sono preservate, non compilate.
Verificato nel codice/test, senza eseguire suite né provider. Solo documentazione,
controllo diff/whitespace; nessuna modifica applicativa, dati, commit o push.
Git iniziale pulito su `prune-backend`, HEAD `b271335`, già pubblicato con il tag
baseline. Prossimo punto: definire il contratto minimo comune testo/checkbox e
le fixture positive/negative prima di implementare o collegare il nuovo resolver.

## Checkpoint GitHub prima del nuovo motore — 10 ottobre 2026

Richiesta esplicita dell'utente: salvare prima tutto il lavoro corrente su GitHub
e partire dal sistema parzialmente funzionante, poi procedere gradualmente.
Questa autorizzazione supera i precedenti divieti di commit/push per il solo
checkpoint. Branch `prune-backend`, tag **`baseline-pre-one-call-20261010`**;
il commit che contiene questa sezione è il nuovo riferimento della demo.

- Inclusi layout/scroll e separatori chat, allineamento azioni dei moduli,
  regressioni UI, runner diagnostico, report, dati JSON dei benchmark,
  strategia proposta e markdown di ripresa. Conservate tutte le modifiche locali.
- Incluso un bundle versionato dei soli benchmark isolati Gemma/DeepSeek:
  `docs/benchmarks/2026-10-10-latency-audit.tar.gz`, con checksum e manifest
  interni verificati. Prompt/schema acquisiti, risposte, evidenze, stati e tempi
  saranno disponibili anche dopo un clone. Nessuna credenziale o database.
  Le acquisizioni storiche delle sessioni utente, i dati applicativi e le chiavi
  restano locali/esclusi da Git; non sono pubblicati dal checkpoint.
- Verifiche **rieseguite per questo checkpoint**: **98 test frontend**,
  lint/build, **10 E2E desktop/mobile** document-mentions/compilation-chat/
  project-forms, **104 test backend** sessioni/retry/stabilità e Ruff completo.
  Test software con provider/API simulati e dati temporanei, non nuove misure
  semantiche. Controllati diff/whitespace, bundle e contenuti prima del commit.
  Non rieseguita l'intera suite backend; nessuna nuova chiamata AI reale.
- Esiti strutturati in `docs/benchmarks/2026-10-10-checkpoint-checks.json`;
  log locali in `backend/data/compilation-audit/checkpoint-20261010-pre-one-call/`.
- Il resolver rimane V1: nuovo motore a chiamata unica **non implementato**,
  nessuna migrazione, reindicizzazione o modifica dei dati locali. La direzione
  globale è confermata; prima del prossimo codice esplicitare le scelte concrete.
  Prossimo punto: recuperare/valutare l'eventuale prototipo non pubblicato e
  definire contratto/validator/test della prima milestone in isolamento.

## Spiegazione del percorso attuale — 10 ottobre 2026

Ricostruito il flusso chat → sessione → mappa/review → batch → SOURCE/review →
checkpoint → USER → export in
[docs/flusso-compilazione-attuale.md](docs/flusso-compilazione-attuale.md).
Il sistema supporta già iterazione, persistenza e raggruppamento; i limiti sono
costi/decisioni distribuite e dominio centrato sulle posizioni candidate, con
dialogo ricavato dagli esiti dei batch. Sono presenti riuso/propagazione,
senza un unico catalogo globale dei fatti. PENDING non significa dato assente
o domanda obbligatoria. Continuazione dei passi pilotata dal frontend, stato DB.
Sola lettura del codice e documentazione; nessuna nuova prova AI, suite, modifica
applicativa o dati. Diff/whitespace controllati. Nessun commit/push.

## Proposta operativa bottom-up — 10 ottobre 2026

Su richiesta dell'utente, descritta la strategia in
[docs/strategia-bottom-up-compilazione.md](docs/strategia-bottom-up-compilazione.md).
**Da discutere**, nessun nuovo motore o contratto implementato: partire dalle
scritture ammesse e dai test; catalogo compatto FORM/prove/fatti/assegnazioni;
una proposta globale validata localmente; riuso di sessione, chat e renderer;
potatura del resolver/reviewer precedente solo dopo confronto reale verificato.
Il matching letterale non sostituisce il controllo di soggetto/ruolo/condizione;
una sola chiamata non garantisce velocità né correttezza. Recuperare il prototipo
non pubblicato prima di duplicarlo. Benchmark e test software restano distinti,
con export XML, casi negativi e coverage esplicita fra i criteri di accettazione.
Sola documentazione: `git diff --check` e whitespace dei file nuovi controllati;
nessuna suite, chiamata AI, modifica dati, commit o push in questo passaggio.

## Chiarimento sulla direzione di pruning già scelta — 10 ottobre 2026

Ricontrollati `RIPRESA-MAPI.md`, lo storico di questo file e `baseline-demo.md`.
La direzione era già autorizzata: sviluppo isolato bottom-up di una
rappresentazione completa/compatta FORM/SOURCE/USER, una chiamata, controlli
locali ed export, senza nuova orchestrazione per gruppi o reviewer AI separati.
La V1 resta la demo di riferimento. Il contratto preciso di fatti/condizioni/
evidenze rimane da discutere, non la direzione generale da decidere da zero.
Le proposte della recente diagnosi di latenza descrivono costi della V1:
non sostituiscono il percorso scelto con un nuovo piano di ottimizzazione V1.
Il markdown segnala un prototipo non committato in `Tesi-one-shot` sul PC di
origine; questo clone contiene soltanto la worktree `tesi` e non quel prototipo.
Per riprenderlo servono i file/diff originali, preservando la demo e i dati.
Nessuna modifica applicativa, test, commit o push per questo chiarimento.

## Confronto reale DeepSeek e conservazione benchmark — 10 ottobre 2026

- Richiesta corrente: provare DeepSeek e salvare stabilmente tutti i dati
  prodotti da benchmark/diagnosi. Aggiunta questa regola di continuità in
  AGENTS.md. Nessuna modifica al motore, ai prompt/schema applicativi, ai
  validator, alle impostazioni AI o alle sessioni locali.
- Nuovo benchmark **reale deepseek-flash**, stesso progetto/form 153/originale
  e KB della prova Gemma, profilo DeepSeek letto da `prova` soltanto nel
  processo diagnostico. Backup SQLite/storage/Qdrant temporanei, nessun USER.
  Mappa/review **117,61 s**, primi 12 candidate **33,56 s**, totale **151,25 s**.
  Cinque campi tutti RESOLVED/SOURCE alla prima ricerca: operatore economico,
  forma giuridica, sede legale, CF e PIVA. Zero errori per questi cinque,
  chunk Company KB `-43`/`-30` ammessi nei rispettivi bucket. Restano 267 PENDING,
  cinque MISSING, una AMBIGUOUS e una NOT_APPLICABLE; nessun READY o DOCX.
- DeepSeek emette il binding `semantic` per tutti e 12 i candidate, senza
  rifiuti di interpretazione. Sette chiamate generative totali, 141,14 s;
  solo mappa/review producono 24.762 token di ragionamento con thinking attivo.
  Cambiare modello permette qui di avanzare ma non elimina l'attesa iniziale.
  Un solo campione, cache prompt attiva: non è una graduatoria generale di velocità.
- Nuovo runner diagnostico bounded e riutilizzabile:
  `backend/scripts/benchmark_compilation_latency.py`. Delega a provider/service
  veri, default sei passi/420 s, stop dopo i target risolti. Non è un E2E browser
  né una prova di completamento del modulo; non genera bozze incomplete.
- Salvati i grezzi DeepSeek, recuperati quelli Gemma da `/tmp` e salvate in
  sola lettura anche le due sessioni storiche. Percorsi permanenti, contenuti,
  archivio trasportabile e comando di ripetizione in
  [docs/benchmarks/README.md](docs/benchmarks/README.md).
  [Report aggiornato](docs/diagnosi-latenza-compilazione-2026-10-10.md) e
  [JSON delle misure](docs/benchmarks/2026-10-10-compilation-latency.json)
  versionabili. I grezzi in `backend/data/` sono esclusi da Git: serve backup
  separato; non affidarsi al solo push. Nessuna credenziale esportata. Per
  Gemma i prompt non erano acquisiti; il limite è documentato.
- Verifiche di questa ripresa: esecuzione reale del runner, Ruff completo
  backend, `--help` del runner, controllo manifest SHA-256, originale invariato,
  sessione assente dal DB live, source_evidence ammesse e scan credenziali.
  `git diff --check` passato. Nessuna suite software/frontend ripetuta: gli
  esiti riportati sotto sono precedenti, non misure appena rieseguite.
- Preservate tutte le modifiche UI/locali. Nessun commit/push. Riprendere la
  direzione bottom-up/una chiamata già scelta nello storico. Contratto preciso
  e criteri di valutazione restano da discutere; le tracce V1 ne sono la baseline.

## Diagnosi reale della lentezza e icone allineate — 10 ottobre 2026

- Su richiesta dell'utente, misurata la compilazione prima di avviare un pruning
  del backend. Nessuna modifica al motore, ai prompt, alle impostazioni o alle
  sessioni locali. Report: [diagnosi dei tempi](docs/diagnosi-latenza-compilazione-2026-10-10.md).
- Prova reale Gemma `gemma4:e2b`, configurazione corrente (contesto 131072,
  Qdrant/BGE-M3), backup SQLite/storage/indice temporanei: creazione 0,48 s;
  mappa completa + review **100,32 s**; primi 12 candidate **16,03 s**, tutti
  respinti perché il modello omette `semantic`. La proprietà è opzionale nello
  schema ma necessaria per i candidate data: il parsing passa, il guard del
  dominio li scarta. SOURCE non parte e i campi restano PENDING. Circa il 98%
  del tempo dei due passi è nelle tre chiamate AI. Nessun dato USER o export.
- Prove I/O separate: parser 0,093 s, lettura sessione 0,111 s (JSON circa
  1,16 MB), FTS5 0,006 s, Qdrant prima ricerca 6,624 s e ripetizione 0,128 s;
  quattro evidenze SOURCE per ricerca. Non sono percentili né confronti di
  qualità semantica, e queste ricerche non appartengono al batch respinto.
- Lettura storica delle revisioni locali: Gemma circa **374 s** per 22 passi,
  zero RESOLVED, con un successivo claim senza completamento e lease scaduto
  (API paused=true). DeepSeek circa **812 s** per 52 passi su due cicli: i cinque
  campi societari restano RESOLVED/SOURCE. Lo status GENERATED di quest'ultima
  sessione riguarda una bozza incompleta, non un modulo interamente risolto.
- Osservazioni diagnostiche sulla V1, non implementate: schema di interpretazione
  coerente con il dominio, riuso della mappa verificata dello stesso originale/hash,
  meno passaggi/payload duplicati e tempi/rifiuti per fase. Non alleggerire i
  guard FORM/SOURCE/USER per recuperare velocità. Il contesto ampio non è stato
  dimostrato come causa principale; non modificato.
- Correzione UI richiesta durante la diagnosi: cestino dei moduli allineato a
  quello delle fonti tramite lo stesso spazio riservato nella colonna azioni;
  SVG, dimensioni e stile hover/focus restano condivisi.
- Verifiche appena eseguite: **104 test backend** sessioni/retry/stabilità
  passati con provider simulati; Ruff completo backend, lint/build frontend e **2 E2E project-forms**
  desktop/mobile con API simulate passati. Misure reali separate dai test
  software. `git diff --check` passato. Artefatti trasferiti successivamente
  nell'archivio permanente indicato nella sezione di confronto DeepSeek.
  Nessun commit o push; preservate le altre modifiche locali. Prossimo punto:
  riprendere il percorso bottom-up già scelto e usare queste misure come baseline.

## Chat: separatori coerenti e scroll nella viewport — 10 ottobre 2026

- Corretta la separazione dei messaggi: la risposta aveva un bordo superiore
  immediatamente sotto la bolla utente, oltre al separatore fra turni. Tolto il
  bordo interno, mantenuti un solo divisore fra scambi e spazi di 24 px coerenti;
  il pannello evidenze conserva la propria separazione.
- Rimossa l'altezza minima di 620 px della conversazione e il calcolo fisso che,
  sommato ai margini del workspace, superava la viewport. La sola shell della
  conversazione occupa `100dvh`, con cronologia e documenti a scroll indipendente;
  il composer rimane visibile. Il workspace iniziale e le altre pagine conservano
  il layout precedente. Su schermi fino a 1100 px il pannello documenti si apre
  dal controllo «Documenti», senza allungare la pagina.
- Esteso l'E2E document-mentions con verifiche comportamentali: conversazione
  breve senza scroll superfluo, storico e documenti lunghi, apertura/chiusura
  del contesto su mobile, composer raggiungibile e `window.scrollY=0`, anche a
  700 px di altezza. Verificati screenshot desktop/mobile.
- Verifiche effettivamente eseguite: **98 test frontend**, lint e build passati;
  **8 E2E** document-mentions/compilation-chat desktop/mobile passati, quindi
  ripetuti e passati i **2 E2E document-mentions** dopo l'aggiunta delle verifiche
  di scroll. API simulate negli E2E; nessun dato locale, provider reale, parser,
  renderer, RAG o workflow backend modificato. `git diff --check` passato.
- Nessuna migrazione/reindicizzazione, commit o push. Preservati il precedente
  aggiornamento locale di questo file e `RIPRESA-MAPI.md` non tracciato.
  Prossimo punto: diagnosticare l'attesa reale segnalata su «Certo. Analizzo il
  modulo… / Sto lavorando…», controllando avanzamento e tempi della compilazione;
  questo intervento UI non dimostra né corregge un eventuale blocco del modello.

## Ripresa su questo PC e accesso GitHub — 10 ottobre 2026

- Letto `RIPRESA-MAPI.md`, preservato come file locale non tracciato. Recuperati
  i commit pubblicati: `main` aggiornato in fast-forward a `b8071d3`, poi aperto
  `prune-backend` a `26976fa`, allineato a `origin/prune-backend`.
- `origin` usa ora `https://github.com/MontesanoDev/Tesi.git`. Riutilizzato il
  Git Credential Manager di Windows già configurato: credenziale esistente
  verificata tramite API GitHub, account MontesanoDev e permesso push=true.
  `git push --dry-run origin prune-backend` con interazione disabilitata termina
  con «Everything up-to-date», senza password e senza inviare modifiche.
  Rinnovo login annullato perché la credenziale conservata è già valida.
  Nessun token riportato o salvato nei file del progetto; chiavi SSH intatte.
- Confermato nel codice recuperato: selettore documentale ancora singolo;
  contratti multipli e correzione scroll descritti nel markdown non sono stati
  pubblicati sul branch remoto e non sono stati ricostruiti in questa ripresa.
- Nessuna suite applicativa o benchmark AI rieseguiti per il recupero Git;
  nessun avvio dei servizi, migrazione locale, commit o push. Prossimo punto:
  riprendere selezione multipla/scroll dal markdown, preservando il routing
  TurnPlan e la UI conversazionale già consolidati nel branch recuperato.

Aggiornato il **10 ottobre 2026**. Base precedente agli interventi: branch `main`, commit
`dcb9557` (`fix: stabilize table autofill and DOCX finalization`).
Ricontrollare Git all'inizio della prossima sessione.

## Consolidamento prima della selezione multipla — 10 ottobre 2026

L'utente ha chiesto di creare prima i commit da pushare. Consolidati in un nuovo
commit locale il selettore @ per fonti/moduli, le regressioni, la documentazione
e l'aumento del font già verificati nelle sezioni seguenti. Nessuna suite
rieseguita per il solo commit; ricontrollato il diff. Nessun push dell'agente.
Autorizzato il passo successivo: selezione multipla dei documenti, consultazione
e compilazione di un modulo con fonti di riferimento. Nessun nuovo comando
«Analizza bando» o «Report»; eventuali scorciatoie restano da valutare.

## Font della chat aumentato di 1 px — 10 ottobre 2026

Su richiesta dell'utente aumentati di 1 px risposte RAG/compilazione (13→14),
messaggi utente (14→15), titolo della risposta (15→16) e campo di scrittura
(16→17) in `App.css`. Allineata la copia sperimentale; build frontend e
`git diff --check` passati. Nessun nuovo test, commit o push.

## Consolidamento locale e selettore @ per documenti — 10 ottobre 2026

Richiesta autorizzata dall'utente: «ok fai 1 e 2 ora». Consolidare le correzioni
già verificate e implementare il selettore unico per fonti/bandi e moduli.
Questa sezione supera la proposta ancora da discutere riportata nello storico.

- Creato il commit locale **`b543fd7`** su `prune-backend`: correzione del thinking
  con modello ereditato e rimozione del download originale dalla lista moduli,
  con test e documentazione già verificati. Branch avanti di un commit rispetto
  a `origin/prune-backend`; nessun push e nessuna modifica alla configurazione Git.
  I precedenti checkpoint e il tag `demo-baseline-20261010` restano conservati.
- Implementato un solo menu **@ / +**, con gruppi **Moduli da compilare** e
  **Bandi e fonti**. Include i documenti del progetto, un riferimento alla volta;
  funziona anche nei progetti con sole fonti. Selezione, riferimenti nei messaggi
  e storico sono conservati dopo la ricarica. Le KB globali non sono nel menu.
- Contratto canonico `document_id` / `document_reference={document_id,name,role}`;
  `form_id` e i riferimenti FORM precedenti restano compatibili. Il backend
  verifica appartenenza al progetto e ruolo prima della chat. Riferimenti
  incompatibili vengono rifiutati, senza creare conversazioni o chiamare AI.
- Riutilizzato il planner semantico unico, senza nuove keyword o classificatori.
  Consultare un documento non avvia una compilazione. La sessione aperta è
  indipendente dalla selezione: cambiare documento o interrogarlo conserva campi,
  revisioni, domanda e budget. Non è introdotta una coda per più compilazioni.
- Una fonte selezionata vincola FTS5, Qdrant, vicini e rilettura delle evidenze
  allo stesso documento, escludendo altri file, altri progetti e KB globali.
  Restano distinti richieste FORM e fatti SOURCE. Nessun ruolo dedotto dai nomi.
- Compilazione consentita soltanto per originali FORM DOCX supportati. Chiedere
  di compilare una fonte/PDF o un TXT produce indicazioni nella chat, senza
  avviare un modulo alternativo. Anche un DOCX senza celle/segnaposti supportati
  riceve una risposta leggibile senza creare una sessione invalida.
- Migrazione additiva automatica: `conversations.selected_document_id` e
  `conversation_turns.document_reference_json`. I vecchi riferimenti sono
  convertiti in lettura, senza riscrivere lo storico. Backend locale riavviato;
  confermate entrambe le colonne e zero violazioni FK con SQLite in sola lettura.
  Nessuna reindicizzazione. Backend e frontend rispondono HTTP 200.
- Verifiche backend a blocchi: **135** test chat/retrieval/routing, **199** test
  vettoriale/provider/settings/generation, **30** nuove regressioni delle mention
  con FTS5 e Qdrant locale, PDF reale e database/storage temporanei. Nel blocco
  più ampio (394 casi raccolti) **390 passati**, poi interruzione manuale dopo
  circa 7 minuti con pressione di memoria e servizi locali non più disponibili;
  non è una suite completata in quel processo. Ripetuto separatamente tutto
  `compilation_active_question`: **47 passati**, inclusi i casi rimasti. Ultimo
  controllo dopo le modifiche finali: **70 passati** (mention/chat/routing).
  Ruff backend completo passato.
- Frontend: **98 test**, lint e build passati; **8 E2E desktop/mobile** con API
  simulate passati (nuovo selettore, ricarica, consultazione durante una domanda
  aperta, guard compilazione, tastiera, storico, lease e movimento ridotto).
  `git diff --check` passato. Queste sono verifiche software con provider
  simulati, non benchmark della qualità semantica del modello reale; nessuna
  nuova chiamata AI a pagamento eseguita in questo intervento.
- Aggiornati README, mappa e guida V1. Modifiche condivise allineate anche in
  `Tesi-one-shot` tramite patch, preservando il prototipo; verifiche eseguite
  nella worktree principale. **La nuova funzione @ resta nel working tree,
  non committata; nessun push.** Prossimo punto: prova manuale del percorso
  bando → consultazione → modulo → compilazione; architettura del motore e
  valutazione delle risposte reali restano interventi separati.

## Thinking disponibile anche con «Usa predefinito» — 10 ottobre 2026

- Corretto il vincolo segnalato dall'utente: lo switch DeepSeek è abilitato
  anche quando il progetto eredita il modello predefinito. Il salvataggio usa
  `profile_id=null`, senza fissare implicitamente il modello corrente.
- Il backend conserva il thinking per progetto quando si sceglie un altro
  modello o si torna al predefinito. Un successivo cambio del predefinito
  generale viene seguito normalmente; le preferenze degli altri progetti
  restano indipendenti. Il thinking è inizialmente disattivato.
- `project_ai_settings.profile_id` ammette ora NULL. Migrazione automatica
  transazionale all'avvio, preservando profili, preferenze e vincoli FK;
  supportati i database precedenti con o senza `thinking_mode`. La migrazione
  è già avvenuta nel backend locale con reload; successivo controllo SQLite
  in sola lettura: colonna nullable, zero violazioni FK. Nessun bisogno di
  reindicizzare e nessuna preferenza utente impostata dalle prove.
- Lo switch resta disponibile per DeepSeek; con un altro provider la preferenza
  è conservata e l'interfaccia non indica erroneamente «ragionamento attivo».
  Questo secondo difetto è emerso nel primo E2E ed è stato corretto. L'ambito
  delle chiamate che usano il thinking resta quello precedente: risposta finale
  RAG; nessuna estensione al planner o alle fasi della compilazione.
- Verifiche eseguite: **164 test backend** (`ai_settings`, `ai_providers`,
  `generation`), **96 test frontend**, Ruff completo, lint e build frontend,
  `git diff --check`; **2 E2E desktop/mobile** con API simulate passati dopo
  la correzione dell'etichetta. Dopo l'ultimo ritocco UI ripetuti i **17 test**
  di `AiSettings`, lint e build. Le prove usano database temporanei e provider
  simulati; nessuna chiamata AI a pagamento.
- Aggiornato README e allineati gli stessi cambiamenti in `Tesi-one-shot`,
  preservando prototipo e modifiche pendenti. Nessun commit o push; conservata
  anche la precedente rimozione del download originale dalla lista moduli.

## Download originale rimosso dalla lista moduli — 10 ottobre 2026

- Su richiesta dell'utente, rimosso il pulsante «Scarica originale» da
  `ProjectFormsPanel`, insieme al relativo handler e all'import dell'icona.
  Upload e rimozione restano nella lista; la bozza compilata si scarica dalla
  risposta di Mapi. Originali e API di download sono conservati.
- Aggiornato l'E2E esistente `project-forms`: verifica la lista dopo ricarica,
  l'assenza del pulsante e i percorsi di upload/rimozione con errori parziali.
- Verifiche eseguite: lint e build frontend, **2 E2E desktop/mobile** con API
  simulate, `git diff --check`. Il primo avvio Chromium senza librerie locali
  falliva per `libnspr4.so`; ripetuto con `LD_LIBRARY_PATH` verso
  `.tools/playwright-libs/usr/lib/x86_64-linux-gnu`, entrambi gli E2E passati.
- Allineati componente e scenario anche in `Tesi-one-shot`. Modifiche locali
  non committate; nessun push, modifica backend o migrazione.

## Commit locali e proposta di estensione di @ — 10 ottobre 2026

- L'utente ha autorizzato i commit delle modifiche già verificate; il push sarà
  eseguito dall'utente. Branch della worktree principale: `prune-backend`.
  Primo commit: `f677aff`, integrazione della compilazione nelle risposte di Mapi
  e permanenza dello storico. Il commit successivo consolida routing unificato,
  relative regressioni e documentazione. Nessun push eseguito dall'agente.
  Usata per i commit l'identità Codex già presente nei due commit precedenti,
  tramite opzioni temporanee; configurazione Git non modificata.
- Revisione finale del diff e `git diff --check` eseguiti prima dei commit.
  Le verifiche software e le valutazioni reali restano quelle documentate nelle
  sezioni seguenti; nessuna nuova suite ripetuta per il solo consolidamento.
- Nuova richiesta/preferenza: poter selezionare con `@` anche il bando PDF
  (`spiegami @avviso.pdf`), mantenendo distinta la consultazione dalla compilazione.
  Per ora va bene lavorare su un modulo alla volta; in futuro è desiderata la
  compilazione di più bandi/moduli. **Estensione non ancora implementata.**
- Verificato nel codice: il menu filtra `project.files` su `kind=form`; le fonti
  PDF sono escluse. La richiesta chat e lo storico espongono solo `form_id` /
  `form_reference`; il retrieval vincola già il modulo, ma non offre lo stesso
  filtro esplicito per una fonte menzionata. Le sessioni richiedono un originale
  registrato come form e in formato DOCX.
- **Proposta da discutere:** unico menu @ per fonti e moduli del progetto,
  riusando archivi e ruoli attuali. Riferimento al documento selezionato validato
  nel backend, distinto dalla sessione di compilazione attiva. Per domande sul
  documento, filtro coerente FTS5/Qdrant/espansione vicini/rilettura delle evidenze.
  L'intenzione è scelta dal modello; il backend autorizza la compilazione in base
  a ruolo e capacità supportate, mai in base al nome «avviso». Se è un bando di
  sola lettura, si può consultare e scegliere il modulo adatto da compilare.
  Il bando descrive requisiti, non dimostra che l'azienda li possieda.
- **Evoluzione proposta, non avviata:** prima un riferimento per messaggio e un
  modulo attivo alla volta, conservando la sessione se si interroga il bando;
  poi eventuale coda con sessioni separate e isolamento fra progetti/bandi.
  Unificare anche gli archivi/upload è un'alternativa più ampia, con maggiore
  impatto e possibili migrazioni, non necessaria per unificare il selettore.

## Routing semantico unificato — 10 ottobre 2026

Richiesta corrente: unificare il routing della chat e della compilazione, senza
nuove liste di frasi o una seconda chiamata classificatrice.

- `intents.py` espone al modello un solo `TurnPlan`, con prompt, schema JSON e
  contesto comuni per chat normale, domanda singola, gruppo e sessione sospesa.
  Rimossi `ChatRoute`, `ActiveQuestionPlan`, `ClarificationGroupPlan` e relativi
  prompt/retry separati. Le decisioni sono tradotte nei tipi interni esistenti:
  persistenza, revisione e validatori del dominio rimangono condivisi.
- Intenzioni esplicite: reply/explain/retrieve/compile/answer_fields/pause/
  resume/finish/generate. Solo answer_fields può contenere risposte ai campi;
  spiegazioni e comandi con valori vengono rifiutati. Senza slot attivi non si
  può rispondere a un campo. Nessun ID di campo/sessione/versione è esposto al
  modello. Gli slot mantengono la posizione anche quando ne resta soltanto uno.
- Le spiegazioni non modificano stato, revisione o budget. «Non so, prima
  spiegami» mantiene aperta la domanda; «no, fermiamoci» non applica una negazione.
  Spiegare durante una pausa non riprende la sessione. I guard letterali
  preesistenti sui controlli restano invariati; nessuna nuova keyword introdotta.
  Percorso normale: una chiamata di pianificazione, massimo un retry strutturale.
- Aggiornate le fixture dei provider al contratto unico, senza parser di
  compatibilità in produzione. Nuove regressioni in `test_unified_routing.py`:
  stesso schema/prompt in ogni stato, confini fra spiegazione/comandi/dati,
  assenza di target attivo, binding singolo/gruppo, risposte miste, pausa/ripresa
  e conservazione della posizione. Allineata un'asserzione di export al testo
  della UI già modificato nel precedente intervento.
- Verifiche software: **552 test backend distinti passati in blocchi**, inclusi
  dialogo, chiarimenti, controlli, stabilità, finalizzazione, routing RAG,
  FORM/SOURCE/mixed, API e trasporto dei provider. Ultimo controllo dopo il prompt
  finale: **102 test** (unified_routing, active_question, chat_flow). Ruff completo
  e `git diff --check` passati. Nella worktree sperimentale passati anche **51
  test** (routing unificato e prototipo whole_document). Frontend invariato: non
  rieseguiti test/build/E2E. Health backend e proxy frontend verificati.
- Valutazione reale separata, DeepSeek Flash configurato, senza applicare le
  decisioni alle sessioni reali: primo confronto **16/16 prima e 16/16 dopo**, una
  chiamata per caso, senza guard letterali. Quindi non è dimostrato un aumento
  dell'accuratezza di routing rispetto al prompt già corretto nell'intervento
  precedente: il beneficio verificato è la coerenza del contratto e dei vincoli.
  Nel controllo delle spiegazioni una parafrasi aggiungeva un'equivalenza fra
  categorie non documentata: rafforzato il vincolo di mantenere letterali ruoli
  e categorie e usare retrieval per definizioni/differenze normative.
- Prova finale ampliata: **20/20 intenzioni corrette**, 20 chiamate, nessun retry,
  **68.454 token**. Nei 16 casi confrontabili: 54.525 contro 48.981 token precedenti
  (**+11,3%**); lo schema nel prompt è ora serializzato compatto. Totale delle due
  prove reali: 52 chiamate e 173.259 token. Misura il routing su casi selezionati,
  non garantisce correttezza di ogni spiegazione o della compilazione completa.
  Report, snapshot precedente e script ripetibile nella worktree principale,
  locali ed esclusi da Git in
  `backend/data/compilation-audit/unified-routing-20261010/`:
  `paired-104700.json`, `paired-105030.json`, `before_intents.py`, `evaluate.py`.
  Lo script apre SQLite in sola lettura e ricostruisce il checkpoint Minervino 81.
- Modifiche condivise allineate anche in `Tesi-one-shot`, preservando prototipo e
  documentazione sperimentale. Nessun commit/push, migrazione o reindicizzazione.
  La base con tag resta intatta. Prossimo punto: valutare la qualità del motore
  di compilazione separatamente; ottimizzare ulteriormente il payload solo con
  confronto delle regressioni. Nessuna riscrittura del motore avviata qui.

## Storico della compilazione e richieste di spiegazione — 10 ottobre 2026

Segnalazioni dell'utente: domande/informazioni che scompaiono dopo un input o
una pausa; «spiegati meglio» trattato come risposta ambigua al modulo.

- Riprodotta la prima regressione: `CompilationReply` proiettava la domanda solo
  sull'ultimo turno, mentre lo storico conservava il semplice annuncio iniziale.
  Ora i paragrafi visualizzati sono conservati nella UI prima del nuovo invio.
  Al completamento automatico il backend salva la domanda nel turno di Mapi
  corrispondente, nella stessa transazione della sessione. Verificati permanenza
  dopo risposta/pausa/ricarica e disponibilità della domanda nella cronologia AI.
  Un turno conversazionale successivo o relativo ad altro modulo non viene
  sovrascritto da questa proiezione.
- Verificato il caso reale nel database in sola lettura: turno 61, Minervino,
  «spiegati meglio» associato alla sessione come `clarify`; il turno 60 conservava
  soltanto l'annuncio iniziale. Il planner a gruppi distingueva insufficientemente
  richieste di spiegazione e risposte ambigue agli slot.
- Chiarite le istruzioni dei percorsi generale, singolo e raggruppato: spiegare
  o riformulare la domanda usa `reply`/`CHAT/reply`, con domanda ed estratto FORM
  limitato a 1.500 caratteri per elemento. Non sono aggiunti riconoscimenti
  letterali di «spiegati meglio» né nuove chiamate nel normale percorso.
  Le regressioni verificano che spiegazione, campi, revisione e budget restino
  separati; domande documentali continuano a usare il retrieval.
- Verifiche eseguite: **202 test backend** (`compilation_conversation`,
  `compilation_clarifications`, `compilation_controls`, `chat_flow`), **95 test
  frontend**, Ruff sui quattro file Python modificati, lint e build frontend;
  **6 E2E desktop/mobile** di `compilation-chat` passati, inclusi storico,
  spiegazione, pausa e ricarica. Queste verifiche usano provider simulati.
- Prova reale separata con il DeepSeek configurato: **6/6 intenzioni riconosciute**
  (tre richieste di spiegazione, negazione, incertezza, pausa), **19.319 token**.
  Usato in memoria il checkpoint precedente al messaggio errato, ricostruito
  dalle revisioni; nessuna modifica della sessione reale da parte della prova.
  Report locale escluso da Git:
  `backend/data/compilation-audit/dialogue-20261010/results-101411.json`.
  Questo risultato misura il routing su sei casi, non garantisce accuratezza
  generale delle spiegazioni o qualità della compilazione completa.
- Modifiche applicative, test e guida allineati anche in `Tesi-one-shot`,
  preservandone il prototipo. Nessun commit/push o nuova migrazione. Le domande
  precedenti mai salvate nei turni non sono state ricostruite nello storico:
  nessun backfill dei dati reali. La base con tag resta intatta.

## Diagnosi dell’avviso «Non ho completato questa operazione» — 10 ottobre 2026

- L’avviso dello screenshot è il fallback del `catch` in
  `useCompilationSession.run`: non identifica la causa della richiesta fallita.
  Il motivo tecnico viene scritto nella console del browser; non è persistito
  dal frontend. Nessuna prova che si tratti di limiti o errori di DeepSeek.
- Ispezionato `backend/data/mapi.db` tramite SQLite in sola lettura. Le ultime
  due sessioni (Minervino e Catanzaro) hanno un ultimo `analyze_start`/
  `source_start` senza conclusione, stato `ANALYZING`, lease ormai scaduta e
  `last_error: null`. Risultano conservati i passaggi precedenti; Minervino non
  aveva ancora valori `SOURCE` risolti, Catanzaro ne aveva sei. Il testo generico
  «dati già verificati» non implica che esistano valori verificati nella sessione.
- All’inizio di questa diagnosi entrambe le porte 8000/5173 erano senza servizi
  in ascolto. Questi elementi sono compatibili con un arresto durante il lavoro,
  ma non dimostrano la causa esatta della richiesta nello screenshot: mancano
  i log di quell’istante e lo screenshot non identifica la sessione.
- Riavviati Uvicorn e Vite separatamente, con log locali esclusi da Git in
  `backend/data/runtime-logs/backend.log` e `frontend.log`. Verificate le risposte
  `{"status":"ok"}` sia direttamente sulla 8000 sia dal proxy sulla 5173.
  Nessuna compilazione, chiamata AI o ripresa automatica avviata dalla diagnosi.
- Il pulsante «Riprova» esegue una rilettura: una lease scaduta richiede poi
  una ripresa esplicita nella chat. Non modificati codice applicativo o sessioni;
  nessuna suite rieseguita. Restano da migliorare distinzione delle cause e
  chiarezza dell’azione proposta quando la sessione è interrotta.

## UI unica per RAG e compilazione — 10 ottobre 2026

Richiesta esplicita dell'utente: eliminare completamente il box della
compilazione e i dettagli tecnici; analisi, animazione, chiarimenti e documento
devono comparire come normali risposte di Mapi.

- Modificato il frontend effettivamente usato in `/home/montesano/Tesi`
  sulla porta 5173. La precedente modifica solo in `Tesi-one-shot` lasciava
  visibile la vecchia UI nella demo; il primo tentativo conservava inoltre
  un disclosure di dettagli che l'utente ha chiesto di eliminare.
- Rimosso `CompilationSessionCard`, insieme a conteggi, stato separato,
  dettagli/evidenze per candidato e controlli manuali della scheda.
  RAG e compilazione condividono `AssistantMessage`, stile e animazione.
  `CompilationReply` produce solo paragrafi e il download DOCX disponibile.
- L'annuncio iniziale lascia posto alla domanda corrente dopo l'analisi.
  Una spiegazione conversazionale non riaggiunge la vecchia domanda.
  Pausa, ripresa e generazione passano dalla chat già esistente.
  Restano visibili errori, natura parziale della bozza e copia non aggiornata.
- Adeguati pochi testi backend che rimandavano alla scheda eliminata e
  aggiornate README, guida e mappa. Le API mantengono evidenze, revisioni,
  report e operazioni manuali; motore e validazione invariati.
- Allineati gli stessi file in `Tesi-one-shot`, preservando prototipo e
  modifiche documentali sperimentali. Nessun commit o push; la base
  `1d7f868` resta recuperabile dal tag `demo-baseline-20261010`.

Verifiche concluse: **92 test frontend**, lint e build; **133 test backend**
(`compilation_chat`, `compilation_controls`, `compilation_clarifications`)
e Ruff sul modulo Python modificato. Dopo l'ultimo controllo di appartenenza
della risposta alla sessione, ripetuti anche i **25 test UI della compilazione**.
Rimossi i test dei comandi manuali eliminati; mantenute regressioni di chat,
isolamento, risposte ambigue, budget, ripristino, errori e download.
Tutti questi test usano provider simulati e dati temporanei.

Conclusi anche i **16 E2E desktop/mobile** sui quattro scenari con API
simulate (`composer-model-menu`, `compilation-chat`, `document-review`,
`project-forms`), inclusi chiarimenti, refresh, pausa/ripresa e generazione
richiesta nella chat. Esito finale: `16 passed`; report `.last-run.json` con
`status: passed`. Controllate le schermate desktop e mobile in
`frontend/artifacts/*-compilation-active.png` e `*-compilation-explanation.png`.
I tentativi precedenti hanno incontrato frontend non raggiungibile e forte
pressione di memoria; un run è stato interrotto dall'utente. La verifica finale
è completa. Eseguire le suite pesanti in sequenza su questa macchina.

Servizi della demo riavviati separatamente: Vite sulla **5173**, Uvicorn con
reload sulla **8000**. Verificato `/api/health` anche attraverso il proxy Vite:
`{"status":"ok"}`. Per vedere la UI aggiornata ricaricare la pagina. Non sono
state effettuate prove di compilazione sui dati reali; i normali inizializzatori
applicativi sono eseguiti dal riavvio del backend. Nessuna migrazione specifica
per questo intervento. Prima di rilanciare `start.sh`, fermare queste istanze
per evitare porte già occupate.
Nessuna nuova chiamata AI o reindicizzazione in questo intervento.
Non è implementato streaming dei token o un diario di turni automatici:
l'avanzamento resta una proiezione dello stato backend nella risposta corrente.
Il contratto compatto di fatti, condizioni ed evidenze resta da discutere.

## Nuova base della demo: UI e thinking opzionale — 10 ottobre 2026

L'utente ha provato RAG e compilazione in chat, apprezza in particolare il
chiarimento conversazionale «in che senso, spiegati meglio» e ha autorizzato
il consolidamento e il push di questa versione prima della semplificazione
architetturale. Questo riscontro manuale non è un benchmark completo della
qualità della compilazione.

Riferimento della nuova base: **`demo-baseline-20261010`**, branch
`prune-backend`, directory `/home/montesano/Tesi`; conserva anche il precedente
tag `demo-baseline-20261009`. Il prototipo one-shot e le sue modifiche non
committate restano nel worktree `/home/montesano/Tesi-one-shot`, senza essere
integrati nella demo. Prima del successivo sviluppo occorre allineare quel
worktree alla nuova base preservandone le modifiche pendenti.

Revisione delle modifiche UI/thinking della sezione seguente:

- Corretto il nuovo pulsante **+**: apre il picker senza cancellare il messaggio
  già scritto; selezione del modulo ed Escape conservano anche il testo
  selezionato nel composer. Aggiunta una regressione frontend.
- Thinking per progetto: verificati persistenza, disattivazione al ritorno al
  default, aggiornamento automatico dello schema precedente senza perdere
  profilo/chiave e compatibilità con gli altri provider. Verificati sul
  trasporto simulato flag, budget 8.192/16.384, timeout e retry per troncamento.
  Il toggle riguarda la generazione finale RAG; planner e passi di compilazione
  non ricevono il thinking. La spiegazione conversazionale mostrata dall'utente
  usa il routing già esistente.
- Allineati i selettori E2E alla nuova classe `compilation-message`; aggiunta
  verifica browser dello switch, senza inviare involontariamente la chat.

Verifiche **rieseguite in questo intervento**: **295 test backend mirati**
(`ai_settings`, `ai_providers`, `generation`, `api`, `chat_flow`, `model_parsing`),
**97 test frontend**, Ruff backend completo, lint e build frontend passati.
**16 E2E desktop/mobile** passati sui quattro scenari con API simulate
(`composer-model-menu`, `compilation-chat`, `document-review`, `project-forms`).
Usato un Vite separato sulla porta 5187 e le librerie Chromium locali tramite
`LD_LIBRARY_PATH`; il primo tentativo senza tali librerie non avviava il browser.
Nessuna nuova chiamata AI o prova sui dati applicativi reali; l'intera suite
backend non è stata ripetuta, resta documentata nel consolidamento del 9 ottobre.

La colonna `thinking_mode` si aggiunge automaticamente all'avvio del backend:
è una migrazione additiva, senza interventi manuali o reindicizzazione.
Git conserva il codice; i dati e le credenziali locali restano esclusi dal push.
Il backup privato del 9 ottobre resta la fotografia dei dati di quella data,
non include le conversazioni successive. Riferimenti in
[baseline-demo](docs/baseline-demo.md).

Prossimo intervento: discutere il contratto unico di fatti, condizioni ed
evidenze e i criteri di valutazione, mantenendo questa versione ripristinabile.
Nessuna ulteriore potatura o sostituzione del motore effettuata in questa revisione.

## UI chat: flusso compilazione, picker e modello+thinking — 9 ottobre 2026

Richiesta esplicita dell'utente, dopo la valutazione del lavoro one-shot:
sistemare la UI della demo in `/home/montesano/Tesi`. Al termine di questo
intervento le modifiche erano nel working tree su `prune-backend`, non committate;
il successivo consolidamento è descritto nella sezione del 10 ottobre.

- **Compilazione in chat**: rimosso il tasto **Avvia compilazione**; si parte
  scrivendo «me lo compili?». Il vecchio pannello è diventato un messaggio
  (`compilation-message`) che vive **dentro l'ultimo turno, prima della
  risposta**: la risposta è l'ultima cosa e resta leggibile. Restano domanda,
  azione principale, download e il disclosure "Dettagli compilazione".
- **Scroll**: ancoraggio solo se si è già vicini al fondo (soglia 140 px), i
  cambi di versione della sessione non trascinano più la vista, il testo
  digitato nel composer sopravvive all'invio in corso.
- **Picker documenti**: menu `@` trasformato in popover ancorato al composer
  (posizionamento assoluto, ombra, max-height 240, apertura verso l'alto) più
  un bottone **+** nella toolbar; chip invariato.
- **Modello + thinking**: il selettore mostra il nome del modello invece della
  sola rotella; lo **switch on/off stile iPhone** per il "Ragionamento
  approfondito", con etichetta **"thinking"**, sta **fuori dal menu, accanto al
  nome del modello** (verde quando attivo), disponibile per DeepSeek con
  profilo specifico selezionato. Default disattivato per ogni progetto.
  Backend: colonna additiva
  `project_ai_settings.thinking_mode`, campo `thinking` in
  `ProjectAiSelection`/PUT `/ai-model`, `AISettings.thinking` applicato solo
  alla risposta finale (thinking enabled, `reasoning_effort=low`, budget
  8.192/16.384 token, timeout 300 s e read esteso). Planner, estrazione fatti,
  bozze e fasi della sessione restano senza thinking.

Verifiche: **96 test frontend** passati con `vitest run --maxWorkers=1` (il run
parallelo ha prodotto timeout da 5 s per pressione di memoria della macchina,
non legati alle modifiche), lint e build frontend passati; Ruff backend
completo e **289 test mirati** passati (ai_settings, ai_providers, generation,
api, chat_flow, model_parsing). E2E non rieseguiti stasera;
`composer-model-menu.spec.ts` è stato aggiornato al nuovo body PUT. Serve il
riavvio del backend per la migrazione additiva automatica. Nessuna migrazione
manuale, reindicizzazione o modifica ai dati reali durante le verifiche.

Prossimo punto: prova manuale della UI (ordine risposta/compilazione, picker,
thinking reale su DeepSeek) e, se ok, commit del blocco. Restano non
implementati il flusso interamente testuale con avanzamento persistito dal
backend come turni e lo streaming delle risposte.

## Consolidamento della demo e nuovo punto di partenza — 9 ottobre 2026

L'utente ha autorizzato il consolidamento della versione attuale, recuperabile
e dimostrabile ai relatori, e il successivo sviluppo a chiamata unica in
isolamento. Il percorso scelto è bottom-up: rappresentazione completa e
compatta di FORM/SOURCE/USER, una chiamata, controlli locali ed export; nessuna
nuova orchestrazione per gruppi o revisori AI separati. Le proposte storiche
delle sezioni seguenti non sono istruzioni per riprendere quel percorso.

Riferimento della demo: `demo-baseline-20261009`, branch `prune-backend`,
directory `/home/montesano/Tesi`. Backup privato di codice e dati:
`/home/montesano/Tesi-snapshots/baseline-20261009T165627Z/`.
Il database è copiato con SQLite backup; integrità `ok`, 32 tabelle,
3.856 file nella copia dei dati, inclusi audit. Nessun push o modifica alla
configurazione Git. Procedura in [baseline-demo](docs/baseline-demo.md).

Riprodotti i due fallimenti noti in `test_compilation_stability.py` (FTS5/Qdrant)
prima della correzione. Risolto `StopIteration` in `chat_control`: la ripresa
riapre un campo rinviato solo se presente. Dopo la correzione **145 test**
stability/controls/finish passati. Completata l'intera suite backend in processi
separati (44 file): **1.332 test passati**, inclusi quei 145, senza fallimenti.
Frontend **94 test**, lint, build e Ruff backend passati. Avvio reale Uvicorn e
Vite su copie dei dati: health, pagina frontend e proxy API funzionanti;
accessibili 3 progetti, 3 moduli, 4 compilazioni e 9 sessioni. Nessuna chiamata
AI durante questi controlli. Log e risultati nel backup privato.

Le nuove implementazioni devono avvenire in `/home/montesano/Tesi-one-shot`,
branch `feat/compilation-one-shot`, dopo il congelamento. Nessuna migrazione,
reindicizzazione o prova AI sui dati reali effettuata nel consolidamento.

## Potatura backend, primo taglio — 9 ottobre 2026

Richiesta esplicita dell'utente: iniziare a potare il backend con risoluzione
bottom-up. Checkpoint locale su branch `prune-backend`, commit `2510418`
("chore: freeze pre-pruning working tree (compilation backend)"), nessun push,
config Git invariata. La potatura di questo intervento è nel working tree, **non
ancora committata**.

Rimossi (recuperabili dal commit di congelamento):
- prototipo globale: `app/global_compilation.py`,
  `scripts/global_compilation_experiment.py`, `tests/test_global_compilation.py`;
  il documento dell'esperimento resta come registrazione storica;
- vecchio motore DOCX a chiamata unica: `load_compilation_sources`,
  `build_prompt`, `request_field_proposals`, `compile_fields_once`,
  `compile_document` e prompt/trasporto in `document_compilation.py`; endpoint
  POST `/document-compilations`;
- script `compile_docx_demo.py`, `compile_docx_ollama.py`,
  `replay_docx_audit.py` e `tests/test_compilation_scripts.py`;
- metodi client morti in `api.ts` (`projectArtifacts`, `projectArtifact`,
  `updateProjectArtifact`, `generateDraft`, `documentCompilations`,
  `documentCompilation`, `compileDocument`, `projectEvidence`) e i tipi usati
  solo da essi.

Conservati: validatori condivisi (`StrictModel`, `CompilationSources`,
`validate_proposals` con controlli numerici/email/protetti), storico delle
compilazioni (elenco, dettaglio, download), `_persist` condiviso con la
finalizzazione delle sessioni, parser/writer DOCX, persistenza, provenienza e
guardie. `document_compilation_routes.py` è passato da quattro a tre operazioni.

Verifiche effettive: Ruff backend completo passato; frontend **94 test**, lint e
build passati. Backend eseguito **a blocchi** per il limite di memoria (3,7 GiB
totali): 127 ai_providers/ai_settings/artifact_storage/call_facts/chat_flow; 222
docx_compilation/tender_cases/validation/numeric/email/api/finalization; 348
compilation A; 203 retry/semantics/guards/sessions/sources/stability/table con
**2 fallimenti preesistenti**; 333 blocco finale; 66 form_retrieval; 41
retrieval/vector. `pytest -q` completo ucciso due volte per memoria (exit 137)
intorno al 64%: nessuna suite completa in un unico processo.

Fallimenti **non introdotti** da questo intervento (i file coinvolti non sono
toccati dalla potatura ed erano già nel congelamento):
`test_consecutive_model_errors_two_resumes_and_partial_export_preserve_source_user`
(fts5/qdrant) fallisce con `StopIteration` in `chat_control` alla ripresa di un
riepilogo senza rinvii. Solo la firma dello stub di
`test_internal_coverage_bug_is_not_recovered_as_model_output` è stata allineata a
`remembered=`. Da decidere se correggere il difetto o riportarlo all'altro
agente.

Prossimo punto: decidere la potatura successiva (nucleo semantico e percorsi
legacy delle sessioni) e se committare questo taglio. Nessuna migrazione,
reindicizzazione o modifica ai dati reali.

## Diagnosi Trapani Green: duplicati, rami e copertura SOURCE — 9 ottobre 2026

Richiesta corrente: capire le domande inadeguate/duplicate e valutare se rifare
il backend; prove DeepSeek esplicitamente autorizzate. Diagnosi conclusa,
**nessuna modifica al codice applicativo né nuova architettura implementata**.
Conservate tutte le modifiche pendenti; HEAD `b8071d3`, nessun commit/push.

- Caso corrente `81bc4d657ff44bdbac538c22d4b53ac5`, conversazione
  `conv-202292d12f3b4e94`, modulo Trapani 29, v59 WAITING_FOR_USER:
  115 candidate, 23 passi, 5 RESOLVED, 47 MISSING, 38 AMBIGUOUS, 25 PENDING.
  Il provider della sessione è già `deepseek-flash`.
- Duplicato riprodotto sul codice attuale: stessa condizione/sezione della
  tabella Studio Associato, 18 celle con `person_role=professionista associato`
  e 6 con ruolo vuoto. `owner()` usa il ruolo della cella per identificare la
  condizione, creando due slot dal testo identico. Uniformarlo solo in memoria
  produce un unico slot da 24 celle; è un controfattuale diagnostico, non una fix.
- Zero dipendenze FORM riconosciute: Trapani usa paragrafi non numerati sotto
  «IN QUALITA’ DI / eliminare le opzioni non pertinenti», mentre il riconoscitore
  richiede intestazioni numerate e «da compilare in caso di». Anche tutti gli
  `exclusive_group_id` sono vuoti. La tipologia SOURCE Società di Ingegneria è
  verificata, ma manca il collegamento fra le alternative. Firma/poteri e forma
  di partecipazione restano fatti distinti; non dedurli dalla tipologia.
- Revisione 46: DeepSeek aveva già proposto la via corretta dalla visura `-1`;
  rifiutata come SOURCE non ammessa per `p75.s1`, mentre la provincia `p75.s4`
  usa la stessa riga nello stesso passo. Via/comune/CAP hanno copertura
  `[91,-2,-5,90]`, insufficiente. Query con etichette underscore, budget quattro
  frammenti senza spazio per vicini quando saturo, riuso fra gruppi vincolato a
  intestazioni con `:`; la riga PDF non le ha. Il retry v48 non recupera la sede.
- **Quattro nuove chiamate DeepSeek riuscite**, stesso matcher/revisore/validatori
  su copie in memoria di via/comune/CAP: copertura salvata **0/3**, aggiungendo
  soltanto il frammento aziendale esistente `-1` **3/3 valori accettati**.
  Per la via, una seconda proposta errata (ragione sociale) è respinta e lascia
  un errore registrato. Nessun export o benchmark completo: non dichiarare tre
  campi completati end-to-end né correttezza generale. Primo tentativo sandbox
  fallito nel trasporto/interrotto; prova riuscita dopo escalation di rete.
- «Ancora 2 chiarimenti» conta il checkpoint, con **54 slot potenziali** dietro;
  non 54 domande tutte necessarie. «5 informazioni» conta posizioni: PEC ripetuta,
  quattro valori distinti. I 25 PENDING sono errori d'interpretazione, non dati
  tutti da chiedere. Le 30 celle esperienze non equivalgono a 30 fatti obbligatori.
- Raccomandazione **da discutere prima di implementare**: riorganizzare il nucleo
  semantico con mappa coerente sezioni/soggetti/condizioni, fatti riutilizzabili e
  domande sui soli fatti necessari; mantenere API, persistenza e writer. Una patch
  al duplicato copre soltanto il sintomo; nessuna evidenza per rifare tutto o per
  integrare automaticamente il prototipo globale già presente.
- Verifiche effettive: replay offline, quattro chiamate reali su tre campi,
  confronto identico prima/dopo di dieci tabelle applicative (incluse sessioni,
  revisioni, conversazioni, originali BLOB e chunk), controlli documentali/diff.
  Nessuna suite software rieseguita; nessuna migrazione/reindicizzazione.

Report e alternative:
[diagnosi Trapani Green](docs/diagnosi-trapani-green-2026-10-09.md).
Audit ignorato: `backend/data/compilation-audit/trapani-diagnosis-20261009/`,
con script, stato v59, revisioni, richieste/risposte parsate e preservazione.
Prossimo punto: concordare il perimetro del nucleo semantico e i criteri di qualità
sui tre moduli prima di implementare. La sessione reale è ancora alla v59;
la prova non ne ha corretto domande o dati.

## Applicabilità dei rami e collocazione SOURCE — 9 ottobre 2026

Richiesta conclusa localmente: diagnosi dell’ultima CompilationSession Catanzaro,
correzione mirata backend e nuova esportazione su copia. Nessuna chiamata AI,
nuovo prototipo, benchmark completo, modifica UI/retrieval/parser, commit o push.
Preservate le modifiche preesistenti; HEAD `b8071d3`, index Git vuoto.

- Ultima sessione reale `5c6666c952be4d0ba16af5994dd3d6a1`, revisione **154**,
  conversazione `conv-c3a56340e3cd4f79`: **279 candidate, 22 SOURCE**, zero esclusioni.
  È diversa dalla sessione con 23 SOURCE del pass precedente: nessun trasferimento
  automatico delle decisioni USER fra conversazioni.
- Causa: intestazioni condizionali in tabelle autonome, perse nel contesto delle
  tabelle interne dopo dodici paragrafi XML. Classificatore/revisore accettavano
  condizioni vuote; gate ed export verificavano il valore, senza richiedere la
  condizione del padre. Il riuso precedente non ricostruiva le alternative della
  famiglia identificativa; l’intestazione Società di Ingegneria, priva della formula
  «dati identificativi», non condivideva l’ambito riconosciuto per altri rami.
- Confermate nell’XML della bozza originale **otto collocazioni errate**: tre
  qualifiche/iscrizioni di Elisa Romano nello Studio Associato; quattro dati della
  stessa direttrice tecnica nelle tabelle dei soci di Società di Professionisti;
  il nome nel direttore tecnico di Altro soggetto abilitato. SOURCE reali, ramo
  sbagliato; non otto fatti aziendali inventati.
- Contatore **20→22**: il turno di incertezza del 9 ottobre alle 09:00:13 UTC
  («Non posso confermare questa condizione…», non letteralmente «non lo so»)
  lascia 20 SOURCE e rinvia il fatto. La prosecuzione automatica aggiunge
  `t25.r5.c0` alla revisione **138**, ore 09:03:07.691 UTC, e `t25.r5.c1` alla
  **141**, ore 09:03:31.748 UTC. Entrambe riportano la sede legale, provata da
  `generalita-mapi.md` chunk -6 e visura chunk -1, ma in una riga completamente
  vuota senza etichette. Dato reale, associazione alla proprietà non provata;
  la sede è già nella cella etichettata `t25.r4.c3`. Ora bloccate anche queste due.
- Vincoli FORM derivati dall’originale immutabile in
  `compilation_form_conditions.py`: attraversamento delle tabelle distanti,
  parentela fra sezioni e candidate, limiti della famiglia identificativa esplicita.
  Nessun nome aziendale, progetto o candidate ID nel codice. FORM dimostra la
  struttura delle alternative; SOURCE/USER dimostrano il fatto. Nessuna deduzione
  della tipologia professionale o della partecipazione dalla sola forma giuridica.
- Riuso delle decisioni verificate prima di analisi, domande, refresh ed export.
  Il diniego USER esplicito del genitore Studio Associato raggiunge i qualificatori;
  un «no» generico al sottoramo non nega il genitore. Condizioni dei rappresentanti,
  direttori e membri conservano soggetto/ruolo/ambito separati. Prove contraddittorie
  restano UNKNOWN e non vengono aggirate da una prova positiva locale. Protezione
  anche delle condizioni SOURCE dalla loro rimozione nella riinterpretazione LLM.
- Gate SOURCE e finalizzatore richiedono applicabilità positiva di padre e
  condizione locale. Citazione/revisione semantica positive non bastano. Celle in
  righe senza etichette non autorizzano copie di proprietà delle righe vicine.
  Partecipazione come **consorziata esecutrice resta UNKNOWN**: società di ingegneria
  può partecipare come consorziata. Escluso il ramo proprio Consorzio Stabile e
  le sue tabelle dipendenti, senza estendere l’esclusione alla partecipazione.
- **Tutti i 22 record SOURCE conservati**, con stato/valore/provenienza/evidenze e
  condizioni originali. Dieci scritture segnalate da `write_blockers`,
  `blocked_previous_writes`, `open_issues` e conteggi scrivibili/bloccati. Nessuna
  cancellazione silenziosa. Export ordinario impedito con problemi aperti;
  export parziale lascia vuote le collocazioni bloccate e le documenta nel report
  versione 6, senza dichiarare READY.
- Replay ed export finali sul codice installato, in SQLite/storage isolati:
  **147 NOT_APPLICABLE**, **22 SOURCE conservati**, **12 valori esportati**,
  **10 bloccati**, **110 candidate irrisolti**. Verificati nell’XML tutti i 22
  candidate: dodici valori mantenuti, dieci celle vuote. Conservati i cinque dati
  aziendali della prima tabella e i sette corretti della Società di Ingegneria /
  direttore tecnico. Report `needs_review`, `ready_for_submission=false`; nessuna
  domanda né auto-continuazione dopo il termine. Restano UNKNOWN partecipazione,
  poteri di rappresentanza non provati e proprietà delle due celle senza etichetta.
- Verifiche effettivamente eseguite: **499 test backend mirati passati** sulla
  copia del codice finale (form_conditions, condition_reuse, finish, clarifications,
  controls, active_question, stability, sessions, guards, semantics, finalization,
  conversation, compilation_chat, retry_phases, chat_flow). **78 test del sottoinsieme
  form_conditions/condition_reuse/sessions rieseguiti e passati nel repository**;
  sono un sottoinsieme, non 78 casi ulteriori. Ruff backend completo passato.
  Provider simulati e FTS5/Qdrant temporanei; replay dati congelati senza provider.
  Nessun test/build frontend aggiunto, perché la UI è rimasta identica.
- Audit ignorato:
  `backend/data/compilation-audit/branch-placement-20261009T091052Z/REPORT.md`,
  con snapshot, timeline revisioni, controlli SOURCE, confronto XML, nuova
  `bozza-verificata.docx` e `report-verificato.json`. Preservati tutti i **32 file
  originali**, sessioni, revisioni, generazioni, conversazioni, fonti globali e
  **106 chunk SOURCE/FORM di progetto**. Le dodici modifiche pendenti non toccate
  da questo intervento sono identiche. Il server `uvicorn --reload` preesistente
  ha rigenerato ID/timestamp di **tre chunk di artefatti derivati**, a contenuto
  invariato, e pagine FTS: dettaglio in `preservation.json`. Non si dichiara il
  database originale identico byte per byte.

Nessuna migrazione/reindicizzazione richiesta. Arricchimento delle sessioni
precedenti in sola lettura; persistenza soltanto alla successiva mutazione
ordinaria autorizzata. Riconoscimento conservativo delle intestazioni condizionali
numerate e delle alternative esplicite, non interprete generale delle condizioni
italiane. Fermarsi qui, senza integrare il prototipo globale.

## Stop chiarimenti ripetuti e termine esplicito — 8 ottobre 2026

Richiesta corrente conclusa localmente: correggere la CompilationSession reale,
con riproduzione su copia, senza nuove chiamate DeepSeek, benchmark completo,
modifiche a retrieval/parser/prototipo globale o commit/push. Preservate le
modifiche UX/UI già presenti; HEAD rimane `b8071d3`, index Git vuoto.

- Riprodotto il bug dalla revisione 146, immediatamente prima del messaggio
  «no, finisci la compilazione», su backup SQLite e storage isolati. Replay della
  decisione archiviata, non una nuova valutazione AI: il backend precedente
  registrava sei falsi `NOT_APPLICABLE` sull’amministratore di fatto, non esportava
  e chiedeva quattro slot Studio Associato (due condizioni duplicate per entità).
  I valori SOURCE erano realmente **23**.
- Separati risposta, prosecuzione/ripresa e **FINISH**. Il comando esplicito
  viene intercettato prima del planner; anche i contratti semantici distinguono
  FINISH. Prima si persiste l’arresto, poi si usa il finalizzatore esistente con
  `allow_unresolved=True`: nessun nuovo checkpoint, nessuna dichiarazione READY.
  Se una validazione blocca l’export, la compilazione resta ferma e conserva i
  dati; versione, lease, provenienza e controlli fattuali restano obbligatori.
- Riuso conservativo di predicati già verificati USER/SOURCE: soggetto della
  condizione distinto dal soggetto della cella; equivalenze esplicite nel FORM,
  congiunzioni e qualificatori di presenza/assenza. Il falso del genitore esclude
  i sottorami, il falso di un sottoramo non nega il genitore. Un genitore positivo
  non decide i qualificatori. Ambiti/persona/ruolo/progetto/template e anchor
  revisionato con digest limitano la propagazione; contraddizioni restano UNKNOWN.
  Nessuna deduzione di partecipazione dalla forma giuridica, nessuna ontologia
  di esclusione reciproca delle forme societarie. Sintassi non riconosciute
  rimangono opache. Non è un interprete logico generale di tutte le frasi italiane.
- Le decisioni valide già persistite non cambiano. Soltanto le esclusioni USER
  che citano esattamente un comando di fine vengono invalidate come prova,
  conservandone traccia di audit: non sono risposte alla condizione. Riconciliazione
  anche in lettura dopo refresh, senza scrittura implicita; persistenza alla
  successiva mutazione autorizzata, senza migrazioni o reindicizzazioni richieste.
- Domande equivalenti accorpate tra celle/sezioni dello stesso operatore; prima
  il genitore, poi soltanto eventuali qualificatori ancora necessari. «No a
  entrambe» richiede due condizioni effettivamente chieste; «non so» rinvia il
  fatto senza negarlo. Un «no» ambiguo a più destinatari non viene inventato.
- Replay finale sulla **revisione 147 realmente attuale**, in copia: **11**
  candidate Studio Associato esclusi grazie al precedente USER valido; **6**
  false esclusioni del comando tornate UNKNOWN. **23/23 record SOURCE identici**,
  **23 valori esportati e verificati anche nelle rispettive celle XML**. Restano
  **214 candidate irrisolti**, non 214 domande obbligatorie. DOCX/report scaricati
  via API, stato `GENERATED`, report `needs_review`, `ready_for_submission=false`,
  domanda assente e auto-continuazione disattivata anche dopo refresh. Ripresa
  esplicita senza domande Studio Associato già risolte e senza alterare i SOURCE.
- Chat: formulazione più naturale; la card non ripete una domanda già presente
  nella chat, anche dopo refresh, ma mostra una domanda nuova. La bozza parziale
  fermata offre **Scarica DOCX** come azione principale; ripresa nei dettagli.
- Verifiche eseguite ora: **403 test backend mirati passati** (condition_reuse,
  finish, clarifications, controls, active_question, stability, sessions, guards,
  semantics, finalization, conversation), più **43 test compilation_chat/chat_flow**;
  **30 test frontend compilazione**, lint frontend, build frontend e Ruff sugli
  otto file backend modificati/aggiunti passati. `git diff --check` passato.
  Test con provider simulati, FTS5/Qdrant temporanei; replay reale dei dati congelati
  senza provider. Nessun benchmark completo né E2E aggiuntivo in questo pass.
- Audit locale ignorato: `backend/data/compilation-audit/finish-clarifications-20261008T195259Z/REPORT.md`,
  con baseline, snapshot, output `verified-v147`, bozza/report e preservazione.
  **29 originali/storage identici**, sessioni, revisioni, conversazioni, generazioni
  originali e chunk SOURCE identici. Il server locale preesistente `uvicorn --reload`
  ha rieseguito il bootstrap durante gli edit: rigenerati ID/timestamp di tre
  chunk di artefatti derivati e pagine FTS, con contenuti invariati. Annotato
  nell’audit; il database originale non viene descritto come identico byte per byte.

Fermarsi qui. Nessun commit/push, integrazione globale o esperimento AI autorizzato.

## UX/UI mirato compilazione in chat — 8 ottobre 2026

Richiesta corrente: consolidare prima il lavoro concluso, quindi intervenire
soltanto sulla UX della CompilationSession, senza integrare il prototipo globale
o avviare chiamate DeepSeek/benchmark. **Il pass UI resta locale: nessun suo
commit/push autorizzato.** Nessun agente aggiunto.

- Prima del pass: letti AGENTS/STATUS e mappa/README, controllati Git e remoto.
  Le sole modifiche pendenti erano STATUS, prototipo globale, CLI, test e report
  versionato. Rieseguiti **309 test mirati** e Ruff backend completo, controllato
  il diff. Salvati quei cinque file nel commit **`b8071d3`**, pubblicato su
  `origin/main`; audit ignorati esclusi, nessun file estraneo incluso. Working
  tree pulito al termine del push. Nessuna modifica permanente alla config Git.
- UI esistente conservata, nessuna pagina o dipendenza applicativa nuova.
  Animazione discreta e stato accessibile solo per operazioni di compilazione,
  lease attiva o prosecuzione automatica autorizzata; pausa e chat normale non
  simulano attività. Rispettato `prefers-reduced-motion`, senza percentuali/ETA.
- Invia e invio da tastiera bloccati durante elaborazione e ripristino stato;
  composer editabile, testo conservato anche durante avvio/navigazione alla nuova
  conversazione. Riabilitazione ai chiarimenti USER. Guardie sincrone condivise
  fra chat e comandi della sessione, anche prima del prossimo render: doppio
  clic e invii incrociati nello stesso tick non lanciano una seconda richiesta.
- Stato leggibile per elaborazione, chiarimenti, pausa recuperabile e bozza.
  Una sola azione principale della compilazione: ripresa, generazione, download
  o aggiornamento dopo errore. Eliminata la ripresa duplicata nel composer.
  Conteggi tecnici, revisione campi, export parziale/report e rigenerazione nei
  **Dettagli compilazione**, chiusi di default. Una bozza parziale non viene
  descritta come documento completato.
- Refresh: snapshot reale riletto dal backend, lease rispettata senza duplicare
  l'analisi; polling di sola lettura riprendibile dopo errori di rete. Aggiornare
  lo stato non smonta la scheda né cancella i valori digitati nei dettagli,
  anche se la lettura fallisce. Nessun reset del budget persistito. Il draft
  chat è conservato durante le operazioni, senza introdurre persistenza del testo
  non inviato attraverso un ricaricamento completo del browser.
- Backend applicativo invariato: test HTTP realmente concorrente verifica
  lease/versione con vecchia e nuova revisione; secondo resolve, modifica USER
  ed export ricevono **409**, senza ulteriori chiamate al modello simulato né
  sovrascritture. Test eseguito con FTS5 e Qdrant temporanei. Restano le semantiche
  e protezioni FORM/SOURCE/USER esistenti.
- Verifiche: **200 test backend mirati passati** (guards, controls, conversation,
  active_question, finalization), Ruff backend completo passato. **93 test
  frontend passati**, più **28 test compilazione rieseguiti** dopo l'ultima
  correzione sul fallimento della rilettura; lint e build passati sul codice finale.
  **6 E2E passati** su desktop/mobile: flusso conversazionale con movimento
  normale/ridotto e refresh durante lease con errore di lettura recuperabile.
  Coperti chiarimenti, pause/errori, bozza parziale, doppio invio, draft, chat
  normale e richieste incrociate. AI/API simulate; dati backend isolati.
- Ambiente verifiche: primo lancio frontend della baseline con un timeout,
  test isolato poi passato; lanci conclusivi con `--maxWorkers=1`. Chromium
  scaricato nella cache; librerie native mancanti estratte in `.tools/playwright-libs`
  ignorata, senza nuove dipendenze del progetto o installazioni di sistema.
  E2E con `LD_LIBRARY_PATH=$PWD/../.tools/playwright-libs/usr/lib/x86_64-linux-gnu`,
  `PLAYWRIGHT_BASE_URL=http://127.0.0.1:5174` e `--workers=1`; server frontend di
  prova separato, arrestato al termine. Screenshot in `frontend/artifacts/`,
  ignorati da Git.

Nessuna chiamata AI reale, integrazione globale, migrazione o reindicizzazione.
Suite backend completa non rieseguita. Originali/sessioni applicative non usati
per scritture. **Fermarsi qui**: UI/test/questo aggiornamento non committati;
un eventuale commit/push del pass richiede una nuova richiesta.

## Correzione mirata soggetti/condizioni, replay offline — 8 ottobre 2026

Nuova richiesta esplicita: correggere il prototipo usando le due risposte
congelate, senza altri esperimenti DeepSeek né integrazione. Preservate tutte
le modifiche pendenti. **Zero nuove chiamate AI, nessun nuovo agente/livello di
orchestrazione, nessuna modifica a pipeline ordinaria/UI/sessioni, commit/push.**

- Validatore prototipo `global-compilation-offline-v3`: decisioni USER verificate
  prioritarie e conservate con prove, scope e condizione esatta, indipendentemente
  da stato/soggetto/citazione LLM. Conflitti fra record verificati espliciti,
  non risolti scegliendo una risposta del modello. SOURCE ammesse valutate prima
  delle domande per le condizioni riconosciute; nessuna esclusività giuridica
  implicita. Supportate anche risposte SOURCE sì/no alla qualificazione esatta;
  consorziata esecutrice e partecipazione richiedono prove della pratica.
- Decisione backend separata dalla proposta LLM: soggetto, origine, regola e
  citazione integrale verificati. La proposta grezza non viene riscritta.
  Contesti dei ruoli riletti dall'originale verificato: didascalia dei titolari
  di poteri ora correttamente representative; direttori, firmatari, consorziate
  e operatore separati. Record SOURCE consorziata non sovrascrive l'operatore;
  amministratore unico non diventa rappresentante per inferenza.
- Partecipazione: **una sola domanda logica predisposta**, con ID stabile per
  originale; prima verificati USER e SOURCE della pratica. Nessuna deduzione da
  S.r.l./tipologia. Include eventuale designazione esecutrice se il FORM la
  richiede. Domande LLM ripetute accorpate, sottorichieste miste conservate per
  revisione. Nessun invio in chat o nuovo registro persistente: prototipo isolato.
- Replay offline su nuove copie, client provider/risoluzione profili bloccati.
  **279/279 candidate e 15/15 sezioni in entrambi; valori scrivibili invariati,
  esattamente 12 e 14.** Prima risposta: 12 VALIDATED, 10 NA, 6 REVIEW, 251 UNKNOWN;
  thinking: **14 VALIDATED, 10 NA, 6 REVIEW, 249 UNKNOWN** (prima 14/7/6/252).
  Entrambi ora **7 APPLICABLE, 1 NA, 7 UNKNOWN**; thinking prima 7/0/8.
- Recupero concreto del thinking: 5.a esclusa con USER già verificato e soggetto
  operatore; due slot dipendenti UNKNOWN → NA. Le sette decisioni USER locali,
  già presenti, conservate tutte. Sede operativa UNKNOWN → NA per coincidenza
  SOURCE esplicita, senza dipendere dalla proposta errata di scriverla.
  Nessun nuovo valore né taglio/composizione di quelli proposti.
- Restano UNKNOWN 5.b/b-bis/c/e/f/g/h per esclusioni non provate, i poteri/ruolo
  rappresentativo di Luca Ferri, modalità di partecipazione, dati personali,
  abilitazione ed estremi camerali mancanti. **0/13 sospette riproposte o
  approvate**; nessun direttore trasferito ai rappresentanti/consorziate.
  Non risolte in questo pass le altre omissioni/alternative delle domande LLM.
- Export parziali verificati: 12/14 celle autorizzate, altre 497/495 e 13 parti
  accessorie identiche; riapertura e confronto canonico XML passati, solo avviso
  di bozza oltre ai valori. Mai completed/ready. Copertura/schema/troncamento,
  firme e provenienza continuano a bloccare scritture non autorizzate.
- **309 test mirati passati:** 121 prototipo (51 nuovi) + 188 regressioni
  script/DOCX/fonti; provider simulati/storage temporanei. Ruff backend completo
  passato; suite completa/frontend/E2E non eseguiti. Runner e moduli condivisi
  invariati. Preservazione per hash di **33 tabelle, 29 file applicativi e 156
  artefatti storici**. Nessuna migrazione/reindicizzazione o impostazione AI mutata.

[Report e UNKNOWN residui](backend/data/compilation-audit/global-subject-conditions-20261008/report.md),
[confronto macchina](backend/data/compilation-audit/global-subject-conditions-20261008/comparison-final.json),
[replay senza thinking](backend/data/compilation-audit/global-subject-conditions-20261008/verified-without-thinking/validation-offline.json),
[replay thinking](backend/data/compilation-audit/global-subject-conditions-20261008/verified-thinking/validation-offline.json).
Gli esiti conclusivi sono nei percorsi `verified-*`; altri replay nella stessa
cartella sono intermedi locali. Prototipo ancora separato. **Fermarsi qui**:
nessuna ulteriore prova AI, integrazione o modifica ordinaria da avviare da soli.

## Seconda prova globale con thinking — 8 ottobre 2026

Successiva richiesta esplicita: **una sola nuova chiamata reale**, stessi input
congelati e stesso validatore aggiornato, confronto senza integrazione; poi
fermarsi. Preservate tutte le modifiche pendenti. **Nessun codice del prototipo,
pipeline ordinaria o UI modificato; nessun commit/push.**

- Supporto verificato prima della prova sulle pagine ufficiali DeepSeek:
  `deepseek-flash`, thinking con JSON mode. Schema invariato nel prompt e
  Pydantic, non imposto dal provider. Nessun completamento di preflight.
  Unica differenza nel request: `thinking.type=enabled` anziché `disabled`;
  effort default documentato high. Temperatura inviata 0.1 invariata ma ignorata
  dal provider in thinking mode: limite esplicito del confronto.
- FORM/SOURCE/USER, originale e messaggi copiati identici dalla prima prova;
  schema identico. Validatore SHA-256
  `60d89fc1b3665e117805fe092724fb031426ec44ec6feff9dbd8052112a166f1`
  invariato rispetto alla baseline offline. Nessuna riparazione del piano.
- **Thinking confermato effettivamente:** canale reasoning presente e
  **29.087 reasoning token** dichiarati dal provider. Una chiamata, HTTP 200/stop,
  nessun fallback/retry/troncamento. Fingerprint del modello uguale alla prima.
  **213.653 input + 59.152 output = 272.805 token**, output finale 30.065 per
  differenza. **178,392 s** complessivi registrati, **178,074 s HTTP**; prima
  prova 94,407 s, senza misura HTTP separata. Input +25 a messaggi identici:
  causa non dimostrata. Massimo richiesto invariato 98.304, non raggiunto.
- **279/279 candidate, 15/15 sezioni**, zero ID inventati/omessi/duplicati;
  conteggio dichiarato ora corretto 279. **17 valori proposti, 14 verificati e
  scrivibili** contro 14/12. Zero composizioni non letterali contro 2: telefono
  e albo sono i due guadagni. Tutti i 12 candidate già scrivibili conservati;
  CF/P.IVA proposti ora letteralmente dalla scheda Markdown, sempre dati demo.
  **14/18 riferimenti SOURCE ai valori ammessi**, da 9 posizioni distinte.
- Tre nuove proposte bloccate: sede operativa nonostante «se diversa» e
  coincidenza SOURCE esplicita; nome/carica di Luca Ferri con ruolo representative
  non provato. Nome e carica sono documentati, poteri e firmatario no: non sono
  tre fatti inventati né falsi negativi dimostrati. Direttore tecnico distinto
  dai rappresentanti; quattro dati in 5.d e nome nella parte terza validati.
- Regressione: tutte le otto sezioni NA del modello sono legate a un'entità
  ignota invece che all'operatore. Backend: **7 APPLICABLE, 0 NA, 8 UNKNOWN**
  contro 7/1/7. 5.a già risolta dalle 7 decisioni USER; niente nuova domanda.
  Cinque rami di tipologia hanno anche esclusioni non certificate dal validatore
  congelato, senza ontologia negativa generale: non implicano cinque nuove
  domande obbligatorie. 5.g/5.h richiedono qualificazione/relazione documentata
  o USER; S.r.l. non determina consorzio né designazione di consorziata.
  SOURCE basta già a escludere la sede operativa coincidente. Nessuna di queste
  valutazioni manuali applicata al piano. Stati candidate: 14 VALIDATED, 7 NA,
  6 REVIEW, 252 UNKNOWN; le sette decisioni USER locali rimangono NA.
- **0/13 vecchie assegnazioni sospette riproposte**, tutte UNKNOWN backend.
  Quattro target consorziate ancora nella sezione corretta; perdita però del
  ruolo distinto consortium_member, ora generico unknown/other.
- **5 domande contro 11**, zero duplicati testuali. Tolte riconferme inutili,
  ma omessi gli estremi camerali e la data di abilitazione, realmente mancanti;
  registro pubblico chiesto insieme ai dati benché alternativa FORM. Domanda
  concordato pertinente alla condizione reale, non attestata negativa da SOURCE.
  Nessuna domanda inoltrata alla chat. Meno domande non prova copertura migliore.
- **Export parziale reale:** 14 celle scritte, altre 495 e 13 parti accessorie
  identiche; riapertura e confronto canonico XML riusciti, oltre alle celle
  autorizzate solo avviso di bozza. Mai completato/pronto all'invio.
  **70 test prototipo passati in 5,53 s**, Ruff backend completo passato.
  Le 181 regressioni precedenti non rieseguite; niente frontend/E2E.
  Preservati 33 tabelle SQLite, 29 file applicativi, codice e prima prova per hash.
  Nessuna migrazione/reindicizzazione o modifica alle impostazioni AI.

[Report comparativo completo](backend/data/compilation-audit/global-thinking-20261008/report.md),
[metriche e verdetti](backend/data/compilation-audit/global-thinking-20261008/comparison.json),
[DOCX parziale thinking](backend/data/compilation-audit/global-thinking-20261008/live-01/bozza-globale-parziale.docx).
**Non dimostrato un miglioramento globale sufficiente:** due scritture in più,
ma regressioni semantiche, chiarimenti omessi, tempo circa 1,89× e token totali
+9,33%. Una coppia di risposte non misura varianza/statistica. Prototipo separato;
fermarsi qui, nessuna ulteriore chiamata o integrazione autorizzata automaticamente.

## Rivalutazione offline del prototipo globale — 8 ottobre 2026

Nuova richiesta esplicita: correggere i limiti dimostrati, rivalutare la risposta
già ottenuta, distinguere le 14 proposte e provare l'export parziale. **Nessuna
nuova chiamata DeepSeek, integrazione, modifica UI, commit o push.** Preservate
tutte le modifiche pendenti del precedente esperimento e tutti i suoi artefatti.

- Copertura ora calcolata dagli ID reali/univoci: **279/279 candidate, 15/15
  sezioni**. Il `coverage_count=400` originale rimane invariato e genera un
  avviso, senza bloccare da solo l'export. Omissioni, duplicati, ID estranei,
  piano incompleto, output troncato e schema invalido continuano a bloccare
  tutte le scritture. Nessuna correzione della risposta del modello.
- Parser SOURCE esteso a righe di tabella PDF con etichette esplicite senza
  `:`, mantenendo proprietario, proprietà e ruolo; ordine professionale nel
  seguito immediato del record direttore. Applicabilità positiva verificata
  anche per enumerazioni FORM riconosciute interamente, senza perdere ulteriori
  qualificazioni o dedurre partecipazione/appartenenze dalla forma giuridica.
- Revisione manuale dei 14 valori: **9 già corretti/validati, 3 falsi negativi
  recuperati, 2 errori di composizione dell'output**. Recuperati CF e P.IVA
  letterali nella riga 13 del PDF, annotazione inclusa, **solo come dati demo**;
  recuperato il nome del direttore in parte terza, con tipologia esplicitamente
  inclusa nella lista FORM. Telefono e numero albo hanno dati di base corretti
  ma stringhe complete ricomposte/non letterali: restano UNKNOWN, senza ritagli
  automatici. Nessuna attestazione di validità degli identificativi fittizi.
- **12 valori e 21/27 riferimenti SOURCE validati**, da 12 posizioni documentali
  distinte, con citazioni ripetute tra campi. Le due fonti non sono indipendenti.
  Ulteriore falso negativo locale corretto: sede operativa «se diversa», esclusa
  dalla relazione SOURCE esplicita di coincidenza delle sedi dello stesso
  operatore. Stati finali: 12 VALIDATED, 10 NA, 6 REVIEW, 251 UNKNOWN.
  Le 13 vecchie assegnazioni sospette non vengono riproposte e restano UNKNOWN;
  esclusioni dei rami non provate e poteri di rappresentanza non approvati.
- Domanda mista sul direttore conservata separatamente per riformulazione,
  senza perdere la data di abilitazione mancante. Nove altre domande conservate
  da valutare; una conferma interamente risolta scartata. Nessuna inoltrata alla
  chat. Il filtro non certifica che tutte le domande residue siano necessarie.
- CLI `--validate-only --replay-from STORICO --output NUOVO` crea una copia nuova,
  verifica coerenza richiesta/input e hash/catalogo dell'originale, preserva
  baseline e manifest e registra **zero chiamate aggiuntive**. Client provider
  e risoluzione profili bloccati durante il replay effettivo. Le usage nei report
  sono quelle della chiamata storica; nessun nuovo consumo di token AI.
- **Export parziale reale riuscito:** 12 celle scritte con valori originali,
  altre 497 celle e 13 parti accessorie identiche. Riapertura python-docx e
  confronto canonico dell'intero XML: sole celle autorizzate e avviso di bozza
  modificati. `document_completed=false`, `ready_for_submission=false`.
- **181 test mirati finali passati in 13,94 s**: 70 del prototipo più 111
  regressioni script/DOCX/validazione, provider simulati e dati temporanei.
  Ruff backend completo passato. Suite completa/frontend/E2E non rieseguiti.
  Originali invariati su **33 tabelle SQLite e 29 file applicativi**, incluse
  tutte le sessioni e revisioni. Nessuna migrazione o reindicizzazione.

[Report offline e 14 verdetti](backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/report.md),
[DOCX parziale](backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/replay-final/bozza-globale-parziale.docx),
[documentazione aggiornata](docs/global-compilation-experiment.md).
Prototipo ancora separato. La rappresentazione FORM ridondante e la modalità
`thinking=disabled` storica non sono cambiate: non sono state provate nuove
configurazioni del modello. La revisione chiarisce i falsi negativi dimostrati,
non misura l'accuratezza globale del modello né autorizza l'integrazione.
Fermarsi dopo questa rivalutazione; ulteriori prove reali o integrazioni non autorizzate.

## Esperimento globale one-shot DeepSeek — 8 ottobre 2026

Richiesta esplicita dell'utente: prototipo separato, una sola chiamata globale
reale su copia Catanzaro, confronto con stability pass; poi fermarsi. Base
`main`, `bf998c5`, working tree inizialmente pulito. **Nessun commit/push.**
Pipeline ordinaria, UI, README/start e tutte le sessioni originali invariati.

- Aggiunti `backend/app/global_compilation.py`, CLI
  `backend/scripts/global_compilation_experiment.py`, 34 test e
  [documentazione del prototipo](docs/global-compilation-experiment.md).
  Una richiesta con FORM completo/strutturato, SOURCE integrali e USER separati;
  schema rigoroso, verifiche backend di provenienza, proprietà, identità/ruolo,
  condizioni, ID, duplicati/omissioni e coverage. Nessun retrieval, batch,
  revisore LLM, riparazione o fallback. `--validate-only` rilegge la medesima
  risposta senza provider. Nessun nome/ID del caso codificato nel motore.
- Profilo reale `deepseek-flash` ufficiale: `context_window=32768` salvato si
  applica solo a Ollama, non al contesto remoto DeepSeek. Documentazione attuale
  verificata: 1M contesto, massimo output dichiarato 393.216 token. Sessioni
  ordinarie inviano 8.192 token/fase; vecchia API unica 32.768 e massimo 200.000
  caratteri di risposta. Prototipo invia **98.304 token**, JSON mode con schema
  nel prompt e validazione Pydantic: non schema imposto dal provider.
- **Una chiamata reale**, HTTP 200/stop, **213.628 input + 35.887 output =
  249.515 token**, **94,407 s** intorno a invio/ricezione e prima verifica locale.
  Nessun troncamento. Tutti i **279 candidate e 15 sezioni** presenti, zero ID
  estranei/omessi; il modello dichiara però **coverage_count=400**. Errore
  globale esplicito: **zero scritture, zero DOCX**, mai completed/READY.
  Il primo ConnectError del sandbox è avvenuto prima dell'invio, model_calls=0;
  dopo l'autorizzazione di rete è stata inviata la sola richiesta reale.
- Input dalla sola **v102**, con **7 decisioni USER non professionista singolo**;
  nessuna fusione con la v83. Copia SQLite read-only, originali/fonti congelati:
  **829 paragrafi** in ordine verificati, **50 tabelle**, titoli nelle celle,
  note, footer, numerazione e stili; **3 SOURCE integrali / 15.824 caratteri**.
  Nessuna SOURCE fattuale nel progetto attuale; project-facts separato come
  USER, altre bozze/artefatti esclusi. Unica immagine: logo della Fondazione,
  verificato localmente; il prototipo inventaria immagini, senza OCR implicito.
- **14 valori proposti / 27 riferimenti SOURCE; 9 valori con 9 prove ammessi
  localmente** nella verifica finale, tutti comunque bloccati dalla coverage.
  Prima verifica: un solo valore, perché una prova PDF non supportata scartava
  anche la prova Markdown valida. Corretto il controllo per prove indipendenti
  e rivalidata **offline la stessa risposta**, senza alterare valori/prompt o
  chiamare DeepSeek. Conservati codice al momento della chiamata, entrambi gli
  esiti e risposta grezza. Il validatore resta limitato a proprietà testuali
  esplicite; 10 riferimenti PDF non supportati non sono dichiarati falsi.
- Confronto concreto: **0/13 vecchie assegnazioni sospette riproposte**, ma le
  esclusioni sostitutive non sono provate e tutti i 13 restano UNKNOWN. I quattro
  blocchi consorziate hanno ora section_id corretto 573 e soggetto distinto dal
  consorzio; esclusioni di 5.g/5.h non approvate. Unica sezione esclusa con prova:
  professionista singolo, USER. 5.d: tre dati aziendali e tre del direttore
  ammessi localmente; albo/telefono contengono composizioni non letterali
  respinte. Prima tabella: tre valori ammessi; CF/P.IVA e condizione sulle sedi
  risentono anche dei limiti del validatore. Luca Ferri è proposto representative
  senza prova di poteri: ruolo non approvato. Non equiparato il direttore tecnico
  a firmatario o soggetto con poteri. **11 domande proposte**: revisione manuale
  distingue 7 gruppi necessari, 2 condizionali, 1 ridondante, 1 alternativa;
  il filtro automatico delle domande miste resta insufficiente. Nessuna domanda
  del modello effettivamente inoltrata alla chat.
- **145 test mirati finali passati in 12,57 s** (34 nuovi + regressioni
  script/DOCX/validazione), provider simulati e dati temporanei. Ruff completo,
  diff/whitespace e riferimenti controllati. Un processo nel sandbox interrotto
  non è contato come passato; la diagnosi mostrava event loop in attesa e thread
  inattivo; gli stessi test completati fuori sandbox. Nessuna suite completa o
  frontend/E2E rieseguiti. Preservazione finale: **33 tabelle SQLite e 29 file
  applicativi invariati**, incluse tutte le sessioni/revisioni e v83/v102.
  Nessuna migrazione o reindicizzazione.

Report locale con confronto campo per campo, 13 assegnazioni, domande, limiti
e tracce: [esperimento globale](backend/data/compilation-audit/global-one-shot-20261008/report.md).
**Non dimostrata una superiorità sufficiente: nessuna integrazione attivata.**
Proposta soltanto condizionata a una prova migliore: ingresso opzionale nel
resolver, unico piano globale verificato, importazione atomica con versione/hash,
riuso di writer e chiarimenti USER esistenti, fallimento esplicito senza fallback.
L'utente ha chiesto di fermarsi dopo questo esperimento: nessuna ulteriore prova
reale o modifica della pipeline da avviare automaticamente.

## Commit locali richiesti dall'utente — 8 ottobre 2026

Su richiesta esplicita sono stati consolidati i fix locali precedenti e lo
stability pass. Backend e regressioni nel commit `52a86ce`
(`fix: isolate DOCX model failures and preserve compilation state`);
il commit successivo contiene messaggi UI di recupero e questa continuità.
Nessun push. DOCX compilati, report reali nuovi, DB, snapshot e tracce restano
locali e ignorati da Git. README/start invariati. Il codice coincide con quello
verificato dai 1.296 test backend, 84 frontend e dalla prova reale mirata sotto;
nessuna suite o prova reale ripetuta per il solo commit. Restano aperti i
quattro blocchi FORM e i problemi di pertinenza dei rami descritti sotto.

## Ultimo intervento: stability pass CompilationSession — 8 ottobre 2026

Preservati i fix locali matcher/classificatore e le modifiche di continuità
preesistenti. Nessun commit/push; README/start invariati. Report completo locale,
audit dei confini e tracce (ignorati da Git):
[stability pass](backend/data/compilation-audit/stability-pass-20261008/report.md).

- Revisioni FORM/SOURCE ora isolano ID estranei, duplicati e item invalidi,
  conservando approvazioni indipendenti; un verdetto per una proposta storica
  già filtrata non provoca più un lookup interno errato. Fatti con SOURCE
  estranea scartati. Coverage backend incoerente resta ValueError esplicito.
- Errori tipizzati soltanto al confine reale del modello: schema recuperabile
  entro i due tentativi della propria fase; provider/timeout sospendono senza
  consumare altri campi. Esaurimento non genera domande sui PENDING né READY.
  Messaggio persistito comprensibile; nessun catch generale di bug interni.
- Risposte USER di gruppo parzialmente invalide conservano gli slot validi
  univoci. Condizioni USER già risposte non vengono dimenticate dalla rianalisi;
  propagazione delle dipendenze non cancella valori SOURCE/USER persistiti.
  Pausa/ripresa letterali disponibili anche se il planner non risponde.
  Modifiche UI limitate a messaggi/avviso: dettagli tecnici nei log, nessun
  nuovo workflow o modifica dell'orchestrazione dei batch.
- **43 nuove regressioni**, **315 test mirati finali passati** (85,50 s).
  **1.296 backend complessivi passati**, copertura disgiunta 315+348+336+297;
  un primo processo unico interrotto non è conteggiato come suite passata.
  **84 frontend passati**, Ruff, lint/build e diff check passati. Test includono
  errori consecutivi, retry esauriti, due resume, decisione negativa già
  registrata, conservazione prove, scope e DOCX parziale materializzato con
  ready_for_submission=false. Nessuna migrazione/reindicizzazione richiesta.
- I quattro blocchi sono `t38.r1.c1`, `t38.r2.c0`, `t38.r2.c1`, `t38.r3.c0`:
  ragioni sociali/CF-P.IVA delle consorziate, non anagrafica dell'operatore.
  La condizione consorzio stabile esiste in paragraph:573, ma il modello la
  legava a paragraph:595. Rebind solo letterale/univoco, con revisione finale
  rigorosa. **Restano bloccati nella prova reale**: modello/reviewer assegnano
  ancora subject_type alle consorziate, confondendole col consorzio compilatore.
  Nessuna deroga al controllo, nessun rimborso dei retry (interpretazione 2,
  SOURCE 0). Distinguere i due soggetti richiede un intervento separato.
- Prova reale mirata, DeepSeek flash/Qdrant/BGE reali su copie: quattro campi
  espliciti + un solo batch automatico successivo di 12; 6 chiamate, 40,195 s,
  nessuna eccezione, 11 query/7 chunk/9 candidate ricercati. **22 SOURCE
  preservati, zero nuovi valori**, 263 altri candidate invariati. Copia v89
  CREATED, auto_continue=true: 22 RESOLVED, 22 MISSING, 34 AMBIGUOUS, 1 NA,
  200 PENDING. Nessun benchmark completo o DOCX reale generato, non READY.
- Nella copia della precedente v102, due resume conservano tutte le **7
  decisioni USER «non professionista singolo»** e tutti gli altri campi.
  La sessione attuale v83 con 22 SOURCE non contiene tali decisioni: non
  confondere i due test. Originali confermati invariati **v83 e v102**.

**Problemi distinti da riprendere solo con un nuovo incarico:** i 22 valori
preservati includono assegnazioni preesistenti non sufficientemente giustificate
nei rami Studio Associato (t14/t15) e Società di Professionisti/soci (t19/t22/t23).
Il report identifica 13 valori interessati e le evidenze; non riapprovati né
cancellati durante questo pass. Serve valutare soggetto della condizione,
eredità del contesto di sezione e identità delle entità elencate. La robustezza
è verificata; la correttezza semantica di quei rami e dei quattro campi non è
dichiarata risolta. I budget esauriti non si riaprono con il solo resume.

## Ultimo intervento: classificazione fuori dal gruppo selezionato — 8 ottobre 2026

Seguito del fix matcher sotto: nella **nuova sessione** Catanzaro
`7945c99079a54d729f67855a4d03a956`, v83 FAILED, l'utente ha ricevuto
`Classificazione con candidate sconosciuto`. Conservati **22 valori SOURCE**.
Il gruppo interrotto riguarda sei celle della tabella delle consorziate,
ciascuna con 2 tentativi di interpretazione e 0 SOURCE. La risposta grezza
storica non è conservata: non è identificabile l'ID estraneo preciso.

- Esteso il controllo degli ID al classificatore: `bind_meanings` filtra gli
  output prima della revisione FORM e dell'applicazione. ID estranei, inclusi
  errori item-local su ID estranei, non interrompono le interpretazioni valide.
  Duplicati tutti respinti, senza scegliere una versione; target omessi restano
  PENDING. Scarti persistiti in `last_resolution.interpretation_rejections`.
  Prompt con lista di ID ammessi. Quote/anchor, revisione indipendente FORM e
  controlli SOURCE restano obbligatori; nessun nuovo counter, retry o migrazione.
  Modificato soltanto il resolver e i test, preservando il fix matcher locale.
- **18 nuove regressioni FTS5/Qdrant**, con riproduzione del medesimo 502 prima
  del fix: sibling valido risolto, precedente SOURCE intatto, filtro prima
  della revisione FORM, ID estranei validi/invalidi, duplicati, FORM non grounded
  respinto, contatori separati, stop dopo due tentativi e failure provider.
  Aggiornata la vecchia aspettativa di test sui duplicati di interpretazione:
  ora sono errori locali, non globali. **272 test mirati passati in 57,97 s**,
  incluse tutte le 254 regressioni del fix precedente; Ruff backend completo e
  diff check superati. Suite completa/frontend non rieseguiti.
- **Prova reale dei soli sei candidate su copia isolata della v83**, con
  rianalisi esplicita perché i tentativi automatici erano già esauriti.
  DeepSeek `deepseek-flash`, 1 chiamata, 6,470 s, nessun errore globale.
  **2 AMBIGUOUS** (barrature/scelte sulle consorziate), **4 PENDING**:
  `Condizione non ancorata alla sezione FORM`. Zero SOURCE interrogate o nuovi
  valori; Qdrant configurato, ma non chiamato perché i dati non superano FORM.
  Nessuna prova di compilazione completa: il vincolo FORM delle quattro celle
  è un limite distinto, non corretto in questo intervento. **273 altri candidate
  identici**, inclusi i 22 SOURCE; codice invariato durante la prova.

**Punto di ripresa:** il controllo di scope ora copre interpretazione e matcher.
La sessione applicativa resta v83 FAILED, campi e counter invariati; **Prosegui
compilazione** rinnova il ciclo sui candidate ancora analizzabili. I sei target
con budget già esaurito non vengono riprovati automaticamente: per riesaminarli
serve una rianalisi esplicita limitata, senza azzerare globalmente i counter.
README/start e documenti preservati. **Nessun commit/push.** Report locale,
snapshot e tracce sotto `backend/data/compilation-audit/classification-scope-20261008/`
(ignorato da Git).

## Ultimo intervento: matcher fuori dal gruppo ricercato — 8 ottobre 2026

Corretto localmente il blocco `Matcher con candidate sconosciuto, duplicato o
non ricercato` della sessione Catanzaro
`7167b46dbb134e0db41ff9f092d55e6b`, v102 FAILED: **17 valori SOURCE conservati**,
113 posizioni analizzate. Il failure era nel passo SOURCE dei dieci candidate
relativi a socio unico/amministratore di fatto, già interpretati. La risposta
grezza del failure storico non è disponibile: non è identificabile l'ID preciso
che lo aveva causato.

- `compilation_session_resolution.py` vincola il matcher agli ID effettivamente
  ricercati, prima della revisione SOURCE e dell'applicazione. Output fuori ambito
  e duplicati vengono scartati e registrati in `last_resolution.matcher_rejections`;
  dei duplicati non viene scelta arbitrariamente una versione. Gli item validi
  conservano le proprie verifiche. Se una risposta contaminata omette un target,
  il suo retry SOURCE rimane limitato dai counter esistenti. Errori globali di
  schema/provider restano espliciti. Nessun nuovo counter o limite, migrazione,
  modifica UI, retrieval, semantica FORM, grouped o renderer.
- **19 nuove regressioni**, incluse FTS5/Qdrant, valore precedente invariato,
  risoluzione del sibling valido, scope prima della revisione SOURCE, duplicati,
  campo non ricercato invariato, retry esaurito senza loop e failure globali.
  **254 test mirati passati in 95,01 s**, incluse semantica, prima tabella,
  retry separati, sessioni/guardie, grouped, active question e finalizzazione.
  Ruff backend completo e diff check superati; suite completa/frontend non
  rieseguiti. Questi sono test software con provider simulati.
- **Prova reale di un solo passo su copia isolata della v102**: DeepSeek
  `deepseek-flash`, Qdrant locale e BGE-M3 reali, stesse fonti/Company KB.
  Superato il gruppo senza failure: **10 SOURCE cercati, 10 MISSING**, zero nuove
  risoluzioni, perché mancano prove dei ruoli/dati personali richiesti. Non
  trasferiti dati aziendali o di un amministratore unico ad altri ruoli/persona.
  2 chiamate modello, 6 query, 7 chunk, 17,637 s. Nessuna interpretazione ripetuta;
  counter interpretazione invariati a 1 e SOURCE a 2 per i dieci target.
  **269 altri candidate invariati**, inclusi i 17 SOURCE; codice invariato durante
  la prova. La copia passa a v105 CREATED con `auto_continue=true`, 123 posizioni
  analizzate e 156 PENDING. Non eseguiti altri passi né generazioni DOCX.

**Punto di ripresa:** la sessione originale è ancora v102 FAILED, campi invariati;
usare **Prosegui compilazione** nella conversazione esistente con il backend
aggiornato. Non serve ricreare la sessione o azzerare i tentativi. La prova
verifica il superamento di quel gruppo, non il completamento dei 279 candidate.
README/start e DOCX locali preservati. **Nessun commit/push.** Report e tracce
restano fuori Git in
`backend/data/compilation-audit/matcher-scope-20261008/report.md`.

## Commit locale richiesto — 8 ottobre 2026

Richiesto dall'utente il commit dello stato funzionante, con push manuale a suo
carico. Inclusi fix FORM delle tabelle, fix SQLite della finalizzazione, relativi
test e modifiche intenzionali già presenti a README/start. Gli originali demo
restano fixture versionate; i DOCX compilati nella radice restano ignorati.
Aggiunte a `.gitignore` le esclusioni di `compilazioni-report.md` e dei due
report locali nuovi in `docs/` (diagnosi Minervino e prima tabella Catanzaro):
restano disponibili sul PC, fuori dal commit. I collegamenti sotto a questi
artefatti si riferiscono alla copia locale.

**Verifiche rieseguite prima del commit:** 24 test mirati passati in 10,89 s
(`test_compilation_table_fields.py` e `test_compilation_finalization.py`), Ruff
backend completo, sintassi Bash, `start.sh --help` e diff check superati.
Nessun nuovo benchmark AI, installazione o avvio dei servizi in questi controlli.
Le suite più ampie riportate sotto sono le esecuzioni precedenti.

## Ultima operazione: DOCX della prima tabella Catanzaro — 8 ottobre 2026

Su richiesta dell'utente, generato nella radice
[catanzaro-domanda-partecipazione-prima-tabella-compilata.docx](catanzaro-domanda-partecipazione-prima-tabella-compilata.docx)
dall'originale della prova limitata descritta sotto: **6 valori SOURCE scritti**,
sede operativa lasciata vuota perché NOT_APPLICABLE/SOURCE. È una **bozza parziale**,
`ready_for_submission=false`, con i restanti 272 candidate non analizzati.

Esportazione con il finalizzatore esistente e `allow_unresolved=true` su una
nuova copia del DB del benchmark; stato e campi della sessione del benchmark
preservati. **Zero nuove chiamate AI**, nessuna analisi dell'intero documento.
Verificati i sei valori nelle celle fisiche, le altre celle e i paragrafi
invariati (salvo avviso di bozza), le parti DOCX esterne al corpo byte per byte
e gli hash dell'originale/output. Codice, README/start e precedente DOCX Catanzaro
preservati; nessun commit/push. Suite software non ripetute per il solo export.
Report tecnico e verifiche in
`backend/data/compilation-audit/catanzaro-first-table-20261008/export-01/`;
nota aggiunta al report reale della prima tabella.

## Ultimo intervento: anagrafica della prima tabella Catanzaro — 8 ottobre 2026

Correzione circoscritta ai normali campi tabellari, sopra le modifiche locali
precedenti, preservate. **Nessun commit/push.** Il codice non contiene riferimenti
a Catanzaro, candidate ID o Mapi per decidere la validazione.

- `compilation_semantics.py` espone sezioni FORM per tabella/riga, ricavate dal
  catalogo dell'originale. Nelle celle tabellari non promuove più automaticamente
  il soggetto aziendale generico a condizione di tipologia. La revisione FORM
  indipendente e `condition_complete` restano obbligatori; le condizioni locali
  letterali possono ancorarsi alla propria riga. Il percorso dei paragrafi non
  cambia. Prompt classificatore/revisore precisati per citazioni locali,
  soggetto corretto e rispetto delle condizioni effettive.
- **16 nuove verifiche** su tabella generica; **227 test mirati passati in
  46,21 s**, incluse semantica, sessioni, retry separati, grouped, active question
  e guardie. Ruff backend completo e diff check passati. Suite backend completa
  e frontend non rieseguite per questa modifica circoscritta.
- **Prova reale limitata ai sette campi `t0.r5.c1`–`t0.r11.c1`**, nuova sessione
  isolata `57cdd64bfb534f64817016f3e3ed81a2`: DeepSeek `deepseek-flash`, Qdrant e
  BGE-M3/Ollama reali, stessa Company KB (contenuti confrontati con l'app).
  **7 FORM accettati, 7 SOURCE cercati, 6 RESOLVED/SOURCE**, al primo passaggio.
  Operatore economico, forma giuridica, sede legale, CF azienda, P.IVA, telefono.
  **Sede operativa NOT_APPLICABLE/SOURCE**: la KB attesta che coincide con la
  sede legale; preservata la condizione «se diversa dalla sede legale».
  Zero valori USER e zero errori di validazione; 5 chiamate modello, 6 query,
  28,893 s. Codice invariato durante la prova, **272 altri candidate invariati**.
- Nessuna modifica a retrieval, provenance SOURCE/USER, placeholder gate, UI,
  grouped, retry, parser/renderer o orchestrazione. Nessuna migrazione né
  reindicizzazione dell'app. Nessun DOCX rigenerato o READY forzato. README/start
  e le tre bozze precedenti nella radice preservati.

**Punto di ripresa:** il blocco FORM dei sette campi è verificato risolto nella
prova limitata; non è una verifica degli altri 272 candidate. I tentativi delle
sessioni storiche non sono azzerati. Per riprovare una sessione esistente usare
la rianalisi esplicita dei soli campi selezionati, che rilegge il contesto del
proprio originale; non avviare automaticamente una nuova analisi completa.
Report con valori, query, anchor, evidence e limiti:
[prima tabella Catanzaro](docs/test-reale-catanzaro-prima-tabella-2026-10-08.md).
Archivio ignorato:
`backend/data/compilation-audit/catanzaro-first-table-20261008/run-01/`.

## Ultima operazione: esportazione dei tre moduli — 8 ottobre 2026

Su richiesta esplicita dell'utente, salvati nella **radice del progetto**:

- `catanzaro-domanda-partecipazione-compilata.docx`: **1 valore SOURCE**.
- `trapani-manifestazione-interesse-compilata.docx`: **9 valori SOURCE**.
- `minervino-domanda-iscrizione-compilata.docx`: **6 valori SOURCE**.
- [compilazioni-report.md](compilazioni-report.md): riepilogo, output chat,
  chiarimenti, valori/prove e tabella completa dei **648 candidate**.

Sono **bozze parziali**, generate con `allow_unresolved=true` su copie isolate:
report nativi `needs_review`, `ready_for_submission=false`; nessun READY forzato,
valore USER inventato o firmatario scelto. Sessioni/documenti originali preservati.
Nessuna modifica al codice applicativo, README/start preservati, nessun commit/push.

Trapani usa la sessione recente `88149be5f16041bbae2985010fea7fdb` v53
(115 candidate: 9 SOURCE, 52 MISSING, 23 AMBIGUOUS, 31 PENDING).
Minervino nel frattempo ha terminato il ciclo avviato dall'applicazione: esportata
la v124 WAITING_FOR_USER (254 candidate: 6 SOURCE, 115 MISSING, 49 AMBIGUOUS,
84 PENDING), distinta dalla v90 della diagnosi storica sotto.

Per Catanzaro, assente una sessione nell'app, creata una **nuova sessione isolata**
`5c863d37ee3d4a00b68ddd00bbb22a20`, usando originale/fonti dell'archivio retry
Catanzaro e KB globale con chunk identici a quelli attuali. DeepSeek
`deepseek-flash`, Qdrant e BGE-M3 reali; 88 chiamate strutturate / 324,49 s.
Analisi **FAILED v74** al passo 28, `GenerationError` nella chiamata
`CandidateMatches`; dettaglio testuale non conservato, causa provider/output
non determinabile dalla traccia. 279 candidate: 1 SOURCE, 31 MISSING,
37 AMBIGUOUS, 210 PENDING. Esportata la sede legale già accettata prima del failure,
senza riusare valori dei benchmark precedenti né aggiungere retry.

**Verifiche effettive dell'export:** 16 valori controllati nelle celle/paragrafi
di destinazione; SHA-256 corretti e tutte le parti DOCX diverse dal corpo
preservate byte per byte. Nessuna chiamata AI per gli export Trapani/Minervino.
Suite software non ripetute per la sola generazione di artefatti; i 436 mirati
sotto rimangono la verifica del precedente fix SQLite. Diff check passato.
Archivio ignorato: `backend/data/compilation-audit/exports-three-20261008T110401Z/`.

**Punto di ripresa:** le tre esportazioni non attestano moduli completi. Restano
le diagnosi semantiche/di applicabilità dei PENDING e il failure Catanzaro;
conservare i counter e i gate FORM/SOURCE. Non trattare le bozze come SOURCE.

## Fix locale: blocco SQLite in finalizzazione Minervino — 8 ottobre 2026

Corretto localmente il 500 `database is locked` durante l'esportazione della
sessione `c34440fe726f4790acd586424e212078`, progetto
`minervino-di-lecce-elenco-sia`. **Nessun nuovo commit/push.** All'inizio `main`
era allineata a `origin/main`, con sole modifiche locali a README/start:
preservate byte per byte. Il commit `f1e06fe` contiene già il precedente lavoro
semantico e i report; lo storico sotto descrive le prove prima di quel commit.

- `_persist` salva il report in una transazione SQLite; il callback della
  sessione rileggeva le SOURCE aprendo una seconda connessione. Il report di
  Minervino (circa 2,37 MB) riproduce il blocco con le impostazioni SQLite
  ordinarie: il cache spill della scrittura impedisce la lettura separata.
- `reload_evidence` accetta una connessione opzionale, senza chiuderla o fare
  commit quando è fornita dal chiamante. `save_generation` la passa tramite
  `check_current_sources`: rilettura SOURCE e salvataggio restano nella stessa
  transazione. Conservati controllo versione, isolamento/provenance e rifiuto
  delle SOURCE cambiate. Nessuna modifica a timeout, journal mode, schema,
  migrazioni, UI, parser/renderer, retry o orchestrazione.
- **8 regressioni nuove passate**, combinazioni FTS5/Qdrant e Company/project
  SOURCE: salvataggio sotto lock esclusivo reale, valori SOURCE/USER nel DOCX,
  rifiuto 409 di SOURCE cambiata e rollback di sessione/report/file.
  **436 test mirati passati in 106,18 s**, incluse le otto regressioni, sessioni,
  guardie, SOURCE/retrieval FORM, DOCX, semantica, retry separati, grouped,
  active question e controlli. Ruff e diff check passati. La suite backend completa e il
  frontend non sono stati rieseguiti per questo fix circoscritto.
- Replay tecnico su due copie dello stesso DB/sessione: prima riprodotto
  `OperationalError: database is locked` in 8,06 s; dopo GENERATED v91 in 2,59 s,
  sei valori materializzati negli slot originali e field/provenance invariati.
  Solo le copie usano `allow_unresolved=true`. **Non è un nuovo benchmark AI
  né un modulo completo**: zero chiamate modello, nessuna sessione reale alterata.

**Stato originale conservato:** v90 FAILED, nessuna generazione; 254 candidate,
6 RESOLVED, 66 MISSING, 35 AMBIGUOUS, 147 PENDING. Il ciclo aveva già raggiunto
36 passi (budget 36/600 s): distinto dal successivo errore in esportazione.
Fra i PENDING: 52 senza tentativi, 12 con un tentativo, 83 con due; 61 riportano
`Condizione non ancorata alla sezione FORM`. Il fix SQLite non risolve questi
errori semantici e non ricarica i retry. La ripresa non garantisce il completamento.

**Prossimo passo minimo:** dopo il reload del backend la finalizzazione usa il
fix; la sessione esistente conserva tutti i valori. Per completare Minervino
occorre una diagnosi separata dei PENDING, partendo dalle condizioni FORM
respinte, e dei chiarimenti di applicabilità. Non azzerare sessioni/counter né
allentare i gate. Nessuna migrazione/reindicizzazione necessaria per il fix.
Dettagli e limiti in
[diagnosi Minervino, 8 ottobre](docs/diagnosi-minervino-finalizzazione-2026-10-08.md).
Archivio tecnico ignorato: `backend/data/compilation-audit/minervino-finalize-lock-20261008/`.

## Storico: semantica FORM e contesto SOURCE — 8 ottobre 2026

Implementazione e test software conclusi sopra le modifiche locali dei retry,
**senza commit/push**. Dopo la ricarica DeepSeek, **criterio principale verificato
sul codice finale**: otto dati societari utili RESOLVED/SOURCE, tipologia SOURCE,
Fax MISSING, nessun firmatario inferito o valore della gara usato come servizio
pregresso. Il modulo completo NON è READY: 30 PENDING e chiarimenti rinviati
restano aperti. Non equiparare questo risultato al completamento dell'intero modulo.

- Binding persistente fra slot fisico, proprietà semantica, soggetto, sezione e
  ruolo temporale. Il backend ancora lo slot all'originale; una revisione FORM
  indipendente ammette label normalizzate anche non letterali, conservando quote,
  soggetti e condizioni ancorati al modulo. Organizzazione rappresentata distinta
  da persona, professionista e firmatario.
- Applicabilità condivisa per sezione/entità/condizione verificate. La tipologia
  implicita di un'organizzazione rappresentata viene conservata come condizione
  FORM; `condition_complete` controlla anche qualificatori esteri/giuridici.
  SOURCE/USER determinano il fatto, non il FORM. Esclusioni fra alternative
  soltanto con istruzione FORM esplicita di scelta unica.
- `PAST_SERVICE` distinto da `CURRENT_PROCEDURE`: estrazione indipendente di
  fatti di servizi già eseguiti, senza candidate/valori attesi nel prompt, poi
  revisione della proposta e rilettura della prova in finalizzazione. Dati della
  gara corrente e attività generiche non attestano incarichi pregressi.
- Respinti placeholder, linee vuote, N/A, etichette senza valore e indicazioni
  esplicite di campo non compilato. Le sigle informative restano ammesse.
  `source_span` non estrae BA dal prefisso di Bari e conserva la grafia SOURCE.
- Errori locali di revisione isolati; failure globali/provider espliciti.
  Retry separati persistenti, massimo due tentativi per fase/candidate;
  batch 12/6 e ciclo 36 passi/600 s preservati. Fino a sei chiamate modello per
  resolve completo, nessuna chiamata per singolo field o riparazione illimitata.
  UI/parser/renderer/orchestrazione chat invariati da questo intervento;
  grouped collegato al contesto di sezione senza riprogettazione.

**Verifiche finali effettive:** 46 regressioni nuove, **269 mirati passati** e
**1.192 backend completi passati** in quattro gruppi sequenziali
(385/343/398/66); Ruff e diff check passati. Provider simulati, DB/storage
temporanei; frontend invariato e non ritestato. La prima suite in un processo
era stata uccisa dall'OOM; non è conteggiata come passata. Nessun test disabilitato.

**Benchmark finale dopo la ricarica:** DeepSeek `deepseek-flash`, Qdrant locale
reale + BGE-M3, nuova sessione `a0122f66352848de94e14c94146c6419`, v59,
WAITING_FOR_USER / deferred_summary. Stesso `manifestazione-interesse.docx`
(hash `d125c7bf…`), Company KB e fonti Trapani in copie isolate.
**115/115 tentati; 9 RESOLVED/SOURCE; 45 MISSING; 31 AMBIGUOUS; 30 PENDING;
0 USER_PROVIDED/NOT_APPLICABLE; 76 DEFERRED** (sovrapposto agli stati).
**15 checkpoint/15 turni USER**, soltanto SKIP numerati, 52 slot complessivi,
media **3,4667**. Tutti e nove i SOURCE prima del primo checkpoint.
17 resolve, 51 chiamate resolver, 335,8 s; zero failure/resume, codice congelato.
Nessun valore manuale, nessun READY/DOCX forzato.

Gli otto valori di `p75.s0–s8` (Fax escluso) sono esattamente quelli richiesti:
Mapi Ingegneria S.r.l.; Via Giovanni Amendola 172/C; Bari; 70126; BA;
IT01234567890; +39 080 000 2040; mapi.ingegneria@pec.demo.
Tutti con SOURCE e applicability=true/SOURCE, tipologia attestata dalla visura.
Fax MISSING. Il nono SOURCE è PEC comunicazioni `p107.s0`.
Comune/CAP/Provincia inizialmente MISSING per SOURCE fuori bucket → RESOLVED al
secondo tentativo SOURCE; interpretation fermo a uno. Nessun counter oltre due.
30 slot della tabella t5 MISSING/PAST_SERVICE; otto slot firmatario p12 MISSING.
Zero proposte current→past o placeholder nel benchmark, zero valori errati accettati.
Replay negativo separato sul codice finale: una chiamata DeepSeek reale restituisce
facts=[], **due offerte di importi correnti respinte**; in RAM senza modello
**due CIG placeholder respinti**. Non sommare il replay alle metriche della sessione.

**Limiti residui:** 30 PENDING (24 condizioni non ancorate alla sezione FORM,
5 review indipendenti assenti, un estratto strutturale non presente). Non vengono
chiesti come valori USER. 76 field chiaribili sono rinviati in 52 slot; SKIP non
fornisce dati. Alcune condizioni del ramo dei prestatori esteri sono abbreviate
al riferimento normativo mentre il qualificatore estero resta nel contesto FORM:
nessuna SOURCE=true applicata a quel ramo, ma la condizione/questione richiede
riesame prima di dichiarare completa la gestione dei qualificatori.

Il codice è identico a quello dei **269 mirati/1.192 backend già passati** prima
della ricarica; la suite non è stata ripetuta per il solo benchmark. Ruff e diff
check rieseguiti e passati. Nessuna modifica al codice durante/dopo la prova.
UI/parser/renderer/orchestrazione e counter non cambiati in questa ripresa.

**Prova precedente, conservata:** sessione `6846e0553a74406f9c5937a9f46e9904`,
v39 FAILED/402, 100 tentati/0 SOURCE/0 checkpoint; non riaperta o alterata.
La precedente intermedia `f9346167a6f54712a3fb14b25c5a6bec` aveva verificato otto
valori ma non era il codice finale; ora il risultato è confermato sulla versione
finale. Tutti gli archivi precedenti conservati.

**Prossimo passo minimo:** diagnosi dei 30 PENDING e dei qualificatori abbreviati
nelle condizioni, separata dal benchmark concluso. Non aumentare retry né chiedere
valori di candidate non interpretati. Per finire il modulo servono chiarimenti
reali su alternative applicabili, firmatario, Fax e servizi pregressi documentati.
Nessuna nuova implementazione avviata dopo il benchmark.
Nessuna migrazione/reindicizzazione dei dati utente; sessioni legacy non riscritte.
Sessione originale dell'app `85daf575481244cd934911c42b3567f4` invariata alla v77;
README/start preservati byte per byte, testo locale precedente conservato sotto.
Report con tracce, query, evidence, confronto PRIMA/DOPO e limiti:
[manifestazione-interesse, 8 ottobre](docs/test-reale-manifestazione-interesse-2026-10-08.md).
Audit finale ignorato: `backend/data/compilation-audit/semantic-slots-20261008-ready/`;
precedente 402 in `semantic-slots-20261008-canonical/`. Snapshot dei documenti prima
della ricarica in `ready/checks/*.before`; STATUS prima dell'intervento semantico
in `canonical/checks/STATUS-before.md`.

## Storico: retry separati — 7 ottobre 2026

Completato il fix mirato sopra `a5e2e2e`, **senza commit/push**. Conservate
integralmente le modifiche locali precedenti ad avvio, README, ambiente e
progetti demo; README/start invariati rispetto all'inizio dell'intervento.

- `analysis_attempts`: interpretazione senza requirement; `source_attempts`:
  retrieval/proposta/validazione di requirement interpretati. Dizionari
  persistenti nel workflow JSON, massimo due tentativi per fase/candidate.
- Batch automatici omogenei; retry SOURCE conserva requisito/applicabilità,
  senza riclassificazione. Dopo interpretazione valida, revisione `source_start`
  prima del retrieval: riserva solo i tentativi SOURCE pertinenti e conserva
  esiti FORM. Item validi del batch conservati, errori locali isolati; failure
  globali/provider e controllo delle revisioni preservati.
- `reopen_phase_attempts`: una conferma di applicabilità riapre soltanto la
  fase necessaria, anche per review senza requisito dopo due interpretazioni.
  SKIP/UNKNOWN/PAUSE/RESUME preservati; budget 12/6 e 36 passi/600 s invariati.
  Sessioni legacy conservano budget speso, senza migrazione/reset automatico.
  UI/parser/renderer/gate SOURCE e grouped non riprogettati.

**Verifiche finali effettive:** 27 nuove regressioni (FTS5/Qdrant dove previsto),
211 mirati finali, **1.146 backend completi passati in 302,18 s**, Ruff e diff
check passati. Provider simulati, DB/storage temporanei; frontend non ritestato.
Le esecuzioni precedenti (280/103 mirati, suite 1.142 passata, suite 1.144 con
2 timeout ambientali poi passati al riesame) sono storiche, non l'esito finale.
Un test finale ha riprodotto il blocco del reset per review senza requisito:
corretto dopo il primo benchmark, test/suite e benchmark nuovo rieseguiti.
Nessun codice modificato durante nessuna delle due prove reali.

**Benchmark reale finale:** DeepSeek `deepseek-flash`, Qdrant locale + BGE-M3;
nuova sessione `382b44b883524bc1a908d4b8515a36e2` in archivio isolato. Dati
dell'app preservati. Company/General KB coerente con la locale e SOURCE
bando/disciplinare Catanzaro. DOCX corrente 279 candidate, hash `5b3ad083…`,
diverso dallo storico `aeb1bda3…` non recuperabile. Indice iniziale standard:
timeout e Ollama OOM; preparato a un frammento per richiesta, stessi hash,
metadati e filtri; riconciliazione ordinaria 214 chunk/1024 dimensioni,
zero aggiornamenti pendenti. Archivio/indice riusati nella nuova prova.

Finale: **279 processati; 17 RESOLVED/SOURCE formali; 0 USER_PROVIDED;
6 NOT_APPLICABLE (tutti non-field/FORM); 123 MISSING; 10 AMBIGUOUS;
123 PENDING; 129 DEFERRED** (disposizione sovrapposta agli stati).
34 checkpoint/34 turni USER, solo SKIP, media 3,79412 chiarimenti;
17 risolti prima del primo checkpoint. 69 passi automatici, counter entro due;
61 claim interpretazione, 8 SOURCE e 29 transizioni verificati: zero consumi
incrociati. Sei output misti conservano gli item validi. Caso positivo reale:
`t25.r4.c1` MISSING al SOURCE attempt 1 («SOURCE non ammessa») → RESOLVED/SOURCE
al attempt 2, interpretation fermo a 1. Fine `deferred_summary`,
WAITING_FOR_USER, auto_continue=false; nessun READY o DOCX forzato.

**Qualità ancora insufficiente:** i cinque field iniziali NON risolti nella
prova reale (forma PENDING per name parafrasato, altri MISSING con Company fuori
bucket); test software dei cinque valori passati. Ingegneria raggiunta:
denominazione/forma/sede SOURCE; direttore/qualifica MISSING, ordine e 8421
PENDING per person_role non grounded. CCIAA/numero iscrizione completo e data
abilitazione assenti dalla KB. Almeno un RESOLVED errato: stazione appaltante
per denominazione società tra professionisti `t31.r0.c1`. Nei 12 RESOLVED del benchmark
preliminare comparivano anche REA per Registro Imprese/CCIAA e stazione appaltante
per consorzio: non sono risultati corretti né modifiche dei gate. Non equiparare
RESOLVED a dato giusto; confronto storico limitato da DOCX/corpus diversi.

**Prossimo passo minimo:** query/bucket Company del primo batch, grounding
name/person_role di direttore/ordine/8421 e falso positivo di soggetto `t31.r0.c1`;
intervento distinto, senza rifare counter o grouped. Report con campi, metriche,
confronto, limiti e acquisizioni:
[retry separati e benchmark reale](docs/test-reale-retry-phases-2026-10-07.md).
Audit ignorati da Git: `backend/data/compilation-audit/retry-phases-20261007-final/`;
archivio preliminare `retry-phases-20261007/` conservato (12 SOURCE, 32 checkpoint,
media 3,72, zero valori USER). Codice/DOCX invariati in ciascun benchmark.

## Avvio e dipendenze — 7 ottobre 2026

Su richiesta dell'utente, `start.sh` installa le dipendenze frontend con
`npm ci --include=dev --include=optional` se `node_modules` manca o
`npm ls --all --include=dev --include=optional` rileva pacchetti mancanti/non
validi. Sincronizza il backend con `uv sync --locked` prima di avviare i servizi;
Uvicorn usa poi `uv run --locked --no-sync`. Un errore di installazione interrompe
l'avvio. Lockfile preservati. Su ulteriore richiesta, installazione automatica
locale di `uv` in `.tools/uv` tramite installer ufficiale senza modificare il
profilo shell, e Node.js 22.23.3 con npm in `.tools/node` tramite archivio
ufficiale verificato SHA-256. Bootstrap Node anche per versione incompatibile
o npm assente/non funzionante; Linux/macOS x64/arm64. Servono curl o wget e
strumenti di estrazione/checksum; niente sudo. README e help aggiornati.
Nessuna migrazione o reindicizzazione.

Verifiche effettive: `bash -n start.sh`, `./start.sh --help`, `git diff --check`;
cinque scenari in directory temporanee con comandi npm/uv simulati: dipendenze
assenti, presenti, incomplete, errore npm e errore uv. Tutti passati. Nessun
download reale o avvio dei servizi effettuato in questa verifica. Bootstrap
verificato anche con otto scenari isolati e download/strumenti simulati:
strumenti presenti, mancanti, Node vecchio, npm assente, checksum errato,
download fallito, npm ci fallito e uv sync fallito; tutti passati. Il primo
tentativo del test isolato mancava di gzip nel PATH di prova, corretto nel
harness prima dell'esecuzione finale. Il punto di
ripresa della compilazione descritto sotto resta aperto.

## Punto di ripresa

### Progetti demo creati — 7 ottobre 2026

Su richiesta dell'utente, esaminati `demo-documents/bandi/`, metadati `fonti.json`
e contenuto degli avvisi/bando; creati tramite POST `/api/projects` tre progetti
con titolo e descrizione documentati:
- `catanzaro-direzione-lavori-e-sicurezza`: Catanzaro - Direzione lavori e sicurezza;
- `minervino-di-lecce-elenco-sia`: Minervino di Lecce - Elenco SIA;
- `trapani-green-progettazione-e-direzione-lavori`: Trapani Green - Progettazione e direzione lavori.

Descrizioni marcate come casi didattici con dati aziendali simulati. Prima della
creazione l'elenco progetti era vuoto; verificati titoli e descrizioni tramite
GET dei singoli progetti dopo il salvataggio e totale finale pari a tre.
Questa richiesta riguardava la creazione dei progetti: fonti e moduli di gara
non caricati nei nuovi workspace. Fixture originali e profili AI preservati.
Nessuna modifica al codice, migrazione o reindicizzazione; diff check passato.

### Ambiente operativo locale — 7 ottobre 2026

Su richiesta dell'utente, installato **Ollama 0.40.0** e scaricato **BGE-M3**;
nessuna aggiunta a `start.sh` in questo intervento. Binari/librerie in
`.tools/ollama`, modelli in `.tools/ollama-models` (esclusi da Git). Comando
`ollama` disponibile tramite link in `~/.local/bin`; servizio systemd utente
`~/.config/systemd/user/ollama.service`, abilitato e attivo su
`127.0.0.1:11434`. Un solo modello caricato e una richiesta parallela per
contenere la memoria sulla macchina da circa 4 GB; inferenza CPU rilevata.
Verifica/riavvio: `systemctl --user status ollama` / `systemctl --user start ollama`.

Configurata tramite API normale la ricerca **Qdrant locale + bge-m3**;
indicizzazione effettiva di 17 frammenti, 1024 dimensioni, senza cancellazioni.
Le dipendenze backend sono state sincronizzate con `uv sync --locked --offline`;
Node 22.23.3 e controllo dei pacchetti frontend disponibili.
All'inizio non c'erano profili AI; durante l'intervento è comparso il profilo
utente **DeepSeek v4 / deepseek-flash**, lasciato predefinito. Installato anche
**Qwen3 1.7B**, profilo locale alternativo con contesto 4096, senza sostituire
DeepSeek. Modello piccolo di riserva: non valutato per moduli complessi.

Verifiche reali effettive, distinte dai test simulati sopra:
- API health backend, servizio Ollama e inventario modelli;
- API retrieval/check: embedding BGE-M3 da 1024 dimensioni e Qdrant disponibili;
- API retrieval/index: 17 frammenti aggiornati, zero eliminati;
- API ai/check: Qwen3 disponibile per generazione;
- query reale Qdrant/BGE-M3 su fonte sintetica in DB/storage temporanei;
- compilazione DOCX reale con DeepSeek di un solo campo sintetico:
  denominazione inserita correttamente, un campo scritto e zero irrisolti;
- risposta strutturata reale Qwen3 via adapter applicativo e schema JSON;
- `git diff --check` passato.

Nessun progetto o modulo di prova creato nel DB dell'app, nessuna credenziale
riportata. Queste prove verificano l'ambiente e un caso minimo: non attestano
il completamento dei moduli reali o la qualità del workflow conversazionale.
README aggiornato per distinguere embedding, generazione e servizio separato.
Il prossimo intervento software resta quello descritto sotto.

### Storico del punto di ripresa precedente al fix dei retry

La separazione indicata sotto come non implementata è ora completata nella
sezione «Ripresa attuale»; le prove seguenti restano storiche.

**Intervento sui chiarimenti raggruppati interrotto su richiesta dell'utente
per salvare il lavoro con un commit locale. Non considerarlo completato.**

Implementati nel workflow: raccolta persistente dei chiarimenti, checkpoint
dopo il lavoro automatico disponibile, priorità delle condizioni condivise,
massimo quattro slot per messaggio, planner semantico senza field_id,
aggiornamenti parziali, UNKNOWN/SKIP per elemento e pausa/ripresa del gruppo.
Metriche `chat.metrics`: automatic_resolved, user_required_fields, user_turns.
Due tentativi automatici per candidate, batch normale massimo 12, retry massimo
6, ciclo massimo 36 passi/600 secondi. Gli output strutturati invalidi sono
interamente rifiutati e recuperabili entro quel budget; provider/timeout e altri
errori tecnici conservano FAILED. Motore SOURCE/parser/renderer non modificati.

**Verifiche effettive sull'ultimo codice:** 276 test backend mirati, 1119 backend
completi, Ruff; 83 test frontend, lint/build; sei E2E browser desktop/mobile,
inclusi reduced-motion e chiarimenti raggruppati. Diff check passato.
I test software usano provider simulati e database temporanei; non attestano
il completamento del benchmark reale.

**Prove reali deepseek-flash, codice congelato durante ciascuna esecuzione:**

- Sessione `45474e57f4cf4b0f879296c097f06a91`, conversazione
  `conv-eece71eeb16a4c03`: cinque dati aziendali richiesti RESOLVED/SOURCE al
  primo passo senza USER; prosegue senza chiedere subito la procura. Dopo una
  ripresa normale arriva a 22 RESOLVED, poi un errore strutturato interrompe
  prima del checkpoint. Nessuna misurazione reale completa dei gruppi/turni.
- Dopo il recupero bounded degli output invalidi, nuova sessione
  `8361b0e782aa49d78f9ec45cff677a94`: 12 RESOLVED, 32 MISSING, 3 AMBIGUOUS,
  232 PENDING, zero valori USER. Messa in pausa via chat «basta»: v53,
  WAITING_FOR_USER + user_paused=true, domanda null e auto_continue=false.
  Resolve tardivo respinto con 409: pausa preservata.
- **Bug residuo:** il retry da sei mescola PENDING con errori di interpretazione
  e MISSING già cercati con errori SOURCE. Un JSON invalido dei primi consuma
  il secondo tentativo anche dei secondi. Nella seconda prova CF/PIVA restano
  MISSING; nella prima sono RESOLVED. Non dichiarare verificata la stabilità
  dei cinque dati nel workflow finale né completato il confronto dei turni.
- Originale invariato; nessun DOCX generato. Audit ignorati da Git in
  `backend/data/compilation-audit/grouped-clarifications-20261007/` e
  `grouped-clarifications-20261007-final/`: non inclusi nel commit.

**Prossimo passo:** separare la selezione dei retry per fase/stato
(interpretazione PENDING vs proposta SOURCE MISSING), senza cambiare il motore
SOURCE/gate. Aggiungere una regressione: candidate non interpretabile non deve
consumare il retry di un altro candidate con SOURCE valida. Questa separazione
**non è ancora implementata**. Poi test mirati/Ruff/diff e nuovo benchmark
reale con conversazione pulita, form 153/stessa KB, senza dati aziendali USER:
misurare checkpoint/gruppi/turni/unresolved, verificare cinque dati e direttore
tecnico. Non modificare codice durante il benchmark.

## Collegamento SOURCE — intervento precedente del 7 ottobre

Corretto il collegamento **candidate → SOURCE → bucket allowed → proposta →
validazione → RESOLVED**, senza modificare UI, parser, renderer, routing
conversazionale o RAG FORM/SOURCE/MIXED generale. Nel benchmark finale con
**deepseek-flash reale**, nuova sessione
`46d5be7dcf444b18ac519d7bf55d1680`, v5, sono persistiti tutti e cinque i criteri
richiesti: operatore economico, forma giuridica, sede legale, CF operatore e PIVA
→ **RESOLVED / SOURCE**, da Company KB, senza valori USER.
Necessario **un resolve esplicito aggiuntivo della sede** dopo un estratto
respinto; non presentare il risultato come successo completo al primo passo.
Diagnosi, raw prima della modifica, query, bucket e benchmark:
[test-reale-candidate-source-2026-10-07.md](docs/test-reale-candidate-source-2026-10-07.md).

### Cause concrete e modifica SOURCE della compilazione

- Per `t0.r5.c1` e `t0.r6.c1`, il vecchio bucket conteneva quattro chunk di
  `avviso.pdf`. `generalita-mapi.md` / Company KB, chunk -43, era nel pool
  del batch, recuperato per altri candidate, ma non ammesso per questi due.
  Il matcher proponeva la forma giuridica dalla SOURCE corretta e il gate
  respingeva «SOURCE non ammessa per questo candidate».
- L'operatore aveva anche un secondo falso negativo: la label FORM non era
  riconosciuta come richiesta dell'identità/ragione sociale. La rimozione di
  entrambi i token «operatore/economico» rendeva sempre falsa l'associazione
  letterale, anche con una prova SOURCE corretta ammessa in una copia diagnostica.
  Due riproduzioni reali read-only eseguite prima di modificare codice; non
  confuse con i raw storici non persistiti dal prodotto.
- Nuovo helper `compilation_sources.py`: una sola pianificazione semantica
  batch deriva cluster e fino a tre nomi equivalenti della proprietà da
  requirement/context. I contesti sono deduplicati; nessun valore proposto,
  dizionario di campi demo, nome aziendale/file/chunk hardcoded.
- Query brevi sulle proprietà. I risultati di un altro cluster entrano nel
  bucket aziendale solo attraverso una proprietà locale pertinente della
  SOURCE. Il validator richiede valore e intestazione nella stessa relazione
  `intestazione: valore`; non basta che la label compaia altrove nel profilo.
  Il requisito FORM originale resta grounded e invariato. Gate personali,
  SOURCE attuali/progetto/role, General KB, validatore DOCX e rivalidazione
  alla finalizzazione restano attivi. FORM e USER non diventano SOURCE.
- Quote/valori normalizzati tornano alla grafia letterale della fonte tramite
  soli Unicode/case/whitespace, senza fuzzy matching o riscritture del contenuto.
  Ricerca e bucket conservano source_names, query, chunk recuperati/allowed;
  evidence conserva file/chunk, scope, categoria e role.
- Budget: 12 candidate/passo; max tre chiamate LLM complessive per passo;
  max sei cluster di quattro requisiti, due query/cluster, 12 query totali,
  quattro evidence/cluster, pool max 24 chunk, allowed max otto/candidate.
  Un fallimento del planner conserva fallback letterale e coverage esplicita,
  senza retry aggiuntivi o chiamate per singolo campo.
- Nessuna migrazione/reindicizzazione né modifica SQL manuale. I MISSING
  preesistenti restano tali finché riesaminati tramite API normale.

### Benchmark reale SOURCE e limiti

- Progetto `minervino-di-lecce-elenco-sia`, form 153,
  `domanda-partecipazione.docx`; Qdrant locale + BGE-M3/Ollama;
  configurazione reale DeepSeek / `deepseek-flash`.
- Nuova conversazione `conv-43455f51f75b4f2c`, sessione sopra: POST create v1,
  resolve dei cinque candidate v3 → quattro RESOLVED e sede MISSING perché
  quote/valore non letterali; un nuovo resolve della sola sede → v5,
  **cinque RESOLVED/SOURCE, zero USER_PROVIDED**. Tutti dalla fonte demo
  `generalita-mapi.md`, file -7, chunk -43, scope global / category company.
- Valori: Mapi Ingegneria S.r.l.; Societa a responsabilita limitata;
  Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia;
  CF e PIVA didattici IT01234567890. Nessuna inserzione manuale di questi dati.
  Stato riletto via GET dopo la mutazione; gli altri quattro non sono stati
  resettati dal riesame della sede. Codice congelato durante il benchmark.
- Prova precedente con primi 12 candidate: quattro campi lasciati PENDING
  dal classificatore per label parafrasate, prima del SOURCE retrieval.
  Sessione nuova `2c1acae1e71c40e19989c28588e836d1`: tutti cinque risolti
  dopo un riesame mirato dei quattro PENDING. **Classificatore non corretto**
  in questo intervento: fuori dal collegamento SOURCE richiesto.
- Finale: 5 RESOLVED / 274 PENDING, sessione CREATED, nessun DOCX generato.
  Non è un test del completamento di tutti i 279 candidate né della UX.
  Restano falsi negativi conservativi di classificazione/quote: non promettere
  che un unico passo automatico risolva sempre i cinque campi.
- Originale invariato, SHA-256
  `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
  Sessioni precedenti preservate; acquisizioni ignorate da Git in
  `backend/data/compilation-audit/candidate-source-20261007/`.

### Verifiche effettive dell'intervento SOURCE

- Mirati finali: **250 passati**, con DB/storage temporanei e provider simulati:
  `uv run --locked pytest -q tests/test_compilation_sources.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_compilation_chat.py tests/test_compilation_controls.py tests/test_compilation_active_question.py tests/test_compilation_conversation.py`.
  Nuove regressioni SOURCE: **12 passate**, inclusi FTS5/Qdrant, alias generici,
  riassociazione limitata, valori di proprietà errate respinti, SOURCE condivisa
  senza contaminazione, provenance/chunk e rivalidazione alla finalizzazione.
- Backend completo finale: **1079 passati**, `uv run --locked pytest -q`;
  `uv run --locked ruff check .` e `git diff --check` passati.
  I tentativi software intermedi hanno segnalato errori nella selezione delle
  coorti della nuova fixture, corretti prima di queste esecuzioni finali.
- Benchmark reale distinto dai test software: normale HTTP, deepseek-flash,
  retrieval corrente e persistenza riletta; nessun provider simulato, valore
  USER o manipolazione manuale DB. Test frontend/browser/lint/build frontend
  non rieseguiti: UI e contratti non modificati da questo intervento.
- Nessun commit/push o ripristino delle modifiche locali già esistenti.

**Prossimo punto:** verificare nel normale flusso chat la stabilità della
classificazione prima del retrieval. Il fix SOURCE soddisfa i cinque criteri
persistiti nel benchmark circoscritto, con il riesame dichiarato; il completamento
automatico dell'intero modulo e la materializzazione finale restano da verificare.

## Chiarimento della domanda attiva — intervento precedente del 7 ottobre

Corretto il contratto delle **risposte a una singola domanda attiva** della
compilazione. **Entrambe le negazioni sono state verificate con deepseek-flash
reale**: «No, il sottoscrittore non agisce come procuratore.» e «no» producono
CONDITION_FALSE, senza field_id, senza retry e senza errori schema; il backend
aggiorna soltanto il target noto a NOT_APPLICABLE / USER e passa al prossimo
problema. Report completo con prompt, schema, raw prima/retry/dopo e transizioni:
[test-reale-active-question-2026-10-07.md](docs/test-reale-active-question-2026-10-07.md).

### Causa e modifica del chiarimento singolo

- Riproduzione prima della modifica, quattro chiamate reali su snapshot letto
  dalla sessione `d08866e079464d34bd2d2fc689392be8` v3, senza modificarla:
  il modello capisceva la negazione, ma copiava `id` da `fields[].id` del contesto
  al posto del richiesto `field_replies[].field_id`. Due errori identici in entrambi
  i tentativi: campo obbligatorio mancante e proprietà extra non ammessa. Il vecchio
  retry non indicava le cause precise; DeepSeek usa JSON mode, che non vincola
  i nomi delle proprietà dello schema Pydantic.
- `ActiveQuestionPlan` richiede la sola decisione semantica: VALUE,
  CONDITION_TRUE/FALSE, UNKNOWN, SKIP, REFUSE, PAUSE, CLARIFY; valore letterale,
  normalizzazione deterministica e breve rationale quando appropriati. Né schema
  né contesto single-field espongono ID di campo/sessione/versione al modello.
  `CHAT` permette una nuova domanda documentale e torna al routing esistente,
  senza un secondo planner. Il modello non sceglie il destinatario.
- Il backend lega l'azione alla domanda del proprio snapshot persistito, verifica
  revisione/progetto/conversazione e riusa i service della sessione. FALSE conserva
  motivo USER e valore nullo; TRUE riapre il candidate prioritario per SOURCE,
  senza risolvere un valore. VALUE conserva grounding e validatore DOCX.
  Alternative esplicite e CLARIFY non cambiano i campi. I controlli e i differimenti
  precedenti restano validi; nessuna nuova keyword per interpretare la condizione.
- Shortcut solo con workflow abilitato e un target coerente. Più destinatari,
  domanda assente o sessione sospesa/non conversazionale usano il percorso
  generale; nessuna selezione arbitraria. Una chiamata per messaggio e un solo
  retry con gli errori precisi. Nessuna modifica a schema DB, parser, renderer,
  RAG, UI o contratti frontend; nessuna migrazione/reindicizzazione necessaria.

### Verifiche effettive di questo intervento

- Mirati finali: **252 passati** con DB/storage temporanei e provider simulati:
  `uv run --locked pytest -q tests/test_compilation_active_question.py tests/test_compilation_conversation.py tests/test_compilation_controls.py tests/test_compilation_chat.py tests/test_form_retrieval.py`.
- Backend completo finale: **1067 passati**, `uv run --locked pytest -q`;
  `uv run --locked ruff check .` e `git diff --check` passati.
  Frontend/browser/lint/build frontend non rieseguiti: non toccati in questa modifica.
- Benchmark finale reale su due nuove conversazioni, avvio/resolve tramite HTTP,
  chiarimento attraverso la stessa API FastAPI via ASGITransport per catturare i
  raw, senza provider/risposte simulate; normale persistenza, riletta via HTTP:
  - negazione completa: sessione `5e1a6b1fcf8a4aa3a94188d89330077b`,
    conversazione `conv-59cdc5c0155d4eaa`, v5 → v6;
  - «no»: sessione `514078f1a6f5493a9164bd38ff809fa4`,
    conversazione `conv-379b5f72d59344f0`, v3 → v4.
  In entrambe target `t0.r4.c1` → NOT_APPLICABLE / USER, nessun valore fattuale,
  altri field invariati; domanda successiva «Operatore economico». WAITING_FOR_USER
  su quel prossimo problema, senza generazione implicita o loop sulla procura.
- Prima sessione: il classificatore iniziale aveva lasciato la procura PENDING
  per una label non grounded. Un resolve mirato tramite API esistente ha raggiunto
  la domanda; nessun dato/condizione imposto con SQL o valori USER. Seconda sessione:
  domanda raggiunta nel primo passo automatico. Questo limite è registrato, non
  nascosto né corretto durante il benchmark.
- Originale e codice applicativo invariati durante la prova (SHA-256); sessione
  iniziale della diagnosi e sessioni precedenti conservate. Nessun commit/push.
  Acquisizioni locali escluse da Git:
  `backend/data/compilation-audit/single-active-field-20261006/`.

**Prossimo punto:** il chiarimento di applicabilità singolo è corretto e provato
con il provider reale. Restano da discutere/correggere, su incarico esplicito, i
blocchi del classificatore e della coverage SOURCE descritti nel test precedente.
La compilazione automatica completa fino al DOCX non è ancora verificata: non
confonderla con l'esito positivo di questo intervento circoscritto.

## Test reale E2E precedente — 6 ottobre (storico)

Eseguito il **test reale E2E con deepseek-flash**, richiesto il 6 ottobre:
**compilazione automatica solo parziale**, senza correggere codice. Diagnosi e
registro: [test-reale-compilation-session-2026-10-06.md](docs/test-reale-compilation-session-2026-10-06.md).
Il workflow conversazionale implementato sotto resta lo stato software precedente;
gli esiti dei test simulati non vanno confusi con questa prova reale.

### Risultato reale e blocchi ancora da correggere

- Progetto `minervino-di-lecce-elenco-sia`, modulo originale ID 153,
  `domanda-partecipazione.docx`, 279 candidate. Profilo reale DeepSeek /
  `deepseek-flash`; Qdrant locale + BGE-M3/Ollama. Avvio dalla chat con mention
  strutturata e «me lo compili?», nuova conversazione `conv-2f20346327a544c7`.
  Sessione `c849656d4e2e46ccab0d42ecd3d13c18`, finale v20 / FAILED.
- Due passi completati: 24 candidate con esito persistito. Altri 12 candidate
  nel terzo gruppo fallito, tentato due volte con una sola ripresa dalla chat.
  Tre RESOLVED/SOURCE: sede legale, codice fiscale operatore e partita IVA,
  da `generalita-mapi.md`, Company KB globale, chunk -43. Identificativo fiscale
  didattico `IT01234567890`, già presente nelle fonti; nessun valore standard
  inserito manualmente per far riuscire il benchmark.
- Stato grezzo: 268 PENDING, 3 RESOLVED, 2 MISSING, 6 AMBIGUOUS; zero
  USER_PROVIDED/CONFLICTING/NOT_APPLICABLE. Gli otto problemi sono differiti:
  nel rapporto richiesto diventano DEFERRED, senza cambiare gli stati DB.
- Denominazione e forma giuridica esistono nella KB e vengono proposte dal
  matcher usando il chunk -43, recuperato per altri field. Il loro bucket
  ammesso contiene però soltanto `avviso.pdf`: i gate rifiutano correttamente
  quelle proposte con «SOURCE non ammessa per questo candidate». Non abbassati
  i filtri per far passare il test. Altri candidate restano PENDING per label
  parafrasate o person_role fuori dal form_quote; SOURCE non viene ricercata.
- Terzo passo: HTTP 502 «Output strutturato della risoluzione non valido»;
  ripresa normale dalla stessa conversazione, stesso fallimento. Riproduzione
  read-only del classificatore con provider reale e stesso batch: cinque
  decorative restituiscono `form_quote=""`, respinto dal minimo due caratteri
  dello schema; fallisce tutto il gruppo prima del salvataggio. Nessuna
  correzione di schema, prompt, output o sessione durante la diagnosi.
- UNKNOWN/SKIP, pausa con «basta», refresh e «riprendi» stessa sessione
  osservati nel percorso reale. Condizione della procura chiesta prima degli
  estremi. In due conversazioni aggiuntive, stesso modello/modulo/fonti:
  incertezza -> UNKNOWN senza valori; «Sì oppure no.» -> chiarimento senza
  modifiche ai field. **«non sono procuratore» e «No» falliscono nel planner**,
  non rendono NOT_APPLICABLE. Riproduzione reale read-only: `field_replies`
  contiene `id` anziché `field_id`, anche dopo retry; parsing respinto.
  Sessioni aggiuntive lasciate in pausa tramite normale «basta».
- Nessuna READY/GENERATED, nessuna bozza incompleta o finalize forzato.
  Materializzazione nel DOCX e input di un valore USER_PROVIDED non raggiunti:
  non dichiararli verificati. Originale immutato, hash prima/dopo e BLOB della
  sessione coincidenti. Persistenza verificata anche dopo riavvio dei servizi.
- Registro completo CSV/JSON, revisioni, evidenze e riproduzioni grezze in
  `backend/data/compilation-audit/real-e2e-deepseek-flash-20261006/`, escluso da Git.
  Le risposte grezze LLM dei resolve originali non sono persistite dal prodotto:
  le riproduzioni isolate sono indicate come nuove chiamate, non come output
  storici. Nessuna credenziale nel report.

Verifiche di questo test: browser Chromium su frontend/backend reali, API e
revisioni reali; letture SQL esclusivamente `mode=ro`, confronto hash e stato
API/DB, riproduzioni isolate con provider reale senza mutazioni delle sessioni,
controllo del diff e degli artefatti. Nessuna suite con provider simulati, Ruff,
lint o build rieseguita: nessuna modifica applicativa. Non confondere i numeri
software conservati sotto con verifiche nuove. Nessun commit/push; modifiche
locali precedenti preservate.

**Prossimo punto del test precedente (storico):** discutere questa diagnosi prima di correggere i contratti
classificazione decorative / risposte USER e la copertura SOURCE dei campi
standard. Poi ripetere il percorso reale completo fino al DOCX. Il RAG generale,
parser e renderer non sono stati modificati in questo test. Non riprendere
automaticamente le sessioni FAILED o forzarne i field tramite SQL.

### Stato software del workflow prima del test reale

Corretto il **workflow conversazionale della compilazione**: risposte di controllo,
pausa/ripresa persistenti, differimento senza loop e condizioni di applicabilità
prima del valore. Intervento circoscritto ai service/routing di compilazione e alla
vista dello stato; parser DOCX, renderer e RAG FORM/SOURCE/MIXED non ridisegnati.
Le milestone precedenti e i loro test sono conservati sotto come storico.

### Diagnosi concreta del test reale

Lettura **soltanto read-only** del DB locale: il field `t0.r4.c1` «Estremi procura»
era MISSING e conservava già `condition="se procuratore"`; il requisito FORM
includeva «(se procuratore) estremi procura (notaio, repertorio, raccolta)».
Il campo sulla carica del sottoscrittore era ancora PENDING: non era stata
stabilita la condizione. Il problema non era il parser:

- `apply_matches` rendeva MISSING qualsiasi campo ricercato senza valore;
  `chat_view` chiedeva la condizione soltanto per AMBIGUOUS, ignorandola in MISSING.
- Il planner non prevedeva UNKNOWN/SKIP/PAUSE. Le risposte non interpretabili
  salvavano un chiarimento e il selettore riprendeva sempre `issues[0]`.
- «basta» produceva reply della chat normale: nessuna mutazione della sessione.

### Correzione implementata

- Il planner esistente distingue semanticamente `compilation_control`, con
  `kind=unknown|skip|refuse|pause|resume`, `field_id` dove serve e `user_quote`.
  Rimane bounded (stesse chiamate/retry del planner), senza nuovo classificatore.
  Un piccolo guard per **messaggi interi inequivoci** («salta», «non lo so»,
  «basta», «riprendi», ecc.) evita che un errore del planner li trasformi in
  reply generiche o valori USER. Le parafrasi continuano a usare il routing
  semantico. Il guard richiede una sessione conversazionale e, per rinviare,
  un solo campo attualmente chiesto; non intercetta domande FORM normali.
- UNKNOWN/SKIP/rifiuto conservano status, valore, SOURCE/USER provenance e prove.
  `conversation_disposition` registra motivo, estratto USER, data e fingerprint
  dello stato significativo del campo. Non si inventano stati fattuali DEFERRED:
  il differimento riguarda la conversazione, non la disponibilità del valore.
- La proiezione esclude i problemi rinviati finché non cambia il loro stato
  significativo oppure l'utente ne chiede esplicitamente la revisione. Passa al
  prossimo problema o ai pending. Quando restano soltanto differimenti, mostra
  un riepilogo (max 5 nomi + conteggio), senza domanda individuale in loop.
  La sessione resta WAITING_FOR_USER e la finalizzazione completa rimane bloccata.
- Prima risposta ambigua/non valida: un chiarimento, senza cambiare campi.
  Seconda risposta non interpretabile sullo stesso stato: differimento e prossimo
  problema. Chiarimenti identificati per campo/tipo; vecchi testi non identificati
  non sovrascrivono una domanda corretta sulla condizione.
- PAUSE salva `chat_workflow.user_paused`, toglie la domanda attiva e impedisce
  i passi automatici, anche dopo refresh. Il composer può inviare «basta» durante
  analisi. La pausa invalida il claim/versione: un risultato tardivo non può
  sovrascriverla. Il provider già in volo può terminare, ma il suo risultato
  viene scartato. «riprendi» rinnova un ciclo della **stessa** sessione.
- Applicabilità: riuso di `field.condition`, già grounded nel FORM. UNKNOWN
  chiede la condizione prima del valore, anche nei vecchi MISSING. Il matcher
  SOURCE può proporre prove esplicite di condizione vera/falsa nello stesso batch:
  ID SOURCE ammesso, estratto/asserzione letterale, parole del predicato e polarità
  locale verificati conservativamente. Un estratto non può omettere una negazione
  o ipotesi precedente nella clausola SOURCE; una conferma USER parziale non può
  rimuovere l'incertezza del messaggio. Assenza, ipotesi, FORM o valore dipendente
  non provano la condizione. Prove discordanti, anche con vecchia exclusion,
  restano da chiarire. Pausa/ripresa conserva anche lo stato GENERATED e i download.
- USER «No»/negazione esplicita della condizione: solo field chiesto NOT_APPLICABLE,
  motivazione e provenance USER. «Sì»: applicabilità USER, field PENDING prioritario
  e nuova ricerca SOURCE prima di chiedere il valore. La condizione già grounded
  non si perde se il classificatore la omette nel retry. Nessuna esclusione di
  intere sezioni o inferenza automatica da forma giuridica.
- SOURCE pertinente + condizione vera + validatori DOCX -> RESOLVED; condizione
  vera senza valore SOURCE -> MISSING/domanda sul valore; falso -> NOT_APPLICABLE;
  sconosciuto -> AMBIGUOUS/domanda sulla condizione. Una risposta libera valida
  sul valore resta USER_PROVIDED, distinta da SOURCE.
- Nessuna tabella o migrazione nuova: dati nel JSON/revisioni esistenti. Conteggi
  di dominio mantenuti; `chat` aggiunge `paused_by_user`, `deferred` e riepilogo.
  API dello storico estesa compatibilmente con azioni paused/resumed/deferred.

### Verifiche di questo intervento

- Backend: **79 nuovi test** per controlli/applicabilità/differimenti, con provider
  simulati e DB/storage temporanei (FTS5/Qdrant dove applicabile). Test mirati
  su sessioni/conversazione eseguiti prima della suite backend
  finale completa: **1024 passati**. Ruff superato sullo stato finale.
- Frontend: **83 passati in 12 file**, inclusi SKIP/UNKNOWN, pausa/refresh/ripresa e
  invio di «basta» durante un passo in corso e negazione della condizione. Oxlint e build TypeScript/Vite passati.
- Browser Chromium: **8 passati**, API simulate, desktop/mobile e movimento
  ridotto; scenari compilation-chat, composer-model-menu, project-forms. Aggiunti
  salta/unknown/ripresa, pausa senza domanda dopo refresh, nessuna mutazione dei
  valori rinviati, oltre al flusso USER -> READY -> download. Frontend separato
  porta 5193; nessun uso del backend/storage locale dell'utente.
- `git diff --check` e controllo whitespace dei file nuovi superati. Nessun
  benchmark con provider reale: i test verificano il software, non DeepSeek/Gemma.

Comandi realmente eseguiti: `uv run --locked pytest -q tests/test_compilation_controls.py`,
`uv run --locked pytest -q tests/test_compilation_controls.py tests/test_compilation_conversation.py`,
`uv run --locked pytest -q tests/test_compilation_conversation.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py`,
`uv run --locked pytest -q`, `uv run --locked ruff check .`; frontend `npm test`,
`npm run lint`, `npm run build`,
`PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npm run test:e2e -- compilation-chat.spec.ts composer-model-menu.spec.ts project-forms.spec.ts`.

### Prova manuale e limiti residui

Riavviare backend/frontend aggiornati. Nessuna reindicizzazione necessaria;
nessuna modifica automatica ai DB/storage locali durante i test. La vecchia
sessione MISSING con condizione già registrata ora mostra la domanda di
applicabilità senza migrare i dati.

1. `@domanda-partecipazione.docx` + «me lo compili?» -> analisi -> condizione
   di «Estremi procura» -> «salta»: voce aperta con differimento SKIP, prossimo
   problema/analisi; riepilogo finale senza ripetizione immediata.
2. Stesso avvio -> condizione «se procuratore» -> «non sono procuratore»:
   NOT_APPLICABLE/USER per quel candidate, nessuna richiesta degli estremi.
3. «basta» -> pausa persistente senza domanda attiva -> refresh -> «riprendi»:
   stessa sessione/versione successiva, domanda o analisi dal punto conservato.
4. Confermare «Sì»: ricerca SOURCE del valore; se assente chiedere gli estremi,
   non inventarli. «non lo so» li lascia aperti, passando oltre.
5. «riassumilo» con mention resta FORM RAG, senza mutare la compilation.

Non c'è un motore generale di dipendenze: una condizione letterale per candidate,
nessuna propagazione automatica fra candidate/sezioni. La qualità dell'estrazione
semantica e delle parafrasi resta dipendente dal provider. I gate di applicabilità
sono prudenti e possono produrre falsi negativi; nessuna assenza SOURCE equivale
al falso. I rinvii non vengono riesaminati solo perché è stata caricata una nuova
fonte: serve ricerca/revisione esplicita o mutazione del field. READY non certifica
la completezza amministrativa. Vecchi conditional RESOLVED antecedenti a questo
intervento non sono riscritti automaticamente: riesaminarli esplicitamente.

**Prossimo punto:** ripetere il test reale con il provider scelto, soprattutto
controlli paraprasati e applicabilità sul sottoscrittore. Valutare successivamente,
con l'utente, eventuale raggruppamento dei chiarimenti. Non riaprire il RAG generale.
Preservate modifiche locali, inclusa `.env.example` eliminata; nessun commit/push.

## Milestone precedente: workflow conversazionale (storico)

È stato implementato il **workflow conversazionale di compilazione nella chat**, su
richiesta esplicita dell'utente. Supera la scheda tecnica manuale come esperienza
primaria. Un DOCX alla volta; parser, renderer e RAG FORM/SOURCE/MIXED restano
quelli già implementati. Non riaprire il RAG generale per proseguire la UX.

### Causa e soluzione

Il planner precedente poteva scegliere soltanto reply/retrieve; «me lo compili?»
finiva nel generatore RAG, mentre l'avvio della sessione era un'azione UI separata.
La compilazione reale e la risposta normale potevano quindi contraddirsi. La UI
esponeva inoltre ogni passo da 12 come un'operazione manuale dell'utente.

- Il planner esistente ora distingue anche compile, compilation_input,
  compilation_clarify e compilation_generate. Con mention strutturata + incarico
  passa al workflow prima del generatore RAG; il backend risponde «Certo. Analizzo
  il modulo e verifico le informazioni disponibili» e crea/riprende la coppia
  conversazione/form. Non è un elenco hardcoded di frasi. Domande informative
  sul modulo, dati o disponibilità restano FORM/SOURCE/MIXED.
- L'orchestratore frontend avanza **un passo per snapshot**; il backend autorizza
  ciascun passo con budget persistito: **36 passi / 600 secondi** per ciclo.
  Rimangono max 12 candidate e max 3 chiamate LLM per passo (108 per ciclo,
  oltre al planner utente e agli embedding). Il limite temporale impedisce nuove
  ammissioni; un passo già partito conserva timeout 180 secondi. Stop su domanda,
  READY, FAILED, errore, budget o mancato progresso dopo visita dei pending.
- GET/refresh non rinnova budget. Al limite una sola azione di alto livello
  «Prosegui compilazione» o incarico equivalente rinnova il ciclo. Nessun loop
  illimitato. Riaprendo ANALYZING si legge lo stato; un claim scaduto offre ripresa
  esplicita, senza restare indefinitamente sullo spinner.
- `chat` è una proiezione backend: domanda corrente, conteggi reali e avanzamento
  autorizzato. WAITING_FOR_USER propone una domanda naturale per **un solo campo**,
  alternative comprese. La conferma di applicabilità non diventa un valore.
- La risposta libera usa `/answer`, con session ID/versione. Il planner propone
  campo, valore e user_quote; il gate accetta soltanto il campo chiesto e valore
  nell'ultimo messaggio USER. Matching deterministico con confini di parola:
  «No» non può essere estratto da «Non lo so». Le date complete italiane sono
  normalizzabili; più date richiedono chiarimento. Nessun aggiornamento multiplo
  ambiguo o da FORM/storico/alternative non confermate. Restano i validatori DOCX.
- Valori liberi validi diventano USER_PROVIDED/provenance USER, con revisioni e
  aggiornamento localizzato; non sono dati verificati SOURCE. Segue la prossima
  domanda o ripresa automatica sui pending. «No» alla condizione esclude il solo
  candidate chiesto; «Sì» conferma la condizione ma lascia da chiarire il valore.
- La vista primaria è il thread con attività/spinner, quantità reali, domanda e
  download. Supporta prefers-reduced-motion anche nello scorrimento. La vecchia
  scheda è sotto **Dettagli compilazione**, inizialmente chiuso: conteggi tecnici,
  ID/prove, Continua analisi, Aggiorna stato, editor field, reset, motivo di
  esclusione e bozza incompleta esplicita. Non si devono pilotare i batch.
- READY chiede conferma breve (chat o **Genera DOCX**). Nessuna generazione
  incompleta implicita. Renderer originale + stato corrente, poi DOCX/report;
  nessun editor, pagina nuova, multi-documento o motore di scrittura duplicato.

### Persistenza, compatibilità e limiti

`chat_workflow` usa lo snapshot JSON esistente, nessuna tabella nuova. Budget,
pausa, chiarimento e conferma USER di applicabilità persistono. Aggiunta colonna
`conversation_turns.compilation_json` per session ID/azione nello storico;
contratti opzionali compatibili e `automatic=true` su resolve. Sessioni legacy
richiedono un avvio/ripresa esplicito; quelle standalone non sono collegate a
una conversazione arbitrariamente. Riavviare il backend per la colonna additiva;
**nessuna reindicizzazione richiesta**.

Restano i limiti della V1: semantica del modello, candidate grezzi, falsi negativi,
applicabilità prudente, allegati senza posizione scrivibile. Il chiarimento libero
si limita al campo chiesto: correzioni arbitrarie di altri campi o risposte
multi-field usano ancora i dettagli espliciti. Una risposta con più date o con alternative/incertezza espresse nel messaggio
viene rifiutata conservativamente anche se include una scelta descritta a parole.
Non c'è worker: la pagina aperta guida l'analisi; chiudendola lo stato rimane,
ma non parte un nuovo ciclo in background. La domanda corrente è la proiezione
dello stato; le revisioni conservano il prima/dopo, senza inventare turni LLM.
READY non certifica la completezza amministrativa del documento.

### Verifiche effettivamente eseguite

- Nuovi test backend conversazionali: **50 passati**, parametrizzati FTS5/Qdrant
  con DB/storage temporanei e provider simulati. Routing senza RAG contraddittorio,
  riuso, budget persistito, passi automatici, domanda, USER/date, aggiornamento
  localizzato, ambiguità/grounding, applicabilità, versioni, isolamento e conferma
  sicura di generazione. Suite backend completa: **945 passati**; Ruff superato.
- Frontend: **78 passati in 12 file**, lint Oxlint e build TypeScript/Vite passati.
- Browser Chromium: **8 passati** con API simulate, desktop/mobile e movimento
  ridotto: compilation-chat, composer-model-menu, project-forms. Due passi
  automatici, ambiguità senza update, risposta libera, refresh WAITING/READY,
  distinzione USER/SOURCE, generazione/download e assenza overflow.
  Screenshot verificati; frontend di prova separato sulla porta 5193.
- `git diff --check` e controllo whitespace dei nuovi file. Nessun benchmark
  con DeepSeek/Gemma reale; questi test misurano il software, non il modello.

Comandi: `uv run --locked pytest -q tests/test_compilation_conversation.py`,
`uv run --locked pytest -q`, `uv run --locked ruff check .`; frontend con Node
locale: `npm test`, `npm run lint`, `npm run build`,
`PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npm run test:e2e -- compilation-chat.spec.ts composer-model-menu.spec.ts project-forms.spec.ts`.

### Prova manuale e prossimo punto

Riavviare backend/frontend aggiornati e usare una conversazione nuova nel progetto
di prova con DOCX e SOURCE pertinenti:

`@domanda-partecipazione.docx` + «me lo compili?» → risposta di avvio → attività e
analisi automatica → domanda assistant → risposta libera univoca → valore USER e
prossima domanda/ripresa → READY → conferma generazione → DOCX/report.

Controllare «riassumilo» con la stessa mention: solo chat FORM, nessun avvio.
Riaprire WAITING/READY e provare una risposta ambigua: valori invariati. Nei dettagli
verificare che il valore USER non sia presentato come SOURCE e che il DOCX venga
sempre generato dall'originale. Nessuna bozza parziale senza azione esplicita.

**Prossimo punto:** benchmark con il provider reale del progetto su routing,
classificazione dei candidate e qualità delle domande. Valutare poi raggruppamento
prudente dei chiarimenti condizionali o correzioni di campi diversi: da discutere,
non da implementare automaticamente. Le invarianti FORM/SOURCE/USER restano ferme.
Preservate modifiche locali, inclusa `.env.example` eliminata; nessun commit/push.
I test non hanno usato database/storage originali dell'utente.

## Milestone precedente: integrazione manuale chat/@ (storico)

È ora collegata la **CompilationSession V1 alla chat esistente**, con una mention
`@` strutturata per un solo modulo e azioni inline. Questa milestone è stata
richiesta esplicitamente dall'utente; le precedenti indicazioni «chat/@ da
progettare» sono superate per il percorso qui descritto. Non è stata implementata
l'interpretazione libera dei chiarimenti. Non riaprire il RAG generale o
ridisegnare l'extractor MIXED per proseguire questa integrazione.

### Integrazione chat implementata

- Il composer mostra i soli `project.files.kind=form` del progetto corrente
  digitando `@`, con filtro per nome, selezione da tastiera/click e chip singola.
  Il riferimento passa come `form_id` all'API; non è testo spacciato per evidenza.
  I TXT restano contesto interrogabile, l'avvio compilazione riguarda i DOCX.
- Una domanda normale con mention non crea sessioni: il planner esistente
  riceve il riferimento esplicito per risolvere le anafore. Il backend verifica
  progetto/ruolo e vincola FORM/MIXED al documento selezionato, anche se il
  planner propone un altro ID. Le domande fattuali restano SOURCE. Nessuna
  modifica a extractor, matcher, filtri, budget RAG o renderer.
- `POST /compilation-sessions` accetta `start_in_chat=true`: se manca una
  conversazione la crea nella stessa transazione della sessione; se esiste
  riusa la sessione della coppia conversazione/form. `BEGIN IMMEDIATE` evita
  duplicati da avvii concorrenti sulla stessa coppia. Eventuali duplicati
  storici non vengono cancellati: si riprende il più recente.
- L'elenco sessioni accetta `?conversation_id=...`, validato nel progetto.
  Riapertura e refresh leggono elenco/dettaglio backend. La UI mostra un solo
  snapshot di sessione alla volta, del modulo selezionato oppure l'ultimo della
  conversazione se non c'è una mention. Nessuno stato di compilazione è salvato
  soltanto in React o localStorage.
- Riquadro nella conversazione con documento, stato, tutti i conteggi backend,
  problemi aperti e valori già valutati espandibili. I pending restano posizioni
  da analizzare, non informazioni automaticamente richieste all'utente.
- **Continua analisi** esegue un solo `resolve`, fino a 12 candidate. Non ci
  sono loop AI. Se si riapre una sessione ANALYZING, polling GET ogni tre secondi
  legge lo stato: non avvia altri step. Claim e versioni sono quelli della V1.
- **Chiarisci/Correggi** apre un solo input inline, legato al `field_id`.
  **Salva valore** usa PATCH e provenance USER; non lo presenta come verificato
  SOURCE. Sono disponibili ricerca mirata per un campo irrisolto, esclusione
  esplicita con motivo e reset. Campi già decisi richiedono reset prima della
  rivalutazione. Le prove FORM e SOURCE restano separate e conservano la KB.
- **Genera DOCX** per READY/stato senza problemi; **Genera bozza con campi
  irrisolti** è un'azione esplicita distinta. Download DOCX/report nella chat.
  Una bozza precedente rimane identificata con la versione da cui deriva.
  La generazione usa sempre il renderer e l'originale della V1.
- Annullamento e controllo delle richieste al cambio progetto/conversazione/
  modulo; una creazione tardiva non riapre la chat abbandonata. I 409/errori
  rileggono lo stato senza ripetere la mutazione. Gli errori di validazione
  mantengono il valore digitato per consentire la correzione.

### Persistenza e compatibilità

Due colonne additive all'avvio: `conversations.selected_form_id` (FK al modulo,
ON DELETE SET NULL) e `conversation_turns.form_reference_json` (snapshot storico
ID/nome). Nessuna nuova tabella. `form_reference` è opzionale nelle risposte chat,
nei turni e nel dettaglio conversazione. La mention viene conservata con l'invio
del messaggio o l'avvio della sessione; una selezione non ancora inviata è una
bozza locale. Rimuoverla e inviare un messaggio azzera il contesto corrente,
senza alterare i riferimenti dei turni precedenti né cancellare la sessione.

Riavviare il backend aggiornato per applicare le colonne. Nessuna reindicizzazione
richiesta da questo intervento; restano le istruzioni per i vecchi form senza
frammenti nel README. Non sono stati modificati database/storage originali durante
i test. Preservate tutte le modifiche precedenti, inclusa `.env.example` eliminata.
Nessun commit o push.

### Verifiche dell'integrazione chat

- Backend mirato: **161 test passati** su sessioni, guardie, chat e FORM retrieval,
  inclusi **14 nuovi casi** con FTS5/Qdrant reali in ambiente temporaneo e provider
  simulati. Suite backend completa: **895 passati**. Ruff superato.
- Frontend: **74 test passati** in 12 file, Oxlint e build TypeScript/Vite superati.
- Browser Chromium: **6 test passati**, desktop e mobile, sugli scenari
  `compilation-chat`, `composer-model-menu`, `project-forms`, con tutte le API
  simulate e frontend separato sulla porta 5193. Verificati anche screenshot e
  assenza di overflow orizzontale nel nuovo flusso.
- `git diff --check` verificato a fine intervento. I test software non misurano
  la qualità semantica di DeepSeek/Gemma; nessun benchmark con provider reale.

Comandi principali effettivamente eseguiti:

```bash
# backend/
uv run --locked pytest -q tests/test_compilation_chat.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_chat_flow.py tests/test_form_retrieval.py
uv run --locked pytest -q
uv run --locked ruff check .
# frontend/, Node locale in PATH
npm test
npm run lint
npm run build
PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npx playwright test e2e/compilation-chat.spec.ts e2e/composer-model-menu.spec.ts e2e/project-forms.spec.ts
```

### Prova manuale e prossimo passo

Su un progetto di prova con DOCX e fonti pertinenti: `@documento` → eventualmente
«riassumilo» (solo chat FORM) → **Avvia compilazione** → **Continua analisi** →
WAITING_FOR_USER → **Chiarisci**, salva un valore o indica non applicabilità →
continua sugli altri pending → READY → **Genera DOCX** → **Scarica DOCX/report**.
Ricaricare e riaprire la conversazione fra i passaggi: sessione, versioni,
conteggi e provenienza devono restare quelli persistiti. Verificare che una
correzione USER non azzeri i valori SOURCE degli altri campi.

Rimangono i limiti della V1 backend (applicabilità prudente, falsi negativi,
candidate grezzi, obblighi/allegati senza posizione DOCX). READY non certifica
la completezza amministrativa. Il riepilogo è lo stato corrente aggiornabile,
non una sequenza di falsi turni LLM: lo storico completo resta nelle revisioni
backend. Sessioni create prima senza conversation_id restano utilizzabili via
API; non sono associate arbitrariamente a una chat.

**Prossimo punto:** prova del flusso con il provider scelto e definizione del
collegamento fra messaggi liberi e `field_id`: distinguere un chiarimento da una
domanda ordinaria, proporre aggiornamenti espliciti, chiedere conferma quando
l'associazione è ambigua e conservare USER/versione/validazioni. Non implementare
automaticamente questa interpretazione, nuovi editor o compilazione multi-documento.

## Milestone precedente: CompilationSession V1 backend (storico)

È implementata la **CompilationSession V1 backend**, per un DOCX archiviato
alla volta. L'utente ha esplicitamente considerato il RAG abbastanza stabile
per procedere e ha autorizzato questa milestone: le precedenti indicazioni
di continuare a correggere MIXED prima delle sessioni sono quindi **superate**.
Non riaprire l'extractor o il RAG generale per questa ragione. Restano noti
falsi negativi conservativi; FORM non verifica valori, SOURCE pertinente sì.

La guida completa, mappa della pipeline, API, budget, esempio demo e istruzioni
manuali sono in [docs/compilation-session-v1.md](docs/compilation-session-v1.md).
Nessun menu `@`, nuova pagina, editor, collegamento automatico alla chat,
compilazione multi-documento o ciclo autonomo implementato.

### Architettura e comportamento implementati

- `compilation_sessions`: progetto, form, conversazione opzionale, snapshot
  immutabile dei byte originali, candidate strutturali in JSON, versione e date.
  `compilation_session_revisions`: cambiamenti prima/dopo e azioni. Sono due
  tabelle additive, create all'avvio; `document_fields` è la revisione demo e
  `document_compilations` conserva risultati immutabili, quindi non sono state
  impropriamente riutilizzate come stato modificabile dei candidate.
- La creazione controlla progetto/form/conversazione, legge il DOCX archiviato,
  usa `inspect_docx`, conserva ID e riferimenti strutturali. Nessuna AI o bozza
  in questa fase. Una sessione resta riprendibile leggendo SQLite. La rimozione
  del form archiviato azzera il collegamento, conservando lo snapshot originale
  e il riferimento storico; la cancellazione del progetto elimina le sessioni.
- `resolve`: massimo 12 candidate, una classificazione strutturale, il planner
  SOURCE esistente e una proposta in batch. Grounding FORM, query derivate dai
  requisiti, stessi filtri FTS5/Qdrant e validatori di associazione MIXED. Nessun
  uso degli embedding per trovare la posizione da scrivere. Nessun retry del
  nuovo classificatore/matcher e nessuna modifica all'extractor della chat.
- Budget: massimo tre chiamate chat LLM, sei gruppi, dodici query e 24 SOURCE
  per richiesta, fino a quattro proposte per campo. Ogni gruppo conserva la
  propria copertura; esclusi per budget restano PENDING/coverage_limit. I pending
  mai analizzati precedono quelli già tentati. Centinaia di candidate richiedono
  richieste successive esplicite, non un agent loop. Timeout 180 secondi,
  claim persistito di 240 secondi per ripresa dopo crash.
- Stati campo: PENDING, RESOLVED, MISSING, AMBIGUOUS, CONFLICTING,
  NOT_APPLICABLE, USER_PROVIDED. RESOLVED richiede SOURCE valida; FORM può
  soltanto sostenere il requisito o classificare uno spazio decorativo senza
  etichetta. USER_PROVIDED è separato da RESOLVED per non fingere verifica
  documentale. Gli aggiornamenti utente sono localizzati, espliciti per ID,
  con azioni set/not_applicable/reset e storico precedente/nuovo.
- Stati sessione: CREATED, ANALYZING, WAITING_FOR_USER, READY, GENERATED,
  FAILED. Se restano solo pending torna CREATED, con conteggio per continuare;
  missing/ambiguous/conflicting producono WAITING_FOR_USER, non un errore tecnico.
  Summary e open_issues sono nell'API e nel report della generazione.
- Applicabilità prudente: esclusione USER esplicita o dichiarazione SOURCE
  esplicita sulla condizione FORM; nessuna deduzione della partecipazione dalla
  forma societaria. Non è un motore generale di regole. Candidate grezzi non
  diventano automaticamente campi obbligatori o domande da fare all'utente.
- Versione obbligatoria per le mutazioni; 409 su versioni superate o claim attivo.
  Errori provider/parser/storage conservano lo stato precedente, oppure marcano
  FAILED senza applicare mezzi batch. Le SOURCE vengono rilette prima del commit
  della risoluzione e della generazione; fonti mutate/cancellate/non più ammesse
  non autorizzano una scrittura.
- Finalizzazione: adapter ai `ModelProposals`, validazione DOCX esistente,
  `fill_docx` dallo snapshot originale, nuovo record `document_compilations` e
  stessi download. Pending/missing/ambiguous/conflicting bloccano di default;
  `allow_unresolved=true` genera esplicitamente una bozza con vuoti e report.
  Mai riscrittura di una bozza precedente, mai indicizzazione degli output.
  Valori USER espliciti possono confermare scelte come «No», ma non aggirano
  firme, email, integrità numerica, limiti o posizioni. Questa autorizzazione
  non è disponibile alle proposte AI del percorso DOCX precedente.

### API V1

Prefisso `/api/projects/{project_id}/compilation-sessions`:

| Operazione | Metodo e suffisso |
|---|---|
| Creare da form_id e conversation_id opzionale | `POST` sul prefisso |
| Elencare / rileggere stato e candidate | `GET` sul prefisso / `GET /{session_id}` |
| Analizzare i prossimi pending o field_ids espliciti, massimo 12 | `POST /{session_id}/resolve` |
| Fornire valori, escludere o rimettere pending campi espliciti | `PATCH /{session_id}/fields` |
| Leggere prima/dopo delle revisioni | `GET /{session_id}/revisions` |
| Generare una nuova copia e report | `POST /{session_id}/finalize` |

`last_generation.downloads` restituisce i percorsi esistenti
`/document-compilations/{run_id}/download/{docx|report|template}`.
Usare sempre la versione dell'ultima risposta: resolve la incrementa sia
all'acquisizione del claim sia alla conclusione. Non serve un nuovo upload
per riprendere o rigenerare una sessione.

### Verifiche di questo intervento e limiti

Eseguiti **287 test mirati** (sessioni, guardie, motore DOCX/email, controlli
requisiti, planner SOURCE e retrieval FORM/SOURCE/MIXED) e **881 test backend
completi**, tutti superati. Ruff e `git diff --check` superati. Nessun frontend
modificato o test frontend rieseguito in questo intervento.

Comandi effettivamente eseguiti da `backend/`:

```bash
uv run --locked pytest -q tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_docx_compilation.py tests/test_docx_email_fields.py tests/test_requirement_checks.py tests/test_source_planning.py tests/test_form_retrieval.py -x
uv run --locked pytest -q
uv run --locked ruff check .
```

Le nuove regressioni specifiche delle sessioni sono 52, incluse nella suite
completa. Le esecuzioni intermedie da 34, 50 e 142 test precedono l'ultimo
insieme mirato: non sono verifiche aggiuntive di qualità semantica.

Database e storage temporanei; FTS5 e Qdrant locali reali con embedding/provider
simulati. Coperti ripresa senza memoria, byte originali immutati, tutti gli stati,
isolamento, USER localizzato, versioni concorrenti, fonti cambiate durante AI,
rollback storage e generazione concorrente, lease scaduto, cancellazione task,
contratti JSON DeepSeek/Ollama, campi di tabella e segnaposti di paragrafo.
Nessun benchmark reale del nuovo workflow con DeepSeek/Gemma in questo intervento.

La fixture DOCX reale ha 279 candidate. Il test analizza otto posizioni 5.d con
fonti simulate: sette resolved (denominazione, forma, sede, nome/qualifica/ordine
del direttore e numero albo **8421**), data di abilitazione missing, 271 pending.
L'organigramma è un allegato testuale senza candidate dedicato: non viene
inventata una posizione DOCX né dichiarata la disponibilità dell'allegato.
READY non dimostra la completezza degli obblighi fuori dai candidate.

Restano limiti conservativi del matcher e della classificazione. Non ci sono
regole generali di applicabilità, composizione automatica di campi complessi,
risoluzione degli obblighi/allegati non scrivibili, interpretazione libera dei
chiarimenti o garbage collection delle revisioni. Il contesto strutturale del
passo è limitato a 60.000 caratteri; gruppi troppo grandi si possono ridurre,
singole tabelle oltre budget richiedono revisione manuale.

Le tabelle saranno create dal normale avvio aggiornato. Nessuna migrazione dei
vecchi risultati o reindicizzazione necessaria, nessuna modifica ai dati locali
dell'utente durante i test. Tutte le modifiche precedenti, inclusa la cancellazione
di `.env.example`, sono state preservate. Nessun commit o push.

**Prossimo punto:** provare una sessione su una sezione con il provider scelto,
poi collegare alla chat creazione/riepilogo/aggiornamenti espliciti/download.
La base backend offre le operazioni richieste per l'integrazione; menu `@`,
UX dei chiarimenti e scelta della sessione rimangono un lavoro successivo.
Non implementarli automaticamente in una chat futura senza richiesta.

## Punto di ripresa precedente: SOURCE MIXED (storico)

L'ultimo intervento riguarda esclusivamente **associazione e copertura SOURCE
di MIXED**. Il numero di iscrizione professionale **8421 è ora verificato**
nelle prove reali B/C: non occorre che la fonte ripeta la parola «albo», ma
numero, iscrizione e ruolo personale devono risultare associati nell'estratto.
Una sola pianificazione SOURCE in batch produce al massimo sei gruppi, due
query e quattro evidenze per gruppo. Ogni requisito è cercato oppure indicato
esplicitamente come non ricercato per limite di copertura/budget. Non c'è più
il top-k globale di quattro SOURCE. Il matcher ha un compito stabile, senza
rispondere alla formulazione originale della domanda. Ruoli, scope e KB restano
invariati. Nessuna modifica all'extractor FORM, a `intents.py`, agli indici,
ai contratti API/frontend, al parser DOCX o ai workflow di compilazione.

Ultima verifica: **329 test mirati e 829 test backend completi** superati;
Ruff e diff check superati. Benchmark reale DeepSeek A–D: B **7/11** verificati,
C **4/6**, A **0/10**, D **0/16**. Tutti i requisiti di queste quattro prove
hanno copertura SOURCE; nessuno è escluso dal budget. A rimane un falso negativo
del matcher: codice fiscale/partita IVA arrivano nel contesto ammesso, ma il
modello restituisce `supports: []`. D riguarda prevalentemente dichiarazioni,
alternative di partecipazione e procedure concorsuali. I dettagli sono nella
sezione «SOURCE MIXED: diagnosi e correzione del 6 ottobre» sotto.

Il precedente intervento aveva corretto il **blocco dell'estrazione MIXED con DeepSeek**:
lo schema accettava al massimo otto requisiti e rifiutava l'intera risposta
quando il modello ne restituiva dieci, anche tutti sostenuti da estratti FORM.
Il problema è stato riprodotto prima di modificare codice. L'extractor ora usa
un compito documentale dedicato, schema esplicito anche in JSON mode, dati
personali distinti per campo/ruolo e un unico retry con gli errori concreti.
Accetta fino a 32 proposte, verifica gli estratti, deduplica e seleziona fino a
16 requisiti per il turno. Le premesse dell'utente non diventano requisiti.
La sezione 5.d ha prodotto **11 requisiti validati** nella nuova prova reale;
la fase SOURCE è partita e sei valori sono stati verificati.

La precedente correzione del **bug MIXED di disponibilità non supportata** resta:
Gemma classificava «con i documenti che ho posso iniziare a compilarlo?» come
`form`, senza cercare alcuna source. Il backend ora impone `mixed` per richieste
esplicite di disponibilità, ricava le query SOURCE da requisiti citati nel FORM
e compone la risposta usando soltanto valori con estratti SOURCE verificabili.
I due contesti hanno filtri e budget separati; una citazione FORM non può
validare la disponibilità di un valore nel confronto MIXED.
La precedente indicizzazione dei moduli era già presente ed è stata preservata:
nessuna nuova modifica a ingestion, parser strutturale o motore DOCX.
Non sono stati implementati compilazione iterativa, sessioni, menu `@` o nuova UI.

Prossimo punto di ripresa: usare la traccia A del benchmark corrente per valutare
il matcher a parità di requisiti e fonti già recuperate. **Non considerare ancora
l'intero MIXED congelato per la CompilationSession**: associazione 8421 e
copertura tracciata sono corrette, ma non è risolto ogni falso negativo semantico
della generazione. L'extractor è stato lasciato invariato e in alcune prove
intermedie ha ancora rifiutato output non grounded; non aggirarne le garanzie.
La compilazione iterativa resta da progettare, senza implementazione autorizzata
in questo intervento. Non allargare automaticamente il lavoro all'extractor.
I moduli già indicizzati non richiedono riestrazione per questa modifica; quelli
ancora privi di frammenti richiedono il comando esplicito già disponibile.
Il modulo corrente di `prova`, file 155, ha 22 frammenti; il file 154 senza
frammenti riguardava la diagnosi precedente. Nessun dato o indice locale
dell'utente è stato modificato dalle prove: sono state usate copie temporanee.

La richiesta iniziale era mappare il progetto, verificare qualità e codice
morto, quindi migliorare la compilazione. La mappa e l'audit sono già in
[docs/mappa-progetto.md](docs/mappa-progetto.md): non occorre rifarli da zero.
La base è utilizzabile per il prototipo, ma i test software non dimostrano
l'accuratezza dei dati compilati da un modello reale.

## Richieste e orientamento dell'utente

- Il relatore ha chiesto una **compilazione iterativa**, perché il percorso
  precedente non era soddisfacente. La richiesta successiva ha definito la V1:
  iterazione sullo stato persistente, passi limitati e input utente espliciti,
  senza ciclo autonomo. La UX della chat rimane da definire.
- L'utente immagina compilazione e chat nella **stessa vista**, con un pulsante
  o `@` nel compositore per avviare la compilazione e scaricare documenti/report.
  È una preferenza espressa, non una funzionalità già disponibile.
- Dopo una prova con `gemma4:e2b`, ha chiesto di verificare anche il codice:
  non attribuire automaticamente ogni risposta errata al modello piccolo.
- È favorevole a indicizzare il modulo, ma teme che il sistema confonda
  moduli, fonti aziendali e dati. Ha poi richiesto esplicitamente il confronto
  informativo `mixed`, mantenendo distinti ruolo e scope/KB. Questa parte è
  implementata; anche la V1 backend di compilazione è ora implementata.

## Cosa esiste oggi

| Area | Stato verificato |
|---|---|
| Fonti documentali | Fonti PDF/TXT/Markdown di progetto e globali, estrazione e frammenti in SQLite. |
| Moduli da compilare | Upload, elenco, download e rimozione di originali DOCX/TXT, massimo 20 MB, ruolo `form`. Il corpo DOCX/TXT viene estratto e frammentato; originale invariato. |
| Chat | Il modello decide risposta diretta oppure ricerca e target source/form/mixed; un controllo backend impone mixed per le richieste esplicite di disponibilità. Fino a tre query FORM; in MIXED fino a sei gruppi/dodici query SOURCE derivate dai requisiti citati. Il backend distingue requisiti, valori verificati, dati non verificati e requisiti non ricercati. |
| Retrieval | FTS5 oppure Qdrant, stessi indici per entrambi i ruoli. Filtri prima della selezione e rilettura delle evidenze impongono ruolo/progetto/modulo. Solo source ammette fonti globali. |
| Provenienza | Evidenze API e storico conservano scope `project:ID`/`global` e category `company`/`general` dove applicabile, oltre a ruolo, ID documento/frammento, progetto, nome e metadati. |
| Compilazione DOCX | Percorso precedente a chiamata unica conservato; nuova CompilationSession persistente con risoluzione, correzioni utente e renderer esistente. |
| Contesto DOCX | Il percorso precedente mantiene fonti per budget; le sessioni partono dal modulo archiviato e usano planner/retrieval SOURCE già disponibili. |
| Iterazioni e UI | Sessioni backend disponibili; collegamento chat, selezione `@`, revisione dialogica e scheda UI non implementati. |
| Percorsi separati | Generazione Markdown e pagine dimostrative esistono; la revisione dimostrativa non è un editor del DOCX prodotto. |

La modalità DOCX a gruppi da 32 e le riparazioni automatiche sono state rimosse
nel commit `f916239`. Errori strutturali della risposta interrompono il percorso
unico; le proposte bloccate dai controlli restano vuote e sono segnalate nel
report. Il passaggio a un ciclo iterativo richiede uno stato e regole esplicite,
non il semplice ripristino della vecchia suddivisione in gruppi.

## Lavoro già completato

L'audit iniziale, conservato nel commit `2e4e946`, ha corretto:

- Effetti delle risposte chat tardive dopo un cambio di progetto/conversazione.
- Validazione delle email DOCX: confronto con l'indirizzo completo nella fonte,
  anche se il modello ne cita solo una parte.
- Incoerenze fra file dell'artefatto, metadati e indice in caso di errori SQL.
- Replay delle compilazioni: inoltro delle opzioni AI e lettura del template
  nei percorsi corrente e storico.

Sono stati inoltre attivati TypeScript strict e lo schema JSON delle proposte
DOCX per Ollama. Rimosse le dipendenze inutilizzate `react-markdown`,
`remark-frontmatter` e `remark-gfm`. Attualmente la risposta chat viene resa come
testo in un paragrafo: il rendering Markdown non è implementato.

La mappa inventaria nove metodi client senza chiamanti applicativi, alcuni
usati nei test. Sono stati conservati perché le API esistono e possono servire
al nuovo percorso: `projectArtifacts`, `projectArtifact`, `updateProjectArtifact`,
`generateDraft`, `documentCompilations`, `documentCompilation`, `compileDocument`,
`downloadCompilation`, `projectEvidence`.

## Diagnosi della prova con Gemma

Verifica del 5 ottobre **precedente all'integrazione RAG dei moduli**, sul database
locale in sola lettura: progetto `prova`,
conversazione `conv-387b173d8b53480e`, turni 77 e 78.

L'utente aveva caricato `domanda-partecipazione.docx` e chiesto prima una
spiegazione, poi la documentazione necessaria in dieci punti e i dati Mapi.
La seconda risposta ripeteva l'apertura della prima, senza i dieci punti.

Riscontri:

1. Il DOCX era presente e leggibile, file 154, ruolo `form`, **zero frammenti**.
   Il parser rilevava 279 posizioni candidate: non sono 279 dati necessariamente
   da compilare. Nel progetto non erano presenti file con ruolo `source`.
2. Le 7 e 8 evidenze dei due turni provenivano tutte dalle fonti globali:
   `generalita-mapi.md`, `progettazione-opere-pubbliche.txt` e/o
   `visura-mapi-ingegneria-simulata.pdf`. **La chat non aveva letto il modulo.**
3. La frase errata «carico e relative qualifiche documentate» derivava da un
   frammento che iniziava nel mezzo di «incarico»: difetto concreto nel codice
   di suddivisione, poi ripreso dal modello.
4. «Assistenza tecnica agli enti nella» coincideva con la fine di un altro
   frammento. I vicini recuperati non garantiscono una sezione completa.
5. Il backend passa l'ultimo messaggio e distingue la cronologia dalle prove.
   Non è emersa una duplicazione applicativa della vecchia risposta. I controlli
   verificano gli ID delle citazioni, non il loro supporto semantico o il
   rispetto dei dieci punti richiesti.

Entrambi i turni erano `completed`, senza errore tecnico salvato. Le query di
ricerca e le risposte grezze del provider non sono persistite: non è possibile
ricostruire esattamente ogni richiesta. La configurazione letta durante la
diagnosi era Qdrant locale/BGE-M3, chat `gemma4:e2b`; non è una registrazione
storica completa delle impostazioni dei turni.

Il [report locale dettagliato](backend/data/chat-audit/prova-turni-77-78.md)
è escluso da Git e può mancare in un altro checkout. I riscontri essenziali
sono riportati qui proprio per non dipendere da quel file.

## Modifiche pendenti e dati non aggiornati

Prima della creazione dei due documenti, `git status` mostrava:

| File | Stato e provenienza |
|---|---|
| `.env.example` | Eliminazione preesistente dell'utente; non ripristinata. |
| `backend/app/ingestion.py` | Correzione non ancora committata di `chunk_text`: confini delle parole anche nell'overlap e con newline; parametri validati e avanzamento garantito. |
| `backend/tests/test_ingestion_chunks.py` | Nuovo file non ancora committato, dieci casi di regressione per la correzione. |

AGENTS.md e STATUS.md si aggiungono a queste modifiche. L'integrazione RAG aggiunge
modifiche a upload moduli, planner, routing chat, retrieval SQL/vettoriale,
generazione e contratti delle evidenze, più test e uno script di reindicizzazione.
Il frontend aggiunge soltanto l'etichetta del ruolo nelle evidenze esistenti.
README e mappa sono aggiornati. Nessun commit o push eseguito.

Il successivo intervento `mixed` modifica planner e orchestrazione chat,
generazione/validazione, metadati SQL/vettoriali, schema API e tipi frontend,
test e documentazione. Nessun nuovo motore o indice, colonna SQLite, pagina,
stato di compilazione o modifica ai componenti UI in questo intervento.
La correzione del bug MIXED aggiunge `backend/app/requirement_checks.py` e i
relativi test; modifica planner, orchestrazione, generazione e la costruzione
delle query FTS per sigle societarie puntate (`S.r.l.`/`S.p.A.`). Non modifica
nuovamente ingestion, parser DOCX, schema API, frontend o motore vettoriale.
Il precedente intervento sull'extractor DeepSeek modifica soltanto `intents.py`,
`requirement_checks.py`, `generation.py`, `main.py`, relativi test e documentazione;
aggiunge `test_requirement_extraction.py`. Non modifica i contratti API/frontend,
i filtri dei corpus, l'indicizzazione o il parser DOCX.
L'intervento SOURCE del 6 ottobre aggiunge `source_planning.py` e relativi test;
modifica `requirement_checks.py`, `main.py`, `generation.py`, test e documentazione.
`intents.py` non viene toccato ulteriormente. Nessuna reindicizzazione necessaria.
Branch e commit di base sono rimasti quelli indicati sopra; tutte le modifiche
locali precedenti, inclusa l'eliminazione di `.env.example`, sono state preservate.

**La correzione storica di chunking non modifica i frammenti già salvati.** Per applicarla alle fonti
esistenti serve riestrarre/suddividere gli originali e poi sincronizzare Qdrant.
Il solo aggiornamento dell'indice vettoriale riusa i frammenti SQLite e non
ripara le parole tagliate. Questa operazione sui dati non è stata eseguita;
anche le risposte storiche restano invariate. La correzione conserva le parole,
ma non garantisce che ogni frammento contenga frasi o sezioni complete.

## Verifiche già eseguite

| Momento | Esiti registrati |
|---|---|
| Audit iniziale, prima delle successive semplificazioni | 671 test backend, 61 frontend, 10 Playwright selezionati; lint e build superati. |
| Diagnosi Gemma e correzione dei frammenti, 5 ottobre | Dieci nuove regressioni fallivano prima della correzione; dopo, 207 test mirati e **646 test della suite backend completa** superati. Ruff e `git diff --check` superati. |
| Creazione AGENTS.md e STATUS.md | Verifica documentale di riferimenti, diff e stato Git; nessuna nuova esecuzione delle suite applicative. |
| Integrazione RAG dei moduli, 5 ottobre | 108 test backend mirati; suite backend completa **678 test** superati; suite frontend completa **62 test** superati. Ruff, Oxlint e TypeScript/build Vite superati. Guida CLI, riferimenti documentali e `git diff --check` verificati. |
| Confronto RAG mixed e provenienza KB, 5 ottobre | **178 test backend mirati** superati; suite backend completa **715 test** superati; suite frontend completa **62 test** superati. Ruff, Oxlint e TypeScript/build Vite superati; `git diff --check` verificato. |
| Correzione bug MIXED reale, 5 ottobre | **217 test backend mirati** e **754 test backend completi** superati. Ruff e `git diff --check` superati. Riproduzione reale Gemma/BGE/Qdrant su copie temporanee: risposta completed, 4 FORM + 4 SOURCE; denominazione sostenuta da SOURCE, nominativo generico non verificato. Nessuna nuova esecuzione frontend o browser E2E in questo intervento. |
| Robustezza estrazione MIXED DeepSeek, 5 ottobre | **298 test backend mirati** e **798 test backend completi** superati. Ruff e `git diff --check` superati. Diagnosi e benchmark reale A–E con DeepSeek/Qdrant su copie temporanee, risultati e limiti sotto. Nessuna nuova esecuzione frontend o browser E2E: contratti e frontend invariati in questo intervento. |
| Associazione/copertura SOURCE MIXED, 6 ottobre | **329 test backend mirati**, **829 test backend completi** superati; Ruff e diff check superati. Benchmark reale DeepSeek A–D su copie temporanee, nuova conversazione per caso, dettagli sotto. Nessun frontend/E2E rieseguito: nessuna modifica ai contratti o alla UI. |

I conteggi appartengono a revisioni diverse: nel frattempo sono stati rimossi
test della compilazione a gruppi. Nella diagnosi precedente non erano cambiati
file frontend; nell'integrazione RAG è stata aggiunta l'etichetta delle evidenze.
Le prove RAG usano SQLite/FTS5 e Qdrant locale reali con planner/provider ed
embedding simulati, database e storage temporanei. Coprono il DOCX Catanzaro,
upload DOCX/TXT, isolamento, esclusione delle globali per form, esclusione dei
form per fatti aziendali, rilettura di risultati del ruolo sbagliato, rimozione,
reindicizzazione esplicita e rollback. I test software usano provider simulati,
non misurano l'accuratezza semantica di Gemma. La successiva riproduzione reale
del bug MIXED è descritta sotto; non modifica dati o indici originali dell'utente.
Gli E2E browser non sono stati rieseguiti in questi interventi RAG.
Sono coperti anche aggiornamento dei payload vettoriali precedenti, cambio di
ruolo durante la query e rifiuto di comandi di reindicizzazione con progetto
o backend incompatibile prima di modificare i frammenti.

Comandi eseguiti nell'ultimo intervento SOURCE MIXED, da `backend/`:

```bash
uv run --locked pytest -q tests/test_source_planning.py tests/test_requirement_extraction.py tests/test_requirement_checks.py tests/test_form_retrieval.py tests/test_generation.py tests/test_chat_flow.py tests/test_retrieval.py tests/test_vector_retrieval.py tests/test_model_parsing.py -x
uv run --locked pytest -q
uv run --locked ruff check .
```

Nel precedente intervento sul contratto di provenienza, da `frontend/`:
`npm test`, `npm run lint`, `npm run build`, con
`/home/montesano/tesi/.tools/node/bin` aggiunto al PATH del comando.
Le nuove regressioni coprono i casi A–G richiesti: solo form per il riassunto,
solo source per i fatti, partita IVA vuota/valore presente soltanto nel form,
requisito e valore con provenienze distinte, requisito senza dati supportati,
fonti progetto/globali con esclusione di altri progetti, entrambi i backend.
Coprono anche norme generali presenti in Company o General KB, contesti
incompleti, citazioni del ruolo sbagliato (incluse quelle nel testo), limiti e
deduplicazione delle query, metadati nello storico/vicini/rilettura e cambio di
categoria durante una query Qdrant. I provider Ollama/DeepSeek sono simulati:
queste prove non misurano la capacità del modello di comprendere o confrontare
requisiti reali. La correzione successiva copre anche i sei casi del bug MIXED:
campo richiesto senza source, denominazione verificata da source, direttore
tecnico non verificato, query derivate dai requisiti, bucket 8 FORM/4 SOURCE
che mantengono 4 FORM/4 SOURCE nel contesto, compilabilità respinta se citata
soltanto dal form. Copre inoltre riparazione parziale delle prove, estratti
inventati, valori di altre persone e norme generiche. Nessuna reindicizzazione
dei dati utente o nuova esecuzione frontend/browser E2E in questa correzione.

## Lettura e indicizzazione dei moduli: implementate

Il ruolo è persistito su `project_files.kind`: i frammenti lo ereditano tramite
la relazione `file_id`, senza una nuova colonna duplicata o un nuovo indice.
SQLite conserva testo, progetto e file; FTS5 si aggiorna con i trigger esistenti.
Qdrant conserva anche ruolo, file, nome, progetto e metadati del documento nel
payload; l'hash include tali dati e aggiorna i vecchi payload alla sincronizzazione.

- `intents.ChatDecision` richiede `target`: source/form/mixed; `form_id` è opzionale.
  Il pianificatore riceve solo ID/nomi dei moduli del progetto, insieme alla
  cronologia non fattuale. Per form deve selezionare un ID effettivamente presente.
- `main.project_answer` valida tale ID e passa target/file a ricerca e vicini.
  Una ricerca form non può includere fonti globali o altri moduli. Un modulo
  assente, ambiguo o senza evidenze produce `no_evidence`, senza generazione
  documentale o ripiego sulle fonti aziendali.
- La ricerca source resta il default delle API di retrieval e non ammette form.
  Gli artefatti fattuali già consentiti restano utilizzabili come prima.
- Un target mixed esegue le ricerche separate descritte nella sezione successiva;
  non chiede più di separare le domande e non avvia una compilazione.
- Le evidenze API/storico includono `role`, `project_id`, `document_metadata`,
  `scope`, `category` (null dove non applicabile o nello storico precedente).
  I vecchi payload privi di ruolo sono compatibili e interpretati come source.
  Nella UI esistente si legge «Modulo» oppure «Fonte».
- Il prompt distingue contenuto/istruzioni del modulo da fatti documentati e
  spiega che una dichiarazione prestampata non prova il possesso di un requisito.
  I filtri del backend, non soltanto il prompt, impongono la separazione.

L'endpoint `/api/projects/{id}/evidence` ammette `target=form&form_id=...` per
la ricerca esplicita; senza target continua a cercare nelle sole fonti fattuali.
Il parser strutturale/candidate DOCX e il motore di compilazione non sono cambiati.
I vettori dei file eliminati vengono rimossi dalla riconciliazione prima della
successiva ricerca/indicizzazione, come per le fonti esistenti; SQLite, FTS e
storage vengono ripuliti all'eliminazione.

### Diagnosi del bug MIXED reale e correzione

Il turno 85, conversazione `conv-5d516e3726e74579`, progetto `prova`, del
5 ottobre alle 13:11:46 UTC contiene la risposta segnalata dall'utente:
«è possibile compilare» con otto evidenze del solo file 155,
`domanda-partecipazione.docx`, tutte `role=form`. La prima, frammento 13880,
descrive i campi richiesti dalla sezione 5.d; non attesta alcun valore aziendale.
Il modulo ha 22 frammenti. Non ci sono file source caricati nel progetto;
restano consentiti gli artefatti fattuali già previsti e le KB globali.

Intent, query e risposta grezza del planner non sono salvati nello storico:
non è possibile dichiarare quale JSON abbia prodotto esattamente il turno 85.
È stata quindi ripetuta la richiesta con Gemma, medesima cronologia e profilo,
su copie temporanee di SQLite/Qdrant; il database originale è stato letto in
sola lettura. **Il planner ha assegnato `target=form`, non mixed**, con query:

1. `requisiti del direttore tecnico nel modulo domanda di partecipazione`
2. `dati richiesti per la compilazione della domanda di partecipazione`
3. `informazioni necessarie per compilare la domanda di partecipazione`

| Fase della riproduzione prima della correzione | FORM | SOURCE |
|---|---:|---:|
| Candidati Qdrant prima del top-k, per ciascuna delle tre query | 22 | 0 |
| Dopo top-k, per query | 4 | 0 |
| Dopo merge | 4 | 0 |
| Dopo espansione, contesto finale | 8 | 0 |

La ricerca SOURCE non è stata eseguita: query SOURCE `[]`, contesto SOURCE
vuoto. Non era un top-k globale che eliminava fonti già recuperate. L'assenza
del contesto fattuale nasceva dal routing. Il validatore FORM controllava
soltanto l'esistenza di `[1]`: quella citazione esisteva, quindi la frase passava.
Anche il precedente contratto libero `MixedAnswer` permetteva la stessa frase
in `requirements` con una citazione form: il modello decideva l'etichetta della
propria affermazione, eludendo il controllo di ruolo. Infine, le query SOURCE
anticipate dal planner non derivavano dal contenuto appena letto del modulo.

Il [report prima della correzione](/tmp/mapi-mixed-diagnosis-before.json) contiene
query, conteggi, contesti FORM/SOURCE e prompt ricostruiti/riprodotti; il
[report dopo la correzione](/tmp/mapi-mixed-diagnosis-corrected.json) contiene
la successiva prova reale. Sono file temporanei esterni al repository e possono
non esistere in una sessione futura; i riscontri essenziali sono riportati qui.

Comportamento corrente:

- `ChatDecision` mantiene source/form/mixed. Il controllo backend riconosce
  richieste esplicite italiane di disponibilità/compilabilità e impone retrieve
  + mixed anche se Gemma propone form. Un answer anticipato insieme a retrieve
  viene scartato in questo caso; query, target e ID restano validati.
- Mixed esegue prima le query FORM. Una chiamata allo stesso provider ricava
  i requisiti con nome, eventuale ruolo personale, estratto e citazione FORM
  verificati dal backend. Il limite corrente è 32 proposte e 16 requisiti
  selezionati dopo controllo e deduplicazione per campo/ruolo personale, usando
  soltanto la prima occorrenza già valida. Non si analizzano candidate/celle DOCX.
- Il backend raggruppa i requisiti con una pianificazione SOURCE in batch,
  poi costruisce al massimo dodici query dalle etichette validate, una/due per
  gruppo, senza usare la domanda generica o le `source_queries` anticipate dal planner. Per la
  denominazione aggiunge «ragione sociale» e forme societarie; FTS5 mantiene
  le sigle puntate come frasi, per trovare anche un nome aziendale senza etichetta.
- Il retriever esistente conserva filtri per ruolo, progetto e modulo. Mixed
  usa due bucket: FORM massimo due frammenti principali/quattro con vicini;
  SOURCE massimo quattro evidenze per ciascuno dei sei gruppi, deduplicate
  nell'elenco finale (massimo 24 SOURCE + 4 FORM). Nessun ranking globale può
  cancellare un gruppo. Per altri target resta quattro principali/otto totali.
- I contesti `REQUISITI DEL MODULO (role=form)` e `FONTI FATTUALI (role=source)`
  restano separati fino alla generazione. Le citazioni hanno numerazione unica;
  l'elenco API concatena i bucket conservando ruolo e provenienza di ogni elemento.
- Il modello propone soltanto supporti con `requirement_id`, `source_citation_id`,
  `source_quote`, `value`. Il backend richiede ruolo SOURCE, ID valido, estratto
  presente nella fonte, valore letterale nell'estratto e associazione testuale
  al requisito. Un nome personale generico richiede lo stesso ruolo personale
  nei due estratti. Moduli, campi vuoti e norme generiche non bastano.
- Dopo un tentativo di correzione, supporti ancora invalidi vengono scartati;
  supporti validi rimangono e gli altri requisiti sono non verificati. Proposte
  concorrenti per lo stesso requisito non vengono selezionate arbitrariamente.
  JSON inutilizzabili/troncati ed errori del provider restano errori espliciti.
- La risposta è composta dal backend: requisiti del modulo, informazioni
  verificate nelle fonti, informazioni non ancora verificate. Solo un supporto
  SOURCE valido autorizza «utilizzabile per una prima compilazione». Zero SOURCE
  produce direttamente la risposta prudente, senza chiamata finale all'LLM;
  zero supporti validi produce la stessa conclusione anche con source recuperate.
  Se manca il form termina con `no_evidence`, senza sostituirlo con dati aziendali.
- La mappa requisito/citazioni SOURCE ammesse è interna al turno: un requisito
  escluso dal budget non può risultare verificato né confondersi con un requisito
  cercato senza prove. Il renderer aggiunge «Requisiti non ricercati» se necessario.
- Anche una generazione FORM_ONLY viene respinta/riparata se contiene una frase
  positiva di disponibilità riconoscibile dal controllo backend. Non esiste
  stato persistente per campo, collegamento a candidate o compilazione avviata.

Provenienza conservata dall'intervento precedente:

- `project_files.kind` continua a rappresentare il ruolo; `global_documents.category`
  distingue company/general. Lo scope reale è `project:ID` oppure `global`.
  Entrambe le KB globali restano condivise fra progetti e ammesse nelle ricerche
  source; i vecchi collegamenti globali per progetto sono compatibilità e non
  filtrano tale accesso. Gli artefatti fattuali già ammessi restano fonti;
  template e bozze restano esclusi. `get_company_context()` seleziona soltanto
  company per la generazione Markdown e non è cambiato. Nessuna categoria prova
  da sola che un documento contenga valori dell'operatore.
- Scope e categoria restano disponibili attraverso SQL, Qdrant, LangChain,
  rilettura, vicini, API e storico. La categoria entra nell'hash dei vettori;
  payload precedenti si aggiornano nella stessa collezione alla sincronizzazione.
  Nessuna nuova migrazione o riestrazione dei moduli già indicizzati necessaria.

La riproduzione reale finale Gemma/BGE/Qdrant ha recuperato 22 FORM candidati,
due principali e quattro con vicini. Gemma ha individuato solo «Denominazione
sociale» e «Nome e cognome» distinti. Le query SOURCE sono quindi diventate:

1. `Denominazione sociale ragione sociale S.r.l. S.p.A. dati effettivi operatore economico`
2. `Nome e cognome dati effettivi operatore economico`

Ogni query SOURCE ha avuto 18 candidati, quattro selezionati; il merge ha
mantenuto quattro SOURCE. Il contesto finale/API contiene **4 FORM + 4 SOURCE**.
Dopo la riparazione Gemma ha citato correttamente la denominazione nella fonte
Company KB `generalita-mapi.md`; il supporto del nominativo citava ancora un FORM
ed è stato scartato. Risultato `completed`: «Mapi Ingegneria S.r.l.» verificata
con citazione SOURCE, nominativo non verificato. La prova non verifica tutti
i requisiti del documento, né è una misura generale della qualità di Gemma.

### Diagnosi DeepSeek: estrazione dei requisiti

Diagnosi effettuata prima delle modifiche, leggendo il database originale in
sola lettura e usando copie temporanee di SQLite, storage e Qdrant per le
chiamate reali. Nessun turno, frammento o indice dell'utente è stato aggiornato.
Nella conversazione `conv-23db5c9659114269`, progetto `prova`:

| Caso storico | Esito | FORM del file 155, nell'ordine del contesto | SOURCE finali |
|---|---|---|---|
| FAIL, turno 94: «Con i documenti disponibili, quali dati della sezione società di ingegneria possiamo già compilare?» | Nessun requisito accettato; disponibilità non valutata | 13880, 13881, 13879, 13882 | Nessuna |
| SUCCESS, turno 95: «Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti?» | Otto requisiti; denominazione, forma giuridica e sede verificate | 13879, 13881, 13878, 13880 | -43, -45, -30, -50 |

I due contesti condividono tre frammenti: entrambi contengono i dati pertinenti
della sezione 5.d. SUCCESS inizia però dalla 5.c e contiene campi personali
generici. Query, prompt e risposte grezze dei turni storici non erano persistiti:
non è possibile attribuire loro retroattivamente un JSON esatto del modello.

La riproduzione con DeepSeek e la cronologia precedente di ciascun turno ha
assegnato **MIXED a entrambi**, recuperando gli stessi elenchi FORM storici.
Le query FORM riprodotte erano:

| SUCCESS | FAIL |
|---|---|
| dati richiesti dal modulo domanda di partecipazione: denominazione sociale, iscrizione CCIAA, forma giuridica, sede legale | sezione 5.d società di ingegneria dati richiesti denominazione sociale iscrizione CCIAA forma giuridica sede legale |
| requisiti del direttore tecnico richiesti dal modulo: nome, qualifica professionale, data di abilitazione, ordine professionale, numero iscrizione Albo | requisiti direttore tecnico art. 36 allegato II.12 D.lgs. 36/2023 nome qualifica data abilitazione ordine numero iscrizione albo |
| allegati richiesti dal modulo domanda di partecipazione: DGUE, contratto di avvalimento, organigramma aggiornato, procura | allegato organigramma aggiornato parte V allegato II.12 D.lgs. 36/2023 |

La divergenza concreta è nel **limite dello schema prima del grounding**:

1. L'extractor precedente riusava il prompt utente di generazione, incluso
   «ULTIMO MESSAGGIO DELL'UTENTE A CUI RISPONDERE». Il system prompt chiedeva
   1–8 requisiti e favoriva l'accorpamento dei dati personali per ruolo.
2. Il JSON richiesto conteneva `requirements`, elementi con `name`,
   `form_quote`, `form_citation_id`; la lista ammetteva da uno a otto elementi.
   Ollama riceveva lo schema nativo; DeepSeek solo `json_object`, senza schema
   completo nel messaggio. Il limite era scritto nel prompt, non imposto dal
   provider.
3. Nella riproduzione **entrambi i testi hanno prodotto dieci requisiti**,
   anche al secondo tentativo. Il JSON era leggibile ma Pydantic lo rifiutava
   con `too_long`: nessun requisito raggiungeva grounding o deduplicazione.
4. Verificati individualmente, tutti e dieci avevano ID ed estratti validi.
   Non erano whitespace, due punti o chunk sbagliati a causare questo stop.
   La normalizzazione precedente gestiva già case, Unicode e spazi; una
   citazione senza i due punti finali era già una sottostringa accettabile.
5. Esisteva già un retry, ma comunicava un rifiuto generico invitando a copiare
   gli estratti, senza segnalare i dieci elementi contro il massimo di otto.
   La seconda lista veniva rifiutata allo stesso modo, producendo il messaggio
   «non ha individuato requisiti con estratti verificabili» prima di SOURCE.

Il SUCCESS storico aveva otto requisiti e rientrava nel limite. La stessa frase
non garantiva però il successo: nella nuova riproduzione ne produceva dieci.
Non è dimostrabile quale errore preciso avesse il JSON storico del turno 94;
è invece stato riprodotto il blocco strutturale con entrambe le formulazioni.
I dump completi di prompt/schema/risposte erano temporanei in `/tmp`; dopo il
riavvio del server non sono più disponibili. I riscontri essenziali e i conteggi
osservati sono conservati qui, senza presentare la riproduzione come storico.

Soluzione implementata:

- Prompt documentale dedicato: la domanda delimita sezione/soggetto/requisito,
  non decide quali valori siano disponibili. Lo schema completo è incluso nel
  messaggio anche per i provider con solo JSON mode. Nessuna nuova lista di
  frasi per riconoscere «possiamo compilare» o campo specifico della sezione 5.d.
- Campo interno opzionale `person_role`: distingue, per esempio, nome,
  qualifica, ordine, numero e data dello stesso soggetto senza chiamare tutto
  «direttore tecnico». Nome del campo e ruolo devono comparire nello stesso
  estratto FORM; il ruolo entra nelle query e nella verifica SOURCE.
- Limite strutturale 32 proposte distinto dal budget 16 requisiti selezionati.
  Ogni proposta non duplicata deve superare il grounding; i requisiti validi
  sono poi deduplicati per campo/ruolo e selezionati in ordine. Non si accettano
  requisiti inventati per evitare un errore. Estratti FORM fino a 2.000 caratteri
  consentono di citare il contesto contiguo dal ruolo fino al singolo campo.
- Normalizzazione deterministica di spazi, case, Unicode, virgolette/apostrofi
  tipografici, trattini e due punti terminali; parole e ordine restano invariati.
  Confini di parola impediscono, per esempio, di confondere ISO 9001 e 90010.
  Nessun fuzzy matching, composizione di frasi distanti o ricerca in altro chunk.
- Un unico retry sulle stesse evidenze, sia per lista vuota sia per output
  invalido, con tutti gli errori di grounding o schema, senza il testo grezzo
  degli input negli errori Pydantic. Budget output 4.096 token, 8.192 soltanto
  se troncato: anche il troncamento consuma l'unico retry disponibile.
  Due liste vuote fermano il turno senza SOURCE e senza valutare disponibilità;
  output ancora invalidi conservano il fallimento esplicito e prudente.
- Gli errori specifici di associazione SOURCE arrivano anche all'unica
  riparazione della generazione. Le prove ancora invalide restano non verificate.
  «Non disponibile» non può diventare un valore verificato. Il rendering continua
  a essere composto dal backend a partire dai soli supporti SOURCE accettati.
- Log INFO per tentativo/errori, numero proposto/selezionato, numero di requisiti
  e tentativi usati. Non viene aggiunto un contratto API o uno stato persistente.

Le nuove regressioni software usano provider simulati: sette formulazioni
equivalenti con lo stesso FORM, schema DeepSeek/Ollama, 11 dati della sezione
5.d, limite separato 32/16, retry vuoto→valido e due tentativi invalidi, ID
inesistenti, estratti inventati, differenze tipografiche, ruoli personali
distinti, premessa ISO non sostenuta, verifica per requisito. FTS5 e Qdrant
sono esercitati con database temporanei e provider/embedding simulati; per
confrontare lo stesso contesto 5.d il testo viene estratto dal DOCX fixture.
Restano i test del DOCX completo e di isolamento/FORM_ONLY/SOURCE_ONLY.
Il test logico del direttore verifica separatamente nome, qualifica, ordine e
numero 8421, lasciando la data di abilitazione non verificata; non dimostra che
DeepSeek produca sempre le stesse prove valide.

### Benchmark DeepSeek e verifica manuale da ripetere

Ultima prova reale su copie temporanee del progetto `prova`, profilo DeepSeek
`deepseek-flash`, Qdrant/BGE, **conversazione nuova per ogni domanda**. Questi
sono conteggi osservati, non attese invarianti di un modello stocastico e non
un confronto a parità di cronologia con i turni 94/95. Nessuna verifica browser
eseguita in questo intervento.

| Caso | Domanda |
|---|---|
| A | Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti? |
| B | Con i documenti disponibili, quali dati della sezione società di ingegneria possiamo già compilare? |
| C | Il modulo richiede i dati del direttore tecnico. Con le fonti disponibili abbiamo tutto ciò che serve per compilare quella parte? |
| D | Possiamo completare oggi la domanda senza chiedere nulla all'utente? Spiega cosa è verificato e cosa manca. |
| E | Il modulo richiede la ISO 9001: Mapi la possiede? |

| Caso | Intent | FORM | Requisiti validati/selezionati | Query SOURCE | SOURCE | Verificati | Non verificati | Retry extraction |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | MIXED | 4 | 16 | 3 | 4 | 0 | 16 | Sì |
| B | MIXED | 4 | 11 | 3 | 4 | 6 | 5 | Sì |
| C | MIXED | 4 | 6 | 3 | 4 | 3 | 3 | No |
| D | MIXED | 4 | 16 | 3 | 4 | 0 | 16 | Sì |
| E | MIXED | 4 | 0 | 0 | 0 | 0 | — | Sì |

A–D terminano `completed`, che non significa copertura completa. In B sono
verificati denominazione, forma giuridica, sede legale, nome del direttore,
qualifica e ordine. Rimangono non verificati CCIAA, numero/data di iscrizione,
data di abilitazione, numero albo e organigramma. In C sono verificati nome
Elisa Romano, qualifica Ingegnere e Ordine degli Ingegneri di Bari; data di
abilitazione, numero albo e organigramma rimangono non verificati.

**Il numero albo 8421 è un falso negativo residuo della prova reale**, non un
dato assente dalla KB: l'estratto SOURCE proposto non supera l'associazione
testuale al campo. Non è stato indebolito il gate per far passare il benchmark.
Le domande ampie A/D recuperano anche condizioni e sezioni differenti: zero
valori verificati non significa KB vuota e non prova che il modulo sia
incompilabile. La copertura richiede ancora valutazione mirata.

In E il primo elenco è vuoto, il retry tenta di sostenere ISO con un estratto
non pertinente e viene rifiutato: esito prudente `failed`, disponibilità non
valutata, nessuna query SOURCE anche se nelle KB esistono riferimenti ISO.
La premessa utente non è stata trasformata in requisito. Il numero di requisiti
non verificati è «—» perché manca un requisito FORM accettato da confrontare.

Per ripetere manualmente:

1. Riavviare il backend con il codice aggiornato, scegliere DeepSeek nel
   progetto con `domanda-partecipazione.docx` già indicizzato e le KB demo.
   Questa modifica non richiede reindicizzazione né aggiornamento dei dati.
2. Aprire una nuova conversazione per ciascuna domanda A–E e inviarla testualmente.
   Per riprodurre una conversazione storica, invece, mantenerne anche il contesto:
   i risultati possono cambiare con la cronologia.
3. Controllare le sezioni requisiti/verificati/non verificati e le etichette
   Modulo/Fonte. Nell'API `POST /api/projects/{id}/answer`, `evidence` conserva
   role, scope, category, file/progetto/chunk. I valori verificati devono citare
   SOURCE; un requisito presente solo nel FORM deve restare non verificato.
4. Per contare query e retry leggere i log INFO `Chat search`, `Chat bucket`,
   `Chat requirements` e `Requirement extraction` (per E guardare i tentativi,
   perché il piano non viene restituito). Query SOURCE solo dopo requisiti validi.
   Non ci sono nuovi pannelli di diagnostica nella UI.
5. In C controllare ogni dato separatamente; non accettare «direttore tecnico
   compilabile» in blocco. In E deve essere esplicita l'assenza di un requisito
   FORM verificato, senza dedurlo dalla domanda o da una certificazione SOURCE.

### SOURCE MIXED: diagnosi e correzione del 6 ottobre

Diagnosi completa, query, requisiti, budget e tabella del benchmark sono in
[docs/diagnosi-source-mixed.md](docs/diagnosi-source-mixed.md).

Prima della modifica, C proponeva già `requirement_id=5`, citazione SOURCE 6,
valore `8421`, preso dal chunk -45 di `generalita-mapi.md`. Anche il chunk -32
della visura era nel contesto. Il validatore rifiutava il supporto soltanto
perché la label FORM conteneva «albo» e la fonte «iscrizione professionale»:
JSON, ruolo, citazione, valore e soggetto erano corretti. Il retry eliminava il
supporto. Ora si controlla la relazione locale iscrizione/numero, con il ruolo
personale: non occorre ripetere ogni parola della label FORM. Numeri estranei
e prove di altri requisiti/gruppi sono respinti.

Nella diagnosi D aveva 15 requisiti riuniti per posizione in tre query
(`1/4/7/10/13`, `2/5/8/11/14`, `3/6/9/12/15`), poi ridotti a quattro SOURCE
globali. Ora `source_planning.py` raggruppa gli ID in una sola chiamata AI
(saltata per uno/due requisiti), senza categorie specifiche di questo DOCX.
Massimo sei gruppi di quattro requisiti, due query con una/due label per gruppo,
due ancore per query e quattro evidenze per gruppo, deduplicate globalmente.
Limite complessivo: **12 ricerche, 24 SOURCE + 4 FORM**. Nessun nuovo indice,
motore o modifica dei filtri. Il timeout totale resta quello precedente.

Le proposte coerenti troppo grandi vengono suddivise. Se il raggruppamento
fallisce, il fallback limitato usa ruoli personali/singoli campi e indica gli
esclusi dal budget. La mappa interna requisito/citazioni distingue ricercato
senza supporto da non ricercato; il renderer espone quest'ultimo caso nel testo
esistente, senza contratto API o UI nuovi. Nessuna SOURCE di un altro gruppo
può verificare il requisito. Il matcher ha un compito SOURCE stabile e conserva
l'unico tentativo di riparazione. Non usa domanda/storico come prove.

Sono state aggiunte regressioni per 8421 e numeri estranei nello stesso record,
campi diversi della stessa persona, 16 requisiti in 16 documenti, copertura
ed esclusioni esplicite, gruppi troppo grandi/invalidi e prompt SOURCE stabile.
Test software con provider simulati e FTS5/Qdrant reali in ambiente temporaneo:
**329 mirati**, **829 suite completa**; Ruff e diff check superati. Durante la
prova reale è stata inoltre corretta un'incompatibilità JSON mode del nuovo
prompt (DeepSeek richiede esplicitamente la parola JSON), con regressione.

Ultimo benchmark DeepSeek `deepseek-flash` con Qdrant/BGE, conversazioni nuove
su copie temporanee: tutti i turni sono MIXED, con quattro evidenze FORM.
Le domande A–D sono riportate integralmente nel report collegato sopra.

| Caso | Requisiti | Gruppi SOURCE | Query SOURCE | Coperti | SOURCE | Verificati | Non verificati | Non ricercati | Retry extractor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A: dati non verificati | 10 | 4 | 8 | 10 | 10 | 0 | 10 | 0 | Sì |
| B: società di ingegneria | 11 | 5 | 7 | 11 | 11 | 7 | 4 | 0 | Sì |
| C: direttore tecnico | 6 | 3 | 4 | 6 | 8 | 4 | 2 | 0 | No |
| D: completamento oggi | 16 | 5 | 10 | 16 | 8 | 0 | 16 | 0 | Sì |

C verifica nome, qualifica, ordine e **numero albo 8421**; data di abilitazione
e organigramma restano non verificati. B aggiunge denominazione, forma giuridica
e sede. A rimane un falso negativo della proposta del matcher: il contesto
ammesso dei requisiti codice fiscale/partita IVA include -43 e -30, ma DeepSeek
restituisce `supports: []`. Nessuna prova viene scartata dal validatore in A:
il modello non ne propone. D seleziona prevalentemente dichiarazioni, alternative
di partecipazione e procedure concorsuali, non l'anagrafica aziendale. Zero
verificati non dimostra che la KB sia priva di dati. In alcune prove intermedie
l'extractor invariato ha fermato A/D prima di SOURCE; la tabella registra
l'ultima esecuzione completa, non una garanzia per ogni risposta del modello.

Report diagnostici persistiti, senza modificare documenti/SQLite/Qdrant originali:
[traccia finale](backend/data/chat-audit/source-mixed-2026-10-06/deepseek-final.json),
[riepilogo](backend/data/chat-audit/source-mixed-2026-10-06/summary.json),
[test mirati](backend/data/chat-audit/source-mixed-2026-10-06/targeted.log),
[suite completa](backend/data/chat-audit/source-mixed-2026-10-06/backend-full.log).
Sono esclusi da Git e possono mancare in un altro checkout; non contengono
credenziali. I dump iniziali in `/tmp` sono andati persi al riavvio, i riscontri
essenziali sono conservati nel report Markdown. Nessuna reindicizzazione o
migrazione richiesta. Nessun frontend/E2E rieseguito in questo intervento.

Prossimo punto circoscritto: valutare il matcher usando la traccia A a parità
di requisiti/fonti, senza cambiare l'extractor o ampliare il retrieval alla cieca.
Non dichiarare congelato l'intero RAG per la CompilationSession in base ai soli
test software. Il workflow di compilazione rimane da discutere con l'utente.

### Verifica manuale di base FORM/SOURCE/MIXED

1. Avviare/riavviare `./start.sh` per caricare il codice aggiornato e scegliere
   Gemma nel progetto, con il servizio/modello configurati.
2. Creare un progetto di prova con il solo modulo
   `domanda-partecipazione.docx`, caricato in «Moduli da compilare». Se si riusa
   un vecchio modulo con zero frammenti, reindicizzarlo esplicitamente come sotto.
   Le KB globali sono condivise: un progetto nuovo non rende vuote tali KB.
3. Nella stessa conversazione inviare le tre domande, nell'ordine seguente.
   Per conoscere la KB esatta aprire gli strumenti sviluppatore del browser,
   scheda Network, risposta `POST /api/projects/{id}/answer`, array `evidence`.
   La UI mostra già Modulo/Fonte e nome; i campi scope/category sono nell'API.

| Domanda | Retrieval atteso | Evidenze e comportamento da controllare |
|---|---|---|
| «riassumi la domanda di partecipazione» | FORM (`target=form`) | Solo `role=form`, `file_id` del modulo, `project_id` del progetto, `scope=project:ID`, category null. Il testo descrive sezioni, dichiarazioni e allegati del modulo; nessuna evidenza globale lo sostituisce. |
| «qual è la partita IVA di Mapi?» | SOURCE (`target=source`) | Solo `role=source`: fonti del progetto o globali, scope e categoria reali. Un valore deve essere sostenuto dal testo della fonte, non dal form. Se non ci sono riscontri, deve indicarlo senza inventare il numero. |
| «con i documenti che ho posso iniziare a compilarlo?» | MIXED (`target=mixed`) | FORM per requisiti, poi SOURCE cercate con query derivate dai requisiti. Se si trovano fonti pertinenti, vedere entrambe le etichette Modulo/Fonte e controllare che i valori verifichino una Fonte. Tre sezioni: requisiti, informazioni verificate nelle fonti, informazioni non ancora verificate. Zero riscontri validi deve impedire ogni affermazione di compilabilità. Non genera/modifica DOCX. |

Per una prova controllata aggiungere in Company KB una fonte di test che documenti
denominazione e partita IVA di Mapi, poi ripetere la seconda e la terza domanda:
le citazioni dei valori devono rimandare a quella fonte, con `scope=global` e
`category=company`. Ripetere con FTS5 e Qdrant nelle impostazioni del retrieval;
per Qdrant servono il modello di embedding e il servizio configurati. Per il
confronto parziale usare un modulo con denominazione sociale e direttore tecnico,
e una fonte con solo la denominazione: questa può risultare verificata, il
direttore deve restare non verificato se nessun'altra fonte ammessa lo documenta.
Le KB globali restano condivise e possono già contenere altri riscontri.
La terza richiesta è stata riprodotta con Gemma su copie temporanee come sopra;
le tre richieste dalla UI e la verifica reale FTS5 restano da eseguire dall'utente.

### Reindicizzazione dei moduli già caricati

Nessun backfill automatico. Da `backend/`:

```bash
uv run --locked python -m scripts.reindex_project_forms --project ID_PROGETTO
# Per un solo modulo:
uv run --locked python -m scripts.reindex_project_forms --project ID_PROGETTO --form-id ID_MODULO
```

La transazione per ciascun modulo sostituisce i suoi frammenti e aggiorna il
conteggio, mantenendo identità e byte dell'originale. FTS5 è subito aggiornato.
Qdrant riconcilia i dati alla ricerca successiva; `--sync-vectors` lo fa subito
se configurato. Aggiornare soltanto Qdrant non estrae il testo dei vecchi moduli.
Il comando non è stato eseguito sul progetto locale `prova` o su altri dati utente.

### Limiti rimasti

- La selezione linguistica del modulo e la classificazione generale restano
  affidate al modello; il controllo di disponibilità copre espressioni italiane
  esplicite, non ogni parafrasi. Più moduli senza selezione attendibile producono
  informazione insufficiente. Non garantisce ogni interpretazione della domanda.
- Otto evidenze non garantiscono un riassunto esaustivo del documento. FTS5
  resta lessicale, Qdrant semantico: la selezione dei frammenti può differire,
  mentre le regole di accesso ai due ruoli sono equivalenti.
- Vengono indicizzati testo del corpo DOCX e tabelle (anche controlli testuali),
  non OCR, intestazioni, piè di pagina o note esterne al corpo. Un DOCX senza
  testo resta archiviabile, con stato «Senza testo estraibile» e zero frammenti.
- L'esattezza semantica delle risposte/citazioni richiede valutazioni reali;
  una risposta form può comunque essere interpretata male dal modello.
- Per mixed il controllo di ruolo, estratti letterali, valori e associazione
  testuale impedisce l'uso del form come prova di disponibilità, ma non è una
  dimostrazione completa di pertinenza semantica o appartenenza al soggetto.
  Può lasciare non verificati dati presenti altrove o con formulazioni diverse.
  Nessuna etichetta company/general prova da sola che il dato sia fattuale.
- L'estrazione seleziona al massimo 16 requisiti nei quattro frammenti FORM
  recuperati, da un output limitato a 32 proposte;
  può omettere requisiti o scegliere campi generici di sezioni diverse, come
  nella prova reale. Il confronto non è un audit completo dell'archivio e non
  risolve, certifica o rende persistente lo stato di tutti i campi del modulo.
- Il controllo SOURCE resta testuale e conservativo. Il numero albo 8421 è
  verificato dopo la correzione del 6 ottobre; rimangono falsi negativi del
  matcher, come codice fiscale/partita IVA nel caso A pur presenti nel contesto.
  Le domande ampie
  possono selezionare condizioni non applicabili, senza un'analisi completa
  dell'operatore e delle alternative previste nel modulo. La copertura SOURCE
  è ora esplicita, ma non dimostra da sola la completezza delle proposte del modello.

## Proposta da discutere: collegamento delle sessioni alla chat

La V1 backend descritta all'inizio implementa già sessione, aggiornamenti e
rigenerazione. Rimane da discutere il collegamento alla chat, per un DOCX:

1. Selezionare il modulo archiviato dal compositore, con pulsante o `@`.
2. Analizzare struttura e campi; cercare le informazioni nelle fonti appropriate.
3. Presentare una prima proposta con dati supportati, mancanti e ambigui.
4. Chiedere chiarimenti mirati e registrare le risposte/correzioni dell'utente.
5. Aggiornare e validare lo stato; rigenerare ogni versione dall'originale.
6. Mostrare nella chat una scheda persistente con stato, problemi, versione,
   download della bozza e report.

L'iterazione comprende proposta, verifica, ricerca/chiarimento e aggiornamento,
con limiti e condizioni di arresto. Ripetere chiamate al modello o dividere i
campi in gruppi, da soli, non realizza questo percorso.

Da chiarire nella discussione: come selezionare il modulo/sessione e mostrare
i problemi e i chiarimenti nella chat. L'iterazione backend e i suoi limiti sono
già stati richiesti esplicitamente e implementati, non vanno riprogettati da zero.
La lettura RAG e il confronto informativo sono disponibili; le prove reali
storiche hanno evidenziato falsi negativi conservativi. Evitare di chiedere
nuovamente all'utente l'intera storia o di trattare queste proposte come decisioni
già approvate.
