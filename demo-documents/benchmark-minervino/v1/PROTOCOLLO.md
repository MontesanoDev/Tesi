# Protocollo Minervino V1

Il riferimento è il contenuto del Word, con controllo distinto di dialogo,
provenienza e fedeltà. Il gold è fissato prima di nuove esecuzioni. Il congelamento
non è una misura di qualità del sistema e non attiva chiamate provider.

## Ambiente e input

Usare DB, storage e KB temporanei con MAPI_DB_PATH, MAPI_STORAGE_PATH e
MAPI_KNOWLEDGE_PATH separati dall'istanza corrente. FTS5 appartiene al DB
isolato; per Qdrant usare un indice locale derivato dal DB o una collezione
dedicata verificata. Non importare sessioni, bozze o gold nell'indice.

Importare il solo modulo originale come FORM e i cinque documenti di
sources.json nei rispettivi scope/categorie, conservando originali e hash.
I metadati di identità non sostituiscono l'evidenza del soggetto nel testo.
Confrontare testo estratto e ricomposizione dei frammenti con gli originali,
registrando eventuali differenze. La frammentazione è una variabile tecnica:
registrarla, senza cambiare contenuti o attese.

Fissare commit effettivo, dipendenze bloccate, versioni dei parser, provider,
modello, parametri, thinking, budget, timeout, prompt/schema e versione del
renderer prima della serie. Nessun segreto viene incluso negli artefatti.
Il nuovo ambiente operativo non è creato dal solo pacchetto della fixture.

## Dialogo e checkpoint

1. T0: inviare soltanto la richiesta iniziale con il modulo selezionato e le
   fonti consentite. Acquisire proposte, rifiuti e stato prima delle risposte.
2. Alle domande rispondere solo per argomento come nel copione. Ordine libero;
   nessun suggerimento spontaneo su dati o scelte che il sistema ha saltato.
   Registrare risposte di chiarimento aggiuntive, ripetizioni e correzioni.
3. T1: acquisire lo stato dopo le risposte effettive. Nel confronto indicare
   quali dei quattro argomenti sono stati chiesti e quali restano mancanti.
4. T2: chiedere esplicitamente l'export, anche parziale, col testo del copione.
   Nessuna firma o allegato viene generato. Se fallisce, conservare il fallimento;
   non ritentare fino a ottenere un risultato più favorevole.

Per la prima baseline integrata usare tre esecuzioni indipendenti con identici
materiali e configurazione, sessioni nuove e tutte le prove conservate. Un primo
run singolo è esplorativo, non una stima della variabilità. Confrontare le
architetture con lo stesso numero di run e input disponibili ai checkpoint.
Non aggiungere indicazioni di scenario ai prompt per recuperare omissioni.

## Misure da separare

| Misura | Denominatore e criterio |
|---|---|
| Copertura SOURCE testuale | 60 occorrenze: valore corretto, soggetto/ruolo, fonte pertinente e destinazione corretta |
| Copertura USER testuale | Quattro testi: correttezza dopo la risposta, assenza di anticipazioni prima |
| Preferenze | Sei selezioni e 61 alternative vuote; confrontare anche il gruppo completo e massimo sei |
| Controlli nativi | Tre selezionati e dieci non selezionati, con stato OOXML e simbolo coerenti |
| Vuoti testuali | 123 vuoti corretti: 120 rami non applicabili, due continuazioni inutilizzate e una firma manuale |
| Dialogo | Quattro argomenti necessari coperti, ripetizioni, risposte ignorate e decisioni anticipate; nessun numero di turni imposto |
| Provenienza | Quote valide e sufficienti anche per identità e ruolo; scelta USER distinta dai fatti e dagli effetti di deselezione |
| Scrittura e layout | Prestampati, quattro tabelle, 130 paragrafi corpo, controlli, numerazione, posizione dei valori e blocco firma |
| Tempo e risorse | Chiamate, errori, tempo totale e per fase, token effettivi; costo solo con criterio dichiarato |

Pubblicare separatamente proposta grezza, risultato dopo i validator, stato
persistito e contenuto effettivamente scritto. Un RESOLVED o una citazione
formalmente valida non dimostrano correttezza semantica. Non aumentare lo
score SOURCE promuovendo automaticamente le proposte.

Gli errori che richiedono evidenza individuale comprendono attribuzione a
persona sbagliata, uso di cariche storiche al 15 ottobre, REA scambiato per
Registro Imprese, preferenze o attestazioni inventate, valori nei rami esclusi,
firme simulate, perdita di etichette e spiegazioni scritte nei campi.

Accettare equivalenze dichiarate di spazi, titoli personali, date e provincia;
confrontare i testi dei professionisti anche per nomi e assegnazioni, senza
imporre punteggiatura identica. Nessuna tolleranza su identità, ruolo, numeri
o significato delle decisioni. Gli identificativi demo vengono trasferiti
letteralmente; checksum e ammissibilità non sono nello score di questo caso.

## Criterio per valutare la nuova architettura

L'obiettivo è coprire tutte le 60 occorrenze SOURCE, ottenere le decisioni
USER mancanti, esportare le 64 destinazioni testuali e le selezioni attese,
conservando tutti i vuoti corretti. Gli errori critici sopra elencati devono
essere zero. Riportare ogni scostamento, anche quando il totale migliora.

Le prove sul layer JSON, documenti interi o file inviati al provider devono
mantenere identici contenuti autorizzati e disponibilità delle risposte;
registrare ciò che il provider ha effettivamente ricevuto. Gold e annotazioni
non entrano in nessuna variante. Le modalità API restano una proposta da
validare, non una scelta implementata da questo congelamento.

Salvare per ogni run input/request/schema, output e validazioni reali, dialogo,
stato, Word/report e rendering con versione, hash e tempi. Non mescolare test
con provider simulati e qualità delle risposte reali. Affiancare occasionalmente
un bando sorteggiato separato, registrando pool/estrazione ed esiti; senza gold
non dichiararne accuratezza percentuale.
