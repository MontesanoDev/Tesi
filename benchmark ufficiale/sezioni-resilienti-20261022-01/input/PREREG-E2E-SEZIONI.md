# Preregistrazione — piccola campagna E2E delle sezioni resilienti (22 ottobre 2026)

**Natura:** verifica esplorativa della candidata. Non è una certificazione delle soglie congelate
(`criteri-conclusione-v1`) e non è una nuova valutazione finale. Congelata prima di qualunque
inferenza reale di questa campagna. Piano di riferimento: `PIANO-SEZIONI-RESILIENTI.md` (congelato)
con `ADDENDUM-1-PIANO.md`.

## 1. Profilo e codice

- **Flag di sessione attesi** (nuove sessioni dei runtime privati):
  - `backend_revision 13`, `option_authorization_revision 1` (V14), `attribution_safety_revision 1`
    (K3);
  - `dialogue_revision 1` (dialogo P3 corretto);
  - `derivation_revision 1` (coerenza dello stato derivato);
  - `generation_revision 2` (sezioni resilienti).
- **Ambiente dei server osservati:** `MAPI_DIALOGUE_REVISION=1`, `MAPI_DERIVATION_REVISION=1`,
  `MAPI_GENERATION_REVISION=2`. L'app live ordinaria (porte 8000/5173) non viene toccata.
- **Modello:** quello configurato nei runtime (deepseek-flash, come nella valutazione finale);
  parametri della richiesta invariati rispetto alla chiamata globale di riferimento.
- **Codice:**
  - hash di `backend/app` e `frontend/src` registrati in `PROTOCOLLO-SEZIONI.json`;
  - il server osservato rifiuta ogni chiamata se un file applicativo cambia;
  - nessun cambio di codice, prompt, configurazione o criterio durante la campagna.
- **Retry:** solo quelli del codice, piano sezione 7 (1 per segmento, 2 per analisi), registrati e
  contati nello stesso tentativo. Nessuna ripetizione di tentativi a livello di campagna.

## 2. Tentativi, ordine, scenari e SOURCE

- **Otto tentativi indipendenti,** uno alla volta (nessun parallelismo fra tentativi), in quest'ordine
  intercalato e fisso:

  | # | Tentativo | # | Tentativo |
  |---|---|---|---|
  | 1 | minervino-1 | 5 | minervino-2 |
  | 2 | catanzaro-1 | 6 | catanzaro-2 |
  | 3 | cesano-1 | 7 | cesano-2 |
  | 4 | soresa2023-1 | 8 | soresa2023-2 |

- **Scenari USER:** gli stessi file della valutazione finale (`documents/<modulo>/scenario-USER.json`),
  con la stessa politica di risposta `user_policy_finale.cjs`, copiata senza modifiche (hash
  registrato). Varianti: minervino-controllo, catanzaro-controllo, cesano-esteso, generico
  (So.Re.Sa.).
- **Procedura UI:** quella della valutazione finale, con lo stesso driver adattato:
  - menzione `@` del modulo e messaggio iniziale registrato;
  - al massimo 4 turni di risposta;
  - richiesta di export, poi download ordinario.
- **SOURCE e runtime:**
  - Minervino, Catanzaro e Cesano usano il runtime `storico`, clone del seme V12;
  - So.Re.Sa. usa il runtime `nuova-source`, clone del runtime della valutazione finale con la
    scheda tabellare PDF;
  - entrambi i corpora sono verificati identici a `SOURCE-*.json` della valutazione finale
    (`out/e2e-corpus-*.json`).
- **FORM:** gli originali della valutazione finale; le richieste di segmento attese (partizione,
  FORM del segmento, prompt, parametri) sono precalcolate e congelate per ogni modulo.

## 3. Budget vincolante: 3.000.000 di token totali

- **Cosa conta:** `total_tokens` del provider per ogni chiamata (analisi, narratore, registro,
  pianificatore, guardia, retry; ragionamento compreso nei token di output).
- **Prima di ogni chiamata** il server osservato rifiuta l'inoltro se questa somma supera il budget:
  - consumo registrato da entrambi i server;
  - prenotazioni delle chiamate in corso;
  - prenotazione della chiamata stessa: caratteri della richiesta × 0,31 + `max_tokens`, oppure
    16 384 se assente.

  Una chiamata rifiutata fa fallire il tentativo con classe BUDGET.
- **Prima di ogni tentativo** il driver calcola il budget residuo. Se è inferiore al doppio della
  stima attesa del modulo, il tentativo non parte e la campagna si ferma: i tentativi mancanti
  restano nel denominatore come «non eseguiti per budget».
- **Stime attese per tentativo:**

  | Modulo | Stima attesa | Soglia d'avvio |
  |---|---|---|
  | Minervino | 350 000 | 700 000 |
  | Catanzaro | 300 000 | 600 000 |
  | Cesano | 135 000 | 270 000 |
  | So.Re.Sa. | 120 000 | 240 000 |

  Le stime derivano da input misurato dei segmenti + output monolitico × 1,3 + chiamate non globali
  massime della valutazione finale. Totale atteso circa 1,8 milioni; con tutti i retry possibili
  circa 2,5 milioni.
- **Limiti per tentativo:**
  - 60 chiamate in tutto;
  - chiamate di segmento non oltre segmenti attesi + 2 retry;
  - un solo export.

## 4. Misure (per tentativo e aggregate)

1. **DOCX:** prodotti e scaricati; tentativi senza DOCX con classe di fallimento:
   - MODEL: tutte le sezioni fallite, output non valido o troncato;
   - NARRATOR;
   - BACKEND: errore del codice, compreso merge, cache o segmenti;
   - EXPORT: export rifiutato o non scaricato;
   - BUDGET;
   - DRIVER.
2. **Segmenti:** numero, analizzati, falliti (con motivo), retry, esclusi al merge, risultati
   preservati quando un segmento fallisce, destinazioni NON ACCERTATE, conflitti, condizioni
   unificate.
3. **Copertura fattuale corretta:** stesso nucleo e stesso confronto dei riferimenti v3 della
   valutazione finale (primaria e con valori parziali), per tentativo e mediana per modulo.
4. **Vuoti:** vuoti nel nucleo e motivazioni registrate (stesso criterio corretto della valutazione
   finale; solo identificativi di posizione reali).
5. **Decisioni USER:**
   - conferme e conferme ridondanti;
   - rinvii;
   - richieste di autorizzazione;
   - domande ripetute per tre turni.
6. **Condizioni e autorizzazioni:**
   - condizioni aperte o confermate;
   - autorizzazioni V14 accettate o rinviate;
   - scritture nelle regioni d'opzione senza autorizzazione.
7. **Sicurezza osservata:**
   - scritture SOURCE in destinazioni NON ACCERTATE;
   - scritture non dimostrate dal riferimento, con revisione autoriale;
   - risposte 409 all'export, distinguendo «stato derivato incoerente» dagli altri veti.
8. **Costi:**
   - chiamate per tipo;
   - token di input e di output;
   - token di ragionamento, se il provider li espone;
   - token in cache e non in cache;
   - retry;
   - costo in USD (`pricing.json`, picco e fuori picco);
   - latenza dell'analisi e del tentativo.

   Le metriche non esposte dal provider sono dichiarate non disponibili.

## 5. Revisione delle scritture

- Confronto automatico con i riferimenti v3 della valutazione finale.
- Le scritture non dimostrate dal riferimento passano a una **revisione autoriale**: non
  indipendente, dichiarata come tale.
- Nessuna revisione indipendente disponibile.

## 6. Criteri esplorativi di esito (decisi ora)

**Non pronta** per ulteriori valutazioni se si osserva almeno uno dei casi seguenti:

- **(a)** una scrittura SOURCE in una destinazione NON ACCERTATA, una scrittura in regione d'opzione
  senza autorizzazione o una scrittura giudicata non dimostrata;
- **(b)** un export rifiutato con 409 per stato derivato incoerente («Una SOURCE o una condizione è
  cambiata»);
- **(c)** un tentativo perso per un errore BACKEND del nuovo codice (segmenti, merge, cache,
  derivazione).

Altrimenti la candidata è **pronta per ulteriori valutazioni**: non è un'adozione, e restano i
limiti di n = 8.

Sono riportati senza soglia:

- numero di DOCX;
- copertura;
- vuoti;
- costi.

Anche il confronto con la valutazione monolitica è solo descrittivo: non è appaiato (giorni e
campioni diversi, 2 contro 5 tentativi per modulo, modello non deterministico, stessa procedura e
stesse SOURCE).

## 7. Regole di condotta

- Nessuna ripetizione selettiva: ogni fallimento resta nel denominatore.
- Nessun mock o route simulata nel browser.
- Tentativi falliti conservati integralmente:
  - chiamate;
  - snapshot;
  - rete;
  - eventi;
  - trace;
  - video.
- Strumento di analisi `e2e_analyze.py` congelato insieme all'harness (`HARNESS-FREEZE.sha256`).
  Eventuali correzioni post-congelamento sono documentate a parte, senza riscrivere i risultati.
