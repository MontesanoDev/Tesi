# Prova esplorativa V12 su tre nuovi bandi

19 ottobre 2026. Pipeline invariata; tre nuove generazioni globali reali dalla
chat. Estrazione unica di CRAA, Bella e Cesano Maderno da un pool congelato di
otto moduli DOCX ammissibili. Non è un campione rappresentativo dei bandi
italiani e non dispone di GOLD indipendenti.

[Rapporto completo](RAPPORTO.md), [confronto JSON](CONFRONTO.json),
[confronto CSV](CONFRONTO.csv), [controlli finali](CONTROLLI-FINALI.json).

| Documento | Testi SOURCE nell'XML | Leggibili nel PDF | DOCX | PDF |
|---|---:|---:|---|---|
| CRAA | 9 | 7 | [Bozza](craa/bozza.docx) | [7 pagine](craa/bozza.pdf) |
| Bella | 4 | 4 | [Bozza](bella/bozza.docx) | [4 pagine](bella/bozza.pdf) |
| Cesano Maderno | 0 | 0 | [Copia senza valori](cesano/bozza.docx) | [3 pagine](cesano/bozza.pdf) |

CRAA contiene due dati CCIAA nell'XML che LibreOffice non rende visibili:
non sono conteggiati come scritture fruibili nel PDF. Cesano è un fallimento
funzionale della compilazione, anche se l'export è tecnicamente valido.
Nessuna nuova scrittura fattuale o decisione indebita rilevata nei tre casi.
Questo non annulla l'errore PEC del precedente benchmark storico.

Ogni cartella conserva originale, scenario USER, riferimento preliminare,
dialogo, report di validazione, stato finale, input/output globale, prompt,
audit, metriche per chiamata, valutazione dei campi e verifiche fisiche/PDF.
Cesano ha un addendum che distingue il preflight generico dal catalogo
effettivo della chat, senza riscrivere gli input congelati.

[Protocollo](PROTOCOLLO.json), [pool](POOL.json), [estrazione](ESTRAZIONE.json),
[metodo e limiti](METODO-CAMPIONAMENTO.json),
[download esclusi](esclusioni-download.json), [input comuni](input/manifest.json).

22 chiamate totali, delle quali tre globali; 271.084 token e circa 0,060070 USD
stimati, non fattura. Nessun retry selettivo, fix applicativo, E1 o adozione
della baseline. Le prove del software precedenti non sono presentate come
nuovamente eseguite.

## Conservazione e verifica indipendente

[Backup completo](audit-completo.tar.gz), [descrittore e hash](BACKUP.json),
[checksum](audit-completo.tar.gz.sha256),
[esito della verifica estratta](VERIFICA-BACKUP.json).

Il backup include acquisizioni web, richieste/risposte provider, transizioni,
browser, risultati pubblici e codice effettivo congelato. Esclude database
privati, chiavi e file di ambiente. Gli artefatti locali sotto `backend/data/`
sono esclusi da Git: il solo push del codice non li conserva.

Dopo l'estrazione, `MANIFEST-SHA256.json` elenca gli hash dei file. Con le
dipendenze Python bloccate del progetto, dalla directory estratta:

```bash
PYTHONPATH=code/backend /percorso/venv/bin/python audit/verify_bundle.py
```

Il verificatore vieta la rete e ricostruisce audit e tre DOCX dagli output
realmente salvati, senza database, credenziali o nuove chiamate. Identità dei
byte significa riproducibilità, compresi i difetti, non correttezza globale.
Non esegue nuove conversioni PDF né una verifica Microsoft Word desktop.

Il benchmark precedente rimane separato e intatto nella
[directory superiore](../README.md).
