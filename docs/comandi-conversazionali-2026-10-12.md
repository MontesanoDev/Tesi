# Comandi conversazionali — 12 ottobre 2026

**28/28** scenari Comandi V1, contro **24/28** prima della modifica;
**43/43** Dialogo V1, contro **40/43** nell'ultima baseline. Nessuna regressione
nei casi prima conformi, nessuna scrittura indebita nei turni di pausa/export.
Un output iniziale invalido corretto dal solo retry previsto, conservato sotto.
Risultati di dialogo su checkpoint, non accuratezza della compilazione completa.

## Diagnosi e scelte

Il vecchio prompt descriveva pause come sospensione o ripresa più tardi senza
chiarire abbastanza l'oggetto: rinviare la domanda corrente poteva sospendere
l'intero lavoro. La priorità di finish sui dati era indicata, ma vicina alle
regole di risposta ai campi. finish/generate rappresentano la stessa operazione
nel motore globale; scambiarne il nome causava due FAIL di contratto della
baseline pur con richiesta di export correttamente riconosciuta.

Intervento minimo, senza nuova chiamata classificatrice o cambio di schema:

- Il prompt unico distingue oggetto e polarità: rinvio locale SKIP, incertezza
  UNKNOWN, pausa della sessione, negazioni e richieste di spiegazione. Lasciare
  vuota una risposta di applicabilità non significa CONDITION_FALSE.
- PAUSE/FINISH mantengono la priorità sui nuovi valori nel turno. Le indicazioni
  degli altri slot restano gestite dal dominio corrente e dal gate di pertinenza.
- Il backend normalizza soltanto il già validato intent generate globale in
  finish se non è attiva una domanda di generazione. Usa engine/checkpoint già
  noti, senza analizzare parole USER o allargare i permessi di export.
- Legacy preservato: lì finish e generate hanno effetti diversi. Engine viene
  conservato nel contesto interno, senza nuove colonne o contratti frontend.

Composizione «salva questo valore POI metti in pausa/esporta» non implementata:
la regola conservativa attuale scarta i valori di quel turno. Una futura
composizione di azioni richiede una decisione di prodotto separata.

## Protocollo congelato

[Comandi V1](../demo-documents/benchmark-dialogo/commands-v1/README.md): 28 scenari,
gold e hash fissati in **b468ea5 prima delle API**. Word e contesti ripresi dal
Dialogo V1, scenari/gold nuovi e separati. BEFORE su b468ea5, codice di produzione
identico al precedente fix USER. AFTER su **802c483**. Successivamente ripetuti
anche i [43 Dialogo V1](../demo-documents/benchmark-dialogo/v1/README.md), senza
cambiare fixture/gold; confronto con la
[baseline 40/43](fix-pertinenza-user-2026-10-12.md). Nessuna modifica applicativa
nel corso di ciascuna serie, nessun caso selettivamente ripetuto.

DeepSeek reale deepseek-flash, thinking disabilitato; stesso trasporto di
produzione, routing 0.1 e gate di pertinenza 0. Gold escluso dai prompt.
Max due tentativi router +un solo gate USER dove necessario. 99 turni in
checkpoint indipendenti, **117 chiamate reali** complessive: non una singola
conversazione di 99 turni o 99 documenti compilati. Gold valutato separatamente
per i due dataset. DB/storage temporanei, profilo live solo in lettura, nessun
database o chiave copiato. Mutation/export reali e rilettura dello stato.
Normali FORM/SOURCE/compile valutati al routing, senza avviare nuove analisi/RAG.

## Esiti e costi

| Misura | Comandi BEFORE | Comandi AFTER | Dialogo AFTER |
|---|---:|---:|---:|
| Casi conformi | 24/28 | 28/28 | 43/43 |
| Routing /gate USER | 28 /3 | 28 /2 | 44 /12 |
| Retry strutturali | 0 | 0 | 1 |
| Token input /output | 93.711 /2.308 | 102.742 /2.293 | 168.447 /4.818 |
| Token totali | 96.019 | 105.035 | 173.265 |
| Tempo turni | 35,54 s | 35,78 s | 66,77 s |
| Tempo API | 35,02 s | 35,26 s | 65,29 s |
| Export confrontati nel Word | 1 | 1 | 5 |
| Eccezioni /export non autorizzati | 0 /0 | 0 /0 | 0 /0 |

Il prompt più esplicito costa circa **353 token input per routing** nei casi
originari: nessuna nuova chiamata introdotta dal fix. Le due anziché tre
verifiche USER nei 28 riflettono il caso local-blank-not-false: prima proponeva
una condizione falsa (respinta dal gate), ora direttamente SKIP, senza verifica
di un valore. Nessuna riduzione strutturale del budget. Comandi AFTER +9.016 token, tempi sostanzialmente simili
in questa singola serie, senza stima causale o di varianza. Dialogo precedente:
154.371 token /66,20 s; oggi 173.265 /66,77 s, includendo un retry aggiuntivo.
Il guadagno osservato comprende miglioramenti nella semantica del rinvio;
le correzioni generate/finish sono in parte normalizzazione di nomenclatura:
non significano nuovi valori compilati o maggiore copertura SOURCE.

### Rinvio della conferma, prima PAUSE

USER «Lasciamo questa conferma per dopo.»; raw reale AFTER:

```json
{"intent": "answer_fields", "answer": "", "queries": [], "target": "form", "form_id": null, "source_queries": [], "replies": [{"action": "SKIP", "slot": 1, "user_quote": "Lasciamo questa conferma per dopo.", "rationale": "L'utente rinvia la conferma sulla domanda corrente, non sospende l'intera sessione."}]}
```

Backend: registra SKIP/USER sul solo slot 1, nessun applies o valore; sessione
non in pausa, continua con le domande residue. Nella baseline questa stessa
frase metteva in pausa tutto. Non si associa il comportamento a label specifiche.

### Rinvio con negazione, prima senza effetto

USER «Lascia vuota questa voce, non sto dicendo che non si applica.»:

```json
{"intent": "answer_fields", "answer": "", "queries": [], "target": "form", "form_id": null, "source_queries": [], "replies": [{"action": "SKIP", "slot": 1, "user_quote": "Lascia vuota questa voce, non sto dicendo che non si applica.", "rationale": "L'utente rinvia la voce senza confermare né negare l'applicabilità."}]}
```

BEFORE il router propone CONDITION_FALSE, ma il gate indipendente restituisce
AMBIGUOUS: intent finale explain, nessuna mutazione. AFTER SKIP/USER: la condizione resta non
verificata; non diventa falsa. È un cambiamento effettivo dello stato, non solo
un diverso nome di intent.

### Messaggi misti e alias export

«Il recapito è contatti@aurora.example; per ora basta, prepara una bozza con
quello che hai già.» -> finish, nessuna VALUE, export richiesto. Al checkpoint
senza valori il dominio risponde con chiarimento; non genera una copia vuota
implicitamente. «Usa ... però ferma la compilazione» -> pausa, nessun valore
acquisito. Solo un consenso alla domanda di generazione può autorizzare la
copia vuota proposta secondo il gate esistente; non è cambiato.

La normalizzazione viene applicata prima del binding al dominio e soltanto a
un output di export già valido; non può trasformare reply, explain o SKIP in
una richiesta di generazione. Schema con export e replies insieme resta invalido.

### Output invalido e retry, senza nasconderlo

Dialogo export-no, USER «No, non generare ancora.»: primo raw
`{"intent":"answer_fields","answer":"","queries":[],"target":"form","replies":[]}`.
Il checkpoint ha question_kind=generate e nessuno slot: parser rifiuta con
«Non ci sono slot attivi a cui rispondere». Retry strutturale unico -> reply,
«Va bene, non genero la bozza…». Nessuna mutazione/export in entrambi i passi.
Prompt di retry, raw completi e validation error conservati nel bundle.
**43/43 è l'esito finale**, non 43 output corretti al primo tentativo.

## Tutti i 28 confronti

| Caso | BEFORE intent/esito | AFTER intent/esito |
|---|---|---|
| local-point | answer_fields /PASS | answer_fields /PASS |
| local-confirmation | answer_fields /PASS | answer_fields /PASS |
| local-next | answer_fields /PASS | answer_fields /PASS |
| group-local-contact | answer_fields /PASS | answer_fields /PASS |
| group-skip-and-value | answer_fields /PASS | answer_fields /PASS |
| local-unknown | answer_fields /PASS | answer_fields /PASS |
| session-stop | pause /PASS | pause /PASS |
| session-tomorrow | pause /PASS | pause /PASS |
| session-stop-no-export | pause /PASS | pause /PASS |
| session-value-and-stop | pause /PASS | pause /PASS |
| negated-pause | answer_fields /PASS | answer_fields /PASS |
| negated-skip | explain /PASS | explain /PASS |
| negated-export | explain /PASS | explain /PASS |
| group-unknown-and-value | answer_fields /PASS | answer_fields /PASS |
| export-current | generate /FAIL | finish /PASS |
| export-no-questions | finish /PASS | finish /PASS |
| export-mixed | generate /FAIL | finish /PASS |
| export-blank | generate /FAIL | finish /PASS |
| session-resume-reference | resume /PASS | resume /PASS |
| session-resume-preserve | resume /PASS | resume /PASS |
| negated-resume | explain /PASS | explain /PASS |
| paused-status | explain /PASS | explain /PASS |
| session-resume-command | resume /PASS | resume /PASS |
| consent-checkpoint | generate /PASS | generate /PASS |
| explain-before-export | explain /PASS | explain /PASS |
| courtesy-after-export | reply /PASS | reply /PASS |
| local-blank-not-false | explain /FAIL | answer_fields /PASS |
| resume-no-export | resume /PASS | resume /PASS |

## Tutti i 43 originali, gold invariato

| Caso | Intent finale | Esito | Check falliti |
|---|---|---|---|
| consent-1 | generate | PASS |  |
| consent-2 | generate | PASS |  |
| consent-3 | generate | PASS |  |
| consent-4 | generate | PASS |  |
| empty-consent | generate | PASS |  |
| export-no | reply | PASS |  |
| export-later | pause | PASS |  |
| export-question | explain | PASS |  |
| courtesy-generated | reply | PASS |  |
| courtesy-paused | reply | PASS |  |
| condition-no | answer_fields | PASS |  |
| condition-negative | answer_fields | PASS |  |
| condition-yes | answer_fields | PASS |  |
| condition-unknown | answer_fields | PASS |  |
| condition-skip | answer_fields | PASS |  |
| condition-ambiguous | answer_fields | PASS |  |
| condition-explain | explain | PASS |  |
| email-value | answer_fields | PASS |  |
| date-value | answer_fields | PASS |  |
| email-unknown | answer_fields | PASS |  |
| email-skip | answer_fields | PASS |  |
| email-refuse | answer_fields | PASS |  |
| email-alternatives | answer_fields | PASS |  |
| group-all | answer_fields | PASS |  |
| group-partial | answer_fields | PASS |  |
| group-controls | answer_fields | PASS |  |
| group-ambiguous-part | answer_fields | PASS |  |
| group-one-blank | answer_fields | PASS |  |
| group-all-blank | answer_fields | PASS |  |
| two-conditions-yes | answer_fields | PASS |  |
| two-conditions-all | answer_fields | PASS |  |
| two-conditions-negative | answer_fields | PASS |  |
| pause | pause | PASS |  |
| pause-mixed | pause | PASS |  |
| resume | resume | PASS |  |
| paused-explain | explain | PASS |  |
| finish-mixed | finish | PASS |  |
| blank-export | finish | PASS |  |
| normal-form | retrieve | PASS |  |
| normal-compile | compile | PASS |  |
| normal-factual | retrieve | PASS |  |
| correction-outside | explain | PASS |  |
| injection | reply | PASS |  |

## Provenance, DOCX e software

Il gate di pertinenza USER è invariato; correction-outside continua a respingere
la denominazione nel recapito, stato before/after identico. Scope dei progetti,
SOURCE e FORM invariati; nessuna conferma USER promossa a SOURCE/RESOLVED.
Tutte le scritture nei checkpoint sono USER autoriali o risposte ai soli slot
attivi. Sette export realmente confrontati: sei inseriscono un recapito USER
preesistente nel campo corretto; uno è la copia senza valori. Celle/report/stato
coincidono, originali e altre celle/paragrafi invariati salvo banner.

Software con provider simulati: **248 mirati /37,67 s**, **1950 backend
completi /145.97 s**, Ruff e diff check. Otto test fixture/harness separati
senza provider /1,11 s. Aggiunte regressioni HTTP su rinvii, pausa/ripresa,
normalizzazione limitata al globale, schema misto invalido, gate di copia vuota
ed export USER. Prime due righe lunghe Ruff nel test corrette, log conservato.
Nessuna modifica UI/contratto frontend: frontend/browser non rieseguiti.

## Limiti e ripresa

Interpretazione ancora semantica e fallibile: nessuna garanzia per tutte le
parafrasi o altri provider. Il retry osservato dimostra che il modello può
ancora scegliere un intent non applicabile; il backend conserva i gate.
Nessuna composizione transazionale di risposta+comando. Nessuna nuova prova
sulla qualità SOURCE, copertura dei moduli reali, checkbox o associazione dei
candidate nell'analisi globale. READY/GENERATED non certificano completezza.
Questi risultati chiudono il passo sui comandi; prima di altre modifiche
riesaminare i limiti con l'utente. Nessuna migrazione/reindicizzazione/push.

[Metriche e tutti gli effetti](benchmarks/2026-10-12-commands.json),
[bundle sanificato](benchmarks/2026-10-12-commands-audit.tar.gz),
[verifiche finali](benchmarks/2026-10-12-commands-final-checks.json).
Grezzi locali: backend/data/compilation-audit/commands-20261012/.
Prompt/schema/raw/tempi/usage/validazioni, stati before/after, Word e report,
fixture e codice BEFORE/AFTER conservati; nessuna credenziale/DB/runtime.
Archivio verificato byte per byte e tramite SHA di ciascun file.

Per ripetere da backend (output nuovi, profilo DeepSeek reale):

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_dialogue.py --project prova --fixture ../demo-documents/benchmark-dialogo/commands-v1 --output data/compilation-audit/comandi-nuova-serie
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_dialogue.py --project prova --output data/compilation-audit/dialogo-nuova-serie
```
