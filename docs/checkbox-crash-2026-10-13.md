# Gruppi checkbox rifiutati: crash della sintesi

## Causa reale

Sessione Minervino `71cc0b5bbe6d463695430f4f4a418d67`, modulo
`domanda-iscrizione.docx`. Il POST resolve falliva in
`compilation_global_dialogue.export_selection`, chiamato da narrate prima del
salvataggio dell'audit in sessione. L'analisi e la risposta della sintesi erano
già conservate su disco; il database risultava FAILED, audit non persistito.
La diagnosi e i replay leggono la sessione senza modificarla.

Il gruppo `g_rtp_stato` conteneva un'opzione con label oltre 250 caratteri.
Il validatore Pydantic lo rifiutava correttamente. Un record REJECTED conserva
proposta, errori e un dizionario options vuoto; non possiede necessariamente
min_selected, selection o gli altri attributi del modello validato.
L'export selection iterava indiscriminatamente su tutti i record e accedeva
a `group["min_selected"]`: **KeyError e HTTP 500**. Il problema era nel consumo
backend dell'audit parziale, non nella validità della scelta rifiutata.

Il secondo gruppo `g_qualita` era rifiutato per lista fisica non verificata:
mantiene la propria diagnosi e non viene approvato da questo intervento.
L'audit conserva tredici proposte testuali SOURCE grounded conditional.

## Correzione minima

L'export selection applica regole di cardinalità **soltanto a GROUNDED_GROUP**.
I record rifiutati restano in quarantena e non diventano gruppi opzionali tramite
valori di default. Le altre proposte possono essere sintetizzate e salvate.
Nessun catch globale di KeyError, aumento del limite label, nuova chiamata di
analisi o modifica a RAG, parser, renderer, UI e provenance.

Dieci regressioni riproducevano il crash prima del fix: record nulli/incompleti
e label fuori schema, mantenendo un gruppo valido indipendente; percorso API
con SOURCE testuali, sintesi, GET dopo persistenza ed export esplicitamente
autorizzato. Ora passano, con i gruppi invalidi sempre REJECTED, nessun valore
checkbox scritto per loro e valori SOURCE indipendenti conservati. FTS5/Qdrant
sono coperti nei test software con provider simulati.

## Replay reale

Riprodotto il KeyError con l'esatto audit e la sintesi DeepSeek già salvati,
senza nuove chiamate. Dopo il fix, lo stesso output passa e genera le due
domande di applicabilità. Nessun requisito o valore riparato nel raw.

Eseguita poi **una nuova sintesi DeepSeek Flash reale**, non una nuova analisi:
3,81 secondi, 3.845 token, nessun errore o retry. Tredici proposte conditional
conservate, due domande naturali, nessun DOCX generato o condizione approvata
automaticamente. Codice congelato durante la prova. Sessione live/versione/
originale verificati invariati. Questo è un replay della sintesi, non una
compilazione nuova end-to-end né il recupero manuale del database dell'utente.

Raw locali: `backend/data/compilation-audit/rejected-checkbox-20261013/`.
Runner: [replay_rejected_checkbox_groups.py](benchmarks/replay_rejected_checkbox_groups.py).
Log del fallimento software e delle verifiche successive conservati separatamente.
[Acquisizioni sanificate](benchmarks/2026-10-13-checkbox-crash-audit.tar.gz),
[manifest, metriche e SHA256](benchmarks/2026-10-13-checkbox-crash-manifest.json).
Bundle di 81 file /1.818.061 byte grezzi, verificato byte per byte e senza
chiavi/DB; SHA256 7e8c4c3f0a2c29e10b94b5c365c143f95aba6c7061a00de104ddf2edbeb2dca3.

Verifiche software: **136 mirati /22,84 s**, **2.061 backend /153,38 s**,
Ruff backend/runner e diff check. Frontend/browser non ripetuti: nessun
contratto frontend o UI cambiato. I test API verificano anche persistenza,
export e provenienza, senza usare il database locale dell'utente.

## Uso e limite

La sessione già fallita non viene modificata automaticamente: dopo aver caricato
il backend aggiornato, usare «riprendi» nella stessa conversazione. Il workflow
esistente autorizza un nuovo tentativo di analisi perché l'audit del tentativo
fallito non era ancora persistito nel DB. L'analisi precedente resta su disco.
Nessuna migrazione o reindicizzazione. Questa correzione impedisce il crash
dei gruppi rifiutati; non certifica tutte le possibili eccezioni interne né
risolve la copertura semantica dei gruppi complessi. Commit locali, nessun push.
