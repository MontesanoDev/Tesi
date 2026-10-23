# Campagna sulla candidata corretta (23 ottobre 2026)

**Esito preregistrato: favorevole.** Sei tentativi su sei eseguiti, 6 DOCX, 0 scritture non
dimostrate su 142, 0 scritture o proposte nelle 25 destinazioni sbagliate della rev 2.

È una verifica esplorativa, non una certificazione. La revisione delle scritture è autoriale e non
indipendente. Candidata non adottata, app live invariata, nessun commit né push. Come deciso
dall'utente, ci si ferma qui per valutare la chiusura del lavoro sperimentale.

**Riferimenti:**
- **Preregistrazione:** `PREREG-CANDIDATA-CORRETTA.md`, congelata alle 12:54:15 UTC prima di
  qualunque inferenza.
- **Grezzo:** `backend/data/compilation-audit/candidata-corretta-20261023-01/`
  (`e2e/EVENTI-CAMPAGNA.md`).
- **Risultati:** `benchmark ufficiale/candidata-corretta-20261023-01/`:
  - `ANALISI-SEZIONI.json`, `RIEPILOGO-SEZIONI.json`;
  - `REVISIONE-AUTORIALE.json`;
  - `CONFRONTO.json`.
- **Separazione:** la campagna arrestata `candidata-completa-20261023-01` resta separata e invariata.

## Candidata e preparazione

- **Profilo:**
  - V14 + K3;
  - stato derivato coerente;
  - dialogo P3;
  - `generation_revision 3`: FORM completo in ogni segmento, controllo d'ambito delle risposte USER;
  - recupero del narratore;
  - guardia rev 3 con motivazione fino a 1000 caratteri.
- **Codice:** 128 file applicativi congelati e controllati a ogni chiamata, invariati per tutta la
  campagna.
- **Congelamento:** harness, preregistrazione, protocollo, politica USER e test
  (`HARNESS-FREEZE.json`).
- **Prenotazione del budget:** caratteri × 0,40 + 1.024 + `max_tokens`, calibrata sul massimo
  misurato (0,303 token per carattere). Nessun consumo l'ha superata.
- **Scenari e SOURCE:** quelli della valutazione finale; corpora verificati identici.

## Verifiche offline prima delle inferenze

- **Contesto:** in tutte le 25 destinazioni sbagliate della rev 2 il paragrafo che governa il ramo
  è ora nell'input del segmento proprietario; nelle richieste rev 2 non c'era mai.
- **Rigioco deterministico** delle uscite registrate della rev 2 con il codice rev 3:
  - le 19 scritture sbagliate senza condizioni sarebbero ancora esportabili se il modello
    ripetesse la stessa uscita;
  - le 6 legate a `s2_c_sing` lo sarebbero solo con una conferma d'ambito della guardia.

  **La protezione contro i rami sbagliati non è garantita in modo deterministico**: dipende dal
  comportamento del modello con il FORM completo e dal giudizio della guardia. La campagna lo ha
  misurato.
- **Preservazione:** 103 scritture corrette rev 2 su 103 (Cesano 7/7) restano esportabili se la
  guardia conferma le risposte USER registrate.
- **Motivazioni più lunghe:**
  - 27 combinazioni di esiti e motivazioni (vuota, 1000 caratteri, testo persuasivo): accetta solo
    SUPPORTED/SUPPORTED;
  - la motivazione non è salvata né letta da altre logiche;
  - i consensi V14 richiedono comunque un assenso USER esplicito;
  - la guardia ordinaria resta a 250.
- **Suite:** 3.677 PASS, Ruff PASS.

## Risultati per tentativo

| Tentativo | DOCX | Scritture | Non dimostrate | Copertura | Segmenti (retry) | Token | Tempo |
|---|---|---|---|---|---|---|---|
| soresa2023-1 | sì | 8 | 0 | 47% | 2/2 (1, recuperato) | 197.497 | 250 s |
| minervino-1 | sì | 56 | 0 | 93% | 5/5 (0) | 388.459 | 312 s |
| catanzaro-1 | sì | 22 | 0 | 45% | 6/6 (1, recuperato) | 650.964 | 251 s |
| soresa2023-2 | sì | 8 | 0 | 47% | 2/2 (0) | 170.593 | 155 s |
| minervino-2 | sì | 30 | 0 | 50% | 5/5 (0) | 570.624 | 298 s |
| catanzaro-2 | sì | 18 | 0 | 32% | 6/6 (0) | 592.058 | 305 s |

Criteri preregistrati:
- **(a)** 0 scritture non dimostrate;
- **(b)** 0 scritture nelle 25 destinazioni;
- **(c)** 0 scritture SOURCE in destinazioni non verificate, 0 scritture in regioni d'opzione senza
  autorizzazione, 0 risposte 409;
- **(d)** 6/6 DOCX;
- **(e)** 0 verifiche d'ambito respinte per la lunghezza della motivazione.

Tutti soddisfatti. Nessun arresto, nessun tentativo mancante.

## Confronto puntuale (descrittivo, non appaiato)

Stessi tre moduli. Monolitica: 5 tentativi per modulo nella valutazione finale; rev 2: 2 per
modulo. Giorni diversi, modello non deterministico, stessa procedura e stesse SOURCE.

### Scritture nei rami sbagliati della rev 2

| Destinazioni | Rev 2 | Candidata corretta: scritte / proposte | Monolitica | Campagna arrestata |
|---|---|---|---|---|
| Minervino `p37.*`, ramo studio associato | 7 | 0 / 0 | 0 | 0 |
| Catanzaro `t19.*`, sezione 5.c | 5 | 0 / 0 | 0 | 0 |
| So.Re.Sa. `p127.*`, `p43`/`p44`: avvalimento e blocchi RT | 13 | 0 / 0 | 0 | 0 (nessun DOCX) |

- Nella candidata corretta nessun segmento ha nemmeno *proposto* valori in quelle destinazioni.
- In minervino-2 il modello ha legato il ramo studio associato a una condizione esplicita, rinviata
  dall'USER.

### Scritture corrette della rev 2 preservate

| Tentativo | Preservate | Mancanti e motivo |
|---|---|---|
| soresa2023-1/2 | 8/9 | `p31.s0`: nome USER nel blocco di un componente RT, già discutibile nella rev 2; ora non viene chiesto né scritto (fuori dal nucleo) |
| minervino-1 | 52/54 | `p15.s0`, `p53.s0`: proposte respinte dal validatore (motivo registrato) |
| minervino-2 | 28/54 | tecnici `p43`-`p53`: 21 sospesi dal narratore, condizione sul direttore tecnico chiusa dalla guardia dei cicli |
| catanzaro-1 | 17/19 | forma giuridica: conflitto fra trascrizioni di tre segmenti, in revisione |
| catanzaro-2 | 18/19 | `t0.r0.c1`, nome del sottoscritto: proposta respinta dal validatore |

### Copertura, DOCX e fallimenti

| Modulo | Candidata corretta | Rev 2 | Monolitica |
|---|---|---|---|
| Minervino: DOCX / copertura mediana | 2/2 / 72% (93% e 50%) | 1/2 / 90% | 4/5 / 79% |
| Catanzaro | 2/2 / 39% | 2/2 / 32% | 4/5 / 32% |
| So.Re.Sa. | 2/2 / 47% | 2/2 / 37% | 5/5 / 47% |
| Fallimenti | nessuno | 1 NARRATOR | 1 EXPORT, 1 MODEL |

- **Segmenti recuperati:** 2. In soresa2023-1 e catanzaro-1 un segmento ha restituito un JSON non
  valido (non troncato) e il retry previsto lo ha recuperato. Nella monolitica lo stesso tipo di
  errore fa perdere il tentativo, come accaduto due volte nella valutazione finale.
- **Robustezza:**
  - 0 segmenti persi;
  - 0 errori del narratore, quindi il recupero del narratore non è stato messo alla prova;
  - 0 verifiche della guardia respinte.
- **Conflitti fra segmenti:** 2 (Catanzaro), entrambi passati in revisione senza valore scritto. È
  prudente, ma costa copertura.
- **Dialogo:**
  - 7 conferme ridondanti;
  - 1 intervento della guardia dei cicli;
  - vuoti con motivo tracciato 102/102.

### Token e latenza

| Modulo, mediane per tentativo | Candidata corretta | Rev 2 | Monolitica |
|---|---|---|---|
| Minervino: token / tempo | 480k / 305 s | 339k / 724 s (con un timeout) | 212k / 183 s |
| Catanzaro | 622k / 278 s | 332k / 239 s | 142k / 163 s |
| So.Re.Sa. | 184k / 202 s | 121k / 163 s | 91k / 125 s |
| Tempo mediano dell'analisi | 226 s | 192 s | 134 s |

- **Totale:** 2.570.195 token misurati su un tetto di 2.800.000 (previsti 2,52 M), di cui
  1.174.400 in cache e 315.500 di ragionamento; circa 0,40 USD.
- **Rispetto alla monolitica:** costa 2-4,4 volte i token e circa 1,6-1,7 volte il tempo. È il
  prezzo del FORM completo in ogni segmento e della guardia con contesto pieno.

## Limiti

- Revisione autoriale, non indipendente; un solo modello; SOURCE sintetiche; n = 6.
- Lo zero nei rami sbagliati è osservato, non garantito: offline 19 di quelle scritture
  supererebbero i controlli deterministici se il modello le riproponesse.
- **Narratore:** in minervino-2 ha sospeso 21 campi corretti con una motivazione non ancorata al
  FORM, e ha lasciato esportare l'iscrizione del secondo tecnico (`p46`) senza il nome: blocco
  incompleto, giudicato dimostrato perché valore, soggetto e ramo lo sono. È un difetto di qualità,
  non di sicurezza.
- **Copertura:** resta bassa su Catanzaro e So.Re.Sa. (binding «in qualità di», condizioni non
  confermate, conflitti); fuori perimetro.
- **Non osservati:** recupero del narratore, ripresa dopo un'interruzione, fallimento definitivo di
  un segmento.

## Giudizio

Secondo i criteri preregistrati, l'esito è **favorevole**:
- la candidata corretta ha eliminato, nei tentativi osservati, le scritture nei rami sbagliati della
  rev 2;
- ha preservato le scritture corrette dove narratore e conflitti non le hanno trattenute;
- ha recuperato due segmenti che nella monolitica avrebbero fatto perdere il tentativo;
- non ha prodotto scritture non dimostrate.

Il prezzo è più token e più latenza. Restano due limiti: copertura ancora bassa su due moduli e
sicurezza dimostrata solo empiricamente.

Come da istruzioni non si apre un nuovo ciclo di correzioni. Restano decisioni separate
dell'utente:
- chiusura del lavoro sperimentale;
- eventuale adozione (non automatica);
- eventuale revisione indipendente del pacchetto.
