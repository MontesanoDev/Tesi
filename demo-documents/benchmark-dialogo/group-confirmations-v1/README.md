# Conferme del gruppo attivo V1 — fixture congelata

16 proposte per il verificatore indipendente, prima/dopo il fix. Non sono
16 compilazioni complete né una prova del retrieval SOURCE. L'originale
modulo-dialogo.docx è quello di ../v1, mai modificato. I due destinatari del
caso registrato vengono rimappati su due candidate distinti della fixture:
si misura solo interpretazione della domanda persistita e mutazione USER.
Il messaggio e le due proposte recorded-real provengono dal turno 04 del test
full-conversation-20261012; le domande di ciascuno slot erano già persistite.
Altri casi sono controesempi autoriali, non risposte di provider simulati.

Ogni caso usa un nuovo checkpoint nel DB temporaneo. Il modello riceve il
messaggio, le domande attive e proposte non affidabili, mai gold o expected.
Solo i check SUPPORTED autorizzano la normale mutazione backend; provenienza
USER, nessun valore SOURCE inventato, nessuna promozione a RESOLVED.

Gold: conferme esplicitamente estese al gruppo di condizioni sono risposte;
le eccezioni locali prevalgono. Un generico sì a più condizioni resta ambiguo.
Una conferma di tutti i punti non fornisce email/date mai comunicate.
Citare un'azienda nelle fonti senza adottarla come partecipante non è conferma.
Parti incerte/estranee non autorizzano scritture e non invalidano parti valide.

Una sola serie per fase, tutti i casi in ordine. Massimo 16 chiamate per fase,
15 s e 768 token output/caso, nessun retry. Errori conservati come FAIL, niente
ripetizioni selettive. Raffronto invariato con guard-v1 (9) e Dialogo V1 (43).
