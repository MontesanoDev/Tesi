# V13 S1 — recupero delle informazioni fattuali disponibili

**Intervento in corso: non è un rapporto conclusivo né un’adozione della V13.**
Richiesta: sole omissioni S1, almeno 100 casi mirati, regressione deterministica
e campagna di 45 nuove compilazioni reali dopo il congelamento del codice.

## Identità e preservazione

V12 sperimentale immutabile: [BASELINE-V12.md](../BASELINE-V12.md).
Lo stato effettivo di partenza comprende la successiva neutralizzazione del nome.
Snapshot `benchmark ufficiale/v13-s1-20261021-01/before/`, identificato da
`FROZEN-BEFORE.json`, con patch locali, 323 file e 13.204 file protetti.
DB live copiato solo nel percorso privato escluso dagli archivi; stato logico e
hash degli originali/storage nel grezzo `backend/data/compilation-audit/v13-s1-20261021-01/`.
Suite iniziale rieseguita: **3.180 PASS, 255,06 s**.

## Diagnosi causale prima dell’implementazione

`DIAGNOSI-17-PRIMA.json` conserva per ogni destinazione fisica il FORM originale,
proposta, fatto grounded, binding, prove SOURCE, chiavi dei record e condizioni.
Audit effettivi Minervino e CRAA riprodotti esattamente senza rete o SQLite.

| Destinazioni | Causa dimostrata | Meccanismo già disponibile |
|---|---|---|
| Minervino p12.s0–s3, p13.s0–s3, p14.s0 | Il binding cita «in qualità di» in p14, mentre la frase è alla fine di p13. Il riuso non riconosce la selezione USER con «scelto per questa domanda». | Gruppo FORM inline, profilo anagrafico con CF, scelta USER persistita, prove della carica. |
| Minervino p51.s0, p52.s0, p53.s0/s1/s2/s4 | Il valore è nella riga socio, il ruolo nel profilo DT; collegamento limitato a CF/alcuni dati d’iscrizione e alias incompleti. | Collegamento fra record per CF oppure stesso ordine e numero, controllo omonimi e proprietà tipizzate. |
| Minervino p15.s0 | Il gate di continuità guarda soltanto fact_id/GROUNDED_PROPOSAL dell’operatore, ignorando proposed_fact_id/proposal_grounding della proposta condizionata. | Relazione fisica adjacent_operator_location, identità societaria grounded, condizioni distinte. |
| CRAA p5.s0 | Nessuna proposta di valore; il nome è inline dentro una cella, fuori dalla grammatica tabella etichetta–valore del riuso. | Profilo SOURCE e scelta USER già presenti; marker fisico nel proprio paragrafo. |

I fatti sono disponibili nei 17 casi, ma questa disponibilità non conferma
condizioni o attestazioni USER. Il riferimento conserva anche una scelta
checkbox omessa e un campo fermo per budget: restano fuori dalla correzione S1.

## Soluzione in verifica

Le nuove sessioni persistono `backend_revision=13`; il contratto della proposta
LLM resta V12 per mantenere uguali prompt B0 e rappresentazione FORM. Le vecchie
sessioni senza quel profilo non vengono aggiornate implicitamente.

Il riuso esistente riconosce la selezione USER esplicita con qualificatore della
pratica e nomi inline nel proprio paragrafo/cella. Il recupero dei record richiede
una proprietà FORM locale tipizzata, ruolo letterale e identità per chiavi
personali/professionali non ambigue. Non trasferisce ruoli, poteri o dati societari
e non assembla valori da span diversi. Il valore mantiene la prova letterale;
le prove separate di ruolo/identità e il rifiuto MODEL originale restano nell’audit.
La continuità societaria distingue grounding da autorizzazione e conserva tutti
i vincoli applicabili. Nessun UNKNOWN viene promosso a TRUE per il recupero.

Il primo confronto sulle stesse risposte e ricevute rende **17/17 proposte
fattualmente validabili**, senza cambiare fatti/binding/condizioni originari;
le sette attribuzioni azienda→persona di Cesano restano respinte. Non è ancora
un conteggio di scritture autorizzate o un risultato della campagna reale.

## Verifica deterministica conclusa, campagna reale in corso

**3.364 test PASS in 281,92 s, Ruff PASS; 184 nuovi casi permanenti**, di cui
154 unitari e 30 API su FTS5/Qdrant. Positivi e avversariali comprendono i 17
controesempi, i sette rifiuti Cesano, omonimi, record contraddittori, proprietà e
ruoli distinti, selezioni USER chiuse/negate/ambigue, condizioni FALSE/UNKNOWN,
sessioni precedenti e riaperte, SOURCE modificate prima dell’export.

Log intermedi conservati: 130 PASS/quattro FAIL, poi 150/un FAIL di fixture,
prima suite completa 3.359 PASS/due FAIL. Quest’ultima ha trovato un nome sotto
«Se procuratore» recuperato dal nuovo riconoscimento inline e un errore su
catalogo incompleto: corretti prima del congelamento, aggiunti tre controesempi
condizionali. Il profilo legacy resta invariato.

69 export storici riprodotti con profilo legacy e 69 con V13: tutti identici,
valori, checkbox e posizioni conservati. 213 validator V2–V12: esiti esatti,
207 validati e sei rifiuti conservati. Sulle tre risposte della baseline le 17
proposte ora sono SOURCE-validabili, ma le vecchie ricevute di revisione e le
condizioni producono ancora gli stessi 54 testi/sei booleani. Non si inventano
nuove revisioni o autorizzazioni nei replay.

Congelati 120 hash applicativi e snapshot candidate-code/. PROTOCOLLO.json
preregistra tutti i 45 tentativi, SOURCE e FORM, scenari, policy USER e criteri.
Campagna avviata il 21 ottobre alle 16:04 UTC: sei contesti browser isolati,
una nuova globale per sessione, nessun mock/riuso/retry selettivo. Codice, prompt
B0 e parametri invariati durante le prove. Massimo quattro risposte USER contro
due della V12: differenza di protocollo esplicita, nessun confronto causale
basato soltanto sui nuovi conteggi. Richieste, risposte, token e tempi acquisiti.

I primi esiti mostrano anche bozze vuote, condizioni MODEL troppo generiche e
conferme non interpretate. La policy preregistrata rinvia contesti non
riconosciuti (per esempio «dell’impresa» o «di partecipare … come»); altre
risposte positive incontrano ambiguità nel dialogo. Questi esiti restano nel
campione, senza adattare la policy dopo le inferenze e senza attribuirli
automaticamente al recupero S1. La revisione documentale delle scritture,
confronti appaiati e controlli XML/PDF procedono sugli export ordinari.

Il rapporto conclusivo distinguerà recupero/validabilità, autorizzazione,
scritture effettive e omissioni residue, con distribuzioni complete e confronto
V12/V13 sulle stesse risposte oltre alle nuove generazioni indipendenti.
