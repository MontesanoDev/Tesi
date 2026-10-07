# Candidate → SOURCE → RESOLVED — 7 ottobre 2026

Intervento circoscritto all'associazione SOURCE della CompilationSession.
Configurazione reale: DeepSeek / `deepseek-flash`, Qdrant locale,
embedding BGE-M3/Ollama, progetto `minervino-di-lecce-elenco-sia`, originale
`domanda-partecipazione.docx`, form ID 153. I dati societari sono quelli demo
presenti nella Company KB; il provider del benchmark è reale.

## Diagnosi prima delle modifiche

Snapshot letto senza mutazioni dalla sessione
`514078f1a6f5493a9164bd38ff809fa4`, v4. Le proposte seguenti sono **nuove
chiamate diagnostiche reali** sullo snapshot: il prodotto non conserva il raw
storico di ogni resolve. Non sono presentate come output della vecchia richiesta.
La sessione manuale `72301a79dc70495299bdf24add3a0f24` mostrava lo stesso problema
di bucket sui due candidate, rimasti MISSING. Nessuna sessione preesistente è
stata aggiornata durante questa diagnosi.

| Candidate | Label | Contesto strutturale |
|---|---|---|
| `t0.r5.c1` | Operatore economico | Prima tabella anagrafica, dopo la procura e prima della forma giuridica; cella valore vuota |
| `t0.r6.c1` | Forma giuridica | Stessa tabella, dopo l'identità dell'operatore e prima delle sedi; cella valore vuota |

Il contesto completo comprende sottoscrittore, nascita, CF personale, carica,
procura, operatore, forma giuridica, sedi, CF/PIVA dell'operatore e telefono.
Parser/posizioni non erano la causa dei due rifiuti.

Per **entrambi** il cluster aveva queste query:

```text
Operatore economico dati effettivi operatore economico
Forma giuridica dati effettivi operatore economico
```

Pool complessivo recuperato nel batch:

| SOURCE ID locale | Chunk | Documento/file | Scope / categoria | Allowed per r5/r6 |
|---|---:|---|---|---|
| 1 | 4306 | avviso.pdf / 124 | project:minervino-di-lecce-elenco-sia | sì |
| 2 | 4299 | avviso.pdf / 124 | project:minervino-di-lecce-elenco-sia | sì |
| 3 | 4305 | avviso.pdf / 124 | project:minervino-di-lecce-elenco-sia | sì |
| 4 | 4298 | avviso.pdf / 124 | project:minervino-di-lecce-elenco-sia | sì |
| 5 | -43 | generalita-mapi.md / -7 | global / company | **no** |
| 6 | -44 | generalita-mapi.md / -7 | global / company | **no** |
| 7 | 4307 | avviso.pdf / 124 | project:minervino-di-lecce-elenco-sia | no |

Tutte sono `role=source`. Gli ID negativi rappresentano il corpus globale
nell'implementazione corrente. Company KB e General KB non sono state accorpate.

### Operatore economico

Primo raw del matcher: `supports=[]`. Motivo: le sole SOURCE ammesse 1–4 parlano
genericamente di operatori economici, senza identificare l'azienda da compilare.
La fonte aziendale era nel pool, ma fuori dal suo bucket.

Seconda prova diagnostica **solo su copie in RAM**, ammettendo la SOURCE 5 già
recuperata, senza mutare la sessione e senza cambiare codice:

```json
{
  "source_id": 5,
  "quote": "Ragione sociale: Mapi Ingegneria S.r.l.",
  "value": "Mapi Ingegneria S.r.l."
}
```

Rifiuto ulteriore in `validate_support` / `validated_supports`:
«la SOURCE non associa il valore al singolo dato e al soggetto».
`_requirement_tokens("Operatore economico")` eliminava entrambi i termini;
il controllo letterale non riconosceva la relazione fra un campo di identità
dell'operatore e la ragione sociale. Nessun errore del validatore DOCX sul valore.

### Forma giuridica

Raw del matcher, nel primo pool non modificato:

```json
{
  "source_id": 5,
  "quote": "Forma giuridica: Societa a responsabilita limitata.",
  "value": "Societa a responsabilita limitata"
}
```

Rifiuto preciso: **«SOURCE non ammessa per questo candidate»** in
`apply_matches`. L'ID 5 non era fra `[1, 2, 3, 4]`.
Controlli isolati sulla proposta: associazione e validatore DOCX passavano
entrambi se la fonte fosse stata ammessa. Il modello aveva indicato una prova
corretta, ma il backend confondeva appartenenza al cluster con pertinenza al campo.

### Punto di costruzione e filtro

In `compilation_session_resolution.retrieve_sources`, il vecchio
`coverage[field["id"]] = source_ids` assegnava soltanto il risultato del cluster
di ricerca. Il matcher vedeva anche il pool complessivo, ma
`apply_matches` rifiutava `support.source_id` fuori da quella lista.
Successivamente `validate_support` applicava il match letterale della label.
Query generiche e dipendenza dal cluster producevano quindi due falsi negativi
distinti; non mancavano i valori nella Company KB.

Acquisizioni complete: `before-matcher-input.json`, `before-matcher-prompt.json`,
`before-matcher-raw.txt`, `before-diagnosis.json`,
`before-assignment-prompt.json`, `before-assignment-raw.txt`,
`before-assignment-diagnosis.json`, nella directory locale ignorata
`backend/data/compilation-audit/candidate-source-20261007/`.

## Correzione generale

- Planner **solo della compilazione**, nello stesso passaggio bounded di
  pianificazione: cluster e fino a tre etichette SOURCE semanticamente equivalenti
  per requisito, ricavate da requisito e contesto strutturale. Non propone valori.
  Nessun dizionario di etichette del modulo demo o di nomi aziendali.
- Query sintetiche sulla proprietà, con ruolo personale quando presente, invece
  di ripetere etichette lunghe e il suffisso generico dell'operatore. Le condizioni
  FORM non vengono aggiunte indiscriminatamente ai campi di tutto il cluster.
- Una SOURCE nel pool di un altro cluster può essere riassociata al candidate
  aziendale soltanto se una proprietà locale della fonte ha una delle etichette
  equivalenti. Non si concede tutto il pool a tutti i campi.
- Per validare il valore, intestazione pertinente e valore devono essere nella
  **stessa proprietà locale** `intestazione: valore`, non in righe diverse di un
  profilo. Il requisito FORM originale resta grounded e invariato. Per persone
  e relazioni professionali restano i gate precedenti su dato/ruolo/numero.
- Quote e valore vengono ricondotti alla grafia della SOURCE solo se lo span
  normalizzato è contiguo e uguale per Unicode/case/whitespace. Non si correggono
  parafrasi o quote inventate e non si altera il renderer.
- Persistiti nomi di ricerca, query, chunk recuperati e chunk allowed. File,
  chunk, scope, categoria e ruolo dell'evidence rimangono riconoscibili;
  rilettura SQL, validatore DOCX e controllo finale della fonte corrente restano.

Budget: max 12 candidate per passo; tre chiamate LLM al massimo
(classificazione, piano SOURCE, matcher), anche con molti campi. Il piano
opera in un batch, con contesti deduplicati e senza retry/per-field call.
Max 6 cluster × 4 requisiti, 2 query/cluster, 12 query totali,
2 anchor/query, 4 evidence/cluster, pool massimo 24 chunk distinti,
bucket massimo 8 evidence/candidate dopo la riassociazione. In caso di piano
invalido si torna alle label letterali e al budget/coverage già esistente.

RAG FORM/SOURCE/MIXED generale, UI, parser, renderer e routing conversazionale
non modificati. Nessuna migrazione o reindicizzazione. Le vecchie MISSING
possono essere riesaminate tramite la API esistente, senza modifiche SQL.

## Benchmark reale finale

Codice congelato durante ciascuna esecuzione. Nuova conversazione
`conv-43455f51f75b4f2c`, nuova sessione
`46d5be7dcf444b18ac519d7bf55d1680`, originale ID 153.
Creazione e risoluzioni attraverso HTTP sul backend corrente, profilo reale
deepseek-flash; nessuna risposta/provider/retrieval simulato, nessun valore USER.

1. Creazione v1.
2. Resolve dei cinque candidate via API normale, v1 → v3, circa 20 s:
   quattro RESOLVED; la sede viene rifiutata perché un estratto/valore proposto
   non è presente letteralmente nella SOURCE. Il gate resta attivo.
3. **Un nuovo resolve esplicito del solo candidate sede**, v3 → v5, circa 20 s:
   cinque RESOLVED/SOURCE. Nessun reset degli altri quattro e nessun input di dati.
   Non è un retry automatico aggiunto al prodotto.

| Candidate | Requisito | Valore persistito | Stato | Provenance / evidence |
|---|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | RESOLVED | SOURCE, generalita-mapi.md, chunk -43 |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | RESOLVED | SOURCE, generalita-mapi.md, chunk -43 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | RESOLVED | SOURCE, generalita-mapi.md, chunk -43 |
| t0.r9.c1 | Codice fiscale operatore | IT01234567890 | RESOLVED | SOURCE, generalita-mapi.md, chunk -43 |
| t0.r10.c1 | Partita IVA operatore | IT01234567890 | RESOLVED | SOURCE, generalita-mapi.md, chunk -43 |

Tutte e cinque: file ID -7, scope global, categoria company, role source.
Il CF/PIVA è l'identificativo didattico letterale della fonte, non un dato reale
validato fiscalmente. Quote finali:

```text
Ragione sociale: Mapi Ingegneria S.r.l.
Forma giuridica: Societa a responsabilita limitata.
Sede legale di Mapi Ingegneria S.r.l.: Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia.
Codice fiscale e Partita IVA riportati nella visura demo: IT01234567890.
```

Il primo resolve raggruppava operatore, forma, CF e PIVA:
`Operatore economico Forma giuridica` / `C.F. P.IVA`, chunk
`4299, 4276, 4306, -43`; il cluster della sede usava
`Sede legale` / `Indirizzo sede legale`. Il resolve finale sede usa
`sede legale` / `indirizzo sede legale`, chunk `-43, 4308, 4307, -44`.
Tre richieste modello per resolve, nessuna nuova call indipendente per campo.

Stato finale persistito/riletto via GET: **5 RESOLVED, 274 PENDING,
0 USER_PROVIDED**, sessione CREATED perché il resto del documento non è ancora
analizzato. Nessuna generazione/finalizzazione: questo è il benchmark SOURCE
circoscritto, non un completamento di tutti i 279 candidate.
Un supporto aggiuntivo della sede è respinto dal gate di pertinenza; la prova
valida rimane quella del chunk -43. Gli errori delle alternative scartate
restano visibili senza invalidare la prova accettata.

Originale invariato: SHA-256
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
Le sessioni precedenti sono conservate. Stato, query, allowed, evidence e hash
del codice: `final-benchmark/` nella directory locale delle acquisizioni.

## Prove precedenti e limite residuo

Una prova iniziale con tutti i primi 12 candidate ha lasciato quattro dei cinque
campi PENDING perché il classificatore parafrasava le label, prima del retrieval.
Nella sessione nuova `2c1acae1e71c40e19989c28588e836d1`, l'operatore si è risolto
al primo passo e gli altri quattro dopo un resolve mirato via API, senza USER.
La prova precedente `bcf826fbc2e64872b729d536e63b1c2f` non risolveva l'operatore
con una query ancora troppo lunga: composizione SOURCE corretta successivamente,
prima del benchmark finale. I primi tentativi sono conservati; non vengono
presentati come successi automatici.

**Limite importante:** il collegamento SOURCE dei cinque campi è verificato,
ma l'esito al primo passo automatico non è stabile: classificazione iniziale
e quote del modello possono ancora produrre falsi negativi conservativi.
Questo intervento non modifica quel classificatore né promette la compilazione
completa senza riesame. Non sono state abbassate le garanzie per ottenere i valori.

## Verifiche software

Provider simulati e DB/storage temporanei per le regressioni; non sono misure
della qualità di DeepSeek. Coperti alias di proprietà generici, valori di un'altra
proprietà respinti, riassociazione da un altro bucket, SOURCE irrilevante respinta,
due candidate sulla stessa SOURCE senza scambi di valori, metadata conservati,
ripresa e rivalidazione alla finalizzazione; FTS5 e Qdrant. Coperti inoltre
fallback del piano, query bounded e normalizzazione conservativa degli span.

Esiti finali: **250 mirati**, **1079 backend completo**, Ruff e diff check passati.
Le nuove regressioni SOURCE sono 12. Comandi esatti riportati in STATUS.md.
I fallimenti intermedi della nuova fixture erano nella selezione simulata
delle coorti, corretta prima delle suite finali. Nessun frontend/contratto
modificato; test browser/frontend, lint e build frontend non rieseguiti.
Nessun commit o push.
