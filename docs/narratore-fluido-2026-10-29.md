# Narratore fluido: cause e correzioni dalla prova manuale Minervino (29 ottobre 2026)

**Ambito:**
- tracce della prova manuale: istanza `tesi-prova-manuale-audit03-20261029`, 21 istantanee dello
  stato, turni della conversazione e chiamate al provider;
- nessuna chiamata DeepSeek, nessun push o merge, app ordinaria non toccata.

**Grezzo:** `backend/data/compilation-audit/prova-manuale-minervino-20261029/`, con
`replay_manuale.py`, i replay, `SIMULAZIONE.md` e i log.

## Ricostruzione e cause radice

L'utente ha confermato società, firmatario e carica, ha scelto la casella 4 e ha rinviato
categorie, dichiarazioni, designazioni e luogo/data.

| Versione | Domanda | Causa |
|---|---|---|
| v3 | Ramo società (`s1_c_societa`) | Necessaria |
| v6 | Scelta «IN QUALITÀ DI», 1.115 caratteri, poi rifiutata senza motivo | Il collegamento alla casella non era derivabile da `s1_c_societa` (casella fuori dallo scope). Messaggio di rifiuto privo di motivo |
| v9 | Stessa scelta, accettata | Ripetizione dovuta al rifiuto |
| v15 | `s2_c_soc`: stessa clausola FORM (paragrafo 39) | **C1:** due segmenti dichiarano la stessa clausola come condizioni distinte |
| v18 | Studio associato ×2, consorzio | **C2:** il collegamento della casella dà destinazioni FORM a tutte le alternative, che diventano domande inutili |
| Export | `p39.cb0` vuota nonostante la scelta esplicita | **C1b:** il collegamento `participation` di `s2_c_soc` occupa il gruppo ma non è mai esportabile; la scelta perde il gruppo. In più, le risposte successive rendono la ricevuta obsoleta senza avviso |
| Testi | Categorie 2.846, dichiarazioni 2.107 caratteri | **C4:** l'estratto FORM è copiato per intero nella domanda |

La guardia restituiva un esito per slot, ma il motivo non veniva conservato né mostrato (**C3**).

## Correzioni (commit separati, rollback verificati)

| Commit | Correzione |
|---|---|
| `e0ac426` | Condizioni semantiche sullo stesso paragrafo FORM: una sola domanda e una ricevuta per condizione, con prova di ambito ricalcolata dal backend |
| `23bbf78` | La scelta esplicita conserva il gruppo al posto di un collegamento non esportabile. Copre tutte le condizioni della casella. Se diventa non verificabile viene richiesta con il motivo; un rinvio non viene mai riproposto |
| `23aefbf` | Nessuna domanda sulle alternative di un'opzione già decisa quando governano solo la propria casella; le condizioni restano aperte |
| `038c062` | Motivo del rifiuto (codici della guardia o controllo del backend) e indicazione mirata; le conferme nominano la clausola FORM |
| `fe47456`, `f47b8db` | Domande brevi: opzioni numerate e brevi, estratti lunghi riassunti, testo integrale in `details` mostrato richiuso dall'interfaccia |
| `7e2951d` | Test negativo: opzioni incompatibili |

**Invariati:** validatori, condizioni, autorizzazioni USER e procedurali, regola di derivazione
della rappresentanza. Nessuna casella viene spuntata in automatico.

## Verifiche

**Replay del dialogo registrato** (risposte USER letterali della sessione; narratore, planner e
guardia simulati; pool, ricevute, gate ed export reali):

| | Prima (`dbdc317`) | Dopo |
|---|---:|---:|
| Turni / domande | 5 / 13 | 3 / 9 |
| Stessa clausola richiesta due volte | sì | no (2 ricevute da 1 risposta) |
| Alternative chieste | 3 | 0 |
| Scelta «IN QUALITÀ DI» | 1.115 caratteri | 638 caratteri: 7 opzioni brevi numerate, con dettagli |
| Categorie / dichiarazioni | 2.846 / 2.107 caratteri | 456 / 301 caratteri, con dettagli |
| Scritture / `p39.cb0` | 56 / vuota | 57 / spuntata (USER) |

- **Restano necessarie:** la conferma del ramo, il nome, la carica, una scelta esplicita della
  casella e le 5 decisioni, tutte rinviate e mai riproposte.
- **Export:** l'unica differenza è `p39.cb0`, con provenienza USER e ricevuta della scelta;
  nessun valore diverso, nessun effetto di deselezione. Dichiarazioni, designazioni, categorie e
  luogo/data restano vuoti.
- **Modalità «pool»:** da 11 a 9 domande, `p39.cb0` scritta.

**Test** (su FORM sintetici, non sul DOCX Minervino):
- nuovi test e test di sessione aggiornati, che falliscono sul codice precedente;
- casi negativi: scelta ambigua, scelta non applicabile, conferma revocata o modificata, soggetto
  diverso (guardia «non riguarda questa domanda»), opzioni incompatibili (nessuna casella e una
  sola scelta esplicita), rinvii.

**Suite (codice finale `f47b8db`):** backend 4.132 PASS (8 saltati per artefatti locali assenti); frontend 164/164, lint e build; Ruff PASS. Log: `suite-narratore-finale.txt`, `rollback-narratore.txt` nel grezzo.

**Rollback** (`tesi-rollback-narratore-<commit>-20261029`):
- ogni revert riporta l'albero del genitore;
- passano i 236 test esistenti dei moduli toccati (34 per `f47b8db`) e la suite frontend del
  genitore (159);
- i test nuovi falliscono sul codice ripristinato.

## Limiti

- **Replay:** la qualità del narratore e della guardia reali non è misurata. Il primo rifiuto
  reale (risposta con «[...]») non è riproducibile offline; ora l'utente vede il motivo e può
  rispondere con il numero dell'opzione.
- **Testi del narratore:** il backend controlla i propri testi (scelte, decisioni, conferma di
  riserva), non le formulazioni libere del narratore.
- **Raggruppamento:** solo per condizioni semantiche sullo stesso paragrafo FORM.
- **Richiesta motivata:** solo per la scelta «IN QUALITÀ DI»; altre ricevute obsolete restano
  bloccate, in modo conservativo, senza una nuova domanda.
- **Istanza manuale:** usa ancora `dbdc317`.
