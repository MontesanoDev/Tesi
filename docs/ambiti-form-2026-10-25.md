# Opzione FORM e dati del ramo: correzione incrementale offline

25 ottobre 2026. Revisione autoriale, non indipendente. Lavoro richiesto sui
tredici controesempi residui, senza nuove inferenze o campagne E2E.

## Esito dei replay

La nuova protezione blocca sette ulteriori scritture storiche di dati aziendali
nel ramo dell'ausiliaria. Dei 25 errori della prima segmentazione risultano
bloccati 19 anziché 12; restano sei casi nei blocchi dei componenti RT.
Non sono nuove scritture reali: sono gli stessi output registrati passati nei
gate correnti, prima e dopo il fix.

| Misura | Base `9cb3129` | Nuovo controllo attivo |
|---|---:|---:|
| Errori ancora ammissibili, guardia d'ambito simulata SUPPORTED | 13/25 | 6/25 |
| Errori ancora ammissibili, sole ricevute USER registrate | 7/25 | 4/25 |
| Scritture corrette consentite, condizioni soddisfatte e ricevute simulate | 245/245 | 245/245 |
| Scritture corrette consentite, sole ricevute registrate | 211/245 | 211/245 |

Le 34 corrette non consentite con sole ricevute registrate erano già escluse
nella base: i vecchi record rev 2 non attestano l'ambito richiesto dalla rev 3.
Il replay non simula nuove risposte USER né trasforma una risposta negativa in
positiva. Nella variante SUPPORTED rigenera soltanto le prove d'ambito delle
risposte positive già presenti, per verificare la resistenza a una guardia LLM
troppo permissiva. Revisione/sospensioni del narratore sono escluse dal confronto
dei gate, come nel protocollo precedente. Nessun benchmark storico è riscritto.

## Diagnosi dei tredici casi

Tutti appartengono a So.Re.Sa. nella campagna `sezioni-resilienti-20261022-01`.
I fatti SOURCE erano veri, ma riguardavano l'impresa concorrente. Il loro
grounding non dimostrava che il campo descrivesse quella stessa impresa.

| Tentativo e destinazioni | Dipendenza FORM mancante o errata | Esito nuovo |
|---|---|---|
| `soresa2023-1`: `p127.s1`, `p127.s2`, `p127.s3`, `p127.s4` | L'opzione introduttiva del paragrafo 125 riguarda l'altro operatore di cui si usano i requisiti. I campi dipendevano invece dalla condizione mista `s2_c_sing`, ancorata al paragrafo 33 e confermata per partecipazione singola. | Quattro bloccati anche con ricevuta SUPPORTED simulata. |
| `soresa2023-2`: `p127.s2`, `p127.s3`, `p127.s4` | Stessa opzione locale omessa; elenco conditions vuoto. | Tre bloccati. |
| `soresa2023-1`: `p44.s0`, `p44.s1` | Blocco ripetuto del componente RT, condizione mista di partecipazione. | Due residui. |
| `soresa2023-2`: `p43.s8`, `p43.s9`, `p44.s0`, `p44.s1` | Stesso blocco del componente RT, condizioni omesse. | Quattro residui. |

Il codice R1 riconosce checkbox native e glifi; non i marcatori ASCII `[ ]` e
`[]`. Inoltre una riga vuota termina la continuazione R1. V14 documenta la
stessa esclusione dei marcatori ASCII. Perciò il paragrafo dei dati successivi
non aveva un obbligo locale d'applicabilità indipendente dal JSON del modello.

Per i componenti RT, l'intestazione generale è distante e governa più schede,
separate da righe decorative e nuove opzioni. Non c'è la struttura locale
corretta qui. Estenderne lo scope automaticamente con nomi di ruoli, parole
chiave o posizione specifica del bando non è giustificato dalle prove raccolte.
I sei casi restano esplicitamente aperti; non si sostiene che richiedano per
forza una riscrittura, né che siano risolti dalle campagne recenti favorevoli.

Inventario con riferimenti FORM/SOURCE/USER e giudizi prima/dopo nei grezzi
`inventory-13.json`, `out/replay-before.json` e `out/replay-after.json`.

## Comportamento introdotto

Un piccolo controllo del catalogo riconosce due opzioni ASCII vuote e fisse,
in paragrafi del corpo, separate da un paragrafo `OPPURE`. La seconda termina
con `:` e introduce il primo paragrafo dati successivo. Sono ammessi spazi
vuoti; tabelle, altre opzioni e testo intermedio interrompono il collegamento.
Non vengono inglobati altri paragrafi dati. Non ci sono nomi di bandi, ID di
destinazione o tipi societari nella regola applicativa.

Una condizione valida deve citare l'intera opzione introduttiva, eventualmente
senza il marcatore della casella, ed essere collegata ai campi governati. La
scelta richiede una ricevuta USER positiva, verificata per lo stesso ambito e
ancora attuale. Una citazione parziale, una condizione distante, un fatto SOURCE
vero o una risposta riferita ad altri campi non bastano. La proiezione viene
ricostruita e rivalidata anche all'export dall'originale e dalla risposta salvata.

Se la condizione è assente, lo stato è NON_ACCERTATA con motivo leggibile.
Se è riconosciuta ma aperta, i normali slot di dialogo possono risolverla;
il test API positivo esporta dopo la conferma pertinente. Il backend non
inventa condizioni mancanti e non genera nuove domande per quelle omesse.

La scelta dell'opzione non conferma altri rami né autorizza una dichiarazione
procedurale. V14 e K3 restano operativi nei loro ambiti attuali; questa modifica
non estende il riconoscimento di V14 ai marcatori ASCII e non corregge le sue
limitazioni preesistenti. Nessuna modifica a prompt, parser, writer o RAG.

## Isolamento e file

Base effettiva: `9cb3129`, successiva all'integrazione ordinaria del 24 ottobre.
Branch `miglioramenti/2026-10-25-ambiti-form`, worktree
`/home/montesano/tesi-ambiti-form`. Il working tree ordinario non è stato usato
per gli interventi e non si applica automaticamente questo fix all'app.

- `backend/app/compilation_form_option_scope.py`: struttura locale, legami e veto.
- `backend/app/compilation_global_sessions.py`: proiezione, motivazione e
  conservazione della revisione della sessione.
- `backend/app/compilation_scope_review.py`: veto comune per SOURCE e USER.
- `backend/app/compilation_segments.py`: applicabilità NON_ACCERTATA.
- `backend/app/compilation_profile.py`: creazione opt-in della sola candidata.
- `backend/tests/test_compilation_form_option_scope.py`: prove sintetiche e API.

Attivazione tecnica della candidata, **non eseguita sull'app ordinaria**:
`MAPI_FORM_OPTION_SCOPE_REVISION=1`, profilo persistito
`sezioni-opzioni-2026-10-25`, flag `form_option_scope_revision=1`.
Il profilo predefinito resta `sezioni-2026-10-24`. Il percorso `storico` ignora
il nuovo opt-in. Le sessioni esistenti mantengono i propri flag, anche se
l'ambiente cambia tra creazione e analisi. Nessuna migrazione o dipendenza.

## Verifiche

Preregistrazione: [piano-ambiti-form-2026-10-25.md](piano-ambiti-form-2026-10-25.md),
copiata e identificata da SHA-256 nei grezzi prima di modificare il codice.
Rete disabilitata e database/storage temporanei per i test.

- Prima: 2 FAIL / 2 PASS; export API restituisce 200 invece del 409 atteso sul
  campo dell'opzione omessa, mentre il campo indipendente è correttamente ammesso.
- Dopo: 38 test nuovi PASS, inclusi export positivo/negativo, motivazione del
  vuoto, revoca, rinvio, citazione parziale, ricevuta obsoleta/estranea, valore
  USER, riuso SOURCE, confini strutturali e conservazione del profilo.
- Regressioni mirate: 286 PASS e 5 SKIP iniziali per copie locali mancanti;
  acquisiti i file storici identici, 134 PASS comprendono i casi prima saltati,
  K3, V14 e recupero del narratore. Nessuno skip finale lasciato senza verifica.
- 26 casi avversari K3 congelati: output identico byte per byte alla base.
  Non si riattiva né si modifica la proposta P2 falsificata.
- Replay 25 negativi / 245 positivi: risultati nella tabella iniziale.
- Suite completa: **3898 PASS in 406,14 s**, senza skip; Ruff completo PASS.
- 1244 file controllati, tra codice ordinario, documenti di stato, baseline e
  artefatti storici: hash invariati. Le 29 sessioni live e gli originali nel
  database risultano identici nelle istantanee in sola lettura.

## Commit e rollback verificato

Fix: `ddb8cb764bcb8dece4a43f80499b4933e759ed08`. Contiene soltanto il nuovo
controllo, le sue integrazioni, i test e la preregistrazione. Il rapporto finale
e gli aggiornamenti di continuità sono in un commit documentale separato.

Rollback del codice, da effettuare sul branch interessato in un worktree isolato:

```bash
git revert ddb8cb764bcb8dece4a43f80499b4933e759ed08
```

Eseguito realmente in `/home/montesano/tesi-ambiti-rollback`: revert
`c16d2a35e9233862b6b6d20e3daf741586c0ee09`, albero identico alla base `9cb3129`
(`eaba5e8bd835411be26aca7da0c10dad99467bf3`). La riproduzione originale torna
a **2 FAIL / 2 PASS**, con gli stessi HTTP 200 indebiti. Il primo lancio della
sonda esterna non trovava i moduli dei test: conservato il log, poi eseguita
la stessa sonda nel percorso test del worktree, senza alterare codice applicativo.

Il revert non modifica database, sessioni, originali o altri fix. Non servono
migrazioni né cambi di dipendenze. Rimuovere la sola variabile d'ambiente
disabilita la candidata per le nuove sessioni; quelle esistenti mantengono il
flag persistito. Il revert rimuove il controllo anche per queste ultime e
ripristina il rischio precedente: è una verifica di reversibilità, non un
suggerimento di disattivazione sull'app. Non si cancellano decisioni o scritture
già registrate; la rivalidazione ordinaria resta obbligatoria.

Grezzi esclusi da Git:
`backend/data/compilation-audit/ambiti-form-20261025-01/`.
Backup separato previsto alla chiusura:
`backend/data/compilation-audit/ambiti-form-backup-20261025/`, con bundle Git,
audit/rapporti e manifest SHA-256; esclusi database, credenziali e originali.

## Limiti e prossima verifica possibile

Nessuna nuova misura di qualità LLM, latenza, costo o copertura E2E: **zero
inferenze**. La conservazione di 245 scritture è provata in questo corpus e
con quelle condizioni, non universalmente. Il riconoscimento è deliberatamente
limitato a questa struttura di alternative e al primo paragrafo dei dati.
Un'opzione legittima con condizione omessa o citazione incompleta può restare
vuota; questo rischio di omissione va misurato in una prova futura. Una citazione
completa non dimostra da sola che la condizione del modello sia semanticamente
corretta: la guardia d'ambito e i controlli di attribuzione restano necessari.

Eventuale micro-verifica successiva, da autorizzare e preregistrare: due
tentativi indipendenti, un So.Re.Sa. con partecipazione singola e senza
avvalimento, più un FORM sintetico della stessa struttura con ramo delegato
applicabile e SOURCE dedicata al soggetto corretto. Scenari/input/hash congelati
prima delle chiamate, tetto proposto 750.000 token complessivi, nessuna
sostituzione di fallimenti; arresto alla prima scrittura non dimostrata o
aggiramento. Misurare proposte nel ramo, veti effettivamente esercitati, vuoti
fondati/superflui, export, token e latenza. Se il modello non propone il ramo
negativo, non presentare l'assenza di errori come prova del nuovo veto.

Non si avvia questa prova, non si promuove la candidata e non si prosegue con
gli altri filoni senza una nuova decisione.
