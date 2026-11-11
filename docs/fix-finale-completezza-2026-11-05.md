# Fix finale: completezza del DOCX e stabilità dell'interfaccia

Data: 5 novembre 2026. Worktree sperimentale, branch `narratore-chiarezza/2026-10-31`.
Riferimento di partenza `11627d4`, commit `d76d7d2`. Nessuna promozione, push o merge.
Nessuna preparazione dei benchmark.

## Esito

I quattro problemi della prova manuale hanno cause identificate e corrette in modo generale,
dietro il nuovo flag `export_completeness_revision`.

Nelle tre esecuzioni reali complete:

- la prima pagina passa da 0/11 a 11/11;
- la casella 4 è l'unica spuntata nell'XML;
- i soci e il direttore tecnico sono presenti;
- i rinvii restano vuoti;
- non c'è nessuna domanda su altre opzioni e nessuna conferma doppia;
- c'è una sola scheda per esportazione, verificata in un browser vero;
- prima e seconda bozza restano scaricabili e identiche ai file salvati.

**La campagna reale non è completa.** Il credito DeepSeek si è esaurito durante la campagna (errore
402, alle 19:38): sono complete 3 esecuzioni, 19 sono state interrotte e non valgono né come prova né
come regressione.

Valutazione: **pronto per una nuova prova manuale, dopo la ricarica del credito DeepSeek**, senza la
quale la prova non può partire. **Non pronto per la promozione**: prima vanno ripetute le regressioni
reali elencate in "Cosa manca".

Per provarlo apri una nuova conversazione: le sessioni esistenti, compresa `145a2038`, conservano
il comportamento con cui sono nate.

## 1. Campi iniziali vuoti

Sessione `145a2038`, ricostruita per ogni destinazione: proposta, evidenza, condizione, gate,
ricevuta, stato esportabile, writer.

| Destinazione | Proposta | Condizione | Esito prima | Classificazione |
|---|---|---|---|---|
| Carica (`p14.s0`) | Nessuna proposta del modello; derivazione dal firmatario possibile | `s1_c_org` con risposta negativa | La derivazione viene scartata da `blocked_conditions` | Condizione erroneamente collegata |
| Denominazione, provincia, telefono, fax, e-mail, PEC, partita IVA, Camera di Commercio e numero (9 campi) | Proposte con evidenza SOURCE valida | condizione sull'operatore confermata, `s1_c_org` negata | Bloccati dal gate | Condizione erroneamente collegata |
| Comune della sede (`p15.s0`) | Respinta: «Continuità FORM senza operatore verificato» | Come sopra | Il recupero esistente l'avrebbe ripristinata, ma la condizione negata lo impediva | Respinta, per la stessa causa |
| Albo professionale e numero (`p17.s2`, `p17.s3`) | Nessuna | Nessuna | Vuoti | Alternativa alla Camera di Commercio, non pertinente per una società: vuoti corretti |

**Causa.** Il modello ha scritto «l'operatore è un'organizzazione, non un libero professionista
singolo» e ha ancorato la condizione all'opzione «Libero professionista singolo», assegnandole
l'intestazione societaria. Quindi:

1. il narratore ha chiesto se quell'opzione si applicasse;
2. il tuo «no», corretto, ha escluso l'intestazione;
3. la stessa esclusione ha impedito la derivazione della carica e il recupero della sede.

È un errore di ancoraggio con la polarità invertita, non una regola di sicurezza da allentare.

**Correzione.** Regola generale: una destinazione sopra le opzioni della regione «in qualità di» non
può dipendere da una di esse (`backend/app/compilation_branch_evidence.py`,
`release_header_from_options`).

- Se la destinazione ha altre condizioni, resta governata da quelle.
- Altrimenti la condizione viene riancorata alla riga del modulo della destinazione stessa, così
  nessun dato perde il proprio controllo.
- Ciò che sta dentro la regione o sotto di essa non cambia.
- L'intestazione non riceve l'autorizzazione della sezione societaria per somiglianza di valori: ha
  una propria ricevuta, ricavata dal ramo confermato della stessa società, che decade se il ramo
  viene ritirato.

Il controllo sulla continuità dell'operatore non è stato toccato. Una prima modifica è stata ritirata
perché non necessaria: con la condizione corretta, il recupero esistente scrive la sede.

## 2. Barra «Scarica DOCX» ripetuta

**Causa.** La barra introdotta nel commit precedente stava sopra il campo messaggio: restava sempre in
fondo e sembrava ripubblicata sotto ogni risposta.

**Correzione.** C'è ora una scheda per ogni esportazione, sotto il messaggio che l'ha prodotta:
`frontend/src/components/CompilationDraftCard.tsx` e `frontend/src/compilationDrafts.ts`. L'esportazione
registra il proprio `generation_id`, così il legame resta dopo il refresh. Per i turni salvati prima di
questa modifica vale l'ordine delle esportazioni.

- Un messaggio ordinario non aggiunge né sposta nulla.
- L'avviso di modifiche non esportate compare solo sulla scheda dell'ultima bozza.
- «Prepara nuova bozza» compila soltanto il messaggio e non genera alcun DOCX.

**Altro difetto trovato.** Al refresh i testi dei turni risultavano sfasati: ogni risposta veniva
riscritta con il testo del messaggio successivo, mentre questo era ancora in elaborazione
(`backend/app/compilation_chat.py`, `retain_compilation_question`). Ora un turno già completo non viene
più riscritto. I testi già salvati nelle sessioni storiche non sono stati modificati.

## 3. Domanda sul ramo incompatibile

**Cause.** La domanda nasceva da:

- l'ancoraggio sbagliato del punto 1, con l'etichetta della condizione scritta dal modello;
- la selezione delle domande: le condizioni delle altre opzioni restavano domandabili anche dopo la
  conferma di un'opzione.

**Correzione.**

- La dipendenza dei dati societari dal ramo incompatibile è rimossa alla radice (punto 1): la domanda
  non è soltanto nascosta.
- Dopo la conferma o la scelta di un'opzione, le condizioni delle altre opzioni non vengono più
  chieste, e il riepilogo della bozza non invita più a confermarle. Ritirando la decisione tornano
  disponibili.

## 4. Conferma duplicata

**Causa.** La stessa clausola è stata confermata due volte nello stesso messaggio: prima come risposta
alla domanda, poi come istruzione libera.

**Correzione.** La clausola viene detta una volta sola; entrambe le ricevute restano.

**Altro difetto trovato.** Alla ripresa il narratore ripeteva «Il file già esportato resta com'è»
anche dopo una nuova esportazione che conteneva già la modifica. Ora, dopo un'esportazione, l'ultimo
turno viene chiuso.

## Verifiche

### Offline, senza provider

- **Replay della sessione `145a2038`** sul codice nuovo, con l'output reale del modello e le tue
  risposte:
  - prima pagina 11/11;
  - 61 valori;
  - una sola casella;
  - nessuna domanda sulle altre opzioni;
  - riepilogo senza inviti al ramo escluso.
- **Regressione su 113 audit reali salvati:** la regola cambia 370 campi, tutti sopra le opzioni.
  Nessun campo perde il proprio controllo, nessun valore proposto cambia, nulla cambia dentro le regioni.
- **Domanda sulla scelta:** su 76 audit con `p39`, la regola non lascia mai la condizione del ramo senza
  dati, quindi la domanda resta raggiungibile.

### Suite

| Controllo | Esito |
|---|---|
| pytest backend sul codice del commit | 4701 passati, 8 saltati |
| Ruff | Pulito |
| vitest | 198 passati |
| `tsc -b` | Pulito |
| oxlint | 2 avvisi già presenti |
| Playwright con API simulate, desktop e mobile | 8 passati |

### Prove reali DeepSeek

| Esecuzione | Tipo | Modulo | Codice |
|---|---|---|---|
| `ff-manuale-1` | API, con le parole della tua prova | Minervino | Commit, salvo il testo del riepilogo |
| `fb-minervino-1` | Browser vero, backend isolato | Minervino | Come sopra, senza la correzione della ripresa |
| `fb-cnr-1` | Browser vero, backend isolato | CNR | Come sopra, senza la correzione della ripresa |

Risultati per esecuzione:

| Controllo | `ff-manuale-1` | `fb-minervino-1` | `fb-cnr-1` |
|---|---|---|---|
| 1. Prima pagina, letta nell'XML | 11/11 | 11/11 | Intestazione presente |
| 2. Casella 4 nell'XML | Sola spuntata, scelta registrata nel primo messaggio | Sola spuntata | Nessuna casella nel modulo |
| 3. Rami incompatibili | Nessuno | Nessuno | — |
| 4. Soci e direttore | 24 dati dei soci, direttore 8/8 | 24 dati dei soci, direttore 8/8 | — |
| 5. Rinvii vuoti | 0 scritti, 0 fuori gold | 0 scritti, 0 fuori gold | — |
| 6. Domande su altre opzioni | 0 | 0 | — |
| 7. Conferme doppie | 0 | 0 | 0 |
| 8. Schede per esportazione | — | 1 dopo «grazie», correzione e refresh; 2 dopo la seconda bozza, pausa e ripresa | Come Minervino |
| 9. Bozze accessibili e immutate | Hash diversi tra prima e seconda | Download dal browser identici ai file salvati | Come Minervino |
| 10. Regressioni | Router multivalore e correzione libera | Correzione libera | «I dati di X nel sottoscritto» |
| Gold | C59 E2 | C59 E2 | 10 valori fuori gold |
| Rispetto alla bozza migliore | 0 mancanti | 0 mancanti | — |
| Banner «BOZZA NON VERIFICATA» | Presente | Presente | Presente |

I due errati sono la carica, il cui gold è più corto della fonte (come nelle campagne precedenti), e
il fax corretto di proposito dal test. Le schermate del browser sono in `esecuzioni/fb-*/browser/`.

Prima e dopo, stesso messaggio: la bozza della sessione manuale aveva 50 valori e 0/11 sulla prima
pagina; `ff-manuale-1` ne ha 61 e 11/11.

Costo complessivo di questo lavoro: 22 esecuzioni avviate, 197 chiamate di cui 134 andate a buon fine,
3.394.808 token, circa 0,36 USD.

## Cosa manca

1. **Regressioni reali sul codice finale.** Interrotte dal 402 e da ripetere dopo la ricarica:
   - dialoghi `multi`, `numero`, `libera`, `ambigua`, `no_ramo`;
   - Trapani;
   - scenari `minervino-v3`, `minervino-rinvio`, `minervino-ramo-errato`, `checkbox-v2`,
     `compilazione-v1`, `trapani-v3`, `cnr-iriss-allegato-a`;
   - ripresa del difetto `p65`.

   Sul codice precedente erano tutte verificate; questa volta le copre solo la parte offline.
2. **Codice delle prove reali.** Differisce dal commit solo per il testo del riepilogo della bozza,
   coperto da test e dal replay offline. `fb-*` precede anche la correzione del messaggio alla ripresa.
3. **Condizioni ancorate sotto le opzioni.** Formule come «di essere inserito/i nell'elenco…» non sono
   coperte dalla regola, che riguarda solo i dati sopra le opzioni. Vengono chieste una volta: in
   `fb-minervino-1` le conferme sono state 4.
4. **Controllo sui ruoli dei soci.** Invariato: in alcune esecuzioni il modello scrive «Soci» e 23 dati
   restano vuoti. Non è comparso in queste tre esecuzioni.
5. **Sessioni storiche.** Restano invariate, compresi i testi dei turni già sfasati.

## Commit, rollback, backup e istanze

- **Commit `d76d7d2`:** 16 file, percorsi espliciti. `STATUS.md` e `relazioni.md` non sono stati toccati.
- **Rollback verificato:** l'albero del revert coincide con il genitore e i 29 test modificati, nella
  versione del genitore, passano.
- **Backup** su `/mnt/d/Backup-tesi-2026-11-02`, verificato in sola lettura e non modificato:
  - contiene il pacchetto del repository, l'archivio dell'app ordinaria e i database;
  - il branch sperimentale vi è salvato solo fino a `930aeef`, del 2 novembre;
  - i 19 commit successivi, compreso `d76d7d2`, esistono solo su questo disco.

  Serve una tua decisione su un nuovo backup.
- **Istanze:**
  - backend sperimentale riavviato su `d76d7d2`, dopo 40 minuti di inattività, con lo storico identico;
  - frontend 5174 sullo stesso albero;
  - istanza ordinaria spenta, HEAD `99ab052` invariato.
- **Dati grezzi** (rapporto non incluso nel commit), nella cartella della campagna:
  - `fix-finale/`;
  - `METRICHE-ff-controllo.json` e `METRICHE-ff.json`;
  - `rollback.txt`.
