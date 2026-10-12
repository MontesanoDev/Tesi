# Destinazioni inline: sette prove reali, 12 ottobre 2026

Il passo circoscritto è positivo: nei tre output Minervino non ricompare lo
slittamento telefono → civico, e-mail → telefono, PEC → e-mail. I recapiti sono
proposti nella destinazione corretta in tutte e tre le prove. La riga completa
compare soltanto in due prove: **posizione migliorata, copertura ancora variabile**.
Non è una compilazione completa né un'autorizzazione alla scrittura automatica.

## Cambiamento e garanzie

Catalogo V4 riusa `text_with_fields` già prodotto dal parser, con un marker per
ciascuno spazio. Aggiunge al candidate `slot_context.before/after`: massimo
120 caratteri per lato, fermandosi ai placeholder adiacenti. Testo originale,
ordine dei paragrafi, gerarchia, ID e coordinate strutturali restano disponibili.
Nessuna etichetta di dominio inventata dal backend; supporta etichette prima o
dopo lo spazio. Una sola chiamata globale, nessun batch o retry aggiunto.

Esempio reale Minervino, estratto della proiezione e del candidate:

```json
{
  "text_with_fields": "… n. [[p42.s2]], tel [[p42.s3]] …",
  "p42.s2": {
    "context_id": "paragraph:42",
    "range": [177, 192],
    "slot_context": {"before": " n. ", "after": ", tel "}
  }
}
```

L'ellissi serve soltanto a questo esempio; nel prompt sono presenti i paragrafi
completi. Nella prova 1 il modello propone `172/C` da una SOURCE per `p42.s2`,
citando `n. [[p42.s2]]`. Contratto V9 richiede un estratto contiguo con il solo
marker della destinazione e testo leggibile. Il backend ripristina il placeholder
originale, verifica il testo FORM e mantiene i gate SOURCE/ruoli/condizioni.
Citare il marker del telefono per il civico produce un rifiuto locale.

`destination_check` conserva marker, paragrafo, range e citazione ripristinata.
Celle vuote senza range e checkbox mantengono i controlli precedenti. Nessuna
modifica a parser generale, renderer, V1/chat/UI, retrieval o fonti autorizzate.
FORM non verifica valori; USER non viene trasformato in SOURCE. Nessun valore
viene promosso a RESOLVED o scritto nel Word da questo prototipo.

**Limite deliberato:** il marker prova la posizione della citazione, non la
relazione semantica fra proprietà, valore e destinazione. Un fatto telefono con
un marker del civico correttamente citato richiede ancora revisione; un test
esplicito impedisce di presentare il gate come validatore semantico completo.

Dopo le acquisizioni, commit `a0ce32b`, è stato aggiunto un controllo della
versione richiesta:
il runner che invia V9 rifiuta output V5–V8. Il validator conserva il replay
storico quando la versione attesa non viene specificata. Nessuna modifica al
prompt/schema/body: sette input e richieste ricostruiti identici e sette raw
rivalidati con lo stesso audit, senza ulteriori chiamate AI.

## Protocollo congelato

Codice durante tutte le acquisizioni: `d86953b`, contratto V9/catalogo V4.
Protocollo registrato prima delle API: Minervino 1, Labirinto 1, Minervino 2,
Labirinto 2, Minervino 3, Labirinto 3, Catanzaro 1. Chiamate seriali reali
`deepseek-flash`, thinking low, timeout 300 s, una chiamata per prova, zero retry.
Sette risposte complete HTTP 200/finish_reason stop, nessun timeout.

Minervino/Catanzaro usano gli stessi 17 chunk SOURCE congelati della serie
precedente: 13 Company KB e quattro General KB, nessuna fonte specifica di
progetto. Labirinto usa esclusivamente le sette fonti della fixture V1 invariata.
Gold e risultati attesi sono solo nell'analisi offline, mai nel prompt.
Documenti reali scelti esplicitamente per regressione/controllo, nessun sorteggio.

Corpus piccolo interamente disponibile: **non misura il retrieval FTS5/Qdrant**
né la latenza E2E della chat V1. Nessuna sessione creata, valore USER o DOCX
prodotto. Database live e originali invariati nei fingerprint prima/dopo questa
serie e dopo i test del controllo versione. Gli snapshot completi sono inclusi.

## Risultati di tutte le chiamate

"Grounded" nella tabella include valori e NA con grounding locale, **non** uno
stato RESOLVED o una certificazione semantica. Conditional conserva una proposta
SOURCE mentre l'applicabilità resta da verificare. Omissioni sono posizioni
strutturali non proposte, non un conteggio di campi obbligatori mancanti.

| Documento | Prova | Candidate | Record emessi | Grounded senza condizioni | Valori conditional | Omissioni | Secondi AI | Token totali |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Minervino | 1 | 267 | 14 | 0 | 9 | 253 | 104,61 | 70.335 |
| Labirinto | 1 | 55 | 21 | 13 | 6 | 34 | 58,55 | 30.814 |
| Minervino | 2 | 267 | 11 | 0 | 11 | 256 | 69,46 | 60.822 |
| Labirinto | 2 | 55 | 21 | 13 | 6 | 34 | 57,92 | 30.712 |
| Minervino | 3 | 267 | 11 | 0 | 9 | 256 | 110,31 | 70.731 |
| Labirinto | 3 | 55 | 21 | 13 | 6 | 34 | 49,63 | 28.824 |
| Catanzaro | 1 | 307 | 7 | 7 | 0 | 300 | 54,54 | 75.894 |

Totale **106 record**: 89 ipotesi di valore con grounding SOURCE (42 senza
condizioni e 47 conditional), quattro NA locali grounded, sei review con
alternative conservate, sette proposte personali bloccate dai gate precedenti.
Zero RESOLVED/scritture. Le 13 righe grounded di ogni Labirinto sono 12 valori
più una NA; le sette di Catanzaro sono sei valori più una NA.

### Minervino: errore di destinazione e copertura

| Candidate | Destinazione | Valore SOURCE | Prove con proposta corretta |
|---|---|---|---|
| `p42.s0` | provincia | BA | 1 e 3 |
| `p42.s1` | via | Via Giovanni Amendola | 1 e 3 |
| `p42.s2` | civico | 172/C | 1 e 3 |
| `p42.s3` | telefono | +39 080 000 2040 | 1, 2 e 3 |
| `p42.s4` | e-mail | segreteria@mapi-ingegneria.demo | 1, 2 e 3 |
| `p42.s5` | PEC | mapi.ingegneria@pec.demo | 1, 2 e 3 |

Nella precedente prova 2 i tre recapiti erano slittati di una posizione; nella
precedente prova seriale 4 erano già corretti. Qui **6/3/6** proposte corrette
nella riga, nessuno slittamento osservato, ma tre componenti dell'indirizzo omesse
nella seconda prova. Questo non dimostra che l'errore sia impossibile in futuro.

Restano sette proposte direttore bloccate complessivamente nelle prove 1/3:
ruolo/soggetto ereditato dai paragrafi precedenti non supera i gate letterali.
Nella prova 2 quei dati sono omessi. Non abbiamo modificato tali gate.
Due proposte per `p41.s1` usano l'indirizzo completo dove il blocco successivo
richiede componenti separati: granularità da rivedere.

Ulteriore limite acquisito: nella prova 2 `p16.s0` contiene correttamente l'e-mail
ordinaria, ma la quote è `[[p16.s0]] P.E.C.`. L'etichetta e-mail è nel paragrafo
precedente; P.E.C. descrive lo spazio successivo. Il marker è corretto, la quote
isolata è semanticamente debole. Il report conserva questa anomalia e il valore
resta review-only: il nuovo gate non viene presentato come soluzione completa.

### Labirinto V1: confronto congelato

**18/22 corrispondenze letterali valore/SOURCE in tutte e tre le prove**, contro
17/22 nell'ultima acquisizione V8. Non è una percentuale di accuratezza semantica.
I cinque dati societari restano corretti; nome Giulia Serra, qualifica, Ordine
degli Ingegneri di Ancona e numero 5739 sono proposti separatamente in 3/3.
La separazione ordine/numero è un miglioramento osservato, non una correzione
specifica della logica dell'albo. Quattro checkbox di tipologia restano omesse.

Due recapiti alternativi e due polizze incompatibili rimangono review separate,
senza selezione arbitraria. La condizione locale della sede operativa è falsa
in 3/3 e la proposta NA non contiene valore. Firmatario e data di abilitazione
non documentati non vengono inventati. Il gold non è stato adattato agli output.

### Catanzaro: controllo dei cinque dati

| Candidate | Requisito | Valore proposto con SOURCE |
|---|---|---|
| `t0.r5.c1` | Operatore economico | Mapi Ingegneria S.r.l. |
| `t0.r6.c1` | Forma giuridica | Societa a responsabilita limitata |
| `t0.r7.c1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia |
| `t0.r9.c1` | Codice fiscale operatore | IT01234567890 |
| `t0.r10.c1` | Partita IVA | IT01234567890 |

Provenance e citazioni/chunk sono nel JSON completo. Sono ipotesi grounded,
**non session fields RESOLVED**. Il campo composito Cellulare + Telefono riceve
solo il telefono documentato: resta incompleto semanticamente. Sede operativa
proposta NA sulla clausola locale. Ramo società di ingegneria/direttore omesso
in questo singolo controllo: copertura inferiore alle prove precedenti.

## Token, tempi e verifiche

**368.132 token osservati**, 505,02 s AI sommati (8 min 25 s), non durata E2E.
Input per prova: Minervino 45.964 contro 39.792 precedenti; Labirinto 16.623
contro 16.249; Catanzaro 65.657 contro 64.485. Il contesto locale aumenta
l'input: **nessun risparmio di token input dimostrato**. Output, ragionamento,
cache e copertura cambiano; non attribuire causalmente al gate i tempi inferiori.
Non è stata calcolata una spesa monetaria completa.

Verifiche software finali: **391 mirati / 18,40 s e 1.797 backend / 119,09 s passati**. Ruff backend, fixture V1
`--check`, diff check, undici replay storici, sette replay V9 con versione
attesa, ricostruzione identica dei sette body/input e controlli strutturali.
ID/range/sezioni e testo originale ordinato invariati per tutti e tre i moduli.
Frontend/lint/build/browser non eseguiti: frontend e contratti API invariati.

Failure intermedie conservate: due test sul ripristino dei placeholder con
oggetti Word non testuali, import order Ruff e assertion rimasta al catalogo V3.
Il ripristino usa ora il placeholder autoritativo del parser, senza modificarlo.
Il controllo finale V9 ha rilevato un mock V5 del runner non aggiornato;
prima modifica applicata alla fixture sbagliata, poi corretta e suite ripetute.
Sono failure software, non risposte DeepSeek scartate o nascoste.
Un controfattuale offline applica i marker alle tre vecchie citazioni sbagliate
e verifica il loro rifiuto: **non** è una nuova prova AI o riparazione del modello.

## Artefatti e prossimo punto

- [JSON completo: tutte le posizioni, proposte, audit e review](benchmarks/2026-10-12-slot-anchors.json).
- [Acquisizioni complete](benchmarks/2026-10-12-slot-anchors-audit.tar.gz) e
  [checksum](benchmarks/2026-10-12-slot-anchors-audit.tar.gz.sha256).
- [Verifiche finali](benchmarks/2026-10-12-slot-anchors-final-checks.json).
- [Registro degli esperimenti](../relazioni.md) e [stato](../STATUS.md).

Bundle: **259 file / 2.066.565 byte**, SHA-256
`414f43a52018547d3e317dc784910b2c0565074684e115a15f347d70abd13fd7`. Include protocolli, input e fonti congelate, originali,
codice usato nelle chiamate, prompt/schema/body, raw/HTTP, usage/tempi, audit,
review di tutti i 106 record, replay e log/failure software; niente DB/config
privata/chiave API/bytecode. Copia locale in
`backend/data/compilation-audit/slot-anchors-20261012/`.

**Prossimo passo da discutere prima di implementare:** preservare il ruolo e
l'etichetta semantica fra paragrafi/sezioni, valutare applicabilità e associazione
soggetto senza indebolire SOURCE. Il primo passo sulla posizione ha risultati
soddisfacenti e una baseline recuperabile; non attivare ancora il prototipo nella
chat né collegarlo al renderer sulla sola base di questo benchmark.
