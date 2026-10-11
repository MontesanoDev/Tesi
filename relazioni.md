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
