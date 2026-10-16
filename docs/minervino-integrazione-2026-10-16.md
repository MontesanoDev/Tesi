# Minervino dopo l'integrazione dei dati: diagnosi della compilazione

**16 ottobre 2026 — analisi offline di una prova già eseguita dall'utente.**

**L'integrazione è arrivata alla Company KB e all'LLM. La compilazione
insufficiente dipende anche da omissioni, controlli di attribuzione,
aggiornamento dopo le risposte USER e gestione delle domande.** Aggiungere
ancora dati non corregge da solo questi passaggi.

Sono stati letti [integrazione.md](<../nuovi dati/integrazione.md>) e il
[Word ricevuto](<../nuovi dati/domanda-iscrizione.compilato(5)(1).docx>),
identificati la sessione e gli artefatti corrispondenti nel backend.
Nessuna nuova chiamata generativa, scrittura nel DB o modifica del motore.

## 1. Identità della prova e verifiche

| Elemento | Valore |
|---|---|
| Codice esaminato | Baseline Git `4b7d828`, con modifiche documentali locali conservate |
| Progetto | `minervino-di-lecce-elenco-sia` |
| Sessione | `607eda672f0b4c46a175adaecc90dd71`, versione 10 |
| Analisi | `211598d4334c46a9a9c6d03f8b601a75` |
| Generazione | `a4231f7387ca407b90afd5d5a82b401b` |
| Data dell'analisi originale | 15 ottobre 2026 |
| Contratto / modello registrati | V12 / `deepseek-flash` |
| Originale | Lo stesso DOCX Minervino archiviato nella fixture |
| Originale SHA-256 | `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c` |
| Word ricevuto SHA-256 | `206c8584d4f78305f4fc4f5d3183ebb93f4fee37f6b7a292ec9c0937e83c0180` |

Il Word ricevuto coincide byte per byte con `bozza.docx` della generazione
indicata e con l'hash nel report. Il file integrativo corrisponde al documento
globale `integrazione-company.md`, ID 10. Il testo è identico alla copia
caricata; i byte differiscono per le terminazioni di riga CRLF/LF.

Ricostruendo l'input con il codice corrente si ottiene lo stesso input
archiviato; rivalidando la risposta originale si ottiene lo stesso audit.
Il corpus corrente coincide nei 56 record e in tutti i campi effettivamente
inviati. Il reload aggiunge metadati `relevance`, `excerpt` e
`document_metadata`: il confronto dei record completi deve considerarli,
senza scambiarli per differenze dei contenuti.

## 2. Dati disponibili e realmente inviati

| Documento | Frammenti nell'input |
|---|---:|
| Avviso della procedura | 34 |
| Generalità Mapi | 9 |
| Conoscenza generale | 4 |
| Visura simulata | 4 |
| Integrazione Company | 5 |
| **Totale** | **56** |

L'input dichiara `complete_small_corpus`, `partial=false`. In questa analisi
sono inviati tutti i frammenti autorizzati; non è una selezione top-k di
FTS5/Qdrant. Il caricamento dell'integrazione è precedente all'analisi.

I cinque frammenti nuovi, ID da -52 a -56, contengono tra l'altro:

- CCIAA, numero Registro Imprese, fax e componenti della sede;
- cessazione di Luca Ferri e subentro di Leonardo Montemurro;
- anagrafica di Leonardo, con nascita, residenza e CF dimostrativo;
- tre soci nominativi con qualifica, CF e dati dell'Ordine;
- dettagli aggiuntivi di Elisa Romano come direttore tecnico.

Quindi diversi campi vuoti hanno dati nel corpus effettivamente letto dal
modello. Non occorre ipotizzare che il file sia rimasto solo nella directory
dell'utente o che la ricerca non lo abbia selezionato.

La frammentazione rimane rilevante per le relazioni: il ruolo di una persona
e i suoi attributi possono trovarsi in frammenti o documenti differenti.
Avere inviato tutti i chunk non rende il validatore capace di collegarli.

## 3. Cosa produce il sistema

| Passaggio | Conteggio osservato |
|---|---:|
| Posizioni candidate nel catalogo | 267 |
| Proposte di valore grezze | 27 |
| Fatti condivisi | 21 |
| Proposte che superano il grounding locale | 21 |
| Proposte bloccate dall'ancoraggio FORM | 2 |
| Proposte personali sospese dall'attribuzione ruolo/dato | 4 |
| Richieste esplicite di chiarimento | 1 |
| Gruppi di checkbox proposti / validati | 1 / 0 |
| Assegnazioni checkbox proposte | 0 |
| Posizioni scritte nella bozza | 22 |
| Provenienza delle scritture | 21 SOURCE + 1 USER |
| Valori USER scritti | Solo il nome del firmatario |

Le 267 posizioni non sono il numero dei campi pertinenti per questa candidatura
e non costituiscono un denominatore di accuratezza.

L'audit iniziale distingue inoltre 140 vuoti con spiegazione FORM ancorata,
92 spiegazioni respinte e 7 omissioni senza spiegazione. Insieme a 21 proposte,
6 proposte bloccate/sospese e un chiarimento, queste categorie coprono le 267
posizioni. Le spiegazioni MODEL dei vuoti non dimostrano l'assenza di un fatto
nelle fonti e non sono automaticamente stato aggiornato dopo il dialogo.

Sono stati effettivamente utilizzati fax ed estremi camerali dell'integrazione.
Il ramo societario contiene anche `sede legale in Bari`, con via e civico
separati: in questa bozza la granularità di quel punto è migliore rispetto
alla precedente diagnosi. L'acquisizione dei dati funziona almeno in parte.

## 4. Problemi ricostruiti

### 4.1 Firmatario scelto, anagrafica non completata

All'avvio la mancata scelta del firmatario giustifica una domanda: la carica
societaria non sceglie da sola chi firma questa domanda. Il modello produce
un chiarimento soltanto per `p12.s0`, il nome.

Sette spazi relativi a nascita e residenza/CF vengono collocati in coverage
con motivo: dati non attribuibili senza scelta del firmatario. La carica in
`p14.s0` riceve un motivo analogo.

L'utente poi identifica Leonardo Montemurro e chiede esplicitamente di usare
la sua anagrafica presente nella Company KB. Dopo l'accettazione il sistema
conserva soltanto il nome come valore USER. Non crea proposte per i sette dati
anagrafici né per la carica, già disponibili nel fascicolo e nella risposta.

L'analisi globale resta una sola. `apply_replies` aggiorna gli slot attivi;
`refresh_dialogue` rigenera la presentazione, non riesegue la risoluzione
SOURCE sui requisiti diventati identificabili. Il passaggio mancante è il
raccordo fra scelta USER del soggetto e utilizzo dei suoi attributi documentati.

La domanda promette anche di poter completare anagrafica e ruolo, mentre
l'operazione disponibile nel turno aggiorna il solo campo del nome.

### 4.2 Prima risposta rifiutata per un valore ricomposto dal router

L'utente aveva già fornito nome e ruolo nella risposta alle tre domande.
Il router emette per lo slot 3:

> Leonardo Montemurro, rappresentante legale di Mapi Ingegneria S.r.l.

La quote USER contiene invece «Leonardo Montemurro, in qualità di
rappresentante legale di Mapi Ingegneria S.r.l.».

Il controllo `contains_span` restituisce false: il valore ricomposto non
compare come estratto contiguo nella quote. Il sistema registra le due
conferme ma non il nome e lo richiede nuovamente. Alla seconda risposta il
router estrae il solo «Leonardo Montemurro», che passa lo stesso controllo.

Il messaggio dell'utente era informativo. Il fallimento nasce dalla
trasformazione della risposta fatta dal router, insieme a una domanda che
chiedeva nome e qualifica ma aggiornava un solo spazio.

### 4.3 Quattro dati del direttore proposti ma bloccati

| Destinazione | Dato proposto | Fonte del fatto | Esito |
|---|---|---|---|
| `p52.s1` | CF di Elisa | Riga nominativa dei soci, chunk -54 | Sospeso |
| `p53.s1` | Sezione A | Riga esplicita di Elisa direttore, chunk -55 | Sospeso |
| `p53.s2` | Provincia dell'Ordine | Riga nominativa dei soci, chunk -54 | Sospeso |
| `p53.s3` | Data iscrizione | Descrizione tecnica, chunk -55 | Sospeso |

I quattro fatti superano il grounding locale. Il binding di ruolo `b_er`
cita invece l'intestazione «Ing. Elisa Romano - direttore tecnico» del vecchio
documento, chunk -45.

`_binding_check` richiede che attribuzione e prove del valore condividano
un chunk ammesso dal binding. I fatti nuovi usano -54/-55, quindi il binding
su -45 non li sostiene secondo quella regola e i valori non diventano
selezionabili.

L'errore registrato è lo stesso per tutti e quattro: «SOURCE non attribuisce
esplicitamente ruolo e soggetto nello stesso chunk del valore».

Il codice ammette inoltre solo alcune forme letterali per i record personali.
La nuova riga «Elisa Romano: direttore tecnico ...» non coincide con tutte
le forme riconosciute. Il collegamento tra identità, ruolo e attributi è un
limite di rappresentazione e validazione, non la semplice assenza dei dati.
Una correzione dovrà verificare tale relazione senza accettare omonimi o ruoli
diversi per sola somiglianza.

### 4.4 Soci presenti nelle fonti ma omessi

Il chunk -54 contiene i tre soci con nominativi, qualifiche e dati personali/
professionali. Il modulo chiede tali informazioni nel ramo societario.

Nessuna delle 24 destinazioni dei soci riceve una proposta grezza. Il modello
le raggruppa in coverage come ramo non confermato e dichiara che manca
l'attribuzione del ruolo «nella forma richiesta».

La condizione `c_soc` non include però i paragrafi 43–49 dei soci nel proprio
scope, benché comprenda i dati della società e del direttore. La spiegazione
di quel gruppo viene quindi respinta: manca una condizione locale unknown
sulle posizioni indicate.

Sono due difetti osservabili: omissione delle assegnazioni e scope incompleto
del ramo. Confermare `c_soc` durante la chat non ricostruisce quei valori.

L'output dimostra l'omissione, non prova che il modello sia tecnicamente
incapace di leggere la tabella. L'ipotesi di un effetto del contratto restrittivo
sulla selezione delle proposte richiederebbe un confronto controllato.

### 4.5 Comune e provincia iniziali proposti ma respinti

Bari e BA vengono proposti per `p15.s0` e `p15.s1`, con dati documentati.
Il testo «con sede in» termina nel paragrafo precedente; gli estratti locali
contengono marker e punteggiatura.

Entrambi falliscono con «Il solo marker non documenta la richiesta del campo».
Le due omissioni sono false negative dell'ancoraggio della destinazione,
riprodotte dalla rivalidazione offline. Gli stessi dati sono scritti altrove
nel ramo societario.

### 4.6 Checkbox: gruppo respinto e nessun valore proposto

Il modello individua un gruppo di sette opzioni «IN QUALITÀ DI», ma accorcia
alcune etichette eliminando riferimenti normativi e altre parole. Per quattro
opzioni l'etichetta non è più una sottostringa letterale della quote FORM.
Il gruppo viene respinto con «Etichetta opzione assente nell'estratto FORM».

Non esiste inoltre alcuna proposta booleana nelle assegnazioni. Il report
contiene `checkbox_values={}`; la conferma del ramo societario non viene
convertita in una selezione Word.

Sono passaggi distinti: interpretare la scelta, validare il gruppo, acquisire
la scelta USER e materializzarla. In questa prova rimane vuota anche la
casella della qualità appena confermata. Il codice esclude inoltre dalla coda
le scelte con minimo zero, ma qui il gruppo è già respinto a monte: correggere
la sola etichetta non dimostrerebbe ancora il funzionamento completo.

### 4.7 La coda si esaurisce mentre restano richieste aperte

Il pool riprodotto in memoria passa da **3 domande a 1**, dopo le due conferme,
e quindi a **0**, dopo il nome del firmatario.

`question_pool` considera condizioni collegate a campi utilizzabili, gruppi
validati e campi con disposition `missing/review` ed etichetta. Le ragioni
in coverage non diventano automaticamente domande o attività di risoluzione.

Pertanto i vuoti anagrafici, i soci e le scelte di categorie/fasce non
costituiscono una coda completa. Le 67 celle di preferenza delle tabelle restano
testuali e vuote, con motivazioni manual_input: quelle motivazioni non bastano
ad acquisire le decisioni necessarie.

L'export è stato richiesto e autorizzato: non è una generazione abusiva. Il
problema di copertura è che prima dell'export non viene portato avanti il lavoro
ancora necessario. La sintesi avvisa della copertura incompleta, ma l'avviso
non sostituisce tale lavoro.

## 5. Scrittura e limiti del controllo

Ricostruendo in memoria tutti i paragrafi dell'originale, sostituendo solo
le 22 destinazioni e i valori nel report, il testo coincide con il Word
ricevuto, escluso il banner iniziale della bozza. Le altre 15 parti ZIP del
DOCX sono identiche all'originale.

Questo controllo non mostra valori persi dal writer: quanto gli è stato
effettivamente passato viene materializzato. Restano problemi di presentazione,
come la giunzione senza spazio tra «professionale» e il nome dell'Ordine.
La paginazione non è stata verificata con Word/LibreOffice.

Firma, categorie non scelte e attestazioni non fornite non devono essere
inventate per aumentare le scritture. Gli identificativi della fixture sono
dimostrativi; questo audit non ne certifica la validità anagrafica/formale.

Non c'è ancora un gold umano completo: nessuna percentuale di accuratezza
è ricavata da questi conteggi. Non è dimostrato un miglioramento causale
rispetto alle vecchie analisi, che avevano fonti e risposte diverse.

## 6. Conseguenze per il gold e il benchmark

La KB già integrata permette di iniziare l'annotazione di molti più campi.
Non serve attribuire ogni vuoto alla mancanza di altri documenti.

Per ottenere il gold sono valide entrambe le modalità proposte dall'utente:
compilazione manuale dell'utente oppure bozza preparata separatamente dal
motore e poi revisionata dall'utente. Valori e motivi devono essere ricavati
da modulo, fonti e scenario, senza promuovere automaticamente questa bozza
o copiare i suoi errori.

Le stesse fonti fattuali possono essere usate nel backend isolato. Word gold,
mappa delle aspettative e risposte future restano materiale di valutazione.
Le scelte della pratica vengono fornite nel momento previsto dal protocollo.

Questa acquisizione va conservata come caso diagnostico prima di cambiamenti.
Il gold successivo e una nuova baseline congelata consentiranno il confronto;
l'output storico già esaminato non diventa retroattivamente un gold.

| Caso da rendere esplicito nel benchmark | Risultato atteso da revisionare |
|---|---|
| Scelta di Leonardo come firmatario | Uso dei suoi dati documentati dopo la scelta, con provenienza SOURCE distinta da USER |
| Risposta con nome e qualifica | Estrazione dei valori pertinenti senza costringere a ripetere la risposta |
| Soci del ramo societario | Inventario completo delle tre persone e delle 24 occorrenze previste |
| Dati aggiuntivi di Elisa | Verifica della relazione con la stessa persona fra prove distinte |
| Comune/provincia fra paragrafi | Collegamento locale verificabile con l'istruzione precedente |
| Casella della qualità di partecipazione | Scelta esplicita coerente con la conferma USER |
| Categorie/fasce e dichiarazioni | Domande pertinenti o rinvio esplicito, senza inferenze aziendali |
| Cambio di rappresentante nel tempo | Conservazione delle date e del precedente incarico; scelta del firmatario distinta |

Questi sono criteri da annotare, non nuove capacità implementate o test già
superati. Le ipotesi architetturali restano da discutere dopo il benchmark.

## 7. Acquisizioni e verifiche

- [Riepilogo delle misure e controlli](benchmarks/2026-10-16-minervino-integrazione.json).
- [Bundle completo](benchmarks/2026-10-16-minervino-integrazione-audit.tar.gz) e
  [SHA-256](benchmarks/2026-10-16-minervino-integrazione-audit.tar.gz.sha256).
- Grezzi locali: `backend/data/compilation-audit/minervino-integrazione-20261016T133808Z/`.
- Bundle di 616.261 byte, 92 file, SHA-256
  `f93a50f933609903a01f2d7e7f1a124d0b5e5a4a77a50136e879ca6a0bc21b1f`.

Conservati input, prompt/schema, risposta e metriche originali, audit,
tracce di routing e sintesi, stato/revisioni della sessione, dialogo, report
di generazione, originali ricevuti/caricati e codice applicativo esaminato.
Database e profili con credenziali non entrano nel bundle.

I dati di risorse sono **storici**, non consumi di questa diagnosi:
una chiamata di analisi, 166,10 secondi, 75.864 token di input,
38.692 di output inclusi 30.059 di reasoning, 114.556 totali.
La risposta termina con `finish_reason=stop`, non per un limite di output
segnalato. Sono conservate anche le successive tracce del dialogo.

Verificati equivalenza input/request, ricostruzione input, rivalidazione audit,
corpus, corrispondenza dei DOCX e ricostruzione del testo esportato. Il confronto
di stato/versione conferma la sessione invariata; i file osservati non cambiano.
Nessun test applicativo completo, rendering visuale, nuovo benchmark LLM,
migrazione o reindicizzazione.

Riferimenti nel codice: [ingestion](../backend/app/ingestion.py),
[contratto e grounding](../backend/app/compilation_global.py),
[record personali](../backend/app/compilation_role_records.py),
[dialogo e selezione per export](../backend/app/compilation_global_dialogue.py),
[gruppi di scelta](../backend/app/compilation_choices.py).
