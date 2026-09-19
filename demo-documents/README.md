# Documenti dimostrativi

`visura-mapi-ingegneria-simulata.pdf` e un fac-simile testuale da caricare nella
sezione `Company KB`. Contiene esclusivamente dati inventati per la demo e non ha
valore camerale o amministrativo.

Il file HTML con lo stesso nome e il sorgente usato per generare il PDF e non va
caricato nell'applicazione.

[generalita-mapi.md](generalita-mapi.md) e una scheda aziendale testuale piu'
completa, pronta per la **Company KB**, con gli stessi dati societari della
visura simulata. Distingue Luca Ferri (amministratore), Elisa Romano (direttore
tecnico), Andrea Greco (qualita') e Mario Rossi (referente organizzativo dello
scenario demo, aggiunto nella scheda). Non inventa dati personali mancanti o
scelte di partecipazione. Per sostituire il profilo iniziale di poche righe,
aggiornare quel documento nella Company KB, evitando copie obsolete.
La creazione del file nel repository non lo carica automaticamente nell'app.

La directory `general-kb/` contiene un corpus tecnico dimostrativo in formato
TXT, pronto per essere caricato nella sezione `General KB`. I documenti sono
trasversali ai progetti e coerenti con gli ambiti operativi della societa
simulata, ma non contengono dati identificativi di Mapi Ingegneria.

La directory [bandi/catanzaro-dl-cse](bandi/catanzaro-dl-cse/README.md) contiene
un caso storico reale per preparare la compilazione assistita di una domanda:
bando e disciplinare originali, modulo Word convertito e mappa dei campi
confrontata con la visura simulata. Non e una candidatura pronta da inviare.

La directory [bandi/minervino-elenco-sia](bandi/minervino-elenco-sia/README.md)
contiene un secondo caso esplorativo: avviso e domanda DOCX nativa del Comune
di Minervino di Lecce, con campi soprattutto nei paragrafi. La prova usa il
compilatore invariato e documenta anche rami errati e recapiti malformati;
non e un benchmark o una candidatura pronta.

`modelli/modulo-paragrafi.docx` e un modello sintetico con segnaposti nei paragrafi
e celle vuote. Si carica da **Template > Word (.docx)**, non nella KB. Contiene
anche campi personali mancanti e una firma da lasciare vuota; serve a provare
il flusso misto, non a presentare una domanda reale. Il sorgente riproducibile
e `backend/scripts/create_paragraph_template.py`.
