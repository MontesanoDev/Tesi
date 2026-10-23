# Valutazione finale del candidato (22 ottobre 2026)

Rapporto sperimentale conclusivo. **Candidato non adottato**, V12 resta la baseline congelata.
Nessun commit, tag o push.
- **Criteri applicati senza modifiche:** `docs/criteri-conclusione-2026-10-21.md` (SHA256 `f3ec66be…`).
- **Preregistrazione:** `PREREG-VALUTAZIONE-FINALE.md` (SHA256 nel protocollo, congelata alle
  10:53:06 UTC, prima delle inferenze).
- **Dati:** `benchmark ufficiale/valutazione-finale-20261022-01/`; grezzo in
  `backend/data/compilation-audit/valutazione-finale-20261022-01/`.

## Esito in breve

| Criterio (soglia v1) | Esito | Note |
|---|---|---|
| DOCX ≥ 4/5 per modulo e ≥ 90% sul totale | **Raggiunto** | 32/35 (91,4%); ogni modulo almeno 4/5 |
| Copertura: mediana ≥ 70% del nucleo per modulo | **Non raggiunto** | 5 moduli su 7; Catanzaro 32%, So.Re.Sa. 47% |
| Sicurezza: zero scritture non dimostrate nella revisione **indipendente** | **Non verificabile** | revisione indipendente non disponibile; revisione autoriale: 0 su 423 scritture |
| Dialogo: nessuna conferma ridondante | **Non raggiunto** | 19 conferme ridondanti in 11 prove su 35 |
| Vuoti: ogni vuoto pertinente con motivo tracciato | **Non raggiunto** | 352/354; 2 vuoti senza motivo specifico in CRAA |
| Generalizzazione: modulo nuovo e SOURCE in formato diverso | **Eseguita**, sotto soglia | So.Re.Sa.: DOCX 5/5, copertura 47% |
| Avviso di visibilità | 0 warning | 32 PDF resi con il renderer V12 congelato |

Giudizio: il candidato **non soddisfa tutte le soglie congelate** e non si può dichiarare la
promessa del sistema mantenuta.
- **Mantenuto:** produce normalmente una bozza DOCX, chiede le decisioni, nella revisione
  dell'autore non inventa dichiarazioni e lascia vuoto con un motivo quasi sempre tracciato.
- **Non raggiunto:** compilare una parte sostanziale dei dati documentati su tutti i moduli
  compatibili (Catanzaro e So.Re.Sa.), e un dialogo senza conferme ridondanti.

## 1. Profilo, protocollo e preparazione

- **Profilo candidato:** V14 + K3, dialogo P3 corretto attivato esplicitamente
  (`MAPI_DIALOGUE_REVISION=1`), generazione monolitica, sezioni disattivate.
- **App live ordinaria:** invariata, profilo V14 + K3 e dialogo P3 spento (verificato prima e dopo).
- **Riproducibilità:**
  - flag delle nuove sessioni identici al profilo;
  - richieste globali deterministiche (costruite due volte) e, per i quattro moduli in comune,
    identiche a quelle della verifica del narratore;
  - suite backend 3.509 PASS e Ruff PASS prima delle prove;
  - hash di 127 file applicativi controllati a ogni chiamata, codice invariato per tutta la
    campagna.
- **Due runtime privati clonati dal seme V12**, per SOURCE diverse:
  - storico (22 frammenti, identici alle campagne precedenti);
  - nuova SOURCE: i tre documenti aziendali globali sostituiti da una scheda tabellare
    DOCX→PDF, che consolida gli stessi 104 valori senza aggiunte ed è costruita prima di
    estrarre il modulo nuovo.
- **Tentativi:** 35, cioè 5 per modulo, indipendenti, nessuna sostituzione; politica USER
  deterministica congelata; budget 6 milioni di token (usati 4,15).
- **Eventi:**
  - il primo lancio del driver è fallito prima di qualunque tentativo (nessun marcatore, nessuna
    chiamata) ed è stato rilanciato (`EVENTI-CAMPAGNA.md`);
  - dopo il congelamento è stato corretto un errore dello script di analisi: le voci descrittive
    di Cesano erano trattate come posizioni (`ANALISI-CORREZIONI.md`), senza cambiare
    definizioni né soglie.

## 2. Moduli e compatibilità

Sei moduli storici, tutti quelli con scenario e riferimento congelati, più un modulo nuovo mai
studiato estratto con seme fisso dal pool dei bandi casuali.

Per il modulo nuovo:
- **Esclusioni a priori:** i moduli già studiati e i due modelli per professionista singolo,
  incompatibili con lo scenario societario.
- **Cannara**, primo estratto, **è fuori ambito**: 0 delle 27 destinazioni del nucleo sono
  riconosciute dal parser, perché gli spazi sono tabulazioni. Per i criteri non conta come
  fallimento.
- **So.Re.Sa. 2023**, il successivo, è compatibile.

Tutti i sette moduli valutati soddisfano le condizioni 1-4. I riferimenti v3 sono conformi ai
criteri:
- **Storici:** derivati meccanicamente dai riferimenti congelati, con valori invariati.
- **CRAA:** il denominatore scende da 10 a 8, perché le due celle CCIAA richiedono
  un'autorizzazione rinviata nella variante «ramo».
- **So.Re.Sa.:** nucleo autoriale di 15 destinazioni, scritto prima delle inferenze.

## 3. Risultati per modulo

| Modulo | DOCX | Copertura per tentativo esportato | Mediana | Fallimenti | Conferme ridondanti | Vuoti con motivo | Token |
|---|---|---|---:|---|---:|---|---:|
| Minervino (267 pos.) | 4/5 | 43, 67, 92, 95% | **79%** | 1 EXPORT (409) | 11 | 78/78 | 1,04 M |
| Cesano (88) | 4/5 | 100, 75, 100, 100% | **100%** | 1 MODEL (JSON) | 0 | 1/1 | 0,48 M |
| CRAA (51) | 5/5 | 100% ×5 | **100%** | — | 0 | 68/70 | 0,49 M |
| Catanzaro (307) | 4/5 | 19, 29, 42, 35% | **32%** | 1 MODEL (JSON) | 1 | 97/97 | 0,73 M |
| Bella (67) | 5/5 | 75, 88, 100, 38, 88% | **88%** | — | 3 | 14/14 | 0,45 M |
| Trapani (115) | 5/5 | 94, 47, 94, 88, 94% | **94%** | — | 1 | 50/50 | 0,51 M |
| **So.Re.Sa. (nuovo)** | 5/5 | 40, 47, 47, 47, 47% | **47%** | — | 3 | 44/44 | 0,45 M |

Copertura primaria: valore uguale, equivalente o più completo, per soggetto e proprietà. Le
corrispondenze parziali non contano: per Trapani, includendole, la mediana sale al 100%.

Motivi dei vuoti del nucleo nei moduli sotto soglia:
- **Catanzaro:**
  - spiegazioni del modello di non compilazione (30, di cui 13 anche con un gate);
  - sospensioni del narratore (15);
  - proposte respinte dal backend (21);
  - spiegazioni respinte (11).
- **So.Re.Sa.:** in tutti e 5 i tentativi il backend ha respinto il binding di ruolo del
  sottoscrittore con «Ruolo richiesto assente nell'estratto FORM».
  - Il modulo chiede solo «in qualità di ___» e non nomina il ruolo, quindi restano vuoti i 7
    dati personali di Leonardo Montemurro.
  - È un limite della grammatica FORM, non della SOURCE tabellare: i dati dell'operatore estratti
    dal nuovo PDF (via, PEC, telefono, CF, P.IVA) sono stati scritti correttamente in tutte le prove.
- **Minervino:** proposte respinte (41) e sospensioni del narratore (18). La revisione dei motivi
  delle sospensioni (sezione 5 della verifica del narratore) resta il primo margine di copertura.

## 4. Sicurezza e revisione

- **Revisione indipendente:** non disponibile. Nessun revisore esterno allo sviluppo era
  designato e la revisione **non** viene presentata come indipendente. Il criterio di sicurezza
  resta quindi non verificabile nella forma richiesta.
  - Per un revisore futuro è pronto un pacchetto cieco: 124 scritture distinte con FORM, SOURCE
    citate e scenario, senza valori attesi (`REVISIONE-CIECA/`).
- **Revisione automatica e autoriale** delle 423 scritture (testi e caselle) nei 32 DOCX:
  - 408 uguali o equivalenti al riferimento v3;
  - 3 caselle attese da scelte USER;
  - 12 occorrenze (5 valori distinti) giudicate dall'autore (`REVISIONE-AUTORIALE.json`):
    nessuna non dimostrata.
    - Due valori incompleti o parziali: So.Re.Sa., denominazione senza sede; Trapani, «Amedeo»
      sotto «via/piazza».
    - Le caselle Bella `p65` seguono una ricevuta USER esplicita sul gruppo; la risposta è della
      politica simulata, su una domanda legata alla designazione dei tecnici.
- **V14:**
  - CRAA: CCIAA vuote 5/5 con autorizzazione rinviata;
  - Cesano: `p19.ft0` scritto 4/4, solo con autorizzazione accettata;
  - nessuna scrittura in regione d'opzione senza autorizzazione.
- **K3:** nessun blocco attivato nei dati di questa campagna.

## 5. Condizioni, decisioni USER e dialogo

- **Sintesi del narratore respinte:** 0 su 35 tentativi. **Interventi della guardia sui cicli:** 2
  (minervino-3, minervino-5). **Domande identiche per tre turni:** 0.
- **Richieste di autorizzazione delle dichiarazioni:** 14 (CRAA 5, Trapani 5, Cesano 4). Sono
  lecite e conteggiate a parte.
- **Conferme ridondanti:** 19, cioè richieste di riconfermare il firmatario, la partecipazione
  societaria in forma singola o la voce «Società di Ingegneria», già dichiarati nel primo messaggio.
  - Distribuzione: Minervino 11, Bella 3, So.Re.Sa. 3, Catanzaro 1, Trapani 1.
  - Regole: partecipazione 9, firmatario 5, nome nella posizione del sottoscrittore 3, voce
    società di ingegneria 2.
  - Restano il principale scostamento dal criterio del dialogo. Come deciso, non sono state
    inseguite con modifiche al narratore.
- **Decisioni USER attese su caselle** (riferimenti): scritte in 3 casi su 25.
  - Minervino `p39.cb0`: 3 su 4.
  - Cesano `p19.cb0`, Catanzaro (3 caselle) e Bella `p30.cb0`: mai.
  - Le domande di scelta non sono state poste entro i turni disponibili, oppure sono state
    rinviate. Non è una scrittura indebita, ma è una decisione non acquisita.

## 6. Fallimenti, separati per livello

| Livello | Tentativi | Causa |
|---|---:|---|
| MODEL | 2 | JSON non valido nella chiamata globale: cesano-4 (testo in più dopo l'oggetto), catanzaro-4 (carattere di controllo in una stringa). Analisi rifiutata, nessun valore scritto. |
| NARRATORE | 0 | — |
| BACKEND | 0 | — |
| EXPORT | 1 | minervino-1: export rifiutato (HTTP 409, «Una SOURCE o una condizione è cambiata»). Vedi sotto. |
| DRIVER | 0 | — |

Causa di minervino-1, ricostruita offline:
1. la risposta della politica alla domanda sui dati anagrafici del sottoscrittore («Il firmatario
   scelto per questa domanda è Leonardo Montemurro.») è stata registrata dal pianificatore come
   SKIP;
2. la ricevuta SKIP annulla la selezione del firmatario, ma l'audit derivato, che conteneva già il
   riuso dei suoi dati, non è stato ricalcolato;
3. all'export il ricalcolo ha prodotto campi diversi e il controllo di coerenza ha rifiutato.

Il fallimento è sicuro, ma è un difetto del candidato: un riallineamento mancante dopo una ricevuta
SKIP. Non è stato corretto durante la campagna.

Nessun troncamento della chiamata globale in questa campagna. Su 35 chiamate la quota massima del
limite è stata del 97% (minervino-4) e 6 chiamate hanno superato il 79%: il rischio noto resta.

## 7. Token, costi e latenza

- **Token:** 4.148.151 in totale (0,45-1,04 milioni per modulo).
- **Costo stimato a tariffa:** 0,92 USD, interamente fuori dalle ore di punta (`pricing.json`;
  stima, non fattura).
- **Latenza mediana per tentativo:** 125 s, da 93 s (CRAA) a 183 s (Minervino).
- **Quota mediana del limite della chiamata globale:** 81% per Minervino, 77% per Catanzaro, 37-53%
  per gli altri moduli.

## 8. Confronto prudente con le campagne precedenti

Stessi riferimenti v3 e stessa regola di equivalenza, applicati ai report delle campagne precedenti
(`CONFRONTO-PRECEDENTI.json`). Profili, scenari, varianti e numero di tentativi differiscono: è un
confronto descrittivo, non un test.

| Modulo | V13 coorte 2 (V12+S1, 2 varianti) | P3 (A+B) | Narratore | Valutazione finale |
|---|---|---|---|---|
| Minervino | 4/10 DOCX, 93% | 1/4, 30% | 1/2, 87% | **4/5, 79%** |
| Cesano | 9/10, 100% | 4/4, 100% | 2/2, 100% | 4/5, 100% |
| CRAA | 10/10, 100% | 4/4, 100% | 2/2, 100% | 5/5, 100% |
| Catanzaro | 5/5, 48% | 3/4, 45% | 2/2, 34% | 4/5, 32% |
| Bella | 5/5, 88% | — | — | 5/5, 88% |
| Trapani | 5/5, 94% | — | — | 5/5, 94% |

- **Esportazione:** su Minervino è molto più affidabile della coorte V13-2 (4/5 contro 4/10).
- **Copertura:** stabile su Bella, Cesano, CRAA e Trapani; più bassa su Catanzaro e su Minervino,
  dove le sospensioni del narratore (P3) tolgono valori che V13 scriveva.
- **Conferme ridondanti:** nella coorte V13-2 non erano misurate con la stessa politica.
- **Precedenti di questi moduli:** la baseline V12 aveva un tentativo per modulo; V14 e P3 erano
  campagne brevi di verifica.

## 9. Limiti

- **Revisione** autoriale, non indipendente.
- **Dati:** SOURCE sintetiche di un'unica azienda fittizia; scenari e politica USER simulati e
  deterministici; un solo modello (deepseek-flash) e una sola configurazione.
- **Copertura:** 5 tentativi per modulo e un solo modulo nuovo, con effetti di modulo e di SOURCE
  non separabili. I valori non sono un'accuratezza universale.
- **Riferimenti:** riferimenti storici d'autore; So.Re.Sa. ha un nucleo autoriale senza secondo
  revisore.
- **Politica USER:** risponde a domande di scelta legate a designazioni (Bella), mentre un utente
  reale potrebbe rinviarle.
- **Fuori ambito:** Cannara mostra un limite del parser (spazi resi con tabulazioni) che riguarda
  una parte dei moduli reali.

## 10. Giudizio sulle soglie congelate

Le soglie v1 restano invariate e vengono riportate così:
1. **Affidabilità dell'export:** raggiunta.
2. **Copertura:** raggiunta su 5 moduli su 7.
3. **Sicurezza:** non verificabile in forma indipendente; nessuna scrittura non dimostrata nella
   revisione autoriale.
4. **Dialogo e vuoti:** non raggiunti, per poco nei vuoti (2 su 354) e in modo netto nelle conferme
   ridondanti.

Come previsto dai criteri, i limiti vengono documentati e non comportano un obbligo di sviluppo.
Il candidato non è adottato; la scelta resta all'utente.

Possibili passi, solo su decisione dell'utente:
1. una revisione indipendente con il pacchetto cieco, l'unico modo per chiudere il criterio di
   sicurezza;
2. il riallineamento dell'audit dopo una ricevuta SKIP che annulla un riuso;
3. il binding di ruolo quando il FORM chiede solo «in qualità di»;
4. le conferme ridondanti del dialogo.
