# Risposte USER con più dati — correzione mirata, 1 novembre 2026

Aggiornamento successivo: fix committato in `930aeef`, suite finale completa superata;
verifica reale parziale, bloccata dal credito DeepSeek. Vedi il
[rapporto successivo](user-multivalue-deepseek-2026-11-01.md). Quanto segue conserva
gli esiti dell'intervento offline precedente al commit.

Correzione implementata **soltanto nel worktree isolato**, su `a0cc223`, branch
`narratore-chiarezza/2026-10-31`; modifiche non committate. Profilo
`sezioni-2026-10-30-r2`, con `user_extraction_revision=1` persistita nelle nuove sessioni.
Nessuna promozione, merge, push, migrazione o reindicizzazione. Demo e dati storici
preservati. Zero nuove chiamate DeepSeek e zero compilazioni live.

## Causa e perimetro

La [diagnosi precedente](sottoscrittore-vuoto-2026-10-31.md) dimostra un limite
preesistente: domanda multivalore su un solo slot nome, router che propone tutta
l'anagrafica, guardia che la accetta e validatore privo di controllo sulla forma del
nome. Quel valore non identifica la persona nelle SOURCE; inoltre resta aperta la
conferma d'identità. «Ho registrato» descriveva il salvataggio senza distinguere
l'utilizzabilità. Non è una regressione deterministica dimostrata di `de2f5de`.

Il fix riguarda le risposte a una domanda attiva sul nome di una persona, quando il
FORM identifica senza ambiguità i campi personali collegati. Vale anche per firmatarie,
richiedenti e referenti, per paragrafi, righe di tabella e moduli con campi in linea.
Non contiene nomi, bandi o ID Minervino nel codice applicativo.

## Correzione

- Estrazione letterale conservativa prima della guardia: nome, luogo/provincia/data
  di nascita, residenza, indirizzo/civico e codice fiscale, solo se presenti nel testo
  e associabili a un campo FORM della stessa persona. Nessuna inferenza di carica.
- Il nome composto viene separato; una frase anagrafica non può essere salvata come
  nome, neppure con un precedente verdetto positivo della guardia. Il nome semplice
  continua a usare il controllo ordinario.
- Ogni campo aggiuntivo passa la **stessa guardia indipendente**, con destinazione e
  ambito propri, e riceve una ricevuta specifica. La persistenza ricalcola l'estrazione
  e rifiuta valori alterati, prove mancanti/scambiate e valori non validi. Non sovrascrive
  risposte precedenti; un rifiuto del nome impedisce la distribuzione degli altri dati.
- Risposta originale e proposta originale del router restano nell'audit. Dati ambigui
  o respinti richiedono chiarimento e non possono essere sostituiti silenziosamente
  con proposte SOURCE. Una successiva risposta esplicita può risolverli.
- Estrazione, applicabilità e autorizzazione restano separate. Nessuna conferma
  d'identità, dichiarazione, carica o checkbox viene autorizzata dall'estrazione.
  Condizioni esistenti e controlli d'export restano obbligatori.
- La ricevuta distingue «Dati acquisiti per la bozza» da risposte conservate con
  conferme ancora necessarie. Anche il riepilogo dell'export segnala i valori USER
  conservati ma non inseriti.

Il modulo principale è `backend/app/compilation_user_extraction.py`; integrazioni in
router, contesto chat, ricevute/persistenza e selezione d'export. Il modulo della guardia
`compilation_reply_guard.py` non è modificato. Il nuovo flag appartiene alla definizione
canonica del profilo; profili storici e sessioni già salvate non vengono aggiornati.

## Evidenze prima/dopo

Replay della prima risposta della sessione reale `d9be7d34947145f69892bfc0bf535bad`,
usando FORM, SOURCE, audit iniziale, domanda e output router acquisiti nella diagnosi.
Rete e SQLite vietati nello script; persistenza in memoria e artefatti temporanei.
I verdetti delle chiamate alla guardia sono **simulati**: non sono nuovi esiti DeepSeek.

| Controllo | Baseline `a0cc223` | Codice corretto |
|---|---|---|
| Valore nome | Intera frase anagrafica | Solo nome e cognome |
| Dati USER separati | 1 valore composto | 7 valori atomici, 7 ricevute valide |
| Riuso SOURCE | Non identifica la persona | Ritrova codice fiscale e carica |
| Conferma d'identità | Aperta | Resta aperta; proposta su tutti i 9 campi |
| Export personale senza quella conferma | Nessun campo | Nessun campo, correttamente |
| Messaggio | «Ho registrato: Il sottoscritto» | Risposte conservate, conferme necessarie |

Il replay non inventa le conferme mancanti della conversazione reale. Il test con
FORM sintetico senza quei blocchi verifica invece l'intero percorso fino a DOCX e
report scaricati: sette valori esatti scritti, nessuna checkbox selezionata.
Il rinvio all'albo è conservato e non viene trasformato in autorizzazione anagrafica.

- **Regressione/rollback:** rimuovendo il fix in una copia temporanea della baseline,
  il test che vieta l'intera frase nel nome fallisce su FTS5 e Qdrant: 2 FAIL, 6 PASS
  (i sei controlli di nome semplice). Riapplicando la patch: 8 PASS. I file
  applicativi ripristinati coincidono byte per byte con la candidata finale.
- **Nuovi test:** 34 PASS, inclusi persone e FORM differenti, nomi semplici e con
  apostrofo/trattino, date invalide, alternative, soggetti diversi, rifiuti della
  guardia, prove mancanti/scambiate, manomissioni, chiarimento successivo e blocchi SOURCE.
- **Verifica finale mirata:** 132 PASS, includendo profili e ripresa delle sessioni;
  cinque nuovi controlli confermano che i profili storici non attivano l'estrazione.
- **Suite completa:** primo passaggio 4.310 PASS, 12 FAIL, 8 SKIP. I dodici fallimenti
  riguardavano la definizione canonica del nuovo flag, corretta mantenendo i profili
  storici. Secondo passaggio: **4.327 PASS, 8 SKIP** in 476,95 secondi,
  registrato in `full-suite-final.txt`; avviato prima
  dell’ultimo affinamento sui nomi con apostrofo; dopo tale affinamento, rieseguiti
  tutti i 132 test interessati sul codice finale.
- **Nome con apostrofo:** aggiunto `Liam O’Connor`: due FAIL prima del restringimento
  del controllo delle alternative, due PASS dopo; nessun cambiamento della guardia.
- Ruff e `git diff --check` PASS. Graphify aggiornato nel solo worktree candidato,
  estrazione AST, nessuna chiamata LLM. La diagnostica della mappa rileva 7 archi
  verso lo stesso nodo, nessun endpoint mancante: limite della mappa segnalato,
  nessuna correzione estranea al task. Frontend invariato, suite frontend non rieseguita.

## Rollback, conservazione e limiti

Rollback provato in una copia estratta da `a0cc223`, mai sull'istanza live: applicazione
e inversione di `implementation-final.patch`, rimozione/ripristino del nuovo modulo,
stessi test prima/dopo. Hash e risultati in `rollback-final.json` e relativi log.
Per tornare al comportamento precedente occorre ripristinare quel codice; non basta
riscrivere le ricevute. Il rollback non ricompila né modifica sessioni già salvate.

Confronto finale in sola lettura: entrambe le sessioni reali restano alla versione 15,
stato e originale invariati; 56 frammenti SOURCE per ciascuna e 114 artefatti originali
immutati. Anche i 138 file dell'acquisizione precedente coincidono con il manifesto.
Tag demo ancora `3a8de0b`, HEAD candidata ancora `a0cc223`.

Limiti espliciti: grammatica italiana delimitata e FORM riconoscibile, non estrattore
universale di testo libero. Nei casi incerti chiede chiarimenti. Ogni risposta composta
può richiedere fino a due verifiche aggiuntive della guardia, in gruppi di quattro
campi; il caso reale richiede due gruppi aggiuntivi. Nessuna chiamata aggiuntiva per il
solo nome. Compatibilità e qualità della guardia reale su questi nuovi input **non
misurate**. Nessuna riparazione retroattiva della sessione difettosa.

**Promozione sospesa:** i controlli offline supportano il fix, ma manca una piccola
verifica manuale con guardia reale su una nuova sessione e conferme esplicite. Non è
stata avviata; ci si ferma a questo rapporto.

Evidenze locali: `backend/data/compilation-audit/user-multivalue-20261031/`, con replay
prima/dopo, input/output simulati dichiarati, log anche falliti, patch, rollback e
controllo d'integrità riproducibile. Il caso reale resta nella precedente acquisizione
`sottoscrittore-vuoto-20261031/`. Backup separato della correzione e delle evidenze in
`/home/montesano/tesi-backups/user-multivalue-20261031/`, manifesto e SHA-256 a fianco
dell'archivio. I dati locali ignorati da Git non vengono preservati dal solo commit.
