# Sintesi: preservare il contesto dei ruoli

## Diagnosi e protocollo congelato

Intervento autorizzato sulla sintesi conversazionale del motore globale V10.
Non cambia retrieval, classificazione dei candidate, parser, renderer o UI.

L'audit conserva già soggetto e prova SOURCE della relazione persona–ruolo.
Il JSON di `compilation_global_dialogue.model_context` perde tale prova: include
il ruolo richiesto dal FORM e solo gli estratti dei singoli valori (nome,
qualifica, Ordine, numero). La revisione non può quindi distinguere bene ruoli
attuali, cessati o destinazioni differenti. Non occorre aggiungere chiamate.

**Correzione della diagnosi precedente:** il replay del gruppo aveva ricostruito
un catalogo grezzo da `initial_state`, senza `anchor_paragraph_ids`, invece del
catalogo arricchito da `build_global_input` persistito dall'analisi reale. Tutti
i `form_context` della sintesi di quel replay erano vuoti. Il risultato 8/12
resta archiviato e il criterio fallito resta tale, ma non costituisce da solo
prova di regressione applicativa. Il runner ora usa il catalogo corretto.

Congelati prima delle nuove API sette casi in
`demo-documents/benchmark-sintesi/v1/`, manifest SHA256, nessun gold nel prompt:
Catanzaro con/senza conferme, Labirinto con risposte già acquisite, due incarichi
generici attuali/uno cessato/entrambi cessati/ruolo differente. Audit reali
precedenti rivalidati e proposte autoriali per i controesempi, non nuove analisi
SOURCE. Un'unica chiamata reale DeepSeek Flash per caso/serie, massimo sette,
timeout 45s/output2048, nessun retry o selezione degli output. Il catalogo include
gli stessi anchor dell'applicazione. Il benchmark non scrive sessioni live.

Runner: `docs/benchmarks/benchmark_narration_roles.py`; replay HTTP isolato:
`docs/benchmarks/replay-group-confirmation.py --output ...`.

La soluzione prevista conserva in un contesto condiviso bounded il soggetto,
il ruolo richiesto e gli estratti SOURCE della relazione già groundata, con
riferimenti per proposta. La sintesi resta soltanto un gate di esclusione:
non inventa valori né promuove proposte a RESOLVED. I risultati e i limiti della
misura vengono aggiunti dopo le serie prima/dopo.
