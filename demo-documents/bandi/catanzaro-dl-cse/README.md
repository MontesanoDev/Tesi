# Caso di prova: domanda di partecipazione DL/CSE Catanzaro

**Obiettivo:** partire da un modulo Word reale e predisporre la sua compilazione
assistita con dati aziendali e fonti tracciabili. Non generare un testo libero
che assomiglia a una domanda.

Questo pacchetto prepara gli input e i risultati attesi. Il backend ora dispone
di una [pipeline DOCX separata](../../../backend/docs/compilazione-docx.md):
lettura del modulo, proposte LLM, controlli, scrittura e download. Il percorso e
collegato alla UI **Template > Word (.docx)**.

## La gara

Fondazione Universita Magna Graecia di Catanzaro: servizi di direzione lavori e
coordinamento della sicurezza in esecuzione per nuove residenze universitarie,
III lotto. CIG `B9304DFF59`, CUP `C65E19000450002`.

[Pagina ufficiale e allegati](https://piattaforma.asmecomm.it/gare/dettaglio.php?codice=84051).
Gara pubblicata nel 2025, con termine di presentazione il 30 dicembre 2025:
**caso storico, non una candidatura da inviare**. Le societa di ingegneria sono
fra i soggetti contemplati dal disciplinare, sezione 5. Questo rende pertinente
il caso, ma non dimostra che Mapi possieda i requisiti.

## File pronti

| File | Uso |
| --- | --- |
| [Bando PDF](originali/bando.pdf) | Oggetto e regole della gara, fonte del progetto |
| [Disciplinare PDF](originali/disciplinare.pdf) | Requisiti, documenti e modalita di partecipazione, fonte del progetto |
| [Domanda DOC originale](originali/domanda-partecipazione.doc) | Originale scaricato, non modificato |
| [Domanda DOCX di lavoro](modello/domanda-partecipazione.docx) | Modello vuoto convertito, per sviluppare il riempimento delle celle |
| [Mappa dei campi](mappa-campi.json) | Celle reali, valori proposti, fonti/pagine, dati mancanti e decisioni |
| [Casi di verifica](casi-verifica.md) | Comportamenti attesi per la futura pipeline |
| [Manifest delle fonti](fonti.json) | URL degli allegati, date, ruoli e SHA-256 |

Fonte aziendale di confronto: [visura Mapi simulata](../../visura-mapi-ingegneria-simulata.pdf).
Contiene dati inventati, non certificazioni utilizzabili per una pratica.

## Cosa si riesce gia a ricavare

La mappa copre **36 campi**, non l'intero documento per tutte le possibili forme
di partecipazione. Distingue il sottoscrittore, l'azienda e il direttore tecnico,
anche quando nel modulo compare piu volte la stessa etichetta.

| Dato richiesto | Situazione nel dataset Mapi |
| --- | --- |
| Ragione sociale, forma giuridica, sede | Disponibili nella visura demo, pagina 1 |
| Amministratore e direttore tecnico | Luca Ferri ed Elisa Romano, pagina 2; ruoli distinti |
| Ordine e numero del direttore tecnico | Disponibili come dati simulati, pagina 2 |
| Telefono | Presente; cellulare assente |
| Nascita, CF e residenza delle persone | Mancanti; non si deducono dal nome o dalla sede aziendale |
| Estremi completi CCIAA/Registro Imprese | Non completi; REA e numero di iscrizione non vanno confusi |
| Data di abilitazione del direttore tecnico | Mancante |
| Importi dei servizi pregressi per categoria | Mancanti; quelli prestampati nel modulo riguardano la gara |
| Forma singola/RTI, deleghe, dichiarazioni | Richiedono scelta o conferma, non inferenza dall'assenza di dati |
| DGUE, organigramma, allegati e firma | Non prodotti da questo pacchetto |

Il ramo `5.d - Societa di ingegneria` e quello candidato per la demo.
Va confermato, non selezionato soltanto perche il nome contiene "Ingegneria".
La partecipazione singola o associata e una decisione separata.

**Avvertenza temporale:** la visura demo e del 6 agosto 2026, successiva alla
gara. I valori servono a provare l'estrazione e la corrispondenza dei campi,
non ad attestare lo stato dell'impresa nel 2025. In particolare non vanno usati
i ricavi 2025 o la polizza 2026 come prove automatiche dei requisiti storici.

## Il percorso backend

Il primo risultato implementato e una **bozza DOCX parziale con report**:

```text
Domanda DOCX + fonti aziendali + documenti della gara
    -> individua campi e ramo pertinente
    -> recupera evidenze per ogni campo
    -> produce proposte strutturate: valore, fonte, pagina, stato
    -> valida corrispondenza dei campi, mancanze e conflitti
    -> scrive solo nelle celle autorizzate di una copia del modello
    -> restituisce DOCX + report dei campi irrisolti
```

Il system prompt governa i limiti dell'agente: non inventare, non dichiarare
requisiti soddisfatti senza evidenze, non confondere i soggetti, non firmare.
**Non sostituisce il codice** che legge il modello, verifica lo schema dei
risultati e scrive il documento.

La mappa JSON e una fixture manuale per questo modello: permette di verificare
le future proposte dell'LLM, ma non e un parser universale di bandi.
Un primo writer puo usare queste celle note; la scoperta automatica dei campi
di un nuovo modulo resta un problema separato.

Le dichiarazioni prestampate richiedono attenzione anche se non hanno caselle:
lasciarle nel documento non equivale ad averne verificato la verita. Una bozza
con dati mancanti o dichiarazioni non confermate deve essere identificata come
**bozza non pronta alla sottoscrizione**, sia nel file sia nel report.

Nell'app il punto d'ingresso resta **Template**: modello caricato, generazione
esplicita, revisione e download. L'output appartiene al progetto e non diventa
una nuova fonte Company/General KB. Non serve una nuova schermata per preparare
questa prova; i Call Facts non sono stati cambiati.

Il modulo DOCX e caricabile sia tramite API sia da **Template > Word (.docx) >
Carica modello**. **Compila Word** avvia la generazione; il risultato mostra
campi, citazioni e avvisi con download di bozza, originale e report. Il formato
**Testo (.md / .txt)** conserva il precedente flusso Markdown.

## Conversione e limiti

Conversione locale con LibreOffice Writer 26.2.5.2:

```bash
soffice --headless --convert-to 'docx:MS Word 2007 XML' \
  --outdir modello originali/domanda-partecipazione.doc
```

Sono presenti 50 tabelle, 28 caselle Word legacy e 7 note a pie di pagina.
Il modello e rimasto vuoto: nessun valore Mapi inserito, nessuna casella spuntata.

Ho confrontato rendering PDF del DOC originale e del DOCX con LibreOffice:
entrambi producono 17 pagine nell'ambiente locale, ma note e alcuni blocchi
flottanti si spostano. Sono state ispezionate anche le pagine con anagrafica,
direttore tecnico e dichiarazioni finali. **La conversione non e approvata per
uso amministrativo**; prima dell'esportazione finale va verificata in Word o
con un modello DOCX nativo fornito dai relatori. I PDF di controllo sono
temporanei, non allegati ufficiali.

Gli indici della mappa sono riferiti all'XML del DOCX, non alle pagine renderizzate.
La combinazione di hash del file, coordinate di cella ed etichetta evita di
riempire silenziosamente il campo sbagliato se il modello cambia.

LibreOffice e stato usato da una directory temporanea: nessuna dipendenza
aggiunta al backend e nessuna installazione di sistema.

## Verifica ripetibile

Dalla radice del repository:

```bash
backend/.venv/bin/python demo-documents/bandi/catanzaro-dl-cse/verifica_fixture.py
```

Controlla integrita degli originali, struttura DOCX, celle vuote, etichette,
caselle non selezionate, riferimenti alle fonti e presenza delle evidenze nelle
pagine dichiarate. Usa `pypdf`, gia presente nel backend.

**Non misura ancora un agente:** i casi funzionali nel documento separato sono
specifiche di accettazione, non risultati di un benchmark gia eseguito.
