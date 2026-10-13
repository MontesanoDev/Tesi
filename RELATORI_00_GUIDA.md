# Compilazione Mapi — materiali da mostrare ai relatori

Copie leggibili delle acquisizioni del 13 ottobre 2026, contratto globale V12.
Le chiamate originali usano DeepSeek Flash reale; i dati aziendali sono simulati
per la demo. Non sono state eseguite nuove compilazioni per preparare questi file.

Per capire il flusso prima di aprire i JSON, leggere
[ARCHITETTURA.md](ARCHITETTURA.md): responsabilità, prompt, esempio reale 8421,
controlli, dialogo, esportazione e limiti dell'attuale motore globale V12.

## Ordine consigliato di lettura

1. [System prompt](RELATORI_02A_MINERVINO_SYSTEM_PROMPT.txt): istruzioni complete,
   estratte letteralmente dalla richiesta inviata al modello.
2. [Input LLM](RELATORI_01_MINERVINO_INPUT_LLM.json): user prompt strutturato,
   con catalogo del Word, candidate, fonti, aiuti di lettura e schema di risposta.
3. [Risposta LLM](RELATORI_03_MINERVINO_RISPOSTA_LLM.json): proposta grezza del
   modello, prima dei controlli backend.
4. [Validazione backend](RELATORI_04_MINERVINO_VALIDAZIONE_BACKEND.json): prove,
   proposte accettate/rifiutate, condizioni e motivazioni dei campi vuoti.
5. [Report dell'ultima bozza](RELATORI_05_MINERVINO_REPORT_ULTIMA_BOZZA.json):
   valori realmente scritti, posizioni e provenienza SOURCE/USER.

La [richiesta completa](RELATORI_02_MINERVINO_RICHIESTA_LLM.json) contiene
entrambi i prompt e i parametri: `messages[0].content` è il system prompt;
`messages[1].content` è lo user prompt serializzato come stringa JSON.
Il file01 espone lo stesso user prompt in forma direttamente leggibile.

## Compilazione reale: domanda di iscrizione di Minervino

Sessione `a067b0abf83f4d948137728669879604`, analisi
`e8ad0f46c3b34157bbe6c9988e1341f8`: 267 candidate strutturali e51 frammenti SOURCE.
L'ultima esportazione `aca0a0dd970343dda73b2b2caba3344f` scrive20 posizioni da
fonti aziendali. Più posizioni possono riutilizzare lo stesso fatto.

Il report05 riguarda questa ultima esportazione. Il DOCX utente
`domanda-iscrizione.compilato(2).docx`, esaminato nel
[controllo documentale](docs/minervino-output-2-2026-10-13.md), appartiene alla
precedente esportazione `6cb97f7bc2784517919f3b99e4d021cc`: condividono la stessa
analisi globale. Una nuova esportazione non implica una nuova risposta LLM.

È una bozza parziale: rimangono il comune Bari omesso nella sede iniziale,
l'indirizzo ridondante e una giunzione senza spazio nell'Ordine professionale.
I limiti delle checkbox e le motivazioni respinte restano visibili negli audit.
Un dato FORM descrive una richiesta; solo SOURCE sostiene un valore documentato.
Una conferma USER resta distinta dalla prova SOURCE. `GROUNDED_PROPOSAL` e
`GENERATED` non certificano completezza o ammissibilità dell'intera domanda.

## Esperimenti separati dalla compilazione della chat

| Esperimento V12 | Input | Risposta originale |
|---|---|---|
| Benchmark congelato Labirinto, serie finale02/prova02 | [Input](RELATORI_06_BENCHMARK_LABIRINTO_INPUT.json) | [Risposta](RELATORI_07_BENCHMARK_LABIRINTO_RISPOSTA_LLM.json) |
| Benchmark Minervino, serie finale02/prova02 | [Input](RELATORI_08_BENCHMARK_MINERVINO_INPUT.json) | [Risposta](RELATORI_09_BENCHMARK_MINERVINO_RISPOSTA_LLM.json) |

Sono le specifiche prove già indicate nella conversazione. I file non
sostituiscono la serie completa: risultati, variabilità e fallimenti sono nel
[report degli esperimenti V12](docs/compilazione-esiti-vuoti-2026-10-13.md).
La fixture Labirinto ha un [gold indipendente](demo-documents/benchmark-compilazione/v1/gold.json),
escluso dai prompt. Minervino non ha un gold completo della candidatura.

## Fedeltà delle copie

I JSON sono stati soltanto riformattati con indentazione, senza cambiare valori,
identificativi, motivazioni, errori o risultati. Le risposte originali `.txt`
contengono JSON e sono qui salvate con estensione `.json`.

[Provenienza e hash](RELATORI_10_PROVENIENZA_FILE.json) conserva percorsi originali,
hash prima/dopo e verifica di equivalenza dei JSON. Le chiavi API non sono incluse.
Originali, database e sessioni rimangono nei loro percorsi; questi sono snapshot
per la presentazione, non file aggiornati automaticamente dalle prossime prove.
