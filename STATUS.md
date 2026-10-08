# Stato di Mapi RAG

Aggiornato il **8 ottobre 2026**. Base precedente agli interventi: branch `main`, commit
`dcb9557` (`fix: stabilize table autofill and DOCX finalization`).
Ricontrollare Git all'inizio della prossima sessione.

## Commit locali richiesti dall'utente — 8 ottobre 2026

Su richiesta esplicita sono stati consolidati i fix locali precedenti e lo
stability pass. Backend e regressioni nel commit `52a86ce`
(`fix: isolate DOCX model failures and preserve compilation state`);
il commit successivo contiene messaggi UI di recupero e questa continuità.
Nessun push. DOCX compilati, report reali nuovi, DB, snapshot e tracce restano
locali e ignorati da Git. README/start invariati. Il codice coincide con quello
verificato dai 1.296 test backend, 84 frontend e dalla prova reale mirata sotto;
nessuna suite o prova reale ripetuta per il solo commit. Restano aperti i
quattro blocchi FORM e i problemi di pertinenza dei rami descritti sotto.

## Ultimo intervento: stability pass CompilationSession — 8 ottobre 2026

Preservati i fix locali matcher/classificatore e le modifiche di continuità
preesistenti. Nessun commit/push; README/start invariati. Report completo locale,
audit dei confini e tracce (ignorati da Git):
[stability pass](backend/data/compilation-audit/stability-pass-20261008/report.md).

- Revisioni FORM/SOURCE ora isolano ID estranei, duplicati e item invalidi,
  conservando approvazioni indipendenti; un verdetto per una proposta storica
  già filtrata non provoca più un lookup interno errato. Fatti con SOURCE
  estranea scartati. Coverage backend incoerente resta ValueError esplicito.
- Errori tipizzati soltanto al confine reale del modello: schema recuperabile
  entro i due tentativi della propria fase; provider/timeout sospendono senza
  consumare altri campi. Esaurimento non genera domande sui PENDING né READY.
  Messaggio persistito comprensibile; nessun catch generale di bug interni.
- Risposte USER di gruppo parzialmente invalide conservano gli slot validi
  univoci. Condizioni USER già risposte non vengono dimenticate dalla rianalisi;
  propagazione delle dipendenze non cancella valori SOURCE/USER persistiti.
  Pausa/ripresa letterali disponibili anche se il planner non risponde.
  Modifiche UI limitate a messaggi/avviso: dettagli tecnici nei log, nessun
  nuovo workflow o modifica dell'orchestrazione dei batch.
- **43 nuove regressioni**, **315 test mirati finali passati** (85,50 s).
  **1.296 backend complessivi passati**, copertura disgiunta 315+348+336+297;
  un primo processo unico interrotto non è conteggiato come suite passata.
  **84 frontend passati**, Ruff, lint/build e diff check passati. Test includono
  errori consecutivi, retry esauriti, due resume, decisione negativa già
  registrata, conservazione prove, scope e DOCX parziale materializzato con
  ready_for_submission=false. Nessuna migrazione/reindicizzazione richiesta.
- I quattro blocchi sono `t38.r1.c1`, `t38.r2.c0`, `t38.r2.c1`, `t38.r3.c0`:
  ragioni sociali/CF-P.IVA delle consorziate, non anagrafica dell'operatore.
  La condizione consorzio stabile esiste in paragraph:573, ma il modello la
  legava a paragraph:595. Rebind solo letterale/univoco, con revisione finale
  rigorosa. **Restano bloccati nella prova reale**: modello/reviewer assegnano
  ancora subject_type alle consorziate, confondendole col consorzio compilatore.
  Nessuna deroga al controllo, nessun rimborso dei retry (interpretazione 2,
  SOURCE 0). Distinguere i due soggetti richiede un intervento separato.
- Prova reale mirata, DeepSeek flash/Qdrant/BGE reali su copie: quattro campi
  espliciti + un solo batch automatico successivo di 12; 6 chiamate, 40,195 s,
  nessuna eccezione, 11 query/7 chunk/9 candidate ricercati. **22 SOURCE
  preservati, zero nuovi valori**, 263 altri candidate invariati. Copia v89
  CREATED, auto_continue=true: 22 RESOLVED, 22 MISSING, 34 AMBIGUOUS, 1 NA,
  200 PENDING. Nessun benchmark completo o DOCX reale generato, non READY.
- Nella copia della precedente v102, due resume conservano tutte le **7
  decisioni USER «non professionista singolo»** e tutti gli altri campi.
  La sessione attuale v83 con 22 SOURCE non contiene tali decisioni: non
  confondere i due test. Originali confermati invariati **v83 e v102**.

**Problemi distinti da riprendere solo con un nuovo incarico:** i 22 valori
preservati includono assegnazioni preesistenti non sufficientemente giustificate
nei rami Studio Associato (t14/t15) e Società di Professionisti/soci (t19/t22/t23).
Il report identifica 13 valori interessati e le evidenze; non riapprovati né
cancellati durante questo pass. Serve valutare soggetto della condizione,
eredità del contesto di sezione e identità delle entità elencate. La robustezza
è verificata; la correttezza semantica di quei rami e dei quattro campi non è
dichiarata risolta. I budget esauriti non si riaprono con il solo resume.

## Ultimo intervento: classificazione fuori dal gruppo selezionato — 8 ottobre 2026

Seguito del fix matcher sotto: nella **nuova sessione** Catanzaro
`7945c99079a54d729f67855a4d03a956`, v83 FAILED, l'utente ha ricevuto
`Classificazione con candidate sconosciuto`. Conservati **22 valori SOURCE**.
Il gruppo interrotto riguarda sei celle della tabella delle consorziate,
ciascuna con 2 tentativi di interpretazione e 0 SOURCE. La risposta grezza
storica non è conservata: non è identificabile l'ID estraneo preciso.

- Esteso il controllo degli ID al classificatore: `bind_meanings` filtra gli
  output prima della revisione FORM e dell'applicazione. ID estranei, inclusi
  errori item-local su ID estranei, non interrompono le interpretazioni valide.
  Duplicati tutti respinti, senza scegliere una versione; target omessi restano
  PENDING. Scarti persistiti in `last_resolution.interpretation_rejections`.
  Prompt con lista di ID ammessi. Quote/anchor, revisione indipendente FORM e
  controlli SOURCE restano obbligatori; nessun nuovo counter, retry o migrazione.
  Modificato soltanto il resolver e i test, preservando il fix matcher locale.
- **18 nuove regressioni FTS5/Qdrant**, con riproduzione del medesimo 502 prima
  del fix: sibling valido risolto, precedente SOURCE intatto, filtro prima
  della revisione FORM, ID estranei validi/invalidi, duplicati, FORM non grounded
  respinto, contatori separati, stop dopo due tentativi e failure provider.
  Aggiornata la vecchia aspettativa di test sui duplicati di interpretazione:
  ora sono errori locali, non globali. **272 test mirati passati in 57,97 s**,
  incluse tutte le 254 regressioni del fix precedente; Ruff backend completo e
  diff check superati. Suite completa/frontend non rieseguiti.
- **Prova reale dei soli sei candidate su copia isolata della v83**, con
  rianalisi esplicita perché i tentativi automatici erano già esauriti.
  DeepSeek `deepseek-flash`, 1 chiamata, 6,470 s, nessun errore globale.
  **2 AMBIGUOUS** (barrature/scelte sulle consorziate), **4 PENDING**:
  `Condizione non ancorata alla sezione FORM`. Zero SOURCE interrogate o nuovi
  valori; Qdrant configurato, ma non chiamato perché i dati non superano FORM.
  Nessuna prova di compilazione completa: il vincolo FORM delle quattro celle
  è un limite distinto, non corretto in questo intervento. **273 altri candidate
  identici**, inclusi i 22 SOURCE; codice invariato durante la prova.

**Punto di ripresa:** il controllo di scope ora copre interpretazione e matcher.
La sessione applicativa resta v83 FAILED, campi e counter invariati; **Prosegui
compilazione** rinnova il ciclo sui candidate ancora analizzabili. I sei target
con budget già esaurito non vengono riprovati automaticamente: per riesaminarli
serve una rianalisi esplicita limitata, senza azzerare globalmente i counter.
README/start e documenti preservati. **Nessun commit/push.** Report locale,
snapshot e tracce sotto `backend/data/compilation-audit/classification-scope-20261008/`
(ignorato da Git).

## Ultimo intervento: matcher fuori dal gruppo ricercato — 8 ottobre 2026

Corretto localmente il blocco `Matcher con candidate sconosciuto, duplicato o
non ricercato` della sessione Catanzaro
`7167b46dbb134e0db41ff9f092d55e6b`, v102 FAILED: **17 valori SOURCE conservati**,
113 posizioni analizzate. Il failure era nel passo SOURCE dei dieci candidate
relativi a socio unico/amministratore di fatto, già interpretati. La risposta
grezza del failure storico non è disponibile: non è identificabile l'ID preciso
che lo aveva causato.

- `compilation_session_resolution.py` vincola il matcher agli ID effettivamente
  ricercati, prima della revisione SOURCE e dell'applicazione. Output fuori ambito
  e duplicati vengono scartati e registrati in `last_resolution.matcher_rejections`;
  dei duplicati non viene scelta arbitrariamente una versione. Gli item validi
  conservano le proprie verifiche. Se una risposta contaminata omette un target,
  il suo retry SOURCE rimane limitato dai counter esistenti. Errori globali di
  schema/provider restano espliciti. Nessun nuovo counter o limite, migrazione,
  modifica UI, retrieval, semantica FORM, grouped o renderer.
- **19 nuove regressioni**, incluse FTS5/Qdrant, valore precedente invariato,
  risoluzione del sibling valido, scope prima della revisione SOURCE, duplicati,
  campo non ricercato invariato, retry esaurito senza loop e failure globali.
  **254 test mirati passati in 95,01 s**, incluse semantica, prima tabella,
  retry separati, sessioni/guardie, grouped, active question e finalizzazione.
  Ruff backend completo e diff check superati; suite completa/frontend non
  rieseguiti. Questi sono test software con provider simulati.
- **Prova reale di un solo passo su copia isolata della v102**: DeepSeek
  `deepseek-flash`, Qdrant locale e BGE-M3 reali, stesse fonti/Company KB.
  Superato il gruppo senza failure: **10 SOURCE cercati, 10 MISSING**, zero nuove
  risoluzioni, perché mancano prove dei ruoli/dati personali richiesti. Non
  trasferiti dati aziendali o di un amministratore unico ad altri ruoli/persona.
  2 chiamate modello, 6 query, 7 chunk, 17,637 s. Nessuna interpretazione ripetuta;
  counter interpretazione invariati a 1 e SOURCE a 2 per i dieci target.
  **269 altri candidate invariati**, inclusi i 17 SOURCE; codice invariato durante
  la prova. La copia passa a v105 CREATED con `auto_continue=true`, 123 posizioni
  analizzate e 156 PENDING. Non eseguiti altri passi né generazioni DOCX.

**Punto di ripresa:** la sessione originale è ancora v102 FAILED, campi invariati;
usare **Prosegui compilazione** nella conversazione esistente con il backend
aggiornato. Non serve ricreare la sessione o azzerare i tentativi. La prova
verifica il superamento di quel gruppo, non il completamento dei 279 candidate.
README/start e DOCX locali preservati. **Nessun commit/push.** Report e tracce
restano fuori Git in
`backend/data/compilation-audit/matcher-scope-20261008/report.md`.

## Commit locale richiesto — 8 ottobre 2026

Richiesto dall'utente il commit dello stato funzionante, con push manuale a suo
carico. Inclusi fix FORM delle tabelle, fix SQLite della finalizzazione, relativi
test e modifiche intenzionali già presenti a README/start. Gli originali demo
restano fixture versionate; i DOCX compilati nella radice restano ignorati.
Aggiunte a `.gitignore` le esclusioni di `compilazioni-report.md` e dei due
report locali nuovi in `docs/` (diagnosi Minervino e prima tabella Catanzaro):
restano disponibili sul PC, fuori dal commit. I collegamenti sotto a questi
artefatti si riferiscono alla copia locale.

**Verifiche rieseguite prima del commit:** 24 test mirati passati in 10,89 s
(`test_compilation_table_fields.py` e `test_compilation_finalization.py`), Ruff
backend completo, sintassi Bash, `start.sh --help` e diff check superati.
Nessun nuovo benchmark AI, installazione o avvio dei servizi in questi controlli.
Le suite più ampie riportate sotto sono le esecuzioni precedenti.

## Ultima operazione: DOCX della prima tabella Catanzaro — 8 ottobre 2026

Su richiesta dell'utente, generato nella radice
[catanzaro-domanda-partecipazione-prima-tabella-compilata.docx](catanzaro-domanda-partecipazione-prima-tabella-compilata.docx)
dall'originale della prova limitata descritta sotto: **6 valori SOURCE scritti**,
sede operativa lasciata vuota perché NOT_APPLICABLE/SOURCE. È una **bozza parziale**,
`ready_for_submission=false`, con i restanti 272 candidate non analizzati.

Esportazione con il finalizzatore esistente e `allow_unresolved=true` su una
nuova copia del DB del benchmark; stato e campi della sessione del benchmark
preservati. **Zero nuove chiamate AI**, nessuna analisi dell'intero documento.
Verificati i sei valori nelle celle fisiche, le altre celle e i paragrafi
invariati (salvo avviso di bozza), le parti DOCX esterne al corpo byte per byte
e gli hash dell'originale/output. Codice, README/start e precedente DOCX Catanzaro
preservati; nessun commit/push. Suite software non ripetute per il solo export.
Report tecnico e verifiche in
`backend/data/compilation-audit/catanzaro-first-table-20261008/export-01/`;
nota aggiunta al report reale della prima tabella.

## Ultimo intervento: anagrafica della prima tabella Catanzaro — 8 ottobre 2026

Correzione circoscritta ai normali campi tabellari, sopra le modifiche locali
precedenti, preservate. **Nessun commit/push.** Il codice non contiene riferimenti
a Catanzaro, candidate ID o Mapi per decidere la validazione.

- `compilation_semantics.py` espone sezioni FORM per tabella/riga, ricavate dal
  catalogo dell'originale. Nelle celle tabellari non promuove più automaticamente
  il soggetto aziendale generico a condizione di tipologia. La revisione FORM
  indipendente e `condition_complete` restano obbligatori; le condizioni locali
  letterali possono ancorarsi alla propria riga. Il percorso dei paragrafi non
  cambia. Prompt classificatore/revisore precisati per citazioni locali,
  soggetto corretto e rispetto delle condizioni effettive.
- **16 nuove verifiche** su tabella generica; **227 test mirati passati in
  46,21 s**, incluse semantica, sessioni, retry separati, grouped, active question
  e guardie. Ruff backend completo e diff check passati. Suite backend completa
  e frontend non rieseguite per questa modifica circoscritta.
- **Prova reale limitata ai sette campi `t0.r5.c1`–`t0.r11.c1`**, nuova sessione
  isolata `57cdd64bfb534f64817016f3e3ed81a2`: DeepSeek `deepseek-flash`, Qdrant e
  BGE-M3/Ollama reali, stessa Company KB (contenuti confrontati con l'app).
  **7 FORM accettati, 7 SOURCE cercati, 6 RESOLVED/SOURCE**, al primo passaggio.
  Operatore economico, forma giuridica, sede legale, CF azienda, P.IVA, telefono.
  **Sede operativa NOT_APPLICABLE/SOURCE**: la KB attesta che coincide con la
  sede legale; preservata la condizione «se diversa dalla sede legale».
  Zero valori USER e zero errori di validazione; 5 chiamate modello, 6 query,
  28,893 s. Codice invariato durante la prova, **272 altri candidate invariati**.
- Nessuna modifica a retrieval, provenance SOURCE/USER, placeholder gate, UI,
  grouped, retry, parser/renderer o orchestrazione. Nessuna migrazione né
  reindicizzazione dell'app. Nessun DOCX rigenerato o READY forzato. README/start
  e le tre bozze precedenti nella radice preservati.

**Punto di ripresa:** il blocco FORM dei sette campi è verificato risolto nella
prova limitata; non è una verifica degli altri 272 candidate. I tentativi delle
sessioni storiche non sono azzerati. Per riprovare una sessione esistente usare
la rianalisi esplicita dei soli campi selezionati, che rilegge il contesto del
proprio originale; non avviare automaticamente una nuova analisi completa.
Report con valori, query, anchor, evidence e limiti:
[prima tabella Catanzaro](docs/test-reale-catanzaro-prima-tabella-2026-10-08.md).
Archivio ignorato:
`backend/data/compilation-audit/catanzaro-first-table-20261008/run-01/`.

## Ultima operazione: esportazione dei tre moduli — 8 ottobre 2026

Su richiesta esplicita dell'utente, salvati nella **radice del progetto**:

- `catanzaro-domanda-partecipazione-compilata.docx`: **1 valore SOURCE**.
- `trapani-manifestazione-interesse-compilata.docx`: **9 valori SOURCE**.
- `minervino-domanda-iscrizione-compilata.docx`: **6 valori SOURCE**.
- [compilazioni-report.md](compilazioni-report.md): riepilogo, output chat,
  chiarimenti, valori/prove e tabella completa dei **648 candidate**.

Sono **bozze parziali**, generate con `allow_unresolved=true` su copie isolate:
report nativi `needs_review`, `ready_for_submission=false`; nessun READY forzato,
valore USER inventato o firmatario scelto. Sessioni/documenti originali preservati.
Nessuna modifica al codice applicativo, README/start preservati, nessun commit/push.

Trapani usa la sessione recente `88149be5f16041bbae2985010fea7fdb` v53
(115 candidate: 9 SOURCE, 52 MISSING, 23 AMBIGUOUS, 31 PENDING).
Minervino nel frattempo ha terminato il ciclo avviato dall'applicazione: esportata
la v124 WAITING_FOR_USER (254 candidate: 6 SOURCE, 115 MISSING, 49 AMBIGUOUS,
84 PENDING), distinta dalla v90 della diagnosi storica sotto.

Per Catanzaro, assente una sessione nell'app, creata una **nuova sessione isolata**
`5c863d37ee3d4a00b68ddd00bbb22a20`, usando originale/fonti dell'archivio retry
Catanzaro e KB globale con chunk identici a quelli attuali. DeepSeek
`deepseek-flash`, Qdrant e BGE-M3 reali; 88 chiamate strutturate / 324,49 s.
Analisi **FAILED v74** al passo 28, `GenerationError` nella chiamata
`CandidateMatches`; dettaglio testuale non conservato, causa provider/output
non determinabile dalla traccia. 279 candidate: 1 SOURCE, 31 MISSING,
37 AMBIGUOUS, 210 PENDING. Esportata la sede legale già accettata prima del failure,
senza riusare valori dei benchmark precedenti né aggiungere retry.

**Verifiche effettive dell'export:** 16 valori controllati nelle celle/paragrafi
di destinazione; SHA-256 corretti e tutte le parti DOCX diverse dal corpo
preservate byte per byte. Nessuna chiamata AI per gli export Trapani/Minervino.
Suite software non ripetute per la sola generazione di artefatti; i 436 mirati
sotto rimangono la verifica del precedente fix SQLite. Diff check passato.
Archivio ignorato: `backend/data/compilation-audit/exports-three-20261008T110401Z/`.

**Punto di ripresa:** le tre esportazioni non attestano moduli completi. Restano
le diagnosi semantiche/di applicabilità dei PENDING e il failure Catanzaro;
conservare i counter e i gate FORM/SOURCE. Non trattare le bozze come SOURCE.

## Fix locale: blocco SQLite in finalizzazione Minervino — 8 ottobre 2026

Corretto localmente il 500 `database is locked` durante l'esportazione della
sessione `c34440fe726f4790acd586424e212078`, progetto
`minervino-di-lecce-elenco-sia`. **Nessun nuovo commit/push.** All'inizio `main`
era allineata a `origin/main`, con sole modifiche locali a README/start:
preservate byte per byte. Il commit `f1e06fe` contiene già il precedente lavoro
semantico e i report; lo storico sotto descrive le prove prima di quel commit.

- `_persist` salva il report in una transazione SQLite; il callback della
  sessione rileggeva le SOURCE aprendo una seconda connessione. Il report di
  Minervino (circa 2,37 MB) riproduce il blocco con le impostazioni SQLite
  ordinarie: il cache spill della scrittura impedisce la lettura separata.
- `reload_evidence` accetta una connessione opzionale, senza chiuderla o fare
  commit quando è fornita dal chiamante. `save_generation` la passa tramite
  `check_current_sources`: rilettura SOURCE e salvataggio restano nella stessa
  transazione. Conservati controllo versione, isolamento/provenance e rifiuto
  delle SOURCE cambiate. Nessuna modifica a timeout, journal mode, schema,
  migrazioni, UI, parser/renderer, retry o orchestrazione.
- **8 regressioni nuove passate**, combinazioni FTS5/Qdrant e Company/project
  SOURCE: salvataggio sotto lock esclusivo reale, valori SOURCE/USER nel DOCX,
  rifiuto 409 di SOURCE cambiata e rollback di sessione/report/file.
  **436 test mirati passati in 106,18 s**, incluse le otto regressioni, sessioni,
  guardie, SOURCE/retrieval FORM, DOCX, semantica, retry separati, grouped,
  active question e controlli. Ruff e diff check passati. La suite backend completa e il
  frontend non sono stati rieseguiti per questo fix circoscritto.
- Replay tecnico su due copie dello stesso DB/sessione: prima riprodotto
  `OperationalError: database is locked` in 8,06 s; dopo GENERATED v91 in 2,59 s,
  sei valori materializzati negli slot originali e field/provenance invariati.
  Solo le copie usano `allow_unresolved=true`. **Non è un nuovo benchmark AI
  né un modulo completo**: zero chiamate modello, nessuna sessione reale alterata.

**Stato originale conservato:** v90 FAILED, nessuna generazione; 254 candidate,
6 RESOLVED, 66 MISSING, 35 AMBIGUOUS, 147 PENDING. Il ciclo aveva già raggiunto
36 passi (budget 36/600 s): distinto dal successivo errore in esportazione.
Fra i PENDING: 52 senza tentativi, 12 con un tentativo, 83 con due; 61 riportano
`Condizione non ancorata alla sezione FORM`. Il fix SQLite non risolve questi
errori semantici e non ricarica i retry. La ripresa non garantisce il completamento.

**Prossimo passo minimo:** dopo il reload del backend la finalizzazione usa il
fix; la sessione esistente conserva tutti i valori. Per completare Minervino
occorre una diagnosi separata dei PENDING, partendo dalle condizioni FORM
respinte, e dei chiarimenti di applicabilità. Non azzerare sessioni/counter né
allentare i gate. Nessuna migrazione/reindicizzazione necessaria per il fix.
Dettagli e limiti in
[diagnosi Minervino, 8 ottobre](docs/diagnosi-minervino-finalizzazione-2026-10-08.md).
Archivio tecnico ignorato: `backend/data/compilation-audit/minervino-finalize-lock-20261008/`.

## Storico: semantica FORM e contesto SOURCE — 8 ottobre 2026

Implementazione e test software conclusi sopra le modifiche locali dei retry,
**senza commit/push**. Dopo la ricarica DeepSeek, **criterio principale verificato
sul codice finale**: otto dati societari utili RESOLVED/SOURCE, tipologia SOURCE,
Fax MISSING, nessun firmatario inferito o valore della gara usato come servizio
pregresso. Il modulo completo NON è READY: 30 PENDING e chiarimenti rinviati
restano aperti. Non equiparare questo risultato al completamento dell'intero modulo.

- Binding persistente fra slot fisico, proprietà semantica, soggetto, sezione e
  ruolo temporale. Il backend ancora lo slot all'originale; una revisione FORM
  indipendente ammette label normalizzate anche non letterali, conservando quote,
  soggetti e condizioni ancorati al modulo. Organizzazione rappresentata distinta
  da persona, professionista e firmatario.
- Applicabilità condivisa per sezione/entità/condizione verificate. La tipologia
  implicita di un'organizzazione rappresentata viene conservata come condizione
  FORM; `condition_complete` controlla anche qualificatori esteri/giuridici.
  SOURCE/USER determinano il fatto, non il FORM. Esclusioni fra alternative
  soltanto con istruzione FORM esplicita di scelta unica.
- `PAST_SERVICE` distinto da `CURRENT_PROCEDURE`: estrazione indipendente di
  fatti di servizi già eseguiti, senza candidate/valori attesi nel prompt, poi
  revisione della proposta e rilettura della prova in finalizzazione. Dati della
  gara corrente e attività generiche non attestano incarichi pregressi.
- Respinti placeholder, linee vuote, N/A, etichette senza valore e indicazioni
  esplicite di campo non compilato. Le sigle informative restano ammesse.
  `source_span` non estrae BA dal prefisso di Bari e conserva la grafia SOURCE.
- Errori locali di revisione isolati; failure globali/provider espliciti.
  Retry separati persistenti, massimo due tentativi per fase/candidate;
  batch 12/6 e ciclo 36 passi/600 s preservati. Fino a sei chiamate modello per
  resolve completo, nessuna chiamata per singolo field o riparazione illimitata.
  UI/parser/renderer/orchestrazione chat invariati da questo intervento;
  grouped collegato al contesto di sezione senza riprogettazione.

**Verifiche finali effettive:** 46 regressioni nuove, **269 mirati passati** e
**1.192 backend completi passati** in quattro gruppi sequenziali
(385/343/398/66); Ruff e diff check passati. Provider simulati, DB/storage
temporanei; frontend invariato e non ritestato. La prima suite in un processo
era stata uccisa dall'OOM; non è conteggiata come passata. Nessun test disabilitato.

**Benchmark finale dopo la ricarica:** DeepSeek `deepseek-flash`, Qdrant locale
reale + BGE-M3, nuova sessione `a0122f66352848de94e14c94146c6419`, v59,
WAITING_FOR_USER / deferred_summary. Stesso `manifestazione-interesse.docx`
(hash `d125c7bf…`), Company KB e fonti Trapani in copie isolate.
**115/115 tentati; 9 RESOLVED/SOURCE; 45 MISSING; 31 AMBIGUOUS; 30 PENDING;
0 USER_PROVIDED/NOT_APPLICABLE; 76 DEFERRED** (sovrapposto agli stati).
**15 checkpoint/15 turni USER**, soltanto SKIP numerati, 52 slot complessivi,
media **3,4667**. Tutti e nove i SOURCE prima del primo checkpoint.
17 resolve, 51 chiamate resolver, 335,8 s; zero failure/resume, codice congelato.
Nessun valore manuale, nessun READY/DOCX forzato.

Gli otto valori di `p75.s0–s8` (Fax escluso) sono esattamente quelli richiesti:
Mapi Ingegneria S.r.l.; Via Giovanni Amendola 172/C; Bari; 70126; BA;
IT01234567890; +39 080 000 2040; mapi.ingegneria@pec.demo.
Tutti con SOURCE e applicability=true/SOURCE, tipologia attestata dalla visura.
Fax MISSING. Il nono SOURCE è PEC comunicazioni `p107.s0`.
Comune/CAP/Provincia inizialmente MISSING per SOURCE fuori bucket → RESOLVED al
secondo tentativo SOURCE; interpretation fermo a uno. Nessun counter oltre due.
30 slot della tabella t5 MISSING/PAST_SERVICE; otto slot firmatario p12 MISSING.
Zero proposte current→past o placeholder nel benchmark, zero valori errati accettati.
Replay negativo separato sul codice finale: una chiamata DeepSeek reale restituisce
facts=[], **due offerte di importi correnti respinte**; in RAM senza modello
**due CIG placeholder respinti**. Non sommare il replay alle metriche della sessione.

**Limiti residui:** 30 PENDING (24 condizioni non ancorate alla sezione FORM,
5 review indipendenti assenti, un estratto strutturale non presente). Non vengono
chiesti come valori USER. 76 field chiaribili sono rinviati in 52 slot; SKIP non
fornisce dati. Alcune condizioni del ramo dei prestatori esteri sono abbreviate
al riferimento normativo mentre il qualificatore estero resta nel contesto FORM:
nessuna SOURCE=true applicata a quel ramo, ma la condizione/questione richiede
riesame prima di dichiarare completa la gestione dei qualificatori.

Il codice è identico a quello dei **269 mirati/1.192 backend già passati** prima
della ricarica; la suite non è stata ripetuta per il solo benchmark. Ruff e diff
check rieseguiti e passati. Nessuna modifica al codice durante/dopo la prova.
UI/parser/renderer/orchestrazione e counter non cambiati in questa ripresa.

**Prova precedente, conservata:** sessione `6846e0553a74406f9c5937a9f46e9904`,
v39 FAILED/402, 100 tentati/0 SOURCE/0 checkpoint; non riaperta o alterata.
La precedente intermedia `f9346167a6f54712a3fb14b25c5a6bec` aveva verificato otto
valori ma non era il codice finale; ora il risultato è confermato sulla versione
finale. Tutti gli archivi precedenti conservati.

**Prossimo passo minimo:** diagnosi dei 30 PENDING e dei qualificatori abbreviati
nelle condizioni, separata dal benchmark concluso. Non aumentare retry né chiedere
valori di candidate non interpretati. Per finire il modulo servono chiarimenti
reali su alternative applicabili, firmatario, Fax e servizi pregressi documentati.
Nessuna nuova implementazione avviata dopo il benchmark.
Nessuna migrazione/reindicizzazione dei dati utente; sessioni legacy non riscritte.
Sessione originale dell'app `85daf575481244cd934911c42b3567f4` invariata alla v77;
README/start preservati byte per byte, testo locale precedente conservato sotto.
Report con tracce, query, evidence, confronto PRIMA/DOPO e limiti:
[manifestazione-interesse, 8 ottobre](docs/test-reale-manifestazione-interesse-2026-10-08.md).
Audit finale ignorato: `backend/data/compilation-audit/semantic-slots-20261008-ready/`;
precedente 402 in `semantic-slots-20261008-canonical/`. Snapshot dei documenti prima
della ricarica in `ready/checks/*.before`; STATUS prima dell'intervento semantico
in `canonical/checks/STATUS-before.md`.

## Storico: retry separati — 7 ottobre 2026

Completato il fix mirato sopra `a5e2e2e`, **senza commit/push**. Conservate
integralmente le modifiche locali precedenti ad avvio, README, ambiente e
progetti demo; README/start invariati rispetto all'inizio dell'intervento.

- `analysis_attempts`: interpretazione senza requirement; `source_attempts`:
  retrieval/proposta/validazione di requirement interpretati. Dizionari
  persistenti nel workflow JSON, massimo due tentativi per fase/candidate.
- Batch automatici omogenei; retry SOURCE conserva requisito/applicabilità,
  senza riclassificazione. Dopo interpretazione valida, revisione `source_start`
  prima del retrieval: riserva solo i tentativi SOURCE pertinenti e conserva
  esiti FORM. Item validi del batch conservati, errori locali isolati; failure
  globali/provider e controllo delle revisioni preservati.
- `reopen_phase_attempts`: una conferma di applicabilità riapre soltanto la
  fase necessaria, anche per review senza requisito dopo due interpretazioni.
  SKIP/UNKNOWN/PAUSE/RESUME preservati; budget 12/6 e 36 passi/600 s invariati.
  Sessioni legacy conservano budget speso, senza migrazione/reset automatico.
  UI/parser/renderer/gate SOURCE e grouped non riprogettati.

**Verifiche finali effettive:** 27 nuove regressioni (FTS5/Qdrant dove previsto),
211 mirati finali, **1.146 backend completi passati in 302,18 s**, Ruff e diff
check passati. Provider simulati, DB/storage temporanei; frontend non ritestato.
Le esecuzioni precedenti (280/103 mirati, suite 1.142 passata, suite 1.144 con
2 timeout ambientali poi passati al riesame) sono storiche, non l'esito finale.
Un test finale ha riprodotto il blocco del reset per review senza requisito:
corretto dopo il primo benchmark, test/suite e benchmark nuovo rieseguiti.
Nessun codice modificato durante nessuna delle due prove reali.

**Benchmark reale finale:** DeepSeek `deepseek-flash`, Qdrant locale + BGE-M3;
nuova sessione `382b44b883524bc1a908d4b8515a36e2` in archivio isolato. Dati
dell'app preservati. Company/General KB coerente con la locale e SOURCE
bando/disciplinare Catanzaro. DOCX corrente 279 candidate, hash `5b3ad083…`,
diverso dallo storico `aeb1bda3…` non recuperabile. Indice iniziale standard:
timeout e Ollama OOM; preparato a un frammento per richiesta, stessi hash,
metadati e filtri; riconciliazione ordinaria 214 chunk/1024 dimensioni,
zero aggiornamenti pendenti. Archivio/indice riusati nella nuova prova.

Finale: **279 processati; 17 RESOLVED/SOURCE formali; 0 USER_PROVIDED;
6 NOT_APPLICABLE (tutti non-field/FORM); 123 MISSING; 10 AMBIGUOUS;
123 PENDING; 129 DEFERRED** (disposizione sovrapposta agli stati).
34 checkpoint/34 turni USER, solo SKIP, media 3,79412 chiarimenti;
17 risolti prima del primo checkpoint. 69 passi automatici, counter entro due;
61 claim interpretazione, 8 SOURCE e 29 transizioni verificati: zero consumi
incrociati. Sei output misti conservano gli item validi. Caso positivo reale:
`t25.r4.c1` MISSING al SOURCE attempt 1 («SOURCE non ammessa») → RESOLVED/SOURCE
al attempt 2, interpretation fermo a 1. Fine `deferred_summary`,
WAITING_FOR_USER, auto_continue=false; nessun READY o DOCX forzato.

**Qualità ancora insufficiente:** i cinque field iniziali NON risolti nella
prova reale (forma PENDING per name parafrasato, altri MISSING con Company fuori
bucket); test software dei cinque valori passati. Ingegneria raggiunta:
denominazione/forma/sede SOURCE; direttore/qualifica MISSING, ordine e 8421
PENDING per person_role non grounded. CCIAA/numero iscrizione completo e data
abilitazione assenti dalla KB. Almeno un RESOLVED errato: stazione appaltante
per denominazione società tra professionisti `t31.r0.c1`. Nei 12 RESOLVED del benchmark
preliminare comparivano anche REA per Registro Imprese/CCIAA e stazione appaltante
per consorzio: non sono risultati corretti né modifiche dei gate. Non equiparare
RESOLVED a dato giusto; confronto storico limitato da DOCX/corpus diversi.

**Prossimo passo minimo:** query/bucket Company del primo batch, grounding
name/person_role di direttore/ordine/8421 e falso positivo di soggetto `t31.r0.c1`;
intervento distinto, senza rifare counter o grouped. Report con campi, metriche,
confronto, limiti e acquisizioni:
[retry separati e benchmark reale](docs/test-reale-retry-phases-2026-10-07.md).
Audit ignorati da Git: `backend/data/compilation-audit/retry-phases-20261007-final/`;
archivio preliminare `retry-phases-20261007/` conservato (12 SOURCE, 32 checkpoint,
media 3,72, zero valori USER). Codice/DOCX invariati in ciascun benchmark.

## Avvio e dipendenze — 7 ottobre 2026

Su richiesta dell'utente, `start.sh` installa le dipendenze frontend con
`npm ci --include=dev --include=optional` se `node_modules` manca o
`npm ls --all --include=dev --include=optional` rileva pacchetti mancanti/non
validi. Sincronizza il backend con `uv sync --locked` prima di avviare i servizi;
Uvicorn usa poi `uv run --locked --no-sync`. Un errore di installazione interrompe
l'avvio. Lockfile preservati. Su ulteriore richiesta, installazione automatica
locale di `uv` in `.tools/uv` tramite installer ufficiale senza modificare il
profilo shell, e Node.js 22.23.3 con npm in `.tools/node` tramite archivio
ufficiale verificato SHA-256. Bootstrap Node anche per versione incompatibile
o npm assente/non funzionante; Linux/macOS x64/arm64. Servono curl o wget e
strumenti di estrazione/checksum; niente sudo. README e help aggiornati.
Nessuna migrazione o reindicizzazione.

Verifiche effettive: `bash -n start.sh`, `./start.sh --help`, `git diff --check`;
cinque scenari in directory temporanee con comandi npm/uv simulati: dipendenze
assenti, presenti, incomplete, errore npm e errore uv. Tutti passati. Nessun
download reale o avvio dei servizi effettuato in questa verifica. Bootstrap
verificato anche con otto scenari isolati e download/strumenti simulati:
strumenti presenti, mancanti, Node vecchio, npm assente, checksum errato,
download fallito, npm ci fallito e uv sync fallito; tutti passati. Il primo
tentativo del test isolato mancava di gzip nel PATH di prova, corretto nel
harness prima dell'esecuzione finale. Il punto di
ripresa della compilazione descritto sotto resta aperto.

## Punto di ripresa

### Progetti demo creati — 7 ottobre 2026

Su richiesta dell'utente, esaminati `demo-documents/bandi/`, metadati `fonti.json`
e contenuto degli avvisi/bando; creati tramite POST `/api/projects` tre progetti
con titolo e descrizione documentati:
- `catanzaro-direzione-lavori-e-sicurezza`: Catanzaro - Direzione lavori e sicurezza;
- `minervino-di-lecce-elenco-sia`: Minervino di Lecce - Elenco SIA;
- `trapani-green-progettazione-e-direzione-lavori`: Trapani Green - Progettazione e direzione lavori.

Descrizioni marcate come casi didattici con dati aziendali simulati. Prima della
creazione l'elenco progetti era vuoto; verificati titoli e descrizioni tramite
GET dei singoli progetti dopo il salvataggio e totale finale pari a tre.
Questa richiesta riguardava la creazione dei progetti: fonti e moduli di gara
non caricati nei nuovi workspace. Fixture originali e profili AI preservati.
Nessuna modifica al codice, migrazione o reindicizzazione; diff check passato.

### Ambiente operativo locale — 7 ottobre 2026

Su richiesta dell'utente, installato **Ollama 0.40.0** e scaricato **BGE-M3**;
nessuna aggiunta a `start.sh` in questo intervento. Binari/librerie in
`.tools/ollama`, modelli in `.tools/ollama-models` (esclusi da Git). Comando
`ollama` disponibile tramite link in `~/.local/bin`; servizio systemd utente
`~/.config/systemd/user/ollama.service`, abilitato e attivo su
`127.0.0.1:11434`. Un solo modello caricato e una richiesta parallela per
contenere la memoria sulla macchina da circa 4 GB; inferenza CPU rilevata.
Verifica/riavvio: `systemctl --user status ollama` / `systemctl --user start ollama`.

Configurata tramite API normale la ricerca **Qdrant locale + bge-m3**;
indicizzazione effettiva di 17 frammenti, 1024 dimensioni, senza cancellazioni.
Le dipendenze backend sono state sincronizzate con `uv sync --locked --offline`;
Node 22.23.3 e controllo dei pacchetti frontend disponibili.
All'inizio non c'erano profili AI; durante l'intervento è comparso il profilo
utente **DeepSeek v4 / deepseek-flash**, lasciato predefinito. Installato anche
**Qwen3 1.7B**, profilo locale alternativo con contesto 4096, senza sostituire
DeepSeek. Modello piccolo di riserva: non valutato per moduli complessi.

Verifiche reali effettive, distinte dai test simulati sopra:
- API health backend, servizio Ollama e inventario modelli;
- API retrieval/check: embedding BGE-M3 da 1024 dimensioni e Qdrant disponibili;
- API retrieval/index: 17 frammenti aggiornati, zero eliminati;
- API ai/check: Qwen3 disponibile per generazione;
- query reale Qdrant/BGE-M3 su fonte sintetica in DB/storage temporanei;
- compilazione DOCX reale con DeepSeek di un solo campo sintetico:
  denominazione inserita correttamente, un campo scritto e zero irrisolti;
- risposta strutturata reale Qwen3 via adapter applicativo e schema JSON;
- `git diff --check` passato.

Nessun progetto o modulo di prova creato nel DB dell'app, nessuna credenziale
riportata. Queste prove verificano l'ambiente e un caso minimo: non attestano
il completamento dei moduli reali o la qualità del workflow conversazionale.
README aggiornato per distinguere embedding, generazione e servizio separato.
Il prossimo intervento software resta quello descritto sotto.

### Storico del punto di ripresa precedente al fix dei retry

La separazione indicata sotto come non implementata è ora completata nella
sezione «Ripresa attuale»; le prove seguenti restano storiche.

**Intervento sui chiarimenti raggruppati interrotto su richiesta dell'utente
per salvare il lavoro con un commit locale. Non considerarlo completato.**

Implementati nel workflow: raccolta persistente dei chiarimenti, checkpoint
dopo il lavoro automatico disponibile, priorità delle condizioni condivise,
massimo quattro slot per messaggio, planner semantico senza field_id,
aggiornamenti parziali, UNKNOWN/SKIP per elemento e pausa/ripresa del gruppo.
Metriche `chat.metrics`: automatic_resolved, user_required_fields, user_turns.
Due tentativi automatici per candidate, batch normale massimo 12, retry massimo
6, ciclo massimo 36 passi/600 secondi. Gli output strutturati invalidi sono
interamente rifiutati e recuperabili entro quel budget; provider/timeout e altri
errori tecnici conservano FAILED. Motore SOURCE/parser/renderer non modificati.

**Verifiche effettive sull'ultimo codice:** 276 test backend mirati, 1119 backend
completi, Ruff; 83 test frontend, lint/build; sei E2E browser desktop/mobile,
inclusi reduced-motion e chiarimenti raggruppati. Diff check passato.
I test software usano provider simulati e database temporanei; non attestano
il completamento del benchmark reale.

**Prove reali deepseek-flash, codice congelato durante ciascuna esecuzione:**

- Sessione `45474e57f4cf4b0f879296c097f06a91`, conversazione
  `conv-eece71eeb16a4c03`: cinque dati aziendali richiesti RESOLVED/SOURCE al
  primo passo senza USER; prosegue senza chiedere subito la procura. Dopo una
  ripresa normale arriva a 22 RESOLVED, poi un errore strutturato interrompe
  prima del checkpoint. Nessuna misurazione reale completa dei gruppi/turni.
- Dopo il recupero bounded degli output invalidi, nuova sessione
  `8361b0e782aa49d78f9ec45cff677a94`: 12 RESOLVED, 32 MISSING, 3 AMBIGUOUS,
  232 PENDING, zero valori USER. Messa in pausa via chat «basta»: v53,
  WAITING_FOR_USER + user_paused=true, domanda null e auto_continue=false.
  Resolve tardivo respinto con 409: pausa preservata.
- **Bug residuo:** il retry da sei mescola PENDING con errori di interpretazione
  e MISSING già cercati con errori SOURCE. Un JSON invalido dei primi consuma
  il secondo tentativo anche dei secondi. Nella seconda prova CF/PIVA restano
  MISSING; nella prima sono RESOLVED. Non dichiarare verificata la stabilità
  dei cinque dati nel workflow finale né completato il confronto dei turni.
- Originale invariato; nessun DOCX generato. Audit ignorati da Git in
  `backend/data/compilation-audit/grouped-clarifications-20261007/` e
  `grouped-clarifications-20261007-final/`: non inclusi nel commit.

**Prossimo passo:** separare la selezione dei retry per fase/stato
(interpretazione PENDING vs proposta SOURCE MISSING), senza cambiare il motore
SOURCE/gate. Aggiungere una regressione: candidate non interpretabile non deve
consumare il retry di un altro candidate con SOURCE valida. Questa separazione
**non è ancora implementata**. Poi test mirati/Ruff/diff e nuovo benchmark
reale con conversazione pulita, form 153/stessa KB, senza dati aziendali USER:
misurare checkpoint/gruppi/turni/unresolved, verificare cinque dati e direttore
tecnico. Non modificare codice durante il benchmark.

## Collegamento SOURCE — intervento precedente del 7 ottobre

Corretto il collegamento **candidate → SOURCE → bucket allowed → proposta →
validazione → RESOLVED**, senza modificare UI, parser, renderer, routing
conversazionale o RAG FORM/SOURCE/MIXED generale. Nel benchmark finale con
**deepseek-flash reale**, nuova sessione
`46d5be7dcf444b18ac519d7bf55d1680`, v5, sono persistiti tutti e cinque i criteri
richiesti: operatore economico, forma giuridica, sede legale, CF operatore e PIVA
→ **RESOLVED / SOURCE**, da Company KB, senza valori USER.
Necessario **un resolve esplicito aggiuntivo della sede** dopo un estratto
respinto; non presentare il risultato come successo completo al primo passo.
Diagnosi, raw prima della modifica, query, bucket e benchmark:
[test-reale-candidate-source-2026-10-07.md](docs/test-reale-candidate-source-2026-10-07.md).

### Cause concrete e modifica SOURCE della compilazione

- Per `t0.r5.c1` e `t0.r6.c1`, il vecchio bucket conteneva quattro chunk di
  `avviso.pdf`. `generalita-mapi.md` / Company KB, chunk -43, era nel pool
  del batch, recuperato per altri candidate, ma non ammesso per questi due.
  Il matcher proponeva la forma giuridica dalla SOURCE corretta e il gate
  respingeva «SOURCE non ammessa per questo candidate».
- L'operatore aveva anche un secondo falso negativo: la label FORM non era
  riconosciuta come richiesta dell'identità/ragione sociale. La rimozione di
  entrambi i token «operatore/economico» rendeva sempre falsa l'associazione
  letterale, anche con una prova SOURCE corretta ammessa in una copia diagnostica.
  Due riproduzioni reali read-only eseguite prima di modificare codice; non
  confuse con i raw storici non persistiti dal prodotto.
- Nuovo helper `compilation_sources.py`: una sola pianificazione semantica
  batch deriva cluster e fino a tre nomi equivalenti della proprietà da
  requirement/context. I contesti sono deduplicati; nessun valore proposto,
  dizionario di campi demo, nome aziendale/file/chunk hardcoded.
- Query brevi sulle proprietà. I risultati di un altro cluster entrano nel
  bucket aziendale solo attraverso una proprietà locale pertinente della
  SOURCE. Il validator richiede valore e intestazione nella stessa relazione
  `intestazione: valore`; non basta che la label compaia altrove nel profilo.
  Il requisito FORM originale resta grounded e invariato. Gate personali,
  SOURCE attuali/progetto/role, General KB, validatore DOCX e rivalidazione
  alla finalizzazione restano attivi. FORM e USER non diventano SOURCE.
- Quote/valori normalizzati tornano alla grafia letterale della fonte tramite
  soli Unicode/case/whitespace, senza fuzzy matching o riscritture del contenuto.
  Ricerca e bucket conservano source_names, query, chunk recuperati/allowed;
  evidence conserva file/chunk, scope, categoria e role.
- Budget: 12 candidate/passo; max tre chiamate LLM complessive per passo;
  max sei cluster di quattro requisiti, due query/cluster, 12 query totali,
  quattro evidence/cluster, pool max 24 chunk, allowed max otto/candidate.
  Un fallimento del planner conserva fallback letterale e coverage esplicita,
  senza retry aggiuntivi o chiamate per singolo campo.
- Nessuna migrazione/reindicizzazione né modifica SQL manuale. I MISSING
  preesistenti restano tali finché riesaminati tramite API normale.

### Benchmark reale SOURCE e limiti

- Progetto `minervino-di-lecce-elenco-sia`, form 153,
  `domanda-partecipazione.docx`; Qdrant locale + BGE-M3/Ollama;
  configurazione reale DeepSeek / `deepseek-flash`.
- Nuova conversazione `conv-43455f51f75b4f2c`, sessione sopra: POST create v1,
  resolve dei cinque candidate v3 → quattro RESOLVED e sede MISSING perché
  quote/valore non letterali; un nuovo resolve della sola sede → v5,
  **cinque RESOLVED/SOURCE, zero USER_PROVIDED**. Tutti dalla fonte demo
  `generalita-mapi.md`, file -7, chunk -43, scope global / category company.
- Valori: Mapi Ingegneria S.r.l.; Societa a responsabilita limitata;
  Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia;
  CF e PIVA didattici IT01234567890. Nessuna inserzione manuale di questi dati.
  Stato riletto via GET dopo la mutazione; gli altri quattro non sono stati
  resettati dal riesame della sede. Codice congelato durante il benchmark.
- Prova precedente con primi 12 candidate: quattro campi lasciati PENDING
  dal classificatore per label parafrasate, prima del SOURCE retrieval.
  Sessione nuova `2c1acae1e71c40e19989c28588e836d1`: tutti cinque risolti
  dopo un riesame mirato dei quattro PENDING. **Classificatore non corretto**
  in questo intervento: fuori dal collegamento SOURCE richiesto.
- Finale: 5 RESOLVED / 274 PENDING, sessione CREATED, nessun DOCX generato.
  Non è un test del completamento di tutti i 279 candidate né della UX.
  Restano falsi negativi conservativi di classificazione/quote: non promettere
  che un unico passo automatico risolva sempre i cinque campi.
- Originale invariato, SHA-256
  `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
  Sessioni precedenti preservate; acquisizioni ignorate da Git in
  `backend/data/compilation-audit/candidate-source-20261007/`.

### Verifiche effettive dell'intervento SOURCE

- Mirati finali: **250 passati**, con DB/storage temporanei e provider simulati:
  `uv run --locked pytest -q tests/test_compilation_sources.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_compilation_chat.py tests/test_compilation_controls.py tests/test_compilation_active_question.py tests/test_compilation_conversation.py`.
  Nuove regressioni SOURCE: **12 passate**, inclusi FTS5/Qdrant, alias generici,
  riassociazione limitata, valori di proprietà errate respinti, SOURCE condivisa
  senza contaminazione, provenance/chunk e rivalidazione alla finalizzazione.
- Backend completo finale: **1079 passati**, `uv run --locked pytest -q`;
  `uv run --locked ruff check .` e `git diff --check` passati.
  I tentativi software intermedi hanno segnalato errori nella selezione delle
  coorti della nuova fixture, corretti prima di queste esecuzioni finali.
- Benchmark reale distinto dai test software: normale HTTP, deepseek-flash,
  retrieval corrente e persistenza riletta; nessun provider simulato, valore
  USER o manipolazione manuale DB. Test frontend/browser/lint/build frontend
  non rieseguiti: UI e contratti non modificati da questo intervento.
- Nessun commit/push o ripristino delle modifiche locali già esistenti.

**Prossimo punto:** verificare nel normale flusso chat la stabilità della
classificazione prima del retrieval. Il fix SOURCE soddisfa i cinque criteri
persistiti nel benchmark circoscritto, con il riesame dichiarato; il completamento
automatico dell'intero modulo e la materializzazione finale restano da verificare.

## Chiarimento della domanda attiva — intervento precedente del 7 ottobre

Corretto il contratto delle **risposte a una singola domanda attiva** della
compilazione. **Entrambe le negazioni sono state verificate con deepseek-flash
reale**: «No, il sottoscrittore non agisce come procuratore.» e «no» producono
CONDITION_FALSE, senza field_id, senza retry e senza errori schema; il backend
aggiorna soltanto il target noto a NOT_APPLICABLE / USER e passa al prossimo
problema. Report completo con prompt, schema, raw prima/retry/dopo e transizioni:
[test-reale-active-question-2026-10-07.md](docs/test-reale-active-question-2026-10-07.md).

### Causa e modifica del chiarimento singolo

- Riproduzione prima della modifica, quattro chiamate reali su snapshot letto
  dalla sessione `d08866e079464d34bd2d2fc689392be8` v3, senza modificarla:
  il modello capisceva la negazione, ma copiava `id` da `fields[].id` del contesto
  al posto del richiesto `field_replies[].field_id`. Due errori identici in entrambi
  i tentativi: campo obbligatorio mancante e proprietà extra non ammessa. Il vecchio
  retry non indicava le cause precise; DeepSeek usa JSON mode, che non vincola
  i nomi delle proprietà dello schema Pydantic.
- `ActiveQuestionPlan` richiede la sola decisione semantica: VALUE,
  CONDITION_TRUE/FALSE, UNKNOWN, SKIP, REFUSE, PAUSE, CLARIFY; valore letterale,
  normalizzazione deterministica e breve rationale quando appropriati. Né schema
  né contesto single-field espongono ID di campo/sessione/versione al modello.
  `CHAT` permette una nuova domanda documentale e torna al routing esistente,
  senza un secondo planner. Il modello non sceglie il destinatario.
- Il backend lega l'azione alla domanda del proprio snapshot persistito, verifica
  revisione/progetto/conversazione e riusa i service della sessione. FALSE conserva
  motivo USER e valore nullo; TRUE riapre il candidate prioritario per SOURCE,
  senza risolvere un valore. VALUE conserva grounding e validatore DOCX.
  Alternative esplicite e CLARIFY non cambiano i campi. I controlli e i differimenti
  precedenti restano validi; nessuna nuova keyword per interpretare la condizione.
- Shortcut solo con workflow abilitato e un target coerente. Più destinatari,
  domanda assente o sessione sospesa/non conversazionale usano il percorso
  generale; nessuna selezione arbitraria. Una chiamata per messaggio e un solo
  retry con gli errori precisi. Nessuna modifica a schema DB, parser, renderer,
  RAG, UI o contratti frontend; nessuna migrazione/reindicizzazione necessaria.

### Verifiche effettive di questo intervento

- Mirati finali: **252 passati** con DB/storage temporanei e provider simulati:
  `uv run --locked pytest -q tests/test_compilation_active_question.py tests/test_compilation_conversation.py tests/test_compilation_controls.py tests/test_compilation_chat.py tests/test_form_retrieval.py`.
- Backend completo finale: **1067 passati**, `uv run --locked pytest -q`;
  `uv run --locked ruff check .` e `git diff --check` passati.
  Frontend/browser/lint/build frontend non rieseguiti: non toccati in questa modifica.
- Benchmark finale reale su due nuove conversazioni, avvio/resolve tramite HTTP,
  chiarimento attraverso la stessa API FastAPI via ASGITransport per catturare i
  raw, senza provider/risposte simulate; normale persistenza, riletta via HTTP:
  - negazione completa: sessione `5e1a6b1fcf8a4aa3a94188d89330077b`,
    conversazione `conv-59cdc5c0155d4eaa`, v5 → v6;
  - «no»: sessione `514078f1a6f5493a9164bd38ff809fa4`,
    conversazione `conv-379b5f72d59344f0`, v3 → v4.
  In entrambe target `t0.r4.c1` → NOT_APPLICABLE / USER, nessun valore fattuale,
  altri field invariati; domanda successiva «Operatore economico». WAITING_FOR_USER
  su quel prossimo problema, senza generazione implicita o loop sulla procura.
- Prima sessione: il classificatore iniziale aveva lasciato la procura PENDING
  per una label non grounded. Un resolve mirato tramite API esistente ha raggiunto
  la domanda; nessun dato/condizione imposto con SQL o valori USER. Seconda sessione:
  domanda raggiunta nel primo passo automatico. Questo limite è registrato, non
  nascosto né corretto durante il benchmark.
- Originale e codice applicativo invariati durante la prova (SHA-256); sessione
  iniziale della diagnosi e sessioni precedenti conservate. Nessun commit/push.
  Acquisizioni locali escluse da Git:
  `backend/data/compilation-audit/single-active-field-20261006/`.

**Prossimo punto:** il chiarimento di applicabilità singolo è corretto e provato
con il provider reale. Restano da discutere/correggere, su incarico esplicito, i
blocchi del classificatore e della coverage SOURCE descritti nel test precedente.
La compilazione automatica completa fino al DOCX non è ancora verificata: non
confonderla con l'esito positivo di questo intervento circoscritto.

## Test reale E2E precedente — 6 ottobre (storico)

Eseguito il **test reale E2E con deepseek-flash**, richiesto il 6 ottobre:
**compilazione automatica solo parziale**, senza correggere codice. Diagnosi e
registro: [test-reale-compilation-session-2026-10-06.md](docs/test-reale-compilation-session-2026-10-06.md).
Il workflow conversazionale implementato sotto resta lo stato software precedente;
gli esiti dei test simulati non vanno confusi con questa prova reale.

### Risultato reale e blocchi ancora da correggere

- Progetto `minervino-di-lecce-elenco-sia`, modulo originale ID 153,
  `domanda-partecipazione.docx`, 279 candidate. Profilo reale DeepSeek /
  `deepseek-flash`; Qdrant locale + BGE-M3/Ollama. Avvio dalla chat con mention
  strutturata e «me lo compili?», nuova conversazione `conv-2f20346327a544c7`.
  Sessione `c849656d4e2e46ccab0d42ecd3d13c18`, finale v20 / FAILED.
- Due passi completati: 24 candidate con esito persistito. Altri 12 candidate
  nel terzo gruppo fallito, tentato due volte con una sola ripresa dalla chat.
  Tre RESOLVED/SOURCE: sede legale, codice fiscale operatore e partita IVA,
  da `generalita-mapi.md`, Company KB globale, chunk -43. Identificativo fiscale
  didattico `IT01234567890`, già presente nelle fonti; nessun valore standard
  inserito manualmente per far riuscire il benchmark.
- Stato grezzo: 268 PENDING, 3 RESOLVED, 2 MISSING, 6 AMBIGUOUS; zero
  USER_PROVIDED/CONFLICTING/NOT_APPLICABLE. Gli otto problemi sono differiti:
  nel rapporto richiesto diventano DEFERRED, senza cambiare gli stati DB.
- Denominazione e forma giuridica esistono nella KB e vengono proposte dal
  matcher usando il chunk -43, recuperato per altri field. Il loro bucket
  ammesso contiene però soltanto `avviso.pdf`: i gate rifiutano correttamente
  quelle proposte con «SOURCE non ammessa per questo candidate». Non abbassati
  i filtri per far passare il test. Altri candidate restano PENDING per label
  parafrasate o person_role fuori dal form_quote; SOURCE non viene ricercata.
- Terzo passo: HTTP 502 «Output strutturato della risoluzione non valido»;
  ripresa normale dalla stessa conversazione, stesso fallimento. Riproduzione
  read-only del classificatore con provider reale e stesso batch: cinque
  decorative restituiscono `form_quote=""`, respinto dal minimo due caratteri
  dello schema; fallisce tutto il gruppo prima del salvataggio. Nessuna
  correzione di schema, prompt, output o sessione durante la diagnosi.
- UNKNOWN/SKIP, pausa con «basta», refresh e «riprendi» stessa sessione
  osservati nel percorso reale. Condizione della procura chiesta prima degli
  estremi. In due conversazioni aggiuntive, stesso modello/modulo/fonti:
  incertezza -> UNKNOWN senza valori; «Sì oppure no.» -> chiarimento senza
  modifiche ai field. **«non sono procuratore» e «No» falliscono nel planner**,
  non rendono NOT_APPLICABLE. Riproduzione reale read-only: `field_replies`
  contiene `id` anziché `field_id`, anche dopo retry; parsing respinto.
  Sessioni aggiuntive lasciate in pausa tramite normale «basta».
- Nessuna READY/GENERATED, nessuna bozza incompleta o finalize forzato.
  Materializzazione nel DOCX e input di un valore USER_PROVIDED non raggiunti:
  non dichiararli verificati. Originale immutato, hash prima/dopo e BLOB della
  sessione coincidenti. Persistenza verificata anche dopo riavvio dei servizi.
- Registro completo CSV/JSON, revisioni, evidenze e riproduzioni grezze in
  `backend/data/compilation-audit/real-e2e-deepseek-flash-20261006/`, escluso da Git.
  Le risposte grezze LLM dei resolve originali non sono persistite dal prodotto:
  le riproduzioni isolate sono indicate come nuove chiamate, non come output
  storici. Nessuna credenziale nel report.

Verifiche di questo test: browser Chromium su frontend/backend reali, API e
revisioni reali; letture SQL esclusivamente `mode=ro`, confronto hash e stato
API/DB, riproduzioni isolate con provider reale senza mutazioni delle sessioni,
controllo del diff e degli artefatti. Nessuna suite con provider simulati, Ruff,
lint o build rieseguita: nessuna modifica applicativa. Non confondere i numeri
software conservati sotto con verifiche nuove. Nessun commit/push; modifiche
locali precedenti preservate.

**Prossimo punto del test precedente (storico):** discutere questa diagnosi prima di correggere i contratti
classificazione decorative / risposte USER e la copertura SOURCE dei campi
standard. Poi ripetere il percorso reale completo fino al DOCX. Il RAG generale,
parser e renderer non sono stati modificati in questo test. Non riprendere
automaticamente le sessioni FAILED o forzarne i field tramite SQL.

### Stato software del workflow prima del test reale

Corretto il **workflow conversazionale della compilazione**: risposte di controllo,
pausa/ripresa persistenti, differimento senza loop e condizioni di applicabilità
prima del valore. Intervento circoscritto ai service/routing di compilazione e alla
vista dello stato; parser DOCX, renderer e RAG FORM/SOURCE/MIXED non ridisegnati.
Le milestone precedenti e i loro test sono conservati sotto come storico.

### Diagnosi concreta del test reale

Lettura **soltanto read-only** del DB locale: il field `t0.r4.c1` «Estremi procura»
era MISSING e conservava già `condition="se procuratore"`; il requisito FORM
includeva «(se procuratore) estremi procura (notaio, repertorio, raccolta)».
Il campo sulla carica del sottoscrittore era ancora PENDING: non era stata
stabilita la condizione. Il problema non era il parser:

- `apply_matches` rendeva MISSING qualsiasi campo ricercato senza valore;
  `chat_view` chiedeva la condizione soltanto per AMBIGUOUS, ignorandola in MISSING.
- Il planner non prevedeva UNKNOWN/SKIP/PAUSE. Le risposte non interpretabili
  salvavano un chiarimento e il selettore riprendeva sempre `issues[0]`.
- «basta» produceva reply della chat normale: nessuna mutazione della sessione.

### Correzione implementata

- Il planner esistente distingue semanticamente `compilation_control`, con
  `kind=unknown|skip|refuse|pause|resume`, `field_id` dove serve e `user_quote`.
  Rimane bounded (stesse chiamate/retry del planner), senza nuovo classificatore.
  Un piccolo guard per **messaggi interi inequivoci** («salta», «non lo so»,
  «basta», «riprendi», ecc.) evita che un errore del planner li trasformi in
  reply generiche o valori USER. Le parafrasi continuano a usare il routing
  semantico. Il guard richiede una sessione conversazionale e, per rinviare,
  un solo campo attualmente chiesto; non intercetta domande FORM normali.
- UNKNOWN/SKIP/rifiuto conservano status, valore, SOURCE/USER provenance e prove.
  `conversation_disposition` registra motivo, estratto USER, data e fingerprint
  dello stato significativo del campo. Non si inventano stati fattuali DEFERRED:
  il differimento riguarda la conversazione, non la disponibilità del valore.
- La proiezione esclude i problemi rinviati finché non cambia il loro stato
  significativo oppure l'utente ne chiede esplicitamente la revisione. Passa al
  prossimo problema o ai pending. Quando restano soltanto differimenti, mostra
  un riepilogo (max 5 nomi + conteggio), senza domanda individuale in loop.
  La sessione resta WAITING_FOR_USER e la finalizzazione completa rimane bloccata.
- Prima risposta ambigua/non valida: un chiarimento, senza cambiare campi.
  Seconda risposta non interpretabile sullo stesso stato: differimento e prossimo
  problema. Chiarimenti identificati per campo/tipo; vecchi testi non identificati
  non sovrascrivono una domanda corretta sulla condizione.
- PAUSE salva `chat_workflow.user_paused`, toglie la domanda attiva e impedisce
  i passi automatici, anche dopo refresh. Il composer può inviare «basta» durante
  analisi. La pausa invalida il claim/versione: un risultato tardivo non può
  sovrascriverla. Il provider già in volo può terminare, ma il suo risultato
  viene scartato. «riprendi» rinnova un ciclo della **stessa** sessione.
- Applicabilità: riuso di `field.condition`, già grounded nel FORM. UNKNOWN
  chiede la condizione prima del valore, anche nei vecchi MISSING. Il matcher
  SOURCE può proporre prove esplicite di condizione vera/falsa nello stesso batch:
  ID SOURCE ammesso, estratto/asserzione letterale, parole del predicato e polarità
  locale verificati conservativamente. Un estratto non può omettere una negazione
  o ipotesi precedente nella clausola SOURCE; una conferma USER parziale non può
  rimuovere l'incertezza del messaggio. Assenza, ipotesi, FORM o valore dipendente
  non provano la condizione. Prove discordanti, anche con vecchia exclusion,
  restano da chiarire. Pausa/ripresa conserva anche lo stato GENERATED e i download.
- USER «No»/negazione esplicita della condizione: solo field chiesto NOT_APPLICABLE,
  motivazione e provenance USER. «Sì»: applicabilità USER, field PENDING prioritario
  e nuova ricerca SOURCE prima di chiedere il valore. La condizione già grounded
  non si perde se il classificatore la omette nel retry. Nessuna esclusione di
  intere sezioni o inferenza automatica da forma giuridica.
- SOURCE pertinente + condizione vera + validatori DOCX -> RESOLVED; condizione
  vera senza valore SOURCE -> MISSING/domanda sul valore; falso -> NOT_APPLICABLE;
  sconosciuto -> AMBIGUOUS/domanda sulla condizione. Una risposta libera valida
  sul valore resta USER_PROVIDED, distinta da SOURCE.
- Nessuna tabella o migrazione nuova: dati nel JSON/revisioni esistenti. Conteggi
  di dominio mantenuti; `chat` aggiunge `paused_by_user`, `deferred` e riepilogo.
  API dello storico estesa compatibilmente con azioni paused/resumed/deferred.

### Verifiche di questo intervento

- Backend: **79 nuovi test** per controlli/applicabilità/differimenti, con provider
  simulati e DB/storage temporanei (FTS5/Qdrant dove applicabile). Test mirati
  su sessioni/conversazione eseguiti prima della suite backend
  finale completa: **1024 passati**. Ruff superato sullo stato finale.
- Frontend: **83 passati in 12 file**, inclusi SKIP/UNKNOWN, pausa/refresh/ripresa e
  invio di «basta» durante un passo in corso e negazione della condizione. Oxlint e build TypeScript/Vite passati.
- Browser Chromium: **8 passati**, API simulate, desktop/mobile e movimento
  ridotto; scenari compilation-chat, composer-model-menu, project-forms. Aggiunti
  salta/unknown/ripresa, pausa senza domanda dopo refresh, nessuna mutazione dei
  valori rinviati, oltre al flusso USER -> READY -> download. Frontend separato
  porta 5193; nessun uso del backend/storage locale dell'utente.
- `git diff --check` e controllo whitespace dei file nuovi superati. Nessun
  benchmark con provider reale: i test verificano il software, non DeepSeek/Gemma.

Comandi realmente eseguiti: `uv run --locked pytest -q tests/test_compilation_controls.py`,
`uv run --locked pytest -q tests/test_compilation_controls.py tests/test_compilation_conversation.py`,
`uv run --locked pytest -q tests/test_compilation_conversation.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py`,
`uv run --locked pytest -q`, `uv run --locked ruff check .`; frontend `npm test`,
`npm run lint`, `npm run build`,
`PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npm run test:e2e -- compilation-chat.spec.ts composer-model-menu.spec.ts project-forms.spec.ts`.

### Prova manuale e limiti residui

Riavviare backend/frontend aggiornati. Nessuna reindicizzazione necessaria;
nessuna modifica automatica ai DB/storage locali durante i test. La vecchia
sessione MISSING con condizione già registrata ora mostra la domanda di
applicabilità senza migrare i dati.

1. `@domanda-partecipazione.docx` + «me lo compili?» -> analisi -> condizione
   di «Estremi procura» -> «salta»: voce aperta con differimento SKIP, prossimo
   problema/analisi; riepilogo finale senza ripetizione immediata.
2. Stesso avvio -> condizione «se procuratore» -> «non sono procuratore»:
   NOT_APPLICABLE/USER per quel candidate, nessuna richiesta degli estremi.
3. «basta» -> pausa persistente senza domanda attiva -> refresh -> «riprendi»:
   stessa sessione/versione successiva, domanda o analisi dal punto conservato.
4. Confermare «Sì»: ricerca SOURCE del valore; se assente chiedere gli estremi,
   non inventarli. «non lo so» li lascia aperti, passando oltre.
5. «riassumilo» con mention resta FORM RAG, senza mutare la compilation.

Non c'è un motore generale di dipendenze: una condizione letterale per candidate,
nessuna propagazione automatica fra candidate/sezioni. La qualità dell'estrazione
semantica e delle parafrasi resta dipendente dal provider. I gate di applicabilità
sono prudenti e possono produrre falsi negativi; nessuna assenza SOURCE equivale
al falso. I rinvii non vengono riesaminati solo perché è stata caricata una nuova
fonte: serve ricerca/revisione esplicita o mutazione del field. READY non certifica
la completezza amministrativa. Vecchi conditional RESOLVED antecedenti a questo
intervento non sono riscritti automaticamente: riesaminarli esplicitamente.

**Prossimo punto:** ripetere il test reale con il provider scelto, soprattutto
controlli paraprasati e applicabilità sul sottoscrittore. Valutare successivamente,
con l'utente, eventuale raggruppamento dei chiarimenti. Non riaprire il RAG generale.
Preservate modifiche locali, inclusa `.env.example` eliminata; nessun commit/push.

## Milestone precedente: workflow conversazionale (storico)

È stato implementato il **workflow conversazionale di compilazione nella chat**, su
richiesta esplicita dell'utente. Supera la scheda tecnica manuale come esperienza
primaria. Un DOCX alla volta; parser, renderer e RAG FORM/SOURCE/MIXED restano
quelli già implementati. Non riaprire il RAG generale per proseguire la UX.

### Causa e soluzione

Il planner precedente poteva scegliere soltanto reply/retrieve; «me lo compili?»
finiva nel generatore RAG, mentre l'avvio della sessione era un'azione UI separata.
La compilazione reale e la risposta normale potevano quindi contraddirsi. La UI
esponeva inoltre ogni passo da 12 come un'operazione manuale dell'utente.

- Il planner esistente ora distingue anche compile, compilation_input,
  compilation_clarify e compilation_generate. Con mention strutturata + incarico
  passa al workflow prima del generatore RAG; il backend risponde «Certo. Analizzo
  il modulo e verifico le informazioni disponibili» e crea/riprende la coppia
  conversazione/form. Non è un elenco hardcoded di frasi. Domande informative
  sul modulo, dati o disponibilità restano FORM/SOURCE/MIXED.
- L'orchestratore frontend avanza **un passo per snapshot**; il backend autorizza
  ciascun passo con budget persistito: **36 passi / 600 secondi** per ciclo.
  Rimangono max 12 candidate e max 3 chiamate LLM per passo (108 per ciclo,
  oltre al planner utente e agli embedding). Il limite temporale impedisce nuove
  ammissioni; un passo già partito conserva timeout 180 secondi. Stop su domanda,
  READY, FAILED, errore, budget o mancato progresso dopo visita dei pending.
- GET/refresh non rinnova budget. Al limite una sola azione di alto livello
  «Prosegui compilazione» o incarico equivalente rinnova il ciclo. Nessun loop
  illimitato. Riaprendo ANALYZING si legge lo stato; un claim scaduto offre ripresa
  esplicita, senza restare indefinitamente sullo spinner.
- `chat` è una proiezione backend: domanda corrente, conteggi reali e avanzamento
  autorizzato. WAITING_FOR_USER propone una domanda naturale per **un solo campo**,
  alternative comprese. La conferma di applicabilità non diventa un valore.
- La risposta libera usa `/answer`, con session ID/versione. Il planner propone
  campo, valore e user_quote; il gate accetta soltanto il campo chiesto e valore
  nell'ultimo messaggio USER. Matching deterministico con confini di parola:
  «No» non può essere estratto da «Non lo so». Le date complete italiane sono
  normalizzabili; più date richiedono chiarimento. Nessun aggiornamento multiplo
  ambiguo o da FORM/storico/alternative non confermate. Restano i validatori DOCX.
- Valori liberi validi diventano USER_PROVIDED/provenance USER, con revisioni e
  aggiornamento localizzato; non sono dati verificati SOURCE. Segue la prossima
  domanda o ripresa automatica sui pending. «No» alla condizione esclude il solo
  candidate chiesto; «Sì» conferma la condizione ma lascia da chiarire il valore.
- La vista primaria è il thread con attività/spinner, quantità reali, domanda e
  download. Supporta prefers-reduced-motion anche nello scorrimento. La vecchia
  scheda è sotto **Dettagli compilazione**, inizialmente chiuso: conteggi tecnici,
  ID/prove, Continua analisi, Aggiorna stato, editor field, reset, motivo di
  esclusione e bozza incompleta esplicita. Non si devono pilotare i batch.
- READY chiede conferma breve (chat o **Genera DOCX**). Nessuna generazione
  incompleta implicita. Renderer originale + stato corrente, poi DOCX/report;
  nessun editor, pagina nuova, multi-documento o motore di scrittura duplicato.

### Persistenza, compatibilità e limiti

`chat_workflow` usa lo snapshot JSON esistente, nessuna tabella nuova. Budget,
pausa, chiarimento e conferma USER di applicabilità persistono. Aggiunta colonna
`conversation_turns.compilation_json` per session ID/azione nello storico;
contratti opzionali compatibili e `automatic=true` su resolve. Sessioni legacy
richiedono un avvio/ripresa esplicito; quelle standalone non sono collegate a
una conversazione arbitrariamente. Riavviare il backend per la colonna additiva;
**nessuna reindicizzazione richiesta**.

Restano i limiti della V1: semantica del modello, candidate grezzi, falsi negativi,
applicabilità prudente, allegati senza posizione scrivibile. Il chiarimento libero
si limita al campo chiesto: correzioni arbitrarie di altri campi o risposte
multi-field usano ancora i dettagli espliciti. Una risposta con più date o con alternative/incertezza espresse nel messaggio
viene rifiutata conservativamente anche se include una scelta descritta a parole.
Non c'è worker: la pagina aperta guida l'analisi; chiudendola lo stato rimane,
ma non parte un nuovo ciclo in background. La domanda corrente è la proiezione
dello stato; le revisioni conservano il prima/dopo, senza inventare turni LLM.
READY non certifica la completezza amministrativa del documento.

### Verifiche effettivamente eseguite

- Nuovi test backend conversazionali: **50 passati**, parametrizzati FTS5/Qdrant
  con DB/storage temporanei e provider simulati. Routing senza RAG contraddittorio,
  riuso, budget persistito, passi automatici, domanda, USER/date, aggiornamento
  localizzato, ambiguità/grounding, applicabilità, versioni, isolamento e conferma
  sicura di generazione. Suite backend completa: **945 passati**; Ruff superato.
- Frontend: **78 passati in 12 file**, lint Oxlint e build TypeScript/Vite passati.
- Browser Chromium: **8 passati** con API simulate, desktop/mobile e movimento
  ridotto: compilation-chat, composer-model-menu, project-forms. Due passi
  automatici, ambiguità senza update, risposta libera, refresh WAITING/READY,
  distinzione USER/SOURCE, generazione/download e assenza overflow.
  Screenshot verificati; frontend di prova separato sulla porta 5193.
- `git diff --check` e controllo whitespace dei nuovi file. Nessun benchmark
  con DeepSeek/Gemma reale; questi test misurano il software, non il modello.

Comandi: `uv run --locked pytest -q tests/test_compilation_conversation.py`,
`uv run --locked pytest -q`, `uv run --locked ruff check .`; frontend con Node
locale: `npm test`, `npm run lint`, `npm run build`,
`PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npm run test:e2e -- compilation-chat.spec.ts composer-model-menu.spec.ts project-forms.spec.ts`.

### Prova manuale e prossimo punto

Riavviare backend/frontend aggiornati e usare una conversazione nuova nel progetto
di prova con DOCX e SOURCE pertinenti:

`@domanda-partecipazione.docx` + «me lo compili?» → risposta di avvio → attività e
analisi automatica → domanda assistant → risposta libera univoca → valore USER e
prossima domanda/ripresa → READY → conferma generazione → DOCX/report.

Controllare «riassumilo» con la stessa mention: solo chat FORM, nessun avvio.
Riaprire WAITING/READY e provare una risposta ambigua: valori invariati. Nei dettagli
verificare che il valore USER non sia presentato come SOURCE e che il DOCX venga
sempre generato dall'originale. Nessuna bozza parziale senza azione esplicita.

**Prossimo punto:** benchmark con il provider reale del progetto su routing,
classificazione dei candidate e qualità delle domande. Valutare poi raggruppamento
prudente dei chiarimenti condizionali o correzioni di campi diversi: da discutere,
non da implementare automaticamente. Le invarianti FORM/SOURCE/USER restano ferme.
Preservate modifiche locali, inclusa `.env.example` eliminata; nessun commit/push.
I test non hanno usato database/storage originali dell'utente.

## Milestone precedente: integrazione manuale chat/@ (storico)

È ora collegata la **CompilationSession V1 alla chat esistente**, con una mention
`@` strutturata per un solo modulo e azioni inline. Questa milestone è stata
richiesta esplicitamente dall'utente; le precedenti indicazioni «chat/@ da
progettare» sono superate per il percorso qui descritto. Non è stata implementata
l'interpretazione libera dei chiarimenti. Non riaprire il RAG generale o
ridisegnare l'extractor MIXED per proseguire questa integrazione.

### Integrazione chat implementata

- Il composer mostra i soli `project.files.kind=form` del progetto corrente
  digitando `@`, con filtro per nome, selezione da tastiera/click e chip singola.
  Il riferimento passa come `form_id` all'API; non è testo spacciato per evidenza.
  I TXT restano contesto interrogabile, l'avvio compilazione riguarda i DOCX.
- Una domanda normale con mention non crea sessioni: il planner esistente
  riceve il riferimento esplicito per risolvere le anafore. Il backend verifica
  progetto/ruolo e vincola FORM/MIXED al documento selezionato, anche se il
  planner propone un altro ID. Le domande fattuali restano SOURCE. Nessuna
  modifica a extractor, matcher, filtri, budget RAG o renderer.
- `POST /compilation-sessions` accetta `start_in_chat=true`: se manca una
  conversazione la crea nella stessa transazione della sessione; se esiste
  riusa la sessione della coppia conversazione/form. `BEGIN IMMEDIATE` evita
  duplicati da avvii concorrenti sulla stessa coppia. Eventuali duplicati
  storici non vengono cancellati: si riprende il più recente.
- L'elenco sessioni accetta `?conversation_id=...`, validato nel progetto.
  Riapertura e refresh leggono elenco/dettaglio backend. La UI mostra un solo
  snapshot di sessione alla volta, del modulo selezionato oppure l'ultimo della
  conversazione se non c'è una mention. Nessuno stato di compilazione è salvato
  soltanto in React o localStorage.
- Riquadro nella conversazione con documento, stato, tutti i conteggi backend,
  problemi aperti e valori già valutati espandibili. I pending restano posizioni
  da analizzare, non informazioni automaticamente richieste all'utente.
- **Continua analisi** esegue un solo `resolve`, fino a 12 candidate. Non ci
  sono loop AI. Se si riapre una sessione ANALYZING, polling GET ogni tre secondi
  legge lo stato: non avvia altri step. Claim e versioni sono quelli della V1.
- **Chiarisci/Correggi** apre un solo input inline, legato al `field_id`.
  **Salva valore** usa PATCH e provenance USER; non lo presenta come verificato
  SOURCE. Sono disponibili ricerca mirata per un campo irrisolto, esclusione
  esplicita con motivo e reset. Campi già decisi richiedono reset prima della
  rivalutazione. Le prove FORM e SOURCE restano separate e conservano la KB.
- **Genera DOCX** per READY/stato senza problemi; **Genera bozza con campi
  irrisolti** è un'azione esplicita distinta. Download DOCX/report nella chat.
  Una bozza precedente rimane identificata con la versione da cui deriva.
  La generazione usa sempre il renderer e l'originale della V1.
- Annullamento e controllo delle richieste al cambio progetto/conversazione/
  modulo; una creazione tardiva non riapre la chat abbandonata. I 409/errori
  rileggono lo stato senza ripetere la mutazione. Gli errori di validazione
  mantengono il valore digitato per consentire la correzione.

### Persistenza e compatibilità

Due colonne additive all'avvio: `conversations.selected_form_id` (FK al modulo,
ON DELETE SET NULL) e `conversation_turns.form_reference_json` (snapshot storico
ID/nome). Nessuna nuova tabella. `form_reference` è opzionale nelle risposte chat,
nei turni e nel dettaglio conversazione. La mention viene conservata con l'invio
del messaggio o l'avvio della sessione; una selezione non ancora inviata è una
bozza locale. Rimuoverla e inviare un messaggio azzera il contesto corrente,
senza alterare i riferimenti dei turni precedenti né cancellare la sessione.

Riavviare il backend aggiornato per applicare le colonne. Nessuna reindicizzazione
richiesta da questo intervento; restano le istruzioni per i vecchi form senza
frammenti nel README. Non sono stati modificati database/storage originali durante
i test. Preservate tutte le modifiche precedenti, inclusa `.env.example` eliminata.
Nessun commit o push.

### Verifiche dell'integrazione chat

- Backend mirato: **161 test passati** su sessioni, guardie, chat e FORM retrieval,
  inclusi **14 nuovi casi** con FTS5/Qdrant reali in ambiente temporaneo e provider
  simulati. Suite backend completa: **895 passati**. Ruff superato.
- Frontend: **74 test passati** in 12 file, Oxlint e build TypeScript/Vite superati.
- Browser Chromium: **6 test passati**, desktop e mobile, sugli scenari
  `compilation-chat`, `composer-model-menu`, `project-forms`, con tutte le API
  simulate e frontend separato sulla porta 5193. Verificati anche screenshot e
  assenza di overflow orizzontale nel nuovo flusso.
- `git diff --check` verificato a fine intervento. I test software non misurano
  la qualità semantica di DeepSeek/Gemma; nessun benchmark con provider reale.

Comandi principali effettivamente eseguiti:

```bash
# backend/
uv run --locked pytest -q tests/test_compilation_chat.py tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_chat_flow.py tests/test_form_retrieval.py
uv run --locked pytest -q
uv run --locked ruff check .
# frontend/, Node locale in PATH
npm test
npm run lint
npm run build
PLAYWRIGHT_BASE_URL=http://127.0.0.1:5193 npx playwright test e2e/compilation-chat.spec.ts e2e/composer-model-menu.spec.ts e2e/project-forms.spec.ts
```

### Prova manuale e prossimo passo

Su un progetto di prova con DOCX e fonti pertinenti: `@documento` → eventualmente
«riassumilo» (solo chat FORM) → **Avvia compilazione** → **Continua analisi** →
WAITING_FOR_USER → **Chiarisci**, salva un valore o indica non applicabilità →
continua sugli altri pending → READY → **Genera DOCX** → **Scarica DOCX/report**.
Ricaricare e riaprire la conversazione fra i passaggi: sessione, versioni,
conteggi e provenienza devono restare quelli persistiti. Verificare che una
correzione USER non azzeri i valori SOURCE degli altri campi.

Rimangono i limiti della V1 backend (applicabilità prudente, falsi negativi,
candidate grezzi, obblighi/allegati senza posizione DOCX). READY non certifica
la completezza amministrativa. Il riepilogo è lo stato corrente aggiornabile,
non una sequenza di falsi turni LLM: lo storico completo resta nelle revisioni
backend. Sessioni create prima senza conversation_id restano utilizzabili via
API; non sono associate arbitrariamente a una chat.

**Prossimo punto:** prova del flusso con il provider scelto e definizione del
collegamento fra messaggi liberi e `field_id`: distinguere un chiarimento da una
domanda ordinaria, proporre aggiornamenti espliciti, chiedere conferma quando
l'associazione è ambigua e conservare USER/versione/validazioni. Non implementare
automaticamente questa interpretazione, nuovi editor o compilazione multi-documento.

## Milestone precedente: CompilationSession V1 backend (storico)

È implementata la **CompilationSession V1 backend**, per un DOCX archiviato
alla volta. L'utente ha esplicitamente considerato il RAG abbastanza stabile
per procedere e ha autorizzato questa milestone: le precedenti indicazioni
di continuare a correggere MIXED prima delle sessioni sono quindi **superate**.
Non riaprire l'extractor o il RAG generale per questa ragione. Restano noti
falsi negativi conservativi; FORM non verifica valori, SOURCE pertinente sì.

La guida completa, mappa della pipeline, API, budget, esempio demo e istruzioni
manuali sono in [docs/compilation-session-v1.md](docs/compilation-session-v1.md).
Nessun menu `@`, nuova pagina, editor, collegamento automatico alla chat,
compilazione multi-documento o ciclo autonomo implementato.

### Architettura e comportamento implementati

- `compilation_sessions`: progetto, form, conversazione opzionale, snapshot
  immutabile dei byte originali, candidate strutturali in JSON, versione e date.
  `compilation_session_revisions`: cambiamenti prima/dopo e azioni. Sono due
  tabelle additive, create all'avvio; `document_fields` è la revisione demo e
  `document_compilations` conserva risultati immutabili, quindi non sono state
  impropriamente riutilizzate come stato modificabile dei candidate.
- La creazione controlla progetto/form/conversazione, legge il DOCX archiviato,
  usa `inspect_docx`, conserva ID e riferimenti strutturali. Nessuna AI o bozza
  in questa fase. Una sessione resta riprendibile leggendo SQLite. La rimozione
  del form archiviato azzera il collegamento, conservando lo snapshot originale
  e il riferimento storico; la cancellazione del progetto elimina le sessioni.
- `resolve`: massimo 12 candidate, una classificazione strutturale, il planner
  SOURCE esistente e una proposta in batch. Grounding FORM, query derivate dai
  requisiti, stessi filtri FTS5/Qdrant e validatori di associazione MIXED. Nessun
  uso degli embedding per trovare la posizione da scrivere. Nessun retry del
  nuovo classificatore/matcher e nessuna modifica all'extractor della chat.
- Budget: massimo tre chiamate chat LLM, sei gruppi, dodici query e 24 SOURCE
  per richiesta, fino a quattro proposte per campo. Ogni gruppo conserva la
  propria copertura; esclusi per budget restano PENDING/coverage_limit. I pending
  mai analizzati precedono quelli già tentati. Centinaia di candidate richiedono
  richieste successive esplicite, non un agent loop. Timeout 180 secondi,
  claim persistito di 240 secondi per ripresa dopo crash.
- Stati campo: PENDING, RESOLVED, MISSING, AMBIGUOUS, CONFLICTING,
  NOT_APPLICABLE, USER_PROVIDED. RESOLVED richiede SOURCE valida; FORM può
  soltanto sostenere il requisito o classificare uno spazio decorativo senza
  etichetta. USER_PROVIDED è separato da RESOLVED per non fingere verifica
  documentale. Gli aggiornamenti utente sono localizzati, espliciti per ID,
  con azioni set/not_applicable/reset e storico precedente/nuovo.
- Stati sessione: CREATED, ANALYZING, WAITING_FOR_USER, READY, GENERATED,
  FAILED. Se restano solo pending torna CREATED, con conteggio per continuare;
  missing/ambiguous/conflicting producono WAITING_FOR_USER, non un errore tecnico.
  Summary e open_issues sono nell'API e nel report della generazione.
- Applicabilità prudente: esclusione USER esplicita o dichiarazione SOURCE
  esplicita sulla condizione FORM; nessuna deduzione della partecipazione dalla
  forma societaria. Non è un motore generale di regole. Candidate grezzi non
  diventano automaticamente campi obbligatori o domande da fare all'utente.
- Versione obbligatoria per le mutazioni; 409 su versioni superate o claim attivo.
  Errori provider/parser/storage conservano lo stato precedente, oppure marcano
  FAILED senza applicare mezzi batch. Le SOURCE vengono rilette prima del commit
  della risoluzione e della generazione; fonti mutate/cancellate/non più ammesse
  non autorizzano una scrittura.
- Finalizzazione: adapter ai `ModelProposals`, validazione DOCX esistente,
  `fill_docx` dallo snapshot originale, nuovo record `document_compilations` e
  stessi download. Pending/missing/ambiguous/conflicting bloccano di default;
  `allow_unresolved=true` genera esplicitamente una bozza con vuoti e report.
  Mai riscrittura di una bozza precedente, mai indicizzazione degli output.
  Valori USER espliciti possono confermare scelte come «No», ma non aggirano
  firme, email, integrità numerica, limiti o posizioni. Questa autorizzazione
  non è disponibile alle proposte AI del percorso DOCX precedente.

### API V1

Prefisso `/api/projects/{project_id}/compilation-sessions`:

| Operazione | Metodo e suffisso |
|---|---|
| Creare da form_id e conversation_id opzionale | `POST` sul prefisso |
| Elencare / rileggere stato e candidate | `GET` sul prefisso / `GET /{session_id}` |
| Analizzare i prossimi pending o field_ids espliciti, massimo 12 | `POST /{session_id}/resolve` |
| Fornire valori, escludere o rimettere pending campi espliciti | `PATCH /{session_id}/fields` |
| Leggere prima/dopo delle revisioni | `GET /{session_id}/revisions` |
| Generare una nuova copia e report | `POST /{session_id}/finalize` |

`last_generation.downloads` restituisce i percorsi esistenti
`/document-compilations/{run_id}/download/{docx|report|template}`.
Usare sempre la versione dell'ultima risposta: resolve la incrementa sia
all'acquisizione del claim sia alla conclusione. Non serve un nuovo upload
per riprendere o rigenerare una sessione.

### Verifiche di questo intervento e limiti

Eseguiti **287 test mirati** (sessioni, guardie, motore DOCX/email, controlli
requisiti, planner SOURCE e retrieval FORM/SOURCE/MIXED) e **881 test backend
completi**, tutti superati. Ruff e `git diff --check` superati. Nessun frontend
modificato o test frontend rieseguito in questo intervento.

Comandi effettivamente eseguiti da `backend/`:

```bash
uv run --locked pytest -q tests/test_compilation_sessions.py tests/test_compilation_session_guards.py tests/test_docx_compilation.py tests/test_docx_email_fields.py tests/test_requirement_checks.py tests/test_source_planning.py tests/test_form_retrieval.py -x
uv run --locked pytest -q
uv run --locked ruff check .
```

Le nuove regressioni specifiche delle sessioni sono 52, incluse nella suite
completa. Le esecuzioni intermedie da 34, 50 e 142 test precedono l'ultimo
insieme mirato: non sono verifiche aggiuntive di qualità semantica.

Database e storage temporanei; FTS5 e Qdrant locali reali con embedding/provider
simulati. Coperti ripresa senza memoria, byte originali immutati, tutti gli stati,
isolamento, USER localizzato, versioni concorrenti, fonti cambiate durante AI,
rollback storage e generazione concorrente, lease scaduto, cancellazione task,
contratti JSON DeepSeek/Ollama, campi di tabella e segnaposti di paragrafo.
Nessun benchmark reale del nuovo workflow con DeepSeek/Gemma in questo intervento.

La fixture DOCX reale ha 279 candidate. Il test analizza otto posizioni 5.d con
fonti simulate: sette resolved (denominazione, forma, sede, nome/qualifica/ordine
del direttore e numero albo **8421**), data di abilitazione missing, 271 pending.
L'organigramma è un allegato testuale senza candidate dedicato: non viene
inventata una posizione DOCX né dichiarata la disponibilità dell'allegato.
READY non dimostra la completezza degli obblighi fuori dai candidate.

Restano limiti conservativi del matcher e della classificazione. Non ci sono
regole generali di applicabilità, composizione automatica di campi complessi,
risoluzione degli obblighi/allegati non scrivibili, interpretazione libera dei
chiarimenti o garbage collection delle revisioni. Il contesto strutturale del
passo è limitato a 60.000 caratteri; gruppi troppo grandi si possono ridurre,
singole tabelle oltre budget richiedono revisione manuale.

Le tabelle saranno create dal normale avvio aggiornato. Nessuna migrazione dei
vecchi risultati o reindicizzazione necessaria, nessuna modifica ai dati locali
dell'utente durante i test. Tutte le modifiche precedenti, inclusa la cancellazione
di `.env.example`, sono state preservate. Nessun commit o push.

**Prossimo punto:** provare una sessione su una sezione con il provider scelto,
poi collegare alla chat creazione/riepilogo/aggiornamenti espliciti/download.
La base backend offre le operazioni richieste per l'integrazione; menu `@`,
UX dei chiarimenti e scelta della sessione rimangono un lavoro successivo.
Non implementarli automaticamente in una chat futura senza richiesta.

## Punto di ripresa precedente: SOURCE MIXED (storico)

L'ultimo intervento riguarda esclusivamente **associazione e copertura SOURCE
di MIXED**. Il numero di iscrizione professionale **8421 è ora verificato**
nelle prove reali B/C: non occorre che la fonte ripeta la parola «albo», ma
numero, iscrizione e ruolo personale devono risultare associati nell'estratto.
Una sola pianificazione SOURCE in batch produce al massimo sei gruppi, due
query e quattro evidenze per gruppo. Ogni requisito è cercato oppure indicato
esplicitamente come non ricercato per limite di copertura/budget. Non c'è più
il top-k globale di quattro SOURCE. Il matcher ha un compito stabile, senza
rispondere alla formulazione originale della domanda. Ruoli, scope e KB restano
invariati. Nessuna modifica all'extractor FORM, a `intents.py`, agli indici,
ai contratti API/frontend, al parser DOCX o ai workflow di compilazione.

Ultima verifica: **329 test mirati e 829 test backend completi** superati;
Ruff e diff check superati. Benchmark reale DeepSeek A–D: B **7/11** verificati,
C **4/6**, A **0/10**, D **0/16**. Tutti i requisiti di queste quattro prove
hanno copertura SOURCE; nessuno è escluso dal budget. A rimane un falso negativo
del matcher: codice fiscale/partita IVA arrivano nel contesto ammesso, ma il
modello restituisce `supports: []`. D riguarda prevalentemente dichiarazioni,
alternative di partecipazione e procedure concorsuali. I dettagli sono nella
sezione «SOURCE MIXED: diagnosi e correzione del 6 ottobre» sotto.

Il precedente intervento aveva corretto il **blocco dell'estrazione MIXED con DeepSeek**:
lo schema accettava al massimo otto requisiti e rifiutava l'intera risposta
quando il modello ne restituiva dieci, anche tutti sostenuti da estratti FORM.
Il problema è stato riprodotto prima di modificare codice. L'extractor ora usa
un compito documentale dedicato, schema esplicito anche in JSON mode, dati
personali distinti per campo/ruolo e un unico retry con gli errori concreti.
Accetta fino a 32 proposte, verifica gli estratti, deduplica e seleziona fino a
16 requisiti per il turno. Le premesse dell'utente non diventano requisiti.
La sezione 5.d ha prodotto **11 requisiti validati** nella nuova prova reale;
la fase SOURCE è partita e sei valori sono stati verificati.

La precedente correzione del **bug MIXED di disponibilità non supportata** resta:
Gemma classificava «con i documenti che ho posso iniziare a compilarlo?» come
`form`, senza cercare alcuna source. Il backend ora impone `mixed` per richieste
esplicite di disponibilità, ricava le query SOURCE da requisiti citati nel FORM
e compone la risposta usando soltanto valori con estratti SOURCE verificabili.
I due contesti hanno filtri e budget separati; una citazione FORM non può
validare la disponibilità di un valore nel confronto MIXED.
La precedente indicizzazione dei moduli era già presente ed è stata preservata:
nessuna nuova modifica a ingestion, parser strutturale o motore DOCX.
Non sono stati implementati compilazione iterativa, sessioni, menu `@` o nuova UI.

Prossimo punto di ripresa: usare la traccia A del benchmark corrente per valutare
il matcher a parità di requisiti e fonti già recuperate. **Non considerare ancora
l'intero MIXED congelato per la CompilationSession**: associazione 8421 e
copertura tracciata sono corrette, ma non è risolto ogni falso negativo semantico
della generazione. L'extractor è stato lasciato invariato e in alcune prove
intermedie ha ancora rifiutato output non grounded; non aggirarne le garanzie.
La compilazione iterativa resta da progettare, senza implementazione autorizzata
in questo intervento. Non allargare automaticamente il lavoro all'extractor.
I moduli già indicizzati non richiedono riestrazione per questa modifica; quelli
ancora privi di frammenti richiedono il comando esplicito già disponibile.
Il modulo corrente di `prova`, file 155, ha 22 frammenti; il file 154 senza
frammenti riguardava la diagnosi precedente. Nessun dato o indice locale
dell'utente è stato modificato dalle prove: sono state usate copie temporanee.

La richiesta iniziale era mappare il progetto, verificare qualità e codice
morto, quindi migliorare la compilazione. La mappa e l'audit sono già in
[docs/mappa-progetto.md](docs/mappa-progetto.md): non occorre rifarli da zero.
La base è utilizzabile per il prototipo, ma i test software non dimostrano
l'accuratezza dei dati compilati da un modello reale.

## Richieste e orientamento dell'utente

- Il relatore ha chiesto una **compilazione iterativa**, perché il percorso
  precedente non era soddisfacente. La richiesta successiva ha definito la V1:
  iterazione sullo stato persistente, passi limitati e input utente espliciti,
  senza ciclo autonomo. La UX della chat rimane da definire.
- L'utente immagina compilazione e chat nella **stessa vista**, con un pulsante
  o `@` nel compositore per avviare la compilazione e scaricare documenti/report.
  È una preferenza espressa, non una funzionalità già disponibile.
- Dopo una prova con `gemma4:e2b`, ha chiesto di verificare anche il codice:
  non attribuire automaticamente ogni risposta errata al modello piccolo.
- È favorevole a indicizzare il modulo, ma teme che il sistema confonda
  moduli, fonti aziendali e dati. Ha poi richiesto esplicitamente il confronto
  informativo `mixed`, mantenendo distinti ruolo e scope/KB. Questa parte è
  implementata; anche la V1 backend di compilazione è ora implementata.

## Cosa esiste oggi

| Area | Stato verificato |
|---|---|
| Fonti documentali | Fonti PDF/TXT/Markdown di progetto e globali, estrazione e frammenti in SQLite. |
| Moduli da compilare | Upload, elenco, download e rimozione di originali DOCX/TXT, massimo 20 MB, ruolo `form`. Il corpo DOCX/TXT viene estratto e frammentato; originale invariato. |
| Chat | Il modello decide risposta diretta oppure ricerca e target source/form/mixed; un controllo backend impone mixed per le richieste esplicite di disponibilità. Fino a tre query FORM; in MIXED fino a sei gruppi/dodici query SOURCE derivate dai requisiti citati. Il backend distingue requisiti, valori verificati, dati non verificati e requisiti non ricercati. |
| Retrieval | FTS5 oppure Qdrant, stessi indici per entrambi i ruoli. Filtri prima della selezione e rilettura delle evidenze impongono ruolo/progetto/modulo. Solo source ammette fonti globali. |
| Provenienza | Evidenze API e storico conservano scope `project:ID`/`global` e category `company`/`general` dove applicabile, oltre a ruolo, ID documento/frammento, progetto, nome e metadati. |
| Compilazione DOCX | Percorso precedente a chiamata unica conservato; nuova CompilationSession persistente con risoluzione, correzioni utente e renderer esistente. |
| Contesto DOCX | Il percorso precedente mantiene fonti per budget; le sessioni partono dal modulo archiviato e usano planner/retrieval SOURCE già disponibili. |
| Iterazioni e UI | Sessioni backend disponibili; collegamento chat, selezione `@`, revisione dialogica e scheda UI non implementati. |
| Percorsi separati | Generazione Markdown e pagine dimostrative esistono; la revisione dimostrativa non è un editor del DOCX prodotto. |

La modalità DOCX a gruppi da 32 e le riparazioni automatiche sono state rimosse
nel commit `f916239`. Errori strutturali della risposta interrompono il percorso
unico; le proposte bloccate dai controlli restano vuote e sono segnalate nel
report. Il passaggio a un ciclo iterativo richiede uno stato e regole esplicite,
non il semplice ripristino della vecchia suddivisione in gruppi.

## Lavoro già completato

L'audit iniziale, conservato nel commit `2e4e946`, ha corretto:

- Effetti delle risposte chat tardive dopo un cambio di progetto/conversazione.
- Validazione delle email DOCX: confronto con l'indirizzo completo nella fonte,
  anche se il modello ne cita solo una parte.
- Incoerenze fra file dell'artefatto, metadati e indice in caso di errori SQL.
- Replay delle compilazioni: inoltro delle opzioni AI e lettura del template
  nei percorsi corrente e storico.

Sono stati inoltre attivati TypeScript strict e lo schema JSON delle proposte
DOCX per Ollama. Rimosse le dipendenze inutilizzate `react-markdown`,
`remark-frontmatter` e `remark-gfm`. Attualmente la risposta chat viene resa come
testo in un paragrafo: il rendering Markdown non è implementato.

La mappa inventaria nove metodi client senza chiamanti applicativi, alcuni
usati nei test. Sono stati conservati perché le API esistono e possono servire
al nuovo percorso: `projectArtifacts`, `projectArtifact`, `updateProjectArtifact`,
`generateDraft`, `documentCompilations`, `documentCompilation`, `compileDocument`,
`downloadCompilation`, `projectEvidence`.

## Diagnosi della prova con Gemma

Verifica del 5 ottobre **precedente all'integrazione RAG dei moduli**, sul database
locale in sola lettura: progetto `prova`,
conversazione `conv-387b173d8b53480e`, turni 77 e 78.

L'utente aveva caricato `domanda-partecipazione.docx` e chiesto prima una
spiegazione, poi la documentazione necessaria in dieci punti e i dati Mapi.
La seconda risposta ripeteva l'apertura della prima, senza i dieci punti.

Riscontri:

1. Il DOCX era presente e leggibile, file 154, ruolo `form`, **zero frammenti**.
   Il parser rilevava 279 posizioni candidate: non sono 279 dati necessariamente
   da compilare. Nel progetto non erano presenti file con ruolo `source`.
2. Le 7 e 8 evidenze dei due turni provenivano tutte dalle fonti globali:
   `generalita-mapi.md`, `progettazione-opere-pubbliche.txt` e/o
   `visura-mapi-ingegneria-simulata.pdf`. **La chat non aveva letto il modulo.**
3. La frase errata «carico e relative qualifiche documentate» derivava da un
   frammento che iniziava nel mezzo di «incarico»: difetto concreto nel codice
   di suddivisione, poi ripreso dal modello.
4. «Assistenza tecnica agli enti nella» coincideva con la fine di un altro
   frammento. I vicini recuperati non garantiscono una sezione completa.
5. Il backend passa l'ultimo messaggio e distingue la cronologia dalle prove.
   Non è emersa una duplicazione applicativa della vecchia risposta. I controlli
   verificano gli ID delle citazioni, non il loro supporto semantico o il
   rispetto dei dieci punti richiesti.

Entrambi i turni erano `completed`, senza errore tecnico salvato. Le query di
ricerca e le risposte grezze del provider non sono persistite: non è possibile
ricostruire esattamente ogni richiesta. La configurazione letta durante la
diagnosi era Qdrant locale/BGE-M3, chat `gemma4:e2b`; non è una registrazione
storica completa delle impostazioni dei turni.

Il [report locale dettagliato](backend/data/chat-audit/prova-turni-77-78.md)
è escluso da Git e può mancare in un altro checkout. I riscontri essenziali
sono riportati qui proprio per non dipendere da quel file.

## Modifiche pendenti e dati non aggiornati

Prima della creazione dei due documenti, `git status` mostrava:

| File | Stato e provenienza |
|---|---|
| `.env.example` | Eliminazione preesistente dell'utente; non ripristinata. |
| `backend/app/ingestion.py` | Correzione non ancora committata di `chunk_text`: confini delle parole anche nell'overlap e con newline; parametri validati e avanzamento garantito. |
| `backend/tests/test_ingestion_chunks.py` | Nuovo file non ancora committato, dieci casi di regressione per la correzione. |

AGENTS.md e STATUS.md si aggiungono a queste modifiche. L'integrazione RAG aggiunge
modifiche a upload moduli, planner, routing chat, retrieval SQL/vettoriale,
generazione e contratti delle evidenze, più test e uno script di reindicizzazione.
Il frontend aggiunge soltanto l'etichetta del ruolo nelle evidenze esistenti.
README e mappa sono aggiornati. Nessun commit o push eseguito.

Il successivo intervento `mixed` modifica planner e orchestrazione chat,
generazione/validazione, metadati SQL/vettoriali, schema API e tipi frontend,
test e documentazione. Nessun nuovo motore o indice, colonna SQLite, pagina,
stato di compilazione o modifica ai componenti UI in questo intervento.
La correzione del bug MIXED aggiunge `backend/app/requirement_checks.py` e i
relativi test; modifica planner, orchestrazione, generazione e la costruzione
delle query FTS per sigle societarie puntate (`S.r.l.`/`S.p.A.`). Non modifica
nuovamente ingestion, parser DOCX, schema API, frontend o motore vettoriale.
Il precedente intervento sull'extractor DeepSeek modifica soltanto `intents.py`,
`requirement_checks.py`, `generation.py`, `main.py`, relativi test e documentazione;
aggiunge `test_requirement_extraction.py`. Non modifica i contratti API/frontend,
i filtri dei corpus, l'indicizzazione o il parser DOCX.
L'intervento SOURCE del 6 ottobre aggiunge `source_planning.py` e relativi test;
modifica `requirement_checks.py`, `main.py`, `generation.py`, test e documentazione.
`intents.py` non viene toccato ulteriormente. Nessuna reindicizzazione necessaria.
Branch e commit di base sono rimasti quelli indicati sopra; tutte le modifiche
locali precedenti, inclusa l'eliminazione di `.env.example`, sono state preservate.

**La correzione storica di chunking non modifica i frammenti già salvati.** Per applicarla alle fonti
esistenti serve riestrarre/suddividere gli originali e poi sincronizzare Qdrant.
Il solo aggiornamento dell'indice vettoriale riusa i frammenti SQLite e non
ripara le parole tagliate. Questa operazione sui dati non è stata eseguita;
anche le risposte storiche restano invariate. La correzione conserva le parole,
ma non garantisce che ogni frammento contenga frasi o sezioni complete.

## Verifiche già eseguite

| Momento | Esiti registrati |
|---|---|
| Audit iniziale, prima delle successive semplificazioni | 671 test backend, 61 frontend, 10 Playwright selezionati; lint e build superati. |
| Diagnosi Gemma e correzione dei frammenti, 5 ottobre | Dieci nuove regressioni fallivano prima della correzione; dopo, 207 test mirati e **646 test della suite backend completa** superati. Ruff e `git diff --check` superati. |
| Creazione AGENTS.md e STATUS.md | Verifica documentale di riferimenti, diff e stato Git; nessuna nuova esecuzione delle suite applicative. |
| Integrazione RAG dei moduli, 5 ottobre | 108 test backend mirati; suite backend completa **678 test** superati; suite frontend completa **62 test** superati. Ruff, Oxlint e TypeScript/build Vite superati. Guida CLI, riferimenti documentali e `git diff --check` verificati. |
| Confronto RAG mixed e provenienza KB, 5 ottobre | **178 test backend mirati** superati; suite backend completa **715 test** superati; suite frontend completa **62 test** superati. Ruff, Oxlint e TypeScript/build Vite superati; `git diff --check` verificato. |
| Correzione bug MIXED reale, 5 ottobre | **217 test backend mirati** e **754 test backend completi** superati. Ruff e `git diff --check` superati. Riproduzione reale Gemma/BGE/Qdrant su copie temporanee: risposta completed, 4 FORM + 4 SOURCE; denominazione sostenuta da SOURCE, nominativo generico non verificato. Nessuna nuova esecuzione frontend o browser E2E in questo intervento. |
| Robustezza estrazione MIXED DeepSeek, 5 ottobre | **298 test backend mirati** e **798 test backend completi** superati. Ruff e `git diff --check` superati. Diagnosi e benchmark reale A–E con DeepSeek/Qdrant su copie temporanee, risultati e limiti sotto. Nessuna nuova esecuzione frontend o browser E2E: contratti e frontend invariati in questo intervento. |
| Associazione/copertura SOURCE MIXED, 6 ottobre | **329 test backend mirati**, **829 test backend completi** superati; Ruff e diff check superati. Benchmark reale DeepSeek A–D su copie temporanee, nuova conversazione per caso, dettagli sotto. Nessun frontend/E2E rieseguito: nessuna modifica ai contratti o alla UI. |

I conteggi appartengono a revisioni diverse: nel frattempo sono stati rimossi
test della compilazione a gruppi. Nella diagnosi precedente non erano cambiati
file frontend; nell'integrazione RAG è stata aggiunta l'etichetta delle evidenze.
Le prove RAG usano SQLite/FTS5 e Qdrant locale reali con planner/provider ed
embedding simulati, database e storage temporanei. Coprono il DOCX Catanzaro,
upload DOCX/TXT, isolamento, esclusione delle globali per form, esclusione dei
form per fatti aziendali, rilettura di risultati del ruolo sbagliato, rimozione,
reindicizzazione esplicita e rollback. I test software usano provider simulati,
non misurano l'accuratezza semantica di Gemma. La successiva riproduzione reale
del bug MIXED è descritta sotto; non modifica dati o indici originali dell'utente.
Gli E2E browser non sono stati rieseguiti in questi interventi RAG.
Sono coperti anche aggiornamento dei payload vettoriali precedenti, cambio di
ruolo durante la query e rifiuto di comandi di reindicizzazione con progetto
o backend incompatibile prima di modificare i frammenti.

Comandi eseguiti nell'ultimo intervento SOURCE MIXED, da `backend/`:

```bash
uv run --locked pytest -q tests/test_source_planning.py tests/test_requirement_extraction.py tests/test_requirement_checks.py tests/test_form_retrieval.py tests/test_generation.py tests/test_chat_flow.py tests/test_retrieval.py tests/test_vector_retrieval.py tests/test_model_parsing.py -x
uv run --locked pytest -q
uv run --locked ruff check .
```

Nel precedente intervento sul contratto di provenienza, da `frontend/`:
`npm test`, `npm run lint`, `npm run build`, con
`/home/montesano/tesi/.tools/node/bin` aggiunto al PATH del comando.
Le nuove regressioni coprono i casi A–G richiesti: solo form per il riassunto,
solo source per i fatti, partita IVA vuota/valore presente soltanto nel form,
requisito e valore con provenienze distinte, requisito senza dati supportati,
fonti progetto/globali con esclusione di altri progetti, entrambi i backend.
Coprono anche norme generali presenti in Company o General KB, contesti
incompleti, citazioni del ruolo sbagliato (incluse quelle nel testo), limiti e
deduplicazione delle query, metadati nello storico/vicini/rilettura e cambio di
categoria durante una query Qdrant. I provider Ollama/DeepSeek sono simulati:
queste prove non misurano la capacità del modello di comprendere o confrontare
requisiti reali. La correzione successiva copre anche i sei casi del bug MIXED:
campo richiesto senza source, denominazione verificata da source, direttore
tecnico non verificato, query derivate dai requisiti, bucket 8 FORM/4 SOURCE
che mantengono 4 FORM/4 SOURCE nel contesto, compilabilità respinta se citata
soltanto dal form. Copre inoltre riparazione parziale delle prove, estratti
inventati, valori di altre persone e norme generiche. Nessuna reindicizzazione
dei dati utente o nuova esecuzione frontend/browser E2E in questa correzione.

## Lettura e indicizzazione dei moduli: implementate

Il ruolo è persistito su `project_files.kind`: i frammenti lo ereditano tramite
la relazione `file_id`, senza una nuova colonna duplicata o un nuovo indice.
SQLite conserva testo, progetto e file; FTS5 si aggiorna con i trigger esistenti.
Qdrant conserva anche ruolo, file, nome, progetto e metadati del documento nel
payload; l'hash include tali dati e aggiorna i vecchi payload alla sincronizzazione.

- `intents.ChatDecision` richiede `target`: source/form/mixed; `form_id` è opzionale.
  Il pianificatore riceve solo ID/nomi dei moduli del progetto, insieme alla
  cronologia non fattuale. Per form deve selezionare un ID effettivamente presente.
- `main.project_answer` valida tale ID e passa target/file a ricerca e vicini.
  Una ricerca form non può includere fonti globali o altri moduli. Un modulo
  assente, ambiguo o senza evidenze produce `no_evidence`, senza generazione
  documentale o ripiego sulle fonti aziendali.
- La ricerca source resta il default delle API di retrieval e non ammette form.
  Gli artefatti fattuali già consentiti restano utilizzabili come prima.
- Un target mixed esegue le ricerche separate descritte nella sezione successiva;
  non chiede più di separare le domande e non avvia una compilazione.
- Le evidenze API/storico includono `role`, `project_id`, `document_metadata`,
  `scope`, `category` (null dove non applicabile o nello storico precedente).
  I vecchi payload privi di ruolo sono compatibili e interpretati come source.
  Nella UI esistente si legge «Modulo» oppure «Fonte».
- Il prompt distingue contenuto/istruzioni del modulo da fatti documentati e
  spiega che una dichiarazione prestampata non prova il possesso di un requisito.
  I filtri del backend, non soltanto il prompt, impongono la separazione.

L'endpoint `/api/projects/{id}/evidence` ammette `target=form&form_id=...` per
la ricerca esplicita; senza target continua a cercare nelle sole fonti fattuali.
Il parser strutturale/candidate DOCX e il motore di compilazione non sono cambiati.
I vettori dei file eliminati vengono rimossi dalla riconciliazione prima della
successiva ricerca/indicizzazione, come per le fonti esistenti; SQLite, FTS e
storage vengono ripuliti all'eliminazione.

### Diagnosi del bug MIXED reale e correzione

Il turno 85, conversazione `conv-5d516e3726e74579`, progetto `prova`, del
5 ottobre alle 13:11:46 UTC contiene la risposta segnalata dall'utente:
«è possibile compilare» con otto evidenze del solo file 155,
`domanda-partecipazione.docx`, tutte `role=form`. La prima, frammento 13880,
descrive i campi richiesti dalla sezione 5.d; non attesta alcun valore aziendale.
Il modulo ha 22 frammenti. Non ci sono file source caricati nel progetto;
restano consentiti gli artefatti fattuali già previsti e le KB globali.

Intent, query e risposta grezza del planner non sono salvati nello storico:
non è possibile dichiarare quale JSON abbia prodotto esattamente il turno 85.
È stata quindi ripetuta la richiesta con Gemma, medesima cronologia e profilo,
su copie temporanee di SQLite/Qdrant; il database originale è stato letto in
sola lettura. **Il planner ha assegnato `target=form`, non mixed**, con query:

1. `requisiti del direttore tecnico nel modulo domanda di partecipazione`
2. `dati richiesti per la compilazione della domanda di partecipazione`
3. `informazioni necessarie per compilare la domanda di partecipazione`

| Fase della riproduzione prima della correzione | FORM | SOURCE |
|---|---:|---:|
| Candidati Qdrant prima del top-k, per ciascuna delle tre query | 22 | 0 |
| Dopo top-k, per query | 4 | 0 |
| Dopo merge | 4 | 0 |
| Dopo espansione, contesto finale | 8 | 0 |

La ricerca SOURCE non è stata eseguita: query SOURCE `[]`, contesto SOURCE
vuoto. Non era un top-k globale che eliminava fonti già recuperate. L'assenza
del contesto fattuale nasceva dal routing. Il validatore FORM controllava
soltanto l'esistenza di `[1]`: quella citazione esisteva, quindi la frase passava.
Anche il precedente contratto libero `MixedAnswer` permetteva la stessa frase
in `requirements` con una citazione form: il modello decideva l'etichetta della
propria affermazione, eludendo il controllo di ruolo. Infine, le query SOURCE
anticipate dal planner non derivavano dal contenuto appena letto del modulo.

Il [report prima della correzione](/tmp/mapi-mixed-diagnosis-before.json) contiene
query, conteggi, contesti FORM/SOURCE e prompt ricostruiti/riprodotti; il
[report dopo la correzione](/tmp/mapi-mixed-diagnosis-corrected.json) contiene
la successiva prova reale. Sono file temporanei esterni al repository e possono
non esistere in una sessione futura; i riscontri essenziali sono riportati qui.

Comportamento corrente:

- `ChatDecision` mantiene source/form/mixed. Il controllo backend riconosce
  richieste esplicite italiane di disponibilità/compilabilità e impone retrieve
  + mixed anche se Gemma propone form. Un answer anticipato insieme a retrieve
  viene scartato in questo caso; query, target e ID restano validati.
- Mixed esegue prima le query FORM. Una chiamata allo stesso provider ricava
  i requisiti con nome, eventuale ruolo personale, estratto e citazione FORM
  verificati dal backend. Il limite corrente è 32 proposte e 16 requisiti
  selezionati dopo controllo e deduplicazione per campo/ruolo personale, usando
  soltanto la prima occorrenza già valida. Non si analizzano candidate/celle DOCX.
- Il backend raggruppa i requisiti con una pianificazione SOURCE in batch,
  poi costruisce al massimo dodici query dalle etichette validate, una/due per
  gruppo, senza usare la domanda generica o le `source_queries` anticipate dal planner. Per la
  denominazione aggiunge «ragione sociale» e forme societarie; FTS5 mantiene
  le sigle puntate come frasi, per trovare anche un nome aziendale senza etichetta.
- Il retriever esistente conserva filtri per ruolo, progetto e modulo. Mixed
  usa due bucket: FORM massimo due frammenti principali/quattro con vicini;
  SOURCE massimo quattro evidenze per ciascuno dei sei gruppi, deduplicate
  nell'elenco finale (massimo 24 SOURCE + 4 FORM). Nessun ranking globale può
  cancellare un gruppo. Per altri target resta quattro principali/otto totali.
- I contesti `REQUISITI DEL MODULO (role=form)` e `FONTI FATTUALI (role=source)`
  restano separati fino alla generazione. Le citazioni hanno numerazione unica;
  l'elenco API concatena i bucket conservando ruolo e provenienza di ogni elemento.
- Il modello propone soltanto supporti con `requirement_id`, `source_citation_id`,
  `source_quote`, `value`. Il backend richiede ruolo SOURCE, ID valido, estratto
  presente nella fonte, valore letterale nell'estratto e associazione testuale
  al requisito. Un nome personale generico richiede lo stesso ruolo personale
  nei due estratti. Moduli, campi vuoti e norme generiche non bastano.
- Dopo un tentativo di correzione, supporti ancora invalidi vengono scartati;
  supporti validi rimangono e gli altri requisiti sono non verificati. Proposte
  concorrenti per lo stesso requisito non vengono selezionate arbitrariamente.
  JSON inutilizzabili/troncati ed errori del provider restano errori espliciti.
- La risposta è composta dal backend: requisiti del modulo, informazioni
  verificate nelle fonti, informazioni non ancora verificate. Solo un supporto
  SOURCE valido autorizza «utilizzabile per una prima compilazione». Zero SOURCE
  produce direttamente la risposta prudente, senza chiamata finale all'LLM;
  zero supporti validi produce la stessa conclusione anche con source recuperate.
  Se manca il form termina con `no_evidence`, senza sostituirlo con dati aziendali.
- La mappa requisito/citazioni SOURCE ammesse è interna al turno: un requisito
  escluso dal budget non può risultare verificato né confondersi con un requisito
  cercato senza prove. Il renderer aggiunge «Requisiti non ricercati» se necessario.
- Anche una generazione FORM_ONLY viene respinta/riparata se contiene una frase
  positiva di disponibilità riconoscibile dal controllo backend. Non esiste
  stato persistente per campo, collegamento a candidate o compilazione avviata.

Provenienza conservata dall'intervento precedente:

- `project_files.kind` continua a rappresentare il ruolo; `global_documents.category`
  distingue company/general. Lo scope reale è `project:ID` oppure `global`.
  Entrambe le KB globali restano condivise fra progetti e ammesse nelle ricerche
  source; i vecchi collegamenti globali per progetto sono compatibilità e non
  filtrano tale accesso. Gli artefatti fattuali già ammessi restano fonti;
  template e bozze restano esclusi. `get_company_context()` seleziona soltanto
  company per la generazione Markdown e non è cambiato. Nessuna categoria prova
  da sola che un documento contenga valori dell'operatore.
- Scope e categoria restano disponibili attraverso SQL, Qdrant, LangChain,
  rilettura, vicini, API e storico. La categoria entra nell'hash dei vettori;
  payload precedenti si aggiornano nella stessa collezione alla sincronizzazione.
  Nessuna nuova migrazione o riestrazione dei moduli già indicizzati necessaria.

La riproduzione reale finale Gemma/BGE/Qdrant ha recuperato 22 FORM candidati,
due principali e quattro con vicini. Gemma ha individuato solo «Denominazione
sociale» e «Nome e cognome» distinti. Le query SOURCE sono quindi diventate:

1. `Denominazione sociale ragione sociale S.r.l. S.p.A. dati effettivi operatore economico`
2. `Nome e cognome dati effettivi operatore economico`

Ogni query SOURCE ha avuto 18 candidati, quattro selezionati; il merge ha
mantenuto quattro SOURCE. Il contesto finale/API contiene **4 FORM + 4 SOURCE**.
Dopo la riparazione Gemma ha citato correttamente la denominazione nella fonte
Company KB `generalita-mapi.md`; il supporto del nominativo citava ancora un FORM
ed è stato scartato. Risultato `completed`: «Mapi Ingegneria S.r.l.» verificata
con citazione SOURCE, nominativo non verificato. La prova non verifica tutti
i requisiti del documento, né è una misura generale della qualità di Gemma.

### Diagnosi DeepSeek: estrazione dei requisiti

Diagnosi effettuata prima delle modifiche, leggendo il database originale in
sola lettura e usando copie temporanee di SQLite, storage e Qdrant per le
chiamate reali. Nessun turno, frammento o indice dell'utente è stato aggiornato.
Nella conversazione `conv-23db5c9659114269`, progetto `prova`:

| Caso storico | Esito | FORM del file 155, nell'ordine del contesto | SOURCE finali |
|---|---|---|---|
| FAIL, turno 94: «Con i documenti disponibili, quali dati della sezione società di ingegneria possiamo già compilare?» | Nessun requisito accettato; disponibilità non valutata | 13880, 13881, 13879, 13882 | Nessuna |
| SUCCESS, turno 95: «Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti?» | Otto requisiti; denominazione, forma giuridica e sede verificate | 13879, 13881, 13878, 13880 | -43, -45, -30, -50 |

I due contesti condividono tre frammenti: entrambi contengono i dati pertinenti
della sezione 5.d. SUCCESS inizia però dalla 5.c e contiene campi personali
generici. Query, prompt e risposte grezze dei turni storici non erano persistiti:
non è possibile attribuire loro retroattivamente un JSON esatto del modello.

La riproduzione con DeepSeek e la cronologia precedente di ciascun turno ha
assegnato **MIXED a entrambi**, recuperando gli stessi elenchi FORM storici.
Le query FORM riprodotte erano:

| SUCCESS | FAIL |
|---|---|
| dati richiesti dal modulo domanda di partecipazione: denominazione sociale, iscrizione CCIAA, forma giuridica, sede legale | sezione 5.d società di ingegneria dati richiesti denominazione sociale iscrizione CCIAA forma giuridica sede legale |
| requisiti del direttore tecnico richiesti dal modulo: nome, qualifica professionale, data di abilitazione, ordine professionale, numero iscrizione Albo | requisiti direttore tecnico art. 36 allegato II.12 D.lgs. 36/2023 nome qualifica data abilitazione ordine numero iscrizione albo |
| allegati richiesti dal modulo domanda di partecipazione: DGUE, contratto di avvalimento, organigramma aggiornato, procura | allegato organigramma aggiornato parte V allegato II.12 D.lgs. 36/2023 |

La divergenza concreta è nel **limite dello schema prima del grounding**:

1. L'extractor precedente riusava il prompt utente di generazione, incluso
   «ULTIMO MESSAGGIO DELL'UTENTE A CUI RISPONDERE». Il system prompt chiedeva
   1–8 requisiti e favoriva l'accorpamento dei dati personali per ruolo.
2. Il JSON richiesto conteneva `requirements`, elementi con `name`,
   `form_quote`, `form_citation_id`; la lista ammetteva da uno a otto elementi.
   Ollama riceveva lo schema nativo; DeepSeek solo `json_object`, senza schema
   completo nel messaggio. Il limite era scritto nel prompt, non imposto dal
   provider.
3. Nella riproduzione **entrambi i testi hanno prodotto dieci requisiti**,
   anche al secondo tentativo. Il JSON era leggibile ma Pydantic lo rifiutava
   con `too_long`: nessun requisito raggiungeva grounding o deduplicazione.
4. Verificati individualmente, tutti e dieci avevano ID ed estratti validi.
   Non erano whitespace, due punti o chunk sbagliati a causare questo stop.
   La normalizzazione precedente gestiva già case, Unicode e spazi; una
   citazione senza i due punti finali era già una sottostringa accettabile.
5. Esisteva già un retry, ma comunicava un rifiuto generico invitando a copiare
   gli estratti, senza segnalare i dieci elementi contro il massimo di otto.
   La seconda lista veniva rifiutata allo stesso modo, producendo il messaggio
   «non ha individuato requisiti con estratti verificabili» prima di SOURCE.

Il SUCCESS storico aveva otto requisiti e rientrava nel limite. La stessa frase
non garantiva però il successo: nella nuova riproduzione ne produceva dieci.
Non è dimostrabile quale errore preciso avesse il JSON storico del turno 94;
è invece stato riprodotto il blocco strutturale con entrambe le formulazioni.
I dump completi di prompt/schema/risposte erano temporanei in `/tmp`; dopo il
riavvio del server non sono più disponibili. I riscontri essenziali e i conteggi
osservati sono conservati qui, senza presentare la riproduzione come storico.

Soluzione implementata:

- Prompt documentale dedicato: la domanda delimita sezione/soggetto/requisito,
  non decide quali valori siano disponibili. Lo schema completo è incluso nel
  messaggio anche per i provider con solo JSON mode. Nessuna nuova lista di
  frasi per riconoscere «possiamo compilare» o campo specifico della sezione 5.d.
- Campo interno opzionale `person_role`: distingue, per esempio, nome,
  qualifica, ordine, numero e data dello stesso soggetto senza chiamare tutto
  «direttore tecnico». Nome del campo e ruolo devono comparire nello stesso
  estratto FORM; il ruolo entra nelle query e nella verifica SOURCE.
- Limite strutturale 32 proposte distinto dal budget 16 requisiti selezionati.
  Ogni proposta non duplicata deve superare il grounding; i requisiti validi
  sono poi deduplicati per campo/ruolo e selezionati in ordine. Non si accettano
  requisiti inventati per evitare un errore. Estratti FORM fino a 2.000 caratteri
  consentono di citare il contesto contiguo dal ruolo fino al singolo campo.
- Normalizzazione deterministica di spazi, case, Unicode, virgolette/apostrofi
  tipografici, trattini e due punti terminali; parole e ordine restano invariati.
  Confini di parola impediscono, per esempio, di confondere ISO 9001 e 90010.
  Nessun fuzzy matching, composizione di frasi distanti o ricerca in altro chunk.
- Un unico retry sulle stesse evidenze, sia per lista vuota sia per output
  invalido, con tutti gli errori di grounding o schema, senza il testo grezzo
  degli input negli errori Pydantic. Budget output 4.096 token, 8.192 soltanto
  se troncato: anche il troncamento consuma l'unico retry disponibile.
  Due liste vuote fermano il turno senza SOURCE e senza valutare disponibilità;
  output ancora invalidi conservano il fallimento esplicito e prudente.
- Gli errori specifici di associazione SOURCE arrivano anche all'unica
  riparazione della generazione. Le prove ancora invalide restano non verificate.
  «Non disponibile» non può diventare un valore verificato. Il rendering continua
  a essere composto dal backend a partire dai soli supporti SOURCE accettati.
- Log INFO per tentativo/errori, numero proposto/selezionato, numero di requisiti
  e tentativi usati. Non viene aggiunto un contratto API o uno stato persistente.

Le nuove regressioni software usano provider simulati: sette formulazioni
equivalenti con lo stesso FORM, schema DeepSeek/Ollama, 11 dati della sezione
5.d, limite separato 32/16, retry vuoto→valido e due tentativi invalidi, ID
inesistenti, estratti inventati, differenze tipografiche, ruoli personali
distinti, premessa ISO non sostenuta, verifica per requisito. FTS5 e Qdrant
sono esercitati con database temporanei e provider/embedding simulati; per
confrontare lo stesso contesto 5.d il testo viene estratto dal DOCX fixture.
Restano i test del DOCX completo e di isolamento/FORM_ONLY/SOURCE_ONLY.
Il test logico del direttore verifica separatamente nome, qualifica, ordine e
numero 8421, lasciando la data di abilitazione non verificata; non dimostra che
DeepSeek produca sempre le stesse prove valide.

### Benchmark DeepSeek e verifica manuale da ripetere

Ultima prova reale su copie temporanee del progetto `prova`, profilo DeepSeek
`deepseek-flash`, Qdrant/BGE, **conversazione nuova per ogni domanda**. Questi
sono conteggi osservati, non attese invarianti di un modello stocastico e non
un confronto a parità di cronologia con i turni 94/95. Nessuna verifica browser
eseguita in questo intervento.

| Caso | Domanda |
|---|---|
| A | Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti? |
| B | Con i documenti disponibili, quali dati della sezione società di ingegneria possiamo già compilare? |
| C | Il modulo richiede i dati del direttore tecnico. Con le fonti disponibili abbiamo tutto ciò che serve per compilare quella parte? |
| D | Possiamo completare oggi la domanda senza chiedere nulla all'utente? Spiega cosa è verificato e cosa manca. |
| E | Il modulo richiede la ISO 9001: Mapi la possiede? |

| Caso | Intent | FORM | Requisiti validati/selezionati | Query SOURCE | SOURCE | Verificati | Non verificati | Retry extraction |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | MIXED | 4 | 16 | 3 | 4 | 0 | 16 | Sì |
| B | MIXED | 4 | 11 | 3 | 4 | 6 | 5 | Sì |
| C | MIXED | 4 | 6 | 3 | 4 | 3 | 3 | No |
| D | MIXED | 4 | 16 | 3 | 4 | 0 | 16 | Sì |
| E | MIXED | 4 | 0 | 0 | 0 | 0 | — | Sì |

A–D terminano `completed`, che non significa copertura completa. In B sono
verificati denominazione, forma giuridica, sede legale, nome del direttore,
qualifica e ordine. Rimangono non verificati CCIAA, numero/data di iscrizione,
data di abilitazione, numero albo e organigramma. In C sono verificati nome
Elisa Romano, qualifica Ingegnere e Ordine degli Ingegneri di Bari; data di
abilitazione, numero albo e organigramma rimangono non verificati.

**Il numero albo 8421 è un falso negativo residuo della prova reale**, non un
dato assente dalla KB: l'estratto SOURCE proposto non supera l'associazione
testuale al campo. Non è stato indebolito il gate per far passare il benchmark.
Le domande ampie A/D recuperano anche condizioni e sezioni differenti: zero
valori verificati non significa KB vuota e non prova che il modulo sia
incompilabile. La copertura richiede ancora valutazione mirata.

In E il primo elenco è vuoto, il retry tenta di sostenere ISO con un estratto
non pertinente e viene rifiutato: esito prudente `failed`, disponibilità non
valutata, nessuna query SOURCE anche se nelle KB esistono riferimenti ISO.
La premessa utente non è stata trasformata in requisito. Il numero di requisiti
non verificati è «—» perché manca un requisito FORM accettato da confrontare.

Per ripetere manualmente:

1. Riavviare il backend con il codice aggiornato, scegliere DeepSeek nel
   progetto con `domanda-partecipazione.docx` già indicizzato e le KB demo.
   Questa modifica non richiede reindicizzazione né aggiornamento dei dati.
2. Aprire una nuova conversazione per ciascuna domanda A–E e inviarla testualmente.
   Per riprodurre una conversazione storica, invece, mantenerne anche il contesto:
   i risultati possono cambiare con la cronologia.
3. Controllare le sezioni requisiti/verificati/non verificati e le etichette
   Modulo/Fonte. Nell'API `POST /api/projects/{id}/answer`, `evidence` conserva
   role, scope, category, file/progetto/chunk. I valori verificati devono citare
   SOURCE; un requisito presente solo nel FORM deve restare non verificato.
4. Per contare query e retry leggere i log INFO `Chat search`, `Chat bucket`,
   `Chat requirements` e `Requirement extraction` (per E guardare i tentativi,
   perché il piano non viene restituito). Query SOURCE solo dopo requisiti validi.
   Non ci sono nuovi pannelli di diagnostica nella UI.
5. In C controllare ogni dato separatamente; non accettare «direttore tecnico
   compilabile» in blocco. In E deve essere esplicita l'assenza di un requisito
   FORM verificato, senza dedurlo dalla domanda o da una certificazione SOURCE.

### SOURCE MIXED: diagnosi e correzione del 6 ottobre

Diagnosi completa, query, requisiti, budget e tabella del benchmark sono in
[docs/diagnosi-source-mixed.md](docs/diagnosi-source-mixed.md).

Prima della modifica, C proponeva già `requirement_id=5`, citazione SOURCE 6,
valore `8421`, preso dal chunk -45 di `generalita-mapi.md`. Anche il chunk -32
della visura era nel contesto. Il validatore rifiutava il supporto soltanto
perché la label FORM conteneva «albo» e la fonte «iscrizione professionale»:
JSON, ruolo, citazione, valore e soggetto erano corretti. Il retry eliminava il
supporto. Ora si controlla la relazione locale iscrizione/numero, con il ruolo
personale: non occorre ripetere ogni parola della label FORM. Numeri estranei
e prove di altri requisiti/gruppi sono respinti.

Nella diagnosi D aveva 15 requisiti riuniti per posizione in tre query
(`1/4/7/10/13`, `2/5/8/11/14`, `3/6/9/12/15`), poi ridotti a quattro SOURCE
globali. Ora `source_planning.py` raggruppa gli ID in una sola chiamata AI
(saltata per uno/due requisiti), senza categorie specifiche di questo DOCX.
Massimo sei gruppi di quattro requisiti, due query con una/due label per gruppo,
due ancore per query e quattro evidenze per gruppo, deduplicate globalmente.
Limite complessivo: **12 ricerche, 24 SOURCE + 4 FORM**. Nessun nuovo indice,
motore o modifica dei filtri. Il timeout totale resta quello precedente.

Le proposte coerenti troppo grandi vengono suddivise. Se il raggruppamento
fallisce, il fallback limitato usa ruoli personali/singoli campi e indica gli
esclusi dal budget. La mappa interna requisito/citazioni distingue ricercato
senza supporto da non ricercato; il renderer espone quest'ultimo caso nel testo
esistente, senza contratto API o UI nuovi. Nessuna SOURCE di un altro gruppo
può verificare il requisito. Il matcher ha un compito SOURCE stabile e conserva
l'unico tentativo di riparazione. Non usa domanda/storico come prove.

Sono state aggiunte regressioni per 8421 e numeri estranei nello stesso record,
campi diversi della stessa persona, 16 requisiti in 16 documenti, copertura
ed esclusioni esplicite, gruppi troppo grandi/invalidi e prompt SOURCE stabile.
Test software con provider simulati e FTS5/Qdrant reali in ambiente temporaneo:
**329 mirati**, **829 suite completa**; Ruff e diff check superati. Durante la
prova reale è stata inoltre corretta un'incompatibilità JSON mode del nuovo
prompt (DeepSeek richiede esplicitamente la parola JSON), con regressione.

Ultimo benchmark DeepSeek `deepseek-flash` con Qdrant/BGE, conversazioni nuove
su copie temporanee: tutti i turni sono MIXED, con quattro evidenze FORM.
Le domande A–D sono riportate integralmente nel report collegato sopra.

| Caso | Requisiti | Gruppi SOURCE | Query SOURCE | Coperti | SOURCE | Verificati | Non verificati | Non ricercati | Retry extractor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A: dati non verificati | 10 | 4 | 8 | 10 | 10 | 0 | 10 | 0 | Sì |
| B: società di ingegneria | 11 | 5 | 7 | 11 | 11 | 7 | 4 | 0 | Sì |
| C: direttore tecnico | 6 | 3 | 4 | 6 | 8 | 4 | 2 | 0 | No |
| D: completamento oggi | 16 | 5 | 10 | 16 | 8 | 0 | 16 | 0 | Sì |

C verifica nome, qualifica, ordine e **numero albo 8421**; data di abilitazione
e organigramma restano non verificati. B aggiunge denominazione, forma giuridica
e sede. A rimane un falso negativo della proposta del matcher: il contesto
ammesso dei requisiti codice fiscale/partita IVA include -43 e -30, ma DeepSeek
restituisce `supports: []`. Nessuna prova viene scartata dal validatore in A:
il modello non ne propone. D seleziona prevalentemente dichiarazioni, alternative
di partecipazione e procedure concorsuali, non l'anagrafica aziendale. Zero
verificati non dimostra che la KB sia priva di dati. In alcune prove intermedie
l'extractor invariato ha fermato A/D prima di SOURCE; la tabella registra
l'ultima esecuzione completa, non una garanzia per ogni risposta del modello.

Report diagnostici persistiti, senza modificare documenti/SQLite/Qdrant originali:
[traccia finale](backend/data/chat-audit/source-mixed-2026-10-06/deepseek-final.json),
[riepilogo](backend/data/chat-audit/source-mixed-2026-10-06/summary.json),
[test mirati](backend/data/chat-audit/source-mixed-2026-10-06/targeted.log),
[suite completa](backend/data/chat-audit/source-mixed-2026-10-06/backend-full.log).
Sono esclusi da Git e possono mancare in un altro checkout; non contengono
credenziali. I dump iniziali in `/tmp` sono andati persi al riavvio, i riscontri
essenziali sono conservati nel report Markdown. Nessuna reindicizzazione o
migrazione richiesta. Nessun frontend/E2E rieseguito in questo intervento.

Prossimo punto circoscritto: valutare il matcher usando la traccia A a parità
di requisiti/fonti, senza cambiare l'extractor o ampliare il retrieval alla cieca.
Non dichiarare congelato l'intero RAG per la CompilationSession in base ai soli
test software. Il workflow di compilazione rimane da discutere con l'utente.

### Verifica manuale di base FORM/SOURCE/MIXED

1. Avviare/riavviare `./start.sh` per caricare il codice aggiornato e scegliere
   Gemma nel progetto, con il servizio/modello configurati.
2. Creare un progetto di prova con il solo modulo
   `domanda-partecipazione.docx`, caricato in «Moduli da compilare». Se si riusa
   un vecchio modulo con zero frammenti, reindicizzarlo esplicitamente come sotto.
   Le KB globali sono condivise: un progetto nuovo non rende vuote tali KB.
3. Nella stessa conversazione inviare le tre domande, nell'ordine seguente.
   Per conoscere la KB esatta aprire gli strumenti sviluppatore del browser,
   scheda Network, risposta `POST /api/projects/{id}/answer`, array `evidence`.
   La UI mostra già Modulo/Fonte e nome; i campi scope/category sono nell'API.

| Domanda | Retrieval atteso | Evidenze e comportamento da controllare |
|---|---|---|
| «riassumi la domanda di partecipazione» | FORM (`target=form`) | Solo `role=form`, `file_id` del modulo, `project_id` del progetto, `scope=project:ID`, category null. Il testo descrive sezioni, dichiarazioni e allegati del modulo; nessuna evidenza globale lo sostituisce. |
| «qual è la partita IVA di Mapi?» | SOURCE (`target=source`) | Solo `role=source`: fonti del progetto o globali, scope e categoria reali. Un valore deve essere sostenuto dal testo della fonte, non dal form. Se non ci sono riscontri, deve indicarlo senza inventare il numero. |
| «con i documenti che ho posso iniziare a compilarlo?» | MIXED (`target=mixed`) | FORM per requisiti, poi SOURCE cercate con query derivate dai requisiti. Se si trovano fonti pertinenti, vedere entrambe le etichette Modulo/Fonte e controllare che i valori verifichino una Fonte. Tre sezioni: requisiti, informazioni verificate nelle fonti, informazioni non ancora verificate. Zero riscontri validi deve impedire ogni affermazione di compilabilità. Non genera/modifica DOCX. |

Per una prova controllata aggiungere in Company KB una fonte di test che documenti
denominazione e partita IVA di Mapi, poi ripetere la seconda e la terza domanda:
le citazioni dei valori devono rimandare a quella fonte, con `scope=global` e
`category=company`. Ripetere con FTS5 e Qdrant nelle impostazioni del retrieval;
per Qdrant servono il modello di embedding e il servizio configurati. Per il
confronto parziale usare un modulo con denominazione sociale e direttore tecnico,
e una fonte con solo la denominazione: questa può risultare verificata, il
direttore deve restare non verificato se nessun'altra fonte ammessa lo documenta.
Le KB globali restano condivise e possono già contenere altri riscontri.
La terza richiesta è stata riprodotta con Gemma su copie temporanee come sopra;
le tre richieste dalla UI e la verifica reale FTS5 restano da eseguire dall'utente.

### Reindicizzazione dei moduli già caricati

Nessun backfill automatico. Da `backend/`:

```bash
uv run --locked python -m scripts.reindex_project_forms --project ID_PROGETTO
# Per un solo modulo:
uv run --locked python -m scripts.reindex_project_forms --project ID_PROGETTO --form-id ID_MODULO
```

La transazione per ciascun modulo sostituisce i suoi frammenti e aggiorna il
conteggio, mantenendo identità e byte dell'originale. FTS5 è subito aggiornato.
Qdrant riconcilia i dati alla ricerca successiva; `--sync-vectors` lo fa subito
se configurato. Aggiornare soltanto Qdrant non estrae il testo dei vecchi moduli.
Il comando non è stato eseguito sul progetto locale `prova` o su altri dati utente.

### Limiti rimasti

- La selezione linguistica del modulo e la classificazione generale restano
  affidate al modello; il controllo di disponibilità copre espressioni italiane
  esplicite, non ogni parafrasi. Più moduli senza selezione attendibile producono
  informazione insufficiente. Non garantisce ogni interpretazione della domanda.
- Otto evidenze non garantiscono un riassunto esaustivo del documento. FTS5
  resta lessicale, Qdrant semantico: la selezione dei frammenti può differire,
  mentre le regole di accesso ai due ruoli sono equivalenti.
- Vengono indicizzati testo del corpo DOCX e tabelle (anche controlli testuali),
  non OCR, intestazioni, piè di pagina o note esterne al corpo. Un DOCX senza
  testo resta archiviabile, con stato «Senza testo estraibile» e zero frammenti.
- L'esattezza semantica delle risposte/citazioni richiede valutazioni reali;
  una risposta form può comunque essere interpretata male dal modello.
- Per mixed il controllo di ruolo, estratti letterali, valori e associazione
  testuale impedisce l'uso del form come prova di disponibilità, ma non è una
  dimostrazione completa di pertinenza semantica o appartenenza al soggetto.
  Può lasciare non verificati dati presenti altrove o con formulazioni diverse.
  Nessuna etichetta company/general prova da sola che il dato sia fattuale.
- L'estrazione seleziona al massimo 16 requisiti nei quattro frammenti FORM
  recuperati, da un output limitato a 32 proposte;
  può omettere requisiti o scegliere campi generici di sezioni diverse, come
  nella prova reale. Il confronto non è un audit completo dell'archivio e non
  risolve, certifica o rende persistente lo stato di tutti i campi del modulo.
- Il controllo SOURCE resta testuale e conservativo. Il numero albo 8421 è
  verificato dopo la correzione del 6 ottobre; rimangono falsi negativi del
  matcher, come codice fiscale/partita IVA nel caso A pur presenti nel contesto.
  Le domande ampie
  possono selezionare condizioni non applicabili, senza un'analisi completa
  dell'operatore e delle alternative previste nel modulo. La copertura SOURCE
  è ora esplicita, ma non dimostra da sola la completezza delle proposte del modello.

## Proposta da discutere: collegamento delle sessioni alla chat

La V1 backend descritta all'inizio implementa già sessione, aggiornamenti e
rigenerazione. Rimane da discutere il collegamento alla chat, per un DOCX:

1. Selezionare il modulo archiviato dal compositore, con pulsante o `@`.
2. Analizzare struttura e campi; cercare le informazioni nelle fonti appropriate.
3. Presentare una prima proposta con dati supportati, mancanti e ambigui.
4. Chiedere chiarimenti mirati e registrare le risposte/correzioni dell'utente.
5. Aggiornare e validare lo stato; rigenerare ogni versione dall'originale.
6. Mostrare nella chat una scheda persistente con stato, problemi, versione,
   download della bozza e report.

L'iterazione comprende proposta, verifica, ricerca/chiarimento e aggiornamento,
con limiti e condizioni di arresto. Ripetere chiamate al modello o dividere i
campi in gruppi, da soli, non realizza questo percorso.

Da chiarire nella discussione: come selezionare il modulo/sessione e mostrare
i problemi e i chiarimenti nella chat. L'iterazione backend e i suoi limiti sono
già stati richiesti esplicitamente e implementati, non vanno riprogettati da zero.
La lettura RAG e il confronto informativo sono disponibili; le prove reali
storiche hanno evidenziato falsi negativi conservativi. Evitare di chiedere
nuovamente all'utente l'intera storia o di trattare queste proposte come decisioni
già approvate.
