# Conferma della bozza: diagnosi e ripresa — 13 ottobre 2026

Baseline Git: `94ccdbc`; modifica backend `decc725`. Branch `prune-backend`, albero iniziale pulito.
Caso osservato dall’utente su `domanda-iscrizione.docx`, sessione
`0ce44c51adcb4b3c995f1100f71aa5e1`, conversazione `conv-1744905f5f314e7c`.

## Cosa è accaduto e cosa possiamo dimostrare

I turni205–207 conservano la sequenza: `compila` → due conferme → `1 si, 2 si`
→ proposta esplicita della bozza parziale → `si` → risposta generica di errore.
La sessione è rimasta alla versione6, WAITING_FOR_USER, dialogue.READY, domanda
`generate`, last_generation=null, last_error=null. Entrambe le conferme sono
persistite come USER (`c_soc_ing`, `c_op_ident`); non sono state perse.

La risposta finale proviene da `interrupted_compilation` in main.py: quel ramo
raggruppava GenerationError e timeout complessivo, senza pubblicare la classe
utile né conservare la traccia del planner. **L’output grezzo e l’eccezione del
tentativo originale non sono stati acquisiti e non sono recuperabili dai turni.**
Non è possibile distinguere retroattivamente JSON non valido, servizio non
disponibile, timeout o un eventuale percorso LLM diverso dal comando atteso.
Non attribuiamo quindi una causa esatta non osservata.

Verifiche in sola lettura: export_selection individua20 proposte SOURCE e2
condizioni confermate; `_selected` passa la rivalidazione corrente; tutti i20
valori superano il validatore DOCX. Nessun valore USER aggiunto al catalogo.
Un rifiuto DOCX/HTTP409 non usa quel messaggio generico: è un percorso diverso.

**Prima di cambiare codice** sono state fatte6 interpretazioni reali DeepSeek
con lo stesso checkpoint e le varianti di mention/cronologia/consenso, più una
richiesta HTTP completa in una copia privata della sessione. Tutte hanno
riconosciuto `generate`. Il replay HTTP ha già prodotto20 valori SOURCE.
**Il guasto storico non è riprodotto e non viene dichiarato risolto nella causa.**

## Modifica minima

Nessuna modifica a classificazione semantica, prompt/schema del router, SOURCE,
FORM, parser, renderer, condizioni o scelta dei valori. Nessun riconoscimento
hardcoded di `si`, `siii`, nomi, campi o documento.

Per sessioni globali con artefatto di analisi disponibile, il planner registra
localmente `artifact_path/routing/<uuid>/trace.json`:

- prompt e schema dei tentativi, massimo2 come prima;
- risposta HTTP senza header/credenziali, limitata a65.536 caratteri, output testuale del
  modello quando acquisito, model/usage e tempi;
- errori di parsing/validazione, richiesta del retry, decisione finale;
- causa dell’errore e fase `routing`/`workflow`, inclusi status HTTP se disponibili.

Le chiavi note vengono oscurate; SQLite e `.ai-key` non entrano negli artefatti.
Una indisponibilità dello storage diagnostico non impedisce la generazione.
La traccia non autorizza alcun valore e `routed` non significa DOCX generato.
La registrazione riguarda il planner; non aggiunge una chiamata LLM, un retry,
un indice o una seconda sessione. Non acquisisce retroattivamente l’errore storico
né copre il primo comando quando non esiste ancora l’artefatto di una sessione.

La risposta in chat identifica il fallimento di interpretazione e conserva
esplicitamente la domanda di bozza. Non propone più «esportare una bozza» come
soluzione all’errore sulla conferma della stessa bozza. Espone solo messaggi
controllati per formato, servizio HTTP, connessione, timeout o decisione
indisponibile: niente testo arbitrario di eccezioni/traceback nella risposta.
Le informazioni tecniche rimangono nella diagnostica locale.

Il nuovo consenso riusa versione, sessione, valori e condizioni correnti.
Non riesegue l’analisi SOURCE e non conferma automaticamente condizioni ulteriori.
Un errore non genera implicitamente una bozza e non acquisisce nuovi valori.

## Prove reali dopo la modifica

Tre replay intermedi e tre replay finali, tutti con provider reale
`deepseek-flash`, stessa sessione al checkpoint6, originale e corpus invariati.
Per ciascuno una copia privata SQLite/storage, una richiesta `/answer` e download
DOCX/report/template reali. Nessuna scrittura sulla sessione live.
Non è una nuova analisi del documento da zero e non misura copertura semantica
su documenti diversi. Il gold non entra in alcun prompt.

| Consenso finale | Intent | Chiamate/retry | Token | Tempo modello | DOCX | Valori SOURCE |
|---|---|---|---:|---:|---|---:|
| `si` | generate |1 /0|4.308|3,17s|GENERATED|20|
| `ok sì va bene` | generate |1 /0|4.312|3,19s|GENERATED|20|
| `siii` | generate |1 /0|4.309|2,40s|GENERATED|20|

I tempi misurano il modello, non l’intera latenza HTTP/rendering.
Totale acquisito, incluse diagnosi e serie intermedi:13 chiamate reali,
55.616 token. Nessuna nuova analisi SOURCE, nessun valore aziendale inserito USER.
Le parafrasi provate non costituiscono una garanzia per ogni frase possibile.

Il controllo del Word ricostruisce il testo atteso da originale e coordinate
dei singoli placeholder, senza invocare il writer per produrre l’atteso.
Tutti i paragrafi corrispondono:20 valori nelle posizioni previste, zero spostamenti,
zero modifiche agli altri spazi testuali. L’avviso di bozza viene escluso dal
confronto delle posizioni; originale identico byte per byte. Report conserva
valori SOURCE e conferme USER separate, resolved=0, ready_for_submission=false.
Nessuna dichiarazione che l’intero modulo sia stato completato.

La prima verifica del runner baseline segnalava erroneamente valori assenti:
contava il paragrafo iniziale aggiunto con l’avviso BOZZA. Conservati il check
iniziale e `word-recheck.json`; il controllo indipendente corretto passa sullo
**stesso** file prodotto prima della modifica, senza cambiare il renderer.

## Valori realmente materializzati nei tre replay finali

| Candidate | Dato | Valore scritto | Provenienza | SOURCE |
|---|---|---|---|---|
| `p14.s1` | Denominazione operatore economico | Mapi Ingegneria S.r.l. | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p15.s1` | Provincia sede operatore | BA | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p15.s2` | Telefono operatore | +39 080 000 2040 | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p16.s0` | E-mail operatore | segreteria@mapi-ingegneria.demo | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p16.s1` | PEC operatore | mapi.ingegneria@pec.demo | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p16.s2` | Partita IVA operatore | IT01234567890 | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p40.s0` | Denominazione/ragione sociale | Mapi Ingegneria S.r.l. | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p41.s0` | P. IVA società | IT01234567890 | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p41.s1` | Sede legale società | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p42.s0` | Provincia sede legale | BA | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p42.s1` | Via/Piazza sede legale | Via Giovanni Amendola | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p42.s2` | Numero civico sede legale | 172/C | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -43 |
| `p42.s3` | Telefono società | +39 080 000 2040 | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p42.s4` | E-mail società | segreteria@mapi-ingegneria.demo | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p42.s5` | PEC società | mapi.ingegneria@pec.demo | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -44 |
| `p51.s0` | Direttore Tecnico - nome e cognome | Elisa Romano | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -45 |
| `p52.s0` | Direttore Tecnico - qualifica professionale | Ingegnere | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -45 |
| `p53.s0` | Direttore Tecnico - Ordine/Collegio professionale | Ordine degli Ingegneri di Bari | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -45 |
| `p53.s2` | Direttore Tecnico - provincia ordine | Bari | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -45 |
| `p53.s4` | Direttore Tecnico - numero iscrizione | 8421 | SOURCE, conferma condizioni USER | generalita-mapi.md, chunk -45 |

## Software e limiti

Suite con provider simulati e DB/storage temporanei, distinta dalle API reali:
191 test mirati. Coperti schema rifiutato in entrambi i tentativi, HTTP503,
timeout, eccezione non pubblicabile, conservazione di sessione/conferme,
riprova sulla stessa revisione e generazione SOURCE, errore del solo storage
tracce, nessuna credenziale/header nel report, percorsi esterni rifiutati,
pausa/ripresa di emergenza e invarianti esistenti FTS5/Qdrant.

La prima suite completa:2227 passati,2 falliti. I controlli esistenti hanno
rilevato che la prima versione pubblicava testo arbitrario dell’eccezione.
Corretto con messaggi derivati dalle classi, senza indebolire quei test.
Primo test dello storage diagnostico falliva per un errore del mock che creava
un’altra cartella dentro un file; corretto il test e mantenuto l’errore reale
NotADirectoryError sullo storage delle sole tracce.

Finale: **2233 test backend passati/161,53s**,191 mirati/28,47s, Ruff
backend/runner e diff check passati. Provider simulati nei test software.
Nessuna nuova chiamata LLM nei controlli automatici.

Frontend/browser/build frontend non rieseguiti: nessuna modifica frontend,
contratto/schema API preesistente invariato, notice già disponibile. Nessuna
migrazione o reindicizzazione. Limiti di copertura/checkbox/condizioni V12
precedenti invariati. Il falso negativo storico resta non localizzato: abbiamo
corretto l’opacità diagnostica, non dimostrato di aver rimosso un guasto intermittente.

Per ritentare: riaprire **la stessa conversazione** e rispondere nuovamente alla
richiesta di bozza. Non occorre ripartire con `compila` né reinserire le conferme.
Se fallisce, conservare il nuovo turno e la traccia di routing: indicano esattamente
se e dove l’interpretazione è stata rifiutata. Nessuna riparazione manuale del DB.

Acquisizioni: `backend/data/compilation-audit/generate-consent-20261013/`.
Runner ripetibile: [replay_draft_consent.py](benchmarks/replay_draft_consent.py),
con `--session-id`, `--expected-version`, `--message`, `--output`; rifiuta una
versione live cambiata. DB privato e chiave temporanea rimossi al termine.
Hash verificati di sessione live/originale e codice invariato durante ciascun
benchmark finale; il controllo non è un fingerprint dell’intero DB del server.
[Metriche](benchmarks/2026-10-13-draft-consent.json),
[bundle completo](benchmarks/2026-10-13-draft-consent-audit.tar.gz),
[manifest](benchmarks/2026-10-13-draft-consent-manifest.json).
115 file,5.697.933 byte non compressi; SHA256 bundle
`f141c5d80e8ec5f46e364bf9ed9c411fa3406204a7c52e0a00213a8e9d79d832`.
Scan credenziale, esclusione DB/chiavi e confronto byte degli archivi passati.
