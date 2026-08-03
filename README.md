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
testo, lo divide in frammenti sovrapposti e li persiste in SQLite. Embedding,
retrieval e risposta del modello saranno aggiunti sopra questo contratto dati
senza dover riscrivere l'interfaccia.
