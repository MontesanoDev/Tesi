# Compilatore globale su tre bandi reali — 12 ottobre 2026

**Il prototipo recupera dati utili, ma non è ancora affidabile per compilare
automaticamente un documento completo.** Anche rimandando checkbox e ordine
professionale, rimangono assegnazioni a posizioni sbagliate, omissioni variabili,
applicabilità incompleta e falsi negativi del binding persona/ruolo.

Richiesta: provare tutti e tre i bandi senza ottimizzare prima costo o token.
Dodici chiamate reali deepseek-flash: nove prove pianificate, tre per bando,
più un controllo seriale per bando dopo due timeout. Nessuna risposta fallita
è stata sostituita o esclusa. Nessun provider simulato nelle acquisizioni.

## Protocollo e perimetro

Codice congelato `6a33c852e14bf3b7d8d23008ac0b35a6de3d6b1a`, contratto V8,
catalogo V3, thinking low predefinito, temperatura 0,1, massimo 49.152 token
di output e 300 secondi per chiamata. Una chiamata per prova, zero retry
automatici, zero valori USER, zero sessioni e zero scritture DOCX.
Motore, prompt, schema e validator non modificati durante o dopo il benchmark.

| Bando | Originale usato | Candidate testuali | Checkbox | Totale |
|---|---|---:|---:|---:|
| Catanzaro DL/CSE | DOCX convertito già presente in `modello/domanda-partecipazione.docx` | 279 | 28 | 307 |
| Minervino di Lecce | `originali/domanda-iscrizione.docx` | 254 | 13 | 267 |
| Trapani Green | `originali/manifestazione-interesse.docx` | 115 | 0 | 115 |

I percorsi sono sotto `demo-documents/bandi/`. Nessuna conversione aggiuntiva
o modifica degli originali. Hash SHA-256 nel protocollo e nel JSON allegato.

Stesso corpus autorizzato del workspace `prova`, congelato prima delle chiamate:
17 chunk SOURCE globali, 13 Company e quattro General, da `generalita-mapi.md`,
`visura-mapi-ingegneria-simulata.pdf` e `progettazione-opere-pubbliche.txt`.
Nessuna fonte di altri progetti, nessun artefatto generato come prova fattuale.
Questo esperimento usa il corpus piccolo completo, non una ricerca FTS/Qdrant:
non misura il retrieval della chat V1. Ruolo, scope, categoria e riferimenti
documento/chunk restano nell'audit.

I DOCX sono caricati in pacchetti isolati del runner con un `manual-only.json`
vuoto, escluso dal prompt. **Non esiste un gold per questi tre confronti**:
il `fixture-score.json` prodotto dal runner non è usato come misura di qualità.
Le istruzioni demo e la vecchia mappa campi non sono inviate all'AI come fatti
o scelte dell'utente. La matrice di ispezione è stata scritta dopo il primo
risultato Minervino: non viene presentata come gold preregistrato o accuratezza.

Le prime nove chiamate sono organizzate in tre giri, con massimo tre richieste
concorrenti. Dopo la chiusura della serie è registrato un protocollo separato:
Catanzaro, Minervino, Trapani, una richiesta alla volta. Stessi body e timeout,
nessuna riparazione di output o cambio del compilatore. I quattro body per
ciascun documento sono byte per byte identici.

## Tutti i risultati

«Grounded» significa che la proposta supera i controlli locali FORM/SOURCE,
non che destinazione, soggetto e applicabilità siano semanticamente approvati.
Tutte le 91 ipotesi conservate sono **conditional / REVIEW_REQUIRED**;
`value` e `written_value` restano null. Zero RESOLVED.

| Bando | Prova | Esito | Assegnazioni raw | Conditional grounded | Omesse | Secondi chiamata | Token osservati |
|---|---|---|---:|---:|---:|---:|---:|
| Catanzaro | 1, concorrente | Timeout | — | — | — | 300,13 | non acquisiti |
| Catanzaro | 2, concorrente | Audit eseguito | 15 | 11 | 292 | 124,90 | 93.870 |
| Catanzaro | 3, concorrente | Audit eseguito | 14 | 10 | 293 | 81,15 | 84.127 |
| Catanzaro | 4, seriale | Audit eseguito | 14 | 9 | 293 | 106,96 | 89.097 |
| Minervino | 1, concorrente | Audit eseguito | 4 | 4 | 263 | 39,74 | 47.027 |
| Minervino | 2, concorrente | Audit eseguito | 8 | 8 | 259 | 63,43 | 54.608 |
| Minervino | 3, concorrente | Audit eseguito | 7 | 7 | 260 | 50,01 | 50.579 |
| Minervino | 4, seriale | Audit eseguito | 21 | 16 | 246 | 109,99 | 62.753 |
| Trapani | 1, concorrente | Timeout | — | — | — | 300,10 | non acquisiti |
| Trapani | 2, concorrente | Audit eseguito | 9 | 9 | 106 | 57,87 | 39.308 |
| Trapani | 3, concorrente | Audit eseguito | 9 | 9 | 106 | 62,08 | 39.727 |
| Trapani | 4, seriale | Audit eseguito | 8 | 8 | 107 | 52,62 | 36.823 |

Dodici tentativi, dieci output completi con finish reason `stop`, due TimeoutError.
Nei timeout non sono stati acquisiti output o usage completi: non equivalgono
a JSON vuoto, zero token fatturati o valori rifiutati dal validator.
Il callback ha contato una risposta per ciascun timeout, ma non ne ha salvato
il corpo completo o lo status: non attribuiamo una causa certa a server/rete.

**597.919 token osservati**, più l'eventuale consumo non acquisito dei due timeout.
Attesa cumulata delle chiamate 1.348,98 s, inclusi 600,23 s dei timeout; le dieci
risposte complete totalizzano 748,75 s. Sono somme di tempi per chiamata, non
durata E2E: alcune richieste erano concorrenti. Nessuna misura monetaria completa
o risparmio dimostrato. Cache, ordine e condizioni del servizio possono incidere.
Tre controlli seriali senza timeout non dimostrano che la concorrenza fosse
l'unica causa dei due fallimenti precedenti.

## Catanzaro: dati societari ripetibili, direttore bloccato

I cinque dati seguenti sono conservati nelle **tre risposte complete su quattro
tentativi**, senza valori USER. Sono ipotesi SOURCE, ancora da autorizzare per
applicabilità/partecipante: non stati RESOLVED della CompilationSession.

| Candidate | Requisito | Valore SOURCE proposto |
|---|---|---|
| `t0.r5.c1` | Operatore economico | Mapi Ingegneria S.r.l. |
| `t0.r6.c1` | Forma giuridica | Societa a responsabilita limitata |
| `t0.r7.c1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia |
| `t0.r9.c1` | Codice fiscale operatore | IT01234567890 |
| `t0.r10.c1` | Partita IVA operatore | IT01234567890 |

Le prove conservano anche denominazione, forma e sede nel ramo 5.d. I riferimenti
effettivi sono Company KB, visura/scheda aziendale; chunk e quote per ogni
valore nel JSON. Identificativi demo preservati, non certificati come validi.

Quattro valori del direttore — Elisa Romano, Ingegnere, Ordine degli Ingegneri
di Bari, 8421 — vengono proposti ma bloccati in tutte le tre risposte complete.
Nelle prove 2/3 il binding FORM/SOURCE è grounded, ma `_asserted_role` richiede
una coppia letterale `ruolo: soggetto` nella SOURCE e nello stesso chunk del
valore. La scheda usa titolo persona più elenco di attributi; la visura usa
`DIRETTORE TECNICO Ing. Elisa Romano`, senza quel formato. Il controllo fallisce,
anche se il lettore umano può ricostruire la relazione. Non è mancato retrieval.
Nella prova seriale la quote del binding salta righe intermedie della scheda:
non è un estratto contiguo, quindi il rifiuto della quote è corretto. Il test
evidenzia sia conservatività del gate sia una proposta di supporto invalida.

Altri limiti: nelle prove 2/3 la sede operativa è proposta con la condizione
generica di partecipazione, senza la clausola locale «se diversa dalla sede
legale», benché le SOURCE dicano che coincide. Nella prova 4 viene proposta NA,
ma senza una condizione calcolabile falsa e viene rifiutata. Nessuno di questi
esiti deve essere materializzato. «Cellulare + Telefono» riceve il solo telefono:
non abbiamo dimostrato disponibilità del cellulare. Un checkbox di tipologia
compare solo nella prova 2; il perfezionamento dei checkbox resta rimandato.

## Minervino: copertura instabile e tre destinazioni sbagliate

Le prime tre prove conservano rispettivamente quattro, otto e sette ipotesi,
con insiemi diversi. La quarta conserva sedici: maggiore copertura osservata,
non effetto causale dimostrato dell'esecuzione seriale. Nessun prompt è cambiato.

La prova 2 ha un errore concreto **prima del renderer**. Nel paragrafo 42 ci
sono sei slot separati per provincia, via, civico, telefono, e-mail e PEC.
Il modello fonde via/civico e sposta le assegnazioni successive:

| Candidate | Destinazione reale nell'originale | Valore proposto | Giudizio manuale |
|---|---|---|---|
| `p42.s1` | Via/piazza | Via Giovanni Amendola 172/C | Granularità: civico dovrebbe restare distinto |
| `p42.s2` | Numero civico | +39 080 000 2040 | Destinazione sbagliata |
| `p42.s3` | Telefono | segreteria@mapi-ingegneria.demo | Destinazione sbagliata |
| `p42.s4` | E-mail ordinaria | mapi.ingegneria@pec.demo | Destinazione sbagliata; PEC ha uno slot distinto |
| `p42.s5` | PEC | nessuna proposta | Omesso |

I valori sono nelle SOURCE e tutte e quattro le proposte superano il grounding
locale. Il catalogo contiene i range corretti, ma la quote FORM viene verificata
nel paragrafo locale, non ancorata alla singola porzione associata allo slot.
Il modello può citare «tel» dello stesso paragrafo per la posizione del civico.
Confrontare `property` del field con `property` del fatto non rileva il problema:
entrambe sono proposte dal modello. Questa è una lacuna concreta di destinazione:
i range del parser sono corretti e il renderer non è stato eseguito.

La prova 4 separa correttamente civico e recapiti; conserva però l'indirizzo
completo in `p41.s1` oltre ai componenti successivi: granularità ancora da
rivedere. Propone cinque dati del direttore ma nessuno supera il binding.
Per `p51.s0` manca la coppia letterale persona/ruolo richiesta dal gate.
Per `p52.s0`, `p53.s0`, `p53.s2`, `p53.s4` il ruolo è citato nel paragrafo 50,
ma `_role_contexts` ammette solo l'ultimo paragrafo precedente, oltre al contesto
locale e all'ultima sezione esplicita. Il ruolo non viene ereditato lungo il
gruppo di paragrafi. Le SOURCE sono presenti; non sono valori da chiedere
all'utente come se fossero assenti.

## Trapani: otto dati ripetuti, ancora condizionati

Le tre risposte complete conservano gli stessi otto dati nel ramo società di
ingegneria: denominazione, via/civico, comune, CAP, provincia, PIVA, telefono,
PEC (`p75.s0`–`p75.s6` e `p75.s8`). I valori e le destinazioni sono coerenti
con le SOURCE. Le prime due risposte aggiungono PEC comunicazioni `p107.s0`,
la seriale la omette. Anche questa PEC non prova il consenso alla sua scelta.

CF personale, firmatario, fax, numeri di albi del dichiarante/paesaggista/agronomo
e firma restano senza proposta. Il numero 8421 del direttore non viene copiato
in quei campi. È il caso più ripetibile per i dati osservati, ma ha comunque
un timeout su quattro tentativi e nessuna applicabilità approvata o DOCX generato.

## Giudizio e prossimo passo

Esaminati tutti i **109 record emessi**: 91 ipotesi con grounding locale,
17 proposte personali bloccate dal binding e una NA rifiutata. Tre record
con destinazione errata, due con granularità da rivedere e due con clausola
di applicabilità incompleta sono conservati esplicitamente nell'audit manuale.
Le categorie non trasformano il grounding in accuratezza semantica.

Nelle proposte esaminate non abbiamo trovato un valore fattuale inventato
senza SOURCE; questo non dimostra sicurezza semantica generale. I controlli
negativi selezionati restano senza assegnazioni nelle risposte disponibili.
Le omissioni non sono automaticamente MISSING, decorative o NOT_APPLICABLE.
I 689 candidate dei tre documenti non sono 689 campi obbligatori.

**Affidabilità insufficiente per compilazione completa automatica.** Il recupero
dei dati societari è promettente e misurabile, ma il problema delle destinazioni
esiste anche ignorando checkbox e ordine professionale. Prima di attivare
l'adapter verso sessione/Word va discusso un passo circoscritto su ancore locali
degli slot, eredità del ruolo e condizioni. Non è stato implementato in questa
esecuzione, né allentato il controllo SOURCE per far passare il test.

## Verifiche e integrità

Eseguiti ora: **314 test software mirati / 14,42 s**, Ruff backend, controllo
fixture Labirinto congelata, otto verifiche della fixture Catanzaro / 0,583 s,
manifest di tutte le dodici acquisizioni, dieci replay esatti del validator,
confronto dei dieci file di codice per acquisizione con il commit congelato,
identità dei body/fonti, finish reason e originali, diff e archivio.
Suite backend completa e frontend non ripetuti: nessun codice applicativo
o contratto cambiato. I test software non misurano la semantica DeepSeek.
Conservata anche una failure di lint esplicito dei soli helper di acquisizione
ignorati da Git (righe lunghe/ordine import); non riguarda il backend applicativo.

**Nota di integrità locale:** il fingerprint dell'intero DB non è invariato.
Cambiano chunk derivati di progetto, FTS e sequenze; progetti, file, sessioni,
revisioni, conversazioni/turni, profili AI, documenti e chunk Company/General
restano invariati, come gli originali. Il server di sviluppo `uvicorn --reload`
era attivo ed è stato osservato il riavvio del worker mentre venivano creati
helper `.py` nel backend. Lo startup ricostruisce FTS e indicizza gli artefatti:
riscontro coerente con questi cambiamenti, senza traccia SQL del writer per
un'attribuzione esclusiva. Nessun ripristino o modifica manuale del DB; il
corpus sperimentale era già congelato e resta identico. In futuro conservare
gli helper fuori dal percorso sorvegliato o usare un'istanza isolata.

## Acquisizioni salvate

- [JSON completo](benchmarks/2026-10-12-tre-bandi.json): cataloghi, tutti i candidate,
  raw strutturati, fatti/condizioni/binding, evidenze, validazioni, metriche e
  annotazioni manuali, inclusi i timeout e le informazioni non acquisite.
- [Bundle grezzo](benchmarks/2026-10-12-tre-bandi-audit.tar.gz) e
  [checksum](benchmarks/2026-10-12-tre-bandi-audit.tar.gz.sha256): protocolli,
  input, copie originali, snapshot codice, prompt/schema/body, risposte HTTP
  complete quando ricevute, output, usage, audit, replay e controlli.
  Niente DB, configurazione privata o chiave API.
  Archivio: **333 file / 3.395.750 byte**, verificati byte per byte; SHA-256
  `70df9a7b8bd489383d62469aa7a61769e322ffc7135d5ab4939d7eb5e07f5d69`.
- Grezzi locali `backend/data/compilation-audit/tre-bandi-20261011/`;
  il bundle versionato conserva i risultati anche senza questa directory ignorata.
- [Registro](../relazioni.md) e [stato corrente](../STATUS.md).
- [Verifiche finali dell'archivio e dei riferimenti](benchmarks/2026-10-12-tre-bandi-final-checks.json),
  incluse le informazioni non acquisite e una failure iniziale del checker
  documentale, corretto senza cambiare motore o risultati.

Nessuna CompilationSession creata, nessun DOCX generato, nessun cambio
a V1/chat/RAG/parser/renderer/UI. Commit dei risultati, nessun push.
