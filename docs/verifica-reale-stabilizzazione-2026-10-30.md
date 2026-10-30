# Verifica reale della stabilizzazione del compilatore DOCX (30 ottobre 2026)

Seguito di `docs/stabilizzazione-compilatore-2026-10-30.md`: la verifica reale del codice
`381ed63` si era fermata per credito DeepSeek esaurito (402). Credito ripristinato: verifica
eseguita con DeepSeek reale per compilatore, narratore e guardia, senza stub.

## Riepilogo

**Domanda:** cinque compilazioni dello stesso FORM producono risultati corretti e
sostanzialmente coerenti?

**Risposta: corretti sì, coerenti non ancora.**

- **Correttezza e sicurezza** in tutti i 64 run reali di questa sessione:
  - errori dei valori: solo la carica di Minervino più ampia del gold, già nota (letterale della
    fonte), e i due identificativi letterali di Catanzaro che la mappa vuole da confermare;
  - 0 dichiarazioni autorizzate, 0 caselle senza decisione valida, 0 caselle diverse dal report
    nel DOCX;
  - ogni valore del report è presente nel DOCX esportato.
- **Ripetibilità migliorata ma insufficiente.**
  - Minervino, campi corretti su 61 attesi:
    - partenza (`45b8794`, run validi): 28 / 42 / 1;
    - codice `381ed63`: 50 / 47 / 59 / 27 / 54;
    - codice finale `f0c48ba`: 55 / 56 / 51 / 43 / 34.
  - Restano run isolati con forti perdite in Minervino, Trapani, checkbox e CNR.
- **Cause residue, tutte dimostrate sui dati reali:**
  1. output dell'analisi respinti dai validatori (fino a 26 campi in un run);
  2. sospensioni del narratore che il backend non può verificare;
  3. condizioni ancorate dal modello a istruzioni del FORM («(eliminare le opzioni non
     pertinenti)»), che la policy simulata rinvia.
- **Nessuna risposta USER persa** in 63 run: 12 risposte non accettate al primo tentativo sono
  state chieste di nuovo una volta e tutte registrate. Alla partenza un solo run perdeva 41 campi
  per rifiuti della guardia (correzione A).
- **Tre nuovi difetti generali corretti:** `cd47147`, `87b756f`, `f0c48ba`. Ciascuno ha un test
  fallito prima e passato dopo, rollback verificato, suite completa e nuovo giro reale.
- **Giudizio:** affidabile come assistente prudente con revisione umana, **non** come
  compilatore ripetibile senza revisione. Restano decisioni architetturali (sotto).

## Controllo iniziale

- Codice `381ed63`, worktree pulito e venv propria (`/home/montesano/tesi-stab-finale-381ed63`).
- Scenari v3, policy USER v3, FORM, SOURCE e parametri identici alla partenza: hash di
  `MANIFEST.json` verificati.
- Evidenze precedenti intatte.
- Sonda reale `bergamo-v3-sonda-381ed63-1`: 7 chiamate, tutte 200.
- Concorrenza 4: con 10 run paralleli erano comparsi i 429. Nessun 402 o 429 in tutta la
  sessione.

## Metodo e misure

- **Driver:** HTTP con le stesse chiamate del frontend, un messaggio USER per turno dalla policy
  congelata, richiesta della bozza alla fine. Runtime nuovo per ogni run; profilo AI copiato
  cifrato.
- **Matrice:** Minervino 5, Trapani 5, Catanzaro (azienda) 3, compilazione 3, checkbox 3,
  Bergamo 3, CNR IRISS 3, eseguita due volte:
  - `finale` sul codice `381ed63`;
  - `f0c48ba` sul codice finale.
  - In mezzo un giro di 13 run su `cd47147`: casi coinvolti più una regressione per FORM.
- **Esiti per campo:** dallo stato del backend (`field_outcomes`), non dalle note del narratore.
- **Verifica indipendente del DOCX** (`analisi/verifica_finale.py`):
  - testo di ogni valore del report cercato nel DOCX;
  - stato di ogni casella letto da `w:checkBox`/`w14:checkbox` e confrontato con il report;
  - nessun'altra casella cambiata rispetto all'originale.
- **Reale e stima:** tutti i numeri delle tabelle vengono da run reali. Le due verifiche
  deterministiche sugli stati registrati sono indicate come stime.

**Gold:** Minervino 61 valori attesi; compilazione 18; checkbox 7-8 (l'ottava è la scelta USER
di partecipazione, quando il modello la chiede); Catanzaro 16 posizioni della mappa. Trapani,
Bergamo e CNR hanno un gold autoriale: conta i valori scritti presenti nelle fonti, non i
mancanti. Trapani ne attende 9.

## Risultati reali per FORM e ripetizione

Campi corretti per run (stesso FORM, SOURCE, parametri e policy):

| FORM | Partenza `45b8794` (validi) | `381ed63` | `cd47147` (giro mirato) | **Finale `f0c48ba`** |
|---|---|---|---|---|
| Minervino (61) | 28 / 42 / 1 | 50 / 47 / 59 / 27 / 54 | 60 / 50 / 49 / 30 / 24 | **55 / 56 / 51 / 43 / 34** |
| Trapani (9) | 9 / 9 / 9 / 9 / 1 | 9 / 9 / 9 / 1 / 8 | 1 | **1 / 9 / 9 / 1 / 9** |
| Compilazione (18) | 17 / 18 | 18 / 17 / 17 | 17 / 17 / 18 | **13 / 17 / 17** |
| Checkbox (7-8) | 0 / 7 / 7 | 7 / 7 / 8 | 8 | **2 / 5 / 7** |
| Catanzaro azienda (16) | 4 | 11 / 10 / 7 | 8 | **7 / 11 / 7** |
| Bergamo (2) | 1 / 1 / 0 | 1 / 1 / 1 | 1 | **1 / 1 / 1** |
| CNR IRISS (nuovo) | nessun run concluso | 1 / 10 / 10 | 1 | **1 / 6 / 13** |

**Coerenza per campo:**
- Minervino: dei 61 valori attesi solo 17 sono corretti in tutti e 5 i run, sia su `381ed63` sia
  su `f0c48ba`;
- compilazione: 17 su 18 su `381ed63`, 13 su 18 su `f0c48ba`;
- media Minervino sui 15 run dopo la correzione A: 45,9; 9 run su 15 sopra 48, 4 sotto 35.

**Errati e non attesi** (uguali in tutte le versioni):
- Minervino `p14.s0`: «amministratore unico e rappresentante legale», letterale della fonte,
  contro «rappresentante legale» del gold; 1 run per giro;
- Catanzaro: codice fiscale e partita IVA «IT01234567890», letterali della visura simulata, che
  la mappa vuole da confermare; in un run anche «BA» come CCIAA.

### Dialogo e sicurezza

| Misura | `381ed63` (25 run) | `cd47147` (13) | `f0c48ba` (25) |
|---|---:|---:|---:|
| Bozze esportate | 25 | 13 | 25 |
| Valori del report presenti nel DOCX | 25/25 run | 13/13 | 25/25 |
| Caselle diverse dal report o cambiate fuori report | 0 | 0 | 0 |
| Caselle errate rispetto al gold | 0 | 0 | 0 |
| Dichiarazioni autorizzate | 0 | 0 | 0 |
| Dichiarazioni bloccate (PEC di Trapani nella dichiarazione) | 5 | 1 | 5 |
| Conferme USER registrate / esclusioni / rinvii di condizioni | 33 / 4 / 5 | 22 / 5 / 2 | 31 / 4 / 7 |
| Risposte non accettate al primo tentativo, richieste una volta e poi registrate | 4 | 5 | 3 |
| Di cui rinvii non accettati al primo tentativo (Trapani) | 0 | 1 | 2 |
| Risposte perse definitivamente | 0 | 0 | 0 |
| Domande ripetute senza causa | 0 | 0 | 0 |
| Condizioni rimaste aperte | 0 | 0 | 0 |
| Conferme senza effetto | 9 | 7 | 7 |
| Turni / domande per run | 1-5 / 0-13 | 2-5 / 1-13 | 1-5 / 0-11 |

**Conferme senza effetto:** sono date dall'utente ma non portano scritture per altri gate
legittimi:
- dichiarazione non autorizzata (PEC di Trapani);
- completezza del campo («Cellulare + Telefono» con un solo numero);
- scelta fra valori alternativi rinviata.

**«Valori documentati chiesti» (3 in `cd47147`):**
- 2 sono le scelte fra «Elisa Romano» e «Ing. Elisa Romano» introdotte dalla correzione
  `cd47147`, che per costruzione richiedono una scelta USER;
- 1 è la carica, chiesta dal narratore.

**Rinvii:** non ci sono cicli. In 3 run di Trapani il rinvio del ramo società non è stato
accettato al primo turno e la conferma è stata richiesta una volta con un testo generico («Confermi
che questa situazione si applica (riguarda: …)?»); il secondo rinvio è stato registrato.
- Verdetto reale della guardia sul primo rinvio: pertinente (`SUPPORTED`), ambito ambiguo
  (`AMBIGUOUS`), perché l'ambito della condizione comprende anche la PEC della dichiarazione al
  punto 1, che non era rinviata.
- La correzione A accetta questa combinazione solo per sì/no, non per i rinvi; la protezione
  contro il rinvio parziale di un blocco è voluta (la correzione D era stata annullata per questo).
- Costo: un turno. Gli altri rinvii sono rispettati e non vengono richiesti di nuovo.

## Dove si perdono ancora i valori

Perdite rispetto al gold, per fase (Minervino, 5 run per giro):

| Fase | `381ed63` | `f0c48ba` |
|---|---:|---:|
| Sospensioni del narratore | 47 | 31 |
| Proposte respinte dal validatore | 15 | 32 (24 in un solo run) |
| Rifiuti della guardia | 0 | 0 |
| Altro (rinvio, nessuna proposta, non selezionati) | 6 | 3 |

**1. Output dell'analisi respinti dai validatori.** È variabilità del modello intercettata da
controlli voluti:
- Minervino `f0c48ba-5`: 24 soci respinti con «Ruolo richiesto e ruolo attestato differenti».
  Il modello ha scritto come ruolo attestato il titolo della tabella «Soci» al posto di «socio»;
  negli altri run il ruolo è «socio» e passa;
- checkbox `f0c48ba-1`: 10 caselle respinte, «SOURCE riferita a soggetto/proprietà differenti»,
  lo stesso schema del run 1 di partenza;
- Catanzaro `f0c48ba-2`: 8 respinte, «SOURCE non sostiene questa opzione e polarità»;
- Minervino `381ed63-2`: 9 respinte, citazioni con più marcatori;
- singoli casi: indirizzo completo dove il FORM chiede il Comune.

**2. Sospensioni del narratore non verificabili dal backend.**
- Minervino `381ed63-4`: 32 campi, dubbi «source» che citano la riga SOURCE di un socio.
  - 9 sono stati riesaminati (revisione 2) e sospesi di nuovo dal narratore.
  - 23 citano la riga di un altro socio, quindi non sono riesaminabili.
- Minervino `f0c48ba-4`: 17 campi, «schede dimostrative non verificate», «ruolo aziendale non
  equivale a una designazione».
- Compilazione, checkbox e Catanzaro: sospensioni di applicabilità o di decisione USER **senza
  slot**. Il narratore dice che serve una scelta dell'utente, ma nessuna domanda la raccoglie,
  quindi restano sospese.
  - Compilazione: 5 caselle della tipologia in 7 run su 9 delle due matrici e del giro mirato.

**3. Condizioni ancorate a istruzioni, rinviate dalla policy.**
- Trapani: in 4 run su 11 tra le due matrici e il giro mirato il modello ha ancorato il ramo
  società a «(eliminare le opzioni non pertinenti)». La domanda mostrata era chiara («Confermi
  che la domanda è presentata in qualità di legale rappresentante di una società di
  ingegneria (riguarda: …)?»), ma la policy simulata confronta solo la clausola e rinvia:
  8 valori persi.
- CNR: 3 run su 7 per lo stesso motivo («il proprio interesse alla procedura», due volte «di
  essere invitato alla gara in oggetto»).
- Trapani `381ed63-5`: «IN QUALITA’ DI» con l'apostrofo tipografico non corrisponde alla regola
  della policy («qualit[aà]»), quindi il nome del firmatario va perso.
- La policy è congelata e non è stata modificata: con un utente reale queste perdite
  probabilmente non ci sarebbero, ma non è misurato.

## Nuove correzioni (commit isolati, nessun push)

| Commit | Difetto dimostrato | Meccanismo | Prova |
|---|---|---|---|
| `cd47147` | Minervino, 3 dei 10 run delle due campagne (uno escluso per 402): scelta fra due valori SOURCE dello stesso dato («Elisa Romano» / «Ing. Elisa Romano») presente nel pool ma mai chiesta; bozza con i nomi vuoti e un avviso che non li nominava | La scelta fra alternative documentate (ambigue, in conflitto o sorelle) è sempre chiesta dal backend, come le conferme che sbloccano dati documentati; l'avviso della bozza la nomina. Niente viene scelto o scritto | 7 test (5 falliti prima). Giri reali: chiesta in tutti i 17 casi; in 7 è la domanda imposta dal backend perché il narratore non l'aveva scelta. La policy la rinvia, quindi il punteggio non cambia |
| `87b756f` | Minervino `cd47147-4`: 19 dati sospesi su «IN QUALITÀ DI», la scelta di qualità indicata come blocco, marcati come citazione non ancorata e mai rilasciati dopo la scelta | La clausola FORM dello slot citato come blocco conta come contesto della sospensione. Il rilascio richiede ancora il collegamento verificato (ramo della scelta che copre le condizioni proprie) e la risposta registrata | 3 test (1 fallito prima, 2 di protezione). **Effetto reale** in Minervino `f0c48ba-3`: 33 sospensioni su «IN QUALITÀ DI», presente solo nel pool di domande, legate alla scelta e rilasciate dopo la risposta; 33 valori scritti e uguali al gold (senza la correzione il run avrebbe 18 corretti invece di 51) |
| `f0c48ba` | Minervino `cd47147-5`: un gruppo esclusivo del modello con 3 delle 7 opzioni, respinto come incompleto, occupava la regione; il backend non derivava la scelta di qualità, che non veniva chiesta, e la casella restava vuota | Solo un gruppo valido possiede le sue opzioni | 2 test (1 fallito prima, 1 di protezione). Sullo stato registrato la scelta torna nel pool. Nella matrice finale nessun gruppo respinto si è ripresentato: effetto reale non osservato; la casella è scritta in 5 run su 5 |

**Verifiche:**
- suite backend: 4.209 passati, 8 saltati; Ruff PASS (`suite-f0c48ba.txt`);
- rollback dei tre commit nel worktree di prova: l'albero torna uguale al genitore e i nuovi test
  falliscono sul codice ripristinato (`rollback.txt`).

**Non corretto per scelta:**
- equivalenza singolare/plurale dei ruoli («socio» / «Soci»): tocca la sicurezza di attribuzione
  K3, quindi è una decisione e non una correzione;
- sospensioni «source» senza chiave verificabile.

## Limiti strutturali che richiedono una decisione architetturale

1. **Sospensioni del narratore.** Oggi il backend rilascia solo ciò che sa collegare. Proposta:
   una domanda di conferma per i dati sospesi con dubbio di applicabilità o di decisione USER
   senza slot, e un riesame unico prima dell'export per i dubbi «source», con le prove già
   collegate.
2. **Clausole scelte dal modello.** Derivare la clausola dalla struttura del FORM (opzione o
   sezione che governa le destinazioni), non dalla citazione del modello.
3. **Copertura dell'analisi.** I validatori proteggono la correttezza ma un output incoerente
   costa fino a 26 campi. Proposta: una seconda analisi solo dei segmenti respinti, con il motivo
   del rifiuto.
4. **Equivalenza dei ruoli** (singolare/plurale, titolo di tabella): regola da decidere dentro
   K3.
5. **Rinvio con ambito ambiguo** (Trapani, un turno in più): va deciso come distinguere il rinvio
   dell'intera conferma mostrata da un rinvio parziale, senza togliere la protezione esistente.
6. **Policy simulata a regole:** misura la sicurezza, non la qualità del dialogo con un utente
   reale. Servono prove con utenti o una policy che risponda alla domanda mostrata e non solo
   alla clausola.

## Costi (stima con le tariffe pubbliche; fatturazione non verificata)

| Giro | Run | Chiamate | Token | In cache | Fuori cache | In uscita | USD stimati |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sonda `381ed63` | 1 | 7 | 47.940 | 33.664 | 8.898 | 5.378 | 0,005 |
| Matrice `381ed63` | 25 | 296 | 6.043.368 | 3.836.888 | 1.388.333 | 818.147 | 0,71 |
| Giro mirato `cd47147` | 13 | 182 | 4.037.070 | 2.471.798 | 1.081.920 | 483.352 | 0,46 |
| Matrice `f0c48ba` | 25 | 300 | 5.966.576 | 3.837.656 | 1.314.022 | 814.898 | 0,70 |
| **Totale sessione** | **64** | **785** | **16.094.954** | | | | **1,87** |

- Tutte le 785 risposte sono 200.
- Costo medio per compilazione: circa 0,06 USD per Minervino, 0,02 per Trapani, meno di 0,01 per
  i FORM piccoli.
- La campagna precedente (partenza): 286 chiamate, 5,71 M token, circa 0,79 USD.

## Chiarimento: 28 o 29 run, 21 validi

- **28** è la matrice della partenza; **29** comprende la sonda `bergamo-v3-sonda402-1` (una
  sola chiamata, risposta 402). Le cartelle sono ora 30, con la sonda di oggi.
- «**21 validi**» del rapporto precedente significava «senza risposte 402». Di questi 21, però,
  3 si sono fermati al primo turno per un 429 non recuperato (CNR 3, DGUE 2 e 3).
- **Run conclusivi della partenza: 18** (17 bozze più DGUE 1, FORM non supportato). Le tabelle
  di partenza usano questi.

## Giudizio sull'affidabilità attuale

- **Sicuro.** In 64 run reali nessuna dichiarazione, casella o scelta è stata fatta senza
  decisione valida. I valori scritti sono quelli delle fonti, con due differenze di gold già
  note. Il DOCX corrisponde sempre al report.
- **Più stabile di prima, non ancora stabile.**
  - I rifiuti della guardia, prima causa di perdita alla partenza, sono spariti.
  - Le scelte che il backend lascia all'utente ora vengono chieste.
  - La variabilità residua nasce dall'analisi e dal narratore: in un run su cinque un FORM
    complesso come Minervino perde fra un terzo e metà dei dati, senza errori ma con campi vuoti.
- **Uso consigliato:** bozza da rivedere, con l'avviso dei campi vuoti; non compilazione
  automatica. Le decisioni 1-3 sopra sono il passo necessario prima di dichiarare il sistema
  stabile.
- Nessuna conclusione si basa su un singolo run riuscito.

## Dati

`backend/data/compilation-audit/stabilizzazione-20261030/` (ignorata da Git):
- `esecuzioni/<scenario>-{finale,cd47147,f0c48ba}-<n>/`;
- `AGGREGATO-*.json`, `VERIFICA-*.json`, `giro-*.log`;
- `suite-*.txt`, `rollback.txt`;
- `analisi/verifica_finale.py`.

Worktree del codice:
- `tesi-stab-finale-381ed63`;
- `tesi-stab-fix-cd47147`;
- `tesi-stab-fix-f0c48ba`.
