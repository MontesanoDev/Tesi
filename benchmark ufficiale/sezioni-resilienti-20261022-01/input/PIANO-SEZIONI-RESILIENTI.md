# Piano minimo — coerenza dello stato derivato e sezioni resilienti (22 ottobre 2026)

Congelato prima di modificare il codice e prima di qualunque test di valutazione. Due soli risultati:
1. coerenza dello stato derivato dopo le risposte USER (HTTP 409 di minervino-1);
2. generazione per sezioni resiliente, verificabile, riprendibile e sicura.

Fuori perimetro:
- nuovo retrieval, ontologie di persone, imprese e ruoli, pianificatore autonomo;
- riscrittura RAG, parser DOCX o writer;
- regole per singole fixture, filoni P1/P2;
- recupero creativo di JSON;
- obiettivi di copertura per Catanzaro o So.Re.Sa.

Ogni ampliamento significativo sarà documentato e fermato prima dell'implementazione.

## 0. Diagnosi di partenza (dimostrata sui dati registrati)

- **409 (minervino-1):**
  1. l'audit salvato conteneva il riuso del firmatario, ricavato dalla selezione esplicita nel
     primo messaggio;
  2. una risposta allo slot `field:p12.s0` è stata registrata come SKIP;
  3. `_selection` restituisce nulla con una ricevuta SKIP, quindi `source_reuse_requested` diventa
     falso;
  4. `apply_replies` ricalcola l'audit solo se il riuso è richiesto *dopo* la risposta, oppure dopo
     CONDITION_TRUE/FALSE: l'audit resta quello vecchio;
  5. l'export seleziona dall'audit vecchio, `refreshed_audit` lo ricalcola senza riuso e il veto
     finale risponde 409.
- **Sezioni P3 (`generation_revision 1`):**
  - partizione per contiguità e numero di posizioni;
  - nessuna validazione strutturale per segmento prima del merge;
  - budget del validatore V12 globali (400 campi, 128 fatti/condizioni/binding, 64 gruppi,
    16 chiarimenti), che possono far fallire l'unione di segmenti validi;
  - FORM e SOURCE completi ripetuti in ogni chiamata (2,5-5× token);
  - riuso SOURCE nelle destinazioni di un segmento fallito (Catanzaro-B1: nome e CF del firmatario,
    `t0.r0.c1` e `t0.r2.c1`);
  - nessuna ripresa: un'interruzione rifà tutta l'analisi.

## 1. Funzioni da modificare (elenco chiuso)

| File | Funzione | Modifica |
|---|---|---|
| `compilation_global_sessions.py` | `initial_state` | flag opt-in separati: `derivation_revision 1` (`MAPI_DERIVATION_REVISION=1`), `generation_revision 2` (`MAPI_GENERATION_REVISION=2`) |
| `compilation_global_sessions.py` | `_prepare` | lease proporzionale al numero di ondate del rev 2 |
| `compilation_global_sessions.py` | `resolve_global` | ramo `generation_revision 2`; copia del flag `derivation_revision` dalla sessione |
| `compilation_global_sessions.py` | `validated_audit` | per il rev 2: scala dei budget = segmenti uniti; stati di applicabilità |
| `compilation_global_sessions.py` | `_selected` | veto finale anche sulle destinazioni NON ACCERTATE (solo rev 2) |
| `compilation_global_sessions.py` | nuova `_resilient_proposal` | segmenti rev 2: cache, retry, validazione, merge |
| `compilation_global_dialogue.py` | `apply_replies` | con `derivation_revision 1`: ricalcolo dell'audit derivato dopo ogni mutazione accettata |
| `compilation_global_dialogue.py` | `export_selection` | esclusione delle destinazioni NON ACCERTATE (solo rev 2) |
| `compilation_global.py` | `validate_global_proposal`, `_validate_sparse_proposal` | parametro `budget_scale=1`, che scala budget dei dizionari e lunghezza massima; predefinito invariato |
| `compilation_segments.py` | nuove funzioni rev 2 | partizione per dipendenze, input del segmento, validazione per segmento, unificazione delle condizioni condivise, stati di applicabilità, cache |

Nessuna modifica a parser DOCX, writer, retrieval, narratore, registro iniziale, moduli V14
(`compilation_option_regions`, `compilation_procedural_consent`) e K3
(`compilation_attribution_safety`).

## 2. Invarianti da preservare

- **I1.** Profilo ordinario e sessioni esistenti con comportamento identico: senza i nuovi flag nessun
  ramo nuovo è raggiungibile; `budget_scale=1` lascia identico il validatore.
- **I2.** Grounding SOURCE, binding di ruolo, regole FORM/SOURCE/USER, V14, K3, completezza dei
  valori e applicabilità FORM: invariati e applicati all'unione come oggi.
- **I3.** Veto finale dell'export (`_selected`: rivalidazione e uguaglianza dei campi selezionati)
  mantenuto.
- **I4.** Un rinvio, un UNKNOWN o un REFUSE non autorizzano mai nulla; una ricevuta USER non diventa
  SOURCE.
- **I5.** Nessuna riparazione di JSON. Si accettano soltanto caratteri di controllo letterali dentro
  le stringhe (come P3); un JSON incompleto o malformato fa fallire il segmento.
- **I6.** Ogni destinazione DOCX ha esattamente un segmento proprietario; i record fuori proprietà
  vengono scartati e registrati.
- **I7.** Un segmento fallito non annulla i segmenti validati indipendenti; le sue destinazioni
  restano «non analizzate» con motivo BACKEND.
- **I8.** Un JSON valido non rende una destinazione applicabile: si scrive solo una destinazione
  VERIFICATA (sezione 4) che superi tutti i gate esistenti.
- **I9.** Ripresa: si riusano soltanto risultati di segmento la cui richiesta (prompt, parametri,
  FORM del segmento, SOURCE, contesto USER iniziale, data di riferimento) è identica byte per byte;
  risultati di richieste diverse non vengono mai uniti.

## 3. Disegno minimo dei segmenti (rev 2)

- **Unità indivisibili** (union-find su strutture esistenti):
  - posizioni nello stesso blocco FORM (paragrafo o tabella);
  - posizioni che condividono un paragrafo locale (`anchor_paragraph_ids`, dalla mappa
    `_form_bindings` usata dal validatore per le condizioni);
  - regioni d'opzione V14.

  Misurato sui moduli reali: unità massima di 51 posizioni (Minervino), tipicamente sotto 20.
- **Proprietà:** ogni unità appartiene a un solo segmento.
- **Impacchettamento:** in ordine di documento. Criterio secondario: obiettivo di 60 posizioni per
  segmento, con taglio preferito prima di un paragrafo in grassetto senza posizioni (intestazione)
  quando il segmento è almeno a metà. Massimo 8 segmenti; oltre, l'obiettivo cresce. Un modulo da
  60 posizioni o meno resta un segmento naturale, ma con il prompt e le regole rev 2.
- **Contesto del segmento:**
  - blocchi propri, blocchi che contengono i paragrafi locali delle posizioni proprie e
    l'intestazione in grassetto più vicina che precede il primo blocco;
  - candidate solo proprie; piano di lettura filtrato alle posizioni proprie;
  - SOURCE completa, schema, contesto USER e data invariati.

  Le parti costanti precedono il FORM nel messaggio, per sfruttare la cache del prompt.
- **Istruzione:** il FORM ricevuto è parziale; si propongono solo le posizioni del segmento; le
  condizioni vanno ancorate ai paragrafi ricevuti.

## 4. Applicabilità: tre stati per destinazione (rev 2)

| Stato | Quando | Controlli che lo assegnano |
|---|---|---|
| NON ACCERTATA | Il segmento proprietario non è analizzato (fallito o non eseguito) e la scrittura non ha una catena indipendente completa | Stato del segmento. Unica catena indipendente ammessa: valore USER accettato per lo slot di quella stessa destinazione, senza gate V14 o predicato FORM pendenti. Il riuso SOURCE del firmatario non basta: la sua applicabilità dipendeva dall'analisi del segmento. |
| CONDIZIONATA | Esiste una condizione riconosciuta non risolta | Condizioni del modello sulla posizione, comprese quelle ancorate ai paragrafi locali e attaccate dal validatore anche se il campo le omette (anche se definite da un altro segmento); autorizzazione V14 non accettata; predicato FORM locale non dimostrato (`compilation_form_applicability`); paragrafi locali marcati incerti. |
| VERIFICATA | Segmento analizzato e nessuna dipendenza di applicabilità riconosciuta pendente | Assenza di tutte le condizioni sopra. **Non** significa che ogni condizione possibile del FORM sia stata verificata: una clausola fuori dai paragrafi locali, omessa dal modello e non riconosciuta da V14 o dal predicato FORM, sfugge (rischio residuo dichiarato, coperto da un test che lo documenta). |

- Una lista vuota di `conditions` non basta: serve il segmento analizzato e nessun riconoscitore
  pendente.
- Le destinazioni NON ACCERTATE sono escluse dalla selezione di export e rifiutate dal veto finale.
  Le CONDIZIONATE lo sono già dai gate esistenti.

## 5. Validazione e merge (rev 2)

1. **Parsing** senza riparazione (I5).
2. **Validazione strutturale per segmento:** `validate_global_proposal` sul solo segmento, con i
   budget normali. Un errore di envelope, budget o chiave duplicata fa fallire **solo** quel segmento.
3. **Proprietà:** campi, chiarimenti e copertura fuori dal segmento vengono scartati e contati.
4. **Merge P3** (rinomina, deduplica esatta, conflitti di valore → revisione «conflicting»). In più:
   condizioni di segmenti diversi con stesso paragrafo, stessa citazione normalizzata, stesso aspetto
   e operatore e fatti di valore identico vengono **unificate**, con unione degli scope. Le altre
   condizioni sullo stesso paragrafo restano distinte e sono registrate come «condivise non
   unificate».
5. **Validazione dell'unione** con `budget_scale` = numero di segmenti uniti, che mantiene i budget
   per chiamata. Se l'unione fallisce comunque, ricerca deterministica: si aggiungono i segmenti in
   ordine e si esclude il primo che provoca l'errore, registrandolo. Nessuna modifica ai dati.
6. **Stati di applicabilità** e copertura UNASSESSED con motivo BACKEND per le posizioni non
   analizzate.

## 6. Ripresa e cache

- Ogni segmento validato strutturalmente viene salvato subito in
  `_global_compilations/<sessione>/segment-cache/<sha256 della richiesta>.json`: risposta grezza,
  esito, usage, tentativi.
- Una nuova analisi della stessa sessione, dopo FAILED o un'interruzione con ripresa esplicita,
  ricostruisce le richieste. Riusa le voci con lo stesso sha256 e chiama soltanto i segmenti
  mancanti o falliti.
- Il report registra per ogni segmento: «riusato» o «chiamato», sha, tentativi.
- Le decisioni USER successive non entrano nella richiesta del modello. Non invalidano quindi i
  segmenti, ma lo stato derivato (riuso, rami, sospensioni, fingerprint delle revisioni), che con
  `derivation_revision 1` viene ricalcolato.
- Nessun nuovo sistema di job: si usano le transizioni di sessione esistenti (lease, `mark_failed`,
  controllo «riprendi»). Non viene aggiunto un percorso per rianalizzare i segmenti falliti di
  un'analisi già conclusa in REVIEW (limite dichiarato).

## 7. Politica di retry (rev 2)

- **Massimo:** 1 retry automatico per segmento e 2 per analisi, nella stessa analisi.
- **Attivazione:** errore di trasporto o del provider (HTTP o timeout), troncamento
  (`finish_reason = length`), JSON non analizzabile o envelope non V12, errore strutturale della
  validazione per segmento.
- **Nessun retry per:** budget di sessione o di campagna esaurito, errori di proprietà o semantici
  dei record (restano quarantena locale).
- Ogni retry è registrato (motivo, usage) e contato nello stesso tentativo sperimentale. Non
  sostituisce mai un tentativo.

## 8. Correzione 409 (`derivation_revision 1`), isolata

- Dopo ogni mutazione accettata in `apply_replies` (VALUE, CONDITION_TRUE/FALSE, SKIP, UNKNOWN,
  REFUSE, interventi della guardia sui cicli, scelte) si ricalcola `refreshed_audit`. Se differisce,
  si salva come nuovo audit di revisione; i fingerprint invalidano le sole revisioni coinvolte.
- Il flag è indipendente dalla segmentazione e attivo solo nelle nuove sessioni candidate. Il veto
  finale resta invariato.
- **Verifiche:**
  - riproduzione deterministica di minervino-1 con le risposte registrate: 409 senza flag, export
    coerente con il flag;
  - conferma, rinvio, revoca, cambio di risposta, risposta a uno slot differente.

## 9. Test deterministici e criteri di accettazione (Fase 4, zero LLM)

| # | Verifica | Accettazione |
|---|---|---|
| T1 | Riproduzione 409 minervino-1 (replay delle risposte registrate) | senza flag: 409 riprodotto; con flag: nessun 409, i campi del riuso non sono selezionati, export riuscito |
| T2 | Conferma, rinvio, revoca, cambio, slot differente | audit salvato sempre uguale a `refreshed_audit`; mai riuso dopo un rinvio; export senza 409 |
| T3 | Fallimento isolato di ciascun segmento | gli altri segmenti sono uniti; destinazioni del fallito UNASSESSED e NON ACCERTATE |
| T4 | JSON incompleto, caratteri di controllo, struttura errata, budget del segmento | incompleto e struttura errata: segmento fallito senza riparazione; controllo letterale nelle stringhe accettato; nessun effetto sugli altri segmenti |
| T5 | Condizione FORM omessa in JSON valido con valore SOURCE corretto | casi riconoscibili (condizione ancorata nei paragrafi locali, definita dallo stesso o da un altro segmento; regione V14; predicato FORM) → CONDIZIONATA, non esportata; caso non riconoscibile documentato come rischio residuo |
| T6 | Condizioni e soggetti condivisi | condizioni equivalenti unificate (una risposta vale per tutti gli scope); non equivalenti registrate; fatti dello stesso soggetto con valori diversi → conflitto in revisione |
| T7 | Conflitti fra proposte | nessuna scelta nascosta |
| T8 | Riuso SOURCE dopo segmento fallito (sintetico + Catanzaro-B1 registrato) | riuso NON ACCERTATO, non esportato; valore USER per lo slot proprio resta scrivibile |
| T9 | Interruzione, ripresa, retry, invalidazione | segmenti validati riusati senza nuove chiamate; retry entro i limiti; richieste diverse mai unite; ripresa soggetta agli stessi gate |
| T10 | Regressioni | negativi P2/K3, consenso V14, sessioni precedenti (replay delle 247 sintesi), audit identici per le 158 risposte globali registrate con `budget_scale=1` |
| T11 | Strumenti di valutazione | solo identificativi di posizione reali come destinazioni; motivi effettivi; rianalisi della valutazione finale invariata dopo la correzione 1 |

Suite backend completa e Ruff verdi prima dell'E2E.

## 10. Rischi non risolvibili senza ampliare il perimetro

- Condizioni FORM fuori dai paragrafi locali, omesse dal modello e non riconosciute da V14 o dal
  predicato FORM.
- Riferimenti incrociati fra sezioni lontane («come indicato al punto 3»).
- Copertura di Catanzaro e So.Re.Sa. (il binding «in qualità di» resta com'è).
- Qualità di un modello che vede soltanto il contesto locale.
- Nessuna rianalisi selettiva dopo REVIEW.
- Caratteri di controllo letterali accettati.

## 11. Budget di verifica

- **Offline:** zero chiamate LLM.
- **E2E:** 8 tentativi indipendenti (Minervino, Catanzaro, Cesano, So.Re.Sa., 2 ciascuno), con
  ordine intercalato e un tentativo alla volta. **Massimo vincolante 3.000.000 token totali**
  (`total_tokens` del provider: analisi, narratore, altre chiamate, ragionamento, retry).
- **Controlli prima di ogni chiamata:** consumo registrato + riserva della chiamata (stima del prompt
  + `max_tokens`) ≤ budget, altrimenti la chiamata viene rifiutata.
- **Controllo prima di ogni tentativo:** budget residuo ≥ stima prudente del modulo (2× la stima
  attesa). Altrimenti il tentativo non parte e resta nel denominatore come mancante.
- **Stima attesa:** circa 1,9 milioni di token.
- Il protocollo E2E con scenari, SOURCE, hash, revisione e criteri sarà congelato separatamente
  prima delle inferenze.
