# Compilatore DOCX monolitico: presenza ed eseguibilità (29 ottobre 2026)

**Ambito:** solo verifiche offline. Nessuna chiamata DeepSeek, nessuna modifica all'app ordinaria,
nessun ripristino della monolitica.

## Dove si trova il codice

| Versione | Posizione | Stato |
|---|---|---|
| Monolitica V12 del benchmark B0 | Commit `99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e`: tag `baseline-minervino-v1-20261016`, branch `prune-backend` | In Git, esatta. Solo chiamata unica: nessun `compilation_segments.py` |
| Baseline V12 del 21 ottobre | `benchmark ufficiale/baseline-v12-20261021-01/before/backend` (app, test, `pyproject.toml`, `uv.lock`) | Fuori da Git. 119 hash su 119 corrispondono al manifest; il commit più vicino, `dd41e2e`, ha 50 file su 70 uguali |
| Valutazione finale del 22 ottobre (V14+K3, dialogo P3, monolitica) | `benchmark ufficiale/valutazione-finale-20261022-01/candidate-code/` | Fuori da Git, senza lock né test. 69 file su 77 uguali a `4890daa` |
| Codice attuale (`a4f9a4c`) | Ramo `else` di `resolve_global` in `compilation_global_sessions.py`, quando `generation_revision` manca | Raggiungibile con `MAPI_COMPILATION_PROFILE=storico`; i test preesistenti lo usano tramite `tests/conftest.py` |

`benchmark ufficiale/` non è tracciata in Git. Le due copie archiviate sono anche nel backup
verificato `tesi-backups/stato-ordinario-20261026-01`. Il tag `baseline-pre-one-call-20261010`
(`b271335`) precede la chiamata unica e non è una versione monolitica.

## Eseguibilità verificata (offline)

- **Worktree isolato e staccato** `/home/montesano/tesi-verifica-monolitica-99ab052`:
  - suite di `99ab052`: **2.233 test passati** in 168 s, con le dipendenze bloccate attuali;
  - l'import risolve il codice del worktree;
  - `test_default_chat_start_and_one_call_persistent_review` esegue l'analisi a chiamata unica
    end-to-end con provider simulato.
- **Codice attuale:** il profilo storico passa
  `test_an_existing_session_keeps_the_profile_it_was_created_with`, con analisi monolitica e
  nessun segmento.
- **Scorer B0:** il bundle B0 (SHA256 OK, 347 file su 347 conformi al manifest) è stato estratto
  nel worktree isolato. Rieseguito, `score_results.py` produce 7 file su 7 byte per byte
  identici agli originali.

## Differenze rispetto alla rev3

- **Generazione:**
  - monolitica: una richiesta con tutto il FORM;
  - rev3: 5 segmenti sul Minervino (obiettivo 60 destinazioni, massimo 8). Ogni segmento legge
    il FORM completo e possiede solo le sue destinazioni; un retry per segmento e due per
    analisi; cache per digest; unione con rilevazione dei conflitti.
- **Istruzioni:**
  - `TASK` cambia di 24 righe (tabelle di ruolo, collegamento fra record);
  - in più: data di riferimento, contesto USER registrato e istruzione di segmento.
- **Controlli:** `backend/app` cambia in 50 file (+7.996/−204 righe) e ha 26 moduli nuovi. Fra
  questi: ambito delle ricevute USER, ambiti di ramo, tabelle e opzioni, riuso SOURCE,
  completezza dei valori, applicabilità FORM, consenso procedurale, riesame delle sospensioni,
  caselle testuali. Dove dipendono da un flag, richiedono `generation_revision == 3`.
- **Dialogo:** narratore P3 e guardia delle risposte assenti in `99ab052`.
- **Costo storico:** la generazione per sezioni costa da 1,8 a 4,1 volte i token della
  monolitica.

## Dipendenze

- **Offline:** Python 3.14 con `uv.lock`, identico fra `99ab052` e HEAD salvo il nome del
  pacchetto; per lo scorer basta `lxml`.
- **Prova reale:**
  - chiave DeepSeek e rete;
  - profilo `deepseek-flash` con thinking attivo e timeout di 300 s, come nel B0;
  - per l'interfaccia, Node 20.19+ o 22.12+;
  - LibreOffice solo per il rendering.
- **Limite del modello:** l'alias del modello non fissa i pesi fra un giorno e l'altro.

## Benchmark storici valutati con lo stesso scorer (gold Minervino V1)

| Esecuzione | Codice | Generazione | SOURCE testuali su 60 | Testi USER su 4 | Vuoti corretti su 123 | Caselle vere su 3 |
|---|---|---|---:|---:|---:|---:|
| B0 run 1-3, reali | `99ab052` | Monolitica | 23, 17, 22 | 0 | 123 | 0 |
| Baseline V12 del 21 ottobre, reale | `before/` | Monolitica | 43 | 0 | 123 | 0 |
| Tentativo 03, reale | `7b31d25` | Rev3 | 0 | 0 | 123 | 0 |
| Rigioco 03 con i fix (dialogo simulato) | `a4f9a4c` | Rev3, output 03 | 47 | 0 | 123 | 0 |
| Controfattuale `p39.cb0` (dialogo simulato) | `a4f9a4c` | Rev3, output 03 | 47 | 0 | 123 | 1 |

Stesso FORM (`25ab2b06…`) in tutte le esecuzioni; 56 porzioni SOURCE sia nel B0 sia nel 03.
Le prove non sono appaiate: giorni, codice e scenari USER diversi.
- B0: copione V1, cioè la richiesta iniziale e quattro argomenti.
- 21 ottobre: `scenario-USER.json`, che lascia ignoti preferenze, attestazioni, designazioni,
  luogo e data.
- 01-03: risposte preregistrate del narratore.

Le valutazioni dei DOCX non B0 sono in
`tesi-verifica-monolitica-99ab052/backend/data/compilation-audit/punteggio-gold-sezioni/`
(locale, ignorata da Git).

## Confronto sugli stessi FORM, SOURCE, modello, USER e criteri

| Elemento | Disponibile oggi |
|---|---|
| FORM e SOURCE | Sì: fixture V1 invariata fra `99ab052` e HEAD |
| Criteri | Sì: lo scorer B0 si applica a ogni coppia DOCX + report di questo FORM |
| Modello | Stesso nome; i pesi non sono garantiti identici nel tempo |
| Istruzioni USER | No: va congelata una sola politica per entrambi i bracci |
| Solo la strategia di generazione come variabile | No: il profilo storico spegne anche i controlli rev3. Servirebbe una candidata isolata con la rev3 a un solo segmento |

**Confronti possibili:**
1. **A costo zero:** rivalidare con la pipeline attuale le 4 risposte monolitiche reali
   conservate (B0 ×3 e V12) e la risposta rev3 del 03, con lo stesso dialogo deterministico e lo
   stesso scorer.
2. **Con autorizzazione:** prove reali appaiate, con uguali numero di run, politica USER e
   giorno.
