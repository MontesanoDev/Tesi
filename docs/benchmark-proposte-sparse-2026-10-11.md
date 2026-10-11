# Proposte sparse: inventario nel backend — 11 ottobre 2026

**Risultato:** nelle due prove finali il JSON non viene più rifiutato in blocco
per la contabilità degli ID. Le assegnazioni sono validate indipendentemente:
9/8 proposte grounded conservate, 40/75 rifiuti locali, tutte le altre posizioni
ancora da verificare. I cinque dati societari principali hanno valori SOURCE
corretti in entrambe le prove. **Non è ancora una compilazione utilizzabile:**
restano errori di soggetto/applicabilità anche fra le proposte grounded.

Quattro esperimenti indipendenti, una chiamata DeepSeek ciascuno. Non sono
quattro chiamate dello stesso workflow. Nessun retry, USER, session write o
DOCX generato. V1/chat/RAG/parser/renderer invariati, originali invariati.

## Modifica e invarianti

Il precedente contratto 4 imponeva che l'IA ripetesse un inventario esatto di
candidate assegnati/rinviati e paragrafi letti. Anche errori su una posizione
facevano rifiutare la risposta prima del controllo dei valori.

Il contratto sperimentale 5 restituisce solo `fields`, `facts`, `conditions`
e l'eventuale incertezza FORM. Il backend mantiene l'inventario dell'originale:
posizione omessa = REVIEW_REQUIRED/non valutata, senza valore/label fabbricati,
non missing, obbligatoria, decorativa o non applicabile per default.

- Nessuna partizione `fields`/`deferred` o ricevuta di lettura da ricopiare.
- Scope delle condizioni `{kind,id}`: candidate, paragraph, table, section
  realmente presenti. Il backend deriva le posizioni coinvolte; paragrafo o
  tabella non possono diventare destinazioni scrivibili. Un paragrafo non
  estende automaticamente il proprio scope ai paragrafi successivi; una sezione
  strutturale richiede outline Word reale. Scope semantico non locale ancora
  unknown. Nessuna regola specifica per azienda, bando o nomi dei campi.
- Assegnazione invalida/ID inventato: quarantena locale. Fatto/condizione
  invalida: dipendenze riconoscibili bloccate, proposte indipendenti conservate.
  Anche una condizione malformata resta collegata all'origine/target riconoscibili.
  Fatti orfani segnalati e inutilizzati, mai trasformati in assegnazioni.
- Schema finale value/NA separato. Per value sono obbligatori `fact_id` e
  `property` non null; per NA nessun valore fattuale. Proprietà, quote FORM
  locali, quote/valori SOURCE letterali, ruoli/scope/provenance e condizioni
  false/ignote continuano a essere controllati.
- JSON troncato, chiavi duplicate, envelope o budget invalidi restano rifiuti
  globali. Non viene riscritto/riparato l'output grezzo per farlo passare.
- Tutto resta `semantic_review_required=true`, `written_value=null`,
  **RESOLVED=0, writes=0**. Grounding non dimostra proprietà/soggetto/ramo.
  FORM non verifica valori e USER non entra nel corpus SOURCE di questa prova.

## Protocollo congelato e budget

Originale upload 153 `domanda-partecipazione.docx`, SHA-256
`aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`.
307 posizioni, 279 testo e 28 checkbox, 324 paragrafi non vuoti. Catalogo e
51 SOURCE identici alle precedenti prove compatte: 34 progetto, 13 Company KB,
4 General KB. Filtri del repository e rilettura invariati; nessun altro progetto,
FORM, artefatto o valore USER nel corpus fattuale.

Prove 1–2 sul commit `7190d2d`; prove 3–4 sul commit `46128f5`. Dentro ogni
coppia input/request byte per byte identici. Codice modificato solo dopo la
conclusione della prima coppia; nessuna modifica durante la seconda coppia.
Manifest verificati e hash di catalogo/SOURCE confrontati fra tutte le prove
e con il precedente contratto 4. Copia SQLite temporanea in sola lettura,
nessuna modifica del database live, delle sessioni o dei documenti originali.

Limiti finali: 400 posizioni/proposte, 128 fatti, 128 condizioni, 96 SOURCE,
100.000 caratteri SOURCE, 350.000 caratteri input, 500.000 caratteri risposta,
49.152 token output e 300 secondi. Una chiamata senza thinking/retry/reviewer.
Il solo limite record è passato da 128 alle 400 posizioni strutturali già ammesse;
non è un obiettivo di output. Budget token/corpus/tempo invariati.

Il profilo salvato riporta context_window=32768, registrato separatamente;
non è la misura della finestra effettiva del provider. Token da usage reale,
nessuna conversione caratteri→token e nessuna stima monetaria nuova.

## Risultati reali

| Prova | Secondi AI | Input token | Output token | Totale | Risultato |
|---|---:|---:|---:|---:|---|
| 1 | 58,43 | 69.322 | 23.129 | 92.451 | Rifiuto globale: 256 fields > 128 |
| 2 | 43,34 | 69.322 | 17.009 | 86.331 | Rifiuto globale: 165 fields > 128 |
| 3 | 20,26 | 69.657 | 6.954 | 76.611 | 9 grounded, 40 rifiuti locali, 258 non valutati |
| 4 | 31,00 | 69.657 | 11.503 | 81.160 | 8 grounded, 75 rifiuti locali, 224 non valutati |

La prima coppia espone una seconda incoerenza del contratto: il modello
produce 249/126 record value con fact_id null. Il precedente schema lasciava
fact_id opzionale pur richiedendolo nel prompt; il tetto 128 impediva di
arrivare ai rifiuti locali. Nella prova 1 mancano anche le cinque proposte
societarie nonostante le SOURCE disponibili; nella prova 2 sono presenti.
Entrambi i fallimenti restano archiviati integralmente, senza replay spacciati
per nuove risposte. Raffinamento dello schema e del tetto solo dopo la coppia.

Nelle due prove finali: 49/83 fields, nessun ID inventato, nessun value senza
fact_id. 16/19 fatti proposti, 14/14 grounded; 9/19 condizioni tutte grounded
nel FORM ma **tutte operator=semantic/result=unknown**, non applicabilità
verificata. Nessuna condizione calcolabile falsa inventata dal backend.

Rifiuti locali:

| Motivo | Prova 3 | Prova 4 |
|---|---:|---:|
| Applicabilità sconosciuta | 24 | 12 |
| NA senza condizione calcolabile falsa | 14 | 59 |
| Fatto SOURCE assente/rifiutato | 2 | 3 |
| Proprietà dell'assegnazione/fatto diverse | 0 | 1 |

Nella prova 3 sono rifiutati i fatti «non disponibile» per nascita/CF del
sottoscrittore. Nella prova 4 anche la combinazione REA/data, la tipologia
riscritta e la partecipazione «NO» non presenti letteralmente nelle quote.
Non diventano valori perché il modello li ha proposti.

Totale quattro esperimenti: **336.553 token e 153,03 secondi AI**, includendo
i fallimenti. Solo coppia finale: 157.771 token/51,26 s; media 78.885,5 token
e 25,63 s. Rispetto alle due precedenti prove compatte (entrambe rifiutate):
**−11,10% token totali, −49,42% output, −45,24% tempo AI** nel campione.
Cache diversa, risposte stocastiche e contratti diversi: non è una stima del
costo/tempo di una compilazione completa o un risparmio dimostrato in produzione.

## Verifica semantica manuale

Ispezionate tutte le 9/8 proposte grounded delle prove finali, oltre ai 16
candidate campionati per ciascuna risposta. La verifica umana non è un verdetto
del backend né abilita scrittura. Sei assegnazioni appropriate in entrambe
le prove: i cinque dati sotto e il recapito telefonico +39 080 000 2040.

| Candidate | Proprietà | Valore proposto | SOURCE prova 3 | SOURCE prova 4 |
|---|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | -43 / file -7 | -30 / file -9 |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | -43 / file -7 | -30 / file -9 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | -43 / file -7 | -30 / file -9 |
| t0.r9.c1 | Codice fiscale | IT01234567890 | -43 / file -7 | -30 / file -9 |
| t0.r10.c1 | Partita IVA | IT01234567890 | -43 / file -7 | -30 / file -9 |

Entrambi i documenti sono Company KB, role=source/scope=global/category=company:
`generalita-mapi.md` e `visura-mapi-ingegneria-simulata.pdf`. Valori demo;
quote letterali, puntatori effettivi/citati, hash e provenance nell'audit.
Questi sono **GROUNDED_PROPOSAL, non RESOLVED** della CompilationSession.

Errori semantici ancora presenti fra i grounded:

- Entrambe: `t0.r0.c1` Ing. Luca Ferri e `t0.r3.c1` Amministratore unico.
  La SOURCE attesta persona/carica aziendale, non chi firma questa pratica.
- Prova 3: `t0.r8.c1` sede operativa uguale alla sede legale, nonostante FORM
  «se diversa». La clausola viene omessa dall'inventario del modello; il
  validator letterale non può provare la completezza semantica delle condizioni.
  Prova 4 propone NA ma senza condizione calcolabile: correttamente rifiutata.

Quindi 3/2 assegnazioni semanticamente improprie fra le 9/8 grounded. È la
ragione concreta per cui **non attivare ancora session adapter/chat/export**.

Direttore tecnico: nome Ing. Elisa Romano, qualifica Ingegnere, Ordine degli
Ingegneri di Bari e numero **8421** sono fatti atomici proposti da SOURCE in
entrambe le risposte finali, ma assegnazioni rifiutate per applicabilità del ramo
ancora unknown. Data di abilitazione non proposta. È un limite conservativo
esplicito, non assenza di dati nella KB. Le esclusioni di sezioni e il ruolo di
consorziata non sono accettati dalla sola tipologia aziendale. Le checkbox
restano soltanto catalogate/non scrivibili; nessuna selezione esportata.

## Verifiche software e acquisizioni

Primo passo: **185 mirati, 1.591 backend completi**, Ruff/help/diff.
Schema raffinato finale: **188 mirati, 1.594 backend completi** (101,60 s),
Ruff completo, CLI help con PYTHONPATH e diff check. Regressioni generiche su
omissioni, ID inventati, rifiuti locali, condizioni invalide/false/ignote,
proprietà, fatti mancanti, scope tipizzati, source/progetto, metadati e casi
oltre 128 record. Provider simulati nei test software, DB/storage temporanei;
non sono misure di qualità DeepSeek. Primo Ruff ha segnalato una riga lunga,
corretta e ricontrollata. Frontend invariato, test frontend non rieseguiti.

- [Riepilogo JSON e annotazioni](benchmarks/2026-10-11-compilation-global-sparse.json).
- Grezzi locali permanenti `backend/data/compilation-audit/global-sparse-20261011-run{1,2,3,4}/`:
  input/schema/request, response/raw HTTP/usage, metriche, codice congelato,
  originale, manifest; validation solo per le risposte arrivate al gate locale.
- Log distinti `global-sparse-20261011-checks/`, `global-sparse-20261011-refined-checks/`;
  analisi e annotazioni `global-sparse-20261011-analysis/`.
- [Bundle completo versionato](benchmarks/2026-10-11-global-sparse-audit.tar.gz)
  e [checksum SHA-256](benchmarks/2026-10-11-global-sparse-audit.tar.gz.sha256).
  Nessuna credenziale, configurazione privata o database. I grezzi esclusi da
  Git sono anche nel bundle, così un futuro push conserva la diagnosi.
  Archivio: 93 file, 986.403 byte, confrontati byte per byte con i grezzi locali;
  verificata l'assenza della chiave reale configurata prima dell'archiviazione.

Nessuna migrazione/reindicizzazione. Nessun push. Prossimo punto da discutere:
accettazione semantica di soggetto/ruolo e applicabilità sulla mappa globale,
senza tornare a reviewer per gruppi o allentare la necessità di SOURCE.
La contabilità strutturale ora resta nel backend; la correttezza semantica
ancora incompleta impedisce di congelare e promuovere il nuovo motore.
