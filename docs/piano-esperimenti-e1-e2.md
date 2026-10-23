# Piano E1/E2 — semplificazione del FORM e prove su estratti

**17 ottobre 2026 — disegno aggiornato dopo B0 ed entrambe le varianti E1.**

L'utente propone di separare il confronto sulla rappresentazione JSON del
modulo completo dal confronto sul contesto ridotto per accelerare lo sviluppo.
La separazione consente di attribuire risultati e limiti a due cambiamenti
distinti. La discussione originaria non approvava l'intera architettura;
l'utente ha poi autorizzato esplicitamente E1, implementato nel banco di prova.

**Decisione successiva dell'utente, 17 ottobre:** fermare la compattazione del
FORM. B0 resta il riferimento; entrambe le varianti E1 non da integrare. E2
non avviato, nessuna prosecuzione automatica del piano qui sotto. La
[diagnosi offline dell'output](diagnosi-contratto-risposta-b0-e1-2026-10-17.md)
usa soltanto gli artefatti salvati e propone un cambiamento minimo del compito
di risposta, ancora senza implementazione o nuove chiamate.

## Domande sperimentali e confronti

| Variante | FORM inviato | Confronto | Cosa permette di valutare |
|---|---|---|---|
| B0 | Minervino completo, rappresentazione attuale | Riferimento per E1 | Prestazioni del sistema precedente alla semplificazione |
| E1 — FORM compatto | Stesso Minervino completo, JSON più efficiente | E1 contro B0, sull'intero modulo | Risparmio di token e tempo, qualità e regressioni mantenendo il contesto globale |
| E2 — Estratti mirati | Stessa rappresentazione compatta E1, limitata a gruppi di requisiti con le loro dipendenze | Ogni gruppo E2 contro E1 completo, valutando soltanto le medesime destinazioni | Risparmio per il ciclo di sviluppo e scostamenti di qualità locale dovuti alla riduzione del contesto |

Il tag baseline-minervino-v1-20261016 congela codice e materiali; non contiene
ancora le misure di B0. Una maggiore brevità del JSON non dimostra da sola
una migliore compilazione. Un estratto con buoni risultati non dimostra
completezza, correttezza dei rami o qualità del Word sull'intero documento.

## E1: isolare la rappresentazione

Il [primo contratto](contratto-e1-form-compatto.md), approvato dopo B0, dettaglia
punto d'intervento, metadati da condividere, supporto alle citazioni e verifiche
strutturali. [Prima serie E1 completata](esperimento-e1-form-compatto-2026-10-16.md):
compact-v1 nel banco di prova, -16,09% input token; Word 14/11/23 contro 23/17/22.
Qualità non stabilizzata, nessuna adozione nella chat. E2 non ancora avviato.

Originale, contenuti documentali, fonti autorizzate, disponibilità delle
informazioni USER e valori attesi restano identici. Si modifica soltanto la
serializzazione del FORM per ridurre ridondanze e dettagli tecnici superflui.
Testo, campi, tabelle, condizioni e riferimenti conservano significato e
collegamento all'originale. La versione interna completa resta disponibile
per validare le prove e materializzare la bozza.

Restano fissi provider/modello, parametri, budget, schema della risposta,
validatori, gestione delle sessioni e writer. Gli adattamenti indispensabili
del prompt alla nuova vista vanno acquisiti e dichiarati: in tal caso il
trattamento è la vista con le sue istruzioni, non la sola lunghezza del JSON.
Se cambiano anche gli identificatori della risposta o i criteri di accettazione,
separarne la valutazione invece di attribuire ogni effetto alla compattezza.

Prima del modello si verifica la copertura strutturale della vista rispetto
all'originale. Il gold rimane nel valutatore: non viene usato per costruire
la rappresentazione o suggerire interpretazioni al sistema.

## E2: valutare l'utilità degli estratti nello sviluppo

La versione della vista compatta viene fissata dopo E1. Per ciascun gruppo
si confrontano E1 completo ed E2 sulle stesse destinazioni, con le medesime
informazioni disponibili al checkpoint. Entrambi vengono valutati contro il
gold: l'accordo fra due risposte sbagliate non è un successo.

I gruppi sono definiti da blocchi e dipendenze del modulo, non dalla sola
pagina renderizzata. Prima delle prove si registrano selezione, destinazioni,
istruzioni ereditate e contesto incluso. Un estratto mantiene titoli, rami,
soggetti e vincoli globali necessari alla sua interpretazione. Il contesto
si seleziona dal FORM e dagli input autorizzati, senza aggiungere fatti,
etichette semantiche o risposte ricavate dal gold.

| Gruppo proposto | Copertura locale e dipendenze da preservare |
|---|---|
| Firmatario e anagrafica | Scelta USER del firmatario, dati personali distinti dalla società, continuità fra paragrafi |
| Soci e direttore tecnico | Tre persone, dati ripetuti, Elisa sia socia sia direttore; ramo societario applicabile |
| Partecipazione e alternative | Scelta iniziale della società di ingegneria, campi degli altri rami da lasciare vuoti |
| Preferenze | Intestazioni e fasce, istruzione massimo sei, dipendenze fra le quattro tabelle |
| Dichiarazioni e sottoscrizione | Decisioni USER disponibili soltanto al loro momento, designazioni, continuazioni vuote e firma manuale |

Questo elenco è una selezione proposta: span e dipendenze esatti devono essere
inventariati e congelati fuori dalla fixture Minervino V1 prima dei run.
Se per un gruppo è necessario tutto un insieme di tabelle, conservarlo.
Un contesto incompatibile con un estratto breve va dichiarato, senza eliminare
il vincolo per ottenere un test più veloce. Eventuali indizi strutturali aggiunti
devono essere dichiarati: rendere esplicito il ramo può facilitare il compito.

Nella prima serie E2 si mantengono tutte le fonti e gli stessi chunk di E1,
così la selezione delle SOURCE non diventa una seconda variabile. Rimane
quindi un costo fisso per fonti, prompt e schema. La riduzione delle fonti
sarebbe un esperimento successivo, con selezione riproducibile indipendente
dal gold. Non scegliere a posteriori soltanto i frammenti che contengono
le risposte corrette.

Il perimetro della risposta deve corrispondere al gruppo visibile, conservando
i criteri di prova: gli altri requisiti non sono omissioni locali, ma fuori
ambito di quella prova. Registrare ogni adattamento del perimetro richiesto.
La minore quantità di output è parte del compito ridotto E2; non dimostra un
guadagno a parità di compilazione completa.

Gli estratti servono al banco di prova. Non introducono un motore produttivo
di compilazione a gruppi, sessioni indipendenti da fondere o export di parti
del documento. La verifica del Word finale resta nel percorso completo.

## Misure e criteri prima delle esecuzioni

| Misura | E1 | E2 |
|---|---|---|
| Qualità | Tutti gli esiti del gold, distinti per categoria | Stessi esiti limitati alle destinazioni del gruppo; confronto con E1 e gold |
| Errori critici | Persone/ruoli errati, invenzioni, rami o scelte non autorizzati, firma simulata | Stessi errori, con attenzione alla perdita delle dipendenze |
| Flusso | Proposta, validazione, stato e scrittura distinti | Fase effettivamente esercitata dichiarata; nessuna qualità del dialogo/export dedotta dalla sola proposta |
| Risorse | Token input/output/reasoning e cache, chiamate e tempo dell'esecuzione completa | Stesse misure per gruppo e somma di tutti i gruppi, incluse ripetizioni di fonti e contesto |
| Copertura | Documento completo | Casi e destinazioni inclusi/esclusi espliciti; nessuna percentuale riferita al documento intero |

Prima del confronto formale fissare modello/configurazione, numero dei run,
criteri di equivalenza e margine ammissibile per eventuali differenze locali.
Proposta: nessun nuovo errore critico; ogni perdita di correttezza va riportata.
Se non viene fissato un margine e un piano adeguato di verifica, descrivere
semplicemente gli scostamenti osservati. Non dichiarare equivalenza o assenza
generale di perdita di qualità sulla base di pochi esiti favorevoli.

Il protocollo completo Minervino prevede tre esecuzioni per versione: mostrano
variabilità iniziale, non bastano da sole a una conclusione statistica robusta.
Le prove brevi singole sono diagnostiche; le varianti candidate richiedono
conferma sul modulo completo. Un eventuale miglioramento solo locale non
autorizza a dichiarare migliore il sistema completo.

Misurare la latenza per la modifica mirata e il costo totale della suite.
La somma di molte chiamate con contesto ripetuto può superare un'unica prova
globale. Confrontare esecuzioni con condizioni di cache dichiarate; token e
costo monetario non sono intercambiabili. Nessuna promessa di risparmio prima
di aver acquisito usage e tempi reali.

## Sequenza e registrazione

1. Predisporre ambiente isolato e acquisizioni; misurare B0 con Minervino V1.
2. Confrontare E1 completo con B0, conservando anche i risultati sfavorevoli.
3. Fissare la versione compatta da usare come riferimento per E2.
4. Congelare i gruppi e confrontarli con le corrispondenti destinazioni di E1.
5. Usare tutti i gruppi brevi a ogni modifica locale; come cadenza proposta,
   controllo completo ogni due o tre varianti e prima di adottarne una.
6. Conservare la regressione Labirinto e le prove occasionali separate su
   altri bandi; non stimare generalizzazione da Minervino soltanto.

Se E1 o il modello cambiano durante lo sviluppo, il riferimento di E2 va
rieseguito e versionato. I risultati dei due esperimenti restano separati;
un futuro confronto con documenti interi inviati al provider è un'altra variabile.

Per ogni esecuzione: input/schema/request effettivi, fonti e hash, scope,
output, validazioni, stato, checkpoint USER quando esercitati, tempi/usage,
confronto con il gold e limiti. Report in docs/, raw in nuove directory sotto
backend/data/compilation-audit/, con backup; registro in relazioni.md.

**Stato dopo la prima serie, 16 ottobre:** [B0](baseline-minervino-b0-2026-10-16.md) ed
[E1 compact-v1](esperimento-e1-form-compatto-2026-10-16.md) acquisiti, ciascuno
con tre analisi reali e tre continuazioni isolate fino al Word. Prima variante
compatta non promossa nella chat: risparmio token, qualità non equivalente
dimostrata. Nuova rappresentazione E1 da valutare prima di fissare la base E2.
Nessun estratto E2 materializzato. Fixture/fonti/gold e motore di produzione
invariati; scelte dei gruppi/margini ancora da fissare prima dei loro risultati.


**Seconda serie E1 conclusa il 17 ottobre:**
[compact-index-v2](esperimento-e1-index-2026-10-17.md), indice diretto e tipi
espliciti, input -13,31% B0. Un rifiuto del contratto, un troncamento, una
analisi accettata con Word 21/60; nessun retry/riparazione, 1/3 successi.
Risparmio input confermato, qualità/affidabilità insufficienti per l'adozione.
Versioni conservate nel runner, default operativo full. E2 ancora da avviare;
prima di altre compattazioni è proposto un esperimento separato su contratto
di uscita e budget reasoning, una variabile per serie. Non ancora approvato.
