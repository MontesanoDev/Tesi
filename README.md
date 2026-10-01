# Mapi RAG

Prototipo per organizzare fonti di progetto e conoscenza aziendale, consultarle
in chat e compilare bozze di moduli Word o template testuali. Frontend React e
TypeScript, API FastAPI e persistenza SQLite. La ricerca usa LangChain con
FTS5 oppure Qdrant; i modelli AI e la ricerca si configurano dall'interfaccia.

**Avvio locale**

Servono Python 3.14 o successivo, `uv`, Node.js 20.19 o successivo della serie
20, oppure Node.js 22.12 o successivo, e npm. Installare le dipendenze nei due
progetti:

```bash
cd backend
uv sync
cd ../frontend
npm ci
cd ..
./start.sh
```

L'applicazione è su `http://localhost:5173`, la documentazione API su
`http://localhost:8000/docs`. Se presente, lo script usa il Node locale in
`.tools/node/bin`; `./start.sh --help` elenca le opzioni di avvio.

Aprire **Impostazioni generali** per configurare i modelli AI e la ricerca.
Con Qdrant occorre anche un servizio Ollama per gli embedding. I dati locali
risiedono normalmente in `backend/data/`; percorsi e configurazione sono
descritti nella documentazione del backend.

**Verifiche**

```bash
cd backend
uv run pytest -q
uv run ruff check .
cd ../frontend
npm test
npm run lint
npm run build
```

Le prove browser e le relative condizioni di esecuzione sono descritte nella
[README frontend](frontend/README.md).

**Documentazione**

- [Backend e gestione dei dati](backend/README.md)
- [Ricerca FTS5 e Qdrant con LangChain](backend/docs/ricerca-vettoriale.md)
- [Configurazione dei modelli AI](backend/docs/modelli-ai.md)
- [Compilazione dei moduli DOCX](backend/docs/compilazione-docx.md)
- [Documenti dimostrativi e fixture](demo-documents/README.md)
- [Architettura e valutazione](architettura.md)
- [Mappa del debito tecnico e stato della pulizia](mappa-debito-tecnico.md)
