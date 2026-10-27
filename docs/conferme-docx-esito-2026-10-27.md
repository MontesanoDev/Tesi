# Conferme USER e rendering DOCX — esito offline del 27 ottobre 2026

## Esito e perimetro

**Recuperato il nome del sottoscrittore; corrette le parole unite; rese esplicite
le ricevute delle risposte. Restano irrisolti il hold SOURCE sulla carica e la
mancata proposta della checkbox di rappresentanza.** Non si dichiara risolto
l'intero caso. Nessuna inferenza, attivazione nell'app ordinaria, merge o push.

Branch `fix/2026-10-27-conferme-docx`, base pubblica `796afaf`.
La [diagnosi preregistrata](diagnosi-conferme-docx-2026-10-27.md) è nel commit
`ac980859c294941f806eb23e393e59f721dbff23`, precedente ai fix. Le prove grezze e il
confronto con dati personali sono **privati**, esclusi da Git, in
`backend/data/compilation-audit/diagnosi-compilato7-20261027-01/`
del checkout ordinario. Non pubblicare i DOCX, i PDF, le SOURCE o le sessioni.

## Correzioni separate

| Commit | File e comportamento | Prova prima/dopo |
|---|---|---|
| `fa83800a35ecae9eeda9d0a750a96b7c8d41dcd9` | `compilation_source_reuse.signatory_fields` conserva label e citazione FORM già validate; `compilation_scope_review.target` usa lo stesso fallback della domanda quando il modello le omette. Nessun hash ignorato o ricevuta ricreata. | Ricevuta valida nell'audit iniziale ma invalida dopo il riuso → valida anche dopo. Test per cambi di FORM, condizioni, destinatario, valore, citazione e revoca continuano a bloccare. |
| `3cfd52137f689bb3c11b036d612b6140c6e6ddf6` | `docx_templates._replace_slot` separa parole alfabetiche adiacenti a leader di puntini. Esclusi codici maiuscoli, cifre, underscore, punteggiatura e FORMTEXT nativi. | Sei casi positivi prima fallenti, anche su run separati; codici/date/controlli invariati. Cinque spazi aggiunti nel caso reale, nessun valore SOURCE cambiato. |
| `0dda3ffe7cb19edbd5ceed2860374d8baa69b867` | `compilation_global_dialogue.continuation_receipt` nomina condizioni confermate/escluse, dati registrati, decisioni pendenti, rinvii e risposte non accettate. | Due test prima fallenti. Registrazione non presentata come scrittura; luogo/data pendenti distinguibili dalle altre risposte nello stesso turno. Nessuna nuova domanda o autorizzazione. |

Nessuna dipendenza o migrazione. I test nuovi usano dati sintetici, senza
incorporare la conversazione privata. Il fix dei separatori è deliberatamente
limitato: non è un correttore generale della tipografia né dei codici composti.

## Rigioco del documento

Creati due database temporanei con un elenco esplicito di tabelle documentali e
la sola sessione interessata; nessuna tabella delle credenziali copiata.
Rete disabilitata nel processo. Usati `export_selection`, `generate_draft`,
`_selected`, `checked_user_fields` e le rivalidazioni alla persistenza.
Nella variante corretta l'audit viene ricalcolato dagli output immutabili e dalle
stesse SOURCE: decisioni e hold rimangono identici. Nessuna spunta o dato aggiunto
manualmente al Word.

Questo ricalcolo è stato eseguito **soltanto nella copia offline**. Il fix previene
la mutazione della destinazione nelle nuove risposte; non migra automaticamente
gli audit storici già incoerenti. Non si sostiene che riaprire oggi la sessione
nell'app ordinaria faccia comparire il nome: la sessione live è rimasta intatta.

Il rigioco della base riproduce **byte per byte** il documento osservato.

| Elemento | Prima | Dopo |
|---|---|---|
| Nome del sottoscrittore, p12.s0 | Segnaposto | Valore USER già registrato |
| Scritture fattuali/USER | 55 | 56; tutte le 55 precedenti preservate |
| Separatore prima dell'Ordine, p43.s3/p45.s3/p49.s0/p53.s0 | `professionaleOrdine` | `professionale Ordine` |
| Separatore dopo la sezione, p53.s1 | `Adella` | `A della` |
| Carica, p14.s0 | Vuoto, hold SOURCE | Invariato |
| Rappresentanza societaria, p39.cb0 | Checkbox non selezionata | Invariata |
| Altre checkbox native | 12 non selezionate | Invariate |

Solo i paragrafi 12, 43, 45, 49 e 53 differiscono. I PDF di controllo hanno nove
pagine; le unioni di parole non compaiono più nel testo estratto. Ispezionate
visivamente pagine 1 e 3. Tutte le tredici caselle conservano stato XML
`w14:checked=0` e glifo `☐`. I test sintetici del writer nativo verificano anche
stato selezionato e glifo coerente: non sono un'autorizzazione a selezionare le
caselle di questa sessione.

## Problemi che restano aperti

**Carica:** esiste una proposta SOURCE riutilizzata e la condizione USER è
confermata. Il narratore la sospende trattando come futura una decorrenza
antecedente alla data di riferimento già presente nella richiesta. Il backend
registra una motivazione ancorata, ma non verifica la correttezza del ragionamento
temporale. Il riesame SOURCE corrente richiede strutture di subject binding
assenti nella proposta di riuso. La diagnosi non giustifica il rilascio di tutti
i hold SOURCE o l'uso di una conferma USER come prova della carica.

**Checkbox societaria:** il modello non produce una proposta booleana o un
gruppo validato. La condizione ha aspetto `representation`, citazione non
coincidente con l'intero paragrafo e ricevuta verificata priva dell'ID della
casella. Sono tre limiti distinti del percorso di derivazione, non un guasto
dimostrato del writer `w14`. Non basta estendere il supporto a `[]` e non sarebbe
corretto allargare retroattivamente la ricevuta USER.

**Domande ripetute:** le due prime conferme sono registrate come non accettate,
quindi tornano nel pool. Dopo l'accettazione non vengono richieste ancora.
La risposta grezza della guardia semantica non è archiviata: impossibile
stabilire retrospettivamente se fosse ambiguità, rifiuto o errore di trasporto.
La nuova ricevuta identifica il punto non accettato, ma non inventa un motivo
che il sistema non ha conservato. Non è una correzione del giudizio semantico.

**Domanda sul soggetto sbagliato:** una data è chiesta nominando un soggetto
diverso dalla destinazione dello slot. Il rinvio mantiene vuota quella
destinazione; un hold USER successivo mantiene vuota anche la data della persona
effettivamente nominata. Nessuna delle due viene recuperata. Restano rinviate
attestazioni, categorie e designazioni; luogo/data rimangono una decisione
`write_authorized=false`. Correggere l'attribuzione delle domande richiede una
prova separata e non è stato nascosto nel fix delle ricevute.

## Verifiche e limiti

I test preliminari riproducono nove fallimenti; un ulteriore test sul fallback
del nome ha riprodotto la stessa invalidazione quando manca la descrizione del
modello. Dopo il fix, 29 test nuovi positivi/negativi passano.

Il primo giro completo ha dato **4016 PASS e 2 FAIL**: due test richiedevano gli
identici byte degli export congelati. Il confronto XML ha isolato cinque soli
spazi intenzionali in due fixture pubbliche. Gli artefatti e i loro hash restano
immutati; il test ora ammette esclusivamente quei cinque delta testuali e
confronta integralmente il resto di XML e pacchetto. Il controllo mirato seguente
ha dato **46 PASS**. Esito della suite finale riportato nel seguito.

**Suite completa finale: 4018 PASS, zero FAIL/SKIP; Ruff PASS.** Comprende
percorsi monolitici/segmentati, V14, K3, R1, istruzioni FORM, veto API, scelte
native, grounding e invalidazione. Frontend non coinvolto e non rieseguito.
Nessun test è una prova di correttezza delle future risposte del modello.

Replay dei gate FORM: **0/25** errori storici ammessi, sia con ricevute registrate
sia con guardia simulata. Positivi: **243/245** e **236/240** estesi con guardia
simulata; **197/245** e **226/240** con sole ricevute storiche. Identici al confronto
della precedente integrazione: nessun nuovo recupero o rifiuto in quel corpus.
Non si tratta di una nuova campagna E2E né di una misura della qualità del modello.
I due positivi controversi restano aperti.

## Rollback individuale

Da un checkout pulito che contenga i fix, usare **uno** dei seguenti comandi:

```bash
git revert fa83800a35ecae9eeda9d0a750a96b7c8d41dcd9
git revert 3cfd52137f689bb3c11b036d612b6140c6e6ddf6
git revert 0dda3ffe7cb19edbd5ceed2860374d8baa69b867
```

Il primo ripristina il comportamento precedente delle ricevute del nome; il
secondo la sostituzione dei puntini senza separatori; il terzo le ricevute
generiche. Non servono flag, migrazioni, ripristini DB o cancellazioni di DOCX.
Gli altri fix e tutte le protezioni FORM restano nel checkout. Nessun comando va
eseguito direttamente sul working tree ordinario sporco.

Verifica in tre worktree separati: tornando alla singola implementazione
precedente ricompaiono rispettivamente **2, 6 e 2** fallimenti attesi; gli altri
test passano (**27, 23 e 27**). Le copie dei test tolti dal revert sono conservate
solo nei dati locali per dimostrare il ritorno del difetto.

Ripetuta la verifica sui commit finali includendo i confronti con i sei DOCX
congelati: **2 FAIL attesi/55 PASS**, **6 FAIL attesi/51 PASS**,
**2 FAIL attesi/55 PASS**. Commit di rollback locali rispettivamente
`5a097ac`, `a4bccc1`, `9f0d630`; worktree `tesi-verifica-nome-20261027`,
`tesi-verifica-spazi-20261027`, `tesi-verifica-ricevute-20261027`.

## Integrità e stato ordinario

Nessun codice ordinario modificato o processo riavviato. La sessione esaminata,
i suoi sette turni registrati, i diciotto eventi, lo snapshot FORM e
tutti i **355 file preesistenti** nell'inventario uploads/knowledge sono identici.
Durante il lavoro è comparsa un'altra sessione nell'app: i conteggi osservati
sono passati da 30/207 a 31/211 sessioni/turni; export archiviati sempre 18.
Il database intero quindi **non** è identico byte per byte e non è stato
ripristinato, per preservare l'attività concorrente. Nessuna inferenza è stata
eseguita da questo intervento.

Il worktree di diagnosi contiene copie private non tracciate di sette artefatti
storici necessari ai test; non devono essere aggiunte a Git. I commit contengono
solo codice, test sintetici/di regressione e documentazione senza registrazioni
personali. Backup privato e risultato finale delle verifiche nel seguito.

Congelato anche `seed.db`, contenente soltanto le tabelle documentali e di
sessione necessarie; tabelle delle credenziali vuote. Il secondo rigioco dalla
copia congelata, indipendente dall'app live, produce lo stesso DOCX corretto
byte per byte e la stessa selezione. Script privati conservati come `.py.txt`
per non attivare il reload del backend ordinario.

Backup audit verificato con SHA-256 per **319 file più manifest** in
`/home/montesano/tesi-backups/diagnosi-conferme-docx-20261027-01/`.
Conservati anche patch dei commit e rapporto; copia separata su
`D:\Backup-tesi-2026-10-23\diagnosi-conferme-docx-20261027-01\`.
Questi backup privati non fanno parte della cronologia Git.

**Fermarsi dopo la consegna.** Prima di qualsiasi adozione occorre valutare il
rapporto; i due problemi sostanziali ancora aperti non sono risolti dal maggiore
numero di test o dalla sola presenza del nome nel Word.
