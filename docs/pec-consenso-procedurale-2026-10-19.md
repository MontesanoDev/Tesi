# PEC e dichiarazione procedurale — verifica conclusa il 20 ottobre 2026

Richiesta: separare la disponibilità di un fatto SOURCE dalla decisione USER che autorizza un impegno nel FORM. Nessun cambio al modello, prompt globale, parser, writer, API o database. Nessun commit/push.

## Causa dimostrata

Il record reale p107.s0 era kind=data, disposition=value, conditions=[], property=pec, fact_id=f_pec. SOURCE -44 di generalita-mapi.md documenta la PEC aziendale. La citazione FORM proposta dal modello comincia da «certificata (della cui operatività il dichiarante assume ogni rischio)» e taglia «di accettare che ogni comunicazione…». Il narratore aveva comunque ricevuto la clausola completa nel form_context: non ha richiesto consenso né prodotto hold. Le due ricevute storiche riguardano luogo/data e veste societaria. Non autorizzano questa dichiarazione.

La verifica locale provava il recapito e il marker; la revisione del narratore non costituiva una decisione dell’utente. Mancava un gate distinto, obbligatorio anche per le proposte etichettate dal MODEL come dati. DIAGNOSI-STORICA.json conserva richieste e risposte originarie.

## Intervento circoscritto

Il nuovo controllo legge il catalogo fisico già esistente. Riconosce verbi espliciti di accettazione, consenso, autorizzazione, elezione di domicilio o impegno nella stessa clausola marcata. Non prende la label MODEL come autorizzazione e non trasforma ogni «dichiara» in decisione. Non modifica grounding, fatti, citazioni o applicabilità.

La domanda mostra la dichiarazione completa con il dato proposto. Il backend la rende obbligatoria nel limite ordinario di tre domande, anche se il narratore non la seleziona. Riusa lo slot booleano esistente senza nuovi endpoint o schema globale. La ricevuta è legata a originale, clausola, destinazioni, valori e percorso univoco della sessione/tentativo. Un assenso esplicito alla domanda chiusa è distinto da export, tipologia societaria, identità del firmatario e altre decisioni.

Rifiuto, UNKNOWN, SKIP, citazione incerta o consenso di altra sessione/valore non autorizzano la scrittura. L’export parziale rimane disponibile; il gate è rivalidato anche nel servizio di export, per valori SOURCE e USER. Gli hold e le condizioni preesistenti restano ulteriori vincoli. Il report conserva la provenienza SOURCE del dato e la ricevuta USER separata.

## Replay identici, senza nuove inferenze

| Caso | Scritture dopo | Variazione |
|---|---:|---|
| bella | 4 | DOCX identico |
| catanzaro | 13 | DOCX identico |
| cesano | 0 | DOCX identico |
| cesano-reale-8 | 1 | DOCX identico |
| craa | 9 | DOCX identico |
| e2e-catanzaro | 15 | DOCX identico |
| minervino | 55 | DOCX identico |
| minervino-v12-61 | 61 | DOCX identico |
| trapani | 9 | Solo PEC nella dichiarazione rimossa; 10→9 |

Gli audit fattuali dei nove replay sono identici. Nessun valore è stato inventato o corretto a mano. Gli altri otto DOCX sono identici byte per byte. A Trapani cambia un solo paragrafo: p107.s0 torna esattamente all’XML originale. Le altre nove scritture, checkbox, firme, stili e parti del pacchetto sono intatte. PDF prima/dopo di cinque pagine, nessuna parola fuori pagina, pagina 3 ispezionata visivamente.

## Limiti dichiarati

Non è un classificatore semantico universale. Il controllo copre la grammatica esplicita riconosciuta entro lo stesso paragrafo e clausola marcata; non ricostruisce impegni impliciti o dipendenze fra paragrafi e celle distinte. La scansione si ferma a punto/frase riconoscibile, punto e virgola e cambio paragrafo. Non risolve automaticamente attestazioni, poteri, preferenze o rami già irrisolti. Il prestampato originale non viene cancellato. Nessuna prova di ammissibilità della gara o di completezza del modulo.

## Validazione e prova reale

49 test permanenti nuovi: 41 casi locali e otto esecuzioni di sessione persistita su FTS5/Qdrant. Casi positivi/negativi per recapiti fattuali, verbi diversi, consenso esplicito, diniego, UNKNOWN/SKIP/REFUSE, risposta incerta, scelta estranea, template/sessione/valore diversi, clausole adiacenti, campo USER, hold e condizioni UNKNOWN. La prova persistita usa il provider simulato e controlla l'export ordinario e il rifiuto del bypass diretto. Non è una misura di qualità LLM.

Test iniziali prima della correzione: 27 FAIL e cinque PASS. Gli insuccessi successivi di sviluppo sono conservati: fixture inizialmente incompleta, tentativo di rileggere una bozza come originale e differenza fra catalogo iniziale e annotato; individuati anche il percorso della sessione mancante nella prima sintesi e il gate da conservare nella vista pubblica senza audit. Risolti prima della prova reale. Nessuna esecuzione provider annullata o ripetuta per migliorarne il risultato.

Risultati finali effettivi: **248 test mirati PASS in 36,96 s; 2.793 backend PASS in 218,66 s; Ruff PASS**. Nessuna modifica al frontend, quindi suite frontend non ripetuta; il percorso UI è verificato dalla nuova prova browser.

Una nuova sessione reale `331f4362017a42dc86f223ea0c8c46c7`, progetto `consenso-procedurale-trapani`, conversazione `conv-d5d97ea176074b26`, FORM 186, versione finale 10 GENERATED. Due turni USER di risposta e richiesta esplicita di export, nessun intervento manuale nello stato interno. Prima della chiamata registrati HEAD `99ab052` con working tree locale, hash di tutti i 66 file applicativi, FORM, SOURCE, prompt, configurazione e scenario. Lo scenario conserva il consenso alle comunicazioni come UNKNOWN; nella chat è ricevuta USER **SKIP**, separata dalla scelta del ramo societario.

Una globale nuova, senza output congelati. Provider `deepseek-flash`, fingerprint `e72d3c7f663d3e1383b00b3884cb4501`, thinking globale enabled/low, temperatura0,1, max_tokens49.152. Stesso system prompt globale SHA `978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`; stessi 22 chunk SOURCE (18 Company, 4 General), snapshot SHA `0982378194a2e3e769ed3e18dc8d92bf6c1c70f6c4e8b5aa9bbf6d236093ff0c`; FORM SHA `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`. L'alias/fingerprint non certifica pesi immutabili del provider.

| Misura | Trapani storico | Stesso output, replay corretto | Nuova chat reale |
|---|---:|---:|---:|
| Fatti SOURCE proposti e grounded | 9 | 9 | 9 |
| Proposte valore | 10 | 10 | 10 |
| Proposte grounded | 10 | 10 | 10 |
| Applicabili secondo condizioni FORM | 10 | 10 | 10 |
| Scritture SOURCE | 10 | 9 | 9 |
| Scritture USER / nuove checkbox | 0 / 0 | 0 / 0 | 0 / 0 |
| Usi procedurali della PEC senza consenso | 1 | 0 | 0 |

Nella nuova chat tutte le dieci proposte sono revisionate dal narratore e nessuna è held: il gate USER impedisce comunque la decima scrittura. **Applicabilità TRUE non equivale a consenso**. La ricevuta SKIP contiene dichiarazione, valore, destinazione e ambito della sessione. La PEC resta nelle SOURCE e nel recapito aziendale p75.s8. Nessun fact o citazione convertito in dichiarazione USER.

Nove valori documentati corretti nelle posizioni XML e leggibili a pagina 2; otto proprietà complete e un indirizzo parziale: la risposta nuova omette il civico 172/C pur disponibile in SOURCE. Non è una perdita nel replay congelato: quel replay conserva la via/civico originale. Persistono le otto omissioni del firmatario p12.s0–s7, presenti nella KB/input e non proposte. PEC dichiarativa e luogo/data restano volutamente vuoti. Zero spunte o firme aggiunte. Nessuna scrittura non supportata o in sezione errata rilevata fra le nove effettive; non si certificano tutte le dichiarazioni prestampate del modulo.

Il ramo societario è chiesto due volte. Prima risposta correttamente marcata SUPPORTED dal guard, ma respinta da `has_user_alternatives` per la «o» nella locuzione negativa «senza raggruppamenti o consorzi». La seconda conferma più stretta è registrata. Questa causa preesistente è riprodotta e lasciata intatta: `DIALOGO-RESIDUO.json`. Tre decisioni distinte (consenso PEC, ramo societario, luogo/data), quattro domande complessive; un duplicato. Nessun trasferimento di firmatari o attestazioni tra gare.

10 chiamate effettive: una globale, quattro router, due guard e tre sintesi. **109.176 token**: 92.309 input,16.867 output; globale 41.921 input+15.917 output, inclusi 11.679 reasoning. Globale 65,86 s; somma HTTP 77,22 s. **0,019564 USD stimati** sul tariffario congelato, fascia off-peak degli orari registrati, non fattura. Nessun errore provider/retry; tutti finish_reason=stop. I tempi browser comprendono attese operative e non sono latenza del modello.

DOCX: CRC/XML/posizioni/report/download e sei tabelle verificati; soltanto word/document.xml cambia rispetto all'originale. Tutte le altre parti, stili e prestampato sono conservati. PDF cinque pagine, nessuna parola oltre bordo, viste pagine 1, 2, 3, 5. Pagina3 dichiarazione con riga vuota; pagina 5 data/firma intatte. Dieci GET ERR_ABORTED al mount/refresh, nessun errore di compilazione o download; trace/video finalizzati. Nessuna verifica Word desktop. Il caso positivo di assenso è coperto dai test di sessione simulati; la singola prova reale usa deliberatamente il rinvio, senza seconda generazione globale.

## Consegna, preservazione e decisione

[Directory esperimento](../benchmark%20ufficiale/pec-consenso-20261019-01/README.md), [DOCX reale](../benchmark%20ufficiale/pec-consenso-20261019-01/e2e/trapani/bozza.docx), [PDF](../benchmark%20ufficiale/pec-consenso-20261019-01/e2e/trapani/bozza.pdf), [dialogo](../benchmark%20ufficiale/pec-consenso-20261019-01/e2e/trapani/dialogo.md), [esito controlli](benchmarks/2026-10-20-pec-consent-checks.json). Grezzi in `backend/data/compilation-audit/pec-consenso-20261019-01/`, backup separato nella consegna.

Tre soli file applicativi interessati: nuovo `compilation_procedural_consent.py`, integrazioni mirate in `compilation_global_dialogue.py` e `compilation_global_sessions.py`. Nessun nuovo framework, endpoint, migrazione o reindicizzazione. Parser FORMTEXT, writer, grounding, FORM, API, modello e prompt applicativi invariati. Il payload del narratore riceve il flag di autorizzazione e uno slot booleano già supportato; le domande testuali sulla dichiarazione sono rese deterministicamente dal backend.

Preservati 1.333 altri file precedenti, 29 sessioni live e 285 file storage. Clone con 34 sessioni precedenti intatte e una nuova; hash di 66 file applicativi invariati durante l'intera prova. Nessuna nuova chiamata al riprendi del20 ottobre. Porte isolate 8001/5174 ora libere. Backup verificato in tre processi separati: nove ricostruzioni con il codice precedente, nove con quello corretto e una del nuovo DOCX reale. Tutti i 19 audit/DOCX coincidono esattamente con i risultati salvati; rete e connessioni SQLite vietate. Manifest e hash nella consegna; database e chiavi esclusi.

**Esito circoscritto: PASS** per la causa riprodotta. Copertura, indirizzo parziale e dialogo restano limiti distinti, non corretti durante il benchmark. Nessuna adozione della baseline, nessun commit/push; arresto dopo rapporto e consegna.
