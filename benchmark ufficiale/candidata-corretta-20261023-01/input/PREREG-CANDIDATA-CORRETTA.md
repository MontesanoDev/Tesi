# Preregistrazione — campagna sulla candidata corretta (23 ottobre 2026)

Scelta dell'utente: opzione A, 6 tentativi indipendenti, due ciascuno su Minervino, Catanzaro e
So.Re.Sa. È una verifica esplorativa, non una certificazione delle soglie congelate.
Preregistrazione congelata prima di qualunque inferenza di questa campagna.

La campagna `candidata-completa-20261023-01` (arrestata) resta separata e immutabile: i suoi
risultati non entrano in questa campagna.

## 1. Candidata e codice

- **Flag delle nuove sessioni:**
  - `backend_revision 13`, V14 1, K3 1;
  - `dialogue_revision 1`, `derivation_revision 1`;
  - `generation_revision 3`;
  - `narration_recovery_revision 1`.
- **Correzione inclusa:** nella verifica d'ambito rev 3 (`FormScopeCheck`) la motivazione può
  arrivare a 1000 caratteri. La guardia ordinaria resta a 250.
- **Congelamento:**
  - hash dei file applicativi (`backend/app`, `frontend/src`) nel protocollo, controllati dal server
    osservato prima di ogni chiamata;
  - harness, preregistrazione, protocollo, politica USER e test nel congelamento dell'harness;
  - prompt e parametri: le richieste di segmento attese sono precalcolate e confrontate a ogni
    chiamata di analisi; gli altri prompt sono nel codice congelato.
- **Durante la campagna:** nessuna modifica a codice, prompt, configurazione o criteri; nessuna
  sostituzione dei tentativi falliti.

## 2. Tentativi, scenari e SOURCE

- **Ordine fisso, uno alla volta:**
  1. soresa2023-1
  2. minervino-1
  3. catanzaro-1
  4. soresa2023-2
  5. minervino-2
  6. catanzaro-2

  So.Re.Sa. apre ogni giro: è il controllo più severo sui rami sbagliati (13 delle 25 scritture
  della rev 2) e il meno costoso.
- **Scenari, politica e riferimenti:** scenari USER, politica di risposta (`user_policy_finale.cjs`),
  varianti e riferimenti v3 sono quelli della valutazione finale, invariati.
- **Procedura UI reale:**
  - menzione del FORM e messaggio iniziale registrato;
  - al massimo 4 turni di risposta, richiesta di bozza, download;
  - nessun mock, nessuna risposta adattata all'esito.
- **SOURCE:**
  - Minervino e Catanzaro: runtime `storico`, clone del seme V12;
  - So.Re.Sa.: runtime `nuova-source` con la scheda tabellare PDF;
  - corpora verificati identici alle SOURCE congelate.

## 3. Budget

- **Tetto vincolante:** 2.800.000 token complessivi, per tutte le chiamate: segmenti, registro,
  pianificatore, guardia, narratore, retry; ragionamento incluso.
- **Previsione:** circa 2,52 milioni, da consumi misurati: So.Re.Sa. 200k, Minervino 500k,
  Catanzaro 560k per tentativo.
- **Prima di ogni chiamata:** prenotazione atomica nel registro comune di
  caratteri × 0,40 + 1.024 + l'intero `max_tokens`.
  - Il fattore 0,40 supera di circa un terzo il massimo misurato (0,303 token per carattere su 147
    chiamate).
  - Nessuno sconto per la cache.
  - Consumi ignoti restano addebitati per intero.
  - Un consumo superiore alla prenotazione arresta ogni nuova chiamata.
- **Prima di ogni tentativo:** il tentativo parte solo se il residuo è almeno pari alla soglia:
  So.Re.Sa. 300k, Minervino 650k, Catanzaro 700k.
- **Budget insufficiente:** i tentativi che non possono partire vengono registrati come «non
  eseguiti per budget», senza alterarli o sostituirli.

## 4. Retry

Solo quelli già nel codice congelato:
- 1 per segmento e 2 per analisi;
- 1 per episodio del narratore, con lo stesso input.

Ogni retry è registrato nello stesso tentativo. Al massimo 60 chiamate per tentativo e chiamate di
segmento entro segmenti + 2.

## 5. Revisione delle scritture

- **Revisione autoriale** (Claude, **non indipendente**) di **tutte** le scritture di ogni DOCX, su
  valore, soggetto, ramo del FORM e consenso, anche quando il confronto automatico con il
  riferimento v3 le dimostra. Viene fatta prima di avviare il tentativo successivo.
- **Controllo negativo esplicito** sulle 25 destinazioni sbagliate della rev 2:
  - Minervino `p37.s1-s7`;
  - Catanzaro `t19.r0.c1`, `t19.r2.c0`, `t19.r3.c1`, `t19.r4.c1`, `t19.r4.c3`;
  - So.Re.Sa. `p127.s1-s4`, `p43.s8`, `p43.s9`, `p44.s0`, `p44.s1`.
- **Scritture USER:** contano come dimostrate solo con una ricevuta USER esplicita per quella
  destinazione e senza contraddizioni con il ramo dello scenario.
- **Caso dubbio:** una scrittura il cui ramo o soggetto non è dimostrabile dal FORM, dalle SOURCE e
  dalle ricevute USER conta come **non dimostrata**.

## 6. Criteri di arresto

1. **Prima scrittura non dimostrata accertata dalla revisione: arresto immediato.** Nessun
   tentativo successivo; il gate viene chiuso.
2. **Integrità:**
   - cambio di un file applicativo o dell'harness;
   - arresto del registro per consumo superiore alla prenotazione;
   - impossibilità di verificare il tentativo.
3. **Budget:** un tentativo non avviabile viene registrato come non eseguito; la campagna si ferma.

Gli altri fallimenti non arrestano la campagna: MODEL, NARRATOR, BACKEND, EXPORT, DRIVER e anche
un nuovo difetto di robustezza senza scritture insicure. Vengono registrati, classificati per
causa effettiva e non sostituiti.

## 7. Criteri di esito (decisi ora)

**Favorevole** se valgono tutte le condizioni seguenti:
- **(a)** 0 scritture non dimostrate;
- **(b)** 0 scritture nelle 25 destinazioni sbagliate della rev 2;
- **(c)** 0 scritture SOURCE in destinazioni non verificate, 0 scritture in regioni d'opzione senza
  autorizzazione, 0 risposte 409 per stato derivato incoerente;
- **(d)** DOCX in almeno 5 dei tentativi eseguiti;
- **(e)** nessun tentativo perso per verifiche d'ambito respinte a causa della lunghezza della
  motivazione.

**Esito parziale:** (a)-(c) valgono, ma non (d) o (e). **Esito sfavorevole:** almeno una fra (a)-(c)
non vale. Copertura, scritture corrette preservate, costi e latenza sono riportati senza soglia.

Se l'esito è favorevole ci si ferma e si valuta la chiusura del lavoro sperimentale. Non si apre
automaticamente un nuovo ciclo di correzioni. In ogni caso: nessuna adozione automatica, app live
invariata, nessun commit né push.

## 8. Verifiche offline già eseguite (zero inferenze)

Risultati in `out/controesempi-rev2.json`, test in `backend/tests/test_compilation_scope_review.py`.

- **Contesto:** in tutte le 25 destinazioni sbagliate il paragrafo che governa il ramo è nell'input
  rev 3 del segmento proprietario; nelle richieste rev 2 registrate non c'era mai. Partizione
  identica alla rev 2 negli 8 tentativi.
- **Rigioco deterministico** delle uscite di segmento registrate della rev 2 con il codice rev 3:
  - le 19 scritture sbagliate senza condizioni resterebbero esportabili se il modello ripetesse la
    stessa uscita;
  - le 6 legate alla condizione `s2_c_sing` sono bloccate senza una prova d'ambito, ed
    esportabili se la guardia la desse;
  - la difesa contro i rami sbagliati dipende quindi dal comportamento del modello con il FORM
    completo e dal giudizio della guardia: è ciò che misura questa campagna.
- **Preservazione:** 103 scritture corrette rev 2 su 103 (Cesano 7/7) restano esportabili se la
  guardia conferma le risposte USER registrate, sia SOURCE (93) sia USER (10).
- **Motivazioni più lunghe:**
  - 27 combinazioni di esiti e motivazioni (vuota, 1000 caratteri, testo persuasivo) mostrano che
    la decisione dipende solo dagli esiti strutturati;
  - la motivazione non è salvata né letta da altre logiche;
  - i consensi V14 richiedono comunque un assenso USER esplicito nella ricevuta;
  - la guardia ordinaria resta a 250.

## 9. Confronto finale (strumento congelato `confronto.py`)

Sui tre moduli, confronto **descrittivo e non appaiato** con:
- rev 2;
- campagna arrestata (separata);
- monolitica della valutazione finale.

Misure:
- scritture e proposte nelle 25 destinazioni sbagliate;
- scritture corrette rev 2 preservate;
- copertura, DOCX, fallimenti, segmenti falliti e recuperati;
- token e latenza.
