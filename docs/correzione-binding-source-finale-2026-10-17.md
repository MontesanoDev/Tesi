# Ultima correzione KISS dei binding SOURCE

17 ottobre 2026. Intervento autorizzato a partire dalla
[diagnosi degli undici rifiuti](diagnosi-undici-source-2026-10-17.md).
Una sola chiamata globale resta l'obiettivo; qui sono state usate solo le
risposte già acquisite. Nessuna nuova chiamata LLM, modifica al FORM B0,
modello, thinking, API o writer. Nessun framework, caso aziendale o ID di
benchmark nel codice di produzione. Nessun commit o push.

## Metodo e confini

Conservati gli input, le risposte e gli ultimi audit nella nuova directory
`backend/data/compilation-audit/binding-final-20261017-01/`.
Prima di modificare il verificatore sono stati riprodotti esattamente i due
audit precedenti. Le due SOURCE sono identiche, entrambi gli input senza
USER. INDEX usa la copia offline preesistente con soli due metadati root
isolati: l'originale continua a fallire sullo schema, senza filtri in produzione.

Il primo passo ha aggiunto una prova indipendente tratta dal binding stesso:
tabella fisica unica, titolo del ruolo, intestazioni e riga della persona.
Il valore deve essere nella colonna coerente con la proprietà. Una `A`
in un'altra colonna non prova la sezione o la provincia. Tutte le citazioni
originali del fatto devono restare riconducibili a record della persona:
una prova aggiuntiva corretta non cancella la citazione di un'altra persona.
Identificatori personali o professionali in conflitto mantengono il rifiuto.

Primo replay intermedio: **B0 38→42, quattro recuperi conformi al gold;
INDEX 23→23**. Recuperati soltanto qualifica, albo, sezione e numero di
iscrizione del socio Elisa. Zero nuove proposte non conformi, nessuna grounded
persa. Nessun collegamento di identità o trasformazione di valore in questo passo.

## Titoli e date: confronto del valore nel record che attesta il ruolo

I titoli abbreviati vengono normalizzati solo nel confronto del nominativo
con la cella nominativa della riga del binding. Nome completo, spazi canonici
e Unicode devono concordare: nessuna distanza testuale, iniziale espansa o
correzione del cognome. Il titolo non dimostra una qualifica, una carica o
un potere. Non crea un'identità condivisa per trasferire altri attributi.

Le date vengono confrontate come date calendariali valide, nei formati
giorno/mese/anno a quattro cifre, ISO e giorno/mese italiano in lettere/anno.
Nessuna interpretazione americana, anno abbreviato o data impossibile.
Questa equivalenza riguarda soltanto la proprietà data di iscrizione e la
sua colonna, non numeri professionali o testo arbitrario.

In entrambi i casi il fatto mantiene il valore e la citazione originali;
l'audit conserva anche il valore della cella e il tipo di confronto.
Il documento non viene riscritto né il valore sostituito da una normalizzazione.

## Collegamento d'identità limitato e verificabile

Il percorso aggiuntivo collega un record personale con ruolo esplicito a
una riga tabellare che documenta il valore. Richiede:

- nome completo concordante, con la sola normalizzazione sintattica dei titoli;
- CF personale condiviso di formato completo, oppure ordine professionale
  e numero di iscrizione condivisi, copiati da attributi esplicitamente etichettati;
- nessun identificatore discordante nei record strutturati disponibili per
  quel nome e nessuna assegnazione dello stesso identificatore a un altro nome;
- citazioni effettive di ogni record usato per il ruolo, le chiavi d'identità
  e il valore, conservando anche quelle originali del modello.

Il collegamento è limitato al **CF personale** e alla **provincia della stessa
iscrizione professionale**. Per la provincia, il solo CF non basta: devono
concordare anche ordine e numero. Non trasferisce qualifiche, cariche, poteri
di firma, designazioni o generici attributi aziendali.

Le tabelle complete, i record con intestazione persona–ruolo e le righe
nominative sono riconosciuti con strutture limitate; le chiavi del percorso
di identità provengono da colonne o attributi etichettati. Colonne sinonime
con valori discordanti, record omonimi, chiavi in conflitto e una seconda
persona annidata nel record impediscono il collegamento. Non è un motore
generale di risoluzione dell'identità in prosa libera.

Assenza di un dato in una vecchia scheda e diniego del ruolo restano distinti.
Il lettore riconosce righe intere di attributi «non disponibili/documentati»
e la forma grammaticale limitata di una nota «Il ruolo … non equivale a …».
La nota non concede alcuna designazione; altre negazioni o revoche restano
bloccanti, anche nella stessa frase. Non vengono eliminate dalle citazioni.

Le prove aggiunte rispettano il limite esistente di 800 caratteri per quote:
un record lungo viene citato per righe reali, senza tagli semantici. Se una
prova strutturale necessaria non è rappresentabile, il campo resta da verificare;
nessuna eccezione non gestita o perdita silenziosa della prova d'identità.

## Identità, ruolo, valore e applicabilità

Le SOURCE della Company KB e quelle del progetto autorizzato usano gli stessi
controlli; la General KB resta esclusa. Scope, progetto e ruolo del documento
continuano a essere validati prima del verificatore dei binding.

I nuovi riscontri SOURCE mantengono tre sezioni nell'audit del binding:
`identity_support`, `role_support`, `value_support`. Il primo distingue
prova diretta nella riga da collegamento con chiave personale/professionale;
nel collegamento riporta solo gli identificatori realmente condivisi come
chiave e conserva separatamente gli attributi dei due record.

L'applicabilità resta in `condition_checks` del campo. Nessun recupero SOURCE
risolve una condizione, sceglie il firmatario o attiva un ramo FORM. La
correzione è soltanto V12: nessun aggiornamento di sessioni storiche, scelta
USER introdotta, migrazione o modifica della KB.

## Verifiche sperimentali

Test scritti prima dei rispettivi passi. Log conservati, comprese le prove
fallite durante lo sviluppo:

- primo red: quattro recuperi attesi falliti e sei negativi passati;
- secondo red: sette positivi attesi falliti e 36 casi già passati;
- controesempi aggiunti: provincia con solo CF, attributi mancanti con nota
  sul ruolo, colonne sinonime discordanti, chiavi di una seconda persona
  dentro il record, identificatori personali discordanti anche nel percorso
  diretto, limite delle citazioni e conservazione della prova d'identità;
- prima Ruff con tre righe troppo lunghe, corrette senza cambiamenti di logica;
- prima suite completa interrotta volontariamente prima del termine per
  aggiungere gli ultimi due controlli sulle citazioni; non è una suite passata.
- ultimi negativi sulle chiavi discordanti nelle righe nominative e due
  prove positive su SOURCE del progetto, seguite dal rifiuto della stessa
  fonte assegnata a un progetto estraneo; rispettivi red conservati.

Finali: **57 nuovi casi, 274 mirati passati in 18,92 s, 2.431 backend passati
in 219,46 s; Ruff passato**. Una suite intermedia, prima degli ultimi quattro
casi, aveva passato 2.427 test in 217,18 s. I test software usano fixture
sintetiche e non misurano la qualità di nuove generazioni. Il frontend non
è stato modificato o ritestato.

## Replay finale e limiti della misura

| Output fisso | Grounded prima | Dopo il primo passo | Grounded finali | Recuperi finali rispetto a prima | Recuperi conformi al gold | Rifiuti residui |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B0-03 | 38 | 42 | 47 | 9 | 9 | 3 |
| INDEX-01, copia root isolata | 23 | 23 | 25 | 2 | 2 | 2 |

Recuperate **11 occorrenze su 10 destinazioni distinte**, tutte conformi al
gold congelato: prima le quattro prove esatte e poi gli altri sette casi.
Nessuna grounded precedente persa e nessuna nuova grounded non conforme al
gold. Anche sull'intero insieme delle proposte grounded dei due replay finali
il confronto non rileva valori non conformi.

| Causa della precedente esclusione | Recuperi | Campo e confronto/prova usata |
| --- | ---: | --- |
| Valore esatto già nella riga del binding | 4 | B0 `p45.s1` Ingegnere, `p45.s3` ordine, `p45.s4` A, `p46.s2` 8421; colonne della riga di Elisa in SOURCE `-54` |
| Titolo nel nominativo | 3 | B0 `p43.s0` Ing. Luca Ferri, `p45.s0` Ing. Elisa Romano, `p47.s0` Arch. Andrea Greco; confronto nominativo con la rispettiva riga soci `-54`, senza unione di attributi fra persone |
| Rappresentazione della data | 1 | B0 `p46.s1`, `18 maggio 2015` dalla frase di Elisa `-55` e `18/05/2015` nella sua riga soci `-54` |
| Identità tra record con ruoli diversi | 3 | B0 e INDEX `p52.s1` CF, INDEX `p53.s2` provincia albo; nome completo, Ordine degli Ingegneri di Bari e numero 8421 concordano fra record del direttore `-45` e riga `-54` |

Otto recuperi usano `binding_source_record` (quattro esatti, tre nominativi,
una data); tre usano `verified_person_records`. Per questi ultimi la chiave
condivisa è **ordine+numero**, non il CF: il CF è documentato nella riga
dei soci e non viene inventato nel record del direttore. Nome e titoli sono
confrontati esattamente con le sole equivalenze sintattiche descritte.

Restano **cinque rifiuti necessari**, mantenuti senza cambiare il contratto:

| Output e campo | Motivo mantenuto |
| --- | --- |
| B0 `p41.s1` e INDEX `p41.s1` | Indirizzo completo incompatibile con la richiesta fisica del Comune. Nessuna estrazione automatica della città |
| B0 `p46.s0` e `p53.s2` | Un fatto, due destinazioni: `Bari (BA)` non è nella citazione scelta per Elisa. Il fatto SOURCE rimane rifiutato, anche se un'altra riga disponibile contiene il dato |
| INDEX `p15.s0` | Il solo marker citato non documenta la richiesta del campo FORM |

La provincia INDEX recuperata cita la riga corretta di Elisa in `-54`;
le due destinazioni B0 rifiutate citano invece la frase `-55` che non contiene
il valore completo. Sono esiti diversi giustificati da prove diverse.

**Applicabilità invariata:** tutti gli undici recuperi sono ancora
`conditional`/`REVIEW_REQUIRED`, con condizioni `unknown`, valori non
selezionati, `RESOLVED=0` e `writes=0`. I fatti e le condizioni sono identici
agli audit precedenti; gli input, le risposte, le fonti e il gold sono congelati.
Zero nuove chiamate provider, USER o DOCX esportati. Non è una misura di
undici campi già scritti nel Word.

Gli zero falsi positivi osservati riguardano i recuperi confrontati col gold
e i test negativi finali. Non sono una certificazione generale dell'identità
o dell'affidabilità su nuovi output. Le accettazioni indebite intercettate
nei controesempi intermedi sono nei log red e risultano respinte dal codice
finale. Formati non riconosciuti, omonimie e conflitti restano conservativamente
da verificare; non è stato costruito un grafo generale di persone o cariche.

## Artefatti, integrità e arresto

[Misure e tracciati dei recuperi/rifiuti](benchmarks/2026-10-17-binding-final.json),
[controlli](benchmarks/2026-10-17-binding-final-checks.json),
[backup del raw](benchmarks/2026-10-17-binding-final-audit.tar.gz).
Il raw include input, risposte fisse, audit prima/primo passo/finali, confronti,
log dei test inclusi fallimenti, codice prima/primo passo/dopo, patch e script
di replay con rete/provider bloccati. Nessuna credenziale acquisita.
Per riprodurre gli script servono il repository e la fixture congelata,
oltre agli artefatti INDEX originali nel
[bundle precedente](benchmarks/2026-10-17-e1-index-audit.tar.gz). Le correzioni
antecedenti del Comune e del contesto sono conservate nel
[bundle field-context](benchmarks/2026-10-17-field-context-audit.tar.gz);
gli snapshot prima/dopo distinguono le modifiche di questo intervento.

11.021 dei 11.023 file protetti sono invariati: differiscono soltanto i due
file del verificatore autorizzati; nuovo file di test separato. In
`compilation_global.py` la sola funzione preesistente modificata è
`_binding_check`, altre trenta funzioni identiche nell'AST. Parser FORM,
validatori dei valori/fatti, schema globale, API, writer, modello/thinking,
fixture e artefatti precedenti preservati. La modifica SOURCE è solo nei
percorsi aggiuntivi V12. Nessuna migrazione o rianalisi di sessioni live.

**Arresto dopo il replay e la registrazione del rapporto.** Nessun altro
esperimento, intervento sull'applicabilità, commit o push avviato. B0 resta
il riferimento; compattazione FORM e cambi del contratto coverage restano fermi.
