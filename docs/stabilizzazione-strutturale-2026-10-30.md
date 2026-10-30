# Stabilizzazione strutturale del compilatore DOCX (30 ottobre 2026)

Branch `stabilizzazione-strutturale/2026-10-30`, partenza dal codice `f0c48ba` (commit `2e940f7`).
Worktree isolati, nessun push, merge o modifica dell'app ordinaria. DeepSeek reale per
compilatore, narratore e guardia.

## Riepilogo

**Criterio dell'utente:** nessuna esecuzione fortunata da 60 campi seguita da una da 15; risultati
corretti, spiegabili e ripetibili su documenti differenti.

- **Ripetibili su 6 FORM su 7.** Campagna finale reale (25 run, codice costante `94e8726`),
  campi corretti per run:

  | FORM | Baseline `f0c48ba` | Finale `94e8726` |
  |---|---|---|
  | Trapani | 1 / 9 / 9 / 1 / 9 | **9 / 9 / 9 / 9 / 9** |
  | Compilazione | 13 / 17 / 17 | **18 / 18 / 18** |
  | CNR IRISS | 1 / 6 / 13 | **10 / 10 / 10** |
  | Checkbox | 2 / 5 / 7 | **7 / 8 / 7** |
  | Bergamo | 1 / 1 / 1 | **1 / 1 / 1** |
  | Catanzaro (azienda) | 7 / 11 / 7 | 7 / 8 / 11 |

- **Minervino resta variabile:** 24 / 43 / 53 / 59 / 52 contro 55 / 56 / 51 / 43 / 34; media
  simile, scarto maggiore. Le perdite restanti nascono dal modello:
  - dati che l'analisi non propone;
  - proposte respinte dai validatori e non recuperate;
  - dubbi «source» del narratore, ora resi espliciti come domande di verifica. La policy
    simulata congelata le rinvia; un utente reale potrebbe rispondere.
- **Spiegabili ovunque:**
  - 0 sospensioni silenziose in tutti i run finali (nella baseline 31 in Minervino, 15 in
    compilazione, 7 in Catanzaro, 3 in checkbox);
  - ogni dato bloccato ha una causa registrata e, se serve una risposta, la sua domanda.
- **Corretti:**
  - 0 dichiarazioni autorizzate;
  - 0 caselle errate o cambiate fuori report;
  - DOCX sempre uguale al report;
  - errati soltanto la carica più ampia del gold di Minervino, già nota, letterale della fonte.
- **Sei commit,** ciascuno con test fallito prima e passato dopo e rollback verificato:
  - tre meccanismi, uno per area;
  - tre correzioni nate dalla campagna intermedia.

## Metodo

- **Baseline congelata:** `BASELINE.json` con gli hash di report, DOCX, valutazione, turni e
  chiamate dei 25 run reali `f0c48ba`, più l'hash degli scenari (`8a36e668aee2`).
- **Costanti:** scenari, policy USER v3 e 29 file FORM/SOURCE identici, verificati per hash prima
  di ogni giro. Concorrenza 4, un runtime nuovo per run, profilo AI cifrato mai letto.
- **Giri reali:**
  1. pilota di 3 run su `ee80067`, per intercettare rotture;
  2. campagna intermedia di 25 run su `ee80067`, che ha fatto emergere 3 difetti;
  3. campagna finale di 25 run su `94e8726`;
  4. giro mirato di 6 run sull'ultima correzione (`4dd1087`).
- **Misure per run:**
  - valori corretti, errati, non attesi;
  - posizioni corrette in tutti i run;
  - perdite per fase, dagli esiti del backend;
  - sospensioni senza domanda;
  - turni, domande, chiamate e costo;
  - verifica indipendente del DOCX: testo dei valori e stato di ogni casella rispetto a report
    e originale.
- **Offline:** riesecuzioni deterministiche sugli stati e sulle risposte registrate dei run reali.
  Sono stime, indicate come tali.

## Cause dimostrate (baseline e campagna intermedia, run reali)

| Area | Causa | Evidenza reale |
|---|---|---|
| 3 | Le proposte respinte dai validatori non venivano mai ritentate: esistevano solo tentativi per errori strutturali | Minervino 26 campi persi in un run, checkbox 10, Catanzaro 8; offline 12 segmenti in 9 run su 25 |
| 1 | La condizione era ancorata al frammento scelto dal modello. A Trapani «(eliminare le opzioni non pertinenti)» diventava la domanda e la risposta dipendeva da quel testo | 4 run su 11 con 8-9 valori persi; negli altri run la stessa condizione era ancorata all'alternativa e confermata |
| 2 | Le sospensioni del narratore senza collegamento verificabile non producevano mai una domanda | 139 sospensioni finali su 139 mai chieste, quasi tutte su valori uguali al gold o equivalenti |
| 2 | Una conferma USER il cui ambito cambia dopo la risposta blocca i dati senza essere richiesta di nuovo | Intermedia, Minervino run 5: 52 valori bloccati, 2 corretti invece di 55-60 |
| 3 | Il recupero correggeva il binding ma rompeva i fatti già ancorati | Intermedia, Minervino run 1: 24 soci |
| 2 | La scelta di un gruppo con opzioni sospese entrava nel pool solo al turno successivo, che non arrivava | Intermedia, checkbox run 3: 3 sospensioni silenziose |

## Scelte architetturali

**Profilo nuovo `sezioni-2026-10-30`:**
- tre revisioni: `segment_recovery_revision`, `form_clause_revision`, `hold_resolution_revision`;
- le sessioni esistenti non vengono aggiornate;
- il profilo precedente `sezioni-2026-10-25` resta disponibile come interruttore di emergenza
  lato server.

**1. Condizioni ancorate al FORM** (`compilation_form_clauses.py`):
- il registro delle clausole si ricava solo dal catalogo immutabile del DOCX:
  - opzioni con casella e la loro continuazione;
  - alternative di un elenco da sfoltire: blocchi separati da righe vuote dopo «eliminare /
    cancellare … non pertinenti», la tabella unita al blocco precedente, fino all'intestazione
    in grassetto successiva;
- una condizione ancorata all'istruzione o all'intestazione dell'elenco viene divisa per
  alternativa, ciascuna con esattamente le sue destinazioni;
- una condizione ancorata a una clausola la porta con sé; la domanda mostra l'etichetta della
  clausola ed è formulata dal backend, uguale in ogni run;
- distinzioni mantenute:
  - le caselle restano scelte USER e non diventano mai conferme di applicabilità;
  - le dichiarazioni restano autorizzazioni procedurali, non toccate;
  - nessuna condizione è inventata e nessuna destinazione guadagna o perde una restrizione.

**2. Sospensioni strutturate** (`hold_resolution_revision`):
- ogni sospensione ha una causa registrata dal backend: `fonte_insufficiente`,
  `applicabilita_incerta` o `scelta_USER`;
- i rifiuti del validatore e i rinvii restano esiti distinti negli esiti per campo;
- risoluzione:
  - una casella di un gruppo valido si risolve con la scelta esplicita del gruppo, posta dal
    backend nello stesso turno;
  - ogni altro caso con una domanda di verifica per causa e citazione: la clausola FORM per un
    dubbio di applicabilità, i valori documentati per un dubbio sulla fonte;
- regole di rilascio:
  - solo una conferma o una scelta esplicita rilascia;
  - un diniego esclude, un rinvio resta rinvio;
  - un dato confermato non viene chiesto di nuovo;
  - un collegamento già verificato mantiene il suo rilascio (contro-esempi P3 C8 e C9);
- una conferma il cui ambito è cambiato continua a bloccare ed è richiesta di nuovo, dicendo
  perché.

**3. Recupero mirato** (`apply_recovery`, `with_original_facts`):
- a ogni segmento analizzato con proposte respinte corrisponde una sola seconda chiamata,
  limitata alle destinazioni respinte, con i motivi del validatore;
- dalla risposta si accettano solo le destinazioni respinte, con i validatori invariati;
- fatti, binding, condizioni e gruppi del recupero hanno nomi propri, il loro ambito non tocca
  altre destinazioni, e le condizioni originali restano sul campo;
- se il fatto recuperato fallisce, si prova il campo recuperato con il fatto originale già
  ancorato: il valore resta quello verificato e la proprietà è ancora controllata;
- le destinazioni ancora respinte tengono la proposta originale, così le riparazioni
  deterministiche successive le trovano invariate;
- il recupero è scartato se cambia una qualsiasi destinazione già accettata;
- sono esclusi:
  - il blocco del firmatario, perché è una decisione USER;
  - i rifiuti riparati dal recupero deterministico già esistente.

**Non indeboliti:** guardia, validatori (grounding, ruoli K3, polarità delle opzioni), ricevute
d'ambito, autorizzazioni procedurali, gate di export.

## Commit, test e rollback

| Commit | Contenuto | Test nuovi (falliti prima) |
|---|---|---|
| `8e16c23` | Recupero mirato dei rifiuti del validatore e profilo nuovo | 16, con una prova di mutazione dell'invariante sulle destinazioni accettate |
| `4c40544` | Clausole FORM, divisione delle condizioni d'elenco, testo del backend | 12, con una prova di mutazione sul raggruppamento delle clausole equivalenti |
| `ee80067` | Cause e risoluzioni delle sospensioni | 13, con le varianti C8/C9 |
| `9484596` | Recupero per componente: il fatto originale resta | 2 |
| `94e8726` | Conferma con ambito cambiato richiesta di nuovo | 2 |
| `4dd1087` | Scelta di un gruppo sospeso posta nello stesso turno | 1 |

- **Suite backend:** su `4dd1087` 4.255 passati, 8 saltati; Ruff PASS. File `suite-*.txt`.
- **Rollback di ciascun commit:** l'albero torna uguale al genitore e i nuovi test falliscono sul
  codice ripristinato; i test modificati del profilo passano nella versione del genitore
  (`rollback.txt`). Per i test aggiunti a file esistenti la verifica è stata fatta a mano.
- **Errori miei colti dalla suite o dai test prima del commit:**
  - una variabile che nascondeva la chiave di raggruppamento delle condizioni equivalenti;
  - la sovrascrittura della proprietà nel recupero per componente, che avrebbe aggirato il
    controllo del validatore.
- **Nota sui test:** i test esistenti girano col profilo «storico» (conftest), mentre i nuovi
  meccanismi sono provati col profilo ordinario. La copertura del profilo nuovo è quindi quella
  dei test aggiunti e dei run reali.

## Verifica offline su FORM differenti (stati e risposte registrate, stime)

- **Recupero:** 12 segmenti in 9 run su 25 lo attiverebbero, sulle stesse destinazioni perse
  nella baseline (Minervino 25 in un run, checkbox 10, Catanzaro 8). Le destinazioni del
  firmatario e quelle riparate dal recupero deterministico sono escluse.
- **Clausole:**
  - Trapani: con la stessa policy, i 4 run rinviati ottengono la conferma di «Legale
    rappresentante di Società di Ingegneria» (35 valori) e l'esclusione delle altre alternative;
  - nessuna decisione cambia sulle 132 condizioni ancorate a clausole;
  - gli altri FORM non cambiano.
- **Sospensioni:** ogni sospensione finale registrata riceve 1-3 domande per run:
  - dubbi «source»: 139 dati, verifiche che la policy rinvia;
  - caselle sospese: 38 dati, scelta del gruppo;
  - dubbi di applicabilità su clausola FORM: 23 dati, la clausola.

## Risultati reali prima e dopo

| FORM | Baseline `f0c48ba` | Intermedia `ee80067` | **Finale `94e8726`** | Mirato `4dd1087` |
|---|---|---|---|---|
| Minervino (61) | 55 / 56 / 51 / 43 / 34 | 34 / 60 / 58 / 32 / 2 | **24 / 43 / 53 / 59 / 52** | 51 / 56 |
| Trapani (9) | 1 / 9 / 9 / 1 / 9 | 9 / 9 / 9 / 9 / 9 | **9 / 9 / 9 / 9 / 9** | — |
| Compilazione (18) | 13 / 17 / 17 | 18 / 18 / 14 | **18 / 18 / 18** | 3 (segmento fallito, sotto) |
| Checkbox (7-8) | 2 / 5 / 7 | 6 / 7 / 7 | **7 / 8 / 7** | 7 / 7 / 8 |
| Catanzaro (16) | 7 / 11 / 7 | 11 / 11 / 2 | **7 / 8 / 11** | — |
| CNR IRISS | 1 / 6 / 13 | 10 / 10 / 1 | **10 / 10 / 10** | — |
| Bergamo | 1 / 1 / 1 | 1 / 1 / 1 | **1 / 1 / 1** | — |

| Misura (finale contro baseline) | Baseline | Finale |
|---|---|---|
| Posizioni corrette in tutti i run: Trapani / compilazione / checkbox / CNR | 1/9, 13/18, 2/7, 1/13 | **9/9, 18/18, 7/8, 10/10** |
| Posizioni corrette in tutti i run: Minervino / Catanzaro | 17/61, 3/16 | 17/61, 7/16 |
| Scarto tipo Minervino / Trapani / CNR / checkbox | 8,3 / 3,9 / 4,9 / 2,1 | 12,2 / **0** / **0** / **0,5** |
| Sospensioni silenziose (somma dei run) | 56 | **0** |
| Errati / non attesi | 1 / 5 | 2 / 3 (carica letterale; CF/P.IVA della mappa) |
| Dichiarazioni autorizzate, caselle errate o fuori report | 0 | 0 |
| Turni / domande per run | 1-5 / 0-11 | 1-4 / 0-12 |

**Perdite di Minervino nel finale:**
- 28 dati mai proposti dall'analisi: nel run 1 il modello giudica che le righe della tabella non
  provino la qualità di socio;
- 25 rinvii espliciti delle domande di verifica, cioè dubbi «source» del narratore, da parte
  della policy;
- 19 rifiuti del validatore non recuperati.

**Peggioramenti trattati, non tenuti per avanzare:**
- l'intermedia aveva Minervino a 2 nel run 5, per la ricevuta con ambito cambiato: corretta in
  `94e8726`, assente nel finale;
- il run 1 perdeva 24 soci per il recupero che rompeva i fatti: corretto in `9484596`;
- il checkbox run 3 aveva 3 sospensioni silenziose: corrette in `4dd1087`.

**Giro mirato su `4dd1087`:**
- checkbox 7/7/8 e Minervino 51/56, nessuna sospensione silenziosa;
- la compilazione scende a 3 perché il modello ha restituito due volte JSON malformato nel
  segmento 1. I tentativi strutturali esistenti (1 per segmento) si sono esauriti e 14
  destinazioni sono rimaste esplicitamente «non accertate». Non dipende dalle modifiche.

## Limiti residui che richiedono decisioni

1. **Domande di verifica e utente simulato.** Le domande che risolvono i dubbi «source» sono
   rinviate dalla policy congelata, che non ha regole per esse. Il punteggio simulato di
   Minervino dipende ancora da quanti dubbi il narratore solleva. Serve una prova con utenti
   reali, oppure una decisione su quanto peso dare a un dubbio non verificabile su un valore già
   validato: nella baseline 129 dei 139 dubbi bloccavano valori uguali al gold o diversi solo
   per forma («Ing.», «Bari (BA)», formato della data); gli altri 10 la carica più ampia del gold.
2. **Omissioni dell'analisi:** dati che il modello non propone affatto. Il recupero copre i
   rifiuti, non le omissioni. Un secondo tentativo sulle destinazioni con SOURCE disponibile e
   nessuna proposta va deciso, con i suoi costi.
3. **Equivalenze dei validatori:** grafie delle proprietà («nome e cognome» / «nome_cognome»)
   e singolare/plurale dei ruoli. Toccano la sicurezza di attribuzione K3.
4. **Clausole di partecipazione senza struttura** (Catanzaro «Specificare la tipologia…», CNR
   «il proprio interesse alla procedura»): nessuna clausola si ricava dal DOCX senza inventarla.
   Restano dipendenti dalla clausola scelta dal modello.
5. **JSON malformato:** un solo tentativo strutturale per segmento non basta sempre.
6. **Copertura dei test:** i test storici non esercitano il profilo nuovo; le nuove revisioni
   sono provate dai test aggiunti e dai run reali.

## Costi (tariffe pubbliche; fatturazione non verificata)

| Giro | Run | Chiamate | Token | USD stimati |
|---|---:|---:|---:|---:|
| Pilota `ee80067` | 3 | 48 | 1.003.600 | 0,12 |
| Intermedia `ee80067` | 25 | 328 | 6.705.415 | 0,76 |
| Finale `94e8726` | 25 | 308 | 6.298.264 | 0,70 |
| Mirato `4dd1087` | 6 | 79 | 1.629.104 | 0,20 |
| **Totale** | **59** | **763** | **15.636.383** | **1,78** |

- Tutte le chiamate hanno risposto 200.
- Il costo per run del finale è uguale a quello della baseline (0,70 USD per 25 run): le
  chiamate in più del recupero sono compensate.

## Giudizio

- **Ripetibilità:** obiettivo raggiunto per i FORM con struttura riconoscibile. Trapani,
  compilazione, CNR e checkbox danno ora lo stesso risultato corretto in ogni ripetizione;
  prima oscillavano fino a 1 contro 13.
- **Minervino non lo è ancora.** Le sue oscillazioni nascono da scelte del modello che il
  backend non può verificare (omissioni, dubbi sulla fonte); oggi sono tutte visibili e
  risolvibili da un utente.
- **Correttezza e autorizzazioni:** intatte in 59 run reali.
- **Uso consigliato:** bozza con revisione, guidata dalle domande di verifica. Per Minervino
  serve una delle decisioni 1-2.

## Dati

`backend/data/compilation-audit/strutturale-20261030/` (ignorata da Git):
- `BASELINE.json`, `scenari/` (copia verificata per hash), `strumenti/`;
- `analisi/` (`recupero_offline.py`, `ancore.py`, `clausole_offline.py`, `sospensioni.py`,
  `sospensioni_offline.py`, `confronto.py`, `verifica_finale.py`);
- `esecuzioni/<scenario>-{pilota,strutturale,definitivo,verifica4dd1087}-<n>/`;
- `AGGREGATO-*.json`, `VERIFICA-*.json`, `CONFRONTO-*.json`, `giro-*.log`, `suite-*.txt`,
  `rollback.txt`.

Worktree:
- sviluppo: `tesi-strutturale-20261030`;
- esecuzione: `tesi-strutturale-ee80067`, `tesi-strutturale-94e8726`, `tesi-strutturale-4dd1087`.
