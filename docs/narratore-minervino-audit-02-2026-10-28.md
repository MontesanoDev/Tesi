# Audit E2E del narratore su Minervino — tentativo 02 (28 ottobre 2026)

**Esito: fallimento infrastrutturale dell'harness nell'analisi iniziale.** Nessun dialogo e
nessun DOCX. L'unico tentativo autorizzato è stato consumato; nessuna ripetizione. Il
tentativo 01 resta registrato invariato.

**Ambiente:**
- compilatore `7b31d25`, harness `7eb8f67`;
- runtime isolato `.tools/narratore-minervino-20261028-02` (porte 18080 e 15173);
- tetto di 900.000 token;
- gate aperto alle 19:21:29 UTC e chiuso alle 19:29:46 UTC.

**Grezzi** in questo worktree: `backend/data/compilation-audit/narratore-minervino-20261028-02/`,
cioè `server.log`, `budget-ledger.json`, `provider-calls/`, `timings.jsonl`, `http.jsonl` e
`browser/`. La revisione è autoriale.

## Cronologia (UTC)

| Ora | Evento | Token | Durata |
|---|---|---:|---:|
| 19:21:30 | Primo messaggio registrato, routing | 3.906 | 1,1 s |
| 19:21:32 | `/resolve`: analisi in 5 segmenti, segmento 1 da solo | 81.642 | 102,7 s |
| 19:23:15 | Segmenti 2, 3 e 4 lanciati in parallelo; prenotano 541k, 546k e circa 545k su 900k | — | — |
| 19:24:50 | Segmento 2 completato; il budget liberato va al segmento 5 | 83.878 | 95,8 s |
| 19:25:14 | Segmento 5 completato | 62.815 | 23,4 s |
| 19:25:15 | Segmento 4: attesa della prenotazione oltre 120 s, `RuntimeError` dell'harness, **HTTP 500** su `/resolve` | — | — |
| 19:25:16 | Richiesta d'export del protocollo: routing, 200 «La compilazione è in pausa…», nessun export | 4.015 | 0,9 s |
| circa 19:25:57 | Segmento 3, inoltrato dopo 119,4 s di attesa, risponde **dopo** il fallimento | 69.590 | 161,7 s |
| 19:29:46 | STOP, gate chiuso, servizi isolati fermati | — | — |

**Interfaccia:** coerente, con «compilazione interrotta» e «Analisi interrotta: nessun valore
applicato». Lo stato finale della sessione è `FAILED`, in pausa. Non c'è alcun HTTP 200 con
`generation_status=failed`: l'export non è stato tentato.

## Token, tempi e costo

- **Token misurati:** 305.846 su 6 risposte, 0 usage ignoti; 1 richiesta (segmento 4) non
  inoltrata.
  - routing: 7.921;
  - segmenti: 297.925, di cui 41.166 di reasoning.
- **Costo stimato:** circa 0,044 USD, con le tariffe registrate nel tentativo. È una stima, non
  una fattura.
- **Spreco:** 69.590 token del segmento 3 consumati dopo il fallimento.
- **Cache:** i segmenti validati restano in cache: 1, 2, 3 e 5.

## Obiettivi del mandato

**Punti 1-6** (ripetizioni, risposte non applicate, conferme perse, attribuzioni, sospensioni,
campi vuoti): **non osservabili**, perché narratore e dialogo non sono mai partiti.

**Campi richiesti:** `p12.s0` e `p14.s0` appartengono al segmento 1; `p39.cb0`, `p46.s1` e
`p49.s3` al segmento 2.
- Nessuno ha uno stato validato, perché unione e validazione non sono avvenute.
- Nelle risposte in cache, `p46.s1` e `p49.s3` sono proposte condizionali al ramo
  «società di ingegneria».
- `p12.s0`, `p14.s0` e `p39.cb0` non sono proposti come campi.

**Altri punti:**
- **confronto con il replay a 58 scritture:** non eseguibile, perché manca il DOCX;
- **punto 7:** tempi e token sono nella cronologia sopra;
- **fix ruolo e checkbox** (`7b31d25`, `f3bc281`): non esercitati.

## Causa (verificata)

1. **Prenotazioni troppo grandi per la concorrenza.** La formula `2 × byte + 32.768 +
   max_tokens` produce 529-546k per segmento, cioè 6,5-8,4 volte l'usage reale (62-84k). Con i 3
   segmenti paralleli del compilatore ne entra uno solo nei 900k; gli altri attendono.
2. **Attesa limitata a 120 s** (`audit_tools/narrator_harness/metrics.py`, in `observe`), che
   avviene dentro `post_chat` e quindi dentro il timeout della chiamata al modello. Un segmento
   dura 96-162 s, e il segmento 4 ha superato il limite.
3. **Eccezione non gestita.** Il `RuntimeError` dell'harness non rientra tra le eccezioni
   gestite per segmento (`GenerationError`, `ValueError`, `TimeoutError`, `httpx.HTTPError`,
   `compilation_global_sessions.py:401` e `:523`). Risale fino all'ASGI: HTTP 500 per l'intera
   analisi, mentre il segmento 3 resta in volo.

## Fix prioritari (proposti, non applicati)

1. **Harness, budget compatibile con la concorrenza.**
   - Un preflight rifiuta l'apertura del gate se concorrenza massima × prenotazione massima
     supera il budget.
   - Le prenotazioni restano garantite ma meno larghe: `1 × byte` invece di `2 × byte`, perché i
     token non superano i byte UTF-8. In alternativa, un budget dimensionato sulla concorrenza.
   - **Test:** rigioco delle 5 richieste registrate con prenotazioni concorrenti, senza attese né
     rifiuti e con usage registrato non superiore alla prenotazione.
2. **Harness, nessuna attesa dentro il timeout del modello e nessun crash.**
   - L'attesa dura solo finché si chiudono le chiamate pendenti, senza un limite fisso di 120 s.
   - Se la prenotazione è davvero impossibile, si fa uno STOP pulito prima dell'inoltro, con
     un'eccezione che il compilatore tratta come guasto del segmento senza retry.
   - **Test:** provider simulato, 3 segmenti da 150 s e budget stretto. Nessun 500, nessuna
     chiamata dopo lo STOP, nessun token speso dopo il fallimento.
3. **Compilatore, da valutare.** Un'eccezione inattesa in un segmento oggi produce un HTTP 500 e
   lascia in volo i segmenti paralleli.
   - Al primo errore non recuperabile, annullare i segmenti concorrenti e restituire un errore
     controllato, conservando la cache.
   - **Test:** eccezione iniettata nel segmento 4. Risposta controllata, segmenti in volo
     annullati, e una ripresa che richiama solo il segmento 4.

## Possibile prosecuzione, da autorizzare

Una ripresa della stessa sessione dall'interfaccia riuserebbe i 4 segmenti in cache e
chiamerebbe solo il segmento 4: prenotazione di circa 545k su un residuo di 594k. Sarebbe un
**secondo tentativo**, oggi non autorizzato, e conviene farlo solo dopo i fix 1 e 2.
