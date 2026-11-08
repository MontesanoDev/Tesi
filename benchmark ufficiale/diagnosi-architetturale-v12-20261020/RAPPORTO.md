# Mapi V12 — diagnosi architetturale controllata B0 / E1 / E2-A

20 ottobre 2026. Studio completato: quattro documenti, tre repliche indipendenti
per configurazione, 57 analisi nuove e 42 revisioni del narratore reale.
**Nessuna variante integrata. Nessuna correzione applicativa durante lo studio.**

**Verdetto:** la sola lunghezza del JSON FORM non è dimostrata come causa delle
omissioni. E1 riduce l'input, ma peggiora la copertura validata complessiva e non
riduce il costo. E2-A mostra un beneficio locale su Catanzaro, senza un vantaggio
complessivo robusto. Sono dimostrati ostacoli del backend e un errore di sicurezza
nell'applicabilità: due bozze contengono una scrittura in un ramo non applicabile.
La V12 resta un controllo sperimentale congelato; non viene dichiarata adottata
come baseline di affidabilità del prodotto.

## 1. Protocollo, baseline e limiti del confronto

[Protocollo preregistrato](PROTOCOLLO.json), [snapshot/hash](FROZEN.json),
[configurazione](input/model.json), [SOURCE](input/SOURCE.json),
[originali SOURCE](input/SOURCE-originals/manifest.json), [riferimento](reference/manifest.json).

L'ultima correzione MODEL225/200 era conclusa. La suite è stata rieseguita:
**2.905 PASS in 225,54 s**. La regressione ricostruisce **23 audit e DOCX identici**
nei sei documenti storici, inclusi Minervino 61 e i casi Cesano/CRAA.
29 controlli sperimentali PASS e tre test diagnostici PASS: inventario, topologia,
marker, riferimenti, immutabilità, ambiti, merge e equivalenze con negativi.
Questa stabilità software non equivale alla correttezza di ogni nuova risposta AI.

HEAD `99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e`, con working tree già modificato:
i 67 moduli applicativi sono congelati per contenuto. Test, lockfile e codice
prima degli esperimenti sono nello snapshot. La KB scelta è verificata identica
alla KB live:22 chunk, tre documenti company e uno general. Nessun troncamento
SOURCE o filtro diverso tra varianti. Gli originali e i dati live sono conservati.

Modello API `deepseek-flash`; versione pubblicata dal provider
`DeepSeek-V4.1-Flash-1017`; fingerprint restituito in tutte le 99 chiamate:
`e72d3c7f663d3e1383b00b3884cb4501`. Il nome restituito resta un alias: non certifica
pesi immutabili. Globale: thinking **enabled**, effort **low**, temperatura 0,1,
max_tokens49.152, timeout 300 s. Il profilo salvato riporta thinking=false,
ma la globale V12 imposta enabled/low esplicitamente: sono i body acquisiti a
provare la configurazione realmente usata. Narratore: thinking disabled,
max_tokens2048. Nessun cambio di modello, API, grounding o writer.

Il contesto configurato 32768 del profilo non è un limite di taglio applicato a
questo percorso: i prompt reali arrivano a 83.997 token e sono accettati. È provata
la presenza dei dati nei body, non che il modello li abbia letti o usati tutti.
Ordine bilanciato con seed 20261020, due richieste concorrenti; nessun seed di
campionamento aggiunto al modello. Ogni replica è una nuova richiesta senza
storia delle altre repliche, con risposta e ID del provider propri. Nessun retry,
rimpiazzo di repliche, riparazione o selezione dell'output migliore.

### Checkpoint USER e significato dei DOCX

Per ciascuna procedura è stato scritto uno scenario sintetico distinto, prima
delle chiamate. La richiesta iniziale sceglie Leonardo Montemurro e la
partecipazione singola come società di ingegneria. La forma S.r.l. è un fatto
SOURCE; società di ingegneria è la tipologia dell'operatore, distinta dalla
modalità di partecipazione. L'etichetta larga natura_giuridica nei metadati dello
scenario non viene usata come inferenza: al modello entra soltanto il messaggio
USER letterale. La scelta nominativa non prova anagrafica o poteri; questi
richiedono SOURCE e controlli propri. Non sono confermati procure, nuovi poteri,
preferenze, attestazioni, esecutori, integrazione o luogo/data.

Il confronto si ferma **dopo l'analisi e la revisione reale del narratore, prima
di ulteriori risposte USER**. Nessuna ricevuta accettata viene costruita per
sbloccare condizioni. Le varianti usano quindi lo stesso checkpoint, ma possono
proporre condizioni diverse. I DOCX misurano questa esportabilità iniziale;
**non rappresentano una nuova prova UI con dialogo completato**, né un confronto
letterale con le 61 scritture ottenute dopo risposte USER nella vecchia sessione.
Lo stato è isolato in JSON; nessuna CompilationSession live viene alterata.
Sono usate le funzioni V12 di revisione, riuso, selezione e validazione, quindi
il writer originale. La revisione del narratore è reale, non un'approvazione
simulata. L'harness non misura persistenza, router chat o guard delle risposte
USER successive. Questo limite impedisce conclusioni sulla qualità finale dopo
un intero dialogo, ed è dichiarato per evitare un confronto improprio.

## 2. Inventario e classificazione antecedenti alle nuove risposte

60 occorrenze SOURCE Minervino,17 Trapani,31 Catanzaro,8 Bella: **116 per pannello**.
Sono richieste in posizioni fisiche, non 116 fatti unici o tutti i requisiti legali.
Tutte le 756 destinazioni sono censite; rami inattivi, firme, dati assenti e decisioni
USER sono separati dal denominatore. Le tabelle a cardinalità variabile non
rendono obbligatoria ogni riga vuota. CRAA non è aggiunto: gli altri quattro
isolano già i problemi in esame. I casi fissi e i riferimenti restano indipendenti
dai prompt. Minervino ha GOLD; gli altri hanno inventari autoriali SOURCE/FORM,
non un GOLD indipendente. La valutazione non è una certificazione giuridica.

Le prove SOURCE mantengono soggetto, documento, chunk e citazioni. Identità,
ruolo, proprietà e applicabilità restano dimensioni distinte. Un recapito aziendale
non è personale; un ruolo aziendale non designa un esecutore. Un dato SOURCE non
autorizza una dichiarazione. La SOURCE è sintetica e temporalmente fissata:
non si certifica l'ammissibilità dell'azienda nelle gare storiche.

Il criterio non è la sola stringa GOLD. Sono accettati case/spazi/Unicode, titoli
professionali documentati, date equivalenti e paese facoltativo nell'indirizzo.
È controllato anche il soggetto e il tipo di entità. Valori corretti con prove
invalide restano distinti da proposte realmente validate. Due stringhe composte
con numero, connettivo del e data completa sono state annotate semanticamente
come complete, senza cambiare il riferimento o gli output: **il grounding le
respinge ancora**, perché non esistono come span SOURCE unico. I punteggi
automatici e le due annotazioni sono entrambi conservati in
[adjudication](SEMANTIC-ADJUDICATION.json). Un numero senza la data richiesta è
parziale, non un fatto inventato; una sede completa nel Comune ha granularità
errata. In Cellulare+Telefono è valutato il telefono documentato, senza inventare
il cellulare assente. La valutazione è autoriale e non cieca.

## 3. Dove si perdono i dati: diagnosi del backend e dell'analisi

[Tracce per tutte le posizioni](TRACE-REFERENCE.json), [cause](CAUSES.json),
[barriere strutturali](STRUCTURAL-BARRIERS.json), [stadi](PIPELINE-COUNTS.json).

### 3.1 Destinazione riconosciuta, prova FORM impossibile

**13 delle 31 posizioni SOURCE di Catanzaro** esistono nel parser e nel writer,
ma tutti i paragrafi ammessi come prova FORM locale sono vuoti. Le etichette
esistono nella riga precedente o nella prima riga della medesima tabella,
che non è marcata come intestazione Word ripetuta. Il validatore ammette riga
locale e header formali; non ricostruisce questi collegamenti.

Esempio `t25.r2.c0`: SOURCE-52 prova Bari come CCIAA; FORM p439 contiene
l'etichetta esatta, ma il campo è nella riga successiva, p440 vuoto. La proposta
veritiera costruita offline conserva il fatto GROUNDED e fallisce soltanto per
FORM esterno al contesto locale. Per le tabelle dei soggetti alcune citazioni
di ruolo del modello sono inoltre sbagliate: non vanno confuse con la barriera
di intestazione. Nessuna fonte di persona diversa viene unita.

Questo è un ostacolo **precedente alla qualità della generazione**: al massimo 18
occorrenze del riferimento Catanzaro possono superare il gate FORM tramite una
proposta del modello, nella rappresentazione congelata. E1 ed E2-A conservano
esattamente gli stessi limiti. Non manca il dato nel prompt e non manca il campo
nel catalogo: manca una relazione utilizzabile dal verificatore. I 13 casi ricorrono
117 volte nei nove confronti Catanzaro. Non sono117 problemi indipendenti.

Le checkbox Catanzaro sono invece collegate alle etichette nella cella adiacente:
non si attribuisce loro erroneamente la stessa mancanza. Otto proposte checkbox
E2-A hanno un gruppo respinto per citazione FORM inesistente; altri gruppi
falliscono completezza o intreccio. I rifiuti preservano correttamente le caselle.

### 3.2 Altri ostacoli dimostrati, senza correggerli

- Sei occorrenze di chiarimento su 18/05/2015 contro 18 maggio 2015: stessa persona,
  proprietà e iscrizione documentate, ma confronto delle alternative come stringhe.
  Due occorrenze analoghe Bari contro Bari(BA), con coppia nome/codice esplicita
  nella SOURCE. Sono differenze di rappresentazione, non nuove decisioni USER.
- Quattro proposte di Comune vengono eliminate dalla continuità con l'operatore
  perché l'operatore è conditional. Identità e dati della stessa società sono
  grounded, ma il controllo richiede stato GROUNDED, fact_id e condizioni TRUE,
  invece dei metadati della proposta grounded. Confusione tra prova di proprietà
  e autorizzazione all'uso. Un quinto caso ha proprietario non dimostrato e resta
  un rifiuto necessario. Nessun UNKNOWN è stato cambiato.
- Per dati composti la stringa pulita data+luogo, o numero+data, spesso non
  compare letteralmente in una singola SOURCE. Il rifiuto è conforme al contratto
  attuale; l'informazione può essere documentata in componenti separati. È un
  limite espressivo distinto dalla lunghezza del FORM, non un permesso di
  concatenare valori arbitrariamente.

### 3.3 Errori del modello e controlli che funzionano

Nelle repliche 2 e 3 E1 Minervino il modello propone tutti i 60 valori di riferimento,
ma inventa `p52.s2` e `p52.s3`, che non esistono. Li ripete anche nello scope
condiviso `c_soc_ing`. Il controllo respinge la condizione e blocca **41 campi reali
per replica**,82 esposizioni complessive. Sono rifiuti necessari: cancellare due
ID per salvare il punteggio avrebbe modificato arbitrariamente il risultato.

Altri errori: binding con ruolo non presente nel testo FORM citato, paragrafo
errato, ruolo/formato SOURCE non attestato dalla citazione fornita, sole parentesi
e marker senza contesto, value dove il contratto richiede conditional. Cinque
proposte di indirizzo completo nel Comune vengono correttamente respinte.
Tre proposte di via omettono il civico del riferimento. Le 15assegnazioni al ramo
di direzione/vigilanza non dimostrato sono respinte: la carica amministrativa
non viene trasferita automaticamente a un diverso ruolo.

Su 1.044 occasioni valutate, le cause esclusive del primo ostacolo sono:

| Prima causa osservata | Occorrenze |
|---|---|
| Valore/soggetto corretti e proposta grounded | 534 |
| Prova FORM locale impossibile nel backend | 117 |
| Omissione con input disponibile, fuori dalla barriera precedente | 113 |
| Binding del modello con citazione insufficiente | 104 |
| Condizione del modello assente/invalida nel contratto | 102 |
| Prova del ruolo/record insufficiente | 24 |
| Valore incompleto o granularità errata | 10 |
| Valore composto completo ma non letterale nella SOURCE | 9 |
| Citazione/fatto non letterale | 7 |
| Altra prova FORM insufficiente | 6 |
| Date equivalenti trattate come alternative | 6 |
| Value con condizione UNKNOWN | 5 |
| Proprietario grounded ma conditional: proposta persa | 4 |
| Provincia equivalente trattata come alternativa | 2 |
| Proprietario non dimostrato: rifiuto necessario | 1 |

Questa tabella distingue il punto della perdita, non assegna una percentuale
causale di responsabilità psicologica al modello. Un valore semanticamente
corretto può violare il protocollo di prova; un'omissione può essere indotta da
quel contratto. Le 178 omissioni grezze comprendono 65 occasioni nelle 13 destinazioni
strutturalmente bloccate e 113 fuori da esse. Non sono178 dimostrazioni che il JSON
sia troppo lungo. Nessuna delle 116 posizioni manca dall'input SOURCE autorizzato.

### 3.4 Storici, riuso e revisione

Gli artefatti storici non sostituiscono le nuove generazioni. La ricostruzione
[storica più recente](HISTORICAL-LATEST-SUMMARY.json) conserva Minervino 60 testi e
checkbox, Trapani 17 testi e Bella 4. Nel Catanzaro storico 15 scritture includono una
carica USER documentata anche nelle SOURCE e un numero di registro privo della
data:14 occorrenze complete secondo lettura semantica, una parziale. I quattro
dati Bella recuperabili dal codice attuale non ricevono retroattivamente le
revisioni mancanti della vecchia sessione. Il replay non inventa nuove approvazioni.

Nelle nuove prove il riuso SOURCE aumenta i valori corretti grounded di64 per
configurazione,192 nel totale. **Omissione della globale e vuoto del DOCX sono
misure diverse.** La scelta del firmatario identifica la persona; i valori
recuperati sono provati dalle SOURCE, non dal nome fornito dall'utente.

## 4. Confronto B0 / E1 / E2-A

E1 riusa la proiezione sperimentale a indice diretto `compact-index-v2`, senza
integrarla: elimina location/range/slot_context duplicati e condivide ancore e
sezioni. I blocks, testi, marker, tabelle, controlli e metadati logici sono uguali
per ricostruzione automatica. Questo non rende complete relazioni che mancavano
già nel catalogo. Le istruzioni aggiuntive sono acquisite integralmente in
`requests/DOCUMENTO/VARIANTE/SEZIONE/system-difference.txt`: cambiano soltanto la
lettura della vista. SOURCE, USER e schema di risposta sono identici.

E2-A usa lo stesso E1 con inventario circoscritto:3 sezioni Minervino,2 Trapani,
4 Catanzaro,2 Bella. Non divide tabelle o unità di continuazione. Tutto il testo
esterno resta nei blocks: è un test del focus, **non di un contesto più corto**.
I gruppi sono definiti manualmente dalle macrosezioni FORM, senza GOLD. Il beneficio
non può essere attribuito soltanto al focus: aumenta anche il budget aggregato
di chiamate e reasoning. Non è provato un sezionatore automatico generico.

Nella tabella ogni cella contiene le tre repliche, non l'output migliore.
G è la proposta con valore/soggetto corretti che supera il grounding; GR include
il riuso SOURCE verificato. W sono scritture conformi nel checkpoint comune.
Le due scritture indebite fuori dal riferimento sono riportate separatamente.

| Documento | Variante | Rif. | Valori corretti proposti | G | GR | W |
|---|---|---|---|---|---|---|
| Minervino | B0 | 60 | 50 / 49 / 59 | 47 / 44 / 42 | 56 / 53 / 50 | 18 / 0 / 16 |
| Minervino | E1 | 60 | 60 / 60 / 60 | 43 / 9 / 10 | 52 / 17 / 19 | 0 / 17 / 18 |
| Minervino | E2-A | 60 | 57 / 60 / 58 | 47 / 43 / 44 | 56 / 52 / 52 | 17 / 0 / 0 |
| Trapani | B0 | 17 | 9 / 9 / 17 | 9 / 9 / 9 | 17 / 17 / 17 | 0 / 0 / 0 |
| Trapani | E1 | 17 | 9 / 9 / 9 | 9 / 9 / 9 | 17 / 17 / 17 | 8 / 8 / 8 |
| Trapani | E2-A | 17 | 8 / 16 / 8 | 8 / 8 / 8 | 16 / 16 / 16 | 0 / 0 / 8 |
| Catanzaro | B0 | 31 | 14 / 29 / 22 | 9 / 13 / 8 | 11 / 14 / 9 | 7 / 7 / 6 |
| Catanzaro | E1 | 31 | 14 / 15 / 30 | 12 / 13 / 13 | 14 / 15 / 15 | 7 / 8 / 8 |
| Catanzaro | E2-A | 31 | 19 / 20 / 30 | 13 / 13 / 13 | 15 / 14 / 15 | 6 / 0 / 8 |
| Bella | B0 | 8 | 8 / 8 / 8 | 0 / 4 / 4 | 3 / 7 / 8 | 0 / 0 / 0 |
| Bella | E1 | 8 | 4 / 4 / 4 | 4 / 4 / 0 | 8 / 8 / 0 | 3 / 3 / 0 |
| Bella | E2-A | 8 | 8 / 4 / 8 | 0 / 4 / 0 | 2 / 8 / 3 | 2 / 8 / 3 |

La copertura grezza migliora ripetutamente soltanto nel Minervino E1:60/60 contro
50,49,59. Ma G crolla a 43,9,10, soprattutto per errori nel contratto di condizioni.
Bella mostra l'opposto: B0 propone 8/8 in tutte le repliche, E1 soltanto 4/8.
Quindi una rappresentazione logicamente equivalente cambia il comportamento,
senza un miglioramento generale della compilazione.

Totali sui medesimi348 obiettivi per configurazione:

| Variante | Obiettivi | Valori corretti | G | GR | Applicabili nei controlli | Grounded ancora UNKNOWN | W conformi |
|---|---|---|---|---|---|---|---|
| B0 | 348 | 282 | 198 | 262 | 62 | 200 | 54 |
| E1 | 348 | 278 | 135 | 199 | 89 | 110 | 88 |
| E2-A | 348 | 296 | 201 | 265 | 52 | 213 | 52 |

Gli 89 applicabili E1 e le 88 scritture non dimostrano che E1 sia migliore: vengono
proposte condizioni e scope diversi. Molti altri valori E1 sono irreversibilmente
respinti prima che una risposta USER possa sbloccarli. La condizione UNKNOWN
non è un dato SOURCE mancante né un errore da rimuovere. La differenza tra
applicabili e scritti è dovuta a 8 valori non revisionati nel fallimento del
narratore B0 e a un hold E1. Altri hold si sovrappongono a condizioni già UNKNOWN.

### Recuperi E2-A sugli stessi campi

[Confronto campo per campo](MATCHED-E2-RECOVERIES.json). E2-A recupera 39 posizioni
omesse dalla corrispondente replica B0 e perde 28 valori corretti che B0 aveva
proposto. Non è un confronto sezione/intero documento: tutti i gruppi sono
ricomposti e le 116 destinazioni sono le stesse.

Non esiste una posizione omessa in tutte e tre le B0 e recuperata in tutte e tre
le E2-A. L'unica omissione B0 stabile è il CF del direttore tecnico nella tabella
Catanzaro, `t44.r1.c3`, non recuperato stabilmente da E2-A e già colpito dalla
barriera FORM. Catanzaro mostra comunque un segnale locale: G E2-A è13 in tutte
le repliche, contro 9,13,8 B0. Nel pannello totale G passa soltanto 198→201 su 348.
Non basta per sostenere un vantaggio complessivo robusto o statisticamente
significativo con tre campioni per documento.

Il merge introduce solo namespace per ID interni di fatti/binding/condizioni;
i candidate fisici restano invariati. Tutti i 12merge riescono, senza collisioni
o perdite di grounding rispetto alle singole sezioni. Duplicazioni e link di
scope aggiunti sono esposti in [interazioni](MERGE-INTERACTIONS.json).
Questo non prova assenza universale di contraddizioni semantiche: Source e
condizioni restano controllati dal medesimo backend. Nessuna selezione fra
risposte alternative o correzione manuale entra nel merge.

## 5. Token, reasoning, latenza e costi

Il tokenizer ufficiale V4 scaricato e congelato misura separatamente i componenti.
I token di richiesta effettivi provengono dal provider; nel pannello differiscono
dalla somma dei contenuti testuali offline di52 token di framing. Non si usa una
stima basata sui caratteri per i totali fatturabili.

| Documento | FORM B0 | FORM E1 | Riduzione FORM | Richiesta B0 | Richiesta E1 | Riduzione richiesta |
|---|---|---|---|---|---|---|
| Minervino | 34.665 | 24.255 | 30,0% | 61.741 | 51.647 | 16,3% |
| Trapani | 16.426 | 11.953 | 27,2% | 41.884 | 37.727 | 9,9% |
| Catanzaro | 53.479 | 47.311 | 11,5% | 83.997 | 78.145 | 7,0% |
| Bella | 12.373 | 10.804 | 12,7% | 37.408 | 36.155 | 3,3% |

Totali delle sole analisi, escludendo il narratore;12 pannelli completi per variante:

| Variante | Chiamate | Input | Output non reasoning | Reasoning | Token totali | Costo USD stimato |
|---|---|---|---|---|---|---|
| B0 | 12 | 675.090 | 94.569 | 249.202 | 1.018.861 | 0,237418 |
| E1 | 12 | 611.022 | 99.260 | 277.743 | 988.025 | 0,253900 |
| E2-A | 33 | 1.683.801 | 127.475 | 404.906 | 2.216.182 | 0,373189 |

E1 riduce l'input delle analisi del9,5%, ma aumenta il reasoning dell'11,5% e
l'output non reasoning. Il costo delle analisi cresce da 0,237418 a0,253900 USD,
circa 6,9%; i token totali scendono soltanto del3,0%. Quindi non è dimostrato
neppure un vantaggio di efficienza complessiva: il risparmio dell'input è reale,
il risparmio di costo no. E2-A usa 2,75 volte le chiamate d'analisi e circa 2,49 volte
l'input; il costo delle sole analisi sale a 0,373189 USD, circa 57,2% più di B0.

Medie delle tre repliche, durata in secondi. Somma è il tempo complessivo delle
chiamate; intervallo è la durata osservata del gruppo, con concorrenza 2 e ordine
preregistrato. Quest'ultimo non è una misura della latenza UI di un'architettura
E2 già integrata. Fonte: [metriche](ANALYSIS-COMPARISON.json).

| Documento | Variante | N analisi | Somma s | Intervallo s | USD/replica analisi |
|---|---|---|---|---|---|
| Minervino | B0 | 1 | 136,5 | 136,5 | 0,025638 |
| Minervino | E1 | 1 | 160,0 | 160,0 | 0,029356 |
| Minervino | E2-A | 3 | 211,7 | 176,6 | 0,038700 |
| Trapani | B0 | 1 | 87,1 | 87,1 | 0,014631 |
| Trapani | E1 | 1 | 77,7 | 77,7 | 0,013114 |
| Trapani | E2-A | 2 | 123,8 | 94,8 | 0,020347 |
| Catanzaro | B0 | 1 | 128,0 | 128,0 | 0,023787 |
| Catanzaro | E1 | 1 | 144,2 | 144,2 | 0,026369 |
| Catanzaro | E2-A | 4 | 284,3 | 190,8 | 0,049281 |
| Bella | B0 | 1 | 93,2 | 93,2 | 0,015084 |
| Bella | E1 | 1 | 97,2 | 97,2 | 0,015794 |
| Bella | E2-A | 2 | 100,1 | 93,7 | 0,016068 |

E1 è più veloce soltanto su Trapani in queste medie; Minervino, Catanzaro e Bella
sono più lenti. La lunghezza del JSON di ingresso non è una misura sufficiente
del lavoro di generazione. Il reasoning occupa931.851 dei1.269.342 token di output
complessivi, circa 73,4%. Effort low non ha prodotto ragionamenti brevi in assoluto.
Il budget thinking non viene cambiato per favorire una configurazione.

**Totale studio:99 chiamate,4.743.461 token,0,931729 USD stimati**, tutti off peak.
Sono inclusi 42 narratori e il loro fallimento; nessun costo viene nascosto come
replay. Costo normalizzato senza cache1,282723 USD; il costo stimato usa cache
hit/miss reali e le [tariffe ufficiali DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/)
archiviate prima delle chiamate. Non è la fattura dell'account. Tempi, fingerprint,
usage, output, reasoning e finish_reason restano in ogni acquisizione.

## 6. DOCX, sicurezza e rendering effettivi

36 DOCX e 36 PDF nuovi, più quattro replay storici e quattro PDF degli originali.
Tutti i 40 DOCX compilati/replay superano XML/CRC e confronto fisico: destinazioni,
valori, parti non modificate, prestampato, stili, geometrie delle tabelle e stato
dei controlli. Modificato solo document.xml, con l'avviso di bozza già previsto.
Questo dimostra che il writer esegue la selezione ricevuta, non che la selezione
sia semanticamente giusta.

**196 scritture SOURCE:194 conformi e 2 indebite. Zero valori USER e zero checkbox
scritti nel checkpoint.**14 copie sono senza valori:13 per vincoli/hold e una per
fallimento del narratore. Non vengono presentate come compilazioni riuscite.
Delle22bozze non vuote,20non mostrano scritture indebite e 2 sono da respingere.
La bozza parziale è ammissibile; una scrittura nel ramo falso rimane un errore.

### Due scritture nella sezione sbagliata — bloccanti

Catanzaro B0 replica 3 ed E1 replica 3, `t0.r8.c1`:

- FORM p34/p35: Sede operativa, se diversa dalla sede legale.
- SOURCE-44: sede operativa coincidente con la sede legale.
- Il modello propone value, nessuna condizione, stesso indirizzo della sede.
- Il grounding letterale accetta il dato; non scopre autonomamente il predicato
  FORM omesso. Il narratore non sospende il valore. Il writer lo inserisce nella
  posizione richiesta senza alterazioni.

[Prove complete](UNSAFE-WRITES.json),
[B0 DOCX](runs/catanzaro/B0/rep-3/final/bozza.docx),
[E1 DOCX](runs/catanzaro/E1/rep-3/final/bozza.docx).
L'errore è una condizione FORM persa dall'analisi più un controllo di uso che
non la rileva indipendentemente; non un dato SOURCE falso o un writer difettoso.
E2-A evita questo errore nel campione, non prova di esserne immune.

Otto proposte PEC Trapani restano bloccate dall'autorizzazione USER pertinente:
il controllo precedente funziona. Tre menzioni Registro delle Imprese non
provano da sole la reperibilità aggiornata di tutti i soggetti: restano fuori
dai DOCX. Le checkbox senza gruppo/form/prova validi non vengono selezionate.

### Un fallimento del narratore — importante

Minervino B0 replica 2: HTTP200, finish_reason=length, limite 2048 del narratore,
`GenerationTruncatedError`. La globale era conclusa e gli output sono acquisiti.
La revisione non avviene e viene prodotta una copia senza valori; otto valori
corretti sarebbero altrimenti applicabili ai controlli nel checkpoint.
Non è un timeout o un JSON FORM globale troppo lungo. Nessun retry eseguito.
La validità tecnica del DOCX non trasforma questa prova in un successo operativo.

### PDF e difetti cosmetici

Tutti i valori effettivamente scritti sono osservabili nei PDF tramite testo o
rettangoli di parole circoscritti; nessuna parola fuori pagina rilevata. Dodici
falsi negativi della ricerca di stringhe intere erano dovuti all'interleaving
delle colonne Catanzaro, non a testo invisibile: conservati sia il controllo
grezzo sia le coordinate del riscontro locale. Il numero di regioni distinte
copre le occorrenze duplicate degli indirizzi. Posizioni XML verificate per ogni
valore; per stringhe brevi/duplicate il solo testo PDF non dimostra la posizione.

Sette pagine campione sono state viste, comprese entrambe le scritture indebite:
[verifica visiva](VISUAL-CHECKS.json). Testo SOURCE leggibile; restano aLecce in Trapani,
1982 in qualità in Bella, etichette contigue e variazioni di pagina Minervino.
La firma rimane vuota e con etichetta, senza firma inventata. Sono difetti
cosmetici o di impaginazione conservati, non corretti. Non è stata effettuata
lettura umana esaustiva di ogni pagina, né rendering Microsoft Word desktop.
Nessun intervento sul difetto CCIAA CRAA, escluso da questo nuovo pannello.

## 7. Decisioni USER e UNKNOWN

[Inventario dei 54 predicati UNKNOWN con proposte grounded](UNKNOWN-INVENTORY.json),
[domande finali](FINAL-QUESTIONS.json), [trasmissione](NARRATOR-USER-CONTEXT.json).
Le 523 occasioni grounded ancora UNKNOWN non sono dati assenti dalla KB.
Nel checkpoint nessuna ricevuta accettata è associata a quelle condizioni.
Alcune richiedono poteri o decisioni realmente non dati; altre formalizzano una
scelta già scritta all'avvio ma non collegata a quel predicato; altre mescolano
tipologia, rappresentanza e partecipazione in un solo scope. Non si promuovono
in blocco a TRUE e non si attribuiscono tutte a un errore del backend.

Le 42 richieste del narratore non contengono il messaggio iniziale completo né
la sua clausola di partecipazione come ricevuta;35 contengono la scelta del
firmatario tramite i metadati di riuso SOURCE. Non è perdita di tutto il contesto
USER. Il codice non passa user_context direttamente al narratore, e nessuna
risposta successiva esiste in questo harness. Occorre distinguere dato mancante,
decisione iniziale non collegata e assenso procedurale effettivamente mancante.
Il testo USER originale resta integralmente disponibile nelle acquisizioni.
Preferenze, attestazioni, esecutori, integrazione e luogo/data restano cinque
gruppi distinti senza decisioni inventate. Non si attestano requisiti o poteri.

## 8. Interpretazione, confidenza e raccomandazione

- Caso A: miglioramento E1 della copertura grezza Minervino, replicato; nessun
  vantaggio complessivo dopo grounding. Non attribuibile alla sola lunghezza,
  perché cambiano anche organizzazione e istruzioni della vista.
- Caso B: risparmio dell'input dimostrato, risparmio complessivo di costo e latenza
  non dimostrato. I token di output e reasoning possono compensarlo.
- Caso C: segnale locale Catanzaro in E2-A; non miglioramento robusto del pannello
  o dei DOCX. Più chiamate e token, Source recuperate e perse in entrambe le direzioni.
- Caso D: non è giustificata una riscrittura multiagente o un cambio provider.
  I dati motivano controlli mirati sul contratto e sulle relazioni FORM.

Le tre repliche sono tutte mostrate, comprese la copia vuota e le due scritture
indebite. Non viene dichiarata significatività statistica. Quattro documenti
noti, una KB sintetica, un modello/effort e un solo periodo/fingerprint limitano
la generalizzazione. Le sezioni E2 sono autoriali; il loro costo incorpora
l'intero contesto ripetuto. La valutazione non è cieca né doppia. Le aspettative
non sono adattate alle risposte; le due equivalenze manuali sono pubblicate anche
contro il punteggio automatico. Il checkpoint iniziale non misura il completamento
con risposte USER: per valutare quell'esito servirà un confronto ulteriore
attraverso la chat ordinaria, con ricevute esplicite equivalenti e lo stesso
criterio di arresto. Non si pretende che i conteggi di questa prova sostituiscano
i 61 valori della precedente sessione Minervino dopo dialogo.

### Risposte esplicite alle cinque domande

| Domanda | Risposta | Prova e confidenza |
|---|---|---|
| Il JSON lungo è complice delle omissioni? | **NON DIMOSTRATO per la lunghezza in sé.** | E1 accorcia tutti i FORM ma non migliora il pannello; struttura e lunghezza covariano. Alta confidenza che questo studio non dimostri quella causalità; nessuna prova che la lunghezza sia sempre irrilevante. |
| Backend o LLM? | **Entrambi, in passaggi distinti.** |13 relazioni FORM inutilizzabili,12 esposizioni di equivalenza/ownership perse nel backend;113 omissioni fuori dalla barriera;102 errori di condizione e altri rifiuti corretti del modello. Due scritture indebite per predicato omesso non rilevato a valle. Alta confidenza sui casi ricostruiti; media sull'attribuzione causale generale delle omissioni. |
| E1 migliora qualità o solo efficienza? | **Nessun miglioramento complessivo di qualità; migliora l'input, non costo/latenza complessivi.** | G135 contro198, input−9,5%, costo analisi+6,9%; Minervino ha un vantaggio grezzo ma 82 campi bloccati da due scope invalidi. Confidenza media nel pannello, senza generalizzazione ad altre compattazioni. |
| E2-A migliora qualità rispetto alla globale? | **NON DIMOSTRATO complessivamente; beneficio locale Catanzaro.** | G201 contro198, costo analisi+57,2%, nessuna omissione B0 stabile recuperata in tutte le E2. Zero scritture indebite osservate E2, su campione piccolo. Confidenza media sulle misure, bassa per una garanzia generale. |
| Quale architettura conviene? | **Mantenere B0 come controllo, non integrare E1; approfondire E2 soltanto in modo mirato dopo i difetti comuni.** | Il primo rischio è una condizione FORM saltata, non la serializzazione. V12 non dichiarata baseline affidabile end-to-end. Confidenza alta sulla priorità di sicurezza, media sulla scelta futura del formato. |

### Il cambiamento minimo consigliato per la fase successiva

Nessun nuovo framework, agente o writer. Conservare una globale e la separazione
SOURCE/USER. Prima un controllo difensivo indipendente per i predicati FORM locali
che limitano l'uso del valore: il caso sede operativa deve restare vuoto anche
quando il modello omette la condizione. Poi completare relazioni FORM verificabili
per etichette sopra il valore e intestazioni di colonna, mantenendo obbligatoria
l'attribuzione al soggetto/ruolo corretto. Non basta ammettere indiscriminatamente
qualsiasi riga della tabella. Separare nel controllo ownership la prova fattuale
dall'applicabilità UNKNOWN, senza autorizzare nuove scritture.

Date e province possono essere confrontate per rappresentazioni equivalenti
soltanto con identità, proprietà e iscrizione dimostrate: nessun confronto
semantico permissivo, unione per nome o trasferimento di qualifica. Il limite
del narratore 2048 va studiato separatamente rispetto alle 40 revisioni possibili,
senza allargare ora il FORM o cambiare il thinking. Gli errori di scope mostrano
inoltre la fragilità di far ricopiare lunghe liste di ID: eventuali scope più
compatti devono essere backend-owned e sperimentati come contratto separato,
non riparati dopo la generazione.

Dopo quelle verifiche, ripetere il confronto con nuova baseline dichiarata e
una prova su documenti non usati nello sviluppo. Per isolare la rappresentazione
si può aggiungere una compattazione minimale che conservi indice e gerarchia B0,
affiancata a un disegno fattoriale ridondanza/organizzazione. Anche tali controlli
non rendono automaticamente neutro il contenuto eliminato: la causalità della
sola lunghezza richiede prudenza. Per E2, testare prima un solo approfondimento
su ruoli/posizioni omessi e documentati, selezionati senza GOLD, misurando anche
false attribuzioni e costo del contesto esterno. Nessuna delle proposte è stata
implementata nella produzione in questo studio.

## 9. Consegna e riproducibilità

[Indice con tutti i 36 DOCX/PDF](README.md), [metriche totali](METRICS-TOTALS.json),
[CSV prove](trials.csv), [CSV chiamate](calls.csv), [CSV posizioni](reference-trace.csv),
[ricostruzione offline](OFFLINE-REBUILD.json), [preservazione](PRESERVAZIONE.json).
Ogni run contiene richiesta, input, risposta HTTP completa con reasoning,
output JSON, audit, stato delle revisioni, scritture, controlli fisici e PDF.
I fallimenti sono integri. I replay storici non figurano nelle 99 generazioni.

Il codice congelato ricostruisce senza rete/SQLite tutti i 36 DOCX byte per byte e
72 audit raw/effettivi identici, usando le revisioni realmente salvate del
narratore. Non migliora gli esiti originari. Il backup separato include codice,
fonti, manifest e acquisizioni, senza database privati, credenziali o .env;
verifica dal pacchetto estratto. Il solo push non conserva i grezzi esclusi da Git.
Nessun commit/push, migrazione, reindicizzazione, modifica API, prompt di
produzione, schema, modello, validatore o writer. Soltanto documentazione di
continuità aggiornata e materiali sperimentali nuovi. Arresto alla consegna.
