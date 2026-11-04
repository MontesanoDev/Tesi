# Stabilizzazione del narratore — 4 novembre 2026

**Fix dei messaggi e del recupero UI verificati. Branch utilizzabile per una prova
manuale controllata, non raccomandato per sostituire la demo.** La nuova analisi
Minervino omette i gruppi checkbox e una correzione PEC resta respinta. Nessuna
promozione, push o merge.

Base `62f6152729c4fac49152c33488bfc63a7c264a3c`, solo worktree
`/home/montesano/tesi-narratore-chiarezza-20261031`. Commit finale in `commit.json`
nell'audit. Le prove reali usano nuove sessioni, profilo `sezioni-2026-10-30-r2`,
copie private di database/storage e modello `deepseek-flash`.

## Cause e modifiche

**Contraddizione Labirinto.** Nella prova precedente Paolo Conti era acquisito,
validato e utilizzabile in `t2.r0.c1`. Il router proponeva anche il nome nel ramo
studio associato; la guardia lo respingeva correttamente come `UNRELATED`. Il
backend trattava quel tentativo di destinazione del router come una risposta USER
non accettata: priorità di retry, conteggio dei tentativi e possibile `UNKNOWN`
automatico dopo due rifiuti. La ricevuta concatenava l'acquisizione corretta con
«nulla è stato scritto», anche quando il nome finiva nel DOCX.

Ora l'ipotesi diretta del router respinta come `UNRELATED` rimane nell'audit in
`discarded_proposals`, con origine e motivo distinti. Non genera una decisione
USER, un rinvio o una nuova domanda sul campo estraneo. Gli altri rifiuti e le
ambiguità restano soggetti agli stessi controlli. Il messaggio riferisce il campo
interessato e l'utilizzabilità per la bozza; l'export resta un'operazione separata.
Nessuna modifica a guardia, Gate, writer o criteri SOURCE/USER.

**Errore UI con `4`.** Il frontend permetteva un carattere, mentre `QuestionRequest`
richiedeva almeno due caratteri: HTTP 422 prima del router. Il contratto ora
accetta un carattere; scegliere un numero richiede sempre una destinazione valida,
una ricevuta e i controlli ordinari.

**Retry.** Prima mancava un identificativo persistente dell'invio. La perdita della
risposta HTTP non permetteva di distinguere una decisione già applicata da una
fallita. Ora la UI conserva UUID, testo originale, documento, conversazione e
versione della sessione. La tabella aggiuntiva `chat_submissions` registra richiesta,
stato e risposta; turno chat e ricevuta completata vengono salvati nella stessa
transazione. Il medesimo invio restituisce il risultato salvato; contenuto diverso
con lo stesso UUID o un esito ancora incerto producono 409, senza nuova applicazione.
La UI legge la ricevuta dopo un errore di trasporto e ritrova l'invio al refresh.
Solo un fallimento dichiarato prima delle mutazioni consente un nuovo tentativo
esplicito con un altro UUID. I client senza UUID conservano il contratto precedente.

Limite intenzionale: un arresto dopo la scrittura di sessione e prima del turno
chat lascia un invio interrotto/incerto, con messaggio originale conservato.
Non viene rieseguito automaticamente; occorre verificare/riprendere la sessione.
Non si dichiara atomicità tra tutte le operazioni di sessione e la chat.

## Verifiche offline

- Replay esatto dei tre output reali precedenti Labirinto: router, guardia e
  continuazione, senza rete. **12 scritture**, Paolo Conti nel DOCX; rifiuto della
  destinazione estranea conservato, nessun falso rinvio né messaggio contraddittorio.
- Test nuovi su FORM generici, persone diverse e FTS5/Qdrant: destinazione estranea
  ripetuta, interruzioni prima/dopo il commit chat, richieste concorrenti, payload
  differente con UUID riusato, singolo carattere e recupero della risposta salvata.
- Backend completo **4.381 PASS, 8 SKIP**, 548,25 s; Ruff PASS. Frontend **191 PASS,
  16 file**, build PASS; lint con i due avvisi `typedDraft` preesistenti.
- Quattro E2E desktop esistenti con API simulate PASS. In aggiunta, browser Chromium
  su frontend 5174 e API reale 8001, database/storage temporanei, **LLM simulato**:
  invio `4`, perdita della risposta dopo la persistenza, perdita della prima lettura
  ricevuta, recupero/reinvio con stesso UUID e versione, un solo turno e una sola
  decisione USER, refresh, quarta checkbox nel DOCX e altre tre vuote.
- I primi tentativi del runner browser contenevano un'attesa sul composer vuoto e
  un export che chiudeva la domanda prima del numero: conservati come errori del
  runner; corretta la sequenza, senza patch applicative aggiuntive.
- Rollback in copia di `62f6152`: **12 FAIL** con i nuovi test; riapplicando i file
  del fix **12 PASS**. Hash dei file applicativi e dei test verificati.
  Graphify aggiornato via AST, senza LLM.

## Nuova prova DeepSeek reale

Una sola nuova analisi per FORM, nessuna riestrazione per ottenere output migliori.
Router, guardia, ricevute, API chat/export e writer reali; messaggi di prova
sintetici espliciti, salvati integralmente. Gold escluso dai prompt. Le esportazioni
parziali non richiedono di risolvere tutte le domande.

| Scenario | Scritture nel DOCX | Risultato |
|---|---:|---|
| Minervino, prima conferma e nessuna autorizzazione checkbox | 1 | Solo nome USER; ramo ancora respinto |
| Minervino, conferma esplicita ramo e identità | 55 | Tutti i nove campi del sottoscrittore; checkbox vuote |
| Minervino, correzione PEC e chiarimento | 55 | Correzione respinta, valori precedenti conservati |
| Labirinto, conferma ramo senza autorizzazioni checkbox | 17 | Nessuna selezione |
| Labirinto, scelta esplicita «Società di ingegneria» | 22 | Una casella vera e quattro alternative false tracciate |
| Labirinto, correzione del nome dopo un chiarimento | 23 | Paolo Conti in `t2.r0.c1`, valori precedenti conservati |

**Percorso positivo checkbox:** ricevuta USER `VALUE` del gruppo tipologia,
`selected_options=[1]`, guardia favorevole; nell'XML reale soltanto `p36.cb0`
selezionata. Le quattro alternative dello stesso gruppo sono deselezionate come
effetti tracciati della scelta esclusiva. Modalità di partecipazione, procura,
qualità del firmatario e dichiarazioni non autorizzate rimangono vuote. Il negativo
precedente ha zero selezioni, pur avendo i dati societari SOURCE.

**Minervino:** Leonardo Montemurro, Lecce (LE), 14 novembre 1982, Bari (BA),
Amedeo 24, CF `MNTLRD82S14E506X`, carica «amministratore unico e rappresentante
legale». Nome USER e dati SOURCE sono distinti; due conferme di applicabilità
separate. La frase anagrafica originale è conservata e non viene salvata come nome.
La nuova analisi ha restituito `choice_groups={}`. La richiesta di selezionare la
quarta opzione è stata instradata soltanto sulle condizioni di ramo e identità:
nessuna ricevuta `choice`, quindi nessuna checkbox scritta. È un'omissione della
nuova generazione e del routing osservato; non viene attribuita al fix dei messaggi
senza un confronto causale. Non è stata introdotta una ricostruzione forzata.

La PEC societaria è stata proposta sul campo del sottoscrittore e respinta per
ambito ambiguo. Dopo il chiarimento, la guardia ha ancora respinto quel campo; per
la PEC societaria era favorevole, ma il router aveva estratto una citazione
anaforica («Usa questo stesso recapito…») senza il valore letterale: il controllo
USER ha bloccato la scrittura. Nessuna patch speculativa; il flusso Minervino con
correzione riuscita nella seconda bozza **non è dimostrato in questa campagna**.

**Labirinto:** il primo tentativo di nome puntava ancora al ramo studio associato:
la guardia lo ha correttamente respinto, senza acquisire Paolo in quel ramo. Un
chiarimento sul campo iniziale ha prodotto proposta accettata, messaggio «Dati
acquisiti per la bozza» e nome effettivo nel DOCX. Il routing conserva contesti poco
distintivi tra campi omonimi. La domanda sul ramo studio associato viene riproposta
nonostante il testo USER lo escluda: ridondanza residua, non risolta in questo fix.

Otto DOCX verificati nelle destinazioni XML reali: sei delle nuove prove, uno del
replay e uno del browser con provider simulato. Tutte le scritture del report
sono presenti nelle rispettive posizioni. Nessuna selezione o scrittura indebita
nelle destinazioni verificate; tre aggiornamenti richiesti restano mancanti su
Minervino (una checkbox e due PEC). Non è un conteggio gold dell'intero FORM.
«BOZZA NON VERIFICATA» sempre presente. Bozze precedenti identiche ai file ancora
scaricabili dallo storage; originali copiati immutati. Pausa/ripresa sulla stessa
sessione conserva esattamente ricevute e valori USER, senza aggiornare sessioni
storiche. Il percorso pausa/ripresa reale usa il controllo di dominio, mentre il
refresh browser è coperto dalla prova con provider simulato.

Nei checkpoint di dialogo salvati: Minervino quattro presentazioni su due chiavi,
Labirinto cinque su due chiavi, una sola domanda per presentazione. Sono snapshot
del runner, non una misura del numero di visualizzazioni UI. Il ramo studio
associato riproposto quattro volte su Labirinto è una ridondanza effettiva.

| FORM | Chiamate | Token totali | Somma tempi provider | Latenza endpoint USER |
|---|---:|---:|---:|---:|
| Minervino | 21 | 723.403 | 403.88 s | 8.14–13.02 s, 4 messaggi |
| Labirinto | 15 | 166.902 | 112.48 s | 3.64–4.10 s, 4 messaggi |

Totale **36 chiamate / 890.305 token**
(784.998 input, 105.307 output),
516.36 s come somma delle durate provider, che comprende
chiamate di analisi parallele e non rappresenta il tempo totale trascorso.
Inclusa una ripetizione di formato del router Minervino: HTTP riuscito non
significa output immediatamente utilizzabile. Nessuna chiamata oltre le due
nuove analisi e i dialoghi descritti; limite preventivo 52, usate 36.
Tempi degli export non acquisiti sistematicamente.

Il confronto causale sul messaggio usa il replay identico e i test prima/dopo.
Le nuove analisi DeepSeek differiscono dagli output di `62f6152`: i conteggi 55 e
23 non sono una misura di miglioramento statistico rispetto alle precedenti bozze.
Non è stimata un'accuratezza globale dei FORM né un risparmio di token.

## Consegna, rollback e limiti

Pronto per **prova manuale controllata**, con questi limiti espliciti. **Non
promuovere nella demo**: resta da rendere affidabile la scelta checkbox Minervino
e da verificare il routing delle correzioni tra campi omonimi. Le guardie hanno
impedito scritture ambigue; l'assenza di violazioni non dimostra completezza.

Schema DB aggiuntivo creato da `init_database()` all'avvio, nessun aggiornamento
retroattivo delle sessioni o delle ricevute storiche. Il rollback al codice base
ignora la nuova tabella: avvio e lettura di una conversazione verificati su una
copia del DB con schema nuovo. Conservare una copia del DB prima dell'eventuale adozione.
Rollback del codice verificato in copia; nessun reset del worktree operativo.
Commit isolato, esclusi rinomini/esempi e modifiche pregresse dell'utente.

Audit locale: `backend/data/compilation-audit/narratore-stabilizzazione-20261104/`.
Contiene protocollo, prompt/schema, output grezzi, stati, ricevute, DOCX, test,
metriche e confronti di integrità; credenziali escluse. Backup separato verificato:
`/home/montesano/tesi-backups/narratore-stabilizzazione-20261104/`.
Gli artefatti locali sono ignorati da Git e richiedono questo backup.

Istanza ordinaria 5173/8000 mai usata per le prove. Controlli di integrità di DB
originali, Git ordinario, SOURCE copiate e tag congelato registrati nell'audit.
I soli processi temporanei di verifica 5174/8001 vengono fermati alla consegna.
Nessun push, merge o promozione; lavoro fermato al rapporto.
