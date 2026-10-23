# Proposta di verifica E2E dopo lo sprint (da approvare, nessun token speso)

**Stato:** solo proposta. Nessuna chiamata LLM finché l'utente non approva protocollo e budget.
Gli hash si riferiscono al commit finale dello sprint (`out/manifest-e2e.json` nella cartella
`backend/data/compilation-audit/sprint-sezioni-20261023-01/`).

## 1. Candidata

**Codice:** worktree `/home/montesano/tesi-sprint`, branch locale `sprint/2026-10-23-sezioni`,
commit e hash nel manifest. Il server osservato parte da questo worktree, non dal main tree.

**Ambiente del server osservato:** runtime temporanei come nella campagna precedente, mai l'app
live.

```
MAPI_GENERATION_REVISION=3
MAPI_DIALOGUE_REVISION=1
MAPI_DERIVATION_REVISION=1
MAPI_NARRATION_RECOVERY_REVISION=1
MAPI_BRANCH_SCOPE_REVISION=1
MAPI_HOLD_REREVIEW_REVISION=1
```

**Flag delle nuove sessioni** (verificati nel manifest):
- `backend_revision 13`, `option_authorization_revision 1`, `attribution_safety_revision 1`;
- `derivation_revision 1`, `dialogue_revision 1`, `generation_revision 3`;
- `narration_recovery_revision 1`, `branch_scope_revision 1`, `hold_rereview_revision 1`.

**Ambiente vuoto, cioè l'app ordinaria:** restano solo i primi quattro flag.

**Differenze dalla candidata corretta del 23 ottobre** (tutto il resto è identico, guardia rev 3
compresa):
- R1;
- revisione unica delle sospensioni attribuite a un'altra condizione;
- rivalidazione finale rev 3 delle proposte non revisionate o sospese.

## 2. Tentativi e scenari

**Sei tentativi, ordine fisso, uno alla volta:**
1. soresa2023-1
2. minervino-1
3. catanzaro-1
4. soresa2023-2
5. minervino-2
6. catanzaro-2

**Scenari e SOURCE:**
- scenari USER, politica di risposta (`user_policy_finale.cjs`), varianti e riferimenti v3 della
  valutazione finale, invariati;
- SOURCE `storico` per Minervino e Catanzaro, `nuova-source` per So.Re.Sa.

**Condizioni di partecipazione e avvalimento:** sono pertinenti in tutti e sei, senza scenari
nuovi. Ogni scenario dichiara partecipazione singola come società di ingegneria, senza
raggruppamenti, consorzi o altre forme:
- **So.Re.Sa.:** alternative esplicite di avvalimento (`p123`/`p125`) e blocchi dei componenti RT
  (13 delle 25 scritture sbagliate della rev 2).
- **Minervino:** opzioni di ramo con continuazioni; è il caso di R1.
- **Catanzaro:** sezioni 5.a-5.g.

Un caso con avvalimento positivo richiederebbe una nuova versione della fixture e un nuovo
riferimento, quindi non è proposto.

## 3. Budget

**Consumi della campagna precedente** (stessi tentativi, 2.570.195 token in totale, circa
0,40 USD):

| Modulo | Token per tentativo |
|---|---|
| So.Re.Sa. | 171-197k |
| Minervino | 388-571k |
| Catanzaro | 592-651k |

**Effetto atteso delle novità:**
- **R1:** più destinazioni nelle domande e nelle verifiche d'ambito già esistenti, nessuna domanda
  nuova nei dati registrati.
- **Revisione unica:** al massimo una finestra di revisione con più proposte.
- **Previsione:** circa 2,65 M token.

**Regole:**
- **Tetto vincolante:** 2.900.000 token complessivi per tutte le chiamate, ragionamento e retry
  inclusi.
- **Prenotazione atomica prima di ogni chiamata:** caratteri × 0,40 + 1.024 + `max_tokens`, senza
  sconti per la cache. Un consumo superiore alla prenotazione arresta tutto.
- **Soglie di avvio per tentativo:** So.Re.Sa. 300k, Minervino 700k, Catanzaro 750k. Un tentativo
  che non può partire è registrato come non eseguito.

**Costo** (tariffa registrata `pricing.json`):
- **Previsto:** 0,40-0,50 USD, fuori dalla fascia di punta e con la cache osservata.
- **Massimo teorico al tetto:**
  - circa 0,63 USD fuori punta senza cache;
  - circa 1,26 USD in fascia di punta senza cache.
- **Fascia di punta, da evitare:** 01:00-04:00 e 06:00-10:00 UTC nei giorni feriali.

## 4. Criteri di arresto

1. Prima scrittura non dimostrata accertata dalla revisione autoriale.
2. Una scrittura in una delle 25 destinazioni sbagliate della rev 2.
3. Un export di una proposta sospesa o non revisionata.
4. **Integrità:**
   - codice o harness cambiati;
   - consumo oltre la prenotazione;
   - tentativo non verificabile.
5. **Budget:** tentativo non avviabile, registrato e non sostituito.

**Fallimenti che non arrestano la campagna** (MODEL, NARRATOR, BACKEND, EXPORT, DRIVER): vengono
registrati e classificati, mai sostituiti. Nessun tentativo viene ripetuto o selezionato.

## 5. Misure ed esito (decisi prima)

**Favorevole se valgono tutte:**
- **(a)** 0 scritture non dimostrate;
- **(b)** 0 scritture nelle 25 destinazioni sbagliate;
- **(c)** nessuna di queste violazioni:
  - scrittura SOURCE in destinazioni non verificate;
  - export di proposte sospese o non revisionate;
  - risposta 409 per stato derivato;
- **(d)** DOCX in almeno 5 tentativi.

**Esiti alternativi:**
- **Parziale:** valgono (a)-(c), non (d).
- **Sfavorevole:** almeno una fra (a)-(c) non vale.

**Riportate senza soglia:**
- **Copertura:** nucleo per tentativo e mediana per modulo; scritture corrette della candidata
  corretta preservate (142 destinazioni).
- **Sicurezza:**
  - collegamenti aggiunti da R1 e loro esito (domanda, conferma, rifiuto);
  - proposte nelle 25 destinazioni.
- **Narratore:**
  - sospensioni marcate M;
  - sospensioni rientrate in revisione, rilasciate dal modello, risospese;
  - campi recuperati, con la prova per campo.
- **Robustezza:** segmenti falliti e recuperati, retry, fallimenti per classe.
- **Latenza:** tempo per tentativo e dell'analisi.
- **Costo:** token (cache e ragionamento) e USD.

**Revisione:**
- **Autoriale e non indipendente:** di tutte le scritture di ogni DOCX, prima del tentativo
  successivo.
- **Confronto:** descrittivo e non appaiato con la candidata corretta e con la monolitica.
- **Interpretazione:** un 6/6 non dimostra una superiorità generale sulla monolitica.

## 6. Cosa non cambia

- **Rimangono invariati:** baseline V12, risultati e criteri delle campagne precedenti, app live,
  branch di salvataggio.
- **Esclusi:** push e merge senza approvazione.
- **Preparazione dell'harness dopo l'approvazione:** copia congelata di quello della candidata
  corretta, con server osservato dal worktree dello sprint. Preregistrazione con data e hash prima
  della prima chiamata.
