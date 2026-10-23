# Sprint sulla compilazione per sezioni (rev 3), 23 ottobre 2026

Lavoro offline, zero chiamate LLM. Branch locale `sprint/2026-10-23-sezioni`, worktree
`/home/montesano/tesi-sprint`, base `dd41e2e`. Nulla è attivo nell'app live: ogni correzione è
una revisione opt-in delle nuove sessioni rev 3.

**Riferimenti:**
- **Grezzi e strumenti:** `backend/data/compilation-audit/sprint-sezioni-20261023-01/`
  (esclusa da Git).
- **Congelamento della base:** `BASE-FREEZE.json` (326 file, base `dd41e2e`).
- **Suite di partenza:** `out/suite-base.log` (3.677 PASS, Ruff PASS).

## PASSO 1 — sicurezza dei rami del FORM

### Controesempi (fase A)

Tabella completa: `out/controesempi-passo1.json`, prodotta da `controesempi_passo1.py` a partire
da `out/diagnosi-rami.json` e `out/rigioco-r1.json`.

**Scenari congelati:** tutti chiedono partecipazione singola come società di ingegneria, senza
raggruppamenti, consorzi o altre forme. Le 25 scritture rev 2 sono tutte accertate dalla revisione
autoriale.

| Tentativo rev 2 | Destinazioni | Ramo applicabile | Ramo scritto | Perché è passata | Chiusura |
|---|---|---|---|---|---|
| minervino-1 | `p37.s1-s7` (7) | `p39`, società | `p35`, studio associato | condizione `s1_c35` ancorata all'opzione, aperta, con scope solo su `p36` | **R1, deterministica** |
| soresa2023-1 | `p127.s1-s4` (4) | `p123`, nessun avvalimento | `p125`, avvalimento: l'ausiliaria è un terzo | `s2_c_sing` (partecipazione singola, confermata) legata dal modello all'avvalimento | rev 3: guardia d'ambito, semantica |
| soresa2023-1 | `p44.s0-s1` (2) | dichiarante singolo | blocco di un componente RT sotto `p19` | `s2_c_sing` ancorata a `p33`, dove «singolo componente il RT» è stato letto come «partecipazione singola» | rev 3: guardia d'ambito, semantica |
| soresa2023-2 | `p127.s2-s4` (3) | nessun avvalimento | avvalimento | nessuna condizione | nessuna deterministica |
| soresa2023-2 | `p43.s8-s9`, `p44.s0-s1` (4) | dichiarante singolo | componente RT | nessuna condizione | nessuna deterministica |
| catanzaro-2 | `t19.*` (5) | 5.d società di ingegneria (`s4_c1` confermata) | 5.c società di professionisti | nessuna condizione sull'intestazione 5.c | nessuna deterministica |

**Casi collegati:**
- **`p31.s0` di So.Re.Sa.** (nome USER nel blocco di un componente RT): non è un'opzione, quindi R1
  non lo tocca. Nella rev 3 un valore USER richiede comunque una ricevuta d'ambito verificata.
  Invariato.
- **`s2_c_sing`:** è la condizione che ha autorizzato in rev 2 sei delle 25 scritture. Nella rev 3
  quelle sei restano bloccate senza una prova d'ambito della guardia: è una protezione semantica,
  non deterministica.

**Cronologia (dichiarata):**
1. La diagnosi strutturale (`diagnosi_rami.py`) e la misura dell'effetto di R1 sulle scritture
   registrate (`valuta_r1.py`) sono state eseguite **prima** del collegamento ai gate.
2. Questo file di risultati attesi è stato scritto **dopo** l'implementazione.
3. I numeri attesi (7 chiuse, 0 falsi rifiuti) erano già stati misurati e non sono cambiati.

### Correzione minima (fase B): R1, `branch_scope_revision 1`

**Regola:**
- **Opzione:** un paragrafo del corpo che comincia con una casella nativa o con un simbolo di
  casella V14.
- **Continuazione:** i paragrafi che seguono l'opzione, fino al primo di questi confini:
  - paragrafo vuoto;
  - nuova opzione;
  - grassetto senza campi;
  - separatore senza lettere né cifre;
  - tabella.
- **Effetto:** una condizione del modello ancorata all'opzione viene collegata anche alle
  destinazioni della continuazione, come il validatore V12 la collega al paragrafo d'origine.
- **Conseguenza:** domanda, ricevuta d'ambito rev 3, stato di applicabilità ed export trattano le
  destinazioni estese come quelle dichiarate.

**Limiti della regola:**
- **Cosa non fa:**
  - non crea condizioni;
  - non decide rami;
  - non legge le intestazioni né parole come «OPPURE»;
  - non tocca le opzioni senza condizione ancorata.
- **«[ ]»:** come in V14 non è riconosciuto, né come opzione né come confine. Un tratto più lungo
  può solo trattenere di più.
- **Campo con condizione omessa:** il validatore V12 lo respinge. R1 invece lo rende CONDIZIONATO,
  cioè in attesa della risposta USER.
- **Tracciabilità:** ogni collegamento aggiunto è registrato in
  `audit.branch_scope.option_continuations` con origine BACKEND.

**Attivazione:** solo nuove sessioni con `MAPI_GENERATION_REVISION=3` e
`MAPI_BRANCH_SCOPE_REVISION=1`. Il collegamento avviene nell'unico punto di validazione
dell'audit rev 2/3 (`validated_audit`). Lì il catalogo viene ricostruito dall'originale, perché lo
stato pubblico reclamato non lo contiene; nei 14 tentativi le continuazioni sono identiche a
quelle del catalogo salvato. Il validatore V12, il percorso monolitico, parser, writer e retrieval
sono invariati.

**File:**
- `backend/app/compilation_branch_scope.py` (nuovo);
- `backend/app/compilation_global_sessions.py`: flag delle nuove sessioni, collegamento in
  `validated_audit`, propagazione del flag allo stato effettivo;
- `backend/tests/test_compilation_branch_scope.py` (nuovo, 26 test).

### Verifiche (fase C)

- **Rigioco dei gate** (`rigioco_r1.py`, codice dello sprint): risposte di segmento registrate di
  14 tentativi (8 rev 2, 6 rev 3), unite e validate con il codice rev 3.

  | | Senza R1 | Con R1 |
  |---|---|---|
  | Sbagliate esportabili, ricevute registrate | 19 / 25 | 12 / 25 |
  | Sbagliate esportabili, guardia simulata SUPPORTED | 25 / 25 | 18 / 25 |
  | Corrette esportabili, guardia simulata (103 rev 2 + 142 rev 3) | 245 / 245 | 245 / 245 |
  | Corrette esportabili, ricevute registrate | 211 / 245 | 211 / 245 |
  | **Nuovi falsi rifiuti** | — | **0** |

  Le 34 corrette perse con le ricevute registrate sono le stesse con e senza R1: ricevute rev 2
  senza prova d'ambito rev 3.
- **Estensione delle regioni** (`valuta_r1.py`, 718 scritture corrette di quattro campagne,
  monolitica inclusa):
  - R1 tocca soltanto le 7 scritture sbagliate di minervino-1;
  - nessuna scritta corretta;
  - nessuna condizione diventa una domanda nuova: le domande esistenti includono solo più
    destinazioni.
- **Alternativa scartata, R1':** compilare la continuazione solo se la casella dell'opzione è
  spuntata. Avrebbe respinto 116 scritture corrette: nei tentativi per sezioni la casella `p39`
  spesso non viene spuntata, un difetto di coerenza del documento ma non di sicurezza.
- **Test deterministici** (26):
  - regioni e confini;
  - il controesempio registrato senza e con R1;
  - risposte USER negative, rinviate, ambigue e revocate;
  - ricevuta vincolata al solo scope del modello;
  - conferma dell'altro ramo;
  - ramo applicabile preservato;
  - nessuna condizione creata;
  - idempotenza;
  - solo rev 3 con flag;
  - profilo delle nuove sessioni;
  - sessione completa con provider simulato: domanda estesa, export 409 sulla destinazione
    estesa, bozza valida senza.
- **Sensibilità:** con R1 neutralizzato 17 test falliscono; passano i 9 negativi e di profilo.

### Limite documentato

Restano esportabili 18 scritture su 25 se il modello ripetesse le uscite rev 2 e la guardia
confermasse l'ambito. Per chiuderle in modo deterministico servirebbe un'interpretazione
semantica delle sezioni:
- l'intestazione So.Re.Sa. `p19` vale anche oltre le intestazioni annidate e i separatori;
- 5.c e 5.d di Catanzaro sono alternative esclusive;
- l'avvalimento di `p125` riguarda un terzo.

Come da istruzioni non è stata tentata. Nei 9 tentativi rev 3 osservati quelle destinazioni non
sono mai state proposte, ma è un comportamento osservato del modello con il FORM completo, non una
garanzia. La sicurezza generale dei rami **non** è dimostrata da questi 25 casi.
