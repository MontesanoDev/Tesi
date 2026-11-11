# Mapi RAG

Prototipo sviluppato per una tesi: un assistente che consulta i documenti di una gara d'appalto e
le fonti di un'azienda, risponde alle domande citando le evidenze e compila bozze dei moduli Word
di partecipazione. Ogni valore inserito nel modulo deriva da una fonte verificata o da una
risposta dell'utente. Il risultato è sempre una bozza da rivedere.

## Obiettivi

- Ridurre il lavoro manuale di compilazione dei moduli di gara (domande di partecipazione,
  dichiarazioni, elenchi).
- Non inventare dati: un valore entra nel documento solo se è riscontrato in una fonte o
  dichiarato dall'utente, e ne resta tracciata la provenienza.
- Tenere distinti il **modulo**, che descrive cosa viene chiesto, e le **fonti**, che documentano
  i dati reali. Una dichiarazione prestampata non prova un requisito.
- Misurare la qualità della compilazione rispetto a un riferimento atteso (gold) con metriche
  standard.

## Come funziona

1. Ogni progetto raccoglie le proprie fonti (PDF, TXT, Markdown) e i moduli da compilare (DOCX,
   TXT). Una conoscenza aziendale condivisa vale per tutti i progetti.
2. I documenti vengono suddivisi in frammenti e indicizzati: ricerca per parole chiave (SQLite
   FTS5) oppure semantica (Qdrant con un modello di embedding, BGE-M3 di default).
3. In chat il modello decide se serve una ricerca, formula le query e risponde citando i frammenti
   usati. Le risposte distinguono ciò che è verificato da ciò che manca.
4. Per compilare, il modulo viene analizzato per sezioni. Il modello propone i valori, il backend
   li accetta solo se sono sostenuti da una citazione corretta. I dati mancanti diventano domande
   all'utente nella chat.
5. Su richiesta viene generata una copia dell'originale con i valori inseriti, scaricabile dalla
   chat.

Il modello propone, il backend verifica: validazione degli schemi JSON, controllo delle citazioni
e della provenienza, scritture nel DOCX solo per campi e opzioni riconosciuti.

## Avvio

Su Linux o macOS (x64/arm64), dalla radice del repository:

```bash
./start.sh
```

- Applicazione: http://localhost:5173
- API (OpenAPI): http://localhost:8000/docs

Lo script installa le dipendenze dai lockfile (`npm ci`, `uv sync --locked`) e, se mancano,
scarica in `.tools/` uv e Node.js 22, senza `sudo`. uv scarica anche Python 3.14 se assente. Il
primo avvio richiede Internet. Porte e host si cambiano con `MAPI_BACKEND_PORT`,
`MAPI_FRONTEND_PORT` e `MAPI_HOST`; `./start.sh --help` mostra le opzioni.

## Configurazione

Tutto si configura dall'interfaccia, in **Impostazioni generali**; il file `.env` non serve.

- **Modelli AI.** Serve un modello generativo per chat e compilazione: OpenAI, Anthropic,
  Google, DeepSeek, Mistral, xAI, Groq, OpenRouter, Ollama o un servizio compatibile con le API
  OpenAI. Le chiavi si inseriscono nella UI e vengono salvate cifrate. Ogni progetto può usare un
  modello diverso dall'ingranaggio della chat.
- **Ricerca nelle fonti.** La ricerca per parole chiave funziona subito. Quella semantica richiede
  un modello di embedding: Ollama (`ollama pull bge-m3`), OpenAI, Mistral o un servizio
  compatibile. Le impostazioni si salvano automaticamente; cambiare modello di embedding richiede
  un nuovo indice.
- **Dati.** Database, file caricati e conoscenza aziendale sono in `backend/data/`, esclusa da
  Git. I percorsi si cambiano con `MAPI_DB_PATH`, `MAPI_STORAGE_PATH` e `MAPI_KNOWLEDGE_PATH`. Per
  recuperare le chiavi da un backup serve anche il file `.ai-key` accanto al database.

## Uso

1. Creare un progetto e caricare le fonti e i moduli da compilare (massimo 20 MB per file).
2. Fare domande in chat. Con `@` si sceglie un documento preciso: `spiegami @avviso.pdf` consulta
   solo quel bando.
3. Per compilare, selezionare il modulo e scrivere `@modulo.docx me lo compili?`. Rispondere alle
   domande direttamente nella chat.
4. Chiedere «genera la bozza parziale» e scaricare il DOCX dalla risposta. Rileggerlo sempre prima
   di usarlo.

Per creare i progetti dimostrativi (Catanzaro e Minervino), da `backend/`:
`uv run python -m scripts.create_tender_projects`.

## Valutazione

- `demo-documents/benchmark-minervino/v1/` contiene un caso congelato: modulo reale, azienda
  sintetica, fonti, risposte dell'utente e il risultato atteso (Word e JSON). Il gold non entra
  mai nei prompt né nella conoscenza indicizzata.
- `valutazione sperimentale/` ospiterà la nuova valutazione dell'architettura con precision,
  recall, F1 e BLEU.

## Struttura del repository

| Percorso | Contenuto |
|---|---|
| `backend/app/` | API FastAPI, ingestione, ricerca, chat, motore di compilazione e scrittura DOCX |
| `backend/tests/` | Test del backend (pytest) e relative fixture |
| `backend/scripts/` | Utilità: progetti dimostrativi, reindicizzazione dei moduli, export del catalogo |
| `frontend/src/` | Interfaccia React + TypeScript (Vite) |
| `frontend/e2e/` | Test nel browser (Playwright) |
| `demo-documents/` | Bandi, moduli e dati aziendali fittizi usati da test e prove |
| `valutazione sperimentale/` | Valutazione quantitativa (in preparazione) |
| `docs/` | Mappa del progetto, guide di versione e ripristino |
| `STATUS.md`, `relazioni.md` | Diario dello sviluppo e registro degli esperimenti |
| `AGENTS.md`, `CLAUDE.md` | Istruzioni per gli assistenti di programmazione |

La [mappa del progetto](docs/mappa-progetto.md) descrive moduli e flussi in dettaglio.

## Verifiche

```bash
cd backend && uv run pytest -q && uv run ruff check .
cd ../frontend && npm test && npm run lint && npm run build
```

Per i test nel browser: `npx playwright install chromium`, avviare l'app e lanciare
`npm run test:e2e`. Alcuni scenari usano il backend vero e modificano i dati: usare un database
temporaneo.

## Versioni e ripristino

La versione in uso è la **R3.1** (tag `demo-default-r3-1-20261111`). La precedente R2 resta
congelata e si ripristina con un comando, ad app ferma:

```bash
/home/montesano/tesi-backups/promozione-r3-20261111/rollback-r2.sh
```

Dettagli, backup e verifiche nella [guida alla promozione](docs/promozione-r3-2026-11-11.md).

## Limiti

- È un prototipo di ricerca, non un prodotto: ogni DOCX è una bozza e va rivisto da una persona.
- La qualità dipende dal modello scelto; le verifiche del backend riducono gli errori ma non
  garantiscono che ogni valore sia corretto o attribuito al soggetto giusto.
- Niente OCR: il testo nelle immagini, nelle intestazioni e nei piè di pagina dei DOCX non viene
  letto.
- Le caselle di spunta Word sono supportate solo nelle forme più comuni.

## Licenza

MIT. Vedi [LICENSE](LICENSE).
