# Motivi dei campi lasciati vuoti: V12

Baseline `fceedfc`, branch prune-backend. Feature backend `5e50021`.
Richiesta: sapere perché una posizione resta vuota, distinguendo omissione,
valutazione esplicita e motivo rifiutato. Nessun nuovo RAG, parser, renderer,
workflow UI o loop per candidate.

## Causa concreta e scelta

Il prompt V11 richiedeva esplicitamente di omettere fields senza SOURCE e
«non serve spiegare ogni vuoto». Il narratore riceveva unassigned_count come
unassessed_positions: un'omissione poteva diventare la frase non verificabile
«non ancora valutato». Non c'era una spiegazione archiviata per quei vuoti.

V12 conserva proposte sparse e separa un resoconto delle altre posizioni.
Riduce la ripetizione della stessa motivazione raggruppando ID dello stesso
contesto. Il costo è output più lungo e un controllo aggiuntivo locale;
non una nuova chiamata AI o un nuovo giro di retrieval.

Esempio di struttura, dati generici:

```json
{
  "coverage": [{
    "candidate_ids": ["p10.s0", "p10.s1"],
    "outcome": "source_not_found",
    "reason": "Non ho trovato i riferimenti richiesti per questo soggetto",
    "form": {"paragraph_id": "paragraph:10", "quote": "Riferimenti professionali"},
    "conditions": []
  }]
}
```

Gli ID devono essere reali. Il resoconto non contiene valori o prove SOURCE.
Gli esiti MODEL ammessi sono source_not_found, condition_unknown, not_applicable,
not_a_field, manual_input, unassessed. Form obbligatorio salvo unassessed.
Una frase «non ho trovato» non dimostra che il dato non esista o che il modello
abbia cercato in modo esaustivo; rimane una spiegazione proposta dal modello.

## Backend e provenance

UnfilledExplanation/CoverageAwareProposal sono nel contratto; compilazione_coverage
valida il resoconto dopo gli attuali gate delle proposte. Ogni candidate ha:

| Stato di copertura | Significato |
|---|---|
| PROPOSED | Record fields presente e non respinto; include proposte condizionate/alternative/NA, non equivale a valore risolto |
| CLARIFICATION | Domanda locale FORM già validata |
| REJECTED_PROPOSAL | Proposta/domanda rifiutata con diagnostica |
| EXPLAINED_UNFILLED | Motivo MODEL ancorato al FORM e compatibile con i controlli locali |
| REJECTED_EXPLANATION | Motivo restituito ma rifiutato; raw e errori restano consultabili |
| UNASSESSED | Il modello dichiara di non aver determinato l'esito |
| UNEXPLAINED | Nessun record identificabile per quella posizione |

Sono metadati della prima analisi, non nuovi stati della CompilationSession.
Il modello non può rimuovere una proposta SOURCE tramite coverage. Sovrapposizioni
fra motivi disabilitano solo le posizioni coinvolte; nessun last-wins. ID ignoti,
quote inventate, record fuori schema e motivazioni fuori contesto sono registrati.
Budget/errori del resoconto non cancellano i valori SOURCE indipendenti.

Contesti condivisi ammessi per spiegazioni: un gruppo di almeno due candidate
della stessa tabella, con paragrafi introduttivi già nel catalogo; una condizione
FORM validata il cui scope contiene il candidate; l'istruzione di un choice_group
validato che contiene l'opzione. Singoli field non ottengono il contesto dell'intera
tabella aggiungendo ID inventati. Raggruppamenti fra tabelle distinte non allargano
il contesto. Queste regole **non modificano i gate o contesti dei valori SOURCE**.

condition_unknown/not_applicable richiedono riferimenti locali validi e risultato
unknown/false effettivo. Un predicate semantic resta unknown. FORM e USER claim
non diventano SOURCE; nessun esito del resoconto produce un valore, un’esenzione
scrivibile o automaticamente una domanda. semantic_review_required rimane vero.

coverage_summary separa tutti i contatori: explicit_decisions_complete misura
solo presenza di un esito dichiarato, coverage_checks_passed anche i controlli
formali, semantic_completeness_verified è sempre false. Non sono percentuali
di accuratezza, prova di lettura o stato live dei valori dopo risposte USER.
L'audit originale resta immutato; dialogo/answers/user_values e report descrivono
gli aggiornamenti e quanto è stato effettivamente scritto.

La sintesi iniziale riceve fino a24 gruppi umani di motivi, senza ID. Il backend
aggiunge un avviso quando mancano esiti o i motivi sono respinti: non dipende
dal modello per segnalare incompletamente la propria risposta. Le categorie
sono distinte anche se coesistono. I follow-up restano ricevute brevi del turno,
senza ripetere inventario/avvisi. Nessun redesign UI o contratto frontend consumato
dall'interfaccia; nuova chiave additiva coverage_summary nella sessione.

API esistenti: GET sessione per il riepilogo, GET global-report per tutti i motivi.
Il report della bozza contiene già global_audit, quindi conserva il resoconto.
Generazione sempre esplicita dall'originale con gate SOURCE/USER preesistenti.

## Prove reali, protocollo congelato

DeepSeek Flash reale, thinking low, configurazione corrente del progetto.
Due baseline V11 prima delle modifiche: Labirinto V1 e modulo Minervino corrente.
Nuove serie:2 prove per caso prima dei miglioramenti di contesto, poi altre2.
Le nuove serie riusano esattamente originali/fonti della baseline:55/267 candidate,
7/51 chunk, nessun adattamento dei gold agli output. Gold valutato dopo la chiamata,
mai nel prompt. Codice applicativo congelato durante ciascuna serie.
Nessuna scrittura di sessioni/database live o DOCX generati; solo audit.

| Caso | Proposte valide di qualsiasi disposition | Domande | Motivi ancorati | Motivi respinti | Vere omissioni |
|---|---:|---:|---:|---:|---:|
| Labirinto baseline V11 | 25 | 2 | non richiesti | non richiesti | 28 |
| Labirinto finale1 V12 | 25 | 2 | 28 | 0 | 0 |
| Labirinto finale2 V12 | 25 | 2 | 28 | 0 | 0 |
| Minervino baseline V11 | 19 | 2 | non richiesti | non richiesti | 244 |
| Minervino finale1 V12 | 19 | 0 | 159 | 88 | 0 |
| Minervino finale2 V12 | 17 | 2 | 135 | 105 | 7 |

Minervino ha anche1 proposta rifiutata in ciascuna prova finale; nella baseline
le proposte rifiutate sono2. La colonna proposte Labirinto include NA/review e
conditional, **non25 valori RESOLVED**. Il conteggio di omissioni della baseline
è unassigned_count, che sottrae le domande valide.

La prima serie negativa è conservata: Labirinto respinge9/10 spiegazioni per
contesti troppo locali; Minervino139/31 motivi accettati e105/224 ancora senza
spiegazione validata, una prova con sole5 proposte SOURCE. Non attribuire
automaticamente questo outlier al nuovo contratto, ma non nasconderlo.
Un replay senza provider degli stessi raw documenta che i controlli aggiornati
non cambiano le proposte/prove SOURCE, soltanto gli esiti del resoconto.

Il secondo passo usa relazioni FORM esistenti e segnala separatamente i motivi
rifiutati. Quote oltre500 caratteri restano respinte: istruzione di citare brevi
span, nessun aumento permissivo del limite. Unità di lettura includono checkbox
e riferimenti dei contesti condivisi, nessuna classificazione semantica backend.

Benchmark fisso: valori letterali/prove SOURCE del gold corrispondono a16 target
nella baseline,22 e16 nelle due prove finali; nessun valore/NA inatteso secondo
quel controllo limitato. Non equivale ad accuratezza semantica o completamento
del modulo. Conditional e applicability rimangono gate autonomi.

Minervino finale: conservati operatore, contatti, PIVA, dati societari e i quattro
riferimenti professionali (nome, qualifica, Ordine,8421). Mancano ancora motivazioni
correttamente ancorate per più gruppi di soci, associati, RTP/consorzi e scelte.
I7 ID omessi nella seconda prova sono controlli nativi di scelta del ruolo:
p20.cb0,p21.cb0,p35.cb0,p39.cb0,p54.cb0,p61.cb0,p64.cb0. Non creati o risolti dal backend.

## Costi e tempi acquisiti

Restano una chiamata di analisi e una di sintesi per una nuova compilazione;
router/guard del dialogo successivo invariati. Il benchmark totalizza10 analisi
e8 sintesi per tutti gli esperimenti,756.341+55.068 token acquisiti. Nessun costo
monetario stimato da listini non verificati, nessun risparmio dimostrato.

Tempi AI analisi: baseline84,43s Labirinto e111,81s Minervino; finali118,11/115,43s
Labirinto e101,91/158,59s Minervino. Output più ricco e ragionamento variabile;
non attribuire causalmente ogni differenza alla modifica con così poche prove.
Non sono tempi della chat end-to-end. Nessun retry automatico o chiamata per field.

Limiti invariati:400 candidate,400 gruppi,quote500 caratteri,motivi300,
output49.152 token,input350.000 caratteri,corpus piccolo completo bounded.
Nella prima analisi non ci sono valori USER e nessun gold entra nel prompt.

## Verifiche e compatibilità

Software con provider simulati, DB/storage temporanei e FTS5/Qdrant dove applicabile:
**277 mirati /19,91s**, **2219 backend /162,60s**, Ruff backend/runner,diff check.
360 mutazioni con seed del nuovo resoconto, oltre ai fuzz preesistenti della suite.
API persistente e download report testati; una spiegazione non autorizza export
e il writer lascia vuote le sue posizioni. Form-only, isolation, USER e proposte
SOURCE restano protetti. Frontend/browser non ripetuti, frontend invariato.

Un fallimento intermedio della suite completa derivava dal provider simulato
del runner che restituiva ancora V11: corretto solo quel test del contratto
richiesto. V11 storiche rimangono V11. Ruff E501 iniziali corretti, log conservati.

Due sessioni reali V11 rivalidate read-only con risultato identico, nessun upgrade.
Checkpoint read-only delle sessioni/originale verificato invariato alla fine.
Il server utente era attivo: una sua sessione è avanzata normalmente alla
versione6 durante il lavoro; nessun benchmark ha chiamato API mutative live.
La prova non certifica immutabilità di ogni riga del DB dall'inizio del turno.

L'ultimo ritocco dopo le serie riguarda solo l'avviso backend quando omissioni
e motivi respinti coesistono; non il prompt, lo schema o il giudizio AI misurato.
Suite finale rieseguita dopo quel ritocco, nessun modello modificato durante prove.

## Ripresa e acquisizioni

Per vedere V12: nuova conversazione, @domanda-iscrizione.docx, «me lo compili?».
Il riepilogo deve spiegare categorie di vuoti e segnalare motivi non validati o
omissioni. Non promette un’analisi successiva in background. Consultare global-report
per ciascuna posizione, senza confondere coverage con lo stato corrente USER.
Le vecchie sessioni non ricevono motivazioni retroattive: nessuna migrazione/reindex.

**Limite ancora aperto:** associazione delle spiegazioni ai blocchi ripetuti e
scope delle condizioni; non risolto aumentando i contesti SOURCE o accettando
quote non ancorate. La copertura semantica Minervino non è completa. Prossimo:
isolare questi gruppi con regressioni FORM, poi migliorare la loro rappresentazione
senza perdere le proposte Source. Le condizioni generiche «IN QUALITÀ DI» e
le domande sul ruolo sono un problema distinto già documentato.

[Metriche complete](benchmarks/2026-10-13-field-decisions.json),
[bundle](benchmarks/2026-10-13-field-decisions-audit.tar.gz),
[manifest](benchmarks/2026-10-13-field-decisions-manifest.json).
Bundle202 file/9.658.949 byte grezzi, confronto byte per byte e scansione chiave
superati; DB e file credenziali esclusi. SHA256
`8092c5f29a8802e674220468690612c7e1912aee89d11583324dbfbad587f6ec`.
Raw locali in backend/data/compilation-audit/field-decisions-20261013/;
log field-decisions-*.txt. Runner riproducibile benchmark_field_decisions.py
con baseline archiviata; credenziali configurate localmente, non nel bundle.
Commit per passi, nessun push.
