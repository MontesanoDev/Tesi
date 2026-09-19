# Prova reale di compilazione con Generalita' Mapi

Data: **17 settembre 2026**. Modello restituito dal provider: **deepseek-flash**.

Questo documento conserva la prima prova fallita con prompt v4 e, in fondo,
il [seguito con prompt v5](#seguito-con-prompt-v5-17-settembre-2026). Nell'ultima
prova il Word viene prodotto, ma sono ancora presenti errori di applicabilita'.

## Esito della prima prova, prompt v4

**Prova end-to-end fallita: nessun Word prodotto.** Il backend ha restituito 502 al primo gruppo di campi, con il messaggio:

> Il modello cita una fonte o un passaggio non fornito

Non considero quindi il flusso attuale sufficientemente affidabile per una demo live senza una precedente prova completa. Il fallimento non dimostra che il modello sia generalmente inadatto: individua problemi concreti nella risposta e nei controlli applicativi. I test automatici superati non avevano dimostrato questa affidabilita' end-to-end.

## Condizioni della prova

- Modulo reale: `demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx`.
- Fonti di progetto: bando e disciplinare del caso Catanzaro.
- Company KB: nuova [generalita-mapi.md](demo-documents/generalita-mapi.md), non il vecchio profilo di poche righe.
- Nessuna estrazione preventiva dei Call Facts; il compilatore puo' usare direttamente le fonti.
- Indicazioni esplicite: prova didattica, partecipazione singola, ramo societa' di ingegneria, sottoscrittore Luca Ferri; nessuna firma, dichiarazione o compilazione di rami alternativi.
- Database e storage temporanei, separati da quelli dell'applicazione. Nessuna modifica ai progetti dell'utente.
- Nessuna mappa manuale di campi o valori attesi inviata al modello. La mappa del caso e' stata consultata solo per la valutazione.

Il system prompt, il parser e i controlli di produzione non sono stati modificati. Lo script di prova e' stato esteso con `--company-file` per scegliere la nuova fonte aziendale. La descrizione della prova nelle indicazioni utente fa riferimento alle fonti aziendali simulate, non piu' specificamente alla visura PDF.

## Numeri osservati

| Misura | Risultato |
|---|---|
| Chiamate reali DeepSeek | 1; nessun rilancio dopo il fallimento |
| Tempo richiesta al modello | 9,92 secondi |
| Tempo della prova, inclusa preparazione | 12,08 secondi |
| Token complessivi dichiarati dal provider | 73.243, input e output insieme |
| Dimensione del prompt utente | 219.653 caratteri, inclusi fonti e catalogo del modulo |
| Frammenti selezionati / disponibili | 86 / 185 |
| Frammenti aziendali inclusi | Tutti e 10 i frammenti della nuova scheda |
| Posizioni candidate del modulo | 279 |
| Posizioni inviate come scrivibili nel primo gruppo | 32 |
| Posizioni classificate dal modello nel gruppo | 32 |
| Valori proposti nel gruppo | 9 |
| Documenti compilati e salvati | 0 |

Le fonti di progetto sono state selezionate parzialmente; quelle aziendali erano tutte disponibili. I problemi qui descritti non dipendono dalla mancata inclusione della scheda Mapi. I restanti 247 candidati non sono stati valutati dal modello in questa prova.

## Problemi riscontrati

### 1. Provenienza errata per un nominativo corretto

Per `t0.r0.c1`, "Il/La sottoscritto/a", il modello propone `Ing. Luca Ferri` con due citazioni:

- `company:3`: `Nominativo completo: Ing. Luca Ferri.` Questa citazione e' presente nella fonte.
- `project:1`: `sottoscrittore Luca Ferri`. Questa citazione **non** e' presente nella fonte indicata.

`project:1` corrisponde al documento `project-facts.md` iniziale, contenente solo titolo e descrizione del progetto. Il sottoscrittore era invece indicato nelle istruzioni utente, esterne al catalogo delle fonti citabili.

**Diagnosi:** non e' un nome inventato, ma una falsa attribuzione documentale. Il modello ha violato il contratto di citazione. Il backend lo ha correttamente rilevato, ma l'attuale gestione interrompe tutto il documento per quell'errore locale.

### 2. Compilazione di un ramo non applicabile

Il modello propone di nuovo `Ing. Luca Ferri` in `t9.r0.c1`. L'intestazione della tabella, presente nel contesto, e':

> 5.a)dati identificativi da compilare in caso di PROFESSIONISTA SINGOLO

Le istruzioni avevano selezionato il ramo **5.d, societa' di ingegneria**. Riportare il sottoscrittore nel ramo del professionista singolo e' quindi un errore di applicabilita', non un successo perche' il nome e' corretto.

**Diagnosi:** errore semantico del modello. Il controllo applicativo attuale accetterebbe isolatamente questa proposta: campo scrivibile e citazione valida non dimostrano che la sezione sia pertinente. Il vincolo sui rami e' affidato al prompt, non a uno stato strutturato delle sezioni applicabili.

Questo e' piu' importante del semplice conteggio dei campi compilati.

### 3. Forma giuridica equivalente bloccata dagli accenti

- Fonte: `Societa a responsabilita limitata`.
- Valore proposto: `Società a responsabilità limitata`.

Il confronto corrente normalizza spazi e maiuscole, non gli accenti. Il valore non risulta contenuto letteralmente nella citazione e viene declassato a `needs_review`.

**Diagnosi:** proposta semanticamente corretta, ma non conforme al requisito di copia letterale. Per questo caso il controllo e' troppo restrittivo dal punto di vista dell'utilita'. Non e' un'allucinazione. Un'eventuale correzione dovra' essere circoscritta: non bisogna rendere permissivi anche confronti su numeri, date o identificativi.

## Che cosa ha fatto correttamente

Nel primo gruppo il modello ha recuperato ragione sociale, carica, sede e telefono dai dati aziendali. Non ha sostituito questi dati con quelli dell'amministrazione appaltante.

Ha lasciato mancanti nascita e codice fiscale personali, ha riconosciuto la coincidenza delle sedi e non ha inventato importi di servizi pregressi. Ha segnalato sia la natura simulata delle fonti sia il disallineamento temporale rispetto alla gara.

Ha anche proposto `IT01234567890` come identificativo fiscale aziendale, dichiarandolo fittizio. Questo e' coerente con la modalita' demo ammessa dal prompt, **non** una validazione fiscale: quel valore non e' utilizzabile in una pratica reale.

## Controllo offline dei singoli campi

Ho rieseguito il validatore sui singoli elementi della risposta gia' ricevuta, senza altre chiamate API e senza produrre Word:

- 1 proposta provoca errore per la falsa citazione.
- 1 proposta viene bloccata dal confronto letterale sugli accenti.
- 7 proposte superano i controlli tecnici isolati, **compresa quella nel ramo sbagliato**.

Questi numeri non descrivono un documento parzialmente salvato: la compilazione reale e' fallita prima del salvataggio. Non vanno trasformati in una percentuale di accuratezza: il campione e' piccolo, alcuni dati sono ripetuti o volutamente fittizi e il modulo non e' stato percorso integralmente.

## Conclusione e priorita'

La scheda aziendale piu' completa aiuta: il modello trova i dati. **I punti deboli ora dimostrati sono la provenienza delle istruzioni, l'applicabilita' delle sezioni e la gestione degli errori locali.** Non c'e' evidenza che cambiare provider, database o tecnica di retrieval risolva questi problemi da solo.

Prima di una demo live affidabile valuterei:

1. Una distinzione esplicita e tracciabile tra istruzioni/scelte dell'utente e fonti documentali, senza attribuire citazioni a documenti che non le contengono.
2. Un controllo dell'applicabilita' dei rami, non soltanto della scrivibilita' fisica delle celle.
3. La possibilita' di bloccare e segnalare una proposta locale non valida senza perdere l'intero documento, mantenendo bloccanti gli errori strutturali.
4. La gestione controllata di varianti testuali equivalenti, senza indebolire i controlli sugli identificativi.

Queste modifiche **non sono state applicate durante la prova**. Non e' stato cercato un risultato favorevole rilanciando il modello piu' volte.

## Materiale della prova

Le tracce sono in [backend/data/compilation-audit/20260917-155339](backend/data/compilation-audit/20260917-155339), cartella gia' esclusa da Git tramite la regola esistente per `backend/data/`:

- [Input e hash dei file](backend/data/compilation-audit/20260917-155339/inputs.json).
- [Prompt utente effettivo](backend/data/compilation-audit/20260917-155339/batch-01.prompt.json).
- [Risposta effettiva del modello](backend/data/compilation-audit/20260917-155339/batch-01.response.json).
- [Tempi e token](backend/data/compilation-audit/20260917-155339/batch-01.meta.json).
- [Esito end-to-end](backend/data/compilation-audit/20260917-155339/result.json).
- [Analisi offline per campo](backend/data/compilation-audit/20260917-155339/offline-analysis.json).

Per ripetere il percorso end-to-end da `backend`, con **nuove chiamate API a consumo** e una directory di output non ancora esistente:

```bash
.venv/bin/python -m scripts.compile_docx_demo --live \
  --company-file ../demo-documents/generalita-mapi.md \
  --output data/docx-demo/prova-generalita-mapi
```

Il comando salva Word, originale e report soltanto se la compilazione termina. Il salvataggio diagnostico dei prompt e delle risposte di questa prova e' stato effettuato separatamente dal test harness; non e' una funzione del compilatore di produzione.

## Seguito con prompt v5, 17 settembre 2026

Sono stati implementati tre interventi generali, senza mappature Catanzaro nel
codice di produzione:

1. Indicazioni citabili con `user:instructions`, distinguibili dai documenti.
2. Errori di evidenza circoscritti al campo, con proposta conservata e nessuna scrittura.
3. Un solo tentativo di correzione per le proposte ammesse, senza rigenerare quelle gia' accettate.

Durante la verifica reale sono emerse due rigidita' di parsing, riprodotte e
corrette con test: `evidence` omesso per campi non applicabili senza valore, ed
etichette vuote di celle lasciate vuote. Ora il parser usa rispettivamente una
lista vuota e la coordinata del campo, **soltanto per campi non proposti e senza
valore**. Non completa valori o fonti e non accetta ID ignoti, JSON troncato,
tipi errati o scritture fuori gruppo.

Sono state eseguite tre prove nuove, senza cancellare gli esiti sfavorevoli:

| Prova | Chiamate | Token input + output | Tempo complessivo | Esito |
|---|---:|---:|---:|---|
| v5 iniziale | 5 | 371.195 | 52,24 s | Fallita: lista delle citazioni omessa in 32 campi non applicabili. |
| Dopo normalizzazione delle citazioni vuote | 3 | 222.023 | 30,57 s | Fallita: etichette vuote in 10 celle senza valore da scrivere. |
| Dopo normalizzazione dei metadati non scrivibili | 9 | 665.331 | 83,95 s | Word, originale e report prodotti. |

Le prove usano gli stessi file e indicazioni del caso iniziale, database
temporanei e nuove chiamate complete. Non sono replay o risultati composti da
gruppi scelti tra esecuzioni. Complessivamente queste tre prove hanno consumato
1.258.549 token. I test sintetici non consumano API.

### Ultimo risultato: successo tecnico, non amministrativo

- 279 posizioni classificate; 21 valori scritti, 134 `missing`, 1 `needs_review`,
  123 `not_applicable`. I 135 irrisolti non sono necessariamente altrettanti dati
  realmente necessari: la classificazione include celle potenzialmente decorative.
- 86/185 frammenti selezionati, inclusi tutti i 10 frammenti aziendali.
- Nessuna proposta bloccata dalle evidenze nell'ultima esecuzione; **nessuna
  correzione automatica attivata**. Il ramo di correzione e' verificato nei test
  controllati, non dimostrato da questa singola esecuzione live.
- Per il sottoscrittore, il report cita correttamente sia il nome nella fonte
  aziendale sia la scelta nelle indicazioni utente, senza inventare un frammento
  documentale per queste ultime.
- La forma giuridica e' copiata con la grafia letterale della fonte; non e'
  stato introdotto un confronto approssimativo per farla passare.

**Sei scritture restano fuori dal perimetro richiesto** (prima tabella e sezione
5.d), nonostante i valori compaiano nelle fonti:

| Coordinate | Errore osservato |
|---|---|
| `t9.r0.c1` | Sottoscrittore inserito nel ramo 5.a, professionista singolo. |
| `t40.r4.c1`, `t40.r4.c3` | Forma giuridica e sede inserite nel ramo 5.h, consorziata esecutrice. |
| `t41.r1.c0`, `t41.r1.c4`, `t44.r1.c0` | Dati di persone/cariche inseriti nelle dichiarazioni successive, fuori dal perimetro richiesto. |

In particolare, la carica di amministratore in un campo "Poteri conferiti /
qualifica" non documenta i poteri specifici. Anche alcuni avvisi generati dal
modello affermano di non aver compilato altri rami, in contrasto con le
scritture effettive: **gli avvisi LLM non sono attestazioni dei controlli**.

La localizzazione di questi sei errori e' stata usata solo per valutare il
risultato, mai per decidere le scritture in produzione. Non si ricava un tasso
di accuratezza generalizzabile da questa prova. Resta necessario intervenire
sull'applicabilita' e sul perimetro delle sezioni, con un approccio generico da
progettare separatamente: la riparazione delle citazioni non risolve quel problema.

### Integrita' del file e verifiche

Controlli offline superati sul Word effettivamente prodotto:

- Tutti i 21 valori corrispondono al report e sono in celle candidate.
- Tutte le altre celle sono invariate nel loro XML, incluse quelle prestampate.
- Cambia soltanto `word/document.xml`; le altre parti del pacchetto sono identiche.
- Testo prestampato del corpo conservato, avviso di bozza presente, nessuna
  posizione riconosciuta dal parser come firma compilata; hash coerenti.
- Nessun rendering Word/LibreOffice disponibile in questo ambiente: non e'
  stata verificata visivamente l'impaginazione finale.

Suite attuale: **278 test backend**, **78 test frontend**, **12 test browser
DOCX su desktop/mobile** superati; TypeScript, build Vite e controlli statici
superati. Questi test verificano contratti e comportamenti del codice, non
l'accuratezza semantica su bandi arbitrari.

### Tracce e file

- [Prima prova v5 fallita](backend/data/compilation-audit/20260917-163102-v5/result.json).
- [Seconda prova v5 fallita](backend/data/compilation-audit/20260917-163637-v5-parser-fix/result.json).
- [Esito dell'ultima prova](backend/data/compilation-audit/20260917-163846-v5-metadata-fix/result.json).
- [Word prodotto, con errori da correggere](backend/data/compilation-audit/20260917-163846-v5-metadata-fix/output/bozza.docx).
- [Report completo](backend/data/compilation-audit/20260917-163846-v5-metadata-fix/output/report.json).
- [Verifiche offline](backend/data/compilation-audit/20260917-163846-v5-metadata-fix/offline-analysis.json).

Ogni cartella conserva prompt effettivi, risposte, token e tempi; le ultime due
includono anche l'hash del compilatore e del system prompt. Restano sotto
`backend/data/`, gia' esclusa da Git, senza nuove regole di ignore. I progetti e
la KB dell'applicazione non sono stati modificati dalle prove isolate.
