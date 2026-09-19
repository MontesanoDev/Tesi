# Seconda prova esplorativa di compilazione: Minervino di Lecce

Data: **18 settembre 2026**. Modello restituito dal provider: **deepseek-flash**.

Questo documento conserva la prova v5. Per le correzioni successive e una nuova
compilazione con gli stessi input: [verifica campi logici v6](verifica-campi-logici.md).

**Esito:** il Word viene prodotto al primo tentativo, ma richiede correzioni.
La prova conferma errori di applicabilita' gia' osservati a Catanzaro e mette
in evidenza un problema di segmentazione dei segnaposti nei paragrafi.
Non e' un benchmark, una misura di accuratezza o una candidatura pronta.

## Caso e condizioni

[Avviso ufficiale del Comune di Minervino di Lecce](https://comuneminervinole.tuttogare.it/albo_fornitori/dettaglio.php?codice=1)
per l'elenco relativo a servizi di ingegneria e architettura, pubblicato nel 2025.
Si prova il modulo di domanda, non tutti gli allegati necessari all'iscrizione.

- [Avviso PDF](demo-documents/bandi/minervino-elenco-sia/originali/avviso.pdf) e
  [domanda DOCX nativa](demo-documents/bandi/minervino-elenco-sia/originali/domanda-iscrizione.docx)
  scaricati dal portale, con hash corrispondenti a quelli ufficiali.
- Stessa [scheda Mapi simulata](demo-documents/generalita-mapi.md) della prova Catanzaro.
- [Indicazioni fissate prima della chiamata](demo-documents/bandi/minervino-elenco-sia/istruzioni.txt):
  societa' di ingegneria singola, sottoscrittore Luca Ferri, anagrafica iniziale
  e dati societari/direttore tecnico nel ramo pertinente. Altri rami, soci non
  documentati, scelte, attestazioni, firme e date esclusi.
- Stessi compilatore, system prompt v5 e configurazione DeepSeek della precedente
  prova, verificati con hash. Nessuna modifica del backend o adattamento del DOCX.
- Vera API FastAPI con database e storage temporanei; nessun progetto o documento
  dell'app dell'utente modificato. Nessuna fonte Catanzaro, nessuna estrazione facts.
- Una sola compilazione completa. Nessun rilancio per ottenere un esito migliore,
  nessuna mappa di campi attesi inviata al modello.

## Numeri descrittivi

| Osservazione | Risultato |
|---|---:|
| Posizioni candidate del parser | 281: 67 celle e 214 segnaposti nei paragrafi |
| Paragrafi complessi esclusi dalla modifica | 15 |
| Frammenti disponibili / inviati | 45 / 45, nessun taglio per budget |
| Caratteri delle fonti selezionate | 50.960, inclusa sovrapposizione dei chunk |
| Chiamate | 9, tutte completate |
| Token totali dichiarati, input + output | 430.061 |
| Tempo complessivo | 84,83 secondi |
| Scritture effettive | 37 segnaposti in 13 paragrafi; nessuna cella di tabella |
| Classificazioni del modello | 37 proposti, 66 mancanti, 74 da verificare, 104 non applicabili |
| Proposte respinte / correzioni automatiche | 0 / 0 |
| Scritture in rami espressamente esclusi | 12 |

**37 scritture non significa 37 campi logici completati correttamente.**
Una singola e-mail e' stata suddivisa in piu' proposte. Anche i 140 elementi
irrisolti non corrispondono necessariamente ad altrettanti dati richiesti.

## Cosa funziona

L'anagrafica iniziale contiene il sottoscrittore scelto, la carica, Mapi come
operatore economico, Bari come sede, telefono, e-mail, PEC e identificativo fiscale
della fixture. In questo primo blocco e-mail e PEC sono riportate integralmente.

Nel ramo societario riconosce Elisa Romano come direttore tecnico, con qualifica,
ordine professionale e numero di iscrizione presenti nella fonte. Non la
sostituisce con il sottoscrittore e non la inserisce come socio.

Nascita, residenza e CF personali non vengono inventati; il REA non viene usato
per riempire il numero di iscrizione camerale. Le quattro tabelle delle scelte
restano invariate. Nessuna firma o data di sottoscrizione viene inserita.

L'identificativo `IT01234567890` e i recapiti `.demo` sono volutamente fittizi:
copiarli dalla scheda non equivale a validarli per un uso amministrativo.

## Problemi osservati nel Word

### 1. Dodici scritture in rami non applicabili

| Posizioni XML | Ramo | Scritture |
|---|---|---:|
| `p24.s0` - `p24.s2` | Rappresentante di studio professionale associato | 3 parti di PEC |
| `p37.s3`, `p37.s4`, `p37.s6` - `p37.s8`, `p37.s10` - `p37.s12` | Professionista appartenente a studio associato | Civico, telefono, 3 parti e-mail, 3 parti PEC |
| `p38.s0` | Rappresentante legale dello studio associato | Luca Ferri |

Sono rami esclusi dalle indicazioni. Le citazioni valide non impediscono di
collocarvi dati aziendali. All'interno dello stesso ramo alcuni campi sono
`not_applicable` e altri vengono compilati: manca una decisione coerente a
livello di sezione. Gli altri 25 inserimenti sono nel perimetro ammesso, ma
alcuni presentano i problemi strutturali descritti sotto.

### 2. E-mail e PEC ricostruite male

Il modulo alterna puntini normali ed ellissi. Il parser interpreta porzioni
della stessa riga come campi distinti e il modello le tratta come componenti
separate dell'indirizzo. Nel Word effettivo compaiono:

| Dove | Testo risultante | Valore nella fonte |
|---|---|---|
| PEC studio associato, `p24` | `mapi.ingegneria.pec..demo` | `mapi.ingegneria@pec.demo` |
| E-mail ramo societario, `p42` | `segreteria...mapi-ingegneria.demo` | `segreteria@mapi-ingegneria.demo` |
| PEC ramo societario, `p42` | `mapi.ingegneria.pec..demo...` seguito da ellissi residue | `mapi.ingegneria@pec.demo` |

Non e' un problema di fonti assenti: le stesse e-mail/PEC sono compilate bene
nel paragrafo iniziale `p16`. Frammenti come `segreteria`, `pec` e `demo` compaiono
letteralmente nelle citazioni, quindi superano i controlli per singolo slot.
Il controllo attuale non verifica l'indirizzo logico ricomposto nel documento.

### 3. Marcatori residui e separatori consumati

- `p40`: la ragione sociale e' preceduta da ellissi lasciate vuote. Il modello
  interpreta un pezzo della linea come un "prefisso" mancante che il modulo non chiede.
- `p42`: compaiono `provBA` e `n172/C`, senza il separatore originario, oltre a
  puntini residui accanto al telefono.
- `p53`: il nome dell'ordine e' seguito da una lunga linea puntinata residua;
  un secondo pezzo dello stesso campo viene classificato come dato mancante.

Questi problemi sono osservabili nel testo XML del Word, senza bisogno di
dedurli dal solo report. Il writer ha eseguito le sostituzioni autorizzate;
e' la suddivisione in campi logici, insieme all'interpretazione del modello,
a essere inadeguata per alcune righe.

### 4. Avvisi non sempre coerenti con le scritture

Un avviso generato dal modello sostiene che i rami associati siano stati
trattati come non applicabili, ma il Word contiene gli inserimenti sopra elencati.
Gli avvisi testuali LLM non vanno confusi con verifiche eseguite dal backend.

## Controlli sul file effettivo

Superati: corrispondenza di tutte le scritture con il report, sostituzione dei
soli intervalli autorizzati, altri paragrafi invariati nel loro XML, quattro
tabelle invariate, 15 paragrafi esclusi invariati, firma non compilata e avviso
di bozza presente. Cambia solo `word/document.xml`; tutte le altre parti ZIP
rimangono identiche. Hash dell'originale e dell'output coerenti con il report.

Non e' disponibile un rendering Word/LibreOffice in questo ambiente: non sono
state verificate visivamente paginazione e resa finale. I controlli strutturali
non rendono corretti i recapiti malformati o i rami compilati impropriamente.

## Cosa aggiunge rispetto a Catanzaro

| Aspetto | Catanzaro, ultima prova | Minervino |
|---|---|---|
| Modulo | DOCX convertito, compilazione osservata in celle | DOCX nativo, compilazione osservata nei paragrafi |
| Copertura delle fonti | 86/185 frammenti | 45/45 frammenti |
| Output | Prodotto, da correggere | Prodotto, da correggere |
| Applicabilita' | 6 scritture fuori perimetro | 12 scritture nei rami associati esclusi |
| Nuova evidenza | Citazioni autentiche non garantiscono il ramo | Neppure garantiscono la correttezza del valore ricomposto tra piu' slot |

Non e' un confronto di accuratezza o velocita': moduli, dati richiesti, corpus
e granularita' dei segnaposti sono diversi, con una sola esecuzione per questa
prova. Non ci sono baseline umana, qrels, misure di tempo di revisione o confronto
tra modelli. La conclusione utile e' qualitativa: il flusso si estende a un altro
modulo, ma il parser dei campi logici e l'applicabilita' sono limiti riprodotti.

Non e' stata implementata alcuna correzione durante questa prova. Un eventuale
intervento futuro sui segnaposti e sui controlli dei valori ricomposti andrebbe
provato su piu' moduli, non con regole legate alle coordinate di Minervino.

## Materiale consultabile

- [Word prodotto, da correggere](backend/data/compilation-audit/20260918-101058-minervino-v5/output/bozza.docx).
- [Report JSON](backend/data/compilation-audit/20260918-101058-minervino-v5/output/report.json).
- [Esito e consumi](backend/data/compilation-audit/20260918-101058-minervino-v5/result.json).
- [Controlli offline ed estratti dei paragrafi reali](backend/data/compilation-audit/20260918-101058-minervino-v5/offline-analysis.json).
- [Input e hash](backend/data/compilation-audit/20260918-101058-minervino-v5/inputs.json).
- [Pacchetto degli originali ufficiali](demo-documents/bandi/minervino-elenco-sia/README.md).

Prompt, risposte e tempi per chiamata sono nella stessa cartella di audit,
sotto `backend/data/`, gia' esclusa da Git. Nessuna regola di ignore aggiunta,
nessun commit e nessun invio al portale.
