# CRAA — conservazione delle risposte USER

[Rapporto](../../docs/craa-risposte-user-2026-10-20.md), [esito](ESITO.json),
[DOCX reale](e2e/craa/bozza.docx), [PDF](e2e/craa/bozza.pdf),
[dialogo](e2e/craa/dialogo.md), [prova integrale USER](e2e/craa/prova-conservazione-USER.json).

Risposta reale da3.113caratteri conservata identica dopo recupero UI, invio,
router, guard, cronologia e SQLite. Tre decisioni verificate: una conferma di
ruolo, due rinvii senza attestazioni implicite. Nessun reinvio automatico.

Una globale nuova;13proposte valore,9grounded,7applicabili/scritte SOURCE,
0USER/checkbox,0scritture indebite rilevate. Due CCIAA rinviati e nome omesso
rimangono vuoti. Non è una correzione della visibilità CCIAA: geometrie intatte.
Il vecchio errore da225caratteri riguardava un metadato MODEL, non il messaggio
USER; rimane distinto e non modificato.

53nuovi test permanenti;2.877backend/126frontend PASS,lint/build/Ruff PASS.
22audit/DOCX precedenti esatti,Minervino61conservate. Costo reale stimato
0,021002USD,95.674token,7chiamate;nessun retry qualità. Primo driver senzaPTY:
riaperta la stessa conversazione;trace iniziale incompleto,trace/video finali
completi. Nessuna modifica applicativa durante la prova.

- [File modificati](FILES-MODIFICATI.json), [preservazione](PRESERVAZIONE.json).
- [Protocollo](PROTOCOLLO.json), [metriche](E2E-RISULTATO.json), [campi](e2e/craa/valutazione-campi.json).
- [Backup completo](audit-completo.tar.gz), [SHA256](audit-completo.tar.gz.sha256), [verifica estratta](VERIFICA-BACKUP.json).

Backup senzaDB/chiavi/env: codice prima/dopo,fixture,rawprovider,stati,dialoghi,
rendering e riferimenti necessari a23ricostruzioni offline (22precedenti+CRAA).
La copia UI è limitata alla scheda;un messaggio ricevuto è conservato anche dal
server. Storage indisponibile segnalato,recupero manuale e nessun assenso implicito.
Nessun commit/push o adozione di baseline. Arresto dopo consegna.
