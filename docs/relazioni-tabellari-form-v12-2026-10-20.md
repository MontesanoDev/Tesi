# Relazioni strutturali FORM nelle tabelle DOCX — 20 ottobre 2026

Intervento backend concluso nel perimetro delle relazioni verificabili descritte
qui. Tutte le **13 barriere FORM del riferimento Catanzaro** hanno ora un
collegamento fisico univoco. Questo non significa tredici valori autorizzati:
restano indipendenti proprietà FORM, fatto/soggetto/ruolo SOURCE e
applicabilità/autorizzazione della pratica.

**Verifica deterministica:** 3.048 test backend e Ruff PASS; 68 export storici
identici byte per byte; 213 confronti di validatori senza perdita di proposte
grounded. **Prova reale:** una nuova sessione UI Catanzaro, export/download
ordinari, 17 testi SOURCE. Sulla stessa nuova risposta e sulle stesse ricevute
USER il backend precedente scriverebbe 16 testi: l'unica aggiunta causale è
`Bari` nella cella CCIAA `t25.r2.c0`. Nessuna scrittura della sede operativa.

[Consegna, input e riproduzione](<../benchmark ufficiale/table-form-links-20261020-01/README.md>),
[esito regressione](<../benchmark ufficiale/table-form-links-20261020-01/REGRESSIONE.json>),
[esito E2E](<../benchmark ufficiale/table-form-links-20261020-01/E2E-REALE.json>).

## Baseline e riproduzione prima dell'implementazione

Letti STATUS, relazioni, diagnosi architetturale, rapporto di applicabilità,
codice, test e acquisizioni. HEAD `99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e`
non descrive da solo il software: preservato il working tree sporco, inclusa
la correzione di applicabilità già conclusa. Prima delle modifiche congelati
233 file e 6.386 hash protetti, stato logico completo del DB e storage live.
Snapshot `before/`, manifest `FROZEN.json`, grezzi e patch sotto
`backend/data/compilation-audit/table-form-links-20261020-01/`.

La riproduzione precedente ha rieseguito i due test diagnostici originali:
barriera di tutte le tredici posizioni e proposta CCIAA veritiera. Entrambi PASS
nel senso diagnostico: fatto CCIAA grounded, assegnazione rifiutata con
`Estratto FORM esterno al contesto strutturale locale`. Log
`reproduction-before.log`. Non modificati test, gold, aspettative o risultati
nello studio congelato.

Causa dimostrata in `compilation_global._form_bindings`: la prova ammessa per
una cella comprendeva i paragrafi della sua riga e tutte le intestazioni
**solo** se marcate `w:tblHeader`. Le tredici righe di destinazione contengono
solo paragrafi vuoti e non hanno intestazioni Word ripetute. Il catalogo
conservava già etichette, ID, celle e `gridSpan`; il writer raggiungeva già le
destinazioni. La perdita avveniva nel collegamento delle prove, non nel parsing
dei valori o nell'indirizzamento XML.

## Le tredici destinazioni, prima e dopo

Indici fisici a base zero, come nel catalogo: `t41.r1.c3` significa tabella 41,
riga 1, cella fisica 3; non una colonna virtuale di python-docx. `pN` abbrevia
`paragraph:N`. Tutti i paragrafi ammessi nella colonna «prima» sono vuoti.
L'esatto XPath XML, il contenuto letterale delle etichette, gli intervalli di
griglia e ogni esito storico sono in
[DIAGNOSI-13.json](<../benchmark ufficiale/table-form-links-20261020-01/DIAGNOSI-13.json>).

| Destinazione | FORM ammesso prima | Cella etichetta → paragrafo | Proprietà richiesta | Relazione verificata |
|---|---|---|---|---|
| t25.r2.c0 | p440 | t25.r1.c0 → p439 | iscrizione alla CCIAA di | riga precedente, stesso intervallo [0,5) |
| t41.r1.c0 | p655–660 | t41.r0.c0 → p650 | Nome e cognome | prima riga, stessa colonna |
| t41.r1.c1 | p655–660 | t41.r0.c1 → p651 | Data e luogo di nascita | prima riga, stessa colonna |
| t41.r1.c2 | p655–660 | t41.r0.c2 → p652 | Residenza | prima riga, stessa colonna |
| t41.r1.c3 | p655–660 | t41.r0.c3 → p653 | Codice fiscale | prima riga, stessa colonna |
| t41.r1.c4 | p655–660 | t41.r0.c4 → p654 | Poteri conferiti / qualifica | prima riga, stessa colonna |
| t43.r1.c0 | p698–703 | t43.r0.c0 → p693 | Nome e cognome | prima riga, stessa colonna |
| t43.r1.c1 | p698–703 | t43.r0.c1 → p694 | Data e luogo di nascita | prima riga, stessa colonna |
| t43.r1.c2 | p698–703 | t43.r0.c2 → p695 | Residenza | prima riga, stessa colonna |
| t43.r1.c3 | p698–703 | t43.r0.c3 → p696 | Codice fiscale | prima riga, stessa colonna |
| t43.r1.c4 | p698–703 | t43.r0.c4 → p697 | Poteri conferiti / qualifica | prima riga, stessa colonna |
| t44.r1.c0 | p717–721 | t44.r0.c0 → p713 | Nome e cognome | prima riga, stessa colonna |
| t44.r1.c3 | p717–721 | t44.r0.c3 → p716 | Codice fiscale | prima riga, stessa colonna |

Per CCIAA entrambi i `w:tc` hanno `w:gridSpan=5`: il testo è in p439 e p440
rimane la destinazione vuota originale. Non serve riconoscere la parola CCIAA
per costruire l'arco. Le altre intestazioni hanno intervalli di colonna esatti;
nessuna delle dodici associazioni usa l'intera riga d'intestazione come prova
della singola proprietà. Tra queste tredici associazioni **zero ambiguità
strutturali residue**. La validità del ruolo e del valore resta un'altra verifica.

Nel catalogo Catanzaro completo: 265 celle testuali considerate, 200 con
relazione strutturale dimostrata; 89 destinazioni prima senza prova locale
non vuota ne acquisiscono una. Questi numeri includono campi privi di SOURCE o
autorizzazione e non misurano accuratezza o compilabilità. Per esempio
`t25.r5.c0/c1` restano non dimostrate: i loro intervalli non individuano una
sola proprietà della riga precedente. Gli altri 65 casi senza arco non vengono
sbloccati per la sola appartenenza alla tabella.

## Soluzione e garanzie

`compilation_table_form.py` usa gli ID del catalogo esistente e rilegge la griglia
XML originale: `tblGrid`, `gridBefore/gridAfter`, `gridSpan`, `vMerge` e confini
fisici di tabella/cella. Non produce un nuovo FORM per il modello o un secondo
motore di compilazione.

Le coppie adiacenti richiedono orientamento univoco, anche per sequenze alternate
etichetta–valore. Le righe precedenti richiedono corrispondenza esatta degli
intervalli. Una prima riga tutta di etichette può essere schema di colonna lungo
righe di valori vuoti/segnaposto non interrotte. I paragrafi fissi della stessa
cella sono conservati insieme. Celle unite orizzontalmente richiedono copertura
esatta; quelle verticali sono accettate solo quando le estensioni distinguono
una coppia univoca, senza distribuire un'etichetta a valori indipendenti.
Continuazioni, griglie insufficienti, sovrapposizioni parziali, orientamenti
concorrenti o nuove righe miste non giustificano un arco. Una tabella annidata
può avere archi propri; le sue etichette non escono dalla cella contenitrice.

Ogni arco conserva SHA256 dell'originale, ID di destinazione e cella etichetta,
paragrafi/quote FORM, tabella, riga, intervalli e metodo. Le nuove assegnazioni
usano `form_table_link` nell'audit. I vecchi risultati già sufficienti non ricevono
metadati che invalidino inutilmente le revisioni. Le celle a segnaposto riusano
l'eleggibilità del parser, invece di essere riclassificate come testo fisso.

Tre controlli rimangono distinti:

1. La prova FORM della proprietà è limitata alla cella e agli archi espliciti.
   Una citazione vera di un'altra colonna/tabella resta respinta. L'arco prova
   una relazione fisica; la correttezza semantica della proprietà richiede ancora
   la revisione prevista da V12.
2. Fatti, citazioni e binding SOURCE mantengono i controlli precedenti. I nuovi
   archi di proprietà non estendono il contesto dei binding di ruolo. Le prove
   personali non diventano societarie e una nuova riga di anagrafica non unisce
   soggetti SOURCE diversi. La compatibilità del tipo non dimostra identità o ruolo.
3. Lo scope delle condizioni precedenti viene conservato separatamente e può
   acquisire i nuovi contesti locali pertinenti. Il veto di applicabilità legge
   anche le nuove etichette collegate: FALSE e UNKNOWN impediscono l'export,
   indipendentemente dalle condizioni omesse dal modello e dall'assenso generico.
   Una dichiarazione riconosciuta nel nuovo contesto tabellare non riceve
   autorizzazione da un fatto SOURCE; resta senza scrittura quando manca un
   flusso USER pertinente. Nessuna nuova ricevuta o nuova procedura USER inventata.

Il catalogo/input inviato al modello è invariato, inclusi gli anchor storici.
La capacità aggiunta è nel validator: il modello può continuare a omettere
campi che ora sarebbero validabili. `INVARIANTI.json` confronta anche gli AST di
costruzione input, prompt globale, chiamata, grounding SOURCE, slot e binding,
oltre ai byte del writer. Modello, provider, architettura e rappresentazione FORM
conservati; nessuna integrazione E1/E2-A.

## Test permanenti e regressione

52 nuovi test: 40 in `test_compilation_table_form.py`, 12 API persistenti in
`test_compilation_table_form_session.py` (FTS5 e Qdrant temporanei, provider
simulato). Fixture `backend/tests/fixtures/table-form-v1/`, che riusa originale
e SOURCE già sigillati di `form-applicability-v1`.

Coperti coppie adiacenti in entrambi gli orientamenti, riga precedente,
intestazione senza flag Word e più righe, celle unite orizzontali/verticali,
paragrafi multipli, segnaposto del parser, tabelle annidate e celle vuote.
Negativi: altra colonna/tabella, etichette duplicate in altra sezione,
interruzioni, griglie insufficienti, un'etichetta unita sopra più valori,
soggetti o ruoli differenti, trasferimenti di tipo, dichiarazioni non
autorizzate e applicabilità TRUE/FALSE/UNKNOWN. Conservati i test precedenti
di negazioni, condizioni non dimostrate, rami alternativi e i controesempi reali.
I test API verificano persistenza e DOCX realmente restituito dall'endpoint,
con rivalutazione al momento dell'export.

| Verifica eseguita | Esito |
|---|---|
| Suite backend completa finale | **3.048 PASS**, 234,16 s |
| Ruff backend completo | **PASS** |
| Mirati prima dell'ultimo caso segnaposto | 163 PASS |
| Mirati finali, inclusa regressione finestre di revisione | 68 PASS |
| Replay storico di export, stesso protocollo prima/dopo | **68 PASS**, tutti i DOCX byte-identici |
| Validatori V2–V12 con triplette congelate | **213 PASS di confronto**: 207 validazioni e 6 rifiuti root pregressi conservati |
| Risultati validatori identici / con nuovi archi | 199 / 14, nessuna perdita di proposta grounded |
| Verità delle condizioni MODEL nei 213 casi | invariata |
| XML, posizioni fisiche, CRC, geometria, parti e controlli | PASS sui 68 replay e sul reale |
| PDF storici | 8 campioni, tutte le sei famiglie, valori osservati e zero parole fuori pagina |

I 213 casi misurano il confronto dei validator attuali prima/dopo sulle stesse
versioni di contratto, non 213 export storici completi o nuove risposte reali.
Nessuna nuova chiamata provider nei replay, rete e SQLite vietati dai runner.
I 68 export conservano le revisioni e ricevute realmente acquisite, senza
approvare retroattivamente le nuove proposte. Minervino conserva il checkpoint
da 60 testi e una checkbox, cioè le 61 scritture precedenti; Trapani conserva
17 testi nel checkpoint reale. Bella, Cesano e CRAA hanno output identici alla
baseline del medesimo protocollo, anche quando altre posizioni restano vuote.

Nei 68 replay **29 occorrenze** di proposte prima respinte diventano grounded
anche condizionate: tre destinazioni distinte (`t25.r2.c0`, `t44.r1.c0`,
`t44.r1.c3`). Nelle nove repliche Catanzaro dello studio sono 17 occorrenze.
Nel protocollo aggiuntivo dei 213 validator sono 21 promozioni: i protocolli
si sovrappongono, i conteggi non si sommano. Restano altre proposte con citazioni
SOURCE insufficienti o binding rifiutati. Nessuna scrittura storica nuova:
le condizioni e revisioni salvate continuano a governare l'uso delle proposte.
Dettagli completi in `PROPOSTE-PRIMA-DOPO.json`, non una percentuale di accuratezza.

### Fallimenti intermedi conservati e risolti

Il primo replay ha rimosso sette scritture CRAA perché restringere il contesto
della proprietà aveva ristretto anche lo scope di una condizione e invalidato
le revisioni. Corretto separando lo scope delle condizioni; test permanente
`test_narrower_property_edge_never_removes_a_preexisting_condition_scope`.
Prima suite completa: 2 FAIL/3.028 PASS sulle 45 celle a underscore; corretta la
classificazione riusando il parser, con tre nuovi test. Suite finale ripetuta.
La prima batteria nuova aveva 8 FAIL/26 PASS: cinque test tentavano di rileggere
una bozza come FORM, due omettevano READY nello stato del test; corretti i test.
Il restante caso ha imposto il rifiuto della riga mista dentro uno schema di
colonna, evitando di leggere un soggetto fisso come etichetta. Anche un primo
assert del nuovo test di scope è stato corretto per esercitare una proposta
conditional realmente UNKNOWN. Log e acquisizioni fallite restano nei grezzi.

### Applicabilità precedente, controesempi esatti

| Caso congelato | Prima di questo intervento | Dopo questo intervento | t0.r8.c1 |
|---|---:|---:|---|
| Catanzaro B0-3 | 6 testi | 6 testi, DOCX identico | vuota, veto FALSE |
| Catanzaro E1-3 | 8 testi | 8 testi, DOCX identico | vuota, veto FALSE |

La proposta originale continua a omettere la condizione e il fatto SOURCE resta
vero. Il backend continua a vietare il ramo; la sede legale corretta resta scritta.
I vecchi artefatti erronei dello studio sono conservati, non riscritti.

## Una nuova prova UI reale, dopo il PASS della regressione

Sessione `343d6caf16d442ed88ef174ebaf4aae0`, conversazione
`conv-3824c2d370f143e4`, progetto isolato `relazioni-form-catanzaro`, versione 7
GENERATED. Chromium reale, frontend e backend ordinari su clone privato;
nessuna rotta simulata, modifica dello stato o correzione durante la prova.
Protocollo preregistrato in `PROTOCOLLO-E2E.json`; 69 moduli applicativi congelati.
FORM originale, 22 SOURCE e impostazioni dello studio verificati; il body globale
conserva anche il FORM completo identico. Deepseek-flash, thinking enabled/low,
temperatura 0,1, max 49.152. Nessun retry di qualità.

Scenario: società di ingegneria singola e Leonardo firmatario; il modello chiede
di confermare queste due scelte. Un solo turno USER le ripete, ciascuna nel
proprio slot attivo; nessuna nuova attestazione, preferenza, consenso o designazione.
Poi richiesta esplicita di bozza parziale, export e download con pulsante UI,
reload ordinario. Le due condizioni MODEL restano UNKNOWN nell'audit; le due
ricevute USER restano separate.

26 assegnazioni MODEL, 18 grounded anche condizionate, una destinazione vietata
dall'applicabilità FALSE: **17 testi SOURCE scritti**, zero valori USER e zero
checkbox modificate. Tra le tredici posizioni: **7 proposte effettive**, una
scritta (CCIAA Bari), sei ancora bloccate da SOURCE/binding; sei non proposte.
Per t44.r1.c0 il binding cita il contesto di un'altra tabella (p451), non quello
locale p711: il nuovo arco della proprietà non lo rende valido. I dati t41
non aggirano i binding rifiutati o i valori SOURCE non letteralmente dimostrati.
T43 e il CF t44 omessi rimangono vuoti, senza un'altra analisi opportunistica.

Il confronto isolato della **stessa nuova risposta** e delle stesse ricevute
con il backend precedente dà 16 testi; il nuovo dà 17, con la sola aggiunta
`t25.r2.c0 = Bari`, nessuna perdita/modifica degli altri sedici. Fatti e binding
SOURCE esatti. `paired-comparison.json` separa questa prova causale dalla
variabilità LLM rispetto alle 15 scritture della precedente sessione reale:
la diversa proposta per la denominazione sociale era già validabile prima.

Ricostruiti offline audit, selezione, DOCX ed effettivo download, esatti.
SHA256 DOCX `c2aac7af7b7917e2b520b180634f57de1eac8a2bc03150d8e45ace1cd8cbc9b2`.
PDF LibreOffice locale: 17 pagine, tutti i 17 valori osservati, due falsi negativi
dell'estrazione lineare risolti verificando i token nei rettangoli della pagina;
zero parole fuori pagina. Ispezione visiva pagine 2 (ramo vuoto e checkbox),
11 (Bari sotto CCIAA e dati nei campi corretti), 17 (prestampato/firma).
Controllo XML separato di tutte le posizioni e dei campi non selezionati.
Non eseguita una prova Word desktop; l'ispezione visiva è campionata.

Sette chiamate reali: una globale, 146,30 s; 153,81 s AI complessivi, 156.322 token,
fingerprint `e72d3c7f663d3e1383b00b3884cb4501`, uguale allo studio. Dieci GET
abortite da mount/reload della UI, nessuna POST/console/provider/driver fallita.
Trace, video, screenshot, rete, richieste/risposte e revisioni nel grezzo.
Servizi isolati arrestati dopo la raccolta.

## Limiti e problemi indipendenti non corretti

Questo è supporto generale a schemi tabellari deterministici, non interpretazione
di qualsiasi layout o testo naturale. Se griglia, soggetti o proprietà competono,
il collegamento rimane non dimostrato. Tabelle con righe fisse di soggetti,
intestazioni gerarchiche o unioni non univoche possono richiedere informazioni
che la struttura non offre: nessuna estensione indiscriminata alla tabella.
Una relazione fisica non dimostra l'equivalenza semantica fra proprietà o ruoli.

Restano i limiti preesistenti di grounding di date/indirizzi composti, equivalenze
di ruolo, condizioni USER e spiegazioni MODEL/narratore. Nella nuova bozza
`t25.r3.c1` contiene solo `01234560981`, mentre l'etichetta chiede numero **e data**:
problema indipendente noto, conservato; 17 scritture non equivale a 17 risposte
complete. Le checkbox non proposte non vengono sintetizzate dalle due conferme.
Le dichiarazioni tabellari senza un flusso USER supportato restano bloccate.
Prestampato e spaziature già presenti (anche CRAA) conservati.

Le sessioni precedenti restano leggibili: nessuna migrazione, approvazione
retroattiva o upgrade implicito. I nuovi archi non entrano nel prompt congelato
e non obbligano il modello a proporre i tredici campi. Nessuna modifica a
SOURCE, gold, modello, provider, writer, frontend o componenti estranei per
migliorare il numero di scritture. Nessun commit o push.

## File, conservazione e riproducibilità

Codice applicativo: nuovo `backend/app/compilation_table_form.py`;
modificati `compilation_global.py` (proiezione interna V12 e separazione scope),
`compilation_form_applicability.py` (nuovi contesti strutturali verificati),
`compilation_global_sessions.py` (contesto di revisione delle nuove prove).
Test nuovi e fixture indicati sopra; aggiornati STATUS/relazioni e rapporto.
Il diff è rispetto allo snapshot sporco iniziale, non un ripristino di HEAD.

`PRESERVAZIONE.json` verifica tutti gli hash protetti, originali e studio/E1/E2-A,
intero DB logico live, 29 sessioni e 273 file live, 12 file knowledge;
38 sessioni e 490 file preesistenti del clone conservati, una sola nuova sessione.
Le snapshot prima/dopo includono codice e test; nessuna migrazione/reindicizzazione.

Backup separato `audit-completo.tar.gz`, SHA256 e manifest nella consegna.
La prova conclusiva è [VERIFICA-BACKUP.json](<../benchmark ufficiale/table-form-links-20261020-01/VERIFICA-BACKUP.json>):
estrazione indipendente, verifica hash, replay 68+68 (136 DOCX), 213+213 risultati
di validator, export reale e confronto causale reale ricostruiti usando solo il
codice estratto; provider e SQLite vietati nei runner di replay. Chiavi, `.env`
e DB privati esclusi e scansione delle credenziali effettive prima dell'archivio.
Il solo push del repository non salva i grezzi esclusi da Git: il tar separato
è l'artefatto necessario. Comandi offline e limiti delle dipendenze nel README.
