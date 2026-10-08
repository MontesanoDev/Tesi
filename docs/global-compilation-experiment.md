# Compilazione globale: prototipo separato e prova del 8 ottobre 2026

È un esperimento attivabile da CLI, senza route, UI o collegamento alla pipeline
ordinaria. Il modello legge simultaneamente FORM, SOURCE e USER e propone un
piano. Il backend decide quali prove e associazioni ammettere. Non vengono
modificati sessioni, revisioni, originali o indici applicativi.

## Soggetti e condizioni: correzione offline v3 — 8 ottobre 2026

Successiva richiesta mirata, senza nuove chiamate AI o integrazione. Il validatore
ora conserva le decisioni USER verificate prima di considerare stato, soggetto o
citazioni proposti dall'LLM. Scope, ID univoci e condizione registrata restano
controllati: un frammento non esclude una condizione composta. Record verificati
in conflitto restano espliciti, senza scegliere per conto dell'utente.

Le condizioni FORM riconosciute sono valutate con le SOURCE pertinenti del
congelato anche quando l'LLM risponde UNKNOWN o cita male: tipologie positive,
enumerazioni già supportate, risposta esplicita sì/no alla qualificazione esatta,
coincidenza delle sedi. Decisione backend con soggetto/prova corretti separata
dalla proposta grezza e dai suoi errori. Nessuna esclusione dedotta dalla sola
S.r.l., dall'attività o dal silenzio delle fonti.

Ruoli riletti dalle didascalie complete dell'originale: rappresentanti, direttori,
firmatari e consorziate non ricevono dati l'uno dell'altro o dell'operatore.
Il record SOURCE di una consorziata conserva proprietario e ruolo; amministratore
unico non prova automaticamente rappresentanza. L'operatore soggetto della
condizione resta distinto dalle consorziate elencate nei campi.

Partecipazione: una sola domanda logica con ID stabile, predisposta dopo il
controllo di USER e delle SOURCE della pratica. Risposte ignote e forme giuridiche
non diventano una scelta. Domande ripetute accorpate; parti miste da riformulare
conservate. Nessun messaggio in chat o registro di conversazione aggiunto:
questa funzionalità rimane nel report del prototipo isolato.

| Replay congelato | Prima → dopo |
|---|---|
| Senza thinking | 12 scritture identiche; 7 APPLICABLE / 1 NA / 7 UNKNOWN invariati |
| Thinking | 14 scritture identiche; sezioni 7 / 0 / 8 → **7 / 1 / 7** |
| Candidate thinking | 14 VALIDATED / 7 NA / 6 REVIEW / 252 UNKNOWN → **14 / 10 / 6 / 249** |
| Copertura | 279/279 candidate e 15/15 sezioni, entrambe le risposte |
| USER locale / sospette stability pass | 7/7 conservate; 0/13 riproposte o approvate |

Nel thinking torna escluso il ramo professionista singolo tramite USER; due
slot dipendenti e sede operativa coincidente passano da UNKNOWN a NA. Fonte sulla
sede riletta integralmente, senza usare la proposta errata come prova. Restano
UNKNOWN le altre sette esclusioni non provate, poteri del rappresentante,
partecipazione e dati mancanti. Non ricreate qui le altre domande omesse dal
modello; i suoi piani grezzi sono invariati.

**309 test mirati passati** (121 prototipo, di cui 51 nuovi, più 188 regressioni
script/DOCX/fonti), Ruff backend completo passato. Due export verificati:
12/14 celle scritte, altre 497/495 celle e 13 parti accessorie identiche; confronto
canonico XML e riapertura passati, solo avviso di bozza oltre alle celle autorizzate.
Copertura incompleta, schema invalido e troncamento continuano a bloccare tutte
le scritture anche quando USER è preservato. Mai completed/ready.

[Report dettagliato](../backend/data/compilation-audit/global-subject-conditions-20261008/report.md),
[confronto e tracce](../backend/data/compilation-audit/global-subject-conditions-20261008/comparison-final.json),
[DOCX senza thinking](../backend/data/compilation-audit/global-subject-conditions-20261008/verified-without-thinking/bozza-globale-parziale.docx),
[DOCX thinking](../backend/data/compilation-audit/global-subject-conditions-20261008/verified-thinking/bozza-globale-parziale.docx).
Zero nuove chiamate, pipeline/UI/sessioni invariate, nessun commit/push o nuovo
livello di orchestrazione. Le sezioni seguenti conservano gli interventi storici.

## Seconda prova controllata con thinking — 8 ottobre 2026

Richiesta successiva: una sola nuova chiamata reale con thinking, su percorso
separato, senza modificare validatore, schema, pipeline o UI. Prima verificato
il supporto ufficiale di `deepseek-flash` per thinking con il JSON mode in uso;
poi **confermato dalla risposta reale**, con canale reasoning presente e
29.087 reasoning token dichiarati. Nessuna simulazione o completion di preflight.

Request clonato byte per byte nei messaggi; unico parametro modificato:
`thinking.type`, da `disabled` a `enabled`. FORM/SOURCE/USER e originale identici,
stesso schema e validatore aggiornato della baseline offline (SHA-256
`60d89fc1b3665e117805fe092724fb031426ec44ec6feff9dbd8052112a166f1`).
Effort non aggiunto: default high documentato. Temperatura 0.1 conservata, ma
ignorata dal provider in thinking mode; limite del confronto fra due sole risposte.

| Misura | Baseline senza thinking, validatore aggiornato | Con thinking |
|---|---:|---:|
| Candidate / sezioni coperti | 279/279; 15/15 | 279/279; 15/15 |
| Valori proposti / verificati e scrivibili | 14 / 12 | 17 / 14 |
| Composizioni non letterali | 2 | 0 |
| Riferimenti SOURCE ai valori proposti / ammessi | 27 / 21 | 18 / 14 |
| Sezioni APPLICABLE / NA / UNKNOWN | 7 / 1 / 7 | 7 / 0 / 8 |
| Vecchie assegnazioni sospette riproposte | 0/13 | 0/13 |
| Domande / duplicati testuali | 11 / 0 | 5 / 0 |
| Token input / output inclusivo | 213.628 / 35.887 | 213.653 / 59.152 |
| Token totali | 249.515 | 272.805 |
| Tempo chiamata e verifica locale | 94,407 s | 178,392 s |

Telefono e numero albo diventano letterali e validati; tutti i 12 candidate già
scrivibili restano tali. I due identificativi fiscali hanno ora valori letterali
senza annotazione, citati dalla scheda Markdown: cambiati dal modello, non dal
backend, sempre valori fittizi. Tre nuovi tentativi bloccati: sede operativa
coincidente nonostante «se diversa» e due celle di Luca Ferri con attribuzione
representative non provata. Nome/carica esistono, ma poteri e scelta del firmatario
non sono documentati. Il direttore tecnico rimane distinto dai rappresentanti.

Regressione sulle sezioni: tutte le otto esclusioni proposte sono associate a
un'entità ignota anziché all'operatore, incluso 5.a già risolto da USER. Le sette
decisioni USER locali rimangono NA; nessuna sessione modificata. 5.b/b-bis/c/e/f
incontrano anche il limite del validatore sulle esclusioni negative di tipologia:
occorre qualificazione/regola verificata, non automaticamente cinque domande.
5.g/5.h richiedono prova di qualificazione o relazione/partecipazione, non deducibili
dalla S.r.l. Sede operativa già risolvibile dalla SOURCE di coincidenza.
Le 13 sospette restano UNKNOWN, non esclusioni certificate; i quattro target
consorziate conservano la sezione corretta ma perdono il ruolo distinto.

Cinque domande più concise, senza riconferma di nome azienda/direttore, ma omessi
numero/data Registro Imprese e data di abilitazione del direttore. Registro
pubblico richiesto anche quando alternativa FORM. Nessuna domanda inviata alla
chat; meno gruppi non dimostra migliore copertura dei chiarimenti.

HTTP 200/stop, JSON/schema validi, nessun troncamento o ID inventato. Budget output
98.304 invariato; consumati 59.152 token, di cui 29.087 reasoning e 30.065 finali
per differenza. Input +25 a messaggi identici, causa non dimostrata. Fingerprint
modello uguale, cache hit zero. Tempo HTTP secondo run 178,074 s, non disponibile
separatamente nella baseline; i tempi complessivi includono elaborazione locale.

Export reale di **14 celle**, 495 altre celle e 13 parti accessorie identiche;
riapertura DOCX e confronto canonico XML passati, solo avviso di bozza oltre alle
celle autorizzate. Mai completed/ready. In questo intervento: **70 test prototipo
passati in 5,53 s**, Ruff completo; codice invariato, nessuna suite frontend/E2E.
Preservati per hash codice, prima prova, 33 tabelle SQLite e 29 file applicativi.

[Report comparativo con tutte le 17 proposte, UNKNOWN e domande](../backend/data/compilation-audit/global-thinking-20261008/report.md),
[conferma thinking](../backend/data/compilation-audit/global-thinking-20261008/thinking-confirmation.json),
[controllo request congelati](../backend/data/compilation-audit/global-thinking-20261008/controlled-input-check.json),
[DOCX parziale](../backend/data/compilation-audit/global-thinking-20261008/live-01/bozza-globale-parziale.docx).
Due scritture recuperate non compensano da sole le regressioni su condizioni e
chiarimenti. **Nessuna superiorità globale dimostrata, integrazione o altra prova
automatica.** Le sezioni seguenti conservano la storia dei precedenti interventi.

## Rivalutazione offline autorizzata — 8 ottobre 2026

Su richiesta successiva dell'utente sono stati corretti i limiti dimostrati del
validatore e rivalutata **la medesima risposta**, su una nuova copia. Nessuna
chiamata DeepSeek aggiuntiva, integrazione nella pipeline o modifica della UI.
Request, risposta grezza, FORM, SOURCE, USER, manifest della chiamata e originale
sono identici; i risultati storici rimangono conservati.

**12 proposte su 14 sono supportate nel dataset dimostrativo:** 9 già validate
localmente e 3 falsi negativi recuperati. Due proposte restano UNKNOWN per errori
di composizione del valore rispetto al contratto letterale. Il dato di base è
corretto anche in questi due casi: non sono allucinazioni di telefono o albo.

| Candidate | Campo e valore proposto | Esito della revisione | SOURCE ammessa: ID/riga |
|---|---|---|---|
| `t0.r5.c1` | Operatore: Mapi Ingegneria S.r.l. | Corretto, già validato | global:1/10; global:2/12 |
| `t0.r6.c1` | Forma: Società a responsabilità limitata | Corretto, già validato | global:1/11; global:2/13 |
| `t0.r7.c1` | Sede legale: Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | Corretto, già validato | global:1/20; global:2/28 |
| `t0.r9.c1` | CF: IT01234567890 (dato simulato) | **Falso negativo PDF**; letterale, solo demo | global:1/13 |
| `t0.r10.c1` | P.IVA: IT01234567890 (dato simulato) | **Falso negativo PDF**; letterale, solo demo | global:1/13 |
| `t0.r11.c1` | Telefono: +39 080 000 2040 (recapito simulato); cellulare non disponibile | **Errore di composizione**, UNKNOWN | Nessuna prova contiene il valore completo |
| `t25.r0.c1` | 5.d denominazione: Mapi Ingegneria S.r.l. | Corretto, già validato | global:1/10; global:2/12 |
| `t25.r4.c1` | 5.d forma: Società a responsabilità limitata | Corretto, già validato | global:1/11; global:2/13 |
| `t25.r4.c3` | 5.d sede: Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | Corretto, già validato | global:1/20; global:2/28 |
| `t26.r0.c1` | Direttore tecnico: Ing. Elisa Romano | Corretto, già validato | global:1/51; global:2/59 |
| `t26.r1.c1` | Qualifica direttore: Ingegnere | Corretto, già validato | global:2/61 |
| `t26.r3.c1` | Ordine direttore: Ordine degli Ingegneri di Bari | Corretto, già validato | global:1/52; global:2/62 |
| `t26.r4.c1` | Albo: 8421 (iscrizione professionale simulata) | **Errore di composizione**, UNKNOWN | Nessuna prova contiene il valore completo |
| `t44.r1.c0` | Parte terza, direttore tecnico: Ing. Elisa Romano | **Falso negativo condizione composta** | global:1/51; global:2/59 |

`global:1` è la visura PDF simulata; `global:2` è la scheda Markdown delle
generalità. Quest'ultima deriva in parte dalla prima: le citazioni ripetute non
sono prove indipendenti. I due identificativi fiscali, annotazione inclusa,
compaiono integralmente nella riga 13 del PDF. Sono accettati **come valori
documentati della bozza dimostrativa**, senza attestare formato, validità fiscale
o utilizzabilità reale. La seconda citazione Markdown non contiene l'annotazione
e rimane correttamente respinta. Nessun valore è stato ritagliato o riscritto.

Per il telefono, le righe global:1/23 e global:2/36 documentano rispettivamente il
recapito e l'indisponibilità del cellulare, ma nessuna contiene la stringa completa
composta dal modello. Per l'albo, global:1/51 e global:2/63 documentano `8421`,
mentre l'annotazione viene ricomposta nel valore. Restano bloccati secondo il
contratto letterale adottato; non sono conteggiati come falsi negativi.

Correzioni del prototipo:

- Copertura calcolata dai **279 ID reali su 279**, con 15 sezioni su 15.
  `coverage_count=400` è conservato e segnalato come avviso. Duplicati, omissioni,
  ID estranei, piano dichiarato incompleto e output troncato bloccano ancora
  l'export; il conteggio riepilogativo non autorizza né impedisce da solo scritture.
- Proprietà esplicite delle tabelle PDF riconosciute anche senza `:`. Ogni record
  resta associato all'organizzazione nominata o alla persona/ruolo espliciti;
  il seguito immediato dell'ordine professionale rimane legato al direttore.
- Una tipologia SOURCE esplicita può soddisfare un'alternativa intera nella
  lista FORM «da compilare ... a cura di». Non vengono dedotti partecipazione,
  appartenenze, poteri, esclusioni giuridiche o condizioni aggiuntive.
- Sede operativa «se diversa»: l'esclusione locale è verificata dalla relazione
  SOURCE esplicita di coincidenza delle sedi dello stesso operatore. Questo
  recupera un falso negativo ulteriore, **fuori dalle 14 proposte di valore**.
- La domanda mista sul direttore non perde più la richiesta della data di
  abilitazione: viene conservata separatamente per riformulazione, con riferimenti
  già risolti e ancora mancanti. Nove altre domande restano da valutare, una
  conferma ormai interamente risolta viene scartata. Nessuna viene inviata in chat.

Esito: **21/27 riferimenti SOURCE validati**, corrispondenti a 12 posizioni
documentali distinte; 12 VALIDATED, 10 NOT_APPLICABLE, 6 REVIEW e 251 UNKNOWN.
Rimangono UNKNOWN i rami la cui esclusione non è provata: comprese le 13 vecchie
assegnazioni sospette, senza riproporne alcuna. Il direttore non viene trasferito
ai rappresentanti; il ruolo di rappresentanza di Luca Ferri resta non verificato.

**Export parziale effettuato e ispezionato:** esattamente 12 celle compilate con
i valori proposti, altre 497 celle identiche, 13 parti accessorie identiche,
nessuna modifica XML ulteriore oltre all'avviso di bozza. DOCX riaperto con
python-docx; `document_completed=false`, `ready_for_submission=false`.

Artefatti locali, ignorati da Git:
[report offline](../backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/report.md),
[revisione manuale dei 14 valori](../backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/manual-review-14.json),
[audit export](../backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/export-audit.json),
[DOCX parziale](../backend/data/compilation-audit/global-one-shot-20261008/offline-review-20261008/replay-final/bozza-globale-parziale.docx).

La rappresentazione ridondante del FORM e la configurazione `thinking=disabled`
della chiamata storica non sono state cambiate: questo intervento rivaluta
l'output congelato e non misura una nuova configurazione del modello.

Verifiche finali: **181 test mirati passati in 13,94 s** (70 del prototipo e 111
regressioni script/DOCX/validazione), con provider simulati e dati temporanei;
Ruff backend completo passato. Nessuna suite completa o verifica frontend/E2E.
Preservazione confermata su 33 tabelle SQLite e 29 file applicativi.

## Limiti verificati

Il profilo locale seleziona `deepseek-flash`, endpoint ufficiale DeepSeek,
`context_window=32768`. Quest'ultimo valore viene applicato dal trasporto solo a
Ollama (`num_ctx`); non limita il contesto remoto DeepSeek.

La [documentazione dei modelli](https://api-docs.deepseek.com/quick_start/pricing/),
consultata l'8 ottobre 2026, dichiara **1M token di contesto** e **384K di output**.
L'[API Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)
specifica `max_tokens <= 393216`, condividendo il contesto fra input e output.
Non è pubblicato un limite token separato per JSON mode. Il massimo dichiarato
non è stato misurato saturandolo: la singola prova ha verificato l'accettazione
di `max_tokens=98304`, con input effettivo oltre 32.768 token.

| Percorso | Limiti applicativi rilevanti |
|---|---|
| CompilationSession attuale | 12 candidate per passo, output di ogni fase 8.192 token; classificazione con contesto massimo 60.000 caratteri |
| API DOCX precedente, già a chiamata unica | Output 32.768 token, risposta massimo 200.000 caratteri; selezione fonti per budget 40.000/90.000/20.000 caratteri |
| Prototipo globale | Una richiesta, output configurabile (default 98.304 token), deadline totale 1.800 s; nessun taglio degli input o retry |

Il prototipo usa lo stesso JSON mode della configurazione attuale, con schema
Pydantic completo nel prompt e validazione rigorosa nel backend. JSON mode
**non impone lo schema** al provider. DeepSeek documenta anche schemi tramite
tool strict e Responses API; questi percorsi non sono quelli provati qui.
Il [manuale JSON](https://api-docs.deepseek.com/guides/json_mode/)
richiede budget sufficiente e avverte di possibili risposte vuote/troncate.

Restano i limiti espliciti del parser DOCX condiviso: massimo 400 candidate,
60.000 caratteri nel corpo e 100.000 caratteri nel catalogo precedente. Il
prototipo non li confonde con il contesto disponibile presso DeepSeek.

## Uso

Dalla directory `backend`, con l'ambiente del README già installato:

```bash
uv run --locked python -m scripts.global_compilation_experiment \
  --session-id ID_SESSIONE \
  --output data/compilation-audit/ESPERIMENTO

# Una sola richiesta reale sugli input congelati appena preparati:
uv run --locked python -m scripts.global_compilation_experiment \
  --live --output data/compilation-audit/ESPERIMENTO

# Solo verifica locale della stessa risposta, senza chiamate al modello:
uv run --locked python -m scripts.global_compilation_experiment \
  --validate-only --output data/compilation-audit/ESPERIMENTO

# Rivalutazione offline su NUOVA copia, preservando tutti i risultati storici:
uv run --locked python -m scripts.global_compilation_experiment \
  --validate-only --replay-from data/compilation-audit/ESPERIMENTO \
  --output data/compilation-audit/RIVALUTAZIONE_NUOVA
```

Non riutilizzare un percorso per preparare un'altra prova. `--live` rifiuta una
richiesta già inviata, fallita dopo l'invio o terminata: non esistono correzioni,
fallback, suddivisioni o revisioni LLM. Un ConnectError prima dell'invio è
registrato separatamente e permette di eseguire la richiesta autorizzata quando
la connessione diventa disponibile. Timeout/errori dopo l'invio non consentono
questa ripresa, perché non si può sapere se il provider abbia già lavorato.

## Input e contratto

- FORM: tutti i paragrafi in ordine fisico, anche quelli senza candidate;
  tabelle e celle fisiche, merge e griglie, riferimenti alle note, numerazione,
  stili usati con dipendenze, note e header/footer. Formattazioni ripetute
  referenziate da un catalogo comune, senza eliminare testo. Tutti gli ID e le
  posizioni provengono dal parser dell'originale. I titoli condizionali vengono
  riconosciuti anche dentro celle. Il catalogo delle sezioni è deterministico;
  il modello non può spostare un candidate in una sezione di propria invenzione.
- SOURCE: documenti globali e fonti del progetto integrali, con ID, ruolo, scope,
  categoria, hash dell'originale e linee numerate. Nessun retrieval/top-k. Il
  testo PDF è quello estraibile con pypdf, con il suo limite nell'ordine di
  lettura. Moduli, bozze, template e sintesi automatiche non diventano prove.
- USER: decisioni della sola sessione scelta, con candidate/condizione e versione;
  `project-facts.md` conserva la provenienza USER separata dalle fonti. Non si
  mescolano decisioni di sessioni diverse. Le vecchie proposte SOURCE non
  rientrano fra gli input fattuali.

Le immagini del DOCX sono inventariate tramite i metadati, senza OCR implicito.
Nella prova reale l'unico disegno EMF contiene il logo della Fondazione, verificato
localmente dopo estrazione della bitmap. Non contiene campi da compilare. Per
moduli con contenuto significativo nelle immagini serve una rappresentazione
visiva/OCR esplicita prima di poter dichiarare completo l'input utile.

Il piano contiene entità e ruoli con prove, decisioni sulle sezioni e soggetto
della condizione, tutti i candidate con soggetto/sezione/valore/prova, domande e
warning. Ogni prova ha `origin`, `reference_id`, `line`, `quote`.
Il backend controlla schema, scope, ID, duplicati, omissioni, condizioni FORM,
identità/ruolo del soggetto e proprietà locale della SOURCE. Le condizioni di
tipologia non diventano decisioni sulla modalità di partecipazione.

Il validatore sperimentale ammette proprietà esplicite in record testuali con
etichetta e `:`, righe di tabella con etichetta maiuscola e ruoli personali
dichiarati nelle intestazioni Markdown o nei record PDF riconosciuti.
Questa copertura resta **limitata**, non è un giudizio di falsità sulle altre
prove. Le prove indipendenti sono controllate separatamente; una prova
non supportata non cancella un'altra prova valida della stessa proposta. Nessun
valore viene corretto, ritagliato o ricostruito dal backend.

Le esclusioni da sola tipologia giuridica non sono autorizzate. Le condizioni
composite o locali fuori dalle regole esplicite supportate restano UNKNOWN;
non esiste un risolutore generale di disgiunzioni e relazioni fra tutte le entità.
Firme protette. Copertura effettiva incompleta, troncamento, JSON/schema invalidi
o ID estranei impediscono l'export; un contatore dichiarato incoerente genera
un avviso. Gli esiti locali rimangono nel report. Ogni export è una bozza
parziale, mai automaticamente pronta all'invio.

## Esito storico della chiamata reale, prima delle correzioni offline

Tracce e confronto dettagliato, locali e ignorati da Git:
[report](../backend/data/compilation-audit/global-one-shot-20261008/report.md).
Input congelati da copia Catanzaro v102, con sette decisioni USER; le tredici
assegnazioni sospette della v83 sono confrontate separatamente.

| Misura | Risultato |
|---|---:|
| Chiamate reali al modello | 1 |
| Input / output effettivi | 213.628 / 35.887 token |
| Totale | 249.515 token |
| Durata invio + elaborazione locale registrata | 94,407 s |
| Candidate restituiti / attesi | 279 / 279 |
| Conteggio dichiarato dal modello | **400, incoerente** |
| Sezioni restituite / attese | 15 / 15 |
| Valori proposti / riferimenti SOURCE per tali valori | 14 / 27 |
| Valori e riferimenti ammessi localmente nella verifica finale | 9 / 9 |
| Valori scritti / DOCX esportati | **0 / 0** |
| Sezioni escluse con prova ammessa | 1: professionista singolo, decisione USER |
| Domande proposte | 11, con ridondanze e dipendenze da rivedere |

`finish_reason=stop`, JSON/schema validi, nessun ID candidate inventato o omesso,
nessun limite di output raggiunto: la risposta usa il 36,5% del budget assegnato.
Il precedente validatore segnalava `coverage_count=400` bloccando l'export, pur
essendo presenti tutti i 279 ID reali. Non era un troncamento. Il controllo degli originali
conferma invariati 33 tabelle SQLite e 29 file applicativi.

La verifica finale è **offline sulla stessa risposta**, non una seconda prova
AI. La prima versione del validatore respingeva l'intero valore quando una
citazione PDF non supportata precedeva una citazione Markdown valida, lasciando
un solo valore ammesso. Corretto il controllo per prove indipendenti, con test:
ora nove valori hanno almeno una prova valida; gli altri restano UNKNOWN.
Output, prompt e codice al momento della chiamata sono conservati, insieme ai
due report di validazione. Nessuna modifica per far passare il conteggio errato.

Il contesto globale evita le tredici vecchie scritture sospette e localizza
correttamente 5.g/consorziate. Tuttavia sostituisce quelle scritture con esclusioni
non sufficientemente provate; assegna inoltre `representative` all'amministratore
senza dimostrarne i poteri. Il backend respinge queste decisioni. Alcuni valori
contengono annotazioni o composizioni non letterali. Non è dimostrata una
superiorità sufficiente per sostituire la compilazione ordinaria.

## Integrazione minima, solo dopo una prova migliore

La possibile integrazione è un ingresso esplicito e opzionale nel resolver:
un'unica pianificazione globale da originale + fonti + decisioni USER, verifica
backend, importazione atomica dei soli risultati verificati nello snapshot
esistente con controllo di versione/hash. Riutilizzare writer e revisione
USER già disponibili. Nessun nuovo motore a gruppi e nessun fallback automatico
alla pipeline corrente dopo un fallimento globale.

Prima servono esiti migliori su condizioni, entità e domande, una copertura
adeguata della validazione SOURCE e un contratto di coverage affidabile. Il
contesto strutturale può essere reso più economico senza perdere testo o
gerarchie: la rappresentazione fedele usata qui consuma molti token di metadati.
Questa è una proposta, **non implementata né attivata**. Nessun'altra chiamata
reale e nessuna integrazione vengono eseguite in questo intervento.
