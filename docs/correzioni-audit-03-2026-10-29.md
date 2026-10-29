# Correzioni offline dopo l'audit narratore Minervino 03 (28-29 ottobre 2026)

**Ambito:**
- branch `fix/2026-10-28-correzioni-audit-03`, worktree `tesi-correzioni-audit03-20261028`, base
  `00f9bce` (compilatore `7b31d25` e harness `d508b64`);
- nessuna chiamata DeepSeek, nessuna modifica all'app ordinaria, nessun push o merge;
- il tentativo 03 e le sue ricevute SKIP restano invariati.

**Revisione:** autoriale.

## Fix e commit

| # | Commit | Causa (audit 03) | Correzione | Test prima → dopo |
|---|---|---|---|---|
| 1 | `cfdbb06` | La policy USER (revisione 1) leggeva ogni slot come condition, choice o value e applicava la regola sulle date a qualunque elenco di campi: al ramo società rispondeva con il testo sulle date e rinviava l'operatore | Regola scelta in base al tipo reale dello slot, alla citazione FORM e alle destinazioni; le decisioni sono sempre rinviate; i testi delle risposte non cambiano | Revisione 1: 4/17 falliti; revisione 2: 17/17 |
| 1b | `2bdaf45` | Dopo il fix 2a, la condizione del sottoscrittore arriva senza `p12.s0` | Blocco del sottoscrittore: conferma del ruolo se la carica è fra le destinazioni, altrimenti conferma del nome | 1/19 → 19/19 |
| 2a | `f7d35f8` | Una proposta del modello bloccata (binding di ruolo respinto, perché il FORM lascia la carica in bianco) eliminava la domanda «Il sottoscritto» di proprietà del FORM, e con essa la condizione | La proposta resta bloccata e viene registrata; il nome si chiede per primo, anche nel fallback del backend; poi derivazione dalle SOURCE e condizione sulle destinazioni derivate | 3/6 falliti → 6/6 |
| 2a' | `4712c49` | La condizione dell'operatore, chiesta prima del nome, non poteva coprire la carica derivata dopo: il gate di ambito USER la bloccava | Finché il nome è aperto, le condizioni che il blocco erediterà aspettano; un nome rinviato le libera | 1/9 → 9/9 |
| 2b | `f2d7577` | Il binding del direttore tecnico veniva respinto perché la seconda citazione (riga della tabella soci) non contiene il ruolo | Una citazione senza ruolo viene solo registrata; serve almeno un'attestazione letterale; respinti come prima i casi senza attestazione, le citazioni inventate, la General KB e il ruolo assente dal FORM | 2/13 falliti → 13/13 (normale e structural) |
| 3 | `9aa37a9` | Qualunque «non» o «nessun» sostituiva l'intera sintesi iniziale con un testo generico | Si eliminano solo le frasi che negano la presenza (negazione più termine di presenza o fonte); il resto resta letterale, con l'avvertenza; con sole negazioni si usa ancora il testo generico | Funzione nuova → 13/13 |
| 4 | `be5be0f` | Ramo società confermato, ma la casella fuori dallo scope del modello: nessuna derivazione e nessuna domanda | Domanda `choice` del backend sulle opzioni FORM «IN QUALITÀ DI»; spunta solo la scelta USER applicabile | 15/25 falliti → 25/25 |

**Rollback:**
- uno per fix, nei worktree `tesi-rollback-audit03-{policy,firmatario,policy-firmatario,ordine,binding-dt,sintesi,p39}-20261029`;
- ogni revert restituisce l'albero del commit genitore;
- i test del genitore passano (harness 70/70; mirati backend 6-39).

**Suite e controlli:**

| Controllo | Esito |
|---|---|
| Backend | **4.077 PASS**, 0 falliti, in 384 s; con il fix 4 **4.102 PASS** in 446 s |
| Ruff (backend e harness) | PASS |
| Harness `audit_tools` | 89/89 PASS |

Gli 8 test saltati richiedono artefatti storici locali assenti in questo worktree
(`test_compilation_narration_recovery`, `test_compilation_scope_review`): non sono stati
eseguiti.

## Rigioco FORM/SOURCE/USER offline del tentativo 03

**Script:** `backend/data/compilation-audit/correzioni-audit03-20261028/replay03.py`. Riparte dalla
sessione 03 alla versione 3, cioè dopo l'analisi reale, e rideriva l'audit dagli output immutati
del modello.

**Simulati:**
- il testo del narratore (prime 3 domande del pool);
- la codifica del planner;
- il verdetto della guardia (accetta la prova di ambito del backend).

**Reali:** pool, ricevute, derivazioni, validatori, gate di export e writer DOCX.

| Codice | Domande | Scritture | Uguali al replay a 58 | Note |
|---|---:|---:|---:|---|
| Tentativo 03 reale (policy rev. 1) | 7 | 0 | 0 | Tutte SKIP |
| `7b31d25` + policy rev. 2 | 7 | 39 | 37 | Più le 2 date dei soci, corrette rispetto alle SOURCE |
| Più 2a, 1b, 2a' | 9 | 48 | 46 | Sottoscrittore completo, carica compresa |
| Più 2b | 10 | 48 | 46 | `s2_c_dt` torna nel pool; la policy la rinvia (direttore tecnico fuori dallo scenario) |
| Più 3 (messaggio reale del 03) | 10 | 48 | 46 | Sintesi persistita con i dati trovati e l'avvertenza |

**Comportamento del dialogo:** 0 domande ripetute, 0 sospensioni e 0 valori diversi dal
riferimento.

**Scritture (48) rispetto al riferimento (58):** 46 uguali, 0 diverse, 2 fuori dal riferimento.
Le 2 in più sono date di iscrizione SOURCE, coperte dalla ricevuta del ramo società:

| ID | Valore | Riga SOURCE `-54` | Esito |
|---|---|---|---|
| `p46.s1` | 18/05/2015 | Elisa Romano, stesso C.F. di `p45.s2` | Corretta |
| `p49.s3` | 12/06/2014 | Andrea Greco, stesso C.F. di `p48.s1` | Corretta |

Nel riferimento restavano vuote per il difetto di dialogo già documentato: la domanda su
`p46.s1` nominava Andrea Greco ed era stata rinviata, e un hold USER bloccava `p49.s3`. Nel
rigioco nessuna domanda sulle date viene posta.

**Campi del riferimento rimasti vuoti (12 ID univoci, 58 − 46):**

| Causa | ID | N |
|---|---|---:|
| Validatore: la citazione FORM è il solo marcatore | `p15.s1` | 1 |
| Validatore: estratto SOURCE del fatto non presente nella fonte citata | `p43.s0`, `p45.s0`, `p47.s0` | 3 |
| Condizione `s2_c_dt` rinviata dalla policy USER, proposta valida | `p51.s0`, `p52.s0`, `p52.s1`, `p53.s0`, `p53.s2`, `p53.s4` | 6 |
| Sotto `s2_c_dt`, nessuna proposta del modello | `p53.s1` | 1 |
| Casella fuori dallo scope della condizione | `p39.cb0` | 1 |

La versione precedente di questo elenco contava `p53.s1` due volte (fra i 7 campi del direttore
tecnico e come sezione non proposta). Fuori dal riferimento resta vuoto anche `p53.s3` (data del
direttore tecnico, nessuna proposta), vuoto anche nel riferimento.

**Direttore tecnico:** i 6 campi rinviati sono `REVIEW_REQUIRED` senza errori. La ricevuta di
`s2_c_soc` li elenca, ma ciascuno richiede anche `s2_c_dt`, che ha ricevuta SKIP. Nella bozza il
blocco è vuoto: il C.F. `RMNLSI85C47A662Y` e il numero `8421` compaiono una sola volta, nel blocco
del socio. Il rinvio è coerente con la policy: le risposte preregistrate non coprono il direttore
tecnico. Nel riferimento il blocco era scritto perché il modello lo aveva incluso nella sola
condizione del ramo società.

## `p39.cb0`: diagnosi

**Stato della condizione `s2_c_soc`:**
- fondata;
- confermata dall'USER con il controllo semantico;
- `applies_to` comprende la casella.

**Perché la casella resta vuota:** il suo `scope` esplicito, prodotto dal modello, non la include.
La derivazione della rappresentanza (`_representation_receipt`) richiede la casella in quello
scope e non lo estende per regola, quindi la casella resta non spuntata. È una scelta
conservativa, non modificata.

**Verifica di chiusura (offline, in memoria, nessuna scrittura):** con l'output 03 la
derivazione dalla ricevuta di `s2_c_soc` fallisce per quattro motivi indipendenti.
1. La casella manca dallo scope della condizione: c'è solo in `applies_to`.
2. Aggiungendola allo scope, la stessa ricevuta non è più valida, perché la prova di ambito
   cambia. È il comportamento corretto: una ricevuta non si estende.
3. La citazione FORM del modello include «avente la seguente», quindi la clausola non supera il
   confronto esatto.
4. La risposta preregistrata contiene «non autorizza altre dichiarazioni» e il controllo
   lessicale `_uncertain` la tratta come incerta.

Nel riferimento lo scope comprendeva la casella e la risposta non conteneva negazioni.

**Esito:** con questo output del modello serve una domanda esplicita. Nel pool non c'è, perché il
modello non ha dichiarato `choice_groups` e la regione «IN QUALITÀ DI» non ha una domanda propria.
La regione (`_capacity_region`) ha 7 opzioni: `p20.cb0`, `p21.cb0`, `p35.cb0`, `p39.cb0`,
`p54.cb0`, `p61.cb0`, `p64.cb0`.

**Modifica minima proposta** (applicata il 29 ottobre in `be5be0f`, vedi la sezione seguente):
- **Quando:** una condizione di rappresentanza, partecipazione o forma giuridica è accettata e ha la
  sua casella in `applies_to`, ma `_receipt_control` non deriva nulla. Inoltre nessuna opzione della
  regione è già spuntata e nessun gruppo fondato del modello la copre.
- **Cosa:** il pool aggiunge una sola domanda `choice` di proprietà del FORM sulla regione, con le
  etichette FORM delle 7 opzioni.
- **Risposta:** passa da `user_choice`. La ricevuta copre le opzioni mostrate; la casella si spunta
  solo se l'USER la seleziona, e un rinvio lascia la regione vuota.
- **Restano invariati:** `_representation_receipt`, `_uncertain` e le ricevute già rese.

**Test necessari:**
- positivo: con una selezione esplicita diventa vera solo `p39.cb0`;
- negativi: rinvio; risposta ambigua; opzione già spuntata; condizione non accettata; derivazione
  già riuscita, che non deve produrre una domanda duplicata;
- rigioco 03: atteso 49 scritture, 47 uguali al riferimento.

## Fix 4: scelta esplicita «IN QUALITÀ DI» (`be5be0f`)

**Quando:** una condizione di rappresentanza, partecipazione o forma giuridica è accettata
dall'USER e la sua casella FORM sta in `applies_to`, ma la ricevuta non può marcarla.
**Cosa:** il pool aggiunge una sola domanda `choice` sulla regione «IN QUALITÀ DI». Il testo è
del backend ed elenca le opzioni con le etichette FORM; lo stesso testo compare nel fallback
quando il narratore non sceglie domande.

**Controlli mantenuti:**
- **Applicabilità:** si può scegliere solo un'opzione resa applicabile da una condizione
  accettata. «Libero professionista singolo» o «Mandatario» senza ramo confermato sono rifiutati.
- **Ambito:** la ricevuta della scelta copre le opzioni mostrate e lega la risposta USER alla
  condizione. Se quella risposta viene revocata o cambia, la scelta decade. Non sblocca altre
  condizioni della casella; le ricevute esistenti non vengono estese né rifirmate.
- **Esclusività:** un'opzione sola; le altre non vengono marcate né svuotate (cardinalità
  ignota). Nessuna domanda se un'opzione è già spuntata.
- **Autorizzazione USER:** nulla si seleziona senza una risposta VALUE dell'USER. Il rinvio
  lascia la regione vuota e la domanda non viene ripetuta.
- **Nessun duplicato:** nessuna domanda se la ricevuta deriva già la casella o se un gruppo
  del modello copre la regione.

**Test (`test_capacity_choice_question.py`, 25):** conferma esplicita, rinvio, 6 risposte ambigue
o malformate, 2 scelte non applicabili, valore non ottenuto dalla scelta, 10 casi senza ramo
applicabile accettato, assenza di duplicati, revoca o modifica della condizione, altra
condizione aperta. Sul genitore 15 su 25 falliscono; i 10 che passano sono i casi negativi
senza domanda.

**Rigioco (nuove etichette; il replay storico e i suoi file restano invariati):**

| Scenario | Domanda di scelta | Scritture | Uguali al riferimento | `p39.cb0` |
|---|---|---:|---:|---|
| Storico, policy preregistrata (`p39-storico-policy-v2`) | Posta una volta, rinviata | 48 | 46 | Vuota |
| Controfattuale (`cf-p39-scelta-autorizzata`) | Posta una volta, scelta autorizzata | 49 | 47 | Spuntata |

- **Controfattuale:** `policy-cf-p39.cjs` risponde alla sola domanda di scelta con il testo
  preregistrato «corporate», che nomina l'opzione. Lo script `replay03_controfattuale.py` è una
  copia di `replay03.py` che seleziona la policy e codifica la scelta con l'estratto letterale
  della risposta.
- **In entrambi:** 0 valori diversi, 0 domande ripetute, 0 sospensioni.
- **Nel DOCX controfattuale:** su 13 caselle native è spuntata solo `p39.cb0`.

## Fix 2a e fix 2b

| | 2a (`f7d35f8`, `4712c49`; policy `2bdaf45`) | 2b (`f2d7577`) |
|---|---|---|
| Soggetto | Sottoscrittore (`s1_b_leo`) | Direttore tecnico (`s2_b_dt`) |
| Binding | Resta respinto, correttamente: il FORM lascia la carica in bianco | Da respinto a fondato: la riga soci è registrata come citazione non attestante |
| Meccanismo | Dialogo: domanda sul nome, riuso SOURCE, ordine delle condizioni | Validatore: una citazione senza ruolo non invalida un'attestazione letterale |
| Campi con errori | 19 → 10 | 10 → 4 |
| Scritture | 39 → 48 | 48 → 48 |
| Pool | Più `field:p12.s0` e `condition:s1_c_firmatario` | Più `condition:s2_c_dt` (6 campi), rinviata dalla policy |

Il 2b rende quindi i campi del direttore tecnico confermabili dall'USER, senza scriverli.

## Limiti

- **Rigioco:** narratore, planner e guardia sono deterministici, quindi il rigioco non misura la
  qualità del modello reale. Un narratore reale può non selezionare la domanda sul nome; il
  fallback del backend la propone solo se il narratore non sceglie nulla.
- **Filtro del fix 3:** è lessicale. Rimuove anche negazioni lecite che citano dati («i dati …
  non sono trasferibili») e non verifica le affermazioni positive (comportamento invariato).
- **Fix 2a':** riguarda solo il blocco del sottoscrittore che sostituisce una proposta bloccata.
- **Ricevute già rese:** non vengono estese né rifirmate. Una conferma resa prima resta limitata
  al suo ambito.
- **Fix 4:**
  - la ricevuta della scelta lega anche le condizioni delle altre opzioni. Se una di esse riceve
    una risposta dopo la scelta, la ricevuta diventa obsoleta e la casella resta vuota senza una
    nuova domanda; è un comportamento conservativo;
  - la policy preregistrata rinvia la nuova domanda, perché la regola «corporate» non vede le
    opzioni. La scrittura c'è solo nello scenario controfattuale.
- **Nessun nuovo audit reale.** Va autorizzato a parte.
