# Revisione delle impostazioni di ricerca — 21 ottobre 2026

**Stato corrente: revisione 2, descritta in fondo.** Il primo intervento e i suoi
esiti sono mantenuti come cronologia; non descrivono da soli la schermata attuale.

Intervento circoscritto alla UI delle impostazioni RAG. Algoritmi, contratti API,
formato persistito e pipeline di compilazione conservati. Nessuna nuova analisi
LLM, modifica al database live o aggiornamento dell'indice esistente.

## Significato verificato delle opzioni

| Responsabilità | Implementazione effettiva | Presentazione |
|---|---|---|
| Ricerca lessicale | `backend=fts5`, SQLite FTS5; nessun embedding necessario | Per parole chiave |
| Ricerca vettoriale | `backend=qdrant`, embedding Ollama e ricerca Qdrant | Per significato (semantica) |
| Generazione embedding | `SourceEmbeddings`, adattatore `OllamaEmbeddings` | Servizio Ollama, senza selettore di provider fittizio |
| Modello | `embedding_model` è accettato, salvato e usato dal backend; predefinito `bge-m3` | Nome modificabile soltanto nella configurazione tecnica |
| Archivio integrato | `QdrantClient(path=...)`, directory associata al database; nessun server Qdrant richiesto | Integrato nell'applicazione |
| Archivio esterno | `QdrantClient(url=..., api_key=...)` | Server Qdrant esterno |
| Verifica | Modello/digest e embedding di testo di prova su Ollama, lettura delle collezioni Qdrant | Verifica collegamento, sui dati inseriti |
| Manutenzione | Sincronizzazione esplicita di tutti i frammenti ammissibili, inclusi fonti condivise e moduli dei progetti | Aggiorna indice, con configurazione salvata |

Riferimenti: `backend/app/retrieval_settings.py`, `retrieval_embeddings.py`,
`vector_retrieval.py`, `retrieval_routes.py`; `frontend/src/types.ts` e `api.ts`.
Nessuno di questi file è stato modificato.

## Struttura della schermata

La sezione principale «Ricerca nei documenti» mostra metodo, spiegazione breve,
modello attivo quando la ricerca semantica è pertinente e «Salva impostazioni».
Una configurazione semantica non ancora attivata mostra invece «Modello previsto»;
modificare il modello non cambia l'indicazione del modello attivo prima del salvataggio.

«Configurazione tecnica» è chiusa inizialmente. Due gruppi distinti raccolgono
generazione embedding (Ollama, modello, indirizzo e chiave) e archivio vettoriale
(tipo, indirizzo e chiave Qdrant solo se esterno). I gruppi sono affiancati su
desktop e impilati su schermi stretti. La nota su `127.0.0.1` e `localhost`
specifica che si tratta della macchina del backend, che può essere diversa da
quella dell'utente.

La manutenzione è una zona separata, disponibile anche con la configurazione
tecnica chiusa. L'aggiornamento è disabilitato quando esistono modifiche non
salvate. La verifica non salva e non richiama l'aggiornamento. Cambiare modello,
servizio embedding o archivio presenta un avviso sulla possibile preparazione
di un nuovo indice; il salvataggio non avvia implicitamente quell'operazione.
Il backend conserva la sincronizzazione automatica prima delle ricerche semantiche.

Caricamento iniziale, operazioni in corso, errori contestualizzati e conferme
sono espliciti; le azioni sono bloccate durante una richiesta. Gli errori non
cancellano le modifiche. Campi obbligatori non validi riaprono la configurazione
tecnica al salvataggio; anche la verifica controlla la validità del form.

Le chiavi restano campi password, senza visualizzazione della chiave salvata.
Lasciare vuoto conserva il segreto; la rimozione è esplicita. Cambiare indirizzo
con chiave salvata richiede reinserimento o rimozione, come già imposto dal
backend: la UI rende visibile questa esigenza finché non viene soddisfatta.
Le configurazioni nascoste passando a ricerca lessicale o archivio integrato
rimangono nello stato del form. I prefissi embedding già presenti sono preservati.

## Compatibilità e limiti funzionali

- Il formato `retrieval_settings_v1`, i valori `fts5/qdrant`, `local/remote`,
  i campi, i flag di presenza/rimozione delle chiavi e gli endpoint restano invariati.
- `bge-m3` non è fisso nel backend: il precedente vincolo di sola lettura era
  della UI. Il backend non fornisce un elenco di modelli embedding compatibili;
  si usa il nome di un modello già installato, verificabile con il comando esistente.
- Il servizio embedding supportato è Ollama. Non è stato introdotto un provider
  alternativo né il riuso delle credenziali del modello generativo della chat.
- La verifica esistente controlla insieme Ollama e Qdrant, non offre due test
  indipendenti. Non indicizza documenti; aprire un archivio integrato assente
  può però inizializzarne i file tramite il client Qdrant. Comportamento invariato.
- Il salvataggio non testa la raggiungibilità dei servizi. La preparazione effettiva
  dell'indice avviene su comando o prima di una ricerca, e può richiedere tempo.
  Non c'è un endpoint di avanzamento: la UI mostra uno stato in corso, senza
  percentuali simulate. Cambiare archivio non costituisce una migrazione dei dati.
- L'applicazione distribuisce attualmente un tema scuro. Il pannello usa i token
  di tema e colori di stato compatibili con `color-scheme`; la prova chiara usa
  token chiari iniettati soltanto nel test. Nessun nuovo selettore globale di tema.

## File dell'intervento

- `frontend/src/components/RetrievalSettingsPanel.tsx`: struttura e stati della UI.
- `frontend/src/components/RetrievalSettings.css`: stile circoscritto al pannello.
- `frontend/src/components/RetrievalSettingsPanel.test.tsx`: 16 casi di componente.
- `frontend/e2e/retrieval-settings.spec.ts`: flussi browser desktop/mobile e token chiari.
- `README.md`, `STATUS.md`, `relazioni.md` e questo rapporto: istruzioni e continuità.

## Verifiche

| Verifica eseguita | Esito |
|---|---|
| Suite frontend completa, inclusi 16 casi del pannello | 138 PASS, 14 file, 8,94 s |
| Playwright, due scenari su desktop e mobile | 4 PASS, 7,8 s |
| Lint frontend (`npm run lint`) | PASS |
| TypeScript e build (`npm run build`) | PASS |
| Suite backend pertinente `test_vector_retrieval.py` | 35 PASS, 3,21 s |
| Diff dei file dell'intervento | PASS |

I test di componente coprono separazione delle responsabilità, campi pertinenti,
configurazioni preesistenti e prefissi non esposti, modello attivo rispetto alle
modifiche, conservazione/rimozione delle chiavi, cambio endpoint, caricamento e
riprova, errori, validazione e blocco delle azioni durante le richieste.

Gli scenari Playwright usano API interamente simulate: selezione del metodo,
verifica senza salvataggio, salvataggio senza indicizzazione, errore e riprova
dell'indice, riapertura, campo obbligatorio nascosto, layout e colori. Nessun
backend live è stato usato dal browser. La prova mobile chiara scende a 320 px.
Le schermate desktop scura e mobile chiara sono state anche ispezionate visivamente.

La suite backend pertinente è quella esistente `tests/test_vector_retrieval.py`:
35 PASS in 3,21 s, su database e Qdrant temporanei, embedding/trasporto simulati.
Non è una verifica di disponibilità dei servizi reali né una nuova valutazione RAG.
Suite backend completa e benchmark di compilazione non rieseguiti per questa
modifica UI; i risultati precedenti V12/V13/V14 non vengono presentati come nuovi.

Log finali frontend, schermate e verifica di preservazione:
`backend/data/compilation-audit/retrieval-settings-ui-20261021-01/`.
Snapshot dei file prima dell'intervento e patch del working tree precedente:
`.tools/retrieval-settings-ui-20261021-01/`. Nessun commit o push.

Preservazione: confronto SHA-256 di 312 file applicativi/test e del manifesto
baseline, con sole tre modifiche preesistenti attese (pannello e relativi test).
Il CSS è nuovo. Per 46.932 file preesistenti di dati/benchmark/backup sono stati
confrontati dimensione e mtime, non ricalcolati tutti gli hash: unica variazione
`backend/data/compilation-audit/v14-verifica-20261021-01/frontend.log`, scritta
dal frontend già attivo su 5173 in risposta ai reload HMR. Il servizio preesistente
non è stato arrestato né il log ripristinato. Database e indici esistenti non
sono stati aperti dai test; il frontend di prova separato è su 5180 con API simulate.
Snapshot e manifest sperimentali non vengono riscritti o aggiornati per la UI.

Backup circoscritto all'intervento, ai file precedenti necessari al confronto,
ai log e alle quattro schermate:
`docs/benchmarks/2026-10-21-retrieval-settings-ui-audit.tar.gz`.
Manifest SHA-256 incluso; hash dell'archivio e verifica da estrazione separata
in `docs/benchmarks/2026-10-21-retrieval-settings-ui-verifica.json`.
Non contiene database, indici, credenziali o copie dei benchmark storici.

## Revisione 2 — due riquadri e selezione dei modelli installati

Su richiesta dell'utente, «Ricerca nelle fonti» contiene il metodo «Semantica»
e il menu richiudibile «Impostazioni avanzate» per archivio vettoriale,
verifica del collegamento e manutenzione. Il secondo riquadro, «Modelli di
embedding», mostra il selettore del modello e «Ricarica modelli». Indirizzo e
chiave di Ollama sono nelle sue «Impostazioni avanzate». Un unico salvataggio
applica le impostazioni dei due riquadri. Il pannello dei modelli generativi
preesistente rimane separato e invariato.

Rimosse la descrizione «Trova passaggi con un significato vicino alla domanda…»,
la dicitura «Per significato», la spiegazione dell'archivio integrato e quella
del nome del modello predefinito, come richiesto. Il modello resta `bge-m3`
quando è quello configurato: nessuna scelta automatica di un altro modello.

Per leggere davvero il server configurato è stato aggiunto un endpoint in sola
lettura `POST /api/settings/retrieval/models`. Accetta solo indirizzo e dati di
accesso del servizio embedding. Riutilizza `resolve_settings` per la protezione
delle credenziali: un indirizzo nuovo richiede reinserimento o rimozione della
chiave salvata. Le chiavi Qdrant non vengono usate, decrittate o modificate.
La risposta privata ha `Cache-Control: no-store` e non restituisce chiavi.

La discovery già esistente legge `/api/tags` e, se necessario, `/api/show`,
filtrando sulla capacità `embedding`. Il filtro predefinito `completion` per
la discovery dei modelli generativi è invariato e coperto dai test precedenti.
Nessuna chiamata di embedding, generazione, download, indicizzazione o migrazione
è richiesta dalla lettura dell'elenco. Nessuna modifica ai formati delle
impostazioni persistite o al comportamento della ricerca.

L'elenco si carica all'apertura e si può rileggere manualmente. Cambiare
indirizzo/chiave invalida l'elenco; risposte tardive del server precedente sono
scartate. Un errore o un elenco vuoto non cancellano la configurazione. Un nome
già configurato ma assente dall'inventario resta visibile come «non verificato»;
non viene presentato come un nuovo modello disponibile. L'alias `:latest` non
normalizza implicitamente il valore già salvato. I modelli devono essere già
installati: la UI non li scarica. Le versioni di Ollama che non dichiarano le
capacità non permettono di verificare la compatibilità attraverso questo elenco;
non si usano euristiche sul nome per aggirare tale limite.

File aggiuntivi rispetto alla revisione 1: `backend/app/retrieval_routes.py`,
`backend/app/ai_discovery.py`, `backend/tests/test_retrieval_embedding_models.py`,
`frontend/src/api.ts` e `frontend/src/types.ts`. Aggiornati pannello, CSS,
test componente/E2E, README, STATUS e relazioni. Nessuna modifica ai backend
di retrieval, embedding o indicizzazione, né ai componenti di compilazione.

Verifiche della revisione 2: 21 casi componente (elenco disponibile, vuoto,
errore, cambio servizio, risposta obsoleta, alias e preservazione dei dati)
inclusi nella suite frontend; 14 nuovi casi backend di discovery inclusi nelle
suite pertinenti. Test di rete simulati, database e storage temporanei; nessuna
prova sui servizi reali o nuova compilazione. Log finali e schermate in
`backend/data/compilation-audit/retrieval-settings-ui-20261021-02/`; snapshot
precedente in `.tools/retrieval-settings-ui-20261021-02/`.

Esiti finali: **143 test frontend PASS** (14 file, 7,30 s), **4 scenari browser
PASS** (desktop/mobile, 4,5 s), **76 test backend pertinenti PASS** (6,03 s),
Ruff completo, lint e build frontend PASS. Suite backend completa e benchmark
di compilazione non rieseguiti per questa rifinitura. Schermate scure desktop
e mobile ispezionate visivamente; prova chiara ancora con token simulati.

Preservazione della revisione 2: dei file backend preesistenti cambiano soltanto
le due componenti di discovery/routing indicate; test e componenti di compilazione
conservano gli hash precedenti. Nessun test ha usato il database o l'indice live.
Nel confronto dimensione/mtime dei 46.932 file fotografati prima della revisione 1,
risultano cambiati `backend/data/mapi.db` e i log runtime `frontend.log` e
`server.log` di v14-verifica-20261021-01. Sono presenti servizi preesistenti su
8000/5173; la sola variazione mtime non permette di stabilire quali righe del DB
siano cambiate o attribuirne la causa. Non si dichiara quindi l'identità byte per
byte del DB in uso e non si effettua alcun ripristino. Gli artefatti congelati
non sono stati riscritti dall'intervento; i servizi preesistenti sono conservati.

Backup della sola revisione UI/discovery, senza dati live o credenziali:
`docs/benchmarks/2026-10-21-retrieval-settings-ui-02-audit.tar.gz`, con manifest
SHA-256 e verifica per estrazione separata nel relativo file `-verifica.json`.
