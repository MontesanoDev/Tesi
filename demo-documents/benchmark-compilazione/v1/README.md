# Modulo labirinto — fixture di benchmark V1

Documento e fonti interamente fittizi, dedicati al nuovo compilatore globale.
Non usarli come dati aziendali reali, non importarli nella Company KB corrente.
Il runner legge direttamente i file; non occorre creare un progetto nel DB.

- [Modulo Word](modulo-benchmark.docx): originale congelato, 55 posizioni,
  44 testuali e 11 checkbox native, sia legacy sia content control.
- [Fonti](sources/): sette testi; [sources.json](sources.json) conserva identità,
  ruolo e scope. Cinque Company KB, una fonte progetto e una General KB.
- [Risultati attesi](gold.json): annotazioni autoriali di ogni posizione,
  indipendenti dalle risposte del modello. **Mai inviarlo all'AI.**
- [Manifest](manifest.json): SHA-256 di Word, fonti e annotazioni.
- [Fonte esclusa](excluded-sources.json): distrattore di un altro progetto.
  Serve al test di isolamento, non deve essere inserito nel corpus del modello.
- [Registro degli esperimenti](../../../relazioni.md).

## Cosa mette alla prova

Il documento mescola intestazioni Word autentiche con titoli solo in grassetto.
I rami 4.a/4.b/4.c/4.d non hanno outline: il loro significato deve essere ricavato
dal FORM, senza inferirlo dal nome di uno stile. Nome e cognome, denominazione
e numero albo si ripetono per soggetti differenti. Una tabella è annidata e
un'altra contiene celle unite. Istruzioni aggiuntive stanno nell'intestazione
e nel piè di pagina, conservati come contesto non scrivibile.

L'operatore di prova è Orione Tecnica S.r.l., società di ingegneria. Le fonti
identificano amministratore e direttore tecnico, ma non il firmatario della
specifica domanda. Non attestano procura, modalità di partecipazione, secondo
direttore, data di abilitazione, organigramma o ISO 9001. Il numero albo atteso
è **5739**; il numero 8821 nella stessa fonte identifica un documento diverso.

La sede operativa coincide esplicitamente con quella legale: il campo locale
«solo se diversa» non va riempito. Due recapiti senza priorità creano ambiguità;
due polizze di pari data con identificativi differenti creano conflitto. La
General KB descrive un'altra società, non prova fatti del richiedente. Una
firma protetta e uno spazio riservato all'ufficio non sono dati da inventare.

## Ground truth congelato

| Esito atteso | Posizioni |
|---|---:|
| Valore supportato e applicabilità pertinente (`RESOLVED`, obiettivo) | 22 |
| Non applicabile | 9 |
| Mancante nelle fonti consentite | 14 |
| Condizione da chiarire prima del valore | 6 |
| Ambiguo | 1 |
| Conflittuale | 1 |
| Firma manuale, non scrivere | 1 |
| Riservato all'ufficio, non scrivere | 1 |

I 22 valori comprendono **17 campi testuali e 5 scelte di tipologia**. Queste
ultime hanno un'esclusività espressa nel FORM, per lo stesso soggetto e ambito.
Gli esiti attesi non sono stati persistiti dal compilatore. Il prototipo
attuale mantiene zero RESOLVED e zero scritture; il benchmark deve rendere
visibili anche le sue false negative conservative, non aggirarle.

Il gold specifica soggetto, ramo, valore, fonti attese e casi critici. È scritto
prima della baseline. È una specifica autoriale, non una valutazione legale né
un giudizio prodotto dallo stesso modello che compila. Da revisionare quando
si estende il benchmark; cambiare scenario richiede una nuova versione.

## Comandi

Dalla directory `backend/`, verifica la fixture senza modificarla:

```bash
uv run --locked python scripts/create_compilation_benchmark.py --check
uv run --locked pytest -q tests/test_compilation_benchmark_fixture.py
```

Una prova reale, usando un profilo DeepSeek già configurato (sostituire
`prova` se il progetto che conserva il profilo ha un altro ID):

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_global.py \
  --fixture ../demo-documents/benchmark-compilazione/v1 \
  --profile-project prova \
  --output data/compilation-audit/labirinto-v1-NUOVO-RUN
```

Il runner usa il profilo solo per provider/modello/credenziali. Il corpus è
esclusivamente quello della fixture, senza DB di documenti o ingestion.
Ogni directory di output deve essere nuova: nessuna sovrascrittura di prove.
La chiamata è una sola, senza retry/reviewer; conservare anche i fallimenti.

Output: input e schema effettivi, request, risposta HTTP/raw, tempi e usage,
validazione, codice congelato, copia della fixture incluso gold solo per audit,
confronto `fixture-score.json` e manifest. Nessuna generazione DOCX/sessione.

## Interpretare le misure

Separare sempre proposta grezza, grounding locale e correttezza semantica.
Il confronto automatico verifica soltanto valore/booleano e ID SOURCE autoriali;
per NA confronta la disposition, **non** dimostra che la condizione sia provata.
Non misura da solo soggetto, completezza delle condizioni, confini dei rami o
entailment delle quote. La revisione di questi aspetti rimane esplicita.

Registrare nel registro: commit e versione fixture, hash input, provider,
thinking, numero chiamate, token/tempo, valori corretti, omissioni, proposte
improprie, differenza dopo i gate e revisione dei casi critici. Nessun valore
grounded diventa automaticamente RESOLVED. Turni USER e valori materializzati
non sono ancora misurabili dal prototipo e vanno indicati come non eseguiti.

Per confronti stabili ripetere tre volte a codice/input congelati; una o due
prove iniziali sono una baseline esplorativa, non una stima affidabile della
qualità. Conservare altri documenti come regressioni esterne: questa fixture
serve a isolare problemi, non dimostra generalizzazione ad ogni Word.

## Rigenerazione

Il generatore `backend/scripts/create_compilation_benchmark.py` costruisce
Word, fonti, gold e manifest in modo riproducibile. `--check` non scrive.
La rigenerazione senza `--check` è un'operazione esplicita sugli artefatti di
test, mai sugli originali dell'utente. Dopo una modifica semantica creare V2,
conservando V1 e i suoi risultati; non adattare il gold a una risposta AI.
