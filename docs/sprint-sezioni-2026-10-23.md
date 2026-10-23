# Sprint sulla compilazione per sezioni (rev 3), 23 ottobre 2026

Lavoro offline, zero chiamate LLM. Branch locale `sprint/2026-10-23-sezioni`, worktree
`/home/montesano/tesi-sprint`, base `dd41e2e`. Nulla è attivo nell'app live: ogni correzione è
una revisione opt-in delle nuove sessioni rev 3.

**Riferimenti:**
- **Grezzi e strumenti:** `backend/data/compilation-audit/sprint-sezioni-20261023-01/`
  (esclusa da Git).
- **Congelamento della base:** `BASE-FREEZE.json` (326 file, base `dd41e2e`).
- **Suite di partenza:** `out/suite-base.log` (3.677 PASS, Ruff PASS).

## PASSO 1 — sicurezza dei rami del FORM

### Controesempi (fase A)

Tabella completa: `out/controesempi-passo1.json`, prodotta da `controesempi_passo1.py` a partire
da `out/diagnosi-rami.json` e `out/rigioco-r1.json`.

**Scenari congelati:** tutti chiedono partecipazione singola come società di ingegneria, senza
raggruppamenti, consorzi o altre forme. Le 25 scritture rev 2 sono tutte accertate dalla revisione
autoriale.

| Tentativo rev 2 | Destinazioni | Ramo applicabile | Ramo scritto | Perché è passata | Chiusura |
|---|---|---|---|---|---|
| minervino-1 | `p37.s1-s7` (7) | `p39`, società | `p35`, studio associato | condizione `s1_c35` ancorata all'opzione, aperta, con scope solo su `p36` | **R1, deterministica** |
| soresa2023-1 | `p127.s1-s4` (4) | `p123`, nessun avvalimento | `p125`, avvalimento: l'ausiliaria è un terzo | `s2_c_sing` (partecipazione singola, confermata) legata dal modello all'avvalimento | rev 3: guardia d'ambito, semantica |
| soresa2023-1 | `p44.s0-s1` (2) | dichiarante singolo | blocco di un componente RT sotto `p19` | `s2_c_sing` ancorata a `p33`, dove «singolo componente il RT» è stato letto come «partecipazione singola» | rev 3: guardia d'ambito, semantica |
| soresa2023-2 | `p127.s2-s4` (3) | nessun avvalimento | avvalimento | nessuna condizione | nessuna deterministica |
| soresa2023-2 | `p43.s8-s9`, `p44.s0-s1` (4) | dichiarante singolo | componente RT | nessuna condizione | nessuna deterministica |
| catanzaro-2 | `t19.*` (5) | 5.d società di ingegneria (`s4_c1` confermata) | 5.c società di professionisti | nessuna condizione sull'intestazione 5.c | nessuna deterministica |

**Casi collegati:**
- **`p31.s0` di So.Re.Sa.** (nome USER nel blocco di un componente RT): non è un'opzione, quindi R1
  non lo tocca. Nella rev 3 un valore USER richiede comunque una ricevuta d'ambito verificata.
  Invariato.
- **`s2_c_sing`:** è la condizione che ha autorizzato in rev 2 sei delle 25 scritture. Nella rev 3
  quelle sei restano bloccate senza una prova d'ambito della guardia: è una protezione semantica,
  non deterministica.

**Cronologia (dichiarata):**
1. La diagnosi strutturale (`diagnosi_rami.py`) e la misura dell'effetto di R1 sulle scritture
   registrate (`valuta_r1.py`) sono state eseguite **prima** del collegamento ai gate.
2. Questo file di risultati attesi è stato scritto **dopo** l'implementazione.
3. I numeri attesi (7 chiuse, 0 falsi rifiuti) erano già stati misurati e non sono cambiati.

### Correzione minima (fase B): R1, `branch_scope_revision 1`

**Regola:**
- **Opzione:** un paragrafo del corpo che comincia con una casella nativa o con un simbolo di
  casella V14.
- **Continuazione:** i paragrafi che seguono l'opzione, fino al primo di questi confini:
  - paragrafo vuoto;
  - nuova opzione;
  - grassetto senza campi;
  - separatore senza lettere né cifre;
  - tabella.
- **Effetto:** una condizione del modello ancorata all'opzione viene collegata anche alle
  destinazioni della continuazione, come il validatore V12 la collega al paragrafo d'origine.
- **Conseguenza:** domanda, ricevuta d'ambito rev 3, stato di applicabilità ed export trattano le
  destinazioni estese come quelle dichiarate.

**Limiti della regola:**
- **Cosa non fa:**
  - non crea condizioni;
  - non decide rami;
  - non legge le intestazioni né parole come «OPPURE»;
  - non tocca le opzioni senza condizione ancorata.
- **«[ ]»:** come in V14 non è riconosciuto, né come opzione né come confine. Un tratto più lungo
  può solo trattenere di più.
- **Campo con condizione omessa:** il validatore V12 lo respinge. R1 invece lo rende CONDIZIONATO,
  cioè in attesa della risposta USER.
- **Tracciabilità:** ogni collegamento aggiunto è registrato in
  `audit.branch_scope.option_continuations` con origine BACKEND.

**Attivazione:** solo nuove sessioni con `MAPI_GENERATION_REVISION=3` e
`MAPI_BRANCH_SCOPE_REVISION=1`. Il collegamento avviene nell'unico punto di validazione
dell'audit rev 2/3 (`validated_audit`). Lì il catalogo viene ricostruito dall'originale, perché lo
stato pubblico reclamato non lo contiene; nei 14 tentativi le continuazioni sono identiche a
quelle del catalogo salvato. Il validatore V12, il percorso monolitico, parser, writer e retrieval
sono invariati.

**File:**
- `backend/app/compilation_branch_scope.py` (nuovo);
- `backend/app/compilation_global_sessions.py`: flag delle nuove sessioni, collegamento in
  `validated_audit`, propagazione del flag allo stato effettivo;
- `backend/tests/test_compilation_branch_scope.py` (nuovo, 26 test).

### Verifiche (fase C)

- **Rigioco dei gate** (`rigioco_r1.py`, codice dello sprint): risposte di segmento registrate di
  14 tentativi (8 rev 2, 6 rev 3), unite e validate con il codice rev 3.

  | | Senza R1 | Con R1 |
  |---|---|---|
  | Sbagliate esportabili, ricevute registrate | 19 / 25 | 12 / 25 |
  | Sbagliate esportabili, guardia simulata SUPPORTED | 25 / 25 | 18 / 25 |
  | Corrette esportabili, guardia simulata (103 rev 2 + 142 rev 3) | 245 / 245 | 245 / 245 |
  | Corrette esportabili, ricevute registrate | 211 / 245 | 211 / 245 |
  | **Nuovi falsi rifiuti** | — | **0** |

  Le 34 corrette perse con le ricevute registrate sono le stesse con e senza R1: ricevute rev 2
  senza prova d'ambito rev 3.
- **Estensione delle regioni** (`valuta_r1.py`, 718 scritture corrette di quattro campagne,
  monolitica inclusa):
  - R1 tocca soltanto le 7 scritture sbagliate di minervino-1;
  - nessuna scritta corretta;
  - nessuna condizione diventa una domanda nuova: le domande esistenti includono solo più
    destinazioni.
- **Alternativa scartata, R1':** compilare la continuazione solo se la casella dell'opzione è
  spuntata. Avrebbe respinto 116 scritture corrette: nei tentativi per sezioni la casella `p39`
  spesso non viene spuntata, un difetto di coerenza del documento ma non di sicurezza.
- **Test deterministici** (26):
  - regioni e confini;
  - il controesempio registrato senza e con R1;
  - risposte USER negative, rinviate, ambigue e revocate;
  - ricevuta vincolata al solo scope del modello;
  - conferma dell'altro ramo;
  - ramo applicabile preservato;
  - nessuna condizione creata;
  - idempotenza;
  - solo rev 3 con flag;
  - profilo delle nuove sessioni;
  - sessione completa con provider simulato: domanda estesa, export 409 sulla destinazione
    estesa, bozza valida senza.
- **Sensibilità:** con R1 neutralizzato 17 test falliscono; passano i 9 negativi e di profilo.

### Limite documentato

Restano esportabili 18 scritture su 25 se il modello ripetesse le uscite rev 2 e la guardia
confermasse l'ambito. Per chiuderle in modo deterministico servirebbe un'interpretazione
semantica delle sezioni:
- l'intestazione So.Re.Sa. `p19` vale anche oltre le intestazioni annidate e i separatori;
- 5.c e 5.d di Catanzaro sono alternative esclusive;
- l'avvalimento di `p125` riguarda un terzo.

Come da istruzioni non è stata tentata. Nei 9 tentativi rev 3 osservati quelle destinazioni non
sono mai state proposte, ma è un comportamento osservato del modello con il FORM completo, non una
garanzia. La sicurezza generale dei rami **non** è dimostrata da questi 25 casi.

## PASSO 2 — sospensioni del narratore

**Riferimenti:**
- **Classificazione e risultati attesi:** `PASSO2-ATTESI.md`, scritto alle 15:34:56 UTC prima del
  codice del passo, con hash registrato.
- **Strumenti:** `sospensioni_passo2.py`, `rigioco_passo2.py`.
- **Prove per campo:** `out/passo2-campi-recuperabili.json`.

### Diagnosi

**Minervino-2:** 21 proposte dei soci di Mapi Ingegneria sospese:
- `p43.*`, `p44.*`, `p45.*`: Luca Ferri ed Elisa Romano;
- `p47.s0`, `p48.*`, `p49.*`: Andrea Greco.

**Motivo dichiarato:** «ruolo del responsabile della progettazione o direttore tecnico non
confermato». Per Greco, «proposti nel blocco del Direttore Tecnico», cosa falsa: `p47`-`p49` sono il
terzo socio e precedono paragraph:50.

**Citazione:** è la clausola di paragraph:50, cioè la condizione `s2_c_dt_role`, che governa solo
`p51`-`p53`.

**Validazione del backend:** `UNANCHORED_QUOTE`, senza chiave di blocco. Per costruzione nessuna
via di rilascio: le sospensioni sono state ereditate fino all'export.

**Classificazione** (categorie richieste):
- **«già risolta da verifiche backend valide»: 21/21.** Per ciascuna:
  - valore SOURCE dalla tabella «Soci della società al 15 ottobre 2026»;
  - binding di ruolo `socio` con esito `literal_match`;
  - unica condizione propria (ramo società, `s2_c_soc_branch`) vera per ricevuta USER con prova
    d'ambito, che comprende la destinazione;
  - stesso valore scritto e giudicato DIMOSTRATA nel gemello minervino-1.
- **Giustificate da un dubbio documentale reale:** 0.
- **Ambigue:** 0.

È il caso descritto al punto 3: il narratore rimette in discussione una relazione verificata
citando la condizione di altre destinazioni, senza indicare una contraddizione.

**Criterio deterministico M:** tutte queste condizioni insieme:
- blocco `applicability`;
- citazione non ancorata;
- citazione uguale alla clausola di una sola condizione del modello;
- quella condizione non governa la proposta.

**Esito su 145 sospensioni registrate** (quattro campagne): individua esattamente queste 21, nessun
falso positivo.

**Fuori dal criterio:**
- le sospensioni non ancorate con blocco `source`: 41 (14 nella campagna arrestata, 23 nella
  monolitica, 4 in rev 2);
- le sospensioni `RECORDED`.

Non sono state giudicate né toccate.

### Correzione: `hold_rereview_revision 1`

Il backend **non** rilascia nulla. Una sospensione che soddisfa M resta sospesa e viene marcata «da
rivedere» (`misattributed_condition`, `rereview: pending`):
1. **Revisione unica.** Alla narrazione successiva la proposta rientra nella finestra di revisione,
   una sola volta. `previous_hold.backend_check` spiega che la clausola citata governa altre
   destinazioni.
2. **Se il narratore la sospende di nuovo,** la sospensione è definitiva, senza altre revisioni.
   Un motivo ancorato segue il meccanismo esistente.
3. **Se non la sospende di nuovo,** torna ai gate invariati del backend (`release_reason:
   MODEL_REREVIEW`).

La decisione resta del narratore. Nessuna conferma USER sostituisce SOURCE e nessun gate d'export
cambia.

**Attivazione:** solo nuove sessioni con `MAPI_GENERATION_REVISION=3` e
`MAPI_HOLD_REREVIEW_REVISION=1`.

**File:**
- `backend/app/compilation_hold_rereview.py` (nuovo);
- `backend/app/compilation_global_dialogue.py`:
  - finestra di revisione;
  - `_hold_updates`;
  - `previous_hold` nel contesto;
- `backend/app/compilation_global_sessions.py`: flag;
- `backend/tests/test_compilation_hold_rereview.py` (nuovo, 14 test).

### Verifiche

**Rigioco** (`rigioco_passo2.py`), controfattuale in memoria sullo stato finale di minervino-2 con
R1 attiva:

| | Prima | Dopo, il narratore non le risospende | Dopo, il narratore le risospende |
|---|---|---|---|
| Sospensioni marcate M / rientrate in revisione | 0 / 0 | 21 / 21 | 21 / 21 |
| Sospese dopo la revisione | 21 | 0 | 21 (definitive) |
| Export SOURCE + USER | 30 + 2 | 51 + 2 | 30 + 2 |
| Aggiunte all'export | — | esattamente le 21, tutte DIMOSTRATA con lo stesso valore nel gemello | 0 |
| Rimosse dall'export | — | 0 | 0 |
| Scritture nei rami sbagliati | 0 | 0 | 0 |

`p51`-`p53` (direttore tecnico) restano fuori in tutti i casi: `s2_c_dt_role` è UNKNOWN per la
guardia dei cicli. Il comportamento reale del narratore alla revisione non è misurabile offline.

**Test** (14):
- criterio M: condizione propria, governata, citazione ambigua o assente, normalizzazione;
- sospensioni non toccate: `source`, ancorate, senza condizione;
- flag spento come prima;
- riferimento non risolvibile alla revisione: resta sospesa e la revisione è consumata;
- sospensione fuori dalla finestra: né rilasciata né consumata;
- profilo;
- tre sessioni con provider simulato:
  - rilascio dopo la revisione con export e bozza 200, la destinazione dell'altra condizione
    sempre esclusa (409);
  - risospensione definitiva senza nuovo ciclo;
  - flag spento.

**Sensibilità:** con la correzione neutralizzata falliscono i 7 test positivi.

## PASSO 3 — ripresa delle compilazioni segmentate

**Riferimenti:**
- **Scenari e risultati attesi:** `PASSO3-ATTESI.md`, scritto alle 15:41:39 UTC prima dei test,
  con hash registrato.
- **Test:** `backend/tests/test_compilation_rev3_resumption.py`, 10 scenari (23 casi con le
  parametrizzazioni).
- **Profilo dei test:** candidata completa: rev 3, dialogo P3, derivazione, recupero del
  narratore, R1, revisione unica.

**Nessun nuovo orchestratore:** cache per digest della richiesta, retry limitati e recupero del
narratore sono quelli esistenti.

| # | Scenario | Esito |
|---|---|---|
| 1 | Interruzione dopo segmenti validati | FAILED, nessun audit né valore esportabile, cache con i soli 2 segmenti validati, bozza 409 |
| 2 | Ripresa | 2 segmenti dalla cache, 1 chiamato; bozza 200 con gli stessi gate |
| 3 | Nessuna duplicazione | una sola chiamata per il segmento mancante; destinazioni uniche nell'audit e nell'export |
| 4 | SOURCE modificata | nessun segmento dalla cache, 3 chiamate |
| 5a | Decisioni USER nel digest | digest uguale con le stesse decisioni, diverso con conferma e con revoca, in ogni segmento |
| 5b | Decisione revocata o condizione cambiata | la destinazione dipendente esce dall'export (bozza 409), quella indipendente resta (bozza 200) |
| 6 | JSON non valido in un segmento | solo quel segmento fallisce, senza riparazione; 4 valori indipendenti esportabili |
| 7 | Conflitto fra segmenti | le destinazioni in conflitto vanno in revisione e sono rifiutate se forzate; la proprietà indipendente resta |
| 8 | Retry esauriti | 2 retry per analisi, tentativi [2, 2, 1]; il segmento indipendente resta; con tutti i segmenti falliti nessun valore |
| 9 | Narratore fallito due volte | modalità degradata con audit e sospensioni invariati; la ripresa rifà solo la sintesi, senza chiamate di analisi; la sospensione resta |
| 10 | Export parziale | bozza 200 con le sole destinazioni ammesse; i limiti restano espliciti: riepilogo con pending, segmento fallito, copertura UNASSESSED, report |

### Difetto trovato e corretto (scenario 10)

**Difetto:** la rivalidazione finale lato server (`_selected`, endpoint `global-draft`) non
controllava revisione e sospensioni del narratore fuori dalla modalità degradata. Un client che
chiedeva esplicitamente una proposta sospesa otteneva 200 e un DOCX con quel valore.

**Portata:**
- Chat e UI usano `export_selection`, che la esclude.
- `generateGlobalDraft` del frontend non è usato da nessun componente.
- La lacuna esiste in ogni profilo.

**Correzione minima, solo per `generation_revision 3`:** la rivalidazione finale rifiuta (409) gli
id che `export_selection` non ammetterebbe per revisione o sospensione
(`reviewed_unheld_ids`, `compilation_global_dialogue.py`).

**Non toccato:** il profilo ordinario, segnalato come rischio residuo.

**Sensibilità:** senza la correzione falliscono i casi dello scenario 10.

**Storico:** sulle scritture SOURCE dei 9 tentativi rev 3 la nuova rivalidazione non avrebbe
rifiutato nulla.

**Correzioni dei test:**
- Due attese iniziali erano sbagliate e le ho corrette:
  - il conflitto coinvolge per costruzione ogni segmento con la stessa proprietà;
  - la condizione va indicata con l'id rinominato dal merge.
- Non sono difetti del codice.
