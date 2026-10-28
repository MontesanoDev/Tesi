# Proposta di nuovo audit Minervino — da autorizzare

**NON AVVIATO.** Il fallimento infrastrutturale del 28 ottobre rimane registrato
come tentativo `narratore-minervino-20261028-01`, senza provider né DOCX.
Questa è una proposta per un nuovo tentativo, non un'autorizzazione implicita.

## Candidata e strumento

- Compilatore invariato: `7b31d25930c52504e0a1461491bde3fd23ca3a0e`, inclusi
  `f3bc281` e i fix precedenti di nome, separatori e ricevute.
- Harness: `4fc0377` (comprende `8524aa5` redirect e `8d047dc` metriche).
- Rapporto precedente: `3f97a59`.
- Profilo: esattamente il `profile.json` precedente, hash sotto. Nessuna adozione
  nell'app ordinaria e nessuna modifica a prompt o configurazione del compilatore.
- Modello richiesto: `deepseek-flash`. Registrare modello/fingerprint eventualmente
  restituiti; l'identità dei pesi dietro un alias remoto non è congelabile da Git.

Le nuove metriche distinguono preparazione, prenotazione, ingresso nel trasporto,
risposta, usage e incertezza. La politica dei redirect esterni rimane restrittiva.
Preflight completato: 51 test, Ruff e 5 percorsi dal composer attraverso FastAPI
al provider simulato, con ulteriori probe sui redirect e sul blocco della rete.
[Rapporto delle prove](harness-narratore-riparazione-2026-10-28.md).

## Input e scenario USER congelati

Riutilizzare per copia verificata gli input privati e la policy del tentativo 01;
nessuna riscrittura delle risposte per aumentare le scritture.

| Artefatto precedente | SHA-256 |
|---|---|
| `harness/policy.cjs` | `d5e06ce58237050d6f5c656f6ea07238ef23928390de3c3dd7de244aa5436397` |
| `browser/protocol.json` | `be535de96af0ba90d5ca0c1d507c68d849f1d509b219d2a77621601fc6e72ed7` |
| `input/FORM.docx` | `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c` |
| `input/SOURCE.json` | `eae18e33499129f61ece52c472b376f8b4c233d4659c6edc97d6a445e5b77319` |
| `input/catalog.json` | `a613858a381d2de937d3a351fbcc9077fca9a65c798b30c826e47263e3a7c178` |
| `input/profile.json` | `1aac7c6b152259bfb278c4f72af34b954374a85ac33b82c66c57900a36cae870` |

Identificazione dell'operatore e del firmatario, ruolo documentato e scelta della
società di ingegneria restano quelle della policy. Clausole legali non autorizzate,
categorie, fasce, designazioni, date non documentate e domande impreviste rimangono
rinviate secondo la regola già congelata. Il rapporto pubblico non riproduce dati
personali, SOURCE o trascrizioni.

## Un tentativo, budget richiesto 900.000 token

Un solo percorso frontend → FastAPI → DeepSeek → dialogo → export. Nessuna
ripetizione esterna se fallisce. Solo i retry già previsti dalla candidata,
contabilizzati nello stesso tentativo. Non aggiungere retry della strumentazione.

Prima della prima chiamata, dopo autorizzazione:

1. Creare un nuovo runtime e una nuova directory `narratore-minervino-…-02`, senza
   riaprire gate o ledger del tentativo 01. Backup verificato, nessuna sessione live.
2. Copiare input/policy; verificare gli hash sopra e il diff nullo del compilatore.
   Solo percorsi, porte, ID del nuovo runtime e identificatore del tentativo nel
   nuovo protocollo possono cambiare; messaggi/regole USER rimangono identici.
3. Congelare il nuovo manifest di codice, harness, prompt, profilo, input e
   protocollo prima dell'apertura del gate. Registrare SHA completi e dipendenze.
4. Budget atomico di 900.000 token complessivi. Riservare prima di ogni chiamata
   `2 × byte UTF-8 del JSON + 32.768 + max_tokens`. Non ridurre le richieste per
   farle rientrare nel residuo. Sono ammesse solo richieste testuali bounded del
   modello previsto; immagini, tools, streaming o richieste senza cap sono rifiutati.
5. Conservare l'intera riserva se usage manca o non è coerente; fermarsi. Input e
   output includono il reasoning secondo l'usage provider, senza doppio conteggio.
6. Congelare un tariffario documentato prima del test se disponibile; altrimenti
   dichiarare costo non determinabile. Non trattare i prezzi sintetici dei test
   come prezzi DeepSeek. Token prenotati, usage e costo stimato restano separati.

Il limite è conservativo, non una certificazione della fattura: se il provider
viola il massimo prenotato, STOP immediato e segnalazione della violazione.
Una prenotazione pendente dopo un crash non è credito automaticamente disponibile.

## Osservazioni e arresto

Conservare localmente trascrizione cronologica, domande e loro riferimenti logici,
risposte, ricevute, revisioni persistite, proposte, hold, selezione ed export.
Registrare chiamate per turno/fase, prenotazioni, usage (input, output, reasoning,
cache), costo se calcolabile, HTTP provider e HTTP app, errori e tempi disponibili.
Un HTTP 200 dell'app con `generation_status=failed` conta come errore applicativo.

Restano richiesti i sette rapporti del mandato originale: cronologia, ripetizioni,
errori, colli di bottiglia, campi finali, confronto DOCX e rapporto E2E. Revisione
**autoriale**; dichiarare metriche e proprietà non esercitate, incluse quelle dei
fix ruolo/checkbox qualora il modello non percorra quei casi.

Arresto alla prima scrittura non dimostrata accertata, sospensione obbligatoria
aggirata, perdita di integrità, variazione degli input congelati, richiesta non
ammessa, budget insufficiente o usage/esito incerto. Nessun cambiamento di codice,
prompt, SOURCE o policy durante la prova. Se il budget impedisce l'export, non
aggirare il limite per ottenere comunque il DOCX.

Il collaudo offline attuale non ha esercitato un'intera compilazione e non dimostra
memoria o correttezza del narratore reale. Serve a evitare che una misura locale
venga confusa con un invio, un consumo o una risposta del provider.

Attendere la decisione dell'utente prima di preparare credenziali reali o aprire
il gate del nuovo tentativo. Nessun merge/push o adozione automatica.
