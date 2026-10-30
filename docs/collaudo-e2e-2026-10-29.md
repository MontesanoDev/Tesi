# Collaudo E2E autonomo del compilatore DOCX (29-30 ottobre 2026)

**Ambito:**
- compilazioni reali con DeepSeek (`deepseek-flash`), autorizzate dall'utente;
- app pilotata via HTTP con le stesse chiamate del frontend: «compila» con il FORM, `/resolve`
  automatici, un messaggio USER per turno, richiesta di bozza;
- worktree isolati per versione del codice e un runtime nuovo per ogni esecuzione;
- profilo AI copiato cifrato, mai decifrato.

Nessun push, merge o modifica dell'app ordinaria; nessuna domanda, firma o attestazione inviata.

**Grezzo:** `backend/data/compilation-audit/collaudo-e2e-20261029/`:
- `scenari/`, scenari e policy congelati, con `MANIFEST.json`;
- `strumenti/`: `esegui.py`, `servizio.py`, `valuta.py`, `riepilogo.py`, `rollback_check.sh`;
- `esecuzioni/<run>/`: trascrizione HTTP, turni, chiamate al provider, runtime, `report.json`,
  `bozza.docx`, `valutazione.json`;
- `RIEPILOGO.json`, `rollback.txt` e le suite.

Fase 1 sulla prova 4: `prova-manuale-minervino-4-20261029/`.

## Metodo

- **Utente simulato:** policy esplicita per scenario, scritta prima dei run.
  - Regole ordinate sulla clausola FORM di ogni domanda: conferma, esclusione o rinvio.
  - Firmatario dello scenario; scelta dell'opzione prevista; rinvio di decisioni e valori
    non noti; rifiuto di ogni dichiarazione o autorizzazione.
  - Nessuna casella, dichiarazione o designazione autorizzata dalla policy.
- **Correzioni dichiarate della policy dopo i primi giri** (`policy_note` negli scenari):
  - Trapani v2: la partecipazione mancava;
  - Catanzaro v2: «CHIEDE di partecipare» ed esclusioni ancorate all'inizio dell'opzione;
  - checkbox v2: conferma del richiedente.
- **Valutazione indipendente:**
  - `report.json` del DOCX esportato confrontato con il gold dello scenario;
  - verifica che ogni valore del report compaia davvero nel testo del DOCX: sempre vera, in
    38 bozze su 38;
  - controlli sul dialogo: domande ripetute, valori documentati chiesti all'utente, conferme
    senza effetto, condizioni aperte, sospensioni, avviso alla bozza, rifiuti della guardia.
- **Nessuno stub:** narratore, planner e guardia sono reali.

## FORM e SOURCE

| FORM | Tipo | Uso | SOURCE | Gold |
|---|---|---|---|---|
| Minervino V1 | reale (sviluppo) | correzioni | Company KB Mapi simulata (3), General KB, avviso | `gold.json` (267 posizioni) |
| Benchmark compilazione V1 | sintetico | ha prodotto 2 correzioni nel giro 1 | 5 Company, 1 progetto, 1 General | `gold.json` (55) |
| Trapani Green | reale pubblico | ha prodotto 2 correzioni | visura Mapi simulata, avviso, disciplinare | autoriale (istruzioni) |
| Catanzaro DL/CSE | reale pubblico | variante «solo azienda» | visura Mapi simulata | `mappa-campi.json` (36) |
| Benchmark checkbox V1 | sintetico | indipendente | 2 Company, 1 General (inline) | `gold.json` |
| Comune di Bergamo, All. 1 | **reale, estratto a caso** (`fuori-campione/POOL.json`) | fuori campione | visura Mapi simulata | autoriale |

Catanzaro con bando e disciplinare (178-200 frammenti, 211-234 mila caratteri) supera il limite
dell'analisi (96 frammenti, 100.000 caratteri): ora fallisce subito con motivo esplicito.

## Esecuzioni e consumi

- **Esecuzioni:** 44 reali; 38 bozze esportate, 2 Catanzaro con il corpus completo (oltre il
  limite) e 4 interrotte dalla fine di una sessione di lavoro.
- **Chiamate:** 539, 0 errori HTTP.
- **Token:** 11.759.596, di cui 6.990.456 in cache, 3.120.278 fuori cache e 1.648.862 in uscita.
- **Costo:** circa 1,48 USD in stima (tariffe pubbliche del 28 ottobre; fatturazione non
  verificata).

## Risultati sul codice finale `45b8794` (e confronto)

«Corretti» comprende i valori uguali al gold, le caselle e la scelta USER. «Non attesi» sono i
valori scritti dove il gold vuole vuoto.

| FORM | Run | Corretti | Errati | Mancanti | Non attesi | Vuoti giustificati | Turni / domande |
|---|---:|---|---:|---|---:|---:|---|
| Minervino | 3 | 49 / 52 / 35 | 1 / 1 / 0 | 11 / 8 / 26 | 0 | 206 | 4 / 8-10 |
| Compilazione | 1 | 18 di 18 | 0 | 0 | 0 | 37 | 4 / 7 |
| Checkbox | 1 | 7 | 0 | 0 | 0 | 9 | 3 / 4 |
| Catanzaro (azienda) | 1 | 7 | 0 | 6 | 2 | 21 | 3 / 6 |
| Trapani v2 | 1 | 0 scritture (attese 9) | 0 | — | 0 | — | 4 / 10 |
| Bergamo (fuori campione) | 1 | 1 (firmatario) | 0 | carica non proposta | 0 | — | 2 / 2 |

**Andamento per versione del codice:**
- Minervino: 27 (`b0d66af`) → 60 (`220f856`) → 9 e 36 (`c8e5808`) → 0 (`ffc983d`, narrazione
  scartata) → 49, 52, 35 (`45b8794`).
- Compilazione: 15 → 18.
- Trapani: 1 → 8 (policy v1); con la policy v2 i risultati vanno da 0 a 9 a seconda del run.

**Caselle:**
- tutte corrette;
- Minervino: solo `p39.cb0` (scelta USER, opzione 4);
- checkbox e compilazione: solo tipologie documentate e le esclusive false del gold.

**Dichiarazioni:** 0 autorizzate e 0 scritte.

**Errati:**
- Minervino `p14.s0`: la carica scritta è «amministratore unico e rappresentante legale», letterale
  della fonte, contro «rappresentante legale» del gold. È più ampia del gold, sulla persona giusta.
- **Catanzaro (2 run):** nel codice fiscale dell'impresa è stata scritta la partita IVA
  «IT01234567890». È un errore vero della proposta del modello e il validatore non lo blocca.

## Difetti trovati e corretti (commit separati, test falliti prima e passati dopo, rollback verificato)

| Commit | Difetto (evidenza reale) | Meccanismo corretto |
|---|---|---|
| `bea2a7c` | Prova 4: «Scelgo l'opzione 4… Genera ora la bozza» → risposte scartate, casella vuota | finish/generate portano le risposte, registrate e verificate prima della bozza |
| `b0d66af` | Prove 3-4: condizioni sui dati documentati mai chieste | domande garantite e avviso alla bozza dei dati rimasti vuoti |
| `56eb679` | Compilazione: l'opzione ISO governava la tabella CCIAA | un'opzione governa la tabella successiva solo se la annuncia |
| `2fa72ee` | Compilazione: firmatario chiesto sulla riga di firma | una riga di firma non è il nome |
| `32600cb` | Trapani: 9 dati in attesa di un rinvio, senza avviso | l'avviso conta anche i rinvii |
| `487fe9e` | Catanzaro: corpus oltre budget, sessione bloccata senza motivo | sessione FAILED con conteggi, limiti e cosa fare |
| `ecc6ed0` | Minervino: estensione rifiutata dalla guardia reale | la domanda di estensione nomina la clausola |
| `302a358` | Minervino: il rifiuto mostrava la nota del modello | il rifiuto nomina la clausola FORM |
| `220f856` | Minervino: 22 soci sospesi in attesa della qualità, mai rilasciati | sospensione legata alla scelta di qualità del ramo |
| `c8e5808` | Trapani: rifiuto inspiegabile | verdetti grezzi della guardia nella traccia privata |
| `ffc983d` | Trapani: la PEC della dichiarazione allargava la condizione (verdetto tracciato) | un valore dichiarativo non autorizzato non allarga una condizione |
| `45b8794` | Minervino: domanda aperta su uno slot di condizione → narrazione scartata 2 volte, bozza vuota | conferma chiusa del backend al posto della domanda aperta |

**Verifiche:**
- test di regressione su FORM sintetici;
- rollback di 12 commit: l'albero torna uguale al genitore e i nuovi test falliscono sul codice
  ripristinato;
- backend 4.187 PASS e 8 saltati su `45b8794` (`suite-finale.txt`), Ruff PASS; frontend
  168/168.

## Anomalie del narratore e problemi aperti

1. **Sospensioni «source» su dati documentati** (Minervino: da 0 a 31 campi per run).
   - Motivi come «la forma di partecipazione non è ancora confermata» o «il modulo distingue
     Responsabile della Progettazione…» sono dubbi di applicabilità, ma vengono etichettati
     come fonte, quindi nessuna risposta USER li scioglie.
   - È un problema architetturale: il giudizio del modello resta, per scelta, non revocabile
     dal backend. Proposta: chiedere all'utente o rivalutare prima dell'export.
2. **Guardia e clausole del modello.**
   - Rifiuti di ambito su conferme esplicite, quando la condizione del modello è un frammento
     («dell'operatore economico», «(eliminare le opzioni non pertinenti)») o unisce due
     alternative («società di professionisti … o di società di ingegneria»).
   - È la causa principale della variabilità di Trapani e Minervino.
3. **Ciclo sul rinvio.** Il rinvio esplicito di una conferma che riguarda molti dati viene
   trasformato in una spiegazione e riproposto: 2-3 turni persi (Minervino `c8e5808-3`).
   Il rifiuto per spiegazione non marca la domanda come `retry`.
4. **Limite del corpus** (96 frammenti, 100.000 caratteri): i bandi reali completi non entrano.
   Serve una selezione delle SOURCE pertinenti, decisione da prendere.
5. **Derivazione della carica:** funziona solo con schede persona strutturate. A Bergamo la
   carica di Luca Ferri, documentata nella visura, è stata chiesta all'utente.
6. **Proposte errate non bloccate:** partita IVA nel codice fiscale (Catanzaro); abbreviazione
   «Ing.» per la qualifica.
7. **Variabilità del modello:** lo stesso FORM e lo stesso codice danno risultati diversi:
   - Minervino: 9, 36, 49, 52 e 35 campi corretti;
   - checkbox: proposte respinte dal validatore in un run.
8. **Policy simulata:** le regole sulla clausola sono fragili su FORM nuovi (Trapani v1,
   Catanzaro v1, checkbox v1) e alcune perdite del primo giro erano della policy. La qualità del
   dialogo con un utente reale non è misurata.
9. **Fuori campione:** un solo FORM estratto a caso e piccolo (Bergamo). Non basta per
   dichiarare la generalizzazione.
