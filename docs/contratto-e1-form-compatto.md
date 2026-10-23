# E1 — contratto del primo FORM compatto

16 ottobre 2026. Proposta approvata esplicitamente dall'utente; implementazione
`compact-v1` nel solo banco di prova. Produzione e criteri di accettazione
invariati. [Misure completate](esperimento-e1-form-compatto-2026-10-16.md):
meno token, qualità non stabilizzata; variante non adottata nella chat. Le sezioni
seguenti conservano anche il ragionamento del contratto originario.

L'obiettivo iniziale è una proiezione deterministica del catalogo già esistente,
con documento completo e stessi identificatori, che riduca ripetizioni nel
payload del modello. Il backend mantiene il catalogo completo per citazioni,
validazione e scrittura dall'originale. Il risultato del modello conserva lo
schema attuale. La [baseline B0](baseline-minervino-b0-2026-10-16.md) è il
riferimento; [E2](piano-esperimenti-e1-e2.md) resta successivo.

## Dove intervenire

Il punto di partenza è la costruzione dell'input in
[compilation_global.py](../backend/app/compilation_global.py), a valle di
`build_global_input`, prima di `global_request`. Il catalogo viene già prodotto
in [compilation_catalog.py](../backend/app/compilation_catalog.py).

Prima applicazione proposta: serializzatore separato e selezione esplicita della
vista nel solo runner di benchmark. La variante B0 rimane ripetibile. L'analisi
E1 passa poi agli stessi validatori sul catalogo canonico, e gli eventuali export
continuano a usare il medesimo originale. Nessuna migrazione delle sessioni.
L'adozione nel flusso applicativo va valutata dopo le misure.

## Cosa pesa nell'input osservato

Lettura offline dell'input reale `analysis-01/input.json` nella directory
`backend/data/compilation-audit/b0-minervino-20261016T154354Z/`. Misura in
caratteri JSON senza indentazione, non in token.

| Parte | Caratteri | Osservazione |
|---|---:|---|
| FORM completo | 126.928 | Circa il 48% dei caratteri dei messaggi completi B0 |
| `form.blocks` | 63.758 | Testi, marker, struttura tabelle e contesto |
| `form.candidates` | 62.947 | 267 record con dati ripetuti e dati per il backend |
| Totale messaggi B0 | 264.951 | Include anche fonti, reading plan, schema e system prompt |

Nel catalogo dei campi, il peso aggregato delle proprietà `location` è circa
12.553 caratteri, `slot_context` 12.451, `anchor_paragraph_ids` 10.489.
`section_ids: []` è presente in tutti i 267 record, circa 4.272 caratteri.
I pesi aggregati includono chiave/valore, senza tutte le parentesi e virgole:
non sono una misura di risparmio ottenuto o da sommare senza precisazioni.

Ci sono inoltre 17.539 caratteri in `reading_plan.source_property_lines`:
rimangono invariati in questo primo confronto. Anche le SOURCE e lo schema
output hanno un costo fisso. La riduzione percentuale del FORM non coincide
con quella dell'intero input o del costo complessivo, che include reasoning/output.

## Trasformazioni proposte

| Elemento | Rappresentazione da provare | Vincolo |
|---|---|---|
| Posizione XML, range e coordinate per il writer | Rimangono nel backend | Ogni ID compatto risolve la stessa destinazione canonica |
| Campi nello stesso paragrafo | Un solo contesto condiviso, elenco degli ID | Conservare tipi, protezioni ed eccezioni per singolo campo |
| Contesto locale before/after | Omettere la copia quando già leggibile nei marker del paragrafo completo | Nessun taglio del testo utile o ricostruzione semantica delle etichette |
| Ancore, sezioni, continuazioni | Relazioni condivise per contesto, con override quando differiscono | Conservare gli stessi riferimenti e ambiti effettivi, senza estenderli |
| Liste vuote e valori predefiniti | Omettere con default documentati | Sezioni e riferimenti non vuoti restano rappresentati |
| Testo e marker | Una copia canonica del testo originale; vista marcata solo dove presente/necessaria | Citazioni letterali e marker attuali restano utilizzabili |
| Tabelle | Griglia, celle, intestazioni e riferimenti condivisi | Ordine, celle unite, intestazioni ripetute e annidamento preservati quando presenti |
| Checkbox native | ID, stato iniziale, testo e contesto collegati | Distinzione dalle celle testuali usate per le X; nessun gruppo semantico inventato |
| Indizi strutturali | Conservare gerarchia esplicita, grassetto osservato, note e parti in sola lettura | Non trasformare un indizio grafico in un requisito o ramo accertato |

La prima versione resta conservativa sulle due viste del testo: alcuni campi
richiedono citazioni con marker, mentre condizioni e ruoli richiedono estratti
del testo originale. Si deduplicano i metadati mantenendo questo supporto.
Una sola stringa con segnaposto riscritti richiederebbe anche ripensare il
protocollo delle citazioni: una modifica ulteriore da dichiarare e misurare.

Esempio indicativo, derivato dal paragrafo reale, senza dati o soluzioni del gold:

```json
{
  "id": "paragraph:12",
  "text": "Il sottoscritto _____________________________, nato a __________________ (__) il __________, residente",
  "text_with_fields": "Il sottoscritto [[p12.s0]], nato a [[p12.s1]] ([[p12.s2]]) il [[p12.s3]], residente",
  "text_fields": ["p12.s0", "p12.s1", "p12.s2", "p12.s3"],
  "context": {
    "anchors": ["paragraph:12"],
    "continuation": "paragraph:11"
  }
}
```

È un estratto dello schema proposto, non l'intero contratto finale. Il contesto
dei quattro campi non viene ripetuto quattro volte. Eccezioni di tipo/protezione
vanno aggiunte dove già presenti nel catalogo canonico. Il riferimento di
continuazione è quello attuale: non afferma un ruolo o una relazione fattuale.
Eventuali citazioni verso altri paragrafi rimangono disponibili nel documento
completo. ID quali `p12.s0`, `paragraph:12`, `t0.r3.c2` conservano identità e
significato; niente rinumerazione per pagina o etichette ricavate dal gold.

## Verifica prima delle chiamate

Il primo risultato da produrre è un confronto leggibile fra input B0 e input
E1 completo, con dimensioni e inventario delle trasformazioni. La proiezione
si costruisce solo dal catalogo, mai dal gold o dalle risposte attese.

Verificare automaticamente la rappresentazione delle 267 destinazioni, con
stessi tipi, stato iniziale dei controlli e protezioni; tutti i riferimenti
risolvibili; ordine, testi originali e viste marcate conservati; contesti,
intestazioni e associazioni di tabella equivalenti alla struttura canonica.
Controllare anche comportamenti fuori da Minervino, inclusi sezioni non vuote,
controlli misti e celle unite, prima di considerare la proiezione generica.

Un insieme di 267 ID uguale non basta: una tabella con gli stessi ID e fasce
scambiate è strutturalmente errata. Queste sono verifiche del serializzatore,
separate dalla qualità delle risposte del provider.

## Prima serie reale proposta

Dopo aver fissato il contratto e verificato la proiezione:

1. Tre analisi E1 del Minervino completo con stesso modello/thinking, fonti,
   chunk, disponibilità USER, schema output, budget e validatori di B0.
2. Conservare il prompt prima/dopo. Cambiare soltanto le istruzioni necessarie
   per leggere la vista; dichiararle come parte del trattamento E1.
3. Valutare tutti i run, inclusi errori: token input/output/reasoning e cache,
   tempo, proposte conformi, perdite nei validatori e risultati per sezione.
4. Proseguire ciascuna analisi nei servizi isolati fino al Word con lo stesso
   copione, per rilevare eventuali regressioni del dialogo e dell'export.

Criteri proposti: riduzione misurata dei token input, integrità strutturale
completa, nessun nuovo errore critico di persona/ruolo/ramo/scelta o firma;
ogni perdita per categoria va riportata. Confrontare la variabilità dei tre
run, senza proclamare equivalenza statistica. Non fissare un risparmio promesso
prima della misura; non usare una singola prova favorevole come criterio.

Un aumento delle proposte corrette bloccate dai validatori indica un beneficio
nella fase LLM e un limite ancora presente a valle. Un Word ugualmente incompleto
non dimostra che la riduzione non abbia risparmiato token, ma impedisce di
attribuirle un miglioramento della compilazione finale.

## Scelte da tenere separate

Il passaggio delle decisioni iniziali (`user_values` oggi vuoto nell'analisi),
il riconoscimento dei ruoli attraverso intestazioni SOURCE, il pool delle
domande e il layout firma sono problemi osservati in B0. Modificarli insieme
alla vista impedirebbe di attribuire i risultati a E1. Restano interventi
successivi da discutere. Anche riduzione/riscrittura dello schema output,
invio dei file ai provider, cambio modello e prove su estratti sono variabili
ulteriori. E1 conserva il documento completo.

## Implementazione approvata e verifica del contratto

Il serializzatore è in
[compilation_form_view.py](../backend/app/compilation_form_view.py), selezionabile
nel runner con `--form-view compact-v1`; default `full`. Il formato effettivo
conserva `form.blocks` esatto e raggruppa i metadati in `form.contexts`, indicizzati
dal `context_id` originale. Ogni gruppo contiene `fields` (ID), `defaults`
(relazioni condivise) e `field_options` (eccezioni e proprietà individuali).
Questa collocazione conserva integralmente i blocchi esistenti e rende diretta
la verifica prima delle chiamate. L'esempio precedente resta illustrativo;
gli input reali completi sono negli artefatti del benchmark.

`validate_form_view` verifica tutti gli ID e i metadati logici, testi/marker,
topologia e riferimenti; coordinate, range e copie before/after rimangono nel
catalogo backend. Le proprietà candidate sconosciute fanno fallire la proiezione
invece di essere eliminate. Nessuna deduzione dal gold.

Preflight: FORM 81.209 caratteri contro 126.928, messaggi 220.519 contro 264.951,
incluso l'adattamento del prompt di 1.287 caratteri. Questi sono conteggi offline,
distinti dalle misure provider. Tutto ciò che non è FORM resta identico a B0;
adattamento del solo prompt di lettura archiviato. Le tre prove sono congelate
prima dei risultati. Default della chat, fonti, schema output e validatori
restano invariati; nessuna migrazione di sessione.

Le verifiche software non certificano la qualità LLM. I test hanno confermato
che il parser attuale non espone slot inline in paragrafi con checkbox native:
la proiezione conserva anche questo limite, senza aggiungere destinazioni.


## Seconda variante misurata, 17 ottobre

Su approvazione dell'utente è stata aggiunta nel runner compact-index-v2:
indice diretto candidate_id, type/context_id espliciti, contesti condivisi.
compact-v1 invariato e riproducibile. Stessi controlli canonici, schema e prove;
istruzioni di lettura proprie del formato. [Risultati](esperimento-e1-index-2026-10-17.md):
input -13,31% B0, due fallimenti su tre e unico Word 21/60. Nessuna adozione,
retry o variazione delle aspettative. Il contratto della prima versione qui
sopra resta il riferimento storico, non viene riscritto dopo gli esiti.
