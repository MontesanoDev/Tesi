# Mapi RAG

Vertical slice della tesi su un assistente RAG per la preparazione e revisione di
documenti tecnici. Il repository separa l'interfaccia dalla pipeline dati:

- `frontend/`: React, TypeScript e Vite;
- `backend/`: FastAPI e SQLite;
- `backend/data/mapi.db`: database locale creato e popolato al primo avvio.

## Avvio locale

Dalla root del progetto e sufficiente un solo comando:

```bash
./start.sh
```

Lo script avvia FastAPI e Vite, mostra gli indirizzi locali e arresta entrambi
con `Ctrl+C`. Le porte possono essere cambiate con `MAPI_BACKEND_PORT` e
`MAPI_FRONTEND_PORT`.

In alternativa, aprire due terminali dalla root del progetto.

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
npm run test:e2e
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

La conoscenza revisionabile segue un approccio Markdown-first. Ogni progetto
collega artefatti globali (`general-kb.md`, `company-facts.md`) e artefatti locali
(`call-facts.md`, `project-facts.md`, `template.md`, `draft.md`). I file Markdown sono la
fonte canonica; SQLite ne conserva catalogo, scope, versione, hash e chunk FTS5
derivati. Il salvataggio dall'editor aggiorna il file e lo reindicizza nel RAG.
Da questa vista e anche possibile avviare l'estrazione dei Call Facts: DeepSeek
analizza i frammenti delle sole fonti del progetto, propone fatti senza un enum di
categorie prefissato e associa a ciascuno nome del documento e numero del
frammento. Il risultato sostituisce `call-facts.md`, viene marcato come da
verificare, versionato e reindicizzato. Le modifiche manuali non salvate bloccano
la riestrazione per evitare sovrascritture involontarie.

I Call Facts dispongono inoltre di una revisione human-in-the-loop. Ogni fatto puo
essere verificato, modificato, scartato o ripristinato dalla vista di progetto; le
azioni riscrivono e versionano `call-facts.md`, che conserva ID, stato e provenienza
di ogni elemento. Soltanto i fatti marcati come verificati vengono derivati in
chunk FTS5 utilizzabili dal RAG. Una modifica riporta sempre il fatto allo stato
`Da verificare`, mentre i fatti scartati restano nel Markdown per tracciabilita ma
sono esclusi dall'indice.

Il draft viene generato seguendo il `template.md` e usando esclusivamente
`company-facts.md`, `project-facts.md` e i Call Facts gia verificati. I dati
assenti restano come `TODO`, mentre i riferimenti `[CF:...]`, `[COMPANY]` e
`[PROJECT]` rendono visibile la provenienza. Il backend rifiuta riferimenti a
Call Facts non verificati. `draft.md` resta modificabile e versionato, ma non
viene indicizzato: un output generato non puo quindi rientrare nel RAG come fonte.

La Company KB usa un indice documentale globale separato. I PDF e TXT aziendali
vengono caricati e suddivisi in frammenti una sola volta dalle impostazioni
generali; ogni progetto puo poi collegarli o scollegarli senza duplicare file o
chunk. Il retrieval unisce le fonti locali ai soli documenti aziendali collegati,
mantenendo l'isolamento tra progetti. `Company Facts` resta distinto dalla Company
KB: il primo contiene dati strutturati verificati, la seconda documenti e referenze.
