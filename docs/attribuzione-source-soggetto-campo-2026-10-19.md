# Attribuzione SOURCE, soggetto e campo: correzione e prova casuale

19 ottobre 2026 — esperimento `source-attribuzione-20261019-01`.

**Correzione mirata PASS:** le sette attribuzioni Cesano non dimostrate sono
respinte; le scritture corrette dei riferimenti restano intatte.
**Nuova prova casuale Catanzaro:** bozza parziale utilizzabile, 15 valori
leggibili, nessuna scrittura non supportata o nel soggetto/sezione sbagliati
rilevata nella revisione. Copertura e dialogo rimangono incompleti.
Non è una certificazione generale del compilatore né un'adozione della baseline.

[Consegna](<../benchmark ufficiale/source-attribuzione-20261019-01/README.md>),
[sette casi](<../benchmark ufficiale/source-attribuzione-20261019-01/CESANO-SETTE-CASI.json>),
[regressione](<../benchmark ufficiale/source-attribuzione-20261019-01/regressione.json>),
[risultato E2E](<../benchmark ufficiale/source-attribuzione-20261019-01/E2E-RISULTATO.json>).

## 1. Causa riprodotta, distinta dalla validità dei fatti

La risposta reale Cesano dell'esperimento FORMTEXT contiene otto fatti
aziendali con citazioni valide, otto assegnazioni `conditional`, nessun binding
personale. Dopo la conferma USER del ramo societario, otto assegnazioni erano
esportabili. La conferma non prova che lo studio, la PIVA e i recapiti del
sottoscrittore coincidano con quelli dell'azienda.

Il controllo personale preesistente si attiva con `fact.entity=person` oppure
con un `binding_id`. Il modello aveva dichiarato tutti i fatti `company`:
la prova letterale dei dati aziendali superava i controlli, senza una verifica
indipendente del soggetto richiesto dal FORM. Il narratore aveva revisionato
le proposte senza sospenderle; il writer le aveva scritte nelle posizioni
esattamente ricevute. Parser FORMTEXT e writer non causavano questi errori.

Il FORM apre il periodo con «Il sottoscritto», poi chiede nascita, studio,
PIVA, posizioni previdenziali, recapiti e iscrizione professionale. Non introduce
un nuovo soggetto aziendale prima di quei sette campi. La denominazione della
società è invece richiesta in un altro periodo esplicito.

| Destinazione | Dato SOURCE proposto | Attribuzione mancante |
|---|---|---|
| p12.ft3, comune studio | Bari, sede legale aziendale, chunk -52 | Sede legale → studio della persona |
| p12.ft4, via studio | Via Giovanni Amendola, -52 | Indirizzo aziendale → studio personale |
| p12.ft5, civico studio | 172/C, -52 | Civico della sede → studio personale |
| p12.ft6, PIVA | IT01234567890, -43 | Identificativo societario → PIVA del sottoscrittore |
| p12.ft10, email | segreteria@mapi-ingegneria.demo, -44 | Recapito aziendale → recapito della persona |
| p12.ft11, PEC | mapi.ingegneria@pec.demo, -44 | PEC aziendale → PEC della persona |
| p12.ft12, telefono | +39 080 000 2040, -44 | Telefono aziendale → telefono della persona |

Non sono sette fatti societari falsi: sono sette trasferimenti non dimostrati.
Soggetto aziendale, firmatario e professionisti restano distinti. La qualifica
di rappresentante o direttore non trasferisce proprietà anagrafiche, contatti,
poteri o incarichi di esecuzione da un soggetto all'altro.

## 2. Modifica minima e limiti intenzionali

Aggiunto un controllo necessario del soggetto fisicamente richiesto dal FORM,
indipendente da etichette, condizioni e soggetti dichiarati dal modello.
Riconosce introduzioni esplicite e ordinate nello stesso paragrafo, fino
all'esatta destinazione: sottoscrittore, firmatario, professionista, nome e
cognome, direttore tecnico; denominazione, sede legale, società/impresa/operatore.
Un'introduzione aziendale successiva non cambia il soggetto dei campi precedenti.
Un passaggio esplicito alla società permette di conservare i dati societari
nei campi successivi, come nei paragrafi misti di Minervino e Bella.

Un contrasto fra tipo di soggetto richiesto e fatto SOURCE respinge
l'assegnazione con `source_subject_type_mismatch`. La compatibilità del tipo
non prova identità, ruolo o proprietà: gli altri controlli restano necessari.
Inoltre, qualificatori di luogo esplicitamente incompatibili nella citazione
e nella richiesta locale, per esempio residenza contro studio, producono
`source_property_scope_mismatch`. Non vengono estratti, modificati o sostituiti
valori per renderli accettabili.

I sette casi vengono respinti dal primo controllo; il comune studio espone
anche il contrasto esplicito sede legale/studio. I fatti restano grounded
come fatti aziendali. Nell'audit delle assegnazioni respinte restano valore
proposto, citazioni, soggetto SOURCE e prova FORM del contrasto.

**Ambito effettivamente implementato:** proposte di valore V12 verso campi
inline con introduzioni esplicite riconoscibili. Non è un interprete generale
dei soggetti in qualunque prosa o tabella; non estende il contesto fra paragrafi
e non crea un nuovo risolutore per le celle tabellari. Dove non determina il
soggetto, non produce una nuova prova positiva e mantiene i controlli storici.
Questa limitazione va conservata nelle conclusioni della tesi.

La modifica può soltanto escludere proposte. Non promuove UNKNOWN, non rende
valide citazioni o binding respinti e non unisce persone per somiglianza del
nome. Nessuna trasformazione arbitraria di studio, residenza, recapiti o ruoli.

I controlli compatibili non aggiungono metadati all'audit persistito: altrimenti
cambierebbero le impronte delle revisioni già valide. I replay confermano
la conservazione delle revisioni, dei valori e delle checkbox. Le vecchie
sessioni non sono migrate o modificate; gli export storici restano artefatti
storici, compreso quello Cesano con le sette attribuzioni problematiche.

## 3. Prima/dopo effettivo Cesano, stesso output reale

Replay senza rete della risposta reale già acquisita e delle sole ricevute
registrate, senza LLM o nuove scelte USER. Entrambi i DOCX sono conservati.

| Misura | Prima | Dopo |
|---|---:|---:|
| Proposte di valore del modello | 8 | 8 |
| Fatti aziendali grounded | 8 | 8 |
| Assegnazioni grounded conservate | 8 | 1 |
| Valori effettivamente scritti | 8 | 1 |
| Corrispondenze soggetto/campo dimostrate | 1 | 1 |
| Attribuzioni non dimostrate scritte | 7 | 0 |
| Nuove checkbox | 0 | 0 |
| Campi testuali vuoti, su 20 | 12 | 19 |

Rimane `p19.ft0`, denominazione della società di ingegneria. Restano omessi
nome e luogo/data di nascita del firmatario, pur disponibili nelle SOURCE;
rimangono assenti gruppo e selezione della checkbox societaria. Non sono stati
corretti in questa fase. Il miglioramento è l'eliminazione delle scritture non
dimostrate, non un aumento artificiale del conteggio.

[DOCX prima](<../benchmark ufficiale/source-attribuzione-20261019-01/replay/cesano-reale-8/prima.docx>),
[DOCX dopo](<../benchmark ufficiale/source-attribuzione-20261019-01/replay/cesano-reale-8/bozza.docx>),
[PDF dopo](<../benchmark ufficiale/source-attribuzione-20261019-01/replay/cesano-reale-8/bozza.pdf>).
Tre pagine; denominazione leggibile a pagina 1; sette campi esclusi vuoti.

## 4. Test permanenti e regressione

Test aggiunti prima della correzione. La riproduzione valida iniziale registra
25 fallimenti e 11 passaggi; due errori iniziali nella preparazione della
fixture/quote del test sono conservati separatamente, non sono difetti
applicativi. Successivamente aggiunti tre negativi su omonimia e binding.

[39 nuovi casi](../backend/tests/test_compilation_source_attribution.py):
risposta reale Cesano; etichette/entità MODEL ingannevoli; passaggio persona–società;
campi societari compatibili; PEC personale con binding valido; UNKNOWN conservato;
assenza di binding, altra persona, altro ruolo, quote inventate; residenza/studio;
omonimia persona/impresa e record personali con identificativi conflittuali.
La fixture reale è salvata in
[source-attribution-v1](../backend/tests/fixtures/source-attribution-v1/README.md).
Non entra nella KB o nei prompt.

Eseguiti: **324 test mirati PASS**, **2.721 backend PASS in 211,25 s**,
**Ruff PASS**. I 39 nuovi casi sono stati verificati anche separatamente sulla
versione finale: 2,54 s. Nessuna suite frontend ripetuta: nessuna modifica UI.

| Documento/riferimento | Scritture prima | Dopo | Catalogo e DOCX |
|---|---:|---:|---|
| Minervino, benchmark ufficiale | 55 | 55 | identici |
| Trapani | 10 | 10 | identici |
| Catanzaro, benchmark ufficiale | 13 | 13 | identici |
| Bella | 4 | 4 | identici |
| CRAA | 9 XML | 9 XML | identici |
| Cesano, vecchio output senza testi | 0 | 0 | riferimento post parser conservato |
| Minervino V12, chat a 61 | 61 | 61 | identici, 60 testi + checkbox |
| Cesano, nuova risposta reale FORMTEXT | 8 | 1 | solo le sette esclusioni attese |

Audit dei sei riferimenti ricalcolati uguali al precedente replay post parser.
Nessuna nuova accettazione e nessuna perdita di scritture corrette nei riferimenti.
I riferimenti non sono nuovi GOLD: PEC Trapani senza consenso e due CCIAA CRAA
invisibili rimangono difetti storici, non correzioni o regressioni di questa fase.

Renderizzati otto replay, 57 pagine; zero parole fuori pagina. I sette export
invariati hanno parole e coordinate identiche ai PDF precedenti. Per Catanzaro
l'estrazione testuale intercalata segnala falsamente due indirizzi assenti;
non è una nuova perdita. Per CRAA trovare «Bari» altrove nel PDF non dimostra
la visibilità del valore CCIAA: il precedente difetto resta documentato.

## 5. Estrazione e configurazione prima dell'E2E

[Estrazione completa](<../benchmark ufficiale/source-attribuzione-20261019-01/ESTRAZIONE.json>).
Pool di convenienza: otto originali scaricati nel precedente campionamento,
meno Cesano, più tre storici, deduplicati per hash: **10 moduli**. Esclusi
GOLD, bozze e duplicati. Tutti gli originali del pool esistenti e hash verificati.
Non è un campione rappresentativo di tutti i bandi.

Seed generato una volta: **13243375443350163391**. Algoritmo:
`random.Random(seed).choice(sorted(pool, key=slug))`. Estratto **Catanzaro**;
nessuna ripetizione o sostituzione. Documento e scenario registrati prima
di qualsiasi nuova chiamata. Il riferimento autoriale era già congelato nel
benchmark storico e non è stato adattato al nuovo output né inviato al modello.

HEAD `99ab052`, working tree preesistente sporco, conservato.
Snapshot applicativo dopo correzione SHA-256:
`ade21881fe3f7397dc91af64a8ff5857539570ebc5efd776c4878d7615b3d8c7`.
Elenco degli hash in [VERSIONE.json](<../benchmark ufficiale/source-attribuzione-20261019-01/VERSIONE.json>).

Stessi 22 chunk Company/General del precedente snapshot, nessuna nuova SOURCE.
Stesso modello richiesto/restituito `deepseek-flash`, fingerprint effettivo
`e72d3c7f663d3e1383b00b3884cb4501`. L'API restituisce l'alias, non un identificativo
immutabile dei pesi. Thinking globale enabled/low; sintesi e routing invariati.
Parametri fuori dai messaggi e system prompt confrontati con il riferimento
prima dell'inoltro. System prompt SHA-256:
`978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`.

Lo scenario sintetico definisce esplicitamente per questa prova la partecipazione
singola dell'azienda come società di ingegneria e Leonardo come firmatario.
Sono decisioni della prova specifica, non inferenze da un'altra gara. Le proprietà
personali, carica e poteri restano da provare nelle SOURCE. Preferenze,
attestazioni, esecutori, integrazione, luogo/data rimangono UNKNOWN e separati.
Massimo due turni di risposta ai soli chiarimenti chiesti, poi export ordinario.

La preparazione ha intercettato un confronto del prompt preflight senza
`user_context` contro il prompt reale con contesto USER: corretto lo script
di acquisizione prima della chiamata, non il prompt applicativo. Nessuna
generazione è stata eseguita con la configurazione di preflight errata.

## 6. Percorso reale e risultato Catanzaro

Nuovo progetto `attribuzione-source-catanzaro`, FORM181, sessione
`b47a62f824894850bab0c058b322051a`, conversazione `conv-1c8692b5cb1a4eaf`.
Stato finale GENERATED, versione 10. Chat UI reale con browser, senza API
simulate, nuove proposte globali reali, nessun intervento sullo stato interno.

Primo turno USER: conferme di partecipazione e sezione 5.d. Secondo: scelta
Leonardo, titolo di firma come rappresentante legale, rinvio degli estremi
procura. Nome e carica registrati come USER, non come false prove SOURCE;
entrambi hanno riscontro indipendente nelle SOURCE -53/-54. Export richiesto
esplicitamente, scaricato e verificato dopo refresh.

| Fase | Numero |
|---|---:|
| Record fields grezzi | 16 |
| Proposte di valore SOURCE | 15 |
| Altro record: sede operativa diversa, non applicabile | 1 |
| Fatti grounded | 13 |
| Assegnazioni di valore grounded | 13 |
| Assegnazioni grounded applicabili dopo ricevute USER | 13 |
| Assegnazioni SOURCE revisionate e scritte | 13 |
| Valori USER scritti, con riscontro SOURCE indipendente | 2 |
| Scritture totali XML e PDF | **15** |
| Valori SOURCE corretti | 13, uno in proprietà composta incompleta |
| Attribuzioni non dimostrate / sezioni sbagliate rilevate | **0 / 0** |
| Checkbox selezionate/deselezionate | **0 / 0** |

Nove scritture SOURCE riguardano l'azienda, quattro il direttore tecnico
Elisa Romano: nome con titolo attestato, qualifica, ordine, numero d'iscrizione.
Non è stata designata come esecutrice della prestazione e non è stata confusa
con il firmatario. Il dato nel campo «numero e data d'iscrizione» contiene solo
il numero: è supportato, ma il campo è parziale e la data disponibile è omessa.

Le differenze giustificate dal riferimento sono esplicite: «Societa» senza
accento è la grafia letterale SOURCE, l'indirizzo completo include «Italia»
attestata, «Ing. Elisa Romano» contiene un titolo documentato. Non sono errori
perché non uguali letteralmente al riferimento. Nessuna percentuale di accuratezza
ottenuta da uguaglianza testuale o dal numero di campi compilati.

[DOCX reale](<../benchmark ufficiale/source-attribuzione-20261019-01/e2e/catanzaro/bozza.docx>),
[PDF](<../benchmark ufficiale/source-attribuzione-20261019-01/e2e/catanzaro/bozza.pdf>),
[dialogo](<../benchmark ufficiale/source-attribuzione-20261019-01/e2e/catanzaro/dialogo.md>),
[valutazione di tutti i 307 candidati](<../benchmark ufficiale/source-attribuzione-20261019-01/e2e/catanzaro/valutazione-campi.json>).

## 7. Residui conservati, senza correzioni nel benchmark

Il riferimento storico contiene **31 posizioni SOURCE**, non 31 fatti atomici
indipendenti né tutti i campi obbligatori del modulo. Quindici posizioni sono
scritte, sedici vuote; una delle quindici manca della componente data.
Fra le sedici: quattordici proposte omesse e due respinte. Le SOURCE attese
sono tutte nell'input. Nome/carica iniziali sono recuperati dal dialogo USER,
non dal riuso automatico dell'anagrafica SOURCE.

Residui dimostrati:

- Nascita e CF del firmatario, telefono aziendale iniziale: dati disponibili
  nell'input, omessi, partecipazione già confermata. Non dipendono da nuove
  risposte USER sui loro valori.
- CCIAA `t25.r2.c0`: valore Bari proposto, citazione FORM nel paragrafo della
  riga precedente, esterna al contesto consentito della destinazione vuota.
  Il fatto SOURCE è valido; il controllo strutturale respinge la proposta.
- Nome del direttore in `t44.r1.c0`: intestazione di tabella non marcata come
  header ripetuto, più binding ancorato all'altra sezione del direttore tecnico.
  Citazione FORM e binding locale respinti. La persona/ruolo sono attestati:
  il rifiuto non dimostra assenza del dato nelle SOURCE.
- Dieci posizioni su amministrazione/rappresentanza nelle tabelle 41/43 non
  proposte; nome/CF del direttore nella Parte terza non scritti. La condizione
  MODEL della Parte terza resta UNKNOWN, pur descrivendo una natura giuridica
  già documentata/confermata. Non è una nuova decisione USER dimostratamente
  mancante: manca il collegamento di pipeline alla condizione. Non è forzata.
- Nessun `choice_group` proposto. Natura dell'operatore e partecipazione
  singola restano senza spunta anche se le decisioni esistono. Tutte le
  checkbox native sono conservate; nessun consenso o attestazione inventato.
- Cinque domande in due turni: quattro chiedono conferme/scelte già espresse
  nel messaggio iniziale, necessarie oggi per ottenere le ricevute attive ma
  ridondanti sul piano informativo. La procura è una domanda condizionata al
  procuratore, benché sia scelto il rappresentante legale; resta rinviata.
  Nessuna domanda identica ripetuta dopo la relativa ricevuta accettata.

Condizioni effettive ancora UNKNOWN: concordato, Parte terza, RTI e forma di
partecipazione. RTI/partecipazione singola erano già indicati dall'utente;
assenza di un collegamento non equivale a scelta mancante. Concordato e altre
dichiarazioni non sono inventati. Sede operativa diversa è FALSE perché le due
sedi SOURCE coincidono: campo correttamente vuoto. Zero hold finali in questa
prova; non è una nuova prova positiva sugli hold legittimi.

Il nucleo incompleto, le associazioni FORM locali rifiutate e le checkbox
rimangono problemi importanti. Nessun intervento per migliorare il punteggio,
nessuna seconda generazione o correzione del DOCX.

## 8. Integrità, leggibilità, costi e confronto

DOCX reale SHA-256
`433c3eb3aba3ba7b86fe48698fa6dc5fdba7ac6236a3607a4d3453cae9857960`.
ZIP/CRC e tutti gli XML validi; quindici valori nelle celle corrette, 50 tabelle,
geometrie e prestampato conservati. Solo `word/document.xml` differisce;
download UI identico all'export. Checkbox e firme intatte. Il testo prestampato
su allegati e dichiarazioni resta quello dell'originale, non prova che allegati
siano stati prodotti o requisiti attestati.

PDF LibreOffice di **17 pagine**, zero parole fuori pagina. Viste pagine
**1, 2, 11, 17**: tutti i quindici valori leggibili, indirizzi nelle celle
corrette anche quando l'estrazione testuale intercalata non li trova come
stringa continua. Non si dichiara una revisione visiva di ogni pagina o un test
in Microsoft Word desktop.

Dieci chiamate: **1 globale, 4 router, 2 guard, 3 sintesi**. Tutte HTTP200,
finish stop; nessun retry di qualità. **135.085 token input + 46.301 output =
181.386**; reasoning incluso nell'output, non aggiunto una seconda volta.
La globale genera 45.115 token output, di cui 35.332 di reasoning secondo
l'usage del provider. La data d'iscrizione omessa è attestata dai chunk -43/-30;
il numero aggiornato è nel -52: sono prove distinte dello stesso dato composto.
Globale **181,33 s**, somma tempi HTTP **193,16 s**, browser **337,32 s** incluse
pause operative. Costo **0,043697 USD stimati**, non fattura, dalla tariffa
ufficiale congelata e dall'usage/cache acquisito. Dieci GET annullate su
mount/refresh (`net::ERR_ABORTED`), nessun altro errore browser registrato;
trace e video finalizzati. Nessun errore provider.

Rispetto al vecchio Catanzaro: 13 SOURCE restano 13 SOURCE, ma cambia la loro
composizione; ora il numero registro è scritto e il telefono è omesso. Si
aggiungono due valori USER nel dialogo reale. Non è una misura causale di
incremento qualità attribuibile alla correzione: nuova inferenza, una sola
replica, nessun controllo A/B. La riduzione causale delle sette scritture
Cesano è dimostrata dal replay dello stesso output; Catanzaro verifica il
percorso reale congelato su un altro documento.

## 9. File, conservazione e punto di arresto

Modifiche applicative: nuovo `compilation_attribution.py` e import/più sei righe
nel verificatore V12 di `compilation_global.py`. Nuovo file di test e due file
di fixture. Nessuna modifica a parser FORMTEXT, writer, modello, API, prompt,
contratti di risposta, schema DB o dialogo. Nessun framework o regola basata
su nomi Mapi/Minervino/Cesano o ID specifici nel codice applicativo.

[Elenco preciso dei file](<../benchmark ufficiale/source-attribuzione-20261019-01/FILES-MODIFICATI.json>).
Script di acquisizione e verifiche conservati nei grezzi, non nel codice del
prodotto. Preservati 967 altri file precedenti, 279 file dell'audit precedente,
29 sessioni live e 285 file storage; nel clone 33 sessioni precedenti intatte
e una sola nuova. Applicazione congelata per tutta la prova finale; servizi
isolati arrestati. Snapshot e backup con hash nella consegna; niente DB o chiavi
nel backup distribuibile. STATUS e relazioni aggiornati.

**Arresto dopo rapporto e consegna**, come richiesto. Nessun commit/push,
nessuna nuova fase di correzione o compattazione avviata.
