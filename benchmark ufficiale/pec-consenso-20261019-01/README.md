# PEC Trapani: SOURCE e impegno procedurale separati

Intervento concluso il 20 ottobre 2026. [Rapporto](../../docs/pec-consenso-procedurale-2026-10-19.md), [controlli](ESITO.json), [file modificati](FILES-MODIFICATI.json).

**Prima:** dieci scritture, una PEC in una dichiarazione non autorizzata.
**Replay corretto:** nove scritture fattuali; dichiarazione vuota. Otto altre bozze identiche, Minervino V12 conserva 61 scritture.
**Nuova chat reale:** nove valori SOURCE, zero USER/checkbox, PEC aziendale leggibile e PEC dichiarativa vuota dopo rinvio USER. Nessuna scrittura indebita rilevata. Restano otto generalità omesse, civico mancante e una domanda societaria ripetuta, documentati senza correzioni durante il benchmark.

## Risultati leggibili

- [DOCX reale](e2e/trapani/bozza.docx) e [PDF](e2e/trapani/bozza.pdf).
- [Conversazione](e2e/trapani/dialogo.md), [report export](e2e/trapani/report-validazione.json), [valutazione campo per campo](e2e/trapani/valutazione-campi.json).
- [Ricevuta e verifica del consenso](e2e/trapani/verifica-consenso.json), [metriche](E2E-RISULTATO.json), [causa del duplicato](DIALOGO-RESIDUO.json).
- [Replay prima](REGRESSIONE-before.json), [dopo](REGRESSIONE-after.json), [XML](REGRESSIONE-XML.json); DOCX/PDF Trapani in `replay/before/trapani` e `replay/after/trapani`.
- [Diagnosi storica](DIAGNOSI-STORICA.json): il narratore vedeva la dichiarazione ma non chiedeva il consenso.
- [Protocollo congelato](PROTOCOLLO.json), `input/`: modello, parametri, prompt, SOURCE e hash del codice prima della nuova generazione.
- [Preservazione](PRESERVAZIONE.json), [backup](BACKUP.json), [verifica separata](VERIFICA-BACKUP.json).

49 nuovi test permanenti; 248 mirati e 2.793 backend PASS, Ruff PASS. Una sola nuova globale reale, dieci chiamate complessive, 109.176 token, 77,22 s HTTP sommati e 0,019564 USD stimati su tariffa congelata, non fattura. Nessuna nuova chiamata al riprendi.

La rilevazione copre impegni espliciti nella stessa clausola marcata, non ogni formulazione implicita o distribuita fra celle/paragrafi. I test di assenso positivo usano il provider simulato; la singola prova reale conserva il consenso UNKNOWN/SKIP dello scenario. Non adottata una baseline generale.

Grezzi in `backend/data/compilation-audit/pec-consenso-20261019-01/`. Backup completo separato, senza database, credenziali o file di chiave; include codice prima/dopo e ricostruzioni offline. Nessun commit/push.
