# Preregistrazione — correzione delle sospensioni del narratore P3 (22 ottobre 2026)

Scritta prima di modificare `compilation_global_dialogue.py`. Codice del narratore = congelamento
della campagna P3 (`working-tree-before.json`). Unica modifica applicativa già fatta, per la
priorità immediata: `initial_state` rende P3 opt-in (sezione 0). Nessuna chiamata LLM finora.

## 0. Priorità immediata (già applicata alle 09:50 locali, prima di questo documento)

- Stato trovato (`out/live-check-prima.json`): l'app live (uvicorn `--reload` sul working tree)
  creava le nuove sessioni con `dialogue_revision 1` e `generation_revision 1`. Nessuna delle 29
  sessioni salvate nel DB live ha flag di revisione (ultima creata il 17 ottobre).
- Modifica: P3 diventa opt-in per un runtime sperimentale privato, con due variabili separate
  (`MAPI_DIALOGUE_REVISION=1`, `MAPI_GENERATION_REVISION=1`). Profilo predefinito delle nuove
  sessioni: `backend_revision 13`, `option_authorization_revision 1` (V14),
  `attribution_safety_revision 1` (K3). Le sessioni esistenti conservano i loro flag.
- Verifiche del fallback (criteri):
  F1. `out/live-check-dopo.json`: worker ricaricato dopo la modifica, nuove sessioni senza flag P3.
  F2. Albero applicativo pre-P3 ricostruito (V14 candidate-code + patch K3, 75/75 hash uguali a
      `p3-20261021-01/working-tree-before-P3.json`): `initial_state` identico al codice corrente
      senza variabili; corpo della richiesta globale identico per i quattro FORM.
  F3. Replay delle 215 sintesi legacy (V13, V14) con l'albero pre-P3 e con il codice corrente
      (dopo la correzione): impronte dei risultati identiche.
  F4. Moduli V14/K3 (`compilation_attribution_safety.py`, `compilation_option_regions.py`,
      `compilation_procedural_consent.py`) invariati rispetto al pre-P3.

## 1. Diagnosi (dimostrata, `replay_failures.py` → `out/replay-failures-prima.json`)

Le quattro sintesi respinte si riproducono deterministicamente: contesto ricostruito dagli
snapshot identico a quello della richiesta reale, prompt identico, stesso errore.

| Prova | Fase | Finestra | Errore | Causa |
|---|---|---|---|---|
| minervino-A1 | prosecuzione (revisione residua) | 11 | citazione | entrambe le citazioni sono record SOURCE letterali di `source_availability`, fuori dalla zona della proposta |
| minervino-B1 | iniziale | 40 | citazione | gruppo 35-38: citazione ancorata solo per la 36; gruppo 39-40: record SOURCE di `source_availability` |
| minervino-B2 | prosecuzione | 0 | esclusioni non valide | `hold_groups` con proposte 1-2 inesistenti (finestra vuota); dubbio su una condizione del pool |
| catanzaro-A2 | iniziale | 16 | citazione | citazione presa da una motivazione MODEL della copertura (`coverage.groups[21].reason`) |

Tutte le sospensioni delle tre prove con citazione sono dubbi SOURCE (soggetto/ruolo o dato
personale non documentato). Il validatore rifiutava l'intera sintesi: niente domande, niente export.

Diagnosi aggiuntiva (`governance_check.py` → `out/governance-prima.json`): nelle 32 sintesi P3,
45 sospensioni sono state legate a uno slot per il rilascio (D4). 18 slot governano davvero la
proposta (la proposta è fra i `field_ids` dello slot). 27 (tutte minervino-B2, sintesi 511ed591)
erano legate a slot RTP/studio associato che non le governano e sono state rilasciate dopo un
rinvio su quegli slot. La loro citazione è la clausola FORM letterale di una loro condizione
(`s1_c_partecipazione`, `s2_c_socing`), già decisa dalla richiesta iniziale.

## 2. Regole (solo sessioni con `dialogue_revision 1`; percorso legacy invariato)

H1. Nessun rifiuto dell'intera sintesi per una singola sospensione. Ogni riferimento è
    valutato a parte e la proposta citata resta sospesa:
    - citazione ancorata nella zona della proposta (regola esistente) → `RECORDED`;
    - citazione non ancorata (altrove nel contesto o assente) → `UNANCHORED_QUOTE`,
      `reason_status: unverified`, con `quote_location` registrata;
    - proposta citata in più gruppi → `REPEATED_REFERENCE`, tutte le motivazioni registrate.
    Solo `RECORDED` può essere legata a uno slot o rilasciata per ridondanza (regola esistente).
H2. Riferimenti a proposte inesistenti (fuori dalla finestra):
    - finestra vuota → registrati in `hold_transition.invalid_references` con il contenuto
      completo; nessun effetto (non c'è alcuna proposta da proteggere in questa revisione;
      le condizioni restano protette dai gate backend);
    - finestra non vuota → destinazione non determinabile: TUTTE le proposte della finestra
      restano sospese (`UNRESOLVED_REFERENCE`, non legate, nessun rilascio per ridondanza).
H3. Rilascio per risposta (D4) solo con collegamento verificabile dal backend, e solo per
    `RECORDED` con blocco `applicability`/`user_decision`:
    1. lo slot indicato dal narratore governa la proposta (proposta fra i suoi `field_ids`)
       → `blocker_key_basis: GOVERNING_SLOT`;
    2. altrimenti, la citazione è la clausola FORM (`form_evidence`) di esattamente una delle
       condizioni della proposta → `condition:<chiave>`, `OWN_CONDITION_QUOTE`;
    3. altrimenti nessun legame: la sospensione resta finché non è rivalutata.
    I legami già registrati nelle sessioni esistenti non vengono ricalcolati.
H4. Invariati: grounding, validatori FORM/SOURCE/USER, gate V14 e K3, prompt e schema del
    narratore, percorso legacy (citazione non ancorata = intera sintesi respinta, come V12/V14).

## 3. Esiti attesi sulle quattro sintesi (`predict.py` → `out/predicted-failures.json`)

Calcolati con le funzioni di export attuali, che la correzione non modifica.

| Prova | Esito | Sospese in finestra | Validazione | Domande | Export atteso |
|---|---|---|---|---|---|
| minervino-A1 | READY, nessun errore | 1-11 (tutte) | 11 × UNANCHORED_QUOTE | slot 1 (`field:p12.s0`), 6 (decisione luogo e data) | 39 |
| minervino-B1 | READY | 35-40 | 36 RECORDED, altre UNANCHORED_QUOTE | D6: prime tre condizioni aperte (slot 1, 2, 3) | 34 |
| minervino-B2 | READY | nessuna | 2 riferimenti non validi registrati | slot 3, 4, 5 | 35 |
| catanzaro-A2 | READY | 12-16 | 5 × UNANCHORED_QUOTE | nessuna (pool vuoto): proposta di bozza | 11 |

Per tutte: nessuna sospensione precedente rilasciata (minervino-A1 conserva `p14.s0`), nessun
legame a slot (sono dubbi SOURCE), nessuna proposta sospesa fra quelle esportabili.

## 4. Controesempi (test unitari, provider simulato)

C1 valida e ancorata → RECORDED, sospesa, le altre proposte esportabili.
C2 riferimento inesistente con finestra vuota → sintesi accettata, domande conservate,
   riferimento registrato, nessuna nuova sospensione.
C3 riferimento inesistente con finestra non vuota → tutte le proposte della finestra sospese,
   nessuna legata; proposte già revisionate fuori finestra non toccate.
C4 ambigua: citazione letterale di un'altra proposta o di un record SOURCE del contesto →
   UNANCHORED_QUOTE con posizione; resta sospesa anche dopo la risposta allo slot indicato.
C5 non letterale (parafrasi) → UNANCHORED_QUOTE, posizione `not_found`, sospesa.
C6 proposta in due gruppi → REPEATED_REFERENCE, sospesa, non legata.
C7 collegata a dichiarazione procedurale (slot di autorizzazione che governa la proposta) →
   legata (GOVERNING_SLOT); dopo un rinvio la sospensione cade ma il gate V14 continua a
   impedire l'export senza autorizzazione accettata.
C8 slot non pertinente e citazione diversa dalle condizioni proprie → RECORDED non legata;
   dopo la risposta a quello slot resta sospesa.
C9 slot non pertinente ma citazione = clausola di una condizione propria → legata a quella
   condizione; se già decisa, sospensione soppressa subito e registrata nella transizione.
C10 sessione legacy: citazione non ancorata → intera sintesi respinta come prima.
C11 sospensioni ereditate non citate restano sospese anche con riferimenti non validi.

## 5. Replay e regressioni

R1. `replay_all.py dopo`: 247 sintesi. Le 215 legacy (V13, V14): impronte identiche a `prima`.
    Le 32 P3: identiche per errore, fase, domande, sospese, export e rilasci, salvo le quattro
    respinte (ora accettate come in sezione 3) e la sintesi minervino-B2 511ed591, dove le 27
    sospensioni legate a slot non pertinenti diventano legate alla propria condizione già
    decisa e soppresse subito. Campi nuovi dei record (posizione, base del legame) attesi.
R2. Replay a catena delle 16 prove P3: export finale identico per le 12 prove riuscite.
R3. Nessuna proposta esportabile bloccata da K3 o dal gate di autorizzazione V14.
R4. Suite backend completa e Ruff verdi; test P3 aggiornati per l'opt-in.

## 6. E2E breve (solo se 1-5 superati; protocollo congelato a parte prima dell'inferenza)

- Runtime isolato clonato dal seme V12, porte 8004/5177, `MAPI_DIALOGUE_REVISION=1`,
  generazione monolitica (segmentazione esclusa: confronto generazione tenuto separato).
- 8 prove, non sostituibili: minervino ×2, catanzaro ×2 (falliti prima), cesano-esteso,
  cesano-breve, craa-autorizza, craa-ramo (riusciti prima). Stessi FORM, SOURCE, scenari e
  politica USER del braccio A della campagna P3 → confronto appaiato con A1/A2.
- Budget 1,5 milioni di token (blocco automatico), massimo 60 chiamate e 4 turni di risposta
  per prova, un export, nessun retry selettivo.
- Misure: DOCX/tentativi; sintesi respinte; sospensioni per validazione e base del legame;
  riferimenti non validi; campi core corretti/omessi/scritture non dimostrate (revisione
  dell'autore, non indipendente); conferme ridondanti; domande ripetute; V14/K3; token e tempi.
- Criteri: 0 sintesi respinte per validazione delle sospensioni; DOCX 8/8 (7/8 solo con causa
  estranea al narratore, documentata); 0 scritture non dimostrate; 0 aggiramenti V14/K3; sui
  documenti riusciti prima nessun peggioramento grave (mediana core ≥ mediana appaiata A − 20
  punti). Arresto immediato per una scrittura non dimostrata o un aggiramento V14/K3.

## 7. Decisione

Se 1-6 sono superati, il rapporto potrà proporre la riattivazione del solo dialogo P3; P3 resta
disattivato nelle nuove sessioni finché l'utente non decide. La generazione per sezioni non è
valutata qui e resta opt-in. Se un criterio offline fallisce: niente E2E, arresto con diagnosi.
Le conferme ridondanti vengono contate, non corrette in questo intervento.
