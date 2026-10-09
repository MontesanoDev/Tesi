# Diagnosi della compilazione Trapani Green — 9 ottobre 2026

La domanda duplicata è riproducibile sul codice corrente. È un difetto nella
costruzione dell'identità dei chiarimenti, ma la scarsa compilazione ha anche
cause nella rappresentazione dei rami e nella selezione delle evidenze.
La raccomandazione è riorganizzare il nucleo semantico della compilazione,
conservando persistenza, API, isolamento e writer DOCX. Questa è una proposta:
in questo intervento non è stata implementata una nuova architettura.

## Caso verificato e perimetro

- Sessione `81bc4d657ff44bdbac538c22d4b53ac5`, conversazione
  `conv-202292d12f3b4e94`, modulo 29 `manifestazione-interesse.docx`.
- Revisione 59, `WAITING_FOR_USER`; originale SHA-256
  `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`.
- Il solo turno utente è «compila». Il modello configurato è già
  `deepseek-flash`; non si tratta di una sessione eseguita con un piccolo modello locale.
- 23 passi automatici, dalle 10:42:43 alle 10:47:45 UTC: 115 posizioni candidate,
  5 RESOLVED, 47 MISSING, 38 AMBIGUOUS, 25 PENDING. Le posizioni includono
  alternative, righe ripetute e firme: **115 non è il numero dei dati obbligatori**.
- Diagnosi sul database in sola lettura, replay su copie in memoria e quattro
  chiamate DeepSeek su tre campi. Nessuna modifica a sessioni, configurazioni AI,
  fonti o codice applicativo; nessuna generazione di DOCX, migrazione o reindicizzazione.

## Perché compaiono due domande uguali

La tabella dello Studio Associato contiene 24 celle, governate dalla stessa
frase in `paragraph:19`. Le interpretazioni salvate hanno due varianti:

| Celle | `entity` | `requirement.person_role` | Condizione/sezione |
|---|---|---|---|
| 18 | `person` | `professionista associato` | Identiche |
| 6 | `person` | stringa vuota | Identiche |

[`owner()`](../backend/app/compilation_conditions.py) include il ruolo del
**dato da inserire** nell'identità del soggetto della **condizione da decidere**.
[`pending_slots()`](../backend/app/compilation_clarifications.py) produce quindi
due slot. Il renderer mostra solo la condizione e nasconde la differenza che
ha separato gli slot: il risultato è precisamente il messaggio segnalato.

Il replay con `attach_form_dependencies()` e `synchronize()` sul codice corrente
restituisce ancora le due domande. In un esperimento causale, uniformare soltanto
il ruolo delle 24 celle su una copia in memoria produce un unico slot da 24 celle.
Questa manipolazione diagnostica non è una correzione applicativa: cancellare
genericamente i ruoli o deduplicare per solo testo potrebbe unire domande su
persone, membri o pratiche diverse.

La priorità usa il numero di celle coinvolte (`impact`): una tabella con tante
righe vuote viene prima di domande più utili sulla pratica. Il problema riguarda
quindi identità e priorità della domanda, oltre alla sua formulazione.

## Perché continua a chiedere dello Studio Associato

Il modulo introduce un blocco «IN QUALITA’ DI», seguito da «eliminare le opzioni
non pertinenti». I rami sono paragrafi non numerati: professionista singolo,
associato, società di professionisti, società di ingegneria, prestatore estero.

Il riconoscitore deterministico in
[`compilation_form_conditions.py`](../backend/app/compilation_form_conditions.py)
richiede intestazioni numerate come `5.a)` e la formula «da compilare in caso di».
Era stato aggiunto per la struttura osservata a Catanzaro: su Trapani assegna
**zero dipendenze FORM su 115 candidate**. Anche l'altro percorso di identità
condivisa richiede «dati identificativi da compilare in caso di». Tutte le
interpretazioni semantiche salvate hanno inoltre `exclusive_group_id` vuoto.

Il fatto SOURCE «Società di Ingegneria» viene riusato tra i campi del paragrafo 75,
ma manca una rappresentazione comune delle alternative del blocco. Resta quindi
aperta una domanda autonoma per ciascun altro ramo.

La soluzione non consiste nel dedurre tutte le esclusioni dalla sola S.r.l.:
tipologia aziendale, persona che firma, poteri e modalità di partecipazione
restano fatti diversi. Occorre rappresentare e verificare le relazioni del
modulo prima di generare i chiarimenti. Qui il fatto relativo alla tipologia è
già disponibile; l'eventuale scelta del firmatario deve essere chiesta con il
suo significato, senza ripetere una frase mista su tipo e rappresentanza.

## Perché chiede dati della sede già presenti

I campi `p75.s1`, `p75.s2`, `p75.s3` chiedono via, comune e CAP. La loro copertura
SOURCE finale è `[91, -2, -5, 90]`: due frammenti dell'avviso e due frammenti
aziendali che non contengono la sede. Il frammento della visura `-1` contiene
l'intero indirizzo ed è ammesso per la provincia `p75.s4`.

La revisione **46** prova che il modello aveva già proposto per `p75.s1`:

> Via Giovanni Amendola 172/C

con estratto dalla sede legale della visura. Il backend scarta il supporto con
`SOURCE non ammessa per questo candidate`; nello stesso passaggio accetta `BA`
per la provincia usando la stessa riga della stessa fonte. Alla revisione 48,
la nuova ricerca per la via restituisce ancora i quattro frammenti insufficienti
e il campo resta MISSING senza errori. Lo scheduler non ritenta automaticamente
un MISSING senza errori solo perché un altro campo dispone della fonte utile.

Tre meccanismi contribuiscono al problema:

1. `compilation_queries()` ordina le etichette per numero di parole. Le etichette
   lunghe con underscore contano come una parola e, a parità, precedono i sinonimi.
   Nelle ricerche effettive rimangono descrittori come
   `indirizzo_sede_societa_ingegneria`. Per gruppi di più campi, la lista delle
   alternative costruita dalla funzione non viene usata.
2. Il limite di quattro frammenti è usato sia per unire gli anchor sia per
   espandere i vicini. Se i quattro posti sono occupati, l'espansione ritorna
   subito: i frammenti adiacenti `-1` e `-6`, entrambi utili alla sede, restano fuori.
3. La condivisione fra gruppi usa `company_property()`, che richiede un'intestazione
   con `:` e una corrispondenza di etichetta. La riga PDF
   `SEDE LEGALE E OPERATIVA ...` non ha i due punti. Il frammento è quindi negato
   agli altri campi anche quando è già nel contesto del medesimo passo.

La cronologia prova il rifiuto della fonte utile; non attribuisce separatamente
un peso causale al ranking vettoriale e alla formulazione delle query. La prova
seguente isola la disponibilità delle evidenze, senza rieseguire il retrieval.

## Prova reale DeepSeek

Stessi tre campi della v59, interpretazioni/applicabilità già salvate, prompt e
validatori applicativi. Modello `deepseek-flash`, temperatura 0,1 e thinking
disabilitato come nel resolver ordinario. Sono state eseguite due prove, ognuna
con matcher e revisore SOURCE, per **quattro chiamate riuscite**.

| Evidenze ammesse | Via | Comune | CAP |
|---|---|---|---|
| Quattro frammenti della sessione | MISSING | MISSING | MISSING |
| Stessi quattro + frammento esistente `-1` | Via Giovanni Amendola 172/C | Bari | 70126 |

Nella seconda prova i tre valori superano revisione semantica e validazione
ordinaria e risultano RESOLVED sulle copie. Il modello propone anche il nome
della società come secondo supporto per l'indirizzo: il revisore lo respinge;
il relativo errore resta registrato nel campo. Anche la prima prova contiene
supporti di applicabilità non letterali respinti. **Non sono tre campi esportati
in una sessione completata**, e la prova non dimostra affidabilità generale del
modello. Dimostra che tre omissioni sono recuperabili fornendo l'evidenza corretta
senza cambiare modello o allentare i controlli.

Il primo tentativo nel sandbox è fallito nel trasporto e il processo è stato
interrotto; la prova riuscita è stata rilanciata con accesso alla rete autorizzato.
Gli output conservati sono risposte strutturate parsate, non catture HTTP grezze.
Non sono stati misurati costo o token delle chiamate.

## Altri limiti che peggiorano l'esperienza

- «Mi servono ancora 2 chiarimenti» conta soltanto gli slot attivi. La v59 ha
  **54 slot potenziali**, inclusi duplicati e rami da chiarire, oltre ai 25
  candidate ancora senza interpretazione accettata. Non sono 54 domande tutte
  necessarie; non sono neppure due soli ostacoli al completamento.
- «5 informazioni» conta celle RESOLVED, compresa la PEC in due posizioni:
  i valori distinti sono quattro. Questo contatore non misura fatti distinti
  acquisiti né percentuale di completamento del documento.
- I 25 PENDING hanno esaurito tentativi di interpretazione, con errori di
  estratto/anchor, confusione persona-organizzazione o schema. Non sono tutti
  dati che l'utente deve fornire. Tra questi c'è il telefono della società.
- Le 30 celle della tabella di esperienze diventano richieste separate per
  campo. Occorre prima stabilire quali prestazioni documentate inserire e quante
  righe usare. Sei proposte di dati della procedura corrente sono state respinte
  dal controllo sui servizi pregressi: rimuovere questi controlli peggiorerebbe
  la correttezza anche se aumentasse il numero di campi riempiti.

## Alternative e intervento raccomandato

| Scelta | Beneficio | Limite/costo |
|---|---|---|
| Correggere solo il duplicato e le query | Intervento circoscritto, utile come regressione immediata | Non risolve dipendenze, righe ripetute e domande su dati recuperabili |
| Riorganizzare il nucleo semantico, riusando il backend esistente | Affronta le cause osservate conservando storage, versioni, API e writer | Richiede un contratto verificabile e confronti sui tre moduli |
| Riscrivere tutto il backend | Permette un ridisegno completo | Nessuna evidenza che FastAPI, SQLite o il writer causino questi difetti; rischio di perdere protezioni già funzionanti |

Raccomandata la seconda opzione, da concordare prima dell'implementazione:

1. **Mappa coerente del modulo.** Sezioni, soggetti, condizioni, alternative e
   tabelle ripetibili interpretati insieme, con ancoraggi all'originale. Il soggetto
   di una condizione deve essere distinto dal soggetto del dato della singola cella.
   Questo non richiede una sola enorme chiamata per compilare tutto il documento.
2. **Fatti riutilizzabili nella sessione.** Ogni fatto mantiene soggetto, proprietà,
   ambito, fonte e stato di verifica; più celle possono riferirsi allo stesso fatto.
   La divisione delle ricerche limita il lavoro, senza rendere una fonte pertinente
   inutilizzabile altrove. Riammissibilità e rilettura devono mantenere isolamento
   di progetto, ruolo SOURCE, soggetto, proprietà e validazione.
3. **Domande sui fatti realmente irrisolti.** Prima risolvere i rami e cercare nelle
   evidenze disponibili; poi chiedere soltanto scelte/dati necessari. Per esempio,
   se la firma non è designata: «Chi sottoscrive questa domanda per Mapi Ingegneria
   e con quale titolo?». Un'identità stabile deve consentire il riuso della risposta
   su tutte le celle dipendenti, distinguendo persone e qualificatori diversi.
4. **Esiti espliciti.** Distinguere dato assente, ricerca insufficiente,
   interpretazione fallita e scelta dell'utente. Non convertire automaticamente
   un limite del motore in una domanda anagrafica.

Il prototipo globale già presente resta separato: i report precedenti non
dimostrano che sostituire il flusso corrente con quella chiamata unica risolva
questi problemi. Cambiare modello può ridurre alcune incongruenze, ma non corregge
la chiave dei chiarimenti né il rifiuto backend della fonte pertinente.

La verifica della nuova soluzione dovrebbe usare Catanzaro, Minervino e Trapani,
con annotazione di valori/prove attesi e domande effettivamente necessarie.
Criteri: nessun duplicato sullo stesso fatto, nessun trasferimento di dati fra
soggetti, sede riutilizzabile nei suoi componenti, nessun dato corrente usato come
esperienza pregressa, errori tecnici distinti da dati mancanti, refresh e risposte
USER coerenti. Test con provider simulati e valutazioni con provider reale vanno
riportati separatamente.

## Artefatti e verifiche eseguite

Audit locale ignorato in
[`backend/data/compilation-audit/trapani-diagnosis-20261009/`](../backend/data/compilation-audit/trapani-diagnosis-20261009/):
script `diagnose.py`, snapshot JSON v59, paragrafi dell'originale, revisioni
selezionate, richieste/risposte della prova, `offline-summary.json`,
`live-summary.json` e `preservation.json`.

Replay del duplicato e controfattuale sul ruolo eseguiti; prova reale dei tre
campi completata. Confronto prima/dopo identico per dieci tabelle applicative,
incluse sessioni, revisioni, conversazioni, originali BLOB, fonti e compilazioni.
Nessuna suite software rieseguita, perché il codice applicativo non è stato
modificato. Modifiche pendenti preesistenti conservate, nessun commit/push.
