# Addendum: eventuale ripresa della sessione Minervino 02 (da autorizzare)

**Non avviata.** Nessun gate aperto e nessuna chiamata. La sessione e gli artefatti del 02
restano immutati. L'harness è quello con i fix `bb602bb`, `c7e5fd7` e `89d1e2e`
([rapporto](harness-narratore-coda-budget-2026-10-28.md)).

## Stato verificato offline

- **Sessione `1d31b38c…`:** stato `FAILED`, fase `ANALYZING`, audit assente.
  - `resume` la riporta a `PENDING`.
  - Una nuova `/resolve` rifà quindi l'analisi.
- **Cache:** 4 voci (segmenti 1, 2, 3 e 5), identiche al backup.
- **Ricostruzione delle 5 richieste di segmento:** fatta con il codice `7b31d25` e il DB in sola
  lettura, senza LLM.
  - **Con `reference_date` 2026-10-28:** le richieste sono byte per byte quelle del 02.
    - I segmenti 1, 2, 3 e 5 vengono serviti dalla cache.
    - Viene chiamato solo il segmento 4, con un corpo identico a quello rifiutato.
  - **Con 2026-10-29:** cambiano tutti e 5 i digest e la cache non serve più.
  - **Causa:** `_prepare` imposta `reference_date` alla data UTC corrente, e la data entra nel
    digest.

**La finestra per un recupero senza scostamenti si chiude alle 00:00 UTC del 29 ottobre 2026,
cioè all'01:00 ora italiana.**

## Budget residuo e margine per il narratore

| Voce | Token |
|---|---:|
| Autorizzati | 900.000 |
| Consumati nel 02 (6 risposte misurate, 0 ignote) | 305.846 |
| **Residuo** | **594.154** |
| Prenotazione esatta del segmento 4 | 539.916 |
| Ticket del segmento (massimo sui 5 corpi) | 546.012 |
| Residuo garantito dopo il segmento 4, caso peggiore | 54.238 |
| Residuo stimato dopo il segmento 4 (usage dei segmenti nel 02: 62.815-83.878) | circa 510-531k, **stima** |

**Ledger:** nuovo, aperto con `carry()` dal ledger 02 (sha256 `3260b2f9…`). Riporta 305.846 token
a carico e nessun credito.

**Margine garantito per il narratore:**
- coincide con la riserva R: al massimo 48.142 con il ticket;
- arriva fino a 54.238 con la sola prenotazione esatta, che è immediata perché non c'è
  nient'altro in volo;
- proposta: **R = 40.000**.

**Quanto vale nei fatti:** il garantito non copre nemmeno una chiamata del narratore. Una
prenotazione del narratore vale `2 × byte + 32.768 + 2.048`. Le grandezze note:
- **Narratore:** con prompt da 10-30k token la prenotazione è di circa 110-265k. È una stima,
  perché su Minervino il narratore non è mai partito.
- **Routing:** nel 02 ha prenotato 63-64k e consumato 3,9-4,0k.
- **Margine stimato:** dopo il segmento 4 restano circa 510k. Il numero di turni e l'export non
  sono misurati.

**Opzione:** prenotare `1 × byte` invece di `2 × byte`. Resta una garanzia, perché con ByteLevel
BPE i token non superano i byte UTF-8. Il segmento 4 prenoterebbe 310.918 e il garantito dopo
salirebbe a 283.236. È però un cambio di regola, da preregistrare e autorizzare.

## Criteri d'arresto

**Prima del gate (tutti obbligatori):**
1. Verificare il backup del 02 (`SHA256SUMS` e `tar -d`). Il 02 resta immutato.
2. Lavorare su un **clone** del runtime 02, con una nuova cartella grezzi `…-02-ripresa`.
   - Serve un nuovo FREEZE: harness dai fix in poi, compilatore `7b31d25`, input invariati.
   - Il FREEZE del 02 non valida più, per i 3 file dell'harness cambiati: è voluto.
3. Ricostruire le 5 richieste nel clone: 4 digest devono essere in cache e il segmento 4 deve
   coincidere con il corpo rifiutato. Altrimenti non è un recupero e il gate non si apre.
4. Aprire il ledger con `carry` (305.846), R congelata e limite 900.000.
5. Riprendere con il controllo `resume` della sessione, senza un messaggio in chat: nessun
   routing prima di `/resolve`.

**Automatici durante la prova:**
- **Rifiuto dell'harness** (`impossible` o `stopped`): STOP, HTTP 503, 0 token.
- **Usage problematico** (mancante, incoerente o oltre la prenotazione): STOP.
- **Esito ignoto dopo l'invio** (`provider_timeout` o `cancelled_after_dispatch`): STOP.
- **Regole preregistrate:**
  - scrittura non dimostrata;
  - sospensione aggirata;
  - perdita di integrità;
  - input variati;
  - richiesta non ammessa;
  - budget che impedisce l'export.

**Manuali:**
- STOP se viene chiamato un segmento diverso dal 4: non sarebbe più un recupero.
- Nessuna nuova `/resolve` finché il ledger ha prenotazioni vive: dopo un errore i segmenti in
  volo completano comunque.

## Recupero o nuovo tentativo

| | Recupero della sessione 02 | Nuovo tentativo 03 |
|---|---|---|
| Sessione | La stessa, su un clone | Nuova, da seed |
| Chiamate di analisi | Solo il segmento 4, con richiesta identica al 02 | 5 segmenti |
| Budget | Residuo dei 900k: 594.154 | Nuova autorizzazione |
| Condizione | Stessa data UTC (entro le 00:00 UTC del 29/10) | Nessuna |
| Fattibilità con `2 × byte` | Sì, con R ≤ 48k | Entro 900k solo in serie e con R ≤ circa 39k (stima sull'usage del 02) |
| Rapporto | Continuazione del 02 | 03, separato |

**Dopo la mezzanotte UTC non va avviata.** La stessa sessione rifarebbe tutti e 5 i segmenti: il
primo (circa 546k) entra nel residuo, il secondo no, quindi STOP dopo circa un segmento.

**Alternative:**
- un nuovo tentativo 03, con una nuova autorizzazione;
- congelare `reference_date` alla data del 02 nel solo processo della ripresa.
  - Cambierebbe il payload rispetto all'app.
  - Va dichiarato e autorizzato.
  - Non è implementato.

## Proposta

1. **Se si vuole il recupero:** autorizzarlo esplicitamente entro le 00:00 UTC di oggi, cioè
   l'01:00 ora italiana, con R = 40.000, il ledger `carry` e i criteri sopra. Costo atteso: il
   segmento 4, circa 60-85k, più il narratore.
2. **Altrimenti:** un nuovo tentativo 03 con un nuovo budget, decidendo prima la regola di
   prenotazione: `2 × byte` in serie, oppure `1 × byte` preregistrata.
