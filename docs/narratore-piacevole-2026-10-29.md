# Narratore piacevole: comportamento del dialogo dalle due prove manuali Minervino (29 ottobre 2026)

**Ambito:**
- prova 1, istanza `tesi-prova-manuale-audit03-20261029`, codice `dbdc317`;
- prova 2, istanza `tesi-prova-manuale-2-20261029`, codice `a4582a1`, lasciata in esecuzione e
  non toccata; analisi in sola lettura delle istantanee.

Nessuna chiamata DeepSeek, push o merge; app ordinaria e audit storici non toccati.

**Grezzo:** `backend/data/compilation-audit/prova-manuale-minervino-20261029/`:
- `replay_manuale.py`, che ora registra anche le voci del pool già risposte;
- `replay/s{1,2}-{prima,dopo}-*-v3`;
- `CONFRONTO-DIALOGO.md`;
- `suite-narratore-piacevole-e28475c.txt`;
- `rollback-narratore-piacevole.txt`.

## Dove si rompeva la catena

| Problema osservato | Anello rotto | Causa |
|---|---|---|
| Conferma del firmatario chiesta, poi il nome chiesto di nuovo («Lo avevo già confermato») | pool | La condizione del firmatario governava solo il nome; era chiesta prima del nome, che restava aperto |
| Nome presente nel DOCX, dati personali e carica vuoti | ricevuta → gate di ambito | Dopo il nome, la derivazione SOURCE aggiunge 8 dati e la carica. La ricevuta della condizione copriva solo il nome e il gate li lasciava vuoti, senza dirlo |
| Data di Elisa Romano chiesta all'utente | validatore | «18/05/2015» (tabella soci) e «18 maggio 2015» (relazione) erano trattate come alternative, quindi il campo era in revisione senza valore |
| Risposta USER sulla data non riflessa | guardia → pool | Rifiutata (ambito); la ricevuta prometteva un chiarimento che non veniva mai chiesto |
| «Luca Ferri amministratore unico» nel riepilogo | narratore | Il ruolo non è attestato: le fonti indicano «socio» e la carica cessata |
| «Confermato: …; Il sottoscritto , nato a.» e formule lunghe | ricevuta | Clausola FORM fatta di segnaposto; testi fissi lunghi; 3 domande per turno |
| Nome perso dopo il riordino (trovato nel replay) | ricevuta del valore | La ricevuta era legata alle risposte sulle condizioni viste al momento; una conferma successiva la invalidava |

## Correzioni (commit separati)

| Commit | Correzione |
|---|---|
| `010192b` | Il nome di proprietà del FORM viene chiesto prima delle condizioni del suo blocco. Una conferma data prima della derivazione viene richiesta una sola volta, nominando i dati nuovi; rinvii ed esclusioni non vengono riproposti |
| `178eac7` | Una risposta rifiutata viene richiesta per prima nel turno successivo. Dopo due tentativi viene chiusa con un messaggio esplicito |
| `ee59c52` | Ricevute brevi in linguaggio semplice, fino a 4 domande per turno, bozza parziale sempre offerta |
| `1bf55bd` | Il riepilogo nomina la carica di una persona solo se un binding GROUNDED la attesta; altrimenti la frase viene tolta, con avviso |
| `b24c725` | Una data completa scritta in due formati è un solo valore documentato; date diverse o parziali restano una scelta dell'utente |
| `1b4b766` | La ricevuta di un valore conserva le risposte sulle condizioni con cui è stata verificata. Resta valida solo se ogni cambiamento successivo è una conferma USER valida che copre il campo; esclusione, rinvio, altra destinazione o dati alterati la invalidano |
| `e28475c` | Una ricevuta di conferma non ripete la nota del modello «non confermati» o «da confermare» |
| `1663f67` → `8365910` | Annullato: il testo vago della domanda sul nome veniva dallo stub del replay, non dalla prova reale |

I controlli non sono indeboliti:
- nessuna casella è spuntata in automatico;
- nessuna dichiarazione è autorizzata implicitamente;
- validatori, guardia e gate di export sono invariati, salvo la ricevuta di `1b4b766`, che resta
  conservativa.

## Verifiche

**Replay offline delle due conversazioni:**
- risposte USER letterali;
- simulati: narratore, planner e guardia;
- reali: pool, ricevute, derivazioni, gate, export e DOCX.

| | Prova 1 prima → dopo | Prova 2 prima → dopo |
|---|---|---|
| Prova reale | 14 domande, 6 turni | 10 domande, 4 turni, nome chiesto due volte |
| Replay: domande / turni | 13 / 5 → 9 / 3 | 10 / 4 → 9 / 3 |
| Domande già risposte riproposte | 0 → 0 | 0 → 0 |
| Conferme USER senza effetto | `p39.cb0` → nessuna | 10 campi → nessuno |
| Scritture | 56 → 57 (`p39.cb0`, USER) | 49 → 59 |

Prova 1: il guadagno viene dal lavoro precedente (`docs/narratore-fluido-2026-10-29.md`);
nessuna regressione.

Le 10 scritture nuove della prova 2 sono tutte SOURCE e coperte da condizioni confermate
dall'utente che includono il campo:
- 8 dati personali del sottoscrittore;
- la carica;
- `p46.s1` e `p53.s3`.

Nessun valore tolto o cambiato; caselle invariate. Il riepilogo reale della prova 2, filtrato sui
dati reali, perde la frase su Luca Ferri.

**Test:**
- nuovi test su FORM sintetici (firmatario, date, ricevute); falliscono sul codice precedente;
- backend: 4.161 passati, 8 saltati (artefatti locali assenti); Ruff PASS dopo `c9af3ea`;
- frontend: 168/168; lint (2 avvisi già presenti) e build PASS.

**Rollback:**
- ogni revert riporta l'albero del genitore;
- i nuovi test falliscono, per asserzione o per import assente;
- i test del genitore passano.

## Limiti

- **Replay:** la formulazione del narratore e la guardia reali non sono misurate. Il percorso
  «rifiuto e nuova richiesta» è verificato solo dai test: nel replay successivo la data non è più
  chiesta.
- **Firmatario:** servono ancora due passi, il nome e poi la conferma dei dati ricavati e della
  carica. Il nome da solo non autorizza la carica. Il nome non viene proposto dalle fonti.
- **Filtro dei ruoli:** toglie l'intera frase. Nel riepilogo reale sparisce anche «direttore
  tecnico Elisa Romano», che è attestato.
- **Date equivalenti:** solo per date complete. Il valore scritto mantiene il formato della fonte
  (`p46.s1` «18/05/2015», `p53.s3` «18 maggio 2015»).
- **Istanza 2:** usa ancora `a4582a1`, non aggiornata.
