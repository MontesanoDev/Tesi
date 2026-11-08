# V12: una prova reale dalla chat dopo la correzione degli hold

19 ottobre 2026. Una sola nuova sessione di compilazione, nessuna correzione
applicativa durante la prova, nessun refactor, commit o push.

**La chat esporta 61 scritture: 60 testi SOURCE e una checkbox USER. Gli otto
campi del direttore non vengono sospesi. I 52 testi precedenti e la checkbox
sono conservati; il DOCX coincide byte per byte con quello del replay61.**

- [DOCX scaricato dalla UI](../nuovi%20dati/domanda-iscrizione.V12-CHAT-REALE-20261019.docx),
  [PDF](../nuovi%20dati/domanda-iscrizione.V12-CHAT-REALE-20261019.pdf),
  [report](../nuovi%20dati/domanda-iscrizione.V12-CHAT-REALE-20261019.report.json),
  [conversazione](../nuovi%20dati/domanda-iscrizione.V12-CHAT-REALE-20261019.conversazione.md).
- [Misure](benchmarks/2026-10-19-v12-holds-chat.json),
  [otto tracciati](benchmarks/2026-10-19-v12-holds-chat-trace.json),
  [controlli](benchmarks/2026-10-19-v12-holds-chat-checks.json).
- [Correzione e replay di riferimento](hold-narratore-v12-2026-10-19.md).

## Protocollo effettivamente eseguito

Nuova sessione `9bd60112c34247f799d320137d81831f`, conversazione
`conv-5037d9a1b3554423`. Database, upload e Company KB clonati in un ambiente
privato; frontend React e backend FastAPI reali su5174/8001. UI pilotata con
Chromium/Playwright, senza intercettazioni o risposte simulate nel browser.
Download del DOCX e ricaricamento della conversazione riusciti.

Come nel riferimento, **la sola inferenza globale è congelata**: stessa risposta
salvata, riusata una volta dopo uguaglianza esatta di FORM,56SOURCE e schema.
Questa scelta, comunicata prima della prova e registrata in `chat/protocol.json`,
isola la correzione del dialogo da variazioni della proposta globale.
Router, guard delle risposte e tre sintesi del narratore chiamano il provider
reale. Validatori, persistenza, rivalidazione ed export sono quelli applicativi,
senza sostituzioni. Non è una nuova valutazione della qualità dell'analisi globale.

Sono inviati dalla chat gli stessi tre messaggi USER letterali del riferimento:

1. Avvio: società di ingegneria, firmatario Leonardo Montemurro, dati documentati
   riferiti al15ottobre2026, domande sulle decisioni mancanti e richiesta di
   conferma prima del Word.
2. Dopo le domande realmente poste: conferma di società e firmatario; rinvio
   della conferma aggiuntiva sul direttore, senza rinunciare all'uso delle fonti.
3. Richiesta esplicita di esportare una bozza parziale con i dati verificati,
   lasciando vuote le altre sezioni.

Nessuna ricevuta originale viene copiata nello stato nuovo. Il router registra
soltanto `condition:c_societa=CONDITION_TRUE` e `condition:c_dt=SKIP`; il secondo
non contiene un consenso di applicabilità. Nessun valore testuale USER è creato.
Il firmatario e le proprietà personali continuano a richiedere le prove SOURCE.
Natura giuridica, scelta della pratica e poteri del firmatario restano distinti.

## Risultato e confronto con il replay

| Misura | Chat precedente | Replay corretto | Questa chat |
|---|---:|---:|---:|
| Testi scritti | 52 | 60 | **60** |
| Checkbox USER selezionate | 1 | 1 | **1** |
| Scritture complessive | 53 | 61 | **61** |
| Otto campi tecnici scritti | 0 | 8 | **8** |
| Hold tecnici dopo USER | 8 | 0 dopo verifica dei motivi | **0, mai introdotti** |
| Testi precedenti persi/cambiati | 0 | 0 | **0** |
| Altre checkbox modificate/deselezionate | 0 | 0 | **0** |
| Nuove scritture indebite osservate | 0 | 0 | **0** |

I61 non sono un parametro imposto alla sessione: il protocollo registra quel
numero come riferimento, senza usarlo per selezionare proposte, modificare lo
stato o ripetere la prova. La misura deriva dal DOCX realmente scaricato e dal
report applicativo. Identici tutti i60 valori testuali rispetto al replay;
sono conservati anche i24 campi dei soci.

SHA256 del DOCX reale e del replay:
`84e33e53477f0bb4935eaa9667ed02c6eea6d010beb091cab4f650a1b87feddd`.
Il file scaricato dalla UI coincide con quello archiviato dal server.
Il report mantiene `ready_for_submission=false`: si tratta di una bozza parziale.

## Comportamento del narratore e transizioni

| Versione | Evento | Proposte revisionate | Hold persistiti |
|---|---|---:|---:|
| 1 | creazione nuova sessione | 0 | 0 |
| 3 | prima sintesi | 40 | 0 |
| 5 | continuazione prima di USER | 51 | 0 |
| 6 | risposta USER, riuso SOURCE e prove del ramo | 51 conservate | 0 |
| 8 | revisione delle17 proposte interessate | 60 complessive | 0 |
| 9 | export esplicito e download | 60 | 0 |

Tutte le nove revisioni persistenti sono salvate, comprese quelle di avvio
elaborazione. I tre output reali del narratore contengono entrambi gli array
`held_proposal_slots=[]` e `hold_reviews=[]`. Dopo USER il modello vede le prove
effettive di applicabilità e lascia aperte le sole decisioni ancora necessarie.

**In questa prova non è scattata la regola di rifiuto dei motivi ridondanti:**
il modello non ha proposto l'hold errato. Questo esito è distinto dal replay B,
nel quale il modello manteneva otto hold e il backend respingeva gli otto motivi.
Non si attribuisce con una sola osservazione tutto il miglioramento a una singola
istruzione del prompt; non è una stima statistica dell'affidabilità generale.

Audit SOURCE finale identico a quello del replay. `c_dt` risulta TRUE dalla prova
composta già verificata; `c_societa` conserva UNKNOWN nell'audit con ricevuta
USER positiva pertinente. Nessun UNKNOWN viene cambiato artificialmente e la
ricevuta SKIP resta intatta. Nessuna divergenza residua nelle scritture.

| Campo originale | Valore effettivo nel DOCX |
|---|---|
| p51.s0 | Elisa Romano |
| p52.s0 | ingegnere |
| p52.s1 | RMNLSI85C47A662Y |
| p53.s0 | Ordine degli Ingegneri di Bari |
| p53.s1 | A |
| p53.s2 | Bari (BA) |
| p53.s3 | 18/05/2015 |
| p53.s4 | 8421 |

## Blocchi necessari e parti ancora vuote

Le cinque decisioni USER restano aperte e coincidono con quelle del riferimento:
categorie/fasce, attestazioni, professionisti esecutori, incaricato
dell'integrazione, luogo/data. Dopo USER la chat presenta categorie, esecutori
e luogo/data; l'utente chiede l'export, senza rispondere a questi punti.
Le altre domande restano nell'agenda del backend, senza ricevute positive.
Non vengono selezionate preferenze, attestate dichiarazioni, assegnati
professionisti o inventati luogo e data.

Quattro testi attesi dallo scenario GOLD rimangono vuoti: `p229.s0`, `p230.s0`,
`p232.s0`, `p242.s0`. Le altre dodici checkbox native restano intatte; solo
`p39.cb0` è selezionata dalla ricevuta USER societaria validata. Zero deselezioni.

**Nello scenario reale non sono comparsi hold fattuali legittimi da conservare:**
non si dichiara quindi di averne osservato una conferma dinamica dalla UI.
Separatamente sono rieseguiti i18 test negativi esistenti del verificatore dei
motivi:18passati,8deselezionati,in1,43s. Prove mancanti, persona diversa, UNKNOWN,
diniego, rinvio del campo, dichiarazione, scope incoerente e ostacoli precedenti
restano bloccanti. Sono controlli software offline con provider simulato,
non ulteriori sessioni UI né chiamate al modello.

## Verifiche sul documento e conservazione

Verificati CRC, XML/rels, posizioni fisiche, corrispondenza col report,
prestampato,4tabelle e13controlli. Cambia soltanto `word/document.xml`;
le tabelle restano intatte e una sola checkbox cambia stato. Gli otto nuovi
valori corrispondono al GOLD congelato. Su60 testi59 sono conformi al confronto
GOLD; resta la carica completa del firmatario già nota, attestata dalla SOURCE,
più estesa della formulazione del GOLD. Zero nuove accettazioni indebite osservate.

Nuovo PDF dal DOCX effettivo con LibreOffice locale:9pagine. Viste le pagine3 e9:
soci e direttore leggibili, linea della firma nell'ultima pagina. Restano le
giunzioni di etichette del writer già documentate, come «sezione Adella»;
nessuna modifica al writer. Il convertitore segnala il registry linguistico
locale mancante ma completa il PDF; il DOCX rimane invariato. Non è una
certificazione tramite Word desktop.

Sono acquisiti input, output e trasporto completo di tutte le7chiamate reali:
3router,3sintesi,1guard. **69.815token =68.766input+1.049output**,13,171s sommati
nelle richieste al provider. Zero nuove globali, un riuso. Nessun retry di qualità.
Il tempo complessivo della sessione include attese dell'operatore e del driver:
non è usato per una conclusione sulle prestazioni. Costo USD non stimato.

Un incidente del driver, avviato inizialmente con stdin chiuso, richiede la
ricarica della **stessa** conversazione in un browser con input interattivo.
Non viene creata una seconda sessione, reinviato l'avvio o ripetuta una chiamata
LLM. DOM, screenshot, rete e trasporti del primo turno sono conservati; la
finalizzazione di trace/video e dettaglio delle5segnalazioni iniziali non è
acquisita. La continuazione salva trace/video e10GET annullate al mount/reload,
zero eccezioni pagina e zero risposte HTTP di errore acquisite. Il ricaricamento
dopo download ripristina correttamente la versione9GENERATED.

Errori dei soli lettori di audit (bytes DOCX nel metadataJSON, nomi di colonne/
tabelle e rappresentazione SKIP/tipi dell'agenda) sono documentati e corretti
nei soli script di raccolta: nessuno cambia sessione, proposte, output o codice
applicativo. Non sono presentati come difetti del compilatore o nuove prove.

La verifica indipendente senza DB, chiavi o rete rigenera l'audit dalle SOURCE,
rivalida le selezioni e ricrea lo stesso DOCX. Raw in
`backend/data/compilation-audit/v12-holds-chat-20261019-01/`; backup separato
in `docs/benchmarks/2026-10-19-v12-holds-chat-audit.tar.gz`, con codice congelato,
richieste/risposte, revisioni, conversazione, Word, PDF e acquisizioni browser.

Nessun file applicativo, test, frontend o fixture modificato durante la prova.
Stati e artefatti precedenti preservati. Servizi isolati arrestati dopo l'export;
nessun'altra compilazione o esperimento avviato.
