**Verifica reale del consumo e delle bozze DOCX — 22 settembre 2026**

La versione mantenuta è `docx-fields-v11-compact-json`: conserva tutto il
contenuto del prompt precedente e rimuove soltanto gli spazi di separazione
del JSON. Il risparmio di token di input è verificato sul provider. Le bozze
superano i controlli tecnici descritti sotto; persistono errori semantici.
Non è una certificazione della correttezza della compilazione né un benchmark
di generalizzazione.

Il modello richiesto è `deepseek-v4-flash`; tutte le risposte indicano
`deepseek-flash`. I moduli sono gli originali Minervino e Catanzaro, le
indicazioni utente sono vuote e i gruppi contengono al massimo 32 candidati.
Minervino riceve 52/52 frammenti, 58.874 caratteri; Catanzaro 92/192 frammenti,
106.718 caratteri su 226.136 disponibili.

**Misura del risparmio della versione finale**

Per ogni modulo è stato inviato il primo gruppo anche nella serializzazione
precedente, limitando la risposta a un token. Si confronta `usage.prompt_tokens`
con quello della prima chiamata della compilazione completa v11. Modello,
istruzioni e dati del gruppo sono uguali; cambia soltanto la spaziatura JSON.
L'output troncato delle richieste di misura è intenzionale e non viene
utilizzato per compilare documenti.

| Caso | Token input riferimento v9 | Token input v11 | Token input risparmiati | Riduzione |
| --- | ---: | ---: | ---: | ---: |
| Minervino, primo gruppo | 47.808 | 44.360 | 3.448 | **7,21%** |
| Catanzaro, primo gruppo | 73.594 | 69.073 | 4.521 | **6,14%** |

Queste percentuali riguardano il primo gruppo, non il totale input/output
dell'intera compilazione. I token in cache sono inclusi nei token di input:
il loro numero varia tra chiamate e non si deduce da questa tabella un
risparmio monetario della stessa percentuale.

| Misura delle compilazioni complete v11 | Minervino | Catanzaro |
| --- | ---: | ---: |
| Token input, incluse eventuali correzioni | 398.990 | 621.566 |
| Token output | 19.259 | 20.641 |
| **Token totali** | **418.249** | **642.207** |
| Chiamate di compilazione | 9 | 9 |
| Gruppi iniziali completati | 8 | 9 |
| Correzioni richieste | 1 | 0 |
| Proposte corrette | 2 | 0 |
| Risposte di compilazione troncate | 0 | 0 |
| Campi candidati classificati | 254 | 279 |
| Campi scritti | 19 | 22 |
| Campi `missing` | 133 | 206 |
| Campi `needs_review` | 102 | 8 |
| Campi `not_applicable` | 0 | 43 |
| Campi candidati non classificati | 0 | 0 |
| Campi con errori di validazione residui | 0 | 0 |

Rispetto alle prove storiche, Minervino passa da 447.885 token della v7 a
418.249 della v11 (−6,62%); Catanzaro da 683.154 della v9 a 642.207 (−5,99%).
Questo confronto include risposte diverse del modello e, per Minervino,
anche tre province riconosciute in più dal parser rispetto alla v7: non
isola l'effetto della serializzazione. La misura controllata è quella di input
nel primo gruppo.

**Perché la v10 è stata ritirata**

La v10 eliminava anche la copia originale dei paragrafi, conservando quella
con gli identificatori. Pur mantenendo informazioni ricostruibili e passando
i test, nella prova Catanzaro ha scritto nove campi aggiuntivi nelle sezioni
5.e e 5.f non confermate: `t28.r3.c1`, `t28.r3.c3`, `t29.r0.c1`, `t29.r1.c1`,
`t29.r3.c1`, `t29.r4.c1`, `t31.r0.c1`, `t31.r4.c1`, `t31.r4.c3`.

| Prova sul quinto gruppo Catanzaro | Scritture nei nove campi indicati |
| --- | ---: |
| v10, durante la compilazione completa | 9 |
| Riferimento v9, richiesta diagnostica sullo stesso gruppo | 0 |
| Solo JSON compatto, richiesta diagnostica sullo stesso gruppo | 0 |
| v11, successiva compilazione completa | 0 |

Le richieste diagnostiche condividono lo stesso contesto della v10. Una
singola osservazione per configurazione non dimostra causalità o assenza di
regressioni future. È stata comunque ritirata la rimozione del testo duplicato,
privilegiando la conservazione integrale del contesto. Non sono state aggiunte
regole specifiche per i campi o per le sezioni di questi bandi.

**Controlli tecnici e risultati semantici**

| Controllo | Esito v11 |
| --- | --- |
| Tutte le 18 richieste live, comprese le correzioni | Dopo il parsing JSON coincidono con i payload del builder precedente; istruzioni di sistema identiche. |
| Integrità dei due DOCX | ZIP leggibili, hash di originali e bozze corrispondenti ai report. |
| Parti del pacchetto | Cambia soltanto `word/document.xml`; tutte le altre parti restano identiche byte per byte. |
| Testo prestampato e scritture | Paragrafi conservati salvo sostituzioni autorizzate e avviso di bozza; 19 e 22 scritture corrispondenti ai report. |
| Evidenze dei valori scritti | Verificate tutte le 19 citazioni Minervino e le 23 Catanzaro contro gli snapshot delle fonti e i relativi hash. |
| Firme | Nessuna scrittura. |
| Persistenza | Nuovi risultati registrati nei progetti; funzioni di lettura e risoluzione dei download verificate. |
| Test e controlli statici | 378 test backend superati; Ruff e `git diff --check` senza errori. |
| Rendering visivo Word | Non verificato. |

| Caso | Confronto e limiti osservati |
| --- | --- |
| Minervino, anagrafica iniziale | Provincia `BA` effettivamente scritta: la bozza contiene `Bari (BA)`. Il telefono rimane nel campo corretto. Gli ID dopo la nuova provincia differiscono da quelli della v7: non si confrontano soltanto gli ID. |
| Minervino, indirizzo societario | Rimane `Via Giovanni Amendola 172/C` nel campo via, seguito da `172/C` nel civico; il campo sede contiene ancora l'indirizzo completo. |
| Minervino, rami non confermati | Rimangono nove scritture nel ramo societario. Si aggiungono rispetto alla v7 la PEC in `p24.s0` e email/PEC dello studio associato in `p37.s6` e `p37.s7`, senza scelta esplicita. Il secondo problema era già osservato nella v8. I 19 inserimenti non significano 19 campi corretti. |
| Catanzaro, scritture | Stessi 22 identificatori e stessi valori della precedente v9, comprese le scritture problematiche in 5.c, 5.h e la sede operativa coincidente con quella legale. Nessuna delle nove scritture aggiuntive della v10 in 5.e/5.f. |
| Catanzaro, classificazione dei vuoti | Gli stati e le motivazioni variano: i `not_applicable` passano da 21 nella v9 a 43 nella v11. Alcune esclusioni vengono dedotte senza scelta esplicita; non è dimostrata equivalenza semantica dei report. |

Non risultano guasti tecnici nelle prove eseguite. Non si può garantire che
ogni nuova generazione conservi le stesse decisioni: il modello interpreta
ancora in modo incoerente le sezioni condizionali. La validazione delle
citazioni conferma la provenienza del valore, non l'applicabilità del campo.

**Materiale verificabile**

| Caso e versione | Compilazione | Bozza e report | Misure e snapshot |
| --- | --- | --- | --- |
| Minervino v11, finale | `c7ce4528606448a0a96db02040569950` | [Bozza](backend/data/uploads/minervino-di-lecce-elenco-sia/_compilations/c7ce4528606448a0a96db02040569950/bozza.docx) · [Report](backend/data/uploads/minervino-di-lecce-elenco-sia/_compilations/c7ce4528606448a0a96db02040569950/report.json) | [Misure](backend/data/compilation-verification-v11/20260922T104926Z-minervino/summary.json) · [Contesto](backend/data/compilation-verification-v11/20260922T104926Z-minervino/context.json) |
| Catanzaro v11, finale | `d7c5cbcfb0db45f0b19eb598bcc40c38` | [Bozza](backend/data/uploads/catanzaro-direzione-lavori-e-sicurezza/_compilations/d7c5cbcfb0db45f0b19eb598bcc40c38/bozza.docx) · [Report](backend/data/uploads/catanzaro-direzione-lavori-e-sicurezza/_compilations/d7c5cbcfb0db45f0b19eb598bcc40c38/report.json) | [Misure](backend/data/compilation-verification-v11/20260922T105632Z-catanzaro/summary.json) · [Contesto](backend/data/compilation-verification-v11/20260922T105632Z-catanzaro/context.json) |
| Minervino v10, ritirata | `eae8e7d0572f42ba8e45656ed1ec9cb2` | [Report](backend/data/uploads/minervino-di-lecce-elenco-sia/_compilations/eae8e7d0572f42ba8e45656ed1ec9cb2/report.json) | [Misure](backend/data/compilation-verification-v10/20260922T104240Z-minervino/summary.json) |
| Catanzaro v10, ritirata | `b9113ba6547f40f7a2642cf85b2457de` | [Report](backend/data/uploads/catanzaro-direzione-lavori-e-sicurezza/_compilations/b9113ba6547f40f7a2642cf85b2457de/report.json) | [Misure](backend/data/compilation-verification-v10/20260922T104435Z-catanzaro/summary.json) · [Diagnosi](backend/data/compilation-verification-v10/20260922T104435Z-catanzaro/diagnostic-comparison.json) |

Le cartelle delle misure contengono richieste, risposte, consumo per chiamata
e controlli sui documenti. Non contengono le credenziali del provider.
Tra le due versioni il riavvio del backend ha aggiornato gli identificatori
dei frammenti `project-facts.md`, conservandone il contenuto: i riferimenti
token v11 sono stati misurati di nuovo sul loro contesto esatto. La compilazione
Minervino v11 era già salvata quando il controllo del vecchio riferimento ha
rilevato questa differenza; è stata completata soltanto la misura, senza
rigenerare la bozza.

**Consumo complessivo di questa verifica**, separato da quello di una singola
compilazione: 42 richieste e **2.492.882 token**, dichiarati dal provider.

| Attività | Richieste | Token totali |
| --- | ---: | ---: |
| Due compilazioni complete v10 | 18 | 1.041.921 |
| Due compilazioni complete v11 | 18 | 1.060.456 |
| Quattro misure con output limitato a un token | 4 | 242.808 |
| Due confronti diagnostici sul gruppo Catanzaro | 2 | 147.697 |
| Totale | 42 | 2.492.882 |
