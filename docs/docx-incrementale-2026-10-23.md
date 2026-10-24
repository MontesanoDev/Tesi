# Compilazione DOCX: interventi incrementali offline, 23 ottobre 2026

Base dello sprint `ff0d4f9140d2421fe2631e890ccd522c64c05fab`; branch
`miglioramenti/2026-10-23-docx-offline`, worktree `/home/montesano/tesi-docx-offline`.
Nessuna inferenza, nessuna E2E, nessuna adozione live. V12 e gli esperimenti
storici sono preservati. Revisione autoriale, non indipendente.

## Stato Git verificato

Il fetch di origin conferma i branch pubblicati. `main` è ancora `b8071d3` e
non contiene l'hotfix. La base del lavoro recente è `dd41e2e`; lo sprint termina
in `ff0d4f9`. L'hotfix generale esiste in `4890daa` sul branch security, ma nello
sprint il veto era presente soltanto per le sessioni rev 3. Il working tree
ordinario, molto modificato e su `prune-backend`, non viene usato per i commit.

## Priorità 1: integrazione dell'hotfix API esistente

Problema: un client dell'endpoint `global-draft` può chiedere esplicitamente un
ID SOURCE sospeso o non più revisionato. Nel profilo ordinario/P3 lo sprint
restituiva 200. La chat già escludeva tali ID. Il consenso alla bozza non è una
revisione delle singole sospensioni.

Riutilizzato `4890daa` con cherry-pick senza commit e verifica del diff: nello
sprint la funzione `reviewed_unheld_ids` esiste già. L'unica modifica applicativa
aggiunge otto righe a `_selected` in `compilation_global_sessions.py`, dopo
la rivalidazione e tutti i gate preesistenti. Le sessioni con dialogo accettano
solo SOURCE revisionate e non sospese. Restano invariati valori USER, sessioni
senza dialogo, V14, K3, analisi e narratore. Il veto rev 3 esistente è preservato.

Prove nuove, rete disabilitata e database/storage temporanei:

- prima: i dieci test originali dell'hotfix danno 8 FAIL e 2 PASS; gli otto
  fallimenti riproducono HTTP 200 al posto di 409;
- dopo: 62 PASS mirati, inclusi API, ripresa rev 3, K3 e autorizzazioni V14;
- replay storico: 210 stati disponibili, 157 esportazioni SOURCE registrate,
  nessuna nuova esclusione da parte del veto;
- preservazione: 245/245 scritture corrette con le conferme d'ambito simulate;
  211/245 con le sole ricevute registrate, identiche al riferimento. Le altre
  34 hanno ricevute rev 2 prive della prova rev 3: non sono regressioni del fix;
- i 25 controesempi di ramo mantengono l'esito precedente: sette bloccati da R1,
  diciotto ancora ammissibili con una guardia d'ambito simulata confermante.
  L'hotfix API non pretende di risolvere l'applicabilità semantica.

Suite completa: **3747 PASS, 3 SKIP in 359,23 s**; i tre casi richiedevano una
risposta storica locale, copiata identica e verificata separatamente: **3 PASS**.
Nessun test lasciato senza verifica. Ruff PASS. Prova di rollback successiva
al commit, registrata nel rapporto conclusivo.

Rollback previsto: `git revert <commit-di-integrazione>` in un worktree isolato.
Non richiede flag, migrazioni o modifiche ai dati. Ripristina anche la vulnerabilità
nei profili ordinari/P3: serve a dimostrare reversibilità, non è una promozione
consigliata. Il profilo rev 3 conserva il veto già presente nella base dello sprint.

Grezzi locali, esclusi da Git:
`backend/data/compilation-audit/docx-incrementale-20261023-01/` nel repository
originario. Piano e risultati prima/dopo separati; nessun risultato storico riscritto.
