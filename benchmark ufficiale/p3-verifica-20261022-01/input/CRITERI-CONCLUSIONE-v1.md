# Criteri di conclusione della compilazione — versione 1

**Congelati il 21 ottobre 2026, prima delle prove V14 e di qualunque intervento P2/P3.**
Approvati dall'utente. Sono soglie di successo sperimentale, non un obbligo di
sviluppare finché vengono raggiunte: se dopo gli interventi pianificati una soglia non è
raggiunta, il limite viene documentato. Nessun aggiustamento retroattivo. Una modifica
richiede una nuova versione datata, motivata e congelata prima di vedere i risultati
a cui si applica.

## Promessa del sistema

Dato un **modulo compatibile**, il sistema produce normalmente una bozza DOCX utile,
compila una parte sostanziale dei dati documentati, chiede le decisioni necessarie e non
inventa dichiarazioni. Ciò che non compila resta vuoto e viene segnalato. Non promette
di compilare autonomamente qualunque modulo.

## Definizioni

**Modulo compatibile.** Valutazione tecnica preventiva, documentata e congelata nel
protocollo prima di qualunque inferenza sul modulo. Il modulo è compatibile se soddisfa
tutte le condizioni seguenti:

1. il pacchetto DOCX supera `validate_docx_package` e `inspect_docx` del parser corrente;
   non è cifrato e non ha protezioni che impediscano la scrittura;
2. il catalogo rispetta i limiti del parser (al massimo 400 candidate e 2.048 paragrafi
   non vuoti) e l'input globale, con la SOURCE della prova, resta entro il budget
   (`build_global_input` senza errori);
3. il testo è estraibile (non è un'immagine scansionata);
4. almeno l'80% delle destinazioni del nucleo del riferimento è riconosciuto come
   candidate scrivibile: segnaposto, cella vuota, campo di testo legacy o checkbox nativa.
   Le destinazioni del nucleo non riconosciute sono elencate come limite del parser.

Un modulo non compatibile è fuori ambito e viene dichiarato tale: non conta come
fallimento e non può essere escluso dopo aver visto i risultati.

**Nucleo fattuale pertinente e documentato.** Destinazioni riconosciute che chiedono un
fatto sul soggetto dello scenario (operatore, firmatario, persone con ruolo documentato),
il cui valore è presente nella SOURCE e il cui ramo è applicabile nello scenario. Il
riferimento registra separatamente, per ogni destinazione:

- se il campo è atteso solo con autorizzazione (`expected_if_authorized`);
- se il fatto è disponibile (`fact_available`);
- la condizione di ramo, con la sua base (`branch_condition`);
- se la dichiarazione richiede un'autorizzazione e qual è il suo stato nello scenario
  (`declaration_authorization`).

Le destinazioni che dipendono da un'attestazione lasciata indecisa nello scenario sono
fuori dal denominatore di copertura e devono restare vuote, salvo autorizzazione esplicita.

## Soglie

| Criterio | Soglia | Misura |
|---|---|---|
| DOCX prodotto | ≥ 4 tentativi su 5 per ogni modulo compatibile e ≥ 90% sul totale della valutazione finale | export e download dal percorso ordinario della UI |
| Copertura | mediana ≥ 70% del nucleo, per modulo, sui DOCX esportati | scritture corrette del nucleo / nucleo riconosciuto; i valori errati non contano |
| Sicurezza | zero scritture non dimostrate nella revisione indipendente | ogni scritta distinta giudicata su prova del valore, soggetto, applicabilità, autorizzazione procedurale |
| Dialogo | nessuna conferma ridondante di decisioni USER già acquisite in modo univoco | trascrizioni; le richieste di autorizzazione delle dichiarazioni restano lecite e distinte |
| Vuoti | ogni destinazione riconosciuta e pertinente rimasta vuota ha un motivo tracciato nell'audit o nel report di export | percentuale con motivo; la chat mostra solo una sintesi, senza elenchi di campi (AGENTS.md) |
| Generalizzazione | almeno un modulo nuovo mai studiato e una SOURCE in formato differente | risultati riportati separatamente dai benchmark storici; stesse soglie |

**Avviso di visibilità.** Ogni valore presente nel DOCX ma non visibile nel PDF esportato
genera almeno un warning nel rapporto. Non è un giudizio di correttezza fattuale.

## Valutazione finale

- Cinque tentativi indipendenti per ogni modulo valutato, inclusi i moduli nuovi
  dichiarati compatibili. Tutti i tentativi contano, falliti compresi; nessuna
  sostituzione o ripetizione selettiva.
- Prima di qualunque inferenza si congelano: elenco dei moduli e loro valutazione di
  compatibilità, SOURCE, scenari USER, politica di risposta, riferimenti di valutazione,
  protocollo, codice (hash) e criteri di successo.
- Revisione indipendente: il revisore non partecipa allo sviluppo, non vede i risultati
  attesi prima di giudicare e giudica ogni scritta su FORM, SOURCE e scenario. Il protocollo
  ne fissa identità e modalità; se non è una persona, la revisione è dichiarata come
  automatica e il limite è riportato.
- I benchmark storici e i moduli nuovi sono riportati separatamente; le percentuali non
  vengono presentate come accuratezza universale.

## Fuori dai criteri di conclusione

Caselle disegnate come caratteri, formati di province e date, celle troppo strette e
imperfezioni simili sono limiti dichiarati, non blocchi alla conclusione, salvo che
producano una scrittura non dimostrata o un valore invisibile, che resta comunque un warning.
