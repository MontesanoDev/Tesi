# P3 — Preregistrazione (21 ottobre 2026)

Scritta dopo la diagnosi (`DIAGNOSI-P3.md`) e prima di qualunque codice P3. La base
tecnica è la candidata V13 + V14 + K3; la V12 resta la baseline adottata. I
[criteri di conclusione v1](../../../../docs/criteri-conclusione-2026-10-21.md) restano
congelati e non vengono modificati. Questa campagna non è la valutazione finale.

## Forma dell'intervento

Due flag indipendenti, solo per le nuove sessioni, copiati in `resolve_global` come
quelli di V14 e K3:
- `dialogue_revision: 1`;
- `generation_revision: 1`.

Le sessioni esistenti (V12, V13, V14, K3) restano identiche. Per la campagna, un runtime
privato può creare sessioni senza `generation_revision` (variabile d'ambiente letta da
`initial_state`): solo così gli effetti si separano.

### Generazione (`generation_revision: 1`)

- **G0. Caratteri di controllo.** Il JSON globale si legge con `strict=False`: tabulazioni
  e altri caratteri di controllo letterali dentro le stringhe sono ammessi, senza alcuna
  riparazione di parentesi, troncamenti o contenuti.
- **G1. Partizione dal backend.** Segmenti di blocchi FORM contigui, con al massimo 60
  candidate ciascuno e al massimo 6 segmenti. Un blocco non si divide mai, e una regione
  d'opzione V14 resta con la tabella che la segue. Un modulo piccolo forma un solo segmento.
- **G2. Contesto intero.** Ogni chiamata riceve lo stesso prompt di sistema, lo stesso
  input completo (FORM, SOURCE, contesto USER) e lo stesso limite di output. In coda c'è
  un'istruzione di segmento: proporre solo per i candidate elencati, usando tutto il resto
  come contesto. `max_tokens` non aumenta.
- **G3. Esecuzione.** Prima il segmento 1, che riscalda la cache del prefisso, poi gli
  altri in parallelo (al massimo 3 alla volta). Nessun nuovo tentativo.
- **G4. Unione.** Le proposte fuori dal segmento si scartano e si registrano. Gli
  identificativi di fatti, binding, condizioni, gruppi e chiarimenti diventano
  `s<i>_<id>`; i contenuti identici si deduplicano. La copertura resta limitata ai candidate
  del segmento. Il payload unito è il `response.txt` canonico ed è validato **dallo stesso
  validatore V12**, insieme a riuso V13, consenso V14, K3, applicabilità e completezza. I
  grezzi di ciascun segmento restano in `segments/`.
- **G5. Conflitti.** Fatti con stesso soggetto e stessa proprietà ma valori diversi in
  segmenti diversi: ogni campo che li usa perde il grounding, con il motivo registrato.
- **G6. Segmento fallito.** Errore, troncamento o JSON non valido lasciano i suoi
  candidate vuoti con il motivo «sezione non analizzata». Gli altri segmenti proseguono, e
  messaggio, report di export e audit mostrano le sezioni non analizzate. Se falliscono
  tutti, l'analisi fallisce come oggi.

### Dialogo (`dialogue_revision: 1`)

- **D1. Decisioni del primo messaggio.** Una piccola chiamata propone le risposte agli
  slot di applicabilità aperti presenti nel messaggio iniziale. La guardia di pertinenza
  esistente le controlla, e un controllo deterministico richiede che l'estratto sia
  letterale nel messaggio. Le risposte accettate diventano ricevute USER con origine
  `initial_request`, applicate come una risposta normale (audit rinfrescato e salvato). La
  sintesi le dichiara, così l'utente può correggerle. Sono esclusi gli slot di
  autorizzazione, di valore e di scelta: nessuna dichiarazione, valore o casella viene da qui.
- **D3. Alternative.** Per le risposte di condizione già controllate dalla guardia
  (`SUPPORTED`) non si usa più il filtro « o ». Per i valori resta un controllo limitato alla
  disgiunzione adiacente al valore stesso («Bari o Lecce»). Il consenso V14 non cambia.
- **D4. Sospensioni.** Ogni sospensione con un riferimento a uno slot registra la chiave del
  suo blocco (condizione, autorizzazione o decisione). Quando quel blocco riceve una risposta
  accettata, la sospensione si rilascia. Si rilascia anche se il narratore la ripropone sullo
  stesso blocco già risolto. Le sospensioni senza un blocco risolvibile restano.
- **D5. Data corrente.** La data del server entra nel contesto del narratore e nell'input
  globale.
- **D6. Domande.** Se il narratore non chiede nulla mentre restano condizioni o
  autorizzazioni aperte che governano proposte grounded, il backend le chiede (al massimo
  3) con il testo dello slot. Dopo 2 risposte non accettate sullo stesso slot, il backend
  registra `UNKNOWN` (`BACKEND_LOOP_GUARD`): la domanda non torna e i campi restano vuoti
  con motivo.
- **D7. Sospensioni raggruppate.** Una motivazione può coprire più proposte con lo stesso
  blocco, così l'output del narratore resta piccolo.

**Non incluso:** riuso di risposte successive per slot non chiesti (D2), scelte di caselle
dal primo messaggio, i quattro rischi residui di P2/K3.

## Verifiche deterministiche (tutte prima della campagna)

1. **Replay per proiezione.** Ogni payload V12 valido registrato si divide nei segmenti G1,
   si unisce con G4 e si valida. L'esito per candidate deve coincidere con la validazione
   monolitica nel 100% dei casi: stato, valore proposto, condizioni (identificativi a parte).
   Ogni differenza è un difetto da correggere prima di proseguire.
2. **Replay delle sospensioni** sugli stati finali registrati: numero di sospensioni
   rilasciate e mantenute, con motivo.
3. **Replay dei 92 rifiuti lessicali:** quanti sarebbero accettati.
4. **Test positivi e negativi** per ogni meccanismo. Devono tenere:
   - consenso V14 mai dal primo messaggio;
   - CCIAA ancora bloccata senza autorizzazione;
   - K3 dopo l'unione;
   - i 7 rifiuti azienda→persona di Cesano;
   - record personali, ruoli e condizioni USER;
   - sessioni senza flag identiche.
5. **Suite backend completa e Ruff.**

## Campagna E2E limitata

- **Documenti:** Minervino, Cesano, CRAA, Catanzaro.
- **Bracci:** **A** = dialogo nuovo + generazione monolitica; **B** = dialogo nuovo +
  generazione per sezioni.
- **Tentativi:** 2 per documento e braccio, quindi 16 in totale. Tutti contano: nessuna
  sostituzione o ripetizione.
- **Condizioni:** stessa politica USER naturale della verifica V14 (risposte di ramo,
  autorizzazione, rinvio), stesso modello e prompt B0, codice congelato con hash.
- **Budget:** 6 milioni di token totali; superato il budget ci si ferma.

Misure:
- DOCX su tentativi;
- campi del nucleo scritti correttamente, omissioni, scritture non dimostrate (revisione
  dell'autore, non indipendente);
- domande ridondanti, decisioni non acquisite, domande ripetute;
- fallimenti di modello, JSON, narratore e backend;
- token, chiamate, latenza;
- motivi dei campi vuoti.

Il confronto con V13 e V14 non è appaiato, perché cambiano le risposte LLM. Il confronto
fra A e B è appaiato per documento e politica, ma non per risposta.

Obiettivi di meccanismo (non soglie di conclusione):
- 0 scritture non dimostrate;
- 0 aggiramenti di V14 o K3;
- 0 conferme ridondanti di decisioni del primo messaggio;
- 0 domande identiche per 3 turni;
- 0 condizioni aperte su proposte grounded non chieste né `UNKNOWN` all'export;
- 0 sospensioni con blocco risolto non rilasciate;
- in B, output inferiore al 50% del limite nel 90% delle chiamate di segmento.

Arresto:
- una scritta non dimostrata attribuibile al nuovo meccanismo, o un aggiramento V14/K3,
  ferma quel braccio;
- in B, una mediana della copertura del nucleo inferiore a quella di A di oltre 20 punti
  su un documento, oppure un tasso di proposte respinte dal validatore almeno doppio, è un
  peggioramento grave: la suddivisione si rivede invece di proseguire.

Gli obiettivi non raggiunti diventano limiti documentati.
