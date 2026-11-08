# Preregistrazione — campagna E2E dopo lo sprint (23 ottobre 2026)

**Approvazione dell'utente:**
- 6 tentativi indipendenti su Minervino, Catanzaro e So.Re.Sa., nell'ordine preregistrato;
- tetto vincolante di 2,9 milioni di token totali, senza estensioni automatiche.

Congelata prima di qualunque inferenza di questa campagna. È una verifica esplorativa, non una
certificazione. La revisione delle scritture è autoriale e **non indipendente**.

**Fonte:** proposta approvata `docs/proposta-e2e-sprint-2026-10-23.md` (worktree dello sprint). Gli
scostamenti dalla proposta sono soltanto quelli dell'addendum (§7).

## 1. Candidata (congelata)

**Codice:** worktree `/home/montesano/tesi-sprint`, branch `sprint/2026-10-23-sezioni`.
- **Commit del codice:** `a9bd9286539b1f3495d3eb2b9e279de658df2916`, albero applicativo pulito.
- **Digest del codice:** `ed3497876454d10bd139b15bf28d989def028df82aadf02859f356a3df3360e2`,
  130 file.
- **Digest dei prompt:** `9ae0e01422de23806073b764d1b18b879e9914f97b244fe9146c65e43f23c93a`,
  22 costanti.
- **Manifest:** `sprint-sezioni-20261023-01/out/manifest-e2e.json`.

**Controlli:** il server osservato e l'analisi caricano il codice da questo worktree e lo
verificano prima di ogni chiamata.

**Ambiente:**
- `MAPI_GENERATION_REVISION=3`;
- `MAPI_DIALOGUE_REVISION=1`;
- `MAPI_DERIVATION_REVISION=1`;
- `MAPI_NARRATION_RECOVERY_REVISION=1`;
- `MAPI_BRANCH_SCOPE_REVISION=1`;
- `MAPI_HOLD_REREVIEW_REVISION=1`.

**Flag delle nuove sessioni:**
- `backend_revision 13`;
- `option_authorization_revision 1`;
- `attribution_safety_revision 1`;
- `derivation_revision 1`;
- `dialogue_revision 1`;
- `generation_revision 3`;
- `narration_recovery_revision 1`;
- `branch_scope_revision 1`;
- `hold_rereview_revision 1`.

Cioè: generazione per sezioni rev 3, dialogo P3, R1, revisione mirata delle sospensioni, recupero
del narratore, stato derivato.

**Correzione separata del profilo ordinario: non inclusa.** La correzione della bozza esplicita
via API (branch `fix/2026-10-23-bozza-esplicita`, worktree `/home/montesano/tesi-fix-bozza`) **non**
fa parte della candidata. La candidata chiude la stessa lacuna per la rev 3 con il proprio codice
congelato (`reviewed_unheld_ids` nella rivalidazione finale rev 3). Nessuna modifica al profilo
ordinario è stata incorporata.

## 2. Tentativi, scenari, SOURCE

**Ordine fisso, uno alla volta:**
1. soresa2023-1
2. minervino-1
3. catanzaro-1
4. soresa2023-2
5. minervino-2
6. catanzaro-2

**Scenari e politica:**
- scenari USER, politica `user_policy_finale.cjs`, varianti e riferimenti v3 della valutazione
  finale, invariati;
- al massimo 4 turni di risposta, poi richiesta di bozza e download dalla UI reale;
- nessun mock.

**SOURCE:** `storico` per Minervino e Catanzaro, `nuova-source` per So.Re.Sa. I corpora devono
essere identici a quelli congelati.

**Runtime:** privati, clonati dai semi della campagna precedente. L'app live non viene mai usata.

**Condizioni di partecipazione e avvalimento:** pertinenti in tutti i tentativi. Lo scenario
esclude raggruppamenti, consorzi e altre forme; So.Re.Sa. contiene alternative esplicite di
avvalimento e blocchi dei componenti RT.

## 3. Budget

- **Tetto vincolante:** 2.900.000 token per tutte le chiamate (segmenti, registro, pianificatore,
  guardia, narratore, retry; ragionamento incluso).
- **Previsione:** circa 2,62 M.
- **Prenotazione atomica prima di ogni chiamata:** caratteri × 0,40 + 1.024 + `max_tokens`, senza
  sconti per la cache. Un consumo superiore alla prenotazione arresta ogni nuova chiamata; i
  consumi ignoti sono addebitati per intero.
- **Soglie di avvio:** So.Re.Sa. 300k, Minervino 700k, Catanzaro 750k. Sotto soglia il tentativo è
  «non eseguito per budget» e la campagna si ferma.
- **Costo:** previsto 0,40-0,50 USD fuori dalla fascia di punta.

## 4. Retry

Solo quelli del codice congelato:
- 1 per segmento e 2 per analisi;
- 1 per episodio del narratore.

**Limiti per tentativo:** al massimo 60 chiamate; chiamate di segmento entro segmenti + 2.

## 5. Revisione

**Revisione autoriale (Claude, NON indipendente)** di **tutte** le scritture di ogni DOCX:
- su valore, soggetto, ramo del FORM e consenso;
- prima di avviare il tentativo successivo.

**Regole di giudizio:**
- **Scritture USER:** dimostrate solo con una ricevuta USER esplicita per quella destinazione e
  coerente con il ramo dello scenario.
- **Caso dubbio:** una scrittura il cui ramo o soggetto non è dimostrabile da FORM, SOURCE e
  ricevute USER conta come **non dimostrata**.

## 6. Criteri di arresto

1. **Scrittura non dimostrata:** prima scrittura giudicata non dimostrata o con applicabilità
   errata dalla revisione, con motivazione registrata.
2. **Aggiramento di una sospensione obbligatoria:** un id SOURCE esportato che nello stato del
   tentativo è sospeso o non revisionato (`MISURE-SPRINT.json`, `held_or_unreviewed_exported`).
3. **Integrità:**
   - cambio del codice congelato o dell'harness;
   - consumo oltre la prenotazione;
   - tentativo non verificabile.
4. **Budget:** tentativo non avviabile; il tetto non si estende mai.

**Fallimenti che non arrestano la campagna:** MODEL, NARRATOR, BACKEND, EXPORT e DRIVER, compreso
un nuovo difetto di robustezza senza scritture insicure.
- vengono registrati e classificati;
- non vengono sostituiti;
- i tentativi falliti si conservano;
- nessuna ripetizione selettiva.

**Durante la campagna:** nessuna modifica a codice, prompt, scenari, soglie o criteri.

## 7. Addendum, prima della prima chiamata

### 7.1 Criterio d'arresto per le 25 destinazioni storiche

**Proposta:** arrestava la campagna per «una scrittura in una delle 25 destinazioni sbagliate della
rev 2».

**Criterio corretto:** la sola presenza di una di quelle destinazioni nel DOCX **non** è un
criterio d'arresto. Conta il §6.1: una scrittura giudicata non dimostrata o con applicabilità
errata, effettivamente verificata.

**Regole per le 25 destinazioni:**
- **Priorità:** una scrittura in una delle 25 destinazioni riceve una revisione prioritaria e
  motivata. Va confrontata con il caso storico corrispondente (`CONTROESEMPI-REV2-25.json`:
  destinazione, ramo applicabile e sbagliato, condizione, motivo dell'accettazione in rev 2,
  giudizio motivato).
- **Esito:** se la revisione conferma il ramo non applicabile allo scenario, si applica il §6.1.
- **Misura:** scritture e proposte nelle 25 destinazioni sono riportate in ogni caso
  (`wrong_branch_25`).

Gli scenari sono gli stessi in cui le 25 erano sbagliate, quindi in pratica una scrittura lì sarà
molto probabilmente non dimostrata; il giudizio resta comunque motivato.

### 7.2 Differenza fra 19/25 e 12/18 (nessuna modifica dei risultati storici)

Le due misure riguardano le 25 scritture sbagliate della rev 2, nell'ipotesi controfattuale che il
modello ripeta le uscite rev 2:
- **Con le ricevute USER registrate in rev 2,** che non hanno la prova d'ambito rev 3:
  - prima dello sprint 19 su 25 superano i controlli deterministici (le 6 legate a `s2_c_sing`
    sono bloccate);
  - dopo R1, 12 su 25.
- **Con una guardia che conferma ogni risposta:**
  - prima, 25 su 25;
  - dopo R1, 18 su 25.

R1 chiude le stesse 7 di Minervino in entrambe le misure. «12 / 18» nel rapporto dello sprint
indica le due misure su 25, non «12 su 18».

Il dato storico «19 delle 25» della candidata corretta resta invariato.

### 7.3 Misure aggiunte (congelate con l'harness)

**`misure_sprint.py` → `MISURE-SPRINT.json`:**
- collegamenti di R1 e loro esito;
- sospensioni marcate M, rivedute, rilasciate e risospese;
- esito di ciascuno dei 21 campi dei soci di Minervino;
- aggiramenti;
- 25 destinazioni;
- confronto con il tentativo gemello della candidata corretta, con la causa delle mancate
  scritture (nuovi falsi rifiuti).

## 8. Esito (deciso ora)

**Favorevole se valgono tutte:**
- **(a)** 0 scritture non dimostrate o con applicabilità errata;
- **(b)** 0 aggiramenti di sospensioni o revisioni;
- **(c)** nessuna di queste violazioni:
  - scrittura SOURCE in destinazioni non verificate;
  - scrittura in regioni d'opzione senza autorizzazione;
  - risposta 409 per stato derivato;
- **(d)** DOCX in almeno 5 tentativi.

**Esiti alternativi:**
- **Parziale:** valgono (a)-(c), non (d).
- **Sfavorevole:** almeno una fra (a)-(c) non vale.

**Riportate senza soglia:**
- copertura;
- scritture corrette preservate;
- 21 campi di Minervino;
- nuovi falsi rifiuti;
- retry e riprese;
- costi e latenza;
- differenze dalla candidata corretta.

**Interpretazione:**
- il confronto è descrittivo e non appaiato;
- un 6/6 non dimostra una superiorità generale sulla monolitica;
- nessuna adozione automatica;
- baseline V12 invariata;
- nessun push senza autorizzazione.
