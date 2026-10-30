# Stabilizzazione architetturale del compilatore DOCX (30 ottobre 2026)

## Riepilogo

- **Partenza (codice `45b8794`):** no, cinque usi reali dello stesso documento non danno oggi
  cinque risultati coerenti.
  - Minervino, nei run validi: 28, 42 e 1 campo corretto.
  - Trapani è stabile in 4 run su 5 (9/9).
  - Il benchmark checkbox varia fra 0 e 7.
- **Diagnosi:** la variabilità di Minervino non nasce dall'analisi (55-58 proposte documentate
  in ogni run), ma dal dialogo. Le cause sono tre, tutte dimostrate sui dati reali:
  1. la guardia rifiuta conferme esplicite perché il loro ambito dipende dal testo libero della
     condizione del modello;
  2. le sospensioni del narratore etichettate «source» citano testo del FORM e nessuna risposta
     USER le scioglie;
  3. le domande sono costruite su frammenti del FORM scelti dal modello («IN QUALITÀ DI»,
     «(eliminare le opzioni non pertinenti)»).
- **Correzioni:** 4 commit generali restano: osservabilità per campo, ambito delle conferme,
  sospensioni citate dal FORM, esiti di validazione. Ognuno ha test falliti prima e passati dopo
  e rollback verificato.
  - **Due correzioni annullate dopo la suite completa:** quella sul rinvio toglieva una protezione
    voluta; quella su codice fiscale e partita IVA si basava su una premessa sbagliata (la fonte
    stessa presenta il valore come codice fiscale).
- **Limite della verifica:** dalle 02:07 UTC DeepSeek ha risposto **402 (credito esaurito)**:
  27 chiamate su 30 rifiutate e la sonda successiva ancora 402. **La verifica reale dopo le
  correzioni non è stata eseguita.**
  - Applicando in modo deterministico le nuove regole agli output reali registrati, Minervino
    passerebbe da 28/42/1 a circa 57/47/41 corretti, senza valori attribuiti alla persona sbagliata.
  - È una stima, non un run reale.
- **Giudizio:** sistema **ancora sperimentale**.
  - Sicurezza: 0 dichiarazioni o caselle senza decisione valida in tutti i run, compresi quelli
    precedenti.
  - Correttezza e ripetibilità non sono ancora dimostrate sul codice finale.

## Dati e metodo

**Grezzo:** `backend/data/compilation-audit/stabilizzazione-20261030/`:
- `scenari/` con `MANIFEST.json`;
- `esecuzioni/`;
- `analisi/` (`variabilita.py`, `validi.py`, `controfattuale.py`);
- `strumenti/` (driver, servizio, valutatore, `aggrega.py`, `giro.sh`);
- `fuori-campione/` con `POOL.json`;
- `AGGREGATO-base.json`, suite e rollback.

La campagna precedente (`collaudo-e2e-20261029/`) è conservata intatta.

**Policy USER v3:** congelata prima di ogni run e identica per partenza e finale.
- Rispetto alla v2 aggiunge solo la conferma dei titoli «Il/la sottoscritto/a» e «IN QUALITÀ
  DI» negli scenari in cui l'utente ha deciso firmatario e qualità.
- Nessuna dichiarazione, designazione o casella autorizzata.

**Valutazione:** report del DOCX contro il gold; testo del DOCX esportato; esiti per campo
calcolati dallo stato del backend, non dalle note del narratore.

**Run validi:** senza risposte 402 dal provider. Ne segnalo a parte 4 con 429 recuperati.

## FORM e SOURCE

| FORM | Ruolo | SOURCE | Esito della campagna |
|---|---|---|---|
| Minervino V1 | sviluppo (gold 267 posizioni, 61 valori a T0) | Company KB Mapi, General KB, avviso | 3 run validi su 5 |
| Trapani Green | ha prodotto fix in passato | visura Mapi, avviso, disciplinare | 5 su 5 validi |
| Benchmark compilazione V1 | ha prodotto fix in passato | 7 fonti fittizie | 2 su 3 validi |
| Benchmark checkbox V1 | indipendente | 3 fonti fittizie | 3 su 3 validi |
| Catanzaro (solo azienda) | variante per il limite del corpus | visura Mapi | 1 su 3 validi |
| Bergamo All. 1 | fuori campione (29 ott) | visura Mapi | 3 su 3 (2 con 429 recuperati) |
| **CNR IRISS Allegato A** | **nuovo, estratto a caso** | visura Mapi | 0 validi (402 e 429) |
| **DGUE editabile, Univ. Trieste** | **nuovo, estratto a caso** | visura Mapi | FORM **non supportato**: «Non riesco a individuare campi compilabili…» (campi modulo Word) |

## Diagnosi: dove nasce la variabilità (run validi, codice di partenza)

| Scenario | Proposte documentate (analisi) | Scritti | Perdite principali (esiti per campo) |
|---|---|---|---|
| Minervino 1 | 58 | 27 | 29 sospesi dal narratore («source», citazione FORM) |
| Minervino 2 | 55 | 40 | 10 rinvii della policy, 5 sospesi |
| Minervino 3 | 55 | 0 | 41 rifiuti della guardia (8 verdetti `SUPPORTED/AMBIGUOUS`), 12 condizioni aperte |
| Trapani 1-4 | 9 | 8-9 | — |
| Trapani 5 | 9 | 0 | 9 rinvii: condizione ancorata a «(eliminare le opzioni non pertinenti)» |
| Checkbox 1 | **1** (12 negli altri run) | 0 | output del modello respinto dal validatore («soggetto/proprietà differenti») |
| Compilazione 1-2 | 23-24 | 17-22 | 5 sospesi in un run |

**Cause radice dimostrate:**
1. **Ambito delle conferme legato al testo del modello.** La guardia reale accetta la pertinenza
   (`result SUPPORTED`) e rifiuta l'ambito (`AMBIGUOUS`) quando la condizione del modello è un
   frammento, unisce due alternative o raggruppa destinazioni eterogenee. Prove: verdetti tracciati
   in Minervino 3 e Trapani; nella campagna precedente 6 rifiuti in un solo run di Trapani.
2. **Sospensioni «source» con citazioni del FORM.** Minervino 1: 29 campi, citazioni «e composta
   da (riportare nominativo…)» e «la quale ha come Responsabile della Progettazione…». Il blocco
   «source» per costruzione non si scioglie con una risposta USER.
3. **Rinvio sottoposto alla guardia.** Ciclo di 2-3 turni sullo stesso rinvio (campagna
   precedente).
4. **Codice fiscale di Catanzaro (riclassificato):** il valore «IT01234567890» nel codice
   fiscale non è un errore del modello. La visura simulata dice «CODICE FISCALE E PARTITA IVA
   IT01234567890 (dato simulato)».
   - La mappa lo vuole «da confermare» perché l'identificativo fittizio non supera il controllo
     formale.
   - Un controllo di formato (cifra di controllo) contraddirebbe il gold di Minervino, che si
     aspetta lo stesso identificativo: va deciso a livello di fixture.

**Altre cause dimostrate, esterne al codice o di limite:**
- **Provider:** 402 per credito esaurito (28 risposte) e 429 per limite di frequenza (11
  risposte) con 10 run in parallelo.
- **FORM non supportati:** il DGUE con campi modulo Word legacy.
- **Analisi:** un output incoerente del modello in checkbox.

**Ipotesi non dimostrate:**
- le domande ancorate a frammenti potrebbero dipendere anche dalla dimensione dei segmenti;
- il narratore reale potrebbe comportarsi diversamente vedendo le destinazioni elencate.

## Modifiche (commit isolati)

| Commit | Causa | Meccanismo |
|---|---|---|
| `c994a99` | Perdite ricostruibili solo leggendo le note | Esito strutturato per campo nel report privato: scritto, escluso, sospeso con il suo blocco, rinvio, rifiuto della guardia, condizione aperta, errore di validazione, dichiarazione non autorizzata, ecc. |
| `e789315` → **annullato da `381ed63`** | Partita IVA nel codice fiscale | Premessa sbagliata: la fonte presenta il valore anche come codice fiscale; la regola respingeva fonti legittime |
| `c3dd35e` | Ambito legato al testo del modello | Ogni domanda di applicabilità elenca le destinazioni del backend; una risposta sì/no pertinente ha esattamente quell'ambito. Risposte ambigue, non pertinenti o assegnate male restano rifiutate |
| `3c91005` → **annullato da `8629bd9`** | Ciclo sul rinvio | Toglieva la protezione contro il rinvio parziale di un blocco (`test_narrow_skip_cannot_silently_defer_a_condition_block`): il ciclo resta aperto |
| `94f0e82` | Sospensioni «source» con citazione FORM | Riclassificate come applicabilità: si sciolgono con lo slot o con le condizioni proprie confermate dall'utente; restano invariate le sospensioni che citano testo SOURCE e quelle con uno slot sbagliato |
| `37ae15c` | Proposte respinte assenti dagli esiti | Il report le classifica come errore di validazione |

**Invariati:** grounding SOURCE, validatori, autorizzazioni procedurali, gate di export e regole
sulle caselle. Nessuna conferma copre destinazioni non mostrate e nessuna dichiarazione è estesa.

**Test e rollback:**
- per ogni commit il nuovo test fallisce sul codice precedente e passa dopo (`rollback.txt`);
- suite backend su `381ed63`: 4.197 passati, 8 saltati; Ruff PASS (`suite-finale.txt`).

## Ripetibilità sul codice di partenza (run reali validi)

| Scenario | Corretti | Errati | Mancanti | Non attesi dal gold | Turni / domande |
|---|---|---|---|---:|---|
| Minervino | 28 / 42 / 1 | 1 / 0 / 0 (carica più ampia del gold) | 32 / 19 / 60 | 0 | 4 / 10-16 |
| Trapani | 9 / 9 / 9 / 9 / 1 | 0 | — | 0 | 2-4 / 4-6 |
| Compilazione | 17 / 18 | 0 | 1 / 0 | 0 | 3-4 / 7 |
| Checkbox | 0 / 7 / 7 | 0 | 7 / 0 / 0 | 0 | 1-3 / 0-3 |
| Catanzaro (azienda) | 4 | 0 | 9 | 2 (CF e P.IVA letterali della fonte, da confermare per la mappa) | 3 / 7 |
| Bergamo | 1 / 1 / 0 | 0 | — | 0 | 2-4 |

- **DOCX:** ogni valore dichiarato nel report è presente nel file esportato.
- **Dichiarazioni:** autorizzate 0, scritte 0.

## Stima deterministica del codice finale sugli output reali registrati (non è un run)

| Run | Corretti reali | Valori sbloccati | Di cui uguali al gold (equivalenze del valutatore) |
|---|---:|---|---|
| Minervino 1 | 28 | B: 29 sospesi | 29 (6 differiscono solo per «Ing.» o «Bari (BA)») |
| Minervino 2 | 42 | B: 5 | 5 |
| Minervino 3 | 1 | A: 41 rifiutati | 40, più la carica più ampia del gold |

Limite della stima: i verdetti della guardia e le scelte del narratore sono quelli registrati con
le domande vecchie, quindi la stima non vale come prova di stabilità.

## Confronto con la campagna precedente

| | Campagna 29 ott (`b0d66af`→`45b8794`) | Campagna 30 ott (`45b8794`→`37ae15c`) |
|---|---|---|
| Compilazioni reali | 44 (38 bozze) | 29 (21 valide; 7 con 402; 1 sonda) |
| Codice | 5 versioni diverse | partenza unica; finale non eseguito (402) |
| Policy | v1/v2 corrette fra i giri | v3 congelata |
| Minervino corretti | 27, 60, 9, 36, 0, 49, 52, 35 | 28, 42, 1 (validi) |
| Trapani | 1 → 8 (v1), 0-9 (v2) | 9, 9, 9, 9, 1 |
| Costo | 539 chiamate, 11,76 M token, ~1,48 USD | 286 chiamate, 5,71 M token, ~0,79 USD |

Gli scenari non sono perfettamente confrontabili: versioni di codice e policy diverse; nella
seconda campagna corpus Catanzaro ridotto e due FORM nuovi.

## Problemi aperti e rischi

1. **Verifica reale del codice finale mancante (402).** Comando pronto, da lanciare dopo una
   sonda:
   `CONCORRENZA=4 strumenti/giro.sh /home/montesano/tesi-stab-finale-381ed63 finale 18601
   minervino-v3:5 trapani-v3:5 catanzaro-azienda-v3:3 compilazione-v1:3 checkbox-v2:3
   bergamo-v3:3 cnr-iriss-allegato-a:3`
2. **Clausole scelte dal modello.** La domanda mostra ancora la citazione del modello, a volte
   un'istruzione senza significato. La correzione A rende stabile l'ambito, non la
   comprensibilità. Proposta: derivare la clausola dalla struttura del FORM, cioè dall'opzione o
   dalla sezione che governa le destinazioni.
3. **Variabilità dell'analisi** (checkbox 1 su 12 in un run). Il validatore protegge la
   correttezza ma non la copertura; serve una seconda analisi solo sui segmenti respinti.
4. **FORM con campi modulo Word legacy (DGUE)** non supportati.
5. **Limiti del provider:** con 10 run paralleli compaiono 429; il giro finale va eseguito con
   concorrenza 4.
6. **Policy simulata a regole:** fragile sui frammenti; la qualità con un utente reale non è
   misurata.
7. **Carica più ampia del gold** (Minervino `p14.s0`) e qualifica «Ing.»: precisione dei valori
   non ancora verificata in modo generale.
8. **Ciclo sul rinvio** (2-3 turni): richiede di distinguere un rinvio dell'intera conferma da uno
   parziale senza togliere la protezione esistente.
9. **Identificativi fittizi formalmente non validi** nelle fonti simulate: i gold li trattano in
   modo diverso (Minervino li scrive, Catanzaro li vuole da confermare).
