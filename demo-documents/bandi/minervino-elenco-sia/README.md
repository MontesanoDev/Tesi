# Seconda prova esplorativa: elenco SIA di Minervino di Lecce

Caso aggiunto il 18 settembre 2026. **Prova didattica, non una candidatura reale,
un benchmark o una verifica di ammissibilita' della societa'.**

## Origine e scelta del caso

[Avviso e allegati ufficiali del Comune di Minervino di Lecce](https://comuneminervinole.tuttogare.it/albo_fornitori/dettaglio.php?codice=1),
pubblicati il 26 agosto 2025 per un elenco relativo a servizi di ingegneria e
architettura. Si prova la domanda di iscrizione, non l'intera pratica e non
gli ulteriori modelli di dichiarazione richiesti dall'avviso.

- [Avviso PDF](originali/avviso.pdf): fonte di progetto.
- [Domanda DOCX originale](originali/domanda-iscrizione.docx): modello da compilare.
- [URL, hash e data di acquisizione](fonti.json): hash verificati contro quelli
  pubblicati dal portale ufficiale.
- [Indicazioni della prova](istruzioni.txt): fissate prima della chiamata.
- Fonte aziendale: [Generalita' Mapi simulate](../../generalita-mapi.md), identica
  alla precedente prova Catanzaro.

Il DOCX e' nativo: nessuna conversione, modifica dei segnaposti o precompilazione.
Non sono stati scaricati elenchi nominativi di altri professionisti iscritti.

## Perimetro della prova

Si usa il compilatore attuale senza modifiche, stesso system prompt v5, stesso
provider e configurazione; nessuna mappa manuale viene fornita al modello.
Il backend viene invocato tramite la vera API FastAPI in un database temporaneo:
non si modificano progetti, KB e compilazioni dell'applicazione dell'utente.

Una sola compilazione, inclusi i tentativi limitati gia' previsti in produzione.
Non si rilancia per ottenere un risultato favorevole e non si corregge il
compilatore durante questa prova. Si conservano anche errori e risposte grezze.
Il test usa avviso, scheda aziendale e indicazioni; nessuna estrazione preventiva
dei facts e nessuna fonte Catanzaro viene caricata nel nuovo progetto isolato.

## Cosa controllare

Prima della generazione si fissano questi criteri qualitativi, non un punteggio:

1. Nome del sottoscrittore scelto, carica e dati aziendali devono riferirsi a Mapi,
   non all'amministrazione. Il direttore tecnico deve restare distinto dal firmatario.
2. Sono ammesse l'anagrafica iniziale e i dati della societa'/direttore tecnico nel
   ramo societario. Professionista individuale, associati, raggruppamenti e consorzi
   devono restare vuoti; i nomi disponibili non provano la qualita' di socio.
3. Nascita, CF personale, residenza, deleghe ed estremi camerali non documentati
   non devono essere inventati. Il REA non completa il numero del Registro Imprese.
4. Non selezionare settori/fasce, firmare, datare o attestare requisiti e allegati.
   Il prestampato dichiarativo rimane nel modulo, ma non viene validato dalla prova.
5. Controllare ripetizioni, etichette preservate, puntini residui, corrispondenza
   tra report e Word, citazioni e integrita' delle parti del pacchetto DOCX.

## Osservazioni preliminari sul parser

Il parser di produzione accetta il documento e individua **281 posizioni
candidate: 67 celle e 214 segnaposti nei paragrafi**. Segnala 15 paragrafi con
contenuti complessi esclusi dalla modifica. Non sono 281 dati necessari.

Le celle delle tabelle riguardano soprattutto scelte di categorie/fasce, mentre
anagrafica e rami societari sono nei paragrafi. Alcune righe miste di puntini ed
ellissi vengono spezzate in piu' segnaposti, anche adiacenti: questo potrebbe
causare ripetizioni o lasciare marcatori residui. E' un limite da osservare,
non da correggere preventivamente per questo documento.

## Esito della prova

Il Word e' stato prodotto al primo tentativo: 9 chiamate, 430.061 token,
84,83 secondi. Sono stati scritti 37 segnaposti, ma 12 nei rami associati esclusi.
Alcuni indirizzi e-mail/PEC risultano malformati per la suddivisione della linea
in piu' segnaposti. Non sono 37 campi logici completati correttamente.

[Resoconto completo, Word prodotto e report](../../../verifica-compilazione-minervino.md).
I limiti osservati non sono stati corretti durante la prova.
