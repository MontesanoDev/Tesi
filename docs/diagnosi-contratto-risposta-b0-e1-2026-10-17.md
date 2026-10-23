# Diagnosi offline delle risposte B0, E1 e indice diretto — 17 ottobre 2026

**Decisione dell'utente recepita:** fermati gli esperimenti di compattazione del
FORM. B0 resta il riferimento; compact-v1 e compact-index-v2 non vanno integrate.
Questa attività legge nove acquisizioni già salvate. **Zero nuove chiamate LLM,
nessuna modifica a codice, prompt, validatori, writer o fixture; nessun commit.**

Il punto principale è che i dati SOURCE mancanti nel risultato erano presenti
nell'input. I limiti osservati riguardano anche emissione delle proposte,
collegamento dei ruoli, citazioni e contratto di risposta. Il 78,35% dei token di
output è reasoning. Non emerge un catalogo di fatti duplicati da eliminare.

[Misure complete](benchmarks/2026-10-17-output-diagnosis.json),
[bundle dei derivati](benchmarks/2026-10-17-output-diagnosis-audit.tar.gz),
[checksum](benchmarks/2026-10-17-output-diagnosis-audit.tar.gz.sha256),
[verifiche](benchmarks/2026-10-17-output-diagnosis-checks.json).
Raw: `backend/data/compilation-audit/diagnosi-output-b0-e1-20261017-01/`.
Archivio dei derivati: 18 file, 99.771 byte, SHA-256
`080bb3190e05e1c7b68a36e40a5a37056683af42b99074dfd1b06c6f1380ec65`.

Gli originali restano nei bundle [B0](benchmarks/2026-10-16-minervino-b0-audit.tar.gz),
[E1](benchmarks/2026-10-16-e1-form-audit.tar.gz) e
[indice diretto](benchmarks/2026-10-17-e1-index-audit.tar.gz).

## Metodo e significato dei conteggi

Analizzati request.json, input.json, http-response.txt, metrics.json e, dove
esistono, response.txt, validation.json e gold-comparison.json di ogni analisi.
Verificato che il messaggio USER effettivamente inviato coincide col rispettivo
input salvato. Le nove liste SOURCE e i nove reading plan sono identici.

I token sono quelli del provider, senza nuova tokenizzazione o stima monetaria.
La quota non reasoning è calcolata per differenza. Le dimensioni delle sezioni
JSON sono in **caratteri Unicode**, non token; non esiste una ripartizione
provider per sezione. Gli otto JSON completi sono già minificati.

«Valore corretto» significa conforme al valore autoriale congelato e alle sue
equivalenze dichiarate. Non significa che citazione, ruolo o applicabilità della
proposta siano tutti dimostrati. I rifiuti locali sono conteggiati soltanto dove
esiste un audit reale: sette analisi. Il rifiuto dell'intero envelope e il JSON
tronco rimangono casi separati. Nessuna risposta è stata riparata o rivalidata
con regole diverse per trasformare un fallimento in successo.

## 1. Perché INDEX-01 e INDEX-02 non arrivano al DOCX

| Passaggio | INDEX-01 | INDEX-02 |
|---|---|---|
| HTTP | 200 | 200 |
| finish_reason del provider | stop | length |
| Durata AI / timeout configurato | 173,44 / 300 s | 214,62 / 300 s |
| Testo restituito | JSON completo, sintassi valida | JSON troncato |
| Arresto effettivo | Validazione dell'envelope Pydantic | GenerationTruncatedError nel trasporto |
| Audit dei singoli campi | Non eseguito | Non eseguito |
| Sessione/Word/writer | Nessun tentativo | Nessun tentativo |

**INDEX-01 — rifiuto del contratto, non timeout o JSON sintatticamente invalido.**
La risposta contiene due chiavi root vietate: `proposal_stage` e `project_id`.
`_validate_sparse_proposal` svuota temporaneamente le mappe di record per
validare l'envelope, conservando le altre chiavi: `CoverageAwareProposal`
respinge le due proprietà extra. La quarantena degli errori dei singoli campi
non si applica agli errori globali dell'envelope.

I due nomi e i loro valori coincidono con metadati presenti nell'input. Questa
corrispondenza è osservata; che il modello li abbia copiati perché confuso dal
formato è un'ipotesi. Tutte le richieste usano `response_format=json_object`:
questa configurazione chiede JSON, mentre lo schema di dominio è fornito nei
messaggi e verificato localmente. Gli artefatti non mostrano un vincolo provider
che imponga l'esatto schema Pydantic.

Il confronto grezzo trova 25 valori conformi su 27 proposti. **Sono 25 valori
persi per rifiuto globale**, non 25 rifiuti dei validatori di campo. Gli altri
due sono indirizzi completi nei campi che richiedono il solo comune.

**INDEX-02 — esaurimento del budget output, non timeout.** Il provider riporta
49.152 completion token, esattamente il limite richiesto: 44.316 reasoning e
4.836 non reasoning. `request_model_content` rileva `finish_reason=length` e
solleva l'errore prima del parsing/validazione della proposta.

Il contenuto visibile, 16.153 caratteri, termina dentro una stringa del fatto
`f_fax`: `Unterminated string ... char 16150`. È presente anche reasoning per
148.894 caratteri. L'output si interrompe nella mappa `facts`, prima di
`clarifications` e `coverage`. Quindi non è dimostrato che i byte di coverage
abbiano causato questo troncamento: non erano ancora stati emessi. Il possibile
peso della pianificazione di tutti gli esiti sul reasoning rimane un'ipotesi.

In entrambi i casi il DOCX non manca per un difetto del writer. Il writer non
viene raggiunto. Nessun retry, rimozione di chiavi extra, completamento del JSON
o aumento del budget è stato eseguito in questa diagnosi.

## 2. Output generato, ridondanza e informazioni usate dal backend

### Token reali delle nove chiamate globali

Sono escluse le successive chiamate del narratore/router: qui si diagnostica
il contratto della singola analisi globale.

| Run | Output totale | Reasoning | Non reasoning, per differenza |
|---|---:|---:|---:|
| B0-01 | 33.962 | 26.284 | 7.678 |
| B0-02 | 40.104 | 30.944 | 9.160 |
| B0-03 | 46.156 | 32.497 | 13.659 |
| E1-01 | 36.542 | 28.304 | 8.238 |
| E1-02 | 26.692 | 17.408 | 9.284 |
| E1-03 | 40.473 | 31.970 | 8.503 |
| INDEX-01 | 39.871 | 32.272 | 7.599 |
| INDEX-02, troncato | 49.152 | 44.316 | 4.836 |
| INDEX-03 | 36.508 | 29.806 | 6.702 |
| **Totale** | **349.460** | **273.801** | **75.659** |

Reasoning: **78,35% dell'output complessivo**, 90,16% nel run troncato. Il backend
riceve dal wrapper il solo `message.content`; `reasoning_content` non entra nei
fatti, nei gate o nel writer. La sua eliminabilità a parità di qualità non è
stata sperimentata. Nessuna conclusione sullo spegnimento del thinking da questi
dati; parametri immutati durante la diagnosi.

### Quanti record sono davvero duplicati

Conteggio all'interno di ciascuno degli otto JSON completi, incluso INDEX-01
sintatticamente valido ma respinto dall'envelope. Non si deduplicano le risposte
di run diversi: sono misure indipendenti dello stesso caso.

| Sezione | Record complessivi | Duplicati esatti di record |
|---|---:|---:|
| fields | 213 | 0 |
| facts | 162 | 0 |
| conditions | 25 | 0 |
| bindings | 11 | 0 |
| choice_groups | 3 | 0 |
| clarifications | 10 | 0 |
| coverage | 210 | 0 |
| **Totale** | **634** | **0** |

Nessun fatto inutilizzato: tutti i 162 fatti sono referenziati da assegnazioni
o condizioni. Nessuna coppia di fatti con subject/entity/aspect/property/value
identici, anche ignorando le citazioni. È un controllo preciso su questi
attributi, non una deduplicazione semantica generale di sinonimi o formulazioni.
Nessun binding inutilizzato rispetto ai riferimenti delle assegnazioni.

Esiste **un ID duplicato in coverage**, `p64.cb0` in B0-02: 1.907 occorrenze di
ID rispetto a 1.906 uniche per risposta. Non sono 1.906 destinazioni diverse nel
Word: sono sommati otto run. Nessun overlap coverage/fields. Sono rilevate 31
ripetizioni di reason fra fields, senza includere la prima occorrenza; non sono
record duplicati e le assegnazioni restano destinate a campi distinti.

Le occorrenze ripetute di uno stesso dato richieste dal modulo non sono
ridondanza eliminabile: due destinazioni diverse richiedono due assegnazioni,
anche quando riusano lo stesso fact_id. Questo riuso è già presente.

### Peso delle parti della risposta

| Run completo | Caratteri JSON | Record coverage | Caratteri coverage | Quota coverage |
|---|---:|---:|---:|---:|
| B0-01 | 24.315 | 21 | 8.676 | 35,68% |
| B0-02 | 27.932 | 21 | 8.663 | 31,01% |
| B0-03 | 42.623 | 28 | 10.535 | 24,72% |
| E1-01 | 25.832 | 33 | 11.779 | 45,60% |
| E1-02 | 28.171 | 20 | 7.478 | 26,55% |
| E1-03 | 26.776 | 36 | 11.683 | 43,63% |
| INDEX-01 | 23.611 | 25 | 7.843 | 33,22% |
| INDEX-03 | 20.774 | 26 | 8.639 | 41,59% |

Sugli otto JSON: 220.034 caratteri, di cui coverage 75.296 (**34,22%**),
fields 68.010, facts 40.944, conditions 20.985, bindings 4.155,
choice_groups 7.056 e clarifications 2.419. Il resto è intestazione/sintassi
root e valori scalari/lista vuota. Questi numeri non sono token.

I 210 record coverage sono spiegazioni ausiliarie sull'inventario già noto al
backend. **Non sono 210 duplicati esatti** e non sono interamente inutili:
alimentano audit, avvisi e contesto del narratore. Le loro motivazioni MODEL
non dimostrano però l'assenza di dati SOURCE e non autorizzano scritture.
Nei sette audit, 90–146 posizioni per run hanno spiegazioni respinte: sono
posizioni, non record, e non coincidono coi rifiuti dei valori corretti.

### Cosa è necessario e per quale funzione

| Parte | Consumatore e necessità |
|---|---|
| version | Seleziona il contratto/validazione storica. |
| fields | Mappa candidate→proposta, con disposizione, FORM, proprietà, condizioni e riferimenti ai fatti/ruoli/gruppi. Serve per attribuzione e scrittura verificata. |
| facts | Valore atomico, soggetto/proprietà e prove SOURCE con chunk/quote. È il supporto fattuale, da conservare. |
| conditions | Clausole FORM, scope, predicati e fatti di supporto. Servono per applicabilità, dipendenze e domande. |
| bindings | Collegamento persona–ruolo con prove FORM/SOURCE. Necessario dove richiesto dai gate personali; non è sostituibile col solo nome. |
| choice_groups | Opzioni native, cardinalità, condizioni e contesto FORM. Necessario per le scelte native quando proposte. |
| clarifications | Poche richieste USER locali, ancorate al FORM. Serve al dialogo, non sostiene un valore SOURCE. |
| uncertain_paragraph_ids | Segnala incertezza sostanziale; vuoto in tutti gli otto JSON completi. Non è un inventario da ripetere. |
| coverage | Spiegazioni di omissioni e osservabilità/narrazione; non è un'autorizzazione a scrivere né una prova fattuale. |
| reasoning_content | Non consumato come proposta o evidenza; acquisito negli HTTP e riflesso nell'usage. |
| project_id / proposal_stage in output | Non richiesti: il backend possiede già questi metadati; nell'envelope corrente sono vietati. |

Non si possono rimuovere oggi arbitrariamente label, property, reason o form
dai record: alcuni sono richiesti dai modelli Pydantic e/o dai controlli.
La presenza di property sia nel fatto sia nell'assegnazione permette anche
il controllo di coerenza fra le due. Distinguere ciò che è riducibile in un
futuro contratto da ciò che l'implementazione attuale accetta.

## 3. Dati disponibili ma omessi: presenza effettiva nell'input

**Verifica positiva su 60 target SOURCE × 9 richieste = 540 controlli.** Per
ogni target è stata cercata la sua quote autoriale completa, contigua dopo sola
normalizzazione Unicode/spazi, nei chunk del documento SOURCE corretto del
messaggio realmente inviato. Tutte le prove sono presenti. Non ci si limita a
cercare parole come «Bari» in qualunque documento.

Il corpus è identico: 56 chunk, 63.655 caratteri di testo SOURCE, cinque file:
34 avviso, nove generalità, quattro conoscenza generale, quattro visura e cinque
integrazione. `source_coverage.partial=false`. Nessuna evidenza di taglio SOURCE
per retrieval, chunk budget o serializzazione del FORM in queste acquisizioni.
Questo risultato riguarda il caso congelato, non qualsiasi corpus o bando.

| Dato omesso o bloccato | Prova già inviata |
|---|---|
| Leonardo: carica aggiornata e rappresentanza | integrazione, chunk -53 |
| Leonardo: nascita, residenza, CF | integrazione, chunk -54, primi dati anche -53 |
| Tutti i 24 campi dei tre soci | tabella completa in integrazione, chunk -54 |
| Elisa: dati professionali integrativi | integrazione -54/-55, oltre al record generalità -45 |
| Società: comune/provincia, fax, CCIAA e Registro Imprese | integrazione -52/-53, con fonti precedenti per identità/recapiti |

Il reading plan ha 125 source_property_lines e una sola source_role_target,
per il direttore tecnico. **Le tre righe della tabella soci non compaiono
nell'indice source_property_lines**, che seleziona righe con attributi; sono
presenti integralmente nel chunk -54. `omitted_property_lines=0` indica nessun
taglio per il limite delle righe ammesse, non che l'indice rappresenti ogni
formato tabellare. L'assenza dall'indice ausiliario non equivale a esclusione
dall'input SOURCE. Il suo possibile effetto sull'attenzione è un'ipotesi.

### Omissioni e rifiuti sono fenomeni distinti

| Run | Target SOURCE senza fields | Proposte corrette grezze | Corrette conservate dai gate locali | Corrette bloccate localmente |
|---|---:|---:|---:|---:|
| B0-01 | 37 | 22 | 21 | 1 |
| B0-02 | 37 | 22 | 17 | 5 |
| B0-03 | 10 | 49 | 21 | 28 |
| E1-01 | 42 | 18 | 13 | 5 |
| E1-02 | 34 | 25 | 19 | 6 |
| E1-03 | 37 | 23 | 21 | 2 |
| INDEX-01 | 33 | 25 | N/D | N/D, envelope respinto |
| INDEX-02 | N/D | N/D | N/D | N/D, output tronco |
| INDEX-03 | 37 | 23 | 21 | 2 |

Le altre proposte grezze non conformi, quando presenti, restano negli artefatti;
non diventano omissioni né valori corretti. Gli esiti locali non sono il numero
finale di scritture dopo dialogo, selezione e revisione.

Nelle motivazioni del modello compaiono sia affermazioni di assenza contraddette
dai chunk, sia dichiarazioni di impossibilità di usare il formato di ruolo:

- E1-02 per i soci: «Soci della società e relative qualifiche/albi non documentati
  nelle SOURCE.» Il chunk -54 contiene la tabella completa: qui la motivazione
  di assenza non è sostenuta dall'input osservato.
- B0-02: dati dei soci presenti in tabella, ma ruolo non attestato nei formati
  ammessi. È distinto dalla mancata disponibilità del dato e coerente col tipo
  di ostacolo mostrato dai rifiuti locali B0-03.
- B0-03 restituisce effettivamente tutti i 24 valori dei soci: dimostra che lo
  stesso corpus permette di recuperarli, pur senza superare i gate di binding.

### Limite distinto sui dati USER iniziali

Tutte le analisi hanno `user_values=[]`. La richiesta T0 della chat sceglie Mapi,
la partecipazione e Leonardo firmatario, ma queste scelte non entrano come dati
USER nella richiesta globale osservata. La SOURCE attesta l'anagrafica e la
carica, non chi sottoscrive quella specifica pratica. Perciò non ogni omissione
dei dati personali è riconducibile alla mancata lettura: mancano anche
l'associazione USER della pratica e/o un binding accettabile. La presenza delle
prove non autorizza a compilare qualsiasi ruolo o a scegliere il firmatario.
Nessun collegamento è stato corretto in questa diagnosi.

## 4. Valori corretti proposti e bloccati dai validatori

**49 occorrenze di campo con valore conforme, bloccate nei sette audit**:
B0 1/5/28, E1 5/6/2, INDEX-03 due. Sono 32 destinazioni distinte; non 49 fatti
aziendali diversi. Separati i 25 valori conformi INDEX-01 persi al gate globale.
Per INDEX-02 nessun punteggio è ricostruito dal frammento.

Classificazione per causa primaria, mutuamente esclusiva:

| Causa primaria | Occorrenze | Esempio |
|---|---:|---|
| Quote FORM insufficiente o non presente | 8 | Comune/provincia p15.s0/p15.s1 |
| Binding letterale del ruolo rifiutato | 23 | Soci di B0-03, esclusa qui l'occorrenza con ulteriore errore SOURCE prioritario |
| Ruolo e valore in chunk/record non collegati dal gate | 16 | Dati integrativi del direttore tecnico |
| Quote SOURCE che non contiene il valore completo | 2 | Provincia Bari (BA) citata da una riga che non la riporta |
| **Totale** | **49** | |

### Quote FORM: otto

Sette errori «Il solo marker non documenta la richiesta del campo» e uno
«Estratto non presente nel FORM». Per esempio `[[p15.s0]] (` o `([[p15.s1]])`
localizzano la posizione ma non contengono parole che ne documentino il
significato. Il validatore inline richiede un solo marker corretto e testo
contiguo utile; quelle citazioni sono respinte anche se Bari/BA sono giusti.
In E1-02 p15.s0 è associato a una quote marcata non presente nel paragrafo.
Non si è ampliato il contesto o rilassato il gate.

### Soci: tutti i 24 campi di B0-03 bloccati

I tre binding propongono source_role «socio» con due citazioni: titolo «Soci
...», poi riga della persona nella tabella. `_subject_bindings` richiede il
ruolo letterale delimitato in **ciascuna** citazione. «socio» non corrisponde
letteralmente a «Soci»; inoltre la riga tabellare non riporta quel ruolo. I
binding vengono respinti con «Ruolo attestato assente nell'estratto SOURCE».
I campi ereditano «Binding di ruolo rifiutato».

Questo non dimostra assenza della relazione nella fonte leggibile da una persona:
il titolo e la tabella la esplicitano. Dimostra un limite dei formati letterali
ammessi dal gate e delle citazioni proposte. Ventitré occorrenze sono assegnate
alla causa primaria binding; la ventiquattresima ha anche una quote SOURCE
insufficiente, classificata separatamente per non contare due volte.

### Direttore: sedici casi di mancato collegamento

Il binding cita il record di Elisa nel chunk generalità -45; alcuni fatti citano
l'integrazione -54/-55. Il gate richiede che ogni prova del fatto ricada in un
chunk supportato da un'attribuzione persona–ruolo ammessa. L'intestazione del
record in -45 non autorizza automaticamente valori di altri chunk. I formati
personali riconosciuti sono intestazione nome–ruolo o riga maiuscola ruolo–nome,
non qualsiasi frase narrativa o tabella. I dati integrativi rimangono bloccati.
Non è una prova che i dati siano assenti; il sistema non ha accettato la relazione
fra le citazioni effettivamente proposte.

### Due rifiuti SOURCE fondati sulla citazione effettiva

B0-03 usa «Bari (BA)» per p46.s0 e p53.s2, ma il fatto condiviso cita la frase
narrativa -55 che riporta Ordine/sezione/data/numero, senza il valore completo
«Bari (BA)». Il valore esiste nella tabella -54, **non nella quote scelta**.
Il fatto è rifiutato e blocca entrambe le destinazioni. La correttezza rispetto
al gold non rende questi due rifiuti un errore del validatore.

Per questo «49 valori corretti bloccati» non significa «49 controlli da togliere».
Le cause comprendono limiti reali del collegamento, citazioni inappropriate e
vincoli di sicurezza intenzionali. I record completi con errori, binding, fatti
e prove corrette disponibili sono in `correct-local-rejections.json`.

## 5. Fatti osservati e ipotesi da non trasformare in conclusioni

| Fatto osservato | Ipotesi ancora non verificata |
|---|---|
| SOURCE identiche e prove presenti in tutte le nove richieste | Ridurre il FORM aumenta o riduce la capacità di usarle in generale |
| INDEX-01 ripete due metadati dell'input vietati in output | L'indice diretto ha causato quella confusione |
| INDEX-02 consuma 90,16% output in reasoning e si tronca nei facts | Il solo obbligo coverage ha causato il reasoning lungo |
| Tutti i soci possono essere estratti in B0-03, poi vengono bloccati | Ogni omissione dei soci è dovuta soltanto al validatore |
| Coverage vale 34,22% dei caratteri JSON completi, senza duplicati di record | Togliere la copertura esaustiva riduce altrettanto i token totali o migliora i valori |
| Nessun fatto duplicato/inutilizzato nei JSON completi | Una nuova deduplicazione semantica sia necessaria o vantaggiosa |

## 6. Minimo cambiamento proposto al contratto di risposta

**Una sola modifica normativa proposta: rendere coverage sparsa, anziché
richiedere la spiegazione esaustiva di ogni posizione senza proposta.**

Mantenere input FORM B0 completo, SOURCE, budget, thinking, writer e tutti i
controlli attuali. Mantenere la stessa struttura dei record per fields, facts,
conditions, bindings, choice_groups e clarifications. Conservare la chiave
`coverage`, consentendo `[]` quando non ci sono spiegazioni specifiche da
restituire. L'inventario e le posizioni senza proposta sono già noti al backend.
La lista vuota è già ammessa dallo schema Pydantic: oggi è il compito espresso
nel prompt a chiedere un rendiconto esaustivo.

Le destinazioni senza proposta/spiegazione restano **UNEXPLAINED o da valutare**,
non SOURCE assente, non NA, non risolte. Non si deve inventare una motivazione
per sostituire quella non prodotta, né dichiarare copertura completa.
`attach_coverage` distingue già questa situazione. Il trade-off è una minore
spiegazione delle omissioni e un avviso di copertura incompleta più frequente;
non è una modifica trasparente della qualità del dialogo.

Il contratto continua ad ammettere soltanto le nove chiavi root esistenti:
version, uncertain_paragraph_ids, conditions, bindings, choice_groups, fields,
facts, clarifications, coverage. project_id e proposal_stage rimangono dati
dell'input/backend. Ribadire questo confine non significa accettare oggi la
risposta INDEX-01 scartando le proprietà vietate.

Controfattuale **solo dimensionale** sui tre B0: sostituire coverage con []
conservando tutto il resto toglierebbe 8.674 / 8.661 / 10.533 caratteri,
rispettivamente **35,67% / 31,01% / 24,71% del JSON visibile**. Nessuna chiamata,
nuova risposta, nuova validazione favorevole o qualità simulata da questo
calcolo. Non è una riduzione misurata di token o del reasoning.

Resta **una sola chiamata globale**, senza riparazioni LLM o secondo passaggio
per completare le posizioni. Se in futuro autorizzato, questo profilo del compito
andrà versionato e confrontato con B0 senza modificare gli archivi storici.
Nessuna modifica di prompt o comportamento è stata applicata qui.

Questa proposta riduce il lavoro di rendiconto e conserva i gate fattuali.
**Non risolve da sola binding, decisioni USER iniziali, marker o reasoning**;
non garantisce di evitare il troncamento avvenuto prima di coverage. Tali limiti
rimangono espliciti, così come le omissioni. Non propongo in questa fase un
nuovo motore, una compattazione del FORM o un aumento dei limiti di generazione.

## Verifiche della diagnosi

Confronto finale di 1.227 file protetti: codice/frontend, fixture e tre audit
originali. Hash identici all'inizio dell'attività. Manifest e bundle nuovi con
soli derivati/riferimenti, senza DB o credenziali. JSON/CSV e riferimenti locali
verificati; git diff --check passato. Nessuna suite software ripetuta: il codice
non è stato modificato. I test storici sono nei rapporti delle serie originali,
non vengono presentati come appena rieseguiti.

Un primo controllo offline confrontava il testo HTTP con response.txt, che
contiene il newline aggiunto dall'archiviazione: assertion fallita, controllo
corretto limitandosi al whitespace esterno. Nessun originale alterato né
chiamata ripetuta. Dettaglio in `diagnostic-issues.json`.
