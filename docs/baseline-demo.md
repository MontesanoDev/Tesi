# Baseline della demo — 10 ottobre 2026

## Checkpoint prima del nuovo motore a chiamata unica

Su richiesta dell'utente, consolidato il sistema attuale sul branch
`prune-backend`, con riferimento **`baseline-pre-one-call-20261010`**.
Questo checkpoint comprende layout/scroll della chat, allineamento delle azioni
dei moduli, runner diagnostico, report e benchmark Gemma/DeepSeek; il resolver
V1 rimane quello già esistente. Il nuovo motore globale non è implementato.
È una base parzialmente funzionante con limiti documentati, non una certificazione
di compilazione completa. Le baseline precedenti restano conservate.

Il bundle versionato in `docs/benchmarks/2026-10-10-latency-audit.tar.gz` conserva
le acquisizioni dei due benchmark isolati, senza credenziali o database. Dati
applicativi, chiavi e sessioni storiche restano locali ed esclusi dal push.
Verifiche del checkpoint e prossimo punto in [STATUS.md](../STATUS.md).

Per identificare il codice della base senza modificare il working tree:

```bash
git show baseline-pre-one-call-20261010 --stat
```

## Baseline precedente della demo

La versione destinata alla dimostrazione rimane in `/home/montesano/Tesi`,
sul branch `prune-backend`. Si avvia come prima con `./start.sh`.
Il riferimento Git **`demo-baseline-20261010`** identifica la nuova base con UI
chat aggiornata e thinking opzionale per progetto. Il branch remoto di
riferimento è `origin/prune-backend`.
Il precedente `demo-baseline-20261009` identifica il codice congelato dopo
la potatura e la correzione della ripresa senza rinvii.
Il precedente `2510418` conserva anche il codice prima della potatura.

Il nuovo percorso a chiamata unica viene sviluppato in un worktree distinto,
`/home/montesano/Tesi-one-shot`, sul branch `feat/compilation-one-shot`.
Le prove devono usare database/storage temporanei o copie esplicite: non
puntare le variabili `MAPI_*` ai dati della demo.

## Copia di sicurezza locale

Il push e i tag proteggono il **codice**. Database, documenti e credenziali
rimangono locali e non sono inclusi nel repository remoto.

`/home/montesano/Tesi-snapshots/baseline-20261009T165627Z/` contiene:

- `baseline.bundle`: codice e storia Git, incluso il tag della baseline;
- `data/`: copia dei dati locali, inclusi originali, fonti, sessioni, bozze,
  configurazioni cifrate e audit degli esperimenti;
- `manifest.json`: hash dei file copiati, conteggi delle tabelle e verifica
  di integrità SQLite; il database è acquisito tramite SQLite backup;
- `restore.sh`: ripristino in una cartella **nuova**, senza sovrascrivere la demo;
- `verification/`: esiti e log delle verifiche della baseline;
- `before.bundle` e `pre-pruning-working-tree.patch`: stato Git e modifiche
  presenti prima di questo consolidamento.

La cartella è privata e rimane fuori da Git. Le credenziali necessarie alla
configurazione locale sono conservate soltanto nella copia privata; non sono
incluse nel bundle del codice né in questo documento.
Questa copia rappresenta i dati del 9 ottobre: non contiene le conversazioni
o i file aggiunti successivamente.

## Ripristino

Esempio, con una destinazione che non esiste:

```bash
/home/montesano/Tesi-snapshots/baseline-20261009T165627Z/restore.sh /home/montesano/Tesi-demo-ripristinata
cd /home/montesano/Tesi-demo-ripristinata
./start.sh
```

I lockfile ripristinano le dipendenze attraverso `start.sh`; Ollama e i servizi
AI esterni restano dipendenze dell'ambiente. La copia locale protegge dalle
modifiche del progetto; non costituisce una copia su un secondo dispositivo.

## Perimetro

Questa baseline conserva la compilazione V1 attuale e i suoi limiti di qualità.
La correzione inclusa impedisce il crash di «riprendi» quando un riepilogo di
problemi tecnici non contiene campi realmente rinviati. Non certifica la
correttezza delle risposte AI né introduce il percorso a chiamata unica.
Le verifiche con provider simulati sono distinte dalle valutazioni AI reali.

Verifiche dell'aggiornamento del 10 ottobre: **295 test backend mirati**, **97
test frontend**, **16 E2E desktop/mobile** con API simulate, Ruff, lint e build
passati. Verificati anche migrazione automatica del thinking, flag/budget/timeout
dei provider e conservazione del messaggio quando si apre il picker con **+**.
Nessuna nuova chiamata AI. Il thinking riguarda la generazione finale RAG,
non il planner o i passi della compilazione. Non è stato introdotto il nuovo
motore a chiamata unica.

Verifiche del consolidamento del 9 ottobre: 1.332 test backend su tutti i 44 file, eseguiti
in processi separati per contenere la memoria; 94 test frontend; Ruff, lint
frontend e build passati. Avvio Uvicorn/Vite su una copia dei dati, con pagina
frontend e proxy API funzionanti, 3 progetti, 3 moduli, 4 compilazioni e 9
sessioni accessibili. I log sono nella cartella `verification/` del backup.
