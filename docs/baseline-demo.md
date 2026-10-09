# Baseline della demo — 9 ottobre 2026

La versione destinata alla dimostrazione rimane in `/home/montesano/Tesi`,
sul branch `prune-backend`. Si avvia come prima con `./start.sh`.
Il riferimento Git locale `demo-baseline-20261009` identifica il codice
congelato dopo la potatura e la correzione della ripresa senza rinvii.
Il precedente `2510418` conserva anche il codice prima della potatura.

Il nuovo percorso a chiamata unica viene sviluppato in un worktree distinto,
`/home/montesano/Tesi-one-shot`, sul branch `feat/compilation-one-shot`.
Le prove devono usare database/storage temporanei o copie esplicite: non
puntare le variabili `MAPI_*` ai dati della demo.

## Copia di sicurezza locale

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

Verifiche del consolidamento: 1.332 test backend su tutti i 44 file, eseguiti
in processi separati per contenere la memoria; 94 test frontend; Ruff, lint
frontend e build passati. Avvio Uvicorn/Vite su una copia dei dati, con pagina
frontend e proxy API funzionanti, 3 progetti, 3 moduli, 4 compilazioni e 9
sessioni accessibili. I log sono nella cartella `verification/` del backup.
