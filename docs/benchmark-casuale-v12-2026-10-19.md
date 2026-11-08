# V12 invariata su tre nuovi bandi estratti da un pool

Richiesta conclusa il 19 ottobre 2026. [Rapporto completo](<../benchmark ufficiale/casuali-v12-20261019-01/RAPPORTO.md>),
[consegna e backup](<../benchmark ufficiale/casuali-v12-20261019-01/README.md>),
[misure](<../benchmark ufficiale/casuali-v12-20261019-01/CONFRONTO.json>),
[controlli](<../benchmark ufficiale/casuali-v12-20261019-01/CONTROLLI-FINALI.json>).

Una sola estrazione di tre moduli da un pool congelato di otto DOCX SIA nuovi:
CRAA, Bella, Cesano Maderno. Dimensione, criteri e seed fissati prima della
ricerca; ricerca estesa prima del sorteggio. Pool di convenienza, casualità
interna al pool, una replica per modulo e nessun GOLD indipendente: nessuna
percentuale di accuratezza globale. Nessuna sostituzione o replica selettiva.

Tre nuove CompilationSession dalla UI reale, una nuova globale per FORM,
stessi 22 chunk Company/General del benchmark storico e scenari USER
indipendenti preregistrati. Due turni di risposta al massimo, poi normale
export parziale. Il codice V12, il modello e i controlli sono rimasti invariati.

| Misura | CRAA | Bella | Cesano Maderno |
|---|---:|---:|---:|
| Valori proposti / grounded / applicabili / scritti nell'XML | 9/9/9/9 | 4/4/4/4 | 0/0/0/0 |
| Testi SOURCE corretti e leggibili nel PDF | 7 | 4 | 0 |
| Scritti nell'XML ma invisibili nel PDF | 2 | 0 | 0 |
| Nucleo SOURCE ancora vuoto nell'XML | 1 | 4 | 4 |
| Nuove checkbox / testi USER | 0/0 | 0/0 | 0/0 |
| Scritture fattuali o decisioni indebite rilevate | 0 | 0 | 0 |
| Pagine PDF | 7 | 4 | 3 |

CRAA perde il chiarimento sul firmatario: motivazione di 225 caratteri contro
un massimo di 200 nello schema. I due dati CCIAA sono corretti nell'XML ma
non appaiono nel PDF LibreOffice, in celle originali di 66/81 twip. Le
dimensioni sono preservate; il nesso causale non è stato sperimentato
modificando la geometria o con Word desktop.

Bella omette quattro proprietà del firmatario presenti nell'input; il riuso
anagrafico non riconosce la struttura inline e la ricevuta della condizione
non conserva la scelta nominativa. Il gruppo della partecipazione è respinto
per etichette FORM incomplete. Cesano espone alla chat solo 68 checkbox:
i 20 campi legacy FORMTEXT non hanno destinazioni testuali supportate. La
globale procede, contrariamente al preflight generico, ma non propone valori;
il chiarimento societario indirizzato a una checkbox è respinto. L'export
senza valori è un fallimento funzionale, non una bozza utile.

Le SOURCE dei nove vuoti del nucleo sono tutte nell'input: cinque omissioni
di valore e quattro destinazioni non esposte. Nessuna proposta di valore
SOURCE è stata respinta in queste tre prove. Preferenze, attestazioni,
esecutori, integrazione e luogo/data restano separati e UNKNOWN; non sono
inferiti consensi, firme o designazioni. CRAA/Bella ripetono una domanda
perché la negazione “senza raggruppamenti o consorzi” viene scambiata per
un'alternativa. Nessun hold finale: questi campioni non verificano hold
legittimi negativi.

22 chiamate reali, tre globali nuove, zero retry di qualità, 271.084 token,
291,57 secondi HTTP sommati e 0,060070 USD stimati da usage/cache e tariffa
ufficiale conservata. DeepSeek `deepseek-flash`, globale thinking enabled/low,
fingerprint comune `e72d3c7f663d3e1383b00b3884cb4501`. Tempi operatore, ricerca
web e rendering esclusi dalla somma HTTP; nessuna misura comparativa di latenza.

Verificati XML/ZIP, posizioni, prestampato, report e download; nessun cambiamento
alle checkbox. Bounding box su 14 pagine, ispezione visiva di pagine selezionate:
il controllo dei bordi da solo non rileva i due valori invisibili. Replay con
rete vietata ricostruisce audit e tre DOCX identici, compresi i difetti.

318 file applicativi/test/frontend/fixture, 41 input congelati, 422 artefatti
precedenti, 29 sessioni originali e 285 file storage invariati. Tre sessioni
nuove isolate e schema DB intatto; servizi isolati arrestati. Grezzi in
`backend/data/compilation-audit/casuali-v12-20261019-01/`, backup separato nella
consegna. Nessuna suite completa rieseguita, commit/push o correzione avviata.

Il risultato sostiene verifiche mirate su destinazioni Word, chiarimenti e
riuso della persona prima di un altro E1. È una proposta, non un intervento
implementato. Il precedente errore PEC resta irrisolto: baseline non adottata.
Se questi casi guidano lo sviluppo, la futura valutazione finale richiederà
un altro lotto non usato per scegliere le correzioni. Arresto alla consegna.
