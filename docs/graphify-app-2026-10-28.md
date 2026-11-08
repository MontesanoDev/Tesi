# Graphify per il codice dell'app — 28 ottobre 2026

Configurazione locale adottata sul working tree ordinario. Non cambia il prodotto,
il compilatore, i prompt, il profilo delle sessioni o i dati. Nessuna inferenza.

## Installazione e perimetro

Graphify `0.9.97`, pacchetto ufficiale `graphifyy`, installato con `uv tool` in un
ambiente distinto da quello dell'app. CLI funzionante, skill Codex presente e
istruzioni native in AGENTS.md/CLAUDE.md conservate. Nessun hook Git installato,
nessun watcher o servizio cloud avviato. Non serve un server MCP per questi comandi.

`.graphifyignore` esclude tutto per impostazione iniziale e ammette solo:

- `backend/app/**/*.py`: 84 file;
- TypeScript/TSX di `frontend/src/`, esclusi test, fixture e dichiarazioni `.d.ts`:
  29 file.

Totale **113 file**. Sono esclusi test backend e frontend, script sperimentali,
audit, documenti, database, benchmark, backup, dipendenze e configurazioni segrete.
Anche cartelle nuove fuori dalle due aree restano escluse automaticamente.
CSS, asset e configurazione di build non sono mappati: la mappa riguarda il codice
applicativo, non ogni elemento del repository. Un eventuale ampliamento deve
avere uno scopo preciso.

La prima ricognizione preparatoria comprendeva anche test e strumenti in una
cache separata. Non è stata adottata: l'indice effettivo in `graphify-out/` contiene
solo il perimetro sopra. Il prototipo di wrapper non è stato installato nell'app;
si usano direttamente i comandi di Graphify già installato dall'utente.

## Uso

Dalla radice del worktree ordinario:

```bash
graphify explain "new_session_flags"
graphify explain "_resilient_proposal"
graphify query "compilation dialogue" --budget 1000
graphify path "backend_app_compilation_global_sessions_generate_draft" "backend_app_docx_templates_fill_docx"
```

Per nomi ambigui usare l'ID restituito dal grafo. `query` cerca termini presenti
nei simboli: una domanda in italiano non viene tradotta semanticamente dal CLI.
L'assistente deve ricondurla ai nomi effettivi. Non leggere l'intero grafo JSON
per ogni domanda; preferire query brevi o `explain` su un simbolo noto.

Dopo modifiche al codice o cambio branch:

```bash
graphify update .
```

Prima costruzione in un altro worktree: riportare intenzionalmente la stessa
`.graphifyignore`, poi `graphify extract . --code-only`. Non riutilizzare il grafo
ordinario per una candidata diversa. La grafica è `graphify-out/graph.html`, il
riepilogo è `graphify-out/GRAPH_REPORT.md`. La cartella è ignorata da Git.

## Verifiche eseguite

- Confronto del rilevamento con la lista indipendente dei file ammessi: 113/113.
- Otto esempi in directory temporanea: i due file applicativi ammessi; sei casi
  esclusi, inclusi dati privati, test, documenti e una cartella futura.
- Prima estrazione: 4,47 secondi, **1697 nodi, 5682 archi, 65 comunità**.
  Analisi AST locale: **0 token LLM, 0 chiamate a provider**. La rete era bloccata
  durante costruzione, esportazione HTML e verifica di aggiornamento.
- `graphify update .` completato, perimetro conservato e nessun cambiamento della
  topologia; 84 file serviti dalla cache, 29 frontend riesaminati.
- Cinque interrogazioni su profilo, generazione per sezioni, risposte USER,
  export e writer trovano il simbolo nel file atteso: 0,26–0,28 secondi ciascuna,
  output di 606–2176 caratteri.
- 113 hash dei file applicativi invariati. Non eseguite suite del compilatore o
  frontend, perché non sono stati modificati.

Non abbiamo misurato un risparmio percentuale dei token degli assistenti a parità
di compito. Queste prove mostrano navigazione funzionante e risposte compatte;
non dimostrano ancora un miglioramento della produttività complessiva.

## Limiti della mappa

L'estrattore segnala nessun simbolo per `frontend/src/main.tsx`. La diagnostica
sull'estrazione grezza rileva 562 relazioni con estremi non dichiarati nel catalogo
originale dei nodi, 9 autoarchi e 276 relazioni accorpate nel grafo diretto. La
libreria completa alcuni riferimenti nel grafo finale; ciò non equivale a una
risoluzione semantica verificata. Conservata la diagnostica completa nell'audit.

Import dinamici, collegamenti HTTP tra frontend/backend e condizioni di esecuzione
non sono necessariamente ricostruiti. La mappa aiuta a trovare i punti da leggere;
non certifica sicurezza, raggiungibilità o correttezza del compilatore.

Esempi dal report generato:

- Nodi più connessi: `connection()` (108 archi), `StrictModel` (68),
  `GenerationError` (48).
- Connessione proposta: `project_ai_context()` → `GenerationNotConfiguredError`,
  marcata **INFERRED**, da verificare nel sorgente.
- Domanda suggerita: il ruolo di `review_fields()` nei collegamenti tra dialogo,
  sessioni, segmenti e ambito delle tabelle. È un punto di partenza per l'analisi,
  non un risultato sperimentale sulla compilazione.

## Reversibilità e artefatti

Modifiche circoscritte: `.graphifyignore`, riga di esclusione in `.gitignore`,
sezione di perimetro in AGENTS.md/CLAUDE.md, STATUS.md, relazioni.md e questa guida.
Nessun commit, push, merge o attivazione di fix applicativi.

Backup precedente delle configurazioni in
`backend/data/compilation-audit/graphify-app-20261028-01/before/`, con manifest.
Grezzi, diagnostica, risultati delle query e verifiche nello stesso audit locale.
Backup separato verificato in `/home/montesano/tesi-backups/graphify-app-20261028-01/`.

Per annullare questa configurazione senza rimuovere l'installazione dell'utente:
spostare `graphify-out/` nel backup; ripristinare i soli file di configurazione
precedenti dal backup se non sono intervenute altre modifiche; archiviare
`.graphifyignore` e la guida nuove. Non ripristinare l'intero repository e non
usare `git reset` o `clean`. In presenza di modifiche successive, rimuovere soltanto
le aggiunte di questa adozione. Sessioni e documenti non sono coinvolti.

## Valutazione di Superpowers

Valutato, **non installato**. È un insieme di procedure/skill, non un indice del
codice. Le skill di debugging sistematico e verifica prima della conclusione sono
coerenti con il nostro lavoro. Il pacchetto completo introduce anche pianificazione,
passaggi di approvazione e lavoro con subagenti: il vantaggio sui nostri task e il
costo di contesto non sono stati misurati.

Una prova successiva sensata è un solo difetto circoscritto, confrontando
riproducibilità, regressioni, tempo e token. Nessuna adozione automatica delle
procedure complete. Riferimenti consultati:
[repository](https://github.com/obra/superpowers),
[systematic-debugging](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md),
[verification-before-completion](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md).
