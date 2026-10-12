# Conversazione completa — protocollo del 12 ottobre 2026

Protocollo fissato prima delle API. Baseline applicativa `fb2894e`, già
pubblicata su `origin/prune-backend`. Nessun cambiamento applicativo durante
la prova; questa verifica precede qualsiasi decisione sui turni composti.

## Percorso e limiti

Nuova conversazione, originale `domanda-partecipazione.docx` del progetto
`prova`, corpus SOURCE attuale congelato in snapshot privato. DeepSeek Flash
reale, stesso profilo selezionato dal progetto. API HTTP ASGI reali in-process;
non è un test browser. Database/storage isolati: nessuna modifica alle sessioni
live, nessun checkpoint di compilazione preparato manualmente.

Avvio con mention strutturata e «me lo compili?», avanzamento tramite il normale
`resolve`, poi risposta ai chiarimenti realmente posti. Provare rinvio locale,
pausa, riapertura in un nuovo processo e ripresa della stessa sessione.
Chiedere esplicitamente una bozza parziale e controllare il DOCX realmente
prodotto. Massimo 12 turni per conversazione e tre avanzamenti automatici per
turno; nessuna nuova analisi per sostituire un esito insoddisfacente.

Non fornire valori aziendali già presenti nelle SOURCE. Le conferme USER di
applicabilità rimangono distinte dai valori SOURCE. Non inventare risposte
su requisiti non conosciuti: UNKNOWN/SKIP sono esiti ammessi. Non forzare
domande o scritture tramite DB/API field. Se la conversazione reale non pone
un chiarimento adatto al rinvio locale, aggiungere una prova distinta sulla
fixture congelata Labirinto V1, con le sue fonti originali e senza gold nel
prompt. Registrare anche failure ed elementi non esercitati.

## Acquisizioni e verifica

Conservare prompt/schema, raw, usage, tempi, richieste/risposte chat,
conversazione e sessione dopo ogni turno. L'osservatore delega invariati i
trasporti al provider reale; non simula decisioni. Confrontare stato, report,
valori selezionati e posizioni Word; altre posizioni, checkbox e originale
devono restare invariati, salvo il banner di bozza previsto dal renderer.

Distinguere GROUNDED_PROPOSAL da RESOLVED e scrittura della bozza da completezza
del modulo. Nessuna accuratezza percentuale senza gold sul bando reale.
Riferimenti grezzi e bundle sanificato saranno aggiunti al report; database,
chiavi e runtime privati non devono entrare nell'archivio pubblico.

## Risultati

Prima conversazione Catanzaro conclusa: 12 valori SOURCE esportati; pausa e
ripresa persistite. Una conferma anaforica del partecipante è stata giudicata
ambigua dal gate, richiedendo un turno aggiuntivo. Nessuna modifica applicativa.

Prima serie Labirinto conclusa: controlli SKIP/UNKNOWN/pausa/ripresa riusciti,
ma rilevato un errore del setup. `06-procedura.txt` è stato caricato come globale
Company anziché SOURCE del progetto. La serie viene conservata integralmente,
senza presentarla come confronto valido della fixture congelata. Prima di una
seconda serie si corregge solo l'harness: scope/category dal `sources.json`
originale, nuovo DB e nuova conversazione, nessun cambiamento a gold o motore.
Gli ID fisici assegnati dalle API restano quelli reali; il confronto offline
con gli ID simbolici della fixture deve verificare nome, scope e contenuto.

Nota d'ambiente: la creazione di script `.py` sotto backend con uvicorn --reload
attivo ha provocato il normale riavvio e la reindicizzazione di 82 frammenti
di quattro artefatti live. Contenuti, SOURCE, conversazioni, sessioni e originali
sono invariati; non si dichiara identità fisica dell'intero database. Nessun
ripristino manuale. Per il secondo harness si usa un file `.txt` interpretato
da Python, così non si sollecita il watcher.

Risultati finali e acquisizioni da completare. Test precedenti sui 43/28
checkpoint non vengono presentati come risultati di questa conversazione.
