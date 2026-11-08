# V13 S1 — recupero delle informazioni fattuali: rapporto conclusivo

**Campagne concluse il 21 ottobre 2026. La candidata V13/S1 NON è adottata:**
la decisione spetta all'utente. La baseline V12 resta quella vigente e immutata
([BASELINE-V12.md](../BASELINE-V12.md)). Il rapporto intermedio delle 18:18 è
conservato nell'addendum documentale (vedi «Backup»).

Richiesta originaria: ridurre le 17 omissioni fattuali della baseline senza
nuove scritture indebite; almeno 100 casi mirati, suite completa, regressioni,
poi 45 compilazioni reali su codice congelato. Nessuna adozione automatica.

## Sintesi

| | Coorte 1 | Coorte 2 | Totale |
|---|---:|---:|---:|
| Tentativi reali preregistrati | 45 | 45 | **90** |
| DOCX esportati / senza DOCX | 41 / 4 | 38 / 7 | **79 / 11** |
| Testi scritti (SOURCE + USER) | 216 + 1 | 525 + 1 | 743 |
| Booleani scritti | 0 | 3 (USER) | 3 |
| Scritture non dimostrate | 0 | **4 (CCIAA)** | **4** |
| Omissioni fattuali ingiustificate (riferimento preregistrato) | 62 | 56 | 118 |
| Stesse risposte, codice V12 → V13 (testi) | 98 → 217 | 407 → 526 | **505 → 743** |
| Aggiunte dovute al codice / rimozioni o cambi | 119 / 0 | 119 / 0 | **238 / 0** |
| Chiamate / token | 455 / 5.752.241 | 340 / 5.374.785 | 795 / 11.127.026 |
| USD stimati a tariffa (non fattura) | 1,209172224 | 1,207551330 | 2,416723554 |

Le due coorti usano lo **stesso codice congelato** (120 hash), prompt B0,
modello, parametri, SOURCE, FORM, scenari e budget (massimo quattro risposte
USER). Cambia solo la formulazione/riconoscimento USER delle scelte già
preregistrate: la coorte 1 conteneva un errore di protocollo (vedi sotto).

Le 238 aggiunte attribuibili al codice sono tutte `CORRECT_WRITE` nella
revisione documentale autoriale. Le quattro scritture CCIAA non dimostrate
**non sono introdotte da S1**: le produce anche il codice V12 sulle stesse
risposte. Restano però scritture del sistema candidato, e restano gravi.

## Punto di ripresa dopo l'interruzione di Codex

Già completati da Codex e **non ripetuti**: le due campagne (90 tentativi,
nessuna sostituzione), raccolta, revisione documentale (103 combinazioni
distinte nella coorte 1; 324 nella coorte 2, di cui 59 con firma identica
riusata e 265 nuove), replay appaiati V12/V13 sulle stesse risposte e
ricevute, esecuzione reale del codice `before/` sugli stessi casi (79/79
identici), classificazione degli 11 fallimenti, incidente craa-03,
preservazione finale (`PRESERVAZIONE.json`, PASS alle 19:31).

Incompleti all'interruzione e chiusi in questa sessione, senza compilazioni,
chiamate LLM né modifiche applicative:

- **PDF:** `render_campaign.py` si era fermato sull'asserzione di visibilità
  di craa-03, lasciando otto DOCX della coorte 2 senza PDF (craa-07…10,
  minervino-04/08, trapani-04/05) e `pdf_final.py` falliva. Aggiunto
  `render_remaining.py`, che riusa invariato il renderer congelato della V12 e
  registra gli esiti negativi in `pdf-local-check-FAILED.json` invece di
  interrompersi. Poi rieseguito `pdf_final.py` invariato. I 14.763 file
  preesistenti delle consegne/grezzi V13 e V12 sono rimasti identici, compresi
  i 66 `PDF-FINAL-VERIFICATION.json` già scritti.
- **Confronto finale:** `final_comparison.py` legge solo JSON registrati e
  produce `CONFRONTO-FINALE-V12-V13.json`: effetto del codice, del protocollo e
  delle risposte LLM; 17 destinazioni della baseline; catena causale CCIAA.
- **Backup:** `backup.py`, preparato da Codex e non ancora eseguito, è stato
  eseguito senza modifiche (vedi «Backup»).
- Questo rapporto, README della consegna, relazioni.md e STATUS.md.

## Identità e protocollo

- Candidata: `backend_revision=13` per le nuove sessioni; contratto MODEL e
  prompt globale B0 restano V12. Sessioni senza revisione restano V12.
- 120 hash applicativi in `code-freeze.json` di entrambe le coorti: **120/120
  identici** sia allo snapshot `candidate-code/` sia al working tree corrente
  (ricontrollati in questa chiusura).
- Verifiche deterministiche precedenti, **storiche e non rieseguite qui**:
  3.364 test PASS in 281,92 s, Ruff PASS, 184 nuovi casi; 69 export legacy e 69
  V13 identici; 213 validator storici invariati; sette rifiuti Cesano conservati.
- Coorte 1 (`v13-s1-20261021-01`, avvio 16:04 UTC): la policy USER trattava
  «senza raggruppamenti o consorzi» come alternativa e rinviava «dell'impresa»
  e «di partecipare … come» benché lo scenario li avesse già scelti.
- Coorte 2 (`v13-s1-validation-20261021-02`, preregistrata 16:37 UTC): replica
  completa dei 45 tentativi, non una selezione dei peggiori. Policy corretta e
  verificata senza chiamate su 58 contesti reali della coorte 1; un primo
  preflight fallito prima di qualsiasi inferenza è conservato. **La correzione
  è stata decisa dopo aver visto la coorte 1:** resta un grado di libertà del
  ricercatore, dichiarato e mitigato conservando integralmente la coorte 1.
- V12 baseline: due risposte USER al massimo; V13: quattro. I confronti con le
  tre prove baseline indipendenti non sono quindi causali.

## Tre effetti tenuti separati

### 1. Codice V13, a parità di risposta MODEL e ricevute USER

Replay offline (rete e SQLite vietati) di ogni DOCX esportato: la stessa
risposta globale e lo stesso stato finale vengono validati ed esportati con
profilo V12 e con profilo V13. Il profilo V12 è stato verificato anche
eseguendo davvero il codice `before/` (79/79 audit e DOCX identici).

| Documento | Coorte 1: DOCX, testi V12 → V13 | Coorte 2: DOCX, testi V12 → V13 |
|---|---|---|
| Minervino | 8: 28 → 63 | 4: 191 → 219 |
| Cesano | 9: 0 → 21 | 9: 8 → 32 |
| CRAA | 10: 56 → 66 | 10: 74 → 83 |
| Trapani | 5: 0 → 40 | 5: 53 → 85 |
| Catanzaro | 4: 10 → 14 | 5: 65 → 75 |
| Bella | 5: 4 → 13 | 5: 16 → 32 |
| **Totale** | **41: 98 → 217** | **38: 407 → 526** |

Nessuna rimozione, nessun valore cambiato, checkbox identiche in tutti i 79
casi; fatti, condizioni e binding originari invariati.

Meccanismo delle 238 aggiunte:

| Meccanismo S1 | Coorte 1 | Coorte 2 |
|---|---:|---:|
| Selezione USER esplicita del firmatario a inizio sessione, proprietà etichettate | 84 | 91 |
| Stessa selezione, proprietà letterali (Minervino) | 35 | 23 |
| Record personali tipizzati e verificati (direttore tecnico) | 0 | 4 |
| Continuità dell'operatore grounded condizionato | 0 | 1 |

**233 aggiunte su 238 derivano da un solo meccanismo**, il riconoscimento della
frase preregistrata «Il firmatario scelto per questa domanda è …». I
collegamenti tipizzati DT e la continuità dell'operatore sono dimostrati su
poche scritture reali (4 e 1), solo nella coorte 2.

Sulle tre risposte e ricevute della baseline V12 il codice V13 rende
SOURCE-validabili 17 proposte, ma i DOCX restano identici (54 testi), perché le
vecchie ricevute di revisione non coprono le nuove proposte e il replay non
inventa autorizzazioni.

Limite del confronto: le ricevute USER sono nate in dialoghi V13. Il replay
isola validazione, selezione ed export; non misura come un narratore V12
avrebbe condotto il dialogo con meno proposte validate.

### 2. Protocollo USER, a parità di codice V13

Medie di testi per DOCX esportato, coorte 1 → coorte 2:

| Documento | Esito reale V13 | Stesse risposte con codice V12 | DOCX |
|---|---|---|---|
| Minervino | 7,9 → 54,8 | 3,5 → 47,8 | 8 → 4 |
| Cesano | 2,3 → 3,6 | 0 → 0,9 | 9 → 9 |
| CRAA | 6,6 → 8,3 | 5,6 → 7,4 | 10 → 10 |
| Trapani | 8 → 17 | 0 → 10,6 | 5 → 5 |
| Catanzaro | 3,5 → 15 | 2,5 → 13 | 4 → 5 |
| Bella | 2,6 → 6,4 | 0,8 → 3,2 | 5 → 5 |

L'aumento assoluto 217 → 526 è dovuto **soprattutto alla correzione del
protocollo USER**, non al codice: con il codice V12 sulle stesse risposte si
passa da 98 a 407. Gli `OPEN_AFTER_FACTUAL_VALIDATION` scendono da 531 a 13.
Non è un confronto appaiato: le risposte MODEL e i fallimenti differiscono.

### 3. Risposte LLM

- **11 tentativi senza DOCX**, tutti conservati e nessuno sostituito:

| Tentativo | Causa | Attribuzione |
|---|---|---|
| C1 minervino-08, minervino-09 | Risposta globale troncata (`length`) | MODEL, limite output |
| C1 catanzaro-04, cesano-07 | JSON globale non valido | MODEL |
| C2 minervino-05, minervino-06 | Risposta globale troncata | MODEL, limite output |
| C2 cesano-08 | JSON globale non valido | MODEL |
| C2 minervino-07, -09, -10 | Narratore troncato a 2.048 token al primo turno | Non dimostrata (vedi sotto) |
| C2 minervino-02 | Dialogo senza export: il narratore chiede tre volte se firma l'«amministratore unico» (Luca Ferri) contro la scelta USER; budget esaurito | Narratore e rigidità della policy |

  Per ogni fallimento la pipeline di validazione/riuso dà lo stesso esito con
  codice V12 e V13; nessuna eccezione S1 ne è la causa. I tre troncamenti del
  narratore avvengono **subito dopo l'analisi globale, prima di qualunque
  risposta USER alle domande**, con input di
  16.871–17.631 token, simile ai 16.286–18.303 degli altri primi turni
  Minervino di entrambe le coorti (completamenti normali 271–512 token): con lo
  stesso codice la coorte 1 non ne ha avuti. È variabilità dell'output del
  narratore. Che il maggior numero di proposte validate dalla V13 vi contribuisca
  non è dimostrato né escluso: manca un input narratore V12 equivalente.
  Minervino resta il documento meno affidabile: 2/10 e 6/10 tentativi senza DOCX.
- **Condizioni omesse dal modello:** in 2 risposte CRAA su 20 manca la
  condizione societaria sulla clausola CCIAA (sezione seguente).
- **Variabilità a parità di codice e protocollo:** con codice V12 sulle stesse
  risposte, Minervino coorte 1 va da 0 a 18 testi e Trapani coorte 2 da 9 a 17
  (trapani-03). Una buona risposta MODEL non dimostra una migliore validazione.

## Le 17 omissioni della baseline, destinazione per destinazione

Opportunità = DOCX esportati del documento × destinazioni (Minervino 16, CRAA 1).

| Gruppo | Coorte 1: scritte / opportunità (codice V13; già V12) | Coorte 2 |
|---|---|---|
| Firmatario p12–p14 (9) | 43 / 72 (35; 8) | 31 / 36 (23; 8) |
| Sede operatore p15.s0 | 2 / 8 (0; 2) | 4 / 4 (1; 3) |
| Direttore tecnico p51–p53 (6) | 0 / 48 | 14 / 24 (4; 10) |
| Nome CRAA p5.s0 | 10 / 10 (10; 0) | 9 / 10 (9; 0) |
| **Totale** | **55 / 138 (45; 10)** | **58 / 74 (37; 21)** |

Non scritte: coorte 1, 72 aperte dopo validazione e 11 omissioni ingiustificate;
coorte 2, 7 aperte e 9 omissioni. p14.s0 («in qualità di») è scritta solo in 1
DOCX per coorte. I conteggi descrivono queste prove sul riferimento
preregistrato, che non è un gold universale; non sono percentuali di accuratezza.

## Scritture non dimostrate: le quattro CCIAA

| Tentativo | Destinazione | Valore | Esito PDF |
|---|---|---|---|
| C2 craa-03 | t6.r0.c1 provincia di iscrizione | Bari | cella larga 66 twip |
| C2 craa-03 | t6.r0.c3 numero di iscrizione | 01234560981 | cella 81 twip, **non visibile** |
| C2 craa-04 | t6.r0.c1 | Bari | cella 66 twip |
| C2 craa-04 | t6.r0.c3 | 01234560981 | cella 81 twip, **non visibile** |

Classe `UNDEMONSTRATED_WRITE_GRAVE_REGRESSION`, sottotipo
`FORM_PROCEDURAL_APPLICABILITY_NOT_DEMONSTRATED`. Valore SOURCE e soggetto
corretti, ma la clausola richiede iscrizione per attività coerente e nessuna
attestazione USER la conferma; lo scenario non la autorizza. Il simbolo simile
a una casella resta vuoto.

Catena causale verificata su tutte le 20 risposte CRAA:

1. In craa-03 e craa-04 la risposta globale **non associa alcuna condizione**
   alle due celle. Nelle altre 18 risposte il modello associa `c_societa` (17)
   o `c_company_cciaa` (1), che resta UNKNOWN e blocca la scrittura.
2. Senza condizione il backend accetta le prove fattuali locali
   (`GROUNDED_PROPOSAL`) e il narratore le include nella revisione.
3. Il codice V12 sulle stesse risposte scrive gli stessi quattro valori; lo
   snapshot pre-V13 li riproduce (`incident-craa-03/`, `PAIRED-SNAPSHOT-V12.json`).

Quindi: **non introdotte da S1, non dovute al protocollo USER**, causate dalla
risposta MODEL e da un controllo di applicabilità FORM assente già nella V12.
L'affermazione della baseline «zero scritture non dimostrate» valeva per tre
prove; su 20 risposte CRAA lo stesso difetto si manifesta due volte. La
correzione richiede un intervento separato, non avviato qui. Le due celle
originali sono anche fisicamente troppo strette: i PDF di craa-03/04 sono FAIL.

## Omissioni residue e altri esiti aperti

| Causa delle omissioni ingiustificate | Coorte 1 | Coorte 2 |
|---|---:|---:|
| Catanzaro, proposta di valore MODEL assente | 21 | 29 |
| Catanzaro, prova soggetto/ruolo o binding respinti | 5 | 6 |
| Minervino, validazione respinta (binding, ruolo, altro) | 27 | 11 |
| Minervino, proposta assente o prova SOURCE insufficiente | 4 | 4 |
| Bella, binding/proprietà o ruolo respinti | 5 | 6 |
| **Totale** | **62** | **56** |

Restano anche i limiti noti di composizione letterale (24 e 30, Catanzaro) e
valori composti (11 e 15). Il gruppo checkbox di partecipazione Cesano non è
mai scritto nei 18 DOCX Cesano (la baseline lo scriveva). Il modello propone un
gruppo grounded solo in 6 risposte su 18; anche in quelle il dialogo non
registra una scelta USER del gruppo (per lo più domande di conferma del ramo).
A parità di ricevute le checkbox sono identiche fra V12 e V13: dipende da
risposte MODEL, narratore e protocollo, non dal codice.
L'unica checkbox scritta è p39.cb0 TRUE da scelta USER in tre DOCX Minervino
della coorte 2.

## PDF, integrità e tempi

- **79 PDF, 553 pagine: 77 PASS_WITH_LIMITS, 2 FAIL** (craa-03, craa-04: valore
  CCIAA in celle originali minuscole). Posizioni XML controllate in modo
  indipendente; Word desktop non provato; la visibilità dei token non prova la
  posizione geometrica di ogni valore ripetuto.
- Tempi UI per tentativo: mediana 107,9 s e 111,4 s, massimo 834 s e 858 s.
  Errori browser: richieste annullate durante la navigazione e gli 11 timeout
  dei tentativi falliti.
- Una sola chiamata globale per tentativo (90/90); nessuna ripetizione.

## Preservazione e backup

`PRESERVAZIONE.json` (Codex, 19:31): 13.204 file preesistenti verificati, solo le
modifiche attese (STATUS, relazioni e cinque moduli S1); snapshot e backup V12,
nome neutro, DB live (29 sessioni, 285 file di storage) e cloni intatti; HEAD,
ref e tag invariati.

**Archivio tecnico unico** per entrambe le coorti:
`benchmark ufficiale/v13-s1-20261021-01/audit-completo.tar.gz`, 828.506.206
byte, SHA256 `75d60b93a607462642e23c3c275e0ef8a16c1b2bde5365e622e9142bb4b42cbc`,
14.091 file elencati con hash in `BACKUP-MANIFEST.json`. Comprende consegne e
grezzi delle due coorti (snapshot `before/` e `candidate-code/`, richieste,
risposte, audit, dialoghi, tracce browser, DOCX e PDF, script e log), fixture e
test S1, `pyproject.toml`, `uv.lock` e il verificatore fisico usato dai replay.
Esclusi DB e storage privati dei cloni, chiavi, ambiente, dipendenze Python e
renderer PDF.

`VERIFICA-BACKUP.json`, **PASS**: estrazione indipendente in
`.tools/v13-s1-backup-verification-20261021-01/` con 14.091 hash identici; 120
hash applicativi dello snapshot estratto, importato al posto del working tree;
replay offline con rete e SQLite vietati che ricostruisce esattamente audit e
download del browser (41 + 38 DOCX); misure e classificazioni ricalcolate
identiche; scansione delle credenziali reali superata.

Controllo aggiuntivo di questa chiusura: credenziali cercate anche nei 2.845
membri decompressi dei 90 ZIP delle tracce, pure in base64: **PASS**
(`VERIFICA-SEGRETI-ZIP.json`). I pixel di video e screenshot non sono
scansionabili. Questo rapporto, il rapporto intermedio, README, STATUS e
relazioni sono nel piccolo addendum `consegna-documentale.tar.gz`, con hash in
`CONSEGNA-MANIFEST.json`. `backend/data/` e `.tools/` sono esclusi da Git;
`benchmark ufficiale/` non lo è, ma l'archivio da 828 MB non va aggiunto a un
commit senza una decisione esplicita.

## Limiti delle prove

Revisione documentale autoriale, non annotazione indipendente; SOURCE sintetiche
e documenti già studiati; riferimento preregistrato non gold universale; nessun
test di significatività. Correzione del protocollo decisa dopo la coorte 1.
Budget USER diverso dalla baseline V12. Le ricevute dei replay appaiati nascono
in dialoghi V13. Meccanismi DT e continuità poco esercitati. Nessuna prova su un
bando casuale nuovo in questo intervento. Nessuna percentuale di accuratezza.

## Giudizio conclusivo sulla candidata V13/S1

**A parità di input la V13 domina la V12:** 238 scritture corrette in più, zero
perdite, zero cambi, checkbox e scritture non dimostrate identiche. È un
miglioramento reale e attribuibile al codice, conservativo nel senso richiesto:
non ha introdotto scritture indebite osservate.

**Non risolve però l'obiettivo S1 in modo completo né robusto.** Il guadagno è
concentrato sui dati del firmatario scelto esplicitamente; p14.s0, direttore
tecnico e continuità dell'operatore restano poco recuperati o poco provati.
Restano 62 e 56 omissioni ingiustificate. L'affidabilità E2E è insufficiente su
Minervino, per cause MODEL/narratore non risolte. Soprattutto, **le quattro
scritture CCIAA mostrano che il sistema, V12 come V13, non garantisce zero
scritture non dimostrate** quando il modello omette una condizione FORM.

**Raccomandazione: non adottare automaticamente.** La V13 è adottabile solo per
decisione esplicita dell'utente, come baseline sperimentale conservativa che
sostituisca la V12. Il manifesto dovrebbe riportare il difetto CCIAA come limite
noto ereditato, insieme a fallimenti e omissioni residue. In alternativa si può
mantenere la V12 e trattare prima, in un intervento separato preregistrato, il
controllo di applicabilità FORM. La seconda strada è più prudente se il criterio
di adozione resta «nessuna scrittura non dimostrata osservata».

## Percorsi

- Consegna coorte 1 e materiali finali: `benchmark ufficiale/v13-s1-20261021-01/`
  (`README.md`, `CONFRONTO-FINALE-V12-V13.json`, `PDF-ALL-RESULTS.json`,
  `CONFRONTO-CAMPAGNA.json`, `PAIRED-*.json`, `FALLIMENTI.json`,
  `PRESERVAZIONE.json`, `VERIFICA-BACKUP.json`, `audit-completo.tar.gz`).
- Consegna coorte 2: `benchmark ufficiale/v13-s1-validation-20261021-02/`
  (stessi file di campagna, `incident-craa-03/`, `PROTOCOLLO-prima-preflight.json`).
- Grezzi e script: `backend/data/compilation-audit/v13-s1-20261021-01/` e
  `backend/data/compilation-audit/v13-s1-validation-20261021-02/`.
- Diagnosi prima del codice: `benchmark ufficiale/v13-s1-20261021-01/DIAGNOSI-17-PRIMA.json`.
