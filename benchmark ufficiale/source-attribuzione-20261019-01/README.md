# Attribuzione SOURCE → soggetto → campo

Correzione mirata e regressione **PASS**. Prova casuale reale Catanzaro:
bozza parziale con **15 valori leggibili, nessuna attribuzione indebita
rilevata**, ma omissioni, checkbox vuote e dialogo ridondante conservati.
Non è una certificazione generale né un'adozione della baseline.

- [Rapporto completo](../../docs/attribuzione-source-soggetto-campo-2026-10-19.md)
- [Controlli PASS/FAIL](CONTROLLI-PASS-FAIL.json)
- [Sette casi Cesano con prove e motivi](CESANO-SETTE-CASI.json)
- Cesano: [DOCX prima](replay/cesano-reale-8/prima.docx),
  [PDF prima](replay/cesano-reale-8/prima.pdf),
  [DOCX dopo](replay/cesano-reale-8/bozza.docx),
  [PDF dopo](replay/cesano-reale-8/bozza.pdf).
  Il prima conserva sette attribuzioni non dimostrate; il dopo le lascia vuote.
- [Regressione dei sei documenti e Minervino V12 a 61](regressione.json)
- [Estrazione: Catanzaro, seed 13243375443350163391](ESTRAZIONE.json)
- [Configurazione e protocollo prima della prova](PROTOCOLLO.json),
  [snapshot del codice](VERSIONE.json)
- Catanzaro reale: [DOCX](e2e/catanzaro/bozza.docx),
  [PDF](e2e/catanzaro/bozza.pdf), [dialogo](e2e/catanzaro/dialogo.md),
  [verifica fisica](e2e/catanzaro/verifica-fisica.json),
  [tutti i campi](e2e/catanzaro/valutazione-campi.json),
  [omissioni](e2e/catanzaro/omissioni-SOURCE.json),
  [metriche](E2E-RISULTATO.json).
- [Elenco preciso dei file modificati/aggiunti](FILES-MODIFICATI.json)
- [Conservazione dello stato precedente](CONSERVAZIONE.json)
- [Backup separato con hash](BACKUP.json),
  [verifica indipendente del backup](VERIFICA-BACKUP.json).

Grezzi in `backend/data/compilation-audit/source-attribuzione-20261019-01/`:
richieste/risposte provider, transizioni, dialogo, browser trace/video,
test, input dei replay e snapshot applicativo. Il backup distribuibile comprende
questi artefatti e la consegna, senza database privato o chiavi. Il codice
applicativo resta congelato per tutta la prova finale; nessun retry di qualità.

Il nuovo veto riconosce soggetti espliciti in paragrafi inline, non ogni
possibile contesto tabellare o prosa. Non riduce i controlli preesistenti e non
rende TRUE condizioni UNKNOWN. Nessun commit/push.
