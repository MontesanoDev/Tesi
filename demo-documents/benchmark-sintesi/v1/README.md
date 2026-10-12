# Sintesi e contesto dei ruoli V1

Fixture congelata prima delle API. Sette audit/checkpoint, NON nuove analisi
SOURCE né sette compilazioni complete. Catanzaro e Labirinto riusano raw reali
archiviati e corpus con scope originali. Originali, SOURCE, raw e risposte USER
sono congelati; solo il JSON inviato alla sintesi e il suo task possono cambiare.
Gold e risultati attesi non entrano nel prompt. Fixture compilazione V1 invariata.

Il catalogo si ricostruisce con build_global_input, come nell'analisi vera:
anchor_paragraph_ids devono essere presenti. Il vecchio replay aveva ricostruito
solo il catalogo grezzo, causando form_context vuoto: errore harness dichiarato,
non prova di regressione applicativa. Non cancellare i vecchi esiti.

Controesempi autoriali generici: due ruoli distinti e un sottoscrittore omesso;
incarichi attuali, primo cessato, entrambi cessati, ruolo SOURCE diverso.
Il gate letterale può groundare un incarico storico: la revisione semantica deve
sospenderlo quando il FORM richiede l'attuale incaricato. Una fonte con un ruolo
diverso viene già esclusa dal validatore prima della sintesi. Nessuna keyword
specifica deve entrare nel codice. I numeri non sono intercambiabili fra soggetti.

Gold per la sintesi: proposte ammesse/escluse e presenza di domande al checkpoint
ancora condizionale. Campo omesso del sottoscrittore resta non analizzato, non è
un motivo per bloccare automaticamente i professionisti. Non certifica la
completezza semantica della narrazione libera, che va letta nel report.

BEFORE e AFTER: sette chiamate seriali ciascuno, timeout45s/output2048, nessun
retry o selezione degli output migliori. Errori registrati. Il provider reale è
DeepSeek Flash; nessun provider simulato. Mutazioni/renderer verificati a parte
con replay HTTP isolato. Nessun database/sessione live modificato.
