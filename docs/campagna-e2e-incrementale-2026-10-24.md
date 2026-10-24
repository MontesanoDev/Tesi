# Campagna E2E della candidata incrementale (24 ottobre 2026)

**Esito esplorativo: favorevole per sicurezza, con una disponibilità di 5 DOCX su 6.**
- 6/6 tentativi eseguiti, 5 DOCX;
- 101 scritture riviste: 101 DIMOSTRATA, 0 DUBBIA, 0 NON_DIMOSTRATA;
- 0 aggiramenti di sospensioni o gate;
- 0 scritture e 0 proposte nelle 25 destinazioni storiche;
- 1.959.366 token su un tetto di 3.000.000.

È una verifica esplorativa, non una certificazione. La revisione è **autoriale e non indipendente**:
- Codex per catanzaro-1, minervino-1, soresa2023-1 e cesano-1;
- Claude, che ha ripreso la campagna dopo l'interruzione di Codex, per catanzaro-2 e minervino-2.

Candidata non adottata, nessun merge in `main`, nessun flag nell'app live. Nessun cambiamento di
codice, prompt o criteri durante le prove.

**Riferimenti:**
- **Proposta approvata:** `docs/proposta-e2e-incrementale-2026-10-24.md`.
- **Preregistrazione e harness congelati:**
  `backend/data/compilation-audit/incrementale-e2e-20261024-01/` (`PREREG-INCREMENTALE-E2E.md`,
  `HARNESS-FREEZE.json`, `out/FROZEN-BEFORE-FIRST-CALL.json`, 10:37:08 UTC).
- **Risultati:** `benchmark ufficiale/incrementale-e2e-20261024-01/`:
  - `ANALISI-SEZIONI.json`, `REVISIONE-AUTORIALE.json`;
  - `MISURE-INCREMENTALI.json`, `CONFRONTO.json`.
- **Riepilogo per il rapporto:** `backend/data/compilation-audit/incrementale-e2e-20261024-01-rapporto/out/riepilogo.json`.

## Candidata

**Codice:** `3ec0af0`, worktree `/home/montesano/tesi-docx-offline`, branch
`miglioramenti/2026-10-23-docx-offline`. Il runtime è identico a quel commit, controllato a ogni
chiamata.

**Profilo:**
- V14, K3, stato derivato;
- dialogo P3;
- generazione per sezioni rev 3;
- recupero del narratore;
- R1;
- controllo delle tabelle condizionali (`table_scope_revision 1`);
- riesame SOURCE delle sospensioni (`hold_rereview_revision 2`);
- veto API generale della bozza esplicita.

**Provider:** `deepseek-flash`.

## Svolgimento

| # | Tentativo | DOCX | Scritture (giudizi) | Copertura del nucleo | Token | Tempo | Note |
|---|---|---|---|---|---|---|---|
| 1 | catanzaro-1 | sì | 25 (25 D) | 55% (17/31) | 581.058 | 223 s | 6 regioni tabellari riconosciute |
| 2 | minervino-1 | **no** | — | — | 0 | 0,2 s | **fallimento DRIVER**: frontend non attivo (`ERR_CONNECTION_REFUSED`), 0 chiamate LLM; non ripetuto né sostituito |
| 3 | soresa2023-1 | sì | 2 (2 D) | 13% (2/15) | 167.036 | 183 s | 5 sospensioni del narratore |
| 4 | cesano-1 | sì | 4 (4 D) | 100% (4/4) | 175.331 | 197 s | nucleo di sole 4 destinazioni |
| 5 | catanzaro-2 | sì | 15 (15 D) | 48% (15/31) | 590.926 | 306 s | 1 conflitto in revisione |
| 6 | minervino-2 | sì | 55 (55 D) | 92% (55/60) | 445.015 | 1.822 s | interruzione programmata e ripresa |

**Totali:**
- 1.959.366 token, di cui 886.016 in cache e 245.036 di ragionamento;
- circa 0,31 USD alla tariffa congelata fuori punta (stima da usage, non fattura);
- 2.731 s complessivi, compresa l'attesa del lease in minervino-2.

**Retry e risposte:**
- 0 retry di segmento, 0 risposte 409, 0 consumi ignoti;
- gli «errori» del browser sono richieste annullate (`ERR_ABORTED`) durante gli aggiornamenti
  della pagina, salvo il guasto di minervino-1.

## Risposte alle domande

1. **DOCX prodotti:** 5 su 6. L'unico fallimento è infrastrutturale, non della candidata: il servizio
   UI non era attivo all'apertura di minervino-1. Codice e database sono risultati invariati e il
   tentativo è registrato come fallito, non sostituito.
2. **Giudizi delle scritture:** 101 corrette, 0 dubbie, 0 indebite. Revisione autoriale.
3. **Errori nei rami:** nessuna ricomparsa. Nessuna scrittura né proposta valida nelle 25
   destinazioni storiche (Catanzaro `t19.*`, Minervino `p37.*`, So.Re.Sa. `p127.*`/`p43`/`p44`).
   - In minervino-2, R1 ha esteso 5 condizioni dei rami non applicabili (studio associato, RTP,
     consorzio: 73 destinazioni) rimaste senza conferma e non scritte.
4. **Controllo delle tabelle:** **non ha dovuto bloccare nulla**. In entrambi i tentativi Catanzaro
   ha riconosciuto 6 regioni tabellari condizionali, ma il modello non ha mai proposto valori
   nella sezione 5.c. È un'assenza di proposte, non un veto esercitato; la protezione resta
   dimostrata solo offline.
5. **Riesame SOURCE del narratore:** **non ha recuperato alcun campo**.
   - Una sola sospensione è stata marcata per il riesame (catanzaro-2, `t44.r1.c0`), ma non c'è
     stata una narrazione successiva.
   - In minervino-2 il narratore non ha sospeso nulla: soci e direttore tecnico, cioè i campi che
     la correzione voleva recuperare, sono stati scritti tutti, ma non grazie al riesame.
6. **Nuove omissioni e falsi rifiuti** rispetto ai gemelli della campagna sprint:
   - **soresa2023-1:** 1 campo in meno, ancora sospeso dal narratore con il motivo «partecipazione
     singola», già confermata. Lo stesso falso rifiuto di prima: le 5 sospensioni restano, fuori
     dal perimetro del riesame.
   - **minervino-2:** 2 campi in meno, rinviati dall'USER (provincia e data d'iscrizione); non è un
     rifiuto del sistema.
   - **catanzaro-1, catanzaro-2:** nessuna perdita; 6 e 2 scritture corrette in più.
   - **Proposte respinte dal validatore:** catanzaro-1 2, soresa 2, cesano 3, catanzaro-2 8;
     restano vuote con motivo tracciato.
   - **Nessun rifiuto** è attribuibile al controllo delle tabelle, a R1 o al veto API.
7. **Copertura, token e latenza per modulo**: confronto descrittivo, non appaiato; giorni e modello
   possono variare.

   | Modulo | Incrementale | Sprint | Candidata corretta | Monolitica |
   |---|---|---|---|---|
   | Catanzaro: DOCX / copertura mediana | 2/2 / 52% (55%, 48%) | 2/2 / 39% | 2/2 / 39% | 4/5 / 32% |
   | Minervino | 1/2 / 92% | 2/2 / 81% | 2/2 / 72% | 4/5 / 79% |
   | So.Re.Sa. | 1/1 / 13% | 2/2 / 30% | 2/2 / 47% | 5/5 / 47% |
   | Cesano | 1/1 / 100% | — | — | 4/5 / 100% |
   | Token mediani Catanzaro / Minervino / So.Re.Sa. / Cesano | 586k / 445k / 167k / 175k | 600k / 550k / 130k / — | 622k / 480k / 184k / — | 142k / 212k / 91k / 95k |

   **Lettura prudente:**
   - **Catanzaro:** migliora, ed è il valore più alto osservato.
   - **Minervino:** 92%, ma su un solo DOCX.
   - **So.Re.Sa.:** resta bassa.
   - **Cesano:** in linea con la monolitica.
   - **Campioni:** troppo piccoli per parlare di superiorità.
   - **Costo:** la candidata costa da 1,8 a 4,1 volte i token della monolitica.

## Interruzione programmata (minervino-2)

**Sequenza:**
1. Alle 15:29:58 UTC, dopo il primo segmento validato e salvato (67.303 token), il runtime è uscito
   con codice 88 senza inoltrare il segmento successivo. Nessuna chiamata in volo, registro coerente.
2. Il supervisore lo ha riavviato una volta.
3. Il browser ha atteso la scadenza naturale del lease, senza intervenire sul database.
4. Alle 15:54:59 UTC ha inviato «Riprendi la compilazione interrotta.» dall'interfaccia ordinaria.

**Esito:**
- **Cache:** il segmento 1 è stato riusato dalla cache e solo i segmenti 2-5 sono stati chiamati,
  una volta ciascuno.
- **Duplicazioni:** nessuna chiamata o proposta duplicata, 0 retry.
- **Esito finale:** DOCX esportato.
- **Limite reale emerso:** dopo un crash l'utente deve aspettare circa 25 minuti, la scadenza del
  lease, prima di poter riprendere.

## Dimostrato e solo offline

**Dimostrato dal vivo in questa campagna:**
- 0 scritture non dimostrate su 101, 0 aggiramenti, 0 rami sbagliati;
- ripresa reale dopo un'interruzione, con riuso della cache e senza duplicazioni;
- veto API attivo senza rifiuti in esportazioni lecite (5 export riusciti, 0 risposte 409).

**Verificato solo offline:**
- il blocco deterministico della sezione 5.c (rigiochi: 12→7 con ricevute registrate, 18→13 con
  guardia simulata);
- il recupero dei campi tramite riesame SOURCE (controfattuali 46→52 e 51→59);
- i 10 scenari di ripresa;
- la chiusura dei 13 casi So.Re.Sa., che **non** è risolta nemmeno offline.

## Limiti

- Revisione non indipendente; n = 6, con un fallimento infrastrutturale; un solo modello; SOURCE
  sintetiche.
- L'assenza di proposte rischiose non prova l'efficacia dei veti.
- Le sospensioni non fondate di So.Re.Sa. sono ancora presenti.
- Dopo un crash la ripresa richiede di aspettare la scadenza del lease.
