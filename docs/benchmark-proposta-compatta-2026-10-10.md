# Proposta globale compatta: prove reali del 10 ottobre 2026

**Esito: non attivare nella chat.** Implementati contratto compatto, collegamento
esplicito delle proprietà e inventario delle condizioni, senza regole specifiche
per bando/azienda. L'output finale è più breve e contiene fatti professionali
separati, ma **tutte le sei risposte sono state rifiutate integralmente**.
Non è dimostrata una compilazione utilizzabile o una maggiore correttezza.

La V1 di produzione, RAG, chat, parser e renderer sono invariati. Nessuna sessione
modificata, nessun valore USER, nessun DOCX generato. Originale invariato in
ogni prova. Benchmark reale DeepSeek, separato dai test software simulati.

## Protocollo e misure

- Originale upload 153, `domanda-partecipazione.docx`, SHA-256
  `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
- Stesso catalogo: 307 candidate (279 testo, 28 checkbox), 324 paragrafi non vuoti.
- Stesse 51 SOURCE documentali ammesse: progetto corrente e Company/General KB,
  ruoli/scope conservati. Nessun FORM come prova fattuale, nessun USER/artefatto.
- Sei esperimenti indipendenti, **una sola chiamata ciascuno**, zero retry o
  riparazioni. Thinking disattivato. Non sono sei chiamate della stessa compilazione.
- Codice congelato nelle coppie 1–2 (`c2ec520`), 3–4 (`0972077`), 5–6 (`bb41dcc`).
  Input byte per byte identico dentro ciascuna coppia; catalogo/fonti identici
  anche rispetto al precedente contratto 2. Modifiche solo fra coppie concluse.

| Prova | Contratto | Secondi AI | Input token | Output token | Totale | Rifiuto |
|---|---|---:|---:|---:|---:|---|
| 1 | 3 iniziale | 126.05 | 70,223 | 49,152 | 119,375 | Troncato a 49.152 output |
| 2 | 3 iniziale | 87.56 | 70,223 | 36,698 | 106,921 | 304 fields oltre budget, ID extra |
| 3 | 3 ristretto | 29.21 | 70,419 | 11,204 | 81,623 | Mappa inversa incoerente |
| 4 | 3 ristretto | 39.77 | 70,419 | 15,698 | 86,117 | Mappa inversa incoerente |
| 5 | 4 canonico | 46.73 | 70,486 | 18,164 | 88,650 | ID mancanti/inventati |
| 6 | 4 canonico | 46.88 | 70,486 | 18,330 | 88,816 | ID mancanti/sovrapposti |

Usage e durata sono quelli reali, non stime da caratteri. Le prove 2/4/6 hanno
cache input elevata; le altre cache miss. Ultime due: ~47 secondi e ~88.700 token,
rispetto a 76,01 secondi/99.462 token nella precedente prova V2 run2:
**circa −38% tempo, −11% token totali, −40% output** nel campione.
Il confronto riguarda risposte con contratti diversi e rifiutate, non una
compilazione riuscita; deferred non equivale a interpretazione completa.
Non è una stima del risparmio di produzione né della qualità dei modelli.

Totale di questi sei esperimenti: **571.502 token, 376,20 secondi AI**. Nessuna
stima monetaria nuova. Il totale comprende anche gli esperimenti falliti.

## Cause e correzioni misurate

1. Contratto 3 iniziale: il compito sui fatti viene interpretato come catalogo
   dell'intera KB. La prima risposta enumera almeno 290 fatti completi nel
   prefisso e termina troncata. Il prefisso è solo diagnostico, mai validato.
   La seconda restituisce 304 fields, inclusi 280 review, invece di usare la
   lista compatta; contiene anche `p188.s0`, non presente nei candidate.
2. Contratto 3 ristretto: facts solo referenziati e fields soltanto value/NA;
   tutto il resto deferred. Rifiuto degli orfani, limiti espliciti, JSON compatto.
   Output ridotto a 11.204/15.698 token. Il modello però confonde la mappa
   paragrafo-clausola con lo scope delle clausole: 175/173 incongruenze nella
   mappa duplicata. Risposte interamente rifiutate, non riscritte dal backend.
3. Contratto 4: origine dichiarata soltanto in `condition.form`, mappa inversa
   derivata dal backend, quote verificate. Ricevuta di esame dei paragrafi e
   lista degli incerti separate. Elimina la ridondanza, ma espone il problema
   seguente: copertura degli ID instabile e paragrafi confusi con field.
   Prova 5 omette `t32.r4.c0/c1`, inventa `p164.s0` e `paragraph:188` in fields.
   Prova 6 omette gli stessi due ID e mette tutti i 12 field di tabella 0 sia
   in fields sia in deferred. Inoltre scope con paragrafi al posto di candidate.

Non si è allentata la copertura per far passare il benchmark. Nessun ID viene
indovinato, nessuna destinazione nuova viene creata, nessun output viene riparato.
I dettagli delle incoerenze e gli output completi sono conservati nel bundle.

## Valori e condizioni: osservazioni semantiche

Nelle due ultime risposte i cinque dati societari sono proposti correttamente,
con SOURCE Company KB `generalita-mapi.md`, chunk `-43`:

| Candidate | Proprietà | Valore proposto | Accettazione |
|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | Risposta globale rifiutata |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | Risposta globale rifiutata |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | Risposta globale rifiutata |
| t0.r9.c1 | Codice fiscale | IT01234567890, demo | Risposta globale rifiutata |
| t0.r10.c1 | Partita IVA | IT01234567890, demo | Risposta globale rifiutata |

Nessuno di questi è RESOLVED del nuovo motore. La stabilità della produzione V1
resta storica e intatta, non è stata rimisurata con nuove sessioni in questo intervento.

Le proposte del direttore tecnico sono ora separate: `Ing. Elisa Romano`,
`Ingegnere`, `Ordine degli Ingegneri di Bari`, **8421** (t26.r0/1/3/4.c1).
Miglioramento osservato rispetto al profilo completo riusato per tutti i campi;
non basta ad approvare assegnazione e ramo. Date non documentate non diventano
dati disponibili. Prova 5 ha anche disposition=value senza fact_id per alcuni
campi: è invalida, non un dato risolto.

Restano errori semantici concreti: amministratore inferito come sottoscrittore
della pratica; sede operativa proposta nonostante richiesta «se diversa» e
SOURCE di coincidenza; dati aziendali copiati nel ramo consorziata esecutrice
senza prova di quel ruolo; REA scambiato con numero/data CCIAA in prova 4.
Le condizioni ora sono presenti (24/19 nelle ultime due risposte), ma sono tutte
`semantic`: **non sono esiti di applicabilità verificati**. Il modello non usa
same/different per calcolare la coincidenza delle sedi. Nessuna condizione
semantica viene trasformata dal backend in vero/falso autodichiarato.

Prova 6 propone anche «non documentati»/«non disponibili» come valori. Dopo la
chiusura di tutti i benchmark, esteso il guard generico alle forme plurali
(commit `cc0485e`), con due regressioni software. Non è una patch per procura
o CCIAA e non modifica RAG/V1. **Non è stata fatta un'altra chiamata DeepSeek
su questo ritocco**; gli audit mantengono il codice davvero usato.

Le annotazioni manuali campionano 18 posizioni per risposta completa, non tutte
le 307. I fatti/proposte grezzi vengono mostrati come tali: la validazione per
field non è stata raggiunta, perché ogni envelope è rifiutato prima.

## Garanzie e limiti

- FORM prova richieste/condizioni; SOURCE è necessaria per ogni valore; USER
  non può entrare nel bucket SOURCE. Scope/categoria/chunk/file conservati.
- Identità della proprietà fra field e fact obbligatoria; fatto generico
  composito non riusabile per proprietà differenti. La classificazione del
  modello può comunque sbagliare: non è una prova semantica indipendente.
- Condizioni locali collegate dal backend anche se omesse nell'assegnazione;
  false/unknown impediscono valori e NA non supportate. Scope non locale resta
  da valutare. Ricevuta dei paragrafi non prova completezza semantica.
- Posizioni deferred ancora da interpretare, non automaticamente missing,
  obbligatorie, decorative o nuove domande all'utente.
- Tutte le proposte non scrivibili, zero RESOLVED, nessun verdetto V1 inventato.
  Checkbox riconosciute nel catalogo, nessuna nuova selezione/scrittura accettata.
- Limiti: 400 candidate, 128 facts referenziati/condizioni/fields, 2.048 paragrafi,
  96 chunk/100.000 caratteri SOURCE, 350.000 input, 49.152 output token/300 secondi.
  Oltre budget rifiuto, niente tagli silenziosi, loop o reviewer aggiuntivi.

## Verifiche e archivio

Controlli finali realmente eseguiti: **148 mirati, 1.544 backend completi**,
Ruff, CLI help con PYTHONPATH e diff check. DB/storage temporanei. Frontend
invariato, non rieseguito. Controlli intermedi e fallimenti software conservati
separatamente; non presentati come qualità semantica DeepSeek.
Nessuna migrazione o reindicizzazione, nessun push.

- [Usage, errori, annotazioni e confronto JSON](benchmarks/2026-10-10-compilation-global-compact.json).
- [Bundle completo](benchmarks/2026-10-10-global-compact-audit.tar.gz) e
  [checksum](benchmarks/2026-10-10-global-compact-audit.tar.gz.sha256).
- Grezzi permanenti `backend/data/compilation-audit/global-compact-20261010-*`:
  input/schema/request, HTTP e uso effettivo, testo completo quando disponibile,
  codice congelato, originali copiati, manifest, diagnostica e controlli.
  Run1 non ha response.txt: il trasporto ha rifiutato l'output troncato, il raw
  HTTP resta completo. Nessuna validazione per field è stata raggiunta.
- Bundle versionato: **142 file, 1.489.411 byte**, senza DB/configurazioni/credenziali;
  trasportabile con Git;
  i grezzi locali da soli restano esclusi. Checksum e manifest verificati.

Prossimo punto **da discutere prima del codice**: eliminare dal modello altre
ripetizioni di informazioni già autorevoli nel backend, soprattutto partizioni
degli ID, e rappresentare lo scope delle condizioni con riferimenti strutturali
reali senza confondere paragrafi e campi. Lasciare sempre irrisolte le posizioni
non assegnate; non reinterpretare ID inventati né attivare l'adapter prima di
un miglioramento semantico dimostrato. Evitare altri reviewer/catene per batch.
