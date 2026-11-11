# Campi legacy FORMTEXT: riconoscimento e scrittura controllata

19 ottobre 2026. Intervento limitato al parser/writer strutturale e ai suoi test.
Nessuna chiamata LLM, modifica al prompt globale, al grounding, al dialogo,
alle API o al database; nessun commit/push. Il benchmark precedente rimane
immutato, inclusi i fallimenti.

## Risultato verificato e limite della misura

Cesano passa da **0 a 20 destinazioni testuali**, mantenendo le **68 checkbox**:
il catalogo reale passa da 68 a 88 candidati. Tutte le nuove destinazioni sono
nell'input costruito dalla stessa funzione usata dalla globale V12. Gli ID e i
record dei candidati precedenti restano identici.

La prova di scrittura distingue due controlli:

- **20 valori sentinella sintetici:** verificano tutte le destinazioni, comprese
  quelle di rami alternativi e la data. È una prova meccanica del writer, non
  una domanda ammissibile o una valutazione di grounding/applicabilità.
- **Quattro valori SOURCE:** nome, luogo/data di nascita e denominazione
  societaria dello scenario preregistrato. Passano i controlli locali esistenti
  sul valore/citazione e vengono scritti nelle destinazioni di prova indicate
  esplicitamente dal banco di test. Non sono nuove proposte del modello,
  ricevute USER o una compilazione autonoma della chat.

Entrambi i DOCX sono validi e producono PDF di tre pagine. Tutti i 20 sentinella
e i quattro valori SOURCE sono nel testo PDF; nessuna parola fuori pagina.
Viste le pagine 1 e 3 di entrambi, con valori leggibili e chiusura/firma
prestampata conservata. Nessuna verifica su Microsoft Word desktop.

**Non ho dimostrato che una nuova globale proporrà o compilerà tutti i dati.**
Il replay della vecchia risposta Cesano, che proponeva zero valori, resta
correttamente a zero: nessun riempimento retroattivo o promozione automatica.
La misura di qualità della futura chat richiederà una nuova prova separata.

## 1. Diagnosi XML

Originale congelato:
`benchmark ufficiale/casuali-v12-20261019-01/cesano/FORM-originale.docx`,
SHA-256 `9386c79ef24b99c9e6b70eca9e1dbee5de187febc241f1d87b5ce3787016e795`.

I 20 campi non sono underscore o celle vuote. Sono campi complessi Word
con struttura:

```xml
<w:fldChar w:fldCharType="begin">
  <w:ffData><w:name w:val="Testo1"/><w:textInput/></w:ffData>
</w:fldChar>
<w:instrText> FORMTEXT </w:instrText>
<w:fldChar w:fldCharType="separate"/>
<!-- risultato: cinque w:t con uno spazio U+2002 ciascuno -->
<w:fldChar w:fldCharType="end"/>
```

Quindici sono nello stesso paragrafo, quattro seguono alternative di
rappresentanza e uno è la data finale. Tutti hanno delimitatori completi,
istruzione FORMTEXT, proprietà textInput senza formato/tipo speciale e
risultato vuoto. Il nome interno **Testo1 è ripetuto 20 volte**: non è una
chiave affidabile. Alcuni paragrafi contengono anche una checkbox legacy
distinta, che deve conservare il proprio ID e stato.

Il parser precedente segnava come non sicuro ogni paragrafo contenente
`fldChar` o `instrText`, quindi scartava anche questi campi validi. La chat
poteva partire perché ammette documenti senza destinazioni testuali; esponeva
soltanto le checkbox. Il modello non aveva ID sui quali proporre i testi.

La distinzione tra istruzione, delimitatori e risultato segue la documentazione
primaria di [Microsoft, FieldChar](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fieldchar?view=openxml-3.0.1).
Le proprietà textInput appartengono a FORMTEXT e possono includere tipo,
lunghezza e formato: [Microsoft, TextInput](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.textinput?view=openxml-3.0.1).
Nessuna conversione del file originale è necessaria.

## 2. Correzione generale

Unico file applicativo modificato: [docx_templates.py](../backend/app/docx_templates.py).

Il parser verifica le coppie di delimitatori nel corpo, distinguendo campi
indipendenti da annidamenti e campi che attraversano paragrafi. Espone soltanto
FORMTEXT semplici, vuoti, abilitati, non bloccati e delimitati nello stesso
paragrafo, con risultato testuale. Restano protetti anche i contenitori
complessi e le continuazioni di celle unite.

Gli ID `p{paragrafo}.ft{indice}` usano posizione del paragrafo e ordine dei
textInput nell'originale; l'indice include anche i campi precompilati lasciati
in sola lettura. Nessun nome di Comune, azienda, professionista o ID reale è
presente nella logica applicativa. L'originale e il suo hash rimangono la base
della stabilità: non è un'identità fra revisioni arbitrarie di documenti diversi.

I campi usano lo stesso contratto testuale già esistente: contesto locale,
marker, destinazione, controlli sulle firme e citazioni FORM. Istruzioni e
delimitatori Word non vengono inseriti nel testo visibile delle citazioni.
Non cambiano lo schema globale o il formato FORM B0. La prova di integrazione
verifica che una proposta sintetica passi il normale controllo della
destinazione FORM e del dato SOURCE; un valore non citato continua a fallire.
Una proposta grounded resta soggetta alla revisione, non è scritta automaticamente.

Il writer sostituisce esclusivamente il risultato tra separatore e fine campo.
Con risultati senza alcun nodo di testo, inserisce il testo prima della fine
campo. Non converte i controlli in testo ordinario e non riscrive le loro
proprietà. I risultati vuoti adiacenti richiedono una precedenza di sostituzione:
a pari offset, la regione non vuota viene scritta prima di quella vuota.
Il test negativo ha riprodotto il difetto prima di correggere questa precedenza.

Sono conservati i vincoli su firme, email complete e recapiti divisi in parti,
limiti di caratteri e contenuto. Un maxLength esplicito del campo viene rispettato:
nessun troncamento. Tipi calcolati/numerici/data, formati speciali, risultati
già compilati e strutture non dimostrate restano esclusi da questa estensione.
**Non è supporto universale a tutti i controlli Word.**

## 3. Le venti destinazioni di Cesano

Gli indici sono a base zero, come gli ID esistenti.

| ID | Richiesta nel modello |
|---|---|
| p12.ft0 | Sottoscritto |
| p12.ft1 | Luogo di nascita |
| p12.ft2 | Data di nascita |
| p12.ft3 | Comune dello studio |
| p12.ft4 | Via dello studio |
| p12.ft5 | Numero civico |
| p12.ft6 | Partita IVA |
| p12.ft7 | Posizione INAIL |
| p12.ft8 | Matricola INPS |
| p12.ft9 | Posizione INARCASSA |
| p12.ft10 | Indirizzo mail |
| p12.ft11 | PEC |
| p12.ft12 | Telefono |
| p12.ft13 | Ordine professionale |
| p12.ft14 | Numero di iscrizione |
| p18.ft0 | Associazione temporanea |
| p19.ft0 | Società di ingegneria |
| p20.ft0 | Società professionale |
| p21.ft0 | Altra forma |
| p105.ft0 | Data finale |

Riconoscere questi campi non dimostra i rispettivi dati personali, iscrizioni,
recapiti o condizioni di ramo. Le proprietà aziendali non vengono trasferite
automaticamente allo studio personale. Nessuna delle 68 checkbox è stata
selezionata nei DOCX tecnici; la data resta vuota nella prova dei quattro SOURCE.

## 4. Regressione offline sui documenti precedenti

I riferimenti sono le nuove globali del benchmark ufficiale storico e quelle
del benchmark casuale, non il vecchio replay Minervino da 61 scritture.

| Documento | Candidati prima/dopo | Testi nell'export precedente | Checkbox scritte | Audit e DOCX precedenti |
|---|---:|---:|---:|---|
| Minervino | 267/267 | 54 | 1 | identici |
| Trapani | 115/115 | 10 | 0 | identici |
| Catanzaro | 307/307 | 13 | 0 | identici |
| Bella | 67/67 | 4 | 0 | identici |
| CRAA | 51/51 | 9 | 0 | identici |
| Cesano | 68/88 | 0 | 0 | DOCX identico; audit con 20 posizioni irrisolte in più |

Per i cinque già supportati, i cataloghi completi sono identici, gli audit
ricalcolati sono identici e ogni valore esportato supera nuovamente i controlli
locali. I DOCX sono identici byte per byte: nessuna perdita, nuova spunta o
scrittura. Cesano conserva identici tutti i 68 candidati precedenti e le loro
valutazioni; le nuove posizioni non ricevono valori dalla vecchia risposta.

L'identità conserva anche **l'errore PEC di Trapani** e i **due valori CCIAA
invisibili di CRAA**. Non sono risolti o riclassificati come corretti da questa
regressione. Non occorre una nuova conversione dei cinque DOCX identici per
attribuire loro un'impaginazione nuova: i PDF precedenti rimangono riferimenti
storici, mentre soltanto i due DOCX tecnici Cesano sono stati renderizzati ora.

## 5. Verifiche e conservazione

[Test nuovi](../backend/tests/test_docx_formtext.py): nomi duplicati, posizione
stabile, scritture parziali e ripetute dall'originale, stili, proprietà Word,
parti del pacchetto, campi in tabella e checkbox indipendenti. Negativi per
istruzione/metadati mancanti, delimitatori incompleti o duplicati, annidamenti,
campi su più paragrafi, disabilitazione/blocco, formato/tipo speciale,
precompilazione, oggetti, contenitori complessi, celle unite, firme,
email incomplete, email divise e maxLength. Prova FORM/SOURCE con valore non
documentato respinto. Test aggiuntivi sui risultati vuoti adiacenti.

I conteggi finali e gli esiti effettivi delle suite sono registrati in
[misure](benchmarks/2026-10-19-legacy-formtext.json) e
[controlli](benchmarks/2026-10-19-legacy-formtext-checks.json), insieme agli hash.
I tentativi RED, gli errori dei primi assert di test e la suite precedente
all'ultima correzione sono conservati separatamente; non sono risultati finali.

Versione finale: **27 nuovi casi parametrizzati**, **230 test mirati passati
in 15,00 s**, **2.654 test backend passati in 197,46 s** e Ruff su tutto il
backend passato. Sono test software con dati controllati/provider simulati,
non misure della qualità di nuove risposte LLM. Il controllo di conservazione
verifica 317 altri file protetti invariati, 546 artefatti precedenti, 29 sessioni
originali e 285 file storage invariati. Nessuna nuova sessione aggiunta.

Le verifiche fisiche rimuovono il solo banner previsto, confrontano il corpo
XML escludendo esclusivamente i testi di risultato, controllano ciascuna
destinazione e verificano CRC/XML e identità delle altre parti del pacchetto.
Questo dimostra la conservazione di prestampato, stili, bookmark, proprietà e
stati dei controlli nei documenti esercitati. Nessuna nuova attestazione, firma
o scelta procedurale è prodotta dalla pipeline.

Grezzi:
`backend/data/compilation-audit/legacy-formtext-20261019-01/`.
Il backup dedicato in `docs/benchmarks/` conserva codice prima/dopo, test,
originali, cataloghi, audit, verifiche e DOCX/PDF tecnici; non contiene database
o credenziali. Sessioni e artefatti originali sono controllati senza modificarli.
[Descrittore e hash](benchmarks/2026-10-19-legacy-formtext-archive.json),
[verifica dell'archivio estratto](benchmarks/2026-10-19-legacy-formtext-backup-checks.json).

[Word tecnico con quattro dati SOURCE](<../nuovi dati/Cesano.FORMTEXT-PROVA-TECNICA-20261019.docx>),
[PDF](<../nuovi dati/Cesano.FORMTEXT-PROVA-TECNICA-20261019.pdf>).
È un artefatto di verifica del writer e non una nuova bozza prodotta dalla chat.
I rami e i dati mancanti conservano i controlli esistenti. Le sessioni già
concluse non sono migrate: le venti nuove destinazioni saranno disponibili
quando una nuova sessione ricostruirà il catalogo.

L'obiettivo strutturale è raggiunto per tutti i 20 FORMTEXT osservati. Il passo
successivo da decidere è una nuova compilazione controllata di Cesano, per
misurare proposte, verifiche e scritture reali sulle destinazioni ora disponibili,
senza attribuire al solo parser un miglioramento della qualità LLM già misurato.
