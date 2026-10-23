# CRAA: conservazione delle risposte USER — 20 ottobre 2026

Intervento circoscritto concluso. [Consegna](../benchmark%20ufficiale/craa-user-20261020-01/README.md),
[DOCX reale](../benchmark%20ufficiale/craa-user-20261020-01/e2e/craa/bozza.docx),
[PDF](../benchmark%20ufficiale/craa-user-20261020-01/e2e/craa/bozza.pdf),
[prova integrale USER](../benchmark%20ufficiale/craa-user-20261020-01/e2e/craa/prova-conservazione-USER.json).

## Diagnosi: due problemi distinti

Il caso storico CRAA non dimostrava la perdita di una risposta USER lunga.
Il MODEL aveva proposto un chiarimento sul firmatario con `reason` di **225
caratteri**, contro il massimo 200 di `UserFieldRequest`. Era rifiutato il
metadato della richiesta generata, non il testo dell'utente. La proposta e
l'errore restano negli artefatti originali; i messaggi USER storici sono nella
conversazione. Un test permanente congela questa distinzione. Quel limite
MODEL non è modificato in questo intervento: non si presenta il recupero USER
come correzione del chiarimento storico.

L'analisi del percorso attuale ha invece identificato tre rischi concreti:

1. Il composer imponeva `maxLength=4000`: un inserimento oltre limite poteva
   essere troncato dal browser; il testo effettivamente inviato era inoltre
   sottoposto a `trim()`, eliminando spazi e righe esterni.
2. Dopo l'invio il composer era svuotato. Un errore HTTP/rete lasciava il testo
   soltanto nel turno React corrente, perso al ricaricamento se non ricevuto e
   salvato dal server. Non c'era un comando esplicito per riutilizzarlo.
3. La API accetta messaggi fino a 4.000 caratteri, ma gli estratti di
   `ClarificationReply` e `ChatControl` erano limitati a 2.000. Un messaggio
   lecito poteva essere scartato se il router citava un estratto più lungo.
   Questo è distinto dall'effettiva capacità di interpretare la risposta.

## Correzione e confini

Il backend conserva il tetto di ingresso di 4.000 caratteri. Soltanto il limite
sugli estratti V12 e sui controlli di sessione è allineato a quel tetto. Nessun
cambio alle azioni ammesse, agli slot attivi, alla pertinenza indipendente,
all'univocità, alle citazioni, alla validazione del valore o al grounding SOURCE.
Il tetto di 1.500 caratteri per un valore rimane: un contesto lungo non rende
lecito un valore che il campo non può gestire. Non si tronca un valore per
farlo superare. Il vecchio `ChatFieldReply` legacy rimane invariato.

Il frontend invia il testo originale, inclusi spazi e nuove righe. Rimuove il
taglio nativo, conta i caratteri Unicode come il backend e blocca esplicitamente
l'invio sopra 4.000, mostrando come dividere la risposta. Il testo oltre limite
rimane disponibile: non viene inviato un prefisso fingendo che sia completo.

Una copia testuale e il riferimento al documento sono conservati in
`sessionStorage`, separati per progetto e conversazione. Il pulsante
**Recupera messaggio** ripristina il testo, senza inviarlo. Una nuova bozza
scritta durante la richiesta non viene cancellata quando arriva la risposta
precedente. Nella nuova conversazione viene trasferita solo la relativa copia.
Un errore `failed`, una configurazione mancante o un errore di rete mantengono
la copia; un'elaborazione conclusa la rimuove solo se è ancora quella inviata.
I turni salvati offrono **Riutilizza messaggio**, anche senza una copia locale.
Il nuovo invio rimane una scelta esplicita e riguarda lo stato corrente.

La conversazione server conserva già `question` integralmente: la correzione
non aggiunge tabelle, endpoint, migrazioni o un registro parallelo. I normali
errori di modello durante una compilazione salvano una risposta fallita con
la domanda originale. Un rifiuto HTTP prima dell'acquisizione non viene
spacciato per un messaggio salvato nel database: in quel caso serve la copia UI.

Limiti dichiarati: la copia locale sopravvive al ricaricamento della stessa
scheda, non garantisce il recupero dopo la sua chiusura. Lo storage indisponibile
produce un avviso esplicito di copiare il testo prima di uscire; il recupero
in memoria resta disponibile finché la pagina è aperta. Dopo la ricezione
server, la cronologia persistita offre un secondo percorso. Non c'è reinvio
silenzioso, recupero automatico di sessioni obsolete o accettazione di decisioni
non verificate. Un messaggio entro limite può restare semanticamente ambiguo:
la lunghezza accettata non è una garanzia di interpretazione.

## Test permanenti e regressione

**53 nuovi casi: 33 backend e 20 frontend.** Test con provider simulati,
persistenza e API reali isolate. Coprono 2.000/2.001/3.999/4.000/4.001 caratteri,
spazi e righe, Unicode, estratti completi, limiti dei valori, testi estranei,
ambigui, valori inventati, persona diversa, errori provider e rifiuti HTTP.
Il percorso positivo verifica controllo indipendente, ricevuta USER, separazione
SOURCE e un export con un valore USER realmente pertinente. Nessuna attestazione
è derivata dalla semplice presenza di dati.

Frontend: copia dopo errore di rete/schema/configurazione, ricaricamento,
richiesta ancora in transito, cronologia server senza copia locale, cambio
progetto/conversazione, nuova chat, nuova bozza durante la richiesta, storage
inaccessibile, dati corrotti e nessun reinvio automatico. Le prove software
non sono misure della qualità del provider.

| Controllo | Esito |
|---|---|
| Suite backend | PASS: 2.877 test, 217,26 s |
| Suite frontend | PASS: 126 test, 6,70 s |
| Ruff / lint frontend / build frontend | PASS |
| Audit e DOCX storici ricostruiti | PASS: 22 confronti esatti, rete/SQLite vietati |
| Minervino V12 | PASS: 61/61 conservate |
| CRAA storico | PASS: 9 scritture XML conservate; difetti PDF storici invariati |
| Trapani, Catanzaro, Bella, Cesano e altri replay precedenti | PASS: DOCX e audit identici ai riferimenti della fase precedente |

I 22 confronti comprendono i dieci casi, sia con contesto conservato sia con
quello USER già registrato, più i due DOCX reali della fase firmatario da 17
scritture. I nuovi collegamenti non ottengono revisioni retroattive. Non si
ricalcolano aspettative sulla base di un nuovo output LLM.

Controfattuale del solo contratto: lo stesso estratto lungo è REJECTED dal
codice precedente, ACCEPTED da quello attuale. Non è una prova che il modello
reale debba citare sempre l'intero messaggio; nel nuovo E2E sceglie clausole
brevi, mentre router e guard ricevono il testo completo.

Conservati i RED e gli errori di allestimento: primo npm senza Node nel PATH,
fixture inizialmente copiata nella directory errata, confronti di test su campi
non esposti dalla vista pubblica e un primo comando contro gli audit `before`
della fase precedente anziché la sua versione finale. Questi ultimi non sono
regressioni del prodotto. Il RED sul limite di estratto e i sette FAIL iniziali
UI restano osservabili; le aspettative corrette distinguono l'estratto normalizzato
dall'originale integrale. Un primo controllo pytest del codice precedente
importava il percorso corrente: sostituito da processi Python distinti con
percorso del modulo verificato, conservando il log iniziale.

## Una nuova prova reale CRAA

Nuova sessione **bc286f4fd88d46d89d55edf0595d68e7**, conversazione
`conv-8e2093a65dd140fa`, progetto `conservazione-user-lunga-craa`, FORM 201,
versione finale 7 GENERATED. Una globale reale nuova, nessuna proposta congelata,
nessuna modifica applicativa durante la prova, nessuna correzione manuale dello
stato o retry di qualità. HEAD `99ab052` dirty, 116 hash backend/frontend congelati.
Stesso originale CRAA, snapshot di 22 SOURCE, prompt globale e configurazione
DeepSeek delle prove precedenti. Hash completi in `PROTOCOLLO.json` e `input/`.
`deepseek-flash`, thinking globale enabled/low; router/sintesi/guard thinking
disabled. Lo schema degli estratti del router ha il solo limite aggiornato.
Alias e fingerprint non certificano pesi immutabili del provider.

Scenario sintetico versione 2, scritto prima dell'inferenza: firmatario e
partecipazione scelti esplicitamente per CRAA, senza trasferimenti fra gare.
Preferenze, attestazioni, esecutori, integrazione e luogo/data rimangono distinti.
Le decisioni aziendali non attestano coerenza della classe merceologica o
fatturato. Le risposte seguono solo le domande effettivamente poste.

Prima dell'avvio, la UI conserva un inserimento oltre 4.000 dopo paste/ricaricamento,
lo recupera integro e ne blocca l'invio, senza chiamate provider. Poi il sistema
chiede ruolo del sottoscrittore, coerenza CCIAA e requisito economico. La risposta
preregistrata contiene **3.113 caratteri**, spazi iniziali/finali e nuove righe.
Viene scritta, recuperata dopo reload e inviata con SHA256:
`52342bd3aaafe13be4213326d3a45610f70fedc34c5932ddc8a915dc02ce542e`.

La stessa stringa è verificata in textarea, richiesta/risposta HTTP, richiesta
router, richiesta guard, conversazione riletta e `conversation_turns.question`
in SQLite. Gli estratti decisionali sono clausole più brevi, con spazi esterni
normalizzati da StrictModel; non sostituiscono il messaggio originale.

Tre ricevute pertinenti persistite:

- `c_impresa_role`: conferma USER del ruolo del sottoscrittore per questa domanda;
- `c_societa_cciaa`: SKIP esplicito della conferma di coerenza merceologica;
- `c_fatturato`: SKIP esplicito del requisito economico.

Nessun valore personale trasformato in dato USER, nessuna conferma ottenuta dai
paragrafi di contesto, nessuna checkbox selezionata. La risposta lunga non provoca
export: segue una richiesta esplicita separata. Rilettura della conversazione e
download tramite UI ordinaria, senza operazioni sullo stato interno.

| Stadio reale | Numero |
|---|---:|
| Fatti SOURCE proposti / grounded | 13 / 13 |
| Assegnazioni valore MODEL proposte | 13 |
| Assegnazioni respinte per citazione FORM | 2 |
| Campi sospesi come alternative non selezionate | 2 |
| Proposte singole grounded / revisionate | 9 / 9 |
| Applicabili / scritte | 7 / 7 |
| SOURCE corrette nel DOCX / USER scritte | 7 / 0 |
| Ricevute decisionali USER accettate | 3 |
| Nuove checkbox / scritture indebite rilevate | 0 / 0 |
| Condizioni ancora UNKNOWN | 2 |

Sette dati aziendali completi, con citazioni corrette, a pagina 1. Due proposte
CCIAA disponibili ma non scritte perché subordinate dal nuovo MODEL alla
conferma più ampia sulla coerenza dell'attività, rinviata esplicitamente. Le due
condizioni rinviate restano UNKNOWN, senza passare a FALSE o TRUE. Gli anni
2024/2025 hanno citazioni FORM rifiutate; i due importi restano alternative senza
selezione e non vengono usati per attestare il fatturato. Il nome del firmatario
`p5.s0` è ancora omesso dal MODEL; il riconoscitore SOURCE della fase precedente
non copre questo blocco isolato. Non si implementa un recupero ulteriore durante
la prova. Il nuovo output non contiene chiarimenti: non esercita il vecchio
metadato `reason` da 225 caratteri.

Il DOCX storico da nove scritture rimane identico nel replay. La nuova prova ne
scrive sette per i rinvii e le condizioni differenti dell'output reale: non è
una perdita di testo USER né una regressione deterministica di due scritture.
Non viene forzato il conteggio precedente. Nucleo SOURCE ancora vuoto: nome
omesso e due dati CCIAA rinviati. Nessuna percentuale di accuratezza generale.

## DOCX, PDF, errori e costi

XML/CRC, sette posizioni fisiche, otto tabelle, prestampato, stili, controlli,
report e download verificati. Solo `word/document.xml` cambia. Tutti i `tcPr`,
`trPr`, `tblPr`, `tblGrid` rimangono identici. PDF sette pagine, sette valori
leggibili, nessuna parola oltre bordo; viste pagine 1/4/7. Firma e attestazioni
non compilate; i testi prestampati non diventano requisiti verificati.
Restano unioni cosmetiche come «impresaMapi», «PECmapi», già presenti nel percorso
writer. Word desktop non provato.

**Nessun intervento CCIAA:** le celle della nuova bozza sono vuote per rinvio,
quindi la loro invisibilità non è verificabile su questo export. Non si dichiara
risolto il difetto. Nel replay restano i nove valori XML e le medesime geometrie
storiche; la diagnosi del rendering richiede un intervento separato.

Il primo driver browser è stato avviato senza PTY ed è rimasto su stdin chiuso
al checkpoint iniziale. È stata riaperta **la stessa sessione**, senza nuova
globale: snapshot/network iniziali conservati, trace iniziale non finalizzato;
trace/video del secondo driver, dal recupero lungo al download, finalizzati.
Il primo processo/Chromium è stato terminato esplicitamente. Nessuna modifica al
prodotto. Nel driver finale 15 GET abortite ai reload/mount; nessun POST fallito
o errore provider. Non si nasconde il limite dell'acquisizione iniziale.

Sette chiamate: tre router, una globale, due sintesi e un guard. **95.674 token**
(73.536 input + 22.138 output), globale 87,21 s, somma HTTP 96,42 s, **0,021002 USD
stimati**, non fattura. Tutte HTTP 200/stop, nessun retry. La somma esclude attese
operatore, test, rendering e riapertura browser. Un campione non dimostra variazioni
statistiche di tempo/costo/qualità. I controlli della risposta lunga usano il
normale percorso router/guard: nessuna nuova generazione globale.

## Consegna e continuità

Modificati due file esistenti del prodotto: `backend/app/compilation_chat.py` e
`frontend/src/pages/ProjectWorkspacePage.tsx`; aggiunto `chatMessageRecovery.ts`.
Test/fixture e file precisi in [FILES-MODIFICATI.json](../benchmark%20ufficiale/craa-user-20261020-01/FILES-MODIFICATI.json).
Nessun nuovo framework, agente, endpoint o modifica a DB, FORM, modello, prompt
globale, grounding SOURCE, validatori di binding/attribuzione, parser o writer.
Nessuna migrazione/reindicizzazione.

Preservati 1.358 altri file, 29 sessioni live, 285 file storage e 37 sessioni
pregresse nel clone; una nuova isolata. Tutti i 116 hash applicativi/frontend
invariati durante la prova. Servizi isolati arrestati. Nessun commit/push o
adozione di baseline generale.

Grezzi in `backend/data/compilation-audit/craa-user-20261020-01/`; backup separato
nella consegna, senza DB, `.env` o credenziali. La verifica estratta ricostruisce
22 audit/DOCX precedenti più il nuovo CRAA, senza rete/SQLite; controlla anche il
contratto degli estratti prima/dopo. STATUS.md e relazioni.md aggiornati.
Esito PASS circoscritto ai sei criteri USER; chiarimento MODEL storico, copertura
del firmatario CRAA e visibilità CCIAA rimangono problemi separati. Arresto alla consegna.
