# Candidata completa: campagna esplorativa arrestata (23 ottobre 2026)

**Esito: campagna arrestata dopo 3 tentativi su 8** per un difetto del nuovo backend, come
prevede la preregistrazione. Il difetto è la verifica d'ambito della guardia rev 3, che respinge
output corretti per la lunghezza della motivazione. Nessuna scrittura non dimostrata.

Candidata non adottata, nessuna modifica al codice durante la campagna, nessun commit. La revisione
delle scritture è autoriale (Claude), non indipendente.

**Riferimenti:**
- **Preregistrazione:** `PREREG-E2E-SEZIONI.md`, preparata da Astra.
- **Addendum prima delle inferenze:** `ADDENDUM-PREFLIGHT.md` (Astra) e
  `ADDENDUM-2-PRIMA-DELLE-INFERENZE.md`:
  - ricongelamento dell'harness corretto;
  - ordine minervino-1, catanzaro-1, soresa2023-1, minervino-2, catanzaro-2, soresa2023-2,
    cesano-1, cesano-2;
  - stime di budget aggiornate.
- **Grezzo:** `backend/data/compilation-audit/candidata-completa-20261023-01/` (registro
  `e2e/EVENTI-CAMPAGNA.md`, `e2e/STOP.json`).
- **Risultati:** `benchmark ufficiale/candidata-completa-20261023-01/`.

## Profilo

- V14 + K3;
- `derivation_revision 1` (predefinita dal passo 1);
- `dialogue_revision 1`;
- `generation_revision 3`: FORM completo in ogni segmento, controllo d'ambito delle risposte USER;
- `narration_recovery_revision 1`.

Stessi scenari, politica USER, SOURCE e riferimenti v3 della valutazione finale. I controlli
preliminari sono superati (`out/preflight-2.json`) e il codice applicativo è invariato per tutta la
campagna (128 hash controllati a ogni chiamata).

## Risultati

| Tentativo | DOCX | Scritture | Non dimostrate | Rami sbagliati della rev 2 | Copertura del nucleo | Token | Tempo |
|---|---|---|---|---|---|---|---|
| minervino-1 | sì | 39, tutte uguali al riferimento | 0 | `p37.*` vuoti (rev 2: 7) | 65% | 484.353 | 281 s |
| catanzaro-1 | sì | 11, tutte uguali al riferimento | 0 | `t19.*` vuoti (rev 2, catanzaro-2: 5) | 35% | 536.892 | 231 s |
| soresa2023-1 | **no** | 0 | 0 | nessuna proposta in `p127`, `p43`/`p44`, `p31`/`p32` (rev 2: 6) | — | 162.994 | 1149 s |

**Confronto descrittivo, non appaiato:**
- monolitica (mediane): Minervino 79%, Catanzaro 32%, So.Re.Sa. 47%;
- rev 2: minervino-1 90% con 7 scritture sbagliate; catanzaro-1 29%.

**Esecuzione dei tentativi:**
- 13/13 segmenti analizzati al primo tentativo, nessun retry;
- un conflitto fra segmenti (nome di un tecnico in Catanzaro) passato in revisione, nessun valore
  scritto;
- 0 risposte 409;
- 0 errori del narratore, quindi il recupero del passo 3 non è stato messo alla prova.

**Vuoti:** tutti con motivo. In Minervino 12 sono sospensioni del narratore e 7 condizioni non
confermate o respinte. La verifica di Minervino respinta per lunghezza aveva comunque esito
UNRELATED/AMBIGUOUS, quindi la decisione sarebbe stata la stessa.

**Costi:**
- 1.184.239 token misurati (nessun consumo ignoto), circa 0,18 USD;
- la cache del provider copre fino a due terzi dell'input dei segmenti;
- Minervino e Catanzaro costano 2,3-3,8 volte la mediana monolitica.

## Il difetto che ha fermato la campagna

- **Nei tentativi eseguiti:** la guardia rev 3 ha prodotto 7 verifiche d'ambito.
  - 3 sono state respinte dalla validazione dello schema perché la `rationale` aveva 251, 261 e 308
    caratteri, oltre il limite di 250.
  - Nelle due di So.Re.Sa. l'esito era «SUPPORTED» sia per la pertinenza sia per l'ambito: risposte
    corrette perse.
  - In quella di Minervino l'esito era UNRELATED/AMBIGUOUS: sarebbe stata respinta comunque.
  - La motivazione non è usata da nessuna decisione: viene solo validata.
- **Origine:** il limite di 250 caratteri esisteva già. Nella rev 3 la guardia riceve il FORM
  completo e deve giustificare anche l'ambito, quindi scrive di più.
- **Effetto:** il rifiuto è sicuro (nessuna autorizzazione), ma la risposta USER non viene
  applicata e la sessione non avanza.
- **In soresa2023-1:**
  - sono state respinte la registrazione della partecipazione singola dal messaggio iniziale e poi
    la conferma esplicita;
  - l'app ha chiesto di precisare;
  - la politica USER preregistrata non riformula, quindi timeout del driver.
- **Classificazione:** lo strumento di analisi lo classifica DRIVER; la causa effettiva è il nuovo
  backend.

Il codice non si può correggere durante la campagna. La preregistrazione prevede l'arresto
immediato per un difetto grave del nuovo backend: la campagna è stata fermata.
- Tentativi non avviati, per arresto e non per budget o sicurezza: minervino-2, catanzaro-2,
  soresa2023-2, cesano-1, cesano-2.
- Gli otto tentativi restano nel denominatore.

## Che cosa dice e che cosa non dice

- **Indicazioni favorevoli** sull'ipotesi della rev 3 (il FORM completo elimina il contesto di ramo
  mancante):
  - nei rami che la rev 2 aveva compilato per errore nessuna scrittura (Minervino, Catanzaro) e
    nessuna proposta (So.Re.Sa.);
  - le scritture prodotte sono tutte nel ramo dello scenario.
- **Non è una prova:**
  - 2 DOCX;
  - il caso più severo, So.Re.Sa., non ha prodotto scritture;
  - la revisione è autoriale.
- **Non verificati:**
  - il recupero del narratore;
  - la ripresa dopo un fallimento di segmento;
  - il comportamento su minervino-2, catanzaro-2, soresa2023-2 e Cesano.

## Correzione proposta (non implementata)

Nella sola verifica d'ambito rev 3 (`FormScopeCheck`):
- non respingere l'output per la lunghezza di una motivazione che nessuna logica usa, per esempio
  alzando il limite a 1000 caratteri;
- lasciare invariati gli altri vincoli (esiti, slot, duplicati, destinazioni).

Test proposti:
- i tre output registrati e respinti devono essere accettati con la stessa decisione;
- un output con esito mancante o duplicato deve restare respinto.

Dopo la correzione serve una **nuova** campagna preregistrata, con nuovo congelamento. Questa resta
arrestata e i suoi risultati restano invariati. Budget residuo del tetto precedente:
1.815.761 token.
