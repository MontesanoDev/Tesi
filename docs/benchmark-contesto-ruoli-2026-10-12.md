# Contesto fra paragrafi e record personali SOURCE — 12 ottobre 2026

Il passo migliora il recupero di dati personali nel prototipo a **una chiamata**.
Non è ancora compilazione completa affidabile: copertura, citazioni FORM e
applicabilità restano variabili. Tutte le proposte richiedono revisione;
**zero RESOLVED, input USER, sessioni create o DOCX scritti**.

## Diagnosi e modifica circoscritta

La baseline V9 Minervino proponeva già dati del direttore ma li rifiutava:

1. Il ruolo è nel paragrafo 50. Il contesto dei candidate 52/53 ammetteva solo
   la riga locale e l'ultimo paragrafo precedente: perdeva l'introduzione 50.
2. La SOURCE usa `### Ing. Elisa Romano - direttore tecnico` oppure una riga
   `DIRETTORE TECNICO Ing. Elisa Romano - ...`. Il gate ammetteva soltanto
   `ruolo: persona` a inizio clausola.
3. Un'altra risposta citava il ruolo nel chunk -32 e i valori nel -45. Il join
   fra chunk non dimostra l'attribuzione e **rimane rifiutato**.

Catalogo **V5** aggiunge solo un riferimento di lettura, ad esempio:

```json
{
  "p53.s4": {
    "context_id": "paragraph:53",
    "continuation_origin_paragraph_id": "paragraph:50",
    "anchor_paragraph_ids": ["paragraph:53"],
    "slot_context": {"before": " con il n. ", "after": ""}
  }
}
```

L'origine è l'ultimo paragrafo del corpo senza candidate prima di una sequenza
consecutiva di massimo **sei paragrafi con candidate**. Nuova prosa, blank,
outline, tabelle e controlli checkbox interrompono il riferimento. Non sono
sei chiamate/batch: il catalogo completo viene inviato una volta. Nessun testo
copiato, ruolo inferito o ampliamento delle ancore di destinazione `field.form`.

Contratto **V10** usa quell'origine solo per il binding del ruolo. Accetta due
formati SOURCE letterali aggiuntivi: heading Markdown persona-ruolo e riga con
ruolo maiuscolo seguito dalla persona. Richiede persona completa, ruolo uguale
al FORM, intera intestazione nella quote e valori nello **stesso record/chunk**.
Record terminato alla prossima intestazione o riga con primo token maiuscolo.
Abbreviazioni sintattiche non diventano qualifiche professionali. Nessun elenco
hardcoded di aziende, campi, ruoli, titoli, documenti o candidate.

Negazioni/narrative, persona o ruolo diversi, altro record, General KB e join
fra chunk non passano il nuovo percorso. FORM non prova un valore; USER non
entra nelle SOURCE. I formati precedenti conservano i loro limiti noti: questi
sono controlli necessari di attribuzione letterale, **non entailment semantico
completo**. Gate condizioni, slot, valore, provenance e alternative invariati.
V2–V9 rimangono per replay; il runner attivo impone V10.

Riutilizzati catalogo, schema condiviso e validatori. Parser generale, renderer,
V1/chat/RAG, UI e dati locali non modificati. Nessuna migrazione/reindicizzazione.

## Due serie separate, entrambe conservate

Prima serie congelata su `660bf0e`: tre Minervino, tre Labirinto V1, un Catanzaro.
**Fallisce il controllo dei cinque dati Catanzaro**: il modello si concentra sul
ramo finale, omette la tabella iniziale e CF/PIVA. Non è un rifiuto SOURCE.

Dopo tutte le sette risposte, commit `a037314` modifica soltanto TASK:
riesaminare tutti i blocchi e tutte le occorrenze compatibili di un fatto,
riusando fact_id con ancore/condizioni proprie. Schema e gate restano V10.
Secondo protocollo preregistrato: tre Catanzaro, un Minervino, un Labirinto.
Nessuna selezione del solo risultato favorevole e nessuna modifica durante
le acquisizioni delle due serie. Nessun nuovo sorteggio: controlli sugli stessi
bandi già scelti nel confronto precedente, non una prova casuale aggiuntiva.

Tutte le **12 chiamate reali deepseek-flash**, seriali, thinking low,
temperature 0,1, timeout 300 s, una chiamata/prova, zero retry, terminano HTTP200/
stop. Minervino/Catanzaro: stessi 17 chunk autorizzati del workspace `prova`
(13 Company, 4 General), nessuna fonte di progetto; Labirinto: sette SOURCE
fixture. Corpus piccolo completo, **non misura retrieval FTS5/Qdrant o chat V1**.
Originali, fonti e gold congelati; gold e risultati attesi fuori dal prompt.

| Serie | Documento/prova | Raw | Valori grounded¹ | Conditional inclusi | NA locale | Alternative | Rifiuti | Omessi² | Token | AI s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| iniziale | Minervino 1 | 21 | 20 | 20 | 0 | 0 | 1 | 246 | 72.466 | 114,62 |
| iniziale | Labirinto 1 | 22 | 18 | 6 | 0 | 2 | 2 | 33 | 37.044 | 91,88 |
| iniziale | Minervino 2 | 15 | 13 | 13 | 0 | 0 | 2 | 252 | 63.332 | 81,27 |
| iniziale | Labirinto 2 | 21 | 18 | 6 | 1 | 2 | 0 | 34 | 37.950 | 95,45 |
| iniziale | Minervino 3 | 10 | 10 | 10 | 0 | 0 | 0 | 257 | 66.584 | 89,52 |
| iniziale | Labirinto 3 | 21 | 17 | 5 | 0 | 2 | 2 | 34 | 35.884 | 74,51 |
| iniziale | Catanzaro 1 | 8 | 7 | 7 | 0 | 0 | 1 | 299 | 85.487 | 83,82 |
| copertura | Catanzaro 1 | 13 | 13 | 13 | 0 | 0 | 0 | 294 | 84.014 | 86,43 |
| copertura | Minervino 1 | 19 | 19 | 19 | 0 | 0 | 0 | 248 | 65.549 | 87,97 |
| copertura | Labirinto 1 | 21 | 18 | 6 | 1 | 2 | 0 | 34 | 40.090 | 104,17 |
| copertura | Catanzaro 2 | 15 | 6 | 0 | 0 | 0 | 9 | 292 | 91.864 | 107,34 |
| copertura | Catanzaro 3 | 15 | 11 | 3 | 0 | 0 | 4 | 292 | 84.922 | 76,32 |

¹ Ipotesi SOURCE con grounding locale, incluse scelte checkbox. Non RESOLVED,
non approvazione semantica o autorizzazione di scrittura. Le conditional hanno
value=null e proposed_value separato. Anche GROUNDED_PROPOSAL resta review-only.
² Posizioni strutturali omesse, non conteggio di requisiti obbligatori missing.

Totale: **201 record, 170 ipotesi di valore** (62 senza condizioni sconosciute,
108 conditional), due NA locali, otto review con alternative e 21 rifiuti.
37 ipotesi personali conservate. Inventario completo: 2.516 posizioni nelle 12
prove, incluse 2.315 omissioni. Nessuna promozione/scrittura.

## Risultati e limiti osservati

**Minervino:** dati del direttore conservati 5/0/4/5 nelle quattro prove nuove,
compreso 8421 nelle tre risposte con dati personali. Nella seconda il modello
li omette: il gate non li ha respinti. La baseline V9 aveva zero personali
conservati. Non è un confronto causale/statistico, ma dimostra un caso prima
bloccato ora correttamente attribuito alla SOURCE.

| Candidate Minervino, prima prova | Valore proposto | Prova SOURCE | Esito |
|---|---|---|---|
| p51.s0 — nome | Ing. Elisa Romano | generalita-mapi.md, -45 | conditional grounded |
| p52.s0 — qualifica | Ingegnere | stesso record -45 | conditional grounded |
| p53.s0 — ordine | Ordine degli Ingegneri di Bari | stesso record -45 | conditional grounded |
| p53.s2 — provincia ordine | Bari | stesso record -45 | conditional grounded |
| p53.s4 — numero albo | 8421 | stesso record -45 | conditional grounded |

Prova di ruolo: `### Ing. Elisa Romano - direttore tecnico`; file_id=-7,
chunk_index=2, role=source, scope=global, category=company. Audit registra header,
line_range `[7,21)` zero-based, quote dei valori e hash del contenuto. FORM del
ruolo paragraph:50, destinazioni rispettivamente 51/52/53. Data abilitazione e
identità personale non documentate non vengono inventate.

Riga critica `p42.s0..s5`: sei/cinque/tre/sei proposte, ma componenti corretti
**sei/quattro/tre/sei**: nella seconda via include il civico, mentre lo slot
civico è omesso. Telefono/e-mail/PEC corretti **4/4**, nessuno slittamento dei
recapiti osservato. Non equivale a completezza della riga. Due proposte iniziali
mettono l'indirizzo completo nel campo città p41.s1; l'ultima usa Bari.
`p16.s0` mantiene una quote debole `[[p16.s0]] P.E.C.` che etichetta lo spazio
successivo, pur proponendo l'e-mail nella posizione corretta. Marker e SOURCE
non certificano l'entailment della proprietà. Marker/punteggiatura senza parole
nei campi iniziali vengono invece correttamente rifiutati. Limite ancora aperto.

**Catanzaro:** dopo TASK, tutti i cinque dati societari sono conservati in 3/3,
con ancore della tabella iniziale e SOURCE reali, senza USER:

| Candidate | Requisito | Valore | SOURCE |
|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | -43 / generalita-mapi.md |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | -43 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | -43 |
| t0.r9.c1 | Codice fiscale | IT01234567890 | -43 |
| t0.r10.c1 | Partita IVA | IT01234567890 | -43 |

Sono dati demo simulati presenti nelle SOURCE, non attestazioni aziendali reali.
Nella prima prova successiva tutti e cinque sono conditional; nelle altre due
sono GROUNDED_PROPOSAL review-only. Prima serie: cinque omessi, non successo.
Cellulare + Telefono riceve solo telefono: resta compilazione parziale del campo.

Quattro dati del direttore proposti in tutte le risposte Catanzaro, ma conservati
solo nella prima iniziale e nella prima successiva. **Due failure distinte nella
seconda serie**, da non mascherare:

- Prova 2: il nuovo binding personale passa, ma il modello usa `value` anziché
  `conditional` con applicabilità semantic=unknown. Sette campi ingegneria e
  un'ulteriore occorrenza personale t44.r1.c0 vengono rifiutati; inoltre NA sede
  operativa non calcolabile respinta. Non convertiti automaticamente in validi.
- Prova 3: binding FORM cita `i requisiti del direttore tecnico ...`, mentre
  paragraph:451 contiene `dei requisiti del direttore tecnico ...`. La quote
  comincia dentro una parola e non passa il matching con confini. Le quattro
  proposte personali vengono bloccate prima del gate del record SOURCE.

La SOURCE del numero 8421 è presente; queste failure non sono assenza del dato
nella KB. Nessuna modifica durante il benchmark per farle passare.

**Labirinto V1:** 18/22 corrispondenze letterali valore/SOURCE in 4/4; dopo tutti
i gate **18/18/17/18** target conservati. Cinque dati societari in 4/4. Numero
5739 separato dall'ordine, salvo terza prova iniziale: il modello aggiunge una
seconda citation reale sul numero documento 8821 che **non contiene 5739**.
Il gate già esistente richiede che ogni citation contenga il valore completo:
fatto e binding rifiutati. Nessun allentamento di SOURCE per evitarlo.

Alternative recapiti/polizza sempre conservate senza scelta arbitraria, ma
polizza classificata ambiguous nelle prove iniziale1/successiva1 contro gold
conflicting. Sede operativa NA grounded solo in 2/4; altre due richieste NA
non calcolabili rifiutate. Quattro checkbox tipologia omesse in 4/4. Gold
immutato; firmatario/date non supportati non inventati. La corrispondenza
letterale non è accuratezza semantica completa.

## Costi, test e integrità

| Serie | Chiamate | Token input | Token totali | Somma AI s |
|---|---:|---:|---:|---:|
| iniziale | 7 | 257.881 | 398.747 | 631,07 |
| copertura | 5 | 262.963 | 366.439 | 462,23 |
| totale | 12 | 520.844 | 765.186 | 1.093,31 |

Tempo AI per chiamata 74,51–114,62 s; non durata E2E della compilazione.
Input per caso cresce vs V9: Minervino 45.964→47.109→47.317, Labirinto
16.623→16.856→17.064, Catanzaro 65.657→65.986→66.194. Nessun risparmio input,
costo monetario completo o miglioramento causale di latenza dimostrato.
Ragionamento, output, cache e copertura differiscono. Una chiamata resta una
scelta di architettura, non una promessa di risposta rapida.

Verifiche software (provider simulati, non valutazione semantica DeepSeek):

- 112 mirati iniziali /5,44 s; Ruff segnala I001 e tre E501, corretti.
- **417 mirati /19,74 s; 1.823 backend /121,23 s; Ruff e fixture check passati**
  prima della prima serie. Aggiunti 26 test su continuità, barriere, record,
  persona/ruolo/provenance, chunk e versioni; suite complete includono gli altri
  percorsi esistenti.
- Dopo il refinement del solo TASK: **417 mirati /19,19 s e Ruff passati**.
  Completa non ripetuta dopo quelle sole istruzioni; frontend invariato/non testato.
- 17 replay storici esatti V8/V9; 12 nuovi replay esatti con versione attesa V10;
  12 input/body ricostruiti identici ai rispettivi snapshot congelati.
- ID, range, sezioni, coordinate e testo dei cataloghi identici alla V9,
  eccetto versione/riferimenti di continuazione. Fonti e gold identici.
- Tutti i manifest/snapshot verificati, tutte le scritture null e provenance
  SOURCE mantenuta. Intero DB live/originali invariati fra inizio/fine delle due
  serie e controllo finale, senza reset manuali o server live attivo.

Failure degli helper registrate: import app mancante (zero API, rilanciato con
PYTHONPATH=.), prima invocazione test dalla directory sbagliata (nessun test),
stdout della seconda registrazione dice calls:7 per una stringa ereditata:
protocollo/jobs/loop contengono cinque chiamate e ne sono state fatte cinque.
Output Ruff iniziale solo nel tool, riepilogo durevole; nessun log non acquisito
viene presentato come disponibile. Questi errori non cambiano i raw dei modelli.

## Conservazione e ripresa

[JSON completo](benchmarks/2026-10-12-role-context.json),
[bundle grezzo delle due serie](benchmarks/2026-10-12-role-context-audit.tar.gz),
[checksum](benchmarks/2026-10-12-role-context-audit.tar.gz.sha256),
[verifiche finali](benchmarks/2026-10-12-role-context-final-checks.json),
[registro cronologico](../relazioni.md), [stato](../STATUS.md).

Grezzi anche in `backend/data/compilation-audit/role-context-20261012/` e
`role-coverage-20261012/`: originali/fixture/fonti/gold, prompt/schema, codice
congelato, risposte HTTP e JSON reali, usage/tempi, ogni candidate anche omesso,
validazioni, diagnosi, replay, controfattuale offline esplicitamente distinto,
log e controlli. Nessun database, configurazione privata o credenziale nel bundle.
L'archivio pubblico in Git evita che il solo push perda i dati ignorati.
Bundle: **431 file, 3.900.981 byte**, SHA-256
`dca4599fa9b17928a4799ef39dc4b548bac903dab024500fdc1835e1e8590066`.

**Prossimo punto da discutere prima di altro codice:** ridurre la dipendenza
dall'LLM per la classificazione value/conditional, mantenendo le condizioni
backend autoritative; stabilizzare quote e proprietà fra paragrafi e completezza.
Le prove sostengono il miglioramento del ruolo, non la chiusura di questi limiti.
Non attivare adapter scrivibile/V1 né reinterpretare i rifiuti attuali come
valori automaticamente utilizzabili. Commit piccoli autorizzati, nessun push.
