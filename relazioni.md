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
