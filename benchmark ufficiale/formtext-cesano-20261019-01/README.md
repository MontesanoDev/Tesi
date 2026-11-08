# Cesano FORMTEXT: regressione ed E2E reale

**Supporto strutturale PASS; qualità della nuova compilazione FAIL.**
La funzionalità complessiva non è dichiarata chiusa.

[Rapporto completo](../../docs/regressione-formtext-e2e-2026-10-19.md),
[controlli PASS/FAIL](CONTROLLI-PASS-FAIL.json),
[elenco dei file modificati](FILES-MODIFICATI.json).

- [DOCX esportato dalla chat](cesano/bozza.docx)
- [PDF della stessa bozza](cesano/bozza.pdf)
- [Dialogo](cesano/dialogo.md)
- [Metriche](cesano/metriche.json)
- [Traccia dei venti campi](cesano/traccia-20-campi.json)
- [Diagnosi dei residui](cesano/diagnosi-residui.json)
- [Verifica fisica](cesano/verifica-fisica.json)
- [Input reale](cesano/input-LLM.json) e [risposta globale](cesano/risposta-globale.json)

Gli otto valori sono scritti correttamente come posizioni e sono leggibili.
Una sola corrispondenza SOURCE/soggetto/campo è dimostrata; sette dati
aziendali nel blocco del sottoscrittore richiedono revisione dell'associazione.
Tre dati personali disponibili sono omessi. Checkbox societaria non selezionata;
data UNKNOWN conservata. Il DOCX è l'export reale, senza rimozioni manuali.

La directory regressione contiene i sei export ricostruiti e PDF nuovi.
La directory controllo-20 è una prova meccanica con sentinella, non una
domanda valida: esercita anche rami alternativi e la data. I due dati CCIAA
invisibili di CRAA e l'errore PEC Trapani sono difetti precedenti conservati.

2.682 test backend, 258 mirati e Ruff passati. Una globale nuova e dieci
chiamate totali, stessi modello/prompt/22 SOURCE e scenario; zero retry di
qualità. Nessuna correzione applicativa durante questa fase o nuova globale
per migliorare il risultato.

[Backup](audit-completo.tar.gz), [descrittore/hash](BACKUP.json),
[verifica del bundle estratto](VERIFICA-BACKUP.json).
Il backup include audit, browser, codice e fixture; esclude database privati
e credenziali. Il verificatore ricostruisce anche le scritture non certificate:
la riproducibilità non ne dimostra la correttezza.
