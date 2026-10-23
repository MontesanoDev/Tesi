# V12 — tre compilazioni reali per valutare una possibile baseline

Valutazione del 21 ottobre 2026, conclusa senza modificare il codice applicativo. Stato: **PROPOSED_NOT_ADOPTED**. La raccomandazione riguarda un riferimento sperimentale per bozze parziali; la decisione di adozione resta all'utente.

[Rapporto comparativo](../../docs/valutazione-baseline-v12-2026-10-21.md) · [Misure](CONFRONTO.json) · [Identità della candidata](CANDIDATO-BASELINE.json).

| Prova reale indipendente | Documento esportato | Rendering verificato | Testi / booleani |
|---|---|---|---:|
| Minervino | [DOCX](trials/minervino/bozza.docx) | [PDF](trials/minervino/render/bozza.pdf) | 43 / 0 |
| Cesano | [DOCX](trials/cesano/bozza.docx) | [PDF](trials/cesano/render/bozza.pdf) | 4 / 6 |
| CRAA | [DOCX](trials/craa/bozza.docx) | [PDF](trials/craa/render/bozza.pdf) | 7 / 0 |

Tre nuove sessioni e risposte globali reali; nessun retry o sostituzione. Totale: 28 chiamate, 397.982 token, costo a tariffa stimato 0,086193018 USD. Revisione documentale di 54 testi e sei booleani: zero scritture non dimostrate osservate. Le 17 omissioni fattuali e una scelta USER omessa impediscono di presentare il sistema come compilatore completo; un altro campo è aperto per il budget preregistrato del dialogo. Non è una stima statistica di accuratezza.

## Protocollo e prove

- [Selezione preventiva](SELEZIONE.json): due strati strutturali fissati e un solo sorteggio dal pool residuo, nessuna ripesca.
- [Protocollo preregistrato](PROTOCOLLO.json): SOURCE identiche, scenario per pratica, massimo due risposte agli slot attivi, export parziale esplicito.
- `input/`: prompt, parametri, SOURCE complete e originali, tariffe; `before/`: codice e documentazione iniziali, comprese le modifiche locali.
- `trials/<documento>/`: originale, input e risposta globale nuovi, dialogo, stato persistito finale, report di export, scritture verificate, classificazione di tutte le destinazioni, controlli fisici, DOCX, PDF e campioni visivi.
- Grezzo: `backend/data/compilation-audit/baseline-v12-20261021-01/`, incluso nel backup con richieste/risposte e usage di ogni chiamata, revisioni, download, trace/video e script. Non sono incluse credenziali o database privati.
- [Verifiche conclusive](VERIFICHE-FINALI.json): 119 hash applicativi invariati, tre nuove analisi, scenario e richieste conformi, download ordinari.
- [Preservazione](PRESERVAZIONE.json): stato live, sessioni e storage precedenti, fixture e artefatti congelati.

## Backup e ricostruzione offline

[Archivio separato](audit-completo.tar.gz) · [SHA256](audit-completo.tar.gz.sha256) · [Manifest dei file](BACKUP-MANIFEST.json) · [Verifica da estrazione indipendente](VERIFICA-BACKUP.json).

L'archivio conserva i percorsi relativi alla radice del repository. Dopo l'estrazione in una directory nuova, con l'ambiente Python del progetto disponibile, dalla radice estratta:

```bash
PYTHONPATH='benchmark ufficiale/baseline-v12-20261021-01/before/backend' \
  /percorso/ambiente/bin/python \
  backend/data/compilation-audit/baseline-v12-20261021-01/verify_real.py minervino
PYTHONPATH='benchmark ufficiale/baseline-v12-20261021-01/before/backend' \
  /percorso/ambiente/bin/python \
  backend/data/compilation-audit/baseline-v12-20261021-01/verify_real.py cesano
PYTHONPATH='benchmark ufficiale/baseline-v12-20261021-01/before/backend' \
  /percorso/ambiente/bin/python \
  backend/data/compilation-audit/baseline-v12-20261021-01/verify_real.py craa
/percorso/ambiente/bin/python \
  backend/data/compilation-audit/baseline-v12-20261021-01/summarize.py
```

Il verificatore vieta rete e SQLite, ricostruisce audit, selezioni e DOCX dalle **tre nuove risposte reali registrate** e controlla l'identità con i download. Non produce nuove inferenze e non automatizza il giudizio documentale delle scritture. `summarize.py` ricalcola usage e costo e ricontrolla i conteggi. Il controllo XML condiviso è incluso nel suo percorso storico. Dipendenze Python e LibreOffice non sono incorporati; i lock sono conservati. La verifica del backup non rilancia né il provider né l'intera suite storica.

Limiti invariati: grammatica FORM limitata, nessuna composizione multi-SOURCE; ruoli, applicabilità, condizioni e USER restano gate separati. Una prova per documento, corpus SOURCE sintetico e revisione autoriale: nessuna generalizzazione automatica. Nessun commit, push, adozione o intervento successivo.
