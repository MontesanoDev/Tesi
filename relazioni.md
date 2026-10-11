# Relazioni — nuovo motore di compilazione

Registro richiesto dall'utente per ogni prova del nuovo motore. Aggiungere
esperimenti datati senza riscrivere gli esiti precedenti, inclusi i fallimenti.
Le acquisizioni complete rimangono nei bundle di `docs/benchmarks/`; questo
file raccoglie scopo, confronto, risultati e decisioni.

## Protocollo fisso

Fixture dedicata: [Modulo labirinto V1](demo-documents/benchmark-compilazione/v1/README.md),
[Word](demo-documents/benchmark-compilazione/v1/modulo-benchmark.docx),
[gold](demo-documents/benchmark-compilazione/v1/gold.json),
[manifest](demo-documents/benchmark-compilazione/v1/manifest.json).

Il gold è autoriale, indipendente dagli output, escluso dal prompt. Documenti,
fonti e risultati attesi congelati; ogni cambiamento di scenario crea una nuova
versione. Nessun caricamento nella KB locale e nessuna modifica di sessioni.
Il profilo reale serve esclusivamente a scegliere provider/modello.

Per ogni esperimento annotare:

1. Ipotesi e modifica confrontata, commit, versione fixture e hash input.
2. Provider/modello, thinking e budget; numero chiamate/retry e token/tempi.
3. Proposte grezze corrette/omesse/improprie, separate dall'esito dei gate.
4. Revisione dei rami omonimi, soggetto firmatario/direttore, condizioni,
   checkbox, fonte General KB/altro progetto, ambiguità e conflitti.
5. Chiamate USER/generazione DOCX realmente eseguite oppure non misurate.
6. Percorsi dei grezzi/bundle con hash, controlli software e limite residuo.

Valore/citazione corretti non equivalgono ad accettazione semantica. Il confronto
automatico è un ausilio limitato, non un secondo validator di produzione.
Il primo obiettivo è zero proposte fattuali improprie; la copertura va aumentata
senza abbassare provenance, isolamento o gestione dell'applicabilità.

## 11 ottobre 2026 — preparazione della fixture V1

Creato un solo DOCX con 55 posizioni: 44 testuali e 11 checkbox native.
Sette SOURCE: cinque Company KB, una progetto, una General KB distrattore;
una fonte di altro progetto è separata e usata solo nei test di isolamento.

Scenari: campi omonimi in rami alternativi, titoli senza outline Word,
condizioni annidate e ignote, dati societari/professionali, amministratore
distinto dal firmatario, sede coincidente, numero albo con numero estraneo,
RTI non determinato, ambiguità, conflitto, ISO dichiarata solo dal FORM,
firma protetta e spazio non compilabile. Aspettative: 22 valori supportati,
9 NA, 14 mancanti, 6 condizioni da chiarire, 1 ambiguo, 1 conflitto,
1 firma manuale e 1 spazio riservato. Sono obiettivi, non risultati del modello.

Esteso esclusivamente il runner di benchmark con `--fixture`; riusa catalogo,
prompt, schema, chiamata e validator correnti. Nessuna modifica del motore,
RAG, UI, parser, renderer o CompilationSession. La struttura semantica globale
rimane una proposta da discutere, non implementata con questa fixture.

Prima verifica conclusa: **209 test mirati passati** (21 nuovi più 188
regressioni di catalogo/proposta globale), Ruff sui file Python modificati.
Controllati copertura esatta del gold, byte riproducibili, scope, firme/email,
assenza del gold dal prompt e funzionamento del runner senza corpus DB.
Nei test del runner il provider è simulato: non sono risultati di DeepSeek.
Suite completa, controlli finali e baseline reale: ancora da completare.
Non considerare i risultati precedenti su domanda-partecipazione come nuove
misure su questo documento.
