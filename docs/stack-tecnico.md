# Stack tecnico e pipeline di Mapi RAG

## 1. Architettura generale

Mapi RAG usa una classica architettura web a tre livelli:

```text
React + TypeScript
        |
        | HTTP / JSON / multipart
        v
FastAPI + Pydantic
        |
        +---- SQLite relazionale
        +---- SQLite FTS5
        +---- filesystem PDF/TXT
        +---- filesystem Markdown
        |
        v
DeepSeek API
```

Il frontend non accede direttamente al database o ai file. Tutte le operazioni
passano attraverso le API FastAPI.

## 2. Stack dichiarato

### Frontend

- React 19;
- TypeScript 6;
- Vite 8;
- React Router;
- Lucide React per le icone;
- CSS custom responsive;
- Vitest e Testing Library;
- Playwright per test end-to-end e visuali;
- Oxlint.

### Backend

- Python 3.14;
- FastAPI;
- Pydantic;
- Uvicorn;
- SQLite tramite il modulo standard `sqlite3`;
- SQLite FTS5;
- PyPDF per l'estrazione testuale;
- HTTPX per DeepSeek;
- python-multipart per gli upload;
- python-dotenv per la configurazione;
- Pytest;
- Ruff.

### Persistenza

- SQLite per dati applicativi, indici e metadati;
- filesystem per i file caricati;
- file Markdown come sorgente canonica degli artefatti revisionabili.

## 3. Responsabilita del frontend

Il frontend gestisce:

- routing tra progetti e viste;
- caricamento dei dati tramite API;
- composer della chat;
- cronologia delle conversazioni;
- upload dei file;
- selezione delle fonti globali;
- editor Markdown;
- revisione dei Call Facts;
- vista del Draft;
- conferme distruttive;
- stati di caricamento ed errore;
- layout desktop e mobile.

React mantiene lo stato della vista corrente, ma i dati importanti vengono
persistiti dal backend. Un refresh non deve eliminare progetti o conversazioni.

## 4. Responsabilita del backend

FastAPI espone endpoint per:

- salute del servizio;
- elenco, creazione, lettura ed eliminazione dei progetti;
- upload dei file locali;
- gestione dell'archivio globale;
- collegamento delle fonti globali ai progetti;
- lettura e modifica degli artefatti Markdown;
- estrazione e revisione dei Call Facts;
- generazione del Draft;
- ricerca delle evidenze;
- conversazioni e risposte;
- vista di revisione documentale.

Pydantic valida payload e risposte. Gli errori di formato, dimensione e contenuto
dei file vengono convertiti in risposte HTTP esplicite.

## 5. Modello di persistenza

Le tabelle principali sono:

| Tabella | Responsabilita |
| --- | --- |
| `projects` | anagrafica e metriche dei progetti |
| `project_files` | file e artefatti visibili nel progetto |
| `document_chunks` | chunk locali |
| `document_chunks_fts` | indice FTS5 locale |
| `global_documents` | documenti General KB e Company KB |
| `global_document_chunks` | chunk globali |
| `global_document_chunks_fts` | indice FTS5 globale |
| `project_global_document_links` | collegamenti selettivi ai progetti |
| `knowledge_artifacts` | catalogo e versioni dei Markdown |
| `project_artifact_links` | esposizione degli artefatti nei progetti |
| `conversations` | conversazioni persistenti |
| `conversation_turns` | domande, risposte, citazioni ed evidenze |
| `document_fields` | campi della vista di revisione dimostrativa |
| `app_metadata` | stato di inizializzazione dell'applicazione |

Le foreign key con `ON DELETE CASCADE` permettono di eliminare i dati locali di
un progetto senza cancellare i documenti globali.

## 6. File e Markdown

I file caricati vengono salvati sotto:

```text
backend/data/uploads/
```

Gli artefatti revisionabili vengono salvati sotto:

```text
backend/data/knowledge/global/
backend/data/knowledge/projects/<project-id>/
```

Il Markdown e la sorgente canonica. SQLite conserva:

- identificativo;
- tipo;
- scope;
- percorso;
- stato;
- hash del contenuto;
- dimensione;
- versione;
- data di aggiornamento.

Quando un Markdown viene salvato:

1. il file viene scritto in modo atomico;
2. hash, versione e metadati vengono aggiornati;
3. i chunk precedenti vengono rimossi;
4. il nuovo contenuto viene reindicizzato, se ammesso.

## 7. Pipeline di ingestione

La pipeline attuale e:

```text
Upload PDF/TXT
-> validazione estensione e dimensione
-> salvataggio sul filesystem
-> estrazione del testo
-> normalizzazione degli spazi
-> chunking
-> persistenza dei chunk
-> indicizzazione FTS5
```

### 7.1 Validazione

Sono accettati soltanto:

- `.pdf` con MIME applicativo PDF;
- `.txt` con MIME testuale;
- file non superiori a 20 MB.

Un documento senza testo estraibile viene rifiutato. Il prototipo non esegue OCR.

### 7.2 Estrazione

Per i TXT viene letto il contenuto UTF-8. Gli errori di codifica vengono sostituiti
per evitare il fallimento completo dell'ingestione.

Per i PDF, PyPDF estrae il testo di ogni pagina. Questa tecnica funziona con PDF
testuali, ma non con scansioni composte soltanto da immagini.

### 7.3 Chunking

Il chunking non usa DeepSeek, embeddings o LlamaIndex. E implementato nel backend
con una funzione deterministica.

Parametri attuali:

- dimensione obiettivo: 1.200 caratteri;
- sovrapposizione: 200 caratteri;
- taglio preferibilmente sul confine di una parola;
- normalizzazione degli spazi e delle righe vuote.

Esempio:

```text
chunk 0: caratteri 0-1200
chunk 1: caratteri 1000-2200
chunk 2: caratteri 2000-3200
```

La sovrapposizione riduce il rischio che un'informazione venga separata dal suo
contesto esattamente sul confine tra due chunk.

## 8. Che cosa e SQLite FTS5

FTS5 significa Full-Text Search 5. E un'estensione inclusa in SQLite per cercare
testo in modo efficiente.

Non e un modello di intelligenza artificiale e non produce embeddings. Costruisce
un indice inverso concettualmente simile al seguente:

```text
direttore      -> chunk 3, chunk 18
certificazione -> chunk 3, chunk 42
scadenza       -> chunk 12, chunk 27
```

Senza indice, il database dovrebbe rileggere ogni chunk per ogni domanda. Con
l'indice inverso puo individuare rapidamente i chunk contenenti i termini utili.

Il tokenizer FTS5 usato dal prototipo:

- gestisce testo Unicode;
- ignora in larga parte le differenze dovute agli accenti;
- associa ogni riga FTS al chunk originale.

## 9. Costruzione della query

Prima della ricerca, la domanda viene normalizzata:

- conversione in minuscolo;
- rimozione degli accenti per il confronto applicativo;
- estrazione dei token;
- rimozione di stop word comuni;
- esclusione dei token troppo brevi;
- uso di prefissi semplici per gestire alcune variazioni morfologiche.

Esempio semplificato:

```text
Domanda:
Chi e il direttore tecnico di Mapi Ingegneria?

Query FTS:
"direttor"* OR "tecnic"* OR "mapi" OR "ingegneri"*
```

Questa trasformazione non equivale a una comprensione semantica. Migliora la
ricerca lessicale, ma non sostituisce gli embeddings.

## 10. Ranking delle evidenze

FTS5 assegna un punteggio BM25 ai risultati. BM25 considera, tra le altre cose:

- presenza dei termini;
- frequenza dei termini;
- rarita dei termini nel corpus;
- lunghezza del documento.

Mapi RAG possiede due indici distinti:

- indice delle fonti locali del progetto;
- indice dei documenti globali collegati.

I punteggi BM25 prodotti da corpus diversi non sono direttamente confrontabili.
Il prototipo applica quindi un reranking comune che considera:

- BM25 normalizzato in scala logaritmica;
- numero di token significativi della domanda coperti dal chunk;
- percentuale della domanda coperta;
- bonus per date e orari nelle domande temporali;
- riduzione dei chunk adiacenti duplicati;
- eventuale espansione ai chunk vicini per recuperare contesto.

Questo passaggio ha corretto il caso in cui il bando superava impropriamente una
visura aziendale per una domanda sul direttore tecnico.

## 11. Retrieval attuale

Il retrieval completo e:

```text
domanda
-> normalizzazione e tokenizzazione
-> ricerca FTS5 locale
-> ricerca FTS5 globale sui soli documenti collegati
-> unione dei candidati
-> reranking comune
-> deduplicazione
-> selezione dei migliori chunk
-> eventuali chunk vicini
```

Il risultato contiene internamente il testo completo del chunk. L'interfaccia
riceve invece un estratto con:

- nome della fonte;
- indice del frammento;
- snippet;
- rilevanza.

## 12. Generazione con DeepSeek

DeepSeek interviene dopo il retrieval. Non legge direttamente SQLite e non decide
quali file siano collegati al progetto.

Riceve:

- domanda dell'utente;
- migliori evidenze recuperate;
- Company Facts;
- cronologia conversazionale recente;
- istruzioni che impongono l'uso delle fonti.

La risposta richiesta al modello contiene:

- testo della risposta;
- numeri delle citazioni;
- informazioni mancanti.

Il backend verifica che ogni numero di citazione faccia riferimento a
un'evidenza realmente fornita. Una citazione inesistente viene rifiutata.

La pipeline e quindi:

```text
domanda
-> retrieval FTS5
-> evidenze ordinate
-> prompt grounded
-> DeepSeek
-> validazione della risposta
-> persistenza
-> visualizzazione con citazioni
```

## 13. Conversazioni e follow-up

Ogni domanda viene associata a una conversazione. SQLite conserva:

- testo della domanda;
- risposta;
- citazioni;
- informazioni mancanti;
- evidenze;
- modello;
- token consumati;
- stato della generazione.

La cronologia recente viene fornita al modello come contesto conversazionale, non
come nuova fonte documentale. Per alcune domande brevi e dipendenti, il sistema
combina la domanda precedente con quella corrente oppure riusa le evidenze del
turno precedente.

## 14. Call Facts

L'estrazione dei Call Facts usa DeepSeek su un insieme limitato di caratteri
provenienti dalle fonti locali del progetto.

Il modello propone fatti strutturati con provenienza. Il backend renderizza il
risultato in Markdown e lo salva come `call-facts.md`.

La revisione non modifica soltanto lo stato nell'interfaccia. Ogni azione:

1. controlla la versione corrente;
2. modifica il documento strutturato;
3. riscrive il Markdown;
4. incrementa la versione;
5. aggiorna le metriche;
6. reindicizza soltanto i fatti verificati.

Questo realizza un ciclo human-in-the-loop effettivo.

## 15. Generazione del Draft

Il generatore legge:

- `template.md`;
- `company-facts.md`;
- `project-facts.md`;
- fatti verificati di `call-facts.md`.

Non usa direttamente tutto il contenuto recuperabile. Questa scelta riduce il
rischio che dati non verificati vengano inseriti nell'output.

Il backend valida i riferimenti del Draft e lascia `TODO` per i dati mancanti.
Il Draft non viene inserito in FTS5.

## 16. Che cosa non viene usato

Il prototipo attuale non usa:

- modelli di embedding;
- vector database;
- LlamaIndex;
- LangChain;
- retrieval semantico;
- reranker neurale;
- OCR;
- code di job;
- streaming della risposta.

Questa precisazione e importante per la tesi. L'attuale sistema e un RAG
lessicale: recupera documenti prima della generazione, ma il recupero dipende
principalmente dalle parole presenti nel testo.

## 17. LlamaIndex ed embeddings

LlamaIndex non e un modello di embedding. E un framework che puo coordinare:

- caricamento dei documenti;
- chunking;
- chiamata a un modello di embedding;
- salvataggio dei vettori;
- retrieval;
- composizione del prompt.

Un modello di embedding trasforma invece testo e domanda in vettori numerici. La
similarita tra vettori permette di recuperare contenuti semanticamente affini
anche quando non condividono le stesse parole.

Esempio:

```text
documento: "responsabile della supervisione ingegneristica"
domanda:   "chi e il direttore tecnico?"
```

FTS5 potrebbe non riconoscere il collegamento. Un buon embedding potrebbe
collocare le due frasi in regioni vicine dello spazio vettoriale.

## 18. Perche FTS5 e una baseline valida

FTS5 offre:

- esecuzione locale;
- nessun costo di embedding;
- bassa latenza;
- dipendenze minime;
- comportamento riproducibile;
- ranking ispezionabile;
- integrazione diretta con SQLite.

Queste caratteristiche rendono FTS5 una buona baseline sperimentale. Il limite e
la minore capacita di gestire sinonimi, parafrasi e concetti espressi con lessico
molto diverso.

## 19. Evoluzione verso il retrieval ibrido

L'evoluzione consigliata non richiede di eliminare FTS5. Un retrieval ibrido puo
combinare:

```text
FTS5
  -> ottimo per codici, date, sigle e corrispondenze esatte

Embedding search
  -> utile per sinonimi, parafrasi e similarita concettuale

Fusione dei risultati
  -> unione e normalizzazione dei candidati

Reranker
  -> ordinamento finale rispetto alla domanda completa
```

Il contratto restituito al generatore puo restare invariato: una lista di chunk
con fonte, indice, contenuto e rilevanza. Frontend e DeepSeek non devono quindi
essere riscritti completamente.

## 20. Testing

### Backend

Pytest verifica:

- API;
- persistenza;
- ingestione;
- scope dei documenti;
- retrieval;
- ranking;
- conversazioni;
- Call Facts;
- Draft;
- eliminazione dei progetti;
- vincoli di provenienza.

Ruff esegue lint e controllo degli import.

### Frontend

Vitest e Testing Library verificano componenti isolati. Oxlint controlla il
codice TypeScript.

Playwright esegue i flussi completi su viewport desktop e mobile, controllando
anche overflow, dialog, upload, navigazione e viste principali.

### Stato corrente

- 40 test backend;
- 2 test unitari frontend;
- 14 test end-to-end Playwright;
- build TypeScript/Vite riuscita.

## 21. Avvio locale

Dalla root:

```bash
./start.sh
```

Lo script:

1. verifica la presenza degli strumenti;
2. carica la configurazione disponibile;
3. avvia FastAPI sulla porta 8000;
4. avvia Vite sulla porta 5173;
5. arresta entrambi con `Ctrl+C`.

Indirizzi:

```text
Applicazione: http://localhost:5173
API docs:     http://localhost:8000/docs
```

## 22. Configurazione DeepSeek

La configurazione viene letta da `.env` oppure `backend/.env`:

```dotenv
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

La chiave non deve essere inserita nel repository.

## 23. Sintesi tecnica

La pipeline attuale puo essere descritta cosi:

> Il backend estrae testo da PDF e TXT, lo divide deterministicamente in chunk,
> indicizza i frammenti con SQLite FTS5, combina fonti locali e globali tramite
> un reranking comune e fornisce le migliori evidenze a DeepSeek. Gli artefatti
> revisionabili sono Markdown versionati e la generazione finale usa soltanto
> dati strutturati ammessi dal workflow human-in-the-loop.

Questa e la descrizione corretta del prototipo attuale. Embeddings, LlamaIndex e
ricerca vettoriale appartengono alla roadmap, non allo stato gia implementato.
