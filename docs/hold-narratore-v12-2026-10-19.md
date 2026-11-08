# V12: divergenza degli otto hold del direttore tecnico

19 ottobre 2026. Intervento limitato alla differenza fra replay61 e chat53.
Preservati working tree, database, sessioni e artefatti originali. Nessun
commit/push. Grounding, condizioni FORM B0, writer, API, modello e impostazioni
del provider invariati. Cambia soltanto il modulo del narratore e i relativi test.

**Risultato: il replay della rivalutazione motivata recupera gli otto testi e
produce 61 scritture, conservando i 52 testi precedenti e la checkbox. La chat
reale precedente resta a 53: non è stata eseguita una nuova prova UI.**

- [Word parziale verificato](../nuovi%20dati/domanda-iscrizione.V12-HOLD-VERIFICATO-20261019.docx),
  [PDF](../nuovi%20dati/domanda-iscrizione.V12-HOLD-VERIFICATO-20261019.pdf),
  [report di esportazione](../nuovi%20dati/domanda-iscrizione.V12-HOLD-VERIFICATO-20261019.report.json).
- [Misure](benchmarks/2026-10-19-v12-narrator-holds.json),
  [tracciato degli otto campi](benchmarks/2026-10-19-v12-narrator-holds-trace.json),
  [controlli](benchmarks/2026-10-19-v12-narrator-holds-checks.json).
- Base precedente: [rami V12](rami-v12-direttore-checkbox-2026-10-19.md).

## Chi introduce e chi conserva gli hold

Le richieste e risposte originali sono in
`backend/data/compilation-audit/v12-narrator-holds-20261019-01/saved-chat/`.
Sessione originaria `133483f76343416082b954f6f7bfd777`, conversazione
`conv-a813341763334b44`. La cronologia è ricostruita con richieste HTTP,
risposte del provider, risultati della sintesi e checkpoint persistiti:

| Passaggio originale | Proposte nella finestra | Hold nuovi | Hold confermati dal modello | Hold ereditati |
|---|---:|---:|---:|---:|
| Sintesi `90a6ab…`, v3 | 40 | 0 | 0 | 0 |
| Continuazione `94aabd…`, v5 | 11 | 0 | 0 | 0 |
| Risposta USER e aggiornamento delle prove, v6 | — | 0 | 0 | 0 |
| Continuazione `a6b831…`, v8 | 17 | 8 | 0 | 0 |
| Export originale, v9 | nessuna nuova sintesi | 0 | 0 | 8 |

Dopo USER, i nove dati del firmatario e gli otto dati tecnici richiedono la
revisione della proposta aggiornata: 17 valori. Il modello restituisce
`held_proposal_slots=[10,11,12,13,14,15,16,17]`, precisamente gli otto tecnici.
Il backend traduce gli slot in ID, li unisce ai vecchi hold e li persiste.
L'export li esclude. La persistenza non costituisce una seconda conferma LLM.
Nessun validatore SOURCE introduce questi hold: i valori sono grounded e
l'applicabilità è già verificata.

Il vecchio schema non contiene motivi, requisiti mancanti o citazioni degli
hold. Le risposte HTTP salvate contengono soltanto `role` e `content`, senza
un motivo separato. **La motivazione privata del modello nella chiamata
storica non è recuperabile.** Il difetto meccanico è certo: otto sospensioni
MODEL nuove, prive di spiegazione, restano bloccanti attraverso l'unione
persistente. L'interpretazione del rinvio USER era un'ipotesi, fino alle due
verifiche mirate descritte sotto; non si riscrive l'audit storico.

Nel vecchio input i valori risultavano `conditional=false` e `deferred=false`:
quest'ultimo indicatore riguarda il collegamento diretto alla singola condizione.
Erano presenti ruoli, SOURCE e risposte USER, ma non la prova composta
`branch_evidence` né un'esposizione completa dell'applicabilità effettiva.

## Che cosa manca davvero, secondo le prove disponibili

Il FORM, paragrafo50, richiede:

> la quale ha come Responsabile della Progettazione (per le società di professionisti) o Direttore Tecnico (per le società di ingegneria):

La SOURCE `-55`, nello stesso input congelato, attesta nominativamente Elisa
Romano come direttore tecnico dell'operatore. I binding verificati attestano
le proprietà della stessa persona. La ricevuta USER positiva già acquisita
sceglie per questa pratica «società di ingegneria» e identifica separatamente
Leonardo Montemurro come firmatario. Quella scelta non prova dati anagrafici o
poteri: le rispettive prove SOURCE restano necessarie e invariate.

La ricevuta su `c_dt` rimane SKIP:

> Rinvia soltanto il secondo punto: non fornisco una conferma aggiuntiva sul ruolo del direttore tecnico.

Non è trasformata in consenso. Il verificatore esistente prova il ramo con
clausola FORM, scelta USER pertinente e ruolo SOURCE esplicito per persona e
azienda. Il modulo non richiede una seconda decisione USER per ripetere quel
medesimo ruolo già documentato. Un diniego, richiesta di lasciare vuoto il
campo, designazione diversa o attestazione ulteriore rimangono bloccanti.

Natura giuridica, categoria scelta per la pratica e poteri del firmatario
restano dimensioni distinte. Non si deduce una modalità di partecipazione da
S.r.l., né una designazione professionale dalla presenza di un direttore.

## Esaurimento degli artefatti e confronto mirato reale

Prima delle chiamate sono stati esaminati tutti i tre input/output originali,
trasporti HTTP disponibili, routing delle risposte USER e transizioni salvate.
La mancanza del motivo nello schema rende impossibile una diagnosi più precisa
usando soltanto tali risposte. Questo limite è registrato prima delle chiamate
in `historical-hold-trace.json` e `protocol.json`.

Sono state quindi eseguite **due sole chiamate al narratore**, senza nuova
analisi globale, nuovi valori o decisioni USER. Stessi otto valori, stesso
modello configurato `deepseek-flash`, thinking disabilitato come già previsto
per la sintesi, temperatura0,1 e limite2048 token. Il confronto riguarda la
presenza delle prove di applicabilità nel contesto, non il FORM o il modello.

| Prova reale | Informazioni esposte | Hold MODEL | Prompt token | Output token | Totale | Secondi |
|---|---|---:|---:|---:|---:|---:|
| A | contesto degli otto valori senza prova composta di applicabilità | 8 | 9.302 | 1.183 | 10.485 | 4,188 |
| B | medesimo contesto con condizioni effettive, ricevute e `branch_evidence` | 8 | 10.427 | 1.228 | 11.655 | 4,237 |

**Il solo passaggio delle prove non risolve il difetto.** In B il modello,
pur riconoscendo il ruolo documentato, indica per tutti gli otto valori:
`missing_information="Conferma del ruolo attuale di Direttore Tecnico"`.
Cita esattamente la clausola FORM del paragrafo50 e motiva la sospensione
con il rinvio USER della conferma aggiuntiva. A esplicita lo stesso problema
con formulazione più lunga. Sono osservazioni delle due nuove risposte,
non recupero retroattivo del pensiero della risposta originale.

Le due prove usano lo schema esplorativo che ammetteva anche una revoca
esplicita: non è stata restituita alcuna revoca. Nel codice finale tale capacità
è rimossa: il narratore può motivare un hold, non autorizzare liberamente una
scrittura. Una prova per variante non misura una probabilità di successo generale.

Totale: **2 chiamate reali, 22.140 token**, di cui19.729 input e2.411 output.
Zero nuove chiamate globali. Nessun costo in USD stimato; prezzo non verificato.
Nessuna chiamata successiva alle due prove.

## Correzione circoscritta e osservabile

Unico file applicativo modificato durante questo intervento:
`backend/app/compilation_global_dialogue.py`.

1. Il contesto collega ciascun valore alle proprie condizioni effettive,
   citazioni FORM, ricevute USER e prove composte già validate. Non cambia
   la decisione dei verificatori. Una versione del contesto nel fingerprint
   richiede una revisione limitata dei soli valori interessati; i52 precedenti
   mantengono la revisione. Questo da solo non elimina nessun hold.
2. Il contratto del narratore aggiunge `hold_reviews`: slot, tipo di ostacolo,
   frase di motivazione, informazione mancante, citazione e condizione pertinente.
   Sono annotazioni MODEL, mai nuove prove SOURCE. I vecchi output restano
   leggibili con motivo `not_recorded`; non si inventano spiegazioni mancanti.
3. `hold_records` e `hold_transition` conservano decisione originale MODEL,
   verifica del motivo e distinzione nuovi/confermati/ereditati/liberati.
   Gli artefatti per chiamata conservano la cronologia completa.
4. Il backend rifiuta soltanto il motivo ridondante dimostrato: richiesta
   letterale «Conferma del ruolo attuale di {ruolo attestato}», riferita alla
   stessa clausola FORM integrale, stesso soggetto, stesso binding e stesso
   campo nel perimetro della condizione. Occorrono prova composta già validata,
   tutte le condizioni effettive TRUE, proprietà personale grounded e campo
   selezionabile. Non basta uno stato TRUE isolato.

Un'altra informazione mancante, citazione diversa, ambito incoerente, motivo
SOURCE/FORM/decisione USER, attestazione, rifiuto o rinvio del singolo campo
conserva l'hold. Anche un ostacolo precedente diverso resta protetto. La regola
non confronta sinonimi e non contiene nomi, ID o valori del caso Minervino/Mapi.
Formulazioni non supportate restano irrisolte; il limite è intenzionale.

**Il modello in B mantiene otto hold. È il verificatore del motivo a registrarli
come `REJECTED_REDUNDANT_ROLE_CONFIRMATION`, consentendo di proseguire con i
normali controlli di esportazione.** Nessuna promozione di fatti a RESOLVED,
nessun UNKNOWN trasformato in TRUE, nessuna nuova decisione USER.

## Replay offline e DOCX fisico

Database e storage clonati; rete e trasporti HTTP vietati nel replay. Le
transizioni attraversano la persistenza, i verificatori e l'export esistenti.

| Percorso | Testi SOURCE | Checkbox USER | Scritture totali | Hold tecnici finali | Precedenti persi/cambiati |
|---|---:|---:|---:|---:|---:|
| Riproduzione storica, stesse tre richieste e risposte | 52 | 1 | 53 | 8 | 0 |
| Codice attuale, sole risposte storiche senza motivi | 52 | 1 | 53 | 8 | 0 |
| Rivalutazione offline con risposta reale B motivata | 60 | 1 | **61** | 0 | 0 |
| Controllo negativo simulato: requisito SOURCE ancora da provare | 52 | 1 | 53 | 8 | 0 |

Il primo replay riproduce esattamente le tre richieste LLM originali con il
codice conservato all'inizio dell'intervento. Il secondo prova che osservabilità
e nuova versione non cancellano sospensioni prive di motivi. La rivalutazione
riparte da una copia del checkpoint originale dopo USER, senza rispondere a
nuove domande. I dati, condizioni, prove e ricevute esposti coincidono con B;
nel percorso reale `narrate` aggiunge anche i metadati preesistenti
`source_availability`, assenti nella chiamata mirata B. Questa differenza è
salvata nel confronto: non si dichiara l'intero input byte-identico a B.

Il controllo negativo cambia esplicitamente il motivo in un ostacolo SOURCE:
è un test software simulato, non una nuova risposta del provider. Tutte le otto
sospensioni vengono mantenute. Audit SOURCE e ricevute USER restano uguali
all'originale in tutti i replay. Restano24 campi dei soci,52 testi preesistenti,
una sola casella `p39.cb0`, zero deselezioni o altre nuove checkbox.

| Campo originale | Valore recuperato nel DOCX |
|---|---|
| p51.s0 — nominativo | Elisa Romano |
| p52.s0 — qualifica | ingegnere |
| p52.s1 — codice fiscale | RMNLSI85C47A662Y |
| p53.s0 — Ordine | Ordine degli Ingegneri di Bari |
| p53.s1 — sezione | A |
| p53.s2 — provincia Ordine | Bari (BA) |
| p53.s3 — data iscrizione | 18/05/2015 |
| p53.s4 — numero iscrizione | 8421 |

Verificati CRC, parsing XML/rels, posizioni, valori fisici rispetto al report,
prestampato, quattro tabelle e tredici controlli nativi. Una sola modifica a
una checkbox; le altre dodici restano intatte. Gli otto nuovi valori sono
conformi al GOLD congelato; zero nuove accettazioni indebite osservate.
Su60 testi,59 risultano conformi al confronto GOLD: resta la differenza già
nota nella carica completa del firmatario, attestata dalle SOURCE.

Il DOCX61 coincide byte per byte con il precedente replay61:
`84e33e53477f0bb4935eaa9667ed02c6eea6d010beb091cab4f650a1b87feddd`.
Storico, soli vecchi motivi assenti e controllo negativo coincidono con il
DOCX originale UI53:
`4ff926e9d644b2a879a26aebca8e0d42db253fe941bc1e9e2f725c16b3058479`.
Il PDF precedente viene riusato soltanto dopo questa uguaglianza binaria:
9pagine, medesima impaginazione. Non è una nuova certificazione con Word desktop;
restano le giunzioni di etichette del writer già documentate.

Restano aperti i cinque gruppi USER: preferenze, attestazioni, esecutori,
integrazione e luogo/data. Quattro campi di testo attesi dallo scenario restano
vuoti (`p229.s0`, `p230.s0`, `p232.s0`, `p242.s0`). Nessuna nuova designazione,
firma, attestazione o scelta viene dedotta per completare il documento.

## Verifiche, conservazione e limiti

26 nuovi casi di test, di cui18 casi parametrizzati che impediscono il rilascio
per requisiti non risolti o non pertinenti. Coprono condizioni UNKNOWN, prove
composte assenti, persona diversa, rifiuti, rinvii, dichiarazioni, motivi
precedenti, ambiti discordanti e informazioni mancanti differenti. Ulteriori
test verificano distinzione delle transizioni, citazioni, vecchi output e
impossibilità di eliminare un hold omettendolo dalla risposta.
210 test mirati passati in22,61s; suite completa **2.627 test passati in186,99s**,
Ruff passato. Dettagli e log nei controlli allegati.

Preservati gli esiti negativi: passaggio del solo contesto insufficiente,
aspettativa del vecchio test di schema da aggiornare, due nuovi test negativi
prima della protezione di ambito/motivo precedente e due avvii del replay
fermati prima della valutazione da un confronto input troppo restrittivo
(`source_availability` aggiunto dal percorso reale). Nessun retry del modello
per ottenere un risultato migliore. Un avvio della verifica indipendente con
percorso relativo errato non ha eseguito la verifica; la successiva è riuscita.

Il bundle consente di ricostruire audit, selezioni e tutti e quattro i DOCX
senza database privati, chiavi o rete, usando il codice archiviato. Comprende
richieste/risposte reali, transizioni, codice prima/dopo, test e log. Raw in
`backend/data/compilation-audit/v12-narrator-holds-20261019-01/`; backup separato
in `docs/benchmarks/2026-10-19-v12-narrator-holds-audit.tar.gz`.

Nessuna migrazione o modifica delle vecchie sessioni. La versione del narratore
è aggiornata per una ripresa esplicita; un export già terminato non viene
riaperto automaticamente. Il recupero61 è dimostrato offline con la risposta
motivata B, non ancora da una nuova UI reale con il contratto finale.
Arresto al termine di questo intervento, senza avvio di ulteriori esperimenti.
