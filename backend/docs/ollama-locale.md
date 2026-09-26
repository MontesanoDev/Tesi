# Ollama in WSL

Ollama è il programma che scarica e fa girare i modelli. Installare Ollama non
scarica automaticamente un modello: sono due passaggi separati.

Nell'installazione WSL di questo computer, Ollama è installato per l'utente
`montesano`, senza sudo:

- eseguibile: `~/.local/bin/ollama`;
- librerie: `~/.local/lib/ollama`;
- servizio: `~/.config/systemd/user/ollama.service`;
- modelli scaricati: `~/.ollama/models`;
- indirizzo per Mapi: `http://127.0.0.1:11434`.

Il servizio è abilitato per la sessione utente WSL. Le funzioni cloud sono
disabilitate con `OLLAMA_NO_CLOUD=1`; il download dei modelli usa Internet,
mentre la generazione con i modelli scaricati avviene sul computer.

## Scaricare e provare un modello

Aprire un terminale Ubuntu/WSL. Come prima prova sulla RTX 3060 Laptop con
6 GB di memoria video si può usare `qwen3:4b`: il download è circa 2,5 GB.
È una scelta iniziale per contenere la memoria richiesta, non un modello
già valutato sulla compilazione dei bandi. [Scheda ufficiale](https://ollama.com/library/qwen3:4b).

```bash
ollama pull qwen3:4b
```

Il comando scarica il modello e lo conserva sul disco. Non occorre ripeterlo
ogni volta che si avvia l'app. Per vedere i modelli scaricati:

```bash
ollama list
```

Per una conversazione direttamente nel terminale:

```bash
ollama run qwen3:4b
```

Scrivere `/bye` per uscire. Per usare il modello da Mapi basta il servizio
Ollama attivo: non bisogna lasciare aperta questa conversazione.

I nomi si trovano nel [catalogo Ollama](https://ollama.com/library).
Per scaricare un altro modello, sostituire `qwen3:4b` con il suo nome e tag.
`4b` indica circa quattro miliardi di parametri, non quattro GB di RAM.
La memoria usata durante la generazione comprende anche il contesto e può
superare la dimensione del download. [Comandi Ollama](https://docs.ollama.com/cli).

## Usarlo nell'app

1. Aprire **Impostazioni generali → Modelli AI → Aggiungi modello**.
2. Scegliere **Ollama**. Non serve una chiave API.
3. Premere **Verifica collegamento e trova modelli**.
4. Scegliere `qwen3:4b` e premere **Salva modello**.
5. Nel progetto, selezionare il profilo locale dall'ingranaggio della chat.

Per questa installazione WSL l'indirizzo è `http://127.0.0.1:11434`, perché
backend e Ollama girano nella stessa WSL. L'app usa questo profilo per chat,
estrazione dei dati e compilazione dei documenti del progetto.

Ollama può anche girare su un altro computer. In quel caso, nel campo
**Indirizzo del servizio** inserire l'URL del server, ad esempio
`http://192.168.1.50:11434` oppure un dominio HTTPS. Il collegamento parte dal
backend Mapi: il server scelto deve essere raggiungibile da lì. I modelli si
scaricano su quel server e il tasto di verifica legge il suo elenco.

L'installazione WSL descritta qui ascolta solo su `127.0.0.1`. Se si vuole
usarla come server per un altro computer, occorre configurare anche l'ascolto
in rete di Ollama e l'accesso alla porta. Inserire un URL nell'app sceglie la
destinazione delle richieste; non modifica l'ascolto del server remoto.
Vedi la [configurazione di rete di Ollama](https://docs.ollama.com/faq#how-can-i-expose-ollama-on-my-network).

La finestra impostata nel profilo Ollama parte da 32.768 token e prevale sul
default del servizio. Con soli 6 GB di VRAM, un contesto ampio può richiedere
anche RAM e rendere la generazione più lenta. Ridurre la finestra riduce la
memoria richiesta, ma può escludere parte delle fonti: va verificato sul
documento concreto. Il cambio di modello non ricalcola i budget dell'app.

La prima risposta può richiedere più tempo perché Ollama carica il modello
in memoria. La chat di Mapi attende fino a 180 secondi per caricamento e
generazione; la verifica del collegamento legge soltanto l'elenco dei modelli
e non esegue questo caricamento. Se la chat supera il limite, segnala che il
tempo è scaduto: non significa necessariamente che Ollama sia spento.

## Gestire il servizio e la memoria

```bash
# Stato del servizio
systemctl --user status ollama --no-pager

# Avvio, se il servizio non è attivo
systemctl --user start ollama

# Modelli attualmente in memoria e uso di CPU/GPU
ollama ps

# Scarica il modello dalla memoria, conservandolo sul disco
ollama stop qwen3:4b
```

Il servizio si arresta quando WSL viene spenta. Per eliminare anche i file di
un modello dal disco si usa `ollama rm NOME_MODELLO`.

La verifica comprende il servizio, la lettura dei modelli da Mapi e una
generazione reale con `gemma4:e2b`. La richiesta «riassumi il bando» sul progetto
Catanzaro, con otto frammenti recuperati, ha restituito una risposta JSON
accettata dal backend in circa 17 secondi, con il modello già caricato.
La GPU viene riconosciuta tramite CUDA. È una verifica del collegamento e
della pipeline, non un benchmark della qualità dei riassunti o della compilazione.
