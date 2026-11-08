# B0-03: DOCX parziale esportato e verificato

17 ottobre 2026. Eseguito il piano operativo sulla **copia isolata della stessa
sessione B0-03**. Il risultato è un documento reale:

- [Word parziale](<../nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.docx>).
- [PDF controllato](<../nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.pdf>).
- [Report originale dell'export](<../nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.report.json>).
- [Misure](benchmarks/2026-10-17-b0-docx-verified.json),
  [controlli](benchmarks/2026-10-17-b0-docx-verified-checks.json),
  [backup](benchmarks/2026-10-17-b0-docx-verified-audit.tar.gz).

**48 valori effettivamente scritti e verificati: 47 SOURCE e un nome USER.**
Nessuna nuova chiamata LLM, risposta USER inventata o checkbox modificata.
La fase ha usato l'export esistente, senza modifiche al codice applicativo,
al writer, al FORM B0 o alle sessioni originali. Nessun commit o push.

## Numeri misurati, con denominatori distinti

| Misura | Esito |
| --- | ---: |
| Assegnazioni SOURCE con valore nell'output B0-03 | 50 |
| Proposte SOURCE grounded nell'audit attuale | 47 |
| Assegnazioni SOURCE respinte | 3 |
| Vecchie proposte revisionate ancora valide | 21 |
| Proposte pendenti riesaminate in questa fase | 26 |
| SOURCE revisionate, approvate e applicabili nello scenario | 47 |
| Valore USER della stessa sessione rivalidato | 1 |
| Valori presenti nel report **e nel DOCX fisico** | **48** |
| Valori scritti non conformi al gold sintetico | 0 su 48 |
| Condizioni UNKNOWN nell'audit, conservate | 1 (`c_p39`) |
| Proposte SOURCE ancora conditional nell'audit | 47 |
| Condizioni confermate nel registro USER originale | 1 (`c_p39`) |
| SOURCE selezionate con condizioni prive di conferma USER | 0 |
| Checkbox native modificate | 0 su 13 |

UNKNOWN nell'audit e conferma USER per l'export sono informazioni distinte.
Non sono stati dichiarati TRUE i risultati dell'audit. I 219 candidati non
riempiti su 267 non sono tutti errori o UNKNOWN: comprendono rami alternativi,
campi da lasciare vuoti, scelte non acquisite e omissioni/rifiuti.

Il precedente DOCX B0-03 aveva 23 valori: 22 SOURCE e un nome USER. Di quei
23, 22 coincidevano con i target testuali del gold; il Comune conteneva
erroneamente l'indirizzo completo. Ora sono presenti gli stessi 22 valori
conformi, **26 inserimenti aggiuntivi** e il Comune errato è vuoto:
23 − 1 + 26 = 48. Sui 60 target testuali SOURCE del gold si passa da 22 a
48 corrispondenze, delle quali 47 con provenienza SOURCE e una USER.

È un miglioramento misurato del documento con revisione assistita, sullo
stesso output globale: non è una nuova misura della qualità autonoma del
modello, del narratore o di una nuova generazione.

## Ricevute, audit e isolamento

Sessione storica: `ee86e66383ac4e5d9df90cf2b3ea3454`, versione 9. Il database
del runtime B0-03 è stato aperto in sola lettura per crearne una copia in
`.tools/b0-docx-verified-20261017-01/export-01/`. Quel database contiene una
copia della sessione con lo stesso ID: non una modifica alla sessione storica.
È stato verificato che lo stato iniziale coincideva con il checkpoint archiviato.

Il catalogo completo, le 56 SOURCE e l'output globale sono invariati rispetto
al B0 congelato. L'audit è stato ricalcolato con i verificatori attuali e
riproduce esattamente `binding-final-20261017-01/b0-03/final-validation.json`.
L'audit storico resta separato e integro; le condizioni del nuovo audit sono
identiche a quelle storiche. Il report dell'export conserva integralmente
il nuovo audit, senza aggiustamenti manuali ai suoi esiti.

Riutilizzate soltanto le ricevute della stessa sessione:

- `condition:c_p39`: «Mapi Ingegneria S.r.l. partecipa soltanto come società
  di ingegneria», con domanda sul legale rappresentante della società.
- `field:p12.s0`: Leonardo Montemurro, con quote nominativa sul firmatario.
- Il messaggio storico di consenso all'export parziale, con firma e irrisolti
  da lasciare vuoti. La richiesta corrente autorizza questa riproduzione isolata.

Le quote sono state confrontate con la cronologia effettiva, non soltanto
con il copione del benchmark. Risposte, `user_values` e citazioni sono
identiche prima e dopo l'export. Nessuna ricevuta di INDEX o altra sessione.

## Applicabilità verificata separatamente

| Dimensione | Verifica effettuata | Conseguenza limitata allo scenario |
| --- | --- | --- |
| Operatore | T0 della stessa sessione identifica Mapi; SOURCE ne documenta i dati | I nove dati generali appartengono all'operatore scelto |
| Natura giuridica | SOURCE `-43`: S.r.l. | Non deduce modalità di partecipazione o poteri |
| Attività | SOURCE `-43`: società di ingegneria civile | Descrizione aziendale, senza certificare requisiti normativi |
| Partecipazione della pratica | Ricevuta USER specifica società di ingegneria | Ramo societario; nessuna attribuzione di mandati RTP o altre modalità |
| Firmatario | Ricevuta USER sceglie Leonardo | Il nome viene riusato solo in `p12.s0` |
| Rappresentanza | SOURCE `-53` attesta Leonardo rappresentante dal 2 ottobre; Luca cessa il 1 ottobre; riferimento USER 15 ottobre | Ruolo attuale documentato, nessuna procura o potere speciale aggiunto |
| Direttore tecnico | p50 distingue società di professionisti/ingegneria; SOURCE `-45/-55` attesta Elisa direttore tecnico | Si usa la sottoalternativa ingegneria, senza designazioni per incarichi |
| Soci | p42 chiede i dati di ogni socio; tabella `-54` | Nessuna scelta USER aggiuntiva su quali soci includere |

**Ambito di `c_p39`: limite conservato, non nascosto.** Il FORM p14–p17 non
subordina letteralmente i nove dati generali al ramo p39. La revisione ne
attesta l'applicabilità sulla base dell'operatore identificato nel T0.
Il collegamento aggiunto dal modello resta nell'audit originale. L'API
esistente, senza conferma di `c_p39`, continua a rifiutare anche quei nove
campi: verificato con `_selected`, risposta 409, senza invocare il writer.
Non è quindi stata implementata la loro indipendenza tecnica dal ramo.
In questo caso la ricevuta p39 esiste, è pertinente ed è stata verificata
insieme a identità, ruolo e sottoalternativa; il vincolo conservativo può
essere soddisfatto senza inventare una condizione o rimuoverne una.

## Revisione delle proposte ed export reale

Le 26 pendenti sono 23 dati dei soci e tre del direttore tecnico: CF,
sezione e data d'iscrizione. Riesaminati anche i 21 dati già revisionati
ancora validi. Ogni approvazione ha una motivazione specifica in
`manual-review.tsv` e un record completo in `completed-review.json`, con
valore, posizione, FORM, SOURCE, binding e risultato del validatore esistente.
Non è stato usato il gold per scegliere o correggere i valori.

Per i soci sono state controllate intestazioni/riga/soggetto e ogni colonna;
per Elisa socio/direttore sono rimaste distinte identità, ruolo e valore,
con ordine e numero condivisi nel collegamento del CF. Titoli e date restano
nel formato proposto. Nessun CF o provincia trasferiti per sola somiglianza
del nome. Tutti i 47 valori SOURCE e il nome USER superano i controlli esistenti.

La nuova revisione è stata effettuata manualmente da Codex su istruzione
dell'utente e registrata nella sola copia. **Non è una nuova risposta USER
storica né una revisione semantica indipendente ottenuta da un altro LLM.**
Il report standard usa `reviewed_by=USER`: l'autore e il metodo effettivi di
questa revisione sono esplicitati nel registro aggiuntivo e nelle revisioni
della copia, senza riscrivere il report standard.

Usati `export_selection`, `GlobalDraftRequest` e `generate_draft` esistenti,
con rilettura SOURCE e rivalidazione atomica prima della persistenza. Il
servizio ha scritto 48 valori, in circa 0,725 secondi per il solo export
locale; il tempo non comprende revisione, rendering o interazione umana.

I tre rifiuti restano `p41.s1` (indirizzo nel Comune), `p46.s0` e `p53.s2`
(provincia non dimostrata nella citazione proposta). Tentativi read-only di
selezionarli sono stati respinti 422. Nessun gruppo checkbox è disponibile:
tutti i 13 controlli originali restano invariati, compreso p39.

## Verifica del risultato

- ZIP/CRC validi, stesse parti e 12 relazioni interne risolte. Solo
  `word/document.xml` cambia; tutte le altre parti sono identiche byte per byte.
- Estrazione indipendente dei 48 valori nei rispettivi slot: coincidenza
  esatta con selezione e report. Tutti gli altri segnaposti sono invariati.
- 246 paragrafi originali conservati, più il solo avviso standard del writer;
  quattro tabelle, proprietà dei paragrafi, numerazione e 13 controlli preservati.
- Firma vuota, nessuna frase diagnostica nelle aree compilabili. L'avviso
  standard «BOZZA NON VERIFICATA» resta: il writer non è stato modificato e
  la pratica resta incompleta, pur essendo verificati i contenuti inseriti.
- Gold aperto soltanto dopo export e controllo fisico: 48/48 valori conformi
  con le equivalenze congelate per titoli/date; nessun valore indebito rilevato.
- Rendering con lo stesso LibreOffice locale di originale e bozza: 10 e
  9 pagine. Controllate visivamente tutte le nove pagine della bozza e le
  pagine originali 3, 4, 9 e 10. Valori presenti anche nel testo PDF; nessuna
  parola fuori pagina nel controllo geometrico. Firma ed etichetta insieme
  a pagina 9; lettere a), b), c), d) conservate.

**Limite visivo effettivo:** cinque giunzioni senza spazio su quattro
paragrafi, nei campi `p43.s3`, `p45.s3`, `p49.s0`, `p53.s0`, `p53.s1`:
«professionaleOrdine» e «Adella». I valori restano leggibili e nei campi
corretti, ma la presentazione richiede una futura correzione separata.
La causa è il segnaposto originale adiacente all'etichetta e la sostituzione
del writer esistente senza separatore. Nessun ritocco diretto al DOCX.
Il numero 3) del direttore è già presente nel modello e resta tale.
Non è stata verificata la paginazione con Microsoft Word.

Restano vuoti 12 target testuali SOURCE del gold: otto dati del firmatario,
due Comuni e due province; nove sono omissioni e tre i rifiuti conservati.
Restano separate preferenze, attestazioni, designazioni e luogo/data non
effettivamente acquisiti. Stato del servizio: `needs_review`, con
`ready_for_submission=false`. Non è un documento pronto alla presentazione.

## Riproducibilità e controlli dell'intervento

Raw: `backend/data/compilation-audit/b0-docx-verified-20261017-01/`.
Conservati originale, input/output globale, audit vecchio e attuale, ricevute,
decisioni manuali, richieste, revisioni della copia, DOCX/report, PDF/PNG,
estrazione fisica, misure e log. Il database privato non viene pubblicato;
per rieseguire i servizi lo script richiede il seed storico indicato in
`setup.json`. Gli artefatti materiali e le verifiche sono nel backup pubblico.

Conservati anche i controlli preliminari falliti: il primo confronto usava
i metadati DB grezzi al posto della proiezione canonica; il confronto canonico
è esatto. L'estrattore di verifica iniziale non contava i marcatori Word di
pagina memorizzati negli offset; corretto solo lo script di verifica. Nessuno
di questi passaggi ha modificato SOURCE, risposta globale, writer o DOCX.

Nessuna suite completa o Ruff rieseguiti: codice applicativo invariato.
Verificati i guard reali, il percorso di export e il documento prodotto.
Integrità finale: **11.455/11.455 file protetti invariati**, inclusi database
live, upload e runtime storici; nessun nuovo file applicativo o di test.
Stato e versione della sessione originale ricontrollati sul database storico.
SHA-256 DOCX:
`6605dcc91ab823cc21d77618c2991feade366cce1137d4b8138600f1c051a889`.
