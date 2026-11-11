# Versione per la dimostrazione ai relatori (31 ottobre 2026)

**Versione sperimentale consolidata per la dimostrazione.** Non è un sistema stabile né pronto
alla produzione. Ogni DOCX prodotto è una bozza: la revisione umana è obbligatoria.

## Versioni

| | Riferimento Git | Profilo delle nuove sessioni |
|---|---|---|
| **Nuovo default** | tag `demo-default-r2-20261031` = `3a8de0b` (branch `demo/2026-10-31-relatori`) | `sezioni-2026-10-30-r2` |
| **Default precedente, congelato** | tag `demo-default-pre-r2-20261031` = `618eb36` | `sezioni-2026-10-25` |

- **Nuovo default (`3a8de0b`):**
  - il compilatore è quello di `c838339`, del branch `riduzione-omissioni/2026-10-30`, con
    tutti i fix verificati del 30 ottobre;
  - in più il lavoro frontend locale del 29 ottobre, conservato com'era:
    - impostazioni di retrieval;
    - campi dell'indirizzo del servizio;
    - condizione del pulsante «Aggiungi un documento».
- **Default precedente (`618eb36`):** è il codice runtime esatto in uso fino al 31 ottobre, cioè
  `796afaf` (integrazione delle caselle testuali, 27 ottobre) più gli stessi 7 file frontend
  locali. Senza `.env` e senza `MAPI_COMPILATION_PROFILE`.

**Come è stata aggiornata l'app ordinaria** (`/home/montesano/tesi`), con lo stesso metodo del 27
ottobre:
- HEAD resta `prune-backend` @ `99ab052`, con il lavoro locale non committato;
- sono stati sostituiti solo 83 file runtime (23 in `backend/app`, 53 in `backend/tests`, 7 in
  `frontend/src`). Ognuno era ancora identico al default precedente e, se nuovo, assente;
- `ProjectWorkspacePage.tsx` è la fusione a tre vie, senza conflitti, della modifica locale con
  il branch;
- non sono stati toccati:
  - documenti locali (README, STATUS, relazioni, AGENTS);
  - dati, sessioni, SOURCE;
  - `audit_tools`, benchmark e strumenti di campagna.
- **Esito:** i 410 file runtime dell'app coincidono con `3a8de0b`.

## Avvio

Dalla radice del repository: `./start.sh`, poi `http://localhost:5173`. I requisiti sono nel
README.

**Configurazione:**
- nessuna variabile d'ambiente necessaria, nessun `.env`;
- non impostare `MAPI_COMPILATION_PROFILE` (serve solo al rollback);
- in **Impostazioni generali → Modelli AI** scegliere un modello generativo (DeepSeek usato nelle
  prove reali). Le chiavi si inseriscono nell'interfaccia;
- la ricerca nelle fonti funziona con FTS5 senza Ollama; la ricerca semantica richiede un
  modello di embedding.

**Senza modello configurato** l'app lo dice chiaramente e non scrive nulla:
- avvio della compilazione: «Configura un modello AI per compilare il modulo» (HTTP 503);
- chat: «Configura un modello AI nelle Impostazioni generali».

**Al primo avvio** il backend rigenera ID e timestamp di 82 frammenti di quattro artefatti
Markdown (`seed_markdown_artifacts`):
- succede a ogni avvio anche col codice precedente, già documentato il 27 ottobre;
- non tocca sessioni, revisioni, turni né SOURCE.

Si consiglia un progetto dedicato alla dimostrazione.

## Rollback

**1. Comportamento precedente, stesso codice** (confronti rapidi):
- comando: `MAPI_COMPILATION_PROFILE=sezioni-2026-10-25 ./start.sh`;
- le nuove sessioni ricevono esattamente i flag del default precedente (verificato nel worker
  reale);
- vale solo per la creazione delle sessioni: le correzioni non legate ai flag restano attive;
- sono selezionabili anche `sezioni-2026-10-30` e `sezioni-2026-10-24`.

**2. Codice precedente esatto.** Con l'app ferma, dalla radice:

```bash
OLD=demo-default-pre-r2-20261031 NEW=demo-default-r2-20261031
P="backend/app backend/tests frontend/src frontend/e2e"
# Controllo: nessun file promosso è stato modificato dopo la promozione.
git diff --name-only --diff-filter=AM $OLD $NEW -- $P | while read -r f; do
  [ "$(git hash-object "$f")" = "$(git rev-parse "$NEW:$f")" ] || echo "MODIFICATO: $f"; done
# Ripristino: 33 file tornano alla versione precedente, 50 file nuovi vengono rimossi.
git diff --name-only --diff-filter=M $OLD $NEW -- $P | while read -r f; do
  git show "$OLD:$f" > "$f"; done
git diff --name-only --diff-filter=A $OLD $NEW -- $P | while read -r f; do rm -- "$f"; done
graphify update .
```

- Se il controllo segnala file modificati, fermarsi e decidere caso per caso.
- La procedura è stata provata in un worktree di prova (`tesi-demo-rollback-20261031`):
  promozione esatta, poi 0 differenze dallo snapshot precedente.
- Le sessioni create con il profilo r2 restano nel database. Che il codice precedente le legga
  non è stato verificato: esportare le bozze della demo prima di un rollback del codice.

## Funzionalità dimostrabili

- Caricamento di FORM DOCX/TXT e di SOURCE di progetto e aziendali.
- «Compilazione DOCX» dalla chat: analisi per segmenti del FORM, ognuno con il FORM completo.
- Domande del narratore e risposte libere dell'utente: conferme, rinvii, scelte e valori USER,
  con guardia semantica delle risposte.
- Riesame deterministico dei dubbi del narratore:
  - i valori documentati senza un motivo verificabile vanno ai controlli ordinari e la bozza li
    segnala «da rivedere»;
  - quelli contraddetti da un'altra SOURCE restano sospesi, con domanda che mostra entrambi i
    testi.
- Recupero mirato delle proposte respinte dai validatori e delle destinazioni dichiarate non
  valutate. Ritentativi limitati per JSON malformato.
- Caselle testuali `[]`/`[X]` solo con scelta USER verificata; caselle native con gruppi FORM
  ancorati.
- Export esplicito di una bozza parziale dall'originale, con report JSON di provenienza e
  motivazioni per campo. Nessuna scrittura di valori non revisionati.

## Limiti noti da non nascondere

- **Dipendenza dal modello.** Su Minervino, 11 run reali hanno dato da 33 a 60 campi corretti.
  La prima risposta del modello sul blocco dei soci (24 posizioni) va «tutto o niente».
- **Condizione generica di partecipazione.** A volte il modello chiede se il partecipante è
  l'operatore economico del profilo e ci lega un blocco intero di campi. Se l'utente rinvia, il
  blocco resta vuoto. Nelle prove: compilazione 4/18, CNR 1/10. Va confermata esplicitamente.
- **`p14.s0` di Minervino** viene scritto con la carica letterale della SOURCE, più ampia del gold.
- **Il riesame dei dubbi non ragiona sulle date** di decorrenza.
- **Non esercitati in esecuzioni reali:**
  - il ramo «evidenza contraddittoria»;
  - il ritentativo per JSON malformato.

  Sono coperti dai test.
- **Caselle:** supporto limitato ai marcatori ASCII previsti e ai gruppi nativi ancorati, non
  universale. Le celle di layout senza ancora FORM non sono recuperate.
- **Prove automatiche:**
  - usano provider simulati e non misurano la qualità delle risposte reali;
  - gli E2E Playwright non sono stati rieseguiti in questa consolidazione;
  - il lint frontend ha 2 avvisi `react-hooks` ereditati dal branch (`typedDraft`).
- **Costo indicativo** con DeepSeek: circa 0,07 USD e 18–22 chiamate per un run Minervino.

Rapporto completo sulle misure: `docs/riduzione-omissioni-2026-10-30.md` (branch
`riduzione-omissioni/2026-10-30`).

## Verifiche della consolidazione (31 ottobre, nessuna chiamata DeepSeek)

| Verifica | Esito |
|---|---|
| Backend nell'app ordinaria | 4.292 passati, 0 saltati; Ruff PASS |
| Frontend | 188 test passati; lint senza errori (2 avvisi ereditati); build riuscita |
| `./start.sh` su dati temporanei | backend e proxy frontend HTTP 200 |
| Codice caricato nel worker | 42–45 moduli `app` caricati, tutti identici a `3a8de0b` |
| Profilo nuove sessioni nel worker | `sezioni-2026-10-30-r2`, persistito nella sessione con tutti i flag |
| Senza modello | messaggi chiari, nessuna scrittura |
| Flusso completo, modello simulato al confine | 3 segmenti analizzati; dubbio contraddetto mantenuto con domanda; export con il valore sospeso rifiutato (409); export dei 5 valori revisionati riuscito, provenienza SOURCE |
| Due FORM reali (compilazione, Trapani) da sessioni DeepSeek già registrate su `c838339` | export dal worker con testo DOCX identico alla registrazione; 22/22 e 9/9 valori scritti uguali |
| Switch `sezioni-2026-10-25` | flag identici al default precedente |
| Rete esterna | 0 tentativi, bloccati da un hook temporaneo fuori da Git |
| Dati reali | 31 sessioni, 495 revisioni, 211 turni e 379 file identici prima e dopo; `integrity_check` ok |

Evidenze grezze: `backend/data/compilation-audit/promozione-demo-20261031/` nell'app ordinaria
(esclusa da Git):
- manifest;
- impronte dei dati;
- esiti delle prove;
- strumenti di prova.
