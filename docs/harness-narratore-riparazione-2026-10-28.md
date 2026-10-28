# Riparazione dell'harness di audit del narratore — 28 ottobre 2026

Revisione **AUTORIALE**, non indipendente. Solo strumentazione: nessuna nuova
inferenza DeepSeek, modifica del compilatore, attivazione nell'app, merge o push.

L'harness supera il collaudo offline del trasporto e del percorso browser/API.
Questo non valida la qualità del narratore, una compilazione Minervino completa,
la latenza reale del provider o la fatturazione. Il nuovo tentativo richiede una
nuova autorizzazione; la proposta è in
[proposta-nuovo-audit-narratore-2026-10-28.md](proposta-nuovo-audit-narratore-2026-10-28.md).

## Versioni e isolamento

- Branch: `fix/2026-10-28-harness-narratore`.
- Worktree: `/home/montesano/tesi-harness-narratore-20261028`.
- Candidata: `7b31d25930c52504e0a1461491bde3fd23ca3a0e`, con fix ruolo `f3bc281`
  e correzioni precedenti. Nessun diff in `backend/`, `frontend/`, fixture e benchmark
  rispetto alla candidata; i nuovi dati sono nella directory locale ignorata da Git.
- Base documentale: `3f97a59f52aebcdb56ca0ec7dc38e88a7e511536`.
- Strumentazione collaudata: `4fc0377` e relativi antenati elencati sotto.
- App ordinaria su `prune-backend` non modificata né riavviata. Le numerose
  modifiche preesistenti del checkout ordinario sono state lasciate intatte.
- Cinque database nuovi con progetto sintetico e credenziale fittizia, sotto
  `backend/data/compilation-audit/harness-repair-20261028-01/preflight-02/`.
  Nessuna sessione reale o documento aziendale copiato nel collaudo.
- Servizi di test su 15174/18081 arrestati al termine; porte verificate libere.

Il tentativo precedente resta un **fallimento infrastrutturale**. Tutti i suoi
64 file acquisiti all'inizio della riparazione e tutti i 159 hash del suo freeze
sono invariati. Verificati anche i backup precedenti, 19 e 65 file, senza difformità.
Questa verifica riguarda gli artefatti congelati: non è un nuovo censimento con
hash dell'intero database live ordinario, che non è stato usato per il collaudo.

## Causa HTTPX verificata

Stack originale conservato in `narratore-minervino-20261028-01/server.log`, righe
91–112: `observed` entra nel trasporto applicativo, poi `send_checked` esegue
`assert not kwargs.get('follow_redirects', False)`.

HTTPX 0.28.1 passa `USE_CLIENT_DEFAULT` per indicare «usa il valore del client».
L'oggetto è truthy anche quando `client.follow_redirects` è False. L'assert falliva
prima di `real_send`: nessun invio al provider in quel tentativo. Non è un difetto
nel compilatore né un errore della richiesta generata dal modello.

Il fix risolve la sentinella con il valore del client e lascia invariati gli
argomenti passati a HTTPX. True esplicito rimane True, False esplicito rimane False.
La politica preesistente vieta redirect per la chiamata esterna a DeepSeek:
non viene rimossa. I redirect locali consentiti seguono la configurazione HTTPX.
Anche il percorso sincrono ha ora una guardia ed è verificato.

Prova prima del fix: **1 FAIL, 6 PASS**; fallisce proprio default False + sentinella.
Dopo il primo fix: **11 PASS**. Il collaudo finale comprende anche sei combinazioni
sul `Client` sincrono effettivo, oltre a quelle su `AsyncClient`.

## Metriche: difetto e nuovo significato

Due test pre-fix fallivano: un'eccezione prima del trasporto lasciava
`forwarded=true` e una prenotazione interamente addebitata come utilizzo incerto.
I grezzi precedenti non sono stati riscritti.

La nuova strumentazione è in `audit_tools/narrator_harness/metrics.py` e osserva
`handle_async_request` / `handle_request` del trasporto selezionato da HTTPX.
`server.py` applica le verifiche del progetto, freeze, URL e corpo originali.

| Stato/metrica | Significato e conseguenza |
|---|---|
| `request_prepared` | Corpo ricevuto dal trasporto applicativo; nessun invio implicito |
| `tokens_reserved` | Limite conservativo prenotato atomicamente; non consumo |
| `transport_started` | Controlli superati, immediatamente prima della delega al trasporto HTTPX |
| `response_headers_received` | Il trasporto ha restituito una risposta, anche 3xx/4xx/5xx |
| `not_dispatched` | Nessun ingresso nel trasporto; eventuale prenotazione liberata |
| `provider_usage_reported` | Usage coerente nella risposta letta; input + output, reasoning non sommato due volte |
| `unknown` | Invio iniziato ma usage assente/incoerente o errore: prenotazione conservata e STOP |
| `estimated_cost_USD` | Solo con usage, cache hit/miss e tariffario completo; altrimenti null |

`transport_started` **non prova** consegna al server né fatturazione. Timeout,
ConnectError, cancellazione e lettura interrotta non diventano automaticamente
«gratis». L'errore HTTP può avere usage valido oppure assente: entrambi sono testati.
Non si ricostruiscono risposte parziali. Una risposta incompleta non viene riletta
per modificare il comportamento di HTTPX.

Ogni hop aggiuntivo richiede un'altra prenotazione prima di entrare nel trasporto.
Il secondo hop viene bloccato se il residuo non basta. Prenotazioni concorrenti
sono atomiche; un'attesa non diventa un falso errore del provider. Un'attesa oltre
120 secondi richiede verifica manuale. Le prenotazioni rimaste pendenti dopo un
crash non sono cancellate automaticamente: si evita di riutilizzare credito incerto.

Le durate hanno nomi locali: attesa prenotazione, durata trasporto fino agli
header, durata complessiva dello scambio; non vengono presentate come tempo di
inferenza server. Il budget include tutte le richieste osservate, indipendentemente
dal fatto che siano routing, analisi, narratore o retry.

## Collaudo senza rete esterna

`preflight.py` avvia la FastAPI originale, configura solo il runtime sintetico e
sostituisce il trasporto del provider con `httpx.MockTransport`. URL, corpo, header
e timeout continuano a essere costruiti dal vero `app.ai_transport.post_chat`.
Il browser apre la vera React, scrive nel composer e preme «Invia»; nessuna API
applicativa viene simulata da Playwright.

| Caso dal composer | HTTP app / esito applicativo | Trasporti provider simulato | Usage |
|---|---|---:|---|
| Risposta valida | 200 / direct | 1 | 15 token **fittizi** |
| Provider HTTP 503 senza usage | 200 / failed | 1 | Sconosciuto; STOP |
| ReadTimeout | 200 / failed | 1 | Sconosciuto; STOP |
| ConnectError | 200 / failed | 1 | Sconosciuto; STOP |
| Budget già esaurito | 500 | 0 | Nessun invio; 0 |

Cinque richieste preparate, quattro ingressi nel trasporto principale. Prenotazione
per ciascuna delle quattro chiamate ammesse: 60.856 token; non consumo reale.
Il caso budget parte da un ledger sintetico già carico di 900.000 token. Gli errori
503/timeout/connessione non sono nascosti dal 200 dell'API: lo stato `failed` è
conservato e controllato. Il 500 per budget esaurito resta un limite dell'harness
applicativo, registrato; non viene corretto modificando il compilatore.

Sei probe aggiuntive sono invocate **dal browser attraverso FastAPI**, su un
endpoint presente solo nel processo di preflight, assente dal prodotto:

- redirect locali sincroni e asincroni disabilitati: 307, un hop;
- redirect locali sincroni e asincroni abilitati: 200, due hop;
- redirect esterno richiesto: rifiutato prima del trasporto dalla politica di audit;
- DNS, socket.connect e socket.connect_ex non loopback: tutti bloccati.

Queste probe non sono turni del narratore né invii tramite il composer. Sono
necessarie per esercitare configurazioni di redirect che il routing ordinario
non richiede. Nel preflight il trasporto HTTPX non ha fallback alla rete reale;
la barriera socket/DNS resta attiva anche se si aggira HTTPX. Il browser blocca
richieste non loopback. Nessuna credenziale reale è caricata.

La prima esecuzione offline `preflight-01` è conservata: risposta valida superata,
poi il test si è fermato perché presumeva erroneamente HTTP >=400 sul 503 del
provider. L'app correttamente espone invece 200 + `generation_status=failed`.
Corretta soltanto l'aspettativa del test; `preflight-02` completa tutti i casi.
Non sono due tentativi DeepSeek né sostituzioni di un risultato sperimentale reale.

## Equivalenza e verifiche

**51 test PASS**, Ruff PASS. Test differenziali con/senza osservatore confrontano
esattamente URL, metodo, corpo, header applicativi, estensioni timeout, ordine degli
hook, redirect e risultati/eccezioni. Quattro prove usano proprio il `post_chat`
della candidata: successo, HTTP errore, timeout e connessione fallita.

Le differenze intenzionali sono: filesystem di audit, temporizzazione locale,
blocco preventivo per budget/freeze/URL/payload e prenotazione degli hop. Il
preflight sostituisce solo il trasporto remoto con il simulatore e blocca l'egress.
Non cambia prompt, modelli selezionati, SOURCE, FastAPI, generatore o writer.

Non è stata rieseguita la suite completa del compilatore né una build di prodotto:
i relativi file sono identici alla candidata. I 4050 test citati nei rapporti
precedenti rimangono risultati storici, non verifiche svolte in questo intervento.

Limiti: adapter legato a HTTPX 0.28.1 e al suo `_transport_for_url`; una versione
diversa viene rifiutata. Non è una prova di equivalenza per streaming, altri
provider, altri protocolli o future versioni HTTPX. Il budget accetta soltanto
richieste testuali bounded del modello congelato. Il limite prudenziale dipende
anche dal rispetto di `max_tokens` da parte del provider; una violazione osservata
causa STOP, non una correzione retroattiva della fatturazione.

## Commit locali e rollback

| Commit | Contenuto |
|---|---|
| `4cce0aa` | Importa il piccolo harness precedente in Git, senza dati privati; directory via ambiente |
| `8524aa5` | Risoluzione della sentinella HTTPX, test pre/post |
| `8d047dc` | Metriche al confine di trasporto, guardia sincrona, budget e regressioni |
| `4fc0377` | Preflight browser/API offline, test differenziali sul trasporto del prodotto |

Nessun commit è pubblicato. Tutti i grezzi restano fuori da Git.

Rollback verificati in tre worktree separati, senza reset/clean:

| Punto di partenza | Comando | Commit di verifica | Prova |
|---|---|---|---|
| `8524aa5` | `git revert --no-edit 8524aa5` | `62bed0f` | Albero harness identico a `4cce0aa`; ricompare solo il fallimento default/sentinella (1 FAIL, 6 PASS) |
| `8d047dc` | `git revert --no-edit 8d047dc` | `6f3d0a2` | Albero identico a `8524aa5`; 11 redirect PASS, ricompaiono i due difetti metrici |
| `4fc0377` | `git revert --no-edit 4fc0377` | `5217a49` | Albero identico a `8d047dc`; 47 test PASS |

Le dipendenze contano: il preflight usa le nuove metriche e la guardia sincrona usa
il resolver dei redirect. Dalla versione completa, per tornare alle vecchie
metriche si annulla prima `4fc0377`, poi `8d047dc`; per tornare alla sentinella
precedente si annulla anche `8524aa5`. Non affermiamo che qualsiasi ordine di
revert sia indipendente. Non usare il vecchio harness per un tentativo reale.

Nessuna migrazione, modifica ai flag o ai dati dell'app. I revert toccano soltanto
strumentazione/test; le directory locali dei log e dei documenti non vengono rimosse.

## Artefatti

Grezzi nuovi: `backend/data/compilation-audit/harness-repair-20261028-01/` del nuovo
worktree: prove prima/dopo, preflight-01 e -02, log browser/API/provider simulato,
ledger, freeze, verifiche hash e rollback. Per il dettaglio degli eventi leggere
`provider-calls/<UUID>/metrics.json`; l'ordine delle chiamate principali è anche
in `context.sequence`. Le prenotazioni e i token simulati non sono metriche di
una campagna reale.

Backup separato: `/home/montesano/tesi-backups/harness-repair-20261028-01/`, con
manifest verificato; chiavi e database di runtime esclusi. Un backup include anche
la strumentazione e i report, senza affidarsi al solo Git.
