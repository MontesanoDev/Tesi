# Candidata completa — verifica esplorativa, 23 ottobre 2026

Preregistrazione precedente alle nuove inferenze. Otto tentativi previsti, nessuna
adozione automatica, nessuna modifica di codice applicativo o prompt durante la prova.
V12 e tutti gli esperimenti precedenti rimangono immutati. L'autore delle correzioni
esegue anche la revisione: NON è una revisione indipendente.

## Candidata e base della verifica

Flag: backend 13, V14 1, K3 1, dialogue 1, derivation 1, generation 3,
narration_recovery 1. Runtime separati su 8020/5190 e 8021/5191. Nessun cambio del
runtime ordinario. Codice fotografato e verificato prima di ogni chiamata provider.
La suite del passo 3 è già conclusa: 3640 PASS e Ruff PASS. Non è una nuova misura
di qualità LLM. Si verificano ora insieme i tre passi documentati in docs/.

Ordine fisso: minervino-1, catanzaro-1, cesano-1, soresa2023-1,
minervino-2, catanzaro-2, cesano-2, soresa2023-2. Scenari, FORM, SOURCE, politica
USER e riferimenti v3 sono quelli della valutazione finale congelata. Minervino,
Catanzaro e Cesano usano SOURCE storiche; So.Re.Sa. la SOURCE PDF tabellare.
Nessun gold nei prompt. Modello configurato nei semi, deepseek-flash; parametri
del codice invariati. Richieste dei segmenti precalcolate con revision=3.

Procedura UI reale: mention del FORM, richiesta iniziale congelata, massimo
quattro risposte secondo la politica congelata, richiesta esplicita di bozza e
download. Nessuna risposta aggiuntiva adattata all'esito, nessun mock nel browser.
Un tentativo per processo del driver permette la revisione prima del successivo.
I tentativi non vengono ripetuti. Tutti gli otto restano nel denominatore.

## Budget e retry

Tetto vincolante 3.000.000 token, per tutte le chiamate: segmenti, registro,
narratore, guard e planner, reasoning incluso. Stime attese per avvio: Minervino
480k, Catanzaro 430k, Cesano 180k, So.Re.Sa. 180k; avvio soltanto con residuo almeno
doppio della stima. Stime prudenti da costi storici e aumento input del passo 2;
non sono token misurati e non garantiscono di completare gli otto tentativi.

Prima di OGNI chiamata: prenotazione atomica fra processi nel ledger comune,
pari ai byte UTF-8 del JSON della richiesta + 4096 token di margine + max_tokens
di output completo. Nessuno sconto per cache. Consumi noti sostituiscono la
prenotazione; consumi ignoti conservano l'intera prenotazione. Chiamate rifiutate
non vengono inoltrate. Un consumo superiore alla prenotazione arresta gli avvii
successivi. È un limite prudente di campagna, non un tokenizer certificato.
Separare sempre consumi misurati da importi prudenzialmente impegnati.

Solo retry già nel codice: uno per segmento, due per analisi; un retry per
episodio del narratore, stessi input. Massimo 60 chiamate per tentativo; analisi
entro numero segmenti + 2. Ogni chiamata e retry resta nello stesso tentativo.
Nessuna ripresa qualitativa manuale o sostituzione di un fallimento.

## Controlli della strumentazione prima dell'apertura del gate

Verificare contabilizzazione concorrente, risposta senza usage, errore di
trasporto, rifiuto prima dell'inoltro, crash con prenotazione pendente. Verificare
che corpus e FORM siano identici, che tutti i flag siano persistiti, che ogni
richiesta di segmento abbia il FORM completo e soltanto candidate proprietarie.
Contare scritture su ID reali del catalogo; i vuoti descrittivi non sono campi.
L'analisi automatica riusa il criterio v3 storico; ogni scrittura viene comunque
revisionata su valore, soggetto, applicabilità e consenso, anche se il confronto
automatico la considera corretta. Verificare il DOCX effettivo contro il report.

## Misure, arresto e decisione

Per tentativo: DOCX prodotto/scaricato, copertura del nucleo corretta e parziale,
vuoti e motivazioni effettive, condizioni e autorizzazioni, decisioni ripetute,
segmenti analizzati/falliti/preservati, retry, ripresa osservata, errori narratore
e fallback, HTTP 409 e causa. Per chiamata: input/output/reasoning/cache quando
disponibili, latenza, uso noto o ignoto. Il costo è stimato con pricing storico
congelato, non certificato come tariffa attuale. Se una metrica manca è ignota.

Revisione autoriale prima del tentativo successivo. Arresto immediato davanti a
scrittura non dimostrata, SOURCE in destinazione non accertata senza catena
indipendente, veto di stato derivato incoerente o difetto grave del nuovo backend.
Non cambiare codice né prompt per proseguire. Conservare anche il tentativo che
ha fatto scattare lo stop e gli altri come non eseguiti, distinguendo motivo
sicurezza, budget o infrastruttura. Se il problema è soltanto infrastrutturale,
non chiamarlo regressione del modello; il tentativo non viene sostituito.

Esito favorevole significa soltanto idoneità a ulteriori valutazioni. Otto
tentativi non certificano le soglie congelate. Il confronto con 32/35 monolitici
e con 7/8 rev 2 è descrittivo, non appaiato; usare gli stessi quattro moduli per
confronti di copertura/costo e non confondere 423 scritture su sette moduli con
271 scritture monolitiche sui quattro moduli condivisi. Nessun obbligo di 70%.

Congelare protocollo, file, strumenti, test e hash prima delle inferenze. Nessun
segreto in report o backup; i runtime con DB e credenziali sono esclusi dal backup.
Rapporto conclusivo, aggiornamento STATUS e relazioni, backup verificato; poi stop.
