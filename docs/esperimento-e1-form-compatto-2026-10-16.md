# E1 — FORM completo compatto, 16 ottobre 2026

**Esperimento completato; compact-v1 rimane nel banco di prova.** Tre analisi
reali e tre Word acquisiti. Input provider ridotto del 16,09%; valori conformi
nel Word 14/11/23 sui 60 target documentati, contro 23/17/22 di B0. Risparmio
di token dimostrato su questo caso, qualità non stabilizzata. La chat continua
a usare il formato completo. Tutti gli esiti, inclusi i peggiori, conservati.

L'utente ha approvato implementazione E1, approccio sperimentale e registrazione
dei test. [Misure](benchmarks/2026-10-16-e1-form.json),
[bundle](benchmarks/2026-10-16-e1-form-audit.tar.gz),
[checksum](benchmarks/2026-10-16-e1-form-audit.tar.gz.sha256),
[verifiche finali](benchmarks/2026-10-16-e1-form-checks.json).

[Contratto approvato](contratto-e1-form-compatto.md),
[baseline B0](baseline-minervino-b0-2026-10-16.md).
Raw permanenti: `backend/data/compilation-audit/e1-form-20261016-01/`.

## Trattamento fissato prima delle chiamate

Nuova proiezione `compact-v1` dal catalogo esistente, attiva solo nel runner con
`--form-view compact-v1`; default `full`. `form.blocks` rimane identico:
paragrafi, testo originale, marker, ordine, tabelle/righe/celle, unioni,
intestazioni, gerarchia e parti in sola lettura. `form.contexts` riunisce gli ID
per contesto con relazioni condivise e proprietà individuali. Coordinate/range
per il writer e copie before/after restano nel backend.

Validatori, schema output, fonti/chunk, disponibilità USER, writer e budget
sono quelli di B0. La chat di produzione usa ancora il catalogo completo.
Aggiunte al system prompt soltanto istruzioni per leggere la nuova vista:
1.287 caratteri, acquisite negli artefatti. Il trattamento E1 è quindi formato
più istruzioni corrispondenti; non la sola lunghezza del JSON.

Ogni chiamata impone che l'input canonico ricostruito sia uguale a quello B0.
Controllo separato di equivalenza strutturale prima dell'invio. Tre analisi
sequenziali, DeepSeek flash con thinking attivo, massimo 300 s, zero retry.
Protocollo e hash dei file modificati congelati prima della prima chiamata;
nessuna variante scelta dopo aver visto il risultato di un run.

## Preflight offline

| Misura in caratteri | B0 | E1 | Differenza |
|---|---:|---:|---:|
| FORM | 126.928 | 81.209 | -36,02% |
| Messaggi completi | 264.951 | 220.519 | -16,77% |

267 destinazioni in 142 contesti. SOURCE, schema output, reading plan e dati
USER identici. Dimensioni serializzate, non token o qualità provider.

## Verifiche software

- Prima serie mirata: **110 passati, quattro falliti**, 6,21 s. I nuovi test
  assumevano slot inline accanto a controlli nativi, che il parser attuale
  omette. La proiezione conservava correttamente l'inventario. Corrette soltanto
  le aspettative dei test; parser invariato, fallimento conservato nei raw.
- Serie mirata finale: **116 passati, 5,84 s**. Originali Minervino, Labirinto
  e Catanzaro; sezioni non vuote, proprietà individuali diverse nello stesso
  contesto, tipi/protezione firma, controlli nativi legacy e content control
  true/false, unioni verticali/orizzontali e tabelle annidate, intestazioni
  ripetute, parti in sola lettura. Controlli negativi su perdita/duplicazione
  ID, sezione errata, alterazione testo/marker, tipo/protezione, riferimenti,
  associazione delle colonne. Proprietà future sconosciute respinte.
- Runner con provider simulato: entrambi i formati, esclusione del gold,
  `--prepare-only` senza chiamate, rifiuto preventivo di input diverso dalla
  baseline. Sono test del software, non valutazioni della qualità del modello.
- Backend completo: **2.258 passati, 166,87 s**. Ruff completo passato.
- Frontend non modificato; nessuna suite frontend rieseguita.

Log delle due serie mirate, suite completa e Ruff conservati. Scorer copiato
identico da B0; equivalenze, gold e denominatori invariati. Nessun dato del
gold impiegato per costruire la vista. Le misure LLM e il Word vanno valutati
separatamente dai controlli software.

## Analisi reali: tutte le tre risposte

| Run | Token input | Token output, incluso reasoning | Reasoning | Tempo analisi | Proposte SOURCE conformi / proposte | Conformi con grounding |
|---|---:|---:|---:|---:|---:|---:|
| E1-01 | 63.661 | 36.542 | 28.304 | 150,96 s | 18/18 | 13/60 |
| E1-02 | 63.661 | 26.692 | 17.408 | 102,40 s | 25/26 | 19/60 |
| E1-03 | 63.661 | 40.473 | 31.970 | 166,16 s | 23/23 | 21/60 |

Tutte le analisi sono state auditate localmente; questo non ne certifica la
completezza. “Grounding” include proposte condizionali ancora da chiarire,
non una promozione automatica a RESOLVED. Tempo dell'analisi misurato separatamente
dalla continuazione. Nessun timeout/errore HTTP, retry o run escluso.

| Media per analisi | B0 | E1 | Differenza descrittiva |
|---|---:|---:|---:|
| Token input | 75.864 | 63.661 | -16,09% |
| Token output, incluso reasoning | 40.074 | 34.569 | -13,74% |
| Token totali | 115.938 | 98.230 | -15,27% |
| Tempo analisi | 170,14 s | 139,84 s | -17,81% |
| Valori conformi con grounding | 19,67/60 | 17,67/60 | Peggioramento nella serie osservata |

Le medie dei tre run sono descrittive; non dimostrano significatività o
non inferiorità. Formato e istruzioni sono cambiati insieme come dichiarato.
Il tempo dipende anche da output/reasoning, cache e condizioni del servizio:
non attribuire la variazione temporale alla sola lunghezza dell'input.

**Cache:** prima E1 6.400 token hit/57.261 miss, poi 63.488 hit/173 miss in
ciascuna delle altre due. B0 era caldo in tutte le analisi, 75.648 hit/216 miss.
Nessun warm-up scartato. Non è un confronto monetario né una misura controllata
della latenza a parità di cache. Il reasoning è già incluso nei token output.

Con dialogo ed export: **27 chiamate, 413.624 token**, di cui 307.073 input,
106.551 output, incluso 77.682 reasoning. B0 aveva 30 chiamate e 481.199 token.
Questi totali coprono percorsi dialogici diversi: non sono un risparmio garantito
per ogni pratica. Somma operazioni provider E1 circa 456,07 s, esclusi tempo
umano, passaggi manuali e UI; nessun prezzo o addebito monetario acquisito.

## Qualità per fase e Word

| Run | Conformi nella proposta B0 → E1 | Conformi con grounding B0 → E1 | Conformi sui 60 target nel Word B0 → E1 | Scritture totali E1 |
|---|---:|---:|---:|---:|
| 1 | 22 → 18 | 21 → 13 | 23 → 14 | 14 |
| 2 | 22 → 25 | 17 → 19 | 17 → 11 | 12 |
| 3 | 49 → 23 | 21 → 21 | 22 → 23 | 23 |

Sono ripetizioni indipendenti sullo stesso caso, non coppie con identico seed.
I 60 target sono occorrenze che il gold documenta nelle SOURCE; la provenienza
reale dei valori nel Word viene conservata separatamente: E1-01 **13 SOURCE +
1 USER** conformi, E1-02 **11 SOURCE**, E1-03 **21 SOURCE + 2 USER**. Le risposte
USER ripetono nome/qualità del firmatario iniziale. Nessun dato USER diventa
prova SOURCE e nessun risultato atteso viene adattato agli output.

Tutte le categorie diverse dai 60 testi documentati hanno gli stessi esiti
osservati in B0: zero dei quattro testi USER della pratica, zero delle sei X
attese, zero delle tre checkbox native attese true. Tutti i 123 vuoti testuali,
61 preferenze non selezionate e dieci checkbox attese false preservati. Non si
calcola un punteggio aggregato su 267 che premi la grande quantità di vuoti;
conservarli non dimostra che il modello ne abbia capito l'inapplicabilità.

### Regressioni, miglioramenti locali e limiti rimasti

- **Società:** nel primo run E1 tutte le nove occorrenze societarie vengono
  omesse, mentre B0 le proponeva in tutte le tre analisi. Negli altri due E1
  ricompaiono. Input canonico e fonti uguali, nessuna perdita nell'estrazione.
- **Soci:** tutte le 24 occorrenze omesse in tutti i run E1. B0 le aveva proposte
  correttamente nel terzo, ma il validatore le bloccava. Qui la perdita è già
  nella proposta. Non è provato quale singola trasformazione la determini.
- **Destinazioni:** E1-03 scrive correttamente il comune Bari in `p41.s1`.
  E1-02 ripete l'indirizzo completo, errore di granularità già osservato in B0;
  E1-01 omette il campo. Un miglioramento locale non dimostra stabilità globale.
- **Validazione:** restano i rifiuti di estratti FORM col solo marker o non
  letterali, e l'attribuzione di ruolo/persona richiesta nello stesso chunk
  del valore per alcuni dati del direttore. Criteri invariati, nessun dato
  accettato mediante una nuova deroga.
- **Checkbox:** i gruppi proposti nei run 1 e 3 sono respinti perché una label
  non è letterale nel FORM; run 2 senza gruppi. Tutte le native restano false,
  compresa la partecipazione societaria scelta inizialmente.
- **Dialogo:** nessuno dei quattro argomenti USER congelati viene chiesto.
  Nel run 1 una ripetizione delle scelte iniziali porta all'offerta di bozza;
  nel run 3 due risposte. Nel run 2, dopo due risposte ammesse, rimane la
  richiesta di riconferma della domanda e dei dati identificativi/recapiti
  SOURCE. Manca una risposta specifica nel copione: registrato lo stop, senza
  inventare una nuova attestazione USER, poi export parziale esplicito.

La minore copertura del secondo Word dipende anche dalle condizioni/dialogo:
una proposta migliore di B0 nella fase LLM non assicura più scritture finali.
Lo stesso protocollo fuori copione aveva fermato B0-02 sulla riconferma del
direttore. Le continuazioni sono supervisionate e non equiparate a utenti reali
liberi di aggiungere informazioni. Il limite del copione è parte della misura.

La revisione delle proposte con grounding ha verificato quote, valore e persona:
nessun nuovo valore incongruente rilevato oltre all'indirizzo completo nel campo
comune. Non certifica codici dimostrativi, abilitazioni o ammissibilità reale.
`grounded-proposals-for-review.json` e `semantic-review.json` conservano i dettagli.

## Artefatti finali e integrità

- [E1-01 Word](<../nuovi dati/domanda-iscrizione.E1-RUN-01.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.E1-RUN-01.pdf>).
- [E1-02 Word](<../nuovi dati/domanda-iscrizione.E1-RUN-02.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.E1-RUN-02.pdf>).
- [E1-03 Word](<../nuovi dati/domanda-iscrizione.E1-RUN-03.docx>) e [PDF](<../nuovi dati/domanda-iscrizione.E1-RUN-03.pdf>).

Tutte le 267 destinazioni controllate contro il DOCX fisico: 187 testi,
67 celle e 13 controlli. Le scritture corrispondono al report effettivo,
placeholder e testo prestampato preservati salvo l'avvertenza di bozza.
Altre 15 parti ZIP identiche all'originale. Nessuna spiegazione aggiunta nelle
righe compilabili. Tre bozze parziali, `ready_for_submission=false`.

LibreOffice 26.2.6.3 produce dieci pagine per ciascun Word; ispezionate visivamente
le pagine 1, 3 e 10 di ciascun run. Blocco societario vuoto nel primo, prima
anagrafica vuota nel secondo, comune corretto nel terzo. La firma resta su
pagina quasi vuota; nei primi due anche luogo/data passa all'ultima pagina.
Log, PDF, testo e PNG conservati, inclusi warning liblangtag del runtime locale.
Nessuna certificazione di impaginazione Microsoft Word.

Tutti i 18 hash Minervino e gli 11 Labirinto verificati. I cinque file SOURCE
backend sono identici bit per bit alla fixture; input canonico uguale a B0
in tutte le chiamate. Nella continuazione, controllo del catalogo canonico,
della proiezione compatta e rivalidazione uguale della risposta reale. Non è
una nuova ingestion né un test browser/endpoint HTTP end-to-end. L'analisi è
acquisita separatamente e riusata, con le stesse modalità della baseline.

Entità live preesistenti confrontate con la copia: 49 conversazioni, 28
sessioni, 464 revisioni e 16 compilazioni uguali, escludendo soltanto le nuove
entità create nella copia. Non si dichiara l'intero DB live immutato, né gli
indici derivati congelati. SQLite e profili operativi privati restano fuori dal
bundle; controlli delle credenziali e manifest effettuati prima dell'archivio.
Nessuna migrazione o reindicizzazione richiesta dall'implementazione E1.

Il bundle conserva input prima/dopo, prompt/schema/request effettivi, risposte
HTTP/LLM, audit, quote, stato/revisioni, dialoghi/stop, Word/rendering, metriche,
CSV di confronto, protocollo, codice/patch e test, inclusi i fallimenti iniziali.
`backend/data/` resta esclusa da Git: il bundle in docs/ è la copia trasportabile.
Nessun commit o push eseguito in questo intervento.

## Decisione sperimentale e passo successivo

**Conservare compact-v1 come esperimento, senza promuoverlo nella chat.**
È dimostrata una riduzione dell'input in questa fixture e configurazione;
non è dimostrata una qualità equivalente o migliore. La media delle destinazioni
conformi nel Word scende da 20,67 a 16 su 60, pur con il terzo E1 favorevole.
La struttura equivalente al backend non garantisce un compito altrettanto
leggibile per il modello. Tre campioni non consentono una conclusione generale
su tutti i FORM compatti o sui bandi reali.

Prossima variante E1 proposta: conservare un indice diretto `candidate_id →
contesto` con record più brevi e contesti condivisi, verificando se rende più
esplicita l'associazione delle destinazioni rispetto al raggruppamento attuale.
È un'ipotesi da congelare e misurare in una nuova serie, non una causa accertata
o una modifica già effettuata. Evitare nuove etichette semantiche dal gold.

Passaggio delle scelte USER iniziali, domande mancanti, prove di ruolo fra
intestazioni/chunk e layout firma rimangono interventi separati. **E2 non
avviato:** prima occorre fissare una vista compatta con qualità sufficiente
sul completo. Nessuna nuova estrazione casuale di un altro bando in questo
passo; Catanzaro e Labirinto esercitati soltanto nei test strutturali, senza
nuove valutazioni LLM o affermazioni di generalizzazione.
