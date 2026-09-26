# Backend Mapi RAG

FastAPI, SQLite/FTS5 e generazione tramite OpenAI, Claude, Gemini, DeepSeek,
Mistral, Grok, Groq, OpenRouter, Ollama o API compatibili.

I modelli e le chiavi si configurano in **Impostazioni generali → Modelli AI**.
Dal progetto si sceglie quale configurazione usare per chat, estrazione e
compilazione. Non è necessario inserire le chiavi nel `.env`.
Dettagli, gestione delle credenziali e limiti: [Modelli AI](docs/modelli-ai.md).

Le fonti PDF, TXT e Markdown del contesto progetto possono essere eliminate con
`DELETE /api/projects/{project_id}/files/{file_id}` (204). La rimozione riguarda
il file caricato, i suoi frammenti e le relative righe FTS5; gli ID di un altro
progetto e gli artefatti di lavoro non sono cancellabili da questo endpoint.
Le evidenze della chat vengono ricontrollate prima del riutilizzo nei follow-up.
Conversazioni, dati gia estratti o inseriti e compilazioni salvate non vengono
riscritti: sono copie separate. Se contengono informazioni della fonte errata,
vanno aggiornati separatamente; eliminare il PDF non ritratta quei contenuti.

Per la gestione unificata delle estrazioni e dei dati inseriti:
[Dati del progetto](docs/dati-progetto.md).

Per il nuovo percorso di compilazione dei moduli Word, API e comando di prova:
[Compilazione assistita DOCX](docs/compilazione-docx.md).

Il template testuale (.md/.txt) parte vuoto: il modello va caricato o creato e
salvato prima della generazione. All'avvio, i vecchi scheletri dimostrativi
vengono rimossi solo se contenuto e stato coincidono con quelli predefiniti.
Modelli personalizzati, modelli salvati dall'utente e compilazioni esistenti
rimangono invariati. Il percorso Word non cambia.

Per creare nell'app i progetti didattici **Catanzaro - Direzione lavori e sicurezza**
e **Minervino di Lecce - Elenco SIA**, dalla directory `backend/`:

```bash
.venv/bin/python -m scripts.create_tender_projects
```

Il comando usa il database configurato, crea i normali documenti di lavoro del
progetto e può essere ripetuto senza duplicare i progetti o sovrascriverne titolo
e descrizione. I documenti dei bandi e i modelli Word restano disponibili in
`demo-documents/bandi/` per il caricamento; il comando non avvia generazioni IA.
