# Sezioni resilienti e coerenza dello stato derivato (22 ottobre 2026)

Ultima revisione architetturale mirata della compilazione DOCX, limitata a due risultati:
1. correggere l'invalidazione incoerente dello stato derivato dopo le risposte USER (HTTP 409 di
   minervino-1);
2. rendere la generazione per sezioni resiliente, verificabile, riprendibile e sicura.

Le due modifiche sono **candidate opt-in, non adottate**:
- `derivation_revision 1`, attivata da `MAPI_DERIVATION_REVISION=1`;
- `generation_revision 2`, attivata da `MAPI_GENERATION_REVISION=2`.

V12 resta la baseline congelata. App live invariata: 29 sessioni, nessun flag sperimentale, ultima
modifica al 17 ottobre. Nessun commit, tag o push.

Riferimenti:
- **Piano:** `PIANO-SEZIONI-RESILIENTI.md`, congelato prima del codice, con `ADDENDUM-1-PIANO.md`
  congelato prima delle inferenze.
- **Preregistrazione E2E:** `PREREG-E2E-SEZIONI.md`.
- **Grezzo:** `backend/data/compilation-audit/sezioni-resilienti-20261022-01/`.
- **Risultati E2E:** `benchmark ufficiale/sezioni-resilienti-20261022-01/`.

## Esito in breve

| Domanda | Esito |
|---|---|
| A. Correzione del 409 | **Dimostrata**: riproduzione deterministica di minervino-1 (409 senza flag, export riuscito con il flag) e 5 casi USER nei test. Nell'E2E 0 risposte 409 |
| B. Segmentazione | Invarianti strutturali verificati offline. **Nell'E2E nessun segmento è fallito**, quindi la resilienza ai fallimenti è dimostrata solo offline |
| C. Ripresa | Verificata offline: cache per digest, chiamate solo dei segmenti mancanti, cache corrotta ignorata, richieste diverse mai unite. Nessuna interruzione osservata nell'E2E |
| D. Applicabilità | Tre stati implementati. I casi riconoscibili sono conservativi. **Il rischio residuo dichiarato si è materializzato nell'E2E:** 25 scritture in rami non pertinenti, tutte valutate VERIFICATA |
| E. Affidabilità | 7/8 DOCX (1 fallimento del narratore); 0 segmenti persi; **25 scritture non dimostrate** in 4 DOCX su 7 (revisione autoriale) |
| F. Costi | 1,85 M token (tetto 3 M), 0,37 USD. Analisi 1,3-2,4× i token della monolitica, non appaiata |
| H. Giudizio | **Non pronta** per ulteriori valutazioni (criterio preregistrato (a)) |

## A. Correzione del 409: dimostrata

- **Causa (minervino-1):**
  - l'audit salvato conteneva il riuso del firmatario, ricavato dalla scelta esplicita nel primo
    messaggio;
  - il pianificatore ha registrato come SKIP la risposta «Il firmatario scelto per questa domanda
    è …» sullo slot `field:p12.s0`;
  - con una ricevuta SKIP il riuso decade, ma `apply_replies` ricalcolava l'audit solo se il
    riuso era richiesto *dopo* la risposta, oppure dopo CONDITION_TRUE/FALSE;
  - l'export selezionava quindi 9 campi dall'audit vecchio e il veto finale li trovava cambiati:
    HTTP 409.
- **Correzione (`derivation_revision 1`, opt-in, isolata):**
  - dopo ogni mutazione accettata `apply_replies` ricalcola `refreshed_audit` dall'output immutabile
    del modello e dalle ricevute correnti;
  - se l'audit cambia, lo salva come audit di revisione.

  Il veto finale dell'export è invariato. Un rinvio non autorizza nulla: il riuso sparisce.
- **Riproduzione deterministica** (`replay_minervino1.py`):
  - clona il runtime della valutazione finale;
  - riporta la sessione allo stato v006;
  - ripete le stesse richieste HTTP della UI e restituisce le risposte registrate del provider.

  Esiti:
  - senza flag: 409 all'export, 9 campi di riuso nell'audit salvato dopo lo SKIP;
  - con flag: 0 campi di riuso, export riuscito, bozza generata.

  Rieseguita con il codice definitivo: stesso esito (`out/replay-minervino1-finale-*.json`).
- **Test** (`test_compilation_derivation.py`): rinvio (con e senza flag), conferma, revoca, cambio
  di risposta, risposta su uno slot differente.

  Dopo ogni risposta l'audit salvato coincide con quello ricalcolato e l'export non dà 409. Senza
  flag il difetto resta riprodotto.
- **Isolamento:**
  - il flag si attiva solo con `MAPI_DERIVATION_REVISION=1` sulle nuove sessioni ed è
    indipendente dalla segmentazione (test dedicato);
  - sessioni storiche e profilo ordinario seguono il ramo precedente;
  - replay di 247 sintesi registrate (V13, V14, P3) identiche e 16/16 catene P3 identiche;
  - suite completa verde.

## B. Segmentazione: verificato offline / soltanto ipotizzato

**Verificato offline** (test deterministici, zero chiamate LLM):

- **Proprietà:**
  - ogni destinazione ha un solo segmento proprietario;
  - le unità di dipendenza (blocco FORM, paragrafi locali condivisi, regioni d'opzione V14) non
    vengono mai divise;
  - ordine di documento;
  - l'intestazione più vicina, la clausola d'opzione, i paragrafi che estendono lo scope delle
    condizioni e il paragrafo d'avvio delle continuazioni sono nel contesto del segmento;
  - sui 7 moduli reali: 0 paragrafi di clausola fuori contesto.
- **Validazione prima del merge:**
  - ogni segmento passa il validatore V12 da solo, con i budget ordinari;
  - JSON incompleto, struttura errata, budget superato e chiave duplicata fanno fallire **solo**
    quel segmento, dopo un retry;
  - nessuna riparazione: le risposte grezze restano salvate;
  - caratteri di controllo letterali nelle stringhe sono accettati, come P3.
- **Fallimento isolato** di ciascuno dei 3 segmenti:
  - gli altri vengono uniti e restano esportabili;
  - le destinazioni del segmento fallito sono UNASSESSED con motivo BACKEND e NON ACCERTATE.

  Se falliscono tutti, l'analisi fallisce senza valori.
- **Merge:**
  - l'unione è validata con `budget_scale` = numero di segmenti, quindi i budget per chiamata
    non invalidano segmenti validi;
  - se l'unione fallisce, esclusione deterministica e registrata del segmento che la rompe;
  - condizioni equivalenti di segmenti diversi unificate (una risposta USER vale per tutti gli
    scope);
  - condizioni diverse sullo stesso paragrafo registrate e non unite;
  - valori SOURCE diversi per lo stesso soggetto e proprietà → revisione «conflicting», nessuna
    scelta nascosta.
- **Retry:** 1 per segmento, 2 per analisi, registrati e contati; un retry riuscito è registrato
  come secondo tentativo dello stesso segmento.
- **Compatibilità:**
  - validatore con `budget_scale=1` ricostruito dal congelamento (hash identico): 193/193 risposte
    globali registrate danno audit o errore identici;
  - suite backend 3.560 PASS, Ruff PASS.

**Soltanto ipotizzato o non verificato:**

- che il modello, vedendo solo il contesto locale, proponga gli stessi dati della monolitica
  (qualità reale: vedi E);
- che i riferimenti incrociati lontani («come indicato al punto 3») siano visti: il backend non li
  riconosce e non sono nel contesto;
- che la riduzione dei token compensi la ripetizione del prefisso (SOURCE e schema in ogni
  segmento): vedi F.

## C. Ripresa: che cosa accade davvero

- **Interruzione:** ogni segmento validato viene salvato subito in
  `segment-cache/<sha256 della richiesta>.json`, con risposta grezza, tentativi e riferimenti
  espliciti della revisione degli input:
  - hash di SOURCE, contesto USER, valori USER e FORM del segmento;
  - contratto e data di riferimento.

  Nel test, con un'interruzione al terzo segmento la sessione va in FAILED ma i due segmenti
  validati restano.
- **Ripresa esplicita** (controllo «riprendi» esistente, nessun nuovo sistema di job):
  - la nuova analisi ricostruisce le richieste;
  - riusa le voci con lo stesso digest, che vengono ripassate dal validatore strutturale;
  - chiama solo il segmento mancante (1 chiamata invece di 3);
  - l'unione passa gli stessi controlli e l'export lo stesso veto finale.
- **Cache corrotta:** la voce viene ignorata e il segmento richiamato.
- **Richieste diverse** (una SOURCE in più): cambiano tutti i digest, nessuna voce viene
  riusata né unita.
- **Decisioni USER modificate:**
  - le risposte date dopo l'analisi non entrano nelle richieste del modello, quindi non
    invalidano i segmenti;
  - invalidano lo stato derivato (riuso, rami, sospensioni, fingerprint delle revisioni), che con
    `derivation_revision 1` viene ricalcolato a ogni risposta.
- **Limiti:**
  - un cambio del contesto USER registrato prima dell'analisi invalida *tutti* i segmenti (ognuno
    lo riceve intero): è conservativo, non selettivo;
  - la data di riferimento fa parte della richiesta, quindi una ripresa in un altro giorno
    rianalizza tutto;
  - non c'è un percorso per rianalizzare i soli segmenti falliti di un'analisi già conclusa in
    REVIEW;
  - la ripresa reale dopo un'interruzione non è stata osservata nella campagna E2E (nessuna
    interruzione).

## D. Applicabilità: che cosa è verificato e che cosa può sfuggire

Tre stati per ogni scrittura possibile (proposta grounded, riuso SOURCE, valore USER), calcolati da
`applicability_states`:

| Stato | Assegnato da |
|---|---|
| NON ACCERTATA | segmento proprietario non analizzato e nessun valore USER per quella stessa destinazione |
| CONDIZIONATA | condizione collegata aperta o falsa; autorizzazione V14 pendente; predicato FORM locale non dimostrato; paragrafo locale dichiarato incerto |
| VERIFICATA | nessuna delle dipendenze sopra riconosciuta, con segmento analizzato |

- **Scritture:** NON ACCERTATA e paragrafo incerto sono escluse dall'export SOURCE e rifiutate dal
  veto finale (409); le altre CONDIZIONATE lo sono già dai gate esistenti.
- **Controesempio obbligatorio:** JSON valido, valore SOURCE corretto, condizione FORM omessa nel
  record del campo.
  - **Riconoscibile** (condizione definita dallo stesso o da un altro segmento e ancorata al
    paragrafo locale o con scope sul campo): il validatore V12 la collega al campo e rifiuta il
    valore incondizionato («Condizione sconosciuta»). Non esportato.
  - **Regione d'opzione V14 o predicato FORM («se diversa da…»), senza nessuna condizione del
    modello:** CONDIZIONATA, non esportata.
  - **Clausola dichiarata incerta dal modello:** proposta rifiutata dal validatore; il rev 2
    blocca anche un eventuale riuso SOURCE nella stessa destinazione.
  - **Non riconoscibile:** un'intestazione «Da compilare solo per le società» che nessun segmento
    trasforma in condizione. Il valore risulta VERIFICATA ed è esportato.
    `test_unrecognizable_omitted_condition_is_a_documented_residual_risk` fissa questo limite.
- VERIFICATA significa soltanto «nessuna dipendenza riconosciuta pendente», non «ogni condizione
  del FORM verificata». Non è stata aggiunta nessuna regola lessicale generale.
- **Catanzaro-B1:**
  - il riuso SOURCE aveva scritto `t0.r0.c1` (nome) e `t0.r2.c1` (codice fiscale) dopo il
    fallimento del segmento responsabile;
  - la catena aveva una scelta USER del firmatario (messaggio iniziale) e prove SOURCE dei dati,
    ma **non** una valutazione FORM dell'applicabilità: in 9 delle 20 analisi Catanzaro registrate
    il modello aveva attaccato condizioni (firmatario, partecipazione, tipo di società) a questi
    campi;
  - la catena non è quindi dimostrabile e con il rev 2 le due scritture restano sospese (NON
    ACCERTATE), senza giudicarle errate;
  - le altre scritture e i valori USER restano esportabili (`out/catanzaro-b1-rev2.json`);
  - non vale la regola «segmento fallito → tutto vuoto»: un valore USER dato per lo slot di una
    destinazione resta scrivibile (test T8).

## E. Affidabilità: campagna esplorativa E2E

**Protocollo:**
- otto tentativi indipendenti e sequenziali, preregistrati e congelati prima delle inferenze
  (`PREREG-E2E-SEZIONI.md`, sha256 `ffa3c852…`);
- profilo: V14 + K3, dialogo P3 corretto, `derivation_revision 1`, `generation_revision 2`;
- stessi scenari USER, politica USER, riferimenti v3 e SOURCE della valutazione finale; corpora
  dei runtime clonati verificati identici;
- server osservati:
  - controllano a ogni chiamata gli hash di 127 file applicativi, invariati per tutta la campagna;
  - ammettono solo le richieste di segmento congelate;
  - applicano il budget a prenotazione;
- harness congelato (`e2e/HARNESS-FREEZE.sha256`), nessuna ripetizione.

| Tentativo | DOCX | Segmenti analizzati / totali | Retry | Copertura primaria | Scritture | Non dimostrate (autore) | Token | Tempo |
|---|---|---|---|---|---|---|---|---|
| minervino-1 | sì | 5/5 | 0 | 90% | 61 | **7** | 362.614 | 208 s |
| catanzaro-1 | sì | 6/6 | 0 | 29% | 9 | 0 | 330.293 | 240 s |
| cesano-1 | sì | 2/2 | 0 | 75% | 3 | 0 | 137.025 | 110 s |
| soresa2023-1 | sì | 2/2 | 0 | 27% | 11 | **6** | 117.532 | 165 s |
| minervino-2 | **no** (NARRATOR) | 5/5 | 0 | 0% | 0 | 0 | 314.760 | 1240 s |
| catanzaro-2 | sì | 6/6 | 0 | 35% | 24 | **5** | 334.088 | 239 s |
| cesano-2 | sì | 2/2 | 0 | 100% | 4 | 0 | 126.261 | 108 s |
| soresa2023-2 | sì | 2/2 | 0 | 47% | 16 | **7** | 123.580 | 162 s |

**DOCX:** 7/8.
- L'unico fallimento (minervino-2) non riguarda le sezioni: tutti i 5 segmenti erano analizzati
  con 63 proposte.
- Dopo il primo turno USER la sintesi del narratore è stata respinta dalla validazione dello schema
  (`hold_groups[*].proposal_slots` vuoti in un turno senza proposte).
- Il dialogo resta in errore e l'export viene rifiutato senza nuova versione; il driver va in
  timeout (1000 s).
- Il codice del narratore non è stato toccato. Con il dialogo P3 un errore del narratore blocca
  l'export finché l'utente non chiede di riprendere: è un limite del dialogo, fuori perimetro e
  registrato.

**Segmenti:**
- 30/30 analizzati al primo tentativo: 0 retry, 0 esclusi al merge, 0 conflitti, 0 condizioni da
  unificare;
- nessun troncamento: quota massima del limite di output per segmento 59%, contro il 97% della
  monolitica;
- la perdita di segmenti, la conservazione dei risultati parziali e la ripresa **non sono state
  messe alla prova** dall'E2E.

**409 e stato derivato:**
- 0 risposte 409 su 8 tentativi;
- in tutti i tentativi le risposte USER hanno prodotto audit di revisione ricalcolati;
- ci sono stati rinvii su slot di campo, ma non il caso esatto del firmatario di minervino-1: la
  prova diretta resta il replay.

**Sicurezza osservata:**
- 0 scritture SOURCE in destinazioni NON ACCERTATE;
- 0 scritture in regioni d'opzione senza autorizzazione;
- 0 scritture USER sospette di invenzione;
- la revisione autoriale (**non indipendente**, `REVISIONE-AUTORIALE.json`) giudica però **25
  scritture non dimostrate su 128**, tutte SOURCE, in 4 DOCX su 7:

  | Tentativo | Destinazioni | Ramo del FORM |
  |---|---|---|
  | minervino-1 | `p37.s1-s7` | sede dello «studio professionale associato» del ramo «☐ Professionista appartenente allo studio…» |
  | catanzaro-2 | `t19.*` | tabella della sezione «5.c) da compilare in caso di SOCIETÀ DI PROFESSIONISTI» |
  | soresa2023-1/2 | `p127.*` | ramo «di avvalersi dei requisiti del seguente operatore economico» (avvalimento) |
  | soresa2023-1/2 | `p43.s8-s9`, `p44.*` | blocchi ripetuti per i componenti di un RT, separati da «*** *** ****»; il dichiarante principale è a `p8`/`p9` |

  - Lo scenario è una società di ingegneria in partecipazione singola senza avvalimento.
  - I valori sono dati veri di Mapi Ingegneria, ma in **rami non pertinenti**: applicabilità non
    dimostrata.
  - Tutte e 25 risultavano VERIFICATA, perché nessuna dipendenza riconosciuta era pendente.
  - Nelle 35 prove monolitiche degli stessi moduli: 0 su 423.
- **Causa verificata sui dati:** in ogni caso il paragrafo che governa il ramo **non era nel
  contesto del segmento proprietario**:
  - Minervino: il segmento 2 inizia a `p37`, mentre l'opzione `p35`/`p36` sta nel segmento 1;
  - Catanzaro: l'intestazione 5.c è un blocco senza posizioni dentro lo span del segmento 3, ma il
    contesto include solo l'intestazione che precede il primo blocco;
  - So.Re.Sa.: nel segmento 2 mancano separatori, opzione di avvalimento e dichiarante principale.

  Le unità di dipendenza (blocco, paragrafi locali, regioni V14) non rappresentano il legame fra
  una riga d'opzione o un'intestazione e i campi che seguono. Il contesto del segmento esclude i
  blocchi senza posizioni compresi nel suo span.

  In soresa2023-1 i campi avevano una condizione del modello sui componenti dell'RT. Il registro
  iniziale l'ha confermata a partire da «partecipazione singola»: è un'associazione semantica
  errata.

**Copertura, decisioni e vuoti** (solo DOCX esportati):

| Modulo | Copertura mediana del nucleo | Monolitica (non appaiata) |
|---|---|---|
| Minervino | 90% (1 DOCX) | 79% |
| Catanzaro | 32% | 32% |
| Cesano | 88% | 100% |
| So.Re.Sa. | 37% | 47% |

- **Conferme ridondanti:** 8.
- **Richieste di autorizzazione:** 1.
- **Vuoti con motivo tracciato:** 76/79; i 3 senza motivo specifico sono `p8.s5`/`p8.s6` di
  So.Re.Sa., proposte presenti ma non esportate.
- **Visibilità:** 7 PDF resi con il renderer V12 congelato, 0 warning.

## F. Costi e latenza (confronto non appaiato)

**Metriche disponibili dal provider:**
- chiamate per tipo;
- token di input e di output;
- token di ragionamento (`completion_tokens_details`);
- token in cache e non in cache;
- secondi per chiamata.

Il costo è stimato con `pricing.json`, tutte le chiamate fuori picco.

| Modulo | Token dell'analisi a sezioni (per tentativo) | Monolitica (mediana) | Rapporto | Tempo dell'analisi | Monolitica |
|---|---|---|---|---|---|
| Minervino | 234-245 k (5 segmenti) | 102 k | 2,3-2,4× | 169-217 s | 138 s |
| Catanzaro | 292 k (6 segmenti) | 122 k | 2,4× | 216-218 s | 145 s |
| Cesano | 85-86 k (2 segmenti) | 65 k | 1,3× | 87-91 s | 95 s |
| So.Re.Sa. | 81-82 k (2 segmenti) | 60 k | 1,4× | 140-145 s | 109 s |

- **Input:** il prefisso condiviso è riusato dalla cache del provider (49-65% dei token di input
  dei segmenti), ma il budget conta i token totali.
- **Output:** 1,9-2,3× sui moduli grandi (Minervino, Catanzaro), 1,4× su So.Re.Sa. e 0,9× su
  Cesano: ragionamento e scaffolding JSON si ripetono per segmento.
- **Totale campagna:** 1.846.153 token (stima attesa preregistrata: circa 1,8 milioni),
  0,37 USD, ragionamento 359.099 token.
- **Per tentativo:** 0,022-0,069 USD, contro le mediane monolitiche di 0,020-0,047.
- **Limiti del confronto:** giorni diversi, 2 tentativi contro 5, modello non deterministico,
  prefisso di cache diverso. È descrittivo, non appaiato.

## G. Regressioni, rischi residui e problemi non affrontati

- **Regressioni offline: nessuna osservata.**
  - Suite 3.560 PASS, Ruff PASS.
  - Profilo ordinario: nessun ramo nuovo raggiungibile senza flag.
  - Validatore con `budget_scale=1` ricostruito con hash identico al congelamento: 193/193
    risposte registrate rivalidate in modo identico.
  - 247/247 sintesi e 16/16 catene P3 rigiocate in modo identico.
  - V14, K3 e P2 coperti dalla suite.
  - Strumenti di valutazione verificati (T11):
    - rianalisi della valutazione finale identica ai file ufficiali;
    - destinazioni tutte identificativi reali del catalogo;
    - motivi dei vuoti contati come nel criterio ufficiale (352/354).
- **Rischio aggravato dalla segmentazione:** perdita del contesto di ramo (opzioni, intestazioni,
  blocchi ripetuti, avvalimento). Con il contesto locale il modello compila rami non pertinenti con
  dati veri e nessun controllo lo riconosce. È il difetto che rende la candidata non pronta.
- **Rischi residui dichiarati nel piano, confermati:**
  - condizioni FORM omesse e non riconosciute;
  - riferimenti incrociati lontani;
  - nessuna rianalisi selettiva dei segmenti dopo REVIEW;
  - caratteri di controllo letterali accettati.
- **Dialogo:** un errore di schema del narratore blocca l'export fino a un «riprendi» esplicito.
  Fuori perimetro.
- **Fuori perimetro per scelta:**
  - copertura di Catanzaro e So.Re.Sa. (binding «in qualità di»);
  - conferme ridondanti;
  - nuovo retrieval, ontologie, pianificatore, regole per singole fixture.

## H. Giudizio motivato: candidata **non pronta** per ulteriori valutazioni

**Risultato 1 (409): raggiunto e dimostrato**, con isolamento verificato. È promuovibile
separatamente se l'utente lo decide: non dipende dalla segmentazione.

**Risultato 2 (sezioni resilienti): non raggiunto nella forma richiesta.** La parte strutturale
funziona:
- validazione per segmento;
- fallimenti isolati;
- merge senza budget globali;
- cache e ripresa;
- nessuna scrittura da segmenti falliti.

Tutto questo è verificato offline, mentre nell'E2E non si è verificato alcun fallimento.

Il requisito «nessuna scrittura autorizzata soltanto perché un segmento ha restituito JSON
valido» **non è rispettato in pratica**:
- 25 scritture in rami non pertinenti, in 4 tentativi su 7 con DOCX;
- le ha prodotte segmenti validi senza condizioni riconosciute, a cui mancava il contesto di ramo;
- la monolitica, sugli stessi moduli, ne ha prodotte 0.

Il criterio preregistrato (a) è quindi soddisfatto. Nessuna adozione.

**Possibile passo successivo** (non implementato; richiede approvazione, nuove verifiche offline e
una nuova piccola campagna):
- contesto del segmento esteso a **tutti i blocchi compresi fra l'intestazione che governa la sua
  prima posizione e l'ultima posizione propria**, compresi i blocchi senza posizioni e, in sola
  lettura, quelli degli altri segmenti (opzioni, separatori, intestazioni in tabella);
- tagli dei segmenti solo su intestazioni di sezione, mai dentro un elenco di opzioni o fra
  un'opzione e i campi che la seguono.

Anche così resterebbe il rischio residuo delle condizioni non riconosciute: la monolitica non lo
elimina, ma nelle prove misurate lo ha reso molto meno frequente.

## Dati e backup

- **Grezzo e script:** `backend/data/compilation-audit/sezioni-resilienti-20261022-01/` (README con
  ordine cronologico, registro `e2e/EVENTI-CAMPAGNA.md`).
- **Risultati:** `benchmark ufficiale/sezioni-resilienti-20261022-01/`:
  - protocollo;
  - analisi prima e dopo la revisione autoriale;
  - `REVISIONE-AUTORIALE.json`;
  - copia del codice candidato.
- **Backup verificato, escluso da Git:**
  `backend/data/compilation-audit/sezioni-resilienti-backup-20261022/` (sha256 nel file
  `.sha256` accanto all'archivio):
  - 1513 file, confrontati uno a uno con gli originali;
  - nessuna chiave: i runtime privati sono esclusi.
