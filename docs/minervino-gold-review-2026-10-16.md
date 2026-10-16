# Revisione del gold sintetico di Minervino

**16 ottobre 2026 — candidato gold dell'utente, non ancora congelato.**

Il gold contiene dati anagrafici e societari coerenti con la KB attuale e
rappresenta una compilazione molto più estesa della bozza del sistema.
**Prima di congelarlo occorre ripristinare il blocco del direttore tecnico
e rendere esplicite le decisioni della pratica che compaiono soltanto nel gold.**

Esaminati il [gold sintetico](<../nuovi dati/domanda-iscrizione.GOLD-SINTETICO.docx>),
l'[originale](../demo-documents/bandi/minervino-elenco-sia/originali/domanda-iscrizione.docx),
il relativo avviso e i documenti effettivamente presenti nel backend.
Il gold e la KB non sono stati modificati o caricati altrove.

## 1. File e perimetro verificati

| Elemento | Originale | Gold |
|---|---|---|
| SHA-256 | `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c` | `c4dbd36e5d1a02f987bdabde3f3cd67ab4e47291aff9d737666bfd4d875991bf` |
| Dimensione | 63.494 byte | 74.309 byte |
| Paragrafi diretti nel corpo | 130 | 127 |
| Paragrafi totali, incluse tabelle | 246 | 243 |
| Tabelle | 4 | 4 |
| Righe delle quattro tabelle | 18 / 2 / 4 / 11 | 18 / 2 / 4 / 11 |
| Checkbox native | 13 | 13 |
| Checkbox selezionate | 0 | 3 |
| Celle marcate X | 0 | 6 |

L'originale archiviato coincide con il modulo attualmente conservato nel
backend per Minervino. Gli identificatori dei 13 controlli Word sono
conservati; simboli visibili e stati nativi delle caselle sono coerenti.

Il salvataggio del gold ha modificato anche stili, metadati e altre parti XML,
aggiungendo parti di note. Questo, da solo, non è un difetto: un editor può
riscrivere tali parti. Non si deve usare l'identità binaria dei DOCX come
criterio di correttezza del risultato.

Sono stati controllati testo e struttura XML. La paginazione e gli eventuali
overflow non sono stati verificati con Word/LibreOffice. Formato A4 e margini
principali restano corrispondenti; ciò non garantisce la stessa impaginazione.

## 2. Correzione principale: direttore tecnico

Dopo il paragrafo:

> la quale ha come Responsabile della Progettazione (...) o Direttore Tecnico (...):

il gold passa direttamente alla casella del capogruppo RTP. Rispetto
all'originale sono stati eliminati i tre paragrafi destinati ai dati del
direttore, non soltanto lasciati vuoti.

| Destinazione nell'originale | Richiesta | Valore documentato da riportare |
|---|---|---|
| `p51.s0` | Nome e cognome | Elisa Romano, con eventuale titolo Ing. |
| `p52.s0` | Qualifica | Ingegnere |
| `p52.s1` | Codice fiscale | RMNLSI85C47A662Y |
| `p53.s0` | Ordine | Ordine degli Ingegneri di Bari |
| `p53.s1` | Sezione | A |
| `p53.s2` | Provincia | Bari / BA secondo la convenzione scelta |
| `p53.s3` | Iscrizione dal | 18/05/2015 |
| `p53.s4` | Numero di iscrizione | 8421 |

La KB attesta che Elisa è il direttore tecnico. Il fatto che i suoi dati siano
già compilati nel blocco dei soci non soddisfa questa diversa occorrenza del
modulo. La ripetizione è significativa per il benchmark: la stessa persona
ricopre due ruoli richiesti in due posizioni.

**Azione consigliata:** ripristinare dall'originale quei tre paragrafi e
compilarli mantenendo le etichette e le destinazioni. Altrimenti il gold
elimina proprio otto campi che vogliamo verificare, inclusi quattro già
individuati come problema nella compilazione automatica.

## 3. Corrispondenza dei valori con la KB attuale

La verifica usa il corpus autorizzato del progetto letto da SQLite in sola
lettura: 56 frammenti, di cui 18 Company KB. Le fonti aziendali sono:

- generalita-mapi.md, documento globale 7, nove frammenti;
- visura-mapi-ingegneria-simulata.pdf, documento globale 9, quattro frammenti;
- integrazione-company.md, documento globale 10, cinque frammenti.

Sono state confrontate **52 occorrenze testuali**: 19 nell'anagrafica iniziale,
nove nel blocco dei dati della società e 24 nei tre record dei soci.
I valori di queste occorrenze corrispondono ai dati nelle fonti, considerate
le equivalenze di presentazione sotto indicate. Questa è una revisione delle
corrispondenze, non una percentuale di accuratezza o un gold strutturato approvato.

| Gruppo | Verifica |
|---|---|
| Leonardo Montemurro | Nome, nascita a Lecce/LE il 14/11/1982, residenza a Bari, indirizzo Amedeo 24 e CF corrispondono all'integrazione |
| Rappresentanza | Leonardo è documentato come amministratore unico e rappresentante legale dal 2 ottobre 2026; la data del gold è successiva |
| Identità e sede della società | Denominazione, Bari/BA, Via Giovanni Amendola e civico 172/C corrispondono |
| Recapiti | Telefono, fax, e-mail e PEC coincidono con generalità e integrazione |
| Camera di Commercio / Registro Imprese | Bari e 01234560981 corrispondono all'integrazione; non è stato usato il REA al posto del Registro Imprese |
| Luca Ferri, socio | Qualifica, CF, Ordine, sezione A, provincia, data 21/03/2012 e numero 7294 corrispondono alla tabella dei soci |
| Elisa Romano, socia | Qualifica, CF, Ordine, sezione A, provincia, data 18/05/2015 e numero 8421 corrispondono |
| Andrea Greco, socio | Qualifica, CF, Ordine, sezione A, provincia, data 12/06/2014 e numero 5267 corrispondono |

Equivalenze da registrare prima dello scoring:

- `14/11/1982` e «14 novembre 1982» indicano la stessa data;
- «Bari» nel campo provincia è coerente con «Bari (BA)» nella fonte;
- «Ing.» e «Arch.» aggiunti ai nomi sono compatibili con le qualifiche attestate;
- nella residenza «via» è già testo del modulo: «via Amedeo 24» rappresenta
  l'indirizzo documentato «Via Amedeo 24».

La cessazione di Luca Ferri al 1 ottobre non contraddice la sua presenza tra
i soci al 15 ottobre. Incarico amministrativo e partecipazione societaria
sono dati distinti. Non emerge un errore del gold su questo punto.

Il vecchio profilo indica alcune informazioni come non disponibili; la nuova
integrazione le fornisce successivamente. Per il benchmark occorre conservare
le versioni e la data di riferimento, senza trattare il vecchio vuoto come
un divieto permanente di usare il dato aggiornato.

### 3.1 Controllo dell'indicizzazione

Per l'integrazione, i chunk rigenerati coincidono con quelli nel DB.
Per le generalità il partizionamento storico differisce da quello del
frammentatore corrente, ma ricomponendo i chunk si ottiene esattamente il
testo normalizzato del file, 8.440 caratteri. Anche l'integrazione si ricompone
integralmente, 4.322 caratteri normalizzati.

Questa differenza di partizionamento non dimostra perdita di dati o necessità
di reindicizzare. Il pacchetto di benchmark dovrà specificare se congela i
file originali per un import nuovo oppure usa il corpus già estratto.

### 3.2 Identificativi sintetici

La P.IVA `IT01234567890` corrisponde esattamente alla KB, che la dichiara
fittizia e non formalmente valida. Non è un errore di trascrizione introdotto
nel gold. I CF personali sono anch'essi dichiarati dimostrativi nelle fonti.

La corrispondenza documentale non certifica la validità formale degli
identificativi: in questa revisione non sono stati eseguiti controlli dei
loro checksum o riscontri anagrafici.

Prima del congelamento va annotata la policy: valutare la fedeltà al dato
sintetico oppure usare uno scenario ordinario con identificativi formalmente
validi e tenere quelli invalidi come casi negativi separati. Eventuali
cambiamenti devono essere coerenti fra fonti e gold, in una nuova versione,
senza correggere silenziosamente i dati della demo.

## 4. Scelte del gold che la KB non contiene

Questi contenuti possono far parte dello scenario sintetico, ma devono essere
comunicati al sistema nel momento previsto dal test. Il solo gold non è
un input accessibile al compilatore.

### 4.1 Partecipante e firmatario

La KB documenta società e ruoli, ma non determina quale soggetto presenti una
specifica domanda. Nel caso osservato l'utente aveva già confermato Mapi,
ramo società di ingegneria e Leonardo come firmatario.

Nel nuovo benchmark queste informazioni vanno inserite nella scheda di
scenario, decidendo se sono note all'avvio oppure acquisite in risposta
alle domande. Il gold finale corrisponde allo stato successivo alle conferme.

### 4.2 Sei preferenze

| Tabella originale | Voce scelta | Fascia / preferenza | Destinazione originale |
|---|---|---|---|
| Progettazione / direzione lavori | Edilizia scolastica e sanitaria | B | `t0.r3.c2` |
| Progettazione / direzione lavori | Strutture | B | `t0.r8.c2` |
| Progettazione / direzione lavori | Opere stradali | A | `t0.r13.c1` |
| Sicurezza | CSP/CSE | A | `t1.r1.c1` |
| Collaudo | Collaudo statico | X | `t2.r1.c1` |
| Altri servizi | Certificato di prestazione energetica | X | `t3.r10.c1` |

Le sole differenze testuali nelle celle delle quattro tabelle sono queste
sei X; categorie e altre celle sono conservate. Con il conteggio delle voci
selezionate il caso arriva a sei, coerente con «max. 6 tipologie» del modulo.
È un utile caso di confine; l'ambito del conteggio va scritto nella scheda.

La KB descrive attività generali ma non contiene queste sei scelte di
candidatura. Devono derivare da decisioni USER, non da una deduzione basata
sul profilo aziendale.

### 4.3 Designazioni professionali

Il gold aggiunge:

- Elisa: progettazione strutturale e direzione lavori;
- Luca: opere stradali e collaudo statico;
- Andrea: progettazione edilizia, certificazione energetica e CSP/CSE;
- Andrea: integrazione delle prestazioni specialistiche.

Le fonti attuali non assegnano queste prestazioni alle persone. Nell'integrazione
è esplicito che il ruolo aziendale non costituisce una designazione per uno
specifico incarico.

Si possono mantenere come scelte dello scenario, con una risposta USER o un
documento di designazione pertinente alla pratica. La designazione non prova
automaticamente requisiti o abilitazioni ulteriori: se il benchmark vuole
verificare anche quelli, occorrono prove dedicate. Per una prova di compilazione
del modulo basta chiarire il perimetro e l'origine della decisione.

### 4.4 Attestazioni, luogo e data

Sono selezionate anche la dichiarazione di veridicità e quella relativa ai
professionisti esecutori. Bari e 15/10/2026 sono indicati come luogo e data.

La KB non contiene una scelta della data della domanda, le attestazioni
personali o una verifica dei curricula allegati. Questi elementi vanno
registrati come decisioni/attestazioni dello scenario. Senza tale input il
comportamento atteso è chiedere o lasciare aperto, non replicare ciò che il
gold contiene.

L'avviso locale, pagine 7–8, menziona curriculum, documento del sottoscrittore
e dichiarazioni ulteriori. Non sono presenti come fascicolo completo nella
KB del caso. Se il benchmark misura il solo DOCX principale, si dichiarano
fuori perimetro e non si valuta la pratica come pronta all'invio. Se comprende
gli allegati, occorre prepararli e annotarne disponibilità e aspettative.

## 5. Vuoti e controlli correttamente conservati

Sono coerenti con lo scenario di una società di ingegneria:

- i rami di professionista singolo, studio associato, RTP e consorzio lasciati
  vuoti e le relative caselle non selezionate;
- l'alternativa di iscrizione all'albo nell'anagrafica dell'operatore lasciata
  vuota mentre sono compilati gli estremi camerali;
- le preferenze non scelte lasciate vuote;
- la firma digitale lasciata vuota, senza una firma simulata.

Le tre checkbox vere sono controlli nativi con valore checked=1, non soltanto
simboli ☒ digitati. Le altre dieci sono checked=0. Identificatori e simboli
sono coerenti. Questo è un punto utile da conservare nel riferimento finale.

Il testo «Nessun altro professionista previsto...» e la nota didattica finale
sono aggiunte autoriali. Va indicato se sono annotazioni del gold oppure testo
che il compilatore dovrà scrivere; non devono diventare requisiti impliciti
desunti dal solo file di riferimento.

## 6. Fedeltà all'originale e scoring

Alcune frasi prestampate sono state riscritte o abbreviate: per esempio la
premessa ai soci e l'etichetta «Ordine/Collegio professionale». Sono cambiamenti
distinti dai valori da inserire.

Per il gold definitivo consiglierei di conservare le etichette originali,
aggiungendo soltanto valori e marcature. Ciò facilita la verifica delle
destinazioni e delle parti da preservare. I punti e virgola migliorano la
lettura, ma non devono imporre al writer una riscrittura non prevista.

Il valutatore dovrà accettare le equivalenze deliberate di data, sigla,
titolo e spaziatura. Dovrà invece rilevare una destinazione eliminata, un
valore nella posizione di un altro ruolo, una casella sbagliata o una
modifica involontaria a una sezione non pertinente.

Non si confrontano gli indici dei paragrafi del gold come se fossero quelli
dell'originale: dopo i tre paragrafi eliminati gli indici sono spostati.
La mappa delle aspettative usa le destinazioni dell'originale.

## 7. Cosa fare prima di congelare

| Priorità | Attività | Esito richiesto |
|---|---|---|
| Necessaria | Ripristinare i tre paragrafi del direttore | Tutte le otto occorrenze presenti e compilate con Elisa |
| Necessaria | Scrivere la scheda dello scenario | Partecipante, firmatario, sei preferenze, designazioni, attestazioni, luogo/data e momento di disponibilità espliciti |
| Necessaria | Affiancare il gold strutturato | Valore/esito, prova, soggetto, condizione e motivazione dei vuoti per ogni richiesta |
| Da definire | Gestire gli identificativi sintetici | Policy coerente fra fedeltà alle fonti e controlli formali |
| Consigliata | Conservare le etichette prestampate | Differenze concentrate sui campi compilati e sulle scelte |
| Da eseguire | Controllare il layout in un editor | Nessun testo tagliato o sovrapposto; tabelle e controlli leggibili |
| Successiva | Congelare originali, fonti, scenario e gold | Versione e manifest condivisi, senza caricamento del gold nella KB |

**Esito della revisione: candidato da correggere, non ancora base congelata.**
Non è necessario ricostruire da zero tutti i dati aziendali: gran parte del
contenuto già compilato è documentato. Il punto principale è completare il
ruolo mancante e rendere valutabili le informazioni specifiche della pratica.

## 8. Acquisizioni e limiti

- [Riepilogo e confronto delle 52 occorrenze](benchmarks/2026-10-16-minervino-gold-review.json).
- [Bundle delle acquisizioni](benchmarks/2026-10-16-minervino-gold-review-audit.tar.gz)
  e [checksum](benchmarks/2026-10-16-minervino-gold-review-audit.tar.gz.sha256).
- Grezzi locali: `backend/data/compilation-audit/minervino-gold-review-20261016T135700Z/`.
- Bundle: 17 file, 232.310 byte, SHA-256
  `a10cf1cba283021923c98f04e60fe0dd1bd6f2c733836da1bdbd672030650762`.

Conservati originale e gold ricevuto, fonti attuali, corpus, metadati dei
documenti, testo estratto, diff e confronto con prove localizzate.
Un primo raccordo delle prove si è interrotto per gli spazi multipli del
Markdown rispetto ai chunk normalizzati: completato dichiarando tale
normalizzazione, senza cambiare i dati.

Nessun file di database né profilo con credenziali è incluso nel bundle.
Il corpus e i metadati letti in sola lettura sono acquisizioni selezionate,
non una copia del DB. Il gold non risulta nel corpus autorizzato del progetto.

File dell'utente e originale invariati. Nessuna nuova chiamata LLM,
compilazione, suite applicativa, modifica al motore o alla KB. Questo controllo
non certifica requisiti professionali o validità anagrafica e non sostituisce
la revisione visuale in Word.
