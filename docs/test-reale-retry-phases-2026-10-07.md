# Retry separati: implementazione e benchmark reale — 7 ottobre 2026

## Ambito e base

Base `main`, HEAD `a5e2e2ea75924b86fcdb01074c067f909fa7e0cd`; nessun commit/push.
Preservate le modifiche locali iniziali di `start.sh`, `README.md` e `STATUS.md`.
Nessuna modifica a UI, parser DOCX, renderer, gate SOURCE o grouped clarifications.

## Flusso precedente realmente osservato

1. `automatic_fields` includeva PENDING e MISSING con requisito ed errori SOURCE,
   usando per entrambi `chat_workflow.analysis_attempts`, massimo due.
2. `claim_resolution` selezionava fino a 12 candidate (6 al retry), incrementando
   il contatore di tutti i selezionati prima della chiamata al classificatore.
3. `resolve_session` azzerava requisito e ricerca anche dei MISSING interpretati;
   classificava tutto il gruppo, poi retrieval, matcher e validazione SOURCE.
4. `request_structured` validava l'intero oggetto: un item invalido annullava
   il batch. `mark_failed` registrava FAILED; il recupero automatico degli errori
   strutturati attribuiva la rejection a tutto il gruppo. Nessuna restituzione
   dei tentativi: dopo due selezioni il candidate usciva dal lavoro automatico,
   anche se il suo retrieval SOURCE non era stato raggiunto.

## Correzione minima implementata

- `analysis_attempts` conserva il ruolo di budget di interpretazione;
  `source_attempts` è un secondo dizionario persistente nel JSON del workflow.
  Massimo due tentativi per fase/candidate; nessuna nuova tabella o migrazione.
- La selezione forma batch omogenei per fase e dà precedenza al lavoro SOURCE
  disponibile. Il retry SOURCE conserva requisito, grounding FORM e applicabilità
  e non richiama il classificatore.
- Per i nuovi candidate validamente interpretati resta possibile la risoluzione
  SOURCE nello stesso passo. La revisione `source_start` conserva gli esiti di
  interpretazione e riserva i soli tentativi SOURCE realmente avviati prima del
  retrieval, anche in caso di failure successivo o crash.
- Item identificabili e distinti vengono validati separatamente. Gli item validi
  restano utilizzabili; quelli invalidi portano un errore locale. Envelope
  invalido, JSON malformato e ID non localizzabili/duplicati/sconosciuti conservano
  failure globali. Provider e timeout non diventano successi silenziosi.
- Il recupero globale riguarda gli ID della fase attiva e riconosce la revisione
  iniziale anche dopo `source_start`. PAUSE/correzioni concorrenti conservano
  precedenza tramite controllo ottimistico.
- Le conferme di applicabilità riaprono il budget SOURCE pertinente. Ripresa
  del ciclo e rinvii non ricaricano i contatori dei retry.
- Le sessioni legacy senza il nuovo contatore conservano prudenzialmente il
  budget condiviso già consumato per i field interpretati. Nessuna riparazione
  automatica dei dati precedenti. Il riesame esplicito API mantiene la precedente
  semantica di riclassificazione.

File: `compilation_clarifications.py`, `compilation_sessions.py`,
`compilation_session_resolution.py`, `compilation_session_models.py` e commento
in `compilation_session_routes.py`. Gli schemi inviati al provider rimangono
invariati: gli errori locali sono attributi privati esclusi dallo schema.

## Verifiche software effettive

Provider simulati e database/storage temporanei, distinti dalle prove reali.

- **27 nuove regressioni**, FTS5/Qdrant dove previsto, incluse le cinque proprietà
  Company KB, isolamento dei counter, failure locali/globali, esaurimento bounded,
  conservazione del requisito e conferma di applicabilità dopo due interpretazioni.
- **211 test mirati finali** su retry, grouped, controlli, active question e guardie:
  passati. Le verifiche precedenti avevano coperto anche sessioni/SOURCE/validazione.
- **Suite backend finale: 1.146 passati in 302,18 secondi**, eseguita separatamente
  dall'indicizzazione reale. Ruff e `git diff --check` passati.
- Frontend non modificato né ritestato. Le suite backend esistenti verificano
  grouped, SKIP, UNKNOWN, PAUSE/RESUME e distinzione FORM/SOURCE/USER.

Prima della versione finale: una suite da 1.142 era passata; una successiva da
1.144 aveva avuto due timeout sotto pressione RAM, entrambi passati al riesame.
La successiva suite da 1.146 sopra è l'esito autorevole sul codice finale.

Il primo benchmark è stato concluso a codice congelato. Un controllo finale ha
poi riprodotto una regressione nel reset: un candidate review senza requisito,
con due interpretazioni già spese, non ripartiva dopo CONDITION_TRUE. Corretto
`reopen_phase_attempts` per riaprire soltanto la fase necessaria, test mirati e
suite completa rieseguiti. Il benchmark finale sotto usa una nuova sessione su
questa versione; nessun codice modificato durante nessuna delle due prove.

## Preparazione del benchmark

Archivio isolato persistente in
`backend/data/compilation-audit/retry-phases-20261007-final/` (escluso da Git).
Il primo archivio `retry-phases-20261007/` resta conservato separatamente.
Dati dell'applicazione principale e vecchie sessioni non modificati.
DeepSeek reale, modello `deepseek-flash`; Qdrant locale reale, embedding BGE-M3
tramite Ollama. Tre documenti globali come nella KB locale: generalità e visura
Company (14 chunk), direzione lavori/sicurezza General (3 chunk). Bando e
disciplinare Catanzaro come SOURCE del progetto e DOCX come FORM: totale
214 chunk indicizzati, con scope/role/category conservati.

L'indicizzazione iniziale a batch standard ha avuto timeout; il journal di
Ollama documenta `Failed with result 'oom-kill'` alle 14:10:38. Preparazione
ripresa un frammento alla volta con embedding reali, stessi ID, metadati e
content hash della pipeline, senza cambiare codice applicativo o gate. La
successiva riconciliazione ordinaria deve risultare senza chunk da aggiornare.

Modulo: `demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx`,
279 candidate, SHA-256
`5b3ad083522b9261c3c45584ac5ce08d73996269eaf0c6c07b7b8c3df3974563`.
L'originale storico dei report aveva hash
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`;
quei byte e gli audit grezzi del vecchio PC non sono disponibili. Stesso modulo
logico e numero di candidate, non una prova di identità byte per byte.

Rinvii USER del benchmark: soltanto «Salta per ora questo chiarimento», con slot
numerati nei gruppi. Nessun valore aziendale/professionale fornito manualmente;
nessuna scelta di applicabilità inventata. Eventuali «riprendi» sono controlli
separati. Questo misura avanzamento e batching dei checkpoint, non qualità di
risposte fattuali di un utente reale.

## Esito reale finale e metriche

Nuova sessione `382b44b883524bc1a908d4b8515a36e2`, progetto isolato
`benchmark-retry-separati-catanzaro`. Corpus e indice preparati copiando
l'archivio di prova precedente; nuova conversazione/sessione con tutti i 279
candidate PENDING e counter vuoti. La sessione precedente è conservata.
Stato finale WAITING_FOR_USER, `question.kind=deferred_summary`,
`auto_continue=false`, `last_generation=null`. Nessun READY né DOCX generato.

| Metrica | Risultato |
|---|---:|
| Candidate totali/processati almeno una volta | 279 / 279 |
| Candidate con stato diverso da PENDING | 156 |
| Candidate con tentativo SOURCE | 142 |
| RESOLVED / SOURCE (conteggio formale) | 17 |
| USER_PROVIDED | 0 |
| NOT_APPLICABLE | 6 |
| MISSING | 123 |
| AMBIGUOUS | 10 |
| CONFLICTING | 0 |
| DEFERRED | 129 |
| PENDING | 123 |
| Ignorati/non-field | 6 |
| Checkpoint USER | 34 |
| Turni USER di chiarimento | 34 |
| Turni aggiuntivi di resume | 0 |
| Chiarimenti medi per checkpoint | 3,79412 |
| RESOLVED prima del primo checkpoint | 17 |
| Passi automatici | 69 |
| Richieste modello di risoluzione acquisite | 135 |
| Tempo del protocollo, esclusa preparazione indice | 458,4 secondi |

DEFERRED è una disposizione ortogonale: non sommarla agli stati. I sei ignorati
sono NOT_APPLICABLE / FORM, non esclusioni fattuali dell'azienda. I 34 turni USER
sono SKIP, senza valori o scelte di applicabilità inventate. I 135 raw coprono
classificazione/pianificazione/matcher, non il planner chat dei rinvii.
Quattro AMBIGUOUS (`t3.r3.c0`–`t3.r6.c0`) restano non proponibili perché senza
requisito grounded/ricerca SOURCE; insieme ai 123 PENDING rimangono aperti.
Non sono stati trasformati artificialmente in non-field o valori USER.

Il primo checkpoint arriva dopo 36 passi: 17 RESOLVED, 73 MISSING,
9 AMBIGUOUS e 180 PENDING; 153 candidate processati, 91 con tentativo SOURCE.
Ha un singolo chiarimento di applicabilità; i gruppi successivi arrivano a
quattro. Totale: 129 slot su 34 checkpoint. La prova non impone gruppi da quattro
quando soggetto/condizione non consentono raggruppamento.

## Prove reali della separazione dei retry

Controllate tutte le revisioni persistite:

- 61 claim di interpretazione: dizionario SOURCE invariato rispetto alla
  revisione precedente.
- 8 claim di retry SOURCE: dizionario di interpretazione invariato.
- 29 transizioni `source_start`: nessun tentativo di interpretazione aggiuntivo.
- Totali: 433 interpretazioni e 163 SOURCE; 21 candidate con secondo tentativo
  SOURCE. Massimo due in entrambe le fasi. Nessuna violazione contabile incrociata,
  nessun failure globale di schema nella sessione.
- Sei output reali misti conservano gli item conformi: raw 061 (5 validi/1
  invalido), 064 (4/2), 093 (4/2), 094 (4/2), 107 e 110 (5/1 ciascuno).
  Conformità allo schema non implica grounding o risoluzione del valore.

**Caso positivo reale:** `t25.r4.c1`, forma giuridica della società di ingegneria:
`state-step-021.json`, v52: MISSING, SOURCE attempt 1, errore «SOURCE non ammessa
per questo candidate». `state-step-022.json`, v54: RESOLVED/SOURCE,
`Societa a responsabilita limitata`, SOURCE attempt 2; interpretation attempt
resta 1. La riclassificazione non è richiamata per quel retry. Gli altri
candidate PENDING non ne consumano il budget e il secondo tentativo può riuscire.

Il punto di arresto precedente è superato: tutti i 279 candidate sono visitati
e ingegneria viene raggiunta. Gli altri 20 retry SOURCE non risolvono il field:
il fix dei budget non elimina errori di grounding, retrieval o proposta.

## Campi richiesti: controllo effettivo finale

| Campo | Candidate | Esito | Evidenza/limite |
|---|---|---|---|
| Operatore economico | t0.r5.c1 | MISSING | Bucket del primo batch dominato da SOURCE di gara, privo della proprietà Company pertinente. |
| Forma giuridica iniziale | t0.r6.c1 | PENDING | Due name parafrasati «Forma giuridica dell'operatore economico», non letterali nel form_quote; SOURCE non avviata. |
| Sede legale iniziale | t0.r7.c1 | MISSING | Bucket di gara, non sede Company. |
| Codice fiscale operatore | t0.r9.c1 | MISSING | Fonte Company pertinente fuori dal bucket selezionato. |
| Partita IVA operatore | t0.r10.c1 | MISSING | Stesso limite della ricerca CF. |
| Denominazione società di ingegneria | t25.r0.c1 | RESOLVED / SOURCE | Mapi Ingegneria S.r.l., global/company. |
| CCIAA, società di ingegneria | t25.r2.c0 | MISSING | Estremi completi non disponibili in KB; REA non è sostituto della CCIAA. |
| Numero/data iscrizione | t25.r3.c1 | MISSING | Data disponibile, numero Registro Imprese non disponibile; campo composto non risolto. |
| Direttore tecnico, nominativo | t26.r0.c1 | MISSING | Elisa Romano presente in KB, ma non proposta/validata nel bucket. |
| Qualifica direttore tecnico | t26.r1.c1 | MISSING | Ingegnere presente in KB; mancata risoluzione. |
| Data di abilitazione | t26.r2.c1 | MISSING | Esplicitamente non disponibile nella KB. |
| Ordine direttore tecnico | t26.r3.c1 | PENDING | Person_role non letterale nel form_quote; Ordine degli Ingegneri di Bari presente in KB. |
| Numero albo 8421 | t26.r4.c1 | PENDING | Due interpretazioni senza person_role grounded nel form_quote; SOURCE non avviata. |

In ingegneria anche `t25.r4.c1` (forma) e `t25.r4.c3` (sede) sono SOURCE con i
valori Company previsti. CF/PIVA `IT01234567890` compare RESOLVED/SOURCE nel
campo combinato `t38.r5.c1`, ma questo NON risolve i cinque field iniziali.
Questi cinque non sono riprodotti come RESOLVED in questa prova reale; le
regressioni software sui cinque valori sono passate, non equivalgono a stabilità
qualitativa del workflow reale. Le prove SOURCE conservano role/scope/category,
span e validazione; non certificano soggetto/applicabilità di ogni sezione.

## Rischi osservati, non corretti durante i benchmark

I 17 RESOLVED sono un conteggio formale, non 17 valori tutti corretti.
Almeno `t31.r0.c1`, denominazione societaria nella sezione società tra professionisti,
è semanticamente errato: `FONDAZIONE UNIVERSITA’ MAGNA GRAECIA` identifica
l'amministrazione appaltante, non la società/il soggetto concorrente.
Non corretto durante la prova e non presentato come successo fattuale.

Nel benchmark preliminare erano stati accettati anche REA per numero Registro
Imprese `t19.r3.c1`, REA per CCIAA `t31.r2.c0` e stazione appaltante per consorzio
`t40.r0.c1`. Sono esiti della prova precedente, non del conteggio finale.
Il diverso risultato delle due inferenze non dimostra una correzione di queste
associazioni: quei gate non sono stati modificati. Resta necessario verificare
proprietà, soggetto e applicabilità prima di considerare affidabili le assegnazioni.

Restano falsi negativi del primo batch: MISSING senza errori di validazione non
vengono automaticamente ricercati di nuovo dalla selezione preesistente, anche
se la KB contiene i valori. Il fix separa e conserva i tentativi; non estende
indiscriminatamente l'eligibilità di tutti i MISSING. Label/person_role non
letterali restano PENDING dopo due interpretazioni, senza domande su dati non cercati.

## Confronto con le prove precedenti

| Prova | RESOLVED | MISSING | AMBIGUOUS | PENDING | Checkpoint/turni |
|---|---:|---:|---:|---:|---|
| SOURCE circoscritta storica `46d5be7…` | 5, i cinque iniziali | 0 | 0 | 274 | Zero valori USER; resolve mirato. |
| Grouped storica `45474e57…` | Fino a 22 | Non documentati completi | Non documentati completi | Non documentati completi | Stop prima della misura completa. |
| Grouped storica finale `8361b0e…` | 12 | 32 | 3 | 232 | Pausa prima del termine. |
| Nuova preliminare `32ecd6c5…` | 12 formali | 112 | 11 | 138 | 32/32, media 3,72. |
| Nuova finale `382b44b8…` | 17 formali | 123 | 10 | 123 | 34/34, media 3,79. |

Avanzamento e batching sono misurati fino al riepilogo; ingegneria è raggiunta.
Più MISSING significa anche più field cercati; non equivale da solo a perdita
di dati. I cinque valori iniziali della prova SOURCE circoscritta non sono
riprodotti. Gli hash DOCX/corpus storici diversi limitano il confronto causale;
nessuna percentuale di miglioramento o equivalenza degli input irrecuperabili.
La differenza preliminare/finale non è attribuita al reset dei counter: il
protocollo reale usa SKIP e non esercita CONDITION_TRUE; le inferenze possono
variare. La correzione del reset è coperta dalle regressioni software.

## Acquisizioni e prossimo passo

Archivio finale `backend/data/compilation-audit/retry-phases-20261007-final/`:
`inputs.json`, `index.json`, `state-initial.json`, `state-step-*.json`,
`state-final.json`, `revisions.json`, `model-*-request.json`, `model-*-raw.txt`,
`checkpoints.json`, `user-turn-*.json`, `metrics.json`, `verification.json`,
`code-hashes-before.json` e `code-hashes-after.json`. Archivio preliminare
conservato. Nessuna credenziale nei report/acquisizioni dei prompt; DB e
profilo cifrato locali esclusi da Git, non allegati al report.
Hash del codice e del DOCX invariati prima/dopo ciascuna prova.

Riprendere dalle query/bucket Company del primo batch e dal grounding
name/person_role di direttore/ordine/8421, poi dal falso positivo di soggetto
`t31.r0.c1`. Non rifare retry separati, UI, parser, renderer o grouped.
Nessun'altra correzione applicata durante i benchmark; nessun commit/push.
