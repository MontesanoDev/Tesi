# Provider di embedding e ordine delle impostazioni — 21 ottobre 2026

Richiesta: consentire provider embedding oltre a Ollama e ordinare i riquadri
in **Modelli AI → Modelli di embedding → Ricerca nelle fonti**. Il motore di
compilazione e le candidate V12/V13/V14 non sono parte di questo intervento.

## Comportamento

Il provider embedding si sceglie nel riquadro dedicato: Ollama, OpenAI, Mistral
o un servizio compatibile con l'API embedding OpenAI. Un solo servizio/modello
è attivo alla volta per tutti i progetti, come prevedeva la configurazione RAG
esistente. Non è introdotto un archivio di profili embedding multipli. Provider
e modello generativo della chat restano indipendenti.

La scelta di un nuovo provider propone indirizzo e modello iniziali, svuota il
campo della chiave e invalida l'elenco precedente. Le impostazioni avanzate si
aprono per consentire l'inserimento delle credenziali. «Ricarica modelli» legge
il catalogo; «Salva impostazioni» conserva la configurazione ma non indicizza.
La verifica del collegamento e la manutenzione rimangono distinte nella ricerca.

Ollama mantiene l'elenco dei modelli installati con capacità embedding. OpenAI
mostra gli identificativi `text-embedding-*` restituiti dal suo catalogo;
Mistral usa la capacità `embeddings` quando dichiarata e riconosce i propri
identificativi embedding documentati, soltanto se presenti nel catalogo restituito.
Un'indicazione esplicita negativa prevale sul riconoscimento del nome. Per gli endpoint
compatibili, senza metadati sufficienti non si propone un modello generativo
come embedding: il nome del modello può essere inserito manualmente e la
verifica del collegamento ne prova l'effettivo utilizzo. La mancata risposta
del catalogo non cambia automaticamente la configurazione salvata.

Ollama conserva il modello `bge-m3` e il trasporto precedente. Gli altri servizi
usano `POST /embeddings` attraverso un adattatore LangChain, con input testuale
integrale e formato float. Numero dei vettori, indici, finitezza, vettori non
nulli e dimensioni vengono controllati. Gli indici della risposta sono usati per
ricostruire l'ordine degli input; duplicati o indici mancanti sono errori.
Non sono introdotti retry o fallback automatici. Errori HTTP, timeout e risposte
non valide non espongono chiavi, header o corpi remoti.

Il contratto API è stato verificato sulla [documentazione ufficiale OpenAI](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
e sulla [documentazione embedding Mistral](https://docs.mistral.ai/api/endpoint/embeddings).
Il filtro di disponibilità Mistral segue il [catalogo dei modelli](https://docs.mistral.ai/api/endpoint/models).
I nomi delle famiglie embedding sono documentati anche nella [guida Mistral](https://docs.mistral.ai/studio/knowledge-rag/embeddings/code_embeddings).
Consultata la skill OpenAI Docs per l'integrazione OpenAI; nessuna chiave o
generazione reale è stata necessaria per i test con trasporto simulato.

## Compatibilità, credenziali e indice

`embedding_provider` è un campo aggiuntivo del JSON esistente, predefinito
`ollama`. Una configurazione precedente senza questo campo continua a essere
letta come Ollama senza riscrivere il database. Nessuna migrazione di schema,
sessione o benchmark; il campo viene persistito solo al salvataggio esplicito.

Cambiare provider oppure indirizzo non autorizza il riuso implicito della
chiave salvata, anche se l'indirizzo coincide. Le chiavi embedding restano
cifrate, separate da chat e Qdrant; la risposta API espone solo il flag di
presenza. OpenAI e Mistral richiedono una propria chiave. Nessuna chiave viene
letta automaticamente dalle variabili API dei provider generativi.

Il percorso Ollama mantiene il digest e il nome dell'indice precedenti. Per
le API remote l'identità include provider, URL e modello, così il cambio di
servizio separa gli indici. Il salvataggio non li popola: la preparazione
rimane esplicita o avviene alla successiva ricerca semantica, come prima.
Algoritmo di retrieval, filtri SOURCE/FORM, Qdrant e controlli documentali non
sono stati modificati. Nessun comando di aggiornamento Qdrant live è stato
eseguito; gli effetti dell'auto-reload sul database/FTS sono descritti sotto.

Limite: le API remote non forniscono un digest dei pesi come Ollama. L'identità
configurata non rileva aggiornamenti invisibili del modello dietro lo stesso
alias remoto. Per versioni o pesi diversi è opportuno usare identificativi
espliciti forniti dal servizio; non viene simulata una riproducibilità dei pesi
che il provider non espone. Gli endpoint compatibili devono implementare davvero
il contratto embedding; il nome del servizio da solo non ne garantisce il supporto.
La lettura del catalogo non prova la disponibilità dell'endpoint di embedding:
questa viene verificata solo dal comando di collegamento o dall'uso effettivo.

## File

- `backend/app/embedding_providers.py`: catalogo dei servizi supportati.
- `backend/app/retrieval_embedding_api.py`: adattatore del protocollo embedding.
- `backend/app/retrieval_embeddings.py`: scelta dell'adattatore, Ollama conservato.
- `backend/app/retrieval_settings.py`: campo aggiuntivo e isolamento delle chiavi.
- `backend/app/ai_discovery.py`, `retrieval_routes.py`: cataloghi e lettura provider.
- `frontend/src/types.ts`, `api.ts`: contratti e client.
- `frontend/src/components/RetrievalSettingsPanel.tsx`: provider e ordine dei riquadri.
- Test backend e UI/E2E pertinenti; README, STATUS e relazioni.

## Verifiche e preservazione

Test backend con database/storage temporanei e trasporti simulati; test del
nuovo adattatore, configurazioni legacy, isolamento delle credenziali e indici
Qdrant reali temporanei. Browser con API interamente simulate, anche per il
nuovo percorso di scelta/salvataggio di un provider cloud. Nessuna prova di
qualità su embedding reali o chiamata a pagamento; nessuna compilazione DOCX.

Audit e log: `backend/data/compilation-audit/embedding-providers-ui-20261021-01/`.
Snapshot dei file precedenti e copia privata in sola lettura dello stato del
DB live: `.tools/embedding-providers-ui-20261021-01/`. La copia privata non entra
nel backup condivisibile. Gli esiti finali sono riportati di seguito e in STATUS.
Nessun commit, tag o push.

## Effetto del runtime già attivo sul database live

L'app di sviluppo su 8000 era in auto-reload. Salvando moduli backend si riesegue
il suo avvio preesistente (`init_database` e `seed_markdown_artifacts`), che
ricostruisce FTS e sostituisce i frammenti degli artefatti. La copia del database
presa prima di questo intervento consente di distinguere questo effetto dalle
scritture applicative delle impostazioni.

Il controllo non certifica l'identità del file DB: sono cambiati gli ID e i
timestamp di creazione dei frammenti di tipo `artifact`, le corrispondenti
strutture FTS e il contatore autoincrementale. Non si esegue alcun ripristino del
DB attivo. I confronti per tabella, la verifica dei contenuti a parità di
file/posizione e il controllo di integrità sono registrati nell'audit.
Il comportamento di avvio che produce questi aggiornamenti non viene corretto
in questo intervento. I test usano invece database e indici temporanei.

Confronto verificato: 340 frammenti prima e dopo; 82 frammenti `artifact` con
ID/timestamp ricreati, contenuto, posizione, appartenenza e conteggi invariati.
Le 29 sessioni di compilazione, i record dei file e delle SOURCE globali sono
identici; `quick_check` SQLite OK. Il file DB completo e FTS non sono identici.

Durante il lavoro sono inoltre cambiati da attività concorrente
`compilation_global_sessions.py` e `compilation_source_reuse.py`: non scritti o
ripristinati da questo intervento. Per questo il working tree condiviso non è
un freeze sperimentale e gli esiti della suite non vanno usati per adottare
automaticamente la candidata di compilazione corrente. I quattro moduli
backend preesistenti modificati qui sono soltanto discovery, routing,
impostazioni e scelta dell'adattatore embedding, oltre ai due nuovi moduli.

## Risultati conclusivi

| Verifica | Esito |
|---|---|
| Suite backend eseguita dopo l'ultimo aggiornamento al catalogo | 3.426 PASS, 354,38 s |
| Suite frontend completa, inclusi 25 casi del pannello | 147 PASS, 6,43 s |
| Tre scenari browser desktop/mobile, API simulate | 6 PASS, 6,4 s |
| Ruff backend, lint frontend, TypeScript/build | PASS |
| Hash dei file dell'intervento durante l'ultima suite | Invariati |
| Database: contenuti SOURCE, record file e 29 sessioni | Invariati; effetti artifact/FTS descritti sopra |

32 nuovi casi backend verificano il protocollo remoto, ordine e dimensione dei
vettori, risposte errate, errori HTTP senza retry/redirect, credenziali, configurazioni
precedenti, cataloghi e separazione degli indici. I quattro casi componente
aggiuntivi verificano provider, ordine dei pannelli, chiavi e modello personalizzato.
Le prove non certificano la disponibilità dei servizi reali né la qualità degli
embedding. La suite è quella raccolta all'avvio; attività concorrente sulla
compilazione resta separata dalla verifica di questa funzionalità RAG.

Acquisizioni intermedie conservate: prima suite completa 3.424 PASS; poi aggiunti
due casi per il catalogo Mistral quando mancano metadati di capacità e rieseguita
la suite. Il primo scenario browser cloud falliva per un mock che pretendeva la
chiave in chiaro anche nelle riletture successive al salvataggio: corretto il solo
mock per rappresentare la conservazione server del segreto, sei scenari finali PASS.

Backup circoscritto a codice, test, documentazione e acquisizioni di questo
intervento: `docs/benchmarks/2026-10-21-embedding-providers-ui-audit.tar.gz`.
Manifest incluso e verifica SHA-256 da estrazione separata nel relativo
`2026-10-21-embedding-providers-ui-verifica.json`. Esclusi database live e copie
private, indici, chiavi e artefatti storici. Non è uno snapshot dell'intera candidata
di compilazione in sviluppo concorrente.
