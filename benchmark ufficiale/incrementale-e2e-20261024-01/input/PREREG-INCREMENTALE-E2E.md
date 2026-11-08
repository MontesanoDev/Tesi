# Campagna incrementale autorizzata — 24 ottobre 2026

Fonte: proposta approvata `docs/proposta-e2e-incrementale-2026-10-24.md`.
Massimo sei tentativi, 3.000.000 token complessivi, nessuna adozione.
Revisione Codex autoriale, NON indipendente. Nessuna inferenza prima del freeze.

Codice HEAD `4f007af3ce2ec3b1baee3e7b08d6442d204696fd`, runtime identico a
`3ec0af00e5088d14455f5da9e12acba0ebbbabbc`. Manifest in out/manifest-e2e.json:
code digest f883b1490462e78a1df47e867e80b3886d70ee85ccac8039c2e5b32e8a4239fd;
prompt digest f8460bca3dbd1cce55301f7a812818bd8a5fd5e0528fbca14e74f283936e98ff.
Hash dei prompt: AST delle stringhe lunghe e f-string, oltre agli hash di tutti
i file applicativi che congelano anche la costruzione dinamica.

Ordine fisso: catanzaro-1, minervino-1, soresa2023-1, cesano-1, catanzaro-2,
minervino-2. FORM, SOURCE, scenari, politica USER e riferimenti v3 identici alla
valutazione finale: due runtime nuovi, 22/14 frammenti SOURCE identici.
Nessun gold nel prompt. Un progetto/sessione nuovo per tentativo; il modulo
ripetuto non riusa sessione, decisioni o cache applicativa dell'altro tentativo.
La cache del provider non è controllabile e viene misurata quando disponibile.

Profilo: backend 13, V14=1, K3=1, derivation=1, dialogue=1, generation=3,
narration_recovery=1, branch_scope=1, table_scope=1, hold_rereview=2.
Provider deepseek, modello richiesto deepseek-flash, configurazione come nello
sprint. Documentazione ufficiale consultata il 24 ottobre: alias associato a
DeepSeek-V4.1-Flash-1017. Registrare modello/fingerprint realmente restituiti;
l'alias non garantisce una versione immutabile del servizio.

Esercizio atteso, non garantito dal comportamento del modello:
- Catanzaro: sezione condizionale 5.c, controllo delle tabelle, cinque negativi.
- Minervino: opzioni/continuazioni, soci/tecnici e rilettura dei dubbi SOURCE.
- So.Re.Sa.: RT e avvalimento; tredici negativi ancora non chiusi deterministicamente.
- Cesano: controllo di preservazione e regressione su modulo diverso.
La mancata proposta di un campo rischioso non dimostra l'efficacia del veto.

Interruzione prevista solo in minervino-2: il wrapper arresta il processo con
exit 88 quando il primo segmento è già validato e persistito, prima di inoltrare
la chiamata del successivo. Salva hash della cache e stato del ledger. Il
supervisore riavvia una sola volta quel runtime. Il browser aspetta la naturale
scadenza del lease (massimo 2050 secondi), poi invia una sola volta «Riprendi la
compilazione interrotta.» nella stessa sessione. Nessuna modifica del database
per eliminare il lease e nessun nuovo tentativo. La latenza include l'attesa;
se la ripresa non riesce, registrare il fallimento, senza seconda ripresa.
Gli altri cinque tentativi non subiscono guasti iniettati.

Retry applicativi invariati: uno per segmento, due per analisi; recupero della
sintesi secondo il codice congelato. Quattro giri USER, un export per tentativo,
60 chiamate massimo per tentativo. Tutte le chiamate, retry e riprese contano.
Budget atomico tra i runtime: input stimato come caratteri JSON × 0,40 + 1024,
più massimo output configurato, reasoning incluso senza doppio conteggio.
Nel precedente sprint il massimo osservato è 0,30115 token input/carattere su
89 chiamate. Non è un limite matematico: se il provider supera la prenotazione,
arresto di integrità; nessuna chiamata nuova senza budget residuo sufficiente.
Token ignoti o chiamate interrotte restano addebitati alla prenotazione.
Soglie conservative di avvio: Catanzaro 750k, Minervino 700k, altri 300k.

Congelare tariffe e input prima dell'apertura del gate. Sabato: fascia off-peak
secondo la documentazione ufficiale, 0,003 / 0,15 / 0,60 USD per milione per
cache hit / miss / output. Costo stimato da usage, non fattura.

Prima di ogni inoltro: progetto e gate del solo tentativo corrente, hash del
codice e harness/input, flag persistiti, richiesta di segmento prevista,
limiti di chiamate e prenotazione comune. Stop alla prima scrittura non
dimostrata accertata, aggiramento di gate o problema d'integrità. Nessun
cambiamento a codice/prompt/criteri durante la campagna. Nessuna sostituzione.

Revisione di ogni scrittura su dato, soggetto/ruolo, ramo e consenso prima del
tentativo successivo. Distinguere DIMOSTRATA, DUBBIA, NON_DIMOSTRATA; un dubbio
non risolto dalle evidenze disponibili sospende ulteriori tentativi e non è
presentato come errore certo. I 25 ID storici da soli non sono un veto.
Tentativi non eseguiti restano nel denominatore sei.

Misure: DOCX prodotti; giudizi per scrittura; rami sbagliati; proposte effettivamente
bloccate dal controllo tabelle; hold SOURCE marcati, riesaminati, rilasciati,
risospesi e scritti; nuove omissioni/falsi rifiuti; copertura v3 per modulo;
segmenti falliti/cache/retry; token input/output/reasoning/cache/ignoti, costo e
latenza. Comparazioni descrittive non appaiate; cinque DOCX su sei è soltanto
un segnale di disponibilità, mai certificazione del 70% o superiorità generale.

App ordinaria, sessioni e campagne precedenti: fingerprint prima/dopo. Porte
8040/8041 e 5210/5211, nessun riavvio o flag nell'app ordinaria. Backup separato
senza chiavi o database, rapporto conclusivo e arresto senza altri sprint.

Controllo degli strumenti prima della prima chiamata: il conteggio dei vuoti
filtra già gli ID reali del catalogo e viene esteso, solo nel nuovo harness,
alla motivazione del veto tabelle. I giudizi DUBBIA sono registrati separatamente.
Nessuna correzione retroattiva delle analisi storiche.
