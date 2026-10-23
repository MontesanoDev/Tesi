# Consenso procedurale: caso reale Trapani

`trapani-real.json` conserva risposta globale, SOURCE e ricevute USER della
sessione storica Trapani, senza correggere l'output del modello. Non è un GOLD
e non entra nel prompt o nella KB. Originale riusato da
`../formtext-v1/trapani/original.docx`.

Il modello propone lo stesso fatto PEC in `p75.s8` (recapito aziendale) e
`p107.s0` (accettazione delle comunicazioni e assunzione del rischio). La SOURCE
dimostra il recapito, non la seconda decisione. Le ricevute storiche riguardano
tipologia/partecipazione e luogo/data, senza autorizzare questa dichiarazione.

Aspettativa: mantenere nove scritture fattuali, lasciare vuoto il campo della
dichiarazione finché una ricevuta USER pertinente non ne autorizza l'uso.
I test separano grounding, revisione, applicabilità e consenso; conservano il
valore e le prove SOURCE. Le sessioni nei test usano provider simulati, mentre
la nuova prova reale è archiviata separatamente.
