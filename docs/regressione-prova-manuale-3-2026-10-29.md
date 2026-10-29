# Regressione della terza prova manuale Minervino (29 ottobre 2026)

**Ambito:**
- prova 3: istanza `tesi-prova-manuale-3-20261029`, codice `5dc8918`, sessione `08cc0cc3…`;
- analisi su copie congelate delle evidenze; istanza in esecuzione non toccata.

Nessuna chiamata DeepSeek, push o merge; app ordinaria e prove precedenti invariate.

**Grezzo:** `backend/data/compilation-audit/prova-manuale-minervino-3-20261029/`:
- `evidenze/`: DB, istantanee, chiamate, log, artefatti e DOCX, con le impronte in
  `SHA256SUMS-evidenze.txt`;
- `replay_manuale.py` (versione 2) e `replay/`;
- `suite-f5c3ef9.txt`;
- `rollback-f5c3ef9.txt`.

## Codice in esecuzione

| | Prova 2 | Replay del rapporto precedente | Prova 3 |
|---|---|---|---|
| Codice | `a4582a1` | `e28475c` / `c9af3ea` (sui dati delle prove 1-2) | `5dc8918`, codice identico a `c9af3ea`; processi dal worktree 3 |
| Output del modello | proprio | prove 1 e 2 | **nuovo**, condizioni diverse |

## Dove si perdono i dati

DOCX della prova 3: 8 scritture contro le 49 della prova 2.

Dei 48 campi mancanti:
- 47 hanno una proposta con fatto SOURCE GROUNDED e sono conditional;
- 1 è la casella `p39.cb0`, coperta da una scelta USER esplicita.

Non mancano proposte, non c'è invalidazione e la guardia non ha rifiutato nulla. **Tutti sono
bloccati da una sola condizione, `s1_c_soc`, rimasta aperta.**

**Catena:**
1. Il modello dichiara la stessa clausola FORM (paragrafo 39, «Legale rappresentante di società…»)
   come due condizioni semantiche:
   - `s1_c_soc` governa i dati dell'operatore nel blocco firmatario (`p14.s1`–`p17.s1`) e
     `p39.cb0`;
   - `s2_c_soc` governa soci e direttore tecnico.
2. **`010192b`** aveva esteso la trattenuta delle condizioni del blocco firmatario: finché il nome
   è aperto, ogni condizione del blocco aspetta. Prima valeva solo con una proposta MODEL
   bloccata. Al turno 1 `s1_c_soc` viene quindi esclusa e il pool chiede la clausola solo per
   `s2_c_soc` (41 campi).
3. L'utente conferma «Sì, come legale rappresentante di una società di ingegneria»: la ricevuta
   copre `s2_c_soc` soltanto.
4. Dal turno 2 `s1_c_soc` è una domanda separata sulla stessa clausola, prima nel pool. Il
   narratore non la sceglie né al turno 2 né al turno 3, e l'utente chiede la bozza.
5. Il gate di export la lascia aperta: blocco formalmente giustificato, ma dovuto alla
   domanda spezzata. La scelta 4 è registrata, ma la casella resta vuota per la stessa
   condizione.

**Prova diretta:** sullo stesso stato v3 della prova 3:
- il codice `a4582a1` produce una sola domanda (`s1_c_soc` + `s2_c_soc`, 50 campi);
- il codice `5dc8918` produce `s2_c_soc` da sola (41 campi).

## Perché il replay risultava positivo

- **Solo dati vecchi:** i replay usavano gli output del modello delle prove 1 e 2. Nella prova 2
  la condizione trattenuta era la chiave del gruppo scelta dal narratore reale; lo stub la
  chiedeva al turno 2 e il gruppo si ricomponeva.
- **Lo stub nascondeva lo split:** sceglieva gli slot solo per chiave registrata. Nel turno 1 del
  replay della prova 2 il pool conteneva già la domanda spezzata `condition:s2_c_soc`, ma quella
  chiave non era tra quelle reali e veniva saltata. Il narratore reale della prova 3 l'ha chiesta
  subito.
- **Controllo «nessuna conferma persa» incompleto:** guardava solo i campi delle ricevute, non le
  proposte bloccate da condizioni mai chieste.

**Replay versione 2:**
- gli slot reali vengono letti dalle istantanee con le loro condizioni e abbinati per chiave o
  per condizione;
- `SESSIONE=3` usa le evidenze congelate;
- `ESTENSIONI=no` simula un narratore che non sceglie mai le domande di estensione.

**Fedeltà:** il replay della prova 3 sul codice della prova 3 riproduce il DOCX reale (8
scritture, valori identici).

## Correzione (`f5c3ef9`)

Una condizione trattenuta non spezza mai una clausola FORM dichiarata anche da una condizione
fuori dalla trattenuta: viene chiesta subito insieme a quella. Il criterio di equivalenza (stesso
paragrafo FORM, operatore semantico) è ora condiviso con il raggruppamento del pool. Una clausola
che riguarda solo il blocco attende ancora il nome.

**Invariati:**
- ricevute, validatori, guardia e gate di export;
- nessuna casella, dichiarazione o valore autorizzato implicitamente.

**Test:**
- `test_signatory_hold_shared_clause.py`, su FORM sintetico: 2 su 3 falliscono sul codice
  precedente e passano dopo. Il terzo, il caso di controllo, passa in entrambi;
- suite backend: 4.164 passati, 8 saltati (artefatti locali assenti); Ruff PASS.

**Rollback:** l'albero torna al genitore, il nuovo test torna a fallire, i 130 test esistenti
dei moduli toccati passano.

## Replay (risposte USER letterali; narratore, planner e guardia simulati)

| Prova | Codice prova 2 `a4582a1` | Codice prova 3 `5dc8918` | Dopo `f5c3ef9` | Dopo, senza estensioni |
|---|---:|---:|---:|---:|
| 1 | 57 | 57 | 57 | — |
| 2 | 49 | 59 | 59 | 58 |
| 3 | 59 | **8** | 60 | 59 |

**Prova 3 dopo `f5c3ef9`:**
- nessun campo tolto o cambiato rispetto al codice della prova 2;
- in più `p14.s0` (carica), solo se l'utente risponde all'estensione;
- `p39.cb0` è l'unica casella: ricevuta della scelta (opzione 4) valida, condizioni
  confermate dall'utente, nessun'altra opzione valida;
- tutti gli altri campi sono SOURCE coperti da conferme USER che li includono;
- dichiarazioni, designazioni, categorie e luogo/data restano vuoti.

## Problemi aperti

- **Domande che il narratore non sceglie:**
  - una condizione aperta che governa proposte, o una domanda di estensione, può restare non
    chiesta: il backend non la impone (lo fa solo per rifiuti e autorizzazioni);
  - la bozza la lascia vuota senza dirlo («Le informazioni non verificate restano vuote»);
  - nella prova 3 questo ha trasformato lo split in 48 campi vuoti silenziosi;
  - serve una decisione: domanda imposta dal backend, avviso esplicito alla bozza, o entrambi.
- **Clausola equivalente già confermata da sola** (sessioni esistenti): l'altra condizione resta
  una domanda separata, senza riuso della conferma. Correttamente non viene autorizzata in
  automatico.
- **Replay:** misura la logica del backend, non le scelte future del narratore reale.
  - Il caso peggiore senza estensioni è coperto.
  - Un narratore che salta le condizioni no: vedi il primo punto.
- **Istanza 3:** ancora in esecuzione su `5dc8918`; non aggiornata, nessuna nuova prova avviata.
