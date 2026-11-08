# Preregistrazione: opzione FORM e dati immediatamente successivi

25 ottobre 2026. Base `9cb3129`, worktree `tesi-ambiti-form`, branch
`miglioramenti/2026-10-25-ambiti-form`. Solo offline, zero chiamate LLM.
Il working tree ordinario e i dati storici non vengono modificati.

## Diagnosi prima della correzione

I 13 controesempi residui sono due insiemi So.Re.Sa. della campagna rev 2:
sette scritture nel paragrafo dei dati dell'ausiliaria e sei nei blocchi ripetuti
dei componenti RT. Nel primo tentativo una condizione di partecipazione singola
ha scope misto; nel secondo mancano le condizioni sui campi errati. Grounding
fattuale e ricevute di ambito (nel controfattuale, simulate SUPPORTED) non
dimostrano la correttezza del ramo. Non sono nuove scritture reali.

Per i sette dati dell'ausiliaria il FORM contiene localmente: opzione testuale
`[ ] ...`, paragrafo `OPPURE`, opzione `[] ...:` e, dopo uno spazio vuoto, un
paragrafo con campi. R1 non riconosce questi marcatori e termina sui vuoti;
V14 lascia esplicitamente fuori i marcatori ASCII. Una condizione ancorata a
un altro paragrafo non prova la scelta dell'opzione che introduce questi dati.
I sei dati dei componenti RT dipendono invece da intestazioni lontane e blocchi
ripetuti: restano fuori dalla modifica, senza inferire confini o tipi d'impresa.

## Modifica minima proposta

- Riconoscere soltanto la struttura locale di due opzioni ASCII vuote separate
  da `OPPURE` isolato. Entrambe sono paragrafi BODY senza destinazioni proprie;
  la seconda termina con due punti e introduce il primo paragrafo non vuoto
  successivo, contenente destinazioni testuali. Non attraversare tabelle,
  intestazioni, testo intermedio o altre opzioni. Non estendere oltre quel
  paragrafo. Nessuna parola su bandi, avvalimento, RT o forme societarie nella
  regola applicativa. Il riconoscimento non crea checkbox né fatti.
- Riutilizzare condizioni e ricevute esistenti. Richiedere una condizione valida
  ancorata all'intera opzione introduttiva e la decisione USER positiva verificata
  per quei campi; non accettare una condizione lontana, una citazione parziale,
  una ricevuta obsoleta o la semplice verità di un fatto SOURCE.
- Se la condizione manca, applicabilità NON_ACCERTATA e motivazione del vuoto.
  Nessuna nuova condizione inventata; nessun nuovo giro di dialogo in questo fix.
- Nuovo flag persistito `form_option_scope_revision=1`, opt-in lato server nel
  solo worktree sperimentale. Profilo ordinario e creazione storica invariati in
  assenza dell'opt-in; sessioni esistenti non aggiornate implicitamente.
- Punti d'integrazione: `compilation_profile.new_session_flags`,
  `compilation_global_sessions.validated_audit/review_fields` e conservazione
  revisioni, `compilation_scope_review.blocked_source_fields`,
  `compilation_segments.applicability_states`. Nuovo piccolo modulo di sola
  struttura FORM; nessuna modifica a parser, writer, prompt o retrieval.

## Criteri e prove che possono falsificare la soluzione

1. Prima del codice: prova API di JSON valido con valore SOURCE vero e opzione
   omessa; export per ID deve risultare erroneamente ammesso nella base.
2. Dopo: stesso output bloccato; campo indipendente ancora esportabile.
3. Positivo: condizione della stessa opzione, conferma USER verificata e
   attribuzione valida consentono l'export; niente blocco indiscriminato.
4. Negativi: condizione estranea/parziale/respinta, scelta negativa, rinvio,
   revoca, ricevuta cambiata, valore USER isolato, riuso SOURCE e proiezione
   mancante; scelta del ramo non equivale ad autorizzazione di altre clausole.
5. Confini: tabelle, intestazioni, note/esempi, opzioni inline, marcatori non
   vuoti e paragrafi successivi non devono essere inglobati arbitrariamente.
6. Rigioco invariato dei 25 negativi e 245 positivi: ipotesi sette ulteriori
   blocchi, 13 -> 6 residui; nessuna nuova perdita dei 245 con condizioni
   soddisfatte né dei 211 con sole ricevute storiche. Non cambiare gold o scope
   delle risposte USER per far passare i test.
7. Regressioni V14/K3/P2, monolitica, profili/sessioni precedenti, suite backend
   e Ruff. Rete disabilitata; database e storage temporanei.
8. Commit del solo fix con prove, prima/dopo e rollback tramite revert in
   worktree isolato; nessuna migrazione. Documentazione conclusiva separata.

Se il replay introduce falsi rifiuti o richiede una nuova interpretazione
semantica generale, documentare il limite e non promuovere la modifica.
L'eventuale pubblicazione del branch richiede controllo di file e cronologia;
nessun merge né attivazione nell'app ordinaria. Budget inferenze: **0 token**.

Grezzi: `backend/data/compilation-audit/ambiti-form-20261025-01/` nel repository
originario; nuovi file, nessun aggiornamento degli artefatti precedenti.
