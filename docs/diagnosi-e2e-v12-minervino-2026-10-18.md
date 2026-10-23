# Minervino: prova reale dalla UI della V12 corretta

18 ottobre 2026. Diagnosi della versione locale corrente, senza modifiche al
compilatore, ai prompt, ai controlli, al writer o al FORM. Nessun commit/push.
E1 non eseguito: la rappresentazione compatta resta una fase successiva.

**La prova conferma progressi nella proposta, ma non una compilazione stabile.**
Il modello propone tutti i 60 campi SOURCE attesi; soltanto 27 superano i
controlli e vengono scritti. Tutti i 27 valori scritti corrispondono al GOLD V1,
con le equivalenze già congelate. Dei 24 campi dei soci, ne propone correttamente
24 e ne scrive 8. Il precedente risultato da 16 aveva una causa diversa e
riproducibile: otto revisioni già effettuate vengono perse quando cambia la
finestra delle prime 40 proposte. Non è una perdita nel writer.

[Word prodotto](<../nuovi dati/domanda-iscrizione.V12-E2E-REALE-20261018.docx>),
[PDF](<../nuovi dati/domanda-iscrizione.V12-E2E-REALE-20261018.pdf>),
[report dell'export](<../nuovi dati/domanda-iscrizione.V12-E2E-REALE-20261018.report.json>),
[conversazione](<../nuovi dati/domanda-iscrizione.V12-E2E-REALE-20261018.conversazione.md>).
[Misure](benchmarks/2026-10-18-v12-e2e-minervino.json),
[traccia dei 24 campi](benchmarks/2026-10-18-v12-e2e-soci.json),
[backup](benchmarks/2026-10-18-v12-e2e-audit.tar.gz),
[controlli](benchmarks/2026-10-18-v12-e2e-checks.json),
[descrittore del backup](benchmarks/2026-10-18-v12-e2e-archive.json).

## 1. Protocollo realmente eseguito

Un Chromium Playwright ha usato la UI React reale, senza API simulate, route
intercettate o risposte sostituite. Mention del modulo, messaggi, avanzamento,
export, download e riapertura della conversazione sono passati dall'interfaccia.
Provider reale `deepseek-flash`, configurazione esistente. Una sola analisi
globale, thinking abilitato, reasoning_effort low, max_tokens 49.152;
narratore senza thinking. Nessun tentativo per migliorare la qualità.

Database, storage e Company KB sono stati copiati prima della prova in
`.tools/ui-v12-e2e-20261018-01/`. Backend isolato su 8001, frontend su 5174;
nessuna scrittura alle sessioni dell'istanza originale. I servizi isolati sono
stati arrestati; quelli originali su 8000/5173 rispondono ancora 200.

Identificativi della sola copia:

- sessione `d538c77c599a4860aa0114c534ce6f0c`, versione finale 7;
- conversazione `conv-e0d25a1af828430e`;
- export `89bd04b9643a4f969ba8f9b208dac5c7`;
- codice: HEAD `99ab052` più le modifiche locali preesistenti, fotografate nel raw;
- modulo SHA256 `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c`;
- DOCX scaricato SHA256 `54f307b4d8f65022924fb5f7afb8c1cc305326f253bf8db38e5ea84490497cfa`.

FORM e tutte le 56 SOURCE coincidono con l'input verificato di compilato(6).
Sono presenti i dati integrativi Company; gold e annotazioni di valutazione
non sono entrati nella KB o nelle richieste al provider.

È stata inviata la **richiesta iniziale congelata di Minervino V1**, che sceglie
già la partecipazione soltanto come società di ingegneria e Leonardo Montemurro
come firmatario. La precedente prova del prompt e compilato(6) iniziavano con
il solo «compila». Inoltre la prova precedente precedeva l'ultima precisazione
delle istruzioni SOURCE. I risultati sono confronti descrittivi, non una coppia
controllata per attribuire il cambiamento a una singola variabile.

Il sistema ha chiesto soltanto di confermare società di ingegneria e
rappresentanza. È stata ripetuta la scelta già presente in T0, senza aggiungere
poteri speciali o dati anagrafici. Poi il sistema ha proposto l'export parziale.
È stato usato il testo T2 del copione. Le quattro risposte su preferenze,
designazioni, attestazioni e luogo/data **non sono state somministrate**, perché
mai richieste. Il checkpoint T1 completo non è stato raggiunto.

## 2. Risultato misurato, senza confondere gli stadi

| Misura | Nuova prova UI reale |
|---|---:|
| Fatti nel JSON del modello | 46 |
| Assegnazioni SOURCE proposte | 60 |
| Campi SOURCE attesi ma non proposti | 0 |
| Valori proposti conformi al gold congelato | 58/60 |
| Proposte SOURCE grounded | 27 |
| Proposte non grounded, escluse dall'export | 33 |
| SOURCE revisionate / trattenute dal narratore | 27 / 0 |
| Grounded ancora bloccate da UNKNOWN dopo la risposta USER | 0 |
| SOURCE effettivamente scritte nel DOCX | 27 |
| Valori USER scritti | 0 |
| Valori scritti conformi al gold | 27/27 |
| Nuovi valori fattualmente indebiti osservati tra le scritture | 0 |
| Checkbox selezionate | 0 |

«Non grounded» comprende REVIEW_REQUIRED e REJECTED: non sono tutti rifiuti
per falsità del valore. I 33 casi sono esclusi per controlli specifici:

| Causa primaria riportata dal gate | Numero | Destinazioni |
|---|---:|---|
| Binding di ruolo rifiutato | 24 | 8 generalità/carica del firmatario, 16 campi soci Elisa/Andrea |
| Solo marker FORM senza richiesta riconoscibile | 2 | Comune iniziale p15.s0; provincia di residenza p13.s1 |
| Ruolo e soggetto non attestati nel record del valore; recupero non ammesso | 7 | Direttore tecnico, tranne CF |

Le due proposte non conformi strettamente al gold sono entrambe rimaste vuote:
`Via Amedeo 24` dove il FORM stampa già «via» e il gold attende `Amedeo 24`;
`amministratore unico e rappresentante legale` invece della carica abbreviata
nel gold. La seconda è più estesa ma attestata dalla SOURCE; la prima produrrebbe
«via Via» se scritta senza valutare il campo. Non equivalgono a due falsità
fattuali, né autorizzano a cambiare lo scorer o a recuperare automaticamente
le proposte respinte.

Zero discrepanze nelle scritture non significa accuratezza generale del sistema:
la copertura SOURCE è soltanto 27/60. Non sono state verificate abilitazioni o
validità fiscale reale degli identificativi sintetici.

## 3. Perché prima erano stati scritti soltanto 16 dati dei soci

Artefatto storico esaminato: `ui-compilato6-fix-20261017-01/prompt-final/`.
La proposta globale era reale; nel successivo replay il narratore era simulato.
Non va presentato come una precedente prova end-to-end reale.

Il percorso storico è dimostrato dagli snapshot, dai contesti delle tre sintesi,
dalla persistenza finale, dalla selezione export e dai valori fisici nel DOCX:

1. Il modello propone tutti i 24 campi dei soci e tutti superano il grounding.
2. Prima del nome USER ci sono 45 proposte grounded: 16 societarie, 24 dei soci,
   5 del direttore. La prima finestra di 40 include **tutti i 24 soci**.
3. Dopo la scelta nominativa USER, il riuso SOURCE inserisce 8 generalità/carica
   del firmatario prima dei dati societari nell'ordine del catalogo.
4. I 24 campi dei soci passano dalle posizioni 17–40 alle posizioni 25–48.
   Gli otto campi di Andrea passano esattamente da 33–40 a 41–48.
5. La sintesi seguente considera di nuovo solo le prime 40. Il risultato
   **sovrascrive** `reviewed_candidate_ids`, anziché conservare le revisioni
   ancora valide. Tutti gli otto di Andrea, prima presenti, spariscono dalla
   lista persistita. `held_candidate_ids` è vuoto: non è un rifiuto del narratore.
6. Le proposte rimangono grounded e persistite; le condizioni USER sono
   soddisfatte. L'export richiede anche una revisione presente: ne seleziona 16.
   Il report e l'XML contengono esattamente quelle 16.

Riferimenti al codice corrente: `compilation_global_dialogue.py`,
`model_context()` e `narrate()` applicano `[:40]`; `narrate()` ricrea la lista
reviewed e la sovrappone allo stato precedente; `export_selection()` interseca
selectable, reviewed, non-held e condizioni confermate.

Restano anche cinque dati del direttore grounded che non entrano mai nella
finestra. Conservare soltanto le revisioni precedenti recupererebbe gli otto
soci persi, ma non revisionerebbe quei cinque. Non basta alzare il limite o
unire indiscriminatamente ID: la revisione deve restare legata a valore,
soggetto, destinazione, prove e condizioni effettivamente esaminati.

## 4. Traccia delle 24 assegnazioni, nel nuovo run

Nel nuovo run **tutte** sono proposte e persistite, con valori conformi al gold.
Nessuna viene trattenuta dal narratore. Per Luca i validatori recuperano il
record tabellare dal fatto SOURCE; per Elisa e Andrea il binding resta respinto.
Solo i primi otto arrivano alla revisione e all'export.

| Campo | Persona / proprietà | Valore proposto | Grounded / revisionato / scritto |
|---|---|---|---|
| p43.s0 | Luca / nome | Luca Ferri | sì / sì / sì |
| p43.s1 | Luca / qualifica | Ingegnere | sì / sì / sì |
| p43.s2 | Luca / CF | FRRLCU80A01A662K | sì / sì / sì |
| p43.s3 | Luca / albo | Ordine degli Ingegneri di Bari | sì / sì / sì |
| p43.s4 | Luca / sezione | A | sì / sì / sì |
| p44.s0 | Luca / provincia | Bari (BA) | sì / sì / sì |
| p44.s1 | Luca / iscrizione dal | 21/03/2012 | sì / sì / sì |
| p44.s2 | Luca / numero | 7294 | sì / sì / sì |
| p45.s0 | Elisa / nome | Elisa Romano | no / no / no |
| p45.s1 | Elisa / qualifica | Ingegnere | no / no / no |
| p45.s2 | Elisa / CF | RMNLSI85C47A662Y | no / no / no |
| p45.s3 | Elisa / albo | Ordine degli Ingegneri di Bari | no / no / no |
| p45.s4 | Elisa / sezione | A | no / no / no |
| p46.s0 | Elisa / provincia | Bari (BA) | no / no / no |
| p46.s1 | Elisa / iscrizione dal | 18/05/2015 | no / no / no |
| p46.s2 | Elisa / numero | 8421 | no / no / no |
| p47.s0 | Andrea / nome | Andrea Greco | no / no / no |
| p48.s0 | Andrea / qualifica | Architetto | no / no / no |
| p48.s1 | Andrea / CF | GRCNDR84D20A662P | no / no / no |
| p49.s0 | Andrea / albo | Ordine degli Architetti di Bari | no / no / no |
| p49.s1 | Andrea / sezione | A | no / no / no |
| p49.s2 | Andrea / provincia | Bari (BA) | no / no / no |
| p49.s3 | Andrea / iscrizione dal | 12/06/2014 | no / no / no |
| p49.s4 | Andrea / numero | 5267 | no / no / no |

La traccia JSON conserva per ogni campo fatti, binding, citazioni complete,
condizioni e ricevute, revisioni T0/finali, report/XML e confronto con il replay
da 16. Nel raw è presente anche la versione TSV.

### Causa precisa dei 16 rifiuti nuovi

Il modello costruisce un'unica quote con titolo, intestazione, separatore e riga.
Per Luca è la prima riga: l'intero estratto esiste nella SOURCE -54. Il binding
iniziale non riconosce il ruolo nel formato concatenato, ma il recupero
`fact_source_record` verifica titolo/intestazioni/riga della stessa tabella.

Per Elisa e Andrea il modello ripete titolo/intestazione e vi incolla subito
la loro riga, **saltando le righe precedenti**. Non è un estratto letterale
continuo del documento. `_source_quote()` restituisce «Quote SOURCE assente o
non localizzabile univocamente nel file». `_recover_binding()` ricontrolla anche
le citazioni del binding e rifiuta di ignorare quella quote non valida.
Le singole righe citate nei fatti sono invece corrette e già nell'input.

È un errore di rappresentazione delle prove emesse dal modello, non l'assenza
dei soci, non un errore nei valori e non il limite delle 40 revisioni. Conservare
il rifiuto di quote inventate è corretto: non serve rendere fuzzy il controllo.

**Controprova offline, distinta dalla misura UI:** su una copia in memoria
dell'output sono state sostituite soltanto le citazioni dei binding con due
span letterali, titolo e riga della rispettiva persona, nello stesso chunk.
Intestazioni e appartenenza alla tabella vengono controllate dal backend
esistente. Identici fatti, valori, campi, condizioni, schema e validatori:
27→43 grounded, +16 corretti, zero grounded perse. Nessun export, revisione
nuova, sessione mutata o provider; il Word consegnato rimane quello da 27.

Un primo tentativo diagnostico con quattro span distinti non passa: SubjectBinding
ammette al massimo due citazioni. Aveva portato 27→19 grounded, perdendo anche
Luca. Conservato nel raw come controprova fallita; non è una regressione della
prova UI. La forma compatibile dimostrata è **titolo + riga**, con la struttura
verificata nella SOURCE, non quattro citazioni né una concatenazione artificiale.

## 5. Bari/BA: quattro campi diversi, esiti diversi

| Destinazione | Valore / SOURCE | Esito e causa osservata |
|---|---|---|
| p15.s0 Comune iniziale | Bari, -52 «Sede legale — comune» | Respinto: quote FORM `[[p15.s0]] (` senza parole |
| p15.s1 Provincia iniziale | BA, -53 «Sede legale — provincia» | Accettato e scritto: quote `([[p15.s1]]), tel.` supera il gate letterale |
| p41.s1 Comune societario | Bari, -52 | Accettato e scritto; questa volta il modello non propone l'indirizzo completo |
| p42.s0 Provincia societaria | BA, -53 | Accettato e scritto, «prov.» nel FORM |

Bari iniziale è già nell'input: il limite è FORM. «con sede in» si trova alla
fine del paragrafo 14, il campo nel 15. Per includerlo nella prova occorre
ricostruire la continuazione strutturale. All'interno del solo paragrafo 15,
non si può raggiungere «tel.» dal Comune senza attraversare il marker della
provincia: il contratto ammette un solo marker per quote. È quindi un limite
concreto dell'ancoraggio attuale, non risolvibile dicendo genericamente al
modello di citare più testo.

Il BA iniziale è migliorato rispetto ai replay precedenti, perché il modello
ha incluso «tel.» dopo il suo marker. Questo successo prova il funzionamento
del gate attuale, non che «tel.» dimostri semanticamente la provincia.

Correzione minima da valutare: verificare sul parser invariato la continuazione
tra antecedente «con sede in», slot Comune e coppia Comune/provincia, mantenendo
marker e posizione esatti. Valore con SOURCE propria e compatibilità semantica
restano obbligatori. Negativi necessari: indirizzo completo nel Comune,
antecedente in altro ramo/persona, marker di altro campo, parentesi isolate
senza relazione ricostruibile. Nessuna correzione implementata qui.

Il fax scritto è documentato in -53, `integrazione-company.md`:
`- **Fax aziendale sintetico:** +39 080 000 2041.` È un dato aziendale dello
scenario, non un recapito personale di Leonardo.

## 6. Checkbox, domande e decisioni USER

Il modello restituisce `choice_groups: {}`, nessuna proposta checkbox e nessuna
clarification. Le checkbox sono tutte vuote nell'originale e restano tali.
Il writer non ha perso una selezione approvata: nessuna gli è stata inviata.

La scelta di partecipazione come società di ingegneria è espressa nel T0,
trasmesso integralmente alla globale come `recorded_request`, e ripetuta nel
turno successivo. La ricevuta persistita è `condition:c_soc_ing = TRUE`.
Rende applicabili le 27 proposte grounded sotto quella condizione; non crea
una scelta in un gruppo checkbox assente. La casella societaria non selezionata
è quindi un errore effettivo rispetto a una decisione già disponibile.

Restano distinti:

- **Natura giuridica:** fatti aziendali e tipologia documentata, non una scelta
  della gara né la prova dei poteri di una persona.
- **Partecipazione alla pratica:** decisione USER «soltanto società di ingegneria»;
  non autorizza RTP, studio associato o altri rami.
- **Firmatario e poteri:** USER sceglie Leonardo; la SOURCE -53 attesta la carica
  dal 2 ottobre. Nessuna procura o potere speciale è stato dedotto.

La condizione del modello è tuttavia una sola espressione semantica che miscela
rappresentanza e partecipazione, pur etichettandola `legal_type`: il backend
la mantiene UNKNOWN nell'audit originale e applica separatamente la conferma
USER del turno pertinente. La sua conferma non certifica genericamente tutte
le condizioni della pratica. L'altra condizione `c_alt_forms` resta UNKNOWN,
senza bloccare proposte grounded attive; i rami alternativi non sono compilati.

Il narratore iniziale riceve un pool di **una** domanda; dopo la risposta il
pool è **vuoto**. Non si è fermato per il limite di tre domande per turno.
Le motivazioni coverage «manual_input» su preferenze, dichiarazioni,
designazioni e luogo/data non creano campi interrogabili: `question_pool()`
richiede campi FORM validi, disposizione missing/review o gruppi grounded.
Molte motivazioni sono inoltre respinte a livello di singola destinazione.
Il modello può vedere quelle motivazioni ma non può inventare nuovi slot.
La mancata raccolta USER dipende quindi anche dall'inventario delle domande,
non soltanto dalla frase generata dal narratore.

Le altre due caselle positive del gold, veridicità e professionisti esecutori,
richiedono attestazioni/designazioni **non ancora ricevute**. Lasciarle vuote
è corretto in questa sessione; non aver chiesto quelle informazioni resta una
lacuna del dialogo. Stesso criterio per le sei preferenze e i quattro campi
USER testuali. Non attribuire incarichi ai soci soltanto perché sono soci,
direttore tecnico o responsabile qualità.

Proposta minima: creare/richiedere il gruppo di partecipazione dal FORM con
opzioni e cardinalità verificate; associarvi la specifica decisione USER solo
dopo verifica di ambito e polarità. Per gli altri vuoti, rendere interrogabili
soltanto richieste già ancorate e validate, preservando rinvii e conferme.
Non promuovere tutte le coverage a domande/valori, non selezionare automaticamente
checkbox dal nome della società o da una condizione generica. I cambiamenti
richiedono prove dedicate prima dell'integrazione; qui sono soltanto proposti.

Il filtro prudente del narratore è intervenuto anche in questa prova: il testo
raw accorpava impropriamente socio e direttore tecnico e diceva non documentate
scelte già fornite. La UI ha mostrato il riepilogo backend che distingue
omissioni, scarti e attese, senza certificare l'assenza SOURCE. È una protezione
osservata; non dimostra la correttezza semantica universale delle sintesi.

## 7. Firmatario e direttore: regressioni concrete

Le nove proposte relative a Leonardo sono presenti nel JSON. Otto falliscono
il binding `b_mont`: cita «in qualità di» nel paragrafo 14, mentre quel testo è
nel 13; il FORM generico non enuncia neppure il ruolo societario completo che
il binding dichiara richiesto. Il nono campo, provincia di residenza, ha una
quote marker-only. I dati personali e la carica sono nelle SOURCE -53/-54.

La scelta nominativa compare nel T0 e nella ricevuta della **condizione**, ma
non esiste una ricevuta `VALUE` del campo firmatario. Il riuso locale attuale
richiede proprio quella ricevuta; non legge arbitrariamente nomi da altri
slot. Inoltre il fallback della domanda sul nome esclude campi con proposta
già presente o errori, e il riuso non sostituisce proposte MODEL respinte.
Perciò il percorso di riuso validato nei replay precedenti **non viene attivato**
qui. Non va dichiarato verificato positivamente dalla nuova prova UI.

Intervento minimo da discutere: rendere recuperabile/interrogabile questo caso
con una selezione nominativa esplicita, verificata e legata al suo slot, poi
riesaminare separatamente ciascuna proprietà SOURCE senza cancellare la proposta
respinta. Non usare una conferma della condizione come prova anagrafica né
sostituire in blocco proposte conflittuali. Serve anche il negativo «via Via».

Per il direttore, il binding in -45 attesta effettivamente Elisa nel ruolo.
Il modello però riusa come prova dei valori le righe **dei soci** in -54:
il trasferimento cross-record attuale ammette solo CF e provincia canonica con
identità forte. Il CF passa; gli altri sette no. La property `provincia_albo`
non è la property canonica `provincia` del percorso ammesso. Qualifica, albo,
data e numero hanno prove dirette riferite al direttore in -45/-55: richiedono
citazioni pertinenti, non l'estensione automatica di tutti i trasferimenti.
Anche questa è una rappresentazione proposta male, non sette dati assenti.

## 8. Confronto post-export con GOLD V1

Gold e scorer non sono stati ritoccati. Sono state lette fisicamente le posizioni
nell'XML, non soltanto contati gli ID del report.

| Aspetto | Confronto e interpretazione |
|---|---|
| 60 testi SOURCE attesi | 27 corretti scritti; 33 vuoti non giustificati da assenza SOURCE |
| 4 testi USER | Tutti vuoti: designazioni, integrazione specialistica e luogo/data mai chiesti/ricevuti |
| 6 preferenze positive | Tutte vuote; decisione mai chiesta/ricevuta, non sei valori SOURCE errati |
| 61 preferenze non selezionate | Fisicamente vuote; non contate come 61 decisioni correttamente raccolte |
| 13 checkbox native | Tutte false; 10 corrispondono alle alternative/non applicabilità T0; 1 positiva T0 manca; 2 positive attendono USER |
| 123 testi da lasciare vuoti | Tutti conservati: 120 di altri rami, 2 continuazioni non usate, firma |

Questo export è un **T2 parziale prima del T1 completo**. Non ha senso assegnargli
un'unica accuratezza sul gold finale, accorpando mancate risposte e valori errati.
I 33 vuoti SOURCE e la casella societaria sono problemi effettivi; le decisioni
mai raccolte misurano invece l'insufficienza del dialogo. Nessuna firma,
abilitazione aggiuntiva o attestazione documentale è stata inventata.

Verifiche: CRC ZIP, parse di tutte le parti XML/rels, pacchetto invariato salvo
`word/document.xml`; 27 scritture identiche al report e nelle posizioni giuste;
prestampato invariato salvo l'avviso di bozza; quattro tabelle e 13 controlli
nativi identici all'originale, nessuna scrittura nei rami alternativi.

Rendering LibreOffice: nuovo Word 10 pagine, gold congelato 9. Viste le pagine
1, 3 e 10 del nuovo PDF e il blocco soci del gold: pagina 1 senza generalità,
solo Luca a pagina 3, CF del direttore isolato dagli altri suoi dati, firma
vuota da sola a pagina 10. Permangono giunzioni del prestampato, ad esempio
«professionaleOrdine». Il renderer ha segnalato un warning liblangtag, conservato
nel log; conversione riuscita. Nessuna certificazione Microsoft Word o revisione
visiva integrale delle dieci pagine dichiarata.

## 9. Confronti storici e limiti causali

| Artefatto | Scritture | Soci | Tipo di prova |
|---|---:|---:|---|
| compilato(6) reale | 25 = 24 SOURCE + nome USER | 0 | Vecchio run UI dell'utente |
| Stesso output con riuso corretto | 33 = 32 SOURCE + nome USER | 0 | Replay, narratore simulato |
| Nuovo prompt, export storico | 41 = 40 SOURCE + nome USER | 16 | Globale reale, dialogo successivo simulato |
| B0-03 con riuso | 56 = 55 SOURCE + nome USER | 23 | Replay con revisione manuale preesistente |
| Nuova UI reale corrente | 27 = 27 SOURCE | 8 | Nuova risposta globale e dialogo reali |

B0-03 con riuso lascia anche una provincia di un socio respinta: non arrotondare
i suoi soci a 24. La traccia delle differenze fisiche è nel raw
`historical-comparisons.json`.

Rispetto al download reale compilato(6): dieci destinazioni nuove scritte,
otto perse, nessun valore cambiato nelle 17 destinazioni comuni. Nuove: BA
iniziale, otto dati di Luca, CF direttore. Perse: nome firmatario e altri sette
dati direttore. Rispetto al replay da 41: tre destinazioni nuove, diciassette
perse; rispetto al B0 manuale: una nuova, trenta perse. «Ing. Luca Ferri» e
«Luca Ferri» sono una differenza letterale ammessa dallo scorer.

Sono regressioni **osservate nel risultato**, non la prova che una singola
modifica del codice le abbia causate: input USER e risposta modello differiscono;
B0 includeva revisione manuale, gli altri replay una sintesi simulata. Un run
non misura varianza o stabilità del provider. Conservare tutti i risultati,
compresi quelli peggiori, rende ora possibile un confronto successivo serio.

## 10. Tempi, token e costo

Sette chiamate effettive: una globale, due narratori, tre routing e una verifica
semantica USER. Nessun retry qualitativo, nessuna seconda globale. Le controprove
di citazione e l'analisi del vecchio 16 sono interamente offline.

| Stadio con usage completo salvato | Input | Output | Di cui reasoning | Tempo provider misurato |
|---|---:|---:|---:|---:|
| Globale | 76.616 | 40.083 | 24.507 | 142,10 s |
| Due narratori | 21.215 | 255 | 0 | 4,08 s |
| Routing risposta + export | 8.914 | 179 | 0 | 2,99 s |

Per la globale restano 15.576 token di output oltre al reasoning: non sono
40.083 token di solo JSON. Cache input globale: 1.920 hit, 74.696 miss.

Totale dell'intero percorso: **153.384 token**. La ripartizione completa
input/output è disponibile per cinque chiamate: 106.745 input + 40.517 output.
Per routing iniziale e guard USER il sistema conserva soltanto i totali,
rispettivamente 3.942 e 2.180: **6.122 token senza split**. Il router iniziale
non ha ancora una sessione a cui allegare il RoutingTrace; il guard non persiste
request/response/usage dettagliata. Non li ho ricostruiti fingendoli acquisiti,
né ho ripetuto la prova per ottenerli. Per questi due passaggi il numero di
chiamate segue il percorso eseguito e i totali registrati; mancano i grezzi HTTP.

Somma delle cinque POST sequenziali dal browser: **154,76 s**, circa 2 min 35 s,
comprende elaborazione server e rete. Sessione browser complessiva **235,50 s**,
comprende letture e attese dell'operatore: non è tutta latenza del sistema.

Costo stimato, non addebito verificato: **0,0390–0,0427 USD** per il percorso.
La parte con usage completo vale 0,038948 USD; l'intervallo copre lo split
ignoto dei 6.122 token, da cache hit a output. Tariffe Flash off-peak per milione:
0,003 USD input hit, 0,15 input miss, 0,60 output; chiamate di domenica.
[Fonte ufficiale DeepSeek, consultata il 18 ottobre](https://api-docs.deepseek.com/quick_start/pricing/).
Nessuna lettura del saldo/account di fatturazione.

## 11. Correzioni minime proposte, in ordine

| Intervento proposto | Causa dimostrata / verifica necessaria | Costo e rischio |
|---|---|---|
| Conservare revisioni valide e visitare proposte nuove/non revisionate | Replay storico: otto soci perdono review dopo il riuso; confrontare impronta di valore/soggetto/FORM/SOURCE/condizioni; verificare cambi, held, export e i cinque DT mai rivisti | Replay iniziale 0 LLM; eventuale sintesi su nuova finestra, nessuna nuova globale. Rischio: conservare revisioni obsolete, quindi niente semplice unione ID |
| Precisare il formato delle prove tabellari nel prompt esistente | Due span letterali titolo+riga passano già; quote concatenata o quattro span no. Identici fatti/valori/validatori nella controprova | Nessun layer o FORM nuovo; dopo la modifica serve una futura prova globale controllata. Mantenere negativi persone/tabelle diverse e quote inesistenti |
| Recuperare ancoraggi di continuazione Comune/provincia | Bari disponibile, FORM diviso tra paragrafi; associare la struttura esatta senza ammettere marker isolati generici | Verifica offline, 0 LLM. Rischio: legare al ramo sbagliato o ammettere indirizzi completi |
| Gestire la scelta del firmatario quando la proposta MODEL è respinta | T0/ricevuta condizione non sono un VALUE nominativo; fallback e riuso attuali non scattano | Prima un test della selezione con slot verificato e prove SOURCE separate. Non cancellare conflitti né attribuire poteri |
| Richiedere gruppi checkbox e rendere interrogabili i vuoti validi | Gruppi assenti, pool 1→0 nonostante coverage manual_input | Test cardinalità/ambito/negazioni; nessuna selezione automatica da natura giuridica. Non basta cambiare il testo del narratore |
| Usare le prove dirette dei dati del direttore | Sette rifiuti con ruolo -45 e valori citati come soci -54 | Citazioni -45/-55 o property canonica nei soli casi già supportati; non estendere il trasferimento di qualifiche/ruoli |

Una formulazione minima da valutare nel prompt è: «Ogni quote deve essere un estratto
continuo della SOURCE. Per una tabella usa al massimo due span distinti: titolo
e riga del soggetto; non concatenare parti saltando righe. Il backend verifica
le intestazioni e l’appartenenza alla medesima tabella». È testo proposto nel
rapporto, non una modifica alle istruzioni attive.

La prima correzione è il difetto software più circoscritto e riproducibile senza
nuova inferenza. La seconda affronta il nuovo fallimento senza indebolire il
verificatore. Prima di attribuire a E1 un guadagno, questi difetti vanno almeno
misurati separatamente: un JSON più piccolo non ripara da solo revisioni perse,
quote inesistenti, pool vuoti o decisioni checkbox non rappresentate.

Sono proposte, non implementazioni autorizzate implicitamente da questo rapporto.
V12 corretta resta il riferimento recuperabile; nessun nuovo motore, migrazione,
reindicizzazione o framework. La futura E1 dovrà confrontare input USER identici,
FORM/SOURCE/gold congelati, tutti gli stadi e lo stesso protocollo di risposte,
conservando anche fallimenti e costo totale, non soltanto token della globale.

## 12. Conservazione e verifiche di questa consegna

Raw: `backend/data/compilation-audit/ui-v12-e2e-20261018-01/`. Contiene protocollo,
input, schema, prompt, output grezzo, HTTP acquisiti, audit, routing, sintesi,
stati/revisioni, conversazione, DOCX, scoring XML, immagini e metriche; anche
le prove controfattuali riuscita/fallita, separate dal risultato reale.

Il backup pubblicabile comprende video completo e trace campionata a 5 secondi,
con eventi API/DOM/azioni preservati. La trace originale da circa 936 MiB,
9.384 frame, rimane locale; hash, dimensione e omissione dal backup sono
espliciti in `trace-sampling.json`. Non è l'unica prova del percorso: richieste
browser, conversazione, screenshot dei checkpoint, video e audit sono nel bundle.
Database e chiavi restano privati ed esclusi dal backup.

Verificati invariati 205 file protetti di codice/test/frontend/fixture,
29 sessioni originali con versioni/stati e 273 file storage originali confrontati
con la copia preventiva. Download e report coincidono con quelli restituiti
dall'export. Test software completi non rieseguiti per questa sola diagnosi;
i 2.459 test riportati nella consegna precedente restano verifiche storiche.
Qui sono stati eseguiti browser reale, replay dei validatori senza rete,
controlli XML/gold e controllo visuale mirato. Dieci ERR_ABORTED del browser
riguardano GET annullate durante mount/refresh; zero errori JavaScript o POST
fallite osservati. Le richieste completate rispondono 200.

Terminato dopo prova e diagnosi. Nessuna modifica del sistema o avvio di E1.
