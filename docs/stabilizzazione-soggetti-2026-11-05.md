# Stabilizzazione della compilazione DOCX e del narratore

Rapporto del 5 novembre 2026. Ramo `narratore-chiarezza/2026-10-31`, worktree
`/home/montesano/tesi-narratore-chiarezza-20261031`, base `e9a374e` (rapporto `cdba67d`). Nessun
push, merge o promozione. La demo ordinaria non è stata toccata.

## Esito

**Valutazione: non promuovibile ora.** Le correzioni funzionano, ma la campagna reale sul codice
definitivo è incompleta. Durante l'ultimo giro DeepSeek ha iniziato a rispondere `402` (credito
esaurito), e una sonda successiva ha avuto la stessa risposta. Mancano quindi tre verifiche reali, e
una delle correzioni più delicate è provata solo offline. La sezione «Promuovibilità» dice cosa
serve.

Risultati principali, tutti letti dal contenuto dei DOCX delle esecuzioni reali indicate:

| Punto | Prima | Ora | Dove è provato |
|---|---|---|---|
| Soggetto sbagliato (77777777777 di Studio Rossi) | nessun controllo deterministico | mai nel DOCX | 14 dialoghi reali (28 bozze), guardia reale |
| REA e Registro Imprese | falso conflitto, `p17.s1` vuoto | `01234560981` scritto, REA assente | dialoghi reali `c52e5bb`, `c500642`, `ec78660` |
| Due Registri Imprese discordanti | non provato sul reale | campo vuoto e domanda motivata | `conflitto-1`, `conflitto-2` |
| Firmatario documentato | 0/9 | 9/9 | 8 dialoghi reali `c500642`, `ec78660` |
| Direttore tecnico | 4 su 8 persi | 5–8 su 8, varia per esecuzione | 8 dialoghi reali |
| Casella 4 senza scelta | vuota | vuota, 0 su 13 nell'XML | 8 dialoghi reali |
| Casella 4 con scelta esplicita | rifiutata o errore 500 (`c52e5bb`) | 1 su 13, sul paragrafo giusto | 8 dialoghi reali |
| Seconda bozza | 0 valori in un caso | nessun valore perso | 8 dialoghi reali |
| Turno «Genera ora» | 95–100 s, 500 oltre il timeout | 5–10 s, nessun 5xx | 8 dialoghi reali |

## Cause effettive

Ogni causa è stata trovata sui dati reali prima di correggerla.

| # | Problema | Causa effettiva | Correzione | Commit |
|---|---|---|---|---|
| 1 | Dati riferiti al soggetto sbagliato | Nessun controllo deterministico tra chi è nominato nell'evidenza o nel messaggio e chi è il proprietario della destinazione | Controllo del soggetto su evidenze, destinazioni e valori USER; veto del backend, non solo il testo `reason` del modello | `2b3e63e` |
| 2 | Firmatario rifiutato dalla guardia | Il proprietario atteso di un campo persona veniva preso dall'azienda vicina nella stessa catena | Il soggetto atteso è calcolato prima sull'entità; nessun nome di un'altra entità | `b503f0b` |
| 3 | Falso conflitto REA/Registro Imprese | Il modello proponeva due identificativi diversi come alternative della stessa proprietà | Tipo dell'identificativo ricavato dall'evidenza e dalla destinazione; due valori dello stesso tipo restano conflitto | `623b435` |
| 4 | 9 dati del firmatario persi | Il router metteva il nome su uno slot inesistente e il backend lo scartava in silenzio | Un messaggio può rispondere e dare altri dati; le parti non registrate vengono dette all'utente | `db2873e`, `c52e5bb` |
| 5 | Seconda bozza con 0 valori | Una conferma ripetuta senza testo di domanda faceva sparire il gruppo della scelta; il digest della ricevuta falliva e 134 campi venivano bloccati | La conferma ripetuta conserva la ricevuta; la scelta del FORM resta indirizzabile | `c52e5bb` |
| 6 | Turno di bozza oltre 90 s, poi 500 | Ogni lettura ricalcolava l'ambito delle ricevute una volta per campo: circa 7.000 derivazioni per narrazione. Il costo esisteva già prima di questo ramo | Target e prova derivati una volta per ricevuta in ogni verifica | `4a6b391` |
| 7 | Scelta della casella 4 rifiutata | Router e guardia concordavano sull'opzione 4, ma il modello copiava l'etichetta del FORM in `value` e il controllo letterale rifiutava | Il valore di una scelta è la frase dell'utente; i numeri delle opzioni passano comunque dalla guardia | `c500642` |
| 8 | «Sì, confermo» perso e richiesto di nuovo | Il nome ripetuto sia sullo slot sia sul target faceva scartare entrambe le risposte dello slot | Si toglie solo il duplicato esatto di valore e citazione | `c500642` |
| 9 | Dati del direttore persi a caso | L'unione per chiave personale dipendeva dalla parola scelta per la proprietà (`nome_cognome`, `albo_professionale`, `data_iscrizione`) | Vocabolario tipizzato; le chiavi richieste non cambiano | `3c954ed` |
| 10 | Una citazione in più faceva respingere il valore | Due record di ruolo, o riga di tabella più riga nominativa, venivano trattati come dubbio | Una citazione in più conta se riguarda la stessa persona e nessun'altra iscrizione | `3c954ed`, `ec78660` |
| 11 | Domanda inutile «Bari» o «Bari (BA)» | Lo stesso dato in due formati risultava alternativa | Confronto tipizzato per provincia, data e nome; due valori reali restano una scelta | `ec78660`, `c7006a9` |
| 12 | Scrittura nel ramo sbagliato del FORM | La scelta esplicita dell'opzione 4 rilasciava anche i dati trattenuti di un'altra opzione: 9 valori in `p65.*`, il ramo consorzio | Una scelta chiude solo il proprio ramo; cambiarla riapre l'altro | `c7006a9` |
| 13 | Errore 500 dopo un'analisi fallita | Con `audit` nullo il contesto della chat andava in errore invece di riportare il rifiuto del provider | Nessuna destinazione finché non c'è un audit | `5c5dcb0` |

Il difetto 12 è emerso perché l'utente scriptato aveva confermato per errore anche il ramo consorzio.
L'errore dello script ha rivelato un difetto vero, che su Minervino reale non si era mai presentato.

## Modifiche

Tutte le novità sono attive solo con il profilo `sezioni-2026-11-05` e i flag
`subject_check_revision`, `identifier_type_revision`, `role_proof_revision` e
`conversation_turn_revision`. Fanno eccezione:
- `4a6b391`, che non cambia alcun esito: 0 differenze su 111 sessioni reali registrate;
- `5c5dcb0`, che agisce su ogni profilo ma solo su sessioni senza audit;
- il testo del prompt di routing, che in questo ramo cambia per ogni sessione con destinazioni
  indirizzabili. Il comportamento del backend resta dietro i flag.

Non sono stati indeboliti Gate, condizioni FORM, controllo SOURCE/USER o validazione all'export. Non
ci sono regole per un singolo FORM né eccezioni per Mapi o Minervino. Le chiavi di identità richieste
per unire una persona sono le stesse di prima.

### Rollback

Verificato su ogni commit con `git revert --no-commit` in un worktree dedicato: l'albero risultante
coincide con il genitore e i test del genitore passano. Registro in
`backend/data/compilation-audit/stabilizzazione-soggetti-20261105/rollback.txt`.

Per tornare indietro basta ripristinare `e9a374e`. In alternativa, per le sole nuove sessioni, si può
selezionare un profilo precedente con `MAPI_COMPILATION_PROFILE`. I commit non sono stati pubblicati.

## Risultati offline

Nessuna chiamata a un provider.

| Controllo | Esito |
|---|---|
| Suite backend su `5c5dcb0` | 4550 passati, 8 saltati |
| Suite backend su `c7006a9` | 4549 passati, 8 saltati |
| Ruff | pulito |
| Memoria delle ricevute | 111 sessioni reali, 222 confronti, 0 differenze nei campi bloccati |
| Lettura sessione | da 14,6 s a 0,5 s sotto profiler, sessione `dialogo-5` |
| Narrazione | da 275,8 s a 5,5 s sotto profiler, modello simulato |
| Unione per ruolo sul gold | 90 run registrati: 19 valori recuperati, tutti prima mancanti e uguali al gold a meno del titolo, 0 errati; cambia solo Minervino |
| Controllo del soggetto sul gold | 90 run: 2.014 campi documentati, 0 respinti, 0 sospesi |
| Identificativi sul gold | 90 analisi: 2 cambiamenti, entrambi corretti |
| Alternative solo di formato | 100 run: 12 sciolte, nessun valore davvero diverso sciolto |
| Blocco dell'altro ramo | 111 sessioni, 32 con scelta esplicita: agisce solo su `dialogo-11` |
| Crash con analisi fallita | riprodotto e corretto sulla sessione reale `compilazione-v1-finale-1` |

Questi confronti sono stime su stati registrati, non esecuzioni nuove.

## Risultati reali con DeepSeek

### Guardia reale

Su `ec78660`, con `compilation_reply_guard.py` e `compilation_subject_check.py` identici a quelli
finali, 12 casi ripetuti 2 volte: 24 esiti
corretti su 24. Gli 8 positivi sono accettati, comprese le correzioni USER legittime. I 16 negativi
sono rifiutati: 6 dal veto del backend, 10 dalla guardia. Copre altra società, altra persona nota,
persona sconosciuta, persona al posto di società, domicilio o studio al posto della sede, riferimento
ambiguo e carica di un'altra persona.

### Dialoghi reali con i messaggi del test manuale

Punteggio contro il gold, sulla seconda bozza.

| Esecuzione | Commit | Corretti | «Errati» | Non attese | Mancanti | Firmatario | Direttore | Casella 4 |
|---|---|---|---|---|---|---|---|---|
| `dialogo-7` | `c500642` | 35 | 2 | 0 | 24 | 9/9 | 8/8 | sì |
| `dialogo-8` | `c500642` | 54 | 2 | 0 | 5 | 9/9 | 5/8 | sì |
| `dialogo-9` | `c500642` | 56 | 2 | 0 | 3 | 9/9 | 6/8 | sì |
| `conflitto-1` | `c500642` | 57 | 2 | 0 | 2 | 9/9 | 8/8 | sì |
| `dialogo-10` | `ec78660` | 56 | 2 | 0 | 3 | 9/9 | 5/8 | sì |
| `dialogo-11` | `ec78660` | 59 | 2 | **9** | 0 | 9/9 | 8/8 | sì |
| `dialogo-12` | `ec78660` | 56 | 2 | 0 | 3 | 9/9 | 7/8 | sì |
| `conflitto-2` | `ec78660` | 58 | 2 | 0 | 1 | 9/9 | 8/8 | sì |

I 2 «errati» sono attesi e uguali ovunque:
- `p15.s3`: è la correzione libera del fax chiesta dallo script, diversa dal gold per costruzione.
- `p14.s0`: «amministratore unico e rappresentante legale» è la carica detta dall'utente e presente
  nella SOURCE, più ampia del gold «rappresentante legale». Era già documentato nel rapporto del 30
  ottobre.

Le 9 scritture non attese di `dialogo-11` sono il difetto 12: corretto in `c7006a9`, verificato
offline e non ancora con un dialogo reale.

In tutte e 8 le esecuzioni:
- «BOZZA NON VERIFICATA» è presente;
- gli hash delle bozze precedenti coincidono;
- `ready_for_submission` è falso;
- nessun dato rifiutato o rinviato è scritto;
- nessuna casella è scritta nella prima bozza.

Il conflitto reale è presentato così: «Le fonti riportano «01234560981» oppure «99999999901». Sono due
valori diversi dello stesso tipo (Registro Imprese): indica quale è corretto.»

### Campagna mirata su `c7006a9`

| Esecuzione | Esito |
|---|---|
| `trapani-v3-finale-1` | valida, 9/9, DOCX 9/9 |
| `trapani-v3-finale-2` | valida, 9/9, DOCX 9/9 |
| `minervino-v3-finale-3` | valida, 49 corretti, 0 errati, 12 mancanti, DOCX 49/49 |
| `minervino-v3-finale-1`, `-2` | **interrotte da 402** durante i turni |
| `checkbox-v2-finale-1`, `-2` | **interrotte da 402**, non valutabili |
| `cnr-iriss-allegato-a-finale-1`, `-2` | **interrotte da 402** alla prima chiamata |
| `compilazione-v1-finale-1`, `-2` | **interrotte da 402** dopo la prima chiamata |

Le esecuzioni interrotte non misurano la qualità e non sono regressioni. Non sono nemmeno una prova a
favore: i loro 0 errati valgono poco, perché nessuna è arrivata a esportare.

I dialoghi su `c7006a9` non sono partiti per un mio errore: una modifica allo script dell'utente
simulato lo aveva corrotto. Quando l'ho ripristinato, il credito era già finito.

## Le 12 regressioni obbligatorie

| # | Regressione | Esito | Prova |
|---|---|---|---|
| 1 | Evidenza del soggetto corretto accettata | OK | Reale: guardia 8/8 e DOCX 9/9. Test |
| 2 | Evidenza di altro soggetto respinta | OK | Reale: guardia 16/16 e 77777777777 in 0 bozze su 28 |
| 3 | Soggetto ambiguo, richiesta mirata | OK | Reale: guardia 2/2 `AMBIGUOUS` e «Puoi precisare soltanto questo punto?» |
| 4 | REA e Registro Imprese non confusi | OK | Reale: `p17.s1 = 01234560981`, REA in 0 bozze su 28 |
| 5 | Due valori discordanti restano conflitto | OK | Reale: `conflitto-1`, `conflitto-2`, campo vuoto e domanda motivata |
| 6 | Firmatario confermato recupera i dati | OK | Reale: 9/9 in 8 esecuzioni |
| 7 | Direttore nelle destinazioni corrette | **Parziale** | Reale: nessun valore errato o fuori posto, ma 5–8 su 8 secondo l'esecuzione |
| 8 | Casella 4 senza scelta vuota | OK | Reale: XML 0 su 13 nelle prime bozze |
| 9 | Casella 4 con scelta selezionata | OK | Reale: XML 1 su 13, paragrafo letto dal DOCX |
| 10 | Dichiarazioni non autorizzate vuote | OK | Reale: nessuna scrittura tra i dati rifiutati o rinviati |
| 11 | Correzioni libere e bozze successive | OK | Reale: fax corretto, nessun valore perso, in 8 esecuzioni |
| 12 | Vecchie bozze immutabili | OK | Reale: hash coincidenti. Bozze del test manuale intatte |

Salvo diversa indicazione le prove reali sono su `c500642` ed `ec78660`, non sul commit finale.

## Regressione del test manuale: classificazione

Bozza migliore `a8e53b1d` (60 valori) contro l'ultima `b7790bed` (46): 14 persi, 1 guadagnato
(`p46.s1`).

| Destinazioni | Categoria | Causa | Stato |
|---|---|---|---|
| 9 del firmatario (`p12`, `p13`, `p14.s0`) | Condizione o ricevuta USER | Nome su slot inesistente, scartato in silenzio: nessuna ricevuta | Risolto |
| `p17.s1` | Guardia o sospensione | Ciclo della guardia e falso conflitto REA/Registro | Risolto |
| `p39.cb0` | Condizione o ricevuta USER | Nessuna scelta esplicita in quella sessione: **vuota a ragione** | Corretto così |
| 4 del direttore (`p51.s0`, `p52.s0`, `p53.s0`, `p53.s4`) | Associazione al soggetto | Ruolo citato in un chunk, valori in un altro | Risolto in parte |

Una dichiarazione USER sul firmatario non viene usata come conferma d'identità automatica: i dati
derivati passano comunque dai controlli di ambito e soggetto.

### Confronto attuale a parità di autorizzazioni

Dialoghi reali su `ec78660` contro la bozza da 60, voce per voce, in
`omissioni-ec78660.txt`:

| Esecuzione | Mancanti | Dettaglio | Categoria |
|---|---|---|---|
| `dialogo-10` | 3 | `p53.s1`, `p53.s3` | Proposta LLM mancante |
| | | `p53.s2`, parola `provincia_iscrizione` | Associazione al soggetto, coperto da `c7006a9` |
| `dialogo-11` | 0 | | |
| `dialogo-12` | 2 | `p45.s0`, nome citato fuori dalla tabella dei soci | Associazione al soggetto, **residuo** |
| | | `p53.s2`, «Bari» contro «Bari (BA)» | Associazione al soggetto, coperto da `c7006a9` |
| `conflitto-2` | 1 | `p17.s1` | Guardia o sospensione, **corretto**: conflitto reale |

Nessuna omissione è nella categoria writer/export. In `minervino-v3-finale-3`, con la policy
simulata standard, i 12 mancanti sono:
- 8 del direttore sospesi dal narratore (guardia o sospensione);
- 3 con evidenza SOURCE non recuperata (`p14.s0`, `p14.s1`, `p15.s0`);
- `p39.cb0`, vuota a ragione.

### Replay della sessione manuale

Il replay offline su `c7006a9` dà 47 valori a parità di autorizzazioni e 55 con il firmatario. I 4
dati del direttore e `p14.s0` restano fuori per un motivo corretto: le ricevute di quella sessione
sono state date prima che quei dati fossero proposti, quindi non li coprono. Una sessione già aperta
richiede una nuova conferma; non viene aggiornata di nascosto. La vecchia bozza resta intatta.

## Chiarimenti inutili

- I dati documentati non vengono chiesti: nei dialoghi le domande sono su applicabilità, scelte e
  conflitti reali.
- La domanda che sblocca più dati viene prima.
- Le bozze distinguono assente, non valutato e sospeso.
- Sono rimaste domanda unica, istruzioni libere, pausa e ripresa, bozze parziali e successive,
  ricevute persistenti. Nessun questionario, nessun refactoring generale.

## Consumi reali

Stima con prezzi cache hit 0,003, cache miss 0,15, output 0,6 USD per milione di token.

| Gruppo | Esecuzioni | Chiamate | Stati HTTP | Token | Stima |
|---|---|---|---|---|---|
| Dialoghi `db2873e` | 3 | 65 | 200 | 2.003.053 | $0,235 |
| Dialoghi `c52e5bb` | 3 | 86 | 200 | 2.335.550 | $0,276 |
| Dialoghi `c500642` | 4 | 112 | 200 | 2.995.470 | $0,361 |
| Dialoghi `ec78660` | 4 | 98 | 200 | 2.648.262 | $0,295 |
| Campagna `c7006a9` | 11 | 105 | 78 × 200, 27 × 402 | 2.039.435 | $0,225 |
| Sonda del credito | 1 | 1 | 402 | 0 | $0 |
| **Totale esecuzioni** | | **467** | | **12.021.770** | **$1,391** |

La guardia reale ha fatto 4 giri con esito salvato: 70 chiamate e 1.563.084 token. Un altro giro è
terminato in errore senza salvare i risultati e non è conteggiato.

Ripetizioni sulle 11 esecuzioni valide degli ultimi commit:
- segmenti: 1 tentativo in più in 4 esecuzioni, nessuno nelle altre 7;
- errori di formato: 0;
- router: 1 turno ripetuto su 70;
- errori `429` e `5xx` del provider: 0.

## Scritture indebite

- **Soggetto sbagliato, REA, dichiarazioni non autorizzate, caselle senza scelta:** 0 in tutte le
  esecuzioni reali lette.
- **Ramo sbagliato:** 9 in `dialogo-11` (`p65.s0`–`p65.s8`), dopo la conferma errata dello script.
  Corretto in `c7006a9`, verificato offline e non con un dialogo reale.
- **Falsi valori:** nessuno rispetto al gold, oltre ai due casi attesi spiegati sopra.

## Problemi residui

1. **Campagna incompleta** per credito esaurito: checkbox, CNR, compilazione e dialoghi sul codice
   finale. Offline non risultano effetti su quei moduli, ma non è una prova equivalente.
2. **Difetto 12 senza prova reale.** La correzione è testata e verificata su stati reali registrati.
3. **Direttore tecnico variabile**, 5–8 su 8. Dipende da cosa propone e cita il modello:
   `source_not_found` su dati presenti, oppure il nome citato fuori dal record del ruolo. Sono
   omissioni, non valori errati. Non ho forzato il riempimento.
4. **Soci talvolta non assegnati:** in `dialogo-7` il modello omette 23 campi con la motivazione
   «nessun criterio per assegnarli agli slot». La prudenza è difendibile e l'ho lasciata, ma la bozza
   scende a 37 valori.
5. **Domande su rami già esclusi:** in `dialogo-11` il narratore chiede del consorzio anche se
   l'utente ha detto «società di ingegneria». Non scrive più nulla di sbagliato dopo la scelta, ma la
   domanda è evitabile.
6. **Sessioni già aperte** non si aggiornano: chi riprende una vecchia sessione deve riconfermare.
7. **Timeout residuo:** con turni oltre 90 s per lentezza del provider, la scrittura dello stato può
   ancora fallire con `database is locked` e un 500. Il costo CPU che lo causava è sparito e non si è
   più visto, ma il percorso non è stato cambiato.
8. **Report dei campi:** per un conflitto reale `field_outcomes` dice `nessuna_proposta`; la domanda
   all'utente è corretta, l'etichetta interna no.
9. **Etichetta incoerente** nella domanda del conflitto: in `conflitto-2` il modello chiama il campo
   «Numero iscrizione Camera di Commercio» anche se il tipo detto è Registro Imprese.

## Promuovibilità

**Non promuovere ora.** Il lavoro è un candidato promettente: sui dialoghi reali scrive più dati
corretti della migliore bozza manuale, senza errori di soggetto. Mancano però tre condizioni:

1. La correzione del ramo sbagliato (difetto 12) tocca un punto di sicurezza e va vista su DOCX reali.
2. Checkbox, CNR e compilazione non hanno alcuna esecuzione valida sul codice finale.
3. Minervino è l'unico modulo dei collaudi con questa scelta di qualità derivata: 27 sessioni su 97
   registrate, 0 negli altri 6 moduli. La sua generalità è quindi provata solo con test sintetici.

Per completare, dopo aver ricaricato il credito DeepSeek:

```bash
cd backend/data/compilation-audit/stabilizzazione-soggetti-20261105
C=/home/montesano/tesi-soggetti-5c5dcb0
PY=$C/backend/.venv/bin/python
for n in 1 2 3; do
  $PY strumenti/esegui_dialogo.py minervino-v3 fin2-dialogo-$n $C $((8300+2*n)) \
    > esecuzioni/fin2-dialogo-$n.log 2>&1 &
done
$PY strumenti/esegui_dialogo.py minervino-conflitto fin2-conflitto-1 $C 8310 \
  > esecuzioni/fin2-conflitto-1.log 2>&1 &
wait
CONCORRENZA=4 bash strumenti/giro.sh $C fin2 8400 \
  minervino-v3:3 checkbox-v2:2 cnr-iriss-allegato-a:2 compilazione-v1:2
```

Criteri per promuovere:
- 0 scritture non attese;
- `p65.*` vuoti anche con la conferma errata del ramo;
- nessun 5xx;
- CNR, checkbox e compilazione non peggiori del rapporto del 30 ottobre.

## Stato di repository e backup

- **Demo ordinaria:** `/home/montesano/tesi` è su `99ab052`. I 143 file di `backend/app` e
  `frontend/src` del tag `demo-default-r2-20261031` coincidono con quelli su disco. Nessun codice è
  stato toccato.
- **Sessioni storiche:** database sperimentale aperto solo in lettura o su copie temporanee. Bozze
  `4320c2ab`, `a8e53b1d`, `b7790bed` invariate.
- **File non miei:** `STATUS.md` e `relazioni.md` invariati e fuori dai commit, verificato con hash
  prima di ogni commit.
- **Backup su D: incompleto:** in `/mnt/d/Backup-tesi-2026-11-02` ci sono il bundle e `database/`;
  `app-ordinaria.tar` può essere troncato; mancano `altri-worktree.tar`, `SHA256SUMS` e `LEGGIMI`. Non
  ho sovrascritto nulla e non ho eseguito operazioni distruttive.
- **Worktree creati:** `tesi-soggetti-db2873e`, `-c52e5bb`, `-c500642`, `-ec78660`, `-c7006a9`,
  `-5c5dcb0`: esecuzioni a commit fisso, da tenere finché servono le verifiche.

## Dove trovare i dati

In `backend/data/compilation-audit/stabilizzazione-soggetti-20261105/`, cartella ignorata da Git:
- `esecuzioni/`: esecuzioni reali, con DOCX, report e chiamate al provider;
- `reale/`: guardia reale;
- `analisi/`: script di verifica;
- `verifica-dialoghi-ec78660.txt`, `omissioni-ec78660.txt`, `metriche-reali.txt`: risultati sintetici;
- `ruoli-offline.txt`, `conflitti-offline.txt`, `equivalenza-blocchi.txt`, `ramo-altra-opzione.txt`:
  confronti offline;
- `rollback.txt`, `suite-finale.txt`.
