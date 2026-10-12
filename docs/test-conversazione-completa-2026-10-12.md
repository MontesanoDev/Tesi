# Conversazione completa — 12 ottobre 2026

Due conversazioni nuove valide, DeepSeek Flash reale: **12 valori SOURCE
nel Word Catanzaro, 17 nel Word Labirinto**. Comandi di pausa/ripresa riusciti;
nel gruppo Labirinto anche SKIP e UNKNOWN, senza domande ripetute o valori
inventati. Conservata una terza conversazione con setup errato, descritta sotto.
Nessuna modifica a codice applicativo, prompt, parser, renderer, UI o gold.

Il percorso funziona per una **bozza parziale**, non dimostra completezza
del modulo. Il gate USER ha richiesto una conferma aggiuntiva per un riferimento
alle fonti; la prima serie Labirinto ha anche accorpato Ordine e numero albo.
Non si dichiarano risolti questi due limiti senza un intervento e nuove prove.

## Risultati misurati

| Misura | Catanzaro | Labirinto R1, setup errato | Labirinto R2, scope corretti |
|---|---:|---:|---:|
| Candidate strutturali | 307 | 55 | 55 |
| Frammenti SOURCE | 17 | 7 | 7 |
| Proposte testuali esportate | 12 | 16 | 17 |
| Posizioni omesse/non valutate | 293 | 35 | 34 |
| RESOLVED persistiti | 0 | 0 | 0 |
| Valori fattuali USER inseriti | 0 | 0 | 0 |
| Domande nel primo gruppo | 2 | 3 | 3 |
| Turni di chiarimento | 2 | 1 | 1 |
| Turni totali, avvio/pausa/ripresa/export inclusi | 6 | 5 | 5 |
| Chiamate AI complessive | 12 | 9 | 9 |
| Chiamate di analisi del Word | 1 | 1 | 1 |
| Secondi della sola analisi | 133,47 | 65,29 | 70,96 |
| Token totali, intero dialogo | 128.420 | 59.915 | 60.200 |
| Secondi AI, somma delle chiamate | 155,41 | 79,05 | 81,78 |

Trenta chiamate /248.535 token /316,23 s AI complessivi, includendo il setup
errato. Nessun retry del router, errore schema o nuova analisi della stessa
sessione. Tempi AI: chiamate realmente osservate, non misure browser né tempi
comprensivi della lettura umana. Catanzaro: 66.188 token input e 27.062 output
nella sola analisi, di cui 24.280 di reasoning; il costo dominante resta qui.
Pause/riprese/export durano circa 1–2 s AI; aggiornamento e nuova sintesi circa
4–6 s. Sono singole osservazioni, non una misura della varianza o un miglioramento
causale rispetto ai benchmark precedenti.

GROUNDED_PROPOSAL resta una proposta supportata localmente e da rivedere,
anche quando il payload dice REVIEW_REQUIRED per una condizione sconosciuta.
Non diventa RESOLVED dopo il consenso. USER conferma applicabilità/destinatario;
i valori già recuperati conservano provenance SOURCE. Nessun dato aziendale
o professionale presente nelle fonti è stato immesso manualmente.

## Conversazione Catanzaro

1. `@domanda-partecipazione.docx`, «me lo compili?» -> nuova sessione globale,
   una analisi e una sintesi. Due domande: ramo società di ingegneria e scelta
   del partecipante. Nessuna risposta generica «non posso compilare».
2. «Basta, riprendiamo dopo.» -> pausa persistita; domanda visibile rimossa.
3. Nuovo processo Python, rilettura DB identica, «Riprendi.» -> stessa sessione
   e stesso gruppo di due slot; nessuna nuova analisi.
4. «Confermo entrambe: la sezione delle società di ingegneria si applica e il
   partecipante è quello indicato nelle fonti.» -> router propone CONDITION_TRUE
   per entrambi. Gate indipendente: slot 1 SUPPORTED, slot 2 AMBIGUOUS.
   Salva soltanto il primo; nuova sintesi chiede soltanto il partecipante.
5. «Sì, confermo.» -> conferma USER sul secondo slot, senza inserire valori.
6. «Sì, prepara una bozza parziale con i dati disponibili e lascia in bianco
   le parti irrisolte.» -> GENERATED, download DOCX/report reali.

Raw del controllo che ha richiesto il turno aggiuntivo:

```json
{"checks":[{"slot":1,"result":"SUPPORTED","rationale":"L'utente conferma esplicitamente che la sezione delle società di ingegneria si applica, rispondendo alla domanda 1."},{"slot":2,"result":"AMBIGUOUS","rationale":"'Il partecipante è quello indicato nelle fonti' non conferma in modo univoco che sia Mapi Ingegneria S.r.l.; è un riferimento generico alle fonti."}]}
```

È un falso negativo conservativo plausibile: la frase confermava entrambe le
domande, ma il gate non ha accettato il riferimento anaforico. Nessun dato
errato scritto. Non è stato corretto o selettivamente ripetuto durante il test:
la successiva conferma è un normale turno della stessa conversazione.

### Valori realmente materializzati

| Candidate | Requisito | Valore | Provenance /evidence |
|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | SOURCE, visura demo, chunk -30 |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | SOURCE, visura demo, chunk -30 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE, visura demo, chunk -30 |
| t0.r9.c1 | Codice fiscale operatore | IT01234567890 | SOURCE, visura demo, chunk -30 |
| t0.r10.c1 | Partita IVA operatore | IT01234567890 | SOURCE, visura demo, chunk -30 |
| t25.r0.c1 | Denominazione società di ingegneria | Mapi Ingegneria S.r.l. | SOURCE, visura demo, chunk -30 |
| t25.r4.c1 | Forma giuridica società di ingegneria | Societa a responsabilita limitata | SOURCE, visura demo, chunk -30 |
| t25.r4.c3 | Sede legale società di ingegneria | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE, visura demo, chunk -30 |
| t26.r0.c1 | Direttore tecnico, nome | Ing. Elisa Romano | SOURCE, generalita-mapi.md, chunk -45 |
| t26.r1.c1 | Qualifica direttore tecnico | Ingegnere | SOURCE, generalita-mapi.md, chunk -45 |
| t26.r3.c1 | Ordine professionale | Ordine degli Ingegneri di Bari | SOURCE, generalita-mapi.md, chunk -45 |
| t26.r4.c1 | Numero albo | 8421 | SOURCE, generalita-mapi.md, chunk -45 |

I valori sono quelli del dataset didattico, inclusa la natura fittizia
dell'identificativo fiscale, senza correzioni o verifiche amministrative esterne.
Nel report sono conservati anche file/chunk index, ruolo, scope Company KB,
quote, hash del contenuto e condizioni confermate dall'utente.

## Conversazione Labirinto

R2: caricamento mediante le API normali in un DB nuovo. Company KB per cinque
fonti, General KB per `07-conoscenza-generale.txt`, SOURCE del progetto per
`06-procedura.txt`. Manifest, Word, testi e gold congelati invariati. ID fisici
assegnati dalle API e progetto temporaneo `prova`: nella verifica offline si
associano agli ID simbolici del gold solo con stesso nome, role, categoria,
scope globale/progetto e contenuto esatto, senza cambiare l'input del modello.

1. Avvio -> 17 proposte, tre domande: applicabilità del ramo, recapito alternativo,
   polizza alternativa. Nessuna scelta arbitraria tra i due valori concorrenti.
2. Un solo messaggio: «1. Sì, quella sezione si applica. 2. Per il recapito salta,
   lo verificheremo dopo. 3. Il numero della polizza non lo so.» -> CONDITION_TRUE,
   SKIP, UNKNOWN sui rispettivi slot backend. Quote/provenance USER persistite.
   I due valori rinviati rimangono vuoti; nuova sintesi propone la bozza,
   senza ripetere le domande. Non si dichiara assente una fonte solo perché
   l'utente non sa scegliere: esistono due alternative non risolte.
3. «Basta, metti in pausa.» -> pausa e domanda di generazione nascosta.
4. Nuovo processo, «Riprendi.» -> stessa sessione, conferma e rinvii conservati.
5. «Ok sì, genera una bozza parziale con i dati disponibili, lasciando vuoti
   il recapito e la polizza.» -> GENERATED, 17 valori SOURCE.

**17/17 valori esportati** coincidono letteralmente, dopo normalizzazione di
case/whitespace del confronto offline, con i corrispondenti valori del gold;
17/17 hanno le fonti attese tramite la mappatura documentata. Non è accuratezza
su tutti i 55 candidate, né prova generale della correttezza semantica.
Ordine = «Ordine degli Ingegneri di Ancona», numero albo = «5739», separati.
Nessun valore per recapito/polizza, checkbox native non materializzate.

R1 aveva gli stessi testi ma la procedura nella KB sbagliata: conservata come
diagnosi dell'harness e prova dei comandi, esclusa dai confronti della fixture.
16 valori scritti, con Ordine = «Ordine degli Ingegneri di Ancona, n. 5739»
e numero albo separato omesso. Non attribuire il 17 anziché 16 al cambio di
scope: manca un confronto controllato che separi questo effetto dalla variabilità
del modello. Anche la sintesi R1 diceva «polizza non disponibile», meno precisa
di «due alternative, l'utente non sa quale usare».

## Controlli e limiti

Confrontati **45 valori** fra stato, report e tre DOCX reali: 12 +16 +17.
Tutti scritti nella cella indicata dallo stato; nessuna cella aggiuntiva cambiata.
Questo verifica materializzazione, non rende semanticamente corretto il valore
accorpato R1. Paragrafi invariati salvo banner, controlli Word nativi identici,
stesse parti ZIP, modificato soltanto `word/document.xml`. Originali immutati.
Le due celle differite Labirinto restano vuote. Nessuna generazione prima
dell'esplicita richiesta. Pause/riprese in nuovi processi, rilettura identica
del DB prima di ogni turno; revisioni/backend e conversazioni acquisite.

**109 test software mirati passati /17,07 s**, provider simulati: sessione
globale, dialogo, guard USER e chat. Ruff backend completo e harness, diff check.
Primo preflight Ruff dei due harness con righe lunghe corretto prima delle API,
log conservati. Un comando ad hoc di ispezione ha avuto un SyntaxError prima
della lettura, poi corretto: nessun risultato AI scartato. Nessuna suite completa
backend o frontend/browser ripetuta: codice applicativo e contratti invariati.
Le HTTP sono reali via ASGI; non è stata guidata la UI nel browser.

Nessun valore fattuale USER nuovo, modifica di valori già acquisiti, non
applicabilità negativa o comando composto esercitati in queste conversazioni.
I test precedenti su tali casi restano separati. La sintesi è ancora LLM e può
essere imprecisa. Molti candidate omessi, checkbox e allegati non completati:
GENERATED significa bozza generata, non sessione completa/pronta alla consegna.

**Prossima priorità proposta:** rendere affidabili le conferme che si riferiscono
al gruppo appena chiesto, mantenendo il gate indipendente e senza allargare i
destinatari. Poi decidere esplicitamente la semantica di «salva questo valore e
poi pausa/export», ancora da discutere. Separazione Ordine/numero da misurare
nel filone SOURCE/compilazione, senza mescolarla al routing dei comandi.

## Acquisizioni

[Metriche e turni](benchmarks/2026-10-12-full-conversation.json),
[archivio sanificato](benchmarks/2026-10-12-full-conversation-audit.tar.gz),
[controlli finali](benchmarks/2026-10-12-full-conversation-final-checks.json).
Grezzi `backend/data/compilation-audit/full-conversation-20261012/`:
root Catanzaro, `labirinto/` R1, `labirinto-r2/` corretta. Prompt/schema/raw,
HTTP analisi/sintesi, usage/tempi, stato/dialoghi/revisioni, audit, originali,
DOCX/report e confronti. Nessun DB, chiave o runtime privato nel bundle.
Snapshot privati eliminati dopo confronti/acquisizioni; niente credenziali
nei report. Codice applicativo identico alla baseline fb2894e in tutte le serie.
Bundle verificato byte-per-byte: **303 file /1.142.223 byte**, SHA-256
`d57f20629d2144e6c2032f859d41c3cd276f81c314a35502beb8bdc04bb1a170`.

## Protocollo e note registrati prima degli esiti finali

Protocollo fissato prima delle API. Baseline applicativa `fb2894e`, già
pubblicata su `origin/prune-backend`. Nessun cambiamento applicativo durante
la prova; questa verifica precede qualsiasi decisione sui turni composti.

## Percorso e limiti

Nuova conversazione, originale `domanda-partecipazione.docx` del progetto
`prova`, corpus SOURCE attuale congelato in snapshot privato. DeepSeek Flash
reale, stesso profilo selezionato dal progetto. API HTTP ASGI reali in-process;
non è un test browser. Database/storage isolati: nessuna modifica alle sessioni
live, nessun checkpoint di compilazione preparato manualmente.

Avvio con mention strutturata e «me lo compili?», avanzamento tramite il normale
`resolve`, poi risposta ai chiarimenti realmente posti. Provare rinvio locale,
pausa, riapertura in un nuovo processo e ripresa della stessa sessione.
Chiedere esplicitamente una bozza parziale e controllare il DOCX realmente
prodotto. Massimo 12 turni per conversazione e tre avanzamenti automatici per
turno; nessuna nuova analisi per sostituire un esito insoddisfacente.

Non fornire valori aziendali già presenti nelle SOURCE. Le conferme USER di
applicabilità rimangono distinte dai valori SOURCE. Non inventare risposte
su requisiti non conosciuti: UNKNOWN/SKIP sono esiti ammessi. Non forzare
domande o scritture tramite DB/API field. Se la conversazione reale non pone
un chiarimento adatto al rinvio locale, aggiungere una prova distinta sulla
fixture congelata Labirinto V1, con le sue fonti originali e senza gold nel
prompt. Registrare anche failure ed elementi non esercitati.

## Acquisizioni e verifica

Conservare prompt/schema, raw, usage, tempi, richieste/risposte chat,
conversazione e sessione dopo ogni turno. L'osservatore delega invariati i
trasporti al provider reale; non simula decisioni. Confrontare stato, report,
valori selezionati e posizioni Word; altre posizioni, checkbox e originale
devono restare invariati, salvo il banner di bozza previsto dal renderer.

Distinguere GROUNDED_PROPOSAL da RESOLVED e scrittura della bozza da completezza
del modulo. Nessuna accuratezza percentuale senza gold sul bando reale.
Riferimenti grezzi e bundle sanificato saranno aggiunti al report; database,
chiavi e runtime privati non devono entrare nell'archivio pubblico.

## Risultati

Prima conversazione Catanzaro conclusa: 12 valori SOURCE esportati; pausa e
ripresa persistite. Una conferma anaforica del partecipante è stata giudicata
ambigua dal gate, richiedendo un turno aggiuntivo. Nessuna modifica applicativa.

Prima serie Labirinto conclusa: controlli SKIP/UNKNOWN/pausa/ripresa riusciti,
ma rilevato un errore del setup. `06-procedura.txt` è stato caricato come globale
Company anziché SOURCE del progetto. La serie viene conservata integralmente,
senza presentarla come confronto valido della fixture congelata. Prima di una
seconda serie si corregge solo l'harness: scope/category dal `sources.json`
originale, nuovo DB e nuova conversazione, nessun cambiamento a gold o motore.
Gli ID fisici assegnati dalle API restano quelli reali; il confronto offline
con gli ID simbolici della fixture deve verificare nome, scope e contenuto.

Nota d'ambiente: la creazione di script `.py` sotto backend con uvicorn --reload
attivo ha provocato il normale riavvio e la reindicizzazione di 82 frammenti
di quattro artefatti live. Contenuti, SOURCE, conversazioni, sessioni e originali
sono invariati; non si dichiara identità fisica dell'intero database. Nessun
ripristino manuale. Per il secondo harness si usa un file `.txt` interpretato
da Python, così non si sollecita il watcher.

Le sezioni precedenti riportano gli esiti finali. Test precedenti sui 43/28
checkpoint non vengono presentati come risultati di queste conversazioni.
