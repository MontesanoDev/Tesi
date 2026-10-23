# CRAA: effetto causale della motivazione MODEL da 225 caratteri

20 ottobre 2026. [Consegna](../benchmark%20ufficiale/craa-model-reason-20261020-01/README.md),
[diagnosi prima](../benchmark%20ufficiale/craa-model-reason-20261020-01/diagnosis-before.json),
[dopo](../benchmark%20ufficiale/craa-model-reason-20261020-01/diagnosis-after.json),
[replay narratore salvato](../benchmark%20ufficiale/craa-model-reason-20261020-01/saved-dialogue.json).

**Esito:** il limite era l'unico ostacolo all'accettazione di un chiarimento
FORM valido e ne impediva l'ingresso nel pool del narratore. Nessuna ricevuta
USER già accettata è stata cancellata. Corretta soltanto la gestione della
motivazione descrittiva troppo lunga. Nessuna nuova scrittura DOCX ottenuta o
attribuita alla correzione, nessuna nuova chiamata LLM.

## Prova a un solo fattore, prima di implementare

Caso storico: sessione `0d05a74a2ccd4e579b217515b637423f`, risposta reale originale
CRAA del benchmark `casuali-v12-20261019-01`. Destinazione `p5.s0`, dopo «Il
sottoscritto». Il MODEL propone un chiarimento, non un valore SOURCE o una
risposta USER. La motivazione è di 225 caratteri, contro 200 nello schema
`UserFieldRequest`.

Percorso dimostrato nel codice:

1. La validazione globale isola le singole proposte. `attach_user_requests`
   verifica `UserFieldRequest` prima dei controlli di destinazione e condizioni.
2. L'errore sulla sola lunghezza di `reason` rende il chiarimento `REJECTED`.
   La proposta originale resta nell'audit; il campo non riceve la richiesta
   locale e rimane privo dei suoi metadati FORM operativi.
3. `question_pool` considera campi con prove FORM e destinatari verificati:
   quella richiesta è quindi esclusa prima che il narratore possa sceglierla.

Confronto offline sullo stesso DOCX, sulle stesse SOURCE e sulla stessa risposta
MODEL. Cambiato **soltanto** `clarifications.p5.s0.reason`, con la frase
«Confermare il nominativo del sottoscritto.», 42 caratteri. Tutti gli altri
byte logici del payload rimangono uguali. La variante è un controfattuale di
diagnosi; non sostituisce la risposta originale né diventa una revisione manuale.

| Stadio | Originale 225 | Solo motivazione abbreviata |
|---|---|---|
| Chiarimento | REJECTED: lunghezza | GROUNDED_REQUEST |
| Altri controlli FORM e condizioni | Non raggiunti per quel record | Tutti superati |
| Pool prima della conferma societaria | Una condizione, nessun firmatario | La stessa condizione più il chiarimento |
| Pool dopo la conferma societaria | Vuoto | Chiarimento disponibile |
| Ricevute USER esistenti | Conservate | Identiche |
| Nuovi fatti SOURCE o valori autorizzati | Nessuno | Nessuno |

Il risultato si ripete nelle cinque copie delle transizioni persistite esaminate.
Non emergono ulteriori gate che impediscano l'ingresso di quel chiarimento nel
pool. Questo dimostra la perdita di una **possibilità operativa del dialogo**.

## Limite della conclusione: domanda disponibile e domanda realmente posta

Le due risposte storiche del narratore sono conservate. La prima chiede solo
la condizione societaria; quella successiva ha `questions=[]`. Riutilizzando
questi esatti piani sul pool corretto, il chiarimento non viene automaticamente
aggiunto: il piano finale continua a offrire l'export. Non abbiamo eseguito una
nuova inferenza, quindi non sappiamo se un nuovo narratore lo sceglierebbe.
Non si dichiara una nuova domanda reale, una risposta USER recuperata o un
miglioramento del DOCX.

Il nome scelto compare inoltre in **tre messaggi USER** originali. Quella scelta
nominativa non è sparita dal testo; non era stata collegata al campo. Il problema
di compilazione del nome CRAA rimane separato. La correzione non presume che
richiedere nuovamente quel nome sia utile e non affronta le domande ridondanti.
La ricevuta societaria già accettata resta identica. Non è dimostrata la
cancellazione di una decisione USER da parte dell'errore sui 225 caratteri.

## Correzione minima del meccanismo

Un solo file applicativo: `backend/app/compilation_user_requests.py`.

Il limite descrittivo **200 rimane nel contratto MODEL**. Per una motivazione
che sia una stringa non vuota e superi quel limite, il validatore operativo
usa una descrizione neutra breve. La stringa originale rimane integralmente in
`clarifications[id].proposal.reason`; l'audit registra separatamente:

- `metadata_warnings[].field = reason`;
- `code = descriptive_text_over_limit`;
- lunghezza originale e massimo del contratto;
- posizione del testo integrale ed effetto `operational_reason_replaced`.

Non viene troncata una frase, reinterpretata una negazione o utilizzata la
motivazione come prova fattuale. La nota operativa non certifica assenza di dati
nelle SOURCE. Il record originale e il payload acquisito non sono modificati.
Un motivo descrittivo troppo lungo non decide più da solo l'esclusione del
chiarimento; tutti i vincoli strutturali rimangono necessari.

Restano rifiutati tipi errati, motivazioni vuote, proprietà extra come `value`,
label troppo lunghe, campi sconosciuti, firme, destinazioni già proposte dalle
SOURCE, citazioni FORM insufficienti e condizioni assenti o duplicate.
Il budget globale dell'output rimane invariato. La correzione riguarda solo
la lunghezza di `reason` nei chiarimenti; non introduce riparazioni generali
sulle altre proprietà o sugli altri metadati MODEL.

Un `GROUNDED_REQUEST` autorizza soltanto una domanda: il campo resta
`REVIEW_REQUIRED`, senza valore, fatto SOURCE, checkbox o condizione TRUE.
Scelte USER e successiva validazione dei valori seguono il percorso esistente.
Schema globale, prompt, modello, API, DB, grounding, writer e FORM invariati.
Nessuna migrazione delle sessioni originali; eventuali nuove rivalidazioni
beneficiano della correzione, senza aggiornamenti impliciti in lettura.

## Verifiche

Prima della correzione: **6 FAIL e 20 PASS**, sulle aspettative di recupero di
motivazioni da 201, 225, 500, 2.001 e 100.000 caratteri e sul caso CRAA reale.
Dopo: **28 nuovi casi permanenti**, incluse due sessioni isolate FTS5/Qdrant con
provider simulati. Conservazione del testo e del warning nel database/audit,
domanda disponibile, risposta UNKNOWN, export dei due dati SOURCE indipendenti
senza valori USER o checkbox. I test software non sono nuove valutazioni LLM.

**101 test mirati PASS in 14,32 s; 2.905 backend PASS in 225,72 s; Ruff PASS.**
Frontend invariato: suite frontend e rendering PDF non ripetuti. Il primo replay
del narratore aveva un errore nel solo harness su `answers` assente, corretto con
un valore vuoto di default; log conservato. Corretti nel nuovo test import e
una riga fuori formato. Un'etichetta ereditata del riepilogo replay è stata
precisata per distinguere DOCX identici e variazioni attese nell'audit.

Regressione deterministica senza rete o SQLite:

| Artefatti | Esito |
|---|---|
| Dieci casi con contesto conservato | 10 DOCX identici; solo CRAA cambia il chiarimento |
| Stessi dieci con contesto USER già registrato | 10 DOCX identici; medesimo delta CRAA |
| Due Trapani reali della fase firmatario | Audit e DOCX identici, 17 scritture ciascuno |
| Ultimo CRAA reale della fase USER | Audit e DOCX identici, 7 scritture |
| Minervino V12 nei due contesti | 61/61 conservate |

Totale **23 DOCX identici**, 21 audit identici e due copie CRAA con la variazione
prevista. Fatti, condizioni, binding, gruppi checkbox e revisioni SOURCE/USER
sono identici in tutti i confronti. Sul CRAA cambia soltanto il chiarimento e
il relativo campo descrittivo, più i contatori di copertura conseguenti:
`unassigned_count` 42→41, un chiarimento respinto→accettato. Il flag strutturale
`coverage_checks_passed` diventa TRUE; `semantic_completeness_verified` rimane
FALSE. Non è una misura di completezza fattuale.

Il DOCX CRAA storico rimane a nove scritture; quello reale più recente rimane a
sette. Il nome del firmatario resta vuoto nei documenti salvati. Nessuna selezione
checkbox o nuova accettazione fattuale introdotta. I due CCIAA invisibili nel PDF
restano gli stessi artefatti e geometrie: nessun intervento sulla loro visibilità.

## Conservazione e consegna

Nessuna chiamata provider: costo e token LLM nuovi **zero**. Le due prove di
sessione usano trasporti simulati e storage temporaneo. Nessuna sessione reale
creata, nessun nuovo DOCX presentato come compilazione migliorata.

Preservati tutti gli altri file e gli artefatti precedenti, le 29 sessioni live
e i 285 file storage. Codice prima/dopo, input, risposte, transizioni, confronti,
log e verifiche salvati in `backend/data/compilation-audit/craa-model-reason-20261020-01/`.
[Backup separato](../benchmark%20ufficiale/craa-model-reason-20261020-01/audit-completo.tar.gz),
[verifica estratta](../benchmark%20ufficiale/craa-model-reason-20261020-01/VERIFICA-BACKUP.json),
senza DB privati, credenziali o `.env`. Ricostruzione dal codice estratto dei
controfattuali prima/dopo, del piano narratore salvato e dei 23 DOCX, senza rete.
Nessun commit/push.

Backlog intatto: nome firmatario CRAA, CCIAA nel PDF, campi composti e domande
ridondanti. La fase si chiude sul recupero del chiarimento validabile; l'effetto
su una nuova conversazione reale resta da misurare separatamente. Nessuna
baseline generale adottata. Arresto alla consegna.
