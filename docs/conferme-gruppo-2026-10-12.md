# Conferme riferite al gruppo attivo — 12 ottobre 2026

**Rettifica successiva sul replay 8/12:** individuato catalogo grezzo senza
anchor nel setup, quindi contesto FORM vuoto alla sintesi. Il risultato storico
rimane archiviato, ma non dimostra da solo una regressione applicativa. Il
[confronto corretto](sintesi-ruoli-2026-10-12.md) conserva 12 export già prima
del fix del contesto SOURCE dei ruoli. Nessun gold o raw storico modificato.

## Diagnosi e protocollo congelato prima delle API

Baseline applicativa fb2894e, HEAD diagnostico 8e90915; al controllo iniziale
working tree pulito, tre commit davanti a origin/prune-backend. Nessun push.
Il turno 04 del [test completo](test-conversazione-completa-2026-10-12.md)
aveva due domande: applicabilità della sezione e identità del partecipante.
Il router proponeva correttamente CONDITION_TRUE su entrambi gli slot. Il gate
USER indipendente accettava il primo e rifiutava il secondo come AMBIGUOUS:
«il partecipante è quello indicato nelle fonti» era considerato troppo generico,
anche nel messaggio completo «Confermo entrambe: ...».

`render_dialogue` conserva già `question` in ciascuno slot persistito;
`intents.routing_context` lo perde nella proiezione destinata ai modelli.
Rimangono la domanda complessiva, label e contesto FORM: la seconda condition
è soltanto «CHIEDE di partecipare alla presente gara». Nessuna perdita della
frase USER intera: è già inviata. Il prompt del verificatore ammette parafrasi
ma non chiarisce l'ambito delle conferme esplicite dell'intero gruppo.
Non è un difetto del retrieval SOURCE o dello schema della risposta.

Modifica minima prevista: preservare il testo naturale per slot (massimo 600
caratteri, stessa dimensione già validata nella sintesi) e precisare nel gate
la risoluzione dei riferimenti alla domanda attiva, le eccezioni e la polarità.
Nessuna accettazione automatica, keyword USER, nuovo schema/API, seconda ricerca
o chiamata AI. Il gate semantico indipendente continua a fallire in modo
conservativo, prima di quote/validator DOCX/CAS/provenance USER. I casi storici
senza question per slot restano leggibili. Turni composti ancora da discutere.

Congelati [16 scenari V1](../demo-documents/benchmark-dialogo/group-confirmations-v1/README.md)
prima delle API: caso reale, parafrasi, conferme di entrambe, riferimenti
numerati, negazioni, eccezioni locali, parti incerte, conferme senza valori,
correzioni estranee e ambiguità. Nuova fixture, gold storico invariato.
Il runner guard esistente accetta una fixture esplicita e verifica hash, slot
e budget prima di leggere il profilo AI o chiamare il provider.

BEFORE e AFTER: stessa fixture, 16 chiamate massime per fase, nessun retry,
15 s/768 token output per chiamata. Nuovo checkpoint DB/storage temporanei
per caso. Proposte preparate non affidabili, provider DeepSeek Flash reale;
gold non inviato. Gli slot registrati vengono rimappati su due candidate della
fixture di dialogo per misurare mutazioni USER, non correttezza del modulo intero.
Regressioni AFTER su guard-v1 (9) e Dialogo V1 (43). Nessuna ripetizione
selettiva, errori conservati. Replay del checkpoint reale separato da nuove
analisi SOURCE; nessuna pretesa di avere rieseguito l'analisi globale.

Prima delle API: quattro test del protocollo senza provider passati /0,54 s;
Ruff runner/test e diff check passati. Risultati e costi saranno aggiunti dopo
le serie, senza modificare aspettative o codice durante ciascuna serie.

## Baseline e modifica applicativa

BEFORE sul commit 0ef3bd5: **14/16** conformi. Riprodotto il caso registrato:
SUPPORTED primo slot, AMBIGUOUS secondo. Anche la conferma di tre punti misti
respingeva interamente le proposte, compresa la sola condizione rispondibile.
Tutti i controesempi negativi conformi, nessuna scrittura estranea.
Grezzi `backend/data/compilation-audit/group-confirmations-20261012/before/`.

Applicata soltanto la proiezione `question` per slot e il task del verificatore,
senza cambiare output, binding destinatari, numero di chiamate o accettazione
deterministica. Task generico: riferimenti univoci alla domanda attiva, ambito
esplicito del gruppo, eccezioni locali; una conferma non inventa valori VALUE.
**72 test software mirati /7,39 s**, provider simulati per i test di stato,
Ruff file modificati superato. Non misurano DeepSeek; la serie AFTER segue.

Prima serie AFTER su c6bd0ff: **15/16**. Il caso reale è corretto, entrambi
SUPPORTED e aggiornamenti USER distinti; i casi già conformi restano conformi.
Rimane il gruppo misto «Confermo tutti e tre i punti»: respinti correttamente
email/data inventati, ma erroneamente anche la conferma della condizione.
Precisata soltanto l'indipendenza delle condizioni booleane dalle richieste
di valori assenti nello stesso gruppo. Nuova serie completa AFTER-2 con lo
stesso gold congelato, nessuna ripetizione selettiva; AFTER precedente conservata.

Replay reale previsto: nuova sessione in snapshot privato, riuso dichiarato
del checkpoint Catanzaro precedente al consenso (non nuova analisi). Rivalidare
il raw reale contro originale e corpus corrente, chiedendo l'uguaglianza con
l'audit archiviato. Due turni HTTP ASGI reali: stessa conferma anaforica, poi
richiesta esplicita di bozza. Routing/gate/sintesi reali, originali e dati live
solo letti. Confrontare due condizioni USER, zero valori fattuali USER, stessa
analisi, 12 proposte SOURCE/stato/report/celle; eliminare snapshot e chiave dopo
le verifiche. Runner fuori dal watch root backend, nessuna modifica durante le API.

Prima preparazione replay fallita prima delle API: l'archivio senza risposte
non contiene ancora le chiavi answers/user_values. Corretto solo l'harness
usando i default vuoti già previsti dal dominio, conservati protocollo/log della
preparazione fallita e rimossi snapshot/chiave privata; nuova preparazione in
cartella distinta. Nessun raw modello o risultato escluso/ripetuto selettivamente.

## Esiti reali e costi

| Serie | Conformi | Chiamate | Token totali | Secondi AI |
|---|---:|---:|---:|---:|
| BEFORE, 0ef3bd5 | 14/16 | 16 | 21.125 | 19,26 |
| AFTER, c6bd0ff | 15/16 | 16 | 27.743 | 20,18 |
| AFTER-2, b8c88f8 | 16/16 | 16 | 29.094 | 21,30 |
| Guard storico V1 | 9/9 | 9 | 12.424 | 9,51 |
| Dialogo storico V1 | 43/43 | 56 | 179.071 | 66,21 |
| Replay reale, conferma + export | conferma riuscita, export 8/12 | 4 | 12.810 | 5,83 |

Totale: **100 casi indipendenti +2 turni replay /117 chiamate /282.267 token
/142,30 s AI**. Sono costi di più serie, non di una singola compilazione.
Nessun retry del verificatore, timeout/768 token invariati. Nel Dialogo V1
44 routing +12 guard: export-no produce prima uno schema/intent invalido, il
retry strutturale lo corregge senza scrivere o esportare. Cinque export della
fixture confrontati con stato/report/Word; originali invariati, USER esplicito.
Nessun caso già conforme diventa scorretto. Guard 9/9 preserva il blocco della
denominazione nel recapito, numeri estranei, alternative e sì ambiguo.

La maggiore chiarezza costa token: nel caso reale congelato il prompt del gate
passa da 1.233 a 1.733 token input (+500), con numero di chiamate invariato. Non è una
riduzione del costo per turno. Latenze/costo e singola variabilità sono dichiarati;
il set è stato usato per affinare il prompt, non è una valutazione held-out.
Gold, fixture e codice congelati durante ogni serie, nessuna selezione dei raw.

## Replay Catanzaro: aggiornamenti e Word

Nuova sessione `252f84a7a8f846e09ca37d0fb20b9251`, due processi HTTP ASGI;
checkpoint reale riutilizzato e rivalidato, nessuna nuova analisi globale.
Il router propone due CONDITION_TRUE con estratti USER. Verificatore reale:

```json
{"checks":[
  {"slot":1,"result":"SUPPORTED","rationale":"L'utente conferma esplicitamente che la sezione delle società di ingegneria si applica, rispondendo alla domanda 1."},
  {"slot":2,"result":"SUPPORTED","rationale":"L'utente conferma che il partecipante è quello indicato nelle fonti, cioè Mapi Ingegneria S.r.l., rispondendo alla domanda 2."}
]}
```

Backend: `condition:c_socing` e `condition:c_domanda` -> CONDITION_TRUE,
`applies=true`, provenance USER, estratti conservati. Zero valori fattuali USER.
Stessa sessione/versioni persistite -> sintesi -> consenso esplicito alla bozza
-> GENERATED. Le due conferme richiedono un turno anziché i due del test precedente.
La bozza resta parziale: nessuna dichiarazione di compilazione completa/RESOLVED.

| Posizione | Valore nel Word | Provenienza |
|---|---|---|
| Operatore economico, t0.r5.c1 | Mapi Ingegneria S.r.l. | SOURCE Company KB, visura, chunk -30 /file -9 |
| Forma giuridica, t0.r6.c1 | Societa a responsabilita limitata | SOURCE, stessa visura |
| Sede legale, t0.r7.c1 | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE, stessa visura |
| Codice fiscale, t0.r9.c1 | IT01234567890 | SOURCE, stessa visura |
| Partita IVA, t0.r10.c1 | IT01234567890 | SOURCE, stessa visura |
| Tre campi omologhi della sezione 5.d | Denominazione, forma giuridica, sede legale | SOURCE, stessa visura |

**Criterio dei dodici valori NON superato**, conservato come fallimento del
replay completo: la nuova sintesi restituisce held_proposal_slots=[9,10,11,12],
sospendendo nome/qualifica/Ordine/8421 del direttore tecnico per dubbio sul ruolo.
Otto valori esportati, tutti effettivamente scritti nelle celle di stato/report.
Le 12 proposte SOURCE restano persistite, niente perso nel retrieval/gate USER;
quattro sono esclusioni conservative della sintesi. Non abbassato il criterio,
non forzati valori o ripetuto il replay per ottenere 12. Sintesi e contesto di
risposte cambiano fra le conversazioni: non è un confronto causale isolato per
quel limite. SOURCE, parser e renderer non sono stati modificati.

Originale immutato, nessuna cella aggiuntiva cambiata; paragrafi invariati salvo
banner, checkbox native identiche, ZIP modificato solo in document.xml. Tabelle
live inalterate dall'inizio del replay; nessuna modifica ai dati dell'utente.
Snapshot e chiave privata eliminati dopo le verifiche, anche dopo l'assert del
conteggio 12 fallito. Il fallimento e la verifica degli otto valori sono archiviati.

## Verifiche software e ripresa

Provider simulati soltanto nei test software; DB/storage temporanei. **72 test
mirati iniziali /7,39 s**, **270 mirati finali /47,74 s**, **1.972 backend finali
/151,49 s**, Ruff backend/runner e diff check superati. Suite intermedia: 1.972
/146,40 s. Quattro controlli del protocollo /0,54 s senza provider. Primo comando
mirato finale senza test eseguiti per un nome di file errato, corretto; preflight
Ruff del runner replay con una riga lunga corretto prima delle API. Log conservati.
Frontend/browser non ripetuti perché nessun contratto/UI è cambiato.

Il falso negativo di conferma del gruppo è corretto nei casi misurati; non è
garanzia matematica di interpretazione. Gate indipendente, slot attivi, USER
letterale/normalizzazione consentita, CAS e validazione DOCX restano richiesti.
Nessuna migrazione/reindex, checkbox o allargamento di SOURCE. Prossimo tema
proposto: sospensioni conservative della sintesi per i ruoli, misurate separatamente.
«Salva valore e poi pausa/export» resta da discutere, comportamento invariato.

[Metriche complete](benchmarks/2026-10-12-group-confirmations.json),
[bundle dei grezzi](benchmarks/2026-10-12-group-confirmations-audit.tar.gz).
Grezzi: `backend/data/compilation-audit/group-confirmations-20261012/`, prompt,
schema, raw, usage/tempi, checkpoint e stati dopo ciascun caso, Word/report reali,
log anche dei fallimenti. Piccoli commit di protocollo/fix/test, nessun push.

Archivio verificato byte per byte: **629 file /1.297.367 byte**,
SHA-256 `09355f5429c68a71fd42e238a0b3739397af3befd0e6f36ec28dc2fa0259a522`.
[Manifest pubblico](benchmarks/2026-10-12-group-confirmations-audit-manifest.json),
[verifiche finali](benchmarks/2026-10-12-group-confirmations-final-checks.json).
Nessun database, chiave o runtime privato incluso.

Per riprovare dalla chat: una nuova compilazione del modulo con il profilo
DeepSeek e le stesse fonti; quando sono attive le due domande, rispondere
«Confermo entrambe: la sezione delle società di ingegneria si applica e il
partecipante è quello indicato nelle fonti». Devono essere acquisite entrambe
come decisioni USER, senza nuova ricerca SOURCE né secondo consenso sul nome.
Se si chiede esplicitamente una bozza, i dati non verificati/esclusi restano vuoti;
le quattro proposte del direttore tecnico possono ancora essere sospese dalla
sintesi. Un sì senza ambito davanti a più condizioni richiede chiarimento.
