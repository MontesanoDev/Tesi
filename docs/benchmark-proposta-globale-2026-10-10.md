# Proposta unica DeepSeek: tre prove reali, 10 ottobre 2026

Esperimento successivo: [fatti e condizioni condivisi](benchmark-condizioni-globali-2026-10-10.md).
Le misure qui sotto restano quelle del primo contratto.

Il catalogo completo permette una proposta iniziale in una sola chiamata.
La riduzione dei passaggi è misurabile, ma **il prototipo non è pronto per
sostituire la V1 nella chat**. Una prova fallisce sul JSON; un'altra propone
un valore in una posizione la cui condizione è falsa. I controlli letterali
non sostituiscono la verifica semantica. Nessun dato sperimentale è diventato
RESOLVED, nessuna sessione live modificata, nessun DOCX generato.

## Condizioni della misura

Provider reale `deepseek-flash`, profilo locale `prova`, thinking disabilitato,
temperature 0,1, massimo 49.152 token output/300 secondi, nessun retry AI.
Il modello server dietro l'alias non è fissato. Originale del form 153:
SHA-256 `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`,
uguale al benchmark V1. Corpus documentale completo piccolo: 51 chunk,
58.512 caratteri, fonti caricate nel progetto + Company KB + General KB;
FORM e altri progetti esclusi, zero valori USER. Non è una prova del retrieval
su KB grandi né del browser/conversation workflow.

Codice congelato prima di ogni prova: `79e6950` per run 1, `2954034` per run 2/3.
Gli ultimi due input sono identici byte per byte. Nessuna modifica durante
le chiamate reali; i cambiamenti sono avvenuti tra le misure e dopo i test.

## Tempi, token e validità

| Prova | Chiamate | Input token | Output token | Totale token | Secondi AI | Risultato locale |
|---|---:|---:|---:|---:|---:|---|
| V1 storica: mappa + primi 12 | 7 | 83.798 | 32.943 | 116.741 | 141,14 | 5 RESOLVED, 267 PENDING |
| Globale 1: tutte le 307 posizioni | 1 | 62.588 | 28.929 | 91.517 | 71,72 | 156 grounded / 151 rifiutate |
| Globale 2: tutte le 307 posizioni | 1 | 68.204 | 33.295 | 101.499 | 81,24 | JSON non valido, rifiutato |
| Globale 3: tutte le 307 posizioni | 1 | 68.204 | 30.547 | 98.751 | 75,69 | 306 grounded / 1 rifiutata |

Il tempo V1 del service comprensivo di I/O era 151,25 secondi; la tabella
confronta invece i tempi delle chiamate AI. Quelli globali non comprendono conversazione,
stato di sessione o rendering. Non sono confronti fra due moduli completati.
La V1 recuperava sottoinsiemi delle stesse KB, il prototipo le include integralmente.
Il campione non permette percentili o stime affidabili di latenza/affidabilità.

Run 3 usa il **15,41% di token in meno** della baseline misurata e analizza
più posizioni; non è una stima del risparmio su una compilazione V1 completa.
I riferimenti espliciti ai paragrafi locali aumentano un poco l'input ma riducono
fortemente gli estratti FORM errati.

La cache è diversa: V1 33.536 token input in cache, run 1 zero, run 2/3 128.
Alle [tariffe ufficiali off-peak consultate](https://api-docs.deepseek.com/quick_start/pricing/)
(sabato: USD/milione 0,003 cache hit, 0,15 miss, 0,6 output), le tre chiamate
sperimentali costerebbero complessivamente circa **0,0855 USD**.
Run 3 circa 0,0285 USD contro 0,0274 della V1, ricalcolata alle stesse tariffe:
meno token non implica qui un costo monetario inferiore, per la cache diversa.
Stime da usage, non ricevute di addebito; prezzi e alias possono cambiare.

## Valori osservati nella prova 3

Questi sono valori **proposti**, controllati manualmente nel FORM e nelle SOURCE,
non campi RESOLVED persistiti. Le cinque proprietà della baseline restano corrette.

| Candidate | Requisito | Valore proposto | SOURCE effettiva |
|---|---|---|---|
| `t0.r5.c1` | Operatore economico | Mapi Ingegneria S.r.l. | visura, chunk -30 |
| `t0.r6.c1` | Forma giuridica | Societa a responsabilita limitata | visura, -30 |
| `t0.r7.c1` | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | visura, -30 |
| `t0.r9.c1` | Codice fiscale operatore | IT01234567890 | visura, -30 |
| `t0.r10.c1` | Partita IVA | IT01234567890 | visura, -30 |
| `t25.r0.c1` | Denominazione società di ingegneria | Mapi Ingegneria S.r.l. | visura, -30 |
| `t25.r4.c1` | Forma giuridica società di ingegneria | Societa a responsabilita limitata | visura, -30 |
| `t25.r4.c3` | Sede legale società di ingegneria | stesso indirizzo | visura, -30 |
| `t26.r0.c1` | Direttore tecnico | Ing. Elisa Romano | visura, -32 |
| `t26.r1.c1` | Qualifica direttore tecnico | Ingegnere | generalità, -45 |
| `t26.r3.c1` | Ordine professionale | Ordine degli Ingegneri di Bari | visura, -32 |
| `t26.r4.c1` | Numero albo | 8421 | visura, -32 |

Sono dati demo, incluso l'identificativo fiscale: il controllo preserva la fonte,
non ne certifica validità fiscale o legale. Anche telefono e ripetizione del
nominativo del direttore tecnico nella parte terza sono proposti con supporto.
La data di abilitazione resta missing, correttamente; non viene inventata.
Il sottoscrittore non è identificato automaticamente con l'amministratore.
La condizione della procura resta review, senza domanda diretta sul valore.

## Difetti osservati e comportamento del backend

1. **JSON globale 2 invalido**: una `}` di troppo dopo l'oggetto completo.
   Anche se il prefisso contiene 307 ID, tutta la risposta è rifiutata. Nessuna
   riparazione di parentesi, retry nascosto o accettazione del prefisso.
2. **Sede operativa, run 3**: il modello cita la sede coincidente con quella
   legale, ma il modulo chiede questa voce «se diversa dalla sede legale».
   Il valore esiste nella SOURCE; scriverlo in questo campo sarebbe errato.
   Il gate letterale passa: perciò l'esperimento mantiene sempre
   `semantic_review_required=true` e `written_value=null`.
3. **Ramo consorziata esecutrice, run 3**: quattro candidate `t40.*` esclusi
   soltanto perché l'operatore è società di ingegneria. La tipologia non
   dimostra l'assenza di questo ruolo di partecipazione. Esclusioni non supportate,
   da conservare in review; non vengono trasferite nello stato V1.
4. **Checkbox tipologia**: riconosciuta la società di ingegneria nelle SOURCE,
   ma nessuna selezione proposta; il modello confonde ancora la casella vuota
   con una selezione non attestata. Le checkbox sono catalogate, non scritte.
5. **Riferimenti**: quattro quote nel run 3 citano il chunk -30 anziché -32
   dello stesso file. Il validator ripristina il puntatore solo con quote
   integrale/univoca nel file fornito; conserva puntatore originale ed effettivo.
   Una proposta FORM cita un paragrafo esterno al contesto locale e resta
   rifiutata. Nessun allargamento a fonti o sezioni arbitrarie.

Valutazione manuale delle 15 proposte con valore del run 3: **14 valori supportati,
1 errore di applicabilità**; il telefono copre il recapito aziendale noto, non
inventa un cellulare. Quattro ulteriori esclusioni non supportate nel campione
controllato. Non tutte le 307 posizioni sono state revisionate semanticamente:
306 grounded non equivale a 306 decisioni corrette.

## Audit e prossimo passo

[Riepilogo JSON, quote e annotazioni](benchmarks/2026-10-10-compilation-global.json),
[prima misura](benchmarks/2026-10-10-compilation-global-run1.json) e
[contratto del prototipo](proposta-globale-compilazione.md).
Grezzi permanenti in `backend/data/compilation-audit/global-20261010-run1/`,
`global-20261010-run2/`, `global-20261010-run3/`. Contengono input/schema,
richiesta, risposta HTTP/testo, usage, validazione, originale e codice congelato.
Acquisizioni senza credenziali, DB o header Authorization.
Disponibili anche nel [bundle versionato](benchmarks/2026-10-10-global-proposal-audit.tar.gz)
con [checksum](benchmarks/2026-10-10-global-proposal-audit.tar.gz.sha256):
78 file verificati, inclusi replay/log e cataloghi della prima milestone.

Verifiche finali realmente eseguite: **74 test mirati, 1.470 test backend
completi**, Ruff completo, CLI help e diff check. Test software e storage/DB
temporanei distinti dalle tre prove semantiche reali. Frontend non modificato.
Regressione aggiunta per rifiutare output con testo/parentesi/JSON extra finali.

La misura giustifica continuare, **non ancora sostituire la V1**. Il prossimo
passo è rendere fatti e condizioni espliciti/condivisi nell'output, collegare ogni
assegnazione al proprio predicato e ridurre ripetizioni. Servono test negativi
per impedire i falsi positivi osservati, poi una nuova prova congelata prima
dell'adapter alla CompilationSession. Nessun reviewer AI per ogni gruppo e
nessuna modifica generale al RAG.
