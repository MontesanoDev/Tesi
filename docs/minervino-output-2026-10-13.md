# Minervino: verifica della bozza fornita dall'utente

## Risultato verificato

File `domanda-iscrizione.compilato.docx`, SHA256
`24acc8624f0c9b36a6909748463d0467bff9a65e967eb6676883bed43ce811b0`.
Identico alla bozza persistita della sessione
`e484f26a4d02493185d76606215f0bf2`, versione 7, generazione
`d25dd2db93a64bd7bb5e68a6771241ea`. Stato GENERATED significa che la bozza
parziale è stata esportata dopo consenso, non che tutto il modulo è completo.

**Nove valori SOURCE scritti, zero valori USER e tutte le tredici checkbox
native vuote.** Tre paragrafi modificati oltre al banner. I nove valori
corrispondono al report e ai candidate indicati nel JSON. Questo verifica la
materializzazione, non la precisione semantica di ogni destinazione. Quindici
parti ZIP estranee al corpo del documento sono identiche all'originale.
Originale, file fornito e sessione/versione verificati invariati durante la diagnosi.

| Candidate | Campo | Valore scritto | Prova |
|---|---|---|---|
| p40.s0 | Denominazione società | Mapi Ingegneria S.r.l. | SOURCE Company KB, generalita-mapi.md, chunk -43 |
| p41.s0 | Partita IVA società | IT01234567890 | SOURCE Company KB, chunk -43 |
| p41.s1 | Sede legale società | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE Company KB, chunk -43 |
| p42.s0 | Provincia | BA | SOURCE Company KB, chunk -43 |
| p42.s1 | Via/piazza | Via Giovanni Amendola | SOURCE Company KB, chunk -43 |
| p42.s2 | Civico | 172/C | SOURCE Company KB, chunk -43 |
| p42.s3 | Telefono | +39 080 000 2040 | SOURCE Company KB, chunk -44 |
| p42.s4 | E-mail | segreteria@mapi-ingegneria.demo | SOURCE Company KB, chunk -44 |
| p42.s5 | PEC | mapi.ingegneria@pec.demo | SOURCE Company KB, chunk -44 |

Conservati file/chunk/ruolo/scope/category, quote letterali e digest del contenuto.
Controllati quote e valori nelle SOURCE effettivamente inviate nell'input
registrato. Confermare l'applicabilità tramite USER non cambia la provenienza
SOURCE dei valori. Non è una verifica anagrafica su un'azienda reale: dati demo.

### Indirizzo troppo esteso per il contesto locale

Il campo p41.s1 è preceduto da «sede legale in»; il paragrafo successivo
richiede già provincia, via/piazza e civico separati. Il modello assegna
l'indirizzo completo al primo e poi ripete via/civico. La struttura suggerisce
di indicare il comune Bari nel primo campo. La bozza è quindi ridondante:
nessun valore inventato o slittamento del writer, ma associazione semantica
da affinare. Il slot_context di p41.s1 conserva soltanto «sede legale in»;
la prosecuzione è disponibile nel catalogo globale come altro paragrafo,
non nel suo anchor locale. Non viene applicata una correzione automatica.

## Perché le checkbox sono vuote

L'output reale DeepSeek V11 contiene **choice_groups={}** e **zero assegnazioni
checkbox**. Tutti i tredici controlli sono nell'inventario backend/input, ma
rimangono non valutati. Il report export contiene checkbox_values={}.
Il renderer riceve quindi zero booleani e preserva gli stati originali, tutti
false. Questo tentativo non esercita la scrittura delle checkbox del modulo.

La risposta «società di ingegneria» viene registrata come CONDITION_TRUE su
c2, applicabilità dei dati del ramo societario. Non è una scelta VALUE su un
gruppo checkbox attivo, non crea user_values e non scrive p39.cb0.
Applicabilità confermata e selezione nativa sono attualmente percorsi distinti;
nessun collegamento valido viene inventato a posteriori dal backend.

Il contratto ammette una mappa di gruppi vuota e l'analisi è sparse. Il backend
non richiede ancora la copertura di tutte le scelte prima di offrire una bozza
parziale. I test del writer dimostrano la scrittura dei gruppi validati, non
che il modello li produca per ogni bando. Questa diagnosi non attribuisce
il risultato a gruppi respinti: in questa esecuzione non sono stati proposti.

## Copertura e direttore tecnico

267 posizioni candidate grezze; 16 assegnazioni del modello, 15 proposte testuali
grounded conditional e una rifiutata. 251 posizioni omesse, incluse le 13 checkbox.
Questi numeri non equivalgono a campi obbligatori o a una percentuale di
accuratezza: candidate e campo semanticamente pertinente non sono sinonimi.

La Company KB **era già nell'input effettivo** con Ing. Elisa Romano,
Ingegnere, Ordine degli Ingegneri di Bari e numero 8421. Prove nei chunk -45
di generalita-mapi.md e -32 di visura-mapi-ingegneria-simulata.pdf.
Il FORM richiede la figura nel ramo Responsabile della Progettazione/Direttore
Tecnico, paragrafi 50–53. Nessuna proposta per p51.s0 (nome), p52.s0 (qualifica),
p53.s0 (Ordine), p53.s4 (numero). L'omissione avviene nella generazione del JSON,
prima di un tentativo di associazione/validazione di quei valori.
Non dichiarare tali dati assenti dalle fonti né già verificati per la bozza.

Il comune Bari, p15.s0, è invece realmente proposto ma rifiutato: la quote di
destinazione contiene sia [[p15.s0]] sia [[p15.s1]], mentre il gate richiede un
solo marker del destinatario. È un falso negativo distinto. Nel risultato
corrente anche quel blocco è rinviato, quindi ammetterlo non basterebbe a farlo
entrare nell'export autorizzato.

## Cosa ha fatto il dialogo

Prima domanda: tipo societario e qualifica del sottoscrittore sono uniti nella
condizione c2 di rappresentanza. «società di ingegneria» viene accettato come
applies=true; ciò non identifica chi firma. È una modellazione da affinare:
la domanda mescola natura dell'operatore e rappresentanza della persona.

Seconda domanda: «A quale titolo ... per conto dell'operatore economico?».
«la seconda lascia vuoto» diventa SKIP della condizione c1, che controlla **sei
proposte aziendali** della parte iniziale. Non rinvia soltanto un valore della
carica. Restano quindi vuoti denominazione operatore, provincia, telefono,
e-mail, PEC e PIVA nell'intestazione; il ramo societario riceve i nove valori.

La sintesi dopo la risposta dice «li propongo in entrambe», pur conservando
c1 rinviata; l'export esclude correttamente quei sei valori. La narrazione
non esplicita bene l'effetto del rinvio. Dopo le due domande il pool disponibile
termina e il sistema offre la bozza; non torna sulle 251 posizioni omesse.
La conferma «si» autorizza poi l'export di nove valori soltanto.

## Metodo, limiti e prossimo intervento da discutere

Diagnosi in sola lettura, nessuna nuova chiamata provider, generazione o
modifica al motore/RAG/parser/renderer/UI/database. Confrontati file utente,
originale, report, stato, revisioni, catalogo, input/raw e sintesi registrate.
Router/gate USER raw non risultano acquisiti dalla chat normale: non vengono
ricostruiti o presentati come osservati. Non è un nuovo benchmark con gold o
un'esecuzione delle suite software; per questo intervento documentale sono
controllati diff e riferimenti.

Proposta, **non implementata**: rendere verificabile la copertura delle scelte
e delle sezioni pertinenti, collegare le scelte native al dialogo su gruppi
validati, separare tipologia societaria/ruolo del firmatario e chiarire cosa
viene escluso quando si rinvia una domanda. Preferire un primo passaggio
globale più completo; un recupero aggiuntivo bounded delle omissioni resta
un'alternativa da discutere, con costi/tempi maggiori. Non ripristinare i
batch da 12 o spuntare caselle senza prova della scelta.

Raw in `backend/data/compilation-audit/minervino-output-20261013/`:
diagnosis.json, integrity.json, originale/copia fornita, stato/report/revisioni,
conversazione e acquisizioni dell'analisi. Originale SHA256
`25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c`.

[Bundle sanificato](benchmarks/2026-10-13-minervino-output-audit.tar.gz),
[manifest e metriche](benchmarks/2026-10-13-minervino-output-manifest.json):
24 file /1.573.365 byte grezzi, confronto byte per byte e scansione credenziali,
nessun database o chiave privata. SHA256
`84a024ad61e665746187568c259e7b7747466a19d49ece1a55a3402f0c054b46`.
