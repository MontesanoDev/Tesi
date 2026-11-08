# E1 compact-index-v2 — 17 ottobre 2026

**Serie conclusa: input ridotto, affidabilità non migliorata.** Tre analisi reali,
un rifiuto del contratto, un troncamento e una risposta accettata. Un solo Word,
con 21 valori conformi sui 60 documentati dalle fonti. La variante rimane nel
banco di prova; nessuna adozione nella chat. L'utente ha autorizzato questa seconda
variante dopo [compact-v1](esperimento-e1-form-compatto-2026-10-16.md).
[B0](baseline-minervino-b0-2026-10-16.md) rimane il riferimento recuperabile.

[Misure complete](benchmarks/2026-10-17-e1-index.json),
[bundle delle acquisizioni](benchmarks/2026-10-17-e1-index-audit.tar.gz),
[checksum](benchmarks/2026-10-17-e1-index-audit.tar.gz.sha256),
[manifest dell'archivio](benchmarks/2026-10-17-e1-index-archive.json),
[verifiche finali](benchmarks/2026-10-17-e1-index-checks.json).
Raw permanenti: `backend/data/compilation-audit/e1-index-20261017-01/`.

## Ipotesi, trattamento e controlli fissati prima dei risultati

L'ipotesi era che un indice diretto delle destinazioni aiutasse il modello rispetto
al raggruppamento per contesti v1. Non era stato promesso un miglioramento.

Nuova vista `compact-index-v2` selezionabile soltanto nel runner. `form.candidates`
conserva un record per ID con `type` e `context_id` espliciti, proprietà individuali
e override. `form.contexts` contiene le relazioni condivise: sezioni, ancore e
continuazione. Eredità di contesto più override riproduce le stesse proprietà
logiche del catalogo canonico. Testi, griglia delle tabelle, marker e parti in sola
lettura restano identici in `form.blocks` e `read_only_parts`.

Coordinate, range e copie before/after restano nel backend come in v1. Il
serializzatore usa il raggruppamento deterministico v1 per condividere le
proprietà; la verifica v2 confronta direttamente ciascun ID col catalogo canonico.
Respinge contesti/ID mancanti o estranei, proprietà tecniche/sconosciute, override
che alterano ruolo/ancore/tipo/protezione e riferimenti non risolvibili.

Le istruzioni di lettura sono adattate al formato, inclusa l'identificazione
inline attraverso i marker quando range non è serializzato. Il trattamento
è **formato più istruzioni corrispondenti**: non si può attribuire un effetto
alla sola presenza dell'indice o alla sola lunghezza. Nessuna indicazione
semantica aggiunta dal gold, nessun suggerimento mirato alle sezioni prima omesse.

Stessi modulo completo, fonti/chunk, dati USER, schema della risposta, validatori,
writer, modello/thinking e budget B0/v1. Il guard impone uguaglianza esatta del
canonico B0 prima di ogni chiamata. Nessuna migrazione, integrazione nella chat
o rimozione di compact-v1. Verificata offline la riproduzione esatta di input e
istruzioni v1 conservati: i confronti precedenti rimangono recuperabili.

Tre analisi DeepSeek flash/thinking sequenziali, timeout 300 s, limite output
49.152 token, zero retry e nessuno scarto. Solo le risposte realmente accettate
proseguono nei servizi isolati, con copione e scorer B0 invariati. Gold escluso
dall'input. Protocollo e hash del codice congelati prima della prima chiamata.
La risposta viene riusata solo dopo uguaglianza del canonico, della proiezione
e dell'audit rivalidato; non viene effettuata una seconda analisi favorevole.

Serie storiche B0/v1 eseguite il giorno precedente: modello nominale uguale,
backend provider non fissato, cache e carico non controllati. Tre campioni non
dimostrano significatività, equivalenza o non inferiorità. Nessuna fattura acquisita.

## Preflight e verifiche software

| Caratteri JSON | B0 | compact-v1 | compact-index-v2 |
|---|---:|---:|---:|
| FORM | 126.928 | 81.209 | 88.522 |
| Messaggi completi | 264.951 | 220.519 | 227.803 |

FORM v2 ridotto del 30,26% rispetto a B0, mantenendo indice diretto e tipi
espliciti; messaggi ridotti del 14,02%. 267 destinazioni e 142 contesti.
Adattamento del system prompt: +1.258 caratteri. Fonti, schema, reading plan,
dati USER e parametri provider identici. Le dimensioni offline sono distinte
dai token effettivamente misurati sotto.

**137 test mirati passati in 7,61 s; 2.279 backend passati in 170,27 s; Ruff
completo passato.** Test su formati precedenti, controlli negativi per
indice/contesti, tipi espliciti, override, protezione firma, ID estranei,
metadata sconosciuti/tecnici e testo/marker alterati; originali Minervino,
Labirinto e Catanzaro, controlli nativi, unioni, annidamento e header. Runner
con provider simulato, prepare-only e guard del riferimento per entrambe le
viste. Questi test verificano il software, non la qualità LLM.

Iniziale errore Ruff E501 su una riga del runner, corretto prima del congelamento;
log conservato. Nessun fallimento pytest in questa serie e nessuna modifica al
codice congelato durante le tre prove. Frontend non modificato, suite non ripetute.

## Tre analisi reali, inclusi i fallimenti

| Run | Esito effettivo | Input | Output, reasoning incluso | Di cui reasoning | Secondi AI | Word |
|---|---|---:|---:|---:|---:|---|
| 01 | Rifiuto del contratto JSON | 65.770 | 39.871 | 32.272 | 173,44 | Nessuno |
| 02 | Troncamento al limite output | 65.770 | 49.152 | 44.316 | 214,62 | Nessuno |
| 03 | Proposta accettata, export parziale | 65.770 | 36.508 | 29.806 | 159,94 | 21/60 conformi |

Run 01: HTTP 200 e JSON completo, ma due proprietà root non ammesse,
`proposal_stage` e `project_id`, causano `ValidationError` di
`CoverageAwareProposal`. Nessun audit accettato, sessione o Word. Lo scorer
invariato può confrontare il JSON grezzo: 27 proposte, 25 valori conformi.
Indirizzo completo in p15.s0 e p41.s1 dove il gold prevede il comune Bari:
fatto documentato ma granularità errata per la destinazione. Questi 25 confronti
non sono un risultato accettato dal sistema. Nessuna rimozione delle chiavi extra.

Run 02: HTTP 200 con `finish_reason=length`, al limite fisso di 49.152 token.
44.316 sono reasoning. Il contenuto visibile è JSON incompleto: stringa non
terminata, controllo JSON offline fallito. Acquisiti HTTP, usage e contenuto
tronco, senza ricostruirlo o produrre una `response.txt` fittizia. Nessun audit,
sessione, Word o punteggio per campo. Il fallimento non è sostituito da un retry.

Run 03: 23 proposte conformi al gold, 21 conservate come ipotesi grounded.
Due rifiuti FORM per p15.s0 e p15.s1: il solo marker non documenta sufficientemente
la richiesta secondo il validatore invariato. Conteggio destinazioni dell'audit:
265 `REVIEW_REQUIRED`, due `REJECTED`, nessun `RESOLVED`. Non sono 265 campi
compilati. Nessun gruppo di scelta o proposta booleana.

| Gruppo SOURCE, run 03 | Target | Proposte grezze conformi | Grounded conformi |
|---|---:|---:|---:|
| Firmatario e anagrafica iniziale | 19 | 10 | 8 |
| Società | 9 | 9 | 9 |
| Soci, occorrenze ripetute | 24 | 0 | 0 |
| Direttore tecnico | 8 | 4 | 4 |
| Totale | 60 | 23 | 21 |

Riletti i 21 valori con citazioni SOURCE e soggetti: dati aziendali attribuiti a
Mapi, dati del direttore a Elisa Romano, p41.s1 correttamente Bari. Controllo sullo
scenario sintetico, non validazione professionale, giuridica o degli identificativi.

## Confronto con B0 e prima variante

I numeri per run sono nell'ordine delle acquisizioni, non coppie di campioni
statisticamente appaiati. N/D significa risultato non disponibile per fallimento,
non uno zero imputato né un campione escluso.

| Misura | B0 completo | compact-v1 | compact-index-v2 |
|---|---|---|---|
| Input token per analisi | 75.864 | 63.661 | 65.770 |
| Riduzione input rispetto a B0 | riferimento | 16,09% | 13,31% |
| Analisi accettate / tentate | 3/3 | 3/3 | 1/3 |
| Grounded conformi, per run | 21 / 17 / 21 | 13 / 19 / 21 | N/D / N/D / 21 |
| Word conformi su 60, per run | 23 / 17 / 22 | 14 / 11 / 23 | N/D / N/D / 21 |
| Word prodotti / tentativi | 3/3 | 3/3 | 1/3 |
| Output medio per analisi, inclusi fallimenti | 40.074 | 34.569 | 41.843,67 |
| Totale token medio per analisi, inclusi fallimenti | 115.938 | 98.230 | 107.613,67 |
| Tempo medio analisi, secondi, inclusi fallimenti | 170,14 | 139,84 | 182,67 |

Rispetto a B0, v2 riduce input del 13,31% e token totali medi di analisi del
7,18%, ma l'output medio aumenta del 4,42%. Il tempo medio aumenta di circa
7,36%. Nessun miglioramento di latenza dimostrato. Prima analisi v2 con 6.400
cache hit/59.370 miss; successive 65.536/234. B0 era tutto caldo. Cache, carico,
giorno e variabilità dell'output impediscono un'attribuzione causale della durata
alla sola rappresentazione. Token totali non equivalgono al costo monetario.

Il singolo successo v2 non consente una media di qualità confrontabile coi tre
Word B0/v1. I due errori restano nel denominatore dell'affidabilità e del consumo.
Il CSV `comparison.csv` nei raw/bundle conserva i nove run storici con N/A dove
manca un esito, senza completarlo artificialmente.

## Continuazione, domande ed export

Solo run 03 proseguito: routing e narratore reali nei servizi isolati, senza
browser, endpoint HTTP, ingestion o tempo umano misurati. Sei chiamate oltre
all'analisi. Prima vengono chieste solo due condizioni di partecipazione già
espresse nella richiesta iniziale: società di ingegneria e operatore Mapi.
Risposta limitata alla ripetizione T0 ammessa da B0/v1, con Leonardo Montemurro
come firmatario; non è una riconferma aggiunta di fatti SOURCE.

L'analisi conserva `user_values=[]` come B0: le decisioni iniziali presenti nella
richiesta della chat non diventano automaticamente input dell'analisi. Nessun
intervento per sistemare questo collegamento durante E1. I campi del firmatario
non sono stati chiesti esplicitamente e la ripetizione T0 non li ha compilati.

Dopo la sola risposta sulle condizioni, il motore offre l'export parziale.
Nessuno dei quattro temi del copione — preferenze, designazioni, attestazioni,
luogo/data — è stato chiesto. Nessun tema inviato proattivamente dall'operatore.
Export esplicito con testo congelato; sessione `GENERATED`,
`ready_for_submission=false`. Nessuna promozione automatica a `RESOLVED`.

| Categoria nel Word 03 | Conformi / target |
|---|---:|
| Testi da SOURCE | 21/60, tutti effettivamente SOURCE |
| Testi da USER | 0/4 |
| Preferenze selezionate attese | 0/6 |
| Checkbox native true attese | 0/3 |
| Testi da lasciare vuoti | 123/123 |
| Preferenze non selezionate | 61/61 |
| Checkbox native false | 10/10 |

Nove chiamate provider totali e 353.942 token: tre analisi, sei operazioni di
dialogo. Il minor totale di chiamate rispetto a B0/v1 deriva anche dai due
fallimenti precoci: non è un risparmio dimostrato per pratica completata.

## Controllo materiale, visivo e integrità

Tutte le 267 destinazioni confrontate con gold, report e DOCX tramite scorer B0
identico; controllo aggiuntivo di tutte le 110 celle, intestazioni comprese.
Insiemi ZIP uguali, solo `word/document.xml` modificato, altre 15 parti identiche.
Nessuna spiegazione aggiunta nelle aree compilabili. I placeholder irrisolti
restano e il writer aggiunge l'avviso di bozza previsto dal sistema esistente.

LibreOffice 26.2.6.3 produce dieci pagine. Visione campionata delle pagine 1, 3 e
10: firmatario vuoto, società compilata, soci vuoti, direttore parziale; firma e
linea insieme sulla pagina finale quasi vuota. Il problema di impaginazione
resta. Non eseguita certificazione visuale di tutte le pagine o in Microsoft Word.

[Word per revisione](<../nuovi dati/domanda-iscrizione.E1INDEX-RUN-03.docx>),
[PDF](<../nuovi dati/domanda-iscrizione.E1INDEX-RUN-03.pdf>),
[guida agli esiti](<../nuovi dati/LEGGIMI-E1INDEX-MINERVINO.md>).
Nessun Word/PDF per run 01/02. Copie del run 03 identiche agli artefatti grezzi.

Verificati 18 hash Minervino e 11 Labirinto, codice congelato e input/request
identici fra i tre run. Cinque file SOURCE live identici alla fixture. Confronto
in sola lettura delle entità preesistenti con la copia isolata, escludendo solo
le nuove entità del run 03: 49 conversazioni, 28 sessioni, 464 revisioni e 16
compilazioni uguali. Nessuna pretesa di immutabilità binaria dell'intero DB o
degli indici derivati. Nessuna modifica a fonti, fixture, gold o motore operativo.

Archivio: 250 file, 3.250.464 byte; SHA-256
`e0f586cf03775c9a699be31b7d75d704af5b61609411fbbdb13d74284dda33fc`.
Bundle con richieste/schema/prompt, output reali inclusi errori/troncamento,
usage/tempi/cache, codice, log test e confronti. Esclusi DB, file .ai-key e
credenziali; verifica in memoria delle chiavi note in chiaro e cifrate.
`backend/data/` è locale: il bundle versionabile in docs/benchmarks rende
trasportabili queste acquisizioni; nessun commit o push effettuato qui.

## Decisione e prossimo esperimento proposto

L'indice diretto è realizzato e misurato, ma non ha fornito evidenza sufficiente
per adottare la variante. Il formato originale resta operativo; compact-v1 e
compact-index-v2 restano riproducibili nel runner. E2 non avviato: manca ancora
una base compatta con qualità stabile. Non possiamo concludere che ogni layer
compatto sia inefficace né che l'indice abbia causato da solo i due fallimenti.

Prima di un'altra riduzione proporrei una prova separata sull'affidabilità del
contratto di uscita e sul budget di ragionamento: questa serie mostra due
modalità di fallimento distinte, proprietà extra e saturazione dell'output.
Tenere fissi vista e fonti, cambiare una sola variabile per serie e acquisire
sempre accettazione, copertura, risorse e Word quando possibile. Non correggere
in silenzio le risposte e non aumentare budget senza misurare il consumo.
Questa è una proposta, non una modifica già implementata o approvata.

Separatamente restano collegamento delle decisioni iniziali USER all'analisi,
binding dei dati personali, copertura dei soci e selezione delle domande.
Un JSON più piccolo da solo non risolve i limiti osservati. Nessun correttivo
aggiunto a questi percorsi nel corso dell'esperimento E1.
