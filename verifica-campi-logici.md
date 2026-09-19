# Correzioni dei campi logici e dei recapiti

18 settembre 2026. Compilatore `docx-fields-v6-logical-fields`.

## Cosa e cambiato

- Un'unica area con puntini ASCII ed ellissi Unicode genera un unico campo,
  anche quando attraversa piu run Word. Restano distinti etichette, date,
  tabulazioni e interruzioni di riga. `prov.` e `n.` non perdono il punto.
- I campi riconosciuti come email/PEC richiedono un recapito completo, con
  sintassi verificata da `email-validator` senza DNS o normalizzazione del dato.
  Non basta citare un frammento come `pec`, ne un indirizzo valido ritagliato da
  uno piu lungo. Il tipo ricavato dal modello Word non dipende dall'etichetta LLM.
- Gli errori di recapito possono usare l'unico tentativo mirato gia esistente.
  Se non corretti, restano bloccati e vuoti; gli altri campi sono conservati.
- Gli indirizzi esplicitamente partizionati (`___@___.___`) riconosciuti dal
  parser restano da compilare manualmente. Il writer non distribuisce un indirizzo
  tra piu pezzi e ripete i controlli sui campi tipizzati.

Nessuna regola di produzione usa il nome di Mapi, le coordinate di Minervino
o quelle di Catanzaro. Nessuna modifica a modello, retrieval o workflow.
Le vecchie compilazioni non vengono riscritte automaticamente.

## Come e stato verificato

**339 test backend e 78 frontend superati**, Ruff e `git diff --check` senza errori.
I test coprono marcatori misti, confini dei run casuali, date e separatori,
abbreviazioni, etichette in celle/colonne, recapiti invalidi e parziali,
blocco del writer, correzione riuscita e fallita. C'e una regressione sul DOCX
nativo di Minervino oltre alle fixture sintetiche indipendenti dal bando.

Eseguite anche **due nuove compilazioni DeepSeek**, una per modulo, senza
scegliere il risultato piu favorevole. Riutilizzati esattamente template, fonti
selezionate e istruzioni dai prompt registrati in precedenza. Hash e copertura
controllati; modello configurato invariato, restituito dal provider `deepseek-flash`.

Questa ripetizione chiama il compilatore reale con fonti congelate: non ripete
ingestion, route HTTP o persistenza del progetto. Nessun accesso al database
dell'app, modifica dei progetti o invio di candidature. Non e un benchmark.

| Osservazione | Minervino v6 | Catanzaro v6 |
|---|---:|---:|
| Celle + segnaposti candidati | 67 + 184 | 265 + 14 |
| Fonti selezionate / totali | 45 / 45 | 86 / 185 |
| Scritture effettive | 22 | 22 |
| Chiamate iniziali + correzioni | 8 + 1 | 9 + 0 |
| Token input + output | 429.927 | 668.181 |
| Tempo | 76,48 s | 87,18 s |
| Scritture fuori dal perimetro richiesto | 1 | 7 |

## Risultato concreto a Minervino

Nel ramo societario il Word contiene ora:

```text
prov. BA via/piazza Via Giovanni Amendola n. 172/C, tel +39 080 000 2040
e-mail segreteria@mapi-ingegneria.demo pec mapi.ingegneria@pec.demo
```

Ragione sociale senza marcatori residui; recapiti completi anche nell'anagrafica
iniziale. Nessuna scrittura nei paragrafi `p24` e `p37`, che nella prova precedente
contenevano recapiti spezzati. Il tentativo di correzione ha riparato una citazione
non letterale del direttore tecnico, non un'email. La correzione di email invalide
e verificata con i test controllati, non dimostrata da questa chiamata reale.

**Limiti ancora visibili:** `p38.s0` contiene Luca Ferri nel ramo dello studio
associato, escluso dalle istruzioni. In `p53` il valore dell'ordine professionale
tocca l'etichetta prestampata, gia priva di spazio prima del segnaposto. Non sono
state aggiunte spaziature arbitrarie, che potrebbero spezzare codici prestampati.

I 214 segnaposti iniziali diventano 184: quindi confrontare le precedenti
37 scritture con le nuove 22 non misura l'accuratezza. Anche le differenze nella
scelta dei rami possono dipendere dal modello non deterministico e dai gruppi
diversi; non attribuiamo al parser un miglioramento semantico dimostrato.

## Risultato concreto a Catanzaro

Il modulo in celle resta compilabile e il numero di candidati non cambia.
Persistono scritture fuori perimetro: `t9.r0.c1`, `t40.r4.c1`, `t40.r4.c3`,
`t40.r5.c0`, `t41.r1.c0`, `t41.r1.c4`, `t44.r1.c0`.
Alcune riguardano rami esclusi, altre dichiarazioni successive non richieste.
Citazioni autentiche non rendono corretta la collocazione del dato.

## Integrita e materiali

In entrambi i Word verificata la corrispondenza tra valori del report e scritture
effettive. Celle/paragrafi non interessati e parti ZIP diverse da
`word/document.xml` sono invariati; hash coerenti e avviso di bozza presente.
**Non verificata la resa visiva/paginazione in Word o LibreOffice.**

- [Word Minervino](backend/data/compilation-audit/20260918-minervino-v6-logical-fields/output/bozza.docx)
  e [report](backend/data/compilation-audit/20260918-minervino-v6-logical-fields/output/report.json).
- [Word Catanzaro](backend/data/compilation-audit/20260918-catanzaro-v6-logical-fields/output/bozza.docx)
  e [report](backend/data/compilation-audit/20260918-catanzaro-v6-logical-fields/output/report.json).
- Input, prompt/risposte per chiamata, consumi e `offline-analysis.json` nelle
  rispettive cartelle, gia escluse da Git.
- [Script di ripetizione](backend/scripts/replay_docx_audit.py), richiede
  `--live --audit <cartella-precedente> --output <nuova-cartella>`.

**Conclusione:** corretti difetti riproducibili di segmentazione e aggiunta una
barriera ai recapiti malformati. Restano applicabilita dei rami, attribuzione del
soggetto, completezza e revisione umana: non e una compilazione automatica certificata.
