# B0 — misura preliminare dell'input attuale

**16 ottobre 2026. Acquisizione offline, zero chiamate provider.**

L'utente chiede se occorra misurare il sistema prima di E1/E2. La baseline
B0 di qualità resta da eseguire. Questa acquisizione misura l'input realmente
costruito dal codice attuale e controlla configurazione e corrispondenza dei
materiali, senza modificare il motore o confondere dimensioni e qualità.

## Input ricostruito

Codice: 99ab052, tag baseline-minervino-v1-20261016. Progetto locale
minervino-di-lecce-elenco-sia, modulo 156. Originale e cinque file SOURCE
coincidono con Minervino V1; tutti i 18 hash del manifest della fixture sono
conformi. Riutilizzati i 56 chunk già indicizzati, senza nuova ingestion.
L'input usa il catalogo attuale e non include il gold o le sue annotazioni.

| Misura | Valore |
|---|---:|
| Destinazioni nel catalogo | 267 |
| Destinazioni classificate text dal catalogo | 254, incluse 67 celle di preferenza |
| Checkbox native | 13 |
| Documenti SOURCE / chunk | 5 / 56 |
| JSON input già serializzato senza indentazione | 240.276 caratteri |
| JSON input in UTF-8 | 242.959 byte |
| FORM nel JSON | 126.928 caratteri |
| SOURCE con metadati nel JSON | 75.735 caratteri |
| Testo dei chunk SOURCE | 63.655 caratteri |
| Reading plan nel JSON | 25.670 caratteri |
| Schema output nel JSON | 11.701 caratteri |
| System prompt | 24.675 caratteri |
| Totale dei contenuti dei messaggi della richiesta | 264.951 caratteri |

I conteggi delle componenti includono la loro serializzazione; non sono una
stima di token. Non è acquisito usage del provider né costo, tempo LLM o score.
Il catalogo copre le stesse 267 destinazioni numeriche del gold, ma questo
non verifica comprensione dei campi, proposta o correttezza della scrittura.

## Configurazione effettiva e correzione della prima ipotesi

Il progetto seleziona deepseek-flash, preferenza thinking disattivata e
context_window salvato pari a 32768. Quest'ultimo è metadato locale, non una
misura della finestra realmente accettata dal provider.

L'analisi globale in [resolve_global](../backend/app/compilation_global_sessions.py:215)
chiama invece global_request con thinking attivo per il provider DeepSeek,
indipendentemente dalla preferenza del progetto. La richiesta fedele B0
mantiene quel comportamento e reasoning_effort low. Disattivarlo sarebbe
una variante distinta, non la misura del sistema corrente.

La prima ricostruzione seguiva erroneamente la preferenza del progetto:
request e summary sono conservati nella directory raw
incorrect-profile-thinking-assumption/. Nessuna delle due richieste è stata
inviata a un provider. Un primo avvio dello script senza PYTHONPATH non trovava
app; avvio corretto dall'ambiente backend e ricostruzione finale riusciti.

## Misure ancora necessarie

Per E1/E2 serve B0 sulla proposta globale e sulla validazione, con input
completo congelato: tre run indipendenti a configurazione fissata, conservando
anche fallimenti, response grezza, usage e tutti gli esiti. Confrontare con il
gold i valori SOURCE, soggetto/ruolo/destinazione, condizioni, omissioni e rifiuti.

Il runner benchmark_compilation_global.py può acquisire proposta e validazione
dal progetto, ma il suo scoring fixture non è compatibile automaticamente con
Minervino V1. Non cambiare il gold per adattarlo al runner. Il percorso
--project/--form-id richiede una verifica del corpus prima di ogni serie,
poiché legge le fonti autorizzate esistenti anziché importare la fixture.

Domande, risposte USER, persistenza ed export richiedono una misura integrata
separata. Il runner precedente non le esercita; neppure la misura della sola
risoluzione automatica di benchmark_compilation_latency.py copre dialogo e Word.
Ogni report deve dichiarare quali fasi sono state realmente eseguite.

## Acquisizioni

[Misure](benchmarks/2026-10-16-b0-preflight.json),
[bundle](benchmarks/2026-10-16-b0-preflight-audit.tar.gz),
[checksum](benchmarks/2026-10-16-b0-preflight-audit.tar.gz.sha256).
Raw backend/data/compilation-audit/b0-preflight-20261016-01/.
Bundle 19 file, 264.115 byte, SHA-256
`4052f21914593c951f8f8f701486078530fb36f3e5d3bdecd6c2e8dd00918f25`.
Conservati input/request/schema, originale, script eseguito, codice pertinente,
misure, note sui tentativi e manifest; nessun DB o credenziale esportato.

Nessuna chiamata provider, nuova sessione, bozza, modifica a codice applicativo,
DB/KB o fixture. Verificati manifest, riferimenti e diff; nessuna suite
applicativa eseguita. Le dimensioni dell'input sono misurate; la baseline di
qualità, i token effettivi e il percorso completo restano da acquisire.
