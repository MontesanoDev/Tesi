# INDEX-01, contesto USER, reasoning e soci B0-03 — 17 ottobre 2026

**Zero nuove chiamate generative.** Riprodotto offline INDEX-01 isolando i soli
metadati root inattesi, senza modificare schema, gate, coverage, FORM o writer.
Implementato un passaggio ristretto del contesto USER registrato dalla chat.
Consultati documentazione ufficiale DeepSeek e metadati del modello con un solo
GET /models, non una generazione. Nessun commit o integrazione delle viste E1.

[Misure e scenari](benchmarks/2026-10-17-root-user-reasoning.json),
[bundle](benchmarks/2026-10-17-root-user-reasoning-audit.tar.gz),
[checksum](benchmarks/2026-10-17-root-user-reasoning-audit.tar.gz.sha256),
[controlli finali](benchmarks/2026-10-17-root-user-reasoning-checks.json).
Raw: `backend/data/compilation-audit/root-user-reasoning-20261017-01/`.
Archivio: 149 file, 3.516.747 byte; SHA-256
`24799ce17ac5baa66c63367ddda807e97cf72f0a13eaab90f71b7770021c987f`.


## 1. INDEX-01: schema, gate e DOCX dopo la sola quarantena dei metadati

Conservata la risposta originale, con hash immutato. Il parsing Pydantic originale
riproduce due soli errori root, `extra_forbidden` su `proposal_stage` e `project_id`.
Verificato che i loro valori coincidono con quelli dell'input storico. Nel solo
replay sono separati in `quarantined-root-metadata.json`. Tutti gli altri valori
JSON, citazioni, ID, fatti, binding e condizioni rimangono esattamente uguali.

**Il JSON risultante supera lo schema completo CoverageAwareProposal:** 27 fields,
20 facts, due conditions, un binding, due clarifications e 25 record coverage.
Non è stato aggiunto un filtro generalizzato al parser di produzione: l'originale
resta un fallimento storico e proprietà root estranee restano vietate.

### Risultati dei validatori invariati

| Passaggio | Numero |
|---|---:|
| Proposte SOURCE grezze | 27 |
| Valori conformi al gold nelle proposte | 25 |
| Proposte con grounding locale superato | 19 |
| Di queste conformi al gold | 18 |
| Rifiuto FORM | 1 |
| Collegamento persona–ruolo non superato | 7 |
| Condizioni semantic ancora unknown | 2 |
| RESOLVED | 0 |

p15.s0 viene respinto perché la citazione contiene solo marker/punteggiatura.
Sette dati di Elisa — qualifica, CF, Ordine, sezione, provincia, data e numero
iscrizione — restano bloccati: binding e valori citano record/chunk che il gate
non collega. Il solo nome del direttore passa. I rifiuti completi sono
nell'audit del replay, senza reinterpretarli come valori risolti.

Il dato p41.s1, indirizzo completo dove il gold chiede il comune Bari, passa
invece i controlli letterali e arriva al writer nel test con conferme. Questo
è un limite semantico osservato della destinazione, non una correzione introdotta
nel replay. Perciò **19 valori validati non significa 19 valori conformi**.

### Valori che arrivano materialmente al DOCX con le due conferme USER

Sono tutti SOURCE. Senza quelle conferme la selezione rimane bloccata.

| Destinazione | Richiesta del gold | Valore scritto nel replay | Conforme |
|---|---|---|---|
| p14.s1 | Operatore economico | Mapi Ingegneria S.r.l. | Sì |
| p15.s1 | Provincia sede | BA | Sì |
| p15.s2 | Telefono | +39 080 000 2040 | Sì |
| p15.s3 | Fax | +39 080 000 2041 | Sì |
| p16.s0 | Email | segreteria@mapi-ingegneria.demo | Sì |
| p16.s1 | PEC | mapi.ingegneria@pec.demo | Sì |
| p16.s2 | PIVA | IT01234567890 | Sì |
| p17.s0 | CCIAA | Bari | Sì |
| p17.s1 | Registro Imprese | 01234560981 | Sì |
| p40.s0 | Denominazione | Mapi Ingegneria S.r.l. | Sì |
| p41.s0 | PIVA società | IT01234567890 | Sì |
| p41.s1 | Comune sede società | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | **No** |
| p42.s0 | Provincia sede società | BA | Sì |
| p42.s1 | Via società | Via Giovanni Amendola | Sì |
| p42.s2 | Civico società | 172/C | Sì |
| p42.s3 | Telefono società | +39 080 000 2040 | Sì |
| p42.s4 | Email società | segreteria@mapi-ingegneria.demo | Sì |
| p42.s5 | PEC società | mapi.ingegneria@pec.demo | Sì |
| p51.s0 | Direttore tecnico Elisa Romano: Nome | Ing. Elisa Romano | Sì |

### Due scenari separati fino all'export

Tutti e due riusano la stessa risposta e la stessa analisi storica senza USER.
SQLite/storage sono copie private in `.tools/index01-root-replay-20261017-01/`.
Non è stato interrogato un modello per router, narratore o interpretazione.

| Scenario software | Conferme di partecipazione | Esito |
|---|---|---|
| Senza conferme | Nessuna | Tentativo di selezionare i 19: HTTP409, conferme richieste; copia vuota soltanto con export parziale/allow_empty espliciti |
| Con conferme archiviate | Due risposte USER registrate con apply_replies | 19 valori scritti, tutti SOURCE; 18 conformi su 60 target; nessun valore USER assegnato ai campi |

Nel secondo scenario le due risposte sono riprese dall'acquisizione INDEX-03.
La corrispondenza fra i vecchi e nuovi ID di condizione è **dichiarata nel test**
e controllata sul paragrafo FORM di origine: c_soc→c_branch_soc, c_oe→c_op.
Non è un trasferimento automatico di decisioni fra sessioni nella produzione.
I testi USER sono letterali e già archiviati, non nuovi nomi o scelte inventati.

Gli slot della domanda sono quelli del backend; il piano di domanda e le reply
tipizzate sono dati controllati del test. Il narratore e l'interprete LLM non
sono valutati. Dopo la registrazione, l'export diretto di sessione usa selezione
esplicita dei 19 campi, conferme effettive e rivalidazione delle SOURCE. Nessun
gate viene aggirato, nessuna condizione ignota resa vera senza la risposta USER.

Il risultato non va aggiunto come un quarto run di qualità a E1 e non trasforma
INDEX-01 in un successo del provider. È un controfattuale locale che identifica
quanto recupera la sola separazione dei metadati.

[Word senza conferme](<../nuovi dati/domanda-iscrizione.INDEX01-ROOT-REPLAY-SENZA-CONFERME.docx>),
[PDF](<../nuovi dati/domanda-iscrizione.INDEX01-ROOT-REPLAY-SENZA-CONFERME.pdf>),
[Word con conferme](<../nuovi dati/domanda-iscrizione.INDEX01-ROOT-REPLAY-CON-CONFERME.docx>),
[PDF](<../nuovi dati/domanda-iscrizione.INDEX01-ROOT-REPLAY-CON-CONFERME.pdf>).
Tutti parziali, ready_for_submission=false. Il secondo contiene l'errore noto
p41.s1 e non è un nuovo gold. Nessun campo dei soci o firmatario recuperato.

Scorer B0 invariato: tutte le 267 destinazioni per Word, prove materiali sul
DOCX e altre 15 parti ZIP preservate. LibreOffice dieci pagine ciascuno;
viste 1/3/10 del documento con conferme. Firma sull'ultima pagina quasi vuota,
nessuna modifica al layout o certificazione Microsoft Word.

## 2. Decisioni USER: cosa mancava e cosa viene ora trasmesso

### Catena osservata

Il router iniziale produce compile, poi viene creata la sessione. La route della
chat salva un turno con `question` originale, `compilation.session_id` e action
start. Solo dopo il frontend richiede l'analisi globale. Prima dell'intervento
_prepare/build_global_input non leggevano quel turno: la richiesta globale
manteneva user_values vuoto e nessuna traccia della scelta USER nella chat.

Il testo del messaggio è registrato, ma **non esiste un'estrazione strutturata
iniziale già approvata** del tipo firmatario=X/partecipazione=Y. Una citazione
USER e una decisione tipizzata confermata sono quindi oggetti distinti.

### Intervento implementato, circoscritto al trasporto

[compilation_user_context.py](../backend/app/compilation_user_context.py) legge
soltanto i turni start riferiti all'esatta sessione, con join su conversazione e
progetto. Non copia risposte AI o cronologia generica, né messaggi di altre
sessioni/moduli. Le richieste sono trasmesse letteralmente come recorded_request.
Non vengono trasformate dal codice in firmatari, partecipazioni o valori.

Le eventuali risposte già accettate nel proprio stato vengono trasmesse come
registered_decision, solo con provenienza USER, destinatario esistente e
coerenza col registro di condizioni/campi/gruppi. Rinvii, risposte ambigue,
provenienza MODEL e scope inesistenti sono esclusi. Effetti booleani derivati
non diventano nuove decisioni individuali: viene conservata la scelta del gruppo.

_prepare passa queste ricevute come `user_context` separato. `user_values` resta
vuoto: non sono assegnazioni automatiche. Fatti ed evidenze SOURCE sono invariati.
L'istruzione aggiuntiva della sola richiesta **con** USER distingue citazioni,
decisioni registrate, alternative e prove SOURCE. Il codice non approva il senso
di un messaggio libero: il modello deve ancora riconoscere le indicazioni
esplicite e pertinenti; i gate e le domande continuano a essere necessari.

Cambiano solo il lettore delle ricevute, la costruzione dell'input e il prompt
condizionale di questo canale USER. TASK B0 di base, FORM, output schema e
coverage restano identici. Nessun cambiamento del router, dei validatori o del
writer, nessuna migrazione o rianalisi automatica delle sessioni storiche.

### Verifica e separazione dei confronti

- Scenario Minervino senza messaggi USER associati: **input e request identici
  esattamente agli artefatti B0**, incluso system prompt.
- Scenario distinto con T0 archiviato: prima viene salvato un vero turno start
  nella sessione di test; _prepare lo rilegge e lo inserisce come citazione.
  FORM, SOURCE, schema, reading plan e parametri invariati; solo il contesto USER
  e le istruzioni necessarie a distinguerlo vengono aggiunti.
- Test su negazioni, scelta del firmatario ancora aperta, alternative e
  rettifiche: il testo rimane letterale, il codice non seleziona una persona.
- Progetti/sessioni estranei, normali turni e risposte AI esclusi; decisioni
  accettate sottoposte a controlli di provenienza e ambito.

Le richieste con USER sono salvate come **NOT-SENT**. Nessun miglioramento della
qualità reale del modello con questo canale è misurato. Anche un generico
«compila» può comparire come richiesta registrata: non contiene una decisione
che il backend possa inventare. Contraddizioni richiedono chiarimento.

La lettura avviene al momento dell'analisi: messaggi successivi non aggiornano
retroattivamente una risposta già acquisita. Il cambiamento non riapre le nove
misure storiche e non aggiunge USER al benchmark congelato senza USER.

## 3. Reasoning: opzioni verificate e confronto minimo proposto

Il GET ufficiale `/models` risponde HTTP200 per il profilo effettivo:
`deepseek-flash`, nome corrente DeepSeek-V4.1-Flash, livelli attivi low/high/max,
default high, contesto 1.048.576 e massimo output dichiarato 393.216. È discovery,
non una chiamata generativa; non fissa retroattivamente il backend del 16 ottobre.
Acquisizione completa non riservata in provider-model-metadata.json.
[Metadati documentati](https://api-docs.deepseek.com/api/list-models/).

Nella Chat Completions API il controllo esplicito è thinking.type enabled/disabled;
reasoning_effort ammette none/low/high/max e minimal è un alias di low. Il budget
separato di soli token reasoning non risulta documentato. La temperatura non ha
effetto con thinking attivo: la modalità modifica anche il campionamento effettivo.
[Documentazione ufficiale](https://api-docs.deepseek.com/api/create-chat-completion/).

B0 inviava già **thinking enabled e reasoning_effort low**: non esiste qui un
livello attivo inferiore documentato da provare. Il limite 49.152 è rimasto
invariato; non è stato aumentato al limite massimo del provider.

Nel profilo progetto lo switch thinking è false, ma il percorso globale forza
ancora true per DeepSeek; il runner lo controlla invece esplicitamente. Questo
comportamento runtime **non è stato modificato** in questa attività: serve
misurare prima il confronto chiesto, preservando B0.

### Più piccolo confronto controllato: un pilot di due chiamate fresche

| Braccio proposto | Configurazione | Stato |
|---|---|---|
| A | FORM B0 completo, thinking enabled, effort low | Body pronto, non inviato |
| B | Identico FORM/input/prompt, thinking disabled, effort omesso | Body pronto, non inviato |

Stessi SOURCE, nessun USER, output schema/coverage, max_tokens=49.152,
temperature=0.1, timeout=300 s, validatori e writer. Una chiamata globale per
braccio, senza retry o completamenti. L'omissione di effort nel braccio B evita
parametri che possano riattivare o contraddire il controllo di modalità.

I due body, generati col runner attuale, differiscono solo per questi parametri
della modalità; le altre proprietà e tutti i messaggi sono identici. Confronto
fra modalità operative, non isolamento di un presunto contatore interno del
reasoning. Nessun parametro non documentato utilizzato.

Acquisire A e B nello stesso intervallo, anche se esiste B0 storico: questo
riduce le differenze di data/alias/cache senza promettere che spariscano.
Conservare entrambe le risposte, errori, finish_reason, usage/cache, tempi,
valori proposti conformi, rifiuti locali e applicabilità/export. Senza conferme
USER non forzare valori condizionati nel DOCX; eventuali continuazioni devono
avere un copione identico e dichiarato, restando separate dal confronto iniziale.

Due chiamate sono un pilot di fattibilità, non equivalenza di qualità o stima
robusta di affidabilità. Un'eventuale replica maggiore va fissata prima di
eseguirla, senza scartare gli esiti negativi. **Pilot solo proposto, non eseguito.**
I test con USER sono un'altra variabile e non entrano in questo A/B.

## 4. B0-03 soci: distinguere ruolo, prova del valore e scrivibilità

Controllate singolarmente le 24 destinazioni dei tre soci, con assegnazioni,
fatti, citazioni originali, audit dei binding e provenienza dei chunk.

| Controllo | Risultato osservato |
|---|---:|
| Valori grezzi conformi al gold | 24/24 |
| Prove dei fatti localmente grounded | 23/24 |
| Prova del fatto insufficiente nella quote scelta | 1/24, p46.s0 |
| Binding personali respinti | 3/3 |
| Destinazioni bloccate anche dal binding | 24/24 |
| Valori con tutte le prove negli stessi chunk grezzi citati dal binding | 15/24 |
| Valori con almeno una prova in altri chunk | 9/24 |

### Tre binding: limite dei formati di attribuzione proposti

Per ogni socio il modello cita il titolo «Soci della società ...» e una riga
della tabella in -54, indicando source_role «socio». Ogni citazione deve contenere
il ruolo letterale delimitato: il titolo usa il plurale Soci; la riga della
persona non riporta il ruolo. Le tre associazioni vengono respinte già qui.

Per una lettura umana la tabella con titolo documenta la compagine sociale:
non è assenza di soci nella KB. Il gate riconosce però attribuzioni letterali
persona–ruolo in formati limitati, non un generico titolo di tabella ereditato
dalle righe. Rimuovere il vincolo o marcare il binding valido a mano sarebbe
un allentamento: non è stato fatto.

### La prova insufficiente: rifiuto corretto

p46.s0 propone Bari (BA) attraverso il fatto condiviso f_elisa_provincia, ma cita
la frase narrativa -55 che non contiene quel valore completo. La tabella -54
lo contiene, ma non è la quote scelta per quel fatto. Il rifiuto del fatto è
fondato rispetto alla citazione effettiva e si somma al problema di binding.
Il medesimo fatto blocca anche la provincia del direttore p53.s2, fuori dalle
24 destinazioni dei soci: non contarla come un secondo socio o un fatto distinto.

### Gli ulteriori collegamenti fra chunk

Nove valori citano almeno un chunk diverso da -54, usato nei binding proposti.
La corrispondenza degli ID di chunk non è comunque un'attribuzione semantica:
15/24 è un controllo strutturale, non un numero di campi che diventerebbero
scrivibili dopo una correzione. Gli attuali gate chiedono anche record persona,
ruolo e citazioni coerenti.

Quindi non abbiamo 24 rifiuti corretti per mancanza del dato né 24 errori da
rimuovere: abbiamo tre binding non accettabili per il contratto attuale,
23 prove fattuali localmente valide, una citazione realmente insufficiente e
ulteriori legami fra chunk da dimostrare. Nessun guadagno controfattuale è
attribuito a una semplice correzione di singolare/plurale.

## 5. Verifiche, limiti e continuità

**79 test mirati passati in 9,33 s; 2.304 backend passati in 168,46 s; Ruff
completo passato.** Sono test software con provider simulati, non prove di
qualità di nuove risposte reali. Iniziale Ruff con otto diagnostiche F401/F811
sugli import fixture del nuovo file test, risolte con alias; log conservato.
Un'acquisizione offline iniziale ha omesso api_key nel costruttore di AISettings:
corretta usando l'oggetto minimo necessario per costruire il body senza rete.
Una sessione abbandonata resta nel solo DB privato, nessuna chiamata ripetuta.

Tutte le funzioni di validazione di compilation_global sono AST-identiche alla
versione congelata; cambiano soltanto build_global_input e global_request per
il contesto USER. Contratto/schema, ruolo-record, coverage, validator DOCX e
writer invariati. Frontend non modificato e suite non ripetute. Originali,
fixture e precedenti audit conservati. Nessuna migrazione, commit o push.

Il bundle contiene codice, patch, script replay, log, analisi dei 24 soci,
risposte originali/riprodotte, ricevute, DOCX/PDF e body NOT-SENT del pilot.
Esclude DB, credenziali e runtime. Il replay completo dei servizi usa la copia
SQLite privata citata nello script: non viene dichiarato autosufficiente il
bundle per quel passaggio. Gli input, il DOCX originale e le tracce conservate
permettono di riesaminare separatamente schema, gate e confronto materiale.

**Decisione:** coverage rimane invariato; B0 resta il riferimento e la
compattazione FORM è ferma. Risolto il trasporto del contesto USER registrato,
non dimostrata la sua qualità generativa. La sola quarantena root recupera
l'audit ma non rende tutti i valori corretti o scrivibili. Prossimo passo
proposto: decidere sul pilot thinking con i due body pronti, senza avviarlo
implicitamente e mantenendo separata qualsiasi futura prova con USER.
