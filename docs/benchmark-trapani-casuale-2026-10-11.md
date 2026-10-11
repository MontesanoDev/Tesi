# Prova occasionale su un altro bando — Trapani Green, 11 ottobre 2026

**Esito negativo: nessuna proposta su 115 posizioni.** I controlli di provenance
restano conservativi, ma questa chiamata non ha prodotto compilazione utile.
È una prova di trasferimento del compilatore globale sperimentale, non una
misura della chat V1 o della compilazione completa. Nessuna modifica al motore.

## Selezione e condizioni della prova

Richiesta dell'utente: benchmark fisso più prove occasionali su altri bandi
scelti a caso. Labirinto V1, fonti e gold restano congelati. Estrazione uniforme
fra gli originali Minervino di Lecce e Trapani Green; Catanzaro escluso perché
già usato estesamente. Seed `2732483673986547453`, zero nuove estrazioni:
selezionato **Trapani Green**.

Originale: [manifestazione-interesse.docx](../demo-documents/bandi/trapani-green/originali/manifestazione-interesse.docx),
SHA-256 `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`.
Il parser individua 115 candidate testuali, nessun checkbox. Non verificata
quindi la copertura delle caselle, problematica nel benchmark fisso.

Trapani non è un progetto presente nel DB locale. Il primo controllo del corpus
con quell'ID restituisce zero fonti: **nessuna chiamata AI su questo input**.
Conservata l'estrazione, usato il workspace autorizzato `prova`: nessuna fonte
di progetto, 17 chunk globali ammessi, **13 Company / 4 General**, da tre documenti:
`generalita-mapi.md`, `visura-mapi-ingegneria-simulata.pdf`,
`progettazione-opere-pubbliche.txt`. Scope e category distinti, tutti role=source;
nessun bypass di isolamento o documento di altro progetto.

Il DOCX è copiato in un pacchetto isolato per riutilizzare l'esatto runner
`--fixture`. **Non è una nuova fixture con gold**: `manual-only.json` dichiara
assenza di aspettative. Il file `fixture-score.json` emesso dal runner va
ignorato; non è una misura di qualità. Nessun upload, sessione, input USER
o DOCX generato. Le istruzioni nella cartella demo non sono SOURCE né decisioni
dell'utente. Bando storico e dati societari simulati del 2026: non si certificano
requisiti o condizioni alla data della procedura.

## Chiamata reale e risultato

Codice congelato `eacecbc2641049c2e633d09665771ed9b6912655`, contratto V7,
catalogo V3, deepseek-flash reale, thinking disabilitato, temperatura 0,1,
una chiamata, zero retry. Codice applicativo invariato durante e dopo la prova.

| Misura | Risultato |
|---|---:|
| Candidate | 115 |
| SOURCE chunk ammessi | 17 |
| Token input / output / totali | 25.332 / 30 / 25.362 |
| Token input cache hit | 2.560 |
| Tempo chiamata AI | 1,4473 s |
| HTTP / finish reason | 200 / stop |
| Fatti / condizioni / binding / assegnazioni proposti | 0 / 0 / 0 / 0 |
| Posizioni senza proposta, conservate REVIEW_REQUIRED | 115 |
| GROUNDED_PROPOSAL / RESOLVED / scritture | 0 / 0 / 0 |

Raw completo:

```json
{"version":7,"uncertain_paragraph_ids":[],"conditions":{},"bindings":{},"fields":{},"facts":{}}
```

Il vuoto nasce **prima della validazione**, nella risposta del modello. Non ci
sono valori poi rifiutati, errori di parsing o troncamenti segnalati. Lo schema
consente mappe vuote, con `additionalProperties` tipizzate per record non vuoti:
non forza il modello a emettere solo `{}`. Il prompt prescrive omissione di
assegnazioni non sostenute o con condizioni sconosciute. Il backend accetta
la struttura e conserva tutte le posizioni non valutate: `proposal_audited`
significa audit eseguito, **non compilazione riuscita**.
`uncertain_paragraph_ids=[]` non dimostra completezza delle condizioni.

Il provider non restituisce una motivazione per questa omissione totale.
Non possiamo attribuirla con certezza al ruolo, all'applicabilità, al contesto
o a una frase del prompt sulla base di una chiamata. Nessuna correzione o
ripetizione selettiva per ottenere un risultato migliore.

## Controlli manuali sul documento e sulle fonti

| Candidate | Contesto reale | Osservazione |
|---|---|---|
| `p12.s0`, `p12.s3` | Nome e CF del sottoscrittore | Nessuna proposta. Amministratore e CF aziendale non dimostrano identità/CF personale del firmatario. |
| `p75.s0`–`p75.s8` | Legale rappresentante di società di ingegneria: società, sede, PIVA, contatti | Tutto omesso. SOURCE -43/-44/-30 contengono denominazione, indirizzo, PIVA, telefono e PEC; i dati non provano da soli rappresentanza/applicabilità né ogni destinazione. |
| `p97.s0` | Iscrizione al proprio ordine del dichiarante | Nessun trasferimento automatico del numero 8421 del direttore tecnico. |
| `p112.s0`, `p113.s0` | Iscrizioni paesaggistica/agronomica | Nessun trasferimento improprio del numero dell'ingegnere. |
| `p107.s0` | PEC per comunicazioni | PEC aziendale nelle SOURCE, ma nessuna proposta o scelta verificata. |
| `p175.s0` | Firma | Nessuna proposta, write_protected conservato. |

Queste osservazioni non costituiscono un gold o una percentuale di accuratezza.
Valori omessi non diventano automaticamente MISSING o NA. Il test evidenzia
mancata copertura operativa; zero falsi positivi in un output vuoto non dimostra
capacità di associare correttamente dati e campi.

## Verifiche e archivio

Eseguiti: replay del validator identico, manifest, dieci file congelati contro
commit, riproduzione estrazione, request/input e corpus canonico coerenti,
hash dei due originali invariati. Fingerprint prima/dopo identici per `projects`,
`project_files`, `document_compilations`, `compilation_sessions`, `conversations`;
non acquisiti fingerprint preventivi delle altre tabelle. Nessuna prova browser.

Ruff e `create_compilation_benchmark.py --check` passati; diff/link controllati.
Suite pytest/frontend non ripetute: codice e contratti invariati. Un primo
confronto offline includeva metadata non inviati; corretto alla proiezione
canonica, failure conservata. Non è un cambio del motore o retry del provider.

- [Metriche e audit delle 115 posizioni](benchmarks/2026-10-11-trapani-casuale.json).
- [Bundle completo](benchmarks/2026-10-11-trapani-casuale-audit.tar.gz) e
  [checksum](benchmarks/2026-10-11-trapani-casuale-audit.tar.gz.sha256):
  **46 file, 227.201 byte**, SHA-256
  `dbfced38011073f2c67eede173b30dbab565073945d9009a500a305c259a7886`.
- Grezzi locali `backend/data/compilation-audit/bando-casuale-20261011/`:
  selezione, preflight anche fallito, input, codice, prompt/schema,
  raw HTTP/output/usage, audit, replay, fingerprint e log.
- Bundle confrontato byte per byte; nessun DB/configurazione privata/credenziale,
  controllo dell'assenza della chiave configurata senza stamparla.

Il benchmark fisso resta il confronto principale. Prove occasionali come questa
rilevano limiti di trasferimento e non vanno aggregate ai suoi punteggi.
I progressi su provenance/ruolo sono circoscritti; completezza e applicabilità
rimangono aperte. Nessuna attivazione del prototipo nella chat o nel renderer.
