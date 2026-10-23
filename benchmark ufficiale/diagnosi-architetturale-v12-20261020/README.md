# Benchmark diagnostico V12 — consegna completa

[Rapporto](RAPPORTO.md) · [Protocollo antecedente alle chiamate](PROTOCOLLO.json) · [Snapshot](FROZEN.json)

**Esito: nessuna variante integrata. La lunghezza del FORM non è dimostrata come causa.**
99 chiamate reali: 57 analisi e 42 narratori; tre repliche per documento/variante.
Costo stimato 0,931729 USD. Due scritture in ramo non applicabile, una revisione troncata; nessun retry.

Gli output sono esportazioni al checkpoint comune dopo le indicazioni USER iniziali,
prima di ulteriori conferme. Non sono prove UI con dialogo completato.
Una copia vuota o una bozza con scritture indebite non è presentata come compilazione riuscita.

| Documento | Variante | Replica | Valori corretti proposti | Grounded | Scritti conformi | Esito osservato | DOCX | PDF |
|---|---|---|---|---|---|---|---|---|
| Minervino | B0 | 1 | 50 | 47 | 18 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/minervino/B0/rep-1/final/bozza.docx) | [PDF](runs/minervino/B0/rep-1/final/render/bozza.pdf) |
| Minervino | B0 | 2 | 49 | 44 | 0 | FALLIMENTO NARRATORE: copia vuota | [DOCX](runs/minervino/B0/rep-2/final/bozza.docx) | [PDF](runs/minervino/B0/rep-2/final/render/bozza.pdf) |
| Minervino | B0 | 3 | 59 | 42 | 16 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/minervino/B0/rep-3/final/bozza.docx) | [PDF](runs/minervino/B0/rep-3/final/render/bozza.pdf) |
| Minervino | E1 | 1 | 60 | 43 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/minervino/E1/rep-1/final/bozza.docx) | [PDF](runs/minervino/E1/rep-1/final/render/bozza.pdf) |
| Minervino | E1 | 2 | 60 | 9 | 17 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/minervino/E1/rep-2/final/bozza.docx) | [PDF](runs/minervino/E1/rep-2/final/render/bozza.pdf) |
| Minervino | E1 | 3 | 60 | 10 | 18 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/minervino/E1/rep-3/final/bozza.docx) | [PDF](runs/minervino/E1/rep-3/final/render/bozza.pdf) |
| Minervino | E2-A | 1 | 57 | 47 | 17 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/minervino/E2-A/rep-1/final/bozza.docx) | [PDF](runs/minervino/E2-A/rep-1/final/render/bozza.pdf) |
| Minervino | E2-A | 2 | 60 | 43 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/minervino/E2-A/rep-2/final/bozza.docx) | [PDF](runs/minervino/E2-A/rep-2/final/render/bozza.pdf) |
| Minervino | E2-A | 3 | 58 | 44 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/minervino/E2-A/rep-3/final/bozza.docx) | [PDF](runs/minervino/E2-A/rep-3/final/render/bozza.pdf) |
| Trapani | B0 | 1 | 9 | 9 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/trapani/B0/rep-1/final/bozza.docx) | [PDF](runs/trapani/B0/rep-1/final/render/bozza.pdf) |
| Trapani | B0 | 2 | 9 | 9 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/trapani/B0/rep-2/final/bozza.docx) | [PDF](runs/trapani/B0/rep-2/final/render/bozza.pdf) |
| Trapani | B0 | 3 | 17 | 9 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/trapani/B0/rep-3/final/bozza.docx) | [PDF](runs/trapani/B0/rep-3/final/render/bozza.pdf) |
| Trapani | E1 | 1 | 9 | 9 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/trapani/E1/rep-1/final/bozza.docx) | [PDF](runs/trapani/E1/rep-1/final/render/bozza.pdf) |
| Trapani | E1 | 2 | 9 | 9 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/trapani/E1/rep-2/final/bozza.docx) | [PDF](runs/trapani/E1/rep-2/final/render/bozza.pdf) |
| Trapani | E1 | 3 | 9 | 9 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/trapani/E1/rep-3/final/bozza.docx) | [PDF](runs/trapani/E1/rep-3/final/render/bozza.pdf) |
| Trapani | E2-A | 1 | 8 | 8 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/trapani/E2-A/rep-1/final/bozza.docx) | [PDF](runs/trapani/E2-A/rep-1/final/render/bozza.pdf) |
| Trapani | E2-A | 2 | 16 | 8 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/trapani/E2-A/rep-2/final/bozza.docx) | [PDF](runs/trapani/E2-A/rep-2/final/render/bozza.pdf) |
| Trapani | E2-A | 3 | 8 | 8 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/trapani/E2-A/rep-3/final/bozza.docx) | [PDF](runs/trapani/E2-A/rep-3/final/render/bozza.pdf) |
| Catanzaro | B0 | 1 | 14 | 9 | 7 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/B0/rep-1/final/bozza.docx) | [PDF](runs/catanzaro/B0/rep-1/final/render/bozza.pdf) |
| Catanzaro | B0 | 2 | 29 | 13 | 7 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/B0/rep-2/final/bozza.docx) | [PDF](runs/catanzaro/B0/rep-2/final/render/bozza.pdf) |
| Catanzaro | B0 | 3 | 22 | 8 | 6 | SCRITTURA INDEBITA | [DOCX](runs/catanzaro/B0/rep-3/final/bozza.docx) | [PDF](runs/catanzaro/B0/rep-3/final/render/bozza.pdf) |
| Catanzaro | E1 | 1 | 14 | 12 | 7 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/E1/rep-1/final/bozza.docx) | [PDF](runs/catanzaro/E1/rep-1/final/render/bozza.pdf) |
| Catanzaro | E1 | 2 | 15 | 13 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/E1/rep-2/final/bozza.docx) | [PDF](runs/catanzaro/E1/rep-2/final/render/bozza.pdf) |
| Catanzaro | E1 | 3 | 30 | 13 | 8 | SCRITTURA INDEBITA | [DOCX](runs/catanzaro/E1/rep-3/final/bozza.docx) | [PDF](runs/catanzaro/E1/rep-3/final/render/bozza.pdf) |
| Catanzaro | E2-A | 1 | 19 | 13 | 6 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/E2-A/rep-1/final/bozza.docx) | [PDF](runs/catanzaro/E2-A/rep-1/final/render/bozza.pdf) |
| Catanzaro | E2-A | 2 | 20 | 13 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/catanzaro/E2-A/rep-2/final/bozza.docx) | [PDF](runs/catanzaro/E2-A/rep-2/final/render/bozza.pdf) |
| Catanzaro | E2-A | 3 | 30 | 13 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/catanzaro/E2-A/rep-3/final/bozza.docx) | [PDF](runs/catanzaro/E2-A/rep-3/final/render/bozza.pdf) |
| Bella | B0 | 1 | 8 | 0 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/bella/B0/rep-1/final/bozza.docx) | [PDF](runs/bella/B0/rep-1/final/render/bozza.pdf) |
| Bella | B0 | 2 | 8 | 4 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/bella/B0/rep-2/final/bozza.docx) | [PDF](runs/bella/B0/rep-2/final/render/bozza.pdf) |
| Bella | B0 | 3 | 8 | 4 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/bella/B0/rep-3/final/bozza.docx) | [PDF](runs/bella/B0/rep-3/final/render/bozza.pdf) |
| Bella | E1 | 1 | 4 | 4 | 3 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/bella/E1/rep-1/final/bozza.docx) | [PDF](runs/bella/E1/rep-1/final/render/bozza.pdf) |
| Bella | E1 | 2 | 4 | 4 | 3 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/bella/E1/rep-2/final/bozza.docx) | [PDF](runs/bella/E1/rep-2/final/render/bozza.pdf) |
| Bella | E1 | 3 | 4 | 0 | 0 | COPIA VUOTA: vincoli/hold | [DOCX](runs/bella/E1/rep-3/final/bozza.docx) | [PDF](runs/bella/E1/rep-3/final/render/bozza.pdf) |
| Bella | E2-A | 1 | 8 | 0 | 2 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/bella/E2-A/rep-1/final/bozza.docx) | [PDF](runs/bella/E2-A/rep-1/final/render/bozza.pdf) |
| Bella | E2-A | 2 | 4 | 4 | 8 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/bella/E2-A/rep-2/final/bozza.docx) | [PDF](runs/bella/E2-A/rep-2/final/render/bozza.pdf) |
| Bella | E2-A | 3 | 8 | 0 | 3 | Bozza parziale, nessuna scrittura indebita rilevata | [DOCX](runs/bella/E2-A/rep-3/final/bozza.docx) | [PDF](runs/bella/E2-A/rep-3/final/render/bozza.pdf) |

Ogni directory `runs/DOCUMENTO/VARIANTE/rep-N/` contiene tutte le chiamate e il risultato,
inclusi input, richiesta, HTTP con reasoning, output, audit, revisioni reali, scritture e verifiche.

- [Metriche totali](METRICS-TOTALS.json), [prove CSV](trials.csv), [chiamate CSV](calls.csv).
- [Criteri e inventario SOURCE](reference/manifest.json), [tracce](TRACE-REFERENCE.json), [cause](CAUSES.json).
- [Punteggi automatici](SCORES.json), [equivalenze motivate](SEMANTIC-ADJUDICATION.json), [punteggi semantici](SEMANTIC-SCORES.json).
- [Scritture indebite e prove](UNSAFE-WRITES.json), [UNKNOWN](UNKNOWN-INVENTORY.json), [domande](FINAL-QUESTIONS.json).
- [Limite strutturale FORM](STRUCTURAL-BARRIERS.json), [controlli visivi](VISUAL-CHECKS.json), [PDF locali](PDF-LOCAL-SUMMARY.json).
- [Ricostruzione offline](OFFLINE-REBUILD.json), [regressione storica](regression/result.json), [preservazione](PRESERVAZIONE.json).
- [File modificati](FILES-MODIFICATI.json), [backup](audit-completo.tar.gz), [SHA256](audit-completo.tar.gz.sha256), [verifica estratta](VERIFICA-BACKUP.json).

Riproduzione offline dal codice congelato (usare ambiente con dipendenze del lockfile):

```bash
PYTHONPATH='benchmark ufficiale/diagnosi-architetturale-v12-20261020/snapshot/backend:benchmark ufficiale/diagnosi-architetturale-v12-20261020/code' backend/.venv/bin/python 'benchmark ufficiale/diagnosi-architetturale-v12-20261020/code/rebuild.py'
```

Il replay vieta rete e SQLite. Non è una nuova generazione e conserva anche le due scritture indebite.
Le credenziali necessarie per nuove chiamate non sono nel pacchetto. I runner reali conservano esiti esistenti e non sostituiscono repliche fallite.
Modello, input, tariffe e ordine sono nel protocollo; una nuova chiamata futura non è garantita identica.

Nessun commit, push, migrazione o modifica alla V12 di produzione.
