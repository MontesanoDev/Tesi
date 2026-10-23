# Due residui V12: applicabilità del direttore e checkbox societaria

19 ottobre 2026. Base conservata: V12 SOURCE52 del 18 ottobre. Intervento
limitato ai due blocchi richiesti, senza nuove proposte globali, decisioni USER
inventate, modifiche FORM B0, writer o framework. Nessun commit/push.

**Replay offline: 52 → 60 campi di testo e una checkbox, totale 61 scritture.
Chat reale isolata: 52 campi di testo e una checkbox, totale 53.** Tutti i 52
valori precedenti sono identici in entrambi. Gli otto dati tecnici superano
l'applicabilità nel backend, ma il narratore li sospende nella nuova chat.
Questo limite end-to-end resta aperto; il replay non è presentato come risultato UI.

- [DOCX del replay, 61 scritture](../nuovi%20dati/domanda-iscrizione.V12-RAMI-REPLAY-61-20261019.docx)
  e [PDF](../nuovi%20dati/domanda-iscrizione.V12-RAMI-REPLAY-61-20261019.pdf).
- [DOCX effettivo della chat, 53 scritture](../nuovi%20dati/domanda-iscrizione.V12-RAMI-CHAT-53-20261019.docx)
  e [PDF](../nuovi%20dati/domanda-iscrizione.V12-RAMI-CHAT-53-20261019.pdf).
- [Misure](benchmarks/2026-10-19-v12-branches.json),
  [otto tracciati](benchmarks/2026-10-19-v12-branches-trace.json),
  [controlli](benchmarks/2026-10-19-v12-branches-checks.json).

## Risultato fisico, non soltanto stato dei validatori

| Misura | V12 SOURCE52 | Replay corretto | Nuova chat |
|---|---:|---:|---:|
| Proposte SOURCE grounded | 60 | 60 | 60 dopo la scelta USER |
| Testi SOURCE scritti | 51 | 59 | 52 |
| Testi USER scritti | 1 | 1 | 0 |
| Totale testi scritti | 52 | 60 | 52 |
| Checkbox USER selezionate | 0 | 1 | 1 |
| Scritture complessive | 52 | 61 | 53 |
| Otto dati tecnici ancora UNKNOWN dopo le ricevute | 8 | 0 | 0 |
| Otto dati tecnici sospesi dal narratore | — | 0, narratore simulato | 8 |
| Testi precedenti persi/cambiati | — | 0 | 0 |
| Altre checkbox modificate | 0 | 0 | 0 |
| Pagine nel medesimo LibreOffice | 9 | 9 | 9 |

Nel replay resta la ricevuta storica «Ingegnere» per un socio: la provenienza
non è riscritta retroattivamente. Nella nuova chat quella domanda non serve e
il medesimo valore proviene dalla SOURCE. Non sono stati copiati nello stato
nuovo né quella ricevuta né risposte a domande non poste.

## Perché UNKNOWN era un limite del verificatore

Il FORM, paragrafo 50, dice letteralmente:

> la quale ha come Responsabile della Progettazione (per le società di professionisti) o Direttore Tecnico (per le società di ingegneria):

Il modello proponeva `c_dt`, `operator=semantic`, con un fatto di aspetto
`legal_type` e uno `professional`. Il vecchio controllo li confrontava come
se dovessero avere la stessa dimensione: «Condizione e fatti su dimensioni
differenti». Conservava correttamente UNKNOWN, senza valutare quella
congiunzione. Tutti gli otto valori avevano già un binding SOURCE valido.

Le prove disponibili sono sufficienti per una verifica molto più circoscritta:

1. **Scelta della pratica USER:** ricevuta positiva già accettata su `c_societa`:
   «Mapi Ingegneria S.r.l. partecipa soltanto come società di ingegneria».
   La condizione è ancorata all'intera opzione FORM e copre il blocco tecnico.
2. **Ramo del FORM:** la frase selezionata coincide letteralmente con
   «società di ingegneria» nella parentesi che qualifica «Direttore Tecnico».
   Non si assume che confermare tutta `c_societa` equivalga a confermare `c_dt`.
3. **Ruolo aziendale SOURCE:** nel chunk `-55`, stesso input congelato:
   «Elisa Romano: direttore tecnico di Mapi Ingegneria S.r.l.; …».
   Nome, ruolo e azienda sono nella stessa asserzione positiva. I binding
   esistenti attestano i dati della medesima persona e iscrizione professionale.
4. **Operatore:** la denominazione SOURCE già grounded nel blocco confermato
   identifica la stessa azienda. Un altro operatore o un'altra persona non passa.

La natura giuridica documentata (S.r.l.) resta distinta dalla categoria della
pratica scelta dall'utente. Non si deduce la partecipazione dalla forma giuridica,
né il firmatario o suoi poteri dalla presenza di un direttore. Un ruolo aziendale
non diventa una designazione per progettazione, sicurezza, collaudo o integrazione.

La ricevuta su `c_dt` resta **SKIP**, con la frase «non fornisco una conferma
aggiuntiva sul ruolo del direttore tecnico». Non viene trasformata in consenso,
attestazione o nuova decisione. La prova della condizione composta è registrata
separatamente in `branch_evidence`: FORM, decisione pertinente e ruolo SOURCE.
Un diniego esplicito o richiesta di lasciare il campo bianco resta bloccante.

La regola riconosce soltanto questa grammatica esplicita di alternative
`ruolo (per le …) o ruolo (per le …)`, con corrispondenze letterali verificate.
Sintassi non supportata, nomi diversi, attribuzioni mancanti, riserve, negazioni,
conflitti o decisioni non equivalenti mantengono UNKNOWN. Non è un valutatore
semantico generale né una promozione di qualsiasi `operator=semantic`.

## Checkbox: stesso consenso, un collegamento verificato

L'output originale non propone gruppi né assegnazioni checkbox. La ricevuta
su `c_societa` corrisponde però all'intera opzione del controllo nativo `p39.cb0`,
incluso nello scope. Non serve una nuova decisione societaria.

Il backend ricostruisce la lista completa sotto l'intestazione letterale
«IN QUALITÀ DI», fino alla successiva intestazione reale. Include i sette
controlli e le etichette originali, anche attraverso i paragrafi con dati
anagrafici. Campi in maiuscolo, come «C.F.», non sono titoli di chiusura.
Liste ambigue, etichette parziali, più controlli nello stesso paragrafo,
attraversamenti di sezioni o caselle già selezionate in conflitto non passano.
Il gruppo ricostruito attraversa il validatore FORM esistente.

**La cardinalità resta `unknown`.** Non si dichiara `multiple` per aggirare il
controllo di esclusività e non si inventa una lista di una sola opzione.
È consentita una sola operazione conservativa: applicare il valore positivo
alla casella corrispondente alla ricevuta USER accettata. Non vengono dedotte
scelte negative, cancellate alternative o selezionate altre condizioni.

La ricevuta originale resta `CONDITION_TRUE`; nessuna falsa risposta `choice`
viene aggiunta alla conversazione. Il collegamento conserva chiave della
ricevuta, testo USER e gruppo. Prima dell'export si rivalutano ricezione,
provenienza, corrispondenza FORM e destinazione. Una semplice proprietà
`receipt_key` su un valore arbitrario non autorizza l'operazione. Restano
invariati i controlli SOURCE e le regole delle normali scelte single/multiple.

## Replay offline e prova reale: differenza osservata

La baseline è riprodotta con il codice conservato all'inizio del lavoro,
soltanto nel processo: 52 scritture e identico hash. Il replay corretto usa
la stessa risposta globale, 56 SOURCE e tutte le ricevute storiche immutate.
Il narratore è simulato; grounding, rivalidazione, persistenza ed export reali.
Una finestra di otto proposte tecniche viene riesaminata. Risultato: gli otto
testi scritti e la sola checkbox societaria selezionata.

Segue **una sola nuova sessione UI isolata**, senza modificare gli stati originali:
`133483f76343416082b954f6f7bfd777`, conversazione `conv-a813341763334b44`.
FORM, SOURCE e schema coincidono con quelli dell'input salvato. Viene riusata
la risposta globale, mentre router, guard e narratore chiamano il provider reale.
È una prova del percorso di chat, non una nuova valutazione della risposta globale.

Nella UI:

1. Nuova richiesta del benchmark, nessuna ricevuta storica inserita nello stato.
2. Domande effettive su società, direttore e luogo/data. Si riutilizza il testo
   storico per confermare società/firmatario e rinviare il secondo punto.
   Luogo/data non risposti. Nessuna attestazione o preferenza somministrata.
3. Backend: `c_dt=true`, tutte le 60 proposte grounded, 60 revisionate.
   Il narratore restituisce però gli otto slot tecnici in `held_proposal_slots`.
   Le sospensioni vengono rispettate; non sono cancellate o ignorate.
4. Richiesta esplicita di bozza parziale, download e ricaricamento. DOCX reale:
   52 testi più una checkbox; gli otto dati tecnici restano vuoti.

**Fatto:** il collo di bottiglia della chat è ora la sospensione MODEL, non
UNKNOWN, binding SOURCE o writer. **Non osservabile con questo schema:** il
motivo preciso della sospensione; `ContinuationPlan` non restituisce una ragione
per ciascun hold. Il contesto contiene il rinvio USER e la prova del ruolo,
ma non il nuovo oggetto `branch_evidence` con la congiunzione completa.
L'interpretazione del rinvio come richiesta di non compilare, o la mancanza di
quel contesto esplicito, sono ipotesi. Non presentiamo questi otto hold come
rifiuti SOURCE necessari o assenza di dati. Nessun nuovo tentativo per ottenere
un risultato migliore e nessuna modifica ulteriore al narratore in questa fase.

## Verifiche, rifiuti necessari e limiti

34 casi generici, di cui 31 negativi: assenza/negazione della decisione, tipo
diverso, citazione narrativa o parziale, scope errato, persona/azienda/ruolo
diverso, ruolo negato/ipotetico, SOURCE generale, binding/fatto respinto,
conflitto, diniego diretto, gruppo ambiguo, casella concorrente già spuntata,
ricevuta modificata e falso `receipt_key`. Nessuna accettazione indebita osservata.

**243 test mirati passati in 32,75s; suite completa 2601 passati in 185,70s;
Ruff passato.** I primi test avevano errori di preparazione (discriminatore,
aspect, formato SOURCE e mutazione che non cambiava la stringa): conservati,
non conteggiati come riproduzioni valide dei difetti. La chiusura errata della
lista sul campo CF è stata riprodotta e corretta nel test generico. Anche i
fallimenti dei comandi di snapshot/collezione e il limite dell'osservatore sono
documentati negli artefatti, senza scartarli.

Due ultimi negativi riproducono un veto incompleto: «lascia il campo vuoto»
veniva distinto male dal rinvio della sola conferma. Prima 2 fail, poi veto
letterale esteso a «vuoto» e test passati. Nessuna modifica ai casi già provati:
verifica indipendente finale con gli stessi hash dei DOCX, senza altre chiamate
o un secondo tentativo UI. Codice prima del veto conservato separatamente.

XML, CRC, posizioni, prestampato e report controllati per tutti i documenti.
Quattro tabelle intatte; tredici controlli nativi, dodici lasciati invariati.
Nessuna deselezione derivata. Gli otto valori del replay coincidono con il GOLD;
resta la sola differenza già nota sulla carica più completa del firmatario.
GOLD/scorer congelati usati solo dopo export: 59/60 testi conformi nel replay,
51/52 nella chat; checkbox societaria coerente con la decisione del caso.

Tutte le versioni hanno nove pagine nel medesimo LibreOffice. Controllata la
pagina 3 prima/dopo/reale e la firma a pagina 9: dati e spunta leggibili, nessuna
sovrapposizione osservata. Nel replay la minore lunghezza del blocco compilato
sposta in alto il seguito. Restano giunzioni prestampato/valore già note,
come «sezione Adella»: writer invariato. Non è una certificazione Microsoft Word.

Preferenze, attestazioni, esecutori, integrazione e luogo/data restano cinque
decisioni distinte e aperte; niente nuove dichiarazioni, designazioni o firma.
Questi vuoti non sono errori da colmare con la SOURCE aziendale. I quattro
testi USER attesi dal GOLD rimangono vuoti anche nel replay completo dei dati.

## Chiamate, conservazione e punto di arresto

Offline: zero chiamate LLM. Chat: **zero nuove globali**, una risposta globale
riusata, sette chiamate reali (tre router, tre sintesi, un guard), **61.977 token**.
Nessun retry di qualità. Prezzi non verificati, costo USD non stimato.
HTTP delle sintesi e tracce dei router successivi conservati; il trasporto
completo del primo router e del guard non è acquisito. I loro totali sono
inclusi dalla telemetria delle risposte. L'osservatore iniziale non intercettava
l'alias usato da generation: corretto nel solo harness prima dell'export,
riavviando il server isolato allo stesso checkpoint; nessuna nuova sessione/proposta.
Dieci richieste GET annullate dalla UI al montaggio/ricaricamento, zero errori
HTTP nelle risposte acquisite e zero eccezioni pagina. Log conservati.

Raw: `backend/data/compilation-audit/v12-branches-20261019-01/`.
[Backup](benchmarks/2026-10-19-v12-branches-audit.tar.gz),
[checksum](benchmarks/2026-10-19-v12-branches-audit.tar.gz.sha256),
[descrittore](benchmarks/2026-10-19-v12-branches-archive.json).
Codice prima/dopo, input/output, ricevute, audit, test, conversazione, video,
trace e DOCX/PDF inclusi; DB/chiavi privati esclusi. `verify_bundle.py`
ricostruisce entrambi gli audit e i DOCX senza database o provider.
29 sessioni e 285 file originali uploads/knowledge immutati; FORM, fonti,
GOLD, modello, prompt/schema globale, API, database e writer invariati.
Nessuna migrazione o aggiornamento implicito delle sessioni storiche.

Arresto dopo confronto e rapporto. La sospensione degli otto valori da parte
del narratore resta esplicitamente da affrontare separatamente; non avviare
nuove chiamate, sessioni o cambiamenti architetturali automaticamente.
