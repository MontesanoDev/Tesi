# V12 — Completezza semantica dei valori composti, 21 ottobre 2026

Intervento circoscritto successivo ai fix di [applicabilità](applicabilita-form-v12-2026-10-20.md) e [relazioni tabellari](relazioni-tabellari-form-v12-2026-10-20.md). V12 globale B0, provider, modello, prompt, rappresentazione FORM, parser e writer conservati. E1/E2-A rimangono esperimenti congelati, solamente riletti nella regressione. Nessun commit, push, migrazione o reindicizzazione.

Consegna: [`compound-values-20261021-01`](../benchmark%20ufficiale/compound-values-20261021-01/README.md). I riferimenti seguenti relativi alla consegna indicano nuovi artefatti, non sovrascritture dei benchmark precedenti. Grezzo e script: `backend/data/compilation-audit/compound-values-20261021-01/`.

## Causa tecnica e riproduzione prima del codice

`RIPRODUZIONE-ORIGINALE.json` ricostruisce l'ultima UI Catanzaro congelata (`table-form-links-20261020-01`). Il replay della risposta MODEL, delle ricevute USER e delle revisioni conservate riproduce il DOCX originale byte per byte prima della modifica.

| Dimensione | Prova acquisita |
|---|---|
| Destinazione fisica | `t25.r3.c1`, paragrafo valore p442; tabella 25, quarta riga, seconda cella XML. La label ha gridSpan: nella griglia logica python-docx il valore è `cell(3,2)`. |
| FORM completo | p441, cella `t25.r3.c0`: «numero e data d’iscrizione:». Arco strutturale adiacente della correzione precedente, non label MODEL. |
| Requisito | Numero **e** data della medesima iscrizione della società pertinente. |
| Proposta MODEL | `f_num_iscr`, valore `01234560981`, `disposition=conditional`, condizione `c_soc_ing`. Motivazione: «Numero documentato; data non separatamente richiesta nel record». La motivazione non può cancellare il requisito FORM. |
| SOURCE | Società Mapi Ingegneria S.r.l.; chunk -52, `integrazione-company.md`, citazione letterale del numero di iscrizione. `GROUNDED_PROPOSAL` corretto per il solo numero. |
| Condizione | MODEL conserva UNKNOWN; una ricevuta USER esplicita conferma il ramo societario. La completezza rimane un controllo separato. |
| Prima | Selezione, validazione letterale e writer accettano il numero; il DOCX e il PDF contengono il numero senza data. |
| Dopo | Fatto SOURCE ancora vero; completezza `INCOMPLETE`, componente `date` mancante, selezione ed export vietati. La cella rimane vuota. |

Il sistema verificava che il FORM fosse collegato alla destinazione, che il valore fosse documentato e attribuito, e che condizioni e autorizzazioni consentissero il ramo. Mancava una verifica della sufficienza del **valore destinato a quella singola posizione**. La corretta prova SOURCE di un componente diventava così sufficiente per l'intero campo. Non era un errore del writer.

La data «14 marzo 2019» esiste nelle SOURCE autorizzate -30 e -43. Sono presenti anche data di costituzione, REA e iscrizioni personali differenti: non sono intercambiabili. Il numero sintetico integrato in -52 e la data degli altri documenti non costituiscono un valore contiguo verificabile né offrono nel contratto corrente una chiave di record attestata per assemblarli automaticamente. **Data disponibile nelle SOURCE non significa coppia numero/data dimostrata e scrivibile.**

## Decisione e modifica

Decisione registrata prima del codice in `PROGETTO-PRIMA-DEL-CODICE.md`; delta attesi registrati separatamente in `DELTA-ATTESI.json`.

Il nuovo modulo `backend/app/compilation_value_completeness.py` deriva requisiti da FORM originali e dagli archi fisici esistenti. Usa una grammatica dichiarata di combinazioni informative: numero/data o anno; luogo/data; identità completa; componenti esplicite dell'indirizzo; autorità, sezione e classe richieste; estremi della procura; oggetto/data di contratto; recapiti distinti. Non divide qualsiasi congiunzione, slash, virgola o testo descrittivo. Considera la singola destinazione: marker e controlli Word separati restano campi separati.

L'audit aggiunge `value_completeness`, senza riscrivere fatti, binding, disposizioni, condizioni o prove precedenti:

- `COMPLETE`: tutti i componenti obbligatori riconosciuti sono presenti nel valore e ne conservano citazioni e provenienza; la relazione di record deve essere verificabile.
- `INCOMPLETE`: il valore non contiene una componente obbligatoria identificata.
- `UNKNOWN`: requisito, associazione, data, record o prova non determinabili; non equivale a TRUE, FALSE o assenza della SOURCE.

Per ogni controllo vengono conservati destinazione e hash del template, contesto e prove FORM, modalità cumulativa/alternativa/ambigua, componenti riconosciuti, parti mancanti, valore e motivazione. I componenti completi conservano la propria evidenza SOURCE. Date equivalenti vengono riconosciute senza alterare il testo scritto né rilassare il grounding letterale. Due date differenti per un singolo requisito restano ambigue. La presenza di numero e data in clausole di pratiche o soggetti differenti non dimostra una coppia, neppure all'interno dello stesso span.

Un'etichetta alternativa esplicita richiede una delle alternative; una componente dichiarata facoltativa non diventa obbligatoria. «Cellulare + Telefono» non dimostra invece se un recapito singolo soddisfi il campo: singolo telefono `UNKNOWN`, due recapiti distinti documentati possono essere `COMPLETE`. Questa esclusione conservativa era preregistrata; non si modifica il gold storico che accettava il telefono. «Ordine/Collegio», «Poteri conferiti/qualifica» e descrizioni con “e” non diventano automaticamente requisiti cumulativi.

Integrazioni minime:

| File | Effetto |
|---|---|
| `compilation_global.py` | Nuova dimensione dell'audit soltanto per V12. |
| `compilation_global_sessions.py` | Selezionabilità e controllo sia dello stato persistito sia dell'audit ricalcolato prima dell'export; vale per selezioni SOURCE e USER. |
| `compilation_global_dialogue.py` | Veto a risposte parziali e selezioni, anche dopo revisione del narratore. Una conferma generica non completa il fatto. |
| `compilation_source_reuse.py` | Ricalcola la dimensione dopo il riuso SOURCE già esistente, senza cambiare regole o valori del riuso. Evita di bloccare un valore completo usando il controllo del vecchio fatto. |

`INVARIANTI-CODICE.json` verifica funzioni di costruzione input, richiesta globale, fatti e condizioni, oltre all'identità dei file di catalogo, contratto, attribuzione, applicabilità, relazioni tabellari, controlli procedurali, checkbox e writer rispetto alla baseline locale. Non rispetto al solo HEAD, che non rappresentava tutte le modifiche pregresse.

Le sessioni V12 antecedenti senza questa dimensione non vengono migrate o dichiarate complete implicitamente: i campi composti riconoscibili richiedono nuova analisi. Selezioni o flag di revisione salvati non superano il ricalcolo finale. I percorsi precedenti V2–V11 conservano il proprio contratto storico.

## Composizione: scelta esplicita e limite del contratto

**Nessuna concatenazione o composizione multi-SOURCE è stata introdotta.** Nel contratto corrente `SharedFact.value` è una stringa; ciascuna evidence deve contenere l'intero valore. Due citazioni non sono una rappresentazione di due componenti assemblabili. Lo stesso requisito letterale rimane nella validazione DOCX.

Un valore già interamente documentato nello stesso span può superare il nuovo controllo con provenienza per componente. Componenti in span distinti, anche dello stesso record, non acquisiscono una deroga al grounding precedente. Le prove relative a iscrizioni o soggetti differenti restano rifiutate.

L'alternativa minima futura, **proposta e non implementata**, è un elenco tipizzato `components[{property,value,source_span,record_key}]` con soggetto, operatore di composizione e chiave di record attestata nella SOURCE. Richiederebbe adeguamenti coordinati di contratto, validazione, riuso, revisione ed export. Una chiave suggerita dal modello o la vicinanza testuale non bastano. Non è necessaria per vietare la scrittura parziale; questa modifica significativa richiede una decisione separata dell'utente.

## Inventario dei documenti e dei casi analoghi

`INVENTARIO-PRIMA-GREZZO.json` conserva l'ispezione iniziale. `INVENTARIO-E-DELTA.json` contiene il censimento classificato per originale, destinazione fisica, FORM, componenti, proposte, precedenti scritture ed esito successivo. Sono esaminati nove originali distinti per hash: le sei famiglie di export, una variante Catanzaro precedente, Labirinto e il laboratorio checkbox. Le ripetizioni dello stesso originale nelle repliche non diventano nuovi moduli.

| Modulo/caso | Destinazioni ed esito |
|---|---|
| Catanzaro, numero/data | `t25.r3.c1` e campi omologhi `t31.r3.c1`, `t37.r3.c1`, `t40.r3.c1`: coppia cumulativa. Sei proposte con solo numero `INCOMPLETE`; cinque erano effettivamente scritte. Tre proposte già composte restano `UNKNOWN` per grounding precedente insufficiente: non vengono recuperate con concatenazioni. |
| Catanzaro, nascita | `t0.r1.c1`, righe anagrafiche omologhe e colonne «Data e luogo di nascita»: requisito cumulativo. Le 18 proposte conservate non superavano già le prove SOURCE; nessun valore viene composto o trasferito da un'altra persona. |
| Catanzaro, indirizzo | `t0.r7.c1`, «Sede legale (via, città, prov.)»: i 17 valori completi documentati restano `COMPLETE`. La sede operativa condizionata è un'altra destinazione e conserva il veto precedente. |
| Catanzaro, altri | `t9.r6.c1` numero/anno albo e `t0.r4.c1` estremi procura: nessuna compilazione forzata; proprietà obbligatorie distinte. `t19.r3.c1` numero albo rimane atomico. Nome/cognome completo rimane accettabile soltanto per il soggetto corretto. |
| Catanzaro, recapiti | `t0.r11.c1`: 11 proposte di solo telefono, `UNKNOWN`; dieci erano scritte. Nessun numero è classificato falso, nessun cellulare viene inventato. |
| Trapani | Sei celle della colonna «Oggetto del contratto di appalto e data di stipula», da `t5.r1.c1`: cumulative, senza proposte complete da scrivere. `p171.s0` luogo/data della pratica: richiede entrambe. Altri numeri, date e iscrizioni con più marker sono destinazioni separate; nessuna estensione indiscriminata delle prove della tabella. |
| Minervino | `p242.s0` luogo/data; campi di nascita/iscrizione con più marker restano atomici per destinazione. Identità complete accettate; le scritture preesistenti restano esattamente conservate. |
| Bella | Sei celle «Qualifica e generalità…», da `t2.r1.c1`: richiesta aperta, `UNKNOWN` senza inventarne le componenti. Data/firma in slot distinti non formano un unico valore. |
| Cesano | Controlli Word di nascita, iscrizione e data in posizioni separate: nessun accorpamento. Export preesistenti conservati. |
| CRAA | Provincia/numero di iscrizione in celle distinte; campi professionali separati. Nessuna nuova composizione, attribuzione o dichiarazione. |
| Labirinto e laboratorio | Iscrizioni e riferimenti separati; identità complete controllate. Checkbox non trasformate in campi composti. |

Il censimento riconosce 159 requisiti fisici nei nove originali, comprese le identità complete e le ripetizioni di sezioni: non sono 159 campi da compilare. Nei 69 replay: 160 controlli con valore proposto, dei quali 118 `COMPLETE` (101 identità complete e 17 indirizzi), sei `INCOMPLETE` e 36 `UNKNOWN`; 1.312 ulteriori controlli non hanno valore proposto. Questi ultimi non dimostrano assenza di dati nelle SOURCE e non sono 1.312 nuovi rifiuti di scrittura. Non sono percentuali di qualità del modello.

## Test permanenti e regressione deterministica

Nuovi file: `test_compilation_value_completeness.py` (98 casi) e `test_compilation_value_completeness_session.py` (34 casi API su FTS5/Qdrant), con fixture congelata `fixtures/value-completeness-v1/`. Un'aspettativa del test precedente di applicabilità viene aggiornata per sottrarre i due veti indipendenti; i controesempi B0-3/E1-3 e le fixture precedenti rimangono intatti.

I 132 nuovi casi coprono numero senza data, data senza numero, coppie complete, formati equivalenti e date invalide; citazioni separate con record uguale/diverso e soggetti diversi; record mescolati anche nello stesso span; qualificatori obbligatori/opzionali; cumulativi, alternative e ambiguità; indirizzi e identità; celle, riga precedente, header non marcato, inline e FORMTEXT; slot distinti realmente scritti; ruoli errati e rifiuti SOURCE preesistenti; applicabilità TRUE/FALSE/UNKNOWN; dialogo, narratore, riapertura, cache e richieste d'export obsolete. Le API usano provider simulati e storage temporaneo: non sono valutazioni LLM reali.

La baseline completa prima del codice è 3.048 PASS. Il primo tentativo nello snapshot backend mancava di due fixture esterne: errore dell'harness conservato, baseline rieseguita nel working tree ancora invariato. Durante lo sviluppo sono conservati i fallimenti su alternative, aspettativa storica del telefono e qualificatore opzionale, corretti senza allentare il grounding; Ruff ha individuato errori di stile poi corretti. Un'esecuzione intermedia è stata interrotta perché superata da una revisione del codice. Due avvii di replay senza PYTHONPATH sono documentati come errori di lancio, non risultati software.

`after-results.json` e `INVENTARIO-E-DELTA.json` dettagliano i 69 export: 56 DOCX identici byte per byte, 13 modificati solamente per 15 rimozioni preregistrate: cinque numeri senza data e dieci recapiti ambigui. Da 797 a 782 istanze testuali, senza nuovi valori, alterazioni dei valori mantenuti o effetti checkbox. Il confronto sottrae esclusivamente la nuova dimensione di audit e verifica l'identità di tutto il resto: fatti, binding, condizioni, campi, attribuzioni e autorizzazioni. Nessun'altra differenza ammessa. Minervino, Trapani, Bella, Cesano e CRAA conservano gli output e le posizioni.

I 213 triplet storici V2–V12 sono un controllo aggiuntivo dei validatori, non 213 export né 213 nuove prove UI: 207 validati, sei rifiuti precedenti conservati. Audit precedenti esattamente identici al netto della nuova dimensione V12. Il flag `underlying_result_exact` confronta anche la dimensione aggiunta e risulta perciò falso nei casi V12; `underlying_result_exact_except_new_dimension` è vero per tutti. Nessun risultato viene nascosto dietro un falso confronto byte per byte.

Tutti i 69 export verificano ZIP/CRC, parsing di ogni XML, geometria delle tabelle, destinazioni fisiche, testo prestampato e parti non selezionate, controlli Word e checkbox. 31 conversioni PDF coprono tutte le 13 bozze modificate prima/dopo e cinque riferimenti delle altre famiglie: valori conservati osservabili, zero parole fuori pagina. Il controllo a coordinate risolve i falsi negativi dell'estrazione lineare fra colonne, senza sostituire l'ispezione XML. Campioni visivi Catanzaro p2/p11 mostrano sede operativa e numero/data vuoti, CCIAA Bari e dati del direttore tecnico conservati. Verifiche in `PDF-REGRESSIONE-VERIFICATA.json`; Word desktop non eseguito.

## Verifiche conclusive ed E2E reale

Suite finale **3.180 PASS in 287,83s**, comprendente i 132 nuovi casi; Ruff PASS. Non si riportano esecuzioni intermedie come se appartenessero alla revisione finale. Gate preregistrato prima dell'inferenza in `preflight-gate.json`, con tutti i 69/213 replay e i 31 confronti PDF già PASS. Settanta moduli applicativi congelati e verificati prima della chiamata globale.

Una nuova sessione reale UI, `e81df1cca6b34606a923857c5605d325`, progetto clone `completezza-valori-catanzaro`, conversazione `conv-1a5bd7d85b3e4e0a`, versione finale 8 `GENERATED`. Scenario preregistrato prima dell'inferenza: firmatario Leonardo Montemurro, società di ingegneria in forma singola; altre preferenze, attestazioni e consensi non confermati. Un solo turno di risposte alle due domande realmente attive, ripetendo la scelta societaria per sezione 5.d e Parte Terza; nessun nuovo fatto o potere. Poi richiesta esplicita di bozza parziale, download ordinario e riapertura UI.

Stesso modello `deepseek-flash`, prompt, intera rappresentazione FORM, 22 chunk SOURCE e parametri B0. Otto chiamate provider, incluso il secondo export della stessa analisi, una globale da 118,06s; 127,89s complessivi, 155.285 token; stesso fingerprint nelle chiamate, nessun retry per migliorare l'output. Nessun provider simulato, modifica manuale di sessione o completamento di campi tramite API di test.

| Misura della nuova risposta reale | Risultato |
|---|---:|
| Assegnazioni MODEL complessive | 23 |
| Proposte su requisiti riconosciuti, con valore | 6 |
| Forma completa generata dal modello | 6 |
| `COMPLETE` anche rispetto alle prove | 4 |
| `UNKNOWN` per rifiuto SOURCE precedente | 2 |
| Proposte parziali `INCOMPLETE` intercettate in questa nuova prova | 0 |
| Proposte composte effettivamente scritte | 3 |
| Valori SOURCE effettivamente scritti, totali | 16 |
| Valori USER / checkbox scritti | 0 / 0 |
| Requisiti riconosciuti senza valore MODEL | 54 |

Le sei proposte comprendono un indirizzo, tre identità complete e due coppie luogo/data di nascita. L'indirizzo e due identità vengono scritti; un'identità completa resta fuori per binding di ruolo rifiutato. Le coppie di nascita restano fuori per grounding/binding precedenti, anche se la forma contiene entrambi i componenti. Completezza non sostituisce le altre verifiche.

**Il nuovo MODEL omette `t25.r3.c1` e il relativo fatto scalare**. Il numero è ancora nelle SOURCE congelate, ma non è un fatto proposto/grounded in questa nuova analisi. Il campo numero/data resta vuoto con `UNKNOWN` per mancanza di proposta; questo risultato non viene attribuito al veto contro una proposta parziale. Anche il recapito ambiguo non è proposto. Nessuna ripetizione per ottenere un controesempio o un risultato migliore.

Dopo la prima acquisizione UI, quattro ulteriori test positivi hanno mostrato rifiuti di «SEZ. a»/«Sezione A» per due confronti sensibili alle maiuscole. Corretti con due sole opzioni `re.I`, senza normalizzare il valore scritto o la citazione. Il codice della prima UI è conservato in `e2e-initial-code/`, il risultato in `E2E-REALE-INIZIALE.json`. La suite iniziale prima dell'inferenza era 3.176 PASS; **la suite finale dopo questo ritocco è 3.180 PASS**, con 132 nuovi casi. Tutti i 69/213 replay e i controlli PDF sono stati ripetuti sul codice finale, senza ulteriori delta.

`PROTOCOLLO-EXPORT-FINALE.json` preregistra la verifica successiva: riapertura della stessa conversazione e nuovo export/download ordinario dopo la regressione finale, nessuna nuova analisi globale o scelta USER. Il backend finale ricalcola l'audit prima di scrivere. Il DOCX della versione 8 coincide byte per byte con quello della prima acquisizione e i due download; il PDF acquisito resta valido per lo stesso DOCX. Nuovo trace browser separato in `browser-final-export/`. Questo distingue l'inferenza reale iniziale dalla verifica UI del codice finale senza ripetere il modello per migliorarne la risposta.

Il confronto deterministico sulla **stessa nuova risposta e sulle stesse ricevute USER** conserva 16 scritture in entrambi i backend e ricostruisce il download esatto. La prova causale della correzione è invece la **stessa vecchia risposta reale congelata**: 17 scritture prima, 15 dopo, rimosse soltanto numero senza data e telefono sotto coordinazione ambigua. Non si presenta la nuova scelta migliore del modello come effetto del backend.

`E2E-REALE.json`, input/risposta completi, richieste e risposte provider, tempi, dialogo, revisioni, stato, trace/video/screenshot e rete browser sono conservati. MODEL `c_soc_ing` e `c_parte_terza` restano UNKNOWN; due ricevute USER separate autorizzano solamente i rami pertinenti. Nessuna POST fallita, nessun errore console/driver/provider; dieci GET abortite per acquisizione su mount/reload (20 totali), registrate separatamente. Il primo riepilogo eseguito prima che il PDF fosse pronto è conservato come errore di sequenza dell'harness e rieseguito dopo il rendering.

Audit, selezione, controlli SOURCE finali, XML, CRC e download DOCX sono ricostruiti esattamente offline, senza SQLite o rete. PDF reale di 17 pagine: tutti i 16 valori osservabili, nessuna parola fuori pagina, campioni visivi p2/p11/p17. Il campo numero/data e la sede operativa restano vuoti, CCIAA Bari e direttore tecnico sono nelle posizioni corrette. Word desktop non testato. Servizi di prova arrestati.

## Preservazione, backup e riproducibilità

`PRESERVAZIONE.json` confronta tutti i file protetti, l'intero contenuto logico del database live, sessioni live, storage e knowledge con manifest acquisiti in lettura. Nel clone conserva tutte le sessioni e i file precedenti, aggiungendo soltanto la nuova sessione della prova. HEAD invariato, nessun commit/push. Gli originali e i backup delle fasi precedenti restano separati e immutati.

Il backup separato `audit-completo.tar.gz`, checksum esterno e `BACKUP-MANIFEST.json` includono input/output congelati, codice e test prima/dopo, fixture esterne necessarie, audit, script, DOCX/PDF e report. DB, storage privato e credenziali sono esclusi e viene cercata anche la presenza della chiave effettiva, senza esporla. L'estrazione in una directory nuova verifica ogni hash e riesegue con il codice estratto i 69 export per versione (138 DOCX e 276 audit raw/effective), i 213 validatori per versione (426 risultati), la nuova UI acquisita, la coppia sulla stessa risposta e 98 nuovi test unitari. I replayer vietano rete e SQLite; le chiamate reali del modello sono acquisizioni, non vengono ripetute offline. Dipendenze Python già installate e lock conservato: il pacchetto non include l'intero ambiente Python né LibreOffice.

L'esito dell'estrazione e il checksum dell'archivio sono in `VERIFICA-BACKUP.json` e `audit-completo.tar.gz.sha256`, esterni all'archivio per evitare riferimenti circolari. I risultati delle riesecuzioni estratte sono nel grezzo. Il README della consegna contiene i comandi riproducibili.

## Limiti residui

Il riconoscimento FORM è una grammatica deterministica limitata alle famiglie esplicitamente implementate e testate, non un interprete universale del linguaggio naturale. Etichette descrittive generiche non vengono arbitrariamente scomposte; richieste aperte/ambigue riconosciute restano UNKNOWN. Forme nuove, lingue diverse o qualificatori non rappresentati richiedono nuovi requisiti e prove: non si dichiara copertura universale di qualsiasi futuro DOCX.

Non è stata introdotta composizione multi-span: coppie fattualmente ricostruibili dall'uomo possono restare non scrivibili con il contratto attuale. Non vengono risolti in questo intervento equivalenze semantiche, copertura del modello, interpretazioni del narratore, ruoli insufficienti, preferenze USER o omissioni di checkbox. Un valore completo rimane soltanto una proposta se non supera attribuzione, applicabilità, autorizzazioni e revisione. Una singola prova UI non misura stabilità statistica o qualità generale.

Il difetto originale è riprodotto e vietato nel backend senza rendere falso il numero SOURCE, senza completarlo con dati inventati e senza bloccare indiscriminatamente tutti i valori composti. La verifica deterministica dimostra il veto; l'E2E reale dimostra che le scritture ammesse continuano lungo il normale percorso UI/export/download.
