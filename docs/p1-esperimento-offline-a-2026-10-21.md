# Esperimento offline A su P1 — 21 ottobre 2026

**Esito: la diagnosi P1 così come era formulata è falsificata in parte; P1 non resta
la priorità migliore.** Raggruppare per decisione USER le condizioni prodotte dal
modello aggiunge circa il 2% di scritture corrette quando le risposte USER vengono
registrate, non è sicuro nemmeno con etichette oracolo e non impedisce le scritture
CCIAA. Restano due componenti utili, da trattare separatamente: un veto strutturale
sulle regioni d'opzione (approfondito in
[cciaa-r2-veto-opzioni-2026-10-21.md](cciaa-r2-veto-opzioni-2026-10-21.md)) e la
registrazione delle decisioni già dichiarate nella richiesta iniziale, non misurabile
offline. Per le omissioni P2 ha un margine misurato più ampio.

Nessuna chiamata LLM, nessuna compilazione, nessuna modifica applicativa, nessun
commit o push. Gold, giudizi, baseline V12, candidata V13 e i 90 tentativi sono
rimasti invariati (controllo `find -newer` sul marcatore dell'esperimento).

## Contesto

La revisione tecnica indipendente dello stesso giorno aveva indicato come prima
priorità P1: rendere le decisioni della pratica (partecipante, forma di partecipazione,
firmatario e carica) stato posseduto dal backend, propagare una ricevuta USER a tutte
le condizioni della stessa decisione e bloccare per struttura le regioni d'opzione
non scelte. La revisione attribuiva le perdite di Minervino anche a una
«frammentazione» delle condizioni (da 1 a 12 per risposta) e citava l'effetto del
protocollo USER (98 → 407 testi a parità di codice V12). L'esperimento A verifica
queste affermazioni sui dati registrati, prima di qualsiasi implementazione.

## Metodo

- Preregistrazione `PREREG.md` (SHA256 `20f4ad41…69901973`, 18:27 UTC) e annotazione
  delle opzioni `OPTION-ANNOTATION.json` (SHA256 `de3f1a1d…4f0d0c99`, 18:28 UTC), scritte
  prima di calcolare i risultati. Un solo emendamento, deciso prima dei risultati: la
  regola «titolo» trattava «P. IVA ____» come intestazione maiuscola.
- Dati: 17 risposte globali Minervino (baseline V12, 8 + 8 risposte valide V13), 21
  risposte CRAA, 806 scritture con verdetto documentale (79 DOCX V13 e 3 baseline:
  802 `CORRECT_WRITE`, 4 non dimostrate). Profili di validazione: `V12-puro`
  (solo validatore) e `V13-effettivo` (audit con riuso V13).
- Verità di valutazione: gold Minervino congelato (60 scritture SOURCE) e revisioni
  documentali. La mappa campo→decisione è annotata dall'autore e concorda con il gold
  su 187 campi testuali su 187, ma è stata costruita conoscendone i rami.
- Tassonomia fine, senza fondere le decisioni: firmatario, carica, operatore, una
  decisione per ogni opzione «IN QUALITÀ DI», intestazione della scelta, alternativa
  CCIAA/albo, dichiarazioni di ramo, attestazioni, designazioni, preferenze, luogo e data.

Strategie (gli altri gate restano quelli del sistema):

| Strategia | Significato | Usa il gold? |
|---|---|---|
| S-clause | ogni condizione LLM etichettata con la decisione della sua clausola; equivale al sistema attuale con domande illimitate e utente coerente | annotazione |
| S-conj | condizione soddisfatta solo se lo sono tutte le decisioni del suo ambito | annotazione |
| S-lex-opt | etichetta da parole chiave; «forma di partecipazione» vale come scelta effettuata | no |
| S-lex-cons | come sopra, ma la forma non è soddisfatta perché non indica l'opzione | no |
| S-field | ignora le condizioni LLM: mappa campo→decisione posseduta dal backend | annotazione |

## Risultati

### Scritture corrette recuperabili su Minervino (codice V13 effettivo)

| Gruppo | Possibili | Esportate | S-clause | S-field | S-lex-opt | S-conj | S-lex-cons |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline V12 (1) | 60 | 43 | 44 | 44 | 44 | 35 | 9 |
| Coorte 2 con DOCX (4) | 240 | 219 | 224 | 224 | 224 | 224 | 54 |
| Coorte 1 con DOCX (8) | 480 | 63 | 448 | 448 | 412 | 255 | 68 |
| Coorte 2 senza DOCX (4) | 240 | 0 | 222 | 222 | 213 | 171 | 27 |

- Con il protocollo corretto (coorte 2 e baseline) il dialogo attuale ottiene già 262
  scritture contro un tetto oracolo di 268: circa +2%.
- Nella coorte 1 la condizione di ramo non è mai confermata: il copione risponde
  «Rinvia questo punto» oppure la domanda non arriva. È un problema di cattura e di
  protocollo, non di raggruppamento.
- Le 4 prove senza DOCX falliscono per il narratore (3 troncamenti e un ciclo di
  domande), non per le condizioni.
- Fuori dal tetto, nelle prove con DOCX: 55 proposte corrette respinte dai gate e 9 non
  proposte con V13; con il validatore V12 i respinti salgono a 147 (territorio P2).
- Le condizioni che bloccano le 60 scritture sono da 1 a 3 per risposta, non da 1 a 12.
  Le tre condizioni della baseline corrispondono a tre decisioni distinte: la
  «frammentazione» indicata nella revisione era sbagliata.
- Le proposte autorizzate hanno valori esatti (789), equivalenti (137) o estesi (12, tutti
  `p14.s0` «amministratore unico e rappresentante legale»), contati come corretti.
  Holds del narratore: 9 campi su 716.

### Autorizzazioni improprie in caso controfattuale

16 combinazioni delle quattro decisioni principali per ciascuna delle 17 risposte
(V13 effettivo; con V12 puro le proposte senza condizioni sono 6/17 risposte).

| Strategia | Etichetta o ambito sbagliati | Proposte senza condizioni | Blocchi in eccesso |
|---|---|---|---|
| S-clause | 17/17 risposte | 11/17 | 10/17 |
| S-lex-opt | 16/17 | 11/17 | 11/17 |
| S-conj | 2/17 | 11/17 | 12/17 |
| S-lex-cons | 2/17 | 11/17 | 17/17 |
| S-field | 0 (per costruzione) | 0 | 0 |

Nello scenario reale nessuna strategia scrive posizioni che il gold lascia vuote, né
valori errati. Nelle prove con DOCX i blocchi in eccesso valgono 0 per S-clause e
S-field, 36 per S-lex-opt, 202 per S-conj e 585 per S-lex-cons. Le etichette lessicali
concordano con l'oracolo su 68 condizioni su 76, ma non indicano quale opzione è stata scelta.

### Controesempi

1. La condizione nata dall'opzione «Legale rappresentante di società … di ingegneria»
   (p39) copre in 16 risposte su 17 il blocco societario p40–p53, che richiede anche la
   decisione sull'operatore: una conferma della forma sbloccherebbe denominazione, soci e
   direttore tecnico senza sapere chi partecipa.
2. La stessa condizione copre i recapiti dell'operatore p14–p17 (8 risposte) e, con il
   riuso V13, i dati personali del firmatario (4–6 risposte).
3. Proposte grounded senza condizioni: 59 istanze in 6 risposte con V12 puro, 136 in 11
   con V13 (72 del firmatario). Passano qualunque raggruppamento: è il meccanismo CCIAA.
4. La condizione d'intestazione «IN QUALITÀ DI» della baseline copre solo rami inattivi:
   una ricevuta «scelta effettuata» li autorizzerebbe.
5. S-conj è sicura ma perde 202 scritture corrette, perché gli ambiti delle condizioni
   includono i rami inattivi.

### Blocco strutturale delle opzioni (prima misura)

| Regola | CCIAA bloccate | Scritture testuali corrette bloccate (806) |
|---|---|---:|
| R1, segmento dell'opzione | 0/4 | 0 |
| R2, seguito se l'opzione termina con «:» | 4/4 | 0 |
| R3, seguito sempre (6 paragrafi) | 4/4 | 114 (dati impresa CRAA) |

I 5 casi Cesano bloccati da tutte le regole sono le checkbox FALSE delle opzioni non
scelte, cioè i controlli stessi delle opzioni: vanno esclusi dalla regola. Il seguito
è analizzato nel rapporto dedicato.

## Dipendenza dal gold

Non usano il gold il rilevamento strutturale R1–R3, le etichette lessicali e le
decisioni dello scenario. Dipendono da annotazioni dell'autore la mappa campo→decisione,
S-clause, S-conj, S-field e lo stato scelto/non scelto delle opzioni. Tutte le strategie
assumono una registrazione perfetta delle decisioni, cioè proprio ciò che è fallito nella
coorte 1. La classificazione CCIAA non è univoca nei riferimenti: vedi il rapporto dedicato.

## Giudizio

- Per le omissioni P2 ha il margine misurato più ampio: 55 proposte respinte con V13
  (147 con V12) contro circa 6 recuperate dal raggruppamento. L'effetto di P2 non è
  simulato: la V13 mostra che il margine esiste, non che un metodo generale lo recuperi.
- Il raggruppamento delle condizioni LLM per decisione non va implementato: non è sicuro
  e aggiunge poco.
- Prima di P2 conviene un piccolo veto strutturale di sicurezza, proposto con piano di test
  nel rapporto dedicato. La cattura delle decisioni dalla richiesta iniziale va provata
  separatamente con compilazioni reali e formulazioni naturali.

## Limiti

Un solo documento con gold e un solo scenario; annotazione non indipendente; regole di
equivalenza dei valori decise dall'autore; narratore non simulato; nessuna verifica su
moduli esterni nell'esperimento A; il controfattuale varia solo quattro decisioni.

## Materiali e verifica

- Grezzi, script, preregistrazione e manifest:
  `backend/data/compilation-audit/p1-offline-a-20261021-01/`, con `MANIFEST.sha256`
  (22 file) e `INPUT-MANIFEST.sha256` (240 input letti).
- Backup: [archivio](benchmarks/2026-10-21-p1-offline-a-audit.tar.gz), SHA256
  `b34bb5eb60f274fee9e8911b1ba38f51639969b3ecaa5d064d7153b156451713`
  ([checksum](benchmarks/2026-10-21-p1-offline-a-audit.tar.gz.sha256),
  [descrittore](benchmarks/2026-10-21-p1-offline-a.json)).
- Verifica: due estrazioni indipendenti, manifest e 240 input invariati, riesecuzione degli
  script dall'archivio con 11 output identici byte per byte. La prima riesecuzione aveva
  rilevato un ordine non deterministico dei controesempi (iterazione su insiemi Python):
  corretto solo l'ordinamento, conteggi e regole invariati, annotato nel README del grezzo.
