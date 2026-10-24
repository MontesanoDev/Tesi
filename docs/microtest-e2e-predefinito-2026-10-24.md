# Micro-test E2E della Compilazione DOCX predefinita — Cesano (24 ottobre 2026)

**Esito: DOCX prodotto dall'interfaccia ordinaria con il profilo per sezioni.**
- **Scritture:** 10 destinazioni scritte, tutte DIMOSTRATA: 5 scritture positive e 5 effetti di
  deselezione. 0 dubbie, 0 indebite.
- **Budget:** 163.006 token su un tetto di 300.000, circa 0,033 USD.
- **Durata:** 189 s.

Autorizzato dall'utente: **un solo tentativo**, `cesano-predefinito-1`, senza ripetizioni.

La revisione è **autoriale (Claude), non indipendente**. Un campione su un modulo piccolo non
misura l'accuratezza generale.

**Preregistrazione e harness congelati:**
`backend/data/compilation-audit/microtest-predefinito-20261024-01/`, con `PREREG-MICROTEST.md`,
`HARNESS-FREEZE.json`, `out/FREEZE.json` e `out/SERVIZI.json`.

**Risultati:** `benchmark ufficiale/microtest-predefinito-20261024-01/`, con `ANALISI.json`,
`REVISIONE-AUTORIALE.json` e `trials/cesano-predefinito-1/`.

## Configurazione fotografata prima delle chiamate

- **Codice:**
  - working tree `/home/montesano/tesi` (branch `prune-backend`), file di `backend/`, `frontend/`
    e `start.sh` uguali a `dc640fc`;
  - code digest `c67b0204…`;
  - le stringhe dei prompt sono identiche alla candidata della campagna (`3ec0af0`) a meno della
    docstring di `compilation_profile.py`, che non viene inviata al modello.
  - Il digest posizionale differisce solo per lo spostamento degli indici AST
    (`out/prompt-confronto.json`).
- **Profilo atteso e osservato:** `sezioni-2026-10-24` (generazione 3, V14, K3, derivazione, P3,
  recupero del narratore, R1, tabelle, riesame 2). Verificato a ogni chiamata.
- **Provider:** profilo AI predefinito dell'app, DeepSeek `deepseek-flash`. Tutte le 9 risposte
  dichiarano `deepseek-flash`.
- **Scenario:** Cesano della campagna incrementale.
  - FORM `9386c79e…`, scenario USER `a933337b…`, politica USER `cesano-esteso`.
  - SOURCE: i 4 documenti globali già presenti nell'app, che per un progetto nuovo producono 22
    frammenti identici al corpus congelato.
  - Catalogo identico, 88 destinazioni.
  - Nessun dato modificato.
- **Servizi:** Vite sulla 5173 con il comando di `start.sh`. Backend ordinario sulla 8000
  avviato da un osservatore (`mt_server.py`):
  - stessa `app.main:app`, stesso `.env`, database e storage ordinari;
  - inoltro invariato al provider;
  - prenotazione del budget e controlli prima di ogni chiamata;
  - nessun `--reload`.
  - Al termine l'app è stata riavviata con `./start.sh`.

## Svolgimento

**Preparazione:** progetto temporaneo e FORM creati con le API dell'interfaccia, tramite il proxy
della 5173.

**Compilazione**, interamente dall'interfaccia: menzione `@`, composer, «Scarica DOCX».

| Passo | Messaggio USER | Chiamate | Esito | Fine |
|---|---|---|---|---|
| richiesta iniziale | richiesta registrata dello scenario | routing, 2 segmenti, registro, narratore | 1 domanda con 3 punti | 174 s |
| risposta 1 | 3 decisioni preregistrate: autorizzazione della clausola, ramo del firmatario, scelta «Società di Ingegneria» | routing, guardia semantica, narratore | pronta per l'export | 183 s |
| export | richiesta d'export registrata | routing | `GENERATED`, DOCX scaricato | 187 s |

## Risposte

1. **DOCX:** prodotto, scaricato dall'interfaccia e identico byte per byte a quello archiviato.
   - **Leggibilità:** 3 pagine, intestazione «BOZZA NON VERIFICATA - NON FIRMARE O INVIARE SENZA
     REVISIONE», valori in linea con il testo, una sola casella spuntata nel gruppo «In nome e
     per conto».
   - **Pagine 2 e 3:** categorie, data e firma vuote.
   - **Renderer V12 congelato:** 4/4 valori testuali visibili nel PDF, 0 parole fuori pagina,
     0 valori invisibili.

2. **Scritture:**

   | Destinazione | Valore | Base | Giudizio |
   |---|---|---|---|
   | `p12.ft0` nome del firmatario | nome della persona scelta | SOURCE (anagrafica del firmatario) + scelta USER, ramo `s1_c_rappr` | DIMOSTRATA |
   | `p12.ft1` luogo di nascita | luogo di nascita | stessa sezione SOURCE della persona | DIMOSTRATA |
   | `p12.ft2` data di nascita | data di nascita | stessa sezione SOURCE della persona | DIMOSTRATA |
   | `p19.ft0` denominazione | Mapi Ingegneria S.r.l. | SOURCE «Ragione sociale» + autorizzazione USER della clausola (V14) | DIMOSTRATA |
   | `p19.cb0` Società di Ingegneria | spuntata | scelta USER esplicita, coerente con SOURCE «società di ingegneria civile» | DIMOSTRATA |
   | `p16`, `p17`, `p18`, `p20`, `p21` `.cb0` | non spuntate | effetto della scelta esclusiva, caselle già vuote, nessun cambiamento visibile | DIMOSTRATA |

   La SOURCE contiene i valori anagrafici, non riportati qui.

3. **Campi documentati e omissioni:**
   - **Nucleo v3:** 4/4 corretti, come in cesano-1.
   - **Decisione USER attesa dal riferimento** (`p19.cb0` = vero): applicata. In cesano-1 mancava.
   - **Campi che il riferimento vuole irrisolti:** restano vuoti (data, preferenze, recapiti e
     posizioni previdenziali personali, iscrizione all'ordine).
   - **Proposte respinte dal validatore:**
     - 7 campi personali del firmatario, dove il modello aveva proposto dati della società (es.
       sede legale per «con studio in»): rifiutate da K3, corretto;
     - 6 checkbox proposte senza decisione USER: respinte, poi scritte solo dopo la scelta USER.
   - Nessuna omissione rispetto al riferimento.

4. **Segmenti e tempi:**
   - 2 segmenti, sequenziali (137,6 s e 28,2 s), 1 tentativo ciascuno, **0 retry**.
   - 2 file di cache scritti, non riusati perché non c'è stata ripresa.
   - Richieste di segmento identiche a quelle congelate di cesano-1: parametri, prompt, FORM,
     SOURCE e piano di lettura.
   - Durata totale 189 s, di cui circa 173 s per la prima risposta.

5. **Token e costo:**
   - **Totale:** 163.006, cioè prompt 127.280 (cache hit 52.480), completion 35.726 (reasoning
     28.822).
   - **Per tipo:**
     - segmenti 109.309;
     - narratore 21.736;
     - guardia 16.776;
     - routing 14.384;
     - registro 801.
   - **Costo:** circa 0,0328 USD, con la tariffa fuori punta congelata (sabato). Stima da usage,
     non fattura.
   - **Budget:** massima prenotazione per chiamata 106.947; nessun rifiuto; nessun usage ignoto.
     Rispetto a cesano-1: 175.331 token, 10 chiamate, 197 s.

6. **Errori dell'interfaccia:**
   - 0 risposte HTTP di errore e 0 errori JavaScript.
   - 10 richieste `ERR_ABORTED`, al caricamento della pagina e al ricaricamento dopo il download:
     richieste annullate dalla navigazione, senza effetti.

7. **Differenze dal comportamento atteso:**
   - **Stati dell'interfaccia:**
     - all'inizio di ogni messaggio compare per 2-6 s l'etichetta generica «Sto lavorando…»,
       mentre il messaggio viene interpretato (6 s nella risposta, con la guardia semantica);
     - per l'export lo stato «Preparazione del DOCX…» non compare, perché routing e generazione
       avvengono nella stessa richiesta.
     - Gli stati principali sono quelli reali: «Analisi del documento e compilazione delle
       sezioni…», «attesa di chiarimenti», «Verifica dei dati…», «verifica dei dati completata»
       e «bozza incompleta», con la nota sulla bozza da verificare. «Incompleta» è corretto,
       perché restano campi irrisolti.
   - **Checkbox:** il gruppo «In nome e per conto» è stato chiesto come scelta e scritto, mentre
     in cesano-1 era stato trattato come condizione. È variabilità del modello a prompt invariati
     e porta al valore atteso dal riferimento.
   - **Controlli non esercitati da questo modulo:** R1 (nessuna continuazione d'opzione),
     tabelle condizionali (nessuna regione), riesame (nessuna sospensione), recupero del narratore
     (riuscito al primo tentativo), retry e ripresa dalla cache.
   - **Controlli esercitati:** V14 (autorizzazione della clausola), K3 (7 rifiuti), guardia
     semantica, veto dell'export (nessun 409, nessuna sospensione da aggirare).

8. **Utilizzabilità per la demo:** sì, per Cesano.
   - **Pro:** percorso completo dall'interfaccia, profilo per sezioni effettivo, stati reali,
     bozza corretta e leggibile, costo trascurabile.
   - **Avvertenze:**
     - circa 3 minuti di attesa iniziale con una sola etichetta di avanzamento;
     - «Preparazione del DOCX» non visibile;
     - moduli più grandi (Catanzaro, So.Re.Sa.) con coperture più basse nelle campagne;
     - un solo campione;
     - revisione non indipendente.

## Integrità e pulizia

- **Arresti:** nessuno STOP, budget mai insufficiente; gate chiuso subito dopo il tentativo.
- **Progetto temporaneo:** copiato con hash verificati (35 file, righe del database in 8
  tabelle), poi eliminato con l'API ordinaria (204, poi 404).
- **Dati invariati:** 3 progetti, 29 sessioni con stato e DOCX originale identici, 273 file
  archiviati identici prima e dopo.
- **Ripristino:** app riavviata con `./start.sh` su 8000 e 5173.

**Non modificati:** codice, prompt, configurazione AI, baseline V12, benchmark storici e
`main` remoto. Nessun merge, nessun push.
