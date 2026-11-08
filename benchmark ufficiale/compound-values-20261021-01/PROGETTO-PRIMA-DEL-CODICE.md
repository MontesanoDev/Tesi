# Decisione prima del codice applicativo — 21 ottobre 2026

Riprodotto il DOCX UI originale byte per byte: numero 01234560981 grounded,
requisito FORM p441 «numero e data d'iscrizione», destinazione t25.r3.c1/p442.
Condizione MODEL c_soc_ing UNKNOWN, ricevuta USER esplicita valida; il numero
viene scritto perché manca una dimensione indipendente di completezza.

Contratto attuale: SharedFact.value stringa, massimo due citazioni; ogni
citazione deve contenere **l'intero valore** (source_span), e il validatore DOCX
lo ricontrolla. Due citazioni non rappresentano componenti assemblabili. Non si
modificano schema, prompt, modello, parser, writer, SOURCE, condizioni o binding.

Scelta minima: nuovo audit backend per le richieste composte fisicamente
ancorate, con COMPLETE/INCOMPLETE/UNKNOWN. Riconoscimento tramite grammatica
limitata e dichiarata, non split di qualsiasi e/slash/virgola. Famiglie da
verificare: numero+data/anno e riferimenti d'iscrizione, luogo+data (nascita o
atto della pratica), identità nome/cognome, componenti esplicite dell'indirizzo,
qualificatori richiesti e richieste aperte/ambigue. Slot separati non sono un
singolo valore composto. Le etichette descrittive non diventano liste di proprietà.

Un'etichetta con alternativa esplicita non richiede entrambe le alternative.
Se la coordinazione fra proprietà distinte è ambigua, un solo componente non
viene promosso a COMPLETE per convenienza. «Cellulare + Telefono» va inventariato
come ambiguo, distinto sia da un requisito cumulativo certo sia da una singola
proprietà; la precedente valutazione autoriale accettava il telefono, ma non è
prova FORM che l'altro componente sia facoltativo. Ogni eventuale esclusione
conservativa verrà mostrata come UNKNOWN, senza cambiare il gold precedente.
«Ordine/Collegio» e le alternative di ruolo non sono automaticamente cumulativi.

La presenza di componenti deve essere documentata dalla provenienza già
verificata, sullo stesso valore/record, non da fatti di altri soggetti o altre
iscrizioni. Completezza non sostituisce grounding, binding, applicabilità o
consenso. Nessun valore viene sintetizzato. Normalizzazioni di date/formati
servono a riconoscere i componenti, senza allentare source_span per tutti i campi.

Composizione multi-span NON implementata. Alternativa minima da discutere in una
fase separata, se necessaria: componenti tipizzati con subject, property,
source_span/offset e record_key attestata nel SOURCE, più una composizione
esplicita/limitata. Servirebbero adattatori coordinati del contratto fatti,
validator, riuso, revisione ed export; aggiungere soltanto una lista di quote
rischierebbe unioni fra iscrizioni e soggetti. Schema proposto, non attivo:

```json
{"value":"<numero> del <data>","subject":"<soggetto>",
 "components":[
  {"property":"registration_number","value":"<numero>",
   "source":{"chunk_id":0,"quote":"<span reale>"},"record_key":"<chiave SOURCE>"},
  {"property":"registration_date","value":"<data>",
   "source":{"chunk_id":0,"quote":"<span reale>"},"record_key":"<stessa chiave SOURCE>"}],
 "composition":{"operator":"registration_number_date","record_key":"<chiave SOURCE>"}}
```

Una chiave dichiarata solo dal modello non sarebbe una prova. Anche più span
nello stesso record rimangono sotto il grounding attuale quando il valore
assemblato non è contiguo. Il limite sarà dichiarato, senza concatenazioni.

Verifiche: fixture originale, positivi/negativi/avversariali e API persistenti,
software completo e Ruff; 69 replay di export e 213 validator prima/dopo,
JSON di ogni delta e classificazione atteso/regressione. Precedenti fix vincoli
applicabilità e relazioni tabellari conservati. Poi una nuova prova UI reale con
scenario preregistrato e configurazione B0 invariata, download, XML e PDF;
confronto sulla stessa risposta ove possibile. Backup estratto offline.

Baseline software nello snapshot tentata ma due test richiedono fixture esterne
alla copia backend: errore del solo harness, log conservato. Baseline completa
rieseguita nel working tree ancora immutato, con storage/database temporanei.
Nessuna mutazione dei benchmark originali o dei dati live.
