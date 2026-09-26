# Compilazione assistita DOCX

Il backend riceve un modello Word, propone i campi e i valori usando DeepSeek,
valida le proposte e restituisce un **DOCX parzialmente compilato** con report
JSON. Il percorso e collegato alla schermata **Template**, nel formato Word.

## Dall'interfaccia

1. Aprire il progetto, poi **Preparazione candidatura > Template**.
2. Lasciare **Formato: Word (.docx)** e scegliere **Carica modello**.
3. Aggiungere eventuali indicazioni e premere **Compila Word**. Il solo caricamento
   non avvia chiamate al modello e non aggiunge il modulo alla KB.
   Specificare modalita di partecipazione, sottoscrittore e sezioni da compilare
   quando queste scelte non sono gia nei Dati del progetto.
4. Consultare campi inseriti, mancanti, proposte bloccate, citazioni e avvisi.
   Il report e consultabile, non un editor Word o una certificazione di verifica.
5. Scaricare **Word compilato**, **Report JSON** o **Modello originale**.

All'apertura il Template mostra **Nuova compilazione**, senza aprire un vecchio
risultato. La scheda **Compilazioni salvate** contiene lo storico, raggruppato
per nome del modello; data e ID distinguono le singole compilazioni, anche di
file omonimi. Ogni risultato ha originali, output e report separati.
**Reimposta compilazione** (icona freccia circolare accanto a Compila Word)
azzera file, indicazioni ed errori del tentativo, dopo conferma, senza cancellare
lo storico. Il semplice cambio di scheda conserva invece gli input non inviati.
Un errore di generazione resta nella scheda nuova compilazione e non viene
mostrato sopra il report di una generazione precedente.

**Riutilizza modello** riprende l'originale e le indicazioni di una
compilazione; una nuova generazione crea un altro risultato, senza sovrascrivere
il precedente, e apre la scheda dei risultati. Il file selezionato e le indicazioni non sono salvati prima della
generazione: in caso di errore restano disponibili nella schermata per riprovare.
Le modifiche al documento compilato si effettuano nel Word scaricato.

Il precedente flusso Markdown e ancora disponibile scegliendo **Testo (.md / .txt)**.
I vecchi collegamenti al Draft aprono direttamente quel percorso. PDF e DOC
binari non sono supportati dal nuovo caricamento.

## Come funziona

1. `docx_templates.py` legge il DOCX con `python-docx`, controlla il pacchetto e
   cataloga celle vuote e segnaposti nei paragrafi, anche nei moduli misti.
   Le coordinate delle celle sono XML fisiche, non una griglia che duplica le
   celle unite. I segnaposti hanno intervalli precisi nel testo del paragrafo.
2. `document_compilation.py` seleziona fonti del progetto, Company KB e General
   KB. I dati estratti con provenienza sono disponibili senza approvazione manuale;
   i dati esclusi non vengono indicizzati. I dati inseriti per il progetto restano
   distinguibili dalle sintesi automatiche. Template e draft non diventano evidenze aziendali.
3. Il prompt dedicato `docx-fields-v11-compact-json` chiede campi, valori, fonte,
   citazione letterale, stato e motivazione in gruppi da massimo 32 elementi.
   Il contesto del modulo e le fonti rimangono disponibili in ogni gruppo, ma
   soltanto gli ID assegnati sono scrivibili. **La mappa manuale Catanzaro non viene letta
   dal codice di produzione**: viene usata soltanto nei test del writer.
4. Il backend rifiuta JSON non interpretabile, campi sconosciuti/duplicati e
   contratti di scrittura incoerenti. Le proposte per candidati validi esterni
   al gruppo vengono scartate e registrate, senza autorizzare scritture.
   Una citazione inesistente
   o un valore non presente nella citazione blocca invece il singolo campo.
   Dopo il primo passaggio, un solo tentativo mirato puo correggere queste
   proposte; quelle ancora non valide restano vuote e segnalate nel report.
5. Il writer inserisce le proposte ammesse in una copia del modello. Conserva
   tutte le parti ZIP diverse da `word/document.xml` byte per byte, incluse
   immagini, note, intestazioni e relazioni. Aggiunge un avviso di bozza e rende
   espandibili le righe compilate che avevano altezza fissa.
   Nei paragrafi sostituisce solo i segnaposti, anche se divisi fra piu run Word,
   mantenendo testo circostante e formattazione; il valore eredita lo stile del
   primo pezzo del segnaposto. Le sostituzioni procedono da destra a sinistra.
6. Originale, bozza e report sono conservati nel progetto sotto
   `MAPI_STORAGE_PATH/<project_id>/_compilations/<run_id>/`, con record SQLite
   separato. **Non vengono aggiunti agli indici RAG.**

La compilazione DOCX e un percorso separato dal generatore Markdown. Entrambi
possono utilizzare i dati estratti senza una verifica preventiva obbligatoria.
Il prompt distingue requisiti del bando da dichiarazioni del proponente:
la presenza di un requisito non certifica che l'azienda lo possieda.
La versione v5 ha aggiunto le indicazioni utente alle fonti citabili e isolato gli
errori di evidenza per campo; i report gia salvati mantengono la versione del
prompt con cui sono stati prodotti.

### Campi logici e recapiti (v6)

Il parser unisce puntini ASCII ed ellissi Unicode nella stessa area, anche tra
run Word diversi. Non unisce campi separati da etichette, tab, interruzioni di
riga o barre delle date. Conserva il punto e lo spazio delle abbreviazioni
come `prov. ....` e `n. ....`. Non ci sono coordinate o nomi di bandi nel parser.

Il catalogo segnala `value_type=email` quando lo riconosce dall'etichetta vicina,
dal segnaposto nominato o dall'intestazione della colonna. Il modello non puo
disattivare questo controllo cambiando l'etichetta nella risposta. Anche un
campo classificato email dal modello viene controllato.

Si usa [email-validator](https://github.com/JoshData/python-email-validator)
con `check_deliverability=False`: niente DNS, invio di messaggi o verifica della
titolarita/qualifica PEC. Si mantiene il valore letterale, senza normalizzarlo.
Recapiti incompleti o sintatticamente invalidi vengono bloccati (`invalid_email`),
cosi come un indirizzo valido ricavato ritagliandone uno piu lungo nella citazione
(`partial_email_evidence`). Rientrano nell'unico tentativo di correzione esistente;
se ancora errati restano vuoti. Il writer ripete il controllo sintattico sui
campi tipizzati prima di sostituire il segnaposto o riempire la cella.

Un recapito esplicitamente diviso come `___@___.___` non e ricomposto automaticamente:
le parti riconosciute sono `email_parts`, bloccate con `unsupported_email_layout`
e da completare manualmente. E' preferibile non scriverle che inserire indirizzi
completi dentro ogni frammento. Formati misti o ambigui non riconosciuti restano
un limite: non esiste una validazione semantica generale di tutti i campi.

Non cambiano retrieval, budget, modello, scelta dei rami o workflow. I risultati
precedenti rimangono invariati; le correzioni si applicano alle nuove compilazioni.

### Integrita dei numeri e codici nelle evidenze (v7)

Il validatore blocca `1234567890` se proviene da `01234567890`, oppure `ABC123`
se ritagliato da `ABC123Z`. Il controllo si applica ai token alfanumerici che
contengono cifre, indipendentemente dall'etichetta restituita dal modello.
Vengono controllati i confini del token nel testo della fonte, anche se la
citazione restituita contiene soltanto la parte troncata. Un'occorrenza del
valore altrove nel frammento, fuori dalla citazione, non basta.

Il codice `partial_numeric_evidence` lascia il campo vuoto e ammette l'unico
tentativo di correzione gia previsto. Non completa automaticamente zeri o
prefissi: il modello deve proporre un valore supportato, oppure astenersi.
Un codice completo viene mantenuto letteralmente, inclusi gli zeri iniziali.

Questo e un controllo lessicale, non una validazione fiscale o semantica.
Non interpreta codici composti, importi decimali o requisiti. I componenti di
una data delimitati da barre restano utilizzabili nei rispettivi segnaposti.
Il writer non riceve fonti: questo controllo viene eseguito dal validatore
prima della scrittura. I risultati salvati con versioni precedenti rimangono
invariati; la versione del prompt distingue le nuove compilazioni.

### Provenienza e correzioni limitate

Le indicazioni non vuote sono una fonte separata `user:instructions`, con
`scope=user`, `source_kind=user_instructions` e `origin=user`. Non hanno
documento, pagina o frammento e non incrementano la copertura dei chunk indicizzati.
I dati inseriti per il progetto hanno anch'essi origine `user`; i dati estratti
hanno origine `extracted`, le fonti documentali `document`. Dichiarare un dato
non equivale a verificarlo documentalmente, ne autorizza firme o attestazioni.

Una proposta con fonte sconosciuta, citazione non letterale, valore non contenuto
nella citazione, numero/codice ritagliato o recapito non valido diventa
`needs_review`, con `written_value=null`. Il report
conserva `validation_codes`, `validation_notes` e `rejected_evidence`: una
citazione rifiutata non compare tra le evidenze valide. Anche una sola citazione
errata aggiunta a una valida blocca quella proposta, non le altre.

Soltanto queste proposte sono ammesse a **una correzione per campo**, dopo aver
eseguito tutti i gruppi iniziali. Il modello riceve errori, proposta e stesse
fonti, e puo modificare valore e citazioni, non ID, etichetta, soggetto o tipo.
I controlli vengono ripetuti integralmente. Nessun confronto fuzzy su accenti,
numeri o codici: la correzione deve copiare il valore letterale dalla fonte.
Campi gia accettati, firme, scelte e dichiarazioni non vengono rigenerati.

`repair` conserva proposta iniziale, eventuale risposta e stato
`corrected`/`unresolved`. Se il tentativo omette il campo, fallisce, cambia
identita o non supera i controlli, rimane bloccato. Un errore strutturale nel
JSON di correzione resta invece bloccante per l'intero documento.

Due normalizzazioni non autorizzano scritture: per i soli campi con stato diverso
da `proposed` e `value=null`, una lista `evidence` omessa diventa vuota e
un'etichetta testuale vuota viene mostrata con la coordinata del campo. Non
vengono inventati significati o fonti; tipi errati e ID sconosciuti restano errori.

### Risposte lunghe e gruppi di campi

La generazione usa chiamate sequenziali, ciascuna limitata a 12.000 token di
output. Nel passaggio iniziale, se il servizio termina con `finish_reason=length`, la risposta viene
scartata senza tentare di riparare il JSON; solo quel gruppo viene diviso a meta
e riprovato. I gruppi gia completati non vengono rigenerati. Errori strutturali
(JSON non valido, ID sconosciuti, non scrivibili o duplicati) e filtri del servizio
interrompono la compilazione.
Una correzione troncata non viene suddivisa o ripetuta: il campo resta bloccato.

Se la risposta include un campo esistente ma esterno a `target_ids`, quella
proposta viene scartata senza interrompere le altre: non autorizza scritture,
classificazioni o correzioni. Il campo puo essere trattato soltanto nella chiamata
del proprio gruppo; se li viene omesso resta vuoto e non classificato. Non viene
riassegnato un ID e non si riusa la proposta scartata in chiamate successive.
La stessa regola vale durante le correzioni, che non possono modificare campi
gia accettati. Non sono aggiunte chiamate al modello per questo caso.

Il report conserva le proposte fuori gruppo in `rejected_proposals`, con
`validation_code=outside_batch`, proposta originale, ID autorizzati, numero
di chiamata e fase (`initial`/`repair`). Un avviso riassuntivo compare nella UI;
`execution.out_of_batch_proposals` ne conta le occorrenze, non i campi unici.
I controlli su formato, duplicati, fonti, valori e firme restano attivi. Questa
gestione riguarda i gruppi tecnici, non l'applicabilita semantica delle sezioni.

Limiti: massimo 40 chiamate complessive, 180 secondi per chiamata e 600 secondi
per l'elaborazione dei gruppi, correzioni incluse. Se il budget di chiamate e
esaurito, le correzioni opzionali non vengono eseguite. Anche un singolo campo
ancora troncato nel passaggio iniziale interrompe il processo. DOCX e record
vengono creati solo dopo il completamento del passaggio iniziale e dei controlli:
possono contenere campi bloccati lasciati vuoti, non gruppi mai elaborati.

Un gruppo puo contenere solo elementi decorativi e restituire `fields=[]`:
rimangono visibili tra gli elementi non classificati. Se tutti i gruppi sono
vuoti, non viene prodotto un file. I controlli su fonti, firme e valori restano
invariati. La suddivisione non garantisce correttezza semantica o completezza.

Il report include `execution` con dimensione dei gruppi, chiamate effettuate,
gruppi completati, risposte troncate, richieste di correzione e campi corretti,
tentati o saltati. `total_tokens` somma anche correzioni e tentativi troncati,
oppure e `null` se il servizio non fornisce tutti i consumi, inclusi errori del
provider durante la correzione. Moduli
grandi richiedono piu chiamate e possono costare di piu e impiegare alcuni minuti.

## Modelli con paragrafi

Sono riconosciuti segnaposti espliciti come:

```text
Il sottoscritto ______, nato a ______ il ___/___/______.
Sede in ______ (__) e provincia di residenza ( __ ).
Societa: {{ragione_sociale}}. Sede: [INSERIRE SEDE LEGALE].
Luogo: ........; data: ........
```

Supporto: almeno tre underscore (anche separati da spazi), due underscore
racchiusi tra parentesi come `(__)` o `( _ _ )`, almeno quattro punti,
almeno due caratteri ellissi consecutivi, `{{campo}}`, `[DA COMPILARE]`,
`[INSERIRE ...]`, `[INDICARE ...]`. I tre puntini di una frase normale non sono
trattati come campi. Piu segnaposti nella stessa frase restano distinti.
Le sequenze di due underscore dentro parole o fuori dalle parentesi non sono
nuovi campi. Le parentesi e gli spazi circostanti sono preservati dal writer.

Un esempio sintetico pronto da caricare si trova in
`demo-documents/modelli/modulo-paragrafi.docx`. Non e un modulo ufficiale.
Per rigenerarlo in un percorso nuovo, da `backend`:

```bash
.venv/bin/python -m scripts.create_paragraph_template --output /tmp/modulo-paragrafi.docx
```

Dal report v2, `cell_id` identifica anche i paragrafi per compatibilita: `p3.s0`
identifica il primo segnaposto del quarto paragrafo XML nel modello originale.
`location` espone tipo e posizione; non e un numero di pagina. La numerazione
comprende anche i paragrafi delle tabelle e precede l'inserimento dell'avviso di
bozza. `unclassified_fields` include celle e segnaposti non classificati;
`unclassified_cells` resta disponibile per le sole celle. La UI legge anche i
vecchi report v1/v2; le nuove compilazioni producono lo schema v3 con provenienza,
proposte rifiutate e traccia delle correzioni. `unsupported_locations` segnala i paragrafi esclusi per
controlli Word o contenuti complessi: non implica una verifica di completezza.

### Campi corti e ripristino del prompt (v9)

La v8 aveva aggiunto istruzioni su componenti dell'indirizzo, ruoli aziendali,
scelte mancanti e coerenza delle sezioni. La successiva compilazione Minervino
ha prodotto due sole scritture, entrambe nel ramo studio associato non confermato,
bloccando anche l'anagrafica generale per mancanza della scelta di partecipazione.
Il report contava zero proposte respinte dal validatore: era il modello a
classificare quasi tutti i campi come `needs_review`.

La v9 ripristina le istruzioni della v7 e mantiene la correzione del parser.
Una sola esecuzione non misura la qualita generale delle versioni, ma l'esito
osservato non giustifica mantenere il cambiamento al prompt come miglioramento.
I problemi semantici della v7 rimangono aperti; il ripristino non garantisce
di riprodurre il precedente numero di scritture.

La correzione del parser e verificabile senza LLM: il modulo Minervino
espone anche le tre province iniziali, passando da 184 a 187 segnaposti.
Non vengono aggiunte coordinate o dati specifici del bando al codice di
produzione; le coordinate del caso reale sono usate solo nei test di regressione.
Gli ID vengono ricalcolati durante ogni nuova analisi del modello: i report
precedenti restano associati alla compilazione e alla versione che li ha prodotti.

### Riduzione del contesto duplicato (v10, successivamente ritirata)

L'esperimento descritto sotto e stato verificato con compilazioni reali e poi
ritirato: la versione corrente mantiene soltanto il JSON compatto (v11).

La v10 conserva le istruzioni della v9 e rende piu compatto il payload JSON:

- nel catalogo dei paragrafi invia `text_with_fields` e i segnaposti originali,
  omettendo la copia ridondante `text`. Il testo originale e ricostruibile dai
  dati inviati; il catalogo interno del parser rimane invariato;
- elimina gli spazi di separazione del JSON, conservando quelli nei valori,
  nelle fonti, nelle citazioni e nelle indicazioni utente.

Rimangono disponibili il testo completo del modulo, i contesti adiacenti,
tutte le fonti selezionate e i metadati. Restano invariati i gruppi da 32 campi,
i budget, i controlli e il tentativo di correzione. La riduzione si applica
anche alle richieste di correzione, senza cambiare i dati da correggere.

Misura offline del 22 settembre 2026 sui due modelli e sulle fonti correnti,
con titolo del progetto salvato e indicazioni utente vuote. La tabella somma
i caratteri dei messaggi utente di tutti i gruppi iniziali; esclude il messaggio
di sistema, le risposte ed eventuali correzioni o tentativi troncati. Il confronto
ricostruisce la serializzazione v9 sugli stessi dati della v10.

| Caso | Gruppi | Caratteri prima | Caratteri dopo | Riduzione |
| --- | ---: | ---: | ---: | ---: |
| Minervino | 8 | 1.557.492 | 1.389.182 | 10,81% |
| Catanzaro | 9 | 2.068.424 | 1.998.647 | 3,37% |

Includendo i 6.193 caratteri del messaggio di sistema ripetuti per chiamata,
le riduzioni sono rispettivamente 10,47% e 3,28%. Le fonti selezionate sono
52 frammenti e 58.874 caratteri per Minervino, 92 frammenti e 106.718 caratteri
per Catanzaro. Queste sono misure di caratteri, **non di token del provider**:
non e stata effettuata una nuova compilazione a pagamento. I test verificano
la conservazione dei dati nei prompt iniziali e di correzione dei due modelli;
non dimostrano equivalenza delle risposte dell'LLM o migliore interpretazione.
Le fonti continuano a essere ripetute in ogni gruppo: il costo principale resta.

Verifica della v10: 378 test backend superati con risposte del provider simulate;
Ruff e `git diff --check` senza errori.

### Verifica reale e versione conservativa (v11)

Le compilazioni live v10 hanno confermato meno token di input, ma Catanzaro
ha prodotto nove scritture aggiuntive nei rami 5.e e 5.f non confermati.
Sul solo gruppo interessato, il riferimento v9 e la variante con il solo JSON
compatto non hanno scritto quei campi. Una prova per configurazione non
isola la variabilita del modello: la rimozione di `paragraph.text` e stata
ritirata per prudenza, senza attribuirle una causalita dimostrata.

La versione **`docx-fields-v11-compact-json`** ripristina il catalogo integrale
dei paragrafi. Rispetto alla v9 cambia soltanto la serializzazione JSON,
con `separators=(",", ":")`. Tutti i dati, le stringhe, le istruzioni, i gruppi
e i controlli restano presenti. Le richieste reali, comprese le correzioni,
sono state confrontate con il builder precedente: dopo il parsing JSON i
payload risultano uguali.

| Caso | Token input primo gruppo, riferimento v9 | Token input primo gruppo v11 | Riduzione input | Token totali compilazione v11 | Campi scritti |
| --- | ---: | ---: | ---: | ---: | ---: |
| Minervino | 47.808 | 44.360 | 7,21% | 418.249 | 19 |
| Catanzaro | 73.594 | 69.073 | 6,14% | 642.207 | 22 |

La misura di input usa il contesto esatto del primo gruppo, stesso modello e
stesse istruzioni. La richiesta di riferimento ha risposta limitata a un token
e non genera una bozza. I totali delle compilazioni includono input e output,
compresa una correzione Minervino; escludono le chiamate di misura e diagnosi.
Non si tratta di una misura del risparmio monetario o della qualita generale.

Le nuove bozze sono registrate nei progetti. Catanzaro conserva gli stessi
22 campi e valori della precedente v9; persistono le scritture in sezioni
non confermate. Minervino scrive la provincia iniziale, ma conserva errori
di indirizzo e scrive recapiti anche nei rami associati non confermati.
L'integrita ZIP, i testi prestampati, le scritture e le evidenze sono stati
verificati; non e stato controllato il rendering in Word. Sulla v11 sono
passati 378 test backend, Ruff e `git diff --check`.

Risultati, differenze semantiche, consumi delle prove e file prodotti sono in
[Verifica token e compilazioni](../../verifica-token-compilazione.md).

## Provare il caso Catanzaro senza modificare i propri dati

Dalla directory `backend`, con dipendenze installate tramite `uv sync`:

```bash
.venv/bin/python -m scripts.compile_docx_demo --live
```

Il flag `--live` autorizza **vere chiamate API a consumo**, una per gruppo ed
eventuali tentativi sui gruppi troncati o sulle proposte correggibili. Occorre
`DEEPSEEK_API_KEY`; modello e URL seguono le impostazioni esistenti in `.env`.
Lo script crea un database temporaneo, carica bando e disciplinare pubblici e
visura Mapi simulata, poi conserva i tre risultati in
`backend/data/docx-demo/<timestamp>/`. Non serve un server e non tocca i progetti
o la KB dell'applicazione. `--output <nuova-directory>` cambia la destinazione;
una directory esistente non viene sovrascritta.

`--company-file ../demo-documents/generalita-mapi.md` usa la scheda aziendale
simulata ampliata invece della visura predefinita, sempre nel database isolato.

La visura e inventata e successiva alla gara: **non prova requisiti reali**.
Anche identificativi presenti nella fonte possono essere fittizi o formalmente
non validi. Il controllo di citazione non e una verifica fiscale o camerale.

## API per un progetto esistente

Avvio, dalla directory `backend`:

```bash
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger: `http://127.0.0.1:8000/docs`, sezione **Compilazione DOCX**.
Se la porta e gia occupata, riutilizzare il backend attivo aggiornato oppure
scegliere un'altra porta.

| Metodo | Percorso | Risultato |
| --- | --- | --- |
| POST | `/api/projects/{project_id}/document-compilations` | Genera una nuova bozza, restituisce report e link |
| GET | `/api/projects/{project_id}/document-compilations` | Ultime 100 compilazioni del progetto |
| GET | `/api/projects/{project_id}/document-compilations/{run_id}` | Report della compilazione |
| GET | `/api/projects/{project_id}/document-compilations/{run_id}/download/docx` | DOCX compilato |
| GET | `/api/projects/{project_id}/document-compilations/{run_id}/download/report` | Report JSON |
| GET | `/api/projects/{project_id}/document-compilations/{run_id}/download/template` | Originale caricato |

Il POST accetta multipart `file` e, opzionalmente, `instructions` (massimo 4.000
caratteri). Le istruzioni possono specificare ramo societario, partecipazione
singola o associata e perimetro della bozza, oppure dati esplicitamente dichiarati
dall'utente. Questi ultimi sono citabili come tali, non come prove documentali.
Esempio dalla radice del repository, sostituendo l'ID con un progetto esistente:

```bash
curl -f http://127.0.0.1:8000/api/projects/ID_PROGETTO/document-compilations \
  -F 'file=@demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx' \
  -F 'instructions=Compila soltanto i dati anagrafici. Segnala ogni dato mancante.'
```

Gli errori non producono una compilazione persistita: 404 progetto assente,
413 dimensioni eccessive, 415 formato diverso da DOCX, 422 modello non supportato,
503 chiave assente, 502 risposta del modello non utilizzabile. Dopo la generazione
viene ricontrollata l'esistenza del progetto, anche in caso di cancellazione
durante la chiamata. La cancellazione del progetto elimina record e file locali.

## Report e limiti espliciti

Ogni campo riporta `cell_id`, etichetta, soggetto, tipo, stato, proposta originale,
`written_value`, citazioni, motivi di blocco ed eventuale traccia della correzione.
`blocked_field_count` distingue le proposte respinte dai dati mancanti. La UI
mostra **Bloccato** e distingue i dati dichiarati dall'utente dalle altre fonti.
La proposta puo essere visibile nel
report anche quando non e stata scritta nel DOCX. `ready_for_submission` e sempre
`false`: questa versione produce bozze, non pratiche validate o firmate.

- Supporto: DOCX con celle vuote o segnaposti nei paragrafi del corpo, massimo
  20 MB, 40 MB decompressi, 400 elementi candidati complessivi. Non PDF, DOC
  binari, riscrittura narrativa libera, macro,
  allegati incorporati, revisioni pendenti o documenti protetti.
- Spazi bianchi senza segnaposti, controlli modulo Word, caselle di testo,
  paragrafi con hyperlink/oggetti complessi, intestazioni, pie di pagina e note
  non vengono compilati. Se non esistono campi supportati, il backend risponde
  422 prima di chiamare il modello. In un modulo misto compila solo le parti
  supportate e segnala le esclusioni rilevate.
- Caselle Word, firme e dichiarazioni non vengono compilate automaticamente.
  Le dichiarazioni gia stampate restano nel file e richiedono conferma umana.
- L'individuazione dei segnaposti e deterministica, la loro interpretazione
  semantica e probabilistica. Celle o linee decorative possono essere scambiate
  per campi; gli elementi omessi rimangono in `unclassified_fields` per il
  controllo. Non si deve interpretare il conteggio dei mancanti come una
  certificazione di completezza del modulo.
- Verificare soggetto, ramo applicabile, validita temporale e conflitti: una
  citazione autentica puo essere usata in modo semanticamente sbagliato.
  L'applicabilita resta affidata al modello: la correzione mirata delle evidenze
  non introduce un controllo deterministico dei rami.
- Il primo writer accetta valori estrattivi, non parafrasi o concatenazioni
  arbitrarie. Per esempio, una qualifica riformulata dal modello puo essere
  bloccata anche se plausibile. Questo comportamento e visibile nel report.
- La selezione riusa il campionamento distribuito gia impiegato nell'estrazione:
  budget di 40.000 caratteri Company, 90.000 progetto, 20.000 General. Non e un
  nuovo retriever vettoriale ne un benchmark FTS5. La copertura parziale e
  dichiarata: "mancante" significa non trovato nelle fonti selezionate.
- L'indice attuale conserva frammenti, non pagine. Il report restituisce il
  numero di frammento e `page: null`, senza inventare riferimenti di pagina.
- Il testo scritto puo cambiare l'impaginazione; controllare Word o un rendering
  PDF. La conversione iniziale DOC -> DOCX del caso Catanzaro aveva gia spostato
  alcune note: preservarle non risolve quel limite preesistente.
- Nessun ciclo autonomo di strumenti, firma, invio al portale o validazione
  amministrativa. E una pipeline controllata con chiamate LLM dedicate a gruppi di campi.

## Verifiche eseguite

```bash
cd backend
.venv/bin/pytest -q -p no:cacheprovider
.venv/bin/ruff check --no-cache .
```

La suite comprende parsing DOCX/JSON, citazioni, celle unite, controllo firme,
download, originali invariati, esclusione degli output dal retrieval, separazione
fra progetti, rollback su errore e cancellazione durante la generazione.
L'estensione ai paragrafi comprende prove con frammentazione casuale dei run,
segnaposti ripetuti, stili diversi, moduli misti, controlli estesi su piu paragrafi,
caratteri XML, firme e compatibilita del modulo Catanzaro. Le prove non misurano
l'accuratezza del riconoscimento semantico dei campi da parte del modello.
Le risposte del modello nei test sono simulate, senza consumo API.
Le regressioni per i gruppi coprono tutti i 279 candidati del modulo Catanzaro,
risposte troncate e suddivisione, limiti di tempo/tentativi, gruppi decorativi,
scritture fuori gruppo, consumi aggregati e assenza di salvataggi parziali.
I test di correzione usano anche moduli sintetici indipendenti, coordinate
spostate e paragrafi: coprono provenienza utente, blocchi locali, singolo tentativo,
budget, fallimenti e impossibilita di riabilitare firme o dichiarazioni.

La UI ha test su upload multipart, errori recuperabili, storico, download,
citazioni, navigazione con modifiche pendenti e risultati asincroni obsoleti.
I test browser `docx-template.spec.ts` e `template-workflow.spec.ts` verificano
il nuovo percorso Word e quello testuale su desktop e mobile; le risposte di
compilazione sono simulate, non una nuova valutazione della qualita del modello.

Il 15 settembre 2026 e stata eseguita anche una prova reale separata sul modulo
Catanzaro: modello restituito dal provider `deepseek-flash`, 13 celle scritte,
report generato, 80 frammenti selezionati su 179, 66.071 token totali dichiarati.
Due proposte riformulate sono state bloccate dal controllo letterale. Alcune
righe decorative sono state segnalate dal modello come campi mancanti: e un
limite emerso dalla prova, non un risultato da nascondere nei conteggi.
Il rendering locale e rimasto di 17 pagine; le pagine con anagrafica e direttore
tecnico sono state ispezionate visivamente. **Questo e uno smoke test del flusso,
non una misura di accuratezza o una dimostrazione di affidabilita generale.**

Il 16 settembre 2026, dopo la suddivisione in gruppi, una nuova prova reale
isolata sullo stesso caso ha completato 9 chiamate senza troncamenti, generando
DOCX e report (`backend/data/docx-demo/20260916-084241/`). Il provider ha riportato
636.402 token totali, inclusi gli input ripetuti: la suddivisione riduce il rischio
di troncamento dell'output, non il costo del contesto. Sono stati scritti 26 campi;
questo numero **non equivale a 26 compilazioni semanticamente corrette**.

L'ispezione del report ha rilevato proposte anche nella sezione 5.e, nonostante
le indicazioni limitassero la prova alla prima tabella e alla 5.d. Inoltre il
modello ha classificato tutti i candidati, incluse celle potenzialmente decorative.
Il controllo letterale ha bloccato una qualifica riformulata, ma non certifica
l'applicabilita delle sezioni. Il test conferma la risoluzione del blocco per
risposte lunghe, non risolve questi limiti semantici. Il documento e stato
riaperto programmaticamente; non e stato effettuato un nuovo rendering Word/PDF.

Riferimenti tecnici: [python-docx, gestione dei documenti](https://python-docx.readthedocs.io/en/latest/user/documents.html),
[tabelle e celle unite](https://python-docx.readthedocs.io/en/latest/user/tables.html),
[DeepSeek JSON output](https://api-docs.deepseek.com/guides/json_mode/).
