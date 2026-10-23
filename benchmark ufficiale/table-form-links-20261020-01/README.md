# Relazioni tabellari FORM V12 — consegna 20261020-01

[Rapporto completo](../../docs/relazioni-tabellari-form-v12-2026-10-20.md).

13/13 relazioni del riferimento Catanzaro ora verificabili, indipendentemente
dalla disponibilità di SOURCE, ruolo o autorizzazione USER. Soluzione dal DOCX
originale, non dalle parole del bando e non da citazioni libere nella tabella.
Modello/prompt globale/input FORM/writer invariati. Nessun commit/push.

| Livello | Esito |
|---|---|
| Software | 3.048 backend PASS, 52 nuovi test permanenti, Ruff PASS |
| Export storici | 68/68 DOCX identici byte per byte, checkbox comprese |
| Validatori V2–V12 | 213 confronti PASS, 207 validazioni e 6 rifiuti root pregressi; 199 identici e 14 con nuovi archi |
| Proposte ora grounded | 29 occorrenze nei 68 replay, su tre destinazioni; 17 nelle nove repliche Catanzaro dello studio |
| Nuova UI reale | Una sessione, 17 testi SOURCE; sulla stessa risposta prima 16, dopo 17: sola aggiunta CCIAA Bari |
| Applicabilità | Sede operativa FALSE vuota, UNKNOWN e autorizzazioni conservati |
| Integrità e PDF | Posizioni XML/struttura/CRC/checkbox PASS; 8 PDF storici e PDF reale verificati |
| Preservazione | [PRESERVAZIONE.json](PRESERVAZIONE.json) |
| Backup estratto | [VERIFICA-BACKUP.json](VERIFICA-BACKUP.json), esito separato dai test |

Le 21 promozioni nei 213 validator si sovrappongono ai 29 casi dell'altro
protocollo: non sommarle. Non sono nuove scritture storiche o percentuali di
accuratezza. Il solo numero senza data in t25.r3.c1 resta un problema noto.

- [DIAGNOSI-13.json](DIAGNOSI-13.json): prima/dopo per ogni posizione, XPath, etichetta e rifiuti residui.
- [CATANZARO-RELAZIONI.json](CATANZARO-RELAZIONI.json): anche archi rifiutati/ambigui fuori dal riferimento.
- [PROPOSTE-PRIMA-DOPO.json](PROPOSTE-PRIMA-DOPO.json): tutte le variazioni, con binding e limiti.
- [REGRESSIONE.json](REGRESSIONE.json), [VALIDATOR-AFTER.json](VALIDATOR-AFTER.json), [INVARIANTI.json](INVARIANTI.json).
- [E2E-REALE.json](E2E-REALE.json), [protocollo preregistrato](PROTOCOLLO-E2E.json), [dialogo](e2e/catanzaro/dialogo.md).
- [DOCX scaricato](e2e/catanzaro/bozza.docx), [PDF](e2e/catanzaro/render/bozza.pdf), [report ordinario](e2e/catanzaro/report-validazione.json).
- [Confronto stessa risposta reale](e2e/catanzaro/paired-comparison.json), [verifica offline reale](e2e/catanzaro/offline-verification.json).
- [PDF storici](PDF-HISTORICAL.json), [ispezione campionata](PDF-VISUAL-HISTORICAL.json).

`before/` e `after-code/` conservano il codice con le modifiche locali, test,
fixture e lockfile. `inputs/` conserva i 68 casi e le ricevute originali;
`validator-inputs/` le 213 triplette e provenienza. `before-replay/` e `after/`
contengono output separati senza alterare gli originali congelati.
I sei rifiuti root sono controesempi precedenti, non sei nuove regressioni.

Grezzi, richieste/risposte/tempi, prove fallite, test/log, acquisizione UI e
script sono in `backend/data/compilation-audit/table-form-links-20261020-01/`.
Il backup separato li include; nessuna chiave, `.env` o DB privato. Le coordinate
XML sono a base zero e gli ID restano quelli del catalogo originale.

## Riproduzione deterministica offline

Estrarre `audit-completo.tar.gz` in una directory nuova, verificarne lo SHA256
con il sidecar e gli hash di `BACKUP-MANIFEST.json`. La directory estratta è una
radice repository autonoma per questi replay. Servono Python e le dipendenze
backend del lockfile già installate/cached; il pacchetto non include venv,
interprete, Chromium o LibreOffice. La prova estratta usa le dipendenze locali
installate, ma **nessun modulo applicativo dal working tree corrente**.

Dalla radice estratta, con `PYTHON` che indica l'interprete di quell'ambiente:

```bash
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/before/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/replay.py before-replay
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/after-code/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/replay.py after
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/before/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/historical_validators.py before
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/after-code/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/historical_validators.py after
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/after-code/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/verify_real.py
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/before/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/real_pair.py before
PYTHONPATH="$PWD/benchmark ufficiale/table-form-links-20261020-01/after-code/backend" \
  "$PYTHON" backend/data/compilation-audit/table-form-links-20261020-01/real_pair.py after
```

Eseguire prima e dopo in sequenza. I runner vietano rete e SQLite; riusano solo
output e ricevute conservate, senza provider, assensi inventati o correzioni
MODEL. I JSON vanno confrontati semanticamente (chiavi oggetto ordinate), i
DOCX per byte. `analyze.py` rigenera diagnosi e riepiloghi dagli input nel pacchetto.
I test permanenti sono eseguibili dalla copia backend `after-code`, con le sue
dipendenze e fixture. Gli API test usano SQLite/storage temporanei e provider
simulati; non sono prove di qualità LLM.

I PDF conservati sono ricontrollabili offline; per rigenerarli occorrono
LibreOffice e Poppler locali. L'installazione di tali dipendenze e una nuova
inferenza reale non sono comprese nella riproduzione offline. L'E2E reale è
un'acquisizione unica verificata, non una promessa di ripetibilità delle risposte
stocastiche. Word desktop non testato; ispezione visiva campionata.

Non avviare gli script di cattura/preparazione contro dati live per riprodurre
il risultato: gli input già congelati bastano. Le copie nello studio originale
e nel precedente intervento di applicabilità restano intatte.
