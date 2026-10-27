# Carica e checkbox societaria — revisione offline del 27 ottobre 2026

Base `0d62a11`: le tre correzioni precedenti sono conservate. Worktree
`tesi-ruolo-checkbox-20261027`, branch `fix/2026-10-27-ruolo-checkbox`.
Nessuna inferenza, modifica dell'app ordinaria, migrazione live, merge o push.
Gli artefatti nel vecchio percorso non erano più disponibili; verificati tutti
i 328 hash del backup `tesi-backups/diagnosi-conferme-docx-20261027-01`.
Il backup viene letto soltanto. Nuovi grezzi privati in
`backend/data/ruolo-checkbox-20261027-01/` del worktree sperimentale.

Piano congelato prima dei fix: `preregistrazione.md`, SHA-256
`48ffad8c1e7bb9b0d8b07ae3aa8bddeb6730f0787bc0b48c60b20adbd483e221`.
I test di produzione usano dati sintetici; la sessione e i suoi dati personali
non entrano in Git. La revisione è autoriale, non indipendente.

## A — cronologia della carica

La SOURCE nomina il soggetto scelto come amministratore unico e rappresentante
legale, con decorrenza **2 ottobre 2026**. La richiesta effettiva al narratore
contiene già `reference_date: 2026-10-27`. La risposta USER positiva sulla
rappresentanza è persistita e verificata; il nome ha la propria ricevuta USER.
Il FORM collega la carica al sottoscrittore e all'operatore economico.

Motivo esatto del modello:

> La carica di amministratore unico e rappresentante legale risulta attestata solo a partire dal 2 ottobre 2026, mentre il ruolo richiesto nel modulo è quello attuale del sottoscrittore.

Richiesta associata:

> Conferma che la carica sia effettivamente in essere alla data odierna e non solo nello scenario futuro.

Il salto erroneo passato→futuro è **nella risposta del modello**. Il backend
non aveva invertito le date: `_hold_updates` verificava che la citazione fosse
nel contesto, classificava la motivazione `RECORDED` e conservava il hold SOURCE.
`export_selection` escludeva poi p14.s0. Aggiungere soltanto la data al prompt
non avrebbe corretto il difetto, perché era già presente.

La modifica aggiunge `compilation_temporal_hold.comparison_proof`. Riconosce
soltanto una **motivazione temporale chiusa**, nella forma sopra riportata con
carica e data variabili, e la relativa richiesta che oppone data odierna e
scenario futuro. Ogni diversa formulazione o motivo misto resta sospeso.
Questo limite esplicito evita di classificare liberamente spiegazioni del modello.

La prova richiede il riuso nominativo già supportato, identità e operatore
coerenti, ricevuta USER valida, ambito FORM corrente, fonte positiva completa,
decorrenza aperta univoca e precedente/uguale alla data di riferimento.
Rilegge le SOURCE autorizzate per ulteriori asserzioni nominative e stati
contraddittori riconoscibili. Non è una verifica generale di tutti i modi di
descrivere una cessazione in linguaggio naturale. Qualificatori non interpretabili
nella dichiarazione di decorrenza impediscono questa prova.

Solo se tutte le verifiche passano, la motivazione è registrata come
`REJECTED_TEMPORAL_COMPARISON`, con date, citazione, ricevuta e impronta del corpus.
Il motivo originale rimane nell'audit. Nessuna ricevuta USER nuova.
`_selected` ricalcola la prova sulle SOURCE correnti: una liberatoria persistita
non è un permesso permanente. Se la prova cambia, export del ruolo respinto con 409.

Test prima: **1 FAIL, 12 PASS**. Positivo e negativi comprendono decorrenza
futura, cessazione, persona diversa, fonte contraddittoria, data mancante o
ambigua, data di riferimento assente, altro motivo/motivo misto, revoca USER,
FORM cambiato e SOURCE obsoleta. Aggiunti anche rivalidazione all'export,
hold precedente differente e intervallo chiuso: **16 test**.
Regressioni mirate complessive: **58 PASS**, Ruff PASS.

Rigioco reale A, trasporto di rete disabilitato: **57 scritture**. p14.s0 diventa
esportabile come dato SOURCE; la prova riporta `2026-10-02 <= 2026-10-27`.
Il nome resta USER, decisioni e rinvii immutati. Le checkbox restano non selezionate.
È una rivalidazione offline della motivazione conservata, non una nuova risposta LLM.

## Limite separato del dialogo

La domanda su una data di iscrizione attribuita al professionista sbagliato
rimane fuori perimetro. Non modificare i due vuoti coinvolti né reinterpretare
il rinvio per aumentare la copertura.
