# Consenso alla bozza: loop rimosso — 12 ottobre 2026

## Causa verificata prima della modifica

La sessione `fe785b8bf9d04341be72dd5e96e0353b` del progetto `prova`, versione 6,
aveva una domanda di generazione attiva. Nei turni 181/182, «si» e «siii»
arrivavano già al comando di generazione: il backend salvava invece una
risposta `clarify`, «Non ho ancora valori utilizzabili per la bozza…».

Il precedente «senti lascia in bianco» aveva rinviato due condizioni USER,
senza confermarle. Tutte le 13 proposte scrivibili dipendevano da quelle
condizioni: `export_selection` restituiva quindi zero valori. Il controllo
del servizio e `_selected` vietavano una selezione vuota, mentre il dialogo
proponeva comunque una bozza «con i dati disponibili».

`compilationReplyParagraphs` ignorava inoltre la risposta `clarify` del backend
per una sessione globale in REVIEW: mostrava nuovamente `dialogue.message`.
Il risultato visibile era la stessa domanda dopo ogni consenso. Non era un
errore di riconoscimento del sì. Acquisizione read-only in
`diagnosis/live-observation.json` nel bundle; raw del planner originale non
disponibile, nessuna nuova chiamata per attribuirgli retroattivamente un output.

## Correzione congelata in fb30ff5

- La UI mostra la risposta `clarify` effettiva, anche se esiste un riepilogo.
- La proposta di generazione calcola quanti valori possono davvero essere
  esportati, riusando la selezione autorizzata. Con zero valori propone una
  **copia senza valori inseriti**, non una compilazione riuscita.
- `GlobalDraftRequest.allow_empty` è false di default. Una selezione vuota
  richiede `allow_empty=true`, `allow_unresolved=true` e una `user_quote`
  non vuota. In chat il caso è consentito solo al checkpoint di generazione
  valido, fuori da pausa/errori, dopo una decisione semantica del planner.
- Il consenso alla copia non conferma condizioni, non scrive valori USER,
  non rimuove rinvii e non cambia le prove SOURCE. Gate, CAS, isolamento,
  rivalidazione delle fonti e renderer sono conservati.
- Il report registra il consenso, zero scritture e un avviso esplicito quando
  la copia non contiene valori inseriti. L'originale è sempre la base.

Nessuna keyword aggiunta per «si», «siii», aziende, moduli o candidate.
RAG, parser, renderer e motore di analisi globale invariati. Nessuna migrazione.

## Prova reale DeepSeek

Codice applicativo invariato durante l'intera serie. Provider reale
`deepseek-flash`, richieste alla API FastAPI tramite ASGI, SQLite/storage
privati. Ogni caso parte da una copia indipendente dello stesso snapshot.

Questa è una regressione del checkpoint reale: **nessuna nuova analisi
globale** e nessun nuovo benchmark di copertura. Per gli ultimi due casi
il dialogo iniziale archiviato è stato ripristinato soltanto nella fixture
privata, con la cronologia coerente precedente al rinvio. Audit, fonti e
originale restano quelli della sessione osservata, senza inventare proposte.

| Caso | Messaggi USER | Risultato | Valori scritti | Tempo API complessivo |
|---|---|---|---:|---:|
| Checkpoint già rinviato | «si» | GENERATED, copia senza valori | 0 | 2,22 s |
| Stesso checkpoint, copia indipendente | «siii» | GENERATED, copia senza valori | 0 | 2,18 s |
| Dialogo iniziale archiviato | «senti lascia in bianco» → nuova proposta esplicita → «si» | GENERATED, rinvii conservati | 0 | 5,17 s |
| Dialogo iniziale archiviato | «Confermo entrambe le condizioni indicate.» → «si» | GENERATED, bozza parziale SOURCE | 13 | 5,03 s |

Sono **6 chiamate di routing +2 sintesi**, **29.205 token**, zero retry
automatici, zero valori fattuali forniti manualmente. La conferma dell'ultimo
caso riguarda solo le due condizioni poste, con provenance USER.
I tempi escludono la precedente analisi globale: non sono una misura della
latenza totale di una compilazione nuova né una riduzione causale dei suoi costi.
Prompt/schema e raw output del planner sono acquisiti per tutti i nuovi turni;
le due nuove sintesi conservano richiesta, raw, validazione e tempi.

## Materializzazione e provenienza

Tre copie senza valori: nessuna cella cambiata, nessun fatto USER inserito,
nessuna condizione trasformata in vera. Il renderer aggiunge il consueto
banner di bozza non verificata: il file generato non è byte-identico all'originale.

Nella bozza parziale, **13/13 valori scritti nelle celle fisiche previste**;
le altre celle restano invariate. Fra i valori mantenuti:

| Candidate | Dato | Valore | Evidenza SOURCE |
|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | generalita-mapi.md, chunk -43 |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | stesso chunk -43 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | stesso chunk -43 |
| t0.r9.c1 | Codice fiscale | IT01234567890 | stesso chunk -43 |
| t0.r10.c1 | Partita IVA | IT01234567890 | stesso chunk -43 |
| t26.r4.c1 | Numero albo | 8421 | generalita-mapi.md, chunk -45 |

Provenienza delle prove: `role=source`, `scope=global`, `category=company`;
valori didattici delle fonti demo. Conferme USER separate nel report.
Materializzazione corretta non certifica completezza o ogni associazione
semantica già presente nell'audit: non ricalcolata in questa prova.

Verificati in sola lettura: sessione live ancora alla stessa versione e con
identico `state_json`, originale live con hash invariato. Nessun confronto
byte-per-byte dell'intero DB live e nessuna modifica/correzione dei suoi dati.

## Controlli software realmente eseguiti

- Backend mirati: **71 passati /16,20 s**, con configurazioni FTS5/Qdrant.
- Backend completo: **1.894 passati /141,32 s**.
- Frontend completo: **102 passati /9,03 s**.
- Browser: **2 passati /7,8 s**, desktop/mobile, API simulate, normale export
  e ripresa dopo refresh. Il caso di risposta backend nascosta è coperto
  anche dal nuovo test frontend. Non presentati come test browser con DeepSeek.
- Ruff, lint, build e diff check passati.

Prime verifiche intermedie: sei fallimenti di asserzioni dovuti a banner del
renderer e scope troppo ampio della fixture; poi due per il nome `cell_id`
del report. Corrette le fixture/asserzioni, senza cambiare i gate per superarle.
Ruff ha segnalato una riga di 101 caratteri, poi spezzata senza cambi funzionali.
Il primo avvio dell'harness reale mancava di `PYTHONPATH=.`: errore prima di
qualsiasi chiamata/provider o snapshot, log conservato. Nessun caso reale
scartato o ripetuto per ottenere un risultato migliore.

## Artefatti e limiti

[Metriche](benchmarks/2026-10-12-blank-draft-consent.json),
[bundle grezzo senza database/chiavi](benchmarks/2026-10-12-blank-draft-consent-audit.tar.gz),
[verifiche finali](benchmarks/2026-10-12-blank-draft-consent-final-checks.json).
Originali, output DOCX, report, prompt/raw, script e controlli nel bundle.
Acquisizioni locali in `backend/data/compilation-audit/blank-consent-20261012/`.
Copie private DB/chiavi rimosse dopo verifica byte-per-byte del backup e scansione
della chiave reale nei grezzi: nessuna credenziale inclusa. Bundle: 142 file,
1.816.941 byte, SHA-256
`e5f574f4832997f6fb543164c0e75f0218c128eda7d5ce41c0b4829e2bd7da5b`.

Risolto il loop di consenso, comprese le sessioni globali già in attesa:
non occorre rifare l'analisi. Il rinvio di una condizione può ancora escludere
molti dati; non è stato corretto l'eccesso di conferme o l'applicabilità
semantica. Restano copertura incompleta, checkbox native non scritte e
correzione/riapertura libera dei punti. Nessuna promessa di modulo completo.

Per riprovare: riaprire la stessa chat e rispondere al consenso di generazione.
Con valori ammessi si scarica la bozza parziale; se nessun valore è ammesso,
si scarica una copia dichiarata senza valori inseriti. Le condizioni saltate
restano saltate. Il download del report tecnico rimane nella API.
