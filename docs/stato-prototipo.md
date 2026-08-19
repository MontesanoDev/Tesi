# Stato del prototipo Mapi RAG

## 1. Obiettivo

Mapi RAG e una vertical slice di un assistente per progetti tecnici e documentali
nel settore dell'ingegneria civile. Il sistema non si limita a rispondere a
domande su un PDF: organizza le fonti di un progetto, separa la conoscenza
aziendale da quella della singola candidatura, recupera evidenze verificabili e
prepara artefatti revisionabili da un utente.

L'obiettivo del prototipo e dimostrare l'intero percorso:

```text
documenti grezzi
-> organizzazione della conoscenza
-> recupero delle evidenze
-> analisi dei fatti
-> revisione umana
-> generazione di un output controllabile
```

Il prototipo non deve essere presentato come un sistema pronto per la produzione
o come un sostituto del professionista. E un sistema di supporto che mantiene
espliciti fonti, dati mancanti e responsabilita della revisione finale.

## 2. Problema affrontato

La preparazione di una candidatura tecnica richiede normalmente di consultare
bandi, allegati, norme, dati aziendali, dati del progetto e modelli di output.
Queste informazioni hanno proprietari, validita e scope differenti.

Un normale chatbot documentale tende a trattare tutto come testo indistinto. Mapi
RAG introduce invece tre principi:

1. separazione tra conoscenza globale e conoscenza del progetto;
2. distinzione tra documenti sorgente e dati strutturati verificati;
3. generazione di output sottoposti a revisione umana.

## 3. Flusso utente attuale

Il flusso principale funzionante e il seguente:

1. l'utente crea oppure apre un progetto;
2. carica i PDF o TXT specifici del progetto;
3. collega eventuali documenti globali gia presenti in General KB o Company KB;
4. interroga le fonti tramite la chat;
5. consulta le evidenze recuperate e le citazioni;
6. estrae i Call Facts dai documenti del progetto;
7. verifica, modifica oppure scarta i fatti estratti;
8. completa Project Facts e Template in Markdown;
9. genera un Draft usando soltanto dati ammessi;
10. revisiona l'output prima di qualsiasi utilizzo esterno.

## 4. Gestione dei progetti

Sono implementate le seguenti operazioni:

- elenco dei progetti;
- creazione di un nuovo progetto;
- apertura del workspace;
- persistenza dei progetti in SQLite;
- eliminazione definitiva con conferma esplicita;
- cancellazione di conversazioni, chunk, collegamenti e artefatti locali;
- rimozione dal filesystem dei file appartenenti al progetto;
- conservazione della conoscenza globale dopo l'eliminazione del progetto.

I progetti dimostrativi vengono inizializzati una sola volta. Se vengono eliminati,
non ricompaiono al successivo riavvio.

La rinomina e l'archiviazione sono ancora comandi non implementati.

## 5. Acquisizione dei documenti

Il sistema accetta attualmente:

- file PDF con testo estraibile;
- file TXT in UTF-8;
- dimensione massima di 20 MB per file.

Il backend salva il file, estrae il testo, lo divide in chunk sovrapposti e
indicizza i chunk in SQLite FTS5.

Non sono ancora supportati:

- PDF composti soltanto da immagini;
- OCR;
- DOCX, XLSX e altri formati Office;
- immagini;
- Markdown caricato come documento;
- archivi compressi o insiemi di file caricati in blocco.

## 6. Organizzazione della conoscenza

### 6.1 General KB

Contiene norme, linee guida, procedure e materiale tecnico riutilizzabile in piu
progetti. I documenti vengono caricati globalmente e collegati solo ai progetti
che devono utilizzarli.

### 6.2 Company KB

Contiene documenti aziendali non strutturati, per esempio:

- visure;
- curriculum societari;
- certificazioni;
- referenze;
- polizze;
- documentazione sulle capacita tecniche.

La visura simulata presente in `demo-documents/` e un esempio di Company KB.

### 6.3 Company Facts

Contiene dati aziendali strutturati e verificati in Markdown, per esempio ragione
sociale e ruolo operativo. Non e una categoria nella quale caricare PDF.

I Company Facts vengono collegati a tutti i progetti. La modifica aggiorna il
file Markdown globale, ne incrementa la versione e reindicizza il contenuto nei
progetti collegati.

L'estrazione automatica dei Company Facts dai documenti della Company KB non e
ancora implementata.

### 6.4 Conoscenza del progetto

Comprende i documenti caricati nel singolo workspace e i seguenti artefatti:

- `call-facts.md`;
- `project-facts.md`;
- `template.md`;
- `draft.md`.

I documenti e i Call Facts di un progetto non vengono resi disponibili agli altri
progetti.

## 7. Chat e risposte grounded

La chat esegue realmente il seguente flusso:

1. riceve la domanda;
2. recupera i chunk pertinenti dalle fonti ammesse nel progetto;
3. passa domanda, evidenze e contesto recente a DeepSeek;
4. richiede una risposta strutturata;
5. valida che le citazioni indicate esistano;
6. salva domanda, risposta, evidenze e metadati in SQLite.

Le evidenze mostrano il nome del documento e il numero del frammento. Se non viene
trovata una fonte sufficiente, il sistema esplicita l'informazione mancante invece
di produrre silenziosamente una risposta non verificabile.

Le conversazioni e i turni persistono dopo il refresh. Le card recenti possono
riaprire una conversazione precedente. Alcune domande brevi di follow-up possono
riutilizzare il contesto della domanda precedente.

Il modello puo comunque commettere errori. La validazione delle citazioni dimostra
che una fonte citata e stata fornita al modello, ma non garantisce ancora in modo
automatico che ogni affermazione sia semanticamente implicata dalla fonte.

## 8. Call Facts e revisione umana

DeepSeek puo analizzare le fonti locali del progetto e proporre un insieme di
Call Facts. Le categorie non dipendono da un enum fisso legato a un singolo bando.

Ogni fatto include:

- identificativo stabile;
- titolo;
- valore;
- stato;
- documento sorgente;
- numero del frammento.

L'utente puo:

- verificare il fatto;
- modificarlo;
- scartarlo;
- ripristinarlo.

Una modifica riporta il fatto nello stato da verificare. I fatti scartati restano
nel Markdown per tracciabilita, ma non vengono indicizzati. Soltanto i fatti
verificati possono essere usati dal RAG e dalla generazione del Draft.

## 9. Generazione del Draft

Il Draft viene generato seguendo `template.md` e usando esclusivamente:

- Company Facts;
- Project Facts;
- Call Facts verificati.

I documenti grezzi della Company KB possono supportare la chat, ma non vengono
copiati automaticamente nel Draft come dati certi.

Le informazioni mancanti restano indicate come `TODO`. La provenienza viene
espressa tramite riferimenti come:

- `[COMPANY]`;
- `[PROJECT]`;
- `[CF:identificativo]`.

Il backend rifiuta riferimenti a Call Facts non verificati. `draft.md` resta
modificabile e versionato, ma viene escluso dall'indice RAG per impedire che un
output generato diventi fonte di se stesso.

L'esportazione effettiva in DOCX o PDF non e ancora implementata.

## 10. Revisione documentale

Esiste una vista che mostra un modulo di candidatura con:

- campi compilati;
- campi mancanti;
- stato di verifica;
- provenienza dei valori;
- riepilogo di completezza;
- richiamo alla revisione umana.

Questa vista e ancora dimostrativa: i campi sono predisposti nel database e non
costituiscono ancora un renderer generico capace di trasformare qualsiasi
`template.md` in un documento compilabile.

## 11. Interfaccia implementata

Sono disponibili:

- lista progetti;
- creazione progetto;
- workspace con chat;
- caricamento delle fonti locali;
- conversazioni recenti;
- pannello delle conoscenze collegate;
- impostazioni generali;
- impostazioni del progetto;
- archivio globale separato;
- selezione tra Company KB, Company Facts e General KB;
- collegamento selettivo delle fonti globali;
- editor degli artefatti Markdown;
- revisione dei Call Facts;
- generazione del Draft;
- vista di revisione documentale;
- eliminazione del progetto con conferma.

Restano ancora parziali oppure non funzionanti:

- modifica delle istruzioni del progetto;
- persistenza delle preferenze generali;
- rinomina e archiviazione del progetto;
- pagina autonoma per tutti i documenti e gli output;
- cancellazione o sostituzione dei singoli file locali;
- esportazione finale.

## 12. Controlli e garanzie presenti

Il prototipo applica gia alcuni vincoli importanti:

- separazione dello scope dei progetti;
- collegamento esplicito dei documenti globali;
- Company Facts distinti dai documenti della Company KB;
- provenienza dei Call Facts;
- revisione prima dell'uso dei fatti estratti;
- esclusione dei fatti scartati;
- esclusione del Draft dal retrieval;
- citazioni limitate alle evidenze recuperate;
- segnalazione dei dati mancanti;
- conferma prima dell'eliminazione di un progetto.

Questi controlli riducono il rischio, ma non sostituiscono validazione tecnica,
controllo amministrativo e responsabilita professionale.

## 13. Parti reali e parti dimostrative

| Componente | Stato |
| --- | --- |
| Persistenza di progetti e conversazioni | Funzionante |
| Upload PDF/TXT e chunking | Funzionante |
| Indice SQLite FTS5 | Funzionante |
| Collegamento Company KB e General KB | Funzionante |
| Chat con DeepSeek e citazioni | Funzionante |
| Editor Markdown e versionamento | Funzionante |
| Estrazione e revisione Call Facts | Funzionante |
| Generazione del Draft | Funzionante |
| Eliminazione completa del progetto | Funzionante |
| Modulo visuale di revisione | Dimostrativo |
| Esportazione DOCX/PDF | Non implementata |
| Embeddings e ricerca vettoriale | Non implementati |
| OCR | Non implementato |
| Autenticazione e ruoli | Non implementati |

## 14. Limiti principali

### 14.1 Retrieval lessicale

Il sistema usa FTS5 e non comprende ancora la similarita semantica tramite
embeddings. Sinonimi lontani e formulazioni molto diverse dal testo originale
possono ridurre il richiamo delle fonti corrette.

### 14.2 Dipendenza dal modello esterno

La generazione richiede una chiave DeepSeek e una connessione di rete. Senza
chiave restano disponibili indicizzazione, retrieval ed evidenze, ma non la
risposta generata.

### 14.3 Formati e OCR

Il sistema gestisce soltanto PDF testuali e TXT. I documenti scannerizzati sono
una limitazione rilevante nel dominio amministrativo e tecnico.

### 14.4 Sicurezza e utenti

Non sono presenti autenticazione, autorizzazioni, cifratura applicativa,
antivirus sugli allegati, quote utente o isolamento multi-tenant.

### 14.5 Scalabilita

L'indicizzazione avviene nella richiesta HTTP e non usa una coda di job. Questa
scelta e sufficiente per la demo, ma non per grandi volumi o molti utenti.

### 14.6 Valutazione

I test verificano il comportamento software, ma manca ancora un dataset di
valutazione del retrieval e della generazione con domande e risposte annotate.

## 15. Verifica automatica corrente

La suite comprende:

- 40 test backend con Pytest;
- 2 test unitari frontend con Vitest;
- 14 test end-to-end e visuali con Playwright su desktop e mobile;
- lint Python con Ruff;
- lint TypeScript con Oxlint;
- build TypeScript e Vite.

I test coprono anche scope della Company KB, revisione dei Call Facts, generazione
del Draft, persistenza delle conversazioni, ranking tra indici globali e locali,
layout responsive ed eliminazione dei progetti.

## 16. Sviluppi futuri consigliati

### Priorita 1 - Consolidamento della demo

- completare le istruzioni modificabili;
- aggiungere cancellazione e sostituzione dei file;
- implementare rinomina e archiviazione;
- migliorare gli stati di caricamento e gli errori;
- rendere generico il renderer degli output.

### Priorita 2 - Retrieval ibrido

- introdurre un modello di embedding;
- aggiungere un indice vettoriale;
- combinare FTS5 e similarita semantica;
- applicare un reranker finale;
- misurare il miglioramento rispetto alla baseline lessicale.

### Priorita 3 - Estrazione strutturata

- estrarre proposte di Company Facts dalla Company KB;
- mantenere obbligatoria la conferma umana;
- confrontare dati nuovi e versioni precedenti;
- segnalare conflitti tra fonti.

### Priorita 4 - Documenti reali

- OCR;
- supporto DOCX;
- compilazione di template reali;
- esportazione DOCX e PDF;
- firme, allegati e pacchetti di candidatura.

### Priorita 5 - Produzione

- autenticazione e ruoli;
- audit log;
- gestione dei segreti;
- job asincroni;
- migrazioni del database;
- backup;
- monitoraggio;
- protezioni contro prompt injection contenuta nei documenti.

### Priorita 6 - Valutazione sperimentale

- costruire un corpus di documenti tecnici;
- annotare domande, risposte e chunk rilevanti;
- misurare Recall@k e Precision@k;
- misurare faithfulness e correttezza delle citazioni;
- confrontare FTS5, retrieval vettoriale e retrieval ibrido;
- misurare latenza e costo delle chiamate al modello.

## 17. Definizione sintetica

Mapi RAG puo essere descritto come:

> Un workspace per progetti tecnici che separa conoscenza globale e fonti del
> progetto, recupera evidenze verificabili, assiste l'analisi dei requisiti e
> genera output strutturati sottoposti a revisione umana.

Il valore della vertical slice non consiste nell'avere gia tutte le funzioni di
un prodotto commerciale. Consiste nell'avere reso funzionante e verificabile il
percorso completo dal documento sorgente all'output revisionabile.
