# Strategia bottom-up della compilazione — proposta del 10 ottobre 2026

Stato: **direzione a chiamata unica confermata dall'utente**; contratto e dettagli
progettuali da comunicare prima del codice. Nessun nuovo motore implementato.
La direzione a chiamata unica è già scelta nello storico; questo documento
propone contratto, ordine di lavoro e criteri per valutarla. Conservare la demo
V1 e recuperare prima il lavoro non pubblicato di `Tesi-one-shot`, se disponibile.
Non rifare inconsapevolmente il prototipo. L'utente ha richiesto prima un
checkpoint del sistema attuale su GitHub, poi sviluppo graduale e misurato.

## Obiettivo e base misurata

Ridurre passaggi AI, rappresentazioni duplicate e domande ripetute mantenendo
correttezza delle scritture, tracciabilità e isolamento. La correttezza prevale
su velocità e numero di celle riempite.

Il benchmark V1 DeepSeek recente impiega 151,25 s per mappa e primi 12 candidate,
con cinque RESOLVED/SOURCE. La sola mappa/review costa 117,61 s. Il precedente
esperimento globale riportava oltre 213.000 token di input e valori/domande
ancora incompleti: una sola chiamata non garantisce velocità o correttezza.
I risultati storici non sono benchmark appena ripetuti.

Riferimenti: [misure recenti](diagnosi-latenza-compilazione-2026-10-10.md),
[esperimento globale storico](global-compilation-experiment.md),
[baseline](baseline-demo.md), [archivio benchmark](benchmarks/README.md).

## Parti da riutilizzare

- Parser DOCX e ID/posizioni strutturali autoritativi; originali immutabili.
- Renderer, validazioni locali utili, controllo SOURCE correnti prima dell'export.
- CompilationSession persistente, versioni/concorrenza, API e download.
- Chat, routing semantico condiviso, stop/ripresa e provenance USER.
- Filtri di progetto/role/scope e FTS5/Qdrant già esistenti.

La modifica riguarda il nucleo della risoluzione della compilazione. Non
richiede un nuovo motore RAG della chat o una nuova interfaccia.

## 1. Partire dal contratto delle scritture

Definire prima i casi ammessi e i casi da rifiutare, riusando i gate esistenti.
Una scrittura automatica richiede:

1. Candidate reale appartenente all'originale/hash della sessione.
2. Requisito e contesto grounded nel FORM.
3. SOURCE ammessa, rileggibile, con riferimento e span del valore/prova.
4. Proprietà, soggetto, ruolo e relazione temporale coerenti con il campo.
5. Condizione applicabile verificata; condizione sconosciuta resta aperta.
6. Nessun conflitto irrisolto e validatore DOCX superato.

USER ha un canale distinto e non diventa SOURCE. La condizione falsa non
produce un valore fattuale. Gli stati e la completezza vengono calcolati dal
backend. Una posizione vuota non è automaticamente un dato obbligatorio.

Il matching letterale non dimostra l'associazione semantica: «8421» può essere
un numero qualsiasi; il nome di un direttore non prova chi firmerà la domanda.
Una proprietà corretta nel ramo sbagliato è comunque una scrittura errata.
La rimozione dei reviewer AI deve essere subordinata a un'alternativa verificata
per queste relazioni. Dove i controlli non possono stabilirle, conservare REVIEW/
AMBIGUOUS o un chiarimento; non accettare la sola autodichiarazione del modello.

## 2. Rappresentare una volta i dati necessari

Proposta di dominio minimo, con nomi/schema ancora da definire:

- **Catalogo FORM**: ordine, testo, sezioni, candidate e relazioni strutturali;
  condizioni e soggetti proposti devono avere anchor nel documento.
- **Catalogo delle prove**: testo SOURCE con ID, file, chunk/span, progetto,
  scope/category reali e hash. USER separato con messaggio/revisione.
- **Fatti proposti e verificati**: soggetto, proprietà, valore, relazione e
  prove. La stessa chiamata può proporli; non sono veri perché strutturati.
- **Assegnazioni**: candidate → fatto/prova, condizione e verdetto backend.

Un fatto validato può sostenere più posizioni dello stesso soggetto/proprietà;
ogni destinazione mantiene la propria verifica di applicabilità. Non creare
un fatto globale «numero albo» privo del titolare e del ruolo.

Compattare senza perdere significato: deduplicare contesti comuni, riferire
SOURCE e sezioni tramite ID, conservare ordine delle righe, titoli e qualificatori.
Evitare copie del medesimo paragrafo per ciascuna cella. Non sostituire le fonti
con riassunti LLM non verificabili e non nascondere testo escluso dal budget.

## 3. Una proposta globale, controlli locali

Flusso proposto:

```text
originale → catalogo strutturale
         + SOURCE ammesse e USER separati
         → una proposta strutturata
         → validazione locale e controllo coverage
         → aggiornamento atomico della sessione
         → chiarimenti necessari oppure export esistente
```

Una chiamata per la proposta iniziale della compilazione; il normale routing e
le risposte successive della chat sono chiamate distinte da misurare esplicitamente.
Niente catena di classificatore/planner/matcher/reviewer per ogni gruppo.

Il modello propone riferimenti/fatti/associazioni e questioni aperte. Evitare
contatori, testi FORM e prove duplicate nell'output; conteggi/status sessione
appartengono al backend. Controllare gli ID effettivi e le omissioni: non
fidarsi di un `coverage_count` dichiarato dal modello.

Schema globale invalido, troncamento o coverage incompleta non autorizzano
scritture automatiche. Proposta locale invalida lascia aperto quel candidate;
un piano strutturalmente valido può conservare le altre assegnazioni validate.
Commit transazionale vincolato a versione/hash: un input USER concorrente vince
senza essere sovrascritto da una proposta vecchia.

Per la prima milestone usare un corpus controllato che entra integralmente nel
budget e dichiararne la copertura. L'accesso a KB grandi richiederà una scelta
esplicita del contesto con il retrieval esistente e budget tracciato: non
promettere una chiamata totale né completezza arbitraria con corpus illimitati.
Un campo non cercato per limite non diventa «dato assente».

## 4. Iterare sui fatti e sulle condizioni mancanti

Riutilizzare sessione e chiarimenti conversazionali. Una domanda sulla forma
di partecipazione può sbloccare più sezioni; lo stesso dato ripetuto non deve
produrre altrettante domande. Gruppi piccoli, provenienze e rinvii persistiti.

Una risposta USER aggiorna il fatto/condizione pertinente e soltanto le
assegnazioni dipendenti. Non ripetere tutta l'analisi e non propagare il dato
ad altri soggetti. UNKNOWN, SKIP, PAUSE e conflitti restano distinguibili.
READY continua a non certificare obblighi/allegati o correttezza amministrativa
completa: i candidate strutturali non coprono necessariamente tutto il modulo.

## 5. Test prima della sostituzione

Preparare un insieme annotato e revisionato manualmente: candidate, requisito,
soggetto, condizione, valore ammesso, prova precisa e motivi di non risoluzione.
Partire dai cinque campi SOURCE misurati e dal direttore tecnico/albo; includere
moduli Catanzaro, Minervino e Trapani e casi indipendenti per evitare overfitting.

- **Test software**: validator, mapping, dipendenze, conflitti, isolamento e
  versioni con dati temporanei e output controllati. Risposte AI simulate qui
  verificano il software, non la comprensione semantica del modello.
- **Test negativi**: numero di un'altra persona, nome nel ramo errato, dichiarazione
  FORM scambiata per possesso, SOURCE generica/esempio, requisito inventato da USER,
  evento futuro scambiato per servizio eseguito, fonte eliminata/cambiata,
  ID duplicati/omessi e output troncato. Nessuna scrittura consentita.
- **Replay offline**: stessa risposta grezza prima/dopo modifiche ai validator,
  confrontando accettazioni/rifiuti. Non correggere i gate per accettare il
  benchmark; ogni cambiamento richiede motivazione e un controesempio negativo.
- **Benchmark reali**: codice congelato, sessioni pulite, profili/corpus/versioni
  registrati. Nessun USER per dati presenti nelle fonti. Ripetizioni e un
  documento non usato per lo sviluppo; misurare variabilità, non un solo run.
- **Export reale**: confrontare stato e XML delle copie generate. Ogni valore
  deve essere scritto nella posizione prevista; nessuna modifica alle altre
  posizioni/parti, originale invariato, unresolved non inventati.

Metriche separate: scritture erronee, valori corretti risolti, falsi negativi,
condizioni valutate, candidate non analizzati, domande/turni USER, durata, chiamate,
token e dimensioni dei payload. La riduzione delle domande non compensa un errore
di compilazione; un valore corretto nel ramo errato conta come errore.

Criterio di promozione proposto: zero scritture errate nel corpus verificato,
nessuna regressione dei valori/provenienze già dimostrati, incertezze esplicite,
export coerente e vantaggio misurato di complessità/tempi. È evidenza limitata
al corpus, non garanzia universale di correttezza del modello.

## 6. Potare dopo aver dimostrato il nuovo percorso

Solo dopo la validazione collegare l'adapter alla CompilationSession/chat.
Poi rimuovere il resolver precedente, reviewer e contatori/retry per fase
divenuti inutili; unificare le rappresentazioni duplicate e gli snapshot
ridondanti preservando la ricostruzione dell'audit e la compatibilità necessaria.
Non mantenere due motori attivi con fallback silenzioso. Conservare un
riferimento Git della demo per il ripristino, senza trasferire dati privati.

Prima milestone proposta: una risoluzione completa e verificabile su fixture,
con report campo per campo e confronto DOCX reale, fuori dalla UI di produzione.
Questa proposta non autorizza ancora nuovi benchmark a pagamento o modifiche
alla demo: prima definire il contratto e recuperare/valutare il prototipo esistente.
