# Mapi RAG

Applicazione per consultare documenti di progetto e fonti aziendali tramite chat
e compilare bozze di moduli Word o template testuali.

Frontend React/TypeScript, backend FastAPI, SQLite per i dati e LangChain per
la ricerca con FTS5 o Qdrant. Provider AI, modelli e chiavi si configurano
dall'interfaccia; Ollama può essere locale o remoto.

La [mappa del progetto e audit del codice](docs/mappa-progetto.md) descrive moduli,
flussi, codice inutilizzato, verifiche e limiti ancora aperti.
La [baseline della demo](docs/baseline-demo.md) documenta il punto di ripristino
locale e la separazione dal nuovo sviluppo a chiamata unica.

**Avvio**

Da Linux o macOS (x64/arm64), dalla radice del repository:

```bash
./start.sh
```

- Applicazione: `http://localhost:5173`
- API e schema OpenAPI: `http://localhost:8000/docs`

Lo script installa automaticamente le dipendenze frontend mancanti o non valide
con `npm ci` e sincronizza quelle backend con `uv sync --locked` prima di
avviare i servizi. Se manca `uv`, usa il suo [installer ufficiale](https://docs.astral.sh/uv/reference/installer/)
per installarlo in `.tools/uv`, senza modificare il profilo della shell.
Se Node o npm mancano o Node non è compatibile, scarica Node.js 22.23.3 con npm
dal [sito ufficiale](https://nodejs.org/download/release/v22.23.3/) in
`.tools/node`, verificando SHA-256. Usa gli strumenti locali con precedenza
su quelli di sistema, senza `sudo`. Sono accettati anche Node 20.19+ della serie
20, 22.12+ della serie 22 e versioni successive alla 22 già installati.
`uv` può scaricare Python 3.14 se assente. Per il primo avvio servono Internet,
Bash, `curl` o `wget`, `tar`/`gzip` e `sha256sum` o `shasum`.
I lockfile non vengono aggiornati. `Ctrl+C`
arresta entrambi i processi. Le porte sono configurabili:

```bash
MAPI_BACKEND_PORT=8001 MAPI_FRONTEND_PORT=5174 ./start.sh
```

Proxy e origini CORS locali seguono le porte scelte. `MAPI_HOST` imposta
l'indirizzo di ascolto; `./start.sh --help` mostra le opzioni.

**Configurazione e utilizzo**

Ollama e i suoi modelli si installano separatamente da `start.sh`.
BGE-M3 è un modello di embedding: per chat e compilazione serve anche un
modello generativo, locale o tramite provider API. Con Ollama installato e
attivo, il modello degli embedding si scarica con `ollama pull bge-m3`.
Nell'installazione locale preparata per questo workspace, Ollama è un servizio
dell'utente: `systemctl --user status ollama` ne verifica lo stato e
`systemctl --user start ollama` lo avvia se arrestato.

1. In **Impostazioni generali → Modelli AI**, aggiungere un provider o un
   endpoint Ollama e scegliere un modello. Le chiavi si inseriscono nella UI;
   il file `.env` non è necessario. L'ingranaggio nella chat cambia il modello
   del progetto. Con DeepSeek, lo switch **thinking** funziona anche con
   **Usa predefinito**: la preferenza resta salvata per progetto quando si cambia
   modello. Il progetto continua a seguire il predefinito generale. Le vecchie
   impostazioni si aggiornano automaticamente all'avvio del backend.
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
   fonti. Il testo del corpo DOCX (incluse le tabelle) o del TXT viene estratto
   e frammentato negli stessi indici delle fonti, conservando il ruolo del file.
   La chat può analizzarlo quando il messaggio riguarda un modulo.

Per esempio, con `domanda-partecipazione.docx` nel progetto, si può chiedere
«riassumi la domanda di partecipazione». Il pianificatore riceve i nomi e gli
identificatori dei moduli del progetto e seleziona il documento da interrogare.
Il backend applica il target `form` oppure `source` alla ricerca e alla
rilettura delle evidenze: una richiesta sul modulo usa solo quel modulo;
una domanda sui dati reali dell'azienda usa solo fonti fattuali, incluse quelle
globali. Le evidenze mostrano il ruolo **Modulo** o **Fonte**.
Una dichiarazione prestampata non prova il possesso di un requisito.
Se manca il modulo o non si recuperano i suoi frammenti, la chat lo segnala
senza sostituirli con fonti aziendali. Un riferimento ambiguo richiede il nome
del modulo. Domande come «con i documenti che ho posso iniziare a compilarlo?»
usano il target `mixed`: ricerche separate sul modulo e sulle fonti, mantenute
in due contesti fino alla generazione. Una protezione backend delle richieste
esplicite di disponibilità impone mixed anche se il planner propone form.
Dopo la lettura del modulo si individuano requisiti con etichette ed estratti
letterali; il backend costruisce da questi le query source, senza riutilizzare
la domanda generica come query fattuale. L'extractor ha un compito documentale
stabile: la domanda delimita l'ambito, senza diventare una prova o una richiesta
di anticipare la disponibilità. I singoli dati personali mantengono il ruolo
della persona, citato nello stesso estratto del campo. Una premessa su un
requisito viene verificata nel FORM prima di cercarne il riscontro nelle SOURCE.
La risposta distingue **Requisiti del
modulo**, **Informazioni verificate nelle fonti** e **Informazioni non ancora
verificate**. Il backend compone queste sezioni; il modello non scrive conclusioni
libere di compilabilità. Un valore richiede un estratto source che lo contenga
e lo associ al requisito. Requisiti senza supporto valido restano non verificati.
Senza riscontri fattuali segnala che i dati non possono ancora essere considerati
compilabili; senza il modulo non tenta il confronto. Non avvia una compilazione.

Ruolo e provenienza restano distinti: le fonti del progetto hanno
`scope=project:ID`; i documenti globali hanno `scope=global` e
`category=company` oppure `general`, secondo la KB effettiva. Entrambe le KB
restano condivise e partecipano alle ricerche fattuali come prima. La categoria
non prova che il documento contenga dati dell'operatore: una norma o un esempio
non ne dimostra i requisiti. API e storico conservano ruolo, scope, categoria,
identificatori di documento/frammento, nome e metadati. La UI mantiene le
etichette esistenti; scope e categoria sono verificabili nella risposta API.

**Moduli già archiviati senza frammenti:** occorre una reindicizzazione esplicita,
da `backend/`, senza modificare gli originali:

```bash
uv run --locked python -m scripts.reindex_project_forms --project ID_PROGETTO
```

`--form-id ID_MODULO` limita l'operazione a un file. FTS5 si aggiorna nella stessa
transazione dei frammenti; Qdrant li sincronizza prima della ricerca successiva.
Con Qdrant configurato si può aggiungere `--sync-vectors` per sincronizzarlo
subito. Il solo comando di aggiornamento Qdrant non estrae testo dagli originali.
Anche la cancellazione dei vettori segue la riconciliazione prima delle ricerche;
la rimozione da SQLite/FTS5 e storage avviene eliminando il modulo.
Gli indici vettoriali precedenti aggiornano i metadati di ruolo e categoria alla
prima sincronizzazione, nella stessa collezione. Il confronto misto non richiede
riestrazione per moduli già indicizzati. Non ci sono migrazioni automatiche dei
moduli archiviati.

La precedente interfaccia di compilazione dei moduli è stata rimossa. È disponibile
la **CompilationSession V1 nella chat**: creazione da un DOCX archiviato, candidate
persistiti, risoluzione SOURCE limitata per richiesta, correzioni utente con
revisioni e generazione di nuove copie dall'originale. API, budget e prova manuale
sono in [docs/compilation-session-v1.md](docs/compilation-session-v1.md).
Nel composer digitare `@` e scegliere un modulo: le domande normali lo usano come
contesto senza compilare. Scrivere **«me lo compili?»** avvia/riprende la sessione
tramite il planner della chat. L'analisi avanza automaticamente con un budget
persistito (36 passi / 10 minuti per ciclo), fermandosi per un chiarimento o errore.
Rispondere alla domanda aperta direttamente nella chat: un valore univoco diventa
USER, distinto dai dati verificati SOURCE. Confermare la generazione nella chat;
la risposta di Mapi presenta il download DOCX quando il documento è disponibile.
Analisi, chiarimenti, pausa e ripresa condividono la stessa presentazione delle
risposte RAG, senza pannelli o conteggi tecnici. Una bozza incompleta richiede
una richiesta esplicita nella conversazione.
Il routing usa un solo contratto semantico per chat e compilazione: una richiesta
come «spiegati meglio» può ricevere una spiegazione senza modificare campi o
rinviare la domanda; pausa e ripresa sono intenzioni distinte dalle risposte.
Riaprire la conversazione ricostruisce stato e domanda dal backend senza azzerare
il budget. Riavviare il backend aggiornato per le colonne additive dei riferimenti
e dello storico workflow; non serve reindicizzare.

Il backend conserva lo storico delle compilazioni generate: elenco, dettaglio e
download dei documenti già prodotti restano disponibili. Il percorso precedente
`/document-compilations`, che creava una nuova bozza con una sola chiamata AI su
tutto il documento, è stato rimosso il 9 ottobre 2026: la creazione passa dalla
CompilationSession V1 nella chat, con retrieval SOURCE mirato e passi limitati.
I validatori delle proposte restano condivisi con le sessioni. Le bozze
richiedono revisione umana.

I controlli dei recapiti verificano l'indirizzo completo nella fonte originale,
anche quando il modello ne cita soltanto una parte. Questi controlli non
garantiscono che il dato appartenga al soggetto o alla sezione corretti.

La chat usa il modello scelto nel progetto per decidere se il messaggio richiede
una ricerca. Saluti, ringraziamenti e chiarimenti possono ricevere una risposta
diretta; per le domande documentali il modello formula da una a tre query,
anche risolvendo i riferimenti alla conversazione. Il backend alterna i risultati
delle ricerche, elimina i duplicati e seleziona quattro frammenti principali;
aggiunge poi il testo adiacente, fino a un massimo di otto evidenze.
Per `mixed` si eseguono fino a tre query FORM. Dopo l'estrazione, una sola
pianificazione SOURCE in batch raggruppa i requisiti per argomento/soggetto:
massimo **6 gruppi, 4 requisiti per gruppo, 2 query per gruppo**. Ogni query
contiene le etichette di uno o due requisiti del gruppo; non si usa la domanda
generica né le source_queries anticipate dal planner iniziale. Le proposte
coerenti troppo grandi vengono suddivise; ID inventati, duplicati e gruppi con
ruoli personali diversi sono respinti. Senza un piano valido si usano gruppi
per ruolo personale e ricerche singole per gli altri campi, entro lo stesso
budget. Ogni requisito escluso è indicato come **non ricercato**, distinto da
uno cercato senza supporto valido. Non viene inventata un'associazione mancante.

Il modulo conserva due frammenti principali/quattro con vicini. Ogni query
SOURCE recupera due frammenti principali, con merge/espansione entro **quattro
evidenze per gruppo**: fino a 12 ricerche e 24 SOURCE, deduplicate, più 4 FORM.
Non c'è un top-k globale SOURCE che cancelli un gruppo. Le fonti ammesse per
ciascun requisito restano quelle recuperate per il suo gruppo. Per la
denominazione si conservano ragione sociale e forme societarie; FTS5 conserva
gli acronimi puntati come frasi per trovare nomi senza un'intestazione del campo.
L'estrazione accetta fino a 32 proposte per risposta e, dopo grounding e
deduplicazione per campo/ruolo personale, usa al massimo 16 requisiti nel turno.
Superare il budget di 16 con altri requisiti validi non invalida l'intera lista.
Gli estratti FORM restano contigui e nella singola evidenza citata, fino a 2.000
caratteri; il confronto normalizza spazi, case, Unicode e varianti tipografiche,
senza fuzzy matching, riordino di parole o ricerca in un'altra evidence.
Non usa un elenco di frasi per riconoscere ringraziamenti o domande successive.

Una risposta diretta richiede normalmente una chiamata AI; una risposta documentale ne
richiede normalmente due. Mixed aggiunge la lettura dei requisiti e, quando
sono più di due, un'unica chiamata per raggrupparli: normalmente quattro chiamate
AI, tre con uno/due requisiti. Se non sono recuperate SOURCE si evita la chiamata
finale, componendo direttamente la conclusione prudente. Il raggruppamento ha
1.024 token di output, senza retry né chiamate per singolo campo. Un testo
answer anticipato dal planner per una
richiesta di disponibilità con action=retrieve viene scartato; query e ID
continuano a essere validati. Il limite complessivo della chat, inclusi decisione,
ricerca, risposta ed eventuale correzione, è di 180 secondi con Ollama e 90 con
gli altri provider. Il conteggio dei token include tutte le chiamate di una
risposta riuscita, se il provider comunica i consumi.

L'extractor espone lo schema anche nel prompt, quindi ai provider con solo JSON
mode. Ha 4.096 token di output e un unico secondo tentativo: per lista vuota,
schema/grounding invalidi riceve gli errori concreti e le stesse evidenze FORM;
per troncamento il budget sale a 8.192. Non aggiunge ricerche o altri tentativi.
Due letture senza requisiti pertinenti terminano senza ricerca SOURCE né
valutazione di disponibilità. Output ancora invalidi restano errori espliciti.

Per la decisione iniziale, Ollama riceve lo schema JSON derivato dal validatore.
Una decisione non valida consente un solo tentativo di correzione. Il limite
di risposta per questa fase è 1.024 token, esteso a 2.048 se il provider segnala
un troncamento. La risposta documentale dispone di 2.048 token; in caso di
troncamento viene richiesta di nuovo con le stesse fonti e un limite di 4.096.
Questo secondo tentativo è ammesso una sola volta, anche se avviene durante
la correzione delle citazioni. Le risposte parziali vengono scartate e tutti
i tentativi restano entro il limite complessivo di tempo.

Il backend controlla che i numeri delle citazioni corrispondano alle evidenze
inviate al modello. Per `mixed` valida proposte strutturate con requirement_id,
source_citation_id, source_quote e value: ruolo source, citazione esistente,
estratto presente nella fonte, valore contenuto nell'estratto e associazione
testuale al requisito. Un nominativo generico richiede lo stesso ruolo personale
nei due estratti. I numeri di iscrizione professionale possono avere etichette
equivalenti senza la parola «albo»: il numero deve essere legato all'iscrizione
nell'estratto, non a un telefono, una data o un altro dato nello stesso chunk.
Anche gli altri valori numerici richiedono un'associazione nel passaggio locale,
non soltanto la presenza della label in una lunga citazione. Il matcher usa un
compito SOURCE stabile su tutti i requisiti e le rispettive fonti ammesse;
la formulazione della domanda e la cronologia non selezionano i supporti.
Ollama riceve gli schemi JSON; la validazione vale per tutti
i provider. Se trova riferimenti o riscontri invalidi, chiede una sola
correzione con le stesse fonti, entro il tempo massimo della richiesta.
Se dopo la correzione mixed restano proposte invalide, le scarta e mantiene
solo i supporti verificabili; gli altri requisiti sono non verificati. Proposte
concorrenti per lo stesso requisito non vengono selezionate arbitrariamente.
JSON inutilizzabili o troncati restano errori espliciti. Per le risposte form
il controllo blocca anche frasi di disponibilità/compilabilità riconoscibili
senza una fonte fattuale. Il controllo non garantisce che ogni
affermazione sia correttamente supportata dalla fonte citata. Anche la decisione
iniziale è affidata al modello e può essere errata; lo schema JSON verifica la
forma della decisione, non la sua correttezza semantica. La scelta del target e
del modulo è normalmente affidata al pianificatore, con la protezione descritta
per le richieste esplicite di disponibilità; il backend garantisce i filtri
del target selezionato, non l'accuratezza dell'interpretazione linguistica.
FORM_ONLY e SOURCE_ONLY conservano il limite di otto evidenze; MIXED ha i budget
per gruppo descritti sopra. Un riassunto può non coprire tutto un modulo lungo.
Non viene eseguita OCR sulle immagini né indicizzazione di intestazioni,
piè di pagina e note esterne al corpo DOCX. L'estrazione dei requisiti può essere
parziale e le associazioni testuali prudenti possono lasciare un valore non
verificato anche quando esiste nelle fonti; non è un audit dell'archivio.
Il falso negativo del numero di albo 8421 è stato riprodotto e corretto sul lato
SOURCE. Le equivalenze testuali gestite restano conservative, non un verificatore
semantico universale. Raggruppamenti, estratti e proposte del modello possono
ancora essere incompleti. Le domande generali possono recuperare sezioni e
condizioni diverse: non certificano che il modulo possa essere completato senza
ulteriori informazioni. Non occorre reindicizzare per queste modifiche SOURCE.

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
