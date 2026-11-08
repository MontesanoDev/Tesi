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
/11,56s; prima suite completa finale 2031 /150,75s. Group/source/user separati,
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

### 13 ottobre 2026 — checkbox, esiti completi e limiti reali

Tre serie congelate di tre analisi sullo stesso set dedicato: tutti i dieci
booleani SOURCE proposti coincidono col gold; quattro caselle senza prove non
ricevono valori fattuali inventati. Serie finale scrive 10/10/7 checkbox e 2 testi
per prova: nel terzo run tre scelte partner sono conditional e restano escluse.
Tempi 46,81/27,21/62,48 s, token analisi 20.439/16.858/23.601. Non è un test held-out
né un confronto controllato di latenza; tutte le ripetizioni salvate.

Labirinto R2:5 checkbox corrette+11 testi scritti,6 testi conditional trattenuti.
Conservati R1 e rivalidazione intermedia negativa: il controllo SOURCE prima
non gestiva attributi inline. Il writer nativo non modifica altri ZIP part,
non inventa valori e non trasforma proposte in RESOLVED. Test riproducono gruppi
esclusivi con alternative estreme omesse: il nuovo gate di lista fisica impedisce
che l'alternativa inizialmente spuntata sopravviva alla scelta incompleta.

Due HTTP reali con DB privato e analisi nuova: R1 solo 2 testi perché i field non
ripetevano marker già verificati nel gruppo. Riusato quel binding con stesso
paragrafo/etichetta grounded; R2 scrive 10 checkbox+2 testi SOURCE, zero USER. La
rivalidazione dei 13 raw salvati conserva i gruppi; non è una nuova esecuzione
provider e non riscrive i Word storici. Verifica read-only 14 copie/50 valori testuali
per posizione, parti ZIP non body e celle non selezionate invariate. Originali/
DB live preservati; DB/chiavi private eliminati.

Limite emerso: gruppi senza SOURCE possono essere omessi dall'analisi e non
diventare domande; una risposta fuori dal gruppo attivo fallisce il router.
Non dichiarare completo il dialogo checkbox. Il checkpoint preparato USER passa
4/4, persistenza/export testati software; non è un nuovo E2E completo.
Regressione Dialogo V1 reale 42/43,56 chiamate/188.418 token, export-no fallisce
schema al primo/retry senza scritture. Nessuna correzione durante il benchmark.

Unica estrazione casuale dal pool Catanzaro/Minervino/Trapani: Trapani.115 candidate,
zero controlli checkbox nativi,8 proposte conditional,107 omesse; senza conferme
zero valori scritti anche nell'export di laboratorio esplicitamente autorizzato.
87,12 s/47.766 token analisi; nessun gold/accuratezza percentuale e nessun redraw.

Totale 100 chiamate reali,14 analisi,651.258 token,1.199,90 s AI sommati, non costo
fatturato. Software finale 2.051 backend/151,19 s,109 mirati/16,41 s,41 scelte/2,53 s,
Ruff/diff check. Test software con provider simulati; frontend/browser non
rieseguiti, UI/contratti invariati. Logs intermedi falliti conservati, incluso
aliasing della fixture di test; il primo log 2031 è stato sovrascritto da 2045,
il suo esito storico viene dalla precedente acquisizione di console.
Nessuna migrazione/reindex/push. [Report](docs/checkbox-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-checkboxes.json). Prossimo: copertura dei
gruppi senza SOURCE da discutere/misurare, RAG testuale invariato; legacy Word
ancora da verificare visivamente su desktop.

Bundle sanificato: 917 file /13.240.541 byte grezzi, confronto byte per byte,
nessuna chiave o DB. Manifest e acquisizioni in docs/benchmarks. SHA256
84ad2b3900dfe96901775a1ca936bfb490e118258ca86f3323a78f813498bd04.

### 13 ottobre 2026 — crash reale Minervino, audit parziale

Test manuale: analisi terminata ma sintesi in HTTP 500. Gruppo con label oltre
250 caratteri correttamente REJECTED; il consumer tentava comunque min_selected
su quel record parziale. Riprodotto con lo stesso output salvato e con dieci
regressioni software (tutte fallite prima della correzione). Ora soltanto i
GROUNDED_GROUP impongono regole di scelta; nessun default permissivo/catch globale.
136 mirati /22,84 s e 2.061 backend /153,38 s, Ruff e diff check passati, provider
simulati nei test; frontend/browser non ripetuti, nessun contratto/UI cambiato.

Replay registrato senza nuove API ora passa. Una nuova sintesi DeepSeek Flash
reale: 3,81 s /3.845 token, un tentativo, tredici proposte conditional e due
domande, nessun DOCX generato; nessuna nuova analisi SOURCE o valore USER.
Codice invariato durante la prova. Sessione/versione/originale live invariati;
il vecchio tentativo resta FAILED e richiede normale ripresa, nessuna modifica
manuale al DB. Non è un nuovo benchmark di compilazione completa.
[Report](docs/checkbox-crash-2026-10-13.md), acquisizioni locali in
backend/data/compilation-audit/rejected-checkbox-20261013/. Fix committato,
nessun push. Completezza dei gruppi fisici e copertura restano limiti separati.
Bundle sanificato e manifest in docs/benchmarks/2026-10-13-checkbox-crash-*:
81 file /1.818.061 byte grezzi, confronto byte per byte, chiavi e DB esclusi.
SHA256 7e8c4c3f0a2c29e10b94b5c365c143f95aba6c7061a00de104ddf2edbeb2dca3.

### 13 ottobre 2026 — verifica della bozza Minervino dell'utente

Diagnosi read-only del DOCX fornito, stesso hash della generazione persistita:
nove valori SOURCE nel ramo societario, ai candidate proposti, zero checkbox su
tredici native. Quindici parti ZIP non body invariate; originale, copia e
sessione/versione invariati. Nessuna nuova chiamata AI o compilazione.
«Sede legale in» riceve l'intero indirizzo, poi via/civico vengono ripetuti:
il contesto del modulo suggerisce il solo comune. Materializzazione coerente
col JSON e SOURCE non certificano la precisione semantica della destinazione.

267 candidate, 16 assegnazioni, 15 proposte grounded conditional e una respinta
per quote con due marker, 251 posizioni omesse. choice_groups={} e nessuna
proposta checkbox. Dati Elisa Romano/qualifica/Ordine/8421 già nel contesto
SOURCE del modello, ma nessuna proposta per quella parte. Non è un'assenza
di dati in KB e non prova un errore del writer. Non usare candidate come
denominatore di accuratezza o numero di dati obbligatori mancanti.

Risposta USER: tipo societario accettato come condizione positiva del ramo,
non scelta nativa. Rinvio della seconda domanda esclude sei proposte aziendali
dell'intestazione; sintesi poco esplicita sull'effetto. Campo di rappresentanza
e natura dell'operatore risultano uniti in una condizione. Solo il consenso
successivo autorizza la bozza parziale con nove valori SOURCE, nessun USER.

[Diagnosi](docs/minervino-output-2026-10-13.md), snapshot/input/raw/report/
revisioni/Word in backend/data/compilation-audit/minervino-output-20261013/.
Solo documentazione: diff e riferimenti, nessuna suite software/provider
simulato/browser. Codice applicativo invariato. Prossima scelta da discutere:
copertura del primo passaggio globale e collegamento condizioni/scelte,
prima di valutare una chiamata bounded di recupero. Nessun push.
Bundle e manifest in docs/benchmarks/2026-10-13-minervino-output-*:
24 file /1.573.365 byte grezzi, confronto byte per byte, chiavi/DB esclusi.
SHA256 84a024ad61e665746187568c259e7b7747466a19d49ece1a55a3402f0c054b46.

### 13 ottobre 2026 — copertura testuale, rinvii locali e fuzzing

Baseline23357b6, passi c9a28fe/052c473. Prima di implementare comunicata la
scelta: una sola analisi, riferimenti di lettura e domande locali distinte da
condizioni; nessun batch12/nuovo RAG/parser/writer/UI. Checkbox rinviate.

Prima serie congelata: Minervino9/16 proposte e quattro proprietà del direttore
in entrambi; HTTP nuovo solo quattro proposte professionali, domanda erronea
sulla denominazione già in KB, quattro testi scritti. Fallimento di copertura
conservato. Seconda serie dopo indice letterale SOURCE: Minervino18/19, HTTP19
proposte, tutte con nome/qualifica/Ordine/8421. Applicabilità resta variabile:
HTTP finale copia vuota autorizzata dopo rinvio, non compilazione riuscita.
Labirinto V1 in entrambe conserva undici testi e cinque checkbox preesistenti.
Fixture/fonti/gold invariati e gold mai nel prompt. Nome proposto con prefisso
Ing., scostamento letterale rispetto al gold conservato. Nessun nuovo sorteggio
bando: Minervino è il caso specifico dell'utente, non prova casuale aggiuntiva.

43 checkpoint comandi reali:42/43, stesso export-no conservativo, zero export
non autorizzati. Due conversazioni HTTP ASGI private da quattro messaggi, source
snapshot importato via repository (ingestion/embedding non misurati), nessun
valore aziendale via USER. Totale87 chiamate/8 analisi/934.320 token/1.245,68s
sommati: nessun risparmio dimostrato, latenza ancora di minuti. Codice congelato
in ciascuna serie, modifiche solo fra serie e ultimo boundary Unicode dopo API.

Finali214 mirati/25,74s e2146 backend/152,53s, Ruff/diff.960 mutazioni globali e
480 piani chat con seed, più boundary HTTP; provider simulati per il software.
Riprodotti3 diagnostici non serializzabili,6 errori formatter422->500 e2 crash
UTF8 nel retry; corretti senza catch generale né normalizzazione di valori
fattuali. Errori di schema atteso/fixture/status502 iniziali conservati e distinti
da bug. Directory assente nel primo runner HTTP e filtro report del verifier
corretti solo negli strumenti. Nessun frontend/browser, UI/contratti invariati.
Otto DOCX/26 valori verificati per paragrafo, prove SOURCE/digest e parti ZIP;
originali e DB live invariati. Report e artefatti duraturi:
[relazione](docs/compilazione-copertura-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-text-coverage.json),
[bundle](docs/benchmarks/2026-10-13-text-coverage-audit.tar.gz).
Restano condizioni troppo ampie, indirizzi compositi e copertura sparse.
Non dichiarare completati tutti i limiti osservati; nessun push.

### 13 ottobre 2026 — prosecuzione conversazionale e feedback stabile

Baseline628fcb9. Diagnosi read-only del dialogo Minervino: domanda aperta legata
a booleano, riepilogo SOURCE rifatto a ogni turno, messaggi finali globali non
salvati in cronologia, snapshot READY visibile brevemente durante refresh.
Prima scelta comunicata: separare ricevuta dell'aggiornamento e sintesi iniziale,
senza modificare SOURCE/RAG/parser/writer. Il solo prompt fallisce in due prove
reali (78/82 parole ripetute): acquisizioni negative conservate.

ContinuationPlan ora senza message: backend rende ricevuta delle sole mutazioni
accettate, modello controlla proposte e seleziona domande residue. Schema lega
confirmation agli slot booleani e question ai valori/scelte. Nessun nuovo fatto
o allentamento dei gate. Feedback unico, cronologia persistita corretta.

Serie reali finali DeepSeek after07/08, codice congelato, stesso checkpoint
V11/originale/fonti:18 proposte preservate, due conferme+rinvio accettati,13 parole
di ricevuta, nessuna nuova analisi/export. «Di ingegneria» non conferma un diverso
incarico personale: richiesta di precisare senza mutazione. Non è compilazione
integrale o benchmark della latenza dell'analisi. Prova separata di ripresa della
vecchia sessione: narrazione breve, ma ruolo troppo specifico da una condizione
«IN QUALITÀ DI» priva di predicato; risposta VALUE respinta nello slot booleano.
Questo limite semantico resta aperto. Tutti i tentativi/preparazioni falliti salvati.

Replica finale after10:18 proposte intatte,13 parole di ricevuta,6 invocazioni,
13,07s AI sommati/26.730 token,nessuna nuova analisi. Può ancora chiedere una
qualità locale già implicata da una conferma di condizione: la selezione delle
domande non è perfetta. after09 fallisce il fingerprint globale DB, pur con
sessione/versione/stato/originali live invariati; origine della differenza non
acquisita. Possibile reload/FTS, non dimostrato. Runner con hash per tabella:
after10 passa anche il controllo globale. Fallimento precedente conservato.

203 mirati/28,42s,2178 backend/162,97s,106 frontend/6,98s,8 browser/10,3s,
320 mutazioni con seed, Ruff/Oxlint/build/diff. Provider simulati nelle suite,
API simulate nel browser, provider reale solo nei replay privati. Nessun nuovo
sorteggio bando: è il caso specifico utente. Integrità sessione live/versione9,
stato e originale confermata read-only. [Report](docs/compilazione-dialogo-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-conversation-flow.json), raw in
backend/data/compilation-audit/conversation-flow-20261013/ e bundle sanificato
con manifest in docs/benchmarks/. Commit piccoli locali, nessun push.

### 13 ottobre 2026 — esiti motivati dei vuoti,V12

Baseline fceedfc, feature5e50021. Verificato il prompt: l'omissione silenziosa
era esplicitamente richiesta. Prima scelta comunicata: stessa singola analisi,
coverage dei vuoti separata dai valori SOURCE. Nuovo contrattoV12, V11 invariata.
Ogni candidate ha proposta/domanda, motivo FORM ancorato, spiegazione respinta,
unassessed esplicito o omissione. Nessun valore/NA/statoUSER inventato dal resoconto.
Errori locali non cancellano le proposte indipendenti. Avvisi backend iniziali
se mancano esiti o motivi validi, senza inferire «non letto». Nessuna nuova UI.

Due baseline reali DeepSeek prima della modifica, poi due serie da2 prove su
Labirinto e Minervino. Originali/fonti/gold congelati; gold mai nei prompt.
Serie iniziale negativa conservata: contesti condivisi respinti troppo localmente,
quote oltre500 e una prova Minervino con sole5 proposte. Correzione bounded con
contesti strutturali/condizioni/gruppi già validati e unità di lettura; non con
contesti SOURCE più larghi o quote tollerate. Replay raw mantiene gli stessi valori.

Finali Labirinto:55/55 esiti formalmente validi in entrambe,28 motivi,zero omissioni
o spiegazioni respinte. Gold letterale/source matches22/16 contro16 baseline,
zero valori/NA inattesi nel controllo limitato; non accuratezza semantica.
Finali Minervino:19/17 proposte SOURCE,159/135 motivi ancorati,88/105 motivi respinti,
0/7 omissioni. Conservati nome/qualifica/Ordine/8421. **Copertura semantica ancora
incompleta**, soprattutto gruppi di persone, scope delle condizioni e7 checkbox
di scelta del ruolo omesse in una prova. Non nascondere questi esiti negativi.

10 analisi+8 sintesi,811.409 token acquisiti; tempi analisi finali118/115s Labirinto
e102/159s Minervino, nessun risparmio dimostrato. Zero sessioni live o Word generati
dal benchmark. Due sessioni V11 rivalidate identiche; checkpoint live/originale
preservato. Attività utente contemporanea non confusa con mutazioni del test.
coverage è fotografia della prima analisi, non stato live dopo USER.

277 mirati/19,91s,2219 backend/162,60s,Ruff/diff,360 mutazioni nuove con seed.
Provider simulati nei test, reali solo nei benchmark. Frontend/browser non ripetuti,
frontend invariato. Suite intermedia fallita solo sul provider fixture ancoraV11,
aggiornato al contratto richiesto. Dopo le serie ritoccato solo l'avviso backend
per coesistenza di omissioni e motivi respinti; suite finale ripetuta.
[Report](docs/compilazione-esiti-vuoti-2026-10-13.md),
[metriche](docs/benchmarks/2026-10-13-field-decisions.json), raw in
backend/data/compilation-audit/field-decisions-20261013/, bundle/manifest in docs.
Prossimo: motivazioni dei blocchi ripetuti e condizioni, senza indebolire provenance.
Commit per passi, nessun push.


## 13 ottobre2026 — consenso alla bozza, tracce e riprova del checkpoint

Baseline94ccdbc, bug utente non riprodotto e causa storica non acquisita.
Sessione Minervino checkpoint6:20 proposte SOURCE e2 conferme USER persistite.
6 interpretazioni reali+1 replay HTTP prima del codice già generano correttamente.
Corretto il catch opaco: trace planner bounded e messaggi pubblici controllati,
nessun cambiamento a prompt/schema/Source/parser/renderer/routing semantico.

Tre replay intermedi e tre finali DeepSeek, codice invariato durante le prove:
`si`, `ok sì va bene`, `siii` → una chiamata/zero retry,20 valori SOURCE nel DOCX,
Elisa/Ordine/8421 inclusi. Check indipendente di tutti i paragrafi tramite offset
originali, spazi irrisolti invariati. Primo check del runner aveva contato anche
il paragrafo BOZZA: falsi negativi di misura conservati e riverificati sullo stesso
output, nessuna correzione del renderer. Totale13 chiamate/55.616 token; nessuna
nuova analisi, costo/coverage generale non misurati. Sessione live invariata.

191 mirati e2233 backend, Ruff/diff check. Suite iniziale:2227 passati+2 falliti
per testo tecnico pubblicato dal nuovo catch; messaggi corretti per classe,
vecchi test mantenuti. Nessun frontend modificato. Nessun miglioramento della
qualità semantica attribuito a questi test software con provider simulati.
[Report](docs/compilazione-consenso-bozza-2026-10-13.md), raw e bundle dedicati.
Prossimo: se l’errore reale ricompare, diagnosticare dalla trace salvata anziché
inventare una causa a posteriori o ripetere l’analisi dei dati già acquisiti.


## 13 ottobre2026 — revisione del compilato(2) reale dell’utente

Revisione, non nuova analisi/benchmark: originale Minervino invariato,
file utente identico alla generazione6cb97f7b, sessionea067b0ab versione7.
20 posizioni SOURCE Company KB scritte, incluso direttore tecnico/Ordine/8421.
Quote, valori e hash verificati contro l’input reale; testo integrale uguale
all’originale con soli20 valori e banner,15 altre parti ZIP immutate. Zero
chiamate provider, valori USER, generazioni nuove o modifiche a codice/DB.

Limiti osservati: Bari iniziale proposto ma rifiutato dal gate FORM per quote
solo marker/punteggiatura; indirizzo completo ridondante; etichetta Ordine
attaccata al valore. Spazi del firmatario/soci/date personali non inventati.
Checkbox escluse su richiesta; nessun rendering visuale Word. Nessuna
percentuale di accuratezza o suite software presentata come appena eseguita.
[Report e acquisizioni](docs/minervino-output-2-2026-10-13.md).

## 15 ottobre 2026 — studio Astra e diagnosi offline della V12

Richiesta di studio architetturale, senza implementazione del nuovo motore:
[astra.md](astra.md), baseline `4b7d828`. Analizzati codice, prompt e acquisizioni
Minervino a067b0ab/e8ad0f46; documentazione ufficiale sulle API file consultata.
Nessuna nuova chiamata provider, estrazione casuale, generazione DOCX o modifica
alla fixture V1/fonti/gold. Le proposte di esperimento sono distinte dagli esiti.

Ricostruzione dell'input e rivalidazione dell'audit identiche agli originali.
I51 chunk SOURCE del database in sola lettura coincidono con il contesto inviato.
21 assegnazioni grezze,20 proposte condizionate grounded,1 rifiutata;147 motivi
ancorati e99 respinti. Replay deterministico del pool in memoria:1 domanda
iniziale,0 dopo conferma dell'unica condizione. Sessione live versione8 e file
esaminati invariati. Nessuna percentuale di accuratezza: gold Minervino completo
non disponibile, confronto visuale degli originali non effettuato in questa prova.

Analisi statica: limite40 della revisione narrativa con conseguente filtro
all'export SOURCE della chat;67 celle di preferenze rappresentate come testo,
mentre il contratto scelte riguarda checkbox native e non ha max_selected.
Sono limiti separati dai dati mancanti e dalle false negative del grounding.
Le misure di token e tempi LLM riportate nello studio sono quelle storiche.

Prima esecuzione del runner fallita per attributo DocxLayout inesistente nello
script di misura: corretto unsupported in unsupported_locations; errore conservato
nel raw01. Diagnosi riuscita nel raw02. Ruff iniziale del solo runner ha segnalato
ordine import e noqa inutili, corretti; non modificata la logica applicativa.
Controllati riferimenti, esempi JSON, diff e integrità degli artefatti.
Nessuna suite completa o nuova valutazione generativa eseguita.

[Metriche](docs/benchmarks/2026-10-15-astra-metrics.json),
[runner](docs/benchmarks/astra_inspect.py),
[backup delle nuove acquisizioni](docs/benchmarks/2026-10-15-astra-offline-audit.tar.gz).
Raw locali astra-20261015-01/02 sotto backend/data/compilation-audit/.
Il bundle conserva diagnostica/hash e script eseguito; gli archivi LLM storici
rimangono nei percorsi già documentati. Nessun upgrade sessioni/reindex/commit/push.

## 16 ottobre 2026 — Minervino con integrazione: diagnosi offline

L'utente ha fornito nuovi dati/integrazione.md e il Word compilato(5)(1),
segnalando che l'arricchimento della KB non risolve la compilazione. Identificati
sessione 607eda67, analisi 211598d4 e generazione a4231f73 del 15 ottobre.
È una lettura/rivalidazione di acquisizioni esistenti, non una nuova valutazione
LLM. Baseline codice 4b7d828; nessuna modifica applicativa o alla fixture V1.

Integrazione Company ID10: cinque frammenti nei 56 effettivamente inviati;
testo del file fornito identico all'upload, differenze byte CRLF/LF. Input
ricostruito e audit rivalidato identici. Corpus DB uguale nei campi inviati;
il confronto iniziale dei record completi risultava falso solo per metadati
aggiuntivi relevance/excerpt/document_metadata, distinto nel riepilogo finale.

27 proposte grezze, 21 grounded, due respinte per quote FORM solo marker
(comune/provincia iniziali), quattro dati del direttore sospesi per binding
su chunk diverso dal valore. Soci: 24 posizioni senza proposte; scope c_soc
incompleto e motivo coverage respinto. Un gruppo checkbox respinto per etichette
accorciate non letterali, zero booleani. Pool in memoria 3→1→0: il primo valore
nome/qualifica ricomposto dal router fallisce contains_span, il secondo turno
registra solo il nome. Nessuna risoluzione SOURCE degli attributi dopo la scelta
del firmatario; vuoti coverage non trasformati in una coda completa di domande.

Il Word fornito coincide con quello persistito e con la ricostruzione del testo
dall'originale più 22 valori del report: 21 SOURCE e un nome USER. Altre 15 parti
ZIP identiche. Questo verifica la materializzazione, non la completezza del caso.
Zero nuovi RESOLVED, generazioni o risposte USER; quelle analizzate sono storiche.
Nessun gold completo o percentuale di accuratezza, nessun rendering visuale.

Conservati input/request/schema, output/audit/metriche, sintesi/routing, dialogo,
stato/revisioni, report, documenti e snapshot del codice; nessun DB o profilo con
credenziali. Raw locali minervino-integrazione-20261016T133808Z/, bundle 92 file,
616.261 byte, SHA-256 f93a50f933609903a01f2d7e7f1a124d0b5e5a4a77a50136e879ca6a0bc21b1f.
File osservati e sessione invariati; nessuna suite applicativa o nuova API AI.

[Report](docs/minervino-integrazione-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-integrazione.json),
[bundle](docs/benchmarks/2026-10-16-minervino-integrazione-audit.tar.gz).
Prossimo: gold umano o bozza indipendente revisionata dall'utente, fondati sulle
fonti già integrate e sulle scelte della pratica. Non aggiungere automaticamente
altre fonti per trattare omissioni e rifiuti come dati assenti.

## 16 ottobre 2026 — revisione del gold sintetico Minervino dell'utente

Ricevuto domanda-iscrizione.GOLD-SINTETICO.docx in nuovi dati/, SHA-256
c4dbd36e5d1a02f987bdabde3f3cd67ab4e47291aff9d737666bfd4d875991bf.
Confrontati originale, avviso locale e KB effettivamente indicizzata, in sola
lettura: 56 frammenti, 18 Company. Non è una nuova prova LLM né un gold congelato.

Revisione di 52 occorrenze: 19 anagrafica iniziale, nove società e 24 soci;
valori coerenti con fonti, con equivalenze di date, titoli e provincia.
Le scelte di partecipazione, sei preferenze, designazioni professionali,
attestazioni e luogo/data vanno formalizzate come scenario USER/checkpoint;
la KB non le determina. Identificativi dimostrativi conservati, checksum non
verificati; chiarire la policy prima dello scoring.

Rilevata omissione strutturale: cancellati tre paragrafi del direttore tecnico,
otto destinazioni originali. Elisa compilata come socia non sostituisce il
blocco del direttore: ripristino necessario prima del congelamento. Le 13
checkbox native mantengono gli ID, tre true coerenti col simbolo; nelle tabelle
solo sei celle differiscono e contengono X. Firma e rami alternativi vuoti.
Etichette prestampate in parte riscritte: preservarle o dichiarare tolleranze.

I chunk delle generalità ricompongono il testo completo normalizzato nonostante
un partizionamento storico diverso da quello corrente; integrazione ricomposta
e partizionamento corrente uguale al DB. Primo raccordo delle prove interrotto
per spazi multipli nelle righe Markdown; completato dichiarando la normalizzazione,
senza alterare dati o input. Rendering visuale non eseguito; nessuna percentuale
di accuratezza, nuova compilazione o suite applicativa.

[Report](docs/minervino-gold-review-2026-10-16.md),
[confronto documentale](docs/benchmarks/2026-10-16-minervino-gold-review.json),
[bundle](docs/benchmarks/2026-10-16-minervino-gold-review-audit.tar.gz).
Raw minervino-gold-review-20261016T135700Z/; bundle 17 file, 232.310 byte,
SHA-256 a10cf1cba283021923c98f04e60fe0dd1bd6f2c733836da1bdbd672030650762.
Conservati file e corpus senza database/profili con credenziali; gold non presente
nel corpus autorizzato. File dell'utente e originale invariati, nessuna modifica
al motore/KB/fixture o chiamata provider. Nessun commit/push.

## 16 ottobre 2026 — Word gold revisione 1 da approvare

Su richiesta dell'utente creata nella stessa cartella
[revisione 1](<nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>),
con [scheda scenario](<nuovi dati/SCENARIO_GOLD_MINERVINO.md>). Ripristinati i
tre paragrafi/otto campi del direttore e le etichette originali della società
e dei soci, conservando valori, note e scelte del gold ricevuto. File dell'utente
e originale invariati. Modifica XML autonoma dell'artefatto, senza writer
applicativo o LLM; riferimenti fisici verificati sui placeholder originali.

Verificate 52 occorrenze già presenti più otto ripristinate, quattro tabelle
identiche, sei X e 13 controlli nativi/tre true identici al candidato. DOCX aperto
con python-docx, ZIP e XML validi; solo document.xml modificato nel pacchetto.
Nessun rendering visuale o suite applicativa. Nessuna modifica a codice/DB/KB
o fixture, nuova API, commit o push. L'utente controllerà il Word: **non congelato,
attendere il suo OK esplicito prima di procedere**.

[Controlli](docs/benchmarks/2026-10-16-minervino-gold-revision-1.json),
[backup](docs/benchmarks/2026-10-16-minervino-gold-revision-1-audit.tar.gz).
Word SHA-256 5bd34a43b22dff44d5a280b690f4187d345e6664619d42272bbe2c590b5c8d67;
bundle 204.042 byte, SHA-256
01398d746fbf4612f959e5ae25d1d964ec1c0673cb3b62a05df2df3fc9807a2d.

## 16 ottobre 2026 — verifica dei quattro rilievi sulla revisione 1

Controllo offline del verdetto fornito dall'utente, senza modificare il Word.
I quattro titoli conservano la numerazione originale lowerLetter/%1), partenza
1 e nessun override. La scheda scenario contiene già le quattro designazioni;
resta il momento di disponibilità degli input USER. Confermate due spiegazioni
autoriali nei paragrafi compilabili 117–118, opportuno spostarle nello scenario.

La firma isolata a pagina 10 non è confermata. MuPDF/mutool 1.27.0 legge i DOCX
ma reimpagina originale/gold in 16/15 pagine: dicitura e linea insieme nell'ultima
pagina del gold, verificata anche nell'immagine. Non disponibile rendering Word;
assenza di keepNext esplicito non prova il distacco. Nessun controllo visuale
completo o certificazione della fedeltà in Word.

[Report](docs/minervino-verifica-verdetto-2026-10-16.md),
[controlli](docs/benchmarks/2026-10-16-minervino-verdetto.json),
[bundle](docs/benchmarks/2026-10-16-minervino-verdetto-audit.tar.gz).
Raw minervino-verdetto-20261016T143707Z/; bundle 11 file, 265.691 byte,
SHA-256 7909c9c5df4d3a82f8b117d9981a8c3bc28931ff6114b47a22208b6b69a9e890.
Verificati hash input, manifest, riferimenti e diff; Word/scenario invariati.
Nessuna modifica applicativa/DB/KB/fixture, API AI, suite applicativa o nuova
misura di accuratezza. Nessun congelamento, commit o push. Attendere revisione/OK
dell'utente; per il pacchetto completo restano checkpoint e annotazioni del caso.

## 16 ottobre 2026 — congelamento autorizzato Minervino V1

L'utente autorizza a risolvere i rilievi, adottare la base per la nuova
architettura, creare tag e pubblicare. Creata fixture separata
[Minervino V1](demo-documents/benchmark-minervino/v1/README.md) con modulo,
cinque fonti, richiesta iniziale, scenario/checkpoint, copione, gold Word/JSON,
inventario e manifest. Nessuna implementazione del nuovo motore o nuova prova
LLM. Labirinto V1 conservato senza modifiche.

Gold ricostruito dall'originale con valori e scelte del gold dell'utente:
note fuori dai campi, continuazioni ripristinate, proprietà per unire il
blocco firma. Altre 15 parti ZIP identiche all'originale. Le fonti Company
e General coincidono con i file backend letti senza modifiche; quinta fonte
avviso. Policy esplicita sui codici dimostrativi, firma/allegati e abilitazioni
specialistiche esclusi dalla verifica di ammissibilità.

267 destinazioni censite: 187 testuali (60 SOURCE, quattro USER, 123 vuote),
67 celle di preferenza (sei X), 13 checkbox native (tre true). Quote, valori,
vuoti, gruppi e checkpoint localizzati; il conteggio non è una misura di
accuratezza. Verifica indipendente completa passata, tutti i 18 hash del
manifest conformi, struttura OOXML invariata annullando solo gli edit ammessi.

MuPDF reimpagina il definitivo in 16 pagine, separando la linea firma anche
con keepNext: fallimento visuale conservato. LibreOffice 26.2.6.3 preparato
localmente da pacchetti Ubuntu, senza installazione di sistema. Primi avvii
falliti per bootstrap/unorc/registry non ricollocati, poi conversione riuscita:
originale dieci pagine, gold nove, tutte ispezionate. Numerazione a)–d) visibile
e firma unita a pagina 9. Warning liblangtag del tool locale conservati;
nessuna certificazione Word. Primo controllo con Python sistema senza docx
fallito, finale riuscito con ambiente backend; nessuna suite applicativa completa.

[Report](docs/minervino-base-v1-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-freeze.json),
[backup](docs/benchmarks/2026-10-16-minervino-freeze-audit.tar.gz).
Raw minervino-freeze-20261016T144815Z/; bundle 75 file, 3.468.040 byte,
SHA-256 8af726b5b36fac4bcf0bb3bc24d6c0dfa51624a2e0f5eba96324c2bbe5999a27.
Gold SHA-256 94e77ce5d04585c4d62d858bec1ec2d6c0af2e4aa5c062e7af6cb32a474c4db3.
Tag della base: baseline-minervino-v1-20261016, ramo prune-backend.
Nessuna modifica a codice applicativo, DB/KB, sessioni o fixture precedenti.
La baseline integrata e la scelta di provider/configurazione rimangono il
passo successivo; runner Labirinto non compatibile automaticamente col nuovo schema.

## 16 ottobre 2026 — disegno proposto E1/E2, nessuna esecuzione

L'utente richiede continuità di STATUS.md per la tesi e chiede se separare E1
(FORM completo compatto) da E2 (estratti nella stessa vista compatta). Registrato
il [piano](docs/piano-esperimenti-e1-e2.md); nessuna nuova baseline o misura LLM.

E1 confronta B0 completo attuale e completo compatto, mantenendo fonti,
disponibilità USER e componenti successive invariati, con ogni adeguamento
di prompt/contratto dichiarato. E2 confronta ogni gruppo con E1 completo
sulle stesse destinazioni e checkpoint, entrambi contro il gold: accordo fra
risposte non equivale a correttezza. La selezione dei gruppi e delle dipendenze
deve essere fissata prima dei risultati e fuori dalla fixture V1.

L'efficienza E2 riguarda il ciclo locale; misurare anche il costo aggregato
della suite e il contesto ripetuto, senza presumere risparmio per una compilazione
completa. Margine ammissibile e configurazione ancora da fissare; nessun nuovo
errore critico come orientamento proposto, nessuna equivalenza o generalizzazione
dimostrata. SOURCE inizialmente identiche; estratti soltanto nel banco di prova,
senza reintrodurre il motore a gruppi. B0/E1 precedono la selezione finale E2.

Aggiornati STATUS, benchmark e proposta; verificati riferimenti, tabelle, diff
e integrità delle fixture. Nessun codice, DB/KB, fixture/gold o protocollo
congelato modificato, nessuna chiamata provider, suite applicativa, estrazione
materializzata, commit o push. Le prove restano da eseguire.

## 16 ottobre 2026 — B0, misura preliminare offline dell'input

L'utente chiede se occorra misurare il sistema corrente. Ricostruito l'input
con funzioni applicative attuali, DB in sola lettura e materiali verificati
contro Minervino V1: 56 chunk da cinque file, 267 destinazioni. JSON compatto
attuale 240.276 caratteri; FORM 126.928, SOURCE/metadati 75.735, reading plan
25.670, schema 11.701. System prompt 24.675, totale messaggi 264.951 caratteri.
Nessuna equivalenza fra caratteri e token, nessuna chiamata o score di qualità.

Il progetto ha thinking false ma resolve_global forza thinking per DeepSeek.
Prima ricostruzione basata erroneamente sulla preferenza, conservata nei raw;
corretta dopo lettura del percorso globale. Non usare --no-thinking per B0
fedele al sistema. Primo avvio script senza PYTHONPATH fallito con import app,
poi acquisizione finale riuscita nell'ambiente backend. Nessun tentativo
ha contattato provider o prodotto una sessione/bozza.

[Report](docs/b0-preflight-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-b0-preflight.json),
[bundle](docs/benchmarks/2026-10-16-b0-preflight-audit.tar.gz).
Raw b0-preflight-20261016-01/; 19 file, 264.115 byte, SHA-256
4052f21914593c951f8f8f701486078530fb36f3e5d3bdecd6c2e8dd00918f25.
Verificati hash, riferimenti e diff; nessuna modifica a codice applicativo,
DB/KB o fixture, suite applicativa, commit/push. Da eseguire tre run B0
proposta/audit, raccordo dello scoring e percorso integrato distinto per
dialogo/export. I runner esistenti non misurano automaticamente tutte le fasi.

## 16 ottobre 2026 — B0 reale Minervino, tre analisi e tre Word

Provider autorizzato dall'utente per la baseline prima dell'architettura.
Codice 99ab052 e fixture/fonti/gold invariati; tre analisi sequenziali DeepSeek
flash con thinking effettivo attivo. Risposte riusate nella continuazione dei
servizi su copie SQLite/storage isolate, dopo input uguale e rivalidazione
audit uguale. Routing, interpretazione USER, narrazione ed export reali;
non misurati browser, endpoint HTTP o ingestion. Nessun nuovo motore.

Valori SOURCE proposti 23/23/50; conformi al gold 22/22/49, conformi e grounding
passato 21/17/21 sui 60 target documentati. Word: 24/18/23 scritture totali;
23/17/22 target conformi, includendo rispettivamente 2/2/1 risposte USER che
ripetono la scelta iniziale del firmatario. Provenienza conservata, nessun
punteggio aggregato favorevole sui tanti vuoti. Tutti i 123 vuoti previsti,
61 preferenze false e dieci controlli false preservati; zero dei quattro testi
USER, sei preferenze true e tre checkbox true attesi. Nessuno dei quattro
argomenti del copione chiesto. Run 2 fermato sulla riconferma SOURCE del
direttore, fuori copione, poi export parziale esplicito: nessuna risposta inventata.

Cause distinte: omissioni LLM, binding letterali che respingono i 24 valori dei
soci correttamente proposti nel terzo run, attribuzione personale nello stesso
chunk, scelte iniziali non trasmesse all'analisi, pool domande incompleto,
indirizzo intero nel campo comune, gruppi checkbox respinti/assenti. Nessuna
correzione durante la misura. Ridurre il JSON è un'ipotesi da misurare con E1,
non una spiegazione già dimostrata di tutti i difetti.

30 chiamate, 481.199 token: 357.871 input, 123.328 output, incluso reasoning
89.725. Input per analisi 75.864 token, cache-hit 75.648/miss216; tempi
146,73/179,84/183,85 s. Somma tempi provider 561,28 s, non latenza UI;
nessun costo monetario acquisito. Nessun timeout o errore HTTP della serie.

Confronto indipendente di tutte le 267 destinazioni e verifica materiale del
DOCX: report e valori coincidono, altre 15 parti ZIP preservate. Rendering
LibreOffice dieci pagine per bozza, visione campionata documentata; firma su
pagina quasi vuota. Gold non alterato, layout Microsoft Word non verificato.
Controllati 18 hash Minervino e 11 Labirinto, manifest e credenziali nel bundle.
Sessioni/compilazioni preesistenti uguali; rigenerati nel live 82 chunk derivati
fuori dalle cinque SOURCE con contenuti canonici identici. Nessuna pretesa di
immutabilità dell'intero DB; differenze del timestamp nella copia documentate.

Fallimenti offline conservati: fingerprint iniziale non serializzava il BLOB,
poi confronto troppo ampio e ispezione incompleta dei soli ID comuni; corretti
con insiemi completi e contenuti canonici. Primo scoring con percorso venv
ridondante emette warning Python, finale nell'ambiente corretto. Nessuna
chiamata ripetuta o risultato scartato per questi problemi diagnostici.

[Rapporto](docs/baseline-minervino-b0-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-minervino-b0.json),
[bundle](docs/benchmarks/2026-10-16-minervino-b0-audit.tar.gz).
Raw b0-minervino-20261016T154354Z/; 348 file, 6.423.265 byte,
SHA-256 85d2d441e0edb297a4d4955929eca8c8ca3c61545fef1be6de5f9575c69009ee.
Word/PDF B0-RUN-01/02/03 in nuovi dati per revisione. Nessuna suite applicativa,
modifica al motore o gold, commit/push. Prossimo passo: contratto minimo E1,
poi confronto del FORM completo compatto; E2 e correzioni di flusso separati.

## 16 ottobre 2026 — proposta concreta del primo passo E1

L'utente chiede da dove iniziare E1. Ispezione offline del codice e dell'input
reale B0: FORM 126.928 caratteri, blocks 63.758 e candidates 62.947. Ripetizioni
di location, slot_context, ancore e 267 section_ids vuoti. Sono misure della
rappresentazione attuale, non risparmi già ottenuti o nuovi token provider.

Registrato il [contratto proposto](docs/contratto-e1-form-compatto.md): proiezione
deterministica dal catalogo canonico, ID invariati, contesti condivisi e dati
writer conservati nel backend. Prima versione prudente conserva testo originale
e viste marcate per non alterare il protocollo delle citazioni; tabelle,
intestazioni, tipi/protezioni, controlli e relazioni devono rimanere equivalenti.
Verifica delle 267 destinazioni e delle associazioni prima del provider.

Primo risultato proposto: confronto offline B0/E1 completo; poi serializzatore
nel solo banco di prova e tre analisi con continuazione fino al Word. Fonti,
schema output, modello/thinking, validatori e copione uguali a B0, adattamenti
necessari del prompt acquisiti. Decisioni iniziali USER, binding SOURCE,
domande e layout restano interventi separati. Nessuna soglia di risparmio
promessa, nessuna equivalenza statistica presunta da tre prove.

Solo proposta e continuità documentale; nessun codice applicativo, nuovo input
E1 materializzato, chiamata provider, modifica DB/fixture/gold, commit o push.
Controlli documentali e riferimenti; nessuna suite applicativa rieseguita.

## 16 ottobre 2026 — E1 compact-v1 approvato, tre analisi e tre Word

Utente autorizza implementazione E1, approccio sperimentale e test da salvare
in STATUS. Proiezione deterministica in compilation_form_view.py, solo nel
runner con --form-view compact-v1; default full e produzione invariati.
Metadati condivisi per contesto, testi/marker e topologia esatti, mapping writer
canonico. Aggiunti prepare-only e guard contro input diverso dal B0 congelato.

Preflight: FORM 126.928→81.209 caratteri (-36,02%), messaggi 264.951→220.519
(-16,77%), incluso prompt di lettura +1.287 caratteri. 267 destinazioni,
142 contesti; SOURCE/USER/schema/reading plan identici. Contratto e hash del
codice congelati prima delle tre chiamate, stesso DeepSeek/thinking/budget B0.
Scorer copiato identico, gold/fixture/fonti/validatori/writer invariati.

Test mirati iniziali: 110 passati/quattro falliti, 6,21 s. I nuovi test
assumevano campi inline accanto a native checkbox che il parser attuale omette;
corrette solo le aspettative, limite conservato e registrato. Finali **116
mirati passati, 5,84 s; 2.258 backend passati, 166,87 s; Ruff completo passato**.
Test su originali Minervino/Labirinto/Catanzaro, sezioni, firme/tipi, riferimenti,
controlli legacy/content control e stati, tabelle unite/annidate/intestazioni,
parti in sola lettura, perdite/associazioni alterate respinte e proprietà future
sconosciute non eliminate. Test runner con provider simulato, non prova qualità.
Nessuna modifica frontend o nuova suite frontend.

Tre analisi reali auditate: input 63.661 ciascuna contro 75.864 (-16,09%);
output 36.542/26.692/40.473, tempi 150,96/102,40/166,16 s. Totale medio analisi
98.230 contro 115.938 (-15,27%). Cache prima E1 solo 6.400 hit, poi 63.488;
B0 tutto caldo. Non attribuire il tempo alla sola lunghezza e non stimare costi
monetari dal totale. Nessun timeout/retry/risultato scartato.

Valori proposti conformi 18/25/23; conformi con grounding 13/19/21 contro
21/17/21 B0. Word **14/11/23 su 60**, B0 23/17/22; provenienza effettiva
13 SOURCE+1 USER, 11 SOURCE, 21 SOURCE+2 USER. Società omessa nel primo,
tutti i 24 dati dei soci omessi nei tre E1. Comune corretto nel terzo,
indirizzo eccessivo nel secondo; rifiuti di ancoraggio/ruolo e checkbox persistono.
Nessuno dei quattro argomenti USER chiesto; nessuna preferenza/casella true
attesa, conservati tutti i vuoti e stati false. Nessun punteggio su 267 che
mascheri le omissioni. Tre campioni non dimostrano equivalenza statistica.

Tre continuazioni isolate con le risposte reali dopo controlli canonico/proiezione/
audit uguali; servizi reali, non browser/endpoint HTTP o ingestion. Risposte solo
al tema chiesto. Run 2 fermato sulla riconferma di fatti SOURCE fuori dal copione,
poi export parziale esplicito; nessuna nuova attestazione creata per migliorarlo.
27 chiamate totali, 413.624 token: percorsi diversi da B0, no confronto diretto
di costo per pratica. Tutti gli output e passaggi conservati.

Controllate tutte le 267 destinazioni nel DOCX e altre 15 parti ZIP preservate;
LibreOffice dieci pagine per bozza, viste pagine 1/3/10 di tutte, firma su pagina
quasi vuota. Word Microsoft non certificato. 18 hash Minervino e 11 Labirinto,
cinque SOURCE live bit-identiche e preesistenti 49 conversazioni/28 sessioni/
464 revisioni/16 compilazioni uguali; non immutabilità dell'intero DB.

[Rapporto](docs/esperimento-e1-form-compatto-2026-10-16.md),
[misure](docs/benchmarks/2026-10-16-e1-form.json),
[bundle](docs/benchmarks/2026-10-16-e1-form-audit.tar.gz).
Raw e1-form-20261016-01/; archivio 386 file, 6.711.650 byte, SHA-256
9cafd05bb2db9d4180aa37d9d47cfb79ad88b9b8bb7bd4a26bdf2215af6516d5.
Word/PDF E1-RUN-01/02/03 in nuovi dati. Nessun DB/credenziale nell'archivio,
commit/push o migrazione. Cancellazioni/modifiche preesistenti conservate.

**Decisione:** compact-v1 resta sperimentale. Input più piccolo dimostrato,
qualità non stabilizzata, media Word 16 contro 20,67 B0. Proposta successiva:
nuova E1 con indice diretto candidate_id e contesti condivisi, da congelare e
misurare; non implementata. E2 e correzioni USER/validazione/dialogo separate.

## 17 ottobre 2026 — E1 compact-index-v2, esito negativo di affidabilità

Seconda variante approvata dall'utente dopo compact-v1: indice diretto per
candidate_id, type/context_id espliciti, relazioni condivise in form.contexts.
Modulo completo e 267 destinazioni, niente estratti. FORM -30,26% caratteri,
messaggi -14,02%; sole istruzioni di lettura adattate (+1.258 caratteri).
Guard input canonico identico B0 prima di ogni chiamata, v1 riprodotto esattamente.
Fonti/USER/schema/validatori/writer/modello/thinking/budget e scorer invariati;
gold fuori dal prompt. Protocollo e codice congelati prima dei risultati.

Tre analisi reali sequenziali, zero retry o scarti: prima JSON completo rifiutato
per extra root proposal_stage/project_id; seconda HTTP 200 length con JSON
tronco al limite 49.152 output; terza accettata, 23 proposte conformi e 21
grounded, due rifiuti FORM. Nessuna eliminazione di chiavi extra, riparazione
JSON o Word dei due run falliti. Nel primo 25 corrispondenze grezze su 27,
non un audit accettato; punteggio del secondo non disponibile.

Input 65.770 token ciascuna (-13,31% B0, +3,31% v1); output
39.871/49.152/36.508, reasoning 32.272/44.316/29.806, tempi
173,44/214,62/159,94 s. Medie comprendono tutti i run: totale token analisi
107.613,67 (-7,18% B0), output 41.843,67 (+4,42%), tempo 182,67 contro
170,14 B0. Cache prima 6.400 hit, poi 65.536; B0 tutto caldo, misure
storiche di altro giorno, provider backend non fissato. Nessuna fattura,
non inferiorità statistica o causalità della sola lunghezza dichiarate.

Solo terzo continuato nei servizi isolati dopo input/proiezione/audit uguali,
sei ulteriori chiamate. Ripetizione T0 sulle due condizioni chieste; nessuno
dei quattro argomenti USER del copione domandato. Un Word parziale esplicito,
21/60 conformi tutti SOURCE: 8 iniziali, 9 società, zero 24 soci, 4 direttore.
Zero testi USER/preferenze/checkbox true attese; vuoti/false tutti preservati.
Non si calcola media Word sui soli successi: N/D per run 01/02 e affidabilità
1/3 contro 3/3 B0/v1. Nove chiamate totali, 353.942 token, minor percorso
anche per fallimenti precoci, non minor costo per pratica completata.

**137 test mirati passati in 7,61 s; 2.279 backend passati in 170,27 s;
Ruff completo passato.** Iniziale E501 di una riga corretto prima del freeze,
log conservato; nessun fallimento pytest. Software con mock distinto da
qualità reale; frontend non modificato/testato. Tutte le 267 destinazioni e
110 celle del DOCX verificate, altre 15 parti ZIP e insiemi preservati.
LibreOffice dieci pagine, viste 1/3/10, firma ancora su pagina quasi vuota;
Microsoft Word non verificato. 18 hash Minervino, 11 Labirinto e cinque file
SOURCE live identici; preesistenti 49 conversazioni/28 sessioni/464 revisioni/
16 compilazioni uguali alla copia iniziale esclusi solo nuovi oggetti run 03.
Nessuna pretesa di immutabilità binaria dell'intero DB.

[Rapporto](docs/esperimento-e1-index-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-e1-index.json),
[bundle](docs/benchmarks/2026-10-17-e1-index-audit.tar.gz),
[verifiche](docs/benchmarks/2026-10-17-e1-index-checks.json).
Raw e1-index-20261017-01/; archivio 250 file, 3.250.464 byte, SHA-256
e0f586cf03775c9a699be31b7d75d704af5b61609411fbbdb13d74284dda33fc.
Word/PDF E1INDEX-RUN-03 in nuovi dati, nessun output per i due fallimenti.
Nessun DB/credenziale nel bundle, modifica fixture/gold/motore operativo,
migrazione, commit o push. Cancellazioni/modifiche dell'utente preservate.

**Decisione:** seconda variante conservata nel runner, non adottata nella chat.
Input più piccolo, nessuna affidabilità migliore osservata. Non prova che ogni
compattazione sia inefficace o che l'indice isolatamente causi gli errori.
Proposto prossimo confronto separato su contratto output e budget reasoning,
una variabile per serie: non implementato né già approvato. E2 non avviato;
USER iniziali, binding dei dati personali, soci e domande restano separati.

## 17 ottobre 2026 — stop FORM e diagnosi offline delle nove risposte

Su richiesta esplicita, stop agli esperimenti di compattazione del FORM:
B0 resta riferimento, E1 e indice diretto non da integrare. Analisi dei soli
artefatti esistenti, zero nuove chiamate LLM e nessuna modifica a codice,
prompt, validatori, writer o fixture; nessun commit.

INDEX-01: HTTP 200 stop, JSON sintatticamente valido, due proprietà root
vietate causano rifiuto globale. 25 valori conformi grezzi persi; non audit
locale. INDEX-02: HTTP 200 length al limite 49.152, di cui 44.316 reasoning,
JSON tronco nei facts prima di coverage. Nessuno dei due è timeout; writer
non raggiunto. Richieste json_object, schema di dominio verificato localmente.

Nove analisi: 349.460 token output, 273.801 reasoning (78,35%), 75.659 residui
non reasoning. Otto JSON completi già minificati: 634 record, zero duplicati
esatti; 162 fatti tutti referenziati, zero duplicati sui cinque attributi
fattuali. Un solo ID duplicato coverage (p64.cb0 B0-02). 210 record coverage,
1.907 occorrenze ID, 75.296 caratteri su 220.034 (34,22%). Coverage è osservabilità
usata dall'audit/narratore, non prova SOURCE o piano di scrittura: distinguerla
da duplicati eliminabili. Nessuna ripartizione token per sezione disponibile.

Verifica sui messaggi USER realmente inviati: 60 target SOURCE × 9 = 540 prove
presenti, quote contigue normalizzate nel documento corretto. SOURCE e reading
plan identici, 56 chunk / 63.655 caratteri / cinque file. Soci in chunk -54, righe
assenti soltanto dall'indice ausiliario delle proprietà. user_values vuoto:
scelte T0 della chat non trasferite all'analisi. Non ogni omissione è una
semplice mancata lettura; associazioni USER/ruolo restano distinte dai valori.

Sette audit: 49 occorrenze conformi bloccate, 32 destinazioni distinte;
B0 1/5/28, E1 5/6/2, INDEX-03 due. Cause primarie disgiunte: 8 quote FORM,
23 binding ruolo, 16 collegamenti record/chunk, 2 citazioni SOURCE senza valore
completo. Tutti i 24 soci proposti da B0-03 bloccati; una occorrenza ha anche
errore SOURCE. Valore corretto nel gold non rende corretta la citazione usata.
Separati 25 valori conformi persi al gate globale INDEX-01; INDEX-02 non valutato.

Proposta minima, soltanto documentale: mantenere FORM B0 e una chiamata
globale, richiedere coverage sparsa invece di esaustiva, consentendo [] già
ammessa nello schema. Core fattuale, condizioni, ruoli e controlli invariati;
residui esplicitamente UNEXPLAINED/da valutare, non assenza SOURCE o risolti.
Trade-off: meno spiegazioni delle omissioni. Solo controfattuale di dimensioni
sui tre B0: -35,67%/-31,01%/-24,71% caratteri JSON visibili. Nessun effetto
su token/reasoning/qualità provato; il troncamento precede coverage. Non
implementato e non autorizza un nuovo esperimento automaticamente.

[Rapporto](docs/diagnosi-contratto-risposta-b0-e1-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-output-diagnosis.json),
[bundle derivati](docs/benchmarks/2026-10-17-output-diagnosis-audit.tar.gz),
[verifiche](docs/benchmarks/2026-10-17-output-diagnosis-checks.json).
Raw diagnosi-output-b0-e1-20261017-01/. Hash di 1.227 file protetti controllati,
originali invariati, controlli JSON/CSV/link/diff; nessuna suite software
ripetuta. Primo assertion offline per newline di archiviazione corretto
nel confronto, senza modificare risposte o ripetere chiamate. Fatti osservati
e ipotesi separati; nessuna causalità attribuita alla compattazione da sola.

Archivio dei derivati: 18 file, 99.771 byte, SHA-256
`080bb3190e05e1c7b68a36e40a5a37056683af42b99074dfd1b06c6f1380ec65`.

## 17 ottobre 2026 — replay INDEX-01, USER e thinking, coverage invariato

Intervento richiesto prima di modificare coverage: replay root fino al DOCX,
trasporto USER registrati, capacità thinking reali e soci B0-03. Zero nuove
generazioni; un solo GET /models non generativo. Nessuna compattazione FORM,
modifica schema/coverage/validatori/writer o commit/push.

INDEX-01 originale preservato e rifiuto riprodotto. Separati soltanto due
metadati, schema pieno passato: 27 proposte, 20 fatti; 19 grounded e 18 conformi.
Un rifiuto FORM e sette collegamenti personali restano; p41.s1 indirizzo intero
passa i gate, ma resta non conforme al comune. Senza conferme, export dei 19
respinto 409; copia vuota solo con allow_empty esplicito. Test distinto con
risposte USER archiviate, apply_replies e mapping dichiarato delle condizioni:
DOCX con 19 SOURCE/18 conformi, zero campi USER. Selezione controllata per
verifica exporter, nessun giudizio sul narratore o nuovo run di qualità.
Entrambe le analisi senza USER; INDEX-01 rimane un fallimento storico.

Implementato solo trasporto USER: turni start dell'esatta sessione con join
conversazione/progetto; citazione letterale distinta da decisione accettata.
Ricevute solo dal proprio registro con provenienza e ambito coerenti, nessuna
inferenza di firmatario/partecipazione, risposta AI o cronologia generica.
_prepare alimenta user_context separato, user_values [], nessuna applicazione
ai campi. Istruzioni aggiuntive soltanto con USER; senza USER input e request
esattamente B0. T0 registrato acquisito NOT-SENT, qualità reale non misurata.
Nessuna migrazione o riapertura automatica delle sessioni storiche.

GET /models HTTP200: deepseek-flash, nome corrente DeepSeek-V4.1-Flash,
low/high/max. API documenta disabled/none; B0 già low, minimal alias low,
nessun cap reasoning indipendente documentato. Pilot minimo proposto ma non
eseguito: due chiamate fresche A enabled/low, B disabled senza effort, stesso
B0 completo senza USER, messaggi/schema/coverage/max_tokens 49.152/timeout300.
Body pronti ma non inviati; runtime globale continua a forzare thinking
DeepSeek. Cache, backend, campionamento e due campioni limitano le conclusioni.

Soci B0-03: 24 valori conformi, 23 fatti grounded, una quote insufficiente
p46.s0. Tre binding respinti per ruolo letterale non presente in ciascuna
citazione (socio/Soci e riga senza ruolo). Nove valori citano chunk esterni
al binding, 15 gli stessi chunk: nessuna stima di guadagno dal solo plurale.
Nessun nuovo ruolo o attribuzione inventati per superare i gate.

**79 mirati passati in 9,33 s; 2.304 backend in 168,46 s; Ruff passato.**
Iniziale lint con otto diagnostiche import fixture risolte e conservate;
acquisizione offline AISettings senza api_key corretta con oggetto minimo,
zero generazioni ripetute. 534 destinazioni, 220 celle, parti ZIP preservate;
due DOCX/PDF dieci pagine, viste 1/3/10 con conferme, firma isolata. Frontend
invariato/non testato; Microsoft Word non certificato. Entità live preesistenti
49/28/464/16 e cinque SOURCE identiche, vecchi audit/fixture invariati.
Funzioni gate AST identiche; soli input/request e nuovo lettore USER modificati.

[Rapporto](docs/replay-index01-user-reasoning-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-root-user-reasoning.json),
[bundle](docs/benchmarks/2026-10-17-root-user-reasoning-audit.tar.gz).
Raw root-user-reasoning-20261017-01/. Runtime SQLite privato escluso e richiesto
per ripetere lo script completo dei servizi, limite documentato. Coverage
sospeso e B0 riferimento; eventuale pilot thinking da approvare, distinto
dalle valutazioni con USER. Nessun commit o push.

Archivio: 149 file, 3.516.747 byte; SHA-256
`24799ce17ac5baa66c63367ddda807e97cf72f0a13eaab90f71b7770021c987f`.

## 17 ottobre 2026 — spiegazione della catena persona–ruolo

Sola analisi dei vecchi artefatti per rispondere a proposta, citazione,
costruzione del binding, controllo esatto e natura del rifiuto. Zero richieste
provider, nuovi replay o export. Codice, prompt, FORM, schema, coverage,
validatori e writer invariati in questo chiarimento; nessun commit/push.

Il modello costruisce gli abbinamenti fact_id/binding_id. Il binding non ha
subject: la persona è letta dal fatto nella verifica per campo. Esempi tracciati:
Luca Ingegnere/7294, ordine di Elisa direttore, provincia di Elisa socio.
Soci: 24 valori conformi al gold, 23 fatti grounded, tre binding respinti per
ruolo letterale in ogni quote; 23 campi REVIEW_REQUIRED e uno REJECTED. Dati
presenti nella tabella, relazione titolo–riga non supportata dal contratto.
INDEX-01: ordine citato da -55 e binding -45; prove separatamente valide ma
catena di attribuzione non accettata. Ordine e ruolo disponibili anche nel
record -45: scelta delle citazioni del modello e limiti del verificatore,
non assenza del dato. Il controllo è quello del precedente replay root,
non un nuovo esito favorevole della chiamata originaria.

Rifiuto corretto distinto per Bari (BA): la quote scelta per Elisa non contiene
il valore completo; una sua occorrenza nel chunk, nella riga di Andrea, non
può sostituire la prova personale. Condizione di partecipazione USER distinta
dal grounding. Nessuna scrivibilità stimata dopo ipotetiche correzioni.

[Analisi](docs/analisi-binding-persona-ruolo-2026-10-17.md),
[estratti, tre SOURCE e hash di dodici file](docs/benchmarks/2026-10-17-binding-persona-ruolo.json).
Verifiche documentali e dei conteggi soltanto; suite software non rieseguite.
Gli artefatti grezzi e i bundle precedenti rimangono i riferimenti, invariati.

## 17 ottobre 2026 — correzione KISS dei binding e replay offline

Modifica autorizzata del verificatore V12: prova di ruolo da titolo/colonne/riga
della stessa tabella Markdown e fallback sui record SOURCE già citati dal fatto.
Nessun framework, ruolo o ID specifico del benchmark, nuovo documento cercato
o collegamento arbitrario fra persone/chunk. Negazioni, ambiguità e provenienza
restano controllate; il valore deve sempre comparire nella propria quote.
Applicabilità e contesto FORM non vengono approvati dal nuovo riscontro SOURCE.

Test prima del codice: red corretto con quattro fallimenti positivi attesi e
30 protezioni passate; log iniziale con tre difetti della fixture conservato.
Prima implementazione con due fallimenti plurale -io, risolta con regola
grammaticale generica. Finali: 40 nuovi casi, 133 mirati passati in 5,65 s,
2.344 backend in 188,62 s, Ruff. Provider simulati nei test software; frontend
invariato/non ritestato. Nessuna nuova generazione o richiesta provider reale.

Riprodotti esattamente i due audit precedenti prima del cambiamento. Replay
su output fissi B0-03 e INDEX-01 già isolato dai due metadati root: fatti,
condizioni, SOURCE e proposte invariate, nessun USER. B0 grounded 22→28 con
6 recuperi conformi (4 soci, 2 direttore); INDEX 19→24 con 5 recuperi conformi.
11 occorrenze/9 destinazioni distinte, nessuna proposta grounded persa, tutti
i recuperi ancora condizionati REVIEW_REQUIRED e 0 RESOLVED/0 scritture.
INDEX originale rimane respinto allo schema, nessun filtro root in produzione.
Primo avvio script senza PYTHONPATH fermato prima del replay, ambiente corretto
e log conservato. Nessun export DOCX o modifica di sessioni live.

Residui B0: 2 destinazioni con lo stesso fatto Bari (BA) non provato dalla quote,
18 ulteriori campi con contesto FORM non ammesso e 2 senza ruolo nel record
del valore. Il gate FORM compare su 19 campi, uno già contato per quote errata;
7294 rimane bloccato da quel contesto. INDEX: 1 quote FORM insufficiente e
2 record SOURCE senza ruolo di direttore. Non presentare questi residui come
assenza generalizzata dei dati in KB. La provincia INDEX è fattualmente citata
dalla tabella, ma non passa l'attribuzione al direttore: caso diverso da B0.

Nessuna nuova accettazione indebita osservata nei recuperi e nei test negativi.
Resta l'errore preesistente p41.s1, indirizzo completo nel campo Comune, in
entrambe le risposte: 2 occorrenze dello stesso difetto, nessuna correzione
fuori scope. Non dichiarare zero errori nell'intero sistema o qualità di nuove
generazioni. Misura locale sulle risposte fisse; nessun miglioramento DOCX misurato.

Modificati solo due file produzione, nuovo test; 10.752/10.754 file protetti
invariati. FORM, prompt, thinking, schema, API, writer, fixture e vecchi audit
preservati. [Rapporto](docs/correzione-binding-kiss-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-binding-kiss.json),
[bundle](docs/benchmarks/2026-10-17-binding-kiss-audit.tar.gz).
Raw binding-kiss-20261017-01/. Fermato dopo replay e rapporto come richiesto;
nessun commit/push, migrazione o upgrade automatico delle sessioni.
Bundle verificato: 40 file, 5.292.563 byte non compressi, SHA-256
`79ea9798c5fa744732e81203226a3f2ae290325cba633028745d20f6ddacd3cb`.

## 17 ottobre 2026 — Comune e contesto FORM, replay senza LLM

Richiesta: compatibilità valore/campo e diagnosi dei 18 rifiuti FORM, correggendo
solo una causa comune dimostrata. Regole SOURCE KISS mantenute, zero nuove
richieste provider, USER o export. Riprodotti esattamente i due audit KISS prima
della modifica; output modello, fonti e gold congelati.

Comune: validatore condiviso legge la label fisica e i componenti separati
dell'indirizzo. L'indirizzo completo letteralmente SOURCE non è ammissibile
nel Comune di p41.s1, preceduto da sede legale in e seguito da provincia/via/n.
Nessuna estrazione di Bari o nuova citazione. Campi indirizzo e richieste
Comune+indirizzo restano ammessi; il nome suggerito dal modello non governa il tipo.
Verifica limitata alla compatibilità deterministica del difetto osservato,
non un nuovo motore semantico generale.

Diagnosi 18: prova FORM sufficiente in tutti, quote realmente insufficienti 0,
sezioni dimostrate false 0, associazioni del modello a ruolo FORM diverso 0.
18 condizioni sconosciute, nessuna selezione dedotta. Backend non conserva
introduzione di ruolo in paragrafo con campi; elenco di sette paragrafi con
tre schede letteralmente identiche su 2/2/3 paragrafi. Sei campi in nuovi membri
e dodici continuazioni. p46.s0 è un ulteriore caso con fatto già rifiutato.
Correzione V12: numerazione consecutiva da 1, almeno due schede identiche,
quote introduttiva dopo ultimo placeholder, subject coerente per membro,
massimo 12 paragrafi, barriere esplicite e audit della prova. Nessun cambiamento
al catalogo o al FORM: input B0 completo esattamente uguale a quello salvato.

Replay B0: grounded 28→38, conformi 27→38, +11 corretti/-1 errato. INDEX con
soli metadati root già isolati: grounded 24→23, corretti 23→23, -1 errato.
Nessuna proposta corretta persa, tutti i vecchi recuperi KISS conservati.
Tutti i 18 FORM riconosciuti; sette restano rifiutati per attribuzione SOURCE.
Fatti e condizioni identici, 0 RESOLVED/0 scritture; nuovi recuperi soltanto
ipotesi conditional. Originale INDEX ancora respinto allo schema, nessun
filtro root o successo storico riscritto.

Residui 12+4: due Comune incompatibili, due destinazioni con lo stesso fatto
Bari (BA) non provato dalla quote, un FORM con solo marker e undici record
SOURCE privi dell'attribuzione richiesta nel chunk del valore. Nessuna nuova
accettazione indebita osservata nei replay finali; zero grounded non conformi
al gold sui due output, senza certificazione generale di correttezza futura.

Test scritti prima: sei fallimenti attesi/22 protezioni passate. Aggiunti due
controesempi: prima lista accettava campo di ruolo senza colon, risolto con
schema ripetuto; primo Comune respingeva richiesta composita, corretta. Log
conservati. 30 nuovi casi finali; 211 mirati passati in 9,78 s, 2.374 backend
in 206,57 s, Ruff. Un E501 di test e la lettura di form_evidence su campo già
respinto corretti, senza nuovi dati o chiamate. Frontend invariato/non testato.

10.793/10.795 file protetti invariati. Cambiano solo compilation_global.py e
document_compilation.py, nuovo test; Fonte KISS, prompt, schema, API, writer,
modello/thinking, fixture e vecchi audit preservati. Nessun commit/push,
migrazione o aggiornamento automatico sessioni. [Rapporto](docs/comune-contesto-form-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-field-context.json),
[bundle](docs/benchmarks/2026-10-17-field-context-audit.tar.gz).
Raw field-context-20261017-01/. Compattazione, coverage e pilot thinking invariati.
Bundle verificato: 47 file, 5.515.935 byte non compressi, SHA-256
`f3d9bdc6f22b0b3837695090ce4ca0a9b8f2347d7011f4cf5517f38071c6fba7`.

## 17 ottobre 2026 — diagnosi degli undici SOURCE residui, sola analisi

Richiesta: distinguere prova assente e collegamento non ricostruito prima di
implementare altre modifiche. Analizzati gli ultimi audit già salvati, senza
rieseguire validatori, provider, dialogo USER o DOCX. Nessun cambiamento a
codice/test software, FORM B0, prompt, contratto, sicurezza o fixture.

11 occorrenze, 9 B0-03 e 2 INDEX-01; dieci destinazioni distinte perché il CF
del direttore si ripete. Un vincolo comune (attribuzione locale nello stesso
chunk) nasconde quattro situazioni: 4 valori esatti già nella riga del binding;
3 nomi con onorifico nella citazione del fatto e senza nella tabella soci;
1 data in lettere contro numerica; 3 collegamenti socio/direttore per CF
(due esecuzioni) e provincia albo. Nessuno degli undici manca del valore o
del ruolo nell'input complessivo. Non equivale a undici accettazioni sicure:
quattro prove congiunte esatte, sette casi con associazione/equivalenza da
definire o verificare. Nessun valore/citazione trasformato.

Fatti riusati fra ruoli con citazioni adatte a uno solo; binding e fatti
separatamente grounded. Il verificatore non usa la propria riga del binding
come prova alternativa e il fallback legge solo i record citati dal fatto.
Per Elisa concordano nome, ordine e 8421 fra record del direttore e tabella,
anche nello stesso documento integrativo; nessuna identità universale
dedotta. I titoli abbreviati sono già ammessi dal confronto sintattico
nel record: la loro forma descrive la differenza, non il controllo fallito.

Preservati gli altri cinque rifiuti. Bari (BA) B0 resta privo del valore
nella quote scelta di Elisa, distinto dalla citazione corretta INDEX della
tabella. Condizioni degli undici tutte unknown, nessun USER nei due input.
Applicabilità rimandata a studio distinto, senza attivazioni o implementazioni.
Date delle cariche da preservare: cessazione Luca amministratore il 1 ottobre,
subentro Leonardo il 2; non sono scelte della pratica né invalidano Luca socio.

[Rapporto](docs/diagnosi-undici-source-2026-10-17.md),
[tracciati e misure](docs/benchmarks/2026-10-17-residual-source-diagnosis.json),
[bundle](docs/benchmarks/2026-10-17-residual-source-diagnosis-audit.tar.gz).
Raw residual-source-20261017-01/, script diagnostico standard library.
Verifiche di conteggi, citazioni esatte, colonne, usi condivisi, provenienza,
identità, hash e riferimenti. I 38/23 grounded restano quelli del precedente
replay; nessun nuovo recupero o misura dei falsi positivi. Suite e Ruff non
rieseguiti. Nessun commit/push, migrazione o modifica ai dati live.

11.006 file protetti verificati invariati; bundle di 17 file, 2.458.181 byte
non compressi. SHA-256
`def45875b6d6aa31d524f229cf1657e2ff3bc079e4541c8e0dd2a2c8bee12c37`.

## 17 ottobre 2026 — ultima correzione SOURCE e replay concluso

Intervento autorizzato dopo la diagnosi degli undici residui. Test prima di
ciascun passo, modificati soltanto compilation_global.py e compilation_role_records.py,
nuovo test_compilation_binding_identity.py. Nessun framework, ID o nome
aziendale nei nuovi controlli. Baseline degli ultimi due audit riprodotta
esattamente, nessun USER aggiunto o provider chiamato.

Primo passo isolato: riuso del valore nella colonna della riga del binding
che attesta persona e ruolo. Replay intermedio B0 38→42 grounded, quattro
recuperi conformi, INDEX 23→23. Nessuna proposta corretta persa, nessuna nuova
accettazione non conforme, 0 RESOLVED/0 scritture. Misura del solo primo passo.

Successivamente aggiunti confronto deterministico titoli/date e collegamento
fra record limitato a CF e provincia della stessa iscrizione, con nome completo
e identificatore personale oppure ordine+numero condivisi. Ruolo, identità,
valore e applicabilità distinti; conflitti espliciti e omonimie mantengono il
rifiuto. I titoli non provano qualifiche o poteri e i valori non vengono riscritti.

57 nuovi casi, 274 mirati passati in 18,92 s e Ruff. Conservati red/controesempi:
provincia con solo CF, attributi mancanti con nota di ruolo, chiavi discordanti
e di altre persone, alias di colonna, quote oltre limite e perdita della prova,
SOURCE del progetto e conflitti nelle righe nominative. Prima suite completa
interrotta per aggiungere gli ultimi due controlli sulle citazioni, non passata;
successiva intermedia 2.427 passata in 217,18 s prima degli ultimi quattro casi.
Suite completa finale passata: 2.431 test in 219,46 s. Nessuna nuova chiamata
LLM o esportazione DOCX; frontend invariato/non ritestato.

Raw backend/data/compilation-audit/binding-final-20261017-01/;
[rapporto](docs/correzione-binding-source-finale-2026-10-17.md),
[misure e tracciati](docs/benchmarks/2026-10-17-binding-final.json),
[bundle](docs/benchmarks/2026-10-17-binding-final-audit.tar.gz).
FORM B0, schema, writer, API, modello, thinking, fixture e vecchi audit invariati.
Nessun commit/push, migrazione o modifica alle sessioni live.

Finale B0 grounded 38→47 (+9 corretti), INDEX 23→25 (+2 corretti). Recuperati
gli undici residui della diagnosi su dieci destinazioni: quattro celle esatte,
tre nominativi con titolo, una data equivalente, tre collegamenti identità.
Otto prove dirette nella riga del ruolo e tre collegamenti tramite nome,
ordine e numero condivisi, senza inventare CF nel record del direttore.
Nessuna grounded precedente persa, zero nuove accettazioni non conformi al gold;
zero non conformi anche sul totale grounded finale. Cinque rifiuti necessari:
due Comune incompatibili, due destinazioni B0 con Bari (BA) non nella quote
di Elisa e un marker FORM INDEX insufficiente. Nessuna generalizzazione alla
qualità di nuove generazioni o ad altri formati; controesempi intermedi conservati.

Fatti/condizioni identici; tutti gli undici ancora conditional/REVIEW_REQUIRED,
condizioni unknown e 0 RESOLVED/0 scritture. SOURCE del progetto autorizzato
ammesse, General e fonti estranee respinte. 11.021/11.023 file protetti invariati,
soli due file verificatore diversi e nuovo test. Arresto dopo replay/rapporto,
senza avviare altri esperimenti o interventi sull'applicabilità.

Bundle verificato: 68 file, 6.634.686 byte non compressi; SHA-256
`efd1a6f0292443c19fae1459cdf8b04a36b69fc9bfc7132643b03a42a68b1087`.

## 17 ottobre 2026 — applicabilità UNKNOWN, diagnosi senza modifiche

Fase binding chiusa. Analizzati i tre predicati dei due output e le ricevute
USER archiviate: B0 c_p39 copre 47 proposte; INDEX c_op 9, c_branch_soc 16.
Tutti semantic con operandi vuoti: il backend verifica l'ancoraggio FORM e
mantiene UNKNOWN, non esegue inferenze di verità. Le risposte USER sono in
un registro distinto, non mutano l'audit. B0 mescola dati generali e ramo
societario; la relazione è proposta dal modello, non clausola p14–p17.

B0-03 ha già proprie ricevute c_p39=true, nome Leonardo p12.s0 e consenso
storico all'export. INDEX-01 originario non produce stato di sessione valido;
le conferme nella copia offline sono trasferimento esplicito di test da
INDEX-03, non dati della chiamata originale. Separati natura S.r.l., attività,
scelta della pratica, firmatario USER e carica/poteri SOURCE. Leonardo è
rappresentante esplicito dal 2 ottobre, Luca cessato il 1 ottobre; non si
attribuiscono mandati o poteri speciali né si deduce firmatario dal direttore.

Preflight nuovi senza writer/DB: 47 B0, 25 INDEX e nome USER passano inalterati.
Proiezione read-only sul dialogo proprio B0: 21 vecchie proposte ancora valide,
1 Comune respinto e 26 nuove grounded senza precedente review. Conferma non
equivale a revisione; nessun nuovo booleano o reviewed fabbricato. Mancano
choice_groups in entrambi gli output: c_p39=true non scrive la checkbox.
Copione T1 esistente non equivale a risposte fornite: temi non chiesti nei dialoghi.

Piano minimo da discutere: replay isolato B0 con ricevute proprie, controllo
semantico dell'intera condizione, revisione 26 nuove, export parziale con
servizi esistenti e verifiche XML/report/PDF/hash. Obiettivo pianificato 47
SOURCE + 1 nome USER, non un DOCX prodotto. Il nome resta USER nel registro,
non nuovo recupero SOURCE; gold resta fuori dalle prove. Lacune SOURCE del
modello B0 13/INDEX 35, distinti omissioni/rifiuti. Firma, native, T1 e
documenti personali restano separati, nessuna dichiarazione di presentabilità.

[Rapporto](docs/applicabilita-b0-index-2026-10-17.md),
[registro e misure](docs/benchmarks/2026-10-17-applicability.json),
[backup](docs/benchmarks/2026-10-17-applicability-audit.tar.gz).
Raw applicability-20261017-01/. Nessuna modifica di codice, test, controlli,
FORM, writer, API, modello o sessioni live, nessun LLM/commit/push/export.
Suite/Ruff non rieseguiti; 73 controlli puri, conteggi, confronti, proiezione
read-only e verifiche documentali/hash. Piano non eseguito, nessuna nuova
architettura o implementazione avviata.

Integrità: 11.092/11.092 file protetti e 14 artefatti letti invariati.
Bundle verificato: 21 file, 2.573.411 byte non compressi; SHA-256
`4c7d1f1f6e20d024d7c9193f94f25a5e060fea68189c44dc97b6c9659a78b2a7`.

## 17 ottobre 2026 — B0-03, export parziale reale e verificato

Eseguito il piano sulla copia isolata della stessa sessione B0-03. Documento
concreto: [Word](<nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.docx>) e
[PDF](<nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.pdf>).
[Rapporto](docs/export-b0-03-verificato-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-b0-docx-verified.json).

47 grounded SOURCE attuali, riesaminate manualmente le26 pendenti (23 soci,
3 direttore) e riconfermate le21 vecchie valide. Ricevute USER proprie e
consenso storico conservati, nessuna risposta inventata o da INDEX. Verificati
natura giuridica, pratica, firmatario, ruolo e sottoalternativa tecnica.
La dipendenza p39 dei9 dati generali è un'associazione del modello, conservata
nell'audit e registrata come limite; guard senza conferma ancora409.

Export esistente: 48 valori scritti, 47 SOURCE e1 nome USER. Prima23 valori,
22 conformi: rimosso il Comune errato e aggiunti26 valori, ora48 conformi sui
60 target testuali SOURCE del gold, di cui1 resta USER. Tre rifiuti mantenuti,
12 target SOURCE ancora vuoti; T1, preferenze, firma e native non inventati.
È un risultato con revisione manuale assistita, non qualità di nuove chiamate
né autonomia del narratore. Gold letto solo dopo l'export e la verifica XML.

Audit con1 condizione UNKNOWN e47 proposte ancora conditional; overlay USER
con c_p39 confermato. Zero condizioni mancanti sui selezionati. Il report
standard dichiara reviewed_by=USER: la nuova review è manuale di Codex su
istruzione dell'utente, non una nuova ricevuta storica o una verifica LLM
indipendente; autore/metodo nel registro aggiuntivo. Sessioni originali intatte.

Controlli fisici: 48 valori nelle rispettive posizioni, altri segnaposti e
prestampato invariati; ZIP/CRC,12 relazioni,246 paragrafi+avviso,4 tabelle e
13 checkbox conservati. Cambia soltanto word/document.xml. PDF9 pagine contro
10 originale, tutte9 viste: firma vuota e unita a pagina9, lettere a/b/c/d
preservate. Cinque giunzioni senza spazio su4 paragrafi osservate e registrate,
nessun intervento sul writer o ritocco DOCX. Stato needs_review mantenuto.

Raw b0-docx-verified-20261017-01/, runtime .tools/b0-docx-verified-20261017-01/export-01/.
Conservati log falliti di confronto metadati grezzi/canonici e dell'estrattore
di verifica prima di gestire i marcatori Word; output non modificato. Zero
nuove chiamate LLM, codice applicativo, framework, commit/push. Suite/Ruff
non rieseguiti, verifiche dirette dei guard e del documento reale. DOCX SHA256
`6605dcc91ab823cc21d77618c2991feade366cce1137d4b8138600f1c051a889`.

Integrità finale: 11.455/11.455 file protetti invariati, incluse sessioni
storiche/runtime e dati live. [Backup](docs/benchmarks/2026-10-17-b0-docx-verified-audit.tar.gz)
verificato: 75 file, 10.911.253 byte non compressi; SHA256
`b396c7d7ba20d80463466ae03f492279585d26e5a930d8d81bd1ab61538172e2`.

## 17 ottobre 2026 — disponibilità delle correzioni nella UI

Su richiesta dell'utente avviati backend8000/frontend5173 con ./start.sh e codice
corrente. Binding, Comune, FORM e trasporto USER sono già nel percorso globale
applicativo: nessun secondo motore o import delle48review manuali del benchmark.
Modulo live e56SOURCE identici al congelato; input canonico senzaUSER ugualeB0.
[Guida alla prova](docs/prova-ui-compilazione-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-ui-binding.json).

298 test backend mirati passati in36,28s,8 E2E desktop/mobile in23,9s e lint
frontend. Provider/API simulati nei test, DB isolati. Prima E2E7pass/1fail:
asserzione obsoleta attendeva Sto lavorando invece dello status Analizzo il
modulo; corretto solo frontend/e2e/global-compilation.spec.ts. Fallimento,
screenshot e trace conservati. Smoke browser sulla veraUI: progetto e mention
DOCX aperti senza messaggi inviati, mutazioni, nuove sessioni o chiamate AI.
28sessioni/versioni/stati e conteggi principali invariati dopo l'avvio.

Le48scritture verificate offline non sono una promessa di risultato automatico:
revisione manuale non promossa a nuova decisione USER. Narratore corrente con
limite40SOURCE per passo, scope c_p39 e altre limitazioni conservate. Nuove
conversazioni per provare i controlli aggiornati, vecchie sessioni inalterate.
La prova qualitativa col provider verrà dall'utente; nessuna generazione nuova
eseguita qui. Nessun writer, modello/thinking o codice applicativo modificato,
nessuna nuova architettura, commit/push. Backup preventivo privato del DB;
raw ui-binding-20261017-01/, servizi lasciati attivi.

[Backup](docs/benchmarks/2026-10-17-ui-binding-audit.tar.gz) verificato:22file,
783.192byte non compressi; SHA256
`cc25fbe50c3dad5253a525f5184a36b0fe97be297f0251a885a6d16fa8cf18a9`.
DB privato escluso; log server vivo escluso e sostituito da snapshot nel bundle.

## 17 ottobre 2026 — diagnosi del download reale compilato(6)

L'utente ha compilato dalla UI e chiesto soltanto spiegazioni. Analizzato il
Word root, identico al server:25scritture,24SOURCE e nomeUSER. Valori25/25
conformi ai target sintetici; non è completezza o validazione di ogni citazione.
35 target SOURCE vuoti:8firmatario,24soci,1CFdirettore omessi;2dati generali
Comune/provincia proposti con Bari/BA ma citazioniFORM marker-only respinte.
[Rapporto](docs/analisi-ui-compilato6-2026-10-17.md),
[misure](docs/benchmarks/2026-10-17-ui-compilato6.json).

SOURCE56/FORM/schema identici a B0. Leonardo ha nascita, residenza, CF e carica
nel vero input. T0solo compila, scelta firmatario dopo globale; nome iniziale
incompleto e poi Leonardo Montemurro. La risposta aggiorna solo p12.s0 senza
ricercare la persona o creare proposte sugli8dati collegati. Le3domande sono
perturno, pool dopo nome vuoto: esaurita coda del sistema, non dati necessari.

Soci: modello riconosce tabella ma omette tutte24assegnazioni dichiarando
formato ruolo non valido. Prompt inviato ancora vecchi formati/samechunk,
mentre backend supporta prove strutturali/identità: disallineamento osservato,
contributo causale plausibile non isolato con nuova chiamata. ElisaDT7/8,
CF nella riga soci-54 omesso.7recuperi fact_source_record nel nuovoaudit
confermano verificatore aggiornato effettivamente usato.

Narratore nega dati soci eCFdirettore senza fondamento; rolehint soloDT,
nessuna proiezione della tabella e nessun alert sul CF solo mancante.
24grounded tutte revisionate/scritte, nessuna held: limite40 e UNKNOWN non
causano il calo;2condizioni entrambe confermateUSER. Non è il replaymanuale48
né un confronto controllato con la medesima risposta del modello.

Controllo fisico: slot/report/ZIP e tabelle/native invariati; PDF10pagine,
viste1/3/4/10,2giunzioni senza spazio e firma sola a10. Analisi originale125,8s,
3sintesi6,6s; usage76.163input/32.252output di cui23.325reasoning. Nessuna
chiamata nuova, modifica applicativa/prompt/writer/validatore, replay o
scrittura di sessioni. Nessun nuovo test/Ruff/commit/push. Raw durevoli
ui-compilato6-20261017-01/. Arresto dopo diagnosi come richiesto.

Integrità verificata: 216 file di codice/test e 29 sessioni invariati, 22
artefatti originali identici alle copie. [Backup](docs/benchmarks/2026-10-17-ui-compilato6-audit.tar.gz)
verificato: 64 file, 4.672.942 byte non compressi; SHA-256
`06cde9948a3751105511866cf26f673ed1a9864b938d48d2bd567986a192c0ef`.

## 18 ottobre 2026 — Correzioni mirate dopo la prova UI compilato(6)

[Rapporto](docs/correzioni-ui-compilato6-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-ui-compilato6-fix.json).
Implementazione autorizzata; preservate le modifiche locali precedenti.
API, schema DB, writer, FORM B0 e fixture/gold invariati. Nessun commit/push.

Prima riprodotti i difetti con test mirati: prompt troppo restrittivo, mancanza
del riuso dopo USER e false affermazioni di assenza del narratore. Poi aggiunti
negativi per omonimie anche in tabelle, CF conflittuali/attribuiti a persone
diverse, ruoli cessati, società diversa, fonti General/fuori progetto, ambiti
FORM e versioni precedenti. Rilevati durante lo sviluppo e conservati anche
gli errori intermedi: regressione su una domanda generica, via duplicata,
fallback della domanda sul firmatario omesso dal modello e guard V12.

Riuso deterministico dopo Leonardo, senza nuova globale: nome USER identifica
una persona SOURCE univoca; nascita/residenza/CF/carica conservano proprie prove.
Carica subordinata all'attribuzione alla stessa società dell'operatore; nessun
potere speciale o recapito personale dedotto. Proposte ancora da revisionare,
condizioni non trasformate in TRUE. Output/audit originali intatti e controllo
di freschezza ripetuto all'export. Narratore distingue indizi presenti, omissioni,
scarti e attese; assenza/recupero non dimostrati rimangono non dimostrati.

Replay reale persistente, narratore simulato e router storico rigiocato:
compilato6 passa da25 a33scritture (32SOURCE+nomeUSER); B0-03 mantiene la propria
revisione manuale e passa da48 a56 (55SOURCE+nomeUSER). Non sono nuove valutazioni
del narratore reale. Tutte le scritture controllate fisicamente nel DOCX.

Un solo nuovo campione globale reale, stesso input/modello/thinking/schema,
sole istruzioni SOURCE diverse:19→45fatti,26→51assegnazioni,24→45grounded.
Soci24/24 proposti e grounded; CF direttore proposto. Non prova stabilità tra
generazioni. Dopo la prova precisato nel prompt il limite CF/provincia fra
record, senza un'altra chiamata. Prompt inviato e finale entrambi conservati.
136,7s,76.408input/37.735output,24.441reasoning; nessuna misura di velocità UI.

Nuova proposta dopo riuso:59SOURCEproposti,53grounded,40revisionati e scritti
più nomeUSER=41. Soci16scritti,8grounded non revisionati; insieme a5direttore
sono13proposte escluse dal limite40, non per assenza KB. Sei non grounded:
2FORM marker-only,1indirizzo incompatibile con Comune,3legami professionali
non supportati da quelle citazioni/property. Nessun allentamento dei binding.
Target SOURCE testuali vuoti27/4/19 nei tre export, grounded UNKNOWN live0
dopo le ricevute effettive, checkbox0. Bari/BA iniziali e ramo checkbox restano
irrisolti con causa documentata. Fax attestato dalla SOURCE-53 sintetica.

Una discordanza dal gold per export: carica completa documentata invece del
solo rappresentante legale. Metriche strette32/33,55/56,40/41; gold/scorer non
adattati. Nessuna nuova accettazione fattuale indebita osservata nei controlli,
senza dichiarare accuratezza generale. Via duplicata corretta prima della consegna.
XML/report/slot e ZIP conformi,4tabelle/13controlli invariati, solo document.xml
modificato. PDF10/9/9pagine; controllate UI1/3/10,B0p3,promptp3. Restano giunzioni
senza spazio e firma isolata del replay UI, writer invariato; MS Word non verificato.

Raw durevoli ui-compilato6-fix-20261017-01/; database isolati privati in .tools,
esclusi dal backup pubblico. Test, hash e backup finali registrati nel rapporto
e nelle misure. Nessuna nuova prova su altro bando in questa correzione mirata.
Fermarsi alla consegna, senza avviare il lavoro sul limite40 o sulle checkbox.

Verifica finale:2459test backend passati172,68s, Ruff e git diff--check passati.
Tre export ricontrollati coi guard del codice definitivo senza scritture.
29sessioni live/schemaDB,22artefatti originali e downloadcompilato6 invariati.
Frontend non modificato né ritestato in questa fase.

[Backup verificato](docs/benchmarks/2026-10-18-ui-compilato6-fix-audit.tar.gz):349file,
32.512.735byte non compressi; SHA256
`8cba065a6d3925e9844f80a99bb5ffb62ee2ae27e9d63658210345d51d92af54`.
DB/credenziali esclusi. I valori precedenti mantengono i propri limiti di
citazione; gli otto nuovi recuperi hanno prove strutturate separate.

## 18 ottobre 2026 — Prova UI reale Minervino V12, senza implementazioni

Richiesta: verificare il sistema corretto dalla UI, tracciare 24 dati dei soci,
spiegare il vecchio 16, confrontare GOLD V1 e distinguere scelte USER mancanti.
[Diagnosi](docs/diagnosi-e2e-v12-minervino-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-e2e-minervino.json),
[24 tracciati](docs/benchmarks/2026-10-18-v12-e2e-soci.json),
[bundle](docs/benchmarks/2026-10-18-v12-e2e-audit.tar.gz).

Codice locale V12 congelato, HEAD99ab052 più modifiche già presenti; nessun
cambio applicativo/prompt/validatori/writer/FORM, commit o push. Copia isolata
DB/storage/CompanyKB, Chromium e UI reali senza mock. Minervino V1: modulo e
56SOURCE identici ai precedenti; gold escluso dal contesto. Questa volta T0 è
la richiesta congelata completa, non il solo compila: differenza esplicita,
nessuna inferenza causale da un confronto non controllato. Scelte già T0:
società di ingegneria e Leonardo firmatario. Una conferma chiesta/ripetuta,
poi export T2; preferenze/designazioni/attestazioni/luogo-data mai chiesti,
quindi risposte non somministrate e T1 completo non raggiunto.

Esito reale conservato senza retry qualitativo:46fatti,60SOURCE assegnazioni;
58valori conformi stretti al gold,1carica più completa attestata,1Via duplicato
se fosse scritto.27grounded/reviewed/scritte,0USER,0held,0grounded ancoraUNKNOWN.
27scritture conformi,33vuotiSOURCE non dovuti a carenza KB. Soci24proposti
corretti,8grounded/revisionati/scritti(Luca),16binding con quote concatenate
inesistenti(Elisa/Andrea). Altri rifiuti:8firmatario per bindingFORM,2markerFORM,
7direttore con valori citati come socio/attributi cross-record non ammessi.
BA iniziale eBari/BA societari scritti,Comune iniziale ancora respinto.
Gruppi checkbox assenti,0spunte:casella società manca con USER giàdisponibile;
2positive,6preferenze e4testi USER attendono risposte mai chieste. Pool1→0,
non limite3domande;coverage manual_input non genera slot attivi.

Due diagnosi distinte:nel vecchio replay da16 tutti24soci erano giàreviewed;
dopo8riusiSOURCE Andrea passa da posizioni33–40 a41–48. Finestra40 e sostituzione
della lista reviewed fanno perdere8review persistite,0held,proposte intatte.
Export/writer coerenti. Altri5DTgrounded mai rivisti. Non basta unioncieca o
promozione automatica:proposta di impronta+revisione dei nuovi solo discussa.

Controprova offline sul nuovo output, socket vietati:solo prove binding in
2span letterali titolo+riga, tutto il resto identico,27→43grounded,+16corretti,
0perse. Nessuna nuova revisione,export o mutazione della sessione reale. Prima
controprova fallita con4span:limite schema2,27→19grounded,8Luca perse;artefatti
conservati separati,non regressione del run UI. Richiedere quote contigue e
2span nel prompt è proposta minima,non implementazione. SOURCE strutturale,
identità,ruolo,valore,FORM e applicabilità restano verifiche separate.

Confronti descrittivi:compilato6reale25,stessooutput+riuso33,promptreplay41,
B0manuale+riuso56,nuovaUI27. Dieci nuove/otto perse rispetto al25;le17comuni
hanno valori identici. Niente stabilità dimostrata:input diverso,nuovo output,
review manuale/simulata nei replay. Gold verificato fisicamente post-export:
27SOURCEcorrette,33vuote;123testi da lasciarevuoti preservati;4tabelle e13checkbox
intatte. CRC/XML/posizioni/report esatti,solo document.xml cambia. PDF10pagine
contro9gold;viste1/3/10 e blocco soci gold,firma isolata/giunzioni persistono.
No certificazione MicrosoftWord o nuova suite completa.

Costi reali misurati:7chiamate(1globale,2sintesi,3router,1guard),153.384token.
Globale142,10s,76.616input/40.083output inclusi24.507reasoning. Usage completo
per5chiamate;6.122token di routeriniziale/guard solo totali,noHTTPgrezzi. Cinque
POST154,76s,browser235,50s include attese. Stima0,0390–0,0427USD da tariffa
ufficiale18/10,non fattura;intervallo per split mancante. Nessuna chiamata extra
per controprove. Dieci GET abortite al mount/refresh,nessun erroreJS/POSTfallita.

205file protetti,29sessioni live/versioni/stati e273file storage originali
invariati. Runtime isolato arrestato,istanza originale ancora200. Backup con
video completo e trace campionata5s;trace originale936MiB locale conhash,
DB/chiavi esclusi. I2459test precedenti non sono stati appena rieseguiti.
Fermati dopo diagnosi. E1 resta successivo,non avviato:confrontare stessi T0,
copione e pipeline,senza attribuire alla compattazione difetti degli altri stadi.

## 18 ottobre 2026 — Correzione revisioni/citazioni e prova UI dei 24 soci

[Rapporto](docs/correzione-revisioni-soci-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-review-soci.json),
[24 tracciati](docs/benchmarks/2026-10-18-v12-review-soci-trace.json),
[bundle](docs/benchmarks/2026-10-18-v12-review-soci-audit.tar.gz).
Utente autorizza conservazione delle revisioni, formato SOURCE, nuovo export UI;
dialogo su preferenze/designazioni/attestazioni separato. Nessun commit/push,
FORM B0/modello/thinking/API/schema globale/validatori/writer invariati. E1 non
avviato. Preimmagini e modifiche precedenti conservate;HEAD99ab052+workingtree.

Revisioni V12 con impronta di campo/fatto/soggetto/ruolo/prove/destinazione/
condizioni e dipendenze; solo nuove o cambiate nelle finestre successive40.
Hold persistenti, UNKNOWN/FALSE non diventano TRUE, nessun RESOLVED automatico.
Filtro della revisione rispetto all'audit completo anche nel payload pubblico.
PENDING/auto_continue esistente completa le finestre prima delle domande;
nessun nuovo motore o ciclo di analisi globale. Sessioni storiche non migrate.
Prompt tabelle:due quote continue e separate titolo+riga;intestazioni verificate
nella stessa SOURCE;non concatenare frammenti saltando altre persone. ASTfunzioni
validatori identico. Nessuna accettazione fuzzy delle quote inesistenti.

Prima test nuovi11fail/2pass,poi20casi complessivi,negativi prove/persona diversa,
cambi di valore/soggetto/prove/ruolo/FORM/condizioni,hold,finestre,errori e legacy.
45campi esportati con DB/storage reali suFTS5/Qdrant,provider simulato. Prima
suite2477pass/2fail per vecchia attesa di ripetere contesto già esaminato;
modificata l'aspettativa senza eliminare verifica delle prove/export. Finale
**2479pass288,71s**,Ruff passato. Setup errati di comandi/harness conservati,
nessuna globale avviata in quei tentativi;non retry di qualità.

Replay provider vietato:vecchio41→54(53SOURCE+nomeUSER),soci16→24SOURCE;
finestre40/5/0/8,0review perse dopo generalitàLeonardo,5DT prima fuori finestra
revisionati. Una differenza stretta gold:carica completa attestata già nota.
Altra baseline27 riprodotta stessoSHA;sole quote corrette27→43SOURCE,soci8→24,
0nuovi valori errati osservati;altri17nongrounded conservati. I replay sono
controlli deterministici della causa,non nuove valutazioni autonome del modello.

Una nuova UI reale isolata,stesso JSONinputglobale/T0V1/56SOURCE/FORM/schema e
parametri del precedente run;solo istruzioni SOURCE diverse.55fatti/60assegnazioni,
44grounded/reviewed,finestre40/4/0/0,0held. Tutti24binding soci verificati,ma una
assegnazione incontra falso conflitto Ingegnere/ingegnere. Solo dopo domanda
attiva scelta USER della forma già inSOURCE,registrata comeUSER. Totale42valori:
41SOURCE+1USER;24soci nelDOCX=23SOURCE+1USER,non24SOURCE autonome. TreDTgrounded
rinviati dalUSER restanoUNKNOWN/non scritti;nessuna nuova attestazione inventata.
Quattro argomenti copione mai chiesti/risposte non somministrate,T1non raggiunto.
Chiarimenti supplementari documentati,nessuna modifica al copione o al gold.

Confronto reale27→42:16nuove destinazioni soci,1CFDT perso per nuova quoteFORM
inesatta,26comuni identiche.42/42gold conformi,18target fattuali vuoti(9firmatario,
Comuneiniziale,8DT);123vuoti prescritti intatti,4tabelle/13checkbox invariati.
XML/CRC/posizioni/report esatti. PDF9pagine invece10;viste1/3/9,tre soci completi,
firma vuota nell'ultima con testo;giunzioni restano. Nessuna certificazioneWord.

Costi/telemetria completi su11chiamate(1globale,4sintesi,4router,2guard).133.102input
+48.674output=181.776token,inclusi32.433reasoning. Globale174,83s contro142,10;
POST194,96s contro154,76. Costo stimato0,04563USD,non fattura. Inputglobale+84token,
reasoning+7926,outputJSONvisibile15250 contro15576. Non imputare il tempo alFORM
invariato,non promettere accelerazioni. Nuova risposta e chiarimenti diversi,
run singolo:nessuna stabilità o effetto causale generale dimostrato.

29sessioni live/versioni/stati e273file storage originali invariati,205file
protetti salvo le modifiche autorizzate. Runtime isolati arrestati,originale
conreload ancoraattivo. DB/chiavi privati esclusi dal backup;video/trace e prove
riuscite/fallite conservati nelraw v12-review-soci-20261018-01/. Seguito separato:
slot di dialogo pertinenti/validati perpreferenze,designazioni,attestazioni,
luogo-data;falso conflitto di case da affrontare esplicitamente senza normalizzare
arbitrariamente identificativi o persone. Non implementati in questa fase.

## 18 ottobre 2026 — Residui V12: equivalenza tipografica e decisioni USER

[Rapporto](docs/residui-v12-dialogo-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-residui.json),
[controlli](docs/benchmarks/2026-10-18-v12-residui-checks.json).
Richiesta circoscritta dopo la fase soci, senza ripeterne le correzioni.
FORM B0/modello/thinking/prompt globale/schema/API/DB/writer invariati; E1
ancora fermo. Nessuna nuova chiamata LLM o prova UI, commit/push o framework.

Confronto dei valori con NFC/spazi/lower solo dopo identità esatta; no sinonimi,
accent folding o unione persone, valori originali/citazioni conservati. Due
falsi conflitti Ingegnere/ingegnere eliminati, senza trasferire il ruolo di socio
al direttore o confermare l'applicabilità. REVIEW esplicite ridondanti rifiutate,
nessuna scelta arbitraria di un fatto che quel record non aveva selezionato.

Agenda di cinque decisioni dalle istruzioni FORM esplicite: preferenze67celle
raggruppate, attestazioni con clausole complete, esecutori, integrazione,
luogo/data. Niente domande duplicate o su campi già risolti; rinvii conservati.
Le risposte raggruppate registrano solo ricevute USER da verificare per
destinazione, non valori/spunte/condizioni vere. Questo limite resta esplicito.
Offerta bozza parziale con domande aperte, inclusa copia vuota dopo avviso
tracciato: regressione iniziale sull'export generico fermata e corretta.

Replay rete vietata, narratore simulato, persistenza e writer reali: codice
originale44grounded,44reviewed,41applicabili; corretto46/46/42. UNKNOWN3→4
per nuova qualifica DT valida ma ancora rinviata. Storico41SOURCE+1USER=42,
24soci,0valori persi/cambiati e0nuovi indebiti. Word identico byte per byte,
SHA4a29f7d306a6664b88208f8ba88bff5738123310a84853ff4e770f69dae126c8.
Controfattuale dallo snapshot prequalifica42SOURCE/0valoriUSER: elimina quel
chiarimento conservando societàTRUE/DT SKIP; non è una prova senza USER.

Restano18SOURCEvuoti(9firmatario,Comuneiniziale,8DT),4testiUSER,preferenze,
2caselle senza nuove decisioni. Casella società già decisa ma senza gruppo
validato: problema tecnico separato. Nessuna firma o dichiarazione personale
dedotta. Non tutti i vuoti del modulo sono requisiti da compilare.

45nuovi casi;221mirati29,69s e2524suite finale181,97s passati,Ruff passato.
Red corretto33fail/12pass sul codice conservato; prima suite completa1fail su
exportvuoto, corretta senza cambiare il test. Setup e prove intermedie conservati.
XML/CRC/posizioni/report coerenti,4tabelle/13controlli intatti. Script indipendente
ricostruisce audit eWord senza DB/chiavi.29sessioni e285file uploads+knowledge
originali invariati,206file protetti salvo4modifiche previste più helper/test nuovi.
Zero token e costo provider aggiuntivo; nessuna accelerazione misurata o nuova
valutazione autonoma del modello. Backup separato, DB/chiavi esclusi. Fermato
dopo replay e rapporto; nessuna fase successiva avviata implicitamente.

## 18 ottobre 2026 — Copertura SOURCE V12: 42 → 52 scritture

[Rapporto](docs/copertura-source-v12-2026-10-18.md),
[misure](docs/benchmarks/2026-10-18-v12-source-coverage.json),
[18 tracciati](docs/benchmarks/2026-10-18-v12-source-coverage-trace.json),
[controlli](docs/benchmarks/2026-10-18-v12-source-coverage-checks.json).
Intervento sui soli18vuoti SOURCE dopo i residui, senza rifare le correzioni
precedenti. Stesse fixture/fonti/gold e risposta MODEL: tutti18dati nelle56SOURCE,
nell'input e proposti. Nessuna nuova LLM/UI o decisione USER; FORM B0/modello/
thinking/prompt globale/schema/API/DB/retrieval/writer invariati. E1 fermo.

Nove firmatario respinti dal binding MODEL: citazione FORM nel paragrafo errato.
Scelta nominativa reale presente nella ricevuta positiva c_societa, riuso prima
limitato a VALUE e fermato da qualsiasi proposta preesistente. Ora clausola
esplicita in ricevuta accettata attiva identità SOURCE con nome completo/CF,
controlli su omonimie/conflitti e stesso operatore. Nessuna generalità/potere
dedotta dal USER. Rimpiazzo solo di proposta fallita con stesso fatto/valore
grounded, senza cancellare vecchio binding, errori, alternative o provenienza.

Comune iniziale: recupero FORM dalla continuità fisica «con sede in», operatore
finale grounded; prefisso CF direttore riconosciuto senza parola del paragrafo
successivo. Tre attributi albo con identificatori deterministici e uguale Ordine/
numero, mai unione per solo nome. Identità/ruolo/valore/applicabilità distinti.
Nessuna UNKNOWN→TRUE: c_dt rinviata resta tale per tutti gli otto dati tecnici.

Replay controllati offline con DB/storage copiati e rete vietata. Baseline42
riprodotta con identico hash usando preimmagini solo nel processo. Corretto:
60grounded/revisionate contro46;52SOURCEapplicabili contro42;51SOURCE+1USER=52
scritture fisiche contro41SOURCE+1USER=42. Dieci nuovi valori(9firmatario+Comune),
42precedenti immutati,24soci conservati,0nuovi indebiti osservati. OttoDT ancora
vuoti, prima4giàgrounded e ora4recuperati;nessuna nuova decisione sull'applicabilità.
Le cinque decisioni USER preferenze/attestazioni/esecutori/integrazione/luogo-data
restano esattamente uguali e non risposte. Export parziale sempre disponibile.

Casella società: singolo controllo e ricevuta positiva corrispondono; manca
choice_groupMODEL. Prove diagnostiche isolate sulla lista di sette alternative:
single rifiutato per lista locale incompleta, multiple strutturalmente accettato
ma cardinalità semantica non dimostrata. Nessun gruppo/spunta persistito per
aggirare il rifiuto;0caselle modificate. Non è una decisione USER mancante.

GOLD congelato usato solo dopo export:51/52conformi, una differenza stretta sulla
carica firmatario più completa, esplicitamente provata. XML/CRC/posizioni/report
coerenti,4tabelle/13controlli intatti. PDF9pagine prima/dopo,viste1/3/9;
3e9raster identiche,firma con linea nell'ultima. Non certificazione MicrosoftWord.

43nuovi casi generici. Red iniziale7fail/31pass; suite intermedie e fallimenti
conservati. Il nuovo contesto Comune esponeva un indirizzo accettato; corretto
con gate semantico e negativo. Primo replay interrotto dal form_evidence nullo
di binding respinto conservato: lettura null-safe e regressione. Ultimo negativo
dimostra ordine catalogo Comune prima di operatore poi respinto:1fail prima,
gate finale dopo tutti i controlli, test passato. Nessun falso positivo residuo
osservato. Finale304mirati32,57s,2567suite185,17s,Ruff passati.

Narratore simulato, nessuna nuova inferenza fattuale; grounding/persistenza/
writer reali e confronto manuale delle nuove prove. Bundle verificabile senza
DB/chiavi ricostruisce audit e52scritture con stessoSHA.29sessioni e285file live
immutati. Backup con codice prima/dopo, input/output, stati, render e fallimenti.
Costi/token provider aggiuntivi0; nessuna misura di accelerazione, stabilità
statistica o nuova qualità LLM. Nessun framework, hardcoding, refactor generale,
commit/push o migrazione. Arresto dopo nuovo documento e rapporto.

## 19 ottobre 2026 — Due rami residui V12: replay 61 e chat 53

[Rapporto](docs/rami-v12-direttore-checkbox-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-branches.json),
[otto tracciati](docs/benchmarks/2026-10-19-v12-branches-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-branches-checks.json).
Intervento esclusivo su applicabilità8DT e checkbox societaria. BaselineV12
SOURCE52, stessoFORM/56SOURCE/rispostaMODEL/schema, fonti/gold congelati. Nessuna
nuova globale o decisione inventata, FORM/modello/prompt globale/API/DB/writer
immutati. Nessun framework/refactor generale/hardcoding/commit/push/E1.

Diagnosi: c_dtsemantic mescolava aspetti legal_type/professional, respinti dal
confronto di dimensioni; ciò non valutava la congiunzione esplicita delFORM.
Verifica circoscritta: ruolo(per le società...) scelto da corrispondenza letterale
alla categoria della pratica nella ricevuta USER positiva del blocco; stesso
operatoreSOURCEgrounded; stesso soggetto/binding e asserzione SOURCE esplicita
persona:ruolo di azienda. Non si promuove semplicementeUNKNOWN né si usa
c_societa come sinonimo dic_dt. RicevutaSKIP conservata, non assenso. Natura
giuridica, partecipazione e poteri restano separati; nessuna designazione dedotta.

Checkbox: ricevuta congruente con l'intera opzione/controllo nativo. GruppoFORM
completo7opzioni dal titoloINQUALITÀDI all'intestazione successiva, attraverso
i blocchi di dati. Il test generico dimostra che CFmaiuscolo non è un titolo.
Validatoregruppi esistente; cardinalitàUNKNOWN mantenuta. Solo valore positivo
da ricevuta accettata rivalutata, nessuna falsa rispostachoice oclear delle
alternative. Protezioni suambiguità/scope/destinazione/provenienza confermate.

Replayoriginale52 stessoSHA, corretto60testi+1checkbox=61. Tutti52precedenti
identici,24soci intatti;SOURCEtext51→59,USERtext1 conservato.8DTapplicabili,
nessunUNKNOWN residuo per quei dati,0nuovi indebiti osservati. Narratore simulato,
rete vietata eDBstorageclonati; veri validatori,persistenza,writer. Cinque gruppi
USER invariati e aperti;4testiUSER delgold ancora vuoti.59/60testigoldconformi,
sola carica più completa attestata.0spunte aggiuntive oltre alla società.

Poi una sola nuova sessioneUI isolata133483f76343416082b954f6f7bfd777.
Globale riusata perFORM/SOURCE/schema identici,router/sintesi/guardprovider reali.
Risposta storica data soltanto a società/firmatario e rinvioDT effettivamente
chiesti; luogo/data e altri cinque argomenti non risposti. FontequalificaElisa
diretta, nessuna ricevutaVALUE ridondante. Backend60grounded/reviewed,c_dtTRUE;
narratore restituiscehold sugli8DT. Export reale53=52SOURCEtext+1USERcheckbox,
nessuna perdita rispetto ai52,51/52textgoldconformi. Non fingere che61siano
stati raggiunti dalla chat. Hold preservati, nessun tentativo di qualità ripetuto.

Schemahold non espone motivo, quindi causa semantica non dimostrata. Il narratore
vede rinvio e ruolo, non l'intero nuovo branch_evidence; interpretazione delloSKIP
o contesto incompleto sono ipotesi, non rifiutiSOURCE necessari. Blocco residuo
del dialogo separato, non corretto forzando le scritture e non avviato altra fase.

34casi generici,31negativi: prove mancanti/altrosoggetto/azienda/ruolo, negazioni,
conflitti, rinvio vs diniego, scope,controllo ambiguo, ricevuta alterata/falsa.
Primi test preparati male(discriminatore/aspect/formatoSOURCE e mutazione senza
effetto) conservati, non presentati comered valido. Finale243mirati32,75s e
2601suite185,70s,Ruff passati. Snapshot/collezione con setup errati conservati.
Ultimi2negativi sul «lascia il campo vuoto» dimostrano veto incompleto, corretto
letteralmente senza equipararlo a rinvio della conferma. Codice precedente e
fallimenti conservati, verifica indipendente finale stesso hash dei dueDOCX;
nessuna altra chiamata o secondo tentativo UI.
XML/CRC/posizioni/prestampato/report,4tabelle e13checkbox controllati; solo1spunta,
0deselezioni.9pagine in tutte3copie;vista3baseline/replay/chat e9replay. Firma
con linea nell'ultima, giunzioni writer note restano; non certificazioneWord.

Offline0LLM;chat7chiamate(3router,3sintesi,1guard),61977token,0nuoveglobali.
Prezzi non verificati,costoUSD non stimato. Trasporto completo primorouter/guard
non acquisito,totali risposte inclusi. Alias osservatore corretto nel soloharness
primaexport con riavvio al checkpoint,nessuna nuova sessione oproposta.10GET
abortiti su mount/reload,0HTTPerrori acquisiti/0pageerror,download/refresh riusciti.
29sessioni e285file live invariati,207altrifileprotetti uguali. Backup completo
con codiceprima/dopo,stati,output,prove fallite,video/trace/render;DB/chiavi esclusi.
Verifica indipendente senzaDB/chiavi genera stesso audit/Word di replay echat.
Nessuna migrazione o upgrade implicito;arresto dopo confronto e rapporto.

## 19 ottobre 2026 — hold del narratore V12: motivo osservabile e replay61

[Rapporto](docs/hold-narratore-v12-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-narrator-holds.json),
[tracciati](docs/benchmarks/2026-10-19-v12-narrator-holds-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-narrator-holds-checks.json).
Base identica alla chat precedente53: stessa risposta globale,FORM,SOURCE,USER;
conservati gli stati originali e il working tree. HEAD99ab052b,nessun commit/push.

Tre trasporti e checkpoint mostrano0hold nelle prime2sintesi; dopo USER17valori,
8nuove sospensioni MODEL nella terza. Export eredita8,non nuova conferma LLM.
Vecchio schema privo di motivi; causa privata storica non recuperabile.
Non è un rifiutoSOURCE oUNKNOWN; il contesto non esponeva branch_evidence.

Esaurite le prove salvate,protocollo2sole sintesi reali ristrette agli8valori;
nessuna globale,nuovi dati o decisioni. Modello configuratodeepseek-flash,
thinkingdisabled della sintesi invariato,temp0,1/max2048. A senza prova composta:
8hold,9302input+1183output=10485token,4,188s. B con prova completa:
8hold,10427input+1228output=11655token,4,237s. Totale22140token,USDnonstimato.
Nessun retry successivo. Handoffcontesto da solo fallisce; inB tutti chiedono
«Conferma del ruolo attuale di Direttore Tecnico» aggiuntiva rinviata da USER.
RuoloSOURCE e ramoFORM/USER già attestati: requisito duplicato,non nuova
attestazione. Questo è il motivo riprodotto,non attribuito retroattivamente.

Unico fileapp nuovo intervento: compilation_global_dialogue.py. Aggiunte prove
alcontesto ehold_reviews citate,persistite con transizioni. Regola KISS verifica
solo motivo letteraleparametrico,stessapersona/binding,clausolaFORM integrale,
ambitocondizione,prova composta eogni condizioneTRUE; non basta unbooleano.
Altro ostacoloSOURCE/FORM/USER,UNKNOWN,diniego,rinviocampo,attestazione,motivo
precedente diverso restano. ModelloinB diceancorahold,backend rifiuta8motivi
ridondanti. Schema esplorativoconrevoca fallito conservato; finale solo hold.
Mancanza motivo/listavuota/fingerprintdiverso non liberano automaticamente.
Nessuna modificaagrounding,branchhelper,FORM,API/DB,writer o modello.

Replayoriginale53 ugualeanchebyte; solanuovaosservabilità+vecchie risposte53;
rivalutazionedel checkpoint clonato con rispostaB61; controlesimulatoSOURCE53.
Tutti52testi+casella conservati,8DTrecuperati,24soci,0nuovi indebiti osservati.
Nessuna nuovaUI: precedentechat53 distinta dalreplay61. Valori,prove,condizioni,
USER delreplay identiciaB; narrate allega anchemetadataavailability preesistente,
assente nelprobe; confronto inputrigido inizialmente fallito conservato.
Audit/ricevute immutati;5gruppiUSER aperti e4testivuoti.59/60testigoldconformi,
solacarica piùcompletaattestata giànota.0altre spunte/clear;13controlli intatti
salvo checkboxsocietaria richiesta. XML/CRC,posizioni,prestampato,4tabelle passano.
DOCX61 stessoSHA84e33e... precedenteoffline;53 stesso4ff926... UI;PDF9pagine
riusatosolo dopouguaglianzaDOCX. Non nuova certificazioneWorddesktop.

26nuovi casi,18negativi parametrizzati,210mirati22,61s,2627suite186,99s eRuff
passati. Redveri eavviiconpercorsi errati distinti/salvati,nessuna chiamataLLM
peraggiustare risultato. Verificaestrattabundle rigenera audit/4Word senzaDB,
chiavi oprovider usando codicearchiviato.29sessioni/285fileoriginali e210altri
fileprotetti invariati. Nessunamigrazione o riaperturaautomatica di export
conclusi;nessunnuovo agent/framework/hardcoding;arresto dopo rapporto/DOCX.

## 19 ottobre 2026 — unica nuova prova chat V12:61 scritture reali

[Rapporto](docs/prova-chat-v12-hold-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-v12-holds-chat.json),
[tracciati](docs/benchmarks/2026-10-19-v12-holds-chat-trace.json),
[controlli](docs/benchmarks/2026-10-19-v12-holds-chat-checks.json).
Nessuna correzione applicativa/refactor/commit/push. Una nuova sessione
9bd60112c34247f799d320137d81831f,conv-5037d9a1b3554423,isolata daDB/storage reali.
Protocollo prima dell'esecuzione: FORM/56SOURCE/schema identici,stessa proposta
globale congelata del riferimento,conversazione reale. Avvio,rispostaUSER ed
export identici letteralmente;nessuna ricevuta originale copiata nello stato.
Router eguard acquisiscono CONDITION_TRUE società eSKIP tecnico;0USERtesti.

Chat61=60SOURCEtesti+1USERcasella;precedenteUI53,replay61. Tutti52precedenti,
24soci ecasella conservati,8DT presenti,0nuove indebite osservate. Narratore
nonintroducehold innessunadelle3risposte;non interviene ilveto su8motivi,che
invece era intervenuto nelreplayB. AuditSOURCEidentico alreplay,60revisionate;
nessunUNKNOWN cambiatoartificialmente/SKIPtrasformato inconsenso. Non si
attribuisce una singola osservazione a un'efficacia statistica delprompt.

CinquegruppiUSER aperti,4testiUSER delgold vuoti. Nessuna preferenza,attestazione,
designazione,integrazione o luogo/data dedotti. Non erano presenti holdSOURCE
legittimi nelcampione:18testnegativi esistenti rieseguiti separatamente,18passati
in1,43s,senzaLLM;non sono ulterioriUI. Suite2627/Ruff delprecedenteintervento
non rieseguiti oggi,non spacciati per controlli della sola prova reale.

7chiamatereali(3router/3sintesi/1guard),69815token=68766input+1049output,
13,171s provider sommate,0nuoveglobali/1riuso. Richieste/risposte complete tutte
acquisite,0retry qualità,USDnonstimato. Tempiwall includonomanualità,non misura
comparativa di velocità. Stdin delprimo driver chiuso: ripresa stessa sessione
inbrowserconPTY,nessunnuovoavvio né retryLLM.5segnalazioni iniziali senza dettaglio
finalizzato/tracevideo nonfinalizzati;DOM/screenshot/rete/trasporti conservati.
Secondodriver10GETannullate su mount/reload,0pageerror/HTTPerroriacquisiti;
trace/video,download ereload versione9GENERATED riusciti. Lettoriaudit conerrori
schema/bytes/tipi corretti solonegli script,non nella prova o nell'applicazione.

Verifica fisica XML/CRC/posizioni/prestampato/report,4tabelle e13controlli;
solap39.cb0,0clear/altrespunte. DOCXreale stessoSHA84e33e...feddddelreplay.
59/60testiGOLDconformi,carica completaSOURCEpreesistente. NuovoPDF9pagine,
viste3e9,firma conlinea ultima,giunzioni writer note;warningLOregistrylingua
salvato ma conversione riuscita/DOCXnonalterato. Verificaestratta bundle con
codice congelato ricrea audit/Word senzaDB,chiavi oprovider.249fileprotetti
invariati,29sessioni/285filelive e artefatti preesistenti preservati. Word/PDF/
report/conversazione innuovidati V12-CHAT-REALE-20261019. Servizi isolati fermati,
nessunaltra prova o esperimento,arresto dopo consegnaDOCX.


## 19 ottobre 2026 — benchmark ufficiale reale dei tre documenti storici

[Rapporto](<benchmark ufficiale/RAPPORTO-CONCLUSIVO.md>), [consegna e backup](<benchmark ufficiale/README.md>),
[misure](<benchmark ufficiale/CONFRONTO.json>), [controlli](<benchmark ufficiale/CONTROLLI-FINALI.json>).

Obiettivo: valutare V12 senza correzioni e senza globali congelate. HEAD 99ab052,
working tree preesistente preservato; hash di 318 file, patch e codice archiviati.
Tre nuove sessioni UI con FORM originali Minervino/Trapani/Catanzaro, 22 chunk
Company/General comuni e immutati, scenari USER per procedura preregistrati.
Massimo due turni USER ed export parziale ordinario, senza manipolare lo stato.
Non è un'estrazione casuale: sono i tre documenti storici richiesti; fixture
labirinto non rieseguita, GOLD escluso dal prompt.

Risultato: Minervino 55 scritture (54 testi SOURCE corretti e una checkbox USER),
Trapani 10 (nove corretti, una PEC completa un'accettazione senza consenso),
Catanzaro 13 testi corretti e nessuna checkbox. Nucleo SOURCE: 60/17/31 posizioni,
non fatti atomici distinti; mancanti 6/8/18, con prove tutte nell'input.
Proposte LLM 60/10/15, grounded iniziali 45/10/13, finali 54/10/13;
nessun hold o valore grounded ancora UNKNOWN. Catanzaro ha anche un record NA,
non contato fra le proposte di valore. Minervino conserva i 24 campi soci;
quattro campi del direttore respinti per nuovo binding, prima del narratore.
Trapani/Catanzaro omettono le generalità e il riuso inline non supporta quei
FORM. Catanzaro non propone choice_groups: tre caselle autorizzate non collegate.
In tutti i casi una conferma con negazione “senza raggruppamenti o consorzi”
è respinta dalla regex delle alternative e ripetuta una volta. Minervino mostra
anche due domande su rami già esclusi. Mancano domande su consensi/attestazioni.

Tre globali nuove, zero riusi/retry di qualità, 30 chiamate totali, 463.201 token,
399,32 s provider, 0,099946 USD stimati con cache e tariffa ufficiale, non fattura.
Deepseek-flash, fingerprint e72d3c7f663d3e1383b00b3884cb4501, globale con thinking
low/enabled. Dopo interruzione del runtime, Trapani ripresa nella stessa sessione:
wall time non comparabile, primo trace non finalizzato, proposta/persistenza/
ricevute/provider acquisiti.

DOCX/PDF ordinari separati, di 9/5/17 pagine. XML/ZIP/prestampato/posizioni/
checkbox/download verificati, nessuna parola fuori pagina sulle 31 pagine;
ispezione visiva di pagine critiche selezionate. Replay indipendente senza
rete/DB/chiavi rigenera audit finali e tre DOCX identici, incluso l'errore PEC.
45/54 testi Minervino letteralmente uguali al riferimento, nove differenze
giustificate; Trapani/Catanzaro senza GOLD indipendente. Nessuna accuratezza
globale dichiarata o totale artificiale di tutti gli adempimenti UNKNOWN.

Conservati 318 file app/test/frontend/fixture, 26 input, 645 artefatti precedenti,
29 sessioni live e 285 file storage; schema DB immutato. Soltanto script di audit,
rapporti e artefatti nuovi, STATUS/registro aggiornati. Nessun fix della pipeline,
nuova suite completa, commit/push o E1. **Baseline non adottata**, non proposta come
affidabile per il bloccante PEC; nessuna replica selettiva per migliorare l'esito.

## 19 ottobre 2026 — V12 invariata su tre nuovi bandi estratti da un pool

[Rapporto](<benchmark ufficiale/casuali-v12-20261019-01/RAPPORTO.md>),
[consegna e backup](<benchmark ufficiale/casuali-v12-20261019-01/README.md>),
[misure](<benchmark ufficiale/casuali-v12-20261019-01/CONFRONTO.json>),
[riepilogo](docs/benchmark-casuale-v12-2026-10-19.md).

Obiettivo autorizzato: verificare la generalizzazione su moduli non usati nelle
correzioni precedenti, prima di decidere altre semplificazioni. Nessun fix o E1.
Prima della ricerca: criteri DOCX SIA originali, otto procedure nel pool, seed
`Mapi-V12-bandi-casuali-2026-10-19-01`. Ricerca estesa prima del sorteggio;
pool congelato e una sola estrazione: CRAA, Bella, Cesano Maderno. Casualità
interna a un pool di convenienza, non campione nazionale rappresentativo.
Payload grezzo della prima ricerca non acquisito, limite esplicitato; successive
acquisizioni, download, esclusioni e sorteggio conservati. Nessuna sostituzione
per qualità o ripetizione selettiva dei fallimenti.

Tre nuove CompilationSession dalla UI reale, una nuova globale DeepSeek per
FORM e stessi 22 chunk Company/General del benchmark storico. Scenari USER
documentati separatamente prima delle chiamate: partecipazione singola come
società di ingegneria, scelta Leonardo firmatario; dati personali e poteri
richiedono SOURCE. Due risposte al massimo, soltanto sugli slot chiesti;
esportazione ordinaria senza stato modificato manualmente.

CRAA: proposti/grounded/applicabili/scritti 9/9/9/9; sette testi leggibili nel
PDF e due dati CCIAA corretti nell'XML ma invisibili in celle originali di
66/81 twip. Il firmatario è omesso, il chiarimento respinto per motivazione
di 225 caratteri oltre il massimo 200. Bella: 4/4/4/4, tutte leggibili; quattro
proprietà del firmatario presenti nell'input omesse. Riuso inline non supportato
e ricevuta della condizione priva della scelta nominativa; gruppo societario
respinto per etichette incomplete. Cesano: 0/0/0/0 e copia esportata senza
valori. La chat espone 68 checkbox ma nessuno dei 20 FORMTEXT legacy; il
chiarimento societario su checkbox è respinto. Preflight generico e percorso
reale divergono: addendum conserva la smentita, senza riscrivere gli input.

Tredici testi SOURCE corretti nell'XML, undici leggibili nel PDF; zero nuove
scritture fattuali o decisioni indebite rilevate, zero checkbox/testi USER.
Il risultato Cesano è un fallimento funzionale nonostante stato GENERATED.
Nucleo SOURCE preliminare 10/8/4 occorrenze, non fatti distinti o denominatore
totale: vuoti 1/4/4, cinque omissioni di valore e quattro destinazioni non
esposte, prove tutte nell'input. Zero proposte di valore SOURCE respinte;
due chiarimenti respinti per cause differenti. Nessun GOLD indipendente o
accuratezza globale dichiarata. Nessun hold finale: non è un test negativo
della protezione di hold legittimi.

CRAA/Bella ripetono una domanda per il falso conflitto di alternative nella
negazione “senza raggruppamenti o consorzi”. Preferenze, attestazioni,
esecutori, integrazione e luogo/data restano separati e UNKNOWN. Nessuna
firma, designazione, adesione o requisito inventato. L'errore PEC del precedente
benchmark storico non viene corretto o annullato da questi esiti.

22 chiamate reali: tre globali, dieci router, quattro guard, cinque sintesi;
271.084 token, 291,57 secondi HTTP sommati e 0,060070 USD stimati con cache e
tariffa ufficiale conservata, non fattura. Alias deepseek-flash e fingerprint
comune e72d3c7f663d3e1383b00b3884cb4501; globale thinking enabled/low invariato.
Zero errori HTTP provider, finish stop, zero retry di qualità. Tempo umano,
ricerca e rendering esclusi; nessuna comparazione di latenza fra moduli diversi.

XML/CRC, posizioni, prestampato, controlli, report e download verificati. PDF
nuovi di 7/4/3 pagine, bounding box su tutte le 14 e pagine selezionate viste:
il controllo dei bordi non rileva i due dati invisibili CRAA. Microsoft Word
desktop non verificato. Replay con rete vietata ricostruisce audit e tre DOCX
identici byte per byte; backup con codice effettivo congelato, senza database
privati o credenziali, estratto e verificato separatamente. Non confondere
la riproducibilità dei difetti con la qualità del risultato.

318 file app/test/frontend/fixture, 41 input, 422 artefatti precedenti, 29
sessioni originali e 285 file storage invariati; schema DB immutato, tre sole
sessioni nuove isolate. Servizi arrestati; nessuna suite completa rieseguita,
modifica a codice applicativo/prompt/FORM/grounding/writer/modello o commit/push.
Grezzi in backend/data/compilation-audit/casuali-v12-20261019-01/ e archivio
separato nella consegna. Baseline non adottata; nessuna correzione avviata.

Proposta da decidere: prima verifiche mirate su destinazioni Word, conservazione
dei chiarimenti e scelta della persona, poi eventuale E1. Se i tre nuovi casi
guidano lo sviluppo diventano regressioni: il test finale richiederà un lotto
non ancora utilizzato per scegliere le correzioni. Arresto alla consegna.

## 19 ottobre 2026 — copertura dei campi legacy FORMTEXT, senza nuove LLM

[Rapporto](docs/legacy-formtext-2026-10-19.md),
[misure](docs/benchmarks/2026-10-19-legacy-formtext.json),
[controlli](docs/benchmarks/2026-10-19-legacy-formtext-checks.json).

Obiettivo autorizzato: rendere indirizzabili i campi testuali legacy ignorati
nel benchmark Cesano, con correzione generale e regressione sui cinque altri
documenti. Nessuna compattazione, nuovo modello/prompt o modifica al grounding
e al dialogo. Nessuna nuova chiamata LLM: costi/token provider pari a zero.

XML osservato: 20 FORMTEXT con ffData/textInput, begin/separate/end completi e
cinque spazi U+2002 nel risultato; tutti hanno nome Testo1. Quindici nello stesso
paragrafo, quattro in rami alternativi e una data finale. L'estrattore scartava
ogni paragrafo con campi complessi. La correzione espone soltanto i FORMTEXT
semplici e vuoti verificati singolarmente, usando ID da paragrafo e ordinale,
senza affidarsi a nomi duplicati o introdurre regole per il Comune/azienda.

Risultato strutturale: **20 destinazioni testuali riconosciute contro zero**,
68 checkbox identiche e catalogo da 68 a 88. Il normale costruttore dell'input
globale include tutte le venti; formato FORM B0/schema globale invariati.
Unico file applicativo modificato: docx_templates.py. Il writer cambia solo il
risultato, preservando contenitori e proprietà Word; gestisce anche risultati
senza testo e rispetta maxLength senza troncamento. I rifiuti di campi non
dimostrati, precompilati, annidati, bloccati, firme e formati speciali restano.
Un ulteriore RED su risultati vuoti adiacenti ha richiesto la precedenza per
start/end decrescenti. Non è un refactor o un nuovo sistema di orchestrazione.

Prova writer su 20 sentinella e prova separata con quattro valori SOURCE
(nome, luogo/data di nascita, denominazione), esplicitamente assegnati dal test:
non nuove proposte LLM o risposte USER, non compilazione chat. Tutte le posizioni
corrette e i risultati leggibili nei due PDF di tre pagine; zero parole fuori
pagina, viste 1 e 3 di entrambi, Microsoft Word desktop non verificato.
Prestampato, stili, bookmark, metadati e 68 checkbox intatti; nessuna firma o
spunta. Il test delle 20 destinazioni esercita rami alternativi/data e non è
una domanda valida. Nel Word con quattro SOURCE gli altri 16 campi sono vuoti.
Non si dichiara verificato automaticamente il binding del firmatario o il ramo.

Regressione offline sul benchmark storico e casuale: cataloghi completi,
audit ricalcolati ed export identici per Minervino, Trapani, Catanzaro, Bella,
CRAA. Conservati 54 testi+1 checkbox/10/13/4/9 scritture, compresi errore PEC
Trapani e difetto PDF CCIAA CRAA; non corretti da questa fase. Il riferimento
Minervino è quello ufficiale a 55, non il replay storico a 61. Per Cesano,
vecchi 68 candidati e rispettive valutazioni identici, 20 nuovi irrisolti;
la vecchia risposta continua a scrivere zero. Nessuna scrittura recuperata
artificialmente o nuova accettazione nel replay.

27 nuovi casi parametrizzati, 230 mirati passati in 15,00 s, **2.654 backend
passati in 197,46 s** e Ruff backend passato sulla versione finale. Conservati
RED iniziale, assert corretti nel test, RED dei vuoti adiacenti e suite da
2.651 casi precedente all'ultima correzione, separati dall'esito finale.
Sono verifiche software, non una nuova valutazione della qualità LLM.

317 altri file protetti, 546 artefatti precedenti, 29 sessioni originali e 285
file storage invariati; nessuna nuova sessione. Nessuna modifica a API/database,
prompt, grounding, dialogo, modello o originali. Grezzi in
backend/data/compilation-audit/legacy-formtext-20261019-01/, backup con codice
prima/dopo e verifica offline separata in docs/benchmarks; nessun commit/push.
Vecchie sessioni non migrate, benchmark precedenti non riscritti, baseline
non adottata. Il prossimo passo da decidere è una nuova prova chat Cesano:
il parser ora consente le proposte, ma non dimostra che il modello le produrrà.
Arresto dopo rapporto e artefatti, nessun E1 o nuova prova globale avviati.

## 19 ottobre 2026 — regressione rigorosa FORMTEXT e nuova chat Cesano

[Rapporto](docs/regressione-formtext-e2e-2026-10-19.md),
[controlli](docs/benchmarks/2026-10-19-formtext-e2e-checks.json),
[metriche](docs/benchmarks/2026-10-19-formtext-e2e.json),
[consegna](<benchmark ufficiale/formtext-cesano-20261019-01/README.md>).

Scopo: controllare sistematicamente il supporto introdotto, poi una sola
nuova compilazione reale senza cambiare gli altri componenti. Nessun file
applicativo modificato in questa fase. Aggiunti 28 casi reali e 26 file fixture;
estesi i negativi esistenti per confrontare l'XML escluso dopo una scrittura
lecita distinta. 55 casi nei due file FORMTEXT. ID stabili anche riaprendo e
serializzando, venti scritture insieme e singole, ordine input rimescolato,
run multipli, nomi duplicati, firme/checkbox/stili/prestampato protetti.

258 mirati in 22,25 s, 2.682 backend in 205,02 s e Ruff passati prima dell'E2E.
Sei cataloghi/audit/DOCX congelati ricostruiti identici, stessi difetti inclusi.
PDF nuovi: tutte le parole e posizioni identiche ai precedenti; 45 pagine più
tre della prova con venti sentinella, tutti leggibili, zero parole oltre bordo.
Ispezione visiva selettiva, non tutte le 48 pagine. CCIAA CRAA invisibili: FAIL
preesistente, conservato. Indirizzi Catanzaro leggibili a pagina 1/11: il confronto
letterale sul testo estratto intercala etichette di colonne diverse. Errore
PEC Trapani conservato, non promosso a dato corretto dal test di uguaglianza.

Nuova sessione chat isolata 226639266b2c4b4a8aaacc2e1f25b65d, conv-436e1eb7ce2d4b6d,
stessi modello/systemprompt/parametri/22 SOURCE/scenario e originale Cesano.
Una globale nuova: tutti i 20 ID testuali presenti, nessun output congelato o
retry qualità. Primo tentativo browser a server spenti dopo riprendi fallito
prima di LLM/sessione, acquisizioni conservate e riavvio stesso progetto.
Due turni USER sul ramo società, data UNKNOWN, poi normale export/download.

Otto valori proposti, grounded, applicabili, revisionati e scritti; tutti
leggibili nei tre fogli PDF e posizioni XML corrette. Una corrispondenza
dimostrata (denominazione); sette fatti societari scritti nello studio/PIVA/
recapiti del sottoscrittore senza prova o conferma di pertinenza. Non sono
sette fatti aziendali falsi, né sette valori certificabili per quei campi.
Tre dati personali SOURCE nell'input omessi; MODEL invoca c_firmatario senza
proporre la relativa condizione o una domanda nominativa. Riuso limitato alla
grammatica inline precedente non supporta Cesano. Tutti i fatti scritti sono
company, senza binding: il gate personale richiede person o binding_id e non
accerta autonomamente il soggetto FORM di queste assegnazioni. Confermare
il ramo non prova la proprietà personale. Zero choice_groups e checkbox
societaria ancora vuota. Data rinviata, altri dodici testi e 68 checkbox intatti.

10 chiamate (1 globale/4 router/2 guard/3 sintesi), 111.691 token, 99,90 s provider,
0,022380 USD stimati, non fattura. Deepseek-flash enabled/low, fingerprint
e72d3c7f663d3e1383b00b3884cb4501. Tutte 200/stop. XML/ZIP e parti del pacchetto
verificati; UI/ricostruzione identiche; trace/video finalizzati e 10 GET abortite
su mount/reload. Word desktop non richiesto/non verificato. Nessuna firma,
data o preferenza inventata. Nessun valore rimosso manualmente dal DOCX.

Supporto strutturale FORMTEXT PASS, qualità E2E FAIL: funzionalità complessiva
non dichiarata chiusa. Nessun controllo obbligatorio rimasto ineseguito e
nessuna regressione tecnica rilevata; le attribuzioni e omissioni richiedono
una fase distinta. Nessuna correzione al modello, prompt, grounding, dialogo,
API o writer per migliorare questo risultato. 328 altri file protetti, 632 artefatti,
29 sessioni live/285 file storage invariati; 32 sessioni nel clone intatte, una nuova.
Grezzi formtext-chiusura-20261019-01/, backup separato nella consegna con
codice/fixture e audit completi senza DB/chiavi; servizi fermati. Nessun commit,
push, nuova globale o E1 dopo la prova. Arresto al rapporto PASS/FAIL.

## 19 ottobre 2026 — Attribuzione SOURCE–soggetto–campo, regressione e sorteggio

Esperimento `source-attribuzione-20261019-01`, richiesta esplicita dell'utente.
[Rapporto](docs/attribuzione-source-soggetto-campo-2026-10-19.md).
Prima test negativi, poi veto conservativo dal FORM inline indipendente da entity
MODEL. Nessuna nuova equivalenza di persone o proprietà; ambiguità non promosse.
Stesso output reale Cesano: 8→1 scritture, sette trasferimenti azienda/persona
non dimostrati esclusi, fatto societario valido preservato. Sei replay identici
ai precedenti e Minervino V12 61→61. Nessuna nuova accettazione nei riferimenti.
39 nuovi test, 324 mirati, 2.721 backend e Ruff PASS. Parser,writer,prompt,modello e
API invariati; niente hardcoding applicativo. Nuovo controllo limitato a contesti
inline espliciti, non verificatore universale dei soggetti in ogni tabella.

Congelato codice prima di una nuova generazione reale. Pool dieci moduli,
Cesano escluso, seed 13243375443350163391, estratto Catanzaro, nessuna ripetizione.
22 SOURCE identiche, deepseek-flash e thinking enabled/low invariati. Sessione UI
nuova:15 proposte valore,13 grounded/applicabili/revisionate/scritteSOURCE più 2 USER,
15 totali leggibili. Zero scritture indebite rilevate,zero checkbox nuove.
31 posizioni del riferimento storico:16 vuote (14 omesse,2 respinte),un campo scritto
solo parzialmente(numero senza data). Conservati difetti di dialogo, condizioni
non collegate e gruppi checkbox assenti. Nessuna modifica durante il benchmark.

10 chiamate,181.386 token,193,16 s HTTP,0,043697 USD stimati. PDF 17 pagine,bordi e XML
validi,viste 1/2/11/17. Una replica non prova aumento statistico della qualità:
la causalità della correzione è misurata nel replay Cesano; la prova casuale
verifica il percorso congelato su un altro FORM. Baseline non adottata. Tutti
gli artefatti e i limiti sono conservati nella consegna; nessun commit/push.

## 19 ottobre 2026 — Verifica mirata delle attribuzioni tabellari

[Rapporto](docs/attribuzioni-tabellari-2026-10-19.md). Zero nuove chiamate LLM.
Quattro proposte errate iniettate su copie del FORM/SOURCE Catanzaro reali
superavano il grounding con entity=company nei dati della persona/direttore.
Non sono errori osservati nelle risposte reali salvate: i quattro probe validi
sono distinti da due prove preliminari respinte per condizioni/schema.
Dopo il veto tabellare limitato a righe etichetta–valore, 4→0 proposte errate
grounded; fatti societari conservati. Nessuna identità o applicabilità dedotta.
Operatore economico ambiguo; header non marcato non diventa prova di binding.
23 test permanenti, 347 mirati, 2.744 backend e Ruff PASS. Nove audit/DOCX
identici, inclusi Minervino V12 61, Cesano 1 e ultimo Catanzaro reale 15.
Esaminate 35 scritture SOURCE tabellari: vincolo di tipo determinato su 13,
non determinato su 22; due ulteriori scritture USER. Conteggi di occorrenze,
non fatti indipendenti. Non certificati record multicolonna, prosa arbitraria
o coerenza universale fra persone dello stesso ruolo. Non ripetuto rendering
per DOCX identici. Nessun nuovo benchmark reale o adozione della baseline.
Modificato un solo helper applicativo, preservati dati e sessioni. Risultati,
probe e codice conservati nella nuova consegna; nessun commit/push.

## 19–20 ottobre 2026 — PEC Trapani: disponibilità SOURCE e impegno procedurale

[Rapporto](docs/pec-consenso-procedurale-2026-10-19.md),
[risultati](<benchmark ufficiale/pec-consenso-20261019-01/ESITO.json>),
[DOCX/PDF/dialogo](<benchmark ufficiale/pec-consenso-20261019-01/e2e/trapani/>).

Ipotesi verificata: un contatto fattuale valido non autorizza un'accettazione
procedurale. Riprodotto esattamente l'output storico:9 fatti,10 proposte/scritture,
una PEC indebita nella dichiarazione senza ricevuta USER. MODEL kind=data e
conditions=[]; citazione abbreviata, ma il narratore vedeva la clausola completa.
Mancava il gate deterministico, non la conoscenza della PEC o la lettura del FORM.

Intervento: controllo FORM per impegni espliciti nella clausola marcata; domanda
con testo e valore, ricevuta separata legata alla sessione e gate nell'export
SOURCE/USER. Applicabilità e grounding restano necessari e indipendenti.
Fonte/proposta/valore originali intatti. Non una classificazione universale di
impegni impliciti o fra celle/paragrafi. Nessun cambio a FORM, modello, prompt,
API, DB, parser, writer o nuove architetture; nessun commit/push.

Metodo: test prima della correzione (27FAIL/5PASS), insuccessi intermedi conservati,
49 nuovi test permanenti (41 locali+8 sessioni FTS5/Qdrant con provider simulati).
248 mirati PASS36,96s,2.793 backend PASS218,66s,Ruff PASS. Nove replay congelati:
Trapani10→9, altre otto bozze identiche, Minervino61 conservate. Audit fattuali
identici. Un solo paragrafo Trapani ripristinato all'XML originale; resto del
pacchetto/firme/checkbox/stili intatto. PDF prima/dopo cinque pagine.

Una nuova generazione reale dalla UI su Trapani, non un riuso dell'output.
Stesso FORM SHA d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701,
stesso snapshot22SOURCE SHA0982378194a2e3e769ed3e18dc8d92bf6c1c70f6c4e8b5aa9bbf6d236093ff0c;
HEAD99ab052 dirty con66hash applicativi congelati. deepseek-flash, thinking
globale enabled/low, narrator/router disabled; stesso prompt globale SHA978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c.

Sessione331f4362017a42dc86f223ea0c8c46c7, versione10 GENERATED:9 fatti grounded,
10 proposte grounded/applicabili/revisionate,9 scritte SOURCE,0 USER,0 checkbox.
PEC aziendale conservata; PEC dichiarativa vuota grazie al gate nonostante
zero hold finali. La ricevuta USER SKIP non è falsa applicabilità: è mancato
consenso all'impegno. Nove valori supportati, otto proprietà complete e una via
senza civico172/C disponibile; otto dati firmatario omessi. Nessuna attribuzione
non supportata o sezione indebita rilevata. I conteggi non sono accuratezza
statistica o validazione delle dichiarazioni prestampate.

Tre decisioni specifiche, quattro domande in due turni USER. Un duplicato per
la «o» in «senza raggruppamenti o consorzi», respinto dal controllo letterale
preesistente pur SUPPORTED dal guard; seconda conferma accettata. Nessuna nuova
correzione durante la prova, nessuna ripetizione selettiva. XML/posizioni/report/
download/tabelle intatti; PDF5pagine,viste1/2/3/5,nove valori leggibili,pagina3
PEC vuota,pagina5firma/data vuote. Dieci GET abortite a mount/refresh; nessun errore
provider. Nessuna prova Word desktop; positiva USER nei test simulati, reale UNKNOWN/SKIP.

10chiamate=1globale+4router+2guard+3sintesi;109.176token,65,86s globale,77,22s HTTP
sommati;0,019564USD stimati,non fattura. Provider fingerprint e72d3c7f663d3e1383b00b3884cb4501;
alias/fingerprint non certificano pesi immutabili. Durata browser comprende attese.
Preservati1.333 altri file,29sessioni live,285file storage e34sessioni clone
precedenti;una nuova. Nessuna chiamata al riprendi. Backup separato e verifica
indipendente senza DB/chiavi/rete nella consegna. Esito circoscritto PASS,
nessuna baseline adottata. Residui esplicitati, arresto dopo rapporto.

## 20 ottobre 2026 — Generalità del firmatario fra paragrafi e tabelle

[Rapporto](docs/firmatario-generale-2026-10-20.md),
[consegna e backup](<benchmark ufficiale/firmatario-generale-20261020-01/README.md>),
[DOCX finale](<benchmark ufficiale/firmatario-generale-20261020-02/e2e/trapani/bozza.docx>).

Ipotesi: l'identità scelta dall'utente e i dati personali già documentati non
vengono collegati alle destinazioni di layout differenti. Causa verificata:
riuso dipendente da un'unica sequenza completa di campi e scelta iniziale solo
nel contesto LLM. Implementato collegamento deterministico da scelta nominativa
registrata nella stessa sessione a profilo SOURCE univoco (nome/cognome/CF) e
FORM personale esplicito, su paragrafi contigui o tabelle semplici. Limiti
strutturali dichiarati, nessuna grammatica per nome di bando. Prove di identità,
proprietà, ruolo e applicabilità restano separate; nessuna inferenza di poteri.
Nessuna promozione automatica o revisione inventata. MODEL/audit originali intatti.

Due controesempi aggiunti dopo la prima prova mostrano che un'associazione già
grounded a società/altra persona poteva essere conservata nel blocco personale.
Corretto nello stesso collegamento con veto di attribuzione rispetto al
firmatario verificato; citazioni e fatto rimangono, associazione rifiutata.
Non erano errori osservati nella prima bozza reale. Aggiunto test sui conteggi.
Modificati source_reuse/global_sessions e nuovo signatory_form. Modello,thinking,
prompt,FORM,grounding,binding fattuali,API,DB,parser e writer invariati.

51 casi permanenti nuovi:45 locali+6 sessioni FTS5/Qdrant simulate.327 mirati
PASS47,55s;2.844 backend PASS321,95s;Ruff PASS. Conservati RED iniziali6FAIL,
retraction4FAIL,catalogo ridotto13FAIL/2.827PASS,una suite interrotta durante
lo sviluppo e gli esiti intermedi2.841/2.843PASS. I test non sono valutazioni LLM.
Dieci replay DOCX identici,Minervino61/61;con contesto USER effettivo si verificano
8proposte personaliTrapani,4Bella,2Catanzaro,9Minervino conservate. Nessun export
retroattivo delle nuove proposte con vecchie revisioni. Catanzaro celle composte
nascita/residenza e carica non associata restano irrisolte: non si concatenano
prove letterali separate né si compila una mezza risposta come completa.

Due sessioni reali nuove UI,una globale per prova,stessoFORM/SOURCE/scenario/model
snapshot. Prima adea29341e9646afb75379928e0070c9:18proposteMODEL,10grounded
iniziali;8personali proposte ma binding rifiutato per ruoloFORM in ordine diverso.
Il riuso recupera indipendentemente8dati verificati;18applicabili/revisionate,
17scritteSOURCE,1PEC dichiarativa bloccata daUSER_SKIP. Nessun allentamento binding.
Finale b7d40c2449ad421580fe267547ac7964:9proposteMODEL grounded,8personali omesse;
riuso8→17grounded/applicabili/revisionate/scritte,0USER/checkbox,0indebite rilevate.
Finale17proprietà complete;il civico aziendale172/C ora proposto è variazioneMODEL,
non effetto attribuito alla correzione. Controfattuale medesimo output prima
prova:codice precedente9→finale17,a parità diSOURCE/ricevute,senza nuove chiamate.
Seconda prova preregistrata dopo il veto,prima17PASS conservata,non retry qualità.
Nessuna modifica dentro ciascuna prova o intervento manuale sullo stato.

Finale3domande/1turnoUSER,conferma societaria e firmatario,luogo/data rinviati.
Una conferma identità duplica scelta iniziale;non richiede di nuovo generalità.
Quattro rami alternativiUNKNOWN conservati. PEC dichiarativa non proposta e vuota,
firma/data/CIG/iscrizioni non verificati vuoti. Le dichiarazioni prestampate non
sono tutte attestate dal benchmark;la bozza non è pronta all'invio.
XML/CRC/17posizioni/6tabelle/prestampato/stili/controlli/download verificati;solo
word/document.xml cambia. PDF5pagine,17valori leggibili,0fuori bordo,viste1/2/3/5.
Difetto cosmetico aLecce originale conservato;Word desktop non provato.

Finale7chiamate(1globale),95.023token,70,76sglobale,79,89sHTTP,0,019047USD stimati.
Prima9chiamate/115.350token/0,023323USD;totale16/210.373/0,042370USD,non fattura.
Deepseek-flash,fingerprint e72d3c7f663d3e1383b00b3884cb4501,globaleenabled/low;
22SOURCE,prompt/config/hash congelati. Alias non certifica pesi immutabili;
non stima statistica di accuratezza,tempo o costo.

Preservati1.426 altri file,29sessioni live,285file storage,35/36sessioni pregresse
nei cloni;2nuove isolate.67hash applicativi finali intatti. Backup separato con
entrambe le prove e codice prima/dopo,senzaDB/chiavi/env;32ricostruzioni esatte
indipendenti senza rete/SQLite più controfattuale. Grezzi sotto
backend/data/compilation-audit/firmatario-generale-20261020-01 e -02.
Nessuna migrazione/reindicizzazione/commit/push;servizi isolati fermati.
PASS circoscritto,nessuna promessa universale o baseline adottata. Arresto dopo consegna.

## 20 ottobre 2026 — CRAA: conservazione delle risposte USER lunghe

[Rapporto](docs/craa-risposte-user-2026-10-20.md),
[consegna](<benchmark ufficiale/craa-user-20261020-01/README.md>),
[DOCX reale](<benchmark ufficiale/craa-user-20261020-01/e2e/craa/bozza.docx>).

Distinzione causale: il vecchio errore CRAA225>200 riguarda reason di una
richiesta MODEL,non il testo USER. Originali storici conservati;contratto MODEL
invariato,test specifico permanente. Non si dichiara corretto quel difetto.
Rischi USER verificati separatamente:textarea maxLength4000 e trim eliminano
parte del testo;errori di rete lasciano la copia solo nel turno React;estratti
V12/controlli limitati2000 contro ingressoAPI4000. Allineati soltanto gli estratti
al tettoAPI,senza aumentare il limite1500dei valori o cambiare i gate di sicurezza.
Frontend invia originale,blocca esplicitamenteoltre4000senza tagli,contaUnicode,
conserva copia nella scheda per progetto/conversazione,consente recupero manuale
e riuso dei turni server. Nessun reinvio automatico,cancellazione di una nuova
bozza,assenso implicito o nuovo registroDB. Storage negato segnalato;garanzia
locale limitata alla scheda,cronologia server dopo ricezione.

53nuovi casi (33backend+20frontend),2.877backend PASS217,26s,126frontend PASS6,70s,
Ruff/lint/build PASS. Limiti2000/2001/3999/4000/4001,Unicode,spazi,righe,errori,
valori non documentati,persona diversa,ambiguità,valori1501,scope e persistence,
exportUSERpertinente;frontendreload,cambio contesto,transito,storage corrotto,
nuovachat e bozza durante richiesta. Provider simulati,non qualitàLLM.
Conservati i RED e gli errori harness (PATH,fixture,assert sulla vista pubblica,
primo riferimento replay before errato e import pytest codicevecchio errato).
Controfattuale Python con percorso verificato:medesimo estrattolungo prima
REJECTED,dopo ACCEPTED,senza nuova inferenza. Nel reale il router cita clausole
brevi:quel risultato non dimostra che richiedesse l'aumento del limite.

22replay esatti senza rete/SQLite:diecicasi in due contesti salvati più due
realiprecedenti17scritture;Minervino61/61 e CRAA9XML invariati. SOURCE,FORM,
writer,grounding,binding,modello,promptglobale,API eDB invariati. Solo
compilation_chat.py e ProjectWorkspacePage.tsx più helper chatMessageRecovery.ts.
Nessun framework,hardcoding o nuovi agenti.

Una nuova sessioneUI bc286f4fd88d46d89d55edf0595d68e7,conv-8e2093a65dd140fa,
form201,versione7 GENERATED. Unaglobale nuova,stessoFORM/22SOURCE/configurazione,
scenarioUSERv2 preregistrato. Risposta3113caratteri recuperata dopo reload e poi
inviata:SHA52342bd3aaafe13be4213326d3a45610f70fedc34c5932ddc8a915dc02ce542e
identico inUI,HTTP,router,guard,cronologia eSQLite. Tredecisioni:ruolo del
firmatarioTRUE,coerenzaCCIAA SKIP,fatturato SKIP. Non convertiti in fattiUSER,
nessuna altra conferma dai paragrafi contestuali,nessuna checkbox. Exportesplicito
successivo;nessun intervento sullo stato o correzione durante il benchmark.

13fattiMODELgrounded,13assegnazioni proposte;2anni respinti per quoteFORM,
2fatturati mantenuti come alternative senza selezione;9proposte singole grounded
e revisionate,7applicabili/scritte SOURCE,0USER/checkbox,0indebite rilevate.
DueCCIAA sospesi dalla condizione più ampia proposta nel nuovooutput e rinviata,
nomefirmatario ancoraomesso. Non è perditaUSER o regressione deterministica
9→7;nessun conteggio forzato. CelleCCIAA vuote non verificano il vecchio difetto
PDF:geometrie invariate,nessuna correzione o miglioramento dichiarato.

XML/CRC/7posizioni/8tabelle/prestampato/stili/report/download verificati;solo
word/document.xml cambia;tcPr/trPr/tblPr/tblGrid intatti. PDF7pagine,7valori
leggibili,0fuoribordo,viste1/4/7. Etichette attaccate ai valori conservate,
firma/attestazioni nonaggiunte;Worddesktop nonprovato. Primodriver senzaPTY
bloccato su stdinchiuso:riaperta stessa conversazione,non globale;primo trace
incompleto,snapshot/network preservati;secondotrace/video completi.15GETabortite
nel driverfinale,nessunPOSTfallito o erroreprovider. Nessun retry di qualità.

7chiamate=3router+1globale+2sintesi+1guard;95.674token,87,21sglobale,96,42sHTTP,
0,021002USD stimati,nonfattura. Deepseek-flash enabled/low globale,stesso
fingerprint e72d3c7f663d3e1383b00b3884cb4501;alias non certifica pesi immutabili.
Singolocampione,non misurastatistica di latenza/accuratezza.
Preservati1358altrifile,29sessionilive,285filestorage,37sessionipregresseclone;
una nuova isolata.116hashbackend/frontend congelati. Grezzi sotto
backend/data/compilation-audit/craa-user-20261020-01;backup separato senzaDB/
credenziali con23ricostruzioni esatte e controfattuale degli estratti.
Servizi isolati arrestati,nessuna migrazione/reindicizzazione/commit/push.
PASS circoscritto ai criteriUSER,nessuna baseline adottata. Arresto alla consegna.

## 20 ottobre 2026 — CRAA: effetto causale della motivazione MODEL da 225 caratteri

[Rapporto](docs/craa-motivazione-model-2026-10-20.md),
[consegna](<benchmark ufficiale/craa-model-reason-20261020-01/README.md>),
[controlli](docs/benchmarks/2026-10-20-model-reason-checks.json).

Esperimento offline sul caso storico, prima di implementare: stessa risposta
reale, FORM, SOURCE e ricevute USER; modificata soltanto la motivazione del
chiarimento per il sottoscrittore da 225 a 42 caratteri. Il rifiuto diventa
GROUNDED_REQUEST e il campo entra nel pool del narratore. Tutti gli altri gate
FORM/condizioni superati. Confermato nelle cinque copie persistite esaminate.
La lunghezza era dunque causa sufficiente della perdita di una possibilità di
chiarimento, senza cancellazione di testo o decisioni USER già accettate.
Tre messaggi originali contengono già il nome: omissione del campo distinta.

Rieseguite le due esatte risposte salvate del narratore: prima chiede soltanto
la condizione societaria, poi continua a offrire l'export. Un pool corretto non
aggiunge domande a un piano già prodotto. Non si dichiara una nuova domanda
reale, una scelta USER recuperata o un miglioramento del DOCX. Zero inferenze,
token o costi provider nuovi.

Correzione minima generale in compilation_user_requests.py: soltanto una
motivazione descrittiva stringa non vuota oltre il limite riceve una nota
operativa neutra; originale integrale in proposal.reason e grezzo, warning con
lunghezze e posizione del testo. Contratto MODEL a 200, budget globale e tutti
gli altri controlli invariati. Nessuna reinterpretazione di negazioni o uso
della motivazione come fatto SOURCE, assenso USER o applicabilità. Nessuna
migrazione delle sessioni. Prompt/modello/FORM/API/DB/grounding/writer invariati.

RED: 6 FAIL, 20 PASS. Finale: 28 nuovi casi permanenti, due con sessioni isolate
FTS5/Qdrant e provider simulati; 101 mirati PASS 14,32 s; 2.905 backend PASS
225,72 s; Ruff PASS. Rifiuti strutturali, tipi errati, valori extra, budget e
condizioni non dimostrate restano attivi. Preservati i log dei difetti harness,
distinti dai difetti del prodotto. Frontend e rendering PDF non ripetuti.

Regressione senza rete/SQLite: 10 casi in due contesti, due Trapani reali e
ultimo CRAA reale; 23 DOCX identici. 21 audit identici e due copie CRAA con il
solo delta del chiarimento, campo descrittivo e contatori dipendenti.
Minervino61/61; CRAA storico9 e ultimo reale7 invariati. Fatti, condizioni,
binding, checkbox e revisioni identici. coverage_checks_passed diventa TRUE
nel CRAA storico, ma semantic_completeness_verified resta FALSE: non è una
misura di qualità fattuale o un nuovo dato scritto.

Altri file e artefatti precedenti, 29 sessioni e 285 file storage live preservati.
Acquisizioni sotto backend/data/compilation-audit/craa-model-reason-20261020-01;
backup con codice prima/dopo, originali e replay verificato separatamente.
Nessun commit/push, nuovo framework o agente. Backlog intatto: nome firmatario,
CCIAA nel PDF, campi composti e domande ridondanti. Esito circoscritto; nessuna
baseline adottata. Arresto alla consegna.

## 20 ottobre 2026 — Indagine architetturale V12/E1/E2-A: preregistrazione

Protocollo e snapshot in `benchmark ufficiale/diagnosi-architetturale-v12-20261020/`;
log in `backend/data/compilation-audit/diagnosi-architetturale-v12-20261020/`.
Nessuna modifica al codice di produzione. Baseline:2.905 PASS225,54s e23audit/DOCX
esatti;29controlli sperimentali PASS0,24s. SOURCE22chunk verificati uguali alla KB
live;originali e hash archiviati. Working tree sporco congelato, HEAD99ab052.
Riferimento antecedente alle risposte:116occorrenze SOURCE su4documenti, con
censimento separato delle756destinazioni. Nessun valore atteso nei prompt.

36confronti=4documenti×3varianti×3repliche;57analisi reali nuove, nessun retry.
B0 canonico;E1 indice diretto compatto con ricostruzione logica esatta;E2-A sezioni
coerenti, stesso E1 e contesto FORM esterno INTEGRALE. E2-A isola la concentrazione
sulle destinazioni, non la riduzione del testo. Budget, thinking e modello invariati.
Ordine bilanciato seed20261020, concorrenza2. Conservare anche errori e fallimenti.

Valutare separatamente risposta grezza, grounding, riuso SOURCE, condizioni,
revisione reale del narratore, esportabilità e scrittura. Il checkpoint USER
rimane identico dopo le indicazioni iniziali della singola procedura e prima
di ulteriori conferme; nessuna ricevuta costruita o UNKNOWN promosso a TRUE.
Le chiamate del narratore reale saranno contabilizzate separatamente dalle57
analisi. Harness isolato con stato JSON: non presentarlo come prova UI reale.
Risultati e raccomandazione ancora da completare; nessuna baseline adottata.

## 20 ottobre 2026 — Indagine V12/E1/E2-A: risultati conclusivi

[Rapporto completo](docs/diagnosi-architetturale-v12-2026-10-20.md) e
[indice di tutte le 36 repliche con DOCX/PDF](<benchmark ufficiale/diagnosi-architetturale-v12-20261020/README.md>).
Il protocollo precedente è conservato; inventario fisso di 116 occorrenze SOURCE,
nessun GOLD nei prompt e nessun adattamento del denominatore ai risultati.
Tre repliche per quattro documenti e tre varianti: 57 analisi nuove, 42 narratori
reali, 99 chiamate totali, zero retry, stesso fingerprint del provider.
4.743.461 token, 0,931729 USD stimati con tariffe ufficiali e cache osservata,
non fatturazione certificata. Modello/configurazione invariati e acquisiti.

Risultati aggregati su 348 posizioni per variante, nell'ordine B0 / E1 / E2-A:
proposte semanticamente corrette 282 / 278 / 296; grounded prima del riuso
198 / 135 / 201; grounded dopo il riuso 262 / 199 / 265; scritte conformi
54 / 88 / 52. Due equivalenze manuali numero+data sono pubblicate separatamente
(la valutazione automatica resta conservata); non diventano nuove accettazioni
nel grounding. Il checkpoint è dopo la richiesta iniziale e la revisione reale,
prima di ulteriori risposte USER, in harness JSON isolato: non UI E2E e non un
confronto con le 61 scritture Minervino dopo dialogo. Nessuna ricevuta costruita.

E1: token input analisi −9,5%, reasoning +11,5%, costo analisi +6,9%; non emerge
un miglioramento generale della qualità. Minervino migliora nelle proposte grezze,
ma due scope inventano ID inesistenti e bloccano 41 campi ciascuno.
E2-A: 33 chiamate contro 12, costo analisi +57,2%, grounding 201 contro 198.
Catanzaro raggiunge 13 grounded in tutte le repliche contro 9/13/8, ma nessuna
posizione omessa in tutte le B0 viene recuperata in tutte le E2. Recuperi e
perdite appaiati pubblicati. Il FORM esterno rimane intero: E2 misura focus sulle
destinazioni e budget aggiuntivo, non una riduzione del contesto globale.

Backend: 13 posizioni Catanzaro hanno etichette presenti nel FORM completo ma
inutilizzabili come prova locale; sei falsi conflitti fra date equivalenti, due
fra provincia e codice, quattro perdite per ownership con proposta condizionale.
Modello: 113 omissioni fuori dalla barriera con input disponibile, citazioni e
binding insufficienti, condizioni/scopes errati. Non sono percentuali causali
esclusive: il contratto può influenzare ciò che il modello omette.
Due scritture indebite reali, Catanzaro B0/E1 replica 3: sede operativa inserita
nel ramo «se diversa dalla sede legale», con SOURCE che attesta la coincidenza.
Il valore è vero ma il suo uso non è applicabile; writer fedele alla selezione.
Otto proposte PEC Trapani correttamente bloccate per consenso USER mancante.
Un narratore Minervino B0 troncato a 2.048 token, errore conservato senza retry.

36 DOCX/PDF prodotti: 14 copie senza valori, di cui una per fallimento narratore;
22 non vuote, due con errore di ramo. 196 scritture SOURCE, 194 conformi;
zero USER/checkbox. XML e posizioni verificati, valori osservabili nei PDF,
sette pagine viste umanamente; non si dichiara revisione visiva esaustiva.
Dodici falsi negativi della ricerca PDF derivano da interleaving di colonne:
riscontro locale con coordinate conservato, senza modifiche al writer.

Verifiche: 2.905 backend PASS (225,54 s), 29 sperimentali PASS (0,24 s),
tre diagnostici PASS (0,88 s); 23 audit/DOCX storici identici sui sei documenti.
36 nuovi DOCX e 72 audit ricostruiti byte per byte/strutturalmente senza rete o
SQLite. Backup portabile verificato da estrazione, incluse le prove negative.
Intero DB live logicamente identico; 29 sessioni e 285 file storage invariati,
67 moduli applicativi e 1.560 altri file protetti preservati.

La causalità della sola lunghezza JSON resta NON DIMOSTRATA: E1 cambia anche
organizzazione e istruzioni. E1 non è una soluzione di qualità dimostrata;
E2 ha un segnale locale, non un vantaggio generale robusto. Mantenere B0 come
controllo sperimentale senza dichiarare adottata una baseline affidabile.
Priorità proposta, non implementata: sicurezza dei predicati locali; poi relazioni
FORM tabellari e perdite di rappresentazione, conservando attribuzione e assenso.
Nessun cambiamento produttivo, nuova architettura, agente, commit o push.
Arresto alla consegna; correzioni e nuovi confronti richiedono una fase separata.

## 20 ottobre 2026 — Applicabilità locale FORM: correzione circoscritta

[Rapporto](docs/applicabilita-form-v12-2026-10-20.md),
[consegna](<benchmark ufficiale/form-applicability-20261020-01/README.md>).
Intervento esplicitamente richiesto dopo la chiusura dello studio. B0 resta
riferimento; E1/E2-A non integrati. Nessuna modifica di FORM, modello, provider,
prompt, architettura, grounding, attribuzione, parser o writer.

Riprodotti i controesempi originali Catanzaro B0-3/E1-3: condizioni MODEL omesse,
sede operativa grounded scritta nonostante il predicato «se diversa» in p35,
stessa cella etichetta di p34. Le SOURCE dello stesso soggetto attestano sedi
coincidenti. Il validatore verificava solo i predicati emessi dal modello;
il writer eseguiva correttamente la selezione. Il nuovo controllo indipendente
riconosce comparazioni locali FORM generali sulle etichette: uguaglianza/diversità,
negazioni, rami alternativi e ancore fisiche. Richiede prove SOURCE nominate per
lo stesso soggetto; stringhe differenti non dimostrano diversità. Insufficienze
e conflitti rimangono UNKNOWN. Dimensione separata nell'audit, senza riscrivere
fatti, proposte o ricevute USER. FALSE e UNKNOWN bloccano chat/API/export
rivalutato, anche per dati USER e cache obsolete. Il consenso resta separato;
nessuna promozione a RESOLVED o nuova autorizzazione implicita.

Baseline nuova: 2.905 PASS in 234,42 s e 36 DOCX/72 audit esatti dello studio,
comprese le scritture indebite. RED iniziale: 2 FAIL/2 PASS. Aggiunti 91 casi
permanenti, 77 locali e 14 API/persistenza/export con FTS5/Qdrant e provider
simulato: TRUE/FALSE/UNKNOWN, equivalenze strutturali, negazioni, contesti
ipotetici, prove assenti o conflittuali, soggetti diversi, rami complementari,
consenso separato e tentativi di aggiramento.

Prima suite completa: 13 FAIL/2.980 PASS in 280,47 s, per accesso obbligatorio a
type nei cataloghi ridotti dei test di revisione. Corretto nel nuovo controllo,
senza adattare quei test; nuovo negativo sulla cache incompleta. 107 mirati PASS
in 14,57 s; finale 2.996 PASS in 281,80 s, Ruff PASS. Conservati i log intermedi
e gli errori di fixture/harness, inclusi setup prima del server e avvio prematuro
del confronto dopo. Nessuna inferenza ripetuta. Frontend intatto; suite/build
frontend non rieseguite, percorso UI reale verificato separatamente.

Regressione export su 67 casi, con medesimi output MODEL, SOURCE, USER e revisioni,
rete/SQLite vietati. 65 DOCX esatti; due soli delta: B0-3 7→6 ed E1-3 9→8,
esclusivamente t0.r8.c1 rimosso. Sedi legali conservate, nessun nuovo dato o
checkbox. Audit sottostanti identici salvo nuova dimensione FORM. Minervino 61,
due Trapani 17, Bella/Cesano/CRAA e altri checkpoint conservati. Ulteriori 213
triplici storici confrontabili V2–V12, incluso Labirinto: 207 validazioni e sei
rifiuti pregressi identici, salvo aggiunta FORM. Sono confronti dei validatori,
non nuovi export, inferenze o misure di qualità.

Una sola nuova sessione UI reale isolata, 196e0ac512b0410e9b7d71cea6cf04a8,
versione 7 GENERATED. Il modello produce 18 proposte, 16 grounded, e ripete
value/conditions=[] per la sede operativa. Il backend ricava FALSE prima del
narratore, senza necessità di un hold. Un turno USER conferma soltanto il ramo
societario già scelto; gli altri due rami UNKNOWN restano non confermati.
Export esplicito: 15 testi SOURCE, zero USER/checkbox; sede operativa vuota,
legale compilata. Audit, Word e download ricostruiti esattamente offline dalle
ricevute effettive. Numero senza data in t25.r3.c1: risposta parziale indipendente
già nota, documentata e non corretta; 15 scritture non sono 15 risposte complete.

Sette chiamate: una globale, tre router, due sintesi e un guard; 150.364 token,
122,05 s globale e 129,92 s HTTP AI sommati. Stesso FORM/22 SOURCE/prompt/parametri
B0 e deepseek-flash, thinking globale enabled/low; stesso fingerprint dello studio.
Alias/fingerprint non garantiscono pesi immutabili. Un campione, nessun retry di
qualità. Dieci GET abortite al mount/reload; zero POST, console o provider falliti.
Trace/video conservati. XML/CRC/posizioni/prestampato/tabelle/controlli verificati
nei 67 replay e nel reale. PDF prima/dopo e reale di 17 pagine, tutti i valori
osservabili anche tramite coordinate, zero parole fuori pagina; viste pagine
reali 1/2/11, non revisione visiva esaustiva o prova Word desktop.

DB live interamente logicamente identico, 29 sessioni e 273 file storage intatti;
38 sessioni/490 file precedenti del clone conservati, una nuova. I 68 hash
applicativi finali restano fissi, esperimenti originali intatti. Grezzi sotto
backend/data/compilation-audit/form-applicability-20261020-01; backup separato
con codice prima/dopo, input/output/log, senza DB privati, chiavi o env.
Ricostruzione dal pacchetto estratto in VERIFICA-BACKUP.json: 134 DOCX,
268 audit strutturali, 426 risultati dei validatori e l'export reale, senza
SQLite/rete. Nessuna migrazione, reindicizzazione, commit o push; servizi fermati.

PASS circoscritto alla grammatica locale supportata e al difetto dimostrato,
non soluzione universale delle condizioni naturali o della completezza. UNKNOWN
resta bloccato, nessun assenso USER sostitutivo. Vecchie V12 leggibili senza
upgrade; destinazioni comparative prive del controllo non autorizzate. I 13
collegamenti tabellari e gli altri problemi restano fuori intervento. Arresto
alla consegna.


## 20 ottobre 2026 — Relazioni strutturali tabellari FORM V12

Richiesta esplicita successiva all'intervento di applicabilità. Baseline sporca
congelata; riprodotte prima del codice le 13 barriere e il caso CCIAA p439/p440.
Nuovo resolver interno dalla griglia DOCX originale, integrato nel catalogo e
nei validator esistenti; nessuna estensione indiscriminata alla tabella o al
contesto di ruolo. Tutti i 13 legami ora dimostrabili; applicabilità e USER
restano distinti dal fatto SOURCE. Input LLM, modello, prompt globale e writer
conservati, E1/E2-A non integrati.

52 test permanenti nuovi; suite finale 3.048 PASS/234,16s e Ruff PASS. Fallimenti
intermedi conservati: primo replay CRAA perdeva sette scritture per scope di
condizione ristretto (separato dalla prova di proprietà e coperto da test);
prima suite completa 2 FAIL/3.028 PASS per underscore, corretta riusando il
parser. Le iterazioni e gli errori delle prime fixture sono nel rapporto.

68 replay export prima/dopo, tutti byte-identici; Minervino61, Trapani17,
Bella/Cesano/CRAA/Catanzaro conservati. 213 confronti validator: 199 esatti,
14 con nuovi archi, sei rifiuti root precedenti invariati, nessuna perdita
grounded o modifica della verità MODEL. 29 occorrenze nuove grounded nei 68
replay (tre destinazioni distinte, 17 occorrenze nelle nove repliche Catanzaro);
21 promozioni nel protocollo 213 sovrapposto, conteggi non sommabili. Nessuna
revisione retroattiva delle nuove proposte o mutazione degli artefatti congelati.

Una sola sessione UI reale `343d6caf16d442ed88ef174ebaf4aae0`, v7 GENERATED,
dopo preregistrazione e regressione PASS. Stesso deepseek-flash/FORM/prompt/22
SOURCE/parametri; un turno ripete società e firmatario già scelti, poi export
parziale e download. 26 proposte, 18 grounded anche condizionate, 17 testi
SOURCE scritti, zero USER/checkbox. Dei 13: 7 proposti, CCIAA Bari scritta,
6 bloccati da altre prove, 6 omessi. Con la stessa risposta/ricevute: 16 testi
nel backend precedente, 17 nel nuovo, sola aggiunta causale t25.r2.c0=Bari.
Sede operativa FALSE vuota. Numero senza data t25.r3.c1 resta difetto noto
indipendente; non dichiarate 17 risposte complete o miglioramenti generali LLM.

XML/CRC/geometria/posizioni e controlli verificati; otto PDF storici delle sei
famiglie e PDF reale 17 pagine leggibili, zero parole fuori pagina, campioni
visivi, non Word desktop. Sette chiamate, una globale 146,30s, 156.322 token,
stesso fingerprint, nessun retry. Dieci GET abortite da mount/reload; nessuna
POST/console/provider fallita. Servizi arrestati; stato live e originali
preservati, nessuna migrazione/reindicizzazione/commit/push.

[Rapporto](docs/relazioni-tabellari-form-v12-2026-10-20.md),
[consegna e backup separato](<benchmark ufficiale/table-form-links-20261020-01/README.md>).
Riproduzione estratta offline e preservazione nei rispettivi JSON della
consegna; chiavi/DB privati esclusi. Limiti semantici, SOURCE composti, ruoli,
USER, narratore e schemi ambigui documentati senza correggere altri componenti.


## 21 ottobre 2026 — Completezza semantica dei valori composti V12

Richiesta corrente distinta dalle relazioni tabellari concluse: impedire che un
fatto SOURCE vero ma parziale soddisfi un campo cumulativo. Riproduzione esatta
prima del codice dell'ultima UI Catanzaro, numero 01234560981 in `t25.r3.c1`
nonostante FORM numero+data. Fonte del numero e condizioni conservate.

Audit backend indipendente COMPLETE/INCOMPLETE/UNKNOWN, requisiti dalle prove
FORM fisiche, componenti/provenienza e legame di record. Selezione, dialogo USER,
riapertura e ricalcolo all'export coperti; riuso esistente aggiornato senza nuove
regole. Nessuna composizione multi-span: limite del contratto letterale attuale,
alternativa con componenti/record_key proposta e non implementata. Prompt, modello,
B0, parser, writer e controlli precedenti invariati; nessuna integrazione E1/E2.

132 nuovi casi permanenti e fixture congelata; 3.180 backend PASS e Ruff PASS.
69 export prima/dopo, 56 identici e 13 con sole 15 rimozioni dichiarate: cinque
numeri senza data, dieci recapiti singoli sotto coordinazione ambigua UNKNOWN.
213 triplet V2–V12: 207 validati, sei precedenti rifiuti conservati; tutti gli audit
uguali al netto della dimensione aggiunta. Inventario nove originali, 159 requisiti,
160 proposte: 118 COMPLETE, sei INCOMPLETE, 36 UNKNOWN. 31 PDF regressione e
posizioni XML/controlli verificati. Fallimenti intermedi su alternative, attese
preesistenti e qualificatori opzionali corretti; tentativi dell'harness senza
fixture/PYTHONPATH e riepilogo PDF anticipato conservati, non nascosti.

Una E2E reale preregistrata su clone: sessione e81df1cca6b34606a923857c5605d325,
otto chiamate, una globale 118,06s, 155.285 token. Stesso FORM, 22 SOURCE, modello,
prompt e parametri. Due conferme USER limitate ai rami societari dello scenario,
nessuna attestazione. 16 scritture SOURCE, zero USER/checkbox, download ordinario
ricostruito esattamente offline; PDF 17 pagine leggibile e campioni visivi.
Il modello omette numero/data e telefono: nessuna nuova proposta parziale in
questa E2E, confronto stessa nuova risposta 16→16. Il veto causale si dimostra
sulla stessa vecchia risposta reale, 17→15. Non attribuire al backend una migliore
proposta del modello. Nessun retry, zero POST/console/provider fallite; dieci GET
abortite per acquisizione (20 totali). Servizi arrestati. Quattro nuovi positivi sui formati di sezione hanno
individuato due confronti sensibili alle maiuscole dopo la prima UI: corretti
con re.I, 3.180 test/replay finali PASS e riesportazione UI della stessa analisi
reale su codice finale, versione 8, senza seconda globale o retry di qualità.

[Rapporto](docs/completezza-valori-composti-v12-2026-10-21.md),
[artefatti e backup separato](<benchmark ufficiale/compound-values-20261021-01/README.md>).
Limiti: grammatica dichiarata, non semantica universale; niente composizione
multi-span, nessuna soluzione indipendente a ruoli/narratore/preferenze/checkbox.
Preservazione e estrazione con replay offline nei rispettivi JSON; credenziali
e DB privati esclusi. Nessun commit/push/migrazione/reindicizzazione.


## 21 ottobre 2026 — Valutazione candidata baseline V12, tre compilazioni indipendenti

Eseguita la richiesta di valutazione senza toccare la correzione conservativa
dei valori composti. Prima delle inferenze congelati working tree, 119 hash
applicativi, SOURCE, scenario USER per pratica e riferimenti; selezionati
Minervino e Cesano per strutture differenti, più CRAA da un solo sorteggio fra
Bella/Catanzaro/CRAA/Trapani (seed e algoritmo in SELEZIONE.json). Errore iniziale
dello script d'ispezione conservato, prima del sorteggio; nessun tentativo modello
fallito sostituito. Tre nuovi progetti/sessioni/conversazioni in clone isolato,
nuova globale reale per ciascuno, UI ordinaria, risposte agli slot 2/2/1 entro
budget uniforme massimo due e una richiesta di export parziale per documento.

DOCX scaricati: Minervino 43 testi, Cesano quattro testi e sei booleani di un
gruppo, CRAA sette testi. Tutte le 60 voci di scrittura hanno revisione documentale
separata da grounding/validatori: nessuna non dimostrata osservata, nessuna pretesa
di accuratezza universale. Dei 74 valori fattuali preregistrati 54 sono scritti:
17 omissioni ingiustificate, uno fermo per budget del dialogo, due CCIAA fermati
da una attestazione non confermata. Una ulteriore checkbox USER Minervino omessa.
Tutte le 406 destinazioni classificate; sette tentativi Cesano di trasferimento
società→persona correttamente respinti. Nome/dati firmatario mancanti, record DT
parziale e copertura checkbox discontinua sono limiti effettivi di completezza.

28 chiamate provider, tre globali nuove, 397.982 token, costo a tariffa
0,086193018 USD stimato. Parametri globali, SOURCE e modello identici; zero retry,
fallimenti provider/POST/driver/console. Tempi monotoni per chiamata e tempi UI
inclusivi delle attese registrati separatamente. Audit, DOCX e download ricostruiti
esatti senza rete/SQLite; XML/CRC, controlli Word e PDF di 19 pagine verificati.
Nessuna nuova prova positiva numero+data o di scrittura tabellare autorizzata;
nessuna modifica alla grammatica FORM o composizione multi-SOURCE. Non rieseguita
la suite storica 3.180 PASS/Ruff PASS perché il codice applicativo è invariato.

Proposta motivata, **non adozione**: possibile baseline sperimentale conservativa
per bozze parziali, non completa/definitiva. Una prova per documento già studiato,
corpus aziendale sintetico, budget di dialogo limitato, revisione autoriale.
Originali, modifiche pregresse, DB/storage live e sessioni precedenti preservati;
backup separato verificato da estrazione con tre ricostruzioni offline, senza
credenziali/DB privati. Servizi fermati. Nessun commit/push o intervento successivo.

[Rapporto](docs/valutazione-baseline-v12-2026-10-21.md),
[DOCX/PDF, protocollo, audit e backup](<benchmark ufficiale/baseline-v12-20261021-01/README.md>).


## 21 ottobre 2026 — Adozione documentale della baseline sperimentale conservativa V12

Decisione esplicita dell'utente successiva alla proposta: adottata per confronti
sperimentali nella compilazione assistita di bozze DOCX parziali con revisione
umana obbligatoria, non versione completa/definitiva o pronta per pratiche
ufficiali senza verifica. Stato candidato ADOPTED_FOR_EXPERIMENTAL_COMPARISONS;
cronologia, hash e copia originale nel backup preservano PROPOSED_NOT_ADOPTED.
[Manifesto BASELINE-V12.md](BASELINE-V12.md), con snapshot/patch locali, 119 hash,
configurazione e input già congelati; nessun tag o nuovo framework di benchmark.

Riferimenti invariati: tre nuove prove precedenti Minervino, Cesano, CRAA,
54 testi e sei booleani; zero non dimostrate osservate nella revisione documentale
autoriale, 17 omissioni fattuali, una checkbox omessa, un campo fermo per budget.
28 chiamate e 397.982 token, costo stimato 0,086193018 USD, sono misure precedenti.
Minervino storico 61 (60 testi+checkbox, risposta globale congelata e dialogo
precedente) distinto dalla nuova globale indipendente a 43 testi; non misura
una regressione deterministica sulla stessa proposta. Tutti i limiti restano,
inclusi variabilità, corpus sintetico, una sola prova/documento, revisione non
indipendente, grammatica FORM limitata, nessuna composizione multi-SOURCE e
copertura incompleta di checkbox/record distribuiti.

Verifica di consistenza documentale e hash, senza riesecuzione di compilazioni,
LLM, suite o rendering. Riutilizzati manifest e archivio originali, senza
riscriverli; addendum documentale separato, nessuna duplicazione dei dati grezzi.
La differenza attesa dal manifest originale riguarda soltanto candidato, STATUS
e relazioni; rapporto, prove, codice, prompt, test, DB/sessioni e backup conservati.
[Verifica e preservazione](<benchmark ufficiale/baseline-v12-20261021-01/ADOZIONE-VERIFICHE.json>).
Nessun commit, tag o push; fermarsi dopo questa formalizzazione.

## 21 ottobre 2026 — Rimozione del nome del progetto dalla presentazione

Richiesta successiva all’adozione della baseline: etichette neutre nell’app,
titolo della scheda «Assistente documentale», risposte «Risposta» e composer
«Messaggio per l’assistente». Aggiornati testi di navigazione, profilo, aiuto,
demo, API, accesso OpenRouter e metadati dei pacchetti. Nei prompt di chat/router
rimossa l’identità nominativa; globale B0, compilazione e controlli invariati.
Conservati documenti, valori aziendali, percorsi e identificatori persistenti.

126 test frontend, 232 backend mirati e quattro E2E simulati desktop/mobile
PASS; lint, build, Ruff e sintassi shell PASS. Ispezione aggiuntiva di titolo,
drawer desktop, navigazione mobile, composer e demo PASS. Un timeout iniziale
dello script dovuto al drawer nascosto su mobile è conservato nell’audit;
corretto lo script senza modificare il comportamento dell’app. Nessuna inferenza
reale o nuova prova di compilazione con provider. La baseline e i suoi backup
restano congelati, mentre il working tree include questa modifica successiva.

Audit ui-neutral-naming-20261021-01 e riepilogo/backup in docs/benchmarks/.
Nessun commit o push.

## 21 ottobre 2026 — V13 S1, candidata in valutazione

Riprodotte le 17 omissioni prima del codice. Recupero conservativo nello stesso
percorso di validazione/riuso SOURCE: selezione USER esplicita con qualificatore
della pratica, nome inline in cella, proprietà di record personali collegati da
chiavi forti e continuità FORM dell’operatore grounded condizionato. Nuove
sessioni backend_revision=13; contratto MODEL/B0 resta V12. Vecchie sessioni
senza revisione non aggiornate; valori letterali e controlli indipendenti conservati.

184 nuovi test; suite finale 3.364 PASS e Ruff PASS. Prima suite completa con due
errori pertinenti corretti prima del congelamento; log conservati. 69 export
legacy e 69 con V13 identici, 213 validator storici invariati, sette trasferimenti
azienda→persona Cesano ancora respinti. Su risposta e ricevute baseline identiche
17 proposte recuperate, ma nessuna nuova scrittura senza la nuova revisione.

Candidata congelata con 120 hash; campagna preregistrata da 45 nuove prove reali,
avviata alle 16:04 UTC. Quattro risposte USER al massimo contro due V12, sei
contesti browser isolati, una globale per sessione, nessuna ripetizione selettiva.
I primi esiti mostrano anche blocchi di dialogo/autorizzazione e bozze vuote:
registrati senza cambiare codice o policy. **Verifica reale ancora in corso,
nessuna adozione o conclusione di efficacia.**

Rapporto in aggiornamento: docs/v13-s1-omissioni-fattuali-2026-10-21.md.
Snapshot/replay/nuovi export: benchmark ufficiale/v13-s1-20261021-01/;
grezzo e log: backend/data/compilation-audit/v13-s1-20261021-01/.

## 21 ottobre 2026 — V13 S1, due coorti reali concluse e giudizio

Prima coorte da 45 tentativi: 41 DOCX, quattro senza DOCX (due risposte globali
troncate, due JSON non validi). Errore del protocollo USER: alternative lette in
«senza raggruppamenti o consorzi», scelte già fatte rinviate. Seconda coorte
completa da 45 con sola correzione della policy, decisa dopo aver visto la prima
e verificata senza chiamate su 58 contesti: 38 DOCX, sette senza (due troncamenti
globali, un JSON non valido, tre narratori troncati al primo turno prima di ogni
risposta USER alle domande, un dialogo Minervino bloccato sull'«amministratore
unico»).
Nessuna sostituzione o ripetizione selettiva; stesso codice da 120 hash.

Stesse risposte e ricevute, codice V12 → V13: 98 → 217 e 407 → 526 testi, 238
aggiunte tutte corrette alla revisione autoriale, zero rimozioni/cambi, checkbox
identiche; codice before/ eseguito su 79/79 casi. 233 aggiunte vengono dalla
selezione USER esplicita del firmatario, quattro dai record DT tipizzati, una
dalla continuità dell'operatore. L'aumento fra coorti a parità di codice è
dovuto soprattutto al protocollo USER (con codice V12: 98 → 407).

Quattro scritture CCIAA non dimostrate in craa-03/04 (provincia e numero di
iscrizione): il modello omette la condizione societaria, presente nelle altre 18
risposte CRAA; il codice V12 sulle stesse risposte le scrive uguali. Non
introdotte da S1, ma il sistema non garantisce zero scritture non dimostrate.
Celle originali da 66 e 81 twip: numero invisibile, due PDF FAIL su 79.
Omissioni ingiustificate residue 62 e 56; gruppo checkbox Cesano mai scritto.

Chiusura senza nuove inferenze: otto PDF mancanti resi con il renderer congelato,
aggregato PDF, confronto finale, backup unico verificato da estrazione e replay
offline (SHA256 75d60b93…), scansione credenziali anche negli ZIP. Giudizio:
miglioramento reale ma parziale, **nessuna adozione automatica**; decisione
all'utente fra adozione con limite CCIAA dichiarato e intervento separato prima.

Rapporto conclusivo: docs/v13-s1-omissioni-fattuali-2026-10-21.md.
Confronto: benchmark ufficiale/v13-s1-20261021-01/CONFRONTO-FINALE-V12-V13.json.

## 21 ottobre 2026 — Esperimento offline A sulla priorità P1

Ipotesi verificata: dopo la revisione tecnica indipendente, P1 (decisioni USER come
stato del backend, una ricevuta propagata a tutte le condizioni della stessa decisione,
blocco strutturale delle opzioni non scelte) sarebbe stata la prima priorità. Nessuna
modifica applicativa: HEAD `99ab052` con il working tree della V13 non adottata;
preregistrazione `PREREG.md` SHA256 `20f4ad41…` (18:27 UTC) e annotazione delle opzioni
`de3f1a1d…` (18:28 UTC) prima dei risultati. Nessun provider, nessuna chiamata, nessun
DOCX generato. Input: 17 risposte globali Minervino (baseline e 8+8 V13), 21 CRAA,
806 scritture verificate; 240 input con hash.

Esiti, codice V13 effettivo, scritture corrette su 60 per risposta: con protocollo
corretto il dialogo reale ottiene 262 contro un tetto oracolo di 268 (baseline e
coorte 2 con DOCX); nella coorte 1 63 contro 448 perché la condizione di ramo non
viene confermata (SKIP del copione o domanda mai posta); nelle 4 prove senza DOCX il
fallimento è del narratore. Condizioni rilevanti 1–3 per risposta: nessuna
frammentazione. Nei controfattuali le condizioni LLM etichettate con oracolo autorizzano
in 17/17 risposte campi che richiedono altre decisioni (la condizione dell'opzione
«società di ingegneria» copre anche dati dell'operatore e del firmatario); proposte
senza condizioni in 6/17 (V12) e 11/17 (V13). Etichette lessicali senza gold:
68/76 condizioni concordi, controesempi analoghi. Blocco strutturale: R1 0/4 CCIAA,
R2 4/4 con 0 corrette bloccate, R3 4/4 con 114 corrette bloccate.

Decisione dell'utente: accettata la revisione di P1; il raggruppamento delle condizioni
LLM non va implementato. Limiti: un solo gold, annotazione dell'autore, cattura delle
decisioni assunta perfetta, narratore non simulato. Rapporto:
docs/p1-esperimento-offline-a-2026-10-21.md; grezzo
backend/data/compilation-audit/p1-offline-a-20261021-01/; backup
docs/benchmarks/2026-10-21-p1-offline-a-audit.tar.gz (SHA256 `b34bb5eb…`), verificato
con due estrazioni e riesecuzione a output identici.

## 21 ottobre 2026 — Diagnosi CCIAA, generalità di R2 e veto minimo proposto

Analisi offline, senza chiamate LLM, campagne o modifiche applicative. CCIAA: i
riferimenti V12/V13 marcano le celle TRUE_IN_SCENARIO perché inventariano ramo attivo e
fatto disponibile; la revisione giudica l'autorizzazione della dichiarazione «per
un'attività coerente con la classe merceologica», che lo scenario lascia UNKNOWN. Stessa
regola nella baseline (LEGITIMATELY_OPEN) e nelle 20 prove V13 (18 aperte dopo SKIP, 2
scritte senza condizione). Valore citato dalla SOURCE (numero RI 01234560981; leggerlo
come «numero di iscrizione» CCIAA anziché REA è un'interpretazione condivisa dal gold
Minervino), autorizzazione mancante; gold e giudizi invariati.

R2 su sei moduli di sviluppo e sette esterni del pool casuale (PREREG-R4 SHA256
`96b7a0c9…`, 18:42 UTC): la struttura Word non codifica l'ambito delle opzioni; R2 perde
figli senza «:» (8 campi Minervino, 15 Calabria); estensioni senza «:» bloccano contenuti
condivisi (24 campi del sottoscritto in Soresa) o tabelle successive a un paragrafo
intermedio (Soresa, Cannara); marcatori «[ ]» e U+F06F non rilevati; condizioni solo
testuali invisibili. Con sblocco da ricevute USER registrate (casella dell'opzione o
condizione confermata ancorata nel suo segmento) R1T, R2 e R4 bloccano 4/4 CCIAA e 0 su
802 scritture corrette; R1T non usa i «:» ed evita gli eccessi osservati di R4.

Proposta, non implementata: veto d'export R1T con sblocco U1/U2, controlli propri
dell'opzione esenti, TRUE annidati bloccati, sole nuove sessioni con revisione esplicita;
piano T0–T5 con replay offline atteso «solo le 4 celle CCIAA rimosse». Rapporto:
docs/cciaa-r2-veto-opzioni-2026-10-21.md; grezzo
backend/data/compilation-audit/cciaa-r2-diagnosi-20261021-01/; backup
docs/benchmarks/2026-10-21-cciaa-r2-diagnosi-audit.tar.gz (SHA256 `f608153b…`), verificato
con due estrazioni, 287 input invariati, 7 output e 7 cataloghi esterni identici.

## 21 ottobre 2026 — Candidata V14, autorizzazione delle clausole d'opzione

Ipotesi: la conferma USER di un ramo («per le società») non deve autorizzare le
attestazioni del ramo. Verifica prima del codice sugli stati registrati: con V13 una sola
ricevuta «è una società» esporta le celle CCIAA in 21/21 prove CRAA; il disegno R1T con
sblocco da condizione ancorata avrebbe ereditato il difetto. Corretto: un valore in una
regione d'opzione (casella o glifo, paragrafo più tabella adiacente) richiede l'assenso
esplicito alla domanda del backend con la clausola integrale, tramite il consenso
procedurale esistente. Solo nuove sessioni (`option_authorization_revision = 1`, base
V13/S1 congelata); preregistrazione T0 SHA256 `d3d179f5…`.

Nessun provider né chiamata LLM. Esiti: 16 test nuovi; suite 3.380 PASS, Ruff PASS; replay
offline di 82 DOCX/806 scritture con 13 rimozioni (4 CCIAA craa-03/04, 9 `p19.ft0` Cesano
basate solo su selezioni) e nessun'altra modifica; profilo V14 0/21 esportazioni CCIAA
dopo ricevuta di ramo. Sessioni senza flag invariate (93/93 stati). Limiti: costo di dialogo
non misurato, protezione limitata ai marcatori riconosciuti e alle tabelle adiacenti.
Candidata non adottata. Rapporto: docs/v14-autorizzazione-clausole-opzione-2026-10-21.md;
grezzo backend/data/compilation-audit/v14-option-authorization-20261021-01/; backup
docs/benchmarks/2026-10-21-v14-option-authorization-audit.tar.gz (SHA256 `b740e151…`).

## 21 ottobre 2026 — Criteri di conclusione congelati (versione 1)

Decisione dell'utente: chiudere il lavoro su criteri misurabili anziché correggere ogni
omissione. Documento docs/criteri-conclusione-2026-10-21.md, copia in sola lettura in
benchmark ufficiale/criteri-conclusione-v1/ (SHA256 `f3ec66be…`, 19:27 UTC), congelato prima
delle prove V14. Soglie: DOCX ≥ 4/5 per modulo e ≥ 90% totale; copertura mediana del nucleo
≥ 70% per modulo; zero scritture non dimostrate alla revisione indipendente; nessuna
conferma ridondante; motivo tracciato per ogni vuoto pertinente; almeno un modulo nuovo e
una SOURCE in formato diverso, separati dai benchmark storici; warning per valori invisibili
nel PDF. Compatibilità tecnica del modulo valutata in anticipo; cinque tentativi per modulo
nella valutazione finale. Soglie sperimentali, nessuna modifica retroattiva.

## 21 ottobre 2026 — Revisione UX/UI delle impostazioni RAG

Separati metodo di ricerca, generazione embedding, archivio vettoriale e
manutenzione. Verificato il significato dei contratti esistenti: Qdrant integrato
usa `QdrantClient(path=...)`, il servizio embedding è Ollama e bge-m3 è soltanto
il modello predefinito. La configurazione tecnica conserva modello, indirizzi,
chiavi e prefissi esistenti; verifica e aggiornamento indice restano azioni
diverse. Solo UI, CSS, test pertinenti e documentazione, nessun algoritmo o
formato persistito modificato; nessuna nuova valutazione V12/V13/V14 o chiamata LLM.
138 test frontend PASS (16 del pannello), quattro E2E desktop/mobile con API
simulate PASS, lint/build PASS e 35 test backend pertinenti PASS su dati
temporanei. Preservazione nel rapporto docs/revisione-ui-ricerca-2026-10-21.md e nell'audit
backend/data/compilation-audit/retrieval-settings-ui-20261021-01/.

## 21 ottobre 2026 — Due riquadri RAG e selettore embedding Ollama

Rifinitura UI richiesta: «Ricerca nelle fonti», metodo «Semantica» e impostazioni
avanzate dell'archivio; riquadro distinto «Modelli di embedding», con proprie
impostazioni avanzate Ollama. Descrizioni rimosse come richiesto. Il nuovo endpoint
in sola lettura riusa la discovery esistente con capacità `embedding`, senza
download, generazione, indicizzazione o migrazione. Chiavi dei due servizi
isolate; formato persistito e filtro generativo predefinito conservati. Modello
salvato preservato se elenco assente/ambiguo o servizio irraggiungibile.
Verifiche e limiti in docs/revisione-ui-ricerca-2026-10-21.md, revisione 2;
audit separato retrieval-settings-ui-20261021-02. Nessun commit o push.
143 test frontend PASS (21 del pannello), quattro E2E desktop/mobile con API
simulate PASS, 76 test backend pertinenti PASS (14 nuovi); Ruff, lint e build PASS.

## 21 ottobre 2026 — Provider embedding e riordino delle impostazioni

Su richiesta, riquadri nell'ordine AI → embedding → ricerca. Aggiunti OpenAI,
Mistral e API embedding compatibili accanto a Ollama, con un provider attivo e
chiavi indipendenti dalla chat. Configurazioni precedenti ancora Ollama senza
migrazione; cambio provider protetto dal riuso involontario della vecchia chiave.
Il nuovo adattatore usa il contratto embedding reale, con ordine/conteggio/dimensioni
dei vettori verificati e identità dell'indice distinta per servizio. Nessun
algoritmo di retrieval, componente DOCX o benchmark modificato. Limite dichiarato:
nessun digest dei pesi per le API remote. Rapporto docs/provider-embedding-2026-10-21.md;
log e risultati in backend/data/compilation-audit/embedding-providers-ui-20261021-01/.
Verifiche: 3.426 backend PASS (32 nuovi), 147 frontend PASS (25 del pannello),
sei E2E desktop/mobile simulati PASS, Ruff/lint/build PASS. Auto-reload del backend
preesistente: ricreati ID/timestamp di 82 chunk artifact e FTS; contenuti e
posizioni conservati, SOURCE e 29 sessioni invariati. Due file di compilazione
modificati da attività concorrente conservati, nessun ripristino del DB attivo.
Backup circoscritto e verificato per estrazione separata, esclusi i dati privati.

## 21 ottobre 2026 — Verifica E2E della candidata V14 (sei prove reali)

Ipotesi: nei dialoghi reali la conferma del solo ramo non deve autorizzare la clausola
d'opzione, mentre un'autorizzazione esplicita deve essere accettata con un costo di
dialogo limitato. Protocollo preregistrato alle 19:30:07 UTC dopo i criteri di conclusione;
codice V14 a 121 hash verificati a ogni chiamata; prompt B0, catalogo e SOURCE identici
alla V13; DeepSeek `deepseek-flash`, una globale per prova, nessuna ripetizione; politica
USER naturale (SHA256 `c6001c3c…`). 55 chiamate, 802.062 token.

Esiti: 6 DOCX su 6. In craa-ramo la ricevuta «Sì, Mapi Ingegneria S.r.l. è una società.»
lascia vuote le celle CCIAA, che la V13 avrebbe scritto con le stesse ricevute. In
craa-autorizza l'autorizzazione è accettata, ma la condizione di ramo del modello non viene
chiesta dal narratore: celle vuote. Cesano: `p19.ft0` recuperato in 1 prova su 2,
nell'altra trattenute del narratore non rilasciate. Minervino: 51/60 e 26/60 (33 rifiuti
di binding). Nessuna scrittura non dimostrata alla revisione dell'autore, nessun valore
invisibile nei PDF, nessuna risposta rifiutata, una domanda slittata. Limiti: sei prove,
revisione non indipendente. Candidata non adottata. Rapporto:
docs/v14-verifica-e2e-2026-10-21.md; archivio in benchmark ufficiale/v14-verifica-20261021-01/
(SHA256 `2c317d72…`).

## 21 ottobre 2026 — P2, attribuzione di ruolo a livello di record (offline)

Ipotesi: molte proposte personali corrette sono respinte perché il ruolo viene legato
alle citazioni scelte dal modello. Una verifica a livello di record recupererebbe queste
proposte senza scritture improprie. La verifica usa:
- il ruolo nel contesto strutturale del campo FORM;
- la proprietà tipizzata dall'etichetta;
- un record SOURCE certo trovato dal backend;
- il valore nel record o collegato da chiavi forti;
- protezioni per cessazione e altra azienda.

Base tecnica V14, non baseline. Zero chiamate LLM; risposte registrate di V13 (due coorti),
verifica V14 e baseline V12. Preregistrazione alle 20:44:06 UTC (SHA256 `a73bffca…`) con
regola di decisione:
- almeno 10 recuperi corretti in almeno due documenti;
- 0 errati;
- tutti i controesempi negativi respinti;
- i sette rifiuti Cesano preservati.

Esiti della simulazione: 47 recuperi corretti (Minervino 43, Catanzaro 4), 0 errati,
0 regressioni. Rifiuti Cesano preservati (8 prove), amministratore cessato bloccato 5
volte, 0 recuperi in regioni d'opzione. I recuperi coprono 41 delle 81 proposte corrette
respinte per ruolo nelle coorti V13/V14, più 6 nella baseline. Nessuna delle 26 proposte
con valore diverso dal riferimento è stata recuperata.

Controesempi su SOURCE sintetiche: prima serie 15/15 conforme. Seconda serie, scritta per
cercare falle: 5 negativi su 11 recuperati.
- FORM: ruolo dell'impresa ausiliaria e della mandante.
- SOURCE: DT di un'altra azienda grounded e CF societario nel record della persona.
- Carica lasciata con un verbo non in elenco.

La regola di decisione non è soddisfatta: non implementata.

Prova diagnostica: gli stessi 5 casi passano anche il gate V12/V14 quando le citazioni
sono corrette. Nessuna delle 719 proposte personali accettate registrate li attiva.

Limiti:
- la SOURCE è una sola KB sintetica;
- i lessici di cessazione sono incompleti;
- l'ambito aziendale del ruolo non è verificabile in modo strutturale;
- il formato dei codici personali non è controllato.

Opzioni lasciate all'utente: nessun P2 autonomo; conferma USER per persona e ruolo
(raccomandata, con P3); rafforzamento del gate condiviso e poi P2 v2. Rapporto:
docs/p2-attribuzione-record-2026-10-21.md; backup docs/benchmarks/2026-10-21-p2-record-binding-audit.tar.gz
(SHA256 `57ba6489…`).

## 21 ottobre 2026 — Controllo di attribuzione condiviso (offline)

Ipotesi: tre controlli generali sul gate condiviso possono impedire attribuzioni
personali all'impresa o al soggetto sbagliato senza perdere scritture corrette:
- classe del codice fiscale (K1);
- coerenza «in chiusura» delle attestazioni di persona e ruolo, senza elenchi di verbi (K2);
- organizzazione nominata nell'attestazione (K3).

L'appartenenza lato FORM (K4) è esclusa a priori: nei 13 moduli reali la stessa
sintassi indica l'operatore tipizzato o un partner, a seconda della forma di partecipazione.

Preregistrazione alle 21:11:57 UTC (SHA256 `2772f511…`) con 27 casi sintetici, inclusi
i cinque controesempi di P2 e SOURCE di formati diversi. La regola di decisione vale per
ciascun controllo:
- tutti i negativi bloccati e nessun positivo bloccato;
- nel replay, perdite corrette al massimo del 2% in totale e del 5% per documento.

Esiti:
- casi sintetici: conformi (25 contati, 2 esclusi perché il gate attuale non li accetta);
- replay su 92 audit registrati: K1 perde 39 corrette (partita IVA `IT01234567890`
  aziendale), K2 ne perde 147 (15,5%; una frase affermativa della KB basta), K3 nessuna.

Solo K3 è implementato, per le nuove sessioni (`attribution_safety_revision: 1`). Il
modulo applicativo è equivalente al candidato valutato su 26 casi e 92 audit. Verifiche:
13 test nuovi, suite backend completa PASS (3.439 test raccolti), Ruff PASS.

Rischio residuo: controesempi 1, 2, 4 e 5 di P2 e documenti di terzi senza organizzazione
esplicita. Rapporto: docs/controllo-attribuzione-2026-10-21.md.

## 22 ottobre 2026 — P3: dialogo con stato delle decisioni e generazione per sezioni

Diagnosi preregistrata degli 11 fallimenti V13 (sola lettura). Le componenti sono diverse:
- 4 troncamenti globali: il ragionamento consuma il 69–76% dell'output;
- 3 JSON non validi: tabulazioni letterali; annidamenti incompleti;
- 3 narratori troncati da sospensioni scritte una per una;
- 1 dialogo bloccato su una condizione diversa dalla risposta.

Altre cause dimostrate:
- 92 rifiuti su 102 dovuti al filtro « o » con la guardia semantica `SUPPORTED`;
- sospensioni ereditate senza condizioni;
- decisioni del primo messaggio chieste di nuovo;
- 402 proposte grounded dietro condizioni mai chieste.

Interventi, solo per le nuove sessioni:
- `generation_revision` (segmenti con contesto intero, unione validata dal V12 invariato);
- `dialogue_revision`: decisioni dal primo messaggio tramite la guardia, niente filtro « o »,
  sospensioni legate al blocco, domande sulle condizioni aperte, guardia sui cicli,
  sospensioni raggruppate, data corrente.

Verifiche:
- proiezione: 0 differenze su 12.677 candidate;
- replay sospensioni: 36 rilasci su 47;
- replay filtro: 110 su 110;
- 34 test nuovi, suite 3.479 PASS, Ruff PASS.

Deviazione prudente dalla preregistrazione: un dubbio SOURCE non si rilascia mai con una
conferma USER.

Campagna E2E preregistrata (16 prove, bracci A e B, 3,62 milioni di token): 12 DOCX su 16.
I 4 fallimenti hanno la stessa causa P3: il narratore viene respinto per sospensioni non
ancorate o fuori finestra. Nelle 96 prove storiche non era mai successo.

B contro A:
- 0 troncamenti;
- 25/28 chiamate sotto il 50% del limite;
- output mediano 12k contro 30k;
- token 2,7×;
- 2 segmenti persi per JSON non valido e resi visibili;
- nessun guadagno dimostrato sul nucleo.

Dialogo: Cesano `p19.ft0` scritto 4/4; CRAA CCIAA scritte 2/2 con ramo e autorizzazione,
vuote 2/2 nella variante «ramo»; nessuna scrittura non dimostrata (revisione dell'autore);
domande ridondanti ancora 10.

Giudizio: candidata non pronta per un peggioramento grave del narratore. Prossimo passo:
correggere la validazione delle sospensioni, verificare offline sulle 4 risposte reali, poi
una nuova breve verifica E2E. Rapporto: docs/p3-dialogo-generazione-2026-10-22.md.

## 22 ottobre 2026 — Narratore P3: correzione delle sospensioni e fallback dell'app live

Richiesta: intervento circoscritto dopo il P3 non adottato (12/16 DOCX).

**Priorità immediata.** L'app live (uvicorn `--reload` sul working tree) creava le nuove
sessioni con P3; nessuna sessione salvata ne era coinvolta. `initial_state` rende P3 opt-in
(`MAPI_DIALOGUE_REVISION=1`, `MAPI_GENERATION_REVISION=1`, separati). Il predefinito è
V14 + K3. Verifiche:
- worker ricaricato;
- profilo e richiesta globale identici all'albero pre-P3 ricostruito (75/75 hash);
- 215 sintesi legacy identiche al pre-P3.

Unica differenza trovata: due chiavi vuote nella transizione delle sessioni legacy, ora solo
P3 (addendum 1).

**Diagnosi** (offline, zero LLM): le 4 sintesi respinte si riproducono con contesto identico
alla richiesta reale. Cause:
- 3 casi: citazioni letterali del contesto ma fuori dalla zona della proposta (record SOURCE,
  fonte di un'altra proposta, motivazione MODEL);
- 1 caso: proposte inesistenti con finestra vuota.

Il validatore V12 respingeva l'intera sintesi. In più, nel rilascio P3, 27 legami su 45 erano
a slot che non governano la proposta.

**Correzione** (solo `dialogue_revision 1`):
- ogni riferimento è valutato a parte e la proposta resta sospesa, con motivo non verificato e
  senza rilascio automatico;
- un riferimento non risolvibile sospende tutta la finestra;
- il rilascio richiede uno slot che governi la proposta, o la clausola della sua condizione.

Grounding, V14, K3, prompt e percorso legacy invariati. Preregistrazione alle 07:56:32 UTC
(SHA256 `042899fd…`), prima del codice.

**Verifiche offline:**
- 4/4 sintesi accettate con sospese e validazioni come previsto;
- minervino-B1 resta in PENDING per la finestra di revisione V12: errore di previsione
  dichiarato (addendum 2);
- 13 test di controesempio;
- replay di 247 sintesi: P3 cambia solo dove previsto; export finale identico nelle 12 prove
  riuscite; nessuna esportabile bloccata da K3/V14;
- suite 3.509 PASS, Ruff PASS.

**E2E** preregistrato (8 prove appaiate al braccio A di P3, dialogo P3 + generazione monolitica,
1,01 milioni di token):
- 7 DOCX su 8 (P3 A: 6/8), 0 sintesi respinte (P3 A: 2);
- CRAA 10/10 e 8/10; Cesano 3/4 e 3/4 (4/4 con date equivalenti); Catanzaro 13/31 e 8/31;
  Minervino 51/60 e un fallimento per troncamento della chiamata globale monolitica (49.152
  token), estraneo al narratore;
- 0 scritture non dimostrate (revisione dell'autore), V14 rispettato;
- 1 conferma ridondante (P3 A: 4).

Limiti:
- i percorsi nuovi non sono stati esercitati da risposte reali (16 sospensioni, tutte
  ancorate);
- campione piccolo; il 51/60 di Minervino dipende dall'output globale, non dalla correzione;
- il troncamento monolitico resta la prima causa di prove perse.

Decisione proposta: P3 disattivato nell'app live, candidata per la valutazione finale;
segmentazione da decidere a parte. Rapporto: docs/narratore-p3-2026-10-22.md.

## 22 ottobre 2026 — Strategia di generazione: criterio per le sezioni (offline)

Richiesta: dopo l'approvazione del dialogo P3 come candidata sperimentale, cercare un criterio
generale, oggettivo e misurabile per usare le sezioni solo con alto rischio di troncamento,
senza regole per fixture. Zero chiamate LLM, codice invariato.

Dati: 158 chiamate globali registrate, stessa configurazione (deepseek-flash, ragionamento basso,
limite 49.152, contratto 12); 132 monolitiche su 6 moduli reali, 26 segmenti.

**Criterio a priori** (posizioni del catalogo):
- spiega il 72% della varianza dell'output (circa 14.200 token + 88 per posizione);
- 0 troncamenti e massimo 66% del limite fino a 115 posizioni;
- però inverte il rischio dei due moduli grandi: 267 posizioni, previsto 77% e osservato 87% con
  5 troncamenti su 28; 307 posizioni, previsto 84% e osservato 71% con 0 su 19;
- non ci sono dati fra 115 e 267 posizioni;
- le sezioni costano da 3,9 a 5 volte i token, senza guadagno di copertura dimostrato.

Respinto.

**Criterio a posteriori** (`finish_reason = length`, poi sezioni una volta):
- oggettivo e senza soglia;
- costo atteso sul modulo a rischio di 169k token contro 98k (monolitico, 18% di sessioni perse) e
  382k (sezioni sempre attive);
- conviene fino a una probabilità di troncamento del 72%;
- portata limitata: un solo modulo osservato.

Esperimento proposto e non eseguito (3 sessioni con troncamento forzato da replay registrato,
circa 1,3 milioni di token).

Pool casuale di 8 bandi: 35-88 posizioni, nessuno a rischio.

Decisione proposta: valutazione finale con generazione monolitica e troncamenti dichiarati come
classe di fallimento separata. Limiti: 6 moduli, 2 grandi, un solo modello, mediane di costo su 2
sessioni per modalità. Rapporto: docs/strategia-generazione-2026-10-22.md.

## 22 ottobre 2026 — Valutazione finale del candidato (criteri v1)

Profilo: V14 + K3, dialogo P3 corretto (runtime sperimentale), generazione monolitica, sezioni
disattivate. Criteri di conclusione v1 invariati; preregistrazione congelata alle 10:53:06 UTC,
prima delle inferenze; codice invariato (hash controllati a ogni chiamata).

Moduli:
- 6 storici con riferimento congelato;
- il modulo nuovo So.Re.Sa. 2023, estratto con seme fisso dal pool dei bandi casuali;
- Cannara, estratto per primo, è fuori ambito: 0 destinazioni del nucleo riconosciute (spazi resi
  con tabulazioni).

SOURCE nuova: scheda tabellare DOCX→PDF con gli stessi 104 valori aziendali, in un runtime
separato. Riferimenti v3 conformi ai criteri: storici derivati senza cambiare valori, So.Re.Sa.
autoriale.

Campagna: 35 tentativi (5 per modulo), politica USER deterministica, nessuna sostituzione;
4,15 milioni di token, circa 0,92 USD stimati, mediana 125 s per tentativo.

| Modulo | DOCX | Copertura mediana |
|---|---|---|
| Minervino | 4/5 | 79% |
| Cesano | 4/5 | 100% |
| CRAA | 5/5 | 100% (CCIAA vuote, autorizzazione rinviata) |
| Catanzaro | 4/5 | 32% |
| Bella | 5/5 | 88% |
| Trapani | 5/5 | 94% |
| So.Re.Sa. | 5/5 | 47% |

Totale DOCX: 32/35 (91,4%).

Fallimenti:
- MODEL 2: JSON non valido;
- EXPORT 1: minervino-1, 409 per ricevuta SKIP del firmatario senza riallineamento dell'audit,
  fallimento sicuro;
- narratore 0, backend 0. Nessun troncamento; quota massima del limite 97%.

Scritture:
- 423 in 32 DOCX;
- 0 non dimostrate nella revisione autoriale e automatica;
- revisione indipendente non disponibile, quindi criterio di sicurezza non verificabile;
- pacchetto cieco di 124 scritture preparato.

Dialogo e vuoti:
- 19 conferme ridondanti;
- 2 interventi della guardia sui cicli;
- 0 sintesi respinte;
- vuoti con motivo tracciato 352/354;
- 0 warning di visibilità.

So.Re.Sa.: binding del sottoscrittore respinto perché il FORM chiede solo «in qualità di»; i dati
della scheda PDF sono stati scritti correttamente.

Esito sulle soglie:
- raggiunti DOCX e copertura su 5 moduli su 7;
- non raggiunti copertura (Catanzaro, So.Re.Sa.), dialogo e vuoti;
- sicurezza non verificabile in forma indipendente.

Candidato non adottato. Limiti: revisione autoriale, SOURCE sintetiche, un modello, 5 tentativi,
un solo modulo nuovo con effetti di modulo e SOURCE non separabili. Rapporto:
docs/valutazione-finale-2026-10-22.md.

## 22 ottobre 2026 — Sezioni resilienti e coerenza dello stato derivato

Due candidate opt-in, non adottate:
- `derivation_revision 1`: ricalcolo dell'audit derivato dopo ogni risposta USER;
- `generation_revision 2`: sezioni per unità di dipendenza, con validazione per segmento, retry
  limitati, merge con `budget_scale`, cache per digest e stati di applicabilità.

Piano congelato prima del codice, addendum prima delle inferenze, preregistrazione E2E congelata
(13:50 UTC).

Verifiche offline (zero LLM):
- replay deterministico di minervino-1: 409 senza flag, export riuscito con il flag;
- test di conferma, rinvio, revoca, cambio e slot differente;
- fallimento isolato di ogni segmento; JSON incompleto, strutture errate, budget e chiavi
  duplicate;
- condizione omessa:
  - caso riconoscibile rifiutato dal validatore V12;
  - V14 e predicato FORM CONDIZIONATA;
  - caso non riconoscibile documentato come rischio;
- condizioni condivise, conflitti, riuso dopo segmento fallito (Catanzaro-B1: due scritture
  sospese), interruzione, ripresa dalla cache, cache corrotta, richieste diverse;
- suite 3.560 PASS, Ruff PASS; 193/193 validazioni registrate e 247/247 sintesi identiche.

Campagna esplorativa (8 tentativi, sequenziale, budget di 3 M token): stessi scenari, politica
USER, SOURCE e riferimenti della valutazione finale.

| Modulo | DOCX | Copertura mediana | Non dimostrate (autore) |
|---|---|---|---|
| Minervino | 1/2 (narratore) | 90% | 7 |
| Catanzaro | 2/2 | 32% | 5 |
| Cesano | 2/2 | 88% | 0 |
| So.Re.Sa. | 2/2 | 37% | 13 |

Totali:
- 7/8 DOCX;
- 30/30 segmenti analizzati, 0 retry, 0 risposte 409;
- 1,85 M token, 0,37 USD;
- token dell'analisi 1,3-2,4× la monolitica (confronto non appaiato).

Le 25 scritture non dimostrate sono in rami non pertinenti, con il paragrafo di ramo assente dal
contesto del segmento:
- studio associato;
- sezione 5.c (società di professionisti);
- avvalimento;
- blocchi dei componenti RT.

Erano tutte VERIFICATA; la monolitica ne aveva 0 su 423.

Esito: **non pronta** (criterio preregistrato (a)). La correzione del 409 è dimostrata e separabile.

Limiti:
- revisione autoriale, non indipendente;
- n = 8;
- nessun fallimento di segmento osservato nell'E2E, quindi resilienza e ripresa verificate solo
  offline.

Rapporto: docs/sezioni-resilienti-2026-10-22.md.

## 22 ottobre 2026 — Passo 1: promozione separata dello stato derivato

Dopo la revisione indipendente dei risultati, l'utente ha autorizzato di
procedere per passi. Promosso soltanto `derivation_revision=1` per le nuove
sessioni; V14 e K3 conservati, dialogo P3 e sezioni ancora opt-in. La logica
applicativa cambia esclusivamente in `initial_state`; ricalcolo e veto finale
già implementati da Opus restano identici.

Le sessioni persistite non vengono migrate. Il valore esplicito
`MAPI_DERIVATION_REVISION=0` permette di creare sessioni col profilo precedente.
I test verificano anche che un cambio dell'impostazione non alteri le revisioni
di una sessione già salvata.

Verifiche effettivamente eseguite, provider simulati e rete bloccata:

- 39 test mirati prima della modifica, PASS;
- 72 test mirati dopo la promozione, PASS;
- prima suite completa: 3.562 PASS e 2 FAIL nella stessa fixture FTS5/Qdrant;
- la fixture modificava solo la disposition nell'audit e non la risposta MODEL
  immutabile, che il nuovo ricalcolo ripristina. Corretta la preparazione facendo
  restituire clarifications al provider simulato; asserzioni sulla risposta
  parziale USER e sul campo ambiguo rimasto aperto invariate;
- 76 test del dialogo/derivazione dopo la correzione della fixture, PASS;
- **suite backend finale: 3.564 PASS in 309,90 s; Ruff completo PASS**.

I tentativi iniziali nel sandbox si sono bloccati nei worker AnyIO; riproduzione
anche con un programma minimo. Esecuzione fuori sandbox autorizzata, mantenendo
nel runner connessioni vietate, dotenv disabilitato e DB/storage temporanei.
Conservati anche i log falliti, incluso un iniziale errore del duplicatore
dell'output corretto prima dei test.

Nessuna chiamata LLM reale, token o costo di inferenza; nessuna campagna E2E,
migrazione, reindicizzazione, modifica dei risultati congelati, commit o push.
Il replay HTTP storico di minervino-1 non è stato rieseguito: non viene contato
fra le nuove verifiche. Questi risultati riguardano il software, non una nuova
misura della qualità del modello.

Rapporto: `docs/compilazione-passo1-stato-derivato-2026-10-22.md`.
Grezzo, patch del passo e copie verificate:
`backend/data/compilation-audit/stato-derivato-passo1-20261022-01/`.
Backup separato da Git:
`backend/data/compilation-audit/stato-derivato-passo1-backup-20261022.tar.gz`.

Restano da affrontare nei passi successivi il contesto FORM delle sezioni,
l'ambito delle decisioni USER e il recupero del narratore. La candidata a
sezioni rev 2 rimane non adottata e le sue scritture non dimostrate non sono
risolte da questa promozione.

## 23 ottobre 2026 — passo 2: contesto FORM e ambito USER, rev 3 non adottata

Su autorizzazione dell'utente, implementata la candidata `generation_revision=3`:
FORM completo in lettura, responsabilità locale dell'output, partizione/cache/
ripresa rev 2 riusate. Rimosse nella sola rev 3 le unificazioni di condizioni
che ignoravano differenze di significato e ampliavano gli scope; resta la
deduplica esatta. Nessuna riscrittura di parser, writer, retrieval o contratto V12.

Il controllo USER già esistente richiede nella candidata un esito separato
sull'ambito effettivo, leggendo FORM e destinazioni complete. Ricevute interne
legano risposta, campi e condizioni; export e rivalidazione rifiutano ricevute
mancanti/obsolete e condizioni false. Un valore USER può sostenere una catena
indipendente verificata, senza autorizzare il riuso SOURCE di un segmento fallito.

Verifiche offline autoriali, con provider simulati, rete bloccata, dotenv
disabilitato e archivi temporanei:

- prima esecuzione mirata: 118 PASS / 3 FAIL, risolti correggendo due preparazioni
  della nuova fixture e un ID errato nel test del reperto So.Re.Sa.; reperto intatto;
- 32 PASS sul nuovo modulo; 74 PASS sul percorso USER e guard precedente;
- prima suite completa: 3.603 PASS in 318,00 s;
- due controesempi finali fallenti (ordine del prefisso e condizione divenuta falsa),
  poi corretti; tutti i log conservati;
- **suite finale: 3.605 PASS in 327,91 s; Ruff completo PASS**.

Verificati gli input congelati dei quattro moduli e il rifiuto controfattuale,
solo in memoria, della vecchia ricevuta ampia So.Re.Sa. Nessuna inferenza reale:
questo non dimostra la correzione semantica del nuovo modello né la scomparsa
delle 25 scritture della rev 2. Il test della condizione FORM non riconosciuta
resta un limite riproducibile.

Confronto statico: input JSON più grandi, 1,21–2,09× in caratteri rispetto alla
rev 2 nei quattro casi; non sono token o costi. Il FORM condiviso precede il
contenuto locale per consentire il riuso del prefisso; cache effettiva, token,
latenza e qualità non misurati. Cambi agli input possono invalidare tutti i
segmenti; nessuna nuova cache semantica o orchestrazione generale.

Profilo ordinario invariato rispetto al passo 1; rev 3 non attivata. Baseline,
sessioni e risultati precedenti preservati. Nessuna campagna E2E, migrazione,
reindicizzazione, commit, tag o push. Il prossimo passo distinto riguarda il
recupero limitato del narratore, prima di un'eventuale verifica reale separata.

Rapporto: `docs/compilazione-passo2-contesto-2026-10-22.md`.
Audit: `backend/data/compilation-audit/contesto-sezioni-passo2-20261022-01/`.
Backup del passo, verificato file per file e separato da Git:
`backend/data/compilation-audit/contesto-sezioni-passo2-backup-20261023.tar.gz`.

## 23 ottobre 2026 — passo 3: recupero limitato del narratore, non adottato

Su autorizzazione dell'utente, aggiunto il flag persistito separato
`narration_recovery_revision=1` (`MAPI_NARRATION_RECOVERY_REVISION=1` solo per
nuove sessioni). Non attivato nel runtime ordinario. Le sessioni senza flag
mantengono il comportamento precedente, indipendentemente dalla rev 3.

Il narratore conserva il tentativo esistente e aggiunge, nel solo profilo
sperimentale, un retry sullo stesso input. Dopo due fallimenti il backend offre
una bozza parziale esplicita: revisioni ancora valide e hold precedenti conservati,
nessuna promozione di proposte non revisionate. Può risultare una copia vuota.
Un «riprendi» avvia di nuovo soltanto la sintesi. Lease adeguate ai due tentativi,
consumi e artefatti separati; nessuna metrica mancante interpretata come zero.
Restano V14/K3, ambito USER, rivalidazione e originali; un ulteriore veto protegge
l'API dalle forzature di proposte SOURCE non revisionate durante il fallback.

Prove offline, provider simulati, connessioni bloccate e DB/storage temporanei:

- 121 PASS nei test mirati del recupero/dialogo/hold P3;
- 33 PASS nei casi del recupero, poi 2 PASS aggiuntivi sul consenso V14;
- **suite completa finale: 3.640 PASS in 353,53 s; Ruff completo PASS**.

Riprodotta la risposta registrata di minervino-2 con hold_groups vuoti e finestra
senza proposte. Controprova sullo stato storico originale solo in memoria:
conservate 63 revisioni, 15 sospensioni e quattro risposte; il filtro torna a
selezionare 48 SOURCE + 1 USER nel vecchio profilo. Non è stato generato un nuovo
DOCX da questo stato né giudicata la correttezza semantica delle scritture; non
modifica il 7/8 congelato e non è una prova dell'intera candidata rev 3.
Nel caso simulato con 45 proposte, il fallimento della seconda finestra preserva
le 40 revisioni precedenti ed esclude le cinque rimaste; la forzatura via API dà
409. Verificati export chat esplicito, ripresa senza nuova analisi, cancellazione,
ricevute obsolete, USER non autorizzato e permanenza del veto V14.

Nessuna inferenza reale o nuova E2E; nessuna migrazione/reindicizzazione, commit,
tag o push. Rimangono i limiti semantici, le 25 scritture rev 2 non dimostrate
risolte e la copertura insufficiente. Candidata non adottata. Prossimo passo:
verifica reale contenuta e preregistrata dei tre interventi insieme.
Questa verifica è autoriale, non indipendente.

Rapporto: `docs/compilazione-passo3-narratore-2026-10-23.md`.
Audit: `backend/data/compilation-audit/recupero-narratore-passo3-20261023-01/`.
Backup verificato del passo, separato da Git:
`backend/data/compilation-audit/recupero-narratore-passo3-backup-20261023.tar.gz`.

## 23 ottobre 2026 — Candidata completa: campagna esplorativa arrestata

Profilo:
- V14 + K3;
- stato derivato (predefinito);
- dialogo P3;
- `generation_revision 3` (FORM completo nei segmenti, controllo d'ambito USER);
- recupero del narratore.

Stessi scenari, politica USER, SOURCE e riferimenti v3 della valutazione finale. Preparazione di
Astra; ripresa con l'addendum 2 (harness ricongelato, Cesano in fondo) prima delle inferenze.

| Tentativo | DOCX | Scritture (non dimostrate) | Rami sbagliati della rev 2 | Copertura | Token |
|---|---|---|---|---|---|
| minervino-1 | sì | 39 (0) | `p37.*` vuoti | 65% | 484k |
| catanzaro-1 | sì | 11 (0) | `t19.*` vuoti | 35% | 537k |
| soresa2023-1 | no | 0 | nessuna proposta in `p127`/`p43`/`p44` | — | 163k |

- **Arresto** per la regola preregistrata «difetto grave del nuovo backend»: la verifica d'ambito
  della guardia rev 3 respinge output per `rationale` oltre 250 caratteri.
  - 3 rifiuti su 7, di cui 2 conferme corrette in So.Re.Sa.;
  - risposta USER non applicata, timeout del driver.
- **Non avviati:** cinque tentativi.
- **Totali:** 1,18 M token, circa 0,18 USD.
- **Esecuzione:** 13/13 segmenti, 0 retry, 0 risposte 409, 0 errori del narratore.

Indicazione favorevole sull'ipotesi del FORM completo, non una prova: 2 DOCX, revisione autoriale,
So.Re.Sa. senza scritture.

Rapporto: docs/candidata-completa-2026-10-23.md.

## 23 ottobre 2026 — Correzione della guardia rev 3 (offline)

Difetto emerso dalla campagna arrestata: la verifica d'ambito rev 3 respingeva output corretti per
una `rationale` oltre 250 caratteri. Correzione autorizzata e limitata a `FormScopeCheck`: limite a
1000 caratteri, altri vincoli invariati, guardia ordinaria invariata.

Prove:
- 9 nuovi test:
  - motivazioni registrate con la loro decisione;
  - rifiuti attesi (oltre 1000 caratteri, esito sconosciuto, campo extra, slot errato);
  - limite ordinario;
  - schema.
- Prova di sensibilità sulla versione precedente: falliscono solo i casi reali.
- Rivalidazione delle 7 verifiche registrate: tutte valide, decisioni precedenti invariate.
- Suite 3.649 PASS, Ruff PASS.

Nessuna inferenza: non dimostra la qualità della guardia né l'assenza di scritture nei rami
sbagliati; serve una nuova campagna. Rapporto: docs/correzione-guardia-rev3-2026-10-23.md.

## 23 ottobre 2026 — Candidata corretta: campagna preregistrata (6 tentativi)

Opzione A scelta dall'utente: due tentativi ciascuno su Minervino, Catanzaro e So.Re.Sa.; tetto
vincolante di 2,8 M token. Candidata rev 3 completa con la guardia corretta (motivazione fino a 1000
caratteri). La campagna arrestata resta separata.

Prima delle inferenze:
- **Contesto:** il paragrafo di ramo dei 25 controesempi è presente nell'input rev 3 in 25 casi su
  25 (rev 2: 0).
- **Rigioco deterministico** delle uscite rev 2: 19 scritture sbagliate senza condizioni
  passerebbero comunque i controlli, se il modello le riproponesse.
- **Preservazione:** 103/103 scritture corrette preservate con la guardia confermante, Cesano
  compreso.
- **Test:** 28 sulle motivazioni lunghe; suite 3.677 PASS.

| Tentativo | DOCX | Scritture (non dimostrate) | Copertura | Token |
|---|---|---|---|---|
| soresa2023-1 | sì | 8 (0) | 47% | 197k |
| minervino-1 | sì | 56 (0) | 93% | 388k |
| catanzaro-1 | sì | 22 (0) | 45% | 651k |
| soresa2023-2 | sì | 8 (0) | 47% | 171k |
| minervino-2 | sì | 30 (0) | 50% | 571k |
| catanzaro-2 | sì | 18 (0) | 32% | 592k |

- **Rami sbagliati della rev 2:** 0 scritture e 0 proposte (rev 2: 25).
- **Esecuzione:**
  - 2 segmenti recuperati con il retry (JSON non valido);
  - 0 risposte 409, 0 errori del narratore, 0 verifiche respinte;
  - 2 conflitti in revisione;
  - 7 conferme ridondanti.
- **Costi:** 2,57 M token, circa 0,40 USD; 2-4,4 volte la monolitica in token, circa 1,65 volte in
  tempo.
- **Esito preregistrato:** favorevole.

Limiti:
- revisione autoriale;
- n = 6;
- sicurezza osservata, non deterministica;
- narratore troppo prudente in minervino-2 (blocco incompleto);
- copertura bassa su Catanzaro e So.Re.Sa.

Rapporto: docs/candidata-corretta-2026-10-23.md.

## 23 ottobre 2026 — Sprint offline sulla compilazione per sezioni (rev 3)

Nessuna chiamata LLM: rigiochi deterministici delle uscite registrate e test con provider
simulato. Rapporto: `docs/sprint-sezioni-2026-10-23.md`. Grezzi e strumenti:
`backend/data/compilation-audit/sprint-sezioni-20261023-01/`.

- **Passo 1, R1** (`rigioco_r1.py`, `valuta_r1.py`):
  - 25 scritture sbagliate rev 2, tutte accertate; R1 chiude le 7 di Minervino (`p37.*`);
  - 245/245 corrette preservate con la guardia simulata, 718 scritture corrette di quattro
    campagne non toccate;
  - **Alternativa scartata, casella spuntata obbligatoria:** 116 falsi rifiuti.
  - **Limite:** le altre 18 richiedono la semantica delle sezioni.
- **Passo 2, sospensioni** (`sospensioni_passo2.py`, `rigioco_passo2.py`):
  - le 21 di minervino-2 sono non fondate: citano la clausola del direttore tecnico, che governa
    altre destinazioni;
  - il criterio M le isola fra 145, senza falsi positivi;
  - **Rigioco controfattuale:** export +21 solo se il narratore non le risospende.
  - **Limite:** l'esito reale non è misurato.
- **Passo 3, ripresa:** 10 scenari deterministici.
  - **Difetto trovato:** bozza esplicita con una proposta sospesa accettata (200). Corretto in
    rev 3, il profilo ordinario è invariato e il difetto vi è segnalato.
- **Verifiche complessive:**
  - suite 3.740 PASS, Ruff PASS;
  - codice base e sprint identici su 79 stati salvati;
  - V14 e K3 185/185 con entrambi i profili;
  - originali DOCX 17/17.
- **Limiti delle misure:**
  - revisione autoriale non indipendente;
  - rigiochi che non riproducono il modello;
  - la sicurezza dei rami resta empirica per 18 casi.

## 23 ottobre 2026 — Campagna E2E dopo lo sprint (6 tentativi, approvata dall'utente)

- **Preregistrazione:** `PREREG-SPRINT-E2E.md` con addendum, congelata alle 17:27:05 UTC:
  - il criterio d'arresto è una scrittura non dimostrata o con applicabilità errata, non la sola
    presenza di una delle 25 destinazioni;
  - spiegazione di 19/25 e 12/18.
- **Esito:** favorevole.
  - 6/6 DOCX, 139 scritture, 0 non dimostrate, 0 aggiramenti, 0 rami sbagliati;
  - 2,56 M token, circa 0,38 USD.
- **Revisione mirata delle sospensioni:** non esercitata (0 casi M).
- **Falsi rifiuti del narratore fuori dal criterio:** 14 campi.
- **Risultati:** `benchmark ufficiale/sprint-e2e-20261023-01/`; rapporto
  `docs/campagna-e2e-sprint-2026-10-23.md`.
- **Correzione ordinaria della bozza esplicita:** separata, `fix/2026-10-23-bozza-esplicita`;
  suite 3.687 PASS; 151 esportazioni storiche verificate, 0 rifiuti.
- **Limiti:**
  - revisione non indipendente;
  - n = 6;
  - confronto descrittivo e non appaiato.


## 23 ottobre 2026 — Integrazione incrementale offline dell’hotfix API

Worktree dedicato `tesi-docx-offline`, base `ff0d4f9`. Riutilizzato il commit
`4890daa`, senza riscrivere il fix. Riproduzione prima: 8 FAIL / 2 PASS; dopo:
62 test mirati PASS. Preservate 157 esportazioni storiche e 245 scritture corrette
nel replay con condizioni soddisfatte. Suite completa 3747 PASS + 3 casi storici PASS separati; Ruff PASS.
Commit `4554ae1`; rollback verificato, albero identico alla base dello sprint.
Nessuna inferenza o adozione. Dettagli in `docs/docx-incrementale-2026-10-23.md`.

## 24 ottobre 2026 — Applicabilità delle tabelle, verifica offline conclusa

Regola strutturale opt-in: intestazione condizionale esplicita in tabella non
editabile e tabella dati immediatamente seguente. Non inventa condizioni; se la
condizione manca, SOURCE e USER restano bloccati. Cinque errori storici aggiuntivi
bloccati, 245/245 scritture corrette preservate alle stesse condizioni.
Prima: 2 FAIL/2 PASS nella riproduzione; dopo: suite 3775 PASS e Ruff PASS.
Restano 13 controesempi non chiusi deterministicamente. Nessuna inferenza o
adozione live. Dettagli in `docs/docx-incrementale-2026-10-23.md`.

## 24 ottobre 2026 — Rilettura mirata dei dubbi SOURCE, offline

Inventario di 143 hold attivi, 90 SOURCE. Nei dati dello sprint, 6 campi soci e
8 tecnici di Minervino hanno prove di ruolo già collegate che meritano una sola
rilettura del narratore. Il FORM esaminato chiede il ruolo aziendale, senza la
nuova designazione per la gara ipotizzata nel dubbio. Il conflitto sul firmatario
e 9 hold di applicabilità Catanzaro/So.Re.Sa. restano esclusi.
Nuovo flag `MAPI_HOLD_REREVIEW_REVISION=2`, solo rev 3: nessun rilascio backend,
seconda sospensione definitiva, invalidazione delle prove cambiate. Prima:
2 FAIL/2 PASS; 123 test mirati dopo PASS. Rigioco delle due risposte simulate:
14 rilasci se il narratore li approva, zero se conferma il dubbio. Non sono
recuperi misurati con un modello reale. Suite completa 3796 PASS, Ruff PASS;
21 test della rilettura ripetuti con fixture indipendente dalla priorità 2.

## 24 ottobre 2026 — Ripresa e chiusura delle verifiche incrementali

I meccanismi esistenti superano i dieci scenari su profilo sprint e nuovo profilo:
46 PASS. Nessuna modifica applicativa per la ripresa. Suite finale 3819 PASS,
Ruff PASS. Limite dichiarato: ogni nuovo contesto SOURCE/USER invalida tutti i
digest dei segmenti alla successiva analisi; le scritture dopo revoca restano
invece bloccate per dipendenza. Guasti e provider sono simulati, non E2E reali.

Fix API `4554ae1`, tabelle `480e7e5`, narratore `3ec0af0`, ciascuno con
rollback al comportamento precedente e verifica selettiva degli altri fix.
Nella rimozione del fix tabelle dopo quello narratore serve preservare le due
righe del flag hold rev 2 nel conflitto locale di `initial_state`.
Tutte le 245 scritture corrette del replay con condizioni soddisfatte sono
preservate; errori storici chiusi 7 → 12 su 25. Quattordici sospensioni SOURCE
riesaminabili non equivalgono a quattordici recuperi già dimostrati dal modello.

Rapporto `docs/docx-incrementale-2026-10-23.md`; proposta E2E separata
`docs/proposta-e2e-incrementale-2026-10-24.md`, non avviata e da autorizzare.
Branch sperimentale pubblicabile dopo controllo; nessun merge o adozione live.

## 24 ottobre 2026 — Campagna E2E della candidata incrementale (6 tentativi, autorizzata)

- **Preregistrazione:** `PREREG-INCREMENTALE-E2E.md`, congelata alle 10:37 UTC.
- **Ordine:** catanzaro-1, minervino-1, soresa2023-1, cesano-1, catanzaro-2, minervino-2; con
  interruzione programmata in minervino-2.
- **Esiti:**
  - 5/6 DOCX: minervino-1 è un fallimento DRIVER, frontend spento, 0 chiamate, non ripetuto;
  - 101 scritture DIMOSTRATA, 0 dubbie, 0 indebite;
  - 0 rami sbagliati, 0 aggiramenti;
  - 1,96 M token, circa 0,31 USD.
- **Effetti delle correzioni dal vivo:**
  - controllo delle tabelle non esercitato, nessuna proposta 5.c;
  - riesame SOURCE non esercitato, 0 recuperi;
  - ripresa riuscita, con cache del segmento 1 e 4 segmenti chiamati.
- **Omissioni:**
  - So.Re.Sa.: le stesse sospensioni non fondate sulla partecipazione singola;
  - Minervino: 2 campi rinviati dall'USER.
- **Limiti:**
  - revisione non indipendente; n = 6;
  - attesa del lease di circa 25 minuti dopo un crash.
- **Rapporto:** `docs/campagna-e2e-incrementale-2026-10-24.md`.

## 24 ottobre 2026 — Compilazione DOCX per sezioni come sistema predefinito (integrazione)

- **Decisione:** dell'utente. Nessuna inferenza e nessuna nuova campagna: verifiche
  deterministiche e con provider simulati.
- **Profilo:**
  - `compilation_profile.py`, `SECTIONS`: backend 13, V14, K3, derivazione 1, dialogo 1,
    generazione 3, recupero del narratore 1, R1, tabelle 1, riesame 2;
  - interruttore di emergenza `MAPI_COMPILATION_PROFILE=storico`, uguale alle regole precedenti.
- **Commit:**
  - `6d7477c`, `0933353`, `dc640fc`;
  - suite 3860 PASS, frontend 152 PASS;
  - E2E simulati 18/18 più 4/4.
- **Rigioco dei 25 controesempi** con il codice integrato:
  - errori esportabili 13 con guardia simulata (7 con le sole ricevute registrate);
  - corrette conservate 245/245;
  - 0 nuovi falsi rifiuti.
- **Confronti:**
  - 162 esportazioni storiche, 0 rifiuti;
  - 90 stati con esiti identici alla candidata `3ec0af0`.
- **Processo reale:**
  - la sessione creata via API senza analisi ha i flag `SECTIONS`;
  - 29 sessioni e 273 file archiviati invariati.
- **Limiti:** l'accuratezza semantica non è stata misurata qui; restano validi gli esiti e i
  limiti della campagna incrementale (n = 6, revisione non indipendente).
- **Rapporto:** `docs/integrazione-compilazione-sezioni-2026-10-24.md`.

## 24 ottobre 2026 — Micro-test E2E della Compilazione DOCX predefinita (Cesano, 1 tentativo)

- **Configurazione:**
  - app ordinaria (codice `dc640fc`), scenario e SOURCE di cesano-1 invariati;
  - DeepSeek `deepseek-flash`, tetto di 300.000 token;
  - harness congelato prima delle chiamate.
- **Esito:**
  - DOCX scaricato e identico all'archiviato;
  - 4/4 valori testuali visibili nel PDF.
- **Scritture:**
  - 5 positive e 5 deselezioni di effetto, tutte DIMOSTRATA;
  - 0 dubbie, 0 indebite.
- **Rispetto a cesano-1:**
  - stesso nucleo 4/4, in più la checkbox «Società di Ingegneria» attesa dal riferimento;
  - 163.006 token contro 175.331, 189 s contro 197 s;
  - richieste di segmento identiche.
- **Limiti:**
  - n = 1, revisione non indipendente;
  - R1, tabelle, riesame e ripresa non esercitati;
  - «Preparazione del DOCX…» non visibile.
- **Rapporto:** `docs/microtest-e2e-predefinito-2026-10-24.md`.

## 25 ottobre 2026 — opzioni FORM e dati del ramo, verifica offline

- Richiesta: partire dai tredici errori residui e correggere soltanto dipendenze
  dimostrabili, preservando le 245 scritture corrette. Base attuale `9cb3129`.
- Preregistrazione: `docs/piano-ambiti-form-2026-10-25.md`, copia/hash nei grezzi
  prima della modifica. Nessuna nuova chiamata LLM o compilazione E2E.
- Diagnosi: sette casi nei dati dell'ausiliaria introdotti da opzione ASCII e
  `OPPURE`; sei nei blocchi ripetuti dei componenti RT. Nel JSON la condizione
  locale è omessa o sostituita da una condizione di partecipazione con scope misto.
- Fix `ddb8cb764bcb8dece4a43f80499b4933e759ed08`, isolato con flag persistito:
  opzione locale riconosciuta senza condizione propria -> NON_ACCERTATA; una
  risposta estranea non autorizza; condizione valida e conferma pertinente
  consentono l'export positivo. Nessuna classificazione semantica generale.
- Prima: 2 FAIL / 2 PASS, HTTP 200 errato. Dopo: 38 test nuovi PASS; replay
  residui 13 -> 6 (ricevute simulate) / 7 -> 4 (registrate), positive 245 -> 245
  / 211 -> 211. Sei casi RT lasciati aperti, nessuna regola specifica per bando.
- Suite 3898 PASS, Ruff PASS; 26 controesempi K3 con output identico alla base.
  Le prove misurano il software e i gate su output registrati, non nuova qualità
  LLM; revisione autoriale, non indipendente.
- Rollback `c16d2a3` verificato in un worktree separato: albero identico alla base
  e ritorno degli stessi 2 FAIL / 2 PASS. Conservato anche l'errore iniziale di
  import della sonda esterna, poi collocata correttamente nel percorso test.
- App ordinaria, V12, benchmark e 29 sessioni live invariati; nessuna adozione.
  Rapporto `docs/ambiti-form-2026-10-25.md`; audit locale
  `backend/data/compilation-audit/ambiti-form-20261025-01/`, backup separato
  `…/ambiti-form-backup-20261025/`. Due E2E futuri soltanto proposti nel rapporto.

## 25 ottobre 2026 — Istruzioni condizionali del FORM, revisione 2 (offline, autorizzata)

- **Obiettivo:** i sei controesempi residui dopo `ddb8cb7`, tutti So.Re.Sa., cioè dati
  dell'impresa singola nelle schede dei componenti RT governate dal paragrafo 19 «(da compilare
  nel caso di … RT … non ancora costituito)».
- **Metodo:** inventario strutturale e preregistrazione prima del codice; rigioco degli output
  registrati; zero inferenze.
- **Arresto preregistrato:** con la citazione intera la regola perdeva 7 corrette. Le cause:
  - 5 per una citazione del paragrafo 7 senza la coda normativa;
  - 2 `p31.s0` USER in una scheda RT.

  Misurate offline A2 e A3; l'utente ha scelto A2.
- **Esito con A2:**
  - insieme congelato: errori 0/25 (simulati) e 0/25 (registrati), corrette 243/245;
  - positive estese: 236/240, come la base;
  - K3 identico; suite 3937 PASS.
- **Discrepanza:** i 2 `p31.s0` sono giudicati DIMOSTRATA nella revisione storica e ritenuti
  dati nel ramo sbagliato da Claude (giudizio non indipendente). Il benchmark non è modificato.
- **Limiti:** grassetto e marcatore letterale; rischio di omissione non misurato dal vivo.
- **Rapporto:** `docs/istruzioni-form-2026-10-25.md`.

## 25 ottobre 2026 — Adozione della protezione dei rami FORM e prova E2E reale (2 tentativi)

- **Adozione:** profilo predefinito `sezioni-2026-10-25` (commit `a152d7f`), integrato nell'app
  ordinaria e verificato sul processo reale senza LLM.
- **Prova:**
  - preregistrata, con harness congelato;
  - runtime isolati clonati dai seed, DeepSeek `deepseek-flash`;
  - tetto 750.000 token, consumati 247.443.
- **soresa2023-rami-1** (scenario e politica della campagna incrementale):
  - DOCX, 7/7 DIMOSTRATA, nucleo v3 7/15;
  - 4 proposte RT nel ramo sbagliato non scritte; il modello le aveva già legate alla
    condizione RT.
- **sintetico-rami-1** (FORM sintetico con RT e avvalimento):
  - DOCX, riferimento 8/8;
  - trappola della scheda singola vuota; 0 falsi rifiuti.
- **Osservazioni:**
  - le citazioni delle condizioni erano intere, quindi la regola A2 non è servita;
  - render PDF del sintetico completato con le funzioni del renderer congelato (DOCX di una
    pagina).
- **Limiti:** n = 2, revisione non indipendente; veto della protezione mai determinante dal
  vivo.
- **Rapporto:** `docs/rami-e2e-2026-10-25.md`.
