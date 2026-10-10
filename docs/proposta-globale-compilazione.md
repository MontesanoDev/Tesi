# Proposta globale sperimentale — 10 ottobre 2026

## Terzo contratto: inventario e assegnazioni compatte

Passo sperimentale autorizzato, **non attivo nella chat**. Una sola chiamata
riceve ancora tutto il catalogo originale e il corpus SOURCE piccolo completo.
Le versioni precedenti restano leggibili soltanto per gli audit storici.

- `condition_scan`: un elemento per ogni paragrafo FORM non vuoto, inclusi
  titoli e istruzioni. Lista di condizioni lì espresse, `[]` se non proposte,
  `null` se incerto. Copertura esatta verificata dal backend, massimo 2.048
  paragrafi; oltre budget errore, nessun troncamento. Non è un detector basato
  su parole del bando e non prova la completezza semantica dell'inventario.
- `conditions.applies_to`: mappa proposta dal modello fra clausole e candidate,
  con estratto FORM. Il backend collega anche tutte le condizioni locali
  inventariate, così un'assegnazione non può ometterne il riferimento. Scope
  non locale ancora da verificare: non autorizza automaticamente valori o NA.
- `facts`: proprietà SOURCE distinte, valori atomici e citazioni condivise.
  `fields.property` deve coincidere con la proprietà del fatto referenziato:
  un generico profilo non può essere usato come nome e numero. Il modello può
  ancora classificare male le proprietà; questa identità non è una prova
  semantica indipendente. Gli indicatori di indisponibilità/placeholder non
  possono diventare fatti utilizzabili, neppure nelle condizioni.
- `fields`: massimo 128 assegnazioni dettagliate. `deferred`: soli ID delle
  altre posizioni, fino a 400 totali. Unione esatta e senza duplicati, nessun
  default implicito. Deferred è **ancora da interpretare**, non missing né
  decorativo e non una nuova domanda all'utente. Riduce l'output ripetitivo;
  non equivale a una compilazione completata di tutti i candidate.

Invariati i gate SOURCE/FORM, le quote, i confronti conservativi, i limiti
corpus/input/output e la singola chiamata senza retry. Inventario locale
incerto impedisce value/missing/NA. Nessun valore scrivibile e nessun RESOLVED;
chat, sessioni V1, parser e renderer invariati. Nessuna migrazione/reindicizzazione.
Prima della prova reale: regressioni generiche su copertura, condizioni omesse,
proprietà diverse, fatto composito, indisponibilità, scope e provenance.

## Secondo contratto: fatti e condizioni condivisi

**Esito reale:** due risposte omettono tutte le condizioni; la prova thinking
low viene troncata. Non attivare nella chat e non assumere un miglioramento
dal nuovo schema. [Misure e diagnosi](benchmark-condizioni-globali-2026-10-10.md).

Il nuovo input richiede `version=2`, `facts`, `conditions`, `fields`. Una sola
chiamata riceve ancora tutto il FORM e il corpus SOURCE piccolo completo.
La versione precedente resta leggibile per riprodurre gli audit archiviati;
non è un secondo percorso operativo né una migrazione delle sessioni.

- `facts`: soggetto, entity, dimensione (`aspect`), proprietà, valore letterale
  e citazioni SOURCE conservate una volta. Un field referenzia `fact_id`;
  non può ripetere un valore/evidence alternativi per eludere il controllo.
- `conditions`: estratto FORM, dimensione, operatore e riferimenti ai fatti.
  `same`/`different` richiedono due fatti distinti dello stesso soggetto/entity,
  stessa dimensione e proprietà distinte. Tipologia, partecipazione e poteri
  sono dimensioni separate. Non si possono confrontare per escludere un ramo.
- Valori identici dopo sola normalizzazione Unicode NFC/whitespace permettono
  di calcolare `same=true` / `different=false`. Testi diversi restano unknown:
  abbreviazioni o grafie diverse non provano valori reali differenti.
  La dimensione `other` e gli operatori `semantic` restano unknown.
- Ogni field elenca esplicitamente le proprie condizioni (`[]` se non ne
  propone). Condizione falsa: niente value/missing; unknown: solo review;
  non applicabile: necessaria almeno una condizione calcolabile falsa.
  Un vincolo fuori dalla riga/intestazione locale non può autorizzare un valore
  o escludere la destinazione: la sua associazione di sezione resta da verificare.
- Le checkbox possono proporre `choice` booleano con riferimento a un fatto;
  restano non scrivibili. Firme e dichiarazioni conservano le protezioni esistenti.

Budget aggiuntivi: massimo **128 fatti**, **128 condizioni**, **8 riferimenti a
condizioni per field**; invariati 400 candidate, 96 chunk/100.000 caratteri
SOURCE, 350.000 caratteri input, 49.152 token output e timeout 300 s. Nessun
reviewer, retry o chiamata per field. Il validator riusa i controlli letterali
precedenti; gli errori dei fatti/condizioni isolano le assegnazioni dipendenti.
Tutte le prove restano nell'audit, incluse quote effettive, ID citato/ripristinato,
hash, scope e categoria. La copertura dei candidate è ancora esatta.

Il runner offre `--thinking` per un confronto isolato con ragionamento DeepSeek
`low` (modalità già impiegata dalla mappa V1). Default disabilitato, invariati
schema/input/validator, budget e numero di chiamate. I token di ragionamento
possono incidere sul limite di output e sulla latenza; salvare il response HTTP
completo e usage, non considerare questo confronto una scelta di produzione.

**Limite intenzionale:** questi risultati sono subordinati alla correttezza
semantica della mappa proposta. Non provano che il modello abbia individuato
tutte le condizioni, classificato bene ogni dimensione o scelto l'operatore
corrispondente al FORM. L'assenza di una condizione proposta non dimostra
incondizionalità. Perciò restano `semantic_review_required=true`, zero RESOLVED
e zero scritture. La V1, chat, parser, renderer e RAG non cambiano.

Il resto della pagina descrive il primo contratto e le misure storiche.

Passo successivo al catalogo FORM condiviso. Una sola chiamata reale DeepSeek
riceve l'intero modulo, un piccolo corpus documentale SOURCE e lo schema di
output. Nessuna mappa/review/ricerca per gruppi né retry AI in questo percorso.
La chat e la CompilationSession continuano a usare la V1: non sono modificate.

## Input e output

`compilation_global.py` prepara `form`, `sources`, `user_values=[]` e copertura.
Ogni SOURCE conserva chunk/file ID, indice, nome, ruolo, progetto, scope e
categoria Company/General KB. Il runner legge una copia temporanea SQLite,
riusa filtro e rilettura del repository e include tutte le fonti documentali
caricate nel progetto e Company/General KB. Moduli, altri progetti e artefatti
(anche fatti USER) restano esclusi da questa prima prova SOURCE-only.

Il modello restituisce `fields`, indicizzato dagli ID strutturali esistenti.
Ogni elemento contiene label, soggetto, tipo, disposition, valore eventuale,
estratto FORM locale, massimo due quote SOURCE e ragione breve. Le disposition
sono `value`, `missing`, `review`, `not_applicable`, `ignore`. Non sono stati
persistiti della CompilationSession. Non vengono accettati contatori del modello.

Budget: massimo 400 candidate, 96 chunk SOURCE/100.000 caratteri SOURCE,
350.000 caratteri di input, 49.152 token massimi di output, 500.000 caratteri
di risposta. Corpus oltre budget: errore esplicito, nessuna selezione/troncamento
silenzioso. Un'unica chiamata con thinking disattivato, timeout totale default
300 secondi (configurabile 1–600), nessun retry automatico.

## Cosa prova il validator

- Coverage esatta, ID validi e univoci; JSON duplicato/troncato non utilizzabile.
- FORM quote letterale nel paragrafo del candidate o riga/intestazione fisica
  della sua tabella; una label di una tabella diversa non è ammessa.
- SOURCE nel corpus consentito, quote verificabile, valore testuale completo
  nella quote, controlli numerici/email e protezioni del validator DOCX esistente.
- Booleani tipizzati per checkbox; firme protette; nessun valore per missing,
  review, ignore o non applicabile. Non applicabilità proposta richiede SOURCE.
- Errore locale: candidate rifiutato, altre proposte conservate per l'audit.

Dopo la prima prova reale, aggiunti riferimenti espliciti ai paragrafi locali
non vuoti (`anchor_paragraph_ids`), senza duplicare testo o dedurre etichette.
Quote vuota consentita esclusivamente per `ignore` + `decorative`, senza valore
né SOURCE: un campo informativo continua a richiedere grounding. Apostrofi e
virgolette tipografiche FORM possono essere normalizzati deterministicamente;
la quote originale viene conservata, nessun fuzzy matching.

Se il modello cita un chunk errato, la quote può essere ricondotta a un altro
chunk **dello stesso file già fornito** solo quando compare integralmente e
univocamente. File diverso, quote ambigua/riscritta o corpus esterno: rifiuto.
L'audit conserva sia `cited_chunk_id` sia chunk effettivo e `citation_rebound`.
Questa correzione di riferimento non approva significato/proprietà/soggetto.
Il prompt distingue meglio condizione falsa/ignota e dati comuni/partecipazione;
non aggiunge regole per il modulo demo o per aziende/candidate particolari.

**GROUNDED_PROPOSAL non significa RESOLVED.** I controlli letterali non provano
che proprietà, soggetto, ruolo e ramo siano corretti, né che una condizione
discenda semanticamente da una SOURCE. Tutte le proposte conservano
`semantic_review_required=true`, `written_value=null`; resolved e scritture
sono zero. Non viene fabbricato il verdetto indipendente della V1. La valutazione
semantica umana annotata del benchmark resta distinta dai controlli software.
Non c'è adapter di sessione/export né scrittura checkbox in questo passo.

## Ripetizione della prova reale

Da `backend`, con il profilo DeepSeek già configurato:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_global.py \
  --project minervino-di-lecce-elenco-sia --form-id 153 \
  --profile-project prova \
  --output data/compilation-audit/global-NUOVA-PROVA
```

Usare una directory nuova. Non modifica profili, sessioni, DB live o originale;
scrive soltanto l'audit e una copia dell'originale. Salva input, schema, richiesta,
risposta HTTP (anche se troncata), testo grezzo, usage, durata, validazione locale,
codice congelato e manifest. Credenziali/header non esportati. Il limite finestra
salvato nel profilo è registrato separatamente dalle capacità del provider.

La modalità JSON e il budget output seguono la
[documentazione ufficiale DeepSeek](https://api-docs.deepseek.com/guides/json_mode/).
Il [contratto API](https://api-docs.deepseek.com/api/create-chat-completion/)
documenta i limiti del servizio: non confonderli con i limiti conservativi della
prova. Nessuna stima di token ottenuta dividendo i caratteri: si usa solo usage.

Per confrontare tempi/token con la V1 usare lo stesso hash DOCX e lo stesso
corpus; distinguere sempre analisi globale e primi 12 candidate della baseline.
Le differenze di cache e variabilità del servizio limitano un singolo confronto.

## Punto successivo

Misurare la proposta reale e annotare almeno i cinque campi SOURCE già dimostrati,
rami condizionali, direttore tecnico/albo e falsi positivi. Decidere poi il
contratto di accettazione semantica locale per l'adapter: il passaggio alla chat
richiede questa garanzia, non soltanto JSON valido o token ridotti.
