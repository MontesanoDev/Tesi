# V12 invariata su tre bandi estratti casualmente

19 ottobre 2026 — esperimento `casuali-v12-20261019-01`.

**Le prove confermano limiti di generalizzazione.** CRAA produce nove scritture SOURCE nell'XML, ma soltanto sette sono leggibili nel PDF: due dati CCIAA finiscono in celle troppo strette. Bella scrive quattro dati aziendali e omette quattro proprietà documentate del firmatario. Cesano Maderno esporta una copia senza valori aggiunti. Nessuna scrittura fattuale indebita rilevata nei tre risultati; questo non rende soddisfacente una compilazione quasi vuota. Nessuna modifica alla pipeline, nessun nuovo esperimento E1, nessun commit/push o adozione di baseline.

## 1. Campionamento e limiti

Prima della ricerca sono stati fissati pool obiettivo di otto procedure, criteri di ammissione, seed e algoritmo. [Protocollo](PROTOCOLLO.json), [pool congelato](POOL.json), [estrazione](ESTRAZIONE.json), [metodo e limitazioni](METODO-CAMPIONAMENTO.json).

Il pool comprende i primi otto moduli DOCX originali ammissibili di procedure diverse trovati durante la ricerca: MIT elenco SIA 2022, Cesano Maderno, CRAA, Cannara, So.Re.Sa. accordo quadro 2023, MIT supporto al RUP 2023, Bella e Consiglio regionale Calabria. Le pagine istituzionali o le piattaforme collegate attestano la provenienza. Le ricerche iniziali hanno restituito molti PDF, DOC e documenti estranei: la ricerca è stata estesa prima dell'estrazione, mantenendo gli stessi criteri. Non tutte le query erano quindi prefissate; seed e dimensione del pool lo erano.

Sono stati esclusi prima del sorteggio documenti non SIA, moduli principali solo DOC/ODT/PDF, allegati che erano soltanto schede di servizi/offerte economiche, il DOCX ARPA FVG con link 404 e Trapani già utilizzato. Bisceglie è il nono candidato ammissibile, oltre il limite del pool; non è stato incluso. Download ed esclusioni sono conservati. Il payload grezzo della prima ricerca non è stato acquisito; sono dichiarati gli esiti pertinenti e conservate le acquisizioni delle ricerche successive.

Algoritmo: ordinamento per URL canonico, rimozione del solo `;jsessionid` transitorio, `random.Random(seed).sample(pool, 3)`. Seed: **`Mapi-V12-bandi-casuali-2026-10-19-01`**. Una sola estrazione, in ordine **CRAA → Bella → Cesano**. Nessuna selezione per lunghezza, numero campi o risultato di compilazione; nessun documento sostituito dopo l'estrazione.

**È un campionamento casuale entro un pool di convenienza trovato sul web, non un campione casuale di tutti i bandi italiani.** Una replica per documento è esplorativa, senza stima statistica di accuratezza. I tre documenti ora sono casi osservati: se verranno usati per correggere il sistema, servirà un diverso lotto riservato alla futura valutazione. Nessun ulteriore holdout è stato eseguito.

## 2. Condizioni controllate

Nuovo database/storage isolato copiato dal sistema locale; tre nuovi progetti e sessioni avviati dalla UI reale. Upload, mention del modulo, composer, risposte, avanzamento ed export ordinari. Nessun mock, proposta congelata, revisione manuale dello stato o patch al codice applicativo. Tre generazioni globali nuove, una per FORM, senza ripetizioni selettive. Richieste provider osservate e inoltrate immutate.

Stessa KB del benchmark storico: **22 chunk, 18 Company e quattro General**, stessi originali e contenuti. Nessuna SOURCE specifica del bando aggiunta. L'uguaglianza dei tre input SOURCE effettivi e con il corpus precedente è verificata; nessun GOLD nel prompt.

Per ogni procedura è stato scritto separatamente, prima delle chiamate, uno scenario sintetico: Mapi partecipa singolarmente come società di ingegneria e sceglie Leonardo Montemurro come firmatario. Anagrafica, ruolo e poteri richiedono comunque le SOURCE. Stato aziendale al 15 ottobre 2026; non è una verifica dell'idoneità alle date delle gare storiche.

Preferenze, attestazioni/consensi, esecutori, integrazione delle prestazioni e luogo/data restano distinti e UNKNOWN. Nessun consenso PEC, allegato, abilitazione o designazione inventati. Si risponde soltanto agli slot effettivamente chiesti, fino a due turni di risposta; poi export esplicito. CRAA e Bella usano due turni per la stessa conferma ripetuta; Cesano non presenta chiarimenti e passa direttamente alla richiesta di copia vuota. I cinque gruppi di decisioni mancanti non sono stati confermati implicitamente.

Codice: HEAD **`99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e`**, branch `prune-backend`, working tree preesistente preservato. Digest dell'inventario dei 318 file protetti: **`28b6bd3aaa71b48cd02a8727cdba0e9bb6d226faf2d69b1399959e3860d1f428`**. Il codice effettivo e la patch preesistente sono nel backup: il solo commit non identifica questa versione.

Provider DeepSeek, modello richiesto/restituito **`deepseek-flash`**, fingerprint globale comune **`e72d3c7f663d3e1383b00b3884cb4501`**. Globale: thinking `enabled`, reasoning `low`, temperatura 0,1, massimo output 49.152 token; nessun parametro modificato. Prompt/schema completi e corpi HTTP sono archiviati; il profilo conversazionale con thinking disabilitato non descrive l'impostazione globale. L'alias del provider non è un identificativo immutabile.

## 3. Risultati separati per fase

| Misura | CRAA | Bella | Cesano Maderno |
|---|---:|---:|---:|
| Candidati nel percorso reale della chat | 51 | 67 | 68, tutti checkbox |
| Nucleo di occorrenze SOURCE documentate prima delle chiamate | 10 | 8 | 4 senza destinazione testuale supportata |
| Assegnazioni di valore proposte dalla globale | 9 | 4 | 0 |
| Grounded al primo stato / finali | 9 / 9 | 4 / 4 | 0 / 0 |
| Grounded applicabili finali | 9 | 4 | 0 |
| Proposte revisionate | 9 | 4 | 0 |
| Testi effettivamente scritti nell'XML | **9** | **4** | **0** |
| Testi fattualmente corretti e nella destinazione prevista | 9 | 4 | 0 |
| Di questi, leggibili nel PDF LibreOffice | **7** | **4** | **0** |
| Dati scritti ma non visibili nel PDF | **2** | 0 | 0 |
| Testi USER scritti / nuove checkbox selezionate | 0 / 0 | 0 / 0 | 0 / 0 |
| Nuove scritture fattuali o decisioni indebite rilevate | 0 | 0 | 0 |
| Nucleo SOURCE rimasto vuoto nell'XML | 1 | 4 | 4 |
| Di questi: assegnazioni omesse dal modello | 1 | 4 | 0 |
| Di questi: destinazioni non esposte al modello | 0 | 0 | 4 |
| Proposte SOURCE respinte | 0 | 0 | 0 |
| Chiarimenti proposti, poi respinti | 1 | 0 | 1 |
| Hold finali / valori grounded ancora UNKNOWN | 0 / 0 | 0 / 0 | 0 / 0 |
| Condizioni effettive TRUE / UNKNOWN | 1 / 4 | 1 / 1 | nessuna condizione proposta |
| Domande mostrate / distinte / duplicate | 2 / 1 / 1 | 2 / 1 / 1 | 0 / 0 / 0 |
| Export e PDF ordinari | sì, 7 pagine | sì, 4 pagine | sì, 3 pagine, copia senza valori |

Le 10/8/4 sono **occorrenze del nucleo SOURCE**, non fatti atomici distinti o totale di tutti gli adempimenti. Una cella può essere di impaginazione e una tabella può avere cardinalità variabile. Attestazioni, requisiti speciali e designazioni non dimostrati restano fuori da un denominatore definitivo. Non essendoci GOLD indipendenti per questi moduli, non dichiaro percentuali globali di accuratezza.

La conformità fattuale nell'XML è distinta dalla leggibilità: i due campi CRAA non visibili non vengono contati come valori utilizzabili nel PDF. La copia Cesano è un **fallimento funzionale della compilazione**, anche se stato `GENERATED`, ZIP valido e assenza di invenzioni sono esiti tecnici corretti.

## 4. Cause dimostrate

### CRAA: perdita del chiarimento e celle quasi nulle

Originale dal [portale CRAA, procedura E00008](https://craa-appalti.maggiolicloud.it/PortaleAppalti/it/ppgare_oper_ec_bandi_avvisi.wp?actionPath=/ExtStr2/do/FrontEnd/Bandi/viewIscrizione.action&codice=E00008&currentFrame=7). La domanda è la dichiarazione cumulativa per l'iscrizione all'elenco SIA. L'originale ha SHA **`4ce8fbc2730a21e86d9b68cf5e9d6d7a530da82272554d6b9baa315c2bcef3ab`**.

Sette dati aziendali iniziali vengono proposti, verificati, scritti e letti nel PDF: denominazione, sede, PEC, CF, PIVA, mail, telefono. Le due proprietà CCIAA sono proposte condizionalmente, poi autorizzate dalla ricevuta sulla sezione societaria e scritte nell'XML. Nessuna attestazione o categoria viene selezionata.

**Firmatario `p5.s0`:** nome documentato nelle SOURCE e presente nell'input; scelta USER già nel messaggio iniziale registrato. Il modello omette l'assegnazione e propone invece un chiarimento, motivandolo con una pretesa differenza tra ruolo societario e sottoscrittore. La motivazione è lunga **225 caratteri**, oltre il limite 200 di `UserFieldRequest.reason`. Il chiarimento viene respinto, perciò il nome non viene chiesto e non viene scritto. Non è una proposta di valore respinta dai validatori SOURCE. Il riuso esistente riconosce zero gruppi anagrafici inline in questo FORM; la ricevuta accettata sul ramo societario non conserva la frase sul firmatario. Queste due limitazioni impediscono anche un recupero successivo. [Traccia](craa/diagnosi-firmatario.json).

**CCIAA `t6.r0.c1` e `t6.r0.c3`:** l'XML contiene rispettivamente Bari e `01234560981`, nelle posizioni riportate dal normale export. Il PDF di pagina 4 mostra però entrambi i campi vuoti; il numero non compare nel testo estratto da nessuna pagina. Le celle del modello sono larghe **66 e 81 twip**, cioè circa **3,3 e 4,05 punti**, con tabella a layout fisso. Le dimensioni sono identiche prima/dopo: il writer non le ha allargate.

Il mancato rendering è osservato e verificato in LibreOffice. Le larghezze costituiscono una forte spiegazione strutturale del problema; non è stata sperimentata una modifica della geometria né verificato Microsoft Word desktop. Non trasformo questa diagnosi in una garanzia su tutti i renderer. I due valori sono fattualmente corretti ma **non fruibili nel PDF consegnato**. La classificazione di celle vuote molto strette come destinazioni valide merita verifica futura. [Diagnosi XML/PDF](craa/diagnosi-visibilita-CCIAA.json).

Rifiuti/irrisolti necessari: rami professionista singolo/studio associato, self-cleaning, avvalimento, CCNL, qualificazioni e fatturato richiesto non dimostrati. Le cifre annuali della KB non attestano automaticamente il miglior triennio nell'ultimo quinquennio. Le checkbox del documento CRAA sono glifi testuali, senza controlli nativi riconosciuti dal catalogo: nessuna nuova spunta esportata.

### Bella: omissioni personali e gruppo di scelta respinto

Originale dalla [procedura del Comune di Bella su ASMECOMM](https://piattaforma.asmecomm.it/gare/dettaglio.php?codice=11368), domanda e dichiarazioni per progettazione dell'intervento ex municipio. SHA **`4d894b3faee91909275589ac5ed8e1dd2eddc09890f95ac0456780bbb6828ae0`**, coincidente con l'hash pubblicato sulla piattaforma.

Quattro campi proposti e scritti: società, sede, CF e PIVA della società (`p21.s4`–`p21.s7`). Sono supportati e leggibili. **Nome, luogo/data di nascita e carica del firmatario (`p21.s0`–`p21.s3`) sono omessi**, con tutti i dati presenti nell'input SOURCE. Il modello dichiara di non avere prova SOURCE del ruolo di sottoscrittore di quella domanda e considera il ruolo societario non identico alla richiesta “in qualità di”. Sono spiegazioni MODEL, non prove che i dati siano assenti o che i validatori avrebbero rifiutato una proposta corretta.

Il riuso anagrafico inline non riconosce questo modulo, che ha otto marker e una struttura diversa. La ricevuta finale conferma la partecipazione singola come società, senza conservare la successiva frase personale: nessuna selezione nominativa utilizzabile dal riuso. Non sono stati trasferiti valori da altri benchmark.

La globale propone sette gruppi di checkbox. `g_partecipazione` è respinto con **“Etichetta opzione assente nell'estratto FORM”**; varie opzioni lunghe sono citate in modo incompleto. Di conseguenza la scelta societaria disponibile nello scenario non arriva a `p30.cb0`. Il gruppo sui tecnici risulta strutturalmente grounded ma con cardinalità UNKNOWN: non autorizza la designazione di persone. Altri cinque gruppi dichiarati esclusivi sono respinti perché incompleti rispetto alla lista fisica Word. Non si è corretto o completato manualmente alcun gruppo.

Il ramo RTP/giovane professionista non è quello scelto. Esecutori della prestazione, abilitazioni specifiche, attestazioni, consensi e data non sono confermati. Lasciarli vuoti evita attribuzioni indebite; manca però un dialogo che distingua questi casi dalle omissioni recuperabili.

### Cesano Maderno: testo non indirizzabile e chiarimento sul tipo sbagliato

Originale dalla [pagina istituzionale dell'elenco SIA di Cesano Maderno](https://www.comune.cesano-maderno.mb.it/amministrazione/documenti-e-dati/bandi/altri-bandi/22d8f1a8-2987-4d87-37a1-08dc49b2da88/), Allegato A. SHA **`9386c79ef24b99c9e6b70eca9e1dbee5de187febc241f1d87b5ce3787016e795`**.

Il documento contiene **20 campi testuali legacy Word `FORMTEXT` e 68 checkbox native**. Il preflight generico `inspect_docx` con impostazioni predefinite rifiuta il modello per assenza di celle vuote/segnaposti testuali supportati. Il percorso reale CompilationSession usa invece l'ispezione senza obbligo di candidati testuali e costruisce un catalogo di **68 sole checkbox**. La sessione e la nuova globale partono regolarmente. La previsione di fallimento prima della sessione, contenuta nei materiali preregistrati, è quindi smentita dalla prova reale.

Non ho riscritto il riferimento originario: [addendum](cesano/ADDENDUM-PREFLIGHT.json), catalogo runtime e input effettivo documentano la differenza. L'osservazione del catalogo è avvenuta mentre la globale era pendente; il file di addendum è stato scritto dopo la risposta e lo dichiara. Non è un nuovo GOLD adattato all'output.

Nome, luogo/data di nascita e denominazione della società costituiscono quattro occorrenze SOURCE certe leggibili nel FORM, ma **non hanno ID di destinazione testuale nel catalogo reale**. Le SOURCE sono comunque tutte inviate al modello. Non classifico questi quattro vuoti come omissioni LLM: la pipeline non espone destinazioni compatibili con quei valori. Nessun tentativo di sostituire i controlli con underscore o di modificare il Word.

La globale restituisce zero fatti e zero assegnazioni. Costruisce il gruppo societario `cg_forma`, validato come `GROUNDED_GROUP`, ma con `selection=unknown`, `min_selected=0`. Per `p19.cb0` propone un chiarimento locale; il backend lo respinge: **“Domanda ammessa soltanto su un campo testuale non firma”**. Inoltre la selezione delle domande di gruppo esclude i gruppi con cardinalità UNKNOWN. Il risultato è zero domande, nessuna ricevuta della scelta già espressa nel testo iniziale e nessuna spunta della società di ingegneria.

Le preferenze per categorie non sono scelte nello scenario e restano giustamente vuote. La chat offre esplicitamente una copia senza valori: l'utente sintetico la richiede e il normale export la produce, con banner bozza. Si conserva come esito fallito della compilazione, non come bozza utile o eccezione cancellata dal campione.

## 5. Dialogo e sicurezza

CRAA e Bella presentano una sola domanda distinta di applicabilità, ripetuta dopo la prima risposta. Il router propone `CONDITION_TRUE` e la verifica di pertinenza la sostiene, ma il controllo deterministico riconosce “ o ” nella negazione **“senza raggruppamenti o consorzi”** come alternativa incerta. Il secondo messaggio chiarisce la stessa decisione senza quella costruzione e viene accettato. Due turni USER, nessuna nuova scelta o proprietà personale inventata.

Nessuno dei tre percorsi ottiene un chiarimento valido sul firmatario. CRAA ne perde uno per lunghezza, Bella non lo propone, Cesano non ha destinazioni testuali supportate. Non vengono chieste molte decisioni procedurali ancora necessarie; poche domande non indicano completezza. In nessuna prova sono comparsi hold fattuali del narratore: questi campioni non misurano la capacità di conservare hold legittimi in casi negativi.

I valori finali non sono promossi artificialmente da UNKNOWN; nessun controllo fattuale, ruolo, soggetto, citazione o writer è stato cambiato. I rami senza prove/decisioni restano aperti. Le nuove prove **non annullano** la scrittura indebita PEC del precedente benchmark storico, che rimane conservato e irrisolto.

## 6. Risorse ed errori

| Misura | CRAA | Bella | Cesano |
|---|---:|---:|---:|
| Chiamate totali / globali | 9 / 1 | 9 / 1 | 4 / 1 |
| Token input totali | 76.227 | 74.716 | 54.183 |
| Token output totali, incluso reasoning | 24.775 | 24.197 | 16.986 |
| Token totali | **101.002** | **98.913** | **71.169** |
| Input / output sola globale | 37.702 / 24.080 | 37.457 / 23.510 | 38.201 / 16.743 |
| Reasoning globale | 20.681 | 18.309 | 11.604 |
| Secondi provider sola globale | 100,64 | 99,36 | 66,01 |
| Secondi provider sommati, intero percorso | 111,51 | 109,79 | 70,27 |
| Costo stimato intero percorso, USD | 0,022272 | 0,021661 | 0,016136 |
| Errori HTTP provider / retry di qualità | 0 / 0 | 0 / 0 | 0 / 0 |

Totale: **22 chiamate reali, 271.084 token, 291,57 s provider sommati, circa 0,060070 USD stimati**. Tre globali, dieci router, quattro guard e cinque sintesi. HTTP 200 e finish reason `stop` in tutte le chiamate. Nessuna globale congelata, output corretto a mano o ripetizione per ottenere più scritture.

Costo stimato con input cached/non cached e completion effettivi, dal [tariffario ufficiale DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/) acquisito nello stesso giorno e conservato: fascia non di punta, USD/milione 0,003 cache hit, 0,15 cache miss, 0,60 output. Il reasoning è già incluso nei completion token; non è una fattura. Discovery web, operatore e rendering non sono compresi nei secondi HTTP. Non è un confronto di latenza con i bandi precedenti, che hanno strutture e percorsi diversi.

Le acquisizioni browser finalizzate registrano dieci GET abortite per mount/reload ciascuna, nessun altro errore browser acquisito. Trace/video/DOM/rete/download completi per tutti e tre. Errori negli script di preparazione/lettura sono conservati come incidenti del banco di prova; non hanno modificato il codice applicativo o comportato nuove generazioni.

## 7. Verifica DOCX/PDF, conservazione e conclusione

ZIP/CRC e XML validi; report e valori fisici corrispondenti; paragrafi, prestampato, tabelle/fusioni e controlli preservati, salvo il banner bozza previsto. Download UI identici agli export salvati. Nessuna nuova selezione/deselezione fra le **18 + 68 checkbox native**, né cambi di glifi checkbox CRAA. Nessuna firma aggiunta.

Conversioni PDF nuove: **7/4/3 pagine**. Bounding box controllati su tutte le 14 pagine, nessuna parola fuori pagina; questo controllo **non rileva da solo** testo che il renderer non disegna. Ispezionate visivamente CRAA 1/4/7, Bella 1/4, Cesano 1/3. Rilevati e documentati i due dati CRAA invisibili. Gli altri testi scritti sono leggibili; restano giunzioni etichetta-valore e spaziature ampie. Firma e chiusura documento presenti; Cesano mantiene campi testuali vuoti. Nessuna verifica su Microsoft Word desktop. Warning locale LibreOffice sul registro linguistico conservato, conversioni riuscite e DOCX immutati.

Replay offline con rete vietata, senza DB/chiavi/provider: ricostruisce audit finali e i tre DOCX **identici byte per byte**, compresa la copia Cesano e il difetto di visibilità CRAA. Non confondere riproducibilità con correttezza o fruibilità.

| DOCX | SHA-256 |
|---|---|
| CRAA | `006f576fc9f3c0e1534a1253f008e8a1d0022ed1e6f8fe80f74e60a8b2d30159` |
| Bella | `781f7db27db8d3fda3c04f4da056552213659811347eb9788a0867d899183b14` |
| Cesano | `409170f436884a9cf5a7c5a4631a2c9505321b4142b61b56fa637c4c11b10a34` |

Verificati invariati: **318 file app/test/frontend/fixture, 41 input preregistrati, 422 artefatti precedenti, 29 sessioni originali e 285 file storage**. Anche le sessioni originali copiate nel runtime sono intatte; tre sole sessioni nuove, schema DB invariato. Servizi isolati arrestati. Nessuna suite software completa rieseguita: qui si riportano nuove prove reali e verifiche offline degli artefatti, senza riattribuire test storici.

**Indicazione per il prossimo intervento, non implementata:** le evidenze ora giustificano verifiche mirate su campi legacy e celle realmente utilizzabili, conservazione dei chiarimenti entro il contratto e collegamento della scelta del firmatario. Bella/Cesano mostrano inoltre due cause diverse di mancata selezione delle checkbox. La lunghezza del JSON resta una variabile da sperimentare, ma non spiega questi fallimenti dimostrati; non avvierei un'altra compattazione prima di affrontarli separatamente.

I tre casi entrano nel corpus di regressione solo se usati per lo sviluppo successivo. Un futuro test finale richiederà documenti ancora non impiegati per decidere correzioni. Risultati e fallimenti sono consegnati; baseline non adottata e nessuna correzione avviata durante o dopo le prove.

## 8. Artefatti

Ogni cartella contiene originale, scenario/riferimento preregistrati, DOCX/PDF esportati, report ordinario, dialogo, stato finale, richieste/risposte globali, prompt, audit iniziale/finale, metriche di ogni chiamata, valutazione per candidato, omissioni e diagnosi specifiche. Cesano aggiunge catalogo runtime e addendum che conservano il limite del preflight originario.

I grezzi sono in `backend/data/compilation-audit/casuali-v12-20261019-01/`. Il backup in questa directory conserva anche acquisizioni web, selezione, richieste/risposte di tutte le chiamate, transizioni, browser e codice congelato, senza database privato o credenziali. [Indice](README.md), [confronto](CONFRONTO.json), [controlli](CONTROLLI-FINALI.json), [backup](BACKUP.json).
