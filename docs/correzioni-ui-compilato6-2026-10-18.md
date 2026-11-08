# Correzioni mirate della compilazione UI e confronto prima/dopo

18 ottobre 2026. Intervento autorizzato dopo la
[diagnosi di compilato(6)](analisi-ui-compilato6-2026-10-17.md).
Modifiche locali precedenti conservate; nessun commit/push.
API, schema del database, writer, FORM B0, fixture e gold invariati.
Nessuna integrazione degli esperimenti E1.

## Risultato consegnato

- [Replay corretto di compilato(6), 33 scritture](<../nuovi dati/domanda-iscrizione.UI-CORRETTA-PARZIALE-20261018.docx>),
  [PDF](<../nuovi dati/domanda-iscrizione.UI-CORRETTA-PARZIALE-20261018.pdf>).
- [Nuova proposta con soci, export parziale da 41 scritture](<../nuovi dati/domanda-iscrizione.PROMPT-SOCI-PARZIALE-20261018.docx>),
  [PDF](<../nuovi dati/domanda-iscrizione.PROMPT-SOCI-PARZIALE-20261018.pdf>).
- [B0-03 con riuso SOURCE, 56 scritture](<../nuovi dati/domanda-iscrizione.B0-03-RIUSO-SOURCE-20261018.docx>),
  [PDF](<../nuovi dati/domanda-iscrizione.B0-03-RIUSO-SOURCE-20261018.pdf>).

Sono bozze parziali, con report JSON omonimi nella stessa cartella.
Non sono documenti completi o pronti alla presentazione.

## Misure e natura dei confronti

Le colonne SOURCE non comprendono il nome acquisito dall'utente. «Verificati»
significa grounding superato, non promozione automatica a RESOLVED o verifica
della completezza della pratica. «Non grounded» include anche proposte in
REVIEW_REQUIRED con errori: non soltanto lo stato letterale REJECTED.

| Esecuzione | Proposti SOURCE | Grounded SOURCE | Revisionati SOURCE | Scritti SOURCE + USER | Non grounded | Grounded ancora UNKNOWN | Target testuali vuoti / 60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Compilato(6), storico | 26 | 24 | 24 | 24 + 1 = **25** | 2 | 0 | 35 |
| Stesso output, riuso SOURCE dopo USER | 34 | 32 | 32 | 32 + 1 = **33** | 2 | 0 | 27 |
| B0-03, precedente replay manuale | 50 | 47 | 47 | 47 + 1 = **48** | 3 | 0 | 12 |
| B0-03, revisione precedente + otto recuperi | 58 | 55 | 55 | 55 + 1 = **56** | 3 | 0 | 4 |
| Nuova proposta del prompt + riuso SOURCE | 59 | 53 | 40 | 40 + 1 = **41** | 6 | 0 | 19 |

**Il primo confronto isola il recupero dopo USER:** stesso output globale,
stesse fonti e sole risposte realmente registrate nella sessione
`f06e75dd1ecf4c0fae668668c153a9df`. Nessuna nuova analisi LLM per recuperare
le generalità. Dialogo, persistenza, validatori ed export reali; il trasporto
del narratore è simulato e dichiarato negli artefatti. Il router non è
richiamato: si riproducono le sue decisioni già registrate.

**B0-03 conserva una revisione manuale**, come il precedente
[replay da 48 valori](export-b0-03-verificato-2026-10-17.md): sessione e ricevute
proprie di `ee86e66383ac4e5d9df90cf2b3ea3454`, senza trasferire decisioni dalla
sessione UI. Gli otto recuperi sono riesaminati offline; questo risultato non
misura l'autonomia del narratore reale.

**La prova del prompt è una sola nuova chiamata globale reale**, prima di
qualsiasi risposta sul firmatario. Input utente ancora «compila», nessuna scelta
USER inventata. Identici input JSON, FORM completo, fonti, schema, modello
`deepseek-flash`, thinking enabled, reasoning low, temperatura e limiti di output.
La sola differenza della richiesta inviata è nelle istruzioni SOURCE del system
prompt. Il confronto comprende inevitabilmente la variabilità del modello:
un campione non dimostra un miglioramento stabile.

L'export di questa nuova proposta riusa esclusivamente le ricevute della stessa
sessione copiata, con associazione semantica documentata ai nuovi ID di condizione:
società nel ramo p39; alternativa direttore tecnico per società di ingegneria
nel p50. Le risposte confermano il caso della società; non nominano automaticamente
un direttore, non provano nuovi poteri e non autorizzano spunte. Il nome incompleto
resta rifiutato, poi si acquisisce il nome completo realmente fornito. Anche qui
il narratore è simulato: **41 non è il risultato di una seconda prova completa
dalla UI con narratore reale**. Le scritture sono invece verificate nel DOCX.

Restano 13 proposte SOURCE grounded non revisionate: il percorso attuale del
narratore considera le prime 40 per passo. Nel Word nuovo entrano 16 dei 24
campi dei soci; gli altri otto e cinque dati del direttore restano pendenti
per quel limite. Non sono dati assenti o rifiutati dai validatori. Il limite
è documentato, non modificato in questo intervento.

## Prompt SOURCE allineato al verificatore

Rimosso il divieto assoluto di ruolo e valore in chunk distinti. Descritti:

1. Titolo, intestazioni e riga nominativa della stessa tabella SOURCE.
   Il ruolo non deve essere ripetuto in ogni riga. Nessun ruolo attribuito
   soltanto perché un nome compare nello stesso chunk.
2. Recupero dal record del fatto, quando attesta direttamente soggetto,
   ruolo e valore, oppure dalle prove complete già presenti nel binding.
3. Collegamenti di identità con chiavi verificabili, senza nomi simili,
   conflitti, trasferimenti di qualifiche o poteri.

Il collegamento tra record separati è attualmente circoscritto a CF personale
e provincia della stessa iscrizione professionale, con proprietà riconosciute
`codice_fiscale` / `provincia`. Le altre proprietà richiedono una prova diretta
del ruolo o il supporto completo del binding. Questo limite è stato reso più
esplicito dopo la lettura degli scarti della prova; **questa precisazione finale
non è stata sottoposta a un'altra chiamata**. Richiesta effettivamente inviata
e istruzioni finali sono entrambe archiviate: non vengono presentate come identiche.

Nel campione reale il modello passa da 19 fatti e 26 assegnazioni a 45 fatti
e 51 assegnazioni. Produce i tre binding dei soci, tutti i 24 relativi valori
superano il grounding, e propone anche il CF del direttore. Non è un recupero
del validatore su dati prima respinti: sono proposte prima omesse dal modello.

## Riuso dopo la scelta del firmatario

Il nuovo passaggio locale riconosce una grammatica FORM esplicita del blocco
«Il sottoscritto … nato … residente … C.F. … in qualità di … dell'operatore».
Legge le posizioni dal catalogo, senza ID, nomi o aziende fissi. Una tabella
interrompe la continuità. Se il modello omette la domanda sul firmatario, il
backend può comunque porla per questo blocco riconosciuto; non sceglie la persona.

La risposta USER identifica il soggetto soltanto. Il riuso richiede nome completo
esatto, ricevuta coerente con il valore acquisito, record anagrafico strutturato
con nome/cognome e CF personale univoci, assenza di conflitti anche nelle altre
tabelle/persone riconosciute. Non ricompone biografie da record parziali
uniti soltanto dal nome. Fonte General e fonti fuori progetto non provano
l'anagrafica. Una proposta del modello già esistente non viene sovrascritta.

| Campo di Leonardo | SOURCE | Risultato |
| --- | --- | --- |
| Nome | Intestazione e nome/cognome in -53/-54 | Identità verificata; scrittura del nome conserva provenienza USER |
| Comune/provincia nascita | «Lecce (LE)» in -54 | Lecce / LE, componenti letterali |
| Data nascita | -54 | 14 novembre 1982 |
| Comune/provincia residenza | «Bari (BA)» in -54 | Bari / BA, componenti letterali |
| Indirizzo | «Via Amedeo 24» in -54 | Amedeo 24 dopo il «via» già stampato |
| CF personale | -54 | MNTLRD82S14E506X |
| Carica | Attribuzione nominativa in -53; società identificata in -52 | amministratore unico e rappresentante legale |

Per la carica servono anche l'operatore SOURCE già grounded nel suo campo e
l'identificazione esplicita della stessa società nel documento che attribuisce
la carica. Nessuna equivalenza fra essere socio, essere amministratore ed essere
il firmatario scelto. Un ruolo cessato, riferito ad altra società o ambiguo non
viene riutilizzato. La carica non prova procuratori o poteri speciali.

I componenti estratti restano sottostringhe della prova, non conversioni arbitrarie:
un «Corso» non viene trasformato in «via». Non vengono riutilizzati recapiti
aziendali come telefono, e-mail o PEC personali.

Le proposte derivate conservano separatamente ricevuta USER, prove di identità,
prova del valore, appartenenza societaria quando necessaria e condizioni FORM.
Attraversano i controlli SOURCE letterali, isolamento/provenienza e validatore
DOCX esistenti, più il controllo deterministico della grammatica FORM. Non
fingono un binding SOURCE «firmatario»: quel legame proviene dalla scelta USER.
Restano proposte da revisionare, con zero risoluzioni automatiche.

Prima dell'export si rivalidano l'output globale originale e il riuso sulle SOURCE
correnti; differenze rispetto alle proposte revisionate bloccano l'export.
La rivalidazione viene ripetuta anche al salvataggio. Il modello non viene
richiamato. Output e audit originari restano immutabili; gli audit di revisione
sono salvati separatamente e restituiti dallo stesso endpoint di report.
Nessuna migrazione o aggiornamento retroattivo delle sessioni originali.

Il supporto è deliberatamente limitato alla grammatica e ai record strutturati
riconosciuti. Per altri layout, nomi ambigui o identità incomplete i campi restano
irrisolti; non viene avviata un'inferenza aggiuntiva implicita.

## Narratore e assenza di dati

Il contesto distingue ora cinque situazioni: assenza verificata nelle fonti;
recupero non dimostrato; record presente nell'input ma non usato dalle proposte;
proposta respinta; proposta condizionata/in attesa. **Per le prime due non esiste
una ricevuta di ricerca esaustiva: lo stato rimane non dimostrato**, anziché
classificare come assente ciò che il modello ha omesso.

Al narratore arrivano anche estratti letterali dei record personali/tabelle
disponibili e non citati dalle proposte. Sono indizi di lettura, non nuovi fatti
validati né autorizzazioni a riempire campi. Le motivazioni storiche dei vuoti
non vengono ripresentate come stato live per i campi recuperati o acquisiti USER.
Le conferme USER vengono considerate nel conteggio delle attese.

Le formulazioni di assenza riprodotte dalla sessione e dalle prove negative
attivano un riepilogo prudente costruito dal backend, preservando domande e
sospensioni. Questo controllo lessicale è intenzionalmente conservativo; non è
una verifica semantica universale del testo libero. I follow-up mantengono le
ricevute deterministiche già esistenti. Non si certifica l'infallibilità del
narratore reale con i soli test di trasporto simulato.

## Anomalie lasciate esplicitamente irrisolte

**Bari / BA iniziali:** SOURCE disponibili e valori corretti, ma citazioni
`[[p15.s0]] (` e `([[p15.s1]])` senza richiesta testuale. Il controllo FORM
«Il solo marker non documenta la richiesta del campo» rimane attivo, anche
nella nuova proposta. Non vengono accettate etichette inventate o dati spostati
dal ramo societario. Il recupero richiede una prova strutturale del collegamento
al «con sede in» precedente, non una deroga basata sulla sola presenza in SOURCE.

**Comune nel ramo società:** nel nuovo output e in B0 il valore proposto è un
indirizzo completo. Il rifiuto semantico del Comune rimane attivo. Non viene
estratta arbitrariamente «Bari» da quella proposta.

**Ramo societario:** confermare l'applicabilità non crea una proposta checkbox.
Non c'è un `choice_group` grounded, quindi nessuna spunta viene esportata.
Restano distinti forma S.r.l., qualità di società di ingegneria nella pratica,
modalità di partecipazione e rappresentanza della persona.

**Fax:** il valore `+39 080 000 2041` è esplicito in `integrazione-company.md`,
file SOURCE -10, chunk -53: «Fax aziendale sintetico». Era già nell'input
originale. È un dato dello scenario sintetico aziendale, non un recapito
personale né un'informazione dedotta dal numero di telefono.

**Tre scarti del direttore nella nuova risposta:** sezione, provincia e data
citano la tabella soci -54 con binding al record direttore -45. Per provincia
il modello usa `provincia albo`, che non è la proprietà canonica del collegamento
supportato; sezione/data non sono trasferibili con quel collegamento. Le prove
esistono altrove nelle SOURCE, ma queste assegnazioni non superano i controlli
attuali. Non sono assenze dalla KB né tre valori necessariamente falsi.
Nessuna ulteriore modifica al verificatore dei binding in questa fase.

I sei non grounded del nuovo campione sono quindi: due ancoraggi FORM incompleti,
un indirizzo incompatibile col Comune, tre collegamenti professionali irrisolti.
I tre rifiuti di B0 rimangono invariati. Nessun rifiuto è trasformato in TRUE
per aumentare le scritture.

## Errori, gold e controllo del documento

Un primo export di sviluppo duplicava «via Via»: difetto riprodotto e corretto
prima della consegna, senza intervenire sul writer. Gli artefatti intermedi
rimangono conservati e distinti dai tre export `*-final`.

Nei tre export finali rimane **una discordanza letterale rispetto al gold**:
la carica completa «amministratore unico e rappresentante legale» invece del
solo «rappresentante legale». Entrambe le componenti sono esplicite nella SOURCE
e riferite all'operatore corretto. Il gold e il suo valutatore non sono stati
adattati: conformità stretta 32/33, 55/56 e 40/41, rispettivamente. Questa
discordanza è riportata come tale, distinta da un dato inventato o da un errore
di soggetto. Nessuna nuova accettazione indebita osservata nelle verifiche
fattuali e nei casi negativi; non è una percentuale di accuratezza generale.

I valori preesistenti conservano le citazioni originarie: questo intervento
non le ricertifica tutte. Rimane, per esempio, il limite storico della provincia
del direttore «Bari» citata nel nome dell'Ordine, documentato nella diagnosi
iniziale. Gli otto recuperi nuovi conservano invece le proprie prove strutturate.

Verificati ZIP/CRC, parsing XML/relazioni, corrispondenza fisica di ogni valore
con il proprio slot e il report, invariabilità del testo prestampato e dei
segnaposti non selezionati. Modificata soltanto `word/document.xml`, con avviso
di bozza; quattro tabelle e tredici controlli nativi conservati, zero spunte.

Rendering LibreOffice: 10 pagine per il replay UI, 9 per B0 e nuova proposta.
Viste UI pagine 1/3/10, B0 pagina 3, nuova proposta pagina 3. Anagrafica corretta
e soci coerenti con gli slot esportati; restano le giunzioni di testo preesistenti
e la firma isolata a pagina 10 del replay UI. Writer invariato. Non verificata
la paginazione in Microsoft Word. Warning del registro linguistico locale
LibreOffice conservato; le conversioni e l'estrazione delle pagine sono riuscite.

## Riproducibilità e limiti

Raw: `backend/data/compilation-audit/ui-compilato6-fix-20261017-01/`.
Include snapshot preventivo del codice, output/prompt reali, errori e tentativi
preliminari falliti, test prima/dopo, replay persistenti, report e misure XML,
confronti gold successivi all'export e rendering. Database privati isolati in
`.tools/ui-compilato6-fix-20261017-01/`, esclusi dal backup pubblico.

La nuova chiamata dura 136,7 s contro i circa 125,8 s storici. Usage nuovo:
76.408 input, 37.735 output, di cui 24.441 reasoning. È una misura singola del
provider, non del tempo totale UI; non dimostra una maggiore velocità. Il riuso
successivo del firmatario usa zero token LLM. Nessun'altra chiamata reale.

Verifica finale: **2.459 test backend passati in 172,68 s**, Ruff e
`git diff --check` passati. Incluso il guard che impedisce nuove domande/riuso
impliciti sui contratti precedenti a V12. I tre export superano nuovamente i
controlli di freschezza con il codice definitivo, senza nuove scritture.
Frontend invariato, suite frontend non rieseguite.

Preservati 29 stati/versioni di sessione live, schema del database, download
originale e 22 artefatti dell'analisi originaria. Test e controlli sono registrati nelle
[misure](benchmarks/2026-10-18-ui-compilato6-fix.json) e nel registro
[relazioni.md](../relazioni.md). Le prove software con provider simulato restano
separate dal campione globale reale. La fase si ferma alla consegna di queste
correzioni e dei DOCX, senza ampliare il compilatore.

[Backup degli artefatti](benchmarks/2026-10-18-ui-compilato6-fix-audit.tar.gz),
[descrittore](benchmarks/2026-10-18-ui-compilato6-fix-archive.json),
[checksum](benchmarks/2026-10-18-ui-compilato6-fix-audit.tar.gz.sha256) e
[controlli di preservazione](benchmarks/2026-10-18-ui-compilato6-fix-checks.json).
349 file verificati, 32.512.735 byte non compressi; database e credenziali esclusi.
