# Compilazione: prosecuzione del dialogo e feedback stabile

Baseline: `628fcb9`, branch `prune-backend`. Intervento circoscritto alla
presentazione e al workflow conversazionale globale. Retrieval FORM/SOURCE/MIXED,
analisi V11, parser, renderer, originali e dati live non modificati.

## Diagnosi osservata

Snapshot in sola lettura della sessione `3ef221896ece4ecf8c57841e50ec3f25`,
versione 9, progetto Minervino. Il primo gruppo chiedeva:

1. «Con quale qualità viene presentata la domanda…?» in uno slot booleano;
2. conferma della condizione della figura tecnica;
3. nome del sottoscrittore.

Erano persistiti `CONDITION_TRUE` per il secondo slot, `SKIP` per il terzo,
poi `CONDITION_TRUE` per il diverso ramo societario dopo «di ingegneria».
La prima condizione risultava ancora aperta. Le conferme di due condizioni
distinte non sono intercambiabili. Il raw storico di router/guard non era stato
acquisito: non è possibile attribuire retroattivamente il primo rifiuto a uno
specifico output. Un nuovo replay reale prima della correzione accettava anche
il semplice assenso alla domanda aperta; quello con il guard aggiornato lo
respinge, conservando gli altri due elementi. Instabilità semantica osservata,
non un parser deterministico che rifiuta sempre la stessa frase.

Il narratore riceveva sempre l'inventario completo e l'istruzione di rispiegare
i dati in circa cento parole. I tre messaggi storici hanno paragrafi introduttivi
di 96, 82 e 92 parole. Mancava una ricevuta del singolo aggiornamento.

Nel frontend il refresh passava attraverso una vecchia snapshot READY prima
del nuovo caricamento: potevano comparire ricevuta provvisoria, vecchia sintesi
e testo statico «Analizzo…», oltre allo spinner. Inoltre il messaggio finale
globale non sostituiva la ricevuta nel turno persistito: riaprire la conversazione
non ricostruiva correttamente la stessa cronologia.

## Modifica

- Primo turno: `DialoguePlan`, breve sintesi AI e massimo tre domande.
- Prosecuzione: `ContinuationPlan`, **solo questions e held_proposal_slots**.
  L'LLM conserva tutto il contesto SOURCE necessario per sospendere proposte
  dubbie, ma non ha più un campo message in cui ripetere l'inventario.
- Il backend compone la ricevuta dalle sole azioni accettate nell'ultimo turno:
  conferme, dati USER, rinvii e parti non interpretate. Non deduce nuovi valori,
  non enumera dati SOURCE e non usa le lunghe reason tecniche come risposta.
- Lo schema della richiesta lega gli slot booleani a `confirmation`, gli altri
  a `question`. Il renderer nuovo esige una proposizione chiusa per applicability;
  gli slot/destinatari restano quelli del backend. Le vecchie domande persistite
  rimangono leggibili. Guard indipendente: un assenso non fornisce un valore
  richiesto da una domanda aperta.
- Le ricevute conservano anche la domanda effettivamente posta. Parti accettate
  e scartate restano distinguibili; aggiornamenti parziali validi proseguono
  verso la nuova narrazione. Una risposta respinta cita la domanda attiva,
  anziché il motivo tecnico estratto dall'audit.
- Rimossi i contatori «N dati collegati» dalla domanda primaria. Il perimetro
  resta internamente disponibile e protetto dal guard dei rinvii condivisi.
- Un solo indicatore: «Analizzo il modulo…» inizialmente, «Aggiorno la
  compilazione…» nella fase REVIEW. Durante refresh/resolve si nascondono
  ricevuta provvisoria e sintesi precedente. Nessuna percentuale o nuova UI.
- Completamento globale: il messaggio finale sostituisce la ricevuta del proprio
  turno nella cronologia. Turni ordinari o appartenenti ad altre sessioni sono
  protetti. Il reload ricostruisce il dialogo dal DB.
- `riprendi` esplicito su vecchie domande non in pausa può aggiornare soltanto
  la narrazione, senza nuova analisi. Pausa/ripresa di un gruppo sospeso conserva
  il gruppo. `presentation_version=2`, nessuna migrazione al GET.

Nessuna chiamata aggiunta per questo intervento: rimangono router, eventuale
guard bounded e una narrazione. Quest'ultima può solo sospendere proposte;
non promuove GROUNDED_PROPOSAL a RESOLVED. USER non diventa SOURCE, FORM non
verifica valori. Nessuna esportazione o bozza incompleta implicita.

## Prove reali DeepSeek Flash

Provider reale configurato nel progetto. Database/storage privati eliminati
alla fine. Checkpoint preparato dalla **stessa proposta SOURCE registrata**,
rivalidata con le stesse fonti e originale; non una nuova analisi globale o
misura della compilazione end-to-end. Ogni serie mantiene invariato il codice
applicativo durante l'esecuzione. Gold/risultati attesi non entrano nel prompt.
Messaggi fissi: «1 si 2 si e 3 lascia in bianco», poi «di ingegneria».

| Prova | Esito osservato |
|---|---|
| before-routing-02 | Replay del vecchio gruppo: accetta tutti e tre, anche l'assenso alla domanda aperta |
| after-old-routing | Guard respinge solo il primo assenso ambiguo; conserva conferma e rinvio |
| after-01/02 | Errore di preparazione dello strumento SQL privato, zero chiamate AI; corretto solo il runner |
| after-03/04 | Prima soluzione di solo prompt insufficiente: ricapitola ancora i dati, 78/82 parole dopo la risposta |
| after-05 | Errore provider nella sintesi e output router invalidi; nessuna mutazione fattuale/export; tempi/usage di due invocazioni non acquisiti |
| after-06 | Ricevuta breve corretta, ma schema ancora permissivo accetta una domanda aperta per un booleano; due parti accettate e una scartata |
| after-07/08 | Schema corretto: due conferme + rinvio accettati; ricevuta di 13 parole, nessun inventario ripetuto; 18 proposte SOURCE intatte |
| resume-existing-01 | Riprende il checkpoint storico senza nuova analisi/inventario; resta un limite semantico della condizione originale, descritto sotto |
| after-09 | Prompt allineato allo schema senza confirmation=null per i valori: dialogo breve e18 proposte intatte; controllo globale DB fallito, descritto sotto |
| after-10 | Replica con ultimo codice: due conferme+rinvio, ricevuta13 parole,18 proposte intatte, intero fingerprint DB invariato |

Nelle prove after-07/08 il primo gruppo riguarda rappresentanza, ramo societario
e sottoscrittore. Dopo la risposta:

> Ho registrato le tue conferme. Lascio in bianco i punti che hai rinviato.

Segue soltanto la conferma residua della figura tecnica. «Di ingegneria» a quel
punto non conferma automaticamente l'incarico di una persona: viene chiesto di
precisare senza modificare lo stato. Il messaggio HTTP immediato resta una
ricevuta tecnica; UI e cronologia attendono/usano la narrazione conclusiva.
Le snapshot turn-2 contengono ancora il messaggio precedente: **la risposta
visibile del turno è response.json/body/answer**, non quella vecchia snapshot.

Le due serie after-07/08: sei invocazioni ciascuna, rispettivamente 15,61/16,53 secondi
AI sommati e 26.444/26.517 token; la narrazione di follow-up richiede 2,16/4,07
secondi. Non sono tempi end-to-end né prova di riduzione dei token: il contesto
completo per il controllo SOURCE è conservato. Nessuna nuova analisi, nessun
valore USER aziendale, nessun DOCX generato. Ricevuta finale realmente salvata
nella cronologia. Tutte le prove, anche fallite, sono conservate.

Ultima replica after-10: sei invocazioni,13,07 secondi AI sommati,26.730 token.
Mantiene13 parole nella ricevuta, ma seleziona anche una domanda locale sul
titolo del sottoscrittore, oltre alla conferma tecnica. In after-09 «di ingegneria»
risponde al diverso aspetto chiesto (ramo della figura tecnica); in after-10 non
risponde alla domanda locale sulla qualità, quindi non modifica nulla. La stessa
frase non conferma indistintamente domande diverse. La selezione e precisione
delle domande rimangono variabili; può ancora richiedere un dato ridondante
rispetto a una conferma di condizione già acquisita, senza convertirla in valore.

after-09 completa il dialogo ma fallisce l'assert finale sul fingerprint globale
del DB live. Per quella serie non erano acquisiti gli hash per tabella, quindi
la differenza non è localizzabile retroattivamente. La sessione/versione9,
lo stato, lo snapshot e il file originale sono verificati invariati. Il server
locale era attivo con reload, e init_database riscrive gli indici FTS: causa
possibile, non dimostrata. Nessun ripristino. Il runner ora salva gli hash
per tabella prima/dopo; after-10 conferma anche **zero tabelle cambiate**.
L'esito negativo after-09 è conservato e non è conteggiato come prova di
integrità globale riuscita.

## Limite residuo concreto

La condizione storica c.qualita è ancorata al solo testo **«IN QUALITÀ DI»**,
con una reason sulla rappresentanza e sei proposte dipendenti. È un contesto
troppo povero per descrivere un predicato booleano preciso. Nel replay di ripresa
il modello propone una conferma sul Direttore Tecnico; l'utente dichiara invece
di essere legale rappresentante. Il router propone VALUE, il guard lo considera
pertinente, ma il validator backend respinge VALUE nello slot booleano:
nessuna mutazione, nessun falso valore o conferma. Raw e transizione conservati.

La qualità di questa domanda resta insoddisfacente: lo schema chiuso non
certifica equivalenza semantica con una condizione mal modellata. Questo
intervento corregge ripetizione, feedback, persistenza e forma del contratto;
**non risolve la decomposizione delle condizioni della prima analisi**.
Non eliminare condizioni né confermarle automaticamente per aggirare il limite.
Nessuna prova di compilazione integrale o completezza delle checkbox.

## Verifiche software effettive

Provider simulati e DB temporanei per le suite, distinti dai replay reali:

- **203 mirati /28,42 s**, inclusi SOURCE/USER, risposte parziali, reprise delle
  vecchie domande, pausa/ripresa, retainer della cronologia e contratti narratore;
- **2.178 backend /162,97 s** sul codice finale; FTS5/Qdrant dove applicabile
  (precedente esecuzione completa2178/171,16s conservata);
- **106 frontend /6,98 s**, Oxlint e build TypeScript/Vite;
- **8 browser Chromium /10,3 s**, API simulate, desktop/mobile, reduced-motion
  e no-preference; MutationObserver rileva anche testi transitori, non solo la
  schermata finale; inclusi normale chat con mention e compilazione globale;
- **320 mutazioni** con seed delle domande strutturate, target preservato oppure
  errore controllato; Ruff backend/runner e diff check.

Fallimenti intermedi conservati: due nomi di file test inesistenti, aspettative
frontend legacy/contatore tecnico obsolete, fixture provider aggiornate al nuovo
schema, una regressione pausa/ripresa corretta conservando il gruppo sospeso,
errori E501 nei soli test corretti. Non sono presentati come esiti finali.

La sessione live è ancora versione 9 con lo stesso hash stato, snapshot originale
e file originale; controlli prima/dopo read-only. Nessuna modifica manuale ai dati.

## Acquisizioni e ripresa

Raw locali: `backend/data/compilation-audit/conversation-flow-20261013/`.
Include diagnosi, originale, catalogo/source audit, prompt/schema/output reali,
stati, cronologia, protocolli, usage/tempi acquisiti e controlli integrità.
Log software `backend/data/compilation-audit/conversation-flow-*.txt`.

[Metriche](benchmarks/2026-10-13-conversation-flow.json),
[bundle sanificato](benchmarks/2026-10-13-conversation-flow-audit.tar.gz),
[manifest](benchmarks/2026-10-13-conversation-flow-manifest.json).
Bundle:344 file,6.194.085 byte grezzi, confronto byte per byte e scansione
credenziali superati; nessun DB o file chiave. SHA256
`6e26f1134b2a208b097ae560eec8181cc245a930d120421a438e7f0e3decc1d6`.
Runner: `docs/benchmarks/benchmark_compilation_continuation.py` e
`replay_conversation_flow.py`; richiedono il checkpoint locale del report,
non le credenziali o il database di un altro ambiente.

Per vedere la correzione: backend/frontend aggiornati, poi nuovo dialogo; su un
vecchio gruppo non in pausa `riprendi` rinnova solo la narrazione. Non ripara
automaticamente le condizioni originali. Prossimo punto tecnico: separare
condizioni di applicabilità, scelte di ramo e valori locali nel primo output,
con regression sulla condizione «IN QUALITÀ DI», senza allentare SOURCE/USER.
Commit locali per passi; nessun push.
