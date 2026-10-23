# Passo 3 — recupero limitato del narratore

## Preregistrazione

Autorizzazione dell'utente: procedere con il terzo passo dopo la candidata rev 3.
Nessuna inferenza reale o campagna E2E; budget esterno zero. Profilo ordinario,
baseline, benchmark e sessioni storiche restano invariati. Nessun commit/tag/push.
La revisione del codice qui svolta è autoriale, non indipendente.

Evidenza letta direttamente: nell'audit minervino-2 della campagna rev 2,
`dialogue/2a80af27c9a142aab6aad88775182775/`, la risposta di continuazione ha due
hold_groups con proposal_slots vuoti. Il contesto contiene zero proposte e otto
slot nel pool. Il validatore rifiuta il JSON per schema; il risultato conserva
READY con error=ValidationError, impedendo l'export conversazionale.

Disegno minimo, prima delle modifiche applicative:

1. Flag persistito separato `narration_recovery_revision=1`, opt-in per nuove
   sessioni con `MAPI_NARRATION_RECOVERY_REVISION=1`. Nessun aggiornamento delle
   sessioni prive del flag, neppure se rev 3. La candidata completa userà i flag
   rev 3 e recupero insieme; non vengono attivati nel runtime ordinario.
2. Riutilizzare il narratore esistente per al massimo **due tentativi totali**
   per risoluzione: timeout 45 secondi e output massimo 2048 token ciascuno.
   Un solo retry per errori già gestiti di provider/timeout/JSON/schema/render.
   Stesso input, nessuna riparazione del JSON, nessun recupero di pezzi di output
   fallito. Zero proposte significa zero hold nel contratto inviato al modello.
3. Dopo due fallimenti, risposta deterministica del backend: conservare audit,
   decisioni, valori USER, sospensioni e revisioni precedenti. Non attribuire
   alcuna nuova revisione alle proposte della finestra fallita; le vecchie
   revisioni valgono solo con fingerprint ancora corrispondente. Offrire
   esplicitamente una bozza parziale con le parti già verificabili, oppure una
   copia vuota se non ce ne sono. Nessuna nuova domanda semantica inventata.
4. Il fallback non autorizza nuove scritture: filtro di selezione esistente,
   V14/K3, ambito USER rev 3 e rivalidazione rimangono attivi. Anche una richiesta
   API diretta, durante il fallback, non potrà forzare SOURCE non revisionate o
   sospese. Nessuna generazione automatica; serve la richiesta USER di export.
5. Il fallback arresta l'avanzamento automatico; un «riprendi» esplicito autorizza
   un nuovo ciclo limitato della sola sintesi. Adeguare le lease al massimo di
   due tentativi. Cancellazioni/interruzioni non diventano autorizzazioni.
6. Registrare i singoli tentativi e l'esito aggregato, includendo token quando
   disponibili; consumo mancante non sarà dichiarato zero. Non sommare consumi
   ereditati da turni precedenti. Nessun conteggio del retry come nuovo trial.

File previsti: `compilation_global_dialogue.py` e
`compilation_global_sessions.py`, test dedicati e documentazione del passo.
Non cambiare il dialogo normale, il recupero SOURCE, la segmentazione, il parser
o il writer. Snapshot prima delle modifiche in
`backend/data/compilation-audit/recupero-narratore-passo3-20261023-01/before/`.

Controprove: output storico minervino-2; JSON troncato e schema errato; errore di
render dopo validazione; errore provider/timeout; retry riuscito e due fallimenti;
nessun lavoro perso né promozione implicita; hold ereditati, ricevute obsolete e
USER non autorizzati; nessun export automatico; ripresa dopo fallback senza nuova
analisi; flag persistiti e profilo ordinario invariati. Provider simulati con
DB/storage temporanei e connessioni vietate. Test mirati, suite backend e Ruff.

Rischi dichiarati: un retry può ripetere lo stesso errore e costa una chiamata;
due timeout possono richiedere circa 90 secondi. Il fallback può produrre una
bozza molto incompleta o vuota; non dimostra che i dati manchino nelle SOURCE.
Non corregge errori semantici validi secondo lo schema, le 25 scritture rev 2 o
la copertura generale dei moduli. Lo schema più preciso non prova la qualità
del modello. Ogni risultato va distinto dalle evidenze delle campagne reali.

## Implementazione

Modificati due file applicativi, conservando la logica normale del narratore:

- `compilation_global_dialogue._narrate_once` contiene il tentativo preesistente;
  il wrapper `narrate` attiva retry e fallback solo con il flag persistito.
  Se la finestra non contiene proposte, lo schema inviato richiede liste di
  sospensioni vuote. Una risposta con gruppi vuoti resta invalida: non viene
  normalizzata o recuperata in parte.
- Il retry riutilizza lo stesso input. I tentativi hanno request/response/result
  distinti; un report `dialogue/recovery-*.json` collega gli artefatti, registra
  retry, esito, durate e consumi. Le metriche aggregate sono sommate solo quando
  disponibili in tutti i tentativi; i valori sconosciuti restano tali.
- `_narration_fallback` conserva le decisioni USER e i blocchi, mantiene solo
  le revisioni con fingerprint valido e offre l'export esplicito. Non aggiunge
  revisioni, non rilascia hold e non genera domande semantiche nuove. Registra
  gli ID non revisionati e interrompe l'avanzamento automatico.
- `compilation_global_sessions` mantiene il flag nei passaggi di stato, adegua
  le lease, consente la ripresa esplicita dopo fallback e aggiunge un veto alle
  richieste API che, durante il fallback, tentino di forzare proposte SOURCE
  non revisionate o sospese. Il controllo viene ripetuto sull'audit ricalcolato.

Profilo sperimentale completo: `MAPI_GENERATION_REVISION=3`,
`MAPI_DIALOGUE_REVISION=1`, `MAPI_NARRATION_RECOVERY_REVISION=1`, con lo stato
derivato già corretto dal passo 1. Questi flag **non sono stati attivati nel
runtime ordinario**. Il recupero è separato dalla segmentazione, così il suo
effetto può essere valutato da solo; le sessioni senza flag restano invariate.

## Prove offline

- Prima esecuzione mirata: **121 PASS in 31,00 s**, includendo il dialogo
  precedente e la validazione delle sospensioni P3.
- Nuovi test del recupero, inclusi il percorso chat e gli artefatti storici:
  **33 PASS in 10,49 s**.
- Controprova V14 aggiunta: **2 PASS**. Dopo fallback le proposte già revisionate
  continuano a richiedere l'autorizzazione procedurale; forzarle via API dà 409.
- **Suite completa finale: 3.640 PASS in 353,53 s; Ruff completo PASS.**
  Nessun test fallito nelle esecuzioni registrate. I tre file codice/test sono
  rimasti identici alle impronte congelate prima della suite.

I casi coprono JSON troncato, schema errato, errore di render successivo alla
validazione, provider/timeout, cancellazione, retry riuscito, due fallimenti,
bozza vuota esplicita, revisioni obsolete, USER senza autorizzazione, hold
ereditati, ripresa senza nuova analisi, flag storici e lease sufficienti.

Un test con 45 proposte fa riuscire la prima finestra da 40 e fallire due volte
la seconda: rimangono selezionabili 40 valori; le cinque proposte non revisionate
restano escluse e la loro imposizione via API dà 409. Si tratta di provider
simulato e DOCX temporaneo, non di una nuova campagna sul modello reale.

Il caso minervino-2 è stato verificato in due modi:

1. La risposta malformata originale viene rifiutata senza modificarla e rigiocata
   in una sessione temporanea con finestra di revisione vuota. Dopo due fallimenti
   il fallback conserva le revisioni precedenti e l'export esplicito riesce.
2. Sullo **stato storico originale, solo in memoria**, il recupero conserva 63
   revisioni, 15 sospensioni e quattro risposte USER. Il veto globale per l'errore
   del narratore lasciava vuota la selezione; il fallback rende nuovamente
   selezionabili 48 proposte SOURCE e un valore USER secondo i controlli di quel
   profilo storico. Non vengono generati DOCX da questa seconda prova, non si
   migra la sessione e **non viene rivalutata la correttezza semantica di quei
   valori**. Non contare questo dato come copertura o come un ottavo successo
   della campagna congelata. È una controprova isolata sullo stato del narratore,
   non una prova dell'intera candidata rev 3.

Diagnostica numerica: `out/minervino-state-counterfactual.json` nell'audit.
Preregistrazione immutabile, copie iniziali, log e patch:
`backend/data/compilation-audit/recupero-narratore-passo3-20261023-01/`.

## Giudizio e limiti

Il difetto di stato è affrontato con un recupero limitato e verificabile: una
sintesi invalida non impone più, nella candidata, di perdere l'accesso a tutte
le parti precedentemente revisionate. Il fallimento della revisione di una
nuova finestra continua invece a bloccare quelle proposte.

Non è dimostrato che il retry migliori il tasso di successo del modello reale.
Una sintesi valida ma semanticamente errata resta fuori da questa correzione;
nessuna conclusione nuova sulle 25 scritture non dimostrate, sulla copertura o
sulle soglie congelate. Due fallimenti possono lasciare una bozza vuota. Il
fallback non formula le decisioni ancora aperte: l'utente può riprendere la
sintesi o chiedere la bozza incompleta. Questo compromesso è intenzionale.

Nessuna inferenza esterna, nuova E2E, migrazione o reindicizzazione. La candidata
resta non adottata. Il passo successivo è una valutazione reale limitata e
preregistrata dei tre interventi insieme, non un altro filone architetturale.

Backup del passo, con piano congelato, copie prima/dopo, log, manifest e patch:
`backend/data/compilation-audit/recupero-narratore-passo3-backup-20261023.tar.gz`.
Verifica file per file e impronta dell'archivio nei sidecar `.verification.json`
e `.sha256`. Non è un backup integrale del repository o del database live;
non include runtime o file con credenziali. Nessun commit, tag o push.
