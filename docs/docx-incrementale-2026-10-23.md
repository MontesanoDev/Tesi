# Compilazione DOCX: interventi incrementali offline, 23 ottobre 2026

Base dello sprint `ff0d4f9140d2421fe2631e890ccd522c64c05fab`; branch
`miglioramenti/2026-10-23-docx-offline`, worktree `/home/montesano/tesi-docx-offline`.
Nessuna inferenza, nessuna E2E, nessuna adozione live. V12 e gli esperimenti
storici sono preservati. Revisione autoriale, non indipendente.

## Stato Git verificato

Il fetch di origin conferma i branch pubblicati. `main` è ancora `b8071d3` e
non contiene l'hotfix. La base del lavoro recente è `dd41e2e`; lo sprint termina
in `ff0d4f9`. L'hotfix generale esiste in `4890daa` sul branch security, ma nello
sprint il veto era presente soltanto per le sessioni rev 3. Il working tree
ordinario, molto modificato e su `prune-backend`, non viene usato per i commit.

## Priorità 1: integrazione dell'hotfix API esistente

Problema: un client dell'endpoint `global-draft` può chiedere esplicitamente un
ID SOURCE sospeso o non più revisionato. Nel profilo ordinario/P3 lo sprint
restituiva 200. La chat già escludeva tali ID. Il consenso alla bozza non è una
revisione delle singole sospensioni.

Riutilizzato `4890daa` con cherry-pick senza commit e verifica del diff: nello
sprint la funzione `reviewed_unheld_ids` esiste già. L'unica modifica applicativa
aggiunge otto righe a `_selected` in `compilation_global_sessions.py`, dopo
la rivalidazione e tutti i gate preesistenti. Le sessioni con dialogo accettano
solo SOURCE revisionate e non sospese. Restano invariati valori USER, sessioni
senza dialogo, V14, K3, analisi e narratore. Il veto rev 3 esistente è preservato.

Prove nuove, rete disabilitata e database/storage temporanei:

- prima: i dieci test originali dell'hotfix danno 8 FAIL e 2 PASS; gli otto
  fallimenti riproducono HTTP 200 al posto di 409;
- dopo: 62 PASS mirati, inclusi API, ripresa rev 3, K3 e autorizzazioni V14;
- replay storico: 210 stati disponibili, 157 esportazioni SOURCE registrate,
  nessuna nuova esclusione da parte del veto;
- preservazione: 245/245 scritture corrette con le conferme d'ambito simulate;
  211/245 con le sole ricevute registrate, identiche al riferimento. Le altre
  34 hanno ricevute rev 2 prive della prova rev 3: non sono regressioni del fix;
- i 25 controesempi di ramo mantengono l'esito precedente: sette bloccati da R1,
  diciotto ancora ammissibili con una guardia d'ambito simulata confermante.
  L'hotfix API non pretende di risolvere l'applicabilità semantica.

Suite completa: **3747 PASS, 3 SKIP in 359,23 s**; i tre casi richiedevano una
risposta storica locale, copiata identica e verificata separatamente: **3 PASS**.
Nessun test lasciato senza verifica. Ruff PASS. Commit: `4554ae1dfb3c9d6dc780e44aaeedeab57e13ba04`. Rollback verificato
con `git revert`: albero identico a `ff0d4f9`, riproduzione tornata a 8 FAIL/2 PASS
(stessi HTTP 200 indebiti). Commit di sola verifica locale: `67b68c0`.

Rollback previsto: `git revert <commit-di-integrazione>` in un worktree isolato.
Non richiede flag, migrazioni o modifiche ai dati. Ripristina anche la vulnerabilità
nei profili ordinari/P3: serve a dimostrare reversibilità, non è una promozione
consigliata. Il profilo rev 3 conserva il veto già presente nella base dello sprint.

Grezzi locali, esclusi da Git:
`backend/data/compilation-audit/docx-incrementale-20261023-01/` nel repository
originario. Piano e risultati prima/dopo separati; nessun risultato storico riscritto.


## Priorità 2: intestazione condizionale e tabella immediatamente seguente

Il rigioco della candidata di partenza riproduce il rischio: 18/25 errori rev 2
restano ammissibili se si simula una guardia d'ambito sempre confermante (12/25
con ricevute registrate). Non sono 18 nuove scritture reali: sono controfattuali
sugli output errati congelati.

Regola nuova, limitata alla struttura riconoscibile: tabella d'intestazione
non editabile, una riga/una cella, istruzione in grassetto «da compilare in caso
di» o «da compilare nel caso di», eventualmente preceduta da una numerazione.
La successiva tabella dati è governata dall'intestazione soltanto se non vi sono
paragrafi non vuoti intermedi. Non si estende ad altre tabelle o sezioni. Si
escludono intestazioni editabili, tabelle annidate e frasi citate come esempi.

La regola non classifica imprese, non interpreta RT o avvalimento e non crea
condizioni. Se una condizione valida è già ancorata all'intestazione, ne estende
lo scope ai campi governati e lascia agire i gate esistenti. Se manca, l'applicabilità
resta NON_ACCERTATA: bloccati sia SOURCE sia USER, anche con un valore vero o una
ricevuta d'ambito per il solo valore. Un consenso relativo ad altri rami non vale.
Il motivo è restituito negli issues; l'audit registra le regioni FORM riconosciute.

Attivazione separata: nuove sessioni `MAPI_GENERATION_REVISION=3` e
`MAPI_TABLE_SCOPE_REVISION=1`, flag persistito `table_scope_revision=1`.
Non si aggiornano le vecchie sessioni. Il profilo ordinario e la monolitica non
cambiano. Nessuna migrazione o dipendenza nuova, nessun nuovo prompt.

Prove prima/dopo:

- prima del codice: 2 FAIL / 2 PASS; JSON valido e fatto SOURCE corretto scrivono
  nel ramo condizionale omesso, anche con il nuovo flag richiesto;
- dopo: i quattro casi passano; due ulteriori prove API confermano il percorso
  positivo dopo una decisione USER con scope verificato;
- test di struttura, confini, condizioni respinte/estranee, rinvio, revoca,
  ricevuta per un altro ramo, valore USER, vecchie sessioni e idempotenza;
- replay dei 25 negativi e 245 positivi, con lo stesso codice applicativo:
  errori ammissibili **18 → 13** con guardia simulata; **12 → 7** con ricevute
  registrate. Corrette **245 → 245**, oppure **211 → 211** con sole ricevute
  storiche. Nessun nuovo falso rifiuto in questo insieme;
- le cinque nuove esclusioni sono le scritture della tabella 5.c di Catanzaro;
  nessun nome di bando, ID XML o tipo societario compare nella regola.

Rischi residui: i 13 casi di So.Re.Sa. non sono risolti deterministicamente.
Sei hanno una condizione con significato/scope errato, sette la omettono. I
blocchi RT e l'avvalimento non hanno la struttura strettamente riconosciuta
qui; estendere il veto per somiglianza avrebbe richiesto inferenze non dimostrate.
Una condizione presente ma semanticamente errata resta un limite del modello e
della guardia. Un'intestazione senza grassetto, fuori tabella, con istruzioni di
altra forma o riferimenti lontani resta fuori da questa correzione. Nessuna
promessa di generalizzazione universale.

Suite completa: **3775 PASS in 351,19 s**, Ruff PASS. Test nuovi: 25 casi,
compresi export positivo/negativo, strutture ambigue e flag. Il replay finale
conferma le stesse 245 scritture corrette. Commit:
`480e7e52b3af12ba0ee4ccc6d8c2912588839c39`. Rollback verificato in
`tesi-docx-rollback-p2`: revert `7121d99`, albero identico alla priorità 1 e
riproduzione tornata a 2 FAIL / 2 PASS. Nessuna modifica a sessioni o database.
Rollback: revert del commit dedicato; nessuna migrazione. Rimuovere solo la
variabile d'ambiente disabilita il flag nelle nuove sessioni, non in quelle che
lo hanno già persistito. Il revert elimina il comportamento anche per tali
sessioni conservandone i dati e la leggibilità.

## Priorità 3: una sola rilettura delle prove SOURCE già collegate

Inventario: 143 sospensioni attive nei cinque insiemi di stati finali disponibili,
di cui 90 SOURCE. Sono stati finali, non tutti gli episodi di sospensione: non si
confrontano direttamente con i 145 episodi contati nel rapporto dello sprint.
Il sottoinsieme dello sprint comprende 24 sospensioni attive:

| Caso | Sospensioni | Diagnosi e intervento |
|---|---:|---|
| Minervino-1 | 6 | Il narratore cita la riga dei soci ma ne trascura intestazione e ruolo già collegati. Una rilettura con il record completo. |
| Minervino-2 | 8 tecnici | Il FORM chiede il ruolo aziendale di responsabile della progettazione/direttore tecnico; il dubbio aggiunge una designazione per la domanda. Una rilettura con FORM e ruolo SOURCE. |
| Minervino-2 | 1 firmatario | Binding `review_required` e dubbio sulla carica corrente: escluso dalla rilettura automatica. |
| Catanzaro-1 | 4 | Dubbi di applicabilità, con decisioni USER pertinenti ma senza l'ancoraggio esatto richiesto dal criterio precedente. Nessun rilascio. |
| So.Re.Sa.-1 | 5 | Analogo problema di ambito della scelta individuale; nessun rilascio. |

La diagnosi sui tecnici corregge l'interpretazione prudenziale del rapporto
precedente: nel paragrafo 50 del FORM esaminato non si trova il requisito di una
nuova designazione per la gara. Questo non autorizza a ignorare una nomina
specifica quando un altro FORM la richiede.

Modifica opt-in `MAPI_HOLD_REREVIEW_REVISION=2`, soltanto con generazione rev 3.
Si riusa la finestra di revisione già esistente, senza nuova chiamata autonoma:
alla successiva sintesi il narratore riceve intestazione/colonne/riga del record,
ruolo e relative evidenze FORM/SOURCE. La proposta deve essere ammissibile ai
gate correnti, con fatto persona grounded e binding letterale senza errori,
ruoli richiesto/documentato coincidenti. Il dubbio deve citare esattamente la
riga univoca oppure nominare il ruolo già collegato. Quest'ultimo criterio è
un motivo per rileggere, non una prova che il dubbio sia infondato.

Nessun rilascio del backend: il campo rimane sospeso fino alla rilettura. Una
seconda sospensione è definitiva per questa revisione. Prove modificate o
condizioni revocate impediscono il riuso del controllo preparato. I flag delle
sessioni precedenti, il criterio rev 1 e tutti i gate di export sono conservati.

Riproduzione prima della modifica: 2 FAIL / 2 PASS (manca la rilettura nel nuovo
profilo, il vecchio profilo è preservato). Dopo: 123 test mirati PASS, compresi
release/nuova sospensione, revisione una sola volta, prove cambiate, condizioni
revocate, riferimenti invalidi e API. Il rigioco degli stati reali, con entrambe
le risposte simulate del narratore, verifica:

- il solo accodamento non cambia alcuna selezione;
- se il narratore rilascia i dubbi, Minervino-1 passa da 46 a 52 SOURCE e
  Minervino-2 da 51 a 59; se li conferma, restano rispettivamente 46 e 51;
- firmatario, quattro sospensioni Catanzaro e cinque So.Re.Sa. restano protetti;
- le selezioni USER restano identiche e non si riapre un terzo riesame.

Sono controfattuali offline, **non 14 recuperi dimostrati con DeepSeek**.
Nessun miglioramento reale della copertura o del costo è ancora misurato.
Restano possibili sospensioni superflue fuori dai criteri, e la rilettura può
confermare anche un dubbio superfluo. Non si sostituisce una decisione del
narratore con un'assunzione del backend.

Il rigioco finale preserva 245/245 scritture corrette con condizioni soddisfatte
e mantiene 13/25 negativi ancora ammissibili: nessuna regressione di ramo
introdotta dalla rilettura. Dati in `out/p3-recorded-replay.json`,
`out/p3-preservation.log`, `out/p3-hold-inventory-role.json` nell'audit locale.

Suite completa **3796 PASS in 351,38 s**, Ruff PASS. I 21 test della nuova
rilettura passano anche dopo averne reso la fixture indipendente dal fix sulle
tabelle. Il controllo storico finale conferma 210 stati / 157 esportazioni
senza nuove esclusioni. Nessuna migrazione. Disattivare il flag torna al profilo
precedente nelle nuove sessioni; il revert ripristina il comportamento anche
per quelle che hanno persistito la revisione 2. Non annulla scritture o
decisioni già registrate: queste restano sottoposte ai controlli ordinari.

Commit: `3ec0af00e5088d14455f5da9e12acba0ebbbabbc`. Revert verificato in
`tesi-docx-selective-p3`: `06cb5dc`, albero identico alla priorità 2,
riproduzione tornata a 2 FAIL / 2 PASS.

## Priorità 4: ripresa, verifica del profilo completo

Nessuna modifica applicativa. Gli stessi dieci scenari già presenti sono stati
eseguiti sia con il profilo sprint sia con `table_scope_revision=1` e
`hold_rereview_revision=2`: **46 PASS** complessivi (23 per profilo).

Sono verificati con API, provider simulati e storage temporaneo:

- interruzione dopo due segmenti validati: cache conservata, export ancora
  bloccato; ripresa con due cache hit e una sola chiamata al segmento mancante;
- niente duplicazioni di proposte o chiamate; SOURCE modificate e decisioni
  USER cambiate non riusano richieste obsolete;
- revoca/condizione modificata blocca le scritture dipendenti e mantiene quelle
  indipendenti, con tentativo di forzatura API respinto;
- JSON invalido, conflitti tra segmenti e retry esauriti conservano le parti
  indipendenti; tutti i segmenti falliti non producono un audit compilabile;
- doppio errore del narratore, degradazione e ripresa della sola sintesi senza
  rigenerare i segmenti o eliminare le sospensioni;
- export parziale con rivalidazione: 409 per campi sospesi, non analizzati o
  con condizione aperta; 200 per le sole scritture indipendenti autorizzate.

Limite concreto: quando si richiede una nuova analisi, una modifica SOURCE o
del contesto USER cambia il digest di **tutti** i segmenti. La cache è sicura ma
l'invalidazione è conservativa, non selettiva per dipendenza semantica. Questo
può aumentare costo e latenza. Le revoche sulle scritture, invece, sono mirate.
Le prove simulano un'interruzione con eccezione del processo: non certificano
crash del filesystem, mancanza di alimentazione o comportamento del provider
remoto. Non è stato costruito un nuovo orchestratore.

Il limite di due retry è per singola analisi, non un budget cumulativo di tutte
le possibili riprese della sessione. Una campagna deve contare anche queste.
Suite finale **3819 PASS in 354,50 s**, Ruff PASS. La differenza rispetto ai 3796
casi precedenti è l'esecuzione degli stessi 23 casi sul secondo profilo: il
numero da solo non dimostra un miglioramento del compilatore.

## Reversibilità verificata e file interessati

| Intervento | Commit applicativo | File principali |
|---|---|---|
| Veto API generale | `4554ae1dfb3c9d6dc780e44aaeedeab57e13ba04` | `compilation_global_sessions.py`, `test_compilation_explicit_draft_gate.py` |
| Applicabilità di tabelle condizionali | `480e7e52b3af12ba0ee4ccc6d8c2912588839c39` | nuovo `compilation_table_scope.py`; `compilation_global_sessions.py`, `compilation_scope_review.py`, `compilation_segments.py`; test dedicato |
| Rilettura SOURCE | `3ec0af00e5088d14455f5da9e12acba0ebbbabbc` | `compilation_hold_rereview.py`, `compilation_global_dialogue.py`, `compilation_global_sessions.py`; test dedicato |
| Verifica della ripresa | commit di chiusura associato a questo rapporto | soltanto `test_compilation_rev3_resumption.py` e documentazione |

Tutti i percorsi Python della tabella sono sotto `backend/app` o `backend/tests`.
Ogni commit aggiorna la continuità. Nessuna dipendenza, migrazione, reindicizzazione
o modifica al formato del database. I flag aggiunti restano opzionali e persistiti
nelle nuove sessioni; non si migrano quelle vecchie.

Oltre al ritorno esatto al genitore di ciascun fix, sono stati provati i revert
selettivi sul codice che contiene tutti e tre gli interventi:

| Fix rimosso | Effetto precedente riprodotto | Verifica degli altri interventi | Worktree locale di prova |
|---|---|---|---|
| API | 8 FAIL / 2 PASS, come prima del fix | 69 PASS su tabelle, narratore e ripresa | `tesi-docx-selective-p1` (`a20887f`) |
| Tabelle | 2 FAIL / 2 PASS, come prima del fix | 54 PASS su API, narratore e ripresa | `tesi-docx-selective-p2` (`e1862c2`) |
| Narratore | 2 FAIL / 2 PASS, come prima del fix | 58 PASS su API, tabelle e ripresa | `tesi-docx-selective-p3` (`06cb5dc`) |

I FAIL in questa tabella sono **attesi soltanto nei worktree di rollback**:
dimostrano che la correzione rimossa non agisce più. La candidata finale passa
tutti i test. I commit di prova non vengono pubblicati.

Procedura conservativa, già esercitata:

1. Da un worktree pulito della candidata, creare un nuovo branch/worktree di
   rollback con `git worktree add -b rollback/<nome> <percorso-nuovo> <SHA-candidata>`.
2. In quel worktree eseguire `git revert --no-commit <SHA-fix>`.
3. Conservare la versione corrente dei soli rapporti cumulativi in conflitto
   (`STATUS.md`, `relazioni.md`, questo rapporto), poi annotare il rollback.
   Non risolvere indiscriminatamente conflitti di codice con `ours`/`theirs`.
4. Nel revert di `480e7e5` dopo `3ec0af0`, esiste un conflitto locale verificato
   in `initial_state`: conservare le due righe che accettano
   `MAPI_HOLD_REREVIEW_REVISION` 1/2 e ne persistono il valore; rimuovere il blocco
   di tre righe che abilita `table_scope_revision`. Gli altri hunk si applicano.
5. Eseguire i test pertinenti degli interventi rimasti, `git diff --check`, quindi
   creare il commit di revert. Nessun reset, clean, cancellazione di sessioni
   o ripristino del database.

Il solo `git revert` non è quindi sempre privo di conflitti: i documenti sono
cumulativi e i due flag sono adiacenti. La risoluzione sopra è stata verificata,
non ipotizzata. Per tornare esattamente alla configurazione precedente nelle
nuove sessioni, rimuovere `MAPI_TABLE_SCOPE_REVISION` quando si rimuove il fix
tabelle; per il narratore riportare `MAPI_HOLD_REREVIEW_REVISION=1` (o assente
se già assente). Nessun flag nuovo è necessario per l'hotfix API. Togliere solo
un flag d'ambiente **non** modifica retroattivamente il profilo persistito;
il revert ripristina il codice anche per queste sessioni, conservandone i dati.
Rimuovere il veto API reintroduce il difetto noto nei profili ordinari/P3.

## Esito, limiti e passo successivo

Sono dimostrati offline: veto esplicito dell'export, cinque esclusioni aggiuntive
di rami errati, preservazione delle 245 scritture corrette alle stesse condizioni,
riesame SOURCE limitato senza rilascio backend e ripresa nei casi simulati.
Non sono dimostrati: più DOCX reali, maggiore copertura generale, minore latenza
o costo, efficacia reale del narratore. Restano 13/25 controesempi non bloccati
deterministicamente e le sospensioni di applicabilità qui escluse.

La monolitica acquisisce soltanto il veto API quando si usa questo branch;
le due novità ulteriori richiedono la candidata rev 3 e i rispettivi flag.
L'app ordinaria in esecuzione non è stata modificata né riavviata. V12, benchmark,
gold e risultati storici restano preservati. Il working tree ordinario già
modificato non è entrato in nessun commit.

Proposta separata: [sei tentativi esplorativi, tetto 3 milioni di token](proposta-e2e-incrementale-2026-10-24.md).
Richiede autorizzazione prima di qualsiasi inferenza. Non è una nuova campagna
da 35 tentativi né una certificazione delle soglie congelate.

Grezzi, preregistrazioni, replay e log sono nell'audit locale
`backend/data/compilation-audit/docx-incrementale-20261023-01/`, escluso da Git.
Backup separato previsto in `backend/data/compilation-audit/docx-incrementale-backup-20261024/`:
manifest per file, archivio audit/rapporti e bundle incrementale dei soli commit
nuovi, con base richiesta `ff0d4f9`. Esito della verifica in `VERIFICA.json`.
Non include database, credenziali o documenti originali.

Pubblicazione autorizzata del solo branch sperimentale dopo controllo dei nuovi
file e della loro cronologia; nessun merge, modifica di tag o force push. Le
evidenze grezze locali non vengono pubblicate. Nessuna revisione autoriale è
presentata come indipendente.
