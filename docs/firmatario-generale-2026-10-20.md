# Firmatario: scelta USER, identità SOURCE e destinazioni FORM — 20 ottobre 2026

Richiesta: recuperare le otto generalità di Trapani e verificare lo stesso
collegamento su Bella, Catanzaro e Minervino, mantenendo i controlli di attribuzione.
Intervento concluso. [Consegna](../benchmark%20ufficiale/firmatario-generale-20261020-01/README.md),
[DOCX finale reale](../benchmark%20ufficiale/firmatario-generale-20261020-02/e2e/trapani/bozza.docx),
[PDF finale](../benchmark%20ufficiale/firmatario-generale-20261020-02/e2e/trapani/bozza.pdf),
[controlli](benchmarks/2026-10-20-signatory-checks.json).

## Causa dimostrata

Il riuso precedente dipendeva da una sola sequenza completa: dieci campi in ordine
fisso, province separate, carica e operatore nello stesso periodo entro quattro
paragrafi. Trapani ha otto slot in ordine diverso e nessuna carica in quel periodo;
Bella quattro dati personali seguiti da quattro aziendali; Catanzaro righe con
etichette e valori in una tabella. Minervino corrispondeva alla sequenza completa.

La scelta esplicita nel messaggio iniziale era presente nell'input globale, ma
non creava un collegamento backend al profilo. Il riuso si attivava dopo un valore
sul campo del firmatario o alcune ricevute di condizione con frase nominativa
riconosciuta. Le generalità della persona non erano dimostrate dalla scelta:
la SOURCE distinta le documenta con nome, cognome e CF personale.

## Correzione circoscritta

Nuovo riconoscitore FORM del ruolo di sottoscrittore, separato dalla lettura SOURCE.
Parte da un ancoraggio esplicito e associa ogni proprietà per etichetta, attraverso
paragrafi di continuazione e tabelle contigue semplici. Conserva le prove fisiche.
Si ferma davanti a soggetti diversi, etichette ignote, contesti condizionati non
verificati, righe complesse o annidate, merge verticali, etichette compilabili e
blocchi multipli non disambiguati. Non usa etichette MODEL come prova, né nomi
di documenti, luoghi, aziende o ID specifici.

Una frase esplicita di scelta nel turno di avvio della stessa sessione viene
riconosciuta deterministicamente; non si interpreta ogni messaggio libero.
Servono provenienza USER, turno registrato, formula nominativa chiusa e unico
blocco compatibile. Ruolo aziendale, citazione di una persona, nome parziale,
alternative, rettifiche o revoche non autorizzano il collegamento. I turni di
altri progetti/sessioni restano esclusi dalla raccolta esistente. Le risposte
successive sul campo prevalgono sulla scelta iniziale. Nessuna deduzione di
partecipazione, attestazioni o poteri.

Il profilo SOURCE identifica univocamente la persona con nome, cognome e CF;
restano i controlli su omonimie, conflitti e persone diverse. Ogni valore o
componente deve comparire nel medesimo profilo e superare validatori esistenti
e veto di attribuzione SOURCE. La carica richiede la relazione documentata con
l'operatore; non costituisce una procura.

Da «Via Amedeo 24» si recuperano «Amedeo» dopo il prestampato «via/piazza» e
«24» dopo «n.». Non si trasforma un corso in una via, non si trasferiscono numeri
da altre proprietà. Comune e provincia si separano solo se il FORM presenta
destinazioni esplicite. SOURCE e scelta USER restano prove distinte e conservate.

Il percorso completo storico Minervino resta prioritario, conservando dati e
revisioni già verificati. Nelle nuove sessioni il contesto acquisito è persistito;
il riuso avviene prima della sintesi iniziale ed è rivalidato a ogni export.
Risposta MODEL e `audit.json` originario restano intatti; `effective-audit.json`
contiene il riuso e diventa il report effettivo. Nessuna promozione automatica
a RESOLVED o revisione inventata.

## Replay senza chiamate LLM

Dieci casi storici ricostruiti, controlli SOURCE letterali su tutti i valori
riusati ed export con le sole revisioni preesistenti. Nessun fingerprint alterato.
Tutti i dieci DOCX rimangono identici: Bella 4, Catanzaro 13, Cesano 0, Cesano
reale corretto 1, CRAA 9, Catanzaro reale 15, Minervino 55, Minervino V12 61,
Trapani 9 e ultimo Trapani reale 9.

Usando, in copie isolate, il contesto USER realmente presente nel rispettivo
input: otto nuove proposte SOURCE Trapani, quattro Bella, due Catanzaro; nove
anagrafiche/carica Minervino già recuperate e conservate. Sul Catanzaro reale
con nome USER acquisito si aggiunge una proposta di CF, senza cambiare nome
o carica USER. Cesano reale ottiene tre proposte personali con lo stesso
meccanismo, mantenendo respinte le attribuzioni societarie. Senza USER valido
non si attiva un nuovo riuso.

Questi recuperi non sono scritture nel vecchio dialogo: attendono nuova revisione.
La nuova prova UI deve misurare il passaggio effettivo fino al DOCX.

## Limiti separati

Catanzaro richiede data e luogo nella medesima cella, ma la KB li documenta su
righe separate. Il riconoscitore identifica la proprietà composta; i controlli
correnti richiedono un valore letterale in una prova. Non si presenta una
concatenazione come citazione, né si scrive una mezza risposta come completa.
Analogo limite per la residenza composta. La carica separata da istruzioni
sulla procura non viene collegata arbitrariamente all'operatore.

Il parser SOURCE mantiene il formato supportato dei profili e l'identificazione
forte: non è un lettore universale di KB. Il riconoscitore FORM non copre tabelle
complesse o etichette implicite. UNKNOWN e hold rimangono vincoli distinti.
Il consenso PEC deve restare UNKNOWN/SKIP nello scenario, anche col firmatario noto.

## Prima validazione e prima prova reale

48 nuovi casi permanenti: 42 locali e sei sessioni persistite, nei backend di
retrieval FTS5/Qdrant con trasporti simulati. Quattro FORM reali e SOURCE congelate
nelle fixture, più positivi/negativi su strutture distribuite, omonimie, conflitti,
persone diverse, dati societari, prove insufficienti, scelta incerta/revocata,
più blocchi, condizioni UNKNOWN e geometrie non supportate.

**324 test mirati PASS in 30,70 s; 2.841 backend PASS in 208,75 s; Ruff PASS.**
Conservati gli insuccessi di sviluppo: sei FAIL/15 PASS iniziali; quattro revoche
di scelta prima del guard; report iniziale da allineare all'audit effettivo;
cataloghi ridotti senza metadato di posizione nei test di finestre di revisione.
Una prima suite è stata interrotta durante lo sviluppo; un'altra ha prodotto
13 FAIL/2.827 PASS sul catalogo ridotto, poi corretta con un caso permanente.
Non sono nuove prove provider fallite né ripetizioni selettive di generazioni.
Frontend invariato, suite frontend non ripetuta; UI verificata dalla prova browser.

### Prima prova reale dalla chat

Nuova sessione `adea29341e9646afb75379928e0070c9`, progetto
`generalita-del-firmatario-trapani`, conversazione `conv-ef3288b0540b47f0`, FORM 191,
versione finale 10 GENERATED. Una sola globale nuova, nessun output riutilizzato,
nessuna correzione del codice o manipolazione dello stato durante la prova.

Stesso originale SHA `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`,
stessi 22 chunk SOURCE (18 Company e quattro General), snapshot SHA
`0982378194a2e3e769ed3e18dc8d92bf6c1c70f6c4e8b5aa9bbf6d236093ff0c`.
`deepseek-flash`, globale thinking enabled/low, temperatura 0,1, max_tokens 49.152;
thinking disabled per router/sintesi/guard come prima. Prompt globale invariato SHA
`978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`, fingerprint
provider `e72d3c7f663d3e1383b00b3884cb4501`. HEAD 99ab052 con working tree locale:
congelati tutti i 67 file applicativi prima della chiamata. Alias/fingerprint non
certificano pesi immutabili del provider.

L'input USER iniziale è identico alla precedente prova PEC: persona scelta
espressamente, partecipazione singola come società di ingegneria; dati personali
solo da SOURCE, attestazioni/preferenze/designazioni/date non inventate.

| Misura | Precedente chat PEC | Nuova chat |
|---|---:|---:|
| Record fatti MODEL | 9 | 18 |
| Proposte valore MODEL | 10 | 18 |
| Proposte grounded prima del riuso | 10 | 10 |
| Generalità recuperate con prova indipendente | 0 | 8 |
| Proposte grounded effettive | 10 | 18 |
| Proposte applicabili e revisionate al termine | 10 | 18 |
| Valori SOURCE effettivamente scritti | 9 | 17 |
| Dati personali scritti | 0 | 8 |
| Valori USER / checkbox aggiunte | 0 / 0 | 0 / 0 |
| Usi PEC procedurali non autorizzati | 0 | 0 |

**Precisazione sul percorso reale:** la nuova risposta MODEL propone già le otto
generalità, ma il suo binding è rifiutato. Cita il paragrafo societario con «Legale
rappresentante» usando required_role «rappresentante legale», non presente
letteralmente nell'ordine richiesto. Il motivo conservato è «Ruolo richiesto
assente nell'estratto FORM». Non è stato corretto/allentato questo controllo:
il binding MODEL resta REJECTED. Il riuso recupera invece gli stessi dati dalla
scelta USER del firmatario, dal profilo identificato col CF e dalle proprie
destinazioni personali FORM. Fonte, identità, ruolo e poteri restano distinti.

In una prima comunicazione di avanzamento i dieci esiti grounded iniziali erano
stati descritti come dieci proposte MODEL: l'audit completo li distingue e
corregge quel conteggio. La traccia completa di ogni campo è in
`TRACCIA-OTTO-GENERALITA.json`, con proposta originaria, rifiuto, nuova prova,
ricevuta USER, condizioni e valore realmente scritto.

La prima sintesi vede gli otto recuperi già costruiti dalla scelta esplicita
iniziale. Il MODEL introduce comunque una condizione UNKNOWN sul firmatario:
la chat richiede ancora la conferma nominativa, già indicata in avvio. È stata
risposta con la medesima decisione dello scenario; nessun UNKNOWN forzato a TRUE.
La risposta cambia la ricevuta del collegamento e comporta una nuova revisione
degli otto recuperi, conservando le altre revisioni. Restano zero hold al termine;
il consenso PEC indipendente è SKIP e blocca comunque quella scrittura.

Controprova offline aggiuntiva sulla **stessa nuova risposta**, con identiche
SOURCE e ricevute finali: il codice precedente esporta nove valori e nessuna
generalità; quello corretto riproduce esattamente il DOCX reale con 17 valori.
Zero chiamate, nessun cambio allo stato o ai fingerprint. Questo confronto
controllato distingue l'effetto del riuso dalla variabilità tra due generazioni.

### Contenuto, dialogo e costi

Le otto generalità sono nome, nascita luogo, data, CF personale, comune e
provincia di residenza, via e civico. Tutte citano le proprietà del profilo
personale; le nove scritture aziendali mantengono gli stessi valori della prova
precedente. La via personale non è la sede aziendale. Nessuna proprietà di
altri professionisti, iscrizione professionale o qualifica è attribuita al firmatario.

17 valori correttamente attribuiti e documentati;16 proprietà complete e un
indirizzo aziendale parziale, ancora privo del civico 172/C come prima. Il
riferimento autoriale ha 17 posizioni SOURCE e ora nessuna è vuota; ciò non è
una percentuale di accuratezza né rende completo l'indirizzo. Nel nuovo DOCX
non sono rilevate scritture non supportate o in sezioni inappropriate.

Due turni USER, otto domande complessive: consenso PEC, ramo societario, conferma
del firmatario; poi CIG, categoria MEPA e Albo Unico Regionale; infine numero
professionale del firmatario e luogo/data. Gli ultimi due restano senza risposta
quando viene richiesto l'export parziale; i tre dati procedurali sono rinviati.
La conferma del firmatario ripete la scelta iniziale e rimane un residuo del
contratto delle condizioni MODEL, non corretto durante il benchmark. Non sono
stati richiesti nuovamente i suoi dati anagrafici.

Nove chiamate=una globale, quattro router, tre sintesi e un guard; 115.350 token
(92.689 input + 22.661 output). Globale 41.923 input + 21.544 output, inclusi 16.447 reasoning;
86,72 s globale e 99,00 s HTTP sommati. Costo stimato 0,023323 USD sul tariffario
congelato, orari off-peak registrati, non fattura. Tutte HTTP 200/stop, nessun retry.
Il riuso delle otto generalità non richiede un'altra chiamata di compilazione.
Tempi/costi delle due generazioni reali sono osservazioni singole, non una stima
statistica dell'effetto sul modello. Durata browser include attese operative.

### Integrità, rendering e continuità

Verificati XML/CRC, posizioni, sei tabelle, stili, prestampato, controlli e
corrispondenza report/download. Solo `word/document.xml` cambia dall'originale;
le altre parti del pacchetto restano identiche. Diciassette valori nelle posizioni
attese, nessuna checkbox modificata, firma e data vuote. PDF cinque pagine,
nessuna parola oltre bordo; viste pagine 1/2/3/5: otto generalità leggibili a
pagina 1, nove valori aziendali a pagina 2, dichiarazione PEC vuota a pagina 3,
firma/data a pagina 5. La riga anagrafica occupa meno righe, senza sovrapposizioni.
Difetto cosmetico conservato: il prestampato «a» tocca lo slot nascita, rendendo
«aLecce»; writer e originale non sono stati modificati. Word desktop non provato.
Dieci GET ERR_ABORTED su mount/refresh, nessun errore di compilazione o download;
trace/video finalizzati.

Preservati 1.426 altri file esistenti, 29 sessioni live e 285 file storage; clone con
35 sessioni precedenti intatte e una nuova. 67 hash applicativi invariati durante
la prova. Nessuna migrazione/reindicizzazione o upgrade implicito degli originali.
Servizi isolati fermati. Grezzi in
`backend/data/compilation-audit/firmatario-generale-20261020-01/`; consegna con
backup separato di codice prima/dopo e risultati, senza DB o credenziali.

Tre file applicativi interessati: `compilation_source_reuse.py`,
`compilation_global_sessions.py` e nuovo `compilation_signatory_form.py`.
Nessun cambiamento a modello, prompt, FORM, API, struttura DB, parser FORMTEXT,
grounding fattuale, validatori dei binding, veto di attribuzione o writer.

### Ultima verifica delle proposte già grounded

Dopo la prima prova reale positiva sono stati aggiunti due controesempi
controllati: un fatto societario e un fatto di un'altra persona già grounded
in un campo personale distribuito su un paragrafo diverso. Non sono errori
osservati nel DOCX reale da17 valori. Il riuso precedente conservava i valori
che avevano già superato il grounding, senza applicare alla loro attribuzione
la scelta del firmatario. I due test sono inizialmente FAIL.

Aggiunto un veto nello stesso collegamento: dopo l'identificazione SOURCE
univoca, un fatto già grounded di società/altra persona non può compilare
quelle destinazioni personali. Il fatto e le citazioni restano documentati;
è respinta l'associazione, con `selected_subject_check` e motivazione.
Nessun nuovo accertamento di fatti o valore corretto dedotto dall'altro soggetto.
Un caso ulteriore controlla che i conteggi riflettano il rifiuto anche quando
non rimangono proposte riusate.

Con il codice completo il primo DOCX reale rimane identico, comprese le otto
generalità, così come tutti i replay. Per verificare la versione completa è
stata preregistrata una seconda sessione reale distinta in
`benchmark ufficiale/firmatario-generale-20261020-02/`: stessa fonte/scenario/
FORM/modello, prima prova17PASS integralmente conservata, nessuna correzione
durante ciascuna prova. Non è una ripetizione selettiva per migliorare l'output
LLM. L'esito finale è riportato di seguito.

Nessuna baseline generale adottata; nessun commit/push.

## Chiusura sulla versione completa

**51 nuovi casi permanenti: 45 locali e sei sessioni persistite FTS5/Qdrant.
327 test mirati PASS in 47,55 s; 2.844 backend PASS in 321,95 s; Ruff PASS.**
Gli ultimi tre casi verificano le due attribuzioni già grounded errate e i
conteggi dopo il rifiuto. Anche l'esito intermedio 2.843 PASS è conservato:
il caso sui conteggi è stato aggiunto successivamente. I test simulati verificano
il software; non sostituiscono le due valutazioni con provider reale.

### Seconda prova reale, dopo il veto di attribuzione

[Consegna finale](../benchmark%20ufficiale/firmatario-generale-20261020-02/README.md),
[metriche](../benchmark%20ufficiale/firmatario-generale-20261020-02/E2E-RISULTATO.json),
[traccia delle otto generalità](../benchmark%20ufficiale/firmatario-generale-20261020-02/TRACCIA-OTTO-GENERALITA.json).
Nuova sessione `b7d40c2449ad421580fe267547ac7964`, progetto
`generalita-firmatario-finale-trapani`, conversazione `conv-19decf96924b488f`,
FORM 196, versione finale 7 GENERATED. Stesso scenario iniziale, FORM, snapshot
SOURCE, modello, thinking, parametri e prompt della prima prova. Nessuna nuova
correzione durante il benchmark. Il motivo della seconda prova è conservato in
`backend/data/compilation-audit/firmatario-generale-20261020-02/MOTIVO-SECONDA-PROVA.md`:
verificare il codice completo dopo i controesempi, conservando il primo esito.

| Misura | Prima prova nuova | Prova finale |
|---|---:|---:|
| Fatti / proposte valore MODEL | 18 / 18 | 9 / 9 |
| Proposte grounded prima del riuso | 10 | 9 |
| Generalità recuperate con prove SOURCE locali | 8 | 8 |
| Proposte effettive grounded | 18 | 17 |
| Applicabili e revisionate al termine | 18 | 17 |
| SOURCE scritte, correttamente attribuite | 17 | 17 |
| Generalità effettivamente scritte | 8 | 8 |
| USER scritte / checkbox nuove | 0 / 0 | 0 / 0 |
| Scritture indebite rilevate | 0 | 0 |
| Chiamate provider / generazioni globali | 9 / 1 | 7 / 1 |
| Token totali | 115.350 | 95.023 |
| Secondi globale / somma HTTP | 86,72 / 99,00 | 70,76 / 79,89 |
| USD stimati, non fattura | 0,023323 | 0,019047 |

Questa volta il MODEL **omette** le otto generalità; il backend le propone tutte
dalle prove già disponibili. Sono otto verifiche locali in `source_reuse`,
distinte dai nove record fattuali globali; non otto nuove inferenze o decisioni
USER. La sintesi le revisiona e l'export ordinario le rivalida. Non è stata
eseguita una seconda chiamata globale per il loro recupero.

Nome, luogo e data di nascita, CF, Comune/provincia, via e civico sono nelle
otto destinazioni personali di pagina 1, separati dai nove dati aziendali di
pagina 2. Le differenze dal riferimento sono giustificate: data letterale
«14 novembre 1982» anziché «14/11/1982»; «Amedeo» dopo il prestampato via/piazza.
Ogni valore ha prova SOURCE personale conservata. Il civico **aziendale** 172/C
è ora presente perché la nuova risposta MODEL lo include: non lo attribuiamo
alla correzione del riuso. Tutte le 17 proprietà di questa prova sono complete.

Tre domande in un turno di risposte: ramo Società di Ingegneria, sottoscrittore,
luogo/data. Le prime due ricevono conferma esplicita prevista dallo scenario;
la terza è rinviata. La conferma del sottoscrittore ripete la selezione iniziale,
senza richiedere di nuovo le sue generalità. Non viene corretta in questa fase.
Restano UNKNOWN i quattro rami alternativi (professionista singolo, studio
associato, società di professionisti, altro prestatore); nessuna scrittura nei
loro blocchi. Zero hold finali. PEC dichiarativa non proposta dal MODEL e vuota,
quindi nessuna domanda di consenso necessaria in questa conversazione. Il caso
di proposta senza consenso resta coperto dalla prima prova e dai test permanenti.

Luogo/data, firma, CIG, iscrizioni Ordine/MEPA/Albo rimangono vuoti: in questa
conversazione non sono acquisiti o verificati. Il benchmark non attesta tutte
le dichiarazioni prestampate dell'originale e non rende la bozza pronta all'invio.
Nessun dato personale non documentato, ruolo o potere di altri professionisti
è stato scritto. Questa valutazione riguarda i valori realmente inseriti.

XML/CRC, 17 posizioni, sei tabelle, stili, prestampato, controlli, parti del
pacchetto e download verificati. Solo `word/document.xml` cambia. PDF cinque
pagine, 17 valori leggibili, nessuna parola oltre bordo; viste pagine 1/2/3/5.
PEC dichiarativa, data e firma sono vuote. Difetto cosmetico «aLecce» conservato;
Word desktop non provato. Trace/video e conversazione finalizzati.

Le due prove costano complessivamente 16 chiamate, 210.373 token e circa
0,042370 USD stimati. Due osservazioni non dimostrano un miglioramento statistico
di latenza, costo o qualità del modello. Il controfattuale offline sul medesimo
output della prima prova dimostra invece 9→17 scritture a parità di risposta,
SOURCE e ricevute, senza nuove chiamate o interventi sullo stato.

### Conservazione e riproducibilità finali

Tutti i dieci replay e il primo DOCX reale sono identici anche con il codice
finale. I nuovi recuperi Bella (4), Catanzaro (2) sono proposte verificate offline,
non nuove scritture approvate retroattivamente; Minervino V12 conserva 61/61.
I limiti sulle celle composte Catanzaro restano aperti e separati da questo PASS.

Preservati 1.426 altri file esistenti, 29 sessioni live e 285 file storage;
35 sessioni pregresse intatte nel primo clone e 36 nel secondo. Due nuove
sessioni isolate, nessuna migrazione, reindicizzazione o upgrade implicito.
67 hash applicativi finali verificati. Servizi isolati fermati; niente commit/push.

Grezzi delle due prove nelle directory `firmatario-generale-20261020-01` e `-02`
sotto `backend/data/compilation-audit/`. Il backup separato nella prima consegna
contiene entrambe le acquisizioni e il codice prima/dopo, escludendo DB, chiavi
e `.env`. [Manifesto e verifica](../benchmark%20ufficiale/firmatario-generale-20261020-01/VERIFICA-BACKUP.json)
riportano la ricostruzione in processi separati dal backup estratto, senza rete
o connessioni SQLite: 30 audit/DOCX storici, due nuovi reali e il controfattuale.

Esito circoscritto PASS per il recupero richiesto. Nessuna promessa di copertura
universale, nuova architettura o adozione della baseline. Arresto dopo consegna.
