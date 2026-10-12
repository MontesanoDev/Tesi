# Dialogo di compilazione V1

43 turni indipendenti, con domanda attiva e gold congelati **prima** delle
chiamate reali. I casi comprendono consenso, negazioni, cortesia, risposte
parziali/multiple, alternative, rinvio, pausa/ripresa, richieste documentali e
correzioni fuori dagli slot. Gli intent alternativi ammessi sono nel gold;
non si confrontano il wording della risposta o il rationale.

`contexts.json` contiene i checkpoint autoriali; `cases.json` contiene anche
le aspettative e NON entra nel prompt. Il modello riceve soltanto messaggio,
domanda, slot attivi e normale contratto di produzione. Destinatari/ID rimangono
del backend. Il Word è una fixture minima per eseguire realmente validazioni,
persistenza e scrittura USER: non è un altro bando né sostituisce Labirinto V1.
I file nel manifest sono immutabili; nuovi scenari richiedono una nuova versione.

Il runner usa il planner di produzione con DeepSeek reale, massimo 48 casi
seriali e due tentativi per caso (retry strutturale di produzione). Applica le
decisioni al dominio globale esistente in SQLite/storage temporanei. Dopo
ogni caso rilegge lo stato dal DB. Nessuna chiamata simulata, nuova analisi
globale o sintesi AI. Le risposte non associate a operazioni di compilazione
sono valutate per routing: non si eseguono RAG o nuove analisi DOCX.

Nel contesto `generate` esiste già un valore USER autoriale per il recapito;
nel contesto `generate_empty` non esiste alcun valore. Si eseguono realmente
gli export autorizzati e si conserva il report. Questo **non** misura retrieval
SOURCE, copertura dei campi, qualità della sintesi o una compilazione E2E nuova.
I checkpoint hanno audit preparati per il dialogo, non risultati di una nuova
analisi LLM. La fixture non contiene proposte fattuali SOURCE.

Scoring separato: intent, target FORM/SOURCE, associazione agli slot, valori
persistiti, pause, richieste di export e mutazioni inattese. CLARIFY non conta
come aggiornamento; UNKNOWN/SKIP/REFUSE sono rinvii USER, mai valori. Un rifiuto
backend di un valore corretto è un falso negativo, non un successo semantico.
Gli export bloccati dal dominio sono registrati separatamente dall'intento.

Da `backend/`, scegliendo un progetto con profilo DeepSeek reale configurato:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_dialogue.py \
  --project prova --output data/compilation-audit/dialogue-v1-20261012
```

Il DB corrente viene aperto soltanto in lettura per risolvere il profilo. Nessuna
chiave/DB entra nell'output. Il runner rifiuta directory output già esistenti.
Prompt/schema/raw/errori, stato prima/dopo, report, tempi e token sono conservati.
Le esecuzioni successive sono confrontabili a fixture e codice dichiarati,
senza selezionare le prove riuscite o reinterpretare il gold dopo gli output.
