# Narratore P3: correzione delle sospensioni e fallback dell'app live (22 ottobre 2026)

Stato: **candidata non adottata**. La V12 resta la baseline. Nessun commit, tag o push.
Audit offline: `backend/data/compilation-audit/narratore-p3-20261022-01/` (preregistrazione
`PREREG-NARRATORE.md`, SHA256 `042899fd…`, 07:56:32 UTC, con due addenda datati).
E2E: `benchmark ufficiale/narratore-p3-verifica-20261022-01/`, grezzo in
`backend/data/compilation-audit/narratore-p3-verifica-20261022-01/`.

## 1. App live: P3 disattivato per le nuove sessioni

- **Stato trovato** (`out/live-check-prima.json`). L'app live (uvicorn `--reload` sul working
  tree, porta 8000) creava le nuove sessioni con `dialogue_revision 1` e `generation_revision 1`.
  Nel database live nessuna delle 29 sessioni salvate ha flag di revisione; l'ultima risale al
  17 ottobre. Nessuna sessione P3 è stata quindi creata nell'app live.
- **Modifica** (`compilation_global_sessions.initial_state`). P3 diventa opt-in, con due variabili
  separate per un runtime sperimentale privato: `MAPI_DIALOGUE_REVISION=1` e
  `MAPI_GENERATION_REVISION=1`. Il profilo predefinito delle nuove sessioni è
  `backend_revision 13`, `option_authorization_revision 1` (V14),
  `attribution_safety_revision 1` (K3). Le sessioni esistenti conservano i propri flag:
  `resolve_global` li copia dalla sessione, non dall'ambiente. Il codice P3 resta intatto.
- **Verifica del fallback**:
  - worker live ricaricato dopo la modifica (09:50:55 contro il file delle 09:50:54), `/api/health`
    OK, nuove sessioni senza flag P3 (`out/live-check-dopo.json`);
  - albero pre-P3 ricostruito (candidate-code V14 + patch K3; 75/75 hash uguali allo snapshot
    pre-P3). Per i quattro FORM della verifica, profilo `initial_state` e corpo della richiesta
    globale sono identici al pre-P3 (`out/fallback-*.json`);
  - moduli V14/K3 identici al pre-P3;
  - replay delle 215 sintesi legacy registrate (V13, V14): risultati identici al pre-P3,
    impronta per impronta;
  - ogni altra differenza P3 nel codice è condizionata dai flag della sessione (data di
    riferimento, segmenti, registro iniziale, guardia semantica, ricevute `SEMANTIC_GUARD`).
    Unica eccezione trovata: due chiavi vuote che P3 aggiungeva alla transizione anche nelle
    sessioni legacy, ora limitate a P3 (addendum 1).
- Nota operativa: con `--reload`, anche gli script `.py` scritti sotto `backend/` (cartelle di
  audit comprese) riavviano il worker live. Era successo anche durante P3; con l'app inattiva
  non ha conseguenze sui dati.

## 2. Diagnosi dei quattro rifiuti (riprodotti offline, zero chiamate LLM)

`replay_failures.py` ricostruisce dallo snapshot persistito lo stato passato al narratore e
riesegue `narrate` con la risposta reale registrata. In tutti e quattro i casi il contesto
ricostruito coincide con quello della richiesta reale, il prompt è identico e l'errore è lo stesso.

| Prova | Fase | Proposte in revisione | Errore | Causa |
|---|---|---|---|---|
| minervino-A1 | prosecuzione | 11 | citazione | le due citazioni sono record SOURCE letterali presenti nel contesto (`source_availability`), ma fuori dalla zona ammessa per quelle proposte |
| minervino-B1 | iniziale | 40 | citazione | gruppo 35-38: citazione ancorata solo per la 36; gruppo 39-40: record SOURCE di `source_availability` |
| minervino-B2 | prosecuzione | 0 | esclusioni non valide | il narratore cita le proposte 1 e 2 con la finestra vuota (dubbio su una condizione del pool) |
| catanzaro-A2 | iniziale | 16 | citazione | la citazione è una motivazione MODEL della copertura (`coverage`), non un testo FORM o SOURCE |

Tutte le sospensioni con citazione erano dubbi SOURCE: ruolo o soggetto (Elisa Romano e Andrea
Greco come soci), oppure dati personali non documentati del direttore tecnico. Il validatore,
pensato per V12 con una citazione per proposta, respingeva l'intera sintesi al primo motivo non
ancorato. Con i gruppi P3 (una citazione per più proposte) il caso è diventato frequente, e la
conseguenza era l'assenza di domande e di export, non una scrittura in più.

Diagnosi aggiuntiva sul rilascio P3 (D4; `governance_check.py`): nelle 32 sintesi P3, 45
sospensioni sono state legate a uno slot per il rilascio. In 18 casi lo slot governa davvero la
proposta. Nelle altre 27 (tutte minervino-B2) lo slot riguardava RTP o studio associato, e queste
sospensioni sono state rilasciate dopo un rinvio su slot estranei. La loro citazione era la
clausola FORM di una condizione propria, già decisa dalla richiesta iniziale.

## 3. Correzione (solo sessioni con `dialogue_revision 1`)

In `compilation_global_dialogue.py` (136 righe di diff rispetto al codice della campagna):

- **Nessun rifiuto dell'intera sintesi per una sospensione dubbia.** Ogni riferimento viene
  valutato a parte e la proposta citata resta comunque sospesa:
  - citazione ancorata nella zona della proposta (regola esistente): `RECORDED`;
  - citazione non ancorata: `UNANCHORED_QUOTE`, motivo `unverified`, con la sezione del contesto
    in cui la citazione compare;
  - proposta citata in più gruppi: `REPEATED_REFERENCE`, con tutte le motivazioni.
- **Riferimenti inesistenti.** Con la finestra vuota vengono registrati per intero nella
  transizione, senza effetto: non c'è alcuna proposta da proteggere e le condizioni restano
  presidiate dai gate backend. Con la finestra non vuota la destinazione non è determinabile,
  quindi tutte le proposte della finestra restano sospese (`UNRESOLVED_REFERENCE`).
- **Rilascio per risposta solo con un collegamento verificabile.** Vale solo per motivi
  `RECORDED` con blocco `applicability` o `user_decision`, in uno di due modi:
  - lo slot indicato governa la proposta (`GOVERNING_SLOT`);
  - la citazione è la clausola FORM di esattamente una condizione propria
    (`OWN_CONDITION_QUOTE`).
  
  Altrimenti la sospensione resta. I legami già salvati nelle sessioni esistenti non vengono
  ricalcolati.
- **Invariati:** grounding, validatori FORM/SOURCE/USER, gate V14 e K3, prompt e schema del
  narratore, percorso legacy. Nelle sessioni V12/V14/K3 una citazione non ancorata respinge
  ancora l'intera sintesi.
- Solo una sospensione `RECORDED` può essere rilasciata per ridondanza (regola V12 esistente).

## 4. Verifiche offline

1. **Quattro risposte respinte** (`out/replay-failures-dopo.json`, esiti preregistrati in
   `out/predicted-failures.json`):
   - **minervino-A1:** accettata. Sospese tutte le 11 proposte (`UNANCHORED_QUOTE`) e mantenuta
     la sospensione precedente `p14.s0`. Domande: sottoscrittore e luogo/data. Export 39.
     Come previsto.
   - **minervino-B2:** accettata. Due riferimenti non validi registrati, nessuna nuova
     sospensione, tre domande. Export 35. Come previsto.
   - **catanzaro-A2:** accettata. Sospese le proposte 12-16, citazione da una motivazione MODEL.
     Proposta di bozza senza domande, export 11. Come previsto.
   - **minervino-B1:** accettata. Sospese le proposte 35-40, la 36 `RECORDED` e le altre
     `UNANCHORED_QUOTE`, come previsto. La fase però è PENDING e non READY: 50 proposte da
     rivedere con una finestra di 40, quindi la prosecuzione automatica V12 rivede le 10
     restanti. **Criterio non soddisfatto alla lettera:** è un errore della mia previsione,
     non della correzione (addendum 2), ma va dichiarato.
2. **Controesempi** (`tests/test_compilation_p3_hold_validation.py`, 13 test, 30 esecuzioni):
   - sospensione valida;
   - citazione di un'altra proposta e parafrasi;
   - sospensione non ancorata che non si rilascia con lo slot che nomina;
   - riferimento fuori da una finestra vuota;
   - riferimento non risolvibile con finestra non vuota;
   - riferimento ripetuto;
   - sospensione procedurale: dopo il rinvio la sospensione cade, ma senza autorizzazione
     accettata il gate V14 continua a impedire l'export;
   - slot che non governa la proposta;
   - citazione della propria condizione;
   - sessione legacy invariata;
   - sospensioni ereditate e fuori finestra;
   - opt-in di P3;
   - sessioni esistenti indipendenti dal predefinito dell'ambiente.
3. **Replay di tutte le 247 sintesi con risposta registrata** (V13 98, V13-validazione 99,
   V14 18, P3 32; `out/compare.json`):
   - **215 legacy:** identiche al pre-P3 e semanticamente identiche al codice della campagna;
   - **32 P3:** cambiano solo le quattro respinte e la sintesi minervino-B2 511ed591, dove le
     27 sospensioni legate a slot estranei vengono legate alla propria condizione, già decisa,
     e soppresse subito;
   - **replay a catena:** export finale identico per le 12 prove P3 riuscite;
   - in nessuna sintesi un'esportabile risulta bloccata da K3 o V14 (`out/r3-check.json`).
4. **Suite backend:** 3.509 test passati; Ruff pulito (`out/suite.log`).

## 5. Verifica E2E breve (preregistrata, 8 prove, nessuna sostituita)

Protocollo congelato prima dell'inferenza (`PROTOCOLLO-NARRATORE.json`, `HARNESS-FREEZE.sha256`,
08:15:47 UTC):
- **profilo:** runtime isolato con dialogo P3 e generazione monolitica (la segmentazione è
  esclusa e il confronto tra generazioni resta separato);
- **materiali:** stessi FORM, SOURCE, scenari e politica USER del braccio A della campagna P3,
  appaiati per documento e turno;
- **limiti:** budget di 1,5 milioni di token, 60 chiamate per prova.

Il codice applicativo è rimasto identico per tutta la campagna.

| Documento | Questa verifica (N1, N2) | P3 braccio A appaiato (A1, A2) |
|---|---|---|
| Minervino | 51/60, **nessun DOCX** | nessun DOCX (narratore), 16/60 |
| Cesano | 3/4, 3/4 (+ data equivalente: 4/4, 4/4) | 3/4, 3/4 (stesso criterio) |
| CRAA | 10/10 (autorizza), 8/10 (ramo) | 10/10, 8/10 |
| Catanzaro | 13/31, 8/31 | 14/31, nessun DOCX (narratore) |

Valori: campi core scritti uguali al riferimento congelato.

- **DOCX:** 7/8 (P3 A: 6/8).
- **Sintesi respinte dal backend:** 0 su 15 (P3 A: 2).
- **L'unico fallimento (minervino-N2) non dipende dal narratore.** La chiamata globale
  monolitica si è fermata al limite (49.152 token di output, di cui 35.706 di ragionamento).
  L'analisi è fallita prima di qualsiasi sintesi, l'export è stato rifiutato e il driver è
  andato in timeout dopo 1000 s. È la causa nota della generazione monolitica: in questa
  campagna 3 chiamate globali su 8 hanno superato il 75% del limite.
- **Sospensioni:** 16, tutte con citazione ancorata (`RECORDED`); nessuna citazione non
  ancorata, nessun riferimento non valido, nessun legame per il rilascio. **I nuovi percorsi
  non sono stati esercitati da risposte reali in questa campagna:** la loro verifica resta
  quella offline (sezione 4).
- **Scritture:** 0 non dimostrate (revisione dell'autore, non indipendente).
  - Fuori dai valori uguali al riferimento ci sono solo tre date in formato esteso equivalente
    («14 novembre 1982» per «14/11/1982»).
  - Restano le caselle di Cesano-N1 (`p19.cb0` vera, altre false), scritte da una scelta USER
    esplicita del gruppo attivo («Scelgo la voce Società di Ingegneria»), come in cesano-A2.
  - V14: CRAA scrive le CCIAA solo con autorizzazione accettata (N1); con il rinvio restano
    vuote (N2). Cesano scrive `p19.ft0` con autorizzazione accettata (2/2).
  - Nessuna scrittura in una regione d'opzione senza autorizzazione; nessun blocco K3 coinvolto.
- **Criterio sui documenti già riusciti:** soddisfatto. Le mediane di Cesano e CRAA sono uguali
  al braccio A appaiato; quella di Catanzaro è migliore (33,9% contro 22,6%).
- **Minervino 51/60 non va attribuito alla correzione.** Dipende soprattutto dall'output globale
  di quella prova, variabile fra un'esecuzione e l'altra: in P3 A2 molti campi avevano solo
  spiegazioni respinte. Il narratore ha sospeso 8 valori del riferimento, tutti con motivo ancorato.
- **Costi:** 1,01 milioni di token (P3 A: 0,99), mediana 149 s per prova (P3 A: 140 s).

## 6. Conferme ridondanti ancora presenti

Una sola, contro 4 nelle prove appaiate del braccio A: cesano-N1, slot `choice:grp_partecipazione`.
Il primo messaggio diceva già «partecipazione singola soltanto come società di ingegneria».
Il registro iniziale registra la condizione ma, per progetto, non converte una frase del primo
messaggio in una scelta di casella, quindi la scelta viene chiesta. Toglierla richiede una
decisione di prodotto (una frase iniziale può selezionare una casella?), non una correzione.
Non è stata toccata.

Altri indicatori del dialogo nelle 8 prove:
- domande identiche per tre turni: 0;
- condizioni aperte mai chieste: 0;
- sospensioni con blocco risolto e non rilasciate: 0;
- risposte non accettate: 0;
- interventi della guardia sui cicli: 0.

## 7. Limiti e rischi residui

- La correzione rende la gestione più prudente, a costo di copertura:
  - una sospensione con citazione non verificabile non si rilascia più automaticamente
    (resta fino a una nuova revisione della proposta);
  - un riferimento non risolvibile sospende l'intera finestra.

  Offline, in minervino-A1 restano vuoti gli 11 dati dei soci 2 e 3, che il riferimento considera
  documentati.
- Il legame `OWN_CONDITION_QUOTE` si basa sull'uguaglianza letterale con la clausola FORM. Se il
  narratore cita la clausola giusta per un dubbio diverso, la sospensione cade quando la
  condizione riceve risposta. In ogni caso resta il gate backend della condizione.
- Campione piccolo (8 prove). I percorsi nuovi sono stati provati offline sulle 4 risposte reali
  e su controesempi, non da nuove risposte reali.
- Il troncamento della generazione monolitica resta il primo motivo di prove perse. Riguarda
  anche la baseline V12/V14, che usa la stessa chiamata.
- La segmentazione non è stata rivalutata: resta opt-in e non predefinita (2,7× token in P3,
  senza guadagno di copertura dimostrato).
- I quattro rischi residui di P2/K3 restano aperti; questo intervento non li tocca.
- Errore di previsione dichiarato su minervino-B1 (addendum 2). Addendum 1 sulle due chiavi
  della transizione.
- Revisione delle scritture fatta dall'autore, non indipendente.

## 8. Decisione sulla riattivazione di P3

I criteri preregistrati sono soddisfatti:
- offline: tutti, con l'eccezione dichiarata di minervino-B1;
- E2E: 0 sintesi respinte; 7/8 DOCX con causa estranea al narratore e documentata; 0 scritture
  non dimostrate; 0 aggiramenti V14/K3; nessun peggioramento sui documenti già riusciti.

Secondo la sezione 7 della preregistrazione posso quindi **proporre** la riattivazione del solo
dialogo P3. Non lo rendo predefinito e la decisione resta all'utente.

**Raccomandazione motivata:** tenere il dialogo P3 **disattivato nell'app live** e usarlo come
candidata (`MAPI_DIALOGUE_REVISION=1`, generazione monolitica) nella valutazione finale con i
criteri congelati. Motivi:
1. i percorsi corretti non hanno ancora visto risposte reali problematiche;
2. 8 prove non bastano per un predefinito;
3. il rischio dominante osservato oggi è il troncamento della generazione, che il dialogo non
   risolve.

La generazione per sezioni resta disattivata e da decidere a parte (eventuale soglia di
dimensione).

Prossime attività strettamente necessarie:
1. decisione dell'utente sul profilo P3 (resta opt-in o diventa candidata per la valutazione
   finale);
2. valutazione finale preregistrata con i criteri congelati, includendo documenti come Minervino,
   dove il narratore produce sospensioni di gruppo;
3. decisione separata sul troncamento della chiamata monolitica (soglia per la segmentazione o
   altra misura), perché oggi è la prima causa di prove senza DOCX.

## 9. File e riproducibilità

- Offline: `backend/data/compilation-audit/narratore-p3-20261022-01/` (README con l'ordine
  cronologico, `albero-preP3/` ricostruito, `out/`).
- E2E: `backend/data/compilation-audit/narratore-p3-verifica-20261022-01/` (chiamate, snapshot,
  browser), `benchmark ufficiale/narratore-p3-verifica-20261022-01/` (protocollo, prove, DOCX,
  `ANALISI-NARRATORE.json`, `RIEPILOGO-NARRATORE.json`).
- Backup verificato per estrazione (1.046 file, nessuna differenza, nessuna chiave):
  `backend/data/compilation-audit/narratore-p3-backup-20261022/narratore-p3-audit-completo.tar.gz`
  (68 MB, SHA256 `aaaff81d96f0612d09a0239fb9fecf6443408c425eb5c0507c0d70f5e9278be2`, con `MANIFEST.sha256`; escluso da Git).
- Il runtime privato `.tools/narratore-p3-verifica-20261022-01/` contiene la chiave ed è escluso
  dal backup.
- Codice:
  - `backend/app/compilation_global_sessions.py`: P3 opt-in;
  - `backend/app/compilation_global_dialogue.py`: correzione;
  - `backend/tests/test_compilation_p3_hold_validation.py`: nuovo;
  - tre file di test adeguati all'opt-in.
