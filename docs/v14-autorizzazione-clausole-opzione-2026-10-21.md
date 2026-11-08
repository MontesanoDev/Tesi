# Candidata V14: autorizzazione delle clausole d'opzione — 21 ottobre 2026

**Esito.** La V14 (V13/S1 più un solo controllo, nelle sole nuove sessioni) non scrive
più le quattro celle CCIAA di craa-03/04. Una ricevuta di selezione del ramo non autorizza
mai la dichiarazione. Costo misurato: anche 9 scritture corrette di Cesano (`p19.ft0`)
richiedono ora un'autorizzazione esplicita che le vecchie conversazioni non contengono.
**Non è una soluzione completa** della sicurezza dei rami: copre solo le regioni d'opzione
riconoscibili. Candidata non adottata; baseline V12 e snapshot V13 invariati; nessuna
chiamata LLM, campagna, commit, tag o push.

## 1. Rischio verificato prima del codice

Simulazione sugli stati registrati di una sola ricevuta di ramo «Sì, Mapi Ingegneria
S.r.l. è una società» sulla condizione CCIAA, con il codice reale:

| Profilo | Prove CRAA | Celle CCIAA esportate dopo la ricevuta di ramo |
|---|---:|---:|
| V13 attuale | 21 | 21 (19 con condizione, 12 domande senza cenno all'attestazione; 2 senza condizione) |
| V14 | 21 | **0** (nessun'altra esportazione cambia) |

Il disegno R1T precedente, con sblocco da condizione ancorata (U2), avrebbe ereditato lo
stesso difetto: per questo è stato corretto prima dell'implementazione.

## 2. Disegno corretto e implementato

- `backend/app/compilation_option_regions.py` (nuovo, solo catalogo):
  - un'opzione è una checkbox nativa oppure un glifo di casella;
  - la regione è il paragrafo dal primo marcatore in poi, più la tabella immediatamente
    successiva se l'opzione è nel corpo; per un'opzione in cella, solo il suo paragrafo;
  - i controlli dell'opzione non sono governati.
- `compilation_procedural_consent.requirements`: per le sessioni con
  `option_authorization_revision == 1`, ogni regione con valori da scrivere genera un
  requisito del consenso procedurale già esistente:
  - la domanda chiusa, generata dal backend, riporta il paragrafo integrale e i dati;
  - sblocca solo l'assenso esplicito a quella domanda, con lo stesso ambito e gli stessi
    valori nella stessa sessione;
  - condizioni, scelte di caselle e ricevute di ramo non sbloccano; i FALSE derivati
    dalla scelta di un gruppo non sono valori da autorizzare.
- `compilation_global_sessions`: le nuove sessioni ricevono il campo; l'analisi lo copia
  dalla sessione o lo rimuove, come `backend_revision`. Le sessioni esistenti non cambiano.
- Contratto MODEL, prompt B0, validatori, writer e regole V13 restano invariati. Cambiano
  2 file su 120 della V13 e se ne aggiunge 1 (`code-freeze-V14.json`).

## 3. Verifiche eseguite

| Test | Esito |
|---|---|
| T0 preregistrazione (SHA256 `d3d179f5…`, 18:59 UTC) | prima del codice, esiti attesi e criteri di rifiuto |
| T1, 16 nuovi test | PASS: regioni (tabella adiacente, paragrafo intermedio, opzione in cella, testo prima del marcatore, controlli nativi); requisiti solo con il campo e impegni identici; ricevute di ramo, SKIP, assenso non esplicito e domanda diversa non sbloccano; valore cambiato richiede nuovo assenso; FALSE non bloccato; sessione reale con e senza condizione di ramo; sessione senza campo con comportamento V13 |
| T2, replay offline (SQLite e rete vietati) di 82 DOCX, 806 scritture | rimosse 13: 4 CCIAA (craa-03/04) e 9 `p19.ft0` Cesano; 0 altre modifiche; V13 rigenerato identico al registrato in 82/82 |
| T2 senza campo | requisiti identici al modulo originale in 93/93 stati |
| T3, selezione con dialoghi registrati | rimossi solo `p19.ft0` (9) e celle CCIAA (2+2); nessuna aggiunta; nessun nuovo blocco fuori dalle regioni |
| T4, 13 moduli (6 di sviluppo, 7 esterni) | nessuna attribuzione in eccesso osservata (revisione dell'autore); Soresa e Cannara non rilevati |
| T5 | suite backend 3.380 PASS (3.364 storici + 16), Ruff PASS; frontend non rieseguito |

Regressioni: condizioni e veti esistenti invariati; checkbox FALSE legittime e controlli
delle opzioni non bloccati (Cesano baseline 5 FALSE e 1 TRUE, Minervino 3 TRUE conservati);
rami condivisi non attribuiti (dati dell'impresa CRAA, tabella preceduta da paragrafo nei
test); campi fuori dalle regioni identici.

## 4. Benchmark e generalizzazione

- **Benchmark.** craa-03/04 non scrivono più le quattro celle. Nessuna scrittura corretta
  fuori dalle regioni d'opzione viene eliminata. Le 9 `p19.ft0` di Cesano si basavano solo
  su ricevute di selezione: in una nuova sessione richiedono una risposta esplicita di
  autorizzazione. Il costo nel dialogo sono domande obbligatorie, che occupano uno dei tre
  slot per turno; il suo effetto sulla copertura non è misurato.
- **Moduli nuovi.** La protezione vale solo dove il marcatore è riconosciuto e il
  contenuto sta nel paragrafo o nella tabella adiacente. Restano scoperti, come prima:
  - i seguiti in paragrafi successivi (Calabria, 23 campi);
  - i marcatori «[ ]» e U+F06F (Soresa, Cannara) e i simboli `w:sym`;
  - le condizioni solo testuali.

  Nessun gold sui moduli esterni.

## Materiali

Grezzo `backend/data/compilation-audit/v14-option-authorization-20261021-01/`:
preregistrazione, copie `before/`, patch, freeze V14, script e output, con 453 input
elencati. [Backup](benchmarks/2026-10-21-v14-option-authorization-audit.tar.gz) SHA256
`b740e15135e69f191ac659d68545e4f5315d92178da3fa94c957bf674e708f54`, verificato con due
estrazioni, manifest, input, 121 hash del codice e 4 output rigenerati identici.
Nuovo test: `backend/tests/test_compilation_option_authorization.py`.
