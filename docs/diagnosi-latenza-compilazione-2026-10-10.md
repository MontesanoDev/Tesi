# Tempi della compilazione: diagnosi del 10 ottobre 2026

Base: `prune-backend`, `26976fa`, con le correzioni UI locali preservate.
Nessuna modifica al motore backend, alle impostazioni AI o alle sessioni utente.
Questa diagnosi prepara il pruning; le proposte sotto non sono implementate.

## Prova reale appena eseguita

Originale `domanda-partecipazione.docx`, **279 candidate**, configurazione del
progetto: **Ollama / gemma4:e2b / contesto 131072**, retrieval Qdrant locale con
BGE-M3. Creati un backup SQLite, uno storage e una copia dell'indice in una
directory temporanea. La nuova sessione esiste soltanto nel database temporaneo.
Usati provider reali, stessi prompt/schema/validator del codice applicativo;
strumentazione dei tempi nel solo processo diagnostico, nessuna risposta simulata.
Eseguiti due passi automatici, senza input USER e senza generare DOCX.

| Operazione | Tempo misurato | Esito |
|---|---:|---|
| Creazione sessione | 0,48 s | 279 candidate persistiti nella copia |
| Proposta mappa completa `DocumentPlan` | 85,94 s | 64 sezioni proposte, 6.128 token generati |
| Verifica completa `DocumentPlanReview` | 13,26 s | 22 sezioni conservate, 42 respinte, nessuna scelta esclusiva |
| Primo passo completo, mappa inclusa | 100,32 s | Nessun candidate ancora risolto |
| Interpretazione primi 12 candidate `CandidateMeanings` | 15,25 s | 12 interpretazioni senza `semantic` |
| Secondo passo completo | 16,03 s | Tutti e 12 respinti; nessuna ricerca SOURCE avviata |

Le tre richieste al modello occupano **114,44 s su 116,34 s** dei due passi:
circa il **98%**. La prima chiamata include 14,27 s di caricamento del modello,
3,57 s di elaborazione del prompt e 68,00 s di generazione. La seconda invia
nuovamente il modulo con la proposta: 56.760 caratteri, 18.469 token di input.
Non si tratta di una prova completa fino a READY, né di una stima statistica
su più esecuzioni.

### Perché il secondo passo non avanza

L'output reale contiene `candidate_id`, `classification=data`, `requirement`,
`form_quote` e `reason`, ma omette `semantic` per tutti i 12 elementi.
`CandidateMeaning.semantic` è opzionale nello schema, con default `None`:
l'output supera il parsing Pydantic, ma `classify_candidates` scarta ogni
interpretazione `data` senza il binding semantico richiesto dal dominio.

Esempio reale abbreviato:

```json
{
  "candidate_id": "t0.r0.c1",
  "classification": "data",
  "requirement": {
    "name": "Nome",
    "form_quote": "Il/La sottoscritto/a | ",
    "form_citation_id": 1,
    "person_role": "Il/La sottoscritto/a"
  },
  "form_quote": "Il/La sottoscritto/a | ",
  "reason": "Nome del sottoscritto/a"
}
```

Errore per ciascun elemento: **«Interpretazione senza anchor semantico»**.
Il requirement non viene persistito come valido; il campo rimane PENDING.
Review FORM, pianificazione SOURCE, retrieval e matcher SOURCE non vengono
chiamati per questo batch. La garanzia è corretta; il costo nasce dal lavoro
AI inutilizzabile e dai successivi tentativi conservativi.

Lo schema applicativo è quindi più permissivo del contratto effettivo richiesto
per `classification=data`. Il formato strutturato di Ollama non può garantire
una proprietà che lo schema dichiara opzionale. Questo riproduce il difetto
osservato; non dimostra che il modello ometterà sempre il binding.

## Confronto reale con DeepSeek

Su richiesta successiva dell'utente, eseguita una nuova sessione isolata con
**DeepSeek / deepseek-flash / contesto configurato 32768**, usando il profilo
già salvato del progetto `prova` soltanto nel processo diagnostico. Conservati
progetto, modulo e corpus della prova Gemma: `minervino-di-lecce-elenco-sia`,
form 153, Qdrant locale/BGE-M3. Nessuna impostazione del progetto cambiata.
Hash dell'originale uguale fra le prove e invariato nel file locale:
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.

| Misura | Gemma | DeepSeek |
|---|---:|---:|
| Creazione sessione | 0,48 s | 0,49 s |
| Proposta `DocumentPlan` | 85,94 s | 53,69 s |
| `DocumentPlanReview` | 13,26 s | 62,92 s |
| Primo passo completo | 100,32 s | 117,61 s |
| `CandidateMeanings`, primi 12 | 15,25 s | 7,73 s |
| Secondo passo completo | 16,03 s | 33,56 s |
| Tempo totale dei due passi | 116,34 s | 151,25 s |
| Chiamate generative | 3 | 7 |
| RESOLVED/SOURCE | 0 | 5 |

Il secondo passo DeepSeek dura di più perché raggiunge anche review FORM,
pianificazione/query SOURCE, matcher e review SOURCE, che Gemma non raggiunge.
`CandidateMeanings` restituisce `semantic` per tutti i 12 elementi, senza
rifiuti di interpretazione. La mappa propone 17 sezioni e una scelta esclusiva;
la review conserva 11 sezioni, scarta sei sezioni e non approva la scelta.

Le due chiamate di mappa hanno `thinking=enabled`, `reasoning_effort=low` per
scelta del codice applicativo; le successive hanno thinking disabilitato.
L'API registra **11.634 + 13.128 = 24.762 token di ragionamento** per la mappa.
La lentezza iniziale rimane quindi concreta anche con DeepSeek. Non è una prova
che DeepSeek sia generalmente più lento: un solo campione, output diversi e
cache prompt del provider attiva. In totale: 83.798 token input, 32.943 output
(incluso ragionamento), 116.741 token complessivi; nessuna stima di costo.

### Valori realmente risolti, senza input USER

| Candidate | Requisito | Valore persistito | Stato/provenance | Evidenze Company KB |
|---|---|---|---|---|
| `t0.r5.c1` | Operatore economico | Mapi Ingegneria S.r.l. | RESOLVED / SOURCE | chunk `-43`, `-30` |
| `t0.r6.c1` | Forma giuridica | Societa a responsabilita limitata | RESOLVED / SOURCE | chunk `-43`, `-30` |
| `t0.r7.c1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | RESOLVED / SOURCE | chunk `-43`, `-30` |
| `t0.r9.c1` | Codice fiscale operatore | IT01234567890 | RESOLVED / SOURCE | chunk `-43`, `-30` |
| `t0.r10.c1` | Partita IVA | IT01234567890 | RESOLVED / SOURCE | chunk `-43`, `-30` |

Riferimenti: `generalita-mapi.md`, file `-7`, chunk `-43`, e la visura demo,
file `-9`, chunk `-30`. Il nome esatto del secondo documento e tutti gli
estratti sono conservati negli artefatti. Ruolo `source`, scope `global`,
category `company`: gli ID negativi appartengono alla rappresentazione corrente
delle fonti globali, non a moduli. I cinque valori hanno zero errori di
validazione e riferimenti appartenenti al rispettivo allowed bucket. I dati
sono quelli simulati delle fixture, non attestazioni aziendali reali.

Nel batch SOURCE: tre cluster, sei query, 21 evidenze nel pool, tutti i 12
candidate coperti. Retrieval/pianificazione insieme: 10,59 s; matcher 6,32 s;
review SOURCE 4,96 s. Chiamate modello totali 141,14 s, circa il 93% del tempo
complessivo. Restano cinque MISSING, una AMBIGUOUS e una NOT_APPLICABLE nel batch;
**267 PENDING** appartengono al resto del documento non ancora analizzato.
La procura rimane AMBIGUOUS perché la condizione non è attestata; la sede
operativa, richiesta solo se diversa dalla legale, è NOT_APPLICABLE tramite
SOURCE che attesta la coincidenza. Il telefono aziendale proposto per il
sottoscrittore è respinto dalla review per soggetto diverso.

Stop esplicito del benchmark dopo i cinque target RESOLVED, al secondo passo:
nessun turno USER, retry, READY o DOCX generato. Budget massimo del diagnostico
sei passi/420 s, non esaurito. È una prova del service automatico con provider
reali, **non un nuovo E2E browser né una compilazione completa dei 279 candidate**.
La sessione diagnostica non è presente nel database dell'utente.

## Parser, lettura e retrieval misurati separatamente

Stesso snapshot temporaneo, nessuna mutazione degli indici originali. Ricerca
diagnostica: «denominazione sociale forma giuridica sede legale», quattro risultati,
target `source`. La prova SOURCE è indipendente dal batch respinto sopra.

| Operazione | Tempo | Esito |
|---|---:|---|
| Parser originale DOCX | 0,093 s | Catalogo strutturale letto |
| Lettura/proiezione sessione | 0,111 s | Risposta JSON di circa 1,16 MB |
| FTS5 | 0,006 s | 4 evidenze, tutte SOURCE |
| Qdrant, prima ricerca della prova | 6,624 s | 4 evidenze, tutte SOURCE |
| Qdrant, ripetizione a caldo | 0,128 s | 4 evidenze, tutte SOURCE |

La prima ricerca vettoriale include avvio/riscaldamento del percorso embedding;
non separati in questa misura i costi interni di ogni operazione. I numeri sono
campioni diagnostici, non percentili o confronti di qualità semantica FTS/Qdrant.
Parser e SQLite non spiegano i minuti iniziali. In questa riproduzione il
retrieval non è nemmeno raggiunto prima del rifiuto delle interpretazioni.

## Sessioni già presenti: lettura storica, non nuovi benchmark

Ricostruiti gli intervalli fra `analyze_start`, `source_start`, `document_plan`
e `analyze_complete` dalle revisioni persistite. Escluse le attese fra turni
USER; inclusi nei passi AI, retrieval, validazione e persistenza.
Il provider indicato è quello associato al progetto/ai turni consultati, non
una traccia immutabile del provider per ogni singola chiamata storica.

| Sessione/progetto | Mappa iniziale | Passi completati | Tempo nei passi | RESOLVED |
|---|---:|---:|---:|---:|
| Gemma, `minervino-di-lecce-elenco-sia` | 85,84 s | 22 | 374,30 s, circa 6 min 14 s | 0 |
| DeepSeek, `prova` | 123,56 s | 52, su due cicli | 811,64 s, circa 13 min 32 s | 5 |

- Gemma: 273 PENDING e 6 AMBIGUOUS. Tutti i 21 passi completati dopo la mappa
  presentano errori di validazione. Il 23° passo ha un claim senza completamento:
  il lease è scaduto. La proiezione API attuale restituisce `paused=true`,
  `auto_continue=false`; lo status persistito resta ANALYZING. Non c'è evidenza
  sufficiente per attribuire l'interruzione a chiusura pagina, riavvio o altra causa.
- DeepSeek: i cinque RESOLVED sono operatore economico, forma giuridica, sede
  legale, codice fiscale e partita IVA, tutti con SOURCE. Primo ciclo: 36 passi
  per 577,97 s; secondo: 16 per 233,67 s. Il ciclo arriva vicino al budget di
  dieci minuti prima del checkpoint. La sessione è GENERATED ma conserva 81
  PENDING, 157 AMBIGUOUS e altri irrisolti: l'export esistente è una bozza
  incompleta esplicitamente richiesta, non prova che il modulo sia completato.
- I primi cinque valori SOURCE risultano risolti nei primi due batch dopo la
  mappa; l'attesa successiva riguarda il resto del documento e i riesami.
- Le revisioni DeepSeek occupano circa 15,61 MiB, con un evento massimo di circa
  2 MiB: vengono conservati oggetti campo completi prima/dopo, non soltanto valori.
  È un costo di complessità e crescita dei dati; non risulta il collo di bottiglia
  principale di questa prova.

## Percorso e punti da valutare nel pruning

Percorso corrente:

```text
TurnPlan → CompilationSession → DocumentPlan → DocumentPlanReview
→ batch strutturale → CandidateMeanings → FormReview
→ CompilationSourcePlan → query SOURCE seriali → CandidateMatches
→ SourceReview (+ HistoricalServices quando necessario)
→ validatori → persistenza → batch successivo / checkpoint USER
```

Massimo 12 candidate per passo, fino a sei chiamate AI per passo, massimo
36 passi / 600 s per ciclo; il passo già avviato ha timeout di 180 s.
La UI avanza in serie. Il primo irrisolto non interrompe più tutto: ciò riduce
le domande ma può prolungare parecchio l'attesa prima del primo checkpoint.

Priorità proposte, **da progettare e approvare prima dell'implementazione**:

1. Allineare lo schema dell'interpretazione al contratto di dominio:
   per un candidate `data` rendere esplicito il binding necessario. Separare
   eventualmente le varianti `data`/review/decorative, mantenendo il rifiuto
   backend di output non grounded. Misurare quanti riesami diventano inutili.
2. Riutilizzare una mappa FORM già verificata per lo stesso originale/hash,
   con invalidazione e ambito documentale corretti. Oggi una nuova sessione
   ripaga due letture complete AI anche quando il file è identico.
   Costo: definire versione/schema della cache e non propagare fatti aziendali.
3. Ridurre passaggi e payload ripetuti, facendo emergere un solo coordinatore
   delle fasi e una rappresentazione condivisa del contesto. Valutare i checkpoint
   in base al lavoro utile; non sostituire verifiche SOURCE con assunzioni e non
   rimuovere review soltanto per ridurre il numero di chiamate.
4. Rendere disponibili tempi/call count/rifiuti per fase e risposte API compatte
   per l'avanzamento. Oggi il thread mostra attività ma non distingue una mappa
   lenta da una serie di interpretazioni respinte. Valutare anche revisioni più
   compatte preservando audit, provenance e concorrenza.

Il contesto configurato di 131072 token è un fattore da misurare, non una causa
dimostrata: i log mostrano offload completo sulla GPU e il tempo dominante
misurato è la generazione della mappa. Non cambiati modello, finestra, prompt,
budget, routing, parser, renderer, RAG o condizioni di validazione.

## Verifiche software e artefatti

- Backend: **104 test passati** (`test_compilation_sessions.py`,
  `test_compilation_retry_phases.py`, `test_compilation_stability.py`). Usano
  provider simulati e dimostrano comportamento software, non latenza/qualità AI.
  Ruff completo backend e `git diff --check` passati.
- Correzione UI concomitante: il cestino dei moduli usa già lo stesso SVG,
  dimensioni e classi di quello delle fonti; aggiunto lo stesso spazio riservato
  prima del pulsante per allinearlo nella colonna corretta. Hover/focus condivisi.
  Lint/build e **2 E2E project-forms desktop/mobile** con API simulate passati.
- Su richiesta dell'utente, artefatti Gemma trasferiti da `/tmp` a
  `backend/data/compilation-audit/latency-20261010-gemma/`: metriche, I/O, raw,
  originale, stato, revisioni e script usato. I prompt non erano stati acquisiti
  nella prova Gemma e non sono ricostruiti retroattivamente.
- DeepSeek: `backend/data/compilation-audit/latency-20261010-deepseek/`, con
  prompt/schema esatti, body delle richieste, risposte complete/raw, token e tempi,
  risultati delle fasi/retrieval, stati dopo ogni passo, CSV dei 279 candidate,
  revisioni, verifiche e manifest SHA-256. Non salvati header di autenticazione,
  chiavi o database. Salvati separatamente anche gli snapshot delle sessioni
  storiche in `latency-20261010-historical/`.
- Indice e modalità di conservazione: [archivio benchmark](benchmarks/README.md).
  [Riepilogo strutturato versionabile](benchmarks/2026-10-10-compilation-latency.json).
  I percorsi `backend/data/` sono esclusi da Git. Per il checkpoint successivo
  richiesto dall'utente è stato aggiunto un bundle versionato dei soli benchmark
  isolati in `docs/benchmarks/2026-10-10-latency-audit.tar.gz`; le sessioni storiche
  rimangono private/locali. Dettagli e checksum nell'indice dell'archivio.
- Runner riutilizzabile: `backend/scripts/benchmark_compilation_latency.py`.
  Dopo il benchmark: Ruff backend completo e controllo SHA-256 dei manifest;
  verificati originale invariato, assenza della sessione nel DB live, bucket
  SOURCE dei cinque valori e nessuna occorrenza della chiave API negli artefatti
  acquisiti. Nessuna suite frontend/backend ripetuta per il solo confronto reale:
  i 104 test software sopra appartengono alla diagnosi Gemma precedente.

Nessun commit o push durante le misure; il successivo checkpoint è richiesto
separatamente dall'utente e documentato in STATUS. Prossimo passo: riprendere la
direzione bottom-up/una chiamata già scelta, usando queste misure come baseline
e mantenendo le garanzie FORM/SOURCE/USER.
