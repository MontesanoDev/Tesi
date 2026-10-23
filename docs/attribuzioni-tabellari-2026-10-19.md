# Verifica mirata delle attribuzioni tabellari

19 ottobre 2026 — `tabelle-attribuzione-20261019-01`.

**È emersa una lacuna riproducibile del verificatore sulle tabelle reali.**
Non sono emerse nuove scritture errate negli output LLM storici esaminati.
Quattro proposte deliberatamente errate, costruite sul FORM e sulle SOURCE
reali di Catanzaro, superavano invece il grounding come proposte selezionabili.
La correzione le respinge senza cambiare gli audit o i DOCX dei nove riferimenti.
Nessuna nuova chiamata LLM, sessione o modifica agli artefatti precedenti.

[Consegna](<../benchmark ufficiale/tabelle-attribuzione-20261019-01/README.md>),
[esito e limiti](<../benchmark ufficiale/tabelle-attribuzione-20261019-01/ESITO.json>),
[regressione](<../benchmark ufficiale/tabelle-attribuzione-20261019-01/REGRESSIONE.json>).

## 1. Cosa è stato verificato e cosa dimostrano le prove

Analizzati i nove input/state/output già congelati: sei documenti del benchmark,
Minervino V12 a 61, Cesano dopo il precedente veto e l'ultimo Catanzaro reale.
Negli export esistenti risultano 37 scritture in tabelle: 35 SOURCE e due USER,
distribuite fra Catanzaro storico, CRAA e Catanzaro recente. Nessuna nuova
attribuzione indebita rilevata fra quei valori. I difetti storici di leggibilità
CRAA e i residui di compilazione restano quelli documentati.

Per verificare la resistenza a proposte sbagliate sono state create **copie**
della risposta Catanzaro, riutilizzando gli stessi fatti SOURCE e citazioni,
ma sostituendo soltanto un'assegnazione per volta. L'originale non è stato
alterato. Non sono quattro errori osservati in una generazione del provider:
sono controesempi controllati del validatore su destinazioni e dati reali.

| Destinazione reale | Fatto societario inserito nella proposta | Soggetto richiesto dal FORM |
|---|---|---|
| t0.r0.c1 — Il/La sottoscritto/a | Denominazione aziendale | Persona che sottoscrive |
| t0.r2.c1 — Codice fiscale iniziale | CF della società | Sottoscrittore introdotto nella stessa tabella |
| t26.r0.c1 — Nome e cognome | Denominazione aziendale | Direttore tecnico |
| t26.r1.c1 — Qualifica professionale | Forma giuridica della società | Persona introdotta dalla riga nome/cognome |

Prima della correzione tutte e quattro diventavano `GROUNDED_PROPOSAL` come
ipotesi conditional. Nessun controllo del binding personale scattava: i fatti
erano `company`. Il precedente veto lavorava solo sui campi inline con range,
quindi le celle vuote tabellari ne restavano escluse.

**Non è stata confusa la groundedness con una scrittura effettiva:** condizioni
e revisione restavano necessarie. I controesempi dimostrano che una proposta
errata poteva arrivare al narratore come selezionabile; non dimostrano che le
quattro nuove scritture siano state prodotte dalla chat. L'ultimo Catanzaro
reale continua a contenere le sue 15 scritture corrette/parziali già revisionate.

I primi tentativi del probe respingevano le proposte per applicabilità non
confermata o per `conditional.conditions` vuoto. Sono conservati separatamente:
non vengono usati come prova di protezione del soggetto. I quattro controesempi
validi conservano le condizioni semantiche reali e sono nello
[stato prima](<../benchmark ufficiale/tabelle-attribuzione-20261019-01/probes-before.json>).

## 2. Correzione circoscritta

Esteso soltanto [compilation_attribution.py](../backend/app/compilation_attribution.py).
Nessuna modifica al parser, al catalogo FORM inviato al modello, al writer,
all'API, al prompt, al modello, al dialogo o alle regole di binding SOURCE.

Il veto legge la struttura già disponibile nel catalogo. Per le tabelle
riconosce **righe con due celle fisiche**, etichetta fissa a sinistra e
destinazione a destra. Identifica introduzioni esplicite, come sottoscrittore,
firmatario, nome e cognome, direttore tecnico, società, ragione sociale o sede
legale. Può mantenere quel soggetto sulle successive etichette riconosciute
della stessa sequenza, per esempio nascita → codice fiscale o nome → qualifica.
Una nuova introduzione sostituisce il soggetto precedente.

Righe vuote, etichette non riconosciute, celle etichetta compilabili, checkbox,
tabelle annidate, merge verticali e strutture diverse interrompono il
collegamento. Non viene preso un soggetto da un'altra tabella, da un titolo
generico distante o dalle etichette suggerite dal modello. Le unioni orizzontali
restano compatibili quando esistono ancora due celle etichetta/valore inequivoche,
come nella tabella reale del direttore tecnico.

**«Operatore economico» da solo è ambiguo:** può indicare una persona fisica.
Interrompe quindi l'eredità del sottoscrittore, ma non produce automaticamente
un soggetto `company`. Natura giuridica, partecipazione e firmatario restano
distinti. Il controllo non assegna o seleziona persone.

Un contrasto di tipo persona/azienda produce `source_subject_type_mismatch`.
Il controllo di ambito del valore già presente si applica anche all'etichetta
tabellare riconosciuta: residenza documentata non diventa studio professionale.
I valori restano originali, senza trasformazioni o sostituzioni.

L'audit della proposta respinta conserva tabella, destinazione, etichetta che
introduce il soggetto e percorso delle etichette intermedie. Le proposte
compatibili non ricevono nuovi metadati: revisioni e relative impronte restano
identiche. I fatti societari dei quattro controesempi rimangono validi come
fatti societari; sono respinte le attribuzioni ai campi personali.

## 3. Identità e citazioni non sono dedotte dal tipo

Compatibilità `person` o `company` è solo un controllo necessario. Non dimostra
che un dato appartenga alla persona scelta, né che questa abbia un certo ruolo.
I binding SOURCE, le citazioni del valore e le condizioni vengono verificati
come prima. Il nuovo percorso non crea record personali e non unisce persone
per nome, omonimia, ruolo simile o appartenenza alla stessa azienda.

Un'etichetta letta nelle righe precedenti per **respingere un contrasto** non
diventa una nuova citazione FORM valida per il grounding. Un test positivo
viene ripetuto senza il marcatore Word di header ripetuto: il binding personale
resta respinto dal controllo strutturale preesistente. Non è stata corretta
indirettamente la mancata compilazione delle tabelle 41/43/44 di Catanzaro.

I negativi verificano persona diversa, ruolo diverso, binding assente, quote
inventate e proprietà di luogo non equivalenti. I test di identità/omonimia e
collegamento dei record SOURCE della fase precedente sono stati rieseguiti
nella regressione mirata e nella suite backend.

## 4. Prima/dopo e regressione

| Misura | Prima | Dopo |
|---|---:|---:|
| Proposte errate controllate considerate grounded | 4 | **0** |
| Fatti societari utilizzati nei quattro probe | validi | validi |
| Nuove scritture errate osservate nei DOCX storici | 0 | 0 |
| Minervino V12 | 61 | **61, DOCX identico** |
| Catanzaro recente | 15 | **15, DOCX identico** |
| Cesano dopo il precedente intervento | 1 | **1, DOCX identico** |

Restano identici anche Minervino ufficiale (55), Trapani (10), Catanzaro storico
(13), Bella (4), CRAA (9 XML) e Cesano storico (0). Nove audit ricalcolati uguali
e nove DOCX byte per byte uguali al riferimento della fase precedente.
Nessuna scrittura corretta persa, nessuna nuova accettazione nei replay.
Il difetto PEC Trapani e i due CCIAA CRAA invisibili non vengono presentati
come risolti. Non sono stati eseguiti nuovi rendering: gli export sono identici
ai DOCX già renderizzati e ispezionati; questa fase non misura un nuovo motore PDF.

Non sono cambiate condizioni UNKNOWN, gruppi checkbox, firme, SOURCE o dati USER.
Nessun aggiornamento automatico delle vecchie sessioni e nessun export manuale
corretto per migliorare il risultato.

## 5. Copertura effettiva e limiti

Sulle 35 scritture SOURCE in tabelle dei riferimenti, 13 hanno un soggetto di
tipo riconoscibile dal controllo attuale; **22 restano non determinati da
questo specifico veto**. I due valori USER tabellari restano verificati dal
percorso USER, non diventano fatti SOURCE. Tutti i valori mantengono i controlli
storici e gli audit identici. Questi conteggi descrivono occorrenze nei replay,
con ripetizioni fra documenti, non 35 fatti aziendali indipendenti.

Coperto con test permanenti:

- Tabellette verticali etichetta–valore con cambi espliciti persona/società.
- Tipo del soggetto indipendente da `entity`/label MODEL, sui quattro casi reali.
- PEC personale nel campo personale e PEC societaria nel campo societario.
- Mancata autorizzazione di persona/ruolo/citazione non dimostrati.
- Separazione dell'applicabilità UNKNOWN dalla groundedness.
- Interruzioni per righe vuote/sconosciute, altro soggetto, altra tabella,
  etichette compilabili, annidamenti, merge verticali e record multicolonna.
- Residenza/studio come proprietà distinte, senza riscrivere il valore.

**Non coperto dal nuovo veto:** record generali multicolonna, etichette o
sinonimi arbitrari, sequenze complesse, identificazione di persone omonime
mediante il solo nome, coerenza universale fra proposte per più persone dello
stesso ruolo, ricostruzione di condizioni e decisioni procedurali. Dove il veto
restituisce `not_determined`, non sta attestando la pertinenza. I controlli
preesistenti e la revisione restano necessari; non si promette che impediscano
qualsiasi possibile errore semantico in quelle strutture.

La lacuna dimostrata è chiusa per la famiglia verificata. Non è corretto
concludere «tutte le attribuzioni tabellari sono sicure» o adottare la baseline
generale sulla base di questa sola prova.

## 6. Test, file e conservazione

[23 nuovi test permanenti](../backend/tests/test_compilation_table_attribution.py),
fixture reale Catanzaro aggiunta a
[source-attribution-v1](../backend/tests/fixtures/source-attribution-v1/README.md).
RED iniziale: 7 fallimenti e 11 passaggi su 18 casi, poi cinque ulteriori negativi
e verifica dei confini. Nessun test usa il provider reale.

347 test mirati PASS in 28,75 s; i 23 tabellari verificati separatamente sulla
versione finale PASS in 3,16 s. **Intera suite backend: 2.744 PASS in 209,28 s**.
Ruff backend PASS. Le verifiche sono state eseguite in questa fase, non sono
riportate come nuove misure quelle della fase precedente.

Unico file applicativo modificato: `compilation_attribution.py`. Nuovo file di
test, nuovo JSON reale di fixture e append alla sua guida. Aggiornati STATUS,
relazioni e questo rapporto; script e acquisizioni restano nella nuova cartella
audit, senza cambiare i rapporti o i benchmark precedenti.

Preservati 1.085 altri file precedenti, 29 sessioni live e 285 file storage.
Zero sessioni nuove, zero chiamate al provider, zero costi LLM. Codice prima e
dopo, probe, test e nove replay salvati in
`backend/data/compilation-audit/tabelle-attribuzione-20261019-01/`.
Consegna e backup separati nella directory indicata sopra. Nessun commit/push.
