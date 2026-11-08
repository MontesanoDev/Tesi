# Strategia di generazione: quando usare le sezioni (22 ottobre 2026)

Analisi offline in sola lettura delle chiamate registrate. Zero chiamate LLM, nessuna modifica al
codice, nessuna adozione. Dati e script: `backend/data/compilation-audit/strategia-generazione-20261022-01/`.

## Stato confermato

- Le nuove sessioni ordinarie hanno solo il profilo V14 + K3.
- Il dialogo P3 corretto è una candidata sperimentale. Si attiva solo con
  `MAPI_DIALOGUE_REVISION=1`, come fanno i test.
- La generazione per sezioni è disattivata. Si attiva solo con `MAPI_GENERATION_REVISION=1`.
- Il DB live ha le stesse 29 sessioni, nessuna con flag P3.

## Dati

158 chiamate globali registrate, tutte con la stessa configurazione (deepseek-flash, ragionamento
basso, limite 49.152 token, contratto 12): 132 monolitiche su 6 moduli reali e 26 segmenti.

| Posizioni nel catalogo | Chiamate | Quota mediana del limite | Massima | Oltre 75% | Troncate |
|---:|---:|---:|---:|---:|---:|
| 51 | 31 | 40% | 52% | 0 | 0 |
| 67 | 11 | 42% | 56% | 0 | 0 |
| 68 / 88 (stesso modulo) | 29 | 43% | 66% | 0 | 0 |
| 115 | 14 | 37% | 46% | 0 | 0 |
| 267 | 28 | 87% | 100% | 25 | **5** |
| 307 | 19 | 71% | 92% | 6 | 0 |

Il pool congelato di 8 bandi reali estratti a caso va da 35 a 88 posizioni. Nessuno è nella
zona di rischio.

## Criterio a priori (dimensione del catalogo): non sufficiente

- **Il segnale c'è ed è misurabile prima della chiamata.** Le posizioni del catalogo spiegano il
  72% della varianza dell'output: circa 14.200 token + 88 per posizione. Nei moduli fino a 115
  posizioni non c'è nessun troncamento e il massimo è il 66% del limite.
- **Non individua però quale modulo tronca.** La previsione inverte l'ordine dei due moduli
  grandi: 77% per quello da 267 posizioni (osservato 87%, 5 troncamenti su 28) e 84% per quello da
  307 (osservato 71%, 0 su 19). Conta anche la densità dei dati nelle SOURCE, che la dimensione
  del modulo non misura.
- **La soglia non è localizzabile.** Fra 115 e 267 posizioni non ci sono dati e i moduli grandi
  sono solo due. Una soglia scelta lì sarebbe tarata su due fixture.
- **Il costo è alto e il beneficio non è dimostrato.** Sui moduli grandi le sezioni costano da 3,9
  a 5 volte i token totali (1,2-1,4 volte quelli non in cache) e allungano la fase globale del
  31-41%. Hanno perso un segmento per JSON non valido in ciascun modulo e non hanno mostrato un
  guadagno di copertura (P3). Sul modulo da 307 posizioni il costo sarebbe pagato senza alcun
  troncamento osservato.

**Decisione:** nessuna segmentazione decisa in base alla dimensione.

## Criterio a posteriori (troncamento osservato): promettente, di portata limitata

- **Oggettivo e generale:** il limite raggiunto è certificato dal provider
  (`finish_reason = length`), non c'è nessuna soglia da tarare e nessuna fixture coinvolta.
- **Non scatta mai sui moduli che non troncano**, quindi su quelli il costo in più è nullo.
- **Costo atteso per sessione** sul modulo a rischio (fase globale, dati registrati):

  | Strategia | Token | Non in cache | Secondi | Sessioni perse |
  |---|---:|---:|---:|---:|
  | sempre monolitico | 98k | 91k | 145 | 18% |
  | sempre sezioni | 382k | 128k | 190 | 0% |
  | sezioni solo dopo un troncamento | 169k | 115k | 184 | ~0% |

  Le sezioni decise in anticipo convengono solo se la probabilità di troncamento supera circa il
  72% (81% sul modulo da 307 posizioni).
- **Portata limitata:** i 5 troncamenti registrati sono tutti dello stesso modulo. Il meccanismo
  aggiunge un percorso (chiamata sprecata, poi sezioni) che non è mai stato provato.

La proposta di esperimento piccolo e preregistrato è in `PROPOSTA-ESPERIMENTO.md` (non eseguita):
- 3 sessioni sul modulo a rischio, con troncamento forzato dal replay registrato, quindi un replay
  parziale dichiarato, e tutte le altre chiamate reali;
- confronto su DOCX, dati corretti, segmenti persi, scritture non dimostrate, token e latenza;
- circa 1,3 milioni di token.

## Decisione motivata sulla strategia di generazione

1. **Valutazione finale con generazione monolitica**, come oggi e come nella baseline. La
   segmentazione resta disattivata.
2. **Nessuna soglia di dimensione.** L'evidenza non la sostiene e il costo sarebbe pagato anche
   dove il rischio non si è mai realizzato.
3. **Il ripiego dopo un troncamento è l'unico criterio promettente, ma non lo introduco ora.**
   Il beneficio atteso riguarda un solo tipo di modulo (circa 1 sessione su 6 in quel modulo, 0
   nel pool casuale) e un meccanismo nuovo subito prima della valutazione finale aggiunge rischio.
   Consiglio di passare alla valutazione finale contando i troncamenti come classe di fallimento
   separata e dichiarata (analisi interrotta, nessun valore scritto: il comportamento è sicuro).
   L'esperimento resta pronto, se vuoi recuperare quei casi prima o dopo la valutazione.

Limiti dell'analisi:
- solo 6 moduli e 2 grandi;
- un solo modello e una sola configurazione;
- le stime di costo usano mediane di poche sessioni (2 per modulo e modalità);
- la qualità delle sezioni dopo la correzione del narratore è misurata solo offline (replay a
  catena).
