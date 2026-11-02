# Narratore fluido e compilazione incrementale — 2 novembre 2026

**Verifica conclusa il 3 novembre: branch non ancora promovibile nella demo.**
Il primo flusso incrementale è implementato e passa i test software; le prove
reali mostrano ancora limiti nella conferma del nuovo firmatario e nel nome sul
secondo FORM. Il ritiro dei dati della persona precedente funziona, ma non basta
per dichiarare completata la verifica funzionale richiesta.

Intervento nel solo worktree `tesi-narratore-chiarezza-20261031`, base
`930aeef9aa6b354e267c19dcbd5fa3d9c065bdaa`. Commit dedicato
`feat(compilation): add selective incremental conversation with guarded edits`.
Nessun merge, push o promozione. Profilo invariato
`sezioni-2026-10-30-r2`; `conversation_revision=1` soltanto nelle nuove sessioni.
Le sessioni reali precedenti non vengono aggiornate implicitamente.

## Ricognizione e intervento

| Percorso | Stato alla base | Intervento |
|---|---|---|
| Domande | Fino a quattro; condizioni imposte e campi mancanti | Una domanda prioritaria per turno, prima conferme con dati documentati e conflitti; i vuoti secondari non diventano automaticamente domande |
| Contesto del narratore | Revisione delle proposte a finestre, condizioni e sospensioni | Conservato completo: la selezione riguarda la presentazione, non la revisione delle evidenze |
| Router USER | Soltanto gli slot della domanda attiva | Destinazioni FORM note disponibili anche fuori domanda e dopo l'export; istruzioni libere con `edit_fields` |
| Risposta multivalore | Estrattore atomico con guardia per ogni dato | Riutilizzato; recupera la frase contigua completa quando il router accorcia la citazione, evitando il limite dei quattro primi dati |
| Correzioni | Destinazioni risolte non sempre raggiungibili dalla chat | Vecchi valori/ricevute conservati nello storico; nuova indicazione sottoposta agli stessi controlli |
| Cambio persona | Riuso SOURCE già disponibile, valori USER dipendenti persistenti | Ritiro dei dati personali e delle conferme dipendenti; ricalcolo SOURCE, nessun trasferimento automatico alla nuova persona |
| Pausa/ripresa | Già persistenti | Conservate; possibile esportare lo stato già validato durante la pausa senza riprendere l'analisi |
| Bozze successive | Writer dall'originale e artefatti separati già esistenti | Riutilizzati; correzioni accettate dopo l'export e riapertura esplicita dei punti rinviati |
| Errore UI | Testo conservato e recuperabile, rilettura dello stato | Nessuna modifica frontend; rieseguiti test automatici e browser |

La nuova mappa dei destinatari contiene etichette e contesto FORM, stato e valori
correnti. Non è una lista di autorizzazioni. Il router non sceglie identificativi
DOCX: i numeri sono risolti dal backend sulla stessa revisione persistita.
Una domanda di spiegazione resta una lettura; `nessuna_proposta` non viene
presentato come prova dell'assenza nelle SOURCE. Sono riutilizzati il recupero
limitato dell'analisi e il riuso documentale della persona selezionata; non è
stato aggiunto un secondo motore di ricerca o compilazione.

Per `REOPEN` viene riaperta la discussione, mantenendo il blocco alla scrittura.
`SKIP`/`REFUSE` ritirano la destinazione anche se esiste una precedente proposta
SOURCE. Il testo originale resta nella conversazione/traccia e nelle istruzioni
acquisite. Destinazioni o significati incerti richiedono chiarimento.

Le istruzioni libere passano dalla guardia indipendente, anche per rinvio e
riapertura. Per esse non viene simulata una domanda precedentemente mostrata né
attivata l'eccezione delle conferme chiuse. La conferma ordinaria mantiene invece
il proprio ambito visibile e i controlli già esistenti. Nessun cambiamento al
compilatore per sezioni, al writer o ai criteri di autorizzazione delle dichiarazioni.
Nelle nuove sessioni le sole proposte SOURCE non selezionano checkbox: occorre
la scelta USER, ancora sottoposta a scope e cardinalità.

## Verifiche e difetti osservati durante lo sviluppo

- Test prima dell'implementazione: cinque fallimenti sul flusso richiesto.
  Rollback successivo più ampio: 18 fallimenti sulla base `930aeef`, 18 passaggi
  con la modifica riapplicata in copia; worktree originale non ripristinato.
- Prima suite generale: 4.341 passaggi, 8 skip, due fallimenti. La selezione era
  stata applicata troppo presto al pool delle condizioni; separata la revisione
  completa dalla singola domanda mostrata. Il test preesistente resta invariato.
- Prima prova reale Minervino: conferme troppo brevi prive dell'ambito visibile,
  rifiuti della guardia e bozze vuote. Ripristinate le destinazioni visibili,
  eliminando soltanto il conteggio tecnico. Non sono stati rilassati i verdetti.
- Il router reale ha restituito quattro dati atomici e omesso la residenza. Il
  nuovo adattamento conserva la frase personale completa e riusa l'estrattore.
- Un ulteriore output reale mescolava `answer_fields` ed `edits`: rifiuto dello
  schema; il retry precedente invitava erroneamente a usare soltanto gli slot
  attivi. Le istruzioni di riparazione ora conservano la possibilità di modifiche
  libere. Test sul contratto errato registrato, senza recuperi che aggirino la guardia.
- Un test su «Nome e cognome del referente» ha incontrato il controllo di
  completezza preesistente che richiede SOURCE: limite conservato, non allentato.
  L'altro FORM offline usa «Nominativo del referente» e verifica nomi con apostrofo,
  ritiro, riapertura, pausa/ripresa e correzione, oltre al FORM del sottoscrittore.

Suite backend finale, congelata dopo l'ultima modifica: **4.347 PASS, 8 SKIP**
in 467,51 secondi (`full-suite-frozen.txt`). I 18 nuovi test passano; gli stessi
18 falliscono sulla base senza intervento e passano dopo la riapplicazione in
copia. Gli hash dei nove file applicativi/test corrispondono alla copia testata
nel rollback (`rollback.json`, `integrity.json`). Ruff e `git diff --check` PASS;
Graphify aggiornato soltanto via AST, senza chiamate AI.

Frontend: **188 test PASS; quattro E2E desktop PASS** su `5174` con API simulate,
inclusa la ripresa dopo errore di lettura. Non sono prove DeepSeek o prove browser
sul backend reale. Le verifiche backend usano database/storage temporanei,
con FTS5 e Qdrant nei test parametrizzati. Frontend non modificato; lint/build
frontend non rieseguiti. Il recupero UI è verificato dai test già presenti, non
da un nuovo guasto riprodotto con il provider reale.

## Protocollo reale e confronto

DeepSeek reale: `deepseek-flash`. Minervino riusa la proposta/analisi registrata,
con interazioni, guardia e narratore reali; Labirinto usa il FORM e le sette fonti
congelate di `demo-documents/benchmark-compilazione/v1/`, con nuova analisi reale.
Gold escluso dai prompt. Conferme e correzioni sono messaggi USER sintetici di
prova, non risposte attribuite all'utente reale.

Il primo esperimento fallito è conservato; il secondo parte dallo stesso
checkpoint e prosegue nella medesima sessione. Il budget massimo è stato portato
da 40 a 48 e poi 56 chiamate complessive per verificare i difetti osservati e il
secondo FORM; non vengono ripetute analisi per cercare un output migliore.
Gli export HTTP e i controlli pausa/ripresa eseguono il dominio reale senza
chiamate LLM aggiuntive. Le istruzioni libere e le relative guardie sono reali.

Sul medesimo checkpoint iniziale Minervino: **quattro domande nella presentazione
registrata, una nella selezione nuova**. La presentazione storica viene dalla
sessione `a0cc223`; `930aeef` è la base del codice modificato, non una nuova
generazione reale usata come controllo. Questo misura la presentazione, non
l'accuratezza, la completezza né una riduzione già dimostrata dei turni totali.
Le 50 proposte documentate dell'audit iniziale non vengono eliminate dal filtro
delle domande. Non è un confronto statistico fra due campagne reali.

## Risultati reali

### Minervino: risposta multivalore e prima bozza

Input: «Il sottoscrittore è Leonardo Montemurro, nato a Lecce (LE) il 14/11/1982,
residente a Bari (BA), via Amedeo 24.» La frase produce sette valori USER e
ricevute indipendenti, passati dalla guardia; CF e carica sono riutilizzati dalle
SOURCE. Applicabilità, identità e operatore richiedono conferme USER separate.

In `minervino-revision2/complete-draft-1/` il DOCX contiene **37 scritture**
(30 SOURCE, 7 USER), comprese tutte le nove destinazioni del sottoscrittore:

| Destinazione | Valore effettivo | Provenienza |
|---|---|---|
| `p12.s0` | Leonardo Montemurro | USER |
| `p12.s1`, `p12.s2`, `p12.s3` | Lecce, LE, 14/11/1982 | USER |
| `p13.s0`, `p13.s1`, `p13.s2` | Bari, BA, Amedeo 24 | USER |
| `p13.s3` | MNTLRD82S14E506X | SOURCE |
| `p14.s0` | amministratore unico e rappresentante legale | SOURCE |

Confronto delle sole scritture testuali con il gold congelato: 34 valori identici;
tre differenze esplicite sono la carica più estesa ma documentata, l'omissione
del titolo facoltativo «Ing.» e «Bari (BA)» invece di «Bari». Non sono conteggiate
come errori di attribuzione; i dettagli restano in `final-summary.json`.
Questo confronto non misura la completezza dell'intero modulo.

Il rapporto segnala **22 campi dei soci sospesi** e un campo senza proposta
(`p17.s1`). Le sospensioni dichiarano dipendenza dalla qualità del firmatario,
con `blocker_key=choice:form_capacity_19`. Nella demo R2 era stata scelta
esplicitamente la checkbox 4; qui non è stata scelta alcuna checkbox. Non si
può quindi chiamare regressione la differenza fra le 59 scritture della vecchia
demo e le 37 attuali. La pertinenza delle sospensioni richiede verifica separata.
Inoltre il copione di questa prova ha confermato esplicitamente il punto
sull'albo, che nella prova manuale precedente era rinviato: altra differenza
di decisioni USER, non un replay integrale a condizioni identiche.

### Minervino: ambiguità e cambio persona

Il negativo con «Mario Rossi oppure Leonardo Montemurro» e decisione ancora
aperta è trattato come richiesta di chiarimento: nessuna modifica a valori,
ricevute o DOCX nel checkpoint provato (`ambiguous_unchanged=true`). Questo
negativo precede la bozza completa: non è una prova negativa sullo stato da 37
scritture.

La successiva istruzione «Il firmatario scelto è Mario Rossi, non Leonardo
Montemurro. Metti Mario Rossi nel campo Il sottoscritto…» viene accettata per il
nome. I dati personali e le conferme dipendenti di Leonardo sono ritirati.
Tre ulteriori richieste di ritiro generate dal router sono respinte come fuori
ambito: la ricevuta può quindi risultare ancora lunga.

**La seconda bozza ha zero scritture.** Il ritiro impedisce di attribuire CF,
carica, nascita e residenza di Leonardo a Mario, ma riapre anche le conferme
del partecipante collegate al blocco personale. Il tentativo successivo
«Confermo che il sottoscrittore di questa domanda è Mario Rossi…» viene ancora
instradato come `VALUE` su `field:p12.s0`, con guardia positiva, anziché come
conferma della condizione `s1_c_firmatario`. La ricevuta dichiara correttamente
`usable_for_draft=false`; la condizione resta `unknown`. Nel rapporto finale
29 campi sono in condizione aperta, 22 sospesi e uno senza proposta; gli altri
dati personali precedenti sono stati ritirati. Nessun nuovo nome nel DOCX.

Non è un rifiuto della guardia e non è una correzione riuscita fino all'export.
La scelta del destinatario della conferma e l'ampiezza delle dipendenze da
riconfermare restano punti da verificare; nessuna deroga introdotta per far
scrivere il documento. Evidenze: `replace-person/`,
`new-identity-confirmation/`, `new-identity-draft/`.

### Altro FORM: Labirinto V1

Nuova analisi reale di FORM e sette SOURCE congelate. Prima bozza:
**11 scritture SOURCE, tutte identiche al gold** per le destinazioni scritte.
Firma, scelte e dichiarazioni non sono autorizzate automaticamente.

«Metti Paolo Conti nel campo Il sottoscritto» supera router e guardia, ma il
validatore restituisce `Valore composto USER incompleto o senza prove SOURCE`
per `t2.r0.c1`, etichetta «Il sottoscritto — Nome e cognome». Nessun nome scritto.
È il controllo di completezza preesistente incontrato anche offline; non è
stato allentato. Il test positivo con altro FORM/etichetta non dimostra che
questa variante funzioni: il limite è conservato esplicitamente.

«Correggi la PEC dell’operatore economico: usa ufficio@pec.example.org nel campo
PEC» viene invece applicato fuori dalla domanda corrente con guardia e
ricevuta. La nuova bozza contiene **11 scritture (10 SOURCE, 1 USER)**; la cella
`t0.r6.c1` contiene la nuova PEC, mentre la prima conserva
`orione@pec.example.org`. Dieci valori restano uguali al gold, uno cambia per
istruzione USER esplicita. Confermata l'immutabilità dei file già esportati.

### Misure complessive e sicurezza osservata

| Esecuzione | Chiamate reali | Token input | Token output | Totale |
|---|---:|---:|---:|---:|
| Minervino, primo tentativo fallito | 14 | 221.707 | 1.970 | 223.677 |
| Minervino, secondo tentativo e prosecuzioni | 31 | 476.635 | 5.033 | 481.668 |
| Labirinto, analisi e correzioni | 8 | 87.829 | 20.033 | 107.862 |
| **Totale** | **53** | **786.171** | **27.036** | **813.207** |

Fonte unica per il totale: `all-calls.json`; include tentativi falliti, retry e
recupero dell'analisi Labirinto. 53 risposte HTTP riuscite non equivalgono a 53
operazioni applicative riuscite. Tempo cumulato misurato delle richieste:
181,328 secondi, esclusi preparazione, export e test. Nessuna misura monetaria.
Non è dimostrato un risparmio complessivo di chiamate, token o turni: è una
verifica di sviluppo su due FORM, non una campagna statistica.

Controllati **12 DOCX**, rapporti e copie nello storage: hash coerenti, bozze
precedenti immutate, dicitura «BOZZA NON VERIFICATA» presente, **zero checkbox
selezionate** anche nell'XML Word. Nel campione non risultano nuove dichiarazioni
o designazioni professionali autorizzate implicitamente né trasferimenti dei
dati personali di Leonardo a Mario. Questo non è una prova generale di assenza
di violazioni. Nei test offline sono verificati anche export diretto di campi
ritirati, riapertura senza autorizzazione, pause e ripresa da persistenza.

Il riepilogo iniziale può ancora essere lungo; la gestione di nomi e condizioni
dipende dalle destinazioni FORM riconosciute. Non è stata introdotta una ricerca
SOURCE universale a ogni messaggio. I dati non valutati, mancanti e sospesi restano
distinti, ma il nuovo filtro delle domande non elimina i limiti della proposta
iniziale o della revisione semantica. La sicurezza conservativa è mantenuta;
la fluidità completa richiesta non è ancora dimostrata.

## Evidenze e rollback

Acquisizioni locali: `backend/data/compilation-audit/narratore-fluido-20261102/`.
Contengono protocolli, prompt/schema/output HTTP, ricevute/stati, rapporti e DOCX,
log delle suite, confronto offline e verifica del rollback. Le credenziali non
sono incluse; i database copiati sono privati di profili/chiavi e sottoposti a
VACUUM. La scansione dei byte con la chiave effettiva in memoria non trova
credenziali. `baseline.json` e `protected-after.json` sono identici per hash
di tutte le tabelle dei due database originali, stato/diff Git ordinario e tag
demo `3a8de0b4fb617c0f28e5cda0b1e10d97c40bb19f`.

Backup separato delle acquisizioni e della consegna:
`/home/montesano/tesi-backups/narratore-fluido-20261102/` (archivio e manifest SHA256).
Gli artefatti ignorati non sono inclusi nel commit. Le modifiche documentali e
le rinominazioni già presenti prima del task sono preservate e non incluse nel
commit dell'intervento.

Rollback: ripristinare il commit base `930aeef` in una copia/worktree dedicata;
non usare reset sul worktree con modifiche preesistenti. Le sessioni create con
la revisione conversazionale restano isolate e non devono essere trasferite alla
demo o reinterpretate con il codice precedente. Nessuna migrazione della demo.

Le prove reali hanno usato il dominio applicativo e le API ASGI su runtime
isolati, non il backend ordinario. Il frontend `5174` è stato avviato soltanto
per gli E2E simulati e poi fermato; non viene dichiarata pronta un'istanza manuale
`5174/8001`. I servizi ordinari non sono stati riavviati o modificati.

**Decisione:** conservare il commit sperimentale e le evidenze, senza promozione.
Per dichiarare il flusso completo servono ancora una conferma/correzione reale
del nuovo firmatario fino al DOCX e una soluzione verificata al nome sul secondo
FORM, senza scavalcare condizioni o validatori. Nessun ulteriore intervento o
campagna avviato dopo questo rapporto.
