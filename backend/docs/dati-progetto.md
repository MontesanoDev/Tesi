# Dati del progetto

Il flusso visibile e **Fonti -> Dati del progetto -> Template e compilazione**.
Non esiste piu una fase obbligatoria di approvazione dei singoli Call Facts.

- **Dati estratti**: sintesi automatiche delle fonti del progetto, con nome del
  documento e frammento di origine. Si possono correggere, escludere e ripristinare.
- **Dati inseriti**: testo modificabile con dati e scelte del proponente.
  Il salvataggio li indicizza nel solo progetto corrente.
- **Company KB e General KB**: restano archivi globali separati e invariati.

## Compatibilita e persistenza

L'unificazione riguarda il workflow, non una fusione distruttiva dei documenti.
Si conservano `call-facts.md` e `project-facts.md`, ID, contenuti e versioni.
Gli endpoint `/call-facts` e i vecchi link restano compatibili; nella UI aprono
la vista unica. Le vecchie verifiche restano registrate, senza essere un requisito
di utilizzo. Nessun fatto viene automaticamente marcato come verificato.

All'avvio gli artefatti vengono reindicizzati: i fatti con fonti e non esclusi
sono disponibili anche se il vecchio stato e `pending`. Il testo salvato non
viene riscritto per convertirne lo stato. Fatti senza fonti non sono promossi
a evidenze; dati dichiarati nuovi vanno nella sezione Dati inseriti.

Le correzioni effettuate dalla nuova UI conservano ID e fonti di origine e
registrano `origin=user_corrected`. Non sono citazioni letterali dei documenti.
Non e possibile ricostruire retroattivamente l'origine delle correzioni storiche
che il vecchio formato non distingueva dalle estrazioni.

La riestrazione sostituisce i dati estratti, incluse correzioni ed esclusioni,
solo dopo conferma nell'interfaccia. Non tocca i dati inseriti; una modifica
concorrente dei fatti durante la richiesta interrompe la sostituzione con 409.
I file originali del progetto rimangono nel corpus anche quando si esclude una
sintesi estratta: l'esclusione non cancella la fonte documentale.

## Risposte incomplete durante l'estrazione

L'estrazione usa un limite di output di 12.000 token e controlla `finish_reason`.
Solo `stop` consente il parsing e il salvataggio. Se il provider segnala `length`,
la risposta viene scartata anche se il JSON e sintatticamente valido; si esegue
un solo nuovo tentativo con 24.000 token e le stesse evidenze complete.
Non si recuperano fatti da JSON parziali. Gli altri errori non attivano tentativi
automatici; il limite totale e di 360 secondi, con 180 secondi per richiesta.

Errori e troncamenti non sostituiscono contenuto, versione o indice dei dati
gia salvati. In caso di successo, `total_tokens` somma entrambi i tentativi;
se manca un dato di utilizzo valido restituisce `null`, non una stima.
I log diagnostici riportano motivo di terminazione, budget e posizione degli
errori JSON, senza stampare contenuto delle fonti o risposta del modello.

## Generazione

Sia il contesto DOCX sia il generatore Markdown usano i dati estratti disponibili,
senza il filtro `status=verified`. Il generatore Markdown puo procedere anche
senza estrazione, usando i dati inseriti e quelli aziendali e lasciando i mancanti
come TODO. Il campo API `available_fact_count` conta i dati estratti disponibili;
`verified_fact_count` resta solo per compatibilita e conta le verifiche storiche.

Restano i controlli su riferimenti, citazioni, scope e scritture DOCX. Il documento
compilato rimane una bozza da controllare, non una candidatura certificata o inviata.
Questa semplificazione non risolve da sola ambiguita dei moduli, scelte di
partecipazione o l'assegnazione di un dato alla persona/sezione corretta.

## Verifica

I test coprono utilizzo dei fatti senza verifica, esclusione/ripristino,
provenienza delle correzioni, reindicizzazione dei vecchi documenti senza
riscriverli, isolamento tra progetti, conservazione dei dati inseriti durante
la riestrazione e protezione dalle risposte asincrone obsolete.
Sono coperti anche troncamenti, retry limitato, conteggio dei token e mancata
sovrascrittura di dati e indice dopo un'estrazione incompleta.
Le risposte del modello nei test sono simulate.
