# Trapani: diagnosi e recupero delle proposte SOURCE — 11 ottobre 2026

Il caso vuoto è superato nel percorso sperimentale con ragionamento low e
compito esplicito di proposta: gli stessi otto dati aziendali sono conservati
in tre output reali rivalidati sul gate finale e in una nuova chiamata reale.
**Non è ancora un DOCX compilato:** tutte queste proposte restano bloccate
finché applicabilità/soggetto/proprietà non sono verificati. Zero RESOLVED e
zero scritture in tutte le prove. Nessuna attivazione nella V1/chat.

## Input e protocollo

Stesso Trapani del [sorteggio precedente](benchmark-trapani-casuale-2026-10-11.md),
seed 2732483673986547453, nessuna nuova estrazione. Originale
`demo-documents/bandi/trapani-green/originali/manifestazione-interesse.docx`,
SHA-256 `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`.
115 candidate testuali, nessuna checkbox strutturale. Corpus congelato del
workspace autorizzato `prova`: 17 chunk globali, 13 Company/4 General, zero
fonti di progetto. Il progetto Trapani non esiste localmente; non creato né
usato per aggirare isolamento. Nessun upload, USER o sessione persistente.

Fixture Labirinto V1, fonti e gold invariati; gold mai incluso nel prompt.
Trapani non ha gold: il file manual-only vuoto serve solo al caricamento del
runner, il suo fixture-score NON viene usato come misura di qualità.
Una chiamata per acquisizione, nessun retry/reviewer/fallback automatico.
Le serie sono congelate e concluse prima di cambiare codice; tutti gli esiti,
anche negativi, sono conservati. Il modello reale è il profilo deepseek-flash.

## Cause riscontrate e correzioni

1. **Emissione e applicabilità accoppiate.** V7 ammetteva valori già applicabili;
   il backend mantiene semantic=unknown. I dati aziendali del ramo condizionale
   sparivano insieme all'assegnazione. V8 esprime conditional con fatto SOURCE,
   condizioni FORM e motivo. I dati restano proposed_value, mai valori selezionati.
2. **Granularità ambigua.** La regola sull'indirizzo intero scoraggiava componenti
   richieste in posizioni separate. Ora la granularità segue la destinazione:
   dato intero se richiesto intero, componenti letterali distinti se campi distinti.
3. **Quote FORM fragili.** Accento ASCII con apostrofo, underscore adiacenti e
   diversa larghezza grafica dei placeholder provocavano rifiuti inutili.
   Normalizzazione deterministica e offset al testo originale; niente fuzzy,
   riordini o prefissi numerici. Identificativi interni e matcher SOURCE invariati.
4. **Compito implicito sul template bianco.** Il modello talvolta richiedeva
   un'intestazione già presente al soggetto SOURCE. JSON/TASK ora dichiarano
   proposal_stage=source_backed_hypotheses: proporre dati documentati non attesta
   scelta del partecipante/rappresentanza. Persone/ruoli restano soggetti ai gate.
5. **Supporto della condizione contaminava dati indipendenti.** Nel primo raw
   hypothesis-stage i campi avevano prove valide, ma la condizione referenziava
   f_tipo non letterale e fatti di dimensioni diverse. Solo V8 separa clausola
   FORM reale da supporto SOURCE opzionale: quest'ultimo resta REJECTED con errori
   visibili, la condizione resta unknown. Ogni campo verifica le proprie SOURCE.
   Nessun f_tipo riparato e nessuna condizione resa vera da FORM.

Gli estratti della traccia del modello sono diagnostici: non provano motivazioni
universali delle risposte precedenti e non entrano come evidenze. Il solo cambio
conditional non bastava: Trapani era ancora vuoto in tre prove V8 senza thinking.
Ablation del contesto degli slot e dei dati simulati ancora vuote; TASK compatto
con associazioni troppo larghe, non adottato. Il solo chiarimento semantic=unknown
ha ancora prodotto un vuoto. Nessun fallimento è stato rimosso dal confronto.

## Risultato Trapani e prova causale del gate

Tre raw congelati hypothesis-stage (`936df7a`) proponevano gli stessi otto dati,
con risultati 0/8/9 conditional grounded. Rivalidando **gli stessi raw**, senza
nuove risposte o modifiche a input/fatti, il gate finale produce **9/8/9**:
sempre gli otto dati corretti del ramo ingegneria, più PEC comunicazioni in due.
L'errore del supporto SOURCE della condizione è ancora presente nell'audit.

Nuova acquisizione reale su `396e7a6`, input/TASK identici: **nove conditional
grounded**, **39.318 token** (26.450 input + 12.868 output, di cui 11.279 di
ragionamento), **53,5899 s AI**. Otto dati riportati sotto e PEC comunicazioni.
Tutte le 115 posizioni hanno validation=REVIEW_REQUIRED; 106 non assegnate,
nessuna equivale automaticamente a campo obbligatorio mancante.

| Candidate | Richiesta locale | Valore proposto | Provenienza effettiva | Stato |
|---|---|---|---|---|
| `p75.s0` | Società di Ingegneria | Mapi Ingegneria S.r.l. | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s1` | Via/P.zza | Via Giovanni Amendola 172/C | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s2` | Comune | Bari | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s3` | CAP | 70126 | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s4` | Prov | BA | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s5` | P.IVA | IT01234567890 | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s6` | Tel. | +39 080 000 2040 | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |
| `p75.s8` | P.E.C. | mapi.ingegneria@pec.demo | SOURCE, visura-mapi-ingegneria-simulata.pdf, chunk -30 | conditional / REVIEW_REQUIRED |

Per tutti: value=null, fact_id=null, written_value=null,
proposal_grounding=GROUNDED_PROPOSAL. Documento/chunk/ruolo/scope/categoria/hash
restano nell'audit. Il codice fiscale e PIVA demo sono fittizi: si conserva il
valore riportato, senza correggerlo o certificarne validità reale. FONTI 2026 e
bando storico non attestano possesso dei requisiti alla data della gara.

PEC comunicazioni p107.s0 non significa che sia stata scelta dall'utente.
Fax, CF personale del dichiarante, firmatario, numeri di altri albi e firma
restano non assegnati. Il numero 8421 del direttore non viene trasferito agli
albi del dichiarante/paesaggista/agronomo. Originale invariato, nessun renderer.

## Controllo sul benchmark fisso e limiti

Nuova Labirinto `396e7a6`: **13 GROUNDED_PROPOSAL + sei conditional grounded**,
17 target letterali, **32.419 token/62,8407 s AI**. Cinque dati societari e
alternative recapito/polizza conservati; nessuna scelta fra alternative.
Nome direttore, qualifica e 5739 conservati come proposte condizionate.
**Limiti osservati:** ordine professionale unito al numero nella proposta e
quattro checkbox tipologia omessi. Letteralità del valore non prova correttezza
della proprietà. semantic_review_required rimane obbligatorio; nessuna percentuale
semantica o miglioramento generale di completezza dichiarato. Gold invariato.

Senza thinking i controlli Trapani restano vuoti, anche dopo il contesto esplicito.
Il solo prototipo/runner ora usa thinking low predefinito (`81d9232`), con
--no-thinking per confrontare. Nessuna modifica a profili UI/V1. Le richieste
prodotte dal nuovo default sono identiche a quelle delle ultime due chiamate
reali con flag esplicito; confronto e patch salvati. Una sola chiamata anche
nel default, nessun fallback dopo vuoto. Non è una garanzia contro ogni omissione
stocastica o un'attivazione in produzione.

## Misure complete, comprese le prove fallite

**38 nuove chiamate reali**, **1.223.138 token**, **1.484,9211 s AI aggregati**.
Non è la durata E2E dell'intervento; test/preparazione/analisi sono esclusi.
Nessun risparmio di token dimostrato: una risposta vuota costa meno, ma non svolge
il compito. Le tre acquisizioni storiche incluse per replay non sono nuove chiamate.

| Acquisizione | Thinking | Esito | Conditional grounded | Token | Secondi AI |
|---|---|---|---:|---:|---:|
| baseline | off | proposal_audited | 0 | 25,362 | 1.6020 |
| ablation | off | proposal_audited | 0 | 25,406 | 1.4228 |
| compact | off | proposal_audited | 0 | 23,396 | 1.9511 |
| explain | off | failed | 0 | 25,729 | 14.6140 |
| conditional-v8-20261011/trapani/1 | off | empty_proposal | 0 | 26,176 | 1.2396 |
| conditional-v8-20261011/trapani/2 | off | empty_proposal | 0 | 26,176 | 1.1301 |
| conditional-v8-20261011/trapani/3 | off | empty_proposal | 0 | 26,176 | 0.9642 |
| conditional-v8-20261011/labirinto/1 | off | proposal_requires_review | 8 | 22,946 | 19.2677 |
| conditional-v8-20261011/labirinto/2 | off | proposal_requires_review | 7 | 20,035 | 11.4844 |
| conditional-v8-20261011/labirinto/3 | off | proposal_requires_review | 6 | 20,008 | 11.4734 |
| slot-context | off | empty_proposal | 0 | 27,344 | 1.0201 |
| reported-data | off | empty_proposal | 0 | 26,382 | 1.2720 |
| compact-v8 | off | proposal_requires_review | 0 | 30,167 | 21.2387 |
| compact-v8-clear | off | proposal_requires_review | 5 | 28,929 | 18.9397 |
| thinking-v8 | low | proposal_requires_review | 6 | 35,073 | 46.7679 |
| form-grounding-20261011/trapani/1 | low | proposal_requires_review | 4 | 38,157 | 60.1837 |
| form-grounding-20261011/trapani/2 | low | proposal_requires_review | 5 | 41,165 | 74.7100 |
| form-grounding-20261011/trapani/3 | low | proposal_requires_review | 7 | 45,220 | 84.6493 |
| form-grounding-20261011/labirinto/1 | low | proposal_requires_review | 0 | 33,082 | 64.8494 |
| form-grounding-20261011/labirinto/2 | low | proposal_requires_review | 0 | 34,149 | 70.6139 |
| form-grounding-20261011/labirinto/3 | low | proposal_requires_review | 0 | 32,491 | 62.6596 |
| granularity-v8-20261011/trapani/1 | low | proposal_requires_review | 8 | 41,017 | 67.2782 |
| granularity-v8-20261011/trapani/2 | low | proposal_requires_review | 8 | 43,219 | 71.2704 |
| granularity-v8-20261011/trapani/3 | low | proposal_requires_review | 0 | 41,571 | 69.0587 |
| granularity-v8-20261011/labirinto/1 | low | proposal_requires_review | 0 | 33,324 | 71.2260 |
| granularity-v8-20261011/trapani-no-thinking/1 | off | empty_proposal | 0 | 26,238 | 1.2859 |
| semantic-contract-20261011/trapani/1 | low | proposal_requires_review | 8 | 41,211 | 62.5701 |
| semantic-contract-20261011/trapani/2 | low | empty_proposal | 0 | 33,994 | 42.8133 |
| semantic-contract-20261011/trapani/3 | low | proposal_requires_review | 8 | 36,185 | 50.2289 |
| semantic-contract-20261011/labirinto/1 | low | proposal_requires_review | 6 | 29,991 | 66.1185 |
| semantic-contract-20261011/trapani-no-thinking/1 | off | empty_proposal | 0 | 26,293 | 1.7199 |
| hypothesis-stage-20261011/trapani/1 | low | proposal_requires_review | 0 | 37,618 | 61.5860 |
| hypothesis-stage-20261011/trapani/2 | low | proposal_requires_review | 8 | 40,609 | 66.8716 |
| hypothesis-stage-20261011/trapani/3 | low | proposal_requires_review | 9 | 40,087 | 59.5798 |
| hypothesis-stage-20261011/labirinto/1 | low | proposal_requires_review | 4 | 33,422 | 82.4086 |
| hypothesis-stage-20261011/trapani-no-thinking/1 | off | proposal_requires_review | 3 | 33,053 | 22.4211 |
| independent-grounding-20261011/trapani/1 | low | proposal_requires_review | 9 | 39,318 | 53.5899 |
| independent-grounding-20261011/labirinto/1 | low | proposal_requires_review | 6 | 32,419 | 62.8407 |

Le metriche literal_target includono value/conditional e citazioni del gold;
non sono un giudizio indipendente su entailment, ruolo o applicabilità.
Le diverse ablation sono diagnosi controllate, non confronti di accuratezza fra
corpus. Tutti i raw, anche l'output diagnostico volutamente fuori schema, sono salvati.

## Verifiche e riproduzione

Software, separato dalla qualità del modello reale: **338 mirati/14,08 s**,
**1.765 backend/110,03 s**, Ruff e fixture --check passati. Coperti provenienza,
isolamento, SOURCE invalida, quote/ancore, ruolo, condizione sconosciuta/falsa,
supporto SOURCE opzionale errato, confronto invalido, campo sorgente invalido e
nuovo default CLI. Failure iniziali delle verifiche sono riportate in relazioni.
Frontend/browser non rieseguiti: nessuna modifica a UI/contratti frontend.

Manifest, codice congelato contro commit, request/input, replay su codice acquisito,
originali e cinque fingerprint live verificati. Scope dei fingerprint:
projects/project_files/document_compilations/compilation_sessions/conversations;
nessun hash preventivo delle altre tabelle acquisito. Nessun DB/sessione modificati.
Nessuna migrazione o reindicizzazione necessaria.

Con il corpus congelato ripristinato, da backend:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_global.py \
  --fixture data/compilation-audit/bando-casuale-20261011/input-workspace \
  --profile-project prova --output data/compilation-audit/NUOVA-PROVA-TRAPANI
```

Usare un output nuovo e un profilo DeepSeek configurato. Default low; aggiungere
--no-thinking per il controllo. Nessun risultato/gold in input. Per riprodurre
una vecchia acquisizione usare codice e richiesta salvati: i vecchi script senza
flag erano eseguiti con il default precedente, non quello corrente.

[JSON completo](benchmarks/2026-10-11-trapani-diagnosis.json),
[registro cronologico](../relazioni.md),
[bundle dei raw](benchmarks/2026-10-11-trapani-diagnosis-audit.tar.gz),
[checksum](benchmarks/2026-10-11-trapani-diagnosis-audit.tar.gz.sha256).
Il bundle ripristina i percorsi relativi a backend/data/compilation-audit e include
raw HTTP/output, input/TASK/schema, uso token/tempi, codice per ogni acquisizione,
fixture congelate, validazioni, replay, protocolli, controlli e tre raw storici.
Esclude DB, .env, .ai-key e cache; assenza della chiave configurata verificata senza
stamparla. File e contenuti confrontati byte per byte.

**Prossimo passo da discutere:** verifica indipendente di applicabilità,
soggetto/proprietà prima dell'adapter/attivazione nella chat. Questo intervento
recupera dati utili senza dichiararli automaticamente compilabili. Commit piccoli locali, nessuno squash/reset o push; i passi restano recuperabili.


Archivio verificato: **1.211 file, 7.976.279 byte**, SHA-256
`7035ffc9c7701e69fe5ec9c08a5616c76d6ad10ff2df7ae25991cd2ca3a66d2b`.
