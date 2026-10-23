# CRAA — motivazione MODEL e perdita del chiarimento

[Rapporto](../../docs/craa-motivazione-model-2026-10-20.md), [esito](ESITO.json),
[prima](diagnosis-before.json), [dopo](diagnosis-after.json),
[piani narratore realmente salvati](saved-dialogue.json).

Il solo limite225>200escludeva un chiarimento FORM altrimenti valido dal pool.
Corretto il trattamento della motivazione descrittiva: originale conservato,
warning separato,stessi controlli strutturali e fattuali. Contratto MODEL200
invariato;nessun fatto o valore autorizzato dal metadato.

Nessuna ricevuta USER cancellata. Il nome era nei messaggi originali; i piani
narratore salvati non aggiungono la domanda. Recuperata una possibilità del
dialogo,non dimostrata una nuova domanda reale o una nuova scrittura DOCX.

28nuovi test permanenti,101mirati e2.905backend PASS,Ruff PASS.
23DOCX precedenti identici,Minervino61conservate. Due audit CRAA hanno il solo
delta del chiarimento e contatori conseguenti;SOURCE/condizioni/binding intatti.
Zero chiamateLLM,costi nuovi zero. Nessun commit/push o baseline adottata.

- [DOCX CRAA storico invariato](replay/conserved/craa/bozza.docx).
- [File modificati](FILES-MODIFICATI.json), [preservazione](PRESERVAZIONE.json).
- [Backup completo](audit-completo.tar.gz), [SHA256](audit-completo.tar.gz.sha256), [verifica](VERIFICA-BACKUP.json).

Backlog intatto:nome firmatario,CCIAA invisibili nelPDF,campi composti,domande
ridondanti. Backup con codice prima/dopo e input congelati,senzaDB/chiavi/env;
verifiche estratte senza rete/SQLite e nessuna nuova inferenza.
