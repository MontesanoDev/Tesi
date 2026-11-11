# Sottoscrittore vuoto — diagnosi della prova manuale del 31 ottobre 2026

**Causa dimostrata:** domanda e risposta multivalore sono state associate al solo campo
nome. Il router ha registrato tutta l'anagrafica come nome del sottoscrittore; la guardia
l'ha accettata. Quel testo composto non identifica il record personale nelle SOURCE,
quindi il riuso degli altri dati non parte. Il nome registrato resta inoltre subordinato
a una conferma d'identità mai acquisita. L'export applica questi blocchi: non cancella
valori già scritti e non perde una ricevuta valida.

Il percorso si riproduce anche col codice R2 precedente. È un limite preesistente attivato
da output LLM differenti, **non una regressione dimostrata del fix `de2f5de`**.
Nessuna patch speculativa; promozione sospesa in attesa di una verifica/correzione mirata
del rapporto fra domanda, campo nome e identificazione della persona.

Versione candidata `a0cc223bbad6355b57f10018119776c4696d893b`, branch
`narratore-chiarezza/2026-10-31`, profilo `sezioni-2026-10-30-r2`, istanza 8001/5174.
Sessione reale `d9be7d34947145f69892bfc0bf535bad`, versione 15; DOCX
`4320c2abb8e54424ae3272ec7e364eac`, generato dalla versione 14, 50 scritture.
Controllati sia il report d'export sia i paragrafi XML del DOCX scaricato dall'API.

1. **Analisi iniziale:** nessuna proposta per i nove campi personali; condizione
   `s1_c_firmatario=unknown`. Mancava anche la chiarificazione esplicita per il nome,
   presente invece nel run R2. Il backend ha creato la domanda di ripiego per `p12.s0`,
   etichettata «Il sottoscritto».
2. **Narratore:** nell'output reale ha chiesto nome, cognome, nascita e residenza, ma la
   destinazione della domanda è rimasta soltanto `field_ids=[p12.s0]`.
3. **Router e guardia:** il router ha estratto come unico valore
   «Leonardo Montemurro, nato a Lecce (LE) il 14/11/1982, residente a Bari (BA), via Amedeo 24».
   La guardia ha restituito `SUPPORTED/SUPPORTED` per questo slot. Nessun rifiuto del
   sottoscrittore; il validatore locale non ha prodotto codici d'errore e il controllo di
   completezza non aveva un controllo applicabile a quel campo (`null`).
4. **Ricevuta:** azione `VALUE`, ambito soltanto `p12.s0`, tuttora valida. Gli altri campi
   non hanno ricevute USER. `continuation_receipt()` dice «Ho registrato» dopo aver salvato
   la risposta, senza verificare che essa sia esportabile: da qui il messaggio fuorviante.
5. **SOURCE:** `integrazione-company.md` contiene tutti i dati, compresi codice fiscale e
   carica. `_selection()` restituisce l'intero valore registrato; `_identity()` richiede
   corrispondenza con nome/cognome del profilo e non trova quella lunga stringa. La stessa
   funzione trova correttamente «Leonardo Montemurro». Nessun dato SOURCE è stato rifiutato
   come falso: il riuso non è arrivato a proporlo.
6. **Condizioni ed export:** manca `condition:s1_c_firmatario`. Una successiva domanda
   chiede nuovamente conferma su Leonardo; il messaggio finale chiede rinvii e bozza
   parziale, senza rispondere a quella conferma. La scelta della checkbox 4 non la
   sostituisce. `export_selection()` esclude tutti i nove campi. Il riepilogo dei vuoti
   considera le proposte SOURCE documentate: non segnala questo valore USER bloccato né
   gli otto campi senza proposta, contribuendo alla scarsa visibilità dell'esito.

| Campo | ID | Motivo del vuoto nella candidata |
|---|---|---|
| Nome e cognome | `p12.s0` | Valore USER composto e ricevuta valida; conferma d'identità aperta. |
| Comune di nascita | `p12.s1` | Presente nel messaggio, non assegnato al campo; nessun riuso SOURCE. |
| Provincia di nascita | `p12.s2` | Presente nel messaggio, non assegnata al campo; nessun riuso SOURCE. |
| Data di nascita | `p12.s3` | Presente nel messaggio, non assegnata al campo; nessun riuso SOURCE. |
| Comune di residenza | `p13.s0` | Presente nel messaggio, non assegnato al campo; nessun riuso SOURCE. |
| Provincia di residenza | `p13.s1` | Presente nel messaggio, non assegnata al campo; nessun riuso SOURCE. |
| Via e civico | `p13.s2` | Presenti nel messaggio, non assegnati al campo; nessun riuso SOURCE. |
| Codice fiscale | `p13.s3` | Documentato nelle SOURCE, ma nessuna proposta derivata. |
| Carica | `p14.s0` | Documentata nelle SOURCE, ma nessuna proposta derivata; le conferme sull'operatore non coprono questo campo. |

Anche gli otto campi privi di proposta conservano la condizione d'identità aperta.
Per la carica sono inoltre presenti `s1_c_partecipante` e `s2_c_part`: confermate per altri
campi, con ricevute che non includono `p14.s0`. Non sarebbe sufficiente forzare la sola
conferma d'identità per ottenere una compilazione corretta.

Il **rinvio sull'albo non causa il vuoto del sottoscrittore**. La ricevuta `SKIP` di
`s1_c_albo` riguarda `p17.s0/p17.s1`; quella condizione non appartiene ai nove campi
personali. Togliendo esclusivamente tale ricevuta da una copia in memoria, blocchi ed
export dell'anagrafica restano identici. Il primo rinvio era stato respinto dalla guardia
per ambito incoerente albo/Camera di Commercio, il successivo accettato: nessuno dei due
ha invalidato la ricevuta del nome.

Il confronto usa la **precedente prova manuale reale**, sessione R2
`cd284a4fe7394ba3ad895acc1d0c3e11`, DOCX `16241b83cf584140925f534d930ae8cd`, 59 scritture.
Originale DOCX identico per SHA-256; identici i cinque frammenti di `integrazione-company.md`
con anagrafica e carica. Il corpus complessivo ha 56 frammenti in entrambi i run, ma altri
frammenti differiscono: non è un confronto integrale a input identici.
R2 chiedeva soltanto nome e cognome; il router salvava «Leonardo Montemurro». Il backend
derivava gli altri otto valori dalle SOURCE e l'utente confermava identità e carica.
Tutti e nove sono effettivamente presenti nel DOCX R2.

**Verifiche offline eseguite:** lo script `replay-offline.py.txt`, con rete e SQLite
bloccati, rilegge entrambe le acquisizioni su `a0cc223` e sul codice estratto dal tag
`3a8de0b`. Tutte le asserzioni passano e i risultati JSON coincidono: nove campi bloccati
per la nuova sessione, nove esportabili per R2; stessa domanda troppo ampia associata al
solo nome e stesso «Ho registrato». Confronto AST: dieci funzioni pertinenti identiche
fra tag R2, padre del fix `ca58972` e candidata. Non è una nuova valutazione del provider:
l'effetto probabilistico dei testi sull'output LLM non è misurato. Il replay dimostra
che il difetto deterministico esiste anche senza il fix, non che ogni generazione futura
sarà uguale.

Nessun codice applicativo modificato, nessun commit, merge, push o promozione; zero nuove
chiamate DeepSeek. Non essendoci una patch, non si dichiara un test prima/dopo né un
rollback di correzione. Sessioni live, versioni, stati e originali verificati invariati
rispetto all'acquisizione; SOURCE e artefatti originali soltanto letti.

Evidenze durevoli nel worktree candidato:
`backend/data/compilation-audit/sottoscrittore-vuoto-20261031/`:
`candidate/` e `demo-r2/` (stati, turni, originali, DOCX/report finali, prompt/output,
tracce router/guardia già registrate), `diagnosis.json`, `docx-check.json`,
`code-comparison.json`, `replay-a0cc223.json`, `replay-3a8de0b.json` e script riproducibile.
Backup separato: `/home/montesano/tesi-backups/sottoscrittore-vuoto-20261031/diagnosi.tar.gz`,
con manifesto e checksum SHA-256 a fianco. Gli artefatti locali restano esclusi da Git.
