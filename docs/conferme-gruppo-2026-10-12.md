# Conferme riferite al gruppo attivo — 12 ottobre 2026

## Diagnosi e protocollo congelato prima delle API

Baseline applicativa fb2894e, HEAD diagnostico 8e90915; al controllo iniziale
working tree pulito, tre commit davanti a origin/prune-backend. Nessun push.
Il turno 04 del [test completo](test-conversazione-completa-2026-10-12.md)
aveva due domande: applicabilità della sezione e identità del partecipante.
Il router proponeva correttamente CONDITION_TRUE su entrambi gli slot. Il gate
USER indipendente accettava il primo e rifiutava il secondo come AMBIGUOUS:
«il partecipante è quello indicato nelle fonti» era considerato troppo generico,
anche nel messaggio completo «Confermo entrambe: ...».

`render_dialogue` conserva già `question` in ciascuno slot persistito;
`intents.routing_context` lo perde nella proiezione destinata ai modelli.
Rimangono la domanda complessiva, label e contesto FORM: la seconda condition
è soltanto «CHIEDE di partecipare alla presente gara». Nessuna perdita della
frase USER intera: è già inviata. Il prompt del verificatore ammette parafrasi
ma non chiarisce l'ambito delle conferme esplicite dell'intero gruppo.
Non è un difetto del retrieval SOURCE o dello schema della risposta.

Modifica minima prevista: preservare il testo naturale per slot (massimo 600
caratteri, stessa dimensione già validata nella sintesi) e precisare nel gate
la risoluzione dei riferimenti alla domanda attiva, le eccezioni e la polarità.
Nessuna accettazione automatica, keyword USER, nuovo schema/API, seconda ricerca
o chiamata AI. Il gate semantico indipendente continua a fallire in modo
conservativo, prima di quote/validator DOCX/CAS/provenance USER. I casi storici
senza question per slot restano leggibili. Turni composti ancora da discutere.

Congelati [16 scenari V1](../demo-documents/benchmark-dialogo/group-confirmations-v1/README.md)
prima delle API: caso reale, parafrasi, conferme di entrambe, riferimenti
numerati, negazioni, eccezioni locali, parti incerte, conferme senza valori,
correzioni estranee e ambiguità. Nuova fixture, gold storico invariato.
Il runner guard esistente accetta una fixture esplicita e verifica hash, slot
e budget prima di leggere il profilo AI o chiamare il provider.

BEFORE e AFTER: stessa fixture, 16 chiamate massime per fase, nessun retry,
15 s/768 token output per chiamata. Nuovo checkpoint DB/storage temporanei
per caso. Proposte preparate non affidabili, provider DeepSeek Flash reale;
gold non inviato. Gli slot registrati vengono rimappati su due candidate della
fixture di dialogo per misurare mutazioni USER, non correttezza del modulo intero.
Regressioni AFTER su guard-v1 (9) e Dialogo V1 (43). Nessuna ripetizione
selettiva, errori conservati. Replay del checkpoint reale separato da nuove
analisi SOURCE; nessuna pretesa di avere rieseguito l'analisi globale.

Prima delle API: quattro test del protocollo senza provider passati /0,54 s;
Ruff runner/test e diff check passati. Risultati e costi saranno aggiunti dopo
le serie, senza modificare aspettative o codice durante ciascuna serie.

## Baseline e modifica applicativa

BEFORE sul commit 0ef3bd5: **14/16** conformi. Riprodotto il caso registrato:
SUPPORTED primo slot, AMBIGUOUS secondo. Anche la conferma di tre punti misti
respingeva interamente le proposte, compresa la sola condizione rispondibile.
Tutti i controesempi negativi conformi, nessuna scrittura estranea.
Grezzi `backend/data/compilation-audit/group-confirmations-20261012/before/`.

Applicata soltanto la proiezione `question` per slot e il task del verificatore,
senza cambiare output, binding destinatari, numero di chiamate o accettazione
deterministica. Task generico: riferimenti univoci alla domanda attiva, ambito
esplicito del gruppo, eccezioni locali; una conferma non inventa valori VALUE.
**72 test software mirati /7,39 s**, provider simulati per i test di stato,
Ruff file modificati superato. Non misurano DeepSeek; la serie AFTER segue.

Prima serie AFTER su c6bd0ff: **15/16**. Il caso reale è corretto, entrambi
SUPPORTED e aggiornamenti USER distinti; i casi già conformi restano conformi.
Rimane il gruppo misto «Confermo tutti e tre i punti»: respinti correttamente
email/data inventati, ma erroneamente anche la conferma della condizione.
Precisata soltanto l'indipendenza delle condizioni booleane dalle richieste
di valori assenti nello stesso gruppo. Nuova serie completa AFTER-2 con lo
stesso gold congelato, nessuna ripetizione selettiva; AFTER precedente conservata.

Replay reale previsto: nuova sessione in snapshot privato, riuso dichiarato
del checkpoint Catanzaro precedente al consenso (non nuova analisi). Rivalidare
il raw reale contro originale e corpus corrente, chiedendo l'uguaglianza con
l'audit archiviato. Due turni HTTP ASGI reali: stessa conferma anaforica, poi
richiesta esplicita di bozza. Routing/gate/sintesi reali, originali e dati live
solo letti. Confrontare due condizioni USER, zero valori fattuali USER, stessa
analisi, 12 proposte SOURCE/stato/report/celle; eliminare snapshot e chiave dopo
le verifiche. Runner fuori dal watch root backend, nessuna modifica durante le API.
