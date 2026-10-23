# Preparazione del benchmark di compilazione

**Inventario e registro aggiornabile — aggiornato al 16 ottobre 2026.**

La priorità richiesta è predisporre dati, risultati attesi e ambiente di prova
prima di scegliere o implementare la nuova architettura. Questo documento
raccoglie cosa serve, cosa esiste e cosa manca. All’inventario iniziale sono
seguite le revisioni del gold e il congelamento autorizzato di Minervino V1.
Nessuna nuova valutazione LLM o istanza integrata di test avviata.

Questo file mantiene lo stato della preparazione e l'indice delle nuove prove.
[relazioni.md](relazioni.md) rimane il registro completo degli esperimenti,
inclusi fallimenti e limiti. La
[proposta architetturale](ARCHITETUTTURA_PROPOSTA.md) resta da discutere.

**Decisione del 17 ottobre:** stop esperimenti di compattazione FORM; B0 resta
il riferimento, E1 e indice diretto non da integrare. Nessuna nuova API LLM o
modifica applicativa nella
[diagnosi del contratto di risposta](docs/diagnosi-contratto-risposta-b0-e1-2026-10-17.md).
E2 non avviato; le proposte di prosecuzione riportate sotto sono storiche.

Il [replay INDEX-01 e controllo USER/thinking](docs/replay-index01-user-reasoning-2026-10-17.md)
del 17 ottobre aggiunge diagnosi offline e test software, non chiamate LLM:
metadati isolati, schema passa ma solo 19 grounded/18 conformi. Trasporto delle
richieste USER registrate implementato separatamente; senza USER B0 identico.
Coverage invariato, futuro pilot thinking non eseguito. Non sommare i replay
ai run reali e non confrontare test con USER col benchmark senza USER.

## 1. Inventario minimo

Servono **un originale, le istruzioni della procedura, fonti aziendali coerenti,
uno scenario di partecipazione, un gold indipendente e un ambiente isolato**.
Il benchmark deve spiegare cosa era richiesto, quali dati erano disponibili,
cosa doveva chiedere il sistema e cosa è stato realmente scritto nel Word.

| ID | Materiale | Contenuto necessario | Stato |
|---|---|---|---|
| P01 | Scheda del caso | Azienda, modulo, data di riferimento, scenario e perimetro | Congelati in Minervino V1: Mapi, Leonardo, 15/10/2026; perimetro e checkpoint espliciti |
| P02 | Word originale vuoto | File immutabile, provenienza, hash e versione | Diversi originali disponibili |
| P03 | Documenti della procedura | Avviso, disciplinare e istruzioni pertinenti, quando presenti | Disponibili per tre bandi archiviati |
| P04 | Fascicolo aziendale | Informazioni societarie, persone, ruoli e documenti necessari | Tre fonti Company verificate contro il backend, un General distrattore e avviso della procedura congelati |
| P05 | Scelte della pratica | Partecipante, firmatario, modalità e altre decisioni USER | Scenario congelato, separato dai fatti documentali |
| P06 | Inventario umano dei requisiti | Richieste, soggetti, condizioni e destinazioni, anche se perse dal parser | 267 destinazioni Minervino annotate con etichette, contesto, soggetto e ramo; Labirinto conservato |
| P07 | Word gold compilato | Risultato atteso redatto e controllato indipendentemente | GOLD V1 autorizzato e congelato; limite del rendering Word dichiarato |
| P08 | Gold strutturato | Valori, vuoti corretti, scelte, prove e checkpoint | Gold JSON congelato: 187 posizioni testuali, 67 preferenze, 13 controlli nativi |
| P09 | Scheda delle risposte USER | Informazioni fornite all'inizio e risposte ai chiarimenti | T0 iniziale e quattro argomenti di risposta fissati; T1/T2 definiti, nessun suggerimento spontaneo |
| P10 | Ambiente separato | DB, storage, KB, indici e sessioni dedicati | Meccanismi disponibili; istanza completa non predisposta qui |
| P11 | Configurazione riproducibile | Codice effettivo, dipendenze, modelli, parametri e budget | Da congelare prima della nuova baseline |
| P12 | Protocollo di valutazione | Denominatori, criteri, ripetizioni e trattamento degli errori | Congelato per Minervino V1: futura baseline su tre run, errori critici e fasi separati |
| P13 | Archivio delle esecuzioni | Prompt, input, output, dialogo, stato, Word e misure | Strumenti esistenti; copertura completa da verificare sul caso |

«Disponibile» indica un materiale esistente, non che sia già pronto per un
nuovo confronto. Non sono state avviate un'istanza di test o una nuova baseline.

## 2. Materiali già esistenti

### 2.1 Labirinto V1: regressione congelata

La [fixture dedicata](demo-documents/benchmark-compilazione/v1/README.md) contiene:

- [originale DOCX](demo-documents/benchmark-compilazione/v1/modulo-benchmark.docx):
  55 posizioni, di cui 44 testuali e 11 checkbox native;
- sette fonti: cinque Company KB, una fonte di progetto e una General KB
  distrattore; una fonte di altro progetto è separata ed esclusa;
- [gold JSON](demo-documents/benchmark-compilazione/v1/gold.json) autoriale:
  22 valori/scelte attesi, 9 non applicabili, 14 mancanti, 6 condizioni da
  chiarire, un caso ambiguo, un conflitto, una firma manuale e uno spazio ufficio;
- [manifest](demo-documents/benchmark-compilazione/v1/manifest.json) con gli hash.

In questa ricognizione gli **11 hash del manifest corrispondono ai file**.
È una verifica di integrità, non una nuova misura della qualità LLM.

Il runner principale legge la fixture direttamente, saltando l'ingestion.
Valuta proposta e controlli, senza creare sessioni o generare Word. I suoi
risultati non misurano l'intero percorso dalla KB all'artefatto finale.

Le fonti contengono volutamente dati mancanti e conflitti: compilare tutti
gli spazi sarebbe scorretto. **V1 resta congelata:** aggiungere informazioni
o cambiare aspettative richiede una nuova versione, conservando l'esistente.

### 2.2 Materiali complementari

| Materiale | Disponibile | Utilità e limite |
|---|---|---|
| [Checkbox V1](demo-documents/benchmark-checkbox/v1/README.md) | DOCX, fonti, gold e manifest | Regressioni delle scelte; non è una candidatura completa |
| [Dialogo V1](demo-documents/benchmark-dialogo/v1/README.md) | 43 casi con checkpoint e aspettative | Misura risposte e mutazioni su contesti preparati; non una nuova analisi completa |
| [Sintesi V1](demo-documents/benchmark-sintesi/v1/README.md) | Checkpoint e casi su ruoli/tempi | Misura la sintesi; non la compilazione completa |
| [Minervino V1](demo-documents/benchmark-minervino/v1/README.md) | Modulo/avviso reali, fonti e scenario sintetici, gold Word/JSON e manifest | Base congelata; nuova baseline integrata da eseguire |
| [Catanzaro](demo-documents/bandi/catanzaro-dl-cse/fonti.json) | Originali, DOCX convertito e mappa parziale dei campi | Utile per tabelle; la mappa non copre tutti i rami |
| [Trapani](demo-documents/bandi/trapani-green/fonti.json) | DOCX originale, avviso e disciplinare | Altro caso reale; accuratezza valutabile solo con annotazioni indipendenti |
| [Profilo Mapi simulato](demo-documents/generalita-mapi.md) e visura demo | Identità, sedi, ruoli e parte dei dati professionali | Vari dati personali e poteri sono assenti; identificativi fiscali demo non formalmente validi |
| [Integrazione fornita dall'utente](<nuovi dati/integrazione.md>) | Rappresentante aggiornato, anagrafica di Leonardo, soci, dati professionali ed estremi camerali | Già caricata come integrazione-company.md; cinque chunk presenti nell'analisi esaminata il 16 ottobre |
| [Gold sintetico dell'utente](<nuovi dati/domanda-iscrizione.GOLD-SINTETICO.docx>) | Dati anagrafici e societari, soci, sei preferenze e scelte della pratica | Candidato revisionato il 16 ottobre: da ripristinare i tre paragrafi del direttore e formalizzare le scelte USER; non congelato |
| [Gold revisione 1](<nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>) | Blocco direttore e etichette ripristinati; scelte e valori dell'utente conservati | Preparato su richiesta dell'utente; 60 occorrenze controllate, in attesa di revisione visuale e OK |
| [Scenario del gold](demo-documents/benchmark-minervino/v1/evaluation/scenario.md) | Scelte, designazioni, attestazioni, policy e checkpoint | Congelato in V1; scheda di lavoro in nuovi dati rimanda alla versione canonica |
| [Gold V1 definitivo](<nuovi dati/domanda-iscrizione.GOLD-V1.docx>) | Riferimento corretto ricostruito dall’originale e copiato nella fixture | Hash nel manifest; firma e continuazioni vuote, note fuori dai campi |
| [Archivio benchmark](docs/benchmarks/README.md) | Report, bundle e manifest storici | Versioni e perimetri differenti; non è una nuova baseline omogenea |

Nei materiali `demo-documents/` inventariati non è stato individuato un DOCX
dedicato e dichiarato come gold compilato. Le bozze prodotte dal sistema,
anche se già controllate, non diventano automaticamente il risultato atteso.
Successivamente l'utente ha fornito il candidato gold in `nuovi dati/`, distinto
dalle bozze del sistema; la revisione è collegata nella sezione 6.4.

## 3. Caso iniziale: Minervino

**Il 16 ottobre l'utente ha scelto Minervino come primo caso.** L'originale è
[domanda-iscrizione.docx](demo-documents/bandi/minervino-elenco-sia/originali/domanda-iscrizione.docx),
accompagnato dall'avviso archiviato. Entrambi gli hash corrispondono al manifest
di provenienza, verificato il 16 ottobre. La scelta del bando non definisce da
sola azienda, scelte della pratica e data di riferimento.

La proposta rimane affiancare alla regressione congelata Labirinto V1 una
compilazione di Minervino con **azienda simulata documentata in modo coerente**,
misurando l'intero percorso dalla KB al Word. Il caso completo è da preparare.

Nel gold ricevuto il 16 ottobre l'operatore è Mapi, il firmatario Leonardo e la
data Bari, 15/10/2026. Questi parametri descrivono lo scenario autoriale;
la disponibilità delle singole decisioni è ora fissata nello scenario V1.

La scheda P01 deve fissare:

- originale e documenti della procedura, senza modifiche;
- un solo operatore, con identità coerente nei diversi documenti;
- ramo e modalità di partecipazione scelti;
- data di riferimento congelata, per valutare documenti e incarichi;
- perimetro: tutte le richieste del modulo, distinguendo pertinenti, escluse,
  irrisolte e manuali;
- dati documentati, decisioni USER e pochi vuoti intenzionali, annotati in anticipo.

Il dataset deve consentire di compilare molti campi correttamente. Le assenze
intenzionali servono a verificare la prudenza. Non si decide quali informazioni
aggiungere dopo aver visto le risposte del modello.

Per un bando storico si chiarisce se lo scenario è una simulazione a data
congelata oppure una verifica alla scadenza originaria. Documenti recenti
non dimostrano automaticamente il possesso di requisiti nel passato.

## 4. Contenuti della KB da preparare

La lista effettiva deriva dal modulo scelto. Questi sono gruppi di informazioni
candidati: non occorre produrre bilanci o certificazioni se il caso non li richiede.

| Documento o gruppo | Dati da includere quando richiesti | Distinzioni da conservare |
|---|---|---|
| Visura/scheda societaria simulata | Denominazione, forma, tipologia, CF, P.IVA, CCIAA, Registro Imprese, REA e date | REA, numero Registro Imprese e date hanno significati distinti |
| Sedi e contatti | Comune, provincia, CAP, via, civico, sede operativa, PEC, e-mail, telefono | Sede aziendale e residenza personale; sede coincidente o diversa |
| Schede delle persone | Nome, cognome, nascita, residenza e CF personale | Ogni dato deve riferirsi a una persona identificata |
| Incarichi e rappresentanza | Amministratori, direttori tecnici, nomine/cessazioni, poteri e procure | Incarico, poteri e scelta del firmatario della pratica sono distinti |
| Iscrizioni professionali | Qualifica, Ordine, provincia, numero, sezione/settore e date | Albo, documento, abilitazione e iscrizione non coincidono |
| Polizze e certificazioni | Numero, titolare, ente, ambito, decorrenza e scadenza | Documento scaduto, altra impresa o altro ambito non sostengono il requisito |
| Servizi e capacità economiche | Servizi, committenti, importi, periodi, categorie e ricavi richiesti | Ricavi generali, fatturato specifico e importi di lavori/servizi non sono intercambiabili |
| Fonti della procedura | Codici, oggetto, scadenze, limiti di scelta e allegati richiesti | Descrivono la procedura, non il possesso dei requisiti aziendali |

Per ogni fonte servono **originale, titolo, soggetto, data, versione, ruolo,
ambito di accesso e hash**. Le prove dei valori attesi si annotano nella
mappa di valutazione, con pagine o estratti localizzabili.

Le fonti devono assomigliare a normali documenti aziendali: niente marker dei
campi, istruzioni per il modello o elenco delle risposte del gold. I dati
vanno controllati per coerenza fra documenti, comprese date, ruoli e indirizzi.

Gli identificativi sintetici del caso ordinario devono rispettare i controlli
formali richiesti. Per Minervino V1 è dichiarata un’eccezione: conservare i valori
dimostrativi delle fonti, senza checksum nello score o attestazione di validità
reale. Un confronto sulla validità fiscale richiede uno scenario distinto.
Non si correggono gli identificativi delle fixture esistenti.

Per iniziare bastano fonti leggibili e un insieme contenuto di documenti.
Scansioni e OCR possono costituire prove successive. Il formato va registrato:
un risultato su TXT non misura la robustezza alle scansioni. Un PDF e la sua
trascrizione non sono due prove indipendenti dello stesso fatto.

### Mappa di copertura da compilare

Questa tabella si compila manualmente per ogni richiesta prima del caricamento.
Appartiene al gold: rimane fuori dalla KB e dai prompt.

| Requisito stabile | Soggetto e ramo | Fonte/prova o decisione USER | Disponibile all'avvio? | Esito atteso | Revisione |
|---|---|---|---|---|---|
| Da compilare sul modulo scelto | — | — | — | — | Non iniziata |

La mappa permette di attribuire un vuoto a dataset, estrazione, ricerca,
proposta, validazione o scrittura, senza dover scegliere una nuova architettura.

## 5. Scelte della pratica e dialogo

Servono una scheda di scenario e una scheda delle risposte USER con:

- operatore partecipante, modalità e persona scelta per firmare;
- eventuali soggetti designati per lo specifico incarico;
- categorie, fasce, preferenze e dichiarazioni previste dal modulo;
- allegati effettivamente disponibili, luogo e data quando necessari;
- cosa fare in caso di dato ignoto, rinvio, risposta ambigua o correzione.

La scelta di un firmatario non documenta i suoi poteri; scegliere una categoria
non dimostra il possesso del requisito. Tali aspetti hanno prove o esiti distinti.

Si specifica quali informazioni sono nella richiesta iniziale e quali
diventano disponibili solo dopo una domanda. La scheda contiene risposte
**per argomento**, senza imporre una sequenza esatta di frasi o domande.

L'operatore risponde coerentemente a formulazioni equivalenti. Non aggiunge
suggerimenti per recuperare un errore del modello; eventuali aiuti sono
interventi registrati, da valutare separatamente.

## 6. Word gold e gold strutturato

Il gold si prepara prima della nuova baseline, revisionando modulo, fonti
e scenario. Non dipende dagli output o dai criteri del compilatore attuale.

### 6.1 DOCX compilato di riferimento

Serve almeno un **Word gold per lo scenario finale**, compilato dallo stesso
originale e controllato indipendentemente dal writer sotto valutazione.

Deve contenere valori e scelte corretti, mantenendo vuoti rami esclusi, dati
irrisolti, spazi ufficio e firma manuale. «Compilato» non significa riempire
ogni spazio. Per il primo caso è ragionevole una redazione manuale con editor
compatibile, seguita da una revisione distinta; una seconda persona è utile
se disponibile. Si annotano autore, revisore, data e punti dubbi.

Una copia PDF aiuta la revisione visuale. Si registrano editor e versione:
differenze di impaginazione fra editor non equivalgono sempre a errori.
Il PDF non sostituisce il DOCX gold.

### 6.2 Annotazioni delle aspettative

Il Word da solo non spiega perché un campo sia vuoto. Per ogni requisito e
occorrenza servono:

| Annotazione | Scopo |
|---|---|
| ID semantico, etichetta e posizione umana | Rilevare anche i campi persi dal parser |
| Soggetto, ruolo e condizioni | Valutare pertinenza e ramo |
| Valore o esito atteso | Distinguere compilazione, attesa, non applicabilità e azione manuale |
| Varianti equivalenti ammesse | Accettare formati innocui, definiti prima degli output |
| Fonte e prova accettabile | Verificare il collegamento al soggetto, ammettendo più prove valide |
| Decisione USER necessaria | Stabilire quando il dato è utilizzabile |
| Vincoli dei gruppi di scelta | Valutare esclusività, minimi, massimi e ambito |
| Motivo del vuoto/blocco | Distinguere prudenza corretta e omissione erronea |
| Esito nei checkpoint | Valutare ciò che era conoscibile nei diversi momenti |

Gli ID del parser possono essere un raccordo, non l'unico inventario del gold.
Requisiti ripetuti richiedono anche la verifica delle singole occorrenze.

### 6.3 Checkpoint minimi

| Momento | Informazioni del sistema | Aspettative da fissare |
|---|---|---|
| T0: avvio | Fonti e decisioni della richiesta iniziale | Dati proponibili, condizioni aperte e domande necessarie |
| T1: chiarimenti | Risposte effettivamente fornite nello scenario | Valori/scelte utilizzabili e vuoti residui |
| T2: export esplicito | Stato acquisito e richiesta di bozza | Contenuto atteso del Word prodotto |

Il Word gold finale corrisponde a T2. Un secondo Word gold T0 è utile se
vogliamo valutare anche una bozza prima dei chiarimenti; non è indispensabile
per iniziare. Le annotazioni coprono entrambi gli stati.

**Gold, Word compilato di riferimento e scheda delle risposte non entrano
nella KB né nei prompt.** Le risposte previste diventano visibili al sistema
solo quando effettivamente fornite dall'utente nel turno stabilito.

### 6.4 Situazione concreta di Minervino

**Minervino V1 congelato su autorizzazione dell’utente il 16 ottobre 2026.**
Il [pacchetto canonico](demo-documents/benchmark-minervino/v1/README.md) contiene
originale, fonti, richiesta iniziale, scenario, copione, gold Word/JSON,
inventario e manifest. Copia del [Word finale](<nuovi dati/domanda-iscrizione.GOLD-V1.docx>)
nella cartella richiesta. La nuova baseline integrata non è ancora eseguita.

Le seguenti revisioni descrivono la preparazione storica del candidato.
La [revisione](docs/minervino-gold-review-2026-10-16.md) confronta 52 occorrenze
con le fonti attuali; i valori corrispondono, ma sono stati eliminati tre
paragrafi del direttore con otto destinazioni. Da ripristinare e compilare.
Sei preferenze, designazioni e attestazioni richiedono una scheda USER distinta
dai dati SOURCE. Le checkbox native sono coerenti e le sei X conservate.

Su richiesta dell'utente è stata poi preparata la
[revisione 1 del Word](<nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>):
ripristinati gli otto campi del direttore e le etichette originali nei paragrafi
della società/soci, preservando dati e scelte del candidato ricevuto. Il file
dell'utente rimane invariato. Le 52 occorrenze precedenti e gli otto nuovi campi
sono verificati; tabelle e controlli nativi sono identici al candidato.
La [scheda scenario](<nuovi dati/SCENARIO_GOLD_MINERVINO.md>) registra le decisioni
contenute nel gold. In seguito l’utente ha autorizzato risoluzione dei rilievi,
adozione della base, tag e push: l’attesa dell’OK è superata da questa richiesta.
Il definitivo usa il pacchetto originale, conserva le scelte, sposta le note
fuori dai campi e tiene unito il blocco firma con proprietà Word. Rendering
alternativo e limiti Word sono registrati nel rapporto di congelamento.
Nessuna baseline o modifica alla KB avviata.

La precedente bozza `domanda-iscrizione.compilato(2).docx` è un output del sistema: il suo hash
corrisponde a quello della [diagnosi storica](docs/minervino-output-2-2026-10-13.md),
che documenta 20 posizioni compilate e difetti di comune, granularità
dell'indirizzo e giunzioni testuali. Non è il riferimento indipendente.

Per completare e congelare il gold del nuovo caso, i passaggi sono:

1. Leggere l'originale e compilare l'inventario umano di richieste e condizioni.
2. Definire lo scenario e preparare le fonti mancanti in un nuovo pacchetto,
   lasciando intatte le fixture e le fonti della demo.
3. Assegnare a ogni richiesta un valore con prova, una decisione USER o un
   motivo esplicito per restare vuota nei diversi checkpoint.
4. Compilare una copia dell'originale in base a queste annotazioni, senza
   passare attraverso il motore sotto valutazione, poi revisionare contenuto,
   scelte e impaginazione.
5. Congelare Word, annotazioni, fonti e scenario prima di misurare il sistema.

Con le sole fonti attuali si può preparare un gold parziale fedele ai dati
disponibili. Il 16 ottobre l'utente ha segnalato un'integrazione già caricata:
contiene anche dati personali, soci ed estremi camerali/professionali prima
assenti. La nuova [diagnosi](docs/minervino-integrazione-2026-10-16.md) conferma
che molti dati erano nell'input e sono stati persi successivamente. Queste
fonti consentono di iniziare un gold più esteso; le scelte e attestazioni non
ancora fornite vanno fissate nello scenario o lasciate esplicitamente aperte.
Non occorre aggiungere indiscriminatamente altre fonti per spiegare i vuoti.

L'utente ha proposto di compilare personalmente il gold oppure revisionare
una bozza preparata separatamente dal motore. Entrambe le modalità sono
compatibili con la valutazione: annotazioni fondate su modulo/fonti e revisione
del Word precedono il congelamento. Le stesse fonti possono entrare nel backend
di test; il Word gold e le aspettative rimangono separati dagli input del modello.

Le [istruzioni storiche](demo-documents/bandi/minervino-elenco-sia/istruzioni.txt)
sceglievano Luca Ferri e limitavano la prova ad anagrafica e dati disponibili
nel ramo societario. Sono il contesto di quella prova: non fissano implicitamente
per il nuovo benchmark la compilazione di categorie, dichiarazioni o allegati.

## 7. Ambiente tecnico

| Elemento | Cosa predisporre | Disponibilità / limite verificato |
|---|---|---|
| Database | SQLite dedicato e stato iniziale ripristinabile | Supportato `MAPI_DB_PATH`; nessun DB creato qui |
| Originali e bozze | Storage separato | Supportato `MAPI_STORAGE_PATH` |
| KB | Directory separata, solo fonti del caso | Supportato `MAPI_KNOWLEDGE_PATH`; evitare la KB condivisa della demo |
| Indice | FTS5/Qdrant dichiarato e isolato | FTS5 nel DB; Qdrant locale deriva il percorso dal DB; remoto richiede isolamento verificato di istanza/collezioni |
| Ingestion | Import reale, errori, testo estratto, numero documenti e chunk | Saltata dal runner principale `--fixture`; va misurata nel percorso integrato |
| Modello generativo | Profilo, modello, impostazioni effettive e budget | Nessun profilo letto o provider chiamato in questa ricognizione |
| Embedding | Modello/versione/parametri se utilizzato | Registrare il percorso effettivo: corpus intero e retrieval sono prove differenti |
| Applicazione | Istanza, porte e browser dedicati | Cambiare solo le porte non isola DB, KB o storage |
| Runtime | Lockfile e versioni degli strumenti | `uv` e Python nel PATH; Node/npm non nel PATH osservato; previsto anche `.tools/node/bin` |
| Editor e rendering | Editor per gold e confronto visuale | `libreoffice`/`soffice` non nel PATH osservato; Word/altri editor non verificati |
| Ripristino | Snapshot iniziale, sessione nuova e output univoco per run | Da predisporre per il nuovo caso completo |

La configurazione deve elencare percorsi effettivi e documenti realmente
visibili dopo l'import. Il controllo iniziale esclude contaminazioni da altri
progetti, gold e bozze. Le credenziali rimangono fuori dai report.

Si tengono distinte due modalità:

1. **Fixture diretta:** corpus esplicito, meno variabili; non misura ingestion
   e caricamento KB.
2. **Percorso integrato:** caricamento dei file, chat, risposte e Word esportato;
   misura anche le perdite prima e dopo la chiamata LLM.

La stessa famiglia di dati può essere usata in entrambe, registrando eventuali
differenze nei testi/chunk effettivi. Il nuovo caso completo richiede la seconda.

## 8. Protocollo di valutazione

Prima della baseline si congelano codice effettivo, fixture, gold, prompt
e configurazione non riservata. Si registrano commit e modifiche locali:
il solo commit non descrive un workspace con cambiamenti pendenti.

| Dimensione | Cosa misurare |
|---|---|
| Comprensione | Richieste/destinazioni riconosciute rispetto all'inventario umano; correttezza di rami e soggetti |
| Disponibilità delle prove | Dati nei file, estratti, disponibili al modello e poi utilizzati |
| Proposte grezze | Corrette, errate e omesse prima dei controlli applicativi |
| Validazione | Proposte corrette respinte e proposte scorrette ammesse, con motivi |
| Dialogo | Informazioni necessarie acquisite, domande ridondanti/ambigue e attribuzione delle risposte |
| Word finale | Valori/scelte nelle posizioni corrette, parti preservate, integrità e leggibilità |
| Correzioni | Effetti sui dipendenti, senza mutazioni estranee |
| Risorse | Chiamate per fase, retry, token, cache, tempi, timeout e costo quando misurabile |

Si contano separatamente **requisiti unici e occorrenze scrivibili**.
Il denominatore dei dati compilabili a T0 comprende quelli pertinenti e
documentati a T0; a T1 include le informazioni effettivamente acquisite.
Firme, spazi ufficio e rami esclusi hanno aspettative proprie.

La precisione delle scritture confronta quelle corrette con tutte le scritture
prodotte. La copertura confronta quelle corrette con quelle attese al checkpoint.
Si riportano conteggi assoluti e valutazione dei gruppi di scelta: molte caselle
vuote non devono gonfiare il risultato. Le deselezioni per esclusività sono
effetti di una scelta, non fatti indipendenti.

Il confronto del Word valuta contenuti, posizioni e controlli, senza pretendere
identità binaria del DOCX. Metadati ed editor cambiano i byte. Serve anche la
revisione visuale per testo tagliato, tabelle illeggibili e giunzioni errate.

Come protocollo iniziale proporrei **tre run a condizioni congelate e sessioni
nuove**, conservando anche errori, timeout e run incompleti. Tre prove mostrano
variabilità iniziale, non forniscono una stima statistica robusta. Budget,
limite di turni e soglie di accettazione restano da concordare prima della serie.

Dati inventati, soggetti errati, scelte non autorizzate e contaminazioni devono
essere evidenti nel report anche se la copertura complessiva è elevata.

## 9. Artefatti di ogni run

- ID, data, stato, modalità e configurazione non riservata.
- Codice effettivo, manifest dei materiali e stato iniziale.
- File visibili, testo estratto e chunk, quando si misura l'ingestion.
- Prompt, schema, input e output reali di ogni fase; errori e dati non acquisiti.
- Proposte, validazioni e stato prima/dopo i turni USER.
- Trascrizione della chat, interventi manuali ed export richiesti.
- Word esportato, report di scrittura e confronto col gold, inclusa la revisione
  visuale quando eseguita.
- Tempi e usage; costo dichiarato come stima se ricavato da un listino.

Report in `docs/`, grezzi in nuove directory di
`backend/data/compilation-audit/`. I dati locali esclusi da Git richiedono
backup verificabile; i bundle destinati al repository escludono credenziali.

Non serve scrivere un nuovo runner per inventariare e revisionare i materiali.
Prima dell'esecuzione si verifica cosa acquisiscono gli strumenti esistenti,
dichiarando i passaggi ancora manuali.

## 10. Varianti e prove esterne

Dopo il primo caso completo si possono congelare scenari separati con dato
mancante, conflitto, omonimia, ruolo cessato o fonte fuori progetto. Si cambia
una condizione controllata per volta, senza modificare il caso base.

Le aspettative si fissano prima delle prove. Non si aggiungono fonti per
salvare un output e poi si presenta il risultato come miglioramento del motore.

Le prove occasionali su un altro bando reale rimangono separate: pool,
sorteggio e tutti gli esiti registrati, senza nuove estrazioni dopo un insuccesso.
Senza gold revisionato non si dichiarano percentuali di accuratezza.

## 11. Ordine di preparazione

| Ordine | Attività | Risultato | Stato |
|---|---|---|---|
| 1 | Scegliere caso, scenario e data | Scheda P01 e decisioni iniziali | Congelati in Minervino V1 |
| 2 | Leggere il modulo | Inventario umano P06, con dubbi/esclusioni dichiarati | 267 destinazioni annotate |
| 3 | Preparare le fonti | Fascicolo P04 e mappa di copertura revisionati | Cinque documenti congelati; quote per le 60 occorrenze SOURCE |
| 4 | Definire risposte e checkpoint | Schede P05/P09 | Richiesta iniziale e quattro argomenti con T0/T1/T2 fissati |
| 5 | Compilare e revisionare i gold | Word P07 e annotazioni P08 coerenti | GOLD V1 e JSON pronti; rendering e limiti dichiarati |
| 6 | Congelare il pacchetto | Versione, hash e revisione registrati | Minervino V1 congelato; Labirinto V1 preservato |
| 7 | Predisporre istanza e caricamento | DB/KB/storage isolati e corpus documentato | Copie isolate dal backend; cinque SOURCE conformi; ingestion nuova non misurata |
| 8 | Fissare protocollo e configurazione | Misure, ripetizioni, turni e budget | B0 fissato: tre analisi DeepSeek thinking, continuazioni con copione e budget registrati |
| 9 | Eseguire la baseline attuale | Tutti i run con i loro artefatti | Tre analisi reali e tre export parziali acquisiti; perimetro servizi dichiarato |
| 10 | Attribuire le perdite alle fasi | Evidenze per discutere i cambiamenti architetturali | Omissioni, binding, scelte iniziali, domande, checkbox e layout distinti nel report B0 |

Il caso è pronto quando un revisore può spiegare, senza consultare gli output
LLM, perché ogni richiesta vada compilata, chiarita o lasciata vuota a ciascun
checkpoint. Un altro operatore deve poter ricostruire l'ambiente dai materiali.
Gli eventuali errori del gold richiedono errata/versione e rivalutazione
dichiarata, conservando le misure precedenti.

## 12. Aggiornamenti della preparazione

| Data | Attività | Esito | Prossimo passo |
|---|---|---|---|
| 15 ottobre 2026 | Inventario dei materiali | Controllati 11 hash Labirinto V1, 55 posizioni gold e composizione delle fonti; rilevati materiali e limiti dei runner | Concordare caso, scenario e data; poi inventario umano delle richieste |
| 16 ottobre 2026 | Scelta di Minervino e verifica del materiale | Bando scelto dall'utente; hash dell'originale e dell'avviso conformi al manifest; confermato che la bozza esistente è l'output già diagnosticato, non un gold | Inventario delle richieste e definizione del nuovo scenario/fonti prima del Word gold |
| 16 ottobre 2026 | Diagnosi della prova con integrazione | Tutti i cinque nuovi chunk nell'input; 22 scritture finali, omissioni e blocchi documentati; input/audit ricostruiti offline identici | Gold dalle fonti già integrate e dallo scenario; non attribuire i vuoti osservati alla sola KB |
| 16 ottobre 2026 | Revisione del gold sintetico dell'utente | 52 occorrenze coerenti con KB, sei X e tre checkbox vere; eliminati tre paragrafi del direttore con otto destinazioni; gold invariato | Ripristinare direttore, formalizzare le scelte USER, annotare vuoti/equivalenze e verificare layout prima del congelamento |
| 16 ottobre 2026 | Preparazione del Word revisione 1 | Ripristinati direttore e label originali; 52 occorrenze precedenti + otto nuove verificate, sei X e 13 controlli preservati; aggiunta scheda scenario | L'utente controlla il file; attendere il suo OK prima di congelare |
| 16 ottobre 2026 | Verifica del verdetto sulla revisione 1 | Numerazione alfabetica conservata; firma isolata a pagina 10 non confermata dal renderer alternativo; assegnazioni già nello scenario; due note nelle aree compilabili confermate | [Riscontro dettagliato](docs/minervino-verifica-verdetto-2026-10-16.md); controllo in Word, eventuali correzioni e OK prima del congelamento |
| 16 ottobre 2026 | Congelamento autorizzato Minervino V1 | Word dall'originale, note fuori dai campi, firma unita nel PDF LibreOffice, 267 destinazioni annotate, fonti/scenario/copione e manifest congelati | [Base e verifiche](docs/minervino-base-v1-2026-10-16.md); tag baseline-minervino-v1-20261016, poi istanza isolata e baseline integrata |
| 16 ottobre 2026 | Discussione separata E1/E2 | Piano documentale: E1 confronta rappresentazioni complete; E2 confronta estratti compatti con E1 sulle stesse destinazioni e contro il gold | [Piano e limiti](docs/piano-esperimenti-e1-e2.md); definire contratto compatto e B0, poi manifest dei gruppi E2 |
| 16 ottobre 2026 | Preflight offline B0 | 240.276 caratteri JSON più 24.675 system; corpus coerente con fixture, 267 destinazioni, thinking globale forzato attivo per DeepSeek | [Misure preliminari](docs/b0-preflight-2026-10-16.md); tre run reali ancora da acquisire, nessuna qualità/token provider misurati |
| 16 ottobre 2026 | B0 con provider autorizzato | Tre analisi e tre Word: 23/17/22 valori conformi sui 60 SOURCE; zero dei quattro argomenti USER chiesti; 30 chiamate, 481.199 token | [Rapporto B0](docs/baseline-minervino-b0-2026-10-16.md); fissare il contratto E1, poi confronto completo; nessun motore modificato |
| 16 ottobre 2026 | E1 compact-v1 approvato ed eseguito | 116 test mirati e 2.258 backend passati, Ruff; input -16,09%; Word 14/11/23 contro 23/17/22 B0; tutti gli esiti conservati | [Rapporto E1](docs/esperimento-e1-form-compatto-2026-10-16.md); variante solo nel banco di prova, qualità non stabilizzata; altra rappresentazione E1 da valutare prima di E2 |
| 17 ottobre 2026 | E1 compact-index-v2 approvato ed eseguito | 137 mirati e 2.279 backend passati, Ruff; input -13,31%; 1/3 analisi accettate, rifiuto JSON e troncamento; unico Word 21/60 | [Rapporto indice diretto](docs/esperimento-e1-index-2026-10-17.md); nessun retry o adozione; prossimo esperimento separato proposto, E2 non avviato |

### Scheda da copiare per i prossimi aggiornamenti

- **Data e attività:** da compilare.
- **Materiali prodotti/revisionati:** percorsi, versione e hash disponibili.
- **Cosa è pronto:** elementi P01–P13 e verifiche effettive.
- **Cosa manca o è dubbio:** problemi e decisioni aperte.
- **Modifiche ai dati/gold:** motivazione e nuova versione.
- **Prossimo passo:** risultato concreto da ottenere.

## 13. Indice delle nuove esecuzioni

Acquisita B0 il 16 ottobre con provider reale: analisi completa e continuazione
dei servizi applicativi su copie isolate, non browser/endpoint o ingestion.
Le prove e i limiti restano in [relazioni.md](relazioni.md) e
nell'[archivio](docs/benchmarks/README.md).

| Run / serie | Versione del caso | Modalità/configurazione | Stato | Esiti e limiti | Report completo |
|---|---|---|---|---|---|
| B0-01/02/03 | Minervino V1 | DeepSeek flash; thinking analisi attivo; copione USER su copie isolate | Tre analisi e tre Word parziali acquisiti | 23/17/22 valori conformi sui 60 target SOURCE, provenienza distinta; nessuno dei quattro argomenti USER chiesti; perimetro servizi | [Baseline B0](docs/baseline-minervino-b0-2026-10-16.md) |
| E1-01/02/03 | Minervino V1 | Stessa configurazione B0; FORM compact-v1 e sole istruzioni di lettura adattate | Tre analisi e tre Word acquisiti; nessuna adozione nella chat | Input -16,09%, 14/11/23 target conformi; cache e percorsi dialogici distinti; nessun argomento USER chiesto | [Esperimento E1](docs/esperimento-e1-form-compatto-2026-10-16.md) |
| Analisi storica 211598d4, eseguita dall'utente il 15 ottobre | Minervino + integrazione Company già caricata; non nuova fixture congelata | Diagnosi offline del 16 ottobre; V12 / deepseek-flash registrati | Acquisita e rivalidata | 21 SOURCE + 1 USER scritti; manca gold completo, nessuna accuratezza percentuale | [Diagnosi](docs/minervino-integrazione-2026-10-16.md) |
| E1INDEX-01/02/03 | Minervino V1 | Stessi input canonici B0; vista compact-index-v2 e istruzioni corrispondenti | Un rifiuto contratto, un troncamento, una analisi accettata e un Word | Input -13,31%; Word N/D / N/D / 21 su 60; tutti gli esiti e consumi conservati | [Indice diretto](docs/esperimento-e1-index-2026-10-17.md) |

## 14. Esperimenti E1/E2 proposti

Il [piano E1/E2](docs/piano-esperimenti-e1-e2.md) separa la rappresentazione
del FORM dal perimetro documentale usato per accelerare le prove.

| Esperimento | Confronto | Misura e limite |
|---|---|---|
| E1 — FORM compatto | B0 completo attuale contro completo compatto | Risorse e qualità globale; fonti, modello e criteri invariati |
| E2 — Estratti mirati | E1 compatto completo contro gruppi nella stessa vista, valutati sulle stesse destinazioni | Risparmio per ciclo e scostamenti locali; nessuna conclusione sulla completezza del modulo |

E1 compact-v1 e compact-index-v2 sono stati eseguiti dopo approvazione:
entrambi riducono input, nessuno sostiene ancora l'adozione. La seconda
variante ha due fallimenti su tre e un solo Word. Dettagli nei rapporti. E2 resta un
piano: prima fissare una vista compatta adeguata e il manifest dei gruppi.
Entrambe le varianti E2 si confrontano con il gold;
non basta che producano la stessa risposta. Fonte e disponibilità USER
rimangono costanti; gruppi, dipendenze e soglie si fissano prima dei risultati.
Registrare costo per gruppo e totale, con verifiche complete periodiche.
Fixture Minervino V1 e protocollo congelato restano invariati; gli estratti
sono materiali derivati separati e non introducono un motore a gruppi.
