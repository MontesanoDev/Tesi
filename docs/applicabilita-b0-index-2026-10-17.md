# Applicabilità UNKNOWN: B0-03, INDEX-01 e percorso minimo al DOCX

17 ottobre 2026. Studio offline successivo alla chiusura della correzione dei
binding. **Nessuna modifica a controlli, prompt, modello, writer o stato di
sessioni; nessuna chiamata LLM e nessun nuovo DOCX.** Le condizioni non sono
state trasformate in TRUE. La diagnosi distingue audit congelato, registro
USER della singola sessione, revisione ed export.

## Risultato principale

UNKNOWN non significa che manchino tutti i dati o tutte le decisioni.
Le tre condizioni restituite dai due output hanno `operator="semantic"` e
`fact_ids=[]`: il verificatore ne controlla l'ancoraggio al FORM, ma non ne
calcola la verità. L'audit rimane congelato anche dopo risposte USER.

**B0-03 ha già una conferma USER nella propria sessione storica**, oltre al
nome del firmatario e al consenso all'export parziale. Il replay dei binding
usa invece solo la risposta globale e non applica il registro del dialogo.
INDEX-01 originario si è fermato allo schema root, senza scritture di sessione;
le conferme applicate alla sua copia offline provengono da INDEX-03 e sono
un test separato con corrispondenza esplicita delle condizioni.

Non occorre fare diventare vero l'audit per poter esportare: il percorso
esistente distingue la proposta SOURCE dall'applicabilità confermata USER.
Occorre verificare la proposizione confermata, il suo ambito e la revisione
delle proposte selezionate. Esiste inoltre un limite distinto: i due output
non propongono alcun gruppo validato per le checkbox native.

## Le condizioni effettivamente presenti nei due output

| Output / ID | Origine FORM e testo | Dimensione dichiarata dal modello | Proposte grounded coinvolte |
| --- | --- | --- | ---: |
| B0 `c_p39` | p39: «Legale rappresentante di società di professionisti […] o di società di ingegneria […] avente la seguente» | `participation` | 47 |
| INDEX `c_op` | p14: «dell’operatore economico ___________________________________ con sede in» | `participation` | 9 |
| INDEX `c_branch_soc` | p39: «Legale rappresentante di società di professionisti […] o di società di ingegneria» | `representation` | 16 |

Le citazioni esatte proposte dal modello sono:

- B0 `c_p39`: «☐ Legale rappresentante di società di professionisti (art. 66, comma 1, lett. b D. Lgs. n. 36/2023) o di società di ingegneria (art.66, comma 1, lett. c D.lgs. n. 36/2023.) avente la seguente».
- INDEX `c_op`: «dell’operatore economico ___________________________________ con sede in».
- INDEX `c_branch_soc`: «Legale rappresentante di società di professionisti (art. 66, comma 1, lett. b D. Lgs. n. 36/2023) o di società di ingegneria».

La terza è una citazione parziale del medesimo p39; non cambia il testo del FORM.
Tutte e tre sono `GROUNDED_PROPOSAL` come condizioni **esistenti nel FORM**,
con `result=unknown`, non condizioni dimostrate applicabili. Non hanno errori
di citazione e non contengono riferimenti a fatti SOURCE.

B0 attribuisce a un unico predicato 9 dati generali dell'operatore, 8 dati
societari, 23 dei soci e 7 del direttore. L'ID `c_p39` copre anche i paragrafi
p14–p17, che precedono la scelta p39: **la dipendenza dei dati generali da
quel ramo non è una clausola letterale del FORM**. È un'associazione proposta
dal modello, da verificare; l'identificazione dell'operatore è una questione
distinta dalla sua qualità societaria e dalla qualità del sottoscrittore.

INDEX separa i 9 dati generali dai 16 del ramo societario/direttore. Non
propone dati dei soci. Non confermare il suo ramo non è la causa unica delle
omissioni: confermarlo non creerebbe le 24 proposte dei soci mancanti.

## Perché il codice conserva UNKNOWN

In [compilation_global.py](../backend/app/compilation_global.py):

- `_shared_conditions` parte da UNKNOWN. Per `semantic` non interpreta il
  significato del testo come un predicato vero; con `fact_ids=[]` non ha
  neppure operandi SOURCE dichiarati. I confronti strutturali `same/different`
  sono un percorso diverso, con due fatti distinti e vincoli propri.
- `_expand_shared_field` conserva UNKNOWN anche per condizioni esterne al
  contesto locale della destinazione. B0 ha 47/47 controlli di ambito
  `semantic_review_required`; INDEX `c_op` 1 locale e 8 non locali, mentre
  `c_branch_soc` ha 16 controlli non locali. Non sono altre prove di assenza
  nelle SOURCE.
- Il valore può superare i controlli SOURCE restando una proposta
  `conditional/REVIEW_REQUIRED`, con `proposed_value` e senza valore scritto.

In [compilation_global_dialogue.py](../backend/app/compilation_global_dialogue.py),
`apply_replies` registra la risposta in `dialogue.answers`, non riscrive
`audit.conditions`. `export_selection` considera separatamente le conferme
USER, le proposte revisionate e quelle sospese. Anche `review_fields` mostra
la condizionalità dell'audit: non equivale al responso effettivo dell'export.

In [compilation_global_sessions.py](../backend/app/compilation_global_sessions.py),
`_selected` richiede selezioni valide e conferme delle condizioni sconosciute,
rilegge le SOURCE e rivalida la risposta originale. Una selezione formalmente
accettabile non dimostra da sola che il significato dell'intera condizione
sia stato verificato: la revisione deve confrontare clausola, soggetto e
risposta. Non va usato un elenco di ID confermati per superare questa verifica.

## Natura giuridica, partecipazione e rappresentanza

| Questione | Prova disponibile | Limite |
| --- | --- | --- |
| Forma giuridica della società | SOURCE `-43`: «Forma giuridica: Societa a responsabilita limitata»; visura demo | S.r.l. non è la scelta della modalità di partecipazione alla singola procedura |
| Attività descritta | SOURCE `-43`: «Tipologia di attivita': societa' di ingegneria civile» | Descrizione aziendale, non verifica automatica dei requisiti richiamati dal FORM |
| Soggetto per cui si prepara la domanda | T0 registrato: «[…] per Mapi Ingegneria S.r.l.» | La presenza di una società nella KB non basta a identificarla come partecipante |
| Scelta del ramo nella pratica | USER: «Mapi Ingegneria S.r.l. partecipa soltanto come società di ingegneria» | È una decisione di questa pratica; non va ricavata dalla sigla S.r.l., dall'ATECO o dai servizi svolti |
| Identità del firmatario | USER: «Il firmatario scelto per questa pratica è Leonardo Montemurro, rappresentante legale» | Scegliere la persona non le attribuisce una carica non documentata |
| Carica attuale di Leonardo | SOURCE `-53`: amministratore unico e rappresentante legale dal 2 ottobre 2026 | Prova il ruolo dichiarato nello scenario; non documenta automaticamente procura, mandato RTP o poteri speciali ulteriori |
| Precedente carica di Luca | SOURCE `-44`/visura e successiva cessazione in `-53` al 1 ottobre | Non dimostra la rappresentanza attuale; la cessazione da amministratore non cancella il suo ruolo di socio |
| Ruolo di Elisa | SOURCE `-45` e `-55`: direttore tecnico | Non la rende firmataria o responsabile di un incarico specifico |

La data di riferimento USER è il 15 ottobre 2026: l'evento successivo della
integrazione prevale per la carica interessata, senza cancellare le altre
informazioni precedenti. Per Leonardo la rappresentanza è **esplicitamente
attestata**, non dedotta dalla sola carica di amministratore. Non emerge una
procura o il dettaglio di poteri speciali. Il blocco analizzato del FORM chiede
la qualità di legale rappresentante, non gli estremi di una procura per questa
persona: quella carenza non rende assente il ruolo letteralmente documentato.

La frase USER «partecipa soltanto come società di ingegneria» documenta la
scelta che lo scenario ha confermato. Non è una regola generale «S.r.l. ⇒
partecipazione singola», né prova la costituzione o i poteri di un RTP.
Qualsiasi ulteriore proposizione sulla partecipazione singola, sul ruolo di
capogruppo/mandante o sui relativi mandati deve rispettare il testo registrato
e la specifica opzione FORM; non può essere introdotta dalla classificazione
aziendale. Gli altri rami non sono fatti negativi sulla società.

## Rami semantici da verificare separatamente

Questa è una matrice diagnostica, non un nuovo schema o motore implementato.

| Ramo e condizione esatta del FORM | SOURCE disponibili | USER registrato | Che cosa manca realmente |
| --- | --- | --- | --- |
| Identificazione generale, p12–p17: «Il sottoscritto […] in qualità di […] dell’operatore economico […]» | Anagrafica societaria `-43/-52/-53`; anagrafica Leonardo `-53/-54` | T0 identifica Mapi e Leonardo; B0 registra anche `field:p12.s0` | Nei replay senza USER manca quel contesto; le proposte anagrafiche omesse non vengono create da una conferma. Non manca l'anagrafica nella KB |
| Società, p39–p42: «Legale rappresentante di società di professionisti […] o di società di ingegneria […]» | Forma/attività, dati società e rappresentanza attuale di Leonardo | B0 conferma `c_p39`; INDEX-03 conferma `c_soc`, che non appartiene a INDEX-01 | Associare la decisione alla pratica e all'intera proposizione; non sostituire rappresentanza con sola natura giuridica. In INDEX-01 originario non c'è un registro di sessione post-analisi |
| Soci, p42–p49: «e composta da (riportare nominativo, qualifica professionale e C.F. di ogni socio)» | Tabella `-54`, tre soci e rispettivi dati; nessuna necessità di designarli USER | Decisione del ramo societario di B0; non serve chiedere chi siano i soci già documentati | B0: una provincia ha quote insufficiente e 23 proposte sono ora grounded. INDEX: le 24 destinazioni dei soci non hanno proposte, non sono semplicemente bloccate da UNKNOWN |
| Figura tecnica, p50–p53: «Responsabile della Progettazione (per le società di professionisti) o Direttore Tecnico (per le società di ingegneria)» | Elisa direttore tecnico in `-45/-55`; suoi valori in `-54/-55` | La frase USER specifica società di ingegneria | Verificare la sottoalternativa ingegneria, non solo il booleano «professionisti O ingegneria». Non trasferire direttore tecnico a responsabile della progettazione se si scegliesse l'altro caso |
| Rami alternativi p20–p38, p54–p75; dichiarazioni associati/RTP p203–p215 | Nessuna prova di associazione, componenti RTP, mandato o consorzio per questa pratica | Nessuna decisione autonoma registrata su costituzione RTP, mandanti o procura | Tenere fuori dal percorso selezionato e non compilare per somiglianza di nomi o presenza di soci. Non farli diventare FALSE dalla sola assenza di SOURCE |

Il modello non ha codificato tutte queste distinzioni nelle sue condizioni:
B0 ne usa una, INDEX due. Anche `condition_inventory.semantic_completeness_verified`
è false. Non va interpretato come un inventario completo delle condizioni
logiche del modulo.

## Le decisioni USER realmente registrate e il loro ambito

**B0-03**, sessione storica `ee86e66383ac4e5d9df90cf2b3ea3454`:

- T0 contiene già società scelta, firmatario e data di riferimento. Non era
  incluso nell'input della chiamata globale congelata.
- `condition:c_p39`, `CONDITION_TRUE`, quote «Mapi Ingegneria S.r.l.
  partecipa soltanto come società di ingegneria». Domanda registrata:
  «Confermi che la domanda è presentata in qualità di legale rappresentante
  di una società di ingegneria, con conseguente compilazione dei dati
  societari e del direttore tecnico?».
- `field:p12.s0`, `VALUE=Leonardo Montemurro`, con quote sul firmatario;
  registrato anche in `dialogue.user_values`.
- Step 02: richiesta esplicita di generare una bozza parziale mantenendo
  vuoti irrisolti e firma. È un'autorizzazione storica del test, non un nuovo
  consenso operativo dedotto per una pratica diversa.

La quote del booleano non contiene da sola il nome o il potere di firma.
La lettura completa richiede anche l'altro messaggio USER e la SOURCE `-53`.
Non si trasferisce la carica dalla domanda del narratore alla persona.

**INDEX-01 originario:** `metrics.json` registra fallimento allo schema,
`session_writes=0` e `docx_writes=0`. Negli artefatti non esiste una sua
sessione integrata con decisioni post-analisi. Il suo output è stato studiato
successivamente nella copia con due metadati root isolati, senza filtro in
produzione e senza nuove generazioni.

**INDEX-03**, altra sessione `ac4edc0ccd5e4acf91d56a55f0895b0a`, registra
`condition:c_soc=true` e `condition:c_oe=true`, con le medesime due frasi
USER su società e firmatario. `c_oe` risponde a «Confermi che il sottoscritto
agisce per l'operatore economico Mapi Ingegneria S.r.l?». Non ha registrato
un valore USER per il campo nome: in quel dialogo il nome compare nella
conferma, non in `user_values`.

Il precedente replay software INDEX-01 con USER, sessione
`5f33f44d46fc40f188f1eee8affa40fe`, ha dichiarato esplicitamente il mapping
`c_soc→c_branch_soc`, `c_oe→c_op`. Ha riusato le quote mediante slot del
backend e selezione manuale: non dimostra che INDEX-01 le avesse ricevute
nella chiamata globale o che il narratore le abbia ricollegate da solo.
Inoltre il booleano «professionisti O ingegneria» conserva il significato
solo leggendo la quote specifica; non è un'identità universale tra gli ID.

Il solo file congelato `richiesta-iniziale.txt` descrive il copione; la
presenza del medesimo testo in `initial-routing`, `context` e nei registri
di risposta dimostra dove è stato effettivamente usato. Le altre quattro
risposte T1 esistono nel copione di valutazione, ma **non furono chieste né
registrate** nei dialoghi qui esaminati: preferenze, designazioni, attestazioni
e luogo/data non diventano per questo decisioni acquisite.

## Applicabilità, revisione e compatibilità col writer sono gate diversi

Controllo read-only eseguito con le funzioni esistenti, senza writer o DB:

| Preflight del valore | Controllati | Passati senza riscrivere il valore |
| --- | ---: | ---: |
| SOURCE B0-03 | 47 | 47 |
| SOURCE INDEX-01 | 25 | 25 |
| Nome USER già registrato in B0 | 1 | 1 |

Questo prova la compatibilità con il validatore usato prima della scrittura;
non ha confermato condizioni, creato proposte o prodotto un documento.

Proiezione solo in memoria dell'audit B0 aggiornato sul **suo** dialogo
storico, usando `review_fields` ed `export_selection` senza cambiare risposte:

- Il vecchio elenco revisionato contiene 22 proposte SOURCE.
- Una, `p41.s1`, è l'indirizzo completo ora respinto nel Comune: ne restano 21.
- Altre **26** sono grounded nel nuovo audit ma non erano nel vecchio elenco
  revisionato. La conferma USER di `c_p39` non le aggiunge automaticamente.
- Il nome USER `p12.s0` è già acquisito; l'audit conserva comunque UNKNOWN.
- L'unico campo già revisionato che cambia tra audit vecchio e nuovo è
  `p41.s1`. Il controllo di rilettura di `_selected` impedisce di esportare
  ciecamente il vecchio audit se include quel campo. Non è stata invocata
  ora una richiesta di export per osservare il suo rifiuto.

Quindi non è corretto dire che la sola applicabilità impedisca tutte le
scritture, o che basti confermarla per ottenere 47 campi. Restano revisione,
coerenza dello snapshot e selezione valida. Nel vecchio test INDEX con USER,
19 selezioni manuali includono il medesimo Comune oggi respinto: 18 sono
ancora grounded, mentre 7 delle attuali 25 non erano in quella selezione.

## Checkbox, dichiarazioni e copertura ancora mancanti

Entrambi gli output hanno `choice_groups={}`; `p39.cb0` non ha una proposta
scrivibile. Un booleano di applicabilità non è un valore della checkbox.
`checked_user_fields` richiede un gruppo `GROUNDED_GROUP` e una scelta USER
coerente: non va aggirato scrivendo direttamente un true nel controllo Word.

Senza altre modifiche è verificabile una **bozza parziale nei testi inseriti**.
Per una copia che esprima anche le scelte native occorre una revisione distinta:
gruppo FORM verificato e scelta USER tracciata, oppure completamento manuale
nel Word con diff documentato. Non è necessario chiedere al modello di
inventare il gruppo o modificare ora i controlli.

Il FORM p235–p240 distingue inoltre le dichiarazioni personali in base a
s.n.c., s.a.s. o altri tipi societari, e cita anche cariche cessate nell'anno.
La forma S.r.l. e la successione Luca/Leonardo sono disponibili: non provano
che tali dichiarazioni siano state rese. La quota del 40% di Elisa non va
automaticamente trasformata in una qualificazione giuridica di «socio di
maggioranza» per produrre attestazioni. Non si confonde questo blocco con
la richiesta dei dati di **ogni socio** in p42.

Il confronto di sola valutazione con i 60 target testuali SOURCE del gold
congelato mostra ancora **13 destinazioni senza proposta grounded in B0**:
9 anagrafiche/carica del firmatario, 2 Comuni e 2 province di Elisa. Dieci
sono omissioni del modello, tre proposte rifiutate. In INDEX restano 35
target: 9 del firmatario, 2 Comuni, 24 dei soci; 33 omissioni e due rifiuti.
Sono dati disponibili nelle fonti, non risolvibili dal solo cambio di
applicabilità. Il nome è già disponibile come USER in B0, ma questo non
aumenta retroattivamente la copertura SOURCE della chiamata globale.

Preferenze, esecutori/integrazione, attestazioni e luogo/data vanno lasciati
vuoti finché manca la rispettiva risposta registrata. La data di riferimento
delle fonti non è una scelta di luogo/data di firma. Firma, curricula e
dichiarazioni individuali restano attività separate; non si dichiara la
bozza pronta alla presentazione.

## Piano minimo proposto, da eseguire successivamente

1. **Partire da B0-03**, che ha risposta valida, audit attuale e proprie
   decisioni USER; conservare la baseline senza USER e l'INDEX originario
   fallito. Preparare una copia isolata con originale, SOURCE e risposta
   immutati, versioni e hash. Riutilizzare il percorso offline già collaudato,
   evitando `advance`, narratore e interprete di risposte che chiamano LLM.
2. **Allegare una scheda di verifica dell'applicabilità**: Mapi è l'operatore;
   la scelta registrata riguarda il ramo della società di ingegneria;
   Leonardo è il firmatario scelto e il rappresentante documentato alla data;
   Elisa è il direttore richiesto dalla sottoalternativa p50. Confrontare
   l'intero ambito di `c_p39`, incluso il suo uso improprio come condizione
   generale p14–p17, senza dedurre partecipazione o poteri dalla sola S.r.l.
   Conservare l'audit UNKNOWN e il registro USER separati.
3. **Revisionare le 26 proposte nuove**, con FORM e citazioni SOURCE, e
   conservare le 21 ancora valide della vecchia revisione. Escludere i tre
   rifiuti B0. Non creare una ricevuta «reviewed» fingendo una nuova sintesi
   AI; registrare che si tratta di revisione manuale/offline. Riutilizzare
   il nome USER solo nel campo dove era effettivamente registrato.
4. **Eseguire l'export parziale con i servizi esistenti**, nel solo scenario
   offline dichiarato, usando le ricevute originali e il consenso storico
   all'export. Nessuna condizione arbitrariamente vera, nessuna migrazione
   della sessione live. Per un diverso uso operativo servirebbe un consenso
   riferito a quella pratica, non il trasferimento delle ricevute di test.
   Obiettivo pianificato: **47 SOURCE + 1 nome USER**, non ancora un export
   misurato. Nessun tentativo di forzare checkbox o proposte omesse.
5. **Verificare il DOCX prodotto**: selezione/report/valori XML coincidono;
   citazioni e condizioni confermate sono tracciate; le altre destinazioni,
   tabelle e parti ZIP sono preservate; firma vuota. Renderizzare e controllare
   numerazione, campi su più righe e firma. Salvare DOCX/PDF/report/hash e
   distinguere errori di contenuto e layout. Lo stato resta `needs_review`.
6. **Se serve il documento completo**, affrontare separatamente le 12
   destinazioni testuali ancora vuote dopo il nome USER, le scelte native e
   i temi T1 non acquisiti. Una revisione umana può usare le SOURCE già
   disponibili senza nuove chiamate, ma deve essere una revisione distinta,
   senza alterare gli output MODEL, il gold o i risultati del benchmark.

Il percorso corto produce una bozza verificata per ciò che contiene, non
una candidatura integralmente verificata. Non richiede un nuovo framework
o la riscrittura delle condizioni: richiede di usare le ricevute realmente
esistenti nel loro ambito e completare la revisione prima di esportare.

## Artefatti e verifiche di questo studio

[Dati e registro delle evidenze](benchmarks/2026-10-17-applicability.json),
[controlli](benchmarks/2026-10-17-applicability-checks.json),
[backup](benchmarks/2026-10-17-applicability-audit.tar.gz).
Raw: `backend/data/compilation-audit/applicability-20261017-01/` con condizioni,
FORM, SOURCE, ricevute USER, hash degli artefatti letti, preflight e proiezione
read-only. Le decisioni sono verificate sui checkpoint archiviati, non tramite
una nuova lettura o modifica delle sessioni live. Gold e copione sono usati
solo per misurare lacune e distinguere risposte previste da risposte registrate.

Integrità verificata: 11.092/11.092 file protetti invariati, nessun nuovo file
nei percorsi protetti; identici anche i 14 artefatti letti e indicizzati con hash.
Il backup contiene script, evidenze derivate, manifest e questo rapporto.
La riproduzione richiede il repository con la fixture congelata e i bundle
B0, E1-index, root-user-reasoning e binding-final già conservati in
`docs/benchmarks/`: non richiede il database privato o nuove chiamate provider.

Nessuna nuova suite backend/frontend o Ruff: i 2.431 test del rapporto
precedente restano verifiche di quella fase. Qui sono stati eseguiti conteggi,
confronti, 72 controlli puri di valori SOURCE e uno USER, selezione read-only,
controlli di hash/JSON/riferimenti/diff. Nessuna nuova misura di generazione,
DOCX esportato, booleano di applicabilità cambiato, commit o push.
