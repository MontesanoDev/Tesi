# Addendum 1 alla preregistrazione (scritto 2026-10-22T07:59:12Z, dopo il congelamento)

Misura eseguita dopo il congelamento e prima di completare la correzione: replay delle 215 sintesi
legacy (V13, V14) con l'albero pre-P3 ricostruito (`out/replay-all-preP3.json`) contro il codice
della campagna P3 (`out/replay-all-prima.json`): 0/215 impronte identiche. Confronto completo su due
sintesi (`dump_results.py` → `out/results-preP3sample.json`, `out/results-campagna.json`): l'unica
differenza sono due chiavi vuote (`released_blocker_answered`, `suppressed_blocker_answered`) che P3
aggiungeva alla transizione anche nelle sessioni legacy.

Conseguenza: i criteri F3 (legacy identico al pre-P3) e R1 (legacy identico a «prima») non possono
valere insieme. Scelta, motivata dalla richiesta di un fallback uguale a quello previsto: queste chiavi
diventano solo P3, così F3 vale alla lettera. R1 viene verificato così: impronte legacy identiche al
pre-P3; rispetto a «prima» la sola differenza ammessa è l'assenza di quelle due chiavi vuote.
Nessun altro criterio, esito atteso o regola H1-H4 cambia.
