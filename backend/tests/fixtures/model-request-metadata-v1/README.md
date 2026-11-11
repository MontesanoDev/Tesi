# Metadati descrittivi MODEL — fixture v1

`craa.json` conserva la risposta reale e le SOURCE originali del benchmark
casuali-v12-20261019-01, insieme alla ricevuta societaria accettata. Il FORM è
riutilizzato da `../formtext-v1/craa/original.docx` senza copiarlo o modificarlo.
Non contiene un gold da inviare al provider: i test sono completamente offline.

L'unica differenza del controfattuale è `clarifications.p5.s0.reason`:
225 caratteri originali e una descrizione diagnostica breve. Tutte le prove FORM,
le SOURCE e i gate fattuali rimangono identici. Il test verifica l'ingresso nel
pool, non attribuisce al narratore una nuova domanda mai generata.

Il contratto MODEL conserva massimo200; il runtime conserva la motivazione
integrale e un warning quando la sola lunghezza eccede il limite. Nessuna
normalizzazione di fatti, identità, citazioni, condizioni o destinatari.
