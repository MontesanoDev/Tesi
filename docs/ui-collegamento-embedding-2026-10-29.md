# Configurazione embedding: indirizzo, porta e verifica — 29 ottobre 2026

Nel pannello **Modelli di embedding → Impostazioni avanzate** l'indirizzo e la
**Porta (opzionale)** sono separati. Per Ollama locale: `127.0.0.1` e `11434`.
Su schermi piccoli i campi sono disposti verticalmente.

La porta vuota indica quella standard HTTP/HTTPS, non un servizio senza porta.
Si può incollare un URL completo; la porta viene estratta. Gli URL già salvati
non vengono riscritti all'apertura. HTTPS, percorsi, IPv6 e protezioni delle
credenziali restano supportati; l'API continua a ricevere il solo URL completo.

**Verifica collegamento** legge il catalogo embedding tramite l'endpoint esistente
`POST /api/settings/retrieval/models`, anche in modalità parole chiave. Usa i dati
non ancora salvati e distingue servizio irraggiungibile, modello elencato e
modello non elencato. Non esegue inferenze, salvataggi o indicizzazioni e non
dimostra che la generazione di embedding funzioni. Cambiando indirizzo, porta o
chiave la richiesta precedente viene annullata e il vecchio esito rimosso.
Il controllo completo di modello e archivio rimane disponibile con il nome
**Verifica ricerca semantica**.

## Modifiche

- `frontend/src/components/ServiceAddressFields.tsx`: presentazione e validazione
  dell'indirizzo e della porta, senza cambiare il contratto backend.
- `frontend/src/components/RetrievalSettingsPanel.tsx` e `RetrievalSettings.css`:
  controllo del catalogo, esiti, layout e denominazioni.
- Test del pannello e `frontend/e2e/retrieval-settings.spec.ts`; README, STATUS,
  relazioni e questo rapporto. Nessuna modifica a backend o compilatore.

## Verifiche effettivamente eseguite

| Verifica | Esito |
|---|---|
| Pannello prima dell'intervento | 25/25 PASS |
| Nuovi casi sul codice precedente | 12 FAIL, 25 preesistenti PASS |
| Suite frontend finale | 171 PASS, inclusi 42 casi del pannello |
| Lint e build frontend | PASS |
| Browser, API simulate | 8 PASS, desktop/mobile; tema chiaro e 320 px inclusi |
| Schermate desktop e mobile | Ispezionate visivamente |
| Graphify | Aggiornato, solo AST, 114 file applicativi |

Coperti salvataggio compatibile, porta assente o non valida, URL completi,
HTTPS/percorso/IPv6, cambio provider, credenziali, esito negativo, modello non
elencato e risposta tardiva. Nel primo giro browser, 6 PASS e 2 FAIL dovuti
all'asserzione che tentava di serializzare `ValidityState`: corretta soltanto
l'asserzione, poi 8/8 PASS. Il log iniziale è conservato.

Tutte le chiamate browser erano intercettate: nessun backend o provider reale
interrogato, nessuna modifica a database/sessioni. Backend non riavviato;
verifica su Vite isolato alla porta 15174, poi arrestato. L'app usa il nuovo
frontend al successivo avvio ordinario con `./start.sh`.

## Evidenze e ripristino

Acquisizioni locali in
`backend/data/compilation-audit/ui-collegamento-embedding-20261029-01/`:
backup dei file preesistenti, log prima/dopo, screenshot, manifest e patch
**del solo intervento**, calcolata rispetto ai file locali già modificati.
La patch non contiene le altre modifiche pendenti del repository.

Rollback selettivo, dalla radice, dopo aver controllato eventuale lavoro successivo:

```bash
git apply --reverse --check backend/data/compilation-audit/ui-collegamento-embedding-20261029-01/ui-collegamento.patch
git apply --reverse backend/data/compilation-audit/ui-collegamento-embedding-20261029-01/ui-collegamento.patch
```

Per riapplicare usare la stessa patch con `git apply --check`, poi `git apply`,
senza `--reverse`. Nessuna migrazione, dipendenza o modifica ai dati richiesta.
La verifica di rollback e riapplicazione è registrata in `rollback-verification.json`.
Nessun commit, push o modifica dei risultati storici.
