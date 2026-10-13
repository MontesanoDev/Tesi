# Relazioni — nuovo motore di compilazione

Registro richiesto dall'utente per ogni prova del nuovo motore. Aggiungere
esperimenti datati senza riscrivere gli esiti precedenti, inclusi i fallimenti.
Le acquisizioni complete rimangono nei bundle di `docs/benchmarks/`; questo
file raccoglie scopo, confronto, risultati e decisioni.

## Protocollo fisso

Fixture dedicata: [Modulo labirinto V1](demo-documents/benchmark-compilazione/v1/README.md),
[Word](demo-documents/benchmark-compilazione/v1/modulo-benchmark.docx),
[gold](demo-documents/benchmark-compilazione/v1/gold.json),
[manifest](demo-documents/benchmark-compilazione/v1/manifest.json).

Il gold è autoriale, indipendente dagli output, escluso dal prompt. Documenti,
fonti e risultati attesi congelati; ogni cambiamento di scenario crea una nuova
versione. Nessun caricamento nella KB locale e nessuna modifica di sessioni.
Il profilo reale serve esclusivamente a scegliere provider/modello.

Per ogni esperimento annotare:

1. Ipotesi e modifica confrontata, commit, versione fixture e hash input.
2. Provider/modello, thinking e budget; numero chiamate/retry e token/tempi.
3. Proposte grezze corrette/omesse/improprie, separate dall'esito dei gate.
4. Revisione dei rami omonimi, soggetto firmatario/direttore, condizioni,
   checkbox, fonte General KB/altro progetto, ambiguità e conflitti.
5. Chiamate USER/generazione DOCX realmente eseguite oppure non misurate.
6. Percorsi dei grezzi/bundle con hash, controlli software e limite residuo.

Valore/citazione corretti non equivalgono ad accettazione semantica. Il confronto
automatico è un ausilio limitato, non un secondo validator di produzione.
Il primo obiettivo è zero proposte fattuali improprie; la copertura va aumentata
senza abbassare provenance, isolamento o gestione dell'applicabilità.

## 11 ottobre 2026 — preparazione della fixture V1

Creato un solo DOCX con 55 posizioni: 44 testuali e 11 checkbox native.
Sette SOURCE: cinque Company KB, una progetto, una General KB distrattore;
una fonte di altro progetto è separata e usata solo nei test di isolamento.

Scenari: campi omonimi in rami alternativi, titoli senza outline Word,
condizioni annidate e ignote, dati societari/professionali, amministratore
distinto dal firmatario, sede coincidente, numero albo con numero estraneo,
RTI non determinato, ambiguità, conflitto, ISO dichiarata solo dal FORM,
firma protetta e spazio non compilabile. Aspettative: 22 valori supportati,
9 NA, 14 mancanti, 6 condizioni da chiarire, 1 ambiguo, 1 conflitto,
1 firma manuale e 1 spazio riservato. Sono obiettivi, non risultati del modello.

Esteso esclusivamente il runner di benchmark con `--fixture`; riusa catalogo,
prompt, schema, chiamata e validator correnti. Nessuna modifica del motore,
RAG, UI, parser, renderer o CompilationSession. La struttura semantica globale
rimane una proposta da discutere, non implementata con questa fixture.

Prima verifica conclusa: **209 test mirati passati** (21 nuovi più 188
regressioni di catalogo/proposta globale), Ruff sui file Python modificati.
Controllati copertura esatta del gold, byte riproducibili, scope, firme/email,
assenza del gold dal prompt e funzionamento del runner senza corpus DB.
Nei test del runner il provider è simulato: non sono risultati di DeepSeek.
Suite completa conclusa: **1.615 test passati in 187,33 s**. Ruff completo,
`--check` della fixture, CLI help, riferimenti Markdown e diff check passati.
Frontend invariato, non rieseguito. Nessuna migrazione/reindicizzazione.
Non considerare i risultati precedenti su domanda-partecipazione come nuove
misure su questo documento.

## 11 ottobre 2026 — baseline reale Labirinto V1

Tre ripetizioni su codice congelato **`5e8cecc`**, fixture V1 e contratto
globale 5 esistente. Nessuna modifica al motore durante o dopo le acquisizioni.
DeepSeek reale, modello `deepseek-flash`, profilo `prova`, thinking disabilitato,
temperatura 0,1. Ogni prova: una chiamata, zero retry/reviewer/USER, timeout 300 s,
massimo output 49.152 token. Input 38.127 caratteri di messaggi, 55 candidate,
sette SOURCE complete. Il profilo salva context_window=32768: non è una misura
del limite effettivo del provider né un nuovo budget deciso dal benchmark.

Originale SHA-256:
`eaa3c2b8e45e147d35766e71f77b90bbb0bdc9a339ee79dd12e6ab007ad9c7ca`.
Input identico byte per byte in tutte le prove:
`d4bb966edcb075f953e8ae2085acf59239f1e28e363005d727aab0a7c94f23ab`.
Request identica:
`1ad0c074cb67a6e44096d6c9717266b045f6ab0e5e3a7b0c0668fd25062274b5`.
Il gold è rimasto fuori dal prompt; il suo snapshot compare solo nell'audit.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Secondi chiamata AI | 10,12 | 12,01 | 9,49 |
| Token input | 11.549 | 11.549 | 11.549 |
| Token output | 3.587 | 4.491 | 3.454 |
| Token totali | 15.136 | 16.040 | 15.003 |
| Token input in cache | 1.536 | 11.392 | 11.392 |
| Assegnazioni grezze | 20 | 32 | 20 |
| Valori/booleani + ID SOURCE corrispondenti al gold | 18/22 | 18/22 | 18/22 |
| Di questi, con grounding locale passato | 12 | 12 | 12 |
| Assegnazioni improprie rispetto al gold | 2 | 14 | 2 |
| Di queste, passate dal solo grounding | 1 | 3 | 1 |
| GROUNDED_PROPOSAL totali, inclusi errori semantici | 13 | 15 | 13 |
| Rifiuti locali | 7 | 17 | 7 |
| Posizioni omesse / ancora non valutate | 35 | 23 | 35 |
| NA proposti correttamente come disposition | 0/9 | 0/9 | 0/9 |
| Condizioni proposte, tutte semantic/unknown | 8 | 8 | 8 |
| ID candidate inventati | 0 | 0 | 0 |

Totale: **3 chiamate, 46.179 token, 31,63 s AI**. Originale invariato in ogni
prova. Nessun errore globale JSON/schema; questo non equivale a successo
semantico. Nessun RESOLVED persistito, zero DOCX generati, zero turni USER:
l'interazione utente e il renderer **non sono stati valutati**.

### Ispezione dei casi critici

| Caso | Osservazione reale | Esito del controllo attuale |
|---|---|---|
| Denominazione, forma, CF, P.IVA, sede legale | Valori e SOURCE corretti in tutte le prove | Grounded; ancora revisione semantica, non RESOLVED |
| PEC, telefono, CCIAA, REA, data iscrizione, codice procedura | Valori documentati proposti correttamente | Grounded |
| Checkbox società di ingegneria | `true` con fatto di tipologia Company KB | Grounded; nessuna scrittura checkbox |
| Quattro checkbox delle altre tipologie | Omesse | Non valutate; non diventano implicitamente `false` |
| Denominazione/forma nel ramo società di ingegneria | Valori corretti in tutte le prove | Rifiutati: applicabilità semantic/unknown |
| Direttore: Giulia Serra, Ingegnere, Ordine di Ancona, albo **5739** | Tutti e quattro corretti nella proposta, sempre | Rifiutati per condizione di ramo non verificata |
| Data abilitazione e organigramma | Nessun valore proposto | Omissione prudente, non verifica completa del requisito |
| Firmatario e carica | Run 2 usa amministratore Paolo Conti e sua carica senza designazione della pratica | Entrambi superano il solo grounding: errori semantici osservati |
| Professionista singolo/studio associato/consorzio | Run 2 riempie otto campi di rami esclusi | Tutti bloccati per condizioni ignote |
| Secondo direttore | Run 2 riusa nome/albo del primo, senza nomina del secondo | Entrambi bloccati |
| Sede operativa «solo se diversa» | Propone indirizzo coincidente in tutte le prove | Bloccato, ma usa semantic/unknown anziché confronto different verificabile |
| Polizza | Sceglie RC-OR-2026-A senza risolvere le due attestazioni discordanti | Grounding letterale passato in tutte le prove, scelta non giustificata |
| ISO prestampata, partecipazione RTI, procura | Nessun valore inventato | Omissioni; non sono decisioni di applicabilità verificate |
| Recapito ambiguo, firma, spazio ufficio | Nessuna assegnazione | Nessuna scelta arbitraria/scrittura; classificazione dei problemi non prodotta |
| Fonte General KB di altra società | Nessun dato utilizzato come valore del richiedente | Distrattore non usato |
| Fonte di altro progetto | Non inviata; la data-esca non compare nell'input | Isolamento verificato dal test software, non da una scelta dell'AI |

La revisione ha ispezionato le assegnazioni grounded, gli scostamenti segnalati
dal confronto e gli ambiti proposti dalle otto condizioni. La corrispondenza
automatica valore/citazione non misura da sola soggetto, ambito o completezza.
La distinzione completa AMBIGUOUS/CONFLICTING non viene valutata dal contratto
sparso: il caso polizza richiede comunque di non scegliere silenziosamente una
sola attestazione. Il gold conserva l'obiettivo di segnalare il conflitto.

### Cosa apprendiamo e cosa rimane da discutere

Il benchmark riproduce il problema dei campi omonimi nei rami esclusi: a input
identico il run 2 produce molti più trasferimenti impropri. Inoltre mostra
false negative conservative: i dati corretti del direttore sono recuperati,
ma il gate non può ancora verificare la condizione semantica. Non basta
ridurre i metadati né aumentare il numero di valori grounded.

Prossima scelta **da discutere prima del codice**: mappa semantica condivisa di
rami/soggetti nella stessa chiamata e accettazione delle condizioni, misurando
se riduce gli errori senza allentare i gate. La gestione delle attestazioni
discordanti è un altro caso di controllo, non corretta durante questa baseline.
Nessuna attivazione nella chat o adapter al renderer è giustificata da questi esiti.

Tre prove restano un campione esplorativo. I tempi non sono confrontabili
direttamente con il modulo reale da 307 posizioni e 51 SOURCE: documento/corpus
sono differenti, nessuna ottimizzazione del motore è stata introdotta qui.
I test software usano provider simulati; solo queste tre acquisizioni sono
misure del provider reale. Nessun costo monetario stimato.

### Acquisizioni e ripetizione

- [Riepilogo e confronto per tutte le 55 posizioni](docs/benchmarks/2026-10-11-labirinto-v1-baseline.json).
- [Bundle completo](docs/benchmarks/2026-10-11-labirinto-v1-audit.tar.gz) e
  [checksum](docs/benchmarks/2026-10-11-labirinto-v1-audit.tar.gz.sha256): tre
  input/schema/request/raw/HTTP/usage/validazioni/confronti, codice e fixture
  congelati, script di analisi e log software. Senza DB/configurazioni/chiavi.
- Bundle: **106 file, 505.698 byte**, SHA-256
  `1c84aeb1c6f612b03b9ac418fc410fbf4a97e9fd9a1977265845648d3fb7ded5`.
  Verificati manifest delle tre prove, byte del bundle, codice congelato,
  assenza di credenziali/DB e assenza del gold dal prompt.
- Grezzi locali: `backend/data/compilation-audit/labirinto-v1-20261011-run{1,2,3}/`,
  `labirinto-v1-20261011-checks/` e `labirinto-v1-20261011-analysis/`.
- Comando di ripetizione nella [guida della fixture](demo-documents/benchmark-compilazione/v1/README.md).

Per il prossimo intervento conservare gli stessi file/hash, cambiare una sola
ipotesi alla volta, ripetere tre volte e aggiungere qui la nuova relazione.
Non sostituire questa baseline o il gold con gli output del tentativo successivo.

## 11 ottobre 2026 — contesto fisico V2, preparazione

Ipotesi: separare riga corrente/intestazioni esplicite e rendere navigabili i
contesti fisici riduce le associazioni improprie fra soggetti e rami. Aggiunti
contesti condivisi riga/blocco, percorso annidato, paragrafi precedenti e
grassetto diretto come osservazione; nessuna inferenza semantica dal backend.
Prompt, schema output, fonti, gold, modello e budget rimangono quelli della
baseline. Il gate locale elimina l'ammissione implicita di ogni prima riga;
gli altri gate non cambiano. Produzione V1, RAG, chat e renderer invariati.

Primo giro software: **228 passati e uno fallito** perché il nuovo catalogo
Catanzaro supera il limite esistente di 200.000 caratteri. Eliminati riferimenti
precedenti ripetuti nei blocchi senza candidate, senza tagliare testo o alzare
limiti. Secondo giro: **229 passati in 11,23 s**, inclusi 20 nuovi casi; Ruff
completo, fixture `--check`, diff check passati. Suite completa: **1.635 passati
in 106,56 s**; benchmark reale da concludere. Il primo Ruff ha segnalato un
ordinamento import, corretto.
Non presentare questi test software come risultati del modello reale.

### Esito reale V2, codice congelato `d14fa9d`

Tre chiamate DeepSeek reali, fixture/input/request identici fra le prove,
prompt/schema/output budget uguali alla baseline. Gold escluso dal prompt;
nessun USER/sessione/export. Tutte e tre arrivano al validator locale.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Secondi AI | 15,34 | 9,48 | 10,16 |
| Token input | 15.092 | 15.092 | 15.092 |
| Token output | 5.850 | 3.350 | 3.616 |
| Valori/booleani e ID SOURCE attesi | 22/22 | 18/22 | 17/22 |
| Di questi, grounding locale superato | 16 | 12 | 11 |
| Valori impropri grezzi | 8 | 1 | 4 |
| Valori impropri grounded | 3 | 1 | 3 |
| NA improprie grezze | 7 | 0 | 0 |

Totale 58.092 token/34,98 s; token input +30,68%, token totali medi +25,80%
contro baseline. Campione piccolo e cache diversa: non prova un aumento
universale di costo/latenza. I cinque dati societari restano corretti nelle
tre prove. Tutti i valori direttore, incluso **5739**, sono proposti, ma ancora
bloccati da applicability unknown. Il run 1 compila tutti i checkbox di tipo,
ma inventa anche ruolo firmatario e partecipazione; sette NA senza supporto.
Le checkbox firmatario passano il grounding locale; nel run 3 passano nome e
carica inferiti. La polizza è scelta arbitrariamente in tutte e tre le prove.
Tutto rimane proposta, zero RESOLVED/scritture.

**Esito non soddisfacente come miglioramento semantico**: la rappresentazione
più ricca non dà un beneficio stabile. Manteniamo la correzione delle prime
righe, eliminiamo la seconda mappa che ripete i riferimenti già nelle tabelle,
e misuriamo un contesto fisico più diretto sul candidate. Nessun allentamento
dei gate o modifica del gold. Riepilogo completo in
`docs/benchmarks/2026-10-11-labirinto-context-v2.json`; grezzi
`backend/data/compilation-audit/context-v2-20261011-*`, da includere nel bundle
finale insieme alla seconda iterazione.

### Seconda iterazione: posizione diretta V3, preparazione

Rimossa la seconda mappa `reading_contexts` e il suo riferimento: `location`
contiene direttamente blocco/tabella/riga del candidate. La struttura canonica
contiene già celle e paragrafi della riga; il percorso annidato si ricostruisce
tramite `parent_cell_id`. Conservati grassetto diretto, contesto precedente e
gate sulle intestazioni esplicite; nessuna nuova inferenza o modifica del prompt.
Input fixture compatto 38.551 caratteri, contro 43.725 V2 e 31.873 baseline:
questa misura non include system prompt e non è una misura di token.
Catalogo Catanzaro nel payload: 166.460 caratteri incluse anchor, Minervino
101.509, entrambi entro il limite. Primo giro V3: **229 mirati in 10,28 s**,
Ruff completo, riproducibilità fixture e diff check passati.

Prima suite completa V3: **1.635 in 111,17 s**. Durante la revisione riprodotto
un errore dei nuovi metadati su XML Word valido con prefisso diverso da `w`:
le ricerche grassetto/header dipendevano dal prefisso. Corrette usando QName
espansi e aggiunta regressione. Stato finale: **230 mirati in 10,00 s**, Ruff,
fixture/diff passati; suite completa finale e benchmark da concludere.

### Esito reale V3, codice congelato `971c5d8`

Tre nuove chiamate reali, medesima fixture V1/hash/fonti/gold, una chiamata per
prova, zero retry/reviewer/USER. Stesso prompt e schema output della baseline;
modello `deepseek-flash`, temperatura 0,1, thinking disabilitato, timeout 300 s,
49.152 token output. Nessuna modifica di codice durante ciascuna serie congelata.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Secondi AI | 10,17 | 9,96 | 10,05 |
| Token input | 13.433 | 13.433 | 13.433 |
| Token output | 3.664 | 3.553 | 3.539 |
| Token totali | 17.097 | 16.986 | 16.972 |
| Token input in cache | 1.536 | 13.184 | 13.184 |
| Valori/booleani e ID SOURCE attesi | 18/22 | 18/22 | 18/22 |
| Di questi, grounding locale superato | 12 | 12 | 12 |
| Valori impropri grezzi | 2 | 1 | 3 |
| Valori impropri grounded | 1 | 1 | 2 |
| NA corrette come disposition | 1 | 1 | 0 |
| NA improprie | 0 | 0 | 0 |
| Posizioni omesse/non valutate | 34 | 35 | 34 |

Input identico nelle tre prove (44.805 caratteri messaggi), SHA-256
`467a3e55a7f8d0570535eda049cb6b42a77b4a5026b98cf9551e99afcd0c7ac9`;
request identica `77790378bf18d0c5532b657479bdcf6618667335ed01bd6c7deac8cd74f23805`.
Fixture/Word invariati, gold fuori dal prompt; nessun ID candidate inventato.
Totale **51.055 token/30,19 s**, media 17.018 token/10,06 s. Rispetto a V2:
−10,99% input, −12,11% token totali medi. Rispetto alla baseline: **+16,31%
input, +10,56% token totali medi**. Questi dati non dimostrano risparmi in
produzione; campione piccolo, cache diversa, nessuna compilazione E2E.
Totale dell'intervento: sei chiamate, **109.147 token/65,17 s** AI.

Revisione dei casi critici:

- Denominazione, forma giuridica, sede legale, CF e PIVA: corretti da SOURCE
  in tutte le sei nuove prove, mai forniti da USER. V3 conferma anche telefono,
  PEC, CCIAA/REA/data e codice procedura. Nessun valore diventa RESOLVED.
- Direttore: Giulia Serra, Ingegnere, Ordine degli Ingegneri di Ancona,
  **5739**, distinti da 8821. Proposte corrette nelle tre V3; restano bloccate
  con denominazione/forma del ramo ingegneria per applicabilità unknown.
- Due V3 usano il confronto `different` fra indirizzi coincidenti: condizione
  false e sede operativa NA. La terza usa semantic/unknown e propone comunque
  l'indirizzo, bloccato. Segnale parziale, non soluzione generale dimostrata.
  Lo scope di tabella proposto nei due confronti include anche la riga recapito:
  la relazione semantica non locale resta da verificare, non è prova di confini.
- Quattro checkbox alternative di tipologia omesse in tutte le V3: non
  interpretarle come false. Nessuna proposta firmatario/carica in V3, ma nel
  run 1 partecipazione singola inferita e bloccata. Le condizioni possono ancora
  essere omesse: 8/8/5 condizioni, completezza mai attestata dal backend.
- Polizza A scelta in tutte le V3 fra attestazioni discordanti, grounding
  superato senza risolvere il contrasto. Terza V3 copia entrambi i recapiti
  alternativi in un unico valore: quote vera, ma campo ambiguo secondo gold.
  I gate letterali non garantiscono unicità/atomicità o risoluzione dei conflitti.
- Nessuna data abilitazione, organigramma o ISO inventata in V3; rami esclusi,
  secondo direttore e procura omessi, non classificati come NA verificata.
  Fonte General KB distrattore non usata per dati aziendali, fonte di altro
  progetto esclusa prima dell'input. Firma protetta e spazio ufficio non scritti.

**Decisione:** mantenere la correzione concreta delle intestazioni e la
posizione diretta V3, che è più semplice della V2 e conserva i dati corretti.
La fedeltà strutturale è verificata; il miglioramento semantico resta **parziale**,
non soddisfa ancora zero assegnazioni improprie. Non promuovere grounded a
RESOLVED, non attivare il prototipo nella chat, non allargare questo task al
renderer o inventare un esito positivo. Il prossimo intervento su applicabilità,
soggetti e conflitti richiede una scelta progettuale discussa separatamente.

Verifiche finali: **230 test mirati in 10,00 s**, **1.636 backend in 105,70 s**,
Ruff completo, fixture `--check`, CLI help e diff check. Le precedenti suite
V2/V3 sono intermedie, con log distinti. Il primo fallimento budget è riportato
dal tool e riassunto qui; non è disponibile un log shell completo di quel giro.
Provider simulati nei test software, DB/storage temporanei; solo le sei
acquisizioni descritte misurano DeepSeek reale. Frontend non toccato/rieseguito.
Originali, sessioni e dati locali dell'applicazione invariati. Nessuna migrazione
o reindicizzazione; nessun DOCX generato, turni USER non misurati.

Riepiloghi [V2](docs/benchmarks/2026-10-11-labirinto-context-v2.json) e
[V3](docs/benchmarks/2026-10-11-labirinto-context-v3.json), confronto di tutte le
55 posizioni per ciascuna prova. [Bundle completo](docs/benchmarks/2026-10-11-labirinto-context-audit.tar.gz)
e [checksum](docs/benchmarks/2026-10-11-labirinto-context-audit.tar.gz.sha256):
sei acquisizioni con input/schema/request/HTTP/raw/usage/validator, codice e
fixture congelati, controlli strutturali, analisi e log senza credenziali/DB.
Grezzi in `backend/data/compilation-audit/context-v{2,3}-20261011-*`.

Controllati anche i nuovi riferimenti Markdown. Il controllo dell'intero
storico incontra 17 riferimenti preesistenti ad audit locali non presenti su
questa macchina: non sono nuovi link rotti e non sono stati alterati o ricreati.

Bundle finale: **219 file, 1.054.963 byte**, SHA-256
`0d5bb111dee1dffceff6c541bc23ff7bfc4a55b97f663d2a0f547619fb7cbf05`.
Verificati tutti i manifest delle sei prove, corrispondenza del codice catturato
ai commit congelati, byte dell'archivio, assenza di credenziali/database e gold
escluso dalle request. Entrambe le iterazioni rimangono recuperabili; nessun push.

## 11 ottobre 2026 — alternative SOURCE, protocollo prima della misura

Causa osservata nelle nove prove reali precedenti: contratto sparse value/NA,
nessun modo esplicito per proporre alternative da chiarire. Polizza scelta
arbitrariamente in tutte le prove V3; terza V3 concatena recapiti alternativi.
Questi errori possono superare grounding letterale. Ipotesi circoscritta:
consentire review grounded nella stessa risposta rende rappresentabile il dubbio
senza una seconda chiamata o nuovi metadati di ingresso.

Contratto sperimentale 6: alternative_fact_ids 2–4, review_kind proposto,
proprietà/soggetto/entity/aspect uguali, valori SOURCE atomici e prove separate.
Nessun valore scritto; condizioni unknown restano unknown. Il backend blocca
anche un value quando altri fatti referenziati e grounded della stessa proprietà
sono già discordanti; non certifica semanticamente conflitto/applicabilità.
Non rileva alternative omesse dall'output o completezza delle fonti considerate.
V1, UI, RAG, parser, renderer, fixture V1/fonti/gold e originali invariati.

Protocollo: tre chiamate reali deepseek-flash sul commit congelato, una per run,
temperatura 0,1, thinking disabilitato, timeout 300 s/49.152 token output,
nessun retry/reviewer/USER. Stesso input nelle tre prove, gold escluso dal prompt.
Confronto con catalogo V3/output V5: non soltanto numero di grounded, ma polizza,
recapiti, soggetti/rami, cinque dati societari, direttore/5739, omissioni e token.
Le nuove metriche review confrontano tipo e ID SOURCE con il gold: non valutano
entailment, completezza o correttezza semantica del conflitto.

Software: primo gruppo 102 passati; successivo test scorer fallito per chiave
fixture errata (`recapito` invece di `corrispondenza`), corretto prima della misura.
Ruff iniziale con righe oltre limite poi corrette. Nessun benchmark reale ancora
avviato in questa fase. Mirati finali 264 passati/11,06 s, Ruff completo/diff
passati; log in `backend/data/compilation-audit/alternatives-v6-20261011-checks/`.
Suite completa in corso; esiti finali e bundle seguiranno senza nascondere prove.

Suite completa pre-benchmark: **1.670 passati in 106,43 s**. Ruff completo,
fixture `--check`, CLI help e diff check passati. Frontend invariato/non eseguito.
Codice e protocollo vengono congelati prima delle tre chiamate; nessuna modifica
prevista durante la serie. I test software usano provider simulati/storage
temporaneo e non sono una misura della qualità di DeepSeek.

### Prima serie V6, commit fd016dd — risultati conservati

Tre chiamate reali senza modifiche durante il benchmark. Tutte distinguono
recapiti e polizze in due alternative SOURCE grounded, nessuna selezione o
concatenazione. Polizza proposta ambiguous/ambiguous/conflicting: il gold è
CONFLICTING ma le fonti non dichiarano esclusività della polizza, quindi il
nome dello stato non è una prova semantica; nessuna aspettativa modificata.
22/22 valori/booleani e ID SOURCE attesi nelle tre prove; 16 passano i gate,
zero RESOLVED/scritture. I quattro checkbox alternativi di tipologia ora sono
proposti false: valore/gold corretti, semantica ancora da verificare.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Secondi AI | 18,06 | 16,06 | 16,64 |
| Token input | 14.082 | 14.082 | 14.082 |
| Token output | 6.501 | 5.840 | 6.141 |
| Token totali | 20.583 | 19.922 | 20.223 |
| Valori impropri grezzi | 0 | 7 | 8 |
| Valori impropri grounded | 0 | 1 | 1 |
| NA improprie grezze | 12 | 5 | 8 |
| Alternative grounded da chiarire | 2 | 2 | 2 |
| Rifiuti locali | 33 | 25 | 29 |
| Omissioni | 3 | 10 | 7 |

Totale 60.728 token/50,76 s. Input SHA
`7d90faf53f844233617d567b75c0d4f864b067cd321c618848884c2cc677177b`,
request `6320902b2397b08ba64dfd55960e86feddde4504cd6a8cd302de05e37ba91bd4`.
Cinque dati societari e direttore/5739 corretti grezzi; direttore bloccato per
condizioni unknown o invalide (run 1 usa same/different con un solo fatto,
rifiutato). Sede coincidente NA grounded in run 1/2. Fonte General distrattore
non usata e fonte esterna assente dall'input, originali invariati.

Regressioni osservate: due run inferiscono il firmatario dall'amministratore,
che passa il grounding letterale ma NON diventa RESOLVED. NA improprie per dati
assenti/condizioni sconosciute e review firmatario con fatti su proprietà diverse
sono rifiutate. L'AI tenta di classificare quasi tutto, aumentando token/rumore.
**Il miglioramento sui due casi alternativi è stabile; il risultato globale non
è ancora accettabile per scrivere.** Nessuna promozione o gate allentato.

Seconda iterazione circoscritta, annunciata prima del codice: istruzione di
emissione sparsa subito all'inizio, prove distinte per value/NA/review e legame
SOURCE fra soggetto e ruolo richiesto. Nessun nuovo campo, parser o checker.
Conservare anche questa prima serie, senza sostituirla con il risultato migliore.
Tre nuove prove a commit congelato, stessi fixture/fonti/schema e budget.

### Seconda serie V6, commit a405f3d — esito finale del passo

Tre nuove chiamate reali, nessuna modifica durante la serie. Input strutturale,
fonti e schema identici alla prima serie; cambia soltanto TASK con i criteri di
emissione all'inizio. Input SHA identico
`7d90faf53f844233617d567b75c0d4f864b067cd321c618848884c2cc677177b`, request
`6260816d628ff7b2f341c567cc68479826f214192e88f3628356f2882ae95351`.
Golden e fixture invariati, nessun dato USER, retry o reviewer.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Secondi AI | 15,32 | 10,59 | 16,44 |
| Token input | 14.390 | 14.390 | 14.390 |
| Token output | 5.682 | 3.644 | 6.049 |
| Token totali | 20.072 | 18.034 | 20.439 |
| Valori/booleani e ID SOURCE attesi | 22/22 | 17/22 | 22/22 |
| Di questi, grounding superato | 16 | 11 | 16 |
| Valori impropri grezzi | 7 | 0 | 7 |
| Valori impropri grounded | 0 | 0 | 1 |
| NA improprie grezze | 2 | 0 | 6 |
| Alternative grounded da chiarire | 2 | 2 | 2 |
| Rifiuti locali | 23 | 6 | 26 |
| Omissioni/non valutati | 13 | 35 | 9 |

Recapiti separati ambiguous e polizze conflicting in tutte le tre prove finali;
quote e ID SOURCE corretti, nessun valore selezionato o concatenato. In tutte
le **sei** acquisizioni sono due review grounded, anche se la prima serie chiama
due volte ambiguous la polizza. Nessun adattamento del gold. Il criterio di
scelta semantica/conflicting vs ambiguous resta da verificare, non basta il nome.

I cinque dati societari, telefono/PEC, CCIAA/REA/data e codice procedura restano
corretti dalle rispettive SOURCE. Direttore Giulia Serra, Ingegnere, Ordine di
Ancona e **5739** corretti grezzi in tutte le sei prove, distinti da 8821; bloccati
con denominazione/forma di ramo da condizioni unknown/invalide. Nel run 2 finale
sono omessi tutti e cinque i checkbox tipologia: per questo 17/22, non perdita
dei dati societari o direttore. Omissioni non significano false/MISSING/NA.
Sede operativa coincidente NA grounded nelle tre finali (5/6 complessive).

Revisione manuale dei grounded: polizza/recapiti non producono più assegnazioni
improprie; tuttavia il run 3 finale propone il firmatario Paolo Conti con sola
quote «Amministratore unico: Paolo Conti.» e supera grounding. Non è prova che
firmi questa domanda: resta semantic_review_required, written_value=null.
Il run 1 propone lo stesso firmatario ma lo vincola a condizione unknown, quindi
rifiutato. Carica e scelte di rappresentanza/partecipazione non provate sono
rifiutate; alcuni NA per condizioni ignote restano impropri e rifiutati.
Nessuna data abilitazione/ISO/organigramma inventata, nessun uso della fonte
General distrattore o di altro progetto. Non dichiarare risolti soggetto/ruolo,
completezza dei rami o associazione semantica perché è migliorato il prompt.

Totale seconda serie: **58.545 token/42,35 s**, media 19.515 token/14,12 s.
Rispetto alla baseline V3: input **+7,12%**, token totali medi **+14,67%**,
tempo medio **+40,32%** nel piccolo campione. Rispetto alla prima V6: meno
output/tempo medi, ma ancora variabilità significativa. Cache diversa, nessuna
misura di risparmio E2E; nessuna compilazione completa. Totale dell'intervento:
**sei chiamate, 119.273 token/93,11 s AI**, zero RESOLVED/scritture/sessioni.

**Decisione:** il passo circoscritto sulle alternative è soddisfacente sulle sei
prove congelate: mantenere il contratto 6 e le prove separate, senza reviewer
aggiuntivi. NON considerare soddisfacente l'intero compilatore: prossimo passo
da discutere è il legame SOURCE soggetto/ruolo e l'applicabilità del ramo prima
di qualsiasi adapter/rendering/attivazione chat. Un backend che vede solo i fatti
scelti dal modello non scopre alternative omesse, non certifica atomicità e non
risolve priorità temporali. I test verificano il gate sui fatti presenti, non
la completezza semantica del corpus.

Verifiche finali realmente eseguite: **264 mirati/10,50 s**, **1.670 backend
completi/106,64 s**, Ruff completo, fixture check, CLI help e diff check. Prima
suite completa 1.670/106,43 s e primi mirati 264/11,06 s conservati distinti.
Test software con provider simulati dove serve, nuove regressioni senza LLM;
solo le sei acquisizioni misurano DeepSeek reale. Frontend invariato/non eseguito.
Nessuna migrazione/reindicizzazione, dati locali/sessioni/originali invariati.

Report [alternative SOURCE](docs/benchmark-alternative-source-2026-10-11.md),
[prima serie](docs/benchmarks/2026-10-11-labirinto-alternatives-v6.json) e
[seconda serie](docs/benchmarks/2026-10-11-labirinto-alternatives-v6b.json).
Grezzi in `backend/data/compilation-audit/alternatives-v6{,b}-20261011-run{1,2,3}/`;
bundle trasferibile e checksum in `docs/benchmarks/2026-10-11-labirinto-alternatives-audit.tar.gz`.
Contiene input/request/schema/raw HTTP/usage/validator, fixture e codice congelati,
analisi per tutte le posizioni e log. Niente credenziali, configurazioni o DB.

Verifica archivio finale: **215 file/1.134.389 byte**, SHA-256
`1ecb3bbcd816aa42d120bf57f01206c9c4785d0ee89d2b00f871a6c258630d63`.
Tutti i sei manifest e snapshot confrontati ai rispettivi commit; sei replay
del validator identici agli audit acquisiti, richieste senza gold, originali
invariati e scansione credenziali/DB superata. Verifica byte per byte del bundle.
Lo script di archivio ha inizialmente usato il nome `catalog_version` al posto
reale di `version`; corretto soltanto nello script di analisi, dopo le prove,
senza modificare motore o risultati. Prima failure fermata prima del bundle.

## 11 ottobre 2026 — legame persona/ruolo, protocollo V7 prima delle prove

Richiesta «ok procedi» sul passo discusso: impedire il salto da persona citata
come amministratore a firmatario del modulo. Nel run `alternatives-v6b-20261011-run3`
`t2.r0.c1` riceve Paolo Conti da «Amministratore unico: Paolo Conti.».
La proprietà «nome del sottoscrittore» è proposta dal modello: il gate V6
controlla presenza del valore, ma non quel ruolo. Resta semantic_review_required,
non è una scrittura; il limite è tuttavia concreto.

Scelta annunciata prima del codice: mappa `bindings` V7, condivisa, massimo 128;
1–2 prove SOURCE per ruolo, `binding_id` obbligatorio dal backend per fatti person.
Ruolo FORM ancorato a riga/header, ultimo paragrafo precedente o outline corrente;
label del campo mantiene il gate locale distinto. Ruoli uguali dopo NFC/casefold/
spazi e coppia esplicita «ruolo: persona» nella SOURCE intera, stesso chunk del
valore. Nessun elenco di ruoli, nomi, campi o fixture nel motore. Niente sinonimi,
join inter-chunk, reviewer/retry o una chiamata per persona. Non risolve applicabilità.
Binding assente/non supportato -> revisione, nessun valore selezionato. Il controllo
non prova completezza del ruolo, entity/property né entailment generale o negazioni
arbitrarie: semantic_review_required rimane obbligatorio. V5/V6 replay storici.

Protocollo congelato: tre acquisizioni reali deepseek-flash con stesso commit,
fixture/fonti/gold Labirinto V1 immutati, gold escluso dai messaggi. Nessuna modifica
durante la serie, USER, ingestion, sessione o DOCX. Confronto con V6b: cinque
valori societari, quattro direttore incluso 5739, alternative corrispondenza/polizza,
firmatario non documentato. Il positivo con ruolo esplicito è test software:
la fixture reale V1 non designa il firmatario. Non confondere assenza dell'errore
in tre campioni con prova di assenza universale. Nessun benchmark E2E.

Prime verifiche realmente eseguite: 109 passati/5,06 s; Ruff segnala una riga
101 caratteri, corretta. Mirati estesi: 294 passati/1 fallito in 12,87 s, perché
un test del vecchio schema non ammetteva bindings; aspettativa aggiornata.
Mirati corretti: 295 passati/13,38 s. Log completi in
`backend/data/compilation-audit/subject-binding-v7-20261011-checks/`.
Ruff, fixture check, CLI help e diff passati; suite completa ancora in corso.
Questo protocollo non anticipa l'esito delle chiamate reali.

Prima suite completa: 1.700 passati/1 fallito in 110,36 s, per la stessa
aspettativa schema raccolta prima della correzione; esecuzione conservata.
Suite corretta: **1.701 passati/106,31 s**, Ruff finale passato. Replay offline
separato della risposta V6b run 3: validator V6 identico al report storico;
controfattuale V7 con bindings vuoto rende il firmatario REVIEW_REQUIRED,
value=null. Non è una nuova risposta AI né una modifica al raw storico.
Codice e protocollo pronti al commit congelato per le tre acquisizioni reali.

### Prima serie reale V7 — esito non soddisfacente per copertura

Commit congelato `97d84fb`, tre chiamate reali, input/request identici, nessuna
modifica durante la serie. 17/16/13 valori e ID SOURCE attesi; 11/11/11 grounded
corretti, nessun valore improprio grounded. Firmatario ancora proposto senza
binding nei run 1/2 ma bloccato; omesso nel run 3. Cinque dati aziendali e due
alternative conservati in tutte le prove. Tutti i direttore binding associano
«Direttore tecnico della società di ingegneria» a «direttore tecnico»: disuguaglianza
letterale conservativa, oltre al blocco applicabilità già presente. Due ordini
professionali includono il numero nel valore; terzo run omette il numero.
Tutte le prove omettono i cinque checkbox tipologia; coincidenza sedi NA soltanto
nel run 1. 58.053 token/39,14 s AI totali, zero USER/retry/scritture.
Questo non è un miglioramento generale del compilatore: copertura regredita.

Seconda iterazione annunciata prima del codice: modifica soltanto le istruzioni
per conservare il contesto FORM completo distinguendolo dal ruolo funzionale
letterale, e per non estendere i binding personali a dati aziendali/checkbox.
Nessun elenco di ruoli/campi, sinonimi, cambio del validator/schema o gate allentato.
La scelta del ruolo resta proposta semantica, non verificata indipendentemente;
un modello potrebbe omettere un qualificatore, limite già dichiarato. Conservare
prima serie e acquisire altre tre prove su nuovo commit, stesso corpus/gold/budget.

Seconda iterazione: 295 mirati passati/12,06 s, Ruff e diff passati prima del
nuovo commit congelato. Nessuna modifica di schema o funzioni di validazione.

### Seconda serie V7 — omissione sistematica dei binding

Commit `c2b30b0`, tre acquisizioni reali congelate: 17/16/17 target attesi,
11/11/11 grounded corretti, zero valori impropri grounded; cinque dati societari
e alternative mantenuti. Direttore/5739 presenti grezzi in tutte le prove;
ordine composto col numero nel secondo run. Binding completamente omessi 3/3,
quindi correttamente bloccati. Firmatario omesso 3/3. 57.112 token/33,98 s AI.
La sola spiegazione ruolo funzionale vs contesto non ha risolto la regressione.

Ultima iterazione bounded annunciata: sostituire il paragrafo verbose sul legame
con istruzioni compatte e un unico esempio JSON di riferimenti collegati,
interamente segnaposto e non tratto dalla fixture. Stessi schema/validator/budget,
nessun fatto o ruolo hardcoded del modulo. Conservare tutti i risultati, tre
nuove acquisizioni congelate, poi fermare questa serie e documentare anche
un eventuale mancato recupero. Nessun passaggio ad applicabilità/rendering.

Suite sul secondo prompt congelato: 1.701 passati/104,52 s. Prima di congelare
l'esempio JSON: 295 mirati passati/11,95 s, Ruff e diff passati. Le funzioni
backend di validazione non sono cambiate nelle due iterazioni del prompt.

### Terza serie V7 — esito finale del passo, con regressione di copertura dichiarata

Commit `5962cb6`, tre nuove acquisizioni reali su codice congelato e input/request
identici; nessuna modifica durante la serie. Il singolo esempio JSON di collegamento
recupera i binding per tutti e quattro i dati del direttore: nome Giulia Serra,
qualifica Ingegnere, Ordine degli Ingegneri di Ancona e **5739**. Ogni proprietà
resta atomica; quote FORM completa e ruolo funzionale letterale separati. Tutti
12 controlli di ruolo risultano literal_match, senza promozione del campo:
applicabilità del ramo resta unknown. Non è una verifica semantica generale.

| Misura | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| Valori/booleani e ID SOURCE attesi su 22 | 17 | 17 | 17 |
| Di questi grounded | 11 | 11 | 11 |
| Valori impropri grounded | 0 | 0 | 0 |
| Proprietà direttore con literal_match | 4 | 4 | 4 |
| Alternative grounded senza valore scelto | 2 | 2 | 2 |
| Rifiuti locali | 7 | 7 | 7 |
| Omissioni/non valutati | 35 | 33 | 32 |
| Secondi AI | 12,0154 | 12,3669 | 12,7965 |
| Token totali | 19.064 | 19.247 | 19.372 |

Cinque dati societari (denominazione/forma/sede/CF/PIVA) sempre corretti da SOURCE
-1, mai USER; recapiti/polizze review con prove individuali sempre conservati.
Il modello omette il firmatario/carica nel run 1 ma li inferisce da amministratore
nei run 2/3: il nuovo gate li lascia REVIEW_REQUIRED con value=null. Questo è
il beneficio concreto; non dichiarare che il modello non tenti più l'inferenza.
Controfattuale offline del vecchio errore conservato separatamente e replay V6
invariato. Condizioni e scope non allentati. Nessun valore RESOLVED/scrivibile.

**Copertura generale regredita:** tutti i cinque checkbox di tipologia sono
omessi, contro due serie V6b con 22 target. Omissione non significa false/NA.
17 valori testuali corretti ma solo 11 grounded perché sei appartengono al ramo
ancora unknown. Sede operativa coincidente: valore improprio proposto nei primi
due run e bloccato, NA grounded soltanto nel terzo. NA ISO improprio nel terzo
rifiutato. Nessuna data abilitazione o certificazione inventata. Nessuna SOURCE
vietata accettata; prima serie aveva un ID inventato -201 rifiutato.

Ultima serie 57.683 token/37,18 s AI, media 19.227,67/12,39 s. Vs V6b: token
medi −1,47%, input +5,15%, tempo −12,22%, ma campione piccolo, cache differente
e copertura inferiore: nessun risparmio E2E o guadagno generale di precisione
certificato. Intervento completo **9 chiamate/172.848 token/110,30 s AI**.
Tutte tre le iterazioni conservate; non selezionate soltanto le prove migliori.

**Decisione:** mantenere la protezione sperimentale e il collegamento esplicito,
ma NON dichiarare pronto l'intero compilatore. Il requisito di ruolo esplicito
positivo funziona nel test software e nel caso reale direttore; mancano verifica
semantica di entity/property/qualificatori, appartenenza e applicabilità.
Un dato riferito ad altra persona nello stesso chunk non è automaticamente
associato correttamente; un'entità mal classificata può eludere il gate personale.
Tutto rimane semantic_review_required e non scrivibile. Falsi negativi su narrativa,
sinonimi, titoli intermedi e prove in chunk diversi dichiarati. Il prossimo
passo da discutere è condizioni/rami/SOURCE e copertura checkbox, senza nuovi
reviewer/batch né attivazione nella chat. Nessun intervento oltre questo passo.

Verifiche finali realmente eseguite: **295 mirati/11,95 s**, **1.701 backend
completi/105,41 s**, Ruff, fixture check, CLI help e diff. Suite intermedie/failure
conservate separatamente, nessuna presentata come nuovo successo. Provider
simulati dove serve nei test software; le nove prove AI usano DeepSeek reale.
Frontend invariato/non eseguito, nessuna migrazione o reindicizzazione; V1/chat/
RAG/parser/renderer/catalogo V3/dati locali/originali invariati. Nove manifest,
snapshot confrontati ai commit e replay identici; catalogo/fonti uguali a V6b,
gold escluso dai messaggi, originali per hash invariati. Nessun push.

[Report persona/ruolo](docs/benchmark-persona-ruolo-2026-10-11.md), JSON per ogni
candidate `docs/benchmarks/2026-10-11-labirinto-subject-binding-v7{,b,c}.json`;
grezzi `backend/data/compilation-audit/subject-binding-v7{,b,c}-20261011-run{1,2,3}/`.
Bundle versionato `docs/benchmarks/2026-10-11-labirinto-subject-binding-audit.tar.gz`,
**361 file/1.904.168 byte**, SHA-256
`e3fff5dca5ebcfd867e2ddc3ff99f2914c35f0f6eca2d7a6019415b199a07c78`.
Verificato byte per byte: nove acquisizioni nuove, una storica usata nel replay,
code/request/schema/HTTP/raw/usage/quote/provenance/validator, fixture/fonti/gold,
analisi/script di riproduzione e log. Nessuna credenziale, DB o configurazione locale.

## 11 ottobre 2026 — Prova occasionale casuale su Trapani Green

Richiesta: non limitare ogni valutazione alla fixture sintetica; ogni tanto
provare un altro bando scelto a caso. Preferenza aggiunta ad AGENTS.md.
Labirinto V1 resta congelato per confronti ripetibili; queste prove supplementari
non sono aggregate ai suoi punteggi e non servono ogni volta. Nessun cambio
di codice applicativo, prompt/schema/validator, V1, chat, parser o renderer.

Pool: originali Minervino di Lecce e Trapani Green; esclusi Labirinto e Catanzaro
già usato estesamente. Estrazione uniforme, seed `2732483673986547453`, scelta
Trapani, nessuna nuova estrazione. Originale
`demo-documents/bandi/trapani-green/originali/manifestazione-interesse.docx`,
SHA-256 `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`:
115 posizioni testuali, zero checkbox individuati. Nessun original modificato,
upload/sessione creato o valore USER. Nessuna misura di copertura delle caselle.

Preflight: Trapani non corrisponde a un progetto locale, quindi il gate restituisce
zero fonti. Nessuna chiamata AI su quell'input. Conservata la scelta, usato
lo stesso DOCX con le KB autorizzate di `prova`: zero fonti di progetto,
13 chunk Company/4 General da tre documenti. Nessun gate role/scope allentato
o documento di altro progetto. Entrambi gli input/setup conservati.
Runner esistente `--fixture`, pacchetto isolato **senza gold**: fields=[] nel
manual-only non sono aspettative di vuoto. Score generato ignorato, nessuna
accuratezza/pass rate. Istruzioni demo non iniettate come SOURCE o decisioni USER.
SOURCE simulate del 2026 e bando storico non dimostrano eleggibilità alla gara.

Una chiamata reale deepseek-flash, commit congelato `eacecbc`, catalogo V3,
contratto V7, thinking off, temperatura 0,1, zero retry. HTTP 200/stop;
25.332 token prompt (2.560 cache hit) + 30 output = **25.362 token**;
**1,4473 s AI**. Risposta grezza completa:

```json
{"version":7,"uncertain_paragraph_ids":[],"conditions":{},"bindings":{},"fields":{},"facts":{}}
```

**Esito negativo:** zero proposte/fatti/condizioni/binding, 115 posizioni
unassigned conservate REVIEW_REQUIRED, zero grounded/RESOLVED/scritture.
Il vuoto nasce nel modello, prima del validator: non sono valori rifiutati.
Nessun troncamento/errore schema/provider segnalato. Il contratto sparso consente
mappe vuote e TASK prescrive omissione senza supporto/applicabilità; non c'è
una restrizione dello schema che imponga fields={}. Non restituita una
motivazione: causa semantica dell'omissione totale non identificata.
Non corretto codice o ripetuta la prova per mascherare l'esito. proposal_audited
e uncertain=[] non provano compilazione/completezza.

Controlli manuali: ramo società di ingegneria `p75.s0`–`p75.s8` tutto omesso,
pur essendo denominazione/indirizzo/PIVA/telefono/PEC nelle SOURCE -43/-44/-30.
La disponibilità non risolve da sola rappresentanza/applicabilità/destinazione,
quindi non etichettati automaticamente falsi negativi certi. Nessun CF aziendale
nel CF personale `p12.s3`, amministratore nel firmatario `p12.s0` o numero 8421
negli albi dichiarante/paesaggista/agronomo `p97.s0`/`p112.s0`/`p113.s0`.
Firma protetta `p175.s0` intatta. Zero falsi positivi in output vuoto non
dimostrano precisione delle associazioni. Nessun DOCX generato.

Eseguiti: manifest, dieci file congelati contro commit, input=request, corpus
canonico identico alle SOURCE congelate, estrazione riprodotta, replay identico,
hash dei due originali invariati. Cinque fingerprint tabelle live prima/dopo
identici: projects/project_files/document_compilations/compilation_sessions/
conversations. Non acquisiti hash preventivi delle altre tabelle, nessun test
chat/browser. Ruff completo e fixture fissa --check passati, diff/link controllati.
Non ripetute suite pytest/frontend, codice e contratti invariati. Una failure
offline confrontava anche metadata non inviati: corretta alla proiezione canonica,
log conservato; acquisizione reale immutata.

[Report](docs/benchmark-trapani-casuale-2026-10-11.md),
[JSON delle posizioni](docs/benchmarks/2026-10-11-trapani-casuale.json).
Grezzi `backend/data/compilation-audit/bando-casuale-20261011/`; bundle
`docs/benchmarks/2026-10-11-trapani-casuale-audit.tar.gz`, **46 file/227.201 byte**,
SHA-256 `dbfced38011073f2c67eede173b30dbab565073945d9009a500a305c259a7886`.
Confrontato byte per byte, include preflight anche senza fonti, prompt/schema/
raw HTTP/usage/audit/codice/analisi/replay/fingerprint/log; esclude DB/config/
credenziali, verificata assenza della chiave reale senza stamparla. Nessun push.

**Valutazione:** migliorata la protezione da assegnazioni improprie nel passo
precedente; non dimostrata migliore completezza. Questa prova rende visibile
un limite fuori dalla fixture. Prossima scelta ancora da discutere:
applicabilità/copertura, includendo output vuoto, senza allentare provenance
o attivare prototipo in chat/renderer. Nessuna correzione durante questo test.

## 11 ottobre 2026 — Trapani: diagnosi e contratto V8 prima dei benchmark

Richiesta autorizzata successiva: risolvere l'output vuoto del bando estratto,
senza rifare RAG, parser, renderer, V1 o UI. Git pulito su `02524d8`.
Prima del codice, quattro chiamate reali sullo stesso input congelato Trapani:

| Prova diagnostica | Risultato | Token totali | Secondi AI |
|---|---|---:|---:|
| Baseline V7 invariata | JSON vuoto | 25.362 | 1,6020 |
| Sola istruzione sull'omissione modificata | JSON vuoto | 25.406 | 1,4228 |
| TASK compatto, stesso schema | Nessun fatto/valore, 13 paragrafi incerti | 23.396 | 1,9511 |
| Risposta diagnostica fuori dal contratto compilazione | Riconosce dati e blocchi, validator la rifiuta | 25.729 | 14,6140 |

L'ultima risposta non è una proposta valida: include anche assenze come valori,
associazioni improprie e più dei 12 link richiesti. Nessun dato promosso o scritto.
Dimostra che il modello legge le SOURCE; la sua spiegazione non costituisce
una verità sulle motivazioni interne delle chiamate precedenti. Non basta
modificare una frase o accorciare il prompt, come mostrano le due ablation.

Limite contrattuale concreto: V7 esige applicabilità verificata per emettere
value; operator=semantic resta unknown nel backend, e i fatti non referenziati
sono vietati. Nel FORM Trapani la società si trova in un ramo di rappresentanza
e il firmatario non è designato nelle SOURCE; la disponibilità aziendale si
perde insieme all'assegnazione. Nessuna evidenza di un problema di retrieval,
troncamento, dati assenti o serializzazione; schema/input/HTTP/raw acquisiti.

Scelta comunicata prima del codice: rappresentare il dato documentato ma ancora
condizionato, senza dichiarare vera la condizione. V8 aggiunge conditional con
fact_id/property, conditions non vuoto e motivo. Stessi gate SOURCE/FORM, ruolo,
tipo, ancore e alternative; source_value diventa solo proposed_value e field.value
resta null/REVIEW_REQUIRED. False/invalide e value con unknown restano rifiuti.
Nessun nuovo corpus, seconda chiamata, retry, loop, scrittura o migrazione.
V5/V6/V7 conservati per replay. Vuoto esplicito empty_proposal, nessuna quota.

Prime verifiche: 59 mirati passati/6,04 s; Ruff segnala due righe lunghe nei
test, corrette. Prima suite mirata: 301 passati/1 fallito per aspettativa schema
ancora V7 in un test storico; corretta alla V8. Mirati finali **302/24,71 s**.
Prima completa, raccolta prima della correzione dell'aspettativa: 1.728 passati/
1 fallito/191,12 s, stessa aspettativa; log conservato. Nuova completa in corso.
Ruff e fixture fissa --check passati. Queste sono prove software, non esiti AI.

Protocollo salvato prima dei benchmark: tre acquisizioni su Trapani originale/
17 SOURCE congelate e tre su Labirinto V1 con gold fuori dal prompt. Congelare
codice, non modificarlo durante la serie, conservare ogni esito. Contare dati
condizionati separatamente da valori grounded e RESOLVED, niente accuracy %
su Trapani senza gold. Non dichiarare risolto prima dei risultati reali.
Acquisizioni in `backend/data/compilation-audit/trapani-diagnosis-20261011/`
e `trapani-conditional-v8-20261011/`, report finale da completare. Nessun push.

Suite completa successiva corretta: **1.729 passati/177,39 s**; Ruff, fixture
--check e diff passati. Frontend invariato/non eseguito. Codice pronto al commit
congelato; i benchmark reali V8 non sono ancora stati eseguiti a questo punto.

### V8: prime sei acquisizioni e cinque diagnosi successive

Codice congelato `c2f3b11`: Trapani senza thinking vuoto in 3/3 (26.176 token
ciascuno, 1,2396/1,1301/0,9642 s). Labirinto: 12/11/11 proposte grounded,
8/7/6 condizionate grounded, 18/17/17 target letterali includendo conditional;
22.946/20.035/20.008 token e 19,2677/11,4844/11,4734 s. Il dato condizionato
resta bloccato, non è un valore compilabile. Prima iterazione insufficiente
per Trapani; nessuna acquisizione eliminata o nuovo sorteggio del bando.

Sul medesimo codice, sole ablation diagnostiche fuori dall'applicazione:

| Diagnosi | Esito | Token | Secondi AI |
|---|---|---:|---:|
| Contesto testuale vicino agli slot | Vuoto | 27.344 | 1,0201 |
| Dato riportato vs validità/autenticità | Vuoto | 26.382 | 1,2720 |
| TASK V8 compatto | 27 proposte, tutte rifiutate; confonde unknown e inventario incerto | 30.167 | 21,2387 |
| TASK compatto chiarito | 19 proposte, cinque PEC condizionate in rami diversi, associazioni troppo larghe | 28.929 | 18,9397 |
| TASK completo invariato + thinking low | Otto proposte aziendali nel ramo ingegneria, sei grounded e due falsi negativi FORM | 35.073 | 46,7679 |

Nessun TASK compatto/contesto aggiunto adottato. Thinking low viene selezionato
prima della singola chiamata; non un retry. Le due citazioni rifiutate nella
prova positiva: accento ASCII anziché Unicode, e label seguita da underscore
che il matcher SOURCE considera parte di una parola. Valori e SOURCE già
corretti, nessuna modifica a dati/fatti per superarli.

Scelta comunicata prima del codice: matcher FORM dedicato conservativo,
normalizzazione Unicode/spazi/case/virgolette, apostrofo terminale dopo vocale
come accento, underscore delimitatore delle label. Prefissi numerici/parole,
riordini e altre proprietà restano vietati; ancore strutturali e matcher SOURCE
invariati. Replay della risposta thinking: otto proposte condizionate grounded,
value=null, zero RESOLVED/scritture. Prima verifica: 86 passati/1 fallito per
quote che terminava a metà placeholder; aggiunto controllo sul bordo del run
underscore. Tentativo suite mirata con nome file inesistente: nessun test,
log conservato; rilancio mediante glob reale. Suite globale: 275/21,48 s.

Protocollo successivo: tre Trapani + tre Labirinto, codice congelato e thinking
low esplicito, nessun cambiamento durante le sei chiamate. Fixture/gold invariati
ed esclusi dal prompt, niente USER/retry/scritture. Misure da acquisire; non
proclamare risolto il comportamento sulla base di una sola risposta positiva.

Verifiche prima del congelamento del secondo protocollo: **321 mirati/19,52 s,
1.748 backend/175,33 s**, Ruff, fixture --check e diff passati. Frontend invariato
e non rieseguito. Nessuna modifica a parser/renderer/RAG/V1 o dati live.

### Seconda serie completa e granularità della destinazione

Sei chiamate congelate `4a0b7a8`, tutte thinking low: Trapani produce 4/5/7
proposte condizionate grounded in 60,1837/74,7100/84,6493 s e
38.157/41.165/45.220 token. Quattro dati stabili nel ramo ingegneria: denominazione,
PIVA, telefono, PEC. Nel secondo compare anche PEC comunicazioni condizionata;
nel terzo proposti tutti i componenti dell'indirizzo, due rifiutati per lunghezza
degli underscore nelle quote FORM. Mancanza di fax rispettata, nessun valore
promosso. Labirinto: 12/13/13 grounded, zero conditional grounded, 17/18/16
target letterali (non entailment), 33.082/34.149/32.491 token e
64,8494/70,6139/62,6596 s. Valori direttore proposti con disposition value e
condizione unknown rimangono rifiutati: il ragionamento non elimina questi
errori né rende la V1 compilabile. Non mascherare questo limite.

Analisi offline: 21 nuove chiamate fin qui, **613.569 token/572,0536 s AI**,
manifest/codice/replay storico e cinque fingerprint live identici. Replay
effettuati con il codice acquisito per ciascuna risposta, senza riscriverne
gli audit; separato il controfattuale del matcher FORM corretto.

Ambiguità concreta del TASK: «Un indirizzo completo resta una singola proprietà»
scoraggia l'estrazione delle componenti quando il FORM ha posizioni distinte.
La traccia acquisita del modello la riconosce; non è una prova SOURCE/validator.
Scelta comunicata prima del codice: granularità determinata dalla destinazione,
componenti letterali distinti se separati nel FORM, dato intero se richiesto intero.
Quote FORM: normalizzare larghezza grafica dei run di almeno due underscore,
con offset al testo originale, escludendo gli underscore interni a identificativi
alfanumerici e quelli singoli. Nessun fuzzy o cambio di corpus/proprietà/numero.
Il precedente test che rifiutava una larghezza diversa è aggiornato a questa
semantica esplicita; aggiunti casi negativi per identificativi e SOURCE invariati.

**327 mirati/25,12 s**, Ruff passato; suite completa in corso. Ultimo protocollo
salvato prima delle chiamate: tre Trapani + un Labirinto thinking low, una Trapani
senza thinking come controllo. Sempre una chiamata/prova, nessun retry/fallback,
codice congelato e zero USER/scritture; non scegliere il risultato migliore.

### Terza serie: otto dati stabili, emissione ancora incoerente

`f2430dd`: Trapani propone gli stessi otto dati corretti in 3/3. Primi due:
otto conditional grounded ciascuno; terzo: otto value con condizione semantic
ritenuta vera dal modello, tutti respinti per unknown backend. Tempi
67,2782/71,2704/69,0587 s; token 41.017/43.219/41.571. Indirizzo corretto e
quote FORM recuperate, ma non dichiarare 3/3 proposte accettate. Labirinto:
13 grounded, zero conditional, 33.324 token/71,2260 s. Controllo senza thinking:
ancora vuoto, 26.238 token/1,2859 s. Nessun dato promosso o scritto.

Suite completa successiva: **1.754 passati/189,09 s**, 327 mirati/25,12 s,
Ruff/fixture/diff passati. Ultimo cambiamento comunicato: solo TASK, esplicitare
che operator=semantic produce SEMPRE unknown nel backend, anche se il modello
lo ritiene vero; per questo richiede conditional. Nessun rilassamento o
riclassificazione nel validator. Stesso protocollo di cinque chiamate congelate
per verificare il solo chiarimento; schema/input/fonti/gold/gate invariati.

### Quarta serie: il compito non esplicita ancora l'ipotesi sul template bianco

`1d31d60`: Trapani thinking 8/0/8 conditional grounded; il run vuoto contiene
sei condizioni ma nessuna assegnazione/fatto. Tempi 62,5701/42,8133/50,2289 s,
41.211/33.994/36.185 token. La traccia acquisita interpreta il template bianco
non intestato al soggetto SOURCE come motivo di omissione: non è assenza di
dati né rifiuto del validator. La traccia è solo diagnosi del modello, non prova
factuale né spiegazione universale delle altre risposte vuote. Labirinto:
12 grounded + sei conditional, 29.991 token/66,1185 s. Senza thinking vuoto,
26.293 token/1,7199 s. **Non dichiarare il bug stabilmente risolto.**

327 mirati/19,58 s e Ruff passati dopo il solo TASK. Scelta comunicata: aggiungere
al JSON `proposal_stage=source_backed_hypotheses` ed esplicitarlo nel TASK.
È il compito del prototipo, non una scelta fattuale del partecipante: dati
SOURCE per destinazioni compatibili possono essere proposti conditional pur
senza intestazione preesistente; uso/rappresentanza restano bloccati. Nessuna
scelta fra soggetti alternativi o elusione del binding persona/ruolo. Un solo
metadata di contesto, FORM/SOURCE/schema/gold/gate invariati. Nuova verifica
congelata stesso protocollo di cinque chiamate, risultati precedenti conservati.

### Quinta serie e separazione finale dei due grounding

`936df7a`, hypothesis-stage: otto dati aziendali corretti e conditional in tutte
le tre risposte; 0/8/9 conditional grounded perché nel primo run la condizione
si appoggia a f_tipo non letterale (accento vs apostrofo SOURCE) e a dimensioni
diverse. Il validator rifiuta il supporto della condizione e di conseguenza
tutti i campi, pur avendo loro SOURCE valide. Tempi 61,5860/66,8716/59,5798 s;
token 37.618/40.609/40.087. Labirinto 12 grounded/quattro conditional,
33.422 token/82,4086 s. Controllo senza thinking ancora vuoto (metriche nel
bundle). Cinque serie conservate; 36 chiamate, 1.151.401 token/1.368,4905 s AI.

Suite completa dopo input stage: **1.754/192,00 s**, mirati 327/28,38 s,
Ruff/fixture passati. Scelta comunicata: in V8 una clausola FORM realmente
grounded resta una condizione sconosciuta quando il supporto SOURCE opzionale
è invalido; l'errore SOURCE resta visibile e NON attesta il risultato. I campi
mantengono tutti i controlli indipendenti sulla propria fonte. Nessuna modifica
a SOURCE matching/RAG/persona/ruolo, e non si ripara f_tipo. same/different,
FORM non grounded e valori SOURCE invalidi restano rifiutati. value+unknown
continua a essere respinto, nessuna riclassificazione. Versioni V2–V7 invariate.

Replay controllato degli stessi raw: 9/8/9 conditional grounded, sempre gli otto
dati del ramo ingegneria; due PEC comunicazioni ulteriori restano bloccate.
Zero RESOLVED/scritture. **335 mirati/26,96 s**, Ruff passato; completa in corso.
Ultimo protocollo: una nuova Trapani e un nuovo Labirinto reali sul commit
congelato, stesso input/TASK della serie appena riletta, sempre una chiamata,
nessun retry/USER/scrittura. Nessun nuovo sorteggio o gold adattato.

### Esito finale del gate e default del solo prototipo

`396e7a6`, due nuove chiamate, input/TASK identici alla serie hypothesis-stage:
Trapani **nove conditional grounded**, gli otto dati aziendali più PEC
comunicazioni, **39.318 token/53,5899 s**. Labirinto **13 grounded + sei
conditional, 17 target letterali**, 32.419 token/62,8407 s. Alternative recapito/
polizza conservate. Limiti: ordine direttore unito al numero e quattro checkbox
di tipologia omessi; grounding non è entailment. Zero RESOLVED/scritture.
Tre replay controllati + nuova chiamata preservano gli otto dati corretti,
senza fax/CF personale/firmatario/altri albi/firma impropri. Originale invariato.

38 nuove chiamate in tutto, **1.223.138 token/1.484,9211 s AI aggregati**:
includono tutte le iterazioni fallite, nessuna cancellata. Non è tempo E2E o
risparmio di token. Ultima suite: **1.762/158,63 s**, 335 mirati/26,96 s;
Ruff/fixture, manifest/codice/replay/fingerprint passati. Frontend invariato.

Scelta comunicata: SOLO prototipo/runner thinking low predefinito, flag esplicito
--no-thinking per controlli. Fonte del cambio: le risposte senza ragionamento
restano vuote; qualità prima della latenza in questa fase. Una chiamata comunque,
nessun fallback dopo vuoto né modifica a profilo UI/V1. Le richieste prodotte dal
nuovo default sono identiche alle ultime due reali: confronto salvato, nessuna
nuova API necessaria per lo stesso body. Dopo default: **338 mirati/14,08 s**,
Ruff passato; ultima completa in corso. Report e bundle da completare, nessun push.

Verifica finale dopo default: **1.765 backend/110,03 s**, **338 mirati/14,08 s**,
Ruff/fixture/replay/manifest/codice/richieste equivalenti/fingerprint passati.
Nessuna migrazione/reindicizzazione o verifica frontend necessaria/eseguita.
[Report finale](docs/diagnosi-trapani-compilazione-2026-10-11.md) e
[JSON completo](docs/benchmarks/2026-10-11-trapani-diagnosis.json).
Bundle `docs/benchmarks/2026-10-11-trapani-diagnosis-audit.tar.gz`:
**1.211 file/7.976.279 byte**, SHA-256
`7035ffc9c7701e69fe5ec9c08a5616c76d6ad10ff2df7ae25991cd2ca3a66d2b`.
Tutti i 38 raw nuovi, tre storici per replay, codice/protocolli/schema/input/
HTTP/usage/validazioni/fixture/replay/manual review/log/default patch; verificato
byte per byte, nessun DB/config/cache/chiave API. Risultati grezzi anche nel data
locale ignorato. Commit incrementali, nessun push.

Passo circoscritto chiuso: dati utili non persi con applicabilità sconosciuta.
Restano revisione semantica indipendente, verifica delle condizioni e copertura
prima di adapter/attivazione in chat; non considerarli già implementati e non
confondere proposed_value con campo RESOLVED o DOCX generato.

Controllo finale dei link: la scansione dell'intero storico segnala un riferimento
locale già presente su `02524d8` a global-subject-conditions-20261008/report.md,
non disponibile in questa copia. Storico lasciato intatto; nuovi riferimenti
verificati. [Esito documentale/bundle](docs/benchmarks/2026-10-11-trapani-final-checks.json)
versionato separatamente dopo il packaging, senza riscrivere l'archivio dei raw.

## 12 ottobre 2026 — tutti e tre i bandi, nessuna modifica al motore

Richiesta: tentare tutti e tre i moduli reali e valutarne l’affidabilità,
rimandando checkbox e ordine professionale. Nessun sorteggio: Catanzaro,
Minervino e Trapani sono il pool completo richiesto. Non è il benchmark con
gold Labirinto V1 e non dichiariamo accuratezza percentuale.

Codice congelato `6a33c85`, V8/catalogo V3, deepseek-flash reale, thinking low,
una chiamata per prova, nessun retry automatico. Stesso corpus autorizzato
`prova`: 17 chunk SOURCE (13 Company/4 General), nessuna fonte progetto.
Corpus piccolo completo, nessuna ricerca FTS/Qdrant. Gold/istruzioni demo
fuori dal prompt; placeholder vuoto del runner non usato per misurare qualità.

Primo protocollo: nove chiamate, tre giri con massimo tre concorrenti.
Dopo due timeout, protocollo separato: un controllo seriale per ciascun bando,
stessi body e timeout 300 s. Tutti i tentativi conservati, nessuna sostituzione.
Quattro richieste identiche per documento, nessun cambio durante le prove.

| Bando | Prova | Fase | Esito | Raw | Conditional grounded | Omesse | Secondi | Token osservati |
|---|---:|---|---|---:|---:|---:|---:|---:|
| catanzaro | 1 | concorrente | timeout | — | — | — | 300.13 | non acquisiti |
| catanzaro | 2 | concorrente | output completo | 15 | 11 | 292 | 124.90 | 93870 |
| catanzaro | 3 | concorrente | output completo | 14 | 10 | 293 | 81.15 | 84127 |
| catanzaro | 4 | seriale | output completo | 14 | 9 | 293 | 106.96 | 89097 |
| minervino | 1 | concorrente | output completo | 4 | 4 | 263 | 39.74 | 47027 |
| minervino | 2 | concorrente | output completo | 8 | 8 | 259 | 63.43 | 54608 |
| minervino | 3 | concorrente | output completo | 7 | 7 | 260 | 50.01 | 50579 |
| minervino | 4 | seriale | output completo | 21 | 16 | 246 | 109.99 | 62753 |
| trapani | 1 | concorrente | timeout | — | — | — | 300.10 | non acquisiti |
| trapani | 2 | concorrente | output completo | 9 | 9 | 106 | 57.87 | 39308 |
| trapani | 3 | concorrente | output completo | 9 | 9 | 106 | 62.08 | 39727 |
| trapani | 4 | seriale | output completo | 8 | 8 | 107 | 52.62 | 36823 |

Dieci output completi (stop), due timeout senza output/usage completi.
**597.919 token osservati**, più eventuale consumo non acquisito dei timeout.
1.348,98 s per chiamata cumulati, 748,75 s per le dieci complete; non durata
E2E a causa della concorrenza. Tre seriali riuscite non dimostrano che questa
fosse la causa dei due timeout: ordine/cache/provider/rete non controllati.

109 record emessi e ispezionati: **91 conditional / REVIEW_REQUIRED**,
17 proposte personali bloccate e una NA rifiutata. Zero RESOLVED, USER,
sessioni create o Word generati; `value`/`written_value` null. 689 candidate
strutturali unici non sono 689 dati obbligatori. Omissione non prova NA/MISSING.

- Catanzaro: nelle tre risposte complete su quattro tentativi i cinque dati
  operatore/forma/sede/CF/PIVA sono conservati. Quattro dati del direttore
  proposti ma bloccati: literal role pair troppo restrittiva nelle prove 2/3,
  quote non contigua nella quarta. Sede operativa con clausola locale omessa
  nelle prove 2/3; NA invalida respinta nella quarta.
- Minervino: 4/8/7/16 ipotesi conservate. Nella prova 2 `p42.s2` riceve telefono
  al posto del civico, `p42.s3` e-mail al posto del telefono, `p42.s4` PEC al
  posto dell’e-mail ordinaria. SOURCE valide non provano la destinazione:
  quote FORM locale al paragrafo, non vincolata alla singola porzione/slot.
  Prova seriale separa meglio i recapiti ma non risolve eredità del ruolo.
- Trapani: gli stessi otto dati aziendali nelle tre risposte complete su quattro
  tentativi. PEC comunicazioni aggiuntiva solo nelle prove 2/3. Nessuna
  applicabilità approvata; firmatario/CF personale/fax/altri albi non inventati.

Giudizio: recupero dati utile ma **affidabilità insufficiente per compilazione
completa automatica**, anche ignorando checkbox/ordine. Grounding locale non
è entailment, destinazione corretta o autorizzazione alla scrittura. Nessun
bug corretto durante questo test, nessun gold adattato ai risultati.

Verifiche realmente eseguite: **314 mirati / 14,42 s**, Ruff backend, fixture
Labirinto --check, **otto verifiche fixture Catanzaro / 0,583 s**, dodici manifest,
dieci replay esatti e snapshot codice, identità body/corpus, originali, scan
credenziale, archivio byte per byte e diff/link. Completa/frontend non ripetuti:
codice applicativo invariato. Test software separati dalla qualità DeepSeek.
Conservate failure iniziale di ispezione audit senza API e dieci errori di stile
nel lint esplicito degli helper locali ignorati; backend applicativo Ruff passa.

Integrità: originali, sessioni/revisioni, conversazioni/turni, progetti/file,
profili e documenti/chunk globali invariati. Il fingerprint dell’intero DB
**non è invariato**: derivati/FTS/sequenze cambiano. Osservato reload del worker
live durante creazione helper .py nel backend; startup ricostruisce indici e
artefatti, coerente ma senza traccia SQL per attribuzione esclusiva. Nessun
ripristino/manual write DB. Corpus sperimentale già congelato e immutato.
Per successive acquisizioni helper fuori dal percorso sorvegliato live.

[Report](docs/benchmark-tre-bandi-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-tre-bandi.json).
Bundle `docs/benchmarks/2026-10-12-tre-bandi-audit.tar.gz`: **333 file, 3.395.750
byte**, SHA-256 `70df9a7b8bd489383d62469aa7a61769e322ffc7135d5ab4939d7eb5e07f5d69`.
Protocolli/input/originali/code/prompt/schema/raw/HTTP/usage/validazioni/manual
review/replay/log e failure inclusi; niente DB/config privata/chiave/bytecode.
Grezzi anche in `backend/data/compilation-audit/tre-bandi-20261011/`.
Commit risultati autorizzato, nessun push. Nessuna migrazione/reindicizzazione.

Prossimo passo **da discutere prima del codice**: partire dalla destinazione
sbagliata Minervino, vincolare proprietà alla singola posizione, conservare
ruolo lungo il blocco e verificare condizioni prima dell’adapter. Non attivare
ancora il prototipo nella chat. Conservare la baseline e tutte le prove negative.

[Verifiche finali documentali](docs/benchmarks/2026-10-12-tre-bandi-final-checks.json):
JSON coerente con dodici acquisizioni, hash originali/bundle e inventario passati.
Conservata la failure del checker che inizialmente assumeva REVIEW_REQUIRED anche
per righe timeout NOT_VALIDATED e una NA rifiutata; corretta soltanto la verifica,
nessun nuovo output AI o cambio al motore.

## 12 ottobre 2026 — ancoraggio delle destinazioni, protocollo prima delle prove

Passo autorizzato: correggere lo slittamento Minervino mantenendo una chiamata.
Catalogo V4 riusa text_with_fields del parser e aggiunge slot_context bounded
120 caratteri per lato fra placeholder adiacenti. Output V9: quote del field
inline con il suo solo marker e testo locale, poi ripristino del placeholder e
validator esistenti. Etichette prima/dopo supportate. Nessuna modifica a SOURCE,
ruoli/condizioni/checkbox, parser generale, renderer, V1/chat/UI.

La posizione della quote non approva semanticamente la proprietà: test esplicito
con quote del civico e fatto telefono rimane review-only/non scrivibile. Nessuna
promozione RESOLVED. Dieci replay storici V8 identici; versioni precedenti
conservate. 340 mirati/14,70 s, Ruff/fixture passati; completa backend in corso.
Prima esecuzione: 336 passati/due failure su Minervino (sentinelle degli oggetti
Word nel parser, assenti nel testo visibile del catalogo). Corretto ripristino
dal placeholder del parser, non dagli offset del testo visibile; nessuna
modifica al parser. Seconda 338/15,24 s; finale 340 include due nuovi test.
Ruff iniziale con un import fuori ordine corretto. Log grezzi conservati.

Protocollo preregistrato: tre chiamate reali Minervino, tre Labirinto V1 e un
controllo Catanzaro, seriali, deepseek-flash/thinking low, timeout 300 s.
Fonti identiche alla serie tre-bandi e fixture/gold Labirinto invariati, gold
fuori dal prompt. Codice congelato prima delle chiamate; zero retry/USER/sessioni/
scritture. Tutti gli esiti, inclusi timeout e omissioni, conservati.

Criteri: nessuno slittamento nei recapiti Minervino, copertura della riga con
sei slot osservata e non soltanto omissione di tutti i recapiti; conservazione
dei cinque dati societari e dei target benchmark senza abbassare i gate.
Token/tempi confrontati dichiarando cache/ordine/servizio non controllati.
Nessuna accuratezza percentuale su Minervino/Catanzaro privi di gold.
Questo passo non conclude verifica di applicabilità/ruoli né autorizza export.
Grezzi in backend/data/compilation-audit/slot-anchors-20261012/. Esiti da aggiungere
dopo la serie, senza cambiare il codice durante le acquisizioni. Nessun push.

Prima delle API: **1.791 backend/113,10 s passati**. Prima completa 1.790 passati
e una assertion storica sulla versione catalogo 3 aggiornata a 4; nessuna
regola di isolamento indebolita. 47 test contesto/slot passati, undicesimo replay
Labirinto storico identico. Frontend invariato/non eseguito. Codice pronto
al congelamento per le sette acquisizioni preregistrate.

## 12 ottobre 2026 — destinazioni V9, tutte le sette acquisizioni

Protocollo precedente eseguito senza modifiche applicative durante la serie:
`d86953b`, deepseek-flash/thinking low, seriale, timeout 300 s, una chiamata
per documento/prova, nessun retry. Minervino/Catanzaro: stessi 17 SOURCE congelati
(13 Company/4 General); Labirinto: sette fonti V1, gold congelato fuori dal prompt.
Nessun sorteggio: due regressioni mirate, controllo Catanzaro concordato.

| Ordine | Caso/prova | Record | Grounded senza condizioni (incl. NA) | Valori conditional | Omissioni | Secondi AI | Token |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Minervino 1 | 14 | 0 | 9 | 253 | 104,61 | 70.335 |
| 2 | Labirinto 1 | 21 | 13 | 6 | 34 | 58,55 | 30.814 |
| 3 | Minervino 2 | 11 | 0 | 11 | 256 | 69,46 | 60.822 |
| 4 | Labirinto 2 | 21 | 13 | 6 | 34 | 57,92 | 30.712 |
| 5 | Minervino 3 | 11 | 0 | 9 | 256 | 110,31 | 70.731 |
| 6 | Labirinto 3 | 21 | 13 | 6 | 34 | 49,63 | 28.824 |
| 7 | Catanzaro 1 | 7 | 7 | 0 | 300 | 54,54 | 75.894 |

Tutte complete HTTP 200/stop; zero timeout, zero nuovi tentativi selettivi.
106 record: 89 ipotesi di valore con grounding SOURCE (42 senza condizioni +47
conditional), quattro NA locali, sei review alternative e sette proposte
personali bloccate. Zero RESOLVED, sessioni, USER o scritture DOCX.
505,02 s AI sommati e 368.132 token osservati, non durata E2E. Input più grande
(Minervino 45.964 vs39.792, Labirinto 16.623 vs16.249, Catanzaro 65.657 vs64.485).
Nessun risparmio input o miglioramento causale di latenza dimostrato: cache,
output/ragionamento/copertura differenti. Nessuna spesa monetaria completa stimata.

Minervino: `p42.s0` provincia BA, `s1` via Giovanni Amendola, `s2` civico 172/C,
`s3` telefono, `s4` e-mail, `s5` PEC nelle destinazioni corrette. Sei/tre/sei
proposte nella riga: seconda prova omette provincia/via/civico, ma tutti i tre
recapiti corretti in 3/3. Nessuno slittamento osservato; vecchia prova 2 ne aveva
tre, vecchia seriale 4 già corretta. Non è una garanzia per ogni futura chiamata.
Due proposte indirizzo completo in `p41.s1` richiedono revisione di granularità.
Sette proposte personali bloccate dai gate invariati, direttore omesso in prova 2.

Failure semantica residua acquisita: `p16.s0` prova 2 propone correttamente
l'e-mail ordinaria, ma cita `[[p16.s0]] P.E.C.` (label dello spazio successivo;
label e-mail nel paragrafo precedente). Marker corretto non implica proprietà
correttamente dimostrata dalla quote isolata. Review obbligatoria mantenuta,
nessuna correzione durante il benchmark o promozione scrivibile.

Labirinto: 18/22 target letterali valore/SOURCE in 3/3 (ultima V8:17/22), cinque
dati societari conservati, direttore/qualifica/ordine/5739 distinti in 3/3.
Separazione ordine/numero osservata senza modificare la logica dell'albo.
Recapiti alternativi e polizze incompatibili conservati senza scelta; quattro
checkbox omesse, firmatario/data non documentati non inventati. Nessun gold
modificato. 13 grounded =12 valori +1 NA locale, sei conditional e due review.

Catanzaro: operatore Mapi Ingegneria S.r.l., forma Societa a responsabilita
limitata, sede Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia, CF/PIVA
IT01234567890 presenti con SOURCE, senza USER. Sei valori più NA sede operativa.
Cellulare + Telefono solo parziale (telefono disponibile, cellulare no);
ramo ingegneria/direttore omesso, copertura inferiore ai controlli precedenti.
Nessuna accuratezza % per documenti reali senza gold.

Controllo finale del contratto: il validator storico accetta V2–V8 per replay;
il runner attivo ora impone expected_version=9 per impedire di evitare il nuovo
gate restituendo il vecchio formato. Aggiunto dopo le sette chiamate, mai durante:
raw tutti V9, sette rivalidazioni esatte e body/input ricostruiti identici,
zero chiamate aggiuntive. Il mock del test runner era V5 (inizialmente descritto
erroneamente come V8 nell'aggiornamento): aggiornato a V9 dopo una prima patch
sull'occorrenza sbagliata. Due suite intermedie 1.796 passati/una failure, log
conservati; la regressione di replay storico resta V5. **391 mirati / 18,40 s e 1.797 backend / 119,09 s passati**.
Ruff/fixture/diff, 11 replay storici, sette guardati, struttura e fingerprint DB
passati. Frontend invariato/non eseguito; nessuna migrazione/reindicizzazione.

Originali e **intero DB live** invariati in questa serie (diversamente dalla
precedente, con reload live osservato). Nessuna manipolazione manuale dei dati.
Helper locali .py.txt, nessun server live attivo durante le acquisizioni.
Un controfattuale offline applica i marker delle label realmente citate alle
tre vecchie proposte slittate e ottiene tre rifiuti: non nuova risposta AI,
non riparazione automatica né metrica semantica.

[Report](docs/benchmark-destinazioni-inline-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-slot-anchors.json),
[verifiche finali](docs/benchmarks/2026-10-12-slot-anchors-final-checks.json).
Bundle: **259 file / 2.066.565 byte**, SHA-256
`414f43a52018547d3e317dc784910b2c0565074684e115a15f347d70abd13fd7`. Grezzi anche in
`backend/data/compilation-audit/slot-anchors-20261012/`; tutti i 106 record annotati,
proposte omesse incluse nell'inventario, input/output/code/usage e failure salvati.

Primo passo sulla posizione concluso con risultato soddisfacente; non è ancora
compilazione completa affidabile. Prossimo punto **da discutere**: conservare
ruoli/etichette lungo il blocco, applicabilità e soggetto prima di un adapter
scrivibile. Una citazione al marker non sostituisce entailment semantico.
Commit piccoli autorizzati, nessun push.

## 12 ottobre 2026 — ruolo e contesto V10, protocollo prima delle API

Diagnosi prima del codice: Minervino raw V9 prova1 propone già nome/qualifica/
ordine/numero del direttore. p51 rifiutato dal formato ruolo:persona; p52/p53
rifiutati prima perché l'origine FORM p50 non è più l'ultimo paragrafo. Raw3 cita
ruolo da -32 e valori da -45: il join fra chunk resta vietato. Tutti i dettagli
FORM/SOURCE/proposte/errori salvati in role-context-20261012/diagnosis-before.json.

V10/catalogo V5: riferimento deterministico a introduzione senza campi per max
sei paragrafi consecutivi con candidate; interrotto da prosa nuova/blank/outline/
tabelle/checkbox. Solo contesto del ruolo, non ancore field.form. Fonte personale:
heading Markdown persona-ruolo o riga RUOLO persona in maiuscolo, match letterale
completo di ruolo/persona, titoli abbreviati sintattici senza inferenza qualifica.
Prova di ruolo e quote dei valori nello stesso record/chunk; altri record/ruoli,
negazioni/narrative/General KB respinti. Formato ruolo:persona precedente resta
compatibile, con i suoi limiti noti; replay V2–V9 separato dalla nuova semantica.
Una chiamata globale, nessun nuovo batch/retry/reviewer, zero RESOLVED/scritture.
Nessun hardcoding di nomi, ruoli, ID, bandi o titoli professionali.

417 mirati/19,74 s, 1.823 backend/121,23 s e Ruff passati. Prima 112/5,44 s passati,
Ruff segnala import order/tre righe lunghe: corretti. Provider simulati solo nei
test software, non come valutazione DeepSeek. Test record sbagliato nello stesso
chunk, ruolo/persona errati, provenienza, continuità/limite e barriere, condizioni
unknown, same-chunk, destinazione indipendente e replay storico. Controfattuale
offline cambia solo version9->10: non è nuova proposta AI né riparazione live.

Protocollo: tre Minervino, tre Labirinto congelato, un Catanzaro; seriali, stessi
17 SOURCE reali autorizzati/seven fixture SOURCE, deepseek-flash/thinking low,
timeout300 s, una chiamata ciascuno, nessun retry/USER/sessione/DOCX. Codice
congelato prima della serie, gold fuori dal prompt. Non cambiare il codice fra
prove. Conservare tutte le risposte e omissioni; nessuna accuratezza % sui bandi
senza gold. Criteri: recuperare ipotesi personali da SOURCE reali, ancorare valori
al record corretto, mantenere tre recapiti e cinque dati societari; non dichiarare
applicabilità né entailment semantico completo. Misurare costi/token/tempi senza
attribuire causalità a cache/ordine. Esiti da aggiungere dopo tutte le chiamate.
Grezzi backend/data/compilation-audit/role-context-20261012/. Nessun push.

## 12 ottobre 2026 — prima serie V10 parziale, refinement della copertura

Sette acquisizioni reali su 660bf0e concluse senza modifica durante le API.
Minervino: cinque dati personali grounded nella prima, nessuno proposto nella
seconda, quattro nella terza (nome/qualifica/ordine/8421). Recapiti corretti 3/3;
via+civico uniti nella seconda e campi iniziali con label nel paragrafo precedente
respinti quando la quote contiene solo marker/punteggiatura. Catanzaro recupera
quattro dati personali ma omette tabella iniziale/CF/PIVA: criterio dei cinque
dati NON superato. Labirinto tre raw con 18 target letterali, ma terza perde
5739 nel validator perché una seconda citation, reale, non contiene quel valore.
NA non calcolabili rifiutate in due prove, polizza ambiguous anziché conflicting
nella prima. Nessun gate indebolito per cambiare questi esiti. Grezzi intatti.

Causa osservabile della regressione Catanzaro: proposte limitate al ramo finale,
nessun record per la tabella generale, non rifiuto del suo bucket SOURCE. Dopo
la serie, refinement solo TASK: riesaminare tutti i blocchi e tutte le occorrenze
compatibili di un fatto, riusare fact_id con ancore/condizioni specifiche. Nessun
nome, campo, ID o documento hardcodato; schema/validator restano V10.

Nuovo protocollo registrato prima delle API: tre Catanzaro, un Minervino, un
Labirinto, seriali, corpus/gold identici, deepseek-flash/thinking low, timeout300,
una chiamata/prova, zero retry/USER/Word/sessioni. Codice congelato separatamente;
conservare tutti i cinque esiti insieme ai sette precedenti. Scopo: verificare
regressione cinque dati e recupero personale, non selezionare un'unica risposta
favorevole. Nessuna modifica durante questa seconda serie. Esiti da registrare
anche se il criterio non è raggiunto. Nessun push.

## 12 ottobre 2026 — conclusione delle due serie V10, esiti completi

Sette prove congelate 660bf0e e cinque successive a037314, tutti i dodici output
HTTP200/stop. Prima serie fallisce copertura Catanzaro; successiva cambia solo
TASK, senza schema/gate diversi. Nessuna modifica durante ciascuna serie,
nessun retry/USER/sessione/DOCX. Gold/fonti/originali identici alla baseline,
nessuna nuova estrazione casuale: controlli degli stessi bandi già confrontati.

Minervino dati personali conservati 5/0/4/5, 8421 incluso nelle tre risposte
con direttore. V9 li bloccava tutti: il riferimento all'introduzione FORM e i
record SOURCE letterali recuperano un caso concreto. La seconda prova omette
il direttore (non validator). Recapiti corretti 4/4, componenti riga critica
sei/quattro/tre/sei: cinque proposte nella seconda, ma via include civico e
civico omesso. Due indirizzi nel campo città da rivedere; nuova prova città=Bari.
Quote p16.s0 semanticamente debole resta aperta, nessuna promozione scrivibile.

Catanzaro iniziale omette tabella generale/CF/PIVA: criterio NON raggiunto.
Dopo TASK cinque dati conservati in 3/3: Mapi Ingegneria S.r.l.; Societa a
responsabilita limitata; Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia;
CF e PIVA IT01234567890, tutti SOURCE -43/generalita-mapi.md. Nessun USER.
Direttore/qualifica/ordine/8421 proposti in tutte le quattro risposte, conservati
nella prima iniziale e prima successiva. Successiva2: binding literal_match,
ma value con condizione semantic unknown rifiutato per sette campi ingegneria
più altra occorrenza personale, oltre una NA non calcolabile. Successiva3:
FORM quote «i requisiti» comincia dentro «dei requisiti» in paragraph:451,
non passa il confine; quattro binding personali bloccati. Non è SOURCE assente.
Questi due casi non vengono reinterpretati/corretti dopo il benchmark.

Labirinto 18/22 target letterali in 4/4, dopo i gate 18/18/17/18. Terza iniziale
aggiunge citation su numero documento 8821 senza valore 5739: fatto rifiutato
dal gate SOURCE esistente; non allentato. Cinque societari in 4/4. Alternative
recapiti/polizza sempre conservate senza scelta, ma polizza ambiguous anziché
conflicting in due prove. NA sede operativa grounded 2/4, quattro checkbox
omesse 4/4. Gold immutato, nessun signer o data non documentata inventati.
Nessuna accuratezza % per bandi privi di gold o pretesa di entailment completo.

201 record: 170 ipotesi SOURCE (62 senza condizioni unknown, 108 conditional),
due NA locali, otto review alternative, 21 rifiuti; 37 ipotesi personali.
2.516 posizioni nell'inventario completo, 2.315 omesse, non requisiti obbligatori.
**Zero RESOLVED/USER/sessioni/scritture**. Prima serie 398.747 token/631,07 s AI;
seconda 366.439/462,23; totale 765.186/1.093,31, non E2E. Nessun risparmio input
provato: Minervino input47.109/47.317, Labirinto16.856/17.064, Catanzaro65.986/
66.194. Una chiamata richiede comunque 74,51–114,62 s, output/cache variabili.

Test realmente eseguiti: 417 mirati/19,74 s, 1.823 backend/121,23 s, Ruff/fixture
prima della prima serie; dopo refinement solo TASK 417/19,19 s e Ruff, completa
non ripetuta. Frontend invariato/non eseguito. 17 replay storici e 12 V10 esatti,
12 body/input ricostruiti identici; ID/range/coordinate/testo/sezioni invariati
rispetto V9 salvo nuova continuazione/versione. Manifest, fonti/gold, record
SOURCE/provenance/hash e assenza scritture verificati. Intero DB live/originali
invariati fra le due serie e dopo la verifica finale, nessun reset manuale.

Failure helper preservate: import app mancante e cwd test errata (zero API/test
per quelle invocazioni); stdout seconda registrazione ereditato calls:7, mentre
protocollo/jobs/loop e chiamate effettive sono cinque. Ruff iniziale nel tool,
riepilogo durevole: non dichiarare un log integrale non acquisito.

[Report](docs/benchmark-contesto-ruoli-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-role-context.json),
[verifiche finali](docs/benchmarks/2026-10-12-role-context-final-checks.json).
Bundle pubblico **431 file /3.900.981 byte**, SHA-256
`dca4599fa9b17928a4799ef39dc4b548bac903dab024500fdc1835e1e8590066`.
Grezzi role-context-20261012/ e role-coverage-20261012/ sotto
backend/data/compilation-audit/, pubblicati anche nel bundle senza credenziali/
DB/config privata. Prompt/schema, HTTP/raw, codice/input/fonti/gold, omissioni,
validazioni, tempi/token, diagnosi/controfattuale e log conservati integralmente
quando acquisiti. Review mirata non certifica tutti i 201 record semanticamente.

Prossimo punto **da discutere prima di codice**: rendere backend autoritativa
la distinzione proposta/utilizzabilità invece di delegare value/conditional,
stabilizzare quote/etichette e completezza. Nessun passaggio ad adapter
scrivibile, chat/V1 o renderer ora. Nessuna migrazione/reindicizzazione.
Miglioramento concreto sui ruoli, affidabilità globale ancora incompleta.
Commit piccoli autorizzati, nessun push.

## 12 ottobre 2026 — Motore globale predefinito nella chat e export con review

Richiesta: rendere provabile con start.sh il nuovo motore, mettendo da parte V1.
Scelte comunicate prima dell'implementazione: nuove sessioni globali, una chiamata
sull'intero catalogo, nessuna promozione delle proposte a RESOLVED, selezione e
conferma USER esplicite prima della bozza parziale, legacy conservato. Nessun
cambio del branch a main o push. Implementazione congelata in **449b109**.

Riusati DB/state_json/routing/trasporto/validatore/renderer/download. Loader SOURCE
spostato dal runner al modulo condiviso, senza cambio di scope o del contratto
V10. UI nella chat con disclosure di review, niente pagina o vecchi batch da 12.
Regenerazione da originale, CAS e rivalidazione SOURCE prima dell'export e nella
transazione di salvataggio. Pausa/refresh/provider error non avviano retry.

Software realmente eseguito: **58 mirati /17,47 s; 1.847 backend /126,81 s;
101 frontend /5,18 s; 8 browser /24,2 s; Ruff, lint/build e diff check passati**.
Provider simulati in questi test, separati dalla prova reale. Failure iniziali
conservate: mock/tipi frontend, kwargs parser legacy, dipendenze fixture importate,
Ruff, completa iniziale interrotta e completa successiva fallita prima della
correzione dei fixture; non nascosti come se tutte le esecuzioni fossero verdi.

Smoke reale con deepseek-flash in DB/storage temporanei: due conversazioni nuove
via /answer (routing reale) e /resolve; quattro chiamate totali, zero retry.
Codice applicativo immutato durante la serie. Catanzaro usa il modulo archiviato
live, hash aeb1bda... diverso dall'originale dei precedenti confronti congelati;
Labirinto V1 fonti reingestite via API, quindi non confronto causale di punteggi.
Gold mai nel prompt; nessuna nuova estrazione casuale, modulo principale richiesto.

- Catanzaro: 307 candidate, 17 SOURCE, **14 proposte selezionabili**, 291 omesse,
  **90,11 s AI /85.483 token**. Cinque dati societari, direttore/qualifica/ordine/
  albo 8421 proposti. Selezionati nove valori, confermate USER partecipazione e
  ramo ingegneria; **9/9 scritti nella posizione XML corretta**. Sede operativa
  uguale alla legale senza condizione locale «se diversa» esclusa dalla selezione;
  firmatario di altra sezione rifiutato dal gate FORM/ruolo.
- Labirinto: 55 candidate, corpus fonte reingestito, **17 proposte selezionabili**,
  34 omesse, **70,05 s AI /32.836 token**. Selezionate tutte le 17 stringhe,
  confermato USER ramo ingegneria; **17/17 scritte nelle celle corrette**.

118.319 token di analisi + 6.453 routing = **124.772 token**. Tempi AI, non E2E;
nessun risparmio causale/costo monetario completo/% di accuratezza dichiarati.
Entrambe arrivano a REVIEW senza DOCX automatico. Export solo dopo review
controllata USER, nessun valore fattuale USER. **Zero RESOLVED**: stato GENERATED
qui significa bozza selezionata/esportata, non completamento di tutti i campi.
26/26 celle selezionate corrette, nessun'altra cella cambiata, paragrafi invariati
salvo avviso bozza previsto, checkbox native invariate. Originali e DB live
invariati anche dopo gli export.

Failure dell'harness di verifica conservate: path/PYTHONPATH, `id` invece di
`cell_id`, griglia espansa invece di celle fisiche, `.xml` sui nodi lxml generici.
Corretto solo l'harness, senza modificare il codice applicativo durante la serie,
né ripetere gli export riusciti o le chiamate AI.

[Report](docs/test-globale-chat-2026-10-12.md),
[JSON completo](docs/benchmarks/2026-10-12-global-chat.json).
Grezzi `backend/data/compilation-audit/global-main-20261012/`: protocollo,
prompt/schema/raw/HTTP/tempi/audit/stati, Word/report e controlli software.
Bundle versionato senza DB/chiavi, hash e inventario nelle verifiche finali.

Limiti: revisione semantica ancora necessaria, applicabilità/omissioni non
complete, checkbox non scritte, nessuna iterazione libera globale sui valori
USER, corpus piccolo entro cap espliciti. Una chiamata può ancora durare circa
90 s. Pronto da provare nella chat come proposta + review + bozza; prossimo
passo osservare l'uso reale prima di automatizzare ulteriormente.

[Bundle completo](docs/benchmarks/2026-10-12-global-chat-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-global-chat-final-checks.json).

Bundle pubblico: **110 file /1.037.437 byte**, SHA-256
`3f61e9427e7e0a6e14b8f16f4c382b0a2a69a621eb935f18b75077e76f8754b0`. Verificato byte per byte e senza
credenziali/DB/configurazioni private.


## 12 ottobre 2026 — La review globale torna nella conversazione

Richiesta: eliminare checkbox manuali ed elenchi XML. Comunicata prima del codice
la scelta di mantenere l'analisi globale unica e aggiungere una breve sintesi
AI dell'audit, con slot backend e risposte nel composer. Il componente tecnico
è rimosso, non spostato in un altro editor. Resta solo download DOCX/report.
Corretto anche il filtro degli unassigned: proposal=None non significa missing.
Nessun cambio a contratto V10/catalogo V5, RAG, parser, renderer o scope.

Tre passi recuperabili, ciascuno congelato durante le proprie prove reali:
fe73786 (dialogo), d6f9991 (schema nel prompt), 8f82c59 (binding personale nella
sintesi e UNKNOWN/SKIP senza falso blocco sulle alternative). Nessun push.
La sintesi può solo escludere proposte; SOURCE/USER non si confondono. Valori
USER solo per slot attivi, estratti letterali/date equivalenti e validator DOCX.
Max 40 proposte, 24 questioni in pool, tre domande, 45 s e 2.048 token output.
Una sintesi per passaggio, nessun loop/retry automatico, analisi non ripetuta
dopo chiarimenti. Generazione parziale solo con consenso esplicito nella chat.

Serie 1: nuova conversazione Catanzaro, 13 proposte SOURCE, ma sintesi rifiutata
(text anziché question). Schema passato al trasporto non visibile a DeepSeek
JSON mode: corretto il prompt, non accettati alias o requisiti meno severi.
Serie 2: ripresa della sola sintesi Catanzaro, pausa/ripresa, conferma USER
applicabilità e bozza in chat. Labirinto V1 con fonti/modulo congelati e
reingestiti in nuovo DB: tre domande in una risposta, CONDITION_TRUE/SKIP/UNKNOWN
in un solo messaggio, poi consenso alla bozza. Nessun valore fattuale USER.
13/13 +17/17 valori SOURCE materializzati nelle celle corrette, nessun'altra
cella o checkbox modificata. Cinque dati societari e albo 8421 automatici.
Serie 3: soltanto due replay di sintesi reale sui medesimi audit, senza cambiare
sessioni/generare. Dopo una frase impropria sul professionista firmatario nella
serie 2, il contesto del binding personale e l'istruzione di non inferire ruoli
producono due sintesi corrette su questo punto. Non è garanzia generale.

**18 chiamate /177.970 token**, fallimento incluso: due analisi, nove routing,
cinque sintesi e due replay. Analisi 108,25/88,13 s; replay sintesi 1,87/2,02 s.
Prime sintesi non cronometrate separatamente. Zero retry automatici, solo ripresa
esplicita dopo schema. Nessun confronto causale di copertura/latency/costo:
proposte stocastiche e fonti reingestite, gold fuori dal prompt. Catanzaro modulo
live già richiesto, non nuova estrazione casuale. Labirinto fixture V1 invariata.
Uno scambio raccoglie i chiarimenti in ciascun caso +un consenso alla bozza;
Catanzaro include anche tre turni deliberati di controllo/ripresa errore.

59 mirati /12,97 s; 1.882 backend /136,02 s; 101 frontend /5,86 s;
12 browser /27 s desktop/mobile/reduced-motion; Ruff/lint/build/diff passati.
Completa dopo cambi funzionali, mirati/Ruff dopo soli contatori/tempi della
sintesi. Software con provider simulati; provider reale solo nelle serie sopra.
Failure software/harness/schema preservate nel report; nessun rerun nascosto
per migliorare gli output. Nessuna revisione del gold o nuova fixture.

Limiti: ancora proposte parziali, 291/34 posizioni non analizzate, native checkbox
non scritte. Narrazione iniziale imprecisa e dubbio sul recapito senza hold:
prosa non è evidenza e i controlli restano backend. Correzioni fuori dal gruppo
attivo/riapertura dei rinvii da discutere. GENERATED non significa modulo completo,
zero RESOLVED in questo adapter. Originali invariati. Hash fisico DB live variato:
confronto read-only di fonti/moduli e record preesistenti invariato; non affermare
byte-identità dell'intero DB. Copie di test private, nessuna modifica/rollback live.

[Report completo](docs/test-chat-conversazionale-globale-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-conversational-review.json),
[bundle pubblico](docs/benchmarks/2026-10-12-conversational-review-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-conversational-review-final-checks.json).
Grezzi in backend/data/compilation-audit/conversation-review-20261012/;
backup pubblico senza runtime/DB/chiavi, con prompt/schema/raw/audit/stati/Word,
script/log e screenshot browser simulato. Prossimo passo: provare la nuova UX
con l'utente prima di estendere correzioni e scrittura checkbox.

Bundle verificato: **193 file /1,039,762 byte**, SHA-256
`e09e888dd2786cd56e1c88d4be24578043fd1314d039822f0a41e29775dba709`. Copie temporanee con DB e chiavi rimosse
dopo backup/verifica; grezzi non sensibili conservati anche in locale.

## 12 ottobre 2026 — consenso alla bozza dopo rinvio, regressione reale

Priorità dell'utente: «lascia in bianco» -> «si»/«siii» ripetevano la proposta
di generazione. Osservazione read-only: il planner raggiungeva già generate,
ma tutte le proposte dipendevano da condizioni rinviate, quindi zero valori
esportabili. Il backend bloccava la selezione vuota; la UI mostrava il vecchio
riepilogo al posto del vero motivo di blocco. Raw del vecchio planner non
acquisito, diagnosi basata su stato e comandi effettivamente persistiti.

Codice congelato **fb30ff5**: risposta clarify visibile; selezione vuota
consentita soltanto esplicitamente, con allow_empty/allow_unresolved e
consenso USER, senza confermare condizioni né promuovere fatti. Il dialogo
dichiara quando propone una copia senza valori. RAG/parser/renderer invariati.

DeepSeek reale su quattro copie private dello stesso checkpoint/audit:
«si» -> copia senza valori /2,22 s; «siii» -> stessa /2,18 s;
dialogo iniziale archiviato + «lascia in bianco» -> «si» -> stessa /5,17 s;
dialogo iniziale + conferma delle due condizioni -> «si» -> **13/13 scritture
SOURCE corrette** /5,03 s. Incluse denominazione, forma giuridica, sede, CF,
PIVA e 8421. Zero valori fattuali USER, nessun nuovo valore nei casi vuoti.
Sei routing +2 sintesi, **29.205 token**, zero retry automatici. Nessuna nuova
analisi globale: misura del checkpoint, non di copertura/qualità completa o
riduzione causale della latenza iniziale. Nessun gold/fixture V1 modificato.

Software: **71 backend mirati**, **1.894 completi /141,32 s**, **102 frontend**,
**2 browser desktop/mobile**, Ruff/lint/build/diff check passati. Provider
simulati per software; reali soltanto nella serie dichiarata sopra. Asserzioni
iniziali corrette per banner, cell_id e scope della fixture; harness reale
iniziale senza PYTHONPATH fallito prima delle chiamate, log conservato.

Sessione live/state_json e originale invariati. Copie private rimosse dopo
backup verificato, grezzi in backend/data/compilation-audit/blank-consent-20261012/.
[Report](docs/test-consenso-bozza-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-blank-draft-consent.json),
[bundle](docs/benchmarks/2026-10-12-blank-draft-consent-audit.tar.gz).
Restano conferme eccessive, copertura incompleta, checkbox e correzioni libere.

Bundle del consenso: **142 file /1.816.941 byte**, verificato byte-per-byte e
senza chiave reale, database o runtime. SHA-256
`e5f574f4832997f6fb543164c0e75f0218c128eda7d5ce41c0b4829e2bd7da5b`.
[Verifiche finali](docs/benchmarks/2026-10-12-blank-draft-consent-final-checks.json).

## 12 ottobre 2026 — protocollo Dialogo V1, prima delle API

Congelati 43 turni indipendenti in `demo-documents/benchmark-dialogo/v1/`:
consenso/negazione/cortesia, valori e date, condizioni singole/multiple,
risposte parziali/ambigue, SKIP/UNKNOWN/REFUSE, pausa/ripresa, export e routing
normale. Gold escluso dal prompt; nuovo benchmark separato da Labirinto V1.
Planner reale di produzione, applicazione delle decisioni in DB/storage
isolati, massimo 48 casi seriali × due tentativi strutturali. Nessuna nuova
analisi globale, RAG o sintesi AI; non misura copertura SOURCE. Al checkpoint
con valori esiste un recapito USER autoriale; al checkpoint vuoto nessun valore.
Il guard finish viene applicato come in chat; si misura comunque il planner
anche dove la chat reale lo anticiperebbe, dichiarando la chiamata diagnostica.
Nessun cambiamento al motore durante la serie. Le prove reali seguono questo
commit; risultati ancora da acquisire. Sei test dell'harness passati /1,02 s;
prime failure di setup/import/Ruff conservate in
`backend/data/compilation-audit/dialogue-v1-preflight/initial-failures.txt`.

Preflight reale e16f87e: arresto PRIMA delle API perché la descrizione del
progetto temporaneo «V1» viola min_length=3. Nessuna chiamata DeepSeek. Corretto
solo il runner, senza cambiare fixture/gold/motore. Conservati protocollo vuoto
in dialogue-v1-20261012/ e traceback in dialogue-v1-preflight/real-run.log;
serie effettiva prevista in dialogue-v1-20261012-r1/.


## 12 ottobre 2026 — Dialogo V1, risultati reali su 4820b95

**39/43 gold conformi**, 43 chiamate deepseek-flash seriali/thinking disabled,
zero retry/schema error/eccezioni, 138.803 input +4.013 output =142.816 token,
47,92 s turni /46,41 s AI, mediana 1,10 s. Nessun cambiamento produzione o gold,
nessun caso reale rieseguito. Checkpoint autoriali e DB/storage temporanei,
nessuna nuova analisi/RAG/sintesi. Un solo confronto selezionato di dialogo,
non una percentuale di affidabilità della compilazione completa.

Tre effetti errati: rinvio locale -> PAUSE; valore+finish -> solo VALUE; cambio
alla denominazione -> VALUE nel recapito attivo. Quest'ultimo persiste davvero
USER nel campo sbagliato pur con slot e quote validi: priorità prossima.
Quarto FAIL di contratto: generate anziché finish, stessa richiesta di export,
nessuna scrittura impropria. Non modificato il gold per far salire il risultato.
28 mutazioni di slot, otto valori USER (due con effetto vietato dal gold).
Nessun destinatario fuori dai soli slot attivi, ma una scelta entro gli slot
può essere semanticamente sbagliata; nessuna promozione a SOURCE/RESOLVED.

Cinque export reali: quattro con un recapito USER autoriale preesistente e uno
senza alcun valore. Scritture/report/posizioni verificate, originali e altre
celle invariati salvo banner. «ok sì va bene» e «siii» corretti. Nessuna misura
SOURCE in questo benchmark. DB live aperto solo in lettura per il profilo;
nessun database/chiave copiato, runtime temporaneo eliminato automaticamente.
Verifiche: 79 backend mirati /12,30 s, Ruff completo e diff check. Sei test
harness senza provider, rimanenti con provider simulati; nessuna suite completa
frontend/browser ripetuta perché non ci sono cambi applicativi.

[Report](docs/benchmark-dialogo-2026-10-12.md),
[JSON](docs/benchmarks/2026-10-12-dialogue-v1.json),
[bundle](docs/benchmarks/2026-10-12-dialogue-v1-audit.tar.gz).
Grezzi dialogue-v1-20261012-r1/ e preflight sotto backend/data/compilation-audit/.
Bundle 251 file /715.315 byte, SHA-256
42d6d271e6a313d7eda40c6c1f19feb3f2b1d3bc72c920a9d191e33c8091c669,
verificato byte per byte e senza credenziali/database. Offline verifier prima
richiamato da un cwd errato, poi corretto: nessuna ripetizione API. Conservati
setup fallito e risultati negativi. Prossimo punto: gate di pertinenza USER,
poi composizione/priorità e scope dei controlli; nessuna patch durante la prova.

## 12 ottobre 2026 — pertinenza USER, protocollo prima delle API

Corretto il collegamento messaggio -> slot attivo: verifica semantica separata
solo delle scritture VALUE/CONDITION_TRUE/CONDITION_FALSE, massimo una chiamata
per gruppo, quattro slot, 768 token output, timeout 15 s, nessun retry. Errori e
ambiguità non autorizzano scritture; gli altri slot validi restano utilizzabili.
Trade-off esplicito: latenza/token aggiuntivi nei turni che aggiornano dati,
per evitare che quote letterale + slot reale salvino il valore nel campo errato.
Nessuna modifica UI/parser/renderer/RAG o promozione USER -> SOURCE.

277 test mirati /46,40 s; 1.924 backend completi /146,27 s; Ruff e diff check.
Provider simulati nei test software. Primo run mirato con 14 failure delle
asserzioni storiche sulle chiamate/prompt, poi corrette senza indebolire i gate;
log conservati sotto reply-scope-20261012/checks/.

Protocollo reale: stessi 43 casi/gold/Word di Dialogo V1, massimo tre chiamate
per turno (due tentativi router +una verifica), seriali su checkpoint e DB
isolati. Separatamente congelate nove proposte in benchmark-dialogo/guard-v1,
incluso il raw errato della baseline: una verifica reale per gruppo, nessun
nuovo output router simulato. Gold escluso dai prompt, nessuna analisi SOURCE.
Confrontare anche risposte valide, costo e latenza; nessuna modifica applicativa
nel corso delle serie. Risultati ancora da acquisire, nessun push.

## 12 ottobre 2026 — pertinenza USER, risultati reali su 132bc6a

Nessuna modifica applicativa durante le due serie, nessun caso ripetuto per
selezionare un risultato. Dialogo V1 invariato: **40/43**, prima 39/43.
DeepSeek ripropone il valore della denominazione nello slot recapito; la verifica
indipendente restituisce UNRELATED, il backend risponde con chiarimento e la
sessione rimane identica. I 39 casi già conformi non regrediscono. Restano
condition-skip (PAUSE), finish-mixed e blank-export (generate invece di finish).
Questa volta finish-mixed non salva alcun valore; il router è variabile e non
attribuiamo al gate un miglioramento su quel comando, rimasto fuori scope.

43 routing +12 verifiche, zero retry/schema error/eccezioni; 149.606 input
+4.765 output =154.371 token, 66,20 s turni /64,79 s API. Verificatore da solo:
11.594 token /13,81 s, mediana 1,14 s. Baseline: 142.816 token /47,92 s;
la protezione ha un costo, nessuna pretesa di risparmio. Dataset indipendente
Guard V1: **9/9**, nove chiamate reali /8.366 token /9,68 s, proposte preparate
prima delle API (prima replica il raw errato precedente), non nuovi router
simulati. Valori e condizioni pertinenti passano; estranei/ambigui bloccati;
gruppo parziale conserva due parti valide e respinge la terza estranea.

Riletti i DB temporanei e confrontati tutti i cinque export DOCX reali:
quattro con un recapito USER autoriale preesistente, uno vuoto; ogni cella
modificata coincide con stato/report, originali e altre celle invariati salvo
banner. Nessuna SOURCE fittizia o promozione di USER. Non è una nuova analisi
SOURCE o una misura di completezza della compilazione. Le invarianti software
passano con provider simulati; il verificatore semantico resta fallibile,
timeout/provider falliscono conservativamente. Frontend/browser non ripetuti,
nessun contratto/UI cambiato. Grezzi in reply-scope-20261012/; report, metriche
e bundle durevole in docs/. Nessun push. Prossimo: comandi misti e SKIP locale.

Bundle finale pertinenza USER: **334 file /792.505 byte**, verificato
byte-per-byte e per SHA di ogni file, senza chiave/DB/runtime. SHA-256
`f994203975c2e22e863a5d0dc24cae12b01b60f743ac0744af6eb0850b3c57b6`.
[Report](docs/fix-pertinenza-user-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-reply-scope.json),
[bundle](docs/benchmarks/2026-10-12-reply-scope-audit.tar.gz),
[verifiche finali](docs/benchmarks/2026-10-12-reply-scope-final-checks.json).
Un vecchio link STATUS a un report locale ignorato del 8 ottobre è assente
in questo checkout: conservato, verificati tutti i nuovi link. Note offline
nel bundle; nessun nuovo benchmark API necessario per i controlli documentali.

## 12 ottobre 2026 — comandi, protocollo prima delle API

Focus autorizzato: distinguere rinvio del chiarimento e pausa della sessione,
priorità dei comandi nei messaggi misti, finish/generate. Nessuna modifica a
UI, parser, renderer o RAG; invarianti SOURCE/USER e gate di pertinenza fermi.
Regola attuale conservata: PAUSE/FINISH non acquisiscono nuovi valori nel turno.

Congelati **28 scenari nuovi** in benchmark-dialogo/commands-v1, con Word e
contesti del Dialogo V1 ma gold separato; i 43 originali rimangono invariati.
Valutazione BEFORE sul codice attuale, poi intervento minimo sul prompt unico
ed eventuale normalizzazione deterministica di export rispetto al checkpoint;
nessuna nuova chiamata AI classificatrice. AFTER sugli stessi 28 e sui 43
originali; massimo tre chiamate per turno, nessuna selezione dei risultati.
DB/storage temporanei, provider DeepSeek reale, gold escluso dai prompt,
nessuna nuova analisi SOURCE. Non è un test di completezza del DOCX.
Otto test fixture/harness passati /1,11 s, senza provider. Risultati reali da
acquisire; nessun cambiamento applicativo durante le singole serie.

BEFORE Comandi V1 su b468ea5: **24/28**, 28 routing +3 verifiche di pertinenza,
zero retry/schema error/eccezioni, 96.019 token /35,54 s turni, un export reale
con recapito USER preesistente. Tre FAIL di nomenclatura generate/finish;
un FAIL locale con negazione interpretato come explain. I rinvii semplici
passano in questa serie: non presumere che il precedente errore sistematico
condition-skip sia scomparso; va riprovato nei 43 originari.

Fix proposto/implementato: prompt unico esplicita oggetto/polarità e priorità
sessione -> dati; rinvio locale e incertezza restano diversi. Normalizzazione
deterministica solo del generate globale fuori dal checkpoint di generazione
in finish: stessa operazione senza nuovi permessi, nessun matching del testo.
Engine nel contesto backend, non nuovo stato o API. Legacy preservato per gli
effetti diversi di finish/generate. Nessuna chiamata AI nuova. 248 test mirati
/37,67 s con provider simulati, inclusi HTTP/DB reali isolati; primo Ruff con
due righe lunghe nel test, corrette. AFTER ancora da acquisire; gold congelato.

## 12 ottobre 2026 — comandi AFTER su 802c483

Comandi V1 **28/28**, prima 24/28 sul gold fissato in b468ea5; Dialogo V1
**43/43**, prima 40/43, gold originario invariato. Nessuna modifica applicativa
nelle serie, nessun caso selettivamente ripetuto. Il rinvio della conferma ora
è SKIP/USER locale. Nel caso «lascia vuota ... non sto dicendo che non si applica»
BEFORE il router proponeva CONDITION_FALSE ma il gate lo bloccava (AMBIGUOUS,
intent finale explain); AFTER direttamente SKIP, condizione non negata.
I cambi di nome generate/finish sono in parte normalizzazione deterministica:
non aumentano valori/campi compilati. Priorità attuale PAUSE/FINISH sui valori
preservata, turni composti ancora da discutere. Nessuna keyword/candidate/azienda
hardcodata; nessuna nuova chiamata AI o schema pubblico.

28 AFTER: 28 routing +2 gate, zero retry/schema error, 105.035 token /35,78 s.
43 AFTER: 44 routing +12 gate, 173.265 token /66,77 s, un retry: «No, non generare
ancora» inizialmente answer_fields senza slot, rifiutato; retry reply, nessuna
mutazione/export. Tutti i raw e l'errore conservati, 43/43 è l'esito finale.
Prompt +353 input token/router, nessun risparmio dichiarato; la chiamata gate
risparmiata nei 28 deriva dalla decisione SKIP anziché dalla condizione falsa.
Singole serie, nessuna stima di varianza. Totale BEFORE+AFTER+43: 99 checkpoint,
117 chiamate reali, non compilazioni intere o qualità SOURCE.

Software: 248 mirati /37,67 s, **1.950 backend completi /145,97 s**, Ruff/diff.
Provider simulati nei test; otto harness/fixture senza provider /1,11 s.
Frontend/browser non ripetuti perché invariati. Sette export realmente confrontati:
sei con un recapito USER preesistente, uno vuoto; stato/report/posizioni coerenti,
originale/altre celle invariati salvo banner. Gate di pertinenza invariato e
correction-outside ancora bloccato. Nessun valore USER promosso a SOURCE.

[Report](docs/comandi-conversazionali-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-commands.json),
[bundle](docs/benchmarks/2026-10-12-commands-audit.tar.gz).
Bundle **592 file /1.425.816 byte**, verificato byte-per-byte e per hash di ogni
file, senza chiavi/DB/runtime, SHA-256
`d47c6280078942bf96475475252d3894788f28270c5e07486d7833f624339566`.
Grezzi in commands-20261012/. Nessuna migrazione/reindicizzazione/push.
Prossimo: concordare il comportamento dei turni composti prima di implementarli.

## 12 ottobre 2026 — conversazioni complete, prima dei turni composti

Protocollo in d5167b9, correzione del setup registrata in 2c5a567 prima di R2.
Applicazione identica a fb2894e, già pubblicata; nessuna modifica durante le
serie. DeepSeek Flash reale, nuove conversazioni/sessioni via API ASGI, non
checkpoint manuali né browser reale. Rilettura in un nuovo processo prima di
ogni turno, solo DB/storage privati per le richieste. Nessun valore aziendale
o professionale presente nelle fonti inserito dall'utente.

Catanzaro: 307 candidate, 12 proposte SOURCE esportate, 293 posizioni omesse,
0 RESOLVED. Due domande iniziali, pausa/ripresa e bozza esplicita. La conferma
di entrambe con riferimento «quello indicato nelle fonti» viene accettata solo
per il ramo; gate sul partecipante AMBIGUOUS. Secondo «Sì, confermo» accettato.
Sei turni, 12 chiamate /128.420 token, analisi 133,47 s. Cinque campi aziendali,
direttore tecnico, Ordine e 8421 realmente nelle celle previste.

Labirinto R1: setup errato, procedura in Company KB invece che progetto;
conservato, escluso dai confronti congelati. Comandi gruppo/pausa/ripresa/export
riusciti, 16 valori, numero albo confluito nell'Ordine e campo numero omesso.
59.915 token /nove chiamate, analisi 65,29 s. Gold non cambiato. Corretto solo
l'harness, nuovo DB e conversazione R2: scope da sources.json, Word/testi/manifest
originali, nessuna modifica applicativa. ID API associati offline agli ID simbolici
solo con nome, role, scope/categoria e contenuto esatto.

R2: 17 proposte SOURCE esportate, 34 posizioni omesse; 17 valori/fonti coerenti
col gold per i campi esportati, non accuratezza su tutto il documento. Una
risposta a tre slot produce CONDITION_TRUE, SKIP, UNKNOWN. Nessun loop,
recapito/polizza vuoti anche dopo pausa/ripresa. Ordine/5739 separati in R2;
non attribuire causalmente il diverso esito al solo scope o dichiarare risolto
lo slittamento. Cinque turni, nove chiamate /60.200 token, analisi 70,96 s.

In totale 16 turni /30 chiamate /248.535 token, includendo R1; zero retry/schema
error. Verificati 45 valori in tre Word/stato/report, zero scritture aggiuntive,
originali/checkbox invariati, solo document.xml e banner previsti. Valori fattuali
USER: zero. Sintesi ancora soggetta a imprecisioni; molti candidate non valutati.
109 software mirati /17,07 s con provider simulati, Ruff backend/harness e diff
check. Suite completa/frontend/browser non ripetuti, nessun contratto cambiato.

Incidente d'ambiente documentato: il dev server --reload reagisce ai nuovi .py
dei runner ed esegue lo startup, ricostruendo 82 chunk di quattro artefatti live.
Solo ID/FTS cambiati; lettura comparativa dimostra contenuti, SOURCE, conversazioni,
sessioni e originali invariati. Nessun ripristino manuale. R2 evita il watcher
usando .txt; prossimi runner fuori dal watch root o senza suffisso .py.

[Report](docs/test-conversazione-completa-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-full-conversation.json),
[bundle](docs/benchmarks/2026-10-12-full-conversation-audit.tar.gz).
Snapshot/chiavi private eliminati dopo i confronti. Proposta successiva:
conferme anaforiche del gruppo attivo; poi decisione esplicita sui turni composti.
Nessun cambiamento a RAG, parser, renderer, UI o stato della compilazione;
nessuna migrazione/reindicizzazione manuale/push.

Bundle sanificato verificato byte-per-byte: **303 file /1.142.223 byte**,
SHA-256 `d57f20629d2144e6c2032f859d41c3cd276f81c314a35502beb8bdc04bb1a170`.
Prompt/schema/raw, tempi/usage, revisioni e tre Word realmente generati inclusi;
nessun DB/chiave/runtime privato. Le serie fallite o non comparabili restano incluse.

## 12 ottobre — protocollo conferme del gruppo attivo, prima delle API

Autorizzato il fix circoscritto del falso negativo del turno Catanzaro: router
corretto, gate USER SUPPORTED/AMBIGUOUS. La domanda naturale esiste per slot
ma routing_context la perde; il prompt non distingue conferma esplicita del
gruppo da sì senza destinatario. Previsti conservazione question bounded e
chiarimento del task del verificatore indipendente, senza automatismi o nuovi
permessi. Congelati 16 casi separati positivi/avversariali, BEFORE/AFTER completi;
guard-v1 (9) e Dialogo V1 (43) invariati per le regressioni. Quattro test del
protocollo /0,54 s, Ruff runner/test e diff check passati, nessuna API ancora.
[Diagnosi e protocollo](docs/conferme-gruppo-2026-10-12.md). Nessun push.

## 12 ottobre — conferme del gruppo attivo, risultati

BEFORE congelato 0ef3bd5: 14/16, falso negativo reale riprodotto. Proiezione
question per slot (600 caratteri, già persistita) e task guard indipendente
c6bd0ff: 15/16. Residuo conservativo su conferma di gruppo misto: respinti
giustamente i valori assenti, ma anche la condizione. Precisata indipendenza
degli slot booleani b8c88f8: 16/16 sull'intera nuova serie, gold invariato.
Tutti i raw intermedi conservati; niente ripetizioni selettive o nuovi permessi.
Regressioni DeepSeek Flash reali 9/9 guard e 43/43 Dialogo V1, un retry strutturale
export-no prima di qualsiasi mutazione, cinque export della fixture verificati.

Replay esplicito del checkpoint Catanzaro reale in nuova sessione/snapshot privato:
raw dell'analisi precedente rivalidato sul corpus/originale, nessuna nuova analisi.
Entrambe le conferme USER salvate in un turno anziché due; zero valori fattuali
USER. Due turni conferma+export, quattro chiamate reali /12.810 token /5,83 s AI.
Bozza con otto valori SOURCE corretti, inclusi i cinque aziendali. Criterio dei
12 valori NON superato: nuova sintesi sospende nome/qualifica/Ordine/8421 per
dubbio sul ruolo. Tutte le 12 proposte ancora persistite, SOURCE non modificato;
non forzati i valori né adattato il criterio. Limite distinto della sintesi,
da misurare separatamente, non attribuito causalmente al fix del gate USER.
Word/originali/checkbox/altre posizioni e tabelle live verificati invariati salvo
gli otto valori e il banner. Snapshot/chiavi private eliminati. Setup iniziale
prima delle API fallito per chiavi risposte assenti, corretto solo il runner e
conservati log/protocollo; nessun output modello scartato.

Totale 100 casi +2 turni /117 chiamate /282.267 token /142,30 s AI. Nuove
verifiche non aggiunte: il gate esistente costa +500 token input nel caso reale congelato.
Singole serie sul set di affinamento, non held-out o accuratezza del modulo.
Software: quattro controlli protocollo /0,54 s, 72 mirati iniziali /7,39 s,
270 mirati finali /47,74 s, 1.972 backend finali /151,49 s; suite intermedia
1.972 /146,40 s, Ruff/diff check passati. Provider simulati nei test software.
Errore path in un comando mirato senza test eseguiti archiviato. Nessun test
frontend/browser, contratti/UI invariati. Nessuna migrazione/reindex/push.
[Report](docs/conferme-gruppo-2026-10-12.md),
[metriche](docs/benchmarks/2026-10-12-group-confirmations.json),
[bundle](docs/benchmarks/2026-10-12-group-confirmations-audit.tar.gz).
Ripresa proposta: gate delle esclusioni della sintesi/ruoli. Turni composti
salva+pausa/export ancora da discutere, nessuna decisione automatica.

Bundle sanificato verificato byte per byte: **629 file /1.297.367 byte**,
SHA-256 `09355f5429c68a71fd42e238a0b3739397af3befd0e6f36ec28dc2fa0259a522`.
Nessun database/chiave privata; manifest e verifiche finali in docs/benchmarks.

### 12 ottobre 2026 — contesto dei ruoli, protocollo prima delle API

Isolata perdita della prova SOURCE persona–ruolo nel JSON della sintesi.
Scoperto inoltre un errore nel precedente replay 8/12: catalogo grezzo senza
anchor, contesto locale vuoto; non prova di regressione applicativa. Corretto
solo il runner. Congelati sette casi separati con manifest, raw reali Catanzaro/
Labirinto e controesempi autoriali attuale/cessato/ruolo diverso. Gold escluso
dal prompt, una chiamata/caso, nessuna nuova analisi né scritture live. Quattro
test protocollo passati /1,97s; primo test incompleto sui campi omessi corretto,
Ruff passato dopo due correzioni di stile. Risultati da misurare e archiviare.
[Diagnosi/protocollo](docs/sintesi-ruoli-2026-10-12.md).

### 12 ottobre 2026 — prova SOURCE del ruolo conservata nella sintesi

Baseline fedele **5/7**, AFTER **7/7** sullo stesso set congelato. Il precedente
8/12 era condizionato da anchor persi nel runner: Catanzaro corretto resta12->12,
Labirinto17->17. Miglioramento concreto: sei valori di incarichi cessati in due
casi ora sospesi, nessuna contaminazione dell'incarico attuale. JSON condiviso
persona/ruolo/prova SOURCE già groundata, massimo40 contesti/due quote800 e
slot per proposta; stesso schema output e stessa chiamata, +455 token input
medi. Nessuna keyword, nuova validazione permissiva o promozione a RESOLVED.

Replay HTTP isolati BEFORE/AFTER, analisi reale precedente rivalidata, niente
nuove analisi/retrieval:12 SOURCE corretti nel Word, incluso8421; due condizioni
USER confermate insieme, consenso esplicito alla bozza, nessun valore USER.
Stato/report/celle coerenti, originali/altre celle/checkbox e DB live invariati,
snapshot e chiavi cancellati. **22 chiamate reali /59.025 token /32,65s AI**.
Singole serie non held-out, nessun gold nel prompt; non completezza del modulo.

Test software con provider simulati:143 mirati /21,30s,1.985 backend /144,54s,
Ruff backend/runner e diff check. UI/API invariati, nessun browser/frontend
rieseguito. Limiti: quote limitate, narrazione ancora cauta/probabilistica,
sospensioni storiche cumulative, sparse coverage/checkbox/comandi composti fuori
scope. Report/metriche/acquisizioni durevoli in docs/benchmarks; nessun push.

Bundle sanificato218 file /1.143.542 byte, confronto byte per byte, nessuna
chiave/DB. SHA256 be28938aa7c3bd0aa98b69d0e0c01ce60c4427c3615245da2e15910b3588675b;
manifest in docs/benchmarks/2026-10-12-narration-roles-manifest.json.

### 13 ottobre 2026 — checkbox native, protocollo congelato

Autorizzati gruppi di scelta e scrittura nel motore globale, senza nuova UI.
Renderer legacy/content control testato102 /7,26s, scelte/API36 /5,41s,167 mirati
/11,56s; prima suite completa finale2031 /150,75s. Group/source/user separati,
massimo64 gruppi/32 opzioni, marker per checkbox, cardinalità all'export e effetti
di deselezione espliciti. Contratto V11, V10 preservato; sola corrispondenza SOURCE
letterale conservativa per le scelte. Nessuna parola di questo bando nel codice.
Prima delle API congelati benchmark-checkbox/v1 e gold,14 checkbox/two soggetti;
tre analisi senza retry, benchmark compilazione V1 invariato e bando estratto
senza ripetere l'estrazione. [Protocollo](docs/checkbox-2026-10-13.md).

Prima serie V11: benchmark-checkbox3/3 analisi con10/10 booleani corretti e
scritti, due testi, zero scelte senza SOURCE; tempi54,78/114,49/48,66s. Dialogo
reale preparato4/4, scelta USER/ambiguità/UNKNOWN/SKIP. Labirinto:22 valori grezzi
corretti ma solo17 ammessi/scritti, cinque checkbox scartate per confronto case
sensitive ereditato da _comparison_text. Fixture/gold/codice invariati durante
le prove, nessun output eliminato. Correzione locale per opzioni (NFC/case/spazi),
con prova positiva della clausola SOURCE intera e veto contro nomi ritagliati
da negazioni. Nessuna modifica ai confronti del RAG/delle condizioni. Nuova serie
sugli stessi gold dopo il congelamento del fix, risultati da acquisire.
