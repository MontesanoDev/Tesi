# Dati del progetto

Il flusso visibile e **Fonti -> Template e compilazione**. La sezione Dati del
progetto, le schede Dati estratti/Dati inseriti e il relativo contatore non sono
piu presenti nell'interfaccia. Per specificare modalita di partecipazione,
firmatario e sezioni da compilare si usano le indicazioni del modulo Word.

Il backend conserva gli artefatti e le API esistenti: quanto descritto sotto
riguarda questa compatibilita, non funzioni accessibili dalla UI attuale.
I dati gia salvati possono ancora entrare nel contesto della chat e della
compilazione secondo i filtri esistenti. La rimozione della sezione non esegue
cancellazioni o migrazioni dei documenti.

## Compatibilita e persistenza

L'unificazione riguarda il workflow, non una fusione distruttiva dei documenti.
Si conservano `call-facts.md` e `project-facts.md`, ID, contenuti e versioni.
Gli endpoint `/call-facts` restano disponibili; i vecchi link della UI aprono
ora il Template. Le vecchie verifiche restano registrate, senza essere un requisito
di utilizzo. Nessun fatto viene automaticamente marcato come verificato.

All'avvio gli artefatti vengono reindicizzati: i fatti con fonti e non esclusi
sono disponibili anche se il vecchio stato e `pending`. Il testo salvato non
viene riscritto per convertirne lo stato. Fatti senza fonti non sono promossi
a evidenze.

Le correzioni effettuate tramite API conservano ID e fonti di origine e
registrano `origin=user_corrected`. Non sono citazioni letterali dei documenti.
Non e possibile ricostruire retroattivamente l'origine delle correzioni storiche
che il vecchio formato non distingueva dalle estrazioni.

La riestrazione tramite API sostituisce i dati estratti, incluse correzioni ed
esclusioni. Non tocca i dati inseriti; una modifica
concorrente dei fatti durante la richiesta interrompe la sostituzione con 409.
I file originali del progetto rimangono nel corpus anche quando si esclude una
sintesi estratta: l'esclusione non cancella la fonte documentale.

## Fonti ammesse nella chat

La ricerca fattuale usa le fonti caricate, i dati inseriti per il progetto,
i dati estratti disponibili e le KB globali. Gli artefatti `template.md` e
`draft.md` restano consultabili/modificabili nei rispettivi percorsi, ma non
vengono indicizzati come evidenze. Il generatore Markdown continua a leggere
il template direttamente per definire la struttura dell'output.

All'avvio il riallineamento degli artefatti elimina dall'indice gli eventuali
vecchi chunk di template e draft, senza riscrivere contenuto o versione dei
documenti personalizzati. Anche le query applicano il filtro per ruolo della
fonte: i chunk legacy non diventano evidenze prima del riallineamento.
Il nome del file non e un criterio di esclusione: un file caricato esplicitamente
fra le fonti resta una fonte anche se si chiama `template.md`.

Il fallback delle domande successive rilegge i chunk citati nel turno precedente
e verifica tipo di fonte e appartenenza al progetto. Gli estratti salvati nella
cronologia non sono piu riutilizzati direttamente come evidenza: fonti eliminate,
chunk sostituiti, template e documenti di altri progetti vengono esclusi.
La cronologia rimane disponibile come contesto conversazionale non fattuale.

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
