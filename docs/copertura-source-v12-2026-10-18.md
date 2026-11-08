# Copertura SOURCE V12: confronto effettivo 42 → 52

18 ottobre 2026. Intervento sui 18 campi ancora vuoti della V12, senza ripetere
le correzioni delle revisioni, delle citazioni tabellari, dei falsi conflitti o
delle cinque decisioni USER. Nessuna nuova chiamata DeepSeek o altro provider.

**Il nuovo DOCX contiene 52 scritture: dieci recuperate dalle SOURCE, tutti i
42 valori precedenti conservati.** Nessuna nuova scrittura indebita osservata.
Restano vuoti gli otto campi del direttore tecnico: ora tutti grounded, ma ancora
condizionati da UNKNOWN e dal rinvio USER registrato. Zero nuove spunte.

[Word parziale](../nuovi%20dati/domanda-iscrizione.V12-SOURCE-52-20261018.docx),
[PDF](../nuovi%20dati/domanda-iscrizione.V12-SOURCE-52-20261018.pdf),
[report di export](../nuovi%20dati/domanda-iscrizione.V12-SOURCE-52-20261018.report.json),
[misure](benchmarks/2026-10-18-v12-source-coverage.json),
[18 tracciati](benchmarks/2026-10-18-v12-source-coverage-trace.json),
[controlli](benchmarks/2026-10-18-v12-source-coverage-checks.json).

## Risultato nel documento

| Misura | V12 precedente | Nuovo replay |
|---|---:|---:|
| Assegnazioni del modello | 60 | 60, risposta originale invariata |
| Proposte SOURCE grounded effettive | 46 | 60 |
| Proposte revisionate nel replay | 46 | 60 |
| Grounded ancora UNKNOWN | 4 | 8 |
| Proposte SOURCE applicabili | 42 | 52 |
| SOURCE fisicamente scritte | 41 | 51 |
| Valori USER scritti | 1 | 1 |
| Scritture totali | 42 | 52 |
| Precedenti valori persi o cambiati | — | 0 |
| Campi SOURCE attesi ancora vuoti | 18 | 8 |
| Campi dei soci nel DOCX | 24 | 24 |
| Spunte nuove | 0 | 0 |
| Pagine nel medesimo LibreOffice | 9 | 9 |

Una destinazione dei soci rimane compilata con la precedente ricevuta USER
«Ingegnere»: non ne è stata riscritta retroattivamente la provenienza.
L'aumento da quattro a otto UNKNOWN riguarda quattro valori prima respinti;
non significa che siano state perse scritture precedenti.

## Presenza nelle fonti e nell'input

**Tutti i 18 dati erano nelle SOURCE, erano nell'input LLM e sono stati proposti
dal modello. Zero omissioni fra questi 18.** I relativi fatti superavano già il
grounding letterale: fallivano destinazione/binding o applicabilità.

Il corpus corrente è stato riletto dal database live in sola lettura e confrontato
con ogni chiave/contenuto dell'input salvato: le 56 SOURCE coincidono. Non è stato
aggiunto alcun dato alla KB e non è servita una reindicizzazione.
I chunk indicati sotto si riferiscono a quell'input, con provenienza Company KB.

| Campo | Valore proposto | SOURCE / input / proposto | Citazione originale | Blocco precedente | UNKNOWN effettivo | Esito |
|---|---|---|---|---|---|---|
| `p12.s0` nome firmatario | Leonardo Montemurro | sì / sì / sì | `-53`, titolo anagrafica | binding FORM rifiutato; riuso non attivo | nessuno | scritto da SOURCE |
| `p12.s1` comune nascita | Lecce | sì / sì / sì | `-53`, luogo nascita | stesso binding | nessuno | scritto da SOURCE |
| `p12.s2` provincia nascita | LE | sì / sì / sì | `-53`, luogo nascita | stesso binding | nessuno | scritto da SOURCE |
| `p12.s3` data nascita | 14 novembre 1982 | sì / sì / sì | `-54`, data nascita | stesso binding | nessuno | scritto da SOURCE |
| `p13.s0` comune residenza | Bari | sì / sì / sì | `-54`, comune residenza | stesso binding | nessuno | scritto da SOURCE |
| `p13.s1` provincia residenza | BA | sì / sì / sì | `-54`, comune residenza | stesso binding | nessuno | scritto da SOURCE |
| `p13.s2` residenza | Via Amedeo 24 | sì / sì / sì | `-54`, indirizzo personale | stesso binding | nessuno | scritto «Amedeo 24» dopo «via» prestampato |
| `p13.s3` CF personale | MNTLRD82S14E506X | sì / sì / sì | `-54`, CF personale | stesso binding | nessuno | scritto da SOURCE |
| `p14.s0` carica | amministratore unico e rappresentante legale | sì / sì / sì | `-53`, carica dal 2 ottobre 2026 | stesso binding | nessuno | scritto da SOURCE |
| `p15.s0` Comune sede | Bari | sì / sì / sì | `-52`, sede legale — comune | FORM con solo marker | nessuno | scritto da SOURCE |
| `p51.s0` nome direttore | Elisa Romano | sì / sì / sì | `-55`, ruolo tecnico nominativo | già grounded | `c_dt`, rinviata | ancora vuoto |
| `p52.s0` qualifica direttore | ingegnere | sì / sì / sì | `-55`, medesimo record | già grounded dopo correzione tipografica | `c_dt`, rinviata | ancora vuoto |
| `p52.s1` CF direttore | RMNLSI85C47A662Y | sì / sì / sì | `-54`, riga personale dei soci | FORM cita «iscritto» nel paragrafo sbagliato | `c_dt`, rinviata | recuperato grounding, non scritto |
| `p53.s0` Ordine | Ordine degli Ingegneri di Bari | sì / sì / sì | `-55`, record del direttore | già grounded | `c_dt`, rinviata | ancora vuoto |
| `p53.s1` sezione | A | sì / sì / sì | `-55`, record del direttore | già grounded | `c_dt`, rinviata | ancora vuoto |
| `p53.s2` provincia albo | Bari (BA) | sì / sì / sì | `-54`, riga dei soci | proprietà `provincia_albo` non riconosciuta dal collegamento | `c_dt`, rinviata | recuperato grounding, non scritto |
| `p53.s3` iscrizione dal | 18/05/2015 | sì / sì / sì | `-54`, riga dei soci | proprietà `data_iscrizione_albo` fuori dall'elenco supportato | `c_dt`, rinviata | recuperato grounding, non scritto |
| `p53.s4` numero albo | 8421 | sì / sì / sì | `-54`, riga dei soci | proprietà `numero_iscrizione_albo` fuori dall'elenco supportato | `c_dt`, rinviata | recuperato grounding, non scritto |

La colonna UNKNOWN considera anche i legami strutturali e le ricevute USER,
non soltanto lo stato del campo respinto. Tutti gli otto dati del direttore
dipendono anche da `c_societa`, confermata dall'utente; resta irrisolta `c_dt`.

## Firmatario: cause e correzione

Il binding `b_leonardo` del modello cita «in qualità di» in `paragraph:14`, dove
quell'estratto non esiste: il testo è nel paragrafo precedente. Errore preciso:
«Estratto non presente nel FORM», poi «Binding di ruolo rifiutato» sui nove campi.
Inoltre il FORM chiede la carica del sottoscritto, non prescrive letteralmente
«amministratore unico e rappresentante legale». Quel binding non viene promosso
a valido spostando soltanto una citazione.

Il riuso SOURCE preesistente aveva due ulteriori barriere:

1. Si attivava soltanto con un VALUE sul campo nominativo. La scelta era invece
   già registrata nella risposta positiva a `c_societa`:
   «per questa pratica il firmatario scelto è Leonardo Montemurro».
2. Rifiutava ogni destinazione con una proposta MODEL presente, anche se respinta.

Ora una **clausola nominativa esplicita in una ricevuta USER accettata** può
attivare il riuso. Non vengono interpretati come decisioni il testo libero
d'avvio, un ruolo aziendale o una citazione narrativa. La ricevuta originale
rimane CONDITION_TRUE, senza fabbricare un VALUE o nuove decisioni USER.

Il profilo SOURCE completo in `-54` documenta nome, cognome e CF e fornisce le
generalità. Identità, conflitti e omonimie vengono controllati prima del riuso.
La carica proviene dall'asserzione nominativa `-53`, nello stesso documento
aziendale con operatore identificato: non dalla scelta USER. Non vengono
dedotti procure, poteri speciali o una designazione professionale.

Una proposta respinta può essere sostituita da una proposta backend indipendente
solo se il suo fatto SOURCE è grounded, riguarda la stessa persona e concorda
con il valore documentato. Restano protetti alternative esplicite, conflitti,
fatti respinti, valori USER e proposte già grounded. L'unica componente di
indirizzo rimossa è «Via», già prestampata dal FORM, con il criterio deterministico
preesistente: nessuna estrazione arbitraria di città o trasformazione di strade.

Il vecchio binding resta rifiutato e diagnosticabile. Il nuovo percorso conserva
le prove dell'identità, del valore, dell'operatore e della scelta. I valori sono
ancora proposte da revisionare, non RESOLVED. La sostituzione di una proposta
già contabilizzata non diminuisce falsamente `unassigned_count`.

## Prove FORM ricostruite e proprietà professionali

Il controllo originale del marker rimane intatto. Solo V12 può derivare una
nuova prova effettiva, conservando citazione/errore originali nell'audit:

- Per il CF, il prefisso reale «C.F.» e il marker dello stesso campo bastano;
  «iscritto» aggiunto erroneamente dal modello non viene trattato come testo FORM.
  Prefissi inventati, altri paragrafi/marker e citazioni SOURCE invalide restano
  respinti. Non si cambia la destinazione per adattarla al valore.
- Per il Comune, «con sede in» conclude il paragrafo dell'operatore e il campo
  successivo è seguito dalla provincia fra parentesi. Le due prove sono tenute
  separate, con il riferimento al campo dell'operatore già verificato. Stessa
  azienda, adiacenza fisica e assenza di barriere sono obbligatorie. Il controllo
  finale sull'operatore avviene dopo tutti i binding, senza dipendere dall'ordine
  del catalogo. Un indirizzo completo nel Comune viene respinto, non abbreviato.

Per i tre attributi dell'albo sono riconosciuti tre identificatori deterministici:
`provincia_albo` → `provincia`, `data_iscrizione_albo` → `iscrizione_dal`,
`numero_iscrizione_albo` → `numero_iscrizione`. Il trasferimento resta limitato
a proprietà della **stessa iscrizione professionale**, dimostrata da nome completo,
Ordine e numero coincidenti, con controllo di CF/conflitti nelle altre fonti.

Il record del direttore in `-45` documenta Ordine e numero 8421; la riga `-54`
documenta la stessa iscrizione e gli attributi. Titolo, intestazioni, riga,
record del ruolo e citazioni originali sono conservati. Nessun collegamento
basato sulla sola somiglianza del nome; nessun trasferimento di qualifiche,
ruoli o poteri. I controlli tabellari e di identità già corretti restano in uso.

## Perché il direttore rimane vuoto

La condizione FORM è in `paragraph:50`: Responsabile della Progettazione per
le società di professionisti oppure Direttore Tecnico per le società di ingegneria.
Il modello usa una condizione semantica con un fatto di natura societaria e uno
professionale. Il verificatore restituisce UNKNOWN e segnala «Condizione e fatti
su dimensioni differenti» nel supporto SOURCE della condizione.

Il record nominativo del direttore è documentato; non equivale però a una
valutazione automatica della condizione composta. La ricevuta già registrata è
SKIP: «non fornisco una conferma aggiuntiva sul ruolo del direttore tecnico».
È conservata, senza trasformarla in TRUE, FALSE o nuova attestazione.

Pertanto tutti gli otto valori sono ora proposte grounded ma **non applicabili
all'export corrente**. Il loro mancato inserimento non indica più prove personali
respinte o dati assenti dalla KB. La valutazione della condizione e del rinvio
resta separata dal recupero dei fatti; non è stata modificata in questo intervento.

## Checkbox societaria: corrispondenza trovata, gruppo ancora assente

La decisione su `c_societa` è positiva e pertinente. La citazione coincide
letteralmente con il paragrafo della checkbox nativa `p39.cb0`, inclusa nel suo
scope. **La corrispondenza della singola casella è dimostrata.** Non manca una
nuova risposta dell'utente sulla partecipazione.

Nell'output reale `choice_groups={}` e nessuna assegnazione riguarda quella
checkbox. L'adapter registra l'applicabilità e abilita i testi dipendenti, ma non
costruisce automaticamente un gruppo di scelte né una ricevuta `choice`.
L'export richiede proprio un gruppo validato e una selezione verificabile.

La sezione «IN QUALITÀ DI» contiene sette controlli, separati da blocchi di dati.
Le controprove offline, mai usate nell'export, mostrano:

- Il gruppo completo dichiarato `single` è respinto: «Gruppo esclusivo incompleto
  rispetto alla lista fisica Word». La chiusura locale attuale non ricostruisce
  la lista con questi blocchi intermedi.
- Dichiararlo `multiple` supera i controlli strutturali, ma il FORM non esplicita
  quella cardinalità: il superamento dello schema non dimostra la semantica.
- `unknown` può descrivere il gruppo, ma non autorizza la scrittura.

Non è stato scelto `multiple` per aggirare il rifiuto del gruppo esclusivo, né
isolata una casella per simulare una lista completa. Nessuna spunta o
deselezione. Natura giuridica SOURCE, partecipazione USER e poteri del firmatario
rimangono distinti. Il limite residuo è la rappresentazione/validazione del
gruppo, non la disponibilità dei dati societari.

## GOLD, errori e impaginazione

I dieci nuovi valori sono supportati dalle SOURCE. Il confronto con lo scorer
congelato restituisce **51 scritture conformi su 52**. L'unica differenza è
`p14.s0`: il GOLD attende «rappresentante legale», la SOURCE e il DOCX riportano
«amministratore unico e rappresentante legale». È un titolo più esteso attestato,
non un potere inventato. La differenza resta registrata; il GOLD non è cambiato.

Il confronto XML verifica tutte le posizioni e i 42 valori precedenti, i vuoti
restanti e il report. CRC/parti XML validi; cambia solo `word/document.xml`.
Quattro tabelle e tredici controlli nativi intatti, nessuna spunta. Tutti i 24
campi dei soci conservati. Gli otto vuoti SOURCE rimasti sono soltanto quelli
del direttore elencati sopra.

Entrambi i documenti sono stati renderizzati con lo stesso LibreOffice locale:
nove pagine. Ispezionate le pagine 1, 3 e 9 prima/dopo: generalità e Comune
leggibili, nessuna sovrapposizione osservata; soci intatti; firma e linea nella
pagina finale con il resto del testo. I raster delle pagine 3 e 9 sono identici.
Le giunzioni fra prestampato e valori e gli spazi di giustificazione preesistenti
rimangono: il writer non è cambiato. È un controllo LibreOffice mirato, non una
certificazione della paginazione Microsoft Word. Avviso liblangtag in entrambi
i render conservato nei log; conversioni riuscite.

Le cinque decisioni USER sono identiche, anche nelle chiavi/destinazioni:
preferenze, attestazioni, esecutori, integrazione, luogo/data. Le relative celle
e dichiarazioni rimangono vuote; firma protetta. Nessuna risposta del copione
è stata somministrata in assenza di una domanda/decisione reale.

## Test, replay e conservazione

43 nuovi casi generici, positivi e negativi. **304 test mirati passati in 32,57s;
suite completa finale 2567 passati in 185,17s; Ruff passato.** Sono coperti
omonimie, persone/aziende diverse, conflitti, scelta non registrata o incerta,
rinvio successivo, proposte concorrenti, SOURCE/FORM inventati, marker errati,
barriere fisiche, indirizzo completo, iscrizione diversa e attributi non provati.

Red iniziale: 7 fail/31 pass. Durante il lavoro sono stati riprodotti e corretti
anche un indirizzo completo accettato dal nuovo recupero, l'ordine del catalogo
che poteva lasciare valido un Comune con operatore successivamente respinto e
un `form_evidence=null` del vecchio binding conservato che interrompeva la sintesi.
Un caso di test iniziale mancava del discriminatore della proposta: corretto
senza rilassare il contratto. Fallimenti, suite intermedie e primo replay interrotto
restano tutti negli artefatti; nessuna prova fallita è stata scartata.

Replay con socket/HTTP vietati e DB/storage copiati. Baseline riprodotta con le
preimmagini dei moduli solo nel processo: 42 scritture e stesso hash V12. Poi
stessa risposta MODEL, stesse SOURCE e ricevute USER: 52 scritture. Persistenza,
grounding e writer reali; solo il trasporto del narratore è simulato, con revisione
delle 14 nuove proposte. Non è una nuova valutazione autonoma della qualità LLM
o una nuova prova UI. Verifica manuale dei valori e confronto GOLD separati.

`verify_bundle.py` ricostruisce audit e DOCX senza database privati o chiavi e
ottiene lo stesso hash finale. Il render del replay finale viene riusato soltanto
dopo confronto binario positivo con il documento già renderizzato.

```text
FORM B0  25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c
V12 42   4a29f7d306a6664b88208f8ba88bff5738123310a84853ff4e770f69dae126c8
Nuovo 52 58f1179d4cff7c6c1de4f2e886c524906c1be618e1025a67d97288f7c7323f2b
```

Raw: `backend/data/compilation-audit/v12-source-coverage-20261018-01/`.
Risultati definitivi in `baseline/` e `corrected-final/`; tentativi precedenti
separati. [Backup](benchmarks/2026-10-18-v12-source-coverage-audit.tar.gz),
[checksum](benchmarks/2026-10-18-v12-source-coverage-audit.tar.gz.sha256),
[descrittore](benchmarks/2026-10-18-v12-source-coverage-archive.json).
DB e chiavi privati esclusi; input/output, prove, codice, stati, test e render inclusi.

Zero nuove chiamate/token/costi provider, nessuna misura di accelerazione.
FORM B0, modello, thinking, prompt/schema globali, API/database, retrieval e writer
invariati. Nessuna migrazione o modifica delle sessioni originali; i nuovi percorsi
si attivano sulla rivalidazione e sulle ricevute pertinenti, senza upgrade impliciti
dell'archivio. Le vecchie sessioni devono essere rivalutate prima di riusarne le
revisioni sui campi cambiati. Nessun framework, hardcoding applicativo, refactor
generale, commit/push o riavvio di E1. Arresto dopo il rapporto e il nuovo DOCX.
