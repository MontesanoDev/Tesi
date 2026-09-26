**Compilazione unica con Gemma locale**

Il percorso Word usa una sola richiesta per tutti i campi candidati. La prova
reale su Catanzaro ha raggiunto Ollama e ricevuto una risposta completa, ma
non ha prodotto una bozza: il JSON non rispetta lo schema richiesto.

**Configurazione e risultato**

| Voce | Valore |
| --- | --- |
| Modulo | `demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx` |
| Progetto | `catanzaro-direzione-lavori-e-sicurezza` |
| Provider e modello | Ollama locale, `gemma4:e2b` |
| Endpoint | `http://127.0.0.1:11434` |
| Prompt | `docx-fields-v12-single-call` |
| Posizioni candidate | 279: 265 celle e 14 segnaposti |
| Indicazioni aggiuntive | Nessuna |
| Fonti inviate | 92 frammenti su 271, per 106.687 caratteri |
| Finestra di contesto del profilo | 131.072 token |
| Massimo output richiesto | 32.768 token |
| Tempo massimo di attesa | 1.800 secondi |
| Richieste effettive | 1, senza correzioni o nuovi tentativi |
| Tempo misurato | 89,78 secondi |
| Token input dichiarati da Ollama | 68.878 |
| Token output dichiarati da Ollama | 3.344 |
| Token totali | 72.222 |
| Termine della generazione | `done=true`, `done_reason=stop` |
| Bozza salvata | Nessuna |

Il profilo Ollama era impostato a 32.768 token ed è stato portato a 131.072,
capacità dichiarata dal modello installato. La richiesta effettiva contiene
`num_ctx=131072`, `num_predict=32768`, `temperature=0.1`, `format=json`,
`think=false` e `stream=false`. Non sono state effettuate chiamate cloud.

Il limite di output e il timeout sono massimali scelti per questa prova:
consentono una risposta più lunga e un'esecuzione locale lenta. Non derivano
da un'ottimizzazione sperimentale. Gemma si è fermato molto prima di entrambi.

**Cosa ha sbagliato il modello**

La risposta è un JSON leggibile con `fields` e `warnings`, ma contiene solo
19 proposte. Tutte hanno `status=proposed`.

| Problema osservato | Conseguenza |
| --- | --- |
| 10 proposte hanno valore vuoto e una citazione con `quote=""`. | Pydantic rifiuta l'intera risposta: la citazione deve contenere testo. Un dato mancante andava indicato con `missing`, `value=null` ed `evidence=[]`. |
| 8 proposte indicano ID estranei alle posizioni candidate scrivibili. | Anche eliminando il primo problema, questi ID farebbero interrompere la compilazione. |
| 18 proposte usano coordinate di celle come `source_id`. | Le coordinate del modulo non sono identificatori delle fonti inviate e non valgono come evidenze. |
| In `t0.r0.c1`, etichettato nel modulo «Il/La sottoscritto/a», propone `Mapi Ingegneria S.r.l.`. | Confusione tra persona e società. La proposta, verificata isolatamente con il validatore esistente, supera i controlli tecnici perché cita un dato aziendale autentico. |

L'ultima verifica è una diagnosi offline sulla risposta ricevuta: non è stata
eseguita un'altra chiamata e non è stato scritto un Word con quella proposta.
Nell'esecuzione completa, la validazione dello schema ha interrotto il processo
prima dei controlli sugli ID e della scrittura.

Il risultato mostra sia errori nel contratto JSON sia un errore semantico.
`format=json` richiede JSON, ma in questa integrazione non impone al generatore
lo schema Pydantic dei campi. Una risposta terminata regolarmente non garantisce
che il modello abbia esaminato tutte le posizioni o rispettato le istruzioni.

**Cosa cambia nel backend**

```text
DOCX → parser → tutte le posizioni candidate
                         +
           fonti selezionate e indicazioni
                         ↓
                una richiesta al modello
                         ↓
           JSON → schema → ID → evidenze
                         ↓
         valori ammessi → copia Word + report
```

`compile_document()` usa `compile_fields_once()`. I budget delle fonti, il
parser, i controlli sulle evidenze e il writer restano gli stessi. Non vengono
richiamate correzioni, divisioni della richiesta o un altro provider. Una
risposta troncata o strutturalmente errata termina senza bozza; una proposta
con evidenze non valide lascia vuoto il relativo campo se il resto del
contratto è valido.

La precedente funzione a gruppi rimane disponibile per confronti espliciti
nel codice, tramite `strategy="batches"`. L'interfaccia usa sempre la richiesta
unica. Il report conserva i vecchi contatori per compatibilità e aggiunge
`execution.strategy=single_call`.

**Come leggere il consumo**

Il contesto ora viene inviato una volta. Nella precedente prova Catanzaro con
DeepSeek erano state effettuate nove richieste, per 642.207 token complessivi.
Quel confronto non isola l'effetto della strategia: cambiano modello, istruzioni,
fonti disponibili e risposta prodotta. Qui il modello ha restituito pochi campi
e la compilazione è fallita. I 72.222 token non dimostrano un risparmio a parità
di qualità.

Questa prova non dimostra che la chiamata unica sia inadatta in generale, né
che Gemma non possa compilare moduli più semplici. Dimostra che questa
combinazione di modello, contesto e prompt non ha completato il caso Catanzaro.
Per confrontare le strategie serve mantenere uguali modello, fonti e indicazioni
e valutare i valori scritti oltre a tempo e token.

**Verifiche e riproduzione**

La suite backend passa: **529 test**. I casi aggiunti verificano che tutti i
279 candidati arrivino nella stessa richiesta, che una risposta valida produca
una sola bozza e che troncamenti, timeout, citazioni vuote e ID non validi non
provochino richieste ulteriori o salvataggi parziali. Restano i test della
strategia precedente e quelli su fonti, provider, firme, email e numeri.

La prova è ripetibile dalla directory `backend`, dopo aver selezionato un
profilo Ollama nel progetto:

```bash
.venv/bin/python -m scripts.compile_docx_ollama \
  --project-id catanzaro-direzione-lavori-e-sicurezza \
  --template ../demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx
```

Lo script rifiuta profili di altri provider. `--instructions-file` permette
di specificare le indicazioni; `--save-in-project` salva nell'app una bozza
solo se l'elaborazione riesce. Le richieste, la risposta grezza e le misure
restano in `backend/data/single-call-gemma/`, esclusa da Git.

I file di questa esecuzione sono nella
[cartella della prova](backend/data/single-call-gemma/20260926T103422Z/):
`inputs.json`, `request.json`, `provider-request.json`, `provider-response.txt`,
`provider-metrics.json` e `result.json`. Lo script conserva gli errori come
risultati; non cambia automaticamente il modello per ottenere una bozza.
