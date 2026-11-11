# Narratore: verifica circoscritta con DeepSeek reale — 31 ottobre 2026

**Esito: la modifica dei testi è promovibile nella demo assistita nel perimetro verificato.**
Non sono emerse regressioni attribuibili ai nuovi testi. Rimane un rifiuto della guardia su
un assenso breve alla condizione «IN QUALITÀ DI», riprodotto anche con il testo precedente.
Questo risultato non certifica affidabilità generale né elimina i limiti del prototipo.
Nessuna promozione, modifica applicativa, modifica alle autorizzazioni, merge, commit o push.

## Versione e istanze

- Worktree: `/home/montesano/tesi-narratore-chiarezza-20261031`.
- Branch: `narratore-chiarezza/2026-10-31`; HEAD testato
  `a0cc223bbad6355b57f10018119776c4696d893b`, fix `de2f5de`.
- Base: demo R2, tag `demo-default-r2-20261031` = `3a8de0b`; `ca58972` aggiunge la guida.
- Default verificato: `sezioni-2026-10-30-r2`. I checkpoint storici conservano i rispettivi
  profili: R2 per `minervino-v3-finale-1`, `sezioni-2026-10-30` per
  `minervino-v3-strutturale-1`. Nessun upgrade delle sessioni.
- `./start.sh` avviato nel worktree sulle porte **8001/5174**, lasciato attivo; installate le
  dipendenze frontend dal lockfile e sincronizzato il backend. Database e storage separati.
  L'avvio iniziale crea tre progetti dimostrativi, 14 file e zero sessioni: «vuoto» nel
  passaggio di consegne significava privo dei dati e delle sessioni dell'app ordinaria.
- Configurato un profilo DeepSeek separato con l'API ordinaria: credenziale letta in memoria
  dal profilo esistente, tramite letture SQLite senza scritture, e ricifrata nel nuovo DB.
  Nessuna credenziale nei rapporti o nei prompt acquisiti.
- Provenienza verificata: directory di worker Uvicorn/Vite, porte e ambiente selezionato,
  import dal worktree, hash dei due moduli identici al commit, proxy Vite verso il profilo
  isolato. Il passaggio HTTP reale ha effettivamente presentato la domanda nuova.
  `runtime-proof.json` conserva i riscontri. HEAD dell'app ordinaria resta `99ab052`:
  i due moduli ordinari risultano invece identici al tag demo, come atteso dal port selettivo.

## Protocollo e risultati

**13 chiamate reali a `deepseek-flash`: 10 alla guardia, 3 al router.**
350.299 token riportati dal provider; 31,88 secondi complessivi delle chiamate misurate
(non tempo dell'intervento né costo fatturato). Nessuna nuova analisi, ricerca SOURCE o
chiamata al modello narratore. Thinking disabilitato nelle richieste di guardia/routing.

Il materiale è quello già registrato nelle campagne, verificato senza cambiare FORM,
SOURCE, gold o originali. Le nuove domande sono ricostruite dal codice candidato; le vecchie
dal testo effettivamente registrato. I confronti conservano chiavi, destinazioni e contesto
FORM. I dati attesi e i gold non sono entrati nel prompt. È una verifica mirata su checkpoint,
non una nuova campagna né un collaudo completo da upload a bozza.

| Verifica | Prima | Dopo | Effetto controllato |
|---|---|---|---|
| Carica di Leonardo, 10 destinazioni, messaggio USER registrato | accettata | accettata | ricevuta USER valida; export 59 scritture, identico allo storico |
| Riga «Il sottoscritto …», 9 destinazioni, messaggio USER registrato | accettata | accettata | ricevuta USER valida; export 34 scritture, identico allo storico |
| Due designazioni, rinvio esplicito di entrambe | due `SKIP` | due `SKIP` | router reale, ruoli distinti; nessuna nuova autorizzazione a scrivere |
| Risposta non pertinente alla carica | — | `UNRELATED` | nessuna conferma autorizzata |
| Risposta incerta alla riga del sottoscritto | — | `AMBIGUOUS` | nessuna conferma autorizzata |
| Assenso breve alla sola domanda «IN QUALITÀ DI» | `AMBIGUOUS` | `AMBIGUOUS` | limite riprodotto anche con testo precedente |

Le quattro esportazioni comparative hanno lo stesso insieme di valori/caselle e sono
**identiche byte per byte** ai rispettivi DOCX storici, non soltanto uguali nei conteggi.
Le scritture includono quelle USER e le caselle già autorizzate nei checkpoint.
Non si tratta di 59 o 34 valori nuovamente estratti dal modello. Le ricevute accettate sono
persistite con provenienza USER e prova d'ambito; nessuna conferma accettata persa e nessuna
scrittura mancante nei confronti positivi.

La riga del sottoscritto produce inoltre il riepilogo deterministico atteso:
«Confermato: la parte del modulo «Il sottoscritto …, nato a … il …, residente».»
La generazione AI di una nuova sintesi non è stata eseguita. Le sintesi lunghe e le altre
regole di presentazione restano coperte dai test software e dal replay storico, non da nuove
misure di qualità del modello narratore.

### Limite osservato nel server reale

Una copia R2 è stata servita temporaneamente sulla porta 8002, con lo stesso codice e un
solo slot attivo, senza nuova analisi. Messaggio: «Sì, confermo che si applica: IN QUALITÀ DI.»
Il router ha proposto `answer_fields / CONDITION_TRUE`; la guardia ha risposto
`AMBIGUOUS / AMBIGUOUS`, interpretando la label come una scelta aperta di qualità.
Il backend ha chiesto chiarimento e non ha salvato la conferma. Non sono seguiti narratore
o export in questo passaggio HTTP. I risultati positivi di persistenza/export sopra sono
acquisizioni distinte, con guardia reale e API FastAPI su copie, non il proseguimento di
questo passaggio rifiutato.

Un solo ulteriore controllo, mantenendo contesto, risposta e destinazioni e ripristinando
il testo precedente, ha restituito ancora `AMBIGUOUS / AMBIGUOUS`. Nei messaggi storici
completi, invece, entrambi i testi passano. Il campione documenta un limite già riproducibile
con la formulazione precedente; non consente di stimarne la frequenza o attribuirne ogni
causa. Non è stato ritentato il caso nuovo per ottenere un esito migliore.

### Errori dello strumento di verifica, conservati

Non sono difetti dell'applicazione e non sono stati nascosti o contati come esiti positivi:

1. Prima di ogni chiamata: adattamento della lettura dei tavoli SQLite senza `rowid` e
   recupero degli slot completi dalla trascrizione, invece della proiezione di `turni.json`.
2. Il primo payload export includeva `provenance`, presente solo nel report: API 422.
   Corretto solo il payload e riusate le ricevute già acquisite, senza nuove chiamate.
3. Per la carica era stato usato l'intero messaggio come `user_quote`: la riconferma rendeva
   obsolete le ricevute di scelte successive legate all'estratto locale originario.
   Il 409 compariva in entrambi i bracci. Eseguite **solo due** nuove verifiche della guardia
   con l'esatto estratto originario, perché una prova d'ambito non può essere trasferita a
   una risposta diversa. Entrambi gli export da 59 scritture sono poi identici allo storico.
4. La prima lettura dopo l'export consultava il report dell'analisi anziché il download del
   report della bozza: corretto il lettore, nessuna chiamata AI aggiuntiva.
5. Pulizia del runtime HTTP interrotta da `VACUUM` nella transazione: completata offline,
   eliminando profili e chiave dalla copia prima dell'archivio. Il rifiuto reale resta acquisito.

## Verifiche e conservazione

- Rieseguiti **51 test software**, tutti passati: `test_narrator_clarity.py`,
  `test_signatory_order_and_extension.py`, `test_compilation_reply_guard.py`,
  `test_guard_verdicts_traced.py`. Questi usano provider simulati: distinti dalle 13 chiamate.
- Non rieseguiti suite completa, Ruff, build/frontend, browser, replay dei 90 run o benchmark
  fisso. I risultati precedenti rimangono quelli del [rapporto offline](narratore-chiarezza-2026-10-31.md).
- Nessun file applicativo differisce da HEAD; guardia, autorizzazioni e validatori invariati.
  Graphify aggiornato nel solo worktree, entro il perimetro AST locale.
- Hash logici dei dati e delle sessioni dell'app ordinaria, stato/diff Git ordinario e hash
  dei due run storici: **invariati** (`protected-before.json`, `protected-after.json`,
  `protected-check.json`). Le copie di test hanno database e storage propri.
- Nessuna migrazione o reindicizzazione necessaria. Server 8002 arrestato; 8000/5173 ordinari
  e 8001/5174 isolati restano distinti.

Acquisizioni durevoli, escluse da Git:
`backend/data/compilation-audit/narratore-deepseek-20261031/` nel worktree candidato.
Contengono protocollo, tutti i prompt/schema/risposte delle chiamate mirate, verdetti e
telemetria HTTP reali, log anche falliti, ricevute, report, DOCX, copie prive di credenziali,
riscontri di runtime, riepilogo e manifest SHA-256. Per il passaggio HTTP i prompt del router
sono nella traccia; il prompt della guardia è ricostruibile da codice/contesto e il suo
verdetto grezzo è registrato: il corpo HTTP completo della guardia non è stato intercettato.

Backup separato:
`/home/montesano/tesi-backups/narratore-deepseek-20261031/verifica.tar.gz`, con SHA-256 a fianco.
Non viene pubblicato con il solo push della documentazione.

Prossimo passo eventuale: integrare **solo** il fix dei testi nella demo, se richiesto.
L'analisi del rifiuto breve è un lavoro distinto, da discutere prima di cambiare la logica.
