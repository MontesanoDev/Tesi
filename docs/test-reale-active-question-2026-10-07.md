# Chiarimento di applicabilità: diagnosi e prova reale — 7 ottobre 2026

Intervento circoscritto al destinatario delle risposte conversazionali su una domanda singola. Profilo reale **DeepSeek / deepseek-flash**, modulo archiviato ID **153**, progetto `minervino-di-lecce-elenco-sia`. Il registro conserva il nome della directory del 6 ottobre, quando è iniziata la diagnosi; il benchmark finale è del 7 ottobre, ora Europe/Rome.

## Prima della modifica: riproduzione effettiva

Letta senza mutazioni la sessione `d08866e079464d34bd2d2fc689392be8`, v3, conversazione `conv-b68b76fcd3474a0f`. Domanda backend persistita/proiettata:

> Per «Estremi procura (procuratore)», il modulo specifica «se procuratore». Questa condizione si applica al tuo caso?

Chiamate reali del planner, con configurazione di progetto corrente e stesso snapshot/cronologia: due risposte USER, due tentativi per ciascuna. Nessuna risposta simulata e nessuna modifica alla sessione usata per la diagnosi.

Il contesto inviato al modello aveva `question.field_ids=["t0.r4.c1"]` e `fields[0].id="t0.r4.c1"`; lo schema backend richiedeva invece `field_replies[0].field_id`. Il modello ha copiato `id` dal contesto. L’interpretazione della negazione era corretta in tutti e quattro gli output.

Il parametro `response_schema` viene applicato nativamente dal trasporto Ollama. Per DeepSeek il trasporto corrente invia `response_format={"type":"json_object"}`, senza un vincolo server sui nomi delle proprietà dello schema Pydantic. Il vecchio prompt chiedeva genericamente “l’ID chiesto”, senza esempio esplicito della proprietà `field_id`; il retry chiedeva soltanto di rispettare il contratto, senza indicare i due errori concreti.

### USER: «No, il sottoscrittore non agisce come procuratore.»

Output grezzo, tentativo 1:

```json
{"action":"compilation_input", "answer":"", "queries":[], "target":"form", "form_id":153, "source_queries":[], "field_replies":[{"id":"t0.r4.c1","action":"not_applicable","value":null,"user_quote":"No, il sottoscrittore non agisce come procuratore."}]}
```

Output grezzo, tentativo 2:

```json
{"action":"compilation_input", "answer":"", "queries":[], "target":"form", "form_id":153, "source_queries":[], "field_replies":[{"id":"t0.r4.c1","action":"not_applicable","value":null,"user_quote":"No, il sottoscrittore non agisce come procuratore."}]}
```

Errori di validazione (identici al primo tentativo e al retry):

```text
field_replies.0.field_id: Field required [missing]
field_replies.0.id: Extra inputs are not permitted [extra_forbidden]
```

Esito finale: `GenerationError`, «Il modello non ha restituito una decisione valida su come gestire il messaggio anche dopo un tentativo di correzione. Riprova.» Nessun field aggiornato.

Acquisizioni complete: [prompt iniziale ricostruito dai primi due messaggi](../backend/data/compilation-audit/single-active-field-20261006/before-negative-paraphrase/prompt-initial-reconstructed.json), [schema richiesto](../backend/data/compilation-audit/single-active-field-20261006/before-negative-paraphrase/schema.json), [prompt di retry](../backend/data/compilation-audit/single-active-field-20261006/before-negative-paraphrase/prompt-2.json), [errori](../backend/data/compilation-audit/single-active-field-20261006/before-negative-paraphrase/validation-errors.json). Il prompt di retry contiene anche l’output respinto e la richiesta originale. Nota di acquisizione: il trace ha salvato il body aggiornato dopo l’append del retry anche in `prompt-1.json`; il file iniziale linkato ricostruisce deterministicamente i due messaggi originali dal retry, senza cambiare contenuti o parametri. Raw/errori originali conservati.

### USER: «no»

Output grezzo, tentativo 1:

```json
{"action":"compilation_input", "answer":"", "queries":[], "target":"form", "form_id":153, "source_queries":[], "field_replies":[{"id":"t0.r4.c1","action":"not_applicable","value":null,"user_quote":"no"}]}
```

Output grezzo, tentativo 2:

```json
{"action":"compilation_input", "answer":"", "queries":[], "target":"form", "form_id":153, "source_queries":[], "field_replies":[{"id":"t0.r4.c1","action":"not_applicable","value":null,"user_quote":"no"}]}
```

Errori di validazione (identici al primo tentativo e al retry):

```text
field_replies.0.field_id: Field required [missing]
field_replies.0.id: Extra inputs are not permitted [extra_forbidden]
```

Esito finale: `GenerationError`, «Il modello non ha restituito una decisione valida su come gestire il messaggio anche dopo un tentativo di correzione. Riprova.» Nessun field aggiornato.

Acquisizioni complete: [prompt iniziale ricostruito dai primi due messaggi](../backend/data/compilation-audit/single-active-field-20261006/before-negative-short/prompt-initial-reconstructed.json), [schema richiesto](../backend/data/compilation-audit/single-active-field-20261006/before-negative-short/schema.json), [prompt di retry](../backend/data/compilation-audit/single-active-field-20261006/before-negative-short/prompt-2.json), [errori](../backend/data/compilation-audit/single-active-field-20261006/before-negative-short/validation-errors.json). Il prompt di retry contiene anche l’output respinto e la richiesta originale. Nota di acquisizione: il trace ha salvato il body aggiornato dopo l’append del retry anche in `prompt-1.json`; il file iniziale linkato ricostruisce deterministicamente i due messaggi originali dal retry, senza cambiare contenuti o parametri. Raw/errori originali conservati.

## Contratto corretto

- Con workflow abilitato, domanda `value`/`applicability`, un solo destinatario e contesto coerente, il planner usa `ActiveQuestionPlan`.
- Output semantico: `VALUE`, `CONDITION_TRUE`, `CONDITION_FALSE`, `UNKNOWN`, `SKIP`, `REFUSE`, `PAUSE`, `CLARIFY`; `value`, `normalized_value`, `rationale` sono facoltativi secondo l’azione. Solo VALUE ammette valori.
- `CHAT` è la via per una nuova domanda: include un routing documentale senza selezione di field, poi torna al percorso reply/retrieve FORM/SOURCE/MIXED esistente. Non aggiunge una seconda chiamata LLM.
- Lo schema e il contesto single-field non espongono al modello identificatori di campo/sessione/versione. Il backend conserva lo snapshot e verifica progetto, conversazione, domanda e revisione prima della mutazione.
- Il backend ricava il target dalla propria domanda e costruisce internamente gli input già consumati dal dominio della sessione. L’intero messaggio USER è la provenienza; non si accettano estratti ritagliati o ID scelti dal modello.
- CONDITION_FALSE opera soltanto su una domanda di applicabilità: NOT_APPLICABLE, USER, valore nullo e motivo conservato. Non scrive fatti.
- CONDITION_TRUE conferma solo l’applicabilità USER: riapre il campo PENDING prioritario e ricerca SOURCE. Soltanto SOURCE pertinente e validata può produrre RESOLVED.
- VALUE mantiene grounding letterale/date deterministiche e validatore DOCX. CLARIFY e alternative esplicite non cambiano valori. UNKNOWN/SKIP/REFUSE differiscono; PAUSE conserva il workflow.
- Nessun nuovo keyword matching, alias `id`/`field_id`, ruolo/label/candidate hardcoded applicativo. Il guard preesistente per i controlli interi e la protezione dalle alternative restano invariati nella semantica; non decidono la polarità di applicabilità.
- Con target multipli/incoerenti o workflow non attivo non si usa la scorciatoia: resta il planner generale; un’eventuale decisione semantica priva di destinatario deterministico è respinta.
- Una chiamata di planner per messaggio, al massimo un retry con errori precisi e lo stesso schema. Nessuna modifica a DB schema, API frontend, RAG, parser o renderer.

## Dopo la modifica: benchmark reale, codice congelato

Nuove conversazioni create con normale POST `/answer`, mention `form_id=153`, «me lo compili?». Preparazione e risoluzione tramite il server HTTP reale, con Qdrant/BGE-M3 e le SOURCE correnti. Per catturare direttamente prompt/raw/errori, il POST di chiarimento attraversa la stessa API FastAPI mediante ASGITransport, **senza MockTransport, provider sostituiti o risposte simulate**. Il planner chiama DeepSeek reale; lo stato viene salvato dai normali service e riletto dal server HTTP. Nessun UPDATE SQL manuale.

Il codice applicativo è identico prima/dopo il benchmark, verificato via SHA-256 di `intents.py`, `compilation_chat.py`, `main.py`. Nessuna modifica applicativa durante preparazione o benchmark; la strumentazione esterna osserva soltanto i frame del planner.

### Limite incontrato durante la preparazione

Nella prima nuova sessione il passo iniziale ha lasciato 278 PENDING e 1 MISSING: il classificatore ha proposto diverse etichette parafrasate, non contenute letteralmente in `form_quote`, fra cui la procura. La domanda attiva era quindi “Operatore economico”. È stato necessario **un solo resolve mirato** tramite l’API esistente, `field_ids=["t0.r4.c1"]`, per rianalizzare quel candidate con il provider reale e arrivare alla domanda di applicabilità. Il field non è stato forzato né sono stati forniti valori aziendali. Questa preparazione è registrata in `preparation-targeted-resolve-0.json`.

La seconda sessione ha raggiunto la domanda di applicabilità direttamente con il primo passo automatico. Il falso negativo del classificatore iniziale rimane fuori da questa correzione e impedisce di interpretare queste due prove come una certificazione della compilazione integrale.

### USER: «No, il sottoscrittore non agisce come procuratore.»

Sessione `5e1a6b1fcf8a4aa3a94188d89330077b`, conversazione `conv-59cdc5c0155d4eaa`.

Output grezzo DeepSeek, primo e unico tentativo:

```json
{"action": "CONDITION_FALSE", "value": null, "normalized_value": null, "rationale": "L'utente nega che il sottoscrittore agisca come procuratore."}
```

**Parsing/validazione: accettato; errori `[]`; retry non usato.**

Transizione backend: target `t0.r4.c1` → **NOT_APPLICABLE / USER**, valore `null`, applicabilità `false`; revisione **5 → 6**. Tutti gli altri field invariati.

Motivo persistito: `Indicazione USER: No, il sottoscrittore non agisce come procuratore.`.

Risposta: «Questa voce non è applicabile. Continuo con il resto.»

La sessione continua su `t0.r5.c1`: «Mi manca un valore verificato per «Operatore economico». Qual è?». Rimane WAITING_FOR_USER sul prossimo problema; `auto_continue=false` è corretto perché attende quella risposta, non perché è bloccata sulla procura. Nessuna finalizzazione/bozza implicita.

[Prompt reale](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/prompt-1.json), [schema](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/schema.json), [raw](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/raw-1.txt), [transizione](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/transition.json), [stato dopo](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/state-after.json), [revisioni](../backend/data/compilation-audit/single-active-field-20261006/after-negative-paraphrase/revisions.json).

### USER: «no»

Sessione `514078f1a6f5493a9164bd38ff809fa4`, conversazione `conv-379b5f72d59344f0`.

Output grezzo DeepSeek, primo e unico tentativo:

```json
{"action": "CONDITION_FALSE", "value": null, "normalized_value": null, "rationale": "L'utente risponde negativamente alla condizione di applicabilità 'se procuratore'."}
```

**Parsing/validazione: accettato; errori `[]`; retry non usato.**

Transizione backend: target `t0.r4.c1` → **NOT_APPLICABLE / USER**, valore `null`, applicabilità `false`; revisione **3 → 4**. Tutti gli altri field invariati.

Motivo persistito: `Indicazione USER: no`.

Risposta: «Questa voce non è applicabile. Continuo con il resto.»

La sessione continua su `t0.r5.c1`: «Mi manca un valore verificato per «Operatore economico». Qual è?». Rimane WAITING_FOR_USER sul prossimo problema; `auto_continue=false` è corretto perché attende quella risposta, non perché è bloccata sulla procura. Nessuna finalizzazione/bozza implicita.

[Prompt reale](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/prompt-1.json), [schema](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/schema.json), [raw](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/raw-1.txt), [transizione](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/transition.json), [stato dopo](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/state-after.json), [revisioni](../backend/data/compilation-audit/single-active-field-20261006/after-negative-short/revisions.json).

## Verifiche e limiti

- Test software finali: **252 passati** mirati; suite backend completa **1.067 passati**; Ruff e diff check passati. Questi test usano provider simulati e DB/storage temporanei, distinti dalle chiamate DeepSeek sopra.
- Coperti destinatario solo backend, negazioni/parafrasi, sì, UNKNOWN/SKIP/PAUSE/REFUSE, VALUE USER localizzato, ambiguità anche con polarità LLM errata, ID estranei respinti, unico retry, target multipli, workflow non attivo, revisioni obsolete, FORM/SOURCE durante domanda attiva e vecchie invarianti di provenance (FTS5/Qdrant).
- Frontend/browser/lint/build frontend non rieseguiti: nessun codice o contratto frontend modificato in questo intervento. Il trasporto ASGI del chiarimento testa il backend reale, non l’interazione browser.
- Originale immutato: SHA-256 `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0` prima/dopo. Sessione della diagnosi `d08866e079464d34bd2d2fc689392be8` confrontata prima/dopo, invariata; sessioni precedenti non riprese/modificate.
- I raw e i prompt completi sono file locali esclusi da Git. Nessun header di autenticazione, credenziale o contenuto `.env` nel report.
- Restano i blocchi già osservati del classificatore (label non grounded, decorative con estratto vuoto) e della coverage SOURCE. Questo test corregge e verifica il chiarimento singolo, non la compilazione completa dei 279 candidate né il DOCX finale.
- Prossimo passo: affrontare i blocchi di classificazione/copertura già diagnosticati, soltanto con incarico esplicito, poi ripetere l’E2E completo. Nessun commit/push.
