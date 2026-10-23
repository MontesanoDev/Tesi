# Correzione della guardia rev 3: limite della motivazione (23 ottobre 2026)

Correzione autorizzata dall'utente dopo l'arresto della campagna `candidata-completa-20261023-01`
(`docs/candidata-completa-2026-10-23.md`). Piano congelato prima della modifica in
`backend/data/compilation-audit/guardia-rationale-rev3-20261023-01/PIANO.md`. Nessuna inferenza
reale, nessuna campagna, nessun commit.

## Difetto

Nella verifica d'ambito della rev 3 (`FormScopeCheck`) la motivazione (`rationale`) era limitata a
250 caratteri, ereditati dalla guardia ordinaria.
- Con il FORM completo la guardia la scrive più lunga.
- Nella campagna 3 verifiche su 7 sono state respinte solo per lunghezza (251, 261, 308 caratteri).
- Due avevano esito corretto SUPPORTED/SUPPORTED, entrambe in So.Re.Sa.: risposte USER perse e
  tentativo senza DOCX.
- La motivazione non è letta da nessuna decisione.

## Modifica

`app/compilation_reply_guard.py`, solo nella classe `FormScopeCheck`:
- `rationale` fino a 1000 caratteri, dichiarati anche nello schema inviato al modello;
- tutti gli altri vincoli invariati (slot 1-4, esiti, `scope_result` obbligatorio, campi extra
  vietati, duplicati, destinazioni effettive);
- la guardia del profilo ordinario (`ReplyScopeCheck`) resta a 250 caratteri;
- l'output della chiamata resta limitato a 768 token.

Copia del file prima della modifica: `before/` nell'audit (sha256 in `before/SHA256`).

## Verifiche (offline, provider simulato)

- **Nuovi test** in `tests/test_compilation_scope_review.py`:
  - le tre motivazioni registrate, con i loro esiti, mantengono la decisione del modello: due
    autorizzano, quella UNRELATED/AMBIGUOUS no;
  - restano respinte una motivazione oltre 1000 caratteri, un esito sconosciuto, un campo extra e
    uno slot fuori intervallo;
  - la guardia ordinaria respinge ancora 251 caratteri e accetta 250;
  - lo schema dichiara 1000 per la rev 3 e 250 per il profilo ordinario.
- **Sensibilità:** gli stessi test, eseguiti su una copia temporanea con la versione precedente,
  falliscono soltanto nei due casi SUPPORTED registrati, con lo stesso `ValidationError` della
  campagna, e nel test dello schema (`out/sensibilita-prima-della-correzione.log`).
- **Rivalidazione delle 7 verifiche registrate:** tutte valide; le 4 già valide hanno la stessa
  decisione (`out/rivalidazione-verifiche-registrate.json`). La decisione rivalidata è a livello di
  schema; l'autorizzazione effettiva richiede anche le destinazioni della sessione.
- **Test mirati:** 89 PASS (scope review e guardia), prima di spostare in un test separato il
  controllo dello schema; la versione finale dei test è inclusa nella suite completa.
- **Suite completa e Ruff:** vedere la sezione «Esito».

## Limiti

- La correzione rimuove una causa di perdita dei tentativi. Non dimostra la qualità semantica della
  guardia, né che la candidata completa elimini le scritture nei rami sbagliati.
- Con 4 verifiche lunghe una risposta può ancora superare i 768 token e venire respinta. Nella
  campagna le 7 risposte andavano da 86 a 340 token di output; la più lunga aveva 4 verifiche.
- Serve una nuova campagna preregistrata con nuovo congelamento. La campagna arrestata e i suoi
  risultati restano invariati.

## Esito

- **Suite backend completa:** 3.649 PASS, cioè i 3.640 precedenti più i 9 nuovi test; Ruff PASS
  (`out/suite-completa.log`).
- **Patch:** `out/patch-guardia.diff`, 3 righe aggiunte in una classe; copie dopo la modifica in
  `after/`.
- **Profilo ordinario e app live:** invariati. Il cambiamento agisce solo sulle sessioni con
  `generation_revision 3`, che non esistono nel DB live.
- **Prossimo passo, da autorizzare:** nuova campagna preregistrata sulla candidata completa, con
  nuovo congelamento del codice.
