# V13 S1 — consegna delle due coorti reali

Stato: **campagne concluse, candidata `CANDIDATE_FROZEN_NOT_ADOPTED`**. Nessuna
adozione: decide l'utente. Baseline vigente: [BASELINE-V12.md](../../BASELINE-V12.md).

Rapporto conclusivo: [docs/v13-s1-omissioni-fattuali-2026-10-21.md](../../docs/v13-s1-omissioni-fattuali-2026-10-21.md).
Rapporto intermedio delle 18:18, conservato: [rapporto-intermedio-codex-1818.md](rapporto-intermedio-codex-1818.md).

## Esiti

90 tentativi preregistrati, **79 DOCX e 11 tentativi senza DOCX**. Stesse
risposte con codice V12 → V13: 98 → 217 testi (coorte 1) e 407 → 526 (coorte 2),
238 aggiunte corrette, nessuna rimozione o cambio. **Quattro scritture CCIAA non
dimostrate** in craa-03/craa-04 della coorte 2, prodotte anche dal codice V12.
79 PDF: 77 PASS_WITH_LIMITS, 2 FAIL (craa-03, craa-04).

## Dove guardare

| File | Contenuto |
|---|---|
| `CONFRONTO-FINALE-V12-V13.json` | Effetti separati di codice, protocollo USER e risposte LLM; 17 destinazioni baseline; catena CCIAA |
| `PDF-ALL-RESULTS.json` | Esito PDF di tutti i 79 DOCX delle due coorti |
| `CONFRONTO-CAMPAGNA.json`, `MISURE-CAMPAGNA.json` | Conteggi, distribuzioni, chiamate, token e costi della coorte 1 |
| `PAIRED-CAMPAIGN.json`, `PAIRED-SNAPSHOT-V12.json`, `PAIRED-BASELINE.json` | Replay appaiati V12/V13 e codice `before/` eseguito |
| `FALLIMENTI.json`, `DOCUMENTARY-*.json` | Fallimenti e revisione documentale delle scritture |
| `PROTOCOLLO.json`, `FROZEN-BEFORE.json`, `candidate-code/`, `before/` | Preregistrazione, snapshot e 120 hash |
| `PRESERVAZIONE.json` | Preservazione di DB live, sessioni, baseline V12 e cloni |
| `audit-completo.tar.gz`, `BACKUP-MANIFEST.json`, `VERIFICA-BACKUP.json` | Archivio tecnico verificato di entrambe le coorti |
| `VERIFICA-SEGRETI-ZIP.json` | Scansione credenziali nei membri decompressi degli ZIP |
| `consegna-documentale.tar.gz`, `CONSEGNA-MANIFEST.json` | Addendum con rapporti, README, STATUS e relazioni |

Coorte 2, stessa struttura: [../v13-s1-validation-20261021-02/](../v13-s1-validation-20261021-02/),
con `incident-craa-03/` e `PROTOCOLLO-prima-preflight.json`.
Grezzi e script: `backend/data/compilation-audit/v13-s1-20261021-01/` e
`backend/data/compilation-audit/v13-s1-validation-20261021-02/`.

## Ripetere le verifiche offline

Estrarre `audit-completo.tar.gz` in una directory nuova e verificare
`BACKUP-MANIFEST.json`. Con le dipendenze del backend e `PYTHONPATH` puntato a
`candidate-code/backend` estratto, `verify_campaign.py` di ogni coorte ricostruisce
audit e DOCX con rete e SQLite vietati (con `PYTHONPATH` su `before/backend` e
l'opzione `--baseline-snapshot` riesegue il codice pre-V13);
`summarize_campaign.py` ricalcola le misure, `final_comparison.py` il confronto
finale. Non riproducono l'inferenza del provider né la revisione umana.
