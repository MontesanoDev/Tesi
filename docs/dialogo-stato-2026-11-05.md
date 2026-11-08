# Fix mirato: dialogo USER, condizioni e gestione bozze

Data: 5 novembre 2026. Worktree sperimentale, branch `narratore-chiarezza/2026-10-31`.
Riferimento di partenza `d57ff89`, commit `11627d4`. Nessuna promozione, push o merge.

## Esito

I cinque problemi della prova manuale hanno cause identificate e corrette in modo generale,
dietro il nuovo flag `dialogue_state_revision`. Su 20 esecuzioni reali finali:

- 0 caselle indebite, lette dall'XML dei DOCX;
- 0 scritture su rami incompatibili e 0 valori vietati;
- 0 dati scritti tra quelli bloccati dal controllo sulle dichiarazioni;
- 0 errori 5xx e 0 risposte 402 o 429 dal provider;
- la scelta non è mai richiesta dopo essere stata registrata;
- nessuna ricevuta duplicata e nessun identificativo tecnico nelle risposte.

Valutazione: **pronto per la tua prova manuale, non ancora per la promozione**. Motivi nella
sezione "Promuovibilità". Restano limiti reali, elencati senza attenuazioni nella sezione
"Limiti residui": il più importante è il controllo sui ruoli dei soci, che in 1 esecuzione finale
su 20 lascia vuoti 23 dati.

**Per provarlo apri una nuova conversazione.** Il flag vale solo per le sessioni nuove: la sessione
manuale `2d34aed3` conserva il comportamento con cui è nata.

## I 12 test obbligatori

"Reale" indica DeepSeek reale sul codice fissato. "Replay" e "Simulato" sono indicati a parte.

| # | Test | Esito | Prova |
|---|---|---|---|
| 1 | «opzione 4» dentro una risposta multipla | Superato | Reale: `sd4-multi-1`, `sd4-multi-2`. Registrata nello stesso turno, mai richiesta, una sola casella nell'XML |
| 2 | `4` da solo alla domanda numerata | Superato | Reale: `sd4-numero-1`. Scelta chiesta una volta, casella presente nell'XML |
| 3 | Scelta assente o rinviata: nessuna spunta | Superato | Reale: `minervino-rinvio-stato4-1`, prima bozza di `sd4-libera-1`, `checkbox-v2-stato4-1`: 0 caselle |
| 4 | Condizione davvero non soddisfatta: dati sospesi | Superato | Reale: `sd4-noramo-1`. Ramo negato, regione del ramo vuota, etichetta non ereditata |
| 5 | Condizione già confermata: nessuna sospensione artificiale | Superato | Reale: `sd4-libera-1`, `sd4-ambigua-1`, `minervino-rinvio-stato4-1`. Ricevuta ereditata, intestazione scritta, nessuna domanda sull'etichetta |
| 6 | Nome del firmatario e dati documentati recuperati | Superato | Reale: firmatario 9/9 in `sd4-libera-1` e `sd4-libera-2`. Su CNR e Trapani il solo nome, perché le fonti non hanno altri dati di quella persona |
| 7 | Istruzione libera che nomina una sezione, senza ID | Superato, con un limite | Reale su tre moduli. Limite 3: su CNR i dati restano in attesa di una conferma |
| 8 | Destinazione davvero ambigua: chiarimento, nessuna scrittura | Superato, con un limite | Reale: `sd4-ambigua-1`, versione invariata. Limite 4: «Metti tutti i dati nel modulo» non è gestita in modo uniforme |
| 9 | Due bozze successive, prima copia immutata | Superato | Reale: hash distinti dopo la correzione in 6 esecuzioni. Simulato: `test_a_later_draft_keeps_the_first_identical…` confronta i byte scaricati |
| 10 | Nessun DOCX duplicato dopo messaggi ordinari o pausa | Superato | Simulato: vitest e Playwright. Reale: bozze uguali alle richieste di generazione, pausa e ripresa non ne creano |
| 11 | Ramo consorzio incompatibile vuoto | Superato | Reale: `rr-stato4-1`. Replay: `replay-stato4b`. Nessuna violazione in tutte le esecuzioni |
| 12 | Nessuna dichiarazione o casella non autorizzata | Superato | Reale: 0 su 20, dall'XML e dal controllo sulle dichiarazioni applicato allo stato finale |

## Cause effettive

### 1. Risposta multipla e casella 4

Passaggi ricostruiti: testo USER, router, target, guardia, ricevuta, stato, messaggio, writer.

- **Scelta persa nel messaggio multiplo.** La destinazione della scelta esiste solo dopo la conferma
  del ramo. Il router non aveva dove metterla e la frase spariva senza avviso. Ora ciò che nessuna
  risposta cita riceve una seconda lettura sullo stato aggiornato:
  `backend/app/compilation_global_sessions.py:955`.
- **«4» rifiutato.** Il router citava la frase del turno precedente, quindi
  `apply_replies` non la trovava nel messaggio. Un numero isolato è ora la propria citazione:
  `backend/app/compilation_conversation.py:174`.
- **Frase consumata da una destinazione sbagliata.** «Scelgo l'opzione 4» diventava il testo di un
  campo o la conferma di una condizione, e la scelta veniva richiesta. Una opzione numerata può
  andare solo a una domanda a scelta: `backend/app/compilation_conversation.py:232`.
- **Scelta richiesta dopo una risposta successiva.** La ricevuta della scelta controlla le
  condizioni di tutte le opzioni: un «no» su un'altra opzione, o un'estensione del proprio ramo, la
  rendeva non verificabile. Ora contano solo le condizioni dell'opzione scelta:
  `backend/app/compilation_scope_review.py:132` e `:170`. Il ritiro del proprio ramo la annulla ancora.
- **Domanda su un ramo già escluso.** Dopo la scelta veniva chiesta la condizione di un'altra opzione,
  i cui dati sarebbero rimasti vuoti comunque: `backend/app/compilation_branch_evidence.py:194`,
  applicata in `question_pool`.

La distinzione tra conferma del ramo e autorizzazione della casella resta: la casella si spunta
solo con una scelta esplicita, che deve superare la guardia.

### 2. «dell'operatore economico» e gli 11 dati sospesi

**È una condizione duplicata e mal ancorata, non autonoma.** La citazione FORM è letteralmente
l'etichetta del campo che governa, quindi non enuncia alcun requisito.

Ricostruzione sulla sessione manuale `2d34aed3`:

| Passaggio | Stato |
|---|---|
| Proposte | 10 dati della stessa società e la carica della persona, da `p14.s0` a `p17.s1` |
| FORM | Condizione `s1_c_part`, aspetto partecipazione, citazione uguale all'etichetta di `p14.s1` |
| Ricevute USER | Ramo della stessa società già confermato, nessuna ricevuta sull'etichetta |
| Sospensione | `pending_signatory_conditions` la rimanda finché il firmatario non è risolto |
| Guardia | `blocked_source_fields` blocca i campi senza ricevuta valida |
| Writer | Campi vuoti e dati «in attesa» nel messaggio |

Causa generale: la condizione rientra nelle domande dopo il ramo, quindi non può mai essere chiesta
insieme a esso (`backend/app/compilation_source_reuse.py:279`).

Correzione:

- finché il ramo è aperto, l'etichetta non è una domanda
  (`backend/app/compilation_conversation.py:424`);
- quando il ramo è confermato, l'etichetta riceve una ricevuta propria con prova ricalcolata e
  `implied_by` (`backend/app/compilation_conversation.py:448`);
- la ricevuta decade se il ramo viene ritirato e non sostituisce mai una risposta esplicita;
- il messaggio lo dichiara: «La stessa conferma vale per…»;
- lo stesso vale per il titolo del modulo, sopra ogni campo
  (`backend/app/compilation_conversation.py:391`).

Limiti voluti, per non unificare condizioni diverse:

- non vale se l'etichetta nomina una qualità del FORM, come «legale rappresentante» o «consorzio»;
- non vale se i dati riguardano più società;
- non vale se il ramo è negato: `sd4-noramo-1` chiede l'etichetta da sola;
- non libera dati personali proposti dalle fonti, salvo che governi anche un'altra condizione o che
  l'USER abbia nominato quella persona.

Replay sullo stato manuale, nessuna chiamata al modello: i campi bloccati passano da 143 a 133.
Si liberano 10 dati della società, la carica resta bloccata.

### 3. Correzioni libere sul firmatario

- **Frase nel campo nome.** «Il sottoscrittore è X, amministratore…» faceva fallire l'estrazione.
  «metti X nato a…» scriveva anche il verbo: il codice sostituiva il nome corretto del router con
  «metti X», e i dati derivati andavano persi (`sd3-libera-2`). Ora comandi e ruolo restano fuori
  dal nome e la stessa persona conserva la grafia registrata:
  `backend/app/compilation_user_extraction.py:28`, `:190`, `:299`.
- **Richiesta naturale non capita.** «I dati di X nel sottoscritto» produceva, a seconda
  dell'esecuzione, una domanda su quale sezione, un numero di target o il nome riscritto. Ora il
  backend sceglie l'unica operazione ammessa dallo stato, e guardia e ricevute restano quelle
  ordinarie: `backend/app/compilation_conversation.py:301`. Una persona diversa da quella registrata
  non viene trattata qui come correzione.
- **Guardia sull'ambito.** Rifiutava perché i valori non erano nel messaggio. Ha una regola esplicita
  per questo caso e resta negativa se il soggetto non è quello atteso:
  `backend/app/compilation_reply_guard.py:249`.
- **Multi-intento.** Citazioni non letterali, frasi spezzate su «D. Lgs. n. 36/2023» e numeri di target
  nelle risposte: `backend/app/compilation_conversation.py:205`, `:247`, `:262`.

«Hai tutti i dati nella KB» non autorizza nulla: la frase viene segnalata come non registrata.

### 4. «Scarica DOCX» ripetuto

Il backend esponeva correttamente `last_generation`. Era il frontend a ripubblicare stato e pulsante
in ogni ultima risposta (`frontend/src/components/CompilationReply.tsx`).

Ora c'è una sola barra persistente, `frontend/src/components/CompilationDraftBar.tsx`, con:

- l'ultima bozza esportata;
- l'avviso di modifiche non ancora esportate, da `dialogue_digest`
  (`backend/app/compilation_global_sessions.py:172`);
- le bozze precedenti, ancora scaricabili;
- «Prepara nuova bozza», che compila soltanto il messaggio e non genera alcun DOCX.

### 5. Esportazioni successive

Una correzione accettata dopo un export dice che il file già esportato resta com'è. Una non accettata
riporta il motivo del verdetto. La prima copia non viene toccata.

### Difetti emersi durante la campagna

Le prove reali intermedie hanno trovato tre difetti che i test simulati non coprivano. Il primo
è stato introdotto da questo stesso lavoro:

- **Seconda lettura e domande non viste.** In `sd2-multi-1`, «lascia vuote categorie, attestazioni e
  luogo/data» è stato preso come risposta a una domanda appena generata, che l'USER non aveva visto.
  Sono rimasti vuoti 52 dati. La seconda lettura ora non vede alcuna domanda attiva
  (`backend/app/compilation_conversation.py:252`).
- **Rinvio di un'estensione.** Cancellava l'intera conferma del blocco. Ora rinvia solo i dati
  aggiunti (`backend/app/compilation_global_dialogue.py:2384`).
- **Comando nel campo nome.** Era un difetto preesistente di `extract`. È emerso in `sd3-libera-1` e
  `sd3-libera-2`, subito dopo una riga di prompt aggiunta qui che spingeva il router a scrivere il
  nome. Vedi sezione 3.

## Prove reali DeepSeek

Tre gruppi di codice:

- dialoghi `sd4-*`: patch `1b50da42832aecaf`;
- scenari `*-stato4-*`: patch `3e552cb3eb508caa`, identica al commit;
- tra le due patch cambia solo il testo di una risposta del caso «nulla da confermare».

C, E, M: valori corretti, errati e mancanti rispetto al gold. F, D, I: firmatario, direttore,
intestazione. Le ultime tre colonne sono chiamate al provider, token e costo.

### Dialoghi sul modulo Minervino

| Esecuzione | Gold | Scritti | F | D | I | Caselle | Scelta chiesta | Bozze | Chiamate | Token | USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `sd4-multi-1` | C57 E2 M2 | 59 | 9/9 | 6/8 | 10/10 | 1 | 0 | 3 | 26 | 695.081 | 0,0675 |
| `sd4-multi-2` | C49 E2 M10 | 51 | 9/9 | 4/8 | 10/10 | 1 | 0 | 3 | 33 | 808.744 | 0,0938 |
| `sd4-numero-1` | C58 E1 M2 | 59 | 9/9 | 8/8 | 10/10 | 1 | 1 | 1 | 22 | 638.719 | 0,0780 |
| `sd4-libera-1` | C59 E1 M1 | 60 | 9/9 | 8/8 | 9/10 | 1 | 2* | 2 | 23 | 660.292 | 0,0698 |
| `sd4-libera-2` | C59 E1 M1 | 60 | 9/9 | 8/8 | 9/10 | 1 | 1 | 2 | 27 | 780.981 | 0,0801 |
| `sd4-ambigua-1` | C32 E1 M28 | 33 | 9/9 | 6/8 | 8/10 | 1 | 4* | 1 | 26 | 725.513 | 0,0702 |
| `sd4-noramo-1` | C17 E1 M43 | 18 | 9/9 | 0/8 | 9/10 | 0 | 0 | 1 | 18 | 541.397 | 0,0635 |

\* La domanda restava aperta mentre lo script dava altre istruzioni. Non è mai riapparsa dopo la
registrazione della scelta.

### Altri moduli e scenari di confronto

| Esecuzione | Gold | Scritti | Caselle | Bozze | Chiamate | Token | USD |
|---|---|---:|---:|---:|---:|---:|---:|
| `sd4-cnr-1` | fuori gold | 1 | n/d | 2 | 19 | 128.871 | 0,0116 |
| `sd4-cnr-2` | fuori gold | 0 | n/d | 2 | 22 | 149.497 | 0,0143 |
| `sd4-trapani-1` | fuori gold | 8 | n/d | 3 | 18 | 235.255 | 0,0237 |
| `sd4-trapani-2` | fuori gold | 9 | n/d | 2 | 22 | 311.682 | 0,0298 |
| `minervino-v3-stato4-1` | C60 E1 | 61 | 1 | 1 | 23 | 669.081 | 0,0674 |
| `minervino-v3-stato4-2` | C43 M18 | 43 | 1 | 1 | 25 | 663.102 | 0,0765 |
| `minervino-rinvio-stato4-1` | C33 E1 M27 | 34 | 0 | 1 | 28 | 785.664 | 0,0813 |
| `minervino-ramo-errato-stato4-1` | C60 E1 | 61 | 1 | 1 | 25 | 681.834 | 0,0814 |
| `checkbox-v2-stato4-1` | C2 M5 | 2 | 0 | 1 | 4 | 42.085 | 0,0081 |
| `compilazione-v1-stato4-1` | C18 | 18 | 1 | 1 | 18 | 174.979 | 0,0213 |
| `trapani-v3-stato4-1` | fuori gold | 9 | n/d | 1 | 12 | 185.610 | 0,0183 |
| `cnr-iriss-allegato-a-stato4-1` | fuori gold | 9 | n/d | 1 | 8 | 60.813 | 0,0072 |
| `rr-stato4-1` | ripresa del difetto `p65` | 61 | 1 | 3 | 4 | 62.738 | 0,0076 |

Colonna Caselle: `compilazione-v1` usa una casella in formato legacy, letta da `valuta_caselle.py`.
Trapani e CNR non hanno caselle. Per `rr-stato4-1` il conteggio delle bozze comprende le due
storiche copiate da `dialogo-11`; quella nuova è la terza.

### A chi attribuire le omissioni

| Esecuzione | Mancanti rispetto alla bozza migliore | Causa |
|---|---|---|
| `minervino-v3-stato4-1`, `ramo-errato` | 0 | Nessuna |
| `sd4-libera-1`, `sd4-libera-2` | 1 | Modello o fonte |
| `sd4-multi-1` | 2 | Modello: proposta mancante |
| `sd4-numero-1` | 2 | Rinvio dell'USER simulato |
| `sd4-multi-2` | 10 | Rinvio dell'USER simulato su domande di verifica |
| `minervino-v3-stato4-2` | 18 | Rinvio dell'USER simulato: 11 su una condizione ancorata a «di essere inserito/i…», 7 su una domanda di verifica |
| `sd4-ambigua-1` | 27 | 23 controllo sui ruoli, 2 rinvio USER, 2 proposta mancante |
| `minervino-rinvio-stato4-1` | 26 | 23 sospesi dal narratore sulla scelta rinviata, 2 proposta mancante, 1 rinvio |
| `sd4-noramo-1` | 42 | 40 ramo negato di proposito, 2 proposta mancante |

L'USER simulato rinvia ciò che la sua politica non riconosce. Quei valori bassi dipendono quindi da
una decisione dello script, non dal modello, e un utente reale potrebbe confermare. Lo stesso vale per
i valori bassi di `sd4-cnr-1` e `sd4-cnr-2`.

L'unico errato ricorrente è la carica: il gold ha «rappresentante legale», il DOCX il testo completo
della fonte. Era già così prima di questo lavoro. Il secondo errato di `sd4-multi-*` è il fax,
corretto di proposito dallo script.

## Prima e dopo

Stesse quattro varianti reali. «Prima» è la prima patch di questo lavoro, senza le correzioni emerse
dalle tracce.

| Variante | Prima | Dopo |
|---|---|---|
| Multipla, prova 1 | C55 E2 M4, scelta richiesta | C57 E2 M2, mai richiesta |
| Multipla, prova 2 | C56 E2 M3, etichetta chiesta | C49 E2 M10, mai richiesta, etichetta non chiesta; i 10 mancanti sono rinvii dello script |
| Numero | C58 E1 M2, intestazione 8/10, scelta chiesta 2 volte, etichetta chiesta | C58 E1 M2, intestazione 10/10, scelta chiesta 1 volta, etichetta non chiesta |
| Libera | C55 E1 M5, etichetta chiesta | C59 E1 M1, etichetta non chiesta |
| Totale di chiamate e token | 123 chiamate, 3.126.780 token | 104 chiamate, 2.802.836 token |
| Totale di costo e tempo modello | 0,3343 USD, 1.378 s | 0,3091 USD, 1.360 s |

Sono quattro esecuzioni per parte: bastano a vedere l'assenza di regressioni, non a misurare un
risparmio.

Riferimenti: la sessione manuale aveva 43 valori e la bozza migliore storica `a8e53b1d` ne ha 60.
A parità di informazioni autorizzate, `minervino-v3-stato4-1` e `ramo-errato` non perdono alcun
valore di quella bozza e ne scrivono 61.

Costo complessivo delle prove reali di questo lavoro: 44 esecuzioni, circa 2,51 USD.

## Suite

| Controllo | Tipo | Esito |
|---|---|---|
| pytest backend, sul commit `11627d4` | Simulato | 4675 passati, 8 saltati |
| Ruff | Statico | Pulito |
| vitest | Simulato | 198 passati |
| `tsc -b` | Statico | Pulito |
| oxlint | Statico | 2 avvisi già presenti, nessuno nuovo |
| Playwright `global-compilation`, `compilation-chat`, desktop e mobile | Simulato, API finte | 8 passati |
| Replay `dialogo-11` su questo codice | Replay | Bozza nuova senza dati in `p65` |

La copia storica di `dialogo-11` conserva la sua seconda bozza con la violazione originale: non è
stata modificata, come richiesto.

## Immutabilità e rollback

- Le bozze precedenti restano sul disco con il loro hash. Esempio `sd4-multi-1`: `1d61f3fefd` alle
  18:11:06, `cd3148bc0c` alle 18:11:22 dopo la correzione del fax.
- Rollback di `11627d4` verificato: l'albero del revert coincide con il genitore e i 29 test
  modificati, nella versione del genitore, passano. Il test nuovo non si raccoglie dopo il revert,
  come previsto. Registro: `rollback.txt` nella cartella della campagna.
- `STATUS.md` e `relazioni.md` non sono stati toccati né inclusi nel commit.

## Stato delle istanze

- Backend sperimentale riavviato su `11627d4`, stesse variabili, dopo quasi due ore di inattività.
  Sessioni e bozze storiche hanno gli stessi hash prima e dopo, il numero di turni è invariato.
- Il frontend su 5174 serve lo stesso albero.
- Istanza ordinaria spenta, HEAD `99ab052` invariato. Demo congelata e backup non toccati.
- Il backup su `/mnt/d/Backup-tesi-2026-11-02` resta incompleto.

## Limiti residui

1. **Controllo sui ruoli dei soci.** In 1 esecuzione finale su 20, più una della campagna intermedia,
   il modello copia il titolo «Soci» come ruolo attestato. Il controllo vuole un confronto letterale
   con «socio» e lascia vuoti 23 dati. Non l'ho allentato: è una protezione sui soggetti.
   Serve una tua decisione su un'eventuale equivalenza singolare-plurale.
2. **Scelta rinviata.** In `minervino-rinvio-stato4-1` il narratore sospende 23 dati in attesa della
   scelta rinviata. Nessuna casella indebita, ma 33 corretti contro i 45 della campagna precedente,
   con una sola esecuzione per parte.
3. **Condizioni ancorate altrove.** Formule come «il proprio interesse alla procedura in oggetto» o
   «di essere inserito/i…» non sono etichette né titoli: vengono chieste una volta, con un testo che
   può risultare strano. Su CNR «nella parte dell'operatore economico metti i dati di…» resta in attesa
   di quella conferma.
4. **«Metti tutti i dati nel modulo».** Non è gestita in modo uniforme: su Minervino non cambia nulla,
   su CNR chiede la conferma aperta, su Trapani può generare una nuova bozza identica. Non scrive mai
   dati non autorizzati, ma resta il rischio di un DOCX non chiesto in modo esplicito.
5. **Domande di verifica generiche.** «Uso dei dati trovati nelle fonti, da verificare» dice poco
   all'utente.
6. **Grafia dei valori digitati.** Il nome conserva la grafia registrata, gli altri valori restano
   letterali: in `sd4-libera-1` il comune di nascita è finito nel DOCX in minuscolo, come digitato.
7. **Riconoscimento di «i dati di X nel sottoscritto».** È un pattern italiano. Altre formulazioni
   passano dal router: restano protette dalla guardia, ma possono ricevere una domanda di chiarimento.
8. **Interfaccia.** Barra e pulsante unico sono verificati con API simulate, non in un browser su una
   sessione reale: lo vedrai con la prova manuale.
9. **Campione.** Poche esecuzioni per variante, con varianza reale del modello: i valori massimi non
   sono garantiti a ogni esecuzione.

## Promuovibilità

**Sicurezza: nessun blocco trovato** nelle 20 esecuzioni finali. **Qualità: non ancora stabile**: con
un USER che conferma si arriva a 59-61 valori, ma i limiti 1 e 2 possono togliere 23 dati in una
singola esecuzione.

Raccomandazione: fai la prova manuale in una nuova conversazione e decidi poi sul limite 1. Non ho
promosso, unito o pubblicato nulla.

Questo rapporto non è incluso nel commit. Dati grezzi nella cartella della campagna:
`METRICHE-stato4.json`, `METRICHE-stato4-dialoghi.json`, `METRICHE-stato4-scenari.json`,
`omissioni-stato4.txt`, `rollback.txt`.
