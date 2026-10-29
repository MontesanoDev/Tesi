# Correzioni offline dopo l'audit narratore Minervino 03 (28-29 ottobre 2026)

**Ambito:**
- branch `fix/2026-10-28-correzioni-audit-03`, worktree `tesi-correzioni-audit03-20261028`, base
  `00f9bce` (compilatore `7b31d25` e harness `d508b64`);
- nessuna chiamata DeepSeek, nessuna modifica all'app ordinaria, nessun push o merge;
- il tentativo 03 e le sue ricevute SKIP restano invariati.

**Revisione:** autoriale.

## Fix e commit

| # | Commit | Causa (audit 03) | Correzione | Test prima → dopo |
|---|---|---|---|---|
| 1 | `cfdbb06` | La policy USER (revisione 1) leggeva ogni slot come condition, choice o value e applicava la regola sulle date a qualunque elenco di campi: al ramo società rispondeva con il testo sulle date e rinviava l'operatore | Regola scelta in base al tipo reale dello slot, alla citazione FORM e alle destinazioni; le decisioni sono sempre rinviate; i testi delle risposte non cambiano | Revisione 1: 4/17 falliti; revisione 2: 17/17 |
| 1b | `2bdaf45` | Dopo il fix 2a, la condizione del sottoscrittore arriva senza `p12.s0` | Blocco del sottoscrittore: conferma del ruolo se la carica è fra le destinazioni, altrimenti conferma del nome | 1/19 → 19/19 |
| 2a | `f7d35f8` | Una proposta del modello bloccata (binding di ruolo respinto, perché il FORM lascia la carica in bianco) eliminava la domanda «Il sottoscritto» di proprietà del FORM, e con essa la condizione | La proposta resta bloccata e viene registrata; il nome si chiede per primo, anche nel fallback del backend; poi derivazione dalle SOURCE e condizione sulle destinazioni derivate | 3/6 falliti → 6/6 |
| 2a' | `4712c49` | La condizione dell'operatore, chiesta prima del nome, non poteva coprire la carica derivata dopo: il gate di ambito USER la bloccava | Finché il nome è aperto, le condizioni che il blocco erediterà aspettano; un nome rinviato le libera | 1/9 → 9/9 |
| 2b | `f2d7577` | Il binding del direttore tecnico veniva respinto perché la seconda citazione (riga della tabella soci) non contiene il ruolo | Una citazione senza ruolo viene solo registrata; serve almeno un'attestazione letterale; respinti come prima i casi senza attestazione, le citazioni inventate, la General KB e il ruolo assente dal FORM | 2/13 falliti → 13/13 (normale e structural) |
| 3 | `9aa37a9` | Qualunque «non» o «nessun» sostituiva l'intera sintesi iniziale con un testo generico | Si eliminano solo le frasi che negano la presenza (negazione più termine di presenza o fonte); il resto resta letterale, con l'avvertenza; con sole negazioni si usa ancora il testo generico | Funzione nuova → 13/13 |

**Rollback:**
- uno per fix, nei worktree `tesi-rollback-audit03-{policy,firmatario,policy-firmatario,ordine,binding-dt,sintesi}-20261029`;
- ogni revert restituisce l'albero del commit genitore;
- i test del genitore passano (harness 70/70; mirati backend 6-39).

**Suite e controlli:**

| Controllo | Esito |
|---|---|
| Backend | **4.077 PASS**, 0 falliti, in 384 s |
| Ruff (backend e harness) | PASS |
| Harness `audit_tools` | 89/89 PASS |

Gli 8 test saltati richiedono artefatti storici locali assenti in questo worktree
(`test_compilation_narration_recovery`, `test_compilation_scope_review`): non sono stati
eseguiti.

## Rigioco FORM/SOURCE/USER offline del tentativo 03

**Script:** `backend/data/compilation-audit/correzioni-audit03-20261028/replay03.py`. Riparte dalla
sessione 03 alla versione 3, cioè dopo l'analisi reale, e rideriva l'audit dagli output immutati
del modello.

**Simulati:**
- il testo del narratore (prime 3 domande del pool);
- la codifica del planner;
- il verdetto della guardia (accetta la prova di ambito del backend).

**Reali:** pool, ricevute, derivazioni, validatori, gate di export e writer DOCX.

| Codice | Domande | Scritture | Uguali al replay a 58 | Note |
|---|---:|---:|---:|---|
| Tentativo 03 reale (policy rev. 1) | 7 | 0 | 0 | Tutte SKIP |
| `7b31d25` + policy rev. 2 | 7 | 39 | 37 | Più le 2 date dei soci, corrette rispetto alle SOURCE |
| Più 2a, 1b, 2a' | 9 | 48 | 46 | Sottoscrittore completo, carica compresa |
| Più 2b | 10 | 48 | 46 | `s2_c_dt` torna nel pool; la policy la rinvia (direttore tecnico fuori dallo scenario) |
| Più 3 (messaggio reale del 03) | 10 | 48 | 46 | Sintesi persistita con i dati trovati e l'avvertenza |

**Comportamento del dialogo:** 0 domande ripetute, 0 sospensioni e 0 valori diversi dal
riferimento.

**Campi che restano vuoti (12):**
- **Validatore:** provincia della sede e nomi dei 3 soci (citazione senza il nome).
- **Scenario:** 7 campi del direttore tecnico, rinviati dalla policy preregistrata.
- **Non proposto:** la sezione del direttore tecnico.
- **`p39.cb0`:** vedi sotto.

## `p39.cb0`: solo diagnosi, casella non selezionata

**Stato della condizione `s2_c_soc`:**
- fondata;
- confermata dall'USER con il controllo semantico;
- `applies_to` comprende la casella.

**Perché la casella resta vuota:** il suo `scope` esplicito, prodotto dal modello, non la include.
La derivazione della rappresentanza (`_representation_receipt`) richiede la casella in quello
scope e non lo estende per regola, quindi la casella resta non spuntata. È una scelta
conservativa, non modificata.

**Soluzione possibile, da discutere:** una domanda di scelta sul gruppo «IN QUALITÀ DI».

## Limiti

- **Rigioco:** narratore, planner e guardia sono deterministici, quindi il rigioco non misura la
  qualità del modello reale. Un narratore reale può non selezionare la domanda sul nome; il
  fallback del backend la propone solo se il narratore non sceglie nulla.
- **Filtro del fix 3:** è lessicale. Rimuove anche negazioni lecite che citano dati («i dati …
  non sono trasferibili») e non verifica le affermazioni positive (comportamento invariato).
- **Fix 2a':** riguarda solo il blocco del sottoscrittore che sostituisce una proposta bloccata.
- **Ricevute già rese:** non vengono estese né rifirmate. Una conferma resa prima resta limitata
  al suo ambito.
- **Nessun nuovo audit reale.** Va autorizzato a parte.
