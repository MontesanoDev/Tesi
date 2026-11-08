# P2 — Attribuzione di persone e ruoli a livello di record — 21 ottobre 2026

Esperimento offline sulla base tecnica V14, che non è una baseline: la V12 resta adottata.
Zero chiamate LLM; si usano solo risposte registrate (V13 in due coorti, verifica V14 e
baseline V12). Nessuna modifica applicativa, nessun commit o push.
Preregistrazione `PREREG-P2.md` (SHA256 `a73bffca…`, 20:44:06 UTC), scritta dopo lo studio
descrittivo dei rifiuti e prima della simulazione.

## Esito

**La regola non è stata implementata.** Ha superato la simulazione sulle risposte reali,
ma non la ricerca di controesempi: 5 negativi su 11 della seconda serie vengono recuperati.
La regola di decisione preregistrata richiede che tutti i negativi siano respinti, quindi
ci si ferma con questa diagnosi.

Gli stessi 5 controesempi superano anche il controllo di ruolo attuale (V12/V14), quando
il modello cita il paragrafo FORM del ruolo e il record SOURCE. P2 non crea queste falle,
ma le estenderebbe ai campi oggi respinti solo per la forma delle citazioni. Nelle risposte
registrate queste falle non hanno prodotto scritture.

## Regola provata (sintesi della preregistrazione)

Si applica solo a proposte personali già respinte per motivi di ruolo. Il ruolo richiesto
dal FORM deve comparire, a parole intere, nel contesto strutturale del campo. La proprietà
del campo deve essere tipizzata dall'etichetta locale o dall'intestazione di colonna. Nella
SOURCE serve un record certo, trovato dal backend, che attesti soggetto e ruolo.
Il valore deve stare nel record o essere collegato da chiavi forti (codice fiscale, oppure
ordine e numero di iscrizione). Si rifiuta se la stessa persona compare con un segno di
cessazione o se il record nomina un'azienda diversa da ogni soggetto aziendale grounded.
L'effetto è solo `REVIEW_REQUIRED`/`GROUNDED_PROPOSAL`: tutti gli altri gate restano.

## Scritture recuperabili (simulazione, non applicate)

| Misura | Esito |
|---|---|
| Recuperi | 47, tutti corretti rispetto a gold o riferimento congelato; 0 errati |
| Per documento | Minervino 43 (direttore tecnico Elisa Romano 30, socio Andrea Greco 8, socia Elisa Romano 5), Catanzaro 4 |
| Prove con recuperi | 9 risposte su 92 audit |
| Prova del valore | 16 dentro il record di ruolo, 31 collegate da chiavi forti |
| Copertura del bersaglio | 41 recuperi nelle coorti V13/V14 su 81 proposte corrette respinte per ruolo e non recuperate dalla V13 (Minervino 65, Catanzaro 13, Bella 3), più 6 negli audit baseline V12 |
| Proposte respinte per ruolo con valore diverso dal riferimento | 26 su 261, nessuna recuperata |

Su 52 proposte esaminate e non recuperate, i motivi sono:
- ruolo FORM assente dal contesto strutturale: 25;
- fatto non personale o non grounded: 6;
- cessazione: 5, blocchi corretti;
- proprietà non tipizzata o con nome diverso: 16 (`dataiscrizione`, `provinciaiscrizione`,
  `albo`, `nomecognome` o etichetta non riconosciuta).

I nomi di proprietà non sono stati adattati dopo i risultati. Sono escluse 7 risposte
senza audit. Una seconda esecuzione produce lo stesso file (SHA256 `2e46106d…`).

## Rifiuti corretti preservati (simulazione)

- I rifiuti azienda→persona di Cesano restano in tutte le 8 prove che li contengono.
- Luca Ferri non viene mai proposto come amministratore unico attuale: 5 blocchi dovuti
  alla cessazione documentata.
- Nessun recupero nelle regioni d'opzione V14: i requisiti di autorizzazione restano invariati.
- 0 regressioni: nessuna proposta già grounded cambia.

## Controesempi

SOURCE sintetiche costruite in modo diverso dalla KB demo, con le attese scritte nello
script prima di eseguirlo.

**Prima serie** (`counterexamples.py`, SHA256 `18f90f92…`): 15 casi su 15 conformi. Tre
positivi recuperati: record con intestazione, voce nominativa collegata a una tabella per
ordine e numero, riga di visura in maiuscolo. Dodici negativi respinti: ruolo solo in
prosa, omonimo con CF diverso, ruolo cessato in un'altra fonte, DT di un'azienda non
grounded, collegamento solo per nome, fatto aziendale, ruolo assente dal FORM, General KB,
nomina da confermare, ruoli FORM e SOURCE diversi, amministratore cessato.
Un caso era debole: la tabella senza titolo di ruolo veniva respinta per un motivo FORM.
È stato ripetuto nella seconda serie.

**Seconda serie** (`counterexamples_batch2.py`, SHA256 `53f1544e…`, eseguita alle
20:50:33 UTC): scritta dopo la prima per cercare attivamente falle.

| Controesempio | P2 | Gate attuale, modello che cita bene |
|---|---|---|
| FORM: «Direttore tecnico dell'impresa ausiliaria» con il DT dell'operatore | **recuperato** | accettato |
| FORM: «direttore tecnico della mandante» | **recuperato** | accettato |
| SOURCE: DT di un'altra azienda che è anch'essa un soggetto grounded | **recuperato** | accettato (recupero dal record del fatto) |
| Codice fiscale della società (11 cifre) nel record della persona, proposto come CF personale | **recuperato** | accettato |
| Carica lasciata con un verbo non in elenco («ha lasciato la carica»), in un'altra fonte | **recuperato** | accettato |
| Ruolo specializzato «vice direttore tecnico» | respinto | — |
| Ruolo specializzato «direttore tecnico di cantiere» | respinto | — |
| Termine nell'intestazione («fino al 2020») | respinto | — |
| Chiavi in conflitto (ordine e numero uguali, CF diverso) | respinto | — |
| Tabella senza titolo di ruolo, ruolo presente nel FORM | respinto | — |
| Visura con un ruolo diverso da quello dichiarato | respinto | — |
| Valore nel record di un'altra persona | respinto | — |
| Controllo positivo: amministratore ancora in carica | recuperato | — |

La colonna sul gate attuale viene da `baseline_gate_check.py`: per ogni caso fallito una
proposta V12 nel caso migliore, validata con `validate_global_proposal`. Lo script è
diagnostico ed è stato scritto dopo aver visto i fallimenti.

## Esposizione osservata

`exposure_check.py` esamina le 719 proposte personali accettate dal gate attuale nelle
risposte registrate. Risultati:
- 0 ruoli FORM appartenenti a un partner (ausiliaria, mandante, consorziata…);
- 0 codici fiscali numerici in fatti personali;
- 144 proposte su una persona con una riga di cessazione, tutte di Luca Ferri come
  **socio**. La cessazione riguarda la carica di amministratore e il gold prevede quei valori.

Le falle sono quindi strutturali, ma sui moduli studiati il modello non le ha mai
attivate. I moduli studiati non hanno sezioni per imprese partner, e la KB demo usa un
solo formato SOURCE. Un modulo nuovo con avvalimento o raggruppamento potrebbe attivarle.

## Limiti di generalizzazione

- Tutti i 47 recuperi vengono dalla stessa KB sintetica: tre persone, quattro formati di
  record. I due documenti sono diversi, la SOURCE no.
- Riconoscere la cessazione con un elenco di parole non sarà mai completo («ha lasciato»,
  «dal … al …», «rassegnate le dimissioni»…).
- L'ambito aziendale del ruolo non è verificabile in modo strutturale. Lato FORM, il ruolo
  può appartenere a un partner; lato SOURCE, «di X» è confrontato con qualunque soggetto
  aziendale grounded e non con l'operatore.
- Il formato dei valori personali non è controllato per proprietà: un CF di 11 cifre
  passa come CF personale.
- Il ruolo FORM deve essere letterale. Le proprietà riconosciute sono otto etichette.
  La voce in grassetto con negazione di Leonardo Montemurro non è un record.

## Opzioni (da decidere, nessuna implementata)

1. **Nessun P2 autonomo.** I campi restano respinti. La copertura di Minervino continua a
   dipendere da come il modello cita il ruolo (51/60 e 26/60 nella verifica V14).
2. **Conferma USER per persona e ruolo.** Quando la regola trova il record, il narratore
   chiede una sola conferma per persona e ruolo, per esempio «Elisa Romano è il direttore
   tecnico della vostra impresa?». La risposta copre proprio ciò che il backend non può
   verificare: impresa di appartenenza e carica attuale. Costo: una domanda in più per
   gruppo, non per campo. Tocca il dialogo, quindi va pianificata insieme a P3.
3. **Rafforzare il gate condiviso, poi una P2 v2.** Le protezioni valgono anche per il
   gate attuale:
   - formato dei codici personali per proprietà;
   - «ruolo di X» confrontato con l'operatore e non con qualunque azienda;
   - ruolo FORM qualificato da un partner trattato come non autonomo;
   - altre menzioni di persona e carica fuori dal record trattate come non autonome.

   Il comportamento della V12 cambierebbe, quindi servirebbero una nuova candidata, il
   replay di tutte le fixture e una terza serie di controesempi scritta prima dei risultati.

**Raccomandazione:** l'opzione 2. Il punto 1 dell'opzione 3 (formato dei codici
personali) è una protezione piccola e generale da valutare a parte. Le falle condivise
vanno comunque segnalate come limite noto alla revisione indipendente finale: sezioni di
imprese partner e cariche cessate vanno controllate esplicitamente.

## Materiali

Grezzo in `backend/data/compilation-audit/p2-record-binding-20261021-01/`:
- snapshot del working tree prima di P2;
- studio dei rifiuti (`out/role-rejections.json`);
- preregistrazione con hash e ora;
- regola candidata (`record_attribution.py`, copia di simulazione e non codice applicativo);
- simulazione (`out/simulation-p2.json`);
- due serie di controesempi;
- verifica sul gate attuale ed esposizione.

Backup in `docs/benchmarks/2026-10-21-p2-record-binding-*`. Il file
`out/counterexamples.json` coincide con `out/counterexamples-run1.json`, copia della prima
esecuzione conservata prima di rieseguire.
