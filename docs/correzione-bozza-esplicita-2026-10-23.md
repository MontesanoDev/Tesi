# Correzione di sicurezza: bozza esplicita via API (23 ottobre 2026)

**Intervento separato e prioritario** per il profilo ordinario:
- **Branch:** locale `fix/2026-10-23-bozza-esplicita`.
- **Worktree:** `/home/montesano/tesi-fix-bozza`.
- **Base:** `dd41e2e`.
- **Stato:** non è nell'app live e non è nella candidata sperimentale dello sprint, che resta
  congelata al codice `a9bd928`. Nessun push.

**Riferimenti:**
- **Grezzi:** `backend/data/compilation-audit/bozza-esplicita-20261023-01/`.
- **Diagnosi e risultati attesi:** `ATTESI.md`, scritto alle 16:57:13 UTC prima del codice.

## Difetto

`POST /compilation-sessions/{id}/global-draft` (`_selected`) verificava grounding, V14, K3,
condizioni, completezza, ambito e rivalidazione. Non verificava però revisione e sospensioni del
narratore, salvo nella modalità degradata del recupero.

**Effetto:** bastava chiedere per id una proposta sospesa per ottenere una bozza con quel valore.

**Portata:**
- **Chat e UI:** usano `export_selection`, che la esclude, quindi la lacuna non era raggiungibile
  da lì. `generateGlobalDraft` del frontend non è usato da nessun componente.
- **API diretta:** la lacuna era raggiungibile da qualunque client.

## Contratto verificato

**Selezione:** `docs/compilation-session-v1.md` dice che la chat costruisce i dati di
`global-draft` «dal proprio stato persistito, senza selezione manuale».

**Sospensioni:** non esiste un percorso di revisione manuale che le sblocchi. Il rilascio
legittimo, esplicito, autorizzato e verificabile resta:
- la risposta USER al dubbio collegato, con ricevuta registrata (`BLOCKER_ANSWERED`);
- oppure una revisione del narratore.

**`reviewed_by=USER` nel report:** registra il consenso alla bozza parziale, non una revisione
delle sospensioni.

## Correzione

**Regola:** in `_selected`, dopo **tutti** i controlli esistenti (fresca rivalidazione compresa),
per ogni sessione con uno stato di dialogo un id SOURCE è ammesso solo se è revisionato e non
sospeso, letto come lo legge `export_selection`. Altrimenti la risposta è 409 «Proposta sospesa o
non revisionata dalla sintesi».

**Funzione:** `reviewed_unheld_ids` in `compilation_global_dialogue.py`, identica a quella della
candidata, dove però resta limitata alla rev 3.

**Invariati:**
- sessioni storiche senza dialogo;
- valori USER (`user_candidate_ids`, con ricevute proprie);
- messaggi e codici dei gate esistenti.

**Prima versione scartata.** Una prima versione metteva il controllo prima degli altri gate e
cambiava il motivo del rifiuto in 34 test esistenti. Erano rifiuti già corretti, con un messaggio
diverso. Spostato in fondo, i 34 tornano verdi senza toccare i test.

## Verifiche

- **Nuovi test** (`backend/tests/test_compilation_explicit_draft_gate.py`, 10 casi):
  - proposta sospesa chiesta per id, profilo ordinario e P3: 409, le altre 200;
  - revisione non più corrente: 409;
  - rilascio legittimo con la risposta al dubbio collegato: 200;
  - sessione senza dialogo: invariata.
- **Sensibilità:** senza la correzione falliscono gli 8 casi positivi.
- **Suite completa:** 3.687 PASS (3.677 esistenti + 10 nuovi), 0 fallimenti; Ruff PASS
  (`out/suite-completa.log`, `out/ruff.log`).
- **Storico** (`storico_bozza.py`): 204 stati salvati (29 sessioni live e tutte le campagne). Nessuna
  delle 151 esportazioni registrate (`last_review.candidate_ids`) sarebbe stata rifiutata.

## Hash

Dettaglio in `out/hash-correzione.json`.

| | Valore |
|---|---|
| Commit della correzione | `c7c34923700cdb74b61069f2dc228128dfccb2b9` |
| Base | `dd41e2e` |
| Digest di `backend/app` e `frontend/src` (128 file) | `0a8d7f416939e1523de85cbef26e0368573920444e2428845162cde5e92fe2e6` |
| Candidata dello sprint, invariata | codice `ed349787…`, prompt `9ae0e014…` |

**Uso nella campagna E2E:** nessuno. La campagna ha usato solo la candidata congelata, che chiude
la stessa lacuna per la rev 3 con il proprio codice.
