# Analisi della compilazione UI: domanda-iscrizione.compilato(6).docx

17 ottobre 2026. Analisi richiesta dall'utente, **senza modificare codice
applicativo, prompt, validatori, writer o sessioni e senza nuove chiamate LLM**.
Il download [compilato(6)](<../domanda-iscrizione.compilato(6).docx>) coincide
byte per byte con l'export del server. SHA-256:
`dd261421ed246645e7b9d084985a6dfcab17d8ac67b494878065fae6e9323523`.

Sessione `f06e75dd1ecf4c0fae668668c153a9df`, conversazione
`conv-423c9cc6f0f3438d`, export `850ebea2fa464ba0aa6a881d5d8313d4`.
Non è il replay manuale di B0-03: è una nuova risposta reale dalla UI.

## Risultato osservato nel Word

**25 valori fisicamente inseriti: 24 SOURCE e il nome USER Leonardo Montemurro.**
I 25 valori coincidono con quelli attesi dal gold sintetico, usando le
equivalenze congelate; questo confronto non certifica ogni singola citazione.
Il problema principale osservato è la copertura insufficiente.

| Blocco testuale del gold | Compilati | Attesi nello scenario |
| --- | ---: | ---: |
| Firmatario: nome, anagrafica, carica | 1, il solo nome USER | 9 |
| Dati generali operatore | 8 | 10 |
| Dati societari nel ramo società | 9 | 9 |
| Tre soci | 0 | 24 |
| Direttrice tecnica Elisa | 7 | 8 |
| Totale target testuali SOURCE del gold | **25**, dei quali uno USER | **60** |

Restano 35 target vuoti: 8 del firmatario, 24 dei soci, CF del direttore e
2 dati generali dell'operatore. I primi 33 non hanno una proposta; gli ultimi
due sono proposti con valore corretto ma citazione FORM respinta.
Scelte della pratica, preferenze, dichiarazioni e firma restano distinte da
questi 60 target. Non si considerano tutti i 267 candidate obbligatori.

## Leonardo: quali dati erano realmente disponibili

In `integrazione-company.md`, SOURCE `-53/-54`, già **incluse nell'input
effettivamente inviato al modello**, sono documentati:

| Dato | Valore nella SOURCE | Risultato nel Word |
| --- | --- | --- |
| Nome | Leonardo Montemurro | Inserito dopo risposta USER |
| Luogo di nascita | Lecce (LE) | Comune e provincia vuoti |
| Data di nascita | 14 novembre 1982 | Vuota |
| Residenza | Bari (BA), Via Amedeo 24 | Tre componenti vuote |
| CF personale dimostrativo | MNTLRD82S14E506X | Vuoto |
| Carica attestata nello scenario | Amministratore unico e rappresentante legale dal 2 ottobre 2026 | Vuota |

Quindi la mancanza di queste otto scritture **non dipende dall'assenza dei dati
nella KB o dal loro taglio prima della chiamata globale**. Non risultano invece
telefono, e-mail e PEC personali di Leonardo: i recapiti aziendali non devono
essere trasferiti automaticamente alla persona. La rappresentanza è documentata;
non sono per questo documentati ogni procura o potere speciale.

Chiedere **chi firma questa pratica** era corretto: l'unico messaggio prima
dell'analisi era «compila». Essere rappresentante nella KB non è la decisione
di firmare una specifica domanda. Il contesto USER di avvio è stato passato
correttamente, ma conteneva solo quel comando generico.

La sequenza effettiva è:

1. Il modello globale riceve tutte le SOURCE e ancora nessuna scelta nominativa.
2. Non propone gli otto dati del firmatario: scrive in coverage «Dati personali
   del sottoscritto non assegnabili senza scelta del firmatario» e «Ruolo del
   firmatario non attestato». Quest'ultima motivazione non dimostra che la
   carica manchi nelle SOURCE.
3. L'utente conferma partecipazione e tipologia societaria. Nella prima
   risposta il nome era ancora «Leonardo [COGNOME DA COMPLETARE]»: il sistema
   richiede correttamente un nominativo completo.
4. Alla risposta «Leonardo Montemurro», `apply_replies` acquisisce il valore
   del solo slot `p12.s0`. Non effettua una ricerca della persona nella KB né
   crea proposte per nascita, residenza, CF e carica.
5. La sintesi successiva riceve il nome USER e l'audit congelato; non riceve
   il record anagrafico SOURCE completo di Leonardo. Negli input delle tre
   sintesi il suo CF non compare. Esauriti gli slot, propone l'export parziale.

Questo è un limite del collegamento **scelta USER → dati SOURCE già disponibili**.
Il nome non è stato ignorato: è stato registrato nel suo campo, senza risolvere
le dipendenze che diventano determinabili dopo quella scelta.

## Soci: omissione del modello, prima della validazione dei binding

La SOURCE `-54` contiene titolo «Soci della società al 15 ottobre 2026»,
intestazioni e righe complete di Luca Ferri, Elisa Romano e Andrea Greco,
con qualifiche, CF, albo, sezione, provincia, data e numero d'iscrizione.
Sono due ingegneri e un architetto. La stessa tabella è presente nell'input
reale, identica a quella di B0.

**Non sono stati proposti 24 valori e poi respinti:** nell'output non ci sono
assegnazioni ai soci né un loro binding. Il modello ha emesso questa motivazione:

> Soci presenti in tabella aziendale, ma il ruolo 'socio' non è attestato nel formato richiesto per il binding

Quindi riconosce l'esistenza dei soci, ma rinuncia a formulare la proposta.
I controlli corretti non possono recuperare un'assegnazione che non esiste.
Il gruppo di spiegazione copriva tutte le 24 destinazioni; il controllo FORM
ne ha accettato soltanto cinque, con 19 spiegazioni respinte per contesto
non locale. Sono spiegazioni dei vuoti respinte, **non 19 valori persi**.

Esiste un disallineamento documentabile nel prompt effettivamente inviato:
continua a descrivere i vecchi formati di ruolo («ruolo: persona», intestazione
«persona - ruolo», riga «RUOLO persona - dettagli») e dice:

> Ruolo e valore devono essere nello stesso chunk SOURCE.

Non descrive il supporto strutturale titolo/intestazioni/riga e i collegamenti
di identità verificabili aggiunti al backend. Il rifiuto dichiarato dal modello
è coerente con quelle istruzioni. **È una spiegazione causale plausibile e
fortemente circostanziata, non un effetto isolato da un confronto controllato**:
non sono stati modificati prompt o eseguite nuove generazioni per provarlo.

## Elisa: sette dati presenti, CF omesso pur essendo nella tabella

Il blocco p50 richiede il direttore tecnico per la società di ingegneria.
Elisa è stata inserita in quel blocco, non scambiata per un altro professionista:
nome, qualifica, albo, sezione, provincia, data e numero d'iscrizione.
Manca il CF `RMNLSI85C47A662Y`, presente nella sua riga soci in SOURCE `-54`.
Il modello dichiara «CF non presente nel record del direttore tecnico».

È vero che la specifica riga nominativa del direttore in `-55` non contiene
il CF; non è vero che esso manchi dalla KB. Nome completo, ordine e numero
8421 consentono il collegamento documentato con la riga di Elisa già studiato
nei replay. Qui il modello non ha proposto quel fatto, dunque il verificatore
non ha potuto valutarne il collegamento.

L'audit registra invece **sette recuperi `fact_source_record`** sulle sette
proposte del direttore. Le correzioni sono quindi operative nel run reale:
non si sta osservando un vecchio verificatore non aggiornato.

La provincia «Bari» è conforme alla colonna Provincia della tabella `-54`.
La citazione usata dall'output è però la riga `-55`, che menziona «Ordine degli
Ingegneri di Bari»: supporto meno esplicito della colonna della tabella. Non si
equipara la conformità del valore al gold alla completezza di quella citazione.

## Domande e messaggi del narratore

Le tre domande iniziali riguardavano:

1. Partecipante/qualità con cui si presenta il modulo (`c_participant`).
2. Tipologia società di ingegneria ex clausola p39 (`c_p39`).
3. Nome del firmatario (`p12.s0`).

Le prime due sono parzialmente sovrapposte nella formulazione, ma corrispondono
a due condizioni diverse proposte dal modello. Non si confondono natura S.r.l.,
scelta della pratica e ruolo della persona. Entrambe le conferme sono state
registrate; nessuna delle 24 proposte SOURCE è stata persa per UNKNOWN.

Il massimo di tre domande è **per turno**, non un tetto complessivo: infatti
è stato richiesto nuovamente il nome incompleto. Dopo l'acquisizione del nome
il pool del backend è vuoto. Le altre lacune sono omissioni/coverage, non slot
di domanda già costruiti; il sistema esaurisce la propria coda, non le informazioni
necessarie per completare il documento.

La prima sintesi dice «Non risultano invece dati su soci» e nega la disponibilità
del CF della direttrice. La prima affermazione contraddice persino la motivazione
del modello, che riconosce la tabella; la seconda generalizza la mancanza in
un record all'intera KB. **Sono comunicazioni di assenza non fondate.**

Al narratore arrivano audit e citazioni ridotte delle proposte, non l'intero
corpus SOURCE. La mappa `source_role_targets` contiene soltanto il direttore;
quel blocco ha già sette proposte e risulta `proposals_present`. Non esiste un
analogo indizio per la tabella dei soci, né un alert per il solo CF mancante.
`unassessed_source_roles` è quindi vuoto nelle tre sintesi. Questo contribuisce
a non rendere visibile al narratore il problema dei dati disponibili ma omessi.
Il prompt della sintesi vieta già di spacciare `source_not_found` per prova
di assenza: il testo prodotto viola comunque questa istruzione.

## Due rifiuti FORM e ciò che non ha causato le omissioni

Il modello propone correttamente Bari e BA nei dati generali iniziali, ma cita
solo `[[p15.s0]] (` e `([[p15.s1]])`. Il backend rifiuta entrambi con «Il solo
marker non documenta la richiesta del campo». Sono problemi di ancoraggio
FORM, non dati SOURCE mancanti; non sono stati aggirati in questa analisi.

Il percorso misurato è: 19 fatti → 26 assegnazioni → 24 proposte grounded →
24 revisionate, nessuna sospesa → 24 SOURCE + un nome USER nel DOCX.

In questa esecuzione **il limite di 40 proposte del narratore non viene raggiunto**.
Nessuna proposta grounded è stata tolta dal narratore o dal writer. Entrambe
le condizioni UNKNOWN dell'audit hanno ricevuta USER confermata per l'export.
Nessun gruppo checkbox proposto: i 13 controlli nativi sono invariati.

## Controllo fisico e limiti della misura

Valori estratti dai singoli slot identici al report; altri segnaposti e testo
prestampato invariati, ZIP/CRC valido, sole modifiche a `word/document.xml`.
Quattro tabelle e 13 controlli conservati. Rendering del download, senza
ritoccarlo: dieci pagine LibreOffice; controllate visivamente 1, 3, 4 e 10.
Soci vuoti a pagina 3 e direttore parziale nello stesso blocco. Due giunzioni
senza spazio («professionaleOrdine», «Adella»), e firma vuota isolata a
pagina 10: problemi di presentazione ancora presenti. Non verificata la
paginazione in Microsoft Word.

La chiamata globale già registrata dura circa 125,8 s; tre sintesi circa
6,6 s complessivi. Non sono il tempo totale UI: mancano routing, I/O e tempo
dell'utente. Usage globale: 76.163 token input, 32.252 output, dei quali
23.325 reasoning secondo il provider. Nessuna di queste chiamate è nuova.

I 48 valori del replay manuale B0-03 non erano una promessa di scritture
automatiche su una nuova risposta. Questa prova mostra che il verificatore
migliorato funziona sulle proposte ricevute, ma restano seri limiti nella
produzione delle proposte, nel riuso dei dati dopo una scelta USER e nel
resoconto dei vuoti. Non è un confronto controllato che isola una regressione:
SOURCE/FORM/schema coincidono, mentre risposta reale e timing USER sono diversi.

## Conservazione della diagnosi

[Dati e misure](benchmarks/2026-10-17-ui-compilato6.json),
[controlli](benchmarks/2026-10-17-ui-compilato6-checks.json),
[backup](benchmarks/2026-10-17-ui-compilato6-audit.tar.gz).
Raw: `backend/data/compilation-audit/ui-compilato6-20261017-01/`, con download,
originale, input/request/output, audit, tre sintesi, trace di routing, cronologia,
stato, report, conteggi, estrazione fisica e rendering. DB aperto in sola lettura.
Nessun test software, replay dei validatori o Ruff rieseguiti: è una diagnosi
dei risultati effettivi, non un'implementazione. Nessun commit o push.
Controllo finale: 216 file di codice/test invariati, tutte le 29 sessioni
invariate per ID/versione/stato e 22 artefatti originali identici alle copie.
