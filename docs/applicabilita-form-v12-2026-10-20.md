# V12: vincoli locali di applicabilità delle destinazioni FORM

**Esito applicabilità: PASS circoscritto**, dimostrato sui due output originali
e in una nuova sessione UI reale che ripete l'omissione del modello.
Intervento circoscritto al difetto Catanzaro, successivo allo studio B0/E1/E2-A.
Gli esperimenti congelati restano intatti; E1 ed E2-A non sono integrati.
Il rapporto distingue implementazione, replay e prova reale.

## Causa riprodotta

Le due risposte originali `catanzaro/B0/rep-3` e `catanzaro/E1/rep-3` propongono
`t0.r8.c1` con `conditions=[]`, citando soltanto «Sede operativa» in `paragraph:34`.
Il valore dell'indirizzo è letteralmente documentato per la società nelle SOURCE.
`paragraph:35` contiene «(se diversa dalla sede legale)»: è nella **stessa cella
etichetta `t0.r8.c0`**, mentre `t0.r8.c1` è la cella del valore della medesima riga.
Entrambi i paragrafi sono già presenti fra le ancore locali del catalogo B0.

Il validatore originale calcola soltanto le condizioni emesse o collegate dal
modello. La proposta senza riferimenti non incontra un predicato da verificare;
la selezione e il narratore la lasciano passare. Il writer esegue fedelmente la
destinazione selezionata. Non manca l'indirizzo né il contesto nel FORM: manca
un controllo indipendente dell'uso consentito di quel valore.

Le SOURCE `-43/-44`, stesso documento/soggetto, riportano sede legale e operativa
con lo stesso indirizzo; `-44` attesta anche la coincidenza. Il nuovo controllo
dimostra la coincidenza tramite le due asserzioni nominative con valori uguali,
senza chiedere al modello una nuova interpretazione della frase di rapporto.
Un fatto SOURCE vero resta distinto dall'applicabilità della destinazione.

Baseline di questa sessione: HEAD `99ab052` con modifiche locali, snapshot per
contenuto, 2.905 test PASS in 234,42 s; 36 esperimenti riprodotti con 72 audit e
36 DOCX esatti. I due test permanenti iniziali falliscono: **2 FAIL, 2 PASS**.

## Implementazione

Nuovo [compilation_form_applicability.py](../backend/app/compilation_form_applicability.py):
riconosce comparazioni locali esplicite di uguaglianza/diversità, con negazioni,
fra etichette del FORM. Usa clausole con marker fisico o righe etichetta/valore
a due celle, compresi più paragrafi nella cella etichetta. Un ramo «altrimenti»
può essere il complemento della clausola immediatamente precedente dello stesso
paragrafo; un genitore assente o ambiguo rimane UNKNOWN. Non cerca nomi di bandi,
ID specifici, indirizzi o denominazioni aziendali nel codice produttivo.

Le proprietà confrontate derivano dalle etichette FORM, non da `label`, `property`
o `conditions` proposte dal modello. Le asserzioni SOURCE ammesse devono nominare
esplicitamente lo stesso soggetto del fatto grounded. Valori letterali uguali
dimostrano coincidenza. Stringhe differenti da sole **non** dimostrano diversità:
abbreviazioni e granularità diverse potrebbero indicare lo stesso dato. La
diversità richiede una relazione SOURCE esplicita attribuita al medesimo soggetto.
Negazioni, ipotesi/esempi locali, conflitti e prove insufficienti non producono
un'approvazione. Una struttura locale riconosciuta ma ambigua resta UNKNOWN.

L'audit aggiunge una dimensione separata `form_applicability`, con esito
`true/false/unknown`, predicato, ancore FORM, soggetto, prove SOURCE e motivazione
deterministica. Non riscrive fatti, proposta grezza, condizioni MODEL, binding,
provenienza o ricevute USER. Non promuove `GROUNDED_PROPOSAL` a `RESOLVED`.

Integrazioni soltanto in:

- [compilation_global.py](../backend/app/compilation_global.py): calcolo indipendente
  dopo il grounding V12, sul catalogo originale e sul corpus autorizzato.
- [compilation_global_sessions.py](../backend/app/compilation_global_sessions.py):
  vista pubblica e veto nella selezione API; rilettura delle fonti e nuovo veto
  prima dell'export, anche per valori USER e in presenza di un verdetto salvato
  obsoleto. La verifica atomica esistente richiama la stessa selezione.
- [compilation_global_dialogue.py](../backend/app/compilation_global_dialogue.py):
  filtro di selezione conversazionale e verifica dei valori USER.

Il veto richiede TRUE. FALSE e UNKNOWN restano distinti e impediscono la
scrittura. Una conferma di export, una revisione del narratore, un valore USER
o una condizione MODEL non sostituiscono la prova del nuovo predicato.
Il consenso procedurale USER resta un controllo distinto anche quando il
predicato FORM è TRUE. Nessun nuovo percorso di attestazione USER è introdotto.

FORM inviato al modello, prompt, schema MODEL, modello, provider, parametri,
architettura globale, grounding, attribuzione, parser, writer, richieste API e database
rimangono invariati; la vista pubblica aggiunge il metadato del controllo.
Le vecchie versioni continuano a essere lette; nessun
upgrade persistito. Le vecchie sessioni V12 prive del nuovo controllo conservano
lo stato, ma le destinazioni comparative interessate non sono autorizzate senza
una nuova analisi esplicita/nuova sessione. Nessuna migrazione o reindicizzazione.

## Verifica deterministica

Fixture permanente con originali/hash e due risposte integrali in
[form-applicability-v1](../backend/tests/fixtures/form-applicability-v1/README.md).
Test in [test_compilation_form_applicability.py](../backend/tests/test_compilation_form_applicability.py)
e [test_compilation_form_applicability_session.py](../backend/tests/test_compilation_form_applicability_session.py).

91 nuovi casi: i due controesempi esatti; TRUE/FALSE/UNKNOWN; condizioni prima e
dopo il marker; etichette in più paragrafi/tabella e identificatori diversi;
negazioni FORM/SOURCE; etichette estranee al dominio sedi; soggetto diverso;
operandi mancanti, valori differenti, conflitti e contesti ipotetici; comparazioni
non analizzabili e merge ambigui; rami alternativi e «altrimenti»; isolamento
fra righe/tabelle/paragrafi; grounding rifiutato anche con predicato TRUE;
consenso separato; sessioni V12 pregresse; cache incompleta e selezioni obsolete.
Quattordici casi esercitano persistenza ed export API con FTS5/Qdrant isolati e
trasporto provider simulato: sono test software, non valutazioni di risposte AI.

Prima regressione completa: **13 FAIL e 2.980 PASS**, tutti i fallimenti nei
test esistenti delle finestre di revisione, per accesso obbligatorio a `type`
in cataloghi ridotti. Corretto nel nuovo controllo, senza modificare quei test;
il veto registrato resta efficace anche con una cache incompleta. 107 test
mirati PASS in 14,57 s (91 nuovi più 16 preesistenti); Ruff PASS.
I log dei tentativi intermedi e degli errori delle fixture/harness sono conservati.

Regressione completa finale: **2.996 PASS in 281,80 s**, Ruff PASS. La suite
frontend e la build non sono ripetute: nessun frontend è stato modificato;
il percorso UI reale è verificato separatamente sotto.

## Confronto prima/dopo e regressione dei benchmark

Stessi output MODEL, SOURCE, originali, condizioni e revisioni salvate; nessuna
nuova inferenza o ricevuta costruita. Replay separati, con rete e SQLite vietati.
67 casi: 36 dello studio; 20 storici in due contesti registrati; tre precedenti
prove reali Trapani/CRAA; otto checkpoint storici dello studio. Sono ricostruzioni
con ripetizioni di contesto, non 67 campioni indipendenti di qualità.

| Caso originale | Prima | Dopo | Destinazione `t0.r8.c1` | Altre scritture |
|---|---:|---:|---|---|
| Catanzaro B0-3 | 7 | 6 | vuota, predicato FALSE | 6/6 conservate |
| Catanzaro E1-3 | 9 | 8 | vuota, predicato FALSE | 8/8 conservate |

**PASS deterministico:** 65 DOCX identici byte per byte; solo i due casi sopra
cambiano, eliminando esclusivamente la scrittura indebita. Nessun nuovo valore,
cambio di posizione, dato USER o checkbox. I 67 audit sottostanti restano esatti
tolta la nuova dimensione separata. Minervino conserva 60 testi SOURCE più una
checkbox USER; Trapani conserva le due prove da 17 testi; Bella/Cesano/CRAA e gli
altri checkpoint restano invariati. Nessuna revisione retroattiva inventata.

Ulteriore confronto di tutti i **213 triplici storici confrontabili** scoperti
in `backend/data/compilation-audit/` con `input.json`, `response.txt` JSON versionato
e `original.docx`: V2–V12, incluso Labirinto. 207 validazioni e sei rifiuti root
pregressi hanno lo stesso risultato prima/dopo, eccetto l'aggiunta separata dei
controlli FORM V12. I sei rifiuti non sono riparati o nascosti. È una regressione
del validatore; non ricostruisce export o dialoghi mancanti e non misura qualità.
Non comprende risposte non JSON o acquisizioni prive del triplice richiesto.
Input, risultati e manifest sono conservati nella nuova consegna; gli originali
non vengono modificati. L'iniziale avvio prematuro del confronto dopo, prima
della conclusione del prima, è registrato come errore del solo harness e rieseguito
in sequenza. Nessuna nuova chiamata provider.

Controlli fisici in tutti i 67 casi: XML delle parti e relazioni, CRC ZIP,
destinazioni effettive, valori, celle non selezionate, testo prestampato, controlli
nativi e geometrie delle tabelle. Cambia soltanto `word/document.xml`, come prima.

PDF prima/dopo dei due controesempi: 17 pagine ciascuno, nessuna parola oltre
pagina, tutti i valori osservabili. Sei falsi negativi della ricerca testuale
semplice sono risolti tramite rettangoli di parole e coordinate, conservando
entrambi gli esiti. La riga sede operativa è a pagina **2**: lettura visiva del
prima B0 e dei due dopo; pagina 1 B0 mostra la sede legale conservata. Non è una
revisione visiva di tutte le 17 pagine né una prova Microsoft Word desktop.

## Prova E2E reale

Preregistrata una sola nuova sessione Catanzaro in UI su un clone isolato, con
un'analisi reale nuova, stesso FORM/22 SOURCE/modello/prompt/parametri B0 e
scenario iniziale conservato. Eventuale unico turno di risposte solo sulle
scelte già autorizzate nello scenario; le altre decisioni restano rinviate.
Export esplicito e download ordinario; nessuna modifica di codice durante la
prova, nessun replay dell'output nel provider o intervento manuale sullo stato.
L'emendamento prima delle chiamate conserva il protocollo iniziale e registra
la correzione software emersa nella regressione.

Sessione reale `196e0ac512b0410e9b7d71cea6cf04a8`, conversazione
`conv-1046343bf298433a`, versione finale 7 `GENERATED`. Il nuovo output propone
18 assegnazioni: 16 grounded effettive, compresa la sede operativa. Per questa
destinazione ripete esattamente la classe di errore: `disposition=value`,
`conditions=[]`. Il backend ricava FALSE dalla riga FORM e dalle SOURCE e la
esclude prima della revisione del narratore: non serve un hold del modello.

Un solo turno USER successivo conferma il ramo società di ingegneria già scelto
nella richiesta iniziale. La ricevuta rimane USER; la condizione semantica MODEL
rimane UNKNOWN nell'audit e l'applicabilità locale della sede rimane FALSE.
Gli altri due rami UNKNOWN non vengono confermati. Export esplicito successivo,
15 scritture SOURCE, zero valori USER/checkbox, sede operativa vuota e sede
legale conservata. Nessuna modifica di stato o codice durante la prova.

**PASS del percorso operativo e del veto richiesto**, non certificazione della
bozza completa: `t25.r3.c1`, che chiede «numero e data d'iscrizione», riceve il
solo numero `01234560981`. È il limite indipendente già noto dei valori composti,
qui osservato nuovamente e lasciato intatto; non è un errore di applicabilità.
Il totale 15 non viene presentato come 15 risposte semanticamente complete.
Direttore tecnico Elisa Romano associato al ruolo SOURCE/FORM; nessuna
designazione di nuovi esecutori o attribuzione di poteri mediante il turno USER.

Controllati report/download e 15 posizioni XML, CRC/parti DOCX, prestampato,
tabelle e controlli nativi. La ricostruzione offline dal nuovo MODEL e dalle
ricevute effettive riproduce audit, DOCX e download esattamente, senza rete/SQLite.
PDF di 17 pagine, tutti i 15 valori osservabili (due tramite rettangoli locali),
nessuna parola fuori pagina; viste pagine 1, 2 e 11. La sede operativa a pagina 2
è vuota; sede legale e dati societari restano leggibili. Nessuna prova Word desktop.

Sette chiamate reali: una globale, tre router, due sintesi e un guard USER;
150.364 token, 122,05 s globale e 129,92 s HTTP AI sommati. Modello `deepseek-flash`,
globale enabled/low e fingerprint `e72d3c7f663d3e1383b00b3884cb4501` invariati
rispetto allo studio. Alias e fingerprint non certificano pesi immutabili;
un campione non misura accuratezza o latenza statistica. Nessun retry di qualità.
Dieci GET abortite a mount/reload del browser; zero POST fallite, errori console,
pageerror o errori provider. Trace/video, richieste, reasoning, output, tempi,
usage e revisioni sono conservati. Primo setup API prima dell'avvio completo
del servizio: connection refused, nessuna richiesta/inferenza eseguita; poi
stesso clone. Nessuna ripetizione della sessione o selezione del risultato.

## Limiti e conservazione

La garanzia indipendente riguarda la grammatica locale riconosciuta. Non è un
interprete generale del linguaggio naturale: condizioni semantiche arbitrarie,
rinvii remoti e topologie prive di un'associazione locale supportata continuano
a richiedere i controlli preesistenti. Le comparazioni riconosciute ma non
dimostrate sono bloccate, con possibile perdita conservativa di compilabilità;
non vengono convertite in false o true. Non si deducono disuguaglianze da
indirizzi scritti diversamente né si risolvono alias o composizioni di valori.
Per un UNKNOWN del nuovo controllo non è introdotto un assenso USER sostitutivo.

Le 13 destinazioni tabellari Catanzaro, equivalenze, ownership condizionale,
limiti CRAA/PDF già diagnosticati e altre omissioni restano separati e invariati.
Nessun intervento successivo è avviato. Gli output storici identici conservano
anche i loro difetti indipendenti: questo rapporto non li presenta come corretti.

Consegna in `benchmark ufficiale/form-applicability-20261020-01/`; acquisizioni
e log in `backend/data/compilation-audit/form-applicability-20261020-01/`.
Snapshot prima/dopo e manifest conservano il working tree, non soltanto HEAD.
Controllo di preservazione: l'intero DB live è logicamente identico, 29 sessioni
e 273 file storage live intatti; 38 sessioni/490 file del clone precedenti
conservati, una nuova sessione isolata. Le 12 risorse knowledge coincidono con
il manifest del precedente studio. I 68 hash applicativi finali restano fissi.
Gli esperimenti originali e gli altri file protetti sono verificati per hash.
Servizi isolati arrestati. Nessun commit, push, migrazione o reindicizzazione.

Il [pacchetto di consegna](<../benchmark ufficiale/form-applicability-20261020-01/README.md>)
contiene indice, casi prima/dopo, nuova bozza reale, manifest e backup separato.
La verifica del pacchetto estratto è in `VERIFICA-BACKUP.json`: ripete 134 DOCX,
268 audit strutturali, 426 risultati dei validatori e l'export reale, vietando
rete e SQLite e usando solo il codice conservato. Credenziali, `.env`, chiavi e
database privati sono esclusi. I grezzi locali esclusi da Git richiedono questo
backup separato; il solo eventuale push futuro non li conserverebbe.
