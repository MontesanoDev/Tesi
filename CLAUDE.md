## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

### Perimetro Graphify di questo progetto

- La mappa ordinaria comprende soltanto `backend/app/**/*.py` e il codice
  TypeScript/TSX di `frontend/src/`, esclusi i test. La lista ammessa è in
  `.graphifyignore`: non allargarla a dati, documenti, audit, fixture o benchmark.
- Prima costruzione: `graphify extract . --code-only`. Aggiornamento dopo
  modifiche o cambio branch: `graphify update .`; conserva lo stesso perimetro.
- Per simboli noti preferire `graphify explain "nome"`; per esplorazione usare
  `graphify query "termini del codice" --budget 1000`. I risultati possono essere
  troncati o incompleti: verificare nel sorgente i passaggi rilevanti prima dei fix.
- `graphify-out/` è locale e ignorata da Git. Ogni worktree deve avere la propria
  mappa; non copiare quella dell'app in una candidata con codice diverso.
- Nessuna estrazione semantica, chiamata LLM, cloud, hook Git o modalità watch
  è necessaria per questa configurazione. Guida: `docs/graphify-app-2026-10-28.md`.
