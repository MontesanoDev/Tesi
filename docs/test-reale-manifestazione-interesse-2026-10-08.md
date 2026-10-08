# Interpretazione semantica e manifestazione-interesse — 8 ottobre 2026

## Esito autorevole dopo la ricarica DeepSeek

**Il criterio principale è soddisfatto sul codice finale:** otto dati societari
utili RESOLVED/SOURCE, tipologia supportata da SOURCE, Fax MISSING, nessun firmatario
inferito e nessun dato della gara corrente accettato come servizio pregresso.
Il benchmark ha attraversato i checkpoint raggruppati senza errori provider.
**Il modulo completo non è READY:** rimangono chiarimenti e 30 candidate PENDING
per interpretazioni non validate. Non è stato generato un DOCX.

Sessione finale nuova `a0122f66352848de94e14c94146c6419`, v59,
WAITING_FOR_USER / deferred_summary. Codice identico alla versione che aveva superato
269 test mirati e 1.192 backend; nessun codice modificato durante o dopo la prova.
La suite precedente non è presentata come appena rieseguita dopo la ricarica.
Ruff e diff check rieseguiti e passati.

Base `main`, HEAD/origin-main `a5e2e2ea75924b86fcdb01074c067f909fa7e0cd`.
Nessun commit/push. README/start preservati byte per byte; STATUS aggiornato
soltanto alla fine preservando lo storico e le modifiche locali precedenti.
Sessione originale dell'app `85daf575481244cd934911c42b3567f4` invariata alla v77.
Tutte le prove nuove usano copie isolate di DB/storage/indice.

## Diagnosi e correzioni

- Slot fisico, proprietà normalizzata, soggetto, sezione e ruolo temporale sono
  distinti. Il backend collega `form_anchor` al candidate dell'originale;
  `semantic.subject_anchor`, `subject_relation`, `context_role`, `section_id`
  e condition restano verificabili nel FORM. Il contesto comprende la frase,
  gli altri slot e fino a dodici paragrafi non vuoti precedenti, entro 6.500
  caratteri; per le tabelle parte dall'inizio della tabella.
- Il nome normalizzato non deve comparire letteralmente nel FORM. Una revisione
  semantica indipendente deve approvare proprietà/soggetto/slot; quote e riferimenti
  strutturali rimangono letterali. La validazione persistita include un digest
  di requisito, binding, entità e condizione, ricontrollato prima di SOURCE/finalizzazione.
- Un'organizzazione rappresentata non è automaticamente la persona che la
  rappresenta. Gli enti pubblici sono organizzazioni valide con `entity=authority`;
  il controllo non richiede più `entity=company` per qualsiasi organizzazione.
- Una tipologia di organizzazione rappresentata, ancorata alla sezione FORM,
  viene conservata dal backend come condizione quando il modello la omette.
  `condition_complete` è un verdetto obbligatorio: il reviewer deve verificare
  anche i qualificatori geografici/giuridici. Non si elimina il vincolo estero
  mantenendo soltanto una generica tipologia. Il ruolo personale non viene
  inserito nella condizione di tipologia; nessuna scelta implicita del firmatario.
- Applicabilità condivisa soltanto per condizione/entità/sezione dello stesso
  originale. Le esclusioni fra alternative richiedono un gruppo FORM esplicitamente
  esclusivo; l'istruzione «eliminare le opzioni non pertinenti» non basta a inventare
  una scelta unica. SOURCE/USER attestano i fatti, FORM descrive il predicato.
- `PAST_SERVICE` è distinto da `CURRENT_PROCEDURE`. Una proprietà formalmente
  corretta non basta: prima di approvare proposte storiche si estraggono fatti di
  prestazioni già eseguite **senza mostrare i candidate o i valori desiderati**.
  Esecutore e servizio devono essere nominati nello stesso passaggio SOURCE;
  quote e valore proposti devono appartenergli. La prova viene persistita e
  riletta in finalizzazione. Istruzioni di gara/attività offerte non sono esperienze.
- Una seconda revisione SOURCE verifica proprietà, soggetto e relazione; i bucket,
  scope/role/category, literalità e validatore DOCX restano obbligatori.
  Le query dei profili e delle esperienze ricevono un contesto generale appropriato.
- Underscore, linee vuote, placeholder, etichette senza valore, N/A e indicazioni di
  campo non compilato non possono diventare valori RESOLVED. Le sigle informative,
  per esempio NA, restano ammesse. La provincia BA non viene più estratta dal prefisso
  di Bari: `source_span` richiede token completi e ripristina la grafia della SOURCE.
- Gli item di revisione localizzabili non validi non scartano quelli validi.
  Un indice SOURCE non richiesto per un candidate noto viene registrato/ignorato;
  un verdetto duplicato disabilita soltanto la proposta duplicata. Candidate
  sconosciuti, envelope globalmente invalidi e failure provider restano espliciti.

File principali: `compilation_semantics.py`, `compilation_session_models.py`,
`compilation_session_resolution.py`, `compilation_sources.py`,
`compilation_sessions.py`, `compilation_clarifications.py`, `document_compilation.py`.
UI, parser DOCX, renderer e orchestrazione chat non modificati da questo intervento.
Il collegamento al contesto condiviso non riprogetta il raggruppamento delle domande.

Bounded: fino a 12 candidate, 6 al retry; counter persistenti separati,
**massimo due tentativi per fase/candidate**, 36 passi/600 secondi per ciclo.
Al massimo sei chiamate modello per resolve quando tutte le verifiche sono necessarie;
nessuna chiamata per singolo field o loop di riparazione. Nessuna migrazione o
reindicizzazione dei dati utente; le vecchie sessioni non vengono riscritte.

## Verifiche software finali

**269 test mirati passati; 1.192 test backend completi passati** in quattro gruppi
consecutivi da 385, 343, 398 e 66. Ruff e diff check passati.
Sono 46 regressioni nuove sopra i 1.146 test del precedente intervento retry.
Provider simulati e DB/storage temporanei: questi test non certificano qualità reale.

Copertura: più slot/proprietà nella stessa frase; label non letterali supportate e
non supportate; anchor errato; persona/organizzazione/ente pubblico; condizione
implicita e qualificatori esteri; applicabilità condivisa da SOURCE; esperienza
pregressa positiva e rifiuto di SOURCE corrente; literalità e rilettura della prova;
placeholder; sigle; output parziali e duplicati; cinque proprietà Company precedenti;
retry separati/esaurimento; grouped, SKIP, UNKNOWN, PAUSE/RESUME, active question e
provenienza FORM/SOURCE/USER. Frontend invariato e non ritestato.

Il primo tentativo di suite in un unico processo era stato ucciso dall'OOM;
le esecuzioni complete successive hanno usato gruppi sequenziali. Non sono test
skippati. I conteggi precedenti 1.174/1.182/1.186/1.189/1.191 descrivono versioni
intermedie, non la suite finale.

## Configurazione del benchmark finale

DeepSeek reale, modello `deepseek-flash`; Qdrant locale reale, BGE-M3/Ollama.
Stesso DOCX form 29, stesso corpus Company (visura + generalità, 14 chunk), General
KB e fonti del progetto Trapani. Indice già preparato: 76 chunk, 1.024 dimensioni,
zero aggiornamenti/eliminazioni nella riconciliazione precedente; nessuna nuova
indicizzazione dei dati utente. Codice applicativo SHA-256 identico prima/dopo.
Hash originale: `d125c7bf1e2c2b2d3d80639a38967b80fb9c7a09decf27d1098157ce0e602701`.

17 resolve, 51 chiamate modello del resolver, 335,8 secondi complessivi;
15 turni USER di test, esclusivamente SKIP numerati per rinviare i chiarimenti.
Non è stato fornito alcun valore fattuale manualmente. Zero resume, zero failure.
I 51 conteggiano il resolver, non i planner dei messaggi USER o gli embedding.
Il replay negativo descritto sotto è separato e aggiunge una chiamata modello.

## Blocco società di ingegneria: traccia reale finale

Tutti i nove slot: `entity=company`, `subject_relation=represented_organization`,
`subject_anchor=Società di Ingegneria`, `context_role=ORGANIZATION_PROFILE`,
`section_id=paragraph:75`, `condition_kind=subject_type`.
FORM reviewer: accepted=true / condition_complete=true.
Condizione «Società di Ingegneria» verificata e condivisa con SOURCE=true.
Prova nella visura Company **V**, chunk -1/idx0:
«MAPI INGEGNERIA S.R.L. SOCIETA DI INGEGNERIA CIVILE».
Non è una deduzione dal solo nome aziendale o dal FORM.

A75 è l'anchor fisico costruito dal backend; ogni riga individua il proprio slot:

```text
Legale rappresentante di Società di Ingegneria [[p75.s0]] con sede in Via/P.zza [[p75.s1]] Comune [[p75.s2]] CAP [[p75.s3]] Prov [[p75.s4]] P.IVA [[p75.s5]] Tel. [[p75.s6]] Fax[[p75.s7]] P.E.C. [[p75.s8]]
```

**V** = `visura-mapi-ingegneria-simulata.pdf`, chunk -1, idx0, global/company/source.
**G** = `generalita-mapi.md`, chunk -6, idx1, global/company/source.
Le query Q1–Q4 sono quelle effettivamente persistite, senza ricostruzioni o nuove ricerche.

| Candidate | Semantic property | Subject/entity | Form anchor | Applicability | Query SOURCE | Evidence letterale | Proposal/value | Status |
|---|---|---|---|---|---|---|---|---|
| `p75.s0` | `denominazione_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s0]]` | true / SOURCE | Q1 | V: DENOMINAZIONE Mapi Ingegneria S.r.l. | Mapi Ingegneria S.r.l. | RESOLVED |
| `p75.s1` | `indirizzo_sede_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s1]]` | true / SOURCE | Q2 | G: Sede legale di Mapi Ingegneria S.r.l.: Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia. | Via Giovanni Amendola 172/C | RESOLVED |
| `p75.s2` | `comune_sede_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s2]]` | true / SOURCE | Q3 | V: SEDE LEGALE E OPERATIVA Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | Bari | RESOLVED |
| `p75.s3` | `cap_sede_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s3]]` | true / SOURCE | Q3 | V: SEDE LEGALE E OPERATIVA Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | 70126 | RESOLVED |
| `p75.s4` | `provincia_sede_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s4]]` | true / SOURCE | Q3 | V: SEDE LEGALE E OPERATIVA Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | BA | RESOLVED |
| `p75.s5` | `partita_iva_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s5]]` | true / SOURCE | Q4 | V: CODICE FISCALE E PARTITA IVA IT01234567890 (dato simulato) | IT01234567890 | RESOLVED |
| `p75.s6` | `telefono_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s6]]` | true / SOURCE | Q4 | V: TELEFONO +39 080 000 2040 (recapito simulato) | +39 080 000 2040 | RESOLVED |
| `p75.s7` | `fax_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s7]]` | true / SOURCE | Q4 | nessuna evidence Fax: nessuna proposta | — | MISSING |
| `p75.s8` | `pec_societa_ingegneria` | company / represented_organization | A75 → `[[p75.s8]]` | true / SOURCE | Q4 | V: PEC mapi.ingegneria@pec.demo | mapi.ingegneria@pec.demo | RESOLVED |

Gli otto valori hanno proposal accepted=true, revisione SOURCE approvata e nessun
validation error finale. Per Fax: nessuna proposta, nessuna evidence sufficiente,
stato MISSING; non è un dato presente nella KB e perso dal sistema.

**Q1**

```text
anagrafica aziendale pec_societa_professionisti denominazione_societa_ingegneria
anagrafica aziendale denominazione_prestatore_servizi_art46
```

**Q2**

```text
anagrafica aziendale indirizzo_sede_societa_ingegneria comune_sede_societa_ingegneria
anagrafica aziendale cap_sede_societa_ingegneria provincia_sede_societa_ingegneria
```

**Q3**

```text
anagrafica aziendale comune_sede_societa_ingegneria cap_sede_societa_ingegneria
anagrafica aziendale provincia_sede_societa_ingegneria
```

**Q4**

```text
anagrafica aziendale partita_iva_societa_ingegneria telefono_societa_ingegneria
anagrafica aziendale fax_societa_ingegneria pec_societa_ingegneria
```

Q1 raggruppava anche altri candidate di organizzazioni nello stesso passo: le
etichette delle altre sezioni sono riportate esattamente, senza ripulire il log.
Il bucket e la verifica di soggetto/applicabilità restano specifici per field.
Q3 è la ricerca SOURCE del secondo tentativo sui tre componenti della sede.

| Candidate | Chunk recuperati nel proprio cluster | Chunk ammessi dopo riassociazione conservativa |
|---|---|---|
| `p75.s0` | 91, -1, -11, 90 | 91, -1, -11, 90, -7 |
| `p75.s1` | -2, -1, 91, -10 | -2, -1, 91, -10, -6 |
| `p75.s2` | -2, 91, -5, -1 | -2, 91, -5, -1 |
| `p75.s3` | -2, 91, -5, -1 | -2, 91, -5, -1 |
| `p75.s4` | -2, 91, -5, -1 | -2, 91, -5, -1 |
| `p75.s5` | 91, -7, -6, -1 | 91, -7, -6, -1 |
| `p75.s6` | 91, -7, -6, -1 | 91, -7, -6, -1 |
| `p75.s7` | 91, -7, -6, -1 | 91, -7, -6, -1 |
| `p75.s8` | 91, -7, -6, -1 | 91, -7, -6, -1 |

Gli ID negativi sono KB globali, quelli positivi sono fonti di progetto.
Un chunk recuperato non è automaticamente una prova: gli unici usati per gli
otto valori sono V e G. Scope, category, role, progetto, quote e valore sono
conservati nelle evidence persistite.

## Retry separati verificati nel caso reale

Al passo 13, v34, Comune/CAP/Provincia `p75.s2–s4` erano MISSING: il matcher aveva
scelto SOURCE fuori dai rispettivi bucket, correttamente respinte. Al passo 14,
v36, tutti e tre diventano RESOLVED/SOURCE con la visura ammessa nella nuova ricerca.
Per ciascuno: analysis_attempts=1, source_attempts 1→2, requisito/semantica conservati.
Gli altri sei slot del blocco, incluso Fax, hanno analysis=1/source=1 e
non sono stati riclassificati o forzati.
Nessun counter di fase supera due e nessun retry infinito.

## Servizi pregressi, sottoscrittore e prove negative

Tutti i **30 candidate della tabella t5** sono interpretati come PAST_SERVICE e
restano MISSING: committente/oggetto e data/importo/incarico/CIG non hanno evidence
di specifici servizi già eseguiti nella KB disponibile. Comune di Trapani,
oggetto/importo della procedura corrente e CIG vuoti non sono stati accettati.
In questa esecuzione il matcher non ha proposto offerte current→past o placeholder:
**0 proposte di quei tipi, 0 accettate, 0 da respingere nel benchmark principale**.
Non si contano come rejection i candidate per cui non è stata proposta una prova.

**Replay negativo separato sullo stesso codice finale**, copie in RAM, nessuna
scrittura a DB/sessioni: le due offerte realmente osservate nella vecchia prova
per `t5.r5.c2`, importo «€ 27.219,95 oltre CNPAIA ed IVA», chunk correnti 100 e 64,
sono ripassate attraverso la revisione SOURCE con DeepSeek reale.
L'estrazione indipendente restituisce `facts=[]`: **2 falsi match current→past
respinti**, field MISSING. Una chiamata modello, nessun nuovo retrieval.
I due vecchi `CIG: ____________`, `t5.r3.c4` e `t5.r4.c4`, ripassati attraverso
`apply_matches` senza chiamate modello diventano MISSING:
**2 placeholder respinti**, errore «Il valore contiene un segnaposto non compilato».
I conteggi del replay non vengono sommati alle metriche della sessione nuova.

Gli **otto slot del sottoscrittore p12.s0–s7** restano MISSING senza valori.
L'amministratore unico nella KB non è stato scelto come firmatario della pratica.
La PEC per comunicazioni `p107.s0` è il nono RESOLVED/SOURCE complessivo, con
`generalita-mapi.md`, chunk -6/idx1, «PEC aziendale simulata: mapi.ingegneria@pec.demo.».

## Checkpoint e chiarimenti residui

**9 RESOLVED/SOURCE prima del primo checkpoint**, dopo l'analisi disponibile.
Il primo gruppo, v44, contiene quattro condizioni ad alto impatto:

1. Studio Associato/Associazione professionale: 9 field.
2. Società di Professionisti: 9 field.
3. Professionista singolo: 7 field.
4. Prestatore di servizi ex art. 46, comma 1, lett. d): 3 field.

Gli otto dati del blocco ingegneria non vengono chiesti all'utente. Le alternative
non sono automaticamente escluse senza una prova di esclusività del FORM.
Il gruppo accetta SKIP numerati in un solo messaggio e passa al successivo.
Tutti i checkpoint hanno 1–4 slot; nessun candidate PENDING viene chiesto.
**15 checkpoint/15 turni SKIP, 52 slot complessivi, media 3,4667.**
I 52 chiarimenti rinviati corrispondono a 76 field; DEFERRED è una disposizione
sovrapposta a MISSING/AMBIGUOUS, non un ulteriore stato da sommare.
A fine prova non c'è un gruppo attivo: c'è deferred_summary / auto_continue=false.

Restano inoltre **30 PENDING non chiaribili come valori**: 24 condizioni non
ancorate alla sezione FORM, 5 revisioni semantiche indipendenti assenti e un
estratto strutturale non presente nel FORM. La guardia conservativa non li
trasforma in richieste di dati USER. È un limite residuo dell'interpretazione,
non una prova che tutti i candidate del modulo siano ormai gestiti correttamente.
Un candidate signature è in AMBIGUOUS; non è stato ignorato automaticamente.

Ulteriore limite osservato: per alcuni slot del ramo dei prestatori esteri il
reviewer approva una condizione abbreviata al riferimento normativo, mentre il
qualificatore «stabiliti in altri Stati membri» rimane nel contesto FORM.
In questa prova non è stata applicata alcuna SOURCE=true a quel ramo; la brevità
della condizione/questione va riesaminata prima di considerare completa la gestione
di tutti i qualificatori. Non è stata corretta durante il benchmark.

## Metriche e confronto

| Metrica | Baseline app, v75 | Intermedia otto dati | Finale dopo ricarica |
|---|---:|---:|---:|
| Candidate totali | 115 | 115 | 115 |
| Candidate tentati | 115 storici; UI 35 non-PENDING | 115 | 115 |
| RESOLVED SOURCE formali | 2, entrambi falsi CIG | 9 | 9 |
| Dati societari utili nel blocco | 0 | 8 | 8 |
| USER_PROVIDED | 0 | 0 | 0 |
| NOT_APPLICABLE | 0 | 0 | 0 |
| MISSING | 32 | 44 | 45 |
| AMBIGUOUS | 1 | 24 | 31 |
| PENDING | 80 | 38 | 30 |
| DEFERRED (sovrapposto agli stati) | 0 al primo checkpoint | 68 | 76 |
| Ignorati/non-field esclusi automaticamente | 0 | 0 | 0 |
| Checkpoint USER | primo noto, 4 voci | 15 | 15 |
| Turni USER di chiarimento | 0 al checkpoint | 15, SKIP | 15, SKIP |
| Chiarimenti medi/checkpoint | 4 nel primo | 3,3333 | 3,4667 |
| Chiarimenti rinviati | 4 attivi noti | 50 slot / 68 field | 52 slot / 76 field |
| Risolti prima del primo checkpoint | 2 falsi | 9 | 9 |
| Resolve / chiamate resolver | — | 24 / 72 | 17 / 51 |
| Tempo totale | — | 346,1 s | 335,8 s |

PRIMA: **0 dati societari utili, 2 falsi RESOLVED CIG placeholder**.
DOPO: **8 dati societari utili, 9 SOURCE complessivi validi, 0 placeholder accettati**.
`processed_candidates` conta chi ha speso un tentativo; non equivale alla quantità
UI 35 della baseline. La prova finale migliora il blocco richiesto, non dimostra
READY né assenza di falsi negativi in tutte le altre sezioni.

## Continuità, limiti e prossimo passo

La precedente sessione finale `6846e0553a74406f9c5937a9f46e9904` (archivio canonical)
resta conservata: 100 tentati, 0 SOURCE, 46 MISSING, 18 AMBIGUOUS, 51 PENDING,
0 checkpoint, failure 402 / Insufficient Balance sul matcher. La ricarica ha
permesso una prova nuova, senza riaprire/alterare quella sessione.
L'endpoint saldo precedente dava is_available=true ma la generazione era rifiutata;
non era una prova di disponibilità della richiesta.

Sono conservate anche le prove intermedie: iniziale con 10 RESOLVED formali e
applicabilità omessa/BA→Ba; failure per candidate extra; interruzione ambientale;
prova con un solo RESOLVED; prova `f9346167a6f54712a3fb14b25c5a6bec` con otto dati;
prova con soli tre dati del blocco per omissione della condizione.
Non sono confuse con l'ultima versione. Le vecchie metriche su DOCX Catanzaro o
Minervino non sono confronti percentuali equivalenti sullo stesso modulo.

Il criterio principale è verificato su questa prova reale. Il prossimo intervento
minimo, distinto dal benchmark concluso, è diagnosticare i 30 PENDING e conservare
nei rami condizionali tutti i qualificatori ancorati al FORM. Nessuna nuova modifica
implementata dopo la prova. Per completare il modulo servono risposte effettive su
applicabilità, firmatario, Fax e servizi documentati; gli SKIP non sono dati.
Non generare il DOCX finché il workflow non raggiunge READY o l'utente non richiede
esplicitamente una bozza incompleta secondo i controlli esistenti.

Acquisizioni ignorate da Git: `backend/data/compilation-audit/semantic-slots-20261008-ready/`
(state/revisions, raw 1–51, metrics, checkpoints, audit-summary, negative-replay,
negative-model-1, code-hashes-before/after, checks). Snapshot dei documenti prima
della ricarica in `checks/*.before`. Archivio canonical/altre prove preservati.
I replay negativi usano copie in RAM, non sessioni persistite modificate.
