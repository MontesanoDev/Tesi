# Revisione della compilazione nel composer — 12 ottobre 2026

La checklist e l'elenco XML sono stati rimossi dalla chat. Il flusso è:
`@modulo` → «me lo compili?» → analisi globale → sintesi AI e massimo tre
domande → risposta nel composer → consenso esplicito alla bozza → download.
Il lavoro riguarda l'interazione sulla proposta globale, non una riscrittura
del catalogo V5, contratto V10, RAG, parser o renderer.

## Causa e soluzione

La UI mostrava direttamente l'audit e chiedeva selezioni manuali per valori e
condizioni. Inoltre `review_fields` cercava disposition=unassigned, mentre i
record omessi hanno proposal=None: passavano così centinaia di etichette XML
senza requisito interpretato. Ora quei record restano nell'audit scaricabile,
non diventano domande o dati mancanti nella chat.

Una breve sintesi riceve solo proposte validate, contesto FORM, prove SOURCE,
binding personale verificato e questioni pendenti. Restituisce testo naturale,
slot da chiedere e proposte eventualmente da trattenere. Il backend conserva
ID e destinatari; il modello non sceglie field_id. Tre domande al massimo,
24 questioni nel pool, 40 proposte nella sintesi, timeout 45 s e 2.048 token
output, nessun retry automatico. La sintesi può solo restringere le proposte,
mai validarne una rifiutata; quelle oltre il budget non sono esportate dalla
conferma generica in chat. L'analisi completa resta una sola chiamata per modulo.

Risposte parziali aggiornano solo slot univoci. UNKNOWN/SKIP/REFUSE differiscono
senza valori fittizi; applicabilità USER non diventa prova SOURCE. Un valore
USER deve appartenere alla clausola del messaggio, riferirsi a uno slot attivo
e superare il validatore DOCX. Le uniche normalizzazioni ammesse sono date
complete equivalenti. Pausa/ripresa, refresh e revisioni usano stato persistito.
Le vecchie proposte globali ricevono una sintesi, senza rianalisi o migrazioni.

La generazione richiesta nel composer sceglie solo SOURCE grounded, condizioni
confermate e valori USER acquisiti; rivalida fonti, originale e revisione anche
nella transazione finale. Ogni copia parte dall'originale. Il report distingue
SOURCE, consenso all'esportazione USER e valori forniti USER. Non si promuove
GROUNDED_PROPOSAL a RESOLVED. Non si genera implicitamente una bozza incompleta.

## Verifiche software

Provider simulati, DB/storage temporanei: **59 mirati**, **1.882 backend completi
/136,02 s**, **101 frontend**, **12 browser desktop/mobile** (movimento ridotto,
mention normale, dialogo, consenso, refresh/download), Ruff, lint, build e diff
check passati. La completa finale segue il refinement funzionale su ruoli e
UNKNOWN; dopo la sola aggiunta dei contatori/tempi della sintesi sono stati
rieseguiti 59 mirati e Ruff. Non misurano qualità semantica di DeepSeek.

Test: nessuna checklist/ID nel DOM; analisi non ripetuta dopo input; persistenza;
condizioni false/ignote non esportate; input USER fuori dagli slot rifiutato;
ambiguità e parti valide indipendenti; rinvii; pausa/ripresa; errori provider/schema
prudenti; ruolo personale preservato nel contesto; SOURCE mutate bloccano export;
provenienza e materializzazione reale tramite validator/renderer esistenti.
FTS5 e Qdrant configurati nelle regressioni; il motore globale carica il corpus
piccolo autorizzato, non esegue il vecchio ranking RAG.

## Serie reali DeepSeek, senza modifiche durante ogni serie

1. **fe73786**: Catanzaro, nuova conversazione, routing + analisi + sintesi reali.
   Analisi riuscita, 13 proposte SOURCE. Sintesi pertinente ma rifiutata:
   questions[].text anziché question. Raw/schema/errore conservati, niente DOCX.
   JSON mode DeepSeek non applica response_schema: mancava lo schema nel prompt.
2. **d6f9991**: schema esplicito, nessun alias permissivo. «Riprendi» ritenta
   solo la sintesi Catanzaro. Poi pausa/ripresa, conferma del ramo ingegneria e
   consenso alla bozza. Labirinto V1 da fonti originali reingestite via API in
   nuovo DB: analisi/sintesi, tre domande in un messaggio, unica risposta
   CONDITION_TRUE + SKIP recapito + UNKNOWN polizza, poi bozza esplicita.
3. **8f82c59**: solo replay reale della sintesi sui due audit, DB read-only,
   nessuna nuova analisi/generazione. Dopo una frase impropria sul «professionista
   che firma» nella serie 2, preservato il contesto del binding personale e
   vietate relazioni non attestate. Nei due replay nessuna attribuzione del ruolo
   di firmatario: distinzione direttore/operatore e posizioni non valutate corretta.

| Caso | Candidate | Proposte SOURCE | Domande primo riepilogo valido | Turni chiarimenti | Consenso bozza | Valori SOURCE scritti |
|---|---:|---:|---:|---:|---:|---:|
| Catanzaro | 307 | 13 | 1 | 1 | 1 | 13/13 |
| Labirinto V1 | 55 | 17 | 3 | 1 | 1 | 17/17 |

Catanzaro include inoltre tre turni di prova ripresa dopo schema/pausa/ripresa;
non sono turni necessari a raccogliere dati. Nessun dato fattuale USER fornito.
Entrambe le sessioni sono GENERATED come **bozze parziali**, zero RESOLVED.
Catanzaro: operatore Mapi Ingegneria S.r.l., forma giuridica, sede legale,
CF/PIVA IT01234567890, direttore Ing. Elisa Romano, qualifica Ingegnere,
Ordine degli Ingegneri di Bari e albo 8421 derivano da generalita-mapi.md.
Tredici valori includono occorrenze ripetute in sezioni differenti.

30/30 valori scritti nelle celle fisiche corrette. Nessun'altra cella modificata;
paragrafi invariati salvo avviso bozza; checkbox native invariate. Recapito e
polizza rinviati nel Labirinto restano vuoti, non diventano USER/SOURCE inventati.
Originali invariati. Le chiamate della chat sono API ASGI + provider reali;
il browser usa API simulate, non viene presentato come E2E con provider reale.

**18 chiamate /177.970 token**: due analisi, nove routing, cinque sintesi
(inclusa quella rifiutata), due replay di sintesi. Zero retry automatici.
Analisi 108,25 s Catanzaro /88,13 s Labirinto; ultimi replay 1,87/2,02 s.
Le prime sintesi non furono cronometrate separatamente: non si inventano tempi
E2E o confronti causali di latenza. Il fallimento iniziale è incluso nei consumi.

## Limiti e ripresa

La UX è conversazionale; il motore continua a produrre proposte parziali.
291/34 posizioni rispettivamente non analizzate, non campi obbligatori mancanti.
Applicabilità semantica, granularità/copertura e checkbox Word restano limiti.
La prosa AI non è una prova: ha mostrato un'imprecisione di ruolo e un dubbio sul
recapito unificato senza escluderlo. Il contesto aggiunto migliora i due replay,
non garantisce che ogni futura sintesi sia perfetta. I gate backend restano
indipendenti. Niente modifica libera arbitraria di campi non chiesti; correzione
conversazionale di una proposta trattenuta e riapertura dei rinvii da estendere
in un prossimo passo, senza rilassare provenance o allargare automaticamente il
corpus. Non dichiarare completamento del modulo o pronto per presentazione.

Test eseguiti in copie temporanee. Hash fisico del DB live cambiato durante
la prova: non si dichiara byte-identità dell'intero file; confronto read-only
con snapshot conserva fonti, moduli, conversazioni e sessioni preesistenti.
Il timestamp del progetto nella copia differisce per l'attività di test.
Gli originali sono identici. Nessun rollback o manipolazione dei dati live.

Failure iniziali dei test e degli harness registrate: tipo/argomento errato
nel test parse_turn_plan, mock frontend con argomento sbagliato, Ruff;
runner Labirinto con created.json del caso sbagliato (GET404 prima del provider),
numerazione che contava anche planner, verifica DOCX da cwd sbagliato e
assert del checksum fisico. Nessuna ripetizione delle analisi/export riusciti.

[Metriche e riferimenti raw](benchmarks/2026-10-12-conversational-review.json),
[bundle pubblico](benchmarks/2026-10-12-conversational-review-audit.tar.gz),
[controlli finali](benchmarks/2026-10-12-conversational-review-final-checks.json).
Grezzi locali: backend/data/compilation-audit/conversation-review-20261012/.
Bundle senza DB/chiavi: prompt/schema/HTTP/raw/errori/audit/stati/Word/log/script,
più screenshot browser con API simulate. Dettagli e consumi in relazioni.md.

Per riprovare: `./start.sh`, selezionare DeepSeek, `@domanda-partecipazione.docx`,
«me lo compili?», rispondere nel composer. «Salta»/«non lo so» rinviano, «basta»
mette in pausa, «riprendi» conserva la sessione. Chiedere «genera la bozza
parziale» solo quando si desidera esportare quanto disponibile; scaricare
DOCX/report e controllarli. Nessuna nuova pagina o operazione tecnica manuale.

Bundle verificato: **193 file /1,039,762 byte**, SHA-256
`e09e888dd2786cd56e1c88d4be24578043fd1314d039822f0a41e29775dba709`. Copie temporanee con DB e chiavi rimosse
dopo backup/verifica; grezzi non sensibili conservati anche in locale.
