# Catalogo unico FORM — prima milestone, 10 ottobre 2026

Implementato il primo passo verso la proposta globale a chiamata unica: una
rappresentazione deterministica condivisa del documento, senza copie del
contesto per ogni candidate. Non è ancora il nuovo resolver: la chat continua
a usare la V1 e non sono state eliminate le sue chiamate generative.

## Contratto e riuso

`backend/app/compilation_catalog.py` produce un JSON con:

- versione, ruolo FORM e hash dell'originale;
- blocchi in ordine fisico, con paragrafi identificati e testo presente una volta;
- struttura delle tabelle, riferimenti ai paragrafi delle celle fisiche,
  celle unite e tabelle annidate;
- candidate testuali con gli ID esistenti, contesto e intervallo del segnaposto;
- checkbox native con ID `pN.cbM`, posizione nel paragrafo, formato e stato
  originale. Lo stato originale non è un valore verificato né provenance SOURCE;
- gerarchia dei titoli esplicitamente codificata negli outline Word, anche
  tramite stili ereditati. I titoli non strutturati e le condizioni restano
  testo letterale completo, da interpretare nella futura proposta unica;
- testo di intestazioni, piè di pagina, note a piè di pagina e note finali come
  contesto FORM in sola lettura, con conteggio degli eventuali controlli esterni.
  I richiami alle note conservano parte, ID e posizione; i tabulatori di
  impaginazione non sono confusi con tabulazioni o a capo del testo.

Non contiene valori proposti, fatti aziendali, applicabilità o stati di sessione.
Nessuna regola cerca categorie societarie, etichette, nomi o ID del modulo demo.
La stessa label in sezioni diverse mantiene contesti e posizioni distinti.
Le firme già riconosciute restano esplicitamente protette.

La proiezione `document_blocks`, prima contenuta in `compilation_document_plan.py`,
è stata spostata nel catalogo. La mappa V1 la riusa con lo stesso contratto:
ID, confini, testo e candidate non cambiano. Nessun reviewer è bypassato.
Il parser accetta l'opzione `require_candidates=False` per l'ispezione in sola
lettura di documenti senza celle/segnaposti, per esempio con sole checkbox.
Il default e l'insieme scrivibile del renderer restano invariati.

## Checkbox e limiti espliciti

Riconosciuti i controlli legacy `w:checkBox` e i content control `w14:checkbox`,
inline o a blocco. Il glifo visibile del content control non è un secondo campo.
La relazione riga/cella permette di leggere l'etichetta anche se è in un'altra
cella. Due caselle nello stesso paragrafo hanno ID e offset distinti.

**Scrittura delle checkbox non implementata in questa milestone**:
`checkbox_write_supported=false`. Non entrano nei campi della sessione V1
e non viene modificato il renderer. Immagini, simboli e quadrati testuali senza
controllo nativo non sono trasformati automaticamente in candidate checkbox.
Il catalogo non prova gruppi esclusivi o applicabilità: le istruzioni FORM
devono sostenere queste decisioni nel prossimo contratto di output.

Budget esplicito: massimo 400 candidate complessivi testo/checkbox e 200.000
caratteri del JSON compatto. Un superamento fallisce senza troncamenti silenziosi;
il limite non è una dichiarazione sulla finestra di contesto di un provider.
Le posizioni scrivibili riguardano il corpo; le parti accessorie sono sola lettura.
Non viene affermato supporto completo a immagini, layout visuali o ogni controllo Word.

## Ripetere l'esportazione

Dalla directory `backend`, senza configurare provider o modificare database:

```bash
PYTHONPATH=. uv run --locked python scripts/export_compilation_catalog.py \
  ../demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx \
  --output-dir data/compilation-audit/catalog-NUOVA-PROVA/catanzaro --compare-v1
```

La directory finale deve essere nuova. Salva `catalog.json` e `metrics.json`;
verifica nuovamente l'hash dell'originale. Zero chiamate AI, retrieval o accessi
al database. `--compare-v1` misura i contesti FORM ripetuti di tutti i candidate
V1, non il payload di una singola richiesta reale. Non vengono stimati token.

## Misure strutturali realmente eseguite

| Fixture | Testuali | Checkbox | Caratteri catalogo | Contesti FORM ripetuti V1 |
|---|---:|---:|---:|---:|
| Catanzaro | 279 | 28 | 124.175 | 418.910 |
| Minervino | 254 | 13 | 67.594 | 1.018.482 |

Il catalogo include più contesto e controlli; la colonna V1 aggrega il materiale
di tutti i campi. È un confronto di rappresentazioni, non una misura di velocità,
costo o qualità semantica di DeepSeek/Gemma. Gli originali fixture sono invariati;
il Catanzaro versionato ha hash diverso dall'upload locale del benchmark di latenza.

Dati versionabili in [riepilogo JSON](benchmarks/2026-10-10-compilation-catalog.json).
Cataloghi grezzi e log permanenti in
`backend/data/compilation-audit/catalog-20261010/`, esclusi da Git.

Verifiche della versione finale: **32 test mirati**, **1.428 test backend
completi**, Ruff, CLI `--help`, integrità di tutti i riferimenti e originali,
diff/whitespace. Test software con provider simulati e database/storage
temporanei; cataloghi esportati senza alcun provider. Frontend non modificato.

## Prossimo passo

Definire e verificare il contratto di output della singola proposta globale:
candidate/ramo → applicabilità → valore → prova SOURCE o USER. Poi adapter della
sessione, scrittura mirata delle checkbox e benchmark congelato prima di rimuovere
la catena precedente. Nessuna autodichiarazione del modello sostituisce un controllo
di soggetto/ruolo/condizione, e una casella vuota non prova una risposta negativa.
