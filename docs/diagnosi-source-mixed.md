# MIXED: associazione e copertura SOURCE — 6 ottobre 2026

Intervento limitato al lato SOURCE. L'extractor FORM, il routing iniziale,
i filtri FTS5/Qdrant, gli scope delle KB e il parser DOCX non sono stati
ridisegnati. Nessuna CompilationSession, nuova UI, modifica DOCX o commit.

## Diagnosi precedente alle modifiche

Le riproduzioni usano copie temporanee di SQLite e Qdrant del progetto `prova`,
profilo DeepSeek `deepseek-flash`. Il database originale è aperto in sola lettura;
le credenziali vengono usate dal provider configurato, senza includerle nei report.

### C: numero di iscrizione professionale

Domanda: «Il modulo richiede i dati del direttore tecnico. Con le fonti
disponibili abbiamo tutto ciò che serve per compilare quella parte?».

Il routing effettivo è MIXED. Sei requisiti validati: nome e cognome, qualifica,
data di abilitazione, ordine, numero albo e organigramma. Il requisito 5 è:

```json
{
  "name": "numero di iscrizione all’Albo professionale",
  "person_role": "direttore tecnico",
  "form_citation_id": 1
}
```

La citazione FORM 1 corrisponde al chunk **13880**, file **155**,
`domanda-partecipazione.docx`, sezione 5.d. Il `form_quote` comprende il testo
contiguo da «gli estremi dei requisiti del direttore tecnico» fino a
«numero di iscrizione all’Albo professionale:». Il grounding FORM è valido.

Le tre query SOURCE precedenti erano queste, con suffisso comune
«dati effettivi operatore economico»:

| Query | Requisiti riuniti | Ancore restituite dal retrieval |
|---|---|---|
| direttore tecnico: Nome e cognome direttore tecnico: Ordine professionale di appartenenza | 1, 4 | 17659, -46, -51, -27 |
| direttore tecnico: qualifica professionale direttore tecnico: numero di iscrizione all’Albo professionale | 2, 5 | -45, -32, -50, -27 |
| direttore tecnico: Data di abilitazione organigramma aggiornato | 3, 6 | -45, -32, -51, -29 |

I chunk **-45** (`generalita-mapi.md`) e **-32** (visura simulata) contengono
8421 ed entrano nel contesto finale del matcher. In particolare la SOURCE
citata con ID 6 è -45: appartiene a `scope=global`, `category=company`, `role=source`.
Il suo testo include ruolo del direttore, nominativo, qualifica, ordine e:

> Numero di iscrizione professionale simulato: 8421.

La visura contiene anche «iscrizione professionale simulata n. 8421, Ordine
degli Ingegneri di Bari». Non c'è una perdita di questa informazione nel ranking.

Il matcher propone effettivamente:

```json
{
  "requirement_id": 5,
  "source_citation_id": 6,
  "source_quote": "### Ing. Elisa Romano - direttore tecnico\n\n- Nome: Elisa.\n- Cognome: Romano.\n- Nominativo completo: Ing. Elisa Romano.\n- Ruolo in Mapi Ingegneria S.r.l.: Direttore tecnico.\n- Qualifica professionale nello scenario: Ingegnere.\n- Ordine professionale simulato: Ordine degli Ingegneri di Bari.\n- Numero di iscrizione professionale simulato: 8421.",
  "value": "8421"
}
```

Questo è il singolo supporto pertinente della risposta grezza del matcher.
Il JSON, l'ID, il ruolo,
la presenza letterale del valore e del soggetto superano i controlli. Fallisce
`quote_matches_requirement`: dopo casefold, normalizzazione Unicode/accenti e
spazi, il controllo richiede **tutte** le parole della label FORM nell'estratto.
Manca soltanto **albo**. La riparazione riceve «Parole del campo assenti
nell'estratto: albo» e il modello elimina il supporto. Risultato: 3 verificati,
3 non verificati. La causa concreta è la validazione dell'associazione.

### D: copertura generale

Domanda: «Possiamo completare oggi la domanda senza chiedere nulla all'utente?
Spiega cosa è verificato e cosa manca.».

La riproduzione precedente alle modifiche valida 15 requisiti:

1. Forma di partecipazione.
2. Tipo di forma di aggregazione.
3. Ruolo dell'operatore nel raggruppamento.
4. Mandatario di un raggruppamento temporaneo.
5. Mandante di un raggruppamento temporaneo.
6. Capogruppo di un consorzio ordinario.
7. Consorziata/esecutrice per il consorzio stabile.
8. Partecipazione contemporanea in forme diverse.
9. Estremi del deposito della domanda di ammissione.
10. Autorizzazione del Tribunale a partecipare alle gare.
11. Soggetto di cui avvalersi.
12. Copie elettroniche di tutti i documenti allegati.
13. Fatturato globale.
14. Estremi del provvedimento di ammissione del Tribunale.
15. Autorizzazione del giudice delegato a partecipare alle gare.

`min(3, len(names))` impone tre query; `names[offset::count]` mescola le label:
la prima contiene 1/4/7/10/13, la seconda 2/5/8/11/14, la terza 3/6/9/12/15.
Nessun requisito è nominalmente omesso, ma fatturato, consorzi e provvedimenti
giudiziari competono nella stessa query. Non esiste una responsabilità di ricerca
per argomento: la copertura è solo nominale. Ogni query restituisce quattro
ancore e il merge mantiene **quattro SOURCE complessive**. Il budget condiviso
tra requisiti eterogenei può eliminare riscontri utili.

Questo non dimostra che tutti i 15 requisiti abbiano valori nelle KB: molte
sono condizioni/dichiarazioni della specifica candidatura. La nuova prova A
precedente alle modifiche si era invece fermata nel grounding dell'extractor;
non è stata presentata come prova di un problema SOURCE.

## Modifica adottata

- Il numero di iscrizione professionale viene riconosciuto attraverso una
  relazione testuale locale fra iscrizione e numero, con varianti quali
  «iscrizione professionale simulata n.» e «iscrizione all'Albo professionale».
  Restano obbligatori ruolo SOURCE, citazione valida, estratto letterale, valore
  letterale e ruolo personale pertinente. Non si accetta un telefono, codice
  fattura, numero CCIAA o altro numero nello stesso chunk. Per gli altri valori
  numerici anche le parole del campo devono risultare nello stesso passaggio
  locale del valore, conservando i confini di riga durante il controllo.
- Una sola chiamata di raggruppamento SOURCE per più di due requisiti, con schema
  JSON esplicito e output massimo 1.024 token. Nessuna chiamata per singolo campo
  e nessun retry del raggruppamento. Il modello raggruppa ID già validati,
  senza creare nuove label o valori. ID inesistenti/duplicati e gruppi di ruoli
  personali differenti vengono respinti. Gruppi coerenti troppo grandi vengono
  suddivisi, senza scartare l'intero piano per un semplice eccesso dimensionale.
- Massimo **6 gruppi operativi**, **4 requisiti per gruppo**, **2 query per gruppo**,
  **2 ancore per query**, **4 evidenze per gruppo** inclusa l'espansione. Le query
  contengono una/due label effettive del gruppo. Totale massimo **12 ricerche e
  24 SOURCE**, deduplicate, più le 4 FORM preesistenti. Nessun ranking globale
  successivo elimina gruppi. Il timeout complessivo rimane 90 s/180 s per Ollama.
- Per ogni requisito si conserva l'insieme delle citazioni SOURCE ammesse dal
  suo gruppo. Un gruppo senza risultati costituisce una ricerca eseguita; un
  requisito escluso dal budget resta **non ricercato**, non «non verificato».
  Se il planner fallisce, il fallback usa ruoli personali e singoli requisiti
  entro lo stesso budget, con esclusioni esplicite. Questa mappa è temporanea,
  senza nuovo stato persistente o contratto API.
- Il matcher SOURCE riceve un compito stabile su tutti i requisiti: domanda
  originale e cronologia non devono orientarlo a proporre solo dati mancanti.
  Il JSON mode viene richiesto esplicitamente nel prompt. La verifica reale ha
  individuato e fatto correggere una risposta HTTP 400 di DeepSeek quando
  questa parola mancava dal nuovo prompt; aggiunta regressione software.

L'extractor FORM e le sue garanzie sono invariati. Nessuna modifica ai filtri
o agli indici FTS5/Qdrant. Company/General KB mantengono categorie e scope reali.

## Test e benchmark finale

**329 test mirati**, **829 test backend completi**, Ruff e diff check superati.
Le regressioni usano provider simulati: 8421 con etichette equivalenti, più dati
della stessa persona verificati separatamente, numeri non pertinenti, fonte di
un altro gruppo, copertura di 16 requisiti/16 documenti su FTS5 e Qdrant, esclusi
dal budget distinti, fallback e suddivisione dei gruppi. Restano i test di
FORM_ONLY/SOURCE_ONLY, isolamento e provenance. Nessun test frontend/E2E nuovo.

Separatamente, benchmark reale con DeepSeek, Qdrant/BGE e conversazioni nuove:

| Caso | Richiesta |
|---|---|
| A | Quali dati richiesti dal modulo non risultano ancora verificati nelle fonti? |
| B | Con i documenti disponibili, quali dati della sezione società di ingegneria possiamo già compilare? |
| C | Il modulo richiede i dati del direttore tecnico. Con le fonti disponibili abbiamo tutto ciò che serve per compilare quella parte? |
| D | Possiamo completare oggi la domanda senza chiedere nulla all'utente? Spiega cosa è verificato e cosa manca. |

Tutti hanno intent MIXED e quattro FORM. Conteggi osservati, non garantiti per
ogni esecuzione del modello:

| Caso | Requisiti | Gruppi | Query SOURCE | Coperti | SOURCE | Verificati | Non verificati | Non ricercati | Retry extractor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | 10 | 4 | 8 | 10 | 10 | 0 | 10 | 0 | Sì |
| B | 11 | 5 | 7 | 11 | 11 | 7 | 4 | 0 | Sì |
| C | 6 | 3 | 4 | 6 | 8 | 4 | 2 | 0 | No |
| D | 16 | 5 | 10 | 16 | 8 | 0 | 16 | 0 | Sì |

B verifica denominazione, forma giuridica, sede, nome del direttore, qualifica,
ordine e **8421**. CCIAA, numero/data d'iscrizione, data di abilitazione e
organigramma restano non verificati. C verifica nome, qualifica, ordine e
**numero albo 8421**, lasciando data di abilitazione e organigramma non verificati.
Entrambi usano l'unica riparazione SOURCE già esistente, senza ulteriori ricerche.

**A resta un falso negativo semantico del matcher**: i requisiti 8/9 sono codice
fiscale e partita IVA; il gruppo 7/8/9/10 riceve anche -43 e -30 con il valore
demo. Il modello restituisce comunque `supports: []`. Nessun validatore scarta
valori: non ne vengono proposti. Questo stop non è più dovuto a tre query globali
o al top-k, e zero verificati non prova l'assenza dei dati nella KB.
D estrae soprattutto titoli/dichiarazioni, alternative di partecipazione,
raggruppamenti e provvedimenti concorsuali; propone anch'esso zero supporti.
Tutti i requisiti hanno ricerche dedicate al gruppo, ma non c'è una verifica
di applicabilità né una garanzia di completezza del modulo.

Report locali, esclusi da Git:
[traccia finale](../backend/data/chat-audit/source-mixed-2026-10-06/deepseek-final.json),
[riepilogo](../backend/data/chat-audit/source-mixed-2026-10-06/summary.json),
[test mirati](../backend/data/chat-audit/source-mixed-2026-10-06/targeted.log),
[suite completa](../backend/data/chat-audit/source-mixed-2026-10-06/backend-full.log).
La traccia conserva query, gruppi, requisiti, contesti, candidati, prompt e
risposte grezze, senza credenziali. I primi dump prima della modifica erano in
`/tmp` e sono andati persi al riavvio: i riscontri essenziali sono riportati sopra.

Per ripetere dalla UI: riavviare il backend aggiornato, usare il progetto con
modulo indicizzato e KB demo, scegliere DeepSeek e aprire una nuova conversazione
per ciascuna domanda. Controllare le citazioni Modulo/Fonte e i log INFO
`SOURCE plan`, `Chat SOURCE cluster`, `Chat SOURCE coverage`, `Chat requirements`.
Nessuna reindicizzazione necessaria. Le quantità possono variare con la selezione
del FORM e l'output del modello; le garanzie di ruolo/copertura devono restare.

Il lato SOURCE ha ora budget e copertura espliciti e risolve il falso negativo
8421. Non è ancora giustificato dichiarare congelato l'intero MIXED: A mostra
che un matcher può omettere dati presenti nel contesto. Durante alcune prove
intermedie l'extractor invariato ha inoltre rifiutato output non grounded.
Il prossimo controllo mirato può riusare requisiti/fonti di A, senza cambiare
retrieval o aggirare il grounding FORM. CompilationSession rimane da discutere.
