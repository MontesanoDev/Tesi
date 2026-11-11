# Promozione R3 a default dell'app ordinaria — 11 novembre 2026

Su richiesta dell'utente, il worktree sperimentale `narratore-chiarezza/2026-10-31` diventa il
default dell'app ordinaria. Il default precedente resta congelato e recuperabile in pochi minuti.
Ogni DOCX prodotto resta una bozza: la revisione umana è obbligatoria.

## Versioni

| | Riferimento Git | Profilo delle nuove sessioni |
|---|---|---|
| **Default attuale R3.1** | tag `demo-default-r3-1-20261111` = `599fd35` (branch `narratore-chiarezza/2026-10-31`) | `sezioni-2026-11-05` |
| R3, prima della pulizia | tag `demo-default-r3-20261111` = `6c8e40e` | `sezioni-2026-11-05` |
| **Default precedente R2, congelato** | tag `demo-default-r2-20261031` = `3a8de0b` | `sezioni-2026-10-30-r2` |
| Default ancora precedente | tag `demo-default-pre-r2-20261031` = `618eb36` | `sezioni-2026-10-25` |

- **R3** = R2 più i 24 commit del branch sperimentale (narratore, chiarimenti, firmatario,
  stabilizzazione, completezza dell'export) e il commit UI `6c8e40e` dell'11 novembre:
  impostazioni di ricerca a salvataggio automatico, icona di copia sui messaggi, recupero dei
  messaggi falliti solo nel composer, rimozione dell'interruttore thinking, ritocchi grafici.
- **R3.1** = R3 senza gli script di misura del vecchio compilatore e i test che controllavano
  solo quegli strumenti (pulizia dello stesso giorno, vedi sotto). Nessun cambiamento all'app.
- Dipendenze invariate: `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json` e
  `start.sh` sono identici fra R2 e R3.

## Come è stata aggiornata l'app ordinaria

Stesso metodo del 27 e del 31 ottobre, su `/home/montesano/tesi`:
- HEAD resta `prune-backend` @ `99ab052`, con il lavoro locale non committato;
- prima della sostituzione, tutti i 399 file runtime erano identici a R2 (confronto per hash);
- sostituiti solo i file runtime in `backend/app`, `backend/tests`, `frontend/src`,
  `frontend/e2e`: 53 modificati, 24 nuovi, 0 rimossi;
- **esito:** i 423 file runtime dell'app coincidevano con `demo-default-r3-20261111`;
- **pulizia successiva (stesso giorno):** tolti 4 script di misura e 4 test collegati, da qui in
  poi anche `backend/scripts` fa parte dei file runtime confrontati. I 425 file runtime dell'app
  (script compresi) coincidono con `demo-default-r3-1-20261111`;
- non toccati: dati, sessioni, SOURCE, audit, benchmark, documenti locali (salvo questa guida,
  la voce in STATUS e il rimando nel README).

I dati del worktree sperimentale (per esempio il progetto «Minervino prova manuale narratore»)
restano lì: l'app ordinaria continua a usare i propri dati.

## Backup fatti prima della promozione

- Locale: `/home/montesano/tesi-backups/promozione-r3-20261111/` con database (API di backup
  SQLite, integrità ok), indice Qdrant, upload, conoscenza, chiave `.ai-key`, file runtime di
  prima, HEAD e `git status`, `MANIFEST.sha256`, `LEGGIMI.md` e i due script qui sotto.
- Secondo SSD: `/mnt/d/Backup-tesi-2026-11-11/promozione-r3-20261111.tar` con `.sha256`
  verificato e `LEGGIMI.md`.

## Rollback

**1. Interruttore rapido, stesso codice (approssimato).** Con
`MAPI_COMPILATION_PROFILE=sezioni-2026-10-30-r2 ./start.sh` le nuove sessioni non ricevono le
revisioni del 5 novembre. Non è identico alla R2: restano attive le revisioni del 1° novembre
(estrazione USER e conversazione) e le correzioni non legate ai flag.

**2. Codice R2 esatto (consigliato).** Con l'app ferma, dalla radice dell'app ordinaria:

```bash
/home/montesano/tesi-backups/promozione-r3-20261111/rollback-r2.sh
graphify update .
./start.sh
```

Lo script equivale a:

```bash
OLD=demo-default-r2-20261031 NEW=demo-default-r3-1-20261111
P="backend/app backend/tests backend/scripts frontend/src frontend/e2e"
# Controllo: nessun file promosso è stato modificato dopo la promozione.
git diff --name-only --diff-filter=AM $OLD $NEW -- $P | while read -r f; do
  [ "$(git hash-object "$f")" = "$(git rev-parse "$NEW:$f")" ] || echo "MODIFICATO: $f"; done
# Ripristino: 63 file tornano alla versione R2 (55 modificati, 8 tolti con la pulizia),
# 24 file nuovi vengono rimossi.
git diff --name-only --diff-filter=MD $OLD $NEW -- $P | while read -r f; do git show "$OLD:$f" > "$f"; done
git diff --name-only --diff-filter=A $OLD $NEW -- $P | while read -r f; do rm -- "$f"; done
```

- Se il controllo segnala file modificati, lo script si ferma senza toccare nulla: decidere caso
  per caso.
- Per tornare di nuovo alla R3.1: `/home/montesano/tesi-backups/promozione-r3-20261111/promuovi-r3.sh`
  (stesso controllo preventivo, nella direzione opposta).
- Il database non va ripristinato per tornare alla R2: il codice R2 legge il database migrato
  dalla R3 (verificato, vedi sotto). Le sessioni di compilazione create con la R3 restano nel
  database; che la R2 le gestisca non è stato verificato: esportare prima le bozze utili.

**3. Dati di prima della promozione.** Solo se servono davvero: le istruzioni sono nel
`LEGGIMI.md` del backup. Si perdono i dati creati dopo l'11 novembre.

**4. Default ancora precedente.** La procedura verso `demo-default-pre-r2-20261031` è in
[demo-relatori-2026-10-31.md](demo-relatori-2026-10-31.md): va eseguita dopo il punto 2.

## Verifiche (11 novembre, nessuna chiamata a provider AI)

- Prova completa in un worktree temporaneo partito da R2: promozione, 0 differenze da R3;
  rollback, 0 differenze da R2. Ripetuta dopo la pulizia verso R3.1 (script compresi): 55
  modificati, 24 nuovi, 8 rimossi, poi 0 differenze da R2. Il controllo preventivo del rollback
  nell'app ordinaria passa (0 file bloccanti). Con un file modificato a mano, promozione e rollback si fermano
  senza toccare nulla. Worktree rimosso.
- Backend R3 avviato su una copia dei dati reali (porta 8001): migrazione riuscita, integrità
  del database ok, API di progetti, impostazioni, modello e conversazioni con HTTP 200, nessun
  errore nel log.
- Codice R2 avviato sulla stessa copia già migrata (porta 8002): le stesse API rispondono con
  HTTP 200, nessun errore nel log.
- App ordinaria dopo la promozione: frontend 201 test PASS, `tsc -b` PASS, lint con i due
  avvisi preesistenti; backend 4.703 PASS (suite completa, 8 min 50 s).
- Nel worktree sperimentale, prima del commit: backend 4.695 PASS / 8 SKIP, frontend 201 PASS,
  E2E con API simulate PASS (impostazioni di ricerca 40/40 su 5 ripetizioni, menu del modello e
  menzioni 24/24, chat 14/14).
