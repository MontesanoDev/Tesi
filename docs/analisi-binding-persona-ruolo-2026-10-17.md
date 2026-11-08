# Catena persona–ruolo: proposte, prove e rifiuti osservati

17 ottobre 2026. Risposta alle cinque domande dell'utente sui soci B0-03 e sui
dati personali di INDEX-01. Analisi dei soli artefatti già acquisiti e del
codice: **nessuna chiamata al provider, nessuna nuova rivalidazione o export,
nessuna modifica a codice, prompt, schema, validatori o writer**.

Le proposte dei soci sono conformi al gold sintetico, ma la catena di prove
proposta dal modello non è accettata dal contratto attuale. Il backend non
riconosce il legame titolo–righe della tabella e non unisce automaticamente
prove di ruolo e valori in chunk diversi. Esiste anche una citazione davvero
insufficiente rispetto al valore proposto: i motivi vanno tenuti distinti.

[Estratti verificabili e hash dei file consultati](benchmarks/2026-10-17-binding-persona-ruolo.json).
[Replay precedente, incluse condizioni ed export](replay-index01-user-reasoning-2026-10-17.md).

## 1. Chi costruisce il binding

È il modello a proporre tutti questi collegamenti nella risposta JSON:

```text
fields[candidate_id].fact_id    → facts[fact_id]
                                subject, entity, property, value, evidence

fields[candidate_id].binding_id → bindings[binding_id]
                                form, required_role, source_role, evidence
```

`SubjectBinding` **non contiene un campo subject**: il soggetto viene letto
dal fatto associato al campo. L'ID `b_luca_socio` è un riferimento scelto dal
modello; il suo nome non prova che il binding appartenga a Luca. La verifica
persona–ruolo avviene quando il backend combina fatto, binding e destinazione.
Non esiste in questo passaggio un registro indipendente di persone e ruoli
che completi gli abbinamenti omessi dalla risposta.

Contratti: [SharedFact](../backend/app/compilation_global_contract.py:30),
[SubjectBinding e binding_id](../backend/app/compilation_global_contract.py:152).
Il [prompt](../backend/app/compilation_global.py:185) richiede esplicitamente
il binding per i fatti personali e specifica i formati supportati e il vincolo
che ruolo e valore appartengano allo stesso chunk.

Il backend esegue due passaggi distinti:

1. [_subject_bindings](../backend/app/compilation_global.py:1091): rilegge il
   FORM e le citazioni SOURCE. Il ruolo richiesto deve essere presente nella
   quote FORM; **ogni quote SOURCE**, individualmente, deve contenere il ruolo
   attestato letterale. Una General KB non può attestarlo. La normalizzazione
   considera Unicode NFC, maiuscole/minuscole e spazi; non singolare/plurale,
   sinonimi o equivalenze professionali.
2. [_binding_check](../backend/app/compilation_global.py:1134): per ciascun
   campo controlla validità del binding, contesto FORM ammesso, uguaglianza dei
   ruoli e validità del fatto. Poi cerca l'attribuzione esplicita di quel ruolo
   al `subject` del fatto e verifica che tutti i chunk delle prove del valore
   siano supportati. Non basta trovare una persona o un ruolo da qualche parte
   nello stesso documento.

Sono riconosciuti l'attributo affermativo `ruolo: persona` a inizio clausola,
l'intestazione Markdown `### persona - ruolo` e la riga `RUOLO persona - dettagli`
con ruolo in maiuscolo. Negli ultimi due casi i valori devono stare nel record
della persona, delimitato dalla successiva intestazione/riga di attributi.
[Formati effettivi e confini](../backend/app/compilation_role_records.py:27),
[controllo delle quote nel record](../backend/app/compilation_role_records.py:64).
Una normale tabella Markdown con il ruolo espresso soltanto dal titolo non
è uno di questi formati.

## 2. B0-03: Luca Ferri socio, qualifica e numero albo

**Informazione proposta.** Il modello propone `Ingegnere` per `p43.s1` e `7294`
per `p44.s2`, entrambi per `subject: Luca Ferri`, tramite i fatti
`f_luca_qualifica` e `f_luca_numero`. Entrambi sono conformi al gold.

**Prova del valore.** Per entrambi cita questa riga, presente letteralmente
nel chunk `-54` di `integrazione-company.md`:

```text
| Luca Ferri | 30% | Ingegnere | Ordine degli Ingegneri di Bari | A | Bari (BA) | 21/03/2012 | 7294 | FRRLCU80A01A662K |
```

**Prova del ruolo proposta.** I campi rimandano al binding `b_luca_socio`:

- FORM `paragraph:42`: «e composta da (riportare nominativo, qualifica
  professionale e C.F. di ogni socio):»;
- `required_role: socio`, `source_role: socio`;
- due quote SOURCE nel chunk `-54`: il titolo
  `## 3. Soci della società al 15 ottobre 2026 — scenario sintetico`
  e la riga completa di Luca riportata sopra.

La tabella, con titolo e intestazioni delle colonne, è presente nell'input
LLM effettivo; non è stata esclusa dal retrieval. È una fonte Company KB
con ruolo `source`, distinta dal FORM e dal gold.

**Controllo che fallisce.** In `_subject_bindings`, il primo titolo non contiene
la parola intera `socio`: contiene `Soci`. Il controllo solleva
`Ruolo attestato assente nell'estratto SOURCE`. L'esecuzione del binding si
ferma già su questa prima quote. Anche la seconda quote non contiene `socio`,
ma questo secondo difetto è rilevato dalla lettura del testo, non da un secondo
errore emesso dal ciclo interrotto.

Il binding risulta `REJECTED`; `_binding_check` restituisce al campo
`Binding di ruolo rifiutato`. I due fatti restano `GROUNDED_PROPOSAL`, mentre
i campi diventano `REVIEW_REQUIRED` con valore non selezionato. Il writer non
è la causa di questo blocco.

**Interpretazione.** La tabella documenta, nello scenario sintetico, sia la
compagine sociale sia i dati professionali. Il blocco non dimostra che la KB
sia priva di queste informazioni. È un limite del modo in cui il modello
presenta la relazione titolo–riga e del modo in cui il backend può verificarla.
Il modello ha comunque proposto un formato che il prompt non ammette; non
si tratta di un binding corretto nel contratto corrente respinto per caso.

Il medesimo errore si ripete per i binding di Elisa Romano e Andrea Greco.
Sull'insieme delle 24 destinazioni dei soci:

| Misura osservata | Numero |
|---|---:|
| Valori proposti conformi al gold | 24 |
| Proposte con fatto localmente grounded | 23 |
| Proposta con citazione insufficiente per il valore | 1 |
| Binding respinti | 3 |
| Campi bloccati anche dal binding | 24 |
| Stato finale REVIEW_REQUIRED | 23 |
| Stato finale REJECTED | 1 |
| Prove del valore tutte negli stessi chunk grezzi del binding | 15 |
| Almeno una prova del valore in chunk diverso dal binding | 9 |

I 15 collegamenti nello stesso chunk non sono 15 scritture recuperabili già
dimostrate. Il controllo successivo richiede anche un record persona–ruolo
riconosciuto. Correggere soltanto `Soci/socio` non è una soluzione verificata.

## 3. INDEX-01: ordine professionale di Elisa, direttore tecnico

Questi controlli provengono dal replay offline precedente: l'originale INDEX-01
si era fermato prima, allo schema root. Il replay ha isolato soltanto
`proposal_stage` e `project_id`, conservando identici tutti i record annidati.
Non riscriviamo l'esito della chiamata originaria.

**Informazione proposta.** Per `p53.s0`, «iscritto all'Ordine/Collegio
professionale», il modello propone `Ordine degli Ingegneri di Bari` mediante
`f_ordine`, con `subject: Ing. Elisa Romano` e `binding_id: b_elisa`.

**Prova del valore.** Il fatto cita nel chunk `-55`, `integrazione-company.md`:

```text
- **Elisa Romano:** direttore tecnico di Mapi Ingegneria S.r.l.; ingegnere, Ordine degli Ingegneri di Bari, sezione A, iscritta dal 18 maggio 2015 con numero 8421.
```

**Prova del ruolo.** Il binding cita invece, dal chunk `-45` di
`generalita-mapi.md`, `### Ing. Elisa Romano - direttore tecnico`.
Il FORM è `paragraph:50`, «la quale ha come Responsabile della Progettazione
(per le società di professionisti) o Direttore Tecnico (per le società di
ingegneria):». I ruoli sono `Direttore Tecnico` e `direttore tecnico`:
la differenza di maiuscole è ammessa.

**Controllo che fallisce.** Il binding preso da solo passa, così come il fatto.
Quando `_binding_check` esamina le prove del binding, legge solo `-45`. Non
trova in quel chunk nessuna quote del valore proposta dal fatto, che cita `-55`.
Non viene quindi registrata un'attribuzione supportata per il chunk `-55`:
`record_attributions: []`. Errore preciso:

```text
SOURCE non attribuisce esplicitamente ruolo e soggetto nello stesso chunk del valore
```

Il campo rimane `REVIEW_REQUIRED`. La frase dell'errore descrive un mancato
riscontro nella catena citata, non l'esito di una ricerca semantica esaustiva
in tutte le SOURCE. Il testo di `-55` **nomina effettivamente persona, ruolo
e ordine nella medesima frase**, ma non è la prova di ruolo scelta dal binding
e ha un formato narrativo non supportato dal riconoscitore di record.

Inoltre `-45` contiene già l'ordine professionale e il numero di iscrizione
di Elisa: per questo esempio il materiale necessario era disponibile anche
nel record della fonte usata dal binding, ma il modello ha scelto una diversa
citazione per il valore. Non manca quindi un dato da aggiungere alla KB.
Il nome `p51.s0`, citato da `-45` come il suo binding, supera invece questo
controllo nel replay: il comportamento non è un rifiuto generale della persona.

Complessivamente, sette dati personali del direttore sono bloccati in INDEX-01,
come documentato nel rapporto del replay. Anche superando il binding, l'applicabilità del ramo
societario resta una decisione distinta: `c_branch_soc` è `unknown` senza
conferma USER. Prova del dato e autorizzazione alla scrittura non coincidono.

## 4. B0-03: provincia di Elisa, citazione insufficiente

**Informazione proposta.** `p46.s0` propone `Bari (BA)` attraverso
`f_elisa_provincia`, `subject: Elisa Romano`, `property: provincia`.

**Prova citata.** La stessa frase narrativa di `-55` riportata nel caso
precedente, che dice «Ordine degli Ingegneri di Bari» ma non contiene
`Bari (BA)`. La riga di Elisa nella tabella `-54` riporta il valore completo,
ma il modello non la cita per questo fatto.

**Controllo preciso.** In [_shared_facts](../backend/app/compilation_global.py:678)
prima viene riletta la quote reale, poi viene chiamato
`source_span(quote, fact.value)`. È questo secondo controllo a sollevare
`Estratto/valore non presente nella SOURCE`. Il fatto diventa `REJECTED` e il
campo riceve `Fatto SOURCE assente o rifiutato`, oltre all'errore del binding
dei soci già descritto. Stato finale del campo: `REJECTED`.

`Bari (BA)` compare anche all'inizio del chunk `-55`, ma nel troncone della
riga tabellare di Andrea. Cercarlo genericamente nell'intero chunk eliminando
il vincolo della quote rischierebbe proprio l'attribuzione alla persona sbagliata.

**Interpretazione.** Rifiuto fondato rispetto alla prova effettivamente
proposta. Il valore coincide con il gold e compare altrove nella KB, ma
la citazione scelta non lo dimostra integralmente. Non è una ragione per
allentare il controllo su valore e citazione. Lo stesso fatto è riusato nella
provincia del direttore `p53.s2`: due destinazioni bloccate, un solo fatto errato.

## 5. Diagnosi e limiti

| Caso | Fatto osservato | Interpretazione motivata |
|---|---|---|
| Soci, titolo e righe in `-54` | Il ruolo singolare deve comparire in ciascuna quote; titolo plurale e righe prive del ruolo vengono respinti | Limite della rappresentazione proposta e della verifica di relazioni tabellari, con dati disponibili |
| Elisa, ruolo `-45` e ordine `-55` | Binding e valore citano chunk differenti; nessun supporto del valore viene registrato dal binding | Catena di citazioni incompleta rispetto al contratto; selezione delle prove del modello e verifica backend troppo limitata per questa relazione documentata |
| Elisa, provincia `Bari (BA)` da frase `-55` | Il valore completo manca nella quote scelta | Rifiuto corretto della prova; usare altre occorrenze senza attribuzione sarebbe scorretto |
| Ramo societario non confermato | Condizione di partecipazione sconosciuta | Blocco indipendente di applicabilità; i dati aziendali non sostituiscono la decisione USER |

Non è dimostrato che tutti i valori conformi al gold diventerebbero scrivibili
dopo un cambiamento dei binding. Non sono stati costruiti binding alternativi,
aggiunte citazioni o simulati esiti favorevoli. Nessun guadagno quantitativo
è assegnato a una correzione non eseguita.

Il punto da discutere è come esprimere e verificare la relazione documentata
persona–ruolo–proprietà mantenendo quote e confini dei record. Questa analisi
non propone di accettare il valore sulla sola dichiarazione del modello o
di rimuovere i controlli. B0 resta il riferimento; FORM e coverage invariati.

Fonti grezze preesistenti:

- `backend/data/compilation-audit/b0-minervino-20261016T154354Z/analysis-03/`:
  `input.json`, `response.txt`, `validation.json`;
- `backend/data/compilation-audit/e1-index-20261017-01/analysis-01/`:
  input e risposta originali;
- `backend/data/compilation-audit/root-user-reasoning-20261017-01/`:
  `analysis-01/response.txt`, `analysis-01/validation.json`,
  `b0-03-partner-details.json`.

Gli estratti pubblici includono quattro casi, tre chunk di input e hash SHA-256
dei dodici file consultati. Verificate uguaglianza delle SOURCE B0/INDEX-01,
identità dei record annidati nel replay, conteggi e coerenza degli estratti.
Questi sono controlli documentali, non nuovi test del motore o nuove misure LLM.
