# Regressione FORMTEXT ed E2E reale Cesano: rapporto PASS/FAIL

19 ottobre 2026 — esperimento `formtext-chiusura-20261019-01`.

**Supporto strutturale FORMTEXT: PASS nei casi verificati. Qualità della nuova
compilazione reale: FAIL. Funzionalità complessiva non dichiarata chiusa.**

Tutti i controlli richiesti sono stati eseguiti prima della nuova prova chat.
Non sono emerse regressioni del parser/writer. La prova reale ha però esposto
un problema distinto: dati aziendali vengono accettati in campi del
sottoscrittore senza dimostrare l'associazione al soggetto/campo. I sette dati
aziendali non sono dichiarati falsi: sono sette scritture che questa prova non
consente di certificare come pertinenti. Non sono state corrette o eliminate
dal DOCX per migliorare il risultato.

[Consegna](<../benchmark ufficiale/formtext-cesano-20261019-01/README.md>),
[controlli dettagliati](benchmarks/2026-10-19-formtext-e2e-checks.json),
[metriche](benchmarks/2026-10-19-formtext-e2e.json),
[elenco preciso dei file](<../benchmark ufficiale/formtext-cesano-20261019-01/FILES-MODIFICATI.json>).

## 1. Controlli e verdetti

| Controllo | Esito | Evidenza e limite |
|---|---|---|
| Riconoscimento dei 20 FORMTEXT reali | PASS | 20 testi + 68 checkbox; nessuna destinazione nativa esclusa fra quei 20 |
| Nomi duplicati, ID e posizioni stabili | PASS | Tutti Testo1; riapertura e serializzazione XML conservano ID/range |
| Scrittura deterministica e ordine degli input | PASS | Tutti i 20 e ciascuno separatamente; input rimescolato, stessi byte |
| Run multipli e proprietà dei campi | PASS | Codici/risultati suddivisi in run, confini e proprietà conservati |
| Malformati, annidati, già compilati e contenuti esclusi | PASS | Negativi permanenti; scrittura lecita altrove non cambia il loro XML |
| Checkbox, firme, stili, prestampato, altre parti | PASS | Confronto XML e ZIP, risultati non richiesti intatti, firme protette |
| Regressione deterministica sui sei documenti | PASS | Cataloghi e DOCX congelati; audit ricalcolati ed export identici |
| Rendering dei sei export precedenti | PASS come conservazione | PDF nuovi, testo e coordinate delle parole identici ai precedenti |
| Leggibilità dei 20 valori sentinella Cesano | PASS | Tutti nel PDF; pagine 1/3 viste, tre pagine, nessun testo fuori pagina |
| Leggibilità dei due CCIAA CRAA | FAIL preesistente | Valori XML in celle di 66/81 twip, non visibili a pagina 4; nessuna regressione |
| E2E reale nuova, stesso modello/prompt/SOURCE | PASS | Una globale nuova, nessun riuso o retry di qualità |
| Export reale: otto valori nelle destinazioni corrette | PASS strutturale | XML, download, ricostruzione e PDF concordano |
| Pertinenza di tutti gli otto valori | FAIL | Una corrispondenza dimostrata, sette associazioni soggetto/campo non dimostrate |
| Recupero dei dati personali SOURCE disponibili | FAIL | Nome e luogo/data di nascita omessi, pur presenti nell'input |
| Checkbox societaria dalla decisione USER | FAIL funzionale | Nessun gruppo proposto, p19.cb0 resta vuota |
| Data UNKNOWN e nessuna scelta/firma inventata | PASS | Data rinviata vuota; tutte le 68 checkbox e firme intatte |
| Suite e Ruff | PASS | 2.682 backend, 258 mirati, Ruff backend |
| Componenti invariati durante E2E | PASS | Nessun file applicativo modificato in questa fase |

Nessun controllo obbligatorio è rimasto ineseguito. Microsoft Word desktop
non è stato usato: il rendering richiesto è stato verificato con LibreOffice
headless. La presenza di un testo nel PDF non basta a valutarne provenienza,
soggetto o applicabilità.

## 2. Test permanenti e riferimenti congelati

[Test generici](../backend/tests/test_docx_formtext.py) già esistenti conservati,
con un'estensione: nei 15 negativi si compila anche un campo lecito distinto e
si confronta l'intero XML escluso. Questo verifica che una scrittura valida
non danneggi campi malformati, annidati, disabilitati, precompilati, bloccati,
oggetti, contenitori complessi e continuazioni di celle unite.

[Nuovi test reali](../backend/tests/test_docx_formtext_regression.py):
sei confronti di catalogo/export congelati, un controllo di nomi/ID/range e
21 prove di scrittura sul Cesano reale: tutti i campi insieme e ciascuno dei
20 separatamente. L'ordine del dizionario dei valori viene rimescolato e
l'export deve rimanere identico. L'XML dei risultati viene letto con un
verificatore dei delimitatori distinto dagli offset del parser.

[Fixture permanenti](../backend/tests/fixtures/formtext-v1/README.md):
sei originali, sei cataloghi, sei export precedenti e sei insiemi di scritture,
con manifest SHA-256. Le aspettative non vengono rigenerate nei test.
Sono 26 file di fixture, non nuovi GOLD fattuali e non entrano nei prompt/KB.

I due file contengono 55 casi parametrizzati, 28 aggiunti in questa fase.
Il difetto già noto PEC Trapani è conservato negli export di riferimento:
uguaglianza dei byte dimostra conservazione, non correttezza di quel dato.

Eseguiti ora:

- 258 test mirati: **22,25 s**, PASS.
- Intera suite backend: **2.682 test, 205,02 s**, PASS.
- Ruff sull'intero backend: PASS.
- Replay senza rete dei sei audit/export e delle due prove writer: PASS.

Le 2.654 prove della fase precedente restano un risultato storico, non
sostituiscono la suite appena eseguita.

## 3. Sei documenti e PDF

| Documento | Candidati attuali | Testi precedenti conservati | Checkbox precedenti | Catalogo / DOCX |
|---|---:|---:|---:|---|
| Minervino | 267 | 54 | 1 | identici |
| Trapani | 115 | 10 | 0 | identici, compreso il difetto PEC |
| Catanzaro | 307 | 13 | 0 | identici |
| Bella | 67 | 4 | 0 | identici |
| CRAA | 51 | 9 XML, 7 fruibili nel PDF | 0 | identici |
| Cesano | 88 | 0 nel vecchio export | 0 | identici alla versione dopo supporto FORMTEXT |

Il riferimento Minervino è il benchmark ufficiale con 55 scritture, non il
precedente replay a 61. Cesano conserva il vecchio export vuoto: il catalogo
confrontato comprende già i 20 nuovi campi, i 68 precedenti restano invariati.

Renderizzati nuovamente i sei DOCX: **9/5/17/4/7/3 pagine**, per 45 pagine.
Tutte le parole e le coordinate coincidono con quelle dei PDF precedenti.
Aggiunta la prova dei 20 sentinella: tre pagine, quindi 48 pagine controllate
prima dell'E2E. Zero parole oltre i bordi.

Ispezione visiva selettiva: Minervino 1, Trapani 1, Catanzaro 1/11, Bella 1,
CRAA 4, Cesano 1; prova dei 20 sentinella 1/3. Non si dichiara un'ispezione
visiva di tutte le 48 pagine. Le due sedi Catanzaro sono leggibili nelle
rispettive celle: il confronto letterale sul testo estratto dava falsi allarmi
per l'intercalazione di etichette di altre colonne. CRAA conserva invece
l'effettiva invisibilità dei due CCIAA. Nessuna correzione effettuata.

## 4. Condizioni della nuova prova reale

Eseguita **dopo** test, replay e rendering, con gate salvato prima dell'invio.
Nuovo progetto isolato `verifica-formtext-v12-cesano`, FORM176; sessione
`226639266b2c4b4a8aaacc2e1f25b65d`, conversazione `conv-436e1eb7ce2d4b6d`,
versione finale 10, stato GENERATED.

Stesso originale SHA-256
`9386c79ef24b99c9e6b70eca9e1dbee5de187febc241f1d87b5ce3787016e795`,
stessi 22 chunk Company/General e stesso scenario del precedente Cesano.
Nessun GOLD, fixture o risultato atteso è stato aggiunto alle SOURCE.

Modello richiesto/restituito `deepseek-flash`; globale thinking enabled/low,
temperatura/max token e tutti gli altri parametri identici. Il trasporto
verifica prima dell'inoltro che corpo fuori dai messaggi e system prompt siano
identici alla richiesta precedente. Fingerprint effettivo comune
`e72d3c7f663d3e1383b00b3884cb4501`. SHA-256 system prompt:
`978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`.

Nel nuovo input sono presenti tutti i 20 ID testuali e le 68 checkbox.
La differenza sperimentale rispetto al vecchio Cesano è l'esposizione dei
FORMTEXT, non una riscrittura del prompt o del modello. Una replica per caso
non costituisce una stima statistica della qualità.

La chat ha chiesto ramo societario e data. Primo turno: conferma della sola
decisione societaria prevista, data UNKNOWN. La negazione “senza raggruppamenti
o consorzi” viene nuovamente interpretata come alternativa dal controllo
esistente; seconda conferma della stessa decisione senza tale costruzione.
Nessuna proprietà personale copiata come USER e nessuna nuova decisione
aggiunta. Poi richiesta ordinaria di bozza parziale, download e refresh.

Il primo accesso browser, dopo il messaggio riprendi, ha trovato i server
isolati spenti: errore conservato prima di qualunque LLM o sessione.
Riavviato lo stesso progetto; non è una seconda generazione né un retry
selettivo. Trace/video finalizzati; dieci GET abortite su mount/reload,
nessun altro errore acquisito nella prova completata.

## 5. Risultato effettivo: otto scritture, non otto dati certificabili

| Fase | Valori |
|---|---:|
| Proposti dalla nuova globale | 8 |
| Grounded secondo i controlli SOURCE correnti | 8 |
| Applicabili dopo la ricevuta societaria | 8 |
| Revisionati | 8 |
| Effettivamente scritti nell'XML e leggibili nel PDF | 8 |
| Corrispondenze SOURCE–soggetto–campo dimostrate | **1** |
| Scritture con corrispondenza soggetto/campo non dimostrata | **7** |
| Dati personali disponibili ma omessi | **3** |
| Testi ancora vuoti | 12 |
| Checkbox nuove / testi USER | 0 / 0 |

**Una scrittura dimostrata:** `p19.ft0`, Mapi Ingegneria S.r.l., nel campo
della società di ingegneria, con SOURCE -43 e decisione USER del ramo.

**Sette scritture da revisionare:**

| Campo | Valore inserito | SOURCE |
|---|---|---|
| p12.ft3 — comune studio | Bari | -52, sede legale società |
| p12.ft4 — via studio | Via Giovanni Amendola | -52, sede legale società |
| p12.ft5 — civico | 172/C | -52, sede legale società |
| p12.ft6 — Partita IVA | IT01234567890 | -43, identificativo aziendale sintetico |
| p12.ft10 — mail | segreteria@mapi-ingegneria.demo | -44, recapito aziendale |
| p12.ft11 — PEC | mapi.ingegneria@pec.demo | -44, recapito aziendale |
| p12.ft12 — telefono | +39 080 000 2040 | -44, recapito aziendale |

Il FORM introduce questi campi nello stesso periodo del sottoscrittore,
insieme a nascita, studio, posizioni previdenziali e iscrizione professionale.
Lo scenario congelato indicava come non dimostrati i recapiti dello studio
personale; le SOURCE non attestano che lo studio/PIVA/recapiti del firmatario
coincidano con quelli societari. La sola partecipazione come società non
aggiunge questa prova. Non sostengo che quei recapiti aziendali siano falsi
o non possano mai essere indicati: **manca qui la prova o conferma della
pertinenza richiesta**, quindi non li conto come sette risultati corretti.

**Tre omissioni:** nome Leonardo Montemurro e luogo/data di nascita, `p12.ft0`,
`p12.ft1`, `p12.ft2`. Le SOURCE -53/-54 sono nell'input e il messaggio
iniziale contiene la scelta del firmatario. Non sono proposte respinte:
la globale non le propone. La spiegazione MODEL invoca `c_firmatario`,
che non esiste nelle condizioni effettivamente proposte; non viene costruita
una domanda valida per acquisire la scelta sul campo. La spiegazione è ancorata
al FORM, non prova di assenza SOURCE né condizione effettiva.

Restano giustamente senza valori INAIL/INPS/INARCASSA e iscrizione professionale
personali non documentati, i tre rami alternativi non scelti e la data rinviata.
Le 68 checkbox sono intatte. La scelta societaria è registrata, ma la globale
propone **zero choice_groups**: la checkbox societaria non viene materializzata.
Il narratore non introduce hold; non è una prova di negativi sugli hold.

## 6. Cause separate dal supporto FORMTEXT

**Fatto osservato:** tutti gli otto fatti scritti sono dichiarati dal modello
come `entity=company`, senza binding; la verifica di binding personale scatta
in [compilation_global.py](../backend/app/compilation_global.py) quando il fatto
è person o il modello fornisce binding_id. Le citazioni dei dati aziendali sono
letterali e valide, ma questo percorso non dimostra il collegamento del fatto
aziendale alla richiesta sul sottoscrittore. La condizione c_soc_ing viene
estesa dal modello anche ai sette campi iniziali; confermarla rende applicabili
le proposte, senza provarne il soggetto.

**Fatto osservato:** il riuso esistente delle generalità riconosce una grammatica
inline di dieci marker con residenza/CF/carica. Il periodo Cesano ha quindici
campi e studio/posizioni previdenziali: nessun gruppo supportato, nessun riuso
e nessuna ricevuta nominativa sul campo. La selezione nel messaggio iniziale
rimane distinta dalle ricevute accettate. Non si è cercato di aggirare il
problema inserendo manualmente una ricevuta.

Omissioni, gruppo checkbox assente e attribuzioni azienda/persona appartengono
a proposta/verifica/dialogo. Il writer non sceglie o cambia il soggetto:
riceve gli otto ID selezionati e li scrive esattamente. Zero errori di ID,
posizione, perdita di testo o struttura FORMTEXT rilevati. Una futura verifica
dell'associazione del soggetto è una fase separata; non è implementata qui.

## 7. Integrità, risorse e conservazione

DOCX reale SHA-256:
`9e7c7302f96c80ba542b3c848c9253907414701f1695f9bb0ece8878afefe2db`.
ZIP/CRC/XML validi; otto risultati esatti, altri 12 vuoti intatti.
Prestampato, bookmark, stili, definizioni dei campi e 68 checkbox conservati.
Altre parti del pacchetto identiche. Download UI e ricostruzione writer
coincidono byte per byte. PDF nuovo di tre pagine, tutti gli otto valori
leggibili; pagine 1/3 viste, nessuna parola fuori pagina. Anche questi controlli
sono distinti dalla correttezza delle sette associazioni.

Dieci chiamate: una globale, quattro router, due guard, tre sintesi.
Input 89.237 token, output 22.454, totale **111.691**; reasoning globale 17.829
incluso nell'output. Globale 88,53 s; tempi HTTP sommati **99,90 s**.
Costo stimato **0,022380 USD**, da uso/cache e tariffa ufficiale congelata nel
benchmark precedente, non fattura. Tutte HTTP200/finish stop; zero retry di
qualità, zero output globale congelato riusato.

In questa fase nessun file applicativo modificato. Conservati 328 altri file
protetti, 632 artefatti precedenti, 29 sessioni live e 285 file storage.
Nel clone le 32 sessioni precedenti sono intatte, una sola nuova. Servizi
isolati arrestati. Nessun commit/push, modifica a modello, prompt, SOURCE,
grounding, API o writer per ottenere un risultato migliore.

I grezzi sono in
`backend/data/compilation-audit/formtext-chiusura-20261019-01/`.
Backup e verifica indipendente nella directory di consegna, con codice,
fixture, chiamate reali, transizioni e browser, senza database privato o chiavi.
La ricostruzione riproduce anche le sette associazioni dubbie: non è una
certificazione della loro correttezza.

## 8. File modificati e stato finale

Modificato in questa richiesta:
`backend/tests/test_docx_formtext.py` — cinque righe di verifica dell'XML escluso.
Aggiunti `backend/tests/test_docx_formtext_regression.py` e i 26 file della
fixture `backend/tests/fixtures/formtext-v1/`. Aggiornati STATUS e relazioni;
aggiunti questo rapporto, due JSON in docs/benchmarks e la consegna separata.
L'elenco completo con hash distingue modifiche, aggiunte pubbliche e script/
acquisizioni locali esclusi da Git.

`backend/app/docx_templates.py` contiene la correzione della fase precedente:
in questa fase è rimasto byte per byte invariato. Le molte altre modifiche
preesistenti nel working tree non sono attribuite a questa richiesta.

**Non dichiaro chiusa la funzionalità complessiva.** Il supporto strutturale dei
20 FORMTEXT supera la regressione; la nuova compilazione reale richiede ancora
una fase separata sulle associazioni soggetto/campo, sul firmatario e sui gruppi
di scelta. Nessuna correzione ulteriore o nuova generazione avviata.
