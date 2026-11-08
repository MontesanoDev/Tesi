# Consolidamento del 23 ottobre 2026

Solo salvataggio, integrazione della correzione di sicurezza dell'API e verifiche.

**Esclusi:**
- nuove funzionalità ed esperimenti;
- chiamate LLM;
- push e merge.

**Grezzi:** `backend/data/compilation-audit/consolidamento-20261023-01/`.

## Stato Git verificato

| Worktree | Branch | Commit | Non committate |
|---|---|---|---|
| `/home/montesano/tesi` | `prune-backend` | `99ab052` | 431 voci (working tree dell'utente, non toccato salvo questo documento e i rimandi) |
| `/home/montesano/tesi-sprint` | `sprint/2026-10-23-sezioni` | `ff0d4f9` | solo un collegamento locale non tracciato |
| `/home/montesano/tesi-fix-bozza` | `fix/2026-10-23-bozza-esplicita` | `e9c1007` | solo un collegamento locale non tracciato |
| `/home/montesano/tesi-security-fix` | `security/2026-10-23-bozza-esplicita` | `4890daa` | solo un collegamento locale non tracciato |

**Remoto `origin`:** `https://github.com/MontesanoDev/Tesi`.
- `main` (`b8071d3`);
- `prune-backend` (`99ab052`);
- `salvataggio/2026-10-23-tesi` (`dd41e2e`), il salvataggio precedente.

Nessun commit dello sprint, della correzione o dell'integrazione è sul remoto.

**Il repository è PUBBLICO** (API anonima: `private: false`). Il requisito «privato» non è
soddisfatto, quindi **non è stato pubblicato nulla**.

**Codice ordinario:** il working tree principale coincide con `dd41e2e`, il salvataggio già
pubblicato (314 file di codice e configurazione, 0 differenze).

**Differenze dal salvataggio:**
- **Modifiche:** solo `STATUS.md` e `relazioni.md` (rimandi).
- **Eliminazioni non registrate:** 14, i file `RELATORI_*`, `RIPRESA-MAPI.md` e
  «json narratore.json».
- **File nuovi:** `benchmark ufficiale/sprint-e2e-20261023-01` (311 file, 32 MB). Tutti gli altri
  20.279 file non tracciati erano già esclusi deliberatamente al salvataggio
  (`backend/data/salvataggio-20261023/FILE-ESCLUSI.json`).

## Correzione di sicurezza dell'API

**Difetto:** `POST /compilation-sessions/{id}/global-draft` poteva esportare una proposta
sospesa o non revisionata dalla sintesi, se chiesta esplicitamente per id. La UI normale non lo
permetteva.

**Integrazione:**
- **Branch dedicato:** `security/2026-10-23-bozza-esplicita` (`4890daa`), un solo commit
  «security: …» su `dd41e2e`.
- **Contenuto:** stesso albero di `fix/2026-10-23-bozza-esplicita`; cambia solo un paragrafo di
  documentazione.
- **File:** 2 applicativi (19 righe), 1 di test, 1 documento.
- **Dipendenze:** nessuna da codice sperimentale; usa solo funzioni già presenti nel codice
  ordinario.

**Verifiche** (`out/`):

| # | Verifica | Esito |
|---|---|---|
| 1 | Proposta sospesa chiesta per id | 409 (profilo ordinario e P3) |
| 2 | Proposta non revisionata | 409 |
| 3 | Proposta revisionata e autorizzata, anche dopo il rilascio con risposta USER | 200 |
| 4 | Sessione senza dialogo | invariata (200) |
| 5 | V14 / K3 | 16/16 / 13/13 |
| 6 | Veto finale dell'export (rivalidazione, applicabilità, completezza, tabelle, copertura) | 64/64 |
| 7 | Sessioni storiche leggibili (29 live in copia di sola lettura e campagne, 79 stati) | identiche al codice base, 0 errori |
| 8 | Esportazioni storiche rigiocate (210 stati, 157 esportazioni) | 0 rifiuti |
| 9 | Profilo delle nuove sessioni con ambiente vuoto | solo V14, K3, `derivation_revision` (= base) |
| 10 | Parser, writer, DOCX | non toccati; 181 originali identici all'hash registrato |

**Sensibilità:** con la correzione disattivata falliscono gli 8 casi positivi.

**Suite e Ruff:** suite backend completa 3.687 PASS (3.677 esistenti + 10 nuovi), 0 fallimenti; Ruff PASS (`out/suite-integrazione.log`).

**Stato:** la correzione è **pronta, non attiva nell'app live**. L'app usa il working tree
principale (`prune-backend`), che non la contiene.

## Controlli prima della pubblicazione

Branch controllati: sprint (5 commit), correzione (2), integrazione (1). I 20 file modificati:
- **Segreti:** nessuno; scansione con i valori locali in memoria, mai stampati.
- **Database, archivi, chiavi, DOCX, PDF o video:** nessuno.
- **File più grandi:** `STATUS.md` (0,57 MB) e `relazioni.md` (0,34 MB), testo.

## Backup verificati per hash

**`D:\Backup-tesi-2026-10-23\`:**
- `tesi-tutti-i-branch.bundle`, `tesi-working-tree.tar` (4,7 GB), `tesi-backend-data.tar`
  (6,3 GB): situazione delle 16:2x;
- `sprint-sezioni-20261023\`;
- `sprint-e2e-20261023\`: grezzi e risultati della campagna E2E, bundle dello sprint e della
  correzione;
- `consolidamento-20261023\`: bundle del branch di integrazione.

**In locale (`backend/data/compilation-audit/`):**
- `sprint-sezioni-backup-20261023`;
- `sprint-e2e-backup-20261023`;
- `consolidamento-20261023-01/backup`;
- i backup precedenti delle campagne.

## Materiali senza copia remota

Sono soltanto sul disco locale o sui backup Windows:
- **Commit dei branch** `sprint/2026-10-23-sezioni`, `fix/2026-10-23-bozza-esplicita` e
  `security/2026-10-23-bozza-esplicita`: solo locali, con bundle verificati in locale e su `D:`.
- **Risultati dell'ultima campagna** `benchmark ufficiale/sprint-e2e-20261023-01/`: non tracciati,
  con archivio in locale e su `D:`.
- **`backend/data/`** (esclusa da Git): DB locali, archivi delle campagne, cartelle di audit,
  backup. Dopo le 16:2x sono coperti solo dai rispettivi archivi locali e da quelli su `D:`.
- **`backend/data/compilation-audit/consolidamento-20261023-01/`** (questo consolidamento): solo
  locale, salvo il bundle su `D:`.
- **`.tools/`:** runtime privati, con chiavi cifrate e collegamenti alle chiavi. Volutamente fuori
  da Git e dai backup pubblicabili.
- **Rimandi recenti** in `STATUS.md`, `relazioni.md` e questo documento: nel working tree
  principale, non committati.
- **Le 14 eliminazioni** di file `RELATORI_*` e affini: non registrate in nessun commit.

## Pubblicazione (su autorizzazione esplicita dell'utente)

**Repository:** pubblico, `MontesanoDev/Tesi`. Push dei tre branch senza force, senza merge in
`main`.

**Controllo della cronologia da pubblicare** (`verifica_cronologia.py` →
`out/verifica-cronologia.json`):
- 8 commit `dd41e2e..`, 26 versioni di file;
- 0 segreti, compresi i valori locali reali confrontati in memoria;
- nessun database, archivio, chiave o binario, nessun file oltre 2 MB;
- 0 codici fiscali e IBAN;
- l'unica email e i due telefoni sono dati simulati dello scenario, già pubblici in `dd41e2e`;
- autori e committer con l'indirizzo GitHub noreply.

**SHA verificati, locale = remoto:**

| Branch | SHA |
|---|---|
| `sprint/2026-10-23-sezioni` | `ff0d4f9140d2421fe2631e890ccd522c64c05fab` |
| `fix/2026-10-23-bozza-esplicita` | `e9c10073fe2e95cf8bf7965d938cb44f92ecbda1` |
| `security/2026-10-23-bozza-esplicita` | `4890daa9f4a6b5e7c49a2b5cd45e3f5c954c2da1` |

**Invariati:** `main`, `prune-backend` e `salvataggio/2026-10-23-tesi`.

**Sezione superata:** «Materiali senza copia remota» vale ancora, tranne i commit dei tre branch,
che ora sono pubblicati.

