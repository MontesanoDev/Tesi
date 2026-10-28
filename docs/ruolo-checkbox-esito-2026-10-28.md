# Minervino: carica e opzione societaria, verifica offline

Intervento iniziato il 27 e concluso il 28 ottobre 2026. Base `0d62a11`, branch
`fix/2026-10-27-ruolo-checkbox`, worktree `tesi-ruolo-checkbox-20261027`.
App ordinaria non modificata né riavviata; nessuna chiamata DeepSeek, push,
merge, modifica di sessioni originali o benchmark. Nessuna migrazione.
Le tre correzioni precedenti di nome, separatori e ricevute restano incluse.

## Risultato del rigioco

| Destinazione | Prima | Dopo | Prova |
|---|---|---|---|
| p14.s0, «in qualità di» | Vuota, hold SOURCE | Amministratore unico e rappresentante legale | Carica nella SOURCE del soggetto scelto; decorrenza 02/10/2026, riferimento 27/10/2026; ricevuta USER e ambito FORM verificati |
| p39.cb0, opzione societaria | Nessuna proposta booleana; unchecked | `true`, checked; glifo ☒ | Conferma USER specifica già persistita, condizione di rappresentanza ancorata alla stessa opzione e al suo controllo |
| 56 scritture precedenti | Presenti | Identiche | Confronto per destinazione e valore scritto |
| Altre 12 checkbox native | Unchecked | Identiche anche nell'XML | Nessuna deselezione o selezione aggiuntiva |

**58 scritture totali**, due aggiunte, nessuna rimossa o modificata. Non sono
58 nuove valutazioni indipendenti: le 56 mantengono la revisione disponibile,
le due aggiunte sono state verificate in questa revisione autoriale.
Le risposte USER e i relativi valori persistiti sono identici prima/dopo:
non è stata simulata una nuova conferma per sbloccare i campi.

Il confronto XML cambia soltanto i paragrafi del ruolo e della casella. I cinque
separatori precedentemente corretti sono conservati. LibreOffice ha generato
il PDF; ispezionate visivamente le pagine 1 e 3, con ruolo e spunta visibili.
Controllati sia `w14:checked=1` sia il glifo nel `w:sdtContent`. Non è stata
applicata una modifica manuale al DOCX e il writer non è stato cambiato.

## A — errore temporale del narratore

Commit `f3bc281`: [diagnosi, motivazione esatta e limiti](ruolo-checkbox-2026-10-27.md).
La data corrente era **già presente** nella richiesta del narratore. La
contraddizione nasce nella sua risposta, poi conservata dal backend come hold
SOURCE: non era un errore di parsing o confronto delle date nel backend.

Il controllo aggiunto respinge soltanto una motivazione temporale dalla forma
chiusa verificabile, se esiste l'intera catena SOURCE/USER/FORM. Non rilascia
genericamente le sospensioni. Il record conserva la motivazione originale,
marcata `REJECTED_TEMPORAL_COMPARISON`, e la prova con date, ricevuta, citazione
e impronta del corpus. La prova viene ricalcolata all'export sulle SOURCE correnti.

File: `compilation_temporal_hold.py`, collegamenti in
`compilation_global_dialogue._hold_updates` / `narrate` e
`compilation_global_sessions._selected`, `test_temporal_role_hold.py`.
Nessuna modifica ai prompt. Il rigioco usa il motivo effettivamente registrato,
non una nuova valutazione LLM né una risposta USER aggiunta.

Limite: questo è un riconoscitore conservativo di un'asserzione temporale
esplicita, con formulazioni e struttura SOURCE delimitate. Una parafrasi diversa
resta sospesa. Non dimostra di riconoscere ogni cessazione, negazione o
contraddizione in linguaggio naturale. Non modifica retroattivamente i messaggi
storici errati né dimostra la qualità di una nuova narrazione dal vivo.

## B — ricevuta di rappresentanza e checkbox

La proposta LLM originaria non conteneva né un booleano né un gruppo di scelta
per p39.cb0. Esisteva però `s2_c_soc_ing`, con prova FORM sul testo dell'opzione,
ambito esplicito comprendente la checkbox e risposta positiva alla domanda sulla
qualità di rappresentante della società di professionisti o di ingegneria.

La ricevuta comprendeva 41 destinazioni testuali, senza la checkbox fra gli
`affected_fields`; la sua impronta includeva però già lo scope esplicito della
condizione e il FORM. Non viene ampliata né rifirmata. Due punti impedivano
il riuso: `_receipt_control` accettava solo `legal_type`/`participation` con
citazione di tutto il paragrafo; `blocked_user_fields` richiedeva poi una nuova
ricevuta `choice:`, inesistente per il collegamento derivato dalla condizione.

La modifica in `compilation_branch_evidence` riconosce soltanto il collegamento
di rappresentanza provato, con conferma esplicita del ruolo e del tipo societario,
ricevuta valida, checkbox nello scope originale e opzione completa. Consente
soltanto una coda neutra quale «avente la seguente»; una dichiarazione ulteriore
non è assorbita nella conferma. Riusa il gruppo FORM «IN QUALITÀ DI», preserva
cardinalità ignota e controlli di conflitto; non inventa alternative false.

`compilation_scope_review` accetta questo collegamento solo per il valore USER
derivato. Non trasforma USER in SOURCE, non allenta il gate SOURCE e non elimina
altre condizioni pendenti. La proposta booleana è una derivazione backend
tracciata della ricevuta esistente, **non** un nuovo fatto o output del modello.

Il gruppo risultante è `form_receipt_p39.cb0`, validato come `GROUNDED_GROUP`;
`materialize_choices` e il writer nativo esistenti applicano la selezione.
Una conferma generica della società, un rinvio, l'assenza della ricevuta,
un'altra opzione già scelta, un'altra condizione irrisolta o una ricevuta
alterata non autorizzano la spunta. Le dichiarazioni legali non sono comprese.
Il supporto resta circoscritto alla rappresentazione nativa qui riconosciuta.

File B: `compilation_branch_evidence.py`, `compilation_scope_review.py`,
`test_representation_checkbox_receipt.py`, questo rapporto, STATUS e relazioni.

## Verifiche riproducibili

- A prima del fix: **1 FAIL / 12 PASS**; B prima del fix: **1 FAIL / 12 PASS**.
  I due fallimenti riguardano precisamente il rilascio della contraddizione
  temporale e il collegamento della ricevuta al controllo.
- Test finali A+B: **32 PASS**. Carica futura, cessata, persona diversa,
  SOURCE contraddittorie, data assente/ambigua, motivo misto, revoca USER,
  FORM/SOURCE cambiati, rivalidazione del rilascio all'export; selezione positiva,
  conferme generiche, SOURCE senza USER, rinvio, falsificazione del collegamento,
  conflitti, condizioni ulteriori pendenti, stato interno e glifo Word.
- Suite backend: **4.050 PASS**, zero FAIL/SKIP, 449,76 secondi; Ruff PASS.
  Comprende regressioni FORM/SOURCE/USER, V14, K3, scope e veto di export.
  Sette artefatti locali necessari ai test sono stati copiati dalle acquisizioni
  precedenti con confronto degli hash; non entrano nel commit.
- Rigioco dei gate, prima/dopo con identici input e supporto caselle testuali
  attivo: risultati JSON identici. **0/25** errori storici esportabili, anche
  simulando il controllo positivo dell'ambito USER. Positive: **243/245** con
  ambito simulato, **197/245** con ricevute registrate; insieme esteso
  **236/240** e **226/240** rispettivamente. I rifiuti residui erano già presenti:
  non si dichiara il recupero di tutte le scritture storiche.
- PDF di controllo e confronto dei report/XML: soltanto le due aggiunte attese.

Il replay usa un database nuovo popolato da una lista chiusa di tabelle del seed,
senza configurazioni o credenziali AI; il trasporto di rete è disabilitato.
L'export attraversa `export_selection`, `generate_draft` e i gate finali.
Nessun frontend modificato: non è stata rieseguita la sua suite.

## Vuoti e limiti conservati

Resta il hold USER su p49.s3. p46.s1 rimane rinviato: la domanda originale
attribuiva la data di iscrizione a un professionista diverso dal destinatario
dello slot. È un difetto di dialogo separato, **non corretto** qui; non sono state
scritte nessuna delle due date né aggiunte domande per forzare il risultato.
Le altre decisioni rinviate e le dichiarazioni non autorizzate sono invariate.

La motivazione temporale storica è falsa rispetto alle prove e resta leggibile
come motivazione respinta, non come blocco valido. Nessun nuovo motivo di
sospensione è stato introdotto. Non si afferma che tutti i motivi storici del
narratore siano ora corretti: rimane il problema di attribuzione sopra descritto.

## Versionamento e rollback

Due commit locali distinti: A `f3bc281`; B è il commit che introduce questo
rapporto (ottenibile con `git log -1 --format=%H -- docs/ruolo-checkbox-esito-2026-10-28.md`).
I due fix non cambiano flag, schema del database, dipendenze o dati originali.
La selezione dei comportamenti storici per profilo resta invariata.

Rollback eseguiti in due worktree separati, seguiti dal rigioco dello stesso
seed e da **45 test PASS ciascuno**, compresi nome, separatori e ricevute:

| Rollback | Scritture | Ruolo | Checkbox societaria |
|---|---:|---|---|
| Solo A | 57 | Vuoto, hold conservato | Selezionata |
| Solo B | 57 | Compilato | Invariata, unchecked |

In entrambi sono preservati i 56 valori precedenti e non sono aggiunte risposte
USER. Le prove del rollback riguardano il codice finale; il completamento della
documentazione non ne modifica alcun file Python.

Su una copia pulita del branch finale, ciascun rollback si esegue separatamente:

```bash
# A: annulla il confronto temporale, conserva B e le tre correzioni precedenti
git revert --no-edit f3bc281

# B: su un'altra copia del branch finale, annulla soltanto il link della checkbox
git revert --no-edit SHA_DEL_COMMIT_B
```

Nessuna eliminazione di sessioni, file o documenti già prodotti. Per utilizzare
in futuro il codice di un rollback servirebbe il normale riavvio dell'istanza
interessata; **non è stato eseguito sull'app ordinaria**. Non fare reset o clean.

## Artefatti privati

Acquisizioni nuove in `backend/data/ruolo-checkbox-20261027-01/` di questo worktree:
`A-before.txt`, `B-before.txt`, `targeted-final.txt`, `backend-full.txt`,
`AB-report.json`, `AB-state.json`, `comparison.json`, `gate-comparison.json`,
`AB-bozza.docx`, `pdf/AB-bozza.pdf` e script di rigioco. Sono esclusi dai commit.
Il seed e il confronto prima provengono dal backup verificato
`tesi-backups/diagnosi-conferme-docx-20261027-01`, mantenuto immutato.
Riverificati alla fine tutti i suoi **328 file**, nessuna differenza. Non si
dichiara un confronto byte per byte dell'intero database dell'app ordinaria:
non è stato usato come database di lavoro né scritto da questi script.
Backup separato dei nuovi artefatti e dei due commit in
`/home/montesano/tesi-backups/ruolo-checkbox-20261027-01/` e copia su
`D:/Backup-tesi-2026-10-23/ruolo-checkbox-20261027-01/`, con manifest SHA-256.
Le acquisizioni di sessione e i DOCX rimangono privati, fuori da Git.

Fermarsi dopo la consegna. Nessuna adozione automatica o nuova campagna.
