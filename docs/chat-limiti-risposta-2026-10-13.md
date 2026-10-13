# Limiti della risposta nella chat

L'etichetta «Informazioni mancanti» veniva aggiunta dalla UI a tutte le risposte
con `missing_information` non vuoto. In un riassunto FORM poteva elencare sezioni
non recuperate come se fossero dati aziendali da fornire o parti assenti dal Word.
L'assenza di un estratto dal contesto non verifica l'assenza dal documento.

Rimosso il riquadro automatico, insieme al CSS usato soltanto da esso. La chat
mostra il testo dell'assistente e conserva le evidenze consultabili con ruolo.
Questo vale anche riaprendo una conversazione precedente. Testo e dati storici
non vengono modificati. API, persistenza, report e output MIXED mantengono il
campo tecnico; i chiarimenti della compilazione restano nel normale messaggio.

Il generatore normale riceve una breve istruzione aggiuntiva: spiegare i limiti
pertinenti in `answer`, riassumere quanto sostenuto dalle evidenze senza inventare
sezioni mancanti e usare `missing_information: []` per i riassunti dei moduli.
Nessuna modifica a retrieval, schema, filtri, gate SOURCE/FORM o motore DOCX.
La copertura del riassunto può ancora essere parziale; il prompt non certifica
la correttezza semantica del modello né modifica risposte già salvate.

Verifiche software realmente eseguite:

- 9 test pagina mirati, inclusi nei **105 frontend passati in 12 file /6,29s**.
  Coperti FORM/SOURCE, spiegazione naturale del limite ed evidenze conservate,
  turni precedenti senza ripristino della lista e compilazione esistente.
- **136 backend /5,98s**, `tests/test_generation.py tests/test_form_retrieval.py`.
  Contratti, citazioni e separazione FORM/SOURCE/MIXED invariati.
- **8 Chromium /7,6s**, `chat-limitations.spec.ts document-mentions.spec.ts`:
  desktop/mobile, risposte FORM/SOURCE/no-evidence, refresh, evidenze e mention.
- **2 Chromium /1,8s**, caso «missing evidence is explained as an assistant answer»
  di `visual.spec.ts`, desktop/mobile. Il caso aveva un placeholder obsoleto e
  un'aspettativa non più valida sulla notice duplicata: aggiornato solo quello.
- Oxlint, build TypeScript/Vite, Ruff e `git diff --check` passati.

Browser su frontend separato5195, API simulate e nessuna modifica di dati utente.
Un primo filtro con ancore non selezionava test; due fallimenti sul vecchio
placeholder conservati prima della correzione. Nessun modello reale invocato:
sono test software, non benchmark DeepSeek. Suite backend completa non ripetuta,
modifica limitata a sette righe di prompt e presentazione nella chat.

[Output dei controlli](benchmarks/2026-10-13-chat-limitations-checks.txt);
log locali in `backend/data/compilation-audit/chat-limitations-*20261013.txt`.
Nessuna migrazione/reindicizzazione. Ricaricando la pagina il riquadro scompare
anche nelle conversazioni salvate; per osservare il nuovo prompt fare una nuova
domanda. Commit locale, nessun push.
