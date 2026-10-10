# Archivio dei benchmark

I benchmark sono dati di progetto da conservare, non output temporanei.
Distinguere prove reali dei provider da test software con risposte simulate.

## Latenza compilazione, 10 ottobre 2026

- [Report e confronto Gemma/DeepSeek](../diagnosi-latenza-compilazione-2026-10-10.md).
- [Riepilogo JSON](2026-10-10-compilation-latency.json): configurazioni pubbliche,
  tempi, token, riepiloghi di stato, valori/quote SOURCE dei primi 12 candidate
  e controlli. Questo file e il report sono versionabili insieme al codice.
- [Bundle Gemma/DeepSeek per il checkpoint Git](2026-10-10-latency-audit.tar.gz),
  con [checksum](2026-10-10-latency-audit.tar.gz.sha256): conserva anche i grezzi
  dei due benchmark isolati senza credenziali, database o snapshot delle sessioni
  storiche dell'utente. Aggiunto su richiesta di salvare il lavoro su GitHub
  prima di iniziare il nuovo motore. I manifest interni verificano i singoli file.
- Acquisizioni locali permanenti, nella radice del repository:
  `backend/data/compilation-audit/latency-20261010-gemma/`,
  `latency-20261010-deepseek/` e `latency-20261010-historical/`.
  Ogni cartella contiene un manifest SHA-256; le cartelle storiche sono letture
  di sessioni precedenti, non prove appena eseguite.
- Archivio trasportabile delle tre cartelle:
  `backend/data/compilation-audit/latency-20261010.tar.gz`, con checksum nel
  file `.tar.gz.sha256` adiacente. Anche questo archivio è locale.

`backend/data/` è esclusa da Git: **un push non salva i dati grezzi su GitHub**.
Il bundle esplicitamente versionato sopra è l'eccezione per i due benchmark
isolati; i dati storici e gli altri audit restano locali. Per spostarli o
conservarli altrove copiare l'archivio locale con il suo checksum.
Non aggiungere credenziali, file `.ai-key`, header Authorization o database
contenenti impostazioni riservate al repository o ai bundle diagnostici.

Il bundle DeepSeek contiene prompt/schema e body realmente inviati, risposte
del provider, tempi/token, query ed evidenze SOURCE, risultati delle fasi,
snapshot della sessione dopo ogni passo, CSV completo, revisioni e verifiche.
Il bundle Gemma conserva quanto acquisito originariamente: i suoi prompt
non furono registrati. Non vengono spacciate ricostruzioni per tracce reali.
I database e gli indici di lavoro sono temporanei; lo stato esportato è durevole.

## Ripetere la misura

Dalla directory `backend`, con profili/KB locali già configurati:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_latency.py \
  --project minervino-di-lecce-elenco-sia --form-id 153 \
  --profile-project prova \
  --output data/compilation-audit/latency-deepseek-NUOVA-PROVA \
  --max-steps 6 --max-seconds 420 \
  --stop-candidate-id t0.r5.c1 --stop-candidate-id t0.r6.c1 \
  --stop-candidate-id t0.r7.c1 --stop-candidate-id t0.r9.c1 \
  --stop-candidate-id t0.r10.c1
```

ID e progetto sono gli input di questa misura, non condizioni hardcoded nel
motore. Per un altro documento scegliere gli ID reali e il profilo desiderato.
La directory di output deve essere nuova: lo script rifiuta di sovrascriverla.
Il runner copia SQLite/storage/indice Qdrant locale e delega alle funzioni reali
di creazione/resolve con provider reale; non modifica profili o sessioni live.
Non supporta un indice Qdrant remoto per questa prova isolata.
Il budget massimo accettato è 36 passi/600 s, default sei passi/420 s; ogni passo
mantiene il timeout applicativo. Niente input USER o generazione DOCX implicita.
La strumentazione non sostituisce le risposte AI e non alleggerisce i validator.

È una misura del percorso automatico backend, non del routing/browser completo.
Non copre la gestione degli errori aggiuntiva della route HTTP. In caso di
failure registra gli artefatti e si ferma, senza correggere il codice in corsa.
