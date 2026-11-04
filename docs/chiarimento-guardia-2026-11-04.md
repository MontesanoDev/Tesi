# Loop di chiarimento su «Numero iscrizione Camera di Commercio» (4 novembre 2026)

Worktree sperimentale, branch `narratore-chiarezza/2026-10-31`, base `cad4102`. Demo e dati
ordinari non toccati; nessun push o merge; nessuna promozione. La sessione preservata
`65c252e8` è stata letta e mai modificata: le prove girano su copie temporanee.

## Diagnosi sui dati della sessione

| Domanda | Risposta, con evidenza |
|---|---|
| Cosa era in sospeso | Una sola destinazione, `p17.s1` («al n.» dopo «Camera di Commercio di»), `review_kind=ambiguous` con due alternative documentate. Non era una sospensione del narratore: `held_candidate_ids` è vuoto. La condizione che la governa, `s1_c_soc`, era già confermata dall'utente |
| Cosa arriva al router | Il target 24, cioè `field:p17.s1`. In entrambi i turni il router produce la modifica giusta: `edit_fields`, target 24, `VALUE 01234560981` |
| Perché il chiarimento non si applica | **Non è un problema di associazione: rifiuta la guardia.** Verdetto `result=SUPPORTED`, `scope_result=AMBIGUOUS` in entrambi i turni. Motivazione: la condizione «governa anche p14.s1, p15.\*, p16.\*, p17.s0» e il messaggio non ribadisce la partecipazione |
| Il falso conflitto nasce a monte? | Sì, dal **modello**, nel segmento 1: dà a REA e Registro Imprese la stessa proprietà e marca il campo `ambiguous` («il modulo non distingue…»), benché la SOURCE dica che il REA «non è» il numero del Registro Imprese. Il backend valida due valori documentati e chiede la scelta. La P. IVA non è mai tra le alternative |
| Perché la domanda si ripete | Il ramo di rifiuto del router non cambia lo stato (nessuna revisione dopo la 9), non ricorda il rifiuto precedente e usa un testo fisso: nulla poteva interrompere il ciclo |

**Causa del rifiuto.** La guardia riceve già la destinazione unica e `user_conditions` con
`CONDITION_TRUE`, ma il suo contratto non diceva mai cosa significhi `user_conditions`. In più la
regola «una stessa proposizione deve governare tutte le destinazioni elencate» veniva applicata a
un valore, leggendo la lista `scope` della condizione come ambito della risposta. Il rifiuto è
**intermittente**, quindi dipende dal modello (vedi la tabella sotto).

## Correzione (generale, nessuna eccezione per FORM, campo o valore)

1. **Contratto della guardia** (`FORM_SCOPE_TASK`):
   - `applies=true` è un'indicazione USER già registrata, non una scelta mancante;
   - una condizione non confermata resta non confermata;
   - `scope` non è l'ambito di un VALUE;
   - la verifica della destinazione resta: il solo valore non identifica un campo.
2. **Rifiuto ripetuto** (`blocked_reply_text`): al secondo rifiuto consecutivo sullo stesso dato il
   sistema non richiede più la stessa cosa. Spiega con fatti del backend cosa blocca (clausola da
   confermare, risposta che varrebbe per più campi, campo citato) e dà le vie d'uscita. Il primo
   rifiuto resta invariato. La motivazione del modello resta privata.

**Non cambiati:** verdetti e loro combinazione, autorizzazioni, ricevute e digest d'ambito,
condizioni, bozze precedenti, controlli all'export. Non ho forzato il verdetto via codice quando
la destinazione è una sola: avrebbe nascosto rifiuti legittimi.

## Verifica reale contenuta

Stessa richiesta della sessione, su copia temporanea, con la risposta del router registrata. Solo
la guardia chiama DeepSeek: 73 chiamate e 1,6 M di token in totale (al massimo 0,25 USD, stima).

| Messaggio | Contratto precedente | Contratto finale |
|---|---|---|
| Turno 19, testo esatto | rifiutato nella sessione reale; 3/3 accettato nel replay | 2/2 accettato |
| Turno 18, testo esatto | rifiutato nella sessione reale; 1/3 accettato nel replay | 2/2 accettato |
| «Il numero è 01234560981.» (nessun campo nominato) | 0/3 accettato | 0/3 accettato |
| Numero dichiarato dell'albo (altro campo) | 0/2 accettato | 0/2 accettato |
| «Metti pure quel numero lì, tanto è uno dei due.» | 0/2 accettato | 0/2 accettato |
| Condizione non confermata (copia modificata) | non provato | 0/2 accettato |
| **Valore attribuito a un altro soggetto** | **2/2 accettato** | **2/2 accettato** |

- Le prime due versioni del contratto, senza l'esempio finale, accettavano 12/12 chiarimenti
  validi ma **allargavano la guardia**: accettavano anche «Il numero è…» (6/6). Le ho scartate: da
  qui l'esempio esplicito nel contratto.
- Il primo giro di prove usava messaggi troncati e non era una baseline valida: conservato, ma
  escluso dalla tabella.

**A valle, sulla copia della sessione reale (guardia e narratore simulati):**
- valori scritti da 46 a 47, con `p17.s1 = 01234560981` e provenienza USER;
- nessun altro campo cambiato, caselle uguali, `ready_for_submission` falso;
- bozza precedente intatta byte per byte.

## Test

`test_clarification_loop.py`, 9 casi: 4 scenari su FTS5 e Qdrant più 1 sul contratto:
- **regressione del dialogo:** conferma, prima bozza, chiarimento accettato, nuova bozza, vecchia
  bozza intatta;
- **negativo con destinazione realmente ambigua:** nessuna scrittura, stessa versione, nessuna
  domanda ripetuta;
- **rifiuto d'ambito ripetuto:** nomina il campo;
- **condizione aperta:** nomina la clausola da confermare.

Il simulatore della guardia riproduce i verdetti reali registrati.

**Commit `e9a374e`.**
- Suite backend: 4.390 passati e 8 saltati; Ruff PASS.
- Rollback: albero uguale al genitore; sul revert falliscono tutti i 9 casi nuovi.

## Limiti aperti, da decidere

- **La guardia accetta un valore attribuito a un altro soggetto** («…di Studio Rossi S.r.l. …»),
  col contratto vecchio e col nuovo. È un limite preesistente, non corretto qui: è il punto più
  serio emerso.
- **Il verdetto resta del modello.** I campioni sono piccoli: migliora la frequenza ma non è una
  garanzia. Se rifiuta ancora, il ciclo non si ripete.
- **Il falso conflitto REA/Registro Imprese resta a monte**, dipende dal modello e non è corretto.
  Nella sessione la domanda «Quale valore vuoi utilizzare…?» non mostrava neppure i valori.
- **Lentezza preesistente:** ogni controllo di ricevuta ricalcola il digest dell'intero FORM; una
  narrazione costa più di un minuto di CPU sulla sessione Minervino.

Evidenze: `backend/data/compilation-audit/chiarimento-loop-20261104/` (esclusa da Git).
