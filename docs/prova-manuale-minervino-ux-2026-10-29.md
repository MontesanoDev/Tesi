# Prova manuale Minervino: primi due problemi UX (29 ottobre 2026)

**Ambito:** istanza isolata `tesi-prova-manuale-audit03-20261029` (codice `dbdc317`), tracce in
`.tools/prova-manuale/` (log del backend, istantanee, database). Nessuna chiamata DeepSeek in
questa analisi; app ordinaria e audit storici non toccati.

## 1. Company KB: «File della fonte non trovato»

- **Riproduzione:** `GET /api/global-knowledge/files/{7,8,10}/content` restituisce 404
  «File della fonte non trovato». Nel log della prova le risposte 404 sono 13. Il PDF (9) risponde
  415 per scelta di progetto: l'endpoint apre solo TXT e Markdown.
- **Causa verificata:** il database dell'istanza ha le 4 righe `global_documents` e i loro
  frammenti (Company 9 + 4 + 5 = 18, General 4), ma lo storage non contiene `uploads/_global/`.
  - Il seed dei tentativi 02/03 portava righe e frammenti, ma il manifest dei file copiava solo
    i 6 file di progetto. Anche i runtime 02 e 03 sono privi di `_global/`.
  - Nell'app ordinaria gli stessi documenti (id 7-10) hanno il file presente.
- **Natura:** difetto di preparazione dell'istanza; il comportamento dell'app è corretto.
- **Correzione (strumenti locali dell'istanza, fuori da Git):**
  - `originali.py` verifica i file referenziati in sola lettura e ripristina soltanto quelli
    mancanti, dalla fixture congelata Minervino V1. Pretende nome, dimensione registrata e
    SHA-256 del manifest uguali; non sovrascrive e non reindicizza.
  - `prepara.py` lo invoca e fallisce se resta un file mancante.
- **Esito:** 200 sui tre documenti; database e frammenti invariati.
- **Test:**
  - controllo prima → 4 file mancanti (uscita 1), dopo → 0;
  - preparazione completa usa e getta superata.
- **Rollback:** spostando `_global/` si torna al 404, riportandola al 200.

## 2. «Recupera messaggio»

**Quando compare:**
- banner del composer: esiste una copia in `sessionStorage` per progetto e conversazione e il
  testo è diverso da quello nel composer;
- pulsante sul turno: il turno è in errore, `failed` o `not_configured`.

La copia si salva a ogni modifica e all'invio. Si rimuove solo dopo una risposta riuscita
allo stesso messaggio.

**Comportamento intenzionale, invariato:**
- recupero dopo errore di rete, `failed` o `not_configured`, anche dopo un refresh;
- recupero di una bozza mai inviata;
- recupero durante un invio interrotto e non ancora registrato;
- nessun passaggio fra conversazioni o progetti;
- il recupero riempie solo il composer: non invia e non conferma.

**Difetto (UX e duplicazione), riprodotto dalle tracce:**
- la conversazione `conv-9c2d…` ha due turni `failed` con lo stesso testo (11:02:25 e 11:03:16),
  seguiti da 12 turni riusciti, e ogni turno fallito conservava il pulsante;
- `conv-b707…` aveva due turni `not_configured` uguali, con due pulsanti;
- una copia conservata uscendo dalla pagina durante l'invio restava recuperabile anche quando
  il server aveva già registrato e risposto allo stesso messaggio.

**Correzione minima (`c31d017`, `ProjectWorkspacePage.tsx`):**
- il pulsante del turno compare solo sull'ultimo turno, se è fallito;
- al caricamento della conversazione, una copia uguale all'ultimo messaggio registrato con
  risposta (stesso testo e stesso documento) viene rimossa.

**Test:**
- 5 nuovi; 3 falliscono senza il fix;
- recupero 21/21;
- suite frontend 159/159, lint e build PASS.

**Rollback:** `tesi-rollback-ux-recupero-20261029`. L'albero torna uguale a `dbdc317`, i 16 test
originali passano e i nuovi tornano a 3 falliti.

**Limiti:**
- se si esce da una conversazione nuova durante l'invio, la copia resta sulla chiave «nuova»
  senza una conversazione da confrontare;
- una bozza identica all'ultimo messaggio riuscito viene considerata già inviata.

L'istanza in esecuzione usa ancora il frontend di `dbdc317`.

## 3. «Recupera messaggio» dopo l'aggiunta di un modello AI (seconda prova)

- **Riproduzione:** testo digitato nel composer, poi «Aggiungi un modello nelle impostazioni»
  (pagina `/settings`) e ritorno al progetto. Compare «Un messaggio è conservato in questa
  scheda…» con «Recupera messaggio» al posto del testo.
- **Tracce:** nella seconda istanza il primo invio («compila», 15:27:24) è successivo alla
  creazione del profilo; prima nessun messaggio era stato inviato.
- **Causa verificata:** il ritorno rimonta la pagina, che svuota il composer, mentre la copia del
  testo digitato resta in `sessionStorage`. La copia non distingueva un testo solo digitato da un
  messaggio inviato. Il banner è unico: il composer compare in due rami alternativi.
- **Correzione (`0264aca`):**
  - la copia registra se il messaggio è stato inviato;
  - un testo solo digitato torna nel composer con il suo riferimento al documento, senza banner;
  - il recupero esplicito resta per le copie di messaggi inviati (errore, invio interrotto);
  - le copie salvate prima del campo contano come inviate;
  - la rimozione delle copie già registrate dal server vale solo per le copie inviate, quindi
    cade il limite sulla bozza identica all'ultimo messaggio.
- **Test:** 6 nuovi o aggiornati falliscono senza il fix; frontend 168/168, lint e build PASS.
- **Rollback:** `tesi-rollback-ux-bozza-0264aca-20261029`, albero uguale a `a4582a1`, 27 test del
  genitore passati.
- **Istanza:** l'istanza della seconda prova (`a4582a1`) non è stata aggiornata durante la prova.
