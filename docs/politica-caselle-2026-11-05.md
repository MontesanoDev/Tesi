# Domande sulle caselle e criteri di valutazione

Rapporto del 5 novembre 2026. Ramo `narratore-chiarezza/2026-10-31`, commit `d57ff89` sopra `1e7a22f`.
Nessun push, merge o promozione. La demo ordinaria non è stata toccata.

## Esito

**Tutti i controlli passano.** Il ramo supera i criteri aggiornati ed è pronto per la tua prova manuale. Non
è stato promosso.

| Criterio | Esito | Prova |
|---|---|---|
| 0 scritture non attese | superato | 0 in 18 esecuzioni su 19, lette dai DOCX. La 19ª è il test in cui l'utente conferma di proposito una casella contro le fonti |
| `p65.*` vuoti anche con la conferma errata del ramo | superato | sessione reale con ramo confermato, router e guardia DeepSeek reali |
| Nessun 5xx | superato | 0 dell'app, 0 del provider |
| Caselle indebite | superato | 0 nelle bozze finali, lette dall'XML |
| Caselle scelte ma rimaste vuote | superato | 0 |

**Il risultato più visibile:** Minervino con la politica simulata passa da 58 / 22 / 51 corretti a **60 / 59**,
perché la domanda di scelta è tornata. Le esecuzioni sono solo 2 e 3 per scenario: è un miglioramento
coerente con la causa, non una misura di stabilità.

**Una correzione al rapporto precedente:** avevo scritto zero scritture indebite su 20 esecuzioni. Era vero per
ciò che il sistema scrive. Con il nuovo criterio, però, le due esecuzioni checkbox di allora contano 1 casella
indebita ciascuna: la spunta dell'originale restava lì, non confermata. Ora viene tolta e nominata.

## Cosa è cambiato

Tutto è attivo solo con il nuovo flag `checkbox_policy_revision`, nel profilo `sezioni-2026-11-05`. Le
sessioni già esistenti non cambiano.

| Richiesta | Comportamento | Dove |
|---|---|---|
| Una domanda prioritaria sul ramo | La scelta torna tra le domande quando riguarda il ramo del FORM o tiene sospese almeno 3 destinazioni. Sempre una domanda alla volta, prima quella che sblocca di più | `selective_pool`, `branch_choice_unlocks` |
| Non ripetere | Una scelta data o rinviata non viene più chiesta | già nel pool, ora con test |
| Scelta rinviata | **Difetto corretto:** un rinvio rilasciava i dati sospesi su quella scelta. Ora restano sospesi fino a una scelta esplicita | `_blocker_answered` |
| Esportazione immediata | Sempre possibile, anche con la domanda aperta | nessuna modifica |
| Gruppi senza selezione | La bozza li nomina, dice se la scelta è rinviata e cosa indicano le fonti. Lo stesso elenco è nel report | `checkbox_review` |
| Caselle già spuntate nell'originale | Tolte all'export e nominate, se nessuna scelta USER le conferma. Se la casella è protetta resta com'è e viene segnalata | `unconfirmed_initial_boxes`, `clearable_controls` |
| Spunta originale nel ramo | Non impedisce più la domanda di scelta | `_capacity_trigger` |

**Decisioni mie, da valutare nella prova:**
- **Togliere la spunta invece di conservarla.** Una spunta non confermata su un modulo legale è un'affermazione; una
  casella vuota è un'omissione visibile. Il costo è che si modifica un valore del FORM. Lo dice sempre la bozza.
- **Soglia di 3 destinazioni** per le scelte non legate al ramo del FORM. Sotto, la domanda sarebbe poco utile.
- **Le caselle senza dipendenze non vengono chieste**, per non creare un questionario: la bozza le elenca con il
  suggerimento delle fonti e basta una frase per indicarle.

Non sono state indebolite le guardie su rami, soggetti e dichiarazioni. Il rinvio e il blocco degli altri rami sono
più severi di prima.

**Esempi reali:**

> Quale opzione di «IN QUALITÀ DI» scegli? Indica il numero di una sola opzione: nessuna casella viene spuntata senza
> la tua scelta. […] 4) Legale rappresentante di società di professionisti o di società di ingegneria (ramo già confermato)

> Caselle ancora senza selezione: «Tipologia del richiedente» (le fonti indicano «Organizzazione tecnica»); […] Nessuna
> casella viene spuntata senza la tua scelta: puoi indicarla quando vuoi. Nel modulo originale era già spuntata
> «Professionista autonomo»: non è una tua scelta, quindi in questa bozza l'ho tolta. Se vale, dimmelo.

## Nuovo criterio per le caselle

Il numero di caselle segnate non è più confrontabile con lo storico: il 2 di oggi e il 7-8 del 30 ottobre misurano
politiche diverse. Ogni casella è ora classificata dall'XML del DOCX, da `analisi/valuta_caselle.py`:

| Categoria | Significato | Atteso |
|---|---|---|
| Autorizzata | Spuntata e una scelta USER la seleziona | quando l'utente sceglie |
| **Indebita** | Spuntata senza scelta USER, comprese le spunte dell'originale | **sempre 0: blocca la promozione** |
| Vuota corretta | Vuota e nessuna scelta la seleziona | |
| **Vuota con scelta** | Vuota benché l'utente l'abbia scelta | **sempre 0: è un difetto** |
| Spunta originale tolta | Spuntata nell'originale, ora vuota, senza scelta USER | deve essere nominata |
| Suggerita dalle fonti | Tra le vuote corrette, le fonti la indicano | il suo gruppo deve essere nominato |

Il controllo è valido: sulle vecchie bozze segnala la spunta conservata di `checkbox-v2-fin2-1`. Non sostituisce il gold, che resta il riferimento per i valori di testo: «indebita» dice se c'è un'autorizzazione, non se la scelta è giusta.

## Campagna

**Condizioni:** patch su `1e7a22f` in un worktree fisso, poi committata con contenuto identico (stesse impronte),
profilo `sezioni-2026-11-05`, modello `deepseek-flash`, runtime nuovo per ogni esecuzione, al massimo 4 insieme.

**Script aggiunti, senza modificare `esegui_dialogo.py`:** `dialogo_guidato.py` risponde a ciò che viene chiesto. Serviva
perché il vecchio script smette di rispondere quando la domanda attiva è la scelta: per questo `pc-dialogo-1` e `-2` si
fermano a 41 e 35.

### Risultati

Punteggio contro il gold sull'ultima bozza. Caselle lette dall'XML.

| Scenario | Esecuzione | Corretti | «Errati» | Mancanti | Non attese | Autorizzate | Indebite | Domande sulla scelta |
|---|---|---|---|---|---|---|---|---|
| Minervino, domanda e scelta 4, politica simulata | `minervino-v3-pc-1` | 60 | 1 | 0 | 0 | `p39` | 0 | 1 |
| | `minervino-v3-pc-2` | 59 | 1 | 1 | 0 | `p39` | 0 | 1 |
| Minervino, domanda e scelta 4, messaggi del test manuale | `pc-guidato-1` | 49 | 1 | 11 | 0 | `p39` | 0 | 1 |
| | `pc-guidato-2` | 59 | 2 | 0 | 0 | `p39` | 0 | 1 |
| | `pc-guidato-3` | 58 | 2 | 1 | 0 | `p39` | 0 | 1 |
| Minervino, prima bozza senza scelta | `pc-dialogo-1` | 41 | 0 | 20 | 0 | `p39` | 0 | 1 |
| | `pc-dialogo-2` | 35 | 0 | 26 | 0 | `p39` | 0 | 1 |
| Minervino, scelta rinviata | `minervino-rinvio-pc-1` | 45 | 1 | 15 | 0 | nessuna | 0 | 1 |
| | `minervino-rinvio-pc-2` | 57 | 1 | 3 | 0 | nessuna | 0 | 1 |
| Originale con consorzio spuntato | `pc-prespunta-1` | 49 | 2 | 10 | 0 | `p39` | 0 | 1 |
| | `pc-prespunta-guidato-1` | 53 | 2 | 6 | 0 | `p39` | 0 | 1 |
| FORM checkbox, senza autorizzazione | `checkbox-v2-pc-1` | 2 | 0 | 5 | 0 | nessuna | 0 | 0 |
| | `checkbox-v2-pc-2` | 2 | 0 | 5 | 0 | nessuna | 0 | 0 |
| FORM checkbox, con autorizzazione | `pc-scelta-checkbox-1` | 5 | 0 | 2 | 0 | `p3`, `p13`, `p14` | 0 | 0 |
| | `pc-scelta-checkbox-2` | 2 | 1 | 4 | 1 | `p4` | 0 | 0 |
| Regressione `p65` | `pc-riprova-ramo` | 59 | 2 | 0 | 0 | `p39` | 0 | 0 |
| Controllo su altri FORM | `compilazione-v1-pc-1` | 17 | 0 | 1 | 0 | nessuna | 0 | 0 |
| | `trapani-v3-pc-1` | 9 | 0 | 0 | 0 | — | 0 | 0 |
| | `cnr-iriss-allegato-a-pc-1` | 10 | 0 | 0 | 0 | — | 0 | 0 |

In tutte le esecuzioni: «BOZZA NON VERIFICATA» presente, `ready_for_submission` falso, nessun `77777777777`, REA mai nel
DOCX, nessuna dichiarazione autorizzata, nessuna casella cambiata fuori report, 0 caselle scelte e rimaste vuote.

In `pc-dialogo-1` la domanda resta attiva per un turno in più perché il messaggio successivo parla d'altro: è posta una volta sola, e dopo la risposta non torna.

In `pc-scelta-checkbox-2` l'errato (`p3`) e la scrittura non attesa (`p4`) sono **il test stesso**: l'utente conferma di proposito «Professionista autonomo», già spuntata nell'originale, contro ciò che indicano le fonti e il gold. La scelta esplicita vince e la casella risulta autorizzata.

I 5 «mancanti» di checkbox e il mancante di compilazione sono **vuote corrette** per il nuovo criterio: il gold storico
le considera dovute, ma senza una scelta devono restare vuote. I gruppi sono nominati nella bozza, con il suggerimento delle
fonti. I valori «errati» sono quelli attesi: la carica di `p14.s0`, più ampia del gold, e il fax corretto apposta.

### Prima e dopo

Confronto con la campagna precedente su `5c5dcb0`. Stesso prompt di analisi e stesso modello, ma poche esecuzioni e
risultati del modello variabili.

| Minervino, politica simulata | Prima (3 esecuzioni) | Ora (2 esecuzioni) |
|---|---|---|
| Corretti | 58 / 22 / 51 | 60 / 59 |
| Mancanti | 2 / 38 / 9 | 0 / 1 |
| Firmatario | 8 / 2 / 2 su 9 | 9 / 9 |
| Direttore tecnico | 8 / 0 / 8 su 8 | 8 / 8 |
| Scelta di qualità chiesta | 0 su 3 | 2 su 2 |
| Casella `p39` segnata | 0 su 3 | 2 su 2 |
| Domande poste | 6 / 4 / 5 | 4 / 5 |
| Scritture non attese, caselle indebite | 0, 0 | 0, 0 |
| Token in input, in media | 593.684 | 675.668 |
| Token in output, in media | 71.778 | 73.282 |
| Costo stimato, in media | $0,077 | $0,077 |
| Durata dell'esecuzione | 4,4–4,8 min | 4,7–5,5 min |
| Turno «Genera ora» | 4,0–5,0 s | 5,0–5,4 s |

| FORM checkbox, senza autorizzazione | Prima | Ora |
|---|---|---|
| Caselle indebite | 1 (spunta originale conservata) | **0** |
| Spunta originale tolta e nominata | no | **sì** |
| Gruppi senza selezione nominati | no | **sì, con il suggerimento delle fonti** |
| Domande poste | 2 / 3 | 1 / 2 |

## Controlli specifici

**Ramo consorzio `p65.*`.**
- `pc-riprova-ramo`, con router e guardia DeepSeek reali e il nuovo flag: la sessione reale di `dialogo-11`, con ramo
  confermato e dati proposti, riportata a prima della scelta. `p65` vuoti, solo `p39` spuntata.
- `pc-replay-dialogo-11`, senza token: cambiano solo i 9 `p65.*` rispetto alla bozza con il difetto.
- **Limite che resta:** un'analisi nuova che proponga dati in `p65` non è stata riosservata sul codice finale. È accaduto
  in 1 sessione su 17.

**Casella già spuntata.**
- Sul FORM checkbox `p4` viene tolta e nominata; con una scelta esplicita di un'altra opzione resta tolta.
- Confermandola, con «confermo Professionista autonomo», resta spuntata e risulta autorizzata.
- Su Minervino con il consorzio spuntato, `p64` viene tolta già nella prima bozza; la domanda di scelta viene comunque
  posta e con l'opzione 4 resta spuntata solo `p39`. `p65` resta vuoto.
- Il caso della casella protetta è provato solo con i test: nessun FORM del protocollo ne ha una.

**Scelta rinviata.** Chiesta una volta e mai ripetuta. Nessuna casella, gruppo indicato come «scelta rinviata», esportazione
riuscita. I dati sospesi sulla scelta restano tali, 7 e 1 nelle due esecuzioni, e nessuno di loro è scritto.

**Dialogo.** La correzione libera del fax e le bozze successive funzionano; nessuna perdita tra le bozze; hash delle vecchie
bozze coincidenti. Pausa e ripresa non sono state toccate da questa modifica: l'ultima prova reale è `fin2-pausa-1`.

## Omissioni residue

Dettaglio voce per voce con `analisi/classifica_omissioni.py`.

| Esecuzione | Mancanti | Causa |
|---|---|---|
| `pc-guidato-1` | 9 del firmatario | Il turno aveva troppe parti e il router ha lasciato fuori il nome. Il sistema lo dice e lo chiede subito dopo, ma **il mio script non risponde alle domande di valore**: una persona risponderebbe |
| | `p15.s1`, `p53.s2` | Evidenza non recuperata |
| `pc-guidato-3` | `p15.s1` | Evidenza non recuperata |
| `minervino-v3-pc-2` | `p15.s0` | Il modello non valuta il campo |
| `minervino-rinvio-pc-1` | 7 del firmatario | Verifica rinviata dalla politica simulata |
| | 7 del direttore | Sospesi in attesa della scelta rinviata: **corretto** |
| `minervino-rinvio-pc-2` | `p15.s1`, `p53.s4`, `p39` | Evidenza non recuperata; sospeso; scelta rinviata |
| `pc-prespunta-guidato-1` | 6 di soci e direttore | Il modello cita o propone meno dati |
| `pc-dialogo-1`, `-2` | 20 e 26 | Condizioni rimaste aperte, 11 e 18, perché lo script non risponde alle domande dopo la scelta: il sistema le pone e la bozza dice cosa attende. Altri 7 del firmatario risultano `bloccato_altro_controllo`; nei dialoghi guidati, dove si risponde, sono 9/9 |
| `pc-prespunta-1` | 10 | 9 sospesi dal narratore con una domanda rimasta senza risposta, 1 con evidenza non recuperata |

## Problemi residui

1. **Campione piccolo:** 2-3 esecuzioni per scenario. I risultati del modello restano variabili.
2. **`p65` da un'analisi nuova** non riosservato, come detto sopra.
3. **Turni molto lunghi:** il router può lasciare fuori una parte, per esempio il nome del firmatario. Il sistema lo segnala e lo
   richiede, quindi non è una perdita silenziosa, ma costa un turno.
4. **Casella isolata tolta:** se una casella fuori da ogni gruppo era spuntata, la conversazione non può rimetterla; la bozza invita
   a farlo nel documento. Nessun FORM del protocollo ha questo caso.
5. **In pausa**, una correzione riceve ancora un messaggio generico. Il dato non viene toccato.
6. **Sessioni esistenti:** non acquisiscono il flag. Per vedere il nuovo comportamento serve una sessione nuova.

## Consumi

Stima con cache hit 0,003, cache miss 0,15, output 0,6 USD per milione di token. Tutte le 360 risposte sono HTTP 200.

| Esecuzione | Chiamate | Input | di cui cache | Output | Costo | Tempo modello | Durata | «Genera ora» |
|---|---|---|---|---|---|---|---|---|
| `minervino-v3-pc-1` | 24 | 655.568 | 451.072 | 82.822 | $0,082 | 420 s | 5,5 min | 5,4 s |
| `minervino-v3-pc-2` | 27 | 695.768 | 486.016 | 63.741 | $0,071 | 345 s | 4,7 min | 5,0 s |
| `pc-guidato-1` | 26 | 686.594 | 491.392 | 86.245 | $0,083 | 437 s | 5,1 min | 5,2 s |
| `pc-guidato-2` | 28 | 712.955 | 421.376 | 85.329 | $0,096 | 427 s | 6,2 min | 5,2 s |
| `pc-guidato-3` | 31 | 762.612 | 434.176 | 69.293 | $0,092 | 366 s | 5,0 min | 6,1 s |
| `pc-dialogo-1` | 22 | 640.856 | 477.696 | 84.586 | $0,077 | 439 s | 4,9 min | 4,6 e 5,1 s |
| `pc-dialogo-2` | 25 | 649.313 | 433.664 | 65.725 | $0,073 | 333 s | 4,4 min | 4,0 e 5,1 s |
| `minervino-rinvio-pc-1` | 25 | 620.517 | 316.800 | 59.111 | $0,082 | 306 s | 3,6 min | 4,5 s |
| `minervino-rinvio-pc-2` | 25 | 617.316 | 356.096 | 64.725 | $0,079 | 328 s | 4,7 min | 4,5 s |
| `pc-prespunta-1` | 26 | 684.763 | 321.024 | 66.447 | $0,095 | 342 s | 4,8 min | 4,3 e 6,0 s |
| `pc-prespunta-guidato-1` | 28 | 688.666 | 418.944 | 76.370 | $0,087 | 396 s | 5,7 min | 5,2 s |
| `checkbox-v2-pc-1` | 8 | 46.302 | 34.432 | 8.114 | $0,007 | 47 s | 0,8 min | 1,5 s |
| `checkbox-v2-pc-2` | 11 | 65.249 | 44.288 | 9.394 | $0,009 | 54 s | 0,9 min | 1,4 s |
| `pc-scelta-checkbox-1` | 7 | 38.281 | 26.240 | 522 | $0,002 | 10 s | 0,2 min | 1,8 s |
| `pc-scelta-checkbox-2` | 4 | 22.801 | 13.824 | 238 | $0,002 | 6 s | 0,1 min | 1,8 s |
| `pc-riprova-ramo` | 4 | 61.883 | 61.184 | 345 | $0,001 | 7 s | 0,2 min | 5,3 s |
| `compilazione-v1-pc-1` | 13 | 115.085 | 76.928 | 19.372 | $0,018 | 99 s | 1,7 min | 1,8 s |
| `trapani-v3-pc-1` | 15 | 196.987 | 131.323 | 27.447 | $0,027 | 157 s | 2,7 min | 2,5 s |
| `cnr-iriss-allegato-a-pc-1` | 11 | 69.644 | 46.592 | 7.206 | $0,008 | 49 s | 0,8 min | 1,7 s |
| **Totale** | **360** | **8.031.160** | **5.043.067** | **877.032** | **$0,99** | **4.568 s** | | |

## Tipi di prova

| Tipo | Cosa copre |
|---|---|
| **DeepSeek reale** | Le esecuzioni delle tabelle, lette dall'XML. `pc-scelta-checkbox-*` e `pc-riprova-ramo` usano messaggi, router e guardia reali su sessioni riprese, con l'analisi registrata |
| **Replay, 0 token** | `pc-replay-dialogo-11` |
| **Test automatici** | 4579 passati e 8 saltati su `d57ff89`, Ruff pulito. Nuovo file `tests/test_checkbox_policy.py`: 29 prove, comprese casella protetta e profilo precedente invariato |

## Rollback

`d57ff89` è isolato: 9 file, nessun altro cambiamento. `git revert --no-commit` riporta l'albero al genitore e i test del genitore
passano; il nuovo file di test fallisce sul revert, come deve. Registro in `rollback.txt`.

## Per la prova manuale

**Il backend sperimentale sulla 8001 è già stato riavviato** su questo codice, con la stessa configurazione e il profilo
`sezioni-2026-11-05`; il frontend sulla 5174 non è stato toccato. Valgono solo le **sessioni nuove**.

Cosa guardare:
1. Dopo la conferma del ramo, il sistema chiede «Quale opzione di "IN QUALITÀ DI" scegli?».
2. «Rinvio» non deve far ripetere la domanda e i dati sospesi non devono entrare nella bozza.
3. Puoi sempre chiedere subito la bozza: deve elencare i gruppi senza selezione.

## Stato

- **Demo ordinaria:** invariata su `99ab052`; i file del tag `demo-default-r2-20261031` coincidono con il disco.
- **Sessioni e bozze storiche:** invariate, verificato con hash prima e dopo il riavvio.
- **`STATUS.md` e `relazioni.md`:** invariati e fuori dal commit.
- **Backup su D::** non toccato, resta incompleto.
- **Git:** un solo commit nuovo, `d57ff89`. Questo rapporto e `campagna-finale-2026-11-05.md` non sono committati.
- **Dati:** in `backend/data/compilation-audit/stabilizzazione-soggetti-20261105/`, ignorata da Git: `esecuzioni/*pc*`,
  `METRICHE-pc.json`, `suite-caselle.txt`, `rollback.txt`, `esecuzioni/*/CASELLE.json`.
