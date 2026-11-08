# Addendum 2 alla preregistrazione (scritto 2026-10-22T08:15:31Z, dopo le verifiche offline, prima dell'E2E)

Esito della sezione 3 per minervino-B1 diverso dall'atteso: fase PENDING (non READY), nessuna domanda,
export 0 (atteso: READY, domande D6, export 34). Sospese (35-40), validazioni (36 RECORDED, altre
UNANCHORED_QUOTE), nessun legame e nessun rilascio coincidono con l'atteso.

Causa verificata (`out/replay-failures-dopo.json`, controllo diretto): la sintesi iniziale di B1 ha 50
proposte da rivedere e una finestra di 40; il codice V12 invariato lascia la revisione in sospeso
(`review_pending`) e la prosecuzione automatica rivede le 10 restanti. Stesso comportamento registrato
in minervino-A1 (v003: `review_pending` vero, 40 riviste). La previsione dell'autore ha ignorato la
finestra di revisione: domande ed export di B1 compaiono solo dopo quella prosecuzione, che offline non
è riproducibile (nessuna risposta registrata).

Valutazione dichiarata: errore di previsione, non difetto della correzione; l'E2E (che include Minervino)
procede. Il rapporto riporta il criterio come non soddisfatto alla lettera.
