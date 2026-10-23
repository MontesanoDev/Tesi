# Baseline B0 Minervino — 16 ottobre 2026

Acquisite **tre analisi reali con DeepSeek e tre bozze Word**, conservando il
motore attuale. Nel Word arrivano rispettivamente **23, 17 e 22 valori conformi
sui 60 attesi dalle fonti**. Nessuna delle tre continuazioni chiede preferenze,
designazioni, attestazioni generali o luogo/data. È ora disponibile un riferimento
misurato per E1; la dimensione del JSON non è l'unica causa dei limiti osservati.

[Misure complete](benchmarks/2026-10-16-minervino-b0.json),
[bundle delle acquisizioni](benchmarks/2026-10-16-minervino-b0-audit.tar.gz),
[checksum](benchmarks/2026-10-16-minervino-b0-audit.tar.gz.sha256),
[verifiche finali](benchmarks/2026-10-16-minervino-b0-checks.json).
Raw: `backend/data/compilation-audit/b0-minervino-20261016T154354Z/`.

## Materiali e configurazione fissati

Codice applicativo **99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e**, corrispondente al
tag `baseline-minervino-v1-20261016`; nessuna modifica al motore durante le prove.
Fixture [Minervino V1](../demo-documents/benchmark-minervino/v1/README.md),
originale, cinque fonti, scenario e gold invariati. Controllati i 18 hash Minervino
e gli 11 della fixture Labirinto. Modulo backend 156, progetto
`minervino-di-lecce-elenco-sia`; 56 chunk SOURCE, 267 destinazioni.

Profilo `deepseek-flash`, provider DeepSeek, risposta dichiarante lo stesso modello.
L'analisi usa **thinking attivo**, come il servizio globale effettivo, benché la
preferenza del progetto sia disattivata. Routing e narrazione mantengono la
configurazione corrente. Il valore context_window=32768 è metadato del profilo:
non costituisce una misura del limite reale del provider, che ha accettato input
più lunghi. Nessun cambio di modello, prompt, schema o validatore fra i tre run.

Il [preflight](b0-preflight-2026-10-16.md) aveva misurato 240.276 caratteri JSON,
126.928 per FORM, 75.735 per SOURCE/metadati e 25.670 per il reading plan;
system prompt 24.675, totale messaggi 264.951. Il JSON era già senza indentazione:
E1 dovrà rimuovere ridondanze e dettagli superflui, non soltanto spazi.

## Perimetro effettivamente misurato

1. Tre esecuzioni sequenziali del runner globale esistente sul modulo completo,
   con provider reale e timeout 300 secondi per analisi. Nessun retry manuale,
   nessun risultato scartato o selezionato a posteriori.
2. Per ogni risposta reale, prosecuzione dei servizi applicativi su una copia
   SQLite/storage isolata. Routing iniziale, interpretazione delle risposte USER,
   narrazione ed export usano le funzioni e il provider reali. Prima di persistere
   l'analisi, uguaglianza esatta dell'input con quello acquisito e rivalidazione
   uguale all'audit originale. Nessuna seconda chiamata di analisi nascosta.
3. Risposte dei quattro argomenti congelati solo se chiesti. Ammessa soltanto la
   ripetizione delle due decisioni già nella richiesta iniziale: società di
   ingegneria e firmatario Leonardo Montemurro. Gold e copione completo non entrano
   nei prompt. Export esplicito con il testo congelato, anche per bozza parziale.
4. Confronto indipendente delle proposte e del Word con tutte le 267 destinazioni,
   seguito da controllo OOXML e rendering LibreOffice. Nessun uso del writer
   applicativo per decidere se il suo output sia corretto.

È una **misura dell'analisi e della sua continuazione a livello di servizi**.
Non è un percorso unico attraverso browser/endpoint HTTP: non misura upload,
ingestion, persistenza dei turni della route, frontend o tempo umano. L'analisi
reale è riutilizzata nella continuazione, con controlli espliciti; questo raccordo
è registrato in `integrated-*/analysis-replay.json`. Budget della continuazione:
40 chiamate provider per run, massimo quattro passi automatici per risposta;
comportamenti interni del router conservati. Nessun budget raggiunto.

## Qualità: proposta, validazione e Word sono misure distinte

Le 60 occorrenze SOURCE sono 19 dati iniziali del firmatario/operatore, nove
societari, 24 dei soci e otto del direttore. Si contano le occorrenze nei campi,
non soltanto i fatti unici. Sono ammesse le equivalenze già definite: spazi e
maiuscole, titoli opzionali, date equivalenti e provincia Bari/BA. Il gold non
viene adattato alle risposte.

| Run | Valori SOURCE proposti | Conformi al gold nella proposta | Conformi e grounding passato | Valori scritti totali | Conformi sui 60 target nel Word |
|---|---:|---:|---:|---:|---:|
| B0-01 | 23 | 22 | 21 | 24 | 23/60, 38,3% |
| B0-02 | 23 | 22 | 17 | 18 | 17/60, 28,3% |
| B0-03 | 50 | 49 | 21 | 23 | 22/60, 36,7% |

“Grounding passato” comprende proposte condizionali ancora `REVIEW_REQUIRED`:
non significa `RESOLVED` né accettazione semantica generale. Nell'ultimo dato
si valuta la conformità dei valori, conservando separatamente la provenienza
reale: nel Word i target corretti sono **21 SOURCE + 2 USER**, **15 SOURCE +
2 USER**, **21 SOURCE + 1 USER**. Le ripetizioni del nome/qualità del firmatario
possono colmare una destinazione autorialmente SOURCE tramite USER; non sono
un recupero riuscito dalla KB. Tutti i report conservano questa distinzione.

| Categoria nel Word | B0-01 | B0-02 | B0-03 |
|---|---:|---:|---:|
| Quattro testi USER della pratica conformi | 0/4 | 0/4 | 0/4 |
| Sei preferenze da selezionare | 0/6 | 0/6 | 0/6 |
| Tre checkbox native attese true | 0/3 | 0/3 | 0/3 |
| Testi da lasciare vuoti, incluso firma | 123/123 | 123/123 | 123/123 |
| Preferenze da lasciare non selezionate | 61/61 | 61/61 | 61/61 |
| Checkbox native attese false | 10/10 | 10/10 | 10/10 |

La conservazione dei vuoti evita scritture indebite, ma non dimostra che il
sistema abbia compreso l'inapplicabilità di tutti i rami. Non si pubblica un
unico punteggio su 267: i numerosi vuoti maschererebbero la scarsa copertura.
Le percentuali descrivono soltanto la conformità dei 60 target di questa fixture.

### Perdite osservabili e loro attribuzione

**Il modello omette dati disponibili.** I primi due run non propongono nessuna
delle 24 occorrenze dei soci, pur ricevendo gli stessi documenti e chunk del
terzo, che le propone tutte correttamente. L'estrazione/associazione non è
stabile. Questa variabilità non dimostra da sola che il JSON lungo ne sia la
causa: E1 serve proprio a verificarlo a parità delle altre componenti.

**Il validatore blocca proposte corrette.** Nel terzo run tutte le occorrenze
dei soci restano escluse per `Binding di ruolo rifiutato`. Il binding cita
“Soci della società” e le righe della tabella, con `source_role="socio"`.
Il controllo letterale richiede la stessa parola in ogni singola citazione:
non riconosce il plurale e la riga della persona non ripete il ruolo dell'intestazione.
Altri dati del direttore sono bloccati dal requisito di soggetto/ruolo nello
stesso chunk del valore. Nel run 3, 49 valori sono conformi nella proposta ma
soltanto 21 superano anche il grounding. Non tutti i rifiuti vanno eliminati:
il supporto documentale e l'attribuzione della persona devono restare verificabili.
Riferimenti: `compilation_global.py`, `_subject_bindings` e `_binding_check`.

**Le scelte iniziali si perdono prima dell'analisi.** La richiesta iniziale
contiene società, forma di partecipazione e firmatario, ma il JSON dell'analisi
ha `user_values: []`. `build_global_input` lo costruisce così; `_prepare` non
trasmette quelle decisioni del messaggio iniziale. Tutti i dialoghi chiedono
nuovamente informazioni già comunicate. Per questo le omissioni anagrafiche
non vanno attribuite tutte alla sola capacità del modello di leggere le fonti.

**Il dialogo non copre le richieste del modulo.** Nel run 1 bastano due risposte
che ripetono le decisioni iniziali per arrivare all'offerta di bozza parziale;
nel run 3 una. Nessuno dei quattro argomenti USER del copione viene chiesto.
Nel run 2, dopo tre risposte ammesse, rimane solo la riconferma del direttore
Elisa Romano: è un fatto SOURCE, senza risposta USER prevista dal copione.
Non lo si inventa come nuova attestazione dell'utente; si registra lo stop e si
richiede l'export parziale consentito. Non è un completamento autonomo del
dialogo. La selezione delle domande deriva da un pool che non trasforma ogni
vuoto spiegato in `coverage` in una domanda attiva.

**La granularità della destinazione resta un problema.** Tutti i run scrivono
l'indirizzo societario completo in `p41.s1`, dove il gold prevede il comune
“Bari”, seguito dai campi separati provincia/via/civico. Il contenuto è nelle
fonti: non è un'invenzione. È un difetto di collocazione/granularità e rimane
non conforme, senza introdurre a posteriori un'equivalenza favorevole al modello.

**Le checkbox non sono risolte.** Tutte le 13 rimangono fisicamente false,
compresa quella della partecipazione societaria già comunicata. Run 1 propone
un gruppo, poi respinto per etichetta opzione non presente nell'estratto FORM;
run 2 e 3 non propongono gruppi. Il fatto che il ramo societario sia compilato
non equivale alla corretta selezione del controllo nativo.

Queste evidenze separano disponibilità dei dati, proposta LLM, accettazione,
dialogo e materializzazione. Escludono la diagnosi “basta aggiungere dati alla KB”.

## Token e tempi reali

| Run | Input analisi | Output analisi, incluso reasoning | Reasoning analisi | Tempo analisi | Chiamate totali, inclusi dialogo/export | Token totali osservati |
|---|---:|---:|---:|---:|---:|---:|
| B0-01 | 75.864 | 33.962 | 26.284 | 146,73 s | 10 | 154.395 |
| B0-02 | 75.864 | 40.104 | 30.944 | 179,84 s | 13 | 174.773 |
| B0-03 | 75.864 | 46.156 | 32.497 | 183,85 s | 7 | 152.031 |

Totale **30 chiamate, 481.199 token**: 357.871 input, 123.328 output, di cui
89.725 reasoning. I token di reasoning sono già inclusi nell'output e non vanno
sommati una seconda volta. Analisi media 170,14 s. Somma dei tempi delle
operazioni provider circa 561,28 s; non è latenza end-to-end dell'interfaccia.
I percorsi hanno lunghezze diverse perché il dialogo evolve diversamente.

Tutte e tre le analisi hanno input e request identici. Il provider dichiara
**75.648 token input in cache e 216 non in cache per ciascuna analisi**:
sono prove con cache calda. Complessivamente 288.128 input cache-hit e 69.743
cache-miss. Non si stima un prezzo né un costo monetario; usage/cache sono
acquisiti, tariffa e addebito effettivo no. Il solo conteggio dei caratteri non
avrebbe mostrato i 33–46 mila token di output e l'ampio contributo del reasoning.

Nessun timeout, errore HTTP o risposta scartata in questi run. Le eventuali
chiamate aggiuntive dei servizi durante l'interpretazione USER sono comprese
nelle acquisizioni; non sono trattate come una sola chiamata logica gratuita.

## Word prodotti e verifica fisica

- [B0-01 Word](<../nuovi dati/domanda-iscrizione.B0-RUN-01.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.B0-RUN-01.pdf>).
- [B0-02 Word](<../nuovi dati/domanda-iscrizione.B0-RUN-02.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.B0-RUN-02.pdf>).
- [B0-03 Word](<../nuovi dati/domanda-iscrizione.B0-RUN-03.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.B0-RUN-03.pdf>).

Verificate tutte le 187 posizioni testuali, le 67 celle di preferenza e i
13 stati nativi contro il report effettivo. Le scritture del report sono
fisicamente nelle destinazioni dichiarate; gli altri placeholder restano
invariati. Cambia soltanto `word/document.xml`, altre 15 parti del DOCX identiche
all'originale. Testo prestampato preservato, salvo la prevista avvertenza di
bozza aggiunta all'inizio; nessuna spiegazione inserita nelle righe compilabili.
Tutti gli export sono parziali, `ready_for_submission=false`.

LibreOffice 26.2.6.3 produce dieci pagine per ogni bozza. Ispezione visiva delle
pagine 1, 3, 9, 10 per run 1 e 3; 1, 3, 10 per run 2. Il blocco firma finisce
su una pagina quasi vuota; nel run 2 anche luogo/data è nell'ultima pagina.
La scarsità del contenuto, l'indirizzo ripetuto e i vuoti dei soci sono visibili.
Il writer corrente parte dall'originale, non dal gold corretto: la buona
impaginazione del gold non si trasferisce automaticamente alle bozze.
PDF/testo/PNG/log conservati; warning liblangtag del runtime locale registrati.
Nessuna verifica con Microsoft Word né certificazione della paginazione.

## Integrità, acquisizioni e limiti della verifica

Il bundle conserva protocollo, codice applicativo e script diagnostici,
input/request/schema effettivi, risposte HTTP e LLM, audit, confronti gold,
revisioni/stati, domande/risposte, Word, rendering, tempi e usage. Non contiene
chiavi, `.env`, database o profili riservati. SQLite/storage operativi rimangono
in `.tools/b0-runtime-20261016T154354Z/`, separati dall'archivio pubblicabile.
La selezione delle risposte è supervisionata sul copione, non generata dal gold.

Confronto di 15 tabelle di dominio live con la copia isolata dopo la prova,
escludendo soltanto le nuove entità del benchmark: 13 coincidono. Il timestamp
progetto differisce perché la creazione della conversazione nella copia lo
aggiorna. Sono inoltre rigenerati nel live 82 chunk derivati dei file
116/117/121/150, fuori dalle cinque SOURCE del benchmark: cambiano ID/timestamp,
contenuti canonici identici. Origine della rigenerazione non tracciata; non si
dichiara l'intero DB live immutato. Avviso SOURCE del benchmark e global chunks
coincidono; originali/fonti congelati verificati, input dei tre run identico.
Sessioni, revisioni, conversazioni e compilazioni preesistenti risultano uguali.

Due errori di aggregazione offline conservati nelle note: serializzazione del
BLOB DOCX nel fingerprint, poi confronto troppo ampio che includeva il timestamp
locale e i chunk derivati. Una prima ispezione dei soli ID comuni non rilevava
righe eliminate/aggiunte: corretta con confronto degli insiemi e del contenuto.
Nessuna chiamata provider ripetuta per questi errori. Primo scoring con percorso
venv ridondante ha emesso un warning del runtime Python; acquisizione finale
rieseguita nell'ambiente corretto. Non sono fallimenti del provider.

Non rieseguite suite backend/frontend: nessuna modifica a codice applicativo,
contratti, gold o KB. Verifiche proporzionate: esecuzioni reali, scoring indipendente,
OOXML, hash/manifest, rendering campionato, confronto dominio, controllo segreti
e diff documentale. Tre esecuzioni non dimostrano significatività statistica o
qualità su altri bandi; nessun nuovo sorteggio reale in questo passo.

## Da dove iniziare dopo B0

Il primo intervento rimane **E1: vista JSON compatta del FORM completo**, come
[pianificato](piano-esperimenti-e1-e2.md). Prima del codice va fissato il contratto
minimo: ID stabili e mapping all'originale, testo e ordine una sola volta,
intestazioni di tabelle, controlli e contesto di rami/ruoli conservati;
metadati di rendering e duplicazioni restano nel backend. È una proiezione
deterministica, senza una nuova chiamata LLM per riscrivere il modulo.

Il trade-off è ridurre costo/ridondanza senza perdere gli indizi che distinguono
persone, ruoli e caselle. Verifica preliminare: tutte le 267 destinazioni ancora
rappresentate e riferimenti risolvibili; poi tre run completi contro B0 con
stesse fonti, modello/thinking, disponibilità USER, schema output e validatori.
Registrare anche perdite e output/reasoning; nessun nuovo errore critico.
Se il prompt richiede un adattamento alla vista, acquisire anche quello come
parte del trattamento. Non modificare contemporaneamente validazione o dialogo
per attribuire tutto il miglioramento alla compattezza.

Dopo E1, valutare separatamente passaggio persistente delle scelte USER,
completezza del pool delle domande e prove di ruolo attraverso intestazioni
SOURCE. E2 viene dopo aver fissato E1: estratti distribuiti fra tutte le sezioni,
confrontati sulle stesse destinazioni e con regressione completa periodica.
**B0 è acquisita; E1 ed E2 non sono ancora implementati né misurati.**
