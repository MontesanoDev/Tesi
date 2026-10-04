# Mapi RAG

Applicazione per consultare documenti di progetto e fonti aziendali tramite chat
e compilare bozze di moduli Word o template testuali.

Frontend React/TypeScript, backend FastAPI, SQLite per i dati e LangChain per
la ricerca con FTS5 o Qdrant. Provider AI, modelli e chiavi si configurano
dall'interfaccia; Ollama può essere locale o remoto.

La [mappa del progetto e audit del codice](docs/mappa-progetto.md) descrive moduli,
flussi, codice inutilizzato, verifiche e limiti ancora aperti.

**Avvio**

Servono Python 3.14 o successivo, `uv`, npm e Node.js 20.19+ della serie 20
oppure 22.12+. Dalla radice del repository:

```bash
cd backend
uv sync
cd ../frontend
npm ci
cd ..
./start.sh
```

- Applicazione: `http://localhost:5173`
- API e schema OpenAPI: `http://localhost:8000/docs`

Lo script usa il Node locale in `.tools/node/bin`, se presente. `Ctrl+C`
arresta entrambi i processi. Le porte sono configurabili:

```bash
MAPI_BACKEND_PORT=8001 MAPI_FRONTEND_PORT=5174 ./start.sh
```

Proxy e origini CORS locali seguono le porte scelte. `MAPI_HOST` imposta
l'indirizzo di ascolto; `./start.sh --help` mostra le opzioni.

**Configurazione e utilizzo**

1. In **Impostazioni generali → Modelli AI**, aggiungere un provider o un
   endpoint Ollama e scegliere un modello. Le chiavi si inseriscono nella UI;
   il file `.env` non è necessario. L'ingranaggio nella chat cambia il modello
   del progetto.
2. In **Ricerca nelle fonti**, scegliere FTS5 oppure Qdrant. La ricerca
   vettoriale usa **BGE-M3** tramite Ollama; Qdrant
   può usare un archivio locale oppure un servizio raggiungibile tramite URL.
   Gli indirizzi dei servizi e i comandi di verifica sono nelle impostazioni
   avanzate. Il modello di embedding è mostrato in sola lettura ed è comune
   a tutti i progetti.
3. Caricare le fonti PDF, TXT o Markdown nel progetto o nella conoscenza
   aziendale. La chat cerca nelle fonti e mostra le evidenze utilizzate.
4. In **Moduli da compilare**, caricare uno o più originali DOCX o TXT,
   fino a 20 MB per file. Si possono scaricare e rimuovere singolarmente.
   I file vengono conservati senza modifiche, con ruolo `form`, separato dalle
   fonti: in questa fase non vengono indicizzati né inviati al modello.

La precedente interfaccia di compilazione dei moduli è stata rimossa. Il backend
conserva le API di compilazione e i documenti già generati; la selezione dei moduli
e la compilazione attraverso la chat non sono ancora implementate. Per i DOCX, il backend individua
celle vuote e segnaposti, valida le proposte del modello e produce una bozza con
report. Tutti i candidati del documento vengono inviati in una sola chiamata AI,
insieme alle istruzioni e alle fonti selezionate entro i budget di contesto.
La modalità a gruppi da 32 è stata rimossa. Una proposta bloccata resta vuota
nel documento ed è segnalata nel report; risposte troncate, JSON malformati e
identificatori sconosciuti interrompono la compilazione senza ulteriori chiamate
o salvataggi parziali. Il contesto non usa il retrieval della chat.
Le bozze richiedono revisione umana.

Ollama riceve lo schema JSON delle proposte anche per la compilazione DOCX.
I controlli dei recapiti verificano l'indirizzo completo nella fonte originale,
anche quando il modello ne cita soltanto una parte. Questi controlli non
garantiscono che il dato appartenga al soggetto o alla sezione corretti.

La chat usa il modello scelto nel progetto per decidere se il messaggio richiede
una ricerca. Saluti, ringraziamenti e chiarimenti possono ricevere una risposta
diretta; per le domande documentali il modello formula da una a tre query,
anche risolvendo i riferimenti alla conversazione. Il backend alterna i risultati
delle ricerche, elimina i duplicati e seleziona quattro frammenti principali;
aggiunge poi il testo adiacente, fino a un massimo di otto evidenze.
Non usa un elenco di frasi per riconoscere ringraziamenti o domande successive.

Una risposta diretta richiede normalmente una chiamata AI; una risposta documentale ne
richiede normalmente due. Il limite complessivo della chat, inclusi decisione,
ricerca, risposta ed eventuale correzione, è di 180 secondi con Ollama e 90 con
gli altri provider. Il conteggio dei token include tutte le chiamate di una
risposta riuscita, se il provider comunica i consumi.

Per la decisione iniziale, Ollama riceve lo schema JSON derivato dal validatore.
Una decisione non valida consente un solo tentativo di correzione. Il limite
di risposta per questa fase è 1.024 token, esteso a 2.048 se il provider segnala
un troncamento. La risposta documentale dispone di 2.048 token; in caso di
troncamento viene richiesta di nuovo con le stesse fonti e un limite di 4.096.
Questo secondo tentativo è ammesso una sola volta, anche se avviene durante
la correzione delle citazioni. Le risposte parziali vengono scartate e tutti
i tentativi restano entro il limite complessivo di tempo.

Il backend controlla che i numeri delle citazioni corrispondano alle evidenze
inviate al modello. Se trova riferimenti fuori elenco, chiede una sola
correzione con le stesse fonti, entro il tempo massimo della richiesta.
Se anche la correzione fallisce, mostra il motivo e mantiene consultabili
le evidenze. Il controllo verifica i riferimenti, non garantisce che ogni
affermazione sia correttamente supportata dalla fonte citata. Anche la decisione
iniziale è affidata al modello e può essere errata; lo schema JSON verifica la
forma della decisione, non la sua correttezza semantica.

Prima di usare la ricerca semantica, sul server Ollama configurato eseguire:

```bash
ollama pull bge-m3
```

BGE-M3 è il modello predefinito delle nuove configurazioni. Le configurazioni
già salvate conservano il proprio modello; il passaggio a un altro modello
richiede una nuova indicizzazione. Il cambio del modello della chat non cambia
gli embedding. I pesi vengono scaricati da Ollama e non sono inclusi nella repo.

I dati locali sono in `backend/data/`, esclusa da Git. Per cambiarne i percorsi
si usano `MAPI_DB_PATH`, `MAPI_STORAGE_PATH` e `MAPI_KNOWLEDGE_PATH`. Le chiavi
API sono cifrate: per recuperarle da un backup occorre conservare anche il
file `.ai-key` associato al database.

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

Per le prove browser, installare Chromium con `npx playwright install chromium`
da `frontend/`. Con il frontend avviato, questi scenari usano API simulate:

```bash
npm run test:e2e -- e2e/composer-model-menu.spec.ts e2e/document-review.spec.ts
```

`npm run test:e2e` esegue l'intera suite desktop/mobile: alcuni scenari richiedono
anche il backend e modificano dati, quindi usare un database temporaneo.
`PLAYWRIGHT_BASE_URL` cambia l'URL dell'app usato dai test; screenshot e trace
finiscono in `frontend/artifacts/`.

`demo-documents/` contiene gli input delle prove: documenti di bandi, moduli e
dati aziendali fittizi. Questi file sono usati da test e script e vanno mantenuti
nel repository. Per creare i progetti dimostrativi di Catanzaro e Minervino,
da `backend/` eseguire `uv run python -m scripts.create_tender_projects`.
