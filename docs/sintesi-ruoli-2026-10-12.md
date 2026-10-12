# Sintesi: preservare il contesto dei ruoli

## Diagnosi e protocollo congelato

Intervento autorizzato sulla sintesi conversazionale del motore globale V10.
Non cambia retrieval, classificazione dei candidate, parser, renderer o UI.

L'audit conserva già soggetto e prova SOURCE della relazione persona–ruolo.
Il JSON di `compilation_global_dialogue.model_context` perde tale prova: include
il ruolo richiesto dal FORM e solo gli estratti dei singoli valori (nome,
qualifica, Ordine, numero). La revisione non può quindi distinguere bene ruoli
attuali, cessati o destinazioni differenti. Non occorre aggiungere chiamate.

**Correzione della diagnosi precedente:** il replay del gruppo aveva ricostruito
un catalogo grezzo da `initial_state`, senza `anchor_paragraph_ids`, invece del
catalogo arricchito da `build_global_input` persistito dall'analisi reale. Tutti
i `form_context` della sintesi di quel replay erano vuoti. Il risultato 8/12
resta archiviato e il criterio fallito resta tale, ma non costituisce da solo
prova di regressione applicativa. Il runner ora usa il catalogo corretto.

Congelati prima delle nuove API sette casi in
`demo-documents/benchmark-sintesi/v1/`, manifest SHA256, nessun gold nel prompt:
Catanzaro con/senza conferme, Labirinto con risposte già acquisite, due incarichi
generici attuali/uno cessato/entrambi cessati/ruolo differente. Audit reali
precedenti rivalidati e proposte autoriali per i controesempi, non nuove analisi
SOURCE. Un'unica chiamata reale DeepSeek Flash per caso/serie, massimo sette,
timeout 45s/output2048, nessun retry o selezione degli output. Il catalogo include
gli stessi anchor dell'applicazione. Il benchmark non scrive sessioni live.

Runner: `docs/benchmarks/benchmark_narration_roles.py`; replay HTTP isolato:
`docs/benchmarks/replay-group-confirmation.py --output ...`.

La soluzione prevista conserva in un contesto condiviso bounded il soggetto,
il ruolo richiesto e gli estratti SOURCE della relazione già groundata, con
riferimenti per proposta. La sintesi resta soltanto un gate di esclusione:
non inventa valori né promuove proposte a RESOLVED. I risultati e i limiti della
misura vengono aggiunti dopo le serie prima/dopo.

## Modifica applicativa

`model_context` conserva `role_contexts`, deduplicato per binding validato,
soggetto ed entity. Ogni proposta lo riferisce con `role_context_slot`; un'altra
persona o un altro binding non condivide il contesto. La mappa contiene ruolo
FORM, ruolo SOURCE, soggetto e prova SOURCE del ruolo già controllata sul field.
Non viene ricostruita una relazione da testi liberi o proposte non validate.
Il riferimento alla proprietà resta la proposta del singolo campo; i quattro
dati del direttore tecnico condividono una prova di ruolo, non i valori.

Esempio ridotto del JSON reale AFTER (gli ID tecnici restano nell'audit backend):

```json
{
  "role_contexts": [{
    "slot": 1,
    "subject": "Ing. Elisa Romano",
    "entity": "person",
    "required_role": "direttore tecnico",
    "source_role": "direttore tecnico",
    "grounding": "literal_match",
    "semantic_review_required": true,
    "sources": [{
      "name": "generalita-mapi.md",
      "quote": "### Ing. Elisa Romano - direttore tecnico",
      "role": "source", "scope": "global", "category": "company"
    }]
  }],
  "document_values": [{
    "proposal_slot": 12,
    "label": "numero di iscrizione all’Albo professionale:",
    "value": "8421",
    "role_context_slot": 1
  }]
}
```

Budget: rimane il massimo di 40 proposte, quindi al massimo 40 contesti di ruolo.
Due estratti SOURCE/contesto, 800 caratteri/estratto con flag `truncated`,
600 per il ruolo FORM, 200 per soggetto/ruoli, 100 per entity. Estratti di valore
e budget chiamate/output della sintesi invariati. Contesti ammessi solo per
fact e binding GROUNDED_PROPOSAL, senza errori, relazione del field literal_match;
FORM e General KB non diventano prove personali. La guardia non promuove mai
a RESOLVED: il task distingue anche incarichi attuali/cessati e destinatari
diversi, ma può solo sospendere proposte, non renderne ammissibili di nuove.
La finalizzazione rivalida comunque SOURCE, destinazione, condizioni e DOCX.
Le esclusioni storiche già persistite rimangono cumulative, senza migrazione
o revoca automatica: per osservare il confronto usare una nuova sessione.

## Risultati reali congelati

Una sola serie BEFORE e AFTER, senza retry né modifiche durante ciascuna serie.
I risultati misurano selezioni e domande sui sette audit, non accuratezza di
moduli completi o tutte le frasi libere. Gold congelato nel commit `30065fe`,
fix in `78b0776`. Nessun risultato atteso passato al modello.

| Caso | BEFORE | AFTER | Esito verificato |
|---|---|---|---|
| Catanzaro, conferme presenti | 12/12 ammessi | 12/12 ammessi | nessun direttore bloccato |
| Catanzaro, conferme assenti | 0 export, 2 domande | 0 export, 2 domande | nessuna condizione assunta |
| Labirinto, risposte già acquisite | 17/17 ammessi | 17/17 ammessi | rinvii conservati |
| Due ruoli attuali | 4/4 ammessi | 4/4 ammessi | persona e numeri distinti |
| Primo incarico cessato | 2 valori impropriamente ammessi | 2 sospesi, 2 ammessi | no contaminazione del secondo ruolo |
| Entrambi cessati | 4 valori impropriamente ammessi | tutti sospesi | 0 valori esportabili |
| Ruolo SOURCE diverso | 2 ammessi, altri già scartati | invariato | validator autoritativo |

**5/7 -> 7/7**, da sei accettazioni improprie di campi a zero nei controesempi
misurati. Nessun miglioramento inventato per Catanzaro 8->12: il vecchio 8/12
era un replay con contesto vuoto. Il confronto corretto resta 12->12.

| Serie | Chiamate | Input token | Token totali | Tempo AI |
|---|---:|---:|---:|---:|
| BEFORE sette casi | 7 | 13.619 | 14.692 | 10,49s |
| AFTER sette casi | 7 | 16.801 | 18.019 | 12,20s |
| Replay HTTP BEFORE | 4 | 12.438 | 12.895 | 5,06s |
| Replay HTTP AFTER | 4 | 12.926 | 13.419 | 4,90s |

L'incremento medio del prompt è **455 token/caso**; per la sintesi Catanzaro
**449 token** (2.707->3.156). Nessuna chiamata aggiunta, nessun risparmio token
rivendicato. I tempi dipendono anche da cache/provider: serie singole, non
benchmark statistico di latenza. Totale: **22 chiamate /59.025 token /32,65s AI**.

## Replay fino al Word

Corretto il catalogo nel runner prima del BEFORE. Due nuove sessioni in snapshot
privati, una per versione; analisi reale precedente rivalidata contro originali
e corpus, zero nuove analisi o valori USER. Routing, gate USER e sintesi reali;
HTTP ASGI, non browser. Un turno conferma entrambe le condizioni; un secondo
turno chiede esplicitamente la bozza parziale. Stesso checkpoint, nessuna nuova
SOURCE evaluation o inferenza sul resto del documento.

BEFORE e AFTER: **12 valori SOURCE correttamente scritti** e zero USER fattuali.
Cinque aziendali, tre omologhi nella sezione società di ingegneria e nome,
qualifica, Ordine e numero **8421** del direttore tecnico. Stato/report/Word
concordano; originali, altre celle e checkbox invariati, solo document.xml
modificato con banner. Tabelle live inalterate; snapshot/chiavi eliminati.
Restano 307 candidate, 293 omesse, zero RESOLVED: bozza parziale, non completa.

## Verifiche e limiti

Software con provider simulati: quattro test protocollo iniziali /1,97s;
**143 mirati /21,30s** dopo il fix. Verificano anchor reali, grounding,
separazione soggetti, prova di ruolo, assenza di mutazioni, esclusione delle
prove non validate/FORM/General KB, budget40/2/800 e condizioni non confermate.
Nel primo preflight un test assumeva che tutti i candidate avessero un binding,
anche gli omessi: corretto il test, non i dati. Ruff corretto per stile prima
delle API. **1.985 backend completi /144,54s**, Ruff backend/runner e diff check
passati. Frontend/browser non ripetuti: nessun contratto/API/UI modificato;
il replay ha attraversato gli endpoint HTTP ASGI.

Limiti: la revisione semantica resta probabilistica; riceve estratti del ruolo,
non l'intero documento SOURCE. Un contesto non citato o troncato può restare
invisibile. La narrazione Catanzaro AFTER conserva cautele generiche sull'attualità
dell'incarico, pur senza sospendere i valori: il wording non è garantito da questi
sette gold. Nessuna cura di sparse coverage, checkbox native, Ordine/numero in
nuove analisi o comandi composti. Non è una ragione per congelare tutta la qualità
semantica come risolta. Nessuna modifica RAG/parser/renderer/UI/API.

Acquisizioni: `backend/data/compilation-audit/narration-roles-20261012/`.
[Metriche, messaggi e confronti](benchmarks/2026-10-12-narration-roles.json).
Bundle sanificato e manifest in `docs/benchmarks/2026-10-12-narration-roles-*`.

[Acquisizioni sanificate](benchmarks/2026-10-12-narration-roles-audit.tar.gz):
218 file /1.143.542 byte, verificati byte per byte, nessuna chiave o snapshot DB.
SHA256 `be28938aa7c3bd0aa98b69d0e0c01ce60c4427c3615245da2e15910b3588675b`;
[manifest dei file](benchmarks/2026-10-12-narration-roles-manifest.json).
