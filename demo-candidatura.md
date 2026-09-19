# Demo concettuale della candidatura

Percorso nel frontend: `/demo/candidatura`.
Server della sessione: http://127.0.0.1:5174/demo/candidatura
La porta puo cambiare al riavvio; il percorso rimane lo stesso.

## Presentazione in due minuti

Premessa da dire ai relatori:
> Questa e una proposta di interazione, non una dimostrazione della compilazione automatica di documenti ufficiali. Serve a discutere il flusso prima di implementarlo.

1. Premi **Usa modello dimostrativo**. In alternativa seleziona un PDF/DOCX: nella demo viene utilizzato soltanto il nome, non il contenuto.
2. Premi **Simula compilazione**: il facsimile mostra tre valori fittizi e due dati mancanti.
3. Apri **Revisiona bozza**: modifica un valore e completa responsabile e importo, ad esempio `Referente della demo` e `450000`.
4. Conferma il controllo dei dati e vai all'esportazione.
5. Scarica il facsimile HTML oppure usa **Stampa / PDF** per aprire la stampa del browser. Non viene compilato il PDF/DOCX selezionato.

Il pulsante con la freccia circolare riporta la demo allo stato iniziale.

## Confini della simulazione

- Nessuna chiamata al backend o al modello, nessuna lettura del contenuto dei file.
- Fonti e valori sono esempi, non risultati del retrieval sulle KB reali.
- Nessun salvataggio nei progetti o nelle KB; al ricaricamento i dati della demo si perdono.
- Call Facts, template e draft dell'applicazione esistente non vengono modificati dalla demo.
- La conferma riguarda il facsimile: non implica la scelta di mantenere la verifica manuale dei Call Facts.
- L'export funziona per questo facsimile HTML; parsing, associazione dei campi e compilazione del modello originale restano da implementare.

## Decisioni da discutere

- Il risultato atteso e un testo di supporto o un allegato ufficiale compilato?
- Quale formato e quale famiglia di modelli supportare per primi?
- Quali dati proporre automaticamente, con quali fonti, e quali lasciare alla revisione dell'utente?

Questa demo non misura la qualita del RAG: confronto tra FTS5, dense e hybrid e relativa validazione rimangono un'attivita separata.
