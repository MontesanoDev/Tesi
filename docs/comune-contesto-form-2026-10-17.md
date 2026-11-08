# Compatibilità del Comune e contesto FORM dei soci

17 ottobre 2026. Correzione autorizzata, senza nuove chiamate LLM. **Eliminate
le due accettazioni dell'indirizzo completo nel Comune; recuperate altre 11
proposte corrette in B0-03.** Tutti i recuperi della precedente correzione KISS
sono conservati. Nei due replay finali nessun valore grounded è non conforme
al gold e nessun valore corretto precedente è perso.

Il riconoscimento del contesto FORM migliora su tutti i 18 casi richiesti,
ma solo 11 superano anche i controlli SOURCE. Gli altri sette restano bloccati:
la nuova prova FORM non costituisce una prova del ruolo nella SOURCE.

[Misure e dettagli per campo](benchmarks/2026-10-17-field-context.json),
[bundle](benchmarks/2026-10-17-field-context-audit.tar.gz),
[checksum](benchmarks/2026-10-17-field-context-audit.tar.gz.sha256),
[controlli](benchmarks/2026-10-17-field-context-checks.json).
Il [rapporto KISS precedente](correzione-binding-kiss-2026-10-17.md) è la baseline
immediata del confronto; gli esiti storici non sono stati riscritti.

## 1. Riproduzione e correzione del campo Comune

Gli audit KISS sono stati riprodotti **esattamente prima della modifica**.
In entrambe le risposte `p41.s1` accettava come proposta grounded:

```text
Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia
```

Il valore è presente nella SOURCE e documenta davvero una sede, ma non è
compatibile con la granularità richiesta dalla destinazione. La label del
modello dice soltanto «sede legale» e non costituisce un controllo indipendente.

Il FORM originale va letto oltre la singola quote: `paragraph:41` contiene
«P. IVA [...] sede legale in [...]»; `paragraph:42` prosegue con campi separati
«prov. [...] via/piazza [...] n. [...]». La richiesta di sola località è
dimostrata da questa suddivisione fisica, non dalla parola «in» presa da sola.

La correzione risiede nel **validatore condiviso delle proposte**, non nel
writer. Rilegge la label fisica del singolo slot, fermandosi ai placeholder
adiacenti; per le celle considera la label nella stessa riga. Identifica:

- richieste esplicite di Comune/città/località municipale;
- sede/residenza in una località seguita da componenti di indirizzo separati,
  nello stesso paragrafo oppure nella continuazione immediata con provincia
  e via/piazza. Non cerca campi di altri soggetti in sezioni successive.

In questi casi un valore con indicazione stradale e numero civico/postale
riceve `incompatible_locality_value`. Il messaggio è:

```text
Il FORM richiede un Comune/località: l'indirizzo completo non è compatibile con questo campo
```

Il validatore **respinge senza trasformare**: nessuna estrazione automatica
di Bari, sostituzione del fatto, nuova citazione o geocodifica. Il fatto SOURCE
resta grounded come dato di sede; è la sua assegnazione al Comune a essere
respinta. Il controllo vale anche se il modello rinomina il campo «indirizzo».

Sono conservati i valori letterali di località come Viareggio, Piazza Armerina
e Bari (BA). Restano ammessi gli indirizzi nei campi che li richiedono e nelle
richieste composite «Comune e indirizzo completo». La sola frase «sede legale
in», senza suddivisione o label esplicita, non viene arbitrariamente convertita
in un tipo Comune.

Questa è una verifica deterministica della compatibilità per il difetto
osservato, non un classificatore semantico universale di tutte le proprietà.
Si limita alle prove strutturali e ai valori stradali riconoscibili descritti
sopra, senza introdurre conoscenze geografiche o trasformazioni.

Codice: [compatibilità fisica](../backend/app/document_compilation.py:153),
[validatore condiviso](../backend/app/document_compilation.py:189).

## 2. Diagnosi dei 18 rifiuti FORM

I 18 sono quelli con fatto SOURCE localmente grounded e rifiuto
`Ruolo FORM esterno al contesto del candidate` nel replay KISS. Esiste un
diciannovesimo campo, `p46.s0`, che presenta lo stesso errore FORM ma anche
la citazione insufficiente per Bari (BA): è tenuto separato dal conteggio.

La prova di ruolo dei tre soci cita `paragraph:42`:

> e composta da (riportare nominativo, qualifica professionale e C.F. di ogni socio):

Questa è l'introduzione letterale dell'elenco numerato seguente. Il contesto
non era riconosciuto perché il paragrafo introduttivo contiene anche campi
aziendali: il vecchio meccanismo di continuazione non lo registra come origine.
Oltre al primo paragrafo dell'elenco rimane soltanto il riferimento al paragrafo
immediatamente precedente, che non contiene più la parola socio.

Non basta estendere di un paragrafo: i tre membri occupano rispettivamente
due, due e tre paragrafi. L'elenco completo ne occupa sette, oltre il limite
di sei delle precedenti continuazioni generiche. Questo secondo limite
resterebbe anche correggendo soltanto il punto di origine.

Classificazione basata sul FORM completo, non sull'obiettivo di recuperare
i valori del gold:

| Categoria richiesta | Casi fra i 18 | Riscontro |
|---|---:|---|
| Prova FORM sufficiente ma non riconosciuta | **18** | Introduzione letterale + elenco numerato e schede ripetute |
| Citazione FORM realmente insufficiente | **0** | Quote di ruolo e destinazioni già verificate nel modello originale |
| Sezione dimostrata non applicabile | **0** | Condizione `c_p39` sconosciuta in tutti i 18, non falsa |
| Associazione del modello a un diverso contesto/ruolo FORM | **0** | Tutti i riferimenti citano l'introduzione dell'elenco corretto |

L'associazione incompleta è quindi costruita dal **backend** in tutti i 18
casi della prima riga; non è un ulteriore gruppo da sommare ai 18. Nessuna
scelta di partecipazione viene dedotta dalle checkbox originali non selezionate.

La stessa causa si manifesta in due sottogruppi:

| Posizione fisica | Casi | Paragrafi |
|---|---:|---|
| Inizio del secondo/terzo membro numerato | 6 | p45, p47 |
| Continuazione dei dati di un membro | 12 | p44, p46, p48, p49 |

Le tre schede hanno **la stessa sequenza letterale di label e placeholder**
dopo la sola normalizzazione di numero dell'elemento, spazi e marker. La terza
è soltanto distribuita su più righe. Le firme ottenute dal FORM sono salvate
in `repeated-form-templates.json`; per ogni campo sono conservati testo completo,
quote, contesti precedenti, condizioni ed esito nuovo.

## 3. Correzione comune del contesto, limitata a V12

Il verificatore riconosce come prova aggiuntiva un elenco con queste proprietà:

1. Introduzione letterale terminata da due punti; se contiene campi, la quote
   di ruolo deve appartenere al testo **dopo l'ultimo placeholder**.
2. Numerazione esplicita da 1, poi consecutiva, almeno due schede con identico
   schema letterale di campi; sono ammesse diverse interruzioni di paragrafo.
3. Massimo 12 paragrafi di dati. Interrompono il legame: prosa, vuoti, heading,
   tabelle, controlli, numerazione riavviata/non consecutiva e nuove introduzioni
   esplicite. Le continuazioni con due punti restano prudentemente escluse.
4. Dentro ciascun elemento numerato i fatti personali proposti devono avere
   un unico subject coerente. Non viene inferito chi debba occupare il primo,
   secondo o terzo posto; nessun soggetto viene copiato da un altro elemento.

L'elenco deve ripetere lo schema: un nuovo campo di ruolo senza heading o due
punti, inserito in una scheda, rompe l'identità della struttura e non eredita
automaticamente il ruolo iniziale. Non vengono aggiunti sinonimi professionali,
regole su Mapi o riferimenti a ID della fixture.

La prova verificata aggiunge **solo quel paragrafo introduttivo** al contesto
ammesso per quel campo. Non amplia gli scope di condizioni, non modifica
quote o FORM, non risolve l'applicabilità. L'audit registra
`form_context_attribution`, numero dell'elemento e quote introduttiva. Le prove
locali già sufficienti restano inalterate.

Il catalogo, il FORM JSON completo, lo schema e i messaggi per l'LLM non sono
modificati. I nuovi riconoscitori di elenco operano soltanto nel verificatore
V12; V10 e le precedenti regole di continuazione non vengono aggiornati.
Il controllo di compatibilità del Comune è invece nel validatore condiviso.

Codice: [elenco verificabile](../backend/app/compilation_global.py:1092),
[associazione al binding](../backend/app/compilation_global.py:1141).

## 4. Replay dei due output fissi

Stesse risposte, stesso originale e 56 chunk SOURCE; nessun USER aggiunto,
nessuna chiamata LLM/HTTP, export DOCX o modifica di sessioni. Il gold viene
usato soltanto per la valutazione offline. Il confronto di riferimento è
l'ultimo replay KISS, non un nuovo campione del modello.

INDEX-01 originale continua a fallire per i due metadati root. Come nel replay
precedente, si usa la copia con soli `proposal_stage/project_id` isolati e tutti
i record annidati identici. Nessun filtro root viene introdotto in produzione.

| Misura, occorrenze | B0-03 prima → dopo | INDEX-01 prima → dopo |
|---|---:|---:|
| Proposte grounded localmente | 28 → **38** | 24 → **23** |
| Grounded conformi al gold | 27 → **38** | 23 → **23** |
| Grounded non conformi al gold | 1 → **0** | 1 → **0** |
| Nuove proposte corrette recuperate | **11** | **0** |
| Accettazioni errate eliminate | **1** | **1** |
| Proposte corrette precedenti perse | **0** | **0** |
| Proposte ancora bloccate | **12** | **4** |
| Risoluzioni/scritture automatiche | **0/0** | **0/0** |

Il minor numero di grounded in INDEX deriva dalla rimozione del solo valore
errato: le 23 proposte corrette sono tutte conservate. Tutti gli 11 recuperi
del precedente intervento KISS sono ancora grounded nei rispettivi replay.

Nuovi recuperi B0-03, tutti da prove tabellari SOURCE già citate:

| Persona e campo | ID | Valore |
|---|---|---|
| Luca, provincia | p44.s0 | Bari (BA) |
| Luca, data iscrizione | p44.s1 | 21/03/2012 |
| Luca, numero iscrizione | p44.s2 | 7294 |
| Elisa socio, CF | p45.s2 | RMNLSI85C47A662Y |
| Andrea, qualifica | p48.s0 | Architetto |
| Andrea, CF | p48.s1 | GRCNDR84D20A662P |
| Andrea, ordine | p49.s0 | Ordine degli Architetti di Bari |
| Andrea, sezione | p49.s1 | A |
| Andrea, provincia | p49.s2 | Bari (BA) |
| Andrea, data iscrizione | p49.s3 | 12/06/2014 |
| Andrea, numero iscrizione | p49.s4 | 5267 |

Le 18 associazioni FORM sono riconosciute; 11 proposte passano tutti i controlli
locali, sette restano respinte dal binding SOURCE. Anche il diciannovesimo
collegamento FORM è riconosciuto, ma il fatto Bari (BA) di Elisa rimane respinto.

Tutti i nuovi recuperi restano `REVIEW_REQUIRED` con `proposal_grounding`
grounded, `value: null` e condizione di partecipazione sconosciuta. **Fatti
SOURCE e condizioni sono identici prima/dopo**; il codice non estrae valori
nuovi e non seleziona sezioni o persone.

## 5. Rifiuti necessari e limiti residui

Classificazione disgiunta delle 16 proposte ancora bloccate:

| Motivo | B0-03 | INDEX-01 |
|---|---:|---:|
| Indirizzo incompatibile con il Comune | 1 | 1 |
| Citazione non prova il valore completo | 2 | 0 |
| Destinazione FORM documentata dal solo marker | 0 | 1 |
| Attribuzione del ruolo non dimostrata nel record SOURCE del valore | 9 | 2 |
| Vecchio rifiuto di contesto FORM sui soci | **0** | **0** |

Le prime cinque esclusioni complessive hanno la carenza specifica di valore,
granularità o destinazione descritta. Le altre undici restano blocchi conservativi
di attribuzione: il fatto può essere presente nel corpus, ma non viene collegato
a un ruolo cercandolo in un diverso chunk per la sola uguaglianza del nome.

Due esempi mostrano che il nuovo contesto non indebolisce i controlli:

- Il CF di Elisa socio è recuperato dalla riga della tabella dei soci. Il CF
  di Elisa direttore resta bloccato, perché quel record non attesta il ruolo
  di direttore, benché sia la stessa persona.
- Bari (BA) per Luca e Andrea passa con la propria riga SOURCE completa. Per
  Elisa in B0 restano respinti `p46.s0` e `p53.s2`: la frase -55 scelta dal fatto
  condiviso non contiene il valore completo. Nessuna occorrenza di Andrea viene
  riutilizzata. La provincia INDEX è un caso distinto, con valore citato nella
  tabella ma ruolo di direttore non dimostrato nel record.

## 6. Test, falsi positivi e conservazione

**30 nuovi casi**, test scritti prima delle correzioni. Red iniziale:
sei fallimenti attesi e 22 casi di protezione già passati. Verificati richiesta
fisica del Comune, label ingannevole del modello, valori letterali preservati,
località con nomi simili a strade, campi indirizzo/compositi, elenchi e barriere,
subject incoerenti, quote insufficienti, numerazione e limite, V10 e condizioni
esplicitamente false. Una condizione falsa resta `REJECTED` anche se la prova
di ruolo FORM diventa valida.

Durante lo sviluppo sono emersi e sono stati corretti due controesempi:

- un campo di ruolo senza due punti poteva ereditare indebitamente il contesto
  nella prima implementazione; il controllo sullo schema ripetuto lo respinge;
- «Comune e indirizzo completo» veniva respinto troppo severamente dalla prima
  regola del Comune; la richiesta composita resta ora ammessa.

Entrambi i log falliti sono conservati. Nei test negativi finali e nelle undici
catene reali recuperate **nessuna nuova accettazione indebita osservata**.
Nei replay finali anche l'errore preesistente di Comune è rimosso: zero valori
grounded non conformi al gold sui due output esaminati. Questa evidenza finita
non certifica qualunque documento o pertinenza semantica futura.

Verifiche finali: **211 mirati passati in 9,78 s; 2.374 backend passati in
206,57 s; Ruff passato.** Prima diagnostica con `form_evidence` assente sul
campo già respinto corretta usando proposta e paragrafo fisico, senza alterare
il motore. Un E501 iniziale nel nome di un test corretto; log conservati.
Frontend invariato e non rieseguito. Test software con provider simulati,
distinti dai replay di risposte reali già salvate.

Hash: **10.793/10.795 file protetti invariati**. Cambiano soltanto
`compilation_global.py` e `document_compilation.py`, con un nuovo file di test.
Le regole SOURCE della correzione KISS restano identiche. Controlli AST confermano
invariati prompt, input, verificatore SOURCE e funzioni precedenti non coinvolte;
il nuovo input B0 completo riproduce esattamente quello salvato. Originale,
fonti, gold, schema, modello/thinking, API, writer e vecchi audit preservati.

Raw: `backend/data/compilation-audit/field-context-20261017-01/`. Include codice
prima/dopo, patch, input/risposte, audit e confronti delle 267 destinazioni per
risposta, analisi FORM prima/dopo, template ripetuti, test intermedi e script
con rete disabilitata. Lo script richiede gli archivi storici per l'originale
INDEX e i confronti gold. Nessun DB, credenziale o documento generato incluso.

Nessun commit/push, migrazione o aggiornamento automatico delle sessioni.
Nessun nuovo esperimento sul provider. B0 resta riferimento; compattazione,
coverage e thinking restano invariati.
