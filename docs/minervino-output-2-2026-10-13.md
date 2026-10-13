# Minervino: controllo di compilato(2) — 13 ottobre2026

Esaminato in sola lettura `domanda-iscrizione.compilato(2).docx`, presente nella
radice del repository. SHA256
`bd0da991ef7ff40833b41e9d14d3eeea323a415ed9815a6788a61fec34057952`.
È identico byte per byte alla generazione reale
`6cb97f7bc2784517919f3b99e4d021cc`, sessione
`a067b0abf83f4d948137728669879604`, ora versione7/GENERATED.
Non è il DOCX del replay privato della diagnosi precedente.

## Giudizio sul contenuto

**Buona bozza parziale per i dati disponibili.** Venti posizioni testuali
compilate con valori provenienti dalla Company KB, nessun valore USER inserito,
nessun valore aggiunto privo di SOURCE osservato. Non sono20 fatti distinti:
operatore, società e recapiti compaiono in più punti dello stesso modulo.

L’operatore economico è identificato correttamente come Mapi Ingegneria S.r.l.;
telefono, e-mail, PEC e partita IVA corrispondono alle fonti. Nel ramo societario
sono presenti denominazione, indirizzo, provincia, via, civico e recapiti.
Elisa Romano, qualifica Ingegnere, Ordine degli Ingegneri di Bari e numero8421
sono scritti nel blocco Responsabile della Progettazione/Direttore Tecnico
collegato alle società, senza essere trasferiti nei rami del professionista
singolo o degli studi associati. La qualità di società di ingegneria è stata
confermata dall’utente; i valori rimangono SOURCE.

I venti valori sono materializzati negli slot previsti. Ricostruiti tutti i
paragrafi dall’originale usando gli offset dei placeholder e i soli valori
presenti nel report: il testo corrisponde integralmente al DOCX ricevuto,
escluso l’avviso BOZZA iniziale. Zero spostamenti rispetto allo stato persistito,
zero testi aggiunti negli altri spazi. Le15 parti ZIP diverse da
word/document.xml sono identiche all’originale.

Questo verifica scrittura/provenienza; il controllo semantico del contesto
rileva comunque i difetti sotto. Nessuna percentuale di accuratezza: non c’è
un gold completo per questa candidatura. Checkbox escluse dall’intervento
come richiesto. Non è stata controllata la paginazione mediante Word/LibreOffice.

## Tre difetti circoscritti ancora presenti

1. **Comune della sede nella parte iniziale omesso pur essendo disponibile.**
   Risulta `con sede in ______ (BA)`. Il raw propone Bari per p15.s0, basato
   sulla SOURCE societaria. Il backend rifiuta la quote FORM `[[p15.s0]] (`
   con errore «Il solo marker non documenta la richiesta del campo».
   Il testo qualificante «con sede in» termina nel paragrafo precedente.
   È un falso negativo di ancoraggio della destinazione, non assenza di Bari
   dalla KB e non uno spostamento del renderer. Non corretto in questa revisione.

2. **Indirizzo completo troppo ampio per la suddivisione locale.** In p41.s1
   compare `Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia`, seguito da
   `prov. BA via/piazza Via Giovanni Amendola n. 172/C`.
   Tutti i dati sono sostenuti dalla stessa SOURCE; la struttura con provincia,
   via e civico separati suggerisce Bari nel primo spazio. Ridondanza semantica
   del valore proposto, già nota nella bozza precedente, non dato inventato.

3. **Separazione tipografica dell’Ordine.** Il testo contiene
   `iscritto all’Ordine/Collegio professionaleOrdine degli Ingegneri di Bari`.
   Valore e posizione corretti; manca uno spazio alla giunzione con il testo
   prestampato, che già nell’originale arriva direttamente ai puntini.
   Anche la giunzione `sezione ....della provincia` conserva il difetto originale.

## Parti vuote e informazioni effettivamente disponibili

Sottoscrittore, nascita, residenza, codice fiscale personale e carica restano
vuoti. La KB identifica Luca Ferri come amministratore unico, ma specifica
che ciò non determina chi firma una candidatura. Non è corretto riempire
automaticamente l’anagrafica del firmatario con l’amministratore o il direttore.
Il C.F. aziendale non deve diventare il C.F. personale dei soggetti.

I soci e gli altri soggetti dei rami alternativi non vengono inventati. La fonte
precisa che i nominativi descritti non sono l’elenco completo dei soci.
Per il direttore tecnico restano vuoti C.F. personale, sezione e data di
iscrizione all’Ordine: non risultano valori pertinenti nei testi aziendali
acquisiti. Il `dal` del modulo è la data relativa all’iscrizione professionale;
non va riempito con la data di iscrizione della società.

CCIAA/numero di iscrizione rimangono vuoti. È presente il REA simulato
BA-654321, ma la scheda precisa che non coincide automaticamente con il numero
di iscrizione al Registro delle Imprese. La data societaria14 marzo2019 non
risolve questi identificativi né la data dell’Ordine professionale.
Categorie, incarichi richiesti, persone incaricate, luogo/data e firma restano
scelte/dati della pratica; il documento non li inventa.

Non tutti i vuoti sono quindi errori. Allo stesso tempo la presenza del falso
negativo Bari impedisce di dire che ogni dato disponibile sia stato usato.
Le99 motivazioni di vuoto respinte nell’audit iniziale rimangono tali:
non provano assenza di dati e non sono99 campi pertinenti sicuramente mancanti.
Il report mantiene ready_for_submission=false e resolved=0: sono proposte
SOURCE accettate per una bozza parziale, non certificazione dell’intera domanda.

## Valori realmente scritti

| Candidate | Dato | Valore | Provenienza | SOURCE |
|---|---|---|---|---|
| `p14.s1` | Operatore economico | Mapi Ingegneria S.r.l. | SOURCE | generalita-mapi.md, chunk-43 |
| `p15.s1` | Provincia | BA | SOURCE | generalita-mapi.md, chunk-43 |
| `p15.s2` | Telefono | +39 080 000 2040 | SOURCE | generalita-mapi.md, chunk-44 |
| `p16.s0` | Indirizzo e-mail | segreteria@mapi-ingegneria.demo | SOURCE | generalita-mapi.md, chunk-44 |
| `p16.s1` | P.E.C. | mapi.ingegneria@pec.demo | SOURCE | generalita-mapi.md, chunk-44 |
| `p16.s2` | Partita IVA | IT01234567890 | SOURCE | generalita-mapi.md, chunk-43 |
| `p40.s0` | Denominazione/ragione sociale | Mapi Ingegneria S.r.l. | SOURCE | generalita-mapi.md, chunk-43 |
| `p41.s0` | P. IVA | IT01234567890 | SOURCE | generalita-mapi.md, chunk-43 |
| `p41.s1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | SOURCE | generalita-mapi.md, chunk-43 |
| `p42.s0` | Provincia | BA | SOURCE | generalita-mapi.md, chunk-43 |
| `p42.s1` | Via/piazza | Via Giovanni Amendola | SOURCE | generalita-mapi.md, chunk-43 |
| `p42.s2` | Numero civico | 172/C | SOURCE | generalita-mapi.md, chunk-43 |
| `p42.s3` | Telefono | +39 080 000 2040 | SOURCE | generalita-mapi.md, chunk-44 |
| `p42.s4` | E-mail | segreteria@mapi-ingegneria.demo | SOURCE | generalita-mapi.md, chunk-44 |
| `p42.s5` | PEC | mapi.ingegneria@pec.demo | SOURCE | generalita-mapi.md, chunk-44 |
| `p51.s0` | Nome e cognome | Ing. Elisa Romano | SOURCE | generalita-mapi.md, chunk-45 |
| `p52.s0` | Qualifica professionale | Ingegnere | SOURCE | generalita-mapi.md, chunk-45 |
| `p53.s0` | Ordine/Collegio professionale | Ordine degli Ingegneri di Bari | SOURCE | generalita-mapi.md, chunk-45 |
| `p53.s2` | Provincia dell'ordine | Bari | SOURCE | generalita-mapi.md, chunk-45 |
| `p53.s4` | Numero di iscrizione | 8421 | SOURCE | generalita-mapi.md, chunk-45 |

Tutte le prove utilizzate hanno role=source, scope=global, category=company:
generalita-mapi.md, chunk-43/-44/-45. Controllati quote letterali, valore nella
quote e hash del contenuto contro l’input realmente inviato al modello.
La conferma USER riguarda c_partecipazione, non sostituisce queste prove.

## Metodo e acquisizioni

Nessun cambio di codice, parser, renderer, RAG, UI o sessioni. Nessuna chiamata
provider, nessuna nuova generazione, nessun dato inserito. Confrontati DOCX
utente, originale, report, stato, input/raw e fonti realmente inviate.
Riutilizzata la verifica indipendente dei testi in
`docs/benchmarks/verify_text_coverage.py`; non viene invocato il writer per
produrre il testo atteso. Verificati invariati hash/versione della sessione,
originale e file ricevuto, oltre alla corrispondenza dell’originale su storage.

Non è un benchmark del modello né una suite software appena rieseguita.
Per questo controllo documentale: verifica XML/ZIP/fonti, integrità e diff check.
Originale SHA256
`25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c`.
Raw: `backend/data/compilation-audit/minervino-output-2-20261013/`.
[Acquisizioni](benchmarks/2026-10-13-minervino-output-2-audit.tar.gz),
[manifest e diagnosi](benchmarks/2026-10-13-minervino-output-2-manifest.json).
11 file/1.451.792 byte grezzi; SHA256 bundle
`32461e06fe6661352b34516f9f1f3d98fb08d54c342cfe6c101f5f5228abb8d3`.
Scansione credenziale, esclusione DB/chiavi e confronto byte dell’archivio passati.

Prossimo punto da discutere: recuperare l’ancoraggio dei campi a cavallo di
paragrafi e proporre componenti di indirizzo coerenti con gli spazi adiacenti,
conservando i gate SOURCE; separazioni tipografiche come rifinitura. Nessuna
implementazione avviata. Checkbox restano fuori dal presente giudizio.
