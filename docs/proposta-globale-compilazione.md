# Proposta globale sperimentale — 10 ottobre 2026

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
