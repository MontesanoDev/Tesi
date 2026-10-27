# Diagnosi offline di una compilazione DOCX — 27 ottobre 2026

## Perimetro e prove congelate prima delle correzioni

Base `796afaf81589c3611bd28ccf1a04230619f0a93c`, worktree separato,
branch `fix/2026-10-27-conferme-docx`. Nessuna inferenza, adozione, merge o push.
I dati della compilazione non sono fixture pubblicabili: copie e tracce dettagliate
restano in `backend/data/compilation-audit/diagnosi-compilato7-20261027-01/`
del checkout ordinario, escluso da Git. Questo rapporto omette nominativi e dati personali.

Il DOCX scaricato coincide byte per byte con l'export archiviato. Acquisiti FORM,
SOURCE usate nell'analisi, proposta e audit iniziali/finali, richieste e risposte
registrate del narratore e router, sette turni, diciotto eventi di revisione,
decisioni, hold e report di export. Gli eventi NON sono diciotto snapshot completi.
Le risposte grezze della guardia semantica USER non sono conservate in questi
artefatti: non è possibile attribuire con certezza ogni prima conferma respinta.

## Difetti riprodotti e classificazione

| Destinazione | Catena osservata | Causa e certezza |
|---|---|---|
| Nome del sottoscrittore | Campo FORM p12.s0; nessuna proposta SOURCE; risposta USER VALUE accettata, valore persistito, nessun hold; selezione USER vuota; segnaposto conservato | **Backend, verificato.** Il riuso SOURCE sostituisce la citazione FORM parziale con il paragrafo intero. La ricevuta di ambito è valida contro l'audit iniziale, non contro quello derivato. Il veto finale è corretto; è scorretto mutare la destinazione già verificata. |
| Carica del sottoscrittore | p14.s0; riuso SOURCE documentato e condizione USER confermata; hold SOURCE del narratore; esclusione dall'export | **Sospensione reale, motivazione temporale non sostenuta dal contesto.** Il narratore interpreta come futura una decorrenza precedente alla data di riferimento già presente nella richiesta. Il controllo della motivazione ne verifica l'ancoraggio, non la verità. Il riesame limitato ai record con subject binding non copre questo percorso di riuso. Non va rilasciato automaticamente tramite una conferma USER. |
| Casella della rappresentanza societaria | p39.cb0 content control; modello senza proposta booleana né choice group; condizione riconosciuta; ricevuta USER dei campi testuali non comprendente la checkbox; nessun valore checkbox all'export | **Omissione a monte, non guasto dimostrato del writer.** Il collegamento conservativo ricevuta→casella non accetta l'aspetto representation, né la citazione incompleta rispetto al paragrafo. Non basta ampliare una regex: manca anche una verifica USER su questa destinazione. |
| Parole unite | Puntini contigui a “professionale” e “della” già nel FORM; valori SOURCE selezionati e corretti; sostituzione letterale dei puntini | **Rendering, verificato nell'XML DOCX.** Il writer non separa parole adiacenti ai leader di puntini. Non è solo un problema di conversione PDF. |
| Ricevuta della conversazione | Conferme, valori e decisione senza destinazione verificata nello stesso turno; risposta generica “decisione registrata” | **Presentazione backend.** La decisione pendente riguarda luogo/data, non il nome. La ricevuta non identifica i punti accettati, rinviati o non accettati. |

Le tredici checkbox native hanno sia stato interno `w14:checked=0` sia glifo
visibile non selezionato. Il fix delle checkbox testuali non si applica a queste.
Prima di modificare questo percorso occorre verificare separatamente il writer
nativo con selezione autorizzata e non selezione; nessuna spunta verrà aggiunta
alla sessione storica inventando una ricevuta.

## Rinvii e limiti del narratore

Restano vuoti categorie/fasce, attestazioni, designazioni dei professionisti e
data di iscrizione espressamente rinviata. Luogo/data sono una decisione
persistita con `write_authorized=false`, non una scrittura acquisita.

Le prime due conferme non risultano accettate; sono chieste di nuovo. Dopo
l'accettazione non risultano nuovamente chieste. Non è quindi dimostrato un
“oblio” di queste due ricevute. È invece certa l'insufficienza della spiegazione
dei rifiuti; il verdetto originale della guardia non è disponibile.

Ulteriore incoerenza: una domanda sulla data di iscrizione nomina un soggetto
diverso da quello della destinazione attiva p46.s1. Il rinvio viene associato
allo slot; un successivo hold USER conserva vuota anche la data p49.s3 della
persona nominata. Non recuperare nessuna delle due date in questo intervento.
La generazione delle domande non garantisce l'identità del soggetto menzionato.

## Disegno minimo e criteri prima dei fix

1. **Ricevuta del nome:** conservare label e prova FORM già validate quando il
   riuso prepara il campo; aggiungere quelle sintetiche solo se mancanti.
   Non cambiare hash, guardia, destinazioni o autorizzazioni; cambi reali di
   FORM/condizioni devono continuare a invalidare la ricevuta.
2. **Spazi:** separatori solo ai confini alfabetici di leader di puntini con
   parole adiacenti riconoscibili. Test negativi per codici, date, underscore,
   punteggiatura e controlli Word. Valore fattuale e prove rimangono invariati.
3. **Ricevute leggibili:** nominare i punti accettati, pendenti, rinviati e non
   accettati; distinguere registrazione da scrittura. Nessuna nuova decisione,
   domanda o autorizzazione introdotta dal testo di presentazione.

I test sintetici devono fallire prima della rispettiva modifica. Poi verificare
veto API, ambito USER, SOURCE reuse, controlli nativi e suite backend/Ruff.
Ogni fix avrà commit e rollback separati. Il confronto privato del DOCX dovrà
passare dalla selezione e rivalidazione reali, senza inserimenti manuali.

Esecuzione preliminare: **9 FAIL, 19 PASS**. Un fallimento sulla ricevuta del
nome, sei sui confini di parola (tre casi anche su run separati), due sulle
ricevute conversazionali. La prima versione del test di rendering puntava al
paragrafo dell'avviso BOZZA: corretto il test prima di modificare il writer;
entrambi i log restano conservati nell'audit privato.

**Fuori da questi fix:** rilascio automatico del hold SOURCE, promozione di una
conferma testuale a checkbox non verificata, interpretazione semantica generale
delle domande. Sono limiti da mostrare nel risultato, non da nascondere mediante
un DOCX compilato a mano. La diagnosi e la revisione sono autoriali, non indipendenti.
