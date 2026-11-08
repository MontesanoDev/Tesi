# Controllo di attribuzione condiviso — 21 ottobre 2026

Intervento di sicurezza limitato prima di P3, sulla base tecnica V14, che non è una baseline:
la V12 resta adottata. Zero chiamate LLM, nessun commit o push. La preregistrazione
`PREREG-SAFETY.md` (SHA256 `2772f511…`, 21:11:57 UTC) precede il codice e le misure.

## Esito

Dei tre controlli richiesti, **solo il controllo d'organizzazione (K3) supera la regola
preregistrata ed è implementato**, soltanto per le nuove sessioni. Gli altri due sono stati
misurati ed esclusi senza adattamenti. Delle cinque falle trovate in P2, una è chiusa e
quattro restano rischio residuo documentato.

| Controllo | Casi sintetici | Replay su 92 audit | Decisione |
|---|---|---|---|
| K1: classe del codice fiscale (persona 16 caratteri, impresa 11 cifre) | conformi | 39 proposte corrette perse: la partita IVA `IT01234567890` registrata come CF dell'impresa | **escluso** |
| K2: coerenza delle attestazioni «in chiusura» (carica attuale o cessata) | conformi | 147 corrette perse (15,5%; 69% a Catanzaro) | **escluso** |
| K3: organizzazione nominata nell'attestazione di ruolo | conformi | 0 perse, 0 modifiche | **implementato** |
| K4: appartenenza lato FORM | — | — | escluso a priori |

## Cosa fa K3

Considera una proposta personale accettata per un ruolo, dal binding V12, da un recupero
V13 o dal riuso della carica del firmatario. Se una voce SOURCE certa della stessa persona
(«- **P:** R di X» o la forma in grassetto V13) nomina esplicitamente un'organizzazione X,
X deve essere una delle due cose seguenti:
- un'impresa che la bozza stessa documenta;
- un riferimento generico alla società («della società…», senza nomi propri).

Altrimenti la proposta perde il grounding e resta vuota con il motivo tracciato
(`REJECTED`, copertura `REJECTED_PROPOSAL`). Il controllo può solo togliere, mai
aggiungere. Nessuna ricevuta USER lo annulla: una selezione o un'autorizzazione non
rendono documentato un fatto. Le sessioni esistenti, quindi V12, V13 e V14, restano
invariate: il flag `attribution_safety_revision: 1` vale solo per le sessioni nuove.

## Scritture

- **Fermate:** controesempio 3 di P2, DT di un'altra azienda grounded. È bloccato anche
  quando la bozza non ha imprese grounded, e quando X è «di cantiere» o «dell'impresa
  ausiliaria».
- **Recuperate:** nessuna; l'intervento non ne cerca.
- **Rifiuti corretti preservati:** il controllo non aggiunge mai grounding, quindi restano i
  rifiuti di tipo soggetto di Cesano, i requisiti V14 e i blocchi esistenti.
- **Regressioni:** nessuna nel replay; nessun campo non bloccato modificato (equivalenza
  verificata su 26 casi e 92 audit).

Nelle risposte registrate K3 non scatta mai: la falla non si è presentata. Il beneficio è
dimostrato solo sui casi sintetici.

## Perché K1 e K2 sono esclusi

- **K1.** Nel replay ha bloccato solo identificativi aziendali. I CF personali, tutti con
  carattere di controllo non valido nella KB demo, erano corretti per classe. Una variante
  limitata alla persona sarebbe una revisione da preregistrare di nuovo: non è stata fatta.
  La validità formale resta comunque solo un avviso: non prova l'attribuzione.
- **K2.** Basta una frase affermativa della KB per togliere tutte le proposte di Elisa Romano
  come direttore tecnico: «Non sostituisce l'amministratore unico Luca Ferri o il direttore
  tecnico Elisa Romano». Un controllo che non usa elenchi di verbi deve trattare come
  conflitto ogni forma non riconosciuta, e la prosa normale ne è piena.

## Rischio residuo documentato

| Falla | Stato |
|---|---|
| ruolo FORM di un partner («dell'impresa ausiliaria», «della mandante») | aperto: nei 13 moduli reali la stessa sintassi indica anche l'operatore tipizzato; dipende dalla forma di partecipazione (scelta USER, P3) |
| carica cessata scritta in prosa altrove («ha lasciato la carica…») | aperto: restano il lessico di incertezza esistente e la lettura del modello |
| CF societario proposto come CF personale | aperto: K1 escluso |
| documento SOURCE di un'altra impresa senza organizzazione esplicita (visura di terzi) | aperto, fuori dalla portata di K3 |
| impresa partner documentata dalla stessa bozza | K3 non distingue quale impresa chiede il campo FORM |

Nelle 719 proposte personali accettate registrate nessuna di queste falle si è attivata
(rapporto P2). Restano un punto da controllare nella revisione indipendente finale.

## Verifiche

- 13 test nuovi (`test_compilation_attribution_safety.py`): unitari, gate V12 reale,
  flag, sessione reale nuova e precedente con provider simulato, bypass dell'export rifiutato.
- Suite backend completa: PASS. L'esecuzione con arresto al primo errore è arrivata al 100%
  (6 min 28 s); subito dopo risultavano 3.439 test raccolti. Ruff su tutto il backend: PASS.
  Durante l'esecuzione un'altra sessione modificava file di embedding e retrieval,
  estranei a questo intervento.

## Materiali

Grezzo in `backend/data/compilation-audit/attribution-safety-20261021-01/`: snapshot,
preregistrazione, candidato K1-K3, casi, replay, equivalenza, patch esatte e copie del
modulo e dei test. Backup in `docs/benchmarks/2026-10-21-controllo-attribuzione-*`.
