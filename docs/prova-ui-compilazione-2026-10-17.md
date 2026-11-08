# Prova dalla UI con le correzioni verificate

17 ottobre 2026. Su richiesta dell'utente sono stati avviati backend e frontend
locali con `./start.sh`, usando il codice corrente e la configurazione esistente.

- [Apri Minervino](http://localhost:5173/projects/minervino-di-lecce-elenco-sia).
- [API locale](http://localhost:8000/docs).
- [Verifiche e misure](benchmarks/2026-10-17-ui-binding.json).
- [Backup dei log e controlli](benchmarks/2026-10-17-ui-binding-audit.tar.gz).

Le correzioni SOURCE, Comune, contesto FORM e trasporto USER erano già nei
moduli applicativi chiamati dalla UI: non un motore separato del benchmark.
Verificato il percorso chat globale → `_prepare` → input completo B0 con
contesto USER registrato → validazione → dialogo → export esistente.
Non sono stati aggiunti selettori, modalità alternative o una nuova architettura.
FORM compatto e indice diretto non sono stati collegati alla UI.

## Come effettuare la prova

1. Aprire il progetto dalla pagina sopra, usando il composer iniziale per
   una **nuova conversazione**. Le conversazioni precedenti conservano i
   propri audit e non vengono migrate o ricalcolate implicitamente.
2. Selezionare con `@` il modulo vuoto `domanda-iscrizione.docx`.
3. Per riprodurre lo scenario sintetico, fornire le scelte della pratica nel
   messaggio iniziale, come nel testo congelato riportato sotto. Per prove
   diverse usare le proprie decisioni, senza inferirle dalle cariche aziendali.
4. Attendere l'analisi, rispondere alle domande e chiedere esplicitamente
   «Genera la bozza parziale», poi scaricare e controllare il Word.

Messaggio iniziale dello scenario Minervino:

> Compila una bozza della domanda di iscrizione all'elenco di Minervino di Lecce per Mapi Ingegneria S.r.l., che partecipa soltanto come società di ingegneria. Il firmatario scelto per questa pratica è Leonardo Montemurro, rappresentante legale.
>
> Usa i dati documentati nelle fonti, riferiti al 15 ottobre 2026. Chiedimi le scelte, le designazioni e le attestazioni della pratica che non sono nelle fonti. Non dedurre queste decisioni dai ruoli aziendali. Prima di generare il Word chiedimi di confermare l'export della bozza.

Il messaggio viene trasmesso come richiesta USER registrata della nuova
sessione, non trasformato dal backend in fatti SOURCE o conferme automatiche.
Questo percorso con USER non è una nuova misura della baseline B0 senza USER.

## Che cosa è disponibile e quali limiti restano

Sono attive le correzioni del verificatore dei binding, l'incompatibilità
indirizzo/Comune, il riconoscimento dei contesti FORM già verificati e la
trasmissione delle richieste/decisioni USER registrate e pertinenti.
Il modulo live ha lo stesso hash del congelato e le stesse 56 SOURCE;
l'input canonico senza USER coincide esattamente con quello B0.

**Il risultato offline di 48 scritture includeva una revisione manuale.**
Quelle approvazioni non sono state importate nella UI, e nessuna proposta
viene automaticamente promossa a risolta. Il narratore conserva le proprie
esclusioni e conferme semantiche. In particolare il codice corrente espone
alla sintesi al massimo 40 proposte SOURCE per passo: è un limite ancora
presente, non rimosso durante questa attivazione. L'indipendenza dei nove
dati generali da `c_p39`, le scelte native e i difetti di spaziatura restano
quelli documentati. Il test dalla UI serve a misurare questo percorso reale,
senza promettere le stesse 48 scritture automaticamente.

## Verifiche eseguite ora

- 298 test backend mirati passati in 36,28 s: binding, identità, Comune/FORM,
  USER, sessioni globali, condizioni e dialogo; provider simulati e DB isolati.
- Otto E2E browser passati in 23,9 s, desktop/mobile, con API simulate:
  compilazione globale, chiarimenti, export esplicito, refresh e lease.
- Prima esecuzione E2E: sette passati e uno fallito perché il test attendeva
  il vecchio testo «Sto lavorando…». Corretto solo quel test: attende ora lo
  status accessibile «Mapi sta elaborando» con «Analizzo il modulo…».
  Log, screenshot e trace del fallimento conservati.
- Lint frontend passato. Nessuna modifica al codice applicativo in questa fase;
  l'unica modifica di test è `frontend/e2e/global-compilation.spec.ts`.
- Verifica browser sulla UI reale: progetto aperto e mention del DOCX selezionata,
  nessun errore JavaScript, nessun messaggio inviato o richiesta di mutazione.
- Health API, frontend e proxy Vite rispondono 200. Le 28 sessioni, versioni e
  stati JSON sono identici prima e dopo avvio/verifiche; invariati anche i
  conteggi di revisioni, turni, esportazioni, progetti e file.

Non effettuata una nuova compilazione con provider reale: la prova qualitativa
è lasciata all'utente. Nessuna nuova chiamata LLM, modifica del writer, cambio
del modello/thinking, migrazione delle sessioni, commit o push.

Raw: `backend/data/compilation-audit/ui-binding-20261017-01/`. Backup preventivo
privato del database: `.tools/ui-binding-20261017-01/before-start.db`, escluso
dall'archivio pubblico; non contiene soltanto dati del benchmark e non va pubblicato.
I servizi sono lasciati avviati per la prova dell'utente.
