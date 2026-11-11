# Campagna finale: verifica di promuovibilità del narratore fluido

Rapporto del 5 novembre 2026. Ramo `narratore-chiarezza/2026-10-31`, HEAD `1e7a22f`, codice identico a
`5c5dcb0`. Nessuna modifica al codice, nessun commit, push, merge o promozione.

## Giudizio

**Non promuovibile con i criteri stabiliti.**

Tre criteri su quattro sono superati, e nessuna scrittura indebita è stata trovata: niente rami
incompatibili, soggetti sbagliati o dichiarazioni non autorizzate. Il quarto criterio, «CNR, checkbox e
compilazione non peggiori del rapporto del 30 ottobre», è **fallito** su checkbox e compilazione.

| Criterio del rapporto | Esito | Prova |
|---|---|---|
| 0 scritture non attese | superato | 0 in tutte le 20 esecuzioni della tabella, lette dai DOCX |
| `p65.*` vuoti anche con la conferma errata del ramo | superato | sessione reale con ramo confermato e router e guardia DeepSeek reali |
| Nessun 5xx | superato | 0 errori dell'app e 0 del provider |
| CNR, checkbox e compilazione non peggiori | **fallito** | checkbox 2 contro 7–8; compilazione 17 contro 18; CNR uguale |

La causa è una sola funzionalità, `7e7383d` del 3 novembre, precedente alla stabilizzazione. **Non è
una perdita di sicurezza ma un problema di completezza e di dialogo**, e richiede una tua decisione
(vedi «Decisione richiesta»).

## 1. Campagna effettivamente completata

**Condizioni comuni:** commit `5c5dcb0` in un worktree fisso, profilo `sezioni-2026-11-05`, modello
`deepseek-flash`, runtime nuovo per ogni esecuzione, al massimo 4 esecuzioni insieme.

| Gruppo | Esecuzioni | Stato |
|---|---|---|
| **Documentata nel rapporto** | 4 dialoghi e 9 esecuzioni con `giro.sh` | tutte completate, 0 errori |
| **Riusata da `c7006a9`** | Trapani × 2 | valida; il comando documentato non la ripeteva |
| **Aggiunta** per lacune del piano | 2 con conferma errata, 1 con pausa e ripresa | completate |
| **Aggiunta** per la diagnosi | 1 ripresa del caso `p65`, 1 scelta su checkbox, 1 replay senza token | completate |

Trapani è su un commit diverso: la differenza tra `c7006a9` e `5c5dcb0` tocca solo le sessioni senza
audit, quindi non può cambiare questi esiti, ma non è la stessa versione.

Due lacune del mio piano, emerse prima di partire:
- lo script dei dialoghi non aveva turni di pausa e ripresa, che hai chiesto esplicitamente;
- l'utente simulato nega il ramo consorzio, quindi il criterio sulla conferma errata non veniva
  esercitato.

Le ho coperte con script separati: `esegui_dialogo.py` non è stato modificato.

**Istanza sperimentale:** riavviato solo il backend sulla 8001. Girava con
`MAPI_COMPILATION_PROFILE=sezioni-2026-10-30-r2`, quindi le nuove sessioni non avrebbero attivato le
correzioni. L'ho portato a `sezioni-2026-11-05`, senza altre modifiche alla configurazione. **Questo
cambia ciò che vedrai nella prova manuale.**

## 2. Risultati per FORM e scenario

Prove DeepSeek reali, punteggio contro il gold, ultima bozza. «Caselle» è: corrette / mancanti / indebite.
«XML» è il conteggio delle caselle spuntate letto da `word/document.xml`.

| Esecuzione | Corretti | «Errati» | Mancanti | Non attese | XML | Caselle |
|---|---|---|---|---|---|---|
| `fin2-dialogo-1` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `fin2-dialogo-2` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `fin2-dialogo-3` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `fin2-conflitto-1` | 57 | 2 | 2 | 0 | 1/13 | 1/0/0 |
| `fin2-pausa-1` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `fin2-ramo-1` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `fin2-ramo-2` | 43 | 2 | 16 | 0 | 1/13 | 1/0/0 |
| `fin2-riprova-ramo-2` | 59 | 2 | 0 | 0 | 1/13 | 1/0/0 |
| `minervino-v3-fin2-1` | 58 | 1 | 2 | 0 | 0/13 | 0/1/0 |
| `minervino-v3-fin2-2` | 22 | 1 | 38 | 0 | 0/13 | 0/1/0 |
| `minervino-v3-fin2-3` | 51 | 1 | 9 | 0 | 0/13 | 0/1/0 |
| `checkbox-v2-fin2-1` | 2 | 0 | 5 | 0 | 1/14 | 0/5/0 |
| `checkbox-v2-fin2-2` | 2 | 0 | 5 | 0 | 1/14 | 0/5/0 |
| `fin2-scelta-checkbox` | 5 | 0 | 2 | 0 | 3/14 | 3/2/0 |
| `compilazione-v1-fin2-1` | 17 | 0 | 1 | 0 | 0/11 | 0/1/0 |
| `compilazione-v1-fin2-2` | 17 | 0 | 1 | 0 | 0/11 | 0/1/0 |
| `cnr-iriss-allegato-a-fin2-1` | 1 | 0 | 0 | 0 | 0/0 | 0/0/0 |
| `cnr-iriss-allegato-a-fin2-2` | 10 | 0 | 0 | 0 | 0/0 | 0/0/0 |
| `trapani-v3-finale-1` (`c7006a9`) | 9 | 0 | 0 | 0 | 0/0 | 0/0/0 |
| `trapani-v3-finale-2` (`c7006a9`) | 9 | 0 | 0 | 0 | 0/0 | 0/0/0 |

**I valori «errati» sono attesi e sempre gli stessi:**
- `p14.s0`: la carica detta dall'utente e presente nella SOURCE è più ampia del gold;
- `p15.s3`: il fax è la correzione libera chiesta dallo script, quindi diverso dal gold per costruzione.
  Compare solo nei dialoghi.

CNR e Trapani non hanno un gold per singolo valore. Ho letto i valori a mano: sono coerenti con le fonti.

### Controlli indispensabili

| Controllo | Esito | Dettaglio |
|---|---|---|
| Rami FORM | superato | nessun paragrafo modificato nelle regioni di altre opzioni, letto dal DOCX |
| Checkbox | superato con riserve | con scelta, solo le caselle autorizzate; senza scelta, vuote. Vedi sezione 4 |
| Identità | superato | `77777777777` in nessun DOCX; i valori non corretti sono solo quelli attesi |
| Firmatario, CF, carica | superato nei dialoghi | 9/9 in 8 dialoghi su 8 |
| Direttore tecnico | superato nei dialoghi | 8/8 in 8 dialoghi su 8 |
| REA e Registro Imprese | superato | `p17.s1` corretto, REA mai nel DOCX, conflitto reale sospeso con domanda |
| Correzioni libere e bozze successive | superato | fax corretto; nessuna perdita tra le bozze; hash delle vecchie bozze coincidenti |
| Pausa e ripresa | superato | terza bozza uguale alla seconda; correzione tentata in pausa non applicata |
| Dichiarazioni e designazioni | superato | nessuna autorizzata, 0 caselle cambiate fuori report |
| «BOZZA NON VERIFICATA» | superato | presente in ogni DOCX; `ready_for_submission` sempre falso |

### Omissioni di Minervino, spiegate separatamente

Le bozze dei dialoghi con i messaggi del test manuale superano la migliore bozza manuale da 60 valori:
61 valori, nessuno mancante, salvo i casi seguenti. Voce per voce in `omissioni-fin2.txt`.

| Esecuzione | Mancanti | Causa | Categoria |
|---|---|---|---|
| `fin2-conflitto-1` | `p17.s1` | conflitto reale: **corretto** | guardia o sospensione |
| | `p15.s1` | evidenza non recuperata | evidenza SOURCE |
| `fin2-ramo-2` | 16 dei soci 2 e 3 | il modello non li propone | proposta LLM mancante |
| `minervino-v3-fin2-1` | `p12.s2` | verifica rinviata dalla politica simulata | ricevuta USER |
| | `p39.cb0` | scelta mai chiesta (sezione 4) | ricevuta USER |
| `minervino-v3-fin2-2` | 27 di soci, direttore e dati aziendali | sospesi in attesa di una scelta mai chiesta (sezione 4) | guardia o sospensione |
| | 7 del firmatario | verifica rinviata dalla politica simulata | ricevuta USER |
| | 3 respinti, più `p39.cb0` | ruolo citato altrove; scelta mai chiesta | associazione al soggetto |
| `minervino-v3-fin2-3` | 7 del firmatario | verifica rinviata dalla politica simulata | ricevuta USER |
| | `p15.s1`, `p39.cb0` | evidenza non recuperata; scelta mai chiesta | evidenza SOURCE |

Nessuna omissione è nella categoria writer/export.

`minervino-v3-fin2-2` resta a 22 corretti, sotto il minimo di 33 del 30 ottobre. Non è un soggetto sbagliato
né un conflitto: `p17.s1`, per esempio, ha il valore giusto ed è sospeso in attesa della scelta. L'utente
legge «Restano vuoti: 34 dati… sospesi in attesa di una verifica», senza che gli venga detto quale scelta li
sblocca.

## 3. Controllo specifico del bug `p65.*`

Il difetto si presenta di rado: il modello ha proposto valori in `p65` in 1 sessione Minervino registrata su
17 prima di questa campagna. Per questo ho distinto quattro prove.

| Prova | Tipo | Sessione con `p65` proposti e ramo confermato? | Esito |
|---|---|---|---|
| `dialogo-11` su `ec78660` (prima della correzione) | DeepSeek reale | sì | **9 valori scritti**: il difetto |
| `fin2-replay-dialogo-11` | replay, 0 token | sì | `p65` vuoti; nessun altro valore cambia |
| `fin2-riprova-ramo-2` | **router e guardia DeepSeek reali**, proposte registrate | sì | **`p65` vuoti**; nessun altro valore cambia; solo l'opzione 4 spuntata |
| `fin2-ramo-1`, `-2` | DeepSeek reale | **no** | `p65` vuoti, ma il difetto **non è stato esercitato** |

La prova decisiva è `fin2-riprova-ramo-2`, 4 chiamate e 61.883 token in input. È una copia di `dialogo-11`
riportata a prima della scelta, con sospensioni ripristinate. Dopo «Scelgo l'opzione 4» le sospensioni
vengono rilasciate esattamente come nel difetto originale (`BLOCKER_ANSWERED`), ma il nuovo blocco tiene
fuori i dati. Rispetto alla bozza con il difetto cambiano solo i 9 `p65.*`.

**Limite:** l'analisi non è stata rigenerata in questa prova. I due tentativi di farla nascere dal vero
(`fin2-ramo-*`) non l'hanno prodotta: il modello non ha proposto `p65` e la guardia ha respinto la conferma
del ramo. Un'analisi nuova che produca di nuovo quel caso non è stata osservata sul codice finale.

## 4. Regressioni

### Confronto con il rapporto del 30 ottobre

| FORM | 30 ottobre | Ora | Esito |
|---|---|---|---|
| Checkbox | 7 / 8 / 7 / 7 | 2 / 2 | **peggiore**: 5 caselle |
| Compilazione | 18 / 18 / 4 | 17 / 17 | **peggiore di 1 sulle migliori** (`p36.cb0`), migliore sul minimo |
| CNR | 1 / 10 | 1 / 10 | uguale, stessa condizione generica rinviata dalla politica |
| Trapani | 9 / 9 | 9 / 9 (`c7006a9`) | uguale |
| Minervino, politica simulata | 58 / 59 / 57 | 58 / 22 / 51 | **peggiore** |
| Minervino, messaggi del test manuale | non misurato | 59 / 59 / 59 | nessun confronto diretto |

### Causa: `7e7383d` («selective incremental conversation»)

Sullo stesso stato della sessione, a parità di prompt (`53bbf21e2a`) e modello, la bisezione offline dà:

| Commit | Elementi selezionati all'export |
|---|---|
| `3a8de0b` (tag demo R2), `de2f5de`, `930aeef` | 12 |
| `7e7383d`, `62f6152`, `cad4102`, `e9a374e`, `5c5dcb0` | 2 |

Nascono da quel commit due comportamenti che insieme producono il problema.

**A. Le sole fonti non segnano più una casella.** `compilation_conversation.py`, `blocked_fields`. È una
regola deliberata, già scritta in `docs/narratore-fluido-2026-11-02.md`, ed è coerente con il tuo controllo
«senza scelta resta vuota». Prima delle sessioni nuove, le caselle documentate venivano scritte: 63 volte
nello storico delle esecuzioni checkbox.

**B. La domanda di scelta non viene posta.** `selective_pool` tiene solo le domande «utili» e scarta la scelta
di qualità, che pure è la prima nel pool. Misurato su Minervino con la politica simulata:

| Profilo | Esecuzioni | Scelta chiesta | Casella scritta |
|---|---|---|---|
| `sezioni-2026-10-30` e `-r2` | 24 | **24** | 23 |
| `sezioni-2026-11-05` | 4 | **0** | 0 |

**Conseguenze:**
- Sul FORM checkbox la bozza finale dice solo «Le informazioni non verificate restano vuote»: **non nomina le 5
  caselle documentate e non le chiede**.
- Quel FORM ha una casella **già spuntata nell'originale**, «Professionista autonomo», mentre la SOURCE indica
  un'altra tipologia. Il 30 ottobre veniva corretta; ora resta spuntata e nessuno lo segnala. Non è una scrittura
  del sistema, ma l'utente può non accorgersene.
- Su Minervino chi non sa di dover dire «Scelgo l'opzione 4» non viene guidato. In 1 esecuzione su 3 questo
  lascia sospesi 27 dati.

**La scelta esplicita invece funziona**, anche fuori da Minervino: in `fin2-scelta-checkbox` due messaggi reali
segnano `p3`, `p13` e `p14`, e tolgono la spunta preesistente nello stesso gruppo a scelta singola. Nient'altro
cambia.

Le esecuzioni precedenti non l'avevano mostrato: i miei dialoghi Minervino davano la scelta spontaneamente, e la
campagna su checkbox e compilazione era stata interrotta dal `402`.

### Altri residui minori

- In pausa, una correzione riceve un messaggio generico («Non sono riuscito a interpretare il messaggio») invece
  dell'invito a riprendere. Il dato non viene toccato.
- `field_outcomes` chiama `nessuna_proposta` un conflitto reale; la domanda all'utente è corretta.
- Il direttore tecnico è 8/8 nei dialoghi, ma 0/8 in `minervino-v3-fin2-2` per la causa B.

## 5. Token, costi e tempi

Stima con cache hit 0,003, cache miss 0,15, output 0,6 USD per milione di token. Solo esecuzioni reali.

| Esecuzione | Chiamate | Input | di cui cache | Output | Segmenti, router ripetuti | Costo | Modello | Più lenta | Durata |
|---|---|---|---|---|---|---|---|---|---|
| `fin2-dialogo-1` | 30 | 769.148 | 511.232 | 85.165 | 7/5, 0/8 | $0,091 | 434 s | 119 s | 6,1 min |
| `fin2-dialogo-2` | 28 | 636.717 | 410.496 | 65.635 | 5/5, 0/8 | $0,074 | 334 s | 106 s | 4,4 min |
| `fin2-dialogo-3` | 25 | 610.030 | 402.176 | 85.178 | 5/5, 0/7 | $0,084 | 418 s | 160 s | 5,6 min |
| `fin2-conflitto-1` | 33 | 841.145 | 508.672 | 67.681 | 7/5, 0/9 | $0,092 | 358 s | 102 s | 5,0 min |
| `fin2-pausa-1` | 40 | 867.370 | 498.304 | 67.339 | 6/5, 1/14 | $0,097 | 366 s | 147 s | 5,5 min |
| `fin2-ramo-1` | 27 | 669.262 | 299.520 | 73.363 | 5/5, 0/8 | $0,100 | 381 s | 105 s | 4,2 min |
| `fin2-ramo-2` | 28 | 696.171 | 388.864 | 64.262 | 6/5, 0/8 | $0,086 | 339 s | 109 s | 4,6 min |
| `fin2-riprova-ramo-2` | 4 | 61.883 | 35.968 | 321 | 5/5, 0/10 | $0,004 | 7 s | 2 s | 0,2 min |
| `minervino-v3-fin2-1` | 26 | 603.659 | 364.032 | 68.802 | 5/5, 0/7 | $0,078 | 350 s | 133 s | 4,7 min |
| `minervino-v3-fin2-2` | 22 | 549.284 | 351.360 | 80.857 | 5/5, 0/5 | $0,079 | 406 s | 129 s | 4,8 min |
| `minervino-v3-fin2-3` | 25 | 628.109 | 411.776 | 65.674 | 6/5, 0/6 | $0,073 | 342 s | 127 s | 4,4 min |
| `checkbox-v2-fin2-1` | 11 | 65.337 | 42.240 | 10.059 | 1/1, 0/3 | $0,010 | 57 s | 44 s | 1,0 min |
| `checkbox-v2-fin2-2` | 15 | 94.652 | 66.304 | 24.592 | 2/1, 0/4 | $0,019 | 136 s | 75 s | 2,3 min |
| `fin2-scelta-checkbox` | 7 | 39.546 | 23.424 | 483 | 1/1, 0/6 | $0,003 | 10 s | 2 s | 0,2 min |
| `compilazione-v1-fin2-1` | 13 | 114.935 | 69.632 | 21.860 | 2/2, 0/4 | $0,020 | 113 s | 66 s | 1,9 min |
| `compilazione-v1-fin2-2` | 13 | 114.820 | 72.704 | 19.514 | 2/2, 0/4 | $0,018 | 101 s | 55 s | 1,7 min |
| `cnr-iriss-allegato-a-fin2-1` | 11 | 67.797 | 40.704 | 17.687 | 1/1, 0/3 | $0,015 | 95 s | 80 s | 1,6 min |
| `cnr-iriss-allegato-a-fin2-2` | 11 | 68.589 | 45.568 | 6.650 | 1/1, 0/3 | $0,008 | 43 s | 28 s | 0,7 min |
| **Totale `5c5dcb0`** | **369** | **7.498.454** | **4.542.976** | **825.122** | | **$0,952** | **4.290 s** | | |

«Segmenti» è tentativi su segmenti; un valore oltre il totale indica un tentativo in più o un recupero.

Oltre alla tabella: la verifica di disponibilità (1 chiamata, 38 token) e le Trapani già pagate su `c7006a9` (27
chiamate, $0,043).

- **Retry:** 0 errori di formato; 1 turno di router ripetuto, sulla correzione in pausa.
- **Provider:** tutte le 369 risposte HTTP 200; nessun `402`, `429` o `5xx`.
- **Esportazione:** riuscita in tutte le esecuzioni; nessuna bozza dichiarata pronta.
- **Turno «Genera ora»:** da 4,4 a 5,9 s nei 4 dialoghi documentati.

## 6. Tipi di prova

| Tipo | Cosa copre |
|---|---|
| **DeepSeek reale** | Le esecuzioni delle tabelle. Le DOCX sono lette dall'XML con `analisi/controllo_docx.py`, indipendente dall'API; rileva il difetto noto di `dialogo-11` |
| **DeepSeek reale su sessione ripresa** | `fin2-riprova-ramo-2` e `fin2-scelta-checkbox`: messaggi e router reali, analisi registrata |
| **Replay offline, 0 token** | `fin2-replay-dialogo-11`; la bisezione di `7e7383d`; la traccia di `export_selection` e `selective_pool` |
| **Test automatici** | 4550 passati e 8 saltati su `5c5dcb0`, dal rapporto precedente. Non rieseguiti: il codice non è cambiato |

## Decisione richiesta

Le cause A e B sono una scelta di prodotto, e non le ho toccate come richiesto.

**La mia raccomandazione:** tenere la regola A, perché coincide con il tuo controllo «senza scelta resta vuota»,
e correggere B. In pratica:
1. far porre di nuovo la domanda di scelta quando sblocca dati o riguarda caselle documentate;
2. far dire alla bozza quali caselle restano vuote e quali erano già spuntate nell'originale;
3. riformulare il criterio su checkbox e compilazione, perché oggi conta come errore un comportamento voluto;
4. rieseguire solo checkbox, compilazione e Minervino con politica simulata.

L'alternativa è tornare a segnare le caselle documentate dalle fonti, ma contraddirebbe il controllo che hai
chiesto.

## Per la prova manuale

L'istanza è sulla 8001 e 5174, con il nuovo profilo. Valgono solo le **sessioni nuove**: quelle vecchie restano con
il profilo precedente. Per vedere il comportamento migliore scrivi spontaneamente la scelta, per esempio «Scelgo
l'opzione 4: …»: oggi il sistema non te la chiede.

Per tornare al profilo precedente basta riavviare il backend con
`MAPI_COMPILATION_PROFILE=sezioni-2026-10-30-r2`.

## Stato

- **Demo ordinaria:** invariata, su `99ab052`; i 143 file del tag `demo-default-r2-20261031` coincidono con il disco.
  Servizi ordinari non avviati né toccati.
- **Sessioni e bozze storiche:** invariate, verificato con hash prima e dopo.
- **`dialogo-11` originale:** intatto, verificato con hash.
- **`STATUS.md` e `relazioni.md`:** invariati.
- **Backup su D::** non toccato, resta incompleto.
- **Git:** nessun commit in questa campagna. Questo rapporto è un file nuovo non committato.
- **Dati:** in `backend/data/compilation-audit/stabilizzazione-soggetti-20261105/`, ignorata da Git: `esecuzioni/`,
  `METRICHE-fin2.json`, `omissioni-fin2.txt`, `minervino-fin2.txt`, `scelta-storico.txt`, `reale/sonda-credito-finale.txt`.
