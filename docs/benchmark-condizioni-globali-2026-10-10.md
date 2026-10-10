# Condizioni esplicite: risultato del secondo esperimento

Il contratto condiviso e i controlli backend sono implementati e testati, ma
**non è dimostrato un miglioramento della compilazione reale**. Il prototipo
resta isolato: nessun RESOLVED persistito, nessun DOCX, nessuna modifica a V1,
RAG, chat, parser o renderer. I risultati negativi restano conservati.

## Cosa cambia

Una sola proposta contiene `facts` SOURCE riutilizzabili, `conditions` FORM e
`fields` che li referenziano. Il backend verifica citazioni, identità/scope,
copertura esatta e i confronti conservativi descritti nel
[contratto](proposta-globale-compilazione.md). Stesso soggetto e dimensione,
due proprietà distinte, valori identici: `same=true` / `different=false`.
Grafie diverse non dimostrano disuguaglianza. Condizioni semantiche/ambiti non
verificati restano unknown. Falsa o ignota impedisce il valore; NA richiede una
condizione locale calcolabile falsa. Non sono verdict semantici indipendenti:
tutte le assegnazioni restano `semantic_review_required=true`, non scrivibili.

Limiti: 128 fatti, 128 condizioni, 8 riferimenti per posizione, 400 candidate,
96 chunk/100.000 caratteri SOURCE, 350.000 caratteri input, 49.152 token output,
300 s. Nessun retry/reviewer aggiuntivo. Il vecchio contratto resta leggibile
per riprodurre gli audit, senza diventare un workflow operativo parallelo.

## Tre chiamate reali DeepSeek

Originale upload 153: SHA-256
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
307 posizioni, stesse 51 SOURCE documentali del precedente esperimento,
zero USER. I tre `input.json` sono identici byte per byte. Profilo locale
`prova`, alias `deepseek-flash`, temperature 0,1. Il codice era congelato prima
di ogni prova: `a29b6f2` nelle prime due, `e7d9e1a` nella terza; nessuna modifica
durante le chiamate. Nella terza cambia solo la modalità di ragionamento `low`,
già usata dalla mappa V1, attivabile con l'opzione sperimentale `--thinking`.

| Prova | Thinking | Input token | Output token | Totale | Secondi AI | Esito |
|---|---|---:|---:|---:|---:|---|
| Precedente globale 3 | off | 68.204 | 30.547 | 98.751 | 75,69 | 306 grounded, 1 rifiutata; difetti semantici noti |
| Condiviso 1 | off | 69.065 | 33.937 | 103.002 | 80,79 | 247 grounded, 60 rifiutate |
| Condiviso 2 | off | 69.065 | 30.397 | 99.462 | 76,01 | 202 grounded, 105 rifiutate |
| Condiviso 3 | low | 69.090 | 49.152 | 118.242 | 156,10 | `finish_reason=length`, tutto rifiutato |

Rispetto alla precedente proposta globale valida: token +4,30% / +0,72%,
tempo AI +6,74% / +0,43% nelle due prove senza ragionamento. Nessun risparmio
dimostrato. Sono pochi campioni, con qualità/output differenti: niente percentili
o stime di compilazione completa. La cache input è 0 / 68.864 / 0 token;
non dedurre costi monetari comparabili dal solo totale token.
Le tre chiamate nuove consumano complessivamente **320.706 token** e
312,90 s AI. Nessuna chiamata aggiuntiva per validare i campi.

## Cosa mostrano le due risposte complete

Entrambe restituiscono **zero condizioni e zero riferimenti a condizioni**.
La prima propone 9 fatti, la seconda 10, invece di una mappa dei vincoli del
modulo. Il nuovo schema consente il riuso, ma non garantisce che la fase
semantica sia stata eseguita. Una lista vuota non prova incondizionalità.

I cinque valori aziendali restano corretti e letteralmente grounded in entrambe:

| Candidate | Requisito | Valore proposto | SOURCE |
|---|---|---|---|
| `t0.r5.c1` | Operatore economico | Mapi Ingegneria S.r.l. | visura simulata, chunk -30/file -9 |
| `t0.r6.c1` | Forma giuridica | Societa a responsabilita limitata | stessa SOURCE |
| `t0.r7.c1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | stessa SOURCE |
| `t0.r9.c1` | Codice fiscale | IT01234567890 | stessa SOURCE, dato demo |
| `t0.r10.c1` | Partita IVA | IT01234567890 | stessa SOURCE, dato demo |

Sono **proposte**, non cinque nuovi RESOLVED. Il controllo non certifica la
validità legale/fiscale dei dati demo. Problemi annotati nel campione:

- Sede operativa: ancora proposta uguale a quella legale nonostante il vincolo
  «se diversa». Rifiutata perché la quote fonde paragraph:34 e paragraph:35,
  **non** perché il modello abbia fornito la condizione al gate. Cambiare la
  quote renderebbe insufficiente il solo controllo letterale: resta il divieto
  generale di promozione/scrittura senza valutazione semantica.
- Direttore tecnico: un unico fatto contiene nome + numero 8421 + ordine.
  La riga intera viene riproposta nei campi nome, qualifica, ordine e numero.
  Il valore esiste nella SOURCE -32 ma non è il valore atomico richiesto.
  Questi errori passano il grounding; non diventano RESOLVED.
- Rami condizionali: dati veri trasferiti a sezioni con ruoli non attestati,
  tra cui consorziata esecutrice, senza verificare l'applicabilità. Nessuna
  approvazione semantica. Le NA prive di condizioni sono invece rifiutate:
  **53** nella prima risposta, **80** nella seconda.
- CCIAA: la prima riusa il numero REA per numero/data iscrizione richiesti;
  la seconda distingue questi dati e lascia review. La data di abilitazione
  rimane senza valore: non viene inventata.
- Quote FORM fuori dal contesto locale: 6 e 24 rifiuti; una quote FORM assente
  nel paragrafo in entrambe. Il backend non allarga i contesti per farle passare.

Le disposition grezze sono, rispettivamente, value=60/review=194/NA=53 e
value=44/review=183/NA=80. Questi conteggi non misurano dati corretti o compilabili.
Le annotazioni umane coprono 16 posizioni per prova, non tutte le 307.

## La risposta con ragionamento

37.418 token di ragionamento, 11.734 token restanti di contenuto: il provider
raggiunge il budget e interrompe il JSON. Il trasporto rifiuta la risposta prima
del validator: zero campi accettati, nessun recupero del prefisso, nessun retry.

Solo per diagnosi offline, i primi oggetti completi contengono 16 fatti e
20 condizioni, seguiti da un oggetto fields troncato. Il ragionamento ha dunque
proposto una struttura differente, **non una proposta utilizzabile**. Rimangono
anche associazioni discutibili, incluso supporto di partecipazione con tipologia
e fatti CCIAA compositi. Non si deduce correttezza dal numero di condizioni.
HTTP completo/usage e frammenti diagnostici separati conservati nell'audit;
i frammenti non entrano nel flusso applicativo.

## Verifiche, conservazione e ripresa

**110 test mirati, 1.506 backend completi**, Ruff completo, CLI help e diff check
effettivamente eseguiti. I primi controlli prima dell'opzione thinking erano
108/1.504: non confondere i checkpoint. Un primo CLI help senza `PYTHONPATH=.`
falliva nell'import; comando corretto riuscito e log entrambi conservati.
Test software con provider simulati e DB/storage temporanei, distinti dalle tre
prove semantiche reali. Frontend intatto, non rieseguito. Originale invariato.
Nessuna migrazione, reindicizzazione o modifica di sessioni locali.

[Riepilogo e annotazioni JSON](benchmarks/2026-10-10-compilation-global-conditions.json).
Acquisizioni persistenti sotto `backend/data/compilation-audit/`, prefisso
`global-conditions-20261010-`: run1, run2, run3-thinking, analysis, checks,
thinking-checks e final-checks. Prompt, schema, input, HTTP/output, usage,
validazione quando disponibile, originale, codice congelato, manifest e log.
Anche [bundle versionato](benchmarks/2026-10-10-global-conditions-audit.tar.gz) con
[checksum](benchmarks/2026-10-10-global-conditions-audit.tar.gz.sha256), senza
credenziali/database; i soli file sotto backend/data non sarebbero trasferiti da Git.

**Decisione: non attivare questo contratto nella chat.** Il passo successivo
deve misurare un output più essenziale, con fatti atomici e un inventario di
sezioni/condizioni effettivamente compilato nella stessa chiamata. Il numero
di spiegazioni ripetute va ridotto, non il grounding. Prima nuove regressioni
per associazioni improprie e condizioni omesse, poi confronto congelato;
nessun adapter a sessione/checkbox/export finché manca una verifica semantica
adeguata. Non aumentare automaticamente il budget o aggiungere reviewer per gruppi.
