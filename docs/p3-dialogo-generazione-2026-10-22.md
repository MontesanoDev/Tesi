# P3 — Dialogo e generazione per sezioni — 21-22 ottobre 2026

Candidata tecnica: V13 + V14 + K3 + P3. **La V12 resta la baseline adottata**; P3 non è
adottata. Nessun commit o push. Diagnosi, preregistrazione, script e replay in
`backend/data/compilation-audit/p3-20261021-01/`. Campagna E2E in
`benchmark ufficiale/p3-verifica-20261022-01/` (grezzo in
`backend/data/compilation-audit/p3-verifica-20261022-01/`).

## 1. Cause iniziali dimostrate

Gli 11 tentativi senza DOCX di V13 (90 prove) hanno quattro componenti diverse:

| Fallimento | Prove | Causa |
|---|---|---|
| Analisi globale troncata | minervino-08, -09 (coorte 1), -05, -06 (coorte 2) | Il ragionamento consuma il 69–76% dei 49.152 token di output. A Minervino l'output totale ha mediana 44,4k token, il 90% del limite, anche quando non tronca. |
| JSON non valido | catanzaro-04 | Tabulazioni letterali copiate dal FORM: con `strict=False` il JSON è valido e completo. |
| JSON non valido | cesano-07, -08 | Annidamento incompleto con `finish: stop` (1 e 10 oggetti aperti) in un oggetto unico di 20–24k caratteri. A Cesano la copertura contabile pesa il 74% del JSON. |
| Narratore troncato | minervino-07, -09, -10 | Oltre 20 sospensioni scritte una per una, con lo stesso motivo. |
| Dialogo bloccato | minervino-02 (coorte 2) | La condizione «amministratore unico» (al turno 3 di una persona cessata) non è la risposta «legale rappresentante». La guardia rifiuta correttamente, ma il narratore ripete la domanda identica per tre turni. |

Altre cause dimostrate:
- **Filtro lessicale « o ».** Dei 102 turni con risposta respinta, 92 avevano la guardia
  semantica `SUPPORTED`: in 89 il messaggio conteneva « o », come in «senza raggruppamenti o
  consorzi». Nella coorte 1 questo esaurisce i 4 turni di risposta.
- **Sospensioni ereditate senza condizioni**
  (`held = (old | incoming) - redundant`): il blocco è solo testo, e una sospensione non si
  rilascia quando la condizione riceve risposta. A fine dialogo restano 47 sospensioni in 17
  prove; in cesano-breve (V14) la condizione e l'autorizzazione erano già confermate.
- **Decisioni del primo messaggio richieste di nuovo**, spesso con formulazioni diverse:
  101 domande del primo turno in 68 prove (misura lessicale e approssimata).
- **Condizioni mai chieste**: 402 proposte grounded su 1.454 restano dietro condizioni senza
  risposta. In 23 prove è l'esaurimento dei turni; in craa-autorizza il narratore restituisce
  `questions: []` con la condizione di ramo CCIAA ancora aperta.

Ipotesi, non dimostrata: senza la data corrente il modello tratta come «futura» una carica
iniziata il 2 ottobre 2026.

## 2. Interventi implementati

Valgono solo per le nuove sessioni. Le sessioni precedenti (V12, V13, V14, K3) restano
identiche, e ogni modifica ai test esistenti mantiene la variante precedente.

**Generazione (`generation_revision: 1`), `compilation_segments.py`:**
- partizione backend in blocchi contigui: al massimo 60 candidate per segmento e 6
  segmenti; una clausola d'opzione resta con la sua tabella;
- ogni chiamata riceve lo stesso prompt, lo stesso input completo e lo stesso limite di
  output, più un'istruzione di segmento in coda, così il prefisso è condiviso e cacheabile;
- esecuzione: segmento 1, poi gli altri (al massimo 3 alla volta); nessun nuovo tentativo;
- lettura non rigorosa delle stringhe (tabulazioni), senza alcuna riparazione di strutture;
- unione con identificativi `s<i>_`, deduplica, scarto delle proposte fuori segmento, e
  validazione del payload unito con il validatore V12 invariato (poi V13, V14, K3);
- conflitti fra segmenti resi come `review/conflicting` con alternative, mai come scelta;
- segmento fallito: campi vuoti con copertura `UNASSESSED` di origine BACKEND e motivo
  «sezione non analizzata»;
- con un solo segmento la richiesta è identica a quella monolitica.

**Dialogo (`dialogue_revision: 1`):**
- **decisioni del primo messaggio** (`compilation_decision_registry.py`): una piccola
  chiamata propone risposte agli slot di applicabilità aperti, che devono superare la guardia
  semantica esistente e avere un estratto letterale. Diventano ricevute USER
  (`origin: initial_request`), applicate come una risposta e dichiarate nella sintesi. Sono
  escluse autorizzazioni, valori e scelte;
- **alternative**: niente filtro « o » sulle condizioni controllate dalla guardia. Restano il
  veto sulle esitazioni («forse», «non so») e quello sulla disgiunzione del valore stesso; il
  consenso V14 non cambia;
- **sospensioni**: legate alla chiave dello slot che le blocca e rilasciate quando questo
  riceve risposta, **solo** per blocchi `applicability` e `user_decision`. Sono raggruppate
  per motivo, così l'output resta piccolo;
- **domande**: se il narratore non chiede nulla, il backend chiede le condizioni aperte;
  dopo due risposte non accettate lo slot diventa `UNKNOWN` (`BACKEND_LOOP_GUARD`);
- data corrente nel contesto del narratore e nell'input globale, come contesto e non come
  SOURCE.

**Deviazione dalla preregistrazione.** Il rilascio delle sospensioni è limitato ai blocchi
risolvibili dall'utente: un dubbio SOURCE non si scioglie con una conferma USER. Decisa
prima della campagna.

## 3. Verifiche deterministiche e offline

- **Proiezione:** i payload V12 registrati, divisi nei segmenti, uniti e validati, danno
  0 differenze su 12.677 candidate (92 payload) in stato, valore, condizioni, copertura e
  binding. Esclusi i 3 JSON non validi. Le prime esecuzioni mostravano differenze dovute a
  oggetti mancanti nella simulazione dei segmenti, non all'unione.
- **Sospensioni:** delle 47 finali registrate, 36 sarebbero rilasciate (14 a Cesano); 9 restano
  perché il dubbio è SOURCE, 2 perché il blocco è aperto.
- **Filtro:** nei 92 turni rifiutati solo dal filtro, tutte le 110 proposte esaminate dalla
  guardia passano le regole nuove. Esitazioni e disgiunzioni del valore restano respinte nei test.
- **Test:** 34 nuovi; tre test esistenti estesi con la variante precedente. Suite backend
  completa 3.479 PASS, Ruff PASS.

## 4. Campagna E2E (22 ottobre 2026, 01:33–02:09 UTC)

Protocollo `PROTOCOLLO-P3.json`, registrato prima dell'inferenza. Condizioni:
- 16 prove: Minervino, Cesano, CRAA e Catanzaro × bracci A e B × 2 ripetizioni;
- politica USER naturale V14, con le varianti appaiate fra i bracci;
- codice congelato, con hash verificati a ogni chiamata, e runtime privato clonato;
- nessuna sostituzione o ripetizione.

**Bracci:**
- **A:** dialogo nuovo + generazione monolitica;
- **B:** dialogo nuovo + sezioni.

Il confronto con V13 e V14 non è appaiato.

| Prova | DOCX | Nucleo corretto* | Secondi | Token |
|---|---|---|---:|---:|
| minervino-A1 / B1 | no / no | — / — | 1135 / 1225 | 136k / 422k |
| minervino-A2 / B2 | sì / no | 18/60 / — | 128 / 1193 | 159k / 446k |
| cesano-A1 / B1 | sì / sì | 4/4 / 4/4 | 133 / 142 | 107k / 153k |
| cesano-A2 / B2 | sì / sì | 4/4 / 3/4 | 146 / 139 | 112k / 150k |
| craa-A1 / B1 (autorizza) | sì / sì | 10/10 / 10/10 | 99 / 105 | 94k / 99k |
| craa-A2 / B2 (ramo) | sì / sì | 8/10 / 8/10 (CCIAA vuote, come devono) | 98 / 98 | 95k / 93k |
| catanzaro-A1 / B1 | sì / sì | 14/31 / 10/31 | 146 / 179 | 144k / 623k |
| catanzaro-A2 / B2 | no / sì | — / 16/31 | 1138 / 245 | 140k / 644k |

\* Date in forma equivalente («14 novembre 1982») contate come corrette. Ogni prova senza DOCX
ha raggiunto il timeout dell'harness, 1.000 s per messaggio.

**DOCX: 12 su 16 (6/8 per braccio).** I quattro tentativi senza DOCX hanno **una sola
causa, introdotta da P3**: il narratore viene respinto dalla validazione backend.
- 3 casi: «Motivo hold senza citazione nel contesto ricevuto»;
- 1 caso: «Esclusioni di proposte non valide»;
- senza sintesi non ci sono domande, la richiesta di export non produce una bozza e la prova
  va in timeout;
- le risposte respinte contengono sospensioni con citazioni non letterali (per esempio «Per il
  direttore tecnico Elisa Romano non sono documentati…»), citazioni da righe SOURCE fuori dal
  contesto di ancoraggio, una citazione unica valida per un solo membro del gruppo, e proposte
  fuori da una finestra di revisione vuota;
- nelle 96 prove storiche con il prompt V14 questo errore non compare mai. La causa sono le
  modifiche P3 al narratore: istruzioni sui gruppi e sulle sospensioni, data, schema raggruppato.

**Generazione (B contro A):**
- 0 analisi troncate in entrambi i bracci (8 chiamate monolitiche, 28 di segmento). Il
  troncamento storico di Minervino, 4 su 22, non è misurabile su due prove per braccio;
- sotto il 50% del limite: **25 chiamate di segmento su 28 (89%; obiettivo di progetto 90%)**
  contro 2 monolitiche su 8;
- output mediano 12,0k token contro 30,2k; ragionamento mediano per chiamata 5–11k
  nei moduli suddivisi, 20–25k in quelli monolitici;
- 2 segmenti su 28 con JSON non valido (Catanzaro-B1 segmento 1, Minervino-B1 segmento 3):
  gli altri segmenti sono proseguiti e i campi sono rimasti vuoti con motivo «sezione non
  analizzata» (Catanzaro-B1: 8 campi del nucleo). Il resto dell'unione: 1 conflitto reso come
  revisione, 2 proposte fuori segmento scartate;
- costo: **2,63 milioni di token in B contro 0,99 in A (2,7×)**; latenza mediana 161 s contro
  140 s;
- qualità del nucleo dove entrambi i bracci hanno esportato: nessuna differenza dimostrabile
  (CRAA identico, Cesano 4/4 e 3/4 contro 4/4 e 4/4, Catanzaro 10 e 16 contro 14). Minervino non
  è confrontabile.

**Dialogo (entrambi i bracci):**
- decisioni del primo messaggio registrate in 12 prove su 16 (nessuna in CRAA);
- domande ridondanti su decisioni già dichiarate: 10 in totale (A 4, B 6), contro un obiettivo
  di 0 (in V14 erano da 0 a 3 per prova);
- nessuna domanda identica per 3 turni;
- una sola applicazione della guardia sui cicli (minervino-B2);
- 0 sospensioni con blocco risolto non rilasciate;
- **Cesano: `p19.ft0` scritto in 4 prove su 4** (V14: 1 su 2), sempre dopo autorizzazione
  accettata;
- **CRAA «autorizza»: celle CCIAA scritte in 2 prove su 2** con ramo confermato e autorizzazione
  accettata (in V14 la condizione di ramo non veniva mai chiesta). CRAA «ramo»: vuote in 2 su 2;
- una condizione aperta mai chiesta, in minervino-B1, cioè una prova fallita.

**Sicurezza (revisione dell'autore, non indipendente):**
- 0 scritture non dimostrate. Fuori dal riferimento solo date in forma equivalente e le
  caselle di partecipazione di Cesano, scelta USER prevista;
- 0 scritture in regioni d'opzione senza autorizzazione accettata;
- nessun aggiramento di V14 o K3 osservato. Il validatore è invariato: i rifiuti di Cesano
  restano, e il replay lo conferma.

**Budget:** 3,62 milioni di token su 6 milioni preregistrati.

## 5. Giudizio

- **La candidata P3 non è pronta e non va adottata.** Il dialogo nuovo introduce un modo di
  fallimento grave: 4 sessioni su 16 senza DOCX, 3 su 4 a Minervino. Questo fa scattare il
  criterio di arresto «peggiora gravemente».
- **Le parti deterministiche del dialogo funzionano nelle prove riuscite:** rilascio delle
  sospensioni, domande riempite dal backend, niente filtro « o », decisioni del primo
  messaggio, guardia sui cicli. Hanno risolto i limiti V14 di Cesano e CRAA.
- **La generazione per sezioni raggiunge il suo obiettivo di output**: niente troncamenti,
  89% delle chiamate sotto metà del limite. Lo fa però a un costo 2,7 volte maggiore, con un
  7% di segmenti persi per JSON non valido e senza un guadagno di qualità dimostrato su questi
  campioni. Non c'è peggioramento grave dei dati scritti, ma neppure una prova del beneficio
  sulla copertura.
- I 4 rischi residui di P2/K3 restano invariati.

## 6. Prossime attività strettamente necessarie

1. **Correggere il narratore.** Una sospensione non valida (citazione non ancorata, proposta
   fuori finestra) non deve far cadere l'intera sintesi: va registrata come sospensione
   prudente oppure scartata se non riguarda alcuna proposta. La citazione di un gruppo va
   verificata sul contesto di almeno un membro. Verifica offline sulle 4 risposte reali
   respinte, conservate negli artefatti, poi una nuova breve verifica E2E. **Nel frattempo, nel
   working tree le nuove sessioni usano P3**: se l'app live gira sul working tree, conviene
   disattivare `dialogue_revision` in `initial_state` finché la correzione non è verificata.
2. **Decidere sulla generazione per sezioni.** Il guadagno è di affidabilità (troncamenti),
   pagato in token. Su moduli piccoli resta di fatto monolitica. Serve una scelta di prodotto:
   attivarla solo oltre una soglia di dimensione, oppure no.
3. Solo dopo, la valutazione finale secondo i criteri congelati.

## 7. Materiali

- **Diagnosi e preregistrazione:** `backend/data/compilation-audit/p3-20261021-01/`
  (`DIAGNOSI-P3.md`, `PREREG-P3.md` SHA256 `7bf79973…`, script e replay in `out/`).
- **Campagna:** `benchmark ufficiale/p3-verifica-20261022-01/` (`PROTOCOLLO-P3.json`,
  `ANALISI-P3.json`, `RIEPILOGO-P3.json`, prove, codice congelato).
- **Grezzo:** `backend/data/compilation-audit/p3-verifica-20261022-01/` (chiamate al provider,
  tracce browser, stati persistiti).
- **Runtime privato** `.tools/p3-verifica-20261022-01/`: contiene la chiave ed è escluso dal backup.
