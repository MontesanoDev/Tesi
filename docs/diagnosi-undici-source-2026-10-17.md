# Diagnosi offline degli undici rifiuti SOURCE residui

17 ottobre 2026. Richiesta: distinguere dati mancanti e collegamenti non
ricostruiti prima di decidere altre modifiche. **Sola diagnosi: nessuna
implementazione, nuova chiamata LLM, esecuzione dei validatori o generazione
DOCX.** L'applicabilità dei rami resta un problema separato da affrontare dopo.

## Risultato

Gli undici casi condividono il vincolo che produce il rifiuto, ma **non hanno
tutti la stessa situazione probatoria**. Il verificatore richiede che le
citazioni del fatto siano attribuibili al ruolo nello stesso record/chunk.
Non riutilizza come prova alternativa del valore la riga già verificata nel
binding e non ricostruisce identità fra record con ruoli diversi.

| Situazione osservata | Occorrenze | Che cosa manca |
| --- | ---: | --- |
| Valore esatto, persona e ruolo già nella riga citata dal binding | 4 | Il riuso di una prova completa già proposta, senza collegamenti fra persone o conversioni |
| Nominativo con onorifico nel fatto, senza onorifico nella tabella soci | 3 | Il collegamento fra i due record della persona; il nome completo proposto non è letteralmente nella riga dei soci |
| Data con mese in lettere nel fatto, numerica nella tabella soci | 1 | Il collegamento fra i record oppure una regola esplicita sull'equivalenza di rappresentazione |
| CF/provincia dalla tabella soci, ruolo di direttore attestato altrove | 3 | Il collegamento verificato dell'identità della persona fra i due ruoli |

Sono **9 occorrenze B0-03 e 2 INDEX-01, 10 destinazioni distinte**: il CF del
direttore `p52.s1` compare in entrambe. Non sono gli undici recuperi della
precedente correzione KISS, che appartengono a un conteggio diverso.

In nessuno degli undici manca dall'intero input SOURCE il valore proposto o
l'attestazione del ruolo richiesto. Tutti i valori compaiono letteralmente
nelle proprie citazioni e tutti i fatti e binding sono già
`GROUNDED_PROPOSAL` nei vecchi audit. Questo stato certifica i controlli
locali effettuati, non dimostra da solo l'associazione fra persona, valore e
ruolo per la destinazione. **Quattro casi hanno già una prova congiunta
esatta; per sette rimane da definire/verificare l'associazione o l'equivalenza
di rappresentazione.** Non li dichiaro undici accettazioni automatiche sicure.

## Materiali e metodo

Punto di partenza: i due `after-validation.json` già acquisiti in
`backend/data/compilation-audit/field-context-20261017-01/`, con input e
risposte corrispondenti. [Rapporto del replay precedente](comune-contesto-form-2026-10-17.md).
INDEX è la copia offline con i soli due metadati root isolati nel precedente
intervento; la chiamata originale resta fallita allo schema. Nessun nuovo
filtro o successo storico riscritto.

Ho selezionato soltanto i campi il cui `subject_binding.validation_errors`
contiene:

> SOURCE non attribuisce esplicitamente ruolo e soggetto nello stesso chunk del valore

Ho confrontato citazione del fatto, citazioni e riga del binding, record
SOURCE originali e usi dello stesso `fact_id` in altre destinazioni. Le
colonne della tabella sono state controllate singolarmente: la presenza
della lettera `A` da qualche parte nel chunk non sarebbe una prova della
sezione dell'albo.

Le due liste SOURCE sono identiche: 56 chunk. `user_values=[]` e nessun
`user_context` in entrambi gli input. Nessun dato dal gold, dalla bozza o da
conferme USER di altre prove è stato usato per costruire i collegamenti.

Acquisizioni derivate e script ripetibile, solo libreria standard Python:
`backend/data/compilation-audit/residual-source-20261017-01/`.
[Indice e misure](benchmarks/2026-10-17-residual-source-diagnosis.json),
[bundle della diagnosi](benchmarks/2026-10-17-residual-source-diagnosis-audit.tar.gz).
Il bundle conserva gli undici tracciati completi, il pool SOURCE, gli
estratti dell'identità e gli hash dei sei artefatti precedenti letti. Per
ripetere lo script occorre anche il
[bundle del precedente replay](benchmarks/2026-10-17-field-context-audit.tar.gz).

## Inventario degli undici casi

`-44/-45/-46` appartengono a `generalita-mapi.md`; `-54/-55` a
`integrazione-company.md`. Tutti sono SOURCE company globali dello stesso
insieme inviato al modello. Gli ID servono solo a localizzare queste prove.

| Esecuzione e campo | Valore proposto | Prova del fatto | Prova del ruolo | Diagnosi |
| --- | --- | --- | --- | --- |
| B0 `p43.s0`, nominativo socio | `Ing. Luca Ferri` | `-44`, nominativo completo | `-54`, titolo soci e riga Luca Ferri | Nome senza onorifico nella tabella; record separati |
| B0 `p45.s0`, nominativo socio | `Ing. Elisa Romano` | `-45`, nominativo completo | `-54`, titolo soci e riga Elisa Romano | Nome senza onorifico nella tabella; record separati |
| B0 `p45.s1`, qualifica socio | `Ingegnere` | `-45`, qualifica professionale | `-54`, riga Elisa, colonna Qualifica professionale | Valore esatto già nella prova del binding |
| B0 `p45.s3`, albo socio | `Ordine degli Ingegneri di Bari` | `-45`, ordine professionale | `-54`, riga Elisa, colonna Albo | Valore esatto già nella prova del binding |
| B0 `p45.s4`, sezione socio | `A` | `-55`, frase nominativa del direttore | `-54`, riga Elisa, colonna Sezione | Valore esatto già nella prova del binding |
| B0 `p46.s1`, data iscrizione socio | `18 maggio 2015` | `-55`, frase nominativa del direttore | `-54`, riga Elisa: `18/05/2015` | Stessa data, rappresentazioni diverse e record separati |
| B0 `p46.s2`, numero iscrizione socio | `8421` | `-45`, numero di iscrizione | `-54`, riga Elisa, colonna N. iscrizione | Valore esatto già nella prova del binding |
| B0 `p47.s0`, nominativo socio | `Arch. Andrea Greco` | `-46`, nominativo completo | `-54`, titolo soci e riga Andrea Greco | Nome senza onorifico nella tabella; record separati |
| B0 `p52.s1`, CF direttore | `RMNLSI85C47A662Y` | `-54`, riga Elisa, CF | `-45`, intestazione e ruolo di direttore | Identità da collegare fra socio e direttore |
| INDEX `p52.s1`, CF direttore | `RMNLSI85C47A662Y` | `-54`, stessa riga Elisa | `-45`, intestazione del direttore | Stesso problema B0, seconda occorrenza |
| INDEX `p53.s2`, provincia albo direttore | `Bari (BA)` | `-54`, riga Elisa, Provincia | `-45`, intestazione del direttore | Identità e iscrizione professionale da collegare |

Tutti hanno destinazione fisica riconosciuta e un solo errore locale residuo,
quello SOURCE indicato sopra. Le condizioni restano `unknown`: `c_p39` in B0,
`c_branch_soc` in INDEX. Nessun caso viene promosso a scrivibile in questa diagnosi.

## Quattro prove complete già citate, ma non riutilizzate

Il binding `b_elisa_socio` cita titolo e riga della stessa tabella. La SOURCE
contiene anche intestazioni e delimitatore, già ricostruiti nel suo
`record_attributions`. La riga dice:

```text
| Elisa Romano | 40% | Ingegnere | Ordine degli Ingegneri di Bari | A | Bari (BA) | 18/05/2015 | 8421 | RMNLSI85C47A662Y |
```

Titolo: `Soci della società al 15 ottobre 2026 — scenario sintetico`.
Le quattro celle corrispondono esattamente alla qualifica, albo, sezione e
numero richiesti. Persona, ruolo e valore sono dunque già presenti nella
prova proposta dal modello per quel binding, senza cambiare valore, consultare
altre persone o risolvere l'identità fra due documenti.

Il fatto condiviso usa però `-45` o `-55`, fonti comode per i campi del
direttore. `_binding_check` verifica l'attribuzione dei chunk scelti dal
fatto; non considera la riga del binding come una seconda prova del valore.
Il fallback KISS legge a sua volta soltanto le citazioni del fatto e cerca
in ciascuna il ruolo richiesto. In quei record il ruolo è direttore tecnico,
non socio. **Questo è un limite dimostrato della catena di verifica,
non evidenza fattuale mancante.** Nessuna correzione è stata applicata.

## Tre nomi e una data: il dato esiste, la prova esatta cambia forma

I tre nomi sono attestati senza prefisso nelle righe soci. Il modello ha
scelto invece `Ing. Luca Ferri`, `Ing. Elisa Romano` e `Arch. Andrea Greco`,
copiandoli da record espliciti di altre cariche. Le qualifiche professionali
sono anche in colonne proprie della tabella: non serve dedurle dall'onorifico.

Il codice possiede già un confronto sintattico che ammette titoli abbreviati
nel riconoscimento della persona all'interno di un record
(`_person`/`_same_person`). Il rifiuto osservato non significa quindi che il
parser non conosca `Ing.`. Manca la ricostruzione del rapporto fra il record
del nominativo citato dal fatto e la riga che attesta il ruolo di socio.
La stringa completa con prefisso non è nella riga della tabella: non sarebbe
corretto dichiararla una prova letterale equivalente a quelle dei primi
quattro casi.

Per la data di Elisa la frase nominativa di `-55` attesta esplicitamente
`18 maggio 2015`; la riga soci attesta `18/05/2015`. Il confronto offline
conferma lo stesso giorno, mese e anno. Il backend non riceve però una
prova locale del ruolo di socio per la stringa in lettere. Il fatto è
riusato e passa già per il direttore in `p53.s3`.

Sono possibili due letture da discutere in seguito: associare esplicitamente
i record mantenendo il valore originale, oppure definire un'equivalenza
controllata delle rappresentazioni con provenienza. **Non ho eliminato
onorifici, convertito date o cambiato le citazioni proposte.** La diversità
di forma non è da sola il controllo che li respinge oggi; spiega perché il
semplice riuso letterale della riga non basta come nei primi quattro.

## CF e provincia del direttore: associazione fra ruoli

Il CF di Elisa compare una sola volta nel pool: la sua riga nella tabella
soci di `-54`. Anche `Bari (BA)` è presente nella colonna Provincia della
stessa riga, coerente con la domanda sull'iscrizione all'albo, non con
residenza o sede aziendale.

Il binding del direttore cita il record `### Ing. Elisa Romano - direttore
tecnico` di `-45`. Questo record attesta nome, cognome, ruolo, ordine e numero
8421, ma non contiene né il CF né il valore completo `Bari (BA)`. Il ruolo di
direttore è ripetuto nella frase nominativa di `-55`:

```text
- **Elisa Romano:** direttore tecnico di Mapi Ingegneria S.r.l.; ingegnere, Ordine degli Ingegneri di Bari, sezione A, iscritta dal 18 maggio 2015 con numero 8421.
```

Tra tabella e record del direttore concordano **nome completo, ordine
professionale e numero di iscrizione 8421**; tabella e frase nominativa
appartengono inoltre allo stesso documento integrativo. Il numero 8421
compare in quattro chunk del pool (`-45`, `-32`, `-54`, `-55`), nei rispettivi
record di Elisa. Non ho trovato un record con quel numero assegnato a una
persona diversa. La visura `-32` conferma nome, ruolo e iscrizione.

Questi sono riscontri documentali concreti per un'associazione; non si
tratta di prendere un valore vicino a un nome qualsiasi. Rimane però
**un'associazione fra record**, non un'unica riga che contenga direttamente
CF/provincia e ruolo di direttore. Nei record del direttore il CF non è
ripetuto, e l'unicità universale dell'identità non è dimostrata dal solo
numero professionale. Un eventuale criterio automatico dovrebbe essere
esplicito, circoscritto alla persona e alla provenienza, e verificato contro
omonimie e conflitti. Questa diagnosi non introduce né approva tale criterio.

Il testo «non disponibili» per alcuni dati personali nella scheda generale
precedente descrive un'assenza in quella scheda; non dimostra un CF contrario
a quello della successiva integrazione. Non è però un'autorizzazione a
riempire i vuoti con qualunque dato di un'altra persona.

## Perché l'errore è comune

Riferimenti al codice corrente, letto senza modificarlo:

- [Costruzione dei binding e controlli](../backend/app/compilation_global.py):
  `_subject_bindings`, `_binding_check`, `_recover_binding`.
- [Record personali e tabelle](../backend/app/compilation_role_records.py):
  `table_support`, `record_support`, `fact_record_support`.

Il fatto contiene il soggetto; il binding contiene ruoli, FORM e citazioni,
non un'identità persistente della persona. Il campo collega `fact_id` e
`binding_id`. La verifica controlla prima FORM, uguaglianza dei ruoli e fatto
grounded, poi richiede attribuzione nel chunk delle citazioni del fatto. Il
fallback non effettua collegamenti fra chunk.

In B0 lo stesso fatto professionale è riusato per socio e direttore: qualifica
`p45.s1/p52.s0`, albo `p45.s3/p53.s0`, sezione `p45.s4/p53.s1`, data
`p46.s1/p53.s3`, numero `p46.s2/p53.s4`. Passa per il direttore e fallisce per
il socio. Il CF fa il percorso opposto: passa come socio `p45.s2`, fallisce
come direttore `p52.s1`. Questi riscontri sono già negli audit salvati.

Il riuso di un fatto della stessa persona non è di per sé un errore del
modello. La scelta di un'unica serie di citazioni per più ruoli si scontra
con un verificatore che richiede una prova locale di ciascun ruolo. **Un
messaggio comune nasconde sia il mancato riuso di prove già complete, sia
una necessità di associare record.** Non giustifica un join generalizzato
né richiede di trasformare undici casi in undici dati mancanti della KB.

## Rifiuti esterni agli undici e applicabilità da tenere separata

Restano distinti e invariati:

- B0 `p46.s0` e `p53.s2`: stesso fatto `Bari (BA)`, citato da `-55`. La frase
  di Elisa non contiene quel valore completo. Il troncone iniziale di Andrea
  nello stesso chunk non può provarlo per Elisa. La presenza nella tabella
  di `-54` non ripara automaticamente una citazione insufficiente.
- INDEX `p53.s2`, compreso negli undici, cita invece proprio la riga di Elisa
  in `-54`: qui il valore completo è nella citazione corretta e resta da
  collegare il ruolo. Non è lo stesso difetto del B0 precedente.
- Due indirizzi completi nel Comune e il solo marker FORM di INDEX `p15.s0`
  rimangono gli altri tre rifiuti esterni. Questa diagnosi non li rivaluta.

Nessun ramo è stato dichiarato applicabile o non applicabile. Tutte le
condizioni degli undici campi sono sconosciute e non ci sono USER in queste
due analisi. Essere socio o direttore non determina partecipazione, firmatario
o designazione professionale della pratica. Non sono state trasferite
conferme USER dai test separati del precedente replay.

Una cautela concreta per il prossimo studio: `generalita-mapi.md` e la visura
precedente chiamano Luca Ferri amministratore, ma l'integrazione `-53` ne
attesta la cessazione il **1 ottobre 2026** e la nuova carica di Leonardo
Montemurro dal **2 ottobre**. Non modifica la prova che Luca sia socio al
15 ottobre e non rende falsa la citazione del suo nominativo. Impedisce però
di promuovere indiscriminatamente la vecchia carica a ruolo attuale o a
scelta del firmatario. Anche l'integrazione distingue espressamente carica
societaria e firma della singola domanda.

## Verifiche e limiti

Controlli diagnostici eseguiti: conteggio 9+2, dieci destinazioni distinte,
valori nelle citazioni letterali, provenienza SOURCE/company, stato dei
fatti/binding, quattro valori esatti nelle rispettive celle, usi condivisi
dei fatti, riscontri di identità, input senza USER e SOURCE identiche.
Conservati i tracciati dei cinque rifiuti esterni e gli hash degli input.

Il precedente replay rimane **38 proposte grounded B0 e 23 INDEX**, tutte
ancora condizionate: nessun nuovo recupero misurato, `RESOLVED=0` e
`writes=0`. Non è stata effettuata una nuova misura di falsi positivi,
poiché nessuna nuova accettazione è stata eseguita. Le suite e Ruff del
precedente intervento non sono stati rieseguiti né attribuiti a questa
diagnosi; controllati documenti, JSON, riferimenti, diff e hash dei file
protetti. Il primo comando locale `python` non era disponibile; analisi
eseguita con `python3`, senza dipendenze o accesso al backend live.

Nessuna modifica a codice applicativo, test software, prompt, FORM B0,
contratto, validatori, API, thinking, writer, fixture o vecchi artefatti.
Nessuna migrazione, commit o push. Una futura modifica va discussa e misurata
per i sottocasi distinti; l'applicabilità richiede un'analisi separata delle
condizioni FORM e delle sole informazioni SOURCE/USER dimostrate.
