# Benchmark Minervino V1

Base congelata il **16 ottobre 2026**, autorizzata dall'utente, per confrontare
il sistema attuale e le proposte della nuova architettura. Modulo reale,
azienda e pratica sintetiche. Labirinto V1 rimane una regressione separata e
non è stato modificato. Nessuna nuova valutazione LLM è inclusa nel congelamento.

## Contenuti

| Materiale | Percorso | Destinazione |
|---|---|---|
| Modulo originale | [input/modulo.docx](input/modulo.docx) | FORM immutabile |
| Fonti | [sources.json](sources.json), input/sources/ e avviso PDF | Corpus consentito; tre Company, un General distrattore, una procedura |
| Richiesta iniziale | [input/richiesta-iniziale.txt](input/richiesta-iniziale.txt) | Unico input USER disponibile a T0 |
| Word gold | [evaluation/gold.docx](evaluation/gold.docx), [PDF LibreOffice](evaluation/gold-libreoffice.pdf) | Solo valutatore |
| Attese di ogni destinazione | [evaluation/gold.json](evaluation/gold.json) | Solo valutatore |
| Inventario leggibile | [evaluation/inventario.md](evaluation/inventario.md) | Solo valutatore |
| Scenario e risposte | [scenario](evaluation/scenario.md), [copione](evaluation/risposte-user.json) | Solo valutatore; inviare solo la risposta pertinente quando richiesta |
| Protocollo | [PROTOCOLLO.md](PROTOCOLLO.md) | Regole del confronto |
| Integrità | [manifest.json](manifest.json) | Hash di tutti i materiali congelati |

**Gold, inventario, scenario e copione completo non entrano nel prompt né nella KB.**
Non caricare ricorsivamente tutta questa directory. Usare esclusivamente
l'allowlist del manifest per gli input. Il PDF dell'avviso descrive requisiti
della procedura; il testo General non prova fatti di Mapi.

## Copertura autoriale

267 destinazioni censite dall'originale: **187 testuali, 67 celle di preferenza,
13 checkbox native**. Le 64 destinazioni testuali attese contengono 60 occorrenze
documentali e quattro testi USER; 123 restano vuote, con motivi e checkpoint.
Sei X e tre checkbox native sono selezionate. Questi numeri descrivono il gold,
non risultati o percentuali di accuratezza di un modello.

Il censimento comprende rami alternativi e righe di continuazione: non deriva
dal solo catalogo di campi riconosciuto dal motore. Gli indici fisici sono
accompagnati da etichetta, soggetto, ramo e testo originale localizzabile.
Valori e scelte provengono dal gold dell'utente e dalla revisione delle fonti,
non dagli output storici del compilatore.

Gli identificativi sintetici sono conservati senza validarli come reali;
firma, allegati e verifica delle abilitazioni restano fuori dal perimetro.
La fedeltà visuale è controllata sulle nove pagine del PDF LibreOffice; Microsoft Word
non è disponibile nell'ambiente. I limiti sono parte della specifica V1.

## Riproduzione e versioni

Prima di ogni confronto verificare tutti gli hash del manifest e registrare
commit, configurazione, input, dialogo e artefatti reali in una nuova directory
di audit. Applicare il protocollo in un ambiente separato dalla KB corrente.
Il pacchetto è pronto come materiale; istanza isolata e nuova baseline integrata
non sono state eseguite in questa preparazione.

Il runner esistente per Labirinto usa un altro schema di fixture e misura la
sola proposta: **non passare questa directory al suo --fixture presumendola
compatibile**. L'adattatore per un confronto integrato va discusso prima
dell'implementazione; non cambiare le aspettative per adattarle al motore.

Qualsiasi modifica semantica o documentale successiva richiede una nuova
versione conservando V1. Il manifest non include se stesso. Il registro
completo rimane [relazioni.md](../../../relazioni.md).
