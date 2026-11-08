# UI della ricerca: Qdrant e avvisi — 29 ottobre 2026

**Completato nel frontend ordinario.** Per Qdrant esterno, indirizzo e **Porta
(opzionale)** sono separati, con suggerimento 6333. Riutilizzato il componente
degli embedding, parametrizzando nomi dei campi, descrizioni accessibili e porta
di esempio. I due servizi mantengono valori e validazioni indipendenti.

Il difetto dell'avviso era la posizione del JSX: `indexConfigChanged` veniva
mostrato alla fine del riquadro embedding. Ora lo stesso avviso è sotto il metodo
di ricerca, fuori dalle impostazioni avanzate; condizioni e operazioni di
indicizzazione sono invariate. La dicitura «Modello previsto» è stata rimossa.
Resta «Modello attivo» soltanto per la configurazione semantica già salvata.

## Verifiche

- Prima: 3 nuovi casi FAIL e 42 preesistenti PASS.
- Dopo: 174 test frontend PASS, inclusi 45 del pannello; lint/build PASS.
- Browser: 8 prove PASS desktop/mobile con API simulate, tema chiaro e 320 px;
  indirizzo e porta Qdrant composti correttamente, indipendenti dagli embedding.
- Verificate posizione e leggibilità dell'avviso, anche con dettagli chiusi,
  e compatibilità delle credenziali e dei controlli già esistenti.
- Un errore nella nuova fixture unit test, che tentava di selezionare un ID
  assente dal catalogo dopo il mapping dell'alias `:latest`, è stato corretto
  rendendo esplicite le opzioni del caso. Log del primo giro conservato.
- Screenshot desktop/mobile ispezionati; Graphify aggiornato via AST.

Nessun cambiamento a backend, algoritmo di ricerca, compilazione o database;
nessuna inferenza o chiamata a provider durante le verifiche. Vite isolato su
15174, poi arrestato; nessun riavvio dell'app backend ordinaria.

## File e rollback

File applicativi: `ServiceAddressFields.tsx` e `RetrievalSettingsPanel.tsx`;
test del pannello e `frontend/e2e/retrieval-settings.spec.ts`; README, STATUS,
relazioni e questo rapporto. Nessun commit/push.

Backup, log, screenshot e patch locale in
`backend/data/compilation-audit/ui-ricerca-qdrant-20261029-01/`, con copia verificata
in `/home/montesano/tesi-backups/ui-ricerca-qdrant-20261029-01/`.

La patch contiene solo questo intervento rispetto allo stato locale precedente.
Rollback dalla radice, con controllo preventivo di eventuali modifiche successive:

```bash
git apply --reverse --check backend/data/compilation-audit/ui-ricerca-qdrant-20261029-01/ui-ricerca.patch
git apply --reverse backend/data/compilation-audit/ui-ricerca-qdrant-20261029-01/ui-ricerca.patch
```

Per riapplicare: `git apply --check` e `git apply` sulla stessa patch.
Rollback e riapplicazione verificati in una copia isolata, controllando hash e
test del pannello: rispettivamente 42 e 45 PASS. Nessuna migrazione o modifica
ai dati. Per annullare anche il precedente intervento sugli embedding, annullare
prima questo, poi utilizzare il suo rollback documentato.
