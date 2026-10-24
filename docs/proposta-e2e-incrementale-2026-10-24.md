# Verifica esplorativa della candidata incrementale — proposta da autorizzare

Nessuna inferenza è stata eseguita per questa proposta. Non è una certificazione
delle soglie congelate, né una promozione nell'app ordinaria.

## Candidata e isolamento

Codice applicativo: `3ec0af00e5088d14455f5da9e12acba0ebbbabbc`, branch
`miglioramenti/2026-10-23-docx-offline`. Il commit di chiusura successivo cambia
soltanto test e documentazione. Prima delle chiamate, registrare SHA effettivo,
hash di codice/prompt/harness, FORM, SOURCE e politica USER, verificando che
l'albero applicativo sia identico a quel commit. Server e database temporanei,
sessioni nuove, nessun collegamento all'app live.

Profilo esatto delle nuove sessioni:

```text
MAPI_GENERATION_REVISION=3
MAPI_DIALOGUE_REVISION=1
MAPI_DERIVATION_REVISION=1
MAPI_NARRATION_RECOVERY_REVISION=1
MAPI_BRANCH_SCOPE_REVISION=1
MAPI_TABLE_SCOPE_REVISION=1
MAPI_HOLD_REREVIEW_REVISION=2
```

Verificare anche i flag persistiti `backend_revision=13`,
`option_authorization_revision=1` (V14), `attribution_safety_revision=1` (K3)
e la corrispondenza di tutti i flag sperimentali. Il provider/modello esatto e
gli eventuali parametri di reasoning vanno congelati nella preregistrazione:
usare la configurazione registrata nello sprint, senza assumere che un alias
remoto identifichi ancora la stessa revisione del modello.

## Sei tentativi, ordine fisso

| Ordine | Scenario storico | SOURCE | Variante USER |
|---|---|---|---|
| 1 | Catanzaro-1 | storico | catanzaro-controllo |
| 2 | Minervino-1 | storico | minervino-controllo |
| 3 | So.Re.Sa.-1 | nuova-source | generico |
| 4 | Cesano-1 | storico | cesano-esteso |
| 5 | Catanzaro-2 | storico | catanzaro-controllo |
| 6 | Minervino-2 | storico | minervino-controllo |

FORM, scenari, riferimenti e politica USER della valutazione finale congelata:
`benchmark ufficiale/valutazione-finale-20261022-01/PROTOCOLLO-FINALE.json`.
Per i cinque casi presenti nello sprint, verificare l'identità degli input con
`benchmark ufficiale/sprint-e2e-20261023-01/PROTOCOLLO-SEZIONI.json` e le rispettive
`input/SOURCE-storico.json` / `input/SOURCE-nuova-source.json`. Non modificare gold
o scenari per far emergere il nuovo comportamento. I riferimenti gold restano
fuori dai prompt. Se emerge una differenza negli input, registrarla prima delle
prove, senza presentare il confronto come appaiato.

Una sola prova di interruzione programmata, in Minervino-2: dopo la persistenza
del primo segmento valido, interrompere il runtime isolato e riprendere la stessa
sessione. Registrare anche le chiamate già in volo e i loro costi. Non è un nuovo
tentativo né una sostituzione. Gli altri cinque tentativi sono senza guasti
iniettati; i due tipi di esito vanno distinti nel rapporto.

Retry invariati: massimo uno per segmento, massimo due per singola analisi,
solo nei casi già ammessi dal runner. Una sola ripresa programmata. Il recupero
del narratore segue la politica esistente; ogni chiamata e ogni retry resta
nel consumo del tentativo. Nessuna ripetizione selettiva di un fallimento.

## Budget e arresto

Tetto proposto **3.000.000 token totali**, comprensivi di input, output, reasoning
ed eventuali retry/recuperi. Non sommare due volte reasoning già incluso negli
output del provider. Separare token in cache e non in cache; nessuno sconto
alla quantità prenotata per decidere se una chiamata può partire.

Prenotazione atomica prima di ogni chiamata, inclusi narratore e guardie:
stima prudente dell'input più massimo output/reasoning configurato. Contare
anche le chiamate concorrenti e mantenere la prenotazione per consumi ignoti.
Se la metrica manca, indicarla come ignota: non convertirla in zero. Non
avviare una chiamata se il residuo non copre la prenotazione. Se la stima non
è attendibile o un consumo la supera, fermarsi. Nessuna promessa di costo
USD: congelare la tariffa verificata quando la campagna sarà autorizzata.

Arresto alla prima scrittura non dimostrata o in ramo non applicabile,
aggiramento di sospensione/autorizzazione, divergenza dello stato all'export,
modifica di codice/prompt/harness o perdita di verificabilità dei consumi.
Un normale fallimento del modello resta registrato e non viene sostituito.
Revisione di tutte le scritture prima di avviare il tentativo successivo.
La presenza di una destinazione fra i 25 casi storici richiede verifica della
catena FORM/SOURCE/USER, non costituisce da sola prova di una scrittura indebita.

Il denominatore resta sei, con tentativi non eseguiti esplicitati se il budget
o un criterio di arresto impedisce di completare la prova. Nessun cambio al
codice durante la campagna.

## Misure e interpretazione

- DOCX riusciti/falliti, distinguendo il tentativo con interruzione programmata.
- Tutte le scritture: dato, soggetto, ruolo, ramo, provenienza e autorizzazione;
  revisione autoriale dichiarata, preferibilmente affiancata da un revisore diverso.
- Copertura del nucleo e omissioni con le motivazioni effettive dei vuoti; conteggio
  delle destinazioni DOCX, senza usare descrizioni libere come ID.
- Vecchi 25 controesempi: proposte, veti e scritture effettive; condizioni
  propagate dalla nuova protezione e possibili falsi rifiuti.
- Hold SOURCE nuovi, riesaminati, rilasciati, risospesi e realmente recuperati;
  un caso che non emerge non dimostra l'efficacia della rilettura.
- Cache riusata, segmenti persi o ripetuti, conflitti, retry e rivalidazione finale.
- Chiamate, token per categoria, consumi ignoti, latenza, costo a tariffa congelata.

Esito esplorativo favorevole solo con zero scritture non dimostrate e nessun
aggiramento dei gate; almeno cinque DOCX su sei è un segnale di disponibilità,
non prova statistica di superiorità. Se una nuova protezione rifiuta un dato
che ha tutte le condizioni dimostrate, analizzare e riportare il falso rifiuto.
Confronti con monolitica e sprint descrittivi, non perfettamente appaiati.
Nessuna promessa del 70% su Catanzaro o So.Re.Sa. e nessuna adozione automatica.
