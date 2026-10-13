# Copertura testuale, dati professionali e rinvii locali

Intervento sui primi tre problemi della diagnosi Minervino: omissioni testuali,
direttore tecnico presente nelle SOURCE ma perso nell'output, rinvio di un dato
personale che sospende anche dati aziendali. Miglioramento delle checkbox rinviato.
Baseline `23357b6`; implementazione in due passi, `c9a28fe` e `052c473`.
Nessuna modifica a RAG, parser, renderer o UI. Nessun push o modifica ai dati live.

## Cause e interventi

Il precedente JSON reale proponeva 16 valori, 15 accettati dal grounding, ma
nessuno per il direttore. I relativi dati erano già nei 51 chunk inviati:
omissione del modello, non perdita nel retrieval o nel renderer. Il catalogo
resta completo; la proposta è sparse e non prova di avere esaminato ogni campo.

La stessa chiamata riceve ora un `reading_plan` deterministico: gruppi di
candidate strutturali, riferimenti a ruoli nominati letteralmente in FORM e
intestazioni SOURCE e un indice compatto delle righe SOURCE con attributi.
Niente valori dedotti, sinonimi hardcodati o assegnazioni approvate dal piano.
Il testo completo delle fonti resta disponibile e tutti i gate precedenti
restano necessari. Un indizio di ruolo senza proposte è segnalato come blocco
ancora da valutare, non come dato assente dalla KB da chiedere all'utente.

Una mappa opzionale `clarifications`, massimo 16 domande locali, separa i dati
USER mancanti dalle vere condizioni di applicabilità. Ogni domanda ha una
destinazione testuale reale, quote FORM locale verificata e condizioni valide.
Non contiene valori, fact_id o SOURCE. Un item invalido viene messo in quarantena
senza eliminare proposte indipendenti. Non è un inventario dei vuoti obbligatori.
Il destinatario USER resta del backend; le risposte usano gli slot esistenti.

Un rinvio locale conserva gli altri valori. Per condizioni che governano più
field, domanda e router conservano il perimetro umano; il backend esplicita
quanti dati resterebbero vuoti. SKIP/UNKNOWN/REFUSE di questi blocchi passano
anche dal verificatore semantico già presente. Un rinvio non univoco produce
chiarimento, non la perdita silenziosa di proposte. Gli altri slot validi si
conservano. Lo stato registra i candidate coinvolti, senza esporre ID nella chat.
La sintesi riceve anche il flag di rinvio e non deve promettere di scrivere
proposte già differite. Non vengono eliminate automaticamente condizioni incerte.

Budget: una sola analisi globale, sintesi separata esistente, 32 indizi di ruolo
con quattro riferimenti ciascuno, 256 righe SOURCE / 24.000 caratteri complessivi.
Omissioni dell'indice dichiarate; il corpus completo non viene troncato da esso.
General KB esclusa dagli indizi anagrafici, scope originali conservati. Il gate
USER resta una chiamata bounded per gruppo, 15 secondi, senza retry: rinviare
solo un campo non aggiunge una chiamata; rinviare un intero blocco può richiederla.

## Test software e crash riprodotti

**2.146 test backend / 152,53 s**, **214 mirati / 25,74 s**, Ruff e diff check
passati sullo stato finale. DB/storage temporanei, provider simulati, FTS5 e
Qdrant dove applicabile. Nessuna misura della qualità del modello da questi test.
Frontend/browser non rieseguiti: nessuna modifica UI o contratto frontend.

Fuzzing riproducibile: 960 mutazioni di JSON globale e 480 piani chat, più
test HTTP con Unicode invalido, NaN/infinito, nesting, SQL/HTML testuali,
emoji, controlli e comandi contraddittori. Regressioni per Source/USER distinti,
rinvio locale, conferma + rinvio parziale, perimetro ambiguo, ripresa da DB,
export dall'originale e grounding delle domande.

Riprodotti e corretti:

- Diagnostici modello con surrogate Unicode o numeri non finiti non serializzabili:
  rifiuto bounded prima di entrare nell'audit; profondità 48 / 100.000 nodi.
- Sei casi HTTP500 nel formatter del normale errore422: Pydantic rifiutava
  correttamente il payload, ma la risposta conteneva l'input non serializzabile.
  Ora errore422 controllato. Il handler riguarda solo RequestValidationError,
  non nasconde errori interni generici.
- Due crash del retry planner: un output con surrogate letterale era rifiutato,
  poi ricopiato nel prompt di correzione non codificabile UTF-8. Escape soltanto
  nel diagnostico inviato al retry e nei log, mai riparazione di valori fattuali.

JSON globale invalido -> HTTP502 controllato, sessione FAILED, nessun DOCX.
Un errore del provider non diventa un successo. Nessuna promessa di assenza
universale di crash: coperti i boundary riprodotti e i casi documentati.
Conservati tutti i log, comprese aspettative di test inizialmente obsolete e
fixture corrette; non confondere tali fallimenti con bug applicativi.

## DeepSeek reale, tutte le prove

[Protocollo](benchmarks/2026-10-13-text-coverage-protocol.json),
[metriche complete](benchmarks/2026-10-13-text-coverage.json).
Codice applicativo congelato dentro ciascuna serie; modifiche soltanto fra serie.
Ultima correzione Unicode applicata dopo le API, testata software; non cambia
i prompt/valori dei casi validi misurati. Nessun gold nel prompt.

Stesso originale Minervino e stesso corpus registrato, nessuna aggiunta di dati.
Fonte `generalita-mapi.md`, record personale, più visura simulata. Due serie:
la prima con gruppi/ruoli e domande locali, la seconda aggiunge l'indice delle
proprietà dopo aver conservato gli esiti negativi della prima.

| Prova | Proposte SOURCE accettate | Nome/qualifica/ordine/8421 | Testi scritti | Analisi |
|---|---:|---|---:|---:|
| Baseline utente storica | 15 | nessuno | 9 | 119,20 s |
| Serie 1 Minervino 1 | 9 | tutti quattro | 0 | 110,90 s |
| Serie 1 Minervino 2 | 16 | tutti quattro | 0 | 121,61 s |
| Serie 1 HTTP nuovo | 4 | tutti quattro | 4 | tempi/call nelle metriche |
| Serie 2 Minervino 1 | 18 | tutti quattro | 0 | 159,09 s |
| Serie 2 Minervino 2 | 19 | tutti quattro | 0 | 105,16 s |
| Serie 2 HTTP nuovo | 19 | tutti quattro | 0 | tempi/call nelle metriche |
| Serie 1 Labirinto V1 | 23 inclusi booleani | fixture diversa | 11 | 99,07 s |
| Serie 2 Labirinto V1 | 23 inclusi booleani | fixture diversa | 11 | 130,55 s |

«Accettate» indica grounding locale, non RESOLVED o applicabilità verificata.
Le quattro proprietà professionali compaiono in tutte sei le analisi Minervino:
`p51.s0 -> Ing. Elisa Romano`, `p52.s0 -> Ingegnere`,
`p53.s0 -> Ordine degli Ingegneri di Bari`, `p53.s4 -> 8421`.
Quote e record SOURCE separati per proprietà. Il gold atteso «Elisa Romano»
non include l'onorifico: questo scostamento letterale non viene cancellato
modificando il gold. La data di abilitazione non viene inventata.

L'indice delle proprietà migliora la copertura osservata: 18/19/19 proposte
contro 9/16/4 della prima serie; non prova un miglioramento statistico generale.
Labirinto conserva undici testi e cinque checkbox già supportate, senza nuovo
codice checkbox. La copertura dei rami senza prova resta incompleta.

Due conversazioni HTTP ASGI nuove/private, quattro messaggi predefiniti ciascuna,
provider reale e nessuna simulazione delle risposte. Corpus importato mediante
repository da snapshot: identità dei chunk rimappate, contenuti/scope confrontati
integralmente. Non è un test di nuova estrazione/embedding. Stessa persistenza,
API di chat/resolve, gate e download dell'applicazione; nessun browser.

Nella prima il modello omette i dati aziendali e chiede erroneamente la
denominazione già in SOURCE. La carica è però una domanda locale: SKIP non
elimina le quattro proposte del direttore, poi materializzate dopo consenso.
Esito negativo di copertura conservato; nessun dato aziendale fornito via USER.

Nella seconda tutti 19 i dati vengono proposti. Il modello crea ancora una
condizione molto ampia sull'operatore. Alla risposta composta produce due
decisioni incompatibili sullo stesso slot: quelle vengono scartate, l'altro
slot valido si conserva. Il rinvio successivo della conferma impedisce l'uso
dei valori: **la copia parziale esplicitamente richiesta è vuota**, non una
compilazione completata. Nessuna condizione o identità confermata dal runner
di nascosto. Queste prove non certificano una UX interamente naturale.

Regressione di comandi su 43 checkpoint preparati: **42/43**, 56 chiamate,
stesso limite conservativo noto su `export-no` (answer_fields senza slot, anche
al retry). Zero export non autorizzati; non è un nuovo E2E di analisi.
Una preparazione HTTP fallisce prima dell'AI per cartella fixture assente:
corretto solo il runner, tentativo conservato. Anche il primo verifier includeva
report di checkpoint con nomi file differenti: esclusi esplicitamente dal suo
perimetro, nessuna modifica del motore durante le prove.

Totale acquisito: **87 chiamate, 8 analisi, 934.320 token, 1.245,68 secondi AI
sommati**; non tempo wall, prezzo fatturato o risparmio dimostrato.
I benchmark reali includono ancora analisi di minuti: nessuna ottimizzazione
della latenza viene rivendicata.

Verificati in sola lettura otto DOCX e 26 valori: ogni paragrafo corrisponde
esattamente all'originale più i valori selezionati, non solo una ricerca globale
del testo. Posizioni non selezionate invariate, 15/18 parti ZIP estranee identiche,
prove SOURCE/digest nei report HTTP controllati. Originale fornito dall'utente
e DB live invariati; DB/chiavi private eliminati. Fonte e USER sempre distinti.

## Limiti e ripresa

Rinvii locali e crash riprodotti sono corretti e coperti da regressioni.
Copertura e dati professionali sono migliorati, **non garantiti su tutti i campi**.
Il modello può ancora creare condizioni troppo ampie o domande sulla qualità
invece che sull'identità/ramo; il gate tutela da rinvii non pertinenti ma non
può inventare una decomposizione semantica corretta. Non si rimuovono condizioni
per rendere artificialmente esportabili i valori. L'indirizzo completo nel
campo comune resta variabile. Non dichiarare conclusi tutti i limiti osservati.

Nessuna migrazione/reindex: usare una nuova conversazione per la nuova analisi.
Sessioni precedenti e originali restano invariati. Prossimo punto di ripresa:
verificare separazione di identità del partecipante/qualità personale e copertura
residua, prima di dichiarare completa la compilazione. Checkbox ancora rinviate.

Raw in `backend/data/compilation-audit/text-coverage-20261013/`;
[bundle](benchmarks/2026-10-13-text-coverage-audit.tar.gz) e
[manifest](benchmarks/2026-10-13-text-coverage-manifest.json) conservano anche
fallimenti, prompt/schema, HTTP, output, audit, codice congelato, stati e copie.
Nessun DB o credenziale nell'archivio.
743 file / 16.587.562 byte grezzi, verificati byte per byte e con controllo
della chiave reale. SHA256 archivio:
`cd1c8becd3fbe54adf46a61fc7bec76ddcdeb82798937e7b3c25419d00dbcc1b`.
