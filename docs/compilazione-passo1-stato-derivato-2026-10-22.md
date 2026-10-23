# Passo 1 — promozione della coerenza dello stato derivato

## Mandato e perimetro

Il 22 ottobre 2026 l'utente ha autorizzato di procedere per passi dopo la revisione
della candidata a sezioni. Questo primo passo promuove separatamente la correzione
HTTP 409 già implementata da Opus. Le sezioni e il dialogo P3 restano sperimentali.
Nessuna nuova inferenza reale, campagna E2E, migrazione delle sessioni, commit o push.

Le modifiche già presenti nel working tree vengono conservate. La baseline V12 e
i risultati delle campagne precedenti rimangono intatti.

## Piano e criteri, registrati prima delle modifiche applicative

1. Conservare una copia verificata dei file interessati in
   `backend/data/compilation-audit/stato-derivato-passo1-20261022-01/before/`.
2. In `compilation_global_sessions.initial_state`, assegnare alle sole nuove
   sessioni `derivation_revision=1` per impostazione predefinita. Conservare
   `MAPI_DERIVATION_REVISION=0` come selezione esplicita del profilo precedente.
3. Non modificare la logica già implementata in `apply_replies`: il ricalcolo
   dopo ogni mutazione accettata resta condizionato al flag persistito.
4. Aggiornare i test del profilo predefinito e verificare che un cambio delle
   impostazioni del processo non aggiorni implicitamente le sessioni salvate.
5. Eseguire dapprima i test mirati e poi la suite backend e Ruff, usando provider
   simulati e storage temporaneo; conservare i log in `out/` nell'audit.
6. Aggiornare STATUS.md, relazioni.md e questo rapporto con i risultati effettivi.

Criteri di accettazione:

- senza il flag persistito il controesempio del rinvio riproduce ancora il 409;
- con il flag l'audit salvato coincide con quello ricalcolato, il riuso revocato
  scompare e l'export parziale riesce senza includere quei valori;
- conferma, rinvio, revoca, cambio di risposta e slot diverso restano distinti;
- le nuove sessioni ordinarie hanno V14 + K3 + derivation_revision 1, senza
  attivare dialogue_revision o generation_revision;
- sessioni preesistenti con e senza flag mantengono il proprio comportamento;
- i controlli negativi SOURCE/USER, V14/K3 e il veto finale restano operativi.

Budget di verifica: zero chiamate LLM esterne, zero retry di inferenza. Il replay
storico di minervino-1 già registrato è evidenza precedente; non verrà presentato
come appena rieseguito. I test correnti usano il controesempio deterministico con
provider simulato e non misurano la qualità delle risposte del modello.

## Limiti e passi successivi

La promozione corregge la coerenza dello stato, non la classificazione errata di
una scelta del firmatario come rinvio. Le vecchie sessioni non sono migrate e
possono ancora manifestare il difetto.

Gli interventi successivi riguardano contesto FORM delle sezioni, ambito delle
decisioni USER e recupero degli errori del narratore. Richiedono disegno e
verifiche distinti e non sono inclusi in questa promozione.

## Risultati

- **Profilo delle nuove sessioni:** V14 + K3 + `derivation_revision=1`.
  `dialogue_revision` e `generation_revision` restano assenti per impostazione
  predefinita. `MAPI_DERIVATION_REVISION=0` ricrea il profilo precedente solo
  per le nuove sessioni; non cambia quelle già salvate.
- **Prima della modifica:** 39 test mirati PASS.
- **Dopo la promozione:** 72 test mirati PASS, inclusi consenso V14 e K3.
- **Dopo la correzione della fixture descritta sotto:** 76 test del dialogo e
  della derivazione PASS.
- **Suite backend finale:** 3.564 PASS in 309,90 secondi. Ruff completo PASS.
- **Perimetro applicativo:** confronto AST senza differenze fuori da
  `initial_state`; `compilation_global_dialogue.py` identico byte per byte allo
  snapshot iniziale. Ricalcolo e veto finale di Opus non modificati.
- **Compatibilità persistente:** test FTS5/Qdrant per sessioni create con e senza
  flag, poi rilette e analizzate sotto il profilo opposto. Nessun aggiornamento
  implicito, nessuna attivazione del dialogo P3 o delle sezioni.
- **Nessuna migrazione/reindicizzazione.** Nessuna compilazione live creata per
  la verifica; nessun riavvio manuale del server. L'esito riguarda il codice e
  i test API con persistenza temporanea, non una nuova campagna sul modello.

I primi tentativi di test nel sandbox si sono bloccati sui worker AnyIO: anche
un programma minimo senza applicazione ha raggiunto il timeout. I controlli
sono stati quindi eseguiti fuori dal sandbox con autorizzazione e mantenendo
nel runner il blocco delle connessioni di rete, dotenv disabilitato e DB/storage
temporanei. Un precedente errore del duplicatore dell'output del runner è stato
corretto prima dell'esecuzione dei test. Tutti i log sono conservati.

Audit: `backend/data/compilation-audit/stato-derivato-passo1-20261022-01/`.
Backup separato da Git:
`backend/data/compilation-audit/stato-derivato-passo1-backup-20261022.tar.gz`,
con SHA-256 e verifica dei contenuti nel file `.verification.json` associato.

**Primo passo completato.** Il fix non aumenta la copertura dei dati né dimostra
la sicurezza della candidata a sezioni. Il prossimo punto è un disegno minimo
per conservare il FORM completo nelle chiamate dei segmenti e verificare
separatamente l'ambito delle decisioni USER; nessuna candidata a sezioni adottata.

## Addendum di verifica — fixture del dialogo

La prima suite completa dopo la promozione ha prodotto 3.562 PASS e 2 FAIL, le due
parametrizzazioni FTS5/Qdrant di
`test_partial_group_reply_updates_valid_slot_and_keeps_ambiguous_one_open`.
Il test modificava direttamente la disposition nell'audit persistito, lasciando
nella risposta MODEL originale due assegnazioni di valore. Il ricalcolo ripristina
correttamente quell'output immutabile, eliminando i chiarimenti inseriti solo
nello stato derivato del test.

La fixture viene corretta facendo restituire al provider simulato due vere
clarifications FORM; il test conserva le stesse asserzioni sulla risposta USER
parziale e sul campo ambiguo che deve restare aperto. Nessuna modifica aggiuntiva
al codice applicativo e nessun allentamento dei criteri.
