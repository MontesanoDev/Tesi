# Correzione circoscritta dei binding e replay offline

17 ottobre 2026. Implementata la correzione autorizzata del verificatore V12,
preceduta da test che riproducono i falsi negativi. **Recuperate 6 proposte in
B0-03 e 5 in INDEX-01: tutte conformi al gold.** Sono 11 occorrenze nelle due
risposte, relative a 9 destinazioni distinte. Nessuna nuova accettazione indebita
osservata nei replay e nei casi negativi testati. Rimane un errore preesistente
di pertinenza del valore al campo, presente in entrambe le risposte.

Non tutte le proposte bloccate dipendevano dalla rappresentazione SOURCE:
il replay rende ora visibili ulteriori blocchi sul contesto FORM e sui record
personali. Non sono stati rimossi per aumentare il numero dei recuperi.

[Misure ed esiti per campo](benchmarks/2026-10-17-binding-kiss.json),
[bundle riproducibile](benchmarks/2026-10-17-binding-kiss-audit.tar.gz),
[checksum](benchmarks/2026-10-17-binding-kiss-audit.tar.gz.sha256),
[controlli](benchmarks/2026-10-17-binding-kiss-checks.json).

## Modifica implementata

Solo due file di produzione e un nuovo file di test. Nessun framework,
dipendenza o caso speciale riferito a Mapi, persone del benchmark o ID di campo.
I nuovi percorsi sono attivi solo per V12; i riconoscitori precedenti restano
inalterati e le versioni storiche non vengono aggiornate implicitamente.

**Tabella SOURCE.** Il verificatore riconosce una tabella Markdown completa
immediatamente preceduta da un'intestazione affermativa di ruolo. Rilegge titolo,
intestazioni, separatore e righe dallo stesso chunk. Richiede colonne coerenti,
soggetto esatto nella prima colonna, riga non ambigua e prova del valore
all'interno di quella riga. Titoli e righe di tabelle diverse non si combinano.
Il ruolo non deve essere ripetuto in ciascuna riga.

La flessione singolare/plurale è limitata alla sintassi del titolo tabellare:
`socio/Soci`, ma anche ruoli diversi nei test generici. Non introduce sinonimi
né un'equivalenza nuova fra `required_role` e `source_role`, che devono ancora
corrispondere esattamente dopo la normalizzazione già prevista. Nomi omonimi
duplicati nella stessa tabella, tabelle malformate e formulazioni negative o
incerte riconosciute vengono lasciati sotto revisione.

**Prove del fatto come alternativa.** Se il controllo originario del binding
fallisce, il verificatore cerca un riscontro indipendente in ciascuna citazione
SOURCE già associata al fatto. Usa un record personale riconosciuto, una riga
della tabella oppure una singola riga nominativa esplicita del tipo
`- **Persona:** ruolo di organizzazione; dettagli.`. Soggetto, ruolo e prova del
valore devono essere supportati nel record del chunk del fatto. Non cerca
nuovi documenti, non unisce chunk in base alla semplice uguaglianza dei nomi
e non sostituisce le citazioni del valore.

Restano obbligatori FORM letterale e contesto ammesso, uguaglianza dei ruoli,
fatto già grounded, citazioni rileggibili, autorità SOURCE e isolamento del
progetto. General KB e citazioni inventate non diventano ammissibili. Per
un fatto con due citazioni entrambe devono superare la nuova attribuzione.
L'onorifico abbreviato può essere presente su uno dei due lati del nome:
questa corrispondenza di identità non dimostra una qualifica professionale.

**Audit.** I recuperi conservano prove effettive, formato del record e confini,
oltre a errore e prove del percorso originario sotto `recovery`. La prova
tabellare conserva anche titolo, intestazioni, separatore e riga. Nessun record
proposto dal modello viene riscritto per farlo passare.

Codice: [tabella e record](../backend/app/compilation_role_records.py:84),
[binding strutturali](../backend/app/compilation_global.py:1091),
[recupero per fatto](../backend/app/compilation_global.py:1148),
[test](../backend/tests/test_compilation_binding_evidence.py:77).

## Metodo e limiti del confronto

Prima della modifica sono stati riprodotti **esattamente** gli audit storici
B0-03 e INDEX-01 già depurato dei soli metadati root. Conservati in
`b0-03/before-validation.json` e `index-01/before-validation.json`.

Dopo i test è stato effettuato un replay dei medesimi output, con originale
Minervino, stessi 56 chunk SOURCE, stessi fatti, condizioni e proposte. Nessun
USER aggiunto; nessun nuovo output LLM, export DOCX o aggiornamento di sessioni.
Lo script blocca le operazioni di rete HTTPX e socket.

INDEX-01 originale **continua a fallire lo schema root** per `proposal_stage`
e `project_id`. Per misurare i binding si usa la risposta già isolata nel replay
precedente; tutti i record annidati sono identici all'originale. Nessun filtro
root aggiunto in produzione e nessun successo storico riscritto.

Il gold è usato soltanto offline per valutare le proposte fisse. La misura è
il grounding locale della proposta, inclusa quella condizionata: **non è una
misura di valori effettivamente scritti nel Word** né di qualità di nuove
generazioni. Gli esiti di pertinenza continuano a richiedere revisione.

## Risultati dei replay

| Misura, occorrenze di campo | B0-03 | INDEX-01 con root isolato |
|---|---:|---:|
| Proposte grezze, invariate | 50 | 27 |
| Grounded prima | 22 | 19 |
| Grounded dopo | 28 | 24 |
| Nuove proposte recuperate | **6** | **5** |
| Recuperate conformi al gold | **6/6** | **5/5** |
| Grounded dopo conformi al gold | 27 | 23 |
| Proposte ancora bloccate | 22 | 3 |
| Proposte prima grounded ora perse | 0 | 0 |
| Nuove accettazioni non conformi al gold | 0 | 0 |
| Proposte non conformi già presenti e ancora grounded | 1 | 1 |
| Valori risolti/scritture automatiche | 0/0 | 0/0 |

I tre binding SOURCE dei soci B0-03 passano ora la verifica strutturale della
tabella. Questo non fa passare automaticamente tutti i campi che li usano:
rimangono i controlli per destinazione e per fatto.

| Risposta | Campo | Valore recuperato | Prova verificata |
|---|---|---|---|
| B0-03 | p43.s1, socio Luca: qualifica | Ingegnere | Tabella -54, titolo/colonne/riga di Luca |
| B0-03 | p43.s2, socio Luca: CF | FRRLCU80A01A662K | Stessa riga |
| B0-03 | p43.s3, socio Luca: ordine | Ordine degli Ingegneri di Bari | Stessa riga |
| B0-03 | p43.s4, socio Luca: sezione | A | Stessa riga |
| B0-03 | p53.s1, direttore Elisa: sezione | A | Riga nominativa -55, persona/ruolo/valore |
| B0-03 | p53.s3, direttore Elisa: iscrizione dal | 18 maggio 2015 | Stessa riga |
| INDEX-01 | p52.s0, direttore Elisa: qualifica | ingegnere | Riga nominativa -55, persona/ruolo/valore |
| INDEX-01 | p53.s0, direttore Elisa: ordine | Ordine degli Ingegneri di Bari | Stessa riga |
| INDEX-01 | p53.s1, direttore Elisa: sezione | A | Stessa riga |
| INDEX-01 | p53.s3, direttore Elisa: iscrizione dal | 18 maggio 2015 | Stessa riga |
| INDEX-01 | p53.s4, direttore Elisa: numero | 8421 | Stessa riga |

Tutte le 11 proposte recuperate restano `REVIEW_REQUIRED`, con
`proposal_grounding: GROUNDED_PROPOSAL`, valore non selezionato e condizioni
ancora `unknown`. Condizioni e fatti validati sono **identici prima/dopo**.
La nuova attribuzione non seleziona partecipante, firmatario o ramo FORM.

## Rifiuti residui: distinguere protezioni e limiti ancora aperti

Classificazione disgiunta delle 25 proposte ancora bloccate:

| Motivo primario | B0-03 | INDEX-01 | Valutazione |
|---|---:|---:|---|
| Citazione non dimostra il valore | 2 | 0 | Rifiuto fondato delle prove effettivamente proposte |
| Estratto di destinazione FORM insufficiente | 0 | 1 | Rifiuto fondato: solo marker senza richiesta |
| Ruolo FORM fuori dal contesto ammesso del campo | 18 | 0 | Vincolo mantenuto; possibile ulteriore limite di rappresentazione del FORM |
| Ruolo non dimostrato nel record SOURCE del valore | 2 | 2 | Nessun collegamento fra chunk costruito per superarlo |

**Bari (BA), B0-03.** `f_elisa_provincia` rimane `REJECTED` perché la frase
citata di Elisa in -55 non contiene il valore completo. Restano respinti
`p46.s0` socio e `p53.s2` direttore: due destinazioni, un solo fatto condiviso.
L'occorrenza nel troncone della riga di Andrea nello stesso chunk non viene
usata per Elisa. Il controllo `source_span(quote, value)` è invariato.

**Destinazione INDEX-01.** `p15.s0` rimane respinto con
`Il solo marker non documenta la richiesta del campo`. La correzione dei
binding non modifica né la quote FORM né il valore proposto per quel campo.

**Contesto FORM B0-03.** Il superamento del vecchio errore sui binding SOURCE
rende visibile `Ruolo FORM esterno al contesto del candidate`. Il controllo
originale autorizza soltanto i contesti locali/di continuazione già esposti
dal catalogo. Per esempio **7294, p44.s2, resta bloccato proprio qui**,
nonostante la nuova prova tabellare SOURCE sia riconosciuta.

Questo errore compare su 19 campi dei soci; uno è anche `p46.s0`, con fatto
già respinto. Nella tabella disgiunta ne contiamo quindi 18. Non è una prova
che il ruolo societario sia falso o che manchi dalla KB: è un limite ulteriore
del collegamento FORM attuale. Non è stato corretto o aggirato in questo passo.
È distinto dalla scelta USER di applicabilità del ramo, anch'essa non confermata.

**Quattro attribuzioni SOURCE residue.** Il nome del socio Luca in B0-03 cita
-44, che non lo attesta come socio; il suo binding tabellare è in -54. Il CF
del direttore Elisa, in entrambe le risposte, cita la tabella dei soci -54.
Anche la provincia del direttore INDEX-01 cita correttamente la tabella -54,
ma il suo record non attesta il ruolo di direttore. Il nuovo fallback non
trasferisce il ruolo da -45/-55 a questi valori per la sola uguaglianza del nome.
I dati possono esistere nel corpus: l'attribuzione richiesta non è dimostrata
nel record usato dal fatto secondo le regole mantenute.

Non presentiamo quindi tutti i 25 residui come rifiuti per dati inesistenti:
tre hanno le precise carenze di prova/destinazione sopra elencate; gli altri
22 rimangono vincoli conservativi o limiti di rappresentazione da discutere.

## Accettazioni indebite e verifiche

**Nuovi recuperi:** nessun valore non conforme al gold, nessun soggetto/ruolo
errato osservato nella revisione delle 11 catene effettivamente recuperate.
Non è una dimostrazione universale di correttezza semantica del verificatore.

**Errore preesistente confermato:** `p41.s1` propone l'indirizzo completo nel
campo «Comune sede società», dove il gold richiede Bari. Rimane grounded in
entrambi i replay come prima della correzione. Sono **due occorrenze dello
stesso errore di destinazione**, non un nuovo fatto inventato dalla patch.
Non è stato corretto, poiché esula dal verificatore dei binding personali.
Quindi non si può dichiarare «zero accettazioni indebite nel sistema».

Sequenza delle verifiche:

1. Test scritti prima della correzione: quattro fallimenti positivi attesi e
   30 protezioni già passate, dopo la correzione di tre difetti della fixture
   iniziale. Log iniziale e red corretto conservati.
2. Prima implementazione: 125 passati e due fallimenti sul plurale in `-io`;
   corretta la regola grammaticale generica, senza aggiungere nomi di ruolo.
3. Test finali: **40 nuovi casi**, sette positivi e 33 di rifiuto/protezione;
   **133 mirati passati in 5,65 s** con regressioni di binding, contesti e
   condizioni. Coperti altri soggetti, titoli di altre tabelle, righe duplicate,
   negazioni, prove multiple, citazioni inventate, scope e versioni storiche.
4. **2.344 test backend passati in 188,62 s**, Ruff passato. Frontend invariato
   e non rieseguito. Sono test software con provider simulati, distinti dai
   replay di risposte reali già salvate.
5. Replay offline completato, zero richieste provider. Primo avvio dello
   script fermato prima del replay per `PYTHONPATH` mancante; corretto il
   comando d'ambiente e conservato il log, nessuna modifica al motore per questo.
6. Hash: **10.752 dei 10.754 file protetti invariati**. Cambiano soltanto i due
   file di produzione autorizzati; nuovo test aggiunto. Fixture, fonti, gold,
   vecchi audit, schema globale, API e writer preservati. Controllo AST conferma
   prompt e funzioni preesistenti dei record inalterati; nessun nuovo parametro
   thinking o cambiamento del FORM.

Artefatti locali: `backend/data/compilation-audit/binding-kiss-20261017-01/`.
Contengono codice prima/dopo e patch circoscritta, input/risposte fissi, audit
prima/dopo, confronti per tutte le 267 destinazioni di ciascuna risposta, log e
script. Riproduzione dal repository con le dipendenze installate:
`PYTHONPATH=backend backend/.venv/bin/python <copia-audit>/replay.py`, conservando
la struttura attesa e usando una cartella senza i risultati `after-*`: lo
script usa creazione esclusiva per non sovrascrivere gli esiti precedenti.
Gli hash degli originali rimandano agli archivi storici invariati.

**Lavoro fermato dopo replay e rapporto**, come richiesto. Nessun commit/push,
migrazione, rianalisi di sessioni live, nuovo test provider o modifica ulteriore
dei contesti FORM. B0 resta riferimento; compattazione FORM e coverage sospesi.
