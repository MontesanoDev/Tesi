# Audit narratore Minervino: tentativo interrotto prima del provider

Revisione **AUTORIALE**, non indipendente. L'unico tentativo autorizzato non ha
completato il percorso E2E: errore nella strumentazione, prima dell'invio a
DeepSeek. Non è una valutazione della qualità del narratore e non è stato ripetuto.

## Configurazione verificata

Candidata `7b31d25930c52504e0a1461491bde3fd23ca3a0e`, comprendente `f3bc281` e
le precedenti correzioni `fa83800a`, `3cfd5213`, `0dda3ffe`. Worktree distinto
`tesi-audit-narratore-20261028`, profilo completo `sezioni-2026-10-25`.
Frontend reale su 15173 e FastAPI su 18080; database nuovo, stesso FORM e 56
evidenze del seed autorizzato, nessuna sessione o conferma precedente importata.
Richiesto `deepseek-flash`; nessuna risposta o fingerprint del provider ricevuta.

Preregistrazione, scenario USER, prompt, codice, configurazione e input congelati
prima del primo invio; 159 hash verificati invariati alla fine. Backup preflight
senza credenziali, 19 file verificati. Budget massimo 900.000 token, prenotazioni
atomiche prima del trasporto; 11 test offline sul registro, tutti passati.

## Fallimento riprodotto

Il primo POST chat reale raggiunge FastAPI, entra nel routing e prepara la prima
richiesta. Il controllo dei redirect nell'harness riceve la sentinella HTTPX
`UseClientDefault`, la considera erroneamente un booleano True e solleva
`AssertionError: Redirect forbidden` **prima** di `real_send`. La UI riceve 500.

Riproduzione deterministica successiva, solo offline: httpx 0.28.1, client con
`follow_redirects=False`, sentinella truthy, assertion, zero invii al trasporto
finto. Il codice del prodotto non causa questo errore e non è stato modificato.
La prova è in `DIAGNOSI-HARNESS.json`, con stack trace originale conservata.

La telemetria grezza marca `forwarded=true` troppo presto, all'ingresso nel
trasporto applicativo. Non prova un invio sulla rete. Il timer etichettato
`provider_seconds` misura qui soltanto il controllo locale fallito. Questi dati
non sono stati riscritti: la loro interpretazione è rettificata nel rapporto.

## Risultato effettivo

| Misura | Esito |
|---|---|
| Tentativi iniziati / completati / ripetuti | 1 / 0 / 0 |
| DOCX | 0 |
| Invii USER / turni narratore | 1 / 0 |
| Sessioni / proposte / hold / ricevute | Nessuno |
| Persistenza | Una conversazione vuota, zero turni salvati |
| Chiamate DeepSeek inviate | 0 |
| Token del provider | Non disponibili: nessuna inferenza |
| Ledger conservativo | 63.494 token prenotati, non consumati dal modello |
| Spesa stimata | 0 USD; fattura non verificata |
| Driver / POST browser / backend | 1,846 s / 0,071130 s / 0,050508 s |

Domande ripetute, conferme perse, sospensioni fondate/infondate, omissioni,
copertura e correttezza delle scritture: **non valutabili**. Zero scritture
indebite osservate non è una prova di sicurezza quando manca qualsiasi export.
I fix del ruolo e della checkbox sono **NON ESERCITATI**, non validati dal vivo.
Il precedente replay a 58 scritture resta un riferimento offline separato.

## Interventi proponibili, non implementati

1. Risolvere correttamente la sentinella `follow_redirects` nel solo harness;
   testare default False, True esplicito e default True senza rete esterna.
2. Separare eventi reserve/dispatch/response nelle metriche, conservando il
   conteggio prudente quando una richiesta effettivamente inviata ha usage ignoto.
3. Aggiungere un preflight dell'intero trasporto strumentato con MockTransport:
   i soli test del ledger non coprivano il difetto emerso.

Sono interventi piccoli e reversibili sulla strumentazione, non correzioni del
compilatore. Non esiste evidenza nuova per proporre tre fix del narratore.
Nessuno dei tre interventi è stato implementato durante o dopo il tentativo.

## Artefatti e chiusura

Sette rapporti completi, JSON cronologico, riepilogo numerico, DOM, screenshot,
trace, richieste e log privati in
`backend/data/compilation-audit/narratore-minervino-20261028-01/` del worktree.
Non aggiungerli a Git: contengono il caso reale e informazioni personali.
Backup separati sotto `tesi-backups/narratore-minervino-20261028-01-*`; il runtime
con credenziali è escluso. Gate chiuso, due servizi isolati arrestati.
App ordinaria, dati storici, baseline e benchmark non modificati. Nessun push,
merge, adozione, correzione automatica o ulteriore inferenza. Fermarsi qui.
