# Benchmark ufficiale V12 — 19 ottobre 2026

Leggere [RAPPORTO-CONCLUSIVO.md](RAPPORTO-CONCLUSIVO.md). **Baseline non adottata:** Trapani contiene un'accettazione PEC completata senza conferma USER; altri vuoti e limiti sono documentati. Nessuna correzione eseguita durante la prova.

| Procedura | DOCX effettivo | PDF | Metriche | Dialogo |
|---|---|---|---|---|
| Minervino | [55 scritture](minervino/bozza.docx) | [9 pagine](minervino/bozza.pdf) | [JSON](minervino/metriche.json) | [MD](minervino/dialogo.md) |
| Trapani | [10 scritture, una indebita](trapani/bozza.docx) | [5 pagine](trapani/bozza.pdf) | [JSON](trapani/metriche.json) | [MD](trapani/dialogo.md) |
| Catanzaro | [13 scritture](catanzaro/bozza.docx) | [17 pagine](catanzaro/bozza.pdf) | [JSON](catanzaro/metriche.json) | [MD](catanzaro/dialogo.md) |

[Confronto JSON](CONFRONTO.json), [CSV](CONFRONTO.csv), [controlli finali](CONTROLLI-FINALI.json).

Ogni cartella conserva separatamente input originale, scenario e riferimento preregistrati, richiesta e risposta globale, system prompt, audit iniziale e finale, stato finale, report del normale export, verifiche fisiche e PDF, valutazione di tutti i candidati, omissioni, domande e uso del provider. I candidati non proposti non sono automaticamente fatti obbligatori o dati assenti. Il giudizio semantico delle scritture è nel rapporto e nella valutazione per campo; il validatore ordinario non basta da solo a escludere errori di contesto.

Il grezzo originale è in `backend/data/compilation-audit/ufficiale-v12-20261019-01/`. [Backup completo](audit-completo.tar.gz), [checksum](audit-completo.tar.gz.sha256), [descrittore](BACKUP.json). Include audit grezzi, browser, prompt/schema/risposte HTTP di tutte le 30 chiamate, stato, transizioni, dialogo, rendering, script e codice della pipeline usata. Esclude database runtime, chiavi, `.env` e credenziali. Le sessioni originali restano intatte nel sistema locale.

Per verificare il bundle estrarlo in una nuova cartella. Dalla directory estratta, usare un ambiente Python con le dipendenze del backend (`uv.lock` incluso):

```bash
PYTHONPATH=code/backend /percorso/al/python/backend audit/verify_bundle.py
```

Il verificatore vieta la rete e non legge database/chiavi: ricostruisce audit e tre DOCX byte per byte da risposte reali e ricevute già registrate. Anche l'errore di contesto Trapani viene riprodotto: uguaglianza del replay e correttezza semantica sono verifiche distinte. `MANIFEST-SHA256.json` nel bundle consente di verificare tutti i file estratti.

Nessun commit/push; nessun congelamento della baseline effettuato.
