# Recupero dei messaggi solo dopo un errore — 26 ottobre 2026

Il pulsante «Riutilizza messaggio» appariva anche sotto messaggi riusciti quando
il composer era vuoto. Serviva a ricopiare il testo, non a reinviarlo, ma la
condizione di visibilità non controllava l'esito del messaggio.

Correzione circoscritta a `ProjectWorkspacePage.tsx`: il comando viene offerto
solo dopo errore di rete o esito `failed` / `not_configured`, si chiama
«Recupera messaggio» e usa lo stile dei pulsanti esistenti. Se c'è già una copia
locale recuperabile, resta il solo comando nel composer. Il testo recuperato
non viene inviato automaticamente e non sovrascrive una nuova bozza digitata.
Nessuna modifica al backend, al motore DOCX, ai profili o alle sessioni.

Verifiche offline con API simulate:

- Prima: i test aggiornati mostrano 4 fallimenti e 12 successi.
- Dopo: tutti i 154 test frontend superati (16 nel file sul recupero).
- Lint e build frontend superati.
- Rollback: applicata la patch inversa nel worktree isolato; entrambi i file
  tornano esattamente alla base `1785357` (`git diff --exit-code`), poi la patch
  viene riapplicata. Nessuna modifica dei dati e nessuna migrazione.

Il fix è isolato sul branch `fix/2026-10-26-recupero-messaggi`; la sola patch UI
viene riportata nel working tree ordinario per correggere il difetto segnalato.
Le modifiche già presenti sono conservate. Nessun push o merge.

Per annullare nell'ordinario, dopo `git apply --reverse --check`, usare:

```bash
git apply --reverse backend/data/compilation-audit/recupero-messaggi-20261026-01/fix.patch
```

Sul branch dedicato è possibile fare il revert del commit del fix. Non servono
flag, nuove dipendenze o modifiche ai dati. Risultati e patch sono conservati in
`backend/data/compilation-audit/recupero-messaggi-20261026-01/`.
