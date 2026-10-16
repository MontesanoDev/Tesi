# Minervino: verifica del verdetto sulla revisione 1

**16 ottobre 2026 — controllo documentale, senza modificare o congelare il Word.**

Il verdetto è **parzialmente fondato**. Il ripristino dei contenuti mancanti è
documentato nei controlli della revisione 1; dei quattro rilievi, quello sulle
frasi esplicative è confermato, quello sulle assegnazioni è già parzialmente
risolto, quello sulla numerazione non trova riscontro nell'XML e quello sulla
firma a pagina 10 non è verificabile come paginazione Word in questo ambiente.
La fedeltà visuale complessiva al modello resta da controllare nell'editor di
riferimento: non è dimostrata né smentita da questa sola verifica.

## Materiali e metodo

- [Originale](../demo-documents/bandi/minervino-elenco-sia/originali/domanda-iscrizione.docx).
- [Gold revisione 1](<../nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>),
  SHA-256 `5bd34a43b22dff44d5a280b690f4187d345e6664619d42272bbe2c590b5c8d67`.
- [Scenario esistente](<../nuovi dati/SCENARIO_GOLD_MINERVINO.md>).
- [Controlli della revisione precedente](benchmarks/2026-10-16-minervino-gold-revision-1.json):
  52 occorrenze conservate e otto dati del direttore ripristinati, etichette
  originali ripristinate, quattro tabelle e 13 controlli nativi preservati.

Confrontati document.xml e definizioni di numerazione, paragrafi finali,
frasi nelle aree compilabili e tabella dello scenario. Eseguiti anche estrazione
e rendering DOCX con MuPDF/mutool 1.27.0. Microsoft Word e LibreOffice non sono
disponibili: il rendering alternativo non certifica l'impaginazione in Word.
Nessuna nuova consultazione della KB: il confronto dei dati con le fonti resta
quello della [revisione del gold](minervino-gold-review-2026-10-16.md).

## Riscontro dei quattro punti

| Rilievo | Evidenza | Valutazione |
|---|---|---|
| Ripristinare a), b), c), d) | I quattro titoli hanno, come nell'originale, numId 5, livello 0, formato lowerLetter, schema %1), partenza 1 e nessun override | Non risulta una numerazione da ripristinare nell'XML |
| Linea della firma isolata a pagina 10 | Nessun rendering Word disponibile. MuPDF produce 15 pagine per il gold e tiene dicitura e linea insieme nell'ultima pagina | Non confermato; richiede controllo nell'editor di riferimento |
| Formalizzare le assegnazioni dei professionisti | La sezione «Designazioni specifiche» dello scenario contiene già quattro assegnazioni nominative | Già fatto sul piano descrittivo; disponibilità iniziale o checkpoint USER ancora da definire |
| Rimuovere spiegazioni dalle aree compilabili | Due frasi autoriali occupano i paragrafi corpo 117 e 118, originariamente destinati alla compilazione | Confermato; opportuno spostarle nello scenario |

### Numerazione

Le quattro voci riguardano progettazione/direzione lavori, coordinamento della
sicurezza, collaudo e altri servizi tecnici. I prefissi sono numerazione
automatica Word: non devono necessariamente comparire nel testo estratto dai
nodi w:t. La loro assenza in un'estrazione testuale non prova che siano stati
eliminati. Non aggiungerei lettere manuali senza un difetto osservato in Word,
per evitare di duplicare i prefissi già definiti.

### Firma e paginazione

Nel gold la dicitura «Firma digitale» e la linea sono due paragrafi consecutivi,
indici corpo 128 e 129. Non c'è un keepNext esplicito sul primo né un salto
pagina esplicito sul secondo: una separazione in un altro renderer rimane
possibile. Queste proprietà da sole non dimostrano la pagina del distacco.

MuPDF reimpagina anche l'originale, in 16 pagine; il suo conteggio non è quello
del Word dell'utente. Nella [immagine dell'ultima pagina del gold](benchmarks/2026-10-16-minervino-verdetto-last-page-mupdf.png)
la dicitura e la linea sono insieme, con luogo/data e nota finale. Questo non
riproduce il difetto segnalato, ma non lo esclude in Microsoft Word. Se il
distacco è confermato lì, tenere uniti i paragrafi della firma è una correzione
mirata da verificare poi nel PDF esportato da quell'editor.

### Assegnazioni e note

Lo scenario già assegna a Elisa progettazione strutturale/direzione lavori,
a Luca opere stradali/collaudo statico, ad Andrea progettazione edilizia,
certificazione energetica/CSP-CSE e integrazione delle prestazioni specialistiche.
Sono scelte autoriali USER, distinte dalle prove di qualifiche e abilitazioni.
Il lavoro ancora necessario è stabilire quando il sistema le riceve, senza
caricare gold o scheda di valutazione nella KB.

Le due frasi nelle aree compilabili sono:

- «Nessun altro professionista previsto nella presente simulazione.»
- «(Dati e qualifiche dichiarati esclusivamente per il benchmark didattico.)»

Le sposterei nella scheda scenario, lasciando vuote le righe non utilizzate.
Il banner iniziale che identifica il documento come sintetico è distinto da
queste righe e non rientra automaticamente nella stessa correzione.

## Prima del congelamento

Condivisibile ripetere il controllo automatico e visuale dopo le correzioni
effettivamente necessarie, quindi calcolare l'hash del DOCX approvato. Il semplice
hash del candidato non equivale al congelamento. Resta richiesto l'OK dell'utente.

Non affermerei invece che bastino soltanto quelle quattro modifiche per rendere
pronto l'intero benchmark: scenario/checkpoint, mappa strutturata di valori e
vuoti, policy degli identificativi sintetici e perimetro degli allegati sono
ancora aperti nella scheda esistente. Il congelamento del Word e la preparazione
del pacchetto completo vanno registrati distintamente.

## Acquisizioni e limiti

[Controlli JSON](benchmarks/2026-10-16-minervino-verdetto.json),
[backup](benchmarks/2026-10-16-minervino-verdetto-audit.tar.gz) e
[checksum](benchmarks/2026-10-16-minervino-verdetto-audit.tar.gz.sha256).
Raw locali in backend/data/compilation-audit/minervino-verdetto-20261016T143707Z/.
Bundle di 11 file, 265.691 byte, SHA-256
`7909c9c5df4d3a82f8b117d9981a8c3bc28931ff6114b47a22208b6b69a9e890`.

Conservati copie dei documenti/scenario, estrazioni e log MuPDF, immagine finale,
controlli e manifest. Verificati hash degli input, manifest e link documentali.
Nessuna modifica a Word, scenario, codice applicativo, DB/KB o fixture; nessuna
chiamata provider, nuova compilazione o misura di accuratezza. Nessuna suite
applicativa necessaria. Controllo visuale limitato all'ultima pagina MuPDF:
non è una revisione visuale completa in Word. Nessun congelamento, commit o push.
