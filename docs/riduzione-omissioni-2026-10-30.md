# Riduzione delle omissioni del compilatore DOCX (30 ottobre 2026)

Branch `riduzione-omissioni/2026-10-30`, partenza da `338da16` (ultimo codice di
`stabilizzazione-strutturale/2026-10-30`, che contiene `4dd1087`). Worktree isolati, nessun push,
merge o modifica dell'app ordinaria. DeepSeek reale per compilatore, narratore e guardia.

## Riepilogo

**Obiettivo dell'utente:** recuperare sistematicamente i dati documentati che oggi si perdono,
riducendo la variabilità senza ridurre la sicurezza, su FORM diversi.

- **Recuperato sistematicamente ciò che si perdeva per i dubbi del narratore.** In Minervino le
  perdite per rinvio USER di sospensioni passano da 34 in 7 run a 0 in 11 run. Fuori dal blocco
  dei soci (37 posizioni) Minervino scrive 30–36 valori corretti in 10 run su 11 (prima 19–35).
  L'eccezione è il pilota, dove la policy ha rinviato una condizione generica di
  partecipazione.
- **La variabilità che resta dipende dalla prima risposta del modello sul blocco dei soci**
  (24 posizioni, p43–p49), che va «tutto o niente»:
  - prima: 0/24 in 1 run su 7;
  - dopo: 0, 8 e 16 su 24 in 3 run su 11, 22–24 negli altri;
  - le tre forme osservate sono la condizione «ordine degli slot non documentato», il binding di
    ruolo respinto che il recupero non corregge e «source_not_found».
- **Su FORM diversi i risultati restano corretti.** Due run deboli hanno la stessa causa:
  - compilazione 4/18, CNR 1/10;
  - il modello rende condizionale un blocco intero con una domanda generica («il partecipante è
    l'operatore economico del profilo?») e la policy simulata la rinvia;
  - succede già sul codice precedente con lo stesso ancoraggio: compilazione `base-3`, CNR
    `f0c48ba-1` e `strutturale-3`.
- **Sicurezza invariata:** in 31 run nuovi
  - 0 dichiarazioni autorizzate;
  - 0 caselle errate o cambiate fuori report;
  - 0 sospensioni silenziose;
  - DOCX sempre uguale al report;
  - 0 errori HTTP.
- **Unico errato rispetto al gold:** `p14.s0` in 10 run Minervino su 11. La carica letterale
  della SOURCE, «amministratore unico e rappresentante legale», è più ampia del gold
  («rappresentante legale»). Prima era spesso sospesa; ora il riesame la rilascia, perché la
  SOURCE risolve il dubbio di decorrenza del narratore.
- **Perdite introdotte dal backend:** 4 nei giri intermedi (Trapani 3, Minervino 1), dovute alla
  fusione dei recuperi. Sono corrette da `d537e4a` e `c838339` e verificate sulle risposte reali
  registrate. Nel giro finale: 0.
- **Cinque commit**, ciascuno con test falliti prima e passati dopo e rollback verificato. Costo
  totale: 31 run, 420 chiamate, circa 1,05 USD stimati.

## Metodo

- **Baseline congelata:** `BASELINE.json` con gli hash dei 31 run reali precedenti:
  - 25 run `definitivo` su `94e8726`;
  - 6 run `verifica4dd1087` su `4dd1087`;
  - hash degli scenari `8a36e668aee2`.
- **Costanti:** scenari, policy USER v3 e 28 file FORM/SOURCE identici, verificati per hash prima
  di ogni giro. Concorrenza 4, runtime nuovo per run, profilo AI cifrato copiato e mai letto.
- **Prima le cause, sui dati reali registrati.** Ogni intervento è nato da una causa riprodotta
  sugli stati e sulle risposte dei run reali, non da un'ipotesi.
- **Prove offline prima di ogni giro.** Riesecuzioni deterministiche, senza chiamate al provider,
  sulle risposte registrate. Sono stime e le indico come tali. Script in
  `backend/data/compilation-audit/omissioni-20261030/analisi/`:
  - `riesame_offline.py`: riesame delle sospensioni;
  - `omissioni_offline.py`: posizioni senza proposta per classe e verdetto gold;
  - `fusione_offline.py`: fusione dei recuperi;
  - `perdite.py`: attribuzione delle perdite per stadio.
- **Giri reali contenuti, uno per stato del codice:**

  | Giro | Codice | Run | Scopo |
  |---|---|---|---|
  | `pilota` | `c8413ed` | 2 | intercettare rotture |
  | `omissioni` | `c8413ed` | 14 | Minervino ×5, Trapani, checkbox e CNR ×3 |
  | `regressione` | `d537e4a` | 5 | correzione nata dal giro precedente |
  | `finale` | `c838339` | 10 | codice finale, compilazione inclusa |

- **Attribuzione delle perdite (`perdite.py`):** ogni valore gold non scritto è assegnato al
  primo stadio che lo perde:
  - il modello non lo propone, con la classe di copertura dichiarata;
  - il modello lo propone e i validatori lo respingono;
  - il narratore lo sospende;
  - la policy USER lo rinvia o lo esclude;
  - il backend lo perde dopo una proposta valida;
  - una condizione lo esclude;
  - scritto con un valore diverso.

## Cause riprodotte sui dati reali

| Area | Causa | Evidenza reale |
|---|---|---|
| Sospensioni | I dubbi del narratore su valori documentati diventavano domande di verifica. La policy congelata le rinvia, quindi il dubbio bloccava valori validi | Baseline Minervino: 34 valori persi in 7 run per rinvio USER di verifiche (18 in un solo run). Offline, sulle sospensioni finali registrate, i valori sospesi erano quasi tutti uguali al gold o sue varianti di forma |
| Omissioni | Il modello lasciava destinazioni senza proposta dichiarandole «unassessed» («il FORM non indica quale nominativo occupi lo slot 1»), benché le SOURCE le documentino | `94e8726` Minervino run 1: 19 soci. Su tutti i run di riferimento la classe «unassessed» con ancora FORM è sempre un valore mancante: 19 su 19 |
| JSON malformato | Il modello chiudeva l'oggetto con una parentesi in meno (`finish_reason: stop`, modalità `json_object` già attiva). Il ritentativo generico ripeteva la stessa richiesta | 7 risposte di segmento su 406 in 147 run precedenti. 6 recuperate dal ritentativo generico; 1 segmento fallito (compilazione `verifica4dd1087-1`, 15 valori mancanti, 3 corretti invece di 18) |
| Recupero (giro `omissioni`) | Il recupero dichiarava sotto un nome nuovo una condizione sulla stessa clausola FORM. La copia raggiungeva destinazioni già accettate e l'invariante scartava l'intero recupero | Trapani `omissioni-2`: 3 valori persi, 6 invece di 9 |
| Recupero (giro `regressione`) | Il recupero ridichiarava un fatto identico a uno originale valido. La copia diventava un'alternativa in più di un campo accettato e l'invariante scartava il recupero | Minervino `regressione-1`, segmento 2 |

## Interventi

**Profilo nuovo `sezioni-2026-10-30-r2`:**
- tre revisioni nuove: `format_retry_revision`, `hold_review_revision`,
  `omission_recovery_revision`;
- le sessioni esistenti non vengono aggiornate;
- `sezioni-2026-10-30`, `-10-25` e `-10-24` restano interruttori di emergenza lato server.

**1. Riesame deterministico delle sospensioni SOURCE** (`compilation_hold_review.py`). Un dubbio
del narratore non blocca da solo un valore valido e non ne autorizza la scrittura: decide il
backend con SOURCE, condizioni, ricevute e validatori.

| Verdetto | Quando | Azione |
|---|---|---|
| `evidenza_assente` | Nessuna proposta ancorata, oppure una condizione esclusa | La sospensione resta; i validatori o i gate bloccano già il valore |
| `evidenza_contraddittoria` | Un passo SOURCE fuori dall'evidenza della proposta, nel chunk dello stesso soggetto, dice che la stessa proprietà non è disponibile o è cessata | La sospensione resta; la domanda USER mostra entrambi i testi |
| `applicabilita_incerta` | Una condizione che governa il campo è ancora aperta, oppure un dubbio di applicabilità su un campo senza condizioni | Resta in attesa della condizione o della domanda; una casella resta una scelta USER |
| `applicabilita_confermata` / `dubbio_generico` | Ogni condizione è confermata, o non ce ne sono, e niente contraddice il valore | La proposta torna ai gate ordinari, che soli decidono l'export; la bozza la elenca «da rivedere» |

**2. Recupero delle proposte omesse** (`compilation_omissions.py`):
- un'omissione è una destinazione di testo senza proposta e senza rifiuto del validatore, che il
  modello stesso ha dichiarato non valutata, con un'ancora FORM (paragrafo o testo dello slot);
- le altre classi non sono toccate:
  - «source_not_found»;
  - «manual_input»;
  - «condition_unknown»;
  - spiegazioni respinte;
  - chiarimenti USER;
  - celle di layout senza ancora;
- le omissioni vanno nell'unica chiamata di recupero del segmento, con il motivo dichiarato dal
  modello e la regola generale sull'ordine degli slot ripetuti (l'ordine in cui le SOURCE elencano
  i soggetti);
- ogni nuova proposta passa dai validatori ordinari, e nessun valore è riempito dal backend.

**3. Ritentativi per JSON malformato** (`format_feedback`):
- al massimo 2 per segmento e 4 per analisi;
- la richiesta ripetuta dice dove la risposta precedente si è rotta (messaggio e posizione) e
  chiede l'oggetto completo;
- i segmenti già validati non cambiano;
- tentativi, errori e token sono registrati nel report dei segmenti (`format_retries`);
- se i ritentativi finiscono, il segmento resta fallito e la bozza parziale sicura resta.

**4. Fusione dei recuperi, due correzioni nate dai giri reali:**
- una condizione del recupero sulla stessa clausola FORM (paragrafo e operatore) è la condizione
  originale (`d537e4a`);
- un fatto del recupero identico (soggetto, entità, aspetto, proprietà, valore) a un fatto
  originale **validato** è quel fatto (`c838339`). La copia di un fatto **respinto** resta un
  fatto distinto, perché la sua evidenza può essere la correzione. Il replay ha mostrato il caso
  reale `regressione-2`: il codice fiscale originale citava un passo che non lo conteneva.

**Non indeboliti:**
- guardia;
- validatori (grounding, ruoli, polarità delle opzioni);
- conferme esplicite e ricevute d'ambito;
- caselle, che restano scelte USER;
- dichiarazioni, che restano autorizzazioni procedurali;
- gate di export;
- invariante del recupero sulle destinazioni accettate.

Nessuna eccezione per FORM, società, persona o identificativo.

## Commit, test e rollback

| Commit | Contenuto | Test nuovi | Sul revert |
|---|---|---|---|
| `531ae7f` | Ritentativi per JSON malformato con la posizione dell'errore | `test_format_retry.py` | 6 falliti; 2 passati, cioè il test del profilo precedente (un solo ritentativo), che verifica proprio il comportamento vecchio |
| `9337eaa` | Riesame deterministico delle sospensioni | `test_hold_review.py` | errore di import: il modulo non esiste |
| `c8413ed` | Recupero delle destinazioni dichiarate non valutate | `test_omission_recovery.py` | errore di import; mutazione del collegamento: 4 falliti, ripristinato 9 passati |
| `d537e4a` | Condizione del recupero sulla stessa clausola | 1 in `test_segment_recovery.py` | 1 fallito |
| `c838339` | Fatto identico a un fatto originale validato | 2 in `test_segment_recovery.py` | 2 falliti |

- **Rollback** in un worktree di prova, per ogni commit:
  - `revert --no-commit`;
  - albero uguale al genitore: sì per tutti e 5;
  - test nuovi sul revert e test del genitore passati;
  - abort.
- **Nota su `c838339`:** sul genitore il test del fatto respinto fallisce per il parametro nuovo.
  Il comportamento che verifica valeva già in `d537e4a`, che non deduplicava. Il caso nasce da una
  versione intermedia mai committata, scoperta dal replay (`regressione-2`, segmento 2: 2 valori
  recuperati, 1 con quella versione). Registro in `rollback.txt`.
- **Test esistenti cambiati perché il comportamento cambia di proposito:**
  - le fixture di `test_hold_resolution.py` girano sul profilo `sezioni-2026-10-30`;
  - due test sul profilo ordinario (`test_9` della ripresa e la sessione del profilo) usano ora
    una sospensione contraddetta da SOURCE, che resta bloccata, invece di un dubbio non
    verificabile, che il riesame rilascia;
  - i loro invarianti sono invariati.
- **Suite backend** su `c838339`: 4.284 passati, 8 saltati; Ruff PASS. Era 4.255 alla partenza.

## Prove offline

**Riesame sulle sospensioni finali registrate** (run `definitivo`, `verifica4dd1087` e
`strutturale`):

| Esito | Posizioni | Confronto col gold |
|---|---|---|
| Rilasciate | 45 | 31 uguali; 6 varianti di forma; 8 diverse (7 volte `p14.s0`, la carica letterale della SOURCE più ampia del gold, e 1 data in un altro formato) |
| Domanda di verifica (applicabilità senza condizione) | 6 | 5 Catanzaro, 1 compilazione |
| Scelta USER (caselle) | 3 | checkbox |
| Contraddizioni trovate | 0 | il ramo `evidenza_contraddittoria` è coperto solo dai test |

**Selezione delle omissioni.** Sui run di riferimento: 19 destinazioni selezionate, 19 valori
mancanti, nessuna posizione fuori dal gold. Le spiegazioni respinte sono state escluse dopo
averle misurate:
- Minervino 256 posizioni, di cui 6 valori mancanti;
- Catanzaro 198 e Trapani 27, nessun valore mancante.

Rimandarle tutte al modello sarebbe stato un riempimento indiscriminato.

**Fusione dei recuperi:**
- 30 risposte di recupero reali registrate, rieseguite con la fusione finale;
- destinazioni recuperate: 51 registrate, 60 con la fusione finale;
- nessun segmento sotto il risultato registrato;
- i 2 rifiuti residui dell'invariante sono legittimi: il recupero aggiunge una condizione nuova
  che raggiungerebbe `p14.s1`, già accettata.

## Risultati reali prima e dopo

**Campi corretti per run.** Prima: 31 run della baseline (`94e8726` e `4dd1087`). Dopo: 31 run
del profilo `sezioni-2026-10-30-r2`.

| FORM | Prima | Dopo `c8413ed` | Dopo `d537e4a` | Finale `c838339` |
|---|---|---|---|---|
| Minervino | 24 / 43 / 53 / 59 / 52 / 51 / 56 | 48 / 33 / 46 / 59 / 60 / 60 | 40 / 56 | **58 / 59 / 57** |
| Trapani | 9 / 9 / 9 / 9 / 9 | 9 / 6 / 9 | 9 / 9 / 9 | 9 / 9 |
| Compilazione | 18 / 18 / 18 / 3 | – | – | 18 / 18 / 4 |
| CNR IRISS | 10 / 10 / 10 | 8 / 10 / 10 | – | 1 / 10 |
| Checkbox | 7 / 8 / 7 / 7 / 7 / 8 | 7 / 8 / 7 / 7 | – | – |

**Minervino in dettaglio:**

| Misura | Prima (7 run) | Dopo (11 run) |
|---|---|---|
| Media e deviazione | 48,3 ± 10,9 | 52,4 ± 8,8 |
| Minimo | 24 | 33 |
| Fuori dal blocco soci (37 posizioni) | 19–35, media 27,7 | 25–36, media 33,0 (30–36 senza il pilota) |
| Blocco soci (24 posizioni) | 24 in 6 run, 0 in 1 | 22–24 in 8 run; 0, 8 e 16 in 3 |
| Posizioni corrette in tutti i run | 17 / 61 | 19 / 61 |

Il finale `c838339` ha dato 58 / 59 / 57, ma non va letto come effetto dell'ultima correzione. In
quei tre run il modello ha proposto bene il blocco soci al primo passaggio: un recupero applicato
e uno rifiutato dall'invariante, per un solo valore ciascuno. Tre run non bastano a dichiarare
stabile Minervino.

**Perdite per stadio** (valori gold non scritti, `perdite.py`):

| Minervino | Prima (7 run) | Dopo (11 run) |
|---|---|---|
| Modello: nessuna proposta | 28 | 37 |
| Modello: proposta respinta e non recuperata | 21 | 30 (1 del backend, corretta) |
| USER: rinvio di sospensioni del narratore | 34 | **0** |
| USER: rinvio di condizioni o campi | 3 | 18 (11 nel pilota per la condizione generica di partecipazione) |
| Scritto con un valore diverso dal gold | 3 | 10 (sempre `p14.s0`) |
| Per run | 12,7 | 8,6 |

**Altri FORM:**
- **Trapani:** l'unico calo, `omissioni-2` (6 invece di 9), è una perdita del backend: il
  recupero ripeteva una condizione sulla stessa clausola e l'invariante lo scartava. Corretta da
  `d537e4a`; poi 9 in tutti i 5 run.
- **Compilazione `finale-3` (4/18) e CNR `finale-1` (1/10):** la condizione generica di
  partecipazione, rinviata dalla policy, blocca 18 e 12 campi.
- **CNR `omissioni-1` (8/10):** i 2 campi mancanti dipendono dalla condizione «Domicilio eletto»,
  rinviata dalla policy. Lì la partecipazione era stata confermata.
- **Nessun JSON malformato** negli 86 segmenti dei giri nuovi: il ritentativo di formato non è
  stato esercitato dal vero, e la sua correttezza poggia sui test.
- **Il recupero delle omissioni è scattato una volta** (Minervino `finale-1`, `p16.s0`). Il
  modello ha ripetuto «unassessed» con un motivo specifico: l'email non ha un'etichetta propria
  distinta dalla P.E.C. Nessun valore inventato, l'omissione resta.

**Sicurezza (31 run nuovi):**
- 0 dichiarazioni autorizzate e 0 caselle errate o cambiate fuori report;
- 0 sospensioni silenziose e 0 rifiuti della guardia;
- 0 errori HTTP;
- DOCX uguale al report in ogni run.

**Costo stimato** (tariffe DeepSeek note, fatturazione non verificata):

| Giro | Run | Chiamate | Token | USD |
|---|---|---|---|---|
| `pilota` | 2 | 25 | 634.289 | 0,0735 |
| `omissioni` | 14 | 181 | 4.046.857 | 0,4466 |
| `regressione` | 5 | 75 | 1.843.211 | 0,2012 |
| `finale` | 10 | 139 | 2.750.856 | 0,3322 |
| **Totale** | **31** | **420** | **9.275.213** | **1,0535** |

**Costo per run Minervino:**
- prima 17–19 chiamate e 0,059–0,064 USD;
- dopo 18–22 chiamate e 0,055–0,079 USD;
- in media circa 2 chiamate e 0,008 USD in più, per i recuperi e le domande di riesame.

## Che cosa dipende ancora dall'LLM

Tre comportamenti del modello spiegano tutta la variabilità residua osservata. Nessuno è
correggibile dal backend senza inventare valori o indebolire conferme e invarianti.

1. **Prima risposta sul blocco dei soci di Minervino** (p43–p49, 24 posizioni). Nella stessa
   richiesta il modello:
   - propone tutto (8 run su 11);
   - dichiara «condition_unknown» per l'ordine degli slot con una spiegazione che il
     validatore respinge (`omissioni-1`, 24 posizioni);
   - lega i soci a un ruolo che il validatore respinge e il recupero non corregge (16 su 17 in
     `regressione-1`);
   - dichiara «source_not_found» (`omissioni-2`, 8 posizioni).

   La regola sull'ordine degli slot arriva solo nella richiesta di recupero, e solo per le
   destinazioni «unassessed»; le spiegazioni respinte sono escluse dalla selezione perché, in
   generale, sono vuoti giustificati (6 valori mancanti su 256 posizioni Minervino).
2. **Condizione generica di partecipazione.** In 3 run su 31 nuovi (e già sul codice
   precedente) il modello ancora una condizione «il partecipante è l'operatore economico del
   profilo?» a un'istruzione generale o al titolo del FORM e ci appende un blocco intero. La
   policy congelata la rinvia; un utente reale risponderebbe. Il backend non può confermarla da
   solo senza indebolire le conferme esplicite.
3. **Condizione nuova nel recupero.** Per `p15.s1` (provincia della sede) il modello, nel
   recupero, introduce una condizione ancorata al paragrafo di `p14.s1`, già accettata.
   L'invariante rifiuta il recupero e costa 1 valore per occorrenza (3 occorrenze registrate).

## Limiti residui

- **Il riesame non ragiona sulle date.** `p14.s0` è stato rilasciato in 10 run perché la SOURCE
  documenta la carica e nessun passo dello stesso soggetto la dice cessata. Il dubbio del
  narratore riguardava la decorrenza (dal 2 ottobre 2026) e la SOURCE lo risolve: Luca Ferri
  cessa il 1° ottobre. Una carica con decorrenza futura verrebbe però rilasciata, a meno che il
  testo non contenga le formule riconosciute («cessata», «non più», «scaduta», «revocata»…).
  In tutti i dati registrati non è mai successo. Il valore rilasciato passa comunque dai gate
  ordinari e la bozza lo elenca «da rivedere».
- **Il ramo «evidenza contraddittoria» non è mai scattato dal vero.** È coperto dai test e dal
  replay, che non ha trovato contraddizioni nelle sospensioni registrate.
- **Il ritentativo di formato non è stato esercitato dal vero** in questi giri (0 JSON malformati
  su 86 segmenti nuovi; prima 7 su 406).
- **`p14.s0` resta errato rispetto al gold.** Decidere se il gold accetta la carica letterale
  della SOURCE o se il FORM chiede solo la rappresentanza è una scelta di benchmark, non del
  compilatore.
- **Campione contenuto.** 11 run Minervino e 2–5 per gli altri FORM bastano a separare le cause,
  non a stimare frequenze sotto il 10%.

## Evidenze

Cartella `backend/data/compilation-audit/omissioni-20261030/` (ignorata da Git, non pubblicata):
- `BASELINE.json`;
- `esecuzioni/<FORM>-<giro>-<n>/`: report, bozza, valutazione, turni, chiamate e runtime;
- `AGGREGATO-*.json`, `VERIFICA-*.json`, `PERDITE-*.json`, `CONFRONTO-*.json`;
- `suite-*.txt`, `rollback.txt`, `giro-*.log`;
- `analisi/`, con le riesecuzioni offline:
  - `riesame_offline.py`, `omissioni_offline.py`, `fusione_offline.py`;
  - `perdite.py`, `condizioni_ampie.py`.

I worktree di esecuzione (`tesi-omissioni-c8413ed`, `-d537e4a`, `-c838339`) restano a codice
fisso.
