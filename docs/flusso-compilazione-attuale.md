# Come funziona oggi la compilazione — 10 ottobre 2026

Ricostruzione del codice attuale su `prune-backend`, HEAD `26976fa`, con le
modifiche locali preservate. Nessuna nuova prova AI, modifica del motore o dei
dati. Le misure citate appartengono ai benchmark già salvati nell'
[archivio](benchmarks/README.md).

## Percorso reale

1. `@` fornisce il document_id e il ruolo registrati. Il planner semantico
   `TurnPlan` riceve selezione, storico e sessione attiva; riconosce `compile`.
   Questo percorso non usa la normale risposta RAG per eseguire l'incarico.
2. Creazione/ripresa della CompilationSession per progetto/conversazione/form.
   Il backend legge l'originale, ne conserva hash/snapshot e usa il parser
   strutturale DOCX per le posizioni candidate. Il modulo della prova ha 279
   candidate: non equivalgono a 279 dati obbligatori o domande necessarie.
3. Il primo passo costruisce una mappa di sezioni/condizioni con `DocumentPlan`;
   `DocumentPlanReview` rilegge FORM e proposta, poi i controlli locali validano
   confini, anchor e scelte esclusive. Nessun valore viene compilato in questa
   fase. Nel benchmark DeepSeek il passo completo costa 117,61 s.
4. I passi successivi selezionano fino a 12 candidate, fino a sei nei retry.
   I batch automatici sono omogenei per fase e danno priorità a SOURCE per
   requirement già interpretati. Per nuove interpretazioni:
   `CandidateMeanings` propone significato/soggetto/condizione e `FormReview`
   li verifica; il backend controlla grounding e binding strutturale.
5. Per i requirement ammessi `CompilationSourcePlan` raggruppa le ricerche.
   Retrieval SOURCE, espansione e rilettura SQL preservano role/scope/progetto;
   vengono costruiti bucket ammessi per candidate. Il pool include evidenze
   di profilo e riutilizzabili secondo le regole esistenti, non soltanto il
   primo risultato della query.
6. `CandidateMatches` propone valori/prove; `SourceReview` controlla relazione,
   soggetto e contesto. I servizi pregressi possono richiedere anche
   `HistoricalServices`. Gate locali, condizioni e validator DOCX determinano
   i valori ammessi e gli stati. Fino a sei richieste AI nel passo completo;
   un retry SOURCE conserva l'interpretazione invece di riclassificare tutto.
7. Il backend persiste campi, versioni, tentativi e revisioni, sincronizza
   dipendenze/condizioni e prepara l'eventuale checkpoint. Il frontend legge
   `chat.auto_continue` e richiede il passo successivo in serie. Il ciclo è
   bounded a 36 passi/600 s, ogni passo ha timeout 180 s. Massimo due tentativi
   automatici per fase/candidate; nessun loop autonomo illimitato.
8. Finché esiste lavoro automatico ammesso nel budget, il primo campo irrisolto
   non causa una domanda. Al checkpoint i chiarimenti sono raggruppati fino a
   quattro slot coerenti, dando priorità a condizioni che interessano più field.
   PENDING non cercati e rifiuti tecnici non diventano automaticamente domande
   USER. I messaggi sono prevalentemente proiezioni/template dello stato.
9. Il messaggio libero successivo viene interpretato nel contesto degli slot
   attivi, associati dal backend. USER rimane distinto da SOURCE. Una conferma
   di condizione può riaprire la fase pertinente; SKIP/UNKNOWN differiscono,
   PAUSE conserva tutto. Non è un editor arbitrario di tutti i campi tramite
   qualsiasi frase libera. Le dipendenze ammesse possono propagare gli effetti.
10. Quando gli stati/blocchi consentono READY, la chat propone la generazione.
    La finalizzazione rilegge SOURCE correnti e originale, rivalida e chiama
    il renderer esistente. L'iterazione modifica lo stato, mai progressivamente
    il Word. Un export incompleto richiede una richiesta esplicita.

## Perché la UX resta poco naturale

- **Attesa iniziale:** due letture AI del modulo prima dei valori. Nel campione
  DeepSeek quasi due minuti, prima del primo batch utile.
- **Unità di lavoro:** il dominio ruota attorno ai candidate fisici. Esistono
  raggruppamento, riuso di evidenze e propagazione delle condizioni, ma non un
  unico catalogo di fatti semantici che governi tutte le destinazioni.
- **Decisioni distribuite:** classificatore, review FORM, piano SOURCE, matcher,
  review SOURCE e gate devono restare coerenti su soggetto/condizione/proprietà.
  L'interruzione di una fase impedisce quelle successive; un dato presente può
  restare irrisolto per rifiuti conservativi o per copertura, non per assenza.
- **Visione parziale:** la mappa iniziale è globale ma la risoluzione è locale
  ai batch. Relazioni/esclusioni sono riutilizzate soltanto quando grounded e
  compatibili; non si assume che una forma giuridica determini partecipazione,
  firmatario o tutte le qualificazioni. Interpretazioni incoerenti o incomplete
  possono frammentare i gruppi e produrre chiarimenti ripetuti.
- **Dialogo derivato dalla coda:** gli slot raggruppano esiti di candidate e
  condizioni verificate. Non costituiscono ancora un piano globale dei pochi
  fatti mancanti necessari per completare i rami pertinenti. I controlli delle
  risposte sono affidabili proprio perché circoscritti agli slot attivi.
- **Continuazione legata al frontend:** lo stato è nel DB ma è la pagina a
  richiedere i passi automatici. Chiuderla interrompe la sequenza dei nuovi
  passi; il lease consente recupero. La persistenza non è una coda server autonoma.

Nel benchmark recente, sette chiamate generative complessive producono cinque
RESOLVED/SOURCE dopo 151,25 s; restano 267 candidate non analizzati. Con Gemma
la prima classificazione ometteva `semantic`: parsing formalmente valido,
interpretazioni tutte respinte e SOURCE mai raggiunta. Sono esempi misurati
di costi e falsi negativi, non una prova che ogni campo fallisca o che la
compilazione iterativa sia impossibile con questa architettura.

I gate proteggono da diversi errori; i reviewer AI non costituiscono una prova
matematica di correttezza. Per sostituire il percorso servono un contratto
verificabile, casi negativi/annotati e controllo delle collocazioni reali nel
DOCX, descritti nella [proposta bottom-up](strategia-bottom-up-compilazione.md).

Punti di riferimento del codice: `main.py`, `intents.py`, `compilation_chat.py`,
`compilation_sessions.py`, `compilation_document_plan.py`,
`compilation_session_resolution.py`, `compilation_clarifications.py` e
`frontend/src/hooks/useCompilationSession.ts`.
