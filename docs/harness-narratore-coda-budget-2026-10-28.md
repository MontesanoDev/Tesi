# Harness narratore: coda del budget, attesa e errore controllato (28 ottobre 2026)

**Solo offline.** Nessuna chiamata DeepSeek, nessuna ripresa, nessun push o merge.
- **Modifiche:** solo `audit_tools/narrator_harness/` e `audit_tools/tests/`.
- **Compilatore:** `7b31d25` invariato; il diff `7b31d25..89d1e2e -- backend frontend` è vuoto.
- **Interventi:** correggono le tre cause del tentativo 02
  ([rapporto](narratore-minervino-audit-02-2026-10-28.md)).

## Commit, prove e rollback

| Fix | Commit | Nuovi test sul commit precedente | Dopo | Rollback (worktree dedicato) |
|---|---|---|---|---|
| 1. Budget e concorrenza | `bb602bb` | 6/6 falliti | 57/57 | revert `71daebd` = albero di `28f4ba8`, 51/51 |
| 2. Attesa | `c7e5fd7` | 8/8 falliti | 64/64 | revert `135d9e2` = albero di `bb602bb`, 57/57 |
| 3. Errore controllato | `89d1e2e` | 3/5 falliti | 69/69 | revert `d7440aa` = albero di `c7e5fd7`, 64/64 |

**Cosa falliva prima di ciascun fix:**
- **fix 1:** mancavano coda, riserva e contabilità separata;
- **fix 2:** 3 casi davano «Pending reservation unresolved», cioè il limite di 120 s; mancava la
  classificazione dei timeout; il budget impossibile veniva rifiutato come `busy` dopo l'attesa;
  mancava l'ammissione prima del timeout;
- **fix 3:** non c'era l'errore controllato; le due caratterizzazioni passavano già.

**Worktree di rollback:** `tesi-harness-rollback-{coda,attesa,errore}-20261028`, sui branch
`verifica-rollback/2026-10-28-harness-*`.

**Verifiche:**
- Ruff PASS;
- preflight browser offline (React, FastAPI, provider simulato, 5 casi):
  `backend/data/compilation-audit/harness-fix-20261028/preflight-{c7e5fd7,89d1e2e}`.

## Fix 1: budget e concorrenza

- **Coda FIFO nel ledger:** una richiesta che non entra attende in fila e nessuna la scavalca.
  Prima del fix ripeteva il tentativo e poteva essere sorpassata all'infinito.
- **Riserva per le fasi successive** (`reserve_tokens`, congelata nel config): le chiamate
  dell'analisi non la impegnano mai, mentre narratore, guardia ed export possono usarla.
  `verify()` ricontrolla ogni ammissione usando solo il ledger.
- **Grandezze separate:**
  - prenotato vivo;
  - consumo misurato;
  - addebito riportato (`carry`);
  - esito incerto, addebitato per intero.

  Le stime, come il costo, non entrano nel ledger.
- **`carry()`:** apre un nuovo ledger partendo dagli addebiti di uno precedente, mai dal suo
  credito.

## Fix 2: attesa senza limite arbitrario

- **Limite eliminato:** non c'è più il fallimento a 120 s.
- **Attesa legittima:** una richiesta attende solo finché esistono prenotazioni vive di questo
  processo che possono liberare spazio.
- **Budget impossibile:** se la richiesta non entrerebbe nemmeno con tutte quelle prenotazioni
  saldate a zero, viene rifiutata subito, prima dell'invio. Il rifiuto e lo STOP sono registrati.
- **Prenotazioni di un processo morto:** restano addebitate e non vengono mai attese; un waiter
  morto non blocca la fila.
- **Ticket prima del timeout del modello:** ogni segmento di un'analisi pianificata prende un
  ticket quando il compilatore apre il suo client HTTPX, cioè dopo il suo semaforo ma prima di
  `asyncio.wait_for` (300 s). In `post_chat` il ticket diventa la prenotazione esatta, mai più
  grande. Così l'attesa in coda non consuma il timeout del modello.
- **Classificazione nei record:**
  - `budget_wait`, con dove e quanti secondi;
  - `cancelled_while_queued`, a 0 token;
  - `provider_timeout`, cioè un timeout del trasporto dopo l'invio;
  - `cancelled_after_dispatch`, con usage ignoto e quindi STOP.
- **Operatore:** chiudendo il gate o creando `STOP.json` termina qualsiasi attesa.
- **Difetto latente di `bb602bb`, corretto qui:** la prenotazione degli hop di redirect non
  passava la riserva. Si manifestava solo con i redirect, che la campagna vieta.

## Fix 3: errore controllato, comportamento del compilatore

**Compilatore `7b31d25`, invariato e caratterizzato con il simulatore:**
- **Errori gestiti per segmento:** `GenerationError`, `ValueError`, `TimeoutError` e
  `httpx.HTTPError` danno un retry (1 per segmento, 2 per analisi). Poi il segmento è `failed`
  e gli altri vengono uniti: analisi parziale, HTTP 200.
- **Qualsiasi altra eccezione** interrompe l'analisi: sessione `FAILED` senza audit.
  - I segmenti già in volo **non sono annullati**: `asyncio.gather` non li cancella.
  - Completano, la loro risposta validata finisce in cache e l'usage viene contabilizzato.
  - La ripresa riusa la cache e chiama solo i segmenti mancanti.

**Scelta dell'harness:**
- **Rifiuto come HTTP 503:** ogni rifiuto prima dell'invio (budget, gate chiuso, STOP) arriva
  all'app come HTTP 503 (`HTTPException`), non più come `RuntimeError` e HTTP 500.
- **Perché non `GenerationError`:** il compilatore lo ritenterebbe e unirebbe un'analisi
  parziale, e il narratore lo assorbirebbe in una sintesi degradata.
- **Nessuna cancellazione aggiunta.**

**Interazione da conoscere:** sotto l'harness, un errore del provider senza usage (trasporto,
risposta senza corpo) ferma la campagna, per la regola preregistrata. Senza harness lo stesso
errore porterebbe a un retry e a un'analisi parziale. Sotto audit si ha quindi un arresto
controllato seguito da una ripresa.

## Test con provider simulato

Sono 69 test in `audit_tools/tests/`, di cui 18 nuovi.
- **Cosa gira davvero:** il candidato reale, cioè FastAPI, `/resolve`, `post_chat`, i client
  HTTPX, il semaforo, i retry, la cache e i timeout.
- **Cosa è simulato:**
  - il trasporto remoto;
  - 5 segmenti da 60 destinazioni, come Minervino;
  - `TIMEOUT_SECONDS` scalato da 300 a 1 s.
- **Rete:** le connessioni non loopback sono bloccate.

| Area | Esito |
|---|---|
| Parallelismo | Con budget sufficiente: 3 segmenti concorrenti, come senza harness |
| Budget | Con budget per un segmento: 5 in serie, FIFO, riserva rispettata; impossibile = STOP immediato senza annullare la chiamata in volo; prenotazioni orfane |
| Timeout | Con attesa dentro `post_chat` (harness 02) il segmento 4 supera il timeout scalato e la campagna si ferma: è il guasto del 02. Con il ticket, attese di 0,8 s e nessun timeout |
| Cancellazione | Un waiter cancellato lascia la fila a costo zero; dopo il fallimento nessuna chiamata in volo viene interrotta |
| Cache e ripresa | Risposte valide in cache anche dopo lo STOP; la ripresa con ledger riportato chiama solo i segmenti 4 e 5 |

**Payload e comportamento del modello invariati:**
- **Differenziale:** stesse 5 richieste byte per byte, stesso parallelismo, stesse uscite
  validate, stessa cache e stessa risposta unita, con e senza harness.
- **Prove precedenti ancora PASS:** `post_chat` reale (4 casi) e parametri, hook, redirect e
  timeout (4 casi).
- **Preflight browser:** esiti e prenotazioni (60.856) uguali a quelli del preflight del 02.
  Cambia solo il caso `budget`, da HTTP 500 a 503.

## Immutabilità verificata

- **Candidata `7b31d25`:** diff vuoto; il worktree `tesi-ruolo-checkbox-20261027` resta a
  `7b31d25`.
- **Tentativo 02:**
  - `SHA256SUMS` del backup OK;
  - `tar -d` di grezzi e cache: nessuna differenza;
  - FREEZE del 02: su 162 file cambiano solo `budget.py`, `metrics.py` e `server.py`;
  - FORM, SOURCE, catalogo, profilo e policy USER invariati.
- **App ordinaria:** nessun file modificato e nessun processo avviato o fermato.

## Rischi residui

1. **La formula `2 × byte` resta preregistrata.** Con richieste da circa 546k e un tetto di
   900k, la concorrenza a 3 del compilatore non è mai ammissibile: un'analisi nuova procede in
   serie, circa 5 × 100 s. Il lease è di 1.560 s e andrebbe al limite con 2 retry in serie.
2. **Dipendenze dell'hook:** `httpx.AsyncClient.__aenter__` e i nomi `_resilient_proposal` e
   `global_request`. L'hook è legato a HTTPX 0.28.1, verificato, e alla struttura di `7b31d25`.
   Se il ticket manca, l'attesa avviene in `post_chat` ed è registrata come `inside_request`.
3. **Chiamate non di segmento** (narratore 45 s, guardia 15 s): l'eventuale attesa resta dentro
   il loro timeout. Sono in sequenza, quindi non dovrebbero attendere.
4. **Prenotazione orfana nello stesso processo:** se `finish` non venisse eseguito, l'attesa
   durerebbe finché l'operatore chiude il gate. Non c'è un limite automatico.
5. **Simulatore:** risposte e usage sono sintetici; non prova la qualità del narratore né i
   tempi reali.
6. **`reference_date`:** la cache vale solo nella stessa data UTC (vedi
   [addendum](narratore-minervino-ripresa-02-addendum-2026-10-28.md)).
