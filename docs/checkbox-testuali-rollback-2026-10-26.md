# Handoff e rollback verificato — caselle testuali, 26 ottobre 2026

Intervento concluso offline; nessuna adozione nell'app e nessuna inferenza.

| Passo | Commit | Risultato |
|---|---|---|
| Snapshot del runtime | `1785357e539e3213a1e35002db8f962ef8e60f1e` | 373 file uguali al runtime ordinario; backup del codice/dati ripristinato, seconda copia su D verificata |
| Fix isolato | `55fcd0ec8d543a00e25833b36e673b5a4a0b6060` | Marcatori ASCII nel catalogo e nel writer, scelte USER e applicabilità preservate; profilo esplicito |

Rapporto e limiti: [checkbox-testuali-2026-10-26.md](checkbox-testuali-2026-10-26.md).
Nota redazionale: l'adapter dedicato ha 53 righe; il numero di righe non è una
misura della qualità o della sicurezza della modifica.

## Rollback effettivamente eseguito

Nel worktree isolato `/home/montesano/tesi-checkbox-rollback-20261026`:

```bash
git revert --no-commit 55fcd0e
```

L'albero preparato dal revert coincide esattamente con quello di `1785357`:
`21ff750cfaccdd8147d7b9866407f020d1b55eb8`.
Confrontati anche i 373 file applicativi tramite SHA-256.

- 90 test nativi, gruppi, API e profili: PASS sul codice ripristinato.
- I due test del difetto originario: entrambi falliscono come atteso
  (destinazione testuale assente, writer che la rifiuta).
- Nessun reset, clean, modifica dei dati live o migrazione.

Per annullare il fix nel proprio branch di lavoro, usare `git revert 55fcd0e`.
Il comando senza commit sopra serve alla verifica isolata; lascia intenzionalmente
la patch inversa nello staging di quel worktree, non nella candidata o nell'app.
La documentazione aggiunta successivamente resta documentazione e non modifica
il comportamento del runtime.

Togliere `MAPI_COMPILATION_PROFILE=checkbox-testuali-2026-10-26` torna al profilo
ordinario per le nuove sessioni. Le sessioni sperimentali già create mantengono
il flag: conservarle, senza convertirle implicitamente. Non sono state create
sessioni sperimentali nei dati dell'app ordinaria durante questo intervento.

## Verifiche conclusive

117 test mirati PASS. Suite 3980 PASS + otto test storici inizialmente SKIP per
artefatti assenti nel worktree; artefatti copiati e verificati, poi 8/8 PASS.
Ruff PASS. Replay: 0/25 errori ammessi, 243/245 positivi congelati e 236/240 estesi
con verifica d'ambito simulata, invariati. Nessun nuovo giudizio indipendente o
esperimento reale. Vecchie ricevute e catalogo ampliato non sono intercambiabili.

Artefatti in `backend/data/compilation-audit/snapshot-checkbox-20261026-01/`
del repository ordinario; prova writer sui DOCX/PDF in `render/`.
Backup snapshot in `/home/montesano/tesi-backups/stato-ordinario-20261026-01/`
e `D:\Backup-tesi-2026-10-23\stato-ordinario-20261026-01\`.
Bundle e audit della candidata conservati separatamente in
`/home/montesano/tesi-backups/checkbox-testuali-20261026/` e nella cartella
omonima sotto `D:\Backup-tesi-2026-10-23\`.

Non risultano push o merge di questo intervento. Il codice della candidata è
nel worktree dedicato, non nel processo dell'app ordinaria.
