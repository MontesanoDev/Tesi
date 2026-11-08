# Caselle testuali DOCX — correzione offline del 26 ottobre 2026

Revisione autoriale Codex, non indipendente. App ordinaria invariata; nessuna
inferenza o campagna reale. Candidata su `fix/2026-10-26-checkbox-testuali`,
worktree `/home/montesano/tesi-checkbox-20261026`.

## Prima: snapshot e riproduzione

Snapshot `1785357e539e3213a1e35002db8f962ef8e60f1e`, branch
`snapshot/2026-10-26-stato-ordinario`: 373 file applicativi uguali al codice live
e al branch pubblicato `aaaaa44`. Il backup privato del codice e dei dati è
stato ripristinato e verificato; seconda copia verificata in
`D:\Backup-tesi-2026-10-23\stato-ordinario-20261026-01\`.
Dettagli in [snapshot-stato-ordinario-2026-10-26.md](snapshot-stato-ordinario-2026-10-26.md).

Il FORM sintetico congelato del 25 ottobre contiene al paragrafo 16 una casella
`[]` in normali elementi `w:t`, fuori dalle tabelle. Non è un controllo Word
né un simbolo `w:sym`. Prima: nessuna destinazione nel catalogo e writer che
rifiuta l'ID. I due test di riproduzione falliscono sulla base.

Piano precedente al codice: [piano-checkbox-testuali-2026-10-26.md](piano-checkbox-testuali-2026-10-26.md),
SHA-256 `51c07133ff476c346a3956ae8f5918dd5658a5ede619cca7ae3176652b721d09`.

## Modifica e autorizzazioni

- Adapter strutturale di 54 righe per un marcatore iniziale `[]`, `[ ]`, `[x]`
  o `[X]` seguito da testo, in un paragrafo semplice del corpo o di una cella.
  Simboli Word, contenuti complessi, marcatori interni o multipli restano esclusi.
- ID `pN.txcb0` distinti dalle checkbox native. Le posizioni originali vengono
  conservate prima delle scritture testuali: dati inseriti non possono creare
  nuove destinazioni; eliminare paragrafi vuoti precedenti non sposta la casella.
- Gruppi e decisioni USER usano il percorso esistente. Una proposta SOURCE da
  sola non seleziona una casella testuale. Servono il gruppo validato, la clausola
  FORM locale intera e la risposta USER verificata per quel gruppo; restano
  attivi applicabilità, V14, K3, sospensioni e rivalidazione all'export.
- Profilo esplicito `MAPI_COMPILATION_PROFILE=checkbox-testuali-2026-10-26`;
  `text_checkbox_revision=1` persistito. Non impostato nell'app ordinaria.
  Le sessioni precedenti mantengono il catalogo e il profilo originari.

File funzionali: nuovo `backend/app/docx_text_checkboxes.py`;
`docx_templates.py`, `docx_checkboxes.py`, `compilation_catalog.py`,
`compilation_choices.py`, `compilation_form_option_scope.py`,
`compilation_profile.py`, `compilation_sessions.py`,
`compilation_global_sessions.py` e `compilation_global.py`.
Nessuna dipendenza aggiunta, migrazione o modifica del retrieval.

Due dettagli necessari sono emersi nelle verifiche, prima della valutazione finale:
riconoscere la casella non deve cancellare il contesto dei campi successivi;
le due opzioni del caso storico, separate da `OPPURE`, devono poter costituire
un gruppo completo. Sono stati prima riprodotti con test fallenti e poi corretti.
Il caso con testo estraneo fra le opzioni continua a essere respinto. Una breve
istruzione al modello viene aggiunta solo quando il catalogo contiene caselle
testuali; il prompt ordinario resta identico.

## Esiti verificati

- **117 test mirati PASS**: writer, gruppi nativi/testuali e API, con FTS5 e Qdrant.
  Scelta verificata: casella marcata. Mancata scelta, rinvio, risposta ad altro
  slot, verifica d'ambito assente: rifiuto. Una condizione falsa o ignota blocca
  l'export anche se la checkbox è stata scelta; la condizione confermata lo consente.
  Provati citazione incompleta, dati SOURCE insufficienti per una scelta,
  istruzione FORM omessa, ID invariati, run spezzati, celle e originali preservati.
- **Suite backend: 3.980 PASS, 8 SKIP**, poi **8/8 PASS** per i test storici
  saltati inizialmente per artefatti locali assenti nel worktree. Copiati sette
  artefatti e verificati tramite hash; originali storici intatti. Totale delle
  verifiche completate: 3.988 test. Ruff PASS.
- **DOCX reale del caso sintetico:** `p16.txcb0` riconosciuto; `[X]` quando
  selezionato, `[]` quando non selezionato. Controllati XML e PDF di entrambe
  le varianti; gli altri paragrafi e le altre parti del pacchetto restano uguali,
  salvo l'avviso di bozza. Questa è una prova del writer con booleani di test;
  l'autorizzazione è verificata separatamente nei test API con provider simulati.
- I 373 file applicativi ordinari coincidono ancora con lo snapshot. Nessun
  aggiornamento dell'app, delle sessioni precedenti o della baseline V12.

Le due prime esecuzioni della suite sono state interrotte durante lo sviluppo
per correggere i casi locali appena riprodotti; non vengono contate come suite
superate. La suite completa riguarda il codice finale, verificato tramite hash.

## Replay storici: sicurezza conservata, ricevute non trasferibili

Rigioco delle risposte registrate, senza nuove inferenze o modifiche ai benchmark.
Confronto con `sezioni-2026-10-25`, non con una baseline positiva da 245/245.

| Misura | Profilo ordinario | Catalogo testuale attivo |
|---|---:|---:|
| Errori storici ancora ammessi, ricevute registrate | 0/25 | 0/25 |
| Errori storici ancora ammessi, guardia SUPPORTED simulata | 0/25 | 0/25 |
| Positivi congelati, guardia SUPPORTED simulata | 243/245 | 243/245 |
| Positivi estesi, guardia SUPPORTED simulata | 236/240 | 236/240 |
| Positivi congelati, vecchie ricevute senza nuova verifica | 211/245 | 197/245 |
| Positivi estesi, vecchie ricevute senza nuova verifica | 236/240 | 226/240 |

Non occultare le ultime due righe: applicare un catalogo ampliato a vecchie
ricevute non equivale a una sessione nuova. Le ricevute sono legate al FORM e
alle destinazioni verificate. Questi replay non autorizzano un aggiornamento
implicito delle sessioni; con il vecchio profilo i risultati rimangono invariati.
Una nuova verifica d'ambito simulata conserva i positivi precedenti, ma non
dimostra che il modello reale interpreterà tutte le nuove scelte correttamente.
I due giudizi controversi del corpus da 245 rimangono aperti e immutati.

## Limiti e rollback

Supporto circoscritto ai marcatori dichiarati, non a ogni casella grafica o font
simbolico. Il modello deve ancora proporre gruppi e condizioni appropriati;
non è stata dimostrata una nuova compilazione reale dell'avvalimento. Nessuna
trasformazione automatica della vecchia risposta sull'avvalimento in consenso
alla nuova casella. L'aggiunta di destinazioni può aumentare le domande.

Rollback del solo fix: `git revert <SHA-del-fix>` in un worktree o branch isolato.
Il padre è `1785357`; non occorrono migrazioni, ripristini dei dati o modifiche
alle dipendenze. Togliere il profilo sperimentale disattiva la funzione per le
nuove sessioni; le eventuali sessioni sperimentali conservano il proprio flag
e richiedono il codice della candidata per riprendere la nuova funzionalità.
Non cancellarle e non convertirle implicitamente. L'app ordinaria non richiede
rollback, perché non ha ricevuto questa modifica.

SHA del fix e verifica concreta del revert sono registrati nell'handoff finale
e nel file locale `commit-rollback.json`, per evitare un riferimento circolare
nel commit stesso. Nessun push, merge o adozione automatica.

Artefatti durevoli:
`backend/data/compilation-audit/snapshot-checkbox-20261026-01/` nel repository
ordinario: piano congelato, test prima/dopo, suite, replay, manifesti e
`render/` con i due DOCX/PDF. I provider dei test sono simulati; budget LLM **zero**.
