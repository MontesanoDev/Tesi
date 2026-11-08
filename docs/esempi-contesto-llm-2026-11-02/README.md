# Che cosa riceve l'LLM durante la compilazione DOCX

Materiale illustrativo preparato il **2 novembre 2026**. Nessuna nuova chiamata AI.

Aprire prima **[00_PRESENTAZIONE.json](00_PRESENTAZIONE.json)**: raccoglie in un solo
file gli esempi essenziali di analisi, narratore, router, guardia ed export.
Gli altri file permettono di approfondire un passaggio alla volta.

Ogni chiamata ha un contesto costruito dal backend per uno specifico compito.
La memoria della compilazione è nello stato persistente del backend: il modello
riceve soltanto la parte che viene inserita in quella richiesta. Una cronologia
conversazionale non diventa automaticamente una fonte fattuale.

## La distinzione da mostrare

| Blocco | Che cosa rappresenta | Esempio |
|---|---|---|
| **Istruzioni / system** | Compito, limiti e contratto dell'output | Proponi valori documentati; non inventare dati |
| **FORM** | Richieste e struttura del modulo | «Il sottoscritto …», clausole, paragrafi, campi e checkbox |
| **SOURCE / sources** | Documenti che sostengono i fatti | Società, sede, anagrafica e ruoli documentati |
| **USER** | Messaggi, dati e decisioni dell'utente | Chi sottoscrive; quale ramo applicare; rinvii |
| **Stato backend** | Proposte validate, condizioni, ricevute e slot attivi | Questo valore attende la conferma d'identità |

Un campo stampato nel FORM non prova il relativo fatto. Una SOURCE non sostituisce
una scelta dell'utente. Una risposta a un campo non autorizza tutti gli altri.

## Il contesto cambia a ogni passaggio

| Passaggio | Input del modello | Output richiesto | File |
|---|---|---|---|
| Router di avvio | Richiesta, cronologia, inventario e FORM selezionato | Intento e riferimento al modulo | [00A](00A_router_avvio_SCHEMA.json) |
| Analisi di un segmento | FORM completo, corpus SOURCE preparato, contesto USER, schema e destinazioni assegnate | Fatti, condizioni, assegnazioni e copertura | [01](01_analisi_segmento.json) |
| Recupero mirato, se necessario | Stesso contesto generale, poche destinazioni respinte e motivi del rifiuto | Nuove proposte soltanto per quelle destinazioni | [02](02_recupero_mirato.json) |
| Decisioni nella richiesta iniziale | Messaggio iniziale e slot ricavati dopo l'analisi | Sole risposte già esplicite nel messaggio | [03](03_decisioni_richiesta_iniziale.json) |
| Narratore iniziale | Copertura e pool di domande; eventuali proposte revisionabili | Riepilogo, domande e sospensioni motivate | [04](04_narratore_primo_riepilogo.json) |
| Narratore che rivede proposte | Finestra di proposte validate, estratti SOURCE, contesti di ruolo/applicabilità e risposte precedenti | Domande e dubbi motivati sulle proposte | [05](05_narratore_revisione_proposte.json) |
| Router di una risposta | Messaggio USER, domande e slot attivi, cronologia pertinente | Associazione tra risposta e slot | [06](06_router_risposta_USER.json) |
| Guardia | Messaggio, domande, proposte del router, FORM e destinazioni precise | Pertinenza e ambito di ogni proposta | [07](07_guardia_nome_e_ramo.json) |
| Guardia sui dati aggiuntivi | Dati separati dal backend e rispettive destinazioni FORM | Controllo indipendente di ciascun dato | [08](08_guardia_dati_atomici.json) |
| Conferme esplicite | Domande di applicabilità/identità e risposte USER | Proposte del router e verifiche della guardia | [09](09_conferme_esplicite.json) |
| Export | Stato e ricevute già verificati | DOCX e report, **senza chiamata LLM** | [10](10_export_senza_LLM.json) |
| Narratore dopo risposte USER | Stato aggiornato, valori USER e nuove proposte da rivedere | Prosecuzione del dialogo | [11](11_narratore_dopo_risposte_USER.json) |

Il file 11 mostra un contesto di prosecuzione che precede l'export, anche se è
numerato dopo il file 10 per consentire il confronto con gli altri narratori.
Il ciclo normale ritorna al narratore dopo gli aggiornamenti USER; l'export avviene
solo su richiesta esplicita. La selezione del FORM e l'inventario delle posizioni,
la validazione, l'estrazione multivalore, la persistenza e la scrittura Word sono
operazioni backend, non ulteriori richieste al modello.

## Quanto contesto viene passato davvero

- Nell'analisi Minervino registrata: **267 posizioni**, distribuite in cinque
  segmenti di **59, 54, 60, 60 e 34** destinazioni. Il segmento 1 riceve tutti i
  **134 blocchi FORM** e tutti i **56 frammenti SOURCE** preparati per l'analisi,
  con responsabilità sulle proprie 59 destinazioni. Gli esempi ne mostrano poche.
- Il narratore riceve fino a **40 proposte per finestra**, i loro contesti e le
  prove selezionate. Può porre fino a **quattro domande**. Non riceve nuovamente
  tutto il corpus come nella chiamata di analisi.
- Il router di risposta riceve contesto conversazionale e slot attivi. In questo
  percorso non riceve il FORM completo o il corpus SOURCE.
- La guardia di questo profilo riceve il FORM completo e gli ambiti delle
  destinazioni, oltre al messaggio e alle proposte da controllare. Non riceve il
  corpus SOURCE. I dati multivalore aggiuntivi sono verificati in gruppi di massimo
  quattro: nel caso mostrato, due gruppi di quattro e due dati.

Questi sono input testuali/JSON, non i byte ZIP del DOCX. Il backend estrae testo,
struttura e identificatori prima di costruire la richiesta.

## Come leggere i JSON abbreviati

- `_guida`, `parametri`, `messaggi_decodificati` e `input_ridotto` sono contenitori
  redazionali: **non sono nuovi campi del protocollo applicativo**.
- Nei blocchi `content_json` sono mantenuti i nomi dei campi originali, per esempio
  `form`, `sources`, `document_values`, `question_pool`, `proposals` e `form_scope`.
- Sono omessi record, schemi completi, contatori di dettaglio e metadati ripetitivi.
  Gli identificatori dei record selezionati mantengono la numerazione originale:
  alcuni riferimenti puntano quindi a parti intenzionalmente non riprodotte.
- Le istruzioni sono estratti, non il prompt completo. I testi accorciati portano
  un marcatore; il contenuto delle SOURCE è talvolta limitato alle citazioni usate.
- Le risposte mostrate sono proiezioni di output reali; una sospensione proposta
  dal narratore è un giudizio da verificare, non un verdetto fattuale certificato.
- Il file **00A** è una ricostruzione illustrativa esplicitamente marcata: non
  abbiamo usato una trascrizione acquisita per il router di avvio.
- Per vedere la serializzazione reale aprire
  **[99_formato_API_con_content_stringa.json](99_formato_API_con_content_stringa.json)**:
  `messages[].content` è una stringa, anche quando contiene JSON. Il contenuto è
  ridotto; la forma del body API e lo schema di risposta della guardia sono conservati.

## Provenienza e limiti

Gli esempi usano lo stesso FORM Minervino in **checkpoint diversi**, non una singola
trascrizione lineare: analisi e narratore dalla prova del 31 ottobre su `a0cc223`;
router e guardie dal replay reale del 1 novembre su `930aeef`. I messaggi di conferma
del file 09 sono risposte USER esplicite **di prova**, non risposte della conversazione
storica. I dati aziendali/personali provengono dal materiale dimostrativo del progetto.

Il file 10 conserva l'esito reale di **sette scritture**, non nove. Il file 11
contiene una richiesta reale che ha ricevuto HTTP 402: non è stato inventato un
output riuscito. La cartella illustra il contesto passato al modello e non costituisce
un nuovo benchmark o una dichiarazione di completamento della verifica precedente.

Originali, versioni, trasformazioni e SHA-256 sono elencati in
**[PROVENIENZA.json](PROVENIENZA.json)**. Gli originali locali sono esclusi da Git;
il backup separato della cartella e delle acquisizioni selezionate è in
`/home/montesano/tesi-backups/esempi-contesto-llm-20261102/`.

Codice applicativo, demo, SOURCE e sessioni non sono stati modificati. Per questa
preparazione non sono state eseguite chiamate DeepSeek.
