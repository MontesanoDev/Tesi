# Compilazione assistita: stack, funzionamento e limiti

Stato del codice verificato il **17 settembre 2026**. Documento riferito al prototipo attuale, non a funzionalita' pianificate.

## 1. Che cosa abbiamo per le mani

Un'applicazione che consulta fonti documentali e prepara una **bozza di un modulo Word**, usando informazioni del progetto e dell'azienda. Il percorso e' collegato alla UI: caricamento modello, compilazione, report, storico e download.

**Non e' un compilatore universale di bandi, non compila qualunque PDF e non certifica una candidatura.** Il risultato richiede controllo finale, anche quando tutte le scritture hanno superato i controlli del codice.

Il bando e il modello da compilare sono oggetti distinti:

- **Bando e allegati:** fonti che descrivono procedura, requisiti, scadenze e istruzioni.
- **Documenti aziendali:** fonti dei dati del concorrente e delle persone coinvolte.
- **Modello DOCX:** documento vuoto sul quale inserire i valori. Non diventa automaticamente una fonte della KB.
- **Output:** copia parzialmente compilata del modello, accompagnata da un report.

## 2. Stack effettivamente utilizzato

| Componente | Tecnologia | Ruolo nel progetto |
|---|---|---|
| Interfaccia | React 19, TypeScript, Vite, React Router | Gestione progetti, fonti, modelli, risultati e download. |
| Componenti visivi | CSS e Lucide | Layout, controlli e icone; non intervengono nella compilazione. |
| Backend | Python >= 3.14, FastAPI, Uvicorn | API, coordinamento delle operazioni, validazione e gestione file. |
| Persistenza | SQLite e filesystem locale | Metadati e record nel DB; originali, bozze e report su disco. |
| Ricerca nella chat | SQLite FTS5/BM25 e riordinamento euristico applicativo | Recupero lessicale dei frammenti; non e' un reranker neurale. |
| Lettura delle fonti PDF | `pypdf` | Estrazione del testo esistente nel PDF, senza OCR. TXT e Markdown sono letti direttamente. |
| Lettura e scrittura Word | `python-docx`, XML tramite `lxml`, `zipfile` | Analisi del DOCX e modifica delle sole posizioni ammesse in una copia. |
| Modello linguistico | API DeepSeek, chiamate HTTP tramite `httpx` | Classificazione dei campi e proposta di valori, citazioni e motivazioni in JSON. |
| Contratto delle risposte | Pydantic e controlli Python | Validazione della struttura JSON, degli identificativi e delle evidenze. |
| Test | pytest, Vitest/Testing Library, Playwright | Test backend, componenti UI e percorsi browser. |

Il modello e' configurato tramite `DEEPSEEK_MODEL`; il default nel codice e' `deepseek-v4-flash`. Il report conserva il nome restituito dal provider: non va confuso il nome configurato con una garanzia di versione immutabile. Le chiavi API rimangono nel backend.

Non sono attualmente usati embedding, vector database, ricerca ibrida, RRF o framework come LangChain/Haystack. L'orchestrazione e' codice applicativo Python.

## 3. Chi fa cosa nella compilazione

```text
Fonti indicizzate + dati aziendali + eventuali dati della candidatura
                              |
Modello DOCX -> catalogo di celle/segnaposti -> selezione delle fonti
                              |
                   DeepSeek propone campi e valori
                              |
                  Python valida le proposte ricevute
                              |
                   Writer DOCX -> bozza + report
```

1. **Il parser Python trova le posizioni candidate.** Usa struttura XML e regole sui segnaposti: non comprende da solo il significato amministrativo di ogni campo. Una cella vuota puo' essere decorativa.
2. **Il modello interpreta quelle posizioni.** Decide quali sono campi effettivi, a quale soggetto si riferiscono e quale valore proporre dalle evidenze. Questa parte non e' deterministica.
3. **Il codice controlla e scrive.** Il modello non produce direttamente il file Word e non puo' scegliere liberamente dove modificare il documento.

Il system prompt dedicato (`docx-fields-v6-logical-fields`) distingue azienda, persone, amministrazione e progetto; richiede evidenze e indica come trattare mancanti, firme e dichiarazioni. Sono istruzioni al modello, non una prova automatica di correttezza.

**E' una pipeline guidata da LLM, non un agente autonomo** che naviga siti, sceglie strumenti, firma o presenta una domanda. Non effettua fine-tuning: fornisce contesto al modello a ogni richiesta.

## 4. Chat, estrazione e compilazione non recuperano le fonti allo stesso modo

| Percorso | Come usa le fonti |
|---|---|
| Chat | Ricerca FTS5/BM25 sulla domanda, riordinamento euristico e possibile aggiunta dei frammenti vicini. |
| Dati estratti, ex Call Facts | Legge una selezione dei frammenti originali del progetto e produce una sintesi strutturata. |
| Compilazione Word | Carica fonti del progetto e KB globali entro budget separati. Oltre i budget seleziona frammenti distribuiti nel corpus, **non quelli classificati come piu' rilevanti per ogni campo**. |

Questa distinzione e' importante: **la compilazione non usa ancora un retrieval mirato per campo, ne' esegue una ricerca aggiuntiva quando manca un dato.** Un'informazione presente nell'indice puo' non essere inclusa nel contesto inviato al modello.

Il contesto delle fonti e del modulo viene ripetuto nei gruppi di compilazione. Questo aiuta a conservare il contesto, ma aumenta i token consumati.

### Ruolo dei dati del progetto

- **Dati estratti:** sintesi derivate dal bando. Non aggiungono conoscenza esterna e non sono necessarie per rendere accessibili le fonti originali. Possono essere utili come riepilogo, ma il loro beneficio sulla compilazione non e' stato misurato.
- **Dati inseriti:** informazioni o scelte specifiche della candidatura non presenti nelle fonti, ad esempio il referente scelto o la modalita' di partecipazione. Non certificano requisiti o poteri di firma.
- **Indicazioni della compilazione:** fonte citabile separata `user:instructions`, con origine utente, senza documento o frammento fittizio. Non vengono attribuite a un documento diverso ne conteggiate come chunk indicizzati.
- **Company KB:** informazioni aziendali riutilizzabili. **General KB:** conoscenza tecnica condivisa, non prova anagrafica del concorrente.

La compilazione puo' procedere senza preventiva estrazione o approvazione manuale dei facts. I dati estratti restano una rappresentazione aggiuntiva, con possibili omissioni e interpretazioni errate. "40 estratti" non significa "40 informazioni corrette e complete".

## 5. Formati e strutture supportate

| Caso | Stato attuale |
|---|---|
| PDF con testo, TXT, Markdown come fonti | Supportati dall'ingestion. La corretta lettura del contenuto va comunque controllata. |
| PDF scannerizzato come fonte | Nessun OCR integrato. Se non contiene testo estraibile viene rifiutato; un PDF misto puo' perdere le parti solo immagine. |
| Modello `.docx` con celle vuote | Supportato per le celle considerate scrivibili dal parser. |
| DOCX con segnaposti nei paragrafi | Supportati marcatori come `___`, `....`, `{{campo}}`, `[DA COMPILARE]`, `[INSERIRE ...]`. |
| DOCX con soli spazi vuoti o struttura arbitraria | Non e' garantito il riconoscimento; senza posizioni supportate la compilazione viene rifiutata. |
| Controlli Word, caselle di testo e contenuti complessi | Non gestiti come campi compilabili generici. Le aree non supportate restano invariate. |
| Intestazioni, pie' di pagina e note | Conservati, ma non compilati. |
| Modelli PDF, vecchi `.doc`, moduli web | Non supportati dal compilatore Word. Nessuna conversione automatica o compilazione AcroForm. |

La disponibilita' del caricamento DOCX in Template **non significa** che l'ingestion della KB accetti Word: sono due percorsi separati. Esiste anche il precedente percorso di generazione testuale Markdown, distinto dalla compilazione DOCX.

Il writer conserva il contenuto delle parti ZIP diverse da `word/document.xml`, incluse immagini e intestazioni. Modifica il corpo, aggiunge l'avviso di bozza e permette l'espansione delle righe compilate. **Non garantisce la stessa impaginazione finale:** valori lunghi possono cambiare righe, pagine e disposizione del testo.

## 6. Controlli reali e loro limiti

Il backend controlla schema JSON, ID dei campi, duplicati, appartenenza al gruppo e posizioni scrivibili. Verifica che la citazione compaia nella fonte fornita, normalizzando spazi e maiuscole, e che il valore proposto compaia nella citazione.

**Aggiornamento v6:** puntini ed ellissi della stessa area diventano un solo segnaposto,
senza consumare abbreviazioni come `prov.`. Nei campi riconosciuti come email/PEC,
`email-validator` controlla la sintassi del recapito completo senza DNS. Non basta
che `pec` sia una sottostringa della fonte: anche un indirizzo sintatticamente
valido ma ritagliato da uno piu lungo viene bloccato. E' ammesso un unico tentativo
mirato di correzione, poi il campo resta vuoto. Il writer ripete il controllo sui
campi tipizzati. Non si verificano esistenza del recapito o titolarita della PEC.
Moduli che suddividono esplicitamente un recapito in parti (`___@___.___`) vengono
lasciati alla compilazione manuale quando riconosciuti. Etichette ambigue e altri
tipi di dati non hanno una validazione generale equivalente.

**Gli errori di evidenza sono locali:** una fonte inesistente, una citazione non letterale o un valore non contenuto nella citazione bloccano il singolo campo, senza perdere le altre proposte. Dopo il primo passaggio viene consentito un solo tentativo mirato per correggere valore/citazioni, mantenendo identita' e tipo del campo. Si riapplicano gli stessi controlli, senza confronti fuzzy su nomi, numeri o identificativi. Se non basta, il campo resta vuoto e segnalato come **Bloccato**. Proposta originale, riferimenti rifiutati ed esito della correzione restano nel report.

Le correzioni non riabilitano firme, scelte o dichiarazioni. JSON non interpretabile, ID sconosciuti/duplicati/esterni al gruppo e incoerenze tra stato e valore rimangono bloccanti. Per campi senza valore da scrivere si normalizzano solo metadati innocui: citazioni omesse come lista vuota, etichetta vuota come coordinata. Questo non risolve errori semantici o sezioni scelte male.

Le proposte riconosciute come firme, scelte o dichiarazioni non vengono scritte automaticamente. Sono presenti controlli sul pacchetto DOCX per rifiutare, tra gli altri, macro, oggetti incorporati, cifratura, firme digitali e protezioni non supportate.

**Questi controlli non dimostrano che il campo sia semanticamente corretto.** Un indirizzo puo' comparire davvero nella fonte ma appartenere all'amministrazione, non all'azienda. Una citazione puo' essere autentica ma riferirsi a una revisione non piu' valida.

Limiti da tenere espliciti:

- Non sono certificati ammissibilita', requisiti, deleghe, dichiarazioni, validita' fiscale o completezza degli allegati.
- Non vengono firmati documenti ne' effettuati invii. Il report mantiene `ready_for_submission: false`.
- La temperatura del modello e' 0,1, ma non garantisce risultati identici: due esecuzioni possono classificare e compilare un numero diverso di campi.
- La richiesta di copiare valori letterali e' prudenziale, ma puo' bloccare anche riformulazioni o composizioni di dati legittime.
- Il PDF viene trasformato in testo e suddiviso in frammenti di circa 1.200 caratteri, con sovrapposizione di 200. Tabelle, colonne e relazioni tra etichette possono perdere struttura.
- La provenienza usa documento e frammento, **non la pagina originale**. Nel report DOCX il campo `page` e' attualmente nullo.
- Il prompt invita a ignorare istruzioni ostili nei documenti; questo non equivale a una garanzia contro ogni prompt injection.

## 7. Limiti quantitativi attuali

Sono vincoli del prototipo, non soglie che garantiscono correttezza o completezza. **Caratteri e token non sono la stessa unita'.**

| Limite | Valore |
|---|---|
| Singola fonte caricata / modello DOCX | 20 MiB ciascuno, indicati come 20 MB nella UI. |
| DOCX decompresso | 40 MiB e massimo 2.048 parti ZIP. |
| Testo del corpo del modello | 60.000 caratteri. |
| Catalogo strutturale del modello | 100.000 caratteri serializzati. |
| Posizioni candidate | 400 tra celle e segnaposti; non necessariamente 400 campi reali. |
| Valore di un campo | Massimo 1.500 caratteri. |
| Indicazioni di compilazione | Massimo 4.000 caratteri. |
| Fonti per compilazione | Budget di 40.000 caratteri aziendali, 90.000 di progetto, 20.000 generali. |
| Dimensione corpus per compilazione | Massimo 5.000 frammenti di progetto e 5.000 globali complessivi; oltre, rifiuto. |
| Gruppo di compilazione | Massimo 32 posizioni candidate per chiamata. |
| Risposta per gruppo | Massimo 12.000 token di output. |
| Esecuzione dei gruppi | Massimo 40 chiamate, 180 secondi per chiamata e 600 secondi complessivi. Altri timeout possono interrompere prima. |

**Gestione del troncamento DOCX:** nel primo passaggio, se il provider dichiara `finish_reason=length`, la risposta viene scartata e solo quel gruppo viene diviso a meta' e riprovato. Non viene salvato un documento se un gruppo iniziale fallisce. Le correzioni opzionali dei singoli campi avvengono dopo tutti i gruppi e rientrano nello stesso limite di 40 chiamate/600 secondi; non sono ripetute o suddivise se troncate. Una correzione non disponibile o ancora non valida lascia il campo bloccato; gli errori strutturali e il timeout complessivo interrompono il processo. Le precedenti compilazioni salvate rimangono disponibili.

**Estrazione dei facts, distinta dal DOCX:** budget di ingresso di 160.000 caratteri; oltre viene selezionato un sottoinsieme dei frammenti. Limite di output 12.000 token, con un solo nuovo tentativo da zero a 24.000 se troncato; massimo 360 secondi complessivi. Se fallisce ancora, niente sostituzione dei dati salvati. Non e' un'estrazione completa garantita per bandi arbitrariamente lunghi.

## 8. Come leggere il risultato

| Indicazione | Significato |
|---|---|
| Campi inseriti | Valori effettivamente scritti dopo i controlli tecnici. Non equivale a valori certificati corretti. |
| Mancante | Il modello non ha trovato un valore utilizzabile nelle evidenze ricevute; potrebbe esistere in una parte non selezionata. |
| Da verificare | Campo non scritto, ambiguo o dichiarativo. |
| Bloccato | Una proposta e' stata respinta dai controlli. Il dato non e' necessariamente assente nelle fonti; aprire i dettagli per motivo ed eventuale correzione tentata. |
| Non applicabile | Classificazione da controllare rispetto alla modalita' di partecipazione effettiva. |
| Elementi non classificati | Posizioni candidate che il modello non ha classificato; possono comprendere elementi decorativi o campi omessi. |

**20 campi inseriti invece di 17 non prova che una compilazione sia migliore.** Servono confronto con i valori attesi, soggetto corretto, applicabilita' delle sezioni e campi effettivamente compilabili. Non tutti gli spazi vuoti devono essere riempiti.

Il report e' consultabile nella UI; non e' un editor Word. Le correzioni al documento finale si fanno nel file scaricato. Originale, bozza e report sono salvati separatamente per ogni esecuzione e gli output non vengono reindicizzati come nuove evidenze.

Il report v3 distingue origine documentale, sintesi automatica e dato dichiarato dall'utente. Nei dettagli mostra riferimenti rifiutati e correzioni applicate/non applicate. Una correzione tecnica riuscita non equivale a una verifica umana. I vecchi report v1/v2 restano leggibili.

## 9. Costi, privacy e maturita' operativa

- Ogni gruppo invia nuovamente fonti e catalogo del modulo. Molti campi e retry aumentano token, durata e costo; i token includono input e output, non soltanto il testo scritto nel Word.
- Il report somma l'utilizzo dichiarato dal provider nelle chiamate, inclusi tentativi troncati e correzioni; se mancano dati validi, il totale e' `null`. Non costituisce un preventivo di costo.
- I contenuti selezionati vengono trasmessi all'API esterna DeepSeek. L'app non e' interamente locale, anche se database e file sono locali.
- Non e' presente un sistema di autenticazione e autorizzazione per utente. L'isolamento logico tra progetti non sostituisce il controllo degli accessi: **non esporre pubblicamente il prototipo cosi' com'e'.**
- La generazione avviene durante una richiesta HTTP: non c'e' una coda persistente di lavori con ripresa dopo riavvio. Il modello appena selezionato e le indicazioni non ancora inviate non costituiscono un salvataggio permanente.
- Norme e dati aziendali non vengono aggiornati o verificati automaticamente sul web.

## 10. Che cosa possiamo mostrare e sostenere

**Dimostrabile:** su un modello supportato, il percorso carica il DOCX, usa le fonti disponibili, propone valori con riferimenti, applica controlli, produce una bozza scaricabile e segnala i punti da completare.

**Non ancora dimostrato:** accuratezza su bandi eterogenei, copertura di tutti i campi, risparmio di tempo misurato, beneficio dei facts rispetto alle sole fonti, superiorita' di un retriever o di un modello rispetto a un altro.

**Aggiornamento dalle prove reali:** la prima prova v4 si era fermata per una citazione attribuita alla fonte sbagliata. Dopo gli interventi v5 e due correzioni dei metadati vuoti emerse in altrettante prove fallite, l'ultima compilazione termina: **21 scritture, 9 chiamate, 665.331 token, circa 84 secondi**. Tuttavia sei scritture sono fuori dalle sezioni richieste, pur avendo evidenze autentiche. Il Word e' una bozza da correggere, non una compilazione semanticamente validata. Nell'ultima prova nessun campo ha attivato la correzione automatica; questa e' verificata dai test controllati. Esiti, file e limiti in [verifica-compilazione-mapi.md](verifica-compilazione-mapi.md), senza nascondere le prove fallite.

Verifiche tecniche effettuate al momento della stesura:

- Suite backend: 278 test passati, inclusi casi indipendenti dal modulo Catanzaro e regressioni sui metadati vuoti.
- Frontend: 78 test passati; 12 test browser DOCX su desktop/mobile. TypeScript e build Vite superati.
- I test del modello usano risposte simulate. I test sul modulo reale di Catanzaro verificano anche struttura e scrittura; la mappa manuale usata per alcuni test non e' usata dal compilatore in produzione.
- Il Word dell'ultima prova supera controlli strutturali e di corrispondenza con il report, ma mostra errori di applicabilita'. Non e' stato eseguito un rendering Word/LibreOffice. Prima della demo serve controllare il documento risultante e l'impaginazione, senza presentarlo come pronto all'invio.

Per valutare la qualita' servira' un piccolo insieme di moduli con valori attesi: correttezza dei valori inseriti, copertura dei campi compilabili con i dati disponibili, compilazioni non supportate dalle fonti e correzioni/tempo richiesti all'utente. I test software e il numero di campi compilati non sostituiscono questa valutazione.

**Descrizione breve per i relatori:** "Il prototipo prepara una bozza di un modulo Word a partire dalle fonti disponibili. Il modello propone i valori; il backend ne controlla riferimenti e posizioni di scrittura. Informazioni mancanti e scelte da confermare restano visibili, con revisione finale dell'utente."

## Riferimenti nel repository

- [Dipendenze backend](backend/pyproject.toml) e [frontend](frontend/package.json).
- [Ingestion delle fonti](backend/app/ingestion.py) e [retrieval lessicale](backend/app/repository.py).
- [Parser e writer DOCX](backend/app/docx_templates.py).
- [Prompt, selezione fonti, validazione e gruppi](backend/app/document_compilation.py).
- [API e salvataggio delle compilazioni](backend/app/document_compilation_routes.py).
- [Estrazione dei facts](backend/app/fact_extraction.py) e [configurazione del modello](backend/app/config.py).
- [Guida operativa DOCX](backend/docs/compilazione-docx.md) e [gestione dei dati del progetto](backend/docs/dati-progetto.md).
