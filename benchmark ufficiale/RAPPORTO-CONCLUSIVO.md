# Benchmark ufficiale V12 — Minervino, Trapani, Catanzaro

19 ottobre 2026. ID acquisizione: `ufficiale-v12-20261019-01`.

**Esito: non propongo di adottare V12 come baseline affidabile alle condizioni richieste.** Tutti e tre i percorsi reali producono un DOCX parziale integro, ma Trapani contiene una scrittura che completa un'accettazione procedurale senza decisione USER. La copertura SOURCE e il dialogo restano inoltre insufficienti su Trapani e Catanzaro. Nessuna correzione o ripetizione selettiva è stata eseguita. Questi risultati possono essere conservati come misurazione dello stato attuale; la baseline non è stata adottata.

## 1. Risultato effettivo

| Misura | Minervino di Lecce | Trapani Green | Catanzaro DL/CSE |
|---|---:|---:|---:|
| Posizioni SOURCE applicabili nel riferimento documentato | 60 | 17 | 31 |
| Proposte LLM di valore, prima dei controlli | 60 | 10 | 15 |
| Proposte di valore grounded al primo stato persistito | 45 | 10 | 13 |
| Proposte SOURCE grounded finali | 54 | 10 | 13 |
| Grounded applicabili secondo la pipeline finale | 54 | 10 | 13 |
| Grounded revisionate ed esportate | 54 | 10 | 13 |
| Testi effettivamente scritti con provenienza SOURCE | 54 | 10 | 13 |
| Testi SOURCE conformi a fonte, destinazione e scenario | **54** | **9** | **13** |
| Testi USER scritti | 0 | 0 | 0 |
| Checkbox USER correttamente selezionate | **1** | 0 | 0 |
| Totale scritture nel report e nell'XML | **55** | **10** | **13** |
| Scritture indebite rilevate | **0** | **1** | **0** |
| Posizioni SOURCE documentate rimaste vuote | 6 | 8 | 18 |
| Di queste: omesse dalla proposta LLM | 0 | 8 | 16 |
| Di queste: proposte, poi respinte | 6 | 0 | 2 |
| Grounded ancora UNKNOWN / hold finali | 0 / 0 | 0 / 0 | 0 / 0 |
| Condizioni effettive TRUE / FALSE / UNKNOWN | 1 / 0 / 6 | 1 / 0 / 0 | 1 / 1 / 11 |
| Domande mostrate / decisioni distinte | 9 / 8 | 3 / 2 | 2 / 1 |
| Domande ripetute / alternative superflue | 1 / 2 | 1 / 0 | 1 / 0 |
| Pagine PDF | 9 | 5 | 17 |
| Integrità DOCX, posizioni e download | verificati | verificati | verificati |

**Le colonne “grounded/applicabili” descrivono gli esiti del software, non una certificazione della correttezza.** Trapani dimostra la differenza: la PEC è letteralmente documentata e accettata dal backend, ma il contesto della sua seconda destinazione richiede una decisione ulteriore. Non si possono contare 10 scritture corrette solo perché il report ne registra 10.

Le 60/17/31 sono **occorrenze in campi**, non fatti atomici distinti: lo stesso CF può essere richiesto in più punti e una cella può richiedere insieme numero e data. Sono il nucleo SOURCE applicabile verificato prima delle chiamate. Non sono il totale di tutti gli adempimenti della procedura. Il totale esatto dei fatti applicabili resta **non determinato** per attestazioni, documenti allegati, esecutori e registri di servizi a cardinalità variabile, ancora UNKNOWN nello scenario. Non presento 267/115/307 candidati tecnici come altrettanti fatti obbligatori, né una percentuale globale di accuratezza. Questa limitazione della misura resta esplicita nel benchmark.

## 2. Protocollo e isolamento

Sono state create tramite API ordinarie tre nuove aree e tre nuove CompilationSession; il browser Playwright ha usato la UI React reale, il composer, le richieste della chat e il download ordinario. Nessuna intercettazione di risposte, nessun mock del provider, nessuna modifica manuale di stato o ricevute. Database/storage di esecuzione sono copie isolate; il database originale è stato aperto soltanto in lettura.

| Documento | Sessione nuova | Conversazione |
|---|---|---|
| Minervino | `3ad3e88c5af2485d96d70413fc050cb3` | `conv-75632ccfa01d4669` |
| Trapani | `b1e0e580235e485c8716a958e95065ef` | `conv-7300a3d967714770` |
| Catanzaro | `e7a4e500e6444d378288e8954e9100e7` | `conv-a75abca0898d49c8` |

Una sola generazione globale reale per documento, con output nuovo e immutato; zero riusi di output congelati, zero retry di qualità. I successivi passaggi di router, verifica delle risposte e narratore sono anch'essi reali. Il conteggio totale delle chiamate comprende tutti questi passaggi.

Il protocollo, gli scenari e i riferimenti sono stati salvati prima della prima chiamata. Massimo due turni USER di risposta ai chiarimenti per ciascun documento, poi richiesta esplicita della bozza parziale. Questo limite riduce i gradi di libertà dell'operatore; non è un limite imposto al prodotto. Le domande rimaste aperte non sono state trasformate in conferme per migliorare il risultato.

**Scenario sintetico, distinto per ciascuna procedura:** Mapi partecipa singolarmente come società di ingegneria; nessun raggruppamento/consorzio o partecipazione contemporanea in altre forme. Leonardo Montemurro è scelto separatamente come firmatario per ogni domanda. Dati e ruolo personale devono comunque essere provati dalle SOURCE. Preferenze, attestazioni, esecutori, integrazione delle prestazioni, allegati effettivi e luogo/data restano non decisi. La situazione aziendale di riferimento è il 15 ottobre 2026; non è una verifica dell'idoneità storica alle gare originarie. Non sono stati trasferiti consensi o designazioni da una procedura all'altra.

L'input iniziale esplicitava già le scelte; il percorso corrente richiede comunque la loro registrazione in risposta a uno slot. Sono state ripetute solo le scelte presenti nello scenario. I dati anagrafici non sono stati forniti come presunte prove USER.

## 3. Versione, FORM, modello, prompt e SOURCE

Codice: branch `prune-backend`, HEAD `99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e`, working tree già modificato all'inizio. Il commit da solo **non identifica** questa pipeline. Il manifest conserva gli hash dei 318 file protetti, la patch preesistente e il codice nel bundle. Digest dell'inventario protetto: `28b6bd3aaa71b48cd02a8727cdba0e9bb6d226faf2d69b1399959e3860d1f428`.

| FORM | SHA-256 originale | Candidati tecnici |
|---|---|---:|
| Minervino | `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c` | 267 |
| Trapani | `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701` | 115 |
| Catanzaro | `5b3ad083522b9261c3c45584ac5ce08d73996269eaf0c6c07b7b8c3df3974563` | 307 |

Provider DeepSeek, endpoint `https://api.deepseek.com`, modello richiesto e restituito **`deepseek-flash`**, fingerprint delle tre globali **`e72d3c7f663d3e1383b00b3884cb4501`**. Il tariffario ufficiale acquisito identifica l'alias come DeepSeek-V4.1-Flash-1017; l'API non restituisce un identificativo immutabile più preciso. La riproducibilità futura dello stesso alias non è garantita.

Configurazione globale effettiva: thinking `enabled`, `reasoning_effort=low`, `max_tokens=49152`, temperatura `0.1`, timeout del percorso 300 s. Router/narratore usano le impostazioni effettive archiviate, con thinking disabilitato. La preferenza del profilo `thinking=false` non descrive la chiamata globale: non è stata cambiata la pipeline per questo benchmark. La dimensione configurata del contesto nel profilo è 32768, ma i prompt reali globali sono più grandi e il provider li ha accettati: le misure usano l'usage restituito, non una stima dal profilo.

Il system prompt globale è uguale nelle tre richieste: SHA-256 `978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`. Ogni cartella contiene richiesta completa, system prompt, risposta e audit; nel bundle ci sono anche tutti i prompt/risposte di router, guard e narratore, con schema, HTTP, finish reason, tempi e uso token. Nessun GOLD o risultato atteso è stato passato al modello.

**Stesso snapshot di 22 chunk in tutte e tre le globali**, 18 Company e 4 General: `generalita-mapi.md`, `visura-mapi-ingegneria-simulata.pdf`, `integrazione-company.md`, `progettazione-opere-pubbliche.txt`. Sono conservati gli originali e i chunk. I nuovi progetti non aggiungono SOURCE specifiche dei bandi: è il controllo scelto per usare la stessa KB in tutte le prove. Non si può quindi attribuire al modello la mancata lettura di CIG o prescrizioni presenti soltanto negli avvisi/disciplinari esclusi.

Il corpus congelato ha SHA `0982378194a2e3e769ed3e18dc8d92bf6c1c70f6c4e8b5aa9bbf6d236093ff0c`. La normale serializzazione omette metadati di presentazione (`excerpt`, `relevance`, `document_metadata`); **il contenuto integrale dei 22 chunk e i dati di provenienza sono conservati**. `input/SOURCE-input-LLM.json` e `input/provenienza-richieste.json` distinguono questa proiezione dal corpus e provano l'uguaglianza dei tre input SOURCE effettivi.

## 4. Minervino: 55 scritture, sei omissioni residue

La globale propone tutti i 60 campi SOURCE del riferimento. Al primo stato sono grounded 45; dopo la ricevuta USER il riuso SOURCE esistente recupera nove proprietà del firmatario, arrivando a 54. Tutte sono revisionate, applicabili ed effettivamente scritte. Una checkbox USER, `p39.cb0`, seleziona il ramo societario: totale 55. Tutti i 24 campi dei tre soci sono nel Word, senza trasferire loro i poteri di Leonardo. Nessun hold del narratore residuo.

| Campi vuoti | Dato disponibile e presente nell'input | Esito dimostrato |
|---|---|---|
| `p15.s1` provincia iniziale | BA | Proposta respinta: la citazione FORM è il solo marker, senza richiesta documentata. |
| `p41.s1` Comune della sede | Bari | Il modello propone l'intero indirizzo. Rifiuto necessario del validatore Comune; Bari era presente separatamente nella SOURCE. |
| `p51.s0`, `p52.s0`, `p53.s0`, `p53.s1` | Nome, qualifica, ordine, sezione di Elisa | Rifiuto del collegamento soggetto–ruolo–valore. La prova completa è nell'input, ma il binding scelto usa intestazione/ruolo di `-45`, mentre i valori sono nella tabella `-54`; non include l'asserzione nominativa completa disponibile in `-55`. |

Gli altri quattro dati del direttore tecnico — CF, provincia, data e numero d'iscrizione — vengono scritti. La sezione è quindi incompleta pur contenendo valori corretti. I quattro vuoti non sono prodotti dagli hold che erano oggetto dell'intervento precedente: questa nuova proposta presenta evidenze diverse e fallisce prima, nel grounding del binding. Non è stato aggirato il controllo.

Confronto con GOLD: 45 dei 54 testi scritti sono letteralmente uguali al riferimento; gli altri nove sono giustificati da fonte e proprietà: data equivalente, carica più completa documentata, nomi senza prefisso professionale, provincia “Bari (BA)” invece di “Bari”. Nessuna di queste differenze è un errore fattuale. I quattro testi USER del riferimento gold — due posizioni esecutori, integrazione, luogo/data — restano vuoti perché lo scenario attuale non contiene quelle decisioni. Attestazioni e preferenze restano non selezionate.

La precedente prova da 61 scritture aveva output globale congelato e 56 SOURCE complessive; questa usa una generazione nuova e 22 chunk comuni. **Non è un confronto causale sul solo codice**, né una replica dello stesso input. La perdita di sei scritture rispetto a 61 non autorizza a dichiarare una regressione deterministica del writer o della correzione degli hold.

## 5. Trapani: nove dati corretti e un'accettazione non autorizzata

La globale propone dieci assegnazioni e nove fatti aziendali distinti. Nove scritture compilano correttamente il blocco società di ingegneria: denominazione, via, Comune, CAP, provincia, PIVA, telefono, fax e PEC. Il fax `+39 080 000 2041` ha prova esplicita nell'integrazione Company `-53`; non è un recapito personale inventato.

La decima è **`p107.s0`**, la stessa PEC, nella clausola che inizia con “di accettare che ogni comunicazione relativa all'Avviso…” e prosegue attribuendo al dichiarante il rischio dell'operatività dell'indirizzo. La proposta la classifica `kind=data`, `disposition=value`, con `conditions=[]`; la prova è la PEC aziendale in `-44`. Il campo supera grounding e revisione e arriva nel DOCX, pagina 3.

**Fatto osservato:** il valore PEC è documentato; il contesto FORM è una dichiarazione di accettazione; nessuna ricevuta USER conferma quell'accettazione o sceglie il recapito per la procedura. Il riferimento preregistrato lasciava proprio `p107.s0` UNKNOWN. **Valutazione:** compilare questo campo rende completa una dichiarazione che non era autorizzata dallo scenario. È una scrittura indebita di contesto/decisione, non una PEC allucinata. Le altre clausole prestampate, lasciate immutate, non vengono contate come nuove scritture.

Gli otto campi iniziali del sottoscrittore sono omessi dalla globale, senza proposte respinte. La spiegazione MODEL sostiene che il ruolo generico di sottoscrittore non è collegabile al rappresentante legale: **non è prova dell'assenza dei dati**. Nome, nascita, residenza e CF di Leonardo sono integralmente nell'input. La scelta esplicita del firmatario compare anche nella ricevuta finale di questa sessione.

Il recupero deterministico esistente non interviene: `_form_groups` / `_SIGNATORY` riconoscono una specifica grammatica inline a dieci marker, con “Il sottoscritto … residente in … in qualità di … dell'operatore economico”. Trapani ha “Il/la sottoscritto/a”, otto marker, numero civico distinto e qualifica successiva. Il parser restituisce **zero gruppi supportati**, contro uno in Minervino. È un limite concreto di copertura del riuso, non una nuova decisione necessaria sui dati anagrafici. Nessuna modifica effettuata.

Restano irrisolti CIG, iscrizione professionale personale, categoria MEPA, iscrizioni regionali/specialistiche, servizi documentati e luogo/data. I dati procedurali non disponibili nello snapshot e le attestazioni non confermate devono restare irrisolti. Non si possono usare l'iscrizione di un socio per Leonardo o le competenze generali della KB per attestare requisiti di questa procedura. Il sistema non chiede però il consenso relativo alla PEC prima di scriverla e non affronta molte attestazioni mancanti.

## 6. Catanzaro: 13 scritture, copertura incompleta

La globale contiene 16 record campo: **15 proposte di valore e un `not_applicable`** per la sede operativa, uguale a quella legale. Tredici proposte di valore passano i controlli e vengono scritte: sei dati generali dell'operatore, tre dati del ramo società di ingegneria e quattro del direttore tecnico. Il campo “data di abilitazione” resta giustamente vuoto: la data d'iscrizione all'Ordine non dimostra la data di abilitazione. Nessuna checkbox nuova selezionata; nessuna scrittura fuori sezione rilevata.

| Gruppo del riferimento SOURCE rimasto vuoto | Numero | Causa |
|---|---:|---|
| Firmatario iniziale, nascita, CF, carica | 4 | Omissione LLM; spiegazione MODEL di ruolo non coincidente. Dati presenti nell'input; grammatica tabellare non supportata dal riuso inline. |
| CCIAA | 1 | Proposta respinta per estratto FORM esterno al contesto strutturale locale. Bari documentata. |
| Numero **e data** iscrizione azienda | 1 | Omissione LLM: dice che non sono disponibili come dato unitario, sebbene i due valori siano documentati nell'input. Non è dato assente dalla KB. |
| Leonardo nelle due tabelle di amministrazione/rappresentanza, cinque proprietà ciascuna | 10 | Omissioni LLM; parte terza mantenuta UNKNOWN e nessun binding proposto. Il FORM include espressamente le società di ingegneria, ma il collegamento alla decisione ricevuta non è costruito. |
| Nome direttore tecnico nella parte terza | 1 | Proposta respinta per contesto FORM non locale. |
| CF direttore tecnico nella parte terza | 1 | Omissione LLM: raggruppato erroneamente con nascita/residenza realmente mancanti. CF presente nella tabella SOURCE `-54`. |

Totale 18: 16 omissioni, due rifiuti. Non sono 18 proposte grounded sospese. La parte terza resta UNKNOWN, ma manca già la proposta di dieci valori: portare la sola condizione a TRUE non li recupererebbe. Non è stato fatto.

La scelta società di ingegneria viene registrata soltanto per `c_soc_ing`, che governa i dati aziendali/tecnici. `c_tipologia`, `c_forma_part`, `c_parte3` e le altre condizioni non vengono collegate. **Zero `choice_groups` nella nuova risposta globale.** Il gruppo societario e i due gruppi di partecipazione sono spiegati come `condition_unknown` nella coverage, senza un gruppo strutturale validato. Le tre selezioni autorizzate nello scenario (`p57.cb0`, `p76.cb1`, `p147.cb0`) restano quindi vuote. Non sono state spuntate manualmente.

Ulteriore limite osservabile: la ricevuta accettata di Catanzaro conserva soltanto la prima frase della risposta sulla società, non la frase successiva sul firmatario. La scelta di Leonardo resta nella conversazione, ma non diventa una ricevuta di selezione personale utilizzabile. È distinto dal limite della grammatica tabellare, già sufficiente a impedire il riuso.

Nascita/residenza di Elisa, abilitazione professionale, attestazioni, allegati effettivi e requisiti specifici non sono dimostrati dallo snapshot. Le righe aggiuntive non implicano persone da inventare. Non si deducono organi di vigilanza, amministratori di fatto o soci unici dai ruoli aziendali. La società a tre soci naturali non giustifica la compilazione automatica dei rami SNC/SAS, socio unico o socio persona giuridica.

Le cinque differenze letterali nei 13 testi corretti sono giustificate: forma giuridica senza accenti ripresa dalla fonte, indirizzo con “Italia”, nome del direttore con prefisso “Ing.”. Nessun GOLD indipendente per Trapani/Catanzaro: il riferimento è la revisione autoriale preregistrata, non una nuova verità adattata all'output.

## 7. Dialogo: decisioni mancanti e ripetizioni

In tutti e tre i casi si osserva lo stesso falso chiarimento. La prima conferma USER include la scelta singola e la negazione “senza raggruppamenti o consorzi”. Router propone `CONDITION_TRUE`, guard risponde `SUPPORTED`, ma `apply_replies` la respinge perché `has_user_alternatives` trova il token “ o ” anche nella negazione. Il secondo messaggio, che ribadisce la stessa decisione senza quella costruzione, viene accettato. Non sono state aggiunte scelte nuove. Il costo comprende le chiamate spese in questa ripetizione.

Minervino mostra sei decisioni distinte pertinenti: conferma del ramo, luogo/data, preferenze, attestazioni, esecutori e integrazione. Le prime cinque ricevono una risposta entro il budget (quattro rinvii, una conferma); integrazione resta aperta. Presenta inoltre due domande sui rami studio associato e capogruppo RTI, già esclusi dalla scelta singola come società: sono superflue rispetto allo scenario. Nove esposizioni complessive, incluse la ripetizione e queste due alternative.

Trapani chiede soltanto ramo e luogo/data, con una ripetizione del ramo. Catanzaro chiede soltanto il ramo, due volte. Poche domande **non equivalgono a dialogo sufficiente**: mancano richieste pertinenti al firmatario non recuperato e alle decisioni/attestazioni del FORM. Dopo la conferma entrambi offrono direttamente l'export parziale.

| Gruppo decisionale | Minervino | Trapani | Catanzaro |
|---|---|---|---|
| Preferenze categorie/fasce | chieste e rinviate | nessuna scelta inventata; eventuali categorie/requisiti non dimostrati | nessuna preferenza trasferita |
| Attestazioni/consensi | chieste e rinviate; checkbox vuota | non chiarite; violazione sulla PEC | non chiarite; nessun nuovo consenso scritto |
| Esecutori | chiesti e rinviati | non designati | non designati |
| Integrazione prestazioni | domanda ancora aperta | nessuna designazione | nessuna designazione |
| Luogo/data | rinviati | rinviati | non chiesti; lasciati vuoti dove previsti |

I cinque gruppi restano separati. L'export è sempre disponibile anche con rinvii e UNKNOWN. Non si è usato un generico “confermo” per attestare tutti i requisiti. In queste tre conversazioni **non emergono hold fattuali legittimi** da mettere alla prova; il benchmark non dimostra da solo il comportamento su tali casi negativi, già oggetto di test storici che non sono stati rieseguiti qui.

## 8. Token, tempi, costo ed errori

| Misura | Minervino | Trapani | Catanzaro |
|---|---:|---:|---:|
| Chiamate totali / globali | 11 / 1 | 10 / 1 | 9 / 1 |
| Token input, tutte le chiamate | 153.082 | 89.087 | 124.312 |
| Token output, incluso reasoning | 44.133 | 16.437 | 36.150 |
| Token totali | **197.215** | **105.524** | **160.462** |
| Input / output della sola globale | 61.785 / 42.522 | 41.923 / 15.547 | 84.045 / 35.484 |
| Reasoning globale | 27.034 | 11.663 | 27.080 |
| Output globale senza reasoning, per differenza usage | 15.488 | 3.884 | 8.404 |
| Tempo provider della sola globale | 155,56 s | 63,82 s | 133,32 s |
| Somma tempi provider, percorso intero | 175,71 s | 77,88 s | 145,72 s |
| Prima–ultima chiamata, incluse pause operatore | 315,52 s | 10.668,29 s | 292,26 s |
| Costo stimato sola globale, USD | 0,033746 | 0,014582 | 0,032862 |
| Costo stimato percorso intero, USD | **0,044531** | **0,019048** | **0,036367** |
| Errori HTTP provider / retry di qualità | 0 / 0 | 0 / 0 | 0 / 0 |

Totale: **30 chiamate reali, 463.201 token, circa 0,099946 USD stimati**. Tre globali, dodici router, sei guard e nove sintesi. Tutte le risposte provider HTTP 200, finish reason `stop`; nessun output troncato o retry nascosto rilevato. Il reasoning è già compreso nei completion token e non viene addebitato due volte nel calcolo.

Stima da cache hit/miss e completion dichiarati dal provider, usando il [tariffario ufficiale DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/) acquisito prima delle prove: fascia non di punta, USD/milione 0,003 input cached, 0,15 input non cached, 0,60 output. Le chiamate sono fuori dalle finestre di punta UTC indicate nella copia del tariffario. **È una stima, non una fattura o il saldo dell'account.** Singole richieste e formula in `chiamate-metriche.json`.

La pausa fra i due turni Trapani e il riavvio del runtime dopo “riprendi” rendono il suo wall time inadatto a confrontare la velocità della pipeline. È stata ripristinata **la stessa sessione alla versione 6**, senza nuova globale o reinvio del primo messaggio. La somma dei tempi HTTP è una misura più pulita del costo temporale delle richieste, ma non include tutti i tempi locali e non sostituisce una distribuzione di latenza su più repliche.

I driver registrano 10 GET abortite su mount/reload in ciascuna acquisizione finalizzata, senza errori di pagina/HTTP acquisiti. Non sono retry LLM. La prima parte browser di Trapani conserva DOM, screenshot, rete ed eventi, ma non ha finalizzato il primo trace e i dettagli errori a causa dell'interruzione del processo. La continuazione ha trace/video e download verificati. Il limite di acquisizione è conservato, non corretto retroattivamente.

## 9. Verifica degli artefatti

Per ciascun DOCX: ZIP/CRC, parsing di XML e relazioni, posizioni di tutte le sostituzioni, preservazione del prestampato, numero di paragrafi salvo il banner bozza previsto, geometria e fusioni delle tabelle, valori fisici delle checkbox. L'unica parte ZIP modificata è `word/document.xml`. I DOCX scaricati dalla UI coincidono byte per byte con quelli salvati dall'export. Nessuna firma inserita. Nessuna deselezione di checkbox o effetto booleano nascosto.

Tabelle fisiche nell'XML: 4 Minervino, 6 Trapani, 50 Catanzaro; i conteggi della vista semplificata/python-docx per Trapani sono inferiori e non indicano che siano state aggiunte tabelle. Si confronta sempre l'XML originale con l'esportato.

Nuova conversione LibreOffice degli export effettivi: PDF di 9/5/17 pagine. Controllati i bounding box del testo su **tutte le 31 pagine**, zero parole fuori pagina. Ispezione visiva delle pagine 1/3/9 Minervino, 1/2/3/5 Trapani e 1/2/11/17 Catanzaro: campi scritti leggibili, nessuna sovrapposizione evidente nelle pagine esaminate, firma/linea nell'ultima pagina. Non è un'ispezione visiva esaustiva di ogni pagina. Restano spaziature giustificate ampie e giunzioni come “professionaleOrdine” o “Fax+39”, difetti cosmetici già compatibili con l'export attuale. Il warning linguistico locale di LibreOffice è archiviato; conversione riuscita, DOCX immutato.

Un verificatore offline, con rete vietata, ricostruisce da output globali reali, SOURCE e ricevute effettive gli audit finali **identici** e i tre DOCX **identici byte per byte**. Non sostituisce la valutazione semantica: ricostruisce anche l'errore PEC di Trapani.

| DOCX | SHA-256 |
|---|---|
| Minervino | `c2d03fb53ae7baf30b876b3b7a2e34a4beccbd9aac0c12e6319198b15564a6ac` |
| Trapani | `2cb8c448475714f234fafcccd535f2b3e9e6d3fade23b2908aa2689e2652fbbb` |
| Catanzaro | `aa940efde8dcc76796b07e247f59baceaaa8ab2af0e092681c58aba60ac9a7b0` |

## 10. Giudizio e decisione proposta

**Bloccante per il criterio di congelamento richiesto:** Trapani `p107.s0`, completamento non autorizzato della clausola PEC. Non è sufficiente che tutti i valori passino i validatori e che il DOCX si apra. Non propongo V12 come baseline affidabile su tutti e tre i documenti.

**Importanti ma non bloccanti per la sola integrità di una bozza parziale:** dati documentati omessi, grammatica del riuso limitata, motivazioni MODEL troppo prudenti o inesatte, associazioni fra rami/checkbox non costruite, rifiuti FORM locali, falso chiarimento dovuto alla negazione con “o”, domande pertinenti mai poste. Minervino è una bozza utile con sei omissioni SOURCE note; Catanzaro è strutturalmente utilizzabile ma ancora povera di identificazione/decisioni. Trapani richiede prima la revisione della scrittura indebita; il suo file è consegnato esattamente come prodotto.

**Cosmetici:** spaziatura, giunzioni etichetta–valore e differenze ortografiche non fattuali; nessuna modifica al writer eseguita.

**Limiti sperimentali:** una sola replica per documento; scenario sintetico; KB comune senza allegati di procedura; GOLD indipendente solo Minervino; denominatore globale di tutti gli adempimenti non ancora definito; niente stima statistica di robustezza; pausa tecnica Trapani. Nessuna conclusione causale sull'E1 compatto o sulla velocità rispetto ai vecchi esperimenti. La fixture fissa `benchmark-compilazione/v1` non è stata eseguita qui: è una valutazione separata dei tre documenti storici espressamente richiesti, non un'estrazione casuale di un bando aggiuntivo.

Per un eventuale passo successivo suggerisco di affrontare prima il solo confine fra dato SOURCE e scelta/attestazione procedurale dimostrato da Trapani, con test negativi ed evidenze di destinazione. Non è stata implementata alcuna correzione e non è stato avviato E1. Il formato FORM, il modello e i controlli attuali sono rimasti invariati.

## 11. Consegna e conservazione

In ciascuna cartella `minervino`, `trapani`, `catanzaro`: FORM originale, bozza DOCX/PDF, report ordinario di validazione, verifica XML/PDF, dialogo, stato, valutazione per candidato in JSON/CSV, omissioni SOURCE, valutazione delle domande, metriche aggregate/per richiesta, richiesta/risposta globale e audit iniziale/finale. `riferimento-valutazione.json` e `scenario-USER.json` sono quelli preregistrati, non riscritti.

Il grezzo completo è in `backend/data/compilation-audit/ufficiale-v12-20261019-01/`. Il backup `audit-completo.tar.gz` in questa directory conserva richieste/risposte HTTP, prompt/schema, ricevute, transizioni, conversazioni, acquisizioni browser, rendering, script e codice congelato, senza database privato o credenziali. Il manifest SHA e le istruzioni di verifica sono in `BACKUP.json` e `README.md`.

Controlli di conservazione: 318 file app/test/frontend/fixture invariati, 26 input preregistrati invariati, 645 artefatti precedenti invariati, 29 sessioni originali e 285 file storage originali invariati; anche le 29 sessioni copiate non sono state alterate. Tre sole sessioni nuove. Schema DB intatto. Servizi isolati arrestati. Nessuna modifica applicativa, nessun commit/push. Le suite software complete non sono state rieseguite: qui si riportano verifiche sui nuovi artefatti e chiamate reali, non si riattribuiscono test storici alla prova odierna.

**Arresto al termine del benchmark: risultati consegnati, baseline non adottata.**
