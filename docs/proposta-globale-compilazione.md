# Proposta globale sperimentale — 11 ottobre 2026

## Contratto corrente 8: dato proposto e applicabilità distinti

Correzione circoscritta del caso Trapani: il prompt V7 permetteva solo valori
con condizioni verificabili, ma operator=semantic rimane sempre unknown nel
backend. Un documento interamente condizionale poteva quindi produrre il JSON
vuoto pur avendo dati SOURCE pertinenti. Diagnosi: baseline invariata e due
ablation del prompt ancora vuote; una risposta documentale separata riconosce
i dati e i blocchi di rappresentanza/partecipazione, ma non è una proposta
compilabile. Nessuna prova che bastasse correggere una singola frase del prompt.

V8 aggiunge solo `disposition=conditional`: fact_id/property SOURCE, condizione
FORM reale non vuota e motivo. Riusa gli stessi gate di ancore, schema, valori,
provenance, alternative e persona/ruolo. Una condizione sconosciuta può differire
l'uso del dato senza cancellarne la proposta. False, condizioni malformate o
SOURCE invalide restano rifiutate; `value` con unknown resta rifiutato.

Audit: `validation=REVIEW_REQUIRED`, `value=null`, `fact_id=null`,
`written_value=null`, con `proposed_value`, `proposed_fact_id`, prove SOURCE e
condition_checks separati. I valori proposti sono conservati solo se passano
tutti gli altri controlli. Alternative non scelgono un valore e binding invalidi
non producono proposed_value. Nessun RESOLVED, renderer o integrazione nella V1.
Un JSON vuoto resta consentito e viene indicato come `assessment=empty_proposal`;
non si impone un numero minimo di valori o si inventano dati dal backend.

Budget invariati, una chiamata per documento, nessun retry/reviewer/batch nuovo.
V5/V6/V7 mantengono la validazione storica per replay. FORM non prova valori,
SOURCE non dimostra automaticamente rappresentanza/scelta dell'utente.
Applicabilità e entailment di proprietà/soggetto restano da verificare.

Protocollo prima delle acquisizioni: tre chiamate congelate su Trapani con lo
stesso DOCX/corpus della prova casuale, tre sulla fixture Labirinto V1 invariata,
nessun gold nel prompt. Misurare proposte condizionate separatamente dai valori
grounded e da RESOLVED; conservare tutte le risposte e i costi. Criterio minimo:
recuperare dati aziendali pertinenti nel ramo appropriato mantenendo i blocchi,
senza CF aziendale usato come CF personale o numero di un professionista usato
per altri. Nessuna modifica durante le serie; report in relazioni.md.

### Diagnosi successiva: modalità di ragionamento ed estratti FORM

Prima serie V8 senza ragionamento: Trapani ancora vuoto in 3/3; Labirinto
conserva proposte, comprese quelle condizionate. Le ablation del contesto slot
e del carattere simulato delle fonti non recuperano Trapani; un TASK compatto
produce associazioni troppo larghe e non viene adottato. Il solo contratto
conditional non basta. Tutte queste acquisizioni vengono conservate.

Stesso TASK completo V8 e input, `--thinking` low: otto dati aziendali nel ramo
corretto, sei grounding validi e due falsi negativi negli estratti FORM. Questi
ultimi dipendono da accento riscritto con apostrofo e underscore immediatamente
successivo a una label. Correzione FORM-only: normalizzazione deterministica
Unicode/case/spazi/virgolette, apostrofo terminale dopo vocale come accento e
underscore come delimitatore. Il testo originale viene ripristinato, senza
distanza fuzzy, riordino, prefissi numerici o cambio di paragrafo/ancora.
SOURCE e suoi controlli sui valori restano identici. Replay della stessa
risposta: otto proposte condizionate grounded, zero RESOLVED/scritture.

Secondo protocollo: tre Trapani e tre Labirinto sul codice congelato con
ragionamento attivo, sempre una chiamata ciascuno. Non si introducono fallback
o retry per attivarlo dopo una risposta vuota. Il flag è esplicito; impostazioni
live/UI e default del runner restano invariati. Misurare anche latenza e token
del ragionamento: non è un risparmio dimostrato né una decisione di produzione.
Esiti finali da leggere nel report, non dedurre successo dal solo replay.

La seconda serie thinking recupera 4/5/7 proposte condizionate Trapani; nei
primi due omette i componenti dell'indirizzo e nel terzo due citazioni hanno
solo lunghezza placeholder errata. Thinking da solo non garantisce copertura.
Rimossa l'ambiguità: la granularità di ogni fatto segue la destinazione FORM;
componenti separati richiedono fatti separati letterali, campo completo richiede
valore completo. Il matcher FORM normalizza anche la larghezza dei run di almeno
due underscore, preservando il run originale negli offset; non cambia underscore
singoli o interni a identificativi alfanumerici. SOURCE resta identico.

Ultimo protocollo: tre Trapani e un Labirinto con thinking low; una Trapani senza
thinking per misurare il limite residuo, senza fallback fra modalità. Codice
congelato, una chiamata per prova, gold invariato fuori dal prompt. Nessun minimo
di assegnazioni imposto e nessun dato inventato quando manca supporto.

## Contratto storico 7: legame letterale persona/ruolo

Passo autorizzato successivo alle alternative, sempre sperimentale e con una
sola chiamata. `bindings` è una mappa condivisa (massimo 128) con origine FORM,
`required_role`, `source_role` e 1–2 quote SOURCE. Un'assegnazione `value` che
referenzia un fatto `entity=person` deve indicare `binding_id`. Se manca, il
valore resta da rivedere. Se un binding è fornito per altre entità viene comunque
controllato. Review/alternative non scelgono un valore e restano invariate.

Il backend rilegge gli estratti e richiede ruoli letteralmente uguali dopo NFC,
casefold e spazi; niente sinonimi/cariche hardcoded. Il ruolo FORM può provenire
dalla riga/header esplicito, dall'ultimo paragrafo del corpo precedente il blocco
o dall'ultima sezione outline del candidate. Questo non estende le ancore del
requisito locale. La SOURCE deve attestare il soggetto con la forma conservativa
«ruolo: persona» all'inizio di una clausola del chunk reale, non soltanto in una
quote ritagliata dal modello. Ogni prova del valore deve appartenere a un chunk
che attesta quel ruolo per quella persona. Stessa persona, più proprietà:
binding condiviso, fatti atomici distinti. Nessun join fra chunk diversi.

Controllo non superato => REVIEW_REQUIRED senza valore scelto; rifiuti precedenti
restano rifiuti. Binding e prove sono conservati anche quando l'applicabilità
unknown blocca il campo. Il controllo non promuove mai a RESOLVED né autorizza
scritture. Il nome di un amministratore non diventa automaticamente firmatario.
Contratti V5/V6 conservati per replay con la loro validazione storica.

**Limiti espliciti:** `literal_match` è tracciabilità necessaria, non entailment
indipendente. Tipo dell'entità, proprietà e completezza del ruolo/condizioni
restano proposti dall'AI. Il gate non certifica che una proprietà nello stesso
chunk appartenga a quella persona, né interpreta negazioni/narrazioni generali.
Sinonimi, ruoli narrativi, titoli intermedi e prove su chunk diversi producono
falsi negativi conservativi. `semantic_review_required=true` rimane obbligatorio.
Applicabilità dei rami, chat, V1, RAG, parser e renderer non vengono modificati.

Protocollo prima delle chiamate: tre prove reali DeepSeek sullo stesso commit
congelato, fixture Labirinto V1 invariata e gold fuori dal prompt; nessun cambio
durante la serie, retry, USER o scrittura. Verificare cinque dati societari,
quattro dati direttore incluso 5739, alternative recapiti/polizze e mancata
promozione del firmatario senza prova. Il caso positivo di un ruolo esplicito
è coperto da test software; la fixture V1 non designa il firmatario.
Esiti, costo e limiti in relazioni.md e nel report dedicato dopo le acquisizioni.

Prima serie V7: firmatario improprio bloccato, ma 17/16/13 valori attesi contro
22/17/22 V6b. Direttore esteso nel FORM / breve nella SOURCE non coincidono;
ordine unito al numero in due run e numero omesso nel terzo. Seconda iterazione
limitata al prompt: conservare designazione FORM completa e distinguere il ruolo
funzionale letterale dal complemento organizzativo, senza sinonimi/sottostringhe
arbitrarie, e ribadire che i binding personali non limitano i fatti aziendali.
Validatore/schema invariati. Non è un controllo indipendente della completezza
del ruolo: il limite semantico resta dichiarato. Tre nuove prove congelate:
binding omessi 3/3, seconda serie conservata come regressione. Ultima iterazione
solo prompt: un esempio JSON generico del legame. Ruolo direttore literal_match
per quattro proprietà in 3/3, firmatario non provato bloccato, cinque dati
societari/alternative conservati. Copertura 17/17/17 contro 22/17/22 V6b,
checkbox tipologia omessi e applicabilità unknown: nessun progresso generale
di completezza dichiarato. [Tutte le prove e limiti](benchmark-persona-ruolo-2026-10-11.md).

## Contratto storico 6: alternative SOURCE esplicite

Passo sperimentale autorizzato l'11 ottobre, senza attivazione nella chat. Stesso
catalogo V3, corpus ammesso e singola chiamata. Il contratto 5 resta disponibile
per rileggere gli audit storici. Il nuovo schema aggiunge soltanto un terzo tipo
di proposta: `disposition=review`, `kind=data`, `property`, `review_kind`
(`ambiguous`/`conflicting`), `alternative_fact_ids` (2–4), motivo, FORM e condizioni.
Non contiene `value`, `fact_id` scelto o `choice`.

Ogni alternativa è un fatto SOURCE atomico con quote e riferimenti propri. Il
backend richiede stesso soggetto/entity/aspect/property dichiarati, valori
distinti dopo normalizzazione conservativa, grounding di ogni valore e validità
sintattica per il candidate. Ancore locali, ID e condizioni restano controllati
dai gate esistenti. Errori locali non eliminano le proposte indipendenti.
Review grounded => `REVIEW_REQUIRED`, `value=null`, `written_value=null`;
conserva separatamente tutte le prove e gli eventuali condition_checks unknown.

Se una proposta value ha già altri fatti referenziati e grounded dello stesso
soggetto/dimensione/proprietà con valori differenti, il backend blocca la scelta
e conserva le alternative. Non calcola CONFLICTING da stringhe diverse: alias,
periodi o significati potrebbero differire. Un'alternativa invalida non ripristina
silenziosamente il valore scelto. I fatti orfani restano esclusi come nel V5.

**Limiti:** identità e property sono ancora metadati proposti dall'AI, non
entailment verificato. Il gate non scopre una seconda SOURCE omessa dall'output
né certifica che tutte le alternative siano state individuate. Review kind è
un giudizio da verificare, non uno stato persistito. Nessuna risoluzione automatica
delle priorità temporali o delle checkbox discordanti. Soggetto/applicabilità
restano aperti: grounding non diventa RESOLVED. Nessuna modifica di V1, parser,
renderer, RAG, UI, originali o sessioni; nessuna migrazione/reindicizzazione.

Budget invariati: massimo 400 proposte, 128 fatti/condizioni, 96 SOURCE/100.000
caratteri, 350.000 input, 49.152 token output e 300 s nel runner. Le alternative
consumano lo stesso budget di fatti; nessun reviewer, retry o chiamata per campo.
La misura usa tre chiamate reali per commit congelato sulla fixture Labirinto V1,
gold fuori dal prompt; registro, esiti anche negativi e acquisizioni in
[relazioni.md](../relazioni.md). Non è un benchmark E2E della V1.

Esito delle due iterazioni: alternative separate in **6/6** acquisizioni, cinque
dati societari sempre corretti, ma soggetto/ruolo e applicabilità ancora aperti.
Ultima serie 22/17/22 valori attesi grezzi, zero RESOLVED/scritture; +14,67% token
totali medi vs V3. [Report completo](benchmark-alternative-source-2026-10-11.md).

## Contratto storico 5: proposte sparse, inventario nel backend

Autorizzata la semplificazione dopo i sei rifiuti del contratto compatto.
Una sola chiamata riceve ancora l'intero catalogo e le SOURCE ammesse. Output:
`version=5`, `conditions`, `fields`, `facts`, opzionale `uncertain_paragraph_ids`.
Niente `deferred`, ricevuta di lettura o partizione da ripetere. L'inventario
autoritativo deriva dall'originale: tutte le posizioni omesse restano
REVIEW_REQUIRED/non valutate, senza valore, requisito o obbligatorietà inventati.

Le condizioni conservano origine FORM e prove; `scope` usa `{kind,id}` con
kind candidate/paragraph/table/section. Il backend verifica che l'oggetto
esista realmente e deriva gli ID coinvolti, incluse tabelle annidate e outline
Word. Un titolo senza outline non diventa una sezione strutturale inventata.
Uno scope di paragrafo copre solo il contesto fisico locale, non automaticamente
tutti i paragrafi successivi. L'associazione semantica non locale resta unknown.

Il JSON originale non viene riscritto. La validazione locale riusa i gate
precedenti: ID inventati in `rejected_assignments`; assegnazioni invalide
rifiutate singolarmente; fatti/condizioni invalidi bloccano le dipendenze
riconoscibili. Errori di scope non eliminano una clausola dal suo contesto
locale. Fatti orfani elencati in `unused_fact_ids` e inutilizzati. Un JSON
troncato, chiavi duplicate, envelope o budget invalidi restano rifiuti globali.

Budget: 400 posizioni/assegnazioni, 128 fatti/condizioni, 96 SOURCE,
100.000 caratteri SOURCE, 350.000 input, 49.152 token output; nessun retry,
reviewer o chiamata per field. Incertezza FORM locale, proprietà diverse,
assenza SOURCE e condizioni false/ignote impediscono ancora il valore.
Grounding non è accettazione semantica: **zero RESOLVED, zero scritture**.
V1/chat/RAG/parser/renderer invariati. I contratti storici restano per gli audit.

Le prime due prove (`7190d2d`) hanno prodotto 256/165 record contro il precedente
tetto di 128: entrambe rifiutate; molti value senza fact_id. Dopo questa coppia
conclusa, separati gli schemi value/NA: fact_id e property obbligatori non null
per value; limite record pari al catalogo, così 129 record invalidi non eliminano
un'assegnazione valida. Nessuna modifica retroattiva dei risultati acquisiti.
Nuova coppia misurata a codice congelato, senza cambiare corpus/budget token.

**Esito finale:** due risposte validate per assegnazione sul commit `46128f5`:
9/8 grounded, 40/75 rifiuti locali e 258/224 posizioni non valutate. 20,26/31,00 s,
76.611/81.160 token. Cinque dati societari corretti, ma errori semantici di
sottoscrittore/carica/sede operativa restano: nessuna attivazione nella chat.
[Report completo e acquisizioni](benchmark-proposte-sparse-2026-10-11.md).
Verifiche finali: 188 mirati/1.594 backend, Ruff, help e diff; frontend invariato.

**Esito dell'esperimento compatto:** tutte le sei risposte rifiutate, nessuna
attivazione nella chat. Output finale più breve, ma ID/applicabilità ancora
incoerenti. [Report reale completo](benchmark-proposta-compatta-2026-10-10.md).

## Contratto storico 4: origine canonica delle condizioni

Le prime quattro prove del contratto 3 sono state rifiutate: espansione inutile
SOURCE, fields review oltre budget, poi inventario duplicato/incoerente. Non
vengono riparate o accettate parzialmente. Sono riproducibili con il codice
congelato allegato ai rispettivi audit, non tramite un nuovo percorso operativo.

La versione 4 toglieva una responsabilità ridondante al modello: l'origine della
condizione compare soltanto in `conditions[id].form.paragraph_id` e quote.
Il backend deriva la mappa inversa paragrafo-condizioni e ne controlla le quote,
poi collega clausole locali e scope proposti agli ID strutturali già noti.
`reviewed_paragraph_ids` è la ricevuta esatta dei paragrafi forniti;
`uncertain_paragraph_ids` è un sottoinsieme esplicito. Queste liste non provano
che ogni condizione sia stata capita: completezza semantica ancora non verificata.
L'assenza di una condizione resta insufficiente a promuovere un valore.

Invariati i limiti del contratto compatto: 128 fatti solo referenziati, 128
condizioni, 128 fields soltanto value/NA, 400 candidate inclusi deferred, 2.048
paragrafi. Grounding, proprietà, SOURCE/FORM e gate di applicabilità invariati.
Non si ammettono quote da paragrafi sbagliati o nuove destinazioni. Nessun
RESOLVED/scrittura/adapter. Le versioni storiche 1/2 restano leggibili per i
precedenti audit; il contratto 3 rifiutato usa il codice congelato delle prove.

## Terzo contratto storico: inventario e assegnazioni compatte

Passo sperimentale autorizzato, **non attivo nella chat**. Una sola chiamata
riceve ancora tutto il catalogo originale e il corpus SOURCE piccolo completo.
Le versioni precedenti restano leggibili soltanto per gli audit storici.

- `condition_scan`: un elemento per ogni paragrafo FORM non vuoto, inclusi
  titoli e istruzioni. Lista di condizioni lì espresse, `[]` se non proposte,
  `null` se incerto. Copertura esatta verificata dal backend, massimo 2.048
  paragrafi; oltre budget errore, nessun troncamento. Non è un detector basato
  su parole del bando e non prova la completezza semantica dell'inventario.
- `conditions.applies_to`: mappa proposta dal modello fra clausole e candidate,
  con estratto FORM. Il backend collega anche tutte le condizioni locali
  inventariate, così un'assegnazione non può ometterne il riferimento. Scope
  non locale ancora da verificare: non autorizza automaticamente valori o NA.
- `facts`: proprietà SOURCE distinte, valori atomici e citazioni condivise.
  `fields.property` deve coincidere con la proprietà del fatto referenziato:
  un generico profilo non può essere usato come nome e numero. Il modello può
  ancora classificare male le proprietà; questa identità non è una prova
  semantica indipendente. Gli indicatori di indisponibilità/placeholder non
  possono diventare fatti utilizzabili, neppure nelle condizioni.
- `fields`: massimo 128 assegnazioni value/NA; nessun record dettagliato
  missing/review/ignore. `deferred`: soli ID delle
  altre posizioni, fino a 400 totali. Unione esatta e senza duplicati, nessun
  default implicito. Deferred è **ancora da interpretare**, non missing né
  decorativo e non una nuova domanda all'utente. Riduce l'output ripetitivo;
  non equivale a una compilazione completata di tutti i candidate.

Invariati i gate SOURCE/FORM, le quote, i confronti conservativi, i limiti
corpus/input/output e la singola chiamata senza retry. Inventario locale
incerto impedisce value/missing/NA. Nessun valore scrivibile e nessun RESOLVED;
chat, sessioni V1, parser e renderer invariati. Nessuna migrazione/reindicizzazione.
Prima della prova reale: regressioni generiche su copertura, condizioni omesse,
proprietà diverse, fatto composito, indisponibilità, scope e provenance.

## Secondo contratto: fatti e condizioni condivisi

**Esito reale:** due risposte omettono tutte le condizioni; la prova thinking
low viene troncata. Non attivare nella chat e non assumere un miglioramento
dal nuovo schema. [Misure e diagnosi](benchmark-condizioni-globali-2026-10-10.md).

Il nuovo input richiede `version=2`, `facts`, `conditions`, `fields`. Una sola
chiamata riceve ancora tutto il FORM e il corpus SOURCE piccolo completo.
La versione precedente resta leggibile per riprodurre gli audit archiviati;
non è un secondo percorso operativo né una migrazione delle sessioni.

- `facts`: soggetto, entity, dimensione (`aspect`), proprietà, valore letterale
  e citazioni SOURCE conservate una volta. Un field referenzia `fact_id`;
  non può ripetere un valore/evidence alternativi per eludere il controllo.
- `conditions`: estratto FORM, dimensione, operatore e riferimenti ai fatti.
  `same`/`different` richiedono due fatti distinti dello stesso soggetto/entity,
  stessa dimensione e proprietà distinte. Tipologia, partecipazione e poteri
  sono dimensioni separate. Non si possono confrontare per escludere un ramo.
- Valori identici dopo sola normalizzazione Unicode NFC/whitespace permettono
  di calcolare `same=true` / `different=false`. Testi diversi restano unknown:
  abbreviazioni o grafie diverse non provano valori reali differenti.
  La dimensione `other` e gli operatori `semantic` restano unknown.
- Ogni field elenca esplicitamente le proprie condizioni (`[]` se non ne
  propone). Condizione falsa: niente value/missing; unknown: solo review;
  non applicabile: necessaria almeno una condizione calcolabile falsa.
  Un vincolo fuori dalla riga/intestazione locale non può autorizzare un valore
  o escludere la destinazione: la sua associazione di sezione resta da verificare.
- Le checkbox possono proporre `choice` booleano con riferimento a un fatto;
  restano non scrivibili. Firme e dichiarazioni conservano le protezioni esistenti.

Budget aggiuntivi: massimo **128 fatti**, **128 condizioni**, **8 riferimenti a
condizioni per field**; invariati 400 candidate, 96 chunk/100.000 caratteri
SOURCE, 350.000 caratteri input, 49.152 token output e timeout 300 s. Nessun
reviewer, retry o chiamata per field. Il validator riusa i controlli letterali
precedenti; gli errori dei fatti/condizioni isolano le assegnazioni dipendenti.
Tutte le prove restano nell'audit, incluse quote effettive, ID citato/ripristinato,
hash, scope e categoria. La copertura dei candidate è ancora esatta.

Il runner offre `--thinking` per un confronto isolato con ragionamento DeepSeek
`low` (modalità già impiegata dalla mappa V1). Default disabilitato, invariati
schema/input/validator, budget e numero di chiamate. I token di ragionamento
possono incidere sul limite di output e sulla latenza; salvare il response HTTP
completo e usage, non considerare questo confronto una scelta di produzione.

**Limite intenzionale:** questi risultati sono subordinati alla correttezza
semantica della mappa proposta. Non provano che il modello abbia individuato
tutte le condizioni, classificato bene ogni dimensione o scelto l'operatore
corrispondente al FORM. L'assenza di una condizione proposta non dimostra
incondizionalità. Perciò restano `semantic_review_required=true`, zero RESOLVED
e zero scritture. La V1, chat, parser, renderer e RAG non cambiano.

Il resto della pagina descrive il primo contratto e le misure storiche.

Passo successivo al catalogo FORM condiviso. Una sola chiamata reale DeepSeek
riceve l'intero modulo, un piccolo corpus documentale SOURCE e lo schema di
output. Nessuna mappa/review/ricerca per gruppi né retry AI in questo percorso.
La chat e la CompilationSession continuano a usare la V1: non sono modificate.

## Input e output

`compilation_global.py` prepara `form`, `sources`, `user_values=[]` e copertura.
Ogni SOURCE conserva chunk/file ID, indice, nome, ruolo, progetto, scope e
categoria Company/General KB. Il runner legge una copia temporanea SQLite,
riusa filtro e rilettura del repository e include tutte le fonti documentali
caricate nel progetto e Company/General KB. Moduli, altri progetti e artefatti
(anche fatti USER) restano esclusi da questa prima prova SOURCE-only.

Il modello restituisce `fields`, indicizzato dagli ID strutturali esistenti.
Ogni elemento contiene label, soggetto, tipo, disposition, valore eventuale,
estratto FORM locale, massimo due quote SOURCE e ragione breve. Le disposition
sono `value`, `missing`, `review`, `not_applicable`, `ignore`. Non sono stati
persistiti della CompilationSession. Non vengono accettati contatori del modello.

Budget: massimo 400 candidate, 96 chunk SOURCE/100.000 caratteri SOURCE,
350.000 caratteri di input, 49.152 token massimi di output, 500.000 caratteri
di risposta. Corpus oltre budget: errore esplicito, nessuna selezione/troncamento
silenzioso. Un'unica chiamata con thinking disattivato, timeout totale default
300 secondi (configurabile 1–600), nessun retry automatico.

## Cosa prova il validator

- Coverage esatta, ID validi e univoci; JSON duplicato/troncato non utilizzabile.
- FORM quote letterale nel paragrafo del candidate o riga/intestazione fisica
  della sua tabella; una label di una tabella diversa non è ammessa.
- SOURCE nel corpus consentito, quote verificabile, valore testuale completo
  nella quote, controlli numerici/email e protezioni del validator DOCX esistente.
- Booleani tipizzati per checkbox; firme protette; nessun valore per missing,
  review, ignore o non applicabile. Non applicabilità proposta richiede SOURCE.
- Errore locale: candidate rifiutato, altre proposte conservate per l'audit.

Dopo la prima prova reale, aggiunti riferimenti espliciti ai paragrafi locali
non vuoti (`anchor_paragraph_ids`), senza duplicare testo o dedurre etichette.
Quote vuota consentita esclusivamente per `ignore` + `decorative`, senza valore
né SOURCE: un campo informativo continua a richiedere grounding. Apostrofi e
virgolette tipografiche FORM possono essere normalizzati deterministicamente;
la quote originale viene conservata, nessun fuzzy matching.

Se il modello cita un chunk errato, la quote può essere ricondotta a un altro
chunk **dello stesso file già fornito** solo quando compare integralmente e
univocamente. File diverso, quote ambigua/riscritta o corpus esterno: rifiuto.
L'audit conserva sia `cited_chunk_id` sia chunk effettivo e `citation_rebound`.
Questa correzione di riferimento non approva significato/proprietà/soggetto.
Il prompt distingue meglio condizione falsa/ignota e dati comuni/partecipazione;
non aggiunge regole per il modulo demo o per aziende/candidate particolari.

**GROUNDED_PROPOSAL non significa RESOLVED.** I controlli letterali non provano
che proprietà, soggetto, ruolo e ramo siano corretti, né che una condizione
discenda semanticamente da una SOURCE. Tutte le proposte conservano
`semantic_review_required=true`, `written_value=null`; resolved e scritture
sono zero. Non viene fabbricato il verdetto indipendente della V1. La valutazione
semantica umana annotata del benchmark resta distinta dai controlli software.
Non c'è adapter di sessione/export né scrittura checkbox in questo passo.

## Ripetizione della prova reale

Da `backend`, con il profilo DeepSeek già configurato:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_global.py \
  --project minervino-di-lecce-elenco-sia --form-id 153 \
  --profile-project prova \
  --output data/compilation-audit/global-NUOVA-PROVA
```

Usare una directory nuova. Non modifica profili, sessioni, DB live o originale;
scrive soltanto l'audit e una copia dell'originale. Salva input, schema, richiesta,
risposta HTTP (anche se troncata), testo grezzo, usage, durata, validazione locale,
codice congelato e manifest. Credenziali/header non esportati. Il limite finestra
salvato nel profilo è registrato separatamente dalle capacità del provider.

La modalità JSON e il budget output seguono la
[documentazione ufficiale DeepSeek](https://api-docs.deepseek.com/guides/json_mode/).
Il [contratto API](https://api-docs.deepseek.com/api/create-chat-completion/)
documenta i limiti del servizio: non confonderli con i limiti conservativi della
prova. Nessuna stima di token ottenuta dividendo i caratteri: si usa solo usage.

Per confrontare tempi/token con la V1 usare lo stesso hash DOCX e lo stesso
corpus; distinguere sempre analisi globale e primi 12 candidate della baseline.
Le differenze di cache e variabilità del servizio limitano un singolo confronto.

## Punto successivo

Misurare la proposta reale e annotare almeno i cinque campi SOURCE già dimostrati,
rami condizionali, direttore tecnico/albo e falsi positivi. Decidere poi il
contratto di accettazione semantica locale per l'adapter: il passaggio alla chat
richiede questa garanzia, non soltanto JSON valido o token ridotti.
