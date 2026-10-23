# Completezza dei valori composti V12 — consegna del 21 ottobre 2026

[Rapporto completo](../../docs/completezza-valori-composti-v12-2026-10-21.md).
Causa, inventario, implementazione, prove e limiti restano distinti. Nessun commit/push.

- `FROZEN.json`, `before/`: baseline locale, comprese modifiche pregresse.
- `RIPRODUZIONE-ORIGINALE.json`: DOCX UI originale ricostruito prima del codice.
- `PROGETTO-PRIMA-DEL-CODICE.md`, `DELTA-ATTESI.json`: decisione e delta preregistrati.
- `inputs/`, `before-replay/`, `after/`, `after-results.json`: 69 export, ogni prova SOURCE/USER, audit, valori, posizioni fisiche e controlli. 56 DOCX identici, 13 modificati solamente per cinque numeri senza data e dieci telefoni sotto coordinazione ambigua.
- `INVENTARIO-E-DELTA.json`: nove originali distinti, ogni destinazione e tutti i delta classificati. 118 COMPLETE, sei INCOMPLETE e 36 UNKNOWN sulle 160 proposte interessate dai requisiti; i controlli senza proposta non provano assenze nelle SOURCE.
- `validator-inputs/`, `validator-before/`, `validator-after/`, `VALIDATOR-*.json`: 213 triplet V2–V12; 207 validati e sei rifiuti precedenti conservati. Non sono 213 export o prove UI.
- `after-code/`, `INVARIANTI-CODICE.json`: codice/test finali e controlli sulle parti conservate.
- `PDF-REGRESSIONE*.json`: 31 coppie DOCX/PDF, tutti gli export modificati prima/dopo e riferimenti delle altre cinque famiglie.
- `PROTOCOLLO-E2E.json`, `e2e/catanzaro/`, `E2E-REALE.json`: una prova UI reale, 16 scritture SOURCE, download e PDF di 17 pagine verificati. La nuova risposta omette numero/data: nessun parziale da intercettare in questa singola E2E; stessa risposta nei due backend 16→16. Prova causale sull'originale congelato 17→15.
- `PRESERVAZIONE.json`: DB live, sessioni, storage, knowledge, originali e modifiche pregresse verificati.
- `audit-completo.tar.gz`, `BACKUP-MANIFEST.json`, checksum e `VERIFICA-BACKUP.json`: backup separato estratto e rieseguito. DB/chiavi privati esclusi. Manifest e risultati della verifica esterna non vengono ricorsivamente incorporati nell'archivio.

Suite conclusiva: **3.180 backend PASS**, 132 nuovi casi (98 unitari, 34 API FTS5/Qdrant), Ruff PASS. Non è implementata composizione multi-span: l'intero valore deve ancora essere documentato secondo il contratto letterale esistente. COMPLETE non sostituisce ruolo, SOURCE, applicabilità o autorizzazione USER. La grammatica copre le famiglie dichiarate nel rapporto, senza pretesa di interpretare qualsiasi linguaggio naturale.

Il grezzo `backend/data/compilation-audit/compound-values-20261021-01/` conserva script, acquisizioni provider, rete/trace/video/screenshot UI, revisioni, manifest e log anche dei tentativi falliti o superati. Nell'archivio mantiene la stessa posizione relativa alla radice.

Il codice della prima UI è conservato in `e2e-initial-code/`. Dopo quattro casi di formato dei qualificatori sono cambiati due soli confronti con `re.I`; regressione finale 3.180 PASS e secondo export/download UI sulla **stessa analisi reale**, versione 8, senza seconda globale. Protocollo e trace finali separati; DOCX iniziale/finale identici.

## Riproduzione offline

Servono Python e le dipendenze del lock già installate. Nessuna credenziale o servizio AI/DB è necessario ai replayer; vietano rete e SQLite. Le chiamate reali vengono rilette, non ripetute. L'ambiente Python e LibreOffice non sono inclusi. Da una nuova estrazione che conservi la struttura della radice, impostare il percorso di un interprete con le dipendenze disponibili:

```bash
REPLAY_PYTHON=/percorso/ambiente/bin/python
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/before/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/replay.py before-replay
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/after-code/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/replay.py after
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/before/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/historical_validators.py before
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/after-code/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/historical_validators.py after
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/after-code/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/verify_real.py
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/before/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/real_pair.py before
PYTHONPATH="$PWD/benchmark ufficiale/compound-values-20261021-01/after-code/backend" "$REPLAY_PYTHON" backend/data/compilation-audit/compound-values-20261021-01/real_pair.py after
```

`backup.py` esegue questi controlli su un'estrazione separata, confronta ogni DOCX e audit acquisito e riesegue 98 nuovi test unitari. Gli altri 34 test API e la suite completa sono eseguiti con DB/storage temporanei, non dai replayer che vietano SQLite. Le fixture esterne dei benchmark sono incluse nelle due copie di codice per rendere disponibili anche i comandi software dal rispettivo `backend/`:

```bash
"$REPLAY_PYTHON" -m pytest -q
"$REPLAY_PYTHON" -m ruff check .
```

Il PDF acquisito è già incluso. Per rigenerarlo serve anche LibreOffice; il renderer conserva controlli a coordinate per il testo fra colonne e non sostituisce le verifiche delle posizioni XML. Word desktop non è stato utilizzato.
