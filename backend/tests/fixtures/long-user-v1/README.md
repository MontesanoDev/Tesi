# Risposte USER lunghe — fixture v1

`craa-diagnosis.json` congela la diagnosi originale del benchmark CRAA:
225 caratteri nel metadato MODEL `UserFieldRequest.reason`, massimo 200.
Non è una risposta USER troppo lunga. Il test preserva questa distinzione e
non modifica il contratto globale per far accettare il metadato.

I test generano separatamente messaggi USER ai limiti 2.000/2.001/3.999/4.000/4.001,
con API e DB isolati e provider simulati. La richiesta originale viene conservata
integralmente; gli estratti StrictModel possono normalizzare gli spazi esterni.
Il limite degli estratti V12/controlli è 4.000; il valore rimane limitato a 1.500.
Nessun taglio automatico, assegnazione arbitraria o confusione fra SOURCE/USER.

Le nuove prove UI reali, separate dai test software, sono documentate in
`docs/craa-risposte-user-2026-10-20.md`. Non sono fixture di accuratezza universale.
