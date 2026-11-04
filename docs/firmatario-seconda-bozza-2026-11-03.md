# Correzione firmatario e seconda bozza — verifica conclusa il 4 novembre 2026

I due blocchi funzionali sono risolti nei casi verificati: seconda bozza Minervino
con il nuovo nome e dati societari conservati; nome USER nel DOCX Labirinto.
**Candidato alla prova manuale finale, non ancora raccomandato per sostituire la
demo**: rimangono il messaggio contraddittorio Labirinto e i limiti SOURCE descritti
sotto. Nessuna promozione, merge o push.

Base `7e7383d12e567ba162716ef6715ad986c4326b29`, solo worktree sperimentale
`/home/montesano/tesi-narratore-chiarezza-20261031`; profilo
`sezioni-2026-10-30-r2`. Commit finale registrato in `commit.json` nell'audit.

## Cause effettive

**Cambio firmatario.** Il router acquisiva il nome come `VALUE`, senza una distinta
conferma d'identità: la guardia accettava il valore, ma la condizione rimaneva
aperta. La ricevuta non rendeva il campo utilizzabile; Gate e writer lo escludevano
correttamente. Inoltre l'invalidazione eliminava ogni ricevuta con destinazioni
intersecanti il blocco personale. Le conferme dell'operatore comprendono anche la
carica: venivano eliminate interamente, pur riguardando la medesima società.
Questo spiega la seconda bozza vuota e la perdita delle scritture indipendenti.

La prima correzione conservava le ricevute, ma la prova reale ha dimostrato un
ulteriore passaggio: ritirando la carica SOURCE scomparivano anche etichetta e
citazione FORM della destinazione. Il digest societario diventava invalido per
quel solo cambiamento. La guardia inoltre interpretava l'inventario MODEL di nove
campi come l'intera conferma richiesta, anche quando l'operazione riguardava solo
il nome disponibile. I rifiuti sono conservati; nessuno è stato convertito in assenso.

**Labirinto.** Il campo corretto era `t2.r0.c1`, la provenienza USER e la citazione
erano riconosciute, la guardia era positiva. Il validatore di completezza esigeva
per «Nome e cognome» un fatto SOURCE completo anche per un nome USER esplicito:
`USER_value_without_same_complete_SOURCE_fact`. Il rifiuto non dipendeva da
un'autorizzazione mancante per quella destinazione.

## Correzione

- Invalidazione basata sull'ambito proprio della condizione, distinto dalle sue
  destinazioni dipendenti. Ambiti mancanti o misti restano conservativi; identità,
  rappresentanza e autorizzazioni non si trasferiscono al nuovo firmatario.
- Conservazione dei soli metadati FORM già verificati quando un fatto personale
  viene ritirato. Nessun vecchio valore, evidenza SOURCE, potere o nuovo assenso.
  Se il fatto viene nuovamente derivato dalle SOURCE, il marcatore del ripiego viene
  tolto, mantenendo stabile la rivalidazione all'export. Un test riproduceva il 409
  causato da quel marcatore anche a dati invariati e ora passa.
- Router informato delle conferme d'identità collegate al nome: `VALUE` e
  `CONDITION_TRUE` restano proposte separate e controllate singolarmente. Il nome
  viene applicato prima della nuova conferma, indipendentemente dall'ordine LLM.
- Conferma richiesta sui dati disponibili; inventario MODEL completo conservato.
  La guardia vede esplicitamente le destinazioni dell'operazione. L'estensione ai
  dati SOURCE derivati richiede ancora una conferma verificata.
- Nome USER completo verificato sulla sua citazione letterale, con forma
  conservativa e almeno nome/cognome. Non diventa un fatto SOURCE. Gli altri dati
  composti mantengono i controlli precedenti; ambito, condizioni e poteri restano distinti.

Sei file applicativi modificati, un file di test. Nessuna modifica al compilatore
per sezioni, writer o criteri della guardia. Nessuna eccezione per nomi o FORM,
nessuna migrazione o riparazione retroattiva delle sessioni.

## Prova DeepSeek reale e DOCX

Modello `deepseek-flash`; API ASGI, router, guardia, persistenza ed export reali,
in copie separate di database/storage. Analisi iniziali registrate riutilizzate:
nessuna nuova analisi, nessun gold nei prompt. Messaggi USER sintetici di prova
esplicitamente conservati, non attribuiti all'utente reale.

| Passaggio | Scritture effettive | Esito |
|---|---:|---|
| Prima bozza Minervino, Leonardo | 37 | Checkpoint precedente riprodotto |
| Correzione libera in Mario, prima della conferma | 9 | Dati societari indipendenti; nome ancora sospeso |
| Conferma esplicita di Mario, seconda bozza | 10 | Mario + tutti i 9 dati indipendenti |
| Nuova scelta di Leonardo, prima dell'estensione | 10 | Nome + società; dati personali SOURCE ancora sospesi |
| Conferma esplicita dell'intero blocco personale | 18 | Tutti i 9 campi personali + 9 societari |
| Labirinto, prima/dopo il nome libero | 11 → 12 | Paolo Conti realmente nella cella `t2.r0.c1` |

Nella bozza Mario sono assenti nome, nascita, residenza, CF e carica di Leonardo:
gli otto dati personali dipendenti sono stati ritirati. Le due ricevute societarie
sono **identiche alle originali**, con digest valido per tutte le destinazioni.
Le altre 19 scritture iniziali appartengono al ramo subordinato alla qualità di
rappresentante: restano correttamente sospese, senza trasferire quella conferma.

Al ritorno a Leonardo il nome è USER, mentre gli otto dati personali sono nuove
derivazioni SOURCE: Lecce (LE), 14 novembre 1982, Bari (BA), Amedeo 24,
`MNTLRD82S14E506X`, «amministratore unico e rappresentante legale».
Le vecchie risposte anagrafiche USER restano archiviate e inattive. La data proviene
dalla SOURCE e ha una forma testuale diversa dal precedente `14/11/1982`.
La carica documentata non riattiva automaticamente il ramo di rappresentanza.

Negativo finale: «Mario Rossi oppure Elisa Romano; non ho ancora deciso» produce
un chiarimento senza cambiare valori o ricevute. Pausa/ripresa conserva la stessa
sessione. Messaggi originali conservati; una sola domanda mostrata per volta.
Nel percorso Minervino finale: due correzioni, due conferme esplicite aggiuntive,
un negativo; cinque presentazioni di domanda su due chiavi distinte, inclusa la
ripresentazione del ramo ancora aperto dopo la ripresa. Nessuna pretesa di riduzione
statistica delle domande sulla base di questo solo caso.

**11 DOCX controllati**, inclusi i tentativi intermedi: valori verificati nelle
posizioni XML effettive, zero checkbox selezionate, dicitura «BOZZA NON VERIFICATA»
presente. Prime bozze immutate byte per byte; originali copiati preservati.
Nessuna scrittura indebita nei campi verificati. I conteggi misurano gli scenari
parziali autorizzati, non la completezza dell'intero modulo.

## Test, confronto e costo

- Backend finale: **4.369 PASS, 8 SKIP**, 497,35 s; Ruff e diff PASS.
- Regressioni mirate: **40 PASS**, inclusi multivalore, apostrofi, nome semplice,
  correzioni, ambiguità, ordine delle risposte, domanda singola e bozze successive.
- Frontend: **188 PASS / 16 file**; build e lint conclusi. Il lint segnala due
  avvisi preesistenti sulle dipendenze `typedDraft`; nessuna modifica frontend.
- Quattro E2E desktop con **API simulate** PASS, compreso recupero dopo errore UI.
  Non sono prove browser con provider reale.
- Rollback in copia di `7e7383d`: **14 FAIL / 8 PASS** con i nuovi test;
  riapplicando il fix **22 PASS**. Hash della copia e del worktree verificati.
  Il test aggiunto per la stabilità del marcatore falliva nella versione intermedia.
- Graphify aggiornato soltanto via AST, senza chiamate LLM.

Confronto con `7e7383d`: la bozza con firmatario cambiato passava da 37 a 0
scritture; ora conserva 9 dati e arriva a 10 dopo la conferma. Labirinto restava a
11 con nome respinto, ora arriva a 12. Baseline registrata e riproduzioni offline,
non un A/B stocastico simultaneo con identiche risposte del provider.

| Acquisizione reale | Chiamate | Token totali | Tempo richieste modello |
|---|---:|---:|---:|
| Tentativo intermedio Minervino, esito insufficiente | 11 | 152.610 | 19,239 s |
| Minervino finale, incluso negativo | 14 | 202.934 | 21,935 s |
| Labirinto finale | 3 | 24.285 | 5,215 s |
| Totale | **28** | **379.829** | **46,389 s** |

28 risposte HTTP riuscite non significano 28 operazioni approvate: i rifiuti della
guardia sono inclusi. Totali: 376.349 token prompt, 3.480 output. Il tempo è quello
delle richieste AI; non comprende elaborazione locale ed esportazione. Le prime
suite intermedie da 4.365/4.368 PASS non sono usate come risultato del codice finale.

## Limiti e conservazione

Sul Labirinto il router ha proposto anche il nome in un ramo «studio associato»
non richiesto. La guardia lo ha respinto e nessun dato è finito in quel ramo, ma il
messaggio combina «dati acquisiti» con «nulla è stato scritto» riferito all'altro
campo. Il DOCX è corretto; la comunicazione richiede una verifica mirata prima di
presentare questa versione come nuova demo. Nessun altro fix introdotto.

Il riuso SOURCE rimane quello esistente: riconosce profili personali espliciti e
non ricompone automaticamente ogni anagrafica distribuita in documenti/tabelle.
Il tentativo intermedio con Elisa non ha recuperato il profilo completo; non è
stato ripetuto sul codice finale. Il recupero finale è provato per Mario → Leonardo,
non per un arbitrario terzo soggetto. Nessuna patch speculativa al retrieval.

Audit: `backend/data/compilation-audit/firmatario-seconda-bozza-20261103/`:
`diagnosis-before.json`, `refinement-initial-diff.json`, `calls/`,
`minervino-refined/`, `labirinto/`, `receipt-verification.json`, `final-summary.json`,
`integrity.json`, `rollback-final.json` e log delle suite. Prompt/schema, output,
stati, rifiuti, DOCX e limiti delle misure conservati, credenziali escluse.
Backup separato: `/home/montesano/tesi-backups/firmatario-seconda-bozza-20261103/`.

Database sperimentale originale, Git ordinario e tag demo invariati. Il database
ordinario live risulta cambiato tra acquisizione e ripresa: differenze per tabella
in `protected-comparison.json`; **non si certifica la sua identità totale**.
Le prove di questo intervento scrivono esclusivamente nelle copie `runtime/`;
nessun intervento sull'istanza ordinaria. Conservati anche i file preesistenti
modificati dall'utente, esclusi dal commit del fix.

Rollback applicativo: revert del solo commit che contiene questo rapporto;
base recuperabile `7e7383d`. La prova di rollback non modifica il worktree reale.
Vite temporaneo 5174 fermato dopo gli E2E, backend 8001 non avviato: l'istanza
manuale non viene dichiarata pronta. Lavoro fermato al rapporto, senza promozione.
