# V12 — Applicabilità locale FORM

[Rapporto completo](../../docs/applicabilita-form-v12-2026-10-20.md) ·
[Esiti dei 67 replay](after-results.json) · [Due controesempi](CONTROESEMPI.json) ·
[Nuova prova UI](E2E-RESULT.json)

**PASS circoscritto al difetto di applicabilità.** Il backend blocca la sede
operativa nel ramo «se diversa dalla sede legale», anche quando il modello omette
il predicato. Il fatto SOURCE resta grounded. FALSE e UNKNOWN non autorizzano
scritture; assenso USER, revisione e grounding restano verifiche distinte.

| Controesempio originale | Prima | Dopo | DOCX corretto | PDF |
|---|---:|---:|---|---|
| Catanzaro B0-3 | 7 scritture | 6 | [DOCX](after/study/catanzaro/B0/rep-3/bozza.docx) | [PDF](after/study/catanzaro/B0/rep-3/render/bozza.pdf) |
| Catanzaro E1-3 | 9 scritture | 8 | [DOCX](after/study/catanzaro/E1/rep-3/bozza.docx) | [PDF](after/study/catanzaro/E1/rep-3/render/bozza.pdf) |

La sola destinazione rimossa è `t0.r8.c1`. Le altre 6/8 scritture, compresa la
sede legale, restano identiche. Gli output prima sono conservati separatamente
in `before-replay/`. Gli esperimenti originali B0/E1/E2-A restano intatti.

La nuova sessione reale ripete `value` con `conditions=[]`: il backend calcola
FALSE prima del narratore. Export ordinario: 15 testi SOURCE, zero USER/checkbox,
sede operativa vuota. [DOCX reale](e2e/catanzaro/bozza.docx),
[PDF](e2e/catanzaro/render/bozza.pdf), [dialogo](e2e/catanzaro/dialogo.md),
[verifica offline](e2e/catanzaro/offline-verification.json).
Una risposta indipendente resta parziale: numero senza data in `t25.r3.c1`;
non è corretta qui e il totale 15 non equivale a 15 risposte complete.

- 2.996 test backend PASS, 91 nuovi; Ruff PASS. Prima regressione negativa
  13 FAIL conservata e corretta nel nuovo controllo; test precedenti invariati.
- 67 replay di export: 65 DOCX esatti e le sole due rimozioni previste;
  Minervino 61, Trapani 17 e altri documenti storici conservati.
- 213 confronti aggiuntivi dei validatori V2–V12: 207 validazioni e sei rifiuti
  pregressi identici, salvo la nuova dimensione separata FORM.
  [Esiti](VALIDATOR-AFTER.json), [manifest/input](validator-inputs/manifest.json).
  Non sono 213 nuovi export o prove di qualità AI.
- XML/posizioni/CRC/prestampato/tabelle/controlli verificati. PDF prima/dopo e
  reale di 17 pagine; [ispezioni visive](VISUAL-CHECKS.json) campionate, non
  Microsoft Word desktop. [Preservazione](PRESERVAZIONE.json).

Snapshot del working tree: [prima](before/backend/app), [dopo](after-code/backend/app),
[manifest iniziale](FROZEN.json). [Protocollo UI](PROTOCOLLO-E2E.json) e
[emendamento prima delle inferenze](PROTOCOLLO-E2E-AMENDMENT-1.json).
Nessun cambio di modello/provider/prompt/FORM/architettura, nessuna integrazione
E1/E2-A, nessuna migrazione/reindicizzazione, commit o push.

La grammatica indipendente copre comparazioni locali esplicite supportate:
non è un interprete di tutte le condizioni del linguaggio naturale. Una
comparazione riconosciuta ma non dimostrata resta UNKNOWN e bloccata.
Non si deduce diversità da indirizzi scritti diversamente. Nessuna risoluzione
USER sostitutiva introdotta; le 13 destinazioni tabellari restano fuori intervento.

Backup separato: [audit-completo.tar.gz](audit-completo.tar.gz),
[SHA256](audit-completo.tar.gz.sha256), [manifest](BACKUP-MANIFEST.json),
[verifica estratta](VERIFICA-BACKUP.json). Include codice, input e risultati
dei replay, nuove acquisizioni/provider/browser e log, senza database privati,
credenziali, `.env` o chiavi. I grezzi esclusi da Git richiedono questo backup.

Riproduzione offline dalla radice del repository o dal pacchetto estratto,
usando Python con le dipendenze del `backend/uv.lock` conservato nello snapshot:

```bash
PYTHONPATH='benchmark ufficiale/form-applicability-20261020-01/after-code/backend' python backend/data/compilation-audit/form-applicability-20261020-01/replay.py after
PYTHONPATH='benchmark ufficiale/form-applicability-20261020-01/after-code/backend' python backend/data/compilation-audit/form-applicability-20261020-01/historical_validators.py after
PYTHONPATH='benchmark ufficiale/form-applicability-20261020-01/after-code/backend' python backend/data/compilation-audit/form-applicability-20261020-01/verify_real.py
```

I runner vietano rete e SQLite, usano le revisioni effettive e verificano i
risultati salvati. Per il controfattuale prima usare `before/backend`, con
`replay.py before-replay` e `historical_validators.py before`. Nessuna nuova
chiamata AI viene compiuta. Una futura inferenza non è garantita identica.
