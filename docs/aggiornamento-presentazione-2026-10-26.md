# Presentazione dell'architettura — aggiornamento del 26 ottobre 2026

Aggiornato `architettura_rag_compilazione_docx_tesi_v2.pptx`, da 24 a 25 slide,
con PDF omonimo nella radice del progetto. Conservati stile, diagrammi, grafici
e dati delle campagne storiche. Aggiunta la prova reale del 25 ottobre;
aggiornati controlli, profilo adottato, limiti, fonti e note del relatore.

## Contenuti verificati nei rapporti

- Profilo delle nuove sessioni `sezioni-2026-10-25`: protezione di opzioni ASCII
  e istruzioni FORM condizionali; sessioni precedenti invariate.
- Replay: 0/25 errori storici ammissibili. Positivi congelati: **243/245**, con
  due giudizi USER da riesaminare; positive estese 236/240, invariate. Nessuna
  modifica ai giudizi o ai risultati storici.
- Prova reale: due DOCX; So.Re.Sa. con 7 scritture corrette e nucleo **7/15**;
  sintetico RT con ausiliaria, 8/8 valori attesi. Totale 247.443 token,
  costo stimato 0,043 USD; tempi 187 e 51 secondi.
- Il nuovo veto non è stato determinante da solo nelle due prove reali;
  regola A2 non esercitata. Revisioni autoriali, non indipendenti.
- Caselle ASCII da completare a mano. Resta la dipendenza dalle strutture
  FORM riconosciute: il replay non dimostra applicabilità universale.
- La ripresa reale con cache è documentata in un tentativo della campagna
  incrementale del 24 ottobre; i dieci scenari di ripresa e i retry rimangono
  verifiche offline.

Fonti: [istruzioni FORM](istruzioni-form-2026-10-25.md),
[adozione e prova reale](rami-e2e-2026-10-25.md), `compilation_profile.py` e
`compilation_form_option_scope.py`. I rapporti storici sprint e incrementale
citati nell'appendice sono disponibili nella `docs/` del branch
`miglioramenti/2026-10-25-ambiti-form`, worktree `/home/montesano/tesi-ambiti-form`.
I 3.940 test indicati nelle slide sono quelli registrati all'adozione,
non una suite rieseguita durante questo aggiornamento documentale.

## Verifiche e ripristino

- PPTX: archivio integro, 124 parti XML analizzabili, riferimenti interni risolti,
  25 slide e 25 pagine di note.
- PDF: rendering LibreOffice di 25 pagine, testo delle slide presente e dentro
  i margini; controllo visivo delle slide modificate. Corrette due sovrapposizioni.
  Microsoft PowerPoint non è stato avviato in questo ambiente.
- Grafici, workbook incorporati, immagini e tema conservati byte per byte;
  nei layout condivisi aggiornata soltanto la data del piè di pagina.
- Nessuna modifica a codice applicativo, sessioni o benchmark; nessuna nuova
  inferenza, campagna, adozione, commit o push.

Originale e controlli sono in
`backend/data/compilation-audit/presentazione-architettura-20261026-01/`:
`backup/`, script di aggiornamento e validazione, rendering, `changes.json`,
`validation-final.json` e `delivery.json`. Il backup è separato da Git.

SHA-256 originale:
`dc3bea24269514b93f89edfd38aa53944372c22707883edc6f3ddda5e1253202`.

SHA-256 PPTX aggiornato:
`bcf761e848ce9cbea91becd49b06a0215f1bf246ed3a2765e3eaea256cf43449`.

Per recuperare la versione precedente, copiare il PPTX dalla cartella `backup/`
con un nome distinto; la sua identità con il file iniziale è verificata tramite
SHA-256. Non occorre intervenire sul codice o sul profilo dell'app.
