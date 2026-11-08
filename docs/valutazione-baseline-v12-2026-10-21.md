# Valutazione della V12 come possibile baseline di tesi — 21 ottobre 2026

Tre compilazioni indipendenti concluse con provider reale, tre nuovi output globali e tre DOCX esportati e scaricati dal normale percorso chat. **Nessuna modifica al codice applicativo, al modello, ai prompt o alle protezioni fra le prove.** La correzione conservativa dei [valori composti](completezza-valori-composti-v12-2026-10-21.md) è considerata verificata e resta immutata.

**Proposta:** la versione è congelabile come **baseline sperimentale conservativa per bozze parziali**, con gli errori di copertura qui misurati. Non la proporrei come compilatore completo o per inviare pratiche senza revisione. L'adozione resta una decisione dell'utente: `CANDIDATO-BASELINE.json` ha stato `PROPOSED_NOT_ADOPTED`; nessun tag, commit o push.

[Consegna, acquisizioni e backup](../benchmark%20ufficiale/baseline-v12-20261021-01/README.md), [confronto numerico](../benchmark%20ufficiale/baseline-v12-20261021-01/CONFRONTO.json), [verifiche finali](../benchmark%20ufficiale/baseline-v12-20261021-01/VERIFICHE-FINALI.json). Grezzo e script: `backend/data/compilation-audit/baseline-v12-20261021-01/`.

## 1. Selezione preventiva, scenario e isolamento

Pool: sei originali reali già disponibili — Minervino, Trapani, Catanzaro, Bella, Cesano e CRAA — deduplicati per hash, esclusi i DOCX generati e i laboratori sintetici. Prima di ogni nuova chiamata sono registrati documenti, ordine, SOURCE, scenari, parametri e criteri di valutazione.

Due strati fissati: Minervino, prevalentemente inline con checkbox native, e Cesano, controlli Word FORMTEXT. Il terzo documento è estratto una sola volta fra `bella, catanzaro, craa, trapani`: seed `7a57847e66f052554d444bfebfc1eecb`, indice SHA256 modulo 4 = 2, **CRAA**. Nessuna nuova estrazione o sostituzione. `SELEZIONE.json` conserva pool, algoritmo e hash. Un errore iniziale dello script d'ispezione, prima della generazione del seed, è conservato: non è un tentativo LLM fallito o una ripesca.

| Documento | Destinazioni nel catalogo attuale | Struttura coperta |
|---|---:|---|
| Minervino | 254 testi + 13 checkbox | Campi inline, blocchi societari/personali, soci, direttore tecnico, tabelle di preferenze |
| Cesano | 20 FORMTEXT + 68 checkbox | Controlli Word legacy, persona e società in periodi distinti, gruppo di partecipazione |
| CRAA | 51 testi, zero checkbox native | Tabelle con etichette e celle, clausole procedurali, caselle testuali prestampate |

Il codice reale è identico ai 70 moduli backend verificati nella fase precedente; congelati anche 49 file frontend, **119 hash applicativi** invariati durante e dopo le prove. HEAD `99ab052` non rappresenta da solo lo stato: snapshot e patch locali sono conservati. La precedente suite 3.180 PASS/Ruff PASS è un risultato storico verificato per identità del codice, **non una suite rieseguita in questa valutazione**. Non sono stati aggiunti test o correttivi applicativi.

Tre progetti/conversazioni/sessioni nuovi su un clone privato, separato dal database e storage live. Stesso provider DeepSeek e modello `deepseek-flash`, V12 globale B0 con thinking enabled/low e massimo 49.152 token; prompt globale, schema e rappresentazione FORM invariati. Il provider restituisce `deepseek-flash` e fingerprint `e72d3c7f663d3e1383b00b3884cb4501` in tutte le chiamate. Il nome commerciale non garantisce un pin immutabile dei pesi per future ripetizioni.

SOURCE identiche: 22 chunk da quattro documenti aziendali sintetici preesistenti, con originali e hash inclusi. Fotografia societaria al 15 ottobre 2026, con integrazione successiva alla vecchia visura: Leonardo Montemurro rappresentante legale attuale, Luca Ferri ancora socio ma cessato dall'amministrazione, Elisa Romano direttore tecnico. Il corpus non è una certificazione di dati reali o di ammissibilità giuridica.

Ogni scenario sceglie separatamente per la propria pratica Leonardo come firmatario e Mapi Ingegneria S.r.l. come società di ingegneria singola. Dati, ruoli e poteri restano da provare nelle SOURCE. Preferenze, designazioni di esecutori, attestazioni, consensi, allegati, luogo/data e firma restano aperti. Budget uniforme preregistrato: massimo due turni di risposta agli slot attivi, poi una richiesta esplicita di export parziale. Risposte effettive registrate prima dell'invio: 2/2/1 turni. Nessuna nuova decisione inventata per aumentare le scritture.

Il budget è un limite dell'esperimento: non misura la massima copertura ottenibile con dialogo illimitato. È rilevante in Minervino, dove una terza richiesta di conferma del firmatario arriva dopo le due risposte consentite. Il budget non viene ampliato dopo aver visto il risultato.

## 2. Artefatti e scritture effettive

| Documento | DOCX / PDF | Testi SOURCE | Testi USER | Booleani scritti | Non dimostrate osservate |
|---|---|---:|---:|---:|---:|
| Minervino | [DOCX](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/minervino/bozza.docx) · [PDF](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/minervino/render/bozza.pdf) | 43 | 0 | 0 | 0 |
| Cesano | [DOCX](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/cesano/bozza.docx) · [PDF](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/cesano/render/bozza.pdf) | 3 | 1 | 6: uno TRUE, cinque FALSE | 0 |
| CRAA | [DOCX](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/craa/bozza.docx) · [PDF](../benchmark%20ufficiale/baseline-v12-20261021-01/trials/craa/render/bozza.pdf) | 7 | 0 | 0 | 0 |

Totale **54 testi** — 53 con provenienza SOURCE e uno USER, nome del firmatario anche documentato nelle SOURCE — e sei booleani di **un solo gruppo di scelta**. Le cinque alternative FALSE di Cesano sono sostenute dalla scelta esclusiva espressa; non sono cinque nuovi fatti negativi aziendali. Cambia effettivamente stato una checkbox rispetto all'originale, le altre cinque erano già non selezionate.

Ogni scrittura ha un dossier `SCRITTURE-VERIFICATE.json`, separato dal semplice esito del validatore: valore fisico, soggetto, proprietà, testo FORM originale, SOURCE/citazioni, ruolo, condizioni e ricevute USER. Le fonti complete sono disponibili per verificare anche il contesto delle citazioni. La revisione è **documentale autoriale di Codex**, non una seconda annotazione umana indipendente; zero errori osservati non significa precisione universale dimostrata.

Le 43 scritture Minervino riguardano dati societari, tre record soci distinti e due proprietà di Elisa Romano come direttore tecnico. CF e data del direttore appartengono alla stessa Elisa delle SOURCE, con nome e iscrizione 8421 concordanti; non sono trasferiti da altri soggetti. Le righe Luca Ferri, Elisa Romano e Andrea Greco mantengono ciascuna qualifica, CF e iscrizione corretti.

Cesano distingue il sottoscrittore dalla società: nome, luogo/data di nascita e denominazione societaria corretti; studio, PIVA, previdenza e recapiti personali non dimostrati rimangono vuoti. Il nome scritto come USER è la scelta del firmatario dello scenario, non un dato inventato, ed è riscontrato nella SOURCE -53. Luogo e data di nascita sono recuperati dal riuso SOURCE deterministico esistente dopo la risposta USER: **non sono due migliori proposte della nuova risposta globale**.

CRAA scrive soltanto i sette dati societari p12–p18. La normale indicazione della PEC p14 non viene usata come consenso alla dichiarazione procedurale prestampata. Il nome del sottoscrittore non è proposto dal MODEL e non viene recuperato nel dialogo: rimane una omissione effettiva.

## 3. Omissioni, aperture legittime e destinazioni non applicabili

Il riferimento è registrato prima delle inferenze: nucleo di 60/4/10 occorrenze fattuali documentate, più le scelte native decise. I riferimenti storici sono conservati e subordinati ai requisiti FORM, ai soggetti e alle autorizzazioni dello scenario attuale. Non si riduce il nucleo dopo l'output: **54 dei 74 valori del riferimento sono scritti; i 20 mancanti sono classificati esplicitamente**.

“Omissione ingiustificata” indica una lacuna della compilazione complessiva rispetto a un fatto pertinente disponibile, non una richiesta di accettare la proposta difettosa. Un rifiuto backend corretto può lasciare un'omissione causata da una prova MODEL non valida. I controlli non sono stati indeboliti.

| Classificazione di tutte le destinazioni catalogate | Minervino | Cesano | CRAA | Totale |
|---|---:|---:|---:|---:|
| Scritture corrette, compresi i booleani | 43 | 10 | 7 | 60 |
| Scritture non dimostrate | 0 | 0 | 0 | 0 |
| Omissioni fattuali ingiustificate | 16 | 0 | 1 | 17 |
| Omissione di scelta USER già definita | 1 | 0 | 0 | 1 |
| Aperto per limite del dialogo | 1 | 0 | 0 | 1 |
| Legittimamente aperti | 76 | 75 | 26 | 177 |
| Non applicabili | 130 | 3 | 15 | 148 |
| Destinazioni ambigue/non autonomamente richieste | 0 | 0 | 2 | 2 |
| Totale | 267 | 88 | 51 | 406 |

`CLASSIFICAZIONE-CAMPI.json` elenca ogni ID fisico, testo FORM, proposta o omissione MODEL, causa backend e motivazione autoriale. Un catalogo di destinazioni non è un elenco di altrettante informazioni obbligatorie.

**Minervino.** Nove dati del firmatario p12/p13/p14.s0 hanno fatti grounded, ma il binding MODEL cita un estratto non presente nel FORM. Sei dati del direttore tecnico — p51.s0, p52.s0, p53.s0/s1/s2/s4 — falliscono l'attribuzione esplicita del ruolo nel chunk del valore; le informazioni pertinenti esistono nelle SOURCE complessive. p15.s0 fallisce la continuità FORM dell'operatore. Sono 16 lacune con cause registrate, senza trasformarle in “dati assenti”. p14.s1 è una proposta societaria senza errori propri, ma dipende anche da `c_firmatario`, ancora UNKNOWN dopo il budget di dialogo: viene tenuta separata, non attribuita soltanto all'assenza di SOURCE. La checkbox p39.cb0 del ramo societario è decisa ma non proposta: nessun gruppo MODEL, nessuna spunta. Il direttore tecnico resta un record visivamente parziale, con CF/data ma senza nome e altre proprietà: il controllo di completezza del singolo valore non certifica la completezza di un record distribuito su più destinazioni.

**Cesano.** Tutti e quattro i valori fattuali del nucleo sono presenti. La nuova proposta globale tenta **sette trasferimenti di dati aziendali a campi personali** — p12.ft3/4/5/6/10/11/12 — che il backend respinge. Sono proposte non dimostrate intercettate, non scritture indebite nel DOCX e non omissioni di dati personali disponibili. Nessuna informazione sullo studio o sui recapiti personali di Leonardo viene dedotta dalla sede o dai contatti della società. Le altre 62 checkbox di preferenza restano originali e non ricevono FALSE fattuali dal backend.

**CRAA.** p5.s0, nome del sottoscrittore, è omesso senza una giustificazione fattuale: identità e scelta sono disponibili. I due campi CCIAA t6.r0.c1/c3 rimangono aperti perché la domanda attiva unisce forma societaria e attestazione di coerenza con la classe merceologica. Quest'ultima è esplicitamente rinviata; non si conferma una congiunzione fornendo soltanto la scelta societaria. Le proprietà di iscrizione restano disponibili nel riferimento, ma non si inventa la conferma per scriverle. Fatturato del miglior triennio, self-cleaning, CCNL, servizi specifici, avvalimento e altre attestazioni non vengono completati con dati annuali genericamente pertinenti. Due proposte di anno hanno anche citazioni FORM respinte, conservate negli audit. Le due celle compagne t1.r0.c1/r1.c1 non dimostrano ulteriori proprietà obbligatorie.

## 4. Checkbox, valori composti, DOCX e PDF

Tutte le tre bozze superano ZIP/CRC, parsing degli XML, posizioni fisiche dei valori, geometria delle tabelle, conservazione delle parti non interessate, controlli Word e confronto con il download reale. Ricostruzione deterministica della **nuova risposta appena acquisita**, senza rete o SQLite, restituisce gli stessi audit e DOCX: non viene usata per sostituire le tre nuove analisi con risposte storiche.

Minervino conserva le 13 checkbox native, nessuna modificata: la scelta societaria mancante è una omissione, non un PASS di copertura checkbox. Cesano conserva 20 FORMTEXT e 68 checkbox: p19.cb0 selezionata, cinque alternative esplicitamente non selezionate, altre 62 intatte. CRAA contiene caselle testuali prestampate, zero controlli checkbox nativi nel catalogo: nessuna nuova spunta e nessuna pretesa di averne dimostrato la scrittura automatica. Le caselle testuali restano un limite di copertura.

I controlli di completezza in Minervino riconoscono quattro identità COMPLETE, tre scritte e una ancora fermata da altri gate; altri 13 controlli restano UNKNOWN, prevalentemente senza valore o in sezioni non attive. Luogo/data della domanda resta una sola destinazione composta, senza decisione USER: vuota. I campi Word separati di Cesano non vengono accorpati. Nessuna composizione multi-SOURCE viene introdotta. Il pannello **non contiene una nuova scrittura positiva numero+data**: la correzione precedente è preservata, non si pretende di riprovarne tutta la copertura con questi tre casi.

PDF di 9/3/7 pagine, **19 pagine complessive**: tutti i 54 testi osservabili, zero parole fuori pagina. Campioni visivi Minervino p1/p2/p3/p4/p9, Cesano p1/p3, CRAA p1/p2. Il gruppo Cesano è leggibile e correttamente selezionato. In Minervino e CRAA rimangono accostamenti senza spazio come `professionaleOrdine`, `impresaMapi` e `PECmapi`: leggibili, documentati e non corretti in questa valutazione. Non sono stati effettuati test in Word desktop.

Le tabelle CRAA sono presenti nell'input e verificate nell'integrità, ma i due campi tabellari fattuali restano non autorizzati: **questa prova non aggiunge una nuova dimostrazione positiva di scrittura tabellare**. Non si modifica lo scenario per ottenerla.

## 5. Chiamate, token, tempi e costo

| Documento | Chiamate, di cui globali | Input | Output incl. reasoning | Reasoning incluso | Token totali | Globale s | Tutte le chiamate s | Costo USD stimato |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Minervino | 11, di cui 1 | 148.410 | 42.664 | 26.798 | 191.074 | 151,24 | 169,52 | 0,042723 |
| Cesano | 10, di cui 1 | 90.397 | 22.736 | 17.676 | 113.133 | 88,59 | 102,61 | 0,022892 |
| CRAA | 7, di cui 1 | 71.988 | 21.787 | 16.330 | 93.775 | 82,63 | 92,62 | 0,020578 |
| Totale | 28, di cui 3 | 310.795 | 87.187 | 60.804 | **397.982** | 322,47 | 364,74 | **0,086193** |

Usage effettivo restituito dal provider, non stima da caratteri. Reasoning già incluso nell'output, non sommato due volte. Input: 86.656 token cache hit e 224.139 miss. Tutte le chiamate avvengono fuori dalle finestre peak; tariffe consultate il 21 ottobre: USD per milione 0,003 hit, 0,15 miss, 0,6 output. Costo = hit × tariffa hit + miss × tariffa miss + output × tariffa output. [Tariffe ufficiali DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/).

È un costo calcolato a tariffa, **non una fattura né una misura del saldo account**. Normalizzando tutto l'input come cache miss risulterebbe 0,09893145 USD. Sono inclusi router, narratori e interpretazioni delle risposte, non solo le globali. Tutte le 28 risposte sono HTTP 200 con `finish_reason=stop`; nessun retry o rimpiazzo selettivo.

I tempi provider sono misurati con orologio monotono. Le sessioni browser durano 529,719/516,645/590,103 secondi, incluse le attese dell'operatore e le verifiche documentali svolte durante il lavoro: non sono tempi di inferenza né un benchmark di velocità automatica. Trenta GET abortite su mount/reload, zero POST fallite ed errori console/driver/provider. Ogni chiamata conserva richiesta, risposta, usage, modello, fingerprint e tempi nel grezzo.

## 6. Problemi bloccanti e proposta motivata

Non sono stati osservati crash, DOCX mancanti/corrotti, scritture non dimostrate, promozioni di condizioni MODEL UNKNOWN o nuove attestazioni non autorizzate che blocchino **la conservazione di questo riferimento sperimentale**. I sette tentativi Cesano respinti forniscono anche evidenza reale del controllo di attribuzione, senza cambiare codice.

Sono invece **bloccanti per presentare la V12 come compilazione completa o pronta all'uso senza revisione**:

1. Firmatario/anagrafica mancanti in Minervino e nome mancante in CRAA nonostante SOURCE e scenario pertinenti; direttore tecnico Minervino incompleto.
2. Copertura discontinua delle scelte native: gruppo Cesano riuscito, gruppo societario Minervino omesso. Le caselle testuali CRAA non sono controlli nativi supportati.
3. Conferme ripetute e condizioni MODEL eccessivamente aggregate o frammentate: incidono sui campi esportabili e sul budget di dialogo, senza essere assenze fattuali.

Nessuno di questi problemi viene corretto durante le tre prove. I due limiti richiesti — grammatica FORM limitata e assenza di composizione multi-SOURCE — restano invariati e documentati. Non si risolvono ruoli, citazioni, dialogo, writer, narratore o completezza di record distribuiti con interventi opportunistici.

**Raccomandazione:** conservare questa esatta V12 come candidata baseline per confronti controllati su **bozze parziali**, usando manifest, SOURCE/scenari e classificazioni fissi, senza chiamarla definitiva. Le tre sessioni sono indipendenti, non tre repliche dello stesso modulo: una replica per documento non stima la variabilità, e i documenti sono già studiati. Corpus sintetico, selezione strutturale, budget USER limitato e revisione autoriale escludono una pretesa di generalizzazione o accuratezza globale. L'adozione della baseline resta da decidere; il lavoro si ferma a questa proposta.

## 7. Preservazione e riproducibilità

`PRESERVAZIONE.json` verifica codice applicativo, originali e modifiche pregresse, intero contenuto logico del DB live, 29 sessioni e 273 file di storage live; conserva le 38 sessioni e 490 file precedenti del clone, aggiungendo soltanto le tre nuove sessioni. Nessuna modifica al fix dei valori composti o agli artefatti congelati precedenti. Servizi di prova arrestati.

Backup separato `audit-completo.tar.gz`, manifest e checksum; esclusi DB e credenziali private. `VERIFICA-BACKUP.json` registra l'estrazione in una directory nuova, controllo di tutti gli hash e ricostruzione offline dei tre audit/DOCX e dei download usando il codice estratto. L'inferenza reale non è riproducibile offline: lo sono gli output acquisiti e i controlli deterministici. Dipendenze Python e renderer non sono incorporati; SOURCE originali, richieste/risposte reali, dialoghi, revisioni, XML, PDF e acquisizioni browser sono conservati. Nessun commit o push.
