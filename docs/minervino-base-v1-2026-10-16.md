# Minervino V1: base congelata prima della nuova architettura

**16 ottobre 2026.** L'utente ha autorizzato a risolvere i rilievi, adottare
il caso come base, creare un tag e pubblicare su GitHub. Questa richiesta
supera la precedente attesa dell'OK sul candidato; non autorizza implicitamente
l'implementazione del nuovo motore o la validazione dell'intera architettura.

## Risultato

- [Word finale](<../nuovi dati/domanda-iscrizione.GOLD-V1.docx>) nella stessa
  cartella del candidato, con [PDF di riferimento](<../nuovi dati/domanda-iscrizione.GOLD-V1.pdf>).
- [Fixture Minervino V1](../demo-documents/benchmark-minervino/v1/README.md),
  separata dalla fixture Labirinto V1, con modulo, cinque fonti, richiesta
  iniziale, scenario, risposte USER, inventario, gold JSON/Word e manifest.
- [Protocollo](../demo-documents/benchmark-minervino/v1/PROTOCOLLO.md) con
  checkpoint, denominatori, variabilità, errori critici e archivio delle prove.
- [Proposta architetturale](../ARCHITETUTTURA_PROPOSTA.md) collegata a questa
  base e ai problemi osservati, senza modifiche al codice applicativo.

Word gold SHA-256:
`94e77ce5d04585c4d62d858bec1ec2d6c0af2e4aa5c062e7af6cb32a474c4db3`.
[Manifest della fixture](../demo-documents/benchmark-minervino/v1/manifest.json)
SHA-256:
`89534c5171a90328b994d4425e9e11b082c6e5968c3a5b275b710438cf3e0139`.
Tag di riferimento: **baseline-minervino-v1-20261016**, ramo **prune-backend**.
Il tag congela la base del confronto, non dichiara qualità LLM già misurata.

## Correzioni e fedeltà

Il definitivo riparte dal pacchetto dell'originale, applicando i valori e le
scelte già revisionati del gold dell'utente. Nessun output del compilatore
è stato usato per decidere le aspettative. Candidato e revisione 1 conservati.

Le due frasi esplicative sono fuori dalle righe compilabili; nelle righe
inutilizzate sono ripristinati i placeholder originali. Le designazioni sono
fissate nello scenario e disponibili soltanto dopo la risposta USER pertinente.
Le lettere a), b), c), d) erano già definite correttamente: ora anche il PDF
LibreOffice ne conferma la visualizzazione. Nessuna numerazione manuale aggiunta.

Luogo/data e paragrafi della firma hanno keepNext/keepLines espliciti. La firma
resta vuota. Restano 130 paragrafi corpo, 246 totali e quattro tabelle con
18/2/4/11 righe. I 13 controlli nativi conservano gli identificatori originali.
Nel pacchetto cambia soltanto word/document.xml: tutte le altre 15 parti sono
identiche byte per byte all'originale. Sono intenzionali il banner sintetico
iniziale e le proprietà del blocco firma.

## Materiali e aspettative

Le tre fonti Company e il distrattore General coincidono con gli originali
attualmente nel backend, verificati in sola lettura; la quinta fonte è l'avviso
archiviato della procedura. DB/KB live non modificati. L'integrazione resta un
evento successivo per le cariche: al 15 ottobre Leonardo rappresenta la società,
Luca è cessato dall'amministrazione; il ruolo del firmatario della pratica è
comunque una scelta USER distinta.

| Destinazioni autoriali | Totale | Attesa finale |
|---|---:|---|
| Testi documentali | 60 | Valore corretto, stessa persona/ruolo, prova e posizione |
| Testi USER | 4 | Due righe esecutori, integratore e luogo/data dopo la risposta |
| Testi vuoti | 123 | 120 rami esclusi, due continuazioni, una firma manuale |
| Celle di preferenza | 67 | Sei X, altre 61 vuote; massimo sei nel gruppo |
| Checkbox native | 13 | Tre selezionate, dieci non selezionate |
| Totale | 267 | Valutare le categorie separatamente |

L'inventario combina lettura del modulo e localizzazione XML dei placeholder;
non si limita alle destinazioni rilevate dal parser applicativo. Il gold
strutturato conserva etichetta, soggetto/ramo, contesto originale, span,
provenienza, quote documentali, condizioni e attese nei checkpoint.

T0 contiene soltanto fonti e richiesta iniziale: Mapi società di ingegneria,
firmatario Leonardo e data di riferimento. Preferenze, designazioni,
attestazioni e luogo/data sono quattro argomenti di risposta successivi,
in ordine libero. Il valutatore non suggerisce argomenti saltati; T2 autorizza
esplicitamente l'export anche parziale. Gli identificativi restano dimostrativi,
con checksum esclusi dallo score e anomalie da segnalare separatamente.
Firma, allegati e abilitazioni specialistiche non vengono prodotti o certificati.

## Verifiche effettive e tentativi conservati

Passati i controlli indipendenti su 267 destinazioni, 64 testi scritti, 123
vuoti, sei X, 13 stati/simboli nativi, quote nelle fonti, separazione input/gold,
ZIP/XML e apertura python-docx. Verificata l'identità strutturale dell'intero
OOXML dopo aver annullato soltanto le modifiche dichiarate. Controllati gli
18 hash del manifest; il manifest stesso è registrato separatamente.

MuPDF 1.27.0 ha reimpaginato il gold in 16 pagine con la linea firma isolata,
anche con keepNext: esito conservato, non usato come riferimento di layout.
Preparato LibreOffice 26.2.6.3 localmente sotto .tools, con pacchetti estratti
senza installazione di sistema. Dopo errori iniziali di bootstrap ricollocato,
conversioni riuscite: originale dieci pagine, gold nove. Ispezionate tutte
le nove pagine PNG del gold: lettere corrette, dati e scelte leggibili,
firma e linea insieme nell'ultima pagina. PDF e immagini sono conservati.

I primi avvii LibreOffice hanno prodotto DeploymentException/RuntimeException;
il primo controllo con Python di sistema non trovava python-docx, poi riuscito
con l'ambiente backend. Log e cause conservati nell'audit. La conversione
LibreOffice segnala warning liblangtag per il percorso dati del tool estratto:
PDF prodotto con return code zero e revisionato, senza certificare equivalenza
di font o paginazione con Microsoft Word, che non è disponibile.

Nessuna suite applicativa completa necessaria: codice motore/frontend invariato.
Nessuna nuova chiamata provider, sessione o baseline integrata; nessuna percentuale
di accuratezza dichiarata. La validazione degli artefatti non misura la qualità
di un modello. La vecchia fixture Labirinto e i suoi hash rimangono invariati.

## Archivio e ripresa

[Riepilogo misurato](benchmarks/2026-10-16-minervino-freeze.json),
[bundle](benchmarks/2026-10-16-minervino-freeze-audit.tar.gz),
[checksum](benchmarks/2026-10-16-minervino-freeze-audit.tar.gz.sha256).
Raw: backend/data/compilation-audit/minervino-freeze-20261016T144815Z/.
Bundle: 75 file, 3.468.040 byte, SHA-256
`8af726b5b36fac4bcf0bb3bc24d6c0dfa51624a2e0f5eba96324c2bbe5999a27`.
Include copie dei materiali congelati, preparazione/verifica, log, rendering e
manifest; esclude profilo/cache LibreOffice e binari locali. I pacchetti scaricati
sono descritti con versione e hash, non pubblicati nel repository.

Il prossimo passo è predisporre l'istanza isolata, fissare provider/configurazione
e acquisire la baseline integrata su tre run, prima dei cambiamenti architetturali.
Il runner Labirinto attuale non legge automaticamente questo schema né misura
tutto il percorso fino al Word: un eventuale adattatore va progettato esplicitamente.
Qualsiasi cambiamento ai materiali congelati richiede errata e nuova versione.
