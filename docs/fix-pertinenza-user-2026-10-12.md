# Pertinenza delle risposte USER — 12 ottobre 2026

**Il caso critico ora non modifica il campo sbagliato.** DeepSeek propone ancora
la denominazione nello slot recapito; il nuovo verificatore indipendente respinge
l'associazione. Stato, valore e versione della sessione rimangono identici.
**40/43** sul gold Dialogo V1 invariato, prima 39/43; **9/9** nel set separato
che sfida direttamente il verificatore. Non sono 52 compilazioni complete.

## Causa e correzione

Prima, `plan_chat_turn` validava il contratto del router e legava lo slot al campo
attivo; il dominio verificava quote USER, alternative e valore DOCX. Il valore
della denominazione era letteralmente nel messaggio e lo slot recapito esisteva:
questi controlli erano corretti ma non verificavano la pertinenza fra i due.
Un validatore email specifico avrebbe lasciato aperto il problema per altri
campi testuali. Nessuna parola o label della fixture è codificata nel fix.

Ora `compilation_reply_guard.py` riceve l'ultimo messaggio, la domanda, tutti gli
slot attivi e le proposte del router, considerate ipotesi non affidabili. Per
VALUE/CONDITION_TRUE/CONDITION_FALSE restituisce solo slot già noto e risultato
SUPPORTED / UNRELATED / AMBIGUOUS, con breve motivazione. Non sceglie field_id,
non cambia valori, non legge SOURCE e non riceve il rationale del router.
Il backend ammette solo check unici SUPPORTED; controlli mancanti, duplicati,
ID estranei, schema invalido o errore provider non autorizzano scritture.
Se non resta alcuna risposta valida, chiede chiarimento conservando la domanda;
in un gruppo conserva le altre parti valide. Poi rimangono obbligatori quote
USER, validazione DOCX, controllo alternative, destinatari backend e CAS.

Una verifica per gruppo, massimo quattro proposte, 768 token di output,
timeout 15 s, nessun retry. Il router conserva il suo solo retry strutturale:
massimo tre chiamate in un turno che scrive. Nessuna verifica aggiuntiva per
soli controlli, RAG, export o analisi globale. Nessun cambio UI/parser/renderer,
nessuna migrazione/reindicizzazione e nessuna promozione USER -> SOURCE.

## Protocollo reale

Commit del codice **132bc6a**, produzione e runner immutati durante entrambe le
serie, nessun caso fallito ripetuto per selezionare un esito. Profilo corrente
`deepseek-flash`, thinking disabilitato; routing temperature 0.1, check 0.
Stessi 43 messaggi/contesti/Word/gold della
[fixture Dialogo V1](../demo-documents/benchmark-dialogo/v1/README.md), hash
verificati prima delle API; aspettative mai inviate al modello. Confronto con
[baseline sul commit 4820b95](benchmark-dialogo-2026-10-12.md).
Checkpoint autoriali su DB/storage temporanei, nessuna sessione live modificata;
DB locale aperto in sola lettura per leggere il profilo. Mutazioni reali tramite
servizi di produzione e rilettura del DB; normali intent si fermano al routing.
La chiamata router diagnostica resta misurata anche dove il guard finish può
precederla in chat. Nessuna nuova analisi globale, retrieval o sintesi AI.

Separatamente [Guard V1](../demo-documents/benchmark-dialogo/guard-v1/README.md)
contiene nove assegnazioni preparate prima delle API: la prima replica la vecchia
proposta errata reale, le altre sono avversarie/corrette/ambigue. Si chiama solo
il verificatore reale e si persistono le sole decisioni ammesse, non si simulano
nuovi output del router. Gold escluso dal prompt; nove chiamate, zero retry.
Questo set evita di attribuire il fix a un caso in cui il router, variabile,
potesse incidentalmente assegnare il campo corretto da solo.

## Il caso critico, raw e stato

Domanda: «Quale recapito devo usare per le comunicazioni?».
USER: «Correggi la denominazione aziendale in Aurora Servizi S.r.l.».
Raw router reale:

```json
{"intent": "answer_fields", "answer": "", "queries": [], "target": "form", "form_id": null, "source_queries": [], "replies": [{"action": "VALUE", "slot": 1, "user_quote": "Correggi la denominazione aziendale in Aurora Servizi S.r.l.", "value": "Aurora Servizi S.r.l.", "normalized_value": null, "rationale": "L'utente fornisce il valore da usare per il recapito/denominazione nelle comunicazioni."}]}
```

Raw verificatore reale:

```json
{"checks":[{"slot":1,"result":"UNRELATED","rationale":"L'utente corregge la denominazione aziendale, non fornisce il recapito per le comunicazioni richiesto dal campo."}]}
```

Esito backend: intent finale explain/reply, nessuna command di compilazione,
nessuna mutazione. Messaggio: «Sto chiedendo «Recapito comunicazioni». Non posso associare con sicurezza la tua indicazione a questa richiesta. Puoi precisare?».
`before.json == after.json`, comprese versione, domanda e USER values.
Nel replay indipendente della vecchia proposta si ottiene nuovamente UNRELATED.

## Misure, includendo il costo

| Misura | Baseline | Dopo |
|---|---:|---:|
| Casi gold conformi | 39/43 | 40/43 |
| Routing / check indipendenti | 43 /0 | 43 /12 |
| Retry / errori schema / eccezioni | 0 /0 /0 | 0 /0 /0 |
| Token input /output | 138.803 /4.013 | 149.606 /4.765 |
| Token totali | 142.816 | 154.371 |
| Tempo turni | 47,92 s | 66,20 s |
| Tempo API | 46,41 s | 64,79 s |
| Mediana /massimo turno | 1,10 /1,54 s | 1,22 /3,04 s |
| Mutazioni slot /valori USER | 28 /8 | 26 /6 |
| Export verificati fisicamente | 5 | 5 |

Solo i 12 check aggiunti: **11.594 token /13,81 s** API, mediana **1,14 s**.
Costo totale +11.555 token rispetto alla baseline; la differenza non coincide
con i check perché il testo restituito dal router varia. Tempo turni +18,28 s:
13,81 s sono check, il resto comprende variazione router/trasporto. Non è un
risparmio o una misura causale della latenza, né il tempo della compilazione.
Set separato Guard V1: **8.366 token /9,68 s** API. Non sommare i due punteggi.
Nessuna regressione dei 39 casi già conformi; nessuna risposta pertinente
respinta nei casi fissati. Una sola serie per dataset, nessuna misura di varianza.

## Tutti i 43 esiti, gold invariato

| Caso | Intent finale | Esito | Check gold falliti |
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
| condition-skip | pause | FAIL | intent, actions |
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
| finish-mixed | generate | FAIL | intent |
| blank-export | generate | FAIL | intent |
| normal-form | retrieve | PASS |  |
| normal-compile | compile | PASS |  |
| normal-factual | retrieve | PASS |  |
| correction-outside | explain | PASS |  |
| injection | reply | PASS |  |

Restano tre FAIL: condition-skip va in PAUSE anziché SKIP locale;
finish-mixed e blank-export scelgono generate anziché finish. In finish-mixed
questa volta il servizio non scrive alcun valore e chiede chiarimento; nella
baseline il router ignorava finish e scriveva il valore. Il contratto dei comandi
non è stato modificato: non attribuiamo questa variazione al gate. Non si cambia
il gold per farli diventare PASS e non si dichiarano questi problemi risolti.

## Tutti i nove controlli indipendenti

| Caso | Slot ammessi | Esito |
|---|---|---|
| old-real-wrong-proposal | nessuno | PASS |
| unrelated-code | nessuno | PASS |
| unrelated-negative | nessuno | PASS |
| bare-date | 1 | PASS |
| natural-contact | 1 | PASS |
| semantic-negative | 1 | PASS |
| partial-group | 1,2 | PASS |
| ambiguous-two-conditions | nessuno | PASS |
| ambiguous-value | nessuno | PASS |

Nel gruppo parziale passano condizione delega e recapito; il nome di un referente
non diventa data di abilitazione. «Sì» con due condizioni non viene assegnato
arbitrariamente; una scelta fra due recapiti non diventa un valore unico.
Valore breve, parafrasi negativa e recapito pertinente restano utilizzabili.
Ogni check ammesso attraversa il dominio; le mutazioni hanno provenance USER.
Ogni rifiuto lascia lo stato identico, non soltanto il valore.

## DOCX, test software e limiti

Cinque export reali, confrontati in sola lettura con stato/report/Word originali:
quattro inseriscono il recapito USER autoriale preesistente in t0.r1.c1; il quinto
non inserisce valori. Tutte le celle materializzate coincidono con il report,
nessuna scrittura extra o evidence SOURCE fittizia. Hash originali invariati;
altre celle/paragrafi invariati salvo banner bozza. Nessuna nuova valutazione
SOURCE o misura della copertura del modulo reale.

Software: **277 test mirati /46,40 s**, **1.924 backend completi /146,27 s**,
Ruff e diff check passati, provider simulati. Nuovi casi su HTTP reale ASGI,
associazioni estranee, gruppi parziali, errori schema/provider, ambiguità e token.
Primo run mirato con 14 failure di vecchie asserzioni su numero/ultimo prompt;
aggiornate senza indebolire i gate, log conservati. UI e contratti invariati:
frontend/browser non ripetuti. I test software non misurano la qualità DeepSeek.

La pertinenza semantica resta affidata a un modello e può ancora sbagliare.
Errori/timeout possono rifiutare conservativamente risposte valide; altri
provider non sono stati valutati in questa serie. Non supportate correzioni
arbitrarie a field fuori dal gruppo: si chiede chiarimento, senza applicarle.
Prossimo intervento: priorità dei comandi misti e SKIP locale/PAUSE, con lo
stesso benchmark. Nessun push; commit locali per codice e report.

## Ripetizione e dati conservati

Da backend, output nuovi e progetto che seleziona DeepSeek reale:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_dialogue.py --project prova --output data/compilation-audit/nuova-serie-dialogo
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_reply_guard.py --project prova --output data/compilation-audit/nuova-serie-guard
```

Grezzi locali: backend/data/compilation-audit/reply-scope-20261012/.
Prompt/schema/output/usage/tempi, validazioni, stati before/after, documenti e
report, log test e snapshot di codice/fixture salvati nel
[bundle sanificato](benchmarks/2026-10-12-reply-scope-audit.tar.gz).
[Metriche e tutti gli esiti](benchmarks/2026-10-12-reply-scope.json),
[controlli finali](benchmarks/2026-10-12-reply-scope-final-checks.json).
Nessuna chiave, database o runtime privato incluso. Archivio verificato
byte per byte e mediante hash di ogni file; runtime temporanei eliminati.
