# Test reale E2E della CompilationSession — 6 ottobre 2026

Aggiornamento successivo, separato da questo test di osservazione: il chiarimento
single-active-field è stato corretto e provato con DeepSeek reale il 7 ottobre.
Vedi [diagnosi, raw e transizioni](test-reale-active-question-2026-10-07.md).
I risultati e le sessioni storiche riportati sotto restano quelli del 6 ottobre;
i blocchi di classificazione/copertura SOURCE non sono stati risolti da quella correzione.

Test di osservazione richiesto dall'utente, senza correzioni applicative,
provider simulati, aggiornamenti SQL manuali, commit o push. Browser Chromium
sulla chat corrente, API FastAPI reali, profilo **DeepSeek / deepseek-flash**;
retrieval **Qdrant locale / BGE-M3 tramite Ollama**. Le fonti aziendali contengono
valori didattici: il provider e le richieste del test sono reali.

Progetto: `minervino-di-lecce-elenco-sia`. Modulo archiviato: ID **153**,
`domanda-partecipazione.docx`, **90.761 byte**, **279 candidate**. È il modulo
che l'utente aveva già selezionato nel progetto del precedente test; la sua
intestazione indica Fondazione Università Magna Graecia. Non è stato sostituito
con un modulo ricreato, reindicizzato o corretto.

Conversazione principale: `conv-2f20346327a544c7`.
Sessione principale: `c849656d4e2e46ccab0d42ecd3d13c18`, finale **v20 / FAILED**.
[Apri la conversazione locale](http://localhost:5173/projects/minervino-di-lecce-elenco-sia/conversations/conv-2f20346327a544c7).

## Campi standard: risultato effettivo nella sessione principale

| candidate | requisito | valore | stato | provenance | evidence |
|---|---|---|---|---|---|
| t0.r0.c1 | Sottoscrittore / nome e cognome | — | PENDING | — |  |
| t0.r3.c1 | Ruolo / carica | — | PENDING | — |  |
| t0.r5.c1 | Operatore economico / denominazione | — | DEFERRED | — |  |
| t0.r6.c1 | Forma giuridica | — | DEFERRED | — |  |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r8.c1 | Sede operativa | — | DEFERRED | — |  |
| t0.r9.c1 | Codice fiscale operatore | IT01234567890 | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r10.c1 | Partita IVA | IT01234567890 | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r11.c1 | Telefono | — | PENDING | — |  |
| — | Tipologia operatore | — | PENDING | — |  |
| t3.r4.c0,t3.r5.c0,t3.r6.c0 | Forma di partecipazione | — | DEFERRED | — |  |
| t25.r0.c1 | Denominazione società di ingegneria | — | PENDING | — |  |
| t25.r2.c0 | Iscrizione CCIAA | — | PENDING | — |  |
| t25.r3.c1 | Numero / data iscrizione | — | PENDING | — |  |
| t26.r0.c1 | Direttore tecnico | — | PENDING | — |  |
| t26.r1.c1 | Qualifica direttore tecnico | — | PENDING | — |  |
| t26.r2.c1 | Data di abilitazione | — | PENDING | — |  |
| t26.r3.c1 | Ordine professionale | — | PENDING | — |  |
| t26.r4.c1 | Numero iscrizione albo | — | PENDING | — |  |


`DEFERRED` è la proiezione conversazionale richiesta per questo rapporto:
nel DB gli otto differiti conservano **due MISSING e sei AMBIGUOUS**, senza valori
né provenienza SOURCE/USER fittizi. Non è stata aggiunta una nuova enumerazione
o modificato lo stato per rendere i conteggi più favorevoli. I conteggi sotto
sono disgiunti e sommano a 279.

**Tipologia operatore:** i checkbox della tabella 1 non hanno un candidate nello
snapshot del parser esistente. PENDING nella tabella del rapporto significa
"non elaborata", non è uno stato persistito di un campo inesistente. La forma
di partecipazione ha tre candidate distinti con etichetta identica; il requisito
non è stato risolto. I nomi nella tabella delle posizioni PENDING identificano
le voci richieste per il benchmark, non requisiti già accettati dal classificatore.

| Misura | Numero |
|---|---:|
| Candidate con passo completato e risultato persistito | 24 |
| Ulteriori candidate nel gruppo fallito, senza esito applicato | 12 |
| Candidate distinti coinvolti complessivamente | 36 |
| Passi resolve completati | 2 |
| Passi resolve falliti, incluso un solo tentativo di ripresa | 2 |
| RESOLVED da SOURCE | 3 |
| USER_PROVIDED | 0 |
| MISSING non differiti | 0 |
| AMBIGUOUS non differiti | 0 |
| CONFLICTING | 0 |
| NOT_APPLICABLE | 0 |
| DEFERRED | 8 |
| PENDING | 268 |

**Campi standard realmente risolti:** sede legale, codice fiscale operatore,
partita IVA. Tutti provengono da `generalita-mapi.md`, file globale **-7**,
chunk **-43**, `role=source`, `scope=global`, `category=company`:

- Sede legale → `Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia` →
  estratto: «Sede legale di Mapi Ingegneria S.r.l.: Via Giovanni Amendola 172/C,
  70126 Bari (BA), Italia.»
- Codice fiscale operatore → `IT01234567890` → estratto: «Codice fiscale e
  Partita IVA riportati nella visura demo: IT01234567890.»
- Partita IVA → `IT01234567890` → stesso estratto SOURCE. È l'identificativo
  fittizio già dichiarato dalla KB, conservato senza inventare un valore reale.

Il termine "risolti" indica valori accettati nello stato. **Non significa che
siano già stati scritti in un DOCX**: la sessione non ha raggiunto READY.

## Flusso realmente osservato

Avvio dal composer: `@domanda-partecipazione.docx` + «me lo compili?».
Il menu mostrava il solo modulo del progetto; la richiesta portava `form_id=153`.
Risposta workflow: «Certo. Analizzo il modulo e verifico le informazioni
 disponibili.» Nessun rifiuto generico dal generatore RAG.

| Versione | Azione | Stato effettivo |
|---|---|---|
| 1 | Creazione nuova sessione | CREATED |
| 2 | Avvio primo passo automatico, 12 candidate | ANALYZING |
| 3 | Risultato primo passo | WAITING_FOR_USER, 3 SOURCE resolved |
| 4 | «salta» sulla condizione della procura | WAITING_FOR_USER, field differito |
| 5 | «basta» | WAITING_FOR_USER + `user_paused=true`; nessuna domanda attiva |
| 6 | Refresh, poi «riprendi» | Stessa sessione, pausa rimossa |
| 7 | «non lo so» per operatore economico | Differito, nessun valore aggiunto |
| 8 | «salta» per forma giuridica | Differito |
| 9 | «non lo so» per condizione sede operativa | Differito, avanzamento automatico |
| 10 | Secondo passo automatico | ANALYZING |
| 11 | Risultato secondo passo | WAITING_FOR_USER |
| 12–15 | «salta» sui quattro nuovi problemi | Differiti, poi avanzamento automatico |
| 16 | Terzo passo automatico | ANALYZING |
| 17 | HTTP 502: output strutturato non valido | FAILED; nessuna applicazione parziale |
| 18 | Una sola nuova richiesta «riprendi» | Stessa sessione, WAITING_FOR_USER |
| 19 | Ritentativo automatico dello stesso gruppo | ANALYZING |
| 20 | Stesso HTTP 502 | FAILED; campi precedenti conservati |

"PAUSED" è rappresentato dal flag persistito del workflow, non da un nuovo
status di dominio. Il refresh ha rimosso la domanda attiva durante la pausa;
la ripresa ha conservato ID e valori. Dopo l'interruzione dell'ambiente di lavoro
sono stati riavviati i servizi con `./start.sh`: le sessioni e revisioni sono
state ritrovate nel DB, senza ricrearle o modificarle manualmente.

UNKNOWN/SKIP hanno cambiato soltanto `conversation_disposition` del campo
chiesto: status fattuale, valore e provenance conservati; prossimo field
oppure nuova analisi. Le tre domande su «Forma di partecipazione» hanno testo
uguale ma ID diversi (`t3.r4.c0`, `t3.r5.c0`, `t3.r6.c0`): non è un loop sullo
stesso ID, ma la ripetizione resta confusa nella UX.

## Cause osservate, senza correzioni

1. **Interpretazioni non grounded:** 13 dei primi 24 candidate restano PENDING.
   Il classificatore propone nomi parafrasati o un ruolo personale non contenuto
   nel proprio `form_quote`: i validatori li scartano correttamente. Esempi:
   `Nome e cognome del sottoscritto` per `Il/La sottoscritto/a`,
   `Cellulare e telefono` per `Cellulare + Telefono`; dati personali con ruolo
   citato fuori dall'estratto. Nessuna ricerca SOURCE eseguita per questi field.
2. **Copertura/associazione SOURCE:** operatore economico e forma giuridica
   vengono ricercati, ma il loro bucket contiene soltanto chunk del progetto
   `avviso.pdf`: **4306, 4299, 4305, 4298**. La Company KB chunk **-43** contiene
   entrambi i valori, ed è recuperata per altri field nel medesimo passo.
   Il matcher la usa nelle proposte per denominazione/forma giuridica, ma non
   è ammessa per questi due candidate: `SOURCE non ammessa per questo candidate`.
   I valori sono quindi rifiutati, non inseriti manualmente dal test.
3. **Blocco strutturato del gruppo successivo:** E2E registra HTTP 502,
   `Output strutturato della risoluzione non valido`. Una riproduzione separata
   in sola lettura, con lo stesso classificatore, lo stesso gruppo e il profilo
   reale, riproduce l'errore: cinque decorative restituiscono `form_quote=""`,
   mentre `CandidateMeaning.form_quote` richiede almeno due caratteri.
   Candidate: `t9.r7.c0`, `t9.r7.c1`, `t11.r1.c0`, `t11.r3.c0`, `t11.r3.c1`.
   Fallisce la validazione JSON dell'intero gruppo, prima di SOURCE e salvataggio.
   I dodici candidate restano PENDING. Nessuna modifica per "riparare" l'output.

La riproduzione non è la risposta grezza storica dei due resolve falliti:
è un'ulteriore chiamata reale isolata, senza eseguire claim/completion né
salvare field. API e snapshot originali non persistono tutti gli output grezzi.
Il registro distingue valori, motivi ed errori persistiti dalle risposte grezze
osservate soltanto in queste riproduzioni. Non si attribuiscono proposte nuove
alle vecchie chiamate.

## Applicabilità e risposte libere: prove aggiuntive

La sessione principale chiede la **condizione** «se procuratore» prima del valore
«Estremi procura». SOURCE non documenta tale condizione; non viene inferita falsa.
«salta» mantiene la voce aperta e non chiede immediatamente di nuovo gli estremi.

Per isolare i controlli senza mutare o saltare artificialmente i candidate della
sessione FAILED sono state usate altre due conversazioni pulite, stesso modulo,
stesse fonti/configurazione e normale `/answer` della chat:

- `conv-d7d0b3011c024717`, sessione `e4e87d3eab5a46139490a20345902b70`:
  «Forse sono procuratore oppure no, non sono sicuro.» è UNKNOWN, differisce la
  condizione, non compila né esclude il campo. Terminata con «basta», v5 in pausa.
- `conv-ce1a9fabedd14572`, sessione `5c9a8ae1955d486aa686390acfafd311`:
  «non sono procuratore» **fallisce nel planner**, dopo il retry, con turno
  `generation_status=failed`; sessione v3 e tutti i field invariati.
  «Sì oppure no.» produce `compilation_clarify`: v4, nessun field cambiato.
  «No» **fallisce anch'esso nel planner**, nessuna NOT_APPLICABLE applicata.
  «basta» riesce: v5 in pausa senza domanda attiva.

Una riproduzione reale, read-only, di «non sono procuratore» mostra la causa del
contratto: il modello restituisce in entrambi i tentativi
`field_replies=[{"id":"t0.r4.c1","action":"not_applicable",...}]`.
Il contratto richiede **`field_id`**, respinge `id` come extra e segnala
`field_id` mancante. Il contesto planner espone `id`; il retry generico non
corregge la chiave. Il significato negativo viene riconosciuto, ma l'operazione
non supera il parsing. Questa riproduzione non aggiorna la sessione.

| Verifica conversazionale | Esito reale |
|---|---|
| UNKNOWN / SKIP senza valore inventato né immediato stesso field | Osservato |
| «basta», refresh e «riprendi» stessa sessione | Osservato |
| Domanda sulla condizione prima del valore dipendente | Osservato |
| Risposta ambigua «Sì oppure no.» | Chiarimento, zero modifiche ai field |
| Condizione falsa -> NOT_APPLICABLE tramite «non sono procuratore» / «No» | **Fallito nel planner** |
| Valore libero univoco -> USER_PROVIDED | Non raggiunto senza aggirare il blocco o fornire dati aziendali vietati |
| Condizione vera + ricerca/valore | Non eseguito in questa diagnosi |
| READY -> GENERAZIONE / verifica posizioni nel DOCX | Non raggiunto |

Non sono stati forniti manualmente denominazione, forma giuridica, sede,
identificativi fiscali, direttore, ordine o numero albo. Le sessioni aggiuntive
non concorrono ai conteggi della sessione principale, evitando di sommare più
volte le stesse tre informazioni.

## DOCX e integrità

**Nessun DOCX generato**, nessuna bozza incompleta richiesta implicitamente
né esplicitamente. `last_generation=null` in tutte le sessioni.
Non si possono attestare valori materializzati o correttezza delle posizioni
nel renderer: il flusso non è arrivato alla generazione. Non sono state fatte
chiamate finalize per aggirare i problemi aperti.

SHA256 originale prima del test, dopo riavvio e a fine test:
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
Lo snapshot BLOB della sessione ha lo stesso hash. I field letti dal DB in
`mode=ro` coincidono con GET API v20. Tutti i valori RESOLVED hanno SOURCE
con file/chunk, scope, categoria ed estratto; nessun MISSING/DEFERRED ha valore
inventato. Non è stato prodotto un report di generazione per testare la distinzione
USER/SOURCE: nessun valore USER_PROVIDED è stato raggiunto in questo percorso.

## Registro per candidate

La tabella seguente contiene i **36 candidate coinvolti**: 24 con risultato
persistito e 12 del passo abortito. Il CSV e il JSON conservano anche tutti i
279 candidate, incluse le posizioni non ancora visitate.

| candidate | requisito | valore | stato | provenance | evidence |
|---|---|---|---|---|---|
| t0.r0.c1 | Il/La sottoscritto/a | — | PENDING | — | FORM |
| t0.r1.c1 | Data e luogo di nascita | — | PENDING | — | FORM |
| t0.r2.c1 | Codice fiscale | — | PENDING | — | FORM |
| t0.r3.c1 | In qualità di (carica sociale: professionista singolo, professionista associato, legale rappresentante società, procuratore, etc.) | — | PENDING | — | FORM |
| t0.r4.c1 | Estremi procura | — | DEFERRED | — | FORM |
| t0.r5.c1 | Operatore economico | — | DEFERRED | — | FORM |
| t0.r6.c1 | Forma giuridica | — | DEFERRED | — | FORM |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r8.c1 | Sede operativa | — | DEFERRED | — | FORM |
| t0.r9.c1 | Codice fiscale operatore economico | IT01234567890 | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r10.c1 | Partita IVA operatore economico | IT01234567890 | RESOLVED | SOURCE | generalita-mapi.md #-43 |
| t0.r11.c1 | Cellulare + Telefono | — | PENDING | — | FORM |
| t3.r3.c0 | In caso affermativo: | — | DEFERRED | — | FORM |
| t3.r4.c0 | Forma di partecipazione:  | — | DEFERRED | — | FORM |
| t3.r5.c0 | Forma di partecipazione:  | — | DEFERRED | — | FORM |
| t3.r6.c0 | Forma di partecipazione:  | — | DEFERRED | — | FORM |
| t7.r1.c3 | €. 3.710.525,77 | — | PENDING | — | FORM |
| t7.r2.c3 | €. 2.148.313,01 | — | PENDING | — | FORM |
| t7.r3.c3 | €. 385.621,50 | — | PENDING | — | FORM |
| t7.r4.c3 | €. 727.128,39 | — | PENDING | — | FORM |
| t7.r5.c3 | €. 1.443.299,24 | — | PENDING | — | FORM |
| t9.r0.c1 | Nome e cognome: | — | PENDING | — | FORM |
| t9.r1.c1 | Data e luogo di nascita: | — | PENDING | — | FORM |
| t9.r2.c1 | Codice fiscale: | — | PENDING | — | FORM |
| t9.r3.c1 | Residenza: | — | PENDING | — | FORM; step abortito |
| t9.r4.c1 | qualifica professionale: | — | PENDING | — | FORM; step abortito |
| t9.r5.c1 | Ordine professionale di appartenenza: | — | PENDING | — | FORM; step abortito |
| t9.r6.c1 | numero ed anno di iscrizione all’Albo professionale: | — | PENDING | — | FORM; step abortito |
| t9.r7.c0 |  | — | PENDING | — | FORM; step abortito |
| t9.r7.c1 |  | — | PENDING | — | FORM; step abortito |
| t11.r0.c1 | Denominazione dello studio associato: | — | PENDING | — | FORM; step abortito |
| t11.r1.c0 |  | — | PENDING | — | FORM; step abortito |
| t11.r3.c0 | Lo studio associato è costituito dai seguenti liberi professionisti: | — | PENDING | — | FORM; step abortito |
| t11.r3.c1 |  | — | PENDING | — | FORM; step abortito |
| t12.r0.c1 | Nome e cognome: | — | PENDING | — | FORM; step abortito |
| t12.r1.c1 | Data e luogo di nascita: | — | PENDING | — | FORM; step abortito |


Artefatti locali, esclusi da Git, sotto
`backend/data/compilation-audit/real-e2e-deepseek-flash-20261006/`:

- `candidates.csv`, `candidates.json`: candidate, label/requisito, condizione,
  applicabilità, query SOURCE, evidence con testo/ruolo/scope/categoria,
  motivo/proposta persistita, errori, valore, status e provenance;
- `primary-state-final.json`, `primary-revisions-final.json`,
  `primary-conversation-final.json`, `transitions.json`, `summary.json`;
- `retrieved-evidence.json`: i sette chunk ammessi al primo passo, riletti
  read-only dai rispettivi ID. Le SOURCE ammesse sono del progetto corrente
  oppure globali; nessuna SOURCE di un altro progetto;
- `probe-input.json`, `probe-classification-raw.txt`,
  `probe-validation-errors.json`: riproduzione reale isolata del classificatore;
- `probe-planner-input.json`, `probe-planner-raw-{1,2}.txt`,
  `probe-planner-validation-errors.json`: riproduzione reale isolata del planner;
- `applicability-*`, `non-procuratore-*`, cartelle con risposte API/screenshot;
- `original-final.docx`, `original-final-sha256.txt`, `integrity.json`.

I file temporanei del primo browser sono stati persi nell'interruzione
 dell'ambiente; stati, query, errori e transizioni sono stati recuperati dalle
API/revisioni persistite e dai chunk letti senza scrivere SQL. Le due risposte
502 della sessione principale sono osservate nel test, ma non è disponibile
la loro risposta grezza LLM storica. Questo limite di osservabilità è esplicito.

## Conclusione

**LA COMPILAZIONE AUTOMATICA STA FUNZIONANDO SOLO PARZIALMENTE**.
Tre valori standard sono realmente recuperati e validati da SOURCE nello stato,
ma denominazione/forma giuridica non passano per il bucket pertinente; diverse
interpretazioni restano PENDING. L'intero percorso si blocca sul JSON delle
celle decorative, prima di raggiungere società di ingegneria/direttore tecnico.
I controlli UNKNOWN/SKIP/pausa/ripresa funzionano; la negazione di applicabilità
fallisce sul contratto `id`/`field_id`. Nessun DOCX prodotto: materializzazione
non verificata. Nessun bug corretto durante questa esecuzione.
