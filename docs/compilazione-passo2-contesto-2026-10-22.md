# Passo 2 — FORM completo e ambito delle decisioni USER

## Preregistrazione prima delle modifiche applicative

Mandato: l'utente ha autorizzato il secondo passo dopo la promozione separata
del fix dello stato derivato. Nessuna adozione della generazione per sezioni,
nessuna inferenza reale, nessuna modifica ai risultati congelati. Il recupero
del narratore resta un passo successivo. Budget di verifica: zero token esterni.

Disegno minimo, candidato `generation_revision=3`:

1. Riutilizzare partizione, cache, retry limitati e validazione rev 2. In
   `compilation_segments.segment_input/resilient_instruction` mostrare tutti
   i blocchi FORM, mantenendo solo le destinazioni proprietarie nell'output.
   La cache deve includere anche i paragrafi lontani. Nessuna nuova euristica
   per nomi di fixture. Non unificare condizioni semanticamente diverse solo
   perché citano lo stesso paragrafo: rev 3 conserva solo dedupliche esatte.
2. Rafforzare il controllo semantico esistente delle risposte USER, senza
   aggiungere un pianificatore o una nuova chiamata. Il guard riceve FORM
   completo, destinazioni effettive e condizioni associate. Richiedere un esito
   distinto per l'ambito: una condizione con scope misto/non dimostrato resta
   irrisolta anche se la risposta è pertinente alla sua descrizione.
3. Conservare ricevute legate all'ambito verificato e alla risposta. Integrare
   registro iniziale, routing e `apply_replies`; all'export rivalidare il legame
   con campi e condizioni correnti. Nessun VALUE USER aggira da solo l'incertezza
   del FORM o un segmento fallito. Una catena indipendente verificata può invece
   giustificare il solo valore USER; il riuso SOURCE resta soggetto ai propri
   controlli e al segmento proprietario.

File applicativi previsti: `compilation_segments.py`,
`compilation_global_sessions.py`, `compilation_global_dialogue.py`,
`compilation_decision_registry.py`, `compilation_reply_guard.py`,
`compilation_chat.py`, `intents.py` e un piccolo modulo per il contesto e le
ricevute di ambito. Parser, writer, retrieval e contratto fattuale V12 invariati.

Invarianti: profilo ordinario invariato; flag persistiti autorevoli; rev 1/2
leggibili senza upgrade; grounding, V14/K3, veto all'export e originale immutato;
proposte estranee al proprietario escluse; errori semantici/strutturali del guard
non autorizzano; ricevute vecchie senza verifica di ambito non autorizzano rev 3.

Controprove offline: contesto lontano presente, cambio lontano invalida cache,
proposte fuori segmento, fallimento isolato/ripresa, condizioni opposte non
unificate, esito SUPPORTED senza verifica di ambito rifiutato, ambito misto
RT/operatore/ausiliaria non sbloccato da una sola scelta, ricevute alterate o
obsolete rifiutate, USER non aggira incertezza, ramo pertinente ancora compilabile,
compatibilità vecchi profili. Usare anche artefatti già registrati dove disponibili.
Eseguire test mirati, suite backend e Ruff; salvare anche i fallimenti.

Limiti dichiarati prima delle prove: il guard resta un modello fallibile; il
FORM completo non prova che ogni condizione venga riconosciuta. Una risposta
semanticamente errata ma conforme allo schema può ancora sfuggire. I test con
provider simulati provano il comportamento del software, non la scomparsa delle
25 scritture osservate. Input e latenza possono aumentare; nessuna nuova misura
di costo reale in questo passo. Non tentare di risolvere la copertura generale.

Snapshot verificato dei file preesistenti:
`backend/data/compilation-audit/contesto-sezioni-passo2-20261022-01/before/`.

## Implementazione del 22–23 ottobre

La candidata è selezionabile solo per nuove sessioni con
`MAPI_GENERATION_REVISION=3`. Non è stata attivata nell'app ordinaria. I flag
dialogo P3 e stato derivato mantengono le rispettive impostazioni; non ci sono
migrazioni implicite di sessioni. Il profilo ordinario resta quello del passo 1.

- `compilation_segments.segment_input`: ogni chiamata legge **tutti i blocchi
  del catalogo FORM**; il catalogo delle destinazioni e il piano locale restano
  limitati al proprietario. Non si dichiara recuperato ciò che il parser DOCX
  non rappresenta. La partizione per unità di dipendenza della rev 2 è riusata.
- `resilient_instruction` e `_resilient_proposal`: responsabilità esplicita;
  gruppi di scelta con opzioni esterne al segmento fanno fallire quel segmento.
  Proposte/clarifications/coverage estranee continuano a essere escluse dal
  merge. Retry, budget locali, cache e ripresa restano quelli della rev 2.
- `resilient_merge`: rev 3 conserva la deduplica esatta e disattiva l'unificazione
  ulteriore che ignorava differenze di significato nella reason e univa scope
  diversi. Compromesso: possono restare conferme ridondanti; non viene costruito
  un nuovo risolutore semantico delle condizioni.
- `compilation_reply_guard`: nella candidata lo schema richiede separatamente
  pertinenza della risposta e compatibilità del suo ambito con **tutte** le
  destinazioni effettive. Il medesimo controllo riceve FORM completo, condizioni
  associate e indicazioni USER pertinenti. Nessuna chiamata aggiuntiva: cambia
  il contenuto della chiamata di verifica esistente. Se manca il nuovo esito,
  è ambiguo o duplicato, la risposta non autorizza la scrittura.
- `compilation_scope_review`, registro iniziale, router e `apply_replies`:
  conservano una ricevuta interna legata alla risposta, alle destinazioni,
  al FORM e alle condizioni conosciute. Le impronte dimostrano corrispondenza
  e stabilità, **non verità semantica**. Il modello non produce queste impronte.
  Una conferma non si estende silenziosamente a nuove destinazioni. Cambiamenti
  alle condizioni pertinenti invalidano le ricevute dipendenti; una condizione
  diventata falsa prevale su una precedente conferma.
- `planner_context` / `export_selection`: quando la vista pubblica omette FORM
  e audit, il backend legge la stessa revisione persistita. Nessuna esposizione
  del FORM completo nella UI. `review_fields`, `_selected` e
  `checked_user_fields` applicano il controllo anche all'export e alla
  rivalidazione finale. Un dato USER da solo non aggira il fallimento del segmento;
  una ricevuta USER verificata indipendentemente può giustificare quel valore.
  Non autorizza il riuso SOURCE nel segmento fallito.

## Verifiche e loro limiti

Tutte le esecuzioni usano provider simulati, connessioni bloccate dal runner,
dotenv disabilitato e storage temporaneo. Nessuna inferenza reale o campagna E2E.
Il runner è in `backend/data/compilation-audit/contesto-sezioni-passo2-20261022-01/`;
log e misure sono nella sottocartella `out/`.

- Prima esecuzione mirata: 118 PASS, 3 FAIL. Due fallimenti erano una nuova
  fixture che forzava una domanda su un campo privo di proposta/form evidence;
  il caso positivo è stato ancorato a un campo realmente proposto. Il terzo
  indicava un ID errato nel test del reperto So.Re.Sa. (`p127.s0` invece di
  `p127.s1`). Nessuna modifica al reperto storico.
- Test del nuovo modulo dopo queste correzioni: 32 PASS.
- Percorso completo router–guard–ricevuta–export e guard precedente: 74 PASS.
- Prima suite completa: **3.603 PASS in 318,00 s**; Ruff PASS.
- Revisione finale: due ulteriori controesempi fallenti hanno dimostrato un
  prefisso di input non riutilizzabile per tutto il FORM e un veto mancante
  nella nuova verifica per una condizione divenuta falsa. Correzioni limitate
  alla rev 3; log prima della correzione conservato.
- **Suite finale: 3.605 PASS in 327,91 s; Ruff completo PASS.** L'interruzione
  della conversazione non ha fermato la suite finale: verificata la sua
  conclusione nel log, senza lanciarne una copia concorrente.

Le prove verificano: ciascun segmento fallito separatamente, conservazione
delle scritture indipendenti, ripresa senza ripetere segmenti validi, cache
invalida su input cambiato, proprietari, condizioni di diverso significato,
ricevute mancanti/obsolete, controllo diretto dell'export, consenso e negativi
precedenti attraverso la suite completa. Sono presenti sia accettazioni sia
rifiuti nel percorso USER. La condizione riconoscibile omessa da JSON valido
resta bloccata; il controesempio di una condizione non riconosciuta resta un
**limite esplicito e ancora riproducibile**.

Verificati in lettura i quattro input registrati di Minervino, Catanzaro,
Cesano e So.Re.Sa.: ogni segmento rev 3 contiene esattamente tutti i blocchi
FORM disponibili nel rispettivo input. Sullo stato registrato So.Re.Sa., una
simulazione in memoria verifica che la vecchia ricevuta `s2_c_sing`, che
comprendeva l'avvalimento, non soddisfi il nuovo contratto. Questo **non** è
una nuova inferenza sul suo significato, né una prova che il modello aggiornato
risponderà correttamente. La sessione storica non viene aggiornata.

## Costo e compromessi

Confronto statico degli input JSON, **caratteri serializzati, non token**:

| Input storico | Segmenti | Blocchi FORM per segmento rev 3 | Dimensione totale rev 3 / rev 2 |
|---|---:|---:|---:|
| Minervino-1 | 5 | 134 | 1,63× |
| Catanzaro-2 | 6 | 299 | 2,09× |
| Cesano-1 | 2 | 112 | 1,21× |
| So.Re.Sa.-1 | 2 | 166 | 1,47× |

La rev 3 ordina SOURCE e FORM condiviso prima delle destinazioni e del piano
specifici del segmento, così da rendere possibile il riuso del prefisso da parte
del provider. **Non sono stati misurati hit di cache, token, costo o latenza
reali.** Anche il guard riceve più contesto. Questa è una scelta conservativa
per recuperare informazioni perse, non un miglioramento di costo dimostrato.

Il digest di richiesta copre tutto il FORM, le SOURCE e gli input USER: a parità
di richiesta la ripresa conserva i risultati validi; modifiche agli input
possono richiedere di ripetere tutti i segmenti. Non è stata introdotta una
cache semantica capace di dimostrare che una modifica lontana è irrilevante.

## Giudizio

Passo implementativo mirato, senza riscrivere parser, writer, retrieval o
contratto fattuale V12. La candidata resta **non adottata e non dimostrata sul
modello reale**. Non si dichiarano risolte le 25 scritture della campagna rev 2,
né miglioramenti di copertura. Il guard può ancora sbagliare semanticamente;
formati/condizioni non riconosciuti restano un limite. Non viene equiparato
VERIFICATA a una prova completa dell'applicabilità di qualunque modulo.

Il prossimo passo distinto è il recupero limitato degli errori del narratore;
poi potrà essere valutata una piccola verifica reale preregistrata. Nessuna
campagna è stata avviata o autorizzata implicitamente da questi test offline.

Questa è una verifica autoriale delle modifiche di Codex, non una nuova revisione
indipendente. Backup del passo (copie prima/dopo, manifest, piano, log e patch):
`backend/data/compilation-audit/contesto-sezioni-passo2-backup-20261023.tar.gz`.
La verifica file per file e l'impronta dell'archivio sono nei sidecar
`.verification.json` e `.sha256`. Il backup non comprende DB live o runtime
con credenziali. Nessun commit, tag, push, migrazione o reindicizzazione.
