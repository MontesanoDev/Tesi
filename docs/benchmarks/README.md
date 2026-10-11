# Archivio dei benchmark

I benchmark sono dati di progetto da conservare, non output temporanei.
Distinguere prove reali dei provider da test software con risposte simulate.

## Modulo labirinto dedicato, 11 ottobre 2026

- Contesto fisico: [V2](2026-10-11-labirinto-context-v2.json),
  [V3 corrente](2026-10-11-labirinto-context-v3.json),
  [registro](../../relazioni.md). Sei chiamate reali; V3 conserva 18/22 valori
  attesi, cinque societari corretti, sede coincidente NA in 2/3. Beneficio
  semantico parziale, polizza/recapiti ancora impropri e nessuna scrittura.
  [Bundle delle due iterazioni](2026-10-11-labirinto-context-audit.tar.gz) e
  [checksum](2026-10-11-labirinto-context-audit.tar.gz.sha256).
  Finali 230 mirati/1.636 backend, Ruff/check/help/diff; frontend invariato.

- [Fixture V1](../../demo-documents/benchmark-compilazione/v1/README.md): Word
  sintetico con 55 posizioni/11 checkbox, sette SOURCE fittizie, gold autoriale
  escluso dal prompt e manifest. Runner `--fixture`, senza ingestion o corpus DB.
- [Registro permanente](../../relazioni.md) e
  [baseline per candidate](2026-10-11-labirinto-v1-baseline.json).
- Tre chiamate reali DeepSeek su `5e8cecc`, stesso input: 18/22 valori attesi
  proposti, 12 passano i gate; errori semantici variabili, nessuna attivazione
  o scrittura. Tempi 9,49–12,01 s sul corpus piccolo, non una misura E2E.
- [Bundle](2026-10-11-labirinto-v1-audit.tar.gz) e
  [checksum](2026-10-11-labirinto-v1-audit.tar.gz.sha256): tutte le acquisizioni,
  codice e fixture congelati, confronto e controlli; nessuna chiave/DB.
- 209 mirati/1.615 backend passati, Ruff/check/help/diff; frontend invariato.

## Proposte sparse e validazione locale, 11 ottobre 2026

- [Report completo](../benchmark-proposte-sparse-2026-10-11.md) e
  [metriche/annotazioni](2026-10-11-compilation-global-sparse.json).
- Quattro chiamate reali in due coppie congelate: prime due rifiutate, ultime
  due con 9/8 grounded conservati e rifiuti locali, ~20/31 s. Errori semantici
  ancora presenti: nessuna attivazione, RESOLVED o scrittura.
- [Bundle completo](2026-10-11-global-sparse-audit.tar.gz) e
  [checksum](2026-10-11-global-sparse-audit.tar.gz.sha256): tutti i grezzi,
  codice/input/schema/request/HTTP/output, validazioni, manifest, analisi e log.
  Esclusi database, configurazioni private e credenziali.
- Finali 188 test mirati/1.594 backend, Ruff/help/diff; V1/frontend invariati.

## Proposta compatta e origine canonica, 10 ottobre 2026

- [Report completo](../benchmark-proposta-compatta-2026-10-10.md),
  [usage/errori/annotazioni](2026-10-10-compilation-global-compact.json).
- Sei chiamate reali, tre coppie a codice congelato; stesso Word e 51 SOURCE.
  Tutte rifiutate, ultime due ~47 s/~88.700 token. Nessuna attivazione/RESOLVED.
- [Bundle completo](2026-10-10-global-compact-audit.tar.gz) e
  [checksum](2026-10-10-global-compact-audit.tar.gz.sha256): prompt, risposte anche
  fallite, codice congelato, originali, manifest, annotazioni e controlli.
  Niente DB/credenziali. Grezzi locali `global-compact-20261010-*`.
- Finali 148 test mirati/1.544 backend, Ruff/help/diff; V1 e frontend invariati.

## Fatti e condizioni condivisi, 10 ottobre 2026

- [Report del secondo esperimento](../benchmark-condizioni-globali-2026-10-10.md)
  e [riepilogo/annotazioni](2026-10-10-compilation-global-conditions.json).
- Due proposte complete senza condizioni estratte; confronto con thinking low
  troncato/rifiutato. Nessun miglioramento semantico o token dimostrato.
- Cinque valori aziendali ancora supportati, ma fatti compositi e rami non
  verificati: nessuna promozione a RESOLVED o attivazione nella chat.
- [Bundle completo](2026-10-10-global-conditions-audit.tar.gz) e
  [checksum](2026-10-10-global-conditions-audit.tar.gz.sha256): prompt, risposte,
  errori, usage, codice, controlli e annotazioni senza database o credenziali.
- 110 test mirati/1.506 backend completi, Ruff, help e diff; originali invariati.

## Proposta globale reale, 10 ottobre 2026

- [Report, limiti e decisione](../benchmark-proposta-globale-2026-10-10.md).
- [Riepilogo JSON e annotazioni semantiche](2026-10-10-compilation-global.json)
  e [prima prova](2026-10-10-compilation-global-run1.json).
- Tre chiamate DeepSeek reali, intero catalogo 307 posizioni, corpus completo
  piccolo di 51 SOURCE. Stesso originale della baseline V1, zero USER.
- Grezzi permanenti `backend/data/compilation-audit/global-20261010-run1/`,
  `global-20261010-run2/`, `global-20261010-run3/`, con manifest e codice congelato.
- Nessuna modifica di sessioni/renderer/chat: grounded non significa RESOLVED.
  Un JSON è rifiutato; rilevati falsi positivi di applicabilità, conservati nel report.
- [Bundle grezzi versionato](2026-10-10-global-proposal-audit.tar.gz) e
  [checksum SHA-256](2026-10-10-global-proposal-audit.tar.gz.sha256): 78 file,
  tre prove, replay, log software e cataloghi strutturali precedenti. Confrontato
  byte per byte con le acquisizioni locali; escluse credenziali/configurazioni
  private/database. Sarà trasferibile con Git, senza dipendere da `backend/data/`.

## Catalogo strutturale, 10 ottobre 2026

- [Contratto, limiti e comando di ripetizione](../catalogo-compilazione.md).
- [Misure JSON](2026-10-10-compilation-catalog.json): candidate testo/checkbox,
  dimensioni e tempi dell'estrazione deterministica, originali verificati.
- Grezzi permanenti: `backend/data/compilation-audit/catalog-20261010/`, con
  cataloghi delle fixture Catanzaro/Minervino, misure e log dei controlli.
- Zero chiamate AI: non è una valutazione semantica del modello né una nuova
  misura della latenza di compilazione. Dati grezzi locali esclusi da Git.

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
