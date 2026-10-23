# Baseline sperimentale conservativa Mapi V12

**Adottata il 21 ottobre 2026 per decisione esplicita dell'utente.** ID documentale `V12-B0-conservativa-20261021`; stato `ADOPTED_FOR_EXPERIMENTAL_COMPARISONS` nel [candidato aggiornato](<benchmark ufficiale/baseline-v12-20261021-01/CANDIDATO-BASELINE.json>).
Ambito: compilazione assistita di **bozze DOCX parziali con revisione umana obbligatoria**. Non è una versione definitiva, completa o pronta per pratiche ufficiali senza verifica. L'ID non è un tag Git.

## Identità esatta

La radice degli artefatti è `benchmark ufficiale/baseline-v12-20261021-01/`; il grezzo è `backend/data/compilation-audit/baseline-v12-20261021-01/`.

- HEAD `99ab052b3c6e626a4e1f6cc21b5ca31baba56a7e` **non identifica da solo la versione**. `before/` conserva il codice effettivo, compresi file non tracciati, test, script e lock; `FROZEN.json` identifica lo snapshot iniziale. Il grezzo contiene `working-tree-before.patch` per le modifiche locali tracciate.
- **119 hash applicativi**, 70 moduli backend e 49 file frontend, in `CANDIDATO-BASELINE.json`, `PROTOCOLLO.json` e nel grezzo `code-freeze.json`. SHA256 del mapping JSON ordinato e compatto: `e78b00698598031eb63edaf4bf07b48d7614cc68ba1e47f4cf61dedabe0e3bdf`. Tutti corrispondono sia al codice corrente sia allo snapshot.
- Configurazione registrata in `input/model.json`, parametri effettivi in `input/global-parameters.json`: DeepSeek `https://api.deepseek.com`, `deepseek-flash`, temperature 0,1, max_tokens 49152, thinking enabled, reasoning_effort low, risposta JSON. B0 globale invariata, nessuna E1/E2. La preferenza thinking=false del profilo non è il parametro della globale: valgono le richieste effettive registrate. Fingerprint osservato `e72d3c7f663d3e1383b00b3884cb4501`; l'alias non congela i pesi del provider.
- Prompt B0 `input/system-prompt.txt`, SHA256 `978c321f5a992e2b53f6dea55f6afcaaab18d4fa728470e9e6a7cc61e9904d8c`; contratto/schema nello snapshot e nelle richieste complete. SOURCE `input/SOURCE.json`, 22 chunk da quattro documenti sintetici, SHA256 `0982378194a2e3e769ed3e18dc8d92bf6c1c70f6c4e8b5aa9bbf6d236093ff0c`; originali e loro manifest nella stessa directory.
- FORM e scenari USER in `trials/<documento>/FORM-originale.docx` e `scenario-USER.json`, hash nel candidato e nel [protocollo preregistrato](<benchmark ufficiale/baseline-v12-20261021-01/PROTOCOLLO.json>). `SELEZIONE.json` conserva pool, strati e singolo sorteggio. Criteri: `riferimento-preregistrato.json`, `SCRITTURE-VERIFICATE.json` e `CLASSIFICAZIONE-CAMPI.json` per ogni prova. Massimo due risposte agli slot e un export parziale esplicito; fatti SOURCE, requisiti FORM, applicabilità e decisioni USER distinti.

## Risultati di riferimento immutati

| Nuova prova indipendente | DOCX | PDF | Testi / booleani | Chiamate | Token | USD stimati |
|---|---|---|---:|---:|---:|---:|
| Minervino | [DOCX](<benchmark ufficiale/baseline-v12-20261021-01/trials/minervino/bozza.docx>) | [PDF](<benchmark ufficiale/baseline-v12-20261021-01/trials/minervino/render/bozza.pdf>) | 43 / 0 | 11 | 191.074 | 0,042723132 |
| Cesano | [DOCX](<benchmark ufficiale/baseline-v12-20261021-01/trials/cesano/bozza.docx>) | [PDF](<benchmark ufficiale/baseline-v12-20261021-01/trials/cesano/render/bozza.pdf>) | 4 / 6 | 10 | 113.133 | 0,022892286 |
| CRAA | [DOCX](<benchmark ufficiale/baseline-v12-20261021-01/trials/craa/bozza.docx>) | [PDF](<benchmark ufficiale/baseline-v12-20261021-01/trials/craa/render/bozza.pdf>) | 7 / 0 | 7 | 93.775 | 0,020577600 |

**54 testi e 6 booleani** (un TRUE e cinque FALSE di un solo gruppo); **zero scritture non dimostrate osservate nella revisione documentale autoriale**. Restano **17 omissioni fattuali ingiustificate, una scelta checkbox omessa e un campo fermo per budget conversazionale**. Non sono una percentuale universale di accuratezza. Totale: **28 chiamate, tre globali nuove, 397.982 token, 0,086193018 USD stimati a tariffa**, non fattura. Tempi provider e UI separati in `MISURE.json` e [CONFRONTO.json](<benchmark ufficiale/baseline-v12-20261021-01/CONFRONTO.json>); richieste/risposte, usage, audit e dialoghi nel grezzo. Integrità DOCX e leggibilità di 19 pagine PDF già verificate.

**Minervino storico non è la nuova prova:** il checkpoint conservato con proposta globale congelata e precedente dialogo USER scrive 60 testi SOURCE più una checkbox USER, cioè **61 scritture**. La nuova sessione indipendente scrive **43 testi**, nessuna checkbox. Risposte globali, contesto SOURCE e dialogo/budget differiscono: non è una regressione deterministica 61→43 sulla stessa risposta né una copertura garantita dal backend. I replay storici a 61 rimangono un distinto vincolo di conservazione; [riferimento storico](docs/prova-chat-v12-hold-2026-10-19.md), [replay conservati](docs/relazioni-tabellari-form-v12-2026-10-20.md).

## Limiti e confronti futuri

Variabilità delle proposte LLM; SOURCE sintetiche e documenti già studiati; **una sola prova per documento**; revisione autoriale non indipendente. Grammatica FORM limitata e **assenza di composizione multi-SOURCE**. Copertura incompleta delle checkbox e dei record distribuiti, inclusi firmatario e direttore tecnico; conferme ripetute e budget conversazionale incidono sulle omissioni. Nessuna nuova dimostrazione positiva numero+data o di scrittura tabellare fattuale autorizzata in queste tre prove. L'adozione non risolve questi limiti né le omissioni.

Per confronti causali riusare le stesse risposte registrate, FORM/SOURCE/scenari e criteri, separando differenze di validazione, selezione, valori/posizioni XML, checkbox e autorizzazioni. Eventuali future inferenze reali vanno misurate separatamente con protocollo preregistrato: una migliore proposta LLM non dimostra una migliore validazione. Gold e riferimenti non entrano nel prompt. La suite 3.180 PASS/Ruff PASS è storica, non rieseguita per questa formalizzazione.

## Cronologia, backup e riproduzione offline

La [proposta e il rapporto originali](docs/valutazione-baseline-v12-2026-10-21.md), il README della valutazione e gli audit restano immutati e riportano lo stato storico `PROPOSED_NOT_ADOPTED`. Lo stato vigente è quello adottato qui sopra; `status_history` nel candidato conserva passaggio, autorità e hash della proposta originale.

Riutilizzato il [backup originale](<benchmark ufficiale/baseline-v12-20261021-01/audit-completo.tar.gz>), SHA256 `5a1d5b0c4df9039bed8f636a441f6484438442965339c4936666b160a0743a1d`, con [manifest](<benchmark ufficiale/baseline-v12-20261021-01/BACKUP-MANIFEST.json>) e [verifica estratta preesistente](<benchmark ufficiale/baseline-v12-20261021-01/VERIFICA-BACKUP.json>). Contiene anche il candidato originale (SHA256 `35252785305df6020d93e28cd901df37c06bc968b40e8ae9f7edf73c3ad66647`). Il vecchio manifest descrive quell'archivio: le sole differenze attese nei suoi file correnti sono candidato, STATUS e relazioni, aggiornati per l'adozione; nessun hash storico è riscritto.

Estrarre l'archivio in una directory nuova, verificarne il manifest, poi seguire i [comandi offline già documentati](<benchmark ufficiale/baseline-v12-20261021-01/README.md#backup-e-ricostruzione-offline>) con lo snapshot estratto e le dipendenze disponibili. `verify_real.py` vieta rete/SQLite e ricostruisce i tre audit/DOCX dalle risposte registrate, confrontandoli con i download; `summarize.py` ricalcola le misure. Non riproduce l'inferenza del provider né sostituisce la revisione umana. Non rilanciare `final_checks.py` per leggere lo stato adottato: è lo script storico che genera la proposta.

[Verifica dell'adozione](<benchmark ufficiale/baseline-v12-20261021-01/ADOZIONE-VERIFICHE.json>) e piccolo [addendum documentale](<benchmark ufficiale/baseline-v12-20261021-01/adozione-documentale.tar.gz>): riutilizzano il backup dei dati senza duplicarlo. Questa formalizzazione verifica file, hash e riferimenti; **nessuna nuova compilazione, chiamata LLM, modifica applicativa, test, migrazione, commit, tag o push**. Database live e sessioni storiche preservati.
