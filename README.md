# Mapi RAG

Vertical slice della tesi su un assistente RAG per la preparazione e revisione di
documenti tecnici. Il repository separa l'interfaccia dalla pipeline dati:

- `frontend/`: React, TypeScript e Vite;
- `backend/`: FastAPI e SQLite;
- `backend/data/mapi.db`: database locale creato e popolato al primo avvio.

## Avvio locale

Aprire due terminali dalla root del progetto.

Backend:

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
export PATH="$PWD/../.tools/node/bin:$PATH"
npm run dev
```

Aprire `http://localhost:5173`. La documentazione delle API e disponibile su
`http://localhost:8000/docs`.

## Configurazione DeepSeek

La generazione grounded legge la configurazione da `.env` nella root oppure da
`backend/.env`:

```dotenv
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

Senza key il retrieval e le citazioni continuano a funzionare e l'interfaccia
segnala esplicitamente che la generazione non e configurata.

## Verifica

```bash
cd backend
UV_CACHE_DIR=../.uv-cache uv run ruff check .
UV_CACHE_DIR=../.uv-cache uv run pytest -q

cd ../frontend
export PATH="$PWD/../.tools/node/bin:$PATH"
npm run lint
npm run test
npm run build
```

## Stato della vertical slice

Sono gia funzionanti elenco e creazione dei progetti, area del progetto,
separazione tra impostazioni generali e impostazioni del progetto, lettura dei
file collegati e revisione del documento con provenienza dei campi. I documenti
PDF e TXT possono essere caricati nell'area di progetto: il backend estrae il
testo, lo divide in frammenti sovrapposti e li persiste in SQLite. Un indice
full-text FTS5 consente gia di recuperare dal composer evidenze ordinate con
nome della fonte e numero del frammento. Se `DEEPSEEK_API_KEY` e configurata,
DeepSeek produce una risposta JSON vincolata alle evidenze recuperate; citazioni
inesistenti vengono rifiutate. Le conversazioni e i relativi turni sono
persistiti in SQLite: le card recenti riaprono le chat, il refresh conserva
risposte e citazioni e la cronologia recente viene passata al modello soltanto
come contesto conversazionale. Il retrieval semantico tramite embedding potra
essere aggiunto sopra questo contratto dati senza riscrivere l'interfaccia.
