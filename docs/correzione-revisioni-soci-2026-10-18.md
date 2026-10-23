# Revisioni conservate e citazioni dei soci: correzione V12

18 ottobre 2026. Implementati i primi due interventi autorizzati e verificato
l'export reale dalla UI. FORM B0, modello, thinking, API del provider, schema
globale di risposta, validatori SOURCE e writer invariati. Nessun commit/push.
E1 non avviato. Le domande mancanti della pratica restano una fase separata.

**Nel nuovo DOCX ci sono tutti i 24 campi dei soci, ma uno richiede ancora una
scelta USER: 23 SOURCE + 1 USER.** Il chiarimento riguarda «Ingegnere» contro
«ingegnere», che il verificatore delle alternative tratta come valori distinti.
Non ho trasformato quella proposta in grounded né modificato il controllo per
raggiungere il numero atteso. I due replay controllati, invece, portano tutti
24 i campi dei soci nel DOCX con provenienza SOURCE.

[Word reale](<../nuovi dati/domanda-iscrizione.V12-SOCI-24-20261018.docx>),
[PDF](<../nuovi dati/domanda-iscrizione.V12-SOCI-24-20261018.pdf>),
[report](<../nuovi dati/domanda-iscrizione.V12-SOCI-24-20261018.report.json>),
[conversazione](<../nuovi dati/domanda-iscrizione.V12-SOCI-24-20261018.conversazione.md>).
[Misure](benchmarks/2026-10-18-v12-review-soci.json),
[traccia delle 24 assegnazioni](benchmarks/2026-10-18-v12-review-soci-trace.json),
[controlli](benchmarks/2026-10-18-v12-review-soci-checks.json),
[backup](benchmarks/2026-10-18-v12-review-soci-audit.tar.gz),
[descrittore](benchmarks/2026-10-18-v12-review-soci-archive.json).

## 1. Modifiche applicate

### Conservazione delle revisioni

`compilation_global_dialogue.py` conserva una ricevuta con impronta SHA256 della
proposta esaminata: valore, soggetto e fatto, binding e prove, richiesta/destinazione
FORM, condizioni e fatti da cui dipendono, gruppo checkbox quando pertinente.
Le impronte sono metadati del dialogo persistito, non vengono inviate all'LLM.
Nessun database nuovo, colonna o migrazione.

La ricevuta resta valida soltanto per la stessa proposta. L'ordine del catalogo
non entra nell'identità della revisione: inserire prima le otto generalità del
firmatario non cancella i soci. Se cambiano valore, soggetto, prova, ruolo,
richiesta o definizione della condizione, occorre un nuovo esame. Le ricevute
USER di applicabilità rimangono un gate separato: confermare una condizione già
presente non richiede di ricontrollare inutilmente tutte le SOURCE immutate.
Una condizione falsa o non confermata continua a impedire la scrittura.

Ogni chiamata del narratore considera al massimo **40 proposte nuove o cambiate**.
Se ne rimangono altre, usa lo stato PENDING e l'avanzamento UI già esistente;
le domande vengono esposte al termine del controllo delle proposte. Ogni passo
riuscito aggiunge ricevute, quindi il percorso è finito sul catalogo immutabile:
nessun ciclo di generazione per campi e nessuna seconda analisi globale.
Un errore ferma l'avanzamento e l'export, conservando gli esiti precedenti.
Le proposte trattenute restano escluse: una nuova sintesi non elimina da sola
un hold già registrato.

`compilation_global_sessions.py` filtra le revisioni anche quando costruisce la
sessione pubblica. È necessario perché il payload pubblico non contiene l'audit
completo: una modifica del soggetto deve invalidare la revisione anche se valore
e testo del campo pubblico non cambiano. Il controllo SOURCE al momento
_dell'export_ resta invariato e viene eseguito nuovamente.

La correzione riguarda V12. Sessioni di contratti precedenti non ricevono nuovi
metadati; le V12 storiche senza impronte restano leggibili secondo le regole
precedenti. Se si richiede esplicitamente una nuova sintesi, le proposte prive
di ricevuta verificabile vengono riesaminate. Nessun aggiornamento implicito
delle sessioni originali e nessuna promozione a RESOLVED.

### Formato delle citazioni SOURCE

Cambiato soltanto il paragrafo pertinente del system prompt in
`compilation_global.py`: per le tabelle richiede due evidence separate,
**titolo e riga completa del soggetto**, ciascuna un estratto letterale continuo
della stessa tabella. Intestazioni e appartenenza della riga vengono verificate
nella SOURCE dal backend esistente. Il prompt vieta di costruire una quote
incollando titolo/intestazione a una riga successiva saltando le precedenti.
Ricorda il massimo di due evidence previsto dal binding.

Non c'è una riparazione automatica delle quote inventate e non sono state
ammorbidite le verifiche di soggetto, ruolo, valore, citazione o applicabilità.
Il confronto AST fra preimmagine e codice finale conferma identiche tutte le
funzioni e classi dei validatori in `compilation_global.py`: cambia il testo
delle istruzioni, non il gate. Nessun hardcoding di persone, società o ID.

## 2. Verifiche controllate offline

Solo il trasporto del narratore è simulato. Persistenza, validatori, ricevute
USER della rispettiva sessione, selezione e writer sono reali, in copie isolate.
Rete/provider vietati nei replay. Tutti i DOCX sono letti fisicamente nell'XML.

| Prova | Prima | Dopo | Recupero e limiti |
|---|---:|---:|---|
| Output storico con 16 soci scritti | 41 scritture: 40 SOURCE + nome USER | 54: 53 SOURCE + nome USER | +13 SOURCE: 8 soci Andrea già revisionati e 5 DT prima fuori finestra |
| Vecchio run UI, stesse prove e controlli | 27 SOURCE, 8 soci | 27 SOURCE, 8 soci | Baseline identica, anche SHA del DOCX |
| Stesso output, sole quote titolo+riga | 27 SOURCE, 8 soci | 43 SOURCE, 24 soci | +16 SOURCE corretti; nessun fatto/valore/condizione modificato |

Nel primo replay le finestre contengono **40, 5, 0, 8** proposte. I primi due
passi revisionano le 45 originali; la conferma USER non le rimanda; la selezione
nominativa aggiunge solo le otto generalità. Tutte 53 le SOURCE grounded risultano
revisionate, nessuna persa. Sei proposte restano respinte: Bari/BA iniziali,
indirizzo completo nel Comune e tre legami del direttore non sostenuti dalle
citazioni proposte. Il gold rileva una differenza testuale sulla carica completa,
già attestata dalla fonte: 53/54 valori conformi stretti, non un nuovo falso fatto.

Nel secondo confronto, dopo il replay di baseline, la modifica delle citazioni
fa riesaminare i 24 binding dei soci, non gli altri 19 valori immutati. L'export
da 43 valori contiene tutti 24 i soci SOURCE, tutti conformi al gold. I restanti
17 campi SOURCE non grounded restano esclusi. Zero nuovi valori indebiti
osservati e nessun rilassamento delle condizioni.

Questi replay dimostrano le cause e le correzioni sui rispettivi output congelati;
non sono altre esecuzioni reali del modello e non sono misure della sua stabilità.

## 3. Nuova prova reale dalla UI

Copia isolata di DB, storage e Company KB; Chromium usa UI React e API vere,
nessun mock o sostituzione di risposte. Una sola globale, nessun retry qualitativo.
Il trasporto osservato inoltra ogni richiesta originale invariata e conserva
request/schema, wire request, risposta HTTP e usage di tutte le chiamate;
nessun header o credenziale salvato. Il wrapper è solo nel harness locale,
non nel codice applicativo o nell'istanza normale.

Sessione `19be5edcf19e49acb2e25a7dab370000`, conversazione
`conv-090ab2720d6340a2`, export `09ffd84febfb48d6a8b64f00bb8d1656`.
Il JSON globale di input è **interamente identico** alla precedente prova UI:
stesso T0 Minervino V1, 56 SOURCE, FORM, schema e reading plan. Uguali modello,
thinking, temperature e max_tokens. La sola differenza nella richiesta globale
è il paragrafo del system prompt sulle citazioni; il dialogo successivo cambia
per effetto della nuova risposta e delle nuove revisioni. Un campione per
variante non dimostra una differenza statistica o stabilità futura.

### Stadi misurati

| Misura | Precedente UI reale | Nuova UI reale |
|---|---:|---:|
| Fatti / assegnazioni MODEL | 46 / 60 | 55 / 60 |
| Assegnazioni grounded | 27 | 44 |
| SOURCE revisionate | 27 | 44 |
| Soci: valori proposti conformi al gold | 24 | 24 |
| Soci: binding verificati | 8 | 24 |
| Soci: assegnazioni SOURCE grounded | 8 | 23 |
| Soci: scritti | 8 SOURCE | 23 SOURCE + 1 USER |
| SOURCE scritte complessive | 27 | 41 |
| USER scritti | 0 | 1 |
| Totale scritture | 27 | 42 |
| Grounded escluse per UNKNOWN/rinvio | 0 | 3 |
| Grounded non revisionate / held finali | 0 / 0 | 0 / 0 |
| Valori fisici scritti conformi al gold | 27/27 | 42/42 |
| Checkbox selezionate | 0 | 0 |

Il narratore visita **40, 4, 0, 0** proposte. Le ultime quattro non si perdono;
le risposte USER successive conservano tutte le 44 revisioni immutate.
I sedici campi di Elisa/Andrea prima rifiutati per quote non letterali ora hanno
binding verificati. La qualifica di Elisa presenta però due fatti SOURCE,
`Ingegnere` nella tabella dei soci e `ingegnere` nel record del direttore:
la rilevazione di alternative, ancora sensibile al case, impedisce la proposta
SOURCE scrivibile per quel campo. È un problema distinto dalle citazioni.

### Chiarimenti realmente forniti

1. Il sistema chiede partecipazione come società di ingegneria e conferma del
   ruolo del direttore. Si ripete la decisione T0 sulla società e sul firmatario;
   si rinvia **solo il secondo punto**, senza inventare una nuova attestazione
   o nomina. Ricevute: c_societa TRUE; c_dt SKIP. Le tre proposte DT grounded
   rimangono UNKNOWN/rinviate ed escluse, senza perdere le revisioni.
2. Soltanto dopo la conferma societaria viene chiesta la qualifica professionale.
   Si risponde «Indica Ingegnere per Elisa Romano, come riportato nella tabella
   dei soci». È una scelta fra forme già documentate, non una qualifica inventata.
   Router e guard USER reali la associano al solo p45.s1. La ricevuta e la scrittura
   restano USER; fatti, quote e binding SOURCE originali rimangono nell'audit.
3. Il sistema chiede il consenso all'export; si invia il T2 congelato e si scarica
   il DOCX dalla UI. Il documento viene poi riletto anche dopo il refresh.

I chiarimenti aggiuntivi sono registrati, come previsto dal protocollo, e non
sono confusi con le quattro risposte del copione. Non sono state somministrate
preferenze, designazioni, attestazioni o luogo/data perché mai richieste.
Il T1 completo non è raggiunto. Il risultato **non** dimostra 24 compilazioni
SOURCE autonome: prima della scelta sulla qualifica ne erano scrivibili 23.
Non ho modificato il comparatore delle alternative per trasformare 23 in 24.

Rispetto al precedente Word reale: sedici destinazioni nuove dei soci, una
persa (CF del direttore: nuova quote FORM inesatta), nessun valore cambiato
nelle 26 destinazioni comuni. Il guadagno netto di 15 scritture non è una
misura isolata del solo prompt: varia anche la risposta del modello e interviene
un chiarimento USER supplementare. Il replay a output fisso isola invece
l'effetto deterministico di ciascuna correzione.

## 4. Controllo DOCX e limiti residui

SHA256 originale `25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c`;
nuovo download `4a29f7d306a6664b88208f8ba88bff5738123310a84853ff4e770f69dae126c8`.
Download UI e download diretto dello stesso export identici.
CRC e tutte le parti XML/rels validi; cambia solo `word/document.xml`.
Tutte 42 le scritture coincidono con report e posizioni fisiche. Quattro tabelle,
13 controlli e tutti 123 i testi da lasciare vuoti sono conservati; nessuna firma,
spunta o designazione è stata inventata.

GOLD V1 invariato: dei 60 target fattuali, 41 scritti SOURCE e uno tramite
scelta USER, 18 ancora vuoti. Questi vuoti sono **9 generalità/carica del
firmatario, Comune iniziale e 8 campi DT**. Restano distinti dai quattro testi
USER e dalle sei preferenze mai ricevuti. Zero valori errati osservati nelle
42 scritture; non è accuratezza generale della KB o del documento completo.

Nel nuovo output restano 16 proposte non grounded:

- 9 per binding FORM del firmatario: dati presenti ma ruolo FORM non attestato
  dalla quote scelta; il riuso richiede un VALUE nominativo che qui non esiste;
- 1 per marker-only del Comune iniziale; BA iniziale e Bari/BA societari passano;
- 2 alternative soltanto tipografiche sulla qualifica di Elisa, in due campi;
  una è stata scelta dall'utente, quella DT resta condizionata;
- 1 CF DT con quote FORM inesatta; 3 dati DT con collegamento SOURCE non ammesso.

Le tre SOURCE DT grounded sono revisionate ma non scritte per c_dt rinviata:
nessuna accettazione automatica UNKNOWN→TRUE. Il ruolo aziendale documentato
non diventa una nomina o una decisione USER aggiuntiva. La checkbox societaria
resta vuota perché il modello non produce un gruppo validabile; non è un dato
mancante nella KB o una perdita nel writer.

Rendering LibreOffice: **9 pagine**, contro 10 del precedente run reale.
Viste pagine 1, 3 e 9: tre soci completi nel blocco corretto, direttore vuoto,
firma vuota insieme al contenuto finale. Il miglioramento di impaginazione
segue i valori inseriti; nessuna modifica al writer. Rimangono giunzioni del
prestampato, ad esempio «professionaleOrdine». Non è una certificazione Word;
warning liblangtag del renderer conservato nel raw.

## 5. Tempi e costo: copertura migliore, nessuna accelerazione dimostrata

| Misura | Precedente run | Nuovo run |
|---|---:|---:|
| Chiamate globali | 1 | 1 |
| Chiamate totali | 7 | 11: 1 globale, 4 narratori, 4 router, 2 guard |
| Input globale | 76.616 | 76.700 |
| Output globale, reasoning incluso | 40.083 | 47.683 |
| Reasoning globale | 24.507 | 32.433 |
| Output globale escluso reasoning | 15.576 | 15.250 |
| Tempo globale applicativo | 142,10 s | 174,83 s |
| Somma POST UI sequenziali | 154,76 s | 194,96 s |
| Token totali del percorso | 153.384 | 181.776 |
| Costo stimato USD | 0,0390–0,0427 | 0,04563 |

La richiesta globale cresce di soli 84 token. L'aumento di tempo si accompagna
soprattutto a 7.926 token di reasoning in più; non attribuirlo al nuovo JSON
FORM, rimasto identico, né dedurre stabilità da un solo run. Il dialogo richiede
una chiamata breve per le quattro proposte oltre la prima finestra e un
chiarimento aggiuntivo, con relativo routing/guard/sintesi. Non promettere che
la compilazione sarà più veloce: ora la revisione non abbandona proposte valide.

Usage completo nuovo: **133.102 input + 48.674 output**, inclusi 32.433 reasoning;
24.064 input cache hit e 109.038 miss. Somma tempi provider 188,27 s.
Browser 512,84 s comprende ispezioni e attese dell'operatore, quindi non è
interamente latenza del sistema. Request, wire request e risposte di tutte
11 le chiamate sono acquisite, comprese quelle prima non osservate.

Stima, non addebito verificato, con prezzi Flash off-peak per milione:
0,003 USD hit, 0,15 miss, 0,60 output; prova domenicale.
[Tariffe ufficiali DeepSeek consultate il 18 ottobre](https://api-docs.deepseek.com/quick_start/pricing/).
Nessuna nuova chiamata per i replay o saldo account interrogato.

## 6. Test, regressioni e conservazione

Prima dell'implementazione: i nuovi test sulle revisioni danno **11 fallimenti e
2 passaggi**, riproducendo perdita, mancato avanzamento e riuso di revisioni
obsolete. Aggiunti poi negativi e compatibilità: 20 casi nuovi complessivi.

Verificati: inserzione di otto dati prima di quaranta revisionati; cambi di
soggetto, valore, prove/hash, ruolo, contesto e condizioni; indici hold locali
alla finestra; hold persistenti; UNKNOWN e FALSE non scrivibili; errore nella
finestra successiva conserva ricevute ma blocca export; sessioni precedenti
senza upgrade implicito; soggetto cambiato nell'audit nascosto al payload pubblico;
45 campi persistiti ed esportati su FTS5/Qdrant con una sola globale simulata.

Citazioni: titolo+riga della persona successiva accettati; concatenazione
inesistente respinta; valore di persona diversa respinto; quattro span respinti.
La suite di binding/identità/campi conserva i controlli precedenti.

La prima suite completa dà 2.477 passaggi e due fallimenti: un vecchio test,
nei due backend, pretendeva che la sintesi ripetesse le due proposte già
revisionate. Aggiornata soltanto quella aspettativa al comportamento autorizzato
(zero proposte da riesaminare, ricevute e prove persistite ancora presenti),
non rimossa la verifica delle SOURCE o dell'export. Test del modulo: 32 passati.
**Suite finale: 2.479 passati in 288,71 s; Ruff passato.**

Sono conservati anche errori di setup dei comandi/harness: import iniziale del
server, browser senza backend, path/sintassi di script diagnostici. Non avevano
avviato una globale; non sono retry qualitativi. Nel run reale completato ci
sono dieci GET annullate al mount/refresh, zero errori JS o POST fallite. Tutte
le risposte API completate sono 200.

Preimmagini di codice e diff completo prima dell'intervento nel raw:
`backend/data/compilation-audit/v12-review-soci-20261018-01/`.
Dei 205 file protetti cambiano solo i tre moduli previsti e due test esistenti;
si aggiunge il file di test delle revisioni. Preservati gli altri file e tutte
le modifiche locali dell'utente. Invariate 29 sessioni originali/versioni/stati
ed i 273 file storage originali. Le copie private sono fuori dal backup,
che conserva prompt, output, audit, conversazione, video/trace e risultati.

I server isolati sono arrestati. L'istanza ordinaria 8000/5173 resta attiva;
il backend usa reload sul codice corrente. Nessuna migrazione o reindicizzazione:
per una nuova valutazione usare una nuova conversazione, conservando gli audit
storici. Nessun commit/push.

## 7. Dialogo: fase separata, ancora da implementare

Il nuovo chiarimento sulla qualifica non risolve le domande mancanti della
pratica. Il pool termina senza preferenze, designazioni, attestazioni e luogo/data;
non è un limite di tre domande per turno. Le motivazioni coverage manual_input
non sono automaticamente slot interrogabili o decisioni USER.

Il prossimo intervento dovrebbe restare circoscritto a richieste FORM già
ancorate e validate, con quattro verifiche distinte:

1. preferenze: categorie/fasce, massimo previsto e alternative non selezionate;
2. designazioni: esecutori e integrazione specialistica scelti dall'utente,
   senza derivare incarichi dai ruoli societari;
3. attestazioni: conferma esplicita e separata, senza attribuire al FORM o a una
   carica la prova di dichiarazioni, consensi o disponibilità degli allegati;
4. luogo/data: domanda pertinente, firma e allegati fuori dall'export.

Prima test del pool e del percorso USER per ciascun caso; poi copione V1 dalla
UI, registrando domande mai poste, risposte ignorate e decisioni anticipate.
Nessuna promozione indistinta delle coverage, spunta da natura giuridica o
conferma del firmatario usata come consenso generale. Anche il falso conflitto
Ingegnere/ingegnere va trattato esplicitamente con test di equivalenza tipografica
limitata alla proprietà pertinente, senza normalizzare arbitrariamente ruoli,
identificativi o persone. Non è stato corretto in questa fase.

Il risultato consegnato è dunque un avanzamento verificato sulla conservazione
e sulle citazioni, con 24 soci presenti nel DOCX e provenienza trasparente;
non è una certificazione di completezza o di compilazione interamente autonoma.
