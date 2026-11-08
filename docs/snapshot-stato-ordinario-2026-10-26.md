# Snapshot dello stato ordinario — 26 ottobre 2026

Primo passo autorizzato prima della correzione delle caselle testuali. Nessuna
modifica funzionale, inferenza, avvio dell'app o modifica alle sessioni live.

Il branch `snapshot/2026-10-26-stato-ordinario` deriva da `aaaaa44` e conserva
esattamente i 373 file applicativi attivi nel working tree ordinario: backend,
frontend, lockfile e `start.sh`. Confronto byte per byte e SHA-256 in
`snapshot-runtime-2026-10-26.json`. Nessun grande commit che ricombini i fix:
i commit già pubblicati restano nella loro cronologia.

## Backup privato e ripristino verificato

Cartella principale:
`/home/montesano/tesi-backups/stato-ordinario-20261026-01/`.

- `mapi.senza-credenziali.db`: snapshot SQLite consistente; nella sola copia
  eliminate le chiavi cifrate e le richieste di login temporanee. `.ai-key` e
  `.env` esclusi. Al ripristino occorre reinserire le credenziali dalla UI.
- `storage-live.tar`: uploads, knowledge e indice Qdrant locale.
- `workspace-pendente.tar`: copia privata dei file non ignorati, inclusi i
  risultati storici; nessun inserimento indiscriminato di questi dati in Git.
- `manifest.json`, `git-status.z`, `restore-verification.json`: inventario,
  hash e verifiche. Log temporanei e file di credenziali esclusi; strumenti,
  cache e acquisizioni storiche sotto `backend/data/compilation-audit/` non
  duplicati, perché separati dallo stato live e già conservati nei backup precedenti.

Ripristino eseguito in `ripristino-verificato/`, senza sovrascrivere il progetto:
integrità SQLite OK, zero violazioni delle foreign key; identità delle **29
sessioni** (originali, stato e versione), **474 revisioni**, **199 turni**,
3 progetti e 17 file registrati. Verificati **290 file storage** e **22.506 file
workspace**, uno per uno tramite SHA-256. Il database e lo storage live non
sono cambiati durante la copia. L'app non è stata avviata sul ripristino.

Per recuperare il codice, creare un nuovo worktree dal commit di questo
snapshot, oppure da `aaaaa44` per il medesimo runtime. Non usare reset o clean
sul working tree ordinario. Per recuperare i dati, usare una nuova cartella,
estrarre `storage-live.tar` e collocare la copia SQLite in `backend/data/mapi.db`.
La copia del workspace conserva anche documenti e modifiche locali; estrarla
separatamente per confrontarli, senza sovrascrivere un repository in uso.

Questo ripristino conserva compilazioni e documenti, ma non le credenziali.
Gli hash degli archivi e del bundle Git e la verifica della copia su `D:` sono
conservati insieme al backup, fuori da Git. Nessun merge o push automatico.

## Passo successivo

Il caso sintetico dell'avvalimento contiene `[]` in normale testo del paragrafo
16: nessun controllo Word, nessun elemento simbolo, nessuna cella. Il writer
attuale accetta soltanto controlli nativi. La diagnosi e l'eventuale modifica
del catalogo/rendering devono restare su un altro branch e in un altro commit.
