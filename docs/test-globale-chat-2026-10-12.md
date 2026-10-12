# Compilazione globale nella chat — 12 ottobre 2026

Il motore globale V10 è il default per le nuove compilazioni nella chat.
Codice congelato **449b109**, baseline recuperabile **5d4bbb9**, branch
`prune-backend`: nessun passaggio al branch `main` e nessun push.

## Uso con start.sh

Dalla radice eseguire `./start.sh`, aprire il progetto e scegliere DeepSeek nel
selettore del modello. Aprire una nuova conversazione, scegliere il modulo
DOCX con `@`, scrivere «me lo compili?». Una chiamata di analisi sull'intero
catalogo; le normali domande sul modulo restano FORM RAG.

Il risultato rimane una proposta da rivedere. Aprire **Rivedi proposte e
condizioni**, verificare posizione/FORM e SOURCE, selezionare i valori, confermare
le sole condizioni applicabili e autorizzare esplicitamente la bozza parziale.
Poi **Genera bozza con i valori selezionati**, **Scarica DOCX** e **Scarica report
bozza**. Prima dell'export è scaricabile il report delle proposte.

Sessioni preesistenti conservate come legacy, senza avanzamento automatico dalla
UI. Non migrare i loro valori al globale. Il default delle API dirette senza
engine rimane V1 per compatibilità; la chat e la sua API frontend scelgono global.

## Architettura e verifiche di sicurezza

Una sessione globale conserva catalogo, audit V10, tentativi, lease e riferimenti
agli artefatti nello state_json esistente. Nessuna nuova tabella. Un solo passo
per catalogo, timeout 300 s e lease 360 s; nessun retry automatico. Il planner
semantico della chat resta una chiamata separata. Pausa/refresh/errori non
ripetono l'analisi; la ripresa esplicita dopo errore autorizza un nuovo tentativo.

Il corpus SOURCE piccolo completo contiene soltanto fonti autorizzate del
progetto e Company/General KB. Riutilizzato il loader del runner senza modificare
query/gate/prompt V10. Limiti: 400 candidate, 96 chunk, 100.000 caratteri SOURCE,
350.000 caratteri input. Superamento esplicito, nessun taglio nascosto.

GROUNDED_PROPOSAL non diventa RESOLVED. Solo stringhe grounded e posizioni
scrivibili possono essere selezionate; alternative/rifiuti/checkbox non vengono
scritte. Conferme di applicabilità USER distinte dai valori SOURCE. L'export
rilegge le SOURCE, confronta l'audit dei valori selezionati, esegue il validatore
DOCX esistente e il renderer da originale. Revisione e SOURCE ricontrollate
nella transazione di salvataggio. Nessuna bozza implicita o generazione vuota.

Report: valori SOURCE, `reviewed_by=USER`, condizioni confermate e consenso alla
bozza parziale USER, zero RESOLVED. Nessuna certificazione di completezza.
Le API `/global-draft` e `/global-report` estendono le compilation-sessions;
`/finalize` V1 rifiuta sessioni globali. Download esistenti riutilizzati.

## Controlli software

Provider simulati soltanto nei test del software, non nelle prove DeepSeek:

- 58 backend mirati /17,47 s.
- **1.847 backend completi /126,81 s**.
- **101 frontend /5,18 s**, 12 file; lint e build passati.
- **8 browser /24,2 s**: desktop/mobile, refresh/download, riduzione del movimento
  e regressioni V1 simulate. Nuovo flusso con selezione/condizioni/consenso;
  niente export prima della revisione o avvio per una normale domanda FORM.
- Ruff e diff check passati.

I test storici V1 scelgono legacy esplicitamente nella fixture, invece di
accidentalmente esercitare il nuovo default. Test di mention e adapter verificano
che il default reale sia global. Sono coperti: isolamento progetto, persistenza,
una sola chiamata, pause concorrenti, provider failure, fonti mutate, selezioni
invalide, consenso esplicito e rigenerazione da originale.

Failure intermedie conservate: mock/API frontend senza engine, tipi dei nuovi
fixture; kwargs del parser nel mock legacy; fixture importate con dipendenze non
registrate nei moduli utilizzatori; Ruff; prima completa interrotta e successiva
completa fallita prima della correzione delle fixture. Nessuna di queste prove
è presentata come misura della qualità semantica reale.

## Prova reale con deepseek-flash

Protocollo registrato prima delle chiamate, codice applicativo immutato per
l'intera serie. Conversazioni/sessioni nuove attraverso `/answer` con mention
strutturata e «me lo compili?», poi `/resolve` e review/export espliciti via API.
Trasporto esterno reale, nessun provider simulato; osservatore planner delega
la richiesta senza modificarla e salva schema/prompt/raw/usage.

API eseguite in-process con ASGI: questo è uno smoke reale del backend/provider,
non un test del browser con provider reale. Browser/UI verificati separatamente.

Catanzaro usa una copia SQLite read-only del workspace prova e una copia del
suo originale archiviato, 17 chunk SOURCE (Company/General). Il modulo live ha
SHA-256 `aeb1bda3016d221c36041d003731b4b3e6bca5cb7fd265094fec07dfa44e47d0`:
non è il file byte-identico dei confronti congelati precedenti. Nessuna nuova
estrazione casuale di bando: è uno smoke d'integrazione sul modulo principale.

Labirinto usa originale/fonti fixture V1, reingestiti via API in DB/storage
separati. ID/chunking conseguenti all'ingestion: non confronto causale con i
precedenti punteggi sulla lista SOURCE congelata. Gold mai inviato al modello.

| Prova | Candidate | Chiamate routing / analisi | Proposte selezionabili | Omesse | Tempo AI analisi | Token analisi | Valori selezionati e scritti |
|---|---:|---:|---:|---:|---:|---:|---:|
| Catanzaro | 307 | 1 / 1 | 14 | 291 | 90,11 s | 85.483 | 9 / 9 |
| Labirinto V1 | 55 | 1 / 1 | 17 | 34 | 70,05 s | 32.836 | 17 / 17 |

Quattro chiamate reali complessive, zero retry; 118.319 token analisi + 6.453
routing = **124.772 token**. I tempi sono quelli della fase AI, non cronometro
E2E; nessun confronto causale di risparmio o latenza, nessuna % di accuratezza.

Entrambe: CREATED -> ANALYZING -> WAITING_FOR_USER/REVIEW, zero RESOLVED,
nessun DOCX generato automaticamente. Dopo review controllata USER:
GENERATED, bozza parziale. Nessun valore fattuale inserito dall'utente.

### Catanzaro: valori verificati nella posizione XML

| Candidate | Requisito | Valore scritto | SOURCE |
|---|---|---|---|
| t0.r5.c1 | Operatore economico | Mapi Ingegneria S.r.l. | generalita-mapi.md, chunk -43 |
| t0.r6.c1 | Forma giuridica | Societa a responsabilita limitata | generalita-mapi.md, chunk -43 |
| t0.r7.c1 | Sede legale | Via Giovanni Amendola 172/C, 70126 Bari (BA), Italia | generalita-mapi.md, chunk -43 |
| t0.r9.c1 | Codice fiscale | IT01234567890 | generalita-mapi.md, chunk -43 |
| t0.r10.c1 | Partita IVA | IT01234567890 | generalita-mapi.md, chunk -43 |
| t26.r0.c1 | Direttore tecnico | Ing. Elisa Romano | generalita-mapi.md, chunk -45 |
| t26.r1.c1 | Qualifica | Ingegnere | generalita-mapi.md, chunk -45 |
| t26.r3.c1 | Ordine | Ordine degli Ingegneri di Bari | generalita-mapi.md, chunk -45 |
| t26.r4.c1 | Numero albo | 8421 | generalita-mapi.md, chunk -45 |

La review controllata conferma partecipazione e ramo società di ingegneria.
I valori restano SOURCE; le conferme sono USER. Non si tratta di un nuovo
benchmark di RESOLVED automatici. Dati demo simulati presenti nelle fonti reali
del progetto, non dati fiscali certificati dal test.

Labirinto: 17 valori scritti, inclusi cinque dati societari, telefono, PEC,
CCIAA/REA/data iscrizione, procedura e i quattro dati del direttore. I dettagli
per ogni cella e relativa SOURCE sono nel JSON di materializzazione.

### Materializzazione e integrità

Per 26 valori selezionati su 26: corrispondenza esatta nelle celle XML fisiche,
non nella griglia espansa di python-docx; solo quelle celle hanno cambiato testo.
Paragrafi invariati salvo l'avviso di bozza già previsto dal renderer; checkbox
native invariate. Originali scaricati identici agli snapshot, DB live e originale
live invariati anche dopo gli export (hash prima/dopo).

Nessuna scrittura di valori omessi, rifiutati o non selezionati. Report distingue
SOURCE dai controlli USER. Il test non afferma che tutti i campi del modulo
siano stati risolti o che gli allegati siano pronti.

Failure dell'harness conservate e poi corrette senza modificare l'applicazione:
path/PYTHONPATH iniziali, nome report `id` anziché `cell_id`, lettura della griglia
espansa anziché celle fisiche, `.xml` non disponibile sui controlli lxml generici.
Gli export già riusciti non sono stati ripetuti: ripresa della sola verifica;
nessuna chiamata AI aggiuntiva.

## Limiti osservati e prossimo passo

- Sede operativa Catanzaro proposta uguale alla legale senza condizione locale
  «se diversa»: **esclusa dalla selezione controllata**. La review resta necessaria.
- Una proposta del firmatario in altra sezione rifiutata per contesto FORM/ruolo;
  il valore non entra nella bozza. Altre 291 posizioni non proposte non sono
  291 campi obbligatori né NOT_APPLICABLE automaticamente.
- Alternative/checkbox/applicabilità non complete; il globale non offre ancora
  l'iterazione libera sui valori USER del motore V1. Non trasferirla implicitamente.
- Un documento può ancora richiedere circa un minuto e mezzo al provider.
  Una chiamata riduce l'orchestrazione, non garantisce un tempo istantaneo.
- Corpus completo limitato: KB grandi danno errore esplicito. Gli altri provider
  passano dal trasporto esistente ma non sono stati validati semanticamente qui.

La versione è pronta da **provare come proposta globale con revisione/export**
nella chat. Il passo successivo è osservare la review con l'utente e misurare
copertura/applicabilità prima di automatizzare altre scritture.

Acquisizioni locali: `backend/data/compilation-audit/global-main-20261012/`;
protocollo, schema/prompt/raw, audit/stato, DOCX, report, verifiche e log software.
Bundle versionato e JSON riepilogativo collegati nel registro e in STATUS.md.
DB temporanei e chiavi private esclusi dal bundle e rimossi dopo la verifica.

[Acquisizioni complete](benchmarks/2026-10-12-global-chat-audit.tar.gz),
[JSON delle celle e SOURCE](benchmarks/2026-10-12-global-chat.json),
[verifiche finali](benchmarks/2026-10-12-global-chat-final-checks.json).

Bundle pubblico: **110 file /1.037.437 byte**, SHA-256
`3f61e9427e7e0a6e14b8f16f4c382b0a2a69a621eb935f18b75077e76f8754b0`. Verificato byte per byte e senza
credenziali/DB/configurazioni private.
